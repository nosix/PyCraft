# -*- coding: utf8 -*-

import os
import logging
from operator import attrgetter
from pycraft.network import Server, LogName
from pycraft.service import Handler
from .client import Client


class TestServer:
    
    def __init__(self, datastore, clock, testcase):
        self._testcase = testcase
        self._addr = ('', 19132)
        self._server = Server(self._addr, Handler(datastore, clock))
        self._clients = []
        self._server_log_handler = None
        self._packet_log_handler = None
        self._running_thread = None

    addr = property(attrgetter('_addr'))

    def init_logger(self, test_id):
        postfix = str(test_id) + '.log'
        server_log_file = os.path.join('server.' + postfix)
        packet_log_file = os.path.join('packet.' + postfix)
        time_log_file = os.path.join('time.' + postfix)
    
        if os.path.exists(server_log_file):
            os.remove(server_log_file)
        if os.path.exists(packet_log_file):
            os.remove(packet_log_file)
        if os.path.exists(time_log_file):
            os.remove(time_log_file)

        logging.basicConfig(level=logging.DEBUG)
    
        logger = logging.getLogger(LogName.SERVER)
        logger.propagate = False
        h = logging.FileHandler(server_log_file)
        h.setFormatter(logging.Formatter(
            '%(asctime)-15s:%(levelname)s:%(message)s'))
        logger.addHandler(h)
        self._server_log_handler = h
        
        logger = logging.getLogger(LogName.PACKET)
        logger.propagate = False
        h = logging.FileHandler(packet_log_file)
        h.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(h)
        self._packet_log_handler = h

    def start(self, thread):
        self._running_thread = thread
        self._server.run()

    def terminate(self):
        self._server.terminate()
        for c in self._clients:
            c.wait()
        self._running_thread.join()
        del self._running_thread
        logger = logging.getLogger(LogName.SERVER)
        if self._server_log_handler != None:
            logger.removeHandler(self._server_log_handler)
        logger = logging.getLogger(LogName.PACKET)
        if self._packet_log_handler != None:
            logger.removeHandler(self._packet_log_handler)

    def __enter__(self):
        return self
    
    def __exit__(self, type_, value, traceback):
        self.terminate()

    def new_client(self):
        c = Client(self._testcase, self)
        self._clients.append(c)
        return c
