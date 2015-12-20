# -*- coding: utf8 -*-

from pycraft.common import Endian, ByteBuffer


class TagType:
    
    END = 0
    BYTE = 1
    SHORT = 2
    INT = 3
    LONG = 4
    FLOAT = 5
    DOUBLE = 6
    BYTE_ARRAY = 7
    STRING = 8
    ENUM = 9
    COMPOUND = 10
    INT_ARRAY = 11


class Tag:

    __slots__ = ['_type', '_name', '_value']

    def __init__(self, type_, name, value):
        self._type = type_
        self._name = name
        self._value = value
        self._parent = None

    def set_parent(self, parent):
        self._parent = parent

    parent = property(lambda self: self._parent, set_parent)

    def encode(self, buffer, endian):
        self._encode_key(buffer, endian)
        self._encode_value(buffer, endian)

    def _encode_key(self, buffer, endian):
        buffer.put_byte(self._type)
        buffer.put_str(self._name, endian)

    def _encode_value(self, buffer, endian):
        pass


class TagByte(Tag):

    def __init__(self, name, value):
        super().__init__(TagType.BYTE, name, value)        
    
    def _encode_value(self, buffer, endian):
        buffer.put_byte(self._value)


class TagShort(Tag):

    def __init__(self, name, value):
        super().__init__(TagType.SHORT, name, value)        
    
    def _encode_value(self, buffer, endian):
        buffer.put_short(self._value, endian)


class TagInt(Tag):

    def __init__(self, name, value):
        super().__init__(TagType.INT, name, value)        
    
    def _encode_value(self, buffer, endian):
        buffer.put_int(self._value, endian)


class TagLong(Tag):

    def __init__(self, name, value):
        super().__init__(TagType.LONG, name, value)        
    
    def _encode_value(self, buffer, endian):
        buffer.put_long(self._value, endian)


class TagFloat(Tag):

    def __init__(self, name, value):
        super().__init__(TagType.FLOAT, name, value)        
    
    def _encode_value(self, buffer, endian):
        buffer.put_float(self._value, endian)


class TagString(Tag):

    def __init__(self, name, value):
        super().__init__(TagType.STRING, name, value)        
    
    def _encode_value(self, buffer, endian):
        buffer.put_str(self._value, endian)


class TagCompound(Tag):

    def __init__(self, name):
        super().__init__(TagType.COMPOUND, name, [])

    def add(self, tag):
        tag.parent = self
        self._value.append(tag)
    
    def _encode_value(self, buffer, endian):
        for tag in self._value:
            tag.encode(buffer, endian)


class NamedTag:
    
    def __init__(self, endian=Endian.LITTLE):
        self._endian = endian
        self._root = None
        self._compound = None
    
    def bytes(self):
        buffer = ByteBuffer()
        if self._root != None:
            self._root.encode(buffer, self._endian)
        buffer.put_byte(TagType.END)
        return buffer.bytes()
        
    def _put(self, tag):
        if self._compound != None:
            self._compound.add(tag)
        elif self._root == None: 
            self._root = tag

    def put_compound(self, name=''):
        tag = TagCompound(name)
        self._put(tag)
        self._compound = tag

    def put_int(self, name, value):
        tag = TagInt(name, value)
        self._put(tag)

    def put_str(self, name, value):
        tag = TagString(name, value)
        self._put(tag)
