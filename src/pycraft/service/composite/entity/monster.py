# -*- coding: utf8 -*-

from pycraft.service.const import EntityType
from pycraft.service.primitive.geometry import Size
from .base import MobEntity
from .player import PlayerEntity


class MonsterEntity(MobEntity):
    
    def has_hostile(self, entity):
        return isinstance(entity, PlayerEntity)


class Zombie(MonsterEntity):

    TYPE = EntityType.ZOMBIE
    STRENGTH = 10
    BODY_SIZE = Size(0.6, 0.6, 1.95)
    VIEW_DISTANCE = 64
    VIEW_ANGLE_H = 60
    VIEW_ANGLE_V = 30


class Skeleton(MonsterEntity):

    TYPE = EntityType.SKELTON
    STRENGTH = 10
    BODY_SIZE = Size(0.6, 0.6, 1.8)
    VIEW_DISTANCE = 64
    VIEW_ANGLE_H = 60
    VIEW_ANGLE_V = 30


class Creeper(MonsterEntity):

    TYPE = EntityType.CREEPER
    STRENGTH = 10
    BODY_SIZE = Size(0.6, 0.6, 1.8)
    VIEW_DISTANCE = 64
    VIEW_ANGLE_H = 60
    VIEW_ANGLE_V = 30


class Spider(MonsterEntity):

    TYPE = EntityType.SPIDER
    STRENGTH = 8
    BODY_SIZE = Size(1.4, 1.4, 0.9)
    VIEW_DISTANCE = 32
    
    def can_climb(self):
        return True


class Enderman(MonsterEntity):

    TYPE = EntityType.ENDERMAN
    STRENGTH = 20
    BODY_SIZE = Size(0.6, 0.6, 2.9)
    VIEW_ANGLE_H = 90
    VIEW_ANGLE_V = 10
