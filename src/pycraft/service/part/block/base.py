# -*- coding: utf8 -*-

from pycraft.common import ImmutableMeta
from .ids import NAMES


class Block(metaclass=ImmutableMeta):
    
    properties = 'id attr'

    @classmethod
    def new(cls, id_, attr=0, **kwargs):
        dynamic_attr = cls.to_attr(**kwargs) \
            if hasattr(cls, 'to_attr') else None
        return id_, (attr if dynamic_attr == None else dynamic_attr)

    def __str__(self):
        return '{cls}({name}, {id}, {attr})'.format(
                    cls=self.__class__.__name__,
                    name=NAMES[self.id],
                    id=self.id,
                    attr=self.attr)

    @classmethod
    def is_transparent(cls):
        return False

    @classmethod
    def is_solid(cls):
        return True

    @classmethod
    def is_fallable(cls):
        return False

    @classmethod
    def can_attach(cls):
        return True

    @classmethod
    def get_remove_func(cls, terrain):
        return None

    @classmethod
    def get_touch_func(cls, terrain):
        return None

    @classmethod
    def get_add_func(cls, terrain):
        return None

    def hit_item(self, item):
        item.use_on_block(self.id)
        
    def to_item(self):
        return None


class MaterialBlock(Block):
    
    def to_item(self):
        return self.id


class WithDirection:

    @classmethod
    def to_attr(cls, attach_face=1, player_face=None, **kwargs):
        """ブロックの向き
        
        2, 3, 4, 5 : See geometry.Face 
        """
        if player_face != None:
            return attach_face \
                if attach_face >= 2 else player_face.inverse().h
