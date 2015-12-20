# -*- coding: utf8 -*-

from itertools import count
from heapq import heappush, heappop


class PriorityQueue:
    
    __slots__ = ['_pq', '_counter', '_task_finder', '_task_num']

    _INVALID = 0

    def __init__(self):
        self._pq = []
        self._counter = count(1)
        # task -> item of self._pq
        self._task_finder = {}
        # priority:int -> num_of_tasks:int
        self._task_num = []
    
    def _increment_task_num(self, priority):
        # サイズが小さければ拡張する
        n = len(self._task_num)
        diff = priority + 1 - n
        if diff > 0:
            self._task_num[n:n+diff] = [0] * diff
        self._task_num[priority] += 1

    def _decrement_task_num(self, priority):
        self._task_num[priority] -= 1

    def empty(self, max_priority=None):
        return sum(
            self._task_num[:max_priority+1] \
                if max_priority != None else self._task_num) == 0
            
    def put(self, priority, task):
        if task in self._task_finder:
            entry = self._task_finder[task]
            if entry[0] <= priority:
                return
            else:
                entry[1] = self._INVALID
                self._decrement_task_num(entry[0])
        count = next(self._counter)
        entry = [priority, count, task]
        self._task_finder[task] = entry
        heappush(self._pq, entry)
        self._increment_task_num(priority)
    
    def get(self):
        while len(self._task_finder) > 0:
            priority, count, task = heappop(self._pq)
            if count is not self._INVALID:
                del self._task_finder[task]
                self._decrement_task_num(priority)
                return priority, task
