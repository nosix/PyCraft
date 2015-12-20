# -*- coding: utf8 -*-

from pycraft.common.util import ndarray, product


class Noise:
    
    __slots__ = ['_noise']

    def __init__(
            self,
            base,
            xSize, ySize, zSize,
            xSamplingRate, ySamplingRate, zSamplingRate,
            x, y, z):
        assert xSamplingRate != 0
        assert ySamplingRate != 0
        assert zSamplingRate != 0
        assert xSize % xSamplingRate == 0
        assert ySize % ySamplingRate == 0
        assert zSize % zSamplingRate == 0
        
        self._noise = ndarray(xSize + 1, zSize + 1, ySize + 1)
        r = product(
            range(0, xSize+1, xSamplingRate),
            range(0, zSize+1, zSamplingRate),
            range(0, ySize+1, ySamplingRate))
        for xx, zz, yy in r:
            self._noise[xx][zz][yy] = base.noise_3d(x+xx, y+yy, z+zz)
        def gen_nd(size, samplingRate):
            nd = [None] * size
            for i in range(size):
                m = i % samplingRate
                n1 = i - m
                n2 = n1 + samplingRate
                d2 = float(m) / samplingRate
                d1 = 1 - d2
                nd[i] = (i, n1, n2, d1, d2)
            return nd
        x_nd = gen_nd(xSize, xSamplingRate)
        y_nd = gen_nd(ySize, ySamplingRate)
        z_nd = gen_nd(zSize, zSamplingRate)
        for xx, n1x, n2x, d1x, d2x in x_nd:
            for zz, n1z, n2z, d1z, d2z in z_nd:
                for yy, n1y, n2y, d1y, d2y in y_nd:
                    if n1x == xx and n1y == yy and n1z == zz:
                        continue
                    self._noise[xx][zz][yy] = (
                        d1z * (
                            d1y * (
                                d1x * self._noise[n1x][n1z][n1y] +
                                d2x * self._noise[n2x][n1z][n1y]) +
                            d2y * (
                                d1x * self._noise[n1x][n1z][n2y] +
                                d2x * self._noise[n2x][n1z][n2y])) +
                        d2z * (
                            d1y * (
                                d1x * self._noise[n1x][n2z][n1y] +
                                d2x * self._noise[n2x][n2z][n1y]) +
                            d2y * (
                                d1x * self._noise[n1x][n2z][n2y] +
                                d2x * self._noise[n2x][n2z][n2y])))

    def on(self, x, z, y):
        return self._noise[x][z][y]
