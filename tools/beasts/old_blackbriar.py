"""Old Blackbriar: the forest's Legend. A hunched giant of black bramble wood: a stag's skull for a head under antlers
wider than it is, a hollow ribcage of branches with a green heart beating in it, crows nesting on its shoulders, long
arms ending in root claws that drag in the leaf litter. Biped (legendkit)."""
import math

from legendkit import X, C, ramp, W, grow, legs, arms, BIPED  # noqa: F401
import legendkit as L

GROW = 1.5
HITBOX = (3.2, 5.8)
IS_LEGEND = True
STATS = dict(hp=600, speed=0.25, dmg=22, armor=8, kb=1.0)
EGG, SPOTS = 0x2a2016, 0x6cd23a
BARK = ramp("#0c0907", "#16110c", "#211910", "#2d2216", "#3a2c1d", "#4a3a26")
THORN = ramp("#060407", "#0d0a0e", "#151017", "#1e1720", "#292030")
HEART = ramp("#1a5a0c", "#36921a", "#62cc2c", "#a2f05a", "#e0ffb0")


def antler(k, part, base, d, L_, w, tines, side):
    """an antler: a beam out along d with tines up off it"""
    n = math.sqrt(sum(c * c for c in d))
    d = tuple(c / n for c in d)
    end = tuple(base[i] + d[i] * L_ for i in range(3))
    k.limb(part, base, end, w, "antler", "antler", d=w)
    for i in range(tines):
        f = (i + 1) / (tines + 1)
        p = tuple(base[i2] + d[i2] * L_ * f for i2 in range(3))
        k.shard(part, p, (side * 0.15, 1, 0.25 - 0.2 * i), 7 - i * 0.8, w * 0.8, mat="antler", tag="tine")
    k.shard(part, end, (d[0], d[1] + 0.6, d[2]), 5, w * 0.8, mat="antler", tag="tine")


def thorns(k, part, pts, L_=3.2, w=1.0):
    for i, (p, d) in enumerate(pts):
        k.shard(part, p, d, L_ * (0.7 + 0.5 * X.h3(i, 3, 2)), w, mat="thorn", tag="thorn")


def old_blackbriar(name="old_blackbriar", legend=False):
    k = X.Kit(name)
    hips = k.part("hips", (0, 24, 0))
    k.blob(hips, (0, 25, 0), (10, 5, 7), "bark", "pelvis", step=1.0)
    for i in range(6):                                   # roots hanging off the pelvis like a torn skirt
        a = math.pi * (0.15 + 0.7 * i / 5)
        x = -math.cos(a) * 9
        k.limb(hips, (x, 24, 5.5), (x * 1.2, 12 + (i % 3) * 2, 7.5), 2.0, "bark", "root_skirt", d=2.0)

    def foot(ft, sx, an):
        k.box(ft, C(an[0], 0, an[2] + 1.5, 10, 3.6, 10), "bark", tag="foot")
        for i, a in enumerate((-0.9, -0.3, 0.3, 0.9)):    # roots splayed into the ground
            e = (an[0] + math.sin(a) * 9, 0.4, an[2] + 1.5 + math.cos(a) * 9)
            k.limb(ft, (an[0] + math.sin(a) * 3, 1.6, an[2] + 1.5 + math.cos(a) * 3), e, 1.8, "bark", "root", d=1.6)

    def shin(low, sx, kn):
        k.blob(low, (kn[0] * 1.05, kn[1], kn[2] + 1), (4.6, 4.0, 4.6), "bark", "knee_knot", step=0.8)
        thorns(k, low, [((kn[0] + sx * 3.4, kn[1] - 2, kn[2]), (sx, 0.3, 0.2)), ((kn[0], kn[1] - 5, kn[2] + 3.6), (0, 0, 1))])
        k.blob(low, (kn[0], kn[1] - 4, kn[2] - 2.4), (3.4, 2.0, 2.2), "moss", "moss", step=0.7)
    legs(k, hips, 7, 24, (8, 13, 3), (8, 4, 0), 9, 8, "bark", foot, plate=shin)

    # ---- the chest: a cage of branches, hollow, the green heart in it
    ch = k.part("chest", (0, 28, 0), (("x", 25),), hips)
    k.stack(ch, 0, -1.5, [(28, 14, 11), (33, 19, 13), (39, 25, 14), (45, 29, 15), (50, 24, 12), (53, 14, 9)], "bark", "torso", step=0.8)
    k.box(ch, C(0, 34, 6.4, 13, 14, 2.4), "hollow", tag="hollow")
    k.blob(ch, (0, 41, 6.6), (3.2, 3.6, 2.4), "heart", "heart", step=0.6)
    for i in range(4):                                   # ribs: branches arched over the hollow
        y = 35.5 + i * 3.4
        for sx in (-1, 1):
            k.limb(ch, (sx * 7.6, y, 6.4), (sx * 2.4, y + 1.6, 8.6), 1.6, "bark", "rib", d=1.6)
            k.limb(ch, (sx * 2.4, y + 1.6, 8.6), (sx * 0.4, y + 1.0, 8.8), 1.4, "bark", "rib", d=1.4)
    k.limb(ch, (0, 33.5, 8.0), (0, 48.5, 8.4), 1.8, "bark", "sternum", d=1.8)
    thorns(k, ch, [((sx * 12, y, z), (sx, 0.4, -0.2)) for sx in (-1, 1) for (y, z) in ((38, 2), (44, -2), (48, -5))]
           + [((x, y, -9), (x * 0.05, 0.4, -1)) for (x, y) in ((-6, 38), (5, 41), (-3, 46), (7, 47), (0, 48))], 4.4, 1.3)
    for (x, y, z, r) in ((-9, 46, 4, 3.4), (8, 36, 5, 2.6), (3, 50, -4, 3.0)):
        k.blob(ch, (x, y, z), (r, 1.6, r), "moss", "moss", step=0.7)
    # the crows' nests on its shoulders
    for sx in (-1, 1):
        k.blob(ch, (sx * 15, 47, 0), (6.4, 5.4, 7), "bark", "shoulder", step=0.9)
        k.ring(ch, sx * 15, 52.6, 0, 3.6, 1.4, "twig", "nest", n=10, axis="y")
        k.box(ch, C(sx * 15, 51.6, 0, 5.4, 1.4, 5.4), "twig", tag="nest")
    for sx, z in ((-1, 0.6), (1, -0.8)):                  # a crow on each
        cx = sx * 15
        k.box(ch, C(cx, 53, z, 2.2, 2.4, 3.4), "crow", tag="crow")
        k.box(ch, C(cx, 54.8, z + 1.6, 1.8, 1.8, 1.8), "crow", tag="crow")
        k.shard(ch, (cx, 55.4, z + 2.4), (0, -0.2, 1), 1.6, 0.6, mat="beak", tag="beak")
        k.box(ch, C(cx, 53.4, z - 2.2, 1.6, 0.6, 2.2), "crow", tag="crow")

    # ---- the head: a stag's skull, eyes of green fire, antlers wider than it is
    hd = k.part("head", (0, 52, 5), (("x", -18),), ch)
    k.blob(hd, (0, 55, 6), (4.2, 3.6, 4.6), "bone", "skull", step=0.6)
    k.limb(hd, (0, 54.5, 9), (0, 51, 17), 3.6, "bone", "snout", d=3.4)
    k.box(hd, C(0, 51.2, 16.4, 2.4, 1.4, 1.8), "dark", tag="nostril")
    for sx in (-1, 1):
        k.box(hd, C(sx * 2.4, 55.2, 9.0, 2.0, 1.8, 1.2), "dark", tag="socket")
        L.W.eye(k, hd, (sx * 2.4, 55.4, 9.5), 1.4, 0.9)
        antler(k, hd, (sx * 2.6, 58, 4.8), (sx * 1, 0.6, -0.15), 22, 2.0, 4, sx)
        k.shard(hd, (sx * 1.4, 50.4, 14.6), (0, -1, 0.15), 2.2, 0.8, mat="bone", tag="tooth")
    # a crown of bramble round the antlers' roots
    k.ring(hd, 0, 58.4, 5, 3.6, 1.4, "thorn", "crown", n=10, axis="y")

    # ---- long arms, root claws dragging the ground
    def upper(up, sx):
        thorns(k, up, [((sx * 21, 40, 0), (sx, 0.2, -0.3)), ((sx * 19, 36, -2.8), (0.2 * sx, 0, -1))], 3.6, 1.1)
        k.blob(up, (sx * 19.6, 42, 2), (2.6, 3.2, 2.4), "moss", "moss", step=0.7)

    def fore(low, sx):
        thorns(k, low, [((sx * 23, 26, 2), (sx, 0.3, 0)), ((sx * 21.6, 21, 5.6), (0.2 * sx, 0.2, 1))], 3.2, 1.0)

    def hand(h, sx, wr):
        k.blob(h, (wr[0], wr[1] - 2, wr[2] + 1), (3.8, 3.0, 4.0), "bark", "palm", step=0.7)
        for i, a in enumerate((-0.6, -0.2, 0.2, 0.6)):   # four long root fingers, reaching down and forward
            base = (wr[0] + math.sin(a) * 3, wr[1] - 3.4, wr[2] + 2.4)
            tip = (wr[0] + math.sin(a) * 6, 2.2, wr[2] + 8 + (i % 2) * 1.5)
            k.limb(h, base, tip, 1.6, "bark", "finger", d=1.6)
            k.shard(h, tip, (0, -0.6, 1), 2.6, 1.0, mat="thorn", tag="claw")
    arms(k, ch, (17, 46, 0), (20, 32, 2), (21, 17, 4), 7.0, 6.0, "bark", hand, hunch=25, upper=upper, fore=fore)

    W = L.W
    W.glow_tags(k, "eye", "heart")
    grow(k, GROW * (1.25 if legend else 1.0))
    k.s.shaders = W.shaders(
        bark=X.surf(BARK, 0.5, 1.2, 0.2, 0.08, stripe=3, crust=(W.MOSS, 0.12)),
        thorn=X.surf(THORN, 0.5, 1.3, 0.14, 0.12),
        twig=X.surf(W.WOOD, 0.55, 1.1, 0.24, 0.0, stripe=2),
        hollow=X.dark(THORN), heart=X.glow(HEART, 0.6, 0.3),
        antler=X.surf(W.BONE, 0.48, 1.2, 0.16, 0.1, pattern=W.grain),
        crow=X.surf(W.PANTHER, 0.5, 1.4, 0.1, 0.1), beak=X.surf(W.HORN, 0.6, 1.2, 0.1, 0.0),
        eye=X.glow(HEART, 0.8, 0.16),
    )
    return k.s, k.parts


BONES = list(BIPED)
make = old_blackbriar
LEGEND = None

# its moves (legendkit templates, tuned): the rake, roots up through the ground, the crows, the lunge; under 60% the thorns
_thorns = L.roar(48, 20, reach=5.5, front=0, radius=5.5, dmg=1.8, phase=2, cool=360, elem=9)
_thorns["events"] = {"slam": [20]}
CLIPS = L.fitted("old_blackbriar", {
    "idle": L.idle(),
    "walk": L.walk(48, 18, 50, 3.0, arms_=(10, 10)),
    "run": L.walk(30, 28, 60, 4.4, 1.5, arms_=(18, 18)),
    "rake": L.sweep(38, 20, reach=6.5, arc=150, dmg=1.1, range=[0, 6.5]),
    "roots": L.slam2(50, 28, event="spikes", range=[6, 18], dmg=1.0, cool=180, kind=1),
    "crows": L.roar(46, 18, reach=10.0, elem=3),
    "lunge": L.lunge(40, 13, 24, reach=4.0, arc=120, dmg=1.3, leap=[1.4, 0.5], range=[6, 14], cool=160),
    "thorns": _thorns,
    "hurt": L.hurt(),
    "death": L.death_kneel(),
})
AIR = {"lunge": [(14, 23)]}
