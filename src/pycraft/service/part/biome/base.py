# -*- coding: utf8 -*-

from pycraft.service.primitive.values import Color


class Biome:
    
    __slots__ = ['_color', '_populators']

    ID_NONE = -1

    id = ID_NONE

    COVER_BLOCKS = tuple()
    MIN_ELEVATION = 0
    MAX_ELEVATION = 0
    TEMPERATURE = 0.5
    RAINFALL = 0.5

    def __init__(self):
        self._color = self._create_color()
        self._populators = []

    @classmethod
    def _create_color(cls):
        def lerp_color(c1, c2, s):
            return c1 * (1 - s) + c2 * s
        x = 1 - cls.TEMPERATURE
        z = 1 - cls.TEMPERATURE * cls.RAINFALL
        l1 = lerp_color(Color(0x47, 0xd0, 0x33), Color(0x6c, 0xb4, 0x93), x)
        l2 = lerp_color(Color(0xbf, 0xb6, 0x55), Color(0x80, 0xb4, 0x97), x)
        return lerp_color(l1, l2, z).astype(lambda v: int(v) & 0xFF) 

    color = property(lambda self: self._color)
    populators = property(lambda self: self._populators)

    def regist_populator(self, populator):
        self._populators.append(populator)
