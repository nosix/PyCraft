# -*- coding: utf8 -*-

import time
from collections import defaultdict
from pycraft.service.part.accident import Fall
from pycraft.service.composite.entity import ItemEntity
from .law import MotionLaw


class EntityWorld:
    
    MOTION_NOTIFY_TICK = 0.1  # sec

    def __init__(self, components, hit_callback):
        self._listener = components.listener
        self._hit_callback = hit_callback
        self._entities = {}
        self._min_unused_eid = 1
        # eid:int
        self._moved_entity = set()
        self._moved_entity_waiting = set()
        # ChunkPosition -> ItemEntity.eid
        self._item_map = defaultdict(set)
        # MotionLaw
        self._motion_law = MotionLaw()
        # 最後に activate を実行した時間
        self._last_activate_time = time.clock()
    
    moved_entities = property(lambda self: self._moved_entities())

    def activate(self):
        t = time.clock()
        if t - self._last_activate_time >= self.MOTION_NOTIFY_TICK:
            self._moved_entity.update(self._moved_entity_waiting)
            self._moved_entity_waiting.clear()
            self._last_activate_time = t

    def notify_moved(self):
        if len(self._moved_entity) == 0:
            return
        motions = (self._entities[eid].motion
            for eid in self._moved_entity if eid in self._entities)
        self._listener.entity_moved(motions)
        self._moved_entity.clear()
        
    def _next_eid(self):
        eid = self._min_unused_eid
        next_eid = eid + 1
        while next_eid in self._entities:
            next_eid += 1
        self._min_unused_eid = next_eid
        return eid
    
    def _free_eid(self, eid):
        if eid < self._min_unused_eid:
            self._min_unused_eid = eid

    def __getitem__(self, eid):
        return self._entities[eid]

    def __iter__(self):
        return iter(self._entities.values())

    def get(self, eid):
        return self._entities.get(eid)

    def add(self, entity):
        entity.eid = self._next_eid()
        self._entities[entity.eid] = entity
    
    def remove(self, eid):
        self._moved_entity_waiting.discard(eid)
        self._moved_entity.discard(eid)
        if eid in self._entities:
            del self._entities[eid]
            self._free_eid(eid)
    
    def move(self, entity, motion, on_ground, immediate=False):
        """Entity を移動する
        
        return : Accident - 死んだ場合は死因、死んでいなければ None
        """
        # 位置と向きを変更する
        did_injure = entity.move(motion.pos, on_ground)
        entity.yaw = motion.yaw
        entity.head_yaw = motion.head_yaw
        entity.pitch = motion.pitch
        # 傷ついたことを通知する
        if did_injure:
            self._listener.entity_injured(entity.eid, entity.health)
            if not entity.is_living():
                return Fall(entity)
        # 移動したことを記録する
        if immediate:
            self._moved_entity.add(entity.eid)
        else:
            self._moved_entity_waiting.add(entity.eid)
        # Entityとの当たり判定
        for e in list(self._entities.values()):
            if entity.eid != e.eid and e.did_meet(entity):
                e.meet(entity)
        return None

    def respawn(self, entity):
        self._moved_entity.add(entity.eid)

    def drop_items(self, entity, accident):
        for item in entity.drop_items():
            speed = accident.direc_of_dropping(self._motion_law)
            self._add_item(item, entity.pos, speed)

    def spawn_item(self, item, pos, player_pos):
        speed = self._motion_law.direc_when_remove(player_pos, pos)
        self._add_item(item, pos, speed)
    
    def _add_item(self, item, pos, speed):
        entity = ItemEntity(item)
        entity.pos = pos.center_in_block
        entity.meet_callback = self._hit_callback
        self.add(entity)
        self._listener.item_added(entity, speed)
        # 初期位置を通知後にアイテムを移動する
        entity.pos += speed
        self._moved_entity.add(entity.eid)
        self._item_map[entity.pos.chunk_pos].add(entity.eid)

    def remove_item(self, entity):
        chunk_pos = entity.pos.chunk_pos
        self._item_map[chunk_pos].discard(entity.eid)
        if len(self._item_map[chunk_pos]) == 0:
            del self._item_map[chunk_pos]
        self.remove(entity.eid)
    
    def push_out_item(self, terrain):
        def push_out(entity):
            if not entity.does_push_out():
                return None
            pos = self._motion_law.move_when_chunk_changed(entity.pos, terrain)
            if pos != None:
                pos = self._motion_law.push_out(pos, entity.pos, terrain)
                from_pos = entity.pos
                entity.pos = pos
                return entity.eid, entity.pos, from_pos

        def entity_in_each_updated_chunk():
            for chunk_pos in terrain.updated_chunk:
                if chunk_pos in self._item_map:
                    for eid in self._item_map[chunk_pos]:
                        yield eid

        def each_updated_entity():
            updated_entities = \
                set(entity_in_each_updated_chunk()) | self._moved_entity
            for eid in updated_entities:
                updated = push_out(self._entities[eid])
                if updated != None:
                    yield updated

        for eid, pos, from_pos in each_updated_entity():
            self._item_map[from_pos.chunk_pos].discard(eid)
            self._item_map[pos.chunk_pos].add(eid)
            self._moved_entity.add(eid)

        terrain.clear_updated()