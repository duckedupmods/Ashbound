"""The Tidewrack: what lives in the open sea, on the reefs, in the surf and up the rivers - not a ship's crew (that's
the Drowned Corsairs) and not the bell-chapel's crabs (the Tide Chapel's), but the deep's own: black-blue hides,
nacre and pearl, sea-glass, violet and orange anemones, and the cold blue-white light of things that live where the
sun never reaches. They come out of the water at night and on stormy days, onto the beaches and up the river banks.

    lamprey_hound   swarm   a sea-hound on four webbed legs: a ring mouth of hooked teeth, a lure on a stalk over
                            its head, fins down its back; packs of them come out of the surf
    merrow          skirm   the fish-folk raider: a shark's head with barbels, a fin crest, nacre plates strapped on
                            and a barbed trident
    reef_knight     guard   a drowned knight's armour that the reef grew into: coral bursting through the joints,
                            anemones on the shoulders, a brain-coral tower shield and a coral-crusted sword
    net_hag         caster  the river hag: hunched under fishing nets full of the bones she's caught, an angler's
                            lure on a long pole, webbed claws
    hullback        brute   a giant in a whale's skull, barnacled hump, dragging a ship's broken keel for a club
    abyss_angler    elite   the merrow lord: tall and gaunt, a great lure arching over its crowned head, a whalebone
                            halberd, a cloak of black kelp

    python tools/monsterforge.py tidewrack --preview ; python tools/mobsheet.py tidewrack
    python tools/connect_check.py tidewrack
"""
import math

import vox2 as X
from vox2 import C, ramp


def Cc(x, y, z, w, h, d):
    """a box by its centre (vox2's C takes its bottom)"""
    return C(x, y - h * 0.5, z, w, h, d)
from serpent_ziggurat import grow
from _folk import lit, legs, arms, held, quad

HIDE = ramp("#05080e", "#0a1018", "#101a26", "#182636", "#223448", "#2e445c")      # black-blue skin
BELLY = ramp("#2a3036", "#3c444a", "#525a60", "#6a7278", "#868c90", "#a4a8aa")     # pale grey under
NACRE = ramp("#262a38", "#383e52", "#4e566c", "#667086", "#7e8aa0", "#9ca8bc")     # mother-of-pearl
GLASS = ramp("#0a2a2e", "#124046", "#1c5a5e", "#2a7676", "#3e9690", "#5cb8aa")     # sea-glass
VIOLET = ramp("#1a0a24", "#2c1238", "#401c50", "#56286a", "#703686", "#8c48a2")    # anemones
ORANGE = ramp("#3a1406", "#5c200a", "#82300e", "#a84416", "#cc5c22", "#ec7c34")    # fire coral
BONE = ramp("#3a3830", "#57544a", "#78746a", "#9a968a", "#bcb8aa", "#dcd8ca")
BARN = ramp("#3e403c", "#5c5e58", "#7c7e76", "#9c9e94", "#bcbcb0")
KELP = ramp("#060a06", "#0c140c", "#121e10", "#1a2a16", "#24381e")
NET = ramp("#2a2418", "#3e3624", "#544a32", "#6c6044", "#867858")
IRON = ramp("#0c0c0e", "#16161a", "#222228", "#303038", "#40404a", "#54545e")
LURE = ramp("#06304a", "#0c5878", "#1a84a8", "#3cb4dc", "#8ee0f8", "#e2faff")     # the deep's cold light
TAR = ramp("#020406", "#06080c", "#0a0e12", "#10141a")


def shaders():
    return {
        "hide": X.wrinkled(HIDE, 0.9),
        "belly": X.surf(BELLY, 0.5, 1.1, 0.16, 0.08, stripe=2),
        "nacre": X.surf(NACRE, 0.6, 1.5, 0.1, 0.26),
        "glass": X.facets(GLASS),
        "violet": X.surf(VIOLET, 0.55, 1.3, 0.26, 0.14),
        "orange": X.surf(ORANGE, 0.55, 1.3, 0.26, 0.16),
        "bone": X.surf(BONE, 0.55, 1.2, 0.16, 0.12, crust=(BARN, 0.22)),
        "barnacle": X.surf(BARN, 0.56, 1.4, 0.3, 0.2, pattern=lambda p, n, i, j, w, h: 0.2 if (i * 3 + j * 5) % 7 == 0 else -0.04),
        "kelp": X.surf(KELP, 0.5, 1.0, 0.3, 0.0, stripe=2, holes=True),
        "net": X.surf(NET, 0.5, 1.1, 0.24, 0.04, pattern=lambda p, n, i, j, w, h: None if (i % 3 and j % 3) else 0.06),
        "iron": X.surf(IRON, 0.5, 1.4, 0.2, 0.22, crust=(BARN, 0.2)),
        "wood": X.surf(KELP, 0.5, 1.0, 0.22, 0.06, stripe=3, crust=(BARN, 0.18)),
        "lure": X.glow(LURE),
        "eye": X.glow(LURE, 0.84, 0.14),
        "dark": X.dark(TAR),
    }


GLOWS = {"lure", "eye"}


def barnacles(k, part, at, n, r, seed=1, z_out=0.6):
    cx, cy, cz = at
    for i in range(n):
        a = (i * 2.399 + seed) % (2 * math.pi)
        d = r * ((i * 0.618 + seed * 0.1) % 1)
        s = 0.7 + ((i * 7 + seed) % 3) * 0.25
        k.box(part, Cc(cx + math.cos(a) * d, cy + math.sin(a) * d * 0.7, cz, s, s, z_out), "barnacle", tag="barnacle")


def anemone(k, part, at, s=1.0, mat="violet", seed=0):
    """a clump of anemone: a stubby foot and a crown of fat tentacles, tips lit"""
    x, y, z = at
    k.blob(part, (x, y + 0.6 * s, z), (1.4 * s, 1.0 * s, 1.4 * s), mat, "anemone", step=0.5)
    for i in range(7):
        a = i * 2 * math.pi / 7 + seed
        tip = (x + math.cos(a) * 2.0 * s, y + 2.4 * s, z + math.sin(a) * 2.0 * s)
        k.limb(part, (x + math.cos(a) * 0.8 * s, y + 1.2 * s, z + math.sin(a) * 0.8 * s), tip, 0.6 * s, mat, "anemone_arm")
        if i % 2 == 0:
            k.box(part, Cc(*tip, 0.5 * s, 0.5 * s, 0.5 * s), "lure", tag="anemone_tip")


def branch(k, part, base, d, s=1.0, mat="orange"):
    """a branch of fire coral bursting out of a joint"""
    bx, by, bz = base
    tip = (bx + d[0] * 3.2 * s, by + d[1] * 3.2 * s, bz + d[2] * 3.2 * s)
    k.limb(part, base, tip, 1.0 * s, mat, "coral")
    for t in (-1, 1):
        k.limb(part, tip, (tip[0] + t * 1.4 * s, tip[1] + 1.6 * s, tip[2] + 0.5 * s), 0.7 * s, mat, "coral")


def lure(k, part, root, over, s=1.0):
    """an angler's lure: a thin rod out of the head, bending over, and a bulb of cold light on the end"""
    rx, ry, rz = root
    mid = (rx + over[0] * 0.4, ry + over[1] * 0.9, rz + over[2] * 0.4)
    end = (rx + over[0], ry + over[1] * 0.7, rz + over[2])
    k.limb(part, root, mid, 0.9 * s, "hide", "lure_rod")
    k.limb(part, mid, end, 0.7 * s, "hide", "lure_rod")
    k.limb(part, end, (end[0], end[1] - 1.6 * s, end[2]), 0.5 * s, "hide", "lure_rod")
    k.blob(part, (end[0], end[1] - 2.6 * s, end[2]), (1.3 * s, 1.5 * s, 1.3 * s), "lure", "lure_bulb", step=0.5)


def fin(k, part, base, h, L, mat="hide", tag="fin", d=0.5):
    """a fin standing up along the spine from `base`, rakes back"""
    bx, by, bz = base
    for i in range(int(L)):
        t = i / max(1, L - 1)
        hh = h * math.sin(math.pi * (0.15 + 0.85 * t)) * (1.0 - 0.4 * t)
        k.box(part, Cc(bx, by + hh * 0.5, bz - i * 1.0 - hh * 0.25, d, hh, 1.1), mat, tag=tag)


def shark_head(k, hd, y, z, s=1.0, crest=True):
    """a shark's head on a biped: a long snout, a wide downturned mouth full of teeth, barbels, small cold eyes"""
    k.box(hd, Cc(0, y + 2.6 * s, z + 0.8 * s, 6.4 * s, 5.2 * s, 7.0 * s), "hide", tag="skull")
    k.box(hd, Cc(0, y + 2.4 * s, z + 5.4 * s, 4.8 * s, 3.6 * s, 3.4 * s), "hide", tag="snout")
    k.box(hd, Cc(0, y - 0.2 * s, z + 3.4 * s, 6.0 * s, 1.6 * s, 6.4 * s), "belly", tag="jaw")
    k.box(hd, Cc(0, y + 0.9 * s, z + 4.4 * s, 5.4 * s, 1.6 * s, 5.0 * s), "dark", tag="mouth")
    k.box(hd, Cc(0, y + 1.0 * s, z + 7.05 * s, 4.6 * s, 0.4 * s, 0.3), "belly", tag="snout_under")
    for i in range(7):
        k.box(hd, Cc(-2.0 * s + i * 0.66 * s, y + 1.3 * s, z + 6.55 * s, 0.4 * s, 1.0 * s, 0.3), "bone", tag="teeth")
        k.box(hd, Cc(-2.0 * s + i * 0.66 * s, y + 0.6 * s, z + 6.45 * s, 0.4 * s, 0.9 * s, 0.3), "bone", tag="teeth")
    for sx in (-1, 1):
        k.box(hd, Cc(sx * 3.25 * s, y + 3.6 * s, z + 3.0 * s, 0.3, 0.8 * s, 1.2 * s), "eye", tag="eye")
        for g in range(3):                          # gill slits
            k.box(hd, Cc(sx * 3.25 * s, y + 1.8 * s, z - 1.2 * s - g * 1.0 * s, 0.3, 2.4 * s, 0.4 * s), "dark", tag="gill")
        k.limb(hd, (sx * 1.6 * s, y + 0.6 * s, z + 5.4 * s), (sx * 2.4 * s, y - 2.6 * s, z + 5.8 * s), 0.5 * s, "hide", "barbel")
    if crest:
        fin(k, hd, (0, y + 5.0 * s, z + 2.0 * s), 4.0 * s, 6, tag="crest")


# ================================================================ the Lamprey Hound (swarm)

def lamprey_hound():
    """The surf's dogs. Long and low on four webbed legs, a hide like wet slate, fins down its back, and no face at
    all: a round mouth ringed with hooked teeth, and above it, on a stalk, the lure it hunts by."""
    k = X.Kit("lamprey_hound")
    body, hd, ab, joints = quad(k, "hide", y=10, chest=((4, 9, 10), (8, 10.4, 11), (12, 9.4, 9.6)), haunch=((4, 8.6, 8.4), (8, 9.4, 9), (11, 8, 8)),
                                leg_w=2.6, foot_w=2.0, front_z=4, back_z=-6, x=4.4, head_at=(0, 11, 5), head_rot=-8, claw="dark", foot_len=4.6)
    k.box(body, Cc(0, 8.0, 0, 7.4, 2.0, 11.0), "belly", tag="belly")
    fin(k, body, (0, 13.4, 4.0), 5.0, 7, tag="back_fin")
    fin(k, ab, (0, 11.6, -3.0), 3.6, 5, tag="back_fin")
    k.limb(ab, (0, 10.0, -10.0), (0, 9.0, -16.0), 3.2, "hide", "tail")
    k.limb(ab, (0, 9.0, -16.0), (0, 10.0, -21.0), 2.0, "hide", "tail")
    k.box(ab, Cc(0, 10.6, -22.4, 0.6, 5.0, 3.0), "hide", tag="tail_fin")
    for sx in (-1, 1):
        for g in range(4):
            k.box(body, Cc(sx * 5.3, 11.0, 4.0 - g * 1.2, 0.3, 3.0, 0.5), "dark", tag="gill")
    # the head: a tube that ends in the ring mouth
    k.stack(hd, 0, 5, [(7.0, 6.4, 6.4), (11.0, 7.6, 7.6), (15.0, 7.0, 7.0)], "hide", "head_tube", step=1.0)
    k.box(hd, Cc(0, 11.0, 11.2, 6.8, 6.8, 1.0), "dark", tag="maw")
    for i in range(12):                              # two rings of hooked teeth
        a = i * 2 * math.pi / 12
        for r, z in ((2.8, 11.6), (1.6, 11.0)):
            k.shard(hd, (math.cos(a) * r, 11.0 + math.sin(a) * r, z), (-math.cos(a) * 0.4, -math.sin(a) * 0.4, 0.6), 1.2, 0.5, mat="bone", tag="teeth")
    for sx in (-1, 1):
        k.box(hd, Cc(sx * 3.6, 13.6, 8.6, 0.3, 0.6, 0.8), "eye", tag="eye")
    lure(k, hd, (0, 14.4, 7.0), (0, 6.0, 6.0), 1.0)
    for i in range(4):
        barnacles(k, body if i < 2 else ab, ((-1) ** i * 3.0, 13.0, 3.0 if i < 2 else -4.0), 4, 1.4, seed=i, z_out=0.6)
    for sx in (-1, 1):                               # webbing between the toes
        for z in (4, -6):
            k.box(body if z > 0 else ab, Cc(sx * 5.0, 0.4, z + 3.0, 4.6, 0.4, 3.0), "hide", tag="web")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


# ================================================================ the Merrow (skirmisher)

def merrow():
    """The fish-folk raider. A shark's head on a man's frame, skin black-blue above and grey beneath, a crest of fin
    from brow to spine, nacre plates strapped to its shoulders and shins, and a barbed trident."""
    k = X.Kit("merrow")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(14, 10.0, 7.0), (20, 10.4, 7.2)], "hide", "hips")
    k.box(hips, Cc(0, 18.8, 0, 11.0, 2.0, 7.8), "kelp", tag="belt")
    for x in (-3.6, 0, 3.6):                         # a kelp kilt
        k.box(hips, Cc(x, 12.6, 3.6, 3.0, 7.0, 0.6), "kelp", tag="kilt")
        k.box(hips, Cc(x, 12.6, -3.6, 3.0, 7.0, 0.6), "kelp", tag="kilt")
    legs(k, hips, 19, 10.4, 3.2, "hide", "hide", knee_mat="nacre", lean=-8, bend=10, w=4.8, cuff=False, toe="dark")
    for side in ("l", "r"):
        sh = k.parts["shin_" + side]
        xx = 3.2 if side == "l" else -3.2
        k.box(sh, Cc(xx, 6.0, 2.6, 4.0, 6.0, 0.8), "nacre", tag="greave")
        k.box(sh, Cc(xx * 1.2, 5.0, -2.0, 0.6, 4.0, 3.0), "hide", tag="ankle_fin")
    to = k.part("torso", (0, 20, 0), (("x", 10),), "hips")
    k.stack(to, 0, 0, [(20, 10.4, 7.2), (26, 12.6, 8.2), (32, 15.0, 9.0), (35, 13.4, 8.0)], "hide", "chest")
    k.box(to, Cc(0, 26.0, 3.8, 9.0, 10.0, 0.8), "belly", tag="belly")
    for y in (23.0, 26.0, 29.0):
        k.box(to, Cc(0, y, 4.3, 8.0, 0.5, 0.3), "dark", tag="belly_fold")
    for sx in (-1, 1):
        for g in range(3):
            k.box(to, Cc(sx * 6.4, 30.0 - g * 1.6, 1.0, 0.3, 1.0, 4.0), "dark", tag="gill")
        k.blob(to, (sx * 7.4, 33.0, 0), (3.4, 1.8, 4.0), "nacre", "pauldron", step=0.6)
        k.box(to, Cc(sx * 7.6, 34.2, 0, 2.0, 0.6, 3.0), "nacre", tag="pauldron_ridge")
        k.limb(to, (sx * 5.6, 34.0, 3.0), (-sx * 3.0, 22.0, 4.2), 1.0, "kelp", "strap", d=0.5)
    fin(k, to, (0, 34.0, -4.0), 4.6, 12, tag="spine_fin")
    hd = k.part("head", (0, 35, 0.4), (("x", -14),), "torso")
    k.limb(hd, (0, 35.0, 0), (0, 37.0, 0.6), 4.4, "hide", "neck")
    shark_head(k, hd, 36.4, 0.6, 1.0)
    arms(k, to, 8.2, 33, "hide", {1: ((("x", -30), ("z", 20)), (("x", -50),)), -1: ((("x", -56), ("z", -10)), (("x", -50),))}, glove="hide", w=3.6)
    for side in ("l", "r"):                          # fins on the forearms, claws
        fo, hn = k.parts["fore_" + side], k.parts["hand_" + side]
        xx = 8.2 if side == "l" else -8.2
        k.box(fo, Cc(xx * 1.1, 20.0, -2.2, 0.5, 4.0, 3.0), "hide", tag="arm_fin")
        for t in (-1.0, 0.0, 1.0):
            k.shard(hn, (xx + t, 18.6, 1.6), (0, -1, 0.4), 1.4, 0.5, mat="dark", tag="claw")
    tr = held(k, "trident", "r", (-8.2, 14.6, 0.3), (("x", 64),))
    k.limb(tr, (-8.2, 2.0, 0.3), (-8.2, 30.0, 0.3), 1.1, "bone", "haft")
    k.box(tr, Cc(-8.2, 30.6, 0.3, 4.6, 1.0, 1.0), "iron", tag="tines_bar")
    for t in (-2.0, 0.0, 2.0):
        k.limb(tr, (-8.2 + t, 31.0, 0.3), (-8.2 + t, 36.0 + (1.2 if t == 0 else 0), 0.3), 0.7, "iron", "tine")
        k.shard(tr, (-8.2 + t, 36.0 + (1.2 if t == 0 else 0), 0.3), (0, 1, 0), 1.6, 0.8, mat="iron", tag="tine_point")
        k.shard(tr, (-8.2 + t, 34.6, 0.3), (-0.2 if t < 0 else 0.2, -1, 0), 1.0, 0.4, mat="iron", tag="barb")
    for y in (8.0, 12.0):
        k.box(tr, Cc(-8.2, y, 0.3, 1.6, 1.0, 1.6), "kelp", tag="wrap")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Reef Knight (guard)

def reef_knight():
    """A knight who went into the sea in full plate a long time ago, and the reef took him. The armour still stands,
    green-black and crusted, and fire coral bursts out of every joint; anemones nest on the shoulders, the visor's
    slit glows with the deep's light, and the shield is one great slab of brain coral."""
    k = X.Kit("reef_knight")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(14, 11.4, 8.0), (20, 11.8, 8.2)], "iron", "faulds")
    for i, x in enumerate((-4.2, -1.4, 1.4, 4.2)):
        k.box(hips, Cc(x, 13.4, 4.2, 2.6, 5.0, 0.8), "iron", tag="tasset")
    legs(k, hips, 19, 10.4, 3.4, "iron", "iron", knee_mat="iron", lean=-4, bend=6, w=5.4)
    for side, nm in ((1, "l"), (-1, "r")):
        branch(k, k.parts["thigh_" + nm], (side * 3.6, 11.4, 3.0), (side * 0.6, 0.4, 0.8), 0.8)
        barnacles(k, k.parts["shin_" + nm], (side * 3.4, 6.0, 3.0), 6, 1.8, seed=side + 2)
    to = k.part("torso", (0, 20, 0), (("x", 4),), "hips")
    k.stack(to, 0, 0, [(20, 11.8, 8.2), (26, 13.4, 9.0), (32, 16.0, 9.6), (35, 14.4, 8.8)], "iron", "breastplate")
    k.box(to, Cc(0, 28.0, 4.6, 1.0, 10.0, 0.6), "iron", tag="ridge")
    branch(k, to, (3.0, 24.0, 4.4), (0.5, 0.6, 0.7), 1.0)
    branch(k, to, (-4.0, 30.0, 4.6), (-0.5, 0.8, 0.5), 0.8)
    barnacles(k, to, (-2.0, 25.0, 4.9), 8, 2.6, seed=4)
    k.box(to, Cc(1.2, 27.6, 4.9, 2.0, 2.0, 0.4), "dark", tag="rust_hole")
    k.box(to, Cc(1.2, 27.6, 5.0, 1.0, 1.0, 0.3), "lure", tag="heart_light")
    for sx in (-1, 1):
        k.blob(to, (sx * 8.4, 33.0, 0), (4.0, 2.4, 4.8), "iron", "pauldron", step=0.6)
        for lame in range(2):
            k.box(to, Cc(sx * 9.4, 30.4 - lame * 1.8, 0, 3.2, 1.2, 8.4), "iron", tag="lame")
        anemone(k, to, (sx * 8.4, 35.0, 0.6 * sx), 1.0, "violet" if sx > 0 else "orange", seed=sx)
    hd = k.part("head", (0, 35, 0.4), (("x", -4),), "torso")
    k.limb(hd, (0, 33.6, 0.2), (0, 36.4, 0.4), 5.4, "iron", "gorget")
    k.box(hd, Cc(0, 38.6, 0.6, 7.0, 7.4, 7.4), "iron", tag="helm")
    k.box(hd, Cc(0, 39.4, 4.4, 6.4, 1.0, 0.4), "dark", tag="visor_slit")
    k.box(hd, Cc(0, 39.4, 4.5, 4.6, 0.5, 0.3), "eye", tag="eye")
    for y in (36.2, 37.4):
        k.box(hd, Cc(0, y, 4.4, 4.0, 0.4, 0.3), "dark", tag="breaths")
    k.box(hd, Cc(0, 42.6, 0.6, 1.0, 1.2, 6.4), "iron", tag="crest_ridge")
    branch(k, hd, (0, 42.6, -1.0), (0.1, 1, -0.4), 1.2)
    branch(k, hd, (2.6, 41.6, 1.6), (0.7, 0.8, 0.2), 0.7)
    barnacles(k, hd, (-2.0, 40.0, 4.4), 4, 1.2, seed=7)
    arms(k, to, 9.0, 33, "iron", {1: ((("x", -40), ("z", 26)), (("x", -60),)), -1: ((("x", -40), ("z", -8)), (("x", -40),))}, glove="iron", w=4.2)
    sh = held(k, "shield", "l", (9.0, 14.6, 0.3), (("x", 100),))
    k.box(sh, Cc(9.0, 14.6, 1.2, 13.0, 22.0, 2.0), "violet", tag="shield")
    k.box(sh, Cc(9.0, 14.6, 0.0, 3.0, 4.0, 1.4), "iron", tag="shield_grip")
    for j in range(9):                               # the brain coral's folds
        k.box(sh, Cc(9.0 + math.sin(j * 1.3) * 2.0, 5.6 + j * 2.3, 2.3, 9.0 - abs(j - 4), 0.9, 0.5), "dark", tag="fold")
    anemone(k, sh, (11.0, 22.0, 2.2), 0.7, "orange", seed=2)
    barnacles(k, sh, (6.0, 8.6, 2.3), 5, 1.8, seed=8)
    sw = held(k, "sword", "r", (-9.0, 14.6, 0.3), (("x", 70),))
    k.limb(sw, (-9.0, 9.4, 0.3), (-9.0, 15.6, 0.3), 1.2, "kelp", "grip")
    k.box(sw, Cc(-9.0, 16.0, 0.3, 1.6, 1.2, 6.0), "iron", tag="guard")
    for i in range(10):
        k.box(sw, Cc(-9.0, 17.4 + i * 2.0, 0.3, 0.8, 2.05, 2.6 - i * 0.08), "iron", tag="blade")
    k.shard(sw, (-9.0, 37.2, 0.3), (0, 1, 0), 2.4, 1.2, mat="iron", tag="blade_tip")
    for y in (20.0, 26.0, 31.0):
        branch(k, sw, (-9.0, y, 1.4), (0.1, 0.4, 0.8), 0.6)
        barnacles(k, sw, (-9.0, y + 1.6, 1.6), 3, 0.8, seed=int(y))
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.08)
    return k.s, k.parts


# ================================================================ the Net Hag (caster)

def net_hag():
    """The thing in the reeds that drags swimmers under. Bent double under a heap of fishing nets, and in the nets
    everything she's caught: skulls, fish bones, a lantern, an oar. Webbed claws, a long grey face, and in one hand a
    pole bent like a fishing rod with a lure of cold light dangling off the end."""
    k = X.Kit("net_hag")
    hips = k.part("hips", (0, 17, 0))
    k.stack(hips, 0, 0, [(10, 11.0, 8.6), (17, 10.4, 8.0)], "kelp", "skirts")
    legs(k, hips, 16, 8.6, 2.8, "hide", "hide", lean=-4, bend=14, w=3.8, cuff=False, toe="dark")
    to = k.part("torso", (0, 17, 0), (("x", 34),), "hips")
    k.stack(to, 0, 0, [(17, 10.0, 7.6), (22, 11.4, 8.6), (27, 11.8, 9.0), (30, 9.6, 7.4)], "belly", "body")
    # the nets: a heap over the hunched back, hanging to the ground behind and down the sides
    k.blob(to, (0, 27.0, -2.6), (8.0, 6.4, 7.4), "net", "net_heap", step=0.9)
    for i in range(7):
        x = -6.0 + i * 2.0
        k.box(to, Cc(x, 18.0, -6.4 - (i % 2), 1.8, 14.0, 0.6), "net", tag="net_hang")
    for (x, y, z), what in (((-3.6, 29.0, -7.0), "skull"), ((3.0, 25.0, -8.0), "skull"), ((0.4, 31.0, -6.4), "fishbone"), ((5.4, 21.0, -6.6), "fishbone")):
        if what == "skull":
            k.box(to, Cc(x, y, z, 3.0, 3.2, 3.0), "bone", tag="caught_skull")
            k.box(to, Cc(x - 0.6, y + 0.4, z - 1.55, 0.8, 0.8, 0.2), "dark", tag="socket")
            k.box(to, Cc(x + 0.6, y + 0.4, z - 1.55, 0.8, 0.8, 0.2), "dark", tag="socket")
        else:
            k.limb(to, (x, y - 3.0, z), (x, y + 3.0, z), 0.6, "bone", "fishbone")
            for t in range(4):
                k.limb(to, (x, y - 2.0 + t * 1.4, z), (x + 1.8, y - 2.6 + t * 1.4, z - 0.4), 0.4, "bone", "fishbone")
    k.limb(to, (-5.0, 22.0, -6.0), (-7.4, 32.0, -6.4), 0.9, "wood", "oar")
    k.box(to, Cc(-7.5, 32.8, -6.4, 2.0, 3.6, 1.0), "wood", tag="oar_blade")
    k.box(to, Cc(4.4, 30.0, -6.6, 2.0, 2.4, 2.0), "iron", tag="lantern")
    k.box(to, Cc(4.4, 30.0, -6.6, 1.2, 1.4, 1.2), "lure", tag="lantern_light")
    hd = k.part("head", (0, 30, 2.6), (("x", -40),), "torso")
    k.box(hd, Cc(0, 31.4, 4.2, 5.0, 7.0, 5.2), "belly", tag="face")
    k.box(hd, Cc(0, 28.0, 5.4, 3.6, 2.4, 3.6), "belly", tag="chin")
    k.box(hd, Cc(0, 29.2, 7.25, 3.0, 0.6, 0.3), "dark", tag="mouth")
    for i in range(5):
        k.box(hd, Cc(-1.2 + i * 0.6, 28.8, 7.3, 0.3, 0.9, 0.3), "bone", tag="teeth")
    for sx in (-1, 1):
        k.box(hd, Cc(sx * 1.3, 33.0, 6.85, 1.4, 1.0, 0.3), "dark", tag="socket")
        k.box(hd, Cc(sx * 1.3, 33.0, 6.9, 0.7, 0.6, 0.3), "eye", tag="eye")
    for i in range(7):                               # lank kelp hair from under the net hood
        a = -1.3 + i * 0.43
        k.limb(hd, (math.sin(a) * 2.6, 35.0, 4.2 + math.cos(a) * 2.2), (math.sin(a) * 3.4, 26.0 - (i % 3), 4.4 + math.cos(a) * 3.0), 0.8, "kelp", "hair")
    k.blob(hd, (0, 35.4, 3.6), (3.6, 1.6, 3.8), "net", "hood", step=0.6)
    arms(k, to, 6.8, 28, "hide", {1: ((("x", -70), ("z", 10)), (("x", -30),)), -1: ((("x", -90), ("z", -14)), (("x", -20),))}, glove="hide", w=2.8, long=1.2)
    for side in ("l", "r"):
        hn = k.parts["hand_" + side]
        xx = 6.8 if side == "l" else -6.8
        for t in (-0.9, 0.0, 0.9):
            k.shard(hn, (xx + t, 13.6, 1.4), (0, -1, 0.5), 2.2, 0.5, mat="dark", tag="claw")
        k.box(hn, Cc(xx, 14.6, 1.2, 2.6, 2.0, 0.3), "hide", tag="web")
    po = held(k, "pole", "r", (-6.8, 13.4, 0.3), (("x", 40),))
    pts = [(-6.8, 4.0, 0.3), (-6.8, 20.0, 0.3), (-6.8, 32.0, 2.4), (-6.8, 38.0, 7.0), (-6.8, 38.6, 12.0)]
    for (a, b), w in zip(zip(pts, pts[1:]), (1.1, 0.9, 0.7, 0.5)):
        k.limb(po, a, b, w, "wood", "pole")
    k.limb(po, (-6.8, 38.6, 12.0), (-6.8, 32.0, 12.4), 0.3, "net", "line")
    k.blob(po, (-6.8, 30.6, 12.4), (1.4, 1.7, 1.4), "lure", "lure_bulb", step=0.5)
    for y in (10.0, 16.0):
        k.box(po, Cc(-6.8, y, 0.3, 1.6, 1.2, 1.6), "net", tag="wrap")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Hullback (brute)

def hullback():
    """A giant of the deep that came up the beach wearing a whale's skull for a helm. Its hump is crusted with
    barnacles like a ship's bottom, its hide hangs in grey folds, and it drags the broken keel of a ship behind it,
    ribs of the hull still pegged on, for a club."""
    k = X.Kit("hullback")
    hips = k.part("hips", (0, 22, 0))
    k.stack(hips, 0, 0, [(15, 15.0, 11.0), (22, 16.4, 12.0)], "hide", "gut")
    k.box(hips, Cc(0, 17.0, 5.6, 12.0, 8.0, 1.2), "belly", tag="belly")
    k.box(hips, Cc(0, 21.0, 0, 16.0, 2.4, 12.4), "net", tag="net_belt")
    legs(k, hips, 21, 11.0, 5.0, "hide", "hide", lean=-4, bend=6, w=7.6, cuff=False, toe="dark", splay=5)
    to = k.part("torso", (0, 22, 0), (("x", 22),), "hips")
    k.stack(to, 0, 0, [(22, 16.4, 12.0), (29, 20.0, 14.0), (35, 22.0, 14.4), (39, 17.0, 12.0)], "hide", "chest")
    k.box(to, Cc(0, 29.0, 6.8, 14.0, 12.0, 1.0), "belly", tag="chest_folds")
    for y in (25.0, 28.0, 31.0, 34.0):
        k.box(to, Cc(0, y, 7.4, 13.0, 0.6, 0.3), "dark", tag="fold")
    # the hump, a ship's bottom of barnacles
    k.blob(to, (0, 37.0, -5.6), (10.0, 7.0, 7.4), "hide", "hump", step=0.9)
    for i in range(5):
        barnacles(k, to, (-6.0 + i * 3.0, 38.0 + (i % 2) * 2.0, -12.4), 7, 2.4, seed=i * 3, z_out=1.0)
    for sx in (-1, 1):
        k.blob(to, (sx * 11.0, 37.0, 0), (5.0, 4.0, 5.6), "hide", "shoulder", step=0.8)
        barnacles(k, to, (sx * 11.0, 40.0, 0), 6, 2.6, seed=sx + 9)
    hd = k.part("head", (0, 38, 4.0), (("x", -10),), "torso")
    k.limb(hd, (0, 37.0, 3.0), (0, 40.0, 5.6), 7.0, "hide", "neck")
    # the whale skull helm: a long flat snout of bone, eye-holes, the dark face inside
    k.box(hd, Cc(0, 43.0, 5.6, 10.0, 7.0, 9.0), "bone", tag="skull_vault")
    k.box(hd, Cc(0, 41.4, 13.0, 8.4, 3.0, 9.0), "bone", tag="skull_snout")
    k.box(hd, Cc(0, 41.0, 19.4, 6.0, 2.2, 4.4), "bone", tag="skull_beak")
    k.box(hd, Cc(0, 40.6, 22.4, 3.6, 1.6, 2.0), "bone", tag="skull_beak")
    k.box(hd, Cc(0, 39.4, 15.0, 7.0, 1.0, 9.0), "bone", tag="skull_jaw_top")
    for sx in (-1, 1):
        k.box(hd, Cc(sx * 4.6, 43.0, 8.6, 1.2, 2.6, 3.0), "dark", tag="socket")
        k.box(hd, Cc(sx * 4.8, 43.0, 8.6, 1.0, 1.0, 1.4), "eye", tag="eye")
        k.limb(hd, (sx * 4.0, 46.0, 3.0), (sx * 7.6, 49.0, -1.4), 1.6, "bone", "skull_horn")
    k.box(hd, Cc(0, 38.6, 9.4, 8.0, 3.0, 4.0), "dark", tag="face_under")
    for i in range(6):
        k.box(hd, Cc(-3.0 + i * 1.2, 38.2, 11.4, 0.7, 1.4, 0.4), "bone", tag="baleen")
    barnacles(k, hd, (2.0, 45.0, 10.2), 5, 1.6, seed=13)
    arms(k, to, 12.6, 37, "hide", {1: ((("x", -16), ("z", 18)), (("x", -30),)), -1: ((("x", -30), ("z", -6)), (("x", -40),))}, glove="hide", w=6.4, long=1.3)
    for side in ("l", "r"):
        hn = k.parts["hand_" + side]
        xx = 12.6 if side == "l" else -12.6
        for t in (-1.6, 0.0, 1.6):
            k.shard(hn, (xx + t, 12.2, 2.2), (0, -1, 0.5), 2.0, 0.9, mat="dark", tag="claw")
    kl = held(k, "keel", "r", (-12.6, 13.8, 0.3), (("x", 84),))
    k.limb(kl, (-12.6, 8.0, 0.3), (-12.6, 40.0, 0.3), 3.4, "wood", "keel")
    for i in range(5):                               # the hull's ribs still pegged on
        y = 20.0 + i * 4.4
        for sz in (-1, 1):
            k.limb(kl, (-12.6, y, 0.3), (-12.6 + 1.6, y + 3.0, 0.3 + sz * 5.4), 1.2, "wood", "hull_rib")
    k.box(kl, Cc(-12.6, 41.0, 0.3, 4.6, 2.4, 4.6), "iron", tag="keel_shoe")
    barnacles(k, kl, (-12.6, 32.0, 2.2), 8, 3.0, seed=21, z_out=0.8)
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.12)
    return k.s, k.parts


# ================================================================ the Abyss Angler (elite)

def abyss_angler():
    """The merrow lord. Taller and leaner than its raiders, black as the trench it came out of, a crown of nacre and
    sea-glass on a long shark's head, and over that head a great lure on a jointed rod, arching forward and blazing
    cold. A cloak of black kelp, a breastplate of a giant shell, and a halberd made of a whale's jaw."""
    k = X.Kit("abyss_angler")
    hips = k.part("hips", (0, 22, 0))
    k.stack(hips, 0, 0, [(15, 10.6, 7.4), (22, 11.0, 7.6)], "hide", "hips")
    k.box(hips, Cc(0, 20.6, 0, 11.6, 2.0, 8.2), "nacre", tag="belt")
    k.box(hips, Cc(0, 13.6, 4.1, 5.0, 10.0, 0.6), "kelp", tag="tabard")
    legs(k, hips, 21, 11.4, 3.4, "hide", "hide", knee_mat="nacre", lean=-6, bend=8, w=4.8, cuff=False, toe="dark")
    for side in ("l", "r"):
        xx = 3.4 if side == "l" else -3.4
        k.box(k.parts["shin_" + side], Cc(xx, 6.4, 2.6, 4.2, 7.0, 0.8), "nacre", tag="greave")
    to = k.part("torso", (0, 22, 0), (("x", 6),), "hips")
    k.stack(to, 0, 0, [(22, 11.0, 7.6), (29, 13.4, 8.6), (35, 16.6, 9.4), (38, 14.4, 8.4)], "hide", "chest")
    # the shell breastplate, ribbed like a scallop
    for i in range(7):
        a = (i - 3) * 0.26
        k.box(to, Cc(math.sin(a) * 5.0, 30.0, 4.4 + math.cos(a) * 0.6, 1.8, 12.0 - abs(i - 3) * 1.4, 0.8), "nacre", tag="shell_rib")
    for sx in (-1, 1):
        k.blob(to, (sx * 8.4, 36.0, 0), (3.8, 2.2, 4.4), "nacre", "pauldron", step=0.6)
        k.box(to, Cc(sx * 8.6, 37.4, 0, 1.4, 1.4, 1.4), "glass", tag="pauldron_gem")
    # the cloak of black kelp, from the shoulders to the heels, torn
    for i in range(8):
        x = -7.0 + i * 2.0
        k.box(to, Cc(x, 22.0, -5.2 - abs(i - 3.5) * 0.3, 2.2, 30.0 - (i % 3) * 3.0, 0.7), "kelp", tag="cloak")
    fin(k, to, (0, 38.0, -4.4), 3.4, 8, tag="spine_fin")
    hd = k.part("head", (0, 38, 0.4), (("x", -8),), "torso")
    k.limb(hd, (0, 38.0, 0), (0, 40.2, 0.6), 4.4, "hide", "neck")
    shark_head(k, hd, 39.8, 0.6, 1.15, crest=False)
    # the crown: nacre points and sea-glass between them
    for i in range(7):
        a = (i - 3) * 0.5
        x, z = math.sin(a) * 3.4, math.cos(a) * 3.4 + 0.6 - 2.0
        k.shard(hd, (x, 46.0, z), (0, 1, 0), 2.4 + (1.6 if i == 3 else 0), 0.9, mat="nacre", tag="crown")
        if i % 2:
            k.box(hd, Cc(x, 46.4, z, 0.9, 0.9, 0.9), "glass", tag="crown_gem")
    k.box(hd, Cc(0, 45.6, -1.4, 7.6, 1.2, 5.8), "nacre", tag="crown_band")
    # the great lure, arching forward over the crown
    pts = [(0, 46.0, -3.0), (0, 53.0, -3.4), (0, 58.0, 0.6), (0, 59.0, 6.0), (0, 56.4, 10.4)]
    for (a, b), w in zip(zip(pts, pts[1:]), (1.6, 1.3, 1.0, 0.8)):
        k.limb(hd, a, b, w, "hide", "lure_rod")
    for p in pts[1:4]:
        k.box(hd, Cc(p[0], p[1], p[2], 1.4, 1.4, 1.4), "nacre", tag="lure_joint")
    k.limb(hd, (0, 56.4, 10.4), (0, 54.0, 10.6), 0.5, "hide", "lure_rod")
    k.blob(hd, (0, 52.0, 10.6), (2.2, 2.6, 2.2), "lure", "lure_bulb", step=0.5)
    for i in range(4):
        a = i * math.pi / 2
        k.shard(hd, (math.cos(a) * 1.6, 52.0, 10.6 + math.sin(a) * 1.6), (math.cos(a), 0.2, math.sin(a)), 1.4, 0.4, mat="lure", tag="lure_spine")
    arms(k, to, 9.0, 36, "hide", {1: ((("x", -24), ("z", 22)), (("x", -40),)), -1: ((("x", -60), ("z", -8)), (("x", -40),))}, glove="hide", w=3.8, long=1.15)
    for side in ("l", "r"):
        hn = k.parts["hand_" + side]
        xx = 9.0 if side == "l" else -9.0
        for t in (-1.0, 0.0, 1.0):
            k.shard(hn, (xx + t, 16.4, 1.6), (0, -1, 0.4), 1.8, 0.5, mat="dark", tag="claw")
    ha = held(k, "halberd", "r", (-9.0, 16.0, 0.3), (("x", 66),))
    k.limb(ha, (-9.0, 0.0, 0.3), (-9.0, 40.0, 0.3), 1.3, "bone", "haft")
    for y in (6.0, 12.0, 30.0):
        k.box(ha, Cc(-9.0, y, 0.3, 1.8, 1.2, 1.8), "kelp", tag="wrap")
    # the blade: a whale's jawbone, curved, teeth set along its edge
    for i in range(8):
        t = i / 7.0
        k.box(ha, Cc(-9.0, 34.0 + i * 1.6, 2.4 + math.sin(t * math.pi) * 2.8, 1.0, 1.8, 4.6 - t * 2.0), "bone", tag="jaw_blade")
        if i % 2 == 0:
            k.shard(ha, (-9.0, 34.0 + i * 1.6, 2.4 + math.sin(t * math.pi) * 2.8 + (4.6 - t * 2.0) * 0.5 - 0.3), (0, 0.2, 1), 1.4, 0.5, mat="bone", tag="jaw_tooth")
    k.shard(ha, (-9.0, 41.0, 0.3), (0, 1, 0), 3.6, 1.0, mat="glass", tag="spike")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.12)
    return k.s, k.parts


MOBS = {
    "lamprey_hound": dict(make=lamprey_hound, rig="crawler", ent=(1.3, 1.2), stats=dict(hp=30, speed=0.32, dmg=6, armor=2, kb=0)),
    "merrow": dict(make=merrow, ent=(0.8, 2.9), stats=dict(hp=46, speed=0.31, dmg=8, armor=4, kb=0)),
    "reef_knight": dict(make=reef_knight, ent=(1.0, 3.2), stats=dict(hp=80, speed=0.21, dmg=10, armor=12, kb=0.5)),
    "net_hag": dict(make=net_hag, ent=(0.9, 2.5), stats=dict(hp=38, speed=0.24, dmg=7, armor=2, kb=0)),
    "hullback": dict(make=hullback, ent=(1.9, 4.2), stats=dict(hp=200, speed=0.19, dmg=19, armor=7, kb=1.0)),
    "abyss_angler": dict(make=abyss_angler, ent=(1.1, 3.8), stats=dict(hp=360, speed=0.25, dmg=16, armor=11, kb=0.6), key=True),
}
