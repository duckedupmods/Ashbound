"""The Storm Bastion (A): a fortress on a mountain spire where the lightning never stops - the cliff path, the outer
bailey, the chain bridge over the drop, the tower stair up, the armoury, the captain's rampart, the spire stair, and
the top of the spire where the Thunder Abbess rings the storm. Rain-black granite, green copper, iron grates,
tarred timber, storm glass. dforge.py imports this."""
from blockforge import R
from dforge import dungeon, B, Pp, common_props

SLATE = R("#101418", "#181e24", "#222a32", "#2e3842", "#3a4652", "#485664")
SLATE_M = R("#06080a", "#0c1014", "#12181e")
COPPER = R("#123a32", "#1c5446", "#2a705c", "#3e8c74", "#5aa88e")
IRON = R("#0e1012", "#181a1e", "#24272c", "#32363c", "#42474e")
TIMBER = R("#0e0c0a", "#181410", "#221c16", "#2e261e", "#3a3026")
TIMBER_END = R("#221c16", "#2e261e", "#3a3026")
STORM = R("#1a3a7a", "#2a5ab0", "#4a86e0", "#7ab0ff", "#d4e6ff")
CLIFF = R("#14161a", "#1e2126", "#2a2e34", "#363b42", "#444a52")
MOSS = R("#1a2622", "#22322c", "#2c3e36")

dungeon("storm_bastion",
        blocks=[
            B("spire_rock", "Spire Rock", "rock", "minecraft:deepslate", args=dict(ramp=CLIFF, spread=0.6, crust=(MOSS, 0.08))),
            B("bastion_bricks", "Bastion Bricks", "bricks", "minecraft:deepslate_bricks", family=("stairs", "slab", "wall"),
              stem="bastion_brick", stem_title="Bastion Brick", args=dict(ramp=SLATE, mortar=SLATE_M)),
            B("bastion_ashlar", "Bastion Ashlar", "ashlar", "minecraft:polished_deepslate", args=dict(ramp=SLATE, mortar=SLATE_M)),
            B("rampart_flags", "Rampart Flagstones", "flags", "minecraft:polished_deepslate", family=("slab",), stem="rampart_flag",
              stem_title="Rampart Flag", args=dict(ramp=SLATE, grout=SLATE_M)),
            B("storm_copper", "Storm Copper", "plate", "minecraft:oxidized_copper", args=dict(ramp=COPPER, rivet=IRON, seams=8)),
            B("iron_grating", "Iron Grating", "grate", "minecraft:iron_block", args=dict(ramp=IRON, gap=SLATE_M)),
            B("tarred_timber", "Tarred Timber", "planks", "minecraft:dark_oak_planks", tool="axe", args=dict(ramp=TIMBER, n=4)),
            B("storm_beam", "Storm Beam", "log", "minecraft:dark_oak_log", tool="axe", args=dict(ramp=TIMBER, rings=TIMBER_END)),
            B("bastion_column", "Bastion Column", "column", "minecraft:polished_deepslate", args=dict(ramp=SLATE, mortar=COPPER, flutes=4)),
            B("bolt_carving", "Bolt Carving", "carved", "minecraft:chiseled_deepslate", args=dict(ramp=SLATE, mortar=SLATE_M, motif="cross")),
            B("storm_glass_block", "Storm Glass Block", "glow", "minecraft:sea_lantern", light=13, args=dict(ramp=STORM, base=SLATE, motif="vein")),
        ],
        props=common_props("storm", "Bastion", wood_color="color_gray") + [
            Pp("lightning_rod", "plain", "Bastion Lightning Rod", box=[6, 0, 6, 10, 16, 10], sound="copper", color="color_cyan",
               strength=3, solid=False),
            Pp("storm_orb", "plain", "Storm Orb", box=[3, 0, 3, 13, 16, 13], sound="glass", color="color_light_blue", strength=2, light=14),
            Pp("weather_vane", "plain", "Weather Vane", box=[4, 0, 4, 12, 16, 12], sound="copper", color="color_cyan", strength=2, solid=False),
            Pp("rope_coil", "plain", "Rope Coil", box=[2, 0, 2, 14, 6, 14], sound="wool", color="color_brown", strength=0.5),
        ],
        seal_words="The Captain's rod locks the spire", broken_words="The rod falls silent and the spire stair opens",
        layout=dict(
            palette=dict(
                hall_floor=[("rampart_flags", 3), ("iron_grating", 1)], hall_wall=[("bastion_bricks", 4), ("bastion_ashlar", 2),
                                                                                    ("bolt_carving", 1)],
                hall_ceil=[("tarred_timber", 2), ("storm_copper", 1)],
                cave_floor=[("spire_rock", 3), ("rampart_flags", 1)], cave_wall=[("spire_rock", 4)],
                cave_ceil=[("spire_rock", 3)],
                arena_floor=[("rampart_flags", 2), ("iron_grating", 1)], arena_wall=[("bastion_bricks", 3), ("storm_copper", 2),
                                                                                     ("storm_glass_block", 1)],
                bridge=[("iron_grating", 2), ("tarred_timber", 1)], rail="bastion_brick_wall",
                fill="spire_rock", pillar="bastion_column", stairs="bastion_brick_stairs", slab="bastion_brick_slab",
                lamp="storm_lantern", chain="storm_chain", bars="storm_bars", coffer="storm_coffer", vein="storm_glass_block"),
            seal=6, lamp_every=6, lamp_height=6, veins=0.02,
            rooms=[
                dict(name="the cliff path", kind="cave", w=27, len=30, h=16,
                     dress=[("clusters", dict(name="lightning_rod", chance=0.02))], mobs=[("spark_hound", 4)]),
                dict(name="the outer bailey", kind="hall", w=33, len=40, h=16, chest=True,
                     dress=[("frames", dict(every=6)), ("scatter", dict(name="rope_coil", n=4)), ("scatter", dict(name="storm_orb", n=3))],
                     mobs=[("gale_knight", 2), ("spark_hound", 3)]),
                dict(name="the chain bridge", kind="chasm", w=31, len=40, h=18, drop=22, mobs=[("spark_hound", 3), ("storm_caller", 1)]),
                dict(name="the tower stair", kind="descent", to=10, gap=6),
                dict(name="the armoury", kind="hall", w=27, len=36, h=14, chest=True,
                     dress=[("frames", dict(every=5)), ("scatter", dict(name="storm_orb", n=4)), ("scatter", dict(name="rope_coil", n=3))],
                     mobs=[("thunder_ogre", 1), ("storm_caller", 2), ("gale_knight", 1)], decor=[("spark_hound", 2)]),
                dict(name="the captain's rampart", kind="hall", w=23, len=26, h=14, elite="storm_captain",
                     dress=[("scatter", dict(name="weather_vane", n=2)), ("scatter", dict(name="lightning_rod", n=4))],
                     mobs=[("thunder_ogre", 1)]),
                dict(name="the spire stair", kind="descent", to=22, gap=6),
                dict(name="the spire top", kind="round", w=45, len=45, h=28, chest=True, ring=12,
                     dress=[("scatter", dict(name="lightning_rod", n=8)), ("scatter", dict(name="storm_orb", n=4))]),
            ]),
        )
