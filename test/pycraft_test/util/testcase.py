# -*- coding: utf8 -*-

from shutil import copy
from threading import Thread
from unittest import TestCase
from cProfile import Profile
from pycraft.service import config, DataStore, StaticClock
from .server import TestServer


def profile(filename):
    """Decorator function"""
    def profile(func):
        def profile(*args, **kwargs):
            profiler = Profile()
            try:
                return profiler.runcall(func, *args, **kwargs)
            finally:
                profiler.dump_stats(filename)
        return profile
    return profile

    
class ServerTestCase(TestCase):

    def run_server(self, test_id):
        db_id = test_id[:2]
        src = str(db_id) + '.db.data'
        dst = str(test_id) + '.db'
        copy(src, dst)
        # Config初期化
        config.update(dict(
            spawn_mob = False,
            ))
        # DataStore初期化
        store = DataStore(dst)
        store.start()
        store.create_table()
        # Clock初期化
        clock = StaticClock()
        # Server初期化
        server = TestServer(DataStore(dst), clock, self)
        server.init_logger(test_id)
        class TestServerThread(Thread):
            @profile(test_id + '.stats')
            def run(self):
                server.start(self)
        thread = TestServerThread()
        thread.start()
        return server
