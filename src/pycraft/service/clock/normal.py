# -*- coding: utf8 -*-

import time
from operator import attrgetter


class Clock:
    """20分で1日となる時刻を刻む時計"""
    
    MC_TIME_PER_DAY = 19200
    SEC_PER_DAY = 20 * 60
    
    MC_TIME_PER_SEC = MC_TIME_PER_DAY // SEC_PER_DAY  # 16
    MC_TIME_TICK = MC_TIME_PER_SEC

    def __init__(self):
        # 現在時刻
        self._mc_time = 0
        # 最後に時を刻んだ時刻
        self._mc_tick_time = 0
        # 基準となる時刻
        self._origin = time.clock()

    time = property(attrgetter('_mc_time'))

    def update(self):
        # 時刻の更新
        sec = int(time.clock() - self._origin) % self.SEC_PER_DAY
        self._mc_time = sec * self.MC_TIME_PER_SEC
        # 時計の針を刻む
        diff_tick = self._mc_time - self._mc_tick_time
        if diff_tick >= self.MC_TIME_TICK or diff_tick < 0:
            self._mc_tick_time = \
                (self._mc_time // self.MC_TIME_TICK) * self.MC_TIME_TICK
            return True
        else:
            return False
