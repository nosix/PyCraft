# -*- coding: utf8 -*-

import time
from pycraft.service.primitive.geometry import Vector, Position
from pycraft.service.primitive.fuzzy import Random


class MotionLaw:
    
    MAX_REBOUNDING = 8

    def __init__(self):
        self._random = Random(int(time.time()))  # TODO: seed を変更する

    def direc_when_fall(self):
        # XZ方向に -5..5 の範囲でブレをつくる
        def get_value():
            return (self._random.next_float() - 0.5) * 10
        x = get_value()
        z = get_value()
        # Y方向に 0..3 の範囲でブレをつくる
        y = self._random.next_float() * 3
        return Vector(x, z, y)
        
    def direc_when_remove(self, player_pos, entity_pos):
        # XZ方向に -0.5..0.5 の範囲でブレをつくる
        def get_value():
            return self._random.next_float() - 0.5
        x = get_value()
        z = get_value()
        return entity_pos.direc(player_pos) / 10 + (x, z, 0)

    def move_when_chunk_changed(self, pos, terrain):
        o = pos.center_in_block
        p = pos
        # 現在のブロックが埋まっているならば周囲に移動
        if not terrain.is_transparent(p):
            a = (p.z - o.z) / (p.x - o.x)
            if abs(a) >= 1:
                ratio = 1.5 / abs(p.z - o.z)
            else:
                ratio = 1.5 / abs(p.x - o.x)
            d = p.direc(o)
            return o + (ratio * d.x, ratio * d.z, d.y)
        else:
            # 下にブロックが無ければ下に移動
            p -= (0, 0, 1)
            if terrain.is_transparent(p):
                return p

    @staticmethod
    def move_down(terrain, o):
        # 下に移動できるならば移動する
        while True:
            o -= (0, 0, 1)
            if not terrain.is_transparent(o):
                o += (0, 0, 1)
                break
        return o

    @staticmethod
    def axis(n, v):
        int_n = int(n)
        if v == 0:
            # 軸と平行
            return None
        if int_n == n:
            if (int_n - 1) < (n + v) < (int_n + 1):
                # 軸をまたがない
                return None
            else:
                # 軸をまたぐ
                return int_n - 1 if v < 0 else int_n + 1
        else:
            if int_n == int(n + v):
                # 軸をまたがない
                return None
            else:
                # 軸をまたぐ
                return int_n if v < 0 else int_n + 1

    @staticmethod
    def intercection(p, q, v):
        x, z = MotionLaw.axis(p.x, v.x), MotionLaw.axis(p.z, v.z)
        b = q.x*p.z - p.x*q.z
        r_x = Position(x, (x*v.z+b)/v.x, q.y) if x != None else None
        r_z = Position((z*v.x-b)/v.z, z, q.y) if z != None else None
        if r_x == None:
            return r_z 
        if r_z == None:
            return r_x
        return r_x if r_x.distance(p) < r_z.distance(p) else r_z

    def push_out(self, pos, from_pos, terrain):
        # 計算は足元の位置で行う
        p = from_pos
        o = p.center_in_block
        q = pos
        v = q.direc(p)
        for _ in range(self.MAX_REBOUNDING):
            # 下に移動できたら移動する
            d = o.direc(MotionLaw.move_down(terrain, o))
            o -= d
            p -= d
            q -= d
            # 境界との交点を求める
            r = MotionLaw.intercection(p, q, v)
            if r == None:
                break
            # 現在のブロックが埋まっていない場合
            if terrain.is_transparent(o):
                v -= r.direc(p)
            # 周辺のブロックに移動する
            d = r.direc(o)
            if abs(d.x) > abs(d.z):
                # X方向に移動する
                if not terrain.is_transparent(o + (2*d.x, 0, 0)):
                    v = Vector(-v.x, v.z, v.y)
                else:
                    o += (2*d.x, 0, 0)
            else:
                # Z方向に移動する
                if not terrain.is_transparent(o + (0, 2*d.z, 0)):
                    v = Vector(v.x, -v.z, v.y)
                else:
                    o += (0, 2*d.z, 0)
            p = r
            q = r + v
        # 現在のブロックが埋まっているならば上に移動
        while True:
            if terrain.is_transparent(q):
                break
            q += (0, 0, 1)
        return q
