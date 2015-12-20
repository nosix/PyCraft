# -*- coding: utf8 -*-

from ..block import BlockID, new_block
from .base import Biome
from .ids import ID


class GrassyBiome(Biome):
    
    COVER_BLOCKS = (
        new_block(BlockID.GRASS),
        new_block(BlockID.DIRT),
        new_block(BlockID.DIRT),
        new_block(BlockID.DIRT),
        new_block(BlockID.DIRT))


class SandyBiome(Biome):
    
    COVER_BLOCKS = (
        new_block(BlockID.SAND),
        new_block(BlockID.SAND),
        new_block(BlockID.SANDSTONE),
        new_block(BlockID.SANDSTONE),
        new_block(BlockID.SANDSTONE))


class SnowyBiome(Biome):

    COVER_BLOCKS = (
        new_block(BlockID.SNOW),
        new_block(BlockID.GRASS),
        new_block(BlockID.DIRT),
        new_block(BlockID.DIRT),
        new_block(BlockID.DIRT))


class Ocean(GrassyBiome):
    
    id = ID.OCEAN
    
    MIN_ELEVATION = 46
    MAX_ELEVATION = 58


class Plains(GrassyBiome):
    
    id = ID.PLAINS

    MIN_ELEVATION = 63
    MAX_ELEVATION = 74
    TEMPERATURE = 0.8
    RAINFALL = 0.4


class Desert(SandyBiome):
    
    id = ID.DESERT
    
    MIN_ELEVATION = 63
    MAX_ELEVATION = 74
    TEMPERATURE = 1.0
    RAINFALL = 0.0


class Mountains(GrassyBiome):
    
    id = ID.MOUNTAINS
    
    MIN_ELEVATION = 63
    MAX_ELEVATION = 127
    TEMPERATURE = 0.4
    

class Forest(GrassyBiome):
    
    id = ID.FOREST
    
    MIN_ELEVATION = 63
    MAX_ELEVATION = 81
    TEMPERATURE = 0.7
    RAINFALL = 0.8


class Taiga(SnowyBiome):
    
    id = ID.TAIGA
    
    MIN_ELEVATION = 63
    MAX_ELEVATION = 81
    TEMPERATURE = 0.05
    RAINFALL = 0.8


class Swanp(GrassyBiome):
    
    id = ID.SWAMP

    color = property(lambda self: 0x6A7039)    

    MIN_ELEVATION = 62
    MAX_ELEVATION = 63
    TEMPERATURE = 0.8
    RAINFALL = 0.9


class River(GrassyBiome):
    
    id = ID.RIVER
    
    MIN_ELEVATION = 58
    MAX_ELEVATION = 62
    RAINFALL = 0.7


class IcePlains(SnowyBiome):
    
    id = ID.ICE_PLAINS
    
    MIN_ELEVATION = 63
    MAX_ELEVATION = 74
    TEMPERATURE = 0.05
    RAINFALL = 0.8


class SmallMountains(Mountains):
    
    id = ID.SMALL_MOUNTAINS
    
    MIN_ELEVATION = 63
    MAX_ELEVATION = 97


class BirchForest(Forest):
    
    id = ID.BIRCH_FOREST
