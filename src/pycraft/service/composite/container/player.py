# -*- coding: utf8 -*-

from collections import defaultdict
from pycraft.service.const import ContainerWindowID
from pycraft.service.part.item import ItemID
from .base import Container


class InventoryContainer(Container):
    
    SIZE = 36

    def __init__(self):
        super().__init__(ContainerWindowID.INVENTORY, self.SIZE)
        # TODO: indexを持たせる

    def add_item(self, item):
        """Itemをslotsに保存する
        
        クライアントの実装では、indexが小さい方から詰めて保存する

        item : Item
        return : Itemを保存したslotsのindex(保存できないときは-1)
        """
        empty_slot = None
        for i in range(self.SIZE):
            if self[i].id == item.id:
                count = self[i].count + item.count
                if count <= self[i].MAX_COUNT:
                    self[i].count = count
                    return i
                else:
                    # 詰めた分は通知しなくてもクライアントが勝手に変更する
                    diff = self[i].MAX_COUNT - self[i].count
                    self[i].count = self[i].MAX_COUNT
                    item.count -= diff
            elif self[i].id == ItemID.AIR:
                if empty_slot == None:
                    empty_slot = i
        if empty_slot != None:
            self[empty_slot] = item
            return empty_slot
        return -1
    
    def use_item(self, i, target):
        """Item を使用する
        
        i : slots の index
        target : Entity or Block (Item を使用する対象)
        return : Item が壊れたら True
        """
        target.hit_item(self[i])
        if self[i].is_broken():
            self[i] = self.create_empty()
            return True
        return False

    def reduce_items(self, items):
        """指定された Item を削除する
        
        return : generator((slot, is_empty))
        """
        # 削除する個数を種類毎に数える
        counts = defaultdict(int)
        for item in items:
            if item.id != ItemID.AIR:
                counts[item.id] += item.count
        # 削除する
        updated = {}
        for slot, item in enumerate(self):
            if item.id in counts:
                before = self[slot].count
                self[slot].count -= counts[item.id]
                counts[item.id] = 0
                if self[slot].count < 0:
                    counts[item.id] = -self[slot].count
                else:
                    del counts[item.id]
                updated[slot] = before - self[slot].count
        # 足りなかった場合はロールバック
        if len(counts) > 0:
            for slot, count in updated:
                self[slot].count += count
            raise ValueError(
                '{name} does not have items.'.format(name=self.name))
        # 更新を確定し、個数 0 は empty に設定する
        for slot in updated.keys():
            if self[slot].count == 0:
                self[slot] = self.create_empty()
                yield slot, True
            else:
                yield slot, False


class ArmorContainer(Container):
    
    SIZE = 4

    def __init__(self):
        super().__init__(ContainerWindowID.ARMOR, self.SIZE)
