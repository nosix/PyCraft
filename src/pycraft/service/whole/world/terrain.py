# -*- coding: utf8 -*-

from pycraft.common import PriorityQueue
from pycraft.service import config
from pycraft.service.const import LevelEventID
from pycraft.service.primitive.geometry import Face, Position
from pycraft.service.primitive.values import BlockRecord
from pycraft.service.primitive.fuzzy import Random
from pycraft.service.part.block import BlockID, new_block
from pycraft.service.part.item import new_item
from pycraft.service.composite.chunk import ChunkFactory
from ..handler import TaskID
from .tile import BlockEntityWorld
from .light import BlockLight


class Terrain:
    
    PRIORITY_THRESHOLD = 4

    AIR_BLOCK = new_block(BlockID.AIR, 0)

    def __init__(self, components, chunk_map, seed):
        self.map = chunk_map
        self._is_over = components.scheduler.is_over
        self._datastore = components.datastore
        self._listener = components.listener
        self._factory = ChunkFactory(Random(seed))
        # 全てのBlockEntityを保存
        self._block_entity = BlockEntityWorld(components)
        # 灯の処理を行う
        self._block_light = BlockLight(self)
        # ChunkPosition -> Chunk
        self._cache = {}
        # 削除されたキャッシュ、永続化されるまで保持する
        self._cache_garbage = []
        # キャッシュサイズ
        self._max_chunk_num = \
            Position.CHUNK_AREA.CHUNK_NUM * config.max_player_num
        # task: ChunkPosition
        self._load_queue = PriorityQueue()
        # 保存する順番でcacheのkeyを持つ
        self._store_queue = []
        # 更新されたChunk(ChunkPosition)
        self._updated_chunk = set()
        # 更新された場所とカウントダウンの数値を持つ
        self._updated_block_queue = []

    block_entity = property(lambda self: self._block_entity)
    updated_chunk = property(lambda self: self._updated_chunk)

    def get_chunk(self, chunk_pos):
        return self._cache.get(chunk_pos)

    def get_block(self, pos):
        chunk = self._cache.get(pos.chunk_pos)
        if chunk != None:
            return chunk.get_block(*pos.in_chunk)
        else:
            return None

    def is_transparent(self, pos):
        chunk = self._cache[pos.chunk_pos]
        return chunk.is_transparent(*pos.in_chunk.astype(int))

    def can_see(self, pos, eye_pos):
        for p in eye_pos.on_lay(pos):
            if not self.is_transparent(p):
                return False
        return True

    def get_ground_pos(self, pos, is_transparent=True, to_bottom=False):
        """指定した位置の地表を返す
        
        pos : Position
        is_transparent :
            True ならば通過できるブロックの座標を返す
            False ならば通過できないブロックの座標を返す
        to_bottom:
            True ならば空洞を下へ探す
            False ならば空洞を上へ探す
        """
        chunk_pos = pos.chunk_pos
        chunk = self.get_chunk(chunk_pos)
        if chunk != None:
            pos_in_chunk = pos.in_chunk
            y = chunk.get_ground_y(
                pos_in_chunk.x, pos_in_chunk.z, pos_in_chunk.y, to_bottom)
            if is_transparent:
                y += 1
            return Position(pos.x, pos.z, y)
        else:
            return None

    def start(self):
        self._factory.start()
        self._block_entity.load()

    def terminate(self):
        self._factory.terminate()
        while self._store():
            pass

    def update(self):
        self._process_updated_block()
        self._update_block_entity()
        self._block_light.update()
        if not self._load_queue.empty(self.PRIORITY_THRESHOLD):
            self._next_load()
        if not self._load_queue.empty() and \
                not self._is_over(TaskID.UPDATE_TERRAIN):
            self._next_load()

    def store(self):
        if not self._is_over(TaskID.STORE_BLOCK_ENTITY):
            self._block_entity.store()
        if not self._is_over(TaskID.STORE_TERRAIN):
            self._store()
        
    def _next_load(self):
        priority, chunk_pos = self._load_queue.get()
        if not self._load(chunk_pos):
            self._load_queue.put(priority, chunk_pos)

    def _load(self, chunk_pos):
        """ChunkPositionのChunkを読み込む、もしくは生成する"""
        chunk = self.get_chunk(chunk_pos)
        if chunk == None:
            # キャッシュに保存されていない場合
            if self.map.num_of_chunk == self._max_chunk_num:
                # 保存できる上限に達したら不要な Chunk を一つ破棄する
                garbage_chunk_pos = self.map.pop()
                if garbage_chunk_pos in self._store_queue:
                    self._store_queue.remove(garbage_chunk_pos)
                    self._cache_garbage.append(self._cache[garbage_chunk_pos])
                del self._cache[garbage_chunk_pos]
            # DataStoreを読み込む
            chunk = self._datastore.load_chunk(chunk_pos)
            if chunk == None:
                # Chunkを生成する
                chunk = self._factory.create(chunk_pos)
                if chunk == None:
                    return False
            self._cache[chunk_pos] = chunk
            self.map.append(chunk_pos)
            self._mark_updated(chunk_pos)
        # Chunk読み込み完了を通知する
        block_entities = self._block_entity.find_in_chunk(chunk.pos)
        self._listener.full_chunk_loaded(chunk, block_entities)
        return True

    def _mark_updated(self, chunk_pos):
        """キャッシュが更新されたことを記録する"""
        self._updated_chunk.add(chunk_pos)
        if chunk_pos not in self._store_queue:
            self._store_queue.append(chunk_pos)

    def clear_updated(self):
        self._updated_chunk.clear()

    def load(self, chunk_place):
        """ChunkPlacementのChunkを読み込む、もしくは生成する"""
        self._load_queue.put(*chunk_place)

    def _store(self):
        """地形データを1件保存する"""
        if len(self._cache_garbage) > 0:
            chunk = self._cache_garbage.pop(0)
            self._datastore.store_terrain(chunk)
            return True
        if len(self._store_queue) > 0:
            chunk_pos = self._store_queue.pop(0)
            self._datastore.store_terrain(self._cache[chunk_pos])
            return True
        return False

    def _update_block_entity(self):
        # かまどの火を設定する
        def update_blocks(pos_list, block_id):
            for pos in pos_list:
                block = self.get_block(pos)
                block = new_block(block_id, block.attr)
                yield self._update_block(pos, block)
        # 更新前の状態を保存
        burning_furnace = set(self._block_entity.burning_furnace)
        # 更新
        self._block_entity.update()
        # 更新前と変化があった場所を更新
        records = []
        records.extend(update_blocks(
            self._block_entity.burning_furnace - burning_furnace,
            BlockID.BURNING_FURNACE))
        records.extend(update_blocks(
            burning_furnace - self._block_entity.burning_furnace,
            BlockID.FURNACE))
        if len(records) > 0:
            self._listener.block_updated(records)

    def _process_updated_block(self):
        def process():
            for pos, count in self._updated_block_queue:
                if count > 0:
                    # カウントが残っている場合は処理しない
                    yield (pos, count-1)
                else:
                    self._fall_block(pos)
        self._updated_block_queue = [t for t in process()]

    def _fall_block(self, pos):
        """Blockの落下処理を行う"""
        chunk = self.get_chunk(pos.chunk_pos)
        x, z, y = pos.in_chunk
        if chunk.get_block_id(x, z, y-1) != BlockID.AIR:
            return  # ひとつ下がAIRでなければ落下しない
        # 上方向にAIRではない地点を探す
        while y <= chunk.TOP_Y:
            if chunk.get_block_id(x, z, y) == BlockID.AIR:
                y += 1
            else:
                break
        else:
            return  # AIRではない地点がなければ落下しない
        def update_block(y, block):
            chunk.set_block_id(x, z, y, block.id)
            chunk.set_block_data(x, z, y, block.attr)
            return BlockRecord(
                pos.x, pos.z, y, block.id, block.attr,
                is_neighbors=True, is_network=True)
        def fall():
            # 落下するブロックを移動する
            yy = y
            while yy <= chunk.TOP_Y:
                block = chunk.get_block(x, z, yy)
                if not block.is_fallable():
                    break
                yield update_block(yy-1, block)
                yy += 1
            if yy != y:
                yield update_block(yy-1, self.AIR_BLOCK)
        # 更新を行う
        updated_blocks = [b for b in fall()]
        if len(updated_blocks) > 0:
            self._mark_updated(chunk.pos)
            self._listener.block_updated(updated_blocks)
            bottom = updated_blocks[0]
            self._updated_block_queue.append(
                (Position(bottom.x, bottom.z, bottom.y), 0))
        
    def _update_block(self, pos, block):
        pos_in_chunk = pos.in_chunk
        chunk = self._cache[pos.chunk_pos]
        chunk.set_block(pos_in_chunk.x, pos_in_chunk.z, pos_in_chunk.y, block)
        self._mark_updated(chunk.pos)
        return BlockRecord(
            pos.x, pos.z, pos.y, block.id, block.attr,
            is_neighbors=True, is_network=True, is_priority=True)

    def remove_block(self, pos, player_pos):
        block = self.get_block(pos)
        if block.id == BlockID.AIR:
            return []
        # BlockからItemに変換
        item_id = block.to_item()
        spawn_items = [new_item(item_id)] if item_id != None else []
        # 削除したBlockをAIRに変更
        records = [self._update_block(pos, self.AIR_BLOCK)]
        # 特別な削除処理
        block_entities = []
        func = block.get_remove_func(self)
        if func != None:
            pos = func(block, pos, records, block_entities, spawn_items)
        # 通知を行う
        if len(records) > 0:
            self._listener.block_updated(records)
        if len(block_entities) > 0:
            self._listener.block_entity_updated(block_entities)
        # 上のブロックの落下処理を行う
        self._updated_block_queue.append((pos+(0,0,1), 1))
        # 灯の処理を行う
        self._block_light.remove(pos)
        return spawn_items

    def _remove_chest(self, block, pos, records, block_entities, spawn_items):
        self._listener.container_broken(
            self._block_entity.find(pos).window_id)
        entities, items = self._block_entity.remove_chest(pos)
        spawn_items.extend(items)
        block_entities.extend(entities)
        return pos
    
    def _remove_furnace(self, block, pos, records, block_entities, spawn_items):
        self._listener.container_broken(
            self._block_entity.find(pos).window_id)
        items = self._block_entity.remove_furnace(pos)
        spawn_items.extend(items)
        return pos
    
    def _remove_sign(self, block, pos, records, block_entities, spawn_items):
        self._block_entity.remove_sign(pos)
        return pos

    def _remove_door(self, block, pos, records, block_entities, spawn_items):
        if block.is_upside():
            records.append(self._update_block(pos-(0,0,1), self.AIR_BLOCK))
            return pos
        else:
            pos += (0,0,1)  # 落下処理の基準は上のブロック
            records.append(self._update_block(pos, self.AIR_BLOCK))
            return pos

    def touch_block(self, player, pos):
        block = self.get_block(pos)
        func = block.get_touch_func(self)
        if func != None:
            func(player, pos)
            return False
        else:
            return block.can_attach()

    def _open_container(self, player, pos):
        """コンテナを開く"""
        self._block_entity.open_container(player, pos)

    def _open_door(self, player, pos):
        """ドアを開く"""
        block = self.get_block(pos)
        if block.is_upside():
            pos -= (0,0,1)
            block = self.get_block(pos)
        block = new_block(block.id, switch_attr=block.attr)
        records = [self._update_block(pos, block)]
        self._listener.block_updated(records)
        self._listener.sounded(LevelEventID.DOOR_SOUND, pos, 0)

    def add_block(self, pos, block):
        curr_block = self.get_block(pos)
        if curr_block.id != BlockID.AIR:
            return
        records = [self._update_block(pos, block)]
        block_entities = []
        func = block.get_add_func(self)
        if func != None:
            func(block, pos, records, block_entities)
        if len(records) > 0:
            self._listener.block_updated(records)
        if len(block_entities) > 0:
            self._listener.block_entity_updated(block_entities)
        # 落下処理を行う
        if pos.y > 0:
            self._updated_block_queue.append((pos, 1))
        # 灯の処理を行う
        self._block_light.add(pos)

    def _add_chest(self, block, pos, records, block_entities):
        entities = self._block_entity.add_chest(pos)
        block_entities.extend(entities)
        if len(entities) > 1:
            chest_records = self._update_chest_block(entities)
            if chest_records != None:
                records.clear()
                records.extend(chest_records)

    def _update_chest_block(self, block_entities):
        def get_face(p1, p2):
            direc = p1.direc(p2)
            for i, d in enumerate(Face.DIRECTION):
                # X(Z)方向に並んでいるならZ(X)方向を向く
                if direc.x == d.z and direc.z == d.x:
                    return i
        def is_same_direc(blocks, face):
            face_direc = Face.DIRECTION[face].astype(abs)
            for b in blocks:
                direc = Face.DIRECTION[b.attr].astype(abs)
                if direc != face_direc:
                    return False
            return True
        def update(face, pos_pair):
            block = new_block(BlockID.CHEST, face)
            for pos in pos_pair:
                yield self._update_block(pos, block)
        # 向きが異なるなら、向きを揃える
        pos_pair = tuple(e.pos for e in block_entities)
        blocks = list(self.get_block(p) for p in pos_pair)
        face = get_face(*pos_pair)
        if not is_same_direc(blocks, face):
            return list(update(face, pos_pair))

    def _add_furnace(self, block, pos, records, block_entities):
        self._block_entity.add_furnace(pos)
    
    def _add_sign(self, block, pos, records, block_entities):
        block_entities.append(self._block_entity.add_sign(pos))

    def _add_door(self, block, pos, records, block_entities):
        left_pos = pos + block.left_side()
        left_block = self.get_block(left_pos)
        leftup_pos = left_pos + (0,0,1)
        leftup_block = self.get_block(leftup_pos)
        is_double = (left_block.id == block.id and 
                     left_block.direc() == block.direc() and
                     not leftup_block.is_double())
        up_block = new_block(block.id, is_double=is_double)
        records.append(self._update_block(pos + (0,0,1), up_block))
