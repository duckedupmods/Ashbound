"""The Abyssal Lighthouse (S): a lighthouse on a black reef in a dead sea, and the way goes down under it - the reef,
the jetty of wrecked boats, the tower stair into the rock, the keeper's cellars, the drowned grotto, the wreck hall,
the whale fall, and the Lamp Below where the Keeper in the Light waits. Dark on purpose: black wet rock, rotten teal
wood, tarnished brass, barnacles, a pale sea glow, and warm gold only at the lamps. dforge.py imports this."""
from blockforge import R
from dforge import dungeon, B, Pp, common_props

WETROCK = R("#040608", "#080c10", "#0e1418", "#141c22", "#1c262e", "#26323a")
BARN = R("#3a3a34", "#585850", "#7a786c")
TEAL = R("#061412", "#0a201c", "#102c28", "#183a34", "#204840")
TEAL_END = R("#102c28", "#183a34", "#204840")
BRASS = R("#1e1608", "#34260e", "#4c3816", "#664c20", "#80622c")
STONE = R("#141618", "#1e2124", "#2a2e32", "#363b40", "#444a50")
STONE_M = R("#060708", "#0a0c0e", "#101214")
SEAGLOW = R("#2a4a4a", "#4a7a78", "#7ab0aa", "#b4e4dc", "#e8fff8")
BONE = R("#3a3a32", "#5a5a4e", "#7a786a", "#9a9888", "#bab8a6")
BONE_M = R("#1a1a14", "#26261e", "#323228")

dungeon("abyssal_lighthouse",
        blocks=[
            B("reef_rock", "Black Reef Rock", "rock", "minecraft:deepslate", args=dict(ramp=WETROCK, spread=0.6, crust=(BARN, 0.1))),
            B("abyss_strata", "Abyss Strata", "strata", "minecraft:deepslate", args=dict(ramp=WETROCK, bands=6)),
            B("lighthouse_bricks", "Lighthouse Bricks", "bricks", "minecraft:deepslate_bricks", family=("stairs", "slab", "wall"),
              stem="lighthouse_brick", stem_title="Lighthouse Brick", args=dict(ramp=STONE, mortar=STONE_M, crust=(BARN, 0.06))),
            B("wet_flags", "Wet Flagstones", "flags", "minecraft:polished_deepslate", family=("slab",), stem="wet_flag",
              stem_title="Wet Flag", args=dict(ramp=STONE, grout=STONE_M)),
            B("wreck_planks", "Wreck Planks", "planks", "minecraft:warped_planks", tool="axe", args=dict(ramp=TEAL, n=4, nails=BRASS)),
            B("wreck_beam", "Wreck Beam", "log", "minecraft:warped_stem", tool="axe", args=dict(ramp=TEAL, rings=TEAL_END)),
            B("tide_brass", "Tide Brass", "plate", "minecraft:copper_block", args=dict(ramp=BRASS, rivet=TEAL, seams=8)),
            B("whalebone", "Whalebone", "column", "minecraft:bone_block", args=dict(ramp=BONE, mortar=BONE_M, flutes=3)),
            B("whalebone_block", "Whalebone Block", "ashlar", "minecraft:bone_block", args=dict(ramp=BONE, mortar=BONE_M)),
            B("sea_glow", "Sea Glow", "glow", "minecraft:sea_lantern", light=9, args=dict(ramp=SEAGLOW, base=WETROCK, motif="vein")),
            B("lens_carving", "Lens Carving", "carved", "minecraft:chiseled_deepslate", args=dict(ramp=STONE, mortar=BRASS, motif="ring")),
        ],
        props=common_props("abyss", "Abyss", metal_color="color_orange", wood_color="color_cyan", light=13) + [
            Pp("oil_barrels", "plain", "Lamp Oil Barrels", box=[1, 0, 1, 15, 14, 15], sound="wood", color="color_cyan", strength=2),
            Pp("rope_net", "plain", "Hanging Nets", box=[0, 0, 0, 16, 16, 16], sound="wool", color="color_brown", strength=0.5, solid=False),
            Pp("ship_wheel", "facing", "Ship's Wheel", box=[1, 0, 6, 15, 16, 10], sound="wood", color="color_cyan", strength=2),
            Pp("diving_helmet", "plain", "Drowned Diving Helmet", box=[3, 0, 3, 13, 10, 13], sound="metal", color="color_orange", strength=2, light=3),
        ],
        seal_words="The Angler's lure is the only light that opens this door", broken_words="The lure lights the door and it opens",
        layout=dict(
            palette=dict(
                hall_floor=[("wet_flags", 3), ("wreck_planks", 1)], hall_wall=[("lighthouse_bricks", 4), ("lens_carving", 1),
                                                                                ("tide_brass", 1)],
                hall_ceil=[("wreck_planks", 2), ("lighthouse_bricks", 1)],
                cave_floor=[("reef_rock", 3), ("abyss_strata", 1)], cave_wall=[("reef_rock", 3), ("abyss_strata", 2)],
                cave_ceil=[("reef_rock", 3)],
                arena_floor=[("wet_flags", 2), ("reef_rock", 2)], arena_wall=[("reef_rock", 3), ("lighthouse_bricks", 2),
                                                                              ("sea_glow", 1)],
                bridge=[("wreck_planks", 2)], rail="lighthouse_brick_wall",
                fill="abyss_strata", pillar="wreck_beam", stairs="lighthouse_brick_stairs", slab="lighthouse_brick_slab",
                lamp="abyss_lantern", chain="abyss_chain", bars="abyss_bars", coffer="abyss_coffer", vein="sea_glow"),
            seal=7, lamp_every=9, lamp_height=6, veins=0.03,
            rooms=[
                dict(name="the reef", kind="cave", w=25, len=24, h=14, mobs=[("deep_thing", 3)]),
                dict(name="the jetty", kind="chasm", w=31, len=40, h=16, drop=16,
                     mobs=[("deep_thing", 4)]),
                dict(name="the tower stair", kind="descent", to=-12, gap=6),
                dict(name="the keeper's cellars", kind="hall", w=25, len=34, h=12, chest=True,
                     dress=[("frames", dict(every=5)), ("scatter", dict(name="oil_barrels", n=8)), ("scatter", dict(name="rope_net", n=4))],
                     mobs=[("drowned_keeper", 1), ("deep_thing", 3)]),
                dict(name="the drowned grotto", kind="cave", w=33, len=40, h=18, chest=True,
                     dress=["pools", ("scatter", dict(name="diving_helmet", n=3))], mobs=[("lamp_siren", 2), ("eyeless", 2)],
                     decor=[("deep_thing", 2)]),
                dict(name="the wreck hall", kind="cave", w=33, len=40, h=20, chest=True, zone="hall",
                     dress=[("frames", dict(every=6)), ("scatter", dict(name="ship_wheel", n=3)), ("scatter", dict(name="oil_barrels", n=4))],
                     mobs=[("drowned_keeper", 1), ("eyeless", 2), ("lamp_siren", 1)]),
                dict(name="the whale fall", kind="hall", w=23, len=34, h=16, elite="angler_knight",
                     dress=[("frames", dict(every=3))], mobs=[("deep_thing", 3)]),
                dict(name="the lamp below", kind="round", w=49, len=49, h=28, chest=True, ring=12,
                     dress=["pools", ("scatter", dict(name="diving_helmet", n=4))]),
            ]),
        )
