# -*- coding: utf8 -*-

from collections import defaultdict
from pycraft.client import PacketAnalyzer


class TestGenerator:
    
    def __init__(self, send, recv):
        self._send = set(send)
        self._recv = set(recv)
        self._passed = defaultdict(lambda: False)
        self._splited = defaultdict(list)
        self._indent = ' ' * 4

    def format(self, value):
        return self._process_packet(value)

    def _switch_inout(self, inout):
        if inout == '>':
            return self._send, self._gen_send_code
        else:
            return self._recv, self._gen_recv_code

    def _process_packet(self, values):
        check_cls, gen_code = self._switch_inout(values['_inout'])
        if 'packets' in values:
            does_gen = False
            split = None
            cls = []
            for p in values['packets']:
                if '_split' in p:
                    split = (values['_client'], p['_split'][1])
                    if p['_class'] == 'EncapsulatedPacket':
                        self._splited[split].append(values)
                        continue
                if p['_class'] == 'Batch':
                    p = p['payload']
                cls.append(p['_class'])
                if p['_class'] in check_cls:
                    does_gen = True
            if does_gen:
                if split != None:
                    for v in self._splited[split]:
                        for code in gen_code(v, ['SPLIT']):
                            yield code
                for code in gen_code(values, cls):
                    yield code
                for p in values['packets']:
                    for code in self._gen_comment(p):
                        yield code
            elif values['_inout'] == '<':
                self._passed[values['_client']] = True
        else:
            if values['_class'] in check_cls:
                for code in gen_code(values, [values['_class']]):
                    yield code
            elif values['_inout'] == '<':
                self._passed[values['_client']] = True

    def _gen_send_code(self, values, cls):
        yield "# {0}".format(', '.join(cls))
        yield "c{0}.send_buffer(\n{1}'{2}')".format(
            values['_client'], self._indent, values['_buffer'])
    
    def _gen_recv_code(self, values, cls):
        param = ["'" + values['_buffer'] + "'"]
        if self._passed[values['_client']]:
            self._passed[values['_client']] = False
            param.append('sometime=True')
        yield "# {0}".format(', '.join(cls))
        yield "c{0}.assert_buffer_equal(\n{1}{2})".format(
            values['_client'], self._indent, ', '.join(param))

    def _gen_comment(self, values):
        yield "### {0} {1}".format(values['_class'], values['_buffer'])


if __name__ == '__main__':
    import sys
    l = {}
    exec('from pycraft_test.server.test_{0} import send, recv'.format(
            sys.argv[1]), {}, l)
    analyzer = PacketAnalyzer()
    analyzer.formatter = TestGenerator(l['send'], l['recv'])
    analyzer.run()
