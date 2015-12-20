# -*- coding: utf8 -*-

from .base import Item, BlockItem
from .ids import ID, NAMES
from . import armor, tool, things


class ItemFactory:
    
    MATERIAL_DURABILITY = dict(
        GOLDEN = 33,
        WOODEN = 60,
        STONE = 132,
        IRON = 251,
        DIAMOND = 1562,
    )

    @classmethod
    def _material_name(cls, id_):
        return NAMES[id_].partition('_')[0]

    # id -> guard
    ARMOR_PROPERTY = {
        ID.LEATHER_CAP : 1,
        ID.LEATHER_TUNIC : 3,
        ID.LEATHER_PANTS : 2,
        ID.LEATHER_BOOTS : 1,
        ID.CHAIN_HELMET : 1,
        ID.CHAIN_CHESTPLATE : 5,
        ID.CHAIN_LEGGINGS : 4,
        ID.CHAIN_BOOTS : 1,
        ID.IRON_HELMET : 2,
        ID.IRON_CHESTPLATE : 6,
        ID.IRON_LEGGINGS : 5,
        ID.IRON_BOOTS : 2,
        ID.DIAMOND_HELMET : 3,
        ID.DIAMOND_CHESTPLATE : 8,
        ID.DIAMOND_LEGGINGS : 6,
        ID.DIAMOND_BOOTS : 3,
        ID.GOLD_HELMET : 1,
        ID.GOLD_CHESTPLATE : 5,
        ID.GOLD_LEGGINGS : 3,
        ID.GOLD_BOOTS : 1
        }

    @classmethod
    def _get_armor_factory(cls, id_):
        guard = cls.ARMOR_PROPERTY[id_]
        def new_armor(id_, count, attr, unknown):
            return armor.Armor(id_, 0, guard, attr, unknown)
        return new_armor

    TOOL = {
        ID.IRON_SHOVEL,
        ID.IRON_PICKAXE,
        ID.IRON_AXE,
        ID.FLINT_AND_STEEL,
        ID.BOW,
        ID.IRON_SWORD,
        ID.WOODEN_SWORD,
        ID.WOODEN_SHOVEL,
        ID.WOODEN_PICKAXE,
        ID.WOODEN_AXE, 
        ID.STONE_SWORD,
        ID.STONE_SHOVEL,
        ID.STONE_PICKAXE,
        ID.STONE_AXE,
        ID.DIAMOND_SWORD,
        ID.DIAMOND_SHOVEL,
        ID.DIAMOND_PICKAXE,
        ID.DIAMOND_AXE,
        ID.GOLDEN_SWORD,
        ID.GOLDEN_SHOVEL,
        ID.GOLDEN_PICKAXE,
        ID.GOLDEN_AXE,
        ID.SHEARS
    }

    # kind -> class
    TOOL_CLASS = dict(
        PICKAXE = tool.Pickaxe,
        AXE = tool.Axe,
        SWORD = tool.Sword
    )

    @classmethod
    def _tool_class(cls, id_):
        kind = NAMES[id_].partition('_')[-1]
        return cls.TOOL_CLASS[kind] if kind in cls.TOOL_CLASS else tool.Tool

    TOOL_DURABILITY = {
        ID.BOW : 385,
        ID.FLINT_AND_STEEL : 65,
        ID.SHEARS : 239,
    }

    @classmethod
    def _tool_durability(cls, id_):
        return cls.TOOL_DURABILITY[id_] if id_ in cls.TOOL_DURABILITY \
            else cls.MATERIAL_DURABILITY[cls._material_name(id_)]

    MATERIAL_ATTACK = dict(
        STONE = 1,
        IRON = 2,
        DIAMOND = 3
    )

    @classmethod
    def _tool_atack(cls, id_):
        material = cls._material_name(id_)
        return cls.MATERIAL_ATTACK.get(material, 0)

    @classmethod
    def _get_tool_factory(cls, id_):
        tool_cls = cls._tool_class(id_)
        durability = cls._tool_durability(id_)
        attack = cls._tool_atack(id_)
        def new_tool(id_, count, attr, unknown):
            return tool_cls(id_, durability, attack, attr, unknown)
        return new_tool
        
    def __init__(self):
        # Default is BlockItem or Item
        self._items = dict(
            (id_, (BlockItem if id_ < 256 else Item))
                for id_ in NAMES.keys())
        # Armors
        self._items.update(
            (id_, self._get_armor_factory(id_)) 
                for id_ in self.ARMOR_PROPERTY.keys())
        # Tools
        self._items.update(
            (id_, self._get_tool_factory(id_))
                for id_ in self.TOOL)
        # Special items
        self._items[ID.SIGN] = things.Sign
        self._items[ID.WOODEN_DOOR] = things.WoodenDoor
        self._items[ID.IRON_DOOR] = things.IronDoor

    def __call__(self, id_, count=1, attr=0, unknown=0):
        return self._items[id_](id_, count, attr, unknown)


new_item = ItemFactory()
