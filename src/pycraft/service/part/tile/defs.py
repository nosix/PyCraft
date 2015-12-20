# -*- coding: utf8 -*-

from operator import attrgetter
from pycraft.service.primitive.values import NamedTag
from .base import BlockEntity, ContainerEntity


class Chest(ContainerEntity):
    
    __slots__ = ['_pair_pos']

    def __init__(self, pos, window_id):
        super().__init__(pos, window_id)
        self._pair_pos = None
        self.named_tag = self._create_tag()

    def clone(self):
        o = super(Chest, self).clone()
        o._pair_pos = self._pair_pos
        return o

    pair_pos = property(attrgetter('_pair_pos'))

    def _create_tag(self):
        tag = NamedTag()
        tag.put_compound()
        tag.put_str('id', 'Chest')
        tag.put_int('x', self._pos.x)
        tag.put_int('y', self._pos.y)
        tag.put_int('z', self._pos.z)
        if self._pair_pos != None:
            tag.put_int('pairx', self._pair_pos.x)
            tag.put_int('pairz', self._pair_pos.z)
        return tag.bytes()

    def is_next(self, pos):
        return (
            self.pos.y == pos.y and 
            abs(self.pos.x - pos.x) + abs(self.pos.z - pos.z) == 1)

    def set_pair(self, pos):
        self._pair_pos = pos
        self.named_tag = self._create_tag()

    def clear_pair(self):
        self._pair_pos = None
        self.named_tag = self._create_tag()


class Furnace(ContainerEntity):

    def __init__(self, pos, window_id):
        super(Furnace, self).__init__(pos, window_id)


class Sign(BlockEntity):
    
    def __init__(self, pos):
        super(Sign, self).__init__(pos)
        self.named_tag = self._create_tag()
    
    def _create_tag(self):
        tag = NamedTag()
        tag.put_compound()
        tag.put_str('id', 'Sign')
        tag.put_str('Text1', '')
        tag.put_str('Text2', '')
        tag.put_str('Text3', '')
        tag.put_str('Text4', '')
        tag.put_int('x', self._pos.x)
        tag.put_int('y', self._pos.y)
        tag.put_int('z', self._pos.z)
        return tag.bytes()