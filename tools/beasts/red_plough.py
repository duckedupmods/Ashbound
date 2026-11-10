"""The Red Plough: the plains' Legend. A rust-iron giant still wearing the ox-yoke it was broken to, a dented great
helm with one dull red slit, its legs caked in red earth to the knee; it drags a huge plough on its beam and swings the
blade like a scythe. Biped (legendkit)."""
import math

from legendkit import X, C, ramp, W, grow, legs, arms, BIPED  # noqa: F401

GROW = 1.5
HITBOX = (3.4, 5.6)
IS_LEGEND = True
STATS = dict(hp=680, speed=0.27, dmg=24, armor=12, kb=1.0)
EGG, SPOTS = 0x6a3418, 0xb04a20
CLAY = ramp("#2a0e06", "#42180a", "#5e2410", "#7a3418", "#964622", "#ae5a2e")
SLIT = ramp("#3a0402", "#6a0804", "#a01408", "#d03010", "#ff6a3a")


def rivets(k, part, pts):
    for p in pts:
        k.box(part, C(p[0], p[1], p[2], 0.9, 0.9, 0.9), "iron_hi", tag="rivet")


def red_plough(name="red_plough", legend=False):
    k = X.Kit(name)
    hips = k.part("hips", (0, 26, 0))
    k.blob(hips, (0, 27, 0), (12, 5, 8), "iron", "pelvis", step=1.0)
    for i, x in enumerate((-8, -3, 3, 8)):               # a skirt of iron lames
        k.box(hips, C(x, 17 + (i % 2), 6.6, 5.4, 9, 1.4), "iron", tag="tasset")
        k.box(hips, C(x, 17 + (i % 2), -6.6, 5.4, 9, 1.4), "iron", tag="tasset")

    def foot(ft, sx, an):
        k.box(ft, C(an[0], 0, an[2] + 2, 11, 4.4, 13.5), "iron", tag="foot")
        k.box(ft, C(an[0], 0, an[2] + 2, 11.8, 2.4, 14.2), "clay", tag="mud")
        k.box(ft, C(an[0], 4.2, an[2] + 0.6, 9.4, 2.4, 9.4), "iron", tag="ankle")

    def shin(low, sx, kn):
        k.blob(low, (kn[0], kn[1], kn[2] + 1.2), (5.4, 4.6, 5.4), "iron", "knee_cop", step=0.8)
        k.limb(low, (kn[0], kn[1] - 3, kn[2] + 2.4), (kn[0], 5, 2.6), 9.4, "clay", "mud", d=4.2)   # red earth to the knee
        for i in range(4):
            k.limb(low, (kn[0] + sx * (4.6 - i * 2.6), kn[1] - 4, kn[2] + 3), (kn[0] + sx * (4.4 - i * 2.6), kn[1] - 8 - i, kn[2] + 3.6),
                   1.0, "clay", "drip", d=0.8)
    legs(k, hips, 8, 26, (9, 14, 3), (9, 4, 0), 11, 10, "iron", foot, plate=shin)

    # ---- a barrel of riveted plate, bent under the yoke
    ch = k.part("chest", (0, 30, 0), (("x", 15),), hips)
    k.stack(ch, 0, 0, [(30, 18, 14), (35, 24, 17), (41, 30, 18), (47, 32, 17), (51, 28, 14), (53, 18, 10)], "iron", "torso", step=0.8)
    for y in (36, 41, 46):
        k.box(ch, C(0, y, 0, 31 - abs(y - 44) * 0.8, 1.2, 18.6 - abs(y - 45) * 0.3), "rust", tag="band")
        rivets(k, ch, [(x, y + 0.2, 9.0 - abs(x) * 0.02) for x in (-10, -5, 0, 5, 10)])
    k.box(ch, C(0, 33, 8.6, 10, 9, 1.2), "iron_hi", tag="plackart")
    # the yoke over its neck: a beam of oak, iron-bound, bows round its shoulders, broken chains hanging
    k.limb(ch, (-30, 53, -3), (30, 53, -3), 4.4, "wood", "yoke", d=5.4)
    for x in (-24, -9, 9, 24):
        k.ring(ch, x, 53, -3, 3.2, 0.9, "iron", "yoke_band", n=8, axis="x")
    for sx in (-1, 1):
        k.ring(ch, sx * 30, 51, -3, 3.4, 1.2, "iron", "yoke_loop", n=10, axis="z")
        k.chain(ch, (sx * 30, 47.6, -3), (sx * 31, 36, -4), 5, "iron", w=1.6)
        k.limb(ch, (sx * 13, 53, -3), (sx * 13, 45, 5), 1.6, "wood", "bow", d=1.6)
        k.limb(ch, (sx * 13, 45, 5), (sx * 8, 43, 8), 1.6, "wood", "bow", d=1.6)

    # ---- the head: a dented bucket of a great helm, one slit
    hd = k.part("head", (0, 52, 4), (("x", -15),), ch)
    k.stack(hd, 0, 5, [(51, 11, 11), (56, 11.6, 11.6), (61, 11, 11), (63, 9, 9)], "iron", "helm", step=0.7)
    k.box(hd, C(0, 56.6, 10.4, 9, 1.6, 1.2), "dark", tag="slit")
    k.box(hd, C(0, 56.9, 10.8, 7, 0.8, 0.6), "eye", tag="eye", group="glow")
    k.limb(hd, (0, 52, 10.8), (0, 62.6, 10.4), 1.6, "iron_hi", "nasal", d=1.0)
    for r in range(3):
        for c in range(3):
            k.box(hd, C(-3 + c * 3, 53 + r * 1.2, 10.6, 0.8, 0.6, 0.6), "dark", tag="breaths")
    k.box(hd, C(3, 62, 6, 4, 1.4, 4), "rust", tag="dent")

    # ---- arms: plate pauldrons, gauntlets like anvils
    def upper(up, sx):
        k.blob(up, (sx * 21, 47.5, 0), (7, 5.6, 8), "iron", "pauldron", step=0.8)
        for i in range(3):
            k.box(up, C(sx * 22, 43 - i * 2.6, 0, 9 - i, 1.6, 10 - i), "iron_hi" if i == 0 else "iron", tag="lame")

    def fore(low, sx):
        k.limb(low, (sx * 22, 30, 2.4), (sx * 22, 22, 4.6), 9.4, "rust", "vambrace", d=9.4)

    def hand(h, sx, wr):
        k.box(h, C(wr[0], wr[1] - 7.6, wr[2] + 0.6, 9, 8.4, 9), "iron", tag="gauntlet")
        for f in range(4):
            k.box(h, C(wr[0] + (f - 1.5) * 2.1, wr[1] - 8.8, wr[2] + 5.0, 1.8, 3.4, 1.8), "iron_hi", tag="knuckle")
    arms(k, ch, (20, 46, 0), (22, 32, 2), (22, 20, 5), 9, 8, "iron", hand, hunch=15, upper=upper, fore=fore)

    # ---- the plough, in its right hand: an oak beam, an iron share and the great curved mouldboard
    rh = k.parts["ar_hand"]
    k.chain(k.parts["al_hand"], (22, 13, 5.6), (24, 4, 9), 4, "iron", w=1.7)       # a chain wrapped round the left fist, hanging
    a, b = (-22, 30, -2), (-23.5, 6, 31)
    k.limb(rh, a, b, 3.2, "wood", "beam", d=3.2)
    for f in (0.15, 0.55, 0.85):
        p = tuple(a[i] + (b[i] - a[i]) * f for i in range(3))
        k.ring(rh, p[0], p[1], p[2], 2.2, 0.8, "iron", "beam_band", n=8, axis="z")
    k.box(rh, C(-23.5, 0.6, 33.5, 5.2, 9.4, 7.4), "iron", tag="frog")               # the iron frog the blade bolts to
    for i in range(6):                                    # the mouldboard: a curved plate turning the earth out to its right
        t = i / 5
        ang = 0.2 + 1.1 * t
        x = -23.5 - math.sin(ang) * 14
        z = 33.5 + math.cos(ang) * 9 - 9
        k.box(rh, C(x, 0.4 + t * 2.0, z + 3, 5.0, 15 - t * 3.6, 3.6), "rust", tag="mouldboard")
        k.box(rh, C(x, 15.2 - t * 1.6, z + 3, 5.2, 1.4, 4.0), "iron_hi", tag="mouldboard_rim")
    k.shard(rh, (-23.5, 1.2, 36.0), (0.12, -0.08, 1), 13.0, 6.4, mat="share", tag="share")   # the share, honed bright
    k.box(rh, C(-23.5, 9.6, 33.2, 6.0, 1.6, 6.0), "iron_hi", tag="bolt")

    W.glow_tags(k, "eye")
    grow(k, GROW * (1.25 if legend else 1.0))
    k.s.shaders = W.shaders(
        iron=X.surf(W.IRON, 0.52, 1.4, 0.16, 0.2, rust=(W.RUST, 0.32, 0.35)),
        iron_hi=X.surf(W.IRON, 0.7, 1.5, 0.14, 0.26, rust=(W.RUST, 0.3, 0.6)),
        rust=X.surf(W.RUST, 0.55, 1.3, 0.26, 0.12),
        share=X.surf(W.IRON, 0.86, 1.6, 0.1, 0.34),
        clay=X.surf(CLAY, 0.5, 1.2, 0.26, 0.04, drip=(CLAY, 0.4)),
        wood=X.surf(W.WOOD, 0.58, 1.1, 0.2, 0.06, stripe=3),
        eye=X.glow(SLIT, 0.7, 0.2),
    )
    return k.s, k.parts


BONES = list(BIPED)
make = red_plough
LEGEND = None
import legendkit as L

# the reap and the chop with its plough, a charge that carves a trench, the bellow; under 60% the earth heaves
_reap = L.sweep(38, 20, reach=7.5, arc=170, dmg=1.1, range=[0, 7])
_reap["events"]["guard"] = [20]
_charge = L.with_events(L.lunge(40, 12, 24, reach=4.0, arc=90, dmg=1.2, range=[7, 18], cool=200, dash=14, speed=0.9), charge=[12])
CLIPS = L.fitted("red_plough", {
    "idle": L.idle(),
    "walk": L.walk(48, 18, 50, 3.0, 1.2),
    "run": L.walk(30, 28, 60, 4.4, 1.6),
    "reap": _reap,
    "chop": L.overhead(42, 22, reach=6.5, arc=50, dmg=1.4, range=[0, 6.5]),
    "charge": _charge,
    "bellow": L.roar(46, 18, reach=9.0, elem=5),
    "heave": L.stomp(44, 24, front=0, radius=6.5, dmg=1.8, phase=2, cool=360, elem=5),
    "hurt": L.hurt(),
    "death": L.death_kneel(),
})
AIR = {"charge": [(13, 23)]}
