"""Summoner staffs: every one calls something, and looks like the thing you'd call it with: bells, crooks, banners, taps, totems, leashes."""
import math

from voxsword import ramp
from weaponsets import design, qb, path, P, L, disc, ring, rect, wave, flat, fire, staves, bone, wrap, stripes
from weaponsets_a import BRASS, GOLD, IRON, LEATHER
from weaponsets_d import RUBY, SILVER, links, stroke
from weaponsets_e import CORK, HORN, IVORY, RAG
from weaponsets_k import pole, orb, HOT, TEAL, FE, NIGHT, VOID
from weaponsets_l import hook, PALE, BIRCH, WARM


def bell(k, cx, top, w, mat, rows=5):
    """a cast bell hanging from top, flared at the lip"""
    for j in range(rows):
        t = j / (rows - 1)
        k.box(cx, top - (j + 1) * 1.8, 0, w * (0.46 + 0.54 * t ** 2), 1.9, w * (0.46 + 0.54 * t ** 2), mat)
    k.box(cx, top - rows * 1.8 - 0.6, 0, w * 1.12, 0.8, w * 1.12, mat)


def skull(k, x, y, s_, mat, eye, jaw=True):
    k.plate(P((x - 3 * s_, y + 4 * s_), (x + 3 * s_, y + 4 * s_), (x + 3.8 * s_, y + 1 * s_), (x + 2 * s_, y - 2 * s_), (x - 2 * s_, y - 2 * s_), (x - 3.8 * s_, y + 1 * s_)), 5 * s_, mat)
    k.plate(disc(x - 1.5 * s_, y + 1 * s_, 1.0 * s_, 7) + disc(x + 1.5 * s_, y + 1 * s_, 1.0 * s_, 7), 5.2 * s_, eye, glow=True)
    if jaw:
        k.plate(rect(x - 1.8 * s_, y - 3.4 * s_, x + 1.8 * s_, y - 2 * s_), 4 * s_, mat)
        for j in (-1, 0, 1):
            k.plate(rect(x + (j * 1.1 - 0.12) * s_, y - 3.4 * s_, x + (j * 1.1 + 0.12) * s_, y - 2 * s_), 4.2 * s_, "dark")


@design("revel_tap")
def revel_tap(k):
    """a barrel bung and tap on a pole, drawn by the drunks that pour out of it: a keg's worth of grinning foam at the spout"""
    R = k.theme("cellar")
    k.mat(stave=staves(R["wood"], 1.4, 0.6), hoop=flat(IRON, 0.62), brass=flat(BRASS, 0.64, bevel=0.14), foam=flat(ramp("#c8c0a8", "#e8e0c8", "#fff8e8"), 0.7, 0.2), beer=fire(WARM, 0.2, 0.7))
    pole(k, 15, "stave")
    k.plate(P((-7, 15), (7, 15), (9, 21), (9, 26), (7, 32), (-7, 32), (-9, 26), (-9, 21)), 9.0, "stave")
    for y in (17, 29.4):
        k.box(0, y, 0, 15.6 + (y == 23), 1.2, 9.4, "hoop")
    k.box(0, 21, 4.4, 3.6, 3.0, 2.4, "brass")
    k.box(0, 21, 7.2, 1.6, 1.6, 4.0, "brass")
    k.box(0, 23.8, 8, 1.0, 3.0, 1.0, "brass")
    k.box(0, 26.6, 8, 3.8, 0.9, 1.0, "brass")
    k.plate(disc(9.6, 23, 1.6, 8) + disc(11.6, 21, 2.0, 9) + disc(10.6, 18.6, 1.4, 8), 2.6, "foam")
    k.plate(rect(9.8, 11, 10.6, 18) + disc(10.2, 11, 0.8, 7), 0.8, "beer", glow=True)


@design("hanging_tree")
def hanging_tree(k):
    """a little dead tree with thirteen small nooses in it, and something sways in every one"""
    R = k.theme("gallows")
    k.mat(ash=flat(ramp("#14100c", "#221a14", "#32281e", "#463828"), 0.62, 0.2, bevel=0.1), cord=flat(ramp("#6a5a3a", "#8e7a52", "#b09c70"), 0.8), hot=fire(R["glow"], 0.3, 0.7))
    pole(k, 14, "ash", 2.4)
    k.plate(P((-1.4, 14), (1.4, 14), (0.8, 25), (-0.8, 25)), 2.2, "ash")
    for s_ in (1, -1):
        k.plate(stroke((s_ * 0.6, 20), (s_ * 8, 22), (s_ * 12, 29), 1.1, 8), 1.6, "ash")
        k.plate(stroke((s_ * 0.6, 24), (s_ * 5, 28), (s_ * 5, 34), 0.9, 8), 1.4, "ash")
        k.plate(stroke((s_ * 7, 23), (s_ * 9, 22), (s_ * 13, 22), 0.6, 6), 1.0, "ash")
        for x, y, ln in ((12, 27, 5), (8, 22, 4), (5, 31, 4), (13, 21.6, 3)):
            k.box(s_ * x, y - ln, 0, 0.4, ln, 0.4, "cord")
            k.plate(ring(s_ * x, y - ln - 0.8, 1.1, 0.5), 0.6, "cord")
            k.plate(disc(s_ * x, y - ln - 0.8, 0.5, 5), 0.7, "hot", glow=True)


@design("thirteen_knots")
def thirteen_knots(k):
    """the Hangman's own rope, thirteen turns of it standing up stiff as a staff with the loop at the top, a pale head hung in it that isn't quite there"""
    R = k.theme("gallows")
    k.mat(rope=wrap(ramp("#4a3a22", "#6a5634", "#8e784c", "#b09c70"), ramp("#2a2014", "#3a2c1a", "#4a3a22")[1], 2), ghost=flat(ramp("#6a7a6a", "#94a494", "#c0d0c0"), 0.7, bevel=0.1), hot=fire(R["glow"], 0.3, 0.7))
    pole(k, 13, "rope", 2.4, grip="rope", shoe="rope")
    k.box(0, 13, 0, 4.2, 8.6, 4.2, "rope")
    for y in range(13, 22, 1):
        k.box(0, y + 0.1, 0, 4.6, 0.4, 4.6, "dark")
    k.plate(ring(0, 29, 7.8, 5.8), 2.2, "rope")
    k.plate(disc(0, 28.6, 3.8, 14), 3.0, "ghost")
    k.plate(disc(-1.4, 29, 0.8, 7) + disc(1.4, 29, 0.8, 7), 3.2, "hot", glow=True)
    k.plate(P((-1, 26.6), (1, 26.6), (0, 25.4)), 3.2, "hot", glow=True)


@design("rootcaller")
def rootcaller(k):
    """a staff that is pulled up rather than made: the root ball still on it, the top a hand of root fingers, a green eye in the palm"""
    R = k.theme("rotwood")
    k.mat(root=staves(R["wood"], 1.0, 0.6), soil=flat(ramp("#1a140e", "#2a2016", "#3c2e1e"), 0.5, 0.4), moss=flat(R["acc"], 0.6, 0.2))
    pole(k, 18, "root", 2.2)
    for j, (x, y, h) in enumerate(((-8, 26, 11), (-3.6, 28, 12), (2, 28.4, 12.6), (7, 27, 10))):
        k.plate(stroke((x * 0.4, 18), (x * 1.2, y - 2), (x * 1.3, y + h - 6), 1.2 - j * 0.04, 10), 1.8, "root")
    k.plate(disc(0, 21, 5.6, 12), 3.0, "root")
    k.plate(disc(0, 21, 2.2, 10), 3.4, "glow", glow=True)
    k.plate(disc(0, -19, 3.4, 9) + disc(-1.8, -21, 2.0, 7) + disc(2.2, -20, 2.0, 7), 3.6, "soil")
    for x in (-4, -1, 2, 4.4):
        k.plate(L([(x * 0.6, -21), (x, -26)], 0.5), 0.8, "root")
    k.plate(P((-5.4, 20), (-2, 18), (-4, 16)) + P((3, 17), (5.6, 19.6), (5, 16)), 3.2, "moss")


@design("ghoulbell")
def ghoulbell(k):
    """a corpse-bell on a bent iron bracket, a finger bone for a clapper, the kind they tied to your hand in case you woke"""
    R = k.theme("crypt")
    k.mat(iron=flat(IRON, 0.62, bevel=0.1), bronze=flat(ramp("#3a2a1a", "#544026", "#705836", "#8e7446"), 0.62, bevel=0.14), bone=bone(IVORY, 0.72), cord=flat(R["acc"], 0.6))
    pole(k, 30, "iron")
    k.plate(stroke((0, 30), (6, 33), (9, 29), 1.2), 1.4, "iron")
    bell(k, 9, 28.6, 9.4, "bronze", 6)
    k.plate(rect(8.5, 14.4, 9.5, 18) + disc(9, 14.4, 0.9, 6), 1.2, "bone")
    k.plate(wave(lambda t: 4 + 0.7 * math.sin(t * 7), lambda t: 0.25, 20, 2, 8), 0.3, "cord")
    k.plate(rect(3, 2, 5, 3) + L([(4, 2), (3.4, -1)], 0.5), 0.8, "bone")
    k.plate(disc(9, 24, 1.0, 7), 9.4, "glow", glow=True)


@design("abbots_crozier")
def abbots_crozier(k):
    """the Pale Abbot's crozier: the curl is a spine, a wax saint in the crook of it with its eyes melted out and a candle burning on its head"""
    R = k.theme("crypt")
    k.mat(bone=bone(IVORY, 0.72), wax=flat(R["acc"], 0.76, bevel=0.1), silver=flat(SILVER, 0.7, bevel=0.14), flame=fire(WARM, 0.1, 0.9))
    pole(k, 20, "silver", shoe="silver")
    pts = []
    for j in range(23):
        a = math.radians(180 - j * 13.5)
        pts.append((7 + math.cos(a) * (7 - j * 0.18), 26 + math.sin(a) * (7 - j * 0.18)))
    k.plate(stroke((0, 20), (0, 23), (0, 26), 2.0, 4), 2.4, "silver")
    for j, p_ in enumerate(pts):
        k.plate(disc(p_[0], p_[1], 1.4, 6), 2.4, "bone")
    k.plate(P((5, 28), (9, 28), (9.6, 20), (4.4, 20)), 2.6, "wax")
    k.plate(disc(7, 29.4, 1.8, 8), 2.8, "wax")
    k.plate(P((5.6, 29), (6.4, 29), (6, 26)) + P((7.6, 29), (8.4, 29), (8, 26)), 3.0, "dark")
    k.box(7, 31, 0, 0.7, 1.6, 0.7, "wax")
    k.plate(P(path(qb((7, 32.4), (5.8, 33.6), (7, 36), 4), qb((7, 36), (8.2, 33.6), (7, 32.4), 4))), 1.0, "flame", glow=True)


@design("lepers_bell")
def lepers_bell(k):
    """the small cracked bell the sick had to ring; the sound brings the sick. A bandage still tied on its handle"""
    R = k.theme("plague")
    k.mat(bronze=flat(R["dark"], 0.64, bevel=0.14), lint=wrap(PALE, PALE[0], 3), cane=flat(R["acc"], 0.56), green=fire(R["glow"], 0.3, 0.6))
    pole(k, 28, "cane", grip="lint")
    k.box(0, 27.6, 0, 3.0, 1.6, 3.0, "lint")
    bell(k, 0, 27.6, 13, "bronze", 6)
    k.plate(L([(4, 16), (2.6, 18.6), (4.4, 20.6), (3, 23)], 0.4), 13.2, "green", glow=True)
    k.plate(rect(-0.6, 13.6, 0.6, 16) + disc(0, 13, 1.2, 8), 1.4, "bronze")
    k.plate(wave(lambda t: -3 - 4 * t + 0.6 * math.sin(t * 8), lambda t: 0.7 - 0.3 * t, 29, 18, 8), 0.4, "lint")


@design("maskbearer")
def maskbearer(k):
    """five blank masks stacked on a pole like a totem, each with its eyes shut but one, and the open one looks at you"""
    R = k.theme("temple", base=0.7)
    k.mat(mask=flat(BIRCH, 0.84, bevel=0.14), gold=flat(R["acc"], 0.66), rod=flat(R["blade"], 0.72))
    pole(k, 12, "rod", shoe="gold")
    for j, (y, w) in enumerate(((13, 5.4), (19, 6.0), (25, 5.0))):
        k.plate(P((-w, y + 5.6), (w, y + 5.6), (w - 0.8, y + 1.6), (w * 0.5, y), (-w * 0.5, y), (-w + 0.8, y + 1.6)), 4.4, "mask")
        k.plate(rect(-w, y + 5.2, w, y + 5.8), 4.6, "gold")
        if j == 1:
            k.plate(disc(-2.2, y + 3, 0.9, 7) + disc(2.2, y + 3, 0.9, 7), 4.8, "glow", glow=True)
        else:
            k.plate(rect(-3.2, y + 2.8, -1.2, y + 3.2) + rect(1.2, y + 2.8, 3.2, y + 3.2), 4.6, "dark")
        k.plate(rect(-0.3, y + 0.8, 0.3, y + 2.4), 4.6, "dark")
    k.plate(P((-3, 30.6), (3, 30.6), (0, 35)), 3.0, "gold")


@design("assemblers_crank")
def assemblers_crank(k):
    """an ossuary surgeon's bone-saw brace and crank: turn the handle and the pieces start to find each other"""
    R = k.theme("ossuary")
    k.mat(bone=bone(R["acc"], 0.68), iron=flat(IRON, 0.62, bevel=0.1), brass=flat(BRASS, 0.64))
    pole(k, 30, "bone", shoe="iron")
    k.plate(disc(0, 24, 7.4, 16) - disc(0, 24, 5.2, 14), 2.0, "iron")
    for j in range(10):
        a = j * math.pi / 5
        k.plate(P((math.cos(a - 0.14) * 7, 24 + math.sin(a - 0.14) * 7), (math.cos(a) * 9, 24 + math.sin(a) * 9), (math.cos(a + 0.14) * 7, 24 + math.sin(a + 0.14) * 7)), 2.0, "iron")
    k.plate(disc(0, 24, 2.2, 10), 3.0, "brass")
    k.box(0, 23.4, 1.6, 12, 1.2, 1.2, "iron")
    k.box(12, 20, 2.4, 1.4, 5, 1.4, "bone")
    k.plate(P((-1.4, 30), (1.4, 30), (0, 34)) , 2.0, "iron")
    for x, y in ((-5, 16), (5, 14)):
        k.plate(rect(x - 0.5, y, x + 0.5, y + 4) + disc(x - 0.8, y + 4, 0.8, 5) + disc(x + 0.8, y + 4, 0.8, 5), 0.8, "bone")
        k.plate(L([(0, 19), (x, y + 2)], 0.2), 0.3, "glow", glow=True)


@design("assemblers_heart")
def assemblers_heart(k):
    """the Assembler's finished work: a ribcage with a clockwork heart ticking inside it, all held up in a ring of little reaching arm bones"""
    R = k.theme("ossuary")
    k.mat(bone=bone(R["acc"], 0.72), brass=flat(BRASS, 0.66, bevel=0.14), pol=flat(R["dark"], 0.62))
    pole(k, 15, "pol", shoe="bone")
    k.box(0, 15, 0, 2.2, 18, 2.0, "bone")
    for j, y in enumerate((17, 20, 23, 26, 29)):
        w = (8, 9, 9, 8, 6)[j]
        for s_ in (1, -1):
            k.plate(stroke((0, y), (s_ * (w + 2), y + 1.6), (s_ * (w - 0.6), y + 4.6), 0.7, 8), 1.4, "bone")
    k.plate(disc(0, 24, 3.6, 12), 3.4, "brass")
    k.plate(disc(0, 24, 1.8, 8), 3.8, "glow", glow=True)
    k.plate(rect(-0.4, 27.4, 0.4, 28.6), 3.4, "brass")
    k.plate(rect(-3.4, 33, 3.4, 34), 2.0, "bone")
    k.plate(disc(0, 36, 2.0, 9), 2.4, "bone")
    k.plate(disc(-0.7, 36, 0.4, 5) + disc(0.7, 36, 0.4, 5), 2.6, "glow", glow=True)


@design("slagmother")
def slagmother(k):
    """a foundry ladle turned upside down over a sprue of cooling slag, the whole lumpy thing still giving birth to little hot things"""
    R = k.theme("foundry")
    k.mat(iron=flat(ramp("#14120f", "#221f1b", "#332f2a", "#46403a", "#5e564e"), 0.64, bevel=0.14), slag=flat(ramp("#1a0a06", "#34140a", "#5a2010"), 0.6, 0.4, bevel=0.1), hot=fire(HOT, 0.3, 0.7))
    pole(k, 14, "iron")
    k.plate(disc(0, 21, 6.6, 12) + disc(-5, 18, 3.4, 9) + disc(5.4, 18.4, 3.6, 9), 6.0, "slag")
    k.plate(L([(-4, 16), (-2, 20), (1, 18), (3, 22)], 0.5) + L([(-1, 24), (0, 21)], 0.4), 6.2, "hot", glow=True)
    k.plate(P(path(qb((-8, 22), (-8, 33), (0, 33), 8), qb((0, 33), (8, 33), (8, 22), 8))) - P(path(qb((-6.4, 21), (-6.4, 31), (0, 31), 8), qb((0, 31), (6.4, 31), (6.4, 21), 8))), 8.0, "iron")
    for x, y, r_ in ((-9.4, 13, 1.6), (9.6, 12, 1.4), (-6.4, 9, 1.1)):
        k.plate(disc(x, y, r_, 7), r_ * 1.4, "slag")
        k.plate(disc(x + 0.3, y + 0.3, r_ * 0.5, 6), r_ * 1.6, "hot", glow=True)


@design("banner_of_the_march")
def banner_of_the_march(k):
    """a frost legion's standard on a long pole, tattered and iced stiff, the cross-staff hung with the tags of the men who march for it still"""
    R = k.theme("frost", base=0.54)
    k.mat(iron=flat(R["dark"], 0.62, bevel=0.12), cloth=flat(ramp("#14243e", "#1e3458", "#2a4874", "#3a6090"), 0.62, 0.2), ice=flat(R["glow"], 0.84), tag=flat(FE, 0.8))
    pole(k, 35, "iron")
    k.box(0, 32, 0, 19, 1.0, 1.0, "iron")
    k.box(0, 35, 0, 2.4, 0.8, 2.4, "iron")
    k.plate(P((0, 35), (1.6, 38), (0, 41), (-1.6, 38)), 1.0, "ice")
    cloth = P((-8.4, 32), (8.4, 32), (8.4, 14), (6, 16), (4.4, 12), (1.4, 16), (-1, 11), (-4, 15), (-6, 12.6), (-8.4, 15))
    k.plate(cloth, 0.8, "cloth", z=0.8)
    k.plate(P((-3.4, 26), (0, 30), (3.4, 26), (0, 18)), 1.0, "ice", z=0.8)
    k.plate(P((-1.6, 25.6), (0, 27.6), (1.6, 25.6), (0, 21.6)), 1.2, "glow", glow=True, z=0.8)
    for x in (-8.8, 8.8):
        k.box(x, 28, 0, 0.3, 4, 0.3, "tag")
        k.box(x, 26.4, 0, 1.0, 1.6, 0.3, "tag")


@design("brood_distaff")
def brood_distaff(k):
    """a spinner's distaff with a cone of raw silk on it, the silk full of small round shapes, one of them already out and climbing the staff"""
    R = k.theme("silk")
    k.mat(silk=flat(ramp("#8e8498", "#b4aabe", "#d6cede", "#f0ecf4"), 0.76, 0.2, bevel=0.1), oak=flat(R["wood"], 0.66, bevel=0.06), spider=flat(ramp("#0e0a14", "#1a1424", "#2a2038"), 0.6, bevel=0.1), egg=fire(R["glow"], 0.3, 0.7))
    pole(k, 15, "oak")
    k.plate(P(path(qb((-7, 15), (-5, 24), (0, 36), 10), qb((0, 36), (5, 24), (7, 15), 10))), 7.0, "silk")
    for x, y in ((-3, 19), (2.4, 18), (0, 23), (-1.4, 28), (1.4, 30.4)):
        k.plate(disc(x, y, 1.3, 8), 7.3, "egg", glow=True)
    k.box(0, 13.6, 0, 8, 1.4, 8, "oak")
    k.plate(disc(1.4, 4, 1.6, 8) + disc(1.4, 1.6, 1.2, 7), 3.0, "spider", z=0.4)
    for s_ in (1, -1):
        for y in (1, 3, 5):
            k.plate(stroke((1.4, y), (1.4 + s_ * 3, y + 1.6), (1.4 + s_ * 3.6, y - 0.6), 0.4, 4), 0.5, "spider", z=1.2)


@design("spinneret_crown")
def spinneret_crown(k):
    """the Queen's own crown of eight black legs closing over a red hourglass of light, threads strung between them"""
    R = k.theme("silk")
    k.mat(leg=flat(ramp("#0e0a14", "#1a1424", "#2a2038", "#3c3050"), 0.66, bevel=0.1), thread=flat(ramp("#b4aabe", "#d6cede", "#f0ecf4"), 0.8), hot=fire(RUBY, 0.3, 0.7), gold=flat(GOLD, 0.66))
    pole(k, 16, "leg", shoe="gold")
    k.box(0, 15, 0, 5, 2.0, 5, "gold")
    k.plate(P((-4, 28), (4, 28), (0.6, 23), (4, 18), (-4, 18), (-0.6, 23)), 2.4, "hot", glow=True)
    for s_ in (1, -1):
        for a, b_, c, w in (((0.6, 17), (15, 22), (4, 36), 1.1), ((0.6, 17), (10, 24), (2.4, 37), 0.9)):
            k.plate(stroke((s_ * a[0], a[1]), (s_ * b_[0], b_[1]), (s_ * c[0], c[1]), w, 10), 1.4, "leg")
        k.plate(stroke((s_ * 2, 16), (s_ * 12, 14), (s_ * 15, 21), 0.9, 8), 1.2, "leg")
        k.plate(L([(s_ * 12, 19), (s_ * 7, 28)], 0.2) + L([(s_ * 9, 30), (s_ * 3, 34)], 0.2), 0.3, "thread")


@design("crawler_lamp")
def crawler_lamp(k):
    """a miner's carbide lamp with something's antennae coming out of it: the light's lure, and the crawlers come to it"""
    R = k.theme("weeping_mine")
    k.mat(tin=flat(FE, 0.56, bevel=0.14), oak=staves(R["wood"], 1.0, 0.6), shell=flat(ramp("#1a1a14", "#2c2a20", "#403c2e", "#565040"), 0.62, bevel=0.14), light=fire(TEAL, 0.3, 0.7))
    pole(k, 16, "oak")
    k.plate(rect(-4.6, 16, 4.6, 24), 9.0, "tin")
    k.plate(disc(0, 20, 4.0, 16), 9.2, "tin")
    orb(k, 0, 20, 3.0, "light")
    k.plate(disc(0, 20, 2.8, 14), 9.6, "light", glow=True)
    k.plate(P((-3, 24), (3, 24), (2, 27), (-2, 27)), 5.0, "shell")
    for s_ in (1, -1):
        k.plate(stroke((s_ * 1, 27), (s_ * 7, 30), (s_ * 10, 37), 0.5, 8), 0.6, "shell")
        for y in (17, 20, 23):
            k.plate(stroke((s_ * 4.4, y), (s_ * 8, y + 1.4), (s_ * 8.6, y - 1.4), 0.6, 5), 0.8, "shell")


@design("crabcaller")
def crabcaller(k):
    """a conch horn on driftwood, held up in one great red crab's claw like a thing that's been offered to you"""
    R = k.theme("tide_chapel")
    k.mat(shell=flat(ramp("#a8866a", "#c8a888", "#e8ccae", "#f8e8d4"), 0.78, bevel=0.14), pink=flat(ramp("#c8606a", "#e88a8a", "#ffb4a4"), 0.76), claw=flat(ramp("#6a1a10", "#94281a", "#c04024", "#e0603a"), 0.72, bevel=0.14), drift=staves(R["wood"], 1.0, 0.6))
    pole(k, 15, "drift")
    k.plate(P((-2.4, 14), (2.4, 14), (5, 16.6), (3, 19), (-3, 19), (-5, 16.6)), 3.6, "claw")
    k.plate(P((-1, 16), (-5, 17), (-12, 23), (-13, 34), (-10, 28), (-5, 22)), 3.0, "claw")
    k.plate(P((1, 16), (5, 16), (13, 20), (16, 33), (11, 26), (5, 21)), 3.0, "claw")
    k.plate(P((-8, 35), (-2, 31), (5, 33), (8, 27), (5, 21), (0, 21), (-3, 25)), 5.4, "shell")
    k.plate(P((0, 29.6), (4.6, 31.4), (6.6, 27), (4.4, 22.6), (1.4, 23)), 5.6, "pink")
    k.plate(P((1.4, 28.6), (4, 29.6), (5, 27), (3.6, 24.4), (2, 24.6)), 5.8, "dark")
    k.plate(L([(-5.6, 32.4), (-4, 30), (-2.6, 28.6)], 0.3) + L([(-3.4, 26), (-0.6, 30.6)], 0.3) + L([(-1, 23), (0.4, 25)], 0.3), 5.7, "drift")


@design("banditcaller")
def banditcaller(k):
    """a bandit's whistle-horn and a red rag on a spear-butt, a knife stuck through the rag so nobody takes it down"""
    R = k.theme("brigands_gorge")
    k.mat(red=flat(ramp("#4e0810", "#7a1018", "#a81c20", "#d0302a"), 0.66, 0.2), hn=flat(HORN, 0.72, bevel=0.14), steel=flat(FE, 0.8, bevel=0.1), oak=staves(R["wood"], 1.0, 0.6), brass=flat(BRASS, 0.64))
    pole(k, 33, "oak")
    k.plate(P((0, 33), (15, 31), (12, 27), (14, 22), (7, 25), (3, 21), (0, 23)), 0.8, "red", z=0.6)
    k.plate(P((5.4, 34), (6.6, 34), (7, 28), (6, 24), (5, 28)), 0.5, "steel", z=1.2)
    k.box(6, 34, 1.2, 2.8, 0.8, 0.8, "brass")
    k.box(6, 34.8, 1.2, 0.9, 2.8, 0.9, "oak")
    k.plate(stroke((0, 20), (-6, 19), (-8, 13), 1.3, 8), 2.2, "hn")
    k.box(0, 19, 0, 3, 1.4, 3, "brass")


@design("crown_of_thieves")
def crown_of_thieves(k):
    """a stolen gold crown jammed down on a pike, every point now hung with the rings of the men who died taking it"""
    k.theme("brigands_gorge")
    k.mat(gold=flat(GOLD, 0.7, bevel=0.14), steel=flat(FE, 0.76, bevel=0.12), ruby=flat(RUBY, 0.7), cord=flat(LEATHER, 0.6), silver=flat(SILVER, 0.76))
    pole(k, 22, "steel", shoe="steel", grip="cord")
    k.plate(P((-1.4, 30), (1.4, 30), (0, 40)), 1.8, "steel")
    k.box(0, 22, 0, 2, 9, 2, "steel")
    k.plate(P((-8, 22), (8, 22), (9.4, 32), (5, 27), (2.6, 33), (0, 27), (-2.6, 33), (-5, 27), (-9.4, 32)), 3.0, "gold")
    k.plate(rect(-8, 22.6, 8, 24), 3.2, "gold")
    for x, m_ in ((-4.4, "ruby"), (0, "ruby"), (4.4, "ruby")):
        k.plate(disc(x, 23.4, 0.8, 6), 3.4, m_)
    for x, y, m_ in ((-9.4, 31, "silver"), (9.4, 31, "gold"), (-2.6, 32, "silver"), (2.6, 32, "gold")):
        k.plate(ring(x, y - 1.4, 1.1, 0.6), 0.5, m_)


@design("murder_staff")
def murder_staff(k):
    """a black pole with crows perched all the way up it, the top one with its beak open and its eye on you"""
    R = k.theme("rookery")
    k.mat(crow=flat(ramp("#0a0a10", "#14141c", "#1e1e2a", "#2c2c3c", "#40405a"), 0.62, bevel=0.1), beak=flat(ramp("#3a3a40", "#5a5a62", "#7e7e86"), 0.7), pol=flat(R["wood"], 0.5))
    pole(k, 28, "pol")

    def crow(x, y, s_, fw):
        k.plate(P((x - fw * 3 * s_, y + 0.6 * s_), (x + fw * 2 * s_, y + 3.6 * s_), (x + fw * 3 * s_, y + 1.4 * s_), (x + fw * 0.4 * s_, y - 1.4 * s_), (x - fw * 5.4 * s_, y - 2.6 * s_)), 2.2 * s_, "crow")
        k.plate(disc(x + fw * 2.6 * s_, y + 3.4 * s_, 1.5 * s_, 8), 2.2 * s_, "crow")
        k.plate(P((x + fw * 3.6 * s_, y + 4 * s_), (x + fw * 6.4 * s_, y + 3 * s_), (x + fw * 3.6 * s_, y + 2.6 * s_)), 1.0 * s_, "beak")
        k.plate(disc(x + fw * 2.9 * s_, y + 3.7 * s_, 0.4 * s_, 5), 2.4 * s_, "glow", glow=True)

    crow(0.4, 33, 1.5, 1)
    crow(-4, 24, 1.0, -1)
    crow(4, 20, 1.0, 1)
    crow(-3.8, 13, 0.8, -1)
    for y, x in ((22.6, -3), (18.6, 3), (11.6, -3)):
        k.box(x / 2, y, 0, abs(x) + 2, 0.7, 0.7, "pol")


@design("murder")
def murder(k):
    """the Rookery's great corvid skull, a beak as long as your arm, black feathers shaken out behind it like a cape"""
    k.theme("rookery")
    k.mat(bone=bone(IVORY, 0.74), fe=flat(ramp("#0a0a10", "#14141c", "#1e1e2a", "#2c2c3c", "#40405a"), 0.62, bevel=0.1), beak=flat(ramp("#2a2a30", "#44444c", "#62626a"), 0.72, bevel=0.14), hot=fire(RUBY, 0.3, 0.7), pol=flat(NIGHT, 0.6))
    pole(k, 17, "pol")
    for j in range(9):
        a = math.radians(160 - j * 18 + 10)
        ln = 15 + 3 * math.sin(j * 1.1)
        tip = (-2 + math.cos(a) * ln, 26 + math.sin(a) * ln * 0.9)
        k.plate(P((-2, 26), (tip[0] - 1.6, tip[1] - 1), tip, (tip[0] + 1.8, tip[1] - 1.8)), 1.2, "fe", z=-1.4 - j * 0.1)
    k.plate(disc(0, 26, 6.6, 16) + rect(-3, 17, 3, 22), 5.0, "bone")
    k.plate(P((4, 31), (19, 18), (4.6, 23)), 3.4, "beak")
    k.plate(P((3.6, 23), (14, 19), (3, 20)), 2.6, "beak")
    k.plate(disc(1, 28, 2.0, 9), 5.2, "dark")
    k.plate(disc(1.2, 28, 0.9, 7), 5.4, "hot", glow=True)


@design("puppeteer_cross")
def puppeteer_cross(k):
    """a marionette's control bar stood on a staff, strings running down to a small painted wooden hand that's holding on to them"""
    R = k.theme("hollow_circus")
    red = ramp("#2a0408", "#4e0810", "#7a1018", "#a81c20", "#d0302a")
    cream = ramp("#8e7c60", "#b4a282", "#d6c8a8", "#efe4c8")
    k.mat(st=stripes(red, cream, 3.0, 0.5), oak=flat(ramp("#6a4426", "#8e6034", "#b07e48"), 0.7, bevel=0.1), str_=fire(WARM, 0.3, 0.7), gold=flat(GOLD, 0.66), hand=flat(BIRCH, 0.8, bevel=0.1))
    pole(k, 31, "st", shoe="gold")
    k.box(0, 30, 0, 22, 2.0, 1.8, "oak")
    k.box(0, 30, 0, 1.8, 2.0, 16, "oak")
    k.box(0, 33, 0, 3, 2.0, 3, "gold")
    for x, b_ in ((-10, 12), (10, 13), (-6, 15), (6, 14.6)):
        k.plate(L([(x, 30), (x, b_)], 0.14), 0.2, "str_", glow=True)
    for x, y in ((-10, 12), (10, 13)):
        k.plate(P((x - 1.6, y), (x + 1.6, y), (x + 1.4, y - 3), (x - 1.4, y - 3)), 1.4, "hand")
        k.plate(L([(x - 1.0, y - 3), (x - 1.4, y - 5.4)], 0.5) + L([(x + 0.1, y - 3), (x, y - 6)], 0.5) + L([(x + 1.0, y - 3), (x + 1.4, y - 5.4)], 0.5), 1.0, "hand")


@design("strings_attached")
def strings_attached(k):
    """the Ringmaster's great cross, gilt and red, and hanging from its strings a tiny grinning jester doll that's looking up at you"""
    k.theme("hollow_circus")
    k.mat(gold=flat(GOLD, 0.7, bevel=0.14), red=flat(ramp("#4e0810", "#7a1018", "#a81c20", "#d0302a"), 0.7, bevel=0.1), cream=flat(BIRCH, 0.8, bevel=0.1), str_=fire(WARM, 0.3, 0.7), blue=flat(ramp("#142458", "#1e3a84", "#2c54b0"), 0.7))
    pole(k, 32, "red", shoe="gold", grip="gold")
    k.plate(rect(-13, 30, 13, 33) + rect(-1.6, 23, 1.6, 39), 2.4, "gold")
    for x in (-13, 13):
        k.plate(disc(x, 31.6, 2.2, 10), 2.8, "red")
    k.plate(P((-1.6, 39), (0, 42), (1.6, 39)), 2.0, "red")
    for x in (-11, 11):
        k.plate(L([(x, 30), (x * 0.6, 19)], 0.14), 0.2, "str_", glow=True)
    for s_ in (1, -1):
        cx = s_ * 8.4
        k.plate(disc(cx, 17, 2.4, 10), 2.0, "cream")
        k.plate(P((cx - 2.6, 18), (cx - 4.4, 22), (cx - 1, 19.6)) + P((cx + 2.6, 18), (cx + 4.4, 22), (cx + 1, 19.6)), 1.0, "red" if s_ > 0 else "blue")
        k.plate(disc(cx - 0.9, 17.4, 0.4, 5) + disc(cx + 0.9, 17.4, 0.4, 5), 2.2, "dark")
        k.plate(rect(cx - 1.3, 15.8, cx + 1.3, 16.2), 2.2, "red")
        k.plate(P((cx - 2.4, 14.6), (cx + 2.4, 14.6), (cx + 2, 8.6), (cx - 2, 8.6)), 1.8, "blue" if s_ > 0 else "red")
        k.plate(rect(cx - 2, 6, cx - 0.5, 8.6) + rect(cx + 0.5, 6, cx + 2, 8.6), 1.4, "red" if s_ > 0 else "blue")


@design("toadcaller")
def toadcaller(k):
    """a fat stone toad squatting on the head of a marsh staff, its throat swelling with light, its mouth just opening"""
    R = k.theme("mirefen_coven")
    k.mat(stone=flat(ramp("#26301c", "#3a4a28", "#506636", "#6c8446"), 0.62, 0.2, bevel=0.14), belly=fire(ramp("#7ec41e", "#b4e848", "#e4ffa0"), 0.3, 0.7), stick=staves(R["wood"], 1.0, 0.6), eye=flat(ramp("#c8a020", "#f0d048"), 0.8))
    pole(k, 17, "stick")
    k.plate(P((-9.4, 17), (9.4, 17), (10, 21), (7, 28), (3.6, 30), (-3.6, 30), (-7, 28), (-10, 21)), 8.0, "stone")
    k.plate(disc(0, 22, 4.4, 14), 8.6, "belly", glow=True)
    k.plate(disc(-4.6, 30, 2.4, 9) + disc(4.6, 30, 2.4, 9), 4.0, "stone")
    k.plate(disc(-4.6, 30.4, 1.2, 7) + disc(4.6, 30.4, 1.2, 7), 4.4, "eye")
    k.plate(rect(-4.8, 30, -4.4, 31) + rect(4.4, 30, 4.8, 31), 4.6, "dark")
    k.plate(rect(-6.4, 26.4, 6.4, 27), 8.4, "dark")
    for s_ in (1, -1):
        for x in (6, 8, 10):
            k.plate(rect(s_ * x - 0.5, 15.4, s_ * x + 0.5, 17.6), 1.6, "stone")


@design("canopic_staff")
def canopic_staff(k):
    """a canopic jar on a sceptre, its stopper a jackal's head, the seal cracked and something in it wanting out"""
    k.theme("sandsunk_tomb")
    k.mat(alab=flat(ramp("#a89a7e", "#c8ba9c", "#e6dabc", "#f6eed8"), 0.74, bevel=0.14), blk=flat(ramp("#0e0c10", "#1a1820", "#2a2632"), 0.62, bevel=0.14), gold=flat(GOLD, 0.68), lapis=flat(ramp("#0e2a6e", "#163e96", "#2458c0"), 0.56), hot=fire(TEAL, 0.3, 0.7))
    pole(k, 14, "lapis", shoe="gold", grip="gold")
    k.plate(P((-3.6, 14), (3.6, 14), (6.4, 19), (6.4, 26), (4.4, 28), (-4.4, 28), (-6.4, 26), (-6.4, 19)), 7.0, "alab")
    for y in (17, 20, 23):
        k.plate(rect(-3.4, y, 3.4, y + 0.6), 7.2, "lapis")
    k.plate(L([(1, 28), (-1, 24), (1.6, 22), (0, 18)], 0.4), 7.3, "hot", glow=True)
    k.plate(rect(-4.8, 28, 4.8, 29), 5.6, "gold")
    k.plate(P((-3.6, 29), (3.6, 29), (4, 32), (2, 35), (-2, 35), (-4, 32)), 4.6, "blk")
    k.plate(P((-3.4, 34), (-1.2, 34), (-2.6, 39.4)) + P((3.4, 34), (1.2, 34), (2.6, 39.4)), 1.6, "blk")
    k.plate(P((2, 33), (2, 30.4), (8.4, 30)), 3.0, "blk")
    k.plate(disc(0.8, 32.6, 0.6, 5), 4.8, "gold")


@design("leechcaller")
def leechcaller(k):
    """a physician's glass leech-jar on a stick, water red with them, a few on the outside feeling for you"""
    k.theme("fallen_titan")
    k.mat(glass=flat(ramp("#5a2a2e", "#864246", "#b4686c"), 0.5, bevel=0.2), blood=fire(ramp("#7a0a10", "#b81a1c", "#e84a30"), 0.3, 0.6), leech=flat(ramp("#0a0608", "#180c10", "#28161a"), 0.7, bevel=0.1), cork=flat(CORK, 0.7), shaft=bone(IVORY, 0.56))
    pole(k, 15, "shaft", shoe="cork")
    k.plate(P((-6, 15), (6, 15), (6.6, 28), (3.6, 30), (-3.6, 30), (-6.6, 28)), 7.6, "glass")
    k.plate(rect(-5, 16, 5, 26.6), 8.0, "blood", glow=True)
    k.plate(rect(-3.6, 30, 3.6, 33), 4.6, "cork")
    for a, b_, c in (((-3, 18), (-1, 21), (-3, 24)), ((1, 23), (3, 21), (2.6, 18)), ((-4, 28), (-8, 27), (-8, 20)), ((5, 28), (9, 29), (8, 22))):
        k.plate(stroke(a, b_, c, 0.9, 6), 8.4 if abs(a[0]) < 3.2 else 1.2, "leech")


@design("acolyte_bell")
def acolyte_bell(k):
    """a jade temple's prayer bells, three of them on a tall lacquered pole, red tassels tied under each"""
    R = k.theme("jade_monastery", base=0.54)
    jade = ramp("#0e4a34", "#1a7050", "#2e9a70", "#5cc898", "#a0ecc8")
    k.mat(jade=flat(jade, 0.74, bevel=0.14), lacq=flat(ramp("#2a0608", "#4a0c10", "#6e1616"), 0.6, bevel=0.06), gold=flat(GOLD, 0.68), red=flat(ramp("#7a1018", "#a81c20", "#d0302a"), 0.72))
    pole(k, 30, "lacq", shoe="gold", grip="gold")
    k.box(0, 29, 0, 21, 1.2, 1.4, "gold")
    k.plate(P((-10.4, 30.2), (-11.6, 33), (-9, 31.4)) + P((10.4, 30.2), (11.6, 33), (9, 31.4)), 1.2, "gold")
    k.plate(P((-1.4, 30), (1.4, 30), (0, 37)), 1.2, "gold")
    for x, top in ((-8, 29), (0, 29), (8, 29)):
        bell(k, x, top, 5.6, "jade", 4)
        k.plate(rect(x - 0.3, 18, x + 0.3, top - 8.6) + P((x - 1, 18), (x + 1, 18), (x + 1.4, 13), (x - 1.4, 13)), 0.9, "red")


@design("prayer_of_hands")
def prayer_of_hands(k):
    """the Abbot's thousand-armed rail: rows of small jade hands in a halo, each with a different sign, a stilled white flame at the centre"""
    R = k.theme("jade_monastery", base=0.54)
    jade = ramp("#0e4a34", "#1a7050", "#2e9a70", "#5cc898", "#a0ecc8")
    k.mat(jade=flat(jade, 0.78, bevel=0.1), gold=flat(GOLD, 0.68, bevel=0.14), flame=fire(HOT, 0.2, 0.8), lacq=flat(ramp("#2a0608", "#4a0c10", "#6e1616"), 0.6))
    pole(k, 14, "lacq", shoe="gold", grip="gold")
    k.plate(ring(0, 24, 8.0, 6.6), 2.0, "gold")
    for j in range(14):
        a = j * 2 * math.pi / 14 + 0.2
        c, s_ = math.cos(a), math.sin(a)
        x, y = c * 10, 24 + s_ * 10
        k.plate(P((c * 7.6 - s_ * 0.8, 24 + s_ * 7.6 + c * 0.8), (x - s_ * 1.4, y + c * 1.4), (x + c * 3 - s_ * 1.1, y + s_ * 3 + c * 1.1), (x + c * 3 + s_ * 1.1, y + s_ * 3 - c * 1.1), (x + s_ * 1.4, y - c * 1.4), (c * 7.6 + s_ * 0.8, 24 + s_ * 7.6 - c * 0.8)), 1.2, "jade")
    k.plate(P(path(qb((0, 19), (-4, 23), (0, 31), 8), qb((0, 31), (4, 23), (0, 19), 8))), 2.0, "flame", glow=True)
    k.plate(disc(0, 16, 2.4, 10), 2.4, "gold")


@design("sparkcaller")
def sparkcaller(k):
    """a copper Tesla ball on a coil wrapped staff, small crackling things climbing up it and leaping off"""
    R = k.theme("storm_bastion")
    k.mat(iron=flat(R["dark"], 0.66, bevel=0.12), copper=flat(ramp("#6a3414", "#9c5a24", "#c8843c", "#e8a860"), 0.7, bevel=0.1), ball=flat(ramp("#6a3414", "#9c5a24", "#c8843c", "#e8a860", "#ffd090"), 0.7, bevel=0.2), white=flat(R["glow"], 0.92, bevel=0.02))
    pole(k, 22, "iron")
    for y in range(6, 22, 2):
        k.box(0, y, 0, 4.0 - (y - 6) * 0.08, 1.2, 4.0 - (y - 6) * 0.08, "copper")
    orb(k, 0, 28, 5.0, "ball")
    k.plate(disc(0, 28, 4.6, 16), 5.2, "ball")
    for pts in (((-4, 31), (-8, 33), (-7, 36), (-11, 39)), ((4, 30), (8, 29), (9, 33), (13, 33)), ((1, 33), (2, 37), (0, 39), (2, 43)), ((-3, 25), (-7, 24), (-9, 20))):
        k.plate(L(list(pts), 0.4), 0.5, "white", glow=True)


@design("thrallcaller")
def thrallcaller(k):
    """a blood-court house key the size of a sword: open the door, and whoever owes the House comes through it"""
    k.theme("bloodmoon_court")
    k.mat(silver=flat(SILVER, 0.72, bevel=0.14), ruby=fire(RUBY, 0.3, 0.7), lacq=flat(ramp("#14040a", "#280a12", "#42101c"), 0.6, bevel=0.06))
    pole(k, 30, "silver", 1.8, grip="lacq", shoe="silver")
    k.plate(ring(0, 32, 7.0, 4.6) + ring(-7, 32, 3.0, 1.6) + ring(7, 32, 3.0, 1.6), 1.8, "silver")
    k.plate(disc(0, 32, 2.4, 10), 2.2, "ruby", glow=True)
    k.plate(P((0, 40.6), (1.6, 38.4), (0, 36.2), (-1.6, 38.4)), 1.8, "silver")
    k.plate(rect(1, 8, 7.6, 11) + rect(1, 12.4, 5.6, 14.6) + rect(5, 11, 6.4, 12.4), 1.4, "silver")


@design("crimson_chalice")
def crimson_chalice(k):
    """the Countess's chalice held up on a long stem, brim-full, a lip of blood running over one side and down the staff"""
    k.theme("bloodmoon_court")
    k.mat(gold=flat(GOLD, 0.7, bevel=0.14), blood=fire(ramp("#7a0a10", "#b81a1c", "#e84a30", "#ffa080"), 0.3, 0.7), ruby=flat(RUBY, 0.74), lacq=flat(ramp("#14040a", "#280a12", "#42101c"), 0.6, bevel=0.06))
    pole(k, 18, "lacq", shoe="gold", grip="gold")
    k.box(0, 18, 0, 2.6, 5, 2.6, "gold")
    k.plate(disc(0, 21, 2.4, 10), 3.4, "gold")
    k.plate(P(path(qb((-9, 35), (-9, 24), (-1.4, 23), 8), qb((1.4, 23), (9, 24), (9, 35), 8), (9, 35))), 9.0, "gold")
    k.box(0, 34.4, 0, 16, 0.8, 8, "blood", glow=True)
    for x in (-4.4, 0, 4.4):
        k.plate(disc(x, 29, 1.1, 8), 9.4, "ruby")
    k.plate(P((5, 35), (9.4, 35), (9.4, 26), (9, 22), (8.4, 29), (6, 30)), 9.2, "blood", glow=True)
    k.plate(wave(lambda t: 2.0 + 0.5 * math.sin(t * 7), lambda t: 0.4, 21, 5, 7), 2.8, "blood", glow=True)


@design("impcaller")
def impcaller(k):
    """an obsidian pitchfork, tines still hot, with a small horned thing sitting cross-legged on the crossbar, grinning"""
    k.theme("obsidian_labyrinth")
    k.mat(glass=flat(ramp("#0c0a10", "#16141e", "#26222e", "#3a3444"), 0.7, bevel=0.2), hot=fire(HOT, 0.3, 0.7), imp=flat(ramp("#5a1006", "#801a0a", "#a82c12", "#d04a1e"), 0.7, bevel=0.1), bronze=flat(BRASS, 0.6))
    pole(k, 22, "bronze", 2.0, grip="wrap")
    k.plate(rect(-9, 21, 9, 23.4), 2.4, "glass")
    for x, h in ((-8, 36), (0, 40), (8, 36)):
        k.plate(P((x - 1.6, 23), (x + 1.6, 23), (x, h)), 2.0, "glass")
        k.plate(P((x - 0.5, h - 8), (x + 0.5, h - 8), (x, h)), 2.3, "hot", glow=True)
    k.plate(P((3, 23.4), (6.6, 23.4), (6, 27), (3.6, 27)), 2.6, "imp", z=2.4)
    k.plate(disc(4.8, 28.4, 1.9, 8), 2.6, "imp", z=2.4)
    k.plate(P((3.2, 29.6), (3.6, 32), (4.4, 30)) + P((6.4, 29.6), (6, 32), (5.2, 30)), 1.0, "glass", z=2.4)
    k.plate(disc(4.1, 28.6, 0.3, 4) + disc(5.5, 28.6, 0.3, 4), 2.8, "hot", glow=True, z=2.4)


@design("deepcaller")
def deepcaller(k):
    """an anglerfish's lure on a long bent rod: the rod is the fish's own spine, the light is the last thing anything down there sees"""
    R = k.theme("abyssal_lighthouse")
    k.mat(sp=bone(ramp("#1a1a2a", "#28283e", "#3a3a56", "#50507a"), 0.62), tooth=flat(IVORY, 0.84), rim=fire(R["glow"], 0.4, 0.6))
    pole(k, 18, "sp", shoe="sp")
    for j in range(13):
        t = j / 12
        x = 13 * t * t
        y = 18 + 18 * math.sin(t * 2.3) * 1.04
        k.plate(disc(x, y, 1.1 - t * 0.3, 6), 1.6, "sp")
        if j % 2 == 0:
            k.plate(P((x - 0.3, y), (x + 0.3, y), (x + 1.6, y + 1.6)), 0.5, "sp")
    orb(k, 14, 20, 2.6, "rim")
    k.plate(rect(13.7, 22, 14.3, 25), 0.5, "sp")
    for j in range(5):
        k.plate(P((-7 + j * 2.6, 21), (-5.4 + j * 2.6, 21), (-6.2 + j * 2.6, 26)), 0.8, "tooth")


@design("cherubcaller")
def cherubcaller(k):
    """a small white stone cherub on a column, wings up, both hands over its eyes; don't let it uncover them"""
    k.theme("eclipse_cathedral", base=0.5)
    k.mat(mar=flat(ramp("#6a6870", "#9694a0", "#c2c0ca", "#e6e4ec", "#fafaff"), 0.8, bevel=0.14), shade=flat(ramp("#6a6870", "#9694a0", "#c2c0ca", "#e6e4ec", "#fafaff"), 0.56, bevel=0.14), gold=flat(GOLD, 0.68), rod=flat(BIRCH, 0.6, bevel=0.06), hot=fire(ramp("#ffe08a", "#fff6d0", "#ffffff"), 0.4, 0.6))
    pole(k, 13, "rod", shoe="gold", grip="gold")
    k.plate(rect(-4.6, 13, 4.6, 15), 5.0, "gold")
    k.plate(P((-3.4, 15), (3.4, 15), (3, 20.6), (-3, 20.6)), 3.6, "mar")
    for s_ in (1, -1):
        k.plate(P((s_ * 3, 19), (s_ * 7, 25), (s_ * 14, 34), (s_ * 15, 26), (s_ * 13, 27), (s_ * 13.6, 20), (s_ * 11, 22), (s_ * 10.6, 15), (s_ * 8, 18), (s_ * 3, 16)), 1.2, "shade", z=-1.2)
    k.plate(disc(0, 26.6, 6.2, 16), 6.0, "mar")
    k.plate(P((-6, 26), (-0.3, 26), (-0.3, 29.6), (-5.4, 29.6)) + P((6, 26), (0.3, 26), (0.3, 29.6), (5.4, 29.6)), 6.8, "shade")
    for x in (-4.2, -2.4, 2.4, 4.2):
        k.plate(rect(x - 0.12, 27.6, x + 0.12, 29.6), 6.9, "dark")
    k.plate(rect(-1.6, 23, 1.6, 23.5), 6.2, "dark")
    k.plate(ring(0, 36, 5.6, 4.6), 0.8, "hot", glow=True)


@design("koboldcaller")
def koboldcaller(k):
    """a scrap-and-candle hoard stick: a pot lid, a stolen spoon, a nail, a coin, a kobold's skull with a birthday candle on it"""
    k.theme("wyrms_hoard")
    k.mat(oak=staves(ramp("#3a2410", "#52341c", "#6e4826"), 1.0, 0.6), tin=flat(FE, 0.66), gold=flat(GOLD, 0.7), bone=bone(IVORY, 0.72), wax=flat(ramp("#a81c20", "#d0302a"), 0.8), flame=fire(WARM, 0.1, 0.9), cord=flat(LEATHER, 0.66))
    pole(k, 18, "oak")
    k.plate(P((-4, 26), (4, 26), (5.4, 21), (2.4, 18), (0, 15.4), (-2.4, 18), (-5.4, 21)), 4.4, "bone")
    k.plate(disc(-2, 22.4, 1.1, 6) + disc(2, 22.4, 1.1, 6), 4.6, "dark")
    k.plate(P((-2, 15.6), (2, 15.6), (1.6, 14.4), (-1.6, 14.4)), 3.0, "bone")
    k.box(0, 26, 0, 1.0, 3.6, 1.0, "wax")
    k.plate(P(path(qb((0, 29.8), (-1.4, 30.6), (0, 33), 4), qb((0, 33), (1.4, 30.6), (0, 29.8), 4))), 0.8, "flame", glow=True)
    k.plate(P((-4, 27), (-5, 26), (-9, 30), (-7.4, 31.6)), 0.8, "tin", z=2)
    k.plate(disc(8.4, 30.4, 2.6, 10), 0.8, "tin")
    k.plate(stroke((3.4, 25), (6, 26.6), (7, 27.6), 0.8, 4), 0.8, "tin")
    k.plate(disc(-6, 14, 1.8, 10), 0.5, "gold")
    k.box(-6, 15.4, 0, 0.3, 3.0, 0.3, "cord")
    k.box(-3, 18.2, 0, 6, 0.3, 0.3, "cord")


# ---------------------------------------------------------------- the world's

@design("bone_rattle")
def bone_rattle(k):
    """a shaman's gourd rattle, stitched with knuckle bones and strung with finger joints, a feather tied on"""
    gourd = ramp("#4a2e14", "#6a4620", "#8e6230", "#b08044")
    k.mat(g=flat(gourd, 0.66, bevel=0.14), bone=bone(IVORY, 0.76), oak=staves(ramp("#3a2410", "#52341c", "#6e4826"), 1.0, 0.6), fe=flat(ramp("#7a1018", "#a81c20", "#d0302a"), 0.76), cord=flat(LEATHER, 0.66), wrap=wrap(LEATHER, IVORY[1], 5), dark=flat(IRON, 0.6))
    pole(k, 18, "oak")
    k.plate(disc(0, 25, 7.2, 16), 7.0, "g")
    k.plate(rect(-2, 16, 2, 19), 3.2, "g")
    for j in range(8):
        a = j * math.pi / 4
        k.plate(rect(math.cos(a) * 4.6 - 0.8, 25 + math.sin(a) * 4.6 - 0.8, math.cos(a) * 4.6 + 0.8, 25 + math.sin(a) * 4.6 + 0.8), 7.6, "bone")
    k.plate(disc(0, 25, 1.4, 8), 7.5, "bone")
    for x, ln in ((-5, 9), (5, 8)):
        k.box(x, 18.6 - ln + 2, 3, 0.3, ln, 0.3, "cord")
        for y in (0, 2.4):
            k.box(x, 18.6 - ln + 2 + y, 3, 1.0, 1.6, 1.0, "bone")
    k.plate(P((0, 32), (5, 41), (6.6, 38), (1.6, 31)), 0.5, "fe")


@design("raven_totem")
def raven_totem(k):
    """a northern carved raven, beak and wings painted black and red, on a totem post"""
    red = ramp("#7a1018", "#a81c20", "#d0302a")
    blk = ramp("#0e0e12", "#1a1a20", "#2a2a32", "#3c3c46")
    cedar = ramp("#4a2a16", "#6a3e22", "#8c5632", "#ae7248")
    k.mat(c=staves(cedar, 1.4, 0.6), b=flat(blk, 0.66, bevel=0.14), r=flat(red, 0.72), w=flat(BIRCH, 0.82), wrap=wrap(blk, red[1], 4), dark=flat(blk, 0.6))
    pole(k, 10, "c", 3.0)
    k.box(0, 10, 0, 5, 12, 4.4, "c")
    k.plate(rect(-2.4, 13, 2.4, 15) + rect(-2.4, 11, 2.4, 12), 4.6, "r")
    k.plate(disc(-1.3, 18.6, 1.0, 7) + disc(1.3, 18.6, 1.0, 7), 4.6, "w")
    k.plate(disc(-1.3, 18.6, 0.5, 5) + disc(1.3, 18.6, 0.5, 5), 4.8, "b")
    k.box(0, 22, 0, 5.4, 11, 5, "b")
    k.plate(P((2, 32), (12, 27), (2, 26)), 3.0, "b")
    k.plate(P((2, 29), (12, 27), (2, 27.6)), 3.2, "r")
    k.plate(disc(0, 29, 1.2, 7), 5.2, "w")
    k.plate(disc(0.2, 29, 0.6, 5), 5.4, "b")
    for s_ in (1, -1):
        k.plate(P((s_ * 2.4, 31), (s_ * 15, 37), (s_ * 15, 30), (s_ * 12, 31), (s_ * 12, 26), (s_ * 9, 28), (s_ * 8, 24), (s_ * 2.4, 25)), 1.4, "b")
        k.plate(P((s_ * 4, 30), (s_ * 13, 35), (s_ * 13, 32)), 1.6, "r")
        k.plate(disc(s_ * 6, 27.4, 0.9, 6), 1.6, "w")


@design("lichcaller")
def lichcaller(k):
    """green fire in a king's skull, the jaw held shut with a silver wire, black iron crown spiked into the bone"""
    k.mat(bone=bone(ramp("#6a6048", "#8e8264", "#b0a682", "#d6cca8"), 0.72), iron=flat(ramp("#0e0e12", "#1a1a20", "#2a2a32", "#3c3c46"), 0.66, bevel=0.14), hot=fire(ramp("#1a7a30", "#30c050", "#70f080", "#c8ffd0"), 0.3, 0.7), silver=flat(SILVER, 0.8), wrap=wrap(ramp("#0e0e12", "#1a1a20"), ramp("#1a7a30", "#30c050")[1], 4), dark=flat(ramp("#050508", "#0a0a0e"), 0.6))
    pole(k, 14, "iron")
    skull(k, 0, 20, 1.5, "bone", "hot")
    k.plate(P((-5, 26), (5, 26), (5.6, 30), (3, 27.4), (1.6, 32), (0, 28), (-1.6, 32), (-3, 27.4), (-5.6, 30)), 7.8, "iron")
    k.plate(P(path(qb((-2.4, 27), (-4, 31), (0, 38), 8), qb((0, 38), (4, 31), (2.4, 27), 8))), 1.6, "hot", glow=True)
    k.plate(rect(-5, 15.4, 5, 15.8), 6.2, "silver")


@design("hollow_kings_crown")
def hollow_kings_crown(k):
    """a dead king's crown hung from a black spear on a chain, no head in it, and a court's worth of tiny pale kneeling figures round the rim"""
    k.mat(iron=flat(ramp("#0e0e12", "#1a1a20", "#2a2a32", "#3c3c46"), 0.66, bevel=0.14), gold=flat(ramp("#3a2a12", "#5a4220", "#7c5e30", "#a08044", "#c0a05e"), 0.66, bevel=0.14), ghost=flat(ramp("#7e8a8e", "#a4b0b4", "#ccd8dc"), 0.76), wrap=wrap(ramp("#0e0e12", "#1a1a20"), ramp("#3a2a12", "#5a4220")[1], 4), dark=flat(ramp("#050508", "#0a0a0e"), 0.6), hot=fire(ramp("#7e8a8e", "#ccd8dc", "#ffffff"), 0.3, 0.7))
    pole(k, 30, "iron")
    k.plate(P((-1.8, 30), (1.8, 30), (0, 41)), 1.8, "iron")
    k.plate(stroke((0, 28), (7, 31), (10, 27), 1.0), 1.2, "iron")
    links(k, [(10, 26.4), (10, 24.8)], "gold", 0.6)
    k.plate(P((3, 13), (17, 13), (18.4, 22), (15, 17.6), (12.6, 24), (10, 18), (7.4, 24), (5, 17.6), (1.6, 22)), 9.0, "gold")
    k.plate(P((5, 16), (15, 16), (15, 18), (5, 18)), 9.2, "hot", glow=True)
    for x in (3.6, 7, 10, 13, 16.4):
        k.plate(disc(x, 11.8, 0.7, 5) + P((x - 0.8, 11), (x + 0.8, 11), (x + 0.5, 9.4), (x - 0.5, 9.4)), 0.8, "ghost")


@design("kennel_crook")
def kennel_crook(k):
    """a hound master's iron crook with a wide spiked collar locked on the curl, its chain cut, a dog's whistle on a thong"""
    k.mat(iron=flat(IRON, 0.62, bevel=0.14), hide=flat(LEATHER, 0.62, bevel=0.1), steel=flat(FE, 0.84), brass=flat(BRASS, 0.7), oak=staves(ramp("#3a2410", "#52341c", "#6e4826"), 1.0, 0.6), wrap=wrap(LEATHER, IRON[1], 5), dark=flat(IRON, 0.6))
    pole(k, 24, "oak")
    hook(k, 24, 5, "iron", 1.5)
    k.plate(ring(11, 19, 5.6, 3.8), 2.8, "hide")
    for j in range(10):
        a = j * math.pi / 5
        k.plate(P((11 + math.cos(a - 0.2) * 5.4, 19 + math.sin(a - 0.2) * 5.4), (11 + math.cos(a) * 8, 19 + math.sin(a) * 8), (11 + math.cos(a + 0.2) * 5.4, 19 + math.sin(a + 0.2) * 5.4)), 0.9, "steel")
    k.plate(rect(9.4, 12, 12.6, 14.4), 3.2, "brass")
    links(k, [(11, 11.2), (11, 9.6), (11, 8)], "iron", 0.7)
    k.box(-1.6, 15, 0, 0.3, 6, 0.3, "hide")
    k.box(-2.4, 12.6, 0, 1.2, 3, 1.2, "brass")


@design("broodcaller")
def broodcaller(k):
    """a veined egg sac on a tall wet stalk, the shapes in it turning over in their sleep"""
    flesh = ramp("#3a1a2a", "#5a2a40", "#7c4058", "#a05e74", "#c8849a")
    k.mat(st=flat(flesh, 0.56, bevel=0.1), sac=fire(ramp("#7a1a5a", "#b03a80", "#e070b0", "#ffb0d8"), 0.2, 0.6), shape=flat(ramp("#2a0a24", "#3e1036"), 0.6), vein=flat(ramp("#3a1a2a", "#5a2a40"), 0.8), wrap=wrap(flesh, flesh[0], 4), dark=flat(flesh, 0.4), wood=flat(flesh, 0.5))
    pole(k, 18, "st", 2.2)
    m = P(path(qb((-2, 18), (-12, 22), (-7, 32), 8), qb((-7, 32), (0, 40), (7, 32), 8), qb((7, 32), (12, 22), (2, 18), 8)))
    k.plate(m, 8.0, "sac", glow=True)
    for x, y, a in ((-3.6, 25, 0.6), (3, 29, -0.4), (2, 22, 1.4), (-1.6, 32, -1)):
        k.plate(P(path(qb((x - math.cos(a) * 3, y - math.sin(a) * 3), (x + math.sin(a) * 3, y - math.cos(a) * 3), (x + math.cos(a) * 3, y + math.sin(a) * 3), 6), qb((x + math.cos(a) * 3, y + math.sin(a) * 3), (x - math.sin(a) * 1, y + math.cos(a) * 1), (x - math.cos(a) * 3, y - math.sin(a) * 3), 6))), 8.2, "shape")
    k.plate(stroke((0, 18), (-7, 26), (-3, 37), 0.3) + stroke((1, 18), (8, 26), (3, 37), 0.3), 8.3, "vein")


@design("sporemother")
def sporemother(k):
    """a great glowing bracket-cap mushroom on a stem, little spore-children hanging by threads under the gills"""
    cap = ramp("#1a4a4a", "#2a7070", "#3e9a96", "#5cc4bc")
    k.mat(c=flat(cap, 0.66, 0.2, bevel=0.14), stem=flat(ramp("#8e8878", "#b4ae9c", "#d6d0be"), 0.62, bevel=0.1), gill=fire(TEAL, 0.3, 0.7), child=flat(ramp("#d6d0be", "#efeadb"), 0.8), thread=flat(ramp("#8ceee2", "#f0fffc"), 0.7), wrap=wrap(cap, cap[0], 4), dark=flat(cap, 0.5), wood=flat(cap, 0.4))
    pole(k, 22, "stem", 3.0)
    k.plate(P(path(qb((-15, 27), (-13, 38), (0, 38), 10), qb((0, 38), (13, 38), (15, 27), 10))), 12.0, "c")
    k.box(0, 26, 0, 29, 1.6, 11, "gill", glow=True)
    for x, y in ((-7, 34), (-1, 33), (7, 34.4), (3.4, 31)):
        k.plate(disc(x, y, 1.3, 8), 12.2, "gill", glow=True)
    for x, ln in ((-11, 8), (-6, 12), (6, 11), (11, 7)):
        k.box(x, 26 - ln, 0, 0.3, ln, 0.3, "thread")
        k.plate(disc(x, 26 - ln - 1, 1.6, 8) + P((x - 1.4, 26 - ln - 2), (x + 1.4, 26 - ln - 2), (x, 26 - ln - 5)), 1.8, "child")
        k.plate(disc(x - 0.6, 26 - ln - 0.8, 0.3, 4) + disc(x + 0.6, 26 - ln - 0.8, 0.3, 4), 2.0, "dark")


@design("bone_gate")
def bone_gate(k):
    """a little arch of ribs and thigh bones, a dark doorway in it, and bone hands coming through from the other side"""
    k.mat(bone=bone(IVORY, 0.72), void=flat(ramp("#000000", "#040408", "#0a0a14"), 0.3, bevel=0), edge=fire(VOID, 0.3, 0.7), iron=flat(IRON, 0.6), wrap=wrap(IVORY, IRON[1], 4), dark=flat(IRON, 0.6), wood=bone(IVORY, 0.54))
    pole(k, 14, "wood")
    door = P(path((-7, 14), qb((-7, 28), (-5, 32), (0, 33), 6), qb((5, 32), (7, 28), (7, 14), 6)))
    k.plate(door, 1.0, "void")
    k.plate(door.inset(0.5), 1.2, "edge", glow=True)
    k.plate(door.inset(1.0), 1.4, "void")
    for s_ in (1, -1):
        k.box(s_ * 8.4, 14, 0, 2.6, 14, 2.6, "bone")
        k.plate(disc(s_ * 8.4, 14, 2.0, 8) + disc(s_ * 8.4, 28, 2.0, 8), 3.0, "bone")
    for j in range(13):
        a = math.radians(j * 15)
        k.plate(disc(math.cos(a) * 8.4, 28 + math.sin(a) * 8.4, 1.5, 6), 2.8, "bone")
    k.plate(disc(0, 37, 2.4, 9), 3.4, "bone")
    k.plate(disc(-0.9, 37.2, 0.5, 5) + disc(0.9, 37.2, 0.5, 5), 3.6, "edge", glow=True)
    for x, y, a in ((-3, 18, 1), (3, 23, -1)):
        k.plate(rect(x - 0.6, y - 4, x + 0.6, y), 1.0, "bone", z=1.0)
        k.plate(disc(x, y + 0.6, 1.1, 7), 1.0, "bone", z=1.0)
        for f in (-1, 0, 1):
            k.plate(L([(x + f * 0.8, y + 1), (x + f * 1.4, y + 3.4)], 0.3), 0.7, "bone", z=1.0)


@design("bound_accord")
def bound_accord(k):
    """the third hand of the bargain: a black gauntlet raised out of the staff, a chain round the wrist, its fingers spread, three small souls circling them"""
    k.mat(iron=flat(FE, 0.56, bevel=0.14), gold=flat(GOLD, 0.66, bevel=0.14), hot=fire(TEAL, 0.4, 0.6), wrap=wrap(NIGHT, GOLD[3], 4), dark=flat(IRON, 0.7), wood=flat(FE, 0.4))
    pole(k, 16)
    k.plate(P((-4, 16), (4, 16), (5.4, 21), (6, 27), (-6, 27), (-5.4, 21)), 3.4, "iron")
    for j, (x, h) in enumerate(((-4.6, 34), (-1.6, 37), (1.6, 37.4), (4.6, 34.6))):
        k.plate(L([(x * 0.86, 27), (x * 1.2, h)], 1.3), 2.2, "iron")
        k.plate(P((x * 1.2 - 0.8, h), (x * 1.2 + 0.8, h), (x * 1.3, h + 2.4)), 1.4, "gold")
    k.plate(stroke((5, 23), (10, 25), (11, 30), 1.4, 6), 2.2, "iron")
    links(k, [(-4.4, 19), (-1.6, 18.4), (1.6, 18.4), (4.4, 19)], "gold", 0.8)
    for x, y in ((-10, 33), (10.6, 37), (0, 42)):
        k.plate(disc(x, y, 1.4, 8), 1.4, "hot", glow=True)
        k.plate(P((x - 1.2, y + 0.4), (x + 1.2, y + 0.4), (x + 0.2, y + 3)), 1.0, "hot", glow=True)


@design("apprentice_summon_staff")
def apprentice_summon_staff(k):
    """a first-year's stick with a bent spoon and a bit of string, and a sock with buttons for eyes: it does come when called"""
    k.mat(oak=staves(ramp("#3a2410", "#52341c", "#6e4826", "#8c6034"), 1.0, 0.6), sock=flat(ramp("#6a3a5a", "#8e5478", "#b07498"), 0.7, 0.2, bevel=0.1), btn=flat(ramp("#0e0e12", "#2a2a32"), 0.8), cord=wrap(RAG, RAG[0], 3), wood=flat(IRON, 0.5))
    pole(k, 13, "oak", grip="cord", shoe="oak")
    k.plate(P((-2.2, 13), (2.2, 13), (3, 20), (2, 23), (-2, 23), (-3, 20)), 3.4, "sock")
    k.plate(disc(-1.3, 19.6, 0.7, 6) + disc(1.3, 19.6, 0.7, 6), 3.6, "btn")
    k.plate(rect(-1.4, 16.6, 1.4, 17), 3.6, "btn")
