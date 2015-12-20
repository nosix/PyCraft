# -*- coding: utf8 -*-

from pycraft.common.util import names


class MetaData:

    class Key:
        FLAGS = 0
        AIR = 1
        NAMETAG = 2
        SHOW_NAMETAG = 3
        SILENT = 4
        POTION_COLOR = 7
        POTION_AMBIENT = 8
        UNKNOWN_12 = 12
        UNKNOWN_14 = 14
        NO_AI = 15
        PLAYER_FLAGS = 16
        PLAYER_BED_POSITION = 17
        UNKNOWN_18 = 18
        UNKNOWN_19 = 19
        UNKNOWN_20 = 20
        UNKNOWN_21 = 21
        UNKNOWN_16 = 48  # 16 + 32
        UNKNOWN_17 = 49  # 17 + 32
        UNKNOWN_17_2 = 50
        UNKNOWN_17_3 = 51

    class DataType:
        BYTE = 0
        SHORT = 1
        INT = 2
        FLOAT = 3
        STRING = 4
        SLOT = 5
        POS = 6
        ROTATION = 7
        LONG = 8
    
    TYPE_MAP = {
        Key.NAMETAG : DataType.STRING,
        Key.PLAYER_BED_POSITION : DataType.POS,
        Key.FLAGS : DataType.BYTE,
        Key.AIR : DataType.SHORT,
        Key.SHOW_NAMETAG : DataType.BYTE,
        Key.SILENT : DataType.BYTE,
        Key.NO_AI : DataType.BYTE,
        Key.POTION_COLOR : DataType.INT,
        Key.POTION_AMBIENT : DataType.BYTE,
        Key.PLAYER_FLAGS : DataType.BYTE,
        Key.UNKNOWN_12 : DataType.BYTE,
        Key.UNKNOWN_14 : DataType.BYTE,
        Key.UNKNOWN_16 : DataType.SHORT,
        Key.UNKNOWN_17 : DataType.ROTATION,
        Key.UNKNOWN_17_2 : DataType.BYTE,
        Key.UNKNOWN_17_3 : DataType.SHORT,
        Key.UNKNOWN_18 : DataType.BYTE,
        Key.UNKNOWN_19 : DataType.BYTE,
        Key.UNKNOWN_20 : DataType.BYTE,
        Key.UNKNOWN_21 : DataType.BYTE,
        }

    KEY_NAMES = names(Key)

    def __init__(self, meta=None):
        if meta == None:
            self._values = {
                self.Key.FLAGS : 0,
                self.Key.AIR : 300,
                self.Key.NAMETAG : '',
                self.Key.SHOW_NAMETAG : 0,
                self.Key.SILENT : 0,
                self.Key.NO_AI : 0,
                }
        else:
            self._values = dict(meta._values)
    
    def clone(self):
        o = self.__class__.__new__(self.__class__)
        o._values = dict(self._values)
        return o

    def __str__(self):
        return str(dict(
            (self.KEY_NAMES[k], v) for k,v in self._values.items()))

    def set(self, key, value, data_type=None):
        # TODO: 見直す
        if key == 17:
            if data_type == self.DataType.ROTATION:
                key = self.Key.UNKNOWN_17
            if data_type == self.DataType.BYTE:
                key = self.Key.UNKNOWN_17_2
            if data_type == self.DataType.SHORT:
                key = self.Key.UNKNOWN_17_3
        if key == 16 and data_type == self.DataType.SHORT:
            key = self.Key.UNKNOWN_16
        assert data_type == None or data_type == self.TYPE_MAP[key]
        self._values[key] = value

    def get(self, key):
        return (self.TYPE_MAP[key], self._values[key])    

    def keys(self):
        return self._values.keys()
