# -*- coding: utf8 -*-

class Random:

    __slots__ = ['_seed', '_value']    

    def __init__(self, seed):
        self._seed = seed
        self._value = seed
    
    seed = property(lambda self: self._seed)

    def reset(self):
        self._value = self._seed

    def next_int(self, signed=False):
        t = (((self._value * 65535) + 31337) >> 8) + 1337
        self._value ^= t
        return t if signed else t & 0x7FFFFFFF
        
    def next_float(self, signed=False):
        return float(self.next_int(signed)) / 0x7FFFFFFF

    def next_range(self, start, end):
        """startからendまでの範囲の整数を返す"""
        return start + (self.next_int() % (end - start + 1))