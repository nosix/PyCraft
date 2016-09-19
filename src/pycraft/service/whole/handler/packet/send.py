# -*- coding: utf8 -*-

from binascii import hexlify as hex
from pycraft.service.primitive.geometry import ChunkPosition
from pycraft.service.primitive.values import BlockRecord
from pycraft.service.part.recipe import recipe_data
from .base import Packet
from .ids import ID


class PlayStatus(Packet):
    
    __slots__ = ['status']

    id = ID.PLAY_STATUS

    LOGIN_SUCCESS = 0
    LOGIN_FAILED_CLIENT = 1
    LOGIN_FAILED_SERVER = 2
    PLAYER_SPAWN = 3
    
    def encode(self):
        super().encode()
        self._buffer.put_int(self.status)

    def decode(self):
        super().decode()
        self.status = self._buffer.next_int()


class Disconnect(Packet):
    
    __slots__ = ['message']

    id = ID.DISCONNECT

    def encode(self):
        super().encode()
        self._buffer.put_str(self.message)

    def decode(self):
        super().decode()
        self.message = self._buffer.next_str()


class StartGame(Packet):
    
    __slots__ = [
        'seed', 'generator', 'game_mode', 'eid', 'spawn', 'pos',
        'unknown1', 'unknown2', 'unknown3']

    id = ID.START_GAME

    GENERATOR_INFINITE = 1
    GENERATOR_FLAT = 2
    
    def encode(self):
        super().encode()
        self._buffer.put_int(self.seed)
        self._buffer.put_byte(0)  # TODO: 対応する
        self._buffer.put_int(self.generator)
        self._buffer.put_int(self.game_mode & 0x01)
        self._buffer.put_long(self.eid)
        self._buffer.put_int_pos(self.spawn)
        self._buffer.put_pos(self.pos)
        self._buffer.put_byte(0)  # TODO: 対応する
        self._buffer.put_int(0)  # TODO: 対応する

    def decode(self):
        super().decode()
        self.seed = self._buffer.next_int()
        self.unknown1 = self._buffer.next_byte()  # TODO: 対応する
        self.generator = self._buffer.next_int()
        self.game_mode = self._buffer.next_int()
        self.eid = self._buffer.next_long()
        self.spawn = self._buffer.next_int_pos()
        self.pos = self._buffer.next_pos()
        self.unknown2 = self._buffer.next_byte()  # TODO: 対応する
        self.unknown3 = self._buffer.next_int()  # TODO: 対応する


class AdventureSettings(Packet):
    
    __slots__ = [
        'is_adventure',
        'show_nametag',
        'auto_jump',
        'allow_flight',
        'is_spectator',
        ]

    id = ID.ADVENTURE_SETTINGS

    FLAG_IS_ADVENTURE = 0x01  # Do not allow placing/breaking blocks
    FLAG_SHOW_NAMETAG = 0x20
    FLAG_AUTO_JUMP = 0x40
    FLAG_ALLOW_FLIGHT = 0x80
    FLAG_IS_SPECTATOR = 0x100

    def encode(self):
        super().encode()
        flags = 0
        flags |= self.FLAG_IS_ADVENTURE if self.is_adventure else 0
        flags |= self.FLAG_SHOW_NAMETAG if self.show_nametag else 0
        flags |= self.FLAG_AUTO_JUMP if self.auto_jump else 0
        flags |= self.FLAG_ALLOW_FLIGHT if self.allow_flight else 0
        flags |= self.FLAG_IS_SPECTATOR if self.is_spectator else 0
        self._buffer.put_int(flags)

    def decode(self):
        super().decode()
        flags = self._buffer.next_int()
        self.is_adventure = (flags & self.FLAG_IS_ADVENTURE) > 0
        self.show_nametag = (flags & self.FLAG_SHOW_NAMETAG) > 0
        self.auto_jump = (flags & self.FLAG_AUTO_JUMP) > 0
        self.allow_flight = (flags & self.FLAG_ALLOW_FLIGHT) > 0
        self.is_spectator = (flags & self.FLAG_IS_SPECTATOR) > 0


class SetDifficulty(Packet):
    
    __slots__ = ['difficulty']

    id = ID.SET_DIFFICULTY

    def encode(self):
        super().encode()
        self._buffer.put_int(self.difficulty)

    def decode(self):
        super().decode()
        self.difficulty = self._buffer.next_int()


class SetSpawnPosition(Packet):
    
    __slots__ = ['pos']

    id = ID.SET_SPAWN_POSITION

    def encode(self):
        super().encode()
        self._buffer.put_int_pos(self.pos)

    def decode(self):
        super().decode()
        self.pos = self._buffer.next_int_pos()


class Respawn(Packet):

    __slots__ = ['pos']    

    id = ID.RESPAWN

    def encode(self):
        super().encode()
        self._buffer.put_pos(self.pos)

    def decode(self):
        super().decode()
        self.pos = self._buffer.next_pos()


class SetTime(Packet):
    
    __slots__ = ['time', 'started']

    id = ID.SET_TIME

    def encode(self):
        super().encode()
        self._buffer.put_int(self.time)
        self._buffer.put_byte(0x80 if self.started else 0x00)

    def decode(self):
        super().decode()
        self.time = self._buffer.next_int()
        self.started = (self._buffer.next_byte() == 0x80)


class SetHealth(Packet):

    __slots__ = ['health']    

    id = ID.SET_HEALTH

    def encode(self):
        super().encode()
        self._buffer.put_int(self.health)

    def decode(self):
        super().decode()
        self.health = self._buffer.next_int()


class AddPlayer(Packet):
    
    __slots__ = ['is_remove', 'players']

    id = ID.ADD_PLAYER

    def _put_player(self, player):
        self._buffer.put(player.public_id)
        self._buffer.put_long(player.eid) 
        self._buffer.put_str(player.name)
        self._buffer.put_str(player.skin_name)
        self._buffer.put_bytes(player.skin)

    def _next_player(self):
        return dict(
            public_id = hex(self._buffer.next(16)),
            eid = self._buffer.next_long(),
            user_name = self._buffer.next_str(),
            skin_name = self._buffer.next_str(),
            skin = self._buffer.next_bytes())
        
    def encode(self):
        super().encode()
        self._buffer.put_byte(1 if self.is_remove else 0)
        self._buffer.put_int(len(self.players))
        if self.is_remove:
            for player in self.players:
                self._buffer.put(player)
        else:
            for player in self.players:
                self._put_player(player)
        
    def decode(self):
        super().decode()
        self.is_remove = self._buffer.next_byte() > 0
        if self.is_remove:
            self.players = [self._buffer.next(16)
                for _ in range(self._buffer.next_int())]
        else:
            self.players = [self._next_player()
                for _ in range(self._buffer.next_int())]

class AddPlayer2(Packet):
    
    __slots__ = [
        'public_id', 'user_name', 'eid',
        'pos', 'speed', 'yaw', 'head_yaw', 'pitch',
        'item', 'meta'
    ]

    id = ID.ADD_PLAYER2

    def encode(self):
        super().encode()
        self._buffer.put(self.public_id)
        self._buffer.put_str(self.user_name)
        self._buffer.put_long(self.eid) 
        self._buffer.put_pos(self.pos) 
        self._buffer.put_direc(self.speed) 
        self._buffer.put_float(self.yaw) 
        self._buffer.put_float(self.head_yaw) 
        self._buffer.put_float(self.pitch) 
        self._buffer.put_item(self.item) 
        self._buffer.put_meta(self.meta) 
        
    def decode(self):
        super().decode()
        self.public_id = self._buffer.next(16)
        self.user_name = self._buffer.next_str()
        self.eid = self._buffer.next_long()
        self.pos = self._buffer.next_pos()
        self.speed = self._buffer.next_direc()
        self.yaw = self._buffer.next_float()
        self.head_yaw = self._buffer.next_float()
        self.pitch = self._buffer.next_float()
        self.item = self._buffer.next_item()
        self.meta = self._buffer.next_meta()


class RemovePlayer(Packet):
     
    __slots__ = ['eid', 'public_id', 'public_id2']
 
    id = ID.REMOVE_PLAYER
 
    def encode(self):
        super().encode()
        self._buffer.put_long(self.eid)
        self._buffer.put(self.public_id)
        self._buffer.put(self.public_id2)
 
    def decode(self):
        super().decode()
        self.eid = self._buffer.next_long()
        self.public_id = self._buffer.next(16)
        self.public_id2 = self._buffer.next(16)


class AddEntity(Packet):
    
    __slots__ = [
        'eid', 'type', 'pos', 'speed', 'yaw', 'pitch', 'meta', 'links']

    id = ID.ADD_ENTITY

    def encode(self):
        super().encode()
        self._buffer.put_long(self.eid)
        self._buffer.put_int(self.type)
        self._buffer.put_pos(self.pos)
        self._buffer.put_direc(self.speed)
        self._buffer.put_float(self.yaw)
        self._buffer.put_float(self.pitch)
        self._buffer.put_meta(self.meta)
        self._buffer.put_short(len(self.links))
        # 用途不明
        for link in self.links:
            self._buffer.put_long(link[0])
            self._buffer.put_long(link[1])
            self._buffer.put_byte(link[2])
    
    def decode(self):
        super().decode()
        self.eid = self._buffer.next_long()
        self.type = self._buffer.next_int()
        self.pos = self._buffer.next_pos()
        self.speed = self._buffer.next_direc()
        self.yaw = self._buffer.next_float()
        self.pitch = self._buffer.next_float()
        self.meta = self._buffer.next_meta()
        # 用途不明
        self.links = [
            (self._buffer.next_long(),
             self._buffer.next_long(),
             self._buffer.next_byte())
                for _ in range(self._buffer.next_short())]


class RemoveEntity(Packet):

    __slots__ = ['eid']    

    id = ID.REMOVE_ENTITY

    def encode(self):
        super().encode()
        self._buffer.put_long(self.eid)

    def decode(self):
        super().decode()
        self.eid = self._buffer.next_long()


class AddItemEntity(Packet):

    __slots__ = ['eid', 'item', 'pos', 'speed']    

    id = ID.ADD_ITEM_ENTITY

    def encode(self):
        super().encode()
        self._buffer.put_long(self.eid)
        self._buffer.put_item(self.item)
        self._buffer.put_pos(self.pos)
        self._buffer.put_direc(self.speed)

    def decode(self):
        super().decode()
        self.eid = self._buffer.next_long()
        self.item = self._buffer.next_item()
        self.pos = self._buffer.next_pos()
        self.speed = self._buffer.next_direc()


class TakeItemEntity(Packet):
    
    __slots__ = ['item_eid', 'player_eid']

    id = ID.TAKE_ITEM_ENTITY

    def encode(self):
        super().encode()
        self._buffer.put_long(self.item_eid)
        self._buffer.put_long(self.player_eid)
    
    def decode(self):
        super().decode()
        self.item_eid = self._buffer.next_long()
        self.player_eid = self._buffer.next_long()


class MoveEntity(Packet):
    
    __slots__ = ['motions']

    id = ID.MOVE_ENTITY

    def encode(self):
        super().encode()
        self._buffer.put_int(len(self.motions))
        for m in self.motions:
            self._buffer.put_motion(m)

    def decode(self):
        super().decode()
        num = self._buffer.next_int()
        self.motions = [self._buffer.next_motion() for _ in range(num)]


class EntityEvent(Packet):
    
    __slots__ = ['eid', 'event']

    id = ID.ENTITY_EVENT

    def encode(self):
        super().encode()
        self._buffer.put_long(self.eid)
        self._buffer.put_byte(self.event)

    def decode(self):
        super().decode()
        self.eid = self._buffer.next_long()
        self.event = self._buffer.next_byte()


class SetEntityData(Packet):
    
    __slots__ = ['eid', 'meta']

    id = ID.SET_ENTITY_DATA

    def encode(self):
        super().encode()
        self._buffer.put_long(self.eid)
        self._buffer.put_meta(self.meta)

    def decode(self):
        super().decode()
        self.eid = self._buffer.next_long()
        self.meta = self._buffer.next_meta()


class SetEntityMotion(Packet):
    
    __slots__ = ['motions']

    id = ID.SET_ENTITY_MOTION

    def encode(self):
        super().encode()
        self._buffer.put_int(len(self.motions))
        for eid, direction in self.motions.items():
            self._buffer.put_long(eid)
            self._buffer.put_direc(direction)

    def decode(self):
        super().decode()
        length = self._buffer.next_int()
        def entity_motions():
            for _ in range(length):
                eid = self._buffer.next_long()
                direc = self._buffer.next_direc()
                yield (eid, direc)
        self.motions = dict(entity_motions())


class SetEntityLink(Packet):
    
    id = ID.SET_ENTITY_LINK


class MobEffect(Packet):
    
    id = ID.MOB_EFFECT
    
    __slots__ = [
        'eid', 'event_id', 'effect_id', 'amplifier', 'particles', 'duration'
    ]

    def encode(self):
        super().encode()
        self._buffer.put_long(self.eid)
        self._buffer.put_byte(self.event_id)
        self._buffer.put_byte(self.effect_id)
        self._buffer.put_byte(self.amplifire)
        self._buffer.put_byte(1 if self.particles else 0)
        self._buffer.put_int(self.duration)
    
    def decode(self):
        super().decode()
        self.eid = self._buffer.next_long()
        self.event_id = self._buffer.next_byte()
        self.effect_id = self._buffer.next_byte()
        self.amplifire = self._buffer.next_byte()
        self.particles = self._buffer.next_byte() > 0
        self.duration = self._buffer.next_int()


class Explode(Packet):
    
    id = ID.EXPLODE


class HurtArmor(Packet):
    
    id = ID.HURT_ARMOR


class FullChunkData(Packet):
    
    __slots__ = ['pos', 'unknown', 'chunk_data']

    id = ID.FULL_CHUNK_DATA

    def encode(self):
        super().encode()
        self._buffer.put_int(self.pos.x)
        self._buffer.put_int(self.pos.z)
        self._buffer.put_byte(0)  # TODO: 調べる 
        self._buffer.put_int(len(self.chunk_data))
        self._buffer.put(self.chunk_data)

    def decode(self):
        super().decode()
        self.pos = ChunkPosition(
            self._buffer.next_int(), self._buffer.next_int())
        self.unknown = self._buffer.next_byte() # TODO: 調べる
        self.chunk_data = self._buffer.next(self._buffer.next_int())


class UpdateBlock(Packet):
    
    __slots__ = ['records']

    id = ID.UPDATE_BLOCK

    def _put_block(self, record):
        self._buffer.put_int(record.x)
        self._buffer.put_int(record.z)
        self._buffer.put_byte(record.y)
        self._buffer.put_byte(record.id)
        self._buffer.put_byte((record.flags << 4) | record.attr)

    def _next_block(self):
        x = self._buffer.next_int()
        z = self._buffer.next_int()
        y = self._buffer.next_byte()
        id_ = self._buffer.next_byte()
        data = self._buffer.next_byte()
        return BlockRecord(x, z, y, id_, data & 0xF, data >> 4)

    def encode(self):
        super().encode()
        self._buffer.put_int(len(self.records))
        for r in self.records:
            self._put_block(r)

    def decode(self):
        super().decode()
        self.records = [
            self._next_block() for _ in range(self._buffer.next_int())]


class LevelEvent(Packet):

    __slots__ = ['event_id', 'pos', 'data']    

    id = ID.LEVEL_EVENT

    def encode(self):
        super().encode()
        self._buffer.put_short(self.event_id)
        self._buffer.put_pos(self.pos)
        self._buffer.put_int(self.data)
    
    def decode(self):
        super().decode()
        self.event_id = self._buffer.next_short()
        self.pos = self._buffer.next_pos()
        self.data = self._buffer.next_int()


class TileEvent(Packet):
    
    __slots__ = ['pos', 'case1', 'case2']

    id = ID.TILE_EVENT

    def encode(self):
        super().encode()
        self._buffer.put_int_pos(self.pos)
        self._buffer.put_int(self.case1)
        self._buffer.put_int(self.case2)
    
    def decode(self):
        super().decode()
        self.pos = self._buffer.next_int_pos()
        self.case1 = self._buffer.next_int()
        self.case2 = self._buffer.next_int()


class ContainerOpen(Packet):
    
    __slots__ = ['window_id', 'type', 'slots', 'pos']

    id = ID.CONTAINER_OPEN

    def encode(self):
        super().encode()
        self._buffer.put_byte(self.window_id)
        self._buffer.put_byte(self.type)
        self._buffer.put_short(self.slots)
        self._buffer.put_int_pos(self.pos)
    
    def decode(self):
        super().decode()
        self.window_id = self._buffer.next_byte()
        self.type = self._buffer.next_byte()
        self.slots = self._buffer.next_short()
        self.pos = self._buffer.next_int_pos()


class ContainerSetContent(Packet):
    
    __slots__ = ['window_id', 'slots', 'hotbar']

    id = ID.CONTAINER_SET_CONTENT

    def encode(self):
        super().encode()
        self._buffer.put_byte(self.window_id)
        self._buffer.put_short(len(self.slots))
        for slot in self.slots:
            self._buffer.put_item(slot)
        self._buffer.put_short(len(self.hotbar))
        for slot in self.hotbar:
            self._buffer.put_int(slot)

    def decode(self):
        super().decode()
        self.window_id = self._buffer.next_byte()
        self.slots = [
            self._buffer.next_item()
                for _ in range(self._buffer.next_short())]
        self.hotbar = [
            self._buffer.next_int()
                for _ in range(self._buffer.next_short())]


class ContainerSetData(Packet):
    """Container に関する情報を送信する
    
    Furnace の燃料消費と進捗を通知するために使用される。
    
    window_id : Container の識別子
    property : 情報の種別
    value : 情報の値
    """
    
    __slots__ = ['window_id', 'property', 'value']

    id = ID.CONTAINER_SET_DATA

    def encode(self):
        super().encode()
        self._buffer.put_byte(self.window_id)
        self._buffer.put_short(self.property)
        self._buffer.put_short(self.value)
    
    def decode(self):
        super().decode()
        self.window_id = self._buffer.next_byte()
        self.property = self._buffer.next_short()
        self.value = self._buffer.next_short()


class Unknown1(Packet):
    """
    (0, '3f80000000000000', 'generic.knockbackResistance')
    (0, '3f80000000000000', 'player.experience')
    (0, '40a000004035687c', 'player.exhaustion')
    (0, '41a0000000000000', 'player.saturation')
    (0, '41a0000041a00000', 'generic.health')
    (0, '41a0000041a00000', 'player.hunger')
    (0, '4500000041800000', 'generic.followRange')
    (0, '46c1ae0000000000', 'player.level')
    (0, '7f7fffff00000000', 'generic.absorption')
    (0, '7f7fffff3dcccccd', 'generic.movementSpeed')
    (0, '7f7fffff3f800000', 'generic.attackDamage')
    """
    
    __slots__ = ['eid', 'unknown']
    
    id = ID.UNKNOWN1
    
    def _next(self):
        unknown1 = self._buffer.next_int()
        unknown2 = hex(self._buffer.next(8))
        unknown3 = self._buffer.next_str()
        return unknown1, unknown2, unknown3

    def decode(self):
        super().decode()
        self.eid = self._buffer.next_long()
        count = self._buffer.next_short()
        self.unknown = list(self._next() for _ in range(count))


class RecipeData(Packet):
    
    __slots__ = ['recipes', 'unknown']
    
    id = ID.RECIPE_DATA

    def _next_recipe(self):
        kind = self._buffer.next_int()
        if kind == 0:
            unknown = self._buffer.next_int()
            count = self._buffer.next_int()
            material_items = list(
                self._buffer.next_item() for _ in range(count))
            count = self._buffer.next_int()
            product_items = list(
                self._buffer.next_item() for _ in range(count))
            recipe_id = hex(self._buffer.next(16))
            return (kind, unknown, material_items, product_items, recipe_id)
        if kind == 1:
            unknown = self._buffer.next_int()
            rows = self._buffer.next_int()
            cols = self._buffer.next_int()
            material_items = list(
                self._buffer.next_item() for _ in range(rows*cols))
            count = self._buffer.next_int()
            product_items = list(
                self._buffer.next_item() for _ in range(count))
            recipe_id = hex(self._buffer.next(16))
            return (
                kind, unknown, rows, cols,
                    material_items, product_items, recipe_id)
        if kind == 2:
            unknown1 = self._buffer.next_int()
            unknown2 = self._buffer.next_int()
            item = self._buffer.next_item()
            return (kind, unknown1, unknown2, item)
        if kind == 3:
            unknown1 = self._buffer.next_int()
            unknown2 = hex(self._buffer.next(11))
            return (kind, unknown1, unknown2)
        if kind == 5:
            unknown1 = hex(self._buffer.next(20))
            return (kind, unknown1)

    def encode(self):
        super().encode()
        self._buffer.put(recipe_data)
    
    def decode(self):
        super().decode()
        self.recipes = list(
            self._next_recipe() for _ in range(self._buffer.next_int()))
        self.unknown = self._buffer.next_byte()


class Unknown4(Packet):

    __slots__ = ['unknown']

    id = ID.UNKNOWN4
    
    def encode(self):
        super().encode()
        self._buffer.put_byte(2)  # TODO: 対応する
    
    def decode(self):
        super().decode()
        self.unknown = self._buffer.next_byte()