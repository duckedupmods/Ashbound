"""Brings one of the older gate dungeons over from E:/Ashbound the way the Silk Archive came: its masonry blocks
(port_city's machinery), its props as the Blender meshes tools/blender/<gate>_props.py made (OBJ block models),
its monsters on Epic Fight's skeletons (efmob.py; stats and hitboxes read from the old classes), its loot, and its
layout: the old .bin with every vanilla block swapped for ours, so nothing vanilla shows but bedrock and water.

Everything new is listed in data files the add-on reads, so no new code per dungeon:
  src/main/resources/ashbound/gate_blocks.json   GateBlocks.java   (masonry + props)
  src/main/resources/ashbound/gate_mobs.json     GateMobs.java     (monsters)

    blender -b -P tools/blender/cellar_props.py     (the meshes, first)
    python tools/port_gate.py cellar [blocks] [props] [mobs] [lair]     (all four when none is named)
"""
import collections
import gzip
import json
import math
import os
import re
import struct
import sys

import port_weapons as P
import port_city as PC
import efmob as E

OLD = "E:/Ashbound/src/main/"
OJ = OLD + "java/com/snoringwalrus/ashbound/"
OLD_SRC = E.SRC
OLAIR = OLD + "resources/data/ashbound/lair/"
STAGED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lairs", "stage", "src", "main", "resources", "data", "ashbound", "lair") + "/"


def lair_src(lair):
    """the EF-scale rebuild (tools/lairs) when there is one, else the old dungeon"""
    return STAGED if os.path.exists(STAGED + lair + ".bin") else OLAIR
OLOOT = OLD + "resources/data/ashbound/loot_table/chests/"
REG = P.GAME + "src/main/resources/ashbound/"
A = P.ASSETS
FACING_Y = {"north": 0, "east": 90, "south": 180, "west": 270}
DIRS = {"north": (0, 0, -1), "south": (0, 0, 1), "west": (-1, 0, 0), "east": (1, 0, 0)}
LEFT_VANILLA = {"bedrock", "barrier", "water", "air", "cave_air", "lava"}   # allowed to stay


# ---------------------------------------------------------------- the gates

def P_(name, kind, title, **kw):
    return dict(name=name, kind=kind, title=title, **kw)


GATES = {
    "cellar": dict(
        lair="gate_cellar",
        blocks=[(["cellar_brick", "cellar_brick_stairs", "cellar_brick_slab", "cellar_brick_wall", "wet_cellar_brick",
                  "wine_brick", "mouldy_brick"], "minecraft:deepslate_bricks"),
                (["cellar_flags", "cellar_flag_stairs", "cellar_flag_slab"], "minecraft:stone_bricks"),
                (["cellar_silt"], "minecraft:mud"),
                (["cask_oak", "cask_oak_stairs", "cask_oak_slab", "cask_hoop", "cask_head"], "minecraft:dark_oak_planks"),
                (["sluice_iron"], "minecraft:iron_block")],
        props=[P_("cellar_cask", "facing", "Wine Cask", box=[1, 0, 1, 15, 14, 15], sound="wood", color="color_brown", strength=2),
               P_("cellar_cask_upright", "plain", "Standing Cask", box=[2, 0, 2, 14, 15, 14], sound="wood", color="color_brown", strength=2),
               P_("cask_rack", "facing", "Cask Rack", sound="wood", color="color_brown", strength=2),
               P_("bottle_rack", "facing", "Bottle Rack", sound="wood", color="color_brown", strength=1.5),
               P_("cellar_lamp", "plain", "Cellar Lamp", box=[4, 3, 4, 12, 16, 12], sound="lantern", color="metal", strength=2, light=15, solid=False),
               P_("cellar_sconce", "facing", "Cellar Sconce", box=[3, 2, 3, 13, 15, 13], sound="lantern", color="metal", strength=2, light=14, solid=False),
               P_("cellar_chain", "chain", "Rusted Chain", sound="chain", color="metal", strength=3, solid=False),
               P_("cellar_grille", "bars", "Rusted Grille", sound="metal", color="metal", strength=4),
               P_("cask_fence", "fence", "Cask Oak Rail", sound="wood", color="color_brown", strength=2),
               P_("sluice_grate", "trapdoor", "Sluice Grate", sound="metal", color="metal", strength=4),
               P_("cellar_coffer", "coffer", "Cellar Coffer", sound="wood", color="color_brown", strength=2.5),
               P_("cooper_bench", "facing", "Cooper's Bench", box=[1, 0, 3, 15, 10, 13], sound="wood", color="color_brown", strength=2),
               P_("wine_spill", "plain", "Spilt Wine", box=[2, 0, 2, 14, 1, 14], sound="glass", color="color_red", strength=0.3, solid=False)],
        swap={"barrel": "cellar_cask", "iron_chain": "cellar_chain", "chain": "cellar_chain", "iron_bars": "cellar_grille",
              "dark_oak_fence": "cask_fence", "dark_oak_planks": "cask_oak", "dark_oak_stairs": "cask_oak_stairs",
              "mud": "cellar_silt", "red_carpet": "wine_spill", "iron_trapdoor": "sluice_grate", "chest": "cellar_coffer",
              "anvil": "cooper_bench", "grindstone": "cooper_bench", "smithing_table": "cooper_bench"},
        mobs={"sodden_reveller": {}, "cask_brute": {}, "drowned_vintner": {},
              "cellar_eel": dict(rig="spider", k=1.0, joints={"body": "Root", "neck": "Head", "jaw": "Head", "seg1": "Stomach", "seg2": "Stomach",
                                                       "seg3": "Stomach", "tail": "Stomach"}),
              "barrel_mimic": dict(rig="spider", key=True, joints={"body": "Root", "lid": "Head", "tongue": "Head", "tongue_tip": "Head",
                                                                   "arm_fl": "LL1", "fore_fl": "LL1", "arm_fr": "RL1", "fore_fr": "RL1",
                                                                   "arm_bl": "LL4", "fore_bl": "LL4", "arm_br": "RL4", "fore_br": "RL4"}),
              "cask_mother": dict(boss=True)},
        debris=["cellar_brick", "cask_hoop", "cask_oak", "wet_cellar_brick", "mouldy_brick"],
    ),
    "gallows": dict(
        lair="gate_gallows",
        blocks=[(["gallows_timber", "gallows_timber_stairs", "gallows_timber_slab", "tarred_planks", "tarred_plank_stairs",
                  "tarred_plank_slab", "notice_planks"], "minecraft:dark_oak_planks"),
                (["hill_fieldstone", "hill_fieldstone_stairs", "hill_fieldstone_slab", "hill_fieldstone_wall"], "minecraft:stone_bricks"),
                (["hill_earth"], "minecraft:coarse_dirt"), (["dead_turf"], "minecraft:grass_block"),
                (["hangmans_tar"], "minecraft:mud"), (["gibbet_iron"], "minecraft:iron_block")],
        props=[P_("tallow_lamp", "plain", "Tallow Lamp", box=[3, 0, 3, 13, 12, 13], sound="lantern", color="metal", strength=1.5, light=14),
               P_("hemp_rope", "plain", "Noose", box=[5, 0, 5, 11, 16, 11], sound="wool", color="wood", strength=0.8, solid=False),
               P_("gibbet_bars", "bars", "Gibbet Straps", sound="metal", color="metal", strength=5),
               P_("gibbet_plate", "trapdoor", "Gibbet Plate", sound="metal", color="metal", strength=5),
               P_("gallows_trapdoor", "trapdoor", "Drop Hatch", sound="wood", color="color_black", strength=3),
               P_("gallows_rail", "fence", "Gallows Rail", sound="wood", color="color_gray", strength=2),
               P_("drop_lever", "facing", "Drop Lever", box=[3, 0, 2, 13, 12, 14], sound="wood", color="metal", strength=3),
               P_("gallows_sign", "facing", "Notice Post", box=[3, 0, 3, 13, 15, 13], sound="wood", color="color_gray", strength=1.5),
               P_("gallows_thorn", "plain", "Gallows Thorn", box=[3, 0, 3, 13, 12, 13], sound="grass", color="color_brown", strength=0.2, solid=False),
               P_("straw_bale", "facing", "Straw Bale", box=[1, 0, 2, 15, 10, 14], sound="grass", color="color_yellow", strength=0.5),
               P_("tar_cauldron", "plain", "Tar Pot", box=[2, 0, 2, 14, 12, 14], sound="metal", color="color_black", strength=3),
               P_("gallows_coffer", "coffer", "Hangman's Strongbox", sound="wood", color="color_black", strength=2.5),
               P_("stall_counter", "plain", "Market Counter", box=[0, 0, 0, 16, 14, 16], sound="wood", color="color_brown", strength=1.5)]
              + [P_("awning_" + c, "facing", "%s Awning" % t, sound="wool", color=mc, strength=0.8)
                 for c, t, mc in (("red", "Red", "color_red"), ("grey", "Grey", "color_gray"), ("black", "Black", "color_black"),
                                  ("brown", "Brown", "color_brown"), ("pale", "Pale", "color_light_gray"))]
              + [P_("drape_" + c, "facing", "%s Drape" % t, box=[0, 6, 0, 16, 16, 16], sound="wool", color=mc, strength=0.8, solid=False)
                 for c, t, mc in (("red", "Red", "color_red"), ("grey", "Grey", "color_gray"), ("black", "Black", "color_black"),
                                  ("brown", "Brown", "color_brown"), ("pale", "Pale", "color_light_gray"))],
        swap={"coarse_dirt": "hill_earth", "dirt_path": "hill_earth", "gravel": "hill_earth", "mossy_cobblestone": "hill_fieldstone",
              "cobblestone": "hill_fieldstone", "iron_chain": "cellar_chain", "chain": "cellar_chain", "iron_bars": "gibbet_bars",
              "iron_trapdoor": "gibbet_plate", "dark_oak_trapdoor": "gallows_trapdoor", "spruce_trapdoor": "stall_counter",
              "dark_oak_fence": "gallows_rail", "dead_bush": "gallows_thorn", "hay_block": "straw_bale", "cauldron": "tar_cauldron",
              "dark_oak_sign": "gallows_sign", "lever": "drop_lever", "stripped_dark_oak_log": "gallows_timber",
              "barrel": "cellar_cask_upright", "chest": "gallows_coffer", "dark_oak_planks": "tarred_planks", "dark_oak_slab": "tarred_plank_slab"},
        mobs={"the_dropped": {}, "noose_walker": {}, "tar_witch": {}, "cutpurse": {}, "gibbet_knight": dict(key=True), "hangman": dict(boss=True)},
    ),
    "rotwood": dict(
        lair="gate_rotwood",
        blocks=[(["rotwood_bark", "root_wall", "black_briar"], "minecraft:dark_oak_wood"),
                (["rotwood_planks", "rotwood_plank_stairs", "rotwood_plank_slab"], "minecraft:dark_oak_planks"),
                (["rot_loam"], "minecraft:coarse_dirt"), (["mycelium_threads"], "minecraft:mycelium"), (["spore_moss"], "minecraft:moss_block"),
                (["glowcap"], "minecraft:shroomlight"), (["shelf_fungus"], "minecraft:mushroom_stem"),
                (["glade_stone", "glade_stone_stairs", "glade_stone_slab"], "minecraft:stone_bricks")],
        made=[("glowcap_stem", "stem", "minecraft:mushroom_stem", "Glowcap Stem", "axe")],
        props=[P_("glowcap_cluster", "plain", "Glowcaps", box=[2, 0, 2, 14, 12, 14], sound="fungus", color="color_purple", strength=0.3, light=11, solid=False),
               P_("glow_bracket", "facing", "Glowing Bracket", box=[0, 4, 0, 16, 14, 16], sound="fungus", color="color_purple", strength=0.5, light=10),
               P_("shelf_bracket", "facing", "Shelf Fungus", box=[0, 3, 0, 16, 14, 16], sound="fungus", color="color_orange", strength=0.5),
               P_("dead_campfire", "plain", "Cold Campfire", box=[1, 0, 1, 15, 6, 15], sound="stone", color="stone", strength=1.5),
               P_("hunter_stake", "facing", "Skull Stake", box=[5, 0, 5, 11, 16, 11], sound="bone_block", color="color_light_gray", strength=1.0),
               P_("rot_coffer", "coffer", "Root-Bound Coffer", sound="wood", color="color_brown", strength=2.5),
               P_("rotwood_rail", "fence", "Rotwood Rail", sound="wood", color="color_gray", strength=2)],
        swap={"podzol": "rot_loam", "coarse_dirt": "rot_loam", "dirt_path": "rot_loam", "mushroom_stem": "glowcap_stem",
              "chest": "rot_coffer", "spruce_fence": "rotwood_rail", "campfire": "dead_campfire", "lever": "hunter_stake"},
        mobs={"the_rooted": {}, "bark_wight": {}, "rot_seer": {},
              "thorn_crawler": dict(rig="spider", joints=dict({"body": "Root", "head": "Head", "jaw": "Head", "whip_l": "Head", "whip_r": "Head",
                                                               "abdomen": "Stomach"},
                                                              **{"leg_%d" % i: ("LL%d" % (i + 1) if i < 4 else "RL%d" % (i - 3)) for i in range(8)})),
              "rot_stag": dict(rig="spider", key=True, joints={"body": "Root", "neck": "Head", "tail": "Stomach", "leg_fl": "LL1", "leg_fr": "RL1",
                                                               "leg_bl": "LL4", "leg_br": "RL4"}),
              "mossking": dict(boss=True)},
    ),
    "crypt": dict(
        lair="gate_crypt",
        blocks=[(["crypt_stone", "crypt_stone_stairs", "crypt_stone_slab", "crypt_bricks", "crypt_brick_stairs", "crypt_brick_slab",
                  "crypt_brick_wall", "crypt_tiles", "crypt_tile_stairs", "burial_niche"], "minecraft:stone_bricks"),
                (["grave_soil"], "minecraft:coarse_dirt"), (["grave_wax"], "minecraft:honeycomb_block"),
                (["coffin_iron", "silver_grating"], "minecraft:iron_block")],
        props=[P_("vigil_candles", "plain", "Vigil Candles", box=[1, 0, 1, 15, 10, 15], sound="candle", color="color_yellow", strength=0.5, light=13),
               P_("crypt_candles", "plain", "Church Candles", box=[4, 0, 4, 12, 10, 12], sound="candle", color="color_yellow", strength=0.5, light=12),
               P_("crypt_pew", "facing", "Abbey Pew", box=[0, 0, 0, 16, 8, 16], sound="wood", color="color_brown", strength=2),
               P_("grave_railing", "bars", "Grave Railing", sound="metal", color="metal", strength=4),
               P_("vault_bars", "bars", "Vault Bars", sound="metal", color="metal", strength=6),
               P_("crypt_lantern", "lantern", "Abbey Lantern", sound="lantern", color="metal", strength=2, light=14),
               P_("crypt_bell", "plain", "Vault Bell", box=[3, 0, 3, 13, 16, 13], sound="metal", color="gold", strength=4),
               P_("bone_pile", "plain", "Bone Pile", box=[1, 0, 1, 15, 6, 15], sound="bone_block", color="color_light_gray", strength=1),
               P_("burial_shroud", "plain", "Burial Shroud", box=[2, 0, 1, 14, 2, 15], sound="wool", color="color_light_gray", strength=0.3, solid=False),
               P_("reliquary", "coffer", "Reliquary", sound="wood", color="color_brown", strength=3)],
        swap={"mud": "grave_soil", "candle": "crypt_candles", "iron_bars": "grave_railing", "iron_chain": "cellar_chain", "chain": "cellar_chain",
              "dark_oak_log": "rotwood_bark", "lantern": "crypt_lantern", "dark_oak_fence": "gallows_rail", "chest": "reliquary",
              "light_gray_carpet": "burial_shroud", "dark_oak_planks": "tarred_planks", "barrel": "cellar_cask_upright", "bone_block": "bone_pile",
              "skeleton_skull": "bone_pile", "bell": "crypt_bell", "dark_oak_stairs": "crypt_pew"},
        mobs={"grave_rat": {}, "ghoul": {}, "coffin_knight": {}, "mourner": {}, "gravedigger": dict(key=True), "pale_abbot": dict(boss=True)},
    ),
    "plague": dict(
        lair="gate_plague",
        blocks=[(["limewash", "stained_limewash", "plague_cross", "limewash_stairs", "limewash_slab", "limewash_wall"], "minecraft:calcite"),
                (["ward_tiles", "ward_tile_stairs", "ward_tile_slab"], "minecraft:stone_bricks"),
                (["tar_planks", "tar_plank_stairs", "tar_plank_slab", "tar_timber"], "minecraft:dark_oak_planks"),
                (["linen_sheet"], "minecraft:white_wool"), (["green_tonic"], "minecraft:moss_block")],
        made=[("ward_bricks", "bricks", "minecraft:stone_bricks", "Ward Bricks", "pickaxe"),
              ("cracked_ward_bricks", "cracked", "minecraft:cracked_stone_bricks", "Cracked Ward Bricks", "pickaxe"),
              ("dark_ward_tiles", "tiles", "minecraft:deepslate_tiles", "Dark Ward Tiles", "pickaxe"),
              ("verdigris_plate", "copper", "minecraft:weathered_cut_copper", "Verdigris Plate", "pickaxe"),
              ("verdigris_plate_slab", "slab:verdigris_plate", "minecraft:weathered_cut_copper_slab", "Verdigris Plate Slab", "pickaxe")],
        props=[P_("quicklime", "plain", "Quicklime Heap", box=[1, 0, 1, 15, 8, 15], sound="sand", color="quartz", strength=0.6),
               P_("lime_lamp", "plain", "Lime Lamp", box=[4, 2, 4, 12, 16, 12], sound="lantern", color="color_light_green", strength=1.5, light=14),
               P_("ward_bars", "bars", "Verdigris Bars", sound="metal", color="warped_stem", strength=5),
               P_("apothecary_shelf", "facing", "Apothecary Shelf", sound="wood", color="color_black", strength=1.5),
               P_("apothecary_jar", "plain", "Apothecary Jar", box=[3, 0, 3, 13, 14, 13], sound="decorated_pot", color="terracotta_white", strength=1),
               P_("alembic", "plain", "Alembic", box=[3, 0, 3, 13, 15, 13], sound="glass", color="color_light_green", strength=0.8, light=6),
               P_("sick_cot_head", "facing", "Sick Cot", box=[0, 0, 0, 16, 9, 16], sound="wood", color="wool", strength=1),
               P_("sick_cot_foot", "facing", "Sick Cot", box=[0, 0, 0, 16, 9, 16], sound="wood", color="wool", strength=1),
               P_("ward_linen", "plain", "Soiled Linen", box=[1, 0, 1, 15, 2, 15], sound="wool", color="wool", strength=0.3, solid=False)],
        swap={"stone_bricks": "ward_bricks", "tuff_bricks": "ward_bricks", "cracked_stone_bricks": "cracked_ward_bricks",
              "deepslate_tiles": "dark_ward_tiles", "polished_deepslate": "dark_ward_tiles", "cobbled_deepslate": "dark_ward_tiles",
              "weathered_cut_copper": "verdigris_plate", "weathered_cut_copper_slab": "verdigris_plate_slab", "smooth_stone_slab": "ward_tile_slab",
              "dark_oak_planks": "tar_planks", "dark_oak_trapdoor": "gallows_trapdoor", "dark_oak_fence": "gallows_rail", "coarse_dirt": "grave_soil",
              "barrel": "cellar_cask_upright", "chiseled_bookshelf": "apothecary_shelf", "decorated_pot": "apothecary_jar", "brewing_stand": "alembic",
              "light_gray_carpet": "ward_linen", "white_carpet": "ward_linen", "iron_trapdoor": "gibbet_plate", "iron_bars": "ward_bars",
              "iron_chain": "cellar_chain", "chain": "cellar_chain", "cauldron": "tar_cauldron", "smithing_table": "cooper_bench", "chest": "gallows_coffer"},
        mobs={"bell_leper": {}, "bloated_patient": {}, "lime_friar": {}, "orderly": {}, "plague_doctor": dict(key=True), "surgeon": dict(boss=True)},
    ),
    "foundry": dict(
        lair="gate_foundry",
        blocks=[(["soot_bricks", "soot_brick_stairs", "soot_brick_slab", "soot_brick_wall"], "minecraft:polished_blackstone_bricks"),
                (["black_slate", "black_slate_stairs", "black_slate_slab"], "minecraft:polished_blackstone"),
                (["cold_slag"], "minecraft:basalt"), (["searing_blackstone"], "minecraft:magma_block"),
                (["kiln_iron", "rusted_kiln_iron"], "minecraft:iron_block"), (["furnace_grate"], "minecraft:shroomlight")],
        made=[("cracked_soot_bricks", "crack:soot_bricks", "minecraft:cracked_polished_blackstone_bricks", "Cracked Soot Bricks", "pickaxe"),
              ("soot_tiles", "soot_tiles", "minecraft:deepslate_tiles", "Soot Tiles", "pickaxe")],
        props=[P_("brazier", "plain", "Fire Basket", box=[2, 0, 2, 14, 16, 14], sound="metal", color="color_orange", strength=3, light=15),
               P_("coal_fire", "plain", "Coal Fire", box=[1, 0, 1, 15, 6, 15], sound="stone", color="color_orange", strength=1.5, light=15),
               P_("foundry_anvil", "facing", "Smith's Anvil", box=[2, 0, 2, 14, 13, 14], sound="anvil", color="metal", strength=5),
               P_("bloomery", "facing", "Bloomery", box=[1, 0, 1, 15, 16, 15], sound="stone", color="color_red", strength=3.5, light=13),
               P_("kiln_coffer", "coffer", "Kiln Strongbox", sound="metal", color="metal", strength=4)],
        swap={"blackstone": "black_slate", "polished_blackstone": "black_slate", "polished_blackstone_stairs": "black_slate_stairs",
              "polished_deepslate": "black_slate", "polished_blackstone_bricks": "soot_bricks", "deepslate_bricks": "soot_bricks",
              "nether_bricks": "soot_bricks", "chiseled_polished_blackstone": "soot_bricks",
              "polished_blackstone_brick_stairs": "soot_brick_stairs", "polished_blackstone_brick_wall": "soot_brick_wall",
              "cracked_polished_blackstone_bricks": "cracked_soot_bricks", "cracked_deepslate_bricks": "cracked_soot_bricks",
              "deepslate_tiles": "soot_tiles", "basalt": "cold_slag", "smooth_basalt": "cold_slag", "polished_basalt": "cold_slag",
              "magma_block": "searing_blackstone", "waxed_copper_grate": "furnace_grate", "iron_chain": "cellar_chain", "chain": "cellar_chain",
              "iron_bars": "gibbet_bars", "lantern": "crypt_lantern", "hay_block": "straw_bale", "blast_furnace": "bloomery",
              "anvil": "foundry_anvil", "chest": "kiln_coffer"},
        mobs={"slagling": {}, "riveter": {}, "bellows_priest": {}, "crucible_bearer": dict(key=True),
              "ossric": dict(boss=True, entity=("Ossric", 5.0, 13.0, True))},
    ),
    "ossuary": dict(
        lair="gate_ossuary",
        blocks=[(["bone_bricks", "bone_brick_stairs", "bone_brick_slab", "bone_brick_wall", "skull_wall", "femur_stack", "bone_pit"], "minecraft:bone_block"),
                (["brass_plating"], "minecraft:copper_block"), (["engine_floor", "engine_floor_stairs", "engine_floor_slab"], "minecraft:polished_deepslate")],
        made=[("marrow_rock", "marrow_rock", "minecraft:deepslate", "Marrow Rock", "pickaxe"),
              ("bone_ash", "bone_ash", "minecraft:soul_soil", "Bone Ash", "shovel"),
              ("brass_grate", "brass_grate", "minecraft:copper_grate", "Brass Grate", "pickaxe")],
        props=[P_("soul_lamp", "plain", "Soul Lamp", box=[4, 0, 4, 12, 13, 12], sound="bone_block", color="color_light_blue", strength=1.5, light=13),
               P_("skull_lamp", "facing", "Skull Lamp", box=[4, 0, 4, 12, 12, 12], sound="bone_block", color="color_light_gray", strength=1, light=10),
               P_("soul_flame", "plain", "Soul Fire", box=[1, 0, 1, 15, 8, 15], sound="wool", color="color_light_blue", strength=0, light=10, solid=False),
               P_("soul_pyre", "plain", "Bone Pyre", box=[1, 0, 1, 15, 8, 15], sound="bone_block", color="color_light_blue", strength=1.5, light=14),
               P_("ossuary_lantern", "lantern", "Engine Lantern", sound="lantern", color="color_yellow", strength=2, light=12),
               P_("grind_wheel", "facing", "Grinding Wheel", box=[2, 0, 2, 14, 14, 14], sound="stone", color="stone", strength=2.5),
               P_("bone_saw", "facing", "Bone Saw", box=[1, 0, 1, 15, 14, 15], sound="metal", color="metal", strength=3)],
        swap={"deepslate": "marrow_rock", "blackstone": "marrow_rock", "polished_blackstone": "black_slate", "polished_blackstone_bricks": "soot_bricks",
              "polished_basalt": "cold_slag", "soul_soil": "bone_ash", "soul_fire": "soul_flame", "waxed_oxidized_copper_grate": "brass_grate",
              "waxed_weathered_copper_grate": "brass_grate", "waxed_weathered_copper": "verdigris_plate", "waxed_weathered_cut_copper": "verdigris_plate",
              "waxed_exposed_cut_copper": "brass_plating", "waxed_exposed_copper": "brass_plating", "iron_block": "kiln_iron",
              "iron_chain": "cellar_chain", "chain": "cellar_chain", "iron_bars": "gibbet_bars", "skeleton_skull": "skull_lamp",
              "candle": "crypt_candles", "soul_lantern": "ossuary_lantern", "dark_oak_log": "tar_timber", "stripped_dark_oak_log": "tar_timber",
              "grindstone": "grind_wheel", "stonecutter": "bone_saw", "chest": "reliquary"},
        mobs={"stitched": {}, "wickling": {}, "cantor": {}, "bone_hound": {}, "pallbearer": dict(key=True), "assembler": dict(boss=True)},
    ),
    "frost": dict(
        lair="gate_frost",
        blocks=[(["glacier_ice"], "minecraft:packed_ice"), (["rime_stone"], "minecraft:stone"),
                (["icebound_bricks", "icebound_brick_slab", "icebound_brick_wall"], "minecraft:stone_bricks"),
                (["frost_flagstones", "frost_flagstone_slab", "frost_flagstone_stairs"], "minecraft:stone_bricks")],
        made=[("packed_rime", "packed_rime", "minecraft:packed_ice", "Packed Rime", "pickaxe"),
              ("deep_ice", "deep_ice", "minecraft:blue_ice", "Deep Ice", "pickaxe"),
              ("drift_snow", "drift_snow", "minecraft:snow_block", "Drift Snow", "shovel"),
              ("ice_lantern", "ice_lantern", "minecraft:sea_lantern", "Ice Lantern", "pickaxe")],
        props=[P_("snow_drift", "plain", "Snow Drift", box=[0, 0, 0, 16, 2, 16], sound="snow", color="snow", strength=0.1, solid=False),
               P_("war_banner", "facing", "Procession Banner", box=[6, 0, 6, 10, 16, 10], sound="wood", color="color_blue", strength=1)],
        swap={"packed_ice": "packed_rime", "blue_ice": "deep_ice", "snow_block": "drift_snow", "sea_lantern": "ice_lantern", "snow": "snow_drift",
              "spruce_fence": "gallows_rail", "spruce_planks": "tarred_planks", "stripped_spruce_log": "gallows_timber", "lantern": "crypt_lantern",
              "campfire": "coal_fire", "magma_block": "searing_blackstone", "iron_chain": "cellar_chain", "chain": "cellar_chain",
              "iron_bars": "gibbet_bars", "chest": "reliquary", "barrel": "cellar_cask_upright"},
        mobs={"frostbound": {}, "frostbound_archer": dict(entity=("Frostbound", 1.0, 2.8, False)), "winter_marshal": dict(boss=True),
              "rime_knight": dict(entity=("RimeKnight", 1.1, 3.0, False), stats=dict(hp=95, speed=0.2, dmg=13, armor=14, kb=0.8)),
              "frost_chaplain": dict(entity=("FrostChaplain", 1.0, 2.9, False), stats=dict(hp=50, speed=0.22, dmg=8, armor=6, kb=0.4)),
              "standard_bearer": dict(entity=("StandardBearer", 1.1, 3.0, False), key=True,
                                      stats=dict(hp=180, speed=0.21, dmg=12, armor=14, kb=0.9))},
    ),
    "temple": dict(
        lair="gate_temple",
        blocks=[(["temple_bricks", "temple_brick_stairs", "temple_brick_slab", "temple_brick_wall", "cracked_temple_bricks", "temple_stone",
                  "temple_stone_slab", "temple_tiles", "temple_pillar", "gilded_temple_stone", "carved_temple_stone", "rune_stone"], "minecraft:stone_bricks"),
                (["abyss_stone"], "minecraft:deepslate"), (["mana_crystal_block"], "minecraft:amethyst_block")],
        made=[("pale_crust", "pale_crust", "minecraft:calcite", "Pale Crust", "pickaxe"),
              ("abyss_grit", "abyss_grit", "minecraft:gravel", "Abyss Grit", "shovel"),
              ("drip_rock", "drip_rock", "minecraft:dripstone_block", "Drip Rock", "pickaxe")],
        props=[P_("mana_crystal", "plain", "Mana Crystals", box=[2, 0, 2, 14, 14, 14], sound="amethyst_cluster", color="color_purple", strength=1.5, light=11),
               P_("mana_crystal_hanging", "plain", "Mana Crystals", box=[2, 2, 2, 14, 16, 14], sound="amethyst_cluster", color="color_purple", strength=1.5, light=11),
               P_("mana_crystal_wall", "facing", "Mana Crystals", box=[2, 2, 0, 14, 14, 16], sound="amethyst_cluster", color="color_purple", strength=1.5, light=11),
               P_("skull_pile", "facing", "Skull Pile", box=[0, 0, 0, 16, 14, 16], sound="bone_block", color="color_light_gray", strength=1.5),
               P_("stalagmite", "plain", "Stalagmite", box=[3, 0, 3, 13, 15, 13], sound="dripstone_block", color="terracotta_brown", strength=1.5)],
        swap={"deepslate": "abyss_stone", "cobbled_deepslate": "abyss_stone", "blackstone": "abyss_stone", "smooth_basalt": "abyss_stone",
              "tuff": "temple_stone", "calcite": "pale_crust", "gravel": "abyss_grit", "dripstone_block": "drip_rock", "pointed_dripstone": "stalagmite",
              "iron_chain": "cellar_chain", "chain": "cellar_chain", "soul_lantern": "ossuary_lantern", "candle": "crypt_candles",
              "bone_block": "bone_pile", "chest": "reliquary"},
        mobs={"sentinel": {}, "hollow": {}, "acolyte": {}, "facetaker": dict(key=True),
              "mask_crawler": dict(rig="spider", root="hips", joints={"hips": "Root", "head": "Head", "abdomen": "Stomach", "leg_l0": "LL1",
                                                                     "leg_l1": "LL3", "leg_l2": "LL4", "leg_r0": "RL1", "leg_r1": "RL3", "leg_r2": "RL4"}),
              "sovereign": dict(boss=True)},
    ),
}


def cellar_special(B, p, name, props):
    """the cellar's casks: a hooped stave standing alone (not in a tun's wall) is a cask, in the rack wall a cask in
    its rack facing the aisle; bottle racks face the aisle; a lone cask head is a cask stood on end"""
    x, y, z = p
    cask = ("ashbound:cask_oak", "ashbound:cask_hoop", "ashbound:cask_head")

    def at(q):
        return B.get(q, "minecraft:air").split("[")[0]

    def open_side():
        for f, (dx, dy, dz) in DIRS.items():
            if at((x + dx, y, z + dz)) in ("minecraft:air", "minecraft:water", "minecraft:cave_air"):
                return f
        return None
    if name == "ashbound:cask_hoop":
        tun = at((x, y + 1, z)) in cask or at((x, y - 1, z)) in cask
        if tun:
            return None
        f = open_side()
        if f is None:
            return None
        walls = sum(1 for d in DIRS.values() if at((x + d[0], y, z + d[2])) not in ("minecraft:air", "minecraft:water", "minecraft:cave_air"))
        return "ashbound:%s[facing=%s]" % ("cask_rack" if walls >= 2 else "cellar_cask", f)
    if name == "ashbound:bottle_rack":
        return "ashbound:bottle_rack[facing=%s]" % (open_side() or "north")
    if name == "ashbound:cask_head" and at((x, y - 1, z)) not in cask:
        return "ashbound:cellar_cask_upright"
    if name == "minecraft:barrel" and props.get("facing") in ("up", "down"):
        return "ashbound:cellar_cask_upright"
    return None


WOOL = {"minecraft:red_wool": "red", "minecraft:gray_wool": "grey", "minecraft:black_wool": "black", "minecraft:brown_wool": "brown",
        "minecraft:light_gray_wool": "pale", "minecraft:white_wool": "pale"}
SIGN_FACING = {0: "south", 4: "west", 8: "north", 12: "east"}


def tents(B, p, name):
    """wool roofs (market stalls, camp tents) become canvas: each top block an awning sloping down to its open side
    (across the roof's short span), the hidden blocks under the ridge hollow, the ones hung from an eave its drape"""
    x, y, z = p

    def at(q):
        return B.get(q, "minecraft:air").split("[")[0]

    def wool(q):
        return at(q) in WOOL

    def run(q, dx, dz):
        n, (a, b, c) = 1, q
        for s in (1, -1):
            k = 1
            while wool((a + s * dx * k, b, c + s * dz * k)) and k < 12:
                k += 1
            n += k - 1
        return n

    def slope(q):
        a, b, c = q
        along_x = run(q, 1, 0) <= run(q, 0, 1)
        sides = (("west", -1, 0), ("east", 1, 0)) if along_x else (("north", 0, -1), ("south", 0, 1))
        for f, dx, dz in sides:
            if not wool((a + dx, b, c + dz)):
                return f
        return sides[0][0]
    if name in WOOL:
        colour = WOOL[name]
        if not wool((x, y + 1, z)):
            return "ashbound:awning_%s[facing=%s]" % (colour, slope(p))
        f = slope((x, y + 1, z))
        dx, dz = {"west": (1, 0), "east": (-1, 0), "north": (0, 1), "south": (0, -1)}[f]
        if wool((x + dx, y, z + dz)) and wool((x - dx, y, z - dz)):
            return "minecraft:air"
        if not wool((x - dx, y, z - dz)) and wool((x, y - 1, z)) is False:
            return "ashbound:drape_%s[facing=%s]" % (colour, f)
        return "minecraft:air"
    return None


def gallows_special(B, p, name, props):
    """the stalls' canvas (tents), the hay lying along its axis, the notice posts facing their old way"""
    t = tents(B, p, name)
    if t:
        return t
    if name == "minecraft:hay_block":
        return "ashbound:straw_bale[facing=%s]" % ("east" if props.get("axis") == "x" else "north")
    if name == "minecraft:dark_oak_sign":
        r = int(props.get("rotation", 0))
        return "ashbound:gallows_sign[facing=%s]" % SIGN_FACING[(r + 2) // 4 * 4 % 16]
    return None


OPPOSITE = {"north": "south", "south": "north", "east": "west", "west": "east"}


def rotwood_special(B, p, name, props):
    """a lone glowcap on the floor is a clump of them, one on a trunk's side a glowing bracket; lone shelf fungus is
    a bracket off its trunk; the camp's tents are canvas"""
    x, y, z = p

    def at(q):
        return B.get(q, "minecraft:air").split("[")[0]
    t = tents(B, p, name)
    if t:
        return t
    if name not in ("ashbound:glowcap", "ashbound:shelf_fungus"):
        return None
    if any(at((x + dx, y + dy, z + dz)) == name for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))):
        return None
    bark = [f for f, (dx, dy, dz) in DIRS.items() if at((x + dx, y, z + dz)) == "ashbound:rotwood_bark"]
    below = at((x, y - 1, z))
    if name == "ashbound:glowcap":
        if len(bark) == 1 and below in ("minecraft:air", "minecraft:cave_air"):
            return "ashbound:glow_bracket[facing=%s]" % OPPOSITE[bark[0]]
        if len(bark) <= 1 and below not in ("minecraft:air", "minecraft:cave_air", "ashbound:rotwood_bark"):
            return "ashbound:glowcap_cluster"
        return None
    return "ashbound:shelf_bracket[facing=%s]" % (OPPOSITE[bark[0]] if bark else "north")


def crypt_special(B, p, name, props):
    """the abbey's stairs-for-pews are pews (sat facing away from the high side); the vault bars, cubes in the old
    gate, join up with each other and the walls as bars do"""
    x, y, z = p
    if name == "minecraft:dark_oak_stairs" and props.get("half", "bottom") == "bottom":
        return "ashbound:crypt_pew[facing=%s]" % OPPOSITE.get(props.get("facing", "south"), "north")
    if name == "ashbound:vault_bars":
        sides = {}
        for f, (dx, dy, dz) in DIRS.items():
            n = B.get((x + dx, y, z + dz), "minecraft:air").split("[")[0]
            sides[f] = "true" if n not in ("minecraft:air", "minecraft:cave_air", "minecraft:barrier") else "false"
        return fmt("ashbound:vault_bars", sides)
    if name == "minecraft:black_wall_banner":
        return "minecraft:air"
    return None


def bars_joined(B, p, name):
    """bars that were cubes in the old gate (or vanilla ones we rename) joined up with their neighbours"""
    x, y, z = p
    sides = {}
    for f, (dx, dy, dz) in DIRS.items():
        n = B.get((x + dx, y, z + dz), "minecraft:air").split("[")[0]
        sides[f] = "true" if n not in ("minecraft:air", "minecraft:cave_air", "minecraft:barrier") else "false"
    return fmt(name, sides)


def plague_special(B, p, name, props):
    """the sick-beds are cots in two halves (head and foot), the verdigris grilles join up as bars"""
    if name.endswith("_bed"):
        return "ashbound:sick_cot_%s[facing=%s]" % (props.get("part", "foot"), props.get("facing", "north"))
    if name == "ashbound:verdigris_grille":
        return bars_joined(B, p, "ashbound:ward_bars")
    return None


def foundry_special(B, p, name, props):
    """the fire baskets were two blocks tall: the foot is our brazier (its fire stands up into the block over it)"""
    if name == "ashbound:brazier":
        return "ashbound:brazier" if props.get("part", "0") == "0" else "minecraft:air"
    if name == "minecraft:campfire":
        return "ashbound:coal_fire"
    return None


def ossuary_special(B, p, name, props):
    if name == "minecraft:soul_campfire":
        return "ashbound:soul_pyre"
    return None


def frost_special(B, p, name, props):
    """the camp's tents are canvas; the banners stand facing their old way"""
    t = tents(B, p, name)
    if t:
        return t
    if name == "minecraft:blue_banner":
        r = int(props.get("rotation", 0))
        return "ashbound:war_banner[facing=%s]" % SIGN_FACING[(r + 2) // 4 * 4 % 16]
    return None


def temple_special(B, p, name, props):
    """the mana crystals grow the way they faced: up from the floor, down from the vault, out of a wall; the fire
    baskets were two blocks tall (the foundry's brazier)"""
    if name == "ashbound:mana_crystal":
        f = props.get("facing", "up")
        if f == "up":
            return "ashbound:mana_crystal"
        if f == "down":
            return "ashbound:mana_crystal_hanging"
        return "ashbound:mana_crystal_wall[facing=%s]" % f
    if name == "ashbound:brazier":
        return "ashbound:brazier" if props.get("part", "0") == "0" else "minecraft:air"
    return None


SPECIAL = {"temple": temple_special, "frost": frost_special, "ossuary": ossuary_special, "cellar": cellar_special, "gallows": gallows_special, "rotwood": rotwood_special, "crypt": crypt_special, "plague": plague_special,
           "foundry": foundry_special}


# ---------------------------------------------------------------- data files

def reg(name):
    path = REG + name
    return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else None


def reg_put(name, obj):
    os.makedirs(REG, exist_ok=True)
    with open(REG + name, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1)


def merge(lst, entries, key):
    have = {e[key]: i for i, e in enumerate(lst)}
    for e in entries:
        if e[key] in have:
            lst[have[e[key]]] = e
        else:
            lst.append(e)


def tag(tool, names):
    path = P.GAME + "src/main/resources/data/minecraft/tags/block/mineable/%s.json" % tool
    have = json.load(open(path, encoding="utf-8"))["values"] if os.path.exists(path) else []
    # optional: one name that isn't a block would lose the whole tag, vanilla's blocks too, and nothing could be mined
    known = {v if isinstance(v, str) else v["id"] for v in have}
    P.dump(path, {"replace": False, "values": have + [{"id": "ashbound:" + n, "required": False} for n in names if "ashbound:" + n not in known]})


def loot_self(n):
    P.dump(P.DATA + "loot_table/blocks/%s.json" % n, {"type": "minecraft:block", "pools": [{"rolls": 1, "entries": [
        {"type": "minecraft:item", "name": "ashbound:" + n}], "conditions": [{"condition": "minecraft:survives_explosion"}]}]})


# ---------------------------------------------------------------- blocks

def port_blocks(g):
    names = [b for fam, _ in g["blocks"] for b in fam]
    kinds, nm, nt = PC.assets(names)
    PC.tags(names)
    PC.lang(names)
    entries = []
    for fam, feel in g["blocks"]:
        for b in fam:
            e = {"name": b, "kind": kinds[b], "feel": feel}
            if kinds[b] == "stairs":
                e["base"] = PC.base_of(b, names)
            entries.append(e)
    r = reg("gate_blocks.json") or {"blocks": [], "props": []}
    merge(r["blocks"], entries, "name")
    reg_put("gate_blocks.json", r)
    print("blocks: %d (%d models, %d textures)" % (len(names), nm, nt))


def paint_stem(name):
    """a pale fibrous stem: streaks running up it (side), cut rings (end)"""
    from PIL import Image
    import random
    rnd = random.Random(name)
    side, end = Image.new("RGB", (16, 16)), Image.new("RGB", (16, 16))
    cols = [rnd.randint(-14, 10) for _ in range(16)]
    for x in range(16):
        for y in range(16):
            v = cols[x] + rnd.randint(-5, 5) - (10 if (x + y // 5) % 5 == 0 else 0)
            side.putpixel((x, y), (148 + v, 136 + v, 150 + v))
            r = ((x - 7.5) ** 2 + (y - 7.5) ** 2) ** 0.5
            w = (-24 if r > 7 else 0) + (8 if int(r) % 3 == 0 else 0) + rnd.randint(-4, 4)
            end.putpixel((x, y), (172 + w, 160 + w, 170 + w))
    side.save(P.ASSETS + "textures/block/%s.png" % name)
    end.save(P.ASSETS + "textures/block/%s_top.png" % name)
    return "column"


def _save(img, name):
    img.save(P.ASSETS + "textures/block/%s.png" % name)


def paint_bricks(name, base=(118, 116, 112), mortar=(70, 68, 66), cracked=False):
    """clean dressed bricks, four courses a block, each brick its own shade, a lit top edge and a shadowed foot;
    cracked: dark cracks wandering across a few of them"""
    from PIL import Image
    import random
    rnd = random.Random(name)
    img = Image.new("RGB", (16, 16))
    shade = {}
    for y in range(16):
        row = y // 4
        off = 4 if row % 2 else 0
        for x in range(16):
            bx = (x + off) % 16 // 8
            if y % 4 == 3 or (x + off) % 8 == 7:
                c = [m + rnd.randint(-3, 3) for m in mortar]
            else:
                k = shade.setdefault((row, bx), rnd.randint(-10, 10))
                edge = 8 if y % 4 == 0 else (-6 if y % 4 == 2 and (x + off) % 8 == 6 else 0)
                c = [b + k + edge + rnd.randint(-4, 4) for b in base]
            img.putpixel((x, y), tuple(max(0, min(255, v)) for v in c))
    if cracked:
        for start in ((3, 1), (11, 6), (6, 12)):
            x, y = start
            for _ in range(5):
                if 0 <= x < 16 and 0 <= y < 16:
                    img.putpixel((x, y), tuple(int(m * 0.6) for m in mortar))
                x += rnd.choice((-1, 0, 1))
                y += 1
    _save(img, name)
    return "cube"


def paint_tiles(name, base=(52, 54, 60), grout=(28, 29, 33)):
    """square floor tiles, four a block, each its own shade, worn lighter at the middle"""
    from PIL import Image
    import random
    rnd = random.Random(name)
    img = Image.new("RGB", (16, 16))
    shade = {}
    for y in range(16):
        for x in range(16):
            if x % 8 in (0, 7) and y % 8 in (0, 7) or x % 8 == 7 or y % 8 == 7:
                c = [g + rnd.randint(-2, 2) for g in grout]
            else:
                k = shade.setdefault((x // 8, y // 8), rnd.randint(-6, 6))
                wear = 6 if 2 <= x % 8 <= 4 and 2 <= y % 8 <= 4 else 0
                c = [b + k + wear + rnd.randint(-3, 3) for b in base]
            img.putpixel((x, y), tuple(max(0, min(255, v)) for v in c))
    _save(img, name)
    return "cube"


def paint_copper(name):
    """copper plates gone to verdigris: green-teal bloom over brown metal, seams between plates, a rivet at each corner"""
    from PIL import Image
    import random
    rnd = random.Random(name)
    img = Image.new("RGB", (16, 16))
    for y in range(16):
        for x in range(16):
            if x % 8 == 7 or y % 8 == 7:
                c = (34, 52, 46)
            elif x % 8 in (1, 5) and y % 8 in (1, 5):
                c = (120, 96, 66)
            else:
                g = rnd.random()
                c = (66 + int(g * 22), 120 + int(g * 30), 104 + int(g * 26)) if g > 0.25 else (108, 82, 58)
                c = tuple(v + rnd.randint(-5, 5) for v in c)
            img.putpixel((x, y), c)
    _save(img, name)
    return "cube"


def paint_rock(name, base, fleck=None, spread=10):
    """rough rock or packed ash: mottled in soft blobs, a few flecks (bone chips) in it"""
    from PIL import Image
    import random
    rnd = random.Random(name)
    img = Image.new("RGB", (16, 16))
    blobs = [(rnd.randint(0, 15), rnd.randint(0, 15), rnd.randint(-spread, spread)) for _ in range(7)]
    for y in range(16):
        for x in range(16):
            k = sum(v * max(0, 1 - ((min(abs(x - bx), 16 - abs(x - bx))) ** 2 + (min(abs(y - by), 16 - abs(y - by))) ** 2) / 18) for bx, by, v in blobs)
            c = [b + int(k) + rnd.randint(-4, 4) for b in base]
            if fleck and rnd.random() < 0.06:
                c = [f + rnd.randint(-8, 8) for f in fleck]
            img.putpixel((x, y), tuple(max(0, min(255, v)) for v in c))
    _save(img, name)
    return "cube"


def paint_grate(name, frame=(92, 70, 34), gap=(14, 12, 10)):
    """a cast brass grate: a frame, a lattice of bars, dark between"""
    from PIL import Image
    import random
    rnd = random.Random(name)
    img = Image.new("RGB", (16, 16))
    for y in range(16):
        for x in range(16):
            bar = x in (0, 15) or y in (0, 15) or x % 5 == 0 or y % 5 == 0
            c = [f + rnd.randint(-8, 8) + (10 if bar and (x + y) % 7 == 0 else 0) for f in frame] if bar else [g + rnd.randint(-2, 2) for g in gap]
            img.putpixel((x, y), tuple(max(0, min(255, v)) for v in c))
    _save(img, name)
    return "cube"


def paint_crack(name, src):
    """an existing texture of ours with dark cracks wandering over it"""
    from PIL import Image
    import random
    rnd = random.Random(name)
    img = Image.open(P.ASSETS + "textures/block/%s.png" % src).convert("RGB")
    for start in ((3, 1), (11, 6), (6, 12)):
        x, y = start
        for _ in range(6):
            if 0 <= x < 16 and 0 <= y < 16:
                r, g, b = img.getpixel((x, y))
                img.putpixel((x, y), (r // 3, g // 3, b // 3))
            x += rnd.choice((-1, 0, 1))
            y += 1
    _save(img, name)
    return "cube"


PAINT = {"stem": paint_stem, "bricks": paint_bricks, "cracked": lambda n: paint_bricks(n, cracked=True), "tiles": paint_tiles,
         "copper": paint_copper, "marrow_rock": lambda n: paint_rock(n, (46, 42, 40), (120, 110, 92)),
         "bone_ash": lambda n: paint_rock(n, (88, 84, 78), (170, 162, 140), 8), "brass_grate": paint_grate,
         "packed_rime": lambda n: paint_rock(n, (150, 180, 214), (205, 225, 240), 12),
         "deep_ice": lambda n: paint_rock(n, (70, 120, 196), (150, 190, 236), 14),
         "drift_snow": lambda n: paint_rock(n, (222, 230, 238), None, 6),
         "ice_lantern": lambda n: paint_rock(n, (190, 228, 240), (250, 255, 255), 10),
         "pale_crust": lambda n: paint_rock(n, (196, 192, 184), (226, 222, 214), 8),
         "abyss_grit": lambda n: paint_rock(n, (58, 56, 62), (110, 104, 118), 8),
         "drip_rock": lambda n: paint_rock(n, (112, 84, 62), (150, 118, 90), 10), "soot_tiles": lambda n: paint_tiles(n, (34, 30, 28), (14, 12, 11))}


def port_made(g):
    """blocks the old gate borrowed from vanilla and we now paint ourselves (a giant glowcap's stem)"""
    entries, tools = [], collections.defaultdict(list)
    lang = json.load(open(A + "lang/en_us.json", encoding="utf-8"))
    for name, paint, feel, title, tool in g.get("made", []):
        if paint.startswith("slab:"):   # a slab of a made block: its texture
            base = paint[5:]
            tex = "ashbound:block/" + base
            for suffix, parent in (("", "slab"), ("_top", "slab_top")):
                P.dump(A + "models/block/%s%s.json" % (name, suffix), {"parent": "minecraft:block/" + parent,
                                                                      "textures": {"bottom": tex, "top": tex, "side": tex}})
            P.dump(A + "blockstates/%s.json" % name, {"variants": {"type=bottom": {"model": "ashbound:block/" + name},
                                                                  "type=top": {"model": "ashbound:block/%s_top" % name},
                                                                  "type=double": {"model": "ashbound:block/" + base}}})
            P.dump(A + "models/item/%s.json" % name, {"parent": "ashbound:block/" + name})
            P.dump(P.DATA + "loot_table/blocks/%s.json" % name, {"type": "minecraft:block", "pools": [{"rolls": 1, "entries": [
                {"type": "minecraft:item", "name": "ashbound:" + name, "functions": [{"function": "minecraft:set_count", "count": 2,
                 "conditions": [{"condition": "minecraft:block_state_property", "block": "ashbound:" + name, "properties": {"type": "double"}}]}]}],
                "conditions": [{"condition": "minecraft:survives_explosion"}]}]})
            lang["block.ashbound." + name] = title
            tools[tool].append(name)
            entries.append({"name": name, "kind": "slab", "feel": feel})
            continue
        shape = paint_crack(name, paint[6:]) if paint.startswith("crack:") else PAINT[paint](name)
        tex = "ashbound:block/" + name
        if shape == "column":
            model = {"parent": "minecraft:block/cube_column", "textures": {"side": tex, "end": tex + "_top"}}
        else:
            model = {"parent": "minecraft:block/cube_all", "textures": {"all": tex}}
        P.dump(A + "models/block/%s.json" % name, model)
        P.dump(A + "blockstates/%s.json" % name, {"variants": {"": {"model": "ashbound:block/" + name}}})
        P.dump(A + "models/item/%s.json" % name, {"parent": "ashbound:block/" + name})
        loot_self(name)
        lang["block.ashbound." + name] = title
        tools[tool].append(name)
        entries.append({"name": name, "kind": "full", "feel": feel})
    P.dump(A + "lang/en_us.json", lang)
    for tool, names in tools.items():
        tag(tool, names)
    r = reg("gate_blocks.json") or {"blocks": [], "props": []}
    merge(r["blocks"], entries, "name")
    reg_put("gate_blocks.json", r)


# ---------------------------------------------------------------- props

# vanilla's block item views: rotation, scale (blockstates' block.json)
VIEWS = {"gui": ([30, 225, 0], 0.625), "ground": ([0, 0, 0], 0.25), "fixed": ([0, 0, 0], 0.5),
         "thirdperson_righthand": ([75, 45, 0], 0.375), "thirdperson_lefthand": ([75, 45, 0], 0.375),
         "firstperson_righthand": ([0, 45, 0], 0.4), "firstperson_lefthand": ([0, 225, 0], 0.4)}


def item_model(name, item):
    """the block's item; a prop bigger than a block (a hoard is three wide) shrunk and centred so it fits the slot"""
    import gui3d as G3
    vs = [tuple(map(float, l.split()[1:4])) for l in open(A + "models/mesh/%s.obj" % item) if l.startswith("v ")]
    lo, hi = [min(v[i] for v in vs) for i in range(3)], [max(v[i] for v in vs) for i in range(3)]
    big = max(h - l for l, h in zip(lo, hi))
    m = {"parent": "ashbound:block/" + item}
    if big > 1.05:
        c = [(l + h) / 2 - 0.5 for l, h in zip(lo, hi)]
        m["display"] = {}
        for view, (rot, sc) in VIEWS.items():
            s = sc / big
            r = G3.mul(G3.mul(G3.rx(math.radians(rot[0])), G3.ry(math.radians(rot[1]))), G3.rz(math.radians(rot[2])))
            t = G3.apply(r, [-k * s * 16 for k in c])
            m["display"][view] = {"rotation": rot, "translation": [round(k, 2) for k in t], "scale": [round(s, 3)] * 3}
    P.dump(A + "models/item/%s.json" % name, m)


def fit_items():
    """rewrites every prop's item model (python tools/port_gate.py --fit-items)"""
    n = 0
    for pr in reg("gate_blocks.json")["props"]:
        item = pr["name"] + {"bars": "_post", "fence": "_post", "trapdoor": "_bottom"}.get(pr["kind"], "")
        if os.path.exists(A + "models/mesh/%s.obj" % item):
            item_model(pr["name"], item)
            n += 1
    print("prop items:", n)


def obj_model(name, mesh):
    P.dump(A + "models/block/%s.json" % name, {"loader": "neoforge:obj", "model": "ashbound:models/mesh/%s.obj" % mesh,
                                                "flip_v": True, "automatic_culling": False, "shade_quads": True,
                                                "render_type": "minecraft:cutout", "textures": {"particle": "ashbound:block/" + mesh}})


def turned(model, y=0, x=0):
    v = {"model": "ashbound:block/" + model}
    if x:
        v["x"] = x
    if y:
        v["y"] = y
    return v


def port_props(g):
    BS = A + "blockstates/%s.json"
    lang = json.load(open(A + "lang/en_us.json", encoding="utf-8"))
    entries, tools = [], collections.defaultdict(list)
    for pr in g["props"]:
        n, k = pr["name"], pr["kind"]
        meshes = {"bars": [n + "_post", n + "_side"], "fence": [n + "_post", n + "_side"],
                  "trapdoor": [n + "_bottom", n + "_top", n + "_open"]}.get(k, [n])
        for m in meshes:
            if not os.path.exists(A + "models/mesh/%s.obj" % m):
                raise SystemExit("no mesh %s: run the gate's Blender props script first" % m)
            obj_model(m, m)
        item = n
        if k in ("facing", "coffer", "hoard"):
            P.dump(BS % n, {"variants": {"facing=%s" % f: turned(n, y) for f, y in FACING_Y.items()}})
        elif k == "chain":
            P.dump(BS % n, {"variants": {"axis=y": turned(n), "axis=z": turned(n, 0, 90), "axis=x": turned(n, 90, 90)}})
        elif k in ("bars", "fence"):
            parts = [{"apply": turned(n + "_post")}]
            for f, y in FACING_Y.items():
                parts.append({"when": {f: "true"}, "apply": dict(turned(n + "_side", y), uvlock=False)})
            P.dump(BS % n, {"multipart": parts})
            item = n + "_post"
        elif k == "trapdoor":
            v = {}
            for f, y in FACING_Y.items():
                for half in ("bottom", "top"):
                    v["facing=%s,half=%s,open=false" % (f, half)] = turned(n + "_" + half, y)
                    v["facing=%s,half=%s,open=true" % (f, half)] = turned(n + "_open", y)
            P.dump(BS % n, {"variants": v})
            item = n + "_bottom"
        elif k == "lantern":
            P.dump(BS % n, {"variants": {"hanging=false": turned(n), "hanging=true": turned(n)}})
        else:
            P.dump(BS % n, {"variants": {"": turned(n)}})
        item_model(n, item)
        loot_self(n)
        lang["block.ashbound." + n] = pr["title"]
        if k in ("coffer", "hoard"):
            lang["container.ashbound." + n] = pr["title"]
        tools["axe" if pr.get("sound") == "wood" else "hoe" if pr.get("sound") in ("wool", "grass") else "pickaxe"].append(n)
        e = {key: val for key, val in pr.items() if key != "title"}
        entries.append(e)
    P.dump(A + "lang/en_us.json", lang)
    for tool, names in tools.items():
        tag(tool, names)
    r = reg("gate_blocks.json") or {"blocks": [], "props": []}
    merge(r["props"], entries, "name")
    reg_put("gate_blocks.json", r)
    print("props: %d" % len(entries))


# ---------------------------------------------------------------- monsters

def old_entity(mid):
    """the old registration line: its class, hitbox, and whether it was born in fire"""
    src = open(OJ + "ModEntities.java", encoding="utf-8").read()
    m = re.search(r'(mob|hot)\("%s", (\w+)::new, ([\d.]+)f, ([\d.]+)f' % mid, src)
    if not m:
        raise SystemExit("no old entity " + mid)
    return m.group(2), float(m.group(3)), float(m.group(4)), m.group(1) == "hot"


def old_stats(cls):
    src = open(OJ + cls + ".java", encoding="utf-8").read()
    out = {}
    for key, name in (("hp", "MAX_HEALTH"), ("speed", "MOVEMENT_SPEED"), ("dmg", "ATTACK_DAMAGE"), ("armor", "ARMOR"),
                      ("kb", "KNOCKBACK_RESISTANCE")):
        m = re.search(r"Attributes\.%s,\s*([\d.]+)" % name, src)
        if m:
            out[key] = float(m.group(1))
    boss = re.search(r"class %s extends (\w+)" % cls, src)
    return out, bool(boss and boss.group(1) == "Boss")


def egg_colours(mesh):
    from PIL import Image
    im = Image.open(E.SRC + "textures/entity/%s.png" % mesh).convert("RGBA")
    px = sorted((p[:3] for p in im.getdata() if p[3] > 200), key=sum)
    dark, light = px[len(px) // 5], px[len(px) * 19 // 20]
    return (dark[0] << 16) | (dark[1] << 8) | dark[2], (light[0] << 16) | (light[1] << 8) | light[2]


def rig_bones(mesh):
    return {b["name"]: b for b in json.load(open(E.SRC + "models/entity/%s/rig.json" % mesh, encoding="utf-8"))["bones"]}


def auto_biped(mesh):
    """the usual two-legged fit; every other bone rides on its nearest fitted parent"""
    bones = rig_bones(mesh)
    rig = E.biped(mesh)
    for b in bones:
        if b in rig:
            continue
        on = bones[b]["parent"]
        while on not in rig and on in bones and bones[on]["parent"]:
            on = bones[on]["parent"]
        if on not in rig:   # a bone with no parent (Ossric's anvil): it goes with the hips
            on = "hips"
        rig[b] = (rig[on][0], rig[on][1], on if isinstance(rig[on][2], tuple) else rig[on][2], rig[on][3])
    return rig


def export_spider(mesh, joints, k=None, root="body"):
    """like efmob.export_spider, every bone given its joint (a leg's own, "LL1".."RL4"), or its parent's. With k
    given (a legless one: the eel) it keeps its own size and lies on the ground, not lifted to the spider's body"""
    bones = rig_bones(mesh)
    pv = bones[root]["pivot"]
    ground = k is not None
    k = k or E.SPIDER_ROOT / pv[1]
    J2 = {n: i for i, n in enumerate(E.SPIDER_JOINTS)}
    pos, uvs, nrm = [], [], []
    pkey, ukey, nkey = {}, {}, {}
    parts = {p: [] for p in E.SPIDER_PARTS}

    def joint_of(b):
        while b not in joints and bones[b]["parent"]:
            b = bones[b]["parent"]
        return joints.get(b, "Root")

    def index(table, lst, key):
        i = table.get(key)
        if i is None:
            i = table[key] = len(lst)
            lst.append(key)
        return i
    for bone in bones:
        joint = joint_of(bone)
        if joint[:2] in ("LL", "RL"):
            part = ("leftLeg" if joint[0] == "L" else "rightLeg") + joint[2]
        else:
            part = {"Root": "middleStomach", "Head": "head", "Stomach": "bottomStomach"}[joint]
        v, vt, vn, tris = E.load_obj(E.SRC + "models/entity/%s/%s.obj" % (mesh, bone))
        for tri in tris:
            for (vi, ti, ni) in tri:
                x, y, z = v[vi]
                mx, my, mz = (x - pv[0]) * k, (y * k if ground else E.SPIDER_ROOT + (y - pv[1]) * k), (z - pv[2]) * k
                pi = index(pkey, pos, (round(-mx, 5), round(mz, 5), round(my, 5), J2[joint]))
                u, w = vt[ti]
                ui = index(ukey, uvs, (round(u, 6), round(1 - w, 6)))
                nx, ny, nz = vn[ni]
                ni2 = index(nkey, nrm, (round(-nx, 4), round(nz, 4), round(ny, 4)))
                parts[part] += [pi, ui, ni2]
    E.write(mesh, pos, uvs, nrm, parts, E.SPIDER_PARTS, k)
    return 1 / k


def port_mobs(g):
    lang = json.load(open(A + "lang/en_us.json", encoding="utf-8"))
    old_lang = json.load(open(OLD + "resources/assets/ashbound/lang/en_us.json", encoding="utf-8"))
    entries = []
    for mid, spec in g["mobs"].items():
        mesh = spec.get("mesh", mid)
        cls, w, h, fire = spec["entity"] if "entity" in spec else old_entity(mid)
        stats, is_boss = (dict(spec["stats"]), False) if "stats" in spec else old_stats(cls)
        # monsters made here for the EF port (tools/frostmobs.py) are read from tools/mob_src, the old ones from Ashbound
        new_src = P.GAME + "tools/mob_src/"
        E.SRC = new_src if os.path.exists(new_src + "models/entity/%s/rig.json" % mesh) else OLD_SRC
        if spec.get("rig") == "spider":
            scale = export_spider(mesh, spec["joints"], spec.get("k"), spec.get("root", "body"))
        else:
            E.RIGS[mesh] = auto_biped(mesh)
            E.export(mesh)
            scale = rig_bones(mesh)["hips"]["pivot"][1] / E.AT["Root"]
        boss = spec.get("boss", is_boss)
        egg, spots = egg_colours(mesh)
        E.SRC = OLD_SRC
        entries.append({"id": mid, "mesh": mesh, "rig": spec.get("rig", "biped"), "scale": round(scale, 3), "w": w, "h": h,
                        "hp": stats.get("hp", 300 if boss else 40), "speed": stats.get("speed", 0.24),
                        "dmg": stats.get("dmg", 14 if boss else 6), "armor": stats.get("armor", 0), "kb": stats.get("kb", 1.0 if boss else 0),
                        "boss": boss, "key": spec.get("key", False), "fire": fire, "egg": egg, "spots": spots})
        name = mid.replace("_", " ").title()
        for k, fallback in (("entity.ashbound." + mid, name), ("item.ashbound.%s_spawn_egg" % mid, name + " Spawn Egg")):
            lang[k] = old_lang.get(k) or fallback
        P.dump(A + "models/item/%s_spawn_egg.json" % mid, {"parent": "minecraft:item/template_spawn_egg"})
    P.dump(A + "lang/en_us.json", lang)
    r = reg("gate_mobs.json") or []
    merge(r, entries, "id")
    reg_put("gate_mobs.json", r)
    print("mobs:", ", ".join("%s x%.2f" % (e["id"], e["scale"]) for e in entries))


# ---------------------------------------------------------------- the layout

def read_bin(path):
    b = gzip.open(path).read()
    i = 4

    def u16():
        nonlocal i
        v = struct.unpack(">H", b[i:i + 2])[0]
        i += 2
        return v

    def s():
        nonlocal i
        n = u16()
        v = b[i:i + n].decode("utf-8")
        i += n
        return v
    pal = [s() for _ in range(u16())]
    pts = {}
    for _ in range(u16()):
        key = s()
        pts[key] = struct.unpack(">ddd", b[i:i + 24])
        i += 24
    n = struct.unpack(">i", b[i:i + 4])[0]
    i += 4
    blocks = {}
    for _ in range(n):
        x, y, z, p = struct.unpack(">hhhH", b[i:i + 8])
        blocks[(x, y, z)] = pal[p]
        i += 8
    return blocks, pts


def write_bin(path, blocks, pts):
    pal, idx = [], {}
    out = []
    for p in sorted(blocks, key=lambda q: (q[0] >> 4, q[2] >> 4, q[1], q[0], q[2])):
        st = blocks[p]
        if st not in idx:
            idx[st] = len(pal)
            pal.append(st)
        out.append(struct.pack(">hhhH", p[0], p[1], p[2], idx[st]))

    def s(v):
        e = v.encode("utf-8")
        return struct.pack(">H", len(e)) + e
    data = b"KILN" + struct.pack(">H", len(pal)) + b"".join(s(v) for v in pal)
    data += struct.pack(">H", len(pts)) + b"".join(s(k) + struct.pack(">ddd", *v) for k, v in pts.items())
    data += struct.pack(">i", len(out)) + b"".join(out)
    with gzip.open(path, "wb") as f:
        f.write(data)


def parse(st):
    flow = st.endswith("#flow")
    st = st[:-5] if flow else st
    if "[" in st:
        n, rest = st[:-1].split("[", 1)
        props = dict(kv.split("=") for kv in rest.split(","))
    else:
        n, props = st, {}
    if ":" not in n:
        n = "minecraft:" + n
    return n, props, flow


def fmt(n, props, flow=False):
    s = n + ("[%s]" % ",".join("%s=%s" % kv for kv in sorted(props.items())) if props else "")
    return s + ("#flow" if flow else "")


# the properties each kind of our block keeps from the vanilla one it replaces
KEEP = {"facing": ("facing",), "coffer": ("facing",), "chain": ("axis",), "bars": ("north", "east", "south", "west"),
        "fence": ("north", "east", "south", "west"), "trapdoor": ("facing", "half", "open"), "lantern": ("hanging",),
        "stairs": ("facing", "half", "shape"), "slab": ("type",), "wall": ("north", "east", "south", "west", "up"), "pillar": ("axis",)}


def port_lair(gate, g):
    src = lair_src(g["lair"])
    print("  from", src)
    blocks, pts = read_bin(src + g["lair"] + ".bin")
    r = reg("gate_blocks.json")
    kinds = {b["name"]: b["kind"] for b in r["blocks"] + r["props"]}   # our props from other gates too (a chain is a chain)
    special = SPECIAL.get(gate)
    out, left, swapped = {}, collections.Counter(), collections.Counter()
    for p, st in blocks.items():
        n, props, flow = parse(st)
        if special:
            sp = special(blocks, p, n, props)
            if sp:
                out[p] = sp
                swapped[n + " ->" + sp.split("[")[0]] += 1
                continue
        short = n.split(":")[1]
        if n.startswith("minecraft:") and short in g["swap"]:
            new = g["swap"][short]
            keep = KEEP.get(kinds.get(new, "full"), ())
            np_ = {k: v for k, v in props.items() if k in keep}
            if kinds.get(new) in ("facing", "coffer") and np_.get("facing") in ("up", "down", None):
                np_["facing"] = "north"
            out[p] = fmt("ashbound:" + new, np_, flow)
            swapped[short + " ->" + new] += 1
            continue
        if n == "minecraft:iron_chain":
            n = "minecraft:chain"
        if n.startswith("minecraft:") and short not in LEFT_VANILLA:
            left[short] += 1
        out[p] = fmt(n, props, flow)
    write_bin(P.DATA + "lair/%s.bin" % g["lair"], out, pts)
    meta = json.load(open(src + g["lair"] + ".json", encoding="utf-8"))
    for k in ("safe_radius", "debris"):
        meta.pop(k, None)
    chk = meta.get("built_check", [[0, 0, 0, ""]])[0]
    if chk[3] and (chk[0], chk[1], chk[2]) in out:
        chk[3] = out[(chk[0], chk[1], chk[2])].split("[")[0]
    meta["built_check"] = [chk]
    P.dump(P.DATA + "lair/%s.json" % g["lair"], meta)
    port_loot(g["lair"])
    print("lair %s: %d blocks, %d states" % (g["lair"], len(out), len(set(out.values()))))
    print("  swapped:", ", ".join("%s %d" % kv for kv in swapped.most_common()))
    if left:
        print("  VANILLA LEFT:", ", ".join("%s %d" % kv for kv in left.most_common()))


def port_loot(lair):
    src = OLOOT + lair + ".json"
    if not os.path.exists(src):
        return
    t = json.load(open(src, encoding="utf-8"))
    have = set(os.path.splitext(f)[0] for f in os.listdir(A + "models/item"))

    def ok(e):
        n = e.get("name", "")
        return not n.startswith("ashbound:") or n.split(":")[1] in have
    for pool in t["pools"]:
        pool["entries"] = [dict(e, name="minecraft:chain") if e.get("name") == "minecraft:iron_chain" else e for e in pool["entries"] if ok(e)]
    t["pools"] = [p for p in t["pools"] if p["entries"]]
    P.dump(P.DATA + "loot_table/chests/%s.json" % lair, t)


if __name__ == "__main__" and sys.argv[1:] == ["--fit-items"]:
    fit_items()
elif __name__ == "__main__":
    gate = sys.argv[1]
    g = GATES[gate]
    steps = sys.argv[2:] or ["blocks", "props", "mobs", "lair"]
    if "blocks" in steps:
        port_blocks(g)
        port_made(g)
    if "props" in steps:
        port_props(g)
    if "mobs" in steps:
        port_mobs(g)
    if "lair" in steps:
        port_lair(gate, g)
