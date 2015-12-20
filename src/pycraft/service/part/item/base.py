# -*- coding: utf8 -*-

from operator import attrgetter
from .ids import NAMES


class Item:
    
    __slots__ = ['_id', '_count', '_attr', '_unknown', '_is_changed']

    MAX_COUNT = 64

    def __init__(self, id_, count=1, attr=0, unknown=0):
        self._id = id_
        self._count = count
        self._attr = attr
        self._unknown = unknown  # TODO: 対応する
        self._is_changed = True  # TODO: なくせないか？

    def __repr__(self):
        return '{cls}({id}, {count}, {attr}, {unknown})'.format(
                    cls=self.__class__.__name__,
                    id=self._id,
                    count=self._count,
                    attr=self._attr,
                    unknown=self._unknown)

    def __str__(self):
        return '{cls}({name}, {id}, {count}, {attr}, {unknown})'.format(
                    cls=self.__class__.__name__,
                    name=NAMES[self._id],
                    id=self._id,
                    count=self._count,
                    attr=self._attr,
                    unknown=self._unknown)

    def clone(self):
        o = self.__class__.__new__(self.__class__)
        o._id = self._id
        o._count = self._count
        o._attr = self._attr
        o._unknown = self._unknown
        o._is_changed = self._is_changed
        return o

    def clear_changed(self):
        self._is_changed = False

    def set_count(self, count):
        self._count = count
        self._is_changed = True

    def set_attr(self, attr):
        self._attr = attr
        self._is_changed = True

    def set_damage(self, damage):
        pass

    id = property(attrgetter('_id'))
    is_changed = property(attrgetter('_is_changed'))
    count = property(attrgetter('_count'), set_count)
    attr = property(attrgetter('_attr'), set_attr)
    damage = property(lambda self: 0, set_damage)
    
    def attack(self, entity):
        entity.injury += 1

    def is_broken(self):
        return False

    def to_block(self, attach_face):
        return None

    def use_on_block(self, block_id):
        pass
    
    def use_on_entity(self):
        pass


class BlockItem(Item):
    
    def to_block(self, attach_face):
        return self.id


class BreakableItem(Item):

    __slots__ = ['_durability']

    MAX_COUNT = 1

    def __init__(self, id_, durability, damage, unknown):
        super().__init__(id_, 1, damage, unknown)
        self._durability = durability

    def clone(self):
        o = super().clone()
        o._durability = self._durability
        return o

    def set_damage(self, damage):
        self._attr = damage

    damage = property(attrgetter('_attr'), set_damage)
    
    def is_broken(self):
        return self.damage >= self._durability
