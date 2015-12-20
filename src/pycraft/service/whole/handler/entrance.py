# -*- coding: utf8 -*-

from pycraft.service import logger
from ..world import World
from .queue import EventQueue
from .task import TaskID


class WorldEntrance:
    
    def __init__(self, components):
        self._is_over = components.scheduler.is_over
        self._world = World(components)
        # Event Queue (コピーしたデータ/変更不可能なデータのみ設定する)
        self._update_queue = EventQueue()
        # Event Queue (次の更新で実行するコマンド)
        self._next_update_queue = EventQueue()

    def start(self):
        self._world.start()

    def terminate(self):
        self._world.terminate()

    def update(self):
        # 時計を進める
        self._world.tick()
        # EventQueue を処理する
        def is_not(empty_func):
            return not empty_func() and \
                not self._is_over(TaskID.UPDATE_ENTRANCE)
        while is_not(self._update_queue.empty):
            waiting = self._update_queue.exec_next()
            if waiting != None:
                self._next_update_queue.put(*waiting)
        # 世界を更新する
        self._world.update()
        # 待機中のコマンドを次回処理にまわす
        while not self._next_update_queue.empty():
            method, param = self._next_update_queue.get()
            self._update_queue.put(method, *param)
        if len(self._update_queue) > 0:
            logger.server.debug(
                'WorldEntrance has {n} tasks.', n=len(self._update_queue))
        
    def add_player(self, player_id, public_id, name, skin_name, skin):
        self._update_queue.put(
            self._world.add_player,
            player_id, public_id, name, skin_name, skin)

    def spawn_player(self, player_id):
        self._update_queue.put(self._world.spawn_player, player_id)

    def remove_player(self, player_id):
        self._update_queue.put(self._world.remove_player, player_id)

    def respawn_player(self, player_id):
        self._update_queue.put(self._world.respawn_player, player_id)

    def move_player(self, player_id, motion, on_ground):
        self._update_queue.put(
            self._world.move_player, player_id, motion, on_ground)

    def equip_item(self, player_id, slot, held_hotbar):
        self._update_queue.put(
            self._world.equip_item, player_id, slot, held_hotbar)

    def remove_block(self, player_id, pos):
        self._update_queue.put(self._world.remove_block, player_id, pos)

    def put_item(self, player_id, pos, face, item_id):
        self._update_queue.put(
            self._world.put_item, player_id, pos, face, item_id)

    def make_item(self, player_id, made_item, used_items):
        made_item = made_item.clone()
        used_items = [item.clone() for item in used_items]
        self._update_queue.put(
            self._world.make_item, player_id, made_item, used_items)

    def edit_container(self, player_id, window_id, slot, item):
        self._update_queue.put(
            self._world.edit_container,
            player_id, window_id, slot, item.clone())
    
    def close_container(self, player_id, window_id):
        self._update_queue.put(
            self._world.close_container, player_id, window_id)

    def edit_sign(self, pos, named_tag):
        self._update_queue.put(self._world.edit_sign, pos, named_tag)

    def attack_entity(self, eid, player_id):
        self._update_queue.put(self._world.attack_entity, eid, player_id)
