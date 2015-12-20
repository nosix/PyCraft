# -*- coding: utf8 -*-

from operator import attrgetter
from pycraft.service.part.item import ItemID, new_item


class Container:

    @staticmethod
    def create_empty():
        return new_item(ItemID.AIR, 0)

    def __init__(self, window_id, size):
        self._window_id = window_id
        self._slots = [self.create_empty() for _ in range(size)]

    def clone(self):
        o = self.__class__.__new__(self.__class__)
        o._window_id = self._window_id
        o._slots = [item.clone() for item in self._slots]
        return o

    window_id = property(attrgetter('_window_id'))

    def __len__(self):
        return len(self._slots)
    
    def __getitem__(self, i):
        return self._slots[i]

    def __setitem__(self, i, item):
        self._slots[i] = item
    
    def __iter__(self):
        return iter(self._slots)

    def reduce_item(self, i):
        """Item を slots から減らす
        
        i : slots の index
        return : なくなったら True
        """
        self[i].count -= 1
        if self[i].count == 0:
            self[i] = self.create_empty()
            return True
        return False

    def drop_all(self):
        """slotsを空にし、保存されていたItemを返す"""
        items = list(item for item in self._slots if item.id != ItemID.AIR)
        self._slots[:] = [self.create_empty() for _ in range(self.SIZE)]
        return items


class PlacedContainer(Container):

    @classmethod
    def update_func(cls, target):
        return None

    def __init__(self, window_id, size):
        super().__init__(window_id, size)
        # 関連づけられている場所
        self._pos = set()
        # 開いているPlayerのplayer_id
        self._opened_by = set()

    def clone(self):
        o = super().clone()
        o._pos = set(self._pos)
        o._opened_by = set(self._opened_by)
        return o

    pos = property(lambda self: list(self._pos))
    opened_by = property(lambda self: list(self._opened_by))

    def bind(self, pos):
        self._pos.add(pos)

    def unbind(self, pos):
        self._pos.discard(pos)

    def open(self, player_id):
        did_open = len(self._opened_by) == 0
        self._opened_by.add(player_id)
        return did_open
    
    def close(self, player_id):
        self._opened_by.discard(player_id)
        return len(self._opened_by) == 0
