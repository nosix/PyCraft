# -*- coding: utf8 -*-

from queue import Queue


class EventQueue:
    
    def __init__(self):
        self._queue = Queue()
    
    def __len__(self):
        return self._queue.qsize()

    def empty(self):
        return self._queue.empty()

    def exec_next(self):
        method, param = self.get()
        return method(*param)

    def put(self, method, *param):
        self._queue.put_nowait((method, param))

    def get(self):
        return self._queue.get_nowait()