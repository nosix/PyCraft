# -*- coding: utf8 -*-

import os
from multiprocessing import Process, Queue, Value
from pycraft.service import logger
from .base import MobAI
from .scratch import ScratchAgentManager


class MobAIProcess:
    
    def __init__(self):
        self._received_motion = {}
        self._terminate = Value('b', False)
        self._status_queue = Queue()
        self._motion_queue = Queue()
        self._process = Process(
            target=self.run,
            args=(self._terminate, self._status_queue, self._motion_queue))                                

    def send(self, eid, status):
        # 別ProcessにMobStatusを渡す
        self._status_queue.put((eid, status))

    def recv(self, eid):
        self._recv_motions()
        return self._received_motion.pop(eid, None)

    def _recv_motions(self):
        # 別Processで生成したMobMotionを受け取る
        while not self._motion_queue.empty():
            eid, m = self._motion_queue.get()
            self._received_motion[eid] = m

    def start(self):
        self._process.start()
    
    def terminate(self):
        self._terminate.value = True
        if self._process.is_alive():
            self._process.join()
        logger.server.info('terminate {name}', name=self.__class__.__name__)
    
    def run(self, terminate, status_queue, motion_queue):
        logger.server.info(
            'start {name}(pid={pid})',
            name=self.__class__.__name__, pid=os.getpid())
        agents = ScratchAgentManager()
        agents.start()
        while not terminate.value:
            agents.update()
            if not status_queue.empty():
                eid, status = status_queue.get()
                scratch_agent = agents.get_agent(eid, status.type)
                if scratch_agent:
                    motion = scratch_agent.next_motion(eid, status)
                else:
                    motion = MobAI().next_motion(status)
                if motion != None:
                    motion_queue.put((eid, motion))
        agents.terminate()
