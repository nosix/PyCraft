# -*- coding: utf8 -*-

class GameMode:

    SURVIVAL = 0
    CREATIVE = 1
    ADVENTURE = 2
    SPECTATOR = 3


class Difficulty:

    PEACEFUL = 0
    EASY = 1
    NORMAL = 2
    HARD = 3


class ContainerWindowID:
    
    INVENTORY = 0
    ARMOR = 0x78
    CREATIVE = 0x79
    CRAFTING = 0x7a


class EntityType:
    
    CHICKEN = 10
    COW = 11
    PIG = 12
    SHEEP = 13
    WOLF = 14
    VILLAGER = 15
    MOOSHROOM = 16
    SQUID = 17
    # FAULT 18
    BAT = 19
    # FAULT 20-31
    ZOMBIE = 32
    CREEPER = 33
    SKELTON = 34
    SPIDER = 35
    ZOMBIE_PIGMEN = 36
    SLIME = 37
    ENDERMAN = 38
    SILVERFISH = 39
    CAVE_SPIDER = 40
    GHASTS = 41
    MAGMA_CUBE = 42
    # FAULT 43-63
    UNKNOWN = 64  # TODO: 正しい名前に直す
    TNT = 65
    UNKNOWN = 77  # TODO: 正しい名前に直す
    # FAULT 78-79
    ARROWS = 80
    BALL1 = 81  # TODO: 正しい名前に直す
    BALL2 = 82  # TODO: 正しい名前に直す
    # FAULT 83
    MINECART = 84
    BOAT = 90


class EntityEventID:

    HURT_ANIMATION = 2
    DEATH_ANIMATION = 3
    TAME_FAIL = 6
    TAME_SUCCESS = 7
    SHAKE_WET = 8
    USE_ITEM = 9
    EAT_GRASS_ANIMATION = 10
    FISH_HOOK_BUBBLE = 11
    FISH_HOOK_POSITION = 12
    FISH_HOOK_HOOK = 13
    FISH_HOOK_TEASE = 14
    SQUID_INK_CLOUD = 15
    AMBIENT_SOUND = 16
    RESPAWN = 17


class LevelEventID:
    
    DOOR_SOUND = 1003


class PlayerActionID:
    
    RESPAWN = 7
