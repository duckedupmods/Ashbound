"""Swords: the Cellar, Gallows Hill, the Rotwood, the Crypt, the Plague Ward, the Faceless Temple, the Ossuary, the Foundry."""
import math

from voxsword import ramp
from weaponsets import design, qb, path, P, L, disc, ring, rect, wave, taper, Mask, flat, fire, heat, staves, steel, honed, bone, gem, at, lit, wrap
from weaponsets_a import BRASS, GOLD, IRON


@design("bilge_falchion")
def bilge_falchion(k):
    """a heavy chopper fished out of the bilge: a belly like a cleaver, rats' bites out of the spine, vinegar weeping
    from a crack; the guard is a stave hoop and the pommel a bung"""
    R = k.theme("cellar", base=0.46, scars=0.05)
    k.mat(hemp=wrap(R["acc"], R["dark"][1], 5))
    m = P((-2, 3), (-2, 24.5), (4.4, 27.6), (6.2, 22), (5.2, 14), (2.4, 3))
    m = m - P((-2.6, 15.4), (-0.8, 14.3), (-2.6, 13)) - P((-2.6, 19.6), (-1.1, 18.8), (-2.6, 17.6)) - P((-2.6, 10.8), (-1.2, 10.2), (-2.6, 9.4))
    k.forge(m - disc(2.8, 23.8, 0.9), 1.9, ridge=-0.35)
    k.inlay(L([(0.6, 6), (1.8, 10.4), (0.8, 14.2), (1.6, 17)], 0.6), 1.9, "glow", glow=True)
    k.box(0.2, 1.8, 0, 7.4, 1.5, 2.8, "dark")
    for s_ in (1, -1):
        k.box(0.2 + s_ * 3.3, 0.4, 0, 1.2, 1.6, 2.6, "dark")
    k.grip(-4.6, 2.0, 2.0, "hemp")
    k.box(0, -6.6, 0, 3.0, 2.0, 3.0, "wood")
    k.box(0, -5.4, 0, 3.3, 0.6, 3.3, "dark")


@design("headsmans_sword")
def headsmans_sword(k):
    """an executioner's sword: wide, parallel, no point at all, the end squared and pierced; a hand and a half of hemp
    and a plain bar. A little gibbet cut in the blade where a smith would sign"""
    R = k.theme("gallows", base=0.44, ridge=0.1)
    k.mat(hemp=wrap(R["wrap"], R["dark"][0], 5))
    m = P((-3.1, 3), (3.1, 3), (3.1, 25.4), (2.3, 27.6), (-2.3, 27.6), (-3.1, 25.4)) - disc(0, 25, 0.8)
    k.forge(m, 1.7)
    k.inlay(rect(-0.5, 5.2, 0.5, 19), 1.7, "dark")
    k.inlay(rect(-1.9, 21.2, 1.9, 21.8) + rect(-1.9, 18.2, -1.3, 21.8) + rect(0.9, 19.6, 1.3, 21.8), 1.7, "dark")
    k.box(0, 1.6, 0, 11.0, 1.5, 2.6, "dark")
    for s_ in (1, -1):
        k.box(s_ * 5.2, 1.2, 0, 1.2, 2.3, 2.9, "dark")
    k.grip(-7.2, 1.8, 2.0, "hemp")
    k.plate(disc(0, -8.6, 2.0) - disc(0, -8.6, 0.8), 2.4, "dark")


@design("hangmans_verdict")
def hangmans_verdict(k):
    """the sword is the gallows: a black post of a blade, a beam jutting from its head on a brace, and from the beam a
    hemp noose swinging with an ember burning in the knot"""
    R = k.theme("gallows", base=0.4, ridge=0.1)
    k.mat(hemp=wrap(R["wrap"], R["dark"][0], 4), rope=flat(R["acc"], 0.6))
    post = P((-2.8, 3), (2.8, 3), (2.4, 29.4), (-2.4, 33.0), (-3.0, 29))
    k.forge(post, 2.2, ridge=-0.2)
    beam = rect(1.6, 28, 11.8, 30.6) + P((11.8, 27.6), (12.8, 28.6), (12.2, 31), (11.0, 30.6))
    brace = L([(2.2, 20.5), (8.6, 28.6)], 1.5)
    k.plate(beam + brace, 2.4, "dark")
    for x, y in ((3.4, 29.3), (9.2, 29.3)):
        k.box(x, y - 0.5, 0, 1.0, 1.0, 2.7, "edge")
    k.inlay(L([(-0.3, 6), (0.7, 11), (-0.5, 16), (0.3, 21)], 0.6), 2.2, "glow", glow=True)
    # the rope, the knot, the loop
    k.box(9.4, 21.6, 0, 0.8, 6.8, 0.8, "rope")
    for j in range(4):
        k.box(9.4, 19.4 + j * 0.6, 0, 1.6, 0.6, 1.6, "hemp")
    k.plate(ring(9.4, 15.8, 3.5, 2.4), 1.2, "rope")
    k.box(9.4, 19.6, 0, 0.9, 1.0, 1.9, "glow", glow=True)
    k.box(0, 1.8, 0, 8.4, 1.5, 3.2, "dark")
    for s_ in (1, -1):
        k.plate(L([(s_ * 3.6, 2.6), (s_ * 5.2, 0.2)], 1.3), 2.6, "dark")
    k.grip(-4.8, 1.9, 2.1, "hemp")
    k.plate(P((-1.8, -5.0), (1.8, -5.0), (2.4, -8.4), (-2.4, -8.4)), 2.8, "dark")


@design("rotbranch_blade")
def rotbranch_blade(k):
    """a dead branch whittled to an edge: bark down the back, pale heartwood along the cut, twig stubs left on,
    a shelf of fungus growing out and one glowcap"""
    R = k.theme("rotwood", base=0.45)
    bark = staves(R["wood"], 1.4, 0.56)
    k.mat(blade=bark, edge=flat(R["blade"], 0.72, bevel=0.06), fungus=flat(R["acc"], 0.6), moss=flat(R["wrap"], 0.6))
    m = wave(lambda t: 1.1 * math.sin(t * 5.4) * (1 - t * 0.2), lambda t: 2.9 * (1 - t ** 2.6) + 0.1, 3, 29)
    m = m + L([(2.2, 12.5), (5.2, 15.6)], 1.2) + L([(5.2, 15.6), (5.0, 17.4)], 0.8) + L([(-2.6, 20.4), (-5.0, 22.8)], 1.1)
    k.forge(m, 2.4, step=1)
    k.plate(disc(-0.2, 9.0, 1.1, 10) - disc(-0.2, 9.0, 0.5, 8), 2.5, "dark")
    k.plate(P((1.8, 19), (6.6, 19.4), (7.0, 18.2), (2.0, 17.4)) + P((1.6, 16.8), (4.8, 17.0), (5.0, 16.0), (1.6, 15.6)), 3.2, "fungus")
    k.plate(rect(-3.8, 5.4, -2.4, 7.2) + rect(-4.2, 7.0, -2.0, 8.0), 2.0, "glow", glow=True)
    k.box(0.2, 1.8, 0, 7.4, 2.0, 3.2, "wood")
    k.box(0.2, 1.4, 0, 5.2, 0.9, 3.4, "moss")
    k.grip(-4.6, 2.0, 2.2, "wrap")
    k.plate(disc(-0.2, -6.0, 2.1, 10), 3.0, "wood")
    k.box(-1.6, -7.8, 0, 2.2, 1.2, 2.4, "moss")


@design("mosskings_briar")
def mosskings_briar(k):
    """three living briars wound together into a blade, you can see through the weave, sap burning cold between them;
    the guard is a rack of antlers and it wears the Mossking's crown at the pommel"""
    R = k.theme("rotwood", base=0.45)
    k.mat(blade=staves(R["wood"], 1.0, 0.62), edge=flat(R["wrap"], 0.7), bone=bone(R["blade"], 0.64), moss=flat(R["wrap"], 0.56))
    m = Mask()
    for ph in (0.0, 3.14):
        m = m + wave(lambda t, ph=ph: 3.3 * (1 - t * 0.8) * math.sin(t * 13 + ph), lambda t: 0.85 * (1 - t * 0.5), 3.5, 32.5, 56)
    thorns = Mask()
    for j, y in enumerate((7, 10.4, 13.6, 16.8, 19.8, 22.6, 25.2, 27.6)):
        s_ = 1 if j % 2 else -1
        x = s_ * (3.6 - j * 0.28)
        thorns = thorns + P((x - s_ * 1.4, y - 1), (x + s_ * 1.9, y + 1.6), (x - s_ * 1.2, y + 0.7))
    k.plate(m + thorns, 1.2, "edge")
    k.plate(m, 2.2, "blade")
    sap = wave(lambda t: 0.5 * math.sin(t * 7), lambda t: 0.5 * (1 - t), 4, 30, 30)
    k.plate(sap - m, 1.0, "glow", glow=True)
    for s_ in (1, -1):
        rack = L(path(qb((s_ * 1.2, 2.2), (s_ * 7.2, 2.0), (s_ * 8.0, 10.6), 8), (s_ * 8.0, 10.6)), 1.3)
        rack = rack + L([(s_ * 5.2, 3.4), (s_ * 9.6, 4.2), (s_ * 10.8, 6.6)], 0.9) + L([(s_ * 7.4, 6.6), (s_ * 10.0, 9.2)], 0.8) + L([(s_ * 6.0, 3.6), (s_ * 4.6, 7.8)], 0.8)
        k.plate(rack, 1.9, "bone")
    k.box(0, 1.2, 0, 4.4, 1.8, 3.2, "moss")
    k.box(0, 1.4, 0, 1.6, 1.3, 3.5, "glow", glow=True)
    k.grip(-4.8, 1.3, 2.1)
    k.box(0, -6.2, 0, 3.0, 1.6, 3.0, "moss")
    for x in (-1.2, 0, 1.2):
        k.plate(P((x - 0.5, -6.2), (x + 0.5, -6.2), (x, -9.4 + abs(x) * 0.7)), 1.2, "bone")


@design("vigil_sword")
def vigil_sword(k):
    """a watch-candle made a weapon: the guard is a drip pan and old wax has run down it and up the blade in pale tongues,
    a cross cut through the fuller"""
    R = k.theme("crypt", base=0.5)
    k.mat(wax=flat(R["acc"], 0.66, bevel=0.1))
    m = taper(2.3, 1.7, 3, 26, 30)
    k.forge(m, 1.6)
    k.inlay(rect(-0.4, 6, 0.4, 22) + rect(-1.3, 18.6, 1.3, 19.4), 1.6, "dark")
    wax = P((-2.8, 2.6), (2.8, 2.6), (2.8, 5.2), (2.2, 9.6), (1.6, 6), (0.8, 5.4), (0.2, 7.0), (-0.8, 5.2), (-1.8, 12.6), (-2.7, 6))
    k.plate(wax, 2.2, "wax")
    pan = P((-5.4, 1.8), (5.4, 1.8), (6.2, 3.0), (-6.2, 3.0))
    k.plate(pan, 3.4, "dark")
    k.box(-5.8, 0.2, 0, 0.9, 2.0, 0.9, "wax")
    k.box(4.8, 0.8, 0, 0.9, 1.4, 0.9, "wax")
    k.grip(-4.8, 1.9, 2.0)
    k.plate(P((-2.0, -7.6), (2.0, -7.6), (1.6, -6.0), (0.7, -4.8), (-0.7, -4.8), (-1.6, -6.0)), 2.8, "dark")
    k.box(0, -8.8, 0, 1.2, 1.3, 1.2, "acc")


@design("pale_vigil")
def pale_vigil(k):
    """the Pale Abbot's candelabrum: three lights. The blade burns at its point like a taper, and two wax-hung arms rise off
    the guard with a candle each, curled round it"""
    R = k.theme("crypt", base=0.56)
    k.mat(wax=flat(R["acc"], 0.72, bevel=0.1), flame=fire(R["glow"], 0.4, 0.6), silver=flat(R["blade"], 0.62))
    m = taper(2.4, 1.5, 3, 27, 29.2)
    k.forge(m, 1.7)
    k.inlay(L([(0, 5), (0, 26)], 0.7), 1.7, "glow", glow=True)
    flame = P(path(qb((0, 28), (-2.2, 30), (0, 34.6)), qb((0, 34.6), (2.2, 30), (0, 28))))
    k.plate(flame, 1.5, "flame", glow=True)
    k.plate(P(path(qb((0, 28.8), (-1, 30), (0, 32)), qb((0, 32), (1, 30), (0, 28.8)))), 1.7, "glow", glow=True)
    for s_ in (1, -1):
        arm = L(path(qb((s_ * 1.2, 2.4), (s_ * 8.2, 1.2), (s_ * 6.8, 11.2), 10), (s_ * 6.8, 11.2)), 1.3)
        k.plate(arm, 1.8, "silver")
        k.plate(rect(s_ * 6.8 - 1.5, 11.0, s_ * 6.8 + 1.5, 11.8), 2.8, "silver")
        k.box(s_ * 6.8, 11.8, 0, 1.9, 5.0, 1.9, "wax")
        k.box(s_ * 6.8 + s_ * 0.7, 12.0, 0, 0.7, 2.8, 2.1, "wax")
        k.plate(P(path(qb((s_ * 6.8, 16.6), (s_ * 6.8 - 1.5, 18), (s_ * 6.8, 20.2)), qb((s_ * 6.8, 20.2), (s_ * 6.8 + 1.5, 18), (s_ * 6.8, 16.6)))), 1.4, "flame", glow=True)
    k.plate(P((-2.8, 2.6), (2.8, 2.6), (2.6, 6.6), (1.4, 5.0), (0.4, 8.6), (-0.8, 5.2), (-2.6, 7.4)), 2.2, "wax")
    k.box(0, 1.4, 0, 4.6, 1.5, 3.2, "silver")
    k.grip(-4.8, 1.5, 2.0)
    k.plate(disc(0, -6.8, 2.2) - disc(0, -6.8, 1.0), 2.4, "silver")
    k.plate(disc(0, -6.8, 1.0, 10), 1.2, "glow", glow=True)


@design("plague_bonesaw")
def plague_bonesaw(k):
    """a surgeon's amputation saw at full size: a stiff brass back, a tall blade, hooked teeth down the working edge,
    one finger ring set in the guard"""
    R = k.theme("plague", base=0.54)
    teeth = []
    y = 4.0
    while y < 25.4:
        teeth += [(5.0, y), (6.6, y + 0.3), (5.0, y + 1.7)]
        y += 1.8
    m = P([(-2.2, 3), (4.6, 3)] + teeth + [(3.0, 27), (-2.2, 28.8)])
    k.forge(m, 1.4, ridge=0.3)
    k.plate(rect(-3.2, 3, -1.4, 29.4), 2.4, "dark")
    for y in (6, 13, 20, 27):
        k.box(-2.3, y, 0, 1.0, 1.0, 2.7, "edge")
    k.inlay(wave(lambda t: 2.2 + 0.4 * math.sin(t * 9), lambda t: 0.6, 8, 22, 14), 1.4, "glow", glow=True)
    k.box(0.4, 1.7, 0, 7.6, 1.5, 2.8, "dark")
    k.plate(ring(-5.0, 0.4, 2.2, 1.2), 1.4, "dark")
    k.grip(-4.8, 1.8, 2.0)
    k.box(0, -6.2, 0, 2.8, 1.5, 2.8, "dark")


@design("mercy")
def mercy(k):
    """the Ward's last kindness: a sword-sized syringe. A glass barrel of glowing cure, brass collars and scale marks, a long
    steel needle for the point; the plunger runs down through the grip and ends in a thumb ring"""
    R = k.theme("plague", base=0.56)
    k.mat(glass=flat(ramp("#2a3a34", "#4a625a", "#7e9a90", "#b4cec4", "#e4f4ec"), 0.6, bevel=0.2), brass=flat(R["dark"], 0.6))
    needle = P((-0.7, 22), (0.7, 22), (0.3, 30), (0, 34), (-0.3, 30))
    k.plate(needle, 1.2, "edge")
    k.plate(rect(-2.6, 4.6, 2.6, 21), 3.4, "glass")
    k.plate(rect(-1.9, 5.2, 1.9, 19.2), 3.5, "glow", glow=True)
    for y in (7, 9.5, 12, 14.5, 17):
        k.box(-1.6, y, 0, 1.6, 0.4, 3.6, "dark")
    k.plate(rect(-3.2, 19.8, 3.2, 22) + P((-1.4, 22), (1.4, 22), (0.8, 24), (-0.8, 24)), 4.0, "brass")
    k.plate(rect(-3.2, 3.4, 3.2, 5.0), 4.0, "brass")
    k.plate(P((-6.8, 2.2), (6.8, 2.2), (6.2, 3.6), (-6.2, 3.6)), 2.2, "brass")
    k.grip(-4.6, 2.4, 2.0)
    k.plate(rect(-0.6, -7.2, 0.6, -4.4), 1.2, "edge")
    k.plate(ring(0, -9.0, 2.5, 1.4), 1.6, "brass")


@design("faceless_blade")
def faceless_blade(k):
    """white stone with nothing on it, the blade rising from the brow of a blank mask set as the guard; one thin gold line
    is the only mark the temple allows"""
    R = k.theme("temple", base=0.72, ridge=0.08)
    k.mat(mask=flat(R["blade"], 0.86, bevel=0.06), gold=flat(R["acc"], 0.66))
    k.forge(P((-2.3, 7), (2.3, 7), (2.7, 17), (1.9, 26), (0, 30.5), (-1.9, 26), (-2.7, 17)), 1.6)
    k.inlay(L([(0, 8), (0, 27)], 0.4), 1.6, "gold")
    mask = P(path(qb((-4.0, 6.2), (-4.4, 0.8), (0, -0.4)), qb((0, -0.4), (4.4, 0.8), (4.0, 6.2)), qb((4.0, 6.2), (0, 9.2), (-4.0, 6.2))))
    k.plate(mask, 2.4, "mask")
    k.inlay(rect(-2.8, 3.8, -0.7, 4.3) + rect(0.7, 3.8, 2.8, 4.3), 2.4, "dark")
    k.grip(-4.8, 0.0, 2.0)
    k.box(0, -6.0, 0, 2.6, 1.3, 2.6, "gold")
    k.box(0, -7.2, 0, 1.4, 1.2, 1.4, "glow", glow=True)


@design("sovereigns_edge")
def sovereigns_edge(k):
    """the crown of a king nobody remembers: a great white blade, gold down both shoulders, mana crystal grown up its middle;
    the guard is a spiked crown round the blade and a blank mask stares from the pommel"""
    R = k.theme("temple", base=0.68, ridge=0.1)
    k.mat(mask=flat(R["blade"], 0.84, bevel=0.06), gold=flat(R["acc"], 0.62, bevel=0.14), edge=honed(R["acc"], 0.82))
    m = P((-3.6, 4), (3.6, 4), (4.2, 12), (3.0, 27), (0, 34), (-3.0, 27), (-4.2, 12))
    k.forge(m, 2.0)
    k.plate(P((-1.1, 7), (1.1, 7), (1.3, 19), (0, 27), (-1.3, 19)), 2.3, "glow", glow=True)
    crown = P((-7.2, 1.6), (7.2, 1.6), (8.6, 9.4), (6.2, 5.2), (4.8, 10.6), (3.4, 5.0), (0, 8.0), (-3.4, 5.0), (-4.8, 10.6), (-6.2, 5.2), (-8.6, 9.4))
    k.plate(crown - rect(-2.2, 5.0, 2.2, 12), 3.2, "gold")
    for x in (-5, 0, 5):
        k.plate(disc(x, 3.3, 0.9, 8), 3.5, "glow", glow=True)
    k.grip(-4.8, 1.7, 2.2)
    mask = P(path(qb((-2.4, -5.0), (-2.8, -9.4), (0, -10.4)), qb((0, -10.4), (2.8, -9.4), (2.4, -5.0))))
    k.plate(mask, 2.6, "mask")
    k.inlay(rect(-1.8, -7.2, -0.5, -6.8) + rect(0.5, -7.2, 1.8, -6.8), 2.6, "dark")


@design("bonewright_blade")
def bonewright_blade(k):
    """a spine: twelve vertebrae threaded on an iron rod and riveted, each with its own wings, the last one filed to a point"""
    R = k.theme("ossuary", base=0.5)
    k.mat(bone=bone(R["acc"], 0.66), brass=flat(R["dark"], 0.62), wing=flat(R["acc"], 0.72, bevel=0.1))
    n = 11
    for j in range(n):
        y = 3.6 + j * 2.25
        w = 3.1 - j * 0.16
        k.plate(rect(-w, y, w, y + 1.8), 2.8, "bone")
        k.plate(P((-w, y + 1.8), (-w - 1.5, y + 2.2), (-w - 0.9, y + 0.4), (-w, y)), 1.6, "wing")
        k.plate(P((w, y + 1.8), (w + 1.5, y + 2.2), (w + 0.9, y + 0.4), (w, y)), 1.6, "wing")
        k.box(0, y + 1.7, 0, w * 1.5, 0.6, 1.8, "dark")
    k.plate(P((-1.5, 28.2), (1.5, 28.2), (0, 33.4)), 2.2, "bone")
    k.box(0, 2.0, 0, 7.6, 1.6, 3.2, "brass")
    k.grip(-4.8, 2.0, 2.0)
    k.plate(disc(0, -6.8, 2.2), 2.6, "bone")
    k.plate(disc(-0.8, -6.5, 0.6, 8) + disc(0.8, -6.5, 0.6, 8), 2.7, "glow", glow=True)


@design("engine_blade")
def engine_blade(k):
    """a sword-engine: a chain of saw teeth runs round a long bar, soul fire behind a window in its root, a cog for a guard
    and a piston driving it from beside the grip"""
    R = k.theme("ossuary", base=0.46)
    k.mat(brass=flat(R["dark"], 0.62), chain=flat(R["blade"], 0.78), bar=steel(R["blade"], 0.4, 0.08))
    bar = P((-2.9, 6), (2.9, 6), (2.9, 26), (1.6, 28.6), (-1.6, 28.6), (-2.9, 26))
    teeth = Mask()
    y = 7.0
    while y < 26:
        for s_ in (1, -1):
            teeth = teeth + P((s_ * 2.7, y), (s_ * 4.6, y + 0.3), (s_ * 2.7, y + 1.6))
        y += 2.1
    for x in (-1.4, 0.8):
        teeth = teeth + P((x, 28.2), (x + 0.8, 30.4), (x + 1.6, 28.2))
    k.plate(teeth, 1.0, "chain")
    k.plate(bar, 1.5, "chain")
    k.plate(bar.inset(0.7), 2.2, "bar", tag="blade")
    k.plate(rect(-1.2, 8.4, 1.2, 15), 2.26, "glow", glow=True)
    k.inlay(rect(-1.3, 10.4, 1.3, 10.9) + rect(-1.3, 12.8, 1.3, 13.3), 2.26, "dark")
    for j in range(10):
        a = j * math.pi / 5
        k.box(math.cos(a) * 5.4, 4.0 + math.sin(a) * 5.4 - 0.7, 0, 1.6, 1.6, 2.2, "brass", rots=(("z", math.degrees(a)),), pivot=(math.cos(a) * 5.4, 4.0 + math.sin(a) * 5.4, 0))
    k.plate(disc(0, 4, 5.0), 2.2, "brass")
    k.plate(disc(0, 4, 2.2) - disc(0, 4, 1.2), 2.5, "bar")
    k.box(-3.0, -4.0, 0, 1.0, 5.4, 1.0, "chain")
    k.box(-3.0, -5.2, 0, 1.8, 2.4, 1.8, "brass")
    k.plate(L([(-3.0, -5.0), (-0.8, -6.2)], 0.9), 1.2, "brass")
    k.grip(-5.2, 0.0, 2.2)
    k.plate(rect(-2.0, -7.6, 2.0, -5.2), 2.8, "brass")


@design("kiln_blade")
def kiln_blade(k):
    """cast, not forged: a wedge of iron with cooling fins cut down its spine like a stove's, a seam along it that never
    went cold and square rivet heads where the sprue was cut off"""
    R = k.theme("foundry", base=0.46, ridge=0.08)
    k.mat(edge=honed(ramp("#2a2622", "#4a433c", "#6e665c", "#9c9286", "#cabeae", "#efe4d4"), 0.76))
    m = P((-2.4, 3), (3.4, 3), (4.0, 22), (1.0, 29.6), (-2.4, 26))
    fins = Mask()
    y = 6.0
    while y < 24:
        fins = fins + rect(-4.6, y, -2.0, y + 1.1)
        y += 2.1
    k.forge(m, 2.2, ridge=-0.4)
    k.plate(fins, 2.0, "dark")
    k.inlay(L([(1.2, 5), (1.6, 13), (1.0, 18), (1.3, 24)], 0.7), 2.2, "glow", glow=True)
    for y in (6.5, 12.5, 18.5):
        k.box(-0.8, y, 0, 1.0, 1.0, 2.6, "dark")
    k.plate(P((-5.0, 1.6), (6.0, 1.6), (6.8, 3.2), (-5.4, 3.2)), 3.0, "dark")
    k.grip(-4.8, 1.7, 2.2)
    k.box(0, -6.8, 0, 3.2, 2.2, 3.2, "dark")
    k.box(0, -6.0, 0, 1.2, 1.2, 3.4, "glow", glow=True)
