"""The Bloodmoon Court (A): a vampire manor where it is always the night of the blood moon - the hedge garden, the
grand foyer, the portrait gallery, the ballroom, the cellar stair and the cellars, the kennels where the Count's
Hound keeps the key, and the Moon Hall with its roof broken open. Black marble, crimson velvet, tarnished silver,
dark red glass. dforge.py imports this."""
from blockforge import R
from dforge import dungeon, B, Pp, common_props

BMARBLE = R("#060506", "#0e0c0e", "#18141a", "#221d24", "#2e2830", "#3c343e")
BMARBLE_M = R("#000000", "#040304", "#0a080a")
VEIN = R("#3a2a30", "#5a4048", "#7a5a64")
VELVET = R("#1e0408", "#32060c", "#4a0a12", "#640e1a", "#7e1422")
SILVER = R("#2a2a30", "#44444c", "#606068", "#7e7e86", "#a0a0a8", "#c4c4cc")
OAK = R("#0e0806", "#180e0a", "#22140e", "#2e1c14", "#3a241a")
OAK_END = R("#22140e", "#2e1c14", "#3a241a")
HEDGE = R("#060a08", "#0c120e", "#121a14", "#1a241c", "#222e24")
REDGLASS = R("#3a0008", "#6a0010", "#a0081c", "#d02030", "#ff5a60")
CELLAR = R("#120e0c", "#1c1612", "#28201a", "#342a22", "#42362c")

dungeon("bloodmoon_court",
        blocks=[
            B("black_marble", "Black Marble", "ashlar", "minecraft:polished_blackstone", args=dict(ramp=BMARBLE, mortar=BMARBLE_M, crust=(VEIN, 0.08))),
            B("marble_bricks", "Black Marble Bricks", "bricks", "minecraft:polished_blackstone_bricks", family=("stairs", "slab", "wall"),
              stem="marble_brick", stem_title="Black Marble Brick", args=dict(ramp=BMARBLE, mortar=BMARBLE_M)),
            B("court_tiles", "Court Tiles", "tiles", "minecraft:polished_blackstone", family=("slab",), stem="court_tile",
              stem_title="Court Tile", args=dict(ramp=BMARBLE, grout=BMARBLE_M, n=2, checker=VELVET)),
            B("crimson_velvet", "Crimson Velvet Panel", "carved", "minecraft:red_wool", tool="hoe", args=dict(ramp=VELVET, mortar=OAK, motif="eye")),
            B("silver_plate", "Tarnished Silver", "plate", "minecraft:iron_block", args=dict(ramp=SILVER, rivet=BMARBLE, seams=8)),
            B("manor_oak", "Manor Oak", "planks", "minecraft:dark_oak_planks", tool="axe", args=dict(ramp=OAK, n=4)),
            B("manor_beam", "Manor Beam", "log", "minecraft:dark_oak_log", tool="axe", args=dict(ramp=OAK, rings=OAK_END)),
            B("marble_column", "Black Marble Column", "column", "minecraft:polished_blackstone", args=dict(ramp=BMARBLE, mortar=SILVER, flutes=5)),
            B("black_hedge", "Black Hedge", "rock", "minecraft:dark_oak_leaves", tool="hoe", args=dict(ramp=HEDGE, spread=0.8)),
            B("blood_glass", "Blood Glass", "glow", "minecraft:redstone_lamp", light=11, args=dict(ramp=REDGLASS, base=BMARBLE, motif="ring")),
            B("cellar_stone", "Cellar Stone", "rock", "minecraft:tuff", args=dict(ramp=CELLAR, spread=0.5)),
        ],
        props=common_props("court", "Court", metal_color="color_light_gray", wood_color="color_red") + [
            Pp("kneeling_statue", "facing", "Kneeling Servant Statue", box=[2, 0, 2, 14, 14, 14], sound="stone", color="color_black", strength=3),
            Pp("blood_cask", "plain", "Blood Cask", box=[1, 0, 1, 15, 14, 15], sound="wood", color="color_red", strength=2),
            Pp("candelabra", "plain", "Silver Candelabra", box=[4, 0, 4, 12, 16, 12], sound="metal", color="color_light_gray", strength=2, light=13),
            Pp("court_mirror", "facing", "Gilt Mirror", box=[1, 0, 6, 15, 16, 10], sound="glass", color="gold", strength=2, light=4),
        ],
        seal_words="The Hound's collar keeps the Moon Hall shut", broken_words="The silver collar breaks and the Moon Hall opens",
        layout=dict(
            palette=dict(
                hall_floor=[("court_tiles", 3), ("manor_oak", 1)], hall_wall=[("marble_bricks", 3), ("crimson_velvet", 2),
                                                                               ("black_marble", 2)],
                hall_ceil=[("manor_oak", 2), ("manor_beam", 1)],
                cave_floor=[("court_tiles", 2), ("black_marble", 2)], cave_wall=[("black_hedge", 4), ("marble_bricks", 1)],
                cave_ceil=[("black_hedge", 2)],
                arena_floor=[("court_tiles", 3)], arena_wall=[("marble_bricks", 3), ("silver_plate", 1), ("blood_glass", 1),
                                                              ("crimson_velvet", 2)],
                bridge=[("court_tiles", 1)], rail="marble_brick_wall",
                fill="black_marble", pillar="marble_column", stairs="marble_brick_stairs", slab="marble_brick_slab",
                lamp="court_lantern", chain="court_chain", bars="court_bars", coffer="court_coffer", vein="blood_glass"),
            seal=7, lamp_every=6, lamp_height=6, veins=0.015,
            rooms=[
                dict(name="the hedge garden", kind="cave", w=31, len=34, h=18,
                     dress=["pools", ("scatter", dict(name="kneeling_statue", n=6))], mobs=[("blood_thrall", 5)]),
                dict(name="the grand foyer", kind="hall", w=33, len=34, h=18, chest=True,
                     dress=[("frames", dict(every=6)), ("scatter", dict(name="candelabra", n=4))],
                     mobs=[("blood_thrall", 4), ("gorged_butler", 1)]),
                dict(name="the portrait gallery", kind="hall", w=21, len=42, h=14,
                     dress=[("frames", dict(every=5)), ("scatter", dict(name="court_mirror", n=6))],
                     mobs=[("duelist", 3)]),
                dict(name="the ballroom", kind="hall", w=37, len=40, h=20, chest=True,
                     dress=[("frames", dict(every=8)), ("scatter", dict(name="candelabra", n=6))],
                     mobs=[("blood_thrall", 6), ("blood_mage", 2)], decor=[("blood_thrall", 3)]),
                dict(name="the cellar stair", kind="descent", to=-10, gap=6),
                dict(name="the cellars", kind="cave", w=29, len=36, h=12, chest=True, zone="hall",
                     dress=[("scatter", dict(name="blood_cask", n=12))], mobs=[("gorged_butler", 2), ("blood_mage", 1)]),
                dict(name="the kennels", kind="hall", w=23, len=28, h=13, elite="counts_hound",
                     dress=[("frames", dict(every=5))], mobs=[("blood_thrall", 2)]),
                dict(name="the moon hall", kind="round", w=45, len=45, h=28, chest=True, ring=12,
                     dress=[("scatter", dict(name="court_mirror", n=8)), ("scatter", dict(name="candelabra", n=6))]),
            ]),
        )
