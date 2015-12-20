# -*- coding: utf8 -*-

from pycraft.service.primitive.geometry import Position
from pycraft.service.part.accident import AttackByPlayer
from ..handler import TaskID


class PlayerWorld:
    
    def __init__(self, components, entity, hit_callback, lose_callback):
        self._is_over = components.scheduler.is_over
        self._datastore = components.datastore
        self._listener = components.listener
        self._entity = entity
        self._hit_callback = hit_callback
        self._lose_callback = lose_callback
        # player_id:int -> Player
        self._players = {}
        # 変更されたプレイヤーの一覧
        self._changed = set()

    def terminate(self):
        while self._store():
            pass
    
    def store(self):
        if not self._is_over(TaskID.STORE_PLAYER):
            self._store()
            
    def _store(self):
        """一人分のデータを保存する"""
        if len(self._changed) == 0:
            return False
        player_id = self._changed.pop()
        player = self._players[player_id]
        self._datastore.store_player(player)
        self._changed.discard(player_id)
        return True
    
    def _mark_changed(self, player_id):
        """変更されたプレイヤーを通知する"""
        self._changed.add(player_id)

    def __contains__(self, player_id):
        return player_id in self._players

    def __getitem__(self, key):
        return self._players[key]

    def __iter__(self):
        return iter(self._players.values())

    def add(self, player, seed):
        """新しいプレイヤーを追加する
        
        データストアにデータがある場合には
        データストアのデータをマージする。
        """
        player_id = player.player_id
        stored_player = self._datastore.load_player(player_id)
        if stored_player == None:
            player.spawn_pos = Position(128, 128, 71)
            player.spawn()
        else:
            player.copy_from(stored_player)
            if not player.is_living():
                player.spawn()
        player.meet_callback = self._hit_callback
        player.lose_callback = self._lose_callback
        self._players[player_id] = player
        self._entity.add(player)
        self._listener.player_loggedin(player, seed)

    def remove(self, player_id):
        """プレイヤーを削除する
        
        データストアに保存してから削除する。
        """
        player = self._players[player_id]
        self._entity.remove(player.eid)
        self._datastore.store_player(player)
        self._changed.discard(player_id)
        del self._players[player_id]
        self._listener.player_removed(player.eid, player.public_id)

    def move(self, player, motion, on_ground):
        """プレイヤーを移動する
        
        return : boolean - 生きていたら True
        """
        accident = self._entity.move(player, motion, on_ground, True)
        self._mark_changed(player.player_id)
        if accident != None:
            player.lose(accident)
            return False
        else:
            return True

    def lose(self, player, accident):
        self._listener.player_died(
            player.eid, player.spawn_pos, accident.death_msg)
        # アイテムを落とす
        self._entity.drop_items(player, accident)
        for slot in range(player.slots.SIZE):
            self._listener.inventory_updated(player, slot)
        # スポーン地点のChunkを返す
        self._listener.player_chunk_moved(player.player_id, player.spawn_pos)
        return list(player.spawn_pos.surrounding_chunk())

    def respawn(self, player):
        player.spawn()
        self._mark_changed(player.player_id)
        self._entity.respawn(player)
        self._listener.player_respawned(player)

    def use_item(self, player, target):
        held_hotbar, slot, _ = player.get_held_slot()
        if slot == player.HOTBAR_NONE:
            return
        slot_is_empty = player.slots.use_item(slot, target)
        self._mark_changed(player.player_id)
        self._listener.inventory_updated(player, slot)
        if slot_is_empty:
            player.set_hotbar(held_hotbar, player.HOTBAR_NONE)
            self._listener.player_equiped(player)

    def meet_item(self, player, entity):
        if not player.is_living():
            return
        # slot 更新
        updated_slot = player.slots.add_item(entity.item)
        if updated_slot == -1:
            return
        self._entity.remove_item(entity)
        self._mark_changed(player.player_id)
        self._listener.item_taken(entity, player)
        self._listener.inventory_updated(player, updated_slot)

    def equip_item(self, player, slot, held_hotbar):
        player.set_hotbar(held_hotbar, slot, True)
        player.hold(held_hotbar)
        self._mark_changed(player.player_id)
        self._listener.player_equiped(player)

    def edit_inventry(self, player, slot, item):
        player.slots[slot] = item
        self._mark_changed(player.player_id)

    def make_item(self, player, made_item, used_items):
        # アイテムを追加する
        updated_slot = player.slots.add_item(made_item)
        if updated_slot == -1:
            return
        self._listener.inventory_updated(player, updated_slot)
        # アイテムを削除する
        try:
            for slot, is_empty in player.slots.reduce_items(used_items):
                self._listener.inventory_updated(player, slot)
                if is_empty:
                    hotbar = player.find_hotbar(slot)
                    if hotbar != -1:
                        player.set_hotbar(hotbar, player.HOTBAR_NONE)
            self._mark_changed(player.player_id)
        except ValueError as e:
            print(e)
            player.slots.reduce_item(updated_slot)

    def attack_entity(self, player, eid):
        entity = self._entity.get(eid)
        if entity == None or not entity.is_living():
            return
        # Entity に傷をつける
        player.attack(entity)
        self._listener.entity_injured(entity.eid, entity.health)
        if not entity.is_living():
            entity.lose(AttackByPlayer(entity, player))
        # Tool を消耗させる
        self.use_item(player, entity)
