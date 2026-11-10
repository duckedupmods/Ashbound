"""Shared strokes for the Legends (tools/beasts/<name>.py): a biped skeleton every one is built on (each then grows its
own body, head, hands and weapon on it), and the animation helpers their clips are keyed with.

Bones: hips (root) - chest - head; chest - al_up - al_low - al_hand; chest - ar_up - ar_low - ar_hand;
       hips - ll_up - ll_low - ll_foot, lr_up - lr_low - lr_foot.   Faces +z, its left is +x, 1 px = 1/16 block.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "mobs"))
sys.path.insert(0, "E:/Ashbound/tools")

import vox2 as X  # noqa: E402,F401
from vox2 import C, ramp  # noqa: E402,F401
import world_beasts as W  # noqa: E402,F401
from serpent_ziggurat import grow  # noqa: E402,F401

BIPED = ["hips", "chest", "head", "al_up", "al_low", "al_hand", "ar_up", "ar_low", "ar_hand"] + \
        ["l%s_%s" % (s, b) for s in "lr" for b in ("up", "low", "foot")]


def legs(k, hips, hip_x, hip_y, knee, ankle, w1, w2, mat, foot, plate=None):
    """two legs: thigh from (+-hip_x, hip_y, 0) to knee (x, y, z), shin to ankle; foot(part, side, ankle) draws the foot
    (one box of it tagged "foot", flat on y 0); plate(part, side, knee) dresses the shin"""
    out = {}
    for sx, s in ((1, "l"), (-1, "r")):
        hp = (sx * hip_x, hip_y, 0)
        kn = (sx * knee[0], knee[1], knee[2])
        an = (sx * ankle[0], ankle[1], ankle[2])
        up = k.part("l%s_up" % s, hp, (), hips)
        k.limb(up, hp, kn, w1, mat, "thigh")
        low = k.part("l%s_low" % s, kn, (), up)
        k.limb(low, kn, an, w2, mat, "shin")
        if plate:
            plate(low, sx, kn)
        ft = k.part("l%s_foot" % s, an, (), low)
        foot(ft, sx, an)
        out[s] = (up, low, ft)
    return out


def arms(k, chest, shoulder, elbow, wrist, w1, w2, mat, hand, hunch=0, upper=None, fore=None):
    """two arms hanging from the shoulders (+-x); hunch: the chest's pitch, undone at the shoulder so they hang straight.
    hand(part, side, wrist) draws each hand; upper/fore(part, side) dress them"""
    out = {}
    for sx, s in ((1, "l"), (-1, "r")):
        sh = (sx * shoulder[0], shoulder[1], shoulder[2])
        el = (sx * elbow[0], elbow[1], elbow[2])
        wr = (sx * wrist[0], wrist[1], wrist[2])
        up = k.part("a%s_up" % s, sh, (("x", -hunch),) if hunch else (), chest)
        k.limb(up, sh, el, w1, mat, "arm")
        if upper:
            upper(up, sx)
        low = k.part("a%s_low" % s, el, (), up)
        k.limb(low, el, wr, w2, mat, "forearm")
        if fore:
            fore(low, sx)
        hd = k.part("a%s_hand" % s, wr, (), low)
        hand(hd, sx, wr)
        out[s] = (up, low, hd)
    return out


def sym(sx, p):
    return (sx * p[0], p[1], p[2])


# ================================================================ animation helpers (keyed for GROW 1.5, hips in blocks)
# x turns a bone pointing forward downward (a hanging arm or leg: its end swings back, so - raises it forward);
# y turns it left; z rolls it (a hanging limb: its end out to its left, +x).

Z = [0, 0, 0, 0]


def wave(length, amp, phase=0.0, base=(0, 0, 0), axis=0, step=2, cycles=1):
    out = []
    for t in range(0, length, step):
        v = list(base)
        v[axis] += amp * math.sin(2 * math.pi * (cycles * t / length + phase))
        out.append([t] + [round(c, 3) for c in v])
    return out


def clip(length, bones, hips=None, **kw):
    return dict({"len": length, "bones": bones, "hips": hips or []}, **kw)


def stride(length, amp, lift, step=2):
    """the legs' cycle: each thigh swings (- forward), the knee folds as it comes through, the foot kept flat"""
    out = {}
    for s, ph in (("l", 0.0), ("r", 0.5)):
        ku, kl, kf = [], [], []
        for t in range(0, length, step):
            c = 2 * math.pi * (t / length + ph)
            swing = -amp * math.sin(c)
            fold = lift * max(0.0, math.cos(c))
            up = swing - fold * 0.35
            ku.append([t, round(up, 2), 0, 0])
            kl.append([t, round(fold, 2), 0, 0])
            kf.append([t, round(-up - fold, 2), 0, 0])
        out["l%s_up" % s], out["l%s_low" % s], out["l%s_foot" % s] = ku, kl, kf
    return out


def walk(length=48, amp=20, lift=56, stride_=3.0, heavy=1.0, arms_=(8.0, 6.0), extra=None):
    b = stride(length, amp, lift)
    b.update({
        "chest": wave(length, 3.0 * heavy, 0.0, axis=2),
        "head": wave(length, 2.0, 0.25, axis=0, cycles=2),
        "al_up": wave(length, arms_[0], 0.5, axis=0), "ar_up": wave(length, arms_[1], 0.0, axis=0),
    })
    if extra:
        b.update(extra(length))
    return {"len": length, "loop": True, "stride": stride_, "bones": b,
            "hips": wave(length, 0.07 * heavy, 0.25, base=(0, -0.04, 0), axis=1, cycles=2)}


def idle(length=80, extra=None):
    b = {"chest": wave(length, 2.0, 0.0, axis=0, step=4), "head": wave(length, 3.0, 0.3, axis=1, step=4),
         "al_up": wave(length, 1.5, 0.1, axis=0, step=4), "ar_up": wave(length, 1.5, 0.6, axis=0, step=4)}
    if extra:
        b.update(extra(length))
    return {"len": length, "loop": True, "bones": b, "hips": wave(length, 0.03, 0.0, axis=1, step=4)}


def death_kneel(length=64, fall=40, extra=None):
    """down on its knees, then over on its face"""
    b = {"ll_up": [Z, [20, -70, 0, 0], [length, -70, 0, 0]], "ll_low": [Z, [20, 110, 0, 0], [length, 110, 0, 0]],
         "ll_foot": [Z, [20, -40, 0, 0], [length, -40, 0, 0]],
         "lr_up": [Z, [20, -70, 0, 0], [length, -70, 0, 0]], "lr_low": [Z, [20, 110, 0, 0], [length, 110, 0, 0]],
         "lr_foot": [Z, [20, -40, 0, 0], [length, -40, 0, 0]],
         "chest": [Z, [20, -12, 0, 0], [36, -16, 0, 0], [56, fall, 0, 0], [length, fall + 4, 0, 0]],
         "head": [Z, [20, -20, 0, 0], [36, -26, 0, 0], [length, 10, 0, 0]],
         "al_up": [Z, [20, -6, 0, 20], [56, -60, 0, 30], [length, -60, 0, 30]],
         "ar_up": [Z, [20, -10, 0, -20], [56, -60, 0, -30], [length, -60, 0, -30]]}
    if extra:
        b.update(extra)
    return clip(length, b, hips=[Z, [20, 0, -1.1, 0], [36, 0, -1.1, 0], [56, 0, -1.5, 0.6], [length, 0, -1.6, 0.7]])


def hurt(extra=None):
    b = {"chest": [Z, [3, -8, 0, 3], [10, 0, 0, 0]], "head": [Z, [3, -10, 0, 0], [10, 0, 0, 0]]}
    if extra:
        b.update(extra)
    return clip(10, b)


# ================================================================ attack templates (keyed for the right arm; mirror() for the left)

def mirror(c):
    """the same move on the other side: al <-> ar, ll <-> lr, turns and rolls the other way"""
    import copy
    c = copy.deepcopy(c)
    swap = {"al": "ar", "ar": "al", "ll": "lr", "lr": "ll"}
    out = {}
    for b, ks in c["bones"].items():
        nb = swap[b[:2]] + b[2:] if b[:2] in swap else b
        out[nb] = [[t, x, -y, -z] for t, x, y, z in ks]
    c["bones"] = out
    c["hips"] = [[t, -x, y, z] for t, x, y, z in c.get("hips", [])]
    return c


def _sym(arm):
    return [[t, x, y, -z] for t, x, y, z in arm]


def overhead(length=42, hit=22, **kw):
    """the weapon up over its head and down in front of it, a step into it"""
    h = hit
    return clip(length, {
        "chest": [Z, [h - 8, -14, 8, 0], [h - 2, 16, -4, 0], [h + 2, 22, -6, 0], [h + 10, 20, -4, 0], [length, 0, 0, 0]],
        "head": [Z, [h - 8, 10, 0, 0], [h + 2, -12, 0, 0], [length, 0, 0, 0]],
        "ar_up": [Z, [h - 8, -172, 0, -10], [h - 3, -90, 0, -4], [h, -18, 0, 4], [h + 10, -16, 0, 4], [length, 0, 0, 0]],
        "ar_low": [Z, [h - 8, -24, 0, 0], [h - 3, -10, 0, 0], [h, -4, 0, 0], [length, 0, 0, 0]],
        "ar_hand": [Z, [h - 8, 30, 0, 0], [h - 3, -14, 0, 0], [h, 8, 0, 0], [h + 10, 8, 0, 0], [length, 0, 0, 0]],
        "al_up": [Z, [h - 8, 12, 0, 6], [h + 2, -16, 0, 4], [length, 0, 0, 0]],
        "ll_up": [Z, [h - 8, 4, 0, 0], [h - 2, -26, 0, 0], [h + 2, -30, 0, 0], [h + 12, -24, 0, 0], [length, 0, 0, 0]],
        "ll_low": [Z, [h - 2, 24, 0, 0], [h + 2, 28, 0, 0], [length, 0, 0, 0]],
        "lr_up": [Z, [h - 8, 4, 0, 0], [h + 2, 22, 0, 0], [h + 12, 18, 0, 0], [length, 0, 0, 0]],
        "lr_low": [Z, [h + 2, 10, 0, 0], [length, 0, 0, 0]], "lr_foot": [Z, [h + 2, -28, 0, 0], [length, 0, 0, 0]]},
        hips=[Z, [h - 8, 0, 0.1, -0.2], [h - 2, 0, -0.2, 0.5], [h + 2, 0, -0.3, 0.75], [h + 12, 0, -0.25, 0.7], [length, 0, 0, 0]],
        events={"hit": [hit]}, **kw)


def sweep(length=38, hit=20, **kw):
    """the right arm swung flat across everything in front, right to left"""
    h = hit
    return clip(length, {
        "chest": [Z, [h - 8, 0, -40, 0], [h - 3, 4, -10, 0], [h + 1, 6, 36, 0], [h + 8, 4, 30, 0], [length, 0, 0, 0]],
        "head": [Z, [h - 8, 0, 24, 0], [h + 1, 0, -20, 0], [length, 0, 0, 0]],
        "ar_up": [Z, [h - 8, -70, 0, -58], [h - 3, -84, 0, -30], [h + 1, -80, 0, 26], [h + 8, -60, 0, 20], [length, 0, 0, 0]],
        "ar_low": [Z, [h - 8, -30, 0, 0], [h - 3, -6, 0, 0], [h + 1, -4, 0, 0], [length, 0, 0, 0]],
        "ar_hand": [Z, [h - 8, 50, 0, 0], [h - 3, 46, 0, 0], [h + 1, 44, 0, 0], [h + 8, 30, 0, 0], [length, 0, 0, 0]],
        "al_up": [Z, [h - 8, 10, 0, 10], [h + 1, -8, 0, 4], [length, 0, 0, 0]],
        "ll_up": [Z, [h - 8, 10, 0, 0], [h + 1, -16, 0, 0], [length, 0, 0, 0]], "ll_low": [Z, [h + 1, 14, 0, 0], [length, 0, 0, 0]],
        "lr_up": [Z, [h - 8, -14, 0, 0], [h + 1, 14, 0, 0], [length, 0, 0, 0]], "lr_low": [Z, [h - 8, 16, 0, 0], [length, 0, 0, 0]]},
        hips=[Z, [h - 8, 0, -0.1, -0.1], [h + 1, 0, -0.15, 0.35], [length, 0, 0, 0]],
        events={"hit": [hit]}, **kw)


def slam2(length=50, hit=28, event="slam", **kw):
    """both arms up over its head and down on the ground in front"""
    h = hit
    arm = [Z, [h - 12, -165, 0, 10], [h - 6, -170, 0, 8], [h - 1, -60, 0, 2], [h + 1, -34, 0, 0], [h + 12, -30, 0, 0], [length, 0, 0, 0]]
    return clip(length, {
        "chest": [Z, [h - 12, -22, 0, 0], [h - 6, -24, 0, 0], [h, 30, 0, 0], [h + 12, 26, 0, 0], [length, 0, 0, 0]],
        "head": [Z, [h - 12, -16, 0, 0], [h, -26, 0, 0], [h + 12, -20, 0, 0], [length, 0, 0, 0]],
        "al_up": arm, "ar_up": _sym(arm),
        "al_low": [Z, [h - 12, -20, 0, 0], [h, -10, 0, 0], [length, 0, 0, 0]], "ar_low": [Z, [h - 12, -20, 0, 0], [h, -10, 0, 0], [length, 0, 0, 0]],
        "ll_up": [Z, [h - 12, 6, 0, 0], [h, -24, 0, 0], [h + 12, -20, 0, 0], [length, 0, 0, 0]], "ll_low": [Z, [h, 30, 0, 0], [length, 0, 0, 0]],
        "lr_up": [Z, [h, 18, 0, 0], [length, 0, 0, 0]], "lr_low": [Z, [h, 16, 0, 0], [length, 0, 0, 0]]},
        hips=[Z, [h - 12, 0, 0.15, -0.2], [h, 0, -0.35, 0.5], [h + 12, 0, -0.3, 0.45], [length, 0, 0, 0]],
        events={event: [hit]}, **kw)


def roar(length=46, at=18, **kw):
    """head and chest thrown back, arms flung wide: the shout goes off at tick at"""
    a = at
    return clip(length, {
        "chest": [Z, [a - 8, 10, 0, 0], [a, -20, 0, 0], [a + 16, -18, 0, 0], [length, 0, 0, 0]],
        "head": [Z, [a - 8, 14, 0, 0], [a, -28, 0, 0], [a + 8, -24, 6, 0], [a + 14, -24, -6, 0], [length, 0, 0, 0]],
        "al_up": [Z, [a - 8, 10, 0, 10], [a, -40, 0, 62], [a + 16, -36, 0, 58], [length, 0, 0, 0]],
        "ar_up": [Z, [a - 8, 10, 0, -10], [a, -40, 0, -62], [a + 16, -36, 0, -58], [length, 0, 0, 0]],
        "al_low": [Z, [a, -30, 0, 0], [length, 0, 0, 0]], "ar_low": [Z, [a, -30, 0, 0], [length, 0, 0, 0]],
        "ll_up": [Z, [a, -10, 0, 6], [length, 0, 0, 0]], "lr_up": [Z, [a, 12, 0, -6], [length, 0, 0, 0]],
        "ll_low": [Z, [a, 12, 0, 0], [length, 0, 0, 0]], "lr_low": [Z, [a, 12, 0, 0], [length, 0, 0, 0]]},
        hips=[Z, [a - 8, 0, -0.1, -0.1], [a, 0, 0, 0.1], [a + 16, 0, 0, 0.1], [length, 0, 0, 0]],
        events={"roar": [at]}, **kw)


def throw(length=44, at=26, **kw):
    """the right arm back over its shoulder, a turn of the body, and the throw"""
    a = at
    return clip(length, {
        "chest": [Z, [a - 10, -10, -38, 0], [a - 4, -12, -40, 0], [a, 14, 24, 0], [a + 8, 10, 20, 0], [length, 0, 0, 0]],
        "head": [Z, [a - 10, -6, 30, 0], [a, -4, -14, 0], [length, 0, 0, 0]],
        "ar_up": [Z, [a - 10, -150, 0, -30], [a - 4, -160, 0, -36], [a, -70, 0, -6], [a + 3, -30, 0, 4], [a + 10, -24, 0, 0], [length, 0, 0, 0]],
        "ar_low": [Z, [a - 10, -70, 0, 0], [a - 4, -80, 0, 0], [a, -10, 0, 0], [length, 0, 0, 0]],
        "al_up": [Z, [a - 10, -60, 0, 20], [a, 20, 0, 10], [length, 0, 0, 0]],
        "ll_up": [Z, [a - 10, -14, 0, 0], [a, -30, 0, 0], [a + 10, -24, 0, 0], [length, 0, 0, 0]], "ll_low": [Z, [a, 24, 0, 0], [length, 0, 0, 0]],
        "lr_up": [Z, [a - 10, 14, 0, 0], [a, 20, 0, 0], [length, 0, 0, 0]], "lr_low": [Z, [a - 10, 18, 0, 0], [a, 10, 0, 0], [length, 0, 0, 0]]},
        hips=[Z, [a - 10, 0, -0.1, -0.3], [a, 0, -0.15, 0.4], [a + 10, 0, -0.1, 0.35], [length, 0, 0, 0]],
        events={"throw": [at]}, **kw)


def breath(length=64, start=20, end=52, **kw):
    """drawn up, then leaning in, the head sweeping slowly across while it pours out of its face"""
    s_, e = start, end
    mid = (s_ + e) // 2
    return clip(length, {
        "chest": [Z, [s_ - 6, -14, 0, 0], [s_, 10, 0, 0], [e, 10, 0, 0], [length, 0, 0, 0]],
        "head": [Z, [s_ - 6, -24, 0, 0], [s_, -6, -26, 0], [mid, -6, 26, 0], [e, -6, -8, 0], [e + 6, 0, 0, 0], [length, 0, 0, 0]],
        "al_up": [Z, [s_, -24, 0, 30], [e, -24, 0, 30], [length, 0, 0, 0]], "ar_up": [Z, [s_, -24, 0, -30], [e, -24, 0, -30], [length, 0, 0, 0]],
        "ll_up": [Z, [s_, -14, 0, 0], [e, -14, 0, 0], [length, 0, 0, 0]], "ll_low": [Z, [s_, 18, 0, 0], [e, 18, 0, 0], [length, 0, 0, 0]],
        "lr_up": [Z, [s_, 12, 0, 0], [e, 12, 0, 0], [length, 0, 0, 0]]},
        hips=[Z, [s_ - 6, 0, 0.06, -0.1], [s_, 0, -0.12, 0.15], [e, 0, -0.12, 0.15], [length, 0, 0, 0]],
        events={"breath": [start]}, spray=[start, end], **kw)


def plunge(length=48, at=22, event="spikes", **kw):
    """the right hand (or what it holds) driven down into the ground in front, down on one knee"""
    a = at
    return clip(length, {
        "chest": [Z, [a - 6, -18, 0, 0], [a, 26, 0, 0], [a + 12, 24, 0, 0], [length, 0, 0, 0]],
        "head": [Z, [a - 6, -10, 0, 0], [a, -24, 0, 0], [a + 12, -22, 0, 0], [length, 0, 0, 0]],
        "ar_up": [Z, [a - 6, -165, 0, 6], [a, -50, 0, 10], [a + 12, -48, 0, 10], [length, 0, 0, 0]],
        "ar_low": [Z, [a - 6, -30, 0, 0], [a, -8, 0, 0], [length, 0, 0, 0]],
        "ar_hand": [Z, [a - 6, 110, 0, 0], [a, 76, 0, 0], [a + 12, 76, 0, 0], [length, 0, 0, 0]],
        "al_up": [Z, [a - 6, 10, 0, 8], [a, -10, 0, 4], [length, 0, 0, 0]],
        "ll_up": [Z, [a - 6, 4, 0, 0], [a, -40, 0, 0], [a + 12, -40, 0, 0], [length, 0, 0, 0]],
        "ll_low": [Z, [a, 58, 0, 0], [a + 12, 58, 0, 0], [length, 0, 0, 0]], "ll_foot": [Z, [a, -18, 0, 0], [a + 12, -18, 0, 0], [length, 0, 0, 0]],
        "lr_up": [Z, [a, 30, 0, 0], [a + 12, 30, 0, 0], [length, 0, 0, 0]], "lr_low": [Z, [a, 60, 0, 0], [a + 12, 60, 0, 0], [length, 0, 0, 0]],
        "lr_foot": [Z, [a, -20, 0, 0], [a + 12, -20, 0, 0], [length, 0, 0, 0]]},
        hips=[Z, [a - 6, 0, 0.1, -0.1], [a, 0, -0.5, 0.3], [a + 12, 0, -0.5, 0.3], [length, 0, 0, 0]],
        events={event: [at]}, **kw)


def lunge(length=40, leap_at=13, hit=24, **kw):
    """down in a crouch, a spring at you, both arms out to land on you"""
    lp, h = leap_at, hit
    arm = [Z, [lp - 2, 20, 0, 10], [lp + 3, -120, 0, 20], [h, -70, 0, 6], [h + 6, -40, 0, 0], [length, 0, 0, 0]]
    return clip(length, {
        "chest": [Z, [lp - 2, 18, 0, 0], [lp + 3, -10, 0, 0], [h, 24, 0, 0], [length, 0, 0, 0]],
        "head": [Z, [lp - 2, -14, 0, 0], [h, -18, 0, 0], [length, 0, 0, 0]],
        "al_up": arm, "ar_up": _sym(arm),
        "ll_up": [Z, [lp - 2, -40, 0, 0], [lp + 3, 30, 0, 0], [h, -30, 0, 0], [length, 0, 0, 0]],
        "ll_low": [Z, [lp - 2, 70, 0, 0], [lp + 3, 10, 0, 0], [h, 40, 0, 0], [length, 0, 0, 0]],
        "lr_up": [Z, [lp - 2, -40, 0, 0], [lp + 3, 40, 0, 0], [h, 10, 0, 0], [length, 0, 0, 0]],
        "lr_low": [Z, [lp - 2, 70, 0, 0], [lp + 3, 20, 0, 0], [h, 30, 0, 0], [length, 0, 0, 0]],
        "ll_foot": [Z, [lp - 2, -30, 0, 0], [lp + 3, 30, 0, 0], [h, -10, 0, 0], [length, 0, 0, 0]],
        "lr_foot": [Z, [lp - 2, -30, 0, 0], [lp + 3, 30, 0, 0], [h, -20, 0, 0], [length, 0, 0, 0]]},
        hips=[Z, [lp - 2, 0, -0.6, -0.2], [lp + 3, 0, 0, 0.2], [h, 0, -0.4, 0.5], [length, 0, 0, 0]],
        events={"leap": [leap_at], "hit": [hit]}, **kw)


def flurry(length=40, hits=(10, 16, 22, 28), arms_=("ar", "al"), **kw):
    """swipe after swipe, one arm then the other"""
    b = {"chest": [Z], "head": [Z, [hits[0], -10, 0, 0]]}
    for i, h in enumerate(hits):
        a = arms_[i % len(arms_)]
        sx = -1 if a.startswith("ar") else 1
        ks = b.setdefault(a + "_up", [Z])
        ks += [[h - 4, -110, 0, sx * 40], [h, -60, 0, -sx * 20], [h + 3, -20, 0, 0]]
        b["chest"] += [[h - 3, 0, sx * 18, 0], [h, 6, -sx * 18, 0]]
    for ks in b.values():
        ks.append([length, 0, 0, 0])
    b.update({"ll_up": [Z, [hits[0], -18, 0, 0], [hits[-1], -18, 0, 0], [length, 0, 0, 0]],
              "ll_low": [Z, [hits[0], 20, 0, 0], [hits[-1], 20, 0, 0], [length, 0, 0, 0]],
              "lr_up": [Z, [hits[0], 14, 0, 0], [hits[-1], 14, 0, 0], [length, 0, 0, 0]]})
    return clip(length, b, hips=[Z, [hits[0], 0, -0.1, 0.3], [hits[-1], 0, -0.1, 0.4], [length, 0, 0, 0]],
                events={"hit": list(hits)}, **kw)


def stomp(length=44, at=24, event="slam", **kw):
    """the left foot raised high, and brought down with all its weight"""
    a = at
    return clip(length, {
        "chest": [Z, [a - 8, -16, 0, 6], [a, 14, 0, 0], [a + 10, 10, 0, 0], [length, 0, 0, 0]],
        "head": [Z, [a - 8, -12, 0, 0], [a, -20, 0, 0], [length, 0, 0, 0]],
        "ll_up": [Z, [a - 8, -80, 0, 6], [a - 2, -70, 0, 4], [a, -16, 0, 0], [a + 10, -14, 0, 0], [length, 0, 0, 0]],
        "ll_low": [Z, [a - 8, 80, 0, 0], [a - 2, 60, 0, 0], [a, 10, 0, 0], [length, 0, 0, 0]],
        "ll_foot": [Z, [a - 8, 0, 0, 0], [a, 6, 0, 0], [length, 0, 0, 0]],
        "lr_up": [Z, [a - 8, 6, 0, 0], [a, 14, 0, 0], [length, 0, 0, 0]], "lr_low": [Z, [a - 8, 10, 0, 0], [a, 20, 0, 0], [length, 0, 0, 0]],
        "al_up": [Z, [a - 8, -30, 0, 40], [a, 10, 0, 20], [length, 0, 0, 0]], "ar_up": [Z, [a - 8, -30, 0, -40], [a, 10, 0, -20], [length, 0, 0, 0]]},
        hips=[Z, [a - 8, 0, 0.1, -0.1], [a, 0, -0.25, 0.3], [a + 10, 0, -0.2, 0.25], [length, 0, 0, 0]],
        events={event: [at]}, **kw)


def grab(length=46, hit=16, fling_at=30, **kw):
    """both arms shot out to seize, lifted high, and flung"""
    h, f = hit, fling_at
    arm = [Z, [h - 6, -40, 0, 30], [h, -100, 0, 6], [f - 4, -175, 0, 4], [f, -60, 0, 10], [f + 6, -40, 0, 10], [length, 0, 0, 0]]
    return clip(length, {
        "chest": [Z, [h - 6, 10, 0, 0], [h, 20, 0, 0], [f - 4, -24, 0, 0], [f, 24, 0, 0], [length, 0, 0, 0]],
        "head": [Z, [h, -16, 0, 0], [f - 4, -30, 0, 0], [f, -10, 0, 0], [length, 0, 0, 0]],
        "al_up": arm, "ar_up": _sym(arm),
        "ll_up": [Z, [h, -24, 0, 0], [length, 0, 0, 0]], "ll_low": [Z, [h, 22, 0, 0], [length, 0, 0, 0]], "lr_up": [Z, [h, 16, 0, 0], [length, 0, 0, 0]]},
        hips=[Z, [h, 0, -0.15, 0.45], [f - 4, 0, 0.05, 0.3], [f, 0, -0.2, 0.5], [length, 0, 0, 0]],
        events={"hit": [fling_at], "grab": [hit]}, **kw)


def spin(length=62, hits=(22, 29, 36, 43), **kw):
    """arms flung out and the whole body spinning, two turns"""
    return clip(length, {
        "hips": [Z, [10, 0, 40, 0], [18, 0, -60, 0], [25, 0, -240, 0], [32, 0, -420, 0], [39, 0, -600, 0], [46, 0, -780, 0],
                 [56, 0, -720, 0], [length, 0, -720, 0]],
        "al_up": [Z, [12, -20, 0, 50], [18, -10, 0, 84], [46, -10, 0, 84], [54, 0, 0, 30], [length, 0, 0, 0]],
        "ar_up": [Z, [12, -20, 0, -50], [18, -10, 0, -84], [46, -10, 0, -84], [54, 0, 0, -30], [length, 0, 0, 0]],
        "chest": [Z, [12, -6, 30, 0], [18, -6, 0, 0], [46, -6, 0, 0], [length, 0, 0, 0]]},
        hips=[Z, [18, 0, 0.05, 0], [46, 0, 0.05, 0], [length, 0, 0, 0]],
        events={"hit": list(hits)}, arc=360, **kw)


def grown(clips, k):
    """clips keyed on a 1.5 body, for one grown k times bigger: its moves, strides and reach with it (a leap's lift stays)"""
    if k == 1:
        return clips
    for c in clips.values():
        c["hips"] = [[t, x * k, y * k, z * k] for t, x, y, z in c.get("hips", [])]
        for key in ("stride", "reach", "radius", "front", "throw"):
            if key in c:
                c[key] = round(c[key] * k, 2)
        if "range" in c:
            c["range"] = [round(v * k, 2) for v in c["range"]]
        if "leap" in c:
            c["leap"] = [round(c["leap"][0] * k, 2), c["leap"][1]]
    return clips


def with_events(c, **ev):
    c["events"] = dict(ev)
    return c


def fitted(name, clips):
    """hips fitted so the planted feet stay on the floor (tools/beastkit.py <name> fitall writes <name>_fit.json)"""
    import json
    p = os.path.join(HERE, name + "_fit.json")
    if os.path.exists(p):
        for n, h in json.load(open(p, encoding="utf-8")).items():
            if n in clips:
                clips[n]["hips"] = h
    return clips
