# -*- coding: utf8 -*-

from pycraft.common import ImmutableMeta
from pycraft.common.util import put_in_range, put_in_border


class Motion(metaclass=ImmutableMeta):
    """Entity の動き
    
    eid : 個体識別子
    pos : 位置
    yaw : 体の水平方向(度)
    head_yaw : 頭の水平方向(度)
    pitch : 頭の垂直方向(度)
    """

    properties = 'eid pos yaw head_yaw pitch'
    
    @classmethod
    def new(cls, eid, pos, yaw, head_yaw, pitch):
        yaw = put_in_range(yaw, 360)
        head_yaw = put_in_range(head_yaw, 360)
        pitch = put_in_border(pitch, -90, 90)
        return eid, pos, yaw, head_yaw, pitch
