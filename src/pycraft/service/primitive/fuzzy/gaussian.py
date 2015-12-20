# -*- coding: utf8 -*-

import math
from pycraft.common.util import ndarray, product


class GaussianKernel:
    
    __slots__ = ['_size', '_kernel']

    def __init__(self, size):
        self._size = size
        self._kernel = ndarray(2*size + 1, 2*size + 1)
        bell_size = 1.0 / size
        bell_height = 2 * size
        for dx, dz in product(range(-size, size+1), range(-size, size+1)):
            bx = bell_size * dx
            bz = bell_size * dz
            self._kernel[dx+size][dz+size] = \
                bell_height * math.exp(-(bx**2 + bz**2) / 2)

    def get(self, dx, dz):
        return self._kernel[dx+self._size][dz+self._size]
