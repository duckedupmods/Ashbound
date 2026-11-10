"""Act III's boss, fought in the Grey Fold (tools/blender/ash_arena.py): the Ash Shepherd.

    ash_shepherd   boss   the thing that walks ahead of every ashfall night, the Ashwalkers its flock: a tall gaunt
                          figure in a hooded cloak of ash that keeps crumbling and re-forming, ember cracks burning in its
                          hem; ram's horns curling out of the hood round a skull with ember eyes; a mantle of layered ash
                          and iron plates on its shoulders, an iron shepherd's bell on a chain at its chest; long bony
                          hands, and a huge iron crook whose hook is a scythe's blade, little bells hanging off it

    python tools/monsterforge.py grey_fold --preview ; python tools/mobsheet.py grey_fold
    python tools/connect_check.py grey_fold
"""
import math

import vox2 as X
from vox2 import ramp
from serpent_ziggurat import grow
from _folk import lit, legs, arms, held
from tidewrack import Cc

ASH = ramp("#1c1a19", "#2a2826", "#3a3735", "#4c4946", "#605c58", "#76726c")
CHAR = ramp("#060505", "#0c0a09", "#14110f", "#1c1815", "#26201c")
BONE = ramp("#3a342c", "#57503f", "#787058", "#9a9078", "#bcb298", "#dcd2b8")
HORN = ramp("#1a1610", "#2c261c", "#40382a", "#564c3a", "#6e624c")
IRON = ramp("#0a0a0b", "#141416", "#202024", "#2e2e34", "#3e3e46", "#525260")
BRONZE = ramp("#1e1206", "#34200c", "#4e3214", "#6a461e", "#8a5e2a")
EMBER = ramp("#4a0e02", "#7a1c04", "#b0360a", "#e05a14", "#ff8a30", "#ffd08a")
TAR = ramp("#020202", "#060505", "#0a0808", "#100c0a")


def shaders():
    return {
        "ash": X.surf(ASH, 0.5, 1.1, 0.3, 0.06, holes=True, crust=(CHAR, 0.22)),
        "cloak": X.surf(ASH, 0.48, 1.0, 0.32, 0.04, holes=True, drip=(EMBER, 0.12)),
        "char": X.surf(CHAR, 0.5, 1.0, 0.26, 0.04),
        "bone": X.surf(BONE, 0.55, 1.2, 0.16, 0.12, crust=(ASH, 0.24)),
        "horn": X.surf(HORN, 0.5, 1.2, 0.2, 0.14, stripe=2),
        "iron": X.surf(IRON, 0.5, 1.4, 0.2, 0.22, rust=(EMBER, 0.08, 0.6)),
        "bronze": X.surf(BRONZE, 0.55, 1.4, 0.16, 0.24, crust=(ASH, 0.2)),
        "ember": X.glow(EMBER),
        "eye": X.glow(EMBER, 0.86, 0.12),
        "dark": X.dark(TAR),
    }


GLOWS = {"ember", "eye"}


def ram_horn(k, part, root, side, s=1.0):
    """a ram's horn curling back and round from the hood, thick at the root, ridged"""
    x0, y0, z0 = root
    pts = []
    for i in range(9):
        t = i / 8
        a = t * math.pi * 1.4
        r = 4.2 * s * (1 - 0.35 * t)
        pts.append((x0 + side * (1.2 * s + 2.6 * s * t + r * 0.35 * (1 - math.cos(a))), y0 + r * math.sin(a) * 0.9, z0 - r * (1 - math.cos(a)) * 0.8))
    for (a, b), i in zip(zip(pts, pts[1:]), range(8)):
        k.limb(part, a, b, (2.4 - i * 0.2) * s, "horn", "horn")


def ash_shepherd():
    k = X.Kit("ash_shepherd")
    hips = k.part("hips", (0, 22, 0))
    # the robe, long, widening to a torn hem pooling on the ground; ember cracks in it
    k.stack(hips, 0, 0, [(1.0, 15.0, 12.0), (8.0, 13.0, 10.4), (16.0, 11.4, 9.0), (22.0, 10.6, 8.2)], "cloak", "robe", step=1.2)
    for i in range(10):
        a = i / 10 * 2 * math.pi
        x, z = math.sin(a) * 7.2, math.cos(a) * 5.8
        k.box(hips, Cc(x, 1.4, z, 3.0, 2.4 - (i % 3) * 0.5, 2.0), "ash", tag="hem_drift")
    for i, (x, y) in enumerate(((-3, 5), (2.4, 9), (-1, 13), (4, 4), (0.6, 17))):
        k.box(hips, Cc(x, y, 5.6 - y * 0.12, 1.0, 4.4, 0.4), "ember", tag="ember_crack")
    k.box(hips, Cc(0, 21.0, 0, 11.4, 2.0, 8.8), "iron", tag="belt")
    legs(k, hips, 21, 11, 3.0, "char", "char", lean=-2, bend=4, w=4.0, cuff=False)   # under the robe: seen when it strides
    to = k.part("torso", (0, 22, 0), (("x", 12),), "hips")
    k.stack(to, 0, 0, [(22, 10.6, 8.2), (28, 11.6, 8.4), (34, 14.0, 8.8), (38, 12.0, 8.0)], "cloak", "chest")
    # the mantle: layered ash and iron plates, wide and pointed (a V from the neck)
    for sx in (-1, 1):
        for lay in range(3):
            k.box(to, Cc(sx * (8.0 + lay * 1.4), 36.2 - lay * 1.8, 0, 6.0 - lay * 0.6, 1.6, 10.0 - lay * 0.8), "iron" if lay == 1 else "ash", tag="mantle")
        k.shard(to, (sx * 12.6, 36.6, 0), (sx * 1, 0.5, 0), 3.0, 1.4, mat="iron", tag="mantle_spike")
    # the bell on its chain at the chest, its mouth glowing
    for i in range(4):
        k.box(to, Cc(-2.4 + i * 1.6, 36.4 - abs(i - 1.5) * 1.0, 4.4, 1.2, 0.8, 0.8), "iron", tag="bell_chain")
    k.blob(to, (0, 30.0, 5.4), (2.6, 3.0, 2.2), "bronze", "bell", step=0.6)
    k.box(to, Cc(0, 27.4, 5.4, 4.2, 1.0, 3.4), "bronze", tag="bell_lip")
    k.box(to, Cc(0, 27.0, 5.4, 2.6, 0.4, 2.0), "ember", tag="bell_mouth")
    # the hood and the face in it
    hd = k.part("head", (0, 38, 0.6), (("x", -14),), "torso")
    k.limb(hd, (0, 37.0, 0.2), (0, 39.4, 0.8), 4.6, "char", "neck")
    k.blob(hd, (0, 42.4, -1.4), (5.4, 5.6, 5.4), "cloak", "hood", step=0.8)
    for sx in (-1, 1):                            # the cowl's sides framing the face, and its brow hanging over it
        k.box(hd, Cc(sx * 3.4, 41.8, 3.6, 1.6, 8.0, 4.2), "cloak", tag="cowl")
    k.box(hd, Cc(0, 46.0, 3.8, 8.4, 1.8, 4.4), "cloak", tag="cowl_brow")
    k.box(hd, Cc(0, 42.0, 3.4, 6.0, 7.0, 1.8), "dark", tag="hood_dark")
    k.box(hd, Cc(0, 42.6, 4.4, 4.0, 4.4, 1.6), "bone", tag="skull")
    k.box(hd, Cc(0, 40.2, 4.4, 3.2, 1.6, 1.4), "bone", tag="jaw")
    for sx in (-1, 1):
        k.box(hd, Cc(sx * 1.0, 43.2, 5.25, 1.2, 1.2, 0.3), "dark", tag="socket")
        k.box(hd, Cc(sx * 1.0, 43.2, 5.3, 0.7, 0.6, 0.3), "eye", tag="eye")
    for i in range(4):
        k.box(hd, Cc(-1.2 + i * 0.8, 40.6, 5.25, 0.4, 0.9, 0.3), "dark", tag="teeth_gap")
    k.box(hd, Cc(0, 47.6, -2.0, 2.4, 2.4, 3.0), "cloak", tag="hood_peak")
    for sx in (-1, 1):
        ram_horn(k, hd, (sx * 3.6, 44.4, 0.6), sx, 1.0)
    # long sleeves, bony hands
    arms(k, to, 9.6, 35, "cloak", {1: ((("x", -30), ("z", 20)), (("x", -40),)), -1: ((("x", -60), ("z", -10)), (("x", -30),))}, glove="char", w=4.4, long=1.25)
    for side in ("l", "r"):
        fo, hn = k.parts["fore_" + side], k.parts["hand_" + side]
        xx = 9.6 if side == "l" else -9.6
        k.box(fo, Cc(xx, 19.6, 0, 6.0, 3.0, 6.0), "cloak", tag="sleeve_cuff")
        for t in (-1.2, -0.4, 0.4, 1.2):
            k.limb(hn, (xx + t, 14.8, 1.0), (xx + t * 1.2, 10.4, 2.6), 0.7, "bone", "finger")
            k.shard(hn, (xx + t * 1.2, 10.4, 2.6), (0, -1, 0.3), 1.6, 0.5, mat="dark", tag="claw")
    # the crook: a long iron staff, the hook a scythe's blade on its inside edge, bells hanging off it
    ck = held(k, "crook", "r", (-9.6, 13.6, 0.3), (("x", 70),))
    k.limb(ck, (-9.6, 0.0, 0.3), (-9.6, 46.0, 0.3), 1.6, "iron", "staff")
    for y in (8.0, 20.0, 34.0):
        k.box(ck, Cc(-9.6, y, 0.3, 2.4, 1.4, 2.4), "bronze", tag="staff_band")
    hook = []
    for i in range(10):
        a = i / 9 * math.pi * 1.15
        hook.append((-9.6, 46.0 + math.sin(a) * 6.0, 0.3 + (1 - math.cos(a)) * 6.0))
    for (a, b), i in zip(zip(hook, hook[1:]), range(9)):
        k.limb(ck, a, b, 1.7 - i * 0.06, "iron", "hook")
    for i in range(1, 9):                         # the blade along the hook's inside
        a = i / 9 * math.pi * 1.15
        y, z = 46.0 + math.sin(a) * 4.6, 0.3 + (1 - math.cos(a)) * 6.0 - (0.2 if a < math.pi / 2 else -0.2)
        k.box(ck, Cc(-9.6, y - 0.8, z, 0.6, 2.8, 2.4), "bone", tag="blade_edge")
    for z in (2.6, 6.2, 9.6):                     # little bells off the hook
        y = 46.0 + math.sqrt(max(0.0, 36 - (z - 6.3) ** 2)) - 0.6
        k.limb(ck, (-9.6, y, z), (-9.6, y - 3.0, z), 0.4, "iron", "bell_string")
        k.blob(ck, (-9.6, y - 4.0, z), (1.0, 1.1, 1.0), "bronze", "little_bell", step=0.4)
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.1)
    return k.s, k.parts


MOBS = {
    "ash_shepherd": dict(make=ash_shepherd, ent=(2.4, 9.0), boss=True, stats=dict(hp=1300, speed=0.24, dmg=24, armor=12, kb=1.0)),
}
