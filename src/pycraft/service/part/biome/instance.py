# -*- coding: utf8 -*-

from functools import partial
from pycraft.common import filter_classes
from .base import Biome
from . import defs


biome_classes = partial(
    filter_classes,
    lambda cls: issubclass(cls, Biome),
    lambda cls: cls.id)


class BiomePool:
    
    __slots__ = ['_instances']

    def __init__(self):
        self._instances = dict(
            (id_, cls()) for id_, cls in biome_classes(defs))

    def __getitem__(self, biome_id):
        return self._instances[biome_id]

    def regist_populator(self, biome_id, populator):
        self._instances[biome_id].regist_populator(populator)


biomes = BiomePool()