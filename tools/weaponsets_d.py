"""Swords: the Fallen Titan, the Jade Monastery, the Storm Bastion, the Bloodmoon Court, the Obsidian Labyrinth, the Abyssal
Lighthouse, the Eclipse Cathedral, the Wyrm's Hoard; the world's finds; Oathbinder."""
import math

from voxsword import ramp
from weaponsets import design, qb, path, P, L, disc, ring, rect, wave, taper, Mask, flat, fire, staves, steel, honed, bone, gem, at, lit, wrap, facet_of
from weaponsets_a import BRASS, GOLD, IRON, LEATHER
from weaponsets_c import shard

RUBY = ramp("#3a0610", "#7a0c1e", "#c01a30", "#ff3b52", "#ffb0b8")
SILVER = ramp("#4a5058", "#6a727c", "#8e98a2", "#b4bec8", "#d8e0e8", "#f4f8fc")


def stroke(a, c, b, w, n=10):
    return L(qb(a, c, b, n) + [b], w)


def links(k, pts, mat, size=1.3):
    """a chain along pts, the links turning alternately edge-on"""
    for j, (a, b) in enumerate(zip(pts, pts[1:])):
        cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        ang = math.degrees(math.atan2(-(b[0] - a[0]), b[1] - a[1]))
        ln = math.hypot(b[0] - a[0], b[1] - a[1]) + 0.5
        k.box(cx, cy - ln / 2, 0, size if j % 2 else 0.5, ln, 0.5 if j % 2 else size, mat, rots=(("z", ang),), pivot=(cx, cy, 0))


def feathers(s_, y0, n, ln, sweep, w, droop=False):
    """a wing off the guard: n long feathers fanned from the root, s_ the side"""
    m = Mask()
    for j in range(n):
        a = math.radians(sweep * j / max(1, n - 1) + 8)
        d = (s_ * math.sin(a), -math.cos(a) if droop else math.cos(a))
        l_ = ln * (1 - 0.13 * j)
        o = (s_ * 1.4, y0)
        side = (-d[1], d[0])
        m = m + P(o, (o[0] + d[0] * l_ * 0.6 + side[0] * w, o[1] + d[1] * l_ * 0.6 + side[1] * w), (o[0] + d[0] * l_, o[1] + d[1] * l_),
                  (o[0] + d[0] * l_ * 0.6 - side[0] * w, o[1] + d[1] * l_ * 0.6 - side[1] * w))
    return m


@design("aorta")
def aorta(k):
    """the Titan's great artery, torn out and hardened: it rises from the hilt, arches over like the real thing with three
    cut vessels standing off the top, and comes down to a calcified spike that does the killing"""
    meat = ramp("#2a0608", "#4a0c10", "#6e161a", "#942428", "#b83c3a", "#d8625a", "#f09a8a")
    fat = ramp("#6a4a20", "#a07c34", "#d0ae56", "#ecd488", "#faeec4")
    ivory = ramp("#5a4a38", "#7e6c54", "#a29074", "#c2b294", "#dccdb0", "#efe4cc", "#fbf6e6")

    def tube(p, n, b, key, i, j, w, h, fr):
        return at(meat, 0.5 + lit(key, i, j, w, h) + 0.22 * (1 - abs(facet_of(p, b)) * 1.4) + 0.06 * math.sin(p[1] * 1.6 + p[0]))

    k.mat(blade=tube, edge=flat(meat, 0.2, bevel=0.04), bone=bone(ivory, 0.7), fat=flat(fat, 0.6, 0.3), hot=fire(ramp("#a01018", "#e02830", "#ff6a5a", "#ffc0a8"), 0.3, 0.6),
          wrap=wrap(meat, meat[0], 4), gut=flat(meat, 0.42))
    spine = qb((0, 3), (-3.4, 34), (12.6, 22.6), 18) + [(12.6, 22.6)]
    m = Mask()
    for j, q in enumerate(spine):
        m = m + disc(q[0], q[1], 3.0 - j * 0.07, 12)
    for a, c, b, w in (((-0.4, 22), (-3.6, 28), (-6.6, 33.4), 2.0), ((2.6, 26), (2.4, 32), (0.6, 36.6), 1.8), ((6.4, 28), (8.4, 32), (8.2, 35.6), 1.6)):
        m = m + stroke(a, c, b, w)
        k.plate(disc(b[0], b[1], w * 0.74, 10), 2.6, "gut")
        k.plate(disc(b[0], b[1], w * 0.4, 8), 2.7, "edge")
    k.plate(m, 1.6, "edge", tag="edge")
    k.plate(m.inset(0.5), 3.0, "blade", tag="blade")
    k.inlay(L(qb((-1.4, 6), (-3.0, 19), (-1.0, 23), 8) + [(-1.0, 23)], 0.8), 3.0, "hot", glow=True)
    k.inlay(L(qb((1.2, 8), (0.8, 17), (5.0, 25), 8) + [(5.0, 25)], 0.7), 3.0, "fat")
    k.plate(P(path(qb((10.6, 22), (12.8, 19), (13.6, 8.6), 10), (13.6, 8.6), qb((15.4, 14), (15.4, 20), (14.8, 23.6), 8))), 2.2, "bone")
    for j, y in enumerate((5.0, 12.0)):
        k.box(-0.6 - j, y, 0, 6.6, 1.0, 3.6, "fat")
    k.box(0, 1.8, 0, 7.0, 1.6, 3.8, "bone")
    k.grip(-4.8, 1.8, 2.3)
    k.plate(disc(0, -6.8, 2.4, 12), 3.0, "gut")
    k.plate(disc(0, -6.8, 1.2, 10), 3.1, "hot", glow=True)


@design("jade_jian")
def jade_jian(k):
    """the monk's plain jian: a straight slip of green stone with a gold line, a guard like a cloud, two rings loose on the
    pommel so it sings when it moves"""
    R = k.theme("jade_monastery", base=0.52)
    k.mat(gold=flat(GOLD, 0.64), cloud=flat(GOLD, 0.56, bevel=0.14), rope=flat(ramp("#3a0608", "#600c0e", "#8a1416", "#b42020", "#dc3a30"), 0.6, 0.3))
    k.forge(P((-1.9, 3), (1.9, 3), (1.5, 29.4), (0, 33.6), (-1.5, 29.4)), 1.4)
    k.inlay(L([(0, 4), (0, 30)], 0.5), 1.4, "gold")
    cloud = disc(0, 2.4, 2.6, 12) + disc(-3.2, 2.0, 1.9, 10) + disc(3.2, 2.0, 1.9, 10) + disc(-5.6, 2.8, 1.2, 8) + disc(5.6, 2.8, 1.2, 8)
    k.plate(cloud, 2.6, "cloud")
    k.grip(-5.0, 1.0, 1.8)
    k.box(0, -5.8, 0, 2.4, 1.0, 2.4, "gold")
    k.plate(ring(-1.2, -8.2, 1.7, 0.9) + ring(1.0, -8.8, 1.7, 0.9), 0.8, "gold")
    k.plate(P((-0.7, -10), (0.7, -10), (1.1, -14.4), (0, -13.4), (-1.1, -14.4)), 1.0, "rope")


@design("gale_sabre")
def gale_sabre(k):
    """a sabre shaped by wind: three gusts have curled off its back like the tops of waves, slots pierced along it so it
    moans when swung; a little storm vane for a guard"""
    R = k.theme("storm_bastion", base=0.5)
    k.mat(vane=flat(BRASS, 0.62), white=flat(R["glow"], 0.86))
    back = qb((-1.8, 3), (-3.0, 18), (6.0, 31.0), 14)
    m = P(path(back, (6.0, 31.0), qb((6.6, 27.4), (4.8, 13), (2.6, 3), 12)))
    for j, (t, ln) in enumerate(((0.3, 5.2), (0.52, 4.6), (0.74, 3.8))):
        q = back[int(t * 14)]
        m = m + stroke((q[0] + 0.8, q[1] + 0.2), (q[0] - ln * 0.9, q[1] - 0.2), (q[0] - ln * 0.7, q[1] + ln * 0.8), 1.1, 8)
        m = m - disc(q[0] - ln * 0.28, q[1] + 1.3, 0.5, 6)
    slots = L(qb((0.4, 8), (0.2, 16), (2.8, 22), 8), 0.6) - rect(-5, 12, 9, 13) - rect(-5, 17, 9, 18)
    k.forge(m - slots, 1.5, step=1, ridge=-0.3)
    k.plate(slots, 0.5, "glow", glow=True)
    k.box(0.4, 1.8, 0, 6.8, 1.3, 2.6, "vane")
    k.plate(P((3.6, 2.6), (8.0, 4.4), (6.2, 1.0), (8.0, -1.0), (3.6, 1.4)), 1.0, "vane")
    k.plate(P((-2.8, 2.8), (-6.0, 3.6), (-6.0, 1.0), (-2.8, 1.8)), 1.0, "vane")
    k.grip(-4.8, 1.9, 2.0)
    k.plate(disc(0, -6.4, 1.8, 10), 2.4, "vane")


@design("abbesss_verdict")
def abbesss_verdict(k):
    """judgement caught in iron: the blade is a thunderbolt, hard zigzags to a point, white fire down its core. The guard
    is a lightning rod's cross and the grip a copper coil still ticking with charge"""
    R = k.theme("storm_bastion", base=0.46)
    k.mat(copper=wrap(ramp("#3a1a08", "#6a3414", "#9c5a24", "#c8843c"), None, 2), white=flat(R["glow"], 0.92, bevel=0.02), rod=flat(R["dark"], 0.62), edge=fire(R["glow"], 0.3, 0.7))
    m = P((-2.2, 3), (3.2, 3), (1.8, 11.4), (6.2, 11.0), (0.8, 21.2), (4.2, 20.6), (-2.2, 37.0), (-0.4, 25.0), (-4.4, 25.6), (-0.8, 15.0), (-4.2, 15.4))
    k.plate(m, 1.2, "edge", glow=True, tag="edge")
    k.plate(m.inset(0.5), 2.2, "blade", tag="blade")
    k.plate(L([(0.2, 4), (-1.6, 14), (2.6, 12.8), (-1.6, 24), (1.6, 22.6), (-1.4, 33)], 0.8), 2.26, "white", glow=True)
    k.plate(rect(-8.0, 1.6, 8.0, 3.0), 2.6, "rod")
    for s_ in (1, -1):
        k.plate(P((s_ * 7.2, 3), (s_ * 8.8, 3), (s_ * 8.0, 8.2)), 1.4, "rod")
        k.plate(disc(s_ * 8.0, 2.3, 1.3, 8), 2.8, "rod")
        k.plate(L([(s_ * 8.0, 8.2), (s_ * 9.4, 10), (s_ * 8.4, 10.8), (s_ * 9.8, 12.8)], 0.5), 0.6, "white", glow=True)
    k.grip(-5.0, 1.7, 2.3, "copper")
    k.plate(P((-2.2, -5), (2.2, -5), (1.0, -7), (0, -10.4), (-1.0, -7)), 2.6, "rod")


@design("court_rapier")
def court_rapier(k):
    """a duellist's blade for the Countess's table: thin as manners, a crescent moon cupped under the blade, two swept
    rings of blackened silver and a ruby at the pommel"""
    R = k.theme("bloodmoon_court", base=0.54)
    k.mat(moon=flat(ramp("#7a3a2a", "#a85a3a", "#d0844a", "#eeb070", "#ffdca0"), 0.7, bevel=0.1), silver=flat(IRON, 0.7), gem=gem(RUBY))
    k.forge(taper(1.2, 0.8, 3, 33, 37.0), 1.3)
    crescent = disc(0, 7.2, 5.4) - disc(0, 8.8, 5.0)
    k.plate(crescent, 1.6, "moon")
    k.box(0, 1.6, 0, 3.6, 1.2, 2.6, "silver")
    for s_ in (1, -1):
        k.plate(stroke((s_ * 0.8, 1.4), (s_ * 5.2, 0.6), (s_ * 2.2, -3.6), 0.8) + stroke((s_ * 0.8, 1.8), (s_ * 7.0, 1.4), (s_ * 4.2, -1.4), 0.7), 1.0, "silver")
    k.grip(-4.8, 1.7, 1.8)
    k.plate(disc(0, -6.2, 1.7, 10), 2.4, "silver")
    k.plate(disc(0, -6.2, 0.9, 8), 2.6, "gem")


@design("countesss_rapier")
def countesss_rapier(k):
    """the Countess at her table: two bat's wings spread from the guard, blood running up a channel in the blade instead of
    down, a rose on the pommel that has never needed watering"""
    R = k.theme("bloodmoon_court", base=0.42)
    wing = ramp("#0e060a", "#1a0a10", "#2a1018", "#3e1822", "#54202e")
    k.mat(wing=flat(wing, 0.56, bevel=0.08), bone=flat(ramp("#2a1a1a", "#4a3030", "#6e4a48", "#967068"), 0.6), silver=flat(IRON, 0.7), gem=gem(RUBY), hot=fire(RUBY, 0.3, 0.6),
          rose=flat(RUBY, 0.56, bevel=0.2), edge=honed(ramp("#2a0a10", "#5a1420", "#9a2030", "#e04a50", "#ffb0a8"), 0.7))
    k.forge(taper(1.5, 1.0, 3, 33, 38.0), 1.5)
    k.inlay(L([(0, 4), (0, 34)], 0.6), 1.5, "hot", glow=True)
    for s_ in (1, -1):
        w = P(path((s_ * 1.0, 3), (s_ * 2.8, 8), qb((s_ * 4.6, 10.6), (s_ * 8.6, 13.4), (s_ * 12.4, 12.0), 8), (s_ * 12.4, 12.0), qb((s_ * 12.0, 8.2), (s_ * 10.2, 7.0), (s_ * 9.2, 5.6), 5),
                   qb((s_ * 8.4, 7.0), (s_ * 7.0, 5.6), (s_ * 6.2, 3.6), 5), qb((s_ * 5.4, 5.0), (s_ * 4.2, 3.8), (s_ * 3.6, 2.0), 5), (s_ * 1.0, 1.6)))
        k.plate(w, 0.8, "wing")
        k.plate(stroke((s_ * 1.2, 2.6), (s_ * 4.4, 8.6), (s_ * 12.4, 12.0), 0.7) + L([(s_ * 2.0, 4.8), (s_ * 9.2, 5.6)], 0.5) + L([(s_ * 1.6, 3.2), (s_ * 6.2, 3.6)], 0.5), 1.3, "bone")
    k.plate(disc(0, 2.6, 2.0, 10), 3.0, "silver")
    k.plate(disc(0, 2.6, 1.1, 8), 3.3, "gem")
    k.grip(-4.8, 1.0, 1.8)
    k.plate(disc(0, -6.6, 2.4, 10), 2.6, "rose")
    k.plate(disc(-0.5, -6.3, 1.4, 8), 2.8, "hot", glow=True)
    k.plate(disc(0.2, -6.6, 0.7, 8), 3.0, "rose")


@design("obsidian_blade")
def obsidian_blade(k):
    """no steel in the Labyrinth: a flat paddle of black wood with knapped volcanic glass set in both edges, shard by shard,
    each one a different length, the glass running purple where it's thin"""
    R = k.theme("obsidian_labyrinth", base=0.46)
    glass = ramp("#050408", "#100c18", "#1e1630", "#32244e", "#50387a", "#7c58b0", "#c0a0f0")
    k.mat(wood=staves(ramp("#1a120c", "#2c1e12", "#42301c", "#5a4228", "#745836"), 1.6, 0.6), glass=flat(glass, 0.62, bevel=0.3), lash=flat(R["glow"], 0.5))
    k.plate(P((-2.8, 3), (2.8, 3), (2.6, 27.5), (0, 30), (-2.6, 27.5)), 2.2, "wood")
    for s_ in (1, -1):
        y = 4.6 + (0.9 if s_ < 0 else 0)
        j = 0
        while y < 26:
            ln = (3.4, 2.4, 3.0)[j % 3]
            k.plate(P((s_ * 2.0, y), (s_ * 2.0, y + 2.3), (s_ * (2.7 + ln), y + 1.7), (s_ * (2.6 + ln * 0.7), y + 0.5)), 1.0, "glass")
            y += 2.6
            j += 1
    k.plate(shard(0, 26.4, 7.4, 0, 2.6), 1.4, "glass")
    k.inlay(L([(0, 6), (0, 25)], 0.6), 2.2, "dark")
    for y in (5.0, 15.0, 25.0):
        k.box(0, y, 0, 5.8, 0.6, 2.4, "dark")
    k.box(0, 1.6, 0, 6.4, 1.4, 3.0, "dark")
    k.grip(-4.8, 1.7, 2.2)
    k.plate(shard(0, -4.6, 4.8, 180, 2.4), 2.0, "glass")


@design("thread_of_the_maze")
def thread_of_the_maze(k):
    """a slab of black stone cut through with the Labyrinth's own plan, so the light comes through it in corridors; a gold
    thread runs in at the guard and finds its way out at the point, and the pommel is what's left of the ball"""
    R = k.theme("obsidian_labyrinth", base=0.44, ridge=0.06)
    k.mat(gold=flat(GOLD, 0.74, bevel=0.04), ball=wrap(GOLD, GOLD[1], 2), thread=fire(GOLD, 0.6, 0.4))
    m = P((-4.2, 3), (4.2, 3), (4.2, 27), (0, 33.8), (-4.2, 27))
    holes = Mask()
    for (x0, y0, x1, y1) in ((-3, 5, 3, 5.7), (-3, 5, -2.3, 25), (2.3, 7.2, 3, 26), (-3, 25, 1, 25.7), (-1.6, 7.2, 3, 7.9), (-1.6, 7.2, -0.9, 23.4), (0.8, 9.4, 1.5, 23.8),
                           (-1.6, 23.4, 0.2, 24.1), (-0.1, 9.4, 1.5, 10.1)):
        holes = holes + rect(x0, y0, x1, y1)
    k.plate(m - holes, 1.2, "edge", tag="edge")
    k.plate((m - holes).inset(0.5), 2.4, "blade", tag="blade")
    k.plate(holes & m, 0.4, "thread", glow=True)
    k.plate(L([(0, 3), (-2.7, 5.4), (-2.7, 25.4), (0.8, 25.4), (2.7, 26.6), (0, 31.6)], 0.4), 2.5, "gold")
    k.plate(P((-6.4, 1.6), (6.4, 1.6), (6.4, 3.2), (-6.4, 3.2)), 3.0, "dark")
    k.grip(-4.8, 1.7, 2.1)
    k.plate(L([(0.6, -4.6), (2.2, -2.6), (3.4, 1.6)], 0.4), 0.5, "gold")
    k.plate(disc(0, -7.2, 2.7, 12), 3.2, "ball")


@design("lightkeeper_sword")
def lightkeeper_sword(k):
    """the keeper's own sword is the tower itself: a tapering blade banded white and rust red, a railed gallery near the top,
    the lamp room burning above it and the roof drawn out into the point. Its foot stands on black rock"""
    R = k.theme("abyssal_lighthouse", base=0.5)
    white = ramp("#7a7a70", "#a4a498", "#c8c8bc", "#e4e4d8", "#f8f8ee")
    red = ramp("#2a0806", "#4a100a", "#722014", "#9a3422", "#c04e36")

    def tower(p, n, b, key, i, j, w, h, fr):
        band = int((p[1] - 4) // 4.4) % 2
        return at(red if band else white, 0.54 + lit(key, i, j, w, h) + (0.14 if facet_of(p, b) < 0 else -0.1))

    k.mat(blade=tower, edge=flat(ramp("#141418", "#24242a", "#3a3a42", "#5a5a64"), 0.7, bevel=0.04), rail=flat(IRON, 0.7), lamp=fire(R["glow"], 0.5, 0.5), rock=flat(ramp("#08080a", "#121216", "#1e1e24", "#2e2e36", "#42424c"), 0.5, 0.4))
    k.forge(P((-3.8, 3), (3.8, 3), (2.0, 25), (-2.0, 25)), 2.0, step=1)
    k.plate(rect(-3.8, 25, 3.8, 26) + P((-3.8, 26), (-3.8, 27), (3.8, 27), (3.8, 26)), 2.6, "rail")
    k.plate(rect(-1.6, 27, 1.6, 30.2), 2.0, "lamp", glow=True)
    k.plate(rect(-0.3, 27, 0.3, 30.2), 2.1, "rail")
    k.plate(P((-2.4, 30.2), (2.4, 30.2), (0.5, 33), (0, 37.6), (-0.5, 33)), 2.2, "rail")
    for s_ in (1, -1):
        k.plate(L([(s_ * 1.2, 28.2), (s_ * 12.0, 31.4)], 0.5), 0.5, "lamp", glow=True)
    k.plate(P((-6.2, 1.4), (6.2, 1.4), (5.0, 3.6), (3.2, 3.2), (-2.2, 3.6), (-4.6, 3.2)), 3.2, "rock")
    k.grip(-4.8, 1.5, 2.1)
    k.plate(disc(0, -6.6, 2.1, 7), 2.6, "rock")


@design("lighthouse_edge")
def lighthouse_edge(k):
    """the beam itself: a Fresnel lens for a guard and, out of it, a blade of solid light that widens as it goes, framed
    in iron, a black tentacle climbing it to put it out"""
    R = k.theme("abyssal_lighthouse", base=0.5)
    beam = ramp("#c0882a", "#e8b84a", "#ffdc7a", "#fff2b0", "#fffbe0")

    def light(p, n, b, key, i, j, w, h, fr):
        return at(beam, 0.95 - (p[1] - 8) * 0.02 + 0.13 * math.sin(p[1] * 1.9) - abs(facet_of(p, b)) * 0.3)

    tent = ramp("#08060e", "#10101a", "#1a1a2a", "#28283e", "#3a3a56")
    k.mat(beam=light, iron=flat(IRON, 0.62), lens=flat(ramp("#6a8a90", "#94b8bc", "#c0dee0", "#e8fafa"), 0.6, bevel=0.2), tent=flat(tent, 0.56, bevel=0.1), sucker=flat(R["glow"], 0.8))
    m = P((-1.6, 7), (1.6, 7), (6.0, 33.6), (0, 37.6), (-6.0, 33.6))
    k.plate(m.inset(0.5), 1.4, "beam", glow=True)
    k.plate(m - m.inset(0.5), 2.0, "iron", tag="edge")
    t = wave(lambda t: -1.2 + 5.2 * math.sin(t * 7.4) * (0.5 + t * 0.5), lambda t: 1.2 * (1 - t) + 0.25, 8, 33, 40)
    k.plate(t, 2.4, "tent")
    for j in (0.2, 0.4, 0.6):
        k.plate(disc(-1.2 + 5.2 * math.sin(j * 7.4) * (0.5 + j * 0.5), 8 + j * 25, 0.4, 6), 2.5, "sucker")
    k.plate(disc(0, 4.8, 5.4), 2.6, "iron")
    k.plate(disc(0, 4.8, 4.5), 2.8, "lens")
    for r_ in (3.4, 2.2):
        k.plate(disc(0, 4.8, r_) - disc(0, 4.8, r_ - 0.5), 3.0, "iron")
    k.plate(disc(0, 4.8, 1.3, 8), 3.1, "beam", glow=True)
    k.grip(-4.8, 0.0, 2.1)
    k.box(0, -6.4, 0, 3.0, 1.7, 3.0, "iron")


@design("seraph_blade")
def seraph_blade(k):
    """six wings folded up round a long white blade, gold at the edge; the guard sits in a halo. It looks like it should
    not be holdable, and it isn't, by most"""
    R = k.theme("eclipse_cathedral", base=0.66, ridge=0.1)
    k.mat(edge=honed(ramp("#a06018", "#d8982c", "#f6d060", "#fff0b0", "#ffffff"), 0.6), plume=flat(ramp("#8a8aa0", "#b0b0c4", "#d4d4e2", "#f0f0f6", "#ffffff"), 0.7, bevel=0.1),
          vane=flat(ramp("#6a6a84", "#8e8ea8", "#b4b4ca"), 0.5, bevel=0.06), halo=fire(GOLD, 0.5, 0.5), gold=flat(GOLD, 0.66))
    k.forge(P((-2.4, 3), (2.4, 3), (2.2, 30), (0, 37), (-2.2, 30)), 1.8)
    for s_ in (1, -1):
        low = feathers(s_, 3.0, 5, 12.0, 96, 0.9)
        mid = feathers(s_, 3.4, 5, 17.0, 46, 0.9)
        k.plate(low, 0.9, "vane", z=-0.6)
        k.plate(mid, 1.0, "plume")
    k.plate(ring(0, 3.2, 3.8, 2.9), 3.2, "halo", glow=True)
    k.box(0, 1.8, 0, 4.8, 1.6, 3.0, "gold")
    k.grip(-4.8, 1.9, 1.9)
    k.plate(P((-1.8, -4.8), (1.8, -4.8), (0, -9.6)), 2.2, "gold")


@design("fallen_grace")
def fallen_grace(k):
    """the same blade after the Eclipse: gone black, broken through and mended with light, wearing the dead sun on its upper
    third, a black disc in a white corona; the wings hang down burnt from the guard"""
    R = k.theme("eclipse_cathedral", base=0.3, ridge=0.08)
    k.mat(blade=steel(ramp("#040408", "#0a0a12", "#12121c", "#1c1c2a", "#2a2a3c", "#40405a"), 0.5, 0.12), edge=honed(ramp("#14141e", "#2a2a3c", "#4e4e6a", "#8a8aa8", "#d0d0e0"), 0.6),
          ash=flat(ramp("#1a1412", "#2a201c", "#3e2e26", "#5a3e30", "#8a5a38"), 0.6, bevel=0.12), corona=fire(ramp("#d0a040", "#ffe08a", "#fff6d0", "#ffffff"), 0.4, 0.6), void=flat(ramp("#000000", "#040408"), 0.3, bevel=0), ember=fire(GOLD, 0.5, 0.5),
          gold=flat(IRON, 0.7))
    m = P((-2.6, 3), (2.6, 3), (2.4, 30), (0, 38), (-2.4, 30))
    gap = P((-3.0, 14.0), (-0.8, 15.0), (0.4, 13.4), (3.0, 15.2), (3.0, 16.0), (0.4, 14.4), (-0.8, 16.0), (-3.0, 15.0))
    k.forge(m - gap, 2.0)
    k.plate(gap & m, 1.0, "ember", glow=True)
    k.inlay(L([(0.4, 14), (-0.8, 10.6), (0.6, 7.8)], 0.4) + L([(-0.4, 16), (0.8, 19), (-0.4, 22)], 0.4), 2.0, "ember", glow=True)
    k.plate(ring(0, 26.0, 7.8, 6.4), 1.2, "corona", glow=True)
    for j in range(8):
        a = j * math.pi / 4 + 0.4
        ln = 10.2 if j % 2 else 9.2
        k.plate(P((math.cos(a - 0.13) * 7.4, 26 + math.sin(a - 0.13) * 7.4), (math.cos(a) * ln, 26 + math.sin(a) * ln), (math.cos(a + 0.13) * 7.4, 26 + math.sin(a + 0.13) * 7.4)), 0.9, "corona", glow=True)
    k.plate(disc(0, 26.0, 6.5), 2.2, "void")
    for s_ in (1, -1):
        k.plate(feathers(s_, 3.0, 6, 15.0, 84, 1.1, True) - P((s_ * 5, -3), (s_ * 8, -9), (s_ * 10, -3)) - disc(s_ * 11, 0, 1.5, 8), 1.0, "ash")
    k.box(0, 1.8, 0, 6.4, 1.6, 3.0, "gold")
    k.grip(-4.8, 1.9, 2.0)
    k.plate(P((-2.0, -4.8), (2.0, -4.8), (0.8, -6.0), (0, -8.8), (-1.0, -6.4)), 2.2, "ash")


@design("drakefang_sword")
def drakefang_sword(k):
    """a wyrm's fang drawn long and set in the mouth it came from: the guard is the head, jaws open round the blade, horns
    swept back, a ruby for the eye; the tail coils down to make the pommel"""
    R = k.theme("wyrms_hoard", base=0.6)
    tooth = ramp("#6a5a40", "#8e7c5a", "#b4a27a", "#d6c8a0", "#efe6c8", "#fffbe8")
    k.mat(blade=bone(tooth, 0.66), edge=flat(tooth, 0.9, bevel=0.04), scale=flat(GOLD, 0.54, bevel=0.2), gold=flat(GOLD, 0.68), gem=gem(RUBY), maw=flat(ramp("#2a0404", "#4a0808", "#7a1410"), 0.4), horn=flat(ramp("#141010", "#241c18", "#3a2f26", "#54453a", "#76665a"), 0.5))
    k.forge(P(path((-1.8, 8), qb((-3.2, 20), (-0.6, 30), (2.6, 35.4), 12), (2.6, 35.4), qb((2.4, 28), (3.6, 18), (2.4, 8), 10))), 2.0, step=1, ridge=-0.2)
    k.plate(P((-5.4, 1.0), (5.4, 1.0), (4.4, 7.6), (-4.4, 7.6)), 2.6, "maw")
    for s_ in (1, -1):   # the head seen from above, jaws gaping up round the blade
        jaw = P(path((s_ * 1.0, 0.4), (s_ * 6.0, 1.0), qb((s_ * 7.4, 6.0), (s_ * 7.8, 11.0), (s_ * 3.8, 15.6), 8), (s_ * 3.8, 15.6), qb((s_ * 5.0, 11.2), (s_ * 4.8, 7.6), (s_ * 2.8, 5.6), 8), (s_ * 1.0, 5.2)))
        k.plate(jaw, 3.4, "scale")
        for y, ln in ((7.4, 2.0), (9.8, 2.0), (12.2, 1.7)):
            x = 4.6 + (10 - y) * 0.1 - (y - 9) * 0.1
            k.plate(P((s_ * x, y), (s_ * x, y + 1.3), (s_ * (x - ln), y + 0.2)), 1.2, "edge")
        k.plate(disc(s_ * 3.8, 4.0, 1.1, 8), 3.8, "gem")
        k.plate(P((s_ * 2.2, 5.6), (s_ * 5.2, 5.8), (s_ * 5.0, 5.0)), 3.7, "horn")
        k.plate(stroke((s_ * 5.2, 2.0), (s_ * 10.8, 1.8), (s_ * 12.0, -5.4), 1.7, 10) + stroke((s_ * 5.0, 1.0), (s_ * 7.6, -1.4), (s_ * 7.0, -5.4), 1.1, 8), 2.2, "horn")
    k.grip(-4.8, 1.0, 2.1, "scale")
    k.plate(stroke((0, -4.8), (3.6, -7.6), (0.4, -9.6), 1.9, 8) + stroke((0.4, -9.6), (-3.2, -11.0), (-2.2, -7.4), 1.1, 8), 2.2, "gold")


@design("hedge_knights_sword")
def hedge_knights_sword(k):
    """nothing clever: a good arming sword a poor knight has kept sharp for twenty years. A long fuller, a wheel pommel, a
    plain bar with its ends turned, and a red tassel his lady tied on"""
    R = {"blade": ramp("#2a2e34", "#3e444c", "#565e68", "#727c86", "#929ca6", "#b4bec6", "#d4dce2", "#f0f4f6")}
    red = ramp("#2a0606", "#4a0c0a", "#741612", "#9c2218", "#c23a26")
    k.mat(blade=steel(R["blade"], 0.54, 0.13, scars=0.04), edge=honed(R["blade"], 0.84), iron=flat(IRON, 0.66), brass=flat(BRASS, 0.62), wrap=wrap(red, BRASS[2], 5), tassel=flat(red, 0.66, 0.2),
          fuller=flat(R["blade"], 0.34, bevel=0.05))
    k.forge(taper(2.4, 1.6, 3, 26, 30.5), 1.5)
    k.inlay(rect(-0.5, 4, 0.5, 21), 1.5, "fuller")
    k.plate(rect(-5.2, 1.7, 5.2, 3.0), 2.4, "iron")
    for s_ in (1, -1):
        k.plate(P((s_ * 4.4, 1.7), (s_ * 5.8, 1.7), (s_ * 6.2, 4.2), (s_ * 5.2, 3.8)), 2.4, "iron")
    k.grip(-4.6, 1.8, 2.0)
    k.plate(disc(0, -6.0, 2.2, 14), 2.0, "brass")
    k.plate(disc(0, -6.0, 1.0, 8), 2.3, "iron")
    k.box(1.2, -2.0, 0, 0.5, 3.8, 0.5, "tassel")
    k.plate(P((0.6, -2.2), (1.8, -2.2), (2.2, -6.4), (1.2, -5.8), (0.2, -6.4)), 1.0, "tassel")


@design("wolfbiter")
def wolfbiter(k):
    """a northern blade with the pack's teeth set up one edge, real fangs bedded in steel, a wolf's ruff round the guard
    and the skull's muzzle for a pommel"""
    fe = ramp("#1c1a18", "#2a2724", "#3a3632", "#4c4741", "#605a52", "#787066", "#928a7e", "#aea698")
    fur = ramp("#1e1c1c", "#34302e", "#524c48", "#786e68", "#a49a90", "#cec4b8")
    ivory = ramp("#8e7c5a", "#b4a27a", "#d6c8a0", "#efe6c8", "#fffbe8")
    k.mat(blade=steel(fe, 0.56, 0.12, scars=0.05), edge=honed(fe, 0.86), fang=flat(ivory, 0.7, bevel=0.1), fur=flat(fur, 0.56, 0.5), wrap=wrap(fur, fur[0], 5), silver=flat(SILVER, 0.6))
    k.forge(P((-2.6, 3), (2.4, 3), (2.4, 25), (-0.4, 30.4), (-2.6, 26)), 1.8, ridge=-0.2)
    y = 6.0
    j = 0
    while y < 24:
        ln = (3.4, 2.2, 2.8)[j % 3]
        k.plate(P((1.8, y), (1.8, y + 1.7), (2.4 + ln, y + 2.4)), 1.0, "fang")
        y += 2.5
        j += 1
    fur_m = Mask()
    for x, ln in ((-4.4, 3.0), (-3.0, 4.2), (-1.4, 3.4), (0.4, 4.4), (2.0, 3.4), (3.6, 4.0), (4.8, 2.6)):
        fur_m = fur_m + P((x - 1.1, 3.2), (x + 1.1, 3.2), (x + 0.2, 3.2 - ln))
    k.plate(rect(-5.2, 1.8, 5.2, 3.6) + fur_m, 3.2, "fur")
    k.grip(-4.6, 1.2, 2.0)
    k.plate(P((-2.2, -4.6), (2.2, -4.6), (1.8, -6.6), (0.9, -9.8), (-0.9, -9.8), (-1.8, -6.6)), 2.8, "fang")
    k.inlay(rect(-1.5, -6.2, -0.5, -5.4) + rect(0.5, -6.2, 1.5, -5.4) + rect(-0.5, -9.8, 0.5, -9.0), 2.8, "wrap")


@design("emberwake")
def emberwake(k):
    """a black falchion with a live heart: cracks run the blade and the belly burns, fire licks up its root; ram's horns
    curl down off the guard"""
    black = ramp("#08080a", "#101014", "#18181e", "#22222a", "#2e2e38", "#3e3e4a", "#54545f")
    ember = ramp("#7a1406", "#c0300a", "#ff6a14", "#ffb040", "#ffe8a0", "#fffbe0")
    k.mat(blade=steel(black, 0.5, 0.1), edge=fire(ember, 0.25, 0.6), rim=honed(black, 0.9), hot=fire(ember, 0.45, 0.55), flame=fire(ember, 0.1, 0.8), horn=flat(ramp("#141010", "#241c18", "#3a2f26", "#54453a", "#76665a", "#9c8c7c"), 0.5, bevel=0.14),
          iron=flat(IRON, 0.56), wrap=wrap(LEATHER, IRON[1]))
    m = P((-2.4, 3), (-2.6, 22), (2.8, 30.6), (6.8, 26), (6.4, 17), (2.8, 3))
    k.plate(m, 1.0, "rim", tag="edge")
    k.plate(m & P((1.0, 0), (9, 0), (9, 33), (2.4, 33), (5.0, 22), (3.4, 12)), 1.04, "edge", glow=True)
    k.plate(m.inset(0.5), 2.2, "blade", ridge=-0.3, tag="blade")
    for pts in (((0, 6), (1.4, 10), (0, 14), (1.6, 18), (0.6, 22), (2.4, 26)), ((1.4, 10), (3.2, 12)), ((1.6, 18), (3.6, 20.4)), ((0, 14), (-1.6, 16))):
        k.inlay(L(list(pts), 0.5), 2.2, "hot", glow=True)
    for x, ln in ((-1.4, 4.0), (0.6, 5.6), (2.2, 3.4)):
        k.plate(P((x - 1.1, 3), (x + 1.1, 3), (x + 0.3, 3 + ln)), 2.4, "flame", glow=True)
    k.box(0.2, 1.6, 0, 7.6, 1.6, 3.2, "iron")
    for s_ in (1, -1):
        k.plate(stroke((s_ * 3.4, 2.6), (s_ * 10.2, 2.4), (s_ * 6.6, -4.4), 1.5, 10) + stroke((s_ * 6.6, -4.4), (s_ * 4.0, -5.0), (s_ * 4.6, -2.2), 0.9, 6), 2.0, "horn")
    k.grip(-4.8, 1.7, 2.1)
    k.box(0, -6.8, 0, 2.8, 2.1, 2.8, "iron")
    k.box(0, -6.2, 0, 1.2, 1.0, 3.0, "hot", glow=True)


@design("starfall")
def starfall(k):
    """the night sky made into a blade: deep blue steel, a constellation burning in it, one star falling up the edge; a
    silver crescent for the guard and a four-pointed star at the tip"""
    night = ramp("#060a1a", "#0a1228", "#101c3c", "#182a54", "#22386c", "#304a86", "#4a66a8", "#7a96d0")
    starc = ramp("#7ab0ff", "#b0d4ff", "#e0f0ff", "#ffffff")
    k.mat(blade=steel(night, 0.54, 0.13, sheen=0.14), edge=honed(SILVER, 0.7), silver=flat(SILVER, 0.66), star=fire(starc, 0.5, 0.5), wrap=wrap(night, SILVER[2], 5))
    k.forge(P((-3.2, 3), (3.2, 3), (3.4, 16), (2.2, 28), (0, 31.4), (-2.2, 28), (-3.4, 16)), 2.0)
    stars = ((-1.2, 7), (1.2, 10.4), (-0.6, 14), (1.4, 17.6), (-1.0, 21), (0.4, 25))
    k.inlay(L(list(stars), 0.3), 2.0, "edge", glow=False)
    for x, y in stars:
        k.inlay(rect(x - 0.5, y - 0.5, x + 0.5, y + 0.5) + rect(x - 1, y - 0.25, x + 1, y + 0.25) + rect(x - 0.25, y - 1, x + 0.25, y + 1), 2.1, "star", glow=True)
    for a, ln, w in ((0, 5.4, 1.5), (90, 3.6, 1.2), (180, 5.0, 1.5), (270, 3.6, 1.2)):
        r = math.radians(a)
        d, t = (-math.sin(r), math.cos(r)), (math.cos(r), math.sin(r))
        k.plate(P((t[0] * w, 32.6 + t[1] * w), (d[0] * ln, 32.6 + d[1] * ln), (-t[0] * w, 32.6 - t[1] * w)), 1.6, "star", glow=True)
    k.plate(disc(0, 8.4, 9.2) - disc(0, 11.0, 9.0), 2.2, "silver")
    k.grip(-4.8, 0.4, 2.0)
    k.plate(disc(0, -6.4, 1.8, 10), 2.4, "silver")
    k.plate(disc(0, -6.4, 0.8, 8), 2.6, "star", glow=True)


@design("brigands_falchion")
def brigands_falchion(k):
    """more rust than steel and the owner doesn't care: a hacked square end, a split spine patched with a riveted plate, a
    bar of a guard off a gate hinge"""
    rust = ramp("#1a0c06", "#301608", "#4e220c", "#723214", "#94481e", "#b4642e", "#cc8644", "#e0ac70")
    k.mat(blade=steel(rust, 0.5, 0.14, scars=0.08), edge=honed(ramp("#3a2a20", "#5a4638", "#7e6a58", "#a4907c", "#c8b6a0"), 0.7), patch=flat(IRON, 0.5), rivet=flat(BRASS, 0.56), cloth=flat(ramp("#2a0606", "#4a0c0a", "#741612", "#9c2218"), 0.56, 0.3),
          wrap=wrap(LEATHER, IRON[1]))
    m = P((-2.4, 3), (-2.4, 25.6), (0.6, 27.4), (1.6, 26.0), (3.0, 28.2), (5.6, 24.4), (5.0, 20.6), (5.6, 16), (3.4, 3))
    k.forge(m - P((5.8, 13.6), (3.8, 12.4), (5.8, 11.4)), 1.8, ridge=-0.3)
    k.plate(rect(-3.0, 14, 1.0, 21), 2.4, "patch")
    for x, y in ((-2.2, 15), (-2.2, 19.4), (0, 15), (0, 19.4)):
        k.box(x, y, 0, 0.9, 0.9, 2.6, "rivet")
    k.plate(L([(-4.8, 2.0), (6.2, 2.8)], 1.3), 2.6, "patch")
    k.plate(ring(-4.9, 1.8, 1.6, 0.7), 2.6, "patch")
    k.grip(-4.6, 1.8, 2.0)
    k.box(0, -6.0, 0, 2.8, 1.4, 2.8, "patch")
    k.plate(P((2.8, 2.4), (4.4, 2.0), (6.6, -3.4), (5.0, -2.4), (4.0, -4.8), (2.6, -2.0)), 0.7, "cloth")


@design("corsairs_cutlass")
def corsairs_cutlass(k):
    """a drowned captain's blade: sea bronze gone green, its edge cut in a line of breaking waves, the guard a ring of ship's
    cable and a small anchor hung off the pommel"""
    bronze = ramp("#0e2420", "#163a30", "#205244", "#2e6e5a", "#448c74", "#6cb094", "#a8d8bc")
    k.mat(blade=steel(bronze, 0.56, 0.13), edge=honed(ramp("#6a5020", "#a07c34", "#d0ae56", "#ecd488", "#faeec4"), 0.7), rope=wrap(ramp("#5a4a30", "#7a6848", "#9c8a64", "#bcaa84"), None, 3), bronze=flat(bronze, 0.56), gold=flat(GOLD, 0.6),
          wrap=wrap(ramp("#061a1c", "#0e2c30", "#164046", "#20565c"), BRASS[3], 5))
    back = qb((-2.0, 3), (-3.0, 16), (5.0, 29), 12)
    crest = []
    y = 3.4
    j = 0
    while y < 25:
        x = 3.0 + (y / 25) ** 2 * 3.6
        crest += [(x, y), (x + 2.4, y + 0.4), (x + 0.6, y + 1.6)] if j else [(x, y)]
        y += 3.6
        j += 1
    k.forge(P(back + [(5.0, 29), (6.8, 25.4)] + crest[::-1]), 1.8, ridge=-0.45)
    k.plate(ring(0.3, 3.0, 5.6, 4.0) - rect(-1.4, 3, 2.8, 9), 2.2, "rope")
    k.box(0.3, 1.7, 0, 7.4, 1.4, 2.6, "bronze")
    k.grip(-4.6, 1.8, 2.0)
    k.box(0, -5.6, 0, 2.6, 1.2, 2.6, "gold")
    k.box(0, -8.2, 0, 0.8, 2.7, 0.8, "bronze")
    k.plate(rect(-1.4, -7.4, 1.4, -6.8), 1.0, "bronze")
    k.plate(stroke((-2.6, -8.0), (-1.4, -10.2), (2.6, -8.0), 0.8) + P((-3.2, -7.4), (-1.8, -8.0), (-2.8, -8.8)) + P((3.2, -7.4), (1.8, -8.0), (2.8, -8.8)), 1.0, "bronze")


@design("thornheart")
def thornheart(k):
    """a blade grown, not made: a dark-red briar leaf with thorns all up it, and at its heart, where the guard would be,
    a rose open and burning"""
    wood = ramp("#100806", "#1e0e0a", "#301610", "#461e16", "#5e281c", "#7c3626")
    rose = ramp("#3a0410", "#6a0a1e", "#a0142e", "#d42a44", "#f4607a", "#ffb0bc")
    leaf = ramp("#0a1a0c", "#122a14", "#1c3e1c", "#285426", "#366c30", "#4a883c")
    k.mat(blade=steel(wood, 0.56, 0.14), edge=honed(rose, 0.66), thorn=flat(ramp("#2a1a10", "#4a3020", "#6e4c34", "#96704e"), 0.6), rose=flat(rose, 0.56, bevel=0.16), hot=fire(ramp("#ff6a6a", "#ffb080", "#ffe8b0", "#ffffff"), 0.3, 0.7), leaf=flat(leaf, 0.56, bevel=0.1),
          wrap=wrap(leaf, wood[1], 4))
    m = wave(lambda t: 0.8 * math.sin(t * 6.4), lambda t: 3.4 * math.sin(min(1, 0.22 + t * 0.78) * math.pi) ** 0.8 + 0.2, 4, 33, 32)
    th = Mask()
    for j, y in enumerate((11, 13.6, 16.2, 18.8, 21.4, 24, 26.6, 28.8)):
        s_ = 1 if j % 2 else -1
        x = 0.8 * math.sin((y - 4) / 29 * 6.4) + s_ * (3.6 - j * 0.28)
        th = th + P((x - s_ * 0.6, y - 0.9), (x + s_ * 3.0, y + 1.8), (x - s_ * 0.4, y + 0.8))
    k.plate(th, 1.2, "thorn")
    k.forge(m, 1.9)
    for r_, sc, off in ((5.2, 1.0, 0.0), (3.8, 1.0, 0.6), (2.6, 1.0, 1.1)):
        ms = Mask()
        for j in range(5):
            a = j * 2 * math.pi / 5 + off
            ms = ms + disc(math.cos(a) * r_ * 0.55, 6.0 + math.sin(a) * r_ * 0.55, r_ * 0.56, 10)
        k.plate(ms, 2.4 + (5.2 - r_) * 0.5, "rose")
    k.plate(disc(0, 6.0, 1.0, 8), 4.2, "hot", glow=True)
    for s_ in (1, -1):
        k.plate(P((s_ * 3, 2.0), (s_ * 6.8, 0.4), (s_ * 9.6, 3.0), (s_ * 6.8, 3.6)), 1.0, "leaf")
    k.grip(-4.8, 2.2, 2.0)
    k.plate(disc(0, -6.2, 1.8, 7), 2.6, "thorn")


@design("chainsworn")
def chainsworn(k):
    """the Fallen Order's oath-blade: a broad knight's sword with a reliquary window in its root, a soul burning blue in it,
    bound round with the chains that hold the oath; the broken ends hang from the guard"""
    tarn = ramp("#14181c", "#222a2e", "#34403f", "#48574f", "#607060", "#808c78", "#a8ae98", "#d0d2bc")
    soul = ramp("#0e3a5a", "#1e6a96", "#3fa0d0", "#6fc8f0", "#c0ecff", "#ffffff")
    k.mat(blade=steel(tarn, 0.54, 0.13, scars=0.04), edge=honed(tarn, 0.84), chain=flat(SILVER, 0.56, bevel=0.2), iron=flat(IRON, 0.66), soul=fire(soul, 0.4, 0.6), wrap=wrap(ramp("#0e1a3a", "#182a54", "#22386c", "#304a86"), SILVER[2], 5))
    m = P((-3.6, 3), (3.6, 3), (3.4, 28), (0, 34), (-3.4, 28))
    window = rect(-1.6, 6.6, 1.6, 12.6) + P((-1.6, 12.6), (1.6, 12.6), (0, 14.8))
    k.forge(m - window, 2.2)
    k.plate(window, 1.6, "soul", glow=True)
    k.plate(L([(-2.4, 5.6), (-2.4, 13), (0, 15.8), (2.4, 13), (2.4, 5.6), (-2.4, 5.6)], 0.8), 2.5, "iron")
    k.inlay(rect(-0.2, 6.6, 0.2, 14), 1.8, "iron")
    for j, (a, b) in enumerate((((-5.0, 15.6), (5.0, 19.0)), ((5.0, 21.0), (-5.0, 24.4)))):
        n = 7
        pts = [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(n + 1)]
        for i, (p, q) in enumerate(zip(pts, pts[1:])):
            cx, cy = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
            ang = math.degrees(math.atan2(-(q[0] - p[0]), q[1] - p[1]))
            ln = math.hypot(q[0] - p[0], q[1] - p[1]) + 0.5
            k.box(cx, cy - ln / 2, 0, 1.2, ln, 2.8, "chain", rots=(("z", ang),), pivot=(cx, cy, 0))
    k.plate(rect(-6.6, 1.6, 6.6, 3.2) + P((-6.6, 3.2), (-7.8, 4.4), (-6.0, 1.6)) + P((6.6, 3.2), (7.8, 4.4), (6.0, 1.6)), 2.8, "iron")
    links(k, [(-5.4, 1.8), (-5.8, 0.2), (-5.4, -1.4), (-5.8, -3.0), (-5.2, -4.6)], "chain")
    links(k, [(5.4, 1.8), (5.6, 0.4), (5.2, -1.0)], "chain")
    k.grip(-4.8, 1.7, 2.1)
    k.plate(ring(0, -6.6, 2.4, 1.2), 2.8, "iron")


@design("oathbinder")
def oathbinder(k):
    """two blades sworn into one: twin narrow swords side by side, a hair apart, held by three clasps shaped like closed
    hands; two grips' worth of guard, one gold, one iron, meeting in the middle"""
    fe = ramp("#2a2e34", "#3e444c", "#565e68", "#727c86", "#929ca6", "#b4bec6", "#d4dce2", "#f0f4f6")
    pale = ramp("#6a5a3a", "#8c7a52", "#b09c6c", "#cec08a", "#e6dcae", "#f6f0d2", "#fffbec", "#ffffff")
    k.mat(blade=steel(fe, 0.54, 0.13), edge=honed(fe, 0.84), goldb=steel(pale, 0.5, 0.13), goldedge=honed(GOLD, 0.8), clasp=flat(GOLD, 0.62, bevel=0.14), iron=flat(IRON, 0.66), gold=flat(GOLD, 0.66), wrap=wrap(LEATHER, GOLD[3], 4),
          hot=fire(ramp("#ffb040", "#ffe8a0", "#fffbe0", "#ffffff"), 0.4, 0.6))
    l_ = P((-3.8, 3), (-0.4, 3), (-0.4, 30), (-1.0, 35), (-3.2, 27))
    r_ = P((3.8, 3), (0.4, 3), (0.4, 30), (1.0, 35), (3.2, 27))
    k.forge(l_, 1.6, ridge=0.0)
    k.plate(r_, 0.8, "goldedge", tag="edge")
    k.plate(r_.inset(1.0 / 2), 1.6, "goldb", tag="blade")
    k.plate(rect(-0.4, 5, 0.4, 28), 0.5, "hot", glow=True)
    for y in (8, 16, 24):
        w = 4.6 - y * 0.04
        k.box(0, y, 0, w * 2, 2.0, 2.6, "clasp")
        for j in range(3):
            k.box(-1.6 + j * 1.6, y + 0.4, 0, 1.0, 1.2, 2.9, "gold")
    k.plate(P((-7.2, 1.6), (0, 1.6), (0, 3.2), (-6.4, 3.2), (-8.4, 5.0)), 2.8, "iron")
    k.plate(P((7.2, 1.6), (0, 1.6), (0, 3.2), (6.4, 3.2), (8.4, 5.0)), 2.8, "gold")
    k.grip(-4.8, 1.7, 2.1)
    k.plate(disc(0, -6.6, 2.3, 12), 2.2, "iron")
    k.plate(disc(0.6, -6.6, 1.7, 10), 2.4, "gold")
