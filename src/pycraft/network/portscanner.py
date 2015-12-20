# -*- coding: utf8 -*-

import os
import ipaddress
import socket
from multiprocessing import Process, Queue
from . import logger


class PortScanner:
    
    def __init__(self):
        self._request = Queue()
        self._response = Queue()
        self._process = Process(
            target=self.run, args=(self._request, self._response))

    def __del__(self):
        self.terminate()

    def start(self):
        self._process.start()
    
    def terminate(self):
        if self._process.is_alive():
            self._process.terminate()
            self._process.join()
        logger.server.info('terminate {name}', name=self.__class__.__name__)

    def run(self, request, response):
        logger.server.info(
            'start {name}(pid={pid})',
            name=self.__class__.__name__, pid=os.getpid())
        while True:
            if not request.empty():
                addr, port = request.get()
                if self._is_open(addr, port):
                    response.put((addr, port))

    def _is_open(self, addr, port, timeout=0.1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as s:
            s.settimeout(timeout)
            try:
                s.connect((addr, port))
                return True
            except:
                return False
    
    def scan(self, port, addr_range):
        for addr in addr_range:
            self._request.put((addr, port))
    
    def scan_network(self, port, network):
        addr_range = (str(addr)
             for addr in ipaddress.ip_network(network).hosts())
        self.scan(port, addr_range)
    
    def is_scanning(self):
        return not self._request.empty()

    def pop(self):
        return self._response.get() if not self._response.empty() else None
