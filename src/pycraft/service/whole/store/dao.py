# -*- coding: utf8 -*-

from pycraft.service.primitive.geometry import Position
from pycraft.service.part.item import new_item
from pycraft.service.part.tile import Chest, Furnace, Sign
from pycraft.service.composite.chunk import Chunk
from pycraft.service.composite.entity import PlayerEntity
from pycraft.service.composite.container import \
    ChestContainer, FurnaceContainer


class ChunkDAO:
    
    __slots__ = []

    def create(self, conn):
        conn.execute(
            "CREATE TABLE IF NOT EXISTS chunk("
                "x INTEGER, z INTEGER, data TEXT, "
                "PRIMARY KEY(x, z)"
            ")")
    
    def store(self, conn, chunk):
        param = (chunk.data, chunk.pos.x, chunk.pos.z)
        conn.execute(
            "UPDATE chunk SET data=? WHERE x=? AND z=?", param)
        conn.execute(
            "INSERT OR IGNORE INTO chunk(data,x,z) VALUES(?,?,?)", param)
    
    def load(self, conn, chunk_pos):
        c = conn.cursor()
        param = (chunk_pos.x, chunk_pos.z)
        c.execute("SELECT data FROM chunk WHERE x=? AND z=?", param)
        row = c.fetchone()
        if row != None:
            chunk = Chunk(chunk_pos, row[0])
        else:
            chunk = None
        c.close()
        return chunk


class PlayerDAO:
    
    __slots__ = []
    
    def create(self, conn):
        conn.execute(
            "CREATE TABLE IF NOT EXISTS player("
                "player_id TEXT, "
                "name TEXT, "
                "x REAL, z REAL, y REAL, "
                "injury INTEGER, air INTEGER, "
                "spawn_x INTEGER, spawn_z INTEGER, spawn_y INTEGER, "
                "PRIMARY KEY(player_id)"
            ")")

    def store(self, conn, player):
        param = (
            bytes(player.name, encoding='utf8'),
            player.pos.x, player.pos.z, player.pos.y,
            player.injury, player.air,
            player.spawn_pos.x, player.spawn_pos.z, player.spawn_pos.y,
            str(player.player_id))
        conn.execute(
            "UPDATE player SET "
                "name=?, x=?, z=?, y=?, injury=?, air=?, "
                "spawn_x=?, spawn_z=?, spawn_y=? "
            "WHERE player_id=?",
            param)
        conn.execute(
            "INSERT OR IGNORE INTO player("
                "name,x,z,y,injury,air,spawn_x,spawn_z,spawn_y,player_id) "
            "VALUES(?,?,?,?,?,?,?,?,?,?)",
            param)
    
    def load(self, conn, player_id):
        c = conn.cursor()
        param = (str(player_id), )
        c.execute("SELECT * FROM player WHERE player_id=?", param)
        row = c.fetchone()
        if row == None:
            player = None
        else:
            player = PlayerEntity(int(player_id), None, None, None)
            player.name = str(row['name'], encoding='utf8')
            player.pos = Position(row['x'], row['z'], row['y'])
            player.injury = row['injury']
            player.air = row['air']
            player.spawn_pos = Position(
                row['spawn_x'], row['spawn_z'], row['spawn_y'])
        c.close()
        return player


class SlotDAO:
    
    __slots__ = []
    
    def create(self, conn):
        conn.execute(
            "CREATE TABLE IF NOT EXISTS slot("
                "player_id TEXT, index_ INTEGER, "
                "item_id INTEGER, count INTEGER, attr INTEGER, "
                "PRIMARY KEY(player_id, index_), "
                "FOREIGN KEY(player_id) REFERENCES player(player_id)"
            ")")

    def store(self, conn, player_id, index, item):
        param = (item.id, item.count, item.attr, str(player_id), index)
        conn.execute(
            "UPDATE slot SET "
                "item_id=?, count=?, attr=? "
            "WHERE player_id=? AND index_=?",
            param)
        conn.execute(
            "INSERT OR IGNORE INTO slot("
                "item_id,count,attr,player_id,index_) "
            "VALUES(?,?,?,?,?)",
            param)
    
    def load(self, conn, player_id):
        c = conn.cursor()
        param = (str(player_id), )
        c.execute(
            "SELECT * FROM slot WHERE player_id=? ORDER BY index_",
            param)
        for row in c:
            item = new_item(row['item_id'], row['count'], row['attr'])
            yield row['index_'], item
        c.close()


class HotbarDAO:
    
    __slots__ = []
    
    def create(self, conn):
        conn.execute(
            "CREATE TABLE IF NOT EXISTS hotbar("
                "player_id TEXT, "
                "slot_0 INTEGER, "
                "slot_1 INTEGER, "
                "slot_2 INTEGER, "
                "slot_3 INTEGER, "
                "slot_4 INTEGER, "
                "slot_5 INTEGER, "
                "slot_6 INTEGER, "
                "slot_7 INTEGER, "
                "slot_8 INTEGER, "
                "PRIMARY KEY(player_id), "
                "FOREIGN KEY(player_id) REFERENCES player(player_id)"
            ")")

    def store(self, conn, player_id, hotbar):
        param = tuple(hotbar) + (str(player_id), )
        conn.execute(
            "UPDATE hotbar SET "
                "slot_0=?, "
                "slot_1=?, "
                "slot_2=?, "
                "slot_3=?, "
                "slot_4=?, "
                "slot_5=?, "
                "slot_6=?, "
                "slot_7=?, "
                "slot_8=? "
            "WHERE player_id=?",
            param)
        conn.execute(
            "INSERT OR IGNORE INTO hotbar("
                "slot_0,"
                "slot_1,"
                "slot_2,"
                "slot_3,"
                "slot_4,"
                "slot_5,"
                "slot_6,"
                "slot_7,"
                "slot_8,"
                "player_id) "
            "VALUES(?,?,?,?,?,?,?,?,?,?)",
            param)
    
    def load(self, conn, player_id):
        c = conn.cursor()
        param = (str(player_id), )
        c.execute(
            "SELECT "
                "slot_0, "
                "slot_1, "
                "slot_2, "
                "slot_3, "
                "slot_4, "
                "slot_5, "
                "slot_6, "
                "slot_7, "
                "slot_8 "
            "FROM hotbar WHERE player_id=?",
            param)
        row = c.fetchone()
        if row != None:
            hotbar = list(row)
        else:
            hotbar = None
        c.close()
        return hotbar


class ArmorSlotDAO:
    
    __slots__ = []
    
    def create(self, conn):
        conn.execute(
            "CREATE TABLE IF NOT EXISTS armor_slot("
                "player_id TEXT, index_ INTEGER, "
                "item_id INTEGER, count INTEGER, attr INTEGER, "
                "PRIMARY KEY(player_id, index_), "
                "FOREIGN KEY(player_id) REFERENCES player(player_id)"
            ")")

    def store(self, conn, player_id, index, item):
        param = (item.id, item.count, item.attr, str(player_id), index)
        conn.execute(
            "UPDATE armor_slot SET "
                "item_id=?, count=?, attr=? "
            "WHERE player_id=? AND index_=?",
            param)
        conn.execute(
            "INSERT OR IGNORE INTO armor_slot("
                "item_id,count,attr,player_id,index_) "
            "VALUES(?,?,?,?,?)",
            param)
    
    def load(self, conn, player_id):
        c = conn.cursor()
        param = (str(player_id), )
        c.execute(
            "SELECT * FROM armor_slot WHERE player_id=? ORDER BY index_",
            param)
        for row in c:
            item = new_item(row['item_id'], row['count'], row['attr'])
            yield row['index_'], item
        c.close()


class ChestDAO:
    
    __slots__ = []
    
    def create(self, conn):
        conn.execute(
            "CREATE TABLE IF NOT EXISTS chest("
                "x INTEGER, z INTEGER, y INTEGER, "
                "window_id INTEGER, "
                "PRIMARY KEY(x, z, y) "
            ")")

    def store(self, conn, chest):
        param = (chest.window_id, chest.pos.x, chest.pos.z, chest.pos.y)
        conn.execute(
            "UPDATE chest SET window_id=? WHERE x=? and z=? and y=?", param)
        conn.execute(
            "INSERT OR IGNORE INTO chest(window_id,x,z,y) VALUES(?,?,?,?)",
            param)
    
    def delete(self, conn, chest):
        param = (chest.pos.x, chest.pos.z, chest.pos.y)
        conn.execute("DELETE FROM chest WHERE x=? and z=? and y=?", param)

    def load_all(self, conn):
        c = conn.cursor()
        c.execute("SELECT * FROM chest")
        for row in c:
            chest = Chest(
                Position(row['x'], row['z'], row['y']), row['window_id'])
            yield chest
        c.close()


class FurnaceDAO:
    
    __slots__ = []
    
    def create(self, conn):
        conn.execute(
            "CREATE TABLE IF NOT EXISTS furnace("
                "x INTEGER, z INTEGER, y INTEGER, "
                "window_id INTEGER, "
                "PRIMARY KEY(x, z, y) "
            ")")

    def store(self, conn, furnace):
        param = (furnace.window_id, furnace.pos.x, furnace.pos.z, furnace.pos.y)
        conn.execute(
            "UPDATE furnace SET window_id=? WHERE x=? and z=? and y=?", param)
        conn.execute(
            "INSERT OR IGNORE INTO furnace(window_id,x,z,y) VALUES(?,?,?,?)",
            param)
    
    def delete(self, conn, furnace):
        param = (furnace.pos.x, furnace.pos.z, furnace.pos.y)
        conn.execute("DELETE FROM furnace WHERE x=? and z=? and y=?", param)

    def load_all(self, conn):
        c = conn.cursor()
        c.execute("SELECT * FROM furnace")
        for row in c:
            furnace = Furnace(
                Position(row['x'], row['z'], row['y']), row['window_id'])
            yield furnace
        c.close()


class ContainerDAO:
    
    __slots__ = []

    CLASS = {
        0 : ChestContainer,
        1 : FurnaceContainer,
        }

    def _class_id(self, cls):
        for k,v in self.CLASS.items():
            if v == cls:
                return k

    def create(self, conn):
        conn.execute(
            "CREATE TABLE IF NOT EXISTS container("
                "window_id INTEGER, class_id INTEGER, "
                "PRIMARY KEY(window_id)"
            ")")

    def store(self, conn, container):
        param = (self._class_id(container.__class__), container.window_id)
        conn.execute(
            "INSERT OR IGNORE INTO container(class_id,window_id) VALUES(?,?)",
            param)
    
    def delete(self, conn, container):
        param = (container.window_id, )
        conn.execute(
            "DELETE FROM container WHERE window_id=?", param)

    def load_all(self, conn):
        c = conn.cursor()
        c.execute("SELECT * FROM container")
        for row in c:
            yield self.CLASS[row['class_id']](row['window_id'])
        c.close()


class ContainerSlotDAO:
    
    __slots__ = []

    def create(self, conn):
        conn.execute(
            "CREATE TABLE IF NOT EXISTS container_slot("
                "window_id INTEGER, index_ INTEGER, "
                "item_id INTEGER, count INTEGER, attr INTEGER, "
                "PRIMARY KEY(window_id, index_)"
            ")")

    def store(self, conn, window_id, index, item):
        param = (item.id, item.count, item.attr, window_id, index)
        conn.execute(
            "UPDATE container_slot SET "
                "item_id=?, count=?, attr=? "
            "WHERE window_id=? AND index_=?",
            param)
        conn.execute(
            "INSERT OR IGNORE INTO container_slot("
                "item_id,count,attr,window_id,index_) "
            "VALUES(?,?,?,?,?)",
            param)
    
    def delete(self, conn, container):
        param = (container.window_id, len(container))
        conn.execute(
            "DELETE FROM container_slot WHERE window_id=? AND index_>=?",
            param)

    def load(self, conn, window_id):
        c = conn.cursor()
        param = (window_id,)
        c.execute(
            "SELECT * FROM container_slot WHERE window_id=? ORDER BY index_",
            param)
        for row in c:
            yield new_item(row['item_id'], row['count'], row['attr'])
        c.close()


class SignDAO:

    __slots__ = []    

    def create(self, conn):
        conn.execute(
            "CREATE TABLE IF NOT EXISTS sign("
                "x INTEGER, z INTEGER, y INTEGER, "
                "named_tag TEXT, "
                "PRIMARY KEY(x, z, y) "
            ")")

    def store(self, conn, sign):
        param = (sign.named_tag, sign.pos.x, sign.pos.z, sign.pos.y)
        conn.execute(
            "UPDATE sign SET named_tag=? WHERE x=? and z=? and y=?", param)
        conn.execute(
            "INSERT OR IGNORE INTO sign(named_tag,x,z,y) VALUES(?,?,?,?)",
            param)
    
    def delete(self, conn, sign):
        param = (sign.pos.x, sign.pos.z, sign.pos.y)
        conn.execute("DELETE FROM sign WHERE x=? and z=? and y=?", param)

    def load_all(self, conn):
        c = conn.cursor()
        c.execute("SELECT * FROM sign")
        for row in c:
            sign = Sign(
                Position(row['x'], row['z'], row['y']))
            sign.named_tag = row['named_tag']
            yield sign
        c.close()
