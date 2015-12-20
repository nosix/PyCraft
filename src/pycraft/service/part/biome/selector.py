# -*- coding: utf8 -*-

from pycraft.common.util import ndarray, product
from pycraft.service.primitive.fuzzy import Simplex
from .ids import ID
from .instance import biomes


class BiomeSelector:
    
    __slots__ = [
        '_temperature_factory',
        '_rainfall_factory',
        '_biome_id_map',
        ]

    SAMPLE = 64

    def __init__(self, random):
        """Biome の地図を作成して初期化する
        
        random : Random (初期化時にのみ使用される)
        """
        self._temperature_factory = Simplex(random, 2, 1.0/16, 1.0/512)
        self._rainfall_factory = Simplex(random, 2, 1.0/16, 1.0/512)
        # 気温と雨量に応じてBiomeを決定する
        self._biome_id_map = ndarray(self.SAMPLE, self.SAMPLE)
        max_sample = self.SAMPLE - 1
        for t, r in product(range(self.SAMPLE), range(self.SAMPLE)):
            self._biome_id_map[t][r] = self._lookup(t/max_sample, r/max_sample)
    
    def _lookup(self, temperature, rainfall):
        if rainfall < 0.05:
            return ID.MOUNTAINS
        if rainfall < 0.15:
            return ID.SMALL_MOUNTAINS
        if rainfall < 0.5:
            if temperature < 0.25:
                return ID.ICE_PLAINS
            if temperature < 0.75:
                return ID.PLAINS
            else:
                return ID.DESERT
        if rainfall < 0.7:
            if temperature < 0.25:
                return ID.TAIGA
            if temperature < 0.75:
                return ID.FOREST
            else:
                return ID.BIRCH_FOREST
        if rainfall < 0.75:
            return ID.RIVER
        else:
            return ID.OCEAN

    def pick_biome(self, pos):
        """位置から気温と雨量を割り出して該当する Biome を返す"""
        max_sample = self.SAMPLE - 1
        t = int(self._temperature(pos) * max_sample)
        r = int(self._rainfall(pos) * max_sample)
        return biomes[self._biome_id_map[t][r]]

    def _temperature(self, pos):
        """気温を0.0-1.0の範囲で返す"""
        return (self._temperature_factory.noise_2d(pos.x, pos.z) + 1.0) / 2
    
    def _rainfall(self, pos):
        """雨量を0.0-1.0の範囲で返す"""
        return (self._rainfall_factory.noise_2d(pos.x, pos.z) + 1.0) / 2
