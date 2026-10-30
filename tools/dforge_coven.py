"""The Mirefen Coven (D): a drowned fen where a coven of hags keep their huts - the mire's edge, the boardwalk over the
sinkhole, the hag huts, the drowned grove, the Matron's hut, and Mother Mire's cauldron pool. dforge.py imports this."""
from blockforge import R
from dforge import dungeon, B, Pp, common_props

MUD = R("#141408", "#1e1e0e", "#2a2a14", "#38361c", "#484624")
PEAT = R("#16100a", "#22180e", "#2e2214", "#3c2e1a", "#4a3a22")
MIRE = R("#1a1e16", "#24281e", "#30362a", "#3e4636", "#4e5844")
MIRE_M = R("#0a0c08", "#10140c", "#161c10")
ROTWOOD = R("#141a10", "#1e2616", "#2a341e", "#384428", "#465432")
WILLOW = R("#1e1a12", "#2c261a", "#3c3424", "#4e4430", "#62563c")
WILLOW_END = R("#3c3424", "#4e4430", "#62563c")
MOSS = R("#1e3410", "#2c4a16", "#3e621e", "#527c28")
WITCH = R("#1a4a10", "#2a7a1a", "#44b02a", "#7ce04a", "#c4ff9a")
REED = R("#3a3a1a", "#4e4e24", "#64642e", "#7a7a3a", "#929248")

dungeon("mirefen_coven",
        blocks=[
            B("bog_mud", "Bog Mud", "rock", "minecraft:mud", tool="shovel", args=dict(ramp=MUD, spread=0.6)),
            B("fen_peat", "Fen Peat", "strata", "minecraft:packed_mud", tool="shovel", args=dict(ramp=PEAT, bands=4)),
            B("mire_rock", "Mire Rock", "rock", "minecraft:tuff", args=dict(ramp=MIRE, spread=0.6, crust=(MOSS, 0.12))),
            B("rotten_planks", "Rotten Planks", "planks", "minecraft:mangrove_planks", tool="axe", family=("stairs", "slab"),
              stem="rotten_plank", stem_title="Rotten Plank", args=dict(ramp=ROTWOOD, n=4)),
            B("willow_log", "Willow Log", "log", "minecraft:mangrove_log", tool="axe", args=dict(ramp=WILLOW, rings=WILLOW_END)),
            B("hag_stone", "Hag Stone", "bricks", "minecraft:mossy_stone_bricks", family=("stairs", "slab", "wall"), stem="hag_stone",
              stem_title="Hag Stone", args=dict(ramp=MIRE, mortar=MIRE_M, crust=(MOSS, 0.14))),
            B("coven_flags", "Coven Flagstones", "flags", family=("slab",), stem="coven_flag", stem_title="Coven Flag",
              args=dict(ramp=MIRE, grout=MIRE_M, crust=(MOSS, 0.1))),
            B("reed_thatch", "Reed Thatch", "planks", "minecraft:hay_block", tool="hoe", args=dict(ramp=REED, n=8, vertical=True)),
            B("witchlight", "Witchlight Stone", "glow", "minecraft:verdant_froglight", light=12, args=dict(ramp=WITCH, base=MIRE, motif="vein")),
            B("carved_hex", "Hex-Carved Stone", "carved", args=dict(ramp=MIRE, mortar=MIRE_M, motif="rune")),
            B("willow_pillar", "Willow Post", "column", tool="axe", feel="minecraft:mangrove_log", args=dict(ramp=WILLOW, mortar=PEAT)),
        ],
        props=common_props("mire", "Mire") + [
            Pp("coven_cauldron", "plain", "Coven Cauldron", box=[1, 0, 1, 15, 12, 15], sound="metal", color="color_black",
               strength=3, light=10),
            Pp("hag_effigy", "facing", "Hag Effigy", box=[3, 0, 3, 13, 16, 13], sound="wood", color="wood", strength=1, solid=False),
            Pp("fen_toadstools", "plain", "Fen Toadstools", box=[2, 0, 2, 14, 10, 14], sound="fungus", color="color_red",
               strength=0.3, light=7, solid=False),
            Pp("fen_reeds", "plain", "Fen Reeds", box=[2, 0, 2, 14, 16, 14], sound="grass", color="plant", strength=0.1, solid=False),
        ],
        seal_words="The Matron's hex holds the door", broken_words="The hex-knot unravels",
        layout=dict(
            palette=dict(
                hall_floor=[("rotten_planks", 3), ("coven_flags", 2)], hall_wall=[("reed_thatch", 3), ("hag_stone", 3),
                                                                                  ("carved_hex", 1)],
                hall_ceil=[("reed_thatch", 1)],
                cave_floor=[("bog_mud", 4), ("fen_peat", 2)], cave_wall=[("mire_rock", 4), ("fen_peat", 3)],
                cave_ceil=[("mire_rock", 3), ("fen_peat", 1)],
                arena_floor=[("bog_mud", 3), ("coven_flags", 2)], arena_wall=[("mire_rock", 3), ("hag_stone", 2), ("witchlight", 1)],
                bridge=[("rotten_planks", 1)], rail="hag_stone_wall",
                fill="mire_rock", pillar="willow_log", stairs="rotten_plank_stairs", slab="rotten_plank_slab",
                lamp="mire_lantern", chain="mire_chain", bars="mire_bars", coffer="mire_coffer", vein="witchlight"),
            seal=6, lamp_every=6, lamp_height=6, veins=0.03,
            rooms=[
                dict(name="the mire's edge", kind="cave", w=29, len=32, h=14,
                     dress=["pools", ("clusters", dict(name="fen_reeds", chance=0.06))], mobs=[("mire_thrall", 5)]),
                dict(name="the boardwalk", kind="chasm", w=31, len=36, h=12, drop=12, mobs=[("fen_crawler", 3)]),
                dict(name="the hag huts", kind="cave", w=33, len=40, h=16, chest=True,
                     dress=[("scatter", dict(name="coven_cauldron", n=3)), ("scatter", dict(name="hag_effigy", n=5)),
                            ("clusters", dict(name="fen_toadstools", chance=0.03))],
                     mobs=[("hag_sister", 2), ("mire_thrall", 3), ("bog_troll", 1)], decor=[("mire_thrall", 3)]),
                dict(name="the root stair", kind="descent", to=-8, gap=6),
                dict(name="the drowned grove", kind="cave", w=31, len=36, h=18, chest=True,
                     dress=["pools", ("clusters", dict(name="fen_toadstools", chance=0.05)), ("frames", dict(every=8))],
                     mobs=[("bog_troll", 2), ("fen_crawler", 2)]),
                dict(name="the matron's hut", kind="hall", w=21, len=22, h=11, elite="coven_matron",
                     dress=[("scatter", dict(name="coven_cauldron", n=1)), ("scatter", dict(name="hag_effigy", n=3))],
                     mobs=[("hag_sister", 1)]),
                dict(name="the sinking stair", kind="descent", to=-16, gap=6),
                dict(name="the cauldron pool", kind="round", w=43, len=43, h=22, chest=True, ring=10,
                     dress=["pools", ("scatter", dict(name="coven_cauldron", n=4)), ("clusters", dict(name="fen_reeds", chance=0.04))]),
            ]),
        )
