# -*- coding: utf8 -*-

from pycraft.network import ApplicationPacket
from .buffer import ByteBuffer


class Packet(ApplicationPacket):
    
    BUFFER_FACTORY = ByteBuffer