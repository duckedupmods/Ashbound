"""Brigand's Gorge's monsters, each built by hand (tools/vox2.py). The cut through the red hills where the road
goes in and nobody comes out: Red Jack's band - sun-cracked leather, red rags, stolen plate, stolen gold, campfire
light, and the green fire of the hedge-witches who ride with them.

    footpad            swarm   a lean cutthroat: hood, scarf mask, a cloak in strips, two curved knives
    gorge_ogre         brute   the band's ogre: tusks, a belly in a cart-wheel girdle, a cleaver, a cage of loot on its back
    hedge_hexer        caster  the hedge-witch: a ram-skull mask, charms and bones, a crook with green fire in a cage
    knife_dancer       skirm   all sash and blade: knives up both arms, a long red scarf, a mask with a painted grin
    bandit_lieutenant  elite   Jack's right hand: stolen plate, a horned helm, a red cloak, the band's banner, a poleaxe
    red_jack           boss    the bandit king: a giant in a red greatcoat, a crown nailed to his helm, a cleaver and a hook

    python tools/monsterforge.py brigands_gorge --preview ; python tools/mobsheet.py brigands_gorge
"""
import math

import vox2 as X
from vox2 import C, ramp

LEATHER = ramp("#120a06", "#1e120a", "#2e1c10", "#402816", "#54361e", "#6a4628")
RED = ramp("#1e0606", "#360a0a", "#540e0e", "#761616", "#9a2020", "#c03030")
IRON = ramp("#0e0e10", "#18181c", "#26262c", "#36363e", "#4a4a52", "#62626a")
RUST = ramp("#2a1408", "#44200c", "#5e2e12", "#7a3e18")
GOLD = ramp("#3a2606", "#5e400c", "#8a6214", "#b48a24", "#dab43c", "#f4d870")
SKIN = ramp("#2a1a12", "#40281a", "#583824", "#704a30", "#8a5e3e")
OGRE = ramp("#1a1e10", "#262c16", "#343c1e", "#444e28", "#566234")
FUR = ramp("#100c08", "#1c150e", "#2a2016", "#3a2e20", "#4c3e2c")
BONE = ramp("#3a3428", "#5a5240", "#7c7258", "#9e9476", "#c0b896")
WOOD = ramp("#140c06", "#20140a", "#2e1e10", "#3e2a16", "#50381e")
FIRE = ramp("#3a0e04", "#6a1e06", "#9a360a", "#c45412", "#e07a22")
HEX = ramp("#0a3a0a", "#167016", "#30aa22", "#7ae04a", "#d4ff9a")
CLOTH = ramp("#1a1610", "#262016", "#342c1e", "#443a28", "#584c36")


def shaders():
    return {
        "leather": X.surf(LEATHER, 0.5, 1.2, 0.24, 0.06, drip=(FUR, 0.1)),
        "red": X.surf(RED, 0.5, 1.1, 0.22, 0.0, holes=True),
        "redcoat": X.surf(RED, 0.52, 1.2, 0.2, 0.04),
        "iron": X.surf(IRON, 0.52, 1.4, 0.16, 0.18, rust=(RUST, 0.3, 0.4)),
        "steel": X.surf(IRON, 0.66, 1.4, 0.08, 0.3),
        "gold": X.surf(GOLD, 0.56, 1.3, 0.14, 0.2),
        "skin": X.wrinkled(SKIN, 0.7),
        "ogre": X.wrinkled(OGRE, 0.9),
        "fur": X.surf(FUR, 0.5, 0.9, 0.3, 0.0, stripe=2),
        "beard": X.surf(FIRE, 0.5, 1.0, 0.3, 0.0, stripe=2),
        "bone": X.surf(BONE, 0.6, 1.1, 0.16, 0.12),
        "wood": X.surf(WOOD, 0.5, 1.0, 0.2, 0.06, stripe=3),
        "cloth": X.surf(CLOTH, 0.48, 1.0, 0.24, 0.0, holes=True),
        "glow": X.glow(HEX),
        "eye": X.glow(GOLD, 0.82, 0.16),
        "hexeye": X.glow(HEX, 0.8, 0.18),
        "dark": X.dark(LEATHER),
    }


def straps(k, part, x0, x1, y0, y1, z, w=1.0, mat="leather"):
    k.limb(part, (x0, y0, z), (x1, y1, z), w, mat, "strap", d=0.5)


# ================================================================ Red Jack (boss)

def red_jack():
    """The bandit king of the gorge. A giant of a man - they say he ate the toll-keeper's horse - in a red greatcoat
    stiff with the blood of the road, the skirts to his ankles, brass buttons torn off a general. His helm is iron
    with two bull horns, and nailed round its brow, upside down, the crown of the last lord who sent soldiers in. A
    red beard like a fire; gold in his teeth. Across his chest the bandoliers hang heavy with rings and coins and
    signet fingers; on his back the banners of every company he has broken. In one hand a cleaver the size of a
    door, in the other a meat hook on a chain he throws and drags back."""
    k = X.Kit("red_jack")
    hips = k.part("hips", (0, 34, 0))
    k.stack(hips, 0, 0, [(28, 18, 12), (34, 20, 13)], "leather", "breeches")
    k.box(hips, C(0, 33, 0, 21, 3.0, 14), "leather", tag="belt")
    k.box(hips, C(0, 32.6, 7.2, 6.0, 4.0, 1.0), "gold", tag="buckle")
    k.box(hips, C(0, 33.4, 7.8, 3.0, 2.2, 0.6), "dark", tag="buckle")
    # the greatcoat's skirts: long panels all round, split at front and back, to the ankles
    for (x, z, sz, lean) in ((-6.6, 7.4, 7, 6), (6.6, 7.4, 7, 6), (-10.6, 0, 1, 0), (10.6, 0, 1, 0), (-5.4, -7.4, 8, -8), (5.4, -7.4, 8, -8)):
        cp = k.part("skirt%d%d" % (x > 0, z > 0 if z else 2), (x, 33, z), (("x", lean),), hips, bone=False)
        if sz == 1:
            k.box(cp, C(x, 6, z, 1.2, 27, 13), "redcoat", tag="skirt")
        else:
            k.box(cp, C(x, 5, z, sz, 28, 1.2), "redcoat", tag="skirt")
            k.box(cp, C(x, 5, z, sz + 0.4, 1.6, 1.6), "dark", tag="hem")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 5
        th = k.part("thigh_" + nm, (x, 31, 0), (("x", -10), ("z", side * 7)), "hips")
        sh = k.part("shin_" + nm, (x, 17, 0), (("x", 14),), th)
        ft = k.part("foot_" + nm, (x, 4, 0), (("x", -4),), sh)
        k.stack(th, x, 0, [(17, 8, 8.4), (24, 9.4, 9.6), (31, 9.0, 9.2)], "leather", "thigh")
        k.stack(sh, x, 0, [(3, 8.6, 9), (10, 9.6, 10), (17, 9.0, 9.4)], "leather", "boot")
        k.box(sh, C(x, 15.4, 0, 10.6, 3.4, 11.0), "leather", tag="boot_cuff")
        for y in (6, 10):
            k.box(sh, C(x, y, 0, 10.0, 1.0, 10.4), "iron", tag="boot_strap")
        k.box(ft, C(x, 0, 2.4, 9.4, 4.4, 14), "leather", tag="foot")
        k.box(ft, C(x, 0, 8.8, 8.0, 2.4, 2.0), "iron", tag="foot")
    # ---------------------------------------------------------------- torso: the coat, bandoliers of loot, a barrel chest
    to = k.part("torso", (0, 35, 0), (("x", 10),), "hips")
    k.stack(to, 0, 0, [(34, 20, 13), (42, 26, 15), (50, 31, 16), (55, 30, 15)], "redcoat", "coat")
    k.box(to, C(0, 36, 7.6, 6.0, 18, 1.0), "leather", tag="waistcoat")
    for y in (38, 42, 46, 50):
        for sx in (-4.2, 4.2):
            k.box(to, C(sx, y, 8.3, 1.4, 1.4, 0.6), "gold", tag="button")
    for sx in (-1, 1):       # lapels and the epaulettes he took off a general
        k.box(to, C(sx * 6.4, 44, 8.2, 3.6, 11, 0.8), "redcoat", tag="lapel")
        k.box(to, C(sx * 15.2, 54.6, 0, 9.0, 1.6, 11.0), "gold", tag="epaulette")
        for i in range(5):
            k.limb(to, (sx * (11.6 + i * 1.8), 54.6, 4.8), (sx * (11.6 + i * 1.8), 51.0, 5.0), 0.6, "gold", "fringe")
    for sx in (-1, 1):       # two bandoliers crossed, hung with rings, coins and fingers
        a, b = (sx * 13, 54, 8.2), (-sx * 9, 35, 8.6)
        k.limb(to, a, b, 2.4, "leather", "bandolier", d=0.8)
        for t in (0.2, 0.35, 0.5, 0.65, 0.8):
            p = tuple(a[i] + (b[i] - a[i]) * t for i in range(3))
            if int(t * 20) % 2:
                k.box(to, C(p[0], p[1] - 2.4, p[2] + 0.6, 1.6, 1.6, 0.6), "gold", tag="coin")
            else:
                k.ring(to, p[0], p[1] - 1.8, p[2] + 0.8, 1.0, 0.5, "gold", "ring", n=6)
    # the banners on his back: three poles, torn cloth, each a different broken company
    for i, (x, h, lean, col) in enumerate(((-7, 30, -12, "cloth"), (0, 36, 0, "red"), (7, 28, 14, "steel"))):
        bp = k.part("banner%d" % i, (x, 40, -8), (("z", lean),), to, bone=False)
        k.limb(bp, (x, 38, -8.6), (x, 56 + h * 0.5, -8.6), 1.2, "wood", "pole")
        k.shard(bp, (x, 56 + h * 0.5, -8.6), (0, 1, 0), 3.4, 1.2, mat="iron", tag="finial")
        k.box(bp, C(x + 3.6, 56 + h * 0.5 - 13, -8.6, 7.0, 12, 0.6), "red" if col == "red" else "cloth", tag="banner")
        k.box(bp, C(x + 3.6, 56 + h * 0.5 - 8, -8.9, 3.0, 3.0, 0.3), "gold" if i != 1 else "bone", tag="device")
    # ---------------------------------------------------------------- the head: horned helm, the crown upside down, red beard
    hd = k.part("head", (0, 55, 1), (("x", -8),), "torso")
    k.box(hd, C(0, 55.4, 1.2, 9.6, 8.6, 9.6), "skin", tag="face")
    k.blob(hd, (0, 64.6, 1.0), (5.6, 3.4, 5.8), "iron", "helm")
    k.box(hd, C(0, 61.4, 1.2, 11.6, 2.4, 11.8), "iron", tag="helm_rim")
    k.box(hd, C(0, 57.6, 6.3, 1.8, 5.6, 1.0), "iron", tag="nasal")
    for sx in (-1, 1):       # bull horns: out, then up and forward
        pts = [(sx * 5.6, 64, 1), (sx * 10, 65.4, 1.4), (sx * 13.4, 68.4, 2.4), (sx * 14.6, 72.6, 4.4)]
        for (a, b), w in zip(zip(pts, pts[1:]), (3.0, 2.2, 1.4)):
            k.limb(hd, a, b, w, "bone", "horn")
    for i in range(8):       # the crown, nailed on upside down: points hanging over his brow
        a = math.radians(i * 45)
        x, z = math.sin(a) * 6.0, 1.2 + math.cos(a) * 6.0
        k.box(hd, C(x, 61.8, z, 2.6, 1.8, 2.6), "gold", tag="crown")
        if i % 2 == 0:
            k.shard(hd, (x, 62.0, z), (0, -1, 0), 2.6, 1.6, mat="gold", tag="crown_point")
    k.box(hd, C(0, 62.6, 7.4, 1.6, 1.6, 0.6), "glow", group="glow", tag="jewel")
    for sx in (-2.4, 2.4):
        k.box(hd, C(sx, 58.4, 6.1, 2.4, 1.0, 0.4), "eye", group="glow", tag="eye")
    k.box(hd, C(0, 54.4, 6.1, 5.0, 1.0, 0.4), "dark", tag="mouth")
    for t in (-1.6, 0, 1.6):
        k.box(hd, C(t, 54.6, 6.2, 0.8, 0.8, 0.4), "gold", tag="gold_tooth")
    k.stack(hd, 0, 4.6, [(42, 4, 3), (46, 8, 4.6), (51, 11, 5.4), (55, 10.4, 4.6)], "beard", "beard")
    k.box(hd, C(0, 55.8, 6.4, 7.4, 1.4, 1.2), "beard", tag="mustache")
    # ---------------------------------------------------------------- arms: coat sleeves with cuffs, iron gauntlets
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 18
        up = k.part("arm_" + nm, (x, 52, 0), (("x", -30 if side > 0 else -50), ("z", side * 12)), "torso")
        fo = k.part("fore_" + nm, (x, 39, 0), (("x", -40 if side > 0 else -40),), up)
        hn = k.part("hand_" + nm, (x, 26, 0), (), fo)
        k.blob(up, (x, 51, 0), (6.4, 5.0, 6.6), "redcoat", "shoulder")
        k.stack(up, x, 0, [(39, 8.4, 8.6), (46, 9.6, 9.8), (52, 10.4, 10.4)], "redcoat", "sleeve")
        k.stack(fo, x, 0, [(27, 10.4, 10.4), (31, 10.8, 10.8), (39, 8.6, 8.8)], "redcoat", "sleeve")
        k.box(fo, C(x, 27, 0, 11.4, 5.0, 11.4), "leather", tag="cuff")
        k.box(hn, C(x, 20, 0.6, 8.0, 6.6, 8.0), "iron", tag="gauntlet")
        for t in (-2.4, 0, 2.4):
            k.box(hn, C(x + t, 22.6, 4.8, 1.6, 1.6, 0.8), "iron", tag="knuckle_spike")
    # the cleaver: a slab of iron like a door, a hole for hanging, the edge bright
    cv = k.part("cleaver", (-18, 23, 0.6), (("x", 80),), k.parts["hand_r"])
    k.limb(cv, (-18, 14, 0.6), (-18, 28, 0.6), 2.2, "wood", "handle")
    k.box(cv, C(-18, 28, 0.6 - 3, 2.2, 42, 20), "iron", tag="blade")
    k.box(cv, C(-18, 28, 0.6 + 16.4, 1.4, 42, 1.6), "steel", tag="edge")
    k.box(cv, C(-18, 63, 0.6 + 1, 2.6, 4, 4), "dark", tag="hole")
    for (y, z) in ((34, 14.8), (44, 15.6), (56, 14.6)):
        k.box(cv, C(-18, y, z, 2.4, 2.0, 1.6), "dark", tag="notch")
    k.box(cv, C(-18, 28, 0.6 - 3, 2.6, 2.0, 20.4), "iron", tag="spine")
    k.box(cv, C(-18, 68, 0.6 - 3, 2.6, 2.0, 20.4), "iron", tag="spine")
    # the hook on its chain, in the left hand
    hk = k.part("hook", (18, 22, 1), (("x", 30),), k.parts["hand_l"])
    k.chain(hk, (18, 22, 1), (18, 4, 3), 6, w=1.6)
    k.limb(hk, (18, 4, 3), (18, -4, 3), 1.8, "steel", "hook")
    k.limb(hk, (18, -4, 3), (18, -6, 7), 1.8, "steel", "hook")
    k.limb(hk, (18, -6, 7), (18, -2, 9.4), 1.6, "steel", "hook")
    k.shard(hk, (18, -2, 9.4), (0, 1, -0.2), 4.0, 1.6, mat="steel", tag="hook")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Bandit Lieutenant (elite, the key)

def bandit_lieutenant():
    """Jack's right hand, who holds the gate: stolen plate that never matched - a knight's breastplate, a
    sergeant's pauldron, mail on one arm - a bucket helm with ram's horns bolted on and a red plume, a red cloak
    in rags, the band's banner (a red hand on black) on a pole at his back, and a poleaxe as tall as he is. The
    gate keys hang on his belt."""
    k = X.Kit("bandit_lieutenant")
    hips = k.part("hips", (0, 21, 0))
    k.stack(hips, 0, 0, [(16, 11.4, 7.4), (21, 12.4, 8.0)], "leather", "breeches")
    for x in (-3.6, 0, 3.6):
        k.box(hips, C(x, 13.0, 4.2, 3.6, 6.0, 0.8), "iron", tag="tasset")
    k.box(hips, C(0, 20.4, 0, 13.0, 1.8, 8.6), "leather", tag="belt")
    k.ring(hips, -6.6, 15.4, 2.2, 1.8, 0.5, "iron", "keyring", n=8)
    for dx, L in ((-0.8, 3.6), (0, 4.6), (0.8, 3.0)):
        k.box(hips, C(-6.6 + dx, 13.6 - L * 0.5, 2.4, 0.5, L, 0.4), "gold", tag="key")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 3.2
        th = k.part("thigh_" + nm, (x, 20, 0), (("x", -6), ("z", side * 5)), "hips")
        sh = k.part("shin_" + nm, (x, 10.6, 0), (("x", 10),), th)
        ft = k.part("foot_" + nm, (x, 2.4, 0), (("x", -4),), sh)
        k.box(th, C(x, 10.8, 0, 5.0, 9.4, 5.4), "leather", tag="thigh")
        k.box(th, C(x, 9.6, 1.0, 5.6, 3.0, 5.0), "iron", tag="poleyn")
        k.shard(th, (x, 10.8, 3.6), (0, 0, 1), 2.0, 1.4, mat="iron", tag="poleyn")
        k.box(sh, C(x, 2.4, 0, 5.0, 8.4, 5.4), "iron", tag="greave")
        k.box(ft, C(x, 0, 1.2, 5.4, 2.8, 8.0), "leather", tag="foot")
    # the cloak behind, long and torn
    cl = k.part("cloak", (0, 35, -4.6), (("x", -6),), "hips", bone=False)
    for i, x in enumerate((-5, -1.6, 1.8, 5.2)):
        k.box(cl, C(x, 3 + i % 2 * 2, -4.8, 3.6, 31 - i % 2 * 2, 0.8), "red", tag="cloak")
    # ---------------------------------------------------------------- torso: the knight's breastplate, one pauldron
    to = k.part("torso", (0, 21, 0), (("x", 6),), "hips")
    k.stack(to, 0, 0, [(21, 12.4, 8.0), (27, 15.0, 9.0), (32, 17.0, 9.6), (35.6, 15.4, 8.6)], "leather", "gambeson")
    k.stack(to, 0, 0.6, [(24, 13.4, 8.6), (29, 16.0, 9.6), (34, 16.4, 9.4)], "iron", "breastplate")
    k.box(to, C(0, 24, 5.2, 1.4, 10, 0.6), "steel", tag="ridge")
    k.box(to, C(0, 28.4, 5.4, 3.6, 3.6, 0.6), "red", tag="red_hand")
    for (sx, sy) in ((-1.2, 2.4), (-0.4, 2.8), (0.4, 2.8), (1.2, 2.2)):
        k.box(to, C(sx, 31.6, 5.4, 0.6, sy, 0.6), "red", tag="red_hand")
    k.blob(to, (9.4, 34.4, 0), (5.4, 3.6, 5.6), "iron", "pauldron")
    for y in (31.4, 32.8):
        k.box(to, C(10.4, y, 0, 7.2, 1.4, 10.6), "iron", tag="lame")
    k.shard(to, (11, 37.4, 0), (0.5, 1, 0), 4.0, 2.0, mat="steel", tag="pauldron_spike")
    k.blob(to, (-8.6, 34.4, 0), (4.0, 2.8, 4.4), "fur", "fur_mantle")
    # the banner pole on the back: a red hand on black, a skull on top
    bn = k.part("banner", (4, 30, -5), (("z", -6),), to, bone=False)
    k.limb(bn, (4, 18, -5.6), (4, 58, -5.6), 1.0, "wood", "pole")
    k.limb(bn, (4, 56, -5.6), (-6, 56, -5.6), 0.8, "wood", "crossbar")
    k.box(bn, C(-1, 41, -5.6, 10, 15, 0.6), "dark", tag="banner")
    k.box(bn, C(-1, 46, -5.2, 4.4, 4.4, 0.4), "red", tag="banner_hand")
    for sx in (-2.2, -0.8, 0.6, 2.0):
        k.box(bn, C(-1 + sx * 0.8, 50.2, -5.2, 0.8, 3.0, 0.4), "red", tag="banner_hand")
    k.box(bn, C(-1, 39, -5.6, 10, 1.6, 0.6), "red", tag="banner_hem")
    k.box(bn, C(4, 58, -5.6, 2.6, 2.6, 2.6), "bone", tag="skull")
    # ---------------------------------------------------------------- the helm: a bucket with ram horns and a plume
    hd = k.part("head", (0, 35.6, 0.4), (("x", -6),), "torso")
    k.box(hd, C(0, 35.4, 0.4, 6.8, 7.2, 7.0), "iron", tag="helm")
    k.box(hd, C(0, 39.2, 3.95, 5.0, 0.9, 0.4), "dark", tag="visor")
    k.box(hd, C(0, 37.6, 3.95, 0.9, 1.8, 0.4), "dark", tag="visor")
    for sx in (-1.4, 1.4):
        k.box(hd, C(sx, 39.3, 4.05, 1.4, 0.6, 0.3), "eye", group="glow", tag="eye")
    for i in range(6):
        k.box(hd, C(1.6 - i * 0.7, 37.0, 4.0, 0.4, 0.4, 0.3), "dark", tag="breath")
    for sx in (-1, 1):       # ram horns curling round the sides
        pts = [(sx * 3.4, 40, 0), (sx * 5.6, 41.6, -1.4), (sx * 6.8, 40, -2.8), (sx * 6.4, 37.4, -1.0), (sx * 5.4, 36.4, 1.4)]
        for (a, b), w in zip(zip(pts, pts[1:]), (2.0, 1.8, 1.5, 1.2)):
            k.limb(hd, a, b, w, "bone", "horn")
    for i in range(5):
        k.box(hd, C(0, 43.0 + i * 0.6, 1.8 - i * 1.6, 1.4, 1.8, 1.8), "red", tag="plume")
    # ---------------------------------------------------------------- arms: mail on the left, leather on the right
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 9.4
        up = k.part("arm_" + nm, (x, 33, 0), (("x", -40 if side > 0 else -20), ("z", side * 10)), "torso")
        fo = k.part("fore_" + nm, (x, 24, 0), (("x", -60 if side > 0 else -70),), up)
        hn = k.part("hand_" + nm, (x, 15.6, 0), (), fo)
        k.box(up, C(x, 24.8, 0, 4.6, 8.6, 4.8), "steel" if side > 0 else "leather", tag="sleeve")
        k.box(fo, C(x, 16.4, 0, 4.4, 8.0, 4.6), "iron", tag="vambrace")
        k.box(hn, C(x, 12.6, 0.4, 4.2, 3.8, 4.2), "leather", tag="glove")
    # the poleaxe: a long haft, an axe blade, a hammer back, a spike
    px = k.part("poleaxe", (9.4, 13.8, 0.6), (("x", 70),), k.parts["hand_l"])
    k.limb(px, (9.4, -14, 0.6), (9.4, 36, 0.6), 1.4, "wood", "haft")
    for y in (4.0, 12.0):
        k.ring(px, 9.4, y, 0.6, 1.2, 0.6, "leather", "wrap", n=8, axis="y")
    k.box(px, C(9.4, 28, 2.0, 1.2, 10, 7), "iron", tag="axe_blade")
    k.box(px, C(9.4, 26.6, 8.6, 1.4, 12.6, 1.2), "steel", tag="axe_edge")
    k.box(px, C(9.4, 31, -3.4, 2.6, 3.2, 3.6), "iron", tag="hammer")
    k.shard(px, (9.4, 36, 0.6), (0, 1, 0), 6.0, 1.8, mat="steel", tag="spike")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Gorge Ogre (brute)

def gorge_ogre():
    """The band keeps an ogre the way other bands keep a dog. Olive-grey, belly like a barrel strapped into an old
    cart wheel for a girdle, lower tusks up past its nose, a ring through it, tiny mean eyes. On its back a wooden
    cage of loot - and a prisoner, still in it. It swings a butcher's cleaver made from a plough blade."""
    k = X.Kit("gorge_ogre")
    hips = k.part("hips", (0, 21, 0))
    k.stack(hips, 0, 0, [(15, 15, 11), (21, 17, 12)], "fur", "loincloth")
    k.box(hips, C(0, 6, 6, 6, 10, 0.8), "fur", tag="flap")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 5.0
        th = k.part("thigh_" + nm, (x, 19, 0), (("x", -10), ("z", side * 10)), "hips")
        sh = k.part("shin_" + nm, (x, 10, 0), (("x", 16),), th)
        ft = k.part("foot_" + nm, (x, 2.6, 0), (("x", -6),), sh)
        k.stack(th, x, 0, [(10, 7.6, 7.6), (15, 9.0, 9.0), (19, 8.4, 8.4)], "ogre", "thigh")
        k.stack(sh, x, 0, [(2.6, 6.8, 7.0), (7, 7.6, 7.6), (10, 7.0, 7.0)], "ogre", "shin")
        k.ring(sh, x, 6, 0, 4.2, 1.0, "leather", "wrap", n=10, axis="y")
        k.box(ft, C(x, 0, 1.6, 8.0, 3.0, 10.4), "ogre", tag="foot")
        for t in (-2.4, 0, 2.4):
            k.box(ft, C(x + t, 0.4, 6.6, 1.8, 1.4, 1.2), "bone", tag="toenail")
    # ---------------------------------------------------------------- torso: the belly in a cart-wheel girdle, hunched shoulders
    to = k.part("torso", (0, 21, 0), (("x", 18),), "hips")
    k.blob(to, (0, 25, 2.4), (10.4, 7.4, 8.6), "ogre", "belly")
    k.stack(to, 0, -1, [(27, 20, 13), (33, 26, 14), (38, 24, 12)], "ogre", "chest")
    k.ring(to, 0, 24, 2.4, 10.2, 1.8, "wood", "wheel", n=16, axis="y")
    for a in range(0, 360, 60):
        r = math.radians(a)
        k.box(to, C(math.cos(r) * 9.4, 23.4, 2.4 + math.sin(r) * 9.4, 2.2, 2.0, 2.2), "iron", tag="wheel_stud")
    k.blob(to, (0, 38, -2), (9.0, 4.4, 6.0), "ogre", "hump")
    k.limb(to, (-11, 37, 4), (8, 22, 9), 1.8, "leather", "strap", d=0.6)
    # the loot cage on its back, a prisoner's hands through the bars
    cg = k.part("cage", (0, 34, -9), (), to, bone=False)
    k.box(cg, C(0, 28, -14, 13, 1.4, 9), "wood", tag="cage_floor")
    k.box(cg, C(0, 43, -14, 13, 1.4, 9), "wood", tag="cage_roof")
    for x in (-6, -3, 0, 3, 6):
        for z in (-9.8, -18.2):
            k.box(cg, C(x, 29, z, 1.0, 14, 1.0), "wood", tag="bar")
    for z in (-12, -15):
        for x in (-6.2, 6.2):
            k.box(cg, C(x, 29, z, 1.0, 14, 1.0), "wood", tag="bar")
    k.box(cg, C(0, 29.4, -14, 8, 6, 6), "gold", tag="loot")
    k.box(cg, C(-1, 35.4, -14.4, 4.6, 5.0, 4.6), "cloth", tag="prisoner")
    k.box(cg, C(-1, 40.4, -14.4, 3.4, 3.4, 3.4), "skin", tag="prisoner")
    k.box(cg, C(-1, 37.6, -18.6, 2.2, 1.2, 1.4), "skin", tag="prisoner_hand")
    k.ring(cg, 0, 44.6, -14, 1.8, 0.8, "iron", "cage_ring", n=8)
    # ---------------------------------------------------------------- the head: set low, tusks, a nose ring
    hd = k.part("head", (0, 37, 4), (("x", -20),), "torso")
    k.box(hd, C(0, 36.0, 5.4, 9.0, 7.6, 8.2), "ogre", tag="head")
    k.box(hd, C(0, 34.4, 8.6, 10.0, 3.6, 4.4), "ogre", tag="jaw")
    k.box(hd, C(0, 42.2, 7.6, 9.6, 1.6, 2.6), "ogre", tag="brow")
    k.box(hd, C(0, 39.2, 9.8, 3.0, 3.0, 2.0), "ogre", tag="nose")
    k.ring(hd, 0, 38.6, 11.0, 1.2, 0.5, "gold", "nose_ring", n=8, axis="x")
    for sx in (-2.4, 2.4):
        k.box(hd, C(sx, 41.0, 9.5, 1.4, 0.8, 0.4), "eye", group="glow", tag="eye")
        k.shard(hd, (sx * 1.1, 37.4, 10.4), (sx * 0.15, 1, 0.2), 5.0, 1.6, mat="bone", tag="tusk")
    for sx in (-1, 1):
        k.shard(hd, (sx * 4.6, 39.6, 5.4), (sx * 1, 0.4, -0.4), 3.4, 1.6, mat="ogre", tag="ear")
    # ---------------------------------------------------------------- arms: hanging to the knees, fists like stones
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 13.0
        up = k.part("arm_" + nm, (x, 35, 0), (("x", -10 if side > 0 else -40), ("z", side * 12)), "torso")
        fo = k.part("fore_" + nm, (x, 24, 0), (("x", -20 if side > 0 else -50),), up)
        hn = k.part("hand_" + nm, (x, 13, 0), (), fo)
        k.blob(up, (x, 33.6, 0), (5.4, 4.6, 5.4), "ogre", "shoulder")
        k.stack(up, x, 0, [(24, 6.6, 6.8), (30, 7.6, 7.8)], "ogre", "upper_arm")
        k.stack(fo, x, 0, [(14, 8.0, 8.0), (20, 8.6, 8.6), (24, 7.0, 7.0)], "ogre", "forearm")
        k.box(fo, C(x, 15, 0, 9.0, 3.0, 9.0), "leather", tag="bracer")
        k.box(hn, C(x, 8.0, 0.6, 7.4, 6.0, 7.4), "ogre", tag="fist")
    # the plough-blade cleaver
    cv = k.part("cleaver", (-13, 11, 0.6), (("x", 70),), k.parts["hand_r"])
    k.limb(cv, (-13, 4, 0.6), (-13, 16, 0.6), 1.8, "wood", "handle")
    k.box(cv, C(-13, 16, -1.4, 1.6, 20, 12), "iron", tag="blade")
    k.box(cv, C(-13, 16, 10.0, 1.0, 20, 1.2), "steel", tag="edge")
    for y in (20, 28):
        k.rivets(cv, [(-13.9, y, 1), (-13.9, y, 5)], "iron", 1.0)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Hedge Hexer (caster)

def hedge_hexer():
    """The band's hedge-witch, who reads the bones before every job. Under a cloak of patched hides and feathers,
    a ram's skull worn as a mask, the horns curling; strings of charms, teeth, little bones and bells hang off
    everything. The crook she leans on has an iron cage at the top with a green fire in it that speaks."""
    k = X.Kit("hedge_hexer")
    hips = k.part("hips", (0, 18, 0))
    k.stack(hips, 0, 0, [(12, 10.4, 8.0), (18, 9.0, 6.4)], "fur", "skirt")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.4
        th = k.part("thigh_" + nm, (x, 18, 0), (("x", -6),), "hips")
        sh = k.part("shin_" + nm, (x, 9.6, 0), (("x", 10),), th)
        ft = k.part("foot_" + nm, (x, 2, 0), (), sh)
        k.box(th, C(x, 9.4, 0, 4.8, 9.0, 6.4), "cloth", tag="skirt")
        k.box(sh, C(x, 1.6, 0, 5.0, 8.4, 6.8), "cloth", tag="skirt")
        k.box(ft, C(x, 0, 1.2, 3.2, 1.8, 5.4), "leather", tag="foot")
    for (x, z, L) in ((-4.4, 3.0, 10), (-1.4, 3.6, 8), (2.2, 3.4, 12), (4.6, 1.6, 9)):       # the charms at the belt
        k.limb(hips, (x, 17.4, z), (x, 17.4 - L, z + 0.4), 0.4, "leather", "cord")
        k.box(hips, C(x, 16.4 - L, z + 0.4, 1.2, 1.4, 1.0), "bone" if L % 2 else "gold", tag="charm")
    # ---------------------------------------------------------------- torso: hunched under a cloak of hides and feathers
    to = k.part("torso", (0, 18, 0), (("x", 20),), "hips")
    k.stack(to, 0, 0, [(18, 9.0, 6.4), (24, 11.4, 7.2), (29, 13.0, 7.6)], "cloth", "body")
    k.stack(to, 0, -0.4, [(14, 15, 9.6), (22, 15.6, 9.6), (29, 14.6, 8.8), (31.6, 12, 8)], "fur", "cloak")
    for i in range(14):      # a collar of feathers, dark, sticking up and out
        a = math.radians(-100 + i * 15)
        k.shard(to, (math.sin(a) * 5.4, 30.4, math.cos(a) * 3.6 - 0.6), (math.sin(a) * 0.6, 1, math.cos(a) * 0.5 - 0.3),
                4.6 + (i % 3), 1.4, mat="dark" if i % 2 else "fur", tag="feather")
    for i, x in enumerate((-3.4, -1.2, 1.2, 3.4)):           # a necklace of finger bones
        k.box(to, C(x, 26.6 + abs(x) * 0.4, 4.0, 0.8, 1.8, 0.6), "bone", tag="necklace")
    k.box(to, C(0, 25.6, 4.2, 1.8, 1.8, 0.6), "glow", group="glow", tag="amulet")
    # ---------------------------------------------------------------- the head: the ram skull mask, a hood behind it
    hd = k.part("head", (0, 30, 0.8), (("x", -16),), "torso")
    k.box(hd, C(0, 30.4, 0, 6.6, 6.6, 6.6), "fur", tag="hood")
    k.box(hd, C(0, 30.2, 3.0, 4.4, 5.4, 2.8), "bone", tag="skull_mask")
    k.box(hd, C(0, 29.0, 5.2, 3.0, 2.4, 2.4), "bone", tag="snout")
    k.box(hd, C(0, 30.4, 6.4, 1.6, 0.8, 0.3), "dark", tag="nostril")
    for sx in (-1.2, 1.2):
        k.box(hd, C(sx, 33.0, 4.35, 1.4, 1.2, 0.3), "dark", tag="socket")
        k.box(hd, C(sx, 33.3, 4.45, 0.8, 0.6, 0.3), "hexeye", group="glow", tag="eye")
    for sx in (-1, 1):       # curling ram horns
        pts = [(sx * 2.0, 35.6, 2.4), (sx * 4.4, 37.0, 1.0), (sx * 6.2, 35.6, -0.6), (sx * 6.4, 33.0, 0.4), (sx * 5.4, 31.4, 2.4)]
        for (a, b), w in zip(zip(pts, pts[1:]), (1.8, 1.6, 1.3, 1.0)):
            k.limb(hd, a, b, w, "bone", "horn")
        k.limb(hd, (sx * 5.4, 31.4, 2.4), (sx * 5.4, 27.0, 2.6), 0.3, "leather", "cord")
        k.box(hd, C(sx * 5.4, 26.0, 2.6, 0.9, 1.2, 0.9), "gold", tag="bell")
    # ---------------------------------------------------------------- arms: thin, wrapped, long-nailed
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 7.0
        up = k.part("arm_" + nm, (x, 28.4, 0), (("x", -60 if side > 0 else -40), ("z", side * 12)), "torso")
        fo = k.part("fore_" + nm, (x, 21, 0), (("x", -60 if side > 0 else -40),), up)
        hn = k.part("hand_" + nm, (x, 13.4, 0), (), fo)
        k.box(up, C(x, 21.0, 0, 4.0, 7.6, 4.2), "fur", tag="sleeve")
        k.box(fo, C(x, 13.6, 0, 2.4, 7.4, 2.6), "skin", tag="forearm")
        for y in (15, 17, 19):
            k.ring(fo, x, y, 0, 1.5, 0.4, "leather", "wrap", n=6, axis="y")
        k.box(hn, C(x, 11.2, 0.3, 2.4, 2.6, 2.4), "skin", tag="hand")
        for t in (-0.8, 0, 0.8):
            k.shard(hn, (x + t, 11.2, 0.8), (0, -1, 0.4), 2.6, 0.5, mat="dark", tag="nail")
        if side > 0:         # bone dice in her left hand, glowing
            k.box(hn, C(x, 11.6, 2.0, 1.0, 1.0, 1.0), "glow", group="glow", tag="dice")
    # the crook, with the green fire caged at its top
    cr = k.part("crook", (-7, 12.2, 0.6), (("x", 80),), k.parts["hand_r"])
    k.limb(cr, (-7, -8, 0.6), (-7, 30, 0.6), 1.2, "wood", "haft")
    for (a, b) in (((-7, 30, 0.6), (-7, 33, 2.6)), ((-7, 33, 2.6), (-7, 32, 5.6)), ((-7, 32, 5.6), (-7, 29, 6.2))):
        k.limb(cr, a, b, 1.1, "wood", "crook")
    k.box(cr, C(-7, 23, 6.2, 3.8, 5.6, 3.8), "glow", group="glow", tag="fire")
    for (dx, dz) in ((-1.9, -1.9), (1.9, -1.9), (-1.9, 1.9), (1.9, 1.9)):
        k.box(cr, C(-7 + dx, 22.6, 6.2 + dz, 0.6, 6.6, 0.6), "iron", tag="cage")
    k.box(cr, C(-7, 28.8, 6.2, 4.6, 0.8, 4.6), "iron", tag="cage")
    k.box(cr, C(-7, 22.4, 6.2, 4.6, 0.8, 4.6), "iron", tag="cage")
    k.limb(cr, (-7, 29, 6.2), (-7, 29.6, 6.2), 0.6, "iron", "hanger")
    for (y, z) in ((26, 0.6), (20, 0.6), (14, 0.6)):
        k.limb(cr, (-7, y, z), (-8.4, y - 3, z), 0.3, "leather", "cord")
        k.box(cr, C(-8.4, y - 4, z, 0.8, 1.2, 0.8), "bone", tag="charm")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Knife Dancer (skirmisher)

def knife_dancer():
    """They dance at the fire before a job and at the job itself. Lean as a whip, wrapped in red sashes, sleeves
    bound tight, knives in sheaths up both arms and across the chest, a long red scarf flying behind - and a white
    mask with a painted grin. Two long curved knives in the hands, held back along the forearms."""
    k = X.Kit("knife_dancer")
    hips = k.part("hips", (0, 19, 0))
    k.box(hips, C(0, 16.6, 0, 7.6, 3.6, 5.0), "leather", tag="breeches")
    k.box(hips, C(0, 19.4, 0, 8.4, 2.2, 5.6), "red", tag="sash")
    k.limb(hips, (3.4, 19, 2.6), (5.0, 8.0, 3.6), 1.6, "red", "sash_tail", d=0.4)
    k.limb(hips, (3.8, 19, 1.4), (6.6, 10.0, 1.0), 1.4, "red", "sash_tail", d=0.4)
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.2
        th = k.part("thigh_" + nm, (x, 19, 0), (("x", -20 if side > 0 else 10), ("z", side * 6)), "hips")
        sh = k.part("shin_" + nm, (x, 10.2, 0), (("x", 30 if side > 0 else 10),), th)
        ft = k.part("foot_" + nm, (x, 2.2, 0), (("x", -10),), sh)
        k.box(th, C(x, 10.4, 0, 3.2, 8.8, 3.4), "leather", tag="thigh")
        k.box(sh, C(x, 2.2, 0, 3.0, 8.2, 3.2), "cloth", tag="wrap")
        for y in (4, 6.4, 8.8):
            k.box(sh, C(x, y, 0, 3.4, 0.6, 3.6), "red", tag="binding")
        k.box(ft, C(x, 0, 1.2, 3.2, 2.0, 5.6), "leather", tag="foot")
        k.box(th, C(x + side * 1.8, 11.4, 0.6, 0.8, 5.0, 1.2), "leather", tag="sheath")
        k.box(th, C(x + side * 1.8, 16.4, 0.6, 0.6, 1.6, 0.6), "steel", tag="knife_hilt")
    # ---------------------------------------------------------------- torso: lean, crossed with knife belts
    to = k.part("torso", (0, 19, 0), (("x", 12), ("y", -14)), "hips")
    k.stack(to, 0, 0, [(19, 7.6, 5.0), (24, 8.6, 5.4), (29, 10.4, 5.6)], "cloth", "vest")
    k.box(to, C(0, 19.6, 0, 8.2, 2.6, 5.6), "red", tag="sash")
    for sx in (-1, 1):
        k.limb(to, (sx * 4.6, 29.4, 2.9), (-sx * 3.2, 20.6, 2.9), 1.2, "leather", "knife_belt", d=0.4)
    for (x, y) in ((-2.6, 27.4), (-0.6, 25.6), (1.4, 23.8), (2.6, 27.4), (0.6, 25.6)):
        k.box(to, C(x, y, 3.2, 0.8, 2.4, 0.4), "leather", tag="sheath")
        k.box(to, C(x, y + 2.4, 3.2, 0.5, 1.2, 0.5), "steel", tag="knife_hilt")
    # the long scarf, flying back from the neck
    pts = [(0, 29, -2.6), (-2, 28, -7), (-1, 25, -11), (-4, 26, -15), (-3, 23, -19)]
    for (a, b), w in zip(zip(pts, pts[1:]), (3.0, 2.8, 2.4, 2.0)):
        k.limb(to, a, b, w, "red", "scarf", d=0.5)
    k.box(to, C(0, 28.6, 0, 7.0, 1.8, 6.0), "red", tag="scarf")
    # ---------------------------------------------------------------- the head: hooded, the grinning white mask
    hd = k.part("head", (0, 30, 0.4), (("x", -8), ("y", 10)), "torso")
    k.box(hd, C(0, 30.2, 0.2, 5.0, 5.6, 5.2), "red", tag="hood")
    k.box(hd, C(0, 35.6, -1.0, 3.6, 1.6, 4.0), "red", tag="hood")
    k.box(hd, C(0, 30.6, 2.8, 4.2, 4.8, 0.8), "bone", tag="mask")
    for sx in (-1.0, 1.0):
        k.box(hd, C(sx, 33.0, 3.25, 1.2, 0.6, 0.3), "dark", tag="mask_eye")
        k.box(hd, C(sx, 33.1, 3.35, 0.6, 0.4, 0.2), "eye", group="glow", tag="eye")
    k.box(hd, C(0, 31.2, 3.25, 3.2, 0.6, 0.3), "red", tag="grin")
    for sx in (-1.6, 1.6):
        k.box(hd, C(sx, 31.6, 3.25, 0.6, 0.8, 0.3), "red", tag="grin")
    for t in (-1.0, -0.3, 0.4, 1.1):
        k.box(hd, C(t, 31.4, 3.3, 0.3, 0.4, 0.2), "dark", tag="grin_tooth")
    # ---------------------------------------------------------------- arms: bound sleeves, the knives back along the forearm
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 6.0
        up = k.part("arm_" + nm, (x, 28, 0), (("x", -90 if side > 0 else -20), ("z", side * 30)), "torso")
        fo = k.part("fore_" + nm, (x, 20.8, 0), (("x", -40 if side > 0 else -100),), up)
        hn = k.part("hand_" + nm, (x, 13.6, 0), (), fo)
        k.box(up, C(x, 21.0, 0, 2.8, 7.4, 3.0), "cloth", tag="sleeve")
        k.box(fo, C(x, 13.8, 0, 2.6, 7.0, 2.8), "cloth", tag="sleeve")
        for y in (15, 17, 19):
            k.box(fo, C(x, y, 0, 3.0, 0.6, 3.2), "red", tag="binding")
        for dz in (-1.8, 1.8):
            k.box(up, C(x, 22, dz, 0.8, 4.2, 0.8), "leather", tag="sheath")
        k.box(hn, C(x, 11.2, 0.3, 2.4, 2.6, 2.4), "leather", tag="hand")
        kn = k.part("knife_" + nm, (x, 11.0, 0.4), (), hn)     # held reversed, the blade back along the forearm
        k.box(kn, C(x, 11.2, 1.8, 1.0, 1.0, 1.4), "gold", tag="guard")
        for i, (dy, dz) in enumerate(((0, 0), (2.6, -0.4), (5.2, -0.2), (7.4, 0.6))):
            k.box(kn, C(x + side * 1.6, 11.4 + dy, 1.4 + dz, 0.5, 2.8, 1.5 - i * 0.25), "steel", tag="blade")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Footpad (swarm)

def footpad():
    """The band's knives in the dark: a lean cutthroat in a hood and a scarf over the face, a cloak cut into strips
    so it doesn't snag, a bandolier of throwing knives, two curved short blades. Small, quick, and never alone."""
    k = X.Kit("footpad")
    hips = k.part("hips", (0, 18, 0))
    k.box(hips, C(0, 15.4, 0, 7.4, 3.6, 4.8), "leather", tag="breeches")
    k.box(hips, C(0, 18.0, 0, 8.0, 1.4, 5.2), "leather", tag="belt")
    k.box(hips, C(-3.6, 14.0, 1.6, 2.0, 2.6, 1.6), "leather", tag="pouch")
    k.box(hips, C(-3.6, 13.2, 1.6, 1.6, 1.2, 1.2), "gold", tag="coin")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.2
        th = k.part("thigh_" + nm, (x, 18, 0), (("x", -14), ("z", side * 6)), "hips")
        sh = k.part("shin_" + nm, (x, 9.6, 0), (("x", 24),), th)
        ft = k.part("foot_" + nm, (x, 2, 0), (("x", -10),), sh)
        k.box(th, C(x, 9.8, 0, 3.2, 8.4, 3.4), "cloth", tag="thigh")
        k.box(sh, C(x, 2.0, 0, 3.2, 7.8, 3.4), "leather", tag="boot")
        k.box(sh, C(x, 8.0, 0, 3.8, 1.4, 4.0), "leather", tag="boot_cuff")
        k.box(ft, C(x, 0, 1.2, 3.4, 2.0, 5.6), "leather", tag="foot")
    # the cloak in strips
    for i, x in enumerate((-3.6, -1.2, 1.2, 3.6)):
        k.box(hips, C(x, 6 + (i % 2) * 2, -3.4, 2.2, 24 - (i % 2) * 2, 0.6), "cloth", tag="cloak")
    # ---------------------------------------------------------------- torso
    to = k.part("torso", (0, 18, 0), (("x", 16),), "hips")
    k.stack(to, 0, 0, [(18, 7.4, 4.8), (23, 8.4, 5.2), (28, 9.4, 5.4)], "leather", "jerkin")
    k.limb(to, (3.8, 28, 2.8), (-3.6, 18.6, 2.8), 1.2, "leather", "bandolier", d=0.4)
    for t in (0.2, 0.4, 0.6, 0.8):
        k.box(to, C(3.8 - 7.4 * t, 28 - 9.4 * t + 0.6, 3.2, 0.6, 2.6, 0.4), "steel", tag="throwing_knife")
    k.box(to, C(0, 28.6, -0.4, 9.6, 1.6, 6.2), "cloth", tag="mantle")
    # ---------------------------------------------------------------- the head: deep hood, a scarf over the face, two eyes
    hd = k.part("head", (0, 29, 0.4), (("x", -12),), "torso")
    k.box(hd, C(0, 29.2, 0.2, 5.6, 5.8, 5.6), "cloth", tag="hood")
    k.shard(hd, (0, 34.8, -1.0), (0, 0.4, -1), 3.6, 3.0, mat="cloth", tag="hood_point")
    k.box(hd, C(0, 29.4, 2.7, 4.4, 4.0, 0.6), "dark", tag="hood_mouth")
    k.box(hd, C(0, 29.2, 2.95, 4.4, 2.2, 0.5), "red", tag="scarf")
    for sx in (-1.0, 1.0):
        k.box(hd, C(sx, 31.8, 3.0, 1.0, 0.6, 0.3), "eye", group="glow", tag="eye")
    # ---------------------------------------------------------------- arms and the two curved blades
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 5.6
        up = k.part("arm_" + nm, (x, 27, 0), (("x", -50), ("z", side * 16)), "torso")
        fo = k.part("fore_" + nm, (x, 20, 0), (("x", -50),), up)
        hn = k.part("hand_" + nm, (x, 13, 0), (), fo)
        k.box(up, C(x, 20.2, 0, 2.8, 7.0, 3.0), "cloth", tag="sleeve")
        k.box(fo, C(x, 13.2, 0, 2.8, 7.0, 3.0), "leather", tag="bracer")
        k.box(hn, C(x, 10.6, 0.3, 2.4, 2.6, 2.4), "leather", tag="hand")
        bl = k.part("blade_" + nm, (x, 11.8, 0.4), (("x", 80),), hn)
        k.box(bl, C(x, 9.8, 0.4, 0.9, 2.6, 0.9), "leather", tag="grip")
        k.box(bl, C(x, 12.2, 0.4, 0.8, 0.5, 2.2), "iron", tag="guard")
        for i, (dy, dz) in enumerate(((0, 0), (2.6, 0.6), (5.0, 1.6))):
            k.box(bl, C(x, 12.6 + dy, 0.4 + dz, 0.5, 2.8, 1.4 - i * 0.3), "steel", tag="blade")
    k.s.shaders = shaders()
    return k.s, k.parts


MOBS = {
    "footpad": dict(make=footpad, ent=(0.8, 2.6), stats=dict(hp=18, speed=0.3, dmg=4, armor=1, kb=0)),
    "gorge_ogre": dict(make=gorge_ogre, ent=(1.6, 3.8), stats=dict(hp=75, speed=0.18, dmg=12, armor=3, kb=0.8)),
    "hedge_hexer": dict(make=hedge_hexer, ent=(0.9, 2.6), stats=dict(hp=26, speed=0.21, dmg=5, armor=1, kb=0)),
    "knife_dancer": dict(make=knife_dancer, ent=(0.8, 2.7), stats=dict(hp=24, speed=0.33, dmg=6, armor=1, kb=0)),
    "bandit_lieutenant": dict(make=bandit_lieutenant, ent=(1.1, 3.1), stats=dict(hp=140, speed=0.23, dmg=10, armor=8, kb=0.6), key=True),
    "red_jack": dict(make=red_jack, texel=1, ent=(2.0, 5.8), stats=dict(hp=420, speed=0.24, dmg=15, armor=10, kb=0.9), boss=True),
}
