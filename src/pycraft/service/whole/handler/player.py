# -*- coding: utf8 -*-

import copy
from operator import attrgetter
from pycraft.common.util import iter_count
from pycraft.network import Reliability
from pycraft.service import logger
from pycraft.service.const import \
    GameMode, Difficulty, ContainerWindowID, EntityEventID
from pycraft.service.lang import ja
from pycraft.service.primitive.geometry import Vector
from pycraft.service.primitive.values import Motion
from pycraft.service.composite.entity import \
    PlayerEntity, MobEntity, ItemEntity
from .packet import send, both


class ChunkMonitor:

    PRIORITY_THRESHOLD = 8

    def __init__(self):
        # 未受信で必要としている Chunk の数
        self._require_num = -1
        # ChunkPosition -> priority (必要としている Chunk 一覧) 
        self._require_chunk = {}
        # 受信済み ChunkPosition
        self._curr_chunk = set()

    def is_ready(self):
        return self._require_num == 0

    def __contains__(self, chunk_pos):
        return chunk_pos in self._require_chunk

    def __delitem__(self, chunk_pos):
        priority = self._require_chunk.pop(chunk_pos)
        if priority <= self.PRIORITY_THRESHOLD:
            self._require_num -= 1
        self._curr_chunk.add(chunk_pos)

    def change_chunk_pos(self, pos):
        self._require_chunk = dict(
            (chunk_pos, priority) 
                for priority, chunk_pos in pos.surrounding_chunk())
        self._require_num = iter_count(
            p for p in self._require_chunk.values() 
                if p <= self.PRIORITY_THRESHOLD)
        next_chunk = set(self._require_chunk.keys())
        for chunk_pos in next_chunk & self._curr_chunk:
            del self._require_chunk[chunk_pos]
        for chunk_pos in self._curr_chunk - next_chunk:
            self._curr_chunk.remove(chunk_pos)

    def reset(self, chunks):
        renew = self._curr_chunk & chunks
        self._curr_chunk -= renew
        for chunk_pos in renew:
            self._require_chunk[chunk_pos] = self.PRIORITY_THRESHOLD + 1


class Player:
    
    OWN_EID = 0

    def __init__(self, handler, session, client_id, name):
        self._handler = handler
        self._session = session
        self._lang = ja
        self._client_id = client_id
        self._name = name
        self._eid = 0
        self._chunk = ChunkMonitor()
        self._spawned = False

    id = property(attrgetter('_client_id')) 
    name = property(attrgetter('_name'))

    def direct_text_packet(self, packet):
        packet = copy.deepcopy(packet)
        packet.tr(self._lang)
        self.direct_data_packet(packet, Reliability.RELIABLE_ORDERED)

    def direct_data_packet(self, packet, reliability, is_immediate=False):
        packet.encode()
        logger.server.debug(
            'H< {addr} {packet}', addr=self._session.addr, packet=packet)
        buffer = packet.buffer()
        if len(buffer) >= both.Batch.THRESHOLD:
            pk = both.Batch()
            pk.payloads = [buffer]
            packet = pk
        self._session.send_packet(packet, reliability, is_immediate)

    def send_full_chunk(self, updated_chunks):
        def chunk_buffer(chunk_pos, chunk_data):
            pk = send.FullChunkData()
            pk.pos = chunk_pos
            pk.chunk_data = chunk_data
            pk.encode()
            logger.server.debug(
                'H< {addr} {packet}', addr=self._session.addr, packet=pk)
            del self._chunk[chunk_pos]
            return pk.buffer()
        chunk_data = (
            chunk_buffer(chunk_pos, chunk_data)
                for chunk_pos, chunk_data in updated_chunks
                    if chunk_pos in self._chunk) 
        pk = both.Batch()
        pk.payloads = list(chunk_data)
        if len(pk.payloads) > 0:
            self._session.send_packet(pk, Reliability.RELIABLE_ORDERED, True)
        # Chunk の準備ができたらスポーンを要求する
        if not self._spawned and self._chunk.is_ready():
            self._handler.spawn(self._client_id)

    def change_chunk_pos(self, pos):
        self._chunk.change_chunk_pos(pos)

    def reset_chunk(self, updated_chunks):
        self._chunk.reset(updated_chunks)
        
    def to_packet_eid(self, eid):
        return eid if eid != self._eid else self.OWN_EID

    def close(self, reason):
        pk = send.Disconnect()
        pk.message = reason
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)

    def login(self, player, seed):
        print('login', self._name, player.pos)
        # ログイン成功
        pk = send.PlayStatus()
        pk.status = pk.LOGIN_SUCCESS
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)
        # ゲーム開始
        pk = send.StartGame()
        pk.seed = seed
        pk.generator = pk.GENERATOR_INFINITE
        pk.game_mode = GameMode.SURVIVAL
        pk.eid = player.eid
        pk.spawn = player.spawn_pos
        pk.pos = player.pos
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)
        # スポーン位置設定
        pk = send.SetSpawnPosition()
        pk.pos = player.spawn_pos
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)
        # 難易度設定
        pk = send.SetDifficulty()
        pk.difficulty = Difficulty.EASY
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)
        # 各種オプション設定
        pk = send.AdventureSettings()
        pk.is_adventure = False
        pk.show_nametag = False
        pk.auto_jump = True
        pk.allow_flight = False
        pk.is_spectator = False
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)
        # 割り振られたeidを記録
        self._eid = player.eid
        # Chunk の位置を設定
        self.change_chunk_pos(player.pos)

    def spawn(self, player, time):
        print('spawn', self._name, player.pos)
        # 時間設定
        pk = send.SetTime()
        pk.time = time
        pk.started = True
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)
        # 生命力設定
        pk = send.SetHealth()
        pk.health = player.health
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)
        # アイテムデータ送信(INVENTORY)
        pk = send.ContainerSetContent()
        pk.window_id = ContainerWindowID.INVENTORY
        pk.slots = player.slots
        pk.hotbar = player.hotbar
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)
        # アイテムデータ送信(ARMOR)
        pk = send.ContainerSetContent()
        pk.window_id = ContainerWindowID.ARMOR
        pk.slots = player.armor_slots
        pk.hotbar = []
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)
        # レシピデータを送信
        pk = send.RecipeData()
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)
        # スポーン
        pk = send.Respawn()
        pk.pos = player.pos
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)
        # スポーン通知
        pk = send.PlayStatus()
        pk.status = send.PlayStatus.PLAYER_SPAWN
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)
        # 動作の初期設定
        pk = both.MovePlayer()
        pk.motion = Motion(self.OWN_EID, player.pos, 0.0, 0.0, 0.0)
        pk.mode = pk.MODE_RESET
        pk.on_ground = False
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)
        # 状態を設定する
        self._spawned = True
    
    def create_animate_packet(self, action):
        pk = both.Animate()
        pk.eid = self._eid
        pk.action = action
        return pk

    def send_animate(self, packet):
        if packet.eid != self._eid:
            self.direct_data_packet(packet, Reliability.UNRELIABLE)

    def send_new_entities(self, entities):
        for entity in entities:
            if isinstance(entity, PlayerEntity):
                self.send_new_player(entity)
            elif isinstance(entity, MobEntity):
                self._send_new_mob(entity)
            elif isinstance(entity, ItemEntity):
                self.send_new_item(entity, Vector(0,0,0))

    def send_new_player(self, player):
        print('send_new_player', self._name, player.name)
        eid = self.to_packet_eid(player.eid)
        v0 = Vector(0,0,0)
        # EntityData
        pk = send.SetEntityData()
        pk.eid = eid
        pk.meta = player.meta
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)
        # EntityMotion
        pk = send.SetEntityMotion()
        pk.motions = {eid : v0}
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)
        # 自分自身の場合はここまで
        if eid == self.OWN_EID:
            return
        # AddPlayer
        pk = send.AddPlayer()
        pk.is_remove = False
        pk.players = [player]
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)
        # AddPlayer2
        pk = send.AddPlayer2()
        pk.public_id = player.public_id
        pk.user_name = player.name
        pk.eid = eid
        pk.pos = player.bottom_pos
        pk.speed = v0
        pk.yaw = player.yaw
        pk.head_yaw = player.head_yaw
        pk.pitch = player.pitch
        pk.item = player.get_held_item()
        pk.meta = player.meta
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)

    def send_removed_player(self, eid, public_id):
        print('send_removed_player', self._name, public_id)
        # RemovePlayer
        pk = send.RemovePlayer()
        pk.eid = eid
        pk.public_id = public_id
        pk.public_id2 = public_id
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)
        # AddPlayer
        pk = send.AddPlayer()
        pk.is_remove = True
        pk.players = [public_id]
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)

    def send_player_equiped(self, eid, held_hotbar, slot, item):
        if eid == self._eid:
            return
        print('send_player_equiped', self._name)
        pk = both.PlayerEquipment()
        pk.eid = eid
        pk.item = item
        pk.attr = item.attr
        pk.slot = slot
        pk.held_hotbar = held_hotbar
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)

    def send_updated_block(self, blocks):
        print('send_updated_block', self._name)
        pk = send.UpdateBlock()
        pk.records = blocks
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)

    def send_block_entities(self, block_entities):
        print('send_block_entities', self._name)
        for e in block_entities:
            pk = both.TileEntityData()
            pk.pos = e.pos
            pk.named_tag = e.named_tag
            self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)

    def send_new_item(self, entity, speed):
        print('send_new_item', self._name)
        pk = send.AddItemEntity()
        pk.eid = entity.eid
        pk.item = entity.item
        pk.pos = entity.pos
        pk.speed = speed
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)

    def send_taken_item(self, entity_eid, player_eid):
        player_eid = self.to_packet_eid(player_eid)
        print('send_taken_item', self._name)
        # TakeItemEntity
        pk = send.TakeItemEntity()
        pk.player_eid = player_eid
        pk.item_eid = entity_eid
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)
        # RemoveEntity
        pk = send.RemoveEntity()
        pk.eid = entity_eid
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)

    def send_inventory(self, updated_slot, item):
        print('send_inventory', self._name)
        pk = both.ContainerSetSlot()
        pk.window_id = ContainerWindowID.INVENTORY
        pk.slot = updated_slot
        pk.item = item
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)

    def send_container(self, pos, container):
        print('send_container', self._name)
        # ContainerOpen
        pk = send.ContainerOpen()
        pk.window_id = container.window_id
        pk.pos = pos
        pk.slots = len(container)
        pk.type = container.TYPE
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED, True)
        # ContainerSetContent
        pk = send.ContainerSetContent()
        pk.window_id = container.window_id
        pk.slots = container
        pk.hotbar = []
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED, True)

    def send_open_event(self, pos_list):
        print('send_open_event', self._name)
        for pos in pos_list:
            pk = send.TileEvent()
            pk.pos = pos
            pk.case1 = 1
            pk.case2 = 2
            self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)

    def send_closed_container(self, window_id):
        print('send_closed_container', self._name)
        pk = both.ContainerClose()
        pk.window_id = window_id
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)

    def send_close_event(self, pos_list):
        print('send_close_event', self._name)
        for pos in pos_list:
            pk = send.TileEvent()
            pk.pos = pos
            pk.case1 = 1
            pk.case2 = 0
            self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)

    def send_changed_container_slot(self, player_ids, window_id, slot, item):
        if self._client_id not in player_ids:
            return
        print('send_changed_container_slot', self._name)
        pk = both.ContainerSetSlot()
        pk.window_id = window_id
        pk.slot = slot
        pk.item = item
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)

    def send_container_data(self, player_ids, window_id, prop):
        if self._client_id not in player_ids:
            return
        print('send_container_data', self._name)
        for index, value in prop.items():
            pk = send.ContainerSetData()
            pk.window_id = window_id
            pk.property = index
            pk.value = value
            self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)

    def send_moved_entity(self, motions):
        motions = list(m for m in motions if m.eid != self._eid)
        if len(motions) == 0:
            return
        print('send_moved_entity', self._name)
        pk = send.MoveEntity()
        pk.motions = motions
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)
        pk = send.SetEntityMotion()
        pk.motions = dict((m.eid, Vector(0, 0, 0)) for m in motions)
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)
        
    def send_injured_entity(self, eid, health):
        print('send_injured_entity', self._name)
        eid = self.to_packet_eid(eid)
        if eid == self.OWN_EID:
            pk = send.SetHealth()
            pk.health = health
            self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)
        pk = send.EntityEvent()
        pk.eid = eid
        pk.event = EntityEventID.HURT_ANIMATION
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)

    def send_changed_entity(self, eid, meta):
        print('send_changed_entity', self._name)
        # EntityData
        pk = send.SetEntityData()
        pk.eid = eid
        pk.meta = meta
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)
        
    def send_new_mob(self, entities):
        print('send_new_mob', self._name)
        for e in entities:
            self._send_new_mob(e)

    def _send_new_mob(self, e):
        pk = send.AddEntity()
        pk.eid = e.eid
        pk.type = e.TYPE
        pk.pos = e.pos
        pk.speed = Vector(0,0,0)
        pk.yaw = e.yaw
        pk.pitch = e.pitch
        pk.meta = e.meta
        pk.links = []  # TODO: link を設定する
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)

    def send_removed_mob(self, eid):
        print('send_removed_mob', self._name)
        # RemoveEntity
        pk = send.RemoveEntity()
        pk.eid = eid
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)

    def send_died_entity(self, eid, spawn_pos=None):
        print('send_died_entity', self._name)
        if eid == self._eid:
            pk = send.Respawn()
            pk.pos = spawn_pos
            self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)
        else:
            pk = send.EntityEvent()
            pk.eid = eid
            pk.event = EntityEventID.DEATH_ANIMATION
            self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)

    def send_time(self, time):
        pk = send.SetTime()
        pk.time = time
        pk.started = True
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)

    def send_sound(self, event_id, pos, data):
        print('send_sound', self._name)
        pk = send.LevelEvent()
        pk.event_id = event_id
        pk.pos = pos
        pk.data = data
        self.direct_data_packet(pk, Reliability.RELIABLE_ORDERED)
