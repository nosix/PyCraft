# -*- coding: utf8 -*-

from . import logger


class WindowIndex:
    """Packet の index を生成する
    
    >>> i = WindowIndex()
    >>> i.curr()
    0
    >>> i.next()
    0
    >>> i.next()
    1
    >>> i.seek(5)
    2
    >>> i.curr()
    7
    >>> i.prev()
    7
    >>> i.seek(-5)
    6
    >>> i.curr()
    1
    """
    
    __slots = ['_current']
    
    def __init__(self, initial=0):
        """添字の初期値を指定して初期化する"""
        self._current = initial
    
    def curr(self):
        """現在の添字を返す"""
        return self._current
    
    def seek(self, n=0):
        """現在の添字を返して、指定した値だけ進める"""
        index = self._current
        self._current += n
        return index
        
    def next(self):
        """現在の添字を返して、現在の添字を次に進める"""
        return self.seek(1)
    
    def prev(self):
        """現在の添字を返して、現在の添字を前に進める"""
        return self.seek(-1)


class DataPacketWindow:

    __slots__ = ['_latest_seq_num', '_wait_seq_nums', '_ack_seq_nums']

    _SIZE = 8

    def __init__(self):
        # 最後に受信した DataPacket 番号
        self._latest_seq_num = -1
        # 受信待ち DataPacket 番号
        self._wait_seq_nums = set()
        # ACK 送信待ち DataPacket 番号
        self._ack_seq_nums = set()

    def put(self, packet):
        self._ack_seq_nums.add(packet.seq_num)
        diff = packet.seq_num - self._latest_seq_num
        if diff > 0:
            # より新しいパケットが届いた
            min_seq_num = packet.seq_num - self._SIZE
            self._wait_seq_nums = set(
                n for n in self._wait_seq_nums if n >= min_seq_num)
            self._wait_seq_nums |= set(
                n for n in range(self._latest_seq_num+1, packet.seq_num))
            self._latest_seq_num = packet.seq_num
            return True
        elif diff + self._SIZE >= 0:
            # 古いパケットが届いた
            if packet.seq_num in self._wait_seq_nums:
                self._wait_seq_nums.discard(packet.seq_num)
                return True
        else:
            # 古すぎるパケットが届いた
            logger.server.info(
                'discard old packet (seq_num={seq_num})',
                seq_num=packet.seq_num)
        return False
            
    def get_seq_nums(self):
        ack_seq_nums = self._ack_seq_nums
        nack_seq_nums = set(self._wait_seq_nums)
        self._ack_seq_nums = set()
        return ack_seq_nums, nack_seq_nums


class EncapsulatedPacketWindow:

    __slots__ = [
        '_latest_index',
        '_wait_index',
        '_latest_order_index',
        '_wait_packets',
        ]

    _SIZE = 8

    def __init__(self):
        # 最新 message.index
        self._latest_index = -1
        # 受信待ち message.index
        self._wait_index = set()
        # channel 毎の最新 index
        self._latest_order_index = {}
        # 処理可能パケット
        self._wait_packets = []
    
    def put(self, packet):
        # 順番付けられていない場合は即座に処理可能
        if not packet.message:
            self._wait_packets.append(packet)
            return

        diff = packet.message.index - self._latest_index
        if diff > 0:
            # より新しいパケットが届いた
            min_index = packet.message.index - self._SIZE
            self._wait_index = set(
                n for n in self._wait_index if n >= min_index)
            self._wait_index |= set(
                n for n in range(self._latest_index+1, packet.message.index))
            self._latest_index = packet.message.index
        elif diff + self._SIZE >= 0:
            # 古いパケットが届いた
            if packet.message.index in self._wait_index:
                self._wait_index.discard(packet.message.index)
            else:
                logger.server.info(
                    'discard duplicate packet m[{index}]',
                    index=packet.message.index)
                return
        else:
            # 古すぎるパケットが届いた
            logger.server.info(
                'discard old packet m[{index}]', index=packet.message.index)
            return
            
        if packet.order:
            channel = packet.order.channel
            index = packet.order.index
            if ((channel not in self._latest_order_index) or 
                    (self._latest_order_index[channel] <= index)):
                self._latest_order_index[channel] = index
            else:
                logger.server.info(
                    'discard old packet o[{channel},{index}]',
                    channel=channel, index=index)
                return

        self._wait_packets.append(packet)

    def get(self):
        return self._wait_packets.pop(0)

    def __len__(self):
        return len(self._wait_packets)


if __name__ == '__main__':
    import doctest
    doctest.testmod()