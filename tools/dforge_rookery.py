"""The Rookery (D): a black tower the crow-men roost in. You climb it: the gate yard, the long stair, the nest hall,
the gallery of perches, the wind bridge, the captain's hall, and the Raven Mother's roost at the top.
dforge.py imports this."""
from blockforge import R
from dforge import dungeon, B, Pp, common_props

BLACK = R("#0e0e12", "#16161c", "#1e1e26", "#282832", "#34343e", "#42424e")
BLACK_M = R("#060608", "#0a0a0e", "#101016")
SLATE = R("#14161e", "#1c1f2a", "#262a38", "#323848", "#40465a")
GUANO = R("#8a8a84", "#a4a49c", "#c0c0b8", "#dadad2")
THATCH = R("#2a2416", "#3e3620", "#544a2c", "#6c6038", "#867846")
BONE = R("#5a5446", "#7a7260", "#9a927c", "#bab29a", "#d8d0b8")
OMEN = R("#1e123a", "#34205e", "#4e3488", "#7056b0", "#9a84d4", "#d0c4f2")
EBONY = R("#0c0a0a", "#161212", "#201a1a", "#2c2424", "#3a3030")
EBONY_END = R("#2a2222", "#3a3030", "#4c4040")

dungeon("rookery",
        blocks=[
            B("rook_stone", "Rook Stone", "bricks", "minecraft:deepslate_bricks", family=("stairs", "slab", "wall"),
              stem="rook_stone", stem_title="Rook Stone", args=dict(ramp=BLACK, mortar=BLACK_M)),
            B("streaked_rook_stone", "Streaked Rook Stone", "bricks", "minecraft:deepslate_bricks",
              args=dict(ramp=BLACK, mortar=BLACK_M, crust=(GUANO, 0.1))),
            B("rook_slate", "Rook Slate", "tiles", "minecraft:deepslate_tiles", family=("slab",), stem="rook_slate",
              stem_title="Rook Slate", args=dict(ramp=SLATE, grout=BLACK_M, n=2)),
            B("tower_rock", "Tower Rock", "rock", "minecraft:deepslate", args=dict(ramp=BLACK, spread=0.6)),
            B("nest_thatch", "Nest Thatch", "planks", "minecraft:hay_block", tool="hoe", args=dict(ramp=THATCH, n=8)),
            B("bone_lattice", "Bone Lattice", "grate", "minecraft:bone_block", args=dict(ramp=BONE, gap=BLACK_M)),
            B("omen_glass", "Omen Stone", "glow", "minecraft:crying_obsidian", light=11, args=dict(ramp=OMEN, base=BLACK, motif="ring")),
            B("carved_rook", "Carved Rook Stone", "carved", args=dict(ramp=BLACK, mortar=BLACK_M, motif="eye")),
            B("rook_column", "Rook Column", "column", args=dict(ramp=BLACK, mortar=BLACK_M)),
            B("ebony_beam", "Ebony Beam", "log", "minecraft:dark_oak_log", tool="axe", args=dict(ramp=EBONY, rings=EBONY_END)),
            B("ebony_planks", "Ebony Planks", "planks", "minecraft:dark_oak_planks", tool="axe", family=("stairs", "slab"),
              stem="ebony_plank", stem_title="Ebony Plank", args=dict(ramp=EBONY, n=4)),
        ],
        props=common_props("rook", "Rook") + [
            Pp("crow_nest", "plain", "Crow Nest", box=[0, 0, 0, 16, 8, 16], sound="grass", color="color_brown", strength=0.5),
            Pp("crow_perch", "facing", "Crow Perch", box=[6, 0, 6, 10, 16, 10], sound="wood", color="color_black", strength=2),
            Pp("bone_chimes", "plain", "Bone Chimes", box=[4, 2, 4, 12, 16, 12], sound="bone_block", color="color_white",
               strength=0.5, solid=False),
            Pp("omen_altar", "plain", "Omen Altar", box=[1, 0, 1, 15, 14, 15], sound="stone", color="color_purple", strength=3, light=10),
        ],
        seal_words="The captain's door is barred with talons", broken_words="The captain's talon turns the lock",
        layout=dict(
            palette=dict(
                hall_floor=[("rook_slate", 3), ("ebony_planks", 2)], hall_wall=[("rook_stone", 6), ("streaked_rook_stone", 2),
                                                                               ("carved_rook", 1)],
                hall_ceil=[("ebony_planks", 2), ("rook_slate", 1)],
                cave_floor=[("nest_thatch", 3), ("tower_rock", 2)], cave_wall=[("tower_rock", 4), ("streaked_rook_stone", 3)],
                cave_ceil=[("tower_rock", 3), ("rook_stone", 1)],
                arena_floor=[("rook_slate", 2), ("nest_thatch", 2)], arena_wall=[("rook_stone", 4), ("streaked_rook_stone", 2),
                                                                                ("omen_glass", 1)],
                bridge=[("ebony_planks", 4), ("bone_lattice", 1)], rail="rook_stone_wall",
                fill="tower_rock", pillar="rook_column", stairs="rook_stone_stairs", slab="rook_stone_slab",
                lamp="rook_lantern", chain="rook_chain", bars="rook_bars", coffer="rook_coffer", vein="omen_glass"),
            seal=7, lamp_every=6, lamp_height=7, veins=0.02,
            rooms=[
                dict(name="the gate yard", kind="hall", w=21, len=20, h=12, dress=[("scatter", dict(name="crow_perch", n=3))],
                     mobs=[("carrion_crow", 4)]),
                dict(name="the long stair", kind="descent", to=10, gap=6),
                dict(name="the nest hall", kind="cave", w=31, len=40, h=20, chest=True,
                     dress=[("scatter", dict(name="crow_nest", n=8)), ("scatter", dict(name="bone_chimes", n=4))],
                     mobs=[("carrion_crow", 4), ("feather_blade", 2), ("augur", 1)]),
                dict(name="the second stair", kind="descent", to=22, gap=6),
                dict(name="the gallery of perches", kind="hall", w=25, len=30, h=18, chest=True, piers=5,
                     dress=[("scatter", dict(name="crow_perch", n=8)), ("scatter", dict(name="omen_altar", n=1))],
                     mobs=[("crowbrute", 2), ("augur", 1), ("feather_blade", 1)], decor=[("crowbrute", 2)]),
                dict(name="the wind bridge", kind="chasm", w=27, len=30, h=14, drop=30, mobs=[("carrion_crow", 3), ("feather_blade", 1)]),
                dict(name="the captain's hall", kind="hall", w=21, len=24, h=12, elite="rook_captain",
                     dress=[("scatter", dict(name="crow_perch", n=4))], mobs=[("crowbrute", 1)]),
                dict(name="the crown stair", kind="descent", to=34, gap=6),
                dict(name="the roost", kind="round", w=41, len=41, h=26, chest=True, ring=12,
                     dress=[("scatter", dict(name="crow_nest", n=10)), ("scatter", dict(name="bone_chimes", n=6)),
                            ("scatter", dict(name="omen_altar", n=2))]),
            ]),
        )
