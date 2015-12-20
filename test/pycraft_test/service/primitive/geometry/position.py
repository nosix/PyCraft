# -*- coding: utf8 -*-

from unittest import TestCase
from pycraft.service.primitive.geometry import Position


class PositionTestCase(TestCase):

    def assertPositionEqual(self, p1, p2):
        for n1, n2 in zip(p1, p2):
            self.assertAlmostEquals(n1, n2)
    
    def assertLayEqual(self, l1, l2):
        l1 = list(l1)
        l2 = list(l2)
        self.assertEquals(len(l1), len(l2))
        for p1, p2 in zip(l1, l2):
            self.assertEqual(p1, p2)

    def test_angle_h_01(self):
        p0 = Position(100, 100, 64)  # center
        pe = Position(150, 100, 64)  # 東
        pw = Position(50, 100, 64)  # 西
        ps = Position(100, 150, 64)  # 南
        pn = Position(100, 50, 64)  # 北
        pu = Position(100, 100, 127)  # 上
        pd = Position(100, 100, 0)  # 下
        
        # yaw 南
        self.assertAlmostEqual(p0.angle_h(ps, 0), 0)
        self.assertAlmostEqual(p0.angle_h(pw, 0), 90)
        self.assertAlmostEqual(p0.angle_h(pn, 0), 180)
        self.assertAlmostEqual(p0.angle_h(pe, 0), -90)
        
        # yaw 西
        self.assertAlmostEqual(p0.angle_h(ps, 90), -90)
        self.assertAlmostEqual(p0.angle_h(pw, 90), 0)
        self.assertAlmostEqual(p0.angle_h(pn, 90), 90)
        self.assertAlmostEqual(p0.angle_h(pe, 90), -180)

        # yaw 北
        self.assertAlmostEqual(p0.angle_h(ps, 180), -180)
        self.assertAlmostEqual(p0.angle_h(pw, 180), -90)
        self.assertAlmostEqual(p0.angle_h(pn, 180), 0)
        self.assertAlmostEqual(p0.angle_h(pe, 180), 90)

        # yaw 東
        self.assertAlmostEqual(p0.angle_h(ps, 270), 90)
        self.assertAlmostEqual(p0.angle_h(pw, 270), -180)
        self.assertAlmostEqual(p0.angle_h(pn, 270), -90)
        self.assertAlmostEqual(p0.angle_h(pe, 270), 0)

        # yaw 南
        self.assertAlmostEqual(p0.angle_h(ps, 360), 0)
        self.assertAlmostEqual(p0.angle_h(pw, 360), 90)
        self.assertAlmostEqual(p0.angle_h(pn, 360), -180)
        self.assertAlmostEqual(p0.angle_h(pe, 360), -90)

        # yaw 西
        self.assertAlmostEqual(p0.angle_h(ps, 450), -90)
        self.assertAlmostEqual(p0.angle_h(pw, 450), 0)
        self.assertAlmostEqual(p0.angle_h(pn, 450), 90)
        self.assertAlmostEqual(p0.angle_h(pe, 450), -180)

        # yaw 東
        self.assertAlmostEqual(p0.angle_h(ps, -90), 90)
        self.assertAlmostEqual(p0.angle_h(pw, -90), 180)
        self.assertAlmostEqual(p0.angle_h(pn, -90), -90)
        self.assertAlmostEqual(p0.angle_h(pe, -90), 0)
        
        self.assertAlmostEqual(p0.angle_h(p0, 0), None)
        
        self.assertAlmostEqual(p0.angle_h(pu, 0), None)
        self.assertAlmostEqual(p0.angle_h(pu, 90), None)
        self.assertAlmostEqual(p0.angle_h(pu, 180), None)
        self.assertAlmostEqual(p0.angle_h(pu, 270), None)
        self.assertAlmostEqual(p0.angle_h(pu, 360), None)
        self.assertAlmostEqual(p0.angle_h(pu, 450), None)
        self.assertAlmostEqual(p0.angle_h(pu, -90), None)

        self.assertAlmostEqual(p0.angle_h(pd, 0), None)
        self.assertAlmostEqual(p0.angle_h(pd, 90), None)
        self.assertAlmostEqual(p0.angle_h(pd, 180), None)
        self.assertAlmostEqual(p0.angle_h(pd, 270), None)
        self.assertAlmostEqual(p0.angle_h(pd, 360), None)
        self.assertAlmostEqual(p0.angle_h(pd, 450), None)
        self.assertAlmostEqual(p0.angle_h(pd, -90), None)

    def test_angle_h_02(self):
        p0 = Position(100, 100, 64)  # center
        pse = Position(150, 150, 64)  # 南東
        psw = Position(50, 150, 64)  # 南西
        pne = Position(150, 50, 64)  # 北東
        pnw = Position(50, 50, 64)  # 北西
        
        self.assertAlmostEqual(p0.angle_h(pse, 0), -45)
        self.assertAlmostEqual(p0.angle_h(pse, -45), 0)
        self.assertAlmostEqual(p0.angle_h(pse, -90), 45)

        self.assertAlmostEqual(p0.angle_h(psw, 90), -45)
        self.assertAlmostEqual(p0.angle_h(psw, 45), 0)
        self.assertAlmostEqual(p0.angle_h(psw, 0), 45)

        self.assertAlmostEqual(p0.angle_h(pne, -90), -45)
        self.assertAlmostEqual(p0.angle_h(pne, -135), 0)
        self.assertAlmostEqual(p0.angle_h(pne, -180), 45)

        self.assertAlmostEqual(p0.angle_h(pnw, 180), -45)
        self.assertAlmostEqual(p0.angle_h(pnw, 135), 0)
        self.assertAlmostEqual(p0.angle_h(pnw, 90), 45)

    def test_angle_v(self):
        p0 = Position(100, 100, 60)  # center
        pe = Position(150, 100, 60)  # 東
        pw = Position(50, 100, 60)  # 西
        ps = Position(100, 150, 60)  # 南
        pn = Position(100, 50, 60)  # 北

        p0u = Position(100, 100, 110)  # 上
        peu = Position(150, 100, 110)  # 東上
        pwu = Position(50, 100, 110)  # 西上
        psu = Position(100, 150, 110)  # 南上
        pnu = Position(100, 50, 110)  # 北上

        p0d = Position(100, 100, 10)  # 下
        ped = Position(150, 100, 10)  # 東下
        pwd = Position(50, 100, 10)  # 西下
        psd = Position(100, 150, 10)  # 南下
        pnd = Position(100, 50, 10)  # 北下

        self.assertAlmostEquals(p0.angle_v(p0, 0), 0)
        self.assertAlmostEquals(p0.angle_v(ps, 0), 0)
        self.assertAlmostEquals(p0.angle_v(pw, 0), 0)
        self.assertAlmostEquals(p0.angle_v(pn, 0), 0)
        self.assertAlmostEquals(p0.angle_v(pe, 0), 0)

        self.assertAlmostEquals(p0.angle_v(p0u, 0), 90)
        self.assertAlmostEquals(p0.angle_v(psu, 0), 45)
        self.assertAlmostEquals(p0.angle_v(pwu, 0), 45)
        self.assertAlmostEquals(p0.angle_v(pnu, 0), 45)
        self.assertAlmostEquals(p0.angle_v(peu, 0), 45)

        self.assertAlmostEquals(p0.angle_v(p0d, 0), -90)
        self.assertAlmostEquals(p0.angle_v(psd, 0), -45)
        self.assertAlmostEquals(p0.angle_v(pwd, 0), -45)
        self.assertAlmostEquals(p0.angle_v(pnd, 0), -45)
        self.assertAlmostEquals(p0.angle_v(ped, 0), -45)

        self.assertAlmostEquals(p0.angle_v(p0, 45), 0)
        self.assertAlmostEquals(p0.angle_v(ps, 45), -45)
        self.assertAlmostEquals(p0.angle_v(p0, 90), 0)
        self.assertAlmostEquals(p0.angle_v(pw, 90), -90)
        self.assertAlmostEquals(p0.angle_v(p0, -45), 0)
        self.assertAlmostEquals(p0.angle_v(pn, -45), 45)
        self.assertAlmostEquals(p0.angle_v(p0, -90), 0)
        self.assertAlmostEquals(p0.angle_v(pe, -90), 90)

        self.assertAlmostEquals(p0.angle_v(p0u, 45), 45)
        self.assertAlmostEquals(p0.angle_v(psu, 45), 0)
        self.assertAlmostEquals(p0.angle_v(p0u, 90), 0)
        self.assertAlmostEquals(p0.angle_v(pwu, 90), -45)
        self.assertAlmostEquals(p0.angle_v(p0u, -45), 135)
        self.assertAlmostEquals(p0.angle_v(pnu, -45), 90)
        self.assertAlmostEquals(p0.angle_v(p0u, -90), 180)
        self.assertAlmostEquals(p0.angle_v(peu, -90), 135)

        self.assertAlmostEquals(p0.angle_v(p0d, 45), -135)
        self.assertAlmostEquals(p0.angle_v(psd, 45), -90)
        self.assertAlmostEquals(p0.angle_v(p0d, 90), -180)
        self.assertAlmostEquals(p0.angle_v(pwd, 90), -135)
        self.assertAlmostEquals(p0.angle_v(p0d, -45), -45)
        self.assertAlmostEquals(p0.angle_v(pnd, -45), 0)
        self.assertAlmostEquals(p0.angle_v(p0d, -90), 0)
        self.assertAlmostEquals(p0.angle_v(ped, -90), 45)

    def test_intersection_01(self):
        p0 = Position(100.5, 100.5, 60.5)

        self.assertEqual(p0.intersection(p0), None)

        pn = Position(100.5, 99.5, 60.5)
        ps = Position(100.5, 101.5, 60.5)
        pw = Position(99.5, 100.5, 60.5)
        pe = Position(101.5, 100.5, 60.5)
        pd = Position(100.5, 100.5, 59.5)
        pu = Position(100.5, 100.5, 61.5)

        self.assertPositionEqual(p0.intersection(pn), (100.5, 100, 60.5))
        self.assertPositionEqual(p0.intersection(ps), (100.5, 101, 60.5))
        self.assertPositionEqual(p0.intersection(pw), (100, 100.5, 60.5))
        self.assertPositionEqual(p0.intersection(pe), (101, 100.5, 60.5))
        self.assertPositionEqual(p0.intersection(pd), (100.5, 100.5, 60))
        self.assertPositionEqual(p0.intersection(pu), (100.5, 100.5, 61))

        # 境界線上
        pn = Position(100.5, 100, 60.5)
        ps = Position(100.5, 101, 60.5)
        pw = Position(100, 100.5, 60.5)
        pe = Position(101, 100.5, 60.5)
        pd = Position(100.5, 100.5, 60)
        pu = Position(100.5, 100.5, 61)

        self.assertPositionEqual(p0.intersection(pn), (100.5, 100, 60.5))
        self.assertPositionEqual(p0.intersection(ps), (100.5, 101, 60.5))
        self.assertPositionEqual(p0.intersection(pw), (100, 100.5, 60.5))
        self.assertPositionEqual(p0.intersection(pe), (101, 100.5, 60.5))
        self.assertPositionEqual(p0.intersection(pd), (100.5, 100.5, 60))
        self.assertPositionEqual(p0.intersection(pu), (100.5, 100.5, 61))

        # 2マス以上離れている点
        pn = Position(100.5, 98, 60.5)
        ps = Position(100.5, 103, 60.5)
        pw = Position(98, 100.5, 60.5)
        pe = Position(103, 100.5, 60.5)
        pd = Position(100.5, 100.5, 58)
        pu = Position(100.5, 100.5, 63)

        self.assertPositionEqual(p0.intersection(pn), (100.5, 100, 60.5))
        self.assertPositionEqual(p0.intersection(ps), (100.5, 101, 60.5))
        self.assertPositionEqual(p0.intersection(pw), (100, 100.5, 60.5))
        self.assertPositionEqual(p0.intersection(pe), (101, 100.5, 60.5))
        self.assertPositionEqual(p0.intersection(pd), (100.5, 100.5, 60))
        self.assertPositionEqual(p0.intersection(pu), (100.5, 100.5, 61))

        pnd = Position(100.5, 99.5, 59.5)
        psd = Position(100.5, 101.5, 59.5)
        pwd = Position(99.5, 100.5, 59.5)
        ped = Position(101.5, 100.5, 59.5)

        self.assertPositionEqual(p0.intersection(pnd), (100.5, 100, 60))
        self.assertPositionEqual(p0.intersection(psd), (100.5, 101, 60))
        self.assertPositionEqual(p0.intersection(pwd), (100, 100.5, 60))
        self.assertPositionEqual(p0.intersection(ped), (101, 100.5, 60))

        pnu = Position(100.5, 99.5, 61.5)
        psu = Position(100.5, 101.5, 61.5)
        pwu = Position(99.5, 100.5, 61.5)
        peu = Position(101.5, 100.5, 61.5)

        self.assertPositionEqual(p0.intersection(pnu), (100.5, 100, 61))
        self.assertPositionEqual(p0.intersection(psu), (100.5, 101, 61))
        self.assertPositionEqual(p0.intersection(pwu), (100, 100.5, 61))
        self.assertPositionEqual(p0.intersection(peu), (101, 100.5, 61))

        pnwd = Position(99.5, 99.5, 59.5)
        pned = Position(101.5, 99.5, 59.5)
        pswd = Position(99.5, 101.5, 59.5)
        psed = Position(101.5, 101.5, 59.5)

        self.assertPositionEqual(p0.intersection(pnwd), (100, 100, 60))
        self.assertPositionEqual(p0.intersection(pned), (101, 100, 60))
        self.assertPositionEqual(p0.intersection(pswd), (100, 101, 60))
        self.assertPositionEqual(p0.intersection(psed), (101, 101, 60))

        pnwu = Position(99.5, 99.5, 61.5)
        pneu = Position(101.5, 99.5, 61.5)
        pswu = Position(99.5, 101.5, 61.5)
        pseu = Position(101.5, 101.5, 61.5)

        self.assertPositionEqual(p0.intersection(pnwu), (100, 100, 61))
        self.assertPositionEqual(p0.intersection(pneu), (101, 100, 61))
        self.assertPositionEqual(p0.intersection(pswu), (100, 101, 61))
        self.assertPositionEqual(p0.intersection(pseu), (101, 101, 61))

    def test_intersection_02(self):
        p0 = Position(100, 100.5, 60.5)

        self.assertEqual(p0.intersection(p0), None)
        
        pn = Position(100, 99.5, 60.5)
        ps = Position(100, 101.5, 60.5)
        pw = Position(99, 100.5, 60.5)
        pe = Position(101, 100.5, 60.5)
        pd = Position(100, 100.5, 59.5)
        pu = Position(100, 100.5, 61.5)
        
        self.assertPositionEqual(p0.intersection(pn), (100, 100, 60.5))
        self.assertPositionEqual(p0.intersection(ps), (100, 101, 60.5))
        self.assertPositionEqual(p0.intersection(pw), (100, 100.5, 60.5))
        self.assertPositionEqual(p0.intersection(pe), (100, 100.5, 60.5))
        self.assertPositionEqual(p0.intersection(pd), (100, 100.5, 60))
        self.assertPositionEqual(p0.intersection(pu), (100, 100.5, 61))

        p0 = Position(100.5, 100, 60.5)

        self.assertEqual(p0.intersection(p0), None)
        
        pn = Position(100.5, 99, 60.5)
        ps = Position(100.5, 101, 60.5)
        pw = Position(99.5, 100, 60.5)
        pe = Position(101.5, 100, 60.5)
        pd = Position(100.5, 100, 59.5)
        pu = Position(100.5, 100, 61.5)
        
        self.assertPositionEqual(p0.intersection(pn), (100.5, 100, 60.5))
        self.assertPositionEqual(p0.intersection(ps), (100.5, 100, 60.5))
        self.assertPositionEqual(p0.intersection(pw), (100, 100, 60.5))
        self.assertPositionEqual(p0.intersection(pe), (101, 100, 60.5))
        self.assertPositionEqual(p0.intersection(pd), (100.5, 100, 60))
        self.assertPositionEqual(p0.intersection(pu), (100.5, 100, 61))

        p0 = Position(100.5, 100.5, 60)

        self.assertEqual(p0.intersection(p0), None)
        
        pn = Position(100.5, 99.5, 60)
        ps = Position(100.5, 101.5, 60)
        pw = Position(99.5, 100.5, 60)
        pe = Position(101.5, 100.5, 60)
        pd = Position(100.5, 100.5, 59)
        pu = Position(100.5, 100.5, 61)
        
        self.assertPositionEqual(p0.intersection(pn), (100.5, 100, 60))
        self.assertPositionEqual(p0.intersection(ps), (100.5, 101, 60))
        self.assertPositionEqual(p0.intersection(pw), (100, 100.5, 60))
        self.assertPositionEqual(p0.intersection(pe), (101, 100.5, 60))
        self.assertPositionEqual(p0.intersection(pd), (100.5, 100.5, 60))
        self.assertPositionEqual(p0.intersection(pu), (100.5, 100.5, 60))

        p0 = Position(100, 100, 60.5)

        self.assertEqual(p0.intersection(p0), None)
        
        pn = Position(100, 99, 60.5)
        ps = Position(100, 101, 60.5)
        pw = Position(99, 100, 60.5)
        pe = Position(101, 100, 60.5)
        pd = Position(100, 100, 59.5)
        pu = Position(100, 100, 61.5)
        
        self.assertPositionEqual(p0.intersection(pn), (100, 100, 60.5))
        self.assertPositionEqual(p0.intersection(ps), (100, 100, 60.5))
        self.assertPositionEqual(p0.intersection(pw), (100, 100, 60.5))
        self.assertPositionEqual(p0.intersection(pe), (100, 100, 60.5))
        self.assertPositionEqual(p0.intersection(pd), (100, 100, 60))
        self.assertPositionEqual(p0.intersection(pu), (100, 100, 61))

        p0 = Position(100, 100, 60)

        self.assertEqual(p0.intersection(p0), None)
        
        pn = Position(100, 99, 60)
        ps = Position(100, 101, 60)
        pw = Position(99, 100, 60)
        pe = Position(101, 100, 60)
        pd = Position(100, 100, 59)
        pu = Position(100, 100, 61)
        
        self.assertPositionEqual(p0.intersection(pn), (100, 100, 60))
        self.assertPositionEqual(p0.intersection(ps), (100, 100, 60))
        self.assertPositionEqual(p0.intersection(pw), (100, 100, 60))
        self.assertPositionEqual(p0.intersection(pe), (100, 100, 60))
        self.assertPositionEqual(p0.intersection(pd), (100, 100, 60))
        self.assertPositionEqual(p0.intersection(pu), (100, 100, 60))

    def test_on_lay(self):
        p0 = Position(100.5, 100.5, 60.5)
        
        p1 = Position(102.5, 100.5, 60.5)
        self.assertLayEqual(p0.on_lay(p1), [
            (101,100,60), (102,100,60)])

        p1 = Position(102.5, 102.5, 60.5)
        self.assertLayEqual(p0.on_lay(p1), [
            (101,100,60), (100,101,60), (101,101,60),
            (102,101,60), (101,102,60), (102,102,60)])

        p1 = Position(102.5, 102.5, 62.5)
        self.assertLayEqual(p0.on_lay(p1), [
            (101,100,60), (100,101,60), (100,100,61),
            (101,101,60), (101,100,61), (100,101,61), (101,101,61),
            (102,101,61), (101,102,61), (101,101,62),
            (102,102,61), (102,101,62), (101,102,62), (102,102,62)])

        p0 = Position(100, 100.5, 60.5)
        p1 = Position(102, 100.5, 60.5)
        self.assertLayEqual(p0.on_lay(p1), [
            (101,100,60), (102,100,60)])

        p0 = Position(100, 100, 60.5)
        p1 = Position(102, 102, 60.5)
        self.assertLayEqual(p0.on_lay(p1), [
            (101,100,60), (100,101,60), (101,101,60),
            (102,101,60), (101,102,60), (102,102,60)])

        p0 = Position(100, 100, 60)
        p1 = Position(102, 102, 62)
        self.assertLayEqual(p0.on_lay(p1), [
            (101,100,60), (100,101,60), (100,100,61),
            (101,101,60), (101,100,61), (100,101,61), (101,101,61),
            (102,101,61), (101,102,61), (101,101,62),
            (102,102,61), (102,101,62), (101,102,62), (102,102,62)])
