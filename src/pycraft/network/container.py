# -*- coding: utf8 -*-

from .packet.data import EncapsulatedPacket as EncapPacket


class DataPacketContainer:
    """EncapsulatedPacket を蓄積して、DataPacket を生成する"""
    
    __slots__ = ['_factory', '_packet']

    def __init__(self, factory):
        """送信する DataPacket のクラスを指定して初期化する"""
        self._factory = factory
        self._packet = self._factory()
    
    def is_empty(self):
        """EncapsulatedPacket が蓄積されていないときに True を返す"""
        return len(self._packet.packets) == 0

    def add(self, packet):
        """EncapsulatedPacket を追加する"""
        self._packet.packets.append(packet)

    def get(self):
        """EncapsulatedPacket を包含した DataPacket を返す"""
        pk = self._packet
        self._packet = self._factory()
        return pk

    def __len__(self):
        """DataPacket を符号化したときの長さを返す"""
        return len(self._packet)


class SplitPacketContainer:
    """分割された EncapsulatedPacket を保存して結合するコンテナ"""
    
    __slots__ = ['_split_packets']

    def __init__(self):
        self._split_packets = {}
    
    def concat(self, packet):
        """分割された EncapsulatedPacket を結合する"""
        # 分割されたパケットを保存するためのコンテナをつくる
        if packet.split.id not in self._split_packets:
            self._split_packets[packet.split.id] = {}
        # コンテナにパケットを保存する
        container = self._split_packets[packet.split.id]
        container[packet.split.index] = packet
        if len(container) == packet.split.count:
            # コンテナにパケットが揃ったならば結合したパケットを返す
            buffer = b''.join(
                pk.buffer for pk in 
                    sorted(container.values(), key=lambda v: v.split.index))
            del self._split_packets[packet.split.id]
            return EncapPacket(0, buffer)
        else:
            # コンテナにパケットが揃っていないならば何も返さない
            return None
