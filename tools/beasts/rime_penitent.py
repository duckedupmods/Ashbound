"""The Rime Penitent: the snow lands' Legend. A hunched knight grown out of glacier ice, a tall penitent's hood of rime,
a man frozen inside its chest pressing at the ice, a cracked bronze bell dragged on a chain in its left hand and a
broken greatsword sheathed in ice dragging from its right. When the bell tolls the ground freezes.

Bones (biped, tools/beastkit.py):
    hips (root) - robe_f, robe_b
                - chest - head
                        - al_up - al_low - al_hand - chain - bell
                        - ar_up - ar_low - ar_hand (the sword)
                - ll_up - ll_low - ll_foot,  lr_up - lr_low - lr_foot

1 px = 1/16 block before GROW; it faces +z, its left is +x.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "mobs"))
sys.path.insert(0, "E:/Ashbound/tools")

import vox2 as X  # noqa: E402
from vox2 import C, ramp  # noqa: E402
import world_beasts as W  # noqa: E402
from serpent_ziggurat import grow  # noqa: E402

GROW = 1.5
HITBOX = (3.2, 6.0)
BRONZE = ramp("#140e06", "#26190a", "#3c2a10", "#584018", "#765822", "#94722e")
VERDIGRIS = ramp("#12302a", "#1e4a3e", "#2e6a56", "#468a70", "#62a88a")
GLACIER = ramp("#1c3a5a", "#2e5a80", "#4e80a6", "#7aa8c8", "#a8cce2", "#d8ecf6", "#f4fbff")
DEEP = ramp("#050c1a", "#0a1830", "#10264a", "#183864", "#224c80")
CORPSE = ramp("#1e2832", "#2e3a48", "#44525e", "#5e6c78", "#7c8a94", "#9eaab2")


def frost_cap(k, part, at, w, d, mat="snow"):
    """snow lying on a top surface"""
    k.box(part, C(at[0], at[1], at[2], w, 1.4, d), mat, tag="snow")


def rime_penitent(name="rime_penitent", legend=False):
    k = X.Kit(name)
    # ---- hips, the frozen robe hanging stiff
    hips = k.part("hips", (0, 26, 0))
    k.blob(hips, (0, 27, 0), (11, 5, 7.5), "deep", "pelvis", step=1.0)
    k.ring(hips, 0, 28.5, 0, 11.2, 1.8, "iron", "belt_chain", n=14, axis="y")
    rf = k.part("robe_f", (0, 26, 6), (), hips)
    for i, x in enumerate((-4.5, -1.5, 1.5, 4.5)):
        low = 10 + 5 * X.h3(i, 2, 5)
        k.limb(rf, (x, 26.5, 6.4), (x * 1.1, low, 8.4 + (i % 2)), 3.2, "robe", "robe", d=1.2)
        k.shard(rf, (x * 1.1, low + 0.6, 8.4 + (i % 2)), (0, -1, 0.1), 3.0, 1.0, mat="ice", tag="icicle")
    rb = k.part("robe_b", (0, 26, -6), (), hips)
    for i, x in enumerate((-8, -5, -2, 1, 4, 7)):
        low = 4 + 4 * X.h3(i, 4, 1)
        k.limb(rb, (x, 26.5, -6.4), (x * 1.15, low, -10 - (i % 2)), 3.4, "robe", "robe", d=1.2)
        k.shard(rb, (x * 1.15, low + 0.6, -10 - (i % 2)), (0, -1, -0.1), 3.4, 1.0, mat="ice", tag="icicle")

    # ---- legs: glacier greaves, ice sabatons
    for sx, s in ((1, "l"), (-1, "r")):
        hip, knee, ankle = (sx * 7, 26, 0), (sx * 8, 14, 2), (sx * 8, 4.5, 0)
        up = k.part("l%s_up" % s, hip, (), hips)
        k.limb(up, hip, knee, 11, "deep", "thigh")
        k.blob(up, (sx * 8.0, 21, 1.0), (6.4, 6.0, 6.4), "ice", "thigh_plate", step=0.8)
        low = k.part("l%s_low" % s, knee, (), up)
        k.limb(low, knee, ankle, 10, "deep", "shin")
        k.limb(low, (sx * 8, 15, 4.8), (sx * 8, 6, 4.4), 9, "ice", "greave", d=3.4)
        k.limb(low, (sx * 11.6, 14, 1.6), (sx * 11.2, 6, 1.0), 2.4, "ice", "greave", d=7)
        k.shard(low, (sx * 8, 15, 5), (sx * 0.2, 0.9, 0.7), 6, 2.4, mat="ice", tag="knee_spike")
        ft = k.part("l%s_foot" % s, ankle, (), low)
        k.box(ft, C(sx * 8, 0, 2.6, 9.6, 4.6, 13), "ice", tag="foot")
        k.box(ft, C(sx * 8, 4.4, 1.2, 8.4, 2.2, 9), "deep", tag="ankle")
        for t in range(3):
            k.shard(ft, (sx * 8 + (t - 1) * 3, 1.4, 8.6), (0, -0.2, 1), 3.4, 1.6, mat="ice", tag="toe")

    # ---- the chest: hunched, a dark window in the ice with the frozen man inside
    ch = k.part("chest", (0, 30, 0), (("x", 22),), hips)
    k.stack(ch, 0, -0.5, [(30, 15, 12), (33, 17, 14), (37, 22, 16), (41, 28, 17.5), (45, 33, 18), (49, 32, 17), (52, 26, 14),
                         (54, 18, 10)], "ice", "torso", step=0.8)
    k.box(ch, C(0, 34, 0, 13, 14, 14), "deep", tag="core")
    k.blob(ch, (0, 47, -5), (11, 7, 7), "ice", "hump", step=1.0)
    for i, (x, y) in enumerate(((-9, 40), (9, 42), (-6, 49), (7, 50), (0, 52), (-11, 46), (11, 47))):   # glacier on the back
        k.shard(ch, (x, y, -8.4), (x * 0.06, 0.6, -1), 10 - i * 0.6, 3.4, mat="ice", tag="back_shard")
    k.box(ch, C(0, 35.5, 8.0, 15, 15, 1.8), "deep", tag="window")
    M = "corpse"
    k.box(ch, C(0, 42.6, 8.8, 4.6, 5.6, 1.0), M, tag="frozen_man")                     # his head, thrown back
    k.box(ch, C(0, 44.6, 9.5, 4.8, 1.0, 0.6), M, tag="frozen_man")                     # brow
    k.box(ch, C(0, 42.6, 9.6, 1.0, 1.8, 0.6), M, tag="frozen_man")                     # nose
    for sx in (-1, 1):
        k.box(ch, C(sx * 1.2, 43.8, 9.6, 1.2, 0.6, 0.4), "dark", tag="frozen_man")    # shut eyes
    k.box(ch, C(0, 41.0, 9.6, 2.0, 1.6, 0.4), "dark", tag="frozen_man")               # the scream
    k.box(ch, C(0, 36.0, 8.7, 7.0, 6.0, 0.9), M, tag="frozen_man")                     # chest
    for r in range(3):                                                                # ribs
        k.box(ch, C(0, 37.0 + r * 1.5, 9.3, 5.4 - r * 0.6, 0.5, 0.4), "corpse_dark", tag="frozen_man")
    for sx in (-1, 1):                                                                # arms up, palms on the ice
        k.limb(ch, (sx * 3.6, 40.8, 8.8), (sx * 5.4, 44.0, 8.9), 1.6, M, "frozen_man", d=0.9)
        k.limb(ch, (sx * 5.4, 44.0, 8.9), (sx * 4.6, 47.4, 9.2), 1.5, M, "frozen_man", d=0.9)
        k.box(ch, C(sx * 4.4, 47.0, 9.4, 2.6, 2.4, 0.6), M, tag="frozen_man")
        for f in range(4):
            k.box(ch, C(sx * 4.4 + (f - 1.5) * 0.75, 49.2, 9.4, 0.5, 1.4, 0.5), M, tag="frozen_man")
    for i, (a, b) in enumerate((((-6, 49), (-2, 45)), ((5, 36), (2, 40)), ((-5, 37), (-3, 41)))):   # cracks in the ice over him
        k.limb(ch, (a[0], a[1], 9.2), (b[0], b[1], 9.2), 0.5, "crack", "crack", d=0.4)
    k.box(ch, C(0, 50.4, 8.4, 17.4, 2.2, 2.4), "ice", tag="window_rim")
    k.box(ch, C(0, 33.6, 8.2, 17.4, 2.2, 2.4), "ice", tag="window_rim")
    for sx in (-1, 1):
        k.box(ch, C(sx * 8.4, 34, 8.4, 2.4, 17, 2.4), "ice", tag="window_rim")
        k.shard(ch, (sx * 8.4, 50, 8.8), (sx * 0.4, 1, 1.3), 4, 1.6, mat="ice", tag="rim_spike")
    k.chain(ch, (-13, 49, -8.4), (12, 33, -8.6), 9, "iron", w=1.8)                      # penitent's chains, over the back
    # shoulders: glacier pauldrons growing up and out, snow lying on them
    for sx in (-1, 1):
        k.blob(ch, (sx * 17, 47.5, 0), (7.4, 6.0, 8.2), "ice", "pauldron", step=0.8)
        k.blob(ch, (sx * 18.6, 44, 0.5), (5.0, 3.0, 7.0), "ice", "pauldron", step=0.8)
        k.cluster(ch, (sx * 18, 52, -0.5), 5, 13, 3.0, mat="ice", seed=2 + sx, spread=0.55, up=(sx * 0.6, 1, -0.2))
        frost_cap(k, ch, (sx * 16.6, 53, 0.5), 9, 10)

    # ---- the head: a tall penitent's hood of rime, two cold slits, a halo of icicles behind
    hd = k.part("head", (0, 50, 4), (("x", -14),), ch)
    k.blob(hd, (0, 50.5, 2), (13, 4.4, 10), "rime", "mantle", step=0.7)
    for i in range(9):                                                               # the mantle's frozen hem
        a = math.pi * (0.1 + 0.8 * i / 8)
        x, z = -math.cos(a) * 12.4, 2 - math.sin(a) * 9.2 + 9.2 * 0.0
        k.shard(hd, (x, 47.5, z if i not in (0, 8) else 2), (0, -1, 0), 3 + (i % 3), 1.8, mat="rime", tag="hem")
    prof = [(50, 11, 11), (53, 11.4, 11.6), (56, 10.6, 10.8), (59, 9.2, 9.4), (62, 7.6, 7.8), (65, 6.0, 6.2), (68, 4.6, 4.8),
            (71, 3.4, 3.6), (74, 2.4, 2.6), (76.5, 1.4, 1.6)]
    for (y0, w0, d0), (y1, w1, d1) in zip(prof, prof[1:]):          # each band set back a little more: the tip leans back
        k.stack(hd, 0, 5 - (y0 - 50) * 0.07, [(y0, w0, d0), (y1, w1, d1)], "rime", "hood", step=0.6)
    for sx in (-1, 1):                                                               # the hood's folds
        k.limb(hd, (sx * 4.6, 51, 9.6), (sx * 2.2, 66, 4.4), 1.0, "rime_dark", "fold", d=0.8)
    k.box(hd, C(0, 51.2, 10.3, 6.4, 6.0, 1.2), "dark", tag="face")
    for sx in (-1, 1):
        W.eye(k, hd, (sx * 1.6, 54.6, 10.95), 1.8, 0.6)
    for i in range(-3, 4):
        k.shard(hd, (i * 2.2, 54, 0.4), (i * 0.34, 1, -0.5), 13 - abs(i) * 2.0, 1.8, mat="ice", tag="halo")

    # ---- left arm: the bell on its chain
    al = k.part("al_up", (18, 45, 0), (("x", -22),), ch)          # hangs straight under the hunch
    k.limb(al, (18, 45, 0), (17, 34, 1), 8.4, "deep", "arm")
    k.chain(al, (11.5, 44, 3), (20, 40, -3), 4, "iron", w=1.6)
    k.blob(al, (19.4, 39, 0.8), (5.0, 5.6, 5.4), "ice", "arm_plate", step=0.8)
    alo = k.part("al_low", (17, 34, 1), (), al)
    k.limb(alo, (17, 34, 1), (17, 23, 3), 7.6, "deep", "forearm")
    k.limb(alo, (19.6, 33, 1.2), (19.4, 24.5, 3), 4, "ice", "vambrace", d=6)
    k.cluster(alo, (20.5, 30, 1.6), 3, 5, 1.8, mat="ice", seed=7, spread=0.4, up=(1, 0.5, -0.2))
    ah = k.part("al_hand", (17, 23, 3), (), alo)
    k.box(ah, C(17, 16.4, 3.6, 9.2, 7.4, 9.2), "ice", tag="gauntlet")
    k.cluster(ah, (17, 22, 3.6), 3, 3.4, 1.4, mat="ice", seed=4, spread=0.6, up=(0.4, 1, 0))
    ch_ = k.part("chain", (17, 18, 4), (), ah)
    k.chain(ch_, (17, 17.5, 4.5), (21, 12.5, 8), 4, "iron", w=1.9)
    bell = k.part("bell", (21, 12.5, 8), (), ch_)
    k.stack(bell, 21, 8, [(0, 15.4, 15.4), (0.8, 15.0, 15.0), (1.8, 13.4, 13.4), (3.2, 11.6, 11.6), (5.5, 10.4, 10.4), (8, 10.0, 10.0),
                          (10, 9.6, 9.6), (11.2, 8.6, 8.6), (12, 6.4, 6.4)], "bronze", "bell", step=0.5)
    k.ring(bell, 21, 1.0, 8, 7.6, 1.0, "bronze_hi", "bell_lip", n=16, axis="y")
    k.ring(bell, 21, 8.6, 8, 5.2, 0.8, "bronze_hi", "bell_band", n=14, axis="y")
    k.ring(bell, 21, 13.2, 8, 1.8, 1.2, "iron", "bell_loop", n=8, axis="x")
    k.limb(bell, (23.6, 10, 12.6), (25.8, 2, 15.0), 0.8, "dark", "crack", d=0.6)
    k.box(bell, C(21, 11.6, 8, 7.4, 1.4, 7.4), "snow", tag="snow")
    for t in range(5):                                                                # icicles off the lip
        a = t * 2 * math.pi / 5 + 0.4
        k.shard(bell, (21 + math.cos(a) * 7.0, 1.0, 8 + math.sin(a) * 7.0), (0, -1, 0), 1.0 + t % 2 * 0.6, 0.9, mat="ice", tag="icicle")

    # ---- right arm: the broken greatsword, its blade grown on in ice
    ar = k.part("ar_up", (-18, 45, 0), (("x", -22),), ch)
    k.limb(ar, (-18, 45, 0), (-17, 34, 3), 8.4, "deep", "arm")
    k.chain(ar, (-11.5, 44, 3), (-20, 40, -3), 4, "iron", w=1.6)
    k.blob(ar, (-19.4, 39, 0.8), (5.0, 5.6, 5.4), "ice", "arm_plate", step=0.8)
    aro = k.part("ar_low", (-17, 34, 3), (), ar)
    k.limb(aro, (-17, 34, 3), (-17, 23, 6), 7.6, "deep", "forearm")
    k.limb(aro, (-19.6, 33, 3.2), (-19.4, 24.5, 6), 4, "ice", "vambrace", d=6)
    k.cluster(aro, (-20.5, 30, 3.6), 3, 5, 1.8, mat="ice", seed=3, spread=0.4, up=(-1, 0.5, -0.2))
    arh = k.part("ar_hand", (-17, 23, 6), (), aro)
    k.box(arh, C(-17, 16.8, 6.6, 9.2, 7.4, 9.2), "ice", tag="gauntlet")
    k.cluster(arh, (-17, 22.4, 6.0), 3, 3.4, 1.4, mat="ice", seed=8, spread=0.6, up=(-0.4, 1, 0))
    k.limb(arh, (-17, 26.5, 6.6), (-17, 17, 7.4), 1.8, "wood", "grip")
    k.box(arh, C(-17, 26.4, 6.6, 2.6, 2.0, 2.6), "iron", tag="pommel")
    k.limb(arh, (-23, 16.2, 8.2), (-11, 16.2, 8.2), 2.0, "iron", "guard", d=2.0)
    k.limb(arh, (-17, 16, 8.4), (-17.4, 11.5, 14.4), 4.4, "iron", "blade", d=1.2)            # what's left of the steel
    k.limb(arh, (-17.4, 11.5, 14.4), (-18, 1.2, 29), 5.0, "ice", "ice_blade", d=1.8)         # the rest is ice
    for t in range(4):
        f = (t + 0.5) / 4
        p = (-17.4 - 0.6 * f, 11.5 - 10.3 * f, 14.4 + 14.6 * f)
        k.shard(arh, p, (-0.9, 0.3, 0.2), 3.2 - t * 0.4, 1.4, mat="ice", tag="blade_shard")
        k.shard(arh, p, (0.9, 0.3, 0.2), 2.6 - t * 0.3, 1.2, mat="ice", tag="blade_shard")

    W.glow_tags(k, "eye")
    grow(k, GROW * (1.25 if legend else 1.0))
    k.s.shaders = W.shaders(
        ice=X.facets(GLACIER), deep=X.facets(DEEP, 0.3), crack=X.dark(DEEP),
        rime_dark=X.surf(W.SNOWFUR, 0.42, 1.0, 0.12, 0.0),
        corpse_dark=X.surf(CORPSE, 0.3, 1.0, 0.1, 0.0),
        bronze_hi=X.surf(BRONZE, 0.68, 1.4, 0.14, 0.24, rust=(VERDIGRIS, 0.2, 0.6)),
        snow=X.surf(W.SNOWFUR, 0.82, 1.0, 0.1, 0.0, pattern=W.shag),
        rime=X.surf(W.SNOWFUR, 0.66, 1.1, 0.16, 0.06, pattern=W.strands),
        robe=X.surf(W.SNOWFUR, 0.36, 1.1, 0.2, 0.05, stripe=2, crust=(W.SNOWFUR, 0.4)),
        corpse=X.surf(CORPSE, 0.6, 1.0, 0.12, 0.0),
        bronze=X.surf(BRONZE, 0.5, 1.3, 0.16, 0.2, rust=(VERDIGRIS, 0.32, 0.5), crust=(W.SNOWFUR, 0.3)),
        eye=X.glow(W.ICE, 0.8, 0.16),
    )
    return k.s, k.parts


BONES = ["hips", "robe_f", "robe_b", "chest", "head", "al_up", "al_low", "al_hand", "chain", "bell",
         "ar_up", "ar_low", "ar_hand"] + ["l%s_%s" % (s, b) for s in "lr" for b in ("up", "low", "foot")]

make = rime_penitent
LEGEND = None


# ================================================================ its animations (tools/beastkit.py)
# x turns a bone pointing forward downward (an arm or leg hanging down: its end swings back, so - raises it forward);
# y turns it left; z rolls it (a hanging limb: its end out to the left, +x). Keyed for GROW 1.5, hips in blocks.

Z = [0, 0, 0, 0]


def _wave(length, amp, phase=0.0, base=(0, 0, 0), axis=0, step=2, cycles=1):
    out = []
    for t in range(0, length, step):
        v = list(base)
        v[axis] += amp * math.sin(2 * math.pi * (cycles * t / length + phase))
        out.append([t] + [round(c, 3) for c in v])
    return out


def _clip(length, bones, hips=None, **kw):
    return dict({"len": length, "bones": bones, "hips": hips or []}, **kw)


def _stride(length, amp, lift, step=2):
    """the legs' cycle: each thigh swings (- forward), the knee folds as it comes through, the foot kept flat"""
    out = {}
    for s, ph in (("l", 0.0), ("r", 0.5)):
        ku, kl, kf = [], [], []
        for t in range(0, length, step):
            c = 2 * math.pi * (t / length + ph)
            swing = -amp * math.sin(c)
            fold = lift * max(0.0, math.cos(c))          # folding while the leg comes forward
            up = swing - fold * 0.35
            ku.append([t, round(up, 2), 0, 0])
            kl.append([t, round(fold, 2), 0, 0])
            kf.append([t, round(-up - fold, 2), 0, 0])
        out["l%s_up" % s], out["l%s_low" % s], out["l%s_foot" % s] = ku, kl, kf
    return out


def _walk(length=48, amp=20, lift=56, stride=3.0, heavy=1.0):
    b = _stride(length, amp, lift)
    b.update({
        "chest": _wave(length, 3.0 * heavy, 0.0, axis=2),
        "head": _wave(length, 2.0, 0.25, axis=0, cycles=2),
        "al_up": _wave(length, 8.0, 0.5, axis=0), "ar_up": _wave(length, 5.0, 0.0, axis=0),
        "chain": _wave(length, 7.0, 0.6, axis=0), "bell": _wave(length, 4.0, 0.7, axis=2),
        "robe_f": _wave(length, 6.0, 0.2, base=(-4, 0, 0), axis=0, cycles=2),
        "robe_b": _wave(length, 6.0, 0.7, base=(6, 0, 0), axis=0, cycles=2),
    })
    return {"len": length, "loop": True, "stride": stride, "bones": b,
            "hips": _wave(length, 0.07 * heavy, 0.25, base=(0, -0.04, 0), axis=1, cycles=2)}


CLIPS = {
    "idle": {"len": 80, "loop": True, "bones": {
        "chest": _wave(80, 2.0, 0.0, axis=0, step=4), "head": _wave(80, 3.0, 0.3, axis=1, step=4),
        "al_up": _wave(80, 1.5, 0.1, axis=0, step=4), "ar_up": _wave(80, 1.5, 0.6, axis=0, step=4),
        "chain": _wave(80, 3.0, 0.2, axis=2, step=4), "robe_f": _wave(80, 3.0, 0.4, axis=0, step=4),
        "robe_b": _wave(80, 3.0, 0.9, axis=0, step=4)},
        "hips": _wave(80, 0.03, 0.0, axis=1, step=4)},
    "walk": _walk(),
    "run": _walk(30, 30, 66, 4.4, 1.6),
    # the sword up over its hood, and down in front of it
    "cleave": _clip(42, {
        "chest": [Z, [14, -14, 8, 0], [20, 16, -4, 0], [24, 22, -6, 0], [32, 20, -4, 0], [42, 0, 0, 0]],
        "head": [Z, [14, 10, 0, 0], [24, -12, 0, 0], [42, 0, 0, 0]],
        "ar_up": [Z, [14, -172, 0, -10], [19, -90, 0, -4], [22, -14, 0, 4], [32, -12, 0, 4], [42, 0, 0, 0]],
        "ar_low": [Z, [14, -24, 0, 0], [19, -10, 0, 0], [22, -4, 0, 0], [42, 0, 0, 0]],
        "ar_hand": [Z, [14, 30, 0, 0], [19, -14, 0, 0], [22, 12, 0, 0], [32, 12, 0, 0], [42, 0, 0, 0]],
        "al_up": [Z, [14, 12, 0, 6], [24, -16, 0, 4], [42, 0, 0, 0]],
        "chain": [Z, [14, -10, 0, 0], [24, 14, 0, 0], [42, 0, 0, 0]],
        "ll_up": [Z, [14, 4, 0, 0], [20, -26, 0, 0], [24, -30, 0, 0], [34, -24, 0, 0], [42, 0, 0, 0]],
        "ll_low": [Z, [20, 24, 0, 0], [24, 28, 0, 0], [42, 0, 0, 0]],
        "ll_foot": [Z, [20, 4, 0, 0], [42, 0, 0, 0]],
        "lr_up": [Z, [14, 4, 0, 0], [24, 22, 0, 0], [34, 18, 0, 0], [42, 0, 0, 0]],
        "lr_low": [Z, [24, 10, 0, 0], [42, 0, 0, 0]],
        "lr_foot": [Z, [24, -28, 0, 0], [42, 0, 0, 0]],
        "robe_f": [Z, [14, -10, 0, 0], [24, 16, 0, 0], [42, 0, 0, 0]], "robe_b": [Z, [14, 8, 0, 0], [24, 18, 0, 0], [42, 0, 0, 0]]},
        hips=[Z, [14, 0, 0.1, -0.2], [20, 0, -0.2, 0.5], [24, 0, -0.3, 0.75], [34, 0, -0.25, 0.7], [42, 0, 0, 0]],
        events={"hit": [22]}, reach=5.5, arc=50, dmg=1.3, range=[0, 6]),
    # the blade swung flat right to left across everything in front: it goes through a raised guard
    "sweep": _clip(38, {
        "chest": [Z, [12, 0, -40, 0], [17, 4, -10, 0], [21, 6, 36, 0], [28, 4, 30, 0], [38, 0, 0, 0]],
        "head": [Z, [12, 0, 24, 0], [21, 0, -20, 0], [38, 0, 0, 0]],
        "ar_up": [Z, [12, -70, 0, -58], [17, -84, 0, -30], [21, -80, 0, 26], [28, -60, 0, 20], [38, 0, 0, 0]],
        "ar_low": [Z, [12, -30, 0, 0], [17, -6, 0, 0], [21, -4, 0, 0], [38, 0, 0, 0]],
        "ar_hand": [Z, [12, 50, 0, 0], [17, 46, 0, 0], [21, 44, 0, 0], [28, 30, 0, 0], [38, 0, 0, 0]],
        "al_up": [Z, [12, 10, 0, 10], [21, -8, 0, 4], [38, 0, 0, 0]],
        "chain": [Z, [12, 10, 0, 8], [21, -16, 0, -6], [38, 0, 0, 0]],
        "ll_up": [Z, [12, 10, 0, 0], [21, -16, 0, 0], [38, 0, 0, 0]], "ll_low": [Z, [21, 14, 0, 0], [38, 0, 0, 0]],
        "lr_up": [Z, [12, -14, 0, 0], [21, 14, 0, 0], [38, 0, 0, 0]], "lr_low": [Z, [12, 16, 0, 0], [38, 0, 0, 0]],
        "robe_f": [Z, [21, 10, 0, -10], [38, 0, 0, 0]], "robe_b": [Z, [21, 10, 0, 10], [38, 0, 0, 0]]},
        hips=[Z, [12, 0, -0.1, -0.1], [21, 0, -0.15, 0.35], [38, 0, 0, 0]],
        events={"hit": [20], "guard": [20]}, reach=6.0, arc=170, dmg=1.0, range=[0, 6.5]),
    # the bell lifted high on its chain and brought down: the toll freezes the ground and throws you back
    "toll": _clip(52, {
        "chest": [Z, [18, -20, 10, 0], [24, -22, 10, 0], [28, 24, 4, 0], [34, 22, 0, 0], [52, 0, 0, 0]],
        "head": [Z, [18, -16, 0, 0], [28, -20, 0, 0], [40, -8, 0, 0], [52, 0, 0, 0]],
        "al_up": [Z, [18, -160, 0, 14], [24, -168, 0, 12], [27, -70, 0, 4], [29, -36, 0, 0], [38, -34, 0, 0], [52, 0, 0, 0]],
        "al_low": [Z, [18, -20, 0, 0], [28, -6, 0, 0], [52, 0, 0, 0]],
        "chain": [Z, [18, 150, 0, 0], [24, 170, 0, 0], [27, 40, 0, 0], [29, 0, 0, 0], [52, 0, 0, 0]],
        "bell": [Z, [18, 20, 0, 0], [24, 30, 0, 0], [29, -10, 0, 0], [33, 4, 0, 0], [52, 0, 0, 0]],
        "ar_up": [Z, [18, 14, 0, -12], [28, -10, 0, -6], [52, 0, 0, 0]],
        "ll_up": [Z, [18, 6, 0, 0], [28, -22, 0, 0], [40, -18, 0, 0], [52, 0, 0, 0]], "ll_low": [Z, [28, 24, 0, 0], [52, 0, 0, 0]],
        "lr_up": [Z, [28, 16, 0, 0], [52, 0, 0, 0]], "lr_low": [Z, [28, 12, 0, 0], [52, 0, 0, 0]],
        "robe_f": [Z, [18, -14, 0, 0], [28, 18, 0, 0], [52, 0, 0, 0]], "robe_b": [Z, [18, 10, 0, 0], [28, 20, 0, 0], [52, 0, 0, 0]]},
        hips=[Z, [18, 0, 0.15, -0.2], [28, 0, -0.3, 0.45], [40, 0, -0.25, 0.4], [52, 0, 0, 0]],
        events={"roar": [28]}, reach=9.0),
    # keep your distance and it drives the blade into the ground: ice spears burst up in a line to you
    "spikes": _clip(48, {
        "chest": [Z, [16, -18, 0, 0], [22, 26, 0, 0], [34, 24, 0, 0], [48, 0, 0, 0]],
        "head": [Z, [16, -10, 0, 0], [22, -24, 0, 0], [34, -22, 0, 0], [48, 0, 0, 0]],
        "ar_up": [Z, [16, -165, 0, 6], [22, -50, 0, 10], [34, -48, 0, 10], [48, 0, 0, 0]],
        "ar_low": [Z, [16, -30, 0, 0], [22, -8, 0, 0], [48, 0, 0, 0]],
        "ar_hand": [Z, [16, 110, 0, 0], [22, 76, 0, 0], [34, 76, 0, 0], [48, 0, 0, 0]],
        "al_up": [Z, [16, 10, 0, 8], [22, -10, 0, 4], [48, 0, 0, 0]],
        "ll_up": [Z, [16, 4, 0, 0], [22, -40, 0, 0], [34, -40, 0, 0], [48, 0, 0, 0]],
        "ll_low": [Z, [22, 58, 0, 0], [34, 58, 0, 0], [48, 0, 0, 0]], "ll_foot": [Z, [22, -18, 0, 0], [34, -18, 0, 0], [48, 0, 0, 0]],
        "lr_up": [Z, [22, 30, 0, 0], [34, 30, 0, 0], [48, 0, 0, 0]], "lr_low": [Z, [22, 60, 0, 0], [34, 60, 0, 0], [48, 0, 0, 0]],
        "lr_foot": [Z, [22, -20, 0, 0], [34, -20, 0, 0], [48, 0, 0, 0]],
        "robe_f": [Z, [22, 24, 0, 0], [34, 24, 0, 0], [48, 0, 0, 0]], "robe_b": [Z, [22, 20, 0, 0], [48, 0, 0, 0]]},
        hips=[Z, [16, 0, 0.1, -0.1], [22, 0, -0.7, 0.3], [34, 0, -0.7, 0.3], [48, 0, 0, 0]],
        events={"spikes": [22]}, range=[6, 18], dmg=1.0, cool=180),
    # under 60%: it throws the bell out on its chain and spins, the bell whirling round it
    "whirl": _clip(62, {
        "hips": [Z, [10, 0, 40, 0], [18, 0, -60, 0], [25, 0, -240, 0], [32, 0, -420, 0], [39, 0, -600, 0], [46, 0, -780, 0],
                 [56, 0, -720, 0], [62, 0, -720, 0]],
        "al_up": [Z, [12, -20, 0, 50], [18, -10, 0, 84], [46, -10, 0, 84], [54, 0, 0, 30], [62, 0, 0, 0]],
        "al_low": [Z, [18, -6, 0, 0], [46, -6, 0, 0], [62, 0, 0, 0]],
        "chain": [Z, [12, 0, 0, 30], [18, 0, 0, 6], [46, 0, 0, 6], [54, 0, 0, 40], [62, 0, 0, 0]],
        "bell": [Z, [18, 0, 0, 20], [46, 0, 0, 20], [62, 0, 0, 0]],
        "ar_up": [Z, [12, -20, 0, -40], [46, -20, 0, -40], [62, 0, 0, 0]],
        "chest": [Z, [12, -6, 30, 0], [18, -6, 0, 0], [46, -6, 0, 0], [62, 0, 0, 0]],
        "robe_f": [Z, [18, -20, 0, 0], [46, -20, 0, 0], [62, 0, 0, 0]], "robe_b": [Z, [18, 20, 0, 0], [46, 20, 0, 0], [62, 0, 0, 0]]},
        hips=[Z, [18, 0, 0.05, 0], [46, 0, 0.05, 0], [62, 0, 0, 0]],
        events={"hit": [22, 29, 36, 43]}, reach=7.0, arc=360, dmg=0.9, range=[0, 7], phase=2, cool=400, odds=0.5),
    "hurt": _clip(10, {
        "chest": [Z, [3, -8, 0, 3], [10, 0, 0, 0]], "head": [Z, [3, -10, 0, 0], [10, 0, 0, 0]],
        "chain": [Z, [3, 10, 0, 0], [10, 0, 0, 0]]}),
    # it goes down on its knees, the bell drops, and it falls on its face
    "death": _clip(64, {
        "ll_up": [Z, [20, -70, 0, 0], [64, -70, 0, 0]], "ll_low": [Z, [20, 110, 0, 0], [64, 110, 0, 0]],
        "ll_foot": [Z, [20, -40, 0, 0], [64, -40, 0, 0]],
        "lr_up": [Z, [20, -70, 0, 0], [64, -70, 0, 0]], "lr_low": [Z, [20, 110, 0, 0], [64, 110, 0, 0]],
        "lr_foot": [Z, [20, -40, 0, 0], [64, -40, 0, 0]],
        "chest": [Z, [20, -12, 0, 0], [36, -16, 0, 0], [56, 40, 0, 0], [64, 44, 0, 0]],
        "head": [Z, [20, -20, 0, 0], [36, -26, 0, 0], [64, 10, 0, 0]],
        "al_up": [Z, [20, -6, 0, 20], [56, -60, 0, 30], [64, -60, 0, 30]],
        "ar_up": [Z, [20, -10, 0, -20], [56, -60, 0, -30], [64, -60, 0, -30]],
        "chain": [Z, [20, 20, 0, 0], [64, 30, 0, 0]],
        "robe_f": [Z, [20, -40, 0, 0], [64, -40, 0, 0]], "robe_b": [Z, [20, 30, 0, 0], [64, 30, 0, 0]]},
        hips=[Z, [20, 0, -1.1, 0], [36, 0, -1.1, 0], [56, 0, -1.5, 0.6], [64, 0, -1.6, 0.7]]),
}

# hips fitted so the lowest planted foot stays on the floor (python tools/beastkit.py rime_penitent fit <clip>)
FIT = {
    "cleave": [[0, 0.0, 0.0, 0.0], [14, 0.0, 0.199, -0.2], [19, 0.0, -0.102, 0.448], [22, 0.0, -0.18, 0.656], [24, 0.0, -0.188, 0.75], [32, 0.0, -0.04, 0.705], [34, 0.0, 0.015, 0.7], [42, 0.0, 0.0, 0.0]],
    "sweep": [[0, 0.0, 0.0, 0.0], [12, 0.0, 0.159, -0.1], [17, 0.0, 0.143, 0.162], [21, 0.0, 0.171, 0.35], [28, 0.0, 0.138, 0.221], [38, 0.0, 0.0, 0.0]],
    "toll": [[0, 0.0, 0.0, 0.0], [18, 0.0, 0.169, -0.2], [24, 0.0, 0.169, 0.221], [28, 0.0, 0.167, 0.45], [34, 0.0, 0.169, 0.425], [40, 0.0, 0.137, 0.4], [52, 0.0, 0.0, 0.0]],
    "spikes": [[0, 0.0, 0.0, 0.0], [16, 0.0, -0.045, -0.1], [22, 0.0, -0.485, 0.3], [34, 0.0, -0.485, 0.3], [48, 0.0, 0.0, 0.0]],
}
for _n, _h in FIT.items():
    CLIPS[_n]["hips"] = _h

# its numbers before Balance (solved as a boss at C, moved to the rank it comes at), and its egg
IS_LEGEND = True
STATS = dict(hp=640, speed=0.24, dmg=24, armor=10, kb=1.0)
EGG, SPOTS = 0xcfe6f4, 0x1c3a5a
