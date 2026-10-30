"""Roster v2 dungeons as data: each one's blocks (blockforge.py paints them), props (blender/kit_props.py models them)
and layout (lairs/forge_lair.py builds it). The monsters are in forge_specs.py, the gear in gear.py.

Block entry: name, title, paint (a blockforge painter) + args (its ramps), feel (sounds/hardness of a vanilla block),
light, family (stairs/slab/wall built on it), stem (family names' stem when the base name ends in a plural).
"""
from blockforge import R

DUNGEONS = {}


def dungeon(gate, **kw):
    kw["gate"] = gate
    DUNGEONS[gate] = kw


def B(name, title, paint, feel="minecraft:stone_bricks", **kw):
    args = kw.pop("args", {})
    return dict(name=name, title=title, paint=paint, args=args, feel=feel, **kw)


# ================================================================ the Weeping Mine (E)

SLATE = R("#14171c", "#1d2128", "#272c34", "#323843", "#3f4652", "#4f5764")
SLATE_M = R("#0b0d10", "#14171c", "#1d2128")
TEAL = R("#0e4a4a", "#167070", "#22a09a", "#46ccc0", "#8ceee2", "#d6fff8")
COPPER = R("#1e130c", "#3a2414", "#5a361c", "#7c4a24", "#a0622e", "#c88444")
VERD = R("#1e4a3e", "#2e6a58", "#4a8c76", "#6ab096")
TIMBER = R("#1a120c", "#281b11", "#382617", "#4a331f", "#5e4229")
TIMBER_END = R("#3a2a1a", "#4e3a24", "#64492e", "#7a5a3a")
MINE_BRICK = R("#1c1d20", "#27292d", "#33363b", "#41454b", "#51565d")

dungeon("weeping_mine",
        blocks=[
            B("mine_rock", "Mine Rock", "rock", "minecraft:deepslate", args=dict(ramp=SLATE, fleck=(TEAL, 4), spread=0.55)),
            B("seam_rock", "Seam Rock", "strata", "minecraft:deepslate", args=dict(ramp=SLATE, bands=4, crust=(VERD, 0.12))),
            B("ore_rubble", "Ore Rubble", "rock", "minecraft:tuff", args=dict(ramp=SLATE, fleck=(COPPER, 10), spread=0.8)),
            B("veined_rock", "Veined Rock", "glow", "minecraft:deepslate", light=7, args=dict(ramp=TEAL, base=SLATE, motif="vein")),
            B("weeping_crystal_block", "Block of Weeping Crystal", "crystal", "minecraft:amethyst_block", light=11, args=dict(ramp=TEAL[:5])),
            B("crystal_rock", "Crystal-Grown Rock", "crystal", "minecraft:deepslate", light=5, args=dict(ramp=TEAL, rock=SLATE)),
            B("shaft_timber", "Shaft Timber", "log", "minecraft:dark_oak_log", tool="axe", args=dict(ramp=TIMBER, rings=TIMBER_END)),
            B("shaft_planks", "Shaft Planks", "planks", "minecraft:dark_oak_planks", tool="axe", family=("stairs", "slab"),
              stem="shaft_plank", stem_title="Shaft Plank", args=dict(ramp=TIMBER, n=4, nails=(COPPER[1], COPPER[4]))),
            B("mine_bricks", "Mine Bricks", "bricks", family=("stairs", "slab", "wall"), stem="mine_brick", stem_title="Mine Brick",
              args=dict(ramp=MINE_BRICK, mortar=SLATE_M, crust=(VERD, 0.08))),
            B("mine_flags", "Mine Flagstones", "flags", family=("stairs", "slab"), stem="mine_flag", stem_title="Mine Flag",
              args=dict(ramp=MINE_BRICK, grout=SLATE_M)),
            B("copper_plate", "Weeping Copper", "plate", "minecraft:copper_block", family=("slab",), stem="copper_plate",
              stem_title="Weeping Copper", args=dict(ramp=COPPER, rust=VERD[:2])),
            B("mine_grating", "Mine Grating", "grate", "minecraft:iron_block", args=dict(ramp=COPPER, gap=SLATE_M)),
            B("carved_seam", "Carved Seam Stone", "carved", args=dict(ramp=MINE_BRICK, mortar=SLATE_M, motif="eye")),
        ],
        )


def Pp(name, kind, title, **kw):
    d = dict(name=name, kind=kind, title=title)
    d.update(kw)
    return d


def common_props(px, title, metal_color="metal", wood_color="color_brown", light=14):
    """the shapes every dungeon has (kit_props.py MAKE_COMMON): its lantern, chain, seal bars, coffer"""
    return [Pp(px + "_lantern", "lantern", title + " Lantern", sound="lantern", color=metal_color, strength=2, light=light),
            Pp(px + "_chain", "chain", title + " Chain", sound="chain", color=metal_color, strength=3, solid=False),
            Pp(px + "_bars", "bars", title + " Bars", sound="metal", color=metal_color, strength=6),
            Pp(px + "_coffer", "coffer", title + " Coffer", sound="wood", color=wood_color, strength=2.5)]


DUNGEONS["weeping_mine"]["props"] = common_props("mine", "Mine") + [
    Pp("weeping_cluster", "plain", "Weeping Cluster", box=[2, 0, 2, 14, 14, 14], sound="amethyst", color="color_cyan",
       strength=1.5, light=12, solid=False),
    Pp("minecart", "facing", "Ore Cart", box=[1, 0, 2, 15, 12, 14], sound="metal", color="metal", strength=3),
    Pp("mine_rail", "facing", "Mine Rail", box=[0, 0, 0, 16, 2, 16], sound="metal", color="metal", strength=1, solid=False),
    Pp("ore_sacks", "plain", "Ore Sacks", box=[1, 0, 1, 15, 12, 15], sound="wool", color="color_brown", strength=1),
]


DUNGEONS["weeping_mine"].update(
    seal_words="The pump-house grille is chained shut", broken_words="The Foreman's keys turn the lock",
    layout=dict(
        palette=dict(
            hall_floor=[("mine_flags", 3), ("shaft_planks", 1)], hall_wall=[("mine_bricks", 6), ("carved_seam", 1)],
            hall_ceil=[("shaft_planks", 1)],
            cave_floor=[("ore_rubble", 3), ("mine_rock", 3)], cave_wall=[("mine_rock", 5), ("seam_rock", 3), ("crystal_rock", 1)],
            cave_ceil=[("mine_rock", 4), ("seam_rock", 2)],
            arena_floor=[("mine_rock", 2), ("crystal_rock", 1), ("ore_rubble", 1)],
            arena_wall=[("crystal_rock", 2), ("seam_rock", 2), ("mine_rock", 2), ("weeping_crystal_block", 1)],
            bridge=[("shaft_planks", 4), ("mine_grating", 1)], rail="mine_brick_wall",
            fill="mine_rock", pillar="shaft_timber", stairs="shaft_plank_stairs", slab="shaft_plank_slab",
            lamp="mine_lantern", chain="mine_chain", bars="mine_bars", coffer="mine_coffer", vein="veined_rock"),
        rail_prop="mine_rail", seal=6, lamp_every=6, lamp_height=6, veins=0.05,
        rooms=[
            dict(name="the pithead", kind="hall", w=19, len=24, h=10, chest=False,
                 dress=["frames", ("scatter", dict(name="minecart", n=2)), ("scatter", dict(name="ore_sacks", n=3))],
                 mobs=[("shard_crawler", 3)]),
            dict(name="the main shaft", kind="descent", to=-10, gap=6),
            dict(name="the crystal gallery", kind="cave", w=31, len=42, h=16, chest=True,
                 dress=[("frames", dict(every=7)), "rails", ("clusters", dict(name="weeping_cluster", chance=0.03))],
                 mobs=[("lamp_miner", 2), ("blind_burrower", 2), ("shard_crawler", 4)], decor=[("lamp_miner", 3)]),
            dict(name="the drop", kind="chasm", w=27, len=34, h=12, drop=22,
                 mobs=[("shard_crawler", 3), ("cart_golem", 1)]),
            dict(name="the ore hall", kind="hall", w=23, len=30, h=12, chest=True,
                 dress=["rails", ("scatter", dict(name="minecart", n=3)), ("scatter", dict(name="ore_sacks", n=4))],
                 mobs=[("cart_golem", 2), ("lamp_miner", 2)]),
            dict(name="the pump house", kind="hall", w=21, len=24, h=10, elite="foreman",
                 dress=[("scatter", dict(name="ore_sacks", n=2))], mobs=[("blind_burrower", 2)]),
            dict(name="the weeping deep", kind="descent", to=-22, gap=6),
            dict(name="the heart of the vein", kind="round", w=43, len=43, h=22, chest=True, ring=12,
                 dress=[("clusters", dict(name="weeping_cluster", chance=0.05))]),
        ]),
)


# the other Roster v2 dungeons, one file each
import dforge_tide  # noqa: E402,F401
import dforge_gorge  # noqa: E402,F401
import dforge_rookery  # noqa: E402,F401
import dforge_circus  # noqa: E402,F401
import dforge_coven  # noqa: E402,F401
import dforge_tomb  # noqa: E402,F401
import dforge_titan  # noqa: E402,F401
import dforge_jade  # noqa: E402,F401
import dforge_storm  # noqa: E402,F401
import dforge_blood  # noqa: E402,F401
import dforge_maze  # noqa: E402,F401
import dforge_abyss  # noqa: E402,F401
import dforge_eclipse  # noqa: E402,F401
import dforge_hoard  # noqa: E402,F401

# world towers (docs/TOWERS.md)
import dforge_clockwork  # noqa: E402,F401
import dforge_ziggurat  # noqa: E402,F401
import dforge_rimeholt  # noqa: E402,F401
import dforge_minaret  # noqa: E402,F401
import dforge_fang  # noqa: E402,F401

# the capital's house stone
import dforge_highmourn  # noqa: E402,F401
