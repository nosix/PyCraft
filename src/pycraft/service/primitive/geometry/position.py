# -*- coding: utf8 -*-

import math
import operator
from pycraft.common import ImmutableMeta
from pycraft.common.util import put_in_range, put_in_border
from .vector import Vector
from .face import Face
from .area import SpiralChunkArea


class ChunkRectangular:
    
    X, Z, Y = 16, 16, 128
    AREA_OF_BASE = X * Z
    VOLUME = AREA_OF_BASE * Y


class Position(metaclass=ImmutableMeta):

    X_RANGE, Z_RANGE, Y_RANGE = 65536, 65536, 128

    CHUNK_AREA = SpiralChunkArea()

    ROUND_NDIGITS = 5

    properties = 'x z y'

    @classmethod
    def new(cls, x, z, y):
        x = put_in_range(x, cls.X_RANGE)
        z = put_in_range(z, cls.Z_RANGE)
        y = put_in_border(y, 0, cls.Y_RANGE-1)
        return x, z, y

    chunk_pos = property(lambda self:
        ChunkPosition(
            int(self.x)//ChunkRectangular.X, int(self.z)//ChunkRectangular.Z))

    in_chunk = property(lambda self:
        Position(
            self.x%ChunkRectangular.X, self.z%ChunkRectangular.Z, self.y))

    center_in_block = property(lambda self:
        Position(int(self.x)+0.5, int(self.z)+0.5, int(self.y)+0.5))

    def __calc(self, f, v):
        if len(v) == 3:
            return Position(f(self.x,v[0]), f(self.z,v[1]), f(self.y,v[2]))
        elif len(v) == 2:
            return Position(f(self.x,v[0]), f(self.z,v[1]), self.y)
        else:
            return NotImplemented

    def __add__(self, v):
        return self.__calc(operator.add, v)

    def __sub__(self, v):
        return self.__calc(operator.sub, v)

    def __mul__(self, n):
        return Position(self.x*n, self.z*n, self.y*n)
    
    def __truediv__(self, n):
        return Position(self.x/n, self.z/n, self.y/n)
    
    def astype(self, func):
        return Position(func(self.x), func(self.z), func(self.y))

    def direc(self, pos):
        return Vector(self.x-pos.x, self.z-pos.z, self.y-pos.y)

    def distance(self, pos):
        """2つの位置の距離を返す"""
        return math.sqrt(
            (self.x-pos.x)**2 + (self.z-pos.z)**2 + (self.y-pos.y)**2)

    def by_face(self, face):
        """指定された面の方向の位置を返す"""
        return self + Face.DIRECTION[face]

    def surrounding_chunk(self, max_priority=None):
        """ChunkPosition 周辺領域の ChunkPlacement を返す
        
        max_priority : int - 指定された優先度の範囲まで返す
        """
        return self.CHUNK_AREA.surrounding_chunk(self.chunk_pos, max_priority)
    
    def angle_h(self, pos, yaw):
        """XZ平面上における角度を返す
        
        2つのベクトルがつくる角度を求める。
        pos : Position - posを終点とするベクトルを1つのベクトルとする
        yaw : int - Z軸方向を0とする角度を1つのベクトルとする
        """
        if self.x == pos.x and self.z == pos.z:
            return None
        v0 = Vector.by_angle(1, yaw)
        v1 = pos.direc(self).norm()
        deg = round(
            math.degrees(math.acos(v1.dot(v0, is_3d=False))),
            self.ROUND_NDIGITS)
        return deg if v0.cross(v1, is_3d=False) >= 0 else -deg
    
    def angle_v(self, pos, pitch):
        """Y軸方向の角度を返す
        
        2つのベクトルがつくる角度を求める。
        pos : Position - posを終点とするベクトルを1つのベクトルとする
        pitch : int - もう1つのベクトルがXZ平面と作る角度
        """
        dy = pos.y - self.y
        d = self.distance(pos)
        return round(
            math.degrees(math.asin(dy/d)) - pitch, self.ROUND_NDIGITS) \
                if d != 0 else 0

    def rotate(self, o, yaw):
        """oを中心としてyawの角度で回転する
        
        o : Position - 回転の中心点
        yaw : float - 回転の角度
        """
        return o + self.direc(o).rotate(yaw)
    
    def intersection(self, o):
        """位置が含まれるブロックとの交点を返す
        
        self : Position - 終点
        o : Position - 起点
        return : Position - 終点を含むブロックとの交点
        """
        zero = Position(0,0,0)
        # 鏡写しにする
        v_sign = self.direc(o).mirror()
        v_fm_pos = o.direc(zero) * v_sign
        v_to_pos = self.direc(zero) * v_sign
        v_border = v_to_pos.astype(math.floor)
        v_lay = v_to_pos - v_fm_pos
        # v_to_pos = v_fm_pos + a * v_lay
        def calc_a(n1, n2, nv):
            return (n2 - n1) / nv if nv != 0 else 2
        a = list(map(calc_a, v_fm_pos, v_border, v_lay))
        # 進行方向に交点を探す
        for ai in (ai for ai in a if 0 <= ai <= 1):
            v_p = v_fm_pos + v_lay * ai
            # XYZ全てが境界より大きいならば交差している
            if all(map(operator.ge, v_p, v_border)):
                return zero + v_p * v_sign
        # 進行方向になければ戻る
        neg_a = [ai for ai in a if ai < 0]
        if len(neg_a):
            v_p = v_fm_pos + v_lay * max(neg_a)
            return zero + v_p * v_sign

    def on_lay(self, pos):
        """posまでの直線上にあるブロックの座標を返す(始点は含まない)
        
        pos : Position - 終点
        return : generator(Position)
        """
        zero = Position(0,0,0)
        # 鏡写しにする
        v_sign = pos.direc(self).mirror()
        v_self = self.direc(zero) * v_sign
        v_pos = pos.direc(zero) * v_sign
        v_lay = v_pos - v_self
        # v_pos = v_self + a * v_lay
        def calc_a(n1, n2, nv):
            return (n2 - n1) / nv if nv != 0 else 2
        def bounds():
            v = v_self.astype(math.floor)
            while True:
                a = Vector(*list(map(calc_a, v_self, v+1, v_lay)))
                a_min = min(a)
                if a_min > 1:
                    break
                dx, dz, dy = 0, 0, 0
                if a.x == a_min:
                    dx = 1
                    yield v + (dx,0,0)
                if a.z == a_min:
                    dz = 1
                    yield v + (0,dz,0)
                if a.y == a_min:
                    dy = 1
                    yield v + (0,0,dy)
                if dx + dz == 2:
                    yield v + (dx,dz,0)
                if dy + dx == 2:
                    yield v + (dx,0,dy)
                if dz + dy == 2:
                    yield v + (0,dz,dy)
                if dx + dz + dy == 3:
                    yield v + (dx,dz,dy)
                v += (dx,dz,dy)
        return ((zero + v * v_sign) for v in bounds())


class ChunkPosition(metaclass=ImmutableMeta):
    
    X_RANGE = Position.X_RANGE//ChunkRectangular.X
    Z_RANGE = Position.Z_RANGE//ChunkRectangular.Z

    properties = 'x z'

    @classmethod
    def new(cls, x, z):
        x = put_in_range(x, cls.X_RANGE)
        z = put_in_range(z, cls.Z_RANGE)
        return x, z

    # West-North-Bottom
    o = property(lambda self:
        Position(ChunkRectangular.X*self.x, ChunkRectangular.Z*self.z, 0))

    def __add__(self, v):
        return ChunkPosition(self.x+v[0], self.z+v[1])

    def __sub__(self, v):
        return ChunkPosition(self.x-v[0], self.z-v[1])

    def pos(self, x=0, z=0, y=0):
        return Position(self.o.x + x, self.o.z + z, y)
