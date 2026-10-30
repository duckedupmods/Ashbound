"""The Eclipse Cathedral (S): a cathedral built to the sun, and the day the sun went black it fell with the angels who
kept it - the ash steps, the burnt nave, the bell drop, the cloister of the choir, the reliquary vaults, the choir
where the Seraph Warden stands, the tower stair, and at the top the Eclipse where the Fallen Seraph waits under the
black sun. Black marble and black gold, pale burnt stone, ash over everything, and the white-gold corona light.
dforge.py imports this."""
from blockforge import R
from dforge import dungeon, B, Pp, common_props

MARBLE = R("#040406", "#0a0a0e", "#121218", "#1a1a22", "#24242e", "#30303c")
MARBLE_M = R("#000000", "#030305", "#08080c")
BURNT = R("#2a2622", "#3a3530", "#4c4640", "#5e5850", "#726a60", "#867e72")
BURNT_M = R("#0e0c0a", "#161412", "#1e1a18")
GILT = R("#1a1204", "#2e2008", "#4a340e", "#6a4c16", "#8e6820", "#b8902e", "#dcb44a")
ASH = R("#1e1c1a", "#2a2826", "#383532", "#46423e", "#55504a")
CORONA = R("#8a6a1a", "#c8a03a", "#f0d070", "#fff0b0", "#ffffff")
EBON = R("#08070a", "#100e12", "#18151a", "#201c22", "#2a252c")
EBON_END = R("#18151a", "#2a252c", "#4a340e")
GLASS = R("#1a1004", "#3a2408", "#6a4410", "#a0701c")

dungeon("eclipse_cathedral",
        blocks=[
            B("eclipse_marble", "Eclipse Marble", "ashlar", "minecraft:polished_blackstone", args=dict(ramp=MARBLE, mortar=MARBLE_M)),
            B("cathedral_bricks", "Cathedral Bricks", "bricks", "minecraft:stone_bricks", family=("stairs", "slab", "wall"),
              stem="cathedral_brick", stem_title="Cathedral Brick", args=dict(ramp=BURNT, mortar=BURNT_M, crust=(ASH, 0.12))),
            B("ashen_flags", "Ashen Flagstones", "flags", "minecraft:polished_deepslate", family=("slab",), stem="ashen_flag",
              stem_title="Ashen Flag", args=dict(ramp=MARBLE, grout=GILT, crust=(ASH, 0.1))),
            B("fallen_scree", "Fallen Scree", "rock", "minecraft:tuff", args=dict(ramp=BURNT, spread=0.6, crust=(ASH, 0.16))),
            B("eclipse_strata", "Eclipse Strata", "strata", "minecraft:deepslate", args=dict(ramp=ASH, bands=5)),
            B("gilt_plating", "Black-Gilt Plating", "plate", "minecraft:gold_block", args=dict(ramp=GILT, rivet=MARBLE, seams=8)),
            B("eclipse_column", "Eclipse Column", "column", "minecraft:polished_blackstone", args=dict(ramp=MARBLE, mortar=GILT, flutes=6)),
            B("seraph_carving", "Seraph Carving", "carved", "minecraft:chiseled_polished_blackstone", args=dict(ramp=MARBLE, mortar=GILT, motif="sun")),
            B("corona_light", "Corona Light", "glow", "minecraft:shroomlight", light=13, args=dict(ramp=CORONA, base=MARBLE, motif="ring")),
            B("eclipse_window", "Eclipse Window", "tiles", "minecraft:black_stained_glass", args=dict(ramp=GLASS, grout=MARBLE_M, n=4, checker=EBON)),
            B("cathedral_planks", "Cathedral Planks", "planks", "minecraft:dark_oak_planks", tool="axe", args=dict(ramp=EBON, n=4, nails=GILT)),
            B("cathedral_beam", "Cathedral Beam", "log", "minecraft:dark_oak_log", tool="axe", args=dict(ramp=EBON, rings=EBON_END)),
        ],
        props=common_props("eclipse", "Eclipse", metal_color="gold", wood_color="color_black", light=14) + [
            Pp("ash_censer", "plain", "Ash Censer", box=[3, 0, 3, 13, 15, 13], sound="metal", color="gold", strength=2, light=9),
            Pp("fallen_angel", "facing", "Fallen Angel Statue", box=[1, 0, 1, 15, 16, 15], sound="stone", color="color_black", strength=4),
            Pp("black_pew", "facing", "Black Pew", box=[0, 0, 3, 16, 12, 13], sound="wood", color="color_black", strength=2),
            Pp("feather_drift", "plain", "Drift of Black Feathers", box=[0, 0, 0, 16, 3, 16], sound="wool", color="color_black", strength=0.3, solid=False),
        ],
        seal_words="The Warden's halo is the only light the choir door knows", broken_words="The halo burns in the lock and the choir door opens",
        layout=dict(
            palette=dict(
                hall_floor=[("ashen_flags", 4), ("eclipse_marble", 1)], hall_wall=[("cathedral_bricks", 4), ("eclipse_marble", 2),
                                                                                    ("seraph_carving", 1), ("eclipse_window", 1)],
                hall_ceil=[("eclipse_marble", 2), ("gilt_plating", 1)],
                cave_floor=[("fallen_scree", 3), ("eclipse_strata", 1)], cave_wall=[("fallen_scree", 3), ("eclipse_strata", 2),
                                                                                     ("cathedral_bricks", 1)],
                cave_ceil=[("fallen_scree", 3)],
                arena_floor=[("ashen_flags", 3), ("gilt_plating", 1)], arena_wall=[("eclipse_marble", 3), ("seraph_carving", 2),
                                                                                    ("corona_light", 1)],
                bridge=[("cathedral_planks", 1), ("ashen_flags", 1)], rail="cathedral_brick_wall",
                fill="eclipse_strata", pillar="eclipse_column", stairs="cathedral_brick_stairs", slab="cathedral_brick_slab",
                lamp="eclipse_lantern", chain="eclipse_chain", bars="eclipse_bars", coffer="eclipse_coffer", vein="corona_light"),
            seal=7, lamp_every=7, lamp_height=7, veins=0.02,
            rooms=[
                dict(name="the ash steps", kind="cave", w=27, len=28, h=16,
                     dress=[("clusters", dict(name="feather_drift", chance=0.03))], mobs=[("cherub_husk", 4)]),
                dict(name="the burnt nave", kind="hall", w=27, len=46, h=22, chest=True,
                     dress=[("frames", dict(every=5)), ("scatter", dict(name="black_pew", n=10)), ("scatter", dict(name="ash_censer", n=3))],
                     mobs=[("halo_knight", 1), ("cherub_husk", 3), ("fallen_blade", 1)]),
                dict(name="the bell drop", kind="chasm", w=31, len=36, h=20, drop=18, mobs=[("cherub_husk", 4)]),
                dict(name="the cloister", kind="hall", w=25, len=38, h=14, chest=True,
                     dress=[("frames", dict(every=4)), ("scatter", dict(name="fallen_angel", n=4)), ("clusters", dict(name="feather_drift", chance=0.02))],
                     mobs=[("ash_choir", 2), ("fallen_blade", 2)]),
                dict(name="the reliquary vaults", kind="cave", w=31, len=38, h=18, chest=True, zone="hall",
                     dress=[("frames", dict(every=6)), ("scatter", dict(name="ash_censer", n=4)), ("scatter", dict(name="fallen_angel", n=2))],
                     mobs=[("halo_knight", 1), ("ash_choir", 1), ("fallen_blade", 2)], decor=[("cherub_husk", 2)]),
                dict(name="the choir", kind="hall", w=25, len=32, h=20, elite="seraph_warden",
                     dress=[("frames", dict(every=3)), ("scatter", dict(name="black_pew", n=6))], mobs=[("ash_choir", 2)]),
                dict(name="the tower stair", kind="descent", to=14, gap=6),
                dict(name="the eclipse", kind="round", w=49, len=49, h=30, chest=True, ring=12,
                     dress=[("scatter", dict(name="fallen_angel", n=6)), ("clusters", dict(name="feather_drift", chance=0.03)),
                            ("scatter", dict(name="ash_censer", n=4))]),
            ]),
        )
