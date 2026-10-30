"""The Jade Monastery (B): a monastery on a mountain where the monks turned to jade at their prayers and got up
again - the mountain gate, the court of steps, the hall of incense, the cloud bridge, the scripture hall, the
abbot's training ground, the stair of heaven up, and the Lotus Throne where the Thousand Hands waits. Red lacquer,
jade, dark tiles, gold, pale granite. dforge.py imports this."""
from blockforge import R
from dforge import dungeon, B, Pp, common_props

GRANITE = R("#3a3a36", "#504e48", "#68665e", "#828076", "#9c9a8e", "#b6b4a6")
GRAN_M = R("#1e1e1a", "#2a2a24", "#36362e")
JADE = R("#0a2a1a", "#124228", "#1c5c38", "#2a784a", "#3e9660", "#5ab47a")
LACQUER = R("#2a0606", "#460a08", "#64120c", "#821c12", "#9e2a1a")
ROOF = R("#0e1214", "#161c1e", "#20282a", "#2a3436", "#364244")
GOLD = R("#5a3c0a", "#8a6214", "#b48a24", "#dab43c", "#f4d870")
WOOD = R("#1a1008", "#2a1a0e", "#3c2614", "#50341c", "#664426")
WOOD_END = R("#3c2614", "#50341c", "#664426")
JGLOW = R("#0a4a2a", "#127a44", "#22aa60", "#46d080", "#9af0c0")
MOSS = R("#1a2a10", "#24381a", "#2e4622")

dungeon("jade_monastery",
        blocks=[
            B("mountain_granite", "Mountain Granite", "rock", "minecraft:andesite", args=dict(ramp=GRANITE, spread=0.6, crust=(MOSS, 0.1))),
            B("temple_granite", "Temple Granite", "bricks", "minecraft:stone_bricks", family=("stairs", "slab", "wall"),
              stem="temple_granite", stem_title="Temple Granite", args=dict(ramp=GRANITE, mortar=GRAN_M)),
            B("granite_flags", "Granite Flagstones", "flags", "minecraft:smooth_stone", family=("slab",), stem="granite_flag",
              stem_title="Granite Flag", args=dict(ramp=GRANITE, grout=GRAN_M)),
            B("jade_tiles", "Jade Tiles", "tiles", "minecraft:prismarine_bricks", args=dict(ramp=JADE, grout=GRAN_M, n=4)),
            B("carved_jade", "Carved Jade", "carved", "minecraft:prismarine_bricks", args=dict(ramp=JADE, mortar=GRAN_M, motif="ring")),
            B("red_lacquer", "Red Lacquer Panel", "planks", "minecraft:crimson_planks", tool="axe", args=dict(ramp=LACQUER, n=4, vertical=True)),
            B("lacquer_pillar", "Lacquer Pillar", "column", "minecraft:crimson_stem", tool="axe", args=dict(ramp=LACQUER, mortar=GOLD, flutes=4)),
            B("roof_tiles", "Temple Roof Tiles", "bricks", "minecraft:deepslate_tiles", args=dict(ramp=ROOF, mortar=GRAN_M, rows=8, run=4)),
            B("temple_beam", "Temple Beam", "log", "minecraft:dark_oak_log", tool="axe", args=dict(ramp=WOOD, rings=WOOD_END)),
            B("gold_lattice", "Gold Lattice", "grate", "minecraft:gold_block", args=dict(ramp=GOLD, gap=LACQUER)),
            B("jade_lamp_stone", "Jadelight Stone", "glow", "minecraft:sea_lantern", light=12, args=dict(ramp=JGLOW, base=GRANITE, motif="ring")),
            B("cloud_stone", "Cloud Stone", "rock", "minecraft:calcite", args=dict(ramp=R("#8a8c8e", "#a4a6a8", "#bcbec0", "#d4d6d6", "#eaeaea"), spread=0.6)),
        ],
        props=common_props("jade", "Monastery", metal_color="gold", wood_color="color_red") + [
            Pp("incense_burner", "plain", "Incense Burner", box=[2, 0, 2, 14, 14, 14], sound="metal", color="color_black", strength=3, light=8),
            Pp("prayer_wheel", "plain", "Prayer Wheel", box=[4, 0, 4, 12, 16, 12], sound="wood", color="gold", strength=2),
            Pp("stone_lantern", "plain", "Stone Lantern", box=[3, 0, 3, 13, 16, 13], sound="stone", color="stone", strength=3, light=13),
            Pp("temple_bell", "plain", "Temple Bell", box=[2, 0, 2, 14, 16, 14], sound="metal", color="color_green", strength=4),
        ],
        seal_words="The Abbot's prayer binds the stair", broken_words="The prayer breaks and the stair to heaven opens",
        layout=dict(
            palette=dict(
                hall_floor=[("granite_flags", 3), ("jade_tiles", 1)], hall_wall=[("red_lacquer", 3), ("temple_granite", 3),
                                                                                  ("carved_jade", 1)],
                hall_ceil=[("roof_tiles", 2), ("temple_beam", 1)],
                cave_floor=[("mountain_granite", 3), ("granite_flags", 1)], cave_wall=[("mountain_granite", 4), ("cloud_stone", 1)],
                cave_ceil=[("mountain_granite", 3)],
                arena_floor=[("jade_tiles", 2), ("granite_flags", 2)], arena_wall=[("red_lacquer", 2), ("gold_lattice", 1),
                                                                                   ("carved_jade", 2), ("temple_granite", 2)],
                bridge=[("granite_flags", 1)], rail="temple_granite_wall",
                fill="mountain_granite", pillar="lacquer_pillar", stairs="temple_granite_stairs", slab="temple_granite_slab",
                lamp="jade_lantern", chain="jade_chain", bars="jade_bars", coffer="jade_coffer", vein="jade_lamp_stone"),
            seal=6, lamp_every=6, lamp_height=6, veins=0.015,
            rooms=[
                dict(name="the mountain gate", kind="cave", w=27, len=30, h=16,
                     dress=[("scatter", dict(name="stone_lantern", n=4))], mobs=[("jade_acolyte", 5)]),
                dict(name="the court of steps", kind="hall", w=33, len=40, h=16, chest=True,
                     dress=[("frames", dict(every=6)), ("scatter", dict(name="incense_burner", n=4)),
                            ("scatter", dict(name="stone_lantern", n=4))],
                     mobs=[("jade_acolyte", 4), ("stone_lion", 1)]),
                dict(name="the cloud bridge", kind="chasm", w=31, len=36, h=16, drop=18, mobs=[("shadow_monk", 3)]),
                dict(name="the hall of incense", kind="hall", w=27, len=38, h=14, chest=True,
                     dress=[("frames", dict(every=5)), ("scatter", dict(name="prayer_wheel", n=8)),
                            ("scatter", dict(name="incense_burner", n=3))],
                     mobs=[("incense_monk", 2), ("jade_acolyte", 3)], decor=[("jade_acolyte", 2)]),
                dict(name="the scripture hall", kind="hall", w=25, len=34, h=13,
                     dress=[("frames", dict(every=6)), ("scatter", dict(name="temple_bell", n=2))],
                     mobs=[("stone_lion", 1), ("shadow_monk", 2), ("incense_monk", 1)]),
                dict(name="the training ground", kind="hall", w=27, len=26, h=14, elite="fist_abbot",
                     dress=[("scatter", dict(name="stone_lantern", n=4))], mobs=[("jade_acolyte", 2)]),
                dict(name="the stair of heaven", kind="descent", to=12, gap=6),
                dict(name="the lotus throne", kind="round", w=45, len=45, h=26, chest=True, ring=12,
                     dress=[("scatter", dict(name="incense_burner", n=6)), ("scatter", dict(name="stone_lantern", n=6))]),
            ]),
        )
