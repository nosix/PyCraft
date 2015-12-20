# -*- coding: utf8 -*-

from .base import BreakableItem


class Armor(BreakableItem):

    __slots__ = ['_guard']    

    def __init__(self, id_, durability, guard, damage, unknown):
        super().__init__(id_, durability, damage, unknown)
        self._guard = guard

    def guard(self):
        return self._guard
