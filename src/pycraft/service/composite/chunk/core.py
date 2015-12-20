# -*- coding: utf8 -*-

from pycraft.common.util import product
from pycraft.service.primitive.geometry import ChunkRectangular
from pycraft.service.primitive.values import Color
from pycraft.service.part.block import new_block


def _data_getter(offset):
    def get_data(self, x, z, y):
        index = offset + ((x << 10) | (z << 6) | (y >> 1))
        if y & 1 == 0:
            return self._data[index] & 0x0F
        else:
            return self._data[index] >> 4
    return get_data


def _data_setter(offset):
    def set_data(self, x, z, y, v):
        index = offset + ((x << 10) | (z << 6) | (y >> 1))
        if y & 1 == 0:
            self._data[index] = (self._data[index] & 0xF0) | (v & 0x0F)
        else:
            self._data[index] = ((v<<4) & 0xF0) | (self._data[index] & 0x0F)
    return set_data


class Chunk:
    
    MAX_LIGHT_LEVEL = 15

    SIZE = ChunkRectangular

    TOP_Y = SIZE.Y - 1

    LEN_BLOCK_ID = SIZE.VOLUME
    LEN_BLOCK_DATA = SIZE.VOLUME//2
    LEN_SKY_LIGHT = SIZE.VOLUME//2
    LEN_BLOCK_LIGHT = SIZE.VOLUME//2
    LEN_HEIGHT_MAP = SIZE.AREA_OF_BASE
    LEN_BIOME_COLOR = SIZE.AREA_OF_BASE*4

    OFFSET_BLOCK_DATA = LEN_BLOCK_ID
    OFFSET_SKY_LIGHT = OFFSET_BLOCK_DATA + LEN_BLOCK_DATA
    OFFSET_BLOCK_LIGHT = OFFSET_SKY_LIGHT + LEN_SKY_LIGHT
    OFFSET_HEIGHT_MAP = OFFSET_BLOCK_LIGHT + LEN_BLOCK_LIGHT
    OFFSET_BIOME_COLOR = OFFSET_HEIGHT_MAP + LEN_HEIGHT_MAP

    DATA_LEN = OFFSET_BIOME_COLOR + LEN_BIOME_COLOR

    PRIMITIVE_DATA = bytes(DATA_LEN)

    def __init__(self, pos, data=PRIMITIVE_DATA):
        """地形データでチャンクを初期化する"""
        # ChunkPosition
        self._pos = pos
        self._data = bytearray(data)

    def __str__(self):
        return '{name}{pos}[{data}]'.format(
            name=self.__class__.__name__, pos=self._pos, data=self._data.hex())

    pos = property(lambda self: self._pos)
    data = property(lambda self: bytes(self._data))
    
    @classmethod
    def each_xz_pos(cls, range_x=None, range_z=None):
        """Chunk内の(x,z)の組み合わせを順に返す"""
        if range_x == None:
            range_x = range(cls.SIZE.X)
        if range_z == None:
            range_z = range(cls.SIZE.X)
        return product(range_x, range_z)
    
    @classmethod
    def each_y_pos(cls, from_top=True, start=None):
        """yの値を順に返す"""
        if from_top:
            if start == None:
                start = cls.TOP_Y
            return range(start, -1, -1)
        else:
            if start == None:
                start = 0
            return range(start, cls.SIZE.Y)

    def get_ground_y(self, x, z, y=None, to_bottom=True):
        """Chunk内の座標に対して地表(通過できないブロック)の位置を返す
        
        x, z : Chunk内の x, z 座標
        to_bottom : True ならば下方向に空洞を探す
        y : 走査を開始する座標
        """
        column = self.get_block_id_column(x, z)
        if y == None:
            y = self.TOP_Y if to_bottom else 0
        if self._is_transparent(column[y]) or to_bottom:
            # 開始地点が空洞か下方向への探索ならば、地表を下方向に探す
            for y in self.each_y_pos(True, y):
                if not self._is_transparent(column[y]):
                    return y
            return 0
        else:
            # 開始地点が空洞ではなく上方向の探索ならば、地表を上方向に探す
            for y in self.each_y_pos(False, y):
                if self._is_transparent(column[y]):
                    return y - 1
            return self.Y_RANGE

    @classmethod
    def _is_transparent(cls, block_id):
        return new_block.cls(block_id).is_transparent()

    def is_transparent(self, x, z, y):
        return self._is_transparent(self.get_block_id(x, z, y))

    @classmethod
    def _block_id_index(cls, x, z, y=0):
        return (x << 11) | (z << 7) | y

    def set_block_id(self, x, z, y, block_id):
        """Chunk内の座標に対して Block ID を設定する"""
        index = self._block_id_index(x, z, y)
        self._data[index] = block_id
        # 最高地点の更新
        heighest_y = self.get_height_map(x, z)
        if self._is_transparent(block_id):
            if y == heighest_y:
                for y in range(heighest_y, -1, -1):
                    if not self._is_transparent(self.get_block_id(x, z, y)):
                        heighest_y = y
                        break
        else:
            if y > heighest_y:
                heighest_y = y
        self.set_height_map(x, z, heighest_y)

    def get_block_id(self, x, z, y):
        """Chunk内の座標に対して Block ID を返す"""
        index = self._block_id_index(x, z, y)
        return self._data[index]

    def get_block_id_column(self, x, z):
        """Chunk内の座標に対して縦一列の Block ID リストを返す"""
        index = self._block_id_index(x, z)
        return bytes(v for v in self._data[index:index+self.SIZE.Y])

    set_block_data = _data_setter(OFFSET_BLOCK_DATA)
    get_block_data = _data_getter(OFFSET_BLOCK_DATA)
    set_sky_light = _data_setter(OFFSET_SKY_LIGHT)
    get_sky_light = _data_getter(OFFSET_SKY_LIGHT)
    set_block_light = _data_setter(OFFSET_BLOCK_LIGHT)
    get_block_light = _data_getter(OFFSET_BLOCK_LIGHT)

    @classmethod
    def _height_map_index(cls, x, z):
        return cls.OFFSET_HEIGHT_MAP + (z << 4) + x

    def set_height_map(self, x, z, y):
        index = self._height_map_index(x, z)
        self._data[index] = y

    def get_height_map(self, x, z):
        index = self._height_map_index(x, z)
        return self._data[index]
    
    @classmethod
    def _biome_color_index(cls, x, z):
        return cls.OFFSET_BIOME_COLOR + ((z << 4) + x) * 4

    def set_biome_id(self, x, z, biome_id):
        """Chunk内の座標に対して Biome ID を設定する"""
        index = self._biome_color_index(x, z)
        self._data[index] = biome_id

    def get_biome_id(self, x, z):
        """Chunk内の座標に対して Biome ID を返す"""
        index = self._biome_color_index(x, z)
        return self._data[index]

    def set_biome_color(self, x, z, c):
        """Chunk内の座標に対して色を設定する"""
        index = self._biome_color_index(x, z) + 1
        self._data[index:index+3] = c

    def get_biome_color(self, x, z):
        """Chunk内の座標の色を返す"""
        index = self._biome_color_index(x, z) + 1
        return Color(*self._data[index:index+3])

    def set_block(self, x, z, y, block):
        self.set_block_id(x, z, y, block.id),
        self.set_block_data(x, z, y, block.attr)

    def get_block(self, x, z, y):
        return new_block(
            self.get_block_id(x, z, y),
            self.get_block_data(x, z, y))
