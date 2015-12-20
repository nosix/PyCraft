# -*- coding: utf8 -*-

import time
from pycraft.service.primitive.fuzzy import Random
from .values import MobMotion


class MobAI:
    
    RANDOM = Random(int(time.clock()))

    def next_motion(self, status):
        if len(status.found) > 0:
            _, distance, angle_h, angle_v = \
                min(status.found, key=lambda t: t[1])
            head_yaw = angle_h * (1 - 1 / (distance + 1))
            return MobMotion(
                status.head_yaw + head_yaw, -status.head_yaw, angle_v,
                distance/30, '')
        else:
            yaw = self.RANDOM.next_float() * 10 - 5
            if status.head_yaw > 45:
                head_yaw = - self.RANDOM.next_float() * 5
            elif status.head_yaw < -45:
                head_yaw = self.RANDOM.next_float() * 5
            else:
                head_yaw = self.RANDOM.next_float() * 10 - 5
            if status.pitch > 30:
                pitch = - self.RANDOM.next_float() * 3
            elif status.pitch < -30:
                pitch = self.RANDOM.next_float() * 3
            else:
                pitch = self.RANDOM.next_float() * 6 - 3
            return MobMotion(yaw, head_yaw, pitch, 0.1, '')