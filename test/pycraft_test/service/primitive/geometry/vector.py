# -*- coding: utf8 -*-

from unittest import TestCase
from pycraft.service.primitive.geometry import Vector


class VectorTestCase(TestCase):

    def assertVectorEqual(self, v1, v2):
        for n1, n2 in zip(v1, v2):
            self.assertAlmostEqual(n1, n2)

    def test(self):
        self.assertVectorEqual(Vector.by_angle(1, -90), (1, 0))
        self.assertVectorEqual(Vector.by_angle(1, 0), (0, 1))
        self.assertVectorEqual(Vector.by_angle(1, 90), (-1, 0))
        self.assertVectorEqual(Vector.by_angle(1, 180), (0, -1))
        self.assertVectorEqual(Vector.by_angle(1, 270), (1, 0))
        self.assertVectorEqual(Vector.by_angle(1, 360), (0, 1))
        self.assertVectorEqual(Vector.by_angle(1, 450), (-1, 0))
