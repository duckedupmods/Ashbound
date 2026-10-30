"""Rimeholt, the Giant's Keep (a world tower, docs/TOWERS.md): blue-black granite cut to a giant's scale, frost in
the joints, pale ice battlements and icicles, rune bands burning cold blue, tarred pine, iron. dforge.py imports this;
the tower is tools/towers/rimeholt.py."""
from blockforge import R
from dforge import dungeon, B, Pp, common_props

GRANITE = R("#141820", "#1c222c", "#252d39", "#2f3846", "#3b4555", "#4a5566")
GRANITE_M = R("#0a0c10", "#10141a", "#161b22")
FROST = R("#8aa6bc", "#a8c2d4", "#c8dcea", "#e6f2fa")
ICE = R("#76aed0", "#86bcda", "#9acae4", "#b0d8ee", "#c8e6f6", "#e0f4ff")
RUNE = R("#0a3a6a", "#1462a4", "#2a8ad8", "#5ab8f4", "#9adcff", "#e4f8ff")
PINE = R("#140e0a", "#1e1610", "#2a2016", "#382a1e", "#463626")
IRON = R("#0e1014", "#16191e", "#1f232a", "#2a2f37", "#373d46", "#464d58")
FUR = R("#6a6a66", "#8a8a84", "#a8a8a0", "#c6c6bc")

dungeon("rimeholt",
        blocks=[
            B("giant_granite", "Giant's Granite", "ashlar", "minecraft:polished_deepslate", family=("stairs", "slab", "wall"),
              stem="giant_granite", stem_title="Giant's Granite", args=dict(ramp=GRANITE, mortar=GRANITE_M)),
            B("rime_bricks", "Rime Bricks", "bricks", "minecraft:deepslate_bricks", family=("stairs", "slab", "wall"),
              stem="rime_brick", stem_title="Rime Brick", args=dict(ramp=GRANITE, mortar=GRANITE_M)),
            B("frost_granite", "Frostbitten Granite", "rock", "minecraft:deepslate", args=dict(ramp=GRANITE, spread=0.5, crust=(FROST, 0.16))),
            B("pale_ice", "Pale Ice", "crystal", "minecraft:packed_ice", family=("stairs", "slab", "wall"), stem="pale_ice",
              stem_title="Pale Ice", args=dict(ramp=ICE)),
            B("rune_band", "Rune Band", "carved", "minecraft:chiseled_deepslate", args=dict(ramp=GRANITE, mortar=RUNE, motif="rune")),
            B("rune_glow", "Rune Stone", "glow", "minecraft:sea_lantern", light=14, args=dict(ramp=RUNE, base=GRANITE, motif="ring")),
            B("ice_glow", "Glowing Ice", "glow", "minecraft:sea_lantern", light=12, args=dict(ramp=ICE, base=ICE, motif="full")),
            B("giant_column", "Giant's Column", "column", "minecraft:polished_deepslate", args=dict(ramp=GRANITE, mortar=RUNE, flutes=4)),
            B("frost_flags", "Frost Flagstones", "flags", "minecraft:polished_deepslate", family=("slab",), stem="frost_flag",
              stem_title="Frost Flagstone", args=dict(ramp=GRANITE, grout=GRANITE_M)),
            B("tarred_pine", "Tarred Pine", "planks", "minecraft:dark_oak_planks", tool="axe", family=("stairs", "slab"),
              stem="tarred_pine", stem_title="Tarred Pine", args=dict(ramp=PINE, n=4)),
            B("pine_log", "Giant Pine Log", "log", "minecraft:spruce_log", tool="axe", args=dict(ramp=PINE, rings=R("#382a1e", "#4c3a28", "#5e4a34"))),
            B("rime_iron", "Rime Iron", "plate", "minecraft:iron_block", family=("slab",), args=dict(ramp=IRON, rivet=FROST, seams=8)),
            B("white_fur", "White Bearskin", "rock", "minecraft:white_wool", tool="hoe", args=dict(ramp=FUR, spread=0.3)),
        ],
        props=common_props("rime", "Rime", light=13) + [
            Pp("rime_hoard", "hoard", "Jarl's Hoard", sound="wood", color="color_light_blue", strength=4, light=7)],
        )
