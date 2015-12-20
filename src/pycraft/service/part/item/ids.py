# -*- coding: utf8 -*-

from pycraft.common.util import names


class ID:
    
    AIR = 0
    STONE = 1
    GRASS = 2
    DIRT = 3
    COBBLESTONE = 4
    PLANKS = 5
    SAPLING = 6
    BEDROCK = 7
    FLOWING_WATER = 8
    STILL_WATER = 9
    FLOWING_LAVA = 10
    LAVA = 11
    SAND = 12
    GRAVEL = 13
    GOLD_ORE = 14
    IRON_ORE = 15
    COAL_ORE = 16
    LOG = 17
    LEAVES = 18
    SPONGE = 19
    GLASS = 20
    LAPIS_ORE = 21
    LAPIS_BLOCK = 22
    SANDSTONE = 24
    NOTE_BLOCK = 25
    BED_BLOCK = 26
    POWERED_RAIL = 27
    DETECTOR_RAIL = 28
    WEB = 30
    TALL_GRASS = 31
    BUSH = 32
    WOOL = 35
    DANDELION = 37
    RED_FLOWER = 38
    BROWN_MUSHROOM = 39
    RED_MUSHROOM = 40
    GOLD_BLOCK = 41
    IRON_BLOCK = 42
    DOUBLE_SLAB = 43
    SLAB = 44
    BRICKS = 45
    TNT = 46
    BOOKSHELF = 47
    MOSS_COBBLESTONE = 48
    OBSIDIAN = 49
    TORCH = 50
    FIRE = 51
    MOB_SPAWNER = 52
    OAK_STAIRS = 53
    CHEST = 54
    DIAMOND_ORE = 56
    DIAMOND_BLOCK = 57
    CRAFTING_TABLE = 58
    WHEAT_BLOCK = 59
    FARMLAND = 60
    FURNACE = 61
    BURNING_FURNACE = 62
    SIGN_POST = 63
    WOODEN_DOOR_BLOCK = 64
    LADDER = 65
    RAIL = 66
    STONE_STAIRS = 67
    WALL_SIGN = 68
    LEVER = 69
    STONE_PRESSURE_PLATE = 70
    IRON_DOOR_BLOCK = 71
    WOODEN_PRESSURE_PLATE = 72
    REDSTONE_ORE = 73
    GLOWING_REDSTONE_ORE = 74
    REDSTONE_TORCH_ON = 76
    STONE_BUTTON = 77
    SNOW = 78
    ICE = 79
    SNOW_BLOCK = 80
    CACTUS = 81
    CLAY_BLOCK = 82
    REEDS = 83
    FENCE = 85
    PUMPKIN = 86
    NETHERRACK = 87
    SOUL_SAND = 88
    GLOWSTONE = 89
    JACK_O_LANTERN = 91
    CAKE_BLOCK = 92
    TRAPDOOR = 96
    STONE_BRICK = 98
    BROWN_MUSHROOM_CAP = 99
    RED_MASHROOM_CAP = 100
    IRON_BARS = 101
    GLASS_PANE = 102
    MELON_BLOCK = 103
    PUMPKIN_STEM = 104
    MELON_STEM = 105
    VINE = 106
    FENCE_GATE = 107
    BRICK_STAIRS = 108
    STONE_BRICK_STAIRS = 109
    MYCELIUM = 110
    WATER_LILY = 111
    NETHER_BRICK_BLOCK = 112
    NETHER_BRICK_FENCE = 113
    NETHER_BRICK_STAIRS = 114
    ENCHANTMENT_TABLE = 116
    END_PORTAL_FRAME = 120
    END_STONE = 121
    REDSTONE_LAMP_OFF = 123
    WOODEN_SLAB_BLOCK = 126
    SANDSTONE_STAIRS = 128
    EMERALD_ORE = 129
    TRIPWIRE_HOOK = 131
    EMERALD_BLOCK = 133
    SPRUCE_WOODEN_STAIRS = 134
    BIRCH_WOODEN_STAIRS = 135
    JUNGLE_WOODEN_STAIRS = 136
    COBBLESTONE_WALL = 139
    CARROT_BLOCK = 141
    POTATOES_BLOCK = 142
    WOODEN_BUTTON = 143
    ANVIL = 145
    TRAPPED_CHEST = 146
    WEIGHTED_PRESSURE_PLATE_LIGHT = 147
    WEIGHTED_PRESSURE_PLATE_HEAVY = 148
    DAYLIGHT_SENSOR = 151
    REDSTONE_BLOCK = 152
    NETHER_QUARTZ_ORE = 153
    QUARTZ_BLOCK = 155
    QUARTZ_STAIRS = 156
    DOUBLE_WOODEN_SLAB = 157
    WOODEN_SLAB = 158
    STAINED_CLAY = 159
    LEAVES2 = 161
    LOG2 = 162
    ACACIA_WOODEN_STAIRS = 163
    DARK_OAK_WOODEN_STAIRS = 164
    IRON_TRAPDOOR = 167
    HAY_BALE = 170
    CARPET = 171
    HARDENED_CLAY = 172
    COAL_BLOCK = 173
    PACKED_ICE = 174
    DOUBLE_PLANT = 175
    FENCE_GATE_SPRUCE = 183
    FENCE_GATE_BIRCH = 184
    FENCE_GATE_JUNGLE = 185
    FENCE_GATE_DARK_OAK = 186
    FENCE_GATE_ACACIA = 187
    GRASS_PATH = 198  # END_ROD?
    PODZOL = 243
    BEETROOT_BLOCK = 244
    STONECUTTER = 245
    GLOWING_OBSIDIAN = 246
    NETHER_REACTOR = 247
    
    # Normal Item IDs
    IRON_SHOVEL = 256
    IRON_PICKAXE = 257
    IRON_AXE = 258
    FLINT_AND_STEEL = 259
    APPLE = 260
    BOW = 261
    ARROW = 262
    COAL = 263
    DIAMOND = 264
    IRON_INGOT = 265
    GOLD_INGOT = 266
    IRON_SWORD = 267
    WOODEN_SWORD = 268
    WOODEN_SHOVEL = 269
    WOODEN_PICKAXE = 270
    WOODEN_AXE = 271
    STONE_SWORD = 272
    STONE_SHOVEL = 273
    STONE_PICKAXE = 274
    STONE_AXE = 275
    DIAMOND_SWORD = 276
    DIAMOND_SHOVEL = 277
    DIAMOND_PICKAXE = 278
    DIAMOND_AXE = 279
    STICKS = 280
    BOWL = 281
    MUSHROOM_STEW = 282
    GOLDEN_SWORD = 283
    GOLDEN_SHOVEL = 284
    GOLDEN_PICKAXE = 285
    GOLDEN_AXE = 286
    STRING = 287
    FEATHER = 288
    GUNPOWDER = 289
    WOODEN_HOE = 290
    STONE_HOE = 291
    IRON_HOE = 292
    DIAMOND_HOE = 293
    GOLDEN_HOE = 294
    SEEDS = 295
    WHEAT = 296
    BREAD = 297
    LEATHER_CAP = 298
    LEATHER_TUNIC = 299
    LEATHER_PANTS = 300
    LEATHER_BOOTS = 301
    CHAIN_HELMET = 302
    CHAIN_CHESTPLATE = 303
    CHAIN_LEGGINGS = 304
    CHAIN_BOOTS = 305
    IRON_HELMET = 306
    IRON_CHESTPLATE = 307
    IRON_LEGGINGS = 308
    IRON_BOOTS = 309
    DIAMOND_HELMET = 310
    DIAMOND_CHESTPLATE = 311
    DIAMOND_LEGGINGS = 312
    DIAMOND_BOOTS = 313
    GOLD_HELMET = 314
    GOLD_CHESTPLATE = 315
    GOLD_LEGGINGS = 316
    GOLD_BOOTS = 317
    FLINT = 318
    RAW_PORKCHOP = 319
    COOKED_PORKCHOP = 320
    PAINTING = 321
    GOLDEN_APPLE = 322
    SIGN = 323
    WOODEN_DOOR = 324
    BUCKET = 325
    MINECART = 328
    IRON_DOOR = 330
    REDSTONE = 331
    SNOWBALL = 332
    BOAT = 333
    LEATHER = 334
    BRICK = 336
    CLAY = 337
    SUGARCANE = 338
    PAPER = 339
    BOOK = 340
    SLIMEBALL = 341
    EGG = 344
    COMPASS = 345
    FISHING_ROD = 346
    CLOCK = 347
    GLOWSTONE_DUST = 348
    RAW_FISH = 349
    COOKED_FISH = 350
    DYE = 351
    BONE = 352
    SUGAR = 353
    CAKE = 354
    BED = 355
    COOKIE = 357
    SHEARS = 359
    MELONS = 360
    PUMPKIN_SEEDS = 361
    MELON_SEEDS = 362
    RAW_BEEF = 363
    STEAK = 364
    RAW_CHICKEN = 365
    COOKED_CHICKEN = 366
    ROTTEN_FLESH = 367
    BLAZE_ROD = 369
    GHAST_TEAR = 370
    GOLD_NUGGET = 371
    NETHER_WART_SEEDS = 372
    GLASS_BOTTLE = 374
    SPIDER_EYE = 375
    FERMENTED_SPIDER_EYE = 376
    BLAZE_POWDER = 377
    MAGMA_CREAM = 378
    BREWING_STAND = 379
    GLISTERING_MELON = 382
    SPAWN_EGG = 383
    EXPERIENCE_POTION = 384
    EMERALD = 388
    FLOWER_POT = 390
    CARROTS = 391
    POTATOES = 392
    BAKED_POTATOES = 393
    POISONOUS_POTATO = 394
    GOLDEN_CARROT = 396
    SKELETON_HEAD = 397
    PUMPKIN_PIE = 400
    ENCHANTED_BOOK = 403
    NETHER_BRICK = 405
    NETHER_QUARTZ = 406
    UNKNOWN_411 = 411
    UNKNOWN_412 = 412
    UNKNOWN_413 = 413
    UNKNOWN_414 = 414
    UNKNOWN_415 = 415
    UNKNOWN_427 = 427
    UNKNOWN_428 = 428
    UNKNOWN_429 = 429
    UNKNOWN_430 = 430
    UNKNOWN_431 = 431
    CAMERA = 456
    BEETROOT = 457
    BEETROOT_SEEDS = 458
    BEETROOT_SOUP = 459
    UNKNOWN_460 = 460
    UNKNOWN_461 = 461
    UNKNOWN_462 = 462
    UNKNOWN_463 = 463
    UNKNOWN_466 = 466


NAMES = names(ID)