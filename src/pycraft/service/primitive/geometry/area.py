# -*- coding: utf8 -*-

from pycraft.common import ImmutableMeta


class ChunkPlacement(metaclass=ImmutableMeta):
    """Chunk の設置に用いる情報を持つ"""
    
    properties = 'priority chunk_pos'


class SpiralChunkAreaMeta(type):
    
    def __new__(cls, cls_name, bases, attrs):
        attrs['CHUNK_NUM'] = cls.chunk_num(attrs['_MAX_SIDE_LEN'])
        return type.__new__(cls, cls_name, tuple(bases), attrs)

    @staticmethod
    def chunk_num(n):
        return 2*n + SpiralChunkAreaMeta.chunk_num(n-1) if n > 0 else 1


class SpiralChunkArea(metaclass=SpiralChunkAreaMeta):
    """Player 周辺の Chunk 領域を渦巻き状にする
    
    Example:
        center = (8,8)
        return =
            priority -> pos
            0 -> (8,8)
            1 -> (9,8), (9,9)
            2 -> (8,9),(7,9), (7,8),(7,7)
            3 -> (8,7),(9,7),(10,7), (10,8),(10,9),(10,10)
            4 -> (9,10),(8,10),(7,10),(6,10), (6,9),(6,8),(6,7),(6,6)
    Law:
        p : current position
        0 -> p
        1 -> p+(1,0), p+(0,1)
        2 -> p+(-1,0),p+(-1,0), p+(0,-1),p+(0,-1)
        3 -> p+(1,0),p+(1,0),p+(1,0), p+(0,1),p+(0,1),p+(0,1)
        4 -> p+(-1,0),p+(-1,0),p+(-1,0),p+(-1,0),
             p+(0,-1),p+(0,-1),p+(0,-1),p+(0,-1)
        l : length (priority)
        s : sign
            +1 if l is odd
            -1 if l is even
    """
  
    _MAX_SIDE_LEN = 13

    CHUNK_NUM = -1  # metaclass で計算
    PRIORITY_NUM = _MAX_SIDE_LEN

    @staticmethod
    def _generate(p, max_priority):
        yield ChunkPlacement(0, p)
        for l in range(1, max_priority+1):
            s = 2 * (l & 1) - 1
            for _ in range(l):
                p += (s, 0)
                yield ChunkPlacement(l, p)
            for _ in range(l):
                p += (0, s)
                yield ChunkPlacement(l, p)

    def surrounding_chunk(self, center, max_priority=None):
        """ChunkPosition 周辺領域の ChunkPlacement を返す"""
        if max_priority == None or max_priority > self.PRIORITY_NUM:
            max_priority = self.PRIORITY_NUM
        return self._generate(center, max_priority)

    def to_priority(self, distance):
        return distance * 2
