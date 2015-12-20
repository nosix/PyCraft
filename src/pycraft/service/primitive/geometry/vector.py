# -*- coding: utf8 -*-

import math
import numbers
import operator
from pycraft.common import ImmutableMeta


class Vector(metaclass=ImmutableMeta):
    
    properties = 'x z y'

    @classmethod
    def by_angle(cls, distance, yaw, pitch=None):
        dx = -distance * math.sin(math.radians(yaw))
        dz = distance * math.cos(math.radians(yaw))
        dy = distance * math.sin(math.radians(pitch)) if pitch else 0.0
        return Vector(dx,dz,dy)

    def __calc(self, f, v):
        if isinstance(v, numbers.Number):
            return Vector(f(self.x,v), f(self.z,v), f(self.y,v))
        else:
            if len(v) == 3:
                return Vector(f(self.x,v[0]), f(self.z,v[1]), f(self.y,v[2]))
            if len(v) == 2:
                return Vector(f(self.x,v[0]), f(self.z,v[1]), self.y)
        return NotImplemented

    def __add__(self, v):
        return self.__calc(operator.add, v)

    def __sub__(self, v):
        return self.__calc(operator.sub, v)

    def __mul__(self, v):
        return self.__calc(operator.mul, v)
    
    def __truediv__(self, v):
        return self.__calc(operator.truediv, v)
    
    def __radd__(self, v):
        return self.__calc(operator.add, v)

    def __rsub__(self, v):
        return self.__calc(operator.sub, v)
    
    def __rmul__(self, v):
        return self.__calc(operator.mul, v)

    def distance(self):
        return math.sqrt(self.x**2 + self.z**2 + self.y**2)

    def norm(self):
        return self / self.distance()

    def dot(self, v, is_3d=True):
        if is_3d:
            return self.x*v.x + self.z*v.z + self.y*v.y
        else:
            return self.x*v.x + self.z*v.z

    def cross(self, v, is_3d=True):
        if is_3d:
            return Vector(
                self.z*v.y-self.y*v.z,
                self.y*v.x-self.x*v.y,
                self.x*v.z-self.z*v.x)
        else:
            return self.x*v.z - self.z*v.x

    def astype(self, func):
        return Vector(func(self.x), func(self.z), func(self.y))

    def rotate(self, yaw):
        """yaw の角度で回転する
        
        yaw : float - 回転の角度
                    z-
                   (180)
            (90) x-    x+ (270)
                   (0)
                    z+
        """
        rad = math.radians(yaw)
        x = -self.z * math.sin(rad) + self.x * math.cos(rad)
        z = self.z * math.cos(rad) + self.x * math.sin(rad)
        return Vector(x, z, self.y)

    def mirror(self):
        """鏡写しにする際の各次元の方向を返す
        
        return : Vector - 各次元の方向は 1 or -1
        """
        return self.astype(lambda n: -1 if n < 0 else 1)
