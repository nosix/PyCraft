# -*- coding: utf8 -*-

import zlib
from .base import Packet
from .ids import ID
from pycraft.common.buffer import ByteBuffer


class Text(Packet):
    
    __slots__ = ['type', 'message', 'params', 'source']

    id = ID.TEXT

    TYPE_RAW = 0
    TYPE_CHAT = 1
    TYPE_TRANSLATION = 2
    TYPE_POPUP = 3
    TYPE_TIP = 4
    
    def tr(self, lang):
        self.message, self.params = self.message.tr(lang)
        
    def encode(self):
        super().encode()
        self._buffer.put_byte(self.type)
        if self.type == self.TYPE_TRANSLATION:
            self._buffer.put_str(self.message)
            self._buffer.put_byte(len(self.params))
            for p in self.params:
                self._buffer.put_str(p)
        else:
            if self.type == self.TYPE_CHAT:
                self._buffer.put_str(self.source)
            self._buffer.put_str(self.message)
            
    def decode(self):
        super().decode()
        self.type = self._buffer.next_byte()
        if self.type == self.TYPE_TRANSLATION:
            self.message = self._buffer.next_str()
            num = self._buffer.next_byte()
            self.params = [self._buffer.next_str() for _ in range(num)]
        else:
            if self.type == self.TYPE_CHAT:
                self.source = self._buffer.next_str()
            self.message = self._buffer.next_str()


class MovePlayer(Packet):

    __slots__ = ['motion', 'mode', 'on_ground']

    id = ID.MOVE_PLAYER

    MODE_NORMAL = 0  # recv
    MODE_RESET = 1  # send
    MODE_ROTATION = 2

    def encode(self):
        super().encode()
        self._buffer.put_motion(self.motion)
        self._buffer.put_byte(self.mode)
        self._buffer.put_byte(1 if self.on_ground else 0)

    def decode(self):
        super().decode()
        self.motion = self._buffer.next_motion()
        self.mode = self._buffer.next_byte()
        self.on_ground = self._buffer.next_byte() > 0


class AddPainting(Packet):
     
    id = ID.ADD_PAINTING
 
    def decode(self):
        super().decode()
        self.eid = self._buffer.next_long()
        self.pos = self._buffer.next_int_pos()
        self.direc = self._buffer.next_int()
        self.title = self._buffer.next_str()


class PlayerEquipment(Packet):
    """プレイヤーの装具通知
    
    eid : 装具が変更された Player の eid
    item_id : 装具された Item の id
    attr : Item の attr
    slot : inventory slots の index (9..), slot から外す時は 255
    held_hotbar : inventory hotbar の index (0..8)
    """
    
    __slots__ = ['eid', 'item', 'slot', 'held_hotbar']

    id = ID.PLAYER_EQUIPMENT

    def encode(self):
        super().encode()
        self._buffer.put_long(self.eid)
        self._buffer.put_item(self.item)
        self._buffer.put_byte(self.slot)
        self._buffer.put_byte(self.held_hotbar)

    def decode(self):
        super().decode()
        self.eid = self._buffer.next_long()
        self.item = self._buffer.next_item()
        self.slot = self._buffer.next_byte()
        self.held_hotbar = self._buffer.next_byte()


class PlayerArmorEquipment(Packet):
    
    __slots__ = ['eid', 'slots']

    id = ID.PLAYER_ARMOR_EQUIPMENT

    def decode(self):
        super().decode()
        self.eid = self._buffer.next_long()
        self.slots = [self._buffer.next_byte() for _ in range(4)]


class Animate(Packet):
    
    __slots__ = ['action', 'eid']

    id = ID.ANIMATE

    def encode(self):
        super().encode()
        self._buffer.put_byte(self.action)
        self._buffer.put_long(self.eid)

    def decode(self):
        super().decode()
        self.action = self._buffer.next_byte()
        self.eid = self._buffer.next_long()


class DropItem(Packet):
    
    id = ID.DROP_ITEM


class TileEntityData(Packet):
    
    __slots__ = ['pos', 'named_tag']

    id = ID.TILE_ENTITY_DATA

    def encode(self):
        super().encode()
        self._buffer.put_int_pos(self.pos)
        self._buffer.put(self.named_tag)

    def decode(self):
        super().decode()
        self.pos = self._buffer.next_int_pos()
        self.named_tag = self._buffer.next()


class ContainerClose(Packet):

    __slots__ = ['window_id']    

    id = ID.CONTAINER_CLOSE

    def encode(self):
        super().encode()
        self._buffer.put_byte(self.window_id)

    def decode(self):
        super().decode()
        self.window_id = self._buffer.next_byte()


class ContainerSetSlot(Packet):
    """コンテナのスロット設定通知
    
    recv:
        チェストにアイテムを出し入れしたとき
    send:
        アイテムを拾ったとき
    """
    
    __slots__ = ['window_id', 'slot', 'unknown', 'item']

    id = ID.CONTAINER_SET_SLOT

    def encode(self):
        super().encode()
        self._buffer.put_byte(self.window_id)
        self._buffer.put_short(self.slot)
        self._buffer.put_short(0)  # TODO: 対応する
        self._buffer.put_item(self.item)

    def decode(self):
        super().decode()
        self.window_id = self._buffer.next_byte()
        self.slot = self._buffer.next_short()
        self.unknown = self._buffer.next_short()  # TODO: 対応する
        self.item = self._buffer.next_item()


class Batch(Packet):
    
    __slots__ = ['payloads']

    id = ID.BATCH
    
    THRESHOLD = 512
    
    def encode(self):
        super().encode()
        buffer = ByteBuffer()
        for payload in self.payloads:
            buffer.put_int(len(payload))
            buffer.put(payload)
        comp_payload = zlib.compress(buffer.bytes())
        self._buffer.put_int(len(comp_payload))
        self._buffer.put(comp_payload)

    def decode(self):
        super().decode()
        size = self._buffer.next_int()
        buffer = ByteBuffer(zlib.decompress(self._buffer.next(size)))
        def payloads():
            while buffer.has_next():
                yield buffer.next(buffer.next_int())
        self.payloads = list(payloads())


class Unknown3(Packet):
    """
    unknow:
        0000000000000000
        013a01000000100a0000090400656e6368010000000000013b01000000100a0000090400656e6368010000000000013c0100000000013d0100000000
    """
    
    __slots__ = ['eid', 'unknown']
    
    id = ID.UNKNOWN3
    
    def decode(self):
        super().decode()
        self.eid = self._buffer.next_long()
        self.unknown = self._buffer.next().hex()