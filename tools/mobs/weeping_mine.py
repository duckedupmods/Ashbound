"""The Weeping Mine's monsters, each built by hand (tools/vox2.py brushes). The copper mine where the crystal grew into
the men who dug it: teal crystal that weeps light, black seam-rock, old copper gone green, shaft timber, rail iron.

    shard_crawler    swarm   a rock crawler with a ridge of crystal spines, crystal-tipped legs (the spider's bones)
    cart_golem       brute   an ore cart that would not stop: rails for legs and arms, the cart for a chest, ore glowing in it
    lamp_miner       caster  a dead miner the crystal grew through: spine fanned with shards, face half crystal, a lantern pole
    blind_burrower   skirm   an eyeless digging thing: spade claws, a star of pink feelers for a nose, bone plates down its back
    foreman          elite   the pit boss: barrel chest, crystal grown over one shoulder, a pick-sledge on his shoulder, the keys
    the_vein         boss    the mine's vein stood up: a hunched colossus, crystal ridge, a heart in its open chest, a crystal arm

    python tools/monsterforge.py weeping_mine --preview ; python tools/mobsheet.py weeping_mine
"""
import math

import vox2 as X
from vox2 import C, ramp, shade, fbm

# ---------------------------------------------------------------- the mine's palette

SLATE = ramp("#0c0e12", "#14171c", "#1d2128", "#272c34", "#323843", "#3f4652", "#4f5764")
CRYSTAL = ramp("#062a2c", "#0e4a4a", "#167070", "#22a09a", "#46ccc0", "#8ceee2", "#d6fff8")
GLOW = ramp("#1a7e78", "#34b8aa", "#7ce8d8", "#c0fff4", "#f4fffd")
COPPER = ramp("#1e130c", "#3a2414", "#5a361c", "#7c4a24", "#a0622e", "#c88444", "#e8aa66")
VERD = ramp("#1e4a3e", "#2e6a58", "#4a8c76", "#6ab096")
TIMBER = ramp("#140c08", "#1e140c", "#2a1c11", "#382617", "#4a331f", "#5e4229")
IRON = ramp("#0e0e10", "#18181c", "#24242a", "#323238", "#424248", "#56565e")
RUST = ramp("#2a1408", "#44200c", "#5e2e12", "#7a3e18")
LEATHER = ramp("#120c08", "#1e140c", "#2c1e12", "#3c2a1a", "#4e3822")
CLOTH = ramp("#101418", "#181e24", "#22282e", "#2c343c", "#3a444e")
SKIN = ramp("#262a2c", "#363c40", "#4a5256", "#626c70", "#7e898c")          # grey, dust-sick
PALE = ramp("#1e1a1c", "#2e2628", "#423638", "#58484a", "#6e5a5a")          # the burrower's naked hide
PINK = ramp("#5a1e2a", "#8a3040", "#b84a5a", "#e07a86", "#ffb4bc")
BONE = ramp("#3a3428", "#5a5240", "#7a7058", "#9a9074", "#bab096")
BEARD = ramp("#140e0a", "#22180f", "#342416", "#46321e")


def shaders():
    return {
        "rock": X.surf(SLATE, 0.5, 1.3, 0.34, 0.14, crust=(CRYSTAL, 0.06), rust=(VERD, 0.08, 0.3)),
        "slate": X.surf(SLATE, 0.5, 1.2, 0.3, 0.12, crust=(CRYSTAL, 0.12)),
        "crystal": X.facets(CRYSTAL),
        "glow": X.glow(GLOW),
        "eye": X.glow(GLOW, 0.75, 0.2),
        "copper": X.surf(COPPER, 0.5, 1.3, 0.16, 0.16, rust=(VERD, 0.32, 0.3)),
        "timber": X.surf(TIMBER, 0.5, 1.0, 0.2, 0.08, stripe=3),
        "iron": X.surf(IRON, 0.5, 1.4, 0.16, 0.2, rust=(RUST, 0.3, 0.4)),
        "rail": X.surf(IRON, 0.62, 1.4, 0.1, 0.3, rust=(RUST, 0.22, 0.5)),
        "leather": X.surf(LEATHER, 0.5, 1.0, 0.2, 0.08, drip=(SLATE, 0.18)),
        "cloth": X.surf(CLOTH, 0.48, 1.0, 0.24, 0.0, holes=True, crust=(CRYSTAL, 0.08)),
        "coat": X.surf(LEATHER, 0.46, 1.0, 0.22, 0.04, holes=True),
        "skin": X.wrinkled(SKIN, 0.8),
        "pale": X.wrinkled(PALE, 1.4),
        "pink": X.surf(PINK, 0.55, 1.0, 0.2, 0.06),
        "bone": X.surf(BONE, 0.6, 1.0, 0.14, 0.12),
        "beard": X.surf(BEARD, 0.5, 0.8, 0.3, 0.0, stripe=2),
        "dark": X.dark(SLATE),
    }


# ================================================================ the Vein (boss)

def the_vein():
    """The mine wept until the vein itself stood up: a hunched colossus of black seam-rock six blocks high, its back
    a ridge of crystal like a broken mountain, its chest torn open on a crystal heart that beats with light. The
    shaft timbers the miners shored it with are still speared through its shoulders, a lantern on one. Its right
    arm ends in a blade of raw crystal longer than a man; its left drags a fist of rock bound in bent rail, a cart
    wheel ground into the knuckles. Its head is small and sunk low between the shoulders, a foreman's copper
    helmet fused into its brow, the lamp still lit."""
    k = X.Kit("the_vein")
    TILT = 22
    hips = k.part("hips", (0, 40, 0))
    # the girdle: rock, shored with timber and a band of rail
    k.stack(hips, 0, 0, [(30, 22, 15), (36, 28, 18), (42, 26, 17)], "rock", "pelvis")
    k.box(hips, C(0, 37.0, 0, 30.0, 2.4, 19.4), "rail", tag="rail_band")
    for x, a in ((-9, 8), (2, -6), (10, 12)):
        k.limb(hips, (x, 30, 9.6), (x + a * 0.2, 41, 9.0), 2.6, "timber", "shoring", d=2.4)
    k.chain(hips, (12, 36, 8), (14, 24, 9), 5)
    k.ring(hips, 14.6, 21.0, 9.4, 3.4, 1.0, "iron", "wheel", n=10)
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 8.5
        th = k.part("thigh_" + nm, (x, 36, 0), (("x", -10), ("z", side * 8)), "hips")
        sh = k.part("shin_" + nm, (x, 20, 0), (("x", 16),), th)
        ft = k.part("foot_" + nm, (x, 5, 0), (("x", -6),), sh)
        k.stack(th, x, 0, [(20, 13, 13), (28, 15, 14), (36, 13, 13)], "rock", "thigh")
        k.blob(th, (x, 21, 1.5), (7.5, 4.5, 7.5), "slate", "knee")
        k.cluster(th, (x + side * 2, 22, 4), 3, 9, 2.4, seed=side + 4, up=(side * 0.3, 0.8, 0.6))
        k.stack(sh, x, 0, [(5, 13, 13), (12, 11, 11), (20, 12, 12)], "rock", "shin")
        k.box(ft, C(x, 0, 2.5, 16, 5, 19), "rock", tag="foot")
        for t in (-5, 0, 5):
            k.shard(ft, (x + t, 1.5, 11.5), (t * 0.05, 0.2, 1), 6, 2.6, tag="foot")
    # ---------------------------------------------------------------- the torso: hunched, wide, torn open in front
    to = k.part("torso", (0, 41, 0), (("x", TILT),), "hips")
    k.stack(to, 0, -1.0, [(40, 26, 18), (52, 36, 22), (62, 44, 24), (70, 40, 22)], "rock", "chest")
    # the wound: a dark cave in its chest, the heart in it, crystal veins spreading out over the rock
    k.box(to, C(0, 48, 10.2, 16, 15, 3.0), "dark", tag="wound")
    for (x, y, w, h) in ((-9, 50, 3, 9), (9, 50, 3, 9), (0, 63, 14, 3), (-6, 46, 4, 3), (7, 45, 4, 3)):
        k.box(to, C(x, y, 11.0, w, h, 2.6), "slate", tag="wound_lip")
    k.blob(to, (0, 55, 9.0), (6.0, 7.0, 5.0), "crystal", "heart", step=1.2)
    k.blob(to, (0, 55.5, 11.0), (3.6, 4.4, 3.4), "glow", "heart_core", step=1.0)
    for (a, L) in ((30, 11), (150, 10), (75, 13), (110, 9), (200, 8), (-20, 9)):
        r = math.radians(a)
        k.shard(to, (0, 55, 11.5), (math.cos(r), math.sin(r), 0.2), L, 1.2, mat="glow", tag="vein", group="glow")
    # the ridge: a broken mountain of crystal up its back, over its head
    for (x, y, z, L, w, lean) in ((0, 66, -10, 34, 6.5, 0.0), (-8, 64, -9, 26, 5.0, -0.4), (8, 64, -9, 28, 5.2, 0.4),
                                  (-15, 58, -7, 18, 4.0, -0.7), (15, 58, -7, 20, 4.2, 0.7), (-4, 56, -12, 22, 4.4, -0.2),
                                  (5, 54, -12, 19, 4.0, 0.25), (0, 48, -11, 14, 3.4, 0.0), (-11, 50, -9, 13, 3.2, -0.6),
                                  (11, 50, -9, 14, 3.2, 0.6)):
        k.shard(to, (x, y, z), (lean, 1.0, -0.45), L, w)
    k.cluster(to, (0, 70, -4), 5, 9, 2.6, seed=8, up=(0, 1, -0.3))
    # the timbers they shored it with, speared through its shoulders, a lantern hung off one
    k.limb(to, (-30, 76, -2), (-6, 58, 4), 3.2, "timber", "beam", d=3.0)
    k.limb(to, (26, 80, 6), (8, 60, -4), 3.0, "timber", "beam", d=2.8)
    k.chain(to, (24, 78, 6), (24, 70, 6), 4, w=1.0)
    k.box(to, C(24, 66, 6, 4.0, 4.4, 4.0), "copper", tag="lantern")
    k.box(to, C(24, 66.6, 6, 4.4, 3.2, 3.2), "glow", group="glow", tag="lantern_glass")
    # ---------------------------------------------------------------- the head: small, sunk low, the foreman's helmet fused on
    hd = k.part("head", (0, 66, 7), (("x", -TILT + 8),), "torso")
    k.blob(hd, (0, 69, 9), (6.0, 5.6, 6.2), "rock", "skull")
    k.box(hd, C(0, 64.4, 11.2, 9.0, 3.4, 5.0), "rock", tag="jaw")
    for t in (-3, -1, 1, 3):
        k.shard(hd, (t, 67.4, 13.4), (0, -1, 0.2), 2.6, 1.0, mat="bone", tag="tooth")
    k.box(hd, C(0, 70.2, 14.4, 10.0, 2.0, 1.4), "rock", tag="brow")
    for sx in (-2.6, 2.6):
        k.box(hd, C(sx, 68.4, 14.6, 2.6, 1.4, 0.8), "dark", tag="socket")
        k.box(hd, C(sx, 68.6, 15.0, 1.8, 0.8, 0.4), "eye", group="glow", tag="eye")
    k.blob(hd, (0, 73.4, 8.6), (6.8, 3.0, 7.0), "copper", "helmet")
    k.box(hd, C(0, 72.0, 8.6, 15.0, 0.8, 15.0), "copper", tag="brim")
    k.box(hd, C(0, 73.6, 15.6, 3.0, 3.0, 1.4), "copper", tag="lamp")
    k.box(hd, C(0, 74.0, 16.4, 2.2, 2.2, 0.4), "glow", group="glow", tag="lamp_glass")
    k.cluster(hd, (-3, 75, 7), 3, 6, 1.6, seed=21, up=(-0.3, 1, -0.2))
    # ---------------------------------------------------------------- arms
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 24
        up = k.part("arm_" + nm, (x, 66, 0), (("x", -30 if side < 0 else -10), ("z", side * 14)), "torso")
        fo = k.part("fore_" + nm, (x, 46, 0), (("x", -50 if side < 0 else -20),), up)
        hn = k.part("hand_" + nm, (x, 28, 0), (), fo)
        k.blob(up, (x + side * 2, 66, 0), (10, 8, 10), "rock", "shoulder")
        k.cluster(up, (x + side * 4, 72, -2), 4, 12, 3.2, seed=30 + side, up=(side * 0.5, 1, -0.3))
        k.stack(up, x, 0, [(46, 11, 11), (58, 13, 13), (64, 14, 14)], "rock", "upper_arm")
        k.blob(up, (x, 47, 0), (7, 4.5, 7), "slate", "elbow")
        if side < 0:     # the crystal blade arm
            k.stack(fo, x, 0, [(30, 13, 13), (40, 12, 12), (46, 11, 11)], "rock", "forearm")
            k.cluster(fo, (x, 38, 4), 4, 8, 2.2, seed=40, up=(0, 0.4, 1))
            k.blob(hn, (x, 28, 0), (8, 5, 8), "crystal", "wrist")
            k.shard(hn, (x, 30, 0), (0, -1, 0.05), 46, 9.0, tag="blade")
            k.shard(hn, (x - 3, 28, 2), (-0.2, -1, 0.3), 20, 4.0, tag="blade")
            k.shard(hn, (x + 3, 28, -2), (0.2, -1, -0.3), 16, 3.4, tag="blade")
        else:            # the dragging fist, bound in rail, a cart wheel in the knuckles
            k.stack(fo, x, 0, [(28, 14, 14), (38, 13, 13), (46, 12, 12)], "rock", "forearm")
            for y in (32, 36, 40):
                k.box(fo, C(x, y, 0, 15.6, 1.4, 15.6), "rail", tag="rail_wrap")
            k.blob(hn, (x, 22, 1), (10, 8, 10), "rock", "fist")
            k.ring(hn, x + 10.2, 22, 1, 6.0, 1.6, "iron", "wheel", n=12, axis="x")
            k.box(hn, C(x + 10.2, 21.2, 1, 1.6, 1.6, 12), "iron", tag="axle")
            k.chain(hn, (x, 16, 4), (x + 4, 2, 10), 6)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Foreman (elite, carries the key)

def foreman():
    """The pit boss, who drove the men down into the seam after the first of them came up crying light. A slab of a
    man, barrel chest under a riveted copper-plated apron, sleeves rolled on forearms like hams. The crystal took
    his left shoulder first and grew there like a pauldron, up his neck to the jaw. A beard to his belt, a dented
    copper hard hat, its lamp still burning; tears of crystal down his cheeks. His pick-sledge - hammer one side,
    pick the other - rides his right shoulder; on his belt the ring of keys to every gate in the mine."""
    k = X.Kit("foreman")
    hips = k.part("hips", (0, 21, 0))
    k.box(hips, C(0, 17.6, 0, 11.6, 4.6, 7.6), "cloth", tag="trousers")
    k.box(hips, C(0, 21.2, 0, 12.4, 2.0, 8.2), "leather", tag="belt")
    k.box(hips, C(0, 21.0, 4.2, 2.6, 2.4, 0.6), "copper", tag="buckle")
    # the keys: a big iron ring on the left hip, five keys, a tag
    k.ring(hips, 6.6, 15.4, 3.2, 2.0, 0.6, "iron", "keyring", n=8)
    for t, (dx, L) in enumerate(((-1.2, 4.0), (-0.4, 5.0), (0.4, 4.4), (1.2, 3.6), (0.0, 3.0))):
        k.box(hips, C(6.6 + dx, 13.4 - L * 0.5, 3.4, 0.6, L, 0.4), "iron", tag="key")
        k.box(hips, C(6.6 + dx + 0.4, 13.4 - L * 0.5 - L * 0.5 + 0.6, 3.4, 1.0, 0.8, 0.4), "iron", tag="key_bit")
    # a lantern and a coil of rope on the right hip
    k.chain(hips, (-6.4, 19.6, 2.6), (-6.4, 15.6, 2.6), 2, w=0.8)
    k.box(hips, C(-6.4, 11.6, 2.6, 2.8, 3.6, 2.8), "copper", tag="belt_lamp")
    k.box(hips, C(-6.4, 12.2, 2.6, 3.0, 2.4, 2.0), "glow", group="glow", tag="belt_lamp_glass")
    k.ring(hips, -5.4, 16.6, -2.6, 2.6, 0.9, "leather", "rope", n=10, axis="x")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 3.4
        th = k.part("thigh_" + nm, (x, 21, 0), (("x", -6), ("z", side * 5)), "hips")
        sh = k.part("shin_" + nm, (x, 11.4, 0), (("x", 10),), th)
        ft = k.part("foot_" + nm, (x, 2.4, 0), (("x", -4),), sh)
        k.box(th, C(x, 11.6, 0, 5.4, 9.8, 5.8), "cloth", tag="trouser")
        k.box(th, C(x, 9.8, 1.0, 5.2, 2.4, 5.2), "leather", tag="kneepad")
        k.box(sh, C(x, 2.4, 0.2, 5.0, 8.8, 5.4), "leather", tag="boot_top")
        k.box(sh, C(x, 7.6, 0.2, 5.6, 1.4, 6.0), "leather", tag="boot_cuff")
        k.box(ft, C(x, 0, 1.2, 5.6, 2.8, 8.4), "leather", tag="foot")
        k.box(ft, C(x, 0, 4.8, 5.0, 2.2, 2.4), "copper", tag="foot")           # steel toecap gone green
    # ---------------------------------------------------------------- the chest: a barrel under the apron
    to = k.part("torso", (0, 21.6, 0), (("x", 6),), "hips")
    k.stack(to, 0, 0, [(21.6, 12.4, 8.0), (27, 15.0, 9.6), (32, 16.4, 9.8), (35.4, 14.2, 8.4)], "cloth", "shirt")
    k.box(to, C(0, 13.0, 4.7, 11.0, 20.6, 0.8), "leather", tag="apron")       # the apron, chest to shin
    for (x, y) in ((-2.8, 25.4), (2.8, 25.4), (-2.8, 19.4), (2.8, 19.4), (0, 31.0)):
        k.box(to, C(x, y, 5.15, 4.6, 4.6, 0.5), "copper", tag="apron_plate")
        k.rivets(to, [(x - 1.8, y + 3.8, 5.45), (x + 1.8, y + 3.8, 5.45), (x - 1.8, y + 0.6, 5.45), (x + 1.8, y + 0.6, 5.45)], "iron", 0.6)
    for sx in (-4.6, 4.6):
        k.limb(to, (sx, 33.4, 4.8), (sx * 0.6, 34.8, -4.6), 1.2, "leather", "apron_strap")
    # the beard, to his belt
    k.stack(to, 0, 4.6, [(22.6, 3.0, 1.4), (27.0, 5.6, 2.0), (32.0, 7.6, 2.4), (35.4, 7.0, 2.2)], "beard", "beard")
    # the crystal that took his left shoulder, up his neck
    k.blob(to, (6.6, 34.0, -0.4), (5.4, 3.6, 5.6), "slate", "crust")
    k.cluster(to, (7.0, 35.6, -0.6), 6, 7.0, 2.2, seed=12, up=(0.5, 1, -0.1))
    k.cluster(to, (4.4, 33.6, 3.2), 3, 4.0, 1.4, seed=13, up=(0.2, 1, 0.6))
    # ---------------------------------------------------------------- the head: hard hat, lamp, crystal tears
    hd = k.part("head", (0, 35.4, 0.4), (("x", -6),), "torso")
    k.box(hd, C(0, 35.2, 0.6, 6.4, 6.0, 6.4), "skin", tag="face")
    k.box(hd, C(0, 38.0, 3.85, 6.0, 0.8, 0.6), "skin", tag="brow")
    k.box(hd, C(0, 36.4, 4.05, 1.4, 1.8, 0.8), "skin", tag="nose")
    for sx in (-1.5, 1.5):
        k.box(hd, C(sx, 37.2, 3.82, 1.4, 0.7, 0.3), "eye", group="glow", tag="eye")
        k.box(hd, C(sx, 33.6, 3.9, 0.7, 3.6, 0.5), "crystal", group="glow", tag="tear")
    k.box(hd, C(0, 34.4, 3.9, 4.0, 1.0, 0.6), "beard", tag="mustache")
    k.stack(hd, 0, 2.6, [(30.8, 5.4, 2.0), (34.4, 7.2, 2.6), (36.0, 6.4, 2.0)], "beard", "beard")
    k.blob(hd, (0, 41.8, 0.4), (4.0, 2.2, 4.2), "copper", "hat")
    k.box(hd, C(0, 40.6, 0.6, 9.6, 0.8, 9.6), "copper", tag="brim")
    k.box(hd, C(0, 41.2, 4.6, 2.4, 2.2, 1.2), "copper", tag="lamp")
    k.box(hd, C(0, 41.6, 5.3, 1.6, 1.4, 0.3), "glow", group="glow", tag="lamp_glass")
    k.box(hd, C(1.8, 43.0, 1.0, 1.6, 0.8, 1.4), "dark", tag="dent")
    # ---------------------------------------------------------------- arms: rolled sleeves, forearms like hams
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 9.4
        up = k.part("arm_" + nm, (x, 32.6, 0), (("x", -22 if side > 0 else -150), ("z", side * 10)), "torso")
        fo = k.part("fore_" + nm, (x, 23.4, 0), (("x", -50 if side > 0 else -100),), up)
        hn = k.part("hand_" + nm, (x, 14.6, 0), (), fo)
        k.box(up, C(x, 25.0, 0, 5.4, 8.6, 5.6), "cloth", tag="sleeve")
        k.box(up, C(x, 23.0, 0, 6.0, 2.0, 6.2), "cloth", tag="rolled")
        k.stack(fo, x, 0, [(14.8, 4.8, 5.0), (19.0, 6.2, 6.0), (23.0, 5.6, 5.6)], "skin", "forearm")
        k.box(hn, C(x, 11.2, 0.4, 5.0, 3.8, 5.0), "leather", tag="glove")
        if side > 0:     # the crystal ran down his left arm too
            k.cluster(up, (x + 2.4, 31.0, -0.4), 4, 5.0, 1.8, seed=14, up=(0.6, 1, 0))
            k.cluster(fo, (x + 2.0, 19.0, 0), 3, 3.4, 1.2, seed=15, up=(1, 0.3, 0))
    # the pick-sledge on his right shoulder: a long haft, an iron head, hammer face and a pick spike
    hr = k.parts["hand_r"]
    w = k.part("sledge", (-9.4, 12.6, 0.4), (("x", 10),), hr)
    k.limb(w, (-9.4, 1.0, 0.4), (-9.4, 30.0, 0.4), 1.8, "timber", "haft")
    k.box(w, C(-9.4, 6.0, 0.4, 2.2, 3.0, 2.2), "leather", tag="grip")
    k.box(w, C(-9.4, 29.0, 0.4, 4.6, 5.6, 4.6), "iron", tag="sledge_eye")
    k.box(w, C(-9.4, 29.4, 5.2, 6.4, 6.4, 5.0), "iron", tag="hammer_face")
    k.box(w, C(-9.4, 29.8, 7.9, 6.8, 6.8, 0.6), "rail", tag="hammer_face")
    k.shard(w, (-9.4, 32.0, -2.4), (0, -0.25, -1), 11, 3.4, mat="iron", tag="pick")
    k.box(w, C(-9.4, 34.6, 0.4, 5.4, 1.2, 5.4), "copper", tag="band")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Lamp Miner (caster)

def lamp_miner():
    """A miner who went down for the night shift and never came up: the crystal grew in him where he sat. It burst
    out of his spine in a fan of shards and through the right side of his face, so one eye is a crystal now, and
    weeps. His long coat hangs in rags, his lamp-helmet is still lit, and he leans on the pole he hung his lantern
    from - he swings it to call the light out of the walls, and the walls answer."""
    k = X.Kit("lamp_miner")
    hips = k.part("hips", (0, 20, 0))
    k.box(hips, C(0, 17.2, 0, 8.6, 4.0, 5.6), "cloth", tag="trousers")
    k.box(hips, C(0, 20.0, 0, 9.2, 1.6, 6.0), "leather", tag="belt")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.6
        th = k.part("thigh_" + nm, (x, 20, 0), (("x", -8), ("z", side * 3)), "hips")
        sh = k.part("shin_" + nm, (x, 10.8, 0), (("x", 14),), th)
        ft = k.part("foot_" + nm, (x, 2.2, 0), (("x", -6),), sh)
        k.box(th, C(x, 11.0, 0, 3.6, 9.6, 3.8), "cloth", tag="trouser")
        k.box(sh, C(x, 2.2, 0, 3.4, 8.8, 3.6), "leather", tag="boot")
        k.box(ft, C(x, 0, 1.0, 3.8, 2.4, 6.0), "leather", tag="foot")
        if side < 0:
            k.cluster(sh, (x - 1.4, 7.0, 0.4), 3, 3.4, 1.0, seed=3, up=(-1, 0.6, 0.2))
    # the coat: long, in rags, open at the front
    for z, lean, wd in ((2.8, -5, 3.4), (-2.6, 9, 8.4)):
        for sx in ((-2.6, 2.6) if z > 0 else (0,)):
            cp = k.part("coat%d%d" % (z > 0, sx > 0), (sx, 21.0, z), (("x", lean),), hips, bone=False)
            k.box(cp, C(sx, 3.0, z, wd, 18.4, 0.7), "coat", tag="coat")
    # ---------------------------------------------------------------- torso: hunched, thin, the shards out of the spine
    to = k.part("torso", (0, 21, 0), (("x", 18),), "hips")
    k.stack(to, 0, 0, [(21, 8.0, 5.0), (27, 9.6, 5.6), (32, 10.4, 5.6)], "coat", "coat")
    k.box(to, C(0, 22.0, 2.95, 3.0, 9.0, 0.3), "cloth", tag="shirt")
    for sx in (-1, 1):
        k.box(to, C(sx * 3.4, 22.0, 3.0, 2.6, 10.0, 0.5), "coat", tag="lapel")
    k.box(to, C(0, 31.0, -0.4, 12.0, 2.2, 6.4), "coat", tag="collar")
    for (x, y, L, w, lx) in ((0, 30, 22, 3.6, 0.0), (-2.6, 29, 18, 3.0, -0.5), (2.6, 29, 19, 3.0, 0.5),
                             (-4.4, 26, 14, 2.4, -1.0), (4.4, 26, 15, 2.4, 1.0), (0, 24, 11, 2.2, 0.1),
                             (-3.0, 22, 9, 1.8, -0.7), (3.0, 22, 9, 1.8, 0.7)):
        k.shard(to, (x, y, -2.8), (lx, 0.9, -0.9), L, w)
    k.box(to, C(0, 26.0, -3.4, 7.0, 7.0, 1.0), "slate", tag="crust")
    # ---------------------------------------------------------------- the head: the lamp helmet, half the face crystal
    hd = k.part("head", (0, 32.4, 0.4), (("x", -14), ("z", 8)), "torso")
    k.box(hd, C(0, 32.4, 0.6, 5.2, 5.8, 5.4), "skin", tag="face")
    k.box(hd, C(-1.4, 33.0, 3.2, 2.6, 4.4, 0.8), "crystal", tag="crystal_face")
    k.cluster(hd, (-2.2, 35.0, 1.6), 3, 4.0, 1.2, seed=5, up=(-0.6, 1, 0.4))
    k.box(hd, C(1.4, 35.2, 3.35, 1.2, 0.7, 0.3), "eye", group="glow", tag="eye")
    k.box(hd, C(-1.4, 35.0, 3.7, 1.4, 1.0, 0.4), "glow", group="glow", tag="crystal_eye")
    k.box(hd, C(-1.4, 31.4, 3.7, 0.6, 3.6, 0.4), "glow", group="glow", tag="tear")
    k.box(hd, C(1.0, 32.4, 3.35, 2.6, 0.6, 0.3), "dark", tag="mouth")
    k.blob(hd, (0, 38.4, 0.6), (3.4, 1.8, 3.6), "copper", "helmet")
    k.box(hd, C(0, 37.4, 0.6, 7.6, 0.6, 7.8), "copper", tag="brim")
    k.box(hd, C(0, 38.0, 4.0, 2.0, 1.8, 1.0), "copper", tag="lamp")
    k.box(hd, C(0, 38.3, 4.55, 1.4, 1.2, 0.3), "glow", group="glow", tag="lamp_glass")
    # ---------------------------------------------------------------- arms: thin, the left hand crystal to the wrist
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 6.0
        up = k.part("arm_" + nm, (x, 30.4, 0), (("x", -40 if side < 0 else -50), ("z", side * 8)), "torso")
        fo = k.part("fore_" + nm, (x, 22.0, 0), (("x", -50 if side < 0 else -60),), up)
        hn = k.part("hand_" + nm, (x, 14.0, 0), (), fo)
        k.box(up, C(x, 22.4, 0, 3.4, 8.6, 3.6), "coat", tag="sleeve")
        k.box(fo, C(x, 14.4, 0, 3.0, 8.0, 3.2), "coat", tag="sleeve")
        k.box(fo, C(x, 13.6, 0, 3.8, 1.6, 4.0), "coat", tag="cuff")
        if side > 0:
            k.box(hn, C(x, 11.0, 0.3, 2.8, 3.0, 2.8), "crystal", tag="crystal_hand")
            for t in (-0.9, 0, 0.9):
                k.shard(hn, (x + t, 11.0, 0.6), (t * 0.2, -1, 0.3), 4.0, 0.9, mat="glow", tag="finger", group="glow")
        else:
            k.box(hn, C(x, 11.2, 0.3, 2.8, 3.0, 2.8), "skin", tag="hand")
    # the lantern pole in his right hand: a long shaft, a crook at the top, the lantern swinging from it
    hr = k.parts["hand_r"]
    pole = k.part("pole", (-6.0, 12.6, 0.6), (("x", 80),), hr)
    k.limb(pole, (-6.0, -6.0, 0.6), (-6.0, 32.0, 0.6), 1.2, "timber", "haft")
    k.limb(pole, (-6.0, 32.0, 0.6), (-6.0, 34.0, 4.6), 1.0, "iron", "crook")
    k.chain(pole, (-6.0, 34.0, 4.6), (-6.0, 28.0, 4.6), 3, w=0.8)
    k.box(pole, C(-6.0, 23.6, 4.6, 3.6, 4.4, 3.6), "copper", tag="lantern")
    k.box(pole, C(-6.0, 24.2, 4.6, 3.9, 3.0, 2.8), "glow", group="glow", tag="lantern_glass")
    k.box(pole, C(-6.0, 28.0, 4.6, 2.4, 1.0, 2.4), "copper", tag="lantern_cap")
    k.cluster(pole, (-6.0, 22.6, 4.6), 3, 3.0, 1.0, seed=7, up=(0, -1, 0))
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Blind Burrower (skirmisher)

def blind_burrower():
    """It was a miner once, or many. It digs: shoulders like a mole's, forearms ending in three spade claws each as
    long as a forearm, naked grey-pink hide in folds, no eyes at all - where the face was, a star of pink feelers
    that reach and twitch for the warmth of you. Plates of bone run down its spine; a rat's tail drags behind."""
    k = X.Kit("blind_burrower")
    hips = k.part("hips", (0, 18, -1))
    k.blob(hips, (0, 18, -1), (5.4, 3.6, 4.4), "pale", "pelvis")
    k.box(hips, C(0, 17.0, -1, 9.6, 2.2, 6.6), "leather", tag="rag")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 3.4
        th = k.part("thigh_" + nm, (x, 18, -1), (("x", -40), ("z", side * 10)), "hips")
        sh = k.part("shin_" + nm, (x, 10.0, -1), (("x", 70),), th)
        ft = k.part("foot_" + nm, (x, 2.0, -1), (("x", -30),), sh)
        k.stack(th, x, -1, [(10, 3.6, 3.8), (14, 5.0, 5.2), (18, 4.8, 5.0)], "pale", "thigh")
        k.box(sh, C(x, 2.0, -1, 2.6, 8.2, 2.8), "pale", tag="shin")
        k.box(ft, C(x, 0, 0.6, 3.6, 2.0, 5.6), "pale", tag="foot")
        for t in (-1.0, 0, 1.0):
            k.shard(ft, (x + t, 0.6, 3.2), (0, -0.2, 1), 2.4, 0.8, mat="bone", tag="foot")
    tail = k.part("tail", (0, 16.4, -4.6), (("x", -60),), "hips", bone=False)
    pts = [(0, 16.4, -4.6), (0, 10, -8), (0.6, 5, -13), (1.6, 2.4, -19), (2.4, 1.6, -24)]
    for (a, b), w in zip(zip(pts, pts[1:]), (2.4, 1.8, 1.2, 0.8)):
        k.limb(tail, a, b, w, "pale", "tail")
    # ---------------------------------------------------------------- torso: pitched far forward, mole shoulders, bone plates
    to = k.part("torso", (0, 18.4, -1), (("x", 46),), "hips")
    k.stack(to, 0, -1, [(18.4, 8.6, 6.4), (24, 11.6, 7.4), (30, 14.0, 7.6), (33, 12.4, 6.6)], "pale", "body")
    for kk in range(5):
        y = 20.0 + kk * 3.0
        k.box(to, C(0, y, -5.0, 4.0 - kk * 0.2, 2.4, 1.6), "bone", tag="plate")
        k.shard(to, (0, y + 1.0, -5.6), (0, 0.5, -1), 4.0 + kk * 0.9, 1.8, mat="bone", tag="plate")
        k.shard(to, (2.2, y, -4.8), (0.8, 0.4, -1), 2.4 + kk * 0.4, 1.2, mat="bone", tag="plate")
        k.shard(to, (-2.2, y, -4.8), (-0.8, 0.4, -1), 2.4 + kk * 0.4, 1.2, mat="bone", tag="plate")
    k.box(to, C(0, 22.0, 3.3, 6.0, 7.0, 0.8), "pale", tag="belly")
    k.cluster(to, (3.6, 31, -2.6), 5, 7.0, 2.0, seed=17, up=(0.4, 1, -0.6))
    k.cluster(to, (-4.0, 26, -3.4), 3, 5.0, 1.6, seed=18, up=(-0.6, 0.8, -0.6))
    # ---------------------------------------------------------------- the head: no eyes, a star of feelers
    hd = k.part("head", (0, 32.6, 0.6), (("x", -40),), "torso")
    k.blob(hd, (0, 34.0, 1.6), (3.4, 3.0, 4.0), "pale", "skull")
    k.box(hd, C(0, 32.2, 4.4, 4.0, 2.6, 3.2), "pale", tag="snout")
    k.box(hd, C(0, 31.0, 4.6, 3.6, 0.8, 2.6), "dark", tag="mouth")
    for t in (-1.2, 0, 1.2):
        k.shard(hd, (t, 31.6, 5.8), (0, -1, 0.3), 1.6, 0.6, mat="bone", tag="tooth")
    for a in range(0, 360, 30):        # the star: twelve feelers round the end of the snout
        r = math.radians(a)
        k.shard(hd, (math.cos(r) * 1.4, 33.6 + math.sin(r) * 1.3, 6.0), (math.cos(r) * 0.7, math.sin(r) * 0.7, 1), 3.2, 0.9,
                mat="pink", tag="feeler")
    k.box(hd, C(0, 33.6, 6.0, 1.4, 1.4, 0.6), "pink", tag="feeler")
    for sx in (-2.2, 2.2):
        k.box(hd, C(sx, 35.0, 3.6, 1.6, 0.6, 0.4), "dark", tag="sealed_eye")
    # ---------------------------------------------------------------- arms: short and huge, three spade claws each
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 7.6
        up = k.part("arm_" + nm, (x, 30.4, 0), (("x", -70), ("z", side * 20)), "torso")
        fo = k.part("fore_" + nm, (x, 23.0, 0), (("x", -30),), up)
        hn = k.part("hand_" + nm, (x, 16.0, 0), (), fo)
        k.blob(up, (x, 28, 0), (4.2, 4.0, 4.2), "pale", "shoulder")
        k.stack(up, x, 0, [(23, 4.6, 4.6), (28, 5.4, 5.2)], "pale", "upper_arm")
        k.stack(fo, x, 0, [(16, 6.4, 5.0), (23, 4.8, 4.6)], "pale", "forearm")
        k.box(hn, C(x, 13.4, 0.6, 6.8, 3.2, 4.4), "pale", tag="paw")
        for t in (-2.2, 0, 2.2):
            k.shard(hn, (x + t, 13.6, 1.4), (t * 0.08, -1, 0.5), 13.0, 2.6, mat="bone", tag="claw")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Cart Golem (brute)

def cart_golem():
    """The ore cart the Vein took back: it stood up off its rails and kept going. Its legs are rail iron bent double,
    the cart's wheels for knees; its chest is the cart itself turned on end, open in front, heaped with ore and
    crystal that glows through it; its arms are bundles of rail with boulders lashed on for fists; its head is a lump
    of seam-rock with a pick still buried in it, two pit-lamps for eyes. Chains everywhere it was hauled."""
    k = X.Kit("cart_golem")
    hips = k.part("hips", (0, 24, 0))
    k.box(hips, C(0, 20.6, 0, 15.0, 5.0, 10.0), "rock", tag="pelvis")
    k.box(hips, C(0, 25.0, 0, 17.0, 1.6, 11.6), "rail", tag="axle_bar")
    k.chain(hips, (-8, 24, 5.4), (-6, 14, 6.4), 5)
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 5.4
        th = k.part("thigh_" + nm, (x, 22, 0), (("x", -10), ("z", side * 8)), "hips")
        sh = k.part("shin_" + nm, (x, 12.0, 0), (("x", 16),), th)
        ft = k.part("foot_" + nm, (x, 3.0, 0), (("x", -6),), sh)
        for dz in (-1.6, 1.6):     # each leg two rails side by side, bolted
            k.limb(th, (x, 22, dz), (x, 12, dz), 2.0, "rail", "rail_leg", d=2.6)
            k.limb(sh, (x, 12, dz), (x, 3, dz), 2.0, "rail", "rail_leg", d=2.6)
        k.ring(th, x + side * 1.8, 12.4, 0, 4.0, 1.4, "iron", "knee_wheel", n=12, axis="x")
        k.box(th, C(x + side * 1.8, 11.6, 0, 1.6, 1.6, 9.0), "iron", tag="knee_hub")
        k.blob(sh, (x, 6.4, 0.4), (3.6, 3.0, 3.6), "rock", "shin_rock")
        k.box(ft, C(x, 0, 1.6, 7.0, 3.2, 10.0), "rock", tag="foot")
        k.box(ft, C(x, 2.6, 1.6, 7.6, 1.2, 10.6), "rail", tag="foot_band")
    # ---------------------------------------------------------------- the chest: the cart on end, open, ore heaped in it
    to = k.part("torso", (0, 25, 0), (("x", 14),), "hips")
    CY0, CY1, HW, BZ = 25.0, 45.0, 10.0, -5.6
    k.box(to, C(0, CY0, BZ, HW * 2, CY1 - CY0, 1.6), "iron", tag="cart_floor")
    for side in (1, -1):
        k.box(to, C(side * (HW - 0.8), CY0, BZ + 4.8, 1.6, CY1 - CY0, 9.6), "iron", tag="cart_wall")
    k.box(to, C(0, CY0 - 0.2, BZ + 4.8, HW * 2, 1.6, 9.6), "iron", tag="cart_wall")
    k.box(to, C(0, CY1 - 1.4, BZ + 4.8, HW * 2, 1.6, 9.6), "iron", tag="cart_wall")
    for y in (28.0, 35.0, 42.0):
        k.box(to, C(0, y, BZ + 4.8, HW * 2 + 0.8, 1.2, 10.4), "copper", tag="cart_band")
        k.rivets(to, [(sx * (HW + 0.4), y + 0.2, BZ + 9.2) for sx in (-1, 1)], "iron", 0.8)
    for (x, y, r) in ((-4, 28.5, 3.6), (3.6, 29.6, 3.8), (-2.4, 33.6, 3.4), (4.0, 35.4, 3.0), (-4.2, 38.6, 3.0), (1.0, 39.6, 3.6)):
        k.blob(to, (x, y, BZ + 6.0), (r, r * 0.8, r * 0.9), "slate", "ore")
    k.cluster(to, (0, 31.0, BZ + 6.6), 6, 8.0, 2.4, seed=33, up=(0, 0.4, 1), group="glow")
    k.box(to, C(0, 30.0, BZ + 4.0, 14.0, 12.0, 1.0), "glow", group="glow", tag="ore_light")
    # the cart's own wheels bolted on as shoulder plates
    for side in (1, -1):
        k.ring(to, side * (HW + 1.0), 41.0, 0, 5.0, 1.8, "iron", "shoulder_wheel", n=12, axis="x")
        k.box(to, C(side * (HW + 1.0), 40.2, 0, 1.8, 1.8, 11.0), "iron", tag="shoulder_hub")
    # ---------------------------------------------------------------- the head: a lump of seam-rock, two pit-lamps, a pick in it
    hd = k.part("head", (0, 45, 1.0), (("x", -8),), "torso")
    k.blob(hd, (0, 48.4, 1.4), (5.6, 4.6, 5.2), "rock", "skull")
    k.box(hd, C(0, 49.0, 5.8, 10.4, 1.6, 1.4), "rock", tag="brow")
    for sx in (-2.4, 2.4):
        k.box(hd, C(sx, 47.0, 6.0, 2.6, 2.2, 1.2), "copper", tag="lamp")
        k.box(hd, C(sx, 47.4, 6.7, 1.8, 1.4, 0.3), "eye", group="glow", tag="eye")
    k.box(hd, C(0, 44.4, 4.6, 7.0, 2.0, 2.6), "rock", tag="jaw")
    pk = k.part("buried_pick", (3.0, 52.0, 0.0), (("z", -30), ("x", -10)), hd, bone=False)
    k.limb(pk, (3.0, 52.0, 0.0), (3.0, 62.0, 0.0), 1.2, "timber", "pick_haft")
    k.limb(pk, (3.0, 61.0, -4.0), (3.0, 61.0, 5.0), 1.6, "iron", "pick_head")
    # ---------------------------------------------------------------- arms: rail bundles, boulder fists, chains
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 14.0
        up = k.part("arm_" + nm, (x, 42, 0), (("x", -20), ("z", side * 12)), "torso")
        fo = k.part("fore_" + nm, (x, 30, 0), (("x", -40),), up)
        hn = k.part("hand_" + nm, (x, 18, 0), (), fo)
        for dx, dz in ((-1.2, -1.2), (1.2, -1.2), (0, 1.4)):
            k.limb(up, (x + dx, 42, dz), (x + dx, 30, dz), 1.8, "rail", "rail_arm", d=2.2)
            k.limb(fo, (x + dx, 30, dz), (x + dx, 19, dz), 1.8, "rail", "rail_arm", d=2.2)
        for y in (38.0, 33.0, 26.0, 22.0):
            k.box(up if y > 30 else fo, C(x, y, 0, 5.6, 1.0, 5.6), "iron", tag="lash")
        k.blob(up, (x, 41.4, 0), (4.6, 3.6, 4.6), "rock", "shoulder_rock")
        k.blob(hn, (x, 13.6, 0.6), (6.6, 6.0, 6.4), "rock", "boulder_fist")
        k.box(hn, C(x, 13.0, 0.6, 13.6, 1.6, 13.4), "rail", tag="fist_band")
        k.chain(hn, (x, 9.0, -3.0), (x + side * 2, 2.0, -7.0), 4)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Shard Crawler (swarm, on the spider)

def shard_crawler():
    """A crawler of the deep seams, armoured in plates of seam-rock: a ridge of crystal spines down its back like a
    hackled dog, eight legs in rock segments ending in crystal points that click on the stone, a cluster of glowing
    eyes, mandibles of crystal. They come out of the walls in fives."""
    k = X.Kit("shard_crawler")
    body = k.part("body", (0, 7, 0))
    k.blob(body, (0, 7, 0), (5.0, 3.0, 5.6), "rock", "thorax")
    for kk in range(4):
        k.box(body, C(0, 9.4 - kk * 0.2, 3.6 - kk * 2.4, 8.4 - kk * 0.6, 1.4, 2.4), "slate", tag="plate")
    hd = k.part("head", (0, 7, 5), (), "body")
    k.blob(hd, (0, 6.8, 7.2), (3.4, 2.6, 2.8), "rock", "head")
    for (x, y) in ((-1.2, 8.0), (1.2, 8.0), (-0.6, 8.9), (0.6, 8.9), (-2.0, 7.2), (2.0, 7.2)):
        k.box(hd, C(x, y, 9.85, 0.7, 0.7, 0.3), "eye", group="glow", tag="eye")
    for sx in (-1, 1):
        k.shard(hd, (sx * 1.4, 5.4, 9.4), (sx * 0.3, -0.4, 1), 4.0, 1.2, tag="mandible")
    ab = k.part("abdomen", (0, 7, -4), (("x", -14),), "body")
    k.blob(ab, (0, 8.0, -9.0), (5.6, 4.4, 6.2), "rock", "abdomen")
    # the ridge of spines: down the thorax and over the abdomen, longest in the middle
    for kk, (z, L) in enumerate(((3.0, 4.0), (0.6, 6.0), (-2.0, 7.0), (-5.0, 8.4), (-8.0, 9.0), (-11.0, 6.4), (-13.4, 4.0))):
        part = body if z > -3 else ab
        y = 10.0 if z > -3 else 12.0 - abs(z + 8) * 0.3
        k.shard(part, (0, y, z), (0, 1, -0.35), L, 1.8)
        k.shard(part, (-1.6, y - 0.6, z), (-0.6, 1, -0.3), L * 0.6, 1.2)
        k.shard(part, (1.6, y - 0.6, z), (0.6, 1, -0.3), L * 0.6, 1.2)
    k.box(ab, C(0, 4.0, -9.0, 5.0, 3.0, 5.0), "glow", group="glow", tag="belly_glow")
    joints = {"body": "Root", "head": "Head", "abdomen": "Stomach"}
    for side, s in ((1, "l"), (-1, "r")):
        for i, z in enumerate((3.0, 1.0, -1.2, -3.4)):
            nm = "leg_%s%d" % (s, i)
            lg = k.part(nm, (side * 4.0, 7, z), (("y", -side * (i - 1.5) * 22),), "body")
            knee = (side * 10.0, 13.0, z)
            foot = (side * 15.0, 0.0, z)
            k.limb(lg, (side * 4.0, 7.4, z), knee, 1.8, "rock", "femur")
            k.box(lg, C(knee[0], knee[1] - 1.2, z, 2.4, 2.4, 2.4), "slate", tag="knee")
            k.limb(lg, knee, (side * 13.6, 3.0, z), 1.4, "rock", "tibia")
            k.shard(lg, (side * 13.6, 3.6, z), (side * 0.3, -1, 0), 4.0, 1.2, tag="foot")
            joints[nm] = ("LL" if side > 0 else "RL") + str(i + 1)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


# ================================================================ registry (monsterforge.export reads these)

MOBS = {
    "shard_crawler": dict(make=shard_crawler, rig="crawler", ent=(1.0, 0.7), stats=dict(hp=18, speed=0.3, dmg=4, armor=4, kb=0)),
    "cart_golem": dict(make=cart_golem, ent=(1.6, 3.8), stats=dict(hp=70, speed=0.18, dmg=11, armor=8, kb=0.9)),
    "lamp_miner": dict(make=lamp_miner, ent=(0.9, 2.6), stats=dict(hp=28, speed=0.22, dmg=5, armor=2, kb=0)),
    "blind_burrower": dict(make=blind_burrower, ent=(1.0, 2.2), stats=dict(hp=24, speed=0.32, dmg=6, armor=0, kb=0)),
    "foreman": dict(make=foreman, ent=(1.2, 3.1), stats=dict(hp=140, speed=0.21, dmg=11, armor=8, kb=0.7), key=True),
    "the_vein": dict(make=the_vein, texel=1, ent=(3.0, 6.2), stats=dict(hp=420, speed=0.2, dmg=16, armor=10, kb=1.0), boss=True),
}
