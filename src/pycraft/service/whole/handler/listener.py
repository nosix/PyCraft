# -*- coding: utf8 -*-

from pycraft.service import logger
from pycraft.service.primitive.values import Message
from .player import Player
from .queue import EventQueue
from .task import TaskID


class WorldEventListener:
    """世界の変更通知を受け取りプレイヤーに通知を振り分ける"""

    def __init__(self, handler):
        self._is_over = handler.scheduler.is_over
        self._handler = handler
        # Event Queue (コピーしたデータ/変更不可能なデータのみ設定する)
        self._update_queue = EventQueue()
        # 更新された Chunk Data を蓄積
        self._loaded_chunks = []

    def player_loggedin(self, player, seed):
        """Player がログインした
        
        player : PlayerEntity
        seed : int
        """
        self._update_queue.put(self._player_loggedin, player.clone(), seed)

    def player_spawned(self, player, time, entities):
        """Player がスポーンした
        
        player : PlayerEntity
        time : int
        entities : iterable(Entity)
        """
        es = [e.clone() for e in entities]
        self._update_queue.put(self._player_spawned, player.clone(), time, es)

    def player_respawned(self, player):
        """Player がリスポーンした
        
        player : PlayerEntity
        """
        self._update_queue.put(self._player_respawned, player.clone())

    def player_removed(self, eid, public_id):
        """Player が削除された
        
        eid : int
        public_id : bytes
        """
        self._update_queue.put(self._player_removed, eid, public_id)

    def player_chunk_moved(self, player_id, pos):
        """PlayerがChunkを移動した
        
        player_id : int
        pos : Position
        """
        self._update_queue.put(
            self._player_chunk_moved, player_id, pos)

    def player_equiped(self, player):
        """Playerが装具を変更した
        
        player : PlayerEntity
        """
        held_hotbar, slot, item = player.get_held_slot(True)
        self._update_queue.put(
            self._player_equiped, player.eid, held_hotbar, slot, item.clone())

    def player_died(self, eid, spawn_pos, msg):
        """Playerが死んだ
        
        spawn_pos : Position
        msg : Message
        """
        self._update_queue.put(
            self._player_died, eid, spawn_pos, msg.clone())

    def full_chunk_loaded(self, chunk, block_entities):
        """Chunkがロードされた
        
        chunk : Chunk
        block_entities : iterable(BlockEntity)
        """
        chunk_data = [chunk.data, bytes(4)]  # TODO: 確認する
        for e in block_entities:
            chunk_data.append(e.named_tag)
        self._loaded_chunks.append((chunk.pos, b''.join(chunk_data)))
    
    def chunk_updated(self, updated_chunks):
        """Chunkが変更された
        
        updated_chunks : set(ChunkPosition)
        """
        self._update_queue.put(self._chunk_updated, set(updated_chunks))

    def block_updated(self, blocks):
        """Blockが更新された
        
        blocks : iterable(BlockRecord)
        """
        blocks = list(blocks)
        self._update_queue.put(self._block_updated, blocks)

    def block_entity_updated(self, block_entities):
        """BlockEntityが更新された
        
        block_entities : iterable(BlockEntity)
        """
        block_entities = [e.clone() for e in block_entities]
        self._update_queue.put(self._block_entity_updated, block_entities)

    def item_added(self, entity, speed):
        """Itemが追加された
        
        entity : ItemEntity
        speed : Position(float)
        """
        self._update_queue.put(self._item_added, entity.clone(), speed)
    
    def item_taken(self, entity, player):
        """Itemが拾われた
        
        entity : ItemEntity
        player : PlayerEntity
        """
        self._update_queue.put(self._item_taken, entity.eid, player.eid)

    def inventory_updated(self, player, updated_slot):
        """Inventoryが更新された

        player : PlayerEntity
        updated_slot : int
        """
        self._update_queue.put(
            self._inventory_updated, player.player_id,
            updated_slot, player.slots[updated_slot].clone())

    def container_opened(self, player_id, pos, container, did_open):
        """PlayerがContainerを開いた
        
        player_id : int
        pos : Position
        container : Container
        did_open : boolean プレイヤーが蓋を開いた
        """
        container = container.clone()
        self._update_queue.put(
            self._container_opened, player_id, pos, container, did_open)

    def container_closed(self, player_id, pos_list, window_id, did_close):
        """PlayerがContainerを閉じた
        
        player_id : int
        pos_list : iterable(Position)
        window_id : int
        did_close : boolean
        """
        pos_list = list(pos_list)
        self._update_queue.put(
            self._container_closed, player_id, pos_list, window_id, did_close)

    def container_changed(self, player_ids, window_id, slot, item):
        """Containerの内容が変更された
        
        player_ids : iterable(int) - list of player_id
        window_id : int - Container.window_id
        slot : int - index of Container
        item : Item
        """
        player_ids = set(player_ids)
        self._update_queue.put(
            self._container_changed, player_ids, window_id, slot, item.clone())

    def container_broken(self, window_id):
        """Containerが壊された
        
        window_id : int
        """
        self._update_queue.put(self._container_broken, window_id)

    def furnace_burning(self, player_ids, window_id, prop):
        """Furnaceが燃焼している
        
        player_ids : iterable(int) - list of player_id
        window_id : int - Container.window_id
        prop : dict(int,int) - Container Data
        """
        player_ids = set(player_ids)
        self._update_queue.put(
            self._furnace_burning, player_ids, window_id, dict(prop))

    def entity_moved(self, motions):
        """Entityが移動した
        
        motions : iterable(Motion)
        """
        self._update_queue.put(self._entity_moved, list(motions))

    def entity_injured(self, eid, health):
        """Entityが傷ついた
        
        eid : int
        health : int
        """
        self._update_queue.put(self._entity_injured, eid, health)

    def entity_changed(self, eid, meta):
        """Entityのデータが変更された"""
        self._update_queue.put(self._entity_changed, eid, meta.clone())

    def mob_added(self, entities):
        """MobEntityが追加された
        
        entities : iterable(Entity)
        """
        entities = [e.clone() for e in entities]
        self._update_queue.put(self._mob_added, entities)

    def mob_removed(self, eid):
        """MobEntityが削除された
        
        eid : int
        """
        self._update_queue.put(self._mob_removed, eid)

    def mob_died(self, eid):
        """Mobが死んだ
        
        eid : int
        """
        self._update_queue.put(self._mob_died, eid)

    def time_updated(self, mc_time):
        """時間が更新された
        
        mc_time : int - MineCraft time
        """
        self._update_queue.put(self._time_updated, mc_time)
        
    def sounded(self, event_id, pos, data):
        """音が鳴った
        
        event_id : int
        pos : Position
        data : 
        """
        self._update_queue.put(self._sounded, event_id, pos, data)

    def update(self):
        def is_not(empty_func):
            return not empty_func() and \
                not self._is_over(TaskID.UPDATE_LISTENER)
        while is_not(self._update_queue.empty):
            self._update_queue.exec_next()
        self._notify_chunk_data()
        if len(self._update_queue) > 0:
            logger.server.debug(
                'WorldEventListener has {n} tasks.',
                    n=len(self._update_queue))

    def _notify_chunk_data(self):
        updated_chunks = self._loaded_chunks
        self._loaded_chunks = []
        self._handler.broadcast(Player.send_full_chunk, updated_chunks)

    def _player_loggedin(self, player, seed):
        self._handler.unicast(Player.login, player.player_id, player, seed)

    def _player_spawned(self, player, time, entities):
        player_id = player.player_id
        self._handler.unicast(Player.spawn, player_id, player, time)
        self._handler.unicast(Player.send_new_entities, player_id, entities)
        self._handler.broadcast(Player.send_new_entities, [player])
        msg = Message(
            Message.Esc.YELLOW + '%multiplayer.player.joined',
            player.name, is_raw=False)
        self._handler.notify(msg)

    def _player_respawned(self, player):
        self._handler.broadcast(Player.send_new_entities, [player])

    def _player_removed(self, eid, public_id):
        self._handler.broadcast(Player.send_removed_player, eid, public_id)

    def _player_chunk_moved(self, player_id, pos):
        self._handler.unicast(Player.change_chunk_pos, player_id, pos)

    def _player_equiped(self, eid, held_hotbar, slot, item):
        self._handler.broadcast(
            Player.send_player_equiped, eid, held_hotbar, slot, item)

    def _player_died(self, eid, spawn_pos, msg):
        self._handler.notify(msg)
        self._handler.broadcast(Player.send_died_entity, eid, spawn_pos)
        
    def _chunk_updated(self, updated_chunks):
        self._handler.broadcast(Player.reset_chunk, updated_chunks)

    def _block_updated(self, blocks):
        self._handler.broadcast(Player.send_updated_block, blocks)
    
    def _block_entity_updated(self, block_entities):
        self._handler.broadcast(Player.send_block_entities, block_entities)
    
    def _item_added(self, entity, speed):
        self._handler.broadcast(Player.send_new_item, entity, speed)
    
    def _item_taken(self, entity_eid, player_eid):
        self._handler.broadcast(Player.send_taken_item, entity_eid, player_eid)
    
    def _inventory_updated(self, player_id, updated_slot, item):
        self._handler.unicast(
            Player.send_inventory, player_id, updated_slot, item)
    
    def _container_opened(self, player_id, pos, container, did_open):
        self._handler.unicast(Player.send_container, player_id, pos, container)
        if did_open:
            self._handler.broadcast(Player.send_open_event, container.pos)

    def _container_closed(self, player_id, pos_list, window_id, did_close):
        self._handler.unicast(
            Player.send_closed_container, player_id, window_id)
        if did_close:
            self._handler.broadcast(Player.send_close_event, pos_list)

    def _container_changed(self, player_ids, window_id, slot, item):
        self._handler.broadcast(
            Player.send_changed_container_slot,
            player_ids, window_id, slot, item)

    def _container_broken(self, window_id):
        self._handler.broadcast(Player.send_closed_container, window_id)

    def _furnace_burning(self, player_ids, window_id, prop):
        self._handler.broadcast(
            Player.send_container_data, player_ids, window_id, prop)

    def _entity_moved(self, motions):
        self._handler.broadcast(Player.send_moved_entity, motions)

    def _entity_injured(self, eid, health):
        self._handler.broadcast(Player.send_injured_entity, eid, health)

    def _entity_changed(self, eid, meta):
        self._handler.broadcast(Player.send_changed_entity, eid, meta)

    def _mob_added(self, entities):
        self._handler.broadcast(Player.send_new_mob, entities)

    def _mob_removed(self, eid):
        self._handler.broadcast(Player.send_removed_mob, eid)

    def _mob_died(self, eid):
        self._handler.broadcast(Player.send_died_entity, eid)

    def _time_updated(self, time):
        self._handler.broadcast(Player.send_time, time)
        
    def _sounded(self, event_id, pos, data):
        self._handler.broadcast(Player.send_sound, event_id, pos, data)
