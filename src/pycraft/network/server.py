# -*- coding: utf8 -*-


import os
import socket
import random
import queue
import time
import selectors
from operator import attrgetter
from pycraft.common.util import max_int, divide_seq
from .packet import ID, ctrl, data, appl
from .packet.data import EncapsulatedPacket as EncapPacket
from . import container, interface, logger, protocol, window


_RECV_BUFFER_SIZE = 4096  # bytes
_MAX_MTU_SIZE = 1464  # bytes
_ACK_TIMEOUT = 60  # sec


class Server:
    """UDPパケットの送受信を行うサーバー
    
    同一クライアント(IPアドレス、ポートで識別)との送受信を
    セッションとして扱う。パケットの符号化/復号化を行う。
    """

    id = property(attrgetter('_id'))
    handler = property(attrgetter('_handler'))

    def __init__(self, server_addr, handler):
        self._server_addr = server_addr
        self._id = random.randrange(max_int(8, False) + 1)
        self._handler = handler
        self._terminated = False
        self._sessions = {}
        self._send_queue = queue.Queue()
        self._init_protocol()
        logger.server.info('PyCraft server initialized.')
    
    def _init_protocol(self):
        protocol.net.regist_handlers({
            ID.UNCONNECTED_PING :
                Session.handle_unconnected_ping,
            ID.OPEN_CONNECTION_REQUEST_1 :
                Session.handle_open_connection_request1,
            ID.OPEN_CONNECTION_REQUEST_2 :
                Session.handle_open_connection_request2,
            ID.ACK :
                Session.handle_ack,
            ID.NACK :
                Session.handle_nack,
            ID.DATA_PACKET_0 : Session.handle_data_packet,
            ID.DATA_PACKET_1 : Session.handle_data_packet,
            ID.DATA_PACKET_2 : Session.handle_data_packet,
            ID.DATA_PACKET_3 : Session.handle_data_packet,
            ID.DATA_PACKET_4 : Session.handle_data_packet,
            ID.DATA_PACKET_5 : Session.handle_data_packet,
            ID.DATA_PACKET_6 : Session.handle_data_packet,
            ID.DATA_PACKET_7 : Session.handle_data_packet,
            ID.DATA_PACKET_8 : Session.handle_data_packet,
            ID.DATA_PACKET_9 : Session.handle_data_packet,
            ID.DATA_PACKET_A : Session.handle_data_packet,
            ID.DATA_PACKET_B : Session.handle_data_packet,
            ID.DATA_PACKET_C : Session.handle_data_packet,
            ID.DATA_PACKET_D : Session.handle_data_packet,
            ID.DATA_PACKET_E : Session.handle_data_packet,
            ID.DATA_PACKET_F : Session.handle_data_packet,
            })
        protocol.app.regist_handlers({
            ID.CLIENT_CONNECT :
                Session.handle_client_connect,
            ID.CLIENT_HANDSHAKE :
                Session.handle_client_handshake,
            ID.CLIENT_DISCONNECT :
                Session.handle_client_disconnect,
            ID.PING : 
                Session.handle_ping,
            ID.PONG : 
                Session.handle_pong,
            })
        protocol.app.regist_default_handler(Session.handle_application_packet)
    
    def _init_socket(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind(self._server_addr)
        self._sock.setblocking(False)
        self._recv_selector = selectors.DefaultSelector()
        self._send_selector = selectors.DefaultSelector()
        self._send_selector.register(
            self._sock, selectors.EVENT_WRITE, self._handle_send_packet)
        self._recv_selector.register(
            self._sock, selectors.EVENT_READ, self._handle_recv_packet)

    def terminate(self):
        self._terminated = True

    def run(self, started_callback=lambda: None):
        logger.server.info(
            'start {name}(pid={pid})',
            name=self.__class__.__name__, pid=os.getpid())
        self._handler.start()
        self._init_socket()
        started_callback()
        while not self._terminated:
            self._handler.scheduler.start()
            self._process()
        self._handler.terminate()
        self._sock.close()
        logger.server.info('terminate {name}', name=self.__class__.__name__)
    
    def _process(self):
        self._update_sessions()
        self._handle_packet()
        self._handler.update()
    
    def _update_sessions(self):
        for s in list(self._sessions.values()):
            s.update()
            # TODO: セッションタイムアウト
            if s.is_disabled():
                del self._sessions[s.addr]

    def _handle_packet(self):
        for key, _ in self._send_selector.select(0):
            key.data(key.fileobj)
        for key, _ in self._recv_selector.select(0):
            key.data(key.fileobj)

    def _handle_send_packet(self, sock):
        while not self._send_queue.empty() \
                and self._send_packet(sock, *self._send_queue.get_nowait()):
            pass

    def _send_packet(self, sock, packet, addr):
        """Packet を送信する"""
        packet.encode()
        buffer = packet.buffer()
        sock.sendto(buffer, addr)
        logger.packet.debug(
            '{addr}<{buffer}', addr=addr, buffer=buffer.hex())
        logger.server.debug(
            'N< {addr} {packet}', addr=addr, packet=packet)

    def _handle_recv_packet(self, sock):
        packet, addr = self._recv_packet(sock)
        session = self._session(addr)
        protocol.net.handle(session, packet)
        session.send_acknowledge()

    def _recv_packet(self, sock):
        """Packet を受信する"""
        buffer, addr = sock.recvfrom(_RECV_BUFFER_SIZE)
        packet = protocol.net.packet(buffer)
        packet.decode()
        logger.packet.debug(
            '{addr}>{buffer}', addr=addr, buffer=buffer.hex())
        logger.server.debug(
            'N> {addr} {packet}', addr=addr, packet=packet)
        return packet, addr
    
    def _session(self, addr):
        """アドレスに該当する Session を返す"""
        if addr not in self._sessions:
            self._sessions[addr] = Session(self, addr)
        return self._sessions[addr]

    def send_packet(self, packet, addr):
        """Packet を送信キューに登録する"""
        self._send_queue.put_nowait((packet, addr))


class Session(object):
    """クライアント(IPアドレス、ポートで識別)との送受信セッション"""

    _STATE_UNCONNECTED = 0
    _STATE_CONNECTED = 1
    _STATE_DISCONNECTED = 2

    addr = property(attrgetter('_addr'))
    id = property(attrgetter('_id'))

    def __init__(self, server, client_addr):
        self._addr = client_addr
        self._id = -1
        self._server = server
        self._state = Session._STATE_UNCONNECTED
        # 外部公開インターフェース
        self._interface = interface.Session(self)
        # Maximum Transmission Unit Size
        self._mtu_size = 0
        # 受信済み DataPacket
        self._recv_packets = window.DataPacketWindow()
        # 処理待ち EncapsulatedPacket
        self._encap_packets = window.EncapsulatedPacketWindow()
        # 分割されたパケットの蓄積
        self._split_packets = container.SplitPacketContainer()
        # 送信待ちパケット
        self._waiting_packet = container.DataPacketContainer(data.DataPacket4)
        # 送信 DataPacket に付与する番号
        self._send_seq_num = window.WindowIndex()
        # 送信 EncapsulatedPacket に付与する番号
        self._send_message_index = window.WindowIndex()
        # channel 毎の index 値
        self._channel_index = [window.WindowIndex() for _ in range(32)]
        # split_id に付与する番号
        self._split_id = window.WindowIndex()
        # seq_num -> (Packet, time)
        self._ack_wait_packets = {}
    
    def is_disabled(self):
        return self._state == Session._STATE_DISCONNECTED
    
    def handle_unconnected_ping(self, packet):
        pk = ctrl.UnconnectedPong()
        pk.server_id = self._server.id
        pk.server_info = self._server.handler.info()
        pk.ping_id = packet.ping_id
        self.send_packet(pk)

    def handle_open_connection_request1(self, packet):
        self._mtu_size = _MAX_MTU_SIZE  # 初期化
        pk = ctrl.OpenConnectionReply1()
        pk.mtu_size = packet.mtu_size
        pk.server_id = self._server.id
        self.send_packet(pk)

    def handle_open_connection_request2(self, packet):
        if self._mtu_size == 0:
            logger.server.warning(
                '{addr} is illegal state. ', addr=self._addr)
            return
        self._id = packet.client_id
        if self._mtu_size > packet.mtu_size:
            self._mtu_size = packet.mtu_size
        pk = ctrl.OpenConnectionReply2()
        pk.mtu_size = self._mtu_size
        pk.server_id = self._server.id
        pk.client_addr = self.addr
        self.send_packet(pk)

    def handle_ack(self, packet):
        for seq_num in packet.seq_nums:
            if seq_num in self._ack_wait_packets:
                del self._ack_wait_packets[seq_num]

    def handle_nack(self, packet):
        for seq_num in packet.seq_nums:
            if seq_num in self._ack_wait_packets:
                pk, _ = self._ack_wait_packets[seq_num]
                del self._ack_wait_packets[seq_num]
                self.send_packet(pk)

    def handle_data_packet(self, packet):
        # 既に処理済みのパケットなら何もしない
        if not self._recv_packets.put(packet):
            return
        # パケットを処理する
        for pk in packet.packets:
            self._handle_encapsulated_packet(pk)
    
    def _handle_encapsulated_packet(self, packet):
        """EncapsulatedPacket を処理する"""
        logger.server.debug(
            'N>> {addr} {packet}', addr=self._addr, packet=packet)
        self._encap_packets.put(packet)
        while len(self._encap_packets) > 0:
            self._handle_encapsulated_packet_route(self._encap_packets.get())
        
    def _handle_encapsulated_packet_route(self, packet):
        """順番に到着した EncapsulatedPacket を処理する"""
        if packet.split:
            packet = self._split_packets.concat(packet)
            if packet == None:
                return
        pk = protocol.app.packet(packet.buffer)
        pk.decode()
        logger.server.debug(
            'N>>> {addr} {packet}', addr=self._addr, packet=pk)
        protocol.app.handle(self, pk)
    
    def handle_client_connect(self, packet):
        pk = appl.ServerHandshake()
        pk.addr = self.addr
        pk.send_ping = packet.send_ping
        pk.send_pong = packet.send_ping + 1000
        self.send_application_packet(pk, 0, True)

    def handle_client_handshake(self, packet):
        self._state = Session._STATE_CONNECTED
        self._server.handler.open(self._interface)

    def handle_client_disconnect(self, packet):
        self._server.handler.close(self._interface, 'client disconnect')
        self._state = Session._STATE_DISCONNECTED

    def handle_ping(self, packet):
        ping_id = random.randrange(max_int(8, False) + 1)
        pk = appl.Pong()
        pk.recv_ping_id = packet.ping_id
        pk.send_ping_id = ping_id
        self.send_application_packet(pk, 0)
        pk = appl.Ping()
        pk.ping_id = ping_id
        self.send_application_packet(pk, 0)

    def handle_pong(self, packet):
        pass  # TODO: セッションタイムアウトに利用する

    def handle_application_packet(self, packet):
        """ApplicationPacket を処理する"""
        if self._state == Session._STATE_CONNECTED:
            self._server.handler.handle(self._interface, packet)
    
    def send_application_packet(self, packet, reliability, is_immediate=False):
        """ApplicationPacket を EncapsulatedPacket に包んで送信する
        
        reliability : EncapsulatedPacket の reliability 参照
        is_immediate : True ならばキューに積まずに送信
        """
        if len(packet.buffer()) == 0:
            packet.encode()
            logger.server.debug(
                'N<<< {addr} {packet}', addr=self._addr, packet=packet)
        # EncapsulatedPacket をつくる
        param = {}
        if EncapPacket.is_reliable(reliability):
            param['message'] = \
                EncapPacket.Message(self._send_message_index.next())
        if EncapPacket.is_ordered(reliability):
            index = self._channel_index[packet.channel].next()
            param['order'] = EncapPacket.Order(index, packet.channel)
        buffer = packet.buffer()
        pk = EncapPacket(reliability, buffer, **param)
        # mtu_size に収まっているならば送信
        overflow = len(data.DataPacket0()) + len(pk) - self._mtu_size
        if overflow <= 0:
            self._send_encapsulated_packet(pk, is_immediate)
            return
        # mtu_size に収まっていなければ分割して送信
        buf_len = len(buffer) - overflow
        buffers = divide_seq(buffer, buf_len)
        self._send_message_index.prev()
        split_count = len(buffers)
        split_id = self._split_id.next()
        for i, buf in enumerate(buffers):
            if EncapPacket.is_reliable(reliability):
                param['message'] = \
                    EncapPacket.Message(self._send_message_index.next())
            param['split'] = EncapPacket.Split(split_count, split_id, i)
            pk = EncapPacket(reliability, buf, **param)
            self._send_encapsulated_packet(pk, True)
    
    def _send_encapsulated_packet(self, packet, is_immediate=False):
        """EncapsulatedPacket を DataPacket に包んで送信する
        
        is_immediate : True ならばキューに積まずに送信
        """
        logger.server.debug(
            'N<< {addr} {packet}', addr=self._addr, packet=packet)
        if is_immediate:
            pk = data.DataPacket0()
            pk.seq_num = self._send_seq_num.next()
            pk.packets = [packet]
            self._send_waiting_packet()
            self.send_packet(pk)
        else:
            if len(self._waiting_packet) + len(packet) > self._mtu_size:
                # mtu_sizeを超えるようであれば超えない範囲を送信する
                self._send_waiting_packet()
            self._waiting_packet.add(packet)
        
    def _send_waiting_packet(self):
        """送信待ちキューに積まれている DataPacket を送信する"""
        if not self._waiting_packet.is_empty():
            pk = self._waiting_packet.get()
            pk.seq_num = self._send_seq_num.next()
            self.send_packet(pk)
        
    def send_packet(self, packet):
        """Packet を送信する"""
        self._server.send_packet(packet, self.addr)
        if packet.require_ack():
            self._ack_wait_packets[packet.seq_num] = (packet, time.clock())

    def send_acknowledge(self):
        # ACK,NACK を送信する
        ack_seq_nums, nack_seq_nums = self._recv_packets.get_seq_nums()
        if len(ack_seq_nums):
            pk = ctrl.Ack()
            pk.seq_nums = ack_seq_nums
            self.send_packet(pk)
        if len(nack_seq_nums):
            pk = ctrl.Nack()
            pk.seq_nums = nack_seq_nums
            self.send_packet(pk)

    def update(self):
        """定期的に更新する"""
        # TIMEOUT を超えた ACK 待ちパケットを破棄する
        now = time.clock()
        for seq_num, p in list(self._ack_wait_packets.items()):
            pk, t = p
            if now - t > _ACK_TIMEOUT:
                del self._ack_wait_packets[seq_num]
                logger.server.info(
                    'ACK_TIMEOUT {addr} {packet}', addr=self._addr, packet=pk)
        # 待機中のパケットを送信する
        self._send_waiting_packet()
