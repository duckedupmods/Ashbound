"""Old Harpoon: the coast's Legend. A whaler drowned so long ago the sea grew on him and he grew with it: bloated and
grey, crusted in barnacles, kelp for hair, his long sea coat rotted to ribbons; the harpoon that killed him still runs
through his chest, its rope trailing; a hook where his left hand was, and a ship's anchor he swings like a hammer.
Biped (legendkit)."""
import math

from legendkit import X, C, ramp, W, grow, legs, arms, BIPED  # noqa: F401

GROW = 1.5
HITBOX = (3.2, 5.8)
IS_LEGEND = True
STATS = dict(hp=640, speed=0.25, dmg=23, armor=8, kb=1.0)
EGG, SPOTS = 0x3a4a56, 0xc8c6b8
DROWNED = ramp("#1e262c", "#2c363e", "#3c4850", "#4e5c64", "#627078", "#78868c")
COAT = ramp("#06080e", "#0c1018", "#141a24", "#1c2430", "#26303e")
BRASS = ramp("#2a1e08", "#4a3610", "#6a5018", "#8a6a24", "#a88432")


def barnacles(k, part, at, n, r, seed=1):
    for i in range(n):
        a = i * 2.399 + seed
        p = (at[0] + math.cos(a) * r * (0.4 + 0.6 * X.h3(i, seed, 3)), at[1] + math.sin(a * 1.7) * r * 0.5, at[2] + math.sin(a) * r * 0.6)
        k.blob(part, p, (1.1, 0.9, 1.1), "barnacle", "barnacle", step=0.5)


def old_harpoon(name="old_harpoon", legend=False):
    k = X.Kit(name)
    hips = k.part("hips", (0, 26, 0))
    k.blob(hips, (0, 27, 0), (12, 5, 8.4), "coat", "waist", step=1.0)
    k.box(hips, C(0, 28.6, 0, 23, 2.0, 17), "leather", tag="belt")
    k.box(hips, C(0, 28.4, 8.8, 4, 2.6, 1.0), "brass", tag="buckle")
    for i, x in enumerate((-11, -6, 6, 11)):            # the coat's tails, rotted to ribbons
        k.limb(hips, (x, 27, -7), (x * 1.15, 8 + (i % 2) * 3, -10), 4.6, "coat", "coat_tail", d=1.4)
    for x in (-10, 10):
        k.limb(hips, (x, 27, 6), (x * 1.1, 13, 8.4), 4.4, "coat", "coat_front", d=1.4)

    def foot(ft, sx, an):
        k.box(ft, C(an[0], 0, an[2] + 2, 10.4, 4.6, 13), "leather", tag="foot")
        k.box(ft, C(an[0], 4.4, an[2] + 0.6, 10, 4.0, 10), "leather", tag="boot_top")
        barnacles(k, ft, (an[0] + sx * 4, 3, an[2] + 4), 3, 2.4, seed=2 + sx)

    def shin(low, sx, kn):
        barnacles(k, low, (kn[0] + sx * 3, kn[1] - 3, kn[2] + 3), 4, 3.0, seed=5 + sx)
        k.limb(low, (kn[0] - sx * 2, kn[1], kn[2] + 4), (kn[0] - sx * 3, kn[1] - 8, kn[2] + 4.4), 1.2, "kelp", "kelp", d=0.8)
    legs(k, hips, 8, 26, (8.5, 14, 2), (8.5, 4.5, 0), 10, 9, "skin", foot, plate=shin)

    # ---- the body: bloated, the coat open over a grey belly, the harpoon through it
    ch = k.part("chest", (0, 30, 0), (("x", 18),), hips)
    k.stack(ch, 0, 0, [(30, 18, 14), (36, 26, 18), (42, 30, 19), (48, 30, 18), (52, 24, 14), (54, 16, 10)], "coat", "torso", step=0.8)
    k.blob(ch, (0, 38, 6), (9, 8, 4.6), "skin", "belly", step=0.8)
    for y in (36, 41, 46):                              # brass buttons down the open coat
        for sx in (-1, 1):
            k.box(ch, C(sx * 9.6, y, 8.4, 1.4, 1.4, 1.0), "brass", tag="button")
    for sx in (-1, 1):
        k.blob(ch, (sx * 17, 47, 0), (7, 5.4, 8), "skin", "shoulder", step=0.8)
        barnacles(k, ch, (sx * 18, 51, 0), 7, 4.4, seed=7 + sx)
        k.limb(ch, (sx * 12, 52, 7), (sx * 9, 40, 9.4), 2.4, "coat", "lapel", d=1.0)
    # the harpoon: in through his belly, its barbed head out of his back, the rope still on it
    shaft_f, shaft_b = (-3, 33, 28), (3, 51, -15)
    k.limb(ch, shaft_f, shaft_b, 2.8, "wood", "harpoon", d=2.8)
    k.shard(ch, shaft_b, (0.2, 0.6, -0.8), 6, 3.0, mat="iron", tag="harpoon_head")
    for sx in (-1, 1):
        k.shard(ch, (3 + sx * 0.6, 51.6, -16), (sx * 0.8, -0.5, 0.4), 3.4, 1.0, mat="iron", tag="barb")
    k.blob(ch, (0, 38.5, 9.8), (2.2, 2.2, 1.2), "wound", "wound", step=0.5)
    rope = [(-3, 33, 28), (-6, 26, 30), (-8, 18, 27), (-7, 10, 24), (-5, 4, 22)]
    for a, b in zip(rope, rope[1:]):
        k.limb(ch, a, b, 1.2, "rope", "rope", d=1.2)

    # ---- the head: bloated, the jaw hanging, kelp for hair, one red eye; a crab in the other socket
    hd = k.part("head", (0, 52, 4), (("x", -18),), ch)
    k.blob(hd, (0, 57, 6), (6.4, 6.0, 6.0), "skin", "head", step=0.6)
    k.box(hd, C(0, 49.6, 7.6, 8.4, 3.6, 7), "skin", tag="jaw")
    k.box(hd, C(0, 52.6, 11.0, 7.0, 1.6, 1.2), "dark", tag="mouth")
    for t in range(5):
        k.shard(hd, (-2.8 + t * 1.4, 53.4, 11.3), (0, -1, 0), 1.3, 0.6, mat="bone", tag="tooth")
    k.box(hd, C(2.6, 57.4, 11.6, 2.4, 2.2, 1.0), "dark", tag="socket")
    W.eye(k, hd, (2.6, 58.0, 12.1), 1.4, 1.0)
    k.box(hd, C(-2.6, 57.4, 11.6, 2.4, 2.2, 1.0), "dark", tag="socket")
    k.box(hd, C(-2.6, 57.6, 12.2, 2.0, 1.2, 1.0), "crab", tag="crab")
    for sx in (-1, 1):
        k.shard(hd, (-2.6 + sx * 1.0, 58.2, 12.6), (sx * 0.6, 0.4, 0.6), 1.4, 0.6, mat="crab", tag="crab_claw")
    barnacles(k, hd, (-3, 61, 7), 5, 3.0, seed=11)
    for i in range(12):                                  # kelp hair, long and hanging
        a = math.pi * (0.9 + 1.2 * i / 11)
        top = (math.cos(a) * 5.4, 61.6, 6 + math.sin(a) * 5)
        bot = (math.cos(a) * 7.4, 42 + (i % 4) * 2.4, 4 + math.sin(a) * 6.4)
        k.limb(hd, top, bot, 1.4, "kelp", "hair", d=0.8)

    # ---- arms: a hook for a left hand, the anchor in the right
    def upper(up, sx):
        barnacles(k, up, (sx * 21, 40, -2), 4, 2.6, seed=3 + sx)

    def fore(low, sx):
        k.limb(low, (sx * 21, 31, 2), (sx * 21, 22, 4.6), 9.4, "coat", "cuff", d=9.4)

    def hand(h, sx, wr):
        if sx > 0:                                       # the hook: iron, a great curve of it off a leather cup
            k.box(h, C(wr[0], wr[1] - 4, wr[2] + 0.4, 6.6, 4.2, 6.6), "leather", tag="cup")
            hook = [(wr[0], wr[1] - 4, wr[2] + 0.6), (wr[0], wr[1] - 12, wr[2] + 1), (wr[0], wr[1] - 16, wr[2] + 5),
                    (wr[0], wr[1] - 14, wr[2] + 9), (wr[0], wr[1] - 10, wr[2] + 9.6)]
            for a, b in zip(hook, hook[1:]):
                k.limb(h, a, b, 1.6, "iron", "hook", d=1.6)
            k.shard(h, hook[-1], (0, 0.6, -0.6), 2.4, 1.2, mat="iron", tag="barb")
        else:                                            # the right fist round the anchor's shank
            k.box(h, C(wr[0], wr[1] - 7, wr[2] + 0.6, 8.4, 7.6, 8.4), "skin", tag="fist")
    arms(k, ch, (19, 46, 0), (21, 32, 2), (21, 20, 5), 9, 8, "skin", hand, hunch=18, upper=upper, fore=fore)
    ah = k.parts["ar_hand"]
    shank_t, crown = (-21, 22, 6), (-21.5, 2.8, 10)
    k.limb(ah, shank_t, crown, 2.6, "anchor", "shank", d=2.6)
    k.ring(ah, -21, 23.8, 6, 2.2, 1.0, "anchor", "anchor_ring", n=8, axis="x")
    k.limb(ah, (-28, 19.4, 6.6), (-14, 19.4, 6.6), 2.0, "wood", "stock", d=2.2)
    for sx in (-1, 1):                                   # the flukes, curving up off the crown
        p1 = (-21.5 + sx * 6, 4.4, 10.6)
        p2 = (-21.5 + sx * 9, 9.6, 10.6)
        k.limb(ah, crown, p1, 2.6, "anchor", "arm", d=2.4)
        k.limb(ah, p1, p2, 2.2, "anchor", "arm", d=2.2)
        k.shard(ah, p2, (sx * 0.4, 1, 0), 4.4, 3.6, mat="anchor", tag="fluke")
    barnacles(k, ah, (-21.5, 4, 10.6), 4, 2.4, seed=17)

    W.glow_tags(k, "eye")
    grow(k, GROW * (1.25 if legend else 1.0))
    k.s.shaders = W.shaders(
        skin=X.surf(DROWNED, 0.5, 1.2, 0.2, 0.06, crust=(W.BARNACLE, 0.18)),
        coat=X.surf(COAT, 0.5, 1.1, 0.2, 0.04, stripe=2, crust=(W.BARNACLE, 0.12)),
        leather=X.surf(W.HIDE, 0.48, 1.2, 0.18, 0.06),
        brass=X.surf(BRASS, 0.6, 1.4, 0.14, 0.24, rust=((W.KELP), 0.3, 0.6)),
        barnacle=X.surf(W.BARNACLE, 0.6, 1.4, 0.2, 0.1),
        kelp=X.surf(W.KELP, 0.48, 1.1, 0.2, 0.0, stripe=2),
        anchor=X.surf(W.IRON, 0.5, 1.4, 0.18, 0.18, rust=(W.RUST, 0.5, 0.4)),
        wood=X.surf(W.WOOD, 0.5, 1.1, 0.2, 0.06, stripe=3),
        rope=X.surf(W.ROPE, 0.55, 1.0, 0.2, 0.0, stripe=2),
        wound=X.surf(W.GORE, 0.4, 1.0, 0.2, 0.0), crab=X.surf(W.SEAEYE, 0.55, 1.3, 0.14, 0.1),
        eye=X.glow(W.SEAEYE, 0.8, 0.16),
    )
    return k.s, k.parts


BONES = list(BIPED)
make = old_harpoon
LEGEND = None
import legendkit as L

# the anchor brought down, the hook raked across to drag you in, the tide; under 60% he rips the harpoon out and throws it
CLIPS = L.fitted("old_harpoon", {
    "idle": L.idle(),
    "walk": L.walk(48, 18, 50, 3.0, 1.3),
    "run": L.walk(30, 28, 60, 4.4, 1.6),
    "anchor": L.overhead(42, 22, reach=6.0, arc=60, dmg=1.5, range=[0, 6]),
    "hook": L.mirror(L.sweep(38, 20, reach=6.5, arc=140, dmg=0.9, pull=1.2, range=[0, 6.5])),
    "tide": L.roar(46, 18, reach=9.0, elem=4),
    "harpoon": L.mirror(L.throw(44, 26, item=2, dmg=1.4, throw=2.2, range=[5, 24], phase=2, cool=240)),
    "hurt": L.hurt(),
    "death": L.death_kneel(),
})
