"""The Rookery's monsters, each built by hand (tools/vox2.py). The black tower on the hill where the crows were fed
on the hanged until they grew big enough to want more: black feathers with a blue-violet sheen, bone and beaks, old
iron, the cold violet light of the omens.

    carrion_crow       swarm   a crow grown to a man's waist, walking: hooked beak, ragged wings, talons, a skull in its claws
    crowbrute          brute   a hulk in a coat of feathers, an iron birdcage for a helm with crows nesting in it, a cage-flail
    augur              caster  the reader of entrails: a long bird-skull mask, eyes sewn shut, a crow on his staff
    feather_blade      skirm   the rookery's knife: a cloak of wings, a beak mask, sickle blades like talons
    rook_captain       elite   the black knight of the tower: beaked visor, feathered pauldrons, a crow shield, a falchion
    raven_mother       boss    the great raven, half a woman: wings like sails, a skull crowned in quills, a nest of eggs on her back

    python tools/monsterforge.py rookery --preview ; python tools/mobsheet.py rookery
"""
import math

import vox2 as X
from vox2 import C, ramp

FEATHER = ramp("#06060a", "#0c0c14", "#14141e", "#1c1c2a", "#262638", "#323248", "#40405a")
SHEEN = ramp("#141230", "#1e1a46", "#2a245c", "#383070")
BONE = ramp("#3a3428", "#5a5240", "#7c7258", "#9e9476", "#c0b896", "#dcd6b8")
BEAK = ramp("#08080a", "#121216", "#1c1c22", "#28282e", "#36363e")
IRON = ramp("#0c0c0e", "#16161a", "#222228", "#303038", "#40404a", "#54545e")
RUST = ramp("#2a1408", "#44200c", "#5e2e12", "#7a3e18")
OMEN = ramp("#3a0a6a", "#6a1aaa", "#9a44e0", "#c890ff", "#f0e0ff")
CLOTH = ramp("#0e0c12", "#18141e", "#221e2a", "#2e2838", "#3c3448")
SKIN = ramp("#2a2428", "#3e3438", "#544a4c", "#6c6062", "#867a7a")
LEATHER = ramp("#120c08", "#1e140c", "#2c1e12", "#3c2a1a", "#4e3822")
GORE = ramp("#1e0406", "#3a080a", "#5a1012", "#7e1a1a")
STRAW = ramp("#1e180a", "#2e2410", "#423418", "#584620", "#6e5a2a")


def feathers(R, S):
    """black feathers in rows: each row a dark line at its base, a sheen of violet on the lit edge"""
    def f(p, n, b, key, i, j, w, h, fr):
        x, y, z = p
        v = 0.42 + 0.2 * n[1] + 0.2 * (X.fbm(x * 0.5, y * 0.5, z * 0.5) - 0.5) + 0.14 * ((j % 3) / 2.0)
        if j % 3 == 0:
            v -= 0.16
        if (i * 3 + j * 5) % 13 == 0 and n[1] > 0.2:
            return X.shade(S, 0.5 + 0.3 * n[1], i, j)
        return X.shade(R, v, i, j)
    return f


def shaders():
    return {
        "feather": feathers(FEATHER, SHEEN),
        "quill": X.surf(FEATHER, 0.5, 1.2, 0.2, 0.12, stripe=2),
        "bone": X.surf(BONE, 0.6, 1.1, 0.16, 0.12),
        "beak": X.surf(BEAK, 0.55, 1.6, 0.1, 0.3),
        "iron": X.surf(IRON, 0.5, 1.4, 0.16, 0.18, rust=(RUST, 0.1, 0.4)),
        "steel": X.surf(IRON, 0.66, 1.4, 0.08, 0.3),
        "glow": X.glow(OMEN),
        "eye": X.glow(OMEN, 0.8, 0.16),
        "cloth": X.surf(CLOTH, 0.48, 1.0, 0.24, 0.0, holes=True),
        "skin": X.wrinkled(SKIN, 0.8),
        "leather": X.surf(LEATHER, 0.5, 1.1, 0.2, 0.06),
        "gore": X.surf(GORE, 0.5, 1.0, 0.2, 0.0),
        "straw": X.surf(STRAW, 0.5, 1.0, 0.3, 0.0, stripe=2),
        "dark": X.dark(FEATHER),
    }


def fan(k, part, root, dirs, length, w, mat="feather", tag="feather", taper=0.5):
    """a spray of long feathers out of one root: dirs = [(dx, dy, dz), ...]"""
    for i, d in enumerate(dirs):
        n = math.sqrt(sum(c * c for c in d))
        L = length * (1.0 - 0.12 * (i % 3))
        tip = tuple(root[a] + d[a] / n * L for a in range(3))
        mid = tuple(root[a] + d[a] / n * L * 0.6 for a in range(3))
        k.limb(part, root, mid, w, mat, tag, d=w * 0.35)
        k.limb(part, mid, tip, w * taper, mat, tag, d=w * 0.3)


def wing(k, part, shoulder, side, span, drop, w=3.0, n=9, z=-1.0):
    """a wing hung off an arm: primaries fanning down and out from the wrist, coverts over the top"""
    sx, sy, sz = shoulder
    wrist = (sx + side * span, sy - drop * 0.25, sz + z)
    k.limb(part, shoulder, wrist, w * 0.9, "feather", "wing_bone", d=w * 0.7)
    dirs = [(side * (0.9 - i * 0.1), -0.25 - i * 0.12, -0.1) for i in range(n)]
    fan(k, part, wrist, dirs, drop, w * 0.8, tag="primary")
    for i in range(5):
        t = (i + 0.5) / 5
        at = tuple(shoulder[a] + (wrist[a] - shoulder[a]) * t for a in range(3))
        k.limb(part, at, (at[0] + side * 1.0, at[1] - drop * (0.5 + 0.1 * i), at[2] - 0.3), w * 0.7, "feather", "secondary", d=w * 0.3)


def talons(k, part, at, side=1, s=1.0, mat="beak"):
    x, y, z = at
    for dx, dz in ((-1.0, 1.0), (0, 1.3), (1.0, 1.0), (0, -1.0)):
        tip = (x + dx * 1.8 * s, y - 0.6 * s, z + dz * 2.4 * s)
        k.limb(part, (x, y, z), tip, 0.9 * s, "skin", "toe")
        k.shard(part, tip, (dx * 0.5, -1, dz * 0.8), 1.6 * s, 0.7 * s, mat=mat, tag="foot")


# ================================================================ the Raven Mother (boss)

def raven_mother():
    """The first crow of the Rookery, fed on the hanged until she was the size of the tower's door, and then on the
    hangmen. She stands on legs like a heron's ending in talons that span a cart; from the waist up she is half a
    woman, feathered, with long arms that are her wings - the primaries hang from her wrists to the ground, and
    she can open them across the whole hall. Her head is a raven's skull, white bone, the beak a yard long, with
    a crown of black quills and a third eye in the brow. On her back a nest of gallows rope and straw with three
    eggs in it, and the eggs glow."""
    k = X.Kit("raven_mother")
    hips = k.part("hips", (0, 42, 0))
    k.blob(hips, (0, 42, -1), (12, 7, 10), "feather", "body")
    fan(k, hips, (0, 40, -9), [(dx, -0.3, -1) for dx in (-0.6, -0.3, 0, 0.3, 0.6)], 22, 4.0, tag="tail")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 6
        th = k.part("thigh_" + nm, (x, 38, 0), (("x", -24), ("z", side * 6)), "hips")
        sh = k.part("shin_" + nm, (x, 24, 0), (("x", 40),), th)
        ft = k.part("foot_" + nm, (x, 4, 0), (("x", -16),), sh)
        k.blob(th, (x, 32, 0), (6, 8, 6.4), "feather", "thigh")
        k.limb(sh, (x, 24, 0), (x, 4, 0), 3.2, "skin", "shank")
        for y in range(6, 24, 3):
            k.box(sh, C(x, y, 1.4, 3.6, 1.2, 1.0), "skin", tag="scale")
        talons(k, ft, (x, 3.0, 0), side, s=2.4)
    # ---------------------------------------------------------------- torso: half a woman, feathered, a ruff of quills
    to = k.part("torso", (0, 44, 0), (("x", 14),), "hips")
    k.stack(to, 0, 0, [(44, 20, 14), (50, 18, 13), (56, 22, 14), (62, 26, 15)], "feather", "torso")
    k.box(to, C(0, 49, 5.2, 9, 10, 1.4), "skin", tag="breast")
    for y in (50.4, 52.4, 54.4):
        k.box(to, C(0, y, 5.9, 8, 0.5, 0.6), "dark", tag="rib")
    for i in range(16):      # the ruff: quills standing round the neck
        a = math.radians(-160 + i * 20)
        k.shard(to, (math.sin(a) * 9, 62, math.cos(a) * 6), (math.sin(a) * 0.8, 1.0, math.cos(a) * 0.6), 9 + (i % 3) * 2, 2.0,
                mat="quill", tag="ruff")
    # the nest on her back: a ring of rope and straw, three glowing eggs
    k.ring(to, 0, 60, -11, 7.0, 3.0, "straw", "nest", n=14, axis="y")
    k.ring(to, 0, 62, -11, 5.4, 2.4, "straw", "nest", n=12, axis="y")
    for (x, z, s) in ((-2.4, -10, 1.0), (2.2, -12.4, 0.9), (0.4, -8.4, 0.8)):
        k.blob(to, (x, 63, z), (2.4 * s, 3.2 * s, 2.4 * s), "glow", "egg", step=0.8)
    for (a, L) in ((20, 9), (110, 7), (200, 8), (290, 10)):
        r = math.radians(a)
        k.limb(to, (math.cos(r) * 6, 60, -11 + math.sin(r) * 6), (math.cos(r) * 10, 54 - L * 0.4, -11 + math.sin(r) * 10), 1.0, "straw", "noose")
    # ---------------------------------------------------------------- the head: a raven skull, a yard of beak, a crown of quills
    hd = k.part("head", (0, 63, 2), (("x", -16),), "torso")
    k.blob(hd, (0, 69, 2), (5.6, 5.6, 6.2), "bone", "skull")
    k.box(hd, C(0, 66.6, 7.6, 5.0, 4.4, 5.0), "bone", tag="beak_root")
    k.shard(hd, (0, 68.8, 9.6), (0, -0.5, 1), 22, 4.6, mat="bone", tag="beak")
    k.shard(hd, (0, 66.2, 9.6), (0, -0.4, 1), 16, 3.2, mat="bone", tag="beak")
    for sx in (-3.0, 3.0):
        k.box(hd, C(sx, 69.8, 6.2, 2.4, 2.4, 1.6), "dark", tag="socket")
        k.box(hd, C(sx, 70.2, 6.8, 1.6, 1.4, 0.8), "eye", group="glow", tag="eye")
    k.box(hd, C(0, 73.2, 7.6, 1.8, 2.6, 0.8), "eye", group="glow", tag="third_eye")
    for i in range(9):       # the crown of quills
        a = math.radians(-80 + i * 20)
        k.shard(hd, (math.sin(a) * 4.0, 73, 2 + math.cos(a) * 3.6), (math.sin(a) * 0.5, 1, -0.4), 12 + 4 * (i % 2), 1.8,
                mat="quill", tag="crown")
    # ---------------------------------------------------------------- arms: long and bare, hooked claws
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 11
        up = k.part("arm_" + nm, (x, 60, 0), (("x", -30), ("z", side * 16)), "torso")
        fo = k.part("fore_" + nm, (x, 44, 0), (("x", -30),), up)
        hn = k.part("hand_" + nm, (x, 28, 0), (), fo)
        k.stack(up, x, 0, [(44, 6, 6), (52, 7, 7), (60, 8, 8)], "feather", "upper_arm")
        k.stack(fo, x, 0, [(28, 4.4, 4.4), (36, 5.4, 5.4), (44, 5.8, 5.8)], "skin", "forearm")
        k.box(hn, C(x, 23, 0.4, 4.4, 5.0, 4.4), "skin", tag="hand")
        for t in (-1.4, 0, 1.4):
            k.shard(hn, (x + t, 23.4, 1.0), (t * 0.1, -1, 0.4), 7.0, 1.0, mat="beak", tag="claw")
        k.blob(up, (x, 58, 0), (5.6, 4.0, 5.6), "feather", "shoulder")
    # the wings, out of her back: a bone arm up and out to the wrist, a wall of feathers hanging off it, primaries fanned
    for side in (1, -1):
        root, elbow, wrist, tip = (side * 6, 60, -8), (side * 20, 76, -12), (side * 36, 82, -14), (side * 52, 70, -16)
        for p0, p1, w in ((root, elbow, 4.6), (elbow, wrist, 3.6), (wrist, tip, 2.6)):
            k.limb(to, p0, p1, w, "feather", "wing_bone", d=w * 0.8)
        for i in range(14):              # secondaries off the bone, longest at the wrist
            u = i / 13.0
            seg = (root, elbow) if u < 0.4 else (elbow, wrist)
            v = u / 0.4 if u < 0.4 else (u - 0.4) / 0.6
            at = tuple(seg[0][c] + (seg[1][c] - seg[0][c]) * v for c in range(3))
            L = 24 + 22 * u
            k.limb(to, at, (at[0] + side * 3, at[1] - L, at[2] - 2), 5.4, "feather", "secondary", d=0.9)
        fan(k, to, wrist, [(side * (1.0 - i * 0.12), -0.3 - i * 0.16, -0.1) for i in range(9)], 40, 5.4, tag="primary")
        fan(k, to, elbow, [(side * 0.6, -1, -0.2), (side * 0.9, -0.8, -0.2), (side * 0.3, -1, -0.3)], 18, 5.0, tag="covert")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Rook Captain (elite, the key)

def rook_captain():
    """The captain of the tower's guard, who feeds the condemned to the birds. Black plate, every edge filed to a
    point, pauldrons sheathed in long black feathers; his helm is drawn out into a crow's beak, the visor a slit
    of violet light. A tall kite shield with a crow in bone nailed to it; a heavy falchion; and on his belt the
    keys to the hanging-cage."""
    k = X.Kit("rook_captain")
    hips = k.part("hips", (0, 21, 0))
    k.stack(hips, 0, 0, [(16, 12, 8), (21, 12.4, 8.2)], "iron", "faulds")
    for x in (-4.0, 0, 4.0):
        k.box(hips, C(x, 12.0, 4.4, 4.0, 6.4, 0.8), "iron", tag="tasset")
        k.shard(hips, (x, 12.0, 4.6), (0, -1, 0.1), 2.6, 3.0, mat="iron", tag="tasset_point")
    k.ring(hips, 6.6, 15, 1.6, 1.8, 0.5, "iron", "keyring", n=8)
    for dx, L in ((-0.6, 3.6), (0.6, 4.4)):
        k.box(hips, C(6.6 + dx, 13.2 - L * 0.5, 1.8, 0.5, L, 0.4), "steel", tag="key")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 3.2
        th = k.part("thigh_" + nm, (x, 20, 0), (("x", -6), ("z", side * 5)), "hips")
        sh = k.part("shin_" + nm, (x, 10.6, 0), (("x", 10),), th)
        ft = k.part("foot_" + nm, (x, 2.4, 0), (("x", -4),), sh)
        k.box(th, C(x, 10.8, 0, 5.0, 9.4, 5.4), "iron", tag="cuisse")
        k.box(th, C(x, 9.6, 1.0, 5.6, 3.0, 5.0), "iron", tag="poleyn")
        k.shard(th, (x, 10.8, 3.6), (0, 0.4, 1), 2.6, 1.6, mat="steel", tag="poleyn")
        k.box(sh, C(x, 2.4, 0, 5.0, 8.4, 5.4), "iron", tag="greave")
        k.box(ft, C(x, 0, 1.6, 5.4, 2.8, 8.6), "iron", tag="foot")
        k.shard(ft, (x, 0.8, 5.8), (0, 0, 1), 2.6, 2.6, mat="iron", tag="foot")
    cl = k.part("cloak", (0, 35, -4.6), (("x", -4),), "hips", bone=False)
    fan(k, cl, (0, 35, -5), [(dx, -1, -0.12) for dx in (-0.4, -0.2, 0, 0.2, 0.4)], 33, 4.0, tag="feather_cloak")
    # ---------------------------------------------------------------- torso: black plate, a bone crow on the breast
    to = k.part("torso", (0, 21, 0), (("x", 6),), "hips")
    k.stack(to, 0, 0, [(21, 12.4, 8.0), (27, 15.0, 9.0), (32, 17.0, 9.6), (35.6, 15.4, 8.6)], "iron", "cuirass")
    k.box(to, C(0, 23, 5.0, 1.2, 12, 0.8), "steel", tag="ridge")
    for sx in (-1, 1):       # the bone crow, wings spread across the chest
        k.limb(to, (0, 30, 5.2), (sx * 6, 31.6, 5.0), 1.2, "bone", "crow_wing", d=0.6)
        k.limb(to, (sx * 6, 31.6, 5.0), (sx * 7.4, 28.6, 4.8), 1.0, "bone", "crow_wing", d=0.6)
    k.box(to, C(0, 27.6, 5.2, 2.0, 4.4, 0.8), "bone", tag="crow_body")
    k.box(to, C(0, 31.4, 5.4, 1.6, 1.6, 1.2), "bone", tag="crow_head")
    for side in (1, -1):     # pauldrons sheathed in feathers, filed to points
        sx = side * 9.6
        k.blob(to, (sx, 34.6, 0), (5.4, 3.4, 5.6), "iron", "pauldron")
        fan(k, to, (sx, 36, 0), [(side * 1, -0.3 - i * 0.18, (i - 2) * 0.35) for i in range(5)], 9, 2.4, tag="pauldron_feather")
        k.shard(to, (sx + side * 2, 37.4, 0), (side * 0.4, 1, 0), 5.0, 2.0, mat="steel", tag="pauldron_spike")
    # ---------------------------------------------------------------- the helm: drawn into a crow's beak
    hd = k.part("head", (0, 35.6, 0.4), (("x", -6),), "torso")
    k.box(hd, C(0, 35.4, 0.0, 6.8, 7.6, 7.0), "iron", tag="helm")
    k.box(hd, C(0, 36.4, 4.2, 5.2, 4.6, 3.0), "iron", tag="beak_root")
    k.shard(hd, (0, 38.0, 5.6), (0, -0.45, 1), 8.0, 4.4, mat="iron", tag="beak")
    k.box(hd, C(0, 40.0, 3.55, 6.0, 1.0, 0.4), "dark", tag="visor")
    for sx in (-1.6, 1.6):
        k.box(hd, C(sx, 40.1, 3.65, 1.8, 0.7, 0.3), "eye", group="glow", tag="eye")
    for i in range(5):
        k.shard(hd, (0, 42.6, 1.6 - i * 1.4), (0, 1 - i * 0.12, -0.6), 5.0 - i * 0.4, 1.4, mat="quill", tag="crest")
    # ---------------------------------------------------------------- arms
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 9.4
        up = k.part("arm_" + nm, (x, 33, 0), (("x", -50 if side > 0 else -30), ("z", side * 10)), "torso")
        fo = k.part("fore_" + nm, (x, 24, 0), (("x", -50 if side > 0 else -60),), up)
        hn = k.part("hand_" + nm, (x, 15.6, 0), (), fo)
        k.box(up, C(x, 24.8, 0, 4.6, 8.6, 4.8), "iron", tag="rerebrace")
        k.box(fo, C(x, 16.4, 0, 4.6, 8.0, 4.8), "iron", tag="vambrace")
        k.shard(fo, (x + side * 2.4, 20, 0), (side * 1, 0.3, -0.4), 3.0, 1.4, mat="steel", tag="elbow_spike")
        k.box(hn, C(x, 12.6, 0.4, 4.4, 3.8, 4.4), "iron", tag="gauntlet")
    # the kite shield on the left: black, a bone crow nailed to it
    sh = k.part("shield", (12.4, 15, 2), (("y", 10),), k.parts["hand_l"])
    k.box(sh, C(12.4, 10, 2, 1.4, 20, 12), "iron", tag="shield")
    k.shard(sh, (12.4, 10, 2), (0, -1, 0), 8, 8.0, mat="iron", tag="shield")
    k.box(sh, C(12.4, 29.4, 2, 1.8, 1.2, 12.6), "steel", tag="shield_rim")
    k.box(sh, C(13.3, 18, 2, 0.6, 7, 2.4), "bone", tag="shield_crow")
    for sz in (-1, 1):
        k.limb(sh, (13.3, 24, 2), (13.3, 25.6, 2 + sz * 5), 1.2, "bone", "shield_crow", d=0.6)
    k.box(sh, C(13.3, 24.4, 2, 0.6, 2.0, 1.6), "bone", tag="shield_crow")
    # the falchion on the right
    fl = k.part("falchion", (-9.4, 13.6, 0.6), (("x", 80),), k.parts["hand_r"])
    k.box(fl, C(-9.4, 10.6, 0.6, 1.4, 5.0, 1.4), "leather", tag="grip")
    k.box(fl, C(-9.4, 15.6, 0.6, 1.6, 1.2, 7.0), "steel", tag="guard")
    for i, (dy, dz, wd) in enumerate(((0, 0, 3.0), (5, 0.4, 3.6), (10, 1.0, 4.4), (15, 1.8, 4.8), (19, 2.6, 3.6))):
        k.box(fl, C(-9.4, 16.8 + dy, 0.6 + dz, 0.8, 5.2, wd), "steel", tag="blade")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Crowbrute (brute)

def crowbrute():
    """The tower's labourer, who carries the bodies up to the birds. A hulk in a coat of stitched crow feathers,
    bare grey arms like posts; his head is locked in an iron birdcage, and the crows have nested in it with him -
    you can see them in there, and his eyes between. He swings a flail of three hanging-cages on chains."""
    k = X.Kit("crowbrute")
    hips = k.part("hips", (0, 22, 0))
    k.stack(hips, 0, 0, [(15, 16, 11), (22, 16, 11)], "feather", "coat")
    for i, x in enumerate((-6, -2, 2, 6)):
        k.box(hips, C(x, 4 + (i % 2) * 2, 5.4, 3.6, 13, 0.8), "feather", tag="coat_skirt")
        k.box(hips, C(x, 4 + ((i + 1) % 2) * 2, -5.4, 3.6, 13, 0.8), "feather", tag="coat_skirt")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 4.6
        th = k.part("thigh_" + nm, (x, 20, 0), (("x", -10), ("z", side * 8)), "hips")
        sh = k.part("shin_" + nm, (x, 11, 0), (("x", 14),), th)
        ft = k.part("foot_" + nm, (x, 3, 0), (("x", -4),), sh)
        k.box(th, C(x, 11, 0, 7.0, 9.4, 7.4), "leather", tag="thigh")
        k.box(sh, C(x, 3, 0, 7.0, 8.4, 7.4), "leather", tag="boot")
        k.ring(sh, x, 7, 0, 4.0, 0.8, "iron", "strap", n=10, axis="y")
        k.box(ft, C(x, 0, 1.6, 7.6, 3.2, 10.4), "leather", tag="foot")
    # ---------------------------------------------------------------- torso: a slab, hunched, a sack of bodies' things
    to = k.part("torso", (0, 22, 0), (("x", 18),), "hips")
    k.stack(to, 0, 0, [(22, 16, 11), (29, 22, 13), (35, 26, 14), (39, 24, 12)], "feather", "coat")
    k.blob(to, (0, 38, -2.4), (11, 4.6, 7.4), "feather", "hump")
    k.limb(to, (-12, 38, 4), (9, 22, 8), 1.6, "leather", "strap", d=0.6)
    for (x, y) in ((-6, 33), (-2, 29), (2, 26)):
        k.box(to, C(x, y, 7.4, 2.4, 2.4, 1.0), "bone", tag="trophy_skull")
    fan(k, to, (0, 40, -6), [(dx, 0.5, -1) for dx in (-0.8, -0.4, 0, 0.4, 0.8)], 8, 2.6, tag="hump_feather")
    # ---------------------------------------------------------------- the head: the birdcage, crows in it
    hd = k.part("head", (0, 38, 3), (("x", -16),), "torso")
    k.box(hd, C(0, 37.4, 3.6, 7.0, 6.6, 7.0), "skin", tag="head")
    for sx in (-1.6, 1.6):
        k.box(hd, C(sx, 41.0, 7.15, 1.4, 0.8, 0.3), "eye", group="glow", tag="eye")
    for a in range(0, 360, 30):          # the cage: bars round, domed on top, a ring
        r = math.radians(a)
        x, z = math.sin(r) * 6.0, 3.6 + math.cos(r) * 6.0
        k.box(hd, C(x, 36, z, 0.8, 10, 0.8), "iron", tag="cage_bar")
        k.limb(hd, (x, 46, z), (x * 0.3, 49.4, 3.6 + (z - 3.6) * 0.3), 0.8, "iron", "cage_dome")
    k.ring(hd, 0, 36.2, 3.6, 6.2, 1.2, "iron", "cage_band", n=14, axis="y")
    k.ring(hd, 0, 46.0, 3.6, 6.2, 1.0, "iron", "cage_band", n=14, axis="y")
    k.ring(hd, 0, 51.0, 3.6, 1.6, 0.6, "iron", "cage_ring", n=8)
    for (x, y, z, f) in ((-3.4, 44.4, 6.4, 1), (3.2, 42.0, 0.4, -1)):        # the crows nesting in there
        k.box(hd, C(x, y, z, 2.0, 2.2, 3.0), "feather", tag="crow")
        k.box(hd, C(x, y + 1.6, z + f * 1.6, 1.4, 1.4, 1.4), "feather", tag="crow")
        k.shard(hd, (x, y + 2.0, z + f * 2.4), (0, -0.1, f), 1.8, 0.6, mat="beak", tag="crow_beak")
        k.box(hd, C(x + 0.6, y + 2.4, z + f * 1.8, 0.3, 0.3, 0.3), "eye", group="glow", tag="crow_eye")
    k.box(hd, C(0, 46.6, 3.6, 8, 1.6, 8), "straw", tag="nest")
    # ---------------------------------------------------------------- arms: bare and grey, like posts
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 13.4
        up = k.part("arm_" + nm, (x, 36, 0), (("x", -20 if side > 0 else -60), ("z", side * 12)), "torso")
        fo = k.part("fore_" + nm, (x, 25, 0), (("x", -30 if side > 0 else -40),), up)
        hn = k.part("hand_" + nm, (x, 14, 0), (), fo)
        k.blob(up, (x, 34.6, 0), (6.0, 4.6, 6.2), "feather", "shoulder")
        k.stack(up, x, 0, [(25, 6.4, 6.6), (31, 7.4, 7.6)], "skin", "upper_arm")
        k.stack(fo, x, 0, [(15, 7.6, 7.6), (20, 8.0, 8.0), (25, 6.8, 6.8)], "skin", "forearm")
        k.box(fo, C(x, 15, 0, 8.6, 3.0, 8.6), "leather", tag="bracer")
        k.box(hn, C(x, 9.0, 0.6, 7.0, 6.0, 7.0), "skin", tag="fist")
    # the cage flail: a short haft, three chains, three hanging-cages with bones in them
    fl = k.part("flail", (-13.4, 12, 0.6), (("x", 40),), k.parts["hand_r"])
    k.limb(fl, (-13.4, 4, 0.6), (-13.4, 16, 0.6), 1.8, "iron", "haft")
    for i, dx in enumerate((-4, 0, 4)):
        top = (-13.4, 4, 0.6)
        end = (-13.4 + dx, -10 - (i % 2) * 3, 0.6 + dx * 0.4)
        k.chain(fl, top, end, 4, w=1.0)
        cx, cy, cz = end
        for a in range(0, 360, 60):
            r = math.radians(a)
            k.box(fl, C(cx + math.sin(r) * 2.2, cy - 6, cz + math.cos(r) * 2.2, 0.6, 6, 0.6), "iron", tag="cage_bar")
        k.box(fl, C(cx, cy - 6.4, cz, 5.0, 0.8, 5.0), "iron", tag="cage_floor")
        k.box(fl, C(cx, cy - 0.6, cz, 5.0, 0.8, 5.0), "iron", tag="cage_top")
        k.box(fl, C(cx, cy - 5.6, cz, 2.2, 2.0, 2.2), "bone", tag="cage_skull")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Augur (caster)

def augur():
    """The augurs read the future in what the crows leave. This one wears a long mask made from a heron's skull,
    the beak to his chest, his own eyes sewn shut behind it - he sees with the eyes painted on his robe, which open.
    A mantle of black feathers; entrails in a bronze bowl on his belt; a crooked staff with a live crow on it."""
    k = X.Kit("augur")
    hips = k.part("hips", (0, 19, 0))
    k.stack(hips, 0, 0, [(13, 10.4, 7.4), (19, 9.2, 6.4)], "cloth", "robe")
    k.box(hips, C(4.6, 15, 2.6, 3.6, 1.6, 3.6), "iron", tag="bowl")
    k.box(hips, C(4.6, 16.4, 2.6, 3.0, 0.6, 3.0), "gore", tag="entrails")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.4
        th = k.part("thigh_" + nm, (x, 19, 0), (("x", -4),), "hips")
        sh = k.part("shin_" + nm, (x, 10, 0), (("x", 6),), th)
        ft = k.part("foot_" + nm, (x, 2, 0), (), sh)
        k.box(th, C(x, 9.6, 0, 4.8, 9.4, 6.4), "cloth", tag="robe")
        k.box(sh, C(x, 1.2, 0, 5.2, 9.2, 6.8), "cloth", tag="robe")
        k.box(ft, C(x, 0, 1.4, 3.0, 1.6, 5.2), "leather", tag="foot")
    for (y, x) in ((6, -2.4), (11, 2.6), (15, -1.4)):     # the painted eyes on the robe, open, glowing
        k.box(hips, C(x, y, 3.65, 2.4, 1.2, 0.3), "bone", tag="painted_eye")
        k.box(hips, C(x, y + 0.2, 3.75, 1.0, 0.8, 0.3), "eye", group="glow", tag="robe_eye")
    # ---------------------------------------------------------------- torso and mantle
    to = k.part("torso", (0, 19, 0), (("x", 10),), "hips")
    k.stack(to, 0, 0, [(19, 9.2, 6.4), (25, 11.4, 7.0), (31, 12.4, 7.0)], "cloth", "robe")
    k.stack(to, 0, -0.2, [(23, 14.6, 9.0), (28, 15.4, 9.2), (31.4, 13.4, 8.4)], "feather", "mantle")
    fan(k, to, (0, 30, -4), [(dx, -1, -0.15) for dx in (-0.5, -0.25, 0, 0.25, 0.5)], 16, 3.0, tag="mantle_tail")
    for (y, x) in ((24, 2.4), (27, -2.0)):
        k.box(to, C(x, y, 3.65, 2.4, 1.2, 0.3), "bone", tag="painted_eye")
        k.box(to, C(x, y + 0.2, 3.75, 1.0, 0.8, 0.3), "eye", group="glow", tag="robe_eye")
    # ---------------------------------------------------------------- the head: the heron-skull mask
    hd = k.part("head", (0, 31, 0.6), (("x", -4),), "torso")
    k.box(hd, C(0, 31, 0.2, 6.0, 6.6, 6.2), "cloth", tag="hood")
    k.box(hd, C(0, 31.4, 2.6, 4.6, 5.4, 2.4), "bone", tag="mask")
    k.shard(hd, (0, 33.0, 4.0), (0, -0.85, 0.55), 12.0, 2.6, mat="bone", tag="mask_beak")
    for sx in (-1.2, 1.2):
        k.box(hd, C(sx, 34.6, 3.85, 1.4, 1.2, 0.3), "dark", tag="socket")
        k.box(hd, C(sx, 35.0, 3.95, 1.2, 0.3, 0.3), "gore", tag="stitches")
    k.box(hd, C(0, 37.0, 3.85, 1.4, 1.4, 0.3), "eye", group="glow", tag="eye")
    for i in range(5):
        k.shard(hd, (0, 37.6, 0.4 - i * 1.2), (0, 0.9, -0.7), 5.0, 1.2, mat="quill", tag="crest")
    # ---------------------------------------------------------------- arms
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 7.0
        up = k.part("arm_" + nm, (x, 29.6, 0), (("x", -50 if side > 0 else -40), ("z", side * 10)), "torso")
        fo = k.part("fore_" + nm, (x, 21.6, 0), (("x", -60 if side > 0 else -40),), up)
        hn = k.part("hand_" + nm, (x, 13.8, 0), (), fo)
        k.box(up, C(x, 21.4, 0, 3.8, 8.4, 4.0), "cloth", tag="sleeve")
        k.stack(fo, x, 0, [(13.4, 6.0, 6.0), (17, 4.8, 4.8), (21.6, 4.0, 4.0)], "cloth", "sleeve")
        k.box(hn, C(x, 11.4, 0.4, 2.6, 2.8, 2.6), "skin", tag="hand")
        if side > 0:
            k.box(hn, C(x, 11.8, 1.8, 1.6, 1.0, 1.6), "gore", tag="liver")
    # the crooked staff with a crow perched on it
    st = k.part("staff", (-7, 12.6, 0.8), (("x", 70),), k.parts["hand_r"])
    pts = [(-7, -8, 0.8), (-7, 8, 0.8), (-6, 18, 1.4), (-7.6, 26, 0.6), (-6.4, 32, 1.2)]
    for (a, b) in zip(pts, pts[1:]):
        k.limb(st, a, b, 1.3, "leather", "haft")
    k.box(st, C(-6.4, 33.0, 1.2, 2.4, 2.6, 3.6), "feather", tag="crow")
    k.box(st, C(-6.4, 35.0, 2.6, 1.8, 1.8, 1.8), "feather", tag="crow")
    k.shard(st, (-6.4, 35.8, 3.6), (0, -0.2, 1), 2.0, 0.7, mat="beak", tag="crow_beak")
    k.box(st, C(-5.6, 36.2, 3.0, 0.3, 0.4, 0.4), "eye", group="glow", tag="crow_eye")
    fan(k, st, (-6.4, 34, -0.4), [(0, -0.4, -1), (0.3, -0.5, -1)], 3.6, 1.2, tag="crow_tail")
    for (y, L) in ((28, 5), (22, 6)):
        k.limb(st, (-7, y, 0.8), (-8.4, y - L, 0.8), 0.3, "leather", "cord")
        k.box(st, C(-8.4, y - L - 1, 0.8, 1.0, 1.2, 1.0), "bone", tag="charm")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Feather Blade (skirmisher)

def feather_blade():
    """The tower's knife, who comes down out of the rafters. A cloak of crow wings sewn together, open behind like a
    second pair; a black beak mask with eye slits; bound legs ending in iron talon-spurs; and in each hand a sickle
    blade curved like a crow's claw."""
    k = X.Kit("feather_blade")
    hips = k.part("hips", (0, 19, 0))
    k.box(hips, C(0, 16.6, 0, 7.6, 3.6, 5.0), "leather", tag="breeches")
    k.box(hips, C(0, 19.2, 0, 8.4, 1.6, 5.6), "leather", tag="belt")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.2
        th = k.part("thigh_" + nm, (x, 19, 0), (("x", -24), ("z", side * 8)), "hips")
        sh = k.part("shin_" + nm, (x, 10.2, 0), (("x", 36),), th)
        ft = k.part("foot_" + nm, (x, 2.2, 0), (("x", -12),), sh)
        k.box(th, C(x, 10.4, 0, 3.2, 8.8, 3.4), "cloth", tag="thigh")
        k.box(sh, C(x, 2.2, 0, 3.0, 8.2, 3.2), "leather", tag="wrap")
        k.box(ft, C(x, 0, 1.2, 3.2, 2.0, 5.6), "leather", tag="foot")
        k.shard(ft, (x, 1.0, -1.4), (0, -0.3, -1), 2.6, 0.8, mat="steel", tag="spur")
        k.shard(ft, (x, 0.8, 3.8), (0, -0.4, 1), 2.2, 0.8, mat="steel", tag="foot")
    # ---------------------------------------------------------------- torso: lean, the wing cloak open behind
    to = k.part("torso", (0, 19, 0), (("x", 24),), "hips")
    k.stack(to, 0, 0, [(19, 7.6, 5.0), (24, 8.6, 5.4), (29, 10.4, 5.6)], "feather", "body")
    for sx in (-1, 1):
        k.limb(to, (sx * 4.6, 29.4, 2.9), (-sx * 3.2, 20.6, 2.9), 1.0, "leather", "harness", d=0.4)
        wing(k, to, (sx * 3.6, 28.6, -2.8), sx, 9, 18, w=2.4, n=7, z=-2)
    # ---------------------------------------------------------------- the head: hood, a black beak mask
    hd = k.part("head", (0, 30, 0.4), (("x", -16),), "torso")
    k.box(hd, C(0, 30.2, 0.2, 5.0, 5.6, 5.2), "feather", tag="hood")
    k.box(hd, C(0, 31.4, 2.8, 4.0, 3.4, 1.2), "beak", tag="mask")
    k.shard(hd, (0, 32.0, 3.4), (0, -0.5, 1), 5.0, 2.4, mat="beak", tag="mask_beak")
    for sx in (-1.0, 1.0):
        k.box(hd, C(sx, 33.0, 3.45, 1.2, 0.5, 0.3), "eye", group="glow", tag="eye")
    for i in range(4):
        k.shard(hd, (0, 35.6, 0.6 - i * 1.2), (0, 0.6, -1), 4.4, 1.0, mat="quill", tag="crest")
    # ---------------------------------------------------------------- arms and the sickles
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 6.0
        up = k.part("arm_" + nm, (x, 28, 0), (("x", -60 if side > 0 else -100), ("z", side * 24)), "torso")
        fo = k.part("fore_" + nm, (x, 20.8, 0), (("x", -60 if side > 0 else -20),), up)
        hn = k.part("hand_" + nm, (x, 13.6, 0), (), fo)
        k.box(up, C(x, 21.0, 0, 2.8, 7.4, 3.0), "feather", tag="sleeve")
        k.box(fo, C(x, 13.8, 0, 2.6, 7.0, 2.8), "leather", tag="bracer")
        k.box(hn, C(x, 11.2, 0.3, 2.4, 2.6, 2.4), "leather", tag="hand")
        sk = k.part("sickle_" + nm, (x, 12.4, 0.4), (("x", 80),), hn)
        k.box(sk, C(x, 10.0, 0.4, 1.0, 4.4, 1.0), "leather", tag="grip")
        pts = [(x, 14.4, 0.4), (x, 18.4, 1.2), (x, 20.6, 3.6), (x, 20.4, 6.6), (x, 18.6, 8.6)]
        for (a, b), w in zip(zip(pts, pts[1:]), (1.6, 1.5, 1.2, 0.8)):
            k.limb(sk, a, b, w, "steel", "sickle", d=0.5)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Carrion Crow (swarm)

def carrion_crow():
    """A crow of the Rookery, fed on the hanged until it stands to a man's waist and walks like a man. Ragged wings
    half open, a hooked beak as long as a forearm, talons, a ruff of oily feathers; it carries a skull in one foot
    when it hops. The eyes have the violet in them."""
    k = X.Kit("carrion_crow")
    hips = k.part("hips", (0, 11, -1))
    k.blob(hips, (0, 11.6, -1), (4.4, 3.6, 5.0), "feather", "body")
    fan(k, hips, (0, 11, -5.4), [(dx, -0.2, -1) for dx in (-0.5, -0.25, 0, 0.25, 0.5)], 8, 2.0, tag="tail")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.2
        th = k.part("thigh_" + nm, (x, 10, 0), (("x", -20),), "hips")
        sh = k.part("shin_" + nm, (x, 6, 0), (("x", 40),), th)
        ft = k.part("foot_" + nm, (x, 1.2, 0), (("x", -20),), sh)
        k.blob(th, (x, 8.4, 0.4), (2.0, 2.4, 2.2), "feather", "thigh")
        k.limb(sh, (x, 6, 0.4), (x, 1.2, 0.4), 1.1, "skin", "shank")
        talons(k, ft, (x, 0.8, 0.4), side, s=1.0)
    # ---------------------------------------------------------------- torso: upright, ruffed
    to = k.part("torso", (0, 12, -1), (("x", 20),), "hips")
    k.stack(to, 0, -0.6, [(12, 8.0, 7.4), (16, 7.4, 6.4), (19, 6.0, 5.4)], "feather", "chest")
    for i in range(10):
        a = math.radians(-120 + i * 26)
        k.shard(to, (math.sin(a) * 3.0, 18.6, -0.6 + math.cos(a) * 2.6), (math.sin(a), 0.4, math.cos(a)), 3.0, 1.2,
                mat="quill", tag="ruff")
    # ---------------------------------------------------------------- the head: big hooked beak
    hd = k.part("head", (0, 19, 0), (("x", -10),), "torso")
    k.blob(hd, (0, 21.6, 0.4), (2.8, 2.6, 3.0), "feather", "head")
    k.box(hd, C(0, 20.6, 3.0, 2.4, 2.0, 2.0), "beak", tag="beak_root")
    k.shard(hd, (0, 21.4, 3.8), (0, -0.25, 1), 6.0, 2.0, mat="beak", tag="beak")
    k.shard(hd, (0, 20.6, 3.8), (0, -0.1, 1), 4.0, 1.4, mat="beak", tag="beak")
    k.shard(hd, (0, 21.0, 9.4), (0, -1, 0.2), 1.4, 0.8, mat="beak", tag="beak_hook")
    for sx in (-1.6, 1.6):
        k.box(hd, C(sx, 22.4, 1.8, 0.4, 0.8, 0.8), "eye", group="glow", tag="eye")
    # ---------------------------------------------------------------- arms that are wings, ragged, half open
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 4.0
        up = k.part("arm_" + nm, (x, 17, -1), (("x", -10), ("z", side * 40)), "torso")
        fo = k.part("fore_" + nm, (x, 13, -1), (("x", -10),), up)
        hn = k.part("hand_" + nm, (x, 9, -1), (), fo)
        k.limb(up, (x, 17, -1), (x, 13, -1), 2.4, "feather", "wing_bone", d=1.6)
        k.limb(fo, (x, 13, -1), (x, 9, -1.4), 2.0, "feather", "wing_bone", d=1.4)
        for i in range(4):
            k.limb(fo, (x, 13 - i, -1.4), (x + side * (0.6 + i * 0.4), 4 - i * 1.4, -2.6 - i * 0.3), 1.8, "feather", "secondary", d=0.4)
        fan(k, hn, (x, 9, -1.4), [(side * (0.4 - i * 0.12), -1, -0.3) for i in range(5)], 9, 1.8, tag="primary")
    k.box(k.parts["foot_l"], C(2.2, 0.4, 3.6, 2.6, 2.6, 2.6), "bone", tag="skull")
    k.box(k.parts["foot_l"], C(2.2, 1.0, 4.95, 1.8, 0.8, 0.3), "dark", tag="skull_eyes")
    k.s.shaders = shaders()
    return k.s, k.parts


MOBS = {
    "carrion_crow": dict(make=carrion_crow, ent=(0.7, 1.6), stats=dict(hp=12, speed=0.32, dmg=3, armor=0, kb=0)),
    "crowbrute": dict(make=crowbrute, ent=(1.4, 3.6), stats=dict(hp=70, speed=0.2, dmg=11, armor=6, kb=0.7)),
    "augur": dict(make=augur, ent=(0.9, 2.8), stats=dict(hp=28, speed=0.22, dmg=5, armor=2, kb=0)),
    "feather_blade": dict(make=feather_blade, ent=(0.9, 2.8), stats=dict(hp=26, speed=0.33, dmg=6, armor=2, kb=0)),
    "rook_captain": dict(make=rook_captain, ent=(1.2, 3.2), stats=dict(hp=150, speed=0.22, dmg=11, armor=9, kb=0.6), key=True),
    "raven_mother": dict(make=raven_mother, texel=1, ent=(2.4, 6.0), stats=dict(hp=460, speed=0.22, dmg=16, armor=8, kb=0.9), boss=True),
}
