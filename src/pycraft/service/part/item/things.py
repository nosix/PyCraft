# -*- coding: utf8 -*-

from pycraft.service.primitive.geometry import Face
from ..block import BlockID
from .base import Item


class Sign(Item):
    
    def to_block(self, attach_face):
        direc = Face.DIRECTION[attach_face]
        if direc.y == 0:
            return BlockID.WALL_SIGN
        if direc.y == 1:
            return BlockID.SIGN_POST
        else:
            return None


class Door(Item):
    
    MAX_COUNT = 1
    

class WoodenDoor(Door):
    
    def to_block(self, attach_face):
        return BlockID.WOODEN_DOOR


class IronDoor(Door):
    
    def to_block(self, attach_face):
        return BlockID.IRON_DOOR