"""Swords: the Frozen March, the Silk Archive, the Weeping Mine, the Tide Chapel, Brigand's Gorge, the Rookery, the Hollow
Circus, the Mirefen Coven, the Sandsunk Tomb."""
import math

from voxsword import ramp
from weaponsets import design, qb, path, P, L, disc, ring, rect, wave, taper, Mask, flat, fire, staves, steel, honed, bone, gem, at, lit, wrap, stripes
from weaponsets_a import BRASS, GOLD, IRON


def shard(x, y, ln, ang, w):
    """a crystal: a long six-sided splinter standing off (x, y), leaning ang degrees from straight up"""
    a = math.radians(ang)
    d, t = (-math.sin(a), math.cos(a)), (math.cos(a), math.sin(a))
    return P((x - t[0] * w * 0.6, y - t[1] * w * 0.6), (x + t[0] * w * 0.6, y + t[1] * w * 0.6),
             (x + d[0] * ln * 0.72 + t[0] * w * 0.5, y + d[1] * ln * 0.72 + t[1] * w * 0.5), (x + d[0] * ln, y + d[1] * ln),
             (x + d[0] * ln * 0.72 - t[0] * w * 0.5, y + d[1] * ln * 0.72 - t[1] * w * 0.5))


@design("rime_sword")
def rime_sword(k):
    """a soldier's sword left out in the March: the steel is still there, but ice has grown off both edges in shards, all
    leaning the way the wind blew, and hangs off the guard"""
    R = k.theme("frost", base=0.5)
    k.mat(ice=flat(R["glow"], 0.7, bevel=0.14), rime=flat(R["glow"], 0.9, bevel=0.06))
    k.forge(taper(2.3, 1.6, 3, 25, 28.5), 1.6)
    ice = Mask()
    for x, y, ln, a, w in ((2.0, 8, 6.6, -28, 2.0), (-2.1, 11, 7.6, 24, 2.2), (1.8, 15, 7.2, -20, 2.0), (-1.8, 18, 6.4, 18, 1.8), (1.4, 21, 7.2, -14, 1.6), (-1.2, 24, 8.4, 8, 1.6)):
        ice = ice + shard(x, y, ln, a, w)
    k.plate(ice, 1.3, "ice")
    k.plate(ice.inset(0.5), 1.5, "rime")
    k.box(0, 1.7, 0, 9.4, 1.5, 2.6, "dark")
    for x, ln in ((-4.0, 3.4), (-2.2, 2.0), (2.6, 2.8), (4.2, 3.8)):
        k.plate(P((x - 0.6, 1.8), (x + 0.6, 1.8), (x, 1.8 - ln)), 1.2, "ice")
    k.grip(-4.6, 1.8, 2.0)
    k.plate(shard(0, -4.4, 4.0, 180, 2.2), 2.0, "ice")


@design("marshals_sabre")
def marshals_sabre(k):
    """the Winter Marshal's dress sabre: a long clean curve that runs out into pure ice at the point, a knuckle bow, and his
    red pennant frozen stiff mid-flap from the guard with a snow crystal on it"""
    R = k.theme("frost", base=0.54)
    k.mat(ice=flat(R["glow"], 0.76, bevel=0.1), red=flat(R["acc"], 0.6, bevel=0.14), white=flat(R["glow"], 0.92, bevel=0.04), silver=flat(R["blade"], 0.7))
    back = qb((-1.8, 3), (-3.0, 19), (5.4, 27), 12)
    belly = qb((6.8, 25.8), (3.2, 12), (2.6, 3), 12)
    k.forge(P(path(back, (5.4, 27), belly, (2.6, 3))), 1.7, ridge=-0.4)
    k.plate(shard(6.0, 25.8, 9.0, -36, 2.4), 1.6, "ice")
    k.plate(shard(6.0, 26.4, 6.0, -36, 1.2), 1.8, "white")
    bow_ = L(path(qb((3.6, 2.4), (8.0, -1.0), (1.2, -5.6), 10), (1.2, -5.6)), 1.0)
    k.plate(bow_, 1.5, "silver")
    k.box(0.6, 1.8, 0, 7.6, 1.3, 2.8, "silver")
    flag = P((-3.2, 2.6), (-3.2, -4.6), (-7.0, -3.0), (-9.4, -5.6), (-10.8, -2.2), (-12.8, -3.0), (-11.2, 1.6), (-8.0, 1.2), (-5.4, 3.0))
    k.plate(flag, 0.9, "red")
    for a in (0, 60, 120):
        r = math.radians(a)
        c, s_ = math.cos(r) * 2.2, math.sin(r) * 2.2
        k.inlay(L([(-7.6 - c, -1.0 - s_), (-7.6 + c, -1.0 + s_)], 0.5), 0.9, "white")
    k.box(-3.1, -5.0, 0, 0.8, 8.4, 0.8, "dark")
    k.grip(-4.8, 1.8, 2.0)
    k.box(0, -6.6, 0, 2.6, 1.9, 2.6, "silver")


@design("scriveners_blade")
def scriveners_blade(k):
    """a pen for a giant: the blade is a steel nib, its slit running down to the breather hole with ink still creeping up
    it; the feather it was cut from curls from the pommel"""
    R = k.theme("silk", base=0.56)
    k.mat(ink=fire(R["glow"], 0.1, 0.8), feather=flat(R["acc"], 0.74, bevel=0.1), vane=flat(R["acc"], 0.5, bevel=0.08), brass=flat(BRASS, 0.6))
    nib = P(path((-2.0, 3), qb((-2.0, 6), (-5.6, 12), (-3.4, 18)), (-3.4, 18), (0, 31.6), (3.4, 18), qb((3.4, 18), (5.6, 12), (2.0, 6)), (2.0, 3)))
    slit = L([(0, 31.6), (0, 14.4)], 0.5)
    hole = disc(0, 13.2, 1.5)
    k.plate(nib - slit - hole, 1.0, "edge", tag="edge")
    k.plate((nib - slit - hole).inset(0.5), 1.8, "blade", tag="blade")
    k.plate((slit + hole) & nib, 0.7, "ink", glow=True)
    k.inlay(L([(-3.0, 9), (-0.6, 16)], 0.4) + L([(3.0, 9), (0.6, 16)], 0.4), 1.8, "dark")
    k.box(0, 1.7, 0, 5.0, 1.6, 2.6, "brass")
    k.box(0, 3.0, 0, 3.6, 1.0, 2.8, "dark")
    k.grip(-4.8, 1.8, 2.0)
    stem = qb((0, -5), (-1, -11), (-7.6, -15.4), 10)
    k.plate(L(stem + [(-7.6, -15.4)], 0.8), 1.2, "feather")
    vane = Mask()
    for j, p_ in enumerate(stem[1:]):
        vane = vane + L([p_, (p_[0] + 2.8, p_[1] - 0.8 - j * 0.1)], 1.0) + L([p_, (p_[0] - 2.4, p_[1] + 0.2 - j * 0.1)], 1.0)
    k.plate(vane, 0.8, "vane")
    k.box(0, -6.0, 0, 2.6, 1.2, 2.6, "brass")


@design("queens_needle")
def queens_needle(k):
    """the Silk Queen's own needle: as long as a sword and as thin as a rumour, its eye threaded with silk that winds down
    the blade; her legs, curled and dry, still clasp the guard"""
    R = k.theme("silk", base=0.6)
    k.mat(silk=flat(R["acc"], 0.86, bevel=0.04), leg=flat(R["dark"], 0.72, bevel=0.2), brass=flat(R["blade"], 0.76))
    m = P((-1.1, 3), (1.1, 3), (0.9, 26), (1.9, 28.6), (0.9, 31.6), (0, 37), (-0.9, 31.6), (-1.9, 28.6), (-0.9, 26)) - P((0, 26.6), (0.8, 28.6), (0, 30.8), (-0.8, 28.6))
    k.forge(m, 1.5)
    thread = Mask()
    for j in range(7):
        y = 25.5 - j * 3.0
        thread = thread + L([(-1.5, y), (1.5, y + 1.6)], 0.4)
    k.plate(thread, 1.8, "silk")
    k.plate(L(path(qb((0, 28.6), (5.0, 29), (2.6, 21), 8), qb((2.6, 21), (0.8, 17), (5.4, 11), 8), (5.4, 11)), 0.4), 0.5, "silk")
    for j, (a, b, c) in enumerate((((1.6, 3.6), (7.0, 7.2), (9.4, 1.8)), ((1.4, 2.8), (5.6, 2.2), (7.2, -3.2)), ((1.2, 2.2), (3.8, -1.0), (4.6, -6.0)), ((1.4, 4.0), (4.8, 10.0), (8.6, 8.8)))):
        for s_ in (1, -1):
            k.plate(L(qb((s_ * a[0], a[1]), (s_ * b[0], b[1]), (s_ * c[0], c[1]), 8) + [(s_ * c[0], c[1])], 0.9 - j * 0.04), 1.2, "leg")
    k.plate(disc(0, 3, 2.4, 12), 3.2, "leg")
    k.plate(P((0, 4.4), (0.9, 3.2), (0.4, 2.6), (0.9, 1.4), (-0.9, 1.4), (-0.4, 2.6), (-0.9, 3.2)), 3.3, "glow", glow=True)
    k.grip(-4.8, 1.2, 1.9)
    k.plate(disc(0, -6.2, 1.7, 12), 2.4, "leg")


@design("seam_cutter")
def seam_cutter(k):
    """a mine worker's chopper cut from a pick bar: a chisel end, not a point; a seam of live crystal runs up it and has burst
    out through the spine. The guard is a length of rail"""
    R = k.theme("weeping_mine", base=0.5)
    k.mat(copper=flat(R["acc"], 0.56), crystal=flat(R["glow"], 0.7, bevel=0.14), rail=flat(R["blade"], 0.5))
    k.forge(P((-2.4, 3), (3.0, 3), (3.4, 26.6), (-2.6, 29.6)), 2.2, ridge=0.2)
    k.inlay(L([(1.4, 4.4), (0.2, 9), (1.2, 13), (-0.6, 17), (-1.6, 19)], 0.7), 2.2, "glow", glow=True)
    k.plate(shard(-2.0, 16, 7.0, 40, 2.2) + shard(-2.2, 19, 5.4, 22, 1.8) + shard(-2.0, 14, 4.6, 66, 1.6), 1.8, "crystal")
    k.plate(shard(-2.0, 16.4, 4.6, 40, 1.0), 2.0, "glow", glow=True)
    for y in (6.0, 23.5):
        k.box(0.3, y, 0, 6.8, 0.9, 2.6, "copper")
    k.plate(rect(-5.0, 1.4, 5.0, 2.0) + rect(-1.2, 2.0, 1.2, 2.6) + rect(-5.0, 2.6, 5.0, 3.6), 2.4, "rail")
    k.grip(-4.8, 1.5, 2.2)
    k.box(0, -6.4, 0, 3.0, 1.7, 3.0, "copper")


@design("veinsplitter")
def veinsplitter(k):
    """what the Weeping Mine does to steel: a great blade split in two by the crystal wedged in it, the halves bowed apart
    round a burning cluster, bound with copper wire so it won't finish the job"""
    R = k.theme("weeping_mine", base=0.5)
    k.mat(copper=flat(R["acc"], 0.6), crystal=flat(R["glow"], 0.72, bevel=0.14))
    left = P(path((-3.4, 3), qb((-3.8, 14), (-8.4, 22), (-3.0, 33.4), 10), (-3.0, 33.4), qb((-2.4, 30), (-3.8, 21), (-0.4, 13), 10), (-0.4, 13), (0.2, 3)))
    right = P(path((3.4, 3), qb((3.8, 14), (8.0, 21), (4.6, 30.6), 10), (4.6, 30.6), qb((3.8, 27.6), (3.8, 20), (0.2, 13), 10), (0.2, 13), (-0.2, 3)))
    k.forge(left + right, 2.4, ridge=0.0)
    k.plate(shard(0, 12.4, 18, 0, 3.8) + shard(-0.8, 13.4, 13, 8, 2.8) + shard(0.9, 13, 14, -10, 2.8), 2.8, "crystal")
    k.plate(shard(0, 13.4, 13, 0, 1.8), 3.0, "glow", glow=True)
    k.inlay(L([(0, 4), (0.6, 8), (0, 12)], 0.7), 2.4, "glow", glow=True)
    for j in range(4):
        k.box(0, 10.2 + j * 0.7, 0, 8.4, 0.45, 3.0, "copper")
    k.plate(P((-6.4, 1.6), (6.4, 1.6), (7.0, 3.4), (-7.0, 3.4)), 3.4, "dark")
    k.grip(-4.8, 1.7, 2.2)
    k.plate(rect(-1.8, -8.0, 1.8, -5.0), 2.8, "copper")
    k.plate(rect(-1.1, -7.6, 1.1, -5.4), 2.9, "glow", glow=True)
    k.plate(ring(0, -9.2, 1.4, 0.6), 1.0, "dark")


@design("wreck_cutlass")
def wreck_cutlass(k):
    """a short broad cutlass off the wreck: barnacles up its back, a nick where it met a rib of the ship; the guard is one
    great scallop shell, fluted, a tarred rope grip"""
    R = k.theme("tide_chapel", base=0.48, scars=0.05)
    k.mat(shell=flat(R["acc"], 0.72, bevel=0.1), rope=wrap(R["dark"], R["dark"][0], 4))
    m = P(path(qb((-2.0, 6), (-2.2, 17), (4.4, 25.6), 10), (4.4, 25.6), (6.6, 23.2), qb((6.6, 22.4), (5.0, 11), (2.8, 6), 10)))
    m = m - P((6.4, 14.5), (4.0, 15.2), (5.8, 16.4))
    k.forge(m, 1.9, ridge=-0.4)
    for x, y, r_ in ((-2.2, 10, 1.0), (-2.0, 13.2, 0.8), (-1.2, 16.6, 1.1), (0.2, 19.2, 0.8)):
        k.plate(disc(x, y, r_, 8) - disc(x, y, 0.3, 6), 2.6, "shell")
    fan = Mask()
    for a in range(-70, 71, 20):
        r = math.radians(a)
        fan = fan + L([(0, 0.8), (-math.sin(r) * 7.6, 0.8 + math.cos(r) * 7.6)], 1.9)
    k.plate(fan, 2.2, "shell")
    k.plate(disc(0, 2.0, 2.0, 10), 2.6, "shell")
    for a in range(-60, 61, 20):
        r = math.radians(a)
        k.inlay(L([(-math.sin(r) * 2.6, 0.8 + math.cos(r) * 2.6), (-math.sin(r) * 7.0, 0.8 + math.cos(r) * 7.0)], 0.4), 2.2, "dark")
    k.grip(-4.6, 1.2, 2.2, "rope")
    k.box(0, -6.4, 0, 2.8, 1.8, 2.8, "shell")


@design("longmourn")
def longmourn(k):
    """the Chapel's drowned bell, cast round a sword: a long thin blade comes up out of the bell's crown, the hand goes up
    inside the mouth, a pearl clapper hangs by the grip, kelp streams from the shoulder"""
    R = k.theme("tide_chapel", base=0.5)
    bronze = ramp("#1a1c10", "#2c3018", "#44482a", "#5e6438", "#7c8448", "#a0a860", "#c8c884")
    k.mat(bell=flat(bronze, 0.56, bevel=0.12), kelp=flat(R["wrap"], 0.56), pearl=flat(R["glow"], 0.86))
    k.forge(taper(1.7, 1.2, 8, 33, 37.5), 1.5)
    bell = P(path((-1.4, 9.6), (1.4, 9.6), qb((3.4, 9.0), (4.0, 3), (6.4, -1.0), 8), (6.4, -1.0), (7.2, -2.0), (-7.2, -2.0), (-6.4, -1.0), qb((-4.0, 3), (-3.4, 9.0), (-1.4, 9.6), 8)))
    k.plate(bell, 4.4, "bell")
    k.plate(rect(-7.4, -2.4, 7.4, -1.4), 5.0, "bell")
    k.plate(rect(-4.2, 5.0, 4.2, 5.7), 4.6, "dark")
    k.plate(ring(0, 10.2, 1.8, 0.9), 2.0, "bell")
    k.grip(-5.2, 0.0, 2.0)
    k.box(0, -6.4, 0, 2.4, 1.3, 2.4, "bell")
    k.box(3.6, -3.4, 0, 0.5, 2.0, 0.5, "dark")
    k.plate(disc(3.6, -4.4, 1.2, 10), 1.8, "pearl")
    k.plate(wave(lambda t: -6.8 - 3.0 * t + 1.1 * math.sin(t * 8), lambda t: 0.8 * (1 - t * 0.7), 3.0, -9.0, 20), 0.6, "kelp")
    k.plate(wave(lambda t: 6.8 + 1.8 * t + 0.8 * math.sin(t * 9), lambda t: 0.7 * (1 - t * 0.7), 1.0, -7.0, 16), 0.6, "kelp")


@design("highwayman_sabre")
def highwayman_sabre(k):
    """a road-agent's sabre: a blackened blade so it won't flash, a stirrup hilt taken off a dead rider, stolen coins hammered
    into the guard and a red sash knotted through it"""
    R = k.theme("brigands_gorge", base=0.4, edge=0.74)
    k.mat(iron=flat(IRON, 0.6), sash=flat(R["wrap"], 0.64, bevel=0.14), coin=flat(GOLD, 0.68))
    m = P(path(qb((-1.6, 3), (-2.6, 17), (6.0, 29), 12), (6.0, 29), qb((6.2, 26.6), (4.6, 13), (2.4, 3), 12)))
    k.forge(m, 1.6, ridge=-0.45)
    k.plate(P(path((-2.6, 3.4), (3.6, 3.4), qb((6.8, 2.8), (6.8, -3.4), (3.4, -5.6), 8), (3.4, -5.6), (-1.0, -5.6), (-1.0, -4.6), (3.2, -4.6), qb((5.6, -3.0), (5.2, 1.6), (3.0, 2.2), 8), (-2.6, 2.2))), 1.8, "iron")
    for x in (0.8, 3.2):
        k.plate(disc(x, 2.8, 0.9, 8), 2.0, "coin")
    k.grip(-4.8, 2.0, 2.0)
    k.plate(P((-2.0, -6.8), (2.0, -6.8), (1.4, -4.8), (-1.4, -4.8)), 2.6, "iron")
    k.box(-2.6, 1.8, 0, 1.6, 1.5, 2.4, "sash")
    k.plate(wave(lambda t: -3.2 - 3.6 * t * t, lambda t: 0.9 + 0.3 * t, 2.2, -7.6, 16) + wave(lambda t: -3.4 - 1.0 * t, lambda t: 0.7, 2.2, -4.4, 10), 0.8, "sash")


@design("red_jacks_sabre")
def red_jacks_sabre(k):
    """the Gorge's king wears his fortune: a blade lacquered blood red, a row of gold coins riveted out past the spine, a
    stolen crown jammed on the pommel and a long ribbon of his colours"""
    R = k.theme("brigands_gorge", base=0.5)
    red = R["wrap"]
    k.mat(blade=steel(ramp("#1a0404", "#2a0606", "#44100a", "#621a10", "#82261a", "#a03424", "#c8503a"), 0.55, 0.14), edge=honed(GOLD, 0.8), coin=flat(GOLD, 0.7),
          ribbon=flat(red, 0.72, bevel=0.14), iron=flat(GOLD, 0.54))
    back = qb((-2.0, 3), (-3.0, 20), (7.0, 31), 14)
    m = P(path(back, (7.0, 31), qb((7.6, 27.6), (5.6, 13), (3.2, 3), 12)))
    k.forge(m, 1.9, ridge=-0.4)
    for j in (2, 4, 6, 8, 10, 12):
        x, y = back[j]
        k.plate(disc(x - 0.5, y + 0.3, 1.5, 12) - disc(x - 0.5, y + 0.3, 0.45, 6), 2.2, "coin")
    k.plate(P(path((-4.6, 2.2), (6.0, 2.2), (7.6, 4.6), (5.0, 3.6), (-3.4, 3.6), (-6.4, 5.6))), 2.8, "iron")
    k.grip(-4.8, 2.3, 2.1)
    crown = P((-3.0, -5.0), (3.0, -5.0), (3.4, -8.8), (1.6, -7.2), (0, -9.6), (-1.6, -7.2), (-3.4, -8.8))
    k.plate(crown, 2.8, "coin")
    k.box(0, -6.2, 0, 3.0, 0.8, 3.2, "ribbon")
    k.plate(wave(lambda t: 2.6 + 7.0 * t * t + 0.9 * math.sin(t * 7), lambda t: 0.9 * (1 - 0.3 * t), 2.0, -11, 22), 0.8, "ribbon")


@design("rook_sabre")
def rook_sabre(k):
    """a sabre filed from a single black flight feather: pale quill up its middle, the vanes cut in slanting barbs, split
    where the wind took them"""
    R = k.theme("rookery", base=0.44, ridge=0.08, edge=0.7)
    k.mat(quill=flat(R["acc"], 0.72, bevel=0.06))
    cx = lambda t: 4.4 * t * t  # noqa: E731
    m = wave(cx, lambda t: 3.4 * math.sin(min(1, t * 1.15 + 0.14) * math.pi) ** 0.5 + 0.5, 3, 31, 34)
    for j in range(9):
        t = 0.14 + j * 0.095
        y = 3 + t * 28
        s_ = 1 if j % 2 else -1
        x = cx(t) + s_ * 3.6
        m = m - L([(x + s_ * 0.8, y + 1.5), (x - s_ * 1.6, y - 1.0)], 0.5)
    k.forge(m, 1.5, step=1)
    k.plate(wave(cx, lambda t: 0.5 * (1 - t * 0.7), 3, 30, 34), 1.8, "quill")
    k.plate(P((-4.2, 2.0), (4.2, 2.0), (5.2, 3.2), (3.0, 3.0), (0, 3.6), (-3.0, 3.0), (-5.2, 3.2)), 2.6, "dark")
    k.grip(-4.8, 2.0, 2.0)
    k.plate(P((-1.6, -5), (1.6, -5), (0.8, -7.0), (0, -9.2), (-0.8, -7.0)), 2.4, "quill")


@design("mothers_pinion")
def mothers_pinion(k):
    """the Mother's torn-off wing, stiffened into a blade: one long primary for the edge and the shorter feathers stepping
    down behind it, each with its own tip; a talon closes round the grip and an unhatched egg sits at the pommel"""
    R = k.theme("rookery", base=0.46, ridge=0.1, edge=0.72)
    k.mat(quill=flat(R["acc"], 0.74, bevel=0.06), egg=flat(R["acc"], 0.82, bevel=0.1), talon=flat(R["dark"], 0.5))
    feathers = ((0.6, 2.6, 3.0, 35.0, 2.6), (-1.2, -1.6, 3.0, 31.0, 2.3), (-2.4, -4.8, 3.0, 26.6, 2.1), (-3.2, -7.2, 3.0, 22.2, 1.9), (-3.8, -8.8, 3.0, 17.6, 1.7))
    for j, (x0, x1, y0, y1, hw) in reversed(list(enumerate(feathers))):
        c = lambda t, a=x0, b=x1: a + (b - a) * t + 2.4 * math.sin(t * math.pi)  # noqa: E731
        f = wave(c, lambda t, h=hw: h * min(1.0, (1 - t) * 3.2 + 0.05), y0, y1, 26)
        k.plate(f, 1.0 + j * 0.0, "edge", z=-0.5 * j * 0.3)
        k.plate(f.inset(0.5), 1.6, "blade", z=-0.5 * j * 0.3, tag="blade")
        k.plate(wave(c, lambda t: 0.3, y0, y1 - 1, 26), 1.7, "quill", z=-0.5 * j * 0.3)
    k.box(-0.8, 1.8, 0, 9.4, 2.2, 3.2, "dark")
    for x, ln in ((-3.4, 4.4), (-1.0, 4.8), (1.6, 4.2)):
        k.plate(P(path(qb((x - 0.9, 2.4), (x - 1.4, -1.0), (x + 0.6, 2.4 - ln), 6), (x + 0.6, 2.4 - ln), qb((x + 0.2, -0.2), (x + 0.2, 1), (x + 0.9, 2.4), 6))), 2.8, "talon")
    k.grip(-4.8, 1.9, 2.1)
    k.plate(disc(0, -7.2, 2.2, 12) + disc(0, -6.0, 1.7, 10), 3.0, "egg")
    k.inlay(L([(-0.8, -5.0), (0.2, -6.6), (-0.4, -7.6), (0.8, -9.0)], 0.4), 3.0, "glow", glow=True)


@design("ringmaster_rapier")
def ringmaster_rapier(k):
    """the magician's finish: a long thin rapier rises out of a top hat turned up for a guard, a red band round it, stars
    painted on, a white-tipped wand for the pommel"""
    R = k.theme("hollow_circus", base=0.6)
    hat = ramp("#08060c", "#121016", "#1c1822", "#2a2432", "#3e3648")
    k.mat(hat=flat(hat, 0.56, bevel=0.14), band=flat(R["wrap"], 0.6), gold=flat(GOLD, 0.66), white=flat(R["acc"], 0.9, bevel=0.04), wand=flat(hat, 0.5))
    k.forge(taper(1.1, 0.8, 8, 34, 38.0), 1.3)
    k.plate(P((-3.4, 0.6), (3.4, 0.6), (4.4, 8.0), (-4.4, 8.0)), 4.4, "hat")
    k.plate(rect(-7.6, 8.0, 7.6, 9.2), 6.0, "hat")
    k.plate(P((-3.9, 5.0), (3.9, 5.0), (4.2, 7.2), (-4.2, 7.2)), 4.6, "band")
    k.inlay(disc(-1.5, 3, 0.7, 5) + disc(1.5, 2.2, 0.5, 5), 4.4, "gold")
    k.grip(-4.6, 0.8, 1.8)
    k.box(0, -5.6, 0, 2.4, 1.2, 2.4, "gold")
    k.box(0, -8.6, 0, 1.0, 3.2, 1.0, "wand")
    k.box(0, -10.0, 0, 1.1, 1.6, 1.1, "white")


@design("reedblade")
def reedblade(k):
    """a sheaf of marsh reed bound hard and tarred, a sliver of bog iron let into the top; a bulrush head left on and a leaf
    trailing. A witch's idea of a sword"""
    R = k.theme("mirefen_coven", base=0.5)
    reed = ramp("#3a3414", "#5a5220", "#7c7230", "#a09844", "#c4bc60", "#e0d88c")
    k.mat(reed=staves(reed, 1.5, 0.56), rush=flat(ramp("#1a0e08", "#2c1a10", "#442a1a", "#5e3c24", "#7a5232"), 0.56, 0.3), bind=wrap(R["dark"] if "dark" in R else reed, reed[0], 3),
          leaf=flat(R["wrap"], 0.6))
    k.plate(rect(-2.25, 3, 2.25, 21) + P((-2.25, 21), (2.25, 21), (1.5, 24), (0.75, 22), (-0.75, 25), (-1.5, 23)), 2.2, "reed")
    k.forge(P((-1.1, 22), (1.1, 22), (1.3, 28), (0, 33), (-1.2, 28)), 1.4)
    for y in (5.0, 12.0, 19.0):
        k.box(0, y, 0, 5.0, 1.2, 2.6, "bind")
    k.plate(wave(lambda t: 3.5, lambda t: 1.2 * min(1, (1 - t) * 6, t * 6 + 0.3), 13.5, 21, 12), 1.8, "rush")
    k.box(3.5, 21, 0, 0.5, 3.6, 0.5, "reed")
    k.plate(L([(2.2, 8), (3.4, 8.8)], 0.5), 0.6, "reed")
    k.plate(wave(lambda t: -2.4 - 6 * t * t, lambda t: 0.9 * math.sin(min(1, t * 1.05 + 0.04) * math.pi), 6, 22, 16), 0.5, "leaf")
    k.grip(-4.8, 3.0, 2.2, "bind")
    k.box(0, -6.8, 0, 2.6, 2.0, 2.6, "reed")


@design("matrons_sickle")
def matrons_sickle(k):
    """the Matron's harvest: a full moon sickle, thin and enormous, its inner edge burning hex-green; bones and a little
    skull swing from the tang on cord"""
    R = k.theme("mirefen_coven", base=0.42, edge=0.72)
    k.mat(bone=bone(R["acc"], 0.7), cord=flat(R["wrap"], 0.56), hot=fire(R["glow"], 0.4, 0.6))
    out = qb((-1.4, 3), (-11.4, 24), (11.0, 30.6), 18)
    inn = qb((11.0, 30.6), (-5.6, 21), (1.8, 3), 18)
    m = P(path(out, inn))
    k.plate(m, 1.0, "hot", glow=True, tag="edge")
    k.plate(P(path(out, qb((11.0, 30.6), (-7.8, 21.6), (0.4, 3), 18))), 2.0, "blade", ridge=-0.2, tag="blade")
    for t in (0.35, 0.6, 0.8):
        q = out[int(t * 18)]
        k.plate(disc(q[0] + 1.6, q[1] - 0.8, 0.5, 6), 2.1, "glow", glow=True)
    k.box(0.2, 1.6, 0, 5.4, 1.8, 3.0, "bone")
    k.grip(-5.2, 1.7, 2.1)
    k.plate(disc(0, -6.8, 1.9, 10), 2.6, "bone")
    k.box(2.0, -1.8, 0, 0.5, 3.4, 0.5, "cord")
    k.plate(rect(1.2, -3.8, 2.8, -2.0) + rect(1.6, -4.4, 2.4, -3.8), 1.6, "bone")
    k.inlay(rect(1.4, -3.0, 1.8, -2.6) + rect(2.2, -3.0, 2.6, -2.6), 1.6, "hot", glow=True)
    k.box(-2.1, -3.8, 0, 0.5, 5.4, 0.5, "cord")
    k.plate(L([(-2.1, -3.8), (-1.6, -6.4)], 0.8), 1.0, "bone")


@design("khopesh")
def khopesh(k):
    """the old kings' sickle-sword: a bronze bar that bends hard and swells into a hooked moon, faience bands inlaid across
    it, the hilt cast in one piece with the blade"""
    R = k.theme("sandsunk_tomb", base=0.54)
    lapis = ramp("#081a4a", "#0e2a6e", "#163e96", "#2458c0", "#4a84e0")
    bronze = ramp("#2a1606", "#432410", "#5e3618", "#7c4c22", "#9c6630", "#bc8444", "#d8a462", "#f0c88a")
    k.mat(blade=steel(bronze, 0.56, 0.12), edge=honed(GOLD, 0.8), lapis=flat(lapis, 0.6, bevel=0.1), gold=flat(GOLD, 0.62))
    m = P(path((-1.2, 3), (1.4, 3), (1.4, 12), qb((1.4, 12), (9.0, 13), (10.2, 21), 10), (10.2, 21), qb((9.6, 23.6), (4.0, 29), (-3.6, 25.0), 12), (-3.6, 25.0), (-1.0, 23.2), qb((1.0, 25.4), (6.6, 23), (4.4, 17.6), 8), qb((4.4, 17.6), (2.0, 15.6), (-1.2, 15.4), 6)))
    k.forge(m, 1.7, ridge=0.0)
    for y in (4.5, 7.5, 10.5):
        k.inlay(rect(-1.2, y, 1.4, y + 1.0), 1.7, "lapis")
    k.plate(P((-2.2, 1.6), (2.4, 1.6), (1.8, 3.0), (-1.6, 3.0)), 2.2, "gold")
    k.grip(-4.6, 1.8, 2.0, "lapis")
    k.plate(P((-1.4, -4.6), (1.4, -4.6), (2.6, -7.6), (0.6, -6.4), (-0.6, -6.4), (-2.6, -7.6)), 2.2, "gold")


@design("sunflayer")
def sunflayer(k):
    """the sun god's skinning knife grown to a sword: gold rays stand round a lapis disc for its guard, a gilded leaf of a
    blade comes up through the sun with a flaying hook on its back and a scarab sits on the pommel"""
    R = k.theme("sandsunk_tomb", base=0.6)
    lapis = ramp("#081a4a", "#0e2a6e", "#163e96", "#2458c0", "#4a84e0")
    k.mat(blade=steel(GOLD, 0.56, 0.14), edge=honed(ramp("#a06018", "#d8982c", "#f6d060", "#fff0b0", "#ffffff"), 0.7), lapis=flat(lapis, 0.56, bevel=0.1), gold=flat(GOLD, 0.66),
          sun=fire(ramp("#e07010", "#ffa81c", "#ffd84a", "#fff4a8"), 0.3, 0.7), bug=flat(ramp("#04181a", "#082c30", "#104a4e", "#1c7070", "#38a09a"), 0.6, bevel=0.2))
    m = wave(lambda t: 0.0, lambda t: 2.0 + 2.6 * math.sin(t * math.pi) ** 1.4 - 0.2 * t, 6, 32.4, 26)
    m = m + P((0, 30), (0, 34.4), (-3.4, 36), (-1.8, 33.8), (-5.2, 29.6), (-2.0, 30))
    k.forge(m, 1.8)
    k.inlay(L([(0, 12), (0, 27)], 0.8), 1.8, "lapis")
    rays = Mask()
    for j in range(16):
        a = 2 * math.pi * (j + 0.5) / 16
        ln = 10.6 if j % 2 else 8.8
        rays = rays + P((math.cos(a - 0.15) * 5, 5.6 + math.sin(a - 0.15) * 5), (math.cos(a) * ln, 5.6 + math.sin(a) * ln), (math.cos(a + 0.15) * 5, 5.6 + math.sin(a + 0.15) * 5))
    k.plate(rays, 1.4, "sun", glow=True)
    k.plate(disc(0, 5.6, 5.8) - disc(0, 5.6, 4.0), 2.6, "gold")
    k.plate(disc(0, 5.6, 4.2), 2.2, "lapis")
    k.grip(-4.8, 1.0, 2.0, "lapis")
    k.plate(P(path(qb((-2.0, -5.0), (-3.0, -8.0), (0, -9.4), 6), qb((0, -9.4), (3.0, -8.0), (2.0, -5.0), 6))), 2.8, "bug")
    k.inlay(L([(0, -5.2), (0, -9.2)], 0.4), 2.8, "gold")
