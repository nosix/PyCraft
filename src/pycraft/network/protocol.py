# -*- coding: utf8 -*-

import functools
from collections import defaultdict
from pycraft.common import filter_classes
from . import packet


class Protocol:

    __slots__ = ['_packet_dict', '_handlers']

    def __init__(self, classes):
        """Protocol が対応する Packet を指定して初期化する"""
        self._packet_dict = defaultdict(lambda: packet.StreamRaw, classes)
        self._handlers = defaultdict(lambda: _abort)

    def regist_default_handler(self, handler):
        self._handlers.default_factory = lambda: handler

    def regist_handlers(self, handlers):
        self._handlers.update(handlers)

    def packet(self, buffer):
        """バイト列に対応する Packet オブジェクトを生成する"""
        id_ = buffer[0]
        packet = self._packet_dict[id_](buffer)
        return packet
    
    def handle(self, session, packet):
        """Packet を処理する"""
        self._handlers[packet.id](session, packet)


def _abort(session, packet):
    raise NotImplementedError(packet)


packet_classes = functools.partial(
    filter_classes,
    lambda c: issubclass(c, packet.Packet) and c.id >= 0,
    lambda c: c.id)


# ネットワーク寄り(下位レイヤー)のプロトコル
net = Protocol(packet_classes(packet.ctrl, packet.data))
# アプリケーション寄り(上位レイヤー)のプロトコル
app = Protocol(packet_classes(packet.appl))
