# -*- coding: utf8 -*-

import math
from pycraft.common import ImmutableMeta
from .ids import ID
from .base import Packet


class EncapsulatedPacket(metaclass=ImmutableMeta):
    """ApplicationPacket を包含するパケット
    
    reliability:
        From http://www.jenkinssoftware.com/mcnet/manual/reliabilitytypes.html
        
        Default: 0b010 (2) or 0b011 (3)
    
        0: UNRELIABLE
        1: UNRELIABLE_SEQUENCED
        2: RELIABLE
        3: RELIABLE_ORDERED
        4: RELIABLE_SEQUENCED
        5: UNRELIABLE_WITH_ACK_RECEIPT
        6: UNRELIABLE_SEQUENCED_WITH_ACK_RECEIPT
        7: RELIABLE_WITH_ACK_RECEIPT
        8: RELIABLE_ORDERED_WITH_ACK_RECEIPT
        9: RELIABLE_SEQUENCED_WITH_ACK_RECEIPT
        
        UNRELIABLE : パケットの到着を保証しない
        RELIABLE : パケットの到着を保証する
        ORDERED : 順番に到着することを保証する
        SEQUENCED : 古いパケットは無視してよい
        WITH_ACK_RECEIPT : 未サポート
    """

    @staticmethod
    def is_reliable(reliability):
        return 2 <= reliability <= 4 or 7 <= reliability <= 9
    
    @staticmethod
    def is_ordered(reliability):
        return reliability not in (0, 2, 5, 7)
    
    class Message(metaclass=ImmutableMeta):

        properties = 'index'
    
    class Order(metaclass=ImmutableMeta):

        properties = 'index channel'
    
    class Split(metaclass=ImmutableMeta):
        
        properties = 'count id index'

    properties = 'reliability buffer message order split'

    @classmethod
    def new(cls, reliability, buffer, message=None, order=None, split=None):
        return reliability, buffer, message, order, split

    def __str__(self):
        message = 'm[{i}]'.format(i=self.message.index) \
            if self.message else '-'
        order = 'o[{i},{c}]'.format(i=self.order.index, c=self.order.channel) \
            if self.order else '-'
        split = 's[{c},{id},{i}]'.format(
            c=self.split.count, id=self.split.id, i=self.split.index) \
            if self.split else '-'
        return '{name}({rel},{m},{o},{s},{len})'.format(
            name=self.__class__.__name__,
            rel=self.reliability,
            m=message, o=order, s=split,
            len=len(self.buffer))

    def __len__(self):
        """EncapsulatedPacket をバイト列に符号化した際のデータ長を返す"""
        return 3 \
            + (3 if self.message else 0) \
            + (4 if self.order else 0) \
            + (10 if self.split else 0) \
            + len(self.buffer)
    
    def require_ack(self):
        return self.is_reliable(self.reliability)


class DataPacket(Packet):
    """EncapsulatedPacket を送受信するためのパケット"""

    __slots__ = ['seq_num', 'packets']

    def __init__(self, buffer=b''):
        super().__init__(buffer)
        self.packets = []
    
    def require_ack(self):
        return any(pk.require_ack() for pk in self.packets)

    def _put_packet(self, packet):
        flags = (packet.reliability << 5) | (0b00010000 if packet.split else 0)
        self._buffer.put_byte(flags)
        self._buffer.put_short(len(packet.buffer) * 8)
        if EncapsulatedPacket.is_reliable(packet.reliability):
            self._buffer.put_triad(packet.message.index)
        if EncapsulatedPacket.is_ordered(packet.reliability):
            self._buffer.put_triad(packet.order.index)
            self._buffer.put_byte(packet.order.channel)
        if packet.split:
            self._buffer.put_int(packet.split.count)
            self._buffer.put_short(packet.split.id)
            self._buffer.put_int(packet.split.index)
        self._buffer.put(packet.buffer)
        
    def _next_packet(self):
        flags = self._buffer.next_byte()
        reliability = (flags & 0b11100000) >> 5
        has_split = (flags & 0b00010000) > 0
        length = math.ceil(self._buffer.next_short() / 8)
        
        param = {}
        if EncapsulatedPacket.is_reliable(reliability):
            param['message'] = EncapsulatedPacket.Message(
                self._buffer.next_triad())
        if EncapsulatedPacket.is_ordered(reliability):
            param['order'] = EncapsulatedPacket.Order(
                self._buffer.next_triad(), self._buffer.next_byte())
        if has_split:
            param['split'] = EncapsulatedPacket.Split(
                self._buffer.next_int(),
                self._buffer.next_short(),
                self._buffer.next_int())
        buf = self._buffer.next(length)
        return EncapsulatedPacket(reliability, buf, **param)

    def __len__(self):
        """符号化する際のデータ長を返す"""
        return 4 + sum(len(pk) for pk in self.packets)
        
    def encode(self):
        super().encode()
        self._buffer.put_triad(self.seq_num)
        for pk in self.packets:
            self._put_packet(pk)
    
    def decode(self):
        super().decode()
        self.seq_num = self._buffer.next_triad()
        def packets():
            while self._buffer.has_next():
                yield self._next_packet()
        self.packets = list(packets())


class DataPacket0(DataPacket):

    id = ID.DATA_PACKET_0


class DataPacket1(DataPacket):

    id = ID.DATA_PACKET_1


class DataPacket2(DataPacket):

    id = ID.DATA_PACKET_2


class DataPacket3(DataPacket):

    id = ID.DATA_PACKET_3


class DataPacket4(DataPacket):

    id = ID.DATA_PACKET_4


class DataPacket5(DataPacket):

    id = ID.DATA_PACKET_5


class DataPacket6(DataPacket):

    id = ID.DATA_PACKET_6


class DataPacket7(DataPacket):

    id = ID.DATA_PACKET_7


class DataPacket8(DataPacket):

    id = ID.DATA_PACKET_8


class DataPacket9(DataPacket):

    id = ID.DATA_PACKET_9


class DataPacketA(DataPacket):

    id = ID.DATA_PACKET_A


class DataPacketB(DataPacket):

    id = ID.DATA_PACKET_B


class DataPacketC(DataPacket):

    id = ID.DATA_PACKET_C


class DataPacketD(DataPacket):

    id = ID.DATA_PACKET_D


class DataPacketE(DataPacket):

    id = ID.DATA_PACKET_E


class DataPacketF(DataPacket):

    id = ID.DATA_PACKET_F
