# -*- coding: utf8 -*-

from .ids import ID
from .base import ApplicationPacket


class ClientConnect(ApplicationPacket):
    """クライアントの接続要求"""

    __slots__ = ['client_id', 'send_ping', 'use_security']

    id = ID.CLIENT_CONNECT
    
    def decode(self):
        super().decode()
        self.client_id = self._buffer.next_long()
        self.send_ping = self._buffer.next_long()
        self.use_security = self._buffer.next_byte() > 0


class ServerHandshake(ApplicationPacket):
    """ClientConnectへの応答としてのサーバーからの握手"""

    __slots__ = ['addr', 'system_addrs', 'send_ping', 'send_pong']

    id = ID.SERVER_HANDSHAKE

    def __init__(self, buffer=b''):
        super().__init__(buffer)
        self.system_addrs = [('127.0.0.1', 0)] + [('0.0.0.0', 0)] * 9

    def encode(self):
        super().encode()
        self._buffer.put_addr(self.addr)
        self._buffer.put_short(0)
        for addr in self.system_addrs:
            self._buffer.put_addr(addr)
        self._buffer.put_long(self.send_ping)
        self._buffer.put_long(self.send_pong)

    def decode(self):
        super().decode()
        self.addr = self._buffer.next_addr()
        self._buffer.next_short()
        self.system_addrs = [self._buffer.next_addr() for _ in range(10)]
        self.send_ping = self._buffer.next_long()
        self.send_pong = self._buffer.next_long()


class ClientHandshake(ApplicationPacket):
    """ServerHandshakeへの応答としてのクライアントからの握手"""

    __slots__ = ['addr', 'system_addrs', 'send_ping', 'send_pong']

    id = ID.CLIENT_HANDSHAKE

    def decode(self):
        super().decode()
        self.addr = self._buffer.next_addr()
        self.system_addrs = [self._buffer.next_addr() for _ in range(10)]
        self.send_ping = self._buffer.next_long()
        self.send_pong = self._buffer.next_long()


class ClientDisconnect(ApplicationPacket):
    """クライアントの切断要求"""

    id = ID.CLIENT_DISCONNECT


class Ping(ApplicationPacket):
    """通信確認要求"""

    __slots__ = ['ping_id']

    id = ID.PING
    
    def encode(self):
        super().encode()
        self._buffer.put_long(self.ping_id)

    def decode(self):
        super().decode()
        self.ping_id = self._buffer.next_long()


class Pong(ApplicationPacket):
    """Pingへの応答"""

    __slots__ = ['recv_ping_id', 'send_ping_id']

    id = ID.PONG

    def encode(self):
        super().encode()
        self._buffer.put_long(self.recv_ping_id)
        self._buffer.put_long(self.send_ping_id)

    def decode(self):
        super().decode()
        self.recv_ping_id = self._buffer.next_long()
        self.send_ping_id = self._buffer.next_long()