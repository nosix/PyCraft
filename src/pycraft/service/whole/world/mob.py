# -*- coding: utf8 -*-

import time
from pycraft.service.primitive.geometry import \
    ChunkRectangular, Vector, Position
from pycraft.service.primitive.values import Motion 
from pycraft.service.primitive.fuzzy import Random
from pycraft.service.part.accident import AttackByMob
from pycraft.service.ai import MobAIProcess, MobStatus
from pycraft.service.composite.entity import animal, monster


class DisabledMobWorld(object):
    """Null Object of MobWorld"""
    
    @staticmethod
    def do_nothing(*args, **kwargs):
        pass
    
    def __getattr__(self, name):
        return self.do_nothing


class MobWorld:
    
    MAX_NUM_OF_MOBS = 10
    MAX_MOVEMENT = 1

    def __init__(
            self, components,
            terrain, entity, player, hit_callback, lose_callback):
        self._listener = components.listener
        self._random = Random(int(time.clock()))  # TODO: 時刻にする
        self._terrain = terrain
        self._entity = entity
        self._player = player
        self._hit_callback = hit_callback
        self._lose_callback = lose_callback
        self._mobs = []
        # 消滅予定時刻とEntity.eidの一覧
        self._dead_mobs = []
        # MobAI
        self._ai_process = MobAIProcess()
        # Mobをデスポーンするスコアの上限
        self._remove_score = 0
        # Mobの行動を停止させるスコアの上限
        self._freeze_score = self._terrain.map.MAX_SCORE_PER_PLAYER // 4
        # Mobをスポーンさせるスコアの範囲
        self._spawn_score = list(range(
            self._freeze_score+1, self._terrain.map.MAX_SCORE_PER_PLAYER))

    def start(self):
        self._ai_process.start()
    
    def terminate(self):
        self._ai_process.terminate()

    def _move_y(self, mob, pos):
        def get_y():
            return (self._terrain.get_ground_pos(p.astype(int)).y 
                for p in mob.BODY_SIZE.lower_bounds(pos))
        y = max(get_y())
        return Position(pos.x, pos.z,y) if y - pos.y <= 1 else pos

    def _push_back(self, mob, pos, distance):
        v_move = pos.direc(mob.pos)
        def has_collision(p):
            for y in range(int(p.y), int(p.y+mob.BODY_SIZE.height+1)):
                if not self._terrain.is_transparent(Position(p.x, p.z, y)):
                    return True
            return False
        def collision_pos():
            l_bounds = mob.BODY_SIZE.lower_bounds(pos, distance)
            return (p for p in l_bounds if has_collision(p))
        def movement_vec():
            yield v_move
            for to_pos in collision_pos():
                fm_pos = to_pos - v_move
                inter = to_pos.intersection(fm_pos)
                yield inter.direc(fm_pos) if (inter != None) else Vector(0,0,0)
        v = min(movement_vec(), key=lambda v: v.distance())
        if mob.can_climb():
            d = distance - v.distance()
            if self._can_move_up(mob, mob.pos + v + (0,0,d)):
                v += (0,0,d)
        return mob.pos + v

    def _can_move_up(self, mob, pos):
        for x, z, y in mob.BODY_SIZE.lower_bounds(pos):
            y += mob.BODY_SIZE.height
            if not self._terrain.is_transparent(Position(x,z,y)):
                return False
        return True

    def spawn(self):
        self._process_dead_mob()
        mob = self._spawn()
        if mob != None:
            mob.meet_callback = self._hit_callback
            mob.lose_callback = self._lose_callback
            self._entity.add(mob)
            self._mobs.append(mob)
            self._listener.mob_added([mob])
    
    def _spawn(self):
        if len(self._mobs) >= self.MAX_NUM_OF_MOBS:
            return None
        # スポーンする Chunk を決める
        candidate = list(self._terrain.map.find(self._spawn_score))
        if len(candidate) == 0:
            return None
        i = self._random.next_int() % len(candidate)
        chunk_pos = candidate[i]
        # スポーンする位置を決める
        x = self._random.next_int() % ChunkRectangular.X
        z = self._random.next_int() % ChunkRectangular.Z
        y = self._random.next_int() % ChunkRectangular.Y
        pos = self._terrain.get_ground_pos(chunk_pos.pos(x, z, y))
        # Chunk が未生成 or 未読み込みの場合は None になる
        if pos == None:
            return None
        # スポーンする Mob を決める TODO: 実装する
        factory = [
            monster.Spider,
            animal.Bat,
            animal.Chicken,
            animal.Sheep,
            animal.Wolf,
            animal.Villager,
            ]
        i = self._random.next_int() % len(factory)
        mob = factory[i]()
        mob.pos = pos
        # スポーン可能な条件か？ TODO: 実装する
        return mob

    def lose(self, mob, accident):
        # 死亡を通知する
        self._listener.mob_died(mob.eid)
        # アイテムを落とす
        self._entity.drop_items(mob, accident)
        # Mobを削除する
        self._terrain.map.remove_mob(mob)
        self._mobs.remove(mob)
        self._append_dead_mob(mob.eid, 3)
    
    def _append_dead_mob(self, eid, wait_time):
        t = time.clock() + wait_time
        i = 0
        for i in range(len(self._dead_mobs)):
            if self._dead_mobs[i][0] < t:
                break
        value = (t, eid)
        self._dead_mobs.insert(i, value)
    
    def _process_dead_mob(self):
        while len(self._dead_mobs) > 0:
            t, eid = self._dead_mobs.pop()
            if time.clock() >= t:
                self._remove(eid)
            else:
                value = (t, eid)
                self._dead_mobs.append(value)
                break

    def _remove(self, eid):
        status = MobStatus(0, 0, 0, tuple())
        self._ai_process.send(eid, status)
        self._entity.remove(eid)
        self._listener.mob_removed(eid)

    def move(self):
        if len(self._mobs) == 0:
            return
        mob = self._mobs.pop(0)
        # Playerと遠く離れていたらデスポーンする
        if self._terrain.map.score(mob.pos) <= self._remove_score:
            self._terrain.map.remove_mob(mob)
            eid = mob.eid
            # TODO: 中立モブならばDBに保存
            self._remove(eid)
            return
        self._mobs.append(mob)
        if not self._does_act(mob):
            return
        motion = self._move(mob)
        if motion != None:
            accident = self._entity.move(mob, motion, not mob.can_fly())
            if accident != None:
                mob.lose(accident)
                return
        self._sence(mob)

    def _does_act(self, mob):
        # 前回の更新から所定の時間が経過していなければ何もしない
        if not mob.tick():
            return False
        # Playerと離れていたら動かない
        if self._terrain.map.score(mob.pos) <= self._freeze_score:
            return False
        return True

    def _move(self, mob):
        # AIから情報を受け取る
        m = self._ai_process.recv(mob.eid)
        if m == None:
            return None
        # 名前を変更
        old_name = mob.name
        mob.name = m.name
        if mob.name != old_name:
            self._listener.entity_changed(mob.eid, mob.meta)
        # 相対値から絶対値に変換
        yaw = mob.yaw + m.yaw
        head_yaw = mob.head_yaw + m.yaw + m.head_yaw
        pitch = mob.pitch + m.pitch
        # 前進する
        abs_fm = abs(m.forward_move)
        if abs_fm > self.MAX_MOVEMENT:
            forward_move = m.forward_move/abs_fm * self.MAX_MOVEMENT
        else:
            forward_move = m.forward_move
        d = Vector.by_angle(
            forward_move, yaw, (pitch if mob.can_fly() else None))
        pos = mob.pos + d
        # 動いた先に Chunk がなければ動かない
        if not self._terrain.map.has_chunk(mob.BODY_SIZE.lower_bounds(pos)):
            return None
        # 地形にあわせて上下に移動する
        if not mob.can_fly():
            pos = self._move_y(mob, pos)
            pos = self._push_back(mob, pos, forward_move)
            if mob.pos.y - pos.y > 1 and mob.can_climb():
                pos = Position(pos.x,pos.z,mob.pos.y-1)
        # 動作を通知する
        motion = Motion(mob.eid, pos, yaw, head_yaw, pitch)
        if motion == mob.motion:
            return None
        return motion

    def _sence(self, mob):
        found = tuple(self._search_player(mob))
        status = MobStatus(mob.TYPE, mob.head_yaw-mob.yaw, mob.pitch, found)
        self._ai_process.send(mob.eid, status)

    def _search_player(self, mob):
        eye_pos = mob.eye_pos
        def can_see(p):
            return mob.in_view(p) and self._terrain.can_see(p, eye_pos)
        def did_find(player):
            body_size = player.BODY_SIZE
            return player.is_living() and any(can_see(p)
                for bp in body_size.lower_bounds(player.bottom_pos)
                    for p in (bp, bp + (0, 0, body_size.height)))
        return (
            (p.eid,
             eye_pos.distance(p.pos),
             eye_pos.angle_h(p.pos, mob.head_yaw),
             eye_pos.angle_v(p.pos, mob.pitch))
                for p in self._player if did_find(p))

    def attack_entity(self, mob, entity):
        mob.attack(entity)
        self._listener.entity_injured(entity.eid, entity.health)
        if not entity.is_living():
            entity.lose(AttackByMob(entity, mob))
