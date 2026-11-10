"""Hammers: a head on a haft, the hands round the origin, the head between y 11 and 26. Every head is a thing of its own."""
import math

from voxsword import ramp
from weaponsets import design, qb, path, P, L, disc, ring, rect, wave, Mask, flat, fire, heat, staves, steel, honed, bone, gem, at, lit, wrap, stripes, facet_of
from weaponsets_a import BRASS, GOLD, IRON, LEATHER
from weaponsets_c import shard
from weaponsets_d import RUBY, SILVER, links, stroke
from weaponsets_e import CORK, HORN, IVORY, RAG

BRONZE = ramp("#1a1c10", "#2c3018", "#44482a", "#5e6438", "#7c8448", "#a0a860", "#c8c884")
SEABRASS = ramp("#2a2008", "#4a3a10", "#6e581c", "#94782e", "#ba9c44", "#dcc26a")


def haft(k, top, bottom=-13.0, w=2.0, mat="wood", grip="wrap", shoe="dark"):
    """the shaft, its grip and its butt"""
    k.box(0, bottom, 0, w, top - bottom, w, mat, tag="haft")
    k.box(0, -5.6, 0, w + 0.4, 8.0, w + 0.4, grip, tag="grip")
    k.box(0, bottom - 1.2, 0, w + 0.8, 1.6, w + 0.8, shoe)


def block(k, m, d, mat, rim=None, z=0.0, inset=0.5):
    """a heavy head from a shape: a lip of rim, the body standing a little prouder"""
    k.plate(m, d - 0.8, rim or mat, z)
    k.plate(m.inset(inset), d, mat, z)


@design("coopers_mallet")
def coopers_mallet(k):
    """a cooper's driving mallet on the scale of the cask: a barrel of a head, bellied, hooped in iron, a bung in its side"""
    R = k.theme("cellar", base=0.5)
    k.mat(stave=staves(R["wood"], 1.4, 0.6), cork=flat(CORK, 0.56, 0.3))
    haft(k, 13)
    for j in range(13):
        x = -7.2 + j * 1.2
        r_ = 4.0 + 1.6 * math.sin((j + 0.5) / 13 * math.pi)
        k.box(x + 0.6, 16 - r_, 0, 1.25, 2 * r_, 2 * r_, "stave")
    for x in (-5.2, 0, 5.2):
        r_ = 4.0 + 1.6 * math.sin((x + 7.2) / 14.4 * math.pi) + 0.25
        k.box(x, 16 - r_, 0, 1.0, 2 * r_, 2 * r_, "dark")
    for s_ in (1, -1):
        k.box(s_ * 7.5, 12.8, 0, 0.8, 6.4, 6.4, "dark")
    k.box(2.6, 20.8, 0, 2.0, 1.0, 2.0, "cork")


@design("trapdoor_maul")
def trapdoor_maul(k):
    """the trap from under the rope: a slab of black gallows oak swung on its strap hinges, the iron ring you pull still in it"""
    R = k.theme("gallows", base=0.5)
    k.mat(oak=staves(R["wood"], 2.2, 0.54), rope=flat(R["acc"], 0.6))
    haft(k, 13)
    k.plate(rect(-8, 11.5, 8, 22), 3.6, "oak")
    for y in (13.2, 18.8):
        k.plate(P((-9, y), (5.4, y), (6.8, y + 0.8), (5.4, y + 1.6), (-9, y + 1.6)), 4.0, "dark")
        k.plate(disc(-8.6, y + 0.8, 1.3, 8), 4.6, "dark")
        for x in (-5, -1.4, 2.2):
            k.box(x, y + 0.4, 0, 0.8, 0.8, 4.3, "edge")
    k.plate(ring(2.2, 22.6, 2.2, 1.2), 1.0, "dark")
    k.box(2.2, 21.2, 0, 1.2, 1.4, 4.2, "edge")
    k.plate(L([(-1, 11.5), (-0.4, 15), (-1.6, 18.2), (-0.8, 22)], 0.4), 3.66, "glow", glow=True)


@design("burl_maul")
def burl_maul(k):
    """a burl the size of a boar's head, torn from a Rotwood oak with the roots still clutching down the haft; a shelf of fungus has found it"""
    R = k.theme("rotwood", base=0.5)
    k.mat(burl=flat(R["wood"], 0.66, 0.5, bevel=0.14), fungus=flat(R["acc"], 0.6), moss=flat(R["wrap"], 0.6))
    haft(k, 13, grip="moss")
    m = disc(0, 17, 7.2, 12) + disc(-4, 20, 4.2, 9) + disc(4.4, 14, 4.4, 9) + disc(2.4, 21, 4.0, 9)
    block(k, m, 7.4, "burl")
    for x, y in ((-3, 15), (2.8, 19.4), (-0.4, 21)):
        k.plate(disc(x, y, 1.3, 8) - disc(x, y, 0.6, 6), 7.6, "dark")
    for s_ in (1, -1):
        k.plate(stroke((s_ * 1, 11.6), (s_ * 2.6, 7), (s_ * 0.4, 1.0), 1.1), 3.0, "burl")
    k.plate(P((5, 21.6), (10.4, 22.4), (10.8, 21), (5.4, 19.6)) + P((-7, 14), (-10.8, 14.4), (-11.0, 13.2), (-6.4, 12.4)), 6.0, "fungus")
    k.plate(disc(-2.2, 13.0, 1.0, 8), 7.8, "glow", glow=True)


@design("bellmaul")
def bellmaul(k):
    """a passing bell cast thick, hung on its side across the haft: the mouth is the striking face and wax has run all down the crown"""
    R = k.theme("crypt", base=0.5)
    k.mat(bell=flat(BRONZE, 0.6, bevel=0.12), wax=flat(R["acc"], 0.72, bevel=0.1))
    haft(k, 13, w=2.2)
    for j in range(12):
        x = -7.0 + j * 1.3
        r_ = 2.4 + 1.3 * (j / 11) ** 0.5 * 2.6 + (1.0 if j == 11 else 0)
        k.box(x, 16.6 - r_, 0, 1.35, 2 * r_, 2 * r_, "bell")
    k.plate(rect(-8.8, 14.9, -6.6, 18.3), 2.2, "bell")
    k.box(-1.0, 12.6, 0, 1.0, 8.0, 7.6, "dark")
    k.plate(P((-6.8, 19), (-4.8, 19.8), (-2.2, 21.6), (-1.6, 16), (-2.6, 18.6), (-3.8, 15.6), (-4.8, 18.8), (-6.2, 17)), 6.2, "wax")


@design("plague_pestle")
def plague_pestle(k):
    """the Ward's great pestle: one turned piece of pale stone, narrow in the hand and swelling to a round grinding end caked in green paste"""
    R = k.theme("plague", base=0.5)
    stone = ramp("#4a463c", "#6a665a", "#8a8678", "#aaa698", "#c8c4b6", "#e4e0d2")
    k.mat(stone=flat(stone, 0.6, bevel=0.06), brass=flat(R["dark"], 0.6), paste=flat(R["glow"], 0.5, 0.3, bevel=0.1))
    for j in range(16):
        y = 2.0 + j * 1.5
        r_ = 1.1 + (j / 15) ** 2.4 * 5.4
        k.box(0, y, 0, r_ * 2, 1.55, r_ * 2, "stone")
    k.box(0, -13, 0, 2.2, 15.2, 2.2, "stone")
    k.box(0, -5.6, 0, 2.6, 7.6, 2.6, "wrap")
    k.box(0, -14.2, 0, 3.0, 1.6, 3.0, "brass")
    k.box(0, 25.2, 0, 11.0, 1.0, 11.0, "stone")
    k.box(0, 26.2, 0, 8.4, 0.8, 8.4, "stone")
    k.box(0, 21, 0, 13.0, 3.4, 13.0, "paste", glow=True)
    k.box(0, 14.4, 0, 5.8, 1.0, 5.8, "brass")
    for x, y, h in ((-6, 18, 3), (5.8, 17, 4), (1, 19, 2)):
        k.box(x, y, 6.2, 1.0, h, 0.6, "paste", glow=True)


@design("faceless_maul")
def faceless_maul(k):
    """two blank white faces back to back: the head is a single block of temple stone with a mask cut in each end, gold round the brow"""
    R = k.theme("temple", base=0.7)
    k.mat(stone=flat(R["blade"], 0.76, bevel=0.06), gold=flat(R["acc"], 0.62))
    haft(k, 13)
    k.plate(rect(-5.4, 11.6, 5.4, 22), 6.6, "stone")
    for s_ in (1, -1):
        for j, (h, off) in enumerate(((11, 5.4), (9.6, 6.6), (7.6, 7.6), (5.0, 8.3))):
            k.box(s_ * (off + 0.0), 16.8 - h / 2, 0, 1.3, h, 7.6 - j * 1.0, "stone")
        k.box(s_ * 8.8, 17.6, 0, 0.5, 0.5, 1.7, "dark")
        k.box(s_ * 8.8, 15.4, 0, 0.5, 0.4, 0.9, "dark")
    k.box(0, 21.6, 0, 11.4, 1.1, 7.2, "gold")
    k.box(0, 11.4, 0, 11.4, 1.1, 7.2, "gold")
    k.box(0, 15.2, 0, 1.2, 3.6, 7.0, "glow", glow=True)


@design("bonewright_maul")
def bonewright_maul(k):
    """an ox skull boiled white and bound to a brass cog, soul fire in the sockets, the horns sawn down to stubs for striking"""
    R = k.theme("ossuary", base=0.5)
    k.mat(bone=bone(R["acc"], 0.7), brass=flat(R["dark"], 0.62), horn=flat(R["acc"], 0.86, bevel=0.1))
    haft(k, 13)
    for j in range(12):
        a = j * math.pi / 6
        k.box(math.cos(a) * 8.0, 17 + math.sin(a) * 8.0 - 0.9, 0, 1.8, 1.8, 3.0, "brass", rots=(("z", math.degrees(a)),), pivot=(math.cos(a) * 8.0, 17 + math.sin(a) * 8.0, 0))
    k.plate(disc(0, 17, 7.6) - disc(0, 17, 5.8), 2.6, "brass")
    k.plate(P(path((-3.8, 22.8), (3.8, 22.8), (5.4, 19), (3.4, 15.8), (2.2, 11.4), (-2.2, 11.4), (-3.4, 15.8), (-5.4, 19))), 5.0, "bone")
    for s_ in (1, -1):
        k.plate(disc(s_ * 2.2, 18.8, 1.3, 8), 5.2, "glow", glow=True)
        k.plate(P((s_ * 3.4, 22.2), (s_ * 7.6, 22.4), (s_ * 8.6, 19.8), (s_ * 5.2, 20.6)), 2.4, "horn")
        for y in (11.8, 13.2):
            k.box(s_ * 0.8, y, 0, 0.8, 1.0, 5.3, "edge")
    k.plate(P((-0.8, 15.8), (0.8, 15.8), (0, 13.6)), 5.1, "dark")


@design("kiln_maul")
def kiln_maul(k):
    """the Foundry's own anvil, on a stick: horn out front, heel behind, the face still glowing from the last strike"""
    R = k.theme("foundry", base=0.46)
    k.mat(iron=flat(ramp("#14120f", "#221f1b", "#332f2a", "#46403a", "#5e564e", "#7a7065", "#9a9084"), 0.7, bevel=0.14), hot=fire(R["glow"], 0.45, 0.5))
    haft(k, 13, w=2.4)
    anvil = P((-9.6, 22), (9.0, 22), (9.4, 20), (4.6, 18.4), (3.2, 15.4), (5.0, 12), (-5.0, 12), (-3.2, 15.4), (-4.6, 18.4), (-6.0, 19), qb((-8.0, 19.0), (-11.0, 19.6), (-12.6, 21.6), 6))
    block(k, anvil, 6.0, "iron")
    k.plate(rect(-5.4, 22, 9.0, 22.6), 5.4, "hot", glow=True)
    k.box(4.6, 19.6, 0, 1.0, 2.3, 6.2, "dark")
    k.box(0, 13.6, 0, 8.0, 0.6, 6.2, "hot", glow=True)


@design("glacier_maul")
def glacier_maul(k):
    """a block of the old glacier chopped out whole, iron straps round it, and something dark and man-shaped frozen in the middle"""
    R = k.theme("frost", base=0.5)
    k.mat(ice=flat(R["glow"], 0.64, bevel=0.14), white=flat(R["glow"], 0.92, bevel=0.04), iron=flat(R["dark"], 0.6))
    haft(k, 13)
    m = P((-8.4, 12), (8.0, 11.6), (9.6, 16), (8.6, 22), (5.4, 24.6), (-3.4, 25.4), (-8.8, 22.6), (-10, 17))
    k.plate(m, 6.6, "ice")
    k.plate(m.inset(1.0), 7.0, "ice")
    k.plate(P((-1.6, 14), (-0.4, 14), (-0.2, 16), (0.6, 14), (1.8, 14), (1, 18), (2.8, 19.4), (1.4, 21), (0.4, 22.8), (-0.8, 22.8), (-1, 21), (-2.8, 19), (-1, 18)), 7.06, "dark")
    for pts in (((-7, 21), (-2, 24)), ((4, 13), (7.6, 18))):
        k.plate(L(list(pts), 1.0), 7.04, "white")
    for x in (-5.6, 5.4):
        k.box(x, 11, 0, 1.3, 15, 7.6, "iron")
    for x, y, ln, a, w in ((-3, 25, 5, 10, 2), (3, 24.6, 6.6, -14, 2.2), (9, 21, 4, -60, 1.8), (-9, 20, 4.6, 60, 1.8)):
        k.plate(shard(x, y, ln, a, w), 2.6, "ice")


@design("bookbinders_maul")
def bookbinders_maul(k):
    """the Archive's heaviest volume, clasped shut, brass at every corner, a silk ribbon hanging out of it and its spine toward the enemy"""
    R = k.theme("silk", base=0.5)
    cover = ramp("#1a0408", "#2e0a10", "#4a1018", "#661a22", "#842a30")
    k.mat(cover=flat(cover, 0.56, bevel=0.1), pages=stripes(ramp("#a89e84", "#c4bba0", "#dad2b8", "#ece6d0"), ramp("#7a7058", "#948a70", "#ada388", "#c4bba0"), 0.5, 0.0, 0.5), brass=flat(BRASS, 0.66), silk=flat(R["acc"], 0.9, bevel=0.04), ribbon=flat(R["glow"], 0.6, bevel=0.1))
    haft(k, 13)
    k.plate(rect(-8.6, 12, 8.6, 23), 7.6, "pages")
    for z in (3.4, -3.4):
        k.plate(rect(-9, 11.5, 9, 23.5), 1.0, "cover", z=z)
    k.plate(rect(-9, 11.5, -7.6, 23.5), 7.6, "cover")
    for x in (-8.2, 7.4):
        for y in (11.2, 21.8):
            k.box(x, y, 0, 2.4, 2.0, 8.1, "brass")
    k.box(8.6, 16, 0, 1.6, 2.2, 8.1, "brass")
    for y in (14, 16.6, 19.6):
        k.box(-8.6, y, 0, 0.8, 0.8, 7.8, "brass")
    k.plate(disc(0, 17.5, 2.6, 8), 8.4, "ribbon")
    k.plate(wave(lambda t: 4 + 3 * t + 0.7 * math.sin(t * 7), lambda t: 0.8, 11.6, 3.6, 10), 0.6, "ribbon", z=1.2)


@design("ore_hammer")
def ore_hammer(k):
    """a sledge whose head never left the rock: a raw lump of ore on a steel core, one bright vein through it, the haft a pit prop"""
    R = k.theme("weeping_mine", base=0.5)
    k.mat(rock=flat(R["blade"], 0.42, 0.3, bevel=0.16), copper=flat(R["acc"], 0.58), crystal=flat(R["glow"], 0.7, bevel=0.14))
    haft(k, 13)
    m = P((-8, 12), (-3, 11), (6, 11.6), (9, 15), (8, 20), (3.6, 22.6), (-4, 22), (-9, 18))
    block(k, m, 6.8, "rock")
    k.inlay(L([(-7, 15), (-2, 17), (0, 15), (4, 18), (7.6, 17)], 0.7), 6.8, "glow", glow=True)
    k.plate(rect(-1.4, 10.8, 1.4, 23), 7.2, "copper")
    k.plate(shard(3, 21, 5.4, -20, 2.4), 2.4, "crystal")


@design("motherlode")
def motherlode(k):
    """the geode the Mine has been weeping round: a boulder split open, black crust outside and a burning teal cave of crystal in, held on the haft by a copper claw"""
    R = k.theme("weeping_mine", base=0.5)
    k.mat(rock=flat(R["blade"], 0.34, 0.3, bevel=0.14), copper=flat(R["acc"], 0.6), crystal=flat(R["glow"], 0.74, bevel=0.14))
    haft(k, 12)
    outer = disc(0, 19, 9.8, 12) + disc(-5, 16, 6, 9)
    cave = disc(0.6, 19.4, 7.0, 12)
    k.plate(outer - cave, 8.0, "rock")
    k.plate(cave, 3.0, "dark")
    for x, y, ln, a, w in ((0, 13, 10, 0, 3), (-4, 14, 8, 28, 2.6), (4.4, 14, 8, -28, 2.6), (-5.6, 19, 6, 70, 2.2), (6.4, 20, 5.4, -80, 2.0), (1, 25, 4, 170, 2.4)):
        k.plate(shard(x, y, ln, a, w) & cave, 6.6, "crystal")
        k.plate(shard(x, y + 0.6, ln * 0.7, a, w * 0.4) & cave, 7.0, "glow", glow=True)
    for s_ in (1, -1):
        k.plate(stroke((s_ * 0.8, 11), (s_ * 8, 10), (s_ * 9.6, 18), 1.4), 8.4, "copper")
    k.box(0, 10, 0, 3.6, 2.4, 3.6, "copper")


@design("anchor_maul")
def anchor_maul(k):
    """the drowned ship's kedge anchor: its shank is the haft, its stock crosses below the head, its flukes curl wide and it has been down a long time"""
    R = k.theme("tide_chapel", base=0.5)
    k.mat(iron=flat(R["blade"], 0.5, bevel=0.14), crust=flat(R["acc"], 0.72, bevel=0.1), rope=wrap(R["dark"], R["dark"][0], 4))
    k.box(0, -13, 0, 2.4, 37, 2.4, "iron")
    k.box(0, -5.6, 0, 2.8, 8, 2.8, "rope")
    k.plate(ring(0, 25.4, 2.4, 1.2), 1.2, "iron")
    k.box(0, 20.6, 0, 11.6, 1.4, 1.8, "wood")
    for x in (-5.8, 5.8):
        k.box(x, 20.4, 0, 1.6, 1.8, 2.2, "iron")
    # the crown comes up from the butt, the flukes up each side of the fist
    for s_ in (1, -1):
        arm = P(path((0, 13.6), qb((s_ * 9, 11.4), (s_ * 11, 15.4), (s_ * 13.0, 19.6), 8), (s_ * 13.0, 19.6), (s_ * 9.8, 18.2), (s_ * 7.6, 20.4), qb((s_ * 7.6, 15.6), (s_ * 5, 15.0), (0, 16.4), 8)))
        block(k, arm, 2.8, "iron")
    for x, y, r_ in ((-8, 15, 1), (-4.6, 14.4, 0.8), (7.2, 15.6, 1.1), (3.8, 15, 0.7)):
        k.plate(disc(x, y, r_, 8) - disc(x, y, 0.3, 6), 3.2, "crust")


@design("toll_of_the_deep")
def toll_of_the_deep(k):
    """the bell they rang for ships that didn't come back, hauled up from the bottom, barnacled, chained to the haft, its pearl tongue glowing out of the mouth"""
    R = k.theme("tide_chapel", base=0.5)
    k.mat(bell=flat(BRONZE, 0.56, bevel=0.12), crust=flat(R["acc"], 0.74, bevel=0.1), chain=flat(R["blade"], 0.66), pearl=fire(R["glow"], 0.5, 0.5), kelp=flat(R["wrap"], 0.56))
    haft(k, 11, w=2.2)
    for j, (w, h) in enumerate(((4.4, 2.4), (5.6, 2.2), (6.8, 2.2), (8.0, 2.4), (9.8, 2.2), (12, 1.6), (14.4, 1.4))):
        y = 28 - sum((2.4, 2.2, 2.2, 2.4, 2.2, 1.6, 1.4)[:j + 1])
        k.box(0, y, 0, w, h + 0.02, w * 0.9, "bell")
    k.box(0, 28, 0, 3.0, 1.6, 3.0, "bell")
    k.plate(ring(0, 30.4, 1.8, 0.9), 1.4, "bell")
    k.box(0, 21.8, 0, 8.6, 0.8, 7.9, "dark")
    k.box(0, 11, 0, 1.0, 3, 1.0, "chain")
    k.plate(disc(0, 12.6, 1.8, 10), 3.0, "pearl", glow=True)
    for x, y, r_ in ((-4.6, 16.4, 1.2), (-2.0, 19.4, 1.0), (4.4, 18, 1.1), (2.4, 24, 0.9), (-1.2, 24.8, 0.8), (5.6, 15.0, 0.7)):
        k.plate(disc(x, y, r_, 8) - disc(x, y, 0.35, 6), 9.0 if abs(x) < 3 else 7.0, "crust")
    links(k, [(-6.4, 15), (-5.6, 11.6), (-3.2, 9.2), (-1.0, 7.6)], "chain")
    links(k, [(6.4, 15), (5.6, 11.6), (3.2, 9.2), (1.0, 7.6)], "chain")
    k.plate(wave(lambda t: 7.4 + 1.6 * math.sin(t * 7), lambda t: 0.7, 15, 5, 12), 0.6, "kelp")


@design("gorge_club")
def gorge_club(k):
    """a wagon's hub on a spoke, horseshoe nails driven through it every way, a red rag and a tooth or two left in"""
    R = k.theme("brigands_gorge", base=0.5)
    k.mat(hub=staves(R["wood"], 1.6, 0.6), nail=flat(IRON, 0.8), rag=flat(R["wrap"], 0.64), tooth=flat(IVORY, 0.8))
    haft(k, 13)
    k.box(0, 11.6, 0, 10, 13, 10, "hub")
    for y in (12.6, 21.8):
        k.box(0, y, 0, 11, 1.4, 11, "dark")
    for x, y, a in ((-5, 15, 90), (-5, 20, 110), (5, 15.5, -90), (5, 20, -70), (-2, 24.6, 20), (2.4, 24.6, -20), (0, 24.6, 0)):
        r = math.radians(a)
        k.seg((x, y), (x - math.sin(r) * 3.2, y + math.cos(r) * 3.2), 0.9, 0.9, "nail")
    k.box(5.6, 17, 0, 1.0, 1.0, 12, "nail")
    k.plate(P((-5.4, 12), (-5.4, 3.4), (-7.4, 5), (-9.0, 2.4), (-9.6, 9), (-8.0, 12.4)), 0.8, "rag", z=0)
    k.box(0.5, 18, 5.2, 1.0, 1.6, 0.8, "tooth")


@design("beak_hammer")
def beak_hammer(k):
    """a war hammer that remembers it was a bird: a black raven's beak for the pick, a skull's dome for the face, a fan of pinions lashed where the head meets the haft"""
    R = k.theme("rookery", base=0.46, edge=0.72)
    k.mat(beak=steel(HORN, 0.6, 0.14), bone=bone(R["acc"], 0.72), feather=flat(R["blade"], 0.42, bevel=0.14))
    haft(k, 17)
    k.plate(P(path((1, 13), (1, 21), qb((6, 22), (12, 21), (15.4, 11.6), 10), (15.4, 11.6), qb((10, 15.4), (6, 15), (1, 13), 8))), 3.0, "beak")
    k.plate(disc(-2.4, 17, 4.6, 12), 5.4, "bone")
    k.plate(disc(-2.6, 18.4, 1.4, 8), 5.6, "dark")
    k.plate(rect(-8, 15, -6, 19), 4.4, "bone")
    for a, ln in ((20, 11), (0, 12), (-20, 11), (40, 8), (-40, 8)):
        r = math.radians(a + 180)
        d = (-math.sin(r), math.cos(r))
        o = (0, 12)
        t_ = (d[1], -d[0])
        k.plate(P(o, (o[0] + d[0] * ln * 0.6 + t_[0], o[1] + d[1] * ln * 0.6 + t_[1]), (o[0] + d[0] * ln, o[1] + d[1] * ln), (o[0] + d[0] * ln * 0.6 - t_[0], o[1] + d[1] * ln * 0.6 - t_[1])), 0.8, "feather")
    k.box(0, 11, 0, 3.4, 2.2, 3.4, "dark")


@design("strongman_mallet")
def strongman_mallet(k):
    """the mallet from the ring-the-bell tent: enormous, striped, a brass band and a star; the head is mostly hollow and it hits like a falling piano"""
    k.theme("hollow_circus", base=0.6)
    red = ramp("#2a0408", "#4e0810", "#7a1018", "#a81c20", "#d0302a", "#ee5a44")
    cream = ramp("#6a5a44", "#8e7c60", "#b4a282", "#d6c8a8", "#efe4c8", "#fff8e8")
    def barrel(p, n, b, key, i, j, w, h, fr):
        return at(red if int(math.floor((p[0] + 20) / 2.6)) % 2 else cream, 0.62 + lit(key, i, j, w, h))
    k.mat(barrel=barrel, gold=flat(GOLD, 0.66), pole=stripes(red, cream, 3.0, 0.5), wrap=wrap(cream, red[3], 3))
    haft(k, 13, mat="pole", shoe="gold")
    k.box(0, 11.6, 0, 19, 11, 9, "barrel")
    for s_ in (1, -1):
        k.box(s_ * 9.8, 12.6, 0, 1.0, 9, 7, "gold")
        k.box(s_ * 10.6, 13.6, 0, 0.8, 7, 5, "barrel")
    k.plate(rect(-9.6, 16.4, 9.6, 17.4), 9.2, "gold")
    star = P(*[(math.cos(a * math.pi / 5 + math.pi / 2) * (2.6 if a % 2 == 0 else 1.1), 17 + math.sin(a * math.pi / 5 + math.pi / 2) * (2.6 if a % 2 == 0 else 1.1)) for a in range(10)])
    k.plate(star, 9.5, "gold")


@design("bog_oak_maul")
def bog_oak_maul(k):
    """a thousand years in the mire turned this oak to black stone: a stump of it on its own root, lilies grown on top, a reed lash round the neck"""
    R = k.theme("mirefen_coven", base=0.5)
    k.mat(oak=staves(ramp("#14100c", "#201a12", "#2e261a", "#3e3424", "#52462f", "#6a5a3c"), 1.6, 0.66), lily=flat(R["wrap"], 0.6), bloom=flat(ramp("#d8a0c0", "#f0c8dc", "#fff0f6"), 0.5), reed=wrap(ramp("#3a3414", "#5a5220", "#7c7230", "#a09844"), None, 3))
    haft(k, 13, mat="oak", grip="reed")
    k.plate(P((-6.6, 11.6), (6.6, 11.6), (7.6, 14), (6.8, 21.6), (-6.8, 21.6), (-7.6, 14)), 8.0, "oak")
    k.plate(rect(-5.2, 21.6, 5.2, 22.2), 6.4, "dark")
    for s_ in (1, -1):
        k.plate(stroke((s_ * 5.6, 12.6), (s_ * 9.6, 11), (s_ * 8.6, 6.6), 1.4), 3.0, "oak")
    k.box(-2, 22, 0, 6.4, 0.5, 6.4, "lily")
    k.plate(P((1.6, 22.2), (3.2, 24), (2.2, 23.6), (2.4, 25.4), (1.2, 24), (0.2, 25.2), (0.4, 23.4), (-0.6, 24), (0.8, 22.2)), 1.4, "bloom", z=1)
    k.box(0, 12.2, 0, 15.8, 1.1, 8.4, "reed")
    k.plate(disc(-3, 17, 1.6, 8) - disc(-3, 17, 0.8, 6), 8.1, "dark")


@design("drowning_pool")
def drowning_pool(k):
    """the coven's cauldron on a pole: squat black iron, three stub legs for spikes, the bog water in it glowing and slopping over the rim and not spilling"""
    R = k.theme("mirefen_coven", base=0.5)
    k.mat(pot=flat(IRON, 0.7, bevel=0.12), hot=flat(R["glow"], 0.56, bevel=0.14), bone=flat(R["acc"], 0.72))
    haft(k, 11, w=2.2)
    pot = P(path((-6, 25), (6, 25), qb((9.4, 21), (9.2, 15), (5.6, 12.4), 8), (5.6, 12.4), (-5.6, 12.4), qb((-9.2, 15), (-9.4, 21), (-6, 25), 8)))
    k.plate(pot, 8.4, "pot")
    k.plate(P((-7.2, 25), (7.2, 25), (7.8, 26.4), (-7.8, 26.4)), 10.0, "pot")
    k.box(0, 26.2, 0, 13.4, 1.2, 8.6, "hot", glow=True)
    for x, y, h in ((-6, 22, 5), (5, 21, 6.4), (0.6, 23.6, 3.4)):
        k.box(x, y, 4.8, 1.0, h, 0.6, "hot", glow=True)
    k.plate(disc(-2, 28, 1.3, 8) + disc(2.4, 27.8, 0.9, 6), 2.0, "hot", glow=True)
    for x in (-5, 5):
        k.plate(P((x - 1.4, 12.4), (x + 1.4, 12.4), (x * 1.3, 7.4)), 3.0, "pot")
    for s_ in (1, -1):
        k.plate(ring(s_ * 9.2, 22, 2.0, 1.1), 1.2, "pot")
    k.plate(disc(0, 18, 2.6, 8) - disc(0, 18, 1.5, 6), 8.6, "bone")


@design("obelisk_maul")
def obelisk_maul(k):
    """the tip off a fallen obelisk, sawn free and socketed lengthwise: gold cap, hieroglyphs down the granite, sand still in the cuts"""
    k.theme("sandsunk_tomb", base=0.5)
    stone = ramp("#3a1e18", "#5a3024", "#7c4632", "#a06244", "#c08460", "#dcaa84")
    lapis = ramp("#081a4a", "#0e2a6e", "#163e96", "#2458c0", "#4a84e0")
    k.mat(stone=flat(stone, 0.56, bevel=0.1), gold=flat(GOLD, 0.68), lapis=flat(lapis, 0.56))
    haft(k, 12, mat="lapis", grip="gold")
    k.plate(P((-4.4, 10), (4.4, 10), (3.2, 26), (-3.2, 26)), 6.4, "stone")
    k.plate(P((-3.4, 25), (3.4, 25), (0, 30.6)), 5.4, "gold")
    k.box(0, 9.4, 0, 9.6, 1.4, 7.4, "gold")
    glyph = rect(-1.6, 12, 1.6, 12.6) + disc(0, 14.6, 1.2, 8) - disc(0, 14.6, 0.6, 6) + P((-1.4, 17), (1.4, 17), (0, 19.2)) + rect(-1.0, 20.2, 1.0, 20.8) + rect(-0.3, 20.2, 0.3, 23.0) + rect(-1.2, 22.6, 1.2, 23.2)
    k.plate(glyph, 6.46, "lapis")


@design("sun_kings_flail")
def sun_kings_flail(k):
    """a true flail: a gold haft, two arm-lengths of chain with a little lazy curve in it, and on the end the Sun King's head, a burning sphere of rays"""
    k.theme("sandsunk_tomb", base=0.5)
    sun = ramp("#e07010", "#ffa81c", "#ffd84a", "#fff4a8", "#ffffff")
    lapis = ramp("#081a4a", "#0e2a6e", "#163e96", "#2458c0", "#4a84e0")
    k.mat(sun=fire(sun, 0.3, 0.7), gold=flat(GOLD, 0.68, bevel=0.14), lapis=flat(lapis, 0.56), wrap=wrap(lapis, GOLD[3], 4), chain=flat(GOLD, 0.56, bevel=0.2))
    haft(k, 9, mat="gold", shoe="lapis")
    k.box(0, 8.6, 0, 3.2, 2.2, 3.2, "lapis")
    k.plate(ring(0, 11.8, 1.3, 0.6), 1.0, "gold")
    links(k, [(0, 12.8), (0.6, 15.4), (2.2, 17.6), (4.4, 19.2), (6.6, 20.6), (8.2, 22.2)], "chain")
    k.plate(disc(9.8, 25, 3.8, 14), 7.2, "gold")
    k.plate(disc(9.8, 25, 3.0, 12), 7.6, "sun", glow=True)
    for j in range(12):
        a = 2 * math.pi * j / 12 + 0.2
        ln = 7.6 if j % 2 else 6.0
        k.plate(P((9.8 + math.cos(a - 0.3) * 3.4, 25 + math.sin(a - 0.3) * 3.4), (9.8 + math.cos(a) * ln, 25 + math.sin(a) * ln), (9.8 + math.cos(a + 0.3) * 3.4, 25 + math.sin(a + 0.3) * 3.4)), 1.8, "gold")


@design("knuckle")
def knuckle(k):
    """a single knuckle of the Titan's hand, two great rounded condyles of bone, a torn stump of tendon lashed down the sawn femur that hafts it"""
    k.theme("fallen_titan", base=0.5)
    meat = ramp("#2a0608", "#4a0c10", "#6e161a", "#942428", "#b83c3a", "#d8625a")
    k.mat(bone=bone(IVORY, 0.72), edgeb=flat(IVORY, 0.88, bevel=0.06), meat=flat(meat, 0.5, 0.3), wrap=wrap(meat, meat[0], 4), shaft=bone(IVORY, 0.54))
    haft(k, 12, w=2.6, mat="shaft", shoe="meat")
    m = disc(-5, 19, 7) + disc(5, 19, 7) + P((-4, 11), (4, 11), (7, 16), (-7, 16))
    block(k, m, 8.0, "bone", "edgeb")
    k.plate(L([(0, 12), (0, 26)], 1.0), 8.04, "shaft")
    k.plate(disc(-5, 21, 2.6, 8) - disc(-5, 21, 1.6, 6), 8.1, "edgeb")
    k.plate(P((-5.6, 12), (5.6, 12), (5, 9), (3, 11), (1, 7), (-1.4, 10.6), (-4, 6.6), (-4.6, 10)), 4.0, "meat")


@design("systole")
def systole(k):
    """the Titan's heart, still contracting: a dense fist of muscle, arteries standing off it, its chambers glowing with every beat, carried on a great vessel"""
    meat = ramp("#2a0608", "#4a0c10", "#6e161a", "#942428", "#b83c3a", "#d8625a", "#f09a8a")
    fat = ramp("#a07c34", "#d0ae56", "#ecd488", "#faeec4")
    hot = ramp("#a01018", "#e02830", "#ff6a5a", "#ffc0a8", "#ffe8e0")

    def muscle(p, n, b, key, i, j, w, h, fr):
        return at(meat, 0.5 + lit(key, i, j, w, h) + 0.12 * math.sin(p[0] * 1.6 + p[1] * 0.9))

    k.mat(heart=muscle, edge=flat(meat, 0.2), fat=flat(fat, 0.6, 0.3), hot=fire(hot, 0.3, 0.7), vessel=flat(meat, 0.42), wrap=wrap(meat, meat[0], 4), dark=flat(meat, 0.1), wood=flat(meat, 0.4))
    haft(k, 12, w=2.4)
    m = disc(-3, 21, 6.4) + disc(3.4, 20.4, 6.6) + P((-8.4, 20), (9.0, 19), (0.4, 8.6))
    k.plate(m, 6.8, "edge")
    k.plate(m.inset(0.5), 8.2, "heart")
    k.plate(L(qb((-1, 26), (1.4, 19), (-0.4, 12), 8) + [(-0.4, 12)], 1.0), 8.3, "fat")
    k.inlay(disc(-3.4, 20, 2.0, 8) + disc(4, 19, 2.2, 8), 8.2, "hot", glow=True)
    for a, c, b, w in (((-4, 26), (-5, 30), (-8.4, 31.6), 2.4), ((1, 26), (1, 30), (2.4, 33), 2.0), ((5, 25), (8, 28), (7, 31), 1.6)):
        k.plate(stroke(a, c, b, w), 3.4, "vessel")
        k.plate(disc(b[0], b[1], w * 0.6, 8), 3.6, "hot", glow=True)


@design("prayer_hammer")
def prayer_hammer(k):
    """a prayer wheel gone to war: a bronze drum on a spindle, the sutras raised on it, a strand of big jade beads hanging"""
    R = k.theme("jade_monastery", base=0.54)
    k.mat(drum=flat(GOLD, 0.5, bevel=0.14), raised=flat(GOLD, 0.8, bevel=0.04), jade=flat(R["blade"], 0.66, bevel=0.2), red=flat(ramp("#3a0608", "#600c0e", "#8a1416", "#b42020", "#dc3a30"), 0.56))
    haft(k, 26, mat="red", grip="wrap", shoe="drum")
    k.plate(rect(-6.4, 12, 6.4, 22), 10.0, "drum")
    for y in (11.2, 21.4):
        k.plate(rect(-7.4, y, 7.4, y + 1.2), 11.4, "raised")
    for x in (-4.6, -2.3, 0, 2.3, 4.6):
        for y in (13.6, 16.4, 18.8):
            k.box(x, y, 0, 1.3, 0.5 + (x + y) % 1.2, 10.3, "raised")
    k.plate(P((-1.4, 26), (1.4, 26), (0, 30)), 2.4, "raised")
    for j in range(7):
        k.plate(disc(7.8 + math.sin(j * 0.6) * 0.5, 17 - j * 1.9, 1.05, 8), 2.2, "jade")
    k.box(7.7, 20, 0, 0.5, 1.4, 0.5, "red")


@design("thunder_maul")
def thunder_maul(k):
    """a storm engine's hammer: two iron drums on a yoke with copper coil between, arcs jumping to the faces"""
    R = k.theme("storm_bastion", base=0.5)
    k.mat(iron=flat(R["dark"], 0.56, bevel=0.14), coil=wrap(ramp("#3a1a08", "#6a3414", "#9c5a24", "#c8843c"), None, 2), white=flat(R["glow"], 0.92, bevel=0.02))
    haft(k, 13)
    for s_ in (1, -1):
        k.box(s_ * 6.4, 12, 0, 4.6, 10, 8, "iron")
        k.box(s_ * 9.2, 13, 0, 1.2, 8, 6, "iron")
        k.box(s_ * 10.1, 14.4, 0, 0.6, 5.2, 3.6, "white", glow=True)
    k.box(0, 13.6, 0, 8.4, 6.8, 6.4, "coil")
    k.box(0, 21.4, 0, 13.0, 1.2, 3.0, "iron")
    k.plate(L([(-6, 23), (-3, 25.4), (-1, 23.4), (1.6, 26), (4, 23.8), (6, 25)], 0.5), 0.6, "white", glow=True)


@design("skybreaker")
def skybreaker(k):
    """the Bastion's last word: a vast double-faced hammer with wings of riveted storm-iron swept back off it, lightning chained along the haft and caged in the eye"""
    R = k.theme("storm_bastion", base=0.5)
    k.mat(iron=flat(R["dark"], 0.6, bevel=0.14), steel_=flat(R["blade"], 0.6, bevel=0.14), white=flat(R["glow"], 0.92, bevel=0.02), hot=fire(R["glow"], 0.35, 0.65))
    haft(k, 15, mat="iron")
    m = P((-11, 12), (11, 12), (12.4, 14), (12.4, 21), (11, 23), (-11, 23), (-12.4, 21), (-12.4, 14))
    block(k, m, 8.0, "steel_", "iron", inset=1.0)
    k.plate(rect(-3, 11.4, 3, 23.6), 8.8, "iron")
    k.plate(rect(-1.8, 13, 1.8, 22), 9.0, "hot", glow=True)
    k.plate(L([(0, 13.4), (-1.0, 16.4), (0.8, 18), (-0.4, 21.6)], 0.5), 9.1, "white", glow=True)
    for s_ in (1, -1):
        for j, (ln, up) in enumerate(((11, 12.6), (9, 9.4), (7, 6.4))):
            k.plate(P((s_ * 3, 22.6 - j * 0.2), (s_ * (3 + ln), 22.6 + up), (s_ * (4 + ln * 0.5), 22.6 + up * 0.3), (s_ * 8, 22.6 - j * 0.2)), 1.4, "iron")
    k.plate(L([(1.2, -4), (-0.8, -1), (1, 2), (-0.8, 6), (0.8, 10)], 0.5), 2.6, "white", glow=True)


@design("gilded_mace")
def gilded_mace(k):
    """a court mace: six gilded flanges in a tulip, a blood garnet at the crown and the lacquered shaft of something you wouldn't want to touch"""
    R = k.theme("bloodmoon_court", base=0.5)
    k.mat(gold=flat(GOLD, 0.66, bevel=0.14), gem=gem(RUBY), lacquer=flat(ramp("#14040a", "#280a12", "#42101c", "#5e1a28"), 0.5))
    haft(k, 15, mat="lacquer", shoe="gold")
    k.box(0, 13.4, 0, 3.6, 12, 3.6, "gold")
    for a in (0, 60, 120):
        for s_ in (1, -1):
            fl = P(path((s_ * 1.4, 14), qb((s_ * 8, 15), (s_ * 8.4, 21), (s_ * 2.4, 27), 8), (s_ * 2.4, 27), (s_ * 1.4, 25)))
            for r_ in fl.rows():
                b = k.s.add(((r_[0] / 2, r_[2] / 2, -0.6), ((r_[1] - r_[0]) / 2, (r_[3] - r_[2]) / 2, 1.2)), "gold", rots=(("y", a),), pivot=(0, 0, 0))
    k.plate(disc(0, 28, 1.9, 8), 3.0, "gem")
    k.box(0, 24.6, 0, 3.0, 1.6, 3.0, "gold")


@design("basalt_maul")
def basalt_maul(k):
    """the Labyrinth's own stone: a bundle of hexagon columns snapped at different heights, each with its cold violet join"""
    R = k.theme("obsidian_labyrinth", base=0.5)
    k.mat(stone=flat(ramp("#0e0c12", "#1a1720", "#282430", "#383242", "#4c4458", "#665c74", "#887c98"), 0.72, bevel=0.16), top=flat(ramp("#3e3848", "#585062", "#7a7088"), 0.6))
    haft(k, 13, w=2.2)
    for x, z, h, w in ((0, 0, 15, 5), (-4.6, 0, 12.4, 4.6), (4.6, 0, 13.6, 4.6), (-2.4, 3.6, 11, 4.4), (2.4, 3.6, 12, 4.4), (-2.4, -3.6, 13.4, 4.4), (2.4, -3.6, 10.4, 4.4)):
        k.box(x, 11, z, w, h, w, "stone")
        k.box(x, 11 + h - 0.1, z, w - 1, 0.3, w - 1, "top")
        k.box(x, 11 + h * 0.5, z, w + 0.1, 0.4, w + 0.1, "glow", glow=True)


@design("foghorn_hammer")
def foghorn_hammer(k):
    """the lighthouse's foghorn off its mount: a brass trumpet flaring wide to one side, the bellows chamber behind for the heavy end. Hit something with it and the sea answers"""
    R = k.theme("abyssal_lighthouse", base=0.5)
    k.mat(brass=flat(SEABRASS, 0.6, bevel=0.12), iron=flat(IRON, 0.6), rub=flat(R["wrap"], 0.56), hot=flat(R["glow"], 0.42, bevel=0.1))
    haft(k, 13)
    for j in range(12):
        x = -2.0 + j * 1.25
        r_ = 2.3 + (j / 11) ** 3 * 6.4
        k.box(x, 17 - r_, 0, 1.3, 2 * r_, 2 * r_, "brass")
    k.box(13.0, 8.8, 0, 0.5, 16.4, 16.4, "hot", glow=True)
    k.box(13.3, 11, 0, 0.5, 12, 12, "dark")
    k.box(-4.8, 12.4, 0, 6.0, 9.2, 8.4, "iron")
    for x in (-7.6, -4.8, -2.0):
        k.box(x, 12, 0, 0.8, 10, 9, "brass")
    k.box(-8.4, 14.4, 0, 1.2, 5.2, 5.2, "iron")


@design("censer_maul")
def censer_maul(k):
    """the Cathedral's thurible on its chains, no bigger than a head and twice as heavy: pierced gold, black smoke, a coal of the dead sun inside"""
    R = k.theme("eclipse_cathedral", base=0.5)
    k.mat(gold=flat(GOLD, 0.6, bevel=0.14), iron=flat(IRON, 0.7), hot=fire(ramp("#ffb040", "#ffe8a0", "#fffbe0", "#ffffff"), 0.4, 0.6), smoke=flat(ramp("#0a0a0e", "#16161c", "#24242c"), 0.5))
    haft(k, 15, mat="iron")
    k.box(0, 14.4, 0, 8.0, 1.6, 2.6, "gold")
    links(k, [(-3.2, 14.6), (-4.8, 12.8), (-5.6, 10.0)], "gold")
    links(k, [(3.2, 14.6), (4.8, 12.8), (5.6, 10.0)], "gold")
    links(k, [(0, 16), (0, 18.2)], "gold")
    k.plate(ring(0, 19, 1.0, 0.5), 0.8, "gold")
    for j, (w, h) in enumerate(((5.6, 2), (8.8, 2), (10.8, 3), (10.8, 3), (8.8, 2), (5.6, 2))):
        y = 20 + sum((2, 2, 3, 3, 2, 2)[:j])
        k.box(0, y, 0, w, h, w, "gold")
    for x in (-3.4, 0, 3.4):
        for z in (5.5, -5.5):
            k.box(x, 24, z, 1.4, 4.0, 0.3, "hot", glow=True)
    k.box(0, 32, 0, 2.0, 1.8, 2.0, "gold")
    k.plate(P((-3.6, 26), (-8.6, 30), (-7, 25.4)) + P((3.6, 28), (8.2, 33.4), (7, 27.6)), 2.0, "smoke")


@design("hoard_hammer")
def hoard_hammer(k):
    """a dragon's small change: gold ingots stacked and strapped into a sledge, a crown nailed to one end, coins falling off it"""
    k.theme("wyrms_hoard", base=0.6)
    k.mat(gold=flat(GOLD, 0.66, bevel=0.16), dgold=flat(GOLD, 0.46, bevel=0.14), strap=flat(IRON, 0.62), coin=flat(GOLD, 0.8, bevel=0.1), gem=gem(RUBY))
    haft(k, 13, mat="strap", shoe="gold")
    for r_, (y, xs, mat) in enumerate(((12.0, (-6.6, 0, 6.6), "gold"), (15.0, (-3.3, 3.3), "dgold"), (18.0, (-6.6, 0, 6.6), "gold"))):
        for x in xs:
            k.plate(P((x - 3.2, y), (x + 3.2, y), (x + 2.6, y + 3), (x - 2.6, y + 3)), 7.0, mat)
    for x in (-8.8, 8.8):
        k.box(x * 0.6, 11.4, 0, 1.2, 10.4, 7.6, "strap")
    k.plate(P((-4, 21), (4, 21), (4.8, 24.4), (2.4, 22.8), (0, 25.4), (-2.4, 22.8), (-4.8, 24.4)), 3.0, "coin")
    k.plate(disc(0, 22, 0.8, 8), 3.3, "gem")
    for x, y in ((11, 12), (-11.4, 13.6), (12, 8)):
        k.plate(disc(x, y, 1.1, 8), 0.5, "coin")
        k.seg((x * 0.8, y + 1), (x, y), 0.3, 0.3, "strap")


@design("hoardbreaker")
def hoardbreaker(k):
    """the treasure chest itself, iron-bound and bursting: the lid strains on the gold inside, a ruby lock holds, and everything it hits gets a share"""
    k.theme("wyrms_hoard", base=0.6)
    k.mat(chest=staves(ramp("#2a0e06", "#42180c", "#5e2412", "#7c321a", "#9c4424"), 2.6, 0.56), band=flat(IRON, 0.7, bevel=0.14), gold=flat(GOLD, 0.72, bevel=0.16), coin=flat(GOLD, 0.84, bevel=0.1), gem=gem(RUBY))
    haft(k, 12, w=2.4, mat="band", shoe="gold")
    k.plate(rect(-10, 11, 10, 19), 10, "chest")
    lid = P(path((-10.4, 21.4), (10.4, 21.4), qb((10.4, 27), (0, 29), (-10.4, 27), 8)))
    k.plate(lid, 10.4, "chest")
    k.plate(rect(-9.6, 19, 9.6, 21.4), 8.8, "gold")
    for x, y in ((-7, 21.4), (-3, 21.0), (2, 21.2), (6.8, 20.8)):
        k.plate(disc(x, y, 1.3, 8), 11.0, "coin")
    for x in (-7.4, 7.4):
        k.box(x, 10.6, 0, 1.6, 8.8, 10.4, "band")
        k.plate(rect(x - 0.8, 21.2, x + 0.8, 27.8), 10.8, "band")
    k.plate(rect(-10.4, 10.6, 10.4, 11.8), 10.4, "band")
    k.plate(rect(-2.2, 15, 2.2, 22), 10.8, "band")
    k.plate(disc(0, 17.2, 1.5, 8), 11.2, "gem")
    for x, y in ((-12, 16), (12.6, 19), (13.6, 12.6)):
        k.plate(disc(x, y, 1.1, 8), 0.5, "coin")
        k.seg((x * 0.8, y), (x, y), 0.3, 0.3, "band")


@design("smiths_hammer")
def smiths_hammer(k):
    """a real one: a cross-peen hammer bigger than sense, the face polished by work, ash handle dark from the hand"""
    fe = ramp("#2a2e34", "#3e444c", "#565e68", "#727c86", "#929ca6", "#b4bec6", "#d4dce2", "#f0f4f6")
    k.mat(head=flat(fe, 0.56, bevel=0.16), face=flat(fe, 0.9, bevel=0.04), wood=staves(ramp("#3a2410", "#52341c", "#6e4826", "#8c6034", "#a87a48"), 1.2, 0.56), wrap=wrap(LEATHER, IRON[1], 5), dark=flat(IRON, 0.66))
    haft(k, 13)
    m = P((-5, 11.6), (5, 11.6), (5.6, 13), (10, 13.6), (10, 21), (5.6, 21.6), (5, 23), (-5, 23), (-5.6, 21), (-10, 18.4), (-13, 17.6), (-13, 16.2), (-10, 15.4), (-5.6, 13))
    block(k, m, 6.4, "head", "head")
    k.box(10.2, 14.2, 0, 0.8, 6.2, 5.0, "face")
    k.plate(rect(-1.4, 11.2, 1.4, 23.4), 6.7, "dark")


@design("frostmaul")
def frostmaul(k):
    """a head of ice that won't melt, cut square by whoever bound it, the corners growing back to points overnight"""
    k.theme("frost", base=0.5)
    ice = ramp("#0e2a3a", "#164058", "#205a78", "#2e7898", "#4a9cbc", "#78c0da", "#b0e0f0", "#e8f8ff")
    k.mat(ice=flat(ice, 0.66, bevel=0.14), white=flat(ice, 0.96, bevel=0), iron=flat(SILVER, 0.5), wrap=wrap(ramp("#14283a", "#203c54", "#30546e"), SILVER[2], 5), wood=staves(ramp("#2a3036", "#3a424a", "#4c565e", "#606a72"), 1.2, 0.56), dark=flat(SILVER, 0.4))
    haft(k, 13)
    m = rect(-7.4, 12, 7.4, 23)
    for x, y, ln, a in ((-7, 23, 6, 24), (7, 23, 6, -24), (-7, 12, 6, 156), (7, 12, 6, -156), (-7.4, 17.6, 4.6, 80), (7.4, 17.6, 4.6, -80), (0, 23, 4.4, 0)):
        m = m + shard(x, y, ln, a, 2.6)
    k.plate(m, 6.4, "ice")
    k.plate(rect(-6, 13.4, 6, 21.6), 7.4, "ice")
    k.plate(L([(-5, 21), (5, 14)], 0.8), 7.46, "white")
    k.plate(rect(-1.2, 11.4, 1.2, 23.6), 8.0, "iron")


@design("thunderhead")
def thunderhead(k):
    """a storm cloud caught in an iron cage on a pole: black billows pushing through the bars, lightning crawling from them down the haft"""
    storm = ramp("#141a22", "#1e2630", "#2a3442", "#384454", "#485668", "#5c6c80", "#7a8a9e")
    bolt = ramp("#3f7fd0", "#7ab0ff", "#c8e4ff", "#ffffff")
    k.mat(cloud=flat(storm, 0.5, 0.2, bevel=0.14), iron=flat(IRON, 0.7), hot=fire(bolt, 0.4, 0.6), wrap=wrap(storm, bolt[0], 4), wood=flat(IRON, 0.5), dark=flat(IRON, 0.7))
    haft(k, 13)
    m = disc(-5, 16, 5) + disc(5, 16.4, 5.4) + disc(0, 20, 6.4) + disc(-7.6, 19, 3.6) + disc(8, 20, 3.4) + disc(-1, 13.6, 4.4)
    k.plate(m, 8.4, "cloud")
    k.plate(m.inset(1.5), 9.4, "cloud")
    for x in (-8, -4, 0, 4, 8):
        k.box(x, 10.4, 0, 0.8, 16.4, 11, "iron")
    for y in (10.4, 26):
        k.box(0, y, 0, 18, 0.9, 11, "iron")
    k.plate(L([(-3, 11), (-1.6, 7.6), (-3, 5.4), (-1.4, 2.6)], 0.5) + L([(4, 15), (3, 18), (5.4, 18.6), (3.6, 22)], 0.5), 9.5, "hot", glow=True)


@design("worldbreaker")
def worldbreaker(k):
    """a mountain, more or less: a peak of obsidian on a pillar, lava running in its veins and out of a crater at the top, a little ring of cloud round its shoulders"""
    obs = ramp("#050406", "#0c0a0e", "#141118", "#1c1822", "#26202e", "#30283a", "#4e425c")
    lava = ramp("#a02206", "#e04a0a", "#ff8a1c", "#ffc84a", "#fff0b0")
    k.mat(rock=flat(obs, 0.6, 0.2, bevel=0.2), hot=fire(lava, 0.3, 0.7), cloud=flat(ramp("#6a6a74", "#94949c", "#c0c0c6", "#e8e8ec"), 0.6, bevel=0.1), wrap=wrap(obs, lava[1], 4), wood=flat(obs, 0.6), dark=flat(obs, 0.6))
    haft(k, 13, w=2.6)
    m = P((-13.4, 11), (13.4, 11), (10.4, 16), (8, 16.4), (5.4, 22), (3.6, 22.6), (2, 29), (-1.6, 29), (-3.4, 24), (-6, 22.6), (-8, 18), (-11, 15.6))
    k.plate(m, 8.0, "rock")
    k.plate(m.inset(1.5), 9.2, "rock")
    k.inlay(L([(0, 29), (-0.8, 24), (0.8, 21), (-1.4, 17), (-0.6, 13)], 1.0) + L([(0.8, 21), (4.6, 17), (5.2, 13.4)], 0.7) + L([(-1.4, 17), (-6.4, 14.4)], 0.7), 9.2, "hot", glow=True)
    k.plate(P((-1.8, 29), (1.8, 29), (2.6, 32.6), (0.6, 31), (-0.6, 33.6), (-2.2, 31)), 2.6, "hot", glow=True)
    k.plate(disc(-10, 17.4, 2.0, 8) + disc(-7.6, 18.4, 2.4, 8) + disc(9.6, 19.4, 2.2, 8) + disc(7.4, 20, 1.8, 8), 2.6, "cloud")


@design("miners_maul")
def miners_maul(k):
    """a delver's two-pound sledge grown to twenty: bare iron, one chipped corner, and the lamp hook still on the haft with a lamp on it"""
    fe = ramp("#1c1a18", "#2a2724", "#3a3632", "#4c4741", "#605a52", "#787066", "#928a7e", "#aea698")
    k.mat(head=flat(fe, 0.6, bevel=0.16), wood=staves(ramp("#2a1a0e", "#3a2616", "#4e3420", "#664428", "#7e5634"), 1.2, 0.56), wrap=wrap(LEATHER, IRON[1], 5), dark=flat(IRON, 0.66), lamp=fire(ramp("#c86a10", "#ffa83a", "#ffd878", "#fff4c8"), 0.3, 0.7), brass=flat(BRASS, 0.6))
    haft(k, 13)
    block(k, P((-8.4, 12), (8.4, 12), (8.4, 22), (6.8, 22), (5.6, 20.6), (5.2, 22), (-8.4, 22)), 6.4, "head")
    k.plate(rect(-1.4, 11.2, 1.4, 22.8), 6.8, "dark")
    k.plate(stroke((1, 7.6), (5, 7.8), (4.6, 4.6), 0.6), 0.7, "dark")
    k.plate(rect(3.2, 0.8, 6.0, 4.2), 2.4, "lamp", glow=True)
    k.plate(rect(3.0, 0.2, 6.2, 1.0) + rect(3.0, 4.2, 6.2, 5.0), 2.8, "brass")


@design("barnacle_maul")
def barnacle_maul(k):
    """a ship's capstan on a broken mast spar: the waisted drum, the bar holes, a lump of reef grown over one side of it"""
    fe = ramp("#16201e", "#22302c", "#30423e", "#425852", "#58726a", "#74908a")
    crust = ramp("#6a6656", "#8a8672", "#aaa692", "#c8c4b0", "#e2dece", "#f4f2e8")
    k.mat(drum=staves(ramp("#2a2622", "#3a3530", "#4c4640", "#5e5850", "#726a60"), 1.4, 0.56), iron=flat(fe, 0.6, bevel=0.14), crust=flat(crust, 0.66, bevel=0.14), wood=staves(ramp("#1e1a14", "#2e281e", "#403828", "#544a34"), 1.0, 0.56), wrap=wrap(fe, fe[0], 4), dark=flat(fe, 0.5))
    haft(k, 13, w=2.6)
    for j, r_ in enumerate((6.6, 6.0, 5.2, 4.8, 4.6, 4.8, 5.2, 6.0, 6.6)):
        k.box(0, 12 + j * 1.25, 0, 2 * r_, 1.3, 2 * r_, "drum")
    k.box(0, 23, 0, 15, 1.4, 15, "iron")
    k.box(0, 24.4, 0, 12.0, 1.4, 12.0, "drum")
    for a in (0, 90):
        k.box(0, 23.4, 0, 18 if a == 0 else 1.6, 0.9, 1.6 if a == 0 else 18, "iron")
    for x, y, r_ in ((-6.4, 14, 1.4), (-5, 18, 1.1), (-6.8, 21, 1.2), (-4, 13, 0.9)):
        k.plate(disc(x, y, r_, 8) - disc(x, y, 0.4, 6), 8.0, "crust")


@design("rockgrinder")
def rockgrinder(k):
    """a steam driller's engine: a spiral drill bit for a face and a riveted boiler for a heart, a pressure gauge in the red, a safety valve hissing"""
    k.mat(iron=flat(IRON, 0.62, bevel=0.14), steel_=flat(SILVER, 0.5, bevel=0.2), brass=flat(BRASS, 0.64), hot=fire(ramp("#c02a06", "#ff6a14", "#ffb040", "#ffe8a0"), 0.4, 0.6), gauge=flat(ramp("#c8c0a8", "#e8e0c8", "#fff8e8"), 0.7), wrap=wrap(LEATHER, IRON[1], 4), wood=flat(IRON, 0.5), dark=flat(IRON, 0.7))
    haft(k, 12, w=2.4)
    for j in range(8):
        r_ = 6.0 - j * 0.1
        k.box(-3 + j * 1.2, 16.6 - r_, 0, 1.25, 2 * r_, 2 * r_, "brass" if j in (1, 6) else "iron")
    k.plate(rect(-5.2, 10.6, 5.6, 11.6) + rect(-5.2, 21.6, 5.6, 22.6), 8.4, "iron")
    k.box(-4.4, 12.8, 0, 1.4, 7.6, 7.6, "hot", glow=True)
    n, x0 = 14, 6.4
    for j in range(n):
        x = x0 + j * 0.86
        r_ = 5.4 * (1 - j / n) + 0.3
        a = j * 0.9
        k.seg((x, 16.6 - math.cos(a) * r_), (x + 0.9, 16.6 + math.cos(a) * r_), 1.0, 2.2, "steel_", z=math.sin(a) * r_ * 0.5)
    k.box(x0 + 5, 16, 0, 12, 1.2, 1.2, "steel_")
    k.plate(disc(-2, 24.4, 1.8, 8), 2.0, "brass")
    k.plate(disc(-2, 24.4, 1.2, 8), 2.2, "gauge")
    k.plate(L([(-2, 24.4), (-1.2, 25.2)], 0.3), 2.3, "hot", glow=True)
    k.box(3, 22.6, 0, 1.0, 3.0, 1.0, "brass")


@design("legions_pillar")
def legions_pillar(k):
    """a basalt column torn from the Ash Legion's gate: fluted drum on drum, teal fire in the joins, the carved capital still on and a stub of the arch it held"""
    bas = ramp("#0e0c12", "#1a1720", "#282430", "#383242", "#4c4458", "#665c74")
    teal = ramp("#0e4a48", "#1a7e78", "#34b8aa", "#5cd8c8", "#8ceee2", "#f0fffc")

    def flute(p, n, b, key, i, j, w, h, fr):
        return at(bas, 0.6 + lit(key, i, j, w, h) + 0.16 * math.sin(p[0] * 2.6 + p[2] * 2.6))

    k.mat(stone=flute, cap=flat(bas, 0.72, bevel=0.2), hot=fire(teal, 0.4, 0.6), wrap=wrap(bas, teal[1], 4), wood=flat(bas, 0.5), dark=flat(bas, 0.7))
    haft(k, 8, w=2.6)
    for j, y in enumerate((8.4, 13.4, 18.4)):
        k.box(0, y, 0, 9.4 - j * 0.3, 4.6, 9.4 - j * 0.3, "stone")
        k.box(0, y + 4.6, 0, 8.4 - j * 0.3, 0.5, 8.4 - j * 0.3, "hot", glow=True)
    k.plate(P((-5, 23.2), (5, 23.2), (7.4, 26), (-7.4, 26)), 9.6, "cap")
    k.plate(rect(-8.4, 26, 8.4, 28), 11, "cap")
    k.plate(P((-8.4, 28), (8.4, 28), (6, 31.6), (2, 30.4), (-1.4, 32), (-6, 30)), 7.6, "stone")
    k.box(0, 6.8, 0, 11, 1.6, 11, "cap")


@design("concord")
def concord(k):
    """two hammers that agreed: an iron head and a gold one on one haft, faces turned in, a band of light held in the gap between them"""
    fe = ramp("#2a2e34", "#3e444c", "#565e68", "#727c86", "#929ca6", "#b4bec6", "#d4dce2")
    k.mat(iron=flat(fe, 0.56, bevel=0.16), gold=flat(GOLD, 0.62, bevel=0.16), hot=fire(ramp("#ffb040", "#ffe8a0", "#fffbe0", "#ffffff"), 0.4, 0.6), wood=flat(IRON, 0.5), dark=flat(IRON, 0.7), wrap=wrap(LEATHER, GOLD[3], 4))
    haft(k, 28, w=2.2)
    for y, m_, r_ in ((11.4, "iron", 1), (20.6, "gold", -1)):
        block(k, P((-8, y), (8, y), (9.6, y + 2), (9.6, y + 5), (8, y + 7), (-8, y + 7), (-9.6, y + 5), (-9.6, y + 2)), 7.0, m_)
    k.plate(rect(-8, 18.4, 8, 20.6), 3.0, "hot", glow=True)
    k.box(0, 28, 0, 3.2, 1.6, 3.2, "gold")
