# -*- coding: utf8 -*-

from operator import attrgetter
from .scheduler import Scheduler


class Reliability:
    """パケット送受信の信頼度

    UNRELIABLE : パケットの到着を保証しない
    RELIABLE : パケットの到着を保証する
    ORDERED : 順番に到着することを保証する(順番はchannel毎につく)
    SEQUENCED : 古いパケットは無視してよい(順番はchannel毎につく)
    """
    
    UNRELIABLE = 0
    UNRELIABLE_SEQUENCED = 1
    RELIABLE = 2
    RELIABLE_ORDERED = 3
    RELIABLE_SEQUENCED = 4


class Session:
    """公開するセッションインターフェース"""
    
    def __init__(self, impl):
        self._impl = impl

    def __str__(self):
        return '{name}:{addr}'.format(
            name=self.__class__.__name__,
            addr=self.addr)

    addr = property(lambda self: self._impl.addr)

    def send_packet(self, packet, reliability, is_immediate):
        self._impl.send_application_packet(packet, reliability, is_immediate)


class Handler:
    """アプリケーションの基底クラス"""
    
    def __init__(self):
        self._scheduler = Scheduler()

    scheduler = property(attrgetter('_scheduler'))

    def start(self):
        raise NotImplementedError()

    def info(self):
        raise NotImplementedError()

    def open(self, session):
        raise NotImplementedError()
    
    def close(self, session):
        raise NotImplementedError()
        
    def handle(self, session, packet):
        raise NotImplementedError()

    def update(self):
        raise NotImplementedError()