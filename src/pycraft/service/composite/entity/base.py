# -*- coding: utf8 -*-

import time
from pycraft.service.primitive.geometry import Position, Face
from pycraft.service.primitive.geometry import OrientedBoundingBox as OBB
from pycraft.service.primitive.values import MetaData, Motion


class Entity:
    
    @staticmethod
    def no_callback(self, entity):
        raise NotImplementedError()

    def __init__(self):
        self.meet_callback = self.no_callback
        self.lose_callback = self.no_callback
        self.eid = 0
        self.pos = Position(0, 0, 0)
        self._meta = MetaData()

    def copy_from(self, other):
        self.eid = other.eid
        self.pos = other.pos
        self._meta = other._meta.clone()

    def clone(self):
        o = self.__class__.__new__(self.__class__)
        o.copy_from(self)
        o.meet_callback = self.no_callback
        o.lose_callback = self.no_callback
        return o

    meta = property(lambda self: MetaData(self._meta))

    bottom_pos = property(lambda self: self.pos)
    
    def is_living(self):
        return False    

    def does_push_out(self):
        return False

    def did_meet(self, entity):
        """Entity に当たられたなら True"""
        return False

    def meet(self, entity):
        """Entity に当たられたときの動作"""
        self.meet_callback(self, entity)

    def lose(self, accident):
        self.lose_callback(self, accident)

    def hit_item(self, item):
        item.use_on_entity()


class LivingEntity(Entity):
    
    STRENGTH = 10
    BODY_SIZE = None

    def __init__(self):
        super().__init__()
        # 体の水平方向(0..360, 0 z+,x-,z-,x+,z+ 360)
        self.yaw = 0
        # 頭の水平方向(0..360)
        self.head_yaw = 0
        # 頭の垂直方向(-90..90, -90 y+,y- 90)
        self.pitch = 0
        # 傷
        self._injury = 0
        # 落下開始地点
        self._fly_top_y = 0
        
    def copy_from(self, other):
        super().copy_from(other)
        self.yaw = other.yaw
        self.head_yaw = other.head_yaw
        self.pitch = other.pitch
        self._injury = other._injury
        self._fly_top_y = other._fly_top_y

    def get_name(self):
        _, value = self._meta.get(MetaData.Key.NAMETAG)
        return value

    def set_name(self, name):
        self._meta.set(MetaData.Key.NAMETAG, name)

    def get_air(self):
        _, value = self._meta.get(MetaData.Key.AIR)
        return value

    def set_air(self, air):
        self._meta.set(MetaData.Key.AIR, air)

    def set_injury(self, injury):
        self._injury = injury if injury < self.STRENGTH else self.STRENGTH

    name = property(get_name, set_name)
    air = property(get_air, set_air)
    health = property(lambda self: self.STRENGTH - self._injury)
    injury = property(lambda self: self._injury, set_injury)
    face = property(lambda self: Face.by_angle(self.head_yaw, self.pitch))
    obb = property(lambda self: OBB(self.bottom_pos, self.BODY_SIZE, self.yaw))
    motion = property(lambda self:
        Motion(self.eid, self.pos, self.yaw, self.head_yaw, self.pitch))

    def is_living(self):
        return self.health > 0

    def has_hostile(self, entity):
        return False

    def move(self, pos, on_ground):
        """移動する
        
        pos : Position 位置
        on_ground : boolean 接地しているか
        return : 傷ついたら True
        """
        self.pos = pos
        if on_ground:
            diff = self._fly_top_y - pos.y
            self._fly_top_y = pos.y
            injury = int(diff - 2.5)
            if injury > 0:
                self.injury += injury
                return True
        else:
            if pos.y > self._fly_top_y:
                self._fly_top_y = pos.y
        return False


class MobEntity(LivingEntity):
    
    TICK_TIME = 0.1  # sec

    TYPE = 0
    VIEW_DISTANCE = 128
    VIEW_ANGLE_H = 180
    VIEW_ANGLE_V = 90

    def __init__(self):
        super().__init__()
        self._meta.set(MetaData.Key.NAMETAG, self.__class__.__name__)
        self._latest_time = time.clock()
    
    def get_name(self):
        _, value = self._meta.get(MetaData.Key.NAMETAG)
        return value

    def set_name(self, name):
        self._meta.set(MetaData.Key.SHOW_NAMETAG, 1 if name else 0)
        if not name:
            name = self.__class__.__name__
        self._meta.set(MetaData.Key.NAMETAG, name)

    name = property(get_name, set_name)
    eye_y = property(lambda self: self.BODY_SIZE.height * 3/4)
    eye_pos = property(lambda self: self.bottom_pos + (0, 0, self.eye_y))

    def can_fly(self):
        return False

    def can_climb(self):
        return False

    def has_hostile(self, entity):
        return False    

    def attack(self, entity):
        entity.injury += 1

    def drop_items(self):
        return []

    def tick(self):
        diff = time.clock() - self._latest_time
        if diff < self.TICK_TIME:
            return False
        self._latest_time += diff
        return True

    def in_view(self, pos):
        eye_pos = self.eye_pos
        return (eye_pos.distance(pos) <= self.VIEW_DISTANCE
            and abs(eye_pos.angle_h(pos, self.head_yaw)) <= self.VIEW_ANGLE_H
            and abs(eye_pos.angle_v(pos, self.pitch)) <= self.VIEW_ANGLE_V)
