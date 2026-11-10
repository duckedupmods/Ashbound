"""Act V's boss, the last of the main story, fought through the Crown Gate under the Lord's Keep: the Founder-King.

    founder_king   boss   the first smith, who lit the Five Fires and made himself the first king, then went into the
                          oldest crack to take what was behind it, and was shut in by his own Fires. A colossus in burnt
                          gold and black iron with molten cracks across it; anvils for pauldrons; a bearded iron mask with
                          its eyes burning; a crown of five flames, each a Fire's colour (kiln orange, sea blue, ash grey,
                          moth violet, star white); a cloak of chains; a great smith's hammer for a sceptre

    python tools/monsterforge.py crown_gate --preview ; python tools/connect_check.py crown_gate
"""
import math

import vox2 as X
from vox2 import ramp
from serpent_ziggurat import grow
from _folk import lit, legs, arms, held
from tidewrack import Cc

GOLD = ramp("#2a1a06", "#46300c", "#6a4a14", "#8e641e", "#b4842c", "#d8aa48")
IRON = ramp("#060606", "#0e0d0c", "#181614", "#24211e", "#322e2a", "#423c36")
CHAIN = ramp("#141414", "#22221f", "#32322e", "#46463f", "#5c5c52")
KILN = ramp("#5a1004", "#8e2006", "#c43c0c", "#ee6a18", "#ffa040", "#ffe0a0")
SEA = ramp("#06304a", "#0c5878", "#1a84a8", "#3cb4dc", "#8ee0f8", "#e2faff")
ASHF = ramp("#3a3430", "#5a524a", "#80766a", "#a89c8c", "#d0c4b2", "#f0e8da")
VIOLET = ramp("#2c0a40", "#4a1466", "#6c2490", "#9040b8", "#b46ad8", "#e0b0f8")
STARF = ramp("#3a5aa0", "#6a8ad0", "#9ab8f0", "#c8dcff", "#ecf4ff", "#ffffff")
TAR = ramp("#010101", "#040303", "#080606", "#0c0a08")


def shaders():
    return {
        "gold": X.surf(GOLD, 0.55, 1.4, 0.18, 0.24, rust=(IRON, 0.3, 0.6)),
        "iron": X.surf(IRON, 0.5, 1.4, 0.22, 0.2, drip=(KILN, 0.1)),
        "chain": X.surf(CHAIN, 0.5, 1.3, 0.2, 0.2, stripe=2),
        "kiln": X.glow(KILN),
        "sea": X.glow(SEA),
        "ashf": X.glow(ASHF),
        "violet": X.glow(VIOLET),
        "starf": X.glow(STARF),
        "eye": X.glow(KILN, 0.86, 0.12),
        "dark": X.dark(TAR),
    }


GLOWS = {"kiln", "sea", "ashf", "violet", "starf", "eye"}


def crack(k, part, a, b):
    k.limb(part, a, b, 0.5, "kiln", "molten_crack")


def flame(k, part, base, mat, h, lean=0.0):
    """a tongue of fire standing up off the crown"""
    x, y, z = base
    k.blob(part, (x, y + h * 0.3, z), (1.3, h * 0.35, 1.3), mat, "flame", step=0.5)
    k.shard(part, (x, y + h * 0.55, z), (lean, 1, 0), h * 0.6, 1.2, mat=mat, tag="flame_tip")


def founder_king():
    k = X.Kit("founder_king")
    hips = k.part("hips", (0, 22, 0))
    k.stack(hips, 0, 0, [(14, 13.0, 9.4), (22, 13.6, 9.8)], "iron", "faulds")
    for i, x in enumerate((-5.0, -1.7, 1.7, 5.0)):
        k.box(hips, Cc(x, 15.0, 5.2, 3.0, 7.0, 0.9), "gold", tag="tasset")
    crack(k, hips, (-3.0, 20.0, 5.0), (1.0, 16.0, 5.0))
    legs(k, hips, 21, 11, 4.0, "iron", "iron", knee_mat="gold", lean=-4, bend=6, w=6.0)
    for side, nm in ((1, "l"), (-1, "r")):
        k.box(k.parts["shin_" + nm], Cc(side * 4.0, 6.0, 3.2, 5.0, 8.0, 0.8), "gold", tag="greave")
        crack(k, k.parts["thigh_" + nm], (side * 4.0, 18.0, 3.0), (side * 4.6, 13.0, 3.2))
    to = k.part("torso", (0, 22, 0), (("x", 6),), "hips")
    k.stack(to, 0, 0, [(22, 13.6, 9.8), (29, 16.0, 10.6), (35, 19.4, 11.4), (40, 17.4, 10.4)], "iron", "cuirass")
    k.box(to, Cc(0, 31.0, 5.8, 10.0, 12.0, 0.8), "gold", tag="breastplate")
    k.box(to, Cc(0, 31.0, 6.3, 1.4, 11.0, 0.4), "iron", tag="ridge")
    for (a, b) in (((-3.6, 35.0, 6.3), (-1.0, 30.0, 6.3)), ((-1.0, 30.0, 6.3), (-2.4, 26.0, 6.3)), ((2.4, 34.0, 6.3), (3.6, 28.0, 6.3))):
        crack(k, to, a, b)
    k.box(to, Cc(0, 31.0, 6.4, 2.2, 2.2, 0.4), "kiln", tag="heart")
    # the anvils for pauldrons, horn outwards, gold-banded
    for sx in (-1, 1):
        k.box(to, Cc(sx * 11.0, 39.0, 0, 8.0, 3.6, 11.0), "iron", tag="anvil_face")
        k.box(to, Cc(sx * 10.6, 36.4, 0, 5.0, 2.0, 7.0), "iron", tag="anvil_waist")
        k.shard(to, (sx * 15.0, 39.4, 0), (sx, 0.05, 0), 5.0, 2.6, mat="iron", tag="anvil_horn")
        k.box(to, Cc(sx * 11.0, 40.9, 0, 8.4, 0.6, 11.4), "gold", tag="anvil_band")
    # the cloak of chains, heavy, from the shoulders to the ground
    for i in range(9):
        x = -8.0 + i * 2.0
        for j in range(19):
            k.box(to, Cc(x, 38.0 - j * 1.6, -5.4 - abs(i - 4) * 0.08 - j * 0.04, 1.4, 2.0 if j % 2 else 1.6, 1.4), "chain", tag="chain_cloak")
    hd = k.part("head", (0, 40, 0.6), (("x", -4),), "torso")
    k.limb(hd, (0, 39.0, 0.4), (0, 42.0, 0.6), 6.0, "iron", "gorget")
    k.box(hd, Cc(0, 46.0, 0.6, 8.0, 8.4, 8.0), "iron", tag="helm")
    k.box(hd, Cc(0, 45.6, 4.75, 6.4, 6.0, 0.4), "gold", tag="mask")
    for sx in (-1, 1):
        k.box(hd, Cc(sx * 1.6, 47.0, 5.0, 1.8, 0.8, 0.3), "dark", tag="eye_slit")
        k.box(hd, Cc(sx * 1.6, 47.0, 5.05, 1.2, 0.5, 0.3), "eye", tag="eye")
    for i in range(7):                                # the iron beard, braided
        x = -2.4 + i * 0.8
        k.limb(hd, (x, 43.0, 4.8), (x * 0.7, 37.0 - (i % 2) * 1.6, 6.0), 0.8, "iron", "beard")
    k.box(hd, Cc(0, 50.6, 0.6, 8.6, 1.6, 8.6), "gold", tag="crown_band")
    for i, (mat, h) in enumerate((("kiln", 7.0), ("sea", 6.0), ("ashf", 5.4), ("violet", 6.0), ("starf", 7.6))):
        a = math.radians(-60 + i * 30)
        flame(k, hd, (math.sin(a) * 3.6, 51.2, math.cos(a) * 3.6 + 0.6), mat, h, lean=math.sin(a) * 0.3)
    arms(k, to, 12.0, 38, "iron", {1: ((("x", -20), ("z", 20)), (("x", -40),)), -1: ((("x", -70), ("z", -8)), (("x", -30),))}, glove="gold", w=5.4)
    for side in ("l", "r"):
        xx = 12.0 if side == "l" else -12.0
        crack(k, k.parts["arm_" + side], (xx, 35.0, 2.2), (xx, 31.0, 2.4))
    hm = held(k, "hammer", "r", (-12.0, 16.2, 0.3), (("x", 72),))
    k.limb(hm, (-12.0, 0.0, 0.3), (-12.0, 44.0, 0.3), 1.8, "gold", "haft")
    for y in (6.0, 14.0, 30.0):
        k.box(hm, Cc(-12.0, y, 0.3, 2.8, 1.4, 2.8), "iron", tag="haft_band")
    k.box(hm, Cc(-12.0, 47.0, 0.3, 7.0, 7.0, 14.0), "iron", tag="hammer_head")
    k.box(hm, Cc(-12.0, 47.0, 0.3, 7.6, 1.4, 14.6), "gold", tag="hammer_band")
    for sz in (-1, 1):
        k.box(hm, Cc(-12.0, 47.0, 0.3 + sz * 7.4, 5.0, 5.0, 0.8), "kiln", tag="hammer_face")
    k.box(hm, Cc(-12.0, 51.4, 0.3, 3.0, 2.0, 3.0), "kiln", tag="hammer_coal")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.12)
    return k.s, k.parts


MOBS = {
    "founder_king": dict(make=founder_king, ent=(3.0, 11.0), boss=True, stats=dict(hp=2400, speed=0.24, dmg=34, armor=22, kb=1.0)),
}
