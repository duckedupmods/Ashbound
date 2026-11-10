"""The player's manor's furniture (tools/capital_home.py), sculpted like the guild hall's (civic_sculpt.py): real
meshes voxelized at 16 a block, then tools/sculpt.py makes the blocks.

    blender -b -P tools/blender/manor_sculpt.py -- [NAME ...]        (none = all)

Each prop faces north (its front at z = 0), stands on y = 0 and fills x 0..w, z 0..d.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sculpt_props as SP  # noqa: E402

MANOR = ["nightstand", "wardrobe", "washstand", "welsh_dresser", "kitchen_worktable", "pot_rack", "hearth_armchair"]


def knob(x, y, z, r=0.028):
    SP.ball((x, y, z), r, "brass", seg=10)


def panel(x0, y0, x1, y1, z, frame="wood_dark", fill="wood", t=0.035):
    """A raised panel on a front at z: a frame of rails and stiles, the field proud of it."""
    SP.box(x0, y0, z - t, x1, y1, z, frame, bevel=0.006)
    SP.box(x0 + 0.06, y0 + 0.06, z - t - 0.018, x1 - 0.06, y1 - 0.06, z - t + 0.002, fill, bevel=0.01)


@SP.prop("nightstand", 1, 1, 1, V=16)
def nightstand():
    """A small oak bedside cupboard: a drawer over a door, a brass candlestick and a book on top."""
    SP.box(0.1, 0.0, 0.14, 0.9, 0.07, 0.9, "wood_dark", bevel=0.01)                 # the plinth
    SP.box(0.13, 0.07, 0.17, 0.87, 0.62, 0.86, "wood", bevel=0.012)                 # the carcass
    SP.box(0.08, 0.62, 0.11, 0.92, 0.69, 0.91, "wood_dark", bevel=0.015)            # the top
    panel(0.17, 0.4, 0.83, 0.58, 0.17)                                              # the drawer
    knob(0.5, 0.49, 0.11)
    panel(0.17, 0.1, 0.83, 0.37, 0.17)                                              # the door
    knob(0.75, 0.24, 0.11, 0.024)
    SP.lathe((0.3, 0.69, 0.42), [(0.0, 0.09), (0.02, 0.1), (0.03, 0.04), (0.11, 0.03), (0.12, 0.045)], "brass", seg=20)
    SP.candle(0.3, 0.81, 0.42, h=0.13, r=0.024)
    SP.book(0.5, 0.69, 0.3, 0.3, 0.06, 0.4, "leather_red", ang=12)


@SP.prop("wardrobe", 2, 2, 1, V=16)
def wardrobe():
    """A tall two-door oak wardrobe: panelled doors, brass pulls, a moulded cornice, bun feet."""
    for x in (0.12, 1.88):
        for z in (0.2, 0.86):
            SP.ball((x, 0.05, z), 0.07, "wood_dark", seg=12)                         # bun feet
    SP.box(0.04, 0.08, 0.12, 1.96, 0.16, 0.96, "wood_dark", bevel=0.01)             # the base moulding
    SP.box(0.07, 0.16, 0.15, 1.93, 1.82, 0.94, "wood", bevel=0.012)                 # the carcass
    SP.box(0.03, 1.82, 0.1, 1.97, 1.89, 0.98, "wood_dark", bevel=0.012)             # the cornice
    SP.box(0.0, 1.89, 0.07, 2.0, 1.95, 1.0, "wood_dark", bevel=0.012)
    SP.prism([(0.3, 1.95), (1.7, 1.95), (1.55, 1.99), (0.45, 1.99)], 0.12, 0.2, "wood_dark")
    for x0, x1 in ((0.11, 0.98), (1.02, 1.89)):                                     # the doors
        panel(x0, 0.2, x1, 0.92, 0.15)
        panel(x0, 0.96, x1, 1.78, 0.15)
    for x in (0.92, 1.08):
        SP.cyl((x, 0.9, 0.08), (x, 1.08, 0.08), 0.016, "brass", seg=8)
        SP.box(x - 0.025, 0.88, 0.08, x + 0.025, 0.9, 0.12, "brass", bevel=0.0)
        SP.box(x - 0.025, 1.08, 0.08, x + 0.025, 1.1, 0.12, "brass", bevel=0.0)
    SP.box(0.98, 0.2, 0.1, 1.02, 1.78, 0.15, "wood_dark", bevel=0.004)              # the meeting stile


@SP.prop("washstand", 1, 2, 1, V=16)
def washstand():
    """A marble-topped washstand: a blue-glazed basin and jug, a towel on its rail, a mirror on the back posts."""
    for x in (0.1, 0.82):
        SP.box(x, 0.0, 0.14, x + 0.08, 0.74, 0.22, "wood_dark", bevel=0.01)          # front legs
        SP.box(x, 0.0, 0.78, x + 0.08, 1.74, 0.86, "wood_dark", bevel=0.01)          # back posts, up to the mirror
        SP.ball((x + 0.04, 1.77, 0.82), 0.045, "wood", seg=10)
    SP.box(0.12, 0.2, 0.16, 0.88, 0.24, 0.84, "wood", bevel=0.006)                  # the shelf under
    SP.box(0.12, 0.6, 0.16, 0.88, 0.72, 0.84, "wood", bevel=0.008)                  # the apron
    SP.box(0.05, 0.72, 0.1, 0.95, 0.78, 0.9, "marble", bevel=0.012)                 # the marble top
    SP.bowl((0.42, 0.78, 0.46), [(0.0, 0.1), (0.04, 0.2), (0.11, 0.25)], 0.025, "tile_blue", seg=28)
    SP.lathe((0.42, 0.8, 0.46), [(0.0, 0.17), (0.06, 0.2)], "water", seg=24)
    SP.lathe((0.76, 0.78, 0.66), [(0.0, 0.06), (0.04, 0.09), (0.16, 0.1), (0.24, 0.06), (0.29, 0.05), (0.31, 0.065)],
             "tile_blue", seg=20)                                                    # the jug
    SP.cyl((0.84, 0.98, 0.66), (0.9, 0.9, 0.66), 0.014, "tile_blue", seg=8)
    SP.box(0.04, 0.4, 0.12, 0.08, 0.66, 0.88, "wood_dark", bevel=0.004)            # the towel rail, a towel over it
    SP.box(0.0, 0.42, 0.25, 0.1, 0.66, 0.72, "towel", bevel=0.02)
    SP.box(0.16, 0.96, 0.8, 0.84, 1.66, 0.86, "wood_dark", bevel=0.012)             # the mirror's frame
    SP.box(0.22, 1.02, 0.79, 0.78, 1.6, 0.8, "silver", bevel=0.0)
    SP.prism([(0.16, 1.66), (0.84, 1.66), (0.7, 1.74), (0.3, 1.74)], 0.8, 0.86, "wood_dark")


@SP.prop("welsh_dresser", 2, 2, 1, V=16)
def welsh_dresser():
    """A kitchen dresser: cupboards and drawers below, open plate racks above with willow-blue plates stood on edge,
    jugs on the counter, cups hung under the shelf."""
    SP.box(0.03, 0.0, 0.1, 1.97, 0.08, 0.98, "wood_dark", bevel=0.01)
    SP.box(0.05, 0.08, 0.13, 1.95, 0.84, 0.96, "wood", bevel=0.012)
    SP.box(0.0, 0.84, 0.06, 2.0, 0.9, 1.0, "wood_dark", bevel=0.012)                 # the counter
    for x0, x1 in ((0.09, 0.97), (1.03, 1.91)):
        panel(x0, 0.62, x1, 0.8, 0.13)                                               # drawers
        knob((x0 + x1) / 2, 0.71, 0.08)
        panel(x0, 0.12, x1, 0.58, 0.13)                                              # cupboards
        knob(x1 - 0.1 if x0 < 1 else x0 + 0.1, 0.36, 0.08, 0.024)
    SP.box(0.06, 0.9, 0.86, 1.94, 1.86, 0.96, "wood", bevel=0.006)                  # the rack's back
    for x in (0.03, 1.89):
        SP.box(x, 0.9, 0.6, x + 0.08, 1.88, 0.98, "wood_dark", bevel=0.01)           # its sides
    SP.box(0.0, 1.86, 0.54, 2.0, 1.94, 1.0, "wood_dark", bevel=0.012)                # its cornice
    for y in (1.22, 1.54):
        SP.box(0.08, y, 0.62, 1.92, y + 0.04, 0.96, "wood_dark", bevel=0.005)        # shelves
        SP.box(0.08, y + 0.04, 0.62, 1.92, y + 0.07, 0.65, "wood_dark", bevel=0.0)   # the plate rail
    for y in (0.92, 1.26, 1.58):                                                     # plates on edge, leaning back
        for k, x in enumerate((0.3, 0.68, 1.06, 1.44, 1.76)):
            if y == 0.92 and k in (1, 3):
                continue
            r = 0.13 if k % 2 else 0.15
            SP.cyl((x, y + r + 0.01, 0.84), (x, y + r + 0.02, 0.8), r, "tile_blue", seg=24)
            SP.cyl((x, y + r + 0.01, 0.8), (x, y + r + 0.015, 0.795), r * 0.6, "marble", seg=20)
    SP.lathe((0.68, 0.9, 0.5), [(0.0, 0.08), (0.12, 0.1), (0.2, 0.07), (0.24, 0.08)], "marble", seg=18)  # a jug
    SP.lathe((1.44, 0.9, 0.48), [(0.0, 0.05), (0.08, 0.12), (0.12, 0.13)], "tile_blue", seg=20)          # a bowl
    for x in (0.4, 0.8, 1.2, 1.6):                                                   # cups on hooks
        SP.lathe((x, 1.08, 0.66), [(0.0, 0.035), (0.09, 0.045)], "marble", seg=12)
        SP.cyl((x, 1.17, 0.66), (x, 1.22, 0.66), 0.006, "brass", seg=6)


@SP.prop("kitchen_worktable", 2, 1, 1, V=16)
def kitchen_worktable():
    """A cook's butcher-block table: a cutting board with a loaf and a knife, carrots and a cabbage, a copper pan,
    baskets of onions on the shelf under."""
    for x in (0.06, 1.84):
        for z in (0.08, 0.8):
            SP.box(x, 0.0, z, x + 0.1, 0.8, z + 0.1, "wood_dark", bevel=0.012)
    SP.box(0.08, 0.16, 0.1, 1.92, 0.2, 0.88, "wood", bevel=0.006)                   # the shelf
    SP.box(0.0, 0.8, 0.02, 2.0, 0.93, 0.98, "wood_end", bevel=0.02)                  # the block top
    SP.box(0.15, 0.93, 0.25, 0.85, 0.96, 0.75, "wood", bevel=0.01)                   # the board
    SP.ellip((0.45, 1.02, 0.5), (0.2, 0.07, 0.11), "clay_fired", seg=16)            # the loaf
    for k in range(4):
        SP.box(0.3 + k * 0.09, 1.07, 0.42, 0.33 + k * 0.09, 1.09, 0.58, "straw", bevel=0.0)
    SP.box(0.6, 0.96, 0.3, 0.84, 0.975, 0.36, "steel", bevel=0.0)                    # the knife
    SP.box(0.84, 0.955, 0.29, 0.96, 0.985, 0.37, "wood_dark", bevel=0.005)
    for k in range(3):                                                               # carrots
        z = 0.3 + k * 0.12
        SP.cyl((1.05, 0.96, z), (1.32, 0.95, z + 0.03), 0.035, "terracotta", r2=0.01, seg=10)
        SP.cyl((1.0, 0.96, z), (1.05, 0.96, z), 0.02, "leaf", seg=6)
    SP.ball((1.55, 1.04, 0.4), 0.11, "leaf", seg=16)                                 # a cabbage
    SP.ball((1.55, 1.06, 0.4), 0.08, "leaf_dark", seg=12)
    SP.lathe((1.6, 0.93, 0.75), [(0.0, 0.14), (0.07, 0.15)], "copper", seg=24)      # the pan, its handle off the edge
    SP.cyl((1.6, 0.98, 0.75), (1.98, 0.99, 0.94), 0.018, "iron_dark", seg=8)
    for x in (0.5, 1.4):                                                             # baskets on the shelf
        SP.lathe((x, 0.2, 0.5), [(0.0, 0.2), (0.22, 0.24)], "straw", seg=20)
        for k in range(5):
            a = k * 1.25
            SP.ball((x + math.cos(a) * 0.1, 0.42, 0.5 + math.sin(a) * 0.1), 0.06, "terracotta" if x < 1 else "wax", seg=10)


@SP.prop("pot_rack", 2, 1, 1, V=16)
def pot_rack():
    """A wrought-iron rack hung from the beams on chains, copper pans and a ladle on its hooks, garlic and herbs."""
    for x in (0.1, 1.9):
        SP.chain((x, 1.0, 0.5), (x, 0.74, 0.5), "iron_dark")
    SP.box(0.04, 0.7, 0.42, 1.96, 0.74, 0.58, "iron_dark", bevel=0.005)
    for x in (0.04, 1.92):
        SP.box(x, 0.66, 0.42, x + 0.04, 0.74, 0.58, "iron_dark", bevel=0.0)
    hooks = (0.3, 0.62, 0.95, 1.3, 1.65)
    for x in hooks:
        SP.cyl((x, 0.7, 0.5), (x, 0.6, 0.5), 0.01, "iron_dark", seg=6)
    for x, r in ((0.3, 0.17), (0.95, 0.14), (1.65, 0.19)):                          # pans, hung by their handles
        SP.cyl((x, 0.6, 0.5), (x, 0.4, 0.5), 0.016, "copper_dark", seg=8)
        SP.cyl((x, 0.4 - r, 0.47), (x, 0.4 - r, 0.53), r, "copper", seg=24)
        SP.cyl((x, 0.4 - r, 0.465), (x, 0.4 - r, 0.47), r * 0.75, "copper_dark", seg=20)
    SP.cyl((0.62, 0.6, 0.5), (0.62, 0.3, 0.5), 0.012, "steel", seg=6)              # the ladle
    SP.ball((0.62, 0.27, 0.5), 0.05, "steel", seg=10)
    for k in range(3):                                                               # garlic
        SP.ball((1.3 + (k - 1) * 0.04, 0.5 - k * 0.07, 0.5), 0.045, "wax", seg=10)
    SP.cyl((1.3, 0.6, 0.5), (1.3, 0.38, 0.5), 0.008, "rope", seg=6)
    for x in (0.47, 1.12, 1.48):                                                     # herbs hung head down
        SP.cyl((x, 0.7, 0.5), (x, 0.56, 0.5), 0.01, "rope", seg=6)
        SP.cyl((x, 0.56, 0.5), (x, 0.38, 0.5), 0.05, "herb", r2=0.02, seg=10)


@SP.prop("hearth_armchair", 1, 2, 1, V=16)
def hearth_armchair():
    """A wingback armchair for the fireside: green leather over oak, rolled arms, brass-nailed, a folded rug on it."""
    for x in (0.1, 0.82):
        SP.box(x, 0.0, 0.1, x + 0.08, 0.2, 0.18, "wood_dark", bevel=0.012)          # turned front feet
        SP.box(x, 0.0, 0.8, x + 0.08, 0.2, 0.88, "wood_dark", bevel=0.012)
    SP.box(0.06, 0.2, 0.08, 0.94, 0.42, 0.92, "leather_green", bevel=0.04)          # the seat's base
    SP.box(0.16, 0.42, 0.12, 0.84, 0.52, 0.82, "leather_green", bevel=0.05)         # the cushion
    SP.box(0.08, 0.42, 0.78, 0.92, 1.36, 0.94, "leather_green", bevel=0.05)         # the back
    SP.ellip((0.5, 1.34, 0.86), (0.42, 0.08, 0.08), "leather_green", seg=20)
    for s, x in ((-1, 0.04), (1, 0.96)):
        SP.box(min(x, x - s * 0.14), 0.42, 0.2, max(x, x - s * 0.14), 0.62, 0.92, "leather_green", bevel=0.04)   # arms
        SP.cyl((x - s * 0.07, 0.62, 0.12), (x - s * 0.07, 0.62, 0.9), 0.08, "leather_green", seg=16)            # rolled
        SP.box(min(x, x - s * 0.12), 0.62, 0.6, max(x, x - s * 0.12), 1.26, 0.92, "leather_green", bevel=0.04)  # wings
        for k in range(6):
            SP.ball((x - s * 0.07 + s * 0.0, 0.52, 0.16 + k * 0.13), 0.016, "brass", seg=6)
    SP.box(0.2, 0.52, 0.3, 0.8, 0.6, 0.6, "cloth_red", bevel=0.03)                  # a folded rug
    SP.box(0.2, 0.56, 0.3, 0.8, 0.565, 0.6, "towel", bevel=0.0)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    for n in (args or MANOR):
        SP.build(n)
