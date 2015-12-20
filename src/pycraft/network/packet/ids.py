# -*- coding: utf8 -*-

class ID:
    
    # Control Packet
    UNCONNECTED_PING = 0x01
    UNCONNECTED_PONG = 0x1c
    OPEN_CONNECTION_REQUEST_1 = 0x05
    OPEN_CONNECTION_REPLY_1 = 0x06
    OPEN_CONNECTION_REQUEST_2 = 0x07
    OPEN_CONNECTION_REPLY_2 = 0x08
    UNCONNECTED_PING_OPEN_CONNECTIONS = 0x02
    ADVERTISE_SYSTEM = 0x1d
    ACK = 0xc0
    NACK = 0xa0
    
    # Data Packet
    DATA_PACKET_0 = 0x80
    DATA_PACKET_1 = 0x81
    DATA_PACKET_2 = 0x82
    DATA_PACKET_3 = 0x83
    DATA_PACKET_4 = 0x84
    DATA_PACKET_5 = 0x85
    DATA_PACKET_6 = 0x86
    DATA_PACKET_7 = 0x87
    DATA_PACKET_8 = 0x88
    DATA_PACKET_9 = 0x89
    DATA_PACKET_A = 0x8A
    DATA_PACKET_B = 0x8B
    DATA_PACKET_C = 0x8C
    DATA_PACKET_D = 0x8D
    DATA_PACKET_E = 0x8E
    DATA_PACKET_F = 0x8F
    
    # Application Packet
    CLIENT_CONNECT = 0x09
    SERVER_HANDSHAKE = 0x10
    CLIENT_HANDSHAKE = 0x13
    CLIENT_DISCONNECT = 0x15
    PING = 0x00
    PONG = 0x03
