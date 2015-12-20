# -*- coding: utf8 -*-

from pycraft.service.primitive.geometry import Face
from ..item import ItemID
from .base import Block, MaterialBlock, WithDirection


class Air(Block):
    
    @classmethod
    def is_transparent(cls):
        return True

    @classmethod
    def is_solid(cls):
        return False

    @classmethod
    def can_attach(cls):
        return False


class Stone(Block):
    
    def to_item(self):
        return ItemID.COBBLESTONE


class Grass(Block):
    
    def to_item(self):
        return ItemID.DIRT


class Sand(MaterialBlock):
    
    @classmethod
    def is_fallable(cls):
        return True


class Chest(MaterialBlock, WithDirection):
    
    @classmethod
    def is_transparent(cls):
        return True

    @classmethod
    def can_attach(cls):
        return False

    @classmethod
    def get_remove_func(cls, terrain):
        return terrain._remove_chest

    @classmethod
    def get_touch_func(cls, terrain):
        return terrain._open_container
    
    @classmethod
    def get_add_func(cls, terrain):
        return terrain._add_chest


class CraftingTable(MaterialBlock):

    @classmethod
    def can_attach(cls):
        return False


class Furnace(Block, WithDirection):
    
    @classmethod
    def can_attach(cls):
        return False

    @classmethod
    def get_remove_func(cls, terrain):
        return terrain._remove_furnace

    @classmethod
    def get_touch_func(cls, terrain):
        return terrain._open_container
    
    @classmethod
    def get_add_func(cls, terrain):
        return terrain._add_furnace

    def to_item(self):
        return ItemID.FURNACE


class Sign(Block):
    
    @classmethod
    def get_remove_func(cls, terrain):
        return terrain._remove_sign

    @classmethod
    def get_add_func(cls, terrain):
        return terrain._add_sign

    def to_item(self):
        return ItemID.SIGN


class WallSign(Sign, WithDirection):

    pass


class SignPost(Sign):
    
    NUM_OF_DIRECTION = 16
    
    @classmethod
    def to_attr(cls, player_yaw=None, **kwargs):
        if player_yaw != None:
            direc = (player_yaw + 180) * cls.NUM_OF_DIRECTION / 360
            return int(direc + 0.5) % cls.NUM_OF_DIRECTION


class Door(Block):
    
    NUM_OF_DIRECTION = 4

    @classmethod
    def to_attr(cls, **kwargs):
        # 下段のドアの向きをプレイヤーの向きに合わせる
        if 'player_yaw' in kwargs:
            direc = (kwargs['player_yaw'] + 90) * cls.NUM_OF_DIRECTION / 360
            return int(direc + 0.5) % cls.NUM_OF_DIRECTION
        # 下段のドアの開閉
        if 'switch_attr' in kwargs:
            return kwargs['switch_attr'] ^ 4
        # 上段の両開きドア設定
        if 'is_double' in kwargs:
            return 9 if kwargs['is_double'] else 8

    @classmethod
    def get_remove_func(cls, terrain):
        return terrain._remove_door

    @classmethod
    def get_touch_func(cls, terrain):
        return terrain._open_door

    @classmethod
    def get_add_func(cls, terrain):
        return terrain._add_door

    def is_upside(self):
        return self.attr >= 8

    def is_double(self):
        return self.attr == 9

    def direc(self):
        return self.attr & 3

    def left_side(self):
        direc = (2,5,3,4)[self.direc()]
        return Face.DIRECTION[direc]


class WoodenDoor(Door):
    
    def to_item(self):
        return ItemID.WOODEN_DOOR


class IronDoor(Door):
    
    def to_item(self):
        return ItemID.IRON_DOOR


class Snow(Block):
    
    @classmethod
    def is_transparent(cls):
        return True