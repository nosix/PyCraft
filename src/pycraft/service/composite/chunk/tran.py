# -*- coding: utf8 -*-

from operator import attrgetter
from pycraft.service.part.block import new_block


class ChunkTransaction:
    
    __slots__ = [
        '_chunk', '_update_block_id', '_update_block_data', '_has_error']

    def __init__(self, chunk):
        self._chunk = chunk
        self._update_block_id = {}
        self._update_block_data = {}
        self._has_error = False
    
    chunk = property(attrgetter('_chunk'))

    def get_block(self, x, z, y):
        return new_block(
            self.get_block_id(x, z, y),
            self.get_block_data(x, z, y))

    def in_range(self, x, z, y):
        return (0 <= x < self._chunk.SIZE.X and
                    0 <= z < self._chunk.SIZE.Z and
                    0 <= y < self._chunk.SIZE.Y)

    def set_block_id(self, x, z, y, block_id):
        if self.in_range(x, z, y):
            self._update_block_id[(x, z, y)] = block_id
        else:
            self._has_error = True

    def get_block_id(self, x, z, y):
        pos = (x, z, y)
        if pos in self._update_block_id:
            return self._update_block_id[pos]
        else:
            return self._chunk.get_block_id(x, z, y)

    def set_block_data(self, x, z, y, attr):
        if self.in_range(x, z, y):
            self._update_block_data[(x, z, y)] = attr
        else:
            self._has_error = True

    def get_block_data(self, x, z, y):
        pos = (x, z, y)
        if pos in self._update_block_data:
            return self._update_block_data[pos]
        else:
            return self._chunk.get_block_data(x, z, y)

    def commit(self):
        if self._has_error:
            return
        for pos, value in self._update_block_id.items():
            self._chunk.set_block_id(pos.x, pos.z, pos.y, value)
        for pos, value in self._update_block_data.items():
            self._chunk.set_block_data(pos.x, pos.z, pos.y, value)
