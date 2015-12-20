# -*- coding: utf8 -*-

from operator import attrgetter
from pycraft.service.primitive.geometry import Size, Position
from pycraft.service.primitive.values import MetaData
from pycraft.service.part.item import ItemID, new_item
from pycraft.service.composite.container import \
    InventoryContainer, ArmorContainer
from .base import LivingEntity


class PlayerEntity(LivingEntity):

    NUM_OF_HOTBAR = 9
    
    HOTBAR_NONE = 255

    STRENGTH = 20
    BODY_SIZE = Size(0.6, 0.6, 1.8)
    EYE_POS = (0, 0, 1.62)

    @staticmethod
    def create_empty():
        return new_item(ItemID.AIR, 0)

    def __init__(self, player_id, public_id, skin_name, skin):
        super().__init__()
        self.spawn_pos = Position(0, 0, 0)
        self.opening_container = 0
        self._player_id = player_id
        self._public_id = public_id
        self._skin_name = skin_name
        self._skin = skin
        self._meta.set(MetaData.Key.SHOW_NAMETAG, 1)
        self._meta.set(MetaData.Key.PLAYER_BED_POSITION, Position(0, 0, 0))
        self._meta.set(MetaData.Key.POTION_COLOR, 0)
        self._meta.set(MetaData.Key.POTION_AMBIENT, 0)
        self._meta.set(MetaData.Key.PLAYER_FLAGS, 0)
        self._slots = InventoryContainer()
        self._armor_slots = ArmorContainer()
        self._hotbar = [self.HOTBAR_NONE] * self.NUM_OF_HOTBAR
        self._held_hotbar = 0

    def copy_from(self, other):
        """datastoreに保存されているデータをコピーする"""
        super().copy_from(other)
        self.spawn_pos = other.spawn_pos
        self._slots = other._slots.clone()
        self._armor_slots = other._armor_slots.clone()
        self._hotbar = list(other._hotbar)

    def clone(self):
        o = super().clone()
        o.opening_container = self.opening_container
        o._player_id = self._player_id
        o._public_id = self._public_id
        o._skin_name = self._skin_name
        o._skin = self.skin
        o._held_hotbar = self._held_hotbar
        return o

    bottom_pos = property(lambda self: self.pos - self.EYE_POS)
    player_id = property(attrgetter('_player_id'))
    public_id = property(attrgetter('_public_id'))
    skin_name = property(attrgetter('_skin_name'))
    skin = property(attrgetter('_skin'))
    slots = property(attrgetter('_slots'))
    armor_slots = property(attrgetter('_armor_slots'))
    hotbar = property(attrgetter('_hotbar'))

    def hold(self, hotbar):
        self._held_hotbar = hotbar
        
    def set_hotbar(self, i, slot, offset=False):
        """hotbar に slots の index を設定する
        
        i : hotbar の index
        slot : slots の index、offset=True のときは +NUM_OF_HOTBAR されている
        """
        if slot == self.HOTBAR_NONE:
            self._hotbar[i] = slot
        else:
            slot = slot - self.NUM_OF_HOTBAR if offset else slot
            self._hotbar[i] = (slot + self.NUM_OF_HOTBAR) \
                if self._slots[slot].id != ItemID.AIR \
                    else self.HOTBAR_NONE

    def find_hotbar(self, slot):
        """slot に該当する hotbar の index を返す
        
        slot : slots の index
        return : hotbar の index、見つからなかった場合は -1
        """
        if slot != self.HOTBAR_NONE:
            slot += self.NUM_OF_HOTBAR
        try:
            return self._hotbar.index(slot)
        except ValueError:
            return -1
    
    def get_held_item(self):
        slot = self._hotbar[self._held_hotbar]
        item = self._slots[slot - self.NUM_OF_HOTBAR] \
            if slot != self.HOTBAR_NONE else self._slots.create_empty()
        return item

    def get_held_slot(self, offset=False):
        """手に持っているslotを返す
        
        return : hotbar_index, slots_index, item
            offset=True のとき slots_index は +NUM_OF_HOTBAR される
            slots_index は Item が無いときには HOTBAR_NONE になる
        """
        slot = self._hotbar[self._held_hotbar]
        item = self._slots[slot - self.NUM_OF_HOTBAR] \
            if slot != self.HOTBAR_NONE else self._slots.create_empty()
        slot = slot if offset or slot == self.HOTBAR_NONE \
            else slot - self.NUM_OF_HOTBAR
        return (self._held_hotbar, slot, item)

    def spawn(self, spawn_pos=None):
        if not self.is_living():
            self.injury = 0
            spawn_pos = None
        if spawn_pos == None:
            spawn_pos = self.spawn_pos
        self.pos = spawn_pos + self.EYE_POS

    def attack(self, entity):
        self.get_held_item().attack(entity)
        
    def drop_items(self):
        """slotsを空にし、保存されていたItemを返す"""
        items = self._slots.drop_all() + self._armor_slots.drop_all()
        self._hotbar = [self.HOTBAR_NONE] * self.NUM_OF_HOTBAR
        self._held_hotbar = 0
        return items

    def did_meet(self, entity):
        if not entity.has_hostile(self) or not self.is_living():
            return False
        return self.obb.has_collision(entity.obb)
