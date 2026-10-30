"""The Brigand's Gorge (E): a red canyon the bandits took for their own - the ambush road, their camp on the ledges,
the rope bridge, the stockade, and Red Jack's hall cut into the rock. dforge.py imports this."""
from blockforge import R
from dforge import dungeon, B, Pp, common_props

REDSTONE = R("#3a1a12", "#52261a", "#6c3422", "#88442c", "#a45a3a", "#c0744c")
RED_M = R("#1e0e0a", "#2a140e", "#381c12")
EARTH = R("#2a1c14", "#3a281c", "#4c3626", "#604632", "#76583e")
TIMBER = R("#1e140c", "#2e1f12", "#40301c", "#544026", "#6a5232")
TIMBER_END = R("#4a3824", "#5e4a30", "#76603e")
SANDB = R("#5a3a24", "#704a30", "#88603e", "#a07650", "#b88c62")
IRON = R("#16161a", "#24242a", "#36363e", "#4a4a54", "#62626c")
COALS = R("#3a0c02", "#6a1a04", "#a83a0a", "#e06a1a", "#ffa04a", "#ffd8a0")
GOLD = R("#4a2e08", "#7a4c10", "#a87018", "#d0961f", "#ecbc34")

dungeon("brigands_gorge",
        blocks=[
            B("gorge_sandstone", "Gorge Sandstone", "strata", "minecraft:sandstone", args=dict(ramp=REDSTONE, bands=4)),
            B("gorge_rock", "Gorge Rock", "rock", "minecraft:terracotta", args=dict(ramp=REDSTONE, spread=0.6)),
            B("packed_earth", "Packed Earth", "rock", "minecraft:packed_mud", args=dict(ramp=EARTH, fleck=(REDSTONE, 6), spread=0.5)),
            B("gorge_bricks", "Gorge Bricks", "bricks", "minecraft:bricks", family=("stairs", "slab", "wall"), stem="gorge_brick",
              stem_title="Gorge Brick", args=dict(ramp=SANDB, mortar=RED_M)),
            B("gorge_flags", "Gorge Flagstones", "flags", family=("slab",), stem="gorge_flag", stem_title="Gorge Flag",
              args=dict(ramp=SANDB, grout=RED_M)),
            B("stockade_planks", "Stockade Planks", "planks", "minecraft:spruce_planks", tool="axe", family=("stairs", "slab"),
              stem="stockade_plank", stem_title="Stockade Plank", args=dict(ramp=TIMBER, n=4, nails=(IRON[1], IRON[4]), vertical=True)),
            B("stockade_log", "Stockade Log", "log", "minecraft:spruce_log", tool="axe", args=dict(ramp=TIMBER, rings=TIMBER_END)),
            B("banded_iron", "Banded Iron", "plate", "minecraft:iron_block", args=dict(ramp=IRON, rust=R("#4a2414", "#6a3418"))),
            B("glowing_coals", "Glowing Coals", "glow", "minecraft:magma_block", light=12, args=dict(ramp=COALS, base=R("#120808", "#1e0e0a", "#2a140e"), motif="full")),
            B("carved_gorge", "Carved Gorge Stone", "carved", args=dict(ramp=SANDB, mortar=RED_M, motif="cross")),
            B("gorge_pillar", "Gorge Pillar", "column", args=dict(ramp=SANDB, mortar=RED_M)),
        ],
        props=common_props("gorge", "Gorge", wood_color="color_brown") + [
            Pp("loot_pile", "plain", "Loot Pile", box=[1, 0, 1, 15, 8, 15], sound="metal", color="gold", strength=1, light=4),
            Pp("gorge_campfire", "plain", "Bandit Campfire", box=[1, 0, 1, 15, 7, 15], sound="wood", color="color_orange",
               strength=1, light=14, solid=False),
            Pp("gorge_weapon_rack", "facing", "Bandit Weapon Rack", box=[0, 0, 5, 16, 16, 11], sound="wood", color="wood", strength=2),
            Pp("bandit_tent", "facing", "Bandit Tent", box=[0, 0, 0, 16, 14, 16], sound="wool", color="color_red", strength=1),
        ],
        seal_words="The lieutenant's gate is barred from within", broken_words="The lieutenant's keys spill in the dust",
        layout=dict(
            palette=dict(
                hall_floor=[("stockade_planks", 3), ("gorge_flags", 2)], hall_wall=[("stockade_planks", 4), ("gorge_bricks", 3),
                                                                                  ("carved_gorge", 1)],
                hall_ceil=[("stockade_planks", 1)],
                cave_floor=[("packed_earth", 4), ("gorge_rock", 2)], cave_wall=[("gorge_sandstone", 5), ("gorge_rock", 3)],
                cave_ceil=[("gorge_sandstone", 3), ("gorge_rock", 2)],
                arena_floor=[("gorge_flags", 3), ("packed_earth", 1)], arena_wall=[("gorge_bricks", 4), ("gorge_sandstone", 3),
                                                                                  ("carved_gorge", 1)],
                bridge=[("stockade_planks", 5), ("banded_iron", 1)], rail="gorge_brick_wall",
                fill="gorge_rock", pillar="stockade_log", stairs="stockade_plank_stairs", slab="stockade_plank_slab",
                lamp="gorge_lantern", chain="gorge_chain", bars="gorge_bars", coffer="gorge_coffer", vein="glowing_coals"),
            seal=6, lamp_every=6, lamp_height=6, veins=0.0,
            rooms=[
                dict(name="the ambush road", kind="cave", w=21, len=28, h=18, dress=[("frames", dict(every=9))],
                     mobs=[("footpad", 4)]),
                dict(name="the lookout climb", kind="descent", to=8, gap=6),
                dict(name="the bandit camp", kind="cave", w=35, len=44, h=18, chest=True,
                     dress=[("scatter", dict(name="gorge_campfire", n=3)), ("scatter", dict(name="loot_pile", n=4)),
                            ("scatter", dict(name="bandit_tent", n=5)), ("scatter", dict(name="gorge_weapon_rack", n=3))],
                     mobs=[("footpad", 3), ("knife_dancer", 2), ("gorge_ogre", 1), ("hedge_hexer", 1)]),
                dict(name="the rope bridge", kind="chasm", w=27, len=32, h=14, drop=26, mobs=[("knife_dancer", 2)]),
                dict(name="the stockade", kind="hall", w=23, len=28, h=10, chest=True,
                     dress=[("scatter", dict(name="gorge_weapon_rack", n=4)), ("scatter", dict(name="loot_pile", n=2))],
                     mobs=[("gorge_ogre", 1), ("hedge_hexer", 2)]),
                dict(name="the lieutenant's tent", kind="hall", w=21, len=22, h=10, elite="bandit_lieutenant",
                     dress=[("scatter", dict(name="bandit_tent", n=2)), ("scatter", dict(name="gorge_campfire", n=1))],
                     mobs=[("footpad", 3)]),
                dict(name="the king's stair", kind="descent", to=-6, gap=6),
                dict(name="red jack's hall", kind="round", w=41, len=41, h=18, chest=True, ring=10,
                     dress=[("scatter", dict(name="loot_pile", n=10)), ("scatter", dict(name="gorge_campfire", n=2))]),
            ]),
        )
