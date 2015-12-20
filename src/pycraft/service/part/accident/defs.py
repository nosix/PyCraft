# -*- coding: utf8 -*-

from .base import Accident


class Fall(Accident):
    
    DEATH_MESSAGE = 'death.fell.accident.generic'

    def __init__(self, entity):
        super().__init__(entity)

    def get_msg_params(self):
        return [self._entity.name]

    def direc_of_dropping(self, motion_law):
        return motion_law.direc_when_fall()


class AttackByPlayer(Accident):
    
    DEATH_MESSAGE = 'death.attack.player'

    __slots__ = ['_attacked_by']

    def __init__(self, entity, attacked_by):
        super().__init__(entity)
        self._attacked_by = attacked_by

    def get_msg_params(self):
        return [self._entity.name, self._attacked_by.name]

    def direc_of_dropping(self, motion_law):
        return motion_law.direc_when_remove(
            self._entity.pos, self._attacked_by.pos)


class AttackByMob(Accident):

    DEATH_MESSAGE = 'death.attack.mob'

    __slots__ = ['_attacked_by']

    def __init__(self, entity, attacked_by):
        super().__init__(entity)
        self._attacked_by = attacked_by

    def get_msg_params(self):
        return [self._entity.name, self._attacked_by.name]

    def direc_of_dropping(self, motion_law):
        return motion_law.direc_when_remove(
            self._entity.pos, self._attacked_by.pos)
