# -*- coding: utf8 -*-

import sqlite3
from pycraft.service import logger
from .dao import ChunkDAO, SignDAO, \
    PlayerDAO, SlotDAO, HotbarDAO, ArmorSlotDAO, \
    ChestDAO, FurnaceDAO, ContainerDAO, ContainerSlotDAO


class DataStore:
    
    __slots__ = ['_database', '_conn']

    def __init__(self, database):
        self._database = database
        self._conn = None
    
    def start(self):
        self._conn = sqlite3.connect(self._database)
        self._conn.text_factory = bytes
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")

    def terminate(self):
        self._conn.close()
        
    def create_table(self):
        with self._conn:
            ChunkDAO().create(self._conn)
            PlayerDAO().create(self._conn)
            SlotDAO().create(self._conn)
            HotbarDAO().create(self._conn)
            ArmorSlotDAO().create(self._conn)
            ChestDAO().create(self._conn)
            FurnaceDAO().create(self._conn)
            ContainerDAO().create(self._conn)
            ContainerSlotDAO().create(self._conn)
            SignDAO().create(self._conn)

    def store_terrain(self, chunk):
        with self._conn:
            ChunkDAO().store(self._conn, chunk)
            logger.server.info('store terrain({pos})', pos=chunk.pos)

    def load_chunk(self, chunk_pos):
        return ChunkDAO().load(self._conn, chunk_pos)
    
    def store_player(self, player):
        with self._conn:
            PlayerDAO().store(self._conn, player)
            dao = SlotDAO()
            for i, slot in enumerate(player.slots):
                if slot.is_changed:
                    dao.store(self._conn, player.player_id, i, slot)
                    slot.clear_changed()
            dao = ArmorSlotDAO()
            for i, armor_slot in enumerate(player.armor_slots):
                if armor_slot.is_changed:
                    dao.store(self._conn, player.player_id, i, armor_slot)
                    armor_slot.clear_changed()
            HotbarDAO().store(self._conn, player.player_id, player.hotbar)
            logger.server.info(
                'store player({name}, {pos})',
                name=player.name, pos=player.pos)

    def load_player(self, player_id):
        player = PlayerDAO().load(self._conn, player_id)
        if player == None:
            return None
        for i, item in SlotDAO().load(self._conn, player_id):
            player.slots[i] = item
        for i, item in ArmorSlotDAO().load(self._conn, player_id):
            player.armor_slots[i] = item
        for i, slot in enumerate(HotbarDAO().load(self._conn, player_id)):
            player.set_hotbar(i, slot, True)
        logger.server.info(
            'load player({player_id}, {pos})',
            player_id=player.player_id, pos=player.pos)
        return player
    
    def store_chest(self, chest):
        with self._conn:
            ChestDAO().store(self._conn, chest)
            logger.server.info('store chest({pos})', pos=chest.pos)

    def delete_chest(self, chest):
        with self._conn:
            ChestDAO().delete(self._conn, chest)
            logger.server.info('delete chest({pos})', pos=chest.pos)

    def load_chest(self):
        chests = list(ChestDAO().load_all(self._conn))
        # ペアを復元する
        chest_dict = {}
        for c in chests:
            if c.window_id in chest_dict:
                p = chest_dict[c.window_id]
                assert c.is_next(p.pos)
                c.set_pair(p.pos)
                p.set_pair(c.pos)
                del chest_dict[c.window_id] 
            else:
                chest_dict[c.window_id] = c
        logger.server.info('load chests(len={len})', len=len(chests))
        return chests

    def store_furnace(self, furnace):
        with self._conn:
            FurnaceDAO().store(self._conn, furnace)
            logger.server.info('store furnace({pos})', pos=furnace.pos)

    def delete_furnace(self, furnace):
        with self._conn:
            FurnaceDAO().delete(self._conn, furnace)
            logger.server.info('delete furnace({pos})', pos=furnace.pos)

    def load_furnace(self):
        furnaces = list(FurnaceDAO().load_all(self._conn))
        logger.server.info('load furnaces(len={len})', len=len(furnaces))
        return furnaces

    def store_sign(self, sign):
        with self._conn:
            SignDAO().store(self._conn, sign)
            logger.server.info('store sign({pos})', pos=sign.pos)

    def delete_sign(self, sign):
        with self._conn:
            SignDAO().delete(self._conn, sign)
            logger.server.info('delete sign({pos})', pos=sign.pos)

    def load_sign(self):
        signs = list(SignDAO().load_all(self._conn))
        logger.server.info('load signs(len={len})', len=len(signs))
        return signs

    def store_container(self, container):
        with self._conn:
            ContainerDAO().store(self._conn, container)
            dao = ContainerSlotDAO()
            for i, slot in enumerate(container):
                dao.store(self._conn, container.window_id, i, slot)
            dao.delete(self._conn, container)
            if len(container) == 0:
                ContainerDAO().delete(self._conn, container)
                logger.server.info(
                    'delete container({window_id})',
                    window_id=container.window_id)
            else:
                logger.server.info(
                    'store container({window_id})',
                    window_id=container.window_id)

    def load_container(self):
        containers = list(ContainerDAO().load_all(self._conn))
        dao = ContainerSlotDAO()
        for c in containers:
            items = list(dao.load(self._conn, c.window_id))
            if len(c) < len(items):
                c.extend()
            for i, item in enumerate(items):
                c[i] = item
            logger.server.info(
                'load container({window_id})', window_id=c.window_id)
        return containers
