# -*- coding: utf8 -*-

import math


class Simplex:
    
    __slots__ = [
        '_octaves', '_persistence', '_expansion', '_perm',
        '_offset_x', '_offset_y', '_offset_z', '_offset_w',
        ]
    
    # from Perlin
    GRAD3 = [
        [1, 1, 0], [-1, 1, 0], [1, -1, 0], [-1, -1, 0],
        [1, 0, 1], [-1, 0, 1], [1, 0, -1], [-1, 0, -1],
        [0, 1, 1], [0, -1, 1], [0, 1, -1], [0, -1, -1]]
    
    # from Simplex
    SQRT_3 = math.sqrt(3)
    SQRT_5 = math.sqrt(5)
    F2 = 0.5 * (SQRT_3 - 1)
    G2 = (3 - SQRT_3) / 6.0
    G22 = G2 * 2.0 - 1
    F3 = 1.0 / 3.0
    G3 = 1.0 / 6.0
    F4 = (SQRT_5 - 1.0) / 4.0
    G4 = (5.0 - SQRT_5) / 20.0
    G42 = G4 * 2.0
    G43 = G4 * 3.0
    G44 = G4 * 4.0 - 1.0

    def __init__(self, random, octaves, persistence, expansion=1):
        # from Perlin
        self._octaves = octaves
        self._persistence = persistence
        self._expansion = expansion
        self._offset_x = random.next_float() * 256
        self._offset_y = random.next_float() * 256
        self._offset_z = random.next_float() * 256
        self._perm = [0] * 512

        for i in range(256):
            self._perm[i] = random.next_int() % 256
        for i in range(256, 512):
            self._perm[i] = 0

        for i in range(256):
            pos = random.next_int() % (256 - i) + i
            old = self._perm[i]
            self._perm[i] = self._perm[pos]
            self._perm[pos] = old
            self._perm[i + 256] = self._perm[i]

        # from Simplex
        self._offset_w = random.next_float() * 256

    def noise_3d(self, x, y, z, normalized=True):
        result = 0.0
        amp = 1.0
        freq = 1.0
        max_ = 0.0

        x *= self._expansion
        y *= self._expansion
        z *= self._expansion

        for _ in range(self._octaves):
            result += self._calc_noise_3d(x * freq, y * freq, z * freq) * amp
            max_ += amp
            freq *= 2
            amp *= self._persistence

        if normalized:
            result /= max_

        return result
    
    def noise_2d(self, x, z, normalized=True):
        result = 0.0
        amp = 1.0
        freq = 1.0
        max_ = 0.0

        x *= self._expansion
        z *= self._expansion

        for _ in range(self._octaves):
            result += self._calc_noise_2d(x * freq, z * freq) * amp
            max_ += amp
            freq *= 2
            amp *= self._persistence

        if normalized:
            result /= max_

        return result

    def _calc_noise_3d(self, x, y, z):
        x += self._offset_x
        y += self._offset_y
        z += self._offset_z

        # Skew the input space to determine which simplex cell we're in
        s = (x + y + z) * self.F3  # Very nice and simple skew factor for 3D
        i = int(x + s)
        j = int(y + s)
        k = int(z + s)
        t = (i + j + k) * self.G3
        # Unskew the cell origin back to (x,y,z) space
        # The x,y,z distances from the cell origin
        x0 = x - (i - t)
        y0 = y - (j - t)
        z0 = z - (k - t)

        # For the 3D case, the simplex shape is a slightly irregular tetrahedron.

        # Determine which simplex we are in.
        if x0 >= y0:
            if y0 >= z0:  # X Y Z order
                i1, j1, k1 = 1, 0, 0
                i2, j2, k2 = 1, 1, 0
            elif x0 >= z0:  # X Z Y order
                i1, j1, k1 = 1, 0, 0
                i2, j2, k2 = 1, 0, 1
            else:  # Z X Y order
                i1, j1, k1 = 0, 0, 1
                i2, j2, k2 = 1, 0, 1
        else:  # x0<y0
            if y0 < 0:  # Z Y X order
                i1, j1, k1 = 0, 0, 1
                i2, j2, k2 = 0, 1, 1
            elif x0 < z0:  # Y Z X order
                i1, j1, k1 = 0, 1, 0
                i2, j2, k2 = 0, 1, 1
            else:  # Y X Z order
                i1, j1, k1 = 0, 1, 0
                i2, j2, k2 = 1, 1, 0

        # A step of (1,0,0) in (i,j,k) means a step of (1-c,-c,-c) in (x,y,z),
        # a step of (0,1,0) in (i,j,k) means a step of (-c,1-c,-c) in (x,y,z), and
        # a step of (0,0,1) in (i,j,k) means a step of (-c,-c,1-c) in (x,y,z), where
        # c = 1/6.
        # Offsets for second corner in (x,y,z) coords
        x1 = x0 - i1 + self.G3 
        y1 = y0 - j1 + self.G3
        z1 = z0 - k1 + self.G3
        # Offsets for third corner in (x,y,z) coords
        x2 = x0 - i2 + 2.0 * self.G3
        y2 = y0 - j2 + 2.0 * self.G3
        z2 = z0 - k2 + 2.0 * self.G3
        # Offsets for last corner in (x,y,z) coords
        x3 = x0 - 1.0 + 3.0 * self.G3
        y3 = y0 - 1.0 + 3.0 * self.G3
        z3 = z0 - 1.0 + 3.0 * self.G3

        # Work out the hashed gradient indices of the four simplex corners
        ii = i & 255
        jj = j & 255
        kk = k & 255

        n = 0

        # Calculate the contribution from the four corners
        t0 = 0.6 - x0 * x0 - y0 * y0 - z0 * z0
        if t0 > 0:
            gi0 = self.GRAD3[
                self._perm[ii + self._perm[jj + self._perm[kk]]] % 12]
            n += t0 * t0 * t0 * t0 * (gi0[0] * x0 + gi0[1] * y0 + gi0[2] * z0)

        t1 = 0.6 - x1 * x1 - y1 * y1 - z1 * z1
        if t1 > 0:
            gi1 = self.GRAD3[
                self._perm[ii + i1 + self._perm[jj + j1 + self._perm[kk + k1]]] % 12]
            n += t1 * t1 * t1 * t1 * (gi1[0] * x1 + gi1[1] * y1 + gi1[2] * z1)

        t2 = 0.6 - x2 * x2 - y2 * y2 - z2 * z2
        if t2 > 0:
            gi2 = self.GRAD3[
                self._perm[ii + i2 + self._perm[jj + j2 + self._perm[kk + k2]]] % 12]
            n += t2 * t2 * t2 * t2 * (gi2[0] * x2 + gi2[1] * y2 + gi2[2] * z2)

        t3 = 0.6 - x3 * x3 - y3 * y3 - z3 * z3
        if t3 > 0:
            gi3 = self.GRAD3[
                self._perm[ii + 1 + self._perm[jj + 1 +self._perm[kk + 1]]] % 12]
            n += t3 * t3 * t3 * t3 * (gi3[0] * x3 + gi3[1] * y3 + gi3[2] * z3)

        # Add contributions from each corner to get the noise value.
        # The result is scaled to stay just inside [-1,1]
        return 32.0 * n

    def _calc_noise_2d(self, x, y):
        x += self._offset_x
        y += self._offset_y

        # Skew the input space to determine which simplex cell we're in
        s = (x + y) * self.F2  # Hairy factor for 2D
        i = int(x + s)
        j = int(y + s)
        t = (i + j) * self.G2
        # Unskew the cell origin back to (x,y) space
        # The x,y distances from the cell origin
        x0 = x - (i - t)
        y0 = y - (j - t)

        # For the 2D case, the simplex shape is an equilateral triangle.

        # Determine which simplex we are in.
        if x0 > y0:  # lower triangle, XY order: (0,0)->(1,0)->(1,1)
            i1, j1 = 1, 0
        else:  # upper triangle, YX order: (0,0)->(0,1)->(1,1)
            i1, j1 = 0, 1

        # A step of (1,0) in (i,j) means a step of (1-c,-c) in (x,y), and
        # a step of (0,1) in (i,j) means a step of (-c,1-c) in (x,y), where
        # c = (3-sqrt(3))/6

        # Offsets for middle corner in (x,y) unskewed coords
        x1 = x0 - i1 + self.G2
        y1 = y0 - j1 + self.G2
        # Offsets for last corner in (x,y) unskewed coords
        x2 = x0 + self.G22
        y2 = y0 + self.G22

        # Work out the hashed gradient indices of the three simplex corners
        ii = i & 255
        jj = j & 255

        n = 0

        # Calculate the contribution from the three corners
        t0 = 0.5 - x0 * x0 - y0 * y0
        if t0 > 0:
            gi0 = self.GRAD3[self._perm[ii + self._perm[jj]] % 12]
            # (x,y) of grad3 used for 2D gradient
            n += t0 * t0 * t0 * t0 * (gi0[0] * x0 + gi0[1] * y0)

        t1 = 0.5 - x1 * x1 - y1 * y1
        if t1 > 0:
            gi1 = self.GRAD3[self._perm[ii + i1 + self._perm[jj + j1]] % 12]
            n += t1 * t1 * t1 * t1 * (gi1[0] * x1 + gi1[1] * y1)

        t2 = 0.5 - x2 * x2 - y2 * y2
        if t2 > 0:
            gi2 = self.GRAD3[self._perm[ii + 1 + self._perm[jj + 1]] % 12]
            n += t2 * t2 * t2 * t2 * (gi2[0] * x2 + gi2[1] * y2)

        # Add contributions from each corner to get the noise value.
        # The result is scaled to return values in the interval [-1,1].
        return 70.0 * n
