# -*- coding: utf8 -*-

import os
import math
from multiprocessing import Process, Queue
from pycraft.common.util import product
from pycraft.service import logger
from pycraft.service.primitive.geometry import ChunkPosition
from pycraft.service.primitive.values import Color
from pycraft.service.primitive.fuzzy import \
    GaussianKernel, Simplex, Noise, Random
from pycraft.service.part.biome import BiomeSelector
from pycraft.service.part.block import BlockID
from .core import Chunk


class ChunkFactoryProcess:
    
    def __init__(self, create):
        self._create = create
        self._waiting = set()
        self._chunks = {}
        self._i_queue = Queue()
        self._o_queue = Queue()
        self._process = Process(
            target=self.run, args=(self._i_queue, self._o_queue))

    def create(self, chunk_pos):
        # 別Processで生成したChunkを受け取る
        while not self._o_queue.empty():
            x, z, data = self._o_queue.get()
            p = ChunkPosition(x, z)
            self._chunks[p] = Chunk(p, data)
            self._waiting.discard(p)
        # Chunkがあれば返し、なければ生成する
        chunk = self._chunks.get(chunk_pos)
        if chunk == None and chunk_pos not in self._waiting:
            self._waiting.add(chunk_pos)
            self._i_queue.put((chunk_pos.x, chunk_pos.z))
        return chunk
        
    def start(self):
        self._process.start()

    def terminate(self):
        if self._process.is_alive():
            self._process.terminate()
            self._process.join()
        logger.server.info('terminate {name}', name=self.__class__.__name__)
        
    def run(self, i_queue, o_queue):
        logger.server.info(
            'start {name}(pid={pid})',
            name=self.__class__.__name__, pid=os.getpid())
        while True:
            x, z = i_queue.get()
            chunk = self._create(ChunkPosition(x, z))
            o_queue.put((x, z, chunk.data))


class ChunkFactory(object):
    """Chunkを生成する役割を担う"""
    
    WATER_HEIGHT = 62
    SMOOTH_SIZE = 2

    def __init__(self, random):
        self._random = random
        self._gaussian = GaussianKernel(self.SMOOTH_SIZE)
        self._random.reset()
        self._noise_base = Simplex(self._random, 4, 1.0/4, 1.0/32)
        self._random.reset()
        self._selector = BiomeSelector(self._random)
        self._process = ChunkFactoryProcess(self.create)
        self.create = self._process.create
    
    def start(self):
        self._process.start()

    def terminate(self):
        self._process.terminate()

    def create(self, chunk_pos):
        chunk = Chunk(chunk_pos)
        noise = Noise(
            self._noise_base,
            chunk.SIZE.X, chunk.SIZE.Y, chunk.SIZE.Z,
            4, 8, 4,
            chunk_pos.o.x, chunk_pos.o.y, chunk_pos.o.z)
        biomes = dict(self._biomes(chunk))
        for x, z in chunk.each_xz_pos():
            pos = chunk_pos.pos(x, z)
            biome = biomes[pos]
            chunk.set_biome_id(x, z, biome.id)
            min_avg, c, h = self._smooth(pos, biomes)
            chunk.set_biome_color(x, z, c)
            for y in chunk.each_y_pos():
                chunk.set_sky_light(x, z, y, chunk.MAX_LIGHT_LEVEL)
                if y == 0:
                    chunk.set_block_id(x, z, y, BlockID.BEDROCK)
                elif noise.on(x, z, y) - 1.0 / h * (y - h - min_avg) > 0:
                    chunk.set_block_id(x, z, y, BlockID.STONE)
                elif y <= self.WATER_HEIGHT:
                    chunk.set_block_id(x, z, y, BlockID.STILL_WATER)
            self._cover_ground(chunk, x, z, biome)
        self._populate(chunk, biomes)
        return chunk

    def _biomes(self, chunk):
        """Chunkの領域の各(x,z,0)のBiomeを返す"""
        r = product(
            range(-self.SMOOTH_SIZE, chunk.SIZE.X+self.SMOOTH_SIZE+1),
            range(-self.SMOOTH_SIZE, chunk.SIZE.Z+self.SMOOTH_SIZE+1))
        for x, z in r:
            pos = chunk.pos.pos(x, z)
            yield (pos, self._pick_biome(pos))

    def _pick_biome(self, pos):
        hash_ = pos.x*2345803 ^ pos.z*9236449 ^ self._random.seed
        hash_ *= hash_ + 223
        # noise = -1, 0, 1 (0 は -1,1 よりも出現頻度が高い)
        x_noise = ((hash_ >> 20) & 3) - 1
        z_noise = ((hash_ >> 22) & 3) - 1
        if x_noise == 2:
            x_noise = 0
        if z_noise == 2:
            z_noise = 0
        return self._selector.pick_biome(pos + (x_noise, z_noise))

    def _smooth(self, pos, biomes):
        min_sum, max_sum = 0, 0
        c_sum = Color(0, 0, 0)
        weight_sum = 0.0
        r = product(
            range(-self.SMOOTH_SIZE, self.SMOOTH_SIZE+1),
            range(-self.SMOOTH_SIZE, self.SMOOTH_SIZE+1))
        for dx, dz in r:
            weight = self._gaussian.get(dx, dz)
            spos = pos + (dx, dz)
            adjacent_biome = biomes[spos]
            min_sum += (adjacent_biome.MIN_ELEVATION - 1) * weight
            max_sum += (adjacent_biome.MAX_ELEVATION) * weight
            c_sum += (adjacent_biome.color ** 2) * weight
            weight_sum += weight
        min_avg = min_sum/weight_sum
        max_avg = max_sum/weight_sum
        c_avg = c_sum.astype(lambda v: int(math.sqrt(v/weight_sum)))
        height = (max_avg - min_avg) / 2.0
        return min_avg, c_avg, height

    def _cover_ground(self, chunk, x, z, biome):
        cover_blocks = biome.COVER_BLOCKS
        if len(cover_blocks) == 0:
            return
        ground_y = chunk.get_ground_y(x, z)
        if not cover_blocks[0].is_solid() and ground_y != chunk.top:
            ground_y += 1
        dont_cover_y = ground_y - len(cover_blocks)
        if dont_cover_y < 0:
            dont_cover_y = -1
        for y in range(ground_y, dont_cover_y, -1):
            block = cover_blocks[ground_y - y]
            if (block.is_solid() and 
                    chunk.get_block_id(x, z, y) == BlockID.AIR):
                break
            chunk.set_block_id(x, z, y, block.id)
            chunk.set_block_data(x, z, y, block.attr)

    def _create_random(self, chunk):
        return Random(
            0xdeadbeef ^ (chunk.pos.x << 8) ^ chunk.pos.z ^ self._random.seed)

    def _populate(self, chunk, biomes):
        random = self._create_random(chunk)
        # 中央付近のBiomeのpopulatorを使用する
        x = random.next_range(0, chunk.SIZE.X//2-1) + chunk.SIZE.X//4
        z = random.next_range(0, chunk.SIZE.Z//2-1) + chunk.SIZE.Z//4
        biome = biomes[chunk.pos.pos(x, z)]
        for p in biome.populators:
            p.populate(chunk, random)