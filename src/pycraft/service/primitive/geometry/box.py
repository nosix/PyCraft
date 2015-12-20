# -*- coding: utf8 -*-

import functools
from pycraft.common import ImmutableMeta
from pycraft.common.util import product
from .vector import Vector
from .position import Position


class Size(metaclass=ImmutableMeta):

    properties = 'width depth height'
    
    def __mul__(self, n):
        return Size(self.width/n, self.depth/n, self.height/n)

    def __truediv__(self, n):
        return Size(self.width/n, self.depth/n, self.height/n)

    def lower_bounds(self, center_bottom, direc=0):
        """底の四隅を左前、右前、左後、右後の順に返す
        
        center_bottom : Position - 底の中心点
        direc : -,0,+ - 向き
            - : 後ろのみ返す
            0 : 四隅を返す
            + : 前のみ返す
        """
        half = self / 2.0
        min_pos = center_bottom - half
        max_pos = center_bottom + half
        def range_z():
            if direc > 0:
                return (max_pos.z, )
            if direc < 0:
                return (min_pos.z, )
            else:
                return (max_pos.z, min_pos.z)
        def each_xz(y):
            return (
                Position(x, z, y)
                    for z, x in product(range_z(), (min_pos.x, max_pos.x)))
        return each_xz(center_bottom.y)


class OrientedBoundingBox(metaclass=ImmutableMeta):
    """Entity の体に使われる直方体
    
    vo : Vector - 中心を表すベクトル
    vf : Vector - 前方向を表すベクトル
    vr : Vector - 右方向を表すベクトル
    vt : Vector - 上方向を表すベクトル
    """
    
    properties = 'vo vf vr vt'

    @classmethod
    def new(cls, center_bottom, size, yaw):
        half = size / 2.0
        vo = center_bottom.direc(Position(0,0,half.height))
        vf = Vector(0,half.depth,0).rotate(yaw)
        vr = Vector(half.width,0,0).rotate(yaw)
        vt = Vector(0,0,half.height)
        return vo, vf, vr, vt
    
    @staticmethod
    def _has_collision_xz(vo, va1, va2, vb1, vb2):
        l = va1.norm()
        rb = abs(l.dot(vb1)) + abs(l.dot(vb2))
        ra = va2.distance()
        interval = abs(l.dot(vo))
        return interval <= ra + rb

    @staticmethod
    def _has_collision_y(vo, va, vb):
        return not abs(vo.y) > va.y + vb.y

    def has_collision(self, other):
        vo = self.vo - other.vo
        has_collision_xz = functools.partial(self._has_collision_xz, vo)
        return (
            has_collision_xz(self.vf, self.vr, other.vf, other.vr) and
            has_collision_xz(self.vr, self.vf, other.vr, other.vf) and
            has_collision_xz(other.vf, other.vr, self.vf, self.vr) and
            has_collision_xz(other.vr, other.vf, self.vr, self.vf) and
            self._has_collision_y(vo, self.vt, other.vt))
