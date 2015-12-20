# -*- coding: utf8 -*-

import socket
import selectors
import functools


class Client:
    
    MAX_ERRORS_LEN = 30

    def __init__(self, testcase, server):
        self._testcase = testcase
        self._addr = server.addr
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._send = self._new_send_buffer()
        self._recv = self._new_recv_buffer()
        self._num_of_data_packet = 0
        self._num_of_ack = 0
        self._num_of_nack = 0
        self._last_seq_num = -1
        self._lost_seq_num = []
        self._pass_seq_num = []
        self._errors = []

    def _new_send_buffer(self):
        send_selector = selectors.DefaultSelector()
        send_queue = []
        def send(buffer):
            send_queue.append(buffer)
            while len(send_queue) > 0:
                for key, _ in send_selector.select(0):
                    key.data(key.fileobj)
        def handle_send_packet(sock):
            if len(send_queue) > 0:
                sock.sendto(bytes.fromhex(send_queue.pop(0)), self._addr)
        send_selector.register(
            self._sock, selectors.EVENT_WRITE, handle_send_packet)
        send_buffer = self._send_buffer(send)
        next(send_buffer)
        return send_buffer

    def _new_recv_buffer(self):
        recv_selector = selectors.DefaultSelector()
        def recv(timeout):
            return (key.data(key.fileobj)
                for key, _ in recv_selector.select(timeout))
        def handle_recv_packet(sock):
            return sock.recv(4096).hex()
        recv_selector.register(
            self._sock, selectors.EVENT_READ, handle_recv_packet)
        recv_buffer = self._recv_buffer(recv)
        next(recv_buffer)
        return recv_buffer

    def __del__(self):
        self._sock.close()

    def _send_buffer(self, send_func):
        while True:
            buffer = yield
            if buffer[0] == '8':
                def triad():
                    n = self._num_of_data_packet
                    for _ in range(3):
                        yield n & 0xFF
                        n >>= 8
                seq_num = bytes(b for b in triad()).hex()
                buffer = buffer[0:2] + seq_num + buffer[8:]
                self._num_of_data_packet += 1
            send_func(buffer)
            yield None

    def _recv_buffer(self, recv_func, timeout=1):
        does_pass = False
        while True:
            if not does_pass:
                does_pass = yield
            bufs = list(recv_func(timeout))
            if len(bufs) == 0:
                if does_pass:
                    does_pass = False
                    yield None
                else:
                    self._testcase.fail(self._error_msg(self._errors))
            else:
                for buf in bufs:
                    if not self._catch_acknowledge(buf):
                        self._check_seq_num(buf)
                        if not does_pass:
                            yield buf
                            does_pass = yield
                            if does_pass:
                                break

    def _catch_acknowledge(self, buf):
        if buf[0:2] == 'c0':
            self._num_of_ack += 1
            return True
        if buf[0:2] == 'a0':
            self._num_of_nack += 1
            return True
        return False

    def _check_seq_num(self, buf, is_pass=False):
        if buf[0:1] == '8':
            seq_num = functools.reduce(
                lambda s, b: s * 256 + b,
                reversed(bytes.fromhex(buf[2:8]), 0))
            for s in range(self._last_seq_num+1, seq_num):
                self._lost_seq_num.append(str(s))
                if is_pass:
                    self._pass_seq_num.append(str(s))
            self._last_seq_num = seq_num
    
    def _error_msg(self, errors):
        # 後ろの空行を取り除く
        while len(errors):
            e = errors.pop()
            if e:
                errors.append(e)
                break
        # メッセージを絞る
        if len(errors) > self.MAX_ERRORS_LEN:
            del errors[1:len(errors)-self.MAX_ERRORS_LEN-1]
        # 情報を追加
        errors.insert(0, 'Packet can not be received.')
        errors.append('{0:d} packet lost: {1}'.format(
            len(self._lost_seq_num), ','.join(self._lost_seq_num)))
        errors.append('{0:d} packet passed: {1}'.format(
            len(self._pass_seq_num), ','.join(self._pass_seq_num)))
        errors.append('Last seq_num: {0:d}'.format(self._last_seq_num))
        return '\n'.join(errors)

    def send_buffer(self, buffer):
        self._send.send(buffer)
    
    def wait(self):
        self._recv.send(True)

    def assert_acknowledge(self):
        self.wait()
        self._testcase.assertEqual(0, self._num_of_nack)
        self._testcase.assertEqual(self._num_of_data_packet, self._num_of_ack)

    def assert_buffer_equal(self, exp, mask=None, cut=None, sometime=False):
        self._errors = []
        if not sometime:
            buf = self._recv.send(False)
            if len(buf) != len(exp):
                self._errors.append(
                    'length ' + str(len(buf)) + ' != ' + str(len(exp)))
                self._errors.append(exp)
                self._errors.append(buf)
            else:
                mbuf = self._mask(buf, mask)
                mexp = self._mask(exp, mask)
                if mbuf != mexp:
                    diff = self._diff(mbuf, mexp)
                    self._errors += \
                        ['', exp, buf, diff, self._diff_summary(diff)]
            if len(self._errors) > 0:
                self._testcase.fail('\n'.join(self._errors))
        else:
            mexp = self._mask(exp, mask)
            self._errors.append(exp)
            min_diff = (len(exp), '', '', '', '')
            self._errors += min_diff[1:]
            while True:
                buf = self._recv.send(False)[0:cut]
                if len(buf) != len(exp):
                    del self._errors[-len(min_diff)+1:]
                    self._errors.append(buf)
                    self._errors += min_diff[1:]
                else:
                    mbuf = self._mask(buf, mask)
                    if mbuf != mexp:
                        diff = self._diff(mbuf, mexp)
                        diff_n = diff.count('^')
                        if diff_n < min_diff[0]:
                            min_diff = (
                                diff_n, 'Most similar:',
                                buf, diff, self._diff_summary(diff))
                        del self._errors[-len(min_diff)+1:]
                        self._errors.append(buf)
                        self._errors.append(diff)
                        self._errors += min_diff[1:]
                    else:
                        break

    def _mask(self, buf, mask):
        if mask != None:
            buf = list(buf)
            for s,l in mask:
                buf[s:s+l] = '*' * l
            buf = ''.join(buf)
        return buf

    def _diff(self, buf, exp):
        diff = ''.join([
            ('  ' if e == a else '^^') 
                for e, a in zip(
                    bytes.fromhex(exp.replace('*', '0')),
                    bytes.fromhex(buf.replace('*', '0')))])
        diff = ''.join([
            ('*' if e == '*' and a == '*' else d)
                for e, a, d in zip(exp, buf, diff)])
        return diff

    def _diff_summary(self, diff):
        def get_range():
            start = None
            for i, d in enumerate(diff):
                if start == None:
                    if d == '^':
                        start = i
                else:
                    if d != '^':
                        yield (start, i-start)
                        start = None
            if start != None:
                yield (start, len(diff)-start)
        diff_range = ','.join([str(r) for r in get_range()])
        return diff_range.replace(' ', '')
