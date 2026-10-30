"""The Joined weapons' hand-built shapes (tools/joinedgear.py): each silhouette says two made one, in old pale steel split
by a seam of molten gold, with the Cold Forge's stone hands and two locked rings. Plugged into weaponforge's build."""
import math
import zlib

import weaponforge as W
from weaponforge import bx, ring_xy


def rings(s, x, y, size, z=1.0):
    """two rings locked through each other, one gold, one burning"""
    r = size * 0.42
    ring_xy(s, x - r * 0.55, y, r, size * 0.17, "acc", 12, depth=z)
    ring_xy(s, x + r * 0.55, y, r, size * 0.17, "glow", 12, glow=True, depth=z)


def grip(s, y0=-4.6, n=6.8, w=2.0):
    bx(s, 0, y0, 0, w, n, w, "wrap", tag="grip")
    for y in (y0 + 1.2, y0 + 3.0, y0 + 4.8):
        bx(s, 0, y, 0, w + 0.3, 0.5, w + 0.3, "acc", tag="wire")
    bx(s, 0, y0 - 1.6, 0, 2.8, 1.8, 2.8, "dark", tag="pommel")
    bx(s, 0, y0 - 1.1, 0, 1.2, 0.9, 3.0, "glow", glow=True)


def cup(s, side, cx, y0, big, mat="blade"):
    """a stone hand rising from its palm, curling in over what it holds"""
    bx(s, cx + side * 2.4 * big, y0 - 1.2 * big, 0, 2.2 * big, 3.2 * big, 3.6 * big, mat, tag="palm")
    for z, k in ((-1.25 * big, 0.9), (0.0, 1.0), (1.25 * big, 0.85)):
        W.chainp(s, (cx + side * 2.8 * big, y0 + 1.6 * big),
                 [(3.0 * big * k, -side * 26, 1.2 * big, 1.1 * big), (3.2 * big * k, side * 8, 1.1 * big, 1.0 * big),
                  (2.4 * big * k, side * 52, 0.9 * big, 0.9 * big), (1.3 * big * k, side * 88, 0.7 * big, 0.7 * big)], mat, z=z)
    W.chainp(s, (cx + side * 1.6 * big, y0 - 0.6 * big), [(2.0 * big, side * 55, 1.1 * big, 1.1 * big), (1.4 * big, side * 95, 0.8 * big, 0.8 * big)], mat, z=1.9 * big)


def fist(s, side, cx, y, sz):
    """a clenched stone fist, knuckles outward, a gold bracer at the wrist"""
    fx = cx + side * sz * 0.72
    bx(s, fx, y, 0, sz * 0.86, sz, sz * 0.82, "blade", tag="fist")
    for k in range(4):                                     # the four knuckles
        bx(s, fx + side * sz * 0.46, y + sz * (0.06 + 0.23 * k), 0, sz * 0.2, sz * 0.2, sz * 0.86, "blade", tag="knuckle")
        bx(s, fx + side * sz * 0.2, y + sz * (0.09 + 0.23 * k), 0, sz * 0.4, sz * 0.04, sz * 0.84, "dark")
    bx(s, fx - side * sz * 0.05, y + sz * 0.02, sz * 0.46, sz * 0.62, sz * 0.26, sz * 0.2, "blade", tag="thumb")
    bx(s, cx + side * sz * 0.2, y + sz * 0.1, 0, sz * 0.22, sz * 0.8, sz * 0.92, "acc", tag="bracer")


def oathbinder(th, it, seed):
    """two blades laid side by side, the seam burning between them, bound by gold, one point"""
    s = W.Sword(it["id"])
    L, y0 = 25.0, 4.4
    for side in (-1, 1):
        W.blade_body(s, y0 + 1.2, y0 + L, lambda t: 2.5 * (1 - 0.3 * t), 1.2, cxf=lambda t, q=side: q * 1.75 * (1 - t ** 3), spine=False)
    bx(s, 0, y0 + 1.2, 0, 1.1, L - 2, 0.9, "glow", glow=True, tag="seam")
    W.tip(s, 0, y0 + L, 3.0, 1.2)
    for y in (0.22, 0.5, 0.76):
        bx(s, 0, y0 + L * y, 0, 6.6 - y * 2.8, 1.0, 1.7, "acc", tag="band")
    bx(s, 0, y0 - 0.6, 0, 7.4, 1.8, 2.0, "dark", tag="ricasso")
    rings(s, 0, 2.2, 7.0, 2.0)
    grip(s)
    return s


def twinfang(th, it, seed):
    """two fangs from one grip, bowing apart and meeting again at the points"""
    s = W.Sword(it["id"])
    L, y0 = 13.0, 3.4
    for side in (-1, 1):
        W.blade_body(s, y0 + 0.8, y0 + L, lambda t: 1.9 * (1 - 0.45 * t), 1.0, cxf=lambda t, q=side: q * 2.8 * math.sin(t * math.pi) ** 0.8, step=1.2, spine=False)
    W.tip(s, 0, y0 + L, 1.6, 1.0, n=2)
    bx(s, 0, y0 + 3.6, 0, 0.7, L * 0.56, 0.7, "glow", glow=True, tag="seam")
    rings(s, 0, 2.0, 5.0, 1.8)
    grip(s, -3.8, 5.6, 1.8)
    return s


def concord(th, it, seed):
    """a maul whose head is two stone fists, knuckles out, the fire between them where they meet"""
    s = W.Sword(it["id"])
    W.haft(s, th, -9.0, 15.0, 2.2, "dark")
    grip(s, -6.0, 8.0, 2.4)
    sz, y = 7.6, 13.0
    for side in (-1, 1):
        fist(s, side, 0, y, sz)
    bx(s, 0, y + 0.6, 0, 1.4, sz - 1.2, 4.0, "glow", glow=True, tag="seam")
    bx(s, 0, y + sz, 0, 3.2, 1.2, 3.2, "acc", tag="crown")
    W.chainp(s, (0, y + sz + 1.1), [(2.2, 0, 1.1, 1.1), (1.4, 0, 0.5, 0.5)], "blade")
    rings(s, 0, 9.4, 4.4, 1.8)
    return s


def wound(s, y0, n, r, turn, w):
    """two shafts wound round each other"""
    for k in range(n):
        a = k * turn
        for q, c in ((0, "dark"), (math.pi, "acc")):
            bx(s, r * math.cos(a + q), y0 + k, r * math.sin(a + q), w, 1.05, w, c, tag="shaft")


def unison(th, it, seed):
    """two thin shafts wound round each other to a forked head that closes on one point"""
    s = W.Sword(it["id"])
    wound(s, -16.0, 34, 0.8, 0.55, 0.9)
    bx(s, 0, -5.0, 0, 2.6, 9.0, 2.6, "wrap", tag="grip")
    y = 18.0
    for side in (-1, 1):
        W.blade_body(s, y, y + 11.0, lambda t: 2.0 * (1 - 0.5 * t), 1.1, cxf=lambda t, q=side: q * 2.0 * math.sin(t * math.pi), step=1.2, spine=False)
    W.tip(s, 0, y + 11.0, 1.8, 1.1, n=3)
    bx(s, 0, y + 1.0, 0, 0.8, 8.5, 0.8, "glow", glow=True, tag="seam")
    rings(s, 0, 16.4, 5.2, 2.0)
    bx(s, 0, -18.0, 0, 2.4, 2.0, 2.4, "dark", tag="shoe")
    return s


def two_hearted(th, it, seed):
    """a great blade with two burning hearts let into it, a stone hand clasped either side of its root"""
    s = W.Sword(it["id"])
    L, y0 = 31.0, 4.8
    W.blade_body(s, y0 + 1.2, y0 + L, lambda t: 9.0 * (1 - 0.22 * t) + 0.9 * math.sin(t * 19), 1.6)
    W.tip(s, 0, y0 + L, 7.0, 1.6, n=4, step=1.5)
    for y in (0.3, 0.68):
        c = y0 + L * y
        bx(s, 0, c - 2.2, 0, 4.6, 4.4, 2.1, "dark", tag="socket")
        bx(s, 0, c - 1.7, 0, 3.4, 3.4, 2.5, "glow", glow=True, tag="heart")
        bx(s, 0, c - 0.9, 0, 1.8, 1.8, 2.8, "white", glow=True)
    bx(s, 0, y0 - 0.2, 0, 10.0, 2.6, 2.6, "dark", tag="ricasso")
    for side in (-1, 1):
        for k in range(4):
            bx(s, side * 4.6, y0 + 1.6 + k * 1.5, 0, 2.0, 1.2, 2.8, "blade", tag="finger")
            bx(s, side * 3.2, y0 + 1.6 + k * 1.5, 0, 1.6, 1.2, 2.2, "blade", tag="finger")
        bx(s, side * 5.8, y0 - 0.4, 0, 2.6, 4.0, 3.2, "acc", tag="bracer")
    grip(s, -7.6, 10.0, 2.4)
    return s


def closed_hand(th, it, seed):
    """a tower of old steel with a great stone fist clenched on its face"""
    s = W.Sword(it["id"])
    F = 2.2
    rows = [(y, y + 2, (15.5 if y > -5 else 15.5 * max(0.3, 1 - (-5 - y) / 12))) for y in range(-15, 13, 2)]
    for y0, y1, w in rows:
        bx(s, 0, y0, 1.4, w, y1 - y0 + 0.02, F - 0.4, "blade", tag="plate")
        for side in (1, -1):
            bx(s, side * (w / 2 - 0.6), y0, 1.6, 1.4, y1 - y0 + 0.02, F + 0.4, "acc", tag="rim")
    bx(s, 0, rows[-1][1] - 0.8, 1.6, 15.5, 1.4, F + 0.4, "acc", tag="rim")
    # the fist, thrust out of the face, a seam of fire round its wrist
    bx(s, 0, -5.0, 3.6, 8.6, 10.0, 3.4, "blade", tag="fist")
    for k in range(4):
        bx(s, -3.3 + k * 2.2, 3.6, 3.8, 2.0, 2.2, 3.8, "blade", tag="knuckle")
        bx(s, -3.3 + k * 2.2, -0.8, 5.2, 2.0, 4.6, 1.8, "blade", tag="finger")
    bx(s, 1.0, -3.2, 5.6, 6.0, 2.2, 1.4, "blade", tag="thumb")
    bx(s, 0, -7.0, 3.2, 9.6, 1.8, 3.4, "acc", tag="bracer")
    bx(s, 0, -8.2, 2.8, 10.2, 1.0, 2.4, "glow", glow=True, tag="seam")
    bx(s, 0, -3.0, -5.0, 2.0, 6.0, 1.2, "wrap", tag="handle")
    for y0 in (-3.0, 2.0):
        bx(s, 0, y0, -2.0, 2.0, 1.0, 6.0, "dark", tag="handle_arm")
    return s


def accord(th, it, seed, school):
    """a staff of two wound shafts, stone hands at its head holding what its school calls"""
    s = W.Sword(it["id"])
    top, big = 12.0, 1.25
    wound(s, -18.0, 30, 0.9, 0.42, 1.0)
    bx(s, 0, -4.0, 0, 2.8, 8.0, 2.8, "wrap", tag="grip")
    bx(s, 0, -19.8, 0, 2.8, 2.0, 2.8, "dark", tag="shoe")
    bx(s, 0, top - 1.0, 0, 3.6, 2.2, 3.6, "acc", tag="collar")
    if school == "black":
        oy = top + 4.2 * big
        bx(s, 0, oy - 2.4 * big, 0, 4.8 * big, 4.8 * big, 4.8 * big, "void", tag="orb")
        ring_xy(s, 0, oy, 3.0 * big, 0.5, "glow", glow=True, depth=5.6)
    if school == "white":
        for k, (w, h) in enumerate(((3.6, 3.0), (2.6, 3.0), (1.4, 2.6))):
            bx(s, 0, top + 2.6 + k * 2.6, 0, w, h, w, "white" if k else "glow", glow=True, tag="flame")
    if school == "summon":
        ring_xy(s, 0, top + 7.0, 5.2, 1.3, "acc", depth=1.8)
        for k in range(5):                                 # the chain that binds it, down from the ring
            bx(s, 0, top + 6.8 - k * 1.3, 0, 0.8 if k % 2 else 1.3, 1.1, 1.3 if k % 2 else 0.8, "dark", tag="chain")
        rings(s, 0, top + 8.8, 5.0, 2.0)
        for side in (1, -1):
            W.chainp(s, (side * 1.4, top + 0.8), [(4.0, -side * 28, 1.5, 1.6), (4.6, side * 6, 1.2, 1.4), (3.0, side * 40, 1.0, 1.1)], "blade")
    else:
        for side in (1, -1):
            cup(s, side, 0, top + 1.6, big)
    return s


HAND_BUILT = {"oathbinder": oathbinder, "twinfang": twinfang, "concord": concord, "unison": unison, "two_hearted": two_hearted,
              "the_closed_hand": closed_hand, "black_accord": lambda t, i, q: accord(t, i, q, "black"),
              "white_accord": lambda t, i, q: accord(t, i, q, "white"), "bound_accord": lambda t, i, q: accord(t, i, q, "summon")}
_old_build, _old_bow = W.build, W.bow


def build(th, it):
    if it["id"] not in HAND_BUILT:
        return _old_build(th, it)
    seed = zlib.crc32(it["id"].encode()) & 0xFFFF
    s = HAND_BUILT[it["id"]](th, it, seed)
    s.shaders = th.shaders
    return s, seed, dict(it)


def twin_bow(th, it, seed, boss, pull=0.0, arrow=False, name=None):
    """the bow with a second, burning bow laid along its back, a string for each"""
    s = _old_bow(th, it, seed, boss, pull, arrow, name)
    k = 1.5

    def off(p):
        return (p[0] + W.A[0] * k, p[1] + W.A[1] * k)
    n = 12
    for i in range(n):
        s0, s1 = -0.84 + 1.68 * i / n, -0.84 + 1.68 * (i + 1) / n
        W.seg(s, off(W.bow_at(s0, pull)), off(W.bow_at(s1, pull)), 0.8, 1.0, "acc" if i % 2 else "glow", W.BZ, glow=not i % 2)
    W.seg(s, off(W.bow_at(-0.84, pull)), off(W.bow_at(0.84, pull)), 0.3, 0.3, "glow", W.BZ, glow=True)
    return s


def install():
    W.build, W.bow = build, twin_bow
