"""Black magic staffs: a shaft to y 12 or so, the head from there to about 34. Each head a dangerous object of its own."""
import math

from voxsword import ramp
from weaponsets import design, qb, path, P, L, disc, ring, rect, wave, Mask, flat, fire, staves, steel, honed, bone, gem, at, lit, wrap, stripes, facet_of
from weaponsets_a import BRASS, GOLD, IRON, LEATHER
from weaponsets_c import shard
from weaponsets_d import RUBY, SILVER, feathers, links, stroke
from weaponsets_e import CORK, HORN, IVORY, RAG

HOT = ramp("#a02206", "#e04a0a", "#ff8a1c", "#ffc84a", "#fff0b0")
VOID = ramp("#3a0a6a", "#6a1ac0", "#a050ff", "#d8b0ff", "#ffffff")
TEAL = ramp("#0e4a48", "#1a7e78", "#34b8aa", "#5cd8c8", "#8ceee2", "#f0fffc")
NIGHT = ramp("#050408", "#0c0a10", "#16121e", "#221c2e", "#322a42", "#4a3e60")
FE = ramp("#2a2e34", "#3e444c", "#565e68", "#727c86", "#929ca6", "#b4bec6", "#d4dce2")


def pole(k, top=12.0, mat="wood", w=2.0, grip="wrap", shoe="dark", bottom=-18.0):
    k.box(0, bottom, 0, w, top - bottom, w, mat, tag="haft")
    k.box(0, -4.0, 0, w + 0.4, 8.0, w + 0.4, grip, tag="grip")
    k.box(0, bottom - 1.6, 0, w + 0.6, 2.0, w + 0.6, shoe)


def orb(k, x, y, r_, mat, d=None):
    """a real ball, built up in stacked discs front to back"""
    for j in range(5):
        z = (j - 2) * r_ * 0.4
        rr = math.sqrt(max(0.05, r_ * r_ - z * z))
        k.plate(disc(x, y, rr, 14), r_ * 0.42, mat, z=z, glow=True)


def claw(k, s_, y, r_, mat, w=1.3):
    """an iron finger curling up round something"""
    k.plate(stroke((s_ * 1.0, y), (s_ * (r_ + 2.4), y + r_ * 0.7), (s_ * 1.4, y + r_ * 2.2), w, 10), 1.6, mat)


@design("sourwell_staff")
def sourwell_staff(k):
    """a well sweep's pole with the sour bucket still swinging on it, the water in it glowing and wrong"""
    R = k.theme("cellar")
    k.mat(stave=staves(R["wood"], 1.2, 0.6), rope=flat(R["acc"], 0.72), hoop=flat(IRON, 0.62), hot=flat(R["glow"], 0.66, bevel=0.14))
    pole(k, 31, "stave")
    k.plate(stroke((0, 30.6), (6, 34), (9, 30), 1.3), 1.6, "stave")
    links(k, [(9, 29.4), (9, 27.4), (9, 25.4)], "rope", 0.7)
    k.plate(P((2.6, 24.6), (15.4, 24.6), (14.2, 12.6), (3.8, 12.6)), 8.0, "stave")
    for y in (13.8, 21.8):
        k.box(9, y, 0, 12.4, 1.1, 8.4, "hoop")
    k.box(9, 24.4, 0, 11.6, 0.7, 7.0, "hot", glow=True)
    k.plate(P((2.6, 24.6), (1.4, 18), (1.8, 14), (3.0, 16), (3.8, 24.6)), 1.4, "hot", glow=True)
    k.plate(P((12, 24.6), (13.4, 24.6), (13, 21), (12.6, 19)), 8.2, "hot", glow=True)


@design("sourmother")
def sourmother(k):
    """a vat-tap as big as a fist, wide open and running: the vinegar never reaches the ground, it hangs off the spout in a burning green ball"""
    R = k.theme("cellar")
    k.mat(brass=flat(BRASS, 0.64, bevel=0.14), stave=staves(R["wood"], 1.2, 0.56))
    pole(k, 18, "stave", 2.2)
    k.box(0, 17, 0, 4.4, 3.0, 4.4, "brass")
    k.plate(P((-2, 22), (2, 22), (9, 20), (10.4, 16), (7.8, 16), (6.6, 18.4), (-2, 19)), 3.4, "brass")
    k.box(0, 21.6, 0, 1.6, 3, 1.6, "brass")
    k.box(0, 24.4, 0, 7.4, 1.2, 1.6, "brass")
    orb(k, 9, 11.4, 3.6, "glow")
    k.plate(L([(9.2, 16), (9.0, 14)], 1.6), 1.8, "glow", glow=True)


@design("tar_staff")
def tar_staff(k):
    """a gallows-tar brush left in the pot too long: a black ball of pitch at the end, dripping upward and burning at the edges"""
    R = k.theme("gallows")
    k.mat(pitch=flat(ramp("#050404", "#100c0a", "#1c1612", "#2a221c"), 0.6, bevel=0.2), ash=staves(R["wood"], 1.0, 0.58), hot=fire(R["glow"], 0.3, 0.7))
    pole(k, 15, "ash")
    m = disc(0, 19.6, 6.0, 14) + disc(-3.6, 23, 3, 9) + disc(3.4, 15.4, 3, 9)
    k.plate(m, 6.0, "pitch")
    for x, top in ((-5, 29.6), (-1, 31), (3.4, 28.6)):
        k.plate(P((x - 1.0, 23), (x + 1.0, 23), (x, top)), 2.0, "pitch")
    for x, y in ((-3, 20), (2.4, 22), (0.2, 17)):
        k.plate(disc(x, y, 1.0, 7), 6.2, "hot", glow=True)
    k.box(0, 13, 0, 3.0, 2.4, 3.0, "dark")


@design("sporeblight")
def sporeblight(k):
    """a staff of dead wood with three puffballs split open at the top, a slow cold cloud of green spores hanging round them"""
    R = k.theme("rotwood")
    k.mat(cap=flat(R["acc"], 0.62, 0.2, bevel=0.14), rot=staves(R["wood"], 1.0, 0.6))
    pole(k, 18, "rot")
    for x, y, r_ in ((0, 24, 5.0), (-5, 18.4, 3.4), (4.8, 18, 3.6)):
        k.plate(disc(x, y, r_, 12), r_ * 1.5, "cap")
        k.plate(disc(x, y + r_ * 0.8, r_ * 0.56, 9), r_ * 0.9, "glow", glow=True)
    for x, y in ((-3, 31), (2.6, 32.6), (-7, 25), (7, 25.4), (0.2, 34.6)):
        k.plate(disc(x, y, 0.7, 6), 0.8, "glow", glow=True)
        k.seg((x, y), (x * 0.6, y - 4), 0.25, 0.25, "glow", glow=True)
    k.plate(stroke((0, 16), (-3, 16), (-4, 16), 1.2), 1.4, "rot")
    k.plate(stroke((0, 16), (3, 15.4), (4, 15.4), 1.2), 1.4, "rot")


@design("wickfire")
def wickfire(k):
    """a twist of black wick thick as an arm with a tall dark flame on it, gold at the heart, nothing burning that you can see"""
    R = k.theme("crypt")
    k.mat(wick=wrap(ramp("#08080c", "#14141a", "#20202a", "#30303e"), None, 3), flame=fire(ramp("#3a0a4a", "#7a1a70", "#d04a40", "#ffa83a", "#fff0b0"), 0.1, 0.8), wax=flat(R["acc"], 0.72, bevel=0.1))
    pole(k, 12, "wick")
    k.plate(P((-4.4, 12), (4.4, 12), (3.0, 14), (-3.0, 14)), 4.6, "dark")
    k.box(0, 14, 0, 2.2, 6, 2.2, "wick")
    k.plate(P(path(qb((0, 19), (-5.4, 23), (0, 35.6), 10), qb((0, 35.6), (5.4, 24), (0, 19), 10))), 2.4, "flame", glow=True)
    k.plate(P(path(qb((0, 20), (-2.4, 23), (0, 29), 6), qb((0, 29), (2.4, 23), (0, 20), 6))), 2.8, "glow", glow=True)
    k.plate(P((-3, 13.6), (-1.6, 13.6), (-1.8, 11), (-2.8, 8)) + P((2, 13.6), (3.2, 13.6), (3, 11.4), (2.6, 10)), 1.8, "wax")


@design("miasma_censer")
def miasma_censer(k):
    """a plague pomander on a chain: a pierced brass ball full of something you should not breathe, green smoke rolling off it and downward"""
    R = k.theme("plague")
    k.mat(brass=flat(R["dark"], 0.64, bevel=0.14), smoke=flat(ramp("#1a3a14", "#2e6210", "#4e901a", "#7ec41e"), 0.4, bevel=0.1), cane=flat(R["acc"], 0.56))
    pole(k, 26, "cane")
    k.plate(stroke((0, 25.6), (6, 28.6), (8, 24), 1.1), 1.4, "brass")
    links(k, [(8, 23.6), (8, 22), (8, 20.4)], "brass", 0.7)
    orb(k, 8, 16.4, 3.6, "glow")
    k.plate(ring(8, 16.4, 4.6, 3.8) + rect(7.6, 12, 8.4, 20.8) + rect(3.6, 16, 12.4, 16.8), 4.0, "brass")
    k.plate(wave(lambda t: 9 + 3 * t + math.sin(t * 7), lambda t: 1.4 - 0.6 * t, 12, -3, 12) + wave(lambda t: 6 - 1 * t + 0.8 * math.sin(t * 6), lambda t: 1.0 - 0.6 * t, 12.4, 2, 10), 0.6, "smoke")


@design("shardcaller")
def shardcaller(k):
    """an iron hand holding up a cluster of raw mana crystal, the shards humming apart from each other a little"""
    R = k.theme("temple", base=0.7)
    k.mat(crystal=flat(R["glow"], 0.7, bevel=0.14), gold=flat(R["acc"], 0.62), white=flat(R["glow"], 0.92, bevel=0.04))
    pole(k, 14, "dark", grip="wrap", shoe="gold")
    for x, y, ln, a, w in ((0, 15, 18, 0, 5), (-3, 16, 12, 24, 3.4), (3.4, 15, 13, -22, 3.6), (-5, 18, 8, 48, 2.4), (5.4, 17, 8, -50, 2.4)):
        k.plate(shard(x, y, ln, a, w), 2.2, "crystal")
    k.plate(shard(0, 18, 12, 0, 1.8), 2.4, "white")
    for s_ in (1, -1):
        k.plate(stroke((s_ * 1, 13), (s_ * 6, 12), (s_ * 7, 19), 1.2), 2.4, "gold")
    k.box(0, 12.6, 0, 4.2, 2.2, 4.2, "gold")


@design("manacrown")
def manacrown(k):
    """a crown nobody wears, hanging in the air above its staff, a bright knot of mana turning slowly inside the ring"""
    R = k.theme("temple", base=0.7)
    k.mat(gold=flat(GOLD, 0.68, bevel=0.14), rod=flat(R["blade"], 0.72))
    pole(k, 17, "rod", shoe="gold")
    k.plate(disc(0, 18, 5.0, 16) - disc(0, 21, 5.0, 16), 2.0, "gold")
    orb(k, 0, 24.6, 3.6, "glow")
    crown = P((-9, 29), (9, 29), (10.4, 37), (6.4, 33), (3.6, 39), (0, 33.6), (-3.6, 39), (-6.4, 33), (-10.4, 37))
    k.plate(crown - rect(-8, 31, 8, 32), 2.4, "gold")
    k.plate(rect(-8, 31, 8, 32), 2.6, "glow", glow=True)
    for x, y in ((-10.4, 37), (10.4, 37), (-3.6, 39), (3.6, 39)):
        k.plate(disc(x, y, 0.9, 7), 2.4, "glow", glow=True)


@design("wickflame")
def wickflame(k):
    """the Ossuary's reading lamp: a skull on a femur with its cap sawn off, a wick burning green in the brain pan"""
    R = k.theme("ossuary")
    k.mat(bone=bone(R["acc"], 0.68), edgeb=flat(R["acc"], 0.86, bevel=0.06), brass=flat(R["dark"], 0.62))
    pole(k, 16, "bone", shoe="brass")
    k.plate(P(path(qb((-5, 26), (-6.4, 20), (-3, 17), 6), (3, 17), qb((6.4, 20), (5, 26), (5, 26), 3))), 6.6, "edgeb")
    k.plate(rect(-2.6, 14.4, 2.6, 17.4), 5.0, "edgeb")
    k.plate(disc(-2.2, 21, 1.5, 8) + disc(2.2, 21, 1.5, 8), 6.8, "glow", glow=True)
    k.plate(P((-0.6, 18.6), (0.6, 18.6), (0, 17.0)), 6.8, "dark")
    for x in (-1.6, 0, 1.6):
        k.plate(rect(x - 0.2, 14.4, x + 0.2, 16), 5.1, "dark")
    k.plate(P(path(qb((0, 25), (-3.8, 28), (0, 35), 8), qb((0, 35), (3.8, 28), (0, 25), 8))), 2.0, "glow", glow=True)
    k.box(0, 25.6, 0, 11, 0.8, 7, "brass")


@design("crucible_staff")
def crucible_staff(k):
    """a founder's crucible in a pair of iron tongs on a long handle, tipped forward, lip glowing, about to pour on someone"""
    R = k.theme("foundry")
    k.mat(iron=flat(ramp("#14120f", "#221f1b", "#332f2a", "#46403a", "#5e564e", "#7a7065"), 0.64, bevel=0.14), clay=flat(ramp("#2a1a10", "#46301e", "#64462c", "#865e3c"), 0.6, bevel=0.14), hot=fire(HOT, 0.3, 0.7))
    pole(k, 14, "iron")
    for s_ in (1, -1):
        k.plate(stroke((0, 14), (s_ * 8, 15), (s_ * 7, 22), 1.3), 1.6, "iron")
    pts = [(-6, 28), (6, 32), (7, 27), (3.6, 17), (-2.4, 17)]
    k.plate(P(*pts), 7.0, "clay")
    k.plate(P((-6, 28), (6, 32), (6.2, 30.8), (-5.8, 26.8)), 7.2, "hot", glow=True)
    k.plate(P((6, 32), (10.4, 32.4), (9.4, 34), (5.6, 33)), 3.0, "hot", glow=True)
    k.plate(wave(lambda t: 10.6 + 0.6 * math.sin(t * 9), lambda t: 0.6, 33, 16, 12), 0.8, "hot", glow=True)


@design("ossrics_brand")
def ossrics_brand(k):
    """Ossric the Kiln-Father's own stamp: a black pole, a heavy square head with his mark cut in it and always hot, smoke crawling off the iron"""
    R = k.theme("foundry")
    k.mat(iron=flat(ramp("#14120f", "#221f1b", "#332f2a", "#46403a", "#5e564e", "#7a7065"), 0.64, bevel=0.14), hot=fire(HOT, 0.45, 0.55), smoke=flat(ramp("#14120f", "#221f1b", "#332f2a"), 0.5))
    pole(k, 18, "iron", 2.4)
    k.plate(rect(-7, 18, 7, 21) , 5.0, "iron")
    k.plate(P((-8.4, 21), (8.4, 21), (9, 32), (-9, 32)), 6.6, "iron")
    mark = rect(-5.6, 23, 5.6, 24.4) + rect(-1.2, 24, 1.2, 28.4) + rect(-5.4, 28, 5.4, 30)
    mark = mark + P((-5.6, 26), (-3.4, 26), (-3.4, 29)) + P((5.6, 26), (3.4, 26), (3.4, 29))
    k.plate(mark, 6.8, "hot", glow=True)
    for x, h in ((-5, 6), (0, 5), (5, 6.4)):
        k.plate(wave(lambda t, x=x: x + math.sin(t * 6), lambda t: 0.9 - 0.5 * t, 32, 32 + h, 8), 1.0, "smoke")


@design("blizzard_staff")
def blizzard_staff(k):
    """a ring of ice shards racing round a white core: the storm is always moving but the staff doesn't seem to mind"""
    R = k.theme("frost", base=0.54)
    k.mat(ice=flat(R["glow"], 0.7, bevel=0.14), white=flat(R["glow"], 0.92, bevel=0.04), iron=flat(R["dark"], 0.6))
    pole(k, 16, "iron")
    orb(k, 0, 24, 3.4, "white")
    for j in range(10):
        a = j * 2 * math.pi / 10
        k.seg((math.cos(a) * 7.4, 24 + math.sin(a) * 2.6), (math.cos(a + 0.5) * 7.4 , 24 + math.sin(a + 0.5) * 2.6), 1.5, 1.5, "ice", z=math.sin(a) * 6)
    for j in range(7):
        a = j * 2 * math.pi / 7
        k.plate(shard(math.cos(a) * 5, 24 + math.sin(a) * 5, 5.2, -math.degrees(a) + 80, 1.6), 1.0, "ice")
    k.plate(stroke((0, 16), (-5, 15), (-4, 21), 1.1) + stroke((0, 16), (5, 15), (4, 21), 1.1), 1.4, "iron")


@design("inkblot_staff")
def inkblot_staff(k):
    """the Archive's great inkwell on a stem, its pen stood in it, purple ink climbing out and hanging in drops"""
    R = k.theme("silk")
    k.mat(glass=flat(ramp("#1a1426", "#2c2240", "#40325c"), 0.6, bevel=0.2), brass=flat(BRASS, 0.64), quill=flat(R["acc"], 0.86, bevel=0.06), ink=fire(R["glow"], 0.1, 0.7))
    pole(k, 15, "dark")
    k.plate(P((-5, 15), (5, 15), (6, 18), (6, 22), (2.6, 24), (-2.6, 24), (-6, 22), (-6, 18)), 7.0, "glass")
    k.plate(rect(-4.4, 16, 4.4, 21), 7.2, "ink", glow=True)
    k.plate(rect(-2.8, 24, 2.8, 25.6), 4.6, "brass")
    k.plate(L([(0.8, 24), (5.4, 34)], 0.7), 0.9, "quill")
    k.plate(P((3, 28), (8, 33), (7, 37), (4.4, 34)) + P((5.6, 30), (3, 36), (6, 35)), 0.5, "quill")
    for x, y in ((-3, 28), (-5.6, 25.6), (-1.6, 32)):
        k.plate(P(path(qb((x, y + 1.6), (x - 1.2, y), (x, y - 1), 4), qb((x, y - 1), (x + 1.2, y), (x, y + 1.6), 4))), 1.0, "ink", glow=True)


@design("gloomvein_staff")
def gloomvein_staff(k):
    """a pick handle with a raw teal vein growing up and around it, breaking out at the top in a crown of crystal"""
    R = k.theme("weeping_mine")
    k.mat(crystal=flat(R["glow"], 0.7, bevel=0.14), oak=staves(R["wood"], 1.0, 0.6))
    pole(k, 18, "oak")
    n = 20
    for j in range(n):
        a = j * 0.9
        p_ = (math.sin(a) * 1.4, 2 + j * 0.9)
        q = (math.sin(a + 0.9) * 1.4, 2.9 + j * 0.9)
        k.seg(p_, q, 0.7, 0.7, "glow", z=math.cos(a) * 1.4, glow=True)
    for x, y, ln, a, w in ((0, 16, 14, 0, 3.6), (-2.4, 16, 10, 24, 2.8), (2.6, 16, 10, -22, 2.8), (-4, 17, 6, 50, 2), (4.4, 17, 6, -56, 2)):
        k.plate(shard(x, y, ln, a, w), 2.0, "crystal")
    k.plate(shard(0, 18, 10, 0, 1.4), 2.2, "glow", glow=True)


@design("heartvein")
def heartvein(k):
    """the Mine's heart: a fist of teal crystal in the shape of the real thing, beating, copper veins running down from it to wrap the whole staff"""
    R = k.theme("weeping_mine")
    k.mat(crystal=flat(R["glow"], 0.74, bevel=0.14), copper=flat(R["acc"], 0.62, bevel=0.1), rock=flat(R["blade"], 0.5))
    pole(k, 18, "copper")
    m = disc(-2.4, 26.4, 3.6, 12) + disc(2.6, 26, 3.8, 12) + P((-6, 25.4), (6.4, 25), (0.2, 17))
    k.plate(m, 6.4, "crystal")
    k.plate(m.inset(1.5), 7.0, "glow", glow=True)
    for a, b_ in (((-3, 19), (-1.4, 10)), ((3, 19), (1.4, 8)), ((0, 17), (0, 4))):
        k.plate(stroke(a, ((a[0] + b_[0]) / 2 + 1.4, (a[1] + b_[1]) / 2), b_, 0.7), 2.8, "copper")
    k.plate(shard(-5, 28, 5, 40, 2) + shard(5, 28, 5, -40, 2) + shard(0, 29, 6, 0, 2.2), 2.0, "crystal")


@design("kelpblack_staff")
def kelpblack_staff(k):
    """a drowned priest's crook wound in kelp, a black pearl the size of a fist caught at the top, and a thin pale light in its heart"""
    R = k.theme("tide_chapel")
    k.mat(kelp=flat(R["wrap"], 0.6, bevel=0.1), pearl=flat(ramp("#08080e", "#14141e", "#22222e", "#34344a", "#6a6a8a"), 0.5, bevel=0.2), drift=staves(R["wood"], 1.0, 0.6))
    pole(k, 18, "drift")
    for j in range(5):
        k.seg((-1.2, 4 + j * 3), (1.2, 5.6 + j * 3), 0.7, 2.4, "kelp")
    for s_ in (1, -1):
        k.plate(stroke((0, 17), (s_ * 8, 20), (s_ * 2, 30), 1.1, 10), 1.3, "kelp")
    k.plate(disc(0, 24, 5.0, 16), 6.0, "pearl")
    k.plate(disc(-1.2, 25.4, 1.1, 8), 6.3, "glow", glow=True)
    k.plate(wave(lambda t: 7 + 1.0 * math.sin(t * 8), lambda t: 0.6, 24, 6, 12), 0.4, "kelp")


@design("charm_staff")
def charm_staff(k):
    """a bandit hedge-wizard's stick hung with every lucky thing he robbed: a horseshoe, a rabbit's foot, a coin, a little brass hand, a skull that was somebody's"""
    R = k.theme("brigands_gorge")
    k.mat(iron=flat(IRON, 0.7), coin=flat(GOLD, 0.7), foot=flat(ramp("#a89a84", "#c8bca8", "#e8dcc8"), 0.6, 0.3), bone=bone(IVORY, 0.72), brass=flat(BRASS, 0.66), cord=flat(R["acc"], 0.6))
    pole(k, 24)
    k.plate(ring(0, 27, 4.0, 2.4) - rect(-1.8, 22, 1.8, 25), 1.2, "iron")
    k.box(0, 21.2, 0, 8.6, 0.8, 1.0, "cord")
    for x, y, mat in ((-4, 15.6, "foot"), (4, 16, "coin"), (-1.6, 14, "bone")):
        k.box(x, y, 0, 0.3, 21 - y, 0.3, "cord")
    k.plate(P((-4.8, 16), (-3.2, 16), (-3.2, 13.6), (-4.8, 12)), 1.4, "foot")
    k.plate(disc(4, 15, 1.5, 10), 0.5, "coin")
    k.plate(rect(-2.8, 12, -0.4, 14.2) + rect(-2.2, 11.2, -1, 12), 2.0, "bone")
    k.plate(disc(-1.6, 13.2, 0.3, 4) + disc(-0.8, 13.2, 0.3, 4), 2.1, "dark")
    k.plate(disc(0, 25, 1.4, 8), 1.0, "glow", glow=True)


@design("omen_staff")
def omen_staff(k):
    """a birdcage on a black staff, a crow's skull in it, and one pale eye open in the dark where its body would have been"""
    R = k.theme("rookery")
    k.mat(iron=flat(IRON, 0.7), bone=bone(IVORY, 0.72), void=flat(NIGHT, 0.4))
    pole(k, 14, "void")
    for j in range(6):
        a = j * math.pi / 3
        x, z = math.cos(a) * 6, math.sin(a) * 6
        k.seg((x, 14), (x * 1.1, 24), 0.6, 0.6, "iron", z=z)
        k.seg((x * 1.1, 24), (0, 31), 0.6, 0.6, "iron", z=z * 0.5)
    k.box(0, 13.8, 0, 13, 1.0, 13, "iron")
    k.box(0, 20.0, 0, 0.5, 0.5, 13, "iron")
    k.box(0, 20.0, 0, 13, 0.5, 0.5, "iron")
    k.plate(ring(0, 32.6, 1.6, 0.8), 0.7, "iron")
    k.plate(disc(0, 21, 2.3, 10), 3.4, "bone")
    k.plate(P((1.6, 22), (1.6, 19.8), (6, 19.4)), 1.4, "bone")
    k.plate(disc(-0.6, 21.8, 0.7, 6), 3.6, "glow", glow=True)


@design("fire_breath_staff")
def fire_breath_staff(k):
    """the fire-eater's twin torches on one long pole, oily rag at both ends and a long sheet of fire curling off the top"""
    R = k.theme("hollow_circus")
    red = ramp("#2a0408", "#4e0810", "#7a1018", "#a81c20", "#d0302a", "#ee5a44")
    cream = ramp("#6a5a44", "#8e7c60", "#b4a282", "#d6c8a8", "#efe4c8")
    k.mat(st=stripes(red, cream, 3.0, 0.5), rag=wrap(RAG, RAG[0], 3), flame=fire(HOT, 0.1, 0.9), gold=flat(GOLD, 0.66))
    pole(k, 22, "st", shoe="rag")
    k.box(0, 21, 0, 3.8, 4.2, 3.8, "rag")
    k.box(0, 20, 0, 3.4, 1.0, 3.4, "gold")
    k.plate(P(path(qb((-2, 25), (-6, 30), (6, 42), 12), (6, 42), qb((6.4, 32), (5, 28), (2, 25), 8))), 1.6, "flame", glow=True)
    k.plate(P(path(qb((-1, 25), (-2, 28), (3, 34), 6), qb((3, 34), (3, 29), (1, 25), 6))), 2.0, "glow", glow=True)
    k.plate(P((-1.4, -19.6), (1.4, -19.6), (0.2, -25), (-1, -22.6)), 1.4, "flame", glow=True)


@design("hexbag_staff")
def hexbag_staff(k):
    """a hag's forked stick with a bulging bag tied in the crook, stitched from something, and eyes sewn on that blink out of step"""
    R = k.theme("mirefen_coven")
    k.mat(hide=flat(ramp("#2c2214", "#44341e", "#5e4a2c", "#78603c"), 0.6, 0.3, bevel=0.1), cord=flat(R["acc"], 0.6), stick=staves(R["wood"], 1.0, 0.6), eye=flat(ramp("#c8c0a8", "#e8e0c8", "#fff8e8"), 0.7), bone=bone(IVORY, 0.7))
    pole(k, 18, "stick")
    for s_ in (1, -1):
        k.plate(stroke((0, 17), (s_ * 5, 20), (s_ * 7, 32), 1.3), 1.6, "stick")
    k.plate(P(path(qb((-3.6, 29), (-7, 22), (0, 17.6), 8), qb((0, 17.6), (7, 22), (3.6, 29), 8))), 6.0, "hide")
    k.box(0, 28.4, 0, 7.6, 1.2, 3.4, "cord")
    for x, y in ((-2.4, 23), (2.2, 24), (0, 20.4)):
        k.plate(disc(x, y, 1.4, 8), 6.2, "eye")
        k.plate(disc(x, y, 0.7, 6), 6.3, "glow", glow=True)
    k.plate(wave(lambda t: 6 + 0.6 * math.sin(t * 7), lambda t: 0.3, 30, 15, 8), 0.3, "cord")
    k.plate(rect(5, 13, 7, 15.4), 1.4, "bone")


@design("coven_broom")
def coven_broom(k):
    """the Matron's broom, the right way up for once: a great fan of black twigs bound tight, green fire running out through the bristle ends"""
    R = k.theme("mirefen_coven")
    k.mat(stick=staves(R["wood"], 1.0, 0.6), twig=flat(ramp("#14100a", "#201a12", "#30281c", "#44382a"), 0.6, 0.3), cord=wrap(R["acc"], R["dark"][0], 3))
    pole(k, 16, "stick")
    for j in range(13):
        a = math.radians(-36 + j * 6)
        k.plate(L([(0, 16), (-math.sin(a) * 20, 16 + math.cos(a) * 20 - abs(j - 6) * 0.3)], 0.8), 1.2 if j % 2 else 2.0, "twig")
    k.box(0, 14, 0, 4.6, 4.6, 4.6, "cord")
    for j in (1, 3, 5, 7, 9, 11):
        a = math.radians(-36 + j * 6)
        x, y = -math.sin(a) * 18, 16 + math.cos(a) * 18
        k.plate(P((x - 1.4, y - 2), (x + 1.4, y - 2), (x * 1.08, y + 4)), 1.0, "glow", glow=True)


@design("sandstorm_staff")
def sandstorm_staff(k):
    """an hourglass in a bronze cage, its sand running up, a tiny storm turning in each bulb"""
    k.theme("sandsunk_tomb")
    bronze = ramp("#2a1606", "#432410", "#5e3618", "#7c4c22", "#9c6630", "#bc8444", "#d8a462")
    k.mat(br=flat(bronze, 0.64, bevel=0.14), glass=flat(ramp("#6a7a70", "#94a498", "#c0d0c4"), 0.5, bevel=0.2), sand=fire(ramp("#a07028", "#d0a048", "#f0d080", "#fff0c0"), 0.2, 0.7), lapis=flat(ramp("#0e2a6e", "#163e96", "#2458c0"), 0.56))
    pole(k, 14, "lapis", shoe="br")
    k.plate(P((-5.4, 16), (5.4, 16), (5.4, 18), (0.9, 23), (5.4, 28), (5.4, 30), (-5.4, 30), (-5.4, 28), (-0.9, 23), (-5.4, 18)), 6.0, "glass")
    k.plate(P((-4.4, 16.6), (4.4, 16.6), (4.4, 17.8), (0.6, 22.4), (-0.6, 22.4), (-4.4, 17.8)), 6.2, "sand", glow=True)
    k.plate(P((-3.0, 28.6), (3.0, 28.6), (0.6, 24), (-0.6, 24)), 6.2, "sand", glow=True)
    k.plate(rect(-7, 14.4, 7, 16) + rect(-7, 30, 7, 31.6), 7.6, "br")
    for x in (-6.4, 6.4):
        k.box(x, 16, 0, 1.0, 14, 1.0, "br")
    k.plate(P((-2, 31.6), (2, 31.6), (0, 35)), 3.0, "br")


@design("bile_staff")
def bile_staff(k):
    """a sac of the Titan's bile in a basket of its ribs, sour yellow-green and thick, dripping through"""
    k.theme("fallen_titan")
    bile = ramp("#3a3a04", "#6a6a0a", "#9ea016", "#cce02a", "#ecf878")
    k.mat(bone=bone(IVORY, 0.7), sac=fire(bile, 0.2, 0.6), wrap=wrap(ramp("#2a0608", "#4a0c10", "#6e161a"), None, 3), shaft=bone(IVORY, 0.54))
    pole(k, 16, "shaft", shoe="bone")
    orb(k, 0, 24, 5.4, "sac")
    for s_ in (1, -1):
        for off in (2.4, 5.0):
            k.plate(stroke((s_ * 0.6, 16), (s_ * (off + 5), 20), (s_ * (off * 0.3), 31.4), 0.9, 8), 1.2, "bone", z=(off - 3.6) * 1.2)
    k.plate(P((-0.8, 18.6), (0.8, 18.6), (0.4, 15), (0, 11), (-0.4, 15)), 1.2, "sac", glow=True)


@design("ink_brush_staff")
def ink_brush_staff(k):
    """a calligrapher's brush for writing on the sky: lacquered bamboo, a great wet tuft that holds one black stroke, gold at the ferrule"""
    R = k.theme("jade_monastery", base=0.54)
    k.mat(bam=flat(ramp("#2a0608", "#4a0c10", "#6e1616", "#8e2020"), 0.6, bevel=0.06), gold=flat(GOLD, 0.66, bevel=0.14), tuft=flat(ramp("#0a0a0e", "#16161c", "#22222c", "#343440"), 0.6, 0.3), ink=flat(ramp("#0a0a0e", "#16161c"), 0.5))
    pole(k, 18, "bam", shoe="gold")
    k.box(0, 17, 0, 4.0, 3.0, 4.0, "gold")
    k.plate(P(path(qb((-3.4, 20), (-5.4, 26), (0, 36), 8), qb((0, 36), (5.4, 26), (3.4, 20), 8))), 3.6, "tuft")
    k.plate(L([(-2, 22), (-1, 30)], 0.4) + L([(2, 22), (1.4, 28)], 0.4), 3.7, "glow", glow=True)
    k.plate(stroke((0, 36), (7, 37), (9, 30), 1.1, 8), 0.6, "ink")


@design("tempest_staff")
def tempest_staff(k):
    """a storm vane spun up to a blur on an iron pole, its four copper cups a wheel of blue sparks"""
    R = k.theme("storm_bastion")
    k.mat(iron=flat(R["dark"], 0.66, bevel=0.12), copper=flat(ramp("#6a3414", "#9c5a24", "#c8843c", "#e8a860"), 0.6, bevel=0.14), white=flat(R["glow"], 0.92, bevel=0.02), hot=fire(R["glow"], 0.3, 0.7))
    pole(k, 28, "iron")
    for j in range(4):
        a = j * math.pi / 2 + 0.5
        x, z = math.cos(a) * 8, math.sin(a) * 8
        k.seg((0, 25), (x, 25), 0.8, 0.8, "iron", z=z / 2)
        k.box(x, 23.6, z, 3.6, 3.0, 3.6, "copper")
    for j in range(12):
        a = j * math.pi / 6
        k.seg((math.cos(a) * 10, 25), (math.cos(a + 0.6) * 10, 25), 0.6, 0.6, "hot", z=math.sin(a) * 10, glow=True)
    k.plate(P((-1.4, 28), (1.4, 28), (0, 34)), 1.4, "iron")
    k.plate(L([(0, 22), (-2, 19), (0.6, 17), (-1, 13)], 0.5), 2.2, "white", glow=True)


@design("tempest_bell")
def tempest_bell(k):
    """the Abbess's storm bell, cast with the bolt inside it for a clapper; strike it and the sky answers"""
    R = k.theme("storm_bastion")
    bronze = ramp("#1a1c24", "#2c303c", "#444a58", "#5e6678", "#7c8498", "#a0a8bc")
    k.mat(bell=flat(bronze, 0.6, bevel=0.14), white=flat(R["glow"], 0.92, bevel=0.02), iron=flat(R["dark"], 0.66), hot=fire(R["glow"], 0.3, 0.7))
    pole(k, 33, "iron")
    for s_ in (1, -1):
        k.plate(stroke((0, 33), (s_ * 9, 34), (s_ * 9, 28), 1.2), 1.4, "iron")
    k.box(0, 32.6, 0, 2.0, 2.2, 2.0, "iron")
    for j, (w, h) in enumerate(((4.4, 2), (6.2, 2), (7.6, 2), (9, 2), (10.6, 2), (13, 1.4))):
        k.box(9, 30 - sum((2, 2, 2, 2, 2, 1.4)[:j + 1]), 0, w, h, w, "bell")
    k.plate(L([(9, 18), (7.4, 15), (10.4, 13), (8.4, 9.4)], 0.8), 1.0, "white", glow=True)
    k.plate(L([(14.6, 20), (17, 23), (16, 25), (18.4, 28)], 0.5) + L([(3.2, 19), (1, 15), (2, 13)], 0.5), 0.6, "hot", glow=True)


@design("hemomancer_staff")
def hemomancer_staff(k):
    """a ring of bloody thorns round a hanging drop of red that doesn't fall, a silver crescent holding it all up"""
    R = k.theme("bloodmoon_court")
    k.mat(silver=flat(IRON, 0.72, bevel=0.14), hot=fire(RUBY, 0.3, 0.7), thorn=flat(ramp("#1a0406", "#34080a", "#561010"), 0.7, bevel=0.1), lacq=flat(ramp("#14040a", "#280a12", "#42101c"), 0.6, bevel=0.06))
    pole(k, 15, "lacq")
    k.plate(disc(0, 21, 8.4, 20) - disc(0, 24, 8.4, 20), 2.4, "silver")
    m = P(path(qb((0, 33), (-4, 26), (0, 20), 8), qb((0, 20), (4, 26), (0, 33), 8)))
    k.plate(m, 4.0, "hot", glow=True)
    for j in range(10):
        a = j * math.pi / 5
        x, y = math.cos(a) * 7, 25 + math.sin(a) * 7
        k.plate(P((x - 0.8, y), (x + 0.8, y), (x + math.cos(a + 1) * 3.6, y + math.sin(a + 1) * 3.6)), 1.0, "thorn")
    k.plate(ring(0, 25, 7.4, 6.5), 1.2, "thorn")


@design("cinder_oracle_staff")
def cinder_oracle_staff(k):
    """a three-legged brazier the Labyrinth's priests read the ashes in, carried high, coals bright, a cracked mask hanging from it"""
    R = k.theme("obsidian_labyrinth")
    k.mat(bronze=flat(BRASS, 0.6, bevel=0.14), coal=flat(ramp("#100a08", "#2a1208", "#6a1a06", "#c0400a", "#ff8a1c"), 0.5, 0.8), flame=fire(HOT, 0.1, 0.9), mask=flat(IVORY, 0.72, bevel=0.1))
    pole(k, 16, "dark")
    for s_ in (1, 0, -1):
        k.plate(stroke((0, 16), (s_ * 6, 17), (s_ * 6.4, 24), 0.9), 1.0, "bronze")
    k.plate(P((-7.4, 27.6), (7.4, 27.6), (5.0, 23), (-5.0, 23)), 7.6, "bronze")
    k.box(0, 27.2, 0, 12, 1.2, 6.4, "coal", glow=True)
    k.plate(P((-4, 28), (4, 28), (2.6, 32), (1.4, 30.4), (0, 35), (-1.4, 30.4), (-2.6, 32)), 2.0, "flame", glow=True)


@design("bulls_crown")
def bulls_crown(k):
    """the Keeper's crown: a bull's great sweep of horns on an iron pole, fire burning in the gap between the tips"""
    k.theme("obsidian_labyrinth")
    k.mat(hn=flat(HORN, 0.7, bevel=0.14), gold=flat(GOLD, 0.68, bevel=0.14), bone=bone(IVORY, 0.72), flame=fire(HOT, 0.1, 0.9), hot=fire(HOT, 0.4, 0.6), pol=flat(IRON, 0.6))
    pole(k, 18, "pol", shoe="gold")
    k.plate(P((-4, 22), (4, 22), (2.4, 14), (-2.4, 14)), 4.6, "bone")
    k.plate(disc(-1.6, 19.6, 0.9, 6) + disc(1.6, 19.6, 0.9, 6), 4.8, "hot", glow=True)
    for s_ in (1, -1):
        k.plate(P(path((s_ * 2.6, 22.6), qb((s_ * 14, 20), (s_ * 16, 28), (s_ * 7, 38), 12), (s_ * 7, 38), qb((s_ * 11, 28), (s_ * 9, 25), (s_ * 2.6, 25.6), 10))), 2.6, "hn")
        k.box(s_ * 4.6, 20.4, 0, 1.0, 4.4, 2.8, "gold")
    k.plate(P(path(qb((-3, 26), (-5, 30), (0, 37), 8), qb((0, 37), (5, 30), (3, 26), 8))), 2.0, "flame", glow=True)


@design("abyss_staff")
def abyss_staff(k):
    """five black tentacles rise from the pole and close round a sphere of nothing, the only light the rim of it"""
    R = k.theme("abyssal_lighthouse")
    fish = ramp("#08060e", "#10101a", "#1a1a2a", "#28283e", "#3a3a56")
    k.mat(tent=flat(fish, 0.66, bevel=0.1), void=flat(ramp("#000000", "#040408"), 0.3, bevel=0), rim=fire(R["glow"], 0.4, 0.6), sucker=flat(R["glow"], 0.8))
    pole(k, 14, "tent")
    k.plate(disc(0, 24, 6.0, 16), 6.0, "void")
    k.plate(ring(0, 24, 6.8, 6.0), 1.4, "rim", glow=True)
    for a0 in (0, 72, 144, 216, 288):
        pts = []
        for j in range(13):
            t = j / 12
            a = math.radians(a0 + t * 170)
            r_ = 2 + 6.4 * math.sin(t * 3.14)
            pts.append((math.cos(a) * r_, 14 + t * 20, math.sin(a) * r_))
        for j, (p_, q) in enumerate(zip(pts, pts[1:])):
            k.seg(p_[:2], q[:2], 1.5 - j * 0.1, 1.5 - j * 0.1, "tent", z=p_[2])


@design("umbra_staff")
def umbra_staff(k):
    """a crescent of pure shadow with a pale edge standing on a thin white rod, turned to face whatever you're looking at"""
    k.theme("eclipse_cathedral", base=0.5)
    k.mat(rod=flat(ramp("#a0a0b4", "#c8c8d8", "#e8e8f0"), 0.6, bevel=0.06), void=flat(ramp("#000000", "#040408", "#0a0a10"), 0.5, bevel=0.1), rim=fire(ramp("#ffe08a", "#fff6d0", "#ffffff"), 0.4, 0.6), gold=flat(GOLD, 0.66))
    pole(k, 15, "rod", shoe="gold")
    m = disc(0, 24, 9.4, 22) - disc(3.4, 25.4, 8.0, 22)
    k.plate(m, 0.8, "rim", glow=True)
    k.plate(m.inset(0.5), 2.0, "void")
    k.box(0, 14, 0, 3.0, 1.6, 3.0, "gold")
    k.plate(disc(3.6, 25, 1.0, 8), 1.0, "rim", glow=True)


@design("totality")
def totality(k):
    """the eclipse at the moment of it, carried: a black disc, a white ring and long uneven tongues of corona, on a staff of burnt bone"""
    k.theme("eclipse_cathedral", base=0.5)
    k.mat(rod=bone(ramp("#1a1412", "#2a201c", "#3e2e26", "#5a3e30"), 0.6), void=flat(ramp("#000000", "#040408"), 0.3, bevel=0), corona=fire(ramp("#d0a040", "#ffe08a", "#fff6d0", "#ffffff"), 0.2, 0.8), rim=fire(ramp("#fff6d0", "#ffffff"), 0.4, 0.6))
    pole(k, 15, "rod")
    m = Mask()
    for j in range(16):
        a = 2 * math.pi * j / 16 + 0.2 * math.sin(j * 2.3)
        ln = 9.6 + 3.0 * math.sin(j * 1.7) ** 2
        m = m + P((math.cos(a - 0.26) * 7.0, 24 + math.sin(a - 0.26) * 7.0), (math.cos(a) * ln, 24 + math.sin(a) * ln), (math.cos(a + 0.26) * 7.0, 24 + math.sin(a + 0.26) * 7.0))
    k.plate(m, 0.8, "corona", glow=True)
    k.plate(ring(0, 24, 7.6, 6.8), 1.2, "rim", glow=True)
    k.plate(disc(0, 24, 7.0, 20), 2.4, "void")


@design("cinder_cult_staff")
def cinder_cult_staff(k):
    """a cultist's mask of the Wyrm on a staff, gold beaten over a skull, its mouth a slot with embers breathing behind it"""
    k.theme("wyrms_hoard")
    k.mat(gold=flat(GOLD, 0.62, bevel=0.16), hn=flat(HORN, 0.7, bevel=0.14), hot=fire(HOT, 0.3, 0.7), red=flat(ramp("#2a0606", "#4a0c0a", "#741612"), 0.6, 0.2))
    pole(k, 16, "red", shoe="gold")
    k.plate(P((-5.4, 27), (5.4, 27), (6, 22), (3.4, 15), (-3.4, 15), (-6, 22)), 4.0, "gold")
    k.plate(P((-3.4, 23.6), (-0.8, 22.6), (-1.0, 21.6), (-3.8, 22.4)) + P((3.4, 23.6), (0.8, 22.6), (1.0, 21.6), (3.8, 22.4)), 4.2, "hot", glow=True)
    k.plate(rect(-2.6, 17.6, 2.6, 19.4), 4.2, "hot", glow=True)
    for x in (-1.4, 0, 1.4):
        k.plate(rect(x - 0.3, 17.6, x + 0.3, 19.4), 4.3, "gold")
    for s_ in (1, -1):
        k.plate(stroke((s_ * 4, 26), (s_ * 9, 28), (s_ * 8, 35), 1.4), 2.0, "hn")


@design("ash_crown")
def ash_crown(k):
    """a young dragon's skull crowned in its own burnt hoard, ash for a breath, the eye sockets lit, the jaw hanging open over the staff"""
    k.theme("wyrms_hoard")
    k.mat(bone=bone(ramp("#2a2420", "#403630", "#5a4e44", "#786a5c", "#9a8c7c", "#bcae9c"), 0.68), gold=flat(GOLD, 0.66, bevel=0.14), hot=fire(HOT, 0.3, 0.7), hn=flat(HORN, 0.72, bevel=0.14), ash=flat(ramp("#3a3a40", "#5a5a62", "#7e7e86"), 0.5), pol=flat(IRON, 0.5))
    pole(k, 16, "pol")
    k.plate(P((-5, 28), (5, 28), (6.4, 24), (9, 18), (9, 15.6), (4, 17), (0.6, 20), (-5, 20)), 4.4, "bone")
    k.plate(P((-4.6, 19), (0.4, 19.6), (7, 13.4), (6.6, 12), (0, 16), (-4.4, 16)), 3.0, "bone")
    k.plate(disc(1.2, 24.6, 1.5, 8), 4.6, "hot", glow=True)
    k.plate(P((-3.4, 28), (-1.4, 28), (-3, 33), (-4.6, 29)) + P((0, 28), (2, 28), (1.2, 33)) + P((3, 28), (4.4, 27), (5.4, 31)), 2.6, "gold")
    k.plate(stroke((-5, 26), (-11, 25), (-13, 32), 1.6), 2.4, "hn")
    k.plate(wave(lambda t: 9 + 4 * t + 1.2 * math.sin(t * 6), lambda t: 1.4 - 0.8 * t, 15, 6, 8), 0.6, "ash")


# ---------------------------------------------------------------- the world's

@design("charred_branch")
def charred_branch(k):
    """a burnt branch that hasn't noticed: black bark, red seams, smouldering at the broken end"""
    k.mat(char=flat(ramp("#0a0808", "#161210", "#241c18", "#362a22"), 0.6, 0.2, bevel=0.1), hot=fire(HOT, 0.3, 0.7), wrap=wrap(LEATHER, IRON[1], 5), dark=flat(IRON, 0.6), wood=flat(IRON, 0.5))
    pole(k, 10, "char", 2.4)
    k.plate(wave(lambda t: 3 * math.sin(t * 3) , lambda t: 1.4 - 0.7 * t, 9, 31, 20), 2.4, "char")
    k.plate(stroke((1.6, 16), (6, 18), (7, 24), 1.0) + stroke((1.0, 22), (-3, 24), (-4, 30), 0.9), 1.4, "char")
    k.plate(L([(0.6, 11), (2, 16), (1.6, 22), (1.0, 28)], 0.4) + L([(7, 24), (5.6, 19)], 0.3), 2.46, "hot", glow=True)
    k.plate(disc(0.6, 31, 1.3, 7) + disc(7, 24.6, 0.8, 6), 2.0, "hot", glow=True)


@design("ember_rod")
def ember_rod(k):
    """a copper rod with a coal in a little cage at the end, the cage worn bright from being carried"""
    copper = ramp("#3a1a08", "#6a3414", "#9c5a24", "#c8843c", "#e8a860", "#ffd090")
    k.mat(cu=flat(copper, 0.66, bevel=0.1), coal=flat(ramp("#100a08", "#2a1208", "#6a1a06", "#c0400a", "#ff8a1c", "#ffc84a"), 0.6, 0.6), wrap=wrap(LEATHER, copper[2], 5), dark=flat(copper, 0.5), wood=flat(copper, 0.5))
    pole(k, 18, "cu", 1.8)
    orb(k, 0, 23, 3.0, "coal")
    for j in range(5):
        a = j * 2 * math.pi / 5
        x, z = math.cos(a) * 3.8, math.sin(a) * 3.8
        k.seg((0, 18), (x, 21), 0.6, 0.6, "cu", z=z * 0.5)
        k.seg((x, 21), (x, 26), 0.6, 0.6, "cu", z=z)
        k.seg((x, 26), (0, 29), 0.6, 0.6, "cu", z=z * 0.5)


@design("void_eye_staff")
def void_eye_staff(k):
    """a staff that stares back: a great lidded eye of black and violet in an iron socket, the lashes spikes"""
    k.mat(iron=flat(IRON, 0.62, bevel=0.14), white=flat(ramp("#2a1a3a", "#402a56", "#5a3e78"), 0.6, bevel=0.1), iris=fire(VOID, 0.2, 0.7), pupil=flat(ramp("#000000", "#040408"), 0.3, bevel=0), wrap=wrap(NIGHT, VOID[0], 4), dark=flat(IRON, 0.6), wood=flat(NIGHT, 0.7))
    pole(k, 15, "wood")
    k.plate(disc(0, 24, 8.4, 20), 5.6, "iron")
    k.plate(disc(0, 24, 7.0, 20), 6.0, "white")
    k.plate(disc(0, 24, 4.4, 16), 6.2, "iris", glow=True)
    k.plate(P((0, 28), (1.4, 24), (0, 20), (-1.4, 24)), 6.4, "pupil")
    for j in range(9):
        a = math.radians(j * 22.5)
        k.plate(P((math.cos(a - 0.1) * 8, 24 + math.sin(a - 0.1) * 8), (math.cos(a) * 12.4, 24 + math.sin(a) * 12.4), (math.cos(a + 0.1) * 8, 24 + math.sin(a + 0.1) * 8)), 1.0, "iron")


@design("last_star")
def last_star(k):
    """the last star of the sky, caught in a silver crescent, too bright to look at, a thin night-blue staff"""
    night = ramp("#060a1a", "#0a1228", "#101c3c", "#182a54", "#22386c", "#304a86")
    star = ramp("#7ab0ff", "#b0d4ff", "#e0f0ff", "#ffffff")
    k.mat(rod=flat(night, 0.7, bevel=0.06), silver=flat(SILVER, 0.7, bevel=0.1), star=fire(star, 0.5, 0.5), wrap=wrap(night, SILVER[2], 5), dark=flat(SILVER, 0.5))
    pole(k, 15, "rod", 1.8)
    k.plate(disc(0, 24, 10.6, 24) - disc(0, 28, 9.6, 24), 2.4, "silver")
    for a, ln, w in ((0, 8, 1.8), (90, 8, 1.8), (180, 8, 1.8), (270, 8, 1.8), (45, 4, 1.2), (135, 4, 1.2), (225, 4, 1.2), (315, 4, 1.2)):
        r = math.radians(a)
        d, t_ = (-math.sin(r), math.cos(r)), (math.cos(r), math.sin(r))
        k.plate(P((t_[0] * w, 25 + t_[1] * w), (d[0] * ln, 25 + d[1] * ln), (-t_[0] * w, 25 - t_[1] * w)), 1.4, "star", glow=True)
    orb(k, 0, 25, 2.0, "star")


@design("vat_stirrer")
def vat_stirrer(k):
    """a long alchemist's paddle, holes in the blade, still dripping something that eats the floor"""
    k.mat(ash=staves(ramp("#5a4628", "#7a6238", "#9a7e4c", "#b89a62"), 1.2, 0.6), stain=flat(ramp("#2e4a0e", "#4c7a14", "#70b020", "#a0e040"), 0.7, bevel=0.1), hot=fire(ramp("#3a7a10", "#68c020", "#a4f040", "#e0ffa0"), 0.3, 0.7), wrap=wrap(LEATHER, IRON[1], 5), dark=flat(IRON, 0.6))
    pole(k, 18, "ash")
    m = P((-2, 18), (2, 18), (6, 23), (6.4, 33), (3.6, 37), (-3.6, 37), (-6.4, 33), (-6, 23))
    holes = disc(-2.6, 32, 1.4, 9) + disc(2.6, 32, 1.4, 9) + disc(0, 26.6, 1.4, 9)
    k.plate(m - holes, 1.8, "ash")
    k.plate((m - holes) & rect(-8, 28, 8, 38), 2.0, "stain")
    k.plate((m - holes) & P((-8, 31), (8, 26), (8, 38), (-8, 38)), 2.1, "hot", glow=True)
    for x, ln in ((-5.2, 12), (5.4, 7), (0.6, 5)):
        k.plate(rect(x - 0.3, 28 - ln, x + 0.3, 28) + disc(x, 28 - ln, 0.7, 6), 0.6, "hot", glow=True)


@design("augurs_rod")
def augurs_rod(k):
    """an Ash Legion augur's rod: a square basalt cage, teal fire in it, bronze lion masks at the corners"""
    bas = ramp("#0e0c12", "#1a1720", "#282430", "#383242", "#4c4458", "#665c74")
    k.mat(stone=flat(bas, 0.7, bevel=0.2), hot=fire(TEAL, 0.3, 0.7), bronze=flat(BRASS, 0.64, bevel=0.14), wrap=wrap(bas, TEAL[1], 4), wood=flat(bas, 0.6), dark=flat(bas, 0.8))
    pole(k, 16, "stone")
    for x, z in ((-4, -4), (4, -4), (-4, 4), (4, 4)):
        k.box(x, 16, z, 2.2, 13, 2.2, "stone")
        k.box(x, 16.4, z, 2.6, 1.4, 2.6, "bronze")
    k.box(0, 15, 0, 11, 1.4, 11, "stone")
    k.box(0, 29, 0, 11, 1.4, 11, "stone")
    orb(k, 0, 22.6, 3.8, "hot")
    k.plate(P((-3.6, 30.4), (3.6, 30.4), (0, 35)), 3.6, "stone")


@design("alembic_of_ruin")
def alembic_of_ruin(k):
    """a glass alembic boiling on the top of a staff, acid bright inside, copper coil spiralling down from its beak and steam at the joints"""
    copper = ramp("#3a1a08", "#6a3414", "#9c5a24", "#c8843c", "#e8a860")
    k.mat(glass=flat(ramp("#2a4a4a", "#4a7a7a", "#7eb0b0", "#bce8e8"), 0.5, bevel=0.2), acid=fire(ramp("#3a7a10", "#68c020", "#a4f040", "#e0ffa0"), 0.3, 0.6), cu=flat(copper, 0.66, bevel=0.1), brass=flat(BRASS, 0.66, bevel=0.1), wrap=wrap(LEATHER, copper[2], 4), wood=flat(copper, 0.46), dark=flat(BRASS, 0.5))
    pole(k, 15, "wood")
    k.plate(P(path((-2, 15), (2, 15), qb((7, 17), (7, 25), (2, 27), 8), (2, 31), (-2, 31), (-2, 27), qb((-7, 25), (-7, 17), (-2, 15), 8))), 6.0, "glass")
    k.plate(P(path((-1.4, 16), (1.4, 16), qb((5.4, 18), (5.6, 21), (5.4, 22), 4), (-5.4, 22), qb((-5.6, 21), (-5.4, 18), (-1.4, 16), 4))), 6.2, "acid", glow=True)
    k.plate(P((-3, 31), (3, 31), (2, 33), (-2, 33)), 3.6, "brass")
    k.plate(stroke((0, 33), (9, 37), (10, 24), 1.0, 10), 1.2, "cu")
    n = 22
    for j in range(n):
        a = j * 0.8
        k.seg((10 + math.sin(a) * 2, 24 - j * 0.7), (10 + math.sin(a + 0.8) * 2, 24 - (j + 1) * 0.7), 0.9, 0.9, "cu", z=math.cos(a) * 2)


@design("riftcaller")
def riftcaller(k):
    """the Void Herald's staff: a broken ring, its two halves held apart by what's between them, a tear of nothing with stars in it"""
    k.mat(iron=flat(ramp("#14141e", "#22222e", "#34344a", "#4e4e6a"), 0.66, bevel=0.14), void=flat(ramp("#000000", "#040408", "#0a0a14"), 0.3, bevel=0), edge=fire(VOID, 0.3, 0.7), star=flat(ramp("#ffffff", "#ffffff"), 0.5, bevel=0), wrap=wrap(NIGHT, VOID[1], 4), dark=flat(NIGHT, 0.7), wood=flat(NIGHT, 0.6))
    pole(k, 13, "wood")
    tear = P(path(qb((0, 33), (-3.6, 25), (0, 17), 8), qb((0, 17), (3.6, 25), (0, 33), 8)))
    k.plate(tear, 1.2, "edge", glow=True)
    k.plate(tear.inset(0.5), 1.6, "void")
    for x, y in ((-0.6, 28), (0.8, 24), (-0.2, 21)):
        k.box(x, y, 0.85, 0.5, 0.5, 0.2, "star")
    r_ = ring(0, 25, 12.4, 9.6)
    k.plate(r_ & rect(-14, 15, -5, 35), 3.0, "iron")
    k.plate(r_ & rect(5, 15, 14, 35), 3.0, "iron")
    k.plate(P((-1.8, 14), (1.8, 14), (0.4, 17), (-0.4, 17)) + rect(-7.4, 12.4, 7.4, 14), 2.4, "iron")
    for s_ in (1, -1):
        k.plate(stroke((s_ * 7, 13), (s_ * 9, 13.4), (s_ * 9.6, 15.6), 1.4), 2.4, "iron")


@design("black_accord")
def black_accord(k):
    """the black half of a bargain: an iron staff with two hands clasped at the top, a burning violet coal held between the palms"""
    k.mat(iron=flat(FE, 0.56, bevel=0.14), gold=flat(GOLD, 0.66, bevel=0.14), hot=fire(VOID, 0.4, 0.6), wrap=wrap(NIGHT, GOLD[3], 4), dark=flat(IRON, 0.7), wood=flat(FE, 0.4))
    pole(k, 16)
    orb(k, 0, 24, 3.4, "hot")
    for s_, m_ in ((1, "iron"), (-1, "gold")):
        k.plate(P((s_ * 1.0, 15), (s_ * 8, 17), (s_ * 8.6, 26), (s_ * 5.4, 30), (s_ * 3.4, 26), (s_ * 4.6, 22), (s_ * 3, 19)), 2.4, m_)
        for j, h in enumerate((33, 34.4, 33.4)):
            k.plate(L([(s_ * (3 + j * 1.4), 28 - j * 0.6), (s_ * (1.0 + j * 1.0), h)], 1.0), 1.6, m_)


@design("apprentice_black_staff")
def apprentice_black_staff(k):
    """a first-year's stick with a chunk of burning slag jammed in a split at the top. It'll do"""
    R = k.theme("foundry")
    k.mat(oak=staves(ramp("#3a2410", "#52341c", "#6e4826", "#8c6034"), 1.0, 0.6), hot=flat(R["glow"], 0.6, 0.3, bevel=0.2), cord=wrap(RAG, RAG[0], 3), wood=flat(IRON, 0.5))
    pole(k, 12, "oak", grip="cord", shoe="oak")
    for s_ in (1, -1):
        k.plate(stroke((s_ * 0.8, 11), (s_ * 4, 14), (s_ * 2.8, 21), 1.0), 1.4, "oak")
    k.plate(disc(0, 16.4, 3.2, 7), 3.0, "hot", glow=True)
