# -*- coding: utf8 -*-

import logging


class Logger:
    
    __slots__ = ['_logger']

    def __init__(self, name):
        self._logger = logging.getLogger(name)

    def debug(self, msg, **kwargs):
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug(msg.format_map(kwargs))

    def info(self, msg, **kwargs):
        if self._logger.isEnabledFor(logging.INFO):
            self._logger.info(msg.format_map(kwargs))

    def warning(self, msg, **kwargs):
        if self._logger.isEnabledFor(logging.WARNING):
            self._logger.warning(msg.format_map(kwargs))
    
    def error(self, msg, **kwargs):
        if self._logger.isEnabledFor(logging.ERROR):
            self._logger.error(msg.format_map(kwargs))
    
    def critical(self, msg, **kwargs):
        if self._logger.isEnabledFor(logging.CRITICAL):
            self._logger.critical(msg.format_map(kwargs))