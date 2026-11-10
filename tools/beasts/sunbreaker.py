"""Sunbreaker: the desert's Legend. A colossus carved from sandstone for a temple nobody remembers: its face is a disc
of polished gold, blank as a mirror, under a crown of gold rays; the stone of it has split and the cracks run with
glowing sand; fists like the blocks it was cut from. Biped (legendkit)."""
import math

from legendkit import X, C, ramp, W, grow, legs, arms, BIPED  # noqa: F401

GROW = 1.5
HITBOX = (3.4, 6.2)
IS_LEGEND = True
STATS = dict(hp=720, speed=0.22, dmg=25, armor=14, kb=1.0)
EGG, SPOTS = 0xc4a66e, 0xfcd860
SANDSTONE = ramp("#3a2a16", "#5a4224", "#7a5c34", "#987646", "#b4925a", "#ccac72", "#e2c68e")
GLOWSAND = ramp("#8a4a08", "#c07410", "#eaa424", "#ffd060", "#fff2b0")
CLOTH = ramp("#2a0e0a", "#46180e", "#642414", "#80321c", "#9a4226")


def crack(k, part, a, b, w=0.9):
    """a jagged split: four short runs zigzagging from a to b, thinning out"""
    pts = [a]
    for i in range(1, 4):
        f = i / 4
        side = (1.4 if i % 2 else -1.4)
        pts.append((a[0] + (b[0] - a[0]) * f + side * 0.8, a[1] + (b[1] - a[1]) * f + side * 0.3, a[2] + (b[2] - a[2]) * f))
    pts.append(b)
    for i, (p, q) in enumerate(zip(pts, pts[1:])):
        ww = max(0.5, w * (1 - i * 0.18))
        k.limb(part, p, q, ww, "glowsand", "crack", d=ww, group="glow")


def sunbreaker(name="sunbreaker", legend=False):
    k = X.Kit(name)
    hips = k.part("hips", (0, 26, 0))
    k.box(hips, C(0, 22, 0, 22, 8, 14), "stone_s", tag="pelvis")
    k.box(hips, C(0, 29, 0, 20, 2, 13), "stone_dark", tag="belt")
    # the faded banner hanging over its loins, the sun stitched on it
    k.box(hips, C(0, 9, 7.6, 10, 20, 1.2), "cloth", tag="banner")
    k.ring(hips, 0, 20, 8.4, 2.6, 1.0, "gold", "banner_sun", n=10, axis="z")
    for i in range(3):
        k.box(hips, C(-3 + i * 3, 6.8 - (i % 2) * 1.4, 7.6, 2.2, 2.6 + (i % 2) * 1.4, 1.2), "cloth", tag="banner_tatter")

    def foot(ft, sx, an):
        k.box(ft, C(an[0], 0, an[2] + 1.5, 12, 4.6, 14), "stone_s", tag="foot")
        k.box(ft, C(an[0], 4.4, an[2] + 1.0, 10, 2.0, 11), "gold", tag="anklet")

    def shin(low, sx, kn):
        k.box(low, C(kn[0], kn[1] - 2, kn[2] + 0.5, 11.6, 4, 11.6), "stone_dark", tag="knee_block")
        crack(k, low, (kn[0] + sx * 1, kn[1] - 4, kn[2] + 5.8), (kn[0] - sx * 2, kn[1] - 9, kn[2] + 5.4))
    legs(k, hips, 8, 26, (8.5, 14, 2), (8.5, 4.5, 0), 11, 10.4, "stone_s", foot, plate=shin)

    # ---- the torso: stacked courses of dressed stone, a broad stepped chest, split open
    ch = k.part("chest", (0, 30, 0), (("x", 8),), hips)
    k.stack(ch, 0, 0, [(30, 18, 13), (34, 22, 14), (38, 28, 15), (44, 34, 16), (50, 34, 15), (53, 26, 12)], "stone_s", "torso", step=1.2)
    for y in (35.5, 41, 47):
        k.box(ch, C(0, y, 0, 26 + (y - 35) * 0.7, 0.8, 15.6 + (y - 35) * 0.06), "stone_dark", tag="course")
    for i, (x, y) in enumerate(((-9, 46), (-3, 46), (3, 46), (9, 46), (-6, 43.5), (0, 43.5), (6, 43.5))):   # a frieze of rays
        k.box(ch, C(x, y, 8.2, 1.4, 1.4, 0.6), "gold", tag="glyph")
    crack(k, ch, (-4, 50, 8.4), (2, 41, 8.6), 1.2)
    crack(k, ch, (2, 41, 8.6), (-1, 33, 8.0), 1.0)
    crack(k, ch, (2, 41, 8.6), (9, 37, 8.0), 0.8)
    crack(k, ch, (13, 49, 4), (16, 42, 2), 0.9)
    k.blob(ch, (1, 40, 8.6), (2.4, 2.6, 0.8), "glowsand", "core", step=0.5)
    for sx in (-1, 1):                                  # shoulders: stepped blocks, gold-capped
        k.box(ch, C(sx * 18, 44, 0, 10, 9, 13), "stone_s", tag="shoulder")
        k.box(ch, C(sx * 18.6, 52.6, 0, 8, 3, 10), "stone_s", tag="shoulder")
        k.box(ch, C(sx * 18.6, 55.4, 0, 6, 1.6, 8), "gold", tag="shoulder_cap")

    # ---- the head: a gold mirror for a face, a crown of rays
    hd = k.part("head", (0, 53, 3), (("x", -8),), ch)
    k.box(hd, C(0, 52.5, 3, 10, 11, 10), "stone_s", tag="head")
    for i in range(14):                                 # the face: a disc of gold, polished blank
        a0 = i * 2 * math.pi / 14
        k.box(hd, C(math.cos(a0) * 3.6, 58 - 0.6 + math.sin(a0) * 3.6 - 0.6, 8.4, 2.2, 2.2, 1.2), "mirror", tag="mirror")
    k.box(hd, C(0, 55.0, 8.5, 5.6, 6.0, 1.2), "mirror", tag="mirror")
    k.box(hd, C(0, 56.0, 9.1, 3.0, 3.0, 0.4), "mirror_hot", tag="glare", group="glow")
    k.ring(hd, 0, 58, 8.6, 5.2, 1.0, "gold", "rim", n=16, axis="z")
    for i in range(11):                                 # the crown of rays behind it, longest overhead
        a0 = math.pi * (0.0 + i / 10)
        L_ = 7 + 6 * math.sin(a0)
        k.shard(hd, (math.cos(a0) * 5.4, 58 + math.sin(a0) * 5.4, 1.5), (math.cos(a0), math.sin(a0), -0.1), L_, 1.8, mat="gold", tag="ray")

    # ---- arms like pillars, fists like the blocks it was cut from
    def upper(up, sx):
        k.box(up, C(sx * 20, 34, 1, 9.6, 3, 9.6), "gold", tag="armband")
        crack(k, up, (sx * 22.6, 42, 3), (sx * 23.4, 37, 1))

    def fore(low, sx):
        k.box(low, C(sx * 21, 21, 3.5, 10.4, 6, 10.4), "stone_dark", tag="bracer")

    def hand(h, sx, wr):
        k.box(h, C(wr[0], wr[1] - 10, wr[2] + 0.5, 12, 10.6, 12), "stone_s", tag="fist")
        k.box(h, C(wr[0], wr[1] - 10.6, wr[2] + 0.5, 12.6, 1.4, 12.6), "stone_dark", tag="fist_edge")
        crack(k, h, (wr[0] - sx * 2, wr[1] - 1.4, wr[2] + 6.6), (wr[0] + sx * 3, wr[1] - 8, wr[2] + 6.6))
    arms(k, ch, (20, 46, 0), (21, 32, 2), (21, 21, 3.5), 10, 9.4, "stone_s", hand, hunch=8, upper=upper, fore=fore)

    W.glow_tags(k, "crack", "core", "glare")
    grow(k, GROW * (1.25 if legend else 1.0))
    k.s.shaders = W.shaders(
        stone_s=X.surf(SANDSTONE, 0.6, 1.3, 0.2, 0.14, stripe=4),
        stone_dark=X.surf(SANDSTONE, 0.38, 1.2, 0.18, 0.1),
        gold=X.surf(W.GOLD, 0.62, 1.5, 0.12, 0.3),
        mirror=X.surf(W.GOLD, 0.82, 1.6, 0.06, 0.36),
        mirror_hot=X.glow(GLOWSAND, 0.9, 0.1),
        glowsand=X.glow(GLOWSAND, 0.62, 0.3),
        cloth=X.surf(CLOTH, 0.5, 1.0, 0.2, 0.0, stripe=2),
    )
    return k.s, k.parts


BONES = list(BIPED)
make = sunbreaker
LEGEND = None
import legendkit as L

# the sunbeam out of its mirror face, the fists, pillars of sandstone; under 60% it spins up a sandstorm
CLIPS = L.fitted("sunbreaker", {
    "idle": L.idle(),
    "walk": L.walk(52, 16, 44, 2.8, 1.4),
    "run": L.walk(34, 24, 54, 4.0, 1.8),
    "beam": L.breath(64, 20, 52, reach=13.0, arc=26, dmg=0.12, elem=1, range=[4, 13], cool=260),
    "smash": L.slam2(50, 28, front=3.5, radius=4.0, dmg=2.0, range=[0, 6]),
    "pillars": L.stomp(44, 24, event="spikes", range=[6, 18], dmg=1.0, cool=180, kind=2),
    "glare": L.roar(46, 18, reach=9.0, elem=8),
    "storm": L.spin(62, reach=7.0, dmg=0.9, range=[0, 7], phase=2, cool=400, odds=0.5, elem=8),
    "hurt": L.hurt(),
    "death": L.death_kneel(),
})
