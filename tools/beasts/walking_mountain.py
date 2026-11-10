"""The Walking Mountain: the badlands' Legend. A titan of red rock that walks on its knuckles, its back a hill with
grass and a ruined fort still standing on it (keep, wall, a torn flag); blue crystal geodes split out of its shoulders,
its face a cave mouth hung with stone teeth under a brow like a cliff, two crystal eyes deep in it.
Biped (legendkit), no hunch: the stoop is in the shape. The fort is its own bone, so it can rock and shed rubble."""
import math

from legendkit import X, C, ramp, W, grow, legs, arms, BIPED  # noqa: F401

GROW = 2.3
HITBOX = (5.0, 8.0)
IS_LEGEND = True
STATS = dict(hp=900, speed=0.2, dmg=28, armor=16, kb=1.0)
EGG, SPOTS = 0x64513c, 0x6aa8dc
REDROCK = ramp("#1e100a", "#2e1a10", "#422618", "#563322", "#6c422c", "#825438", "#9a6646")
GRASS = ramp("#1c2a0c", "#2a3e12", "#3a5418", "#4c6c20", "#5e8428")
BRICK = ramp("#22242a", "#33363e", "#464a52", "#5a5e66", "#70747c", "#888c94")


def geode(k, part, at, up, n=4, L_=6, seed=1):
    k.blob(part, at, (3.4, 2.6, 3.4), "rock_dark", "geode_bed", step=0.6)
    k.cluster(part, (at[0], at[1] + 1, at[2]), n, L_, 2.0, mat="crystal", seed=seed, spread=0.55, up=up)


def walking_mountain(name="walking_mountain", legend=False):
    k = X.Kit(name)
    hips = k.part("hips", (0, 26, -10))
    k.blob(hips, (0, 27, -10), (13, 7, 9), "rock", "haunch", step=1.0)

    def foot(ft, sx, an):
        k.box(ft, C(an[0], 0, an[2] + 2, 13, 5, 14), "rock", tag="foot")
        k.blob(ft, (an[0], 4.4, an[2] + 1), (5.6, 2.6, 5.6), "rock_dark", "ankle", step=0.7)
    legs(k, hips, 10, 26, (11, 15, -6), (11, 4.5, -9), 12, 11, "rock", foot)

    # ---- the body: a hill of red rock, stooped forward, its back flat enough to build on
    ch = k.part("chest", (0, 30, -4), (), hips)
    k.blob(ch, (0, 40, -3), (18, 11.6, 16), "rock", "body", step=1.0)
    k.blob(ch, (0, 31, 2), (12, 6, 10), "rock_dark", "belly", step=1.0)
    for sx in (-1, 1):
        k.blob(ch, (sx * 17, 45, 6), (9, 8, 9), "rock", "shoulder", step=0.9)
        geode(k, ch, (sx * 19, 51, 4), (sx * 0.5, 1, 0.1), 5, 8, seed=3 + sx)
        geode(k, ch, (sx * 12, 48, -12), (sx * 0.3, 1, -0.4), 3, 5, seed=7 + sx)
    for i, (a, b) in enumerate((((-8, 35, 13), (-3, 42, 14)), ((6, 33, 12), (9, 41, 11)), ((14, 38, 10), (16, 44, 8)))):
        k.limb(ch, a, b, 0.8, "vein", "vein", d=0.6, group="glow")       # crystal veins in the rock, glowing faint
    # its back: turf and scrub on top, the fort standing on it
    k.box(ch, C(0, 50.6, -4, 26, 1.8, 24), "grass", tag="turf")
    for (x, z, h) in ((-10, 4, 3), (11, -10, 4), (-11, -12, 2.6)):
        k.blob(ch, (x, 52 + h * 0.5, z), (2.2, h * 0.5 + 0.6, 2.2), "scrub", "scrub", step=0.6)
    ft = k.part("fort", (0, 52, -6), (), ch)
    k.stack(ft, -3, -7, [(52, 13, 13), (56, 12, 12), (66, 11, 11)], "brick", "keep", step=1.0)
    for i in range(4):                                   # crenellations, one corner broken away
        for j in range(4):
            if (i in (0, 3) or j in (0, 3)) and not (i == 3 and j == 0) and (i + j) % 2 == 0:
                k.box(ft, C(-3 - 4.2 + i * 2.8, 66, -7 - 4.2 + j * 2.8, 2.2, 2.4, 2.2), "brick", tag="merlon")
    for (y, z) in ((58, -1.2), (62, -1.4)):
        k.box(ft, C(-3, y, z, 1.2, 2.6, 0.8), "dark", tag="slit")
    k.box(ft, C(-3, 52, -0.6, 4, 5, 1.0), "door", tag="door")
    k.box(ft, C(7, 52, -4, 2.6, 7, 12), "brick", tag="wall")           # a stretch of curtain wall, its end fallen
    k.box(ft, C(7, 59, -6, 2.6, 2, 2), "brick", tag="merlon")
    k.box(ft, C(7, 59, -1, 2.6, 2, 2), "brick", tag="merlon")
    for (x, z) in ((10, 3), (11, -1), (9, 5)):
        k.box(ft, C(x, 52, z, 2, 1.6, 2), "brick", tag="rubble")
    k.limb(ft, (-6, 66, -10), (-6, 76, -10), 0.8, "wood", "flagpole", d=0.8)
    k.box(ft, C(-3.4, 72.4, -10, 5, 3.4, 0.4), "flag", tag="flag")
    k.box(ft, C(-0.4, 72.4, -10, 1.6, 2.0, 0.4), "flag", tag="flag")

    # ---- the head: low between its shoulders, a brow like a cliff, a cave of a mouth
    hd = k.part("head", (0, 38, 14), (), ch)
    k.blob(hd, (0, 39, 16), (7.6, 6.4, 6.4), "rock", "head", step=0.8)
    k.box(hd, C(0, 42.6, 19.6, 15, 3.0, 5.2), "rock_dark", tag="brow")
    k.box(hd, C(0, 33.4, 19.0, 10, 4.6, 4.6), "dark", tag="maw")
    for t in range(5):
        k.shard(hd, (-4 + t * 2, 38.2, 21.0), (0, -1, 0.1), 2.6 + (t % 2) * 1.2, 1.2, mat="rock_dark", tag="tooth")
        k.shard(hd, (-3 + t * 1.6, 33.4, 21.0), (0, 1, 0.1), 1.6 + (t % 2) * 0.8, 1.0, mat="rock_dark", tag="tooth")
    k.box(hd, C(0, 32.0, 17.6, 12, 2.4, 8), "rock", tag="jaw")
    for sx in (-1, 1):
        k.box(hd, C(sx * 3.6, 40.2, 21.2, 2.8, 2.0, 1.0), "dark", tag="socket")
        W.eye(k, hd, (sx * 3.6, 40.8, 21.7), 1.8, 1.0)
        k.shard(hd, (sx * 6.6, 43, 18), (sx * 0.8, 0.6, 0.3), 4.6, 2.4, mat="crystal", tag="horn_crystal")

    # ---- arms: long, heavy, it walks on its knuckles
    def upper(up, sx):
        k.blob(up, (sx * 21, 36, 8), (5.6, 6.4, 5.6), "rock", "bicep", step=0.8)

    def fore(low, sx):
        k.blob(low, (sx * 22.6, 20, 11), (6, 6.4, 6), "rock", "forearm_bulk", step=0.8)
        geode(k, low, (sx * 25, 24, 9), (sx * 1, 0.6, -0.2), 3, 4.4, seed=11 + sx)

    def hand(h, sx, wr):                                 # knuckles down, a fist like a boulder
        k.box(h, C(wr[0], 0, wr[2] + 2, 12, 9, 12), "rock", tag="foot")
        for f in range(4):
            k.box(h, C(wr[0] + (f - 1.5) * 2.8, 0, wr[2] + 8.2, 2.4, 3, 2), "rock_dark", tag="knuckle")
    arms(k, ch, (18, 46, 6), (22, 28, 9), (22, 9, 12), 10, 9.4, "rock", hand, upper=upper, fore=fore)

    W.glow_tags(k, "eye", "vein")
    grow(k, GROW * (1.2 if legend else 1.0))
    k.s.shaders = W.shaders(
        rock=X.surf(REDROCK, 0.56, 1.3, 0.24, 0.12, stripe=5, crust=(W.MOSS, 0.08)),
        rock_dark=X.surf(REDROCK, 0.32, 1.2, 0.2, 0.08),
        crystal=X.facets(W.CRYSTAL), vein=X.glow(W.CRYSTAL, 0.66, 0.3),
        grass=X.surf(GRASS, 0.55, 1.1, 0.22, 0.0), scrub=X.surf(W.PINE, 0.55, 1.1, 0.26, 0.0),
        brick=X.surf(BRICK, 0.55, 1.3, 0.2, 0.12, stripe=4, crust=(W.MOSS, 0.2)),
        door=X.surf(W.WOOD, 0.4, 1.1, 0.2, 0.04, stripe=3), wood=X.surf(W.WOOD, 0.5, 1.1, 0.2, 0.06),
        flag=X.surf(W.BLOOD, 0.55, 1.0, 0.2, 0.0),
        eye=X.glow(W.CRYSTAL, 0.85, 0.12),
    )
    return k.s, k.parts


BONES = list(BIPED) + ["fort"]
make = walking_mountain
LEGEND = None
import legendkit as L

# knuckles brought down together, a boulder torn off its back and thrown, a stomp that shakes the ground; under 60% the
# fort on its back sheds rubble down on everyone round it. Keyed on the 1.5 body, grown with it.
K = GROW / 1.5
CLIPS = L.grown(L.fitted("walking_mountain", {
    "idle": L.idle(extra=lambda n: {"fort": L.wave(n, 1.5, 0.2, axis=2, step=4)}),
    "walk": L.walk(56, 14, 40, 3.2, 1.6, arms_=(16, 16), extra=lambda n: {"fort": L.wave(n, 3.0, 0.1, axis=2)}),
    "run": L.walk(36, 22, 50, 4.4, 2.0, arms_=(24, 24), extra=lambda n: {"fort": L.wave(n, 5.0, 0.1, axis=2)}),
    "smash": L.slam2(50, 28, front=4.0, radius=4.5, dmg=2.0, range=[0, 7]),
    "boulder": L.throw(44, 26, item=3, dmg=1.2, throw=1.5, range=[8, 28], cool=200),
    "quake": L.stomp(44, 24, event="roar", reach=10.0, elem=5),
    "rubble": L.with_events(L.roar(46, 18, phase=2, cool=360, n=10), rain=[18]),
    "hurt": L.hurt(),
    "death": L.death_kneel(),
}), K)
