# -*- coding: utf8 -*-

from ..util import ServerTestCase 


send = [
    'UnconnectedPing',
    'OpenConnectionRequest1',
    'OpenConnectionRequest2',
    'ClientConnect',
    'ClientHandshake',
    'Login',
    'ClientDisconnect',
    ]

recv = [
    'UnconnectedPong',
    'OpenConnectionReply1',
    'OpenConnectionReply2',
    'ServerHandshake',
    'PlayStatus',
    'StartGame',
    'SetDifficulty',
    'AdventureSettings',
    'SetHealth',
    'ContainerSetContent',
    'SetSpawnPosition',
    'Respawn',
    'MovePlayer',
    'SetEntityData',
    'SetEntityMotion',
    'Text',
    'Disconnect',
    ]


class TestGame(ServerTestCase):

    def test_0000(self):
        """World一覧画面(UnconnectedPing/Pong)"""
        with self.run_server('0000') as s:
            c = s.new_client()

            c.assert_acknowledge()