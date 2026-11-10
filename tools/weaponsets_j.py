"""Bows, in the Kiln bows' space: drawn across the item square on z 8, the design called again for each draw (k.pull) with an arrow
on (k.arrow). Bow() works in the bow's own frame: u along it, tip up; v forward, toward the target. kiln_longbow stays."""
import math

from voxsword import ramp
from weaponsets import design, qb, path, P, L, disc, ring, rect, wave, Mask, flat, fire, staves, steel, honed, bone, gem, at, lit, wrap, stripes, facet_of
from weaponsets_a import BRASS, GOLD, IRON, LEATHER
from weaponsets_d import RUBY, SILVER
from weaponsets_e import CORK, HORN, IVORY, RAG

O, U, A, BZ = (8.0, 8.0), (0.651, 0.759), (-0.759, 0.651), 8.0
HOT = ramp("#a02206", "#e04a0a", "#ff8a1c", "#ffc84a", "#fff0b0")


class Bow:
    def __init__(self, k, L=9.4, bulge=3.4, curl=1.4, tips=0.82, wob=None, rig=0.35):
        self.k, self.L, self.bulge, self.curl, self.tips, self.wob, self.rig = k, L, bulge, curl, tips, wob, rig
        self.p = k.pull

    def c(self, s, dv=0.0):
        """the limb's centre at s, -1 bottom tip to 1 top tip, in (u, v)"""
        p = self.p
        bend = self.bulge * (1 - s * s) + self.rig * p * abs(s)
        cu = self.curl * max(0.0, abs(s) - self.tips) / (1 - self.tips)
        v = bend + cu - 0.9 * p * s * s + dv
        if self.wob:
            v += self.wob(s)
        return (s * self.L * (1 - 0.05 * p), v)

    def w(self, q):
        return (O[0] + U[0] * q[0] + A[0] * q[1], O[1] + U[1] * q[0] + A[1] * q[1])

    def P(self, pts):
        return P([self.w(q) for q in pts])

    def L_(self, pts, w):
        return L([self.w(q) for q in pts], w)

    def limb(self, width, mat, d=1.5, n=20, s0=-1.0, s1=1.0, dv=0.0, glow=False):
        l, r = [], []
        for j in range(n + 1):
            s = s0 + (s1 - s0) * j / n
            a, b = self.c(s - 0.02), self.c(s + 0.02)
            du, dv_ = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(du, dv_) or 1
            nu, nv = -dv_ / ln, du / ln
            q = self.c(s, dv)
            hw = width(abs(s)) / 2
            l.append((q[0] + nu * hw, q[1] + nv * hw))
            r.append((q[0] - nu * hw, q[1] - nv * hw))
        m = self.P(l + r[::-1])
        self.k.plate(m, d, mat, z=BZ, glow=glow)
        return m

    def put(self, m, d, mat, glow=False):
        self.k.plate(m, d, mat, z=BZ, glow=glow)

    def dot(self, s, r_, mat, dv=0.0, d=2.0, glow=False, n=8):
        x, y = self.w(self.c(s, dv))
        self.put(disc(x, y, r_, n), d, mat, glow)

    def tri(self, s, du, dv, w, mat, d=1.0, glow=False, off=0.0):
        """a spike standing off the limb at s"""
        q = self.c(s, off)
        self.put(self.P([(q[0] - w / 2, q[1]), (q[0] + du, q[1] + dv), (q[0] + w / 2, q[1])]), d, mat, glow)

    def band(self, s, w, h, mat, d=2.0):
        q = self.c(s)
        self.put(self.P([(q[0] - h / 2, q[1] - w / 2), (q[0] + h / 2, q[1] - w / 2), (q[0] + h / 2, q[1] + w / 2), (q[0] - h / 2, q[1] + w / 2)]), d, mat)

    def along(self, s0, s1, dv, w, mat, d=1.56, glow=False, n=8):
        pts = [self.c(s0 + (s1 - s0) * j / n, dv) for j in range(n + 1)]
        self.put(self.L_(pts, w), d, mat, glow)

    def string(self, mat, w=0.35, glow=False, a=-1.0, b=1.0):
        """from tip to tip through the nock"""
        t0, t1 = self.c(a), self.c(b)
        mid = ((t0[0] + t1[0]) / 2, (t0[1] + t1[1]) / 2 - 4.2 * self.p)
        self.nock = mid
        for e in (t0, t1):
            self.k.seg(self.w(e), self.w(mid), w, w, mat, z=BZ, glow=glow)

    def shaft(self, wood="wood", head="edge", fletch="glow", glow=True):
        """the arrow on the string"""
        if not self.k.arrow:
            return
        n = self.nock
        tip = (n[0], n[1] + 14.0)
        self.k.seg(self.w(n), self.w(tip), 0.5, 0.5, wood, z=BZ + 0.6)
        self.put_arrow(tip, head, n, fletch, glow)

    def put_arrow(self, tip, head, n, fletch, glow):
        k = self.k
        k.seg(self.w(tip), self.w((tip[0], tip[1] + 2.2)), 1.3, 0.6, head, z=BZ + 0.6)
        k.seg(self.w(n), self.w((n[0], n[1] + 2.4)), 1.2, 0.3, fletch, z=BZ + 0.6, glow=glow)


def grip(b, mat="wrap", w=2.6, h=3.2, d=2.0):
    b.band(0, w, h, mat, d)


@design("hoop_bow")
def hoop_bow(k):
    """a length of barrel hoop sprung into a bow, oak stave grip, tarred cord"""
    R = k.theme("cellar")
    k.mat(hoop=flat(R["dark"], 0.66, bevel=0.1), stave=staves(R["wood"], 1.2, 0.6))
    b = Bow(k)
    b.limb(lambda s: 1.5, "hoop")
    for s in (-0.7, -0.4, 0.4, 0.7):
        b.band(s, 2.4, 0.7, "dark", 1.8)
    grip(b, "stave", 3.0, 4.4)
    b.string("acc")
    b.shaft()


@design("undertow_bow")
def undertow_bow(k):
    """the Cask Mother's: a warped wet stave wound in weed, a brass tap at the grip, vinegar burning green up the back"""
    R = k.theme("cellar")
    k.mat(stave=staves(R["wood"], 1.2, 0.56), brass=flat(BRASS, 0.64), weed=flat(ramp("#1a2a14", "#2c4018", "#425a22"), 0.6))
    b = Bow(k, L=10, wob=lambda s: 0.4 * math.sin(s * 7))
    b.limb(lambda s: 2.1 - 0.9 * s, "stave")
    b.along(-0.8, 0.8, 0.5, 0.5, "glow", glow=True)
    for s in (-0.6, -0.2, 0.3, 0.7):
        b.band(s, 2.8, 0.6, "weed", 1.8)
    grip(b, "brass", 3.0, 3.0)
    b.tri(0, 0, 2.8, 1.2, "brass", 1.4, off=0.8)
    b.string("acc")
    b.shaft()


@design("noose_bow")
def noose_bow(k):
    """a hangman's ash stave with a little noose dangling off the lower tip, for luck, somebody's"""
    R = k.theme("gallows")
    k.mat(rope=flat(R["acc"], 0.64), hemp=wrap(R["wrap"], R["dark"][0], 4), ash=staves(R["wood"], 1.0, 0.6))
    b = Bow(k)
    b.limb(lambda s: 2.0 - 1.0 * s, "ash")
    grip(b, "hemp", 2.8, 4.2)
    x, y = b.w(b.c(-0.96))
    b.put(ring(x + 1.0, y - 3.0, 1.7, 1.0), 0.7, "rope")
    k.seg((x, y), (x + 1.0, y - 1.4), 0.4, 0.4, "rope", z=BZ)
    b.string("rope")
    b.shaft()


@design("long_drop")
def long_drop(k):
    """a gallows upright turned bow: tall and black, its string a true hangman's rope, an ember burning in the knot at the top"""
    R = k.theme("gallows")
    k.mat(rope=flat(R["acc"], 0.64), hemp=wrap(R["wrap"], R["dark"][0], 4), oak=staves(R["wood"], 1.2, 0.54))
    b = Bow(k, L=11.4, bulge=2.6, curl=0.4)
    b.limb(lambda s: 2.4 - 0.8 * s, "oak", 1.7)
    for s in (-0.8, -0.3, 0.3, 0.8):
        b.band(s, 3.0, 0.9, "dark", 2.0)
    grip(b, "hemp", 3.0, 4.2)
    b.string("rope", 0.5)
    b.dot(0.96, 1.2, "hemp", d=2.0)
    b.dot(0.96, 0.6, "glow", d=2.2, glow=True)
    b.shaft()


@design("yewrot_bow")
def yewrot_bow(k):
    """an old yew stave with the rot in it: bark coming off in plates, shelf fungus up one limb, still a good bow"""
    R = k.theme("rotwood")
    k.mat(bark=staves(R["wood"], 0.9, 0.6), fungus=flat(R["acc"], 0.6), moss=flat(R["wrap"], 0.6))
    b = Bow(k, wob=lambda s: 0.3 * math.sin(s * 11))
    b.limb(lambda s: 2.2 - 1.2 * s, "bark")
    for s, ln in ((0.3, 2.8), (0.5, 2.2), (-0.5, 2.6)):
        b.tri(s, 0.8, ln, 1.6, "fungus", 1.6)
    grip(b, "moss", 2.8, 3.8)
    b.dot(-0.3, 0.7, "glow", d=1.9, glow=True)
    b.string("acc")
    b.shaft()


@design("antlerbow")
def antlerbow(k):
    """two sheds of the Mossking's antlers joined at the grip: each limb a beam of bone with its tines still on, moss at the join"""
    R = k.theme("rotwood")
    k.mat(bone=bone(R["blade"], 0.68), moss=flat(R["wrap"], 0.6))
    b = Bow(k, L=10)
    b.limb(lambda s: 2.2 - 0.9 * s, "bone")
    for s, du, dv in ((0.32, 1.6, 4.0), (0.6, 1.8, 3.4), (0.84, 1.8, 2.6), (-0.32, -1.6, 4.0), (-0.6, -1.8, 3.4), (-0.84, -1.8, 2.6)):
        b.tri(s, du, dv, 1.1, "bone", 1.3)
    grip(b, "moss", 3.0, 3.8)
    b.dot(0, 0.8, "glow", d=2.2, glow=True)
    b.string("acc")
    b.shaft()


@design("mourners_bow")
def mourners_bow(k):
    """a thin black bow for a funeral, a grey ribbon knotted on each limb, a drip of wax at the grip"""
    R = k.theme("crypt")
    k.mat(black=staves(R["wood"], 1.0, 0.5), ribbon=flat(ramp("#54545e", "#72727c", "#94949e", "#b8b8c0"), 0.6, bevel=0.1), wax=flat(R["acc"], 0.74, bevel=0.1))
    b = Bow(k, L=9.8, bulge=2.8)
    b.limb(lambda s: 1.6 - 0.7 * s, "black")
    for s in (0.6, -0.6):
        b.band(s, 2.4, 0.8, "ribbon", 1.8)
        x, y = b.w(b.c(s))
        b.put(wave(lambda t, x=x: x + 2.4 * t + 0.4 * math.sin(t * 6), lambda t: 0.5, y, y - 5, 8), 0.4, "ribbon")
    grip(b, "wax", 2.8, 3.4)
    b.string("acc")
    b.shaft()


@design("requiem")
def requiem(k):
    """the Abbot's last service: silver limbs ending in a lit candle at each tip, wax running back down them, the grip a small prayer book"""
    R = k.theme("crypt", base=0.56)
    k.mat(silver=flat(R["blade"], 0.66, bevel=0.1), wax=flat(R["acc"], 0.74, bevel=0.1), flame=fire(R["glow"], 0.4, 0.6), book=flat(ramp("#14141e", "#22222e", "#30303e"), 0.6, bevel=0.14))
    b = Bow(k, L=10)
    b.limb(lambda s: 1.8 - 0.7 * s, "silver")
    for s in (1, -1):
        q = b.c(s * 0.95)
        x, y = b.w(q)
        b.put(rect(x - 0.7, y, x + 0.7, y + 2.6), 1.4, "wax")
        b.put(P((x - 0.8, y + 2.6), (x + 0.8, y + 2.6), (x + 0.2, y + 5)), 1.0, "flame", True)
        b.along(s * 0.9, s * 0.5, 0.3, 0.7, "wax")
    grip(b, "book", 3.2, 4.0)
    b.string("acc")
    b.shaft()


@design("tourniquet_bow")
def tourniquet_bow(k):
    """a spring steel strap with a surgeon's turn-screw at the grip: you wind it tighter until the bow, or something else, gives"""
    R = k.theme("plague", base=0.6)
    k.mat(strap=flat(R["blade"], 0.7, bevel=0.1), brass=flat(R["dark"], 0.64), gauze=flat(R["wrap"], 0.72, bevel=0.06))
    b = Bow(k)
    b.limb(lambda s: 1.3, "strap")
    for s in (-0.6, -0.3, 0.3, 0.6):
        b.band(s, 2.0, 1.0, "gauze", 1.7)
    grip(b, "brass", 2.8, 3.4)
    b.tri(0, 0, 3.0, 0.9, "brass", 1.0, off=-3.4)
    q = b.c(0, -3.4)
    b.put(b.P([(q[0] - 2, q[1]), (q[0] + 2, q[1]), (q[0] + 2, q[1] - 0.8), (q[0] - 2, q[1] - 0.8)]), 1.0, "brass")
    b.string("strap")
    b.shaft()


@design("suture_bow")
def suture_bow(k):
    """a bow sewn together from pieces: a seam of black stitches up both limbs with the green leaking through them, a curved needle at each tip"""
    R = k.theme("plague", base=0.56)
    k.mat(skin=flat(ramp("#7e6a58", "#9c8872", "#baa68e", "#d4c2aa"), 0.6, bevel=0.1), brass=flat(R["dark"], 0.62), needle=flat(R["blade"], 0.84))
    b = Bow(k, L=10)
    b.limb(lambda s: 2.3 - 1.0 * s, "skin")
    b.along(-0.86, 0.86, 0.0, 0.4, "glow", glow=True)
    for j in range(13):
        s = -0.84 + j * 0.14
        b.band(s, 1.8, 0.3, "dark", 1.6)
    for s in (1, -1):
        b.tri(s * 1.0, s * 3.0, -1.8, 0.7, "needle", 0.6)
    grip(b, "wrap", 2.8, 3.4)
    b.string("acc")
    b.shaft()


@design("shardstring_bow")
def shardstring_bow(k):
    """white temple stone with mana crystals grown out along the back, thin gold at the grip"""
    R = k.theme("temple", base=0.7)
    k.mat(stone=flat(R["blade"], 0.74, bevel=0.08), gold=flat(R["acc"], 0.64), crystal=flat(R["glow"], 0.7, bevel=0.14))
    b = Bow(k)
    b.limb(lambda s: 2.0 - 0.9 * s, "stone")
    for s, ln in ((0.25, 3.2), (0.5, 3.8), (0.75, 2.6), (-0.25, 3.0), (-0.5, 3.6), (-0.75, 2.8)):
        b.tri(s, 0.8 if s > 0 else -0.8, ln, 1.3, "crystal", 1.1)
    grip(b, "gold", 2.6, 3.0)
    b.string("glow", glow=True)
    b.shaft()


@design("starfall_bow")
def starfall_bow(k):
    """white gold with a star at each tip and one over the grip, a trail of small lights running down the limbs from them"""
    R = k.theme("temple", base=0.7)
    k.mat(gold=flat(R["acc"], 0.7, bevel=0.1), star=fire(ramp("#7ab0ff", "#b0d4ff", "#e0f0ff", "#ffffff"), 0.5, 0.5))
    b = Bow(k, L=10.4, bulge=3.8)
    b.limb(lambda s: 2.0 - 1.0 * s, "gold")
    for s in (1, -1):
        x, y = b.w(b.c(s * 0.98))
        b.put(P((x, y + 3), (x + 0.8, y + 0.8), (x + 3, y), (x + 0.8, y - 0.8), (x, y - 3), (x - 0.8, y - 0.8), (x - 3, y), (x - 0.8, y + 0.8)), 1.0, "star", True)
        for f in (0.75, 0.55, 0.38):
            b.dot(s * f, 0.42, "star", d=1.7, glow=True, n=5)
    x, y = b.w(b.c(0, 3.2))
    b.put(P((x, y + 2.2), (x + 0.6, y + 0.6), (x + 2.2, y), (x + 0.6, y - 0.6), (x, y - 2.2), (x - 0.6, y - 0.6), (x - 2.2, y), (x - 0.6, y + 0.6)), 1.0, "star", True)
    grip(b, "wrap", 2.6, 3.0)
    b.string("acc")
    b.shaft()


@design("brass_recurve")
def brass_recurve(k):
    """a machined recurve, brass lapped over bone, limbs kicking hard forward at the tips, a small cog at the grip"""
    R = k.theme("ossuary")
    k.mat(brass=flat(R["dark"], 0.66, bevel=0.1), bone=bone(R["acc"], 0.68))
    b = Bow(k, curl=3.2, tips=0.6, bulge=2.8)
    b.limb(lambda s: 1.9 - 0.8 * s, "bone")
    b.along(-0.9, 0.9, 0.4, 0.8, "brass", 1.7)
    x, y = b.w(b.c(0))
    for j in range(8):
        a = j * math.pi / 4
        b.put(disc(x + math.cos(a) * 2.4, y + math.sin(a) * 2.4, 0.6, 6), 1.8, "brass")
    b.put(disc(x, y, 2.3, 12), 2.0, "brass")
    b.put(disc(x, y, 0.9, 8), 2.2, "glow", True)
    b.string("edge")
    b.shaft()


@design("steam_arbalest")
def steam_arbalest(k):
    """not a bow at all: a short steel prod on a brass stock with a boiler on it, a piston does the drawing and the bolt comes out hissing"""
    R = k.theme("ossuary")
    k.mat(brass=flat(R["dark"], 0.64, bevel=0.14), iron=flat(R["blade"], 0.6, bevel=0.14))
    b = Bow(k, L=8.4, bulge=1.6, curl=0.8, rig=0.2)
    b.limb(lambda s: 2.0 - 0.8 * s, "iron")
    s0 = (0, -7.0)
    e = (0, b.c(0)[1] + 2)
    b.put(b.L_([s0, e], 2.4), 2.2, "brass")
    b.put(b.P([(-2.0, -5.6), (2.0, -5.6), (2.0, -1.6), (-2.0, -1.6)]), 3.0, "iron")
    b.put(b.P([(-1.0, -4.8), (1.0, -4.8), (1.0, -2.4), (-1.0, -2.4)]), 3.2, "glow", True)
    grip(b, "dark", 3.0, 3.0, 2.6)
    b.string("edge")
    b.shaft()


@design("bellows_bow")
def bellows_bow(k):
    """a smith's bellows at the grip feeds two iron limbs like pipes, each tip a little forge mouth that breathes when the string is drawn"""
    R = k.theme("foundry")
    k.mat(iron=flat(ramp("#14120f", "#221f1b", "#332f2a", "#46403a", "#5e564e", "#7a7065"), 0.66, bevel=0.14), leather=flat(LEATHER, 0.8, bevel=0.14), flame=fire(HOT, 0.2, 0.8))
    b = Bow(k, L=10)
    b.limb(lambda s: 2.0 - 0.3 * s, "iron")
    b.along(-0.9, 0.9, 0.3, 0.5, "glow", glow=True, d=2.06)
    for s in (1, -1):
        x, y = b.w(b.c(s * 0.97))
        b.put(disc(x, y, 1.5, 8), 2.2, "iron")
        b.put(P((x - 1.2, y), (x + 1.2, y), (x, y + 2.4 + 2.4 * k.pull)), 1.0, "flame", True)
    q = b.c(0)
    b.put(b.P([(-3.2, q[1] - 1.2), (3.2, q[1] - 1.2), (2.0, q[1] + 3.4 - 1.4 * k.pull), (-2.0, q[1] + 3.4 - 1.4 * k.pull)]), 2.6, "leather")
    b.string("edge")
    b.shaft()


@design("frostbound_longbow")
def frostbound_longbow(k):
    """a tall ash longbow of the March, rimed white along its back, icicles hanging from its lower edge"""
    R = k.theme("frost", base=0.54)
    k.mat(ash=staves(R["wood"], 1.0, 0.6), ice=flat(R["glow"], 0.7, bevel=0.14), white=flat(R["glow"], 0.92, bevel=0.02))
    b = Bow(k, L=11.2, bulge=2.8, curl=0.3)
    b.limb(lambda s: 1.9 - 0.8 * s, "ash")
    b.along(-0.86, 0.86, 0.4, 0.5, "white", 1.6)
    for s, ln in ((0.6, 2.4), (0.25, 3.0), (-0.3, 2.6), (-0.65, 3.2)):
        b.tri(s, -0.2, -ln, 0.9, "ice", 0.9)
    grip(b, "wrap", 2.6, 3.6)
    b.string("white")
    b.shaft()


@design("hoarfrost_bow")
def hoarfrost_bow(k):
    """it has stopped being wood: feathered ice crystals branch off a pale bow on both sides, a snow crystal shut in the grip"""
    R = k.theme("frost", base=0.54)
    k.mat(ice=flat(R["glow"], 0.74, bevel=0.14), white=flat(R["glow"], 0.92, bevel=0.04))
    b = Bow(k, L=10.4)
    b.limb(lambda s: 2.1 - 1.0 * s, "ice")
    for s in (0.25, 0.45, 0.65, 0.84, -0.25, -0.45, -0.65, -0.84):
        for dv in (3.0, -2.2):
            b.tri(s, 1.2 if s > 0 else -1.2, dv * (1.2 - abs(s) * 0.6), 0.8, "white", 0.9)
    b.dot(0, 2.2, "ice", d=2.4)
    b.dot(0, 1.2, "glow", d=2.6, glow=True)
    b.string("white")
    b.shaft()


@design("silkstring_bow")
def silkstring_bow(k):
    """a spare black bow bound every inch in white thread, the string so fine you only see it when it moves"""
    R = k.theme("silk")
    k.mat(thread=stripes(R["acc"], R["dark"], 0.8, 0.9, 0.6))
    b = Bow(k)
    b.limb(lambda s: 1.6 - 0.7 * s, "thread")
    grip(b, "wrap", 2.4, 3.4)
    b.string("acc", 0.25)
    b.shaft()


@design("webcaster")
def webcaster(k):
    """the Queen's bow: a pair of spider's legs with real web slung in the angle between grip and tip, and a bright little spider sitting in it"""
    R = k.theme("silk")
    k.mat(leg=flat(R["dark"], 0.76, bevel=0.2), web=flat(R["acc"], 0.86, bevel=0))
    b = Bow(k, L=10.4, bulge=4.4, curl=0.8)
    b.limb(lambda s: 1.7 - 0.5 * s, "leg")
    for s in (-0.66, -0.33, 0.33, 0.66):
        b.band(s, 2.6, 0.7, "leg", 1.8)
    for s in (1, -1):
        for f in (0.35, 0.6, 0.85):
            a, c = b.w(b.c(s * f)), b.w(b.c(s * f * 0.35, -2))
            k.seg(a, c, 0.2, 0.2, "web", z=BZ)
    q = b.c(0, -1.6)
    for f in (0.3, 0.5):
        k.seg(b.w(q), b.w(b.c(f)), 0.2, 0.2, "web", z=BZ)
        k.seg(b.w(q), b.w(b.c(-f)), 0.2, 0.2, "web", z=BZ)
    b.dot(0, 1.3, "leg", dv=-1.6, d=1.8)
    b.dot(0, 0.5, "glow", dv=-1.6, d=2.0, glow=True, n=6)
    grip(b, "wrap", 2.6, 2.8)
    b.string("acc")
    b.shaft()


@design("lampwick_bow")
def lampwick_bow(k):
    """a pit prop stave with a miner's safety lamp lashed to the grip and a length of lamp wick for the string"""
    R = k.theme("weeping_mine")
    k.mat(copper=flat(R["acc"], 0.6), lamp=fire(R["glow"], 0.4, 0.6), oak=staves(R["wood"], 1.2, 0.6), wick=flat(ramp("#b0a888", "#d0c8a8", "#ece4c8"), 0.6))
    b = Bow(k)
    b.limb(lambda s: 2.0 - 0.9 * s, "oak")
    grip(b, "wrap", 2.6, 3.4)
    q = b.c(0, 2.6)
    x, y = b.w(q)
    b.put(rect(x - 1.2, y - 1.6, x + 1.2, y + 1.6), 2.2, "lamp", True)
    b.put(rect(x - 1.5, y - 2.2, x + 1.5, y - 1.5) + rect(x - 1.5, y + 1.5, x + 1.5, y + 2.2), 2.4, "copper")
    b.string("wick", 0.45)
    b.shaft()


@design("deep_seam_bow")
def deep_seam_bow(k):
    """the limbs are the seam: two long crystals growing out of a copper grip, teal fire inside, and they flex, which they should not"""
    R = k.theme("weeping_mine")
    k.mat(crystal=flat(R["glow"], 0.72, bevel=0.14), copper=wrap(ramp("#3a1a08", "#6a3414", "#9c5a24", "#c8843c"), None, 2))
    b = Bow(k, L=10.4, bulge=3.0, curl=0.6)
    b.limb(lambda s: 3.0 - 2.4 * s, "crystal", 2.2)
    b.limb(lambda s: 1.2 - 0.9 * s, "glow", 2.4, glow=True, s0=-0.9, s1=0.9)
    for s, ln in ((0.5, 3.0), (0.25, 2.2), (-0.4, 3.0)):
        b.tri(s, 1.2 if s > 0 else -1.2, ln, 1.4, "crystal", 1.4)
    grip(b, "copper", 3.0, 4.6, 2.8)
    b.string("edge")
    b.shaft()


@design("driftwood_bow")
def driftwood_bow(k):
    """a silver piece of driftwood that happened to be the right shape, two barnacles, a loop of net cord"""
    R = k.theme("tide_chapel")
    k.mat(drift=staves(R["wood"], 1.0, 0.66), crust=flat(R["acc"], 0.72, bevel=0.1), cord=flat(R["acc"], 0.6))
    b = Bow(k, wob=lambda s: 0.5 * math.sin(s * 8 + 0.6))
    b.limb(lambda s: 2.3 - 1.1 * s, "drift")
    for s, r_ in ((0.5, 0.9), (0.62, 0.7), (-0.46, 0.9)):
        b.dot(s, r_, "crust", d=2.0)
    grip(b, "wrap", 2.8, 3.4)
    b.string("cord")
    b.shaft()


@design("shoreline_bow")
def shoreline_bow(k):
    """sea bronze cast in the curve of a breaking wave, limbs ending in curled crests, a pearl at the grip and shells up its back"""
    R = k.theme("tide_chapel")
    bronze = ramp("#0e2420", "#163a30", "#205244", "#2e6e5a", "#448c74", "#6cb094", "#a8d8bc")
    k.mat(bronze=flat(bronze, 0.6, bevel=0.1), pearl=flat(R["glow"], 0.88), shell=flat(R["acc"], 0.72, bevel=0.12))
    b = Bow(k, L=9.8, curl=2.6, tips=0.7)
    b.limb(lambda s: 2.2 - 0.8 * s, "bronze")
    for s in (0.3, 0.55, -0.3, -0.55):
        b.tri(s, 1.8 if s > 0 else -1.8, 2.4, 1.6, "bronze", 1.3)
    for s in (0.15, -0.15, 0.45, -0.45):
        b.dot(s, 0.7, "shell", dv=0.3, d=1.8)
    b.dot(0, 1.3, "pearl", d=2.4)
    grip(b, "wrap", 2.4, 2.2, 1.9)
    b.dot(0, 1.3, "pearl", d=2.4)
    b.string("acc")
    b.shaft()


@design("ambush_bow")
def ambush_bow(k):
    """short, dark and quiet: a horse-archer's stave wrapped in sacking so it won't shine"""
    R = k.theme("brigands_gorge", base=0.46)
    k.mat(oak=staves(R["wood"], 0.9, 0.5), sack=wrap(RAG, RAG[0], 3))
    b = Bow(k, L=7.8, bulge=3.0, curl=1.6)
    b.limb(lambda s: 2.2 - 1.2 * s, "oak")
    b.limb(lambda s: 2.6, "sack", 1.8, s0=-0.5, s1=0.5)
    b.string("acc")
    b.shaft()


@design("gorge_longbow")
def gorge_longbow(k):
    """Red Jack's great bow: red lacquer, gold nocks, a string of stolen coins swinging from the lower limb"""
    R = k.theme("brigands_gorge")
    k.mat(red=flat(R["wrap"], 0.66, bevel=0.1), gold=flat(GOLD, 0.68, bevel=0.1))
    b = Bow(k, L=11.2, bulge=3.2, curl=0.6)
    b.limb(lambda s: 2.2 - 1.0 * s, "red")
    for s in (0.94, -0.94):
        b.band(s, 2.2, 1.6, "gold", 2.0)
    for s in (0.55, 0.25, -0.25, -0.55):
        b.band(s, 2.6, 0.5, "gold", 1.8)
    x, y = b.w(b.c(-0.7))
    for j in range(4):
        b.put(disc(x + 0.5 + j * 0.3, y - 1.6 - j * 1.7, 0.9, 8), 0.5, "gold")
    grip(b, "wrap", 2.8, 3.8)
    b.string("acc")
    b.shaft()


@design("crowfletch_bow")
def crowfletch_bow(k):
    """a hedge archer's bow hung with crow feathers on thread, a bird skull at the grip"""
    R = k.theme("rookery")
    k.mat(ash=staves(R["acc"], 1.0, 0.56), f=flat(R["blade"], 0.5, bevel=0.14), bone=bone(IVORY, 0.72))
    b = Bow(k)
    b.limb(lambda s: 1.9 - 0.8 * s, "ash")
    for s in (0.7, 0.45, -0.45, -0.7):
        x, y = b.w(b.c(s, -0.4))
        b.put(P((x, y), (x - 0.8, y - 2.4), (x + 0.4, y - 5.0), (x + 1.2, y - 2.2)), 0.5, "f")
    grip(b, "wrap", 2.6, 3.0)
    b.dot(0, 1.3, "bone", dv=1.8, d=2.0)
    b.string("edge")
    b.shaft()


@design("raven_bow")
def raven_bow(k):
    """two wings stiffened into limbs, primaries raked back along the whole length, an eye glowing at the grip"""
    R = k.theme("rookery")
    k.mat(bone=bone(R["acc"], 0.68), f1=flat(R["blade"], 0.44, bevel=0.14), f2=flat(R["blade"], 0.6, bevel=0.14))
    b = Bow(k, L=10.2, bulge=3.0, curl=0.8)
    for j, s in enumerate((0.2, 0.34, 0.48, 0.62, 0.76, 0.9, -0.2, -0.34, -0.48, -0.62, -0.76, -0.9)):
        b.tri(s, 1.2 if s > 0 else -1.2, -4.2 + abs(s), 1.7, "f2" if j % 2 else "f1", 0.8)
    b.limb(lambda s: 1.8 - 0.8 * s, "bone")
    b.dot(0, 1.4, "bone", d=2.2)
    b.dot(0, 0.7, "glow", d=2.4, glow=True)
    b.string("edge")
    b.shaft()


@design("trick_bow")
def trick_bow(k):
    """a circus archer's bow: barber-striped limbs, gold stars on the tips and a little flag that says what it says"""
    R = k.theme("hollow_circus")
    red = ramp("#2a0408", "#4e0810", "#7a1018", "#a81c20", "#d0302a", "#ee5a44")
    cream = ramp("#6a5a44", "#8e7c60", "#b4a282", "#d6c8a8", "#efe4c8", "#fff8e8")
    k.mat(st=stripes(red, cream, 1.6, 1.0), gold=flat(GOLD, 0.68), flag=flat(ramp("#0e1a3a", "#182a54", "#22386c", "#304a86"), 0.66))
    b = Bow(k)
    b.limb(lambda s: 2.0 - 0.8 * s, "st")
    for s in (1, -1):
        x, y = b.w(b.c(s * 0.98))
        b.put(P(*[(x + math.cos(a * math.pi / 5 + 1.57) * (1.7 if a % 2 == 0 else 0.7), y + math.sin(a * math.pi / 5 + 1.57) * (1.7 if a % 2 == 0 else 0.7)) for a in range(10)]), 1.0, "gold")
    x, y = b.w(b.c(0.6, 1))
    b.put(P((x, y), (x + 4.4, y + 0.8), (x + 3.4, y - 0.4), (x + 4.4, y - 1.6), (x, y - 1.6)), 0.4, "flag")
    grip(b, "wrap", 2.6, 3.2)
    b.string("acc")
    b.shaft()


@design("calliope_bow")
def calliope_bow(k):
    """the steam calliope's pipes run along its back in gold, shortest at the tips, and when the string sings they answer"""
    R = k.theme("hollow_circus")
    k.mat(red=flat(R["wrap"], 0.6, bevel=0.1), gold=flat(GOLD, 0.68, bevel=0.14))
    b = Bow(k, L=10.2)
    for s_ in (1, -1):
        for j in range(7):
            s = s_ * (0.14 + j * 0.12)
            q = b.c(s, 0.2)
            h = 6.4 - j * 0.6
            b.put(b.P([(q[0] - 0.46, q[1]), (q[0] + 0.46, q[1]), (q[0] + 0.46, q[1] + h), (q[0] - 0.46, q[1] + h)]), 1.1, "gold")
    b.limb(lambda s: 2.2 - 0.8 * s, "red", 1.7)
    grip(b, "gold", 2.8, 3.0)
    b.string("edge")
    b.shaft()


@design("willow_bow")
def willow_bow(k):
    """a green willow switch that never dried out: long leaves still hanging from it, bending the way a willow bends"""
    R = k.theme("mirefen_coven")
    k.mat(wood=staves(ramp("#3a3414", "#5a5220", "#7c7230", "#a09844"), 1.0, 0.56), leaf=flat(R["wrap"], 0.66, bevel=0.1))
    b = Bow(k, L=9.8, bulge=3.0, curl=0.6)
    b.limb(lambda s: 1.5 - 0.7 * s, "wood")
    for s in (0.85, 0.6, 0.35, -0.35, -0.6):
        x, y = b.w(b.c(s))
        b.put(wave(lambda t, x=x: x + 0.8 * t, lambda t: 0.6 * math.sin(t * 3.14) + 0.1, y, y - 6, 8), 0.4, "leaf")
    grip(b, "wrap", 2.6, 3.2)
    b.string("acc")
    b.shaft()


@design("wisp_bow")
def wisp_bow(k):
    """bog oak with a little cage at each tip, and in each cage a marsh light that does not want to be there"""
    R = k.theme("mirefen_coven")
    k.mat(oak=staves(ramp("#14100c", "#201a12", "#2e261a", "#3e3424", "#52462f"), 1.0, 0.62), cage=flat(IRON, 0.7), wisp=fire(R["glow"], 0.3, 0.7))
    b = Bow(k, L=9.6)
    b.limb(lambda s: 2.0 - 0.8 * s, "oak")
    for s in (1, -1):
        b.dot(s * 0.96, 1.7, "wisp", d=1.6, glow=True)
        x, y = b.w(b.c(s * 0.96))
        b.put(ring(x, y, 2.2, 1.7), 2.0, "cage")
        b.put(rect(x - 0.2, y - 2.2, x + 0.2, y + 2.2) + rect(x - 2.2, y - 0.2, x + 2.2, y + 0.2), 2.0, "cage")
    grip(b, "wrap", 2.6, 3.2)
    b.string("glow", glow=True)
    b.shaft()


@design("reed_bow")
def reed_bow(k):
    """Nile reeds bound with blue thread in the old way, a composite bow small enough to shoot from a chariot"""
    k.theme("sandsunk_tomb")
    reed = ramp("#3a3414", "#5a5220", "#7c7230", "#a09844", "#c4bc60", "#e0d88c")
    lapis = ramp("#081a4a", "#0e2a6e", "#163e96", "#2458c0", "#4a84e0")
    k.mat(reed=staves(reed, 0.6, 0.6), blue=flat(lapis, 0.56), gold=flat(GOLD, 0.66))
    b = Bow(k, L=8.8, bulge=2.2, curl=2.6, tips=0.6)
    b.limb(lambda s: 2.4 - 1.2 * s, "reed")
    for s in (-0.8, -0.6, -0.4, -0.2, 0.2, 0.4, 0.6, 0.8):
        b.band(s, 2.8 - abs(s) * 1.2, 0.5, "blue", 1.8)
    grip(b, "gold", 2.6, 2.4)
    b.string("edge")
    b.shaft()


@design("horizon_bow")
def horizon_bow(k):
    """the bow of the sun barque: a long flat gold crescent, the sun's disc riding the grip, rays and lapis along it"""
    k.theme("sandsunk_tomb")
    lapis = ramp("#081a4a", "#0e2a6e", "#163e96", "#2458c0", "#4a84e0")
    k.mat(gold=flat(GOLD, 0.68, bevel=0.1), blue=flat(lapis, 0.56), sun=fire(ramp("#e07010", "#ffa81c", "#ffd84a", "#fff4a8"), 0.3, 0.7))
    b = Bow(k, L=10.8, bulge=3.0, curl=1.4)
    b.limb(lambda s: 2.6 - 1.4 * s, "gold")
    b.along(-0.7, 0.7, 0, 0.6, "blue", 1.6)
    x, y = b.w(b.c(0, 1.6))
    for j in range(12):
        a = j * math.pi / 6
        b.put(P((x + math.cos(a - 0.26) * 2.0, y + math.sin(a - 0.26) * 2.0), (x + math.cos(a) * 3.8, y + math.sin(a) * 3.8), (x + math.cos(a + 0.26) * 2.0, y + math.sin(a + 0.26) * 2.0)), 1.0, "sun", True)
    b.put(disc(x, y, 2.4, 12), 2.4, "sun", True)
    b.string("edge")
    b.shaft()


@design("sinew_bow")
def sinew_bow(k):
    """Titan rib and raw sinew: the belly bone, the back a long red cord of tendon glued down its length"""
    k.theme("fallen_titan")
    meat = ramp("#2a0608", "#4a0c10", "#6e161a", "#942428", "#b83c3a")
    k.mat(bone=bone(IVORY, 0.7), sinew=flat(meat, 0.6, 0.2), wrap=wrap(meat, meat[0], 4))
    b = Bow(k, L=9.8)
    b.limb(lambda s: 2.3 - 1.0 * s, "bone")
    b.along(-0.92, 0.92, 0.6, 0.8, "sinew", 1.7)
    grip(b, "wrap", 2.8, 3.2)
    b.string("sinew", 0.45)
    b.shaft()


@design("tendon_bow")
def tendon_bow(k):
    """the Titan's arm in small: bulging muscle for limbs, tendons running to the tips, a heartbeat's glow going through it each time it's drawn"""
    meat = ramp("#2a0608", "#4a0c10", "#6e161a", "#942428", "#b83c3a", "#d8625a")
    k.theme("fallen_titan")
    k.mat(muscle=flat(meat, 0.58, 0.2, bevel=0.14), bone=bone(IVORY, 0.76), hot=fire(ramp("#e02830", "#ff6a5a", "#ffc0a8", "#ffffff"), 0.3, 0.7), wrap=wrap(meat, meat[0], 4))
    b = Bow(k, L=10)
    b.limb(lambda s: (3.2 + k.pull * 0.8) * (1 - s ** 2) + 1.0, "muscle", 2.4)
    b.along(-0.7, 0.7, 0.0, 0.5, "hot", 2.46, glow=True)
    for s in (1, -1):
        b.limb(lambda t: 0.9, "bone", 1.4, s0=s * 0.74, s1=s * 1.0)
    grip(b, "wrap", 3.6, 2.8, 2.8)
    b.string("bone", 0.45)
    b.shaft()


@design("bamboo_bow")
def bamboo_bow(k):
    """a single green bamboo, the nodes showing, a monk's cord at the grip"""
    R = k.theme("jade_monastery")
    bam = ramp("#2a4a14", "#3e6a1e", "#5a8e2c", "#7cb040", "#a4d05c")
    k.mat(bam=flat(bam, 0.56, bevel=0.1), node=flat(bam, 0.92, bevel=0.0), red=wrap(ramp("#3a0608", "#600c0e", "#8a1416", "#b42020"), None, 3))
    b = Bow(k, L=10.2, bulge=2.8, curl=0.2)
    b.limb(lambda s: 1.9, "bam")
    for s in (-0.8, -0.56, -0.32, 0.32, 0.56, 0.8):
        b.band(s, 2.2, 0.5, "node", 1.8)
    grip(b, "red", 2.4, 3.4)
    b.string("acc")
    b.shaft()


@design("moon_gate_bow")
def moon_gate_bow(k):
    """the round gate in the monastery garden: a full circle of jade, broken only by the string's gap, gold at the hinge"""
    R = k.theme("jade_monastery", base=0.56)
    k.mat(jade=flat(R["blade"], 0.68, bevel=0.14), gold=flat(GOLD, 0.68, bevel=0.14), tass=flat(ramp("#3a0608", "#600c0e", "#8a1416", "#b42020"), 0.6, 0.2))
    p = k.pull

    def c(self, s, dv=0.0):
        a = s * 2.2
        r_ = 8.4 + 0.2 * p - dv
        return (math.sin(a) * r_ * (1 - 0.05 * p), math.cos(a) * r_ * (1 - 0.02 * p) - 5.0 - 2.4 * p * s * s)

    b = Bow(k)
    b.c = c.__get__(b)
    b.limb(lambda s: 2.2 - 0.6 * s, "jade", 1.8, n=30)
    b.along(-0.9, 0.9, 0, 0.4, "gold", 1.86, n=24)
    b.band(0, 3.0, 3.6, "gold", 2.4)
    for s in (1, -1):
        b.dot(s * 0.98, 1.0, "gold", d=2.2)
    b.string("acc")
    b.shaft()


@design("thunderhead_bow")
def thunderhead_bow(k):
    """storm iron with a black cloud gathered round the grip, a copper rod at each tip and little jumps of blue between them"""
    R = k.theme("storm_bastion")
    k.mat(iron=flat(R["dark"], 0.66, bevel=0.12), cloud=flat(R["blade"], 0.4, 0.2, bevel=0.14), copper=flat(ramp("#6a3414", "#9c5a24", "#c8843c", "#e8a860"), 0.6), white=flat(R["glow"], 0.92, bevel=0.02))
    b = Bow(k)
    b.limb(lambda s: 2.0 - 0.8 * s, "iron")
    for s, dv, r_ in ((0, 1.6, 3.0), (0.25, 1.2, 2.2), (-0.25, 1.2, 2.2), (0.12, -0.4, 2.0), (-0.14, -0.4, 2.0)):
        b.dot(s, r_, "cloud", dv=dv, d=3.0, n=9)
    for s in (1, -1):
        b.tri(s * 0.98, s * 3.0, 0.4, 0.8, "copper", 0.8)
    b.put(b.L_([b.c(0.55, 0.4), b.c(0.45, 2.0), b.c(0.35, 0.8), b.c(0.28, 2.6)], 0.4), 0.5, "white", True)
    b.string("white", glow=True)
    b.shaft()


@design("bolt_of_heaven")
def bolt_of_heaven(k):
    """the bow is the lightning: two hard zigzags of white fire meeting at a black iron grip, a string you shouldn't touch"""
    R = k.theme("storm_bastion")
    k.mat(iron=flat(R["dark"], 0.66, bevel=0.14), bolt=fire(R["glow"], 0.35, 0.65), white=flat(R["glow"], 0.92, bevel=0.02))
    b = Bow(k, L=10.6, wob=lambda s: 1.5 * (1 if int((s + 2) * 3.5) % 2 else -1) * min(1, abs(s) * 4))
    b.limb(lambda s: 2.2 - 1.3 * s, "bolt", 1.5, n=30, glow=True)
    b.limb(lambda s: 0.7, "white", 1.7, n=30, glow=True)
    grip(b, "iron", 3.0, 3.6, 2.6)
    b.string("white", 0.3, glow=True)
    b.shaft()


@design("crimson_bow")
def crimson_bow(k):
    """a duellist's lady's bow: black lacquer inside, red out, gold silk at the grip, tips turned like a violin's"""
    R = k.theme("bloodmoon_court")
    k.mat(red=flat(ramp("#2a0408", "#4e0810", "#7a1018", "#a81c20", "#c4302a"), 0.6, bevel=0.1), gold=flat(GOLD, 0.66), blackl=flat(ramp("#14040a", "#280a12", "#42101c"), 0.6))
    b = Bow(k, curl=2.4, tips=0.72)
    b.limb(lambda s: 2.0 - 0.8 * s, "red")
    b.along(-0.8, 0.8, -0.5, 0.6, "blackl", 1.6)
    for s in (1, -1):
        b.dot(s * 0.99, 1.0, "gold", d=1.8)
    grip(b, "gold", 2.6, 3.2)
    b.string("acc")
    b.shaft()


@design("bloodmoon_bow")
def bloodmoon_bow(k):
    """a thin red crescent with the full moon behind it, the moon's disc rising higher up the bow as it is drawn"""
    R = k.theme("bloodmoon_court")
    moon = ramp("#7a1408", "#b02a10", "#e04a1c", "#ff8040", "#ffc080")
    k.mat(red=flat(RUBY, 0.56, bevel=0.1), moon=fire(moon, 0.2, 0.7), silver=flat(IRON, 0.72))
    b = Bow(k, L=9.8, bulge=4.4, curl=1.0)
    x, y = b.w(b.c(0, -1.6 - 1.6 * k.pull))
    k.plate(disc(x, y, 5.4, 18), 0.7, "moon", z=BZ - 0.9, glow=True)
    b.limb(lambda s: 2.4 - 1.5 * s, "red")
    grip(b, "silver", 2.8, 2.8)
    b.string("edge")
    b.shaft()


@design("ember_bow")
def ember_bow(k):
    """Labyrinth basalt that remembers being lava, cracks glowing along black limbs"""
    R = k.theme("obsidian_labyrinth")
    k.mat(rock=flat(R["blade"], 0.5, 0.2, bevel=0.14), hot=fire(HOT, 0.3, 0.7))
    b = Bow(k)
    b.limb(lambda s: 2.2 - 0.8 * s, "rock")
    b.put(b.L_([b.c(-0.8, 0.2), b.c(-0.6, -0.5), b.c(-0.4, 0.4), b.c(-0.2, -0.3), b.c(0.1, 0.3), b.c(0.3, -0.4), b.c(0.5, 0.3), b.c(0.8, -0.2)], 0.4), 1.56, "hot", True)
    grip(b, "wrap", 2.6, 3.2)
    b.string("hot", glow=True)
    b.shaft()


@design("obsidian_longbow")
def obsidian_longbow(k):
    """a tall black glass bow built up of long knapped plates, each overlapping the next, the edge cutting the archer a little every time"""
    R = k.theme("obsidian_labyrinth")
    glass = ramp("#050408", "#100c18", "#1e1630", "#32244e", "#50387a", "#7c58b0", "#c0a0f0")
    k.mat(g=flat(glass, 0.5, bevel=0.3), g2=flat(glass, 0.66, bevel=0.3))
    b = Bow(k, L=11.6, bulge=2.8, curl=0.3)
    b.limb(lambda s: 2.0 - 1.0 * s, "g")
    for j, s in enumerate((-0.8, -0.6, -0.4, -0.2, 0.2, 0.4, 0.6, 0.8)):
        q = b.c(s)
        d = 1 if s > 0 else -1
        b.put(b.P([(q[0] - d * 0.8, q[1] - 0.9), (q[0] - d * 0.8, q[1] + 0.9), (q[0] + d * 2.6, q[1] + 1.4), (q[0] + d * 2.4, q[1] - 1.2)]), 1.7, "g2" if j % 2 else "g")
    grip(b, "wrap", 2.6, 3.6)
    b.string("glow", glow=True)
    b.shaft()


@design("deepline_bow")
def deepline_bow(k):
    """a long surf rod bent double, the string a fishing line, a hook and a sinker hanging from the top ring"""
    R = k.theme("abyssal_lighthouse")
    k.mat(rod=flat(R["dark"], 0.7, bevel=0.06), ring=flat(BRASS, 0.66), hook=flat(SILVER, 0.7), lure=fire(R["glow"], 0.4, 0.6))
    b = Bow(k, L=10.6, bulge=3.0, curl=0.3)
    b.limb(lambda s: 1.5 - 0.9 * s, "rod")
    for s in (0.8, 0.5, 0.25, -0.25, -0.5, -0.8):
        b.dot(s, 0.6, "ring", dv=-0.9, d=0.5, n=6)
    x, y = b.w(b.c(0.98))
    k.seg((x, y), (x + 1.6, y - 6), 0.2, 0.2, "ring", z=BZ)
    b.put(L(qb((x + 1.6, y - 6), (x + 2, y - 8), (x + 0.4, y - 7.6), 5), 0.4), 0.4, "hook")
    grip(b, "wrap", 2.6, 3.6)
    b.string("ring", 0.25)
    b.shaft()


@design("beam_bow")
def beam_bow(k):
    """a lens at the grip, and from it two blades of hard yellow light for limbs. The string is the only part that's solid"""
    R = k.theme("abyssal_lighthouse")
    k.mat(beam=fire(ramp("#e8b84a", "#ffdc7a", "#fff2b0", "#fffbe0"), 0.3, 0.7), iron=flat(IRON, 0.7), lens=flat(ramp("#94b8bc", "#c0dee0", "#e8fafa"), 0.6, bevel=0.2))
    b = Bow(k, L=10.2)
    b.limb(lambda s: 0.8 + 2.4 * s, "beam", 1.2, glow=True)
    b.along(-1.0, 1.0, 1.1, 0.4, "iron", 1.3, n=12)
    x, y = b.w(b.c(0))
    b.put(disc(x, y, 3.0, 14), 2.2, "iron")
    b.put(disc(x, y, 2.2, 12), 2.4, "lens")
    b.put(disc(x, y, 1.0, 8), 2.6, "beam", True)
    b.string("iron")
    b.shaft()


@design("wingbow")
def wingbow(k):
    """white feathers laid along a pale bow, a single gold band: pretty, if you don't ask what it was before"""
    k.theme("eclipse_cathedral", base=0.7)
    plume = ramp("#a0a0b4", "#c8c8d8", "#e8e8f0", "#ffffff")
    k.mat(w=flat(plume, 0.6, bevel=0.1), pale=flat(plume, 0.42, bevel=0.06), gold=flat(GOLD, 0.66))
    b = Bow(k, L=10, curl=0.8)
    b.limb(lambda s: 1.8 - 0.8 * s, "pale")
    for s in (0.2, 0.36, 0.52, 0.68, 0.84, -0.2, -0.36, -0.52, -0.68, -0.84):
        b.tri(s, 1.6 if s > 0 else -1.6, 2.8, 1.5, "w", 0.8)
    grip(b, "gold", 2.6, 2.8)
    b.string("edge")
    b.shaft()


@design("penumbra_bow")
def penumbra_bow(k):
    """the shadow's edge: black limbs inside a thin white corona that follows them exactly, a burnt-out sun at the grip"""
    k.theme("eclipse_cathedral", base=0.3)
    k.mat(void=flat(ramp("#000000", "#040408", "#0a0a10"), 0.5, bevel=0.1), corona=fire(ramp("#ffe08a", "#fff6d0", "#ffffff"), 0.4, 0.6))
    b = Bow(k, L=10)
    b.limb(lambda s: 3.0 - 1.4 * s, "corona", 1.0, glow=True)
    b.limb(lambda s: 2.2 - 1.4 * s, "void", 1.6)
    x, y = b.w(b.c(0))
    b.put(disc(x, y, 3.4, 14), 1.0, "corona", True)
    b.put(disc(x, y, 2.6, 14), 2.0, "void")
    b.string("edge")
    b.shaft()


@design("dragonbone_bow")
def dragonbone_bow(k):
    """a young dragon's wing bones, knuckled at the joints, gold wire where they meet, the tips still clawed"""
    k.theme("wyrms_hoard")
    k.mat(bone=bone(IVORY, 0.72), gold=flat(GOLD, 0.68), claw=flat(HORN, 0.7, bevel=0.14))
    b = Bow(k, L=10)
    b.limb(lambda s: 2.0 - 0.8 * s, "bone")
    for s in (-0.66, -0.33, 0.33, 0.66):
        b.dot(s, 1.4, "bone", d=2.0)
        b.band(s, 3.0, 0.4, "gold", 2.1)
    for s in (1, -1):
        b.tri(s * 1.0, s * 2.8, 1.2, 1.3, "claw", 1.2)
    grip(b, "wrap", 2.6, 3.0)
    b.string("gold")
    b.shaft()


@design("dragonbreath_bow")
def dragonbreath_bow(k):
    """a dragon's head at the grip, jaws opening as the bow is drawn, the fire showing behind its teeth; horns sweep out along the limbs"""
    k.theme("wyrms_hoard")
    k.mat(horn=flat(HORN, 0.72, bevel=0.14), scale=flat(GOLD, 0.54, bevel=0.2), hot=fire(HOT, 0.2, 0.8), gem=gem(RUBY), tooth=flat(IVORY, 0.9))
    b = Bow(k, L=10.2)
    b.limb(lambda s: 2.8 - 1.8 * s, "horn", 1.8)
    q = b.c(0)
    gape = 0.6 + 1.6 * k.pull
    b.put(b.P([(-3.2, q[1] - 1.2), (3.2, q[1] - 1.2), (2.6, q[1] + 1.2), (-2.6, q[1] + 1.2)]), 3.0, "scale")
    b.put(b.P([(0.6, q[1] + 1), (3.0, q[1] + 1), (gape + 0.4, q[1] + 6), (0.4, q[1] + 5)]), 2.4, "scale")
    b.put(b.P([(-0.6, q[1] + 1), (-3.0, q[1] + 1), (-gape - 0.4, q[1] + 6), (-0.4, q[1] + 5)]), 2.4, "scale")
    b.put(b.P([(-0.5, q[1] + 1.2), (0.5, q[1] + 1.2), (0.1, q[1] + 5.4), (-0.1, q[1] + 5.4)]), 1.6, "hot", True)
    b.dot(0.15, 0.7, "gem", dv=1.6, d=3.2)
    b.dot(-0.15, 0.7, "gem", dv=1.6, d=3.2)
    b.string("edge")
    b.shaft()


# ---------------------------------------------------------------- the world's

@design("hunters_bow")
def hunters_bow(k):
    """yew and gut string: heartwood belly, sapwood back, a hunter's bow"""
    k.mat(y=staves(ramp("#5a3214", "#7a4820", "#9a6030", "#bc7c44", "#d89a60"), 1.2, 0.6), sap=flat(ramp("#a89060", "#c8b080", "#e4cca0"), 0.6, bevel=0.06), wrap=wrap(LEATHER, IRON[1], 5), edge=flat(SILVER, 0.7), gut=flat(ramp("#a8987a", "#c8b898", "#e0d4b8"), 0.6), wood=staves(ramp("#3a2410", "#52341c", "#6e4826"), 1.0, 0.56), glow=flat(RUBY, 0.56))
    b = Bow(k)
    b.limb(lambda s: 2.0 - 0.9 * s, "y")
    b.along(-0.9, 0.9, 0.5, 0.6, "sap", 1.56)
    grip(b, "wrap", 2.6, 3.4)
    b.string("gut")
    b.shaft(fletch="gut", glow=False)


@design("raven_recurve")
def raven_recurve(k):
    """a black recurve, deep curled tips, raven feathers tied just below them"""
    black = ramp("#08080a", "#101014", "#18181e", "#22222a", "#2e2e38", "#3e3e4a", "#54545f")
    k.mat(b_=flat(black, 0.66, bevel=0.1), f=flat(ramp("#10101a", "#1a1a2a", "#28283e", "#3a3a56"), 0.6, bevel=0.14), wrap=wrap(black, SILVER[1], 4), silver=flat(SILVER, 0.6), wood=flat(black, 0.7), edge=flat(SILVER, 0.7), glow=flat(SILVER, 0.5))
    b = Bow(k, curl=3.6, tips=0.62, bulge=2.6)
    b.limb(lambda s: 2.0 - 1.0 * s, "b_")
    for s in (0.62, -0.62):
        b.band(s, 2.4, 0.7, "silver", 1.8)
        for f in (-1, 0, 1):
            b.tri(s, s * 1.0 + f * 0.8, -3.8, 1.0, "f", 0.6)
    grip(b, "wrap", 2.6, 3.0)
    b.string("silver")
    b.shaft(glow=False)


@design("stormstring")
def stormstring(k):
    """a plain grey war bow with a strand of lightning for a string: it never stays quite still, and neither do your arm hairs"""
    storm = ramp("#141a22", "#1e2630", "#2a3442", "#384454", "#485668", "#5c6c80", "#7a8a9e")
    bolt = ramp("#3f7fd0", "#7ab0ff", "#c8e4ff", "#ffffff")
    k.mat(b_=flat(storm, 0.6, bevel=0.1), hot=fire(bolt, 0.4, 0.6), wrap=wrap(storm, bolt[0], 4), wood=flat(storm, 0.7), edge=fire(bolt, 0.4, 0.6), glow=fire(bolt, 0.4, 0.6))
    b = Bow(k)
    b.limb(lambda s: 2.1 - 0.8 * s, "b_")
    grip(b, "wrap", 2.6, 3.2)
    b.string("hot", 0.5, glow=True)
    t0, t1 = b.c(-1), b.c(1)
    n = b.nock
    pts = [(t0[0] + (n[0] - t0[0]) * f, t0[1] + (n[1] - t0[1]) * f + (0.5 if j % 2 else -0.5)) for j, f in enumerate((0.25, 0.5, 0.75))]
    b.put(b.L_([t0] + pts + [n], 0.4), 0.5, "hot", True)
    pts = [(n[0] + (t1[0] - n[0]) * f, n[1] + (t1[1] - n[1]) * f + (-0.5 if j % 2 else 0.5)) for j, f in enumerate((0.25, 0.5, 0.75))]
    b.put(b.L_([n] + pts + [t1], 0.4), 0.5, "hot", True)
    b.shaft()


@design("phoenix_wing")
def phoenix_wing(k):
    """a phoenix's wing, bent into a bow and still burning: feathers of fire, red and gold, lifting off the limb and renewing"""
    flame = ramp("#a02206", "#e04a0a", "#ff8a1c", "#ffc84a", "#fff0b0", "#fffbe8")
    k.mat(b_=flat(ramp("#6a1a06", "#a02a08", "#d04a10", "#f07a20"), 0.6, bevel=0.1), f=fire(flame, 0.1, 0.8), f2=fire(flame, 0.3, 0.7), wrap=wrap(ramp("#4a1006", "#6a1a0a", "#8e2a10"), GOLD[4], 4), gold=flat(GOLD, 0.7), wood=flat(GOLD, 0.6), edge=flat(GOLD, 0.8), glow=fire(flame, 0.3, 0.7))
    b = Bow(k, L=10.4, curl=1.0)
    for j, s in enumerate((0.15, 0.3, 0.45, 0.6, 0.75, 0.9, -0.15, -0.3, -0.45, -0.6, -0.75, -0.9)):
        b.tri(s, 2.0 if s > 0 else -2.0, 5.0 - abs(s) * 2.6 + (j % 2), 1.8, "f2" if j % 2 else "f", 0.8, glow=True)
    b.limb(lambda s: 2.0 - 0.8 * s, "b_")
    grip(b, "wrap", 2.8, 3.0)
    b.string("gold")
    b.shaft()


@design("poachers_bow")
def poachers_bow(k):
    """short, quiet, and furred: rabbit skin wound round the limbs to stop the noise, a rabbit's foot on a string"""
    fur = ramp("#5a4a3a", "#7c6a58", "#9e8c78", "#c0b09c", "#dcd0be")
    k.mat(f=flat(fur, 0.6, 0.5, bevel=0.1), w_=staves(ramp("#2a1a0e", "#3a2616", "#4e3420", "#664428"), 0.9, 0.6), wrap=wrap(LEATHER, IRON[1], 5), gut=flat(ramp("#a8987a", "#c8b898"), 0.6), wood=flat(fur, 0.4), edge=flat(SILVER, 0.7), glow=flat(fur, 0.6))
    b = Bow(k, L=7.6, bulge=3.2, curl=1.0)
    b.limb(lambda s: 2.0 - 0.9 * s, "w_")
    b.limb(lambda s: 2.8, "f", 2.2, s0=-0.6, s1=0.6)
    x, y = b.w(b.c(-0.7))
    k.seg((x, y), (x + 0.6, y - 2.4), 0.2, 0.2, "gut", z=BZ)
    b.put(P((x, y - 2.2), (x + 1.4, y - 2.2), (x + 1.8, y - 5), (x + 0.4, y - 5.4)), 1.0, "f")
    b.string("gut")
    b.shaft(glow=False)


@design("thornbow")
def thornbow(k):
    """a living briar bent and left to grow that way: thorns all along it, two roses opening on the limbs, and it does drink a bit"""
    wood = ramp("#100806", "#1e0e0a", "#301610", "#461e16", "#5e281c")
    rose = ramp("#3a0410", "#6a0a1e", "#a0142e", "#d42a44", "#f4607a")
    k.mat(br=flat(wood, 0.7, bevel=0.1), th=flat(ramp("#4a3020", "#6e4c34", "#96704e"), 0.6), rose=flat(rose, 0.6, bevel=0.2), leaf=flat(ramp("#122a14", "#1c3e1c", "#285426", "#366c30"), 0.6), wrap=wrap(wood, rose[1], 4), wood=flat(wood, 0.7), edge=flat(rose, 0.8), glow=flat(rose, 0.8))
    b = Bow(k, L=9.8, wob=lambda s: 0.5 * math.sin(s * 9))
    b.limb(lambda s: 1.9 - 0.7 * s, "br")
    for j, s in enumerate((-0.82, -0.66, -0.5, -0.34, -0.18, 0.18, 0.34, 0.5, 0.66, 0.82)):
        b.tri(s, 0.9 if s > 0 else -0.9, 2.4 if j % 2 else -2.4, 0.8, "th", 0.9)
    for s in (0.55, -0.55):
        b.dot(s, 1.8, "rose", dv=1.0, d=2.4, n=9)
        b.dot(s, 0.8, "edge", dv=1.0, d=2.6, n=6)
    grip(b, "wrap", 2.6, 3.0)
    b.string("edge")
    b.shaft()


@design("kraken_bow")
def kraken_bow(k):
    """two kraken arms for limbs, thick at the grip and whip-thin at the tips, suckers down the inside, an ink-black eye with a gold slit watching over the arrow"""
    flesh = ramp("#1a0a24", "#2e1040", "#46185e", "#622480", "#8238a4")
    k.mat(arm=flat(flesh, 0.6, bevel=0.1), sucker=flat(ramp("#c8a0d8", "#e0c4ec", "#f4e4fa"), 0.6), eye=flat(ramp("#000000", "#080410"), 0.5, bevel=0.0), slit=fire(GOLD, 0.5, 0.5), wrap=wrap(flesh, flesh[0], 4), wood=flat(flesh, 0.5), edge=flat(SILVER, 0.7), glow=flat(GOLD, 0.7), ink=flat(flesh, 0.8))
    b = Bow(k, L=10.2, curl=1.8, tips=0.6, wob=lambda s: 0.4 * math.sin(s * 6))
    b.limb(lambda s: 3.4 * (1 - s) ** 0.8 + 0.5, "arm", 2.2)
    for s in (0.18, 0.32, 0.46, 0.6, -0.18, -0.32, -0.46, -0.6):
        b.dot(s, 0.65 - abs(s) * 0.4, "sucker", dv=-0.9 + abs(s) * 0.5, d=2.3, n=6)
    x, y = b.w(b.c(0, 0.6))
    b.put(disc(x, y, 2.4, 12), 2.8, "eye")
    b.put(disc(x, y, 2.6, 12) - disc(x, y, 2.2, 12), 2.6, "arm")
    b.put(b.L_([(0, b.c(0)[1] - 0.8), (0, b.c(0)[1] + 2.0)], 0.5), 3.0, "slit", True)
    b.string("ink")
    b.shaft()


@design("khans_horn")
def khans_horn(k):
    """the Salt Khan's great horn bow: ram's horns laminated to sinew and curling in full spirals at the tips, a sandstorm in its string that hisses on release"""
    k.mat(hn=flat(ramp("#3a2a1a", "#54402a", "#74583c", "#967650", "#b89668"), 0.62, bevel=0.1), ridge_=flat(ramp("#54402a", "#74583c", "#967650", "#b89668", "#d8b888"), 0.8, bevel=0.0), gold=flat(GOLD, 0.68), sand=fire(ramp("#a07028", "#d0a048", "#f0d080", "#fff0c0"), 0.3, 0.7), wrap=wrap(LEATHER, GOLD[3], 4), wood=flat(GOLD, 0.5), edge=flat(GOLD, 0.8), glow=fire(ramp("#a07028", "#d0a048", "#f0d080", "#fff0c0"), 0.3, 0.7))
    b = Bow(k, L=9.4, bulge=2.8, curl=0.6)
    b.limb(lambda s: 2.6 - 1.2 * s, "hn", 1.9)
    for s in (-0.8, -0.65, -0.5, -0.35, 0.35, 0.5, 0.65, 0.8):
        b.band(s, 2.6 - abs(s), 0.5, "ridge_", 2.0)
    for s_ in (1, -1):
        c0 = b.c(s_ * 0.98)
        pts = []
        for j in range(16):
            a = j * 0.42
            r_ = 3.2 * (1 - j / 18)
            pts.append((c0[0] + s_ * (math.sin(a) * r_ + 0.2), c0[1] + r_ - math.cos(a) * r_))
        b.put(b.L_(pts, 1.1), 1.8, "hn")
    grip(b, "gold", 2.8, 3.2)
    b.string("sand", 0.45, glow=True)
    b.shaft()


@design("twinstring")
def twinstring(k):
    """two bows on one grip, the iron one drawn inside the gold, two strings meeting in one nock"""
    fe = ramp("#2a2e34", "#3e444c", "#565e68", "#727c86", "#929ca6", "#b4bec6", "#d4dce2")
    k.mat(iron=flat(fe, 0.62, bevel=0.1), gold=flat(GOLD, 0.68, bevel=0.1), wrap=wrap(LEATHER, GOLD[3], 4), hot=fire(ramp("#ffb040", "#ffe8a0", "#fffbe0", "#ffffff"), 0.4, 0.6), wood=flat(IRON, 0.7), edge=flat(SILVER, 0.7), glow=fire(ramp("#ffb040", "#ffe8a0", "#fffbe0", "#ffffff"), 0.4, 0.6))
    a = Bow(k, L=10.6, bulge=4.4, curl=1.0)
    a.limb(lambda s: 1.6 - 0.7 * s, "gold")
    a.string("hot", 0.3, glow=True)
    b = Bow(k, L=8.2, bulge=2.6, curl=1.0)
    b.limb(lambda s: 1.6 - 0.7 * s, "iron")
    grip(b, "wrap", 2.8, 3.2)
    b.string("hot", 0.3, glow=True)
    b.shaft()
