"""Frostjaw on its own skeleton (not the spider's): the same beast as tools/mobs/world_beasts.py, rigged for its own
animations (tools/beastkit.py). Bones:

    body (root: chest and shoulders) - neck - head - jaw
                                     - abdomen (haunch) - tail0 - tail1 - tail2
    each leg: <leg>_up (hip/shoulder) - <leg>_low (knee) - <leg>_paw (ankle), legs fl fr bl br

1 px = 1/16 block before GROW; it faces +z.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "mobs"))
sys.path.insert(0, "E:/Ashbound/tools")

import vox2 as X  # noqa: E402
from vox2 import C  # noqa: E402
import world_beasts as W  # noqa: E402
from serpent_ziggurat import grow  # noqa: E402

GROW = 2.3          # 11/5: Frostmaw-sized (about 4.5 blocks tall); the clips are keyed for 1.5 and scaled below
LEGEND_SCALE = 1.35
LEGS = ("fl", "fr", "bl", "br")


def leg3(k, parent, nm, hip, knee, ankle, w1, w2, paw):
    """a leg in three bones: thigh from the hip, shin from the knee, the paw from the ankle"""
    up = k.part(nm + "_up", hip, (), parent)
    k.limb(up, hip, knee, w1, "fur", "leg")
    k.blob(up, ((hip[0] + knee[0]) / 2, (hip[1] + knee[1]) / 2 + 1, (hip[2] + knee[2]) / 2), (w1 * 0.62, 4.0, w1 * 0.7), "fur", "thigh", step=0.8)
    low = k.part(nm + "_low", knee, (), up)
    k.limb(low, knee, ankle, w2, "fur", "shin")
    pw = k.part(nm + "_paw", ankle, (), low)
    paw(pw, ankle)
    return up, low, pw


def frostjaw(name="frostjaw", legend=False):
    k = X.Kit(name)
    body = k.part("body", (0, 19, 3))
    k.blob(body, (0, 21.6, 5), (9.6, 9.6, 11.0), "fur", "chest", step=1.0)
    k.blob(body, (0, 26.4, 7), (8.4, 5.2, 7.0), "fur", "hump", step=1.0)
    k.blob(body, (0, 14.6, 5), (6.4, 2.8, 8.6), "fur_w", "belly", step=0.9)
    for sx in (-1, 1):
        k.blob(body, (sx * 7.4, 22, 9), (3.6, 6.4, 5.0), "fur", "shoulder_blade", step=0.8)
    for i, z in enumerate((10, 6, 2, -2)):          # ice plates down the spine
        k.shard(body, (0, 29 - abs(z - 4) * 0.2, z), (0, 1, -0.5), 6.0 - i * 0.6, 3.0, mat="ice", tag="ice_plate")
        k.shard(body, (0, 28.4, z - 1.4), (0, 1, -0.7), 3.0, 1.6, mat="ice", tag="ice_plate")
    # the neck carries the frost mane
    nk = k.part("neck", (0, 22, 12), (), body)
    k.blob(nk, (0, 21.8, 14.4), (5.6, 5.8, 4.2), "fur", "neck", step=0.8)
    k.blob(nk, (0, 25, 12.4), (8.0, 6.4, 4.6), "frost", "mane", step=0.8)
    for i in range(10):
        a = i * 2 * math.pi / 10
        k.shard(nk, (math.cos(a) * 7, 24 + math.sin(a) * 5.4, 12.4), (math.cos(a), math.sin(a) + 0.2, -0.6), 4.0, 1.4,
                mat="frost", tag="mane_spike")
    # the head, big and low, and the jaw on its own hinge
    hd = k.part("head", (0, 23, 15), (("x", 12),), nk)
    S, O = 1.3, (0, 23, 15)

    def P(x, y, z):
        return (O[0] + (x - O[0]) * S, O[1] + (y - O[1]) * S, O[2] + (z - O[2]) * S + 1.0)

    def B(x, y, z, w, h, d):
        p = P(x, y, z)
        return C(p[0], p[1], p[2], w * S, h * S, d * S)
    k.blob(hd, P(0, 24, 18.4), (5.4 * S, 4.6 * S, 5.0 * S), "fur", "skull", step=0.8)
    k.box(hd, B(0, 21.4, 22.6, 5.4, 4.2, 4.2), "fur_w", tag="muzzle")
    k.box(hd, B(0, 21.0, 25.6, 4.4, 3.0, 3.6), "fur_w", tag="muzzle")
    k.box(hd, B(0, 23.4, 27.2, 2.4, 1.4, 0.6), "dark", tag="nose")
    k.limb(hd, P(-4.6, 27.0, 21.4), P(4.6, 27.0, 21.4), 1.6 * S, "fur", "brow", d=2.4 * S)
    for sx in (-1, 1):
        W.eye(k, hd, P(sx * 2.6, 25.8, 22.55), 1.6 * S, 0.8 * S)
        k.shard(hd, P(sx * 4.0, 28.0, 16.6), (sx * 0.5, 0.8, -0.8), 3.4 * S, 2.0 * S, mat="fur", tag="ear")
        k.blob(hd, P(sx * 4.8, 22.4, 18.6), (1.6 * S, 2.8 * S, 2.6 * S), "fur_w", "cheek_ruff", step=0.6)
        s0, s1 = P(sx * 1.9, 21.6, 23.8), P(sx * 2.2, 15.6, 24.4)       # the sabres hang from the upper jaw
        k.limb(hd, s0, s1, 1.6 * S, "ice", "sabre", d=1.0 * S)
        k.shard(hd, s1, (0, -1, -0.25), (5.4 if not legend else 6.8) * S, 1.4 * S, mat="ice", tag="sabre")
    k.blob(hd, P(0, 18.4, 22.8), (1.4 * S, 1.0 * S, 1.6 * S), "breath", "frost_breath", step=0.5)
    jw = k.part("jaw", P(0, 20.4, 19.6), (), hd)
    k.limb(jw, P(0, 20.2, 19.6), P(0, 14.6, 23.6), 3.6 * S, "fur_w", "jaw", d=3.2 * S)
    k.limb(jw, P(0, 20.8, 20.0), P(0, 16.6, 23.8), 3.0 * S, "mouth", "mouth", d=2.6 * S)
    W.teeth(k, jw, P(-1.2, 16.0, 23.6), P(1.2, 16.0, 23.6), 3, 1.0 * S, down=False)
    # haunch and tail
    ab = k.part("abdomen", (0, 19, -7), (), body)
    k.blob(ab, (0, 19.4, -12), (7.6, 7.4, 9.4), "fur", "haunch", step=1.0)
    for i, z in enumerate((-8, -12, -16)):
        k.shard(ab, (0, 26.4 - i, z), (0, 1, -0.6), 4.4 - i * 0.6, 2.4, mat="ice", tag="ice_plate")
    tail = [(0, 21, -20), (0, 19, -26), (0, 15, -31), (0, 13, -36), (0, 14, -40)]
    parent = ab
    for t, ((a, b), w) in enumerate(zip(zip(tail, tail[1:]), (3.2, 2.8, 2.4, 2.0))):
        if t < 3:
            parent = k.part("tail%d" % t, a, (), parent)
        k.limb(parent, a, b, w, "fur", "tail")
    k.cluster(parent, (0, 14, -40), 3, 3.4, 1.2, mat="ice", seed=5, spread=0.6, up=(0, 0.3, -1))

    def paw(pw, a):
        k.box(pw, C(a[0], 0, a[2] + 1.0, 5.6, 2.4, 6.2), "fur_w", tag="foot")
        W.claws(k, pw, (a[0], 0.6, a[2] + 3.6), 4, 1.1, 2.0, 0.7, mat="ice")

    def fpaw(pw, a):        # the front paws are its weapons: wide, heavy, long ice hooks
        k.box(pw, C(a[0], 0, a[2] + 1.4, 7.4, 3.0, 7.6), "fur_w", tag="foot")
        k.blob(pw, (a[0], 3.0, a[2] + 0.6), (3.4, 2.0, 3.4), "fur_w", "wrist", step=0.6)
        W.claws(k, pw, (a[0], 0.8, a[2] + 4.8), 4, 1.6, 3.2, 1.0, mat="ice")
    for side, s in ((1, "l"), (-1, "r")):
        leg3(k, body, "f" + s, (side * 6.4, 17, 8), (side * 6.8, 8, 10.4), (side * 6.6, 1.6, 9.4), 7.6, 5.8, fpaw)
        leg3(k, ab, "b" + s, (side * 5.6, 17, -13), (side * 6.0, 9, -17), (side * 5.8, 1.4, -14), 6.4, 4.0, paw)
    W.glow_tags(k, "eye", "frost_breath")
    if legend:
        for sx in (-1, 1):
            k.shard(jw, P(sx * 1.6, 15.2, 23.4), (sx * 0.2, 1, 0.5), 3.4 * S, 1.0 * S, mat="oldice", tag="low_tusk")
        for b in k.s.boxes:
            if b.mat == "ice" and b.tag in ("ice_plate", "mane_spike"):
                b.mat = "oldice"
    grow(k, GROW * (LEGEND_SCALE if legend else 1.0))
    k.s.shaders = W.shaders(
        fur=X.surf(W.SNOWFUR, 0.56, 1.2, 0.18, 0.02, pattern=W.tiger),
        fur_w=X.surf(W.SNOWFUR, 0.66, 1.1, 0.16, 0.0, pattern=W.strands),
        frost=X.surf(W.SNOWFUR, 0.74, 1.0, 0.14, 0.0, pattern=W.shag),
        ice=X.facets(W.ICEL), oldice=X.facets(W.OLDICE),
        breath=X.glow(W.ICE), eye=X.glow(W.ICE, 0.8, 0.16),
    )
    return k.s, k.parts


BONES = ["body", "neck", "head", "jaw", "abdomen", "tail0", "tail1", "tail2"] + \
        ["%s_%s" % (l, b) for l in LEGS for b in ("up", "low", "paw")]

make = frostjaw
LEGEND = "pale_widow"


# ================================================================ its animations (tools/beastkit.py)
# x turns a bone pointing forward downward (a leg: its foot back); y turns it left; z rolls (a leg: its foot out left)

def _wave(length, amp, phase=0.0, base=(0, 0, 0), axis=0, step=2, cycles=1):
    out = []
    for t in range(0, length, step):
        v = list(base)
        v[axis] += amp * math.sin(2 * math.pi * (cycles * t / length + phase))
        out.append([t] + [round(c, 3) for c in v])
    return out


def _gait(length, phases, up, low, paw, base=None, step=2):
    """a leg cycle per leg: the thigh swings (+ back, - forward), the knee and paw fold while the leg comes forward"""
    base = base or {}
    out = {}
    for leg, ph in phases.items():
        b_up, b_low, b_paw = base.get(leg, (0, 0, 0))
        ku, kl, kp = [], [], []
        f_ = 1.0 if leg[0] == "f" else 0.85
        for t in range(0, length, step):
            c = 2 * math.pi * (t / length + ph)
            lift = max(0.0, -math.cos(c))
            ku.append([t, round(b_up + up * f_ * math.sin(c), 2), 0, 0])
            kl.append([t, round(b_low + low * lift * (1.0 if leg[0] == "f" else 0.7), 2), 0, 0])
            kp.append([t, round(b_paw + paw * lift - 0.3 * paw * max(0.0, math.cos(c)), 2), 0, 0])
        out[leg + "_up"], out[leg + "_low"], out[leg + "_paw"] = ku, kl, kp
    return out


def _walk(length=40, crouch=0.0):
    c = crouch
    bones = _gait(length, {"bl": 0.0, "fl": 0.25, "br": 0.5, "fr": 0.75}, 20, 34, 26,
                  base={l: (-14 * c, 30 * c, -10 * c) for l in ("fl", "fr", "bl", "br")})
    bones.update({
        "body": _wave(length, 2.0, 0.0, base=(4 * c, 0, 0), axis=2),
        "neck": _wave(length, 3.0, 0.1, base=(10 * c, 0, 0), axis=0, cycles=2),
        "head": _wave(length, 2.0, 0.35, base=(-6 * c, 0, 0), axis=0, cycles=2),
        "tail0": _wave(length, 9.0, 0.0, base=(6 - 10 * c, 0, 0), axis=1),
        "tail1": _wave(length, 12.0, 0.15, axis=1),
        "tail2": _wave(length, 15.0, 0.3, axis=1),
    })
    return {"len": length, "loop": True, "stride": 3.4 if not c else 2.2, "bones": bones,
            "hips": _wave(length, 0.035, 0.0, base=(0, -0.38 * c, 0), axis=1, cycles=2)}


def _run(length=18):
    bones = _gait(length, {"bl": 0.0, "br": 0.08, "fl": 0.5, "fr": 0.58}, 42, 58, 40, step=1)
    bones.update({
        "body": _wave(length, 7.0, 0.25, axis=0, step=1),
        "abdomen": _wave(length, 12.0, 0.0, axis=0, step=1),
        "neck": _wave(length, 9.0, 0.75, base=(4, 0, 0), axis=0, step=1),
        "head": _wave(length, 5.0, 0.5, axis=0, step=1),
        "jaw": [[0, 8, 0, 0]],
        "tail0": _wave(length, 10.0, 0.0, base=(-6, 0, 0), axis=0, step=1),
        "tail1": _wave(length, 14.0, 0.2, axis=0, step=1),
        "tail2": _wave(length, 16.0, 0.4, axis=0, step=1),
    })
    return {"len": length, "loop": True, "stride": 6.0, "bones": bones, "hips": _wave(length, 0.16, 0.25, axis=1, step=1)}


def _idle(length=80):
    return {"len": length, "loop": True, "bones": {
        "neck": _wave(length, 2.0, 0.0, axis=0, step=4), "head": _wave(length, 2.5, 0.3, axis=0, step=4),
        "jaw": _wave(length, 2.0, 0.1, base=(3, 0, 0), axis=0, step=4),
        "body": _wave(length, 1.0, 0.0, axis=0, step=4),
        "tail0": _wave(length, 7.0, 0.0, base=(4, 0, 0), axis=1, step=4),
        "tail1": _wave(length, 10.0, 0.2, axis=1, step=4),
        "tail2": _wave(length, 14.0, 0.4, axis=1, step=4)},
        "hips": _wave(length, 0.025, 0.0, axis=1, step=4)}


def _both(side, keys):
    """the same keys on both legs of a pair (fl and fr...), the roll (z) mirrored"""
    out = {}
    for s in ("l", "r"):
        for b, ks in keys.items():
            out[side + s + b] = [[t, x, y, z if s == "l" else -z] for t, x, y, z in ks]
    return out


def _clip(length, bones, hips=None, **kw):
    return dict({"len": length, "bones": bones, "hips": hips or []}, **kw)


Z = [0, 0, 0, 0]
CLIPS = {
    "idle": _idle(),
    "walk": _walk(),
    "stalk": _walk(48, 1.0),
    "run": _run(),
    # rears its head back and roars: anyone close is slowed by the cold of it
    "roar": _clip(44, dict({
        "body": [Z, [10, -6, 0, 0], [16, -12, 0, 0], [34, -12, 0, 0], [44, 0, 0, 0]],
        "neck": [Z, [10, 8, 0, 0], [16, -24, 0, 0], [34, -22, 0, 0], [44, 0, 0, 0]],
        "head": [Z, [10, 10, 0, 0], [16, -22, 0, 0], [30, -18, 4, 0], [34, -18, -4, 0], [44, 0, 0, 0]],
        "jaw": [Z, [12, 6, 0, 0], [16, 46, 0, 0], [32, 44, 0, 0], [38, 8, 0, 0], [44, 0, 0, 0]],
        "tail0": [Z, [16, 22, 0, 0], [34, 22, 0, 0], [44, 0, 0, 0]],
        "tail1": [Z, [16, 14, 0, 0], [34, 14, 0, 0], [44, 0, 0, 0]],
        "abdomen": [Z, [16, 8, 0, 0], [34, 8, 0, 0], [44, 0, 0, 0]]},
        **_both("f", {"_up": [Z, [16, -14, 0, 4], [34, -14, 0, 4], [44, 0, 0, 0]],
                      "_low": [Z, [16, 8, 0, 0], [34, 8, 0, 0], [44, 0, 0, 0]]}),
        **_both("b", {"_up": [Z, [16, 12, 0, 0], [34, 12, 0, 0], [44, 0, 0, 0]],
                      "_low": [Z, [16, -10, 0, 0], [34, -10, 0, 0], [44, 0, 0, 0]]})),
        hips=[Z, [10, 0, -0.08, 0], [16, 0, 0.1, 0], [34, 0, 0.1, 0], [44, 0, 0, 0]],
        events={"roar": [16]}, reach=7.0),
    # crouches low, springs, lands on you claws first and bites
    "pounce": _clip(40, dict({
        "body": [Z, [12, 8, 0, 0], [15, -20, 0, 0], [20, -8, 0, 0], [25, 12, 0, 0], [30, 6, 0, 0], [40, 0, 0, 0]],
        "abdomen": [Z, [12, -6, 0, 0], [15, 14, 0, 0], [20, 6, 0, 0], [25, -10, 0, 0], [40, 0, 0, 0]],
        "neck": [Z, [12, 14, 0, 0], [15, -10, 0, 0], [22, 4, 0, 0], [26, 18, 0, 0], [40, 0, 0, 0]],
        "head": [Z, [12, -10, 0, 0], [18, -14, 0, 0], [24, 10, 0, 0], [40, 0, 0, 0]],
        "jaw": [Z, [12, 10, 0, 0], [18, 44, 0, 0], [24, 44, 0, 0], [26, 0, 0, 0], [40, 0, 0, 0]],
        "tail0": [Z, [12, -8, 0, 0], [16, 20, 0, 0], [24, 10, 0, 0], [40, 0, 0, 0]],
        "tail1": [Z, [12, 10, 0, 0], [18, -12, 0, 0], [26, 14, 0, 0], [40, 0, 0, 0]]},
        **_both("f", {"_up": [Z, [12, -26, 0, 0], [15, -72, 0, 6], [22, -80, 0, 8], [25, -30, 0, 4], [30, -10, 0, 0], [40, 0, 0, 0]],
                      "_low": [Z, [12, 52, 0, 0], [15, -8, 0, 0], [22, 10, 0, 0], [25, 36, 0, 0], [40, 0, 0, 0]],
                      "_paw": [Z, [12, -20, 0, 0], [16, 30, 0, 0], [24, 50, 0, 0], [26, -10, 0, 0], [40, 0, 0, 0]]}),
        **_both("b", {"_up": [Z, [12, -38, 0, 0], [15, 48, 0, 0], [22, 58, 0, 0], [26, 10, 0, 0], [40, 0, 0, 0]],
                      "_low": [Z, [12, 62, 0, 0], [15, 12, 0, 0], [22, 30, 0, 0], [26, 40, 0, 0], [40, 0, 0, 0]],
                      "_paw": [Z, [12, -30, 0, 0], [15, 40, 0, 0], [26, 0, 0, 0], [40, 0, 0, 0]]})),
        hips=[Z, [12, 0, -0.55, 0], [15, 0, 0.3, 0], [20, 0, 0.9, 0], [25, 0, -0.25, 0], [30, 0, -0.1, 0], [40, 0, 0, 0]],
        events={"leap": [13], "hit": [24, 25, 26]}, reach=3.0, leap=[1.25, 0.55], range=[5, 14]),
    # head back, then the sabres driven down into whoever's in front
    "bite": _clip(26, dict({
        "body": [Z, [8, -5, 0, 0], [12, 7, 0, 0], [26, 0, 0, 0]],
        "neck": [Z, [8, -16, 0, 0], [12, 20, 0, 0], [18, 12, 0, 0], [26, 0, 0, 0]],
        "head": [Z, [8, -20, 0, 0], [12, 18, 0, 0], [18, 10, 0, 0], [26, 0, 0, 0]],
        "jaw": [Z, [6, 30, 0, 0], [9, 40, 0, 0], [12, 0, 0, 0], [26, 0, 0, 0]]},
        **_both("f", {"_up": [Z, [8, 6, 0, 0], [12, -16, 0, 0], [26, 0, 0, 0]],
                      "_low": [Z, [12, 14, 0, 0], [26, 0, 0, 0]]})),
        hips=[Z, [8, 0, 0.04, -0.2], [12, 0, -0.1, 0.45], [20, 0, 0, 0.2], [26, 0, 0, 0]],
        events={"hit": [11]}, reach=3.4, arc=70),
    # up on its haunches a little, the left paw raised and raked across
    "swipe": _clip(26, {
        "body": [Z, [8, -8, 0, -6], [13, 6, 0, 5], [26, 0, 0, 0]],
        "neck": [Z, [8, -8, -10, 0], [13, 8, 12, 0], [26, 0, 0, 0]],
        "head": [Z, [8, 0, -8, 0], [13, 6, 10, 0], [26, 0, 0, 0]],
        "jaw": [Z, [8, 22, 0, 0], [13, 14, 0, 0], [26, 0, 0, 0]],
        "fl_up": [Z, [8, -70, 0, 26], [11, -50, 0, 10], [14, -12, 0, -18], [26, 0, 0, 0]],
        "fl_low": [Z, [8, 64, 0, 0], [11, 20, 0, 0], [14, 6, 0, 0], [26, 0, 0, 0]],
        "fl_paw": [Z, [8, 40, 0, 0], [12, -20, 0, 0], [26, 0, 0, 0]],
        "fr_up": [Z, [8, -8, 0, 0], [26, 0, 0, 0]],
        "bl_up": [Z, [8, 8, 0, 0], [26, 0, 0, 0]], "br_up": [Z, [8, 8, 0, 0], [26, 0, 0, 0]]},
        hips=[Z, [8, 0, 0.1, -0.15], [13, 0, -0.05, 0.25], [26, 0, 0, 0]],
        events={"hit": [13]}, reach=3.2, arc=110),
    "hurt": _clip(10, {
        "body": [Z, [3, -6, 0, 3], [10, 0, 0, 0]], "neck": [Z, [3, -12, 0, 0], [10, 0, 0, 0]],
        "head": [Z, [3, -10, 0, 0], [10, 0, 0, 0]], "jaw": [Z, [3, 18, 0, 0], [10, 0, 0, 0]]}),
    # it goes down on its side and the cold goes out of its eyes
    "death": _clip(50, dict({
        "body": [Z, [8, -10, 0, 0], [26, 6, 0, 82], [50, 6, 0, 86]],
        "neck": [Z, [8, -18, 0, 0], [26, 10, 0, 0], [50, 14, 6, 0]],
        "head": [Z, [8, -18, 0, 0], [26, 6, 0, -8], [50, 8, 0, -10]],
        "jaw": [Z, [8, 36, 0, 0], [30, 26, 0, 0], [50, 22, 0, 0]],
        "tail0": [Z, [26, -20, 0, 0], [50, -24, 10, 0]], "tail1": [Z, [50, -10, 14, 0]]},
        **_both("f", {"_up": [Z, [26, -18, 0, -10], [50, -24, 0, -14]], "_low": [Z, [50, 30, 0, 0]]}),
        **_both("b", {"_up": [Z, [26, 16, 0, -10], [50, 22, 0, -12]], "_low": [Z, [50, 26, 0, 0]]})),
        hips=[Z, [8, 0, 0.05, 0], [26, 0, -1.25, 0], [50, 0, -1.3, 0]]),
}


# ---------------------------------------------------------------- 11/5 boss moves (the Frostmaw bar): a move for every distance
CLIPS.update({
    # left paw, then right: the second rake breaks a raised guard
    "swipe2": _clip(36, {
        "body": [Z, [7, -8, 0, -6], [10, 6, 0, 5], [16, -8, 0, 6], [21, 6, 0, -5], [36, 0, 0, 0]],
        "neck": [Z, [7, -8, -10, 0], [10, 8, 12, 0], [16, -8, 10, 0], [21, 8, -12, 0], [36, 0, 0, 0]],
        "head": [Z, [7, 0, -8, 0], [10, 6, 10, 0], [16, 0, 8, 0], [21, 6, -10, 0], [36, 0, 0, 0]],
        "jaw": [Z, [7, 22, 0, 0], [10, 14, 0, 0], [16, 26, 0, 0], [21, 14, 0, 0], [36, 0, 0, 0]],
        "fl_up": [Z, [7, -70, 0, 26], [9, -50, 0, 10], [11, -12, 0, -18], [16, -4, 0, 0], [36, 0, 0, 0]],
        "fl_low": [Z, [7, 64, 0, 0], [9, 20, 0, 0], [11, 6, 0, 0], [16, 0, 0, 0], [36, 0, 0, 0]],
        "fl_paw": [Z, [7, 40, 0, 0], [10, -20, 0, 0], [16, 0, 0, 0], [36, 0, 0, 0]],
        "fr_up": [Z, [7, -8, 0, 0], [11, -4, 0, 0], [16, -70, 0, -26], [19, -50, 0, -10], [21, -12, 0, 18], [36, 0, 0, 0]],
        "fr_low": [Z, [11, 0, 0, 0], [16, 64, 0, 0], [19, 20, 0, 0], [21, 6, 0, 0], [36, 0, 0, 0]],
        "fr_paw": [Z, [11, 0, 0, 0], [16, 40, 0, 0], [20, -20, 0, 0], [36, 0, 0, 0]],
        "bl_up": [Z, [7, 8, 0, 0], [30, 8, 0, 0], [36, 0, 0, 0]], "br_up": [Z, [7, 8, 0, 0], [30, 8, 0, 0], [36, 0, 0, 0]]},
        hips=[Z, [7, 0, 0.1, -0.15], [10, 0, -0.05, 0.3], [16, 0, 0.1, 0.15], [21, 0, -0.05, 0.55], [36, 0, 0, 0]],
        events={"hit": [10, 21], "guard": [21]}, reach=3.4, arc=130, range=[0, 4.5], dmg=0.8),
    # draws the cold in (head up), then breathes a narrow cone of it, sweeping slowly across
    "breath": _clip(64, dict({
        "body": [Z, [14, -8, 0, 0], [20, 6, 0, 0], [52, 6, 0, 0], [64, 0, 0, 0]],
        "abdomen": [Z, [14, 6, 0, 0], [52, 2, 0, 0], [64, 0, 0, 0]],
        "neck": [Z, [14, -22, 0, 0], [20, 14, -16, 0], [36, 14, 16, 0], [52, 14, -6, 0], [58, 4, 0, 0], [64, 0, 0, 0]],
        "head": [Z, [14, -20, 0, 0], [20, -4, -8, 0], [36, -4, 8, 0], [52, -4, -3, 0], [64, 0, 0, 0]],
        "jaw": [Z, [10, 8, 0, 0], [14, 4, 0, 0], [20, 48, 0, 0], [52, 46, 0, 0], [58, 6, 0, 0], [64, 0, 0, 0]],
        "tail0": [Z, [14, 16, 0, 0], [52, 10, 0, 0], [64, 0, 0, 0]],
        "tail1": [Z, [14, -10, 0, 0], [52, -6, 0, 0], [64, 0, 0, 0]]},
        **_both("f", {"_up": [Z, [20, -10, 0, 6], [52, -10, 0, 6], [64, 0, 0, 0]],
                      "_low": [Z, [20, 14, 0, 0], [52, 14, 0, 0], [64, 0, 0, 0]]}),
        **_both("b", {"_up": [Z, [20, 10, 0, 0], [52, 10, 0, 0], [64, 0, 0, 0]]})),
        hips=[Z, [14, 0, 0.06, -0.1], [20, 0, -0.12, 0.15], [52, 0, -0.12, 0.15], [64, 0, 0, 0]],
        events={"breath": [20]}, spray=[20, 52], reach=8.0, arc=50, range=[3, 10], dmg=0.1, cool=260),
    # smashes the right paw into the ground, tears a slab of ice up and flings it at you
    "hurl": _clip(44, dict({
        "body": [Z, [10, -14, 0, -6], [14, 10, 0, 4], [20, 4, 0, 0], [24, -10, 0, -4], [27, 8, 0, 4], [44, 0, 0, 0]],
        "neck": [Z, [10, -12, 0, 0], [14, 20, 0, 0], [22, 10, 0, 0], [27, -6, 0, 0], [44, 0, 0, 0]],
        "head": [Z, [10, -8, 0, 0], [14, 14, 0, 0], [27, -10, 0, 0], [44, 0, 0, 0]],
        "jaw": [Z, [10, 24, 0, 0], [14, 36, 0, 0], [20, 10, 0, 0], [27, 40, 0, 0], [34, 10, 0, 0], [44, 0, 0, 0]],
        "fr_up": [Z, [10, -90, 0, -14], [14, -30, 0, -6], [20, -26, 0, -4], [24, 30, 0, -10], [27, -80, 0, -20], [32, -40, 0, -6], [44, 0, 0, 0]],
        "fr_low": [Z, [10, 70, 0, 0], [14, 4, 0, 0], [20, 6, 0, 0], [24, 40, 0, 0], [27, 0, 0, 0], [44, 0, 0, 0]],
        "fr_paw": [Z, [10, 40, 0, 0], [14, -10, 0, 0], [24, 30, 0, 0], [27, -30, 0, 0], [44, 0, 0, 0]],
        "fl_up": [Z, [10, -6, 0, 4], [27, -6, 0, 4], [44, 0, 0, 0]],
        "tail0": [Z, [10, 14, 0, 0], [27, -10, 0, 0], [44, 0, 0, 0]]},
        **_both("b", {"_up": [Z, [10, 14, 0, 0], [30, 8, 0, 0], [44, 0, 0, 0]]})),
        hips=[Z, [10, 0, 0.12, -0.2], [14, 0, -0.1, 0.25], [27, 0, 0.05, -0.05], [44, 0, 0, 0]],
        events={"dig": [14], "throw": [27]}, range=[9, 24], throw=1.6, dmg=0.9, cool=200),
    # hug it and it springs aside (the server throws it sideways) - and usually breathes on you next
    "dodge": _clip(18, dict({
        "body": [Z, [4, 4, 0, 0], [8, -4, 0, 0], [12, 6, 0, 0], [18, 0, 0, 0]],
        "neck": [Z, [4, 10, 0, 0], [8, -6, 0, 0], [18, 0, 0, 0]],
        "tail0": [Z, [8, -18, 0, 0], [18, 0, 0, 0]]},
        **_both("f", {"_up": [Z, [4, -18, 0, 0], [8, -30, 0, 10], [12, -10, 0, 0], [18, 0, 0, 0]],
                      "_low": [Z, [4, 34, 0, 0], [8, 50, 0, 0], [12, 20, 0, 0], [18, 0, 0, 0]],
                      "_paw": [Z, [4, -14, 0, 0], [8, 30, 0, 0], [12, -6, 0, 0], [18, 0, 0, 0]]}),
        **_both("b", {"_up": [Z, [4, -24, 0, 0], [8, 20, 0, 10], [12, -14, 0, 0], [18, 0, 0, 0]],
                      "_low": [Z, [4, 40, 0, 0], [8, 40, 0, 0], [12, 30, 0, 0], [18, 0, 0, 0]],
                      "_paw": [Z, [4, -16, 0, 0], [8, 20, 0, 0], [12, -10, 0, 0], [18, 0, 0, 0]]})),
        hips=[Z, [4, 0, -0.4, 0], [6, 0, 0, 0], [12, 0, -0.3, 0], [18, 0, 0, 0]],
        events={"dodge": [5]}, side=1.0, cool=160),
    # under 60%: rears up on its hind legs, paws high, and brings its whole weight down in front of it
    "slam": _clip(56, dict({
        "body": [Z, [20, -46, 0, 0], [28, -50, 0, 0], [32, 14, 0, 0], [36, 10, 0, 0], [46, 4, 0, 0], [56, 0, 0, 0]],
        "abdomen": [Z, [20, 22, 0, 0], [28, 24, 0, 0], [32, -6, 0, 0], [40, 0, 0, 0], [56, 0, 0, 0]],
        "neck": [Z, [20, 24, 0, 0], [28, 28, 0, 0], [31, -10, 0, 0], [34, 22, 0, 0], [46, 6, 0, 0], [56, 0, 0, 0]],
        "head": [Z, [20, 10, 0, 0], [28, 14, 0, 0], [32, 8, 0, 0], [56, 0, 0, 0]],
        "jaw": [Z, [20, 30, 0, 0], [28, 44, 0, 0], [32, 40, 0, 0], [38, 10, 0, 0], [56, 0, 0, 0]],
        "tail0": [Z, [20, -20, 0, 0], [32, 20, 0, 0], [56, 0, 0, 0]]},
        **_both("f", {"_up": [Z, [20, -40, 0, 14], [28, -50, 0, 18], [31, -60, 0, 6], [33, -28, 0, 6], [46, -10, 0, 0], [56, 0, 0, 0]],
                      "_low": [Z, [20, 40, 0, 0], [28, 50, 0, 0], [31, 10, 0, 0], [33, 10, 0, 0], [56, 0, 0, 0]],
                      "_paw": [Z, [20, 30, 0, 0], [28, 40, 0, 0], [31, -20, 0, 0], [33, 0, 0, 0], [56, 0, 0, 0]]}),
        **_both("b", {"_up": [Z, [20, 40, 0, 0], [28, 44, 0, 0], [32, -10, 0, 0], [40, 0, 0, 0], [56, 0, 0, 0]],
                      "_low": [Z, [20, -20, 0, 0], [32, 10, 0, 0], [56, 0, 0, 0]]})),
        hips=[Z, [20, 0, 0.6, -0.3], [28, 0, 0.7, -0.3], [32, 0, -0.2, 0.5], [36, 0, -0.1, 0.5], [46, 0, 0, 0.2], [56, 0, 0, 0]],
        events={"slam": [32]}, front=3.0, radius=3.2, phase=2, dmg=2.4, cool=500, odds=0.35),
})

# hips fitted so the lowest planted paw stays on the floor (python tools/beastkit.py frostjaw fit <clip> [air ticks a-b])
FIT = {
    "slam": [[0, 0.0, 0.0, 0.0], [20, 0.0, 0.747, -0.3], [28, 0.0, 0.971, -0.3], [31, 0.0, 0.008, 0.375], [32, 0.0, -0.007, 0.5], [33, 0.0, 0.068, 0.5], [34, 0.0, 0.054, 0.5], [36, 0.0, 0.039, 0.5], [38, 0.0, 0.043, 0.469], [40, 0.0, 0.036, 0.394], [46, 0.0, 0.015, 0.2], [56, 0.0, 0.0, 0.0]],
    "hurl": [[0, 0.0, 0.0, 0.0], [10, 0.0, 0.43, -0.2], [14, 0.0, 0.106, 0.25], [20, 0.0, 0.054, 0.117], [22, 0.0, 0.212, 0.049], [24, 0.0, 0.312, -0.009], [27, 0.0, 0.072, -0.05], [30, 0.0, 0.068, -0.046], [32, 0.0, 0.06, -0.04], [34, 0.0, 0.05, -0.032], [44, 0.0, 0.0, 0.0]],
    "swipe2": [[0, 0.0, 0.0, 0.0], [7, 0.0, 0.281, -0.15], [9, 0.0, 0.057, 0.183], [10, 0.0, 0.14, 0.3], [11, 0.0, 0.128, 0.289], [16, 0.0, 0.281, 0.15], [19, 0.0, 0.03, 0.409], [20, 0.0, 0.107, 0.508], [21, 0.0, 0.152, 0.55], [30, 0.0, 0.059, 0.194], [36, 0.0, 0.0, 0.0]],
    "breath": [[0, 0.0, 0.0, 0.0], [10, 0.0, 0.135, -0.08], [14, 0.0, 0.171, -0.1], [20, 0.0, 0.112, 0.15], [36, 0.0, 0.112, 0.15], [52, 0.0, 0.112, 0.15], [58, 0.0, 0.062, 0.075], [64, 0.0, 0.0, 0.0]],
    "dodge": [[0, 0.0, 0.0, 0.0], [4, 0.0, 0.058, 0.0], [6, 0.0, 0.0, 0.0], [8, 0.0, 0.1, 0.0], [12, 0.0, 0.064, 0.0], [18, 0.0, 0.0, 0.0]],
}
for _n, _h in FIT.items():
    CLIPS[_n]["hips"] = _h


# the clips were keyed on the 1.5 body: its moves, strides and reach grow with it (a leap's lift stays, it isn't a flea)
K = GROW / 1.5


def _grown(c):
    c = dict(c)
    c["hips"] = [[t, x * K, y * K, z * K] for t, x, y, z in c.get("hips", [])]
    for key in ("stride", "reach", "radius", "front", "throw"):
        if key in c:
            c[key] = round(c[key] * K, 2)
    if "range" in c:
        c["range"] = [round(v * K, 2) for v in c["range"]]
    if "leap" in c:
        c["leap"] = [round(c["leap"][0] * K, 2), c["leap"][1]]
    return c


CLIPS = {n: _grown(c) for n, c in CLIPS.items()}
