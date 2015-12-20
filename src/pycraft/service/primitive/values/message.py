# -*- coding: utf8 -*-

class Message(object):
    
    class Esc:
        PREFIX = str(b'\xc2\xa7', encoding='utf8')
    
        BLACK = PREFIX + '0';
        DARK_BLUE = PREFIX + '1'
        DARK_GREEN = PREFIX + '2'
        DARK_AQUA = PREFIX + '3'
        DARK_RED = PREFIX + '4'
        DARK_PURPLE = PREFIX + '5'
        GOLD = PREFIX + '6'
        GRAY = PREFIX + '7'
        DARK_GRAY = PREFIX + '8'
        BLUE = PREFIX + '9'
        GREEN = PREFIX + 'a'
        AQUA = PREFIX + 'b'
        RED = PREFIX + 'c'
        LIGHT_PURPLE = PREFIX+ 'd' 
        YELLOW = PREFIX + 'e'
        WHITE = PREFIX + 'f'

        OBFUSCATED = PREFIX + 'k'
        BOLD = PREFIX + 'l'
        STRIKETHROUGH = PREFIX + 'm'
        UNDERLINE = PREFIX + 'n'
        ITALIC = PREFIX + 'o'

        RESET = PREFIX + 'r'

    def __init__(self, message, *params, is_raw=True):
        self._message = message
        self._params = params
        self._is_raw = is_raw

    def clone(self):
        o = self.__class__.__new__(self.__class__)
        o._is_raw = self._is_raw
        o._message = self._message
        o._params = list(self._params)
        return o

    is_raw = property(lambda self: self._is_raw)

    def tr(self, lang):
        if self._is_raw:
            # Translate to raw text 
            return lang.tr(self._message, self._params), []
        else:
            return self._message, self._params
