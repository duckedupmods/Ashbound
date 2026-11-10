"""The homestead's working stations and its blocky replacements for the smooth props (11/7 rework, user: "the
stations are little blocks, make them so the player knows what they do"; "some assets are minecraft, some 3D").

    blender -b -P tools/blender/homestead_sculpt.py -- [NAME ...]        (none = all)
    python tools/sculpt.py

Each prop faces north (its front at z = 0), stands on y = 0 and fills x 0..w, z 0..d. Voxelized at 16 a block, so
every part that should read is at least ~0.08 thick.

  manor_cookhearth  the Cook's Hearth: an open stone hearth, a fire, a big stew cauldron on a crane, pans, a mantel
  manor_brewery     the Brewer's Kettle: a copper kettle on a brick firebox, the swan-neck pipe into a tapped cask
  manor_alembic     the Alchemist's Bench: a burner under a glowing flask, the still's tube to a receiver, potion shelves
  cellar_barrel     a barrel laid on its cradle, a tap in its head
  wine_rack         a lattice of bottle ends
  field_scarecrow   a straw man on a post, a hat and a patched coat
  farm_handcart     a two-wheeled cart heaped with hay, a pitchfork in it
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sculpt_props as SP  # noqa: E402

HOME = ["manor_cookhearth", "manor_brewery", "manor_alembic", "cellar_barrel", "wine_rack", "field_scarecrow",
        "farm_handcart"]


def pipe(pts, r, mat, seg=12):
    """A tube through the points, a ball at each bend so it reads as one bent pipe."""
    for a, b in zip(pts, pts[1:]):
        SP.cyl(a, b, r, mat, seg=seg)
    for p in pts[1:-1]:
        SP.ball(p, r, mat, seg=seg)


def arc(c, R, a0, a1, n, plane="xy"):
    """Points on a circle arc (degrees) about c in the xy plane."""
    out = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        out.append((c[0] + R * math.cos(a), c[1] + R * math.sin(a), c[2]))
    return out


def lying_cask(cx, cy, z0, z1, r, hoop="iron_dark", tap=True):
    """A cask on its side, its axis along z from z0 (the head at the front) to z1."""
    L = z1 - z0
    zc = (z0 + z1) / 2
    SP.lathe((cx, cy, zc), [(-L / 2, r * 0.86), (-L / 4, r * 0.97), (0, r), (L / 4, r * 0.97), (L / 2, r * 0.86)], "wood",
             seg=28, axis=((cx + 1, cy, zc), 90))
    for t in (-0.42, -0.2, 0.2, 0.42):
        rr = r * (0.9 if abs(t) > 0.3 else 0.985) + 0.012
        SP.torus((cx, cy, zc + t * L), rr, 0.022, hoop, normal=(0, 0, 1), seg=32, tseg=6)
    SP.cyl((cx, cy, z0 - 0.005), (cx, cy, z0 + 0.03), r * 0.8, "wood_end", seg=24)          # the head
    if tap:
        SP.cyl((cx, cy - r * 0.45, z0 + 0.02), (cx, cy - r * 0.45, z0 - 0.1), 0.035, "brass", seg=10)
        SP.cyl((cx, cy - r * 0.45, z0 - 0.1), (cx, cy - r * 0.45 - 0.08, z0 - 0.1), 0.03, "brass", seg=10)
        SP.box(cx - 0.05, cy - r * 0.45 + 0.02, z0 - 0.08, cx + 0.05, cy - r * 0.45 + 0.06, z0 - 0.06, "brass", bevel=0.0)


def tankard(x, y, z, mat="wood", h=0.18, r=0.07):
    SP.bowl((x, y, z), [(0.0, r), (h, r * 1.05)], 0.02, mat, seg=14)
    SP.lathe((x, y + 0.02, z), [(0, r * 0.85), (h - 0.03, r * 0.9)], "foam", seg=14)
    SP.torus((x + r + 0.03, y + h / 2, z), 0.05, 0.015, mat, normal=(0, 0, 1), seg=12, tseg=5, arc=1.0)
    for t in (0.04, h - 0.04):
        SP.torus((x, y + t, z), r + 0.008, 0.01, "iron_dark", seg=16, tseg=4)


# ================================================================ the Cook's Hearth

@SP.prop("manor_cookhearth", 3, 3, 2, V=16)
def manor_cookhearth():
    """An open kitchen hearth big enough to walk into: dressed jambs, a firebrick back, a log fire on its dogs, the
    great iron stew cauldron hung from a swinging crane over it, a ladle in the stew; copper pans on the jambs, the
    mantel set with crocks and a loaf, the hood rising to the chimney."""
    SP.box(0.0, 0.0, 0.05, 3.0, 0.22, 2.0, "stone_pale", bevel=0.02)                   # the hearthstone, proud
    for i in range(6):                                                               # the jambs, quoined
        y0 = 0.22 + i * 0.25
        for x0, x1 in ((0.0, 0.48), (2.52, 3.0)):
            SP.box(x0 + (0.0 if i % 2 else 0.04), y0, 0.18, x1 - (0.04 if i % 2 else 0.0), y0 + 0.25, 2.0,
                   "stone_pale" if i % 2 else "stone", bevel=0.02)
    for i in range(6):                                                               # the firebrick back and cheeks
        y0 = 0.22 + i * 0.25
        SP.box(0.48, y0, 1.62 + (0.02 if i % 2 else 0.0), 2.52, y0 + 0.24, 2.0, "firebrick", bevel=0.015)
    SP.box(0.48, 0.22, 1.5, 2.52, 1.72, 1.62, "coal", bevel=0.01)                     # soot on the back
    SP.box(0.0, 1.72, 0.1, 3.0, 2.02, 2.0, "stone_pale", bevel=0.025)                  # the lintel
    SP.box(1.3, 1.74, 0.08, 1.7, 2.0, 0.12, "stone", bevel=0.01)                       # its keystone
    SP.box(-0.0, 2.02, 0.0, 3.0, 2.12, 0.62, "wood_dark", bevel=0.015)                 # the mantel shelf
    for x in (0.25, 2.75):                                                           # its brackets
        SP.box(x - 0.06, 1.86, 0.02, x + 0.06, 2.02, 0.3, "wood_dark", bevel=0.01)
    SP.frustum_shell(0.2, 0.62, 2.8, 2.0, 2.12, 3.0, (0.75, 0.9, 2.25, 2.0), 0.12, "firebrick")   # the hood
    SP.box(0.15, 2.12, 0.6, 2.85, 2.24, 2.0, "stone", bevel=0.015)                     # the hood's base course
    # the fire: a bed of coals, logs crossed on iron dogs, flames licking the pot
    SP.box(0.85, 0.22, 0.8, 2.15, 0.32, 1.5, "coals_glow", bevel=0.03)
    for x in (0.9, 2.1):
        SP.box(x - 0.04, 0.22, 0.6, x + 0.04, 0.48, 0.7, "iron_dark", bevel=0.01)
        SP.box(x - 0.04, 0.3, 0.6, x + 0.04, 0.36, 1.45, "iron_dark", bevel=0.01)
    SP.cyl((0.8, 0.42, 0.95), (2.2, 0.4, 1.1), 0.09, "wood_dark", seg=12)
    SP.cyl((0.85, 0.38, 1.3), (2.15, 0.44, 1.15), 0.085, "wood", seg=12)
    SP.cyl((1.1, 0.34, 0.75), (1.9, 0.5, 1.4), 0.08, "wood_dark", seg=12)
    for x, z, h in ((1.15, 1.0, 0.36), (1.5, 1.15, 0.46), (1.85, 1.0, 0.34), (1.3, 1.3, 0.3), (1.7, 1.3, 0.32)):
        SP.ellip((x, 0.46 + h / 2, z), (0.1, h / 2, 0.1), "flame", seg=10)
    # the crane: a post on the left cheek, its arm swung out over the fire, the pot on a chain
    SP.cyl((0.6, 0.22, 1.42), (0.6, 1.62, 1.42), 0.045, "iron_dark", seg=10)
    SP.cyl((0.6, 1.52, 1.42), (1.55, 1.52, 1.05), 0.04, "iron_dark", seg=10)
    SP.cyl((0.6, 1.2, 1.42), (1.2, 1.5, 1.2), 0.03, "iron_dark", seg=8)                  # the brace
    SP.chain((1.5, 1.5, 1.07), (1.5, 1.24, 1.07), "iron_dark", link=0.07, r=0.018)
    # the cauldron: big, black, three-legged, brimming
    c = (1.5, 0.56, 1.07)
    SP.bowl(c, [(0.0, 0.18), (0.06, 0.34), (0.2, 0.44), (0.4, 0.45), (0.56, 0.4), (0.62, 0.42)], 0.04, "iron_dark", seg=32)
    SP.torus((c[0], c[1] + 0.62, c[2]), 0.42, 0.03, "iron", seg=32, tseg=6)
    SP.torus((c[0], c[1] + 0.62, c[2]), 0.4, 0.02, "iron_dark", normal=(1, 0, 0), seg=32, tseg=5, arc=0.5)   # the bail
    for a in (90, 210, 330):
        t = math.radians(a)
        SP.cyl((c[0] + 0.3 * math.cos(t), c[1] + 0.04, c[2] + 0.3 * math.sin(t)),
               (c[0] + 0.36 * math.cos(t), c[1] - 0.2, c[2] + 0.36 * math.sin(t)), 0.035, "iron_dark", seg=8)
    SP.lathe((c[0], c[1] + 0.5, c[2]), [(0, 0.38), (0.06, 0.39)], "stew", seg=28)
    for dx, dz, r in ((-0.15, -0.1, 0.06), (0.12, 0.08, 0.05), (0.05, -0.2, 0.045), (-0.05, 0.18, 0.05)):
        SP.ball((c[0] + dx, c[1] + 0.57, c[2] + dz), r, "meat" if r > 0.05 else "herb", seg=10)
    SP.cyl((c[0] + 0.2, c[1] + 0.5, c[2] - 0.05), (c[0] + 0.55, c[1] + 1.05, c[2] - 0.3), 0.025, "wood", seg=8)   # the ladle
    SP.bowl((c[0] + 0.18, c[1] + 0.44, c[2] - 0.04), [(0.0, 0.03), (0.06, 0.08)], 0.015, "wood", seg=12)
    # copper pans hung on the jambs' faces, a ham from the lintel
    for x, r in ((0.24, 0.17), (2.76, 0.15)):
        SP.cyl((x, 1.0, 0.13), (x, 1.0, 0.18), r, "copper", seg=24)
        SP.torus((x, 1.0, 0.12), r, 0.025, "copper_dark", normal=(0, 0, 1), seg=24, tseg=5)
        SP.cyl((x, 1.0 + r, 0.12), (x, 1.0 + r + 0.3, 0.12), 0.03, "copper_dark", seg=8)
        SP.ball((x, 1.0 + r + 0.34, 0.14), 0.03, "iron_dark", seg=8)
    SP.ellip((2.25, 1.38, 1.0), (0.12, 0.2, 0.12), "meat", seg=14)                     # a ham smoking in the hood
    SP.cyl((2.25, 1.58, 1.0), (2.25, 1.72, 1.0), 0.012, "rope", seg=6)
    # the mantel: crocks, a loaf, a pepper mill, a candle
    for x, h in ((0.3, 0.22), (0.55, 0.16)):
        SP.lathe((x, 2.12, 0.32), [(0, 0.08), (h * 0.7, 0.1), (h, 0.07), (h + 0.02, 0.075)], "clay_fired", seg=16)
    SP.ellip((1.5, 2.2, 0.32), (0.22, 0.1, 0.14), "bread", seg=16)
    SP.lathe((2.2, 2.12, 0.3), [(0, 0.05), (0.18, 0.045), (0.22, 0.03)], "wood_dark", seg=12)
    SP.candle(2.6, 2.12, 0.32, h=0.16, r=0.035)
    for x in (0.95, 1.15, 1.85, 2.05):                                                # garlic and herbs from the shelf
        SP.cyl((x, 2.02, 0.5), (x, 1.88, 0.5), 0.01, "rope", seg=6)
        SP.ball((x, 1.84, 0.5), 0.05, "wax" if x < 1.5 else "herb", seg=10)


# ================================================================ the Brewer's Kettle

@SP.prop("manor_brewery", 3, 3, 2, V=16)
def manor_brewery():
    """A copper brew kettle on a brick firebox (its fire door glowing), the swan-neck pipe arching off its dome into
    a great tapped cask on a cradle, a tankard under the tap, hop bines and tankards on a shelf behind."""
    # the firebox
    SP.box(0.1, 0.0, 0.3, 1.7, 0.78, 1.8, "firebrick", bevel=0.02)
    for i in range(3):
        SP.box(0.08, 0.06 + i * 0.25, 0.28, 1.72, 0.08 + i * 0.25, 1.82, "mortar", bevel=0.0)
    SP.box(0.05, 0.74, 0.25, 1.75, 0.84, 1.85, "stone", bevel=0.015)                  # its cap
    SP.box(0.55, 0.12, 0.24, 1.25, 0.56, 0.3, "iron_dark", bevel=0.01)                  # the fire door's frame
    SP.box(0.63, 0.18, 0.22, 1.17, 0.5, 0.27, "coals_glow", bevel=0.01)                  # the fire in it
    for x in (0.7, 0.82, 0.94, 1.06):
        SP.box(x, 0.18, 0.19, x + 0.04, 0.5, 0.22, "iron_dark", bevel=0.0)                # the door's grate
    # the kettle: a copper belly, a dome, a band of brass, a manway with its wheel
    c = (0.9, 0.84, 1.05)
    SP.lathe(c, [(0.0, 0.56), (0.08, 0.66), (0.5, 0.68), (0.62, 0.64), (0.82, 0.5), (0.98, 0.3), (1.08, 0.16), (1.14, 0.1)],
             "copper", seg=36)
    SP.torus((c[0], c[1] + 0.5, c[2]), 0.69, 0.03, "brass", seg=40, tseg=6)
    SP.torus((c[0], c[1] + 0.08, c[2]), 0.67, 0.03, "copper_dark", seg=40, tseg=6)
    for a in range(0, 360, 30):                                                       # its rivet line
        t = math.radians(a)
        SP.ball((c[0] + 0.69 * math.cos(t), c[1] + 0.3, c[2] + 0.69 * math.sin(t)), 0.022, "copper_dark", seg=6)
    SP.cyl((0.9, 1.2, 0.45), (0.9, 1.4, 0.52), 0.13, "brass", seg=16)                  # the manway on the front
    SP.torus((0.9, 1.43, 0.53), 0.1, 0.018, "iron_dark", normal=(0, 0.35, -1), seg=16, tseg=5)
    SP.cyl((0.45, 1.05, 0.55), (0.45, 1.05, 0.38), 0.07, "brass", seg=14)              # a gauge
    SP.cyl((0.45, 1.05, 0.38), (0.45, 1.05, 0.36), 0.055, "paper", seg=14)
    # the swan neck: up off the dome, over and down into the cask's back
    top = (0.9, c[1] + 1.14, 1.05)
    pts = [top, (0.9, 2.3, 1.05)] + arc((1.55, 2.3, 1.05), 0.65, 180, 0, 8)[1:] + [(2.2, 1.7, 1.05), (2.2, 1.62, 1.05)]
    pipe(pts, 0.065, "copper", seg=12)
    SP.ellip((0.9, 2.55, 1.05), (0.14, 0.2, 0.14), "copper", seg=16)                    # the head on the neck
    for k in range(3):                                                                  # steam off the vent
        SP.ellip((0.62 - k * 0.06, 2.1 + k * 0.22, 0.95), (0.08 + k * 0.03, 0.08 + k * 0.02, 0.08 + k * 0.03), "steam", seg=10)
    SP.cyl((0.65, 1.95, 1.0), (0.62, 2.04, 0.97), 0.03, "brass", seg=8)
    # the cask on its cradle, its head to the front with the tap; a tankard under it
    for z in (0.5, 1.6):
        SP.box(1.82, 0.0, z - 0.08, 2.98, 0.42, z + 0.08, "wood_dark", bevel=0.015)
        SP.box(1.82, 0.42, z - 0.08, 1.95, 0.75, z + 0.08, "wood_dark", bevel=0.015)
        SP.box(2.85, 0.42, z - 0.08, 2.98, 0.75, z + 0.08, "wood_dark", bevel=0.015)
    lying_cask(2.4, 1.0, 0.25, 1.9, 0.56)
    SP.cyl((2.2, 1.56, 1.6), (2.2, 1.66, 1.6), 0.09, "brass", seg=12)                   # the pipe's bung
    tankard(2.4, 0.42, 0.12)
    # the shelf behind: tankards and a hop bine hung along it
    SP.box(0.0, 2.6, 1.7, 1.5, 2.66, 2.0, "wood_dark", bevel=0.01)
    for x in (0.18, 1.32):
        SP.box(x - 0.04, 2.38, 1.92, x + 0.04, 2.6, 2.0, "wood_dark", bevel=0.006)
    for x in (0.25, 0.5):
        tankard(x, 2.66, 1.84, mat="wood_dark", h=0.16, r=0.06)
    for i in range(7):
        x = 1.6 + i * 0.2
        SP.ball((x, 2.75 - 0.05 * math.sin(i * 1.3), 1.92), 0.06, "hops", seg=10)
        SP.ball((x + 0.1, 2.7, 1.9), 0.045, "leaf", seg=8)
    SP.cyl((1.55, 2.78, 1.94), (2.95, 2.78, 1.94), 0.012, "rope", seg=6)
    # a mash paddle leant on the firebox's side
    SP.cyl((0.05, 0.0, 0.2), (0.0, 1.3, 0.45), 0.03, "wood", seg=8)
    SP.box(-0.0, 0.0, 0.1, 0.12, 0.3, 0.3, "wood", bevel=0.01)


# ================================================================ the Alchemist's Bench

@SP.prop("manor_alembic", 3, 3, 2, V=16)
def manor_alembic():
    """A heavy oak bench: a brass burner's blue flame under a great round flask of green, its glass head and tube
    running down to a receiving flask of violet; a grimoire open, a mortar, a skull, crystals; behind, shelves of
    glowing bottles up to a crown of candles."""
    # the bench
    for x in (0.12, 2.88):
        for z in (0.3, 1.6):
            SP.lathe((x, 0.0, z), [(0, 0.09), (0.1, 0.1), (0.2, 0.07), (0.45, 0.09), (0.6, 0.07), (0.82, 0.08)], "wood_dark", seg=14)
    SP.box(0.0, 0.82, 0.12, 3.0, 0.95, 1.95, "wood_dark", bevel=0.02)                  # the top
    SP.box(0.08, 0.7, 0.2, 2.92, 0.82, 1.85, "wood", bevel=0.01)                       # its apron
    SP.box(0.08, 0.18, 0.25, 2.92, 0.24, 1.8, "wood", bevel=0.008)                      # the shelf under
    for i, m in enumerate(("leather_violet", "leather_red", "leather_blue", "leather_green", "leather")):
        SP.book(0.25 + i * 0.13, 0.24, 0.5, 0.11, 0.34 - (i % 2) * 0.05, 0.4, m)
    SP.box(1.6, 0.24, 0.45, 2.4, 0.5, 1.2, "wood", bevel=0.01)                          # a crate of bottles under it
    for i in range(4):
        SP.cyl((1.72 + i * 0.18, 0.5, 0.65), (1.72 + i * 0.18, 0.66, 0.65), 0.05, "glass", seg=10)
    # the still: tripod and burner, the round flask, its head, the tube, the receiver
    b = (0.95, 0.95, 0.8)
    SP.cyl(b, (b[0], b[1] + 0.14, b[2]), 0.11, "brass", seg=16)
    SP.ellip((b[0], b[1] + 0.26, b[2]), (0.08, 0.14, 0.08), "flame_blue", seg=10)
    for a in (90, 210, 330):
        t = math.radians(a)
        SP.cyl((b[0] + 0.3 * math.cos(t), b[1], b[2] + 0.3 * math.sin(t)), (b[0] + 0.2 * math.cos(t), b[1] + 0.42, b[2] + 0.2 * math.sin(t)),
               0.025, "iron_dark", seg=8)
    SP.torus((b[0], b[1] + 0.42, b[2]), 0.2, 0.022, "iron_dark", seg=24, tseg=5)
    f = (b[0], b[1] + 0.68, b[2])
    SP.ball(f, 0.28, "glass", seg=28)                                                    # the round flask
    SP.ellip((f[0], f[1] - 0.06, f[2]), (0.24, 0.2, 0.24), "potion_green", seg=24)
    SP.cyl((f[0], f[1] + 0.24, f[2]), (f[0], f[1] + 0.56, f[2]), 0.07, "glass", seg=14)
    SP.lathe((f[0], f[1] + 0.56, f[2]), [(0, 0.08), (0.08, 0.17), (0.2, 0.16), (0.3, 0.06), (0.36, 0.04)], "copper", seg=20)  # the head
    pipe([(f[0] + 0.15, f[1] + 0.72, f[2]), (1.55, 1.75, 0.75), (2.0, 1.45, 0.7), (2.05, 1.32, 0.7)], 0.035, "glass", seg=10)
    SP.flask(2.05, 0.95, 0.7, 0.16, 0.42, "potion_violet")                               # the receiver
    for k in range(3):
        SP.ball((2.05, 1.18 + k * 0.05, 0.7), 0.025, "potion_violet", seg=8)
    # on the bench: the grimoire open, a mortar and pestle, a skull, a crystal cluster, a candle
    SP.box(0.15, 0.95, 0.25, 0.75, 0.99, 0.62, "leather_violet", bevel=0.008, rot=(0, 8, 0))
    SP.box(0.18, 0.99, 0.27, 0.44, 1.02, 0.6, "paper", bevel=0.004, rot=(0, 8, 0))
    SP.box(0.46, 0.99, 0.27, 0.72, 1.02, 0.6, "paper", bevel=0.004, rot=(0, 8, 0))
    SP.bowl((2.6, 0.95, 0.5), [(0.0, 0.08), (0.06, 0.12), (0.14, 0.13)], 0.03, "stone_pale", seg=16)
    SP.cyl((2.6, 1.0, 0.5), (2.72, 1.25, 0.42), 0.03, "stone_pale", seg=8)
    SP.ball((1.55, 1.08, 1.3), 0.13, "bone", seg=16)                                    # the skull
    SP.box(1.48, 0.95, 1.18, 1.62, 1.04, 1.32, "bone", bevel=0.02)
    for dx in (-0.05, 0.05):
        SP.ball((1.55 + dx, 1.1, 1.18), 0.035, "ink", seg=8)
    for i, (dx, dz, h) in enumerate(((0, 0, 0.36), (0.1, 0.06, 0.24), (-0.09, 0.05, 0.22), (0.04, -0.08, 0.18))):
        SP.crystal((2.55 + dx, 0.95, 1.3 + dz), h, 0.06, "crystal_cyan", tilt=(dx * 120, 0, dz * 120))
    SP.candle(0.3, 0.95, 1.4, h=0.2, r=0.035)
    # the shelves behind: two boards of bottles in all the colours, sides, a top with candles
    for x in (0.02, 2.9):
        SP.box(x, 0.95, 1.55, x + 0.08, 2.75, 1.98, "wood_dark", bevel=0.01)
    SP.box(0.02, 0.95, 1.9, 2.98, 2.75, 1.98, "wood", bevel=0.005)
    for y in (1.6, 2.2, 2.75):
        SP.box(0.02, y - 0.05, 1.5, 2.98, y + 0.01, 1.98, "wood_dark", bevel=0.01)
    pots = ("potion_red", "potion_blue", "potion_green", "potion_violet")
    for row, y in enumerate((1.6, 2.2)):
        for i in range(9):
            x = 0.22 + i * 0.31
            r = 0.07 + 0.02 * ((i + row) % 3 == 0)
            SP.flask(x, y + 0.01, 1.72, r, 0.24 + 0.06 * ((i + row) % 2), pots[(i * 3 + row) % 4])
    for x in (0.4, 1.5, 2.6):
        SP.candle(x, 2.76, 1.75, h=0.18, r=0.035)


# ================================================================ the plain props, blocky to match

@SP.prop("cellar_barrel", 1, 1, 1, V=16)
def cellar_barrel():
    """A barrel laid on its cradle, head to the front, a brass tap in it."""
    for z in (0.18, 0.82):
        SP.box(0.06, 0.0, z - 0.07, 0.94, 0.16, z + 0.07, "wood_dark", bevel=0.012)
        SP.box(0.06, 0.16, z - 0.07, 0.2, 0.32, z + 0.07, "wood_dark", bevel=0.012)
        SP.box(0.8, 0.16, z - 0.07, 0.94, 0.32, z + 0.07, "wood_dark", bevel=0.012)
    lying_cask(0.5, 0.52, 0.06, 1.0, 0.4)


@SP.prop("wine_rack", 1, 1, 1, V=16)
def wine_rack():
    """A square of pigeonholes, a bottle's end in each: green, dark, one red-sealed."""
    SP.box(0.02, 0.0, 0.1, 0.98, 1.0, 1.0, "wood_dark", bevel=0.015)
    for i in range(3):
        for j in range(3):
            x, y = 0.2 + i * 0.3, 0.2 + j * 0.3
            SP.box(x - 0.13, y - 0.13, 0.05, x + 0.13, y + 0.13, 0.12, "wood", bevel=0.01)
            SP.cyl((x, y, 0.02), (x, y, 0.4), 0.1, "bottle_green" if (i + j) % 3 else "wood_dark", seg=14)
            SP.cyl((x, y, -0.02), (x, y, 0.03), 0.045, "cloth_red" if (i, j) == (1, 1) else "wax", seg=10)


@SP.prop("field_scarecrow", 1, 2, 1, V=16)
def field_scarecrow():
    """A straw man on a post and cross-bar: a sack head with stitched eyes, a floppy hat, a patched red coat, straw
    sticking out of the cuffs."""
    SP.box(0.45, 0.0, 0.45, 0.55, 1.75, 0.55, "wood_dark", bevel=0.01)
    SP.box(0.0, 1.22, 0.45, 1.0, 1.3, 0.55, "wood_dark", bevel=0.01)
    SP.box(0.24, 0.62, 0.32, 0.76, 1.32, 0.68, "cloth_red", bevel=0.05)                 # the coat
    SP.box(0.3, 0.8, 0.3, 0.45, 0.95, 0.33, "leather_blue", bevel=0.01)                  # a patch
    SP.box(0.24, 0.62, 0.31, 0.76, 0.68, 0.69, "rope", bevel=0.01)                       # its belt
    for s in (-1, 1):
        SP.box(0.5 + s * 0.22 - 0.12, 1.12, 0.38, 0.5 + s * 0.48, 1.34, 0.62, "cloth_red", bevel=0.04)   # sleeves
        SP.ellip((0.5 + s * 0.5, 1.23, 0.5), (0.08, 0.1, 0.1), "straw", seg=10)          # straw at the cuffs
    for x in (0.34, 0.66):
        SP.box(x - 0.08, 0.3, 0.4, x + 0.08, 0.64, 0.6, "leather", bevel=0.03)            # trouser legs
        SP.ellip((x, 0.3, 0.5), (0.08, 0.08, 0.08), "straw", seg=10)
    SP.ball((0.5, 1.5, 0.5), 0.2, "paper", seg=20)                                        # the sack head
    for x in (0.42, 0.58):
        SP.box(x - 0.035, 1.52, 0.29, x + 0.035, 1.58, 0.31, "ink", bevel=0.0)
    SP.box(0.4, 1.42, 0.29, 0.6, 1.44, 0.31, "ink", bevel=0.0)
    SP.cyl((0.5, 1.62, 0.5), (0.5, 1.66, 0.5), 0.34, "straw", seg=24)                     # the hat's brim
    SP.lathe((0.5, 1.64, 0.5), [(0, 0.17), (0.18, 0.14), (0.24, 0.08)], "straw", seg=18)
    SP.torus((0.5, 1.7, 0.5), 0.165, 0.025, "cloth_red", seg=20, tseg=5)


@SP.prop("farm_handcart", 1, 1, 2, V=16)
def farm_handcart():
    """A two-wheeled barrow cart, its bed heaped with hay, a pitchfork stuck in, the shafts resting on the ground."""
    for s in (0.04, 0.96):                                                              # the wheels
        SP.cyl((s - 0.04, 0.34, 1.2), (s + 0.04, 0.34, 1.2), 0.34, "wood", seg=24)
        SP.torus((s, 0.34, 1.2), 0.33, 0.03, "iron_dark", normal=(1, 0, 0), seg=28, tseg=5)
        SP.cyl((s - 0.06, 0.34, 1.2), (s + 0.06, 0.34, 1.2), 0.07, "wood_dark", seg=12)
    SP.cyl((0.0, 0.34, 1.2), (1.0, 0.34, 1.2), 0.03, "iron_dark", seg=8)
    SP.box(0.12, 0.42, 0.55, 0.88, 0.5, 1.8, "wood_dark", bevel=0.01)                   # the bed
    for x0, x1, z0, z1 in ((0.12, 0.2, 0.55, 1.8), (0.8, 0.88, 0.55, 1.8), (0.12, 0.88, 1.72, 1.8), (0.12, 0.88, 0.55, 0.63)):
        SP.box(x0, 0.5, z0, x1, 0.82, z1, "wood", bevel=0.01)
    SP.ellip((0.5, 0.82, 1.18), (0.36, 0.18, 0.6), "straw", seg=20)                     # the hay
    for x in (0.22, 0.78):                                                               # the shafts down to the ground
        SP.cyl((x, 0.5, 0.6), (x, 0.06, 0.02), 0.04, "wood_dark", seg=8)
    SP.cyl((0.6, 0.85, 1.3), (0.7, 1.75, 1.6), 0.025, "wood", seg=8)                    # the pitchfork
    for dx in (-0.05, 0.0, 0.05):
        SP.cyl((0.6 + dx, 0.85, 1.3), (0.58 + dx, 0.62, 1.22), 0.012, "iron", seg=6)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    for n in (args or HOME):
        SP.build(n)
