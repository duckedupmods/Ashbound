"""The Hollow Circus (D): a carnival that died in a cavern and kept performing - the midway, the sideshow tent, the
menagerie of empty cages, the high wire over the pit, the green room, and the big top where the Ringmaster waits.
dforge.py imports this."""
from blockforge import R
from dforge import dungeon, B, Pp, common_props

RED = R("#3a0810", "#561018", "#741a24", "#922432", "#b03242")
CREAM = R("#6a5a48", "#857258", "#a08c6c", "#bca882", "#d6c49c")
DARKRED_M = R("#14040a", "#1e080e", "#2a0c14")
CAVE = R("#140e14", "#1e161e", "#2a202a", "#382c38", "#463848")
SAWDUST = R("#4a3a1e", "#604c28", "#786034", "#907642", "#a88c52")
GILT = R("#4a2e08", "#7a4c10", "#a87018", "#d0961f", "#ecbc34", "#ffdc6a")
BULB = R("#6a3a08", "#a8601a", "#e09a3a", "#ffc870", "#fff0c8")
WAGON = R("#1e0e0a", "#2e1810", "#422418", "#583222", "#70422e")
WAGON_END = R("#4a3020", "#5e3e2a", "#765036")
BLACK = R("#0e0a0e", "#181218", "#221a22", "#2e242e")

dungeon("hollow_circus",
        blocks=[
            B("big_top_canvas", "Big Top Canvas", "stripes", "minecraft:white_wool", tool="hoe", args=dict(a=RED, b=CREAM, width=4)),
            B("circus_boards", "Circus Boards", "planks", "minecraft:spruce_planks", tool="axe", family=("stairs", "slab"),
              stem="circus_board", stem_title="Circus Board", args=dict(ramp=WAGON, n=4, nails=(GILT[1], GILT[4]))),
            B("sawdust", "Packed Sawdust", "rock", "minecraft:packed_mud", tool="shovel", args=dict(ramp=SAWDUST, spread=0.6)),
            B("circus_cavern_rock", "Circus Cavern Rock", "rock", "minecraft:deepslate", args=dict(ramp=CAVE, spread=0.6)),
            B("circus_bricks", "Circus Bricks", "bricks", "minecraft:bricks", family=("stairs", "slab", "wall"), stem="circus_brick",
              stem_title="Circus Brick", args=dict(ramp=RED, mortar=DARKRED_M)),
            B("ring_tiles", "Ring Tiles", "tiles", family=("slab",), stem="ring_tile", stem_title="Ring Tile",
              args=dict(ramp=RED, grout=DARKRED_M, n=2, checker=BLACK)),
            B("gilded_trim", "Gilded Trim", "plate", "minecraft:gold_block", args=dict(ramp=GILT)),
            B("bulb_lights", "Bulb Lights", "glow", "minecraft:redstone_lamp", light=13, args=dict(ramp=BULB, base=RED, motif="ring")),
            B("carved_mask", "Carved Mask Stone", "carved", args=dict(ramp=CREAM, mortar=DARKRED_M, motif="eye")),
            B("circus_pillar", "Circus Pillar", "column", args=dict(ramp=RED, mortar=GILT)),
            B("wagon_beam", "Wagon Beam", "log", "minecraft:spruce_log", tool="axe", args=dict(ramp=WAGON, rings=WAGON_END)),
        ],
        props=common_props("circus", "Circus") + [
            Pp("circus_drum", "plain", "Circus Drum", box=[1, 0, 1, 15, 12, 15], sound="wood", color="color_red", strength=2),
            Pp("circus_cage", "plain", "Menagerie Cage", box=[0, 0, 0, 16, 16, 16], sound="metal", color="gold", strength=4),
            Pp("circus_tent", "facing", "Sideshow Tent", box=[0, 0, 0, 16, 14, 16], sound="wool", color="color_red", strength=1),
            Pp("juggling_clubs", "plain", "Dropped Clubs", box=[2, 0, 2, 14, 4, 14], sound="wood", color="color_white",
               strength=0.5, solid=False),
        ],
        seal_words="The green room is locked from the inside", broken_words="The Harlequin's bell rings the door open",
        layout=dict(
            palette=dict(
                hall_floor=[("circus_boards", 3), ("sawdust", 2)], hall_wall=[("big_top_canvas", 5), ("circus_bricks", 2),
                                                                              ("carved_mask", 1)],
                hall_ceil=[("big_top_canvas", 1)],
                cave_floor=[("sawdust", 3), ("circus_cavern_rock", 2)], cave_wall=[("circus_cavern_rock", 6), ("circus_bricks", 1)],
                cave_ceil=[("circus_cavern_rock", 1)],
                arena_floor=[("ring_tiles", 3), ("sawdust", 2)], arena_wall=[("big_top_canvas", 4), ("gilded_trim", 1),
                                                                            ("bulb_lights", 1)],
                bridge=[("circus_boards", 4), ("gilded_trim", 1)], rail="circus_brick_wall",
                fill="circus_cavern_rock", pillar="circus_pillar", stairs="circus_board_stairs", slab="circus_board_slab",
                lamp="circus_lantern", chain="circus_chain", bars="circus_bars", coffer="circus_coffer", vein="bulb_lights"),
            seal=6, lamp_every=6, lamp_height=7, veins=0.03,
            rooms=[
                dict(name="the midway", kind="cave", w=29, len=36, h=16,
                     dress=[("scatter", dict(name="circus_tent", n=6)), ("scatter", dict(name="circus_drum", n=4)),
                            ("scatter", dict(name="juggling_clubs", n=3))],
                     mobs=[("circus_puppet", 5)], decor=[("circus_puppet", 3)]),
                dict(name="the sideshow tent", kind="hall", w=23, len=28, h=14, chest=True,
                     dress=[("scatter", dict(name="circus_drum", n=4)), ("scatter", dict(name="circus_cage", n=3))],
                     mobs=[("fire_eater", 2), ("knife_juggler", 2)]),
                dict(name="the drop to the cages", kind="descent", to=-8, gap=6),
                dict(name="the menagerie", kind="cave", w=31, len=36, h=14, chest=True,
                     dress=[("scatter", dict(name="circus_cage", n=8))], mobs=[("strongman", 2), ("circus_puppet", 3)]),
                dict(name="the high wire", kind="chasm", w=27, len=30, h=14, drop=28, mobs=[("knife_juggler", 2)]),
                dict(name="the green room", kind="hall", w=21, len=22, h=10, elite="harlequin",
                     dress=[("scatter", dict(name="juggling_clubs", n=4))], mobs=[("fire_eater", 1)]),
                dict(name="the ring stair", kind="descent", to=-16, gap=6),
                dict(name="the big top", kind="round", w=45, len=45, h=28, chest=True, ring=14,
                     dress=[("scatter", dict(name="circus_drum", n=8)), ("scatter", dict(name="juggling_clubs", n=4))]),
            ]),
        )
