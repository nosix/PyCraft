# -*- coding: utf8 -*-

class Language:
    
    __slots__ = ['_format']

    def __init__(self, format_dict):
        self._format = format_dict

    def tr(self, message, params):
        return self._format[message].format(*params) \
            if message in self._format else message
