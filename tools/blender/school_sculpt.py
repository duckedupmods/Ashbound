"""The Arcanum's classrooms and the city's gardens, sculpted like the other props and made into blocks by
tools/sculpt.py:

  - school_desk: a student's oak desk, its lid sloped to the sitter, an open book on it, an inkwell and quill on the
    flat strip at its head, a candle stub. Give it the same facing as the school_chair behind it: the sitter looks
    `facing` across it (the desk's own back, z = 1, is the sitter's side).
  - school_chair: a plain oak chair with a violet cushion and a pointed crest rail; the sitter looks `facing`.
  - master_desk: the master's panelled desk, its front to the class: grimoires, a skull with a candle on it, a
    crystal ball on a brass stand, a scroll.
  - rune_board: the slate board on the classroom wall in an oak frame, chalked with sigils round a glowing circle,
    a ledge of chalk and a sponge; its back to the wall.
  - topiary_pot, flower_tub, rose_bush, hydrangea: the gardens' pieces for doorsteps, squares and beds.

    blender -b -P tools/blender/school_sculpt.py -- [NAME ...]        (none = all)     then  python tools/sculpt.py

Game axes in blocks, each prop facing north (its front at z = 0); seen from the front the viewer's right is -x.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sculpt_props as SP  # noqa: E402


# ================================================================ the classroom

@SP.prop("school_desk", 1, 1, 1, V=16)
def school_desk():
    for x in (0.1, 0.82):
        for z in (0.1, 0.82):
            SP.box(x, 0.0, z, x + 0.08, 0.66, z + 0.08, "wood_dark", bevel=0.012)       # legs
        SP.box(x + 0.01, 0.12, 0.18, x + 0.07, 0.17, 0.82, "wood", bevel=0.005)        # side stretchers
    SP.box(0.18, 0.06, 0.4, 0.82, 0.1, 0.6, "wood", bevel=0.005)                        # the foot bar
    SP.box(0.08, 0.5, 0.08, 0.92, 0.66, 0.92, "wood_dark", bevel=0.01)                 # the book well
    SP.box(0.07, 0.66, 0.06, 0.93, 0.74, 0.3, "wood", bevel=0.012)                     # the flat strip at its head
    SP.prism([(0.3, 0.66), (0.3, 0.75), (0.95, 0.68), (0.95, 0.66)], 0.07, 0.93, "wood", plane="zy")   # the lid
    SP.prism([(0.3, 0.745), (0.3, 0.76), (0.95, 0.69), (0.95, 0.675)], 0.07, 0.93, "wood_dark", plane="zy")
    # the open book on the lid: two pages either side of the spine, a red cover under them
    SP.prism([(0.42, 0.755), (0.42, 0.768), (0.86, 0.72), (0.86, 0.707)], 0.22, 0.78, "leather_red", plane="zy")
    for x0, x1 in ((0.24, 0.49), (0.51, 0.76)):
        SP.prism([(0.44, 0.768), (0.44, 0.786), (0.84, 0.742), (0.84, 0.724)], x0, x1, "paper", plane="zy")
    for k in range(5):                                                                    # lines of writing
        z = 0.5 + k * 0.065
        y = 0.787 - (z - 0.44) * 0.11
        for x0, x1 in ((0.27, 0.46), (0.54, 0.73)):
            SP.box(x0, y, z, x1 - (0.05 if k == 4 else 0), y + 0.006, z + 0.012, "ink", bevel=0.0)
    SP.cyl((0.75, 0.74, 0.17), (0.75, 0.82, 0.17), 0.045, "glass", seg=14)              # the inkwell
    SP.cyl((0.75, 0.74, 0.17), (0.75, 0.8, 0.17), 0.038, "ink", seg=14)
    SP.cyl((0.75, 0.82, 0.17), (0.75, 0.84, 0.17), 0.025, "brass", seg=10)
    SP.caps((0.76, 0.8, 0.17), (0.6, 1.0, 0.24), 0.01, 0.006, "wood", seg=6)            # the quill
    SP.ellip((0.64, 0.95, 0.225), (0.035, 0.07, 0.012), "paper", rot=(0, 25, 38), seg=10)
    SP.cyl((0.24, 0.74, 0.18), (0.24, 0.76, 0.18), 0.06, "brass", seg=14)              # the candle stub
    SP.candle(0.24, 0.76, 0.18, h=0.08, r=0.028)


@SP.prop("school_chair", 1, 1, 1, V=16)
def school_chair():
    for x in (0.16, 0.78):
        SP.box(x, 0.0, 0.14, x + 0.07, 0.44, 0.21, "wood_dark", bevel=0.012)        # front legs
        SP.box(x, 0.0, 0.76, x + 0.07, 0.98, 0.84, "wood_dark", bevel=0.012)       # back posts
        SP.ball((x + 0.035, 1.0, 0.8), 0.04, "wood", seg=12)
        SP.box(x + 0.01, 0.13, 0.21, x + 0.06, 0.17, 0.76, "wood", bevel=0.005)    # side stretchers
    SP.box(0.23, 0.13, 0.16, 0.78, 0.17, 0.2, "wood", bevel=0.005)
    SP.box(0.14, 0.42, 0.12, 0.86, 0.48, 0.86, "wood", bevel=0.02)                  # the seat
    SP.box(0.2, 0.48, 0.16, 0.8, 0.53, 0.8, "leather_violet", bevel=0.025)         # its cushion
    for x in (0.34, 0.47, 0.6):                                                     # the back's slats
        SP.box(x, 0.52, 0.79, x + 0.07, 0.84, 0.83, "wood", bevel=0.008)
    SP.prism([(0.2, 0.84), (0.8, 0.84), (0.8, 0.9), (0.5, 0.97), (0.2, 0.9)], 0.77, 0.85, "wood_dark")   # crest rail
    SP.box(0.2, 0.52, 0.77, 0.8, 0.56, 0.85, "wood_dark", bevel=0.008)


@SP.prop("master_desk", 2, 1, 1, V=16)
def master_desk():
    SP.box(0.04, 0.0, 0.08, 1.96, 0.08, 0.94, "wood_dark", bevel=0.02)             # the plinth
    for x0, x1 in ((0.06, 0.6), (1.4, 1.94)):                                       # the pedestals, panelled
        SP.box(x0, 0.08, 0.1, x1, 0.76, 0.92, "wood", bevel=0.015)
        SP.box(x0 + 0.06, 0.16, 0.07, x1 - 0.06, 0.4, 0.1, "wood_dark", bevel=0.01)
        SP.box(x0 + 0.06, 0.46, 0.07, x1 - 0.06, 0.7, 0.1, "wood_dark", bevel=0.01)
        for y in (0.28, 0.58):
            SP.ball(((x0 + x1) / 2, y, 0.06), 0.025, "brass", seg=10)
    SP.box(0.6, 0.5, 0.12, 1.4, 0.76, 0.2, "wood", bevel=0.01)                      # the modesty panel
    SP.box(0.66, 0.54, 0.1, 1.34, 0.72, 0.12, "leather_violet", bevel=0.01)
    SP.box(0.0, 0.76, 0.04, 2.0, 0.84, 0.96, "wood_dark", bevel=0.025)             # the top
    SP.box(0.1, 0.84, 0.14, 1.9, 0.85, 0.86, "leather_green", bevel=0.005)
    # the grimoires stacked at one end, one open by the middle
    SP.book(0.15, 0.85, 0.2, 0.32, 0.07, 0.42, "leather_red")
    SP.book(0.18, 0.92, 0.24, 0.28, 0.06, 0.36, "leather_blue", ang=8)
    SP.book(0.16, 0.98, 0.22, 0.3, 0.05, 0.4, "leather_violet", ang=-5)
    SP.box(0.7, 0.85, 0.3, 1.25, 0.87, 0.7, "leather", bevel=0.004)
    SP.box(0.72, 0.87, 0.32, 0.97, 0.9, 0.68, "paper", bevel=0.003)
    SP.box(0.98, 0.87, 0.32, 1.23, 0.9, 0.68, "paper", bevel=0.003)
    # the skull with its candle
    SP.ball((1.55, 0.97, 0.6), (0.1, 0.1, 0.12), "bone", seg=18)
    SP.ball((1.55, 0.92, 0.5), (0.07, 0.05, 0.05), "bone", seg=12)
    for sx in (-1, 1):
        SP.cut(SP.ball((1.55 + sx * 0.04, 0.97, 0.49), 0.028, "x", seg=10))
    SP.candle(1.55, 1.06, 0.6, h=0.14, r=0.03)
    SP.ellip((1.55, 1.04, 0.6), (0.05, 0.02, 0.05), "wax", seg=12)
    # the crystal ball on its brass claw
    SP.lathe((1.78, 0.85, 0.3), [(0.0, 0.08), (0.03, 0.08), (0.06, 0.04), (0.1, 0.06)], "brass", seg=20)
    SP.ball((1.78, 1.0, 0.3), 0.09, "crystal_cyan", seg=20)
    # a scroll and a quill
    SP.cyl((0.6, 0.875, 0.8), (1.1, 0.875, 0.8), 0.025, "paper", seg=12)
    SP.caps((1.3, 0.86, 0.75), (1.5, 0.88, 0.85), 0.008, 0.005, "paper", seg=6)


SIGILS = [  # chalk strokes on the board in its own (s across from its left, t up) metres
    ((0.25, 1.55), (0.6, 1.55)), ((0.25, 1.45), (0.5, 1.45)), ((0.25, 1.35), (0.55, 1.35)),
    ((0.25, 1.1), (0.45, 1.25)), ((0.45, 1.25), (0.6, 1.05)), ((0.3, 1.0), (0.6, 1.0)),
    ((0.25, 0.85), (0.62, 0.85)), ((0.25, 0.75), (0.48, 0.75)),
    ((2.4, 1.55), (2.75, 1.55)), ((2.4, 1.45), (2.7, 1.45)), ((2.45, 1.2), (2.75, 1.2)),
    ((2.6, 1.32), (2.6, 0.95)), ((2.45, 0.95), (2.75, 0.95)), ((2.4, 0.8), (2.72, 0.8)),
]


@SP.prop("rune_board", 3, 2, 1, V=16)
def rune_board():
    SP.box(0.06, 0.5, 0.82, 2.94, 1.86, 1.0, "wood_dark", bevel=0.03)               # the frame
    SP.box(0.14, 0.58, 0.8, 2.86, 1.78, 0.84, "slate", bevel=0.005)                 # the slate
    SP.prism([(0.06, 1.86), (2.94, 1.86), (2.94, 1.9), (1.5, 1.98), (0.06, 1.9)], 0.8, 1.0, "wood_dark")
    SP.ball((1.5, 1.93, 0.84), 0.05, "brass", seg=12)
    for s0, t0, s1, t1 in [(*a, *b) for a, b in SIGILS]:                            # chalk notes either side
        L = math.hypot(s1 - s0, t1 - t0)
        n = max(1, int(L / 0.03))
        for k in range(n + 1):
            u = k / n
            x, y = 3.0 - (s0 + (s1 - s0) * u), t0 + (t1 - t0) * u
            SP.box(x - 0.018, y - 0.018, 0.785, x + 0.018, y + 0.018, 0.8, "chalk", bevel=0.0)
    c = (1.5, 1.18)                                                                 # the circle in the middle, alight
    SP.torus((c[0], c[1], 0.79), 0.46, 0.02, "rune_glow", normal=(0, 0, 1), seg=64, tseg=6)
    SP.torus((c[0], c[1], 0.79), 0.34, 0.015, "rune_glow", normal=(0, 0, 1), seg=56, tseg=6)
    for k in range(6):
        a0, a1 = k * math.pi / 3, (k + 2) * math.pi / 3
        p0 = (c[0] + 0.34 * math.cos(a0), c[1] + 0.34 * math.sin(a0))
        p1 = (c[0] + 0.34 * math.cos(a1), c[1] + 0.34 * math.sin(a1))
        SP.caps((p0[0], p0[1], 0.79), (p1[0], p1[1], 0.79), 0.013, 0.013, "rune_glow", seg=6)
        p = (c[0] + 0.4 * math.cos(a0 + math.pi / 6), c[1] + 0.4 * math.sin(a0 + math.pi / 6))
        SP.ball((p[0], p[1], 0.79), 0.03, "rune_glow", seg=8)
    SP.box(0.14, 0.52, 0.66, 2.86, 0.58, 0.84, "wood", bevel=0.01)                  # the chalk ledge
    for k, x in enumerate((0.5, 0.62, 2.2)):
        SP.cyl((x, 0.6, 0.74), (x + 0.09, 0.6, 0.72), 0.014, "chalk", seg=8)
    SP.box(2.4, 0.58, 0.68, 2.6, 0.65, 0.78, "straw", bevel=0.015)                  # the sponge


# ================================================================ the gardens

def leaf_mass(c, r, rnd, n, mats=("leaf", "leaf_dark"), size=0.07):
    """A dome of leaves: many small tilted leaves over a solid core, so it reads leafy at block scale."""
    SP.ball(c, (r[0] * 0.86, r[1] * 0.86, r[2] * 0.86), "leaf_dark", seg=20)
    for k in range(n):
        u, v = rnd.uniform(-1, 1), rnd.uniform(0, 2 * math.pi)
        s = math.sqrt(1 - u * u)
        d = (s * math.cos(v), u, s * math.sin(v))
        if d[1] < -0.35:
            continue
        p = (c[0] + d[0] * r[0], c[1] + d[1] * r[1], c[2] + d[2] * r[2])
        SP.ellip(p, (size, size * 0.4, size * 0.7), rnd.choice(mats),
                 rot=(rnd.uniform(-60, 60), rnd.uniform(0, 180), rnd.uniform(-60, 60)), seg=8)


def bloom(c, r, mat, rnd, n=7):
    """A flower head: a cluster of petal balls round a darker heart."""
    for k in range(n):
        a = 2 * math.pi * k / n + rnd.uniform(-0.3, 0.3)
        SP.ball((c[0] + math.cos(a) * r * 0.6, c[1] + rnd.uniform(-0.2, 0.3) * r, c[2] + math.sin(a) * r * 0.6), r * 0.55, mat, seg=8)
    SP.ball(c, r * 0.6, mat, seg=10)


@SP.prop("topiary_pot", 1, 2, 1, V=16)
def topiary_pot():
    """A bay tree clipped to a ball on a straight stem in a ribbed terracotta pot."""
    SP.lathe((0.5, 0, 0.5), [(0, 0.2), (0.04, 0.24), (0.36, 0.3), (0.4, 0.34), (0.46, 0.34), (0.48, 0.31)], "terracotta", seg=32)
    for k in range(16):                                                               # ribs
        a = 2 * math.pi * k / 16
        SP.cyl((0.5 + math.cos(a) * 0.235, 0.05, 0.5 + math.sin(a) * 0.235),
               (0.5 + math.cos(a) * 0.29, 0.36, 0.5 + math.sin(a) * 0.29), 0.014, "terracotta", seg=6)
    SP.lathe((0.5, 0.0, 0.5), [(0.43, 0.29), (0.45, 0.29)], "soil", seg=24)
    SP.cyl((0.5, 0.44, 0.5), (0.5, 1.12, 0.5), 0.03, "wood_dark", seg=10)
    leaf_mass((0.5, 1.42, 0.5), (0.36, 0.34, 0.36), random.Random(11), 230, size=0.06)


@SP.prop("flower_tub", 1, 1, 1, V=16)
def flower_tub():
    """Half a cask of flowers: oak staves in two iron hoops, geraniums and daisies spilling over its rim."""
    SP.lathe((0.5, 0, 0.5), [(0, 0.36), (0.2, 0.4), (0.42, 0.39)], "wood", seg=32)
    for k in range(18):
        a = 2 * math.pi * k / 18
        SP.box(0.5 + math.cos(a) * 0.395 - 0.01, 0.02, 0.5 + math.sin(a) * 0.395 - 0.01,
               0.5 + math.cos(a) * 0.395 + 0.01, 0.42, 0.5 + math.sin(a) * 0.395 + 0.01, "wood_dark", bevel=0.0)
    for y in (0.08, 0.34):
        SP.lathe((0.5, y, 0.5), [(0, 0.405), (0.04, 0.41)], "iron_dark", seg=32)
    SP.lathe((0.5, 0.0, 0.5), [(0.38, 0.37), (0.4, 0.37)], "soil", seg=24)
    rnd = random.Random(5)
    leaf_mass((0.5, 0.46, 0.5), (0.36, 0.14, 0.36), rnd, 120, size=0.06)
    for k in range(14):
        a, r = rnd.uniform(0, 2 * math.pi), rnd.uniform(0.05, 0.36)
        mat = ("petal_red", "petal_red", "petal_pink", "petal_white", "petal_yellow")[k % 5]
        bloom((0.5 + math.cos(a) * r, 0.58 + rnd.uniform(0, 0.12), 0.5 + math.sin(a) * r), 0.055, mat, rnd, n=5)


@SP.prop("rose_bush", 1, 1, 1, V=16)
def rose_bush():
    """A rose bush in bloom: a dense dome of dark leaves dotted with red roses."""
    rnd = random.Random(21)
    leaf_mass((0.5, 0.45, 0.5), (0.44, 0.45, 0.44), rnd, 260, mats=("leaf_dark", "leaf_dark", "leaf"), size=0.065)
    for k in range(16):
        u, v = rnd.uniform(-0.2, 1), rnd.uniform(0, 2 * math.pi)
        s = math.sqrt(1 - u * u)
        p = (0.5 + s * math.cos(v) * 0.44, 0.45 + u * 0.45, 0.5 + s * math.sin(v) * 0.44)
        bloom(p, 0.06, "petal_red" if k % 4 else "petal_pink", rnd, n=6)


@SP.prop("hydrangea", 1, 1, 1, V=16)
def hydrangea():
    """A hydrangea: a broad leafy dome crowned with big round heads of blue and violet florets."""
    rnd = random.Random(33)
    leaf_mass((0.5, 0.4, 0.5), (0.46, 0.36, 0.46), rnd, 200, size=0.08)
    heads = [(0.5, 0.0)] + [(2 * math.pi * k / 6 + rnd.uniform(-0.25, 0.25), 0.27) for k in range(6)]
    for k, (a, r) in enumerate(heads):
        c = (0.5 + math.cos(a) * r, 0.4 + math.sqrt(max(0.0, 1 - (r / 0.46) ** 2)) * 0.36 - 0.02, 0.5 + math.sin(a) * r)
        mat = ("petal_blue", "petal_violet", "petal_blue", "petal_pink", "petal_blue", "petal_violet", "petal_blue")[k]
        for j in range(22):
            u, v = rnd.uniform(-0.2, 1), rnd.uniform(0, 2 * math.pi)
            s = math.sqrt(1 - u * u)
            SP.ball((c[0] + s * math.cos(v) * 0.13, c[1] + u * 0.1, c[2] + s * math.sin(v) * 0.13), 0.04, mat, seg=8)
        SP.ball(c, (0.13, 0.1, 0.13), mat, seg=14)


SCHOOL = ["school_desk", "school_chair", "master_desk", "rune_board", "topiary_pot", "flower_tub", "rose_bush", "hydrangea"]


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    for n in (args or SCHOOL):
        SP.build(n)
