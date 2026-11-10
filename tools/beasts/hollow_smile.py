"""The Hollow Smile: the jungle's Legend. Too tall and too thin, black as the canopy at night with teal marks that glow
along it, four long arms ending in finger-claws, legs bent backward like a heron's; its face is a white wooden mask
carved with a smile far too wide, two pinpricks of light deep in the eye holes. It hangs in the canopy and drops.
Biped plus a second pair of arms (al2/ar2)."""
import math

from legendkit import X, C, ramp, W, grow, legs, arms, BIPED  # noqa: F401

GROW = 1.5
HITBOX = (2.2, 6.6)
IS_LEGEND = True
STATS = dict(hp=480, speed=0.34, dmg=20, armor=4, kb=0.8)
EGG, SPOTS = 0x101018, 0x40e4cc
MASK = ramp("#5a5244", "#867c68", "#aaa08a", "#c8c0aa", "#e2dcc8", "#f6f2e4")
SKIN = ramp("#030305", "#07070b", "#0c0c12", "#12121a", "#191924", "#22222e")


def fingers(k, h, wr, sx, n=4, L_=9, fwd=1.0):
    k.blob(h, (wr[0], wr[1] - 1.6, wr[2] + 0.4), (2.0, 2.0, 2.2), "skin", "palm", step=0.5)
    for i in range(n):
        a = (i - (n - 1) / 2) * 0.3
        base = (wr[0] + math.sin(a) * 1.8, wr[1] - 2.6, wr[2] + 1.0)
        tip = (wr[0] + math.sin(a) * 4.0, wr[1] - 2.6 - L_, wr[2] + 2.0 + fwd * 3)
        k.limb(h, base, tip, 0.9, "skin", "finger", d=0.9)
        k.shard(h, tip, (0, -1, 0.3 * fwd), 2.4, 0.8, mat="claw", tag="claw")


def marks(k, part, a, b):
    k.limb(part, a, b, 0.6, "mark", "mark", d=0.6, group="glow")


def hollow_smile(name="hollow_smile", legend=False):
    k = X.Kit(name)
    hips = k.part("hips", (0, 34, 0))
    k.blob(hips, (0, 34, 0), (6, 3.6, 4.6), "skin", "pelvis", step=0.7)

    def foot(ft, sx, an):                                # long feet, three toes forward, one back
        k.limb(ft, an, (an[0], 1.4, an[2] + 1.6), 3.0, "skin", "metatarsal", d=3.0)
        k.box(ft, C(an[0], 0, an[2] + 4.6, 4.2, 2.0, 10), "skin", tag="foot")
        for t in range(3):
            k.shard(ft, (an[0] + (t - 1) * 1.6, 0.8, an[2] + 9.4), (0, -0.25, 1), 3.0, 0.9, mat="claw", tag="claw")
        k.shard(ft, (an[0], 0.8, an[2] - 0.2), (0, -0.2, -1), 2.4, 0.9, mat="claw", tag="claw")

    def shin(low, sx, kn):
        marks(k, low, (kn[0], kn[1] - 2, kn[2] - 1.8), (kn[0], kn[1] - 10, kn[2] - 5.4))
    legs(k, hips, 4.6, 34, (5.5, 20, 6), (5.5, 6, -3), 5.0, 4.0, "skin", foot, plate=shin)

    # ---- a thin torso, every rib showing
    ch = k.part("chest", (0, 37, 0), (("x", 12),), hips)
    k.stack(ch, 0, 0, [(36, 8, 6.6), (42, 11, 7.4), (48, 15, 8.6), (54, 18, 9), (57, 12, 7)], "skin", "torso", step=0.8)
    for i in range(5):
        y = 44 + i * 2.4
        for sx in (-1, 1):
            k.limb(ch, (sx * 1.2, y, 4.4), (sx * (5 + i * 0.7), y - 1.4, 3.2), 0.8, "rib", "rib", d=0.6)
    marks(k, ch, (0, 38, 4.0), (0, 56, 4.6))
    for sx in (-1, 1):
        marks(k, ch, (sx * 4, 40, 3.4), (sx * 8, 52, 4.0))
    # the neck, long, and the head on it
    hd = k.part("head", (0, 57, 1), (("x", -12),), ch)
    k.limb(hd, (0, 56, 1), (0, 63, 3), 3.4, "skin", "neck", d=3.4)
    k.blob(hd, (0, 66, 3), (4.2, 4.6, 4.0), "skin", "skull", step=0.6)
    # the mask: a long white oval, the smile carved ear to ear
    k.stack(hd, 0, 6.8, [(59.5, 6, 1.4), (61, 8.6, 1.6), (65, 10, 1.8), (69, 9.6, 1.8), (72, 7, 1.6), (73.5, 4, 1.4)], "mask", "mask", step=0.6)
    pts = []
    for i in range(11):                                  # the smile: a curve up at both ends, far too wide
        f = (i - 5) / 5
        pts.append((f * 4.6, 62.6 + 2.2 * f * f, 7.9))
    for a, b in zip(pts, pts[1:]):
        k.limb(hd, a, b, 0.9, "dark", "smile", d=0.5)
    for i in range(1, 10, 2):
        k.box(hd, C(pts[i][0], pts[i][1] - 0.2, 8.0, 0.5, 1.0, 0.3), "mask", tag="tooth")
    for sx in (-1, 1):
        k.box(hd, C(sx * 2.2, 67.4, 7.8, 2.0, 2.6, 0.6), "dark", tag="eyehole")
        W.eye(k, hd, (sx * 2.2, 68.3, 8.0), 0.6, 0.6)
        k.limb(hd, (sx * 3.8, 70, 7.6), (sx * 1.0, 69, 7.9), 0.5, "dark", "brow_cut", d=0.4)
    for i in range(10):                                  # hair like black vines, long
        a = math.pi * (0.95 + 1.1 * i / 9)
        top = (math.cos(a) * 3.8, 69, 3 + math.sin(a) * 3.6)
        bot = (math.cos(a) * 5.4, 48 + (i % 3) * 3, 1 + math.sin(a) * 4.8)
        k.limb(hd, top, bot, 1.0, "vine", "hair", d=0.9)

    # ---- the upper arms, long enough to touch its knees
    def upper(up, sx):
        marks(k, up, (sx * 11, 53, 1.2), (sx * 13.4, 43, 2.2))

    def hand(h, sx, wr):
        fingers(k, h, wr, sx, 4, 9)
    arms(k, ch, (10, 55, 0), (14, 40, 2), (15, 25, 4), 3.4, 3.0, "skin", hand, hunch=12, upper=upper)
    # ---- the second pair, lower on its ribs, held forward and bent
    for sx, s in ((1, "l"), (-1, "r")):
        sh, el, wr = (sx * 7.4, 47, 2.4), (sx * 12, 38, 8), (sx * 11, 30, 13)
        up = k.part("a%s2_up" % s, sh, (("x", -12),), ch)
        k.limb(up, sh, el, 3.0, "skin", "arm")
        low = k.part("a%s2_low" % s, el, (), up)
        k.limb(low, el, wr, 2.6, "skin", "forearm")
        h = k.part("a%s2_hand" % s, wr, (), low)
        fingers(k, h, wr, sx, 3, 7, fwd=1.4)

    W.glow_tags(k, "eye", "mark")
    grow(k, GROW * (1.25 if legend else 1.0))
    k.s.shaders = W.shaders(
        skin=X.surf(SKIN, 0.5, 1.5, 0.08, 0.12),
        rib=X.surf(SKIN, 0.85, 1.4, 0.08, 0.1),
        mask=X.surf(MASK, 0.66, 1.2, 0.14, 0.08, pattern=W.grain),
        claw=X.surf(W.HORN, 0.5, 1.4, 0.1, 0.1),
        vine=X.surf(W.KELP, 0.4, 1.1, 0.18, 0.0),
        mark=X.glow(W.STRIPE, 0.6, 0.3), eye=X.glow(W.STRIPE, 0.9, 0.1),
    )
    return k.s, k.parts


BONES = list(BIPED) + ["a%s2_%s" % (s, b) for s in "lr" for b in ("up", "low", "hand")]
make = hollow_smile
LEGEND = None
import legendkit as L

# it drops on you, four arms raking, it seizes and flings you; under 60% it is suddenly behind you
_blink = L.with_events(L.sweep(30, 18, reach=5.0, arc=150, dmg=1.2, range=[0, 14], phase=2, cool=200), blink=[6], hit=[18])
CLIPS = L.fitted("hollow_smile", {
    "idle": L.idle(),
    "walk": L.walk(40, 24, 56, 3.6),
    "run": L.walk(24, 34, 70, 5.4, 1.2),
    "drop": L.lunge(40, 13, 24, reach=4.0, arc=120, dmg=1.3, leap=[1.6, 0.7], range=[6, 16], cool=140),
    "rake": L.flurry(40, (10, 15, 20, 25), ("ar", "al", "ar2", "al2"), reach=4.2, arc=120, dmg=0.6, range=[0, 4.5]),
    "seize": L.grab(46, 16, 30, reach=4.0, arc=60, dmg=1.2, fling=1.6, range=[0, 4], cool=200),
    "giggle": L.roar(46, 18, reach=8.0, elem=7),
    "blink": _blink,
    "hurt": L.hurt(),
    "death": L.death_kneel(),
})
AIR = {"drop": [(14, 23)]}
