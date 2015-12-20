# -*- coding: utf8 -*-

import time
from operator import attrgetter
from pycraft.service.part.item import ItemID, furnace_recipe
from .base import PlacedContainer


class ChestContainer(PlacedContainer):
    
    TYPE = 0

    UNIT_SIZE = 27

    def __init__(self, window_id):
        super().__init__(window_id, self.UNIT_SIZE)

    def is_large(self):
        return len(self._slots) != self.UNIT_SIZE

    def extend(self):
        self._slots.extend(self.create_empty() for _ in range(self.UNIT_SIZE))

    def reduce(self):
        items = list(item 
            for item in self._slots[-self.UNIT_SIZE:] 
                if item.id != ItemID.AIR)
        del self._slots[-self.UNIT_SIZE:]
        return items


class FurnaceContainer(PlacedContainer):

    TYPE = 2    

    MAX_PROGRESS = 200

    SMELTING_SEC = 10.0
    SMELTING_TICK = SMELTING_SEC / MAX_PROGRESS

    SLOT_RAW = 0
    SLOT_FUEL = 1
    SLOT_PRODUCT = 2

    PROPERTY_PROGRESS = 0
    PROPERTY_ENERGY = 1

    __slots__ = ['_property', '_burning_start']    

    @classmethod
    def update_func(cls, target):
        return target._update_furnace

    def __init__(self, window_id):
        super().__init__(window_id, 3)
        self._property = {
            self.PROPERTY_PROGRESS: 0,
            self.PROPERTY_ENERGY: 0,
            }
        # 精錬していないときは 0、精錬中は最終更新時間
        self._burning_start = 0

    prop = property(attrgetter('_property'))

    def reduce(self):
        self._burning_start = 0
        items = list(item for item in self._slots if item.id != ItemID.AIR)
        del self._slots[:]
        return items

    def open(self, player_id):
        super().open(player_id)
        return False
    
    def close(self, player_id):
        super().close(player_id)
        return False

    def __setitem__(self, i, item):
        self._slots[i] = item
        if i == self.SLOT_RAW:
            self._property[self.PROPERTY_PROGRESS] = 0
        if i != self.SLOT_PRODUCT:
            self._burning_start = time.clock()
    
    def is_burning(self):
        return self._property[self.PROPERTY_ENERGY] != 0

    def _burn(self):
        """燃料を燃やす
        
        return : SLOT_FUEL に変化があった場合は True
        """
        if self._property[self.PROPERTY_ENERGY] == 0:
            # 精錬する対象がなければ燃やさない
            if self._slots[self.SLOT_RAW].id == ItemID.AIR:
                return False
            # 燃料を燃やす
            item = self._slots[self.SLOT_FUEL]
            if item.id == ItemID.AIR:
                return False
            self._property[self.PROPERTY_ENERGY] = furnace_recipe.burn(item)
            self.reduce_item(self.SLOT_FUEL)
            return True

    def _smelt(self):
        """精錬を進める
        
        return : tuple (変化があった slots index)
        """
        # エネルギーが無ければ燃料を燃やす
        if self._property[self.PROPERTY_ENERGY] == 0:
            if self._burn():
                return (self.SLOT_FUEL, )
            else:
                self._burning_start = 0
                return ()
        # エネルギーを減らす
        self._property[self.PROPERTY_ENERGY] -= 1
        # 精錬対象がなければ何もしない
        if self._slots[self.SLOT_RAW].id == ItemID.AIR:
            return ()
        # 精錬を進める
        self._property[self.PROPERTY_PROGRESS] += 1
        # 精錬中
        if self._property[self.PROPERTY_PROGRESS] != self.MAX_PROGRESS:
            return ()
        self._property[self.PROPERTY_PROGRESS] = 0
        self._slots[self.SLOT_PRODUCT] = \
            furnace_recipe.smelt(self._slots[self.SLOT_RAW])
        self.reduce_item(self.SLOT_RAW)
        return (self.SLOT_RAW, self.SLOT_PRODUCT)

    def _repeat(self, count):
        for _ in range(count):
            for slot in self._smelt():
                yield slot

    def update(self):
        """定期的に更新を行う
        
        return : tuple(boolean, tuple(int))
            boolean - 更新を行ったら True
            tuple(int) - 更新された slot index
        """
        if self._burning_start == 0:
            return False, ()
        diff = time.clock() - self._burning_start
        count = int(diff/self.SMELTING_TICK)
        updated_slots = set(self._repeat(count))
        # 精錬が終了していなければ最終更新時間を更新
        if self._burning_start != 0:
            self._burning_start += count * self.SMELTING_TICK
        return count > 0, tuple(updated_slots)
