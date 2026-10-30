"""The Eclipse Cathedral's monsters, each built by hand (tools/vox2.py). The angels who kept the sun's cathedral, and
fell with it the day the sun went black: black-gold plate, black feathers, burnt porcelain skin cracked with the
white-gold light still inside them, ash falling off everything, haloes nailed on, broken, or burning black.

    cherub_husk     swarm   a burnt cherub: a fat cracked porcelain child with a gilt mask, stub wings, a broken halo on a spike
    halo_knight     brute   a giant in black-gold plate, his halo hammered onto the helm as a crown of spikes, a censer flail
    ash_choir       caster  a choir in one robe: a tall hood with three singing gilt faces stacked in it, ash pouring, a burning hymnal
    fallen_blade    skirm   a lean fallen angel, one great black wing and one burnt stump, blindfolded, two curved black-gold blades
    seraph_warden   elite   six wings - two over its face (with eyes on them), two raised, two over the legs - gilt plate,
                            a great halo behind (the key), a sword of white fire
    fallen_seraph   boss    the Fallen Seraph: huge, the black sun behind its head with the corona burning round it, six torn
                            black wings, black-gold plate, a burnt face half masked in gold, broken chains, the Eclipse greatsword

    python tools/monsterforge.py eclipse_cathedral --preview ; python tools/mobsheet.py eclipse_cathedral
"""
import math

import vox2 as X
from vox2 import C, ramp

BLACK = ramp("#040406", "#0a0a0e", "#121218", "#1c1c24", "#282832", "#363642", "#4a4a58")
GILT = ramp("#2e2008", "#4a340e", "#6a4c16", "#8e6820", "#b8902e", "#dcb44a", "#f4d878")
FEATH = ramp("#030304", "#08080a", "#0e0e12", "#16161c", "#202028", "#2c2c36")
ASH = ramp("#1e1c1a", "#2a2826", "#383532", "#46423e", "#55504a", "#666058")
SKIN = ramp("#2a2420", "#4a4036", "#6e6252", "#968872", "#bcae94", "#ddd2ba")
CORONA = ramp("#8a6a1a", "#c8a03a", "#f0d070", "#fff0b0", "#ffffff")
FIRE = ramp("#c8a03a", "#f0d070", "#fff0b0", "#ffffff")
ROBE = ramp("#0a0a0c", "#121216", "#1a1a20", "#24242a", "#2e2e36")


def shaders():
    return {
        "plate": X.surf(BLACK, 0.5, 1.5, 0.14, 0.24, crust=(ASH, 0.1)),
        "gilt": X.surf(GILT, 0.55, 1.5, 0.12, 0.26),
        "feather": X.surf(FEATH, 0.5, 1.2, 0.2, 0.12, stripe=2),
        "ash": X.surf(ASH, 0.5, 1.0, 0.3, 0.0, holes=True),
        "skin": X.surf(SKIN, 0.56, 1.3, 0.06, 0.14, crust=(ASH, 0.14)),
        "robe": X.surf(ROBE, 0.5, 1.0, 0.22, 0.0, holes=True, drip=(ASH, 0.3)),
        "glow": X.glow(CORONA),
        "fire": X.glow(FIRE, 0.7, 0.3),
        "eye": X.glow(CORONA, 0.84, 0.14),
        "void": X.dark(FEATH),
        "dark": X.dark(BLACK),
        "iron": X.surf(BLACK, 0.5, 1.2, 0.2, 0.1),
    }


def along(pts, t):
    t = max(0.0, min(0.999, t)) * (len(pts) - 1)
    i = int(t)
    f = t - i
    return tuple(pts[i][j] + (pts[i + 1][j] - pts[i][j]) * f for j in range(3))


def wing(k, part, root, side, span, rise, s=1.0, back=-3.0, mat="feather", trim="gilt", torn=(), n=9):
    """an angel's wing: an arm of bone out and up from the back, long primaries hanging off it (longest at the tip),
    a shorter row of gilt-edged coverts over them; `torn` lists primaries burnt short"""
    x, y, z = root
    pts = [root, (x + side * span * 0.35, y + rise * 0.6, z + back), (x + side * span * 0.75, y + rise, z + back * 1.6),
           (x + side * span, y + rise * 0.82, z + back * 2.0)]
    for (a, b), w in zip(zip(pts, pts[1:]), (2.2 * s, 1.7 * s, 1.2 * s)):
        k.limb(part, a, b, w, mat, "wing_bone")
    for i in range(n):
        f = i / (n - 1)
        p = along(pts, 0.22 + 0.78 * f)
        L = (9 + 15 * f) * s * (0.45 if i in torn else 1.0)
        k.limb(part, p, (p[0] + side * f * 4 * s, p[1] - L, p[2] - 1.0), 2.6 * s, mat, "feather", d=0.6 * s)
    for i in range(6):
        f = i / 5
        p = along(pts, 0.08 + 0.84 * f)
        k.limb(part, p, (p[0] + side * 1.0 * s, p[1] - 6.0 * s, p[2] - 0.4), 2.8 * s, trim if i % 2 else mat, "covert", d=0.8 * s)


def halo_ring(k, part, c, r, w, mat="glow", n=20, axis="z", tag="halo"):
    cx, cy, cz = c
    for i in range(n):
        a0, a1 = i * 2 * math.pi / n, (i + 1) * 2 * math.pi / n

        def at(a):
            u, v = math.cos(a) * r, math.sin(a) * r
            return {"z": (cx + u, cy + v, cz), "y": (cx + u, cy, cz + v)}[axis]
        k.limb(part, at(a0), at(a1), w, mat, tag, group="glow" if mat in ("glow", "fire", "eye") else "lit")


def mask(k, part, cx, cy, cz, w, h, mouth="slit"):
    """a gilt face mask: brow, cheek planes, empty eye holes with light behind, a mouth"""
    k.box(part, C(cx, cy, cz, w, h, 1.0), "gilt", tag="mask")
    k.box(part, C(cx, cy + h * 0.62, cz + 0.4, w * 0.9, h * 0.14, 0.6), "gilt", tag="brow")
    for sx in (-1, 1):
        k.box(part, C(cx + sx * w * 0.22, cy + h * 0.46, cz + 0.55, w * 0.2, h * 0.14, 0.3), "eye", group="glow", tag="eye")
    k.box(part, C(cx, cy + h * 0.25, cz + 0.6, w * 0.12, h * 0.28, 0.6), "gilt", tag="nose")
    if mouth == "o":
        k.box(part, C(cx, cy + h * 0.04, cz + 0.55, w * 0.3, h * 0.2, 0.3), "void", tag="mouth")
    else:
        k.box(part, C(cx, cy + h * 0.1, cz + 0.55, w * 0.36, h * 0.05, 0.3), "void", tag="mouth")


# ================================================================ the Fallen Seraph (boss)

def fallen_seraph():
    """The highest of the angels who kept the sun. When the sun went black it would not leave it, and it fell with it,
    and the black sun came down with it and hangs behind its head still: a disc of nothing with the corona burning
    round it and rays of white fire standing out. Six wings, black, torn, the top pair raised over it, the middle
    pair spread, the lowest hanging. Black-gold plate cracked to the burning light inside. Its face is burnt to the
    bone on one side and the other is a mask of gold. The chains the other angels bound it with hang broken from its
    wrists. It carries the Eclipse: a greatsword as long as it is tall, black, the edge gold, a white-hot core."""
    k = X.Kit("fallen_seraph")
    hips = k.part("hips", (0, 36, 0))
    k.stack(hips, 0, 0, [(28, 20, 13), (36, 21, 13.4)], "plate", "faulds")
    k.box(hips, C(0, 35, 0, 22, 2.4, 14.4), "gilt", tag="belt")
    for i in range(12):                    # the skirt of black feathers, gilt every third
        a = math.radians(-160 + i * 29)
        x, z = math.sin(a) * 10.6, math.cos(a) * 7.0
        k.limb(hips, (x, 32, z), (x * 1.3, 12 + (i % 3) * 2, z * 1.4), 3.4, "gilt" if i % 3 == 0 else "feather", "feather_skirt", d=0.8)
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 5.6
        th = k.part("thigh_" + nm, (x, 32, 0), (("x", -6), ("z", side * 4)), "hips")
        sh = k.part("shin_" + nm, (x, 18, 0), (("x", 8),), th)
        ft = k.part("foot_" + nm, (x, 4, 0), (("x", -2),), sh)
        k.stack(th, x, 0, [(18, 8.0, 8.4), (32, 9.4, 9.6)], "plate", "cuisse")
        k.blob(th, (x, 18.6, 1.2), (4.6, 2.8, 4.6), "gilt", "knee")
        k.stack(sh, x, 0, [(4, 7.0, 7.6), (17, 8.4, 8.8)], "plate", "greave")
        k.box(sh, C(x, 9, 3.8, 2.0, 8, 1.0), "gilt", tag="greave_ridge")
        k.box(ft, C(x, 0, 2.0, 8.0, 4.0, 12), "plate", tag="foot")
        k.shard(ft, (x, 1.6, 8.0), (0, 0, 1), 3.4, 3.0, mat="gilt", tag="foot")
    # ---------------------------------------------------------------- torso: black-gold plate cracked to the light
    to = k.part("torso", (0, 36, 0), (("x", 6),), "hips")
    k.stack(to, 0, 0, [(36, 21, 13.4), (44, 24, 14.6), (52, 30, 16), (58, 28, 14.4)], "plate", "cuirass")
    k.box(to, C(0, 51, 7.6, 3.0, 12, 1.4), "gilt", tag="sternum")
    for (x0, y0, x1, y1) in ((-2, 40, -7, 48), (-7, 48, -10, 55), (3, 44, 8, 52), (8, 52, 6, 57), (-1, 38, 1, 44)):
        k.limb(to, (x0, y0, 7.7), (x1, y1, 8.0), 1.0, "fire", "crack", group="glow", d=0.4)
    for side in (1, -1):
        k.blob(to, (side * 16, 57, 0), (8.4, 5.4, 8.4), "plate", "pauldron")
        k.blob(to, (side * 16.4, 58.6, 0), (6.4, 3.4, 6.6), "gilt", "pauldron_trim")
        for dz in (-3, 0.6, 4):
            k.shard(to, (side * 18, 61, dz), (side * 0.5, 1, 0), 6.0, 2.0, mat="gilt", tag="pauldron_spike")
    k.box(to, C(0, 58, -6.8, 12, 6, 2), "plate", tag="wing_mount")
    # ---------------------------------------------------------------- the six wings, black and torn (fixed to the torso)
    wg = k.part("wings", (0, 56, -7), (), to, bone=False)
    for side in (1, -1):
        wing(k, wg, (side * 5, 58, -7), side, 44, 30, s=1.7, back=-2.4, torn=(2, 6) if side > 0 else (4,))
        wing(k, wg, (side * 5, 52, -7.4), side, 38, 6, s=1.4, back=-3.0, torn=(5,) if side > 0 else (1, 7))
        wing(k, wg, (side * 4, 44, -7.4), side, 26, -12, s=1.1, back=-2.0, torn=(3,), n=7)
    # ---------------------------------------------------------------- the black sun behind its head
    sun = k.part("black_sun", (0, 82, -12), (), to, bone=False)
    k.blob(sun, (0, 84, -13), (19, 19, 1.2), "void", "black_sun", step=1.2)
    halo_ring(k, sun, (0, 84, -12.2), 19.6, 2.8, "fire", n=36, tag="corona")
    halo_ring(k, sun, (0, 84, -12.6), 22.6, 1.2, "glow", n=36, tag="corona")
    for i in range(20):
        a = i * 2 * math.pi / 20 + 0.1
        L = 12 if i % 2 else 6
        k.shard(sun, (math.cos(a) * 21, 84 + math.sin(a) * 21, -12.4), (math.cos(a), math.sin(a), 0), L, 2.6, mat="fire", tag="ray", group="glow")
    # ---------------------------------------------------------------- the head: burnt to the bone on one side, a gold mask on the other
    hd = k.part("head", (0, 58, 1), (("x", -6),), "torso")
    k.box(hd, C(0, 58, 0.6, 7, 4, 7), "plate", tag="gorget")
    k.blob(hd, (0, 66, 1.4), (5.6, 6.8, 6.0), "skin", "skull")
    k.box(hd, C(-2.6, 61.6, 6.4, 5.8, 9.6, 1.4), "gilt", tag="half_mask")
    k.box(hd, C(-2.6, 66.4, 7.2, 2.2, 1.4, 0.4), "eye", group="glow", tag="eye")
    k.box(hd, C(2.6, 66.2, 6.8, 2.4, 1.8, 0.6), "void", tag="eye_socket")
    k.box(hd, C(2.6, 66.4, 7.1, 1.2, 0.8, 0.4), "fire", group="glow", tag="eye")
    for x in (1.2, 2.4, 3.6):
        k.box(hd, C(x, 61.6, 6.6, 0.8, 1.6, 0.6), "skin", tag="teeth")
    for (x, z, L) in ((-4, -2, 26), (-2, -4, 30), (0, -5, 32), (2, -4, 28), (4, -2, 24), (5, 1, 18), (-5, 1, 20)):
        k.limb(hd, (x, 71, z), (x * 1.6, 71 - L, z * 1.8 - 3), 2.0, "ash", "hair")
    for i in range(7):                     # a crown of broken gilt rays
        a = math.radians(-60 + i * 20)
        k.shard(hd, (math.sin(a) * 5, 71, math.cos(a) * 3), (math.sin(a) * 0.5, 1, math.cos(a) * 0.2), 5 if i % 2 else 3, 1.4, mat="gilt", tag="crown")
    # ---------------------------------------------------------------- arms, the broken chains, the Eclipse
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 17
        up = k.part("arm_" + nm, (x, 55, 0), (("x", -20 if side > 0 else -50), ("z", side * 14)), "torso")
        fo = k.part("fore_" + nm, (x, 42, 0), (("x", -30 if side > 0 else -50),), up)
        hn = k.part("hand_" + nm, (x, 29, 0), (), fo)
        k.stack(up, x, 0, [(42, 7.4, 7.6), (54, 8.4, 8.6)], "plate", "rerebrace")
        k.blob(up, (x, 42.6, 0), (4.8, 3.0, 4.8), "gilt", "elbow")
        k.stack(fo, x, 0, [(30, 8.0, 8.0), (41, 7.2, 7.2)], "plate", "vambrace")
        k.box(fo, C(x, 30, 0, 9.6, 3.0, 9.6), "gilt", tag="manacle")
        k.chain(fo, (x + side * 4, 31, 0), (x + side * 7, 18, 3), 6, w=1.6)
        k.box(hn, C(x, 24.4, 0.6, 6.4, 6.0, 6.0), "plate", tag="gauntlet")
    sw = k.part("eclipse_blade", (-17, 26, 1), (("x", 82),), k.parts["hand_r"])
    k.limb(sw, (-17, 12, 1), (-17, 30, 1), 2.4, "plate", "grip")
    k.box(sw, C(-17, 11, 1, 3.6, 3.0, 3.6), "gilt", tag="pommel")
    k.box(sw, C(-17, 30, 1, 18, 2.8, 4.0), "gilt", tag="guard")
    for sx in (-1, 1):
        k.shard(sw, (-17 + sx * 9, 30, 1), (sx * 0.4, 1, 0), 6, 2.4, mat="gilt", tag="guard")
    k.box(sw, C(-17, 32, 1, 8.6, 60, 2.0), "dark", tag="blade")
    k.box(sw, C(-17, 32, 1, 9.6, 60, 1.2), "gilt", tag="blade_edge")
    k.box(sw, C(-17, 33, 1, 2.0, 56, 2.4), "fire", group="glow", tag="blade_core")
    k.shard(sw, (-17, 92, 1), (0, 1, 0), 9, 9.0, mat="dark", tag="blade_tip")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Seraph Warden (elite, the key)

def seraph_warden():
    """The warden of the choir door is a seraph of the old kind: six wings. Two it holds crossed over its face, and
    there are eyes in the feathers of those that see for it. Two stand raised from its shoulders. Two hang over its
    legs like a skirt. Its body is gilt plate, its halo is a wheel of white fire behind it as wide as a door - the
    halo is the key - and in its hand a sword that is all white flame."""
    k = X.Kit("seraph_warden")
    hips = k.part("hips", (0, 24, 0))
    k.stack(hips, 0, 0, [(18, 14, 9), (24, 15, 9.6)], "gilt", "faulds")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 3.8
        th = k.part("thigh_" + nm, (x, 22, 0), (("x", -4),), "hips")
        sh = k.part("shin_" + nm, (x, 12, 0), (("x", 6),), th)
        ft = k.part("foot_" + nm, (x, 3, 0), (), sh)
        k.box(th, C(x, 12.4, 0, 5.4, 9.6, 6.0), "plate", tag="cuisse")
        k.box(sh, C(x, 3.0, 0, 5.2, 9.4, 5.8), "gilt", tag="greave")
        k.box(ft, C(x, 0, 1.6, 5.6, 3.0, 8.4), "plate", tag="foot")
    # the lowest pair of wings hangs over the legs like a skirt (fixed to the hips)
    lw = k.part("leg_wings", (0, 22, 0), (), hips, bone=False)
    for side in (1, -1):
        for i in range(7):
            f = i / 6
            x = side * (2 + f * 7)
            k.limb(lw, (x, 23, 4 - f * 6), (x * 1.25, 4 + f * 3, 5.6 - f * 7), 3.0, "gilt" if i == 0 else "feather", "skirt_feather", d=0.7)
    # ---------------------------------------------------------------- torso
    to = k.part("torso", (0, 24, 0), (("x", 4),), "hips")
    k.stack(to, 0, 0, [(24, 15, 9.6), (30, 18, 10.6), (36, 21, 11.4), (40, 19, 10)], "gilt", "cuirass")
    k.box(to, C(0, 32, 5.8, 9, 6, 1.0), "plate", tag="sun_plate")
    halo_ring(k, to, (0, 33, 6.4), 2.6, 0.9, "glow", n=10, tag="sun_sigil")
    for side in (1, -1):
        k.blob(to, (side * 11, 39, 0), (5.6, 3.8, 6.0), "gilt", "pauldron")
    wg = k.part("wings", (0, 38, -5), (), to, bone=False)
    for side in (1, -1):
        wing(k, wg, (side * 4, 40, -5), side, 26, 24, s=1.15, back=-2.0)
    # the halo: a wheel of white fire behind it, as wide as a door - this is the key
    hl = k.part("halo", (0, 50, -9), (), to, bone=False)
    halo_ring(k, hl, (0, 52, -9), 13, 2.2, "fire", n=28, tag="halo")
    halo_ring(k, hl, (0, 52, -9.2), 9.6, 0.9, "glow", n=24, tag="halo")
    for i in range(8):
        a = i * math.pi / 4
        k.limb(hl, (math.cos(a) * 9.6, 52 + math.sin(a) * 9.6, -9.1), (math.cos(a) * 13, 52 + math.sin(a) * 13, -9.1), 0.8, "glow", "spoke", group="glow")
    # ---------------------------------------------------------------- the head, and the two wings crossed over the face
    hd = k.part("head", (0, 40, 0.6), (), "torso")
    k.blob(hd, (0, 44, 0.6), (4.0, 4.6, 4.2), "plate", "head")
    for side in (1, -1):
        for i in range(6):
            f = i / 5
            a = (side * (1.5 + f * 3), 49 - f * 1.6, 3.4)
            b = (-side * (2.6 + f * 2.4), 39 + f * 3.6, 6.6 - f * 0.6)
            k.limb(hd, a, b, 2.6, "gilt" if i == 5 else "feather", "face_wing", d=0.7)
        for (u, v) in ((0.25, 0.4), (0.55, 0.6), (0.8, 0.3)):   # eyes in the feathers
            ex = side * (2.0 - u * 4.6)
            k.box(hd, C(ex, 43 + v * 4, 7.0 - u * 0.4, 1.4, 1.0, 0.5), "eye", group="glow", tag="eye")
    # ---------------------------------------------------------------- arms, the sword of white fire
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 11
        up = k.part("arm_" + nm, (x, 38, 0), (("x", -30 if side > 0 else -40), ("z", side * 10)), "torso")
        fo = k.part("fore_" + nm, (x, 29, 0), (("x", -30 if side > 0 else -60),), up)
        hn = k.part("hand_" + nm, (x, 20, 0), (), fo)
        k.box(up, C(x, 29.6, 0, 4.8, 8.6, 5.0), "plate", tag="rerebrace")
        k.box(fo, C(x, 20.6, 0, 4.8, 8.6, 5.0), "gilt", tag="vambrace")
        k.box(hn, C(x, 16.8, 0.4, 4.4, 4.0, 4.4), "plate", tag="gauntlet")
    sw = k.part("fire_sword", (-11, 18, 0.6), (("x", 82),), k.parts["hand_r"])
    k.limb(sw, (-11, 10, 0.6), (-11, 20, 0.6), 1.6, "plate", "grip")
    k.box(sw, C(-11, 20, 0.6, 9, 1.8, 2.4), "gilt", tag="guard")
    k.box(sw, C(-11, 21.6, 0.6, 4.0, 30, 1.4), "fire", group="glow", tag="blade")
    for i in range(6):                     # flames licking off the blade
        y = 25 + i * 4.4
        sx = 1 if i % 2 else -1
        k.shard(sw, (-11 + sx * 1.8, y, 0.6), (sx * 0.6, 1, 0), 3.4, 1.4, mat="glow", tag="flame", group="glow")
    k.shard(sw, (-11, 51.4, 0.6), (0, 1, 0), 6, 4.0, mat="fire", tag="blade_tip", group="glow")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Halo Knight (brute)

def halo_knight():
    """The cathedral's knights were given haloes. When they fell, the haloes would not come off, so they hammered them
    down onto their helms: a crown of gilt spikes driven round the head. A giant in black-gold plate, a tabard of ash
    with the sun on it gone black, small burnt wings folded on his back, and he swings the cathedral's great censer
    on its chain like a flail - white coals inside, ash pouring off it."""
    k = X.Kit("halo_knight")
    hips = k.part("hips", (0, 22, 0))
    k.stack(hips, 0, 0, [(15, 17, 11), (22, 18, 11.6)], "plate", "faulds")
    k.box(hips, C(0, 4, 6.2, 10, 18, 0.8), "ash", tag="tabard")
    k.box(hips, C(0, 4, -6.2, 10, 16, 0.8), "ash", tag="tabard")
    halo_ring(k, hips, (0, 15, 6.8), 2.4, 0.8, "dark", n=10, tag="black_sun")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 5.0
        th = k.part("thigh_" + nm, (x, 20, 0), (("x", -8), ("z", side * 8)), "hips")
        sh = k.part("shin_" + nm, (x, 11, 0), (("x", 12),), th)
        ft = k.part("foot_" + nm, (x, 3, 0), (("x", -4),), sh)
        k.stack(th, x, 0, [(11, 7.6, 7.8), (20, 8.6, 8.8)], "plate", "cuisse")
        k.blob(th, (x, 11.4, 1.6), (4.4, 2.6, 4.0), "gilt", "knee")
        k.stack(sh, x, 0, [(3, 7.0, 7.4), (11, 7.8, 8.0)], "plate", "greave")
        k.box(ft, C(x, 0, 1.8, 8.6, 3.6, 11.6), "plate", tag="foot")
    # ---------------------------------------------------------------- torso
    to = k.part("torso", (0, 22, 0), (("x", 14),), "hips")
    k.stack(to, 0, 0, [(22, 18, 11.6), (29, 24, 13.6), (35, 28, 14.4), (39, 26, 13)], "plate", "cuirass")
    k.box(to, C(0, 22, 0, 19, 4, 12.6), "gilt", tag="belt")
    for x in (-8, 0, 8):
        k.box(to, C(x, 30, 7.0, 2.0, 8, 0.8), "gilt", tag="cuirass_rib")
    for side in (1, -1):
        k.blob(to, (side * 15, 37, 0), (7.4, 5.0, 7.6), "plate", "pauldron")
        k.blob(to, (side * 15.6, 38.6, 0), (5.6, 3.2, 6.0), "gilt", "pauldron_trim")
    wg = k.part("wings", (0, 36, -7), (), to, bone=False)
    for side in (1, -1):
        wing(k, wg, (side * 4, 36, -7), side, 12, 6, s=0.7, back=-1.6, torn=(1, 4), n=6)
    # ---------------------------------------------------------------- the helm and the halo hammered onto it
    hd = k.part("head", (0, 39, 2), (("x", -14),), "torso")
    k.blob(hd, (0, 44, 2.4), (5.6, 6.0, 6.0), "plate", "helm")
    k.box(hd, C(0, 44.4, 8.0, 7.0, 1.0, 0.6), "eye", group="glow", tag="eye")
    k.box(hd, C(0, 40, 7.6, 1.4, 4.0, 1.0), "gilt", tag="nasal")
    halo_ring(k, hd, (0, 48.4, 2.4), 6.4, 1.4, "gilt", n=16, axis="y", tag="halo_crown")
    for i in range(10):
        a = i * 2 * math.pi / 10
        k.shard(hd, (math.cos(a) * 6.2, 48.4, 2.4 + math.sin(a) * 6.2), (math.cos(a) * 0.3, 1, math.sin(a) * 0.3), 6 if i % 2 else 4, 1.6, mat="gilt", tag="halo_spike")
    k.box(hd, C(0, 48.6, 2.4, 2.0, 1.6, 2.0), "fire", group="glow", tag="nail")
    # ---------------------------------------------------------------- arms: the censer flail
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 15
        up = k.part("arm_" + nm, (x, 36, 0), (("x", -20 if side > 0 else -50), ("z", side * 12)), "torso")
        fo = k.part("fore_" + nm, (x, 25, 0), (("x", -30 if side > 0 else -40),), up)
        hn = k.part("hand_" + nm, (x, 14, 0), (), fo)
        k.stack(up, x, 0, [(25, 7.0, 7.2), (33, 8.0, 8.2)], "plate", "rerebrace")
        k.stack(fo, x, 0, [(15, 7.6, 7.6), (25, 7.0, 7.0)], "plate", "vambrace")
        k.box(fo, C(x, 15.6, 0, 8.6, 2.6, 8.6), "gilt", tag="cuff")
        k.box(hn, C(x, 9.4, 0.6, 7.4, 6.4, 7.4), "plate", tag="gauntlet")
    cf = k.part("censer", (-15, 9, 1), (("x", 30),), k.parts["hand_r"])
    k.limb(cf, (-15, 6, 1), (-15, 12, 1), 2.0, "plate", "haft")
    k.chain(cf, (-15, 6, 1), (-15, -8, 4), 5, mat="gilt", w=1.6)
    k.blob(cf, (-15, -14, 5), (6.0, 6.4, 6.0), "gilt", "censer_bowl")
    for (dx, dy) in ((-3, -12), (3, -12), (0, -16), (-3, -17), (3, -16)):
        k.box(cf, C(-15 + dx, -14 + (dy + 14), 10.6, 1.4, 1.4, 0.6), "fire", group="glow", tag="censer_hole")
    k.shard(cf, (-15, -8, 5), (0, 1, 0), 3, 3.0, mat="gilt", tag="censer_cap")
    for (dx, dz, L) in ((-2, 1, 10), (1, -1, 14), (3, 2, 8)):
        k.limb(cf, (-15 + dx, -20, 5 + dz), (-15 + dx * 2, -20 - L * 0.4, 5 + dz * 2), 2.6, "ash", "ash_smoke", d=2.0)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Choir of Ash (caster)

def ash_choir():
    """The cathedral choir sang the sun up every morning. On the last morning they were singing when it went black, and
    they burnt where they stood, and the ash is still singing: a tall robe, a hood too wide, and in the hood three
    gilt faces one above another with their mouths open on the same note. Ash pours off it. It holds the hymnal
    open, and the pages are burning white."""
    k = X.Kit("ash_choir")
    hips = k.part("hips", (0, 22, 0))
    k.stack(hips, 0, 0, [(0, 16, 13), (8, 13, 10), (22, 11, 7.6)], "robe", "robe")
    for (x, z, L) in ((-6, 4, 8), (6, 5, 10), (0, -6, 9), (-5, -5, 7), (5, -4, 8), (0, 6, 6)):
        k.limb(hips, (x, 2, z), (x * 1.2, -0.4, z * 1.3), 2.2, "ash", "ash_pour", d=1.4)
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.4
        th = k.part("thigh_" + nm, (x, 22, 0), (), "hips")
        sh = k.part("shin_" + nm, (x, 12, 0), (), th)
        ft = k.part("foot_" + nm, (x, 3, 0), (), sh)
        k.box(ft, C(x, 0, 1.4, 3.0, 1.2, 5.0), "ash", tag="foot")
    # ---------------------------------------------------------------- torso: narrow, the wide hood, three faces
    to = k.part("torso", (0, 22, 0), (("x", 4),), "hips")
    k.stack(to, 0, 0, [(22, 11, 7.6), (30, 12.6, 8.0), (36, 14, 8.6)], "robe", "robe")
    k.stack(to, 0, -0.6, [(34, 18, 12), (44, 17, 12), (52, 12, 9), (55, 6, 5)], "robe", "hood")
    k.box(to, C(0, 33.6, 3.4, 13, 20, 4.0), "void", tag="hood_dark")
    halo_ring(k, to, (0, 44, 6.4), 8.0, 1.2, "gilt", n=18, tag="hood_rim")
    for x in (-4.6, 4.6):
        k.box(to, C(x, 14, 4.2, 2.4, 22, 0.8), "gilt", tag="stole")
    for i, y in enumerate((35, 41, 47)):
        mask(k, to, 0, y, 5.8, 8.6 - i * 0.8, 5.4, mouth="o")
        k.limb(to, (0, y + 0.6, 6.4), (0, y - 3.4, 9.0), 1.2, "ash", "ash_breath", d=0.8)
    wg = k.part("wings", (0, 36, -5), (), to, bone=False)
    for side in (1, -1):
        wing(k, wg, (side * 3, 36, -5), side, 14, 10, s=0.7, back=-1.4, mat="ash", trim="ash", torn=(2, 3), n=6)
    k.part("head", (0, 44, 0), (), "torso")
    # ---------------------------------------------------------------- arms: the burning hymnal
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 7.0
        up = k.part("arm_" + nm, (x, 35, 0), (("x", -50), ("z", side * 8)), "torso")
        fo = k.part("fore_" + nm, (x, 26, 0), (("x", -40),), up)
        hn = k.part("hand_" + nm, (x, 17, 0), (), fo)
        k.stack(up, x, 0, [(26, 4.6, 4.8), (35, 5.0, 5.2)], "robe", "sleeve")
        k.stack(fo, x, 0, [(17, 6.4, 6.4), (26, 5.0, 5.0)], "robe", "sleeve")
        k.box(hn, C(x, 13.6, 0.4, 2.6, 3.6, 2.2), "skin", tag="hand")
    bk = k.part("hymnal", (0, 14, 6), (), k.parts["hand_l"], bone=False)
    k.box(bk, C(4, 12.6, 4.0, 7.0, 1.0, 5.0), "plate", tag="book")
    k.box(bk, C(4, 13.6, 4.0, 6.4, 0.6, 4.4), "fire", group="glow", tag="pages")
    for (dx, dz) in ((-2, 0), (0, 1), (2, -1)):
        k.shard(bk, (4 + dx, 14, 4 + dz), (0, 1, 0), 3.0, 1.2, mat="glow", tag="flame", group="glow")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Fallen Blade (skirmisher)

def fallen_blade():
    """The cathedral's executioners. They fell fastest. Lean, in black leather and gilt bracers, one great black wing
    still on, the other burnt to a stump of bone; a strip of gold cloth tied over their eyes so they cannot see what
    they did; two curved blades of black gold."""
    k = X.Kit("fallen_blade")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(15, 9.0, 6.0), (20, 9.6, 6.4)], "plate", "hips")
    k.box(hips, C(0, 6, 3.4, 5, 12, 0.6), "feather", tag="loincloth")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.8
        th = k.part("thigh_" + nm, (x, 19, 0), (("x", -20), ("z", side * 8)), "hips")
        sh = k.part("shin_" + nm, (x, 11, 0), (("x", 30),), th)
        ft = k.part("foot_" + nm, (x, 3, 0), (("x", -10),), sh)
        k.box(th, C(x, 11.4, 0, 3.6, 8.4, 4.0), "plate", tag="thigh")
        k.box(sh, C(x, 3.0, 0, 3.2, 8.6, 3.6), "plate", tag="shin")
        k.box(sh, C(x, 7.0, 2.0, 3.6, 3.6, 0.6), "gilt", tag="knee_plate")
        k.box(ft, C(x, 0, 1.2, 3.6, 2.6, 6.4), "plate", tag="foot")
    to = k.part("torso", (0, 20, 0), (("x", 18),), "hips")
    k.stack(to, 0, 0, [(20, 9.6, 6.4), (26, 12, 6.8), (31, 13.4, 7.0)], "plate", "body")
    for y in (22, 25, 28):
        k.box(to, C(0, y, 3.5, 9, 0.8, 0.4), "gilt", tag="strap")
    wg = k.part("wings", (0, 30, -3.6), (), to, bone=False)
    wing(k, wg, (3, 30, -3.6), 1, 26, 18, s=1.0, back=-2.0, torn=(3,))
    pts = [(-3, 30, -3.6), (-7, 34, -5), (-10, 33, -6)]    # the burnt stump on the other side
    for (a, b) in zip(pts, pts[1:]):
        k.limb(wg, a, b, 1.6, "skin", "stump_bone")
    k.limb(wg, (-7, 34, -5), (-8, 29, -6), 1.4, "ash", "stump_feather", d=0.6)
    hd = k.part("head", (0, 31, 1), (("x", -18),), "torso")
    k.blob(hd, (0, 35, 1.2), (3.0, 3.6, 3.2), "skin", "head")
    k.box(hd, C(0, 35.6, 4.0, 6.8, 1.6, 0.8), "gilt", tag="blindfold")
    k.limb(hd, (2.6, 36.4, 0), (5, 33, -4), 1.0, "gilt", "blindfold_tail", d=0.3)
    k.limb(hd, (2.4, 36.2, -1), (4, 31, -5), 1.0, "gilt", "blindfold_tail", d=0.3)
    for (x, z) in ((-2, -2), (0, -3), (2, -2), (-1, 0), (1, 0)):
        k.limb(hd, (x, 38.4, z), (x * 1.4, 32, z - 3), 1.4, "ash", "hair")
    k.box(hd, C(0, 33, 4.2, 1.6, 0.4, 0.3), "void", tag="mouth")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 7.4
        up = k.part("arm_" + nm, (x, 30, 0), (("x", -40), ("z", side * 20)), "torso")
        fo = k.part("fore_" + nm, (x, 22, 0), (("x", -50),), up)
        hn = k.part("hand_" + nm, (x, 14, 0), (), fo)
        k.box(up, C(x, 22.4, 0, 2.8, 8.0, 3.0), "plate", tag="arm")
        k.box(fo, C(x, 14.4, 0, 3.2, 8.0, 3.4), "gilt", tag="bracer")
        k.box(hn, C(x, 11.6, 0.3, 2.8, 2.8, 2.6), "plate", tag="hand")
        bl = k.part("blade_" + nm, (x, 12.6, 0.4), (("x", 80),), hn)
        k.box(bl, C(x, 13.4, 0.4, 3.4, 1.0, 1.8), "gilt", tag="guard")
        pts = [(x, 14.4, 0.4), (x, 22, 0.4), (x + side * 1.4, 28, 0.4), (x + side * 3.4, 32, 0.4)]
        for (a, b), w in zip(zip(pts, pts[1:]), (2.4, 2.0, 1.4)):
            k.limb(bl, a, b, w, "dark", "blade", d=0.6)
            k.limb(bl, (a[0] + side * 0.9, a[1], a[2]), (b[0] + side * 0.9, b[1], b[2]), 0.6, "gilt", "blade_edge", d=0.7)
        k.limb(bl, (x, 9, 0.4), (x, 12.6, 0.4), 1.0, "plate", "grip")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Cherub Husk (swarm)

def cherub_husk():
    """The cathedral's cherubs were porcelain, painted gold, and when the sun went black something got into them.
    A fat baby the size of a dog, the porcelain burnt and cracked and the white light coming out of the cracks, a
    gilt mask for a face with nothing behind the eyes, two little charred wings that cannot lift it, and its halo
    broken off and stuck back on a spike in its skull. It runs on all fours, and laughs."""
    k = X.Kit("cherub_husk")
    hips = k.part("hips", (0, 9, 0))
    k.blob(hips, (0, 8.6, 0), (4.4, 3.4, 3.8), "skin", "belly")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.6
        th = k.part("thigh_" + nm, (x, 8, 0), (("x", -40), ("z", side * 10)), "hips")
        sh = k.part("shin_" + nm, (x, 4, 0), (("x", 50),), th)
        ft = k.part("foot_" + nm, (x, 1.2, 0), (("x", -10),), sh)
        k.blob(th, (x, 5.6, 0.4), (2.0, 2.6, 2.2), "skin", "thigh")
        k.blob(sh, (x, 2.4, 0), (1.6, 2.0, 1.8), "skin", "calf")
        k.box(ft, C(x, 0, 0.8, 2.6, 1.2, 3.6), "skin", tag="foot")
    to = k.part("torso", (0, 9, 0), (("x", 30),), "hips")
    k.blob(to, (0, 12.4, 0), (4.0, 3.4, 3.4), "skin", "chest")
    for (x0, y0, x1, y1) in ((-2, 9, -3, 13), (1, 10, 3, 14), (0, 12, -1, 15)):
        k.limb(to, (x0, y0, 3.4), (x1, y1, 3.3), 0.6, "fire", "crack", group="glow", d=0.3)
    wg = k.part("wings", (0, 14, -2.6), (), to, bone=False)
    for side in (1, -1):
        wing(k, wg, (side * 2, 14, -2.6), side, 7, 5, s=0.4, back=-0.8, mat="ash", trim="feather", torn=(1, 3), n=5)
    hd = k.part("head", (0, 15, 0.6), (("x", -24),), "torso")
    k.blob(hd, (0, 19, 0.6), (4.2, 4.0, 4.0), "skin", "head")
    mask(k, hd, 0, 16.4, 4.2, 6.0, 5.2, mouth="o")
    for (x, z) in ((-3, -1), (3, -1), (-2, -3), (2, -3), (0, -3.4)):
        k.box(hd, C(x, 21.4, z, 1.6, 1.4, 1.6), "gilt", tag="curls")
    k.limb(hd, (0.6, 22.6, 0), (1.4, 26.4, -0.6), 0.6, "plate", "spike")
    halo_ring(k, hd, (1.4, 26.4, -0.6), 3.0, 0.7, "gilt", n=10, axis="y", tag="broken_halo")
    k.box(hd, C(4.0, 26.0, -0.6, 1.6, 0.8, 0.8), "void", tag="halo_break")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 4.2
        up = k.part("arm_" + nm, (x, 14, 0), (("x", -70), ("z", side * 12)), "torso")
        fo = k.part("fore_" + nm, (x, 10, 0), (("x", -10),), up)
        hn = k.part("hand_" + nm, (x, 6, 0), (), fo)
        k.blob(up, (x, 12, 0), (1.6, 2.4, 1.8), "skin", "arm")
        k.blob(fo, (x, 8, 0), (1.4, 2.2, 1.6), "skin", "forearm")
        k.box(hn, C(x, 4.4, 0.4, 2.2, 1.8, 2.0), "skin", tag="hand")
        for t in (-0.6, 0.6):
            k.shard(hn, (x + t, 4.6, 1.4), (0, -0.6, 1), 1.6, 0.6, mat="plate", tag="claw")
    k.s.shaders = shaders()
    return k.s, k.parts


MOBS = {
    "cherub_husk": dict(make=cherub_husk, ent=(0.8, 1.3), stats=dict(hp=34, speed=0.36, dmg=8, armor=4, kb=0)),
    "halo_knight": dict(make=halo_knight, ent=(1.8, 4.0), stats=dict(hp=150, speed=0.2, dmg=20, armor=16, kb=1.0)),
    "ash_choir": dict(make=ash_choir, ent=(1.0, 3.4), stats=dict(hp=56, speed=0.22, dmg=10, armor=4, kb=0)),
    "fallen_blade": dict(make=fallen_blade, ent=(0.9, 2.6), stats=dict(hp=50, speed=0.38, dmg=11, armor=6, kb=0)),
    "seraph_warden": dict(make=seraph_warden, ent=(1.4, 3.6), stats=dict(hp=300, speed=0.24, dmg=18, armor=16, kb=0.7), key=True),
    "fallen_seraph": dict(make=fallen_seraph, texel=1, ent=(3.0, 6.4), stats=dict(hp=840, speed=0.24, dmg=26, armor=14, kb=1.0), boss=True),
}
