# -*- coding: utf8 -*-

from pycraft.common import ImmutableMeta


class MobStatus(metaclass=ImmutableMeta):
    """
    type : int - EntityType(亡くなっている場合には 0)
    head_yaw : float - 頭の水平向き(角度, 体の向きと同じとき 0)
    pitch : float - 頭の垂直向き(角度, 水平のとき 0)
    found: tuple
        Player.eid : int - 発見したプレイヤーの eid
        distance : float - 発見したプレイヤーとの距離
        angle_h : float - 発見したプレイヤーへの向き(水平方向)
        angle_v : float - 発見したプレイヤーへの向き(垂直方向)
    """
    
    properties = 'type head_yaw pitch found'

    @classmethod
    def new(cls, *args):
        return tuple(args) if len(args) != 1 else tuple(args[0])


class MobMotion(metaclass=ImmutableMeta):
    """
    yaw : float - 体の水平方向の移動量(角度)
    head_yaw : float - 頭の水平方向の移動量(角度)
    pitch : float - 頭の垂直方向の移動量(角度)
    forward_move : float(-1.0..1.0) - 前後の移動量
    name : str - mob name 
    """
    
    properties = 'yaw head_yaw pitch forward_move name'

    @classmethod
    def new(cls, *args):
        return tuple(args) if len(args) != 1 else tuple(args[0])
