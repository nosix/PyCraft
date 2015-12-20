# -*- coding: utf8 -*-

from pycraft.common import ImmutableMeta


class Color(metaclass=ImmutableMeta):
    
    properties = 'r g b'

    def __add__(self, c):
        return Color(self.r+c.r, self.g+c.g, self.b+c.b)

    def __sub__(self, c):
        return Color(self.r-c.r, self.g-c.g, self.b-c.b)

    def __mul__(self, v):
        return Color(self.r*v, self.g*v, self.b*v)

    def __truediv__(self, v):
        return Color(self.r/v, self.g/v, self.b/v)

    def __pow__(self, v):
        return Color(self.r**v, self.g**v, self.b**v)

    def astype(self, func):
        return Color(func(self.r), func(self.g), func(self.b))