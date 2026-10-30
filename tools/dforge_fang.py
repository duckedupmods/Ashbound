"""The Warlord's Fang (a world tower, docs/TOWERS.md): red crag rock, crooked rough-cut courses, raw timber
hoardings, rusted spiked iron, bone, red-and-black war hide, bonfire. dforge.py imports this; the tower is
tools/towers/warlords_fang.py."""
from blockforge import R
from dforge import dungeon, B, Pp, common_props

CRAG = R("#3a1610", "#521e14", "#6c2a1a", "#863822", "#a04a2e", "#b8603e")
CRAG_M = R("#1e0c08", "#2a120c", "#3a1610")
TIMBER = R("#1c120a", "#2a1c10", "#3a2818", "#4c3620", "#5e462a")
IRON = R("#140e0c", "#1e1612", "#2a1e18", "#3a2a1e", "#4a3424")
RUST = R("#3a1a0a", "#5a2a10", "#7a3c18")
BONE = R("#6a6050", "#8a7e68", "#a89c82", "#c4b89c", "#dcd2b8")
HIDE_R = R("#3a0806", "#5a100a", "#7a1a10")
HIDE_K = R("#0e0a08", "#16100c", "#201812")
FIRE = R("#5a1606", "#9a2c08", "#d2520e", "#f68a1c", "#ffc24a", "#fff0b0")

dungeon("warlords_fang",
        blocks=[
            B("crag_rock", "Red Crag", "rock", "minecraft:red_terracotta", args=dict(ramp=CRAG, spread=0.6)),
            B("fang_stone", "Fangstone", "bricks", "minecraft:red_nether_bricks", family=("stairs", "slab", "wall"),
              stem="fang_stone", stem_title="Fangstone", args=dict(ramp=CRAG, mortar=CRAG_M, rows=3, run=6, crack=0.2)),
            B("crag_ashlar", "Crag Ashlar", "ashlar", "minecraft:red_sandstone", family=("stairs", "slab", "wall"),
              stem="crag_ashlar", stem_title="Crag Ashlar", args=dict(ramp=CRAG, mortar=CRAG_M)),
            B("war_timber", "War Timber", "planks", "minecraft:spruce_planks", tool="axe", family=("stairs", "slab"),
              stem="war_timber", stem_title="War Timber", args=dict(ramp=TIMBER, n=4, nails=IRON)),
            B("war_log", "War Log", "log", "minecraft:spruce_log", tool="axe", args=dict(ramp=TIMBER, rings=R("#4c3620", "#5e462a", "#705636"))),
            B("spiked_iron", "Spiked Iron", "plate", "minecraft:iron_block", family=("slab",), args=dict(ramp=IRON, rivet=BONE, seams=8, rust=RUST)),
            B("fang_bone_pile", "Bone Heap", "carved", "minecraft:bone_block", args=dict(ramp=BONE, mortar=CRAG_M, motif="eye")),
            B("tusk_bone", "Tusk Bone", "strata", "minecraft:bone_block", args=dict(ramp=BONE, bands=5)),
            B("war_hide", "War Hide", "stripes", "minecraft:red_wool", tool="hoe", args=dict(a=HIDE_R, b=HIDE_K, width=4)),
            B("war_fire", "War Fire", "glow", "minecraft:shroomlight", light=15, args=dict(ramp=FIRE, base=IRON, motif="ring")),
            B("fang_flags", "Fang Flagstones", "flags", "minecraft:red_sandstone", family=("slab",), stem="fang_flag",
              stem_title="Fang Flagstone", args=dict(ramp=CRAG, grout=CRAG_M)),
        ],
        props=common_props("fang", "Fang", light=14) + [
            Pp("fang_hoard", "hoard", "Warlord's Hoard", sound="wood", color="color_red", strength=4, light=7)],
        )
