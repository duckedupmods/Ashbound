"""The Serpent Ziggurat (a world tower, docs/TOWERS.md): mossy green-grey limestone, jade inlay, gold friezes cut with
serpents, red-painted plaster, root-wood, and jade fire. dforge.py imports this; the tower is tools/towers/serpent_ziggurat.py."""
from blockforge import R
from dforge import dungeon, B, Pp, common_props

LIME = R("#2a2e26", "#383d32", "#474d3f", "#585f4e", "#6a7160", "#7e8572")
LIME_M = R("#151812", "#1e221a", "#272c22")
MOSS = R("#1c3216", "#26421c", "#325424", "#40682e")
JADE = R("#0a3a2a", "#105238", "#18704c", "#249262", "#3ab47e", "#62d6a0")
GOLD = R("#3a2606", "#5e400c", "#8a6214", "#b48a24", "#dab43c", "#f4d870")
RED = R("#3a0e0a", "#561610", "#741e16", "#92281c", "#ae3626")
ROOT = R("#1c140c", "#2a1e12", "#3a2a1a", "#4a3822", "#5c482c")
ROOT_END = R("#3a2a1a", "#4e3a24", "#64492e")
FIRE = R("#0a4a2a", "#127a44", "#1ea862", "#3ad486", "#7cf0b4", "#d4ffe8")

dungeon("serpent_ziggurat",
        blocks=[
            B("temple_limestone", "Temple Limestone", "ashlar", "minecraft:mossy_stone_bricks", family=("stairs", "slab", "wall"),
              stem="temple_limestone", stem_title="Temple Limestone", args=dict(ramp=LIME, mortar=LIME_M, crust=(MOSS, 0.12))),
            B("temple_bricks", "Temple Bricks", "bricks", "minecraft:mossy_stone_bricks", family=("stairs", "slab", "wall"),
              stem="temple_brick", stem_title="Temple Brick", args=dict(ramp=LIME, mortar=LIME_M, crust=(MOSS, 0.2))),
            B("overgrown_limestone", "Overgrown Limestone", "rock", "minecraft:moss_block", args=dict(ramp=LIME, spread=0.5, crust=(MOSS, 0.45))),
            B("jade_tiles", "Jade Tiles", "tiles", "minecraft:prismarine_bricks", family=("slab",), stem="jade_tile", stem_title="Jade Tile",
              args=dict(ramp=JADE, grout=LIME_M, n=4)),
            B("gold_frieze", "Gold Frieze", "carved", "minecraft:gold_block", args=dict(ramp=GOLD, mortar=R("#24180a", "#3a2606", "#5e400c"), motif="scale")),
            B("serpent_carving", "Serpent Carving", "carved", "minecraft:chiseled_stone_bricks", args=dict(ramp=LIME, mortar=LIME_M, motif="eye")),
            B("red_plaster", "Red Plaster", "rock", "minecraft:red_terracotta", args=dict(ramp=RED, spread=0.3)),
            B("root_wood", "Root Wood", "log", "minecraft:jungle_log", tool="axe", args=dict(ramp=ROOT, rings=ROOT_END)),
            B("temple_column", "Temple Column", "column", "minecraft:stone_bricks", args=dict(ramp=LIME, mortar=GOLD, flutes=4)),
            B("jade_fire", "Jade Fire", "glow", "minecraft:sea_lantern", light=14, args=dict(ramp=FIRE, base=LIME, motif="full")),
            B("jade_block", "Jade Block", "crystal", "minecraft:emerald_block", light=6, args=dict(ramp=JADE)),
        ],
        props=common_props("coil", "Coil", light=13) + [
            Pp("coil_hoard", "hoard", "Coiled King's Hoard", sound="wood", color="color_green", strength=4, light=7)],
        )
