"""The Wyrm's Hoard (S): a dead volcano, and in its crater the gold of three kingdoms that Ignavar the Ash Wyrm carried
off and lay down on - the ash slope, the kobold warrens, the lava gallery, the counting hall, the cinder temple of the
cult that worships him, the drake roost, the priest's door, the long way down into the crater, and the Hoard where
Ignavar sleeps on the gold. Black basalt and grey ash, the old orange fire still in the cracks, and gold, gold
everywhere. dforge.py imports this."""
from blockforge import R
from dforge import dungeon, B, Pp, common_props

CALDERA = R("#08070a", "#100e10", "#1a1716", "#24201e", "#302a26", "#3c3530")
ASH = R("#2a2826", "#3a3734", "#4c4844", "#5e5954", "#706a64")
PUMICE = R("#1c1816", "#2a2420", "#38302a", "#463c34", "#56483e")
GOLD = R("#3a2604", "#5e400a", "#8a6010", "#b8861c", "#e0ac2c", "#fcd860")
GOLD_M = R("#1a1004", "#2a1a06", "#3a2604")
BRICK = R("#1a1210", "#261a16", "#34241e", "#443028", "#563c32")
BRICK_M = R("#060404", "#0c0808", "#120c0a")
FIRE = R("#5a1004", "#a02a06", "#e05a0c", "#ff9a20", "#ffd060")
BONE = R("#3e3628", "#5c5240", "#7c705a", "#9c9076", "#bcb094")
BONE_M = R("#1a160e", "#262016", "#322a1e")

dungeon("wyrms_hoard",
        blocks=[
            B("caldera_rock", "Caldera Rock", "rock", "minecraft:blackstone", args=dict(ramp=CALDERA, spread=0.6, crust=(ASH, 0.14))),
            B("pumice_strata", "Pumice Strata", "strata", "minecraft:tuff", args=dict(ramp=PUMICE, bands=6)),
            B("ash_bank", "Ash Bank", "rock", "minecraft:gray_concrete", args=dict(ramp=ASH, spread=0.3)),
            B("coin_heap", "Heaped Coins", "rock", "minecraft:raw_gold_block", args=dict(ramp=GOLD, spread=0.9, fleck=(R("#fff0a0", "#ffffff"), 14))),
            B("wyrm_bricks", "Wyrm-Cult Bricks", "bricks", "minecraft:nether_bricks", family=("stairs", "slab", "wall"), stem="wyrm_brick",
              stem_title="Wyrm-Cult Brick", args=dict(ramp=BRICK, mortar=BRICK_M, crust=(ASH, 0.1))),
            B("wyrm_flags", "Wyrm Flagstones", "flags", "minecraft:polished_blackstone", family=("slab",), stem="wyrm_flag",
              stem_title="Wyrm Flag", args=dict(ramp=CALDERA, grout=GOLD_M, crust=(ASH, 0.08))),
            B("scale_carving", "Scale Carving", "carved", "minecraft:chiseled_nether_bricks", args=dict(ramp=BRICK, mortar=GOLD, motif="scale")),
            B("hoard_plating", "Hoard Plating", "plate", "minecraft:gold_block", args=dict(ramp=GOLD, rivet=BRICK_M, seams=8)),
            B("dragonbone", "Dragonbone", "column", "minecraft:bone_block", args=dict(ramp=BONE, mortar=BONE_M, flutes=3)),
            B("wyrmfire_vein", "Wyrmfire Vein", "glow", "minecraft:magma_block", light=12, args=dict(ramp=FIRE, base=CALDERA, motif="vein")),
        ],
        props=common_props("hoard", "Hoard", metal_color="gold", wood_color="color_brown", light=13) + [
            Pp("gold_pile", "plain", "Pile of Gold", box=[0, 0, 0, 16, 10, 16], sound="metal", color="gold", strength=2),
            Pp("dragon_egg", "plain", "Petrified Dragon Egg", box=[3, 0, 3, 13, 15, 13], sound="stone", color="color_black", strength=4, light=7),
            Pp("wyrm_skull", "facing", "Drake Skull", box=[0, 0, 1, 16, 12, 15], sound="bone_block", color="sand", strength=3),
            Pp("kobold_totem", "facing", "Kobold Totem", box=[4, 0, 4, 12, 16, 12], sound="wood", color="color_brown", strength=1.5, light=6),
        ],
        seal_words="Only the Wyrm Priest's scale opens the crater gate", broken_words="The scale fits the lock and the crater gate opens",
        layout=dict(
            palette=dict(
                hall_floor=[("wyrm_flags", 3), ("coin_heap", 1)], hall_wall=[("wyrm_bricks", 4), ("scale_carving", 1),
                                                                             ("hoard_plating", 1)],
                hall_ceil=[("wyrm_bricks", 2), ("caldera_rock", 1)],
                cave_floor=[("caldera_rock", 3), ("ash_bank", 2), ("pumice_strata", 1)], cave_wall=[("caldera_rock", 3), ("pumice_strata", 2)],
                cave_ceil=[("caldera_rock", 3)],
                arena_floor=[("coin_heap", 4), ("caldera_rock", 1)], arena_wall=[("caldera_rock", 3), ("pumice_strata", 2),
                                                                                  ("wyrmfire_vein", 1)],
                bridge=[("wyrm_flags", 1)], rail="wyrm_brick_wall",
                fill="pumice_strata", pillar="dragonbone", stairs="wyrm_brick_stairs", slab="wyrm_brick_slab",
                lamp="hoard_lantern", chain="hoard_chain", bars="hoard_bars", coffer="hoard_coffer", vein="wyrmfire_vein"),
            seal=7, lamp_every=8, lamp_height=6, veins=0.04,
            rooms=[
                dict(name="the ash slope", kind="cave", w=27, len=30, h=16, mobs=[("kobold", 4)]),
                dict(name="the kobold warrens", kind="cave", w=25, len=36, h=12, chest=True,
                     dress=[("scatter", dict(name="kobold_totem", n=5)), ("scatter", dict(name="gold_pile", n=3))],
                     mobs=[("kobold", 6), ("ash_cultist", 1)]),
                dict(name="the lava gallery", kind="chasm", w=31, len=38, h=18, drop=20, mobs=[("kobold", 3), ("drake", 1)]),
                dict(name="the counting hall", kind="hall", w=27, len=40, h=16, chest=True,
                     dress=[("frames", dict(every=5)), ("scatter", dict(name="gold_pile", n=8)), ("scatter", dict(name="kobold_totem", n=2))],
                     mobs=[("hoard_golem", 1), ("kobold", 4)]),
                dict(name="the cinder temple", kind="hall", w=27, len=38, h=20, chest=True,
                     dress=[("frames", dict(every=4)), ("scatter", dict(name="wyrm_skull", n=3)), ("scatter", dict(name="dragon_egg", n=2))],
                     mobs=[("ash_cultist", 3), ("drake", 1)]),
                dict(name="the drake roost", kind="cave", w=33, len=40, h=22, chest=True,
                     dress=[("scatter", dict(name="dragon_egg", n=4)), ("scatter", dict(name="wyrm_skull", n=3))],
                     mobs=[("drake", 3), ("hoard_golem", 1)], decor=[("kobold", 2)]),
                dict(name="the priest's door", kind="hall", w=23, len=30, h=18, elite="wyrm_priest",
                     dress=[("frames", dict(every=3)), ("scatter", dict(name="gold_pile", n=4))], mobs=[("ash_cultist", 2)]),
                dict(name="the way into the crater", kind="descent", to=-14, gap=6),
                dict(name="the hoard", kind="round", w=55, len=55, h=32, chest=True, ring=12,
                     dress=[("scatter", dict(name="gold_pile", n=16)), ("scatter", dict(name="wyrm_skull", n=4)),
                            ("scatter", dict(name="dragon_egg", n=3))]),
            ]),
        )
