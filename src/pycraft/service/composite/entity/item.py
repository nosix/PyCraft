# -*- coding: utf8 -*-

from operator import attrgetter
from pycraft.service.primitive.values import Motion
from .base import Entity
from .player import PlayerEntity


class ItemEntity(Entity):
    
    def __init__(self, item):
        super().__init__()
        self._item = item

    def clone(self):
        o = super().clone()
        o._item = self._item.clone()
        return o

    item = property(attrgetter('_item'))

    motion = property(lambda self: Motion(self.eid, self.pos, 0, 0, 0))

    def does_push_out(self):
        return True

    def did_meet(self, entity):
        if not isinstance(entity, PlayerEntity):
            return False
        # TODO: 当たり判定を見直す
        d = self.pos.distance(entity.pos - (0,0,0.5))
        return d < 1.5
