"""The Tide Chapel (E): a seaside church the sea took - its nave flooded, its crypt opened into a sea cave, the bell
fallen into the pit under the tower. dforge.py imports this."""
from blockforge import R
from dforge import dungeon, B, Pp, common_props

SEASTONE = R("#1e2826", "#2a3634", "#384644", "#485856", "#5a6c68", "#6e827e")
SEA_M = R("#0e1414", "#161e1e", "#1e2828")
BARN = R("#8a8676", "#aaa694", "#c8c4b0", "#e2dece")
WEED = R("#1e3a20", "#2e5430", "#40703e")
DRIFT = R("#2a2622", "#3a3530", "#4c4640", "#5e5850", "#726a60")
DRIFT_END = R("#4a4238", "#5e5448", "#74685a")
BRONZE = R("#1e2414", "#2e3420", "#42462a", "#5a5a36", "#7a7444")
VERDI = R("#2a5a4a", "#3e7a64", "#5a9a80")
PEARL = R("#4a8a90", "#7cc0c4", "#b4e4e6", "#e6fafa")
REEF = R("#3a1e1a", "#5a2e26", "#7a4234", "#9a5a44", "#b87656")
TILE_W = R("#7a8a86", "#94a49e", "#b0beb8", "#c8d4ce")

dungeon("tide_chapel",
        blocks=[
            B("chapel_stone", "Chapel Stone", "ashlar", family=("stairs", "slab", "wall"), stem="chapel_stone",
              stem_title="Chapel Stone", args=dict(ramp=SEASTONE, mortar=SEA_M)),
            B("barnacled_stone", "Barnacled Stone", "bricks", args=dict(ramp=SEASTONE, mortar=SEA_M, crust=(BARN, 0.12))),
            B("weeded_stone", "Weeded Stone", "bricks", args=dict(ramp=SEASTONE, mortar=SEA_M, crust=(WEED, 0.25))),
            B("chapel_tiles", "Chapel Tiles", "tiles", family=("slab",), stem="chapel_tile", stem_title="Chapel Tile",
              args=dict(ramp=TILE_W, grout=SEA_M, n=2, checker=SEASTONE)),
            B("reef_rock", "Reef Rock", "rock", "minecraft:tuff", args=dict(ramp=SEASTONE, fleck=(REEF, 12), spread=0.7)),
            B("tide_rock", "Tide Rock", "strata", "minecraft:deepslate", args=dict(ramp=SEASTONE, bands=3, crust=(BARN, 0.12))),
            B("drowned_sand", "Drowned Sand", "rock", "minecraft:sandstone",
              args=dict(ramp=R("#4a4638", "#5e5a48", "#747058", "#8a866c"), spread=0.4)),
            B("driftwood_planks", "Driftwood Planks", "planks", "minecraft:spruce_planks", tool="axe", family=("stairs", "slab"),
              stem="driftwood_plank", stem_title="Driftwood Plank", args=dict(ramp=DRIFT, n=4, nails=(BRONZE[1], BRONZE[4]))),
            B("driftwood_log", "Driftwood Log", "log", "minecraft:spruce_log", tool="axe", args=dict(ramp=DRIFT, rings=DRIFT_END)),
            B("bell_bronze", "Bell Bronze", "plate", "minecraft:copper_block", args=dict(ramp=BRONZE, rust=VERDI)),
            B("pearl_stone", "Pearl Stone", "glow", "minecraft:sea_lantern", light=12, args=dict(ramp=PEARL, base=SEASTONE, motif="ring")),
            B("carved_chapel", "Carved Chapel Stone", "carved", args=dict(ramp=SEASTONE, mortar=SEA_M, motif="sun")),
            B("chapel_column", "Chapel Column", "column", args=dict(ramp=SEASTONE, mortar=SEA_M)),
        ],
        props=common_props("tide", "Chapel", light=14) + [
            Pp("drowned_pew", "facing", "Drowned Pew", box=[0, 0, 2, 16, 10, 14], sound="wood", color="wood", strength=2),
            Pp("kelp_strand", "plain", "Kelp Strand", box=[4, 0, 4, 12, 16, 12], sound="wet_grass", color="color_green",
               strength=0.2, solid=False),
            Pp("clam_heap", "plain", "Clam Heap", box=[1, 0, 1, 15, 8, 15], sound="bone_block", color="color_white", strength=1, light=6),
            Pp("chapel_font", "plain", "Drowned Font", box=[2, 0, 2, 14, 14, 14], sound="stone", color="stone", strength=3, light=9),
        ],
        seal_words="The choir's grille will not lift", broken_words="The choir falls silent, the grille lifts",
        layout=dict(
            palette=dict(
                hall_floor=[("chapel_tiles", 3), ("chapel_stone", 2), ("drowned_sand", 1)],
                hall_wall=[("chapel_stone", 5), ("barnacled_stone", 2), ("weeded_stone", 2), ("carved_chapel", 1)],
                hall_ceil=[("chapel_stone", 3), ("barnacled_stone", 1)],
                cave_floor=[("drowned_sand", 3), ("reef_rock", 2)],
                cave_wall=[("tide_rock", 4), ("reef_rock", 3), ("barnacled_stone", 1)],
                cave_ceil=[("tide_rock", 3), ("reef_rock", 1)],
                arena_floor=[("chapel_tiles", 2), ("drowned_sand", 1), ("bell_bronze", 1)],
                arena_wall=[("barnacled_stone", 3), ("weeded_stone", 2), ("chapel_stone", 2), ("pearl_stone", 1)],
                bridge=[("driftwood_planks", 4), ("chapel_stone", 1)], rail="chapel_stone_wall",
                fill="tide_rock", pillar="chapel_column", stairs="chapel_stone_stairs", slab="chapel_stone_slab",
                lamp="tide_lantern", chain="tide_chain", bars="tide_bars", coffer="tide_coffer", vein="pearl_stone"),
            seal=6, lamp_every=6, lamp_height=7, veins=0.02,
            rooms=[
                dict(name="the drowned porch", kind="hall", w=19, len=20, h=10,
                     dress=[("scatter", dict(name="drowned_pew", n=4, facing="south")), ("scatter", dict(name="clam_heap", n=2))],
                     mobs=[("tide_crab", 4)]),
                dict(name="the flooded nave", kind="hall", w=27, len=44, h=18, chest=True, piers=6,
                     dress=["pools", ("scatter", dict(name="drowned_pew", n=12, facing="south")),
                            ("scatter", dict(name="chapel_font", n=1, facing="none")),
                            ("scatter", dict(name="kelp_strand", n=6, facing="none"))],
                     mobs=[("tide_priest", 2), ("net_thrower", 2), ("tide_crab", 3)], decor=[("tide_priest", 2)]),
                dict(name="the crypt stair", kind="descent", to=-8, gap=6),
                dict(name="the sea cave", kind="cave", w=33, len=40, h=14, chest=True,
                     dress=["pools", ("clusters", dict(name="kelp_strand", chance=0.04)), ("scatter", dict(name="clam_heap", n=4, facing="none"))],
                     mobs=[("crab_knight", 2), ("net_thrower", 2), ("tide_crab", 4)]),
                dict(name="the reef chasm", kind="chasm", w=29, len=30, h=12, drop=20, mobs=[("tide_crab", 3), ("net_thrower", 1)]),
                dict(name="the choir loft", kind="hall", w=23, len=26, h=14, elite="barnacle_choir",
                     dress=[("scatter", dict(name="drowned_pew", n=6, facing="north"))], mobs=[("tide_priest", 2)]),
                dict(name="the bell shaft", kind="descent", to=-20, gap=6),
                dict(name="the bell pit", kind="round", w=43, len=43, h=24, chest=True, ring=12,
                     dress=["pools", ("scatter", dict(name="clam_heap", n=6, facing="none")),
                            ("clusters", dict(name="kelp_strand", chance=0.03))]),
            ]),
        )
