# -*- coding: utf8 -*-

import os
import sys
import logging
from pycraft import service, network
from pycraft.console import Console 


def init_logger(root):
    server_log_file = os.path.join(root, 'server.log')
    packet_log_file = os.path.join(root, 'packet.log')

    logging.basicConfig(level=logging.DEBUG)

    logger = logging.getLogger(network.LogName.SERVER)
    logger.propagate = False
    h = logging.FileHandler(server_log_file)
    h.setFormatter(logging.Formatter('%(asctime)-15s:%(levelname)s:%(message)s'))
    logger.addHandler(h)

    logger = logging.getLogger(network.LogName.PACKET)
    logger.propagate = False
    h = logging.FileHandler(packet_log_file)
    h.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(h)


def init_store(database):
    store = service.DataStore(database)
    store.start()
    store.create_table()
    store.terminate()


def dirname(path, n):
    for _ in range(n):
        path = os.path.dirname(path)
    return path


def main():
    host = ''  # このマシンの全IPで接続可能
    port = 19132
    
    root = dirname(sys.argv[0], 3)
    init_logger(root)
    database = os.path.join(root, 'world.db')
    init_store(database)
    store = service.DataStore(database)
    clock = service.Clock()
    server = network.Server((host, port), service.Handler(store, clock))
    console = Console(server)
    server.run(console.start)
    print('Server terminated.')


if __name__ == '__main__':
    main()
