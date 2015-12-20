# -*- coding: utf8 -*-

from pycraft.common import ImmutableMeta


class BlockRecord(metaclass=ImmutableMeta):
    
    properties = 'x z y id attr flags'

    @classmethod
    def new(
            cls, x, z, y, id_, attr,
            flags=0,
            is_neighbors=False,
            is_network=False,
            is_nographic=False,
            is_priority=False):
        if is_neighbors:
            flags |= 0b0001
        if is_network:
            flags |= 0b0010
        if is_nographic:
            flags |= 0b0100
        if is_priority:
            flags |= 0b1000
        return x, z, y, id_, attr, flags
