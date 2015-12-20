# -*- coding: utf8 -*-

from .ids import ID
from .base import Packet


_MAGIC = b'\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78'
_MAGIC_LEN = len(_MAGIC)


class UnconnectedPing(Packet):
    """未接続時のサーバー情報取得要求"""

    __slots__ = ['ping_id', 'unknown']

    id = ID.UNCONNECTED_PING

    def decode(self):
        super().decode()
        self.ping_id = self._buffer.next_long()
        self._buffer.next(_MAGIC_LEN)
        self.unknown = self._buffer.next_long()


class UnconnectedPong(Packet):
    """UnconnectedPing への応答"""

    __slots__ = ['ping_id', 'server_id', 'server_info']

    id = ID.UNCONNECTED_PONG

    def encode(self):
        super().encode()
        self._buffer.put_long(self.ping_id)
        self._buffer.put_long(self.server_id)
        self._buffer.put(_MAGIC)
        self._buffer.put_str(self.server_info)
        
    def decode(self):
        super().decode()
        self.ping_id = self._buffer.next_long()
        self.server_id = self._buffer.next_long()
        self._buffer.next(_MAGIC_LEN)
        self.server_info = self._buffer.next_str()


class OpenConnectionRequest1(Packet):
    """接続要求(Step1)"""

    __slots__ = ['protocol', 'mtu_size']
    
    id = ID.OPEN_CONNECTION_REQUEST_1

    def decode(self):
        super().decode()
        self._buffer.next(_MAGIC_LEN)
        self.protocol = self._buffer.next_byte()
        self.mtu_size = len(self._buffer.next()) + 18


class OpenConnectionReply1(Packet):
    """接続要求(Step1)への応答"""

    __slots__ = ['server_id', 'mtu_size']

    id = ID.OPEN_CONNECTION_REPLY_1
    
    def encode(self):
        super().encode()
        self._buffer.put(_MAGIC)
        self._buffer.put_long(self.server_id)
        self._buffer.put_byte(0)  # server security
        self._buffer.put_short(self.mtu_size)

    def decode(self):
        super().decode()
        self._buffer.next(_MAGIC_LEN)
        self.server_id = self._buffer.next_long()
        self._buffer.next_byte()  # server security
        self.mtu_size = self._buffer.next_short()


class OpenConnectionRequest2(Packet):
    """接続要求(Step2)"""

    __slots__ = ['server_addr', 'mtu_size', 'client_id']

    id = ID.OPEN_CONNECTION_REQUEST_2

    def decode(self):
        super().decode()
        self._buffer.next(_MAGIC_LEN)
        self.server_addr = self._buffer.next_addr()
        self.mtu_size = self._buffer.next_short()
        self.client_id = self._buffer.next_long()


class OpenConnectionReply2(Packet):
    """接続要求(Step2)への応答"""

    __slots__ = ['server_id', 'client_addr', 'mtu_size']

    id = ID.OPEN_CONNECTION_REPLY_2

    def encode(self):
        super().encode()
        self._buffer.put(_MAGIC)
        self._buffer.put_long(self.server_id)
        self._buffer.put_addr(self.client_addr)
        self._buffer.put_short(self.mtu_size)
        self._buffer.put_byte(0)  # server security

    def decode(self):
        super().decode()
        self._buffer.next(_MAGIC_LEN)
        self.server_id = self._buffer.next_long()
        self.client_addr = self._buffer.next_addr()
        self.mtu_size = self._buffer.next_short()
        self._buffer.next_byte()  # server security


class UnconnectedPingOpenConnections(Packet):

    id = ID.UNCONNECTED_PING_OPEN_CONNECTIONS


class AdvertiseSystem(Packet):

    id = ID.ADVERTISE_SYSTEM


class AcknowledgePacket(Packet):
    """Packet 受信確認のための応答"""

    __slots__ = ['seq_nums']

    @staticmethod
    def _ranges(seq_nums):
        start, last = seq_nums[0], seq_nums[0]
        for n in seq_nums[1:]:
            if last + 1 == n:
                last += 1
            else:
                yield start, last
                start, last = n, n
        yield start, last

    def encode(self):
        super().encode()
        records = list(self._ranges(sorted(self.seq_nums)))
        self._buffer.put_short(len(records))
        for start_num, last_num in records:
            if start_num == last_num:
                self._buffer.put_byte(0x01)
                self._buffer.put_triad(start_num)
            else:
                self._buffer.put_byte(0x00)
                self._buffer.put_triad(start_num)
                self._buffer.put_triad(last_num)

    def decode(self):
        super().decode()
        def seq_nums():
            for _ in range(self._buffer.next_short()):
                flag = self._buffer.next_byte()
                if flag & 0x01:
                    yield self._buffer.next_triad()
                else:
                    start, last = self._buffer.next_triad(), self._buffer.next_triad()
                    for seq_num in range(start, last+1):
                        yield seq_num
        self.seq_nums = set(seq_nums())


class Ack(AcknowledgePacket):

    id = ID.ACK


class Nack(AcknowledgePacket):

    id = ID.NACK
