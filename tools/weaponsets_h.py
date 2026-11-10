"""Two-handers: a long grip from y -10 to 4, blades up to y 38 and as wide as they like. The six animated old boss greatswords
(tidebreaker, thornmother, gravewardens_oath, starfell_edge, brasshog_cleaver, kilnheart) stay as they were."""
import math

from voxsword import ramp
from weaponsets import design, qb, path, P, L, disc, ring, rect, wave, taper, Mask, flat, fire, heat, staves, steel, honed, bone, gem, at, lit, wrap, stripes, facet_of
from weaponsets_a import BRASS, GOLD, IRON, LEATHER
from weaponsets_c import shard
from weaponsets_d import RUBY, SILVER, feathers, links, stroke
from weaponsets_e import CORK, HORN, IVORY, RAG

HOT = ramp("#a02206", "#e04a0a", "#ff8a1c", "#ffc84a", "#fff0b0")


def long_grip(k, top=3.6, w=2.4, mat="wrap", bottom=-9.6):
    k.box(0, bottom, 0, w, top - bottom, w, mat, tag="grip")


@design("stave_cleaver")
def stave_cleaver(k):
    """a butcher's blade built like a barrel: oak staves side by side, iron hoops round them, the edge one long strip of hoop iron sharpened"""
    R = k.theme("cellar", base=0.5)
    k.mat(stave=staves(R["wood"], 2.0, 0.6), hoop=flat(R["dark"], 0.56), rim=honed(R["blade"], 0.8))
    m = P((-5, 5), (5, 5), (6, 33), (-4.4, 35))
    k.plate(m, 2.2, "stave")
    k.plate(m - P((-9, 0), (4, 0), (4.8, 40), (-9, 40)), 2.6, "rim")
    for y in (8, 19, 30):
        k.box(0.2, y, 0, 11.8, 1.3, 2.9, "hoop")
    k.box(0, 3.6, 0, 12.0, 1.8, 3.2, "hoop")
    long_grip(k)
    k.box(0, -11.4, 0, 3.2, 2.2, 3.2, "hoop")


@design("gibbet_greatblade")
def gibbet_greatblade(k):
    """a post from the old gibbet, axed flat and shod with iron, a ragged hemp noose knotted where a crossguard ought to go"""
    R = k.theme("gallows", base=0.44, edge=0.74)
    k.mat(oak=staves(R["wood"], 2.4, 0.54), hemp=wrap(R["wrap"], R["dark"][0], 4), rope=flat(R["acc"], 0.6))
    m = P((-3.6, 5), (3.6, 5), (3.8, 31), (-0.4, 37), (-3.8, 31))
    k.plate(m, 1.2, "edge")
    k.plate(m.inset(1.0), 2.8, "oak")
    for y in (10, 18, 26):
        k.plate(rect(-3.4, y, 3.4, y + 1.1), 3.0, "dark")
        k.box(0, y + 0.1, 0, 0.9, 0.9, 3.2, "edge")
    k.plate(rect(-4.4, 3.4, 4.4, 6.4), 3.6, "hemp")
    k.plate(ring(5.4, 0.2, 3.4, 2.3), 1.1, "rope")
    k.box(5.0, 3.0, 0, 1.0, 2.2, 1.0, "hemp")
    long_grip(k, mat="hemp", top=3.4)
    k.box(0, -11.6, 0, 3.4, 2.4, 3.4, "dark")


@design("last_drop")
def last_drop(k):
    """the headsman's axe the Hill is named for: a tall bearded crescent on a black pole, one drop-shaped window cut in the cheek and a bead of ember hanging in it"""
    R = k.theme("gallows", base=0.42, edge=0.8)
    k.mat(hemp=wrap(R["wrap"], R["dark"][0], 4), pole=flat(R["wood"], 0.6, bevel=0.06), iron=flat(R["blade"], 0.6, bevel=0.14))
    k.box(0, -12, 0, 2.4, 44, 2.4, "pole")
    long_grip(k, 0, mat="hemp")
    m = P(path((1, 21), qb((8, 20), (14, 14), (15.4, 8), 10), (15.4, 8), qb((19, 18), (19, 28), (14.6, 38), 12), (14.6, 38), qb((12, 32), (8, 31), (1, 30), 10)))
    drop = P(path((8.2, 28), qb((5.6, 24.6), (7, 21.8), (8.2, 21.8), 6), qb((9.4, 21.8), (10.8, 24.6), (8.2, 28), 6)))
    k.forge(m - drop, 2.0, step=2, ridge=-0.3)
    k.plate(drop, 1.0, "glow", glow=True)
    k.box(0.4, 19.6, 0, 3.8, 12.6, 3.4, "iron")
    k.plate(P((-1, 29), (-1, 22), (-7, 26), (-8.4, 30), (-5, 28)), 1.6, "iron")
    k.box(0, 32, 0, 3.0, 1.4, 3.0, "iron")
    k.box(0, -13.2, 0, 3.0, 1.6, 3.0, "iron")


@design("antler_greatblade")
def antler_greatblade(k):
    """the stag that ruled the Rotwood: its whole rack bound into one branching blade, the main beam straight up, tines jutting in pairs, moss in every fork"""
    R = k.theme("rotwood", base=0.5)
    k.mat(bone=bone(R["blade"], 0.68), edgeb=flat(R["blade"], 0.86, bevel=0.06), moss=flat(R["wrap"], 0.6), hot=fire(R["glow"], 0.3, 0.6))
    m = P(path(qb((-3.2, 4), (-4.2, 22), (0.6, 38), 12), (0.6, 38), qb((4.2, 22), (3.2, 12), (3.2, 4), 10)))
    for y, ln, c in ((11, 8.6, 4), (16, 8.4, 5), (21, 7.4, 4.6), (26, 6, 3.6), (30, 4.6, 3)):
        for s_ in (1, -1):
            yy = y + (1.6 if s_ < 0 else 0)
            m = m + stroke((s_ * 2.4, yy - 1.8), (s_ * (2.6 + c), yy - 1.4), (s_ * (2.4 + ln), yy + 4.0), 1.5 - y * 0.02)
    k.plate(m, 1.6, "edgeb")
    k.plate(m.inset(0.5), 2.6, "bone")
    k.plate(rect(-3.4, 3, 3.4, 7), 3.2, "moss")
    k.plate(disc(0, 5.2, 1.4, 8), 3.4, "hot", glow=True)
    long_grip(k)
    k.plate(disc(0, -11.2, 2.6, 8), 3.0, "edgeb")


@design("candlewake")
def candlewake(k):
    """the Crypt's night watch in one sword: a row of living candles stands along the blade's back, wax sheeting down it, the guard another drip pan"""
    R = k.theme("crypt", base=0.5)
    k.mat(wax=flat(R["acc"], 0.72, bevel=0.1), flame=fire(R["glow"], 0.4, 0.6), silver=flat(R["blade"], 0.56))
    m = P((-3.4, 5), (4.4, 5), (4.8, 30), (1.4, 37), (-3.0, 31))
    k.forge(m, 2.0, ridge=0.1)
    for y, h in ((10, 5), (16.6, 4), (22.6, 5), (29, 3.4)):
        k.plate(rect(-6.4, y - 0.6, -2.8, y + 0.2), 2.2, "silver")
        k.plate(rect(-5.6, y, -3.8, y + h), 2.0, "wax")
        k.plate(P(path(qb((-4.7, y + h), (-6.2, y + h + 1.4), (-4.7, y + h + 3.4), 5), qb((-4.7, y + h + 3.4), (-3.2, y + h + 1.4), (-4.7, y + h), 5))), 1.2, "flame", glow=True)
    k.plate(P((-3.6, 4.4), (5, 4.4), (5.0, 11), (3.6, 8), (2.6, 13.6), (0.8, 8.4), (-0.4, 11.4), (-3.2, 7.6)), 2.6, "wax")
    k.plate(P((-7.4, 3.2), (7.4, 3.2), (8.4, 4.8), (-8.4, 4.8)), 3.8, "dark")
    long_grip(k)
    k.plate(disc(0, -11, 2.2, 10) - disc(0, -11, 1.0, 8), 2.4, "dark")


@design("plague_amputator")
def plague_amputator(k):
    """for when the saw is too slow: a square-ended surgical cleaver with a blood gutter, tooth-backed, gauze hanging from the grip and a brass tourniquet screw for a guard"""
    R = k.theme("plague", base=0.56)
    k.mat(brass=flat(R["dark"], 0.62), gauze=flat(R["wrap"], 0.72, bevel=0.06))
    teeth = []
    y = 5.0
    while y < 32:
        teeth += [(-3.4, y), (-5.0, y + 0.3), (-3.4, y + 1.8)]
        y += 2.0
    m = P([(-3.4, 5), (5.4, 5), (6.4, 30), (5.0, 34.4), (-3.4, 33.6)] + teeth[::-1])
    k.forge(m, 1.8, ridge=-0.3)
    k.inlay(L([(1.0, 7), (1.2, 30)], 1.0), 1.8, "dark")
    k.inlay(L([(1.0, 8), (1.0, 20)], 0.5), 1.9, "glow", glow=True)
    k.plate(rect(-5.6, 3.2, 7.2, 5.0), 2.8, "brass")
    k.plate(rect(6.4, 2.0, 8.6, 6.2) + rect(8.6, 3.6, 10.4, 4.6) + rect(10.0, 1.8, 11.0, 6.4), 1.6, "brass")
    long_grip(k)
    k.plate(P((-1.4, 1), (-4.0, -3.8), (-2.4, -3), (-2.8, -6.6), (-1.0, -3.0)), 0.5, "gauze")
    k.box(0, -11.4, 0, 3.0, 2.0, 3.0, "brass")


@design("faceless_greatsword")
def faceless_greatsword(k):
    """a slab of pale temple stone cut to a sword: tall, square-shouldered, three blank faces rising up the middle of it, each a little more worn away"""
    R = k.theme("temple", base=0.72, ridge=0.08)
    k.mat(face=flat(R["blade"], 0.88, bevel=0.06), gold=flat(R["acc"], 0.64))
    k.forge(P((-5.2, 5), (5.2, 5), (4.4, 31), (0, 38), (-4.4, 31)), 2.2)
    for j, (y, w) in enumerate(((10, 3.2), (18, 2.7), (25.6, 2.1))):
        h = w * 1.9
        f = P(path(qb((-w, y + h), (-w * 1.2, y), (0, y - h * 0.25), 6), qb((0, y - h * 0.25), (w * 1.2, y), (w, y + h), 6), qb((w, y + h), (0, y + h * 1.3), (-w, y + h), 6)))
        k.plate(f, 2.7, "face")
        if j < 2:
            k.plate(rect(-w * 0.7, y + h * 0.55, -w * 0.2, y + h * 0.65) + rect(w * 0.2, y + h * 0.55, w * 0.7, y + h * 0.65), 2.8, "dark")
    k.plate(P((-8, 3.2), (8, 3.2), (9, 5), (-9, 5)), 3.4, "gold")
    long_grip(k)
    k.plate(rect(-2, -12, 2, -9.4), 3.0, "face")


@design("bonewright_greatblade")
def bonewright_greatblade(k):
    """a ribcage made a weapon: a long sternum for the blade with rib after rib curving up off both sides, a pelvis for the guard, brass-riveted"""
    R = k.theme("ossuary", base=0.5)
    k.mat(bone=bone(R["acc"], 0.68), edgeb=flat(R["acc"], 0.88, bevel=0.06), brass=flat(R["dark"], 0.62))
    k.plate(P((-2.4, 5), (2.4, 5), (2.0, 33), (0, 39), (-2.0, 33)), 2.8, "bone")
    for j in range(8):
        y = 7.6 + j * 3.3
        ln = 9.0 - j * 0.5
        for s_ in (1, -1):
            k.plate(stroke((s_ * 2, y), (s_ * (2 + ln * 0.8), y + 0.4), (s_ * (2 + ln), y + 5.6), 1.1, 8), 1.5, "edgeb")
        k.box(0, y - 0.1, 0, 5.6, 0.7, 3.1, "brass")
    k.plate(P(path((-2.4, 5), (2.4, 5), qb((9.6, 7), (10.6, 3.6), (8, 1.6), 6), (8, 1.6), (3, 3.2), (-3, 3.2), qb((-8, 1.6), (-10.6, 3.6), (-9.6, 7), 6))), 3.0, "bone")
    k.plate(disc(-5.4, 4.2, 1.2, 8) + disc(5.4, 4.2, 1.2, 8), 3.2, "dark")
    long_grip(k)
    k.plate(disc(0, -11.2, 2.4, 10), 3.0, "bone")
    k.plate(disc(-0.9, -10.8, 0.6, 6) + disc(0.9, -10.8, 0.6, 6), 3.1, "glow", glow=True)


@design("kiln_greatsword")
def kiln_greatsword(k):
    """a pour of slag frozen on the way out of the crucible: an open channel runs the length of a stepped black blade with the metal still liquid in it"""
    R = k.theme("foundry", base=0.42, ridge=0.08, edge=0.7)
    m = P((-5, 5), (5, 5), (5.6, 13), (4.6, 13.6), (5.2, 21), (4.0, 21.6), (4.4, 29), (2.6, 30), (0, 38), (-2.6, 30), (-4.4, 29), (-4.0, 21.6), (-5.2, 21), (-4.6, 13.6), (-5.6, 13))
    k.forge(m, 2.6)
    ch = wave(lambda t: 0.5 * math.sin(t * 7), lambda t: 1.6 - 1.0 * t, 5, 33, 20)
    k.plate(ch, 2.66, "glow", glow=True)
    k.plate(L([(-3.6, 8), (-3.6, 16)], 0.6) + L([(3.6, 12), (3.4, 24)], 0.6), 2.66, "dark")
    k.plate(P((-8.4, 3), (8.4, 3), (9.4, 5.4), (-9.4, 5.4)), 3.6, "dark")
    for x in (-6.4, 6.4):
        k.box(x, 3.4, 0, 1.2, 1.2, 3.9, "edge")
    long_grip(k)
    k.box(0, -12, 0, 3.6, 2.8, 3.6, "dark")
    k.box(0, -11.2, 0, 1.6, 1.2, 3.8, "glow", glow=True)


@design("procession_greatsword")
def procession_greatsword(k):
    """carried at the head of the dead march: long as a man, fluted, a hanging crossbar with icicles, a snow crystal set where the blade meets the hilt"""
    R = k.theme("frost", base=0.54)
    k.mat(ice=flat(R["glow"], 0.7, bevel=0.14), white=flat(R["glow"], 0.92, bevel=0.04), silver=flat(R["blade"], 0.68), red=flat(R["acc"], 0.6))
    k.forge(P((-3.2, 6), (3.2, 6), (2.6, 34), (0, 42), (-2.6, 34)), 1.9)
    k.inlay(rect(-1.2, 8, -0.6, 30) + rect(0.6, 8, 1.2, 30), 1.9, "dark")
    k.plate(rect(-9.4, 4.4, 9.4, 6), 3.0, "silver")
    for x, ln in ((-8.4, 4), (-6, 6.4), (-3.4, 3.6), (3.4, 4.6), (6, 7), (8.4, 3.6)):
        k.plate(P((x - 0.8, 4.4), (x + 0.8, 4.4), (x, 4.4 - ln)), 1.2, "ice")
    for a in (0, 60, 120):
        r = math.radians(a)
        c, s_ = math.cos(r) * 3.6, math.sin(r) * 3.6
        k.plate(L([(-c, 11 - s_), (c, 11 + s_)], 0.8), 2.2, "white")
    long_grip(k, 4.4)
    k.plate(shard(0, -9.4, 5, 180, 2.8), 2.2, "ice")


@design("folio_cleaver")
def folio_cleaver(k):
    """an entire folio bound to a steel spine, its pages fanned open and hardened into a stepped blade, ink lines still legible along each one"""
    R = k.theme("silk", base=0.56)
    k.mat(page=flat(R["acc"], 0.74, bevel=0.1), pagedark=flat(R["acc"], 0.56, bevel=0.1), cover=flat(R["wrap"], 0.56, bevel=0.1), brass=flat(BRASS, 0.64), ink=flat(R["dark"], 0.5), hot=fire(R["glow"], 0.1, 0.8))
    for j in range(7):
        x0 = -3.2 + j * 1.0
        top = 37 - j * 2.2
        m = P((x0 - 1, 5), (x0 + 1.4 + j * 0.5, 5), (x0 + 2.6 + j * 0.7, top - 2), (x0 + 1.0 + j * 0.5, top), (x0 - 1, top - 1))
        k.plate(m, 0.7, "page" if j % 2 else "pagedark", z=-1.4 + j * 0.4)
    k.plate(rect(-5.4, 4, -3.0, 39), 3.8, "cover")
    for y in (5, 19, 33):
        k.box(-4.2, y, 0, 3.0, 1.4, 4.0, "brass")
    for y in (10, 14, 18, 22):
        k.plate(rect(-1.4, y, 6 - (y - 10) * 0.1, y + 0.4), 3.0, "ink")
    k.plate(rect(-1.4, 26, 3.6, 26.5), 3.0, "hot", glow=True)
    k.plate(rect(-6.6, 3.2, 9, 5.2), 3.4, "cover")
    long_grip(k)
    k.box(0, -11.2, 0, 3.0, 1.8, 3.0, "brass")


@design("widowmaker")
def widowmaker(k):
    """the Queen's own: a flamberge of black chitin, each wave ending in a leg-barb, a blood-red hourglass burning at its root"""
    R = k.theme("silk", base=0.44)
    k.mat(blade=steel(R["dark"], 0.62, 0.16), edge=honed(R["blade"], 0.66), red=fire(ramp("#7a0c1e", "#c01a30", "#ff3b52", "#ffb0b8"), 0.3, 0.6), leg=flat(R["dark"], 0.76, bevel=0.2))
    c = lambda t: 1.8 * math.sin(t * 19)  # noqa: E731
    m = wave(c, lambda t: 4.2 * (1 - t ** 3) + 0.15, 6, 40, 60)
    for j in range(6):
        t = 0.16 + j * 0.14
        y = 6 + t * 34
        s_ = 1 if j % 2 else -1
        x = c(t) + s_ * 4.0 * (1 - t ** 3)
        m = m + P((x - s_ * 0.8, y - 1.4), (x + s_ * 3.0, y + 2.4), (x - s_ * 0.6, y + 0.8))
    k.forge(m, 2.0, step=2)
    k.plate(P((-2.2, 19), (2.2, 19), (0.3, 15), (2.2, 11), (-2.2, 11), (-0.3, 15)), 2.06, "red", glow=True)
    for j, (a, b, c_) in enumerate((((2, 4.4), (9, 8), (11, 1)), ((2, 3.8), (7, 2.4), (8.4, -5)), ((2, 5), (7, 12), (11.6, 10)))):
        for s_ in (1, -1):
            k.plate(L(qb((s_ * a[0], a[1]), (s_ * b[0], b[1]), (s_ * c_[0], c_[1]), 8) + [(s_ * c_[0], c_[1])], 1.0), 1.3, "leg")
    k.plate(disc(0, 4, 3.0, 10), 3.4, "leg")
    long_grip(k)
    k.plate(disc(0, -11.4, 2.4, 10), 3.0, "leg")


@design("tunnel_cleaver")
def tunnel_cleaver(k):
    """a coal shovel somebody has been sharpening for thirty years: broad square scoop on a pit-prop handle, the lamp still hooked on and the crystal starting to take it"""
    R = k.theme("weeping_mine", base=0.5)
    k.mat(copper=flat(R["acc"], 0.6), crystal=flat(R["glow"], 0.7, bevel=0.14), lamp=fire(R["glow"], 0.4, 0.6))
    m = P((-5.4, 8), (5.4, 8), (5.8, 32), (4.6, 34), (-4.6, 34), (-5.8, 32))
    k.forge(m, 1.5)
    k.plate(P((-1.8, 4), (1.8, 4), (2.4, 20), (0, 22), (-2.4, 20)), 2.3, "dark")
    for s_ in (1, -1):
        k.plate(rect(s_ * 4.8 - 0.5, 8, s_ * 4.8 + 0.5, 32), 2.2, "dark")
    k.plate(shard(4, 12, 7, -28, 2.6) + shard(-4, 26, 6.4, 40, 2.4) + shard(-5.2, 22, 4.6, 62, 2.0), 2.2, "crystal")
    k.plate(rect(-2.4, 3.4, 2.4, 5.6), 3.0, "copper")
    long_grip(k, 4, mat="wood", w=2.6)
    k.box(0, -3.6, 0, 3.0, 8, 3.0, "wrap")
    k.plate(stroke((1, 2.6), (5, 3.2), (5, 0.4), 0.5), 0.6, "dark")
    k.plate(rect(3.8, -3.2, 6.2, 0.4), 2.2, "lamp", glow=True)
    k.box(0, -11.2, 0, 3.2, 1.8, 3.2, "copper")


@design("keel_greatblade")
def keel_greatblade(k):
    """a section of the drowned ship: the keel timber shod in iron along its edge, three ribs still standing off it, weed and barnacles, a figurehead's face for a pommel"""
    R = k.theme("tide_chapel", base=0.5)
    k.mat(oak=staves(R["wood"], 2.0, 0.56), crust=flat(R["acc"], 0.72, bevel=0.1), kelp=flat(R["wrap"], 0.56), rib=flat(R["wood"], 0.5, bevel=0.14))
    m = P(path((-3.6, 5), qb((-5.0, 22), (-1.0, 32), (2.4, 38), 10), (2.4, 38), qb((6.6, 26), (6, 14), (4.8, 5), 10)))
    k.plate(m, 1.0, "edge")
    k.plate(m - P(path(qb((5.4, 2), (7.4, 26), (2.4, 40), 10), (20, 40), (20, 2))), 2.8, "oak")
    for y, ln in ((12, 7), (19, 7.6), (26, 6)):
        k.plate(stroke((-3, y), (-3 - ln * 0.9, y + 0.6), (-3 - ln, y + 6), 1.3), 1.8, "rib")
    for x, y, r_ in ((-3.2, 9.2, 1.0), (0.4, 16, 0.8), (-2.4, 23, 0.9), (1.4, 28.6, 0.8)):
        k.plate(disc(x, y, r_, 8) - disc(x, y, 0.3, 6), 3.2, "crust")
    k.plate(wave(lambda t: -11 + 1.0 * math.sin(t * 7), lambda t: 0.8, 21, 8, 12), 0.5, "kelp")
    k.plate(rect(-6.4, 3.2, 6.6, 5.4), 3.4, "dark")
    long_grip(k)
    k.plate(P(path(qb((-2.4, -9.4), (-2.8, -13), (0, -14.4), 6), qb((0, -14.4), (2.8, -13), (2.4, -9.4), 6))), 2.8, "crust")
    k.plate(rect(-1.5, -11.6, -0.5, -11.1) + rect(0.5, -11.6, 1.5, -11.1), 2.9, "dark")


@design("ogre_cleaver")
def ogre_cleaver(k):
    """what an ogre uses for carving: a door of pitted steel, hole at the top to hang it, a bent meat hook through that, a rope grip for hands that size"""
    R = k.theme("brigands_gorge", base=0.46, scars=0.08, edge=0.74)
    k.mat(iron=flat(IRON, 0.7), rope=wrap(R["acc"], R["dark"][0], 4))
    m = P((-5.4, 6), (5.4, 6), (7.8, 30), (5.4, 34.6), (-5, 35), (-6.4, 32)) - disc(-2.2, 31, 1.4, 10)
    m = m - P((8, 20), (5.2, 21), (8, 22.6)) - P((6.4, 12), (4.8, 12.8), (6.4, 14))
    k.forge(m, 2.0, ridge=-0.4)
    k.plate(stroke((-2.2, 32.4), (-7, 33), (-8.4, 27), 0.9) + P((-8.8, 27), (-7.8, 27), (-9.4, 24.4)), 1.2, "iron")
    k.plate(rect(-3, 3.8, 3, 6.6), 3.2, "iron")
    long_grip(k, mat="rope", w=2.8)
    k.box(0, -11.4, 0, 3.6, 2.2, 3.6, "iron")


@design("ransom")
def ransom(k):
    """Red Jack's demand: a heavy sabre-cleaver with a ransom note spiked to it, a padlock and shackle through the blade and a bag of somebody's coin dangling"""
    R = k.theme("brigands_gorge", base=0.5)
    k.mat(blade=steel(ramp("#1a0404", "#2a0606", "#44100a", "#621a10", "#82261a", "#a03424", "#c8503a"), 0.55, 0.14), edge=honed(GOLD, 0.8), paper=flat(ramp("#a89878", "#c8b898", "#e0d2b4", "#f0e6cc"), 0.7, bevel=0.06), ink=flat(ramp("#2a1408", "#3a1e10"), 0.5), lock=flat(GOLD, 0.6, bevel=0.14), iron=flat(IRON, 0.7), bag=flat(LEATHER, 0.72, bevel=0.14), coin=flat(GOLD, 0.8))
    m = P(path(qb((-3.4, 5), (-4.4, 22), (6.0, 38), 12), (6.0, 38), qb((9.8, 32), (9, 16), (5.2, 5), 12)))
    k.forge(m - disc(2.6, 26, 1.2, 8), 2.0, ridge=-0.3)
    k.plate(P((-2.6, 12), (4.6, 11.4), (4.8, 20.4), (2.6, 19.6), (-2.4, 20.8)), 2.2, "paper")
    k.plate(rect(-1.6, 18, 3.4, 18.5) + rect(-1.6, 16.4, 2.4, 16.9) + rect(-1.6, 14.8, 3.2, 15.3) + rect(1.6, 12.8, 3.6, 13.8), 2.26, "ink")
    k.box(1.0, 20, 0, 1.0, 1.0, 2.8, "iron")
    k.plate(ring(2.6, 25.4, 2.2, 1.3), 1.0, "iron")
    k.plate(rect(0.6, 21, 4.6, 24.4), 2.6, "lock")
    k.plate(disc(2.6, 22.6, 0.5, 6), 2.8, "ink")
    k.plate(P((-4.6, 3.2), (7.4, 3.2), (9.0, 5.4), (-5.4, 5.4)), 3.0, "lock")
    long_grip(k)
    k.box(0, -11.2, 0, 3.0, 1.8, 3.0, "lock")
    links(k, [(8.0, 3.2), (8.4, 1.0), (8.0, -1.2)], "iron", 0.9)
    k.plate(disc(8.0, -3.8, 2.6, 10), 3.0, "bag")
    k.box(8.0, -1.6, 0, 2.8, 0.7, 2.8, "coin")


@design("wingblade")
def wingblade(k):
    """one sweep of an enormous black wing: a long single edge along the leading bone, primaries stepping back behind it, a claw at the wrist for a hook"""
    R = k.theme("rookery", base=0.42, edge=0.74)
    k.mat(bone=bone(R["acc"], 0.68), feather=flat(R["blade"], 0.44, bevel=0.14), f2=flat(R["blade"], 0.6, bevel=0.14), talon=flat(HORN, 0.6))
    for j in range(8):
        x = -2.6 - j * 1.8
        top = 34 - j * 3.3
        f = P(path((x + 2, 6), qb((x - 1.4, top * 0.6), (x - 1.6, top * 0.8), (x - 2.8, top), 6), (x - 2.8, top), qb((x + 1.8, top * 0.8), (x + 2.2, top * 0.6), (x + 3.4, 6), 6)))
        k.plate(f, 1.4 - j * 0.04, "f2" if j % 2 else "feather", z=-0.2 * j)
    m = P(path((-2.6, 5), qb((-3.6, 24), (3.0, 38), (5.0, 42), 12), (5.0, 42), qb((6.4, 30), (4.0, 16), (3.2, 5), 12)))
    k.forge(m, 2.0, ridge=0.1)
    k.plate(P(path(qb((-1, 26), (-5.4, 30), (-7.4, 26.4), 6), (-7.4, 26.4), qb((-4.8, 27), (-2.4, 25), (-1, 23), 6))), 2.0, "talon")
    k.plate(rect(-10, 3.2, 5, 5.2), 3.0, "dark")
    long_grip(k)
    k.plate(P((-1.8, -9.4), (1.8, -9.4), (0, -14)), 2.2, "bone")


@design("big_top_cleaver")
def big_top_cleaver(k):
    """the big top, folded down into a blade: a striped canvas peak on a tent pole, scalloped at the skirts, a pennant flying off the point"""
    R = k.theme("hollow_circus", base=0.6)
    red = ramp("#2a0408", "#4e0810", "#7a1018", "#a81c20", "#d0302a", "#ee5a44")
    cream = ramp("#6a5a44", "#8e7c60", "#b4a282", "#d6c8a8", "#efe4c8", "#fff8e8")

    def canvas(p, n, b, key, i, j, w, h, fr):
        u = p[0] / max(1.0, (36 - p[1]) / 3.2)
        return at(red if int(math.floor(u + 8)) % 2 else cream, 0.62 + lit(key, i, j, w, h))

    k.mat(blade=canvas, edge=honed(GOLD, 0.7), gold=flat(GOLD, 0.66), pole=stripes(red, cream, 2.6, 0.5), flag=flat(ramp("#0e1a3a", "#182a54", "#22386c", "#304a86", "#4a66a8"), 0.66), wrap=wrap(cream, red[3], 3))
    pts = [(0, 37)]
    for x in (9.6, 7.2, 4.8, 2.4, 0, -2.4, -4.8, -7.2, -9.6):
        pts += [(x, 8), (x - 1.2, 5.4)]
    m = P(pts[:-1])
    k.forge(m, 2.2, step=2)
    k.box(0, 36, 0, 0.8, 5.6, 0.8, "gold")
    k.plate(P((0.4, 41), (6.8, 39.8), (4.6, 39), (6.8, 37.6), (0.4, 38)), 0.5, "flag")
    k.plate(rect(-3.4, 3, 3.4, 5.4), 3.0, "gold")
    long_grip(k, 3.6, mat="pole")
    k.box(0, -3.6, 0, 2.8, 6, 2.8, "wrap")
    k.box(0, -11.4, 0, 3.0, 2.0, 3.0, "gold")


@design("final_act")
def final_act(k):
    """the last show: a blade of heavy red curtain drawn aside on a burning slit of stage, gold tie-backs, and the masks of laughter and grief for its crossguard"""
    R = k.theme("hollow_circus", base=0.6)
    red = ramp("#2a0408", "#4e0810", "#7a1018", "#a81c20", "#d0302a", "#ee5a44")

    def curtain(p, n, b, key, i, j, w, h, fr):
        return at(red, 0.54 + lit(key, i, j, w, h) + 0.2 * math.sin(p[0] * 2.6 + p[1] * 0.12))

    k.mat(curtain=curtain, edge=honed(GOLD, 0.72), gold=flat(GOLD, 0.66, bevel=0.14), hot=fire(HOT, 0.3, 0.7), mask=flat(ramp("#a89878", "#c8b898", "#e0d2b4", "#f8f0dc"), 0.76, bevel=0.1), blackm=flat(ramp("#14121a", "#221e2c", "#322c40"), 0.6, bevel=0.1))
    outer = P((-4.6, 6), (4.6, 6), (4.0, 33), (0, 42), (-4.0, 33))
    k.plate(outer, 1.2, "edge")
    slit = P((0, 40), (2.2, 28), (1.4, 22), (2.0, 13), (0.6, 8), (-0.6, 8), (-2.0, 13), (-1.4, 22), (-2.2, 28))
    k.plate(outer.inset(0.5) - slit, 2.2, "curtain")
    k.plate(slit & outer, 1.4, "hot", glow=True)
    k.plate(rect(-3.8, 13.6, -1.4, 14.8) + rect(1.4, 13.6, 3.8, 14.8), 2.5, "gold")
    for s_, m_, sad in ((1, "mask", 0), (-1, "blackm", 1)):
        f = P(path(qb((s_ * 3.6, 7), (s_ * 3.4, 1), (s_ * 7.4, 0), 6), qb((s_ * 7.4, 0), (s_ * 11.4, 1), (s_ * 11.2, 7), 6), qb((s_ * 11.2, 7), (s_ * 7.4, 9.4), (s_ * 3.6, 7), 6)))
        k.plate(f, 2.0, m_)
        k.plate(disc(s_ * 5.8, 5.2, 0.7, 6) + disc(s_ * 9.0, 5.2, 0.7, 6), 2.2, "gold" if sad else "dark")
        mouth = stroke((s_ * 5.4, 3.0), (s_ * 7.4, 0.8 if not sad else 3.8), (s_ * 9.4, 3.0), 0.6, 6) if not sad else stroke((s_ * 5.4, 2.0), (s_ * 7.4, 4.0), (s_ * 9.4, 2.0), 0.6, 6)
        k.plate(mouth, 2.2, "gold" if sad else "dark")
    k.box(0, 3.4, 0, 7.4, 2.4, 3.0, "gold")
    long_grip(k)
    k.box(0, -11.6, 0, 3.0, 2.4, 3.0, "gold")


@design("mirecleaver")
def mirecleaver(k):
    """a slab of bog iron dredged out with its dead still on it: weed trailing, and a hand of the drowned closed over the edge, not letting go"""
    R = k.theme("mirefen_coven", base=0.44, edge=0.68, scars=0.06)
    skin = ramp("#2c2a1c", "#46422c", "#625e40", "#807c58", "#a09c74")
    k.mat(weed=flat(R["wrap"], 0.56), skin=flat(skin, 0.6, bevel=0.14), hot=fire(R["glow"], 0.3, 0.6))
    m = P((-5, 5), (5, 5), (6.2, 18), (5, 28), (2, 36), (-3, 34), (-5.4, 26), (-6.4, 14))
    k.forge(m, 2.4, step=2)
    k.inlay(L([(-2, 8), (-1, 14), (-2.4, 19)], 0.6) + L([(2.2, 12), (1.2, 20), (2.4, 27)], 0.6), 2.4, "hot", glow=True)
    hand = rect(4, 15, 9.4, 17) + rect(-1, 15.6, 6.4, 18.4)
    for y in (16, 18.0, 20.0):
        hand = hand + L([(4.8, y), (0.4, y + 0.6), (-1.2, y - 0.4)], 1.0)
    k.plate(hand, 3.0, "skin")
    for x, top in ((-5, 6), (-2.6, 2), (3, 4), (5.2, 7)):
        k.plate(wave(lambda t, x=x: x + 0.7 * math.sin(t * 6), lambda t: 0.6, 5, top - 7, 8), 0.5, "weed")
    k.plate(rect(-6.6, 3.2, 6.6, 5.2), 3.0, "dark")
    long_grip(k)
    k.box(0, -11.2, 0, 3.0, 1.8, 3.0, "dark")


@design("sickle_greatblade")
def sickle_greatblade(k):
    """a war khopesh made for a pharaoh's bodyguard: a great bronze question mark of a blade, the crescent deep enough to take a shield rim, hieroglyphs up the shank"""
    k.theme("sandsunk_tomb", base=0.54)
    lapis = ramp("#081a4a", "#0e2a6e", "#163e96", "#2458c0", "#4a84e0")
    bronze = ramp("#2a1606", "#432410", "#5e3618", "#7c4c22", "#9c6630", "#bc8444", "#d8a462", "#f0c88a")
    k.mat(blade=steel(bronze, 0.56, 0.12), edge=honed(GOLD, 0.8), lapis=flat(lapis, 0.6, bevel=0.1), gold=flat(GOLD, 0.62))
    m = P(path((-2, 4), (2, 4), (2, 15), qb((13, 15), (17, 26), (10, 37), 14), (10, 37), qb((4, 41), (-4, 37), (-7, 31), 8), (-7, 31), (-3, 31), qb((1, 35), (6, 34), (8.6, 28), 8), qb((8.6, 28), (9, 22), (2, 20), 8), (-2, 20)))
    k.forge(m, 2.0, ridge=0.0)
    for y in (6, 10, 14):
        k.inlay(rect(-2, y, 2, y + 2), 2.0, "lapis")
    k.plate(P((-3.4, 2.6), (3.4, 2.6), (2.6, 4.4), (-2.6, 4.4)), 2.8, "gold")
    long_grip(k, mat="lapis")
    k.plate(P((-2, -9.4), (2, -9.4), (3.4, -12.6), (0.6, -11.4), (-0.6, -11.4), (-3.4, -12.6)), 2.6, "gold")


@design("jawbone")
def jawbone(k):
    """half the Titan's lower jaw, hinge and all: the ramus is the hilt, the long curve of the mandible is the blade, and it still has its teeth"""
    k.theme("fallen_titan", base=0.5)
    meat = ramp("#2a0608", "#4a0c10", "#6e161a", "#942428", "#b83c3a")
    k.mat(bone=bone(IVORY, 0.68), edgeb=flat(IVORY, 0.88, bevel=0.06), tooth=flat(IVORY, 0.92, bevel=0.04), wrap=wrap(meat, meat[0], 4), meat=flat(meat, 0.5, 0.3))
    m = P(path((-3.2, 2), qb((-6, 20), (-2, 32), (2, 38), 12), (2, 38), qb((4.4, 34), (4.2, 18), (4.4, 2), 12)))
    k.plate(m, 2.4, "edgeb")
    k.plate(m.inset(0.5), 3.8, "bone")
    for j, y in enumerate((8, 13, 18, 22.6, 26.8, 30.6)):
        h = 4.6 - j * 0.3
        x = 4.0 - abs(j - 2) * 0.2
        k.plate(P((x - 0.6, y - 1.8), (x + 1.2, y - 1.6), (x + 1.2 + h, y + 0.8), (x + 1.0, y + 1.7), (x - 0.6, y + 1.8)), 2.6, "tooth")
    k.plate(P(path((-3, 3), (-8, 7), (-9.6, 11), (-5.6, 9), (-3, 6))), 2.0, "bone")
    k.plate(P((-3.4, 3.4), (4.4, 3.4), (5.6, 0.6), (2.4, 2.0), (0, -0.6), (-2.4, 2.0), (-4.8, 0.2)), 3.6, "meat")
    long_grip(k)
    k.plate(disc(0, -11.4, 2.8, 10), 3.2, "edgeb")


@design("guandao")
def guandao(k):
    """a monastery's great crescent blade on a long red pole, the back notched for catching steel, a gold dragon's head at the socket"""
    R = k.theme("jade_monastery", base=0.54)
    k.mat(gold=flat(GOLD, 0.66, bevel=0.14), pole=flat(ramp("#2a0608", "#4a0c10", "#6e1616", "#8e2020"), 0.56, bevel=0.06), silk=flat(ramp("#3a0608", "#600c0e", "#8a1416", "#b42020", "#dc3a30"), 0.6, 0.2), edge=honed(R["blade"], 0.84))
    k.box(0, -18, 0, 2.2, 36, 2.2, "pole")
    long_grip(k, 2)
    k.box(0, -19.4, 0, 3.0, 2.0, 3.0, "gold")
    m = P(path((-2.4, 17), qb((-3.8, 28), (0, 35), (6.6, 42), 12), (6.6, 42), qb((10, 32), (9.6, 25), (2.6, 17), 12)))
    for y in (22, 26):
        x = -3.0 + (y - 17) * 0.1
        m = m - disc(x, y, 0.8, 8)
    k.forge(m, 1.8, ridge=-0.2)
    k.plate(P((-3.4, 14.4), (3.4, 14.4), (4.4, 20), (2, 18.4), (0.2, 21.4), (-1.6, 18.4), (-4.2, 20)), 3.2, "gold")
    k.plate(P((-2.0, 14.6), (2.0, 14.6), (3.0, 8), (0.8, 9.4), (-0.8, 8.2), (-3.0, 9)), 1.4, "silk")


@design("stormcleaver")
def stormcleaver(k):
    """a storm-iron blade cut through with louvres like a shutter in a gale: the wind comes through it screaming and lightning lives in the slots"""
    R = k.theme("storm_bastion", base=0.5)
    k.mat(white=flat(R["glow"], 0.92, bevel=0.02), hot=fire(R["glow"], 0.3, 0.7), iron=flat(R["dark"], 0.6))
    m = P((-5, 5), (5, 5), (6, 12), (5.4, 29), (0, 38), (-5.4, 29), (-6, 12))
    slots = Mask()
    for y in (9, 13, 17, 21, 25):
        slots = slots + L([(-3.4, y), (3.4, y + 2.2)], 1.0)
    k.forge(m - slots, 2.0, step=2)
    k.plate(slots, 0.6, "hot", glow=True)
    k.plate(L([(0, 30), (-1, 32.4), (0.8, 33.2), (0, 36)], 0.4), 2.06, "white", glow=True)
    k.plate(P((-8, 3), (8, 3), (9.6, 7), (6.6, 5.2), (-6.6, 5.2), (-9.6, 7)), 3.0, "iron")
    long_grip(k)
    k.plate(P((-2.4, -9.4), (2.4, -9.4), (0, -13.6)), 2.4, "iron")


@design("executioners_claymore")
def executioners_claymore(k):
    """a Highland claymore in Court service: down-swept quillons ending in quatrefoils, a long ricasso wrapped in red, the point rounded by law"""
    R = k.theme("bloodmoon_court", base=0.5)
    k.mat(silver=flat(IRON, 0.72, bevel=0.14), edge=honed(SILVER, 0.76), red=flat(RUBY, 0.46, bevel=0.1), fuller=flat(R["dark"], 0.4))
    k.forge(P(path((-2.8, 5), (2.8, 5), (2.8, 34), qb((2.8, 38), (0, 39.6), (-2.8, 38), 5), (-2.8, 34))), 1.8)
    k.inlay(rect(-0.6, 12, 0.6, 30), 1.8, "fuller")
    k.plate(rect(-2.9, 5, 2.9, 9), 2.2, "red")
    for s_ in (1, -1):
        k.plate(stroke((0, 4.4), (s_ * 6, 5), (s_ * 9.6, 0.4), 1.5) , 2.4, "silver")
        for a in range(4):
            r = a * math.pi / 2
            k.plate(disc(s_ * 10.4 + math.cos(r) * 1.1, -0.6 + math.sin(r) * 1.1, 1.1, 8), 2.2, "silver")
    long_grip(k)
    k.plate(disc(0, -11.2, 2.3, 10), 2.8, "silver")
    k.plate(disc(0, -11.2, 1.1, 8), 3.0, "red")


@design("kingsplitter")
def kingsplitter(k):
    """the blade that ended a dynasty and kept the proof: a broad black sword driven through a king's crown, the gold bent round it, one ruby still in place"""
    R = k.theme("bloodmoon_court", base=0.42)
    k.mat(gold=flat(GOLD, 0.66, bevel=0.14), gem=gem(RUBY), edge=honed(ramp("#2a0a10", "#5a1420", "#9a2030", "#e04a50", "#ffb0a8"), 0.74), hot=fire(RUBY, 0.3, 0.6))
    k.forge(P((-4.4, 5), (4.4, 5), (3.6, 32), (0, 41), (-3.6, 32)), 2.2)
    k.inlay(L([(0, 7), (0, 33)], 0.8), 2.2, "hot", glow=True)
    crown = P((-8, 20), (-3.6, 20.6), (3.6, 19.4), (8.6, 20), (10, 27), (6.4, 23.6), (4.2, 29), (2, 24), (-1.4, 26), (-3.8, 24), (-5.8, 29), (-7.6, 24.4), (-10, 26.6))
    k.plate(crown, 3.2, "gold")
    k.plate(rect(-8, 19.4, 8.6, 21), 3.6, "gold")
    k.plate(disc(5.6, 20.2, 1.1, 8), 3.9, "gem")
    k.plate(P((-7, 3), (7, 3), (8, 5.4), (-8, 5.4)), 3.2, "gold")
    long_grip(k)
    k.plate(disc(0, -11, 2.2, 10), 2.8, "gold")


@design("ninth_gate_axe")
def ninth_gate_axe(k):
    """a door of the Labyrinth on a pole: a tall square iron-black axe head with a keyhole cut in it and the key still turned, meander round the rim"""
    R = k.theme("obsidian_labyrinth", base=0.46)
    k.mat(gold=flat(GOLD, 0.66), iron=flat(R["blade"], 0.54, bevel=0.14), pole=flat(R["dark"], 0.7, bevel=0.06))
    k.box(0, -13, 0, 2.6, 46, 2.6, "pole")
    long_grip(k, 0, w=3.0)
    k.box(0, -14.4, 0, 3.4, 1.8, 3.4, "gold")
    m = P((1, 13), (12, 8), (14, 12), (14, 34), (12, 38), (1, 33))
    key = disc(7.6, 25, 1.7, 10) + P((6.8, 25), (8.4, 25), (9.2, 19), (6.0, 19))
    k.forge(m - key, 2.0, step=2, ridge=-0.5)
    k.plate(key, 0.8, "glow", glow=True)
    for j in range(6):
        k.plate(rect(3, 12 + j * 0.9, 3.8, 12.4 + j * 0.9) + rect(3, 32 - j * 0.9, 3.8, 32.4 - j * 0.9), 2.1, "gold")
    k.plate(rect(-1.6, 12, 2.6, 34), 3.4, "iron")
    for y in (14, 23, 32):
        k.box(0.6, y, 0, 4.8, 1, 3.8, "gold")
    k.plate(P((-1.6, 20), (-7, 22.6), (-1.6, 26)), 1.6, "iron")


@design("labrys")
def labrys(k):
    """the double axe of the first Labyrinth: two great waisted crescents back to back on a horn-tipped pole, bronze going to fire at the edges"""
    k.theme("obsidian_labyrinth", base=0.46)
    bronze = ramp("#2a1606", "#432410", "#5e3618", "#7c4c22", "#9c6630", "#bc8444", "#d8a462", "#f0c88a")
    k.mat(blade=steel(bronze, 0.54, 0.12), edge=fire(HOT, 0.3, 0.7), gold=flat(GOLD, 0.66, bevel=0.14), pole=flat(HORN, 0.6, bevel=0.06), hornp=flat(HORN, 0.76, bevel=0.14))
    k.box(0, -13, 0, 2.4, 42, 2.4, "pole")
    long_grip(k, 0)
    k.box(0, -14.4, 0, 3.2, 1.8, 3.2, "gold")
    for s_ in (1, -1):
        m = P(path((s_ * 0.8, 19), qb((s_ * 6, 21), (s_ * 9, 16), (s_ * 13.6, 8), 8), (s_ * 13.6, 8), qb((s_ * 19, 20), (s_ * 19, 28), (s_ * 13.6, 40), 12), (s_ * 13.6, 40), qb((s_ * 9, 32), (s_ * 6, 27), (s_ * 0.8, 29), 8)))
        k.plate(m, 1.0, "edge", glow=True, tag="edge")
        k.plate(m.inset(1.0), 2.2, "blade", tag="blade")
        k.plate(disc(s_ * 7, 24, 2.0, 10) - disc(s_ * 7, 24, 1.2, 8), 2.4, "gold")
    k.plate(rect(-1.8, 18, 1.8, 30), 3.4, "gold")
    k.plate(P(path(qb((-1.2, 29), (-1.4, 34), (1.2, 37.4), 6), (1.2, 37.4), qb((1.2, 34), (1.2, 32), (1.2, 29), 4))), 2.2, "hornp")


@design("leviathan_cleaver")
def leviathan_cleaver(k):
    """a slice of the thing under the Lighthouse: scaled hide over a jaw of needle teeth, a fin for a guard and a row of pale photophores burning down the flank"""
    R = k.theme("abyssal_lighthouse", base=0.5)
    fish = ramp("#06080e", "#0c1018", "#141a26", "#1e2838", "#2c3a50", "#3e5270")

    def scales(p, n, b, key, i, j, w, h, fr):
        row = int(p[1] // 2.2)
        u = (p[0] + (row % 2) * 1.2) % 2.4
        v = 0.5 + lit(key, i, j, w, h) + (0.2 if u < 0.6 else 0) - 0.14 * ((p[1] % 2.2) / 2.2)
        return at(fish, v)

    k.mat(blade=scales, edge=flat(fish, 0.86, bevel=0.04), tooth=flat(IVORY, 0.9, bevel=0.04), fin=flat(R["wrap"], 0.56, bevel=0.1), hot=fire(R["glow"], 0.4, 0.6), gum=flat(ramp("#2a0a18", "#4a1228", "#6e1e3c"), 0.56))
    m = P(path((-4.6, 5), qb((-6, 24), (-1, 36), (6, 40), 12), (6, 40), qb((8, 28), (7, 16), (5, 5), 12)))
    k.forge(m, 2.6, ridge=-0.3)
    k.plate(P(path(qb((5.2, 6), (7.6, 18), (6.0, 38), 10), (6, 38), (4.4, 36), qb((5.0, 26), (5, 16), (3.8, 6), 8))), 2.8, "gum")
    for j in range(9):
        y = 7.4 + j * 3.2
        x = 5.2 + math.sin(j / 8 * math.pi) * 1.6
        ln = 4.8 - abs(j - 4) * 0.4
        k.plate(P((x - 0.8, y - 1.2), (x - 0.8, y + 1.2), (x + ln, y + 1.8)), 1.2, "tooth")
    for y in (10, 15, 20, 25, 30):
        k.plate(disc(-2.4 + (y - 10) * 0.16, y, 0.6, 6), 2.8, "hot", glow=True)
    fin = P((-5, 5.4), (-7, 12), (-11, 16), (-10.4, 10), (-11.6, 7), (-8.6, 7.2), (-7.4, 3.4))
    k.plate(fin, 0.8, "fin")
    k.plate(rect(-5.6, 3.2, 5.6, 5.4), 3.4, "gum")
    long_grip(k)
    k.plate(P((-3.4, -13), (0, -9.4), (3.4, -13), (1, -12), (-1, -12)), 1.4, "fin")


@design("eclipse_greatsword")
def eclipse_greatsword(k):
    """a black greatsword with the moon's bite taken out of it: a clean round notch in the edge, white fire round the rim of the notch, a small cold corona at the guard"""
    k.theme("eclipse_cathedral", base=0.3, ridge=0.08)
    black = ramp("#040408", "#0a0a12", "#12121c", "#1c1c2a", "#2a2a3c", "#40405a")
    k.mat(blade=steel(black, 0.54, 0.14), edge=honed(ramp("#14141e", "#2a2a3c", "#4e4e6a", "#8a8aa8", "#d0d0e0"), 0.64), corona=fire(ramp("#d0a040", "#ffe08a", "#fff6d0", "#ffffff"), 0.4, 0.6), gold=flat(IRON, 0.72))
    m = P((-4.6, 5), (4.6, 5), (4.6, 30), (0, 40), (-4.6, 30))
    bite = disc(6.4, 22, 6.0, 20)
    k.forge(m - bite, 2.2)
    k.plate((disc(6.4, 22, 6.8, 20) - bite) & m, 2.3, "corona", glow=True)
    k.plate(ring(0, 3.6, 5.6, 4.4), 1.2, "corona", glow=True)
    k.plate(disc(0, 3.6, 4.4, 14), 3.4, "gold")
    long_grip(k)
    k.plate(P((-2.4, -9.4), (2.4, -9.4), (0, -14)), 2.4, "gold")


@design("ashveil_requiem")
def ashveil_requiem(k):
    """the Cathedral's funeral: a tall gravestone of a blade with a grey veil wound round it, organ pipes for the guard, the last few lines of a hymn carved and burning"""
    k.theme("eclipse_cathedral", base=0.46, ridge=0.08)
    stone = ramp("#1a1a20", "#2a2a32", "#3e3e48", "#565660", "#72727c", "#94949e")
    k.mat(blade=steel(stone, 0.6, 0.1), edge=honed(stone, 0.92), veil=flat(ramp("#3a3a42", "#54545e", "#72727c", "#94949e", "#b8b8c0"), 0.6, 0.1, bevel=0.1), pipe=flat(ramp("#4a4438", "#6e6652", "#948a70", "#bcb294", "#dcd4b8"), 0.6, bevel=0.14), hot=fire(ramp("#ffb040", "#ffe8a0", "#fffbe0", "#ffffff"), 0.4, 0.6))
    m = P(path((-4.6, 6), (4.6, 6), (4.6, 29), qb((4.6, 37), (0, 40), (-4.6, 37), 6), (-4.6, 29)))
    k.forge(m, 2.4)
    for y in (24, 21.6, 19.2):
        k.inlay(rect(-3.0, y, 3.0 - (24 - y) * 0.2, y + 0.5), 2.4, "hot", glow=True)
    k.inlay(rect(-0.5, 26.6, 0.5, 34) + rect(-2.4, 30.4, 2.4, 31.4), 2.4, "hot", glow=True)
    v = wave(lambda t: -5.0 + 8.6 * t, lambda t: 2.0 + 0.6 * math.sin(t * 6), 18, 7, 14)
    k.plate(v, 3.0, "veil")
    k.plate(wave(lambda t: -5.8 - 1.6 * t + 0.6 * math.sin(t * 6), lambda t: 1.0, 18, 4, 10), 0.6, "veil")
    for j, x in enumerate((-9, -6.8, -4.6, -2.4, 2.4, 4.6, 6.8, 9)):
        h = 8 - abs(abs(x) - 2.4) * 0.7
        k.box(x, 5 - 3, 0, 1.8, h, 1.8, "pipe")
        k.box(x, 3.4, 0.9, 1.2, 0.6, 0.3, "edge")
    k.plate(rect(-10, 1.6, 10, 2.6), 2.6, "pipe")
    long_grip(k, 1.8)
    k.plate(rect(-2, -12, 2, -9.4), 2.8, "pipe")


@design("wyrmcleaver")
def wyrmcleaver(k):
    """a dragon's wing-finger for a spine and its own membrane stretched and scorched for the blade, the wrist claw at the top, ember veins"""
    k.theme("wyrms_hoard", base=0.54)
    hide = ramp("#2a0a06", "#44120a", "#621c10", "#822a18", "#a43e22", "#c85a30")
    k.mat(blade=steel(hide, 0.56, 0.14), edge=honed(hide, 0.92), bone=bone(IVORY, 0.66), claw=flat(HORN, 0.72, bevel=0.14), hot=fire(HOT, 0.3, 0.7), gold=flat(GOLD, 0.66), scale=flat(GOLD, 0.5, bevel=0.2))
    m = P(path((-3, 5), (6, 5), (9.4, 13), (7.4, 15.6), (9.6, 23), (6.4, 25), (7.4, 32), (2.8, 33), (1, 38), qb((-2, 26), (-4, 16), (-3, 5), 10)))
    k.forge(m, 1.6, step=2)
    k.plate(stroke((-1.8, 5), (-3.6, 22), (1, 38), 2.0, 12), 3.2, "bone")
    for a, b in (((-2, 12), (7.8, 13.6)), ((-1.6, 22), (7.8, 23.6)), ((-0.4, 30), (6, 32))):
        k.inlay(L([a, b], 0.6), 1.6, "hot", glow=True)
    k.plate(P(path(qb((1, 38), (1, 41), (-3, 43), 6), (-3, 43), qb((-1.2, 40), (-1, 38), (-0.6, 36), 6))), 2.2, "claw")
    k.plate(rect(-4.4, 3, 7.4, 5.4), 3.4, "scale")
    long_grip(k, mat="scale")
    k.plate(disc(0, -11.4, 2.4, 10), 3.0, "gold")


# ---------------------------------------------------------------- the world's

@design("mercenarys_zweihander")
def mercenarys_zweihander(k):
    """a landsknecht's sword: long, straight, a leather-wrapped ricasso to choke up on, parrying lugs below the point of balance, big swept quillons"""
    fe = ramp("#2a2e34", "#3e444c", "#565e68", "#727c86", "#929ca6", "#b4bec6", "#d4dce2", "#f0f4f6")
    k.mat(blade=steel(fe, 0.54, 0.13), edge=honed(fe, 0.84), iron=flat(IRON, 0.7), wrap=wrap(LEATHER, IRON[1], 5))
    k.forge(P((-2.8, 11), (2.8, 11), (2.2, 36), (0, 42), (-2.2, 36)), 1.7)
    k.plate(rect(-1.8, 4, 1.8, 11.4), 2.0, "wrap")
    k.plate(P((-4.8, 11), (-1.8, 11.4), (-1.8, 9.4)) + P((4.8, 11), (1.8, 11.4), (1.8, 9.4)), 1.8, "iron")
    k.plate(P(path((-11, 6), qb((-6, 3), (-3, 2), (0, 2.4), 6), qb((3, 2), (6, 3), (11, 6), 6), (10.4, 7), qb((6, 4.4), (3, 4), (0, 4.2), 6), qb((-3, 4), (-6, 4.4), (-10.4, 7), 6))), 2.4, "iron")
    long_grip(k, 2.6)
    k.plate(disc(0, -11.2, 2.3, 10), 2.8, "iron")


@design("headsmans_cleaver")
def headsmans_cleaver(k):
    """a broad, flat-ended block of a sword, a straight bar for a guard, cleaned by nobody; the stain has its own grain by now"""
    fe = ramp("#1a1a1e", "#2a2a30", "#3c3c44", "#52525c", "#6e6e78", "#8e8e96")
    rust = ramp("#1a0606", "#2e0a0a", "#4a100e", "#661812", "#842416")
    plain = steel(fe, 0.56, 0.12, scars=0.05)

    def blade(p, n, b, key, i, j, w, h, fr):
        if p[1] > 19 + 6 * math.sin(p[0] * 1.3) + 2 * math.sin(p[0] * 3.1):
            return at(rust, 0.5 + lit(key, i, j, w, h) + (0.14 if p[0] < 0 else -0.08))
        return plain(p, n, b, key, i, j, w, h, fr)

    k.mat(blade=blade, edge=honed(fe, 0.9), iron=flat(IRON, 0.66), wrap=wrap(LEATHER, IRON[1], 5))
    k.forge(P((-5, 5), (5, 5), (5.8, 34), (4.4, 36), (-4.4, 36), (-5.8, 34)), 1.9)
    k.plate(rect(-9, 3.2, 9, 5), 2.8, "iron")
    long_grip(k)
    k.box(0, -11.6, 0, 3.4, 2.4, 3.4, "iron")


@design("grave_reaver")
def grave_reaver(k):
    """a blade of fused bone, femurs and ribs knitted into one long curve, the dead's green fire breathing out of every gap"""
    bonec = ramp("#3a3428", "#544c3c", "#706652", "#8e846c", "#aca286", "#c8bea4", "#e0d8c0", "#f4eedc")
    soul = ramp("#0c3a20", "#167a40", "#2ab866", "#6ee6a0", "#c0ffd8", "#f0fff6")
    k.mat(bone=bone(bonec, 0.66), edgeb=flat(bonec, 0.86, bevel=0.06), hot=fire(soul, 0.3, 0.7), iron=flat(IRON, 0.66), wrap=wrap(ramp("#101a10", "#1c2a1c", "#2c3e2c"), soul[1], 4))
    m = P(path(qb((-3.4, 5), (-6, 24), (6, 42), 14), (6, 42), qb((8.4, 28), (7, 16), (4.4, 5), 12)))
    gaps = Mask()
    for a, b in (((0, 9), (2, 15)), ((-1, 18), (1, 24)), ((3, 12), (4, 19)), ((1, 27), (3, 33))):
        gaps = gaps + L([a, b], 1.2)
    k.plate(m - gaps, 1.8, "edgeb")
    k.plate((m - gaps).inset(0.5), 3.0, "bone")
    k.plate(gaps, 1.2, "hot", glow=True)
    k.plate(P((-7, 3), (7, 3), (6, 5.4), (-6, 5.4)) + disc(-7.6, 4, 1.6, 8) + disc(7.6, 4, 1.6, 8), 3.0, "bone")
    k.plate(disc(-7.6, 4.2, 0.6, 6) + disc(7.6, 4.2, 0.6, 6), 3.2, "hot", glow=True)
    long_grip(k)
    k.plate(disc(0, -11.2, 2.4, 8), 3.0, "edgeb")


@design("dragonspine")
def dragonspine(k):
    """a dragon's spine pulled out still burning: vertebrae shrinking to the tip, tall dorsal spines all up one side, fire in every disc"""
    bonec = ramp("#2a1408", "#44241a", "#6a3a26", "#8e5a3c", "#b08458", "#d0ae82")
    k.mat(bone=flat(bonec, 0.66, bevel=0.14), spine=flat(bonec, 0.82, bevel=0.1), hot=fire(HOT, 0.3, 0.7), gold=flat(GOLD, 0.66), wrap=wrap(ramp("#2a0a06", "#44120a", "#621c10"), HOT[1], 4))
    n = 11
    for j in range(n):
        y = 5 + j * 3.0
        w = 4.2 - j * 0.28
        cx = 0.3 * j * j * 0.08
        k.plate(rect(cx - w, y, cx + w, y + 2.4), 3.4 - j * 0.1, "bone")
        k.plate(rect(cx - w + 0.6, y + 2.4, cx + w - 0.6, y + 3.0), 2.8, "hot", glow=True)
        ln = 7.6 - j * 0.46
        k.plate(P((cx - w, y), (cx - w, y + 2.2), (cx - w - ln, y + 5.2)), 1.2, "spine")
        k.plate(P((cx + w, y + 0.6), (cx + w, y + 2), (cx + w + 1.6, y + 2.4)), 1.6, "bone")
    k.plate(P((2.2, 38), (5.4, 38), (5.4, 44)), 1.6, "spine")
    k.plate(rect(-6.4, 3, 6.4, 5), 3.8, "gold")
    long_grip(k)
    k.plate(P(path(qb((-2.2, -9.4), (-3.4, -13), (1, -15.4), 6), (1, -15.4), qb((-0.6, -13), (2, -11), (2.2, -9.4), 6))), 2.4, "spine")


@design("barrowsteel_greatsword")
def barrowsteel_greatsword(k):
    """dug from a barrow mound, pitted to lace near the point: a plain wide old sword, bronze hilt green with age, grave moss in the fuller, fur on the grip"""
    fe = ramp("#1c1a18", "#2a2724", "#3a3632", "#4c4741", "#605a52", "#787066", "#928a7e", "#aea698")
    bronze = ramp("#0e2420", "#163a30", "#205244", "#2e6e5a", "#448c74", "#6cb094")
    k.mat(blade=steel(fe, 0.52, 0.12, scars=0.12), edge=honed(fe, 0.82), bronze=flat(bronze, 0.56), moss=flat(ramp("#1a2a10", "#2c4018", "#425a22"), 0.6, 0.3), fur=wrap(ramp("#2a2420", "#403630", "#5a4e44"), None, 3))
    m = P((-3.4, 5), (3.4, 5), (3.0, 30), (1.0, 38), (-0.4, 35), (-3.0, 31))
    m = m - disc(2.8, 30, 0.8, 6) - disc(-2.2, 26, 0.6, 6) - disc(1.2, 33, 0.6, 6)
    k.forge(m, 1.8)
    k.inlay(rect(-0.7, 7, 0.7, 26), 1.8, "moss")
    k.plate(rect(-6.4, 3.2, 6.4, 5.2), 3.0, "bronze")
    long_grip(k, mat="fur")
    k.plate(disc(0, -11.2, 2.8, 12) - disc(0, -11.2, 1.1, 8), 2.2, "bronze")


@design("dune_cleaver")
def dune_cleaver(k):
    """a Salt Khan's rider's broad bronze crescent, swollen at the end, sand-polished bright along its belly, a horsetail hanging from the grip"""
    bronze = ramp("#2a1606", "#432410", "#5e3618", "#7c4c22", "#9c6630", "#bc8444", "#d8a462", "#f0c88a")
    k.mat(blade=steel(bronze, 0.58, 0.14), edge=honed(bronze, 0.92), gold=flat(GOLD, 0.62), wrap=wrap(LEATHER, bronze[3], 4), tail=flat(ramp("#1a1410", "#2e241c", "#463828", "#60503a"), 0.6, 0.3))
    m = P(path(qb((-2.4, 5), (-3, 19), (2, 28), 10), (2, 28), qb((4, 33), (10, 41), (16, 37), 6), (16, 37), qb((16.4, 26), (10, 13), (3.2, 5), 12)))
    k.forge(m, 1.9, ridge=-0.3)
    k.plate(P((-5, 3.2), (6, 3.2), (7.4, 5.4), (-6, 5.4)), 2.8, "gold")
    long_grip(k)
    k.box(0, -11, 0, 3.0, 1.6, 3.0, "gold")
    k.plate(P((-1.4, -12.4), (1.4, -12.4), (2.4, -19), (0.6, -17.6), (-0.6, -19.4), (-2.4, -17.6)), 1.4, "tail")


@design("chimera_jaw")
def chimera_jaw(k):
    """a vat-grown beast's long jaw, teeth down both edges, the gum still wet and an acid green running in the groove between"""
    bonec = ramp("#3a3428", "#544c3c", "#706652", "#8e846c", "#aca286", "#c8bea4", "#e0d8c0")
    acid = ramp("#3a7a10", "#68c020", "#a4f040", "#e0ffa0")
    k.mat(bone=bone(bonec, 0.66), tooth=flat(IVORY, 0.92, bevel=0.04), gum=flat(ramp("#2a0a12", "#4a1420", "#6e2030", "#944040"), 0.56), hot=fire(acid, 0.3, 0.7), iron=flat(IRON, 0.66), wrap=wrap(ramp("#1a0a0a", "#2e1414", "#461e1e"), acid[0], 4))
    m = P((-3.4, 5), (3.4, 5), (2.8, 32), (0, 39), (-2.8, 32))
    k.plate(m, 3.4, "bone")
    k.plate(L([(0, 6), (0, 32)], 1.6), 3.5, "gum")
    k.plate(L([(0, 7), (0, 31)], 0.7), 3.6, "hot", glow=True)
    for s_ in (1, -1):
        for j in range(9):
            y = 6.6 + j * 2.9 + (1.0 if s_ < 0 else 0)
            x = 3.2 - j * 0.1
            ln = 3.6 - j * 0.16
            k.plate(P((s_ * x, y - 1.1), (s_ * x, y + 1.1), (s_ * (x + ln), y + 1.6)), 1.6, "tooth")
    k.plate(rect(-7, 3.2, 7, 5.2), 3.4, "gum")
    long_grip(k)
    k.box(0, -11.2, 0, 3.2, 1.8, 3.2, "iron")


@design("kingsbarrow")
def kingsbarrow(k):
    """the Barrow King's greatsword: black steel, his crowned dead rising along its edge as pale shapes in soul fire, a gold crown for its guard"""
    black = ramp("#08080a", "#101014", "#18181e", "#22222a", "#2e2e38", "#3e3e4a", "#54545f")
    soul = ramp("#0c3a5a", "#1a6a96", "#3aa8dc", "#7ad8ff", "#c0f0ff", "#ffffff")
    k.mat(blade=steel(black, 0.54, 0.13), edge=fire(soul, 0.3, 0.7), rim=honed(black, 0.92), gold=flat(GOLD, 0.66, bevel=0.14), hot=fire(soul, 0.4, 0.6), wrap=wrap(ramp("#1e1c1c", "#34302e", "#524c48"), GOLD[3], 5), gem=gem(soul))
    m = P((-4.2, 5), (4.2, 5), (3.6, 33), (0, 42), (-3.6, 33))
    k.plate(m, 1.2, "edge", glow=True, tag="edge")
    k.plate(m.inset(0.5), 2.4, "blade", tag="blade")
    for j, y in enumerate((10, 16, 22, 28)):
        s_ = 1 if j % 2 else -1
        x = s_ * (1.2 - j * 0.1)
        ghost = disc(x, y + 2.4, 1.4, 8) + P((x - 2, y - 2.0), (x + 2, y - 2.0), (x + 1.3, y + 1.4), (x - 1.3, y + 1.4)) + P((x - 1.4, y + 3.4), (x + 1.4, y + 3.4), (x + 1.6, y + 5), (x + 0.6, y + 4.2), (x, y + 5.2), (x - 0.6, y + 4.2), (x - 1.6, y + 5))
        k.plate(ghost, 2.46, "hot", glow=True)
        k.plate(disc(x - 0.5, y + 2.6, 0.3, 4) + disc(x + 0.5, y + 2.6, 0.3, 4), 2.52, "blade")
    crown = P((-8, 2.8), (8, 2.8), (9.4, 9), (6.2, 6), (4.4, 9.4), (2.6, 6.2), (-2.6, 6.2), (-4.4, 9.4), (-6.2, 6), (-9.4, 9))
    k.plate(crown, 3.2, "gold")
    k.plate(disc(0, 4, 1.2, 8), 3.5, "gem")
    long_grip(k, 3.0)
    k.plate(P((-2.4, -9.4), (2.4, -9.4), (2.8, -12.4), (1.2, -11), (0, -13), (-1.2, -11), (-2.8, -12.4)), 2.8, "gold")


@design("two_hearted")
def two_hearted(k):
    """two swords' hearts in one blade: a long broad sword split down its middle by a seam of light, an iron half and a gold half, each with a heart beating in it"""
    fe = ramp("#2a2e34", "#3e444c", "#565e68", "#727c86", "#929ca6", "#b4bec6", "#d4dce2", "#f0f4f6")
    k.mat(blade=steel(fe, 0.54, 0.13), edge=honed(fe, 0.84), goldb=steel(GOLD, 0.56, 0.13), goldedge=honed(ramp("#a06018", "#d8982c", "#f6d060", "#fff0b0", "#ffffff"), 0.7), iron=flat(IRON, 0.66), gold=flat(GOLD, 0.66), hot=fire(ramp("#ffb040", "#ffe8a0", "#fffbe0", "#ffffff"), 0.4, 0.6), wrap=wrap(LEATHER, GOLD[3], 4), red=fire(RUBY, 0.3, 0.6))
    l_ = P((-5, 5), (-0.4, 5), (-0.4, 42), (-4.4, 32))
    r_ = P((5, 5), (0.4, 5), (0.4, 42), (4.4, 32))
    k.forge(l_, 2.0)
    k.plate(r_, 1.0, "goldedge", tag="edge")
    k.plate(r_.inset(1.0), 2.0, "goldb", tag="blade")
    k.plate(rect(-0.4, 5, 0.4, 40), 0.8, "hot", glow=True)
    for x in (-2.4, 2.4):
        k.plate(disc(x - 0.8, 19.6, 1.1, 8) + disc(x + 0.8, 19.6, 1.1, 8) + P((x - 1.8, 19.4), (x + 1.8, 19.4), (x, 16.4)), 2.06, "red", glow=True)
    k.plate(P((-9, 3), (0, 3), (0, 5), (-8, 5), (-10, 6.6)), 3.0, "iron")
    k.plate(P((9, 3), (0, 3), (0, 5), (8, 5), (10, 6.6)), 3.0, "gold")
    long_grip(k)
    k.plate(disc(0, -11.2, 2.3, 10), 2.6, "iron")
    k.plate(disc(0.7, -11.2, 1.6, 10), 2.8, "gold")
