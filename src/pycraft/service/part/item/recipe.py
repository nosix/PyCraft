# -*- coding: utf8 -*-

from .ids import ID
from .factory import new_item


class FurnaceRecipe:
    
    __slots__ = ['_smelt_factory', '_fuel_energy']

    @staticmethod
    def _gen(id_, attr=None):
        if attr == None:
            return lambda item: new_item(id_, attr=item.attr)
        else:
            return lambda item: new_item(id_, attr=attr)

    def __init__(self):
        self._smelt_factory = {
            ID.COBBLESTONE : self._gen(ID.STONE),
            ID.STONE_BRICK : self._gen(ID.STONE_BRICK, 2),
            ID.SAND : self._gen(ID.GLASS),
            ID.LOG : self._gen(ID.COAL, 1),
            ID.GOLD_ORE : self._gen(ID.GOLD_INGOT),
            ID.IRON_ORE : self._gen(ID.IRON_INGOT),
            ID.EMERALD_ORE : self._gen(ID.EMERALD),
            ID.DIAMOND_ORE : self._gen(ID.DIAMOND),
            ID.NETHERRACK : self._gen(ID.NETHER_BRICK),
            ID.RAW_PORKCHOP : self._gen(ID.COOKED_PORKCHOP),
            ID.CLAY : self._gen(ID.BRICK),
            ID.RAW_FISH : self._gen(ID.COOKED_FISH),
            ID.CACTUS : self._gen(ID.DYE, 2),
            ID.RED_MUSHROOM : self._gen(ID.DYE, 1),
            ID.RAW_BEEF : self._gen(ID.STEAK),
            ID.RAW_CHICKEN : self._gen(ID.COOKED_CHICKEN),
            ID.POTATOES : self._gen(ID.BAKED_POTATOES),
            ID.CLAY_BLOCK : self._gen(ID.HARDENED_CLAY),
            }
        self._fuel_energy = {
            ID.COAL : 1600,
            ID.COAL_BLOCK : 16000,
            ID.LOG : 300,
            ID.PLANKS : 300,
            ID.SAPLING : 100,
            ID.WOODEN_AXE : 200,
            ID.WOODEN_PICKAXE : 200,
            ID.WOODEN_SWORD : 200,
            ID.WOODEN_SHOVEL : 200,
            ID.WOODEN_HOE : 200,
            ID.STICKS : 100,
            ID.FENCE : 300,
            ID.FENCE_GATE : 300,
            ID.FENCE_GATE_SPRUCE : 300,
            ID.FENCE_GATE_BIRCH : 300,
            ID.FENCE_GATE_JUNGLE : 300,
            ID.FENCE_GATE_ACACIA : 300,
            ID.FENCE_GATE_DARK_OAK : 300,
            ID.OAK_STAIRS : 300,
            ID.SPRUCE_WOODEN_STAIRS : 300,
            ID.BIRCH_WOODEN_STAIRS : 300,
            ID.JUNGLE_WOODEN_STAIRS : 300,
            ID.TRAPDOOR : 300,
            ID.CRAFTING_TABLE : 300,
            ID.BOOKSHELF : 300,
            ID.CHEST : 300,
            ID.BUCKET : 20000,
            }
    
    def smelt(self, item):
        """Itemを精錬して得られるItemを返す"""
        return self._smelt_factory[item.id](item)
    
    def burn(self, item):
        """Itemを燃料として燃やして得られるエネルギー量を返す"""
        assert item.id != ID.BUCKET or item.attr == 10
        return self._fuel_energy[item.id]


furnace_recipe = FurnaceRecipe()