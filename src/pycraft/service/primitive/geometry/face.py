# -*- coding: utf8 -*-

from pycraft.common import ImmutableMeta
from .vector import Vector


class Face(metaclass=ImmutableMeta):

    DIRECTION = (
        Vector(0,0,-1), Vector(0,0,1),
        Vector(0,-1,0), Vector(0,1,0),
        Vector(-1,0,0), Vector(1,0,0))

    properties = 'h v mix'

    @staticmethod
    def _vertical(pitch):
        return 1 if pitch < 0 else 0

    @staticmethod
    def _horizontal(yaw):
        if 45 <= yaw <= 135:
            return 4
        if 225 <= yaw <= 315:
            return 5
        if 135 < yaw < 225:
            return 2
        else:
            return 3

    @staticmethod
    def _mix(yaw, pitch):
        if pitch > 45:
            return 0
        if pitch < -45:
            return 1
        return Face._horizontal(yaw)

    @classmethod
    def by_angle(cls, yaw, pitch):
        """角度から向きをえる

        vertical:
            1 : 上面(下向き)
            0 : 下面(上向き)

        horizontal:
                   (0)
                    3
            (270) 5   4 (90)
                    2
                  (180)

        mix:
            1 : (< -45)
            0 : (> +45)
            horizontal : (other)
        """
        return Face(
            cls._horizontal(yaw), cls._vertical(pitch), cls._mix(yaw, pitch))

    def inverse(self):
        return Face(self.h^1, self.v^1, self.mix^1)
