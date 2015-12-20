# -*- coding: utf8 -*-

from collections import defaultdict
from operator import attrgetter
from pycraft import network
from . import packet


class Protocol(network.Protocol):

    def __init__(self, protocol_ver, minecraft_ver, classes):
        super().__init__(classes)
        self._protocol_ver = protocol_ver
        self._minecraft_ver = minecraft_ver

    protocol_version = property(attrgetter('_protocol_ver'))
    minecraft_version = property(attrgetter('_minecraft_ver'))


v38 = Protocol(
    38, '0.13.1', network.packet_classes(packet.both, packet.recv))

default = v38

shelf = defaultdict(lambda: default)
