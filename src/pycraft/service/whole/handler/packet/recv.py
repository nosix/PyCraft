# -*- coding: utf8 -*-

from binascii import hexlify as hex
from pycraft.service.primitive.geometry import Position
from .base import Packet
from .ids import ID


class Login(Packet):
    
    __slots__ = [
        'user_name', 'protocol1', 'protocol2', 'client_id', 'public_id',
        'server', 'unknown', 'skin_name', 'skin',
        ]

    id = ID.LOGIN

    def decode(self):
        super().decode()
        self.user_name = self._buffer.next_str()
        self.protocol1 = self._buffer.next_int()
        self.protocol2 = self._buffer.next_int()
        self.client_id = self._buffer.next_long()
        self.public_id = self._buffer.next(16)  # TODO: 確認する
        self.server = self._buffer.next_str()
        self.unknown = self._buffer.next_bytes()  # TODO: 対応する
        self.skin_name = self._buffer.next_str()
        self.skin = self._buffer.next_bytes()


class RemoveBlock(Packet):

    __slots__ = ['eid', 'pos']    

    id = ID.REMOVE_BLOCK

    def decode(self):
        super().decode()
        self.eid = self._buffer.next_long()
        x = self._buffer.next_int()
        z = self._buffer.next_int()
        y = self._buffer.next_byte()
        self.pos = Position(x, z, y)


class Interact(Packet):
    
    __slots__ = ['action', 'target']

    id = ID.INTERACT

    def decode(self):
        super().decode()
        self.action = self._buffer.next_byte()
        self.target = self._buffer.next_long()


class UseItem(Packet):
    """アイテムの使用通知
    
    bpos : Item を設置した Block の Position
    face : Item を設置した面 (0: y-,y+,z-,z+,x-,x+ :5), 設置しない場合 255
    item_id : Item の id
    attr : Item の attr
    eid : Player の eid
    f : Player の相対位置 (負方向 0.0..1.0 正方向)
    pos : Player の Position
    """
    
    __slots__ = ['bpos', 'face', 'f', 'pos', 'item']

    id = ID.USE_ITEM

    FACE_NONE = 255

    def has_face(self):
        return self.face != self.FACE_NONE

    def decode(self):
        super().decode()
        self.bpos = self._buffer.next_int_pos()
        self.face = self._buffer.next_byte()
        self.f = self._buffer.next_pos()
        self.pos = self._buffer.next_pos()
        self.item = self._buffer.next_item()


class PlayerAction(Packet):
    
    __slots__ = ['eid', 'action', 'pos', 'face']

    id = ID.PLAYER_ACTION

    def decode(self):
        super().decode()
        self.eid = self._buffer.next_long()
        self.action = self._buffer.next_int()
        self.pos = self._buffer.next_int_pos()
        self.face = self._buffer.next_int()


class Unknown2(Packet):
    
    __slots__ = ['unknown', 'item']

    id = ID.UNKNOWN2
    
    def decode(self):
        super().decode()
        self.unknown = self._buffer.next_byte()
        self.item = self._buffer.next_item()


class MakeItem(Packet):
    
    __slots__ = [
        'unknown1', 'unknown2', 'recipe_id', 'material_items', 'product_items'
    ]
    
    id = ID.MAKE_ITEM
    
    def decode(self):
        super().decode()
        self.unknown1 = self._buffer.next_byte()
        self.unknown2 = self._buffer.next_int()
        self.recipe_id = hex(self._buffer.next(16))
        self.material_items = list(
            self._buffer.next_item() for _ in range(self._buffer.next_int()))
        self.product_items = list(
            self._buffer.next_item() for _ in range(self._buffer.next_int()))