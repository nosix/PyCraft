# -*- coding: utf8 -*-

import sys
import traceback
import textwrap
from threading import Thread


class Console:
    
    def __init__(self, server):
        self._server = server
        self._thread = Thread(target=self.run)
    
    def start(self):
        self._thread.start()

    def usage(self):
        print(textwrap.dedent("""\
        Usage:
            help or ? - Print this document.
            stop or q - Stop server.
        """))

    def execute(self, cmd):
        if cmd in ('?', 'help'):
            self.usage()
            return True
        if cmd in ('q', 'stop'):
            return False

    def run(self):
        self.usage()
        try:
            while True:
                argv = input('> ').split()
                if len(argv) > 0 and not self.execute(argv[0]):
                    break
        except:
            traceback.print_exc(file=sys.stdout)
        self._server.terminate()
        print('Server is terminating...')
