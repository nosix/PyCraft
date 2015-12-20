# -*- coding: utf8 -*-

from pycraft.service.part.block import BlockID
from ..chunk import ChunkTransaction
from .base import Structure


class Tree(Structure):

    __slots__ = ['_sapling']

    OVERRIDABLE = {
        BlockID.AIR,
        BlockID.SAPLING,
        BlockID.LOG,
        BlockID.LEAVES,
        BlockID.SNOW,
        BlockID.LEAVES2,
        BlockID.LOG2,
        }
    
    TRUNK_HEIGHT = 7
    LEAVES_BOTTOM = TRUNK_HEIGHT - 2
    TREE_HEIGHT = TRUNK_HEIGHT + 1
    
    TRUNK_BLOCK = BlockID.LOG
    LEAF_BLOCK = BlockID.LEAVES

    def __init__(self, sapling):
        self._sapling = sapling
        
    def place(self, chunk, x, z, y, random):
        tran = ChunkTransaction(chunk)
        if not self._place_trunk(tran, x, z, y, random):
            return
        if not self._place_leaves(tran, x, z, y, random):
            return
        tran.commit()

    def _place_trunk(self, tran, x, z, y, random):
        tran.set_block_id(x, z, y-1, BlockID.DIRT)
        for yy in range(y, y+self.TRUNK_HEIGHT):
            if not tran.in_range(x, z, yy):
                return False
            bid = tran.get_block_id(x, z, yy)
            if bid not in self.OVERRIDABLE:
                return False
            tran.set_block_id(x, z, yy, self.TRUNK_BLOCK)
            tran.set_block_data(x, z, yy, self._sapling)
        return True

    def _place_leaves(self, tran, x, z, y, random):
        height = self.TREE_HEIGHT - self.LEAVES_BOTTOM
        for h in range(height+1):
            radius = 1 + (height - h) // 2
            yy = y + self.LEAVES_BOTTOM + h
            is_top = (h == height)
            for xx in range(x-radius, x+radius+1):
                is_edge = (abs(xx - x) == radius)
                for zz in range(z-radius, z+radius+1):
                    is_edge |= (abs(zz - z) == radius)
                    if is_edge and (is_top or random.next_int() % 3 == 0):
                        continue
                    if not tran.in_range(xx, zz, yy):
                        return False
                    block = tran.get_block(xx, zz, yy)
                    if not block.is_solid():
                        tran.set_block_id(xx, zz, yy, self.LEAF_BLOCK)
                        tran.set_block_data(xx, zz, yy, self._sapling)
        return True
