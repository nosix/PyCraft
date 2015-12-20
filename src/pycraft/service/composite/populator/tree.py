# -*- coding: utf8 -*-

from pycraft.service.part.block import BlockID


class TreePopulator:
    
    __slots__ = ['_tree', '_base_amount']

    def __init__(self, tree, base_amount):
        self._tree = tree
        self._base_amount = base_amount

    def populate(self, chunk, random):
        amount = random.next_range(0, 1) + self._base_amount
        for _ in range(amount):
            x = random.next_range(0, chunk.SIZE.X-1)
            z = random.next_range(0, chunk.SIZE.Z-1)
            y = self._heighest_workable_block(chunk, x, z)
            if y != None:
                self._tree.place(chunk, x, z, y, random)
    
    def _heighest_workable_block(self, chunk, x, z):
        column = chunk.get_block_id_column(x, z)
        for y in chunk.each_y_pos():
            bid = column[y]
            if bid == BlockID.DIRT or bid == BlockID.GRASS:
                return y + 1
            if bid != BlockID.AIR and bid != BlockID.SNOW:
                return None
        return 1
