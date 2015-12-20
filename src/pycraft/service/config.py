# -*- coding: utf8 -*-

class Config(dict):
    
    def __init__(self):
        self.seed = 3
        self.max_player_num = 20
        self.spawn_mob = True
        self.scratch_port = 42001
        self.scratch_network = '192.168.197.0/24'

    def __getattr__(self, name):
        if name in self:
            return self[name]


instance = Config()
