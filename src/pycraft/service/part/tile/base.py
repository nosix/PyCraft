# -*- coding: utf8 -*-

from operator import attrgetter


class BlockEntity:
    
    __slots__ = ['_pos', '_named_tag']

    def __init__(self, pos):
        self._pos = pos
        self._named_tag = b''

    def clone(self):
        o = self.__class__.__new__(self.__class__)
        o._pos = self._pos
        o._named_tag = self._named_tag
        return o

    def set_named_tag(self, named_tag):
        self._named_tag = named_tag

    pos = property(attrgetter('_pos'))
    named_tag = property(attrgetter('_named_tag'), set_named_tag)


class ContainerEntity(BlockEntity):

    __slots__ = ['_window_id']

    def __init__(self, pos, window_id):
        super().__init__(pos)
        self._window_id = window_id

    def clone(self):
        o = super().clone()
        o._window_id = self._window_id
        return o

    window_id = property(attrgetter('_window_id'))
