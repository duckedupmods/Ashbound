"""The Broodmothers' hive: insects grown to the size of men under the old nests, who hold the world's spider pits,
amethyst nests, mechanical nests and infested temples, built by hand (tools/vox2.py). Glossy blue-black chitin
with an oil-sheen, amber plates, pale membrane wings, bristles, and the hot orange glow of the brood they carry -
in their sacs, their eyes, their spit. (Not the Silk Archive's spiders: this is a hive of ants and mantids and
beetles.)

    brood_mite       swarm   an ant the size of a hound, mandibles like shears, a glowing gaster
    hive_soldier     guard   an ant that walks on two legs, its great flat head a shield, four arms, a chitin spear
    hive_juggernaut  brute   a rhinoceros beetle risen upright, a horn like a lance, armoured like a siege tower
    spitter          caster  thin legs under a swollen glowing sac, a head that spits the brood's acid
    mantis_reaper    skirm   a mantis taller than a man, scythe-arms folded to strike, wings half-raised
    brood_queen      elite   the queen: an ant crowned with a crest of horns, wings like stained glass, dragging an
                             egg-sac that glows like a furnace

    python tools/monsterforge.py broodmothers --preview ; python tools/mobsheet.py broodmothers
"""
import math

import vox2 as X
from vox2 import C, ramp
from serpent_ziggurat import grow
from _folk import lit, eyes, legs, arms, held, quad, wing

CHITIN = ramp("#04040a", "#0a0a16", "#121424", "#1c1e36", "#282a4a", "#363a60")
AMBER = ramp("#1a0a02", "#301404", "#4a2008", "#68300c", "#884214", "#a8561e")
MEMBR = ramp("#4a4a46", "#6a6a64", "#8a8a82", "#aaaaa0", "#cac8bc")
BRISTLE = ramp("#0a0806", "#14100c", "#1e1812", "#282018")
SAC = ramp("#5a1a02", "#8a2c04", "#c04a0a", "#f07818", "#ffaa40", "#ffe0a0")
GREEN = ramp("#0a1408", "#122010", "#1a2e16", "#24401e", "#30542a")


def shaders():
    sheen = lambda p, n, i, j, w, h: 0.22 if (i + j) % 7 == 0 else (0.1 if (i * 2 + j) % 11 == 0 else 0.0)
    return {
        "chitin": X.surf(CHITIN, 0.56, 1.7, 0.08, 0.34, pattern=sheen),
        "amber": X.surf(AMBER, 0.56, 1.6, 0.1, 0.3, pattern=sheen),
        "membrane": X.surf(MEMBR, 0.6, 1.2, 0.1, 0.0, pattern=lambda p, n, i, j, w, h: -0.3 if (i % 5 == 0 or j % 6 == 0) else 0.04),
        "bristle": X.surf(BRISTLE, 0.5, 1.0, 0.3, 0.0, stripe=2),
        "mantis": X.surf(GREEN, 0.56, 1.5, 0.12, 0.24, pattern=sheen),
        "sac": X.glow(SAC),
        "eye": X.glow(SAC, 0.86, 0.12),
        "dark": X.dark(CHITIN),
    }


GLOWS = {"sac", "eye"}


def mandibles(k, part, base, s=1.0, mat="amber"):
    bx, by, bz = base
    for sx in (-1, 1):
        k.limb(part, (bx + sx * 1.4 * s, by, bz), (bx + sx * 3.4 * s, by - 0.4 * s, bz + 3.0 * s), 1.4 * s, mat, "mandible")
        k.limb(part, (bx + sx * 3.4 * s, by - 0.4 * s, bz + 3.0 * s), (bx + sx * 0.8 * s, by - 0.8 * s, bz + 5.2 * s), 1.1 * s, mat, "mandible")
        for t in (0.3, 0.6):
            k.shard(part, (bx + sx * (3.4 - 2.6 * t) * s, by - (0.4 + 0.4 * t) * s, bz + (3.0 + 2.2 * t) * s), (-sx, 0, 0.2), 0.9 * s, 0.4, mat="chitin", tag="mandible_tooth")


def compound_eyes(k, part, c, gap, r, axis="x"):
    cx, cy, cz = c
    for sx in (-1, 1):
        k.blob(part, (cx + sx * gap, cy, cz), (r * 0.7, r, r), "eye", "compound_eye", step=0.5)


def antennae(k, part, base, L, s=1.0):
    bx, by, bz = base
    for sx in (-1, 1):
        mid = (bx + sx * 1.6 * s, by + L * 0.5, bz + 0.6 * s)
        k.limb(part, (bx + sx * 0.8 * s, by, bz), mid, 0.5, "chitin", "antenna")
        k.limb(part, mid, (bx + sx * 3.6 * s, by + L * 0.7, bz + L * 0.5), 0.4, "chitin", "antenna")


def insect_legs(k, part, at, side, n, L, mat="chitin", spread=4.0):
    """extra jointed legs off a body (the rig's own legs carry it; these are the rest of them)"""
    x, y, z = at
    for i in range(n):
        zz = z + (i - (n - 1) / 2) * spread
        kn = (x + side * L * 0.6, y + L * 0.3, zz + 0.4)
        k.limb(part, (x, y, zz), kn, 1.2, mat, "insect_leg")
        k.limb(part, kn, (x + side * L * 0.9, 0.6, zz + 1.0), 0.9, mat, "insect_leg")


# ================================================================ the Brood Mite (swarm)

def brood_mite():
    """The hive's workers come out of every crack at once: ants the size of hounds, glossy blue-black, jaws like
    shears, the gaster behind swollen with the brood and glowing through the plates."""
    k = X.Kit("brood_mite")
    body, hd, ab, joints = quad(k, "chitin", y=8, chest=((4, 7, 8), (7, 8, 9), (9.6, 6.6, 7)), haunch=((4, 6, 6), (6.4, 6.4, 6.4), (8, 5.4, 5.4)),
                                leg_w=1.4, foot_w=1.0, front_z=4, back_z=-5, x=4.0, head_at=(0, 8, 8), head_rot=4, claw="chitin", foot_len=2.6,
                                knees=(1.0, -1.0))
    insect_legs(k, body, (3.6, 7.0, 0.6), 1, 1, 7.0)
    insect_legs(k, body, (-3.6, 7.0, 0.6), -1, 1, 7.0)
    k.blob(ab, (0, 10.0, -11.0), (4.4, 4.0, 5.6), "chitin", "gaster", step=0.7)
    for i, z in enumerate((-8.0, -10.6, -13.2)):
        k.box(ab, C(0, 6.6 + i * 0.2, z, 7.0 - i * 0.6, 7.0 - i * 0.6, 0.6), "sac", tag="gaster_glow")
    k.shard(ab, (0, 9.0, -16.4), (0, -0.2, -1), 2.4, 1.0, mat="amber", tag="stinger")
    k.box(hd, C(0, 6.0, 11.0, 6.4, 5.4, 5.4), "chitin", tag="head")
    compound_eyes(k, hd, (0, 9.4, 12.6), 2.8, 1.4)
    mandibles(k, hd, (0, 7.0, 13.6), 1.0)
    antennae(k, hd, (0, 11.4, 12.4), 6.0)
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


# ================================================================ the Hive Soldier (guard)

def hive_soldier():
    """The hive's soldiers stand up to fight. An ant as tall as a man on its two hind legs, its head grown into a
    great flat plate that blocks a doorway, mandibles under it, four arms - two to hold the spear of chitin, two
    smaller ones clasped to its chest - amber plates over the joints."""
    k = X.Kit("hive_soldier")
    hips = k.part("hips", (0, 18, 0))
    k.blob(hips, (0, 16.0, -5.0), (5.4, 5.0, 6.4), "chitin", "gaster", step=0.8)       # the abdomen behind, hanging
    k.box(hips, C(0, 12.6, -8.0, 7.0, 0.6, 7.0), "sac", tag="gaster_glow")
    k.box(hips, C(0, 15.4, 0, 7.0, 4.0, 5.0), "amber", tag="petiole")
    legs(k, hips, 17, 9.0, 3.2, "chitin", "chitin", knee_mat="amber", lean=-14, bend=28, w=3.6, cuff=False)
    for side in (1, -1):
        nm = "foot_" + ("l" if side > 0 else "r")
        for t in (-0.9, 0.9):
            k.shard(k.parts[nm], (side * 3.2 + t, 0.6, 4.0), (t * 0.3, -0.4, 1), 2.4, 0.7, mat="chitin", tag="foot")
    to = k.part("torso", (0, 18, 0), (("x", 10),), "hips")
    k.stack(to, 0, 0, [(18, 7.0, 5.6), (22, 8.6, 6.4), (27, 11.0, 7.4), (30.6, 10.0, 6.8)], "chitin", "thorax")
    for y in (21.0, 25.0):
        k.box(to, C(0, y, 3.4, 8.0, 2.0, 0.6), "amber", tag="thorax_plate")
    for sx in (-1, 1):                            # the small arms, clasped to the chest
        k.limb(to, (sx * 4.2, 24.0, 2.4), (sx * 3.4, 21.0, 5.6), 1.4, "chitin", "small_arm")
        k.limb(to, (sx * 3.4, 21.0, 5.6), (sx * 0.8, 23.0, 6.2), 1.2, "chitin", "small_arm")
    hd = k.part("head", (0, 30.4, 1.0), (("x", -10),), "torso")
    # the shield-head: a broad flat plate, rim raised, the eyes at its edge, the mandibles under it
    k.blob(hd, (0, 35.4, 3.0), (6.6, 6.0, 2.4), "chitin", "shield_head", step=0.6)
    k.blob(hd, (0, 35.4, 4.6), (5.4, 4.8, 1.0), "amber", "head_plate", step=0.6)
    k.box(hd, C(0, 33.0, 5.4, 1.2, 6.0, 0.6), "chitin", tag="head_ridge")
    for sx in (-1, 1):
        k.blob(hd, (sx * 6.0, 38.6, 3.4), (1.2, 1.6, 1.6), "eye", "compound_eye", step=0.5)
    for i in range(5):
        k.shard(hd, (-4.4 + i * 2.2, 41.0, 3.2), (0, 1, 0.2), 2.0, 1.0, mat="amber", tag="head_spike")
    mandibles(k, hd, (0, 30.6, 4.2), 1.3)
    antennae(k, hd, (0, 40.6, 2.4), 8.0)
    arms(k, to, 6.2, 29, "chitin", {1: ((("x", -40), ("z", -10)), (("x", -40),)), -1: ((("x", -40), ("z", 10)), (("x", -44),))}, glove="chitin", w=2.6)
    for side in (1, -1):
        k.box(k.parts["fore_" + ("l" if side > 0 else "r")], C(side * 6.2, 17.6, 0, 3.2, 3.0, 3.2), "amber", tag="elbow_plate")
    sp = held(k, "chitin_spear", "r", (-6.2, 12.4, 0.3), (("x", 96), ("z", -6)))
    k.limb(sp, (-6.2, -8.0, 0.3), (-6.2, 26.0, 0.3), 1.4, "amber", "spear_shaft")
    for y in (-2.0, 6.0, 14.0, 22.0):
        k.box(sp, C(-6.2, y, 0.3, 2.0, 1.0, 2.0), "chitin", tag="shaft_segment")
    k.shard(sp, (-6.2, 26.0, 0.3), (0, 1, 0), 8.4, 2.4, mat="chitin", tag="spear_point")
    for sz in (-1, 1):
        k.shard(sp, (-6.2, 27.4, 0.3 + sz * 0.8), (0, -0.6, sz), 2.4, 0.8, mat="chitin", tag="barb")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Hive Juggernaut (brute)

def hive_juggernaut():
    """The hive breaks walls with these: a rhinoceros beetle risen onto its hind legs and grown to twice a man's
    height, plated like a siege tower in blue-black and amber, a horn curving up off its head like a lance, a second
    horn off its back meeting it, and forelimbs thick as tree trunks ending in toothed clubs."""
    k = X.Kit("hive_juggernaut")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(12, 15, 12), (20, 16, 12.6)], "chitin", "abdomen_base")
    k.blob(hips, (0, 18.0, -6.4), (8.0, 7.0, 7.0), "chitin", "abdomen", step=0.9)
    for y in (13.0, 17.0, 21.0):
        k.box(hips, C(0, y, -12.0, 12.0 - abs(y - 17) * 0.6, 1.0, 1.2), "amber", tag="segment_line")
    legs(k, hips, 19, 10.4, 5.4, "chitin", "chitin", knee_mat="amber", lean=-8, bend=14, w=6.4, cuff=False)
    insect_legs(k, hips, (6.0, 15.0, -2.0), 1, 1, 10.0)
    insect_legs(k, hips, (-6.0, 15.0, -2.0), -1, 1, 10.0)
    to = k.part("torso", (0, 20, 0), (("x", 12),), "hips")
    k.stack(to, 0, 0, [(20, 16, 12.6), (26, 20, 14), (31, 24, 15), (35, 22, 14), (37.6, 16, 11)], "chitin", "pronotum")
    for y in (23.0, 28.0, 33.0):
        k.box(to, C(0, y, 7.0 + (y - 23) * 0.04, 14.0, 3.0, 0.8), "amber", tag="plate")
    pts = [(0, 36.0, -4.0), (0, 42.0, -2.0), (0, 46.0, 2.6)]            # the back horn, curving forward over the head
    for (a, b), w in zip(zip(pts, pts[1:]), (5.0, 3.4)):
        k.limb(to, a, b, w, "chitin", "back_horn")
    k.shard(to, pts[-1], (0, -0.2, 1), 3.4, 2.4, mat="amber", tag="back_horn_tip")
    hd = k.part("head", (0, 36.0, 4.0), (("x", -16),), "torso")
    k.box(hd, C(0, 33.0, 7.4, 9.0, 7.0, 7.4), "chitin", tag="head")
    for sx in (-1, 1):
        k.blob(hd, (sx * 4.4, 36.4, 9.6), (1.0, 1.4, 1.4), "eye", "compound_eye", step=0.5)
    pts = [(0, 34.0, 11.0), (0, 38.0, 16.0), (0, 44.0, 18.0), (0, 49.0, 16.6)]   # the great horn
    for (a, b), w in zip(zip(pts, pts[1:]), (4.6, 3.6, 2.6)):
        k.limb(hd, a, b, w, "chitin", "great_horn")
    k.shard(hd, pts[-1], (0, 1, -0.4), 3.4, 2.0, mat="amber", tag="horn_tip")
    for y in (36.0, 40.0):
        k.box(hd, C(0, y, 16.4, 3.4, 1.0, 1.2), "amber", tag="horn_ring")
    mandibles(k, hd, (0, 33.4, 10.6), 1.4)
    arms(k, to, 13.0, 34, "chitin", {1: ((("x", -40), ("z", -16)), (("x", -40),)), -1: ((("x", -56), ("z", 16)), (("x", -30),))}, w=6.4, long=1.15)
    for side in (1, -1):
        nm = "l" if side > 0 else "r"
        k.box(k.parts["fore_" + nm], C(side * 13.0, 22.0, 0, 7.4, 3.4, 7.4), "amber", tag="fore_plate")
        for b in list(k.s.boxes):
            if b.part is k.parts["hand_" + nm]:
                k.s.boxes.remove(b)
        y = 34 - 8 * 1.15 - 7.6 * 1.15
        k.blob(k.parts["hand_" + nm], (side * 13.0, y - 3.6, 0.4), (4.6, 4.6, 4.6), "chitin", "club", step=0.8)
        for i in range(6):
            a = i * math.pi / 3
            k.shard(k.parts["hand_" + nm], (side * 13.0 + math.cos(a) * 3.6, y - 5.0, 0.4 + math.sin(a) * 3.6), (math.cos(a) * 0.6, -0.6, math.sin(a) * 0.6), 2.4, 1.2, mat="amber", tag="club_tooth")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.3)
    return k.s, k.parts


# ================================================================ the Spitter (caster)

def spitter():
    """The hive's artillery: an ant whose abdomen has swollen into a sac bigger than the rest of it, the brood's acid
    glowing through the stretched skin, carried up over its back on thin legs, its head on a long neck that rears
    back and spits."""
    k = X.Kit("spitter")
    hips = k.part("hips", (0, 19, 0))
    k.box(hips, C(0, 16.0, 0, 6.0, 4.0, 5.0), "amber", tag="petiole")
    # the sac, enormous, over and behind it
    k.blob(hips, (0, 27.0, -7.0), (8.0, 9.0, 8.6), "sac", "acid_sac", step=0.9)
    for i in range(8):                            # the plates stretched apart over it
        a = i * 2 * math.pi / 8
        k.box(hips, C(math.cos(a) * 7.0, 26.0 + math.sin(a) * 6.0, -7.0 + math.sin(a * 2) * 2.0, 3.0, 2.4, 4.0), "chitin", tag="stretched_plate")
    k.blob(hips, (0, 20.0, -3.0), (4.4, 3.4, 4.0), "chitin", "sac_root", step=0.7)
    legs(k, hips, 18, 9.6, 3.0, "chitin", "chitin", knee_mat="amber", lean=-16, bend=30, w=2.8, cuff=False)
    insect_legs(k, hips, (3.0, 17.0, -1.0), 1, 1, 8.0)
    insect_legs(k, hips, (-3.0, 17.0, -1.0), -1, 1, 8.0)
    to = k.part("torso", (0, 19, 0), (("x", 30),), "hips")
    k.stack(to, 0, 0, [(19, 6.0, 5.0), (23, 7.0, 5.6), (27, 8.0, 6.0), (29, 6.4, 5.0)], "chitin", "thorax")
    k.box(to, C(0, 22.0, 2.8, 6.4, 4.0, 0.6), "amber", tag="thorax_plate")
    hd = k.part("head", (0, 29, 1.0), (("x", -50),), "torso")
    k.limb(hd, (0, 29.0, 1.0), (0, 34.0, 3.0), 2.6, "chitin", "neck")
    k.box(hd, C(0, 33.4, 4.4, 5.4, 5.0, 5.4), "chitin", tag="head")
    compound_eyes(k, hd, (0, 36.6, 5.4), 2.4, 1.2)
    k.box(hd, C(0, 33.0, 7.15, 2.6, 2.0, 0.3), "sac", tag="spit_glow")
    k.shard(hd, (0, 34.0, 7.0), (0, -0.2, 1), 2.4, 2.6, mat="amber", tag="spit_snout")
    antennae(k, hd, (0, 38.4, 4.4), 6.0, 0.8)
    arms(k, to, 4.4, 27, "chitin", {1: ((("x", -60), ("z", -10)), (("x", -40),)), -1: ((("x", -60), ("z", 10)), (("x", -40),))}, glove="chitin", w=1.8, long=0.9)
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Mantis Reaper (skirmisher)

def mantis_reaper():
    """The mantids hunt for the hive: taller than a man, the long green-black body swaying, a triangle head that
    turns all the way round, two great eyes with the brood's light in them, and the forelimbs folded like a priest
    at prayer - until they open, and they are scythes, serrated, as long as the mantis's own body."""
    k = X.Kit("mantis_reaper")
    hips = k.part("hips", (0, 20, 0))
    k.box(hips, C(0, 17.4, 0, 5.0, 4.0, 4.4), "mantis", tag="waist")
    k.blob(hips, (0, 18.6, -8.0), (3.6, 3.4, 8.4), "mantis", "abdomen", step=0.8)
    for z in (-4.0, -8.0, -12.0):
        k.box(hips, C(0, 21.4, z, 6.0, 0.6, 1.0), "chitin", tag="segment")
    legs(k, hips, 19, 10.4, 3.0, "mantis", "mantis", knee_mat="chitin", lean=-12, bend=26, w=2.6, cuff=False)
    insect_legs(k, hips, (2.6, 17.0, -4.0), 1, 1, 9.0, mat="mantis")
    insect_legs(k, hips, (-2.6, 17.0, -4.0), -1, 1, 9.0, mat="mantis")
    to = k.part("torso", (0, 20, 0), (("x", 16),), "hips")
    k.stack(to, 0, 0, [(20, 5.0, 4.4), (26, 4.4, 4.0), (32, 5.6, 4.6), (35, 4.4, 4.0)], "mantis", "prothorax")
    for side in (1, -1):                          # wings half raised off its back
        wing(k, to, (side * 2.0, 32.0, -2.4), side, 11.0, "mantis", membrane="membrane", ribs=3, up=0.7, back=0.8, drop=12.0, feather=False)
    hd = k.part("head", (0, 35, 0.6), (("x", -10),), "torso")
    # the triangle head: wide at the eyes, narrowing to the mouth
    k.box(hd, C(0, 37.4, 1.0, 7.4, 2.4, 3.4), "mantis", tag="head_top")
    k.box(hd, C(0, 35.4, 1.4, 4.4, 2.2, 3.0), "mantis", tag="head_mid")
    k.box(hd, C(0, 34.0, 1.8, 2.0, 1.6, 2.6), "mantis", tag="mouth")
    for sx in (-1, 1):
        k.blob(hd, (sx * 4.0, 38.4, 1.2), (1.4, 1.8, 1.8), "eye", "compound_eye", step=0.5)
    antennae(k, hd, (0, 39.6, 1.4), 7.0, 0.8)
    arms(k, to, 4.0, 33, "mantis", {1: ((("x", -80), ("z", -10)), (("x", 140),)), -1: ((("x", -70), ("z", 10)), (("x", 130),))}, glove="mantis", w=2.4, long=1.2)
    for side, nm in ((1, "l"), (-1, "r")):        # the scythes along the folded forearms
        x = side * 4.0
        f = k.parts["fore_" + nm]
        y0 = 33 - 8 * 1.2
        k.box(f, C(x, y0 - 9.0, -1.4, 1.2, 9.4, 1.2), "chitin", tag="scythe_spine")
        for i in range(6):
            k.shard(f, (x, y0 - 1.6 - i * 1.4, -2.0), (0, -0.2, -1), 1.6, 0.6, mat="amber", tag="scythe_tooth")
        k.limb(k.parts["hand_" + nm], (x, y0 - 7.6 * 1.2, 0), (x, y0 - 7.6 * 1.2 - 6.0, -3.0), 1.2, "chitin", "scythe_hook", d=2.4)
        k.shard(k.parts["hand_" + nm], (x, y0 - 7.6 * 1.2 - 6.0, -3.0), (0, -0.4, -1), 2.4, 1.0, mat="chitin", tag="hook_point")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Brood Queen (elite)

def brood_queen():
    """The queen lies in the heart of the nest and comes out only when it burns. An ant as long as a cart, blue-
    black and amber, a crest of horns round her head like a crown, wings like panes of stained glass she no longer
    flies with, and behind her the egg-sac, vast, its skin stretched so thin over the brood it glows like a forge."""
    k = X.Kit("brood_queen")
    body, hd, ab, joints = quad(k, "chitin", y=14, chest=((7, 12, 14), (12, 15, 16), (18, 13, 14)), haunch=((7, 10, 10), (12, 11, 11), (16, 10, 10)),
                                leg_w=2.6, foot_w=2.0, front_z=6, back_z=-8, x=6.4, head_at=(0, 16, 10), head_rot=-6, claw="chitin", foot_len=4.0)
    insect_legs(k, body, (6.0, 12.0, 0.0), 1, 1, 12.0)
    insect_legs(k, body, (-6.0, 12.0, 0.0), -1, 1, 12.0)
    for y in (12.0, 16.0):
        k.box(body, C(0, y, 8.0, 12.0, 2.0, 0.6), "amber", tag="thorax_plate")
    # the egg-sac: vast, glowing, plates stretched apart over it
    k.blob(ab, (0, 14.0, -22.0), (11.0, 10.0, 14.0), "sac", "egg_sac", step=1.0)
    for i in range(12):
        a = i * 2.399
        k.box(ab, C(math.cos(a) * 9.6, 14.0 + math.sin(a) * 7.0, -22.0 + math.cos(a * 1.7) * 9.0, 3.6, 2.6, 4.4), "amber", tag="stretched_plate")
    for z in (-12.0, -20.0, -28.0):
        k.ring(ab, 0, 14.0, z, 10.6 - abs(z + 20) * 0.2, 1.0, "chitin", "sac_band", n=16, axis="z")
    for side in (1, -1):                          # the stained-glass wings, laid back over the sac
        wing(k, body, (side * 3.0, 20.0, -2.0), side, 16.0, "chitin", membrane="membrane", ribs=4, up=0.25, back=1.4, drop=8.0, feather=False)
    k.box(hd, C(0, 12.0, 14.6, 9.0, 8.0, 8.0), "chitin", tag="head")
    compound_eyes(k, hd, (0, 17.4, 16.6), 4.0, 2.0)
    mandibles(k, hd, (0, 13.4, 18.4), 1.4)
    antennae(k, hd, (0, 20.0, 15.4), 10.0, 1.2)
    for i in range(9):                            # the crest of horns, a crown
        a = math.radians(-80 + i * 20)
        k.shard(hd, (math.sin(a) * 4.6, 20.0, 14.6 + math.cos(a) * 3.4), (math.sin(a) * 0.4, 1, -0.3), 3.4 + (4 - abs(i - 4)) * 0.9, 1.2, mat="amber", tag="crown_horn")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


MOBS = {
    "brood_mite": dict(make=brood_mite, rig="crawler", ent=(1.0, 0.9), stats=dict(hp=22, speed=0.36, dmg=6, armor=4, kb=0)),
    "hive_soldier": dict(make=hive_soldier, ent=(0.9, 2.8), stats=dict(hp=60, speed=0.25, dmg=10, armor=10, kb=0.3)),
    "hive_juggernaut": dict(make=hive_juggernaut, ent=(1.9, 4.2), stats=dict(hp=220, speed=0.18, dmg=19, armor=14, kb=1.0)),
    "spitter": dict(make=spitter, ent=(1.0, 2.6), stats=dict(hp=36, speed=0.23, dmg=8, armor=3, kb=0)),
    "mantis_reaper": dict(make=mantis_reaper, ent=(0.9, 2.8), stats=dict(hp=44, speed=0.36, dmg=9, armor=4, kb=0)),
    "brood_queen": dict(make=brood_queen, rig="crawler", ent=(2.4, 2.6), stats=dict(hp=330, speed=0.26, dmg=15, armor=12, kb=0.6), key=True),
}
