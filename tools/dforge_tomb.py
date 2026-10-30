"""The Sandsunk Tomb (C): a sun-king's tomb the desert swallowed - the drift stair down through the sand, the
sunken court, the embalmers' hall, the scarab pit, the jackal gallery, the guardian's door, the solar stair, and the
Sun-King's burial chamber under its gold disc. dforge.py imports this."""
from blockforge import R
from dforge import dungeon, B, Pp, common_props

SAND = R("#4a3618", "#6a4e24", "#8a6a34", "#a88446", "#c4a05a", "#dcbc78")
SANDSTONE = R("#3e2a14", "#5a3e1e", "#76542a", "#946c38", "#ae8648", "#c8a060")
SAND_M = R("#22160a", "#2e1e0e", "#3a2814")
LAPIS = R("#0a1430", "#122048", "#1c3066", "#284484", "#3a5ca4")
GOLD = R("#5a3c0a", "#8a6214", "#b48a24", "#dab43c", "#f4d870")
CEDAR = R("#2a160a", "#3e2210", "#563018", "#6e4020", "#86522a")
CEDAR_END = R("#563018", "#6e4020", "#86522a")
SUN = R("#8a4a0a", "#c4720e", "#f0a020", "#ffd060", "#fff2b0")
DARKROCK = R("#1a120a", "#261a0e", "#342414", "#44301a", "#563e22")

dungeon("sandsunk_tomb",
        blocks=[
            B("drift_sandstone", "Drift Sandstone", "rock", "minecraft:sandstone", args=dict(ramp=SAND, spread=0.7)),
            B("tomb_strata", "Tomb Strata", "strata", "minecraft:smooth_sandstone", args=dict(ramp=SANDSTONE, bands=5)),
            B("tomb_bricks", "Tomb Bricks", "bricks", "minecraft:cut_sandstone", family=("stairs", "slab", "wall"),
              stem="tomb_brick", stem_title="Tomb Brick", args=dict(ramp=SANDSTONE, mortar=SAND_M, crack=0.08)),
            B("tomb_ashlar", "Tomb Ashlar", "ashlar", "minecraft:smooth_sandstone", args=dict(ramp=SANDSTONE, mortar=SAND_M)),
            B("tomb_flags", "Tomb Flagstones", "flags", "minecraft:smooth_sandstone", family=("slab",), stem="tomb_flag",
              stem_title="Tomb Flag", args=dict(ramp=SANDSTONE, grout=SAND_M)),
            B("lapis_tiles", "Lapis Tiles", "tiles", "minecraft:lapis_block", args=dict(ramp=LAPIS, grout=SAND_M, n=4, checker=GOLD)),
            B("hieroglyph_stone", "Hieroglyph Stone", "carved", "minecraft:chiseled_sandstone", args=dict(ramp=SANDSTONE, mortar=SAND_M, motif="eye")),
            B("sun_carving", "Sun Carving", "carved", "minecraft:chiseled_sandstone", args=dict(ramp=GOLD, mortar=SAND_M, motif="sun")),
            B("tomb_column", "Lotus Column", "column", "minecraft:cut_sandstone", args=dict(ramp=SANDSTONE, mortar=GOLD, flutes=5)),
            B("cedar_beam", "Cedar Beam", "log", "minecraft:stripped_spruce_log", tool="axe", args=dict(ramp=CEDAR, rings=CEDAR_END)),
            B("sunstone", "Sunstone", "glow", "minecraft:shroomlight", light=13, args=dict(ramp=SUN, base=SANDSTONE, motif="ring")),
            B("tomb_bedrock", "Tomb Bedrock", "rock", "minecraft:terracotta", args=dict(ramp=DARKROCK, spread=0.5)),
        ],
        props=common_props("tomb", "Tomb", wood_color="sand") + [
            Pp("canopic_jars", "plain", "Canopic Jars", box=[2, 0, 2, 14, 12, 14], sound="decorated_pot", color="terracotta_orange",
               strength=1),
            Pp("sarcophagus", "facing", "Sarcophagus", box=[0, 0, 1, 16, 12, 15], sound="stone", color="gold", strength=4),
            Pp("sun_brazier", "plain", "Sun Brazier", box=[3, 0, 3, 13, 16, 13], sound="metal", color="gold", strength=3, light=14),
            Pp("jackal_statue", "facing", "Jackal Statue", box=[3, 0, 3, 13, 16, 13], sound="stone", color="color_black", strength=3),
        ],
        seal_words="The Guardian's ankh bars the way", broken_words="The ankh breaks and the door grinds open",
        layout=dict(
            palette=dict(
                hall_floor=[("tomb_flags", 4), ("lapis_tiles", 1)], hall_wall=[("tomb_bricks", 4), ("hieroglyph_stone", 2),
                                                                                ("tomb_ashlar", 2)],
                hall_ceil=[("tomb_ashlar", 2), ("lapis_tiles", 1)],
                cave_floor=[("drift_sandstone", 4), ("tomb_flags", 1)], cave_wall=[("drift_sandstone", 3), ("tomb_strata", 3)],
                cave_ceil=[("tomb_strata", 3), ("drift_sandstone", 1)],
                arena_floor=[("tomb_flags", 3), ("lapis_tiles", 1)], arena_wall=[("tomb_bricks", 3), ("sun_carving", 1),
                                                                                 ("hieroglyph_stone", 2)],
                bridge=[("tomb_flags", 1)], rail="tomb_brick_wall",
                fill="tomb_bedrock", pillar="tomb_column", stairs="tomb_brick_stairs", slab="tomb_brick_slab",
                lamp="tomb_lantern", chain="tomb_chain", bars="tomb_bars", coffer="tomb_coffer", vein="sunstone"),
            seal=6, lamp_every=6, lamp_height=6, veins=0.02,
            rooms=[
                dict(name="the drift stair", kind="cave", w=27, len=30, h=14,
                     dress=[("clusters", dict(name="canopic_jars", chance=0.02))], mobs=[("tomb_scarab", 5)]),
                dict(name="the sunken court", kind="hall", w=31, len=38, h=16, chest=True,
                     dress=[("frames", dict(every=7)), ("scatter", dict(name="jackal_statue", n=4)),
                            ("scatter", dict(name="sun_brazier", n=4))],
                     mobs=[("jackal_runner", 3), ("embalmer", 1)]),
                dict(name="the embalmers' hall", kind="hall", w=25, len=34, h=12, chest=True,
                     dress=[("scatter", dict(name="sarcophagus", n=6)), ("clusters", dict(name="canopic_jars", chance=0.04))],
                     mobs=[("embalmer", 2), ("tomb_scarab", 4)], decor=[("tomb_scarab", 2)]),
                dict(name="the scarab pit", kind="chasm", w=31, len=36, h=14, drop=14, mobs=[("tomb_scarab", 4), ("jackal_runner", 2)]),
                dict(name="the jackal gallery", kind="hall", w=23, len=36, h=13,
                     dress=[("frames", dict(every=6)), ("scatter", dict(name="jackal_statue", n=6))],
                     mobs=[("sand_colossus", 1), ("jackal_runner", 3)]),
                dict(name="the guardian's door", kind="hall", w=21, len=22, h=14, elite="sun_guardian",
                     dress=[("scatter", dict(name="sun_brazier", n=4))], mobs=[("embalmer", 1)]),
                dict(name="the solar stair", kind="descent", to=-14, gap=6),
                dict(name="the burial chamber", kind="round", w=45, len=45, h=24, chest=True, ring=12,
                     dress=[("scatter", dict(name="sarcophagus", n=4)), ("scatter", dict(name="sun_brazier", n=6)),
                            ("clusters", dict(name="canopic_jars", chance=0.02))]),
            ]),
        )
