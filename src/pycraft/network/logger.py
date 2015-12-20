# -*- coding: utf8 -*-

from pycraft.common import Logger


class LogName:
    
    SERVER = 'pycraft.network.server'
    PACKET = 'pycraft.network.packet'


server = Logger(LogName.SERVER)
packet = Logger(LogName.PACKET)
