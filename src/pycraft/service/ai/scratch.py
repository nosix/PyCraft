# -*- coding: utf8 -*-

import os
import sys
import traceback
from collections import defaultdict
from multiprocessing import Process, Queue
from pycraft.service import logger
from pycraft.network import PortScanner
from pycraft.extension import scratch
from pycraft.service import config
from .values import MobMotion


class ScratchAgent:
    
    def __init__(self, free_mob, host):
        self._free_mob = free_mob
        self._scratch = scratch.Scratch(host)
        self._received = Queue()
        self._process = Process(target=self.run, args=(self._received,))
        # eid:int -> name
        self._controlled = {}
        # param_name -> param_value
        self._latest_params = {}
        # eid:int -> MobMotion
        self._latest_motion = {}
        # eid:int -> MobStatus
        self._latest_status = {}
        # eid:int -> player_eid -> {mob_id, id, distance, angle_h, angle_v}
        self._found_players = {}

    def start(self):
        self._process.start()
        try:
            self._scratch.broadcast('enabled')
        except:
            traceback.print_exc(file=sys.stdout)
    
    def terminate(self):
        if self._process.is_alive():
            self._process.terminate()
            self._process.join()
        try:
            self._scratch.disconnect()
        except:
            traceback.print_exc(file=sys.stdout)
        logger.server.info('terminate {name}', name=self.__class__.__name__)
    
    def is_alive(self):
        return self._process.is_alive()

    def _receive_data(self):
        def execute(message, params):
            if message == 'search mob':
                self._search_mob(params)
            if message == 'control':
                self._control(params)
            if message == 'free':
                self._free(params)
            if message == 'show status':
                self._show_status(params)
            if message == 'search player':
                self._search_player(params)
            if message == 'move':
                self._move(params)
        while not self._received.empty():
            msg = self._received.get()
            if msg[0] == 'sensor-update':
                self._latest_params.update(msg[1])
            elif msg[0] == 'broadcast':
                try:
                    execute(msg[1], self._latest_params)
                except:
                    traceback.print_exc(file=sys.stdout)
                    self.terminate()
    
    def _search_mob(self, params):
        if 'mob_type' in params:
            eids = self._free_mob[int(params['mob_type'])]
            if len(eids) > 0:
                self._scratch.sensorupdate({'mob_id': eids.pop()})
                self._scratch.broadcast('mob found')
            else:
                self._scratch.broadcast('mob not found')

    def _control(self, params):
        if 'mob_id' in params:
            eid = int(params['mob_id'])
            self._controlled[eid] = str(params.get('mob_name', ''))
            self._latest_motion[eid] = MobMotion(
                0, 0, 0, 0, self._controlled[eid])
    
    def _free(self, params):
        if 'mob_id' in params:
            eid = int(params['mob_id'])
            self.free(eid)

    def _show_status(self, params):
        if 'mob_id' in params:
            eid = int(params['mob_id'])
            if eid in self._latest_status:
                self._scratch.sensorupdate(self._latest_status[eid])
                self._scratch.broadcast('status found')
            else:
                self._scratch.broadcast('status not found')

    def _search_player(self, params):
        if 'mob_id' in params:
            eid = int(params['mob_id'])
            if (eid in self._found_players) and \
                    len(self._found_players[eid]) > 0:
                player_eid = list(self._found_players[eid].keys())[0]
                data = self._found_players[eid].pop(player_eid)
                self._scratch.sensorupdate(data)
                self._scratch.broadcast('player found')
            else:
                self._scratch.broadcast('player not found')
            
    def _move(self, params):
        if 'mob_id' in params:
            eid = int(params['mob_id'])
            if eid in self._controlled:
                yaw = float(params.get('yaw', 0))
                head_yaw = float(params.get('head_yaw', 0))
                pitch = float(params.get('pitch', 0))
                forward_move = float(params.get('movement', 0))
                self._latest_motion[eid] = MobMotion(
                    yaw, head_yaw, pitch, forward_move, self._controlled[eid])
    
    def free(self, eid):
        if eid in self._controlled:
            del self._controlled[eid]
        if eid in self._latest_motion:
            del self._latest_motion[eid]
        if eid in self._latest_status:
            del self._latest_status[eid]
        if eid in self._found_players:
            del self._found_players[eid]

    def has_control(self, eid):
        if not self.is_alive():
            return False
        self._receive_data()
        return eid in self._controlled
    
    def next_motion(self, eid, status):
        if not self.is_alive():
            return None
        self._receive_data()
        self._latest_status[eid] = {
            'mob_id': eid,
            'mob_type': status.type,
            'head_yaw': int(status.head_yaw),
            'pitch': int(status.pitch)}
        self._found_players[eid] = {}
        for player_eid, distance, angle_h, angle_v in status.found:
            self._found_players[eid][player_eid] = {
                #'mob_id': eid, # 送信できるデータ量に限りがある
                'player_id': player_eid,
                'distance': int(distance),
                'angle_h': int(angle_h),
                'angle_v': int(angle_v)}
        return self._latest_motion.pop(eid, None)

    def run(self, received):
        logger.server.info(
            'start {name}(pid={pid})',
            name=self.__class__.__name__, pid=os.getpid())
        def listen():
            while True:
                try:
                    yield self._scratch.receive()
                except scratch.ScratchError:
                    raise StopIteration        
        for msg in listen():
            received.put(msg)


class ScratchAgentManager:
    
    def __init__(self):
        # addr -> ScratchAgent
        self._scratch_agent = {}
        # list(addr)
        self._order = []
        # eid -> ScratchAgent
        self._control = {}
        # type -> set(eid)
        self._free_mob = defaultdict(set)
        # PortScanner
        self._portscanner = PortScanner()
    
    def start(self):
        self._portscanner.start()
    
    def terminate(self):
        self._portscanner.terminate()
        for agent in self._scratch_agent.values():
            agent.terminate()
    
    def update(self):
        if not self._portscanner.is_scanning():
            self._portscanner.scan_network(
                config.scratch_port, config.scratch_network)
        addr = self._portscanner.pop()
        if (addr != None) and (addr not in self._scratch_agent):
            ipaddr, _ = addr
            try:
                agent = ScratchAgent(self._free_mob, ipaddr)
                agent.start()
                self._scratch_agent[addr] = agent
                self._order.append(addr)
                print('new scratch agent', addr)
            except:
                traceback.print_exc(file=sys.stdout)
    
    def get_agent(self, mob_eid, mob_type):
        if mob_eid in self._control:
            agent = self._control[mob_eid]
            if agent.has_control(mob_eid):
                if mob_type != 0:
                    return agent
                else:
                    agent.free(mob_eid)
                    return None
            else:
                self._free_mob[mob_type].add(mob_eid)
                del self._control[mob_eid]
        if mob_type == 0:
            return None
        if len(self._order) > 0:
            addr = self._order.pop(0)
            agent = self._scratch_agent[addr]
            if not agent.is_alive():
                del self._scratch_agent[addr]
                print('delete scratch agent', addr)
                return None
            self._order.append(addr)
            if agent.has_control(mob_eid):
                self._free_mob[mob_type].discard(mob_eid)
                self._control[mob_eid] = agent
                return agent
        self._free_mob[mob_type].add(mob_eid)
        return None