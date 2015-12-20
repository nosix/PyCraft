# -*- coding: utf8 -*-

from pycraft.service.primitive.geometry import Vector
from pycraft.service.primitive.values import Message


class Accident:
    
    DEATH_MESSAGE = ''

    __slots__ = ['_entity']

    def __init__(self, entity):
        self._entity = entity

    death_msg = property(lambda self:
        Message(self.DEATH_MESSAGE, *self.get_msg_params(), is_raw=False))
    
    def get_msg_params(self, entity):
        return []

    def direc_of_dropping(self, motion_law):
        return Vector(0,0,0)
