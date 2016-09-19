# -*- coding: utf8 -*-


from binascii import hexlify as hex
from pycraft.common import ByteBuffer
from pycraft.common.util import summary


class Packet:
    """全てのパケットの基底クラス"""
    
    __slots__ = ['_buffer']

    ID_NONE = -1

    id = ID_NONE

    BUFFER_FACTORY = ByteBuffer

    def __init__(self, buffer=b''):
        self._buffer = self.BUFFER_FACTORY(buffer)

    def __str__(self):
        attrs = (
            summary(k, getattr(self, k)) 
                for k in self.__slots__ 
                    if not k.startswith('_') and hasattr(self, k))
        buf = hex(self._buffer.bytes()) if self._buffer.is_reading() else ''
        return '{name}({attrs}) {buf}'.format(
            name=self.__class__.__name__, attrs=', '.join(attrs), buf=buf)
    
    def require_ack(self):
        """Ackが返されるまで再送するか？"""
        return False

    def buffer(self):
        """バイト列を返す"""
        return self._buffer.bytes()

    def trim(self):
        """オフセット以降のバイト列を捨てる"""
        self._buffer.trim()
    
    def encode(self):
        """属性の情報からバイト列に符号化する"""
        self._buffer = self.BUFFER_FACTORY(bytes([self.id]))

    def decode(self):
        """バイト列から属性の情報に復号化する"""
        self._buffer.next_byte()


class ApplicationPacket(Packet):
    """アプリケーションパケットの基底クラス"""
    
    __slots__ = ['channel']

    CHANNEL_NONE = 0
    
    def __init__(self, buffer=b''):
        super().__init__(buffer)
        self.channel = self.CHANNEL_NONE


class StreamRaw(Packet):
    """いずれのPacketクラスにも該当しないデータを格納する"""

    def __str__(self):
        return '{name}({buf})'.format(
            name=self.__class__.__name__,
            buf=hex(self._buffer.bytes()))

    def decode(self):
        pass