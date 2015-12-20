# -*- coding: utf8 -*-

from collections import defaultdict
from pycraft import network
from pycraft.common import ImmutableMeta
from pycraft.service import logger, config
from pycraft.service.const import ContainerWindowID, PlayerActionID
from pycraft.service.primitive.values import Message
from .listener import WorldEventListener
from .entrance import WorldEntrance
from .player import Player
from .task import TaskID
from .packet import ID, both
from . import protocol


class HandlerComponents(metaclass=ImmutableMeta):
    
    properties = 'listener datastore clock scheduler'


class Handler(network.Handler):
    
    FRAME_RATE = 20

    def __init__(self, datastore, clock):
        super().__init__()
        # Session.addr -> Player.id
        self._addr2id = {}
        # Player.id -> Player
        self._players = {}
        # MainThreadで動くWorldThreadのイベントリスナー
        self._listener = WorldEventListener(self)
        # Entrance
        self._entrance = WorldEntrance(HandlerComponents(
            self._listener, datastore, clock, self.scheduler))
        # 各セッションのプロトコル(Session.addr -> Protocol)
        self._session_protocol = defaultdict(lambda: protocol.default)
        # 各種初期化
        self._init_protocol()
        self._init_scheduler()

    def _init_protocol(self):
        def do_nothing(session, packet):
            pass

        def wrap_handler(handler):
            def handle_if_exists(session, packet):
                player_id = self._addr2id.get(session.addr)
                if player_id != None:
                    handler(packet, player_id)
                else:
                    logger.server.info(
                        '{addr} Player is not found.', session.addr)
            return handle_if_exists

        protocol.default.regist_handlers({
            ID.UNKNOWN3 : do_nothing,
            ID.BATCH : self._handle_batch,
            ID.LOGIN : self._handle_login,
            ID.MOVE_PLAYER :
                wrap_handler(self._handle_move_player),
            ID.ANIMATE :
                wrap_handler(self._handle_animate),
            ID.REMOVE_BLOCK :
                wrap_handler(self._handle_remove_block),
            ID.PLAYER_EQUIPMENT :
                wrap_handler(self._handle_player_equipment),
            ID.USE_ITEM :
                wrap_handler(self._handle_use_item),
            ID.MAKE_ITEM : 
                wrap_handler(self._handle_make_item),
            ID.CONTAINER_CLOSE :
                wrap_handler(self._handle_container_close),
            ID.CONTAINER_SET_SLOT : 
                wrap_handler(self._handle_container_set_slot),
            ID.PLAYER_ACTION :
                wrap_handler(self._handle_player_action),
            ID.TILE_ENTITY_DATA :
                wrap_handler(self._handle_tile_entity_data),
            ID.INTERACT : 
                wrap_handler(self._handle_interact),
            })

    def _init_scheduler(self):
        s = self.scheduler
        s.frame_rate = self.FRAME_RATE
        s.set(TaskID.UPDATE_LISTENER, 1.0)
        s.set(TaskID.UPDATE_ENTRANCE, 1.0)
        s.set(TaskID.UPDATE_TERRAIN, 0.1)
        s.set(TaskID.STORE_BLOCK_ENTITY, 0.2)
        s.set(TaskID.STORE_TERRAIN, 0.2)
        s.set(TaskID.STORE_PLAYER, 0.2)

    def start(self):
        self._entrance.start()

    def terminate(self):
        self._entrance.terminate()

    def update(self):
        self._listener.update()
        self._entrance.update()

    def info(self):
        # MCPE;サーバー名;プロトコルバージョン;MCPEバージョン;ログイン人数;上限
        return 'MCPE;{name};{protocol};{version};{players};{players_max}'.format(
            name='PyCraft',
            protocol=protocol.default.protocol_version,
            version=protocol.default.minecraft_version,
            players=len(self._players),
            players_max=config.max_player_num)

    def open(self, session):
        logger.server.info('open session {session}', session=session)
    
    def close(self, session, reason):
        logger.server.info('close session {session}', session=session)
        if session.addr in self._addr2id:
            player_id = self._addr2id[session.addr]
            player = self._players[player_id]
            self._entrance.remove_player(player_id)
            # プレイヤーの終了処理を行う
            player.close(reason)
            # 全プレイヤーに通知を行う
            self.notify(Message(
                Message.Esc.YELLOW + '%multiplayer.player.left',
                player.name, is_raw=False))
            # プレイヤーを削除する
            del self._players[player_id]
            del self._addr2id[session.addr]
            del self._session_protocol[session.addr]

    def spawn(self, player_id):
        self._entrance.spawn_player(player_id)
        
    def _protocol(self, session):
        return self._session_protocol[session.addr]

    def _packet(self, buffer, session):
        packet = self._protocol(session).packet(buffer)
        packet.decode()
        return packet

    def handle(self, session, packet):
        pk = self._packet(packet.buffer(), session)
        logger.server.debug(
            'H> {addr} {packet}', addr=session.addr, packet=pk)
        self._protocol(session).handle(session, pk)
        if len(pk.buffer()) != 0:
            logger.server.error(
                'Decode did not conclude. [{buffer}]', buffer=pk.buffer())
            raise NotImplementedError()

    def _handle_batch(self, session, packet):
        for buffer in packet.payloads:
            pk = self._packet(buffer, session)
            logger.server.debug(
                'H>> {addr} {packet}', addr=session.addr, packet=pk)
            self._protocol(session).handle(session, pk)
            if len(pk.buffer()) != 0:
                logger.server.error(
                    'Decode did not conclude. [{buffer}]', buffer=pk.buffer())
                raise NotImplementedError()

    def _handle_login(self, session, packet):
        # バージョンチェック
        prot = protocol.shelf[packet.protocol1]
        if prot.protocol_version != packet.protocol1:
            logger.server.info(
                '{addr} Protocol version {ver} is not supported.',
                addr=session.addr, ver=packet.protocol1)
            return
        self._session_protocol[session.addr] = prot
        # 受信情報を保存
        player_id = packet.client_id
        player_name = packet.user_name
        player = Player(self, session, player_id, player_name)
        self._players[player_id] = player
        self._addr2id[session.addr] = player_id
        # 世界にPlayerを追加
        self._entrance.add_player(
            player_id, packet.public_id,
            player_name, packet.skin_name, packet.skin)

    def notify(self, message):
        pk = both.Text()
        pk.type = pk.TYPE_RAW if message.is_raw else pk.TYPE_TRANSLATION 
        pk.message = message
        for player in self._players.values():
            player.direct_text_packet(pk)

    def broadcast(self, func, *args, **kwargs):
        for player in self._players.values():
            func(player, *args, **kwargs)

    def unicast(self, func, player_id, *args, **kwargs):
        if player_id in self._players:
            func(self._players[player_id], *args, **kwargs)

    def _handle_animate(self, packet, player_id):
        player = self._players[player_id]
        pk = player.create_animate_packet(packet.action)
        # 他Playerにアニメーションを通知
        for player in self._players.values():
            player.send_animate(pk)

    def _handle_player_action(self, packet, player_id):
        if packet.action == PlayerActionID.RESPAWN:
            self._entrance.respawn_player(player_id)

    def _handle_move_player(self, packet, player_id):
        # 世界でPlayerを移動
        self._entrance.move_player(player_id, packet.motion, packet.on_ground)

    def _handle_player_equipment(self, packet, player_id):
        # 装具を変更
        self._entrance.equip_item(
            player_id, packet.slot, packet.held_hotbar)

    def _handle_remove_block(self, packet, player_id):
        self._entrance.remove_block(player_id, packet.pos)

    def _handle_use_item(self, packet, player_id):
        if not packet.has_face():
            return
        # アイテムを設置
        self._entrance.put_item(
            player_id, packet.bpos, packet.face, packet.item.id)

    def _handle_make_item(self, packet, player_id):
        assert len(packet.product_items) == 1
        made_item = packet.product_items.pop()
        used_item = packet.material_items
        self._entrance.make_item(player_id, made_item, used_item)

    def _handle_container_close(self, packet, player_id):
        self._entrance.close_container(player_id, packet.window_id)

    def _handle_container_set_slot(self, packet, player_id):
        if (packet.window_id == ContainerWindowID.ARMOR or
                packet.window_id == ContainerWindowID.CRAFTING or
                packet.window_id == ContainerWindowID.CREATIVE):
            return
        self._entrance.edit_container(
            player_id, packet.window_id, packet.slot, packet.item)
    
    def _handle_tile_entity_data(self, packet, player_id):
        self._entrance.edit_sign(packet.pos, packet.named_tag)

    def _handle_interact(self, packet, player_id):
        self._entrance.attack_entity(packet.target, player_id)
