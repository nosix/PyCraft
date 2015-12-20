# -*- coding: utf8 -*-

from pycraft.service import config
from pycraft.service.const import ContainerWindowID
from pycraft.service.part.block import new_block
from pycraft.service.composite import populator
from pycraft.service.composite.entity import PlayerEntity
from .entity import EntityWorld
from .player import PlayerWorld
from .map import ChunkMap
from .terrain import Terrain
from .mob import MobWorld, DisabledMobWorld


class World:
    
    def __init__(self, components):
        self._seed = config.seed
        self._datastore = components.datastore
        self._listener = components.listener
        self._clock = components.clock
        # 全てのEntityを保存
        self._entity = EntityWorld(components, self.meet_item)
        # 全てのPlayerを保存
        self._player = PlayerWorld(
            components, self._entity, self.meet_player, self.lose_player)
        # TerrainMap
        self._map = ChunkMap()
        # Terrain
        self._terrain = Terrain(components, self._map, self._seed)
        # Mob
        self._mob = MobWorld(
            components, self._terrain, self._entity, self._player,
            self.meet_mob, self.lose_mob) \
                if config.spawn_mob else DisabledMobWorld()
        # populator を登録
        populator.regist()

    def start(self):
        self._datastore.start()
        self._terrain.start()
        self._mob.start()
    
    def terminate(self):
        self._player.terminate()
        self._mob.terminate()
        self._terrain.terminate()
        self._datastore.terminate()
    
    def tick(self):
        if self._clock.update():
            self._listener.time_updated(self._clock.time)

    def update(self):
        self._terrain.update()
        self._mob.spawn()
        self._mob.move()
        self._entity.activate()
        self._entity.push_out_item(self._terrain)
        self._entity.notify_moved()
        self._terrain.store()
        self._player.store()

    def add_player(self, player_id, public_id, name, skin_name, skin):
        player = PlayerEntity(player_id, public_id, skin_name, skin)
        player.name = name
        # ログアウトせずに残っているプレイヤーを削除する
        if player.player_id in self._player:
            self.remove_player(player.player_id)
        # プレイヤーを追加する
        self._player.add(player, self._seed)
        for p in self._map.move_player(player):
            self._terrain.load(p)

    def spawn_player(self, player_id):
        player = self._player[player_id]
        player.spawn(
            self._terrain.get_ground_pos(player.pos.astype(int)))
        self._listener.player_spawned(
            player, self._clock.time, self._entity)

    def remove_player(self, player_id):
        player = self._player[player_id]
        if player.opening_container:
            self._close_container(player_id, player.opening_container)
        self._map.remove_player(player)
        self._player.remove(player_id)

    def respawn_player(self, player_id):
        player = self._player[player_id]
        self._player.respawn(player)

    def move_player(self, player_id, motion, on_ground):
        player = self._player[player_id]
        if not self._player.move(player, motion, on_ground):
            return
        surrounding_chunk = self._map.move_player(player)
        # 異なるChunkに移動した場合、地形を読み込む
        if len(surrounding_chunk) != 0:
            self._listener.player_chunk_moved(player_id, player.pos)
            for p in surrounding_chunk:
                self._terrain.load(p)
    
    def equip_item(self, player_id, slot, held_hotbar):
        player = self._player[player_id]
        self._player.equip_item(player, slot, held_hotbar)

    def remove_block(self, player_id, pos):
        player = self._player[player_id]
        # プレイヤーの装備を更新する
        self._player.use_item(player, self._terrain.get_block(pos))
        # ブロックを削除し、アイテムを生成する
        for item in self._terrain.remove_block(pos, player.pos):
            self._entity.spawn_item(item, pos, player.pos)

    def put_item(self, player_id, pos, face, item_id):
        player = self._player[player_id]
        # ブロックに触れてアイテムを設置できるか確認する
        if not self._terrain.touch_block(player, pos):
            return
        # 所持しているアイテムが使用されたことを確認する
        _, slot, item = player.get_held_slot()
        if item.id != item_id:
            raise ValueError('put_item {0} != {1}'.format(item.id, item_id))
        if slot == player.HOTBAR_NONE:
            return
        # ブロックを生成するアイテムであることを確認する
        block_id = item.to_block(face)
        if block_id == None:
            print('{item} does not become block.'.format(item=item))
            return
        # ブロックを生成して地形に追加する
        block = new_block(
            block_id, attach_face=face,
            player_face=player.face, player_yaw=player.head_yaw)
        self._terrain.add_block(pos.by_face(face), block)

    def make_item(self, player_id, made_item, used_items):
        player = self._player[player_id]
        self._player.make_item(player, made_item, used_items)

    def edit_container(self, player_id, window_id, slot, item):
        if window_id == ContainerWindowID.INVENTORY:
            player = self._player[player_id]
            self._player.edit_inventry(player, slot, item)
        else:
            self._terrain.block_entity.edit_container(window_id, slot, item)

    def close_container(self, player_id, window_id):
        player = self._player[player_id]
        self._terrain.block_entity.close_container(window_id, player)

    def edit_sign(self, pos, named_tag):
        self._terrain.block_entity.edit_sign(pos, named_tag)

    def attack_entity(self, eid, player_id):
        player = self._player[player_id]
        self._player.attack_entity(player, eid)

    def meet_item(self, entity, player):
        self._player.meet_item(player, entity)

    def meet_player(self, player, entity):
        self._mob.attack_entity(entity, player)

    def meet_mob(self, mob, entity):
        pass

    def lose_player(self, player, accident):
        for p in self._player.lose(player, accident):
            self._terrain.load(p)

    def lose_mob(self, mob, accident):
        self._mob.lose(mob, accident)