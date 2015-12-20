# -*- coding: utf8 -*-

import time


class Scheduler:
    
    __slots__ = ['frame_rate', '_time_table', '_e_time']

    DEFAULT_FRAME_RATE = 30  # frame/sec
    
    def __init__(self):
        self.frame_rate = self.DEFAULT_FRAME_RATE
        self._time_table = {}

    frame_time = property(lambda self: 1.0 / self.frame_rate)

    def set(self, task_id, limit_rate):
        self._time_table[task_id] = limit_rate

    def start(self):
        now = time.clock()
        frame_time = self.frame_time
        def end_time(limit_rate):
            return now + frame_time * limit_rate
        self._e_time = dict(
            (task_id, end_time(rate)) for task_id, rate in self._time_table.items())
    
    def is_over(self, task_id):
        return time.clock() > self._e_time[task_id]
