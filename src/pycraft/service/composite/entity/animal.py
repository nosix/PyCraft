# -*- coding: utf8 -*-

from pycraft.service.const import EntityType
from pycraft.service.primitive.geometry import Size
from pycraft.service.part.item import ItemID, new_item
from .base import MobEntity


class Chicken(MobEntity):

    TYPE = EntityType.CHICKEN
    STRENGTH = 2
    BODY_SIZE = Size(0.3, 0.3, 0.7)
    
    def drop_items(self):
        return [
            new_item(ItemID.FEATHER),
            new_item(ItemID.FEATHER),
            new_item(ItemID.RAW_CHICKEN),
            ]


class Sheep(MobEntity):

    TYPE = EntityType.SHEEP
    STRENGTH = 4
    BODY_SIZE = Size(0.9, 0.9, 1.3)
    
    def drop_items(self):
        return [
            new_item(ItemID.WOOL)
            ]


class Wolf(MobEntity):

    TYPE = EntityType.WOLF
    STRENGTH = 4
    BODY_SIZE = Size(0.6, 0.6, 0.8)


class Villager(MobEntity):

    TYPE = EntityType.VILLAGER
    STRENGTH = 10
    BODY_SIZE = Size(0.6, 0.6, 1.8)
    VIEW_DISTANCE = 128
    VIEW_ANGLE_H = 60
    VIEW_ANGLE_V = 20


class Bat(MobEntity):
    
    TYPE = EntityType.BAT
    STRENGTH = 3
    BODY_SIZE = Size(0.5, 0.5, 0.9)

    def can_fly(self):
        return True
