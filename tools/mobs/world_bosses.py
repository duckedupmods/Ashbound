"""The five overworld bosses (WorldBosses.java): fought out in the world whenever you like, called with a summon item on
open ground of their own land, away from towns. One per region and mood. v2 (11/7): rebuilt from heavy masses like the
Walking Mountain (blobs, tilted slabs, one glow colour each, a story prop), not boxes on stock limbs.

    cairn_giant        mountains   a hunched giant of piled boulders, shoulders higher than its little slate head, fists
                                   like rockfalls, a cairn of skulls on its back, green runes cut into its chest and into
                                   the standing stone it drags for a club
    hart_lord          forest      the lord of the old hunt: a tall hunched stag-skull hunter on deer legs, antlers like a
                                   dead tree hung with trophy skulls, an open ribcage with a green heart, a leaf-and-hide
                                   cape to the ground, clawed hands, a crescent axe of antler bone
    saltglass_hydra    coast       a heavy sea-croc body crusted with salt glass; three long necks rising in S-curves,
                                   jaws open on glass teeth and a throat of cold light; a crest of crystal on each head
    ironback_scorpion  badlands    a scorpion the size of a cart, eight legs, overlapping rusted iron plates with rivets,
                                   crab-heavy pincers, a segmented tail arched over to a venom bulb and a green stinger
    rime_lich          snow        a gaunt dead mage in a midnight robe, a skull deep in its hood, a fan of ice behind
                                   its head and a jagged icicle crown, an open ribcage holding the cold heart, long bone
                                   fingers, a twisted staff with a caged phylactery

    python tools/monsterforge.py world_bosses --preview ; python tools/connect_check.py world_bosses
"""
import math

import vox2 as X
from vox2 import ramp
from serpent_ziggurat import grow
from _folk import lit, held
from tidewrack import Cc
from world_beasts import teeth, leg

STONE = ramp("#1c1c1a", "#2c2c28", "#3e3e38", "#53534b", "#6a6a60", "#848478")
MOSS = ramp("#0c1806", "#16260a", "#22380e", "#2e4a14", "#3c5e1a", "#4e7422")
BONE = ramp("#3a342c", "#57503f", "#787058", "#9a9078", "#bcb298", "#dcd2b8")
HIDE = ramp("#1a120a", "#2a1c10", "#3c2a18", "#503a22", "#664a2e")
FUR = ramp("#120c08", "#1e150e", "#2c2014", "#3c2c1c", "#4e3a24")
LEAF = ramp("#141a06", "#22300a", "#34460e", "#4a5e16", "#62781e", "#7c9228")
BARK = ramp("#0e0a06", "#18120c", "#241a12", "#322418", "#40301e")
ROPE = ramp("#2a2014", "#3c2e1c", "#504026", "#665232")
SALT = ramp("#2a3a40", "#3e5258", "#566e74", "#728c90", "#94acae", "#bccccc")
SEA = ramp("#050f14", "#08181f", "#0d242c", "#13323c", "#1a424e", "#22545e")
BELLY = ramp("#2c3a36", "#3e4e48", "#52645c", "#687a70")
RUST = ramp("#1a0a04", "#2e1408", "#48200c", "#642e12", "#823e18", "#a05222")
IRON = ramp("#0a0a0c", "#141418", "#202026", "#2e2e36", "#3e3e48", "#50505c")
ROBE = ramp("#05070c", "#0a0e16", "#111722", "#1a2232", "#243044", "#2e3c54")
FROST = ramp("#2a3a4c", "#3e5268", "#566e88", "#7290aa", "#94b2c8", "#c0d8e8")
ICE = ramp("#3a6080", "#5884a4", "#7aa8c4", "#a0c8dc", "#c8e4f0", "#eef8ff")
GREEN = ramp("#0a3010", "#14501c", "#207a2c", "#36a440", "#5ccc5a", "#a0f090")
COLD = ramp("#06304a", "#0c5878", "#1a84a8", "#3cb4dc", "#8ee0f8", "#e2faff")
TAR = ramp("#010101", "#040404", "#080808", "#0c0c0c")


def cracks(p, n, i, j, w, h):
    """stone in rough blocks: dark joints between them, faces a touch uneven"""
    v = X.fbm(p[0] * 0.35, p[1] * 0.35, p[2] * 0.35)
    if v > 0.46 and v < 0.5:
        return -0.34
    return 0.08 if v > 0.66 else (-0.07 if v < 0.28 else 0)


def strands(p, n, i, j, w, h):
    return -0.2 if (i + int(2 * X.fbm(p[0] * 0.4, p[1] * 0.1, p[2] * 0.4))) % 3 == 0 else 0.04


def plates(p, n, i, j, w, h):
    return -0.26 if j % 5 == 0 else (0.06 if j % 5 == 1 else 0)


def shaders():
    return {
        "stone": X.surf(STONE, 0.5, 1.3, 0.22, 0.18, crust=(MOSS, 0.22), pattern=cracks),
        "moss": X.surf(MOSS, 0.52, 1.1, 0.3, 0.02, pattern=strands),
        "bone": X.surf(BONE, 0.56, 1.25, 0.14, 0.14),
        "hide": X.surf(HIDE, 0.5, 1.0, 0.22, 0.06, holes=True),
        "fur": X.surf(FUR, 0.5, 1.1, 0.2, 0.02, pattern=strands),
        "leaf": X.surf(LEAF, 0.5, 1.0, 0.32, 0.04, holes=True),
        "bark": X.surf(BARK, 0.5, 1.0, 0.24, 0.08, stripe=2),
        "rope": X.surf(ROPE, 0.5, 1.0, 0.2, 0.0, stripe=2),
        "salt": X.facets(SALT),
        "sea": X.wrinkled(SEA, 0.8),
        "belly": X.surf(BELLY, 0.5, 1.1, 0.14, 0.04, pattern=plates),
        "rust": X.surf(RUST, 0.5, 1.4, 0.26, 0.2, rust=(IRON, 0.3, 0.5)),
        "iron": X.surf(IRON, 0.5, 1.5, 0.18, 0.26, rust=(RUST, 0.32, 0.45)),
        "robe": X.surf(ROBE, 0.5, 1.1, 0.16, 0.06, holes=True, crust=(FROST, 0.16)),
        "frost": X.surf(FROST, 0.55, 1.4, 0.16, 0.24, crust=(ICE, 0.24)),
        "ice": X.facets(ICE),
        "green": X.glow(GREEN),
        "cold": X.glow(COLD),
        "eye": X.glow(GREEN, 0.86, 0.12),
        "ceye": X.glow(COLD, 0.86, 0.12),
        "dark": X.dark(TAR),
    }


GLOWS = {"green", "cold", "eye", "ceye"}

_n = [0]


def tilt(k, parent, at, rx=0.0, rz=0.0):
    """a little unboned part turned about `at`: a slab set crooked, a stone not quite square"""
    _n[0] += 1
    return k.part("tilt%d" % _n[0], at, tuple(r for r in (("x", rx), ("z", rz)) if r[1]), parent, bone=False)


def bezier(pts, n):
    """n+1 points along a Bezier through the control points"""
    out = []
    for i in range(n + 1):
        t = i / n
        q = list(pts)
        while len(q) > 1:
            q = [tuple(a[c] + (b[c] - a[c]) * t for c in range(3)) for a, b in zip(q, q[1:])]
        out.append(q[0])
    return out


def skull(k, part, c, s, mat="bone", eye_mat="dark"):
    """a small skull facing +z (a trophy, a cairn stone)"""
    x, y, z = c
    k.blob(part, (x, y, z), (s, s * 0.9, s), mat, "skull", step=0.4)
    k.box(part, Cc(x, y - s * 0.7, z + s * 0.3, s * 1.2, s * 0.6, s * 1.1), mat, tag="skull_jaw")
    for sx in (-1, 1):
        k.box(part, Cc(x + sx * s * 0.4, y + s * 0.05, z + s * 0.82, s * 0.5, s * 0.45, 0.3), eye_mat, tag="skull_eye")


# ================================================================ the Cairn Giant (mountains)

def cairn_giant():
    k = X.Kit("cairn_giant")
    hips = k.part("hips", (0, 20, 0))
    k.blob(hips, (0, 20, 0), (10, 5.5, 7.5), "stone", "pelvis", step=1.0)
    sl = tilt(k, hips, (0, 16, 7), rx=-6)
    k.box(sl, Cc(0, 15.0, 7.4, 8.0, 7.0, 1.6), "stone", tag="loin_slab")
    k.box(sl, Cc(0, 15.6, 8.3, 1.0, 4.4, 0.3), "green", tag="rune")
    # short, elephant-thick legs of piled stone
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 7.4
        th = k.part("thigh_" + nm, (x, 20, 0), (("x", -4), ("z", side * 4)), hips)
        sh = k.part("shin_" + nm, (x, 11, 0), (("x", 6),), th)
        ft = k.part("foot_" + nm, (x, 2.4, 0), (("x", -2),), sh)
        k.blob(th, (x, 16, 0), (5.4, 5.6, 5.4), "stone", "thigh", step=1.0)
        k.blob(th, (x + side * 0.8, 11.6, 2.4), (3.8, 3.0, 3.4), "stone", "knee", step=0.8)
        k.blob(sh, (x, 6.6, 0.2), (5.2, 5.2, 5.2), "stone", "shin", step=1.0)
        k.blob(sh, (x - side * 3.0, 8.6, 1.0), (1.6, 3.0, 2.4), "moss", "shin_moss", step=0.6)
        k.stack(ft, x, 1.4, [(0, 10.0, 11.0), (2.8, 8.6, 9.0)], "stone", "foot")
        for t in (-3.0, 0.0, 3.0):
            k.blob(ft, (x + t, 1.3, 7.0), (1.6, 1.3, 1.6), "stone", "foot", step=0.6)
    # the body: a hunched heap of boulders, the head sunk low between the shoulders
    to = k.part("torso", (0, 22, 0), (("x", 18),), "hips")
    k.blob(to, (0, 27, 1), (10.5, 6.0, 8.0), "stone", "belly", step=1.0)
    k.blob(to, (0, 35, 1.5), (14.0, 8.0, 9.5), "stone", "chest", step=1.0)
    k.blob(to, (0, 40, -3), (13.0, 7.0, 9.0), "stone", "hump", step=1.0)
    for x, y, z, w, h, rz in ((-5.4, 36.0, 10.2, 8.4, 6.4, 7), (5.4, 36.4, 10.2, 8.0, 6.0, -6), (-4.6, 29.0, 8.6, 7.0, 5.4, -9),
                              (4.8, 29.4, 8.6, 7.4, 5.2, 8)):
        s = tilt(k, to, (x, y, z), rx=-6, rz=rz)
        k.box(s, Cc(x, y, z, w, h, 2.4), "stone", tag="chest_slab")
    # the runes cut into the chest slabs, burning green
    for a, b in (((-4.0, 31.0, 10.0), (-5.6, 27.4, 10.0)), ((-5.6, 27.4, 10.0), (-3.4, 26.6, 10.0)), ((4.6, 31.0, 10.0), (5.6, 27.8, 10.0))):
        k.limb(to, a, b, 0.7, "green", "rune", group="glow")
    for sx in (-1, 1):
        k.blob(to, (sx * 2.0, 32.4, 10.4), (1.6, 3.6, 1.4), "moss", "moss_seam", step=0.6)
    # boulder shoulders, higher than the head, each with a little cairn and a cap of moss
    for sx in (-1, 1):
        k.blob(to, (sx * 15.0, 41.0, 1.0), (7.6, 7.2, 7.6), "stone", "shoulder", step=1.0)
        k.blob(to, (sx * 15.4, 47.4, 0.4), (4.2, 2.6, 4.0), "stone", "shoulder_stone", step=0.7)
        k.blob(to, (sx * 16.0, 50.6, -0.4), (2.4, 1.8, 2.2), "stone", "shoulder_stone", step=0.6)
        k.blob(to, (sx * 14.6, 46.2, 1.4), (6.4, 1.4, 6.0), "moss", "moss_cap", step=0.5)
        for i, (dx, dz, L) in enumerate(((-3.0, 6.4, 7.0), (0.0, 7.2, 9.0), (3.0, 6.4, 6.0), (4.6, 2.0, 8.0))):
            x0 = sx * 15.0 + sx * dx
            k.limb(to, (x0, 46.0, dz), (x0 + sx * 0.4, 46.0 - L, dz + 1.6), 1.2, "moss", "moss_hang")
    # the cairn on its back: boulders piled up, skulls set among them, a standing stone on top
    for x, y, z, r in ((0.0, 47.0, -5.0, 6.4), (-4.4, 52.0, -6.0, 4.4), (3.8, 53.0, -5.0, 4.0), (0.0, 57.6, -6.0, 3.4), (-1.0, 61.0, -6.4, 2.4)):
        k.blob(to, (x, y, z), (r, r * 0.75, r * 0.9), "stone", "cairn", step=0.8)
    cap = tilt(k, to, (-1.0, 62.0, -6.4), rz=8)
    k.box(cap, Cc(-1.0, 66.0, -6.4, 2.6, 9.0, 2.2), "stone", tag="capstone")
    k.limb(cap, (-1.0, 63.0, -5.2), (-1.0, 69.0, -5.2), 0.6, "green", "rune", group="glow")
    for c in ((-4.0, 54.6, -2.6), (3.6, 50.6, -1.0), (1.4, 59.4, -3.4), (-6.6, 49.0, -1.8)):
        skull(k, to, c, 1.6)
    # the head: a slate face under a heavy brow, an underbite of stone teeth, green embers for eyes
    hd = k.part("head", (0, 36, 11), (("x", -18),), "torso")
    k.blob(hd, (0, 37.0, 13.0), (5.8, 5.2, 5.4), "stone", "skull", step=0.8)
    k.box(hd, Cc(0, 40.2, 17.6, 12.4, 2.6, 3.6), "stone", tag="brow")
    k.shard(hd, (-5.4, 40.6, 16.6), (-0.8, 0.4, 0.2), 3.0, 1.6, mat="stone", tag="brow_horn")
    k.shard(hd, (5.4, 40.6, 16.6), (0.8, 0.4, 0.2), 3.0, 1.6, mat="stone", tag="brow_horn")
    for sx in (-1, 1):
        k.box(hd, Cc(sx * 2.6, 37.8, 18.2, 3.2, 2.2, 0.8), "dark", tag="socket")
        k.box(hd, Cc(sx * 2.6, 37.8, 18.6, 1.8, 1.2, 0.4), "eye", tag="eye")
        k.box(hd, Cc(sx * 4.6, 36.0, 16.8, 2.6, 2.8, 2.6), "stone", tag="cheek")
    k.box(hd, Cc(0, 36.6, 18.8, 2.0, 3.0, 1.6), "stone", tag="nose")
    k.box(hd, Cc(0, 32.8, 16.6, 10.0, 3.2, 5.6), "stone", tag="jaw")
    k.box(hd, Cc(0, 34.8, 18.6, 7.0, 1.2, 0.6), "dark", tag="mouth")
    teeth(k, hd, (-3.8, 34.2, 19.2), (3.8, 34.2, 19.2), 4, 2.0, down=False, w=1.1, mat="stone")
    # long ape arms to the knees, fists like rockfalls
    rots = {1: ((("x", -16), ("z", 10)), (("x", -18),)), -1: ((("x", -30), ("z", -4)), (("x", -34),))}
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 15.6
        ar, fr = rots[side]
        a = k.part("arm_" + nm, (x, 41, 1), ar, to)
        f = k.part("fore_" + nm, (x + side * 1.0, 28, 2), fr, a)
        h = k.part("hand_" + nm, (x + side * 1.6, 15, 3), (), f)
        k.limb(a, (x, 40, 1), (x + side * 1.0, 28.4, 2), 7.0, "stone", "upper_arm")
        k.blob(a, (x + side * 1.2, 28.6, 1.6), (4.6, 3.6, 4.6), "stone", "elbow", step=0.8)
        k.blob(f, (x + side * 1.4, 21.4, 2.6), (6.0, 7.0, 6.0), "stone", "forearm", step=1.0)
        k.blob(f, (x + side * 1.4, 23.0, 7.2), (2.2, 3.6, 1.4), "moss", "forearm_moss", step=0.6)
        k.blob(h, (x + side * 1.6, 10.6, 3.6), (5.6, 5.0, 5.8), "stone", "hand", step=0.9)
        for t in (-3.2, -1.1, 1.1, 3.2):
            k.blob(h, (x + side * 1.6 + t, 7.2, 7.8), (1.4, 1.6, 1.6), "stone", "hand", step=0.6)
    # the club: a standing stone pulled out of a ring, roped at the grip, runes down its face
    cl = held(k, "menhir", "r", (-17.2, 10.6, 3.6), (("x", 24), ("z", -12)))
    hx, hy, hz = -17.2, 10.6, 3.6
    k.stack(cl, hx, hz, [(hy - 8, 6.4, 6.0), (hy - 2, 9.0, 8.0), (hy + 18, 8.6, 7.6), (hy + 30, 6.4, 5.8), (hy + 35, 3.4, 3.2)], "stone", "menhir", step=1.2)
    for y in (hy - 2.4, hy + 0.4, hy + 3.0):
        k.box(cl, Cc(hx, y, hz, 9.4, 1.0, 8.4), "rope", tag="grip_rope")
    for zz in (3.95, -3.95):
        for y0, y1, dx in ((hy + 8, hy + 14, 1.4), (hy + 16, hy + 22, -1.2), (hy + 23, hy + 27, 1.0)):
            k.limb(cl, (hx - dx, y0, hz + zz), (hx + dx, y1, hz + zz), 0.7, "green", "rune", group="glow")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.15)
    return k.s, k.parts


# ================================================================ the Hart-Lord (forest)

def hart_lord():
    k = X.Kit("hart_lord")
    hips = k.part("hips", (0, 25, 0))
    k.blob(hips, (0, 25, 0), (6.0, 3.6, 4.6), "hide", "pelvis", step=0.8)
    for i in range(11):                              # a loin of hides and leaves, ragged
        a = (i / 11 - 0.5) * math.pi * 1.6
        x, z = math.sin(a) * 5.6, math.cos(a) * 4.0
        L = 9.0 + 3.0 * X.h3(i, 3, 1)
        k.limb(hips, (x, 26.0, z), (x * 1.15, 26.0 - L, z * 1.2 + 0.6), 2.2, "leaf" if i % 2 else "hide", "loin", d=0.7)
    # deer legs: a heavy thigh, the shin back to a high hock, a long cannon bone down to a cloven hoof
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 4.4
        th = k.part("thigh_" + nm, (x, 25, 0), (("x", -6), ("z", side * 3)), hips)
        sh = k.part("shin_" + nm, (x, 16, 4.0), (("x", 6),), th)
        ft = k.part("foot_" + nm, (x, 8, -2.6), (("x", -2),), sh)
        k.blob(th, (x, 20.6, 1.8), (3.6, 5.8, 4.2), "fur", "thigh", step=0.8)
        k.limb(sh, (x, 16.4, 4.0), (x, 8.0, -2.6), 2.6, "hide", "shin")
        k.blob(sh, (x, 8.6, -3.0), (1.8, 2.2, 1.8), "fur", "hock", step=0.5)
        k.limb(ft, (x, 8.0, -2.6), (x, 1.8, -0.8), 2.0, "hide", "cannon")
        for dx in (-0.8, 0.8):
            k.box(ft, Cc(x + dx, 1.0, -0.2, 1.4, 2.0, 3.4), "dark", tag="foot")
    # the body: hunched, a narrow waist under a deep chest, the ribs open on a green heart
    to = k.part("torso", (0, 25, 0), (("x", 14),), "hips")
    k.limb(to, (0, 25, 0), (0, 31, 0.4), 6.6, "hide", "waist", d=5.2)
    k.blob(to, (0, 35.6, 0.4), (7.6, 6.4, 5.2), "hide", "chest", step=0.8)
    k.box(to, Cc(0, 34.6, 4.4, 8.2, 9.0, 1.4), "dark", tag="rib_cavity")
    k.blob(to, (0, 34.4, 4.6), (1.9, 2.2, 1.2), "green", "heart", step=0.5)
    k.limb(to, (0, 30.0, 5.6), (0, 40.0, 5.2), 1.2, "bone", "sternum")
    for y in (31.0, 33.4, 35.8, 38.2):
        for sx in (-1, 1):
            k.limb(to, (0, y + 0.4, 5.6), (sx * 4.2, y - 0.4, 5.0), 0.9, "bone", "rib")
            k.limb(to, (sx * 4.2, y - 0.4, 5.0), (sx * 6.6, y - 1.4, 2.0), 0.9, "bone", "rib")
    # a mantle of fur and leaves, and a cape of them to the ground
    k.blob(to, (0, 41.0, -0.6), (10.6, 3.2, 6.8), "fur", "mantle", step=0.6)
    for i in range(14):
        a = i / 14 * 2 * math.pi
        x, z = math.cos(a) * 9.6, math.sin(a) * 6.0 - 0.6
        k.limb(to, (x, 42.0, z), (x * 1.25, 36.0, z * 1.25), 2.4, "leaf", "mantle_leaf", d=0.7)
    for i in range(12):
        x = -11.0 + i * 2.0
        L = 30.0 + 4.0 * X.h3(i, 7, 2)
        k.limb(to, (x * 0.8, 41.0, -5.6), (x * 1.2, 41.0 - L, -9.0 - (i % 3)), 2.4, "leaf" if i % 3 else "hide", "cape", d=0.8)
    # the head: a long stag skull, low and forward on a maned neck
    k.limb(to, (0, 40.0, 1.0), (0, 43.4, 4.6), 3.8, "fur", "mane")
    hd = k.part("head", (0, 43, 3), (("x", -6),), "torso")
    k.blob(hd, (0, 46.0, 4.6), (3.2, 3.0, 3.4), "bone", "cranium", step=0.6)
    k.limb(hd, (0, 45.6, 6.6), (0, 42.8, 13.6), 3.0, "bone", "muzzle", d=2.6)
    k.limb(hd, (0, 43.4, 6.4), (0, 41.2, 12.0), 2.2, "bone", "jaw", d=1.2)
    k.box(hd, Cc(0, 43.0, 14.0, 2.2, 1.4, 1.2), "dark", tag="nose")
    for sx in (-1, 1):
        k.box(hd, Cc(sx * 2.4, 46.4, 6.4, 1.2, 1.8, 2.0), "dark", tag="socket")
        k.box(hd, Cc(sx * 2.7, 46.4, 6.6, 0.4, 0.9, 1.0), "eye", tag="eye")
    teeth(k, hd, (-0.8, 42.6, 9.0), (0.8, 41.8, 12.6), 4, 1.2, down=True, w=0.5)
    for i in range(5):                               # a beard of moss under the jaw
        k.limb(hd, (-1.2 + i * 0.6, 41.6, 7.0 + i * 0.6), (-1.4 + i * 0.7, 37.4 - (i % 2), 7.6 + i * 0.5), 0.7, "moss", "jaw_moss")
    # the antlers: a dead tree, wider than its shoulders, hung with the skulls of what it hunted
    for sx in (-1, 1):
        pts = [(sx * 2.0, 48.4, 4.0), (sx * 6.0, 52.0, 2.6), (sx * 11.0, 56.0, 1.6), (sx * 15.0, 61.0, 0.6), (sx * 16.4, 67.0, -0.4), (sx * 14.6, 71.0, -1.0)]
        for (a, b), w in zip(zip(pts, pts[1:]), (2.0, 1.7, 1.4, 1.1, 0.8)):
            k.limb(hd, a, b, w, "bark", "antler")
        k.shard(hd, pts[1], (sx * 0.1, 0.4, 1.0), 5.0, 1.0, mat="bark", tag="brow_tine")
        for p, L in zip(pts[2:5], (6.0, 7.0, 5.0)):
            k.shard(hd, p, (sx * 0.15, 1.0, 0.4), L, 0.9, mat="bark", tag="tine")
        k.shard(hd, pts[3], (sx * 1.0, 0.5, -0.2), 5.0, 0.8, mat="bark", tag="tine")
        k.limb(hd, pts[2], (sx * 11.4, 50.4, 1.8), 0.4, "hide", "trophy_cord")
        skull(k, hd, (sx * 11.4, 49.0, 1.8), 1.2)
    # long arms, clawed hands, bark bracers
    rots = {1: ((("x", -18), ("z", 14)), (("x", -24),)), -1: ((("x", -56), ("z", -6)), (("x", -40),))}
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 8.6
        ar, fr = rots[side]
        a = k.part("arm_" + nm, (x, 39, 0), ar, to)
        f = k.part("fore_" + nm, (x + side * 0.8, 29, 1), fr, a)
        h = k.part("hand_" + nm, (x + side * 1.2, 19.4, 2.4), (), f)
        k.limb(a, (x, 39.4, 0), (x + side * 0.8, 29.0, 1.0), 3.2, "fur", "upper_arm")
        k.limb(f, (x + side * 0.8, 29.0, 1.0), (x + side * 1.2, 19.6, 2.4), 2.8, "hide", "forearm")
        for y in (21.6, 24.0, 26.4):
            k.box(f, Cc(x + side * 1.0, y, 1.8, 3.8, 1.2, 3.8), "bark", tag="bracer")
        k.blob(h, (x + side * 1.2, 17.6, 2.6), (1.8, 2.2, 1.8), "dark", "hand", step=0.5)
        for t in (-0.9, 0.0, 0.9):
            k.shard(h, (x + side * 1.2 + t, 15.8, 3.2), (t * 0.2, -1.0, 0.5), 4.6, 0.7, mat="bone", tag="claw")
    # the greataxe: a crescent of antler bone on a long haft, a green rune in it, a strip of hide off its beard
    ax = held(k, "axe", "r", (-9.8, 17.6, 2.6), (("x", 64),))
    hx, hy, hz = -9.8, 17.6, 2.6
    k.limb(ax, (hx, hy - 7.0, hz), (hx, hy + 32.0, hz), 1.3, "bark", "haft")
    for y in (hy - 1.6, hy + 1.6):
        k.box(ax, Cc(hx, y, hz, 1.9, 1.4, 1.9), "hide", tag="grip")
    cy = hy + 27.0
    arc = [(hx, cy + 8.0 * math.sin(a), hz + 2.4 + 5.6 * math.cos(a)) for a in [math.radians(-80 + i * 8) for i in range(21)]]
    for p, q in zip(arc, arc[1:]):
        k.limb(ax, p, q, 1.6, "bone", "axe_edge", d=1.0)
    for p in arc[1:-1]:
        k.limb(ax, (hx, cy + (p[1] - cy) * 0.5, hz + 0.6), p, 2.2, "bone", "axe_blade", d=0.9)
    k.limb(ax, (hx, cy - 2.4, hz + 4.4), (hx, cy + 2.4, hz + 4.4), 0.5, "green", "rune", group="glow")
    k.shard(ax, (hx, cy, hz - 0.4), (0, 0.4, -1), 5.0, 1.1, mat="bark", tag="axe_tine")
    k.limb(ax, arc[0], (hx, arc[0][1] - 6.0, arc[0][2] - 0.6), 0.9, "hide", "axe_strip", d=0.4)
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.12)
    return k.s, k.parts


# ================================================================ the Saltglass Hydra (coast)

def hydra_head(k, part, base, sway, rise, reach):
    """one neck, an S rising from `base`, and the head at its end: jaws open, glass teeth, a throat of cold light"""
    bx, by, bz = base
    pts = bezier([base, (bx + sway * 0.3, by + rise * 0.45, bz + reach * 0.05), (bx + sway * 0.8, by + rise * 0.8, bz + reach * 0.05),
                  (bx + sway, by + rise, bz + reach)], 9)
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        w = 5.4 - i * 0.24
        k.limb(part, a, b, w, "sea", "neck")
        if i % 2 == 0:
            k.shard(part, (b[0], b[1] + w * 0.36, b[2] - w * 0.3), (0, 0.7, -1), 2.4, 1.0, mat="salt", tag="neck_spine")
    hx, hy, hz = pts[-1]
    hz += 1.0
    first = len(k.s.boxes)
    _hydra_face(k, part, hx, hy, hz)
    c, f = (hx, hy, hz - 2.0), 1.35                  # the heads a size up: they are what you look at
    for b in k.s.boxes[first:]:
        b.lo = tuple(c[i] + (b.lo[i] - c[i]) * f for i in range(3))
        b.size = tuple(v * f for v in b.size)
        if getattr(b, "pivot", None) is not None:
            b.pivot = tuple(c[i] + (b.pivot[i] - c[i]) * f for i in range(3))


def _hydra_face(k, part, hx, hy, hz):
    k.blob(part, (hx, hy + 0.6, hz), (3.4, 2.8, 3.8), "sea", "skull", step=0.6)
    k.limb(part, (hx, hy + 1.0, hz + 2.0), (hx, hy + 0.2, hz + 9.0), 3.8, "sea", "snout", d=2.4)
    k.limb(part, (hx, hy - 1.2, hz + 1.6), (hx, hy - 4.6, hz + 7.6), 3.2, "sea", "lower_jaw", d=1.4)
    k.limb(part, (hx, hy - 0.8, hz + 2.4), (hx, hy - 2.4, hz + 6.4), 2.2, "cold", "throat", d=1.2, group="glow")
    teeth(k, part, (hx - 1.4, hy - 0.8, hz + 3.0), (hx - 0.6, hy - 1.0, hz + 8.6), 4, 1.6, down=True, w=0.6, mat="salt")
    teeth(k, part, (hx + 0.6, hy - 1.0, hz + 8.6), (hx + 1.4, hy - 0.8, hz + 3.0), 4, 1.6, down=True, w=0.6, mat="salt")
    teeth(k, part, (hx - 1.0, hy - 3.6, hz + 4.0), (hx + 1.0, hy - 4.2, hz + 7.0), 4, 1.4, down=False, w=0.6, mat="salt")
    for sx in (-1, 1):
        k.box(part, Cc(hx + sx * 2.1, hy + 1.8, hz + 3.6, 0.4, 1.0, 1.4), "ceye", tag="eye")
        k.box(part, Cc(hx + sx * 2.0, hy + 2.6, hz + 3.6, 0.8, 0.6, 2.0), "sea", tag="eye_ridge")
        k.shard(part, (hx + sx * 1.6, hy + 2.6, hz + 0.4), (sx * 0.35, 0.7, -1), 5.0, 1.2, mat="salt", tag="crest")
    k.shard(part, (hx, hy + 3.0, hz + 1.0), (0, 0.9, -1), 6.0, 1.3, mat="salt", tag="crest")
    k.shard(part, (hx, hy + 2.4, hz + 5.2), (0, 1, 0.3), 2.2, 0.9, mat="salt", tag="nose_horn")


def saltglass_hydra():
    k = X.Kit("saltglass_hydra")
    J = {"body": "Root", "head": "Head", "abdomen": "Stomach"}
    body = k.part("body", (0, 14, 2))
    k.blob(body, (0, 15.0, 4.0), (11.0, 7.6, 10.0), "sea", "chest", step=1.0)
    k.blob(body, (0, 11.0, 6.0), (8.0, 4.0, 7.0), "belly", "belly", step=0.8)
    ab = k.part("abdomen", (0, 14, -8), (), "body")
    k.blob(ab, (0, 14.0, -9.0), (10.0, 6.6, 9.0), "sea", "haunch", step=1.0)
    tail = bezier([(0, 13.0, -16.0), (0, 11.0, -26.0), (4.0, 6.0, -32.0), (9.0, 4.0, -38.0)], 7)
    for i, (a, b) in enumerate(zip(tail, tail[1:])):
        k.limb(ab, a, b, 6.4 - i * 0.7, "sea", "tail")
        k.shard(ab, (b[0], b[1] + 3.0 - i * 0.3, b[2]), (0, 1, -0.4), 3.4 - i * 0.3, 1.2, mat="salt", tag="tail_spine")
    k.shard(ab, tail[-1], (0.6, 0.2, -1), 5.0, 2.4, mat="salt", tag="tail_fin")
    # salt glass crusted in clusters along the back and shoulders, barnacles on the flanks
    for at, n, L, w in (((0, 21.6, 4.0), 6, 7.0, 2.2), ((-6.0, 20.0, 8.0), 4, 5.0, 1.8), ((6.0, 20.0, 7.0), 4, 5.4, 1.8),
                        ((-5.0, 20.0, -1.0), 3, 4.0, 1.6), ((5.0, 20.4, 0.0), 3, 4.6, 1.6)):
        k.cluster(body, at, n, L, w, mat="salt", seed=int(at[0] * 3 + at[2]), spread=0.55)
    k.cluster(ab, (0, 19.6, -8.0), 5, 6.0, 2.0, mat="salt", seed=7, spread=0.6)
    k.cluster(ab, (-5.0, 18.0, -12.0), 3, 4.0, 1.6, mat="salt", seed=9, spread=0.5)
    for i in range(10):
        a = i * 2.3
        sx = 1 if i % 2 else -1
        k.blob(body if i < 6 else ab, (sx * 10.2, 13.0 + math.sin(a) * 3.0, 6.0 - i * 2.0), (0.9, 0.9, 0.9), "bone", "barnacle", step=0.4)
    # four splayed legs, webbed feet with glass claws

    def foot(lg, a):
        k.box(lg, Cc(a[0], 0.9, a[2] + 2.2, 5.6, 1.8, 6.4), "sea", tag="foot")
        for t in (-1.8, 0.0, 1.8):
            k.shard(lg, (a[0] + t, 0.8, a[2] + 5.2), (t * 0.15, -0.3, 1), 2.2, 0.8, mat="salt", tag="claw")
    for side, s in ((1, "l"), (-1, "r")):
        lg = leg(k, body, J, "leg_%s0" % s, ("LL" if side > 0 else "RL") + "1", (side * 9.6, 14.0, 7.0), (side * 14.4, 9.0, 9.0),
                 (side * 13.6, 2.0, 10.0), 5.2, 4.0, "sea", foot)
        k.shard(lg, (side * 14.6, 10.0, 7.6), (side * 0.6, 0.3, -1), 3.0, 1.2, mat="salt", tag="elbow_spike")
        leg(k, ab, J, "leg_%s1" % s, ("LL" if side > 0 else "RL") + "4", (side * 8.6, 13.0, -11.0), (side * 13.4, 8.0, -9.0),
            (side * 12.4, 2.0, -11.0), 5.4, 4.0, "sea", foot)
    # three necks: the middle on the head bone (tallest), the side two off the shoulders, leaning out
    hd = k.part("head", (0, 18, 12), (), "body")
    hydra_head(k, hd, (0, 18.0, 11.0), 0.0, 30.0, 12.0)
    hydra_head(k, body, (-5.6, 18.0, 9.0), -11.0, 22.0, 13.0)
    hydra_head(k, body, (5.6, 18.0, 9.0), 11.0, 22.0, 13.0)
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts, J


# ================================================================ the Ironback Scorpion (badlands)

def ironback_scorpion():
    k = X.Kit("ironback_scorpion")
    J = {"body": "Root", "head": "Head", "abdomen": "Stomach"}
    body = k.part("body", (0, 9, 2))
    k.blob(body, (0, 9.0, 3.0), (10.0, 4.6, 9.0), "rust", "thorax", step=0.9)
    ab = k.part("abdomen", (0, 9, -6), (), "body")
    k.blob(ab, (0, 9.4, -10.0), (8.6, 4.4, 7.4), "rust", "abdomen", step=0.9)
    # overlapping iron plates down its back, each riveted, a ridge of spikes down the middle
    for i, z in enumerate((10.0, 5.6, 1.2, -3.2, -7.6, -12.0, -16.0)):
        part = body if i < 3 else ab
        w = 20.0 - i * 1.3
        p = tilt(k, part, (0, 12.6, z), rx=-10)
        k.box(p, Cc(0, 12.8, z, w, 1.8, 5.6), "iron", tag="plate")
        k.box(p, Cc(0, 12.2, z + 2.6, w + 0.4, 1.0, 0.8), "rust", tag="plate_lip")
        k.rivets(p, [(sx * (w * 0.5 - 1.0), 13.8, z + 1.2) for sx in (-1, 1)] + [(sx * w * 0.22, 13.8, z + 1.6) for sx in (-1, 1)], mat="rust", s=0.9)
        k.shard(p, (0, 13.6, z), (0, 1, -0.5), 2.4 - i * 0.12, 1.2, mat="iron", tag="ridge_spike")
    # eight legs, knees high like a spider's, iron-shod tips
    for side, s in ((1, "l"), (-1, "r")):
        for i, z in enumerate((7.0, 2.6, -3.0, -8.4)):
            parent = body if i < 2 else ab
            hip = (side * 8.4, 9.0, z)
            knee = (side * 15.6, 14.0, z + (2.0 - i * 1.4))
            foot_at = (side * 19.0, 0.2, z + (3.0 - i * 2.2))

            def tip(lg, a, side=side):
                k.shard(lg, (a[0], a[1] + 2.6, a[2]), (side * 0.15, -1, 0.1), 3.0, 1.4, mat="iron", tag="foot")
            lg = leg(k, parent, J, "leg_%s%d" % (s, i), ("LL" if side > 0 else "RL") + str(i + 1), hip, knee, foot_at, 2.8, 2.0, "rust", tip)
            k.box(lg, Cc(knee[0], knee[1] + 0.6, knee[2], 3.4, 2.0, 3.4), "iron", tag="knee_plate")
            k.shard(lg, (knee[0], knee[1] + 1.4, knee[2]), (side * 0.3, 1, 0), 2.4, 1.0, mat="iron", tag="knee_spike")
    # the tail: up and over its back in plated segments, a venom bulb veined green, a long curved stinger
    tail = bezier([(0, 11.0, -16.0), (0, 22.0, -26.0), (0, 38.0, -22.0), (0, 40.0, -6.0), (0, 34.0, 2.0)], 7)
    for i, (a, b) in enumerate(zip(tail, tail[1:])):
        w = 5.6 - i * 0.4
        k.limb(ab, a, b, w, "rust", "tail")
        k.blob(ab, b, (w * 0.62, w * 0.62, w * 0.62), "iron", "tail_plate", step=0.6)
        k.shard(ab, b, (0, 1, -0.2) if i < 3 else (0, 0.4, -1), 2.0, 1.0, mat="iron", tag="tail_spike")
    bx, by, bz = tail[-1]
    k.blob(ab, (bx, by - 1.4, bz + 2.0), (3.6, 3.4, 4.0), "rust", "venom_bulb", step=0.6)
    for a, b in (((-2.6, by - 0.4, bz + 1.0), (-1.4, by - 3.0, bz + 4.0)), ((2.6, by - 0.4, bz + 1.0), (1.4, by - 3.0, bz + 4.0)),
                 ((0, by + 1.8, bz + 1.4), (0, by - 0.6, bz + 5.4))):
        k.limb(ab, a, b, 0.6, "green", "venom_vein", group="glow")
    sting = bezier([(0, by - 2.6, bz + 5.0), (0, by - 4.0, bz + 9.0), (0, by - 8.4, bz + 10.0)], 3)
    for i, (a, b) in enumerate(zip(sting, sting[1:])):
        k.limb(ab, a, b, 2.0 - i * 0.5, "iron", "stinger")
    k.shard(ab, sting[-1], (0, -1, -0.3), 2.2, 0.8, mat="green", tag="sting_tip")
    # the head: low and wide under a jagged brow plate, a cluster of green eyes, the mandibles; the great pincers
    hd = k.part("head", (0, 9, 11), (), "body")
    k.blob(hd, (0, 9.0, 12.6), (6.6, 3.6, 4.2), "rust", "head", step=0.7)
    k.box(hd, Cc(0, 12.4, 13.6, 13.0, 1.6, 5.0), "iron", tag="brow_plate")
    for t in (-4.4, -1.5, 1.5, 4.4):
        k.shard(hd, (t, 12.6, 16.0), (t * 0.05, 0.1, 1), 1.8, 1.0, mat="iron", tag="brow_tooth")
    for ex, ey, s in ((-1.2, 11.0, 0.9), (1.2, 11.0, 0.9), (-3.0, 10.4, 0.7), (3.0, 10.4, 0.7), (-0.5, 9.6, 0.5), (0.5, 9.6, 0.5)):
        k.box(hd, Cc(ex, ey, 16.6, s, s, 0.4), "eye", tag="eye")
    for sx in (-1, 1):
        k.shard(hd, (sx * 1.6, 7.4, 15.4), (-sx * 0.5, -0.6, 1), 3.2, 0.9, mat="iron", tag="mandible")
        k.limb(hd, (sx * 5.0, 9.0, 13.0), (sx * 11.6, 10.4, 17.6), 3.6, "rust", "pincer_arm")
        k.box(hd, Cc(sx * 11.6, 10.6, 17.6, 4.0, 3.6, 4.0), "iron", tag="pincer_joint")
        k.limb(hd, (sx * 11.6, 10.4, 17.6), (sx * 12.6, 10.8, 24.0), 3.2, "rust", "pincer_arm")
        k.shard(hd, (sx * 12.0, 12.0, 21.0), (sx * 0.4, 1, 0.1), 2.2, 1.0, mat="iron", tag="pincer_spike")
        k.blob(hd, (sx * 12.8, 11.2, 28.0), (4.8, 4.0, 5.2), "iron", "pincer_palm", step=0.6)
        k.blob(hd, (sx * 12.8, 11.4, 28.0), (5.2, 2.0, 4.2), "rust", "pincer_band", step=0.6)
        k.shard(hd, (sx * 13.6, 12.0, 31.6), (-sx * 0.22, 0.05, 1), 9.0, 3.2, mat="iron", tag="pincer_finger")
        k.shard(hd, (sx * 11.0, 10.0, 31.6), (sx * 0.24, -0.05, 1), 7.4, 2.4, mat="rust", tag="pincer_thumb")
        for t in (1.6, 3.4, 5.2):
            k.shard(hd, (sx * (13.4 - t * 0.22), 11.6, 31.6 + t), (-sx, 0, 0.3), 1.4, 0.6, mat="bone", tag="pincer_tooth")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts, J


# ================================================================ the Rime Lich (snow)

def rime_lich():
    k = X.Kit("rime_lich")
    hips = k.part("hips", (0, 24, 0))
    # the robe: a long flared bell to the ground, its hem in rags, icicles hanging off it
    k.stack(hips, 0, -0.4, [(0.8, 18.0, 14.0), (6.0, 15.6, 12.0), (14.0, 12.6, 9.6), (25.0, 10.4, 7.6)], "robe", "robe", step=1.0)
    for i in range(16):
        a = i / 16 * 2 * math.pi
        x, z = math.sin(a) * 8.6, math.cos(a) * 6.6 - 0.4
        L = 3.0 + 3.0 * X.h3(i, 5, 3)
        k.limb(hips, (x, 5.0, z), (x * 1.08, max(0.4, 5.0 - L), z * 1.08), 2.6, "robe", "hem_rag", d=0.6)
        if i % 2:
            k.shard(hips, (x * 0.9, 6.4, z * 0.9 + (0.6 if z > 0 else -0.6)), (0, -1, 0), 3.4, 0.9, mat="ice", tag="icicle")
    for sx in (-1, 1):                               # frost riming the robe in streaks
        k.limb(hips, (sx * 3.0, 22.0, 4.2), (sx * 5.6, 3.0, 7.2), 1.2, "frost", "rime_streak", d=0.6)
    # legs (hidden under the robe; the rig wants them)
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 3.0
        th = k.part("thigh_" + nm, (x, 22, 0), (), hips)
        sh = k.part("shin_" + nm, (x, 11, 0), (), th)
        ft = k.part("foot_" + nm, (x, 2.4, 0), (), sh)
        k.limb(th, (x, 22.0, 0), (x, 11.0, 0), 2.2, "robe", "thigh")
        k.limb(sh, (x, 11.0, 0), (x, 2.0, 0), 2.0, "robe", "shin")
        k.box(ft, Cc(x, 1.0, 1.0, 2.6, 2.0, 4.0), "robe", tag="foot")
    # the body: gaunt, the robe open on a ribcage and the cold heart caged in it
    to = k.part("torso", (0, 25, 0), (("x", 6),), "hips")
    k.stack(to, 0, -0.4, [(24.0, 9.0, 6.6), (30.0, 10.0, 7.0), (36.0, 13.6, 7.8), (40.4, 12.0, 7.0)], "robe", "chest", step=1.0)
    k.box(to, Cc(0, 33.0, 3.4, 6.0, 10.0, 1.0), "dark", tag="rib_cavity")
    k.blob(to, (0, 33.4, 3.6), (1.8, 2.0, 1.2), "cold", "heart", step=0.5)
    k.limb(to, (0, 28.0, 4.0), (0, 38.6, 3.6), 1.0, "bone", "sternum")
    for y in (29.6, 32.0, 34.4, 36.8):
        for sx in (-1, 1):
            k.limb(to, (0, y + 0.4, 4.0), (sx * 3.4, y - 0.4, 3.8), 0.8, "bone", "rib")
    for sx in (-1, 1):                               # the robe's lapels, frost-edged
        k.limb(to, (sx * 3.8, 40.0, 3.8), (sx * 3.2, 26.0, 4.0), 1.6, "frost", "lapel", d=0.8)
    # frozen pauldrons spiked with ice, and a fan of ice behind its head like a collar
    for sx in (-1, 1):
        k.blob(to, (sx * 8.4, 40.0, 0), (4.4, 3.0, 4.8), "frost", "pauldron", step=0.6)
        k.cluster(to, (sx * 9.4, 41.6, -0.4), 4, 7.0, 1.8, mat="ice", seed=3 + sx, spread=0.5, up=(sx * 0.6, 1, -0.2))
    for i in range(9):
        a = math.radians(-70 + i * 17.5)
        L = 9.0 + 4.0 * math.cos(a) + 1.6 * X.h3(i, 2, 2)
        k.shard(to, (math.sin(a) * 3.6, 41.0, -2.6), (math.sin(a) * 0.8, 1, -0.35), L, 1.4, mat="ice", tag="ice_collar")
    for i in range(10):                              # the cape behind, in rags
        x = -8.0 + i * 1.8
        L = 32.0 + 4.0 * X.h3(i, 9, 4)
        k.limb(to, (x * 0.9, 40.0, -3.8), (x * 1.3, max(0.6, 40.0 - L), -7.6 - (i % 2)), 2.2, "robe", "cape", d=0.7)
    # the head: a skull deep in a ragged hood, cold eyes, a jagged crown of icicles through the hood
    hd = k.part("head", (0, 41, 0.6), (("x", -6),), "torso")
    k.limb(hd, (0, 40.4, 0.4), (0, 43.0, 0.8), 1.4, "bone", "neck")
    k.blob(hd, (0, 46.0, 1.0), (3.0, 3.4, 3.2), "bone", "cranium", step=0.6)
    k.box(hd, Cc(0, 46.8, 3.9, 5.4, 1.2, 1.0), "bone", tag="brow")
    for sx in (-1, 1):
        k.box(hd, Cc(sx * 1.3, 45.6, 3.9, 1.6, 1.6, 0.8), "dark", tag="socket")
        k.box(hd, Cc(sx * 1.3, 45.6, 4.2, 0.8, 0.7, 0.4), "ceye", tag="eye")
        k.box(hd, Cc(sx * 2.2, 44.4, 3.4, 1.0, 1.0, 1.4), "bone", tag="cheekbone")
    k.box(hd, Cc(0, 44.4, 4.0, 0.8, 1.0, 0.6), "dark", tag="nose_hole")
    k.box(hd, Cc(0, 42.6, 2.6, 3.4, 1.6, 2.6), "bone", tag="jaw")
    teeth(k, hd, (-1.2, 43.4, 3.9), (1.2, 43.4, 3.9), 5, 0.9, down=True, w=0.45)
    k.box(hd, Cc(0, 46.4, -1.8, 9.0, 10.0, 2.4), "robe", tag="hood")
    for sx in (-1, 1):
        k.box(hd, Cc(sx * 4.0, 45.8, 1.2, 1.2, 9.4, 6.4), "robe", tag="hood")
        k.limb(hd, (sx * 4.0, 41.2, 4.2), (sx * 4.6, 37.4, 4.6), 1.2, "robe", "hood_rag", d=0.6)
    k.box(hd, Cc(0, 50.8, 0.6, 9.0, 1.6, 7.4), "robe", tag="hood")
    k.box(hd, Cc(0, 51.8, 0.6, 7.6, 0.8, 6.0), "frost", tag="crown_band")
    for i in range(11):
        a = (i / 11) * 2 * math.pi
        L = 4.0 + (5.0 if i in (0, 3, 8) else 2.0 * X.h3(i, 4, 4))
        k.shard(hd, (math.sin(a) * 3.0, 52.0, math.cos(a) * 2.6 + 0.6), (math.sin(a) * 0.25, 1, math.cos(a) * 0.25), L, 1.1, mat="ice", tag="crown")
    # arms: bell sleeves, long bone fingers; the left hand raised with cold light between its fingers
    rots = {1: ((("x", -58), ("z", 24)), (("x", -52),)), -1: ((("x", -40), ("z", -8)), (("x", -30),))}
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 8.6
        ar, fr = rots[side]
        a = k.part("arm_" + nm, (x, 39, 0), ar, to)
        f = k.part("fore_" + nm, (x + side * 0.4, 30, 0.6), fr, a)
        h = k.part("hand_" + nm, (x + side * 0.6, 21.6, 1.0), (), f)
        k.limb(a, (x, 39.4, 0), (x + side * 0.4, 30.0, 0.6), 3.2, "robe", "upper_arm")
        k.stack(f, x + side * 0.5, 0.8, [(22.6, 6.4, 6.4), (26.0, 4.8, 4.8), (30.4, 3.6, 3.6)], "robe", "sleeve", step=0.8)
        k.box(f, Cc(x + side * 0.5, 22.9, 0.8, 6.8, 0.8, 6.8), "frost", tag="cuff")
        k.box(h, Cc(x + side * 0.6, 20.8, 1.0, 1.8, 2.0, 1.4), "bone", tag="hand")
        for t in (-0.7, -0.2, 0.3, 0.8):
            k.limb(h, (x + side * 0.6 + t, 20.0, 1.0 + t * 0.3), (x + side * 0.6 + t * 1.8, 16.0, 1.6 + t * 0.4), 0.45, "bone", "finger")
        if side > 0:
            k.blob(h, (x + 0.6, 17.4, 1.4), (1.4, 1.4, 1.4), "cold", "cast_light", step=0.4)
    # the staff: twisted ice and bone, a caged phylactery in a bloom of ice at its head
    st = held(k, "staff", "r", (-9.2, 20.0, 1.0), (("x", 64),))
    hx, hy, hz = -9.2, 20.0, 1.0
    shaft = [(hx + 0.4 * math.sin(i * 1.3), hy - 14.0 + i * 4.6, hz + 0.4 * math.cos(i * 1.3)) for i in range(12)]
    for i, (p, q) in enumerate(zip(shaft, shaft[1:])):
        k.limb(st, p, q, 1.2, "bone" if i % 3 else "frost", "staff")
    top = shaft[-1]
    cx, cy, cz = top[0], top[1] + 4.0, top[2]
    for i in range(5):
        a = i * 2 * math.pi / 5
        k.limb(st, top, (cx + math.cos(a) * 2.8, cy, cz + math.sin(a) * 2.8), 0.6, "frost", "cage")
        k.limb(st, (cx + math.cos(a) * 2.8, cy, cz + math.sin(a) * 2.8), (cx, cy + 4.2, cz), 0.6, "frost", "cage")
        k.shard(st, (cx + math.cos(a) * 2.6, cy - 0.4, cz + math.sin(a) * 2.6), (math.cos(a) * 0.6, 1, math.sin(a) * 0.6), 5.0, 1.0, mat="ice", tag="staff_bloom")
    k.blob(st, (cx, cy, cz), (1.8, 2.4, 1.8), "cold", "phylactery", step=0.5)
    k.shard(st, (cx, cy + 4.0, cz), (0, 1, 0), 4.0, 1.0, mat="ice", tag="staff_tip")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.1)
    return k.s, k.parts


MOBS = {
    "cairn_giant": dict(make=cairn_giant, ent=(3.4, 9.0), boss=True, stats=dict(hp=1400, speed=0.2, dmg=26, armor=18, kb=1.0)),
    "hart_lord": dict(make=hart_lord, ent=(2.0, 8.0), boss=True, stats=dict(hp=1100, speed=0.3, dmg=22, armor=10, kb=0.8)),
    "saltglass_hydra": dict(make=saltglass_hydra, rig="crawler", ent=(4.5, 7.0), boss=True, stats=dict(hp=1300, speed=0.24, dmg=22, armor=12, kb=1.0)),
    "ironback_scorpion": dict(make=ironback_scorpion, rig="crawler", ent=(4.5, 4.4), boss=True, stats=dict(hp=1300, speed=0.27, dmg=24, armor=20, kb=1.0)),
    "rime_lich": dict(make=rime_lich, ent=(2.0, 7.4), boss=True, stats=dict(hp=1000, speed=0.22, dmg=22, armor=10, kb=0.6)),
}
