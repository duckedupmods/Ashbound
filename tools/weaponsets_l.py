"""White magic staffs: the healers. Warm light, kind objects, and a few that are mercy of a harder sort."""
import math

from voxsword import ramp
from weaponsets import design, qb, path, P, L, disc, ring, rect, wave, flat, fire, staves, bone, wrap, stripes
from weaponsets_a import BRASS, GOLD, IRON, LEATHER
from weaponsets_c import shard
from weaponsets_d import RUBY, SILVER, links, stroke
from weaponsets_e import CORK, IVORY, RAG
from weaponsets_k import pole, orb, HOT, TEAL, FE

WARM = ramp("#c08a2a", "#e8b84a", "#ffdc7a", "#fff0b0", "#fffbe8")
HOLY = ramp("#d8c8a0", "#f0e4c0", "#fff6dc", "#ffffff")
PALE = ramp("#6a6458", "#8e8878", "#b4ae9c", "#d6d0be", "#efeadb")
BIRCH = ramp("#7a7264", "#a09888", "#c6bead", "#e6dfd0", "#f6f0e4")


def lantern(k, y, w, h, frame, light, cap=None):
    """a square lantern: four corner posts, a light in it, a roof and a ring"""
    orb(k, 0, y + h / 2, min(w, h) / 2 - 0.7, light)
    for x, z in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        k.box(x * w / 2, y, z * w / 2, 0.9, h, 0.9, frame)
    k.box(0, y - 1.0, 0, w + 1.4, 1.2, w + 1.4, frame)
    k.box(0, y + h, 0, w + 1.4, 1.0, w + 1.4, frame)
    k.plate(P((-w / 2 - 0.6, y + h + 1), (w / 2 + 0.6, y + h + 1), (0, y + h + 4.2)), w * 0.9, cap or frame)
    k.plate(ring(0, y + h + 5, 1.4, 0.7), 0.7, frame)


def hook(k, top, r_, mat, w=1.2):
    """a shepherd's crook curling off the top of the pole"""
    k.plate(stroke((0, top), (0, top + r_ * 2.0), (r_ * 1.6, top + r_ * 1.5), w, 8), 1.6, mat)
    k.plate(stroke((r_ * 1.6, top + r_ * 1.5), (r_ * 2.5, top + r_ * 0.8), (r_ * 2.2, top), w, 6), 1.6, mat)


@design("mothers_ladle")
def mothers_ladle(k):
    """the Cask Mother's great kitchen ladle, the bowl still full and steaming, soup that mends you"""
    R = k.theme("cellar")
    k.mat(tin=flat(FE, 0.66, bevel=0.14), broth=fire(WARM, 0.2, 0.7), oak=staves(R["wood"], 1.0, 0.6))
    pole(k, 20, "oak")
    k.box(0, 20, 0, 1.6, 7, 1.0, "tin")
    k.plate(P(path(qb((-7, 33), (-7, 26), (0, 25.6), 8), qb((0, 25.6), (7, 26), (7, 33), 8))), 8.0, "tin")
    k.box(0, 32.4, 0, 12.6, 0.8, 6.6, "broth", glow=True)
    for x in (-3, 2.6):
        k.plate(wave(lambda t, x=x: x + math.sin(t * 7), lambda t: 0.7 - 0.4 * t, 33.4, 39, 8), 0.5, "tin")


@design("last_rites")
def last_rites(k):
    """a noose of white cord tied into a wreath of lilies: the Gallows' one kind thing"""
    R = k.theme("gallows")
    k.mat(cord=wrap(PALE, PALE[1], 3), lily=flat(BIRCH, 0.86, bevel=0.1), ash=staves(R["wood"], 1.0, 0.6), hot=flat(WARM, 0.7))
    pole(k, 18, "ash")
    k.plate(ring(0, 26.6, 7.6, 5.8), 1.8, "cord")
    k.box(0, 17.4, 0, 2.8, 2.4, 2.8, "cord")
    k.plate(stroke((0, 19.6), (0.6, 19.6), (0, 19.8), 1.2), 1.4, "cord")
    for j in range(6):
        a = j * math.pi / 3 + 0.4
        x, y = math.cos(a) * 6.8, 26.6 + math.sin(a) * 6.8
        for b in (0, 2.1, 4.2):
            k.plate(P((x, y), (x + math.cos(a + b) * 3.2 - math.sin(a + b), y + math.sin(a + b) * 3.2 + math.cos(a + b)), (x + math.cos(a + b) * 3.2 + math.sin(a + b), y + math.sin(a + b) * 3.2 - math.cos(a + b))), 1.2, "lily", z=0.6)
        k.plate(disc(x, y, 0.8, 6), 1.5, "hot", glow=True, z=0.6)


@design("mossheart")
def mossheart(k):
    """a living staff in new leaf, a heart of green moss at the head with a warm pulse under it"""
    R = k.theme("rotwood")
    k.mat(moss=flat(ramp("#1e4a1e", "#2e6a26", "#46902e", "#68b43c"), 0.62, 0.3, bevel=0.1), bark=staves(R["wood"], 1.0, 0.6), leaf=flat(ramp("#2e6a26", "#46902e", "#7cc844"), 0.7), hot=fire(WARM, 0.3, 0.6))
    pole(k, 18, "bark")
    m = disc(-3, 26.4, 4.2, 12) + disc(3, 26.4, 4.2, 12) + P((-7, 25), (7, 25), (0, 17))
    k.plate(m, 5.0, "moss")
    k.plate(m.inset(2.8), 5.3, "hot", glow=True)
    for x, y, a, s_ in ((-7, 28, 150, 3.4), (7, 28, 30, 3.4), (0, 31, 90, 3.0), (-5, 19, 200, 2.6), (5, 19, -20, 2.6)):
        r_ = math.radians(a)
        d = (math.cos(r_) * s_, math.sin(r_) * s_)
        k.plate(P((x, y), (x + d[0] * 0.5 - d[1] * 0.3, y + d[1] * 0.5 + d[0] * 0.3), (x + d[0], y + d[1]), (x + d[0] * 0.5 + d[1] * 0.3, y + d[1] * 0.5 - d[0] * 0.3)), 0.8, "leaf")


@design("mosscrown")
def mosscrown(k):
    """a ring of stag-horn antler gone green, a little tree growing in the middle of it, fruit like lamps"""
    R = k.theme("rotwood")
    k.mat(ant=bone(ramp("#4a3e2a", "#6a5a3e", "#8c7a58", "#b0a07c"), 0.7), moss=flat(ramp("#2e6a26", "#46902e", "#68b43c"), 0.6, 0.2), bark=staves(R["wood"], 1.0, 0.6), hot=fire(WARM, 0.3, 0.7))
    pole(k, 17, "bark")
    for s_ in (1, -1):
        k.plate(stroke((0, 17), (s_ * 13, 18), (s_ * 9, 33), 1.4), 2.0, "ant")
        k.plate(stroke((s_ * 8.4, 21), (s_ * 12, 24), (s_ * 15, 27), 0.9), 1.4, "ant")
        k.plate(stroke((s_ * 10.6, 27), (s_ * 13, 30), (s_ * 13.4, 33), 0.8), 1.4, "ant")
    k.plate(stroke((0, 17), (0.6, 21), (0, 25), 1.0) + stroke((0, 22), (-3, 24), (-4, 27), 0.6) + stroke((0, 23), (3, 25), (4, 28), 0.6), 1.2, "ant")
    k.plate(disc(0, 28, 3.6, 10) + disc(-3.6, 29, 2.6, 8) + disc(3.6, 30, 2.6, 8), 3.0, "moss")
    for x, y in ((-3.4, 27.4), (0, 31), (3.4, 28.4)):
        k.plate(disc(x, y, 1.0, 7), 3.2, "hot", glow=True)


@design("censer_of_rest")
def censer_of_rest(k):
    """a wax-sealed censer on three chains, sweet white smoke rolling off it to bring you sleep"""
    R = k.theme("crypt")
    k.mat(silver=flat(SILVER, 0.68, bevel=0.14), wax=flat(R["acc"], 0.74, bevel=0.1), smoke=flat(PALE, 0.5))
    pole(k, 29, "silver")
    k.plate(stroke((0, 29), (6, 32.6), (9, 29), 1.1), 1.4, "silver")
    links(k, [(9, 28.4), (9, 26.8), (9, 25.2), (9, 23.6)], "silver", 0.6)
    k.plate(P((5, 23), (13, 23), (14, 19), (12, 15), (6, 15), (4, 19)), 7.0, "silver")
    k.plate(P((5, 19.4), (13, 19.4), (13.4, 17.4), (4.6, 17.4)), 7.2, "wax")
    k.plate(disc(9, 21, 0.9, 6) + disc(6.6, 21, 0.7, 6) + disc(11.4, 21, 0.7, 6), 7.2, "glow", glow=True)
    k.plate(wave(lambda t: 11 + 4 * t + 1.1 * math.sin(t * 6), lambda t: 1.0 - 0.5 * t, 23.4, 37, 10), 0.8, "smoke")
    k.plate(wave(lambda t: 6 - 1 * t + math.sin(t * 7), lambda t: 0.7 - 0.3 * t, 23.4, 32, 9), 0.8, "smoke")


@design("limelight_staff")
def limelight_staff(k):
    """a plague doctor's lamp, green glass and a brass beak, burning clean quicklime: the light kills the sickness it falls on"""
    R = k.theme("plague")
    k.mat(brass=flat(BRASS, 0.64, bevel=0.14), cane=flat(R["acc"], 0.56), light=fire(ramp("#7ec41e", "#b4e848", "#e4ffa0", "#ffffff"), 0.3, 0.7))
    pole(k, 16, "cane", shoe="brass")
    lantern(k, 18, 7.0, 8.4, "brass", "light")
    k.plate(P((3.6, 30), (3.6, 27), (11, 25)), 3.0, "brass")


@design("lampbearer")
def lampbearer(k):
    """Hospice's lamp, carried by the Ward's last nurse: a tall thin light in a cage of bent surgical steel, a linen bandage trailing from it"""
    R = k.theme("plague")
    k.mat(steel=flat(FE, 0.76, bevel=0.14), lint=flat(PALE, 0.86), light=fire(HOLY, 0.3, 0.7), cane=flat(R["acc"], 0.6))
    pole(k, 15, "steel", shoe="steel")
    for s_ in (1, -1):
        k.plate(stroke((s_ * 0.6, 15), (s_ * 8.4, 20), (s_ * 0.6, 34), 0.9, 12), 1.2, "steel")
        k.plate(stroke((s_ * 0.6, 15), (s_ * 4.4, 20), (s_ * 0.6, 34), 0.6, 12), 1.0, "steel")
    orb(k, 0, 24, 2.8, "light")
    k.plate(P((-0.9, 28), (0.9, 28), (0, 34)), 1.2, "light", glow=True)
    k.plate(wave(lambda t: 3 + 5 * t + math.sin(t * 8), lambda t: 0.9, 16, -2, 12), 0.4, "lint")


@design("veilhealer")
def veilhealer(k):
    """a faceless white mask on a staff, a veil of soft light falling from it and hiding the hand that carries it"""
    R = k.theme("temple", base=0.7)
    k.mat(mask=flat(BIRCH, 0.86, bevel=0.14), veil=flat(ramp("#7ea6c0", "#a8c8dc", "#cce2ee"), 0.4), gold=flat(GOLD, 0.66), rod=flat(R["blade"], 0.72))
    pole(k, 18, "rod", shoe="gold")
    k.plate(P(path(qb((-6, 31), (-7, 21), (0, 17), 8), qb((0, 17), (7, 21), (6, 31), 8), qb((3, 34.6), (-3, 34.6), (-6, 31), 6))), 4.0, "mask")
    k.plate(rect(-3.4, 24.6, 3.4, 25.2), 4.1, "glow", glow=True)
    for x in (-5, -1.6, 1.6, 5):
        k.plate(wave(lambda t, x=x: x + 0.7 * math.sin(t * 6 + x) + x * 0.3 * t, lambda t: 0.8, 21, 7, 10), 0.4, "veil", z=-1.4)
    k.plate(rect(-6.4, 20.6, 6.4, 21.4), 3.8, "gold")


@design("hymn_staff")
def hymn_staff(k):
    """a bone flute, tall as a staff, with a little reed head that sings on its own in the wind, warm notes hanging in the air"""
    R = k.theme("ossuary")
    k.mat(bone=bone(R["acc"], 0.7), brass=flat(BRASS, 0.64), hot=flat(WARM, 0.8))
    pole(k, 28, "bone", 2.6, grip="brass", shoe="brass")
    k.plate(P((-2.2, 28), (2.2, 28), (1.4, 34), (-1.4, 34)), 2.4, "bone")
    k.plate(rect(-0.7, 28.4, 0.7, 29.2), 2.6, "dark")
    for y in (8, 12, 16, 20, 24):
        k.plate(disc(0, y, 0.7, 6), 2.8, "dark")
    for x, y in ((5, 30), (8, 27), (6.4, 23)):
        k.plate(disc(x, y, 1.0, 7) + rect(x + 0.6, y, x + 1.0, y + 3.4), 0.5, "hot", glow=True)
        k.plate(P((x + 1, y + 3.4), (x + 2.8, y + 2.2), (x + 1, y + 2.6)), 0.5, "hot", glow=True)


@design("hearth_staff")
def hearth_staff(k):
    """a blacksmith's own hearth in small: a brick well, a kind low fire, a kettle hook, a place to get warm"""
    R = k.theme("foundry")
    k.mat(brick=flat(ramp("#3a1a10", "#5a2a18", "#7a3c22", "#9c5230"), 0.62, bevel=0.1), mort=flat(ramp("#2a2420", "#3e362e"), 0.5), flame=fire(WARM, 0.1, 0.9), hot=flat(HOT, 0.7), iron=flat(IRON, 0.6))
    pole(k, 15, "iron")
    for j, y in enumerate((15, 17.4, 19.8, 22.2)):
        k.box(0, y, 0, 13 - (j == 3) * 0, 2.2, 8.4, "brick")
        k.box(0, y + 2.0, 0, 13.2, 0.4, 8.6, "mort")
    k.box(0, 17.4, 2, 7.0, 5.0, 5.6, "hot", glow=True)
    k.plate(P((-3, 24.4), (3, 24.4), (1.6, 30), (0.4, 28), (0, 33), (-1.6, 28.6)), 1.8, "flame", glow=True)
    k.plate(stroke((-6, 24.4), (-7, 34), (2, 34.6), 0.8), 1.0, "iron")


@design("thaw_staff")
def thaw_staff(k):
    """ice over the first flower of spring: the crystal is melting from inside and the bud is alive in it"""
    R = k.theme("frost", base=0.54)
    k.mat(ice=flat(R["glow"], 0.62, bevel=0.14), pet=flat(ramp("#c86a8a", "#e8a0b8", "#ffd4e0"), 0.74, bevel=0.06), stem=flat(ramp("#2e6a26", "#46902e", "#68b43c"), 0.66), iron=flat(R["dark"], 0.62), hot=flat(WARM, 0.8))
    pole(k, 15, "iron")
    k.plate(P((-6.4, 16), (6.4, 16), (8, 24), (4, 33), (0, 36), (-4, 33), (-8, 24)), 5.4, "ice")
    k.plate(stroke((0, 16), (1, 20), (0, 24), 0.6), 5.8, "stem")
    for a in (-60, -20, 20, 60):
        r_ = math.radians(a + 90)
        k.plate(P((0, 24), (math.cos(r_ + 0.34) * 4, 24 + math.sin(r_ + 0.34) * 4), (math.cos(r_) * 6.4, 24 + math.sin(r_) * 6.4), (math.cos(r_ - 0.34) * 4, 24 + math.sin(r_ - 0.34) * 4)), 5.8, "pet")
    k.plate(disc(0, 25.4, 0.9, 7), 6.0, "hot", glow=True)
    k.plate(wave(lambda t: 7.6 + 0.3 * math.sin(t * 6), lambda t: 0.5 - 0.2 * t, 22, 9, 8), 0.5, "ice")


@design("last_ember")
def last_ember(k):
    """the Frost Keep's last coal, kept all through the long winter in a little iron house under glass"""
    R = k.theme("frost", base=0.54)
    k.mat(iron=flat(R["dark"], 0.62, bevel=0.1), coal=fire(HOT, 0.3, 0.7), glass=flat(ramp("#6a8aa0", "#94b4c8", "#c0dae8"), 0.5, bevel=0.2), rim=flat(R["glow"], 0.8), hot=flat(WARM, 0.8))
    pole(k, 15, "iron")
    k.plate(P((-7, 15.6), (7, 15.6), (7.6, 24), (0, 29.6), (-7.6, 24)), 2.4, "iron")
    k.plate(P((-5, 17), (5, 17), (5.4, 23.4), (0, 27.6), (-5.4, 23.4)), 2.8, "glass")
    orb(k, 0, 21.4, 3.2, "coal")
    k.plate(P((-9.4, 24.4), (0, 31.4), (9.4, 24.4), (9.4, 26.4), (0, 33.6), (-9.4, 26.4)), 4.6, "rim")
    k.plate(P((-3, 33), (3, 33), (0, 37.6)), 2.4, "rim")


@design("mending_spool")
def mending_spool(k):
    """a giant bobbin wound with golden thread, the free end flying off to stitch up whatever's broken"""
    R = k.theme("silk")
    k.mat(oak=flat(R["wood"], 0.66, bevel=0.1), thr=wrap(GOLD, GOLD[3], 2), needle=flat(SILVER, 0.8), hot=fire(WARM, 0.3, 0.7))
    pole(k, 16, "oak")
    k.box(0, 16, 0, 11, 1.8, 11, "oak")
    k.box(0, 29, 0, 11, 1.8, 11, "oak")
    k.box(0, 17.8, 0, 8.4, 11.2, 8.4, "thr")
    k.plate(wave(lambda t: 6 + 6 * t + 1.6 * math.sin(t * 9), lambda t: 0.35, 26, 8, 16), 0.5, "hot", glow=True)
    k.plate(L([(11.8, 9), (13.4, 3)], 0.5), 0.5, "needle")
    k.plate(ring(11.8, 9.4, 0.8, 0.4), 0.5, "needle")


@design("weeping_lantern")
def weeping_lantern(k):
    """a miner's safety lamp the Mine's teal water has been dripping on for a hundred years, a slow bright tear forming at its foot"""
    R = k.theme("weeping_mine")
    k.mat(brass=flat(BRASS, 0.64, bevel=0.14), bluegreen=flat(ramp("#1a5a54", "#2a8078", "#3ea89e"), 0.6, 0.3), oak=staves(R["wood"], 1.0, 0.6), light=fire(TEAL, 0.3, 0.7))
    pole(k, 16, "oak")
    lantern(k, 18, 7.0, 7.6, "brass", "light", "bluegreen")
    k.plate(P(path(qb((5, 16.6), (6.2, 13), (5, 11.6), 4), qb((5, 11.6), (3.8, 13), (5, 16.6), 4))), 1.0, "light", glow=True)
    k.plate(rect(4.6, 15.8, 5.4, 17.6), 1.0, "bluegreen")
    k.plate(P((-4.4, 25.6), (-3, 25.6), (-3.2, 22), (-4, 21)), 8.2, "bluegreen")


@design("chapel_lamp")
def chapel_lamp(k):
    """the drowned chapel's sanctuary lamp, sea-green glass on a tide-worn crook, its flame burning quite calmly underwater"""
    R = k.theme("tide_chapel")
    k.mat(drift=staves(R["wood"], 1.0, 0.6), brass=flat(ramp("#1e4a44", "#2e6a5e", "#46907e", "#6cb49e"), 0.62, bevel=0.14), glass=flat(ramp("#1a6a5e", "#2a9080", "#5cc4b0"), 0.6, bevel=0.2), flame=fire(WARM, 0.1, 0.9))
    pole(k, 22, "drift")
    hook(k, 22, 4.6, "drift", 1.4)
    k.plate(stroke((10.2, 22), (10.4, 21), (10.2, 20), 0.5), 0.5, "brass")
    k.plate(P((5.6, 20), (14.8, 20), (13.4, 13), (7, 13)), 7.0, "glass")
    k.plate(rect(5, 19, 15.4, 20.4) + rect(6.4, 12.4, 14, 13.4), 7.2, "brass")
    k.plate(P(path(qb((10.2, 14), (8, 16), (10.2, 19.6), 6), qb((10.2, 19.6), (12.4, 16), (10.2, 14), 6))), 7.4, "flame", glow=True)
    k.plate(disc(5, 21, 0.5, 5) + disc(3.6, 16.6, 0.4, 5), 0.5, "glass")


@design("bellringer")
def bellringer(k):
    """the Chapel's small bell that rings the drowned home, barnacled, its rope still wet, a soft light swinging in it for a clapper"""
    R = k.theme("tide_chapel")
    k.mat(bronze=flat(ramp("#1e4a44", "#2e6a5e", "#46907e", "#6cb49e", "#94d4bc"), 0.64, bevel=0.14), barn=flat(PALE, 0.7), rope=wrap(RAG, RAG[0], 3), drift=staves(R["wood"], 1.0, 0.6), light=fire(WARM, 0.3, 0.7))
    pole(k, 24, "drift")
    k.box(0, 24, 0, 12, 1.2, 2.0, "drift")
    for j, (w, y) in enumerate(((3.4, 22.6), (5, 20.8), (6.6, 19), (8.4, 17.2), (10, 15.4), (12.4, 14.0))):
        k.box(0, y, 0, w, 1.9, w, "bronze")
    orb(k, 0, 12.6, 1.8, "light")
    k.box(4.4, 15, 3.2, 1.2, 1.2, 1.2, "barn")
    k.box(-3, 17.4, 2.8, 1.4, 1.0, 1.0, "barn")
    k.plate(wave(lambda t: 5.4 + 1.0 * math.sin(t * 6), lambda t: 0.4, 24, 8, 8), 0.6, "rope")


@design("poultice_staff")
def poultice_staff(k):
    """a field medic's stave with herb bundles hung to dry and a mortar lashed at the top, the pestle still in it"""
    R = k.theme("brigands_gorge")
    k.mat(stone=flat(ramp("#6a6458", "#8e8878", "#b4ae9c"), 0.6, bevel=0.14), herb=flat(ramp("#2e5a22", "#46802e", "#68a83c"), 0.66, 0.3), cord=flat(R["acc"], 0.6), oak=staves(R["wood"], 1.0, 0.6), balm=fire(ramp("#68a83c", "#a4d868", "#e0ffa0"), 0.3, 0.7))
    pole(k, 22, "oak")
    k.plate(P((-6, 30), (6, 30), (4.4, 22), (-4.4, 22)), 7.0, "stone")
    k.box(0, 29.8, 0, 10.4, 0.6, 5.6, "balm", glow=True)
    k.box(0, 20, 0, 3.4, 2.4, 3.4, "cord")
    k.plate(L([(1, 29), (5, 37)], 1.0), 1.4, "stone")
    k.plate(disc(5, 37, 1.3, 8), 1.6, "stone")
    for x, y in ((-3.4, 18.6), (3.4, 16.6)):
        k.box(x, y, 0, 0.3, 19.6 - y + 1, 0.3, "cord")
        k.plate(P((x - 0.8, y), (x + 0.8, y), (x + 1.8, y - 5.4), (x, y - 6.4), (x - 1.8, y - 5.4)), 1.4, "herb")
    k.box(0, 19.2, 0, 7.6, 0.6, 0.7, "cord")


@design("carrion_mercy")
def carrion_mercy(k):
    """a vulture's wing bound to a staff, the feathers grey and gentle, a little white flame in a bird's breastbone: death cleaning up after itself"""
    R = k.theme("rookery")
    k.mat(fe=flat(ramp("#2e2c30", "#46424a", "#605c66", "#7c7884"), 0.6, 0.2, bevel=0.1), bone=bone(IVORY, 0.72), flame=fire(HOLY, 0.2, 0.8), oak=flat(R["wood"], 0.6))
    pole(k, 18, "oak")
    for j in range(7):
        a = math.radians(100 - j * 18)
        x0, y0 = 1 + j * 1.0, 19 + j * 1.2
        ln = 15 - j * 0.8
        tip = (x0 + math.cos(a) * ln, y0 + math.sin(a) * ln)
        k.plate(P((x0 - 1.4, y0), (x0 + 1.4, y0 - 0.6), (tip[0] + 1.2, tip[1] - 0.6), tip), 1.2, "fe", z=j * 0.3)
    k.plate(P((-1, 16), (1, 16), (0.6, 27), (-5, 30), (-6, 26), (-1, 24)), 1.8, "bone")
    k.plate(P(path(qb((-3, 26), (-5.4, 30), (-3, 35), 6), qb((-3, 35), (-1, 30), (-3, 26), 6))), 1.2, "flame", glow=True)


@design("applause_staff")
def applause_staff(k):
    """a ringmaster's kindness: two gloved wooden hands on a stick that clap by themselves, a rain of gold confetti coming off them"""
    R = k.theme("hollow_circus")
    red = ramp("#2a0408", "#4e0810", "#7a1018", "#a81c20", "#d0302a")
    cream = ramp("#8e7c60", "#b4a282", "#d6c8a8", "#efe4c8")
    k.mat(st=stripes(red, cream, 3.0, 0.5), glove=flat(BIRCH, 0.8, bevel=0.1), gold=flat(GOLD, 0.8), hot=flat(WARM, 0.9))
    pole(k, 16, "st", shoe="gold")
    for s_ in (1, -1):
        k.plate(P((0, 16), (s_ * 1.8, 17), (s_ * 1.8, 24), (s_ * 7, 33), (s_ * 5.6, 35), (s_ * 3.4, 31.6), (s_ * 3.4, 36), (s_ * 1.6, 36), (s_ * 0.8, 30), (0, 24)), 2.4, "glove")
        k.plate(P((s_ * 1.8, 22), (s_ * 7, 22), (s_ * 7.4, 25), (s_ * 2.6, 26)), 1.6, "glove")
    for x, y, c in ((-6, 40, "gold"), (-1, 39, "hot"), (5, 41, "gold"), (9, 34, "hot"), (-10, 33, "gold"), (2, 44, "hot")):
        k.box(x, y, 0, 1.0, 1.0, 0.5, c, glow=c == "hot")


@design("swamp_lantern")
def swamp_lantern(k):
    """a marsh-light caught in a jar and hung off a bent reed, the warm light a traveller follows the right way, for once"""
    R = k.theme("mirefen_coven")
    k.mat(reed=flat(ramp("#3a4a1e", "#58702c", "#7c9a3c"), 0.62, bevel=0.06), glass=flat(ramp("#3e5a4a", "#5e8068", "#88a88c"), 0.5, bevel=0.2), cork=flat(CORK, 0.7), light=fire(ramp("#7ec44a", "#b4e878", "#e4ffc0", "#ffffff"), 0.3, 0.7), cord=flat(R["acc"], 0.6))
    pole(k, 23, "reed")
    k.plate(stroke((0, 23), (1, 33), (10, 29), 1.0, 12), 1.3, "reed")
    k.box(10, 24, 0, 0.3, 5, 0.3, "cord")
    k.plate(P((6, 23), (14, 23), (14.4, 13), (5.6, 13)), 7.0, "glass")
    k.plate(rect(6.6, 23, 13.4, 25), 3.0, "cork")
    k.plate(disc(10, 18, 3.4, 14), 7.4, "light", glow=True)


@design("ankh_staff")
def ankh_staff(k):
    """a tall gold ankh, the loop full of light, lapis banded at the waist: the Tomb's own word for life"""
    k.theme("sandsunk_tomb")
    k.mat(gold=flat(GOLD, 0.68, bevel=0.14), lapis=flat(ramp("#0e2a6e", "#163e96", "#2458c0", "#3a74dc"), 0.7), light=fire(WARM, 0.3, 0.7))
    pole(k, 18, "gold", 2.2, grip="lapis", shoe="lapis")
    k.plate(rect(-9, 18, 9, 21.6), 2.4, "gold")
    m = P(path(qb((-1.6, 21), (-9, 28), (0, 36), 10), qb((0, 36), (9, 28), (1.6, 21), 10)))
    k.plate(m - m.inset(1.8), 2.4, "gold")
    k.plate(m.inset(1.8), 1.0, "light", glow=True)
    k.box(0, 18.8, 0, 5.4, 1.6, 2.9, "lapis")


@design("crown_of_the_sun")
def crown_of_the_sun(k):
    """the Pharaoh's sun disc between two falcon wings, all gold and lapis, raised on a sceptre"""
    k.theme("sandsunk_tomb")
    k.mat(gold=flat(GOLD, 0.7, bevel=0.14), lapis=flat(ramp("#0e2a6e", "#163e96", "#2458c0", "#3a74dc"), 0.7), light=fire(ramp("#e8761a", "#ffb03a", "#ffe08a", "#fff6d0"), 0.3, 0.7))
    pole(k, 18, "lapis", shoe="gold", grip="gold")
    for s_ in (1, -1):
        for j, (y, ln) in enumerate(((22.6, 16), (20.4, 12.4), (18.4, 9))):
            k.plate(P((s_ * 2, y + 1.6), (s_ * (2 + ln), y + 3.4 - j * 0.6), (s_ * (2 + ln * 0.9), y + 1), (s_ * 2, y - 1.4)), 1.8, "gold" if j % 2 == 0 else "lapis")
    k.plate(disc(0, 28, 6.0, 18), 1.8, "gold")
    k.plate(disc(0, 28, 4.8, 18), 2.2, "light", glow=True)
    k.plate(P((-1.4, 33.6), (1.4, 33.6), (1, 37), (2.6, 38.4), (-0.4, 39), (-1.4, 36)), 1.6, "gold")


@design("lifeblood_staff")
def lifeblood_staff(k):
    """a great clot of the Titan's living blood, red and warm in a clamp of knuckle bone, slowly healing its own crack"""
    k.theme("fallen_titan")
    k.mat(bone=bone(IVORY, 0.72), blood=fire(ramp("#7a0a10", "#b81a1c", "#e84a30", "#ffa080"), 0.3, 0.7), shaft=bone(IVORY, 0.56), hot=flat(WARM, 0.8))
    pole(k, 18, "shaft", shoe="bone")
    orb(k, 0, 25, 5.2, "blood")
    k.plate(L([(-2.4, 29), (0, 25), (-1, 21)], 0.4), 5.6, "hot", glow=True)
    for s_ in (1, -1):
        k.plate(stroke((s_ * 1.4, 17), (s_ * 9.4, 20), (s_ * 6.4, 31), 1.6, 8), 2.4, "bone")
        k.plate(P((s_ * 5, 30), (s_ * 8, 30), (s_ * 4.4, 35)), 2.0, "bone")


@design("diastole")
def diastole(k):
    """the Titan's heart in its open beat, huge chambers and the arteries still attached, one mended with gold wire"""
    k.theme("fallen_titan")
    k.mat(meat=flat(ramp("#3a0608", "#5e0c10", "#841618", "#a82420", "#cc4030"), 0.6, 0.3, bevel=0.14), art=flat(ramp("#6a2a30", "#8e4044", "#b45c5c"), 0.6, bevel=0.1), gold=flat(GOLD, 0.72), hot=fire(RUBY, 0.3, 0.7), shaft=bone(IVORY, 0.56))
    pole(k, 16, "shaft", shoe="gold")
    m = disc(-3.6, 26, 5.6, 14) + disc(3.4, 24.6, 5.4, 14) + P((-8.6, 24), (8.4, 22), (0, 15))
    k.plate(m, 6.6, "meat")
    k.plate(P((-1, 30), (0.2, 22), (-0.8, 17), (0.2, 16), (1.4, 22), (0.6, 30)), 6.8, "hot", glow=True)
    k.plate(stroke((-3, 30), (-4.4, 34), (-1, 37), 1.5) + stroke((2, 29), (3, 33), (7, 35), 1.3) + stroke((5, 28), (10, 28), (11, 33), 1.1), 2.4, "art")
    for y in (20, 22, 24):
        k.box(4.4 - (y - 20) * 0.1, y, 3.3, 2.8, 0.4, 0.4, "gold")


@design("incense_staff")
def incense_staff(k):
    """a jade monk's long incense holder, three sticks burning and their smoke painted in a neat rising ribbon"""
    R = k.theme("jade_monastery", base=0.54)
    jade = ramp("#0e4a34", "#1a7050", "#2e9a70", "#5cc898", "#a0ecc8")
    k.mat(jade=flat(jade, 0.74, bevel=0.14), lacq=flat(ramp("#2a0608", "#4a0c10", "#6e1616"), 0.6, bevel=0.06), stick=flat(ramp("#6a3a1a", "#8e5428"), 0.6), hot=fire(HOT, 0.4, 0.6), smoke=flat(PALE, 0.7), gold=flat(GOLD, 0.66))
    pole(k, 18, "lacq", shoe="gold", grip="gold")
    k.plate(P((-7, 22), (7, 22), (5.4, 18), (-5.4, 18)), 6.4, "jade")
    k.box(0, 21.8, 0, 12.6, 0.8, 6.8, "gold")
    for x, h in ((-3.4, 10), (0, 12), (3.4, 9.4)):
        k.box(x, 22.6, 0, 0.6, h, 0.6, "stick")
        k.plate(disc(x, 22.6 + h, 0.6, 5), 0.7, "hot", glow=True)
    k.plate(wave(lambda t: 3 * math.sin(t * 7) * (0.4 + t), lambda t: 0.4 + 0.6 * t, 35, 46, 14), 0.5, "smoke")


@design("calm_eye_staff")
def calm_eye_staff(k):
    """the storm's eye held still: a ring of cloud standing round a clear gap of sky, sun in the middle of it"""
    R = k.theme("storm_bastion")
    k.mat(iron=flat(R["dark"], 0.66, bevel=0.12), cloud=flat(ramp("#6a7a94", "#8ea0b8", "#b8c8dc", "#dce8f4"), 0.74, bevel=0.14), sky=flat(ramp("#2a6ab4", "#3e8cd8", "#6cb4f0"), 0.6), sun=fire(WARM, 0.3, 0.7))
    pole(k, 15, "iron")
    k.plate(disc(0, 25, 8.4, 20), 1.0, "sky")
    orb(k, 0, 25, 2.6, "sun")
    for j in range(11):
        a = j * 2 * math.pi / 11
        r_ = 2.6 + 0.9 * math.sin(j * 2.3) ** 2
        k.plate(disc(math.cos(a) * 9.4, 25 + math.sin(a) * 9.4, r_, 10), 3.6, "cloud")


@design("transfusion_staff")
def transfusion_staff(k):
    """a court physician's glass and silver instrument: a graduated cylinder of blood, a plunger, a very fine needle at the top"""
    k.theme("bloodmoon_court")
    k.mat(silver=flat(SILVER, 0.72, bevel=0.14), glass=flat(ramp("#6a5a64", "#94808a", "#c0b0b8"), 0.5, bevel=0.2), blood=fire(ramp("#7a0a10", "#b81a1c", "#e84a30"), 0.3, 0.6), lacq=flat(ramp("#14040a", "#280a12", "#42101c"), 0.6, bevel=0.06), needle=flat(FE, 0.92))
    pole(k, 12, "silver", 1.6, grip="lacq", shoe="silver")
    k.box(0, 14, 0, 7.8, 15, 7.8, "glass")
    k.box(0, 14.6, 0, 6.6, 9.4, 8.0, "blood", glow=True)
    k.box(0, 12.4, 0, 10.6, 1.6, 2.4, "silver")
    k.box(0, 29, 0, 8.6, 1.6, 8.6, "silver")
    for y in (17, 20, 23, 26):
        k.box(-3.4, y, 0, 1.4, 0.3, 8.2, "silver")
    k.box(0, 30.6, 0, 1.6, 3.0, 1.6, "silver")
    k.box(0, 33.6, 0, 0.5, 6, 0.5, "needle")


@design("mending_ember")
def mending_ember(k):
    """a piece of dragon-glass with a healed crack through it, the fix itself bright gold, an ember warming it from under"""
    k.theme("obsidian_labyrinth")
    k.mat(glass=flat(ramp("#0c0a10", "#16141e", "#26222e", "#3a3444"), 0.7, bevel=0.2), gold=fire(WARM, 0.4, 0.6), hot=fire(HOT, 0.3, 0.7), bronze=flat(BRASS, 0.6))
    pole(k, 15, "dark")
    m = P((-5.4, 16), (5.4, 16), (8.4, 24), (3.6, 36), (0, 38), (-4.4, 34), (-8.4, 24))
    k.plate(m, 4.4, "glass")
    k.plate(L([(1, 37), (-2, 30), (2.6, 25), (-1, 21), (0.6, 16)], 0.6) + L([(2.6, 25), (7, 24)], 0.4) + L([(-2, 30), (-6, 29)], 0.4), 4.7, "gold", glow=True)
    k.box(0, 14, 0, 7, 2.2, 5.0, "bronze")


@design("beacon_staff")
def beacon_staff(k):
    """a real lighthouse, a tiny one, stone and white paint, its great lens turning and the beam sweeping out"""
    R = k.theme("abyssal_lighthouse")
    k.mat(paint=flat(ramp("#a0988c", "#c6bead", "#e6dfd0"), 0.7, bevel=0.1), red=flat(ramp("#6a1014", "#94181c", "#c02a2a"), 0.66, bevel=0.1), lens=fire(HOLY, 0.3, 0.7), iron=flat(IRON, 0.62), beam=fire(ramp("#d0c890", "#f0e8b0", "#fff8d0"), 0.3, 0.6))
    pole(k, 13, "iron")
    for j in range(7):
        k.box(0, 13 + j * 2, 0, 9 - j * 0.6, 2, 9 - j * 0.6, "red" if j % 2 else "paint")
    k.box(0, 27, 0, 8.4, 0.8, 8.4, "iron")
    orb(k, 0, 29.6, 1.9, "lens")
    k.box(0, 27.6, 0, 3.8, 3.8, 3.8, "lens", glow=True)
    k.plate(P((-3, 31.6), (3, 31.6), (0, 35)), 3.0, "red")
    k.plate(P((1, 29), (15, 31.6), (15, 27)) + P((-1, 29), (-11, 26.6), (-11, 30)), 0.3, "beam", glow=True)


@design("lamp")
def lamp(k):
    """the great lamp from the top of the Lighthouse itself, ribbed Fresnel glass a hand wide, and everything drowned turns its face toward it"""
    R = k.theme("abyssal_lighthouse")
    k.mat(iron=flat(IRON, 0.62, bevel=0.12), lens=fire(HOLY, 0.3, 0.7), glass=flat(ramp("#b8c8d4", "#dce8ee", "#ffffff"), 0.8, bevel=0.1), brass=flat(BRASS, 0.64, bevel=0.14), tent=flat(R["blade"], 0.6))
    pole(k, 15, "iron", 2.4, shoe="brass")
    k.box(0, 15, 0, 13, 1.6, 13, "brass")
    k.box(0, 32, 0, 13, 1.6, 13, "brass")
    k.plate(disc(0, 24.4, 6.6, 18), 7.6, "lens", glow=True)
    for j in (2.4, 4.4, 6.0):
        k.plate(ring(0, 24.4, j + 0.4, j), 7.8, "glass")
    for x, z in ((-5.6, -5.6), (5.6, -5.6), (-5.6, 5.6), (5.6, 5.6)):
        k.box(x, 16.6, z, 1.0, 15.4, 1.0, "iron")
    k.plate(P((-6, 33.6), (6, 33.6), (0, 39)), 7.0, "iron")


@design("corona_staff")
def corona_staff(k):
    """a sunburst monstrance: gold rays long and short from a round white window, the holiest thing the Cathedral owns"""
    k.theme("eclipse_cathedral", base=0.5)
    k.mat(gold=flat(GOLD, 0.7, bevel=0.14), light=fire(HOLY, 0.4, 0.6), rod=flat(BIRCH, 0.78, bevel=0.06), ruby=flat(RUBY, 0.7))
    pole(k, 15, "rod", shoe="gold", grip="gold")
    for j in range(20):
        a = j * 2 * math.pi / 20
        ln = 13 if j % 2 == 0 else 9.4
        w = 0.34 if j % 2 == 0 else 0.26
        k.plate(P((math.cos(a - w) * 5, 25 + math.sin(a - w) * 5), (math.cos(a) * ln, 25 + math.sin(a) * ln), (math.cos(a + w) * 5, 25 + math.sin(a + w) * 5)), 1.2, "gold")
    k.plate(ring(0, 25, 6.0, 4.0), 2.4, "gold")
    k.plate(disc(0, 25, 4.0, 16), 2.0, "light", glow=True)
    for j in range(4):
        a = j * math.pi / 2 + 0.78
        k.plate(disc(math.cos(a) * 5, 25 + math.sin(a) * 5, 0.8, 6), 2.8, "ruby")


@design("ember_heart_staff")
def ember_heart_staff(k):
    """a dragon's coal-sac, hard as stone now, gold-caged and still warm; hold your hands to it and be well"""
    k.theme("wyrms_hoard")
    k.mat(gold=flat(GOLD, 0.66, bevel=0.14), scale=flat(ramp("#2a0606", "#4a0c0a", "#741612", "#a02416"), 0.62, 0.2, bevel=0.1), hot=fire(WARM, 0.3, 0.7))
    pole(k, 15, "scale", shoe="gold", grip="gold")
    orb(k, 0, 24, 5.2, "hot")
    for s_ in (1, -1):
        k.plate(stroke((0, 16), (s_ * 12, 20), (0, 33), 1.0, 10), 1.2, "gold")
        k.plate(stroke((0, 16), (s_ * 6, 20), (0, 33), 0.8, 10), 1.0, "gold")
    k.plate(ring(0, 34, 2.2, 1.0), 1.2, "gold")
    for j in range(5):
        a = math.radians(j * 72 + 20)
        x, y = math.cos(a) * 3.4, 24 + math.sin(a) * 3.4
        k.plate(P((x - 1, y), (x + 1, y), (x, y + 1.8)), 5.8, "scale")


# ---------------------------------------------------------------- the world's

@design("pilgrims_staff")
def pilgrims_staff(k):
    """a walking staff worn smooth where hands have been, a scallop shell, a water gourd on a thong and a road's worth of scratched tallies"""
    oak = ramp("#5a3a1e", "#7a5430", "#9c7044", "#bc8e5c", "#d8ae7c")
    k.mat(oak=staves(oak, 1.0, 0.66), shell=flat(BIRCH, 0.8, bevel=0.1), gourd=flat(ramp("#7a5a22", "#a07c34", "#c49c4a"), 0.7, bevel=0.14), cord=flat(LEATHER, 0.66), wrap=wrap(LEATHER, IRON[1], 5), dark=flat(IRON, 0.6), wood=flat(oak, 0.5), hot=flat(WARM, 0.8))
    pole(k, 32, "oak", 2.2, shoe="oak", bottom=-20)
    k.box(0, 25, 0, 2.8, 0.7, 2.8, "cord")
    k.plate(disc(0, 21, 4.4, 14) & rect(-5, 16, 5, 26) & P((-6, 26), (6, 26), (0, 15)), 2.8, "shell", z=1.6)
    for x in (-2, 0, 2):
        k.plate(L([(0, 16), (x, 24)], 0.3), 3.0, "cord", z=1.6)
    k.plate(disc(6.4, 14.4, 3.0, 12) + disc(6.4, 19, 2.0, 10), 3.0, "gourd")
    k.box(6.4, 20.6, 0, 1.0, 1.0, 1.0, "cord")
    k.plate(stroke((0.6, 25), (6, 25), (6.4, 21), 0.4), 0.5, "cord")
    for y in (29, 30, 31):
        k.box(0, y, 1.1, 1.4, 0.3, 0.2, "hot")


@design("moonpetal_staff")
def moonpetal_staff(k):
    """a silver vine climbing a pale pole and opening at the top in moon-white petals, one falling"""
    k.mat(rod=flat(BIRCH, 0.66, bevel=0.06), silver=flat(SILVER, 0.76, bevel=0.1), pet=flat(ramp("#a8b8d4", "#ccd8ec", "#f0f4ff"), 0.8, bevel=0.06), light=fire(ramp("#b0c8ff", "#e0ecff", "#ffffff"), 0.3, 0.7), wrap=wrap(SILVER, SILVER[1], 4), dark=flat(SILVER, 0.5))
    pole(k, 18, "rod", 1.8)
    for j in range(24):
        a = j * 0.7
        k.seg((math.sin(a) * 1.4, -10 + j * 1.2), (math.sin(a + 0.7) * 1.4, -8.8 + j * 1.2), 0.5, 0.5, "silver", z=math.cos(a) * 1.4)
    for a in (-80, -48, -16, 16, 48, 80):
        r_ = math.radians(a + 90)
        c, s_ = math.cos(r_), math.sin(r_)
        k.plate(P((0, 18), (c * 6 - s_ * 2.4, 18 + s_ * 6 + c * 2.4), (c * 14, 18 + s_ * 14), (c * 6 + s_ * 2.4, 18 + s_ * 6 - c * 2.4)), 1.0, "pet", z=abs(a) / 70)
    orb(k, 0, 21.6, 2.0, "light")
    k.plate(P((9, 9), (11, 11), (12, 7), (10, 6)), 0.6, "pet")


@design("seraph_staff")
def seraph_staff(k):
    """an angel's two wings folding round a holy flame, gold on the feather tips, on a staff of white marble"""
    k.mat(mar=flat(BIRCH, 0.7, bevel=0.06), fe=flat(ramp("#a8a498", "#ccc8ba", "#ecE8da", "#fffef6"), 0.72, bevel=0.1), gold=flat(GOLD, 0.7), flame=fire(WARM, 0.1, 0.9), wrap=wrap(GOLD, GOLD[1], 4), dark=flat(GOLD, 0.5))
    pole(k, 15, "mar", shoe="gold")
    for s_ in (1, -1):
        for j in range(6):
            t = j / 5
            a = math.radians(92 - t * 66 + 6)
            ln = 21 - j * 2.4
            x0, y0 = s_ * (1.4 + j * 0.8), 16 + j * 0.8
            tip = (x0 + s_ * math.cos(a) * ln * 0.66, y0 + math.sin(a) * ln)
            k.plate(P((x0 - s_ * 1.0, y0), (x0 + s_ * 1.6, y0 - 0.4), (tip[0] + s_ * 1.4, tip[1] - 1.6), tip), 1.2, "fe", z=j * 0.34)
            k.plate(P((tip[0], tip[1]), (tip[0] + s_ * 1.4, tip[1] - 1.6), (tip[0] - s_ * 0.2, tip[1] - 2.6)), 1.5, "gold", z=j * 0.34)
    k.plate(P(path(qb((0, 17), (-4.4, 22), (0, 34), 10), qb((0, 34), (4.4, 22), (0, 17), 10))), 1.0, "flame", glow=True, z=2.6)


@design("sunspire")
def sunspire(k):
    """a gold spire of stacked rings like a temple's top, the noon sun burning at the very tip of it"""
    k.mat(gold=flat(GOLD, 0.7, bevel=0.14), sun=fire(ramp("#ffb03a", "#ffe08a", "#fff6d0", "#ffffff"), 0.4, 0.6), wrap=wrap(LEATHER, GOLD[2], 4), dark=flat(GOLD, 0.5), wood=flat(GOLD, 0.56))
    pole(k, 15, "gold", grip="wrap", shoe="gold")
    for j in range(9):
        w = 9 - j * 0.86
        k.box(0, 15 + j * 2, 0, w, 1.6, w, "gold")
        k.box(0, 16.6 + j * 2, 0, w * 0.6, 0.4, w * 0.6, "gold")
    orb(k, 0, 36, 3.0, "sun")
    for j in range(8):
        a = j * math.pi / 4
        k.plate(P((math.cos(a - 0.3) * 3.4, 36 + math.sin(a - 0.3) * 3.4), (math.cos(a) * 7.4, 36 + math.sin(a) * 7.4), (math.cos(a + 0.3) * 3.4, 36 + math.sin(a + 0.3) * 3.4)), 0.8, "sun", glow=True)


@design("censer_staff")
def censer_staff(k):
    """a war chaplain's censer on a pole: heavy iron, chains, more like a flail than a blessing, and it works as both"""
    k.mat(iron=flat(IRON, 0.62, bevel=0.14), gold=flat(GOLD, 0.68), oak=staves(ramp("#3a2410", "#52341c", "#6e4826"), 1.0, 0.6), smoke=flat(PALE, 0.5), hot=fire(WARM, 0.3, 0.7), wrap=wrap(LEATHER, IRON[1], 5), dark=flat(IRON, 0.6))
    pole(k, 31, "oak")
    k.box(0, 30.6, 0, 3.0, 2.0, 3.0, "iron")
    k.plate(rect(-0.5, 31, 11, 32), 1.2, "iron")
    links(k, [(10.4, 30.4), (10.4, 28.6), (10.4, 26.8), (10.4, 25)], "iron", 0.7)
    orb(k, 10.4, 19, 4.2, "hot")
    k.plate(ring(10.4, 19, 5.4, 4.4) + rect(9.8, 13.2, 11, 24.8) + rect(4.8, 18.4, 16, 19.6), 5.6, "iron")
    k.plate(P((7, 24), (13.8, 24), (10.4, 27)), 5.0, "gold")
    k.plate(wave(lambda t: 14 + 3 * t + math.sin(t * 7), lambda t: 0.9 - 0.4 * t, 22, 34, 9), 0.7, "smoke")


@design("oracles_laurel")
def oracles_laurel(k):
    """a gold laurel wreath round its own quiet light, the leaves real enough to count"""
    k.mat(gold=flat(GOLD, 0.7, bevel=0.1), rod=flat(BIRCH, 0.66, bevel=0.06), light=fire(WARM, 0.3, 0.7), wrap=wrap(GOLD, GOLD[1], 4), dark=flat(GOLD, 0.5))
    pole(k, 16, "rod", 1.8, shoe="gold")
    orb(k, 0, 26, 3.4, "light")
    for s_ in (1, -1):
        k.plate(stroke((s_ * 0.5, 17), (s_ * 12.6, 22), (s_ * 2.6, 36), 0.5, 10), 1.0, "gold")
        for j in range(8):
            t = j / 8
            x = s_ * (1.4 + 2 * (1 - t) * t * 2 * 12.4 * 0.9)
            y = 18 + t * 18
            a = math.radians(30 + t * 110)
            c, s2 = s_ * math.cos(a), math.sin(a)
            k.plate(P((x, y), (x + c * 1.6 - s2 * 0.9, y + s2 * 1.6 + c * 0.9), (x + c * 3.6, y + s2 * 3.6), (x + c * 1.6 + s2 * 0.9, y + s2 * 1.6 - c * 0.9)), 0.8, "gold")


@design("everbloom")
def everbloom(k):
    """a rose on a stem with real thorns, always opening and never open, its petals made of light"""
    k.mat(stem=flat(ramp("#14361a", "#1e4e26", "#2e6e34", "#46904a"), 0.62, bevel=0.06), thorn=flat(ramp("#4a2a1a", "#6a3e28"), 0.7), rose=fire(ramp("#c02a5a", "#e85a8a", "#ffa0c0", "#ffe4ee"), 0.2, 0.8), inner=fire(ramp("#ff80a8", "#ffc0d4", "#ffffff"), 0.4, 0.6), wrap=wrap(ramp("#14361a", "#1e4e26"), None, 4), dark=flat(ramp("#14361a", "#1e4e26"), 0.6))
    pole(k, 18, "stem", 1.6)
    for y, s_ in ((12, 1), (8, -1), (16, -1), (4, 1), (-8, -1)):
        k.plate(P((s_ * 0.8, y + 0.8), (s_ * 0.8, y - 0.8), (s_ * 2.8, y - 1.4)), 0.8, "thorn")
    for s_ in (1, -1):
        k.plate(P((s_ * 0.6, 13), (s_ * 5, 15), (s_ * 9, 13), (s_ * 5, 11.6)), 0.6, "stem")
    for s_ in (1, -1):
        k.plate(P(path((0, 18), qb((s_ * 10, 19), (s_ * 10.4, 28), (s_ * 2, 32), 8), (0, 28))), 3.0, "rose")
    for s_ in (1, -1):
        k.plate(P(path((0, 19.4), qb((s_ * 6.4, 21), (s_ * 7, 28), (s_ * 0.6, 34), 8), (s_ * -1, 28))), 2.0, "rose", z=1.4)
    k.plate(P(path(qb((-3.4, 24), (0, 21), (3.4, 25), 4), qb((3.4, 25), (2, 33), (-1, 35), 5), qb((-3, 31), (-3.4, 28), (-3.4, 24), 3))), 1.2, "inner", glow=True, z=2.6)
    k.plate(L([(-1, 25), (1.6, 28), (-0.6, 30)], 0.4), 1.2, "rose", z=3.0)


@design("auroras_vigil")
def auroras_vigil(k):
    """a crown of ice with the northern lights hanging from it in curtains, green to violet, moving"""
    A = ramp("#2ae0a0", "#5cf0c0", "#a0ffe0")
    B = ramp("#7a4aff", "#a87aff", "#d0b0ff")
    ice = ramp("#5e8cb0", "#88b4d0", "#b4d8ec", "#e0f4ff")
    k.mat(ice=flat(ice, 0.76, bevel=0.14), rod=flat(ice, 0.52), a=fire(A, 0.3, 0.7), b=fire(B, 0.3, 0.7), wrap=wrap(ice, ice[0], 4), dark=flat(ice, 0.46))
    pole(k, 18, "rod")
    k.plate(P((-10, 20), (10, 20), (11, 25), (-11, 25)), 3.0, "ice")
    for x, h, w in ((-9, 8, 2), (-4.4, 12, 2.4), (0, 16, 2.8), (4.4, 12, 2.4), (9, 8, 2)):
        k.plate(shard(x, 24, h, 0, w), 2.4, "ice")
    for j, x in enumerate((-9, -6, -3, 3, 6, 9)):
        k.plate(wave(lambda t, x=x, j=j: x + 0.8 * math.sin(t * 7 + j), lambda t: 0.9, 20, 7 - abs(x) * 0.4, 10), 0.3, "a" if j % 2 else "b", glow=True)


@design("white_accord")
def white_accord(k):
    """the white half of the bargain: two open hands, one bone and one gold, holding up a small pale sun between them"""
    k.mat(bonem=flat(BIRCH, 0.76, bevel=0.14), gold=flat(GOLD, 0.66, bevel=0.14), hot=fire(HOLY, 0.4, 0.6), wrap=wrap(BIRCH, GOLD[3], 4), dark=flat(GOLD, 0.6), wood=flat(BIRCH, 0.5))
    pole(k, 16, "wood")
    orb(k, 0, 28, 3.6, "hot")
    for s_, m_ in ((1, "bonem"), (-1, "gold")):
        k.plate(P((s_ * 1.0, 15), (s_ * 8, 16), (s_ * 10, 21), (s_ * 7.6, 25), (s_ * 2, 22)), 2.4, m_)
        for j, (x, y) in enumerate(((10.6, 28), (8.4, 29.6), (6, 29.6), (4, 28.4))):
            k.plate(L([(s_ * (x - 1.4), 23), (s_ * x, y)], 1.0), 1.6, m_)
        k.plate(L([(s_ * 2.6, 20), (s_ * 0.6, 23.4)], 1.1), 1.6, m_)


@design("apprentice_white_staff")
def apprentice_white_staff(k):
    """a first-year healer's birch stick with a candle tied on and a bandage round it. Sweet"""
    k.mat(oak=flat(BIRCH, 0.6, bevel=0.06), wax=flat(BIRCH, 0.9, bevel=0.1), lint=wrap(PALE, PALE[1], 3), flame=fire(WARM, 0.1, 0.9), wood=flat(IRON, 0.5))
    pole(k, 15, "oak", grip="lint", shoe="oak")
    k.box(0, 13.6, 0, 3.2, 3.0, 3.2, "lint")
    k.box(0, 15, 0, 2.6, 5, 2.6, "wax")
    k.plate(P((-1.8, 19), (-1.0, 19), (-1.4, 16)), 3.0, "wax")
    k.plate(P(path(qb((0, 20), (-2, 22), (0, 26), 5), qb((0, 26), (2, 22), (0, 20), 5))), 1.4, "flame", glow=True)
