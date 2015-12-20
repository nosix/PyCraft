# -*- coding: utf8 -*-

import io
import re
import sys
from collections import defaultdict
from pycraft.network import packet_classes
from pycraft.network.container import SplitPacketContainer
from pycraft.network import protocol
from pycraft.network.packet.base import StreamRaw
from pycraft.network.packet.data import EncapsulatedPacket as EncapPacket
from pycraft.service.whole.handler.packet.both import Batch
from pycraft.service.whole.handler.protocol import Protocol
from pycraft.service.part.item.base import Item
from pycraft.service.whole.handler import packet
from pycraft.service.primitive.values import MetaData


protocol_serv = Protocol(
    38, '0.13.1', packet_classes(packet.both, packet.recv, packet.send))


class DecodeException(Exception):
    
    pass


class PacketAnalyzer:
    
    def __init__(self):
        self.formatter = Formatter(4)
        self._re = re.compile('(.+)([<>])(.+)')
        self._session = defaultdict(Session)
    
    def run(self):
        for r in self._analyze():
            for l in self.formatter.format(r):
                print(l)

    def _analyze(self):
        with io.open(sys.stdin.fileno()) as sin:
            for line in sin:
                for addr, inout, buffer in self._re.findall(line):
                    s = self._session[addr]
                    try:
                        yield s.analyze_packet(inout, buffer)
                    except DecodeException:
                        pass


class Session:
    
    cur_id = 0

    @classmethod
    def _next_id(cls):
        cls.cur_id += 1
        return cls.cur_id
        
    def __init__(self):
        self._id = self._next_id()
        self._split_packets = {
            '>' : SplitPacketContainer(),
            '<' : SplitPacketContainer()}

    def _update_meta(self, data, inout, packet, buffer):
        data['_client'] = self._id
        data['_inout'] = inout
        data['_buffer'] = buffer
        data['_class'] = packet.__class__.__name__

    def analyze_packet(self, inout, buffer):
        data = {}
        packet = protocol.net.packet(bytes.fromhex(buffer))
        self._decode_packet(packet, buffer, inout, 'NetworkPacket')
        self._update_meta(data, inout, packet, buffer)
        for name, value in self._analyze_attrs(inout, packet):
            data[name] = self._analyze_value(inout, value)
        return data
    
    def _analyze_attrs(self, inout, packet):
        for name in packet.__slots__:
            if not name.startswith('_') and hasattr(packet, name):
                value = getattr(packet, name)
                yield name, value

    def _analyze_value(self, inout, value):
        if isinstance(value, set) or isinstance(value, list):
            return self._analyze_list(inout, value)
        if isinstance(value, bytes):
            return value.hex()
        if isinstance(value, EncapPacket):
            return self._analyze_encapsulated_packet(inout, value)
        if isinstance(value, Item) or isinstance(value, MetaData):
            return str(value)
        return value

    def _analyze_list(self, inout, values):
        return list(self._analyze_value(inout, v) for v in values)
    
    def _analyze_encapsulated_packet(self, inout, packet):
        data = {}
        if getattr(packet, 'reliability') != None:
            data['_reliability'] = getattr(packet, 'reliability')
        if getattr(packet, 'message') != None:
            data['_message'] = getattr(packet, 'message')
        if getattr(packet, 'order') != None:
            data['_order'] = getattr(packet, 'order')
        if getattr(packet, 'split') != None:
            data['_split'] = getattr(packet, 'split')
        buffer = packet.buffer.hex()
        self._update_meta(data, inout, packet, buffer)
        if packet.split:
            packet = self._split_packets[inout].concat(packet)
            if packet == None:
                return data
        buffer = packet.buffer.hex()
        packet = protocol.app.packet(bytes.fromhex(buffer))
        if not isinstance(packet, StreamRaw):
            self._decode_packet(packet, buffer, inout, 'NetworkPacket')
            self._update_meta(data, inout, packet, buffer)
            for name, value in self._analyze_attrs(inout, packet):
                data[name] = self._analyze_value(inout, value)
            return data
        packet = protocol_serv.packet(bytes.fromhex(buffer))
        if isinstance(packet, StreamRaw):
            self._update_meta(data, inout, packet, buffer)
            data['payload'] = buffer
            return data
        self._decode_packet(packet, buffer, inout, 'ServicePacket')
        self._update_meta(data, inout, packet, buffer)
        if not isinstance(packet, Batch):
            for name, value in self._analyze_attrs(inout, packet):
                data[name] = self._analyze_value(inout, value)
            return data
        data['packets'] = list(
            self._analyze_batch(inout, payload)
                for payload in packet.payloads)
        return data

    def _analyze_batch(self, inout, payload):
        data = {}
        buffer = payload.hex()
        packet = protocol_serv.packet(bytes.fromhex(buffer))
        if isinstance(packet, StreamRaw):
            self._update_meta(data, inout, packet, buffer)
            data['payload'] = buffer
            return data
        self._decode_packet(packet, buffer, inout, 'ServicePacket')
        self._update_meta(data, inout, packet, buffer)
        for name, value in self._analyze_attrs(inout, packet):
            data[name] = self._analyze_value(inout, value)
        return data

    def _decode_packet(self, packet, buffer, inout, kind):
        try:
            packet.decode()
            assert len(packet.buffer()) == 0
        except Exception as e:
            print(packet.__class__.__name__, '%r' % e, packet.buffer().hex())
            print(kind, inout, buffer)
            raise DecodeException()


class Formatter:
    
    def __init__(self, indent):
        self._indent = ' ' * indent
        self._hide = set(['skin', 'chunk_data', 'namded_tag'])
        self._hide.update(set([
#              'EncapsulatedPacket', 'Ack', 'Nack', 'Ping', 'Pong',
#              'OpenConnectionRequest1', 'OpenConnectionReply1',
#              'OpenConnectionRequest2', 'OpenConnectionReply2',
#              'ClientConnect', 'ServerHandshake', 'ClientHandshake',
#              'RecipeData',
#              'FullChunkData',
#              'MovePlayer', 'Animate',
#              'MoveEntity', 'SetEntityMotion', 'PlayerAction', 
#              'SetEntityData', 'Unknown1',
            ]))

    def format(self, values):
        if not self._does_filter(values):
            values = self._filter(values)
            if values != None:
                return self._format(values, '')
        return []

    def _does_filter(self, values):
        return '_class' in values and values['_class'] in self._hide

    def _filter(self, src):
        dst = dict(src)
        if 'packets' in src:
            filtered = (
                self._filter(v) for v in src['packets']
                    if not self._does_filter(v))
            dst['packets'] = list(v for v in filtered if v != None)
            if len(dst['packets']) == 0:
                return None
        return dst
        
    def _format(self, values, indent):
        head = []
        if '_reliability' in values:
            head.append('r=' + str(values['_reliability']))
        if '_message' in values:
            head.append('m' + str(values['_message']))
        if '_order' in values:
            head.append('o' + str(values['_order']))
        if '_split' in values:
            head.append('s' + str(values['_split']))
        if len(head) > 0:
            yield indent + ' '.join(head)
        head = []
        if '_client' in values:
            head.append(str(values['_client']))
        if '_inout' in values:
            head.append(values['_inout'])
        if '_class' in values:
            head.append(values['_class'])
        if len(head) > 0:
            yield indent + ' '.join(head)
        for key, value in values.items():
            key = str(key)
            if not key.startswith('_'):
                for l in self._format_value(key, value, indent + self._indent):
                    yield l
    
    def _format_value(self, key, value, indent):
        if key in self._hide:
            return
        if isinstance(value, dict):
            if key != None:
                yield indent + key + ':'
                indent += self._indent
            for l in self._format(value, indent):
                yield l
            return
        if isinstance(value, list):
            if key != None:
                yield indent + key + ':'
                indent += self._indent
            for v in value:
                for l in self._format_value(None, v, indent):
                    yield l
            return
        if key != None:
            yield indent + key + ': ' + str(value)
        else:
            yield indent + str(value)


if __name__ == '__main__':
    analyzer = PacketAnalyzer()
    analyzer.run()