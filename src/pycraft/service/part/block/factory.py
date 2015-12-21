# -*- coding: utf8 -*-

from .base import MaterialBlock
from .ids import ID, NAMES
from . import defs


class BlockFactory:
    
    __slots__ = ['_blocks']

    def __init__(self):
        # Default is MaterialBlock.
        self._blocks = dict((id_, MaterialBlock) for id_ in NAMES.keys())
        # Special blocks
        self._blocks[ID.AIR] = defs.Air
        self._blocks[ID.STONE] = defs.Stone
        self._blocks[ID.GRASS] = defs.Grass
        self._blocks[ID.SAND] = defs.Sand
        self._blocks[ID.TORCH] = defs.Torch
        self._blocks[ID.CHEST] = defs.Chest
        self._blocks[ID.CRAFTING_TABLE] = defs.CraftingTable
        self._blocks[ID.FURNACE] = defs.Furnace
        self._blocks[ID.BURNING_FURNACE] = defs.Furnace
        self._blocks[ID.SIGN_POST] = defs.SignPost
        self._blocks[ID.WALL_SIGN] = defs.WallSign
        self._blocks[ID.WOODEN_DOOR] = defs.WoodenDoor
        self._blocks[ID.IRON_DOOR] = defs.IronDoor
        self._blocks[ID.SNOW] = defs.Snow
    
    def __call__(self, id_, attr=0, **kwargs):
        return self._blocks[id_](id_, attr, **kwargs)
    
    def cls(self, id_):
        return self._blocks[id_]


new_block = BlockFactory()
