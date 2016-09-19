# -*- coding: utf8 -*-

import struct
from pycraft.common.immutable import ImmutableMeta


class Endian:
    """LittleEndian, BigEndian を扱う
    
    >>> from binascii import hexlify as hex
    >>> hex(Endian.LITTLE.pack('h', 1))
    b'0100'
    >>> hex(Endian.BIG.pack('h', 1))
    b'0001'
    >>> Endian.LITTLE.unpack('h', bytearray.fromhex('0100'))
    1
    >>> Endian.BIG.unpack('h', bytearray.fromhex('0001'))
    1
    """

    class Converter(metaclass=ImmutableMeta):

        properties = 'byte_order slice_pack slice_unpack'

        def pack(self, type_char, value, byte=None):
            array = struct.pack(self.byte_order + type_char, value)
            if byte != None:
                array = array[self.slice_pack(len(array), byte)]
            return array

        def unpack(self, type_char, buffer, fill_byte=None):
            if fill_byte != None:
                buffer[self.slice_unpack(len(buffer))] = b'\x00' * fill_byte
            return struct.unpack(self.byte_order + type_char, buffer)[0]

    __slots = ['LITTLE', 'BIG']

    LITTLE = Converter(
        '<', lambda l,n: slice(None, n), lambda n: slice(n+1,n+1))

    BIG = Converter(
        '>', lambda l,n: slice(l-n, None), lambda n: slice(0,0))


class ByteBuffer:
    """bytearray を操作する
    
    >>> from binascii import hexlify as hex
    >>> buf = ByteBuffer()
    >>> buf.put_str('abcde')
    >>> buf.put_byte(1)
    >>> buf.put_triad(2)
    >>> buf.put_int(3)
    >>> buf.put_float(4.0)
    >>> buf.put_addr(('192.168.0.1', 80))
    >>> b = buf.bytes()
    >>> hex(b)
    b'00056162636465010200000000000340800000043f57fffe0050'
    >>> buf = ByteBuffer(b)
    >>> buf.next_str()
    'abcde'
    >>> buf.next_byte()
    1
    >>> buf.next_triad()
    2
    >>> buf.next_int()
    3
    >>> buf.next_float()
    4.0
    >>> buf.next_addr()
    ('192.168.0.1', 80)
    """
    
    __slots__ = ['_buffer', '_offset']

    def __init__(self, buffer=b''):
        self._buffer = bytearray(buffer)
        self._offset = 0

    def bytes(self):
        """オフセット以降のバイト列を返す"""
        return bytes(self._buffer[self._offset:])

    def trim(self):
        """オフセット以降のバイト列を捨てる"""
        del self._buffer[self._offset:]

    def is_reading(self):
        """バイト列から取得途中ならば True を返す"""
        return self._offset != 0

    def has_next(self):
        """取得されていないバイト列が残っていれば True を返す"""
        return self._offset < len(self._buffer)

    def put(self, v):
        self._buffer += v

    def put_str(self, v, endian=Endian.BIG, encoding='utf8'):
        v = bytes(v, encoding)
        self.put_short(len(v), endian)
        self.put(v)

    def put_bytes(self, v, endian=Endian.BIG):
        self.put_short(len(v), endian)
        self.put(v)

    def put_byte(self, v):
        self.put(bytes([v]))

    def put_short(self, v, endian=Endian.BIG):
        self.put(endian.pack('H', v))

    def put_triad(self, v, endian=Endian.LITTLE):
        self.put(endian.pack('I', v, 3))

    def put_int(self, v, endian=Endian.BIG, unsigned=True):
        self.put(endian.pack('I' if unsigned else 'i', v))

    def put_long(self, v, endian=Endian.BIG):
        self.put(endian.pack('Q', v))

    def put_float(self, v, endian=Endian.BIG):
        self.put(endian.pack('f', v))
    
    def put_addr(self, addr):
        ipaddr, port = addr
        self.put_byte(4)  # version
        for b in ipaddr.split('.'):
            self.put_byte(~int(b) & 0xFF)
        self.put_short(port)

    def _next(self, byte=None):
        if byte == None:
            buf = self._buffer[self._offset:]
        else:
            buf = self._buffer[self._offset:self._offset+byte]
        self._offset += len(buf)
        return buf
    
    def next(self, byte=None):
        return bytes(self._next(byte))

    def next_str(self, endian=Endian.BIG, encoding='utf8'):
        return str(self._next(self.next_short(endian)), encoding)
    
    def next_bytes(self, endian=Endian.BIG):
        return bytes(self._next(self.next_short(endian)))

    def next_byte(self):
        return ord(self._next(1))

    def next_short(self, endian=Endian.BIG):
        return endian.unpack('H', self._next(2))

    def next_triad(self, endian=Endian.LITTLE):
        return endian.unpack('I', self._next(3), 1)
    
    def next_int(self, endian=Endian.BIG, unsigned=True):
        return endian.unpack('I' if unsigned else 'i', self._next(4))

    def next_long(self, endian=Endian.BIG):
        return endian.unpack('Q', self._next(8))

    def next_float(self, endian=Endian.BIG):
        return endian.unpack('f', self._next(4))

    def next_addr(self):
        version = self.next_byte()
        if version == 4:
            ipaddr = '.'.join(str(~self.next_byte() & 0xFF) for _ in range(4))
            port = self.next_short() 
            return (ipaddr, port)
        else:
            raise NotImplementedError(version)


if __name__ == '__main__':
    import doctest
    doctest.testmod()