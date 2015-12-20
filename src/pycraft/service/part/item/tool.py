# -*- coding: utf8 -*-

from ..block import BlockID
from .base import BreakableItem


class Tool(BreakableItem):

    __slots__ = ['_attack']    

    BASE_ATTACK = 1

    def __init__(self, id_, durability, attack, damage, unknown):
        super().__init__(id_, durability, damage, unknown)
        self._attack = attack

    def clone(self):
        o = super().clone()
        o._attack = self._attack
        return o

    def attack(self, entity):
        entity.injury += self.BASE_ATTACK + self._attack

    def use_on_block(self, block_id):
        self.damage += 1
    
    def use_on_entity(self):
        self.damage += 2


class Hoe(Tool):
    
    PLOWABLE = {BlockID.GRASS, BlockID.DIRT}

    def use_on_block(self, block_id):
        if block_id in self.PLOWABLE:
            self.damage += 1


class Pickaxe(Tool):
    
    BASE_ATTACK = 2


class Axe(Tool):

    BASE_ATTACK = 3    


class Sword(Tool):

    BASE_ATTACK = 4    

    def use_on_entity(self):
        self.damage += 1
