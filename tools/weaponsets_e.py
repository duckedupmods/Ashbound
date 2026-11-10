"""Daggers: every gate's pair, the world's finds, Twinfang. Short: the blade seldom past y 18."""
import math

from voxsword import ramp
from weaponsets import design, qb, path, P, L, disc, ring, rect, wave, taper, Mask, flat, fire, staves, steel, honed, bone, gem, at, lit, wrap, stripes, facet_of
from weaponsets_a import BRASS, GOLD, IRON, LEATHER
from weaponsets_c import shard
from weaponsets_d import RUBY, SILVER, feathers, stroke

IVORY = ramp("#5a4a38", "#7e6c54", "#a29074", "#c2b294", "#dccdb0", "#efe4cc", "#fbf6e6")
CORK = ramp("#6a4a2a", "#8a6840", "#a88658", "#c8a878", "#e0c49a")
RAG = ramp("#3a3428", "#544c3c", "#706652", "#8e846c", "#aca286")
HORN = ramp("#141010", "#241c18", "#3a2f26", "#54453a", "#76665a", "#9c8c7c")


@design("spigot_knife")
def spigot_knife(k):
    """a cask's spigot with a knife where the spout was: a brass tap for a guard, its key sticking out to one side, a cork pommel"""
    R = k.theme("cellar", base=0.5)
    k.mat(brass=flat(BRASS, 0.62), cork=flat(CORK, 0.56, 0.3))
    k.forge(P((-1.8, 3), (1.8, 3), (2.2, 9), (0.4, 16.4), (-1.6, 11)), 1.5)
    k.inlay(L([(0.2, 4), (0.5, 9)], 0.5), 1.5, "glow", glow=True)
    k.plate(rect(-2.0, 1.2, 2.0, 3.4), 2.6, "brass")
    k.plate(rect(2.0, 1.8, 3.8, 2.8) + rect(3.2, 0.8, 4.2, 4.0) + rect(2.6, 3.6, 4.8, 4.4), 1.2, "brass")
    k.grip(-3.8, 1.3, 2.0)
    k.box(0, -5.6, 0, 2.6, 1.9, 2.6, "cork")


@design("corkscrew")
def corkscrew(k):
    """the Cask Mother's: a real worm of black iron, four full turns tapering to a needle, on a T of old oak and an iron boss"""
    R = k.theme("cellar", base=0.5)
    k.mat(iron=flat(R["blade"], 0.72), brass=flat(BRASS, 0.6))
    n, prev = 34, None
    for j in range(n + 1):
        a = math.radians(j * 40)
        r_ = 2.1 * (1 - j / n * 0.85)
        p = (math.sin(a) * r_, 3.0 + j * 0.46)
        z = math.cos(a) * r_
        if prev:
            k.seg(prev[0], p, 1.2 - j * 0.012, 1.2, "iron", z=(prev[1] + z) / 2)
        prev = (p, z)
    k.box(0, 1.6, 0, 3.0, 2.0, 3.0, "brass")
    k.box(0, 0.2, 0, 2.0, 1.6, 2.0, "dark")
    k.box(0, -1.8, 0, 13.0, 2.4, 2.4, "wood")
    for x in (-5.8, 5.8):
        k.box(x, -2.1, 0, 1.2, 3.0, 2.8, "dark")
    k.grip(-4.6, -1.8, 1.8)
    k.box(0, -5.6, 0, 2.4, 1.1, 2.4, "dark")
    k.box(0, -4.6, 0, 1.0, 1.0, 2.8, "glow", glow=True)


@design("gibbet_knives")
def gibbet_knives(k):
    """a coffin nail the length of a hand, drawn from the gibbet and filed sharp: square section, a wide rough head, hemp round the shank"""
    R = k.theme("gallows", base=0.5)
    k.mat(rope=wrap(R["wrap"], R["dark"][0], 4), nail=flat(R["blade"], 0.76))
    for j, y in enumerate((1.6, 5.4, 9.0, 12.2)):
        w = 2.4 - j * 0.5
        k.box(0, y, 0, w, 4.0, w, "nail")
    k.plate(P((-0.7, 16), (0.7, 16), (0, 19.2)), 0.9, "edge")
    k.grip(-3.6, 1.6, 2.1, "rope")
    k.plate(P((-3.0, -5.4), (3.0, -5.4), (2.6, -3.6), (-2.6, -3.6)), 3.2, "nail")


@design("noose_cutter")
def noose_cutter(k):
    """the hook a hangman keeps for the rope: a hawkbill blade curling in on its own edge, and a little noose still round the pommel, an ember tied in the knot"""
    R = k.theme("gallows", base=0.46)
    k.mat(rope=flat(R["acc"], 0.6), hemp=wrap(R["wrap"], R["dark"][0], 4))
    m = P(path(qb((-1.8, 3), (-3.6, 14), (5.4, 15.4), 12), (5.4, 15.4), (4.4, 10.8), qb((3.6, 12.2), (1.0, 11), (1.8, 3), 10)))
    k.forge(m, 1.6, ridge=-0.3)
    k.box(0, 1.8, 0, 6.0, 1.3, 2.6, "dark")
    k.grip(-3.6, 1.9, 2.0, "hemp")
    k.box(0, -5.0, 0, 2.4, 1.4, 2.4, "dark")
    k.plate(ring(0, -9.4, 3.0, 2.0), 1.1, "rope")
    k.box(0, -6.6, 0, 1.5, 1.6, 1.5, "hemp")
    k.box(0, -6.2, 0, 0.8, 0.8, 1.7, "glow", glow=True)


@design("thorn_shiv")
def thorn_shiv(k):
    """one thorn off a Rotwood briar as long as a forearm, the stub of its branch still on for a handle"""
    R = k.theme("rotwood", base=0.5)
    k.mat(blade=steel(R["acc"], 0.42, 0.12), edge=honed(R["blade"], 0.7), bark=staves(R["wood"], 1.2, 0.6), moss=flat(R["wrap"], 0.6))
    k.forge(P(path((-2.6, 2), qb((-1.6, 8), (-0.8, 12), (2.4, 19), 10), (2.4, 19), qb((1.6, 12), (2.8, 8), (2.6, 2), 10))), 1.9, step=1)
    k.plate(rect(-2.4, -5.4, 2.4, 2.4) - P((2.6, -3), (1.6, -2), (2.6, -1)), 2.6, "bark")
    k.plate(L([(-2.2, -3), (-5.2, -1.2)], 1.1), 1.4, "bark")
    k.box(0, 1.4, 0, 5.4, 1.0, 2.9, "moss")
    k.box(-1.2, -5.8, 0, 2.6, 1.0, 2.9, "moss")


@design("velvet_tine")
def velvet_tine(k):
    """an antler tine torn off the Mossking in rut: bone curved to a point, red velvet still peeling from it in strips, one glowing bead of sap"""
    R = k.theme("rotwood", base=0.5)
    velvet = ramp("#3a0a0c", "#601216", "#8a1e20", "#b03230", "#d05a4a")
    k.mat(blade=bone(R["blade"], 0.64), edge=flat(R["blade"], 0.86), velvet=flat(velvet, 0.56, 0.3), moss=flat(R["wrap"], 0.58))
    m = P(path(qb((-2.2, 2), (-3.6, 12), (4.6, 20), 12), (4.6, 20), qb((1.2, 13), (2.4, 8), (2.2, 2), 10)))
    k.forge(m, 2.2, step=1, ridge=-0.2)
    k.plate(P((-2.4, 2), (2.4, 2), (2.2, 5), (0.8, 8.4), (0.2, 5.6), (-1.0, 11), (-2.0, 7), (-3.8, 3.8)), 2.5, "velvet")
    k.plate(P((-3.0, 8), (-4.8, 4.6), (-3.8, 5.4), (-2.8, 3.8)), 1.0, "velvet")
    k.plate(disc(0.6, 12.4, 0.8, 8), 2.4, "glow", glow=True)
    k.box(0, 0.6, 0, 5.4, 1.5, 3.0, "moss")
    k.grip(-3.8, 0.8, 2.1)
    k.plate(disc(0, -5.4, 2.1, 8), 2.8, "edge")


@design("gravediggers_knife")
def gravediggers_knife(k):
    """cut down from a dead sexton's spade: the square-shouldered shovel blade, a tread on top, a D-handle at the grip's end"""
    R = k.theme("crypt", base=0.46)
    k.mat(ash=staves(R["wood"], 0.9, 0.6))
    k.forge(P((-3.6, 4), (3.6, 4), (3.2, 12), (0, 17.6), (-3.2, 12)), 1.3)
    k.plate(rect(-3.8, 3.2, 3.8, 4.2), 2.2, "dark")
    k.plate(P((-1.0, 2.0), (1.0, 2.0), (0.7, 9), (-0.7, 9)), 1.7, "dark")
    k.grip(-3.6, 2.2, 1.8, "ash")
    k.plate(P((-2.6, -7.6), (2.6, -7.6), (2.6, -6.4), (1.2, -3.6), (-1.2, -3.6), (-2.6, -6.4)) - P((-1.6, -6.8), (1.6, -6.8), (0.7, -4.8), (-0.7, -4.8)), 2.0, "ash")


@design("last_candle")
def last_candle(k):
    """the last of the abbey's candles, its wick still lit: a stiletto sheathed in wax to the point, tallow frozen running down over a brass drip cup"""
    R = k.theme("crypt", base=0.56)
    k.mat(wax=flat(R["acc"], 0.72, bevel=0.1), brass=flat(GOLD, 0.56), flame=fire(R["glow"], 0.4, 0.6))
    k.plate(P((-1.7, 3), (1.7, 3), (1.4, 14.4), (-1.4, 15.2)), 2.8, "wax")
    k.forge(P((-0.5, 14), (0.5, 14), (0, 19.0)), 0.9)
    k.plate(P(path(qb((0, 15.8), (-2.2, 18.2), (0, 23.0)), qb((0, 23.0), (2.2, 18.2), (0, 15.8)))), 1.4, "flame", glow=True)
    k.plate(P(path(qb((0, 16.6), (-1, 18), (0, 20.2)), qb((0, 20.2), (1, 18), (0, 16.6)))), 1.6, "glow", glow=True)
    k.plate(P((-2.8, 2.4), (-1.6, 2.6), (-1.4, 8), (-2.4, 6.4)) + P((1.4, 2.6), (2.8, 2.4), (2.6, 10), (1.6, 11.8)), 3.0, "wax")
    k.plate(P((-4.8, 1.4), (4.8, 1.4), (5.4, 2.8), (-5.4, 2.8)), 3.4, "brass")
    k.plate(ring(5.6, 1.6, 1.6, 0.8), 0.9, "brass")
    k.grip(-3.8, 1.5, 1.8)
    k.box(0, -4.8, 0, 2.4, 1.1, 2.4, "brass")


@design("plague_lancets")
def plague_lancets(k):
    """a barber-surgeon's folding lancet opened out: a small leaf blade between two horn scales swung wide, a brass pin at the fork"""
    R = k.theme("plague", base=0.58)
    k.mat(horn=flat(HORN, 0.6, bevel=0.14), brass=flat(R["dark"], 0.62))
    k.forge(P((-1.0, 2), (1.0, 2), (2.0, 7), (0, 17), (-2.0, 7)), 1.0, step=1)
    for s_ in (1, -1):
        k.plate(P(path((s_ * 0.2, 2.4), qb((s_ * 3.6, 6.4), (s_ * 6.6, 10), (s_ * 5.0, 12.0), 8), (s_ * 5.0, 12.0), (s_ * 3.2, 11.0), qb((s_ * 1.6, 6.8), (s_ * 0.4, 5), (s_ * 0.0, 3.4), 6))), 1.1, "horn")
    k.plate(disc(0, 2.6, 1.3, 8), 2.0, "brass")
    k.grip(-3.8, 1.8, 1.9)
    k.plate(P((-1.6, -5.2), (1.6, -5.2), (1.0, -3.8), (-1.0, -3.8)), 2.2, "brass")
    k.plate(rect(-0.2, -5.2, 0.2, 1.8) & rect(-1, -1, 1, 1), 2.1, "glow", glow=True)


@design("scalpel_saint")
def scalpel_saint(k):
    """the surgeon who was canonised: a gilded scalpel, its handle knurled, its belly honed white, a thin halo standing behind the blade"""
    R = k.theme("plague", base=0.62)
    k.mat(gold=flat(GOLD, 0.62, bevel=0.14), halo=fire(GOLD, 0.5, 0.5), knurl=wrap(GOLD, GOLD[1], 2), edge=honed(SILVER, 0.86))
    k.forge(P((-1.0, 2.6), (1.4, 2.6), (2.2, 8), (1.4, 13), (-1.0, 19.4)), 0.9, step=1, ridge=-0.2)
    k.plate(ring(0, 12.0, 6.0, 5.0), 0.8, "halo", glow=True, z=-0.9)
    for j in range(8):
        a = j * math.pi / 4 + 0.39
        k.plate(P((math.cos(a - 0.14) * 5.8, 12 + math.sin(a - 0.14) * 5.8), (math.cos(a) * 7.8, 12 + math.sin(a) * 7.8), (math.cos(a + 0.14) * 5.8, 12 + math.sin(a + 0.14) * 5.8)), 0.6, "halo", glow=True, z=-0.9)
    k.plate(P((-1.0, 1.0), (1.0, 1.0), (1.2, 3.2), (-1.2, 3.2)), 1.5, "gold")
    k.box(0, -5.0, 0, 1.5, 6.2, 1.5, "knurl")
    k.plate(P((-1.2, -6.6), (1.2, -6.6), (0, -4.8)), 1.7, "gold")


@design("faceless_fang")
def faceless_fang(k):
    """a white tooth of stone in a black hilt, unmarked, with a small blank face staring out of the pommel"""
    R = k.theme("temple", base=0.72, ridge=0.08)
    k.mat(mask=flat(R["blade"], 0.86, bevel=0.06))
    k.forge(P((-1.9, 3), (1.9, 3), (1.6, 10), (0, 16.6), (-1.6, 10)), 1.5)
    k.plate(P((-3.0, 1.8), (3.0, 1.8), (2.2, 3.4), (-2.2, 3.4)), 2.2, "dark")
    k.grip(-3.8, 1.9, 1.9)
    k.plate(P(path(qb((-2.2, -3.8), (-2.6, -7.6), (0, -8.8)), qb((0, -8.8), (2.6, -7.6), (2.2, -3.8)))), 2.2, "mask")
    k.inlay(rect(-1.5, -5.8, -0.5, -5.4) + rect(0.5, -5.8, 1.5, -5.4), 2.2, "dark")


@design("visage_thief")
def visage_thief(k):
    """a waved kris with a face for every one it has taken: small blank masks strung up the blade, the top one still screaming blue fire"""
    R = k.theme("temple", base=0.66)
    k.mat(mask=flat(R["blade"], 0.86, bevel=0.06), gold=flat(R["acc"], 0.62), edge=honed(R["acc"], 0.8))
    k.forge(wave(lambda t: 1.2 * math.sin(t * 11), lambda t: 2.2 * (1 - t ** 2.2) + 0.1, 3, 21, 26), 1.5)
    for j, y in enumerate((6, 10.4, 14.8)):
        x = 1.2 * math.sin((y - 3) / 18 * 11)
        s_ = 1.0 - j * 0.1
        k.plate(P(path(qb((x - 1.5 * s_, y + 1.4), (x - 1.8 * s_, y - 1.3), (x, y - 2.0)), qb((x, y - 2.0), (x + 1.8 * s_, y - 1.3), (x + 1.5 * s_, y + 1.4)))), 2.0, "mask")
        k.plate(rect(x - 1 * s_, y - 0.1, x - 0.3 * s_, y + 0.3) + rect(x + 0.3 * s_, y - 0.1, x + 1 * s_, y + 0.3), 2.1, "glow" if j == 2 else "dark", glow=j == 2)
    k.plate(P((-3.6, 1.8), (3.6, 1.8), (2.6, 3.6), (-2.6, 3.6)), 2.4, "gold")
    k.grip(-3.8, 1.9, 1.9)
    k.plate(disc(0, -5.2, 1.7, 8), 2.2, "gold")


@design("bonewright_shiv")
def bonewright_shiv(k):
    """a thighbone snapped on the bias: the break is the edge, the knuckle end is the hilt, brass staples where it cracked"""
    R = k.theme("ossuary", base=0.5)
    k.mat(bone=bone(R["acc"], 0.68), edge=flat(R["acc"], 0.9, bevel=0.04), brass=flat(R["dark"], 0.62))
    m = P((-2.0, -2), (2.0, -2), (2.2, 8), (1.0, 11), (0.6, 18.4), (-1.6, 12))
    k.plate(m, 1.6, "edge")
    k.plate(m.inset(0.5), 3.0, "bone")
    k.plate(disc(-1.4, -4.4, 2.2, 10) + disc(1.4, -4.4, 2.2, 10), 3.0, "bone")
    for y in (5, 8):
        k.box(0, y, 0, 3.4, 0.7, 3.2, "brass")
    k.plate(rect(-2.4, -1.6, 2.4, 0.6), 3.2, "wrap")
    k.plate(rect(-0.3, 9, 0.3, 13), 3.04, "dark")


@design("piston_shiv")
def piston_shiv(k):
    """a piston made a stabbing tool: the grip is the cylinder, a steel rod drives the short spike out of it, a coil spring round the rod, soul fire in the sight glass"""
    R = k.theme("ossuary", base=0.56)
    k.mat(brass=flat(R["dark"], 0.62), spring=flat(R["blade"], 0.78), rod=steel(R["blade"], 0.66, 0.1))
    k.forge(P((-1.7, 11), (1.7, 11), (1.4, 14), (0, 21), (-1.4, 14)), 1.6)
    k.plate(rect(-0.9, 1.5, 0.9, 11.5), 1.8, "rod")
    for j in range(6):
        k.seg((-1.6, 2.0 + j * 1.4), (1.6, 2.7 + j * 1.4), 0.5, 2.4, "spring")
    k.plate(rect(-2.4, 10.4, 2.4, 11.6), 2.6, "brass")
    k.plate(rect(-2.2, -4.4, 2.2, 1.6), 3.2, "brass")
    k.plate(rect(-2.6, 1.0, 2.6, 2.0) + rect(-2.6, -4.8, 2.6, -3.8), 3.6, "dark")
    k.plate(rect(-1.1, -3.2, 1.1, 0.4), 3.3, "glow", glow=True)
    k.plate(ring(-3.6, -1.6, 1.4, 0.6), 0.9, "brass")
    k.box(0, -6.2, 0, 2.2, 1.4, 2.2, "brass")


@design("kiln_fang")
def kiln_fang(k):
    """a smith's cold chisel gone wrong: a thick wedge, its end burning, the struck head mushroomed over from a thousand hammer blows"""
    R = k.theme("foundry", base=0.46)
    hot = ramp("#120a08", "#2a0e08", "#5a1206", "#9a2206", "#e04a0a", "#ff8a1c", "#ffc84a", "#fff0b0")
    from weaponsets import heat
    k.mat(blade=heat(hot, 6, 20), edge=heat(hot, 2, 12), rimc=honed(ramp("#2a2622", "#4a433c", "#6e665c", "#9c9286"), 0.8))
    m = P((-1.9, 3), (1.9, 3), (2.6, 11), (2.6, 14), (-0.4, 19.6), (-2.6, 12))
    k.forge(m & rect(-4, 0, 4, 11), 2.4, body="dark", rim="rimc")
    k.plate(m & rect(-4, 11, 4, 21), 2.4, "blade", glow=True)
    k.inlay(L([(0.4, 11), (-0.6, 8.4), (0.4, 6.4)], 0.5), 2.4, "edge", glow=True)
    k.plate(P((-2.6, 1.8), (2.6, 1.8), (2.0, 3.2), (-2.0, 3.2)), 2.8, "dark")
    k.grip(-3.6, 1.9, 2.2)
    k.plate(P((-1.4, -3.8), (1.4, -3.8), (2.8, -5.0), (3.2, -6.4), (1.8, -5.8), (0, -6.8), (-1.8, -5.8), (-3.2, -6.4), (-2.8, -5.0)), 3.0, "dark")


@design("ember_fang")
def ember_fang(k):
    """not steel at all: a tongue of the Foundry's fire held in a dagger's shape, a coal for its heart, gripped in a cage of black tines"""
    R = k.theme("foundry", base=0.46)
    flame = ramp("#a02206", "#e04a0a", "#ff8a1c", "#ffc84a", "#fff0b0", "#fffbe8")
    k.mat(flame=fire(flame, 0.1, 0.9), coal=flat(ramp("#100a08", "#2a1208", "#6a1a06", "#c0400a", "#ff8a1c"), 0.4, 0.8), iron=flat(IRON, 0.56))
    m = P(path(qb((-3.0, 3), (-5.6, 10), (-1.6, 14.2), 8), (-1.6, 14.2), (-2.2, 10.8), (0.4, 16.8), (0.2, 13.0), (1.8, 22.4), qb((3.0, 13.6), (4.8, 8), (3.0, 3), 8)))
    k.plate(m, 1.6, "flame", glow=True)
    k.plate(m.inset(1.0), 1.9, "glow", glow=True)
    k.plate(disc(0, 7, 1.6, 8), 2.3, "coal")
    for s_ in (1, -1):
        k.plate(stroke((s_ * 1.0, 1.6), (s_ * 5.6, 3.0), (s_ * 2.8, 9.4), 0.9, 8), 1.6, "iron")
    k.box(0, 1.4, 0, 5.4, 1.5, 2.6, "iron")
    k.grip(-3.8, 1.5, 2.0)
    k.plate(P((-1.8, -5.2), (1.8, -5.2), (0, -7.8)), 2.2, "iron")


@design("icicle_dirk")
def icicle_dirk(k):
    """an icicle snapped off the eaves, bound to a stick with strips of a dead man's coat"""
    R = k.theme("frost", base=0.5)
    k.mat(ice=flat(R["glow"], 0.7, bevel=0.14), white=flat(R["glow"], 0.92, bevel=0.04), rag=wrap(R["wrap"], R["dark"][2], 3), stick=staves(R["wood"], 1.0, 0.56))
    m = P((-2.6, 0), (-1.6, 2), (2.2, 0.6), (2.4, 4), (1.4, 9), (0.8, 13), (0.3, 19.6), (-0.6, 11), (-1.8, 6))
    k.plate(m, 1.8, "ice")
    k.plate(L([(-0.2, 2), (0.0, 9), (0.2, 15)], 0.9), 2.0, "white")
    k.grip(-5.0, 0.0, 1.8, "stick")
    k.plate(rect(-2.2, -2.6, 2.2, 2.6) - P((2.4, 2.8), (2.4, 1.2), (1.0, 2.8)), 2.6, "rag")
    k.plate(P((-2.0, -2.4), (-3.4, -5.6), (-2.2, -5.0), (-1.2, -2.4)), 0.7, "rag")


@design("frostbite")
def frostbite(k):
    """a hand of ice closing: five frozen fingers grow from the guard and curl together into the blade, black at the tips where frost has killed them"""
    R = k.theme("frost", base=0.5)
    black = ramp("#06080e", "#0e1420", "#1a2436", "#2e4056")

    def finger(p, n, b, key, i, j, w, h, fr):
        t = p[1] / 20
        if t > 0.72:
            return at(black, 0.6 + lit(key, i, j, w, h))
        return at(R["glow"], 0.72 - t * 0.3 + lit(key, i, j, w, h) + (0.1 if facet_of(p, b) < 0 else -0.1))

    k.mat(finger=finger, bone=flat(R["glow"], 0.9, bevel=0.04), iron=flat(R["dark"], 0.56))
    for s_, x0, cx, x1, top, w in ((1, 3.0, 8.4, 7.6, 11.6, 1.5), (-1, 3.0, 8.6, 8.2, 13.4, 1.6), (1, 1.4, 5.2, 3.4, 17.6, 1.8), (-1, 1.6, 5.0, 3.0, 18.8, 1.8)):
        k.plate(P(path(qb((s_ * (x0 - w), 3), (s_ * (cx - w * 1.2), top * 0.7), (s_ * x1, top), 10), (s_ * x1, top), qb((s_ * cx, top * 0.6), (s_ * (x0 + w), 4), (s_ * (x0 + w), 3), 8))), 1.7, "finger")
    k.plate(P(path(qb((-1.7, 3), (-1.5, 15), (0.3, 24.0), 12), (0.3, 24.0), qb((1.5, 15), (1.7, 8), (1.7, 3), 10))), 2.1, "finger")
    k.plate(P((-4.8, 1.6), (4.8, 1.6), (3.4, 4.4), (-3.4, 4.4)), 2.8, "iron")
    k.grip(-3.8, 1.7, 1.9)
    k.plate(shard(0, -3.6, 4.2, 180, 2.0), 1.8, "bone")


@design("quill_knife")
def quill_knife(k):
    """a penknife the size of a dirk: a short nib of a blade in the shaft of a great white quill, its feather fanning from the hilt"""
    R = k.theme("silk", base=0.56)
    k.mat(feather=flat(R["acc"], 0.8, bevel=0.1), vane=flat(R["acc"], 0.56, bevel=0.08), ink=fire(R["glow"], 0.1, 0.8))
    m = P((-1.4, 2), (1.4, 2), (1.8, 6), (0, 16.6), (-1.8, 6))
    k.forge(m - L([(0, 16.6), (0, 9)], 0.4), 1.2, step=1)
    k.plate(L([(0, 16.6), (0, 9)], 0.4) & m, 0.5, "ink", glow=True)
    stem = qb((0, 1), (1.4, -6), (7.0, -11.6), 10)
    v = Mask()
    for j, q in enumerate(stem[1:]):
        v = v + L([q, (q[0] + 2.4 + j * 0.1, q[1] + 1.2)], 1.0) + L([q, (q[0] - 2.4, q[1] - 0.8)], 1.0)
    k.plate(v, 0.7, "vane")
    k.plate(L(stem + [(7.0, -11.6)], 0.9), 1.4, "feather")
    k.box(0, 0.6, 0, 3.0, 1.5, 2.2, "dark")


@design("fang_of_the_queen")
def fang_of_the_queen(k):
    """the Silk Queen's chelicera sawn off whole: a black hooked fang on its bristled base, venom beading purple along the inside"""
    R = k.theme("silk", base=0.46)
    k.mat(blade=steel(R["dark"], 0.62, 0.16), edge=honed(R["blade"], 0.64), bristle=flat(R["dark"], 0.5, 0.5), base=flat(R["dark"], 0.76, bevel=0.2))
    m = P(path(qb((-2.6, 7), (-3.2, 18), (5.6, 21.6), 12), (5.6, 21.6), qb((2.0, 16.4), (2.4, 12), (2.8, 7), 8)))
    k.forge(m, 2.0, ridge=-0.2)
    y = 9.0
    while y < 18:
        x = 2.0 + (y - 9) * 0.12
        k.plate(disc(x, y, 0.6, 6), 1.4, "glow", glow=True)
        y += 3
    b = P(path(qb((-3.0, 8), (-5.0, 3), (-2.2, 1), 6), (-2.2, 1), (2.2, 1), qb((5.0, 3), (3.2, 8), (3.2, 8), 3)))
    for x, y in ((-4.0, 4), (-3.6, 6.4), (3.8, 4), (3.6, 6.2)):
        s_ = 1 if x > 0 else -1
        b = b + P((x - 0.5, y), (x + s_ * 2.0, y - 1.2), (x, y + 0.6))
    k.plate(b, 3.0, "base")
    k.grip(-3.6, 1.4, 1.9)
    k.plate(disc(0, -5.0, 1.7, 8), 2.4, "base")


@design("pick_knife")
def pick_knife(k):
    """half a broken pick: the point and the eye, the old handle cut down to a grip and the crack bound with copper"""
    R = k.theme("weeping_mine", base=0.5)
    k.mat(copper=flat(R["acc"], 0.56))
    m = P(path(qb((-2.2, 4), (-0.6, 12), (5.6, 19), 10), (5.6, 19), qb((1.8, 13), (2.6, 9), (2.2, 4), 8)))
    k.forge(m, 2.0, ridge=-0.25)
    k.plate(P((-3.2, 0.8), (3.0, 0.8), (3.0, 4.4), (-3.2, 4.4), (-5.4, 3.4), (-5.4, 2)), 2.8, "dark")
    k.grip(-3.8, 1.0, 2.2, "wood")
    for y in (-0.6, -2.0):
        k.box(0, y, 0, 2.6, 0.7, 2.6, "copper")
    k.box(0, -5.0, 0, 2.6, 1.2, 2.6, "copper")


@design("shardfang")
def shardfang(k):
    """a raw splinter of the mine's weeping crystal, wrapped at the root in copper wire, a smaller one growing beside it"""
    R = k.theme("weeping_mine", base=0.5)
    k.mat(crystal=flat(R["glow"], 0.7, bevel=0.14), copper=wrap(ramp("#3a1a08", "#6a3414", "#9c5a24", "#c8843c"), None, 2))
    k.plate(shard(0, 3, 19, -5, 4.0) + shard(-1.6, 3, 11, 20, 2.4) + shard(1.8, 3, 8.6, -30, 2.2), 2.4, "crystal")
    k.plate(shard(0, 4, 15, -5, 1.6), 2.6, "glow", glow=True)
    k.grip(-3.8, 4.0, 2.4, "copper")
    k.plate(shard(0, -3.8, 3.2, 180, 1.8), 1.6, "crystal")


@design("barnacle_shiv")
def barnacle_shiv(k):
    """an oyster shell's broken lip for an edge, crusted thick, set in a twist of tarred line"""
    R = k.theme("tide_chapel", base=0.5)
    k.mat(shell=flat(R["acc"], 0.7, bevel=0.1), rope=wrap(R["dark"], R["dark"][0], 4))
    m = P((-2.6, 2), (2.6, 2), (3.6, 7), (2.6, 11), (2.8, 13.4), (0.4, 18), (-1.0, 14.2), (-2.2, 13.8), (-2.0, 10), (-3.6, 7))
    k.plate(m, 1.2, "edge")
    k.plate(m.inset(0.5), 1.9, "shell")
    for x, y, r_ in ((-1.4, 4.6, 1.1), (1.3, 6.4, 1.0), (-0.8, 9.4, 0.9), (0.9, 11, 0.7)):
        k.plate(disc(x, y, r_, 8) - disc(x, y, 0.35, 6), 2.8, "wood")
    k.grip(-3.8, 2.4, 2.1, "rope")
    k.box(0, -5.6, 0, 2.8, 1.8, 2.8, "shell")


@design("pearl_stiletto")
def pearl_stiletto(k):
    """a bishop's silver needle, three pearls along its guard, and an oyster held open at the pommel with the biggest one inside"""
    R = k.theme("tide_chapel", base=0.6)
    k.mat(silver=flat(SILVER, 0.56), pearl=flat(R["glow"], 0.88), shell=flat(R["acc"], 0.6, bevel=0.14))
    k.forge(taper(1.0, 0.7, 3, 18, 22.0), 1.3)
    k.plate(rect(-4.4, 1.8, 4.4, 3.0), 2.0, "silver")
    for x in (-4.4, 0, 4.4):
        k.plate(disc(x, 2.4, 1.1, 8), 2.4, "pearl")
    k.grip(-3.8, 1.9, 1.8, "wrap")
    k.plate(P(path(qb((0, -4.2), (-4.2, -4.6), (-3.2, -8.8), 6), (-3.2, -8.8), (-0.4, -6.6))) + P(path(qb((0, -4.2), (4.2, -4.6), (3.2, -8.8), 6), (3.2, -8.8), (0.4, -6.6))), 1.2, "shell")
    k.plate(disc(0, -6.2, 1.5, 10), 2.6, "pearl")


@design("cutthroat_knife")
def cutthroat_knife(k):
    """a barber's straight razor, the kind they name after what it does: a square-ended hollow blade, a tang and two horn scales"""
    R = k.theme("brigands_gorge", base=0.6)
    k.mat(horn=flat(HORN, 0.56, bevel=0.14), brass=flat(GOLD, 0.6))
    k.forge(P((-1.0, 4), (2.6, 4), (3.6, 16.6), (-1.4, 17.4), (-1.6, 15)), 1.0, step=1, ridge=-0.4)
    k.plate(rect(-1.6, 3.0, -0.6, 17), 1.9, "dark")
    k.plate(P((-1.2, 2.4), (0.6, 2.4), (0.6, 5), (-1.2, 5)), 1.5, "brass")
    k.plate(P((-1.8, 2.8), (1.2, 2.8), (1.8, -5.4), (-1.0, -6.0)), 1.8, "horn")
    k.box(0.2, -0.2, 0, 0.9, 0.9, 2.0, "brass")
    k.box(0.2, -4.4, 0, 0.9, 0.9, 2.0, "brass")


@design("purse_slitter")
def purse_slitter(k):
    """a tiny hooked blade with the takings still on it: a stolen purse cut and tied to the pommel, coins spilling from the neck"""
    R = k.theme("brigands_gorge", base=0.52)
    k.mat(purse=flat(R["wrap"], 0.6, bevel=0.14), coin=flat(GOLD, 0.68), cord=flat(R["acc"], 0.7))
    m = P(path(qb((-1.4, 3), (-2.8, 12), (4.2, 16.4), 10), (4.2, 16.4), qb((1.0, 11), (1.4, 8), (1.4, 3), 8)))
    k.forge(m, 1.3, step=1, ridge=-0.3)
    k.plate(P((-3, 1.8), (3, 1.8), (3.8, 3.4), (-2.2, 3.0)), 2.2, "coin")
    k.grip(-3.2, 1.9, 1.8)
    k.box(0, -4.2, 0, 2.2, 1.0, 2.2, "coin")
    k.box(0, -6.0, 0, 0.6, 1.8, 0.6, "cord")
    k.plate(P(path((-1.0, -6.0), (1.0, -6.0), qb((3.8, -7.2), (4.6, -12.0), (0, -12.2), 8), qb((0, -12.2), (-4.6, -12.0), (-3.8, -7.2), 8))), 3.0, "purse")
    k.box(0, -6.6, 0, 3.0, 0.7, 3.2, "cord")
    for x, y in ((3.8, -13.2), (1.2, -14.0), (5.0, -11.0)):
        k.plate(disc(x, y, 1.0, 8), 0.5, "coin")
        k.seg((x - 0.8, y + 0.6), (0.4, -11.8), 0.2, 0.2, "cord")


@design("talon_knife")
def talon_knife(k):
    """a giant rook's foot cut off at the ankle: one black hook of a claw and the scaled toe it grew from, the foot's knuckle in the hand"""
    R = k.theme("rookery", base=0.46, edge=0.7)
    k.mat(scale=flat(ramp("#2a2410", "#4a401c", "#6e6030", "#948444", "#b8a660"), 0.56, bevel=0.2), blade=steel(HORN, 0.56, 0.14))
    m = P(path(qb((-2.4, 6), (-3.4, 15), (4.8, 18.6), 12), (4.8, 18.6), qb((1.2, 13), (1.6, 9), (2.0, 6), 8)))
    k.forge(m, 2.2, ridge=-0.2)
    for j, y in enumerate((0.8, 2.6, 4.4, 6.0)):
        k.plate(rect(-2.8 + j * 0.2, y, 2.8 - j * 0.2, y + 1.5), 3.0 - j * 0.1, "scale")
    k.grip(-3.8, 1.0, 2.2, "scale")
    k.plate(disc(0, -5.0, 2.2, 9), 2.8, "scale")


@design("eyepick")
def eyepick(k):
    """a long spike and what it found: the eye is still on it, wet and burning, its optic trailing down the shaft"""
    R = k.theme("rookery", base=0.5)
    k.mat(white=flat(ramp("#a89c80", "#ccc0a4", "#e8dec6", "#fbf6e6"), 0.7, bevel=0.14), iris=flat(R["glow"], 0.62), pupil=flat(ramp("#000000", "#0a0a0a"), 0.4, bevel=0), nerve=flat(ramp("#4a0c10", "#6e161a", "#942428", "#b83c3a"), 0.56))
    k.forge(taper(1.0, 0.5, 3, 20, 24.6), 1.2)
    k.plate(disc(0, 13.2, 3.4, 16), 3.4, "white")
    k.plate(disc(0, 13.2, 1.9, 12), 3.6, "glow", glow=True)
    k.plate(disc(0, 13.2, 0.8, 8), 3.8, "pupil")
    k.plate(wave(lambda t: 0.8 + 0.8 * math.sin(t * 8), lambda t: 0.4, 10.2, 3.6, 12), 1.5, "nerve")
    k.plate(P((-2.6, 1.8), (2.6, 1.8), (1.2, 3.4), (-1.2, 3.4)), 2.2, "dark")
    k.grip(-3.8, 1.9, 1.8)
    k.plate(disc(0, -5.0, 1.6, 8), 2.2, "dark")


@design("juggling_knives")
def juggling_knives(k):
    """an act's knife: blade polished for the spotlights, a bowling-pin handle in stripes, ribbons streaming"""
    R = k.theme("hollow_circus", base=0.66)
    red = ramp("#2a0408", "#4e0810", "#7a1018", "#a81c20", "#d0302a", "#ee5a44")
    cream = ramp("#6a5a44", "#8e7c60", "#b4a282", "#d6c8a8", "#efe4c8", "#fff8e8")
    k.mat(pin=stripes(red, cream, 1.6, 0.0), ribbon=flat(red, 0.7, bevel=0.14), gold=flat(GOLD, 0.66))
    k.forge(taper(1.7, 1.2, 3.4, 14, 19.0), 1.4)
    k.plate(rect(-2.6, 2.4, 2.6, 3.4), 2.0, "gold")
    k.plate(P(path((-1.0, 2.4), (1.0, 2.4), qb((1.2, 0), (3.0, -2), (2.2, -5.2), 6), qb((2.2, -5.2), (1.6, -6.6), (0, -6.6), 4), qb((0, -6.6), (-1.6, -6.6), (-2.2, -5.2), 4), qb((-2.2, -5.2), (-3.0, -2), (-1.2, 0), 6))), 2.6, "pin")
    k.plate(wave(lambda t: 2.6 + 4.0 * t, lambda t: 0.5, 2.8, -6, 12) + wave(lambda t: -2.6 - 3.0 * t, lambda t: 0.5, 2.8, -3.6, 10), 0.4, "ribbon")


@design("knife_thrower_pick")
def knife_thrower_pick(k):
    """the card up the thrower's sleeve: a black spade for a head, a gold ace pip cut in it, a tasselled needle of a handle"""
    R = k.theme("hollow_circus", base=0.5)
    black = ramp("#08060c", "#121016", "#1c1822", "#2a2432", "#3e3648", "#5a5068")
    k.mat(blade=steel(black, 0.54, 0.14), edge=honed(GOLD, 0.76), gold=flat(GOLD, 0.66), ribbon=flat(R["wrap"], 0.66, 0.2))
    m = disc(-3.0, 9.0, 3.4) + disc(3.0, 9.0, 3.4) + P((-6.2, 10.4), (6.2, 10.4), (0, 21.4)) + P((-1.0, 3), (1.0, 3), (0, 8))
    k.forge(m, 1.5)
    k.inlay(P((0, 15.4), (1.4, 12.6), (0, 10.0), (-1.4, 12.6)), 1.5, "gold")
    k.plate(rect(-1.8, 2.2, 1.8, 3.4), 2.0, "gold")
    k.grip(-3.8, 2.2, 1.6)
    k.plate(disc(0, -4.8, 1.3, 8), 1.8, "gold")
    k.plate(P((-0.8, -5.6), (0.8, -5.6), (1.2, -10.0), (0, -9.0), (-1.2, -10.0)), 0.8, "ribbon")


@design("toad_knife")
def toad_knife(k):
    """a fat bog toad squats on the hilt, warts and gold eyes, and what it spits is the blade: a long wet tongue of hexed iron"""
    R = k.theme("mirefen_coven", base=0.5)
    toad = ramp("#10180c", "#1c2a14", "#2c401c", "#3e5826", "#547432", "#749848")
    tongue = ramp("#3a0c1a", "#6a1c2e", "#a03448", "#d05a68", "#f09a9a")
    k.mat(toad=flat(toad, 0.6, bevel=0.14), blade=steel(tongue, 0.56, 0.16), edge=honed(tongue, 0.88), eye=flat(GOLD, 0.8), wart=flat(toad, 0.92, bevel=0))
    k.forge(wave(lambda t: 1.0 * math.sin(t * 5), lambda t: 1.8 * (1 - t ** 3) + 0.3 * math.sin(t * 3.1) + 0.05, 5, 19.0, 20), 1.5)
    body = disc(0, 2.0, 4.6, 16) + disc(-2.6, 4.6, 1.7, 10) + disc(2.6, 4.6, 1.7, 10)
    k.plate(body, 3.6, "toad")
    k.plate(rect(-2.4, 3.6, 2.4, 4.2), 3.7, "edge")
    for s_ in (1, -1):
        k.plate(disc(s_ * 2.6, 5.0, 1.0, 8), 3.9, "eye")
        k.plate(rect(s_ * 2.6 - 0.2, 4.4, s_ * 2.6 + 0.2, 5.6), 4.0, "wart")
    for x, y in ((-3.0, 0.8), (2.0, -0.6), (0.0, 1.8), (3.0, 2.0), (-1.2, -1.2)):
        k.plate(disc(x, y, 0.5, 6), 3.8, "wart")
    k.grip(-5.2, -1.6, 1.9)
    k.plate(disc(0, -6.0, 1.6, 8), 2.2, "toad")


@design("hags_nail")
def hags_nail(k):
    """the Matron's thumbnail: cracked, yellow, grown out for a hundred years in one long curl, still on a finger bound in bandage"""
    R = k.theme("mirefen_coven", base=0.5)
    nail = ramp("#3a3010", "#5a4c1c", "#7e6e2c", "#a29440", "#c4b860", "#e4dc90")
    skin = ramp("#2c2a1c", "#46422c", "#625e40", "#807c58", "#a09c74")
    k.mat(blade=steel(nail, 0.56, 0.12, scars=0.08), edge=honed(nail, 0.9), skin=flat(skin, 0.56, bevel=0.14), rag=wrap(RAG, RAG[0], 3), hot=fire(R["glow"], 0.3, 0.6))
    m = P(path(qb((-2.2, 7), (-5.2, 16), (3.2, 24.4), 12), (3.2, 24.4), qb((7.8, 25.2), (8.2, 19.6), (6.0, 18.6), 6), (6.0, 18.6), qb((6.4, 21.0), (3.2, 21.2), (0.6, 16.4), 6), qb((0.6, 16.4), (2.0, 12), (2.2, 7), 6)))
    k.forge(m, 1.5, step=1, ridge=-0.3)
    k.inlay(L([(-1.4, 9), (-0.8, 13), (-1.4, 15.6)], 0.4), 1.5, "hot", glow=True)
    k.plate(P(path((-2.6, 1), (2.6, 1), qb((3.0, 5), (2.8, 9), (2.8, 9), 3), (-2.8, 9))), 2.8, "skin")
    k.inlay(L([(-2.2, 4.4), (2.2, 4.0)], 0.5) + L([(-2.2, 2.2), (2.2, 2.4)], 0.5), 2.8, "dark")
    k.grip(-3.8, 1.2, 2.3, "rag")
    k.plate(disc(0, -5.2, 2.0, 8), 2.6, "edge")


@design("scarab_dagger")
def scarab_dagger(k):
    """a tomb guard's dagger: a gold leaf of a blade with a lapis line, and for a guard a scarab with its wings half lifted"""
    k.theme("sandsunk_tomb", base=0.56)
    lapis = ramp("#081a4a", "#0e2a6e", "#163e96", "#2458c0", "#4a84e0")
    k.mat(blade=steel(GOLD, 0.54, 0.14), edge=honed(ramp("#a06018", "#d8982c", "#f6d060", "#fff0b0", "#ffffff"), 0.7), lapis=flat(lapis, 0.56), gold=flat(GOLD, 0.66), bug=flat(lapis, 0.46, bevel=0.2))
    k.forge(P((-1.8, 4), (1.8, 4), (2.4, 9), (0, 18), (-2.4, 9)), 1.4)
    k.inlay(L([(0, 5), (0, 14)], 0.6), 1.4, "lapis")
    k.plate(disc(0, 2.6, 2.4, 12), 2.6, "bug")
    for s_ in (1, -1):
        k.plate(P(path((s_ * 1.6, 1.4), qb((s_ * 5.4, 1.0), (s_ * 8.2, 3.4), (s_ * 7.6, 6.4), 6), (s_ * 7.6, 6.4), qb((s_ * 5.2, 4.4), (s_ * 3.6, 4.4), (s_ * 1.8, 3.8), 6))), 1.2, "gold")
    k.grip(-3.8, 1.2, 1.9, "lapis")
    k.plate(P((-1.6, -3.8), (1.6, -3.8), (2.4, -6.2), (0, -5.2), (-2.4, -6.2)), 2.2, "gold")


@design("scarab_fang")
def scarab_fang(k):
    """the sacred beetle at its work: the blade is a pair of great mandibles closing on nothing, the beetle's lapis body is the hilt, gold-legged"""
    lapis = ramp("#04181a", "#082c30", "#104a4e", "#1c7070", "#38a09a", "#70d0c0")
    k.theme("sandsunk_tomb", base=0.56)
    k.mat(blade=steel(GOLD, 0.56, 0.14), edge=honed(ramp("#a06018", "#d8982c", "#f6d060", "#fff0b0", "#ffffff"), 0.7), bug=flat(lapis, 0.5, bevel=0.2), gold=flat(GOLD, 0.66), red=flat(RUBY, 0.56))
    for s_ in (1, -1):
        k.forge(P(path((s_ * 0.2, 3), qb((s_ * 7.4, 4), (s_ * 7.8, 14), (s_ * 0.8, 21 + s_ * 0.8), 12), (s_ * 0.8, 21 + s_ * 0.8), qb((s_ * 3.8, 13), (s_ * 2.6, 8), (s_ * 0.2, 7), 10))), 1.7, step=1)
    k.plate(disc(0, 2.0, 3.0, 12), 3.0, "bug")
    k.plate(rect(-0.2, -5, 0.2, 5), 3.04, "gold")
    k.grip(-5.2, 0.0, 2.8, "bug")
    k.plate(disc(0, -5.6, 2.4, 12), 2.8, "bug")
    for y in (-1.0, -3.0, -5.0):
        for s_ in (1, -1):
            k.plate(L([(s_ * 1.4, y), (s_ * 3.8, y - 0.6), (s_ * 4.0, y - 2.0)], 0.5), 0.8, "gold")


@design("fangs")
def fangs(k):
    """a great tooth from the fallen Titan's jaw, two roots still on it, forked round the fist and lashed with sinew"""
    R = k.theme("fallen_titan", base=0.5)
    k.mat(blade=bone(IVORY, 0.72), edge=flat(IVORY, 0.92, bevel=0.04), rootc=bone(IVORY, 0.42), sinew=wrap(ramp("#2a0608", "#4a0c10", "#6e161a", "#942428"), None, 3))
    k.plate(P(path((-3.6, 2), qb((-3.8, 10), (-2.4, 14), (0.6, 21), 8), (0.6, 21), qb((2.6, 13), (3.6, 9), (3.6, 2), 8))), 1.8, "edge")
    k.plate(P(path((-3.2, 2), qb((-3.4, 10), (-2.0, 14), (0.4, 19), 8), (0.4, 19), qb((2.2, 13), (3.2, 9), (3.2, 2), 8))), 3.0, "blade")
    for s_ in (1, -1):
        k.plate(P(path((s_ * 1.0, 2), (s_ * 3.8, 2), qb((s_ * 4.2, -3), (s_ * 2.0, -5), (s_ * 2.0, -6.8), 6), qb((s_ * 0.8, -3), (s_ * 1.4, -1), (s_ * 1.0, 2), 6))), 3.0, "rootc")
    k.grip(-5.6, 1.8, 2.0, "sinew")


@design("fang_of_the_titan")
def fang_of_the_titan(k):
    """the Titan's eye tooth, as long as a sword and cracked to the nerve; the nerve is still alive and glows up the channel. It should not fit a dagger's grip, and doesn't"""
    R = k.theme("fallen_titan", base=0.5)
    nerve = ramp("#7a1018", "#c02030", "#ff5a4a", "#ffb09a", "#ffe8e0")
    k.mat(blade=bone(IVORY, 0.72), edge=flat(IVORY, 0.92, bevel=0.04), rootc=bone(IVORY, 0.42), nerve=fire(nerve, 0.3, 0.7), sinew=wrap(ramp("#2a0608", "#4a0c10", "#6e161a", "#942428"), None, 3))
    m = P(path((-4.4, 3), qb((-5.4, 14), (-2.2, 20), (3.4, 27.6), 12), (3.4, 27.6), qb((4.4, 16), (4.6, 10), (4.4, 3), 10)))
    k.plate(m, 1.8, "edge")
    k.plate(m.inset(0.5), 3.4, "blade")
    k.plate(L(qb((0, 3), (-1.6, 12), (1.4, 22), 8) + [(1.4, 22)], 1.0), 3.46, "nerve", glow=True)
    k.plate(L([(-0.9, 13), (-3.0, 15.6)], 0.5) + L([(0, 17), (1.8, 15)], 0.5), 3.46, "nerve", glow=True)
    k.plate(rect(-4.8, 1.2, 4.8, 3.2), 3.6, "rootc")
    for s_ in (1, -1):
        k.plate(P(path((s_ * 2, 1.4), (s_ * 4.6, 1.4), qb((s_ * 5.0, -3), (s_ * 2.4, -6), (s_ * 3.4, -9.4), 6), qb((s_ * 1.4, -5), (s_ * 2.0, -2), (s_ * 1.4, 1.2), 6))), 3.0, "rootc")
    k.grip(-5.8, 1.4, 2.1, "sinew")


@design("mantis_knife")
def mantis_knife(k):
    """a praying mantis's foreleg cut in green stone, by a monk with time: the hooked claw, the row of spines, the folded joint for a guard"""
    R = k.theme("jade_monastery", base=0.54)
    k.mat(gold=flat(GOLD, 0.64), joint=flat(R["blade"], 0.5, bevel=0.14))
    m = P(path(qb((-1.8, 4), (-2.8, 13), (3.6, 19.4), 10), (3.6, 19.4), qb((0.6, 14), (1.8, 10), (2.0, 4), 8)))
    y = 6.0
    while y < 14.6:
        x = 1.9 - (y - 6) * 0.05
        m = m + P((x - 0.5, y), (x + 1.9, y + 1.2), (x - 0.6, y + 1.4))
        y += 2.3
    k.forge(m, 1.5, step=1, ridge=-0.2)
    k.plate(disc(0, 2.6, 2.5, 8), 2.6, "joint")
    k.plate(disc(0, 2.6, 1.1, 8), 2.8, "gold")
    k.grip(-3.8, 1.0, 1.9)
    k.box(0, -5.0, 0, 2.4, 1.2, 2.4, "gold")


@design("jade_fang")
def jade_fang(k):
    """a sliver of the temple's oldest jade, a tiger fang in its green, the gold mount a tiger's open mouth, a short red tassel"""
    R = k.theme("jade_monastery", base=0.58)
    tassel = ramp("#3a0608", "#600c0e", "#8a1416", "#b42020", "#dc3a30")
    k.mat(gold=flat(GOLD, 0.64, bevel=0.14), tassel=flat(tassel, 0.56, 0.25), gem=gem(tassel))
    k.forge(P(path((-2.4, 5), qb((-2.6, 13), (-0.6, 18), (2.0, 21.6), 8), (2.0, 21.6), qb((2.0, 13), (2.8, 10), (2.4, 5), 8))), 1.9, ridge=-0.1)
    mouth = P((-3.4, 1.8), (3.4, 1.8), (4.4, 7.4), (2.8, 5.4), (1.6, 6.8), (0.6, 5.0), (-0.6, 5.0), (-1.6, 6.8), (-2.8, 5.4), (-4.4, 7.4))
    k.plate(mouth, 2.8, "gold")
    k.plate(disc(-1.8, 3.2, 0.5, 6) + disc(1.8, 3.2, 0.5, 6), 2.9, "gem")
    k.grip(-3.6, 1.9, 1.8)
    k.box(0, -4.8, 0, 2.2, 1.2, 2.2, "gold")
    k.plate(P((-1.0, -5.0), (1.0, -5.0), (1.5, -10.4), (0.2, -9.2), (-1.5, -10.4)), 1.0, "tassel")


@design("spark_knife")
def spark_knife(k):
    """a lightning rod's two prongs: a copper fork with a spark jumping back and forth across its tines, an insulated grip"""
    R = k.theme("storm_bastion", base=0.5)
    copper = ramp("#3a1a08", "#6a3414", "#9c5a24", "#c8843c", "#e8a860", "#ffd090")
    k.mat(blade=steel(copper, 0.54, 0.14), edge=honed(copper, 0.8), white=flat(R["glow"], 0.92, bevel=0.02), rub=wrap(IRON, None, 3))
    fork = P((-3.2, 4), (3.2, 4), (3.2, 16), (2.6, 20), (1.6, 16), (1.6, 6), (-1.6, 6), (-1.6, 16), (-2.6, 20), (-3.2, 16))
    k.forge(fork, 1.4, step=1)
    k.plate(L([(-2, 8), (0.8, 9.6), (-0.8, 11), (2, 12.4)], 0.5) + L([(-2, 14), (-0.2, 15.2), (1.0, 14.4), (2, 16)], 0.4), 0.5, "white", glow=True)
    k.plate(rect(-1.0, 2.0, 1.0, 4.4), 1.8, "edge")
    k.grip(-3.8, 2.2, 2.2, "rub")
    k.box(0, -5.2, 0, 2.6, 1.4, 2.6, "edge")


@design("static_fang")
def static_fang(k):
    """a bottled storm: a glass ball at the pommel with lightning crawling in it, a jag of blue-white steel out the other end, a coil of copper between"""
    R = k.theme("storm_bastion", base=0.5)
    k.mat(white=flat(R["glow"], 0.92, bevel=0.02), edgef=fire(R["glow"], 0.3, 0.7), copper=wrap(ramp("#3a1a08", "#6a3414", "#9c5a24", "#c8843c"), None, 2), glass=flat(ramp("#2a3a4a", "#4a6278", "#7e9ab0", "#b4cee0"), 0.3, bevel=0.2))
    m = P((-1.6, 3), (2.2, 3), (1.0, 9), (3.8, 8.6), (0.2, 15.6), (2.2, 15), (-1.6, 24), (-0.4, 16.6), (-3.0, 17), (-0.6, 10.4), (-3.0, 10.8))
    k.plate(m, 1.0, "edgef", glow=True)
    k.plate(m.inset(0.5), 1.8, "blade")
    k.plate(L([(0.2, 4), (-1.2, 10), (1.8, 9.4), (-1.0, 16.4), (0.8, 15.6)], 0.5), 1.86, "white", glow=True)
    k.plate(P((-3.0, 1.6), (3.0, 1.6), (3.4, 3.2), (-3.4, 3.2)), 2.4, "dark")
    k.grip(-3.8, 1.7, 2.1, "copper")
    k.plate(disc(0, -6.4, 3.0, 14), 2.8, "glass")
    k.plate(L([(0, -3.8), (-1.2, -5.8), (0.8, -6.4), (-0.6, -8.4)], 0.5) + L([(0.8, -6.4), (2.0, -7.4)], 0.4), 3.0, "white", glow=True)


@design("fang_dagger")
def fang_dagger(k):
    """a courtier's pair of needles set side by side, a bite you can hide in a sleeve: two white fangs in a bat-eared guard"""
    R = k.theme("bloodmoon_court", base=0.56)
    k.mat(tooth=flat(IVORY, 0.8, bevel=0.06), silver=flat(IRON, 0.7), gem=gem(RUBY))
    for s_ in (1, -1):
        k.plate(P((s_ * 0.4, 3), (s_ * 3.0, 3), (s_ * 2.4, 11), (s_ * 1.4, 19.0), (s_ * 0.8, 10)), 1.6, "tooth")
    k.plate(rect(-3.2, 1.8, 3.2, 3.6) + P((-3.2, 2.6), (-5.0, 7.0), (-3.0, 5.4), (-2.0, 3.0)) + P((3.2, 2.6), (5.0, 7.0), (3.0, 5.4), (2.0, 3.0)), 2.4, "silver")
    k.plate(disc(0, 2.7, 0.9, 8), 2.7, "gem")
    k.grip(-3.8, 1.9, 1.8)
    k.plate(disc(0, -5.0, 1.6, 8), 2.2, "silver")


@design("vaels_fang")
def vaels_fang(k):
    """Vael's ritual knife, red glass over black steel with a blood channel that fills itself; a ruby the size of a thumb hangs from the crescent guard on a thread"""
    R = k.theme("bloodmoon_court", base=0.42)
    k.mat(hot=fire(RUBY, 0.3, 0.6), silver=flat(IRON, 0.7), gem=gem(RUBY), edge=honed(ramp("#2a0a10", "#5a1420", "#9a2030", "#e04a50", "#ffb0a8"), 0.74))
    k.forge(wave(lambda t: 0.7 * math.sin(t * 6.4), lambda t: 2.3 * (1 - t ** 2.4) + 0.1, 4, 23, 24), 1.8)
    k.inlay(wave(lambda t: 0.7 * math.sin(t * 6.4), lambda t: 0.45, 5, 19, 18), 1.8, "hot", glow=True)
    k.plate(disc(0, 7.2, 6.2) - disc(0, 9.4, 6.0), 2.2, "silver")
    k.box(-4.8, 0.6, 0, 0.3, 3.0, 0.3, "silver")
    k.plate(P((-4.8, 0.8), (-3.8, -0.8), (-4.8, -2.8), (-5.8, -0.8)), 1.6, "gem")
    k.grip(-3.8, 1.3, 1.9)
    k.plate(disc(0, -5.0, 1.7, 8), 2.2, "silver")
    k.plate(disc(0, -5.0, 0.8, 8), 2.4, "hot", glow=True)


@design("glass_shiv")
def glass_shiv(k):
    """black volcanic glass, knapped to a blade of long conchoidal facets, its grip a torn rag of the last person lost down here"""
    k.theme("obsidian_labyrinth", base=0.46)
    glass = ramp("#050408", "#100c18", "#1e1630", "#32244e", "#50387a", "#7c58b0", "#c0a0f0")

    def knap(p, n, b, key, i, j, w, h, fr):
        return at(glass, 0.42 + lit(key, i, j, w, h) + 0.2 * math.sin(p[1] * 1.1 + p[0] * 1.9))

    k.mat(glass=knap, rim=flat(glass, 0.85, bevel=0.04), rag=wrap(RAG, RAG[0], 3))
    m = P((-2.8, 1.4), (2.0, 1.4), (3.4, 6), (1.6, 11), (2.0, 13), (-0.6, 21.0), (-2.2, 12), (-1.4, 9), (-3.4, 5))
    k.plate(m, 1.0, "rim")
    k.plate(m.inset(0.5), 1.8, "glass")
    k.grip(-3.8, 3.4, 2.4, "rag")
    k.plate(P((-1.6, -3.2), (-3.6, -7.4), (-2.0, -6.4), (-0.4, -3.2)), 0.7, "rag")


@design("horn_shard")
def horn_shard(k):
    """the Labyrinth's keeper broke this off on a wall: a ridged black horn with a gold-capped point, the first turn of the red thread still tied round it"""
    k.theme("obsidian_labyrinth", base=0.46)
    def ribbed(p, n, b, key, i, j, w, h, fr):
        return at(HORN, 0.5 + lit(key, i, j, w, h) + (0.16 if facet_of(p, b) < 0 else -0.08) + 0.14 * math.sin(p[1] * 3.0))
    k.mat(blade=ribbed, edge=flat(HORN, 0.8, bevel=0.04), gold=flat(GOLD, 0.68), thread=flat(RUBY, 0.56), wrap=wrap(LEATHER, GOLD[3], 4))
    m = P(path(qb((-3.0, 3), (-3.6, 16), (6.0, 24), 14), (6.0, 24), qb((2.0, 15), (2.8, 9), (3.0, 3), 12)))
    k.forge(m, 3.0, step=1, ridge=-0.2)
    k.plate(m & P((2.0, 17), (9, 17), (9, 26), (1.0, 26), (4.0, 20)), 3.2, "gold")
    for j in range(4):
        k.seg((-3.6, 8.0 + j * 0.9), (3.6, 8.6 + j * 0.9), 0.5, 3.4, "thread")
    k.plate(P((-3.6, 1.6), (3.6, 1.6), (3.0, 3.2), (-3.0, 3.2)), 3.4, "gold")
    k.grip(-3.8, 1.7, 2.1)
    k.plate(disc(0, -5.0, 1.8, 8), 2.4, "gold")


@design("lure_knife")
def lure_knife(k):
    """a fisherman's gaff from the deep: a barbed hook of a blade, and from its back on a long thin stalk the angler's lure, burning cold"""
    R = k.theme("abyssal_lighthouse", base=0.5)
    k.mat(lure=fire(R["glow"], 0.4, 0.6), stalk=flat(R["dark"], 0.7))
    m = P(path((-1.6, 3), (1.6, 3), qb((3.2, 9), (5.4, 15), (1.0, 17.6), 8), (1.0, 17.6), (-1.4, 14.2), (0.4, 14.8), qb((2.2, 13), (0.4, 9), (-1.6, 7), 6)))
    k.forge(m, 1.6, step=1, ridge=0.0)
    k.plate(stroke((-1.2, 4), (-6.6, 9), (-3.4, 17.6), 0.6, 10), 0.7, "stalk")
    k.plate(disc(-3.4, 18.8, 1.7, 10), 2.0, "lure", glow=True)
    k.plate(P((-3.0, 1.8), (3.0, 1.8), (2.2, 3.2), (-2.2, 3.2)), 2.2, "dark")
    k.grip(-3.8, 1.9, 1.9)
    k.box(0, -5.0, 0, 2.4, 1.2, 2.4, "dark")


@design("lure_fang")
def lure_fang(k):
    """the angler itself, or the front of it: a black jaw for a guard, needle teeth overlapping, one of them long enough to be the blade, the lure curling over and hanging in front"""
    R = k.theme("abyssal_lighthouse", base=0.5)
    fish = ramp("#08060e", "#10101a", "#1a1a2a", "#28283e", "#3a3a56")
    k.mat(fish=flat(fish, 0.58, bevel=0.12), tooth=flat(IVORY, 0.82, bevel=0.06), lure=fire(R["glow"], 0.4, 0.6), blade=bone(IVORY, 0.7), edge=flat(IVORY, 0.92, bevel=0.04), gum=flat(ramp("#2a0a18", "#4a1228", "#6e1e3c"), 0.5))
    k.forge(P(path((-1.8, 4), qb((-2.2, 12), (-0.4, 18), (0.8, 24), 8), (0.8, 24), qb((1.6, 14), (2.0, 10), (1.8, 4), 8))), 1.8, step=1)
    k.plate(P(path((-7.0, 1.4), (7.0, 1.4), qb((7.4, 5), (5.6, 7.4), (4.6, 8), 5), (3.4, 5.4), (1.8, 4.6), (-1.8, 4.6), (-3.4, 5.4), qb((-4.6, 8), (-5.6, 7.4), (-7.4, 5), 5))), 3.0, "fish")
    k.plate(rect(-6, 3.4, 6, 4.4), 3.2, "gum")
    for x, ln in ((-5.4, 3.6), (-3.6, 5.0), (3.2, 5.6), (5.0, 3.8)):
        k.plate(P((x - 0.7, 3.8), (x + 0.7, 3.8), (x, 3.8 + ln)), 1.0, "tooth")
    k.plate(stroke((1.0, 6.0), (10.4, 20), (4.6, 20.4), 0.6, 12), 0.7, "fish")
    k.plate(disc(4.2, 18.8, 1.7, 10), 2.0, "lure", glow=True)
    k.grip(-3.8, 1.5, 2.0)
    k.plate(P((-2.8, -6.6), (0, -4.4), (2.8, -6.6), (0.8, -5.8), (0, -7.8), (-0.8, -5.8)), 1.6, "fish")


@design("black_feather")
def black_feather(k):
    """one black feather fell in the Cathedral and it was sharp: the vane hard as steel, split near the tip, a dull gold quill for the grip"""
    R = k.theme("eclipse_cathedral", base=0.3, ridge=0.08)
    black = ramp("#040408", "#0a0a12", "#12121c", "#1c1c2a", "#2a2a3c", "#40405a", "#6a6a88")
    k.mat(blade=steel(black, 0.5, 0.16, sheen=0.16), edge=honed(black, 0.9), quill=flat(GOLD, 0.56))
    m = wave(lambda t: 2.0 * t * t, lambda t: 2.9 * math.sin(min(1, t * 1.05 + 0.1) * math.pi) ** 0.6 + 0.3, 1, 22, 24)
    for y, s_ in ((15, 1), (10, -1), (17, -1)):
        x = 2.0 * ((y - 1) / 21) ** 2 + s_ * 3.3
        m = m - L([(x + s_ * 0.6, y + 1.2), (x - s_ * 1.6, y - 0.8)], 0.4)
    k.forge(m, 1.2, step=1)
    k.plate(wave(lambda t: 2.0 * t * t, lambda t: 0.3, -5, 20, 24), 1.5, "quill")
    k.grip(-3.8, 1.2, 1.8, "wrap")


@design("last_feather")
def last_feather(k):
    """the last one to fall, still burning: white at the shaft, gold where it catches, a thin halo round the grip that won't go out"""
    k.theme("eclipse_cathedral", base=0.66, ridge=0.1)
    flame = ramp("#a06018", "#e8a020", "#ffd060", "#fff0b0", "#ffffff")
    k.mat(blade=steel(ramp("#8a8aa0", "#b0b0c4", "#d4d4e2", "#f0f0f6", "#ffffff"), 0.6, 0.12), edge=fire(flame, 0.3, 0.7), quill=flat(GOLD, 0.66), flame=fire(flame, 0.1, 0.9), halo=fire(GOLD, 0.5, 0.5))
    m = wave(lambda t: -2.4 * t * t, lambda t: 3.3 * math.sin(min(1, t * 1.05 + 0.1) * math.pi) ** 0.6 + 0.3, 1, 25, 26)
    k.plate(m, 1.0, "edge", glow=True, tag="edge")
    k.plate(m.inset(0.5), 1.6, "blade", tag="blade")
    k.plate(wave(lambda t: -2.4 * t * t, lambda t: 0.35, -5, 23, 26), 1.9, "quill")
    for x, y, h in ((-4.6, 15, 4), (-5.6, 20, 3.4), (3.2, 12, 3.2), (2.6, 17, 3.0)):
        k.plate(P((x - 0.9, y), (x + 0.9, y), (x + (0.5 if x > 0 else -0.5), y + h)), 0.8, "flame", glow=True)
    k.plate(ring(0, -1.0, 3.4, 2.7), 0.9, "halo", glow=True)
    k.grip(-3.8, 1.2, 1.8, "wrap")


@design("kobold_shiv")
def kobold_shiv(k):
    """what a kobold takes from a dragon's hoard: one gold spoon, the bowl beaten to an edge, the handle wound in stolen ribbon"""
    k.theme("wyrms_hoard", base=0.6)
    k.mat(blade=steel(GOLD, 0.56, 0.14), edge=honed(ramp("#a06018", "#d8982c", "#f6d060", "#fff0b0", "#ffffff"), 0.7), gold=flat(GOLD, 0.62), bowl=flat(GOLD, 0.34, bevel=0.1), rag=wrap(ramp("#2a0606", "#4a0c0a", "#741612", "#9c2218"), None, 3), gem=gem(RUBY))
    bowl = P(path((-0.8, 3), qb((-4.0, 6), (-3.8, 13), (0, 17.8), 8), qb((0, 17.8), (3.8, 13), (4.0, 6), 8), (0.8, 3)))
    k.forge(bowl, 1.0, step=2)
    k.plate(bowl.inset(1.5), 1.08, "bowl")
    k.plate(rect(-0.9, 0, 0.9, 4), 1.0, "gold")
    k.grip(-3.8, 1.8, 1.7, "rag")
    k.plate(P((-1.7, -5.2), (1.7, -5.2), (0.9, -3.8), (-0.9, -3.8)), 1.0, "gold")
    k.plate(disc(0, -4.6, 0.6, 6), 1.3, "gem")


@design("wyrm_tooth")
def wyrm_tooth(k):
    """a wyrm's incisor in a mount worth a kingdom: gold filigree climbing the root, rubies, and the tooth itself barely scratched by the things it has bitten"""
    k.theme("wyrms_hoard", base=0.6)
    k.mat(blade=bone(IVORY, 0.72), edge=flat(IVORY, 0.92, bevel=0.04), gold=flat(GOLD, 0.64, bevel=0.14), gem=gem(RUBY))
    m = P(path((-3.2, 3), qb((-3.8, 13), (-0.8, 20), (1.2, 25), 10), (1.2, 25), qb((3.4, 14), (3.4, 9), (3.2, 3), 10)))
    k.forge(m, 2.4, step=1)
    fil = stroke((-3.4, 3), (-0.4, 7), (3.2, 10), 0.8) + stroke((3.4, 3), (0.4, 7), (-3.0, 10.4), 0.8) + stroke((-3.2, 6), (-3.2, 9), (-1.8, 14), 0.6) + stroke((3.2, 7), (3.0, 11), (2.4, 15), 0.6)
    k.plate(fil, 2.7, "gold")
    k.plate(disc(0, 6.0, 1.3, 8), 3.0, "gem")
    k.plate(P((-4.4, 1.6), (4.4, 1.6), (3.6, 3.6), (-3.6, 3.6)), 3.2, "gold")
    k.grip(-3.8, 1.7, 2.0)
    k.plate(disc(0, -5.2, 2.0, 8), 2.6, "gold")
    k.plate(disc(0, -5.2, 1.0, 8), 2.9, "gem")


# ---------------------------------------------------------------- the world's

@design("cutpurse_knife")
def cutpurse_knife(k):
    """a thief's bronze leaf: short, broad, nothing to catch on, a bit of cord in the pommel hole"""
    bronze = ramp("#2a1606", "#432410", "#5e3618", "#7c4c22", "#9c6630", "#bc8444", "#d8a462", "#f0c88a")
    k.mat(blade=steel(bronze, 0.56, 0.14), edge=honed(bronze, 0.88), bronze=flat(bronze, 0.5), wrap=wrap(LEATHER, bronze[2], 4), cord=flat(RAG, 0.7))
    k.forge(P(path((-0.9, 2.8), qb((-3.8, 7), (-2.4, 12), (0, 16), 8), qb((0, 16), (2.4, 12), (3.8, 7), 8), (0.9, 2.8))), 1.3)
    k.plate(rect(-1.8, 1.8, 1.8, 3.0), 2.0, "bronze")
    k.grip(-3.2, 1.9, 1.7)
    k.plate(ring(0, -4.4, 1.5, 0.6), 1.2, "bronze")


@design("vipers_kiss")
def vipers_kiss(k):
    """a viper struck in steel: the blade is the snake, S-curved, its head at the point with jaws open and a green drop on the fang; its tail wraps the grip"""
    venom = ramp("#0a1a0c", "#122a14", "#1c3e1c", "#285426", "#366c30", "#4a883c", "#68a650", "#94c870")
    hot = ramp("#3a7a10", "#68c020", "#a4f040", "#e0ffa0")
    k.mat(blade=steel(venom, 0.56, 0.14), edge=honed(venom, 0.9), hot=fire(hot, 0.3, 0.7), fang=flat(IVORY, 0.9), gold=flat(GOLD, 0.56), scale=flat(venom, 0.5, bevel=0.2), wrap=wrap(venom, venom[0], 3))
    cx = lambda t: 2.6 * math.sin(t * 6.0)  # noqa: E731
    k.forge(wave(cx, lambda t: 1.9 - 0.6 * t, 3, 18, 24), 1.8)
    x = cx(1)
    head = P((x - 1.6, 17), (x + 1.8, 17), (x + 3.0, 19.4), (x + 1.8, 23.2), (x + 0.6, 21.2), (x - 0.4, 23.6), (x - 2.6, 19.4))
    k.plate(head, 2.4, "scale")
    k.plate(P((x + 1.8, 22), (x + 2.4, 22), (x + 1.8, 25.2)) + P((x - 0.8, 22), (x - 0.1, 22), (x - 0.6, 25.8)), 0.8, "fang")
    k.plate(disc(x - 0.6, 19.8, 0.6, 6) + disc(x + 1.0, 19.8, 0.6, 6), 2.5, "hot", glow=True)
    k.plate(disc(x - 0.6, 26.8, 0.6, 6), 0.8, "hot", glow=True)
    k.plate(rect(-3.0, 1.8, 3.0, 3.2), 2.4, "gold")
    k.grip(-3.8, 1.9, 1.8)
    k.plate(stroke((0, -3.6), (3.4, -5.6), (0.4, -7.6), 1.2, 8), 1.6, "scale")


@design("shadowfang")
def shadowfang(k):
    """a kukri-backed fang of night, a void rune burning down it; where the belly should be there is a bite of nothing, the edges of the hole lit violet"""
    black = ramp("#050408", "#0c0a10", "#16121e", "#221c2e", "#322a42", "#4a3e60")
    void = ramp("#3a0a6a", "#6a1ac0", "#a050ff", "#d8b0ff", "#ffffff")
    k.mat(blade=steel(black, 0.54, 0.14), edge=honed(black, 0.95), hot=fire(void, 0.3, 0.7), iron=flat(IRON, 0.56), wrap=wrap(black, void[0], 4))
    m = P(path((-2, 3), qb((-3.0, 8), (0.0, 12), (0.4, 21), 8), (0.4, 21), qb((5.6, 17), (6.8, 11), (2.4, 3), 10)))
    hole = disc(3.0, 11.4, 1.8, 10)
    k.forge(m - hole, 1.8, ridge=-0.2)
    k.plate(disc(3.0, 11.4, 2.3, 10) - hole, 1.9, "hot", glow=True)
    k.inlay(L([(0.2, 5), (0.8, 8.4), (0.0, 11.2), (1.2, 14), (0.8, 17)], 0.5), 1.8, "hot", glow=True)
    k.plate(P((-3.4, 1.8), (3.8, 1.8), (2.8, 3.4), (-2.4, 3.4)), 2.2, "iron")
    k.grip(-3.8, 1.9, 1.9)
    k.plate(P((-1.8, -5.6), (1.8, -5.6), (0.8, -3.8), (-0.8, -3.8)), 2.2, "iron")


@design("bloodmoon_kris")
def bloodmoon_kris(k):
    """seven waves of crimson steel under a blood moon: the guard rises to one side in the old way, the disc of the moon sits behind the blade's root with a cloud across it"""
    crim = ramp("#1a0406", "#2e080c", "#460c12", "#62121a", "#801c22", "#a02a2c", "#c4443c", "#e8705c")
    moon = ramp("#7a1408", "#b02a10", "#e04a1c", "#ff8040", "#ffc080")
    k.mat(blade=steel(crim, 0.58, 0.16), edge=honed(crim, 0.92), moon=fire(moon, 0.2, 0.7), cloud=flat(ramp("#0a0608", "#1a1014", "#2e1e24"), 0.5), gold=flat(GOLD, 0.64), wrap=wrap(crim, GOLD[3], 4))
    k.plate(disc(0, 8.0, 6.2), 0.8, "moon", glow=True, z=-1.1)
    k.plate(wave(lambda t: -2.0 + 4 * t, lambda t: 0.8, 4.4, 5.4, 6), 0.5, "cloud", z=-1.5)
    k.forge(wave(lambda t: 1.7 * math.sin(t * 21.5), lambda t: 2.5 * (1 - t ** 2.2) + 0.15, 3, 24, 40), 1.6)
    k.plate(P((-3.0, 1.8), (2.0, 1.8), (3.4, 3.0), (6.0, 5.4), (5.0, 2.0), (3.2, 1.2)), 2.4, "gold")
    k.grip(-3.8, 1.9, 1.8)
    k.plate(stroke((-0.4, -3.8), (-3.6, -5.2), (-3.0, -3.0), 1.3, 6), 1.8, "gold")


@design("tunnel_rats_shiv")
def tunnel_rats_shiv(k):
    """a sharpened drill bit, the flutes still in it, a rag for a grip and a rat's tail tied on for luck"""
    fe = ramp("#1c1a18", "#2a2724", "#3a3632", "#4c4741", "#605a52", "#787066", "#928a7e")
    k.mat(iron=flat(fe, 0.66), wrap=wrap(RAG, RAG[0], 3), tail=flat(ramp("#3a2028", "#5a3038", "#7a4650", "#a06a70"), 0.6))
    n, pa, pb = 26, None, None
    for j in range(n + 1):
        a = math.radians(j * 34)
        r_ = 1.7 * (1 - (j / n) ** 2 * 0.9)
        y = 2.2 + j * 0.62
        q = (math.sin(a) * r_, y)
        q2 = (-math.sin(a) * r_, y)
        if pa:
            k.seg(pa[0], q, 1.1, 1.1, "iron", z=(pa[1] + math.cos(a) * r_) / 2)
            k.seg(pb[0], q2, 1.1, 1.1, "iron", z=(pb[1] - math.cos(a) * r_) / 2)
        pa, pb = (q, math.cos(a) * r_), (q2, -math.cos(a) * r_)
    k.box(0, 2.0, 0, 1.2, 15.6, 1.2, "iron")
    k.grip(-3.6, 2.4, 2.3)
    k.box(0, -4.6, 0, 1.8, 1.0, 1.8, "iron")
    k.plate(wave(lambda t: 1.2 + 2.4 * t + 0.8 * math.sin(t * 7), lambda t: 0.4 * (1 - t * 0.7), -4.2, -11, 12), 0.5, "tail")


@design("gillblade")
def gillblade(k):
    """a sporefolk sickle of living cap: fine gills ranked under its curve, breathing out a little light, the stem for a grip"""
    cap = ramp("#2a1a1a", "#4a2e2a", "#6e463c", "#946050", "#bc8468")
    gill = ramp("#a08a60", "#c8b080", "#e4d0a4", "#f8ecc8")
    spore = ramp("#1a6a50", "#2aa070", "#6ee0a0", "#d0ffe0")
    k.mat(blade=flat(cap, 0.6, bevel=0.1), edge=flat(cap, 0.9, bevel=0.04), gill=flat(gill, 0.6, bevel=0.06), hot=fire(spore, 0.3, 0.7), stem=staves(gill, 1.0, 0.5))
    out = qb((-1.4, 2), (-7.6, 15), (6.6, 19.6), 14)
    m = P(path(out, (6.6, 19.6), qb((-1.0, 13.6), (1.2, 8), (1.4, 2), 12)))
    k.plate(m, 2.0, "blade")
    k.plate(P(path(out, (6.6, 19.6), qb((-3.6, 14), (-1.0, 8), (0.4, 2), 12))), 2.4, "edge")
    k.plate(m - P(path(out, (6.6, 19.6), qb((-3.0, 13.8), (-0.6, 8), (0.8, 2), 12))), 2.2, "gill")
    for t, r_ in ((0.32, 0.5), (0.52, 0.6), (0.72, 0.5)):
        q = out[int(t * 14)]
        k.plate(disc(q[0] + 1.8, q[1] - 2.0, r_, 6), 2.6, "hot", glow=True)
    k.grip(-4.0, 2.4, 2.1, "stem")
    k.plate(disc(0, -5.0, 2.2, 8), 2.6, "blade")


@design("mantis_talon")
def mantis_talon(k):
    """a brood reaper's foreleg, chitin and all: a long hooked claw, double saw teeth, the thigh joint jutting back past the hand"""
    chitin = ramp("#0c0a14", "#181420", "#262034", "#362c4a", "#4a3e66", "#6a5a90")
    k.mat(blade=steel(chitin, 0.54, 0.16), edge=honed(ramp("#3a6a2a", "#5a9a3a", "#88c850", "#c0f080"), 0.7), joint=flat(chitin, 0.62, bevel=0.2), wrap=wrap(chitin, chitin[0], 4))
    m = P(path(qb((-2.0, 3), (-4.6, 19), (6.2, 22.4), 14), (6.2, 22.4), qb((0.8, 16.4), (1.8, 10), (2.0, 3), 10)))
    y = 5.0
    while y < 17:
        x = 2.0 - (y - 5) * 0.03
        m = m + P((x - 0.4, y), (x + 2.6, y + 1.0), (x - 0.5, y + 1.3)) + P((x - 0.3, y + 1.4), (x + 1.5, y + 2.0), (x - 0.5, y + 2.1))
        y += 3.0
    k.forge(m, 1.9, step=1, ridge=-0.2)
    k.plate(P((-2.6, 1.4), (2.6, 1.4), (2.0, 3.4), (-2.0, 3.4)) + P((-2.4, 3.0), (-8.0, 0.6), (-8.6, -2.0), (-3.0, 1.0)), 2.6, "joint")
    k.grip(-3.8, 1.5, 2.0)
    k.plate(disc(0, -4.8, 1.8, 8), 2.4, "joint")


@design("void_splinter")
def void_splinter(k):
    """a blade of the void, broken and refusing to accept it: five black shards hang in line along a thread of violet, the hilt holding on to them by habit"""
    black = ramp("#050408", "#0c0a10", "#16121e", "#221c2e", "#322a42", "#4a3e60")
    void = ramp("#3a0a6a", "#6a1ac0", "#a050ff", "#d8b0ff", "#ffffff")
    k.mat(blade=steel(black, 0.56, 0.16), edge=honed(black, 0.96), hot=fire(void, 0.4, 0.6), iron=flat(IRON, 0.56), wrap=wrap(black, void[1], 3))
    k.plate(L([(0, 3), (0, 27)], 0.7), 0.7, "hot", glow=True)
    for pts in (((-2.8, 3), (2.8, 3), (2.2, 7.6), (0.4, 9.0), (-2.2, 6.6)), ((-2.4, 11.2), (0.2, 9.6), (2.6, 10.6), (2.0, 13.8), (-0.8, 14.8)),
                ((-2.0, 16.8), (0.6, 15.8), (2.0, 17.4), (0.8, 20.2), (-1.4, 19.8)), ((-1.2, 22.8), (0.2, 21.6), (1.4, 23), (0.2, 25.4))):
        k.forge(P(*pts), 1.5, step=1)
    k.forge(P((-0.7, 26), (0.8, 26.6), (0.1, 31)), 1.1, step=1)
    k.plate(P((-3.4, 1.6), (3.4, 1.6), (2.6, 3.2), (-2.6, 3.2)), 2.2, "iron")
    k.grip(-3.8, 1.7, 1.9)
    k.plate(P((-1.8, -5.4), (1.8, -5.4), (0, -3.6)), 2.2, "iron")
    k.plate(disc(0, -6.8, 1.0, 6), 1.4, "hot", glow=True)


@design("twinfang")
def twinfang(k):
    """two fangs that grew from one root: a split blade, iron on one side and gold on the other, curling away from each other and back to almost touch"""
    fe = ramp("#2a2e34", "#3e444c", "#565e68", "#727c86", "#929ca6", "#b4bec6", "#d4dce2", "#f0f4f6")
    k.mat(blade=steel(fe, 0.54, 0.13), edge=honed(fe, 0.86), goldb=steel(GOLD, 0.56, 0.13), goldedge=honed(ramp("#a06018", "#d8982c", "#f6d060", "#fff0b0", "#ffffff"), 0.7), iron=flat(IRON, 0.62), gold=flat(GOLD, 0.66), hot=fire(ramp("#ffb040", "#ffe8a0", "#fffbe0", "#ffffff"), 0.4, 0.6), wrap=wrap(LEATHER, GOLD[3], 4))
    a = P(path((-0.2, 3), qb((-7.6, 6), (-6.4, 15), (-0.4, 21.6), 12), (-0.4, 21.6), qb((-3.4, 14), (-2.8, 9), (-0.2, 7.4), 8)))
    b = P(path((0.2, 3), qb((7.6, 6), (6.4, 15), (0.4, 21.6), 12), (0.4, 21.6), qb((3.4, 14), (2.8, 9), (0.2, 7.4), 8)))
    k.forge(a, 1.7, step=1)
    k.plate(b, 0.9, "goldedge", tag="edge")
    k.plate(b.inset(0.5), 1.7, "goldb", tag="blade")
    k.plate(disc(0, 12.0, 1.5, 10), 1.4, "hot", glow=True)
    k.plate(rect(-0.3, 7.4, 0.3, 11) + rect(-0.3, 13, 0.3, 21), 0.5, "hot", glow=True)
    k.plate(rect(-3.0, 1.8, 0, 3.4), 2.6, "iron")
    k.plate(rect(0, 1.8, 3.0, 3.4), 2.6, "gold")
    k.grip(-3.8, 1.9, 1.9)
    k.plate(disc(0, -5.0, 1.8, 8), 2.2, "iron")
    k.plate(disc(0.5, -5.0, 1.3, 8), 2.4, "gold")
