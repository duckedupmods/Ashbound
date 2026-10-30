"""The Tide Chapel's monsters, each built by hand (tools/vox2.py). The sea took the chapel on the point and kept the
congregation: green-black drowned stone, bronze gone to verdigris, barnacles, kelp, wet vestments, and the cold
blue-green light of things that live in the deep.

    tide_crab        swarm   a hermit crab that took a reliquary for a shell, one crushing claw, candles still on it
    crab_knight      brute   a drowned knight the crabs grew into: carapace plate, one arm a great claw, eye stalks
    tide_priest      caster  the drowned priest: an angler's lure over his hood, gills, needle teeth, a conch staff
    net_thrower      skirm   the fisherman ghoul: sou'wester, a net of hooks and floats on his back, a harpoon
    barnacle_choir   elite   the choir that would not stop singing: three heads on one body, the hymn board, barnacles
    drowned_bell     boss    the chapel's great bell walking: worn as a hood, kelp from its mouth, clapper and anchor

    python tools/monsterforge.py tide_chapel --preview ; python tools/mobsheet.py tide_chapel
"""
import math

import vox2 as X
from vox2 import C, ramp

STONE = ramp("#0a100e", "#111a17", "#182420", "#20302a", "#2a3c35", "#364a42", "#445a50")
BRONZE = ramp("#1a120a", "#2e2010", "#4a3418", "#6a4c22", "#8c6830", "#b08a44", "#d4b066")
VERD = ramp("#123a32", "#1c5446", "#2a705c", "#3e8c74", "#5aa88e")
BARN = ramp("#3a3a34", "#585850", "#7a786c", "#9c9888", "#bcb6a2", "#dad4bc")
KELP = ramp("#0a140a", "#122010", "#1a2e16", "#24401c", "#305224")
SEA = ramp("#0a5a5a", "#128a84", "#2abcae", "#6ae8d4", "#c4fff2")
CORAL = ramp("#3a0e10", "#5e1618", "#8a2422", "#b43a30", "#d8604a")
SHELL = ramp("#1a0c0a", "#2e1610", "#4a2216", "#6a321e", "#8c4628", "#ae5e36")
VEST = ramp("#0c1014", "#141a20", "#1c242c", "#263038", "#323e48")
GOLD = ramp("#3a2a0a", "#5e4612", "#8a6a1e", "#b48e30", "#dab450")
SKIN = ramp("#16201e", "#20302c", "#2c403a", "#3a524a", "#4a665c")      # drowned, blue-green
IRON = ramp("#0e1010", "#181a1a", "#242828", "#323636", "#424848")
RUST = ramp("#2a1408", "#44200c", "#5e2e12", "#7a3e18")
ROPE = ramp("#1e180e", "#2e2416", "#40321e", "#544428", "#6a5634")
WAX = ramp("#5a5444", "#7a7460", "#9c967e", "#c0b89c", "#e2dcc0")
OIL = ramp("#1a1a0a", "#2a2a10", "#3e3c16", "#56521e", "#6e6a28")
FLAME = ramp("#8a3a0a", "#d06a14", "#f4a030", "#ffd27a", "#fff4d0")


def shaders():
    return {
        "stone": X.surf(STONE, 0.5, 1.2, 0.3, 0.12, crust=(BARN, 0.16), drip=(KELP, 0.14)),
        "bronze": X.surf(BRONZE, 0.52, 1.3, 0.16, 0.2, rust=(VERD, 0.42, 0.3), crust=(BARN, 0.08)),
        "verd": X.surf(VERD, 0.5, 1.0, 0.24, 0.1),
        "barnacle": X.surf(BARN, 0.5, 1.2, 0.5, 0.16),
        "kelp": X.surf(KELP, 0.5, 1.0, 0.24, 0.0, stripe=2, holes=True),
        "glow": X.glow(SEA),
        "eye": X.glow(SEA, 0.78, 0.2),
        "coral": X.surf(CORAL, 0.5, 1.2, 0.3, 0.14),
        "shell": X.surf(SHELL, 0.5, 1.5, 0.4, 0.0, crust=(BARN, 0.2), rust=(CORAL, 0.18, 0.5)),
        "oil": X.surf(OIL, 0.5, 1.4, 0.2, 0.18, drip=(KELP, 0.22)),
        "vest": X.surf(VEST, 0.48, 1.0, 0.2, 0.0, holes=True, drip=(KELP, 0.2)),
        "gold": X.surf(GOLD, 0.55, 1.3, 0.14, 0.2, rust=(VERD, 0.2, 0.4)),
        "skin": X.wrinkled(SKIN, 0.7),
        "iron": X.surf(IRON, 0.5, 1.3, 0.16, 0.18, rust=(RUST, 0.4, 0.4)),
        "rope": X.surf(ROPE, 0.5, 1.0, 0.2, 0.0, stripe=2),
        "wax": X.surf(WAX, 0.6, 0.8, 0.1, 0.1),
        "flame": X.glow(FLAME, 0.7, 0.3),
        "bone": X.surf(BARN, 0.62, 1.0, 0.14, 0.12),
        "dark": X.dark(STONE),
    }


def barnacles(k, part, pts, s=1.2):
    """little volcano cones of barnacle: a ring of shell with a dark mouth"""
    for (x, y, z, nx, nz) in pts:
        k.box(part, C(x, y, z, s * 1.6, s * 1.0, s * 1.6), "barnacle", tag="barnacle")
        k.box(part, C(x, y + s * 0.9, z, s * 0.9, s * 0.4, s * 0.9), "dark", tag="barnacle")


# ================================================================ the Drowned Bell (boss)

def drowned_bell():
    """When the sea came over the point the great bell fell from its tower onto the bell-ringer, and he would not let
    it go. Now it walks: the bell worn as a hood down to the chest, crusted in barnacles and green with the sea, a
    crack down its face where two eyes burn through. Kelp and drowned rope hang from its mouth like a beard. Its
    arms are long and grey and swollen with water; one swings the bell's own clapper on a length of chain, the
    other drags the chapel's anchor. A tide pool has settled on the bell's crown, with a crab in it."""
    k = X.Kit("drowned_bell")
    hips = k.part("hips", (0, 38, 0))
    k.stack(hips, 0, 0, [(28, 20, 13), (34, 24, 15), (40, 22, 14)], "skin", "pelvis")
    for i, (x, L) in enumerate(((-9, 22), (-4, 30), (1, 26), (6, 32), (10, 20))):       # the ringer's robe, in tatters
        k.box(hips, C(x, 38 - L, 7.4, 4.6, L, 0.8), "vest", tag="robe")
        k.box(hips, C(x, 38 - L * 0.9, -7.4, 4.6, L * 0.9, 0.8), "vest", tag="robe")
    k.box(hips, C(0, 36, 0, 25, 2.4, 16), "rope", tag="belt")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 7
        th = k.part("thigh_" + nm, (x, 34, 0), (("x", -8), ("z", side * 6)), "hips")
        sh = k.part("shin_" + nm, (x, 18, 0), (("x", 14),), th)
        ft = k.part("foot_" + nm, (x, 4, 0), (("x", -6),), sh)
        k.stack(th, x, 0, [(19, 13, 13), (27, 15, 15), (34, 14, 14)], "skin", "thigh")
        k.stack(sh, x, 0, [(4, 12, 12), (12, 12, 12), (19, 13, 13)], "skin", "shin")
        k.ring(sh, x, 9, 0, 5.4, 1.4, "rope", "lashing", n=10, axis="y")
        barnacles(k, sh, [(x + side * 4.6, 12, 1, 0, 0), (x + side * 4.4, 8, -2, 0, 0), (x, 14, 4.8, 0, 1)])
        k.box(ft, C(x, 0, 2, 14, 4, 17), "skin", tag="foot")
        for t in (-3.5, 0, 3.5):
            k.box(ft, C(x + t, 0, 9.4, 2.8, 2.6, 3.0), "bone", tag="foot")
    # ---------------------------------------------------------------- torso: hunched, swollen, under the bell
    to = k.part("torso", (0, 39, 0), (("x", 14),), "hips")
    k.stack(to, 0, 0, [(39, 24, 15), (48, 30, 18), (55, 34, 20)], "skin", "chest")
    k.box(to, C(0, 42, 9.2, 14, 8, 1.2), "skin", tag="belly")
    # the bell: a stack of rings, widest at the mouth (chest), the crown at the top
    BELL = [(50, 44, 40), (52, 42, 38), (56, 37, 33), (61, 33, 30), (67, 31, 28), (73, 30, 27), (78, 27, 25), (81, 20, 18)]
    k.stack(to, 0, 0, BELL, "bronze", "bell", step=1.0)
    k.box(to, C(0, 50, 0, 45, 2.0, 41), "bronze", tag="bell_lip")
    k.box(to, C(0, 58, 0, 37.6, 1.4, 33.6), "gold", tag="bell_band")
    k.box(to, C(0, 72, 0, 31, 1.4, 27.6), "gold", tag="bell_band")
    for a in range(0, 360, 45):          # raised saints round the bell's waist, worn down to stubs
        r = math.radians(a)
        k.box(to, C(math.sin(r) * 17.4, 61.6, math.cos(r) * 15.6, 3.0, 8.0, 1.4), "bronze", tag="saint")
    # the crack down its face, and the eyes burning through
    for (y, x) in ((78, 1.0), (75, 0.0), (72, -1.4), (69, -0.6), (66, 0.8), (63, 0.2), (60, -1.0), (57, 0.0)):
        k.box(to, C(x, y, 14.2, 2.0, 3.2, 1.0), "dark", tag="crack")
    hd = k.part("head", (0, 60, 4), (), "torso")      # the ringer's head is inside the bell: only the eyes show
    for sx in (-3.2, 3.2):
        k.box(hd, C(sx, 66.0, 15.0, 4.0, 2.0, 0.8), "dark", tag="eye_hole")
        k.box(hd, C(sx, 66.2, 15.2, 3.0, 1.4, 0.6), "eye", group="glow", tag="eye")
    barnacles(k, to, [(12, 54, 17.4, 0, 1), (-14, 56, 15.2, 0, 1), (16, 66, 9, 1, 0), (-15, 70, 8, 0, 0),
                      (-6, 76, 11, 0, 1), (8, 79, 6, 0, 0), (17, 53, -8, 1, 0), (-18, 60, -6, 0, 0)], s=1.8)
    k.cluster(to, (-12, 76, 6), 4, 6, 2.2, mat="coral", seed=3, up=(-0.4, 1, 0.3))
    # what hangs from the bell's mouth: kelp, drowned rope, a bead of light at the end of each
    for i, (x, z, L) in enumerate(((-16, 14, 18), (-9, 18, 24), (-2, 19, 28), (5, 18.6, 22), (12, 16, 26), (18, 10, 16),
                                   (-19, 2, 20), (19, -4, 22), (-15, -14, 18), (14, -16, 20))):
        k.limb(to, (x, 50, z), (x * 1.04, 50 - L, z * 1.05), 2.2, "kelp" if i % 3 else "rope", "kelp", d=0.8)
        if i % 2 == 0:
            k.box(to, C(x * 1.04, 49 - L, z * 1.05, 1.6, 1.6, 1.6), "glow", group="glow", tag="bead")
    # the crown: its hanging loop, a broken beam of the tower still through it, a tide pool with a crab
    k.ring(to, 0, 85.0, 0, 4.4, 2.0, "bronze", "crown", n=10, axis="z")
    k.limb(to, (-18, 86, 2), (20, 82, -2), 3.6, "rope", "beam", d=3.2)
    k.box(to, C(6, 81.0, 4, 8, 1.0, 6), "glow", group="glow", tag="pool")
    k.box(to, C(6, 81.6, 4, 3.6, 1.6, 3.0), "shell", tag="crab")
    for sx in (-1, 1):
        k.limb(to, (6 + sx * 1.6, 82, 5), (6 + sx * 3.4, 83.2, 6.8), 0.9, "shell", "crab")
    # ---------------------------------------------------------------- arms: long, grey, swollen; the clapper and the anchor
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 19
        up = k.part("arm_" + nm, (x, 50, 0), (("x", -18 if side > 0 else -40), ("z", side * 18)), "torso")
        fo = k.part("fore_" + nm, (x, 32, 0), (("x", -20 if side > 0 else -60),), up)
        hn = k.part("hand_" + nm, (x, 14, 0), (), fo)
        k.stack(up, x, 0, [(32, 12, 12), (42, 14, 14), (50, 15, 15)], "skin", "upper_arm")
        k.stack(fo, x, 0, [(14, 13, 13), (24, 14, 14), (32, 12, 12)], "skin", "forearm")
        k.ring(fo, x, 20, 0, 7.6, 1.8, "iron", "manacle", n=12, axis="y")
        k.chain(fo, (x, 19, 5), (x + side * 2, 8, 7), 4, w=1.4)
        barnacles(k, up, [(x + side * 5, 44, 0, 1, 0), (x, 38, 5.4, 0, 1)])
        k.box(hn, C(x, 7, 0.5, 13, 8, 12), "skin", tag="hand")
        for t in (-3, -1, 1, 3):
            k.box(hn, C(x + t * 1.3, 1, 4.6, 2.6, 7, 2.6), "skin", tag="finger")
            k.shard(hn, (x + t * 1.3, 1.2, 5.6), (0, -1, 0.3), 3.0, 1.6, mat="bone", tag="nail")
    # the clapper on its chain, in the right hand: an iron pear as big as a man
    cl = k.part("clapper", (-19, 10, 2), (("x", 60),), k.parts["hand_r"])
    k.chain(cl, (-19, 10, 2), (-19, -10, 2), 6, w=2.2)
    k.blob(cl, (-19, -20, 2), (8.0, 11.0, 8.0), "iron", "clapper", step=1.2)
    k.box(cl, C(-19, -31, 2, 7.0, 3.0, 7.0), "iron", tag="clapper")
    k.ring(cl, -19, -14, 2, 8.2, 1.6, "bronze", "clapper_band", n=12, axis="y")
    # the anchor, in the left: shank, stock, flukes
    an = k.part("anchor", (19, 8, 1), (("x", 20),), k.parts["hand_l"])
    k.limb(an, (19, 12, 1), (19, -26, 1), 3.2, "iron", "shank", d=2.6)
    k.limb(an, (11, 6, 1), (27, 6, 1), 2.4, "iron", "stock")
    k.ring(an, 19, 15, 1, 2.6, 1.4, "iron", "anchor_ring", n=8)
    for sx in (-1, 1):
        k.limb(an, (19, -26, 1), (19 + sx * 10, -20, 1), 3.0, "iron", "fluke_arm", d=2.4)
        k.shard(an, (19 + sx * 10, -20, 1), (sx * 0.5, 1, 0), 7, 4.2, mat="iron", tag="fluke")
    barnacles(k, an, [(20.4, -12, 2.4, 0, 1), (18, -4, 2.4, 0, 1), (11, -21, 2, 0, 0)])
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Barnacle Choir (elite, the key)

def barnacle_choir():
    """The choir was singing when the water came in, and they sang on, and the sea grew them together: one great
    body in a sodden choir robe, three heads on it, all three mouths wide in the same note. Barnacles have taken the
    left side of it. It carries the hymn board torn from the chapel wall, the numbers still on it, and swings it
    like a door; candles still burn on the shoulders where the altar boys left them."""
    k = X.Kit("barnacle_choir")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(15, 13, 9), (20, 12, 8.4)], "vest", "robe")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 3.4
        th = k.part("thigh_" + nm, (x, 19, 0), (("x", -4), ("z", side * 4)), "hips")
        sh = k.part("shin_" + nm, (x, 10.4, 0), (("x", 6),), th)
        ft = k.part("foot_" + nm, (x, 2.0, 0), (), sh)
        k.box(th, C(x, 9.6, 0, 6.4, 9.6, 7.6), "vest", tag="robe")
        k.box(sh, C(x, 1.6, 0, 6.8, 9.0, 8.0), "vest", tag="robe")
        k.box(sh, C(x, 1.0, 0, 7.4, 2.4, 8.6), "vest", tag="hem")
        k.box(ft, C(x, 0, 1.2, 4.0, 2.0, 6.0), "skin", tag="foot")
    # ---------------------------------------------------------------- torso: a wide body, the white surplice, barnacles up the left
    to = k.part("torso", (0, 20, 0), (("x", 6),), "hips")
    k.stack(to, 0, 0, [(20, 13, 8.4), (27, 18, 10), (33, 22, 11), (37, 22, 10)], "vest", "robe")
    k.stack(to, 0, 0.4, [(27, 18.6, 10.6), (32, 22.6, 11.6), (36, 22.6, 10.6)], "wax", "surplice")
    k.box(to, C(0, 23.4, 0, 18.8, 1.4, 10.8), "gold", tag="sash")
    barnacles(k, to, [(8, 26, 4.8, 1, 0), (9.4, 30, 2, 1, 0), (6, 32, 5.4, 0, 1), (10, 34, -2, 1, 0), (8.6, 22, -3, 1, 0),
                      (5, 29, 5.6, 0, 1), (-2, 33, -5.2, 0, 0)], s=1.3)
    k.cluster(to, (9, 35, 0), 3, 4, 1.4, mat="coral", seed=7, up=(0.5, 1, 0))
    # three heads, all singing: the middle one tallest, the two outer ones grown out of the shoulders
    for i, (hx, hy, tilt, sz) in enumerate(((0, 37.6, 0, 1.25), (-8.4, 35.4, -22, 1.1), (8.4, 35.4, 22, 1.1))):
        hd = k.part("head" if i == 0 else "head%d" % i, (hx, hy, 0.6), (("z", tilt),), "torso", bone=(i == 0))
        w, h = 5.6 * sz, 6.8 * sz
        k.box(hd, C(hx, hy, 0.6, w, h, w), "skin", tag="face")
        k.box(hd, C(hx, hy + h - 0.6, 0.4, w + 0.8, 1.8, w + 0.6), "kelp", tag="hair")
        k.box(hd, C(hx, hy + 0.6, 0.6 + w / 2, 2.4 * sz, 3.4 * sz, 0.4), "dark", tag="mouth")    # the open O of the note
        k.box(hd, C(hx, hy + 1.2, 0.6 + w / 2 + 0.05, 1.4 * sz, 2.0 * sz, 0.4), "glow", group="glow", tag="note")
        for sx in (-1.3, 1.3):
            k.box(hd, C(hx + sx * sz, hy + h * 0.66, 0.6 + w / 2, 1.2, 0.8, 0.3), "eye", group="glow", tag="eye" if i == 0 else "eye_side")
        k.box(hd, C(hx, hy - 1.4, 0.4, w + 1.4, 1.6, w + 1.4), "wax", tag="ruff")
    # candles on the shoulders
    for sx in (-10.4, 10.4):
        for dz, hh in ((-1.6, 3.0), (1.2, 4.2)):
            k.box(to, C(sx, 37, dz, 1.2, hh, 1.2), "wax", tag="candle")
            k.box(to, C(sx, 37 + hh, dz, 0.7, 1.2, 0.7), "flame", group="glow", tag="flame")
    # ---------------------------------------------------------------- arms: heavy sleeves
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 12
        up = k.part("arm_" + nm, (x, 34, 0), (("x", -30 if side > 0 else -70), ("z", side * 10)), "torso")
        fo = k.part("fore_" + nm, (x, 25, 0), (("x", -40 if side > 0 else -30),), up)
        hn = k.part("hand_" + nm, (x, 16, 0), (), fo)
        k.box(up, C(x, 25.6, 0, 5.6, 9.4, 5.8), "vest", tag="sleeve")
        k.stack(fo, x, 0, [(16, 8.0, 8.0), (20, 6.6, 6.6), (25, 5.6, 5.6)], "wax", "sleeve")
        k.box(hn, C(x, 12.4, 0.4, 4.0, 4.0, 4.0), "skin", tag="hand")
        if side > 0:
            barnacles(k, fo, [(x + 3.2, 20, 0, 1, 0), (x + 2.4, 23, 2, 1, 0)])
    # the hymn board: a tall dark plank, gilt frame, the hymn numbers in white, nails through it
    hb = k.part("board", (-12, 13.6, 1.0), (("x", 60),), k.parts["hand_r"])
    k.box(hb, C(-12, 2, 1, 2.0, 32, 13), "stone", tag="board")
    k.box(hb, C(-12, 2, 1, 2.6, 1.4, 14.2), "gold", tag="frame")
    k.box(hb, C(-12, 32.6, 1, 2.6, 1.4, 14.2), "gold", tag="frame")
    for z in (-6.8, 6.8):
        k.box(hb, C(-12, 2, 1 + z, 2.6, 32, 1.2), "gold", tag="frame")
    for r in range(4):                      # four hymns, three numbers each
        for c in range(3):
            k.box(hb, C(-13.1, 26 - r * 6.2, 1 - 3.6 + c * 3.6, 0.3, 3.6, 2.4), "wax", tag="numeral")
    for (y, z) in ((5, -4), (11, 5), (19, -5), (29, 3)):
        k.limb(hb, (-12, y, 1 + z), (-17, y + 1, 1 + z), 0.7, "iron", "nail")
    barnacles(k, hb, [(-11, 8, 6, 0, 0), (-11, 4, 4, 0, 0), (-11, 30, -5, 0, 0)])
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Tide Priest (caster)

def tide_priest():
    """The priest who stayed to bless the water as it came in. The deep took him in and gave him back changed: his
    face drawn out into a fish's, wide and lipless, full of needle teeth, gills open down his neck, and from the
    peak of his hood a stalk of flesh hangs a lure of cold light, like the fish that hunt in the dark. His
    vestments are kelp-heavy and dripping; he carries a staff topped with a great conch, and blows it to call the
    tide."""
    k = X.Kit("tide_priest")
    hips = k.part("hips", (0, 19, 0))
    k.stack(hips, 0, 0, [(13, 9.6, 7.0), (19, 9.0, 6.4)], "vest", "robe")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.4
        th = k.part("thigh_" + nm, (x, 19, 0), (("x", -4),), "hips")
        sh = k.part("shin_" + nm, (x, 10, 0), (("x", 6),), th)
        ft = k.part("foot_" + nm, (x, 2, 0), (), sh)
        k.box(th, C(x, 9.6, 0, 4.6, 9.4, 6.2), "vest", tag="robe")
        k.box(sh, C(x, 1.2, 0, 5.0, 9.2, 6.6), "vest", tag="robe")
        k.box(ft, C(x, 0, 1.4, 3.2, 1.6, 5.4), "skin", tag="foot")
        k.shard(ft, (x, 0.4, 3.8), (0, 0, 1), 2.0, 2.4, mat="skin", tag="foot")   # webbed toes
    # the stole and the kelp hanging off him to the floor
    for sx in (-2.0, 2.0):
        k.box(hips, C(sx, 4, 3.4, 1.8, 15, 0.5), "gold", tag="stole")
    for (x, z, L) in ((-4.6, 2.6, 16), (4.4, -2.0, 18), (-3.0, -3.4, 14), (3.4, 3.2, 12)):
        k.limb(hips, (x, 18, z), (x * 1.1, 18 - L, z * 1.1), 1.6, "kelp", "kelp", d=0.6)
    # ---------------------------------------------------------------- torso: stooped, the chasuble with a bronze cross
    to = k.part("torso", (0, 19, 0), (("x", 14),), "hips")
    k.stack(to, 0, 0, [(19, 9.0, 6.4), (25, 11.6, 7.0), (31, 12.6, 7.0)], "vest", "robe")
    k.box(to, C(0, 19.6, 3.4, 8.6, 11.4, 0.6), "kelp", tag="chasuble")
    k.box(to, C(0, 21, 3.75, 1.6, 9.0, 0.4), "bronze", tag="cross")
    k.box(to, C(0, 27, 3.75, 6.0, 1.6, 0.4), "bronze", tag="cross")
    barnacles(k, to, [(4.4, 29, 2, 0, 1), (-4.6, 24, 3.2, 0, 1)], s=1.0)
    # ---------------------------------------------------------------- the head: a fish's face in a deep hood, the lure
    hd = k.part("head", (0, 31, 0.8), (("x", -10),), "torso")
    k.box(hd, C(0, 30.4, 0.4, 8.4, 9.0, 8.0), "vest", tag="hood")
    k.box(hd, C(0, 30.4, 4.0, 6.0, 7.0, 1.4), "dark", tag="hood_mouth")
    k.box(hd, C(0, 30.6, 3.0, 5.2, 5.8, 4.0), "skin", tag="face")
    k.box(hd, C(0, 30.0, 4.8, 5.8, 1.6, 2.6), "skin", tag="jaw")          # the underbite of a deep-sea fish
    k.box(hd, C(0, 31.6, 5.2, 4.4, 0.8, 1.6), "dark", tag="mouth")
    for t in (-1.8, -0.9, 0, 0.9, 1.8):
        k.shard(hd, (t, 30.9, 6.6), (0, 1, 0.3), 1.8, 0.5, mat="bone", tag="tooth")
        k.shard(hd, (t + 0.45, 33.0, 6.2), (0, -1, 0.3), 1.4, 0.5, mat="bone", tag="tooth")
    for sx in (-2.0, 2.0):
        k.box(hd, C(sx, 34.0, 4.9, 1.4, 1.4, 0.4), "eye", group="glow", tag="eye")
        for g in range(3):
            k.box(hd, C(sx * 1.35, 29.8 - g * 1.0, 1.6, 0.4, 0.5, 2.6), "coral", tag="gill")
    k.box(hd, C(0, 38.6, -1.6, 4.6, 2.4, 4.4), "vest", tag="hood_peak")
    lure = [(0, 40.4, -1.2), (0, 43.0, 1.0), (0, 43.4, 4.0), (0, 41.6, 6.6), (0, 39.4, 7.6)]
    for (a, b), w in zip(zip(lure, lure[1:]), (1.0, 0.9, 0.8, 0.6)):
        k.limb(hd, a, b, w, "skin", "lure_stalk")
    k.blob(hd, (0, 37.6, 7.6), (1.6, 1.8, 1.6), "glow", "lure", step=0.6)
    # ---------------------------------------------------------------- arms: long sleeves, webbed claws
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 7.0
        up = k.part("arm_" + nm, (x, 29.6, 0), (("x", -60 if side > 0 else -40), ("z", side * 10)), "torso")
        fo = k.part("fore_" + nm, (x, 21.6, 0), (("x", -50 if side > 0 else -40),), up)
        hn = k.part("hand_" + nm, (x, 13.8, 0), (), fo)
        k.box(up, C(x, 21.4, 0, 3.8, 8.4, 4.0), "vest", tag="sleeve")
        k.stack(fo, x, 0, [(13.4, 6.4, 6.4), (17, 5.0, 5.0), (21.6, 4.0, 4.0)], "vest", "sleeve")
        k.box(hn, C(x, 11.4, 0.4, 3.0, 3.0, 3.0), "skin", tag="hand")
        for t in (-1.0, 0, 1.0):
            k.shard(hn, (x + t, 11.6, 1.0), (t * 0.3, -1, 0.3), 3.6, 0.8, mat="bone", tag="claw")
    # the conch staff
    st = k.part("staff", (-7, 12.6, 0.8), (("x", 70),), k.parts["hand_r"])
    k.limb(st, (-7, -8, 0.8), (-7, 32, 0.8), 1.3, "stone", "haft")
    for y in (6.0, 18.0):
        k.ring(st, -7, y, 0.8, 1.1, 0.6, "rope", "wrap", n=8, axis="y")
    k.blob(st, (-7, 35.6, 0.8), (3.0, 4.6, 3.0), "wax", "conch", step=0.9)
    for y, r in ((34, 3.6), (36.4, 3.0), (38.6, 2.0)):
        k.ring(st, -7, y, 0.8, r, 0.7, "coral", "conch_spiral", n=10, axis="y")
    k.shard(st, (-7, 39.6, 0.8), (0, 1, 0), 3.6, 1.6, mat="shell", tag="conch_tip")
    k.box(st, C(-7, 33.0, 3.6, 2.2, 3.2, 0.6), "glow", group="glow", tag="conch_mouth")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Net Thrower (skirmisher)

def net_thrower():
    """The fishermen moored at the point came up with the rest. This one is all hunch and sinew in an oilskin coat,
    a sou'wester hat dripping weed over a face with no lips left, a pale eel coiled round his arm. A net is slung
    over his back with cork floats and hooks hanging off it; he throws it, and drags you in, and finishes you with
    the harpoon."""
    k = X.Kit("net_thrower")
    hips = k.part("hips", (0, 18, 0))
    k.box(hips, C(0, 15.4, 0, 8.6, 3.8, 5.6), "vest", tag="trousers")
    k.box(hips, C(0, 18.0, 0, 9.2, 1.6, 6.0), "rope", tag="belt")
    k.box(hips, C(4.8, 12.4, 1.8, 2.2, 4.6, 1.6), "iron", tag="knife")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.6
        th = k.part("thigh_" + nm, (x, 18, 0), (("x", -16), ("z", side * 6)), "hips")
        sh = k.part("shin_" + nm, (x, 10, 0), (("x", 26),), th)
        ft = k.part("foot_" + nm, (x, 2, 0), (("x", -10),), sh)
        k.box(th, C(x, 10, 0, 3.6, 8.6, 3.8), "vest", tag="trouser")
        k.box(sh, C(x, 2, 0, 3.8, 8.4, 4.0), "shell", tag="wader")
        k.box(sh, C(x, 8.4, 0, 4.6, 1.6, 4.8), "shell", tag="wader_top")
        k.box(ft, C(x, 0, 1.2, 4.0, 2.4, 6.2), "shell", tag="foot")
    # ---------------------------------------------------------------- torso: bent double, an oilskin coat
    to = k.part("torso", (0, 18.4, 0), (("x", 30),), "hips")
    k.stack(to, 0, 0, [(18, 8.6, 5.8), (24, 10.4, 6.6), (29, 11.4, 6.8)], "oil", "oilskin")
    for sx in (-2.6, 2.6):
        k.box(to, C(sx, 7, 3.2, 4.0, 12, 0.6), "oil", tag="coat_skirt")
        k.box(to, C(sx, 7, -3.2, 4.0, 12, 0.6), "oil", tag="coat_skirt")
    for y in (20.0, 23.0, 26.0):
        k.box(to, C(0.6, y, 3.4, 1.0, 1.0, 0.4), "bronze", tag="clasp")
    # the net on his back: a grid of rope, floats and hooks
    for i in range(6):
        k.limb(to, (-6 + i * 2.4, 30, -3.8), (-7 + i * 2.8, 12, -5.4), 0.5, "rope", "net")
    for j in range(6):
        y = 29 - j * 3.2
        k.limb(to, (-6.6, y, -3.9 - j * 0.3), (6.6 + j * 0.3, y, -3.9 - j * 0.3), 0.5, "rope", "net")
    for (x, y) in ((-6, 15), (-2, 13.4), (3, 14), (7, 16), (5, 24), (-5, 25)):
        k.box(to, C(x, y, -5.2, 2.0, 1.4, 1.4), "coral" if (x + y) % 2 else "wax", tag="float")
    for (x, y) in ((-4, 12), (1, 11.4), (6, 12.4)):
        k.limb(to, (x, y, -5.4), (x, y - 2.6, -5.4), 0.4, "iron", "hook")
        k.limb(to, (x, y - 2.6, -5.4), (x + 1.0, y - 1.8, -5.4), 0.4, "iron", "hook")
    # ---------------------------------------------------------------- the head: sou'wester, no lips, weed
    hd = k.part("head", (0, 29.4, 0.6), (("x", -24),), "torso")
    k.box(hd, C(0, 29.4, 0.6, 5.2, 5.6, 5.2), "skin", tag="face")
    k.box(hd, C(0, 30.0, 3.25, 3.6, 1.2, 0.3), "dark", tag="mouth")
    for t in (-1.4, -0.7, 0, 0.7, 1.4):
        k.box(hd, C(t, 30.0, 3.4, 0.4, 1.2, 0.2), "bone", tag="tooth")
    for sx in (-1.3, 1.3):
        k.box(hd, C(sx, 32.4, 3.25, 1.2, 0.8, 0.3), "eye", group="glow", tag="eye")
    k.blob(hd, (0, 35.2, 0.4), (3.2, 1.6, 3.4), "oil", "hat")
    k.box(hd, C(0, 34.0, -0.6, 7.4, 0.6, 9.6), "oil", tag="brim")
    for (x, L) in ((-3.0, 4), (-1.0, 6), (1.6, 3), (3.2, 5)):
        k.limb(hd, (x, 34, -4.4), (x, 34 - L, -4.8), 0.8, "kelp", "weed")
    # ---------------------------------------------------------------- arms: sinew, the eel round the left
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 6.6
        up = k.part("arm_" + nm, (x, 27.4, 0), (("x", -70 if side > 0 else -40), ("z", side * 12)), "torso")
        fo = k.part("fore_" + nm, (x, 19.6, 0), (("x", -40 if side > 0 else -70),), up)
        hn = k.part("hand_" + nm, (x, 12.4, 0), (), fo)
        k.box(up, C(x, 19.8, 0, 3.4, 7.8, 3.6), "oil", tag="sleeve")
        k.box(fo, C(x, 12.8, 0, 2.6, 7.0, 2.8), "skin", tag="forearm")
        k.box(hn, C(x, 10.0, 0.3, 2.8, 2.8, 2.8), "skin", tag="hand")
        if side > 0:
            for i in range(5):
                a = i * 1.5
                k.limb(fo, (x + math.cos(a) * 2.0, 13.4 + i * 1.4, math.sin(a) * 2.0),
                       (x + math.cos(a + 1.5) * 2.0, 14.8 + i * 1.4, math.sin(a + 1.5) * 2.0), 1.0, "wax", "eel")
            k.box(fo, C(x + 1.4, 21.2, 1.4, 1.8, 1.2, 2.4), "wax", tag="eel_head")
            k.box(fo, C(x + 1.4, 21.6, 2.4, 0.4, 0.4, 0.4), "eye", group="glow", tag="eel_eye")
    # the harpoon in the right hand: a long shaft, a barbed iron head, a rope trailing back
    hp = k.part("harpoon", (-6.6, 11.4, 0.6), (("x", 90),), k.parts["hand_r"])
    k.limb(hp, (-6.6, -4, 0.6), (-6.6, 30, 0.6), 1.2, "rope", "shaft")
    k.limb(hp, (-6.6, 30, 0.6), (-6.6, 34, 0.6), 1.2, "iron", "socket")
    k.shard(hp, (-6.6, 34, 0.6), (0, 1, 0), 6.0, 2.0, mat="iron", tag="harpoon_head")
    for sx in (-1, 1):
        k.shard(hp, (-6.6, 35.6, 0.6), (sx * 0.5, -1, 0), 2.6, 0.8, mat="iron", tag="barb")
    k.ring(hp, -6.6, 28, 0.6, 1.4, 0.6, "iron", "eye_ring", n=8, axis="y")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Crab Knight (brute)

def crab_knight():
    """A knight of the chapel's order, drowned in his plate, and the crabs came and lived in it and grew. Now the
    shell is the armour: red-brown carapace in overlapping plates, the old bronze showing in the joints, a great
    spiked carapace over each shoulder. His left arm is gone into one huge crushing claw; his right still holds his
    sword, barnacled to the hilt. His helm is a crab's head: eye stalks out of the visor, mouthparts working
    beneath it."""
    k = X.Kit("crab_knight")
    hips = k.part("hips", (0, 22, 0))
    k.stack(hips, 0, 0, [(17, 13, 9), (22, 14, 9.4)], "bronze", "girdle")
    for i, x in enumerate((-4.4, 0, 4.4)):          # carapace tassets
        k.box(hips, C(x, 13.6, 4.6, 4.6, 6.4, 1.2), "shell", tag="tasset")
        k.box(hips, C(x, 13.6, -4.6, 4.6, 6.4, 1.2), "shell", tag="tasset")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 3.8
        th = k.part("thigh_" + nm, (x, 21, 0), (("x", -8), ("z", side * 6)), "hips")
        sh = k.part("shin_" + nm, (x, 11.6, 0), (("x", 12),), th)
        ft = k.part("foot_" + nm, (x, 3.0, 0), (("x", -4),), sh)
        k.box(th, C(x, 11.8, 0, 5.4, 9.6, 6.0), "bronze", tag="cuisse")
        k.box(th, C(x, 12.6, 0.4, 6.2, 7.6, 6.4), "shell", tag="cuisse_shell")
        k.blob(th, (x, 12.0, 2.6), (3.2, 2.2, 2.4), "shell", "knee")
        k.shard(th, (x, 12.4, 4.6), (0, 0.3, 1), 3.0, 1.6, mat="shell", tag="knee_spike")
        k.stack(sh, x, 0, [(3, 5.6, 6.0), (8, 6.4, 6.8), (11.6, 5.6, 6.0)], "shell", "greave")
        k.box(ft, C(x, 0, 1.6, 6.0, 3.0, 9.0), "shell", tag="foot")
        for t in (-1.6, 1.6):
            k.shard(ft, (x + t, 1.0, 5.6), (t * 0.2, -0.2, 1), 2.6, 1.4, mat="shell", tag="foot")
    # ---------------------------------------------------------------- torso: carapace plates over bronze
    to = k.part("torso", (0, 22, 0), (("x", 10),), "hips")
    k.stack(to, 0, 0, [(22, 14, 9.4), (28, 18, 11), (34, 21, 12), (38, 19, 11)], "bronze", "cuirass")
    for i, y in enumerate((23.0, 26.6, 30.2, 33.8)):          # overlapping plates, each a little wider
        k.box(to, C(0, y, 5.4 - i * 0.1, 13 + i * 2.2, 3.6, 1.6), "shell", tag="plate")
        k.box(to, C(0, y, 6.1 - i * 0.1, 10 + i * 2.0, 0.6, 0.6), "shell", tag="plate_edge")
    k.box(to, C(0, 27, -5.8, 16, 11, 1.4), "shell", tag="back_plate")
    for z in (-3.0, -6.0):
        k.shard(to, (0, 37, z), (0, 0.6, -1), 5.0, 2.2, mat="shell", tag="back_spike")
    barnacles(k, to, [(6, 24, 6.4, 0, 1), (-7, 32, 6.0, 0, 1), (5, 36, -5.6, 0, 0), (-6, 25, -6.4, 0, 0)])
    # the shoulders: a great spiked carapace on each, like a crab's back
    for side in (1, -1):
        sx = side * 11.0
        k.blob(to, (sx, 36.6, 0), (6.0, 3.6, 6.4), "shell", "pauldron")
        for i, (dz, L) in enumerate(((-3.6, 4.0), (-1.2, 5.6), (1.2, 5.0), (3.6, 3.4))):
            k.shard(to, (sx + side * 3.4, 37.6, dz), (side * 1.0, 0.8, dz * 0.1), L, 1.6, mat="shell", tag="pauldron_spike")
        k.box(to, C(sx, 34.0, 0, 13.0, 1.2, 12.6), "bronze", tag="pauldron_rim")
    # ---------------------------------------------------------------- the helm: a crab's face, eye stalks, mouthparts
    hd = k.part("head", (0, 38, 0.4), (("x", -8),), "torso")
    k.box(hd, C(0, 38.0, 0.4, 7.0, 6.6, 7.4), "bronze", tag="helm")
    k.blob(hd, (0, 44.0, 0.2), (4.8, 1.8, 4.8), "shell", "crown_shell")
    k.box(hd, C(0, 41.0, 4.15, 6.0, 1.0, 0.4), "dark", tag="visor")
    for sx in (-1, 1):
        k.limb(hd, (sx * 1.6, 41.4, 4.0), (sx * 2.6, 46.0, 5.6), 0.9, "shell", "eye_stalk")
        k.box(hd, C(sx * 2.6, 46.0, 5.6, 1.6, 1.6, 1.6), "eye", group="glow", tag="eye")
    for i, sx in enumerate((-1.8, -0.6, 0.6, 1.8)):
        k.limb(hd, (sx, 39.2, 4.2), (sx * 1.2, 36.6, 5.6), 0.7, "coral", "mouthpart")
    # ---------------------------------------------------------------- arms: the claw and the sword
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 11.0
        up = k.part("arm_" + nm, (x, 35, 0), (("x", -30 if side > 0 else -50), ("z", side * 12)), "torso")
        fo = k.part("fore_" + nm, (x, 26, 0), (("x", -50 if side > 0 else -30),), up)
        hn = k.part("hand_" + nm, (x, 17, 0), (), fo)
        k.stack(up, x, 0, [(26, 5.4, 5.6), (35, 6.2, 6.4)], "shell", "rerebrace")
        if side > 0:     # the great claw: thick forearm, a fixed jaw and a hinged one, serrated
            k.stack(fo, x, 0, [(17, 9.0, 9.0), (22, 8.0, 8.0), (26, 6.4, 6.4)], "shell", "claw_arm")
            k.box(hn, C(x, 7.0, 0.4, 9.6, 10.0, 9.4), "shell", tag="claw_palm")
            k.box(hn, C(x - 1.6, -5.0, 0.4, 5.4, 12.0, 6.4), "shell", tag="claw_fixed")
            k.shard(hn, (x - 1.6, -5.0, 0.4), (0.15, -1, 0), 4.0, 4.0, mat="shell", tag="claw_fixed")
            jaw = k.part("claw_jaw", (x + 3.0, 7.0, 0.4), (("z", -16),), hn)
            k.box(jaw, C(x + 3.2, -3.0, 0.4, 4.0, 10.0, 5.6), "shell", tag="claw_jaw")
            k.shard(jaw, (x + 3.2, -3.0, 0.4), (-0.2, -1, 0), 3.4, 3.4, mat="shell", tag="claw_jaw")
            for y in (-3.0, 0.0, 3.0):
                k.box(hn, C(x + 1.4, y, 0.4, 1.2, 1.4, 1.6), "bone", tag="serration")
                k.box(jaw, C(x + 1.0, y + 1.0, 0.4, 1.2, 1.4, 1.6), "bone", tag="serration")
            barnacles(k, hn, [(x - 4.8, 10, 2, 0, 0), (x + 2, 14, 4.6, 0, 1), (x - 4, 2, -2, 0, 0)])
        else:
            k.stack(fo, x, 0, [(17, 5.0, 5.0), (22, 5.8, 5.8), (26, 5.2, 5.2)], "shell", "vambrace")
            k.box(hn, C(x, 13.6, 0.4, 4.4, 4.0, 4.4), "bronze", tag="gauntlet")
    # the sword: a broad drowned blade, notched, the hilt crusted with barnacles
    sw = k.part("sword", (-11, 15.6, 0.6), (("x", 80),), k.parts["hand_r"])
    k.box(sw, C(-11, 12.6, 0.6, 1.6, 6.0, 1.6), "rope", tag="grip")
    k.box(sw, C(-11, 18.6, 0.6, 1.8, 1.4, 9.0), "bronze", tag="crossguard")
    k.box(sw, C(-11, 11.2, 0.6, 2.2, 1.8, 2.2), "bronze", tag="pommel")
    k.box(sw, C(-11, 20, 0.6, 1.0, 22, 4.6), "iron", tag="blade")
    k.shard(sw, (-11, 42, 0.6), (0, 1, 0), 4.0, 4.4, mat="iron", tag="blade")
    for y in (25, 31, 36):
        k.box(sw, C(-11, y, 2.9, 1.2, 1.4, 0.8), "dark", tag="notch")
    barnacles(k, sw, [(-11, 19.6, 3.6, 0, 1), (-11, 21, -2.4, 0, 0), (-11, 24, 2.4, 0, 1)], s=0.9)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Tide Crab (swarm, on the spider)

def tide_crab():
    """The crabs of the drowned chapel take what they find for shells, and this one found a bronze reliquary: it
    wears the little gilded house on its back, the saint's window glowing, two candle stubs still burning on the
    roof. One claw is small; the other is a crusher half the size of its body."""
    k = X.Kit("tide_crab")
    body = k.part("body", (0, 6, 0))
    k.blob(body, (0, 5.4, 0), (5.6, 2.4, 4.6), "shell", "carapace")
    k.box(body, C(0, 3.6, 0, 9.0, 1.0, 7.4), "shell", tag="carapace_rim")
    # the reliquary it wears: a little bronze chapel, gilt roof, a glowing window, candles
    ab = k.part("abdomen", (0, 7, -2), (), "body")
    k.box(ab, C(0, 7, -2.6, 7.4, 5.4, 6.6), "bronze", tag="reliquary")
    k.box(ab, C(0, 12.4, -2.6, 8.2, 1.0, 7.4), "gold", tag="roof")
    k.box(ab, C(0, 13.4, -2.6, 6.0, 1.0, 5.4), "gold", tag="roof")
    k.box(ab, C(0, 14.4, -2.6, 3.6, 1.0, 3.6), "gold", tag="roof")
    k.box(ab, C(0, 8.6, 0.75, 2.8, 3.4, 0.4), "glow", group="glow", tag="window")
    k.box(ab, C(0, 9.6, 0.85, 3.6, 0.5, 0.4), "gold", tag="window_frame")
    for sx in (-3.9, 3.9):
        k.box(ab, C(sx, 7, -2.6, 0.6, 6.0, 7.2), "gold", tag="corner")
    for (x, z, h) in ((-1.8, -3.6, 1.8), (1.6, -1.4, 2.6)):
        k.box(ab, C(x, 15.4, z, 0.8, h, 0.8), "wax", tag="candle")
        k.box(ab, C(x, 15.4 + h, z, 0.5, 0.9, 0.5), "flame", group="glow", tag="flame")
    barnacles(k, ab, [(3.8, 8, -5.8, 1, 0), (-3.6, 10, -5.6, 0, 0)], s=0.9)
    hd = k.part("head", (0, 6, 3.6), (), "body")
    k.box(hd, C(0, 4.6, 4.6, 4.6, 2.4, 2.0), "shell", tag="head")
    for sx in (-1, 1):
        k.limb(hd, (sx * 1.2, 6.6, 5.2), (sx * 1.8, 9.4, 6.0), 0.6, "shell", "eye_stalk")
        k.box(hd, C(sx * 1.8, 9.2, 6.0, 1.0, 1.0, 1.0), "eye", group="glow", tag="eye")
        k.limb(hd, (sx * 0.8, 5.0, 5.6), (sx * 1.2, 3.6, 6.8), 0.5, "coral", "mouthpart")
    # the claws: the crusher on the right, a pincer on the left
    for side, big in ((1, False), (-1, True)):
        s = 2.0 if big else 1.0
        cp = k.part("claw%d" % (side > 0), (side * 4.0, 5.6, 4.0), (("y", side * 20),), hd, bone=False)
        k.limb(cp, (side * 4.0, 5.6, 4.0), (side * 6.0, 5.6, 8.0), 1.6 * s ** 0.5, "shell", "claw_arm")
        k.box(cp, C(side * 6.0, 4.0, 8.6 + s, 3.4 * s, 3.0 * s, 3.6 * s), "shell", tag="claw")
        k.shard(cp, (side * 6.0 - side * 0.6 * s, 4.6, 8.6 + 2.6 * s), (0, 0, 1), 3.6 * s, 1.6 * s, mat="shell", tag="claw")
        k.shard(cp, (side * 6.0 + side * 0.6 * s, 5.6 + s, 8.6 + 2.0 * s), (0, -0.3, 1), 3.0 * s, 1.2 * s, mat="shell", tag="claw")
    joints = {"body": "Root", "head": "Head", "abdomen": "Stomach"}
    for side, s in ((1, "l"), (-1, "r")):
        for i, z in enumerate((2.0, 0.6, -0.8, -2.2)):
            nm = "leg_%s%d" % (s, i)
            lg = k.part(nm, (side * 4.4, 5, z), (("y", -side * (i - 1.5) * 18),), "body")
            knee = (side * 8.8, 8.0, z)
            k.limb(lg, (side * 4.4, 5.0, z), knee, 1.4, "shell", "femur")
            k.limb(lg, knee, (side * 11.0, 0.6, z), 1.0, "shell", "tibia")
            k.shard(lg, (side * 11.0, 1.2, z), (side * 0.2, -1, 0), 1.6, 0.8, mat="coral", tag="foot")
            joints[nm] = ("LL" if side > 0 else "RL") + str(i + 1)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


MOBS = {
    "tide_crab": dict(make=tide_crab, rig="crawler", ent=(1.1, 0.7), stats=dict(hp=16, speed=0.32, dmg=4, armor=4, kb=0)),
    "crab_knight": dict(make=crab_knight, ent=(1.4, 3.4), stats=dict(hp=70, speed=0.19, dmg=10, armor=10, kb=0.8)),
    "tide_priest": dict(make=tide_priest, ent=(0.9, 2.8), stats=dict(hp=30, speed=0.21, dmg=5, armor=2, kb=0)),
    "net_thrower": dict(make=net_thrower, ent=(0.9, 2.7), stats=dict(hp=26, speed=0.3, dmg=6, armor=2, kb=0)),
    "barnacle_choir": dict(make=barnacle_choir, ent=(1.3, 3.4), stats=dict(hp=150, speed=0.2, dmg=10, armor=8, kb=0.6), key=True),
    "drowned_bell": dict(make=drowned_bell, texel=1, ent=(3.0, 6.4), stats=dict(hp=440, speed=0.2, dmg=16, armor=10, kb=1.0), boss=True),
}
