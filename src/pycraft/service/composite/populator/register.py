# -*- coding: utf8 -*-

from pycraft.service.part.biome import BiomeID, biomes
from pycraft.service.part.block import SaplingType
from ..structure import Tree
from .tree import TreePopulator


static_defs = {
    BiomeID.FOREST : TreePopulator(Tree(SaplingType.OAK), 5),
    BiomeID.BIRCH_FOREST : TreePopulator(Tree(SaplingType.BIRCH), 5),
    BiomeID.TAIGA : TreePopulator(Tree(SaplingType.SPRUCE), 10),
    }


def regist():
    for biome_id, populator in static_defs.items():
        biomes.regist_populator(biome_id, populator)