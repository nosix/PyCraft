# -*- coding: utf8 -*-

from queue import Queue
from pycraft.common.util import product
from pycraft.service.primitive.geometry import \
    Vector, Face, Position, ChunkPosition
from pycraft.service.part.block import BlockID


class BlockCursor:
    
    __slots__ = [
        '_center_pos', '_chunks', '_cur_pos', '_direc',
        '_updated_chunk', '_light_level',
        ]

    def __init__(self, terrain, center_pos):
        def get_chunks():
            cx, cz = center_pos.chunk_pos
            r = product(range(cx-1, cx+2), range(cz-1, cz+2))
            for x, z in r:
                chunk = terrain.get_chunk(ChunkPosition(x, z))
                yield chunk.pos, chunk
        # 中心の位置
        self._center_pos = center_pos
        # 中心の周辺 Chunk
        self._chunks = dict(get_chunks())
        # カーソルの現在位置
        self._cur_pos = self._center_pos
        # カーソルが向いている方向
        self._direc = Vector(0,0,0)
        # 更新された Chunk の記録
        self._updated_chunk = set()
        # 更新された light_level の記録
        self._light_level = {}

    updated_chunk = property(lambda self: self._updated_chunk)
    light_lavel = property(lambda self: self._light_level.items())

    def current(self):
        return self._cur_pos, self._chunks[self._cur_pos.chunk_pos] 

    def surrounding(self):
        return list((pos, self._chunks[pos.chunk_pos])
            for pos in (self._cur_pos.by_face(face)
                for face in range(len(Face.DIRECTION))))
        
    def reset(self, x=False, z=False, y=False):
        px = self._center_pos.x if x else self._cur_pos.x
        pz = self._center_pos.z if z else self._cur_pos.z
        py = self._center_pos.y if y else self._cur_pos.y
        self._cur_pos = Position(px, pz, py)

    def move(self, x=0, z=0, y=0):
        self._cur_pos += Vector(x, z, y)
    
    def mark_updated(self, chunk_pos):
        self._updated_chunk.add(chunk_pos)

    def save_light(self, light_level):
        self._light_level[self._cur_pos] = light_level


class BlockLight:
    
    __slots__ = ['_terrain', '_levels', '_queue']

    def __init__(self, terrain):
        self._terrain = terrain
        self._levels = {
            BlockID.TORCH : 14,
            BlockID.BURNING_FURNACE : 13
            }
        self._queue = Queue()

    def update(self):
        if self._queue.empty():
            return set()
        func, pos = self._queue.get_nowait()
        return func(pos)

    def add(self, pos):
        self._queue.put_nowait((self._add, pos))

    def remove(self, pos):
        self._queue.put_nowait((self._remove, pos))

    def _add(self, pos):
        block = self._terrain.get_block(pos)
        light_level = self._levels.get(block.id, 0)
        if light_level == 0:
            return set()
        return self._add_light(pos, light_level)
    
    def _add_light(self, pos, light_level):
        cursor = BlockCursor(self._terrain, pos)
        # X=0 に灯を追加する
        light_level = self._add_column_x(cursor, light_level)
        if light_level > 1:
            # X<0 と X>0 に灯を追加する
            for direc in (-1, 1):
                cursor.move(x=direc)
                l = light_level
                while l > 1:
                    l = self._add_column_x(cursor, l-1)
                    cursor.move(x=direc)
                cursor.reset(x=True)
        return cursor.updated_chunk
    
    def _add_column_x(self, cursor, light_level):
        # Z=0 に灯を追加する
        light_level = self._add_column_xz(cursor, light_level)
        if light_level > 1:
            # Z<0 と Z>0 に灯を追加する
            for direc in (-1, 1):
                cursor.move(z=direc)
                l = light_level
                while l > 1:
                    l = self._add_column_xz(cursor, l-1)
                    cursor.move(z=direc)
                cursor.reset(z=True)
        return light_level
    
    def _add_column_xz(self, cursor, light_level):
        # Y=0 に灯を追加する
        light_level = self._add_point(cursor, light_level)
        if light_level > 1:
            # Y<0 と Y>0 に灯を追加する
            for direc in (-1, 1):
                cursor.move(y=direc)
                l = light_level
                while l > 1:
                    l = self._add_point(cursor, l-1)
                    cursor.move(y=direc)
                cursor.reset(y=True)
        return light_level
    
    def _add_point(self, cursor, light_level):
        # 周辺で最も明るいレベルを求める
        max_light_level = light_level
        for pos, chunk in cursor.surrounding():
            l = chunk.get_block_light(*pos.in_chunk) - 1
            if l > max_light_level:
                max_light_level = l
        # 現在よりも明るければ変更する
        pos, chunk = cursor.current()
        x, z, y = pos.in_chunk
        l = chunk.get_block_light(x, z, y)
        if l < max_light_level:
            chunk.set_block_light(x, z, y, max_light_level)
            cursor.mark_updated(chunk.pos)
            return max_light_level
        else:
            return 0

    def _remove(self, pos):
        cursor = BlockCursor(self._terrain, pos)
        # X=0 の灯を削除する
        if self._remove_column_x(cursor) == 0:
            # X<0 と X>0 の灯を削除する
            for direc in (-1, 1):
                cursor.move(x=direc)
                while self._remove_column_x(cursor) == 0:
                    cursor.move(x=direc)
                cursor.reset(x=True)
        updated_chunk = cursor.updated_chunk
        # 灯を残した地点から追加処理を行う
        for pos, light_level in cursor.light_lavel:
            updated_chunk.update(self._add_light(pos, light_level))
        return updated_chunk

    def _remove_column_x(self, cursor):
        # Z=0 の灯を削除する
        light_level = self._remove_column_xz(cursor)
        if light_level == 0:
            # Z<0 と Z>0 の灯を削除する
            for direc in (-1, 1):
                cursor.move(z=direc)
                while self._remove_column_xz(cursor) == 0:
                    cursor.move(z=direc)
                cursor.reset(z=True)
        return light_level
    
    def _remove_column_xz(self, cursor):
        # Y=0 の灯を削除する
        light_level = self._remove_point(cursor)
        if light_level == 0:
            # Y<0 と Y>0 の灯を削除する
            for direc in (-1, 1):
                cursor.move(y=direc)
                while self._remove_point(cursor) == 0:
                    cursor.move(y=direc)
                cursor.reset(y=True)
        return light_level
    
    def _remove_point(self, cursor):
        # 周辺で最も明るいレベルを求める
        max_light_level = 0
        for pos, chunk in cursor.surrounding():
            l = chunk.get_block_light(*pos.in_chunk)
            if l > max_light_level:
                max_light_level = l
        # 灯をなくす
        pos, chunk = cursor.current()
        x, z, y = pos.in_chunk
        l = chunk.get_block_light(x, z, y)
        chunk.set_block_light(x, z, y, 0)
        # 現在地が周囲よりも暗ければ灯をなくす処理を終える
        if l < max_light_level:
            cursor.save_light(l)
            return l
        # 周囲に灯があれば処理は継続する
        if max_light_level != 0:
            cursor.mark_updated(chunk.pos)
            return 0
        # 周囲に灯がなければ処理は終了する
        else:
            return -1
