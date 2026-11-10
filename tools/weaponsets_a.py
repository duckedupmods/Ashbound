"""Swords, first look: six far apart, to set the bar before the rest."""
import math

from voxsword import ramp, h3, fbm
from weaponsets import (design, qb, path, P, L, disc, ring, rect, Mask, at, lit, facet_of, steel, honed, flat, bone, wrap, heat,
                        fire, gem, stripes)

IRON = ramp("#0a0a0c", "#141416", "#201f22", "#2e2c30", "#403d42", "#585458", "#7a7478", "#a09aa0")
GOLD = ramp("#3a2206", "#5e3a0a", "#8a5a12", "#b47e1c", "#dca62c", "#f6d060", "#fff0b0")
BRASS = ramp("#2a1a08", "#4a3010", "#6e4c1c", "#94702e", "#ba9444", "#dcbc6a")
LEATHER = ramp("#120a06", "#21130b", "#331e12", "#472c1a", "#5e3c24")


@design("brandsteel")
def brandsteel(k):
    """a branding iron with a sword's edge: a black slab ending in a square brand head, the glyph cut through it and
    still white hot, heat crawling down the steel; held in the forge's own tongs, the jaws bowed round the blade"""
    hot = ramp("#120a08", "#2a0e08", "#5a1206", "#9a2206", "#e04a0a", "#ff8a1c", "#ffc84a", "#fff0b0")
    k.mat(blade=steel(ramp("#08080a", "#101012", "#1a191b", "#262427", "#343136", "#484449", "#646066"), base=0.42, ridge=0.1),
          edge=honed(ramp("#141416", "#262528", "#3c3a3e", "#5a5659", "#7e7a7c", "#a8a4a4", "#d0ccc8"), 0.62),
          head=heat(hot, 18, 33), rimhot=heat(hot, 12, 28),
          glyph=fire(ramp("#ff7a1c", "#ffb04a", "#ffe08a", "#fff6d0", "#ffffff"), 0.4, 0.6),
          tong=flat(IRON, 0.5), rivet=flat(BRASS, 0.6), wrap=wrap(LEATHER, IRON[1]))
    body = P((-3.2, 3), (3.2, 3), (2.6, 21), (1.6, 23.2), (5.2, 23.6), (5.6, 31.4), (-5.6, 31.4), (-5.2, 23.6), (-1.6, 23.2), (-2.6, 21))
    bite = P((5.8, 27.5), (4.6, 27), (5.8, 26)) + P((-5.8, 29), (-4.8, 28.4), (-5.8, 27.6))
    body = body - bite
    glyph = rect(-3.2, 29, 3.2, 29.9) + rect(-0.8, 25, 0.8, 29.5) + rect(-3, 25, 3, 25.9) + P((-3.2, 27.4), (-2, 26), (-2, 28.2)) + P((3.2, 27.4), (2, 26), (2, 28.2))
    cold = body & rect(-9, 0, 9, 16)
    warm = body & rect(-9, 16, 9, 33)
    k.plate(cold, 1.0, "edge", tag="edge")
    k.plate(warm, 1.0, "rimhot", glow=True, tag="edge")
    k.plate(cold.inset(0.5), 2.2, "blade", tag="blade")
    k.plate((warm.inset(0.5) - glyph), 2.2, "head", glow=True, tag="blade")
    k.plate(glyph, 1.4, "glyph", glow=True)
    k.inlay(L([(0.4, 16), (-0.5, 12.5), (0.5, 9.5), (0, 6.5)], 0.5) + L([(-0.5, 12.5), (-1.7, 10.5)], 0.5), 2.2, "glyph", glow=True)
    # the tongs: two jaws bowed out round the blade, the reins running down as the grip
    for s_ in (1, -1):
        jaw = P(path(qb((s_ * 1.2, 1.2), (s_ * 8.4, 2.4), (s_ * 3.4, 8.4)), (s_ * 2.4, 8.6), qb((s_ * 3.0, 7.4), (s_ * 5.6, 3.2), (s_ * 1.0, 3.0)), (s_ * 0.8, 1.2)))
        k.plate(jaw, 3.0, "tong")
        k.box(s_ * 3.0, 7.0, 0, 1.0, 1.0, 3.3, "rivet")
    k.box(0, 0.8, 0, 3.4, 1.5, 3.4, "rivet")
    k.grip(-5.2, 1.0, 2.2)
    k.plate(ring(0, -6.8, 2.1, 1.0), 2.2, "tong")


@design("lees_sabre")
def lees_sabre(k):
    """a cellarmaster's sabre, the steel drowned in wine: dregs climb the blade in a ragged tide. Its knuckle bow is a
    barrel hoop, a brass spigot sits on the guard and the pommel is a cork"""
    wine = ramp("#16040e", "#2a0818", "#460e26", "#661436", "#882048", "#b03a60")
    metal = ramp("#1a2422", "#2a3836", "#3e504c", "#566c66", "#728a82", "#94aaa0", "#bcccc2", "#e0ebe2")
    plain = steel(metal, base=0.52, ridge=0.13, scars=0.03)

    def blade(p, n, b, key, i, j, w, h, fr):
        x, y, z = p
        tide = 12.5 + 5.5 * fbm(x * 0.6, 1.5, z * 0.3) + 1.6 * math.sin(x * 2.3)
        if y < tide:
            return at(wine, 0.3 + (y / tide) * 0.45 + (0.14 if facet_of(p, b) < -0.3 else -0.08) + lit(key, i, j, w, h) * 0.5)
        return plain(p, n, b, key, i, j, w, h, fr)

    def rim(p, n, b, key, i, j, w, h, fr):
        return at(wine, 0.9 + lit(key, i, j, w, h)) if p[1] < 8 else at(metal, 0.84 + lit(key, i, j, w, h))

    k.mat(blade=blade, edge=rim, hoop=flat(ramp("#120c08", "#22160e", "#3a2414", "#5a361c", "#7c4a24", "#a0622e"), 0.5),
          brass=flat(BRASS, 0.6), cork=flat(ramp("#6a4a2a", "#8a6840", "#a88658", "#c8a878", "#e0c49a"), 0.55, 0.3),
          wrap=wrap(ramp("#1a060e", "#2e0c18", "#461426", "#5e1e34"), BRASS[2]))
    # the blade: straight off the guard, then sweeping forward to a clipped point
    blade_m = P(path(qb((-2.1, 3), (-2.6, 17), (7.4, 28.5)), (7.9, 25.6), qb((8.2, 24.4), (5.4, 11), (3.2, 3))))
    k.forge(blade_m, 1.9, ridge=-0.45)
    k.box(0.6, 2.2, 0, 7.4, 1.5, 3.2, "hoop")
    k.box(0.6, 2.0, 0, 8.6, 0.5, 3.6, "brass")
    # the hoop: a D of iron from the guard to the cork, riveted
    bow_ = P(path(qb((4.0, 3.2), (8.8, 0), (1.6, -5.4)), (0.8, -4.6), qb((1.4, -4.6), (6.8, -0.6), (3.0, 2.2))))
    k.plate(bow_, 1.6, "hoop")
    for x, y in ((4.8, 0.4), (3.2, -3.2)):
        k.box(x, y, 0, 0.9, 0.9, 1.9, "brass")
    # the spigot, its tap handle turned
    k.box(-3.8, 2.3, 0, 2.2, 1.3, 1.5, "brass")
    k.box(-4.6, 1.2, 0, 1.0, 1.2, 1.0, "brass")
    k.box(-4.4, 3.5, 0, 0.8, 1.0, 0.8, "brass")
    k.box(-4.4, 4.3, 0, 2.6, 0.7, 0.8, "brass")
    k.grip(-4.6, 2.2, 2.0)
    k.box(0, -7.2, 0, 2.6, 2.7, 2.6, "cork")
    k.box(0, -5.2, 0, 3.0, 0.7, 3.0, "brass")


@design("rib")
def rib(k):
    """one rib of the fallen titan, sawn off and sharpened: a great curve of bone knapped along its inner edge, its
    joint knuckle still on for a pommel, raw tendon lashed round the grip"""
    ivory = ramp("#3a2e22", "#5a4a38", "#7e6c54", "#a29074", "#c2b294", "#dccdb0", "#efe4cc", "#fbf6e6")
    meat = ramp("#2a0608", "#4a0c10", "#6e161a", "#942428", "#b83c3a", "#d8625a")
    k.mat(blade=bone(ivory), edge=flat(ivory, 0.82, bevel=0.06), wrap=wrap(meat, meat[0], 5), meat=flat(meat, 0.45, 0.3),
          marrow=flat(ramp("#3a1412", "#5e2018", "#8a3a24", "#b05e34"), 0.5, 0.4))
    outer = qb((-1.8, 2.6), (-11.5, 17), (4.6, 33.0), 12)
    inner = qb((5.0, 31.0), (-3.0, 17.5), (2.4, 2.6), 12)
    m = P(path(outer, (5.0, 31.0), inner, (2.4, 2.6)))
    # knapped: flakes taken out of the inner edge
    for t, sz in ((0.2, 1.1), (0.34, 1.3), (0.5, 1.0), (0.63, 1.3), (0.78, 1.0)):
        a = int(t * len(inner))
        q = inner[a]
        m = m - P((q[0] + 1.2, q[1] - sz), (q[0] - 0.7, q[1]), (q[0] + 1.2, q[1] + sz))
    k.forge(m, 3.0, step=1, ridge=-0.15)
    # the marrow channel where it was sawn: a dark split along the bone
    k.inlay(L(qb((-1.4, 7), (-5.4, 15), (-2.0, 25), 8), 0.7), 3.0, "marrow")
    k.plate(L(qb((-0.4, 6), (-4.2, 15), (-1.0, 23), 8), 0.5), 3.06, "edge")
    # tendon torn and hanging off the root
    k.box(0.2, 2.0, 0, 6.0, 1.6, 3.8, "meat")
    k.plate(P((-2.8, 2.4), (-3.6, -1.4), (-2.6, -0.2), (-2.0, 2.4)), 1.4, "meat")
    k.plate(P((3.0, 2.4), (4.4, -2.6), (3.2, -1.4), (2.0, 2.4)), 1.4, "meat")
    k.grip(-4.8, 2.0, 2.3)
    # the joint knuckle
    k.plate(disc(0, -6.6, 2.7) + disc(-1.4, -8.0, 1.5), 3.4, "edge")
    k.plate(disc(-0.3, -6.9, 1.5), 3.5, "blade")


@design("showstopper")
def showstopper(k):
    """the Ringmaster's closing act: a flame-waved blade painted in circus stripes, thrust through a burning hoop that
    is its guard; the pommel is a jester's cap, two bells hanging"""
    red = ramp("#2a0408", "#4e0810", "#7a1018", "#a81c20", "#d0302a", "#ee5a44")
    cream = ramp("#6a5a44", "#8e7c60", "#b4a282", "#d6c8a8", "#efe4c8", "#fff8e8")
    flame = ramp("#a02206", "#e04a0a", "#ff8a1c", "#ffc84a", "#fff0b0")
    k.mat(blade=stripes(red, cream, 3.6, 0.9), edge=honed(GOLD, 0.7), gold=flat(GOLD, 0.62), hoop=flat(GOLD, 0.5),
          flame=fire(flame, 0.1, 0.9), cloth=stripes(red, ramp("#0e1a3a", "#182a54", "#22386c", "#304a86", "#4a66a8"), 2.4, 0.0),
          wrap=wrap(ramp("#0e1a3a", "#182a54", "#22386c", "#304a86"), GOLD[4], 4))
    left, right = [], []
    n = 24
    for j in range(n + 1):
        t = j / n
        y = 3 + t * 30.5
        wob = 1.25 * math.sin(t * 15) * (1 - t * 0.3)
        hw = 3.0 * (1 - t ** 3) + 0.05
        left.append((wob - hw, y))
        right.append((wob + hw, y))
    k.forge(P(path(left, right[::-1])), 1.8, ridge=0.0)
    cy = 7.0
    k.plate(ring(0, cy, 6.6, 5.4), 1.9, "hoop")
    for j in range(12):
        a = math.radians(j * 30 + 15)
        ox, oy = math.cos(a), math.sin(a)
        tx, ty = -oy, ox
        lean = 0.9 + (j % 3) * 0.7
        base = (ox * 6.3, cy + oy * 6.3)
        tip = (ox * (7.4 + lean) + 0.5 * ox, cy + oy * (7.4 + lean) + 1.3)
        k.plate(P((base[0] + tx * 1.3, base[1] + ty * 1.3), tip, (base[0] - tx * 1.3, base[1] - ty * 1.3)), 1.3, "flame", glow=True)
    for s_ in (1, -1):   # spokes carrying the hoop
        k.plate(L([(0, 1.6), (s_ * 4.4, 2.8)], 1.3), 2.2, "gold")
    k.box(0, 1.2, 0, 4.4, 1.8, 2.8, "gold")
    k.grip(-4.4, 1.3, 2.0)
    for s_, m in ((1, "cloth"), (-1, "cloth")):
        k.plate(P(path(qb((-s_ * 0.2, -4.4), (s_ * 1.0, -9.4), (s_ * 5.2, -7.0)), (s_ * 4.8, -8.4), qb((s_ * 4.0, -9.0), (s_ * 0.0, -11.0), (-s_ * 1.2, -4.4)))), 2.0, m)
        k.plate(disc(s_ * 5.2, -8.6, 1.1), 2.2, "gold")
    k.box(0, -5.2, 0, 3.0, 0.9, 3.0, "gold")


@design("thousand_hand_jian")
def thousand_hand_jian(k):
    """a straight jade jian with arms growing out of it: gold hands reach up off both edges, thinning toward the tip,
    as if the whole monastery were still holding the blade. A lotus for a guard, a long red tassel"""
    jade = ramp("#04261c", "#083a2a", "#0e523c", "#167050", "#229068", "#3ab484", "#74d8ac", "#c0f4dc")
    tassel = ramp("#3a0608", "#600c0e", "#8a1416", "#b42020", "#dc3a30")
    k.mat(blade=steel(jade, base=0.5, ridge=0.16, sheen=0.14), edge=honed(jade, 0.84), gold=flat(GOLD, 0.66, bevel=0.14),
          lotus=flat(jade, 0.62, bevel=0.14), wrap=wrap(tassel, GOLD[3], 5), tassel=flat(tassel, 0.55, 0.25), gem=gem(GOLD))
    blade_m = P((-2.2, 3), (2.2, 3), (1.7, 28), (0, 33.0), (-1.7, 28))
    k.forge(blade_m, 1.7, ridge=0.0)
    arms = Mask()
    for j, y in enumerate((6.0, 11.0, 15.6, 19.8, 23.6)):
        for s_ in (1, -1):
            yy = y + (0.9 if s_ < 0 else 0)
            sc = 1.2 - j * 0.12
            e = 2.0 - j * 0.03
            elbow = (s_ * (e + 2.6 * sc), yy + 0.6 * sc)
            palm = (s_ * (e + 3.6 * sc), yy + 3.0 * sc)
            arms = arms + L([(s_ * (e - 0.4), yy), elbow, palm], 1.0)
            arms = arms + disc(palm[0], palm[1] + 0.2, 0.85 * sc + 0.1, 10)
            for f in (-0.9, 0.0, 0.9):
                arms = arms + L([(palm[0] + f * 0.7 * sc, palm[1] + 0.3), (palm[0] + f * 1.6 * sc, palm[1] + 2.4 * sc)], 0.5)
            arms = arms + L([(palm[0] - s_ * 0.6, palm[1] - 0.2), (palm[0] - s_ * 1.8 * sc, palm[1] + 0.5 * sc)], 0.5)
    k.plate(arms, 1.2, "gold")
    # the lotus
    for a, ln, w in ((0, 5.0, 2.4), (32, 5.4, 2.1), (-32, 5.4, 2.1), (62, 5.4, 1.8), (-62, 5.4, 1.8)):
        r = math.radians(a)
        d, t = (-math.sin(r), math.cos(r)), (math.cos(r), math.sin(r))
        k.plate(P((t[0] * w * 0.5, 1.2 + t[1] * w * 0.5), (d[0] * ln * 0.55 + t[0] * w, 1.2 + d[1] * ln * 0.55 + t[1] * w),
                  (d[0] * ln, 1.2 + d[1] * ln), (d[0] * ln * 0.55 - t[0] * w, 1.2 + d[1] * ln * 0.55 - t[1] * w),
                  (-t[0] * w * 0.5, 1.2 - t[1] * w * 0.5)), 2.4 - abs(a) * 0.01, "lotus")
    k.box(0, 0.4, 0, 5.0, 1.2, 3.0, "gold")
    k.grip(-5.0, 0.8, 1.9)
    k.box(0, -6.0, 0, 2.6, 1.2, 2.6, "gold")
    k.box(0, -6.8, 0, 1.4, 1.0, 1.4, "gem")
    # the tassel: a cord, a knot, long strands
    k.box(0, -9.0, 0, 0.6, 2.4, 0.6, "tassel")
    k.box(0, -10.2, 0, 1.8, 1.4, 1.8, "gold")
    k.plate(P((-1.1, -10.2), (1.1, -10.2), (1.8, -18.0), (0.8, -16.6), (0.3, -18.8), (-0.5, -16.8), (-1.6, -18.2)), 1.4, "tassel")


@design("ignavars_claw")
def ignavars_claw(k):
    """the dragon's own talon: one great hooked claw, black at the root and burning at its inner edge, sunk in a
    gold-scaled cuff; two lesser talons hook down as the guard and a ruby sits where the toe met the foot"""
    horn = ramp("#080406", "#120809", "#1e0c0c", "#301210", "#481a12", "#642414", "#8a3216")
    ember = ramp("#7a1406", "#c0300a", "#ff6a14", "#ffb040", "#ffe8a0", "#fffbe0")
    ruby = ramp("#3a0610", "#7a0c1e", "#c01a30", "#ff3b52", "#ffb0b8")

    def claw(p, n, b, key, i, j, w, h, fr):
        ringy = 0.09 * math.sin(p[1] * 1.5 + p[0] * 0.8)
        return at(horn, 0.52 + p[1] * 0.012 + lit(key, i, j, w, h) + (0.14 if facet_of(p, b) < -0.2 else -0.08) + ringy)

    k.mat(blade=claw, edge=fire(ember, 0.3, 0.5), gold=flat(GOLD, 0.6), scale=flat(GOLD, 0.44, bevel=0.2), gem=gem(ruby),
          dark=flat(horn, 0.6, bevel=0.14), wrap=wrap(ramp("#1a0606", "#2e0c0a", "#461410", "#5e1e16"), GOLD[3], 5))
    back = qb((-3.8, 4), (-5.0, 22), (9.8, 32.0), 14)
    belly = qb((10.2, 27.6), (5.2, 18.4), (3.8, 4), 14)
    tip = qb((9.8, 32.0), (14.2, 32.4), (14.4, 25.0), 6)
    m = P(path(back, tip, (14.4, 25.0), qb((13.2, 27.8), (11.6, 28.4), (10.2, 27.6), 4), belly, (3.8, 4)))
    k.plate(m, 1.0, "edge", glow=True, tag="edge")
    body = P(path(back, tip, (14.0, 25.8), qb((12.6, 28.4), (10.4, 29.0), (9.2, 27.6), 4), qb((9.2, 27.6), (3.8, 18.4), (2.8, 4), 14), (2.8, 4)))
    k.plate(m & body, 3.0, "blade", ridge=-0.2, tag="blade")
    # the scale cuff, overlapping rows round the root
    for r_, y in enumerate((3.0, 5.0, 7.0)):
        w = 9.4 - r_ * 1.2
        n = 4 - r_ % 2
        for j in range(n):
            x = (j - (n - 1) / 2) * w / n
            k.plate(P((x - w / n / 2 - 0.1, y + 2.2), (x + w / n / 2 + 0.1, y + 2.2), (x + w / n / 2 + 0.1, y + 0.8), (x, y - 0.6), (x - w / n / 2 - 0.1, y + 0.8)), 3.8 - r_ * 0.2, "scale")
    k.box(0, 1.6, 0, 9.0, 1.7, 3.8, "gold")
    # the lesser talons
    for s_ in (1, -1):
        k.plate(P(path(qb((s_ * 3.4, 3.0), (s_ * 9.4, 3.0), (s_ * 8.6, -4.0), 8), qb((s_ * 8.6, -4.0), (s_ * 7.6, 0.8), (s_ * 3.0, 1.2), 8))), 2.2, "dark")
    k.plate(disc(0, 2.4, 1.8, 10), 4.4, "gem")
    k.grip(-4.8, 1.8, 2.1)
    k.box(0, -7.0, 0, 3.2, 2.4, 3.2, "gold")
    k.plate(P(path(qb((-1.6, -7.0), (-1.4, -10.0), (0.4, -11.0), 6), qb((0.4, -11.0), (1.8, -9.4), (1.6, -7.0), 6))), 2.6, "dark")
