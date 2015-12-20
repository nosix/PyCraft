# -*- coding: utf8 -*-

import io
import sys


class Tshark2PyCraft:
    """tshark で生成したファイルを PacketAnalyzer に対応する形式に変換する
    
    $ tshark.exe -nr [name].pcap -T fields -e ip.addr -e data > [name].txt
    $ cat [name].txt | tshark2pycraft.py [host_ip]
    """
    
    def __init__(self, host_ip):
        self._host_ip = host_ip

    def convert(self):
        with io.open(sys.stdin.fileno()) as sin:
            for line in sin:
                line = line.strip()
                if not line:
                    continue
                try:
                    addr, data = line.split()
                    src, dst = addr.split(',')
                    if dst == self._host_ip:
                        inout = '>'
                        client = src
                    else:
                        inout = '<'
                        client = dst
                    print('{client}{inout}{data}'.format(
                            client=client, inout=inout, data=data))
                except:
                    pass


if __name__ == '__main__':
    import os
    if len(sys.argv) <= 1:
        print('Usage: {0} host_ip'.format(os.path.basename(sys.argv[0])))
    else:
        Tshark2PyCraft(sys.argv[1]).convert()
