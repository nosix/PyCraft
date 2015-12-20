# -*- coding: utf8 -*-

import time


class StaticClock:
    """常に同じ時刻を刻む時計(for testing)"""
    
    MORNING = 17760
    NOON = 4800
    EVENING = 9600
    NIGHT = 14400
    
    def __init__(self, mc_time=0, tick=None):
        """時を決めて初期化する
        
        mc_time : 開始時刻
        tick : 指定した間隔(sec)で開始時刻に戻す
        """
        self.time = mc_time
        self._tick = tick
        self._tick_time = time.clock()
    
    def update(self):
        if self._tick == None:
            return False
        diff = time.clock() - self._tick_time
        if diff >= self._tick:
            self._tick_time += self._tick
            return True
        else:
            return False