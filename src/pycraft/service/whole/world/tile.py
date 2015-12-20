# -*- coding: utf8 -*-

from queue import Queue
from pycraft.service.part.tile import Chest, Furnace, Sign
from pycraft.service.composite.container import \
    ChestContainer, FurnaceContainer


class BlockEntityWorld:

    MIN_WINDOW_ID = 3

    def __init__(self, components):
        self._datastore = components.datastore
        self._listener = components.listener
        # pos:Position -> BlockEntity
        self._chest = {}
        self._furnace = {}
        self._sign = {}
        self._maps = [self._chest, self._furnace, self._sign]
        # 次にChestContainerを追加したときに使うwindow_id
        self._min_window_id = self.MIN_WINDOW_ID
        # window_id:int -> PlacedContainer
        self._container = {}
        # 燃えているFurnaceの位置
        self._burning_furnace = set()
        # 保存/削除待ち
        self._tran_queue = Queue()

    burning_furnace = property(lambda self: self._burning_furnace)

    def find(self, pos):
        for m in self._maps:
            e = m.get(pos)
            if e != None:
                return e
    
    def find_in_chunk(self, chunk_pos):
        return (e
            for m in self._maps
                for e in m.values() if e.pos.chunk_pos == chunk_pos)
    
    def load(self):
        self._chest.update((c.pos, c)
            for c in self._datastore.load_chest())
        self._furnace.update((c.pos, c)
            for c in self._datastore.load_furnace())
        self._sign.update((c.pos, c)
            for c in self._datastore.load_sign())
        self._container.update((c.window_id, c)
            for c in self._datastore.load_container())
        self._init_window_id()
        for e in self._chest.values():
            c = self._container[e.window_id]
            c.bind(e.pos)
        for e in self._furnace.values():
            c = self._container[e.window_id]
            c.bind(e.pos)

    def update(self):
        for c in self._container.values():
            func = c.update_func(self)
            if func != None:
                func(c)
    
    def store(self):
        self._process_transaction()

    def _update_furnace(self, c):
        did_update, updated_slots = c.update()
        if len(updated_slots) == 0 and not c.is_burning():
            self._burning_furnace.difference_update(c.pos)
        else:
            for slot in updated_slots:
                self._tran_queue.put_nowait((self._store_container, c))
                self._listener.container_changed(
                    c.opened_by, c.window_id, slot, c[slot])
            if did_update:
                self._listener.furnace_burning(
                    c.opened_by, c.window_id, c.prop)
            self._burning_furnace.update(c.pos)

    def _process_transaction(self):
        if not self._tran_queue.empty():
            method, target = self._tran_queue.get_nowait()
            method(target)

    def _store_container(self, c):
        if len(c) == 0:
            del self._container[c.window_id]
        self._datastore.store_container(c)

    def _init_window_id(self):
        while self._min_window_id in self._container:
            self._min_window_id += 1
        
    def _next_window_id(self):
        window_id = self._min_window_id
        self._min_window_id += 1
        while self._min_window_id in self._container:
            self._min_window_id += 1
        return window_id

    def _free_window_id(self, window_id):
        if window_id < self._min_window_id:
            self._min_window_id = window_id

    def _add_container(self, container):
        self._container[container.window_id] = container

    def _find_next_small_chest(self, pos):
        for c in self._chest.values():
            if c.is_next(pos) and not self._container[c.window_id].is_large():
                return c

    def add_chest(self, pos):
        # ChestContainerを作るか、隣接するChestがあるならば拡張する
        base_chest = self._find_next_small_chest(pos)
        if base_chest != None:
            container = self._container[base_chest.window_id]
            container.extend()
        else:
            container = ChestContainer(self._next_window_id())
            self._add_container(container)
        container.bind(pos)

        chest = Chest(pos, container.window_id)
        if base_chest != None:
            chest.set_pair(base_chest.pos)
            base_chest.set_pair(chest.pos)
        self._chest[chest.pos] = chest

        self._tran_queue.put_nowait((self._store_container, container))
        self._tran_queue.put_nowait((self._datastore.store_chest, chest))
        chests = (chest, base_chest) if base_chest != None else (chest, )
        return chests

    def remove_chest(self, pos):
        chest = self._chest.pop(pos)
        # 結合されたチェストを解除する
        if chest.pair_pos != None:
            pair_chest = self._chest[chest.pair_pos]
            chest.clear_pair()
            pair_chest.clear_pair()
        else:
            pair_chest = None
        # コンテナを縮小し、位置との関連づけを削除する
        container = self._container[chest.window_id]
        items = container.reduce()
        container.unbind(pos)

        self._tran_queue.put_nowait((self._datastore.delete_chest, chest))
        self._tran_queue.put_nowait((self._store_container, container))
        chests = (chest, pair_chest) if pair_chest != None else (chest, )
        return chests, items
    
    def add_furnace(self, pos):
        # PlacedContainerを生成する
        container = FurnaceContainer(self._next_window_id())
        self._container[container.window_id] = container
        self._add_container(container)
        container.bind(pos)
        # BlockEntityを生成する
        furnace = Furnace(pos, container.window_id)
        self._furnace[furnace.pos] = furnace

        self._tran_queue.put_nowait((self._store_container, container))
        self._tran_queue.put_nowait((self._datastore.store_furnace, furnace))

    def remove_furnace(self, pos):
        furnace = self._furnace.pop(pos)
        # コンテナを縮小し、位置との関連づけを削除する
        container = self._container[furnace.window_id]
        items = container.reduce()
        container.unbind(pos)
        
        self._tran_queue.put_nowait((self._datastore.delete_furnace, furnace))
        self._tran_queue.put_nowait((self._store_container, container))
        return items

    def add_sign(self, pos):
        sign = Sign(pos)
        self._sign[sign.pos] = sign
        self._tran_queue.put_nowait((self._datastore.store_sign, sign))
        return sign

    def edit_sign(self, pos, named_tag):
        sign = self._sign[pos]
        sign.named_tag = named_tag
        self._listener.block_entity_updated([sign])
        self._tran_queue.put_nowait((self._datastore.store_sign, sign))
        return sign

    def remove_sign(self, pos):
        sign = self._sign.pop(pos)
        self._tran_queue.put_nowait((self._datastore.delete_sign, sign))

    def open_container(self, player, pos):
        block_entity = self.find(pos)
        container = self._container[block_entity.window_id]
        did_open = container.open(player.player_id)
        player.opening_container = container.window_id
        self._listener.container_opened(
            player.player_id, pos, container, did_open)

    def edit_container(self, window_id, slot, item):
        container = self._container[window_id]
        container[slot] = item
        self._tran_queue.put_nowait((self._store_container, container))
        self._listener.container_changed(
            container.opened_by, window_id, slot, container[slot])

    def close_container(self, window_id, player):
        container = self._container[window_id]
        did_close = container.close(player.player_id)
        player.opening_container = 0
        self._listener.container_closed(
            player.player_id, container.pos, window_id, did_close)
