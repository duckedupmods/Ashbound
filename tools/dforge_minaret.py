"""The Glass Minaret (a world tower, docs/TOWERS.md): sun-bleached sandstone, turquoise tile banded in gold, brass
screens with amber glass, white plaster, cedar, sun-mirror fire. dforge.py imports this; the tower is
tools/towers/glass_minaret.py."""
from blockforge import R
from dforge import dungeon, B, Pp, common_props

SAND = R("#6a5034", "#866848", "#a2825c", "#bc9c72", "#d2b48a", "#e6cca4")
SAND_M = R("#3a2a1a", "#4e3a26", "#624a32")
TURQ = R("#0a3a44", "#105660", "#18767e", "#24989c", "#3cbab8", "#74dad2")
GOLD = R("#3a2606", "#5e400c", "#8a6214", "#b48a24", "#dab43c", "#f4d870")
BRASS = R("#2a1a08", "#4a300e", "#6e4a18", "#966826", "#bc8a38", "#dcb056")
AMBER = R("#7a3a08", "#b45c10", "#e08a1e", "#ffb53a", "#ffd77a", "#fff2c4")
SUN = R("#8a4a06", "#c87410", "#f0a020", "#ffc84a", "#ffe48a", "#fffae0")
PLASTER = R("#a49a88", "#bab09c", "#cec6b2", "#e0dacb", "#eeeadf")
CEDAR = R("#2a1408", "#3e200e", "#542e16", "#6c3e20", "#86502a")

dungeon("glass_minaret",
        blocks=[
            B("sun_sandstone", "Sunbleached Sandstone", "ashlar", "minecraft:smooth_sandstone", family=("stairs", "slab", "wall"),
              stem="sun_sandstone", stem_title="Sunbleached Sandstone", args=dict(ramp=SAND, mortar=SAND_M)),
            B("minaret_bricks", "Minaret Bricks", "bricks", "minecraft:sandstone", family=("stairs", "slab", "wall"),
              stem="minaret_brick", stem_title="Minaret Brick", args=dict(ramp=SAND, mortar=SAND_M)),
            B("turquoise_tiles", "Turquoise Tiles", "tiles", "minecraft:prismarine_bricks", family=("stairs", "slab"),
              stem="turquoise_tile", stem_title="Turquoise Tile", args=dict(ramp=TURQ, grout=GOLD, n=4)),
            B("star_frieze", "Star Frieze", "carved", "minecraft:chiseled_sandstone", args=dict(ramp=TURQ, mortar=GOLD, motif="sun")),
            B("gold_inlay", "Gold Inlay", "carved", "minecraft:gold_block", args=dict(ramp=GOLD, mortar=SAND_M, motif="scale")),
            B("brass_screen", "Brass Screen", "lattice", "minecraft:glass", light=10, args=dict(ramp=AMBER, lead=BRASS)),
            B("dome_brass", "Dome Brass", "plate", "minecraft:copper_block", family=("stairs", "slab"), args=dict(ramp=BRASS, rivet=GOLD, seams=4)),
            B("sun_glow", "Sun Mirror", "glow", "minecraft:shroomlight", light=15, args=dict(ramp=SUN, base=BRASS, motif="ring")),
            B("white_plaster", "White Plaster", "rock", "minecraft:white_terracotta", family=("stairs", "slab"),
              stem="white_plaster", stem_title="White Plaster", args=dict(ramp=PLASTER, spread=0.2)),
            B("minaret_column", "Minaret Column", "column", "minecraft:smooth_sandstone", args=dict(ramp=SAND, mortar=TURQ, flutes=4)),
            B("cedar_planks", "Cedar Planks", "planks", "minecraft:jungle_planks", tool="axe", family=("stairs", "slab"),
              stem="cedar_plank", stem_title="Cedar Plank", args=dict(ramp=CEDAR, n=4)),
            B("bazaar_flags", "Bazaar Flagstones", "flags", "minecraft:smooth_sandstone", family=("slab",), stem="bazaar_flag",
              stem_title="Bazaar Flagstone", args=dict(ramp=SAND, grout=SAND_M)),
        ],
        props=common_props("minaret", "Minaret", light=14) + [
            Pp("minaret_hoard", "hoard", "Sultan's Hoard", sound="wood", color="color_yellow", strength=4, light=7)],
        )
