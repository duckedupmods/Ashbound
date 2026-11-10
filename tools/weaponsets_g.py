"""Spears: a long shaft, the hands round the origin, the head from y 13 up to about 36."""
import math

from voxsword import ramp
from weaponsets import design, qb, path, P, L, disc, ring, rect, wave, taper, Mask, flat, fire, staves, steel, honed, bone, gem, at, lit, wrap, stripes, facet_of
from weaponsets_a import BRASS, GOLD, IRON, LEATHER
from weaponsets_c import shard
from weaponsets_d import RUBY, SILVER, feathers, links, stroke
from weaponsets_e import CORK, HORN, IVORY, RAG


def shaft(k, top, bottom=-24.0, w=1.8, mat="wood", grip="wrap", shoe="dark"):
    k.box(0, bottom, 0, w, top - bottom, w, mat, tag="haft")
    k.box(0, -4.0, 0, w + 0.4, 8.0, w + 0.4, grip, tag="grip")
    k.box(0, bottom - 1.4, 0, w + 0.6, 1.8, w + 0.6, shoe)


def socket(k, y, h=3.0, w=2.8, mat="dark"):
    k.box(0, y, 0, w, h, w, mat)
    k.box(0, y + h - 0.6, 0, w + 0.8, 0.8, w + 0.8, mat)


@design("bilge_boathook")
def bilge_boathook(k):
    """a real boathook: an iron spike with a blunt recurved hook beside it, the shaft black with tar, rope served round the grip"""
    R = k.theme("cellar", base=0.5)
    k.mat(rope=wrap(R["acc"], R["dark"][1], 4))
    shaft(k, 16, grip="rope")
    socket(k, 14, 3.6)
    m = P((-1.0, 17), (1.0, 17), (0.7, 26), (0, 31), (-0.7, 26)) + P(path(qb((0.8, 18), (6.4, 18.4), (6.2, 24.6), 8), (6.2, 24.6), (4.2, 26.0), (4.6, 23), qb((4.2, 20.6), (2, 20.4), (0.8, 21), 6)))
    k.forge(m, 1.5, step=1)


@design("gibbet_hook")
def gibbet_hook(k):
    """the crook they lift the body down with: one wide hook of black iron, a length of chain, a gibbet nail for a spike"""
    R = k.theme("gallows", base=0.48)
    k.mat(chain=flat(R["blade"], 0.76, bevel=0.14), hemp=wrap(R["wrap"], R["dark"][0], 4))
    shaft(k, 16, grip="hemp")
    socket(k, 14, 3.4)
    m = P(path((-1.2, 17), (1.2, 17), (1.0, 23), qb((1.0, 27), (5.8, 30), (6.8, 25.6), 8), (6.8, 25.6), (5.0, 22.4), (8.4, 24.4), qb((9.6, 33.4), (-0.4, 34.4), (-1.2, 25), 12)))
    k.forge(m, 1.7, step=1)
    links(k, [(5.6, 22.8), (5.4, 20.4), (5.8, 18), (5.2, 15.6), (5.6, 13.2)], "chain")
    k.plate(ring(5.6, 12, 1.5, 0.7), 0.7, "chain")


@design("stagtine_spear")
def stagtine_spear(k):
    """three tines of a Rotwood stag's antler bound to a dead sapling: the long one the point, the brow tines forked out either side"""
    R = k.theme("rotwood", base=0.5)
    k.mat(bone=bone(R["blade"], 0.68), edgeb=flat(R["blade"], 0.86, bevel=0.06), moss=flat(R["wrap"], 0.6), cord=wrap(R["wrap"], R["dark"][1], 3))
    shaft(k, 15, grip="cord")
    m = P(path(qb((-1.6, 13), (-1.8, 25), (1.4, 35), 10), (1.4, 35), qb((1.8, 25), (1.8, 20), (1.6, 13), 8)))
    m = m + stroke((1.0, 19), (6.6, 20), (7.0, 28), 1.5) + stroke((-1.0, 16.4), (-6.8, 17), (-7.4, 25), 1.4) + stroke((1.0, 25), (4.0, 26), (4.8, 30), 1.0)
    k.plate(m, 1.6, "edgeb")
    k.plate(m.inset(0.5), 2.2, "bone")
    k.box(0, 12, 0, 3.8, 3.4, 3.2, "moss")
    k.box(0, 12.8, 0, 2.6, 1.0, 3.5, "cord")


@design("gravespike")
def gravespike(k):
    """a wrought iron grave cross pulled out of the ground and sharpened at the wrong end: scrolled arms, a dead candle wired to it"""
    R = k.theme("crypt", base=0.5)
    k.mat(iron=flat(R["blade"], 0.54, bevel=0.14), wax=flat(R["acc"], 0.72, bevel=0.1))
    shaft(k, 18, mat="iron")
    k.forge(P((-1.5, 18), (1.5, 18), (1.1, 28), (0, 36), (-1.1, 28)), 1.5)
    k.plate(rect(-6.4, 22, 6.4, 23.4), 1.8, "iron")
    for s_ in (1, -1):
        k.plate(ring(s_ * 7.0, 24.0, 1.7, 0.8), 1.6, "iron")
        k.plate(ring(s_ * 7.0, 21.2, 1.3, 0.6), 1.6, "iron")
    k.plate(ring(0, 25.0, 0.1 + 1.8, 0.9), 2.0, "iron")
    k.box(3.6, 23.4, 0, 1.3, 3.4, 1.3, "wax")
    k.box(3.6, 26.8, 0, 0.3, 0.8, 0.3, "dark")


@design("beak_cane")
def beak_cane(k):
    """a plague doctor's walking stick: a long black cane topped with a bird's skull, its beak the blade, a brass ring at the throat and a posy of green herbs"""
    R = k.theme("plague", base=0.5)
    k.mat(skull=bone(ramp("#6a6048", "#8e8468", "#b0a688", "#cec6a8", "#e8e2c8", "#f8f4e6"), 0.7), edgeb=flat(R["blade"], 0.84), brass=flat(R["dark"], 0.62), cane=flat(R["acc"], 0.56), herb=flat(ramp("#1a3a14", "#2e5c1e", "#4a8028", "#74a838"), 0.6, 0.3))
    shaft(k, 15, mat="cane", shoe="brass")
    socket(k, 14, 2.0, 2.6, "brass")
    k.plate(disc(0, 19, 3.2, 12), 4.4, "skull")
    k.plate(disc(-1.1, 19.8, 1.0, 8) + disc(1.1, 19.8, 1.0, 8), 4.6, "glow", glow=True)
    k.forge(P((-1.8, 20), (1.8, 20), (1.3, 28), (0, 37), (-1.3, 28)), 2.0, step=1, rim="edgeb")
    for x, ln, a in ((-1.0, 5, 0.5), (0, 6, 0), (1, 5, -0.5), (-2, 4, 1)):
        k.seg((x * 0.6, 16), (x * 0.6 - math.sin(a) * ln + 2.0, 16 - math.cos(a) * ln), 0.7, 0.7, "herb")
    k.box(0, 14.6, 0, 3.0, 1.1, 3.0, "brass")


@design("surgeons_probe")
def surgeons_probe(k):
    """the longest instrument on the tray: a slim steel rod that ends in a tiny, terribly exact hooked tip, graduated, a brass collar, a bead of green at the eye"""
    R = k.theme("plague", base=0.6)
    k.mat(rod=flat(R["blade"], 0.72, bevel=0.1), mark=flat(R["blade"], 0.2), brass=flat(R["dark"], 0.64))
    shaft(k, 18, mat="rod", shoe="brass", grip="wrap")
    k.forge(P(path((-0.9, 18), (0.9, 18), (0.7, 33), qb((0.7, 36), (3.4, 37), (3.8, 34.2), 6), (3.8, 34.2), (2.6, 33.6), (3.0, 35), qb((2.6, 35.6), (1.4, 35.4), (1.4, 33), 4), (-0.7, 33))), 1.2, step=1)
    for y in range(-14, 16, 2):
        k.box(0.4, y, 0, 1.4 if y % 6 == 0 else 1.0, 0.4, 2.0, "mark")
    k.plate(rect(-2.6, 16.8, 2.6, 18.4), 2.6, "brass")
    k.plate(disc(0, 24, 1.2, 8), 1.5, "glow", glow=True)


@design("faceless_lance")
def faceless_lance(k):
    """a tall white oval of stone with one slit through it where an eye would go: the Temple's idea of a spearhead, a thin gold rod running up behind"""
    R = k.theme("temple", base=0.72, ridge=0.08)
    k.mat(gold=flat(R["acc"], 0.64), rod=flat(R["blade"], 0.66))
    shaft(k, 16, mat="dark", shoe="gold")
    socket(k, 14, 2.2, 2.6, "gold")
    m = P(path(qb((0, 15.6), (-7, 21), (-3.0, 30), 8), (0, 36.6), qb((3.0, 30), (7, 21), (0, 15.6), 8))) - rect(-2.6, 24.4, 2.6, 25.4)
    k.forge(m, 1.6)
    k.plate(rect(-2.6, 24.4, 2.6, 25.4), 0.7, "glow", glow=True)
    k.inlay(L([(0, 17), (0, 23)], 0.4), 1.6, "gold")


@design("bonewright_pike")
def bonewright_pike(k):
    """a rib ground straight, bound with brass into a vertebra collar: the shaft is a long chain of bones, the Ossuary wastes nothing"""
    R = k.theme("ossuary", base=0.5)
    k.mat(bone=bone(R["acc"], 0.68), edgeb=flat(R["acc"], 0.88, bevel=0.06), brass=flat(R["dark"], 0.62))
    shaft(k, 16, mat="bone", shoe="brass")
    for y in (-20, -14, 6, 10):
        k.box(0, y, 0, 2.8, 1.2, 2.8, "edgeb")
    k.forge(P(path(qb((-2.2, 17), (-2.4, 27), (1.4, 36.4), 10), (1.4, 36.4), qb((2.4, 27), (2.2, 22), (2.2, 17), 8))), 2.2, step=1, rim="edgeb", body="bone")
    k.plate(P((-1.8, 14), (1.8, 14), (3.0, 17.4), (-3.0, 17.4)) + P((-3.0, 16), (-6, 17.4), (-3.4, 18)) + P((3.0, 16), (6, 17.4), (3.4, 18)), 3.0, "bone")
    k.plate(rect(-3.0, 16.6, 3.0, 17.4), 3.2, "brass")


@design("kiln_pike")
def kiln_pike(k):
    """a forge poker as long as a horse: black bar, a bent hook at the end for dragging out clinker, the working end lit from inside"""
    R = k.theme("foundry", base=0.46)
    from weaponsets import heat
    hot = ramp("#120a08", "#2a0e08", "#5a1206", "#9a2206", "#e04a0a", "#ff8a1c", "#ffc84a", "#fff0b0")
    k.mat(iron=flat(R["blade"], 0.6, bevel=0.14), hoth=heat(hot, 16, 34))
    shaft(k, 16, mat="iron")
    m = P(path((-1.3, 16), (1.3, 16), (1.0, 28), qb((1.0, 32), (4, 33), (6.2, 30.4), 6), (6.2, 30.4), (7.6, 33), qb((6, 36.6), (-1.0, 37), (-1.2, 28), 8)))
    k.plate(m, 2.2, "hoth", glow=True)
    k.box(0, 8, 0, 3.0, 1.2, 3.0, "dark")
    k.box(0, 5.0, 0, 3.0, 1.2, 3.0, "dark")
    k.plate(ring(0, -27.4, 1.8, 0.9), 1.4, "iron")


@design("frostbound_pike")
def frostbound_pike(k):
    """a marching pike gone white: the leaf blade lost in a long spear of ice, more ice bearded down the shaft, all leaning one way"""
    R = k.theme("frost", base=0.5)
    k.mat(ice=flat(R["glow"], 0.68, bevel=0.14), white=flat(R["glow"], 0.92, bevel=0.04), wood=flat(R["wood"], 0.6, bevel=0.06))
    shaft(k, 16)
    socket(k, 14, 2.6)
    m = shard(0, 16, 21, 0, 4.6) + shard(1.2, 19, 12, -14, 2.8) + shard(-1.2, 20, 10, 14, 2.6) + shard(1.6, 15, 7, -40, 2.0) + shard(-1.6, 16, 6, 44, 1.8)
    k.plate(m, 2.0, "ice")
    k.plate(shard(0, 18, 15, 0, 1.6), 2.2, "white")
    for y, ln in ((10, 5), (5, 4), (-9, 5.4), (-15, 4)):
        k.plate(P((-1.0, y), (1.0, y), (2.6, y - ln), (0.4, y - 1.2)), 2.1, "ice")


@design("wintermarch")
def wintermarch(k):
    """the procession's standard and its execution: a tall halberd, axe crescent and back spike, rimed; the Marshal's long red banner hanging stiff from the crossbar"""
    R = k.theme("frost", base=0.54)
    k.mat(red=flat(R["acc"], 0.6, bevel=0.14), white=flat(R["glow"], 0.92, bevel=0.04), silver=flat(R["blade"], 0.7))
    shaft(k, 18, mat="dark", shoe="silver")
    k.forge(P((-1.2, 18), (1.2, 18), (0.9, 30), (0, 37), (-0.9, 30)), 1.6)
    k.forge(P(path((1, 25.4), qb((6, 28), (9.8, 26), (10.6, 30.6), 6), (10.6, 30.6), qb((12.6, 24), (12.6, 20), (9.8, 15.0), 8), qb((9.2, 18), (6, 18), (1, 19.8), 6))), 1.5, step=1)
    k.forge(P((-1, 21), (-1, 25), (-7.6, 22.6)), 1.5, step=1)
    k.box(0, 17.2, 0, 3.2, 1.8, 3.2, "silver")
    k.box(0, 12.6, 0, 19, 0.9, 1.2, "silver")
    flag = P((-9.2, 12.6), (9.2, 12.6), (9.2, 3), (6, 0), (3, 3.4), (0, -2.0), (-3, 3.4), (-6, 0), (-9.2, 3))
    k.plate(flag, 0.8, "red")
    for a in (0, 60, 120):
        r = math.radians(a)
        c, s_ = math.cos(r) * 3.0, math.sin(r) * 3.0
        k.inlay(L([(-c, 7 - s_), (c, 7 + s_)], 0.6), 0.8, "white")


@design("spindle_spear")
def spindle_spear(k):
    """a drop spindle the height of a man, its fat cop of silk wound round the shaft below a long needle point, the whorl for a guard"""
    R = k.theme("silk", base=0.56)
    k.mat(silk=flat(R["acc"], 0.72, bevel=0.06), sw=stripes(R["acc"], ramp("#a8a294", "#c4bfb2", "#dcd8cc"), 1.0, 0.8, 0.6), whorl=flat(R["wood"], 0.6, bevel=0.14), wood=staves(R["wood"], 1.0, 0.6))
    shaft(k, 18)
    k.forge(taper(1.0, 0.7, 18, 30, 37.6), 1.4)
    for j, r_ in enumerate((1.6, 2.6, 3.4, 3.9, 4.1, 3.9, 3.4, 2.6, 1.6)):
        k.box(0, 8 + j * 1.2, 0, r_ * 2, 1.25, r_ * 2, "sw")
    k.plate(disc(0, 6.4, 5.2) & rect(-6, 5.6, 6, 7.2), 5.6, "whorl")
    k.box(0, 5.6, 0, 9.4, 1.6, 9.4, "whorl")
    k.plate(stroke((3.4, 12), (8, 8), (6, 0), 0.4), 0.4, "silk")


@design("drill_lance")
def drill_lance(k):
    """a rock drill driven by hand: a fluted steel auger, a copper gearbox and the crank sticking out to the side; crystal dust glowing in the flutes"""
    R = k.theme("weeping_mine", base=0.5)
    k.mat(iron=flat(R["blade"], 0.7, bevel=0.14), copper=flat(R["acc"], 0.62), hot=fire(R["glow"], 0.3, 0.6))
    shaft(k, 15)
    n = 26
    for j in range(n):
        a = j * 0.85
        r_ = 2.6 * (1 - j / n) + 0.3
        y = 18 + j * 0.72
        k.seg((-math.cos(a) * r_, y), (math.cos(a) * r_, y + 0.5), 1.0, 1.4, "iron", z=math.sin(a) * 0.6)
    k.box(0, 17, 0, 1.0, 19, 1.0, "hot", glow=True)
    k.box(0, 13, 0, 5.4, 4.6, 4.2, "copper")
    k.box(0, 12.4, 0, 4.0, 0.9, 4.6, "dark")
    k.plate(rect(2.6, 15, 6.4, 15.8) + rect(5.8, 12, 6.6, 15.8) + rect(5.0, 11.2, 7.4, 12.4), 1.0, "iron")


@design("tide_harpoon")
def tide_harpoon(k):
    """a chapel fisherman's harpoon: a broad arrow head with two swept barbs, a bone foreshaft and a coil of wet line round the shaft"""
    R = k.theme("tide_chapel", base=0.5)
    k.mat(line=flat(R["acc"], 0.64), bone=bone(R["acc"], 0.72))
    shaft(k, 18)
    k.box(0, 14, 0, 2.2, 8, 2.2, "bone")
    k.forge(P((-1, 22), (1, 22), (1.2, 25), (4.6, 21), (3.6, 26), (1.4, 29), (0, 36), (-1.4, 29), (-3.6, 26), (-4.6, 21), (-1.2, 25)), 1.5)
    for j in range(7):
        k.box(0, 0 + j * 0.9, 0, 3.8 + (j % 2) * 0.4, 0.7, 3.8, "line")
    k.plate(stroke((0, 3), (6, 4), (5, -5), 0.5) + stroke((5, -5), (4, -9), (2, -8), 0.5), 0.5, "line")


@design("pike_of_the_pass")
def pike_of_the_pass(k):
    """what the brigands plant at the head of the pass: a rough pike with a skull jammed down it, a toll pouch and a red rag"""
    R = k.theme("brigands_gorge", base=0.48)
    k.mat(skull=bone(IVORY, 0.72), rag=flat(R["wrap"], 0.64), coin=flat(GOLD, 0.68), pouch=flat(LEATHER, 0.7, bevel=0.14))
    shaft(k, 16)
    socket(k, 14, 3.0)
    k.forge(P((-2.0, 17), (2.0, 17), (2.6, 21), (0.4, 37), (-2.2, 24)), 1.6)
    s_ = P(path((-3.2, 22.4), (3.2, 22.4), (3.8, 25.6), (2.4, 28.6), (-2.4, 28.6), (-3.8, 25.6)))
    k.plate(s_, 5.0, "skull")
    k.plate(rect(-2.2, 19.8, 2.2, 22.6), 3.6, "skull")
    k.inlay(disc(-1.6, 24.6, 0.9, 8) + disc(1.6, 24.6, 0.9, 8), 5.0, "dark")
    k.inlay(rect(-1.4, 20.2, -0.9, 21.6) + rect(-0.2, 20.2, 0.2, 21.6) + rect(0.9, 20.2, 1.4, 21.6), 3.6, "dark")
    k.plate(P((-0.8, 13), (-8.8, 13.4), (-7.0, 10.2), (-9.4, 7.4), (-0.8, 9)), 0.8, "rag")
    k.box(2.6, 6.0, 0, 0.4, 2.6, 0.4, "pouch")
    k.plate(disc(2.6, 4.6, 2.0, 10), 2.4, "pouch")
    k.plate(disc(1.8, 4.2, 0.6, 6) + disc(3.2, 3.6, 0.6, 6), 2.6, "coin")


@design("rookery_spear")
def rookery_spear(k):
    """a heron-beak head on a long pale shaft, a bundle of black flight feathers bound under it with red thread"""
    R = k.theme("rookery", base=0.46, edge=0.72)
    k.mat(feather=flat(R["blade"], 0.5, bevel=0.14), thread=flat(RUBY, 0.56), shaftw=flat(R["acc"], 0.62, bevel=0.06), quill=flat(R["acc"], 0.86))
    shaft(k, 18, mat="shaftw")
    k.forge(P((-1.5, 18), (1.5, 18), (1.0, 30), (0, 37), (-1.0, 30)), 1.5)
    for s_ in (1, -1):
        for j, (ln, sw) in enumerate(((12, 8), (11, 22), (9, 36))):
            r = math.radians(sw)
            d = (s_ * math.sin(r), -math.cos(r))
            t_ = (-d[1], d[0])
            o = (s_ * 0.6, 16)
            k.plate(P(o, (o[0] + d[0] * ln * 0.6 + t_[0] * 1.1, o[1] + d[1] * ln * 0.6 + t_[1] * 1.1), (o[0] + d[0] * ln, o[1] + d[1] * ln), (o[0] + d[0] * ln * 0.6 - t_[0] * 1.1, o[1] + d[1] * ln * 0.6 - t_[1] * 1.1)), 0.7, "feather")
    k.box(0, 15, 0, 3.0, 2.4, 3.0, "thread")


@design("nevermore")
def nevermore(k):
    """the great black bird itself on a pole: a raven's skull with a beak as long as a sword, wings half open behind it, an eye of pale fire"""
    R = k.theme("rookery", base=0.42, edge=0.68)
    k.mat(skull=bone(IVORY, 0.64), beak=steel(HORN, 0.6, 0.14), beakedge=honed(HORN, 0.92), feather=flat(R["blade"], 0.4, bevel=0.16), quill=flat(R["acc"], 0.72), wood=flat(R["dark"], 0.7, bevel=0.06))
    shaft(k, 15)
    k.plate(disc(0, 18.4, 3.6, 12), 5.0, "skull")
    k.plate(disc(-1.3, 19, 1.1, 8) + disc(1.3, 19, 1.1, 8), 5.2, "glow", glow=True)
    k.forge(P(path(qb((-2.4, 21), (-2.0, 31), (2.4, 39), 10), (2.4, 39), qb((1.6, 31), (2.8, 26), (2.4, 21), 8))), 2.2, step=1, body="beak", rim="beakedge", ridge=-0.2)
    for s_ in (1, -1):
        m = feathers(s_, 17, 7, 17, 92, 1.3)
        k.plate(m, 0.9, "feather")
        for a in (12, 40):
            r = math.radians(a + 8)
            k.plate(L([(s_ * 1.4, 17), (s_ * (1.4 + math.sin(r) * 14), 17 + math.cos(r) * 14)], 0.3), 1.0, "quill")


@design("lion_tamer_lance")
def lion_tamer_lance(k):
    """a tamer's goad: a gilded lion's head roaring a spike out of its mouth, a mane of red and gold rays, the pole striped like the ring"""
    R = k.theme("hollow_circus", base=0.6)
    red = ramp("#2a0408", "#4e0810", "#7a1018", "#a81c20", "#d0302a", "#ee5a44")
    cream = ramp("#6a5a44", "#8e7c60", "#b4a282", "#d6c8a8", "#efe4c8", "#fff8e8")
    k.mat(pole=stripes(red, cream, 3.0, 0.5), gold=flat(GOLD, 0.66, bevel=0.14), mane=flat(red, 0.6, bevel=0.14), lion=flat(GOLD, 0.52, bevel=0.14))
    shaft(k, 14, mat="pole", shoe="gold")
    mane = Mask()
    for j in range(14):
        a = 2 * math.pi * j / 14
        mane = mane + P((math.cos(a - 0.26) * 3.6, 20 + math.sin(a - 0.26) * 3.6), (math.cos(a) * (8.4 if j % 2 else 7.0), 20 + math.sin(a) * (8.4 if j % 2 else 7.0)), (math.cos(a + 0.26) * 3.6, 20 + math.sin(a + 0.26) * 3.6))
    k.plate(mane, 1.4, "mane")
    k.plate(disc(0, 20, 4.8, 14), 3.4, "lion")
    k.forge(P((-1.4, 21), (1.4, 21), (1.0, 31), (0, 38), (-1.0, 31)), 1.4)
    k.plate(rect(-2, 19.4, 2, 21.2), 3.6, "dark")
    for s_ in (1, -1):
        k.plate(disc(s_ * 2.0, 22.8, 0.7, 8), 3.6, "gold")
    k.box(0, 13.4, 0, 3.2, 2.4, 3.2, "gold")


@design("eel_spear")
def eel_spear(k):
    """a marsh leister: five flat barbed tines fanned from one socket, an eel still wrapped round them, its eye gone milky"""
    R = k.theme("mirefen_coven", base=0.5)
    eel = ramp("#0a100a", "#141e14", "#203020", "#2e442c", "#3e5a38")
    k.mat(eel=flat(eel, 0.6, bevel=0.1), belly=flat(ramp("#6a6a44", "#8e8e60", "#b4b488"), 0.6), eye=flat(R["acc"], 0.8), hot=fire(R["glow"], 0.3, 0.6))
    shaft(k, 15)
    socket(k, 13, 3.0, 3.2)
    for x0, x1, top in ((-2.4, -6.2, 30), (-1.2, -3.0, 33), (0, 0, 35.6), (1.2, 3.0, 33), (2.4, 6.2, 30)):
        m = L([(x0, 16), (x1, top - 3)], 1.1) + P((x1 - 0.8, top - 3.4), (x1 + 0.8, top - 3.4), (x1, top))
        m = m + P((x1 + 0.5, top - 6), (x1 + 1.8, top - 7.4), (x1 + 0.5, top - 4.6))
        k.plate(m, 1.1, "edge")
    e = wave(lambda t: 6.8 * math.sin(t * 6.6), lambda t: 1.3 * (1 - abs(t - 0.5) * 0.8), 15, 29, 40)
    k.plate(e, 2.0, "eel")
    x = 6.8 * math.sin(6.6)
    k.plate(disc(x, 29, 1.5, 8), 2.0, "eel")
    k.plate(disc(x - 0.5, 29.4, 0.45, 6), 2.1, "eye")


@design("sunspear")
def sunspear(k):
    """a gold spear of the sun cult: the head is a long hooked ray, a lapis disc set in the socket with rays standing round its top half"""
    k.theme("sandsunk_tomb", base=0.56)
    lapis = ramp("#081a4a", "#0e2a6e", "#163e96", "#2458c0", "#4a84e0")
    k.mat(blade=steel(GOLD, 0.56, 0.14), edge=honed(ramp("#a06018", "#d8982c", "#f6d060", "#fff0b0", "#ffffff"), 0.7), lapis=flat(lapis, 0.56), gold=flat(GOLD, 0.66), sun=fire(ramp("#e07010", "#ffa81c", "#ffd84a", "#fff4a8"), 0.3, 0.7), wood=flat(lapis, 0.46, bevel=0.06), wrap=wrap(GOLD, lapis[2], 3))
    shaft(k, 15, shoe="gold")
    k.forge(P((-2.2, 19), (2.2, 19), (1.4, 31), (0, 38), (-1.4, 31)), 1.6)
    for j in range(9):
        a = math.radians(j * 22.5)
        ln = 10 if j % 2 else 8
        k.plate(P((math.cos(a - 0.15) * 3.8, 18 + math.sin(a - 0.15) * 3.8), (math.cos(a) * ln, 18 + math.sin(a) * ln), (math.cos(a + 0.15) * 3.8, 18 + math.sin(a + 0.15) * 3.8)), 1.0, "sun", glow=True)
    k.plate(disc(0, 18, 4.4, 14), 2.8, "gold")
    k.plate(disc(0, 18, 3.2, 12), 3.0, "lapis")
    k.box(0, 13.6, 0, 3.0, 1.2, 3.0, "gold")


@design("femur_spear")
def femur_spear(k):
    """the Titan's little finger bone for a shaft and a flake knapped from its tooth for a head, lashed with its own tendon"""
    k.theme("fallen_titan", base=0.5)
    meat = ramp("#2a0608", "#4a0c10", "#6e161a", "#942428", "#b83c3a")
    k.mat(bone=bone(IVORY, 0.66), edgeb=flat(IVORY, 0.92, bevel=0.04), sinew=wrap(meat, meat[0], 3), knob=flat(IVORY, 0.76, bevel=0.1))
    shaft(k, 15, w=2.4, mat="bone", grip="sinew", shoe="knob")
    k.plate(disc(-1.2, -26.4, 2.0, 8) + disc(1.2, -26.4, 2.0, 8), 3.2, "knob")
    m = P((-3.0, 15), (3.0, 15), (4.0, 20), (2.4, 25), (1.6, 28), (0, 37), (-1.8, 29), (-2.6, 25), (-4.0, 20))
    for x, y in ((-3.6, 21), (-2.2, 26), (3.6, 22), (2.2, 27)):
        s_ = 1 if x > 0 else -1
        m = m - P((x + s_ * 1.2, y - 1), (x - s_ * 0.6, y), (x + s_ * 1.2, y + 1))
    k.forge(m, 2.0, step=1, rim="edgeb", body="bone")
    for j in range(5):
        k.seg((-3.0, 13.6 + j * 0.8), (3.0, 14.4 + j * 0.8), 0.6, 3.0, "sinew")


@design("crescent_spear")
def crescent_spear(k):
    """a monk's spade, both ends sharp: a flat crescent at the bottom for the staff's butt, a broad shovel at the top and rings that chime"""
    R = k.theme("jade_monastery", base=0.54)
    k.mat(gold=flat(GOLD, 0.64, bevel=0.14), rod=flat(R["wood"], 0.6, bevel=0.06), dark=flat(GOLD, 0.48))
    k.box(0, -24, 0, 1.8, 40, 1.8, "rod", tag="haft")
    k.box(0, -4, 0, 2.2, 8, 2.2, "wrap", tag="grip")
    k.forge(P(path((-1.4, 16), (1.4, 16), qb((5.4, 20), (5.2, 27), (3.8, 29.6), 6), (3.8, 29.6), (0, 33), (-3.8, 29.6), qb((-5.2, 27), (-5.4, 20), (-1.4, 16), 6))), 1.5)
    k.forge(disc(0, -18.4, 8.2) - disc(0, -15.6, 8.0) + rect(-1.2, -26, 1.2, -24), 1.4)
    for s_ in (1, -1):
        k.plate(ring(s_ * 3.0, 15.0, 1.6, 0.9), 0.5, "gold")


@design("heavens_guandao")
def heavens_guandao(k):
    """Guan's own glaive for a hall of statues: a huge curved jade blade with a back spine of clouds, a gold dragon's mouth biting it at the socket, red silk flying"""
    R = k.theme("jade_monastery", base=0.54)
    k.mat(gold=flat(GOLD, 0.66, bevel=0.14), silk=flat(ramp("#3a0608", "#600c0e", "#8a1416", "#b42020", "#dc3a30"), 0.6, bevel=0.14), edge=honed(R["blade"], 0.86), wood=flat(ramp("#2a0608", "#4a0c10", "#6e1616"), 0.6, bevel=0.06))
    shaft(k, 16, w=2.1, shoe="gold")
    m = P(path((-2.0, 15), qb((-3.4, 26), (-1.0, 33), (7.0, 42), 12), (7.0, 42), qb((9.6, 32), (9.4, 24), (2.4, 15), 12)))
    for y in (19, 23, 27, 31):
        x = -3.0 + (y - 15) * 0.1
        m = m + disc(x, y, 1.4, 8)
    k.forge(m, 1.8, ridge=-0.2)
    k.plate(P((-3.4, 13.6), (3.4, 13.6), (4.4, 19.4), (2.0, 17.6), (0.4, 21), (-1.6, 17.6), (-4.4, 19.8)), 3.2, "gold")
    k.plate(disc(-1.6, 15.2, 0.6, 6) + disc(1.6, 15.2, 0.6, 6), 3.4, "silk")
    k.plate(wave(lambda t: 3 + 7 * t + 1.2 * math.sin(t * 8), lambda t: 1.0, 13.6, 2, 14) + wave(lambda t: 2.6 + 3 * t, lambda t: 0.8, 13.6, 5, 10), 0.6, "silk")


@design("lightning_rod_spear")
def lightning_rod_spear(k):
    """off the Bastion's tallest roof: a three-pointed copper rod on glass insulators, always a little alive"""
    R = k.theme("storm_bastion", base=0.5)
    copper = ramp("#3a1a08", "#6a3414", "#9c5a24", "#c8843c", "#e8a860", "#ffd090")
    k.mat(blade=steel(copper, 0.54, 0.14), edge=honed(copper, 0.82), glass=flat(ramp("#2a4a5a", "#4a7a8a", "#7eb0bc", "#bce8ec"), 0.6, bevel=0.2), white=flat(R["glow"], 0.92, bevel=0.02), rod=flat(copper, 0.5, bevel=0.1))
    shaft(k, 16, mat="rod")
    for y in (14, 9):
        for j, w in enumerate((3.0, 4.0, 5.0)):
            k.box(0, y + (2 - j) * 0.8, 0, w, 0.8, w, "glass")
    k.forge(P((-0.9, 17), (0.9, 17), (0.6, 32), (0, 38.4), (-0.6, 32)), 1.2)
    k.forge(P(path((0.6, 19), qb((7, 18), (6.6, 26), (6.0, 33), 8), (6.0, 33), qb((5.4, 26), (5.0, 21), (0.6, 22), 8))), 1.2, step=1)
    k.forge(P(path((-0.6, 19), qb((-7, 18), (-6.6, 26), (-6.0, 33), 8), (-6.0, 33), qb((-5.4, 26), (-5.0, 21), (-0.6, 22), 8))), 1.2, step=1)
    k.plate(L([(-5.6, 30), (-3.4, 31.6), (-2.2, 29.8), (-0.4, 32)], 0.4) + L([(0.4, 28), (2, 29.6), (3.2, 27.6), (5.6, 29.4)], 0.4), 0.5, "white", glow=True)


@design("partisan")
def partisan(k):
    """the Court's guard carries this and has never needed to use it twice: a long point, two curved wings at its root, red velvet at the neck, blackened silver"""
    R = k.theme("bloodmoon_court", base=0.46)
    k.mat(tassel=flat(RUBY, 0.56, 0.2), gem=gem(RUBY), silver=flat(IRON, 0.72), edge=honed(SILVER, 0.7))
    shaft(k, 16)
    k.forge(P(path((-1.8, 16), (1.8, 16), qb((3.0, 18), (7.0, 16), (8.4, 19), 6), (8.4, 19), qb((5.0, 19.4), (3.4, 21), (1.8, 24), 6), (1.1, 30), (0, 38), (-1.1, 30), (-1.8, 24), qb((-3.4, 21), (-5.0, 19.4), (-8.4, 19), 6), qb((-7.0, 16), (-3.0, 18), (-1.8, 16), 6))), 1.6)
    k.plate(disc(0, 20, 1.1, 8), 2.0, "gem")
    k.box(0, 14, 0, 3.0, 2.4, 3.0, "silver")
    k.plate(P((-2.0, 14), (2.0, 14), (3.0, 7.0), (0.8, 8.4), (0, 6.6), (-0.8, 8.4), (-3.0, 7.0)), 1.6, "tassel")


@design("labyrinth_pike")
def labyrinth_pike(k):
    """cut with a set square by something patient: a key-shaped head, the meander stepped out of its edge, all right angles until the very point"""
    R = k.theme("obsidian_labyrinth", base=0.46, edge=0.86)
    k.mat(gold=flat(GOLD, 0.68), wood=flat(R["dark"], 0.7, bevel=0.08))
    shaft(k, 16, shoe="gold")
    m = rect(-1.6, 15, 1.6, 33) + P((-1.6, 33), (1.6, 33), (0, 39))
    for y, s_ in ((17, 1), (21, -1), (25, 1)):
        m = m + rect(s_ * 1.6 if s_ > 0 else s_ * 6.4, y, s_ * 6.4 if s_ > 0 else s_ * 1.6, y + 1.3)
        x0, x1 = sorted((s_ * 5.2, s_ * 6.4))
        m = m + rect(x0, y, x1, y + 4.2)
        x0, x1 = sorted((s_ * 3.4, s_ * 6.4))
        m = m + rect(x0, y + 3.0, x1, y + 4.2)
    k.forge(m, 1.7, step=1)
    k.plate(L([(0, 16), (0, 32)], 0.5), 1.76, "gold")
    k.box(0, 13.6, 0, 3.0, 1.4, 3.0, "gold")


@design("angler_spear")
def angler_spear(k):
    """a long whip of a spear taken off something at the bottom of the light: a thin barbed head and from behind it the lure on a flexible ray, hanging out over the point"""
    R = k.theme("abyssal_lighthouse", base=0.5)
    k.mat(lure=fire(R["glow"], 0.4, 0.6), stalk=flat(R["dark"], 0.72), fin=flat(R["wrap"], 0.56, bevel=0.1))
    shaft(k, 18, mat="stalk")
    k.forge(P((-1.2, 18), (1.2, 18), (3.0, 19), (1.2, 22), (0.9, 30), (0, 36), (-0.9, 30), (-1.2, 22), (-3.0, 19)), 1.4)
    k.plate(stroke((-0.6, 20), (-11, 26), (-6, 40), 0.7, 14) + stroke((-6, 40), (-3.4, 42.6), (-1.0, 40), 0.5, 6), 0.8, "stalk")
    k.plate(disc(-1.0, 38.2, 2.0, 10), 2.4, "lure", glow=True)
    k.plate(P((1, 4), (7, 2), (5.6, -2), (7, -6), (1, -6)), 0.5, "fin")


@design("pale_lantern")
def pale_lantern(k):
    """the keeper's last light: a hanging iron lantern on the shepherd's crook of a long spear, cold blue flame behind real glass, a spike standing above it"""
    R = k.theme("abyssal_lighthouse", base=0.5)
    flame = ramp("#0b3f7a", "#1466b8", "#1e9be0", "#3fd0ff", "#8fecff", "#d9fbff", "#ffffff")
    k.mat(iron=flat(ramp("#12161c", "#1b2128", "#2a333d", "#3c4855", "#56667a", "#7a8ca0"), 0.62, bevel=0.14), flame=fire(flame, 0.2, 0.75), glass=flat(ramp("#2f7f9a", "#5fb8d0", "#9fe4f2", "#e8fdff"), 0.5, bevel=0.2), cord=flat(ramp("#3a4b5c", "#5e7488", "#8ea4b6"), 0.6), wood=flat(R["dark"], 0.6, bevel=0.06))
    shaft(k, 17, mat="iron")
    k.forge(P((-1.2, 17), (1.2, 17), (0.8, 33), (0, 40), (-0.8, 33)), 1.3)
    k.plate(stroke((0.6, 27), (11, 31), (9.6, 20.8), 1.2, 12), 1.4, "iron")
    links(k, [(9.6, 21), (9.4, 19.4), (9.6, 18)], "iron", 0.9)
    k.box(9.6, 11, 0, 5.2, 6.4, 5.2, "glass")
    k.plate(P(path(qb((9.6, 11.6), (7.2, 13.4), (9.6, 17.2), 6), qb((9.6, 17.2), (12, 13.4), (9.6, 11.6), 6))), 5.3, "flame", glow=True)
    for x, z in ((7.2, 2.4), (12, 2.4), (7.2, -2.4), (12, -2.4)):
        k.box(x, 11, z, 0.7, 6.4, 0.7, "iron")
    k.box(9.6, 10.4, 0, 6.4, 0.8, 6.4, "iron")
    k.box(9.6, 17.2, 0, 6.4, 0.8, 6.4, "iron")
    k.box(9.6, 18, 0, 3.0, 0.8, 3.0, "iron")


@design("halo_lance")
def halo_lance(k):
    """a thin white lance threaded through three halos, each smaller than the last, burning without touching it"""
    k.theme("eclipse_cathedral", base=0.7, ridge=0.1)
    k.mat(edge=honed(ramp("#a06018", "#d8982c", "#f6d060", "#fff0b0", "#ffffff"), 0.6), halo=fire(GOLD, 0.5, 0.5), gold=flat(GOLD, 0.66), wood=flat(ramp("#8a8aa0", "#b0b0c4", "#d4d4e2", "#f0f0f6"), 0.6, bevel=0.06))
    shaft(k, 16, shoe="gold")
    k.forge(P((-1.6, 16), (1.6, 16), (1.0, 34), (0, 42), (-1.0, 34)), 1.5)
    for y, r_ in ((20, 7.0), (26, 5.2), (31, 3.6)):
        for j in range(20):
            a, b = j * math.pi / 10, (j + 1.1) * math.pi / 10
            k.seg((math.cos(a) * r_, y), (math.cos(b) * r_, y), 0.7, 0.7, "halo", z=math.sin(a) * r_, glow=True)
    k.box(0, 14, 0, 2.8, 2.2, 2.8, "gold")


@design("drake_lance")
def drake_lance(k):
    """a dragon knight's jousting lance: a tapering scaled shaft running up from a great flared vamplate, tipped with a horn"""
    k.theme("wyrms_hoard", base=0.6)
    k.mat(gold=flat(GOLD, 0.64, bevel=0.14), scale=flat(GOLD, 0.5, bevel=0.2), horn=steel(HORN, 0.6, 0.14), hedge=honed(HORN, 0.94), gem=gem(RUBY), red=flat(ramp("#2a0606", "#4a0c0a", "#741612", "#9c2218"), 0.6))
    shaft(k, 8, w=2.2, mat="red", shoe="gold")
    for j in range(10):
        y = 8 + j * 2.4
        w = 5.6 - j * 0.48
        k.box(0, y, 0, w, 2.0, w, "scale")
        k.box(0, y + 1.8, 0, w + 0.5, 0.7, w + 0.5, "gold")
    k.forge(P(path(qb((-1.1, 31.6), (-1.0, 36), (1.4, 41), 6), (1.4, 41), qb((1.2, 36), (1.1, 34), (1.1, 31.6), 6))), 1.8, step=1, body="horn", rim="hedge")
    for j, (w, h) in enumerate(((3.0, 1), (5.4, 1), (7.8, 1), (9.6, 1.2), (11, 1))):
        k.box(0, 7.4 - j * 1.0, 0, w, h, w, "gold")
    k.plate(disc(4.6, 4.6, 0.9, 8), 1.4, "gem")


# ---------------------------------------------------------------- the world's

@design("boar_spear")
def boar_spear(k):
    """a hunter's spear, nothing more: a broad leaf with a strong rib and two lugs of iron below it so the boar can't run up the shaft"""
    fe = ramp("#2a2e34", "#3e444c", "#565e68", "#727c86", "#929ca6", "#b4bec6", "#d4dce2", "#f0f4f6")
    k.mat(blade=steel(fe, 0.54, 0.14), edge=honed(fe, 0.84), wood=staves(ramp("#3a2410", "#52341c", "#6e4826", "#8c6034", "#a87a48"), 1.0, 0.56), wrap=wrap(LEATHER, IRON[1], 5), dark=flat(IRON, 0.66))
    shaft(k, 16)
    socket(k, 14, 3.0)
    k.forge(P(path((-1, 18), qb((-5.4, 22), (-3.4, 30), (0, 36), 8), qb((0, 36), (3.4, 30), (5.4, 22), 8), (1, 18))), 1.4)
    k.plate(rect(-4.6, 15, 4.6, 16), 1.6, "dark")


@design("gilded_partisan")
def gilded_partisan(k):
    """the palace's parade version: gold chased up a broad ogival head, its wings curled into scrolls, a tassel of real silk"""
    k.mat(blade=steel(GOLD, 0.56, 0.14), edge=honed(ramp("#a06018", "#d8982c", "#f6d060", "#fff0b0", "#ffffff"), 0.7), gold=flat(GOLD, 0.66), wood=flat(ramp("#14243a", "#1c3050", "#2a4468"), 0.6, bevel=0.06), wrap=wrap(GOLD, GOLD[1], 4), dark=flat(GOLD, 0.5), tassel=flat(ramp("#0e1a3a", "#182a54", "#22386c", "#304a86", "#4a66a8"), 0.6, 0.2))
    shaft(k, 16)
    k.forge(P((-2.6, 16), (2.6, 16), (3.2, 22), (1.4, 30), (0, 38), (-1.4, 30), (-3.2, 22)), 1.6)
    for s_ in (1, -1):
        k.plate(ring(s_ * 5.4, 17.8, 2.4, 1.2), 1.4, "gold")
    k.plate(L([(0, 18), (-1.4, 21), (1.4, 24), (0, 27)], 0.5), 1.66, "dark")
    k.box(0, 14, 0, 3.2, 2.2, 3.2, "gold")
    k.plate(P((-2.2, 14), (2.2, 14), (3.0, 7), (0.8, 8.2), (-0.8, 7.4), (-3.0, 8.0)), 1.4, "tassel")


@design("wyrmtongue")
def wyrmtongue(k):
    """a wyrm's forked tongue, dried hard and hot: two wet red points curling apart from a black throat on a blackened haft"""
    red = ramp("#2a0408", "#4e0810", "#7a1018", "#b01c20", "#e0442a", "#ff8a5a")
    fire_ = ramp("#a02206", "#e04a0a", "#ff8a1c", "#ffc84a", "#fff0b0")
    k.mat(blade=steel(red, 0.56, 0.14), edge=fire(fire_, 0.3, 0.7), rim=honed(red, 0.92), scale=flat(ramp("#14100e", "#241c18", "#3a2f26", "#54453a"), 0.6, bevel=0.2), wood=flat(ramp("#0c0a0a", "#181414", "#242020"), 0.7, bevel=0.06), wrap=wrap(red, red[0], 4), dark=flat(IRON, 0.6))
    shaft(k, 16)
    t = P(path((-2.6, 16), (2.6, 16), (2.2, 24), qb((3.4, 28), (6.6, 32), (8.4, 39), 8), (8.4, 39), qb((4.4, 33), (1.6, 30), (0, 28), 6), qb((-1.6, 30), (-3.2, 33), (-5.4, 40), 6), (-5.4, 40), qb((-6.4, 33), (-3.4, 28), (-2.2, 24), 6)))
    k.plate(t, 1.0, "edge", glow=True, tag="edge")
    k.plate(t.inset(0.5), 2.0, "blade", tag="blade")
    k.plate(P((-3.4, 12), (3.4, 12), (4.6, 18.4), (2.4, 16.8), (0, 19.4), (-2.4, 16.8), (-4.6, 18.4)), 3.4, "scale")
    k.plate(disc(-1.4, 14.6, 0.6, 6) + disc(1.4, 14.6, 0.6, 6), 3.6, "edge", glow=True)


@design("heavens_lance")
def heavens_lance(k):
    """a lance of light: a blade too bright to see the edges of, white-gold wings spread at its root, more wings further down the shaft, folded"""
    pale = ramp("#c0a060", "#e0c880", "#f6e8b0", "#fff8e0", "#ffffff")
    k.mat(beam=fire(pale, 0.3, 0.7), gold=flat(GOLD, 0.66, bevel=0.14), plume=flat(ramp("#a0a0b4", "#c8c8d8", "#e8e8f0", "#ffffff"), 0.66, bevel=0.1), wood=flat(pale, 0.66, bevel=0.06), wrap=wrap(GOLD, pale[1], 4), dark=flat(GOLD, 0.6))
    shaft(k, 16)
    m = P((-2.2, 16), (2.2, 16), (1.4, 32), (0, 44), (-1.4, 32))
    k.plate(m, 1.2, "beam", glow=True)
    k.plate(m.inset(0.5), 1.6, "beam", glow=True)
    for s_ in (1, -1):
        k.plate(feathers(s_, 16, 7, 16, 86, 1.3), 1.0, "plume")
        k.plate(feathers(s_, 6, 4, 8, 30, 0.9, True), 0.8, "plume")
    k.plate(disc(0, 16, 2.4, 12), 2.4, "gold")
    k.plate(disc(0, 16, 1.2, 8), 2.6, "beam", glow=True)


@design("whalers_harpoon")
def whalers_harpoon(k):
    """a whale iron: one big flue on a long soft-iron shank meant to bend, its line still knotted on and trailing away"""
    fe = ramp("#1c1a18", "#2a2724", "#3a3632", "#4c4741", "#605a52", "#787066", "#928a7e")
    k.mat(blade=steel(fe, 0.56, 0.14), edge=honed(fe, 0.92), iron=flat(fe, 0.66, bevel=0.1), line=flat(ramp("#8a7a5a", "#a8987a", "#c4b89a", "#e0d4b8"), 0.6), wood=staves(ramp("#2a1a0e", "#3a2616", "#4e3420", "#664428"), 1.0, 0.56), wrap=wrap(ramp("#8a7a5a", "#a8987a", "#c4b89a"), None, 3), dark=flat(fe, 0.6))
    shaft(k, 4)
    k.box(0, 4, 0, 1.2, 26, 1.2, "iron")
    k.box(0, 2, 0, 2.8, 3.6, 2.8, "dark")
    k.forge(P((-0.7, 28), (0.7, 28), (0.7, 31), (4.6, 28.6), (3.4, 32.4), (0, 39), (-1.0, 33), (-0.7, 31)), 1.4, step=1)
    for j in range(4):
        k.box(0, 1 + j * 0.8, 0, 3.4, 0.7, 3.4, "line")
    k.plate(stroke((1.6, 2), (8, 0), (6, -9), 0.5) + stroke((6, -9), (3, -14), (6, -19), 0.5), 0.5, "line")


@design("dune_pilum")
def dune_pilum(k):
    """a salt legionary's javelin: a thin square shank as long as the wood, a tiny bronze pyramid at the end, the join wrapped and pinned"""
    bronze = ramp("#2a1606", "#432410", "#5e3618", "#7c4c22", "#9c6630", "#bc8444", "#d8a462", "#f0c88a")
    k.mat(blade=steel(bronze, 0.6, 0.14), edge=honed(bronze, 0.9), iron=flat(bronze, 0.6, bevel=0.1), wood=staves(ramp("#5a4628", "#7a6238", "#9a7e4c", "#b89a62"), 1.0, 0.56), wrap=wrap(LEATHER, bronze[3], 5), dark=flat(bronze, 0.5), pin=flat(GOLD, 0.7))
    shaft(k, 12)
    k.box(0, 10, 0, 3.2, 4.0, 3.2, "dark")
    k.box(0, 11.2, 0, 3.6, 0.8, 1.0, "pin")
    k.box(0, 14, 0, 1.1, 22, 1.1, "iron")
    k.forge(P((-1.8, 36), (1.8, 36), (0, 41.6)), 1.8, step=1)
    k.plate(P((-1.8, 36.6), (-3.0, 35), (-0.5, 36)) + P((1.8, 36.6), (3.0, 35), (0.5, 36)), 1.0, "iron")


@design("wardens_bardiche")
def wardens_bardiche(k):
    """the Rime Warden's bardiche: a tall black crescent lashed to the shaft top and bottom, rime along its edge and the cell keys still hanging on a ring"""
    black = ramp("#08080e", "#10121a", "#1a1e28", "#262c3a", "#384254", "#4e5a70")
    ice = ramp("#0e2a3a", "#164058", "#205a78", "#2e7898", "#4a9cbc", "#78c0da", "#b0e0f0", "#e8f8ff")
    k.mat(blade=steel(black, 0.56, 0.12), edge=honed(ice, 0.8), iron=flat(IRON, 0.66), wood=flat(black, 0.66, bevel=0.06), wrap=wrap(black, ice[2], 4), dark=flat(black, 0.66), key=flat(BRASS, 0.62), ice=flat(ice, 0.72, bevel=0.14))
    shaft(k, 34)
    m = P(path((1, 12), qb((12, 11), (15, 22), (10, 40), 12), (10, 40), qb((9.6, 30), (9, 24), (1, 30), 10)))
    k.forge(m, 1.7, step=2, ridge=-0.2)
    for y in (13, 29):
        k.box(0.6, y, 0, 3.4, 1.6, 2.6, "iron")
    for x, y, ln, a in ((13.4, 22, 3.4, -80), (13, 28, 3.2, -70), (12.4, 15, 3.4, -100)):
        k.plate(shard(x, y, ln, a, 1.4), 1.2, "ice")
    k.plate(ring(-1.6, 7.0, 2.2, 1.3), 0.6, "iron")
    for x, y, a in ((-3.2, 4.8, 0.3), (-1.4, 4.2, 0), (0.6, 4.8, -0.3)):
        k.seg((x + 0.2, y + 1.4), (x - a * 4, y - 3), 0.5, 0.5, "key")
        k.plate(rect(x - a * 4 - 0.6, y - 3.6, x - a * 4 + 0.6, y - 2.6), 0.6, "key")


@design("tidecallers_trident")
def tidecallers_trident(k):
    """a drowned god's fork: three long sea-gold tines, the outer two swept like waves, a ring of water standing turning round them"""
    gold = ramp("#3a2a08", "#5e4a10", "#8a7218", "#b89c28", "#e0c84a", "#f8ec96")
    sea = ramp("#0a4a5a", "#147a8a", "#2aa8b8", "#6ad8e0", "#c4f4f8", "#ffffff")
    k.mat(blade=steel(gold, 0.56, 0.14), edge=honed(gold, 0.92), water=fire(sea, 0.3, 0.6), wood=flat(ramp("#0e2428", "#163438", "#204a4e", "#2e6266"), 0.6, bevel=0.06), wrap=wrap(gold, gold[1], 4), dark=flat(gold, 0.56))
    shaft(k, 16)
    k.forge(P((-1.4, 16), (1.4, 16), (1.1, 34), (0, 42), (-1.1, 34)), 1.5)
    for s_ in (1, -1):
        k.forge(P(path((s_ * 1, 16), qb((s_ * 9.4, 15), (s_ * 7.4, 25), (s_ * 8.6, 35), 10), (s_ * 8.6, 35), (s_ * 6.0, 30), qb((s_ * 4.6, 24), (s_ * 5.0, 21), (s_ * 1, 20), 8))), 1.5, step=1)
    for j in range(26):
        a, b = j * math.pi / 13, (j + 1.1) * math.pi / 13
        r_ = 9.6 + math.sin(j * 1.5) * 0.5
        k.seg((math.cos(a) * r_, 26 + math.sin(j * 0.9) * 0.7), (math.cos(b) * r_, 26 + math.sin((j + 1) * 0.9) * 0.7), 1.0, 1.0, "water", z=math.sin(a) * r_, glow=True)
    k.box(0, 14, 0, 3.4, 2.6, 3.4, "edge")


@design("unison")
def unison(k):
    """two spears that are one: the shafts twisted round each other all the way up, iron and gold, parting only at the two heads"""
    fe = ramp("#2a2e34", "#3e444c", "#565e68", "#727c86", "#929ca6", "#b4bec6", "#d4dce2", "#f0f4f6")
    k.mat(blade=steel(fe, 0.54, 0.13), edge=honed(fe, 0.84), goldb=steel(GOLD, 0.56, 0.13), goldedge=honed(ramp("#a06018", "#d8982c", "#f6d060", "#fff0b0", "#ffffff"), 0.7), iron=flat(fe, 0.6, bevel=0.1), gold=flat(GOLD, 0.66, bevel=0.1), wrap=wrap(LEATHER, GOLD[3], 4), hot=fire(ramp("#ffb040", "#ffe8a0", "#fffbe0", "#ffffff"), 0.4, 0.6))
    n, prev = 30, None
    for j in range(n + 1):
        y = -24 + j * 1.3
        a = j * 0.7
        p = (math.sin(a) * 0.9, y)
        z = math.cos(a) * 0.9
        if prev:
            k.seg(prev[0], p, 1.3, 1.3, "iron", z=(prev[1] + z) / 2)
            k.seg((-prev[0][0], prev[0][1]), (-p[0], p[1]), 1.3, 1.3, "gold", z=-(prev[1] + z) / 2)
        prev = (p, z)
    k.box(0, -4, 0, 3.0, 8, 3.0, "wrap", tag="grip")
    k.plate(stroke((0, 14), (-4, 18), (-4.0, 24), 1.3), 1.3, "iron")
    k.plate(stroke((0, 14), (4, 18), (4.0, 24), 1.3), 1.3, "gold")
    k.forge(P((-5.8, 24), (-2.2, 24), (-3.2, 33), (-4.0, 39), (-4.8, 33)), 1.4)
    r_ = P((5.8, 24), (2.2, 24), (3.2, 33), (4.0, 39), (4.8, 33))
    k.plate(r_, 0.8, "goldedge", tag="edge")
    k.plate(r_.inset(0.5), 1.4, "goldb", tag="blade")
    k.plate(disc(0, 21, 1.4, 8), 1.2, "hot", glow=True)
