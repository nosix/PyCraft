# -*- coding: utf8 -*-

from pycraft import common
from pycraft.common import Endian
from pycraft.service.primitive.geometry import Vector, Position
from pycraft.service.primitive.values import Motion, MetaData
from pycraft.service.part.item import new_item


class ByteBuffer(common.ByteBuffer):
    
    def __init__(self, buffer=b''):
        super().__init__(buffer)
    
    def put_pos(self, pos):
        self.put_float(pos.x)
        self.put_float(pos.y)
        self.put_float(pos.z)

    def next_pos(self):
        x, y, z = self.next_float(), self.next_float(), self.next_float()
        return Position(x, z, y)

    def put_int_pos(self, pos, endian=Endian.BIG):
        self.put_int(pos.x, endian)
        self.put_int(pos.y, endian)
        self.put_int(pos.z, endian)

    def next_int_pos(self, endian=Endian.BIG):
        x = self.next_int(endian)
        y = self.next_int(endian)
        z = self.next_int(endian)
        return Position(x, z, y)

    def put_direc(self, direc):
        self.put_float(direc.x)
        self.put_float(direc.y)
        self.put_float(direc.z)
    
    def next_direc(self):
        x, y, z = self.next_float(), self.next_float(), self.next_float()
        return Vector(x, z, y)

    def put_motion(self, motion):
        self.put_long(motion.eid)
        self.put_pos(motion.pos)
        self.put_float(motion.yaw)
        self.put_float(motion.head_yaw)
        self.put_float(motion.pitch)

    def next_motion(self):
        eid = self.next_long()
        pos = self.next_pos()
        yaw = self.next_float()
        head_yaw = self.next_float()
        pitch = self.next_float()
        return Motion(eid, pos, yaw, head_yaw, pitch)

    def put_item(self, item, endian=Endian.BIG):
        self.put_short(item.id, endian)
        if item.id != 0:
            self.put_byte(item.count)
            self.put_short(item.attr, endian)
            self.put_short(0, endian)  # TODO: 対応する
         
    def next_item(self, endian=Endian.BIG):
        item_id = self.next_short(endian)
        if item_id != 0:
            count = self.next_byte()
            attr = self.next_short(endian)
            unknown = self.next_short(endian)
        else:
            count = 0
            attr = 0
            unknown = 0
        return new_item(item_id, count, attr, unknown)
    
    def put_meta(self, meta):
        endian = Endian.LITTLE
        for key in meta.keys():
            data_type, value = meta.get(key)
            flags = data_type << 5 | key & 0x1F
            self.put_byte(flags)
            if data_type == MetaData.DataType.BYTE:
                self.put_byte(value)
            elif data_type == MetaData.DataType.SHORT:
                self.put_short(value, endian)
            elif data_type == MetaData.DataType.INT:
                self.put_int(value, endian)
            elif data_type == MetaData.DataType.LONG:
                self.put_long(value, endian)
            elif data_type == MetaData.DataType.FLOAT:
                self.put_float(value, endian)
            elif data_type == MetaData.DataType.STRING:
                self.put_str(value, endian)
            elif data_type == MetaData.DataType.POS:
                self.put_int_pos(value, endian)
            elif data_type == MetaData.DataType.SLOT:
                self.put_item(value, endian)
        self.put_byte(0x7F)

    def next_meta(self):
        endian = Endian.LITTLE
        meta = MetaData()
        while True:
            flags = self.next_byte()
            if flags == 0x7F:
                return meta
            key = flags & 0x1F
            data_type = flags >> 5
            if data_type == MetaData.DataType.BYTE:
                meta.set(key, self.next_byte(), data_type)
            elif data_type == MetaData.DataType.SHORT:
                meta.set(key, self.next_short(endian), data_type)
            elif data_type == MetaData.DataType.INT:
                meta.set(key, self.next_int(endian), data_type)
            elif data_type == MetaData.DataType.LONG:
                meta.set(key, self.next_long(endian), data_type)
            elif data_type == MetaData.DataType.FLOAT:
                meta.set(key, self.next_float(endian), data_type)
            elif data_type == MetaData.DataType.STRING:
                meta.set(key, self.next_str(endian), data_type)
            elif data_type == MetaData.DataType.POS:
                meta.set(key, self.next_int_pos(endian), data_type)
            elif data_type == MetaData.DataType.SLOT:
                meta.set(key, self.next_item(endian), data_type)
            elif data_type == MetaData.DataType.ROTATION:
                rotation = (
                    self.next_int(endian, False),
                    self.next_int(endian, False))
                meta.set(key, rotation, data_type)  # TODO: 確認する
