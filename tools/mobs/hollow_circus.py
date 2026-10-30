"""The Hollow Circus's monsters, each built by hand (tools/vox2.py). The travelling show that pitched in the hollow
and never packed up: faded red and cream stripes, flaking gilt, painted wood, cracked porcelain, gas-lamp light
gone sickly yellow, and the grins - everything grins.

    circus_puppet    swarm   a marionette walking on its own: ball joints, a cracked porcelain face, its strings still on
    strongman        brute   the strongman in the lion's skin: a stitched grin, a cannonball barbell, a belt of iron
    fire_eater       caster  burnt black under the greasepaint, a torch in each hand, the flame coming out of his mouth
    knife_juggler    skirm   a lanky clown with a fan of knives in each hand and a target board strapped to his back
    harlequin        elite   the star of the show: diamond motley, a mask half laughing half crying, skull bells, two rapiers
    ringmaster       boss    the Ringmaster, three men tall: a top hat with a light inside, a red tailcoat, a whip and a cane

    python tools/monsterforge.py hollow_circus --preview ; python tools/mobsheet.py hollow_circus
"""
import math

import vox2 as X
from vox2 import C, ramp

RED = ramp("#1e0608", "#38090c", "#560e12", "#781a1c", "#9a2a28", "#b84038")
CREAM = ramp("#3a3424", "#5a5038", "#7c7052", "#9e9070", "#bcb08e", "#d6caa8")
GILT = ramp("#3a2606", "#5e400c", "#8a6214", "#b48a24", "#d6ae44")
BLACK = ramp("#08080a", "#101014", "#18181e", "#22222a", "#2e2e38")
TEAL = ramp("#06201e", "#0c3430", "#164a44", "#226058", "#30786e")
PORC = ramp("#5a5650", "#7c7870", "#a09a90", "#c4bfb2", "#e6e2d6")
WOOD = ramp("#140c06", "#20140a", "#2e1e10", "#3e2a16", "#50381e")
PAINT = ramp("#2a1a10", "#4a2e18", "#6a4426", "#8a5c34", "#a87444")
GAS = ramp("#6a5a0a", "#a88e14", "#d8c030", "#f4e070", "#fffad0")
FIRE = ramp("#8a2a04", "#d0560c", "#f49020", "#ffcc5a", "#fff2c0")
SOOT = ramp("#060504", "#0e0c0a", "#181410", "#221c16", "#2e261e")
IRON = ramp("#0e0e10", "#18181c", "#26262c", "#36363e", "#4a4a52", "#62626a")
FUR = ramp("#2a1a08", "#44300e", "#604414", "#7c5a1c", "#987028", "#b48a38")
SKIN = ramp("#2e2220", "#46322e", "#5e4440", "#785852", "#926c64")


def stripes(A, B, every=4, vertical=True):
    """a striped cloth: bands of A and B, a dark seam between, flaking at the edges"""
    def f(p, n, b, key, i, j, w, h, fr):
        x, y, z = p
        u = (x + z) if vertical else y
        band = int(math.floor(u * 2.0 / every)) % 2
        R = A if band else B
        v = 0.46 + 0.18 * n[1] + 0.16 * (X.fbm(x * 0.6, y * 0.6, z * 0.6) - 0.5)
        if X.fbm(x * 0.9 + 3, y * 0.9, z * 0.9) > 0.8:
            v -= 0.2
        return X.shade(R, v, i, j)
    return f


def diamonds(A, B):
    def f(p, n, b, key, i, j, w, h, fr):
        x, y, z = p
        d = (int(math.floor((x + z + y) * 0.5)) + int(math.floor((x + z - y) * 0.5))) % 2
        v = 0.48 + 0.18 * n[1] + 0.14 * (X.fbm(x, y, z) - 0.5)
        return X.shade(A if d else B, v, i, j)
    return f


def shaders():
    return {
        "stripe": stripes(RED, CREAM),
        "hstripe": stripes(RED, CREAM, 3, vertical=False),
        "red": X.surf(RED, 0.5, 1.2, 0.2, 0.04),
        "cream": X.surf(CREAM, 0.5, 1.1, 0.2, 0.04),
        "gilt": X.surf(GILT, 0.56, 1.3, 0.16, 0.2, rust=(BLACK, 0.18, 0.5)),
        "black": X.surf(BLACK, 0.5, 1.3, 0.16, 0.12),
        "teal": X.surf(TEAL, 0.5, 1.1, 0.2, 0.04),
        "motley": diamonds(RED, BLACK),
        "motley2": diamonds(TEAL, CREAM),
        "porcelain": X.surf(PORC, 0.62, 1.2, 0.08, 0.14, pattern=lambda p, n, i, j, w, h: -0.4 if abs(X.fbm(p[0] * 0.5, p[1] * 0.5, p[2] * 0.5) - 0.5) < 0.02 else 0),
        "wood": X.surf(WOOD, 0.5, 1.0, 0.2, 0.06, stripe=3),
        "paint": X.surf(PAINT, 0.52, 1.2, 0.16, 0.1),
        "glow": X.glow(GAS),
        "eye": X.glow(GAS, 0.82, 0.16),
        "fire": X.glow(FIRE, 0.66, 0.34),
        "soot": X.surf(SOOT, 0.5, 1.2, 0.3, 0.04, crust=(FIRE, 0.04)),
        "iron": X.surf(IRON, 0.52, 1.4, 0.16, 0.18),
        "fur": X.surf(FUR, 0.5, 1.0, 0.34, 0.0, stripe=2),
        "skin": X.wrinkled(SKIN, 0.7),
        "dark": X.dark(BLACK),
    }


def grin(k, part, cx, cy, z, w, teeth=7, s=1.0):
    """the circus grin: a wide dark mouth turned up at the ends, a row of square teeth"""
    k.box(part, C(cx, cy, z, w, 1.4 * s, 0.4), "dark", tag="grin")
    for sx in (-1, 1):
        k.box(part, C(cx + sx * (w / 2 + 0.3 * s), cy + 0.6 * s, z, 1.0 * s, 1.6 * s, 0.4), "dark", tag="grin")
    for t in range(teeth):
        x = cx - w / 2 + (t + 0.5) * w / teeth
        k.box(part, C(x, cy + 0.6 * s, z + 0.05, w / teeth * 0.7, 0.8 * s, 0.4), "cream", tag="tooth")


# ================================================================ the Ringmaster (boss)

def ringmaster():
    """The Ringmaster, who sold the circus to something under the big top for one more season, and got it - every
    season, forever. He is three men tall and thin as a tent pole, in a red tailcoat with gold frogging, striped
    trousers, boots to the knee. His top hat is a yard high, and a light burns inside it, shining out of a rip in
    the crown like the big top's spotlight. His face is a white mask with a grin that goes ear to ear; one eye is a
    monocle that glows. He cracks a whip of chain in one hand and leans on a cane in the other, a striped pole
    topped with a crystal ball that holds the light of the show."""
    k = X.Kit("ringmaster")
    hips = k.part("hips", (0, 44, 0))
    k.stack(hips, 0, 0, [(38, 14, 9), (44, 15, 9.6)], "stripe", "trousers")
    k.box(hips, C(0, 43, 0, 16, 2.4, 10.4), "black", tag="belt")
    k.box(hips, C(0, 42.8, 5.3, 3.0, 2.8, 0.6), "gilt", tag="buckle")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 3.8
        th = k.part("thigh_" + nm, (x, 40, 0), (("x", -8), ("z", side * 4)), "hips")
        sh = k.part("shin_" + nm, (x, 22, 0), (("x", 10),), th)
        ft = k.part("foot_" + nm, (x, 4, 0), (("x", -4),), sh)
        k.stack(th, x, 0, [(22, 5.4, 5.6), (32, 6.4, 6.6), (40, 6.6, 6.8)], "stripe", "trousers")
        k.stack(sh, x, 0, [(4, 6.6, 7.0), (14, 6.8, 7.2), (22, 7.4, 7.6)], "black", "boot")
        k.box(sh, C(x, 20.6, 0, 8.4, 2.4, 8.6), "black", tag="boot_cuff")
        k.box(sh, C(x, 21.4, 4.4, 2.0, 1.4, 0.4), "gilt", tag="boot_buckle")
        k.box(ft, C(x, 0, 2.0, 7.0, 4.0, 12), "black", tag="foot")
        k.box(ft, C(x, 2.8, 2.0, 7.4, 0.8, 12.4), "gilt", tag="spat")
    # the coat tails, to the back of his knees, split
    for sx in (-1, 1):
        tl = k.part("tail%d" % (sx > 0), (sx * 3.4, 46, -5), (("x", -8), ("z", sx * 6)), hips, bone=False)
        k.box(tl, C(sx * 3.4, 18, -5.4, 6.6, 28, 1.2), "red", tag="coat_tail")
        k.box(tl, C(sx * 3.4, 18, -6.1, 6.6, 1.6, 0.6), "gilt", tag="tail_hem")
        k.box(tl, C(sx * (3.4 + 3.4), 18, -5.4, 0.6, 28, 1.4), "gilt", tag="tail_edge")
    # ---------------------------------------------------------------- torso: the tailcoat, gold frogging, a waistcoat
    to = k.part("torso", (0, 45, 0), (("x", 6),), "hips")
    k.stack(to, 0, 0, [(44, 16, 10.6), (52, 18, 11), (60, 26, 12.4), (66, 30, 12.4)], "red", "coat")
    k.box(to, C(0, 45, 5.0, 7.0, 18, 1.0), "teal", tag="waistcoat")
    for y in (48, 51, 54, 57, 60):
        k.box(to, C(0, y, 5.6, 1.0, 1.0, 0.6), "gilt", tag="button")
        for sx in (-1, 1):       # the frogging: gold cords across the coat front
            k.box(to, C(sx * 6.0, y, 5.4, 4.6, 0.7, 0.6), "gilt", tag="frogging")
            k.box(to, C(sx * 8.4, y, 5.4, 1.0, 1.0, 0.7), "gilt", tag="frogging")
    for sx in (-1, 1):
        k.box(to, C(sx * 4.6, 54, 5.6, 2.8, 12, 0.8), "black", tag="lapel")
        k.box(to, C(sx * 12.0, 66, 0, 6.0, 1.6, 10.6), "gilt", tag="epaulette")
        for i in range(4):
            k.limb(to, (sx * (9.8 + i * 1.6), 66, 4.4), (sx * (9.8 + i * 1.6), 62.4, 4.6), 0.6, "gilt", "fringe")
    k.box(to, C(0, 65.4, 0.6, 7.0, 2.6, 6.6), "cream", tag="collar")
    # the cape cut from the big top itself: red and cream panels from the shoulders to the floor, flaring, scalloped
    for i in range(9):
        u = (i - 4) / 4.0
        cp = k.part("cape%d" % i, (u * 12, 66, -6), (("x", -10 - abs(u) * 6), ("z", u * 14)), to, bone=False)
        k.box(cp, C(u * 12, 6, -6.6 - abs(u) * 2, 6.4, 60, 1.0), "red" if i % 2 else "cream", tag="cape")
        k.box(cp, C(u * 12, 4.4, -6.7 - abs(u) * 2, 4.0, 2.0, 1.0), "red" if i % 2 else "cream", tag="scallop")
        k.box(cp, C(u * 12, 6, -7.3 - abs(u) * 2, 6.6, 1.2, 0.6), "gilt", tag="cape_hem")
    for sx in (-1, 1):           # great shoulder boards, the cape pinned under them with gilt stars
        k.box(to, C(sx * 13.4, 65.6, 0, 9.0, 3.0, 12.6), "gilt", tag="shoulder_board")
        k.box(to, C(sx * 13.4, 68.4, 4.6, 2.4, 2.4, 1.0), "glow", group="glow", tag="star")
    k.box(to, C(0, 63.4, 4.0, 4.6, 2.8, 1.2), "red", tag="cravat")
    # ---------------------------------------------------------------- the head: the white grin mask, the monocle, the hat
    hd = k.part("head", (0, 68, 0.6), (("x", -4), ("z", -6)), "torso")
    k.box(hd, C(0, 67.6, 0.6, 2.8, 2.4, 2.8), "cream", tag="neck")
    k.box(hd, C(0, 70.0, 0.6, 8.6, 9.6, 8.4), "porcelain", tag="face")
    k.box(hd, C(0, 72.8, 4.85, 2.0, 2.6, 1.2), "porcelain", tag="nose")
    grin(k, hd, 0, 71.2, 4.85, 7.2, teeth=9, s=1.2)
    k.box(hd, C(-2.2, 75.2, 4.85, 2.0, 1.2, 0.3), "dark", tag="eye_slit")
    k.box(hd, C(-2.2, 75.4, 4.95, 1.2, 0.6, 0.3), "eye", group="glow", tag="eye")
    k.ring(hd, 2.2, 75.8, 4.95, 1.8, 0.5, "gilt", "monocle", n=10)
    k.box(hd, C(2.2, 74.8, 4.95, 2.6, 2.2, 0.3), "eye", group="glow", tag="eye")
    k.limb(hd, (3.8, 75.0, 5.0), (4.6, 68, 5.6), 0.3, "gilt", "monocle_chain")
    for sx in (-1, 1):
        k.box(hd, C(sx * 4.6, 73.4, 1.6, 0.8, 3.0, 2.6), "dark", tag="cheek_paint")
        k.box(hd, C(sx * 2.6, 77.6, 4.85, 3.0, 0.6, 0.3), "dark", tag="brow")
    k.box(hd, C(0, 79.4, 0.6, 15.4, 1.2, 14.4), "black", tag="hat_brim")
    k.stack(hd, 0, 0.6, [(80.6, 9.4, 9.0), (88, 10.0, 9.6), (96, 11.4, 10.8), (98, 11.6, 11.0)], "black", "hat")
    k.box(hd, C(0, 81.0, 0.6, 10.0, 2.4, 9.6), "red", tag="hat_band")
    k.box(hd, C(4.0, 81.2, 5.4, 2.6, 2.6, 0.6), "gilt", tag="hat_badge")
    # the rip in the crown, the light inside it pouring out, and the hat stuffed with what it took
    for (y, x) in ((91, 1.6), (93, 0.4), (95, -1.0), (89, 2.6)):
        k.box(hd, C(x, y, 5.6, 2.4, 2.4, 0.6), "glow", group="glow", tag="hat_light")
    k.box(hd, C(0, 98.2, 0.6, 10.0, 0.6, 9.4), "glow", group="glow", tag="hat_top_light")
    for (x, z, L) in ((-3, -2, 6), (2, 3, 8), (3, -3, 5)):
        k.shard(hd, (x, 98, 0.6 + z), (x * 0.1, 1, z * 0.1), L, 1.0, mat="glow", tag="light_ray", group="glow")
    # ---------------------------------------------------------------- arms: long and thin, white gloves
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 13
        up = k.part("arm_" + nm, (x, 64, 0), (("x", -60 if side > 0 else -30), ("z", side * 16)), "torso")
        fo = k.part("fore_" + nm, (x, 50, 0), (("x", -50 if side > 0 else -40),), up)
        hn = k.part("hand_" + nm, (x, 36, 0), (), fo)
        k.blob(up, (x, 63, 0), (4.4, 3.4, 4.6), "red", "shoulder")
        k.stack(up, x, 0, [(50, 5.0, 5.2), (64, 6.0, 6.2)], "red", "sleeve")
        k.stack(fo, x, 0, [(37, 6.2, 6.4), (40, 5.0, 5.2), (50, 4.8, 5.0)], "red", "sleeve")
        k.box(fo, C(x, 37, 0, 6.6, 2.2, 6.8), "gilt", tag="cuff")
        k.box(hn, C(x, 31, 0.4, 4.8, 5.6, 4.8), "cream", tag="glove")
        for t in (-1.6, -0.5, 0.6, 1.7):
            k.box(hn, C(x + t, 27.4, 1.2, 1.0, 3.6, 1.2), "cream", tag="finger")
    # the cane: a striped pole, a gilt collar, the crystal ball holding the show's light
    cn = k.part("cane", (13, 32, 1), (("x", 20),), k.parts["hand_l"])
    k.limb(cn, (13, -2, 1), (13, 44, 1), 2.6, "hstripe", "cane", d=2.6)
    k.box(cn, C(13, 43, 1, 3.4, 2.0, 3.4), "gilt", tag="cane_collar")
    k.blob(cn, (13, 48, 1), (3.6, 3.6, 3.6), "glow", "crystal_ball", step=0.9)
    for a in range(0, 360, 90):
        r = math.radians(a)
        k.limb(cn, (13, 44, 1), (13 + math.cos(r) * 3.0, 47, 1 + math.sin(r) * 3.0), 0.6, "gilt", "claw")
    # the whip of chain, coiled out from the right hand
    wp = k.part("whip", (-13, 32, 1), (("x", 60),), k.parts["hand_r"])
    k.limb(wp, (-13, 28, 1), (-13, 36, 1), 1.8, "black", "whip_handle")
    k.box(wp, C(-13, 35.4, 1, 2.6, 1.2, 2.6), "gilt", tag="whip_pommel")
    pts = [(-13, 28, 1), (-15, 20, 4), (-12, 12, 8), (-16, 6, 12), (-20, 4, 18), (-22, 8, 24), (-20, 14, 28)]
    for (a, b), w in zip(zip(pts, pts[1:]), (1.6, 1.5, 1.3, 1.2, 1.0, 0.8)):
        k.limb(wp, a, b, w, "iron", "chain_whip", d=w * 0.6)
    k.shard(wp, (-20, 14, 28), (0.3, 1, 0.4), 3.0, 1.4, mat="iron", tag="whip_barb")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Harlequin (elite, the key)

def harlequin():
    """The star of the show, who has danced every night since the last audience left. Long-limbed, in diamond
    motley red and black, a ruff; a porcelain mask split down the middle - one half laughing, one half weeping
    tears of black paint; a three-horned jester's cap whose bells are little skulls. Two thin rapiers. The key to
    the Ringmaster's ring hangs round its neck on a ribbon."""
    k = X.Kit("harlequin")
    hips = k.part("hips", (0, 21, 0))
    k.box(hips, C(0, 18.4, 0, 8.4, 3.8, 5.4), "motley", tag="hips")
    k.box(hips, C(0, 21.0, 0, 9.0, 1.4, 6.0), "black", tag="belt")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.4
        th = k.part("thigh_" + nm, (x, 21, 0), (("x", -20 if side > 0 else 6), ("z", side * 6)), "hips")
        sh = k.part("shin_" + nm, (x, 11.4, 0), (("x", 24 if side > 0 else 6),), th)
        ft = k.part("foot_" + nm, (x, 2.2, 0), (("x", -10),), sh)
        k.box(th, C(x, 11.6, 0, 3.4, 9.8, 3.6), "motley", tag="thigh")
        k.box(sh, C(x, 2.2, 0, 3.2, 9.4, 3.4), "motley", tag="shin")
        k.box(ft, C(x, 0, 1.6, 3.2, 2.2, 6.4), "black", tag="foot")
        k.shard(ft, (x, 1.0, 4.6), (0, 0.6, 1), 3.0, 1.4, mat="black", tag="foot")       # curled toe
        k.box(ft, C(x, 3.2, 7.2, 1.0, 1.0, 1.0), "gilt", tag="toe_bell")
    # ---------------------------------------------------------------- torso: slim, a big ruff
    to = k.part("torso", (0, 21, 0), (("x", 4), ("y", -10)), "hips")
    k.stack(to, 0, 0, [(21, 8.4, 5.4), (26, 9.6, 5.8), (32, 11.4, 6.0)], "motley", "torso")
    for i in range(14):      # the ruff: pleats all round the neck
        a = math.radians(i * 360 / 14)
        k.box(to, C(math.sin(a) * 4.6, 31.6, math.cos(a) * 4.0, 2.4, 2.4, 2.4), "cream", tag="ruff")
    k.limb(to, (-2.4, 32, 2.6), (0, 26, 3.4), 0.5, "red", "ribbon")
    k.limb(to, (2.4, 32, 2.6), (0, 26, 3.4), 0.5, "red", "ribbon")
    k.box(to, C(0, 24.4, 3.6, 1.2, 2.4, 0.5), "gilt", tag="key")
    k.box(to, C(0.6, 24.4, 3.6, 1.0, 0.6, 0.5), "gilt", tag="key_bit")
    # ---------------------------------------------------------------- the head: split mask, three-horned cap with skull bells
    hd = k.part("head", (0, 33, 0.4), (("x", -6), ("z", 10)), "torso")
    k.box(hd, C(0, 33.2, 0.4, 5.6, 6.2, 5.6), "porcelain", tag="face")
    k.box(hd, C(0, 33.2, 3.25, 0.3, 6.2, 0.3), "dark", tag="split")
    k.box(hd, C(-1.4, 37.0, 3.25, 1.4, 0.7, 0.3), "dark", tag="eye_hole")
    k.box(hd, C(-1.4, 37.1, 3.35, 0.8, 0.4, 0.2), "eye", group="glow", tag="eye")
    k.box(hd, C(1.4, 36.6, 3.25, 1.4, 1.0, 0.3), "dark", tag="eye_hole")
    k.box(hd, C(1.4, 36.8, 3.35, 0.8, 0.4, 0.2), "eye", group="glow", tag="eye")
    k.box(hd, C(-1.4, 34.4, 3.25, 1.8, 0.5, 0.3), "dark", tag="laugh")       # the laughing half
    k.box(hd, C(-2.2, 34.9, 3.25, 0.5, 0.6, 0.3), "dark", tag="laugh")
    k.box(hd, C(1.4, 34.6, 3.25, 1.8, 0.5, 0.3), "dark", tag="weep")         # the weeping half
    k.box(hd, C(2.2, 34.2, 3.25, 0.5, 0.6, 0.3), "dark", tag="weep")
    k.box(hd, C(1.4, 33.4, 3.3, 0.4, 3.2, 0.2), "dark", tag="tear")
    k.box(hd, C(0, 39.4, 0.4, 6.4, 1.6, 6.4), "motley", tag="cap")
    for i, (dx, dz, col) in enumerate(((-1, 0, "motley"), (1, 0, "motley2"), (0, -1, "motley"))):
        pts = [(dx * 2.0, 40.6, 0.4 + dz * 2.0), (dx * 4.4, 43.6, 0.4 + dz * 4.0), (dx * 6.4, 43.0, 0.4 + dz * 6.4), (dx * 7.4, 40.4, 0.4 + dz * 7.4)]
        for (a, b), w in zip(zip(pts, pts[1:]), (2.2, 1.6, 1.0)):
            k.limb(hd, a, b, w, col, "cap_horn")
        x, y, z = pts[-1]
        k.box(hd, C(x, y - 2.2, z, 1.8, 1.8, 1.8), "cream", tag="skull_bell")
        k.box(hd, C(x, y - 1.4, z + 0.9, 1.2, 0.5, 0.2), "dark", tag="skull_bell_eyes")
    # ---------------------------------------------------------------- arms: long, the two rapiers
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 6.4
        up = k.part("arm_" + nm, (x, 30, 0), (("x", -80 if side > 0 else -30), ("z", side * 30)), "torso")
        fo = k.part("fore_" + nm, (x, 21.6, 0), (("x", -20 if side > 0 else -70),), up)
        hn = k.part("hand_" + nm, (x, 13.4, 0), (), fo)
        k.box(up, C(x, 21.8, 0, 2.8, 8.2, 3.0), "motley", tag="sleeve")
        k.box(fo, C(x, 13.8, 0, 2.6, 7.8, 2.8), "motley", tag="sleeve")
        k.box(fo, C(x, 13.8, 0, 3.6, 1.4, 3.8), "cream", tag="cuff_ruff")
        k.box(hn, C(x, 11.0, 0.3, 2.4, 2.8, 2.4), "black", tag="glove")
        rp = k.part("rapier_" + nm, (x, 12.4, 0.4), (("x", 80),), hn)
        k.box(rp, C(x, 10.4, 0.4, 0.9, 3.8, 0.9), "black", tag="grip")
        k.ring(rp, x, 14.4, 0.4, 1.6, 0.4, "gilt", "swept_hilt", n=8, axis="x")
        k.box(rp, C(x, 14.0, 0.4, 0.6, 0.8, 4.6), "gilt", tag="quillon")
        k.box(rp, C(x, 14.8, 0.4, 0.4, 20, 0.7), "iron", tag="blade")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Strongman (brute)

def strongman():
    """The strongman wore the circus lion when the lion died, and now he can't take it off: the mane round his
    shoulders, the jaws over his head like a hood, the teeth on his brow. Under it a body like a barrel on posts in
    a striped leotard, a moustache waxed into hooks and a grin stitched wider than it ever was. He swings the
    show barbell: two cannonballs on a bar, chained to his wrist so he can never put it down."""
    k = X.Kit("strongman")
    hips = k.part("hips", (0, 22, 0))
    k.stack(hips, 0, 0, [(16, 14, 9.6), (22, 15, 10)], "hstripe", "leotard")
    k.box(hips, C(0, 21, 0, 16.4, 3.4, 11), "black", tag="belt")
    k.box(hips, C(0, 21, 5.6, 5.0, 3.6, 0.8), "gilt", tag="belt_plate")
    k.rivets(hips, [(sx, 22.6, 5.6) for sx in (-6, -3, 3, 6)], "iron", 0.9)
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 4.4
        th = k.part("thigh_" + nm, (x, 19, 0), (("x", -8), ("z", side * 10)), "hips")
        sh = k.part("shin_" + nm, (x, 10.6, 0), (("x", 12),), th)
        ft = k.part("foot_" + nm, (x, 2.6, 0), (("x", -4),), sh)
        k.stack(th, x, 0, [(10.6, 6.6, 6.8), (16, 7.6, 7.8), (19, 7.0, 7.2)], "skin", "thigh")
        k.stack(sh, x, 0, [(2.6, 6.6, 7.0), (10.6, 7.2, 7.4)], "black", "boot")
        k.box(sh, C(x, 9.6, 0, 7.8, 1.4, 8.0), "gilt", tag="boot_band")
        k.box(ft, C(x, 0, 1.6, 7.6, 2.8, 10.6), "black", tag="foot")
    # ---------------------------------------------------------------- torso: a barrel, the leotard strap, tattoos
    to = k.part("torso", (0, 22, 0), (("x", 10),), "hips")
    k.stack(to, 0, 0.4, [(22, 15, 10), (28, 20, 12), (34, 25, 13), (38, 24, 12)], "skin", "chest")
    k.stack(to, 0, 0.4, [(22, 15.6, 10.6), (26, 18.6, 11.6), (29, 20.4, 12.2)], "hstripe", "leotard")
    k.limb(to, (5.4, 29, 6.0), (6.8, 38, 3), 2.6, "hstripe", "strap", d=0.8)
    k.box(to, C(-4.6, 32, 6.6, 4.0, 4.0, 0.4), "teal", tag="tattoo_anchor")
    k.box(to, C(-4.6, 30, 6.6, 1.0, 6.0, 0.4), "teal", tag="tattoo_anchor")
    # the lion skin: the mane round his shoulders, the jaws over his head
    k.blob(to, (0, 38.4, -1.2), (14, 4.6, 9.6), "fur", "mane")
    for i in range(16):
        a = math.radians(i * 22.5)
        k.shard(to, (math.sin(a) * 11, 37, -1.2 + math.cos(a) * 7.4), (math.sin(a), -0.6, math.cos(a)), 6, 2.4, mat="fur", tag="mane_lock")
    k.box(to, C(0, 22, -6.4, 9, 16, 1.0), "fur", tag="lion_back")
    # ---------------------------------------------------------------- the head: in the lion's jaws, a stitched grin, the moustache
    hd = k.part("head", (0, 38, 1.0), (("x", -10),), "torso")
    k.box(hd, C(0, 38.4, 1.4, 7.4, 7.8, 7.4), "skin", tag="face")
    grin(k, hd, 0, 40.0, 5.15, 6.0, teeth=7, s=0.9)
    for t in range(6):
        k.box(hd, C(-2.5 + t, 40.3, 5.25, 0.3, 2.4, 0.2), "dark", tag="stitch")
    for sx in (-1, 1):       # the moustache waxed into hooks
        k.limb(hd, (0, 42.4, 5.4), (sx * 3.6, 42.0, 5.6), 1.2, "black", "moustache")
        k.limb(hd, (sx * 3.6, 42.0, 5.6), (sx * 4.4, 43.6, 5.6), 0.8, "black", "moustache")
        k.box(hd, C(sx * 1.6, 43.8, 5.15, 1.4, 0.8, 0.3), "eye", group="glow", tag="eye")
    k.blob(hd, (0, 47.4, 1.8), (5.6, 3.0, 6.2), "fur", "lion_head")
    k.box(hd, C(0, 46.0, 7.0, 7.0, 2.4, 3.0), "fur", tag="lion_muzzle")
    k.box(hd, C(0, 46.6, 8.6, 2.4, 1.6, 0.6), "dark", tag="lion_nose")
    for sx in (-2.6, -0.9, 0.9, 2.6):
        k.shard(hd, (sx, 45.2, 7.8), (0, -1, 0.15), 2.6 if abs(sx) > 2 else 1.4, 0.8, mat="cream", tag="lion_tooth")
    for sx in (-1, 1):
        k.box(hd, C(sx * 2.4, 48.4, 6.6, 1.6, 0.8, 0.4), "dark", tag="lion_eye")
        k.shard(hd, (sx * 4.4, 49.0, 0.4), (sx * 0.4, 1, -0.3), 2.0, 1.6, mat="fur", tag="lion_ear")
    # ---------------------------------------------------------------- arms: the biggest in the show
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 14
        up = k.part("arm_" + nm, (x, 36, 0), (("x", -20 if side > 0 else -100), ("z", side * 14)), "torso")
        fo = k.part("fore_" + nm, (x, 25, 0), (("x", -60 if side > 0 else -20),), up)
        hn = k.part("hand_" + nm, (x, 14, 0), (), fo)
        k.blob(up, (x, 34, 0), (6.0, 5.0, 6.2), "skin", "shoulder")
        k.stack(up, x, 0, [(25, 7.0, 7.2), (30, 8.4, 8.4)], "skin", "upper_arm")
        k.stack(fo, x, 0, [(15, 7.4, 7.4), (20, 8.4, 8.4), (25, 7.0, 7.0)], "skin", "forearm")
        k.box(fo, C(x, 15, 0, 8.6, 3.4, 8.6), "black", tag="wrist_strap")
        k.rivets(fo, [(x - 4.4, 16.6, 0), (x + 4.4, 16.6, 0)], "gilt", 1.0)
        k.box(hn, C(x, 9.0, 0.6, 7.0, 6.0, 7.0), "skin", tag="fist")
    # the barbell: a bar and two cannonballs, chained to his right wrist
    bb = k.part("barbell", (-14, 10, 0.6), (("z", 90), ("y", 10)), k.parts["hand_r"])
    k.limb(bb, (-14, -2, 0.6), (-14, 22, 0.6), 1.8, "iron", "bar")
    for y in (-6, 26):
        k.blob(bb, (-14, y, 0.6), (6.6, 6.6, 6.6), "black", "cannonball", step=1.2)
        k.box(bb, C(-14, y - 0.4, 0.6, 9.0, 1.0, 9.0), "gilt", tag="ball_band")
        k.box(bb, C(-14, y + 1.6, 6.4, 2.6, 2.6, 0.6), "cream", tag="ball_number")
    k.chain(k.parts["fore_r"], (-14, 15, 4.4), (-14, 6, 6), 3, w=1.2)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Fire Eater (caster)

def fire_eater():
    """He ate the fire every night, until one night it ate him back, and he went on with the act. Burnt black and
    cracked under the greasepaint, the paint still on - white face, red diamonds round the eyes - flame coming out
    of his mouth like a beard, a torch in each hand, a vest of tassels, a can of lamp oil on his belt."""
    k = X.Kit("fire_eater")
    hips = k.part("hips", (0, 19, 0))
    k.box(hips, C(0, 16.4, 0, 8.2, 3.8, 5.4), "stripe", tag="trousers")
    k.box(hips, C(0, 19.0, 0, 8.8, 1.6, 5.8), "red", tag="sash")
    k.box(hips, C(-4.8, 13.6, 1.0, 2.6, 4.0, 2.6), "iron", tag="oil_can")
    k.box(hips, C(-4.8, 17.8, 1.0, 1.0, 0.8, 1.0), "iron", tag="oil_cap")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.4
        th = k.part("thigh_" + nm, (x, 19, 0), (("x", -8), ("z", side * 6)), "hips")
        sh = k.part("shin_" + nm, (x, 10.2, 0), (("x", 12),), th)
        ft = k.part("foot_" + nm, (x, 2.2, 0), (("x", -4),), sh)
        k.box(th, C(x, 10.4, 0, 3.8, 8.8, 4.0), "stripe", tag="trouser")
        k.box(sh, C(x, 2.2, 0, 3.8, 8.4, 4.0), "stripe", tag="trouser")
        k.box(ft, C(x, 0, 1.4, 3.6, 2.2, 6.0), "black", tag="foot")
    # ---------------------------------------------------------------- torso: burnt, a tasselled vest
    to = k.part("torso", (0, 19, 0), (("x", -6),), "hips")
    k.stack(to, 0, 0, [(19, 8.4, 5.4), (24, 9.6, 5.8), (30, 11.4, 6.0)], "soot", "chest")
    for sx in (-1, 1):
        k.box(to, C(sx * 3.6, 20.4, 0, 4.0, 9.4, 6.4), "red", tag="vest")
        for i in range(4):
            k.limb(to, (sx * (2.0 + i * 1.2), 20.4, 3.3), (sx * (2.0 + i * 1.2), 17.6, 3.5), 0.5, "gilt", "tassel")
    for (x, y) in ((-1, 26), (1.4, 23), (0, 28.6)):
        k.box(to, C(x, y, 2.95, 0.5, 2.4, 0.3), "fire", group="glow", tag="crack")
    # ---------------------------------------------------------------- the head: greasepaint on the burnt face, a flame beard
    hd = k.part("head", (0, 30, 0.4), (("x", -20),), "torso")
    k.box(hd, C(0, 30.2, 0.4, 5.4, 6.0, 5.4), "soot", tag="head")
    k.box(hd, C(0, 31.0, 3.1, 4.4, 4.8, 0.3), "cream", tag="greasepaint")
    for sx in (-1.2, 1.2):
        k.box(hd, C(sx, 33.2, 3.2, 1.6, 1.6, 0.3), "red", tag="diamond")
        k.box(hd, C(sx, 33.6, 3.3, 0.8, 0.6, 0.3), "eye", group="glow", tag="eye")
    k.box(hd, C(0, 31.0, 3.25, 2.6, 1.6, 0.4), "fire", group="glow", tag="mouth")
    flame = [(0, 31.4, 3.6), (0, 30.4, 6.0), (0.4, 32.0, 8.4), (-0.4, 34.4, 10.0), (0, 37.4, 10.4)]
    for (a, b), w in zip(zip(flame, flame[1:]), (2.4, 2.8, 2.4, 1.6)):
        k.limb(hd, a, b, w, "fire", "breath", group="glow")
    for (x, z) in ((-1.2, 0), (1.0, -1.2), (0, 1.4)):          # what's left of his hair, still smouldering
        k.shard(hd, (x, 36.0, 0.4 + z), (x * 0.2, 1, -0.2), 2.4, 1.2, mat="fire", tag="hair_flame", group="glow")
    # ---------------------------------------------------------------- arms: a torch in each hand, held wide
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 6.4
        up = k.part("arm_" + nm, (x, 28.4, 0), (("x", -30), ("z", side * 40)), "torso")
        fo = k.part("fore_" + nm, (x, 21, 0), (("x", -70),), up)
        hn = k.part("hand_" + nm, (x, 13.8, 0), (), fo)
        k.box(up, C(x, 21.2, 0, 3.0, 7.4, 3.2), "soot", tag="arm")
        k.box(fo, C(x, 14.0, 0, 2.8, 7.2, 3.0), "soot", tag="forearm")
        k.box(fo, C(x, 18.0, 1.5, 0.4, 2.4, 0.3), "fire", group="glow", tag="crack")
        k.box(hn, C(x, 11.4, 0.3, 2.6, 2.8, 2.6), "soot", tag="hand")
        tc = k.part("torch_" + nm, (x, 12.6, 0.4), (("x", 90),), hn)
        k.limb(tc, (x, 9.0, 0.4), (x, 20.0, 0.4), 1.0, "wood", "torch_handle")
        k.box(tc, C(x, 19.4, 0.4, 2.0, 2.0, 2.0), "iron", tag="torch_cup")
        k.blob(tc, (x, 23.0, 0.4), (1.8, 2.8, 1.8), "fire", "torch_flame", step=0.8)
        k.shard(tc, (x, 24.4, 0.4), (0, 1, 0), 3.0, 1.4, mat="fire", tag="torch_flame", group="glow")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Knife Juggler (skirmisher)

def knife_juggler():
    """A clown gone thin as a rake, in a long patched coat, a ruff, a bald painted head with a tuft of red hair each
    side and a grin painted past the cheeks. A fan of knives in each hand, ready to throw; on his back the wheel
    of the knife-throwing act, a painted target with knives still in it."""
    k = X.Kit("knife_juggler")
    hips = k.part("hips", (0, 20, 0))
    k.box(hips, C(0, 17.4, 0, 7.6, 3.6, 5.0), "motley2", tag="trousers")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.2
        th = k.part("thigh_" + nm, (x, 20, 0), (("x", -10), ("z", side * 8)), "hips")
        sh = k.part("shin_" + nm, (x, 10.8, 0), (("x", 16),), th)
        ft = k.part("foot_" + nm, (x, 2.2, 0), (("x", -6),), sh)
        k.box(th, C(x, 11.0, 0, 3.0, 9.2, 3.2), "motley2", tag="thigh")
        k.box(sh, C(x, 2.2, 0, 2.8, 8.8, 3.0), "motley2", tag="shin")
        k.box(ft, C(x, 0, 2.4, 3.6, 2.4, 8.4), "red", tag="foot")           # the big clown shoes
        k.box(ft, C(x, 2.0, 0.0, 2.8, 0.6, 3.0), "cream", tag="spat")
    # the long patched coat
    for (x, z, w) in ((-3.0, 3.0, 3.0), (3.0, 3.0, 3.0), (0, -3.0, 8.0)):
        k.box(hips, C(x, 6, z, w, 15, 0.7), "teal", tag="coat")
    k.box(hips, C(-3.0, 10, 3.4, 2.0, 2.4, 0.3), "red", tag="patch")
    k.box(hips, C(1.6, -3.0 + 12, -3.4, 2.4, 2.0, 0.3), "cream", tag="patch")
    # ---------------------------------------------------------------- torso
    to = k.part("torso", (0, 20, 0), (("x", 10),), "hips")
    k.stack(to, 0, 0, [(20, 7.6, 5.0), (25, 8.6, 5.4), (31, 10.0, 5.6)], "teal", "coat")
    for y in (22, 25, 28):
        k.box(to, C(0, y, 2.85, 1.4, 1.4, 0.4), "red", tag="pompom")
    for i in range(12):
        a = math.radians(i * 30)
        k.box(to, C(math.sin(a) * 4.0, 31.0, math.cos(a) * 3.4, 2.0, 2.0, 2.0), "cream", tag="ruff")
    # the target wheel on his back
    tw = k.part("target", (0, 26, -4), (), to, bone=False)
    for r, col in ((8.0, "red"), (6.0, "cream"), (4.0, "red"), (2.0, "cream")):
        k.box(tw, C(0, 26 - r, -4.0 - (8 - r) * 0.05, r * 2, r * 2, 0.8), col, tag="target")
    for (x, y, a) in ((-4, 28, 0.3), (3, 22, -0.4), (5, 30, 0.6), (-2, 20, -0.2)):
        k.limb(tw, (x, y, -4.6), (x + a, y + 0.6, -8.4), 0.4, "iron", "stuck_knife")
        k.box(tw, C(x + a, y + 0.6, -9.2, 0.6, 0.6, 1.6), "black", tag="stuck_knife_grip")
    # ---------------------------------------------------------------- the head: bald, painted, tufts of red
    hd = k.part("head", (0, 31.6, 0.4), (("x", -10), ("z", -12)), "torso")
    k.box(hd, C(0, 31.6, 0.4, 5.4, 6.4, 5.4), "porcelain", tag="face")
    grin(k, hd, 0, 32.6, 3.15, 4.6, teeth=6, s=0.8)
    k.box(hd, C(0, 34.4, 3.3, 1.4, 1.4, 1.0), "red", tag="nose")
    for sx in (-1.4, 1.4):
        k.box(hd, C(sx, 35.6, 3.15, 1.0, 1.4, 0.3), "dark", tag="eye_paint")
        k.box(hd, C(sx, 35.9, 3.25, 0.6, 0.5, 0.2), "eye", group="glow", tag="eye")
    for sx in (-1, 1):
        k.blob(hd, (sx * 3.6, 36.0, -0.2), (1.6, 1.8, 2.0), "red", "hair_tuft", step=0.8)
    # ---------------------------------------------------------------- arms: a fan of knives in each hand
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 6.0
        up = k.part("arm_" + nm, (x, 29.6, 0), (("x", -120 if side < 0 else -40), ("z", side * 20)), "torso")
        fo = k.part("fore_" + nm, (x, 21.6, 0), (("x", -20 if side < 0 else -50),), up)
        hn = k.part("hand_" + nm, (x, 13.6, 0), (), fo)
        k.box(up, C(x, 21.8, 0, 3.0, 7.8, 3.2), "teal", tag="sleeve")
        k.box(fo, C(x, 14.0, 0, 2.8, 7.6, 3.0), "teal", tag="sleeve")
        k.box(fo, C(x, 14.0, 0, 3.8, 1.2, 4.0), "cream", tag="cuff_ruff")
        k.box(hn, C(x, 11.2, 0.3, 2.6, 2.8, 2.6), "cream", tag="glove")
        for i in range(5):           # five knives fanned out, held by the tips
            a = math.radians(-40 + i * 20)
            d = (math.sin(a), -math.cos(a), 0.2)
            k.limb(hn, (x, 10.6, 0.8), (x + d[0] * 6, 10.6 + d[1] * 6, 0.8 + d[2] * 6), 0.8, "iron", "fan_knife", d=0.3)
            k.box(hn, C(x + d[0] * 7, 10.6 + d[1] * 7 - 0.6, 0.8 + d[2] * 7, 0.9, 1.4, 0.9), "black", tag="fan_knife_grip")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Circus Puppet (swarm)

def circus_puppet():
    """The marionettes from the puppet tent walk on their own now, but they still wear their strings, and the
    strings still go up to the cross of wood that once worked them - it jerks above their heads as they come.
    Ball joints at every limb, a cracked porcelain face with painted cheeks, motley rags, a key in its back that
    turns."""
    k = X.Kit("circus_puppet")
    hips = k.part("hips", (0, 18, 0))
    k.box(hips, C(0, 15.6, 0, 6.6, 3.6, 4.4), "paint", tag="pelvis")
    k.box(hips, C(0, 14.0, 0, 8.0, 4.0, 5.6), "motley", tag="skirt")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.0
        th = k.part("thigh_" + nm, (x, 15.6, 0), (("x", -10), ("z", side * 8)), "hips")
        sh = k.part("shin_" + nm, (x, 8.6, 0), (("x", 20),), th)
        ft = k.part("foot_" + nm, (x, 1.8, 0), (("x", -10),), sh)
        k.box(th, C(x, 9.6, 0, 2.2, 6.0, 2.2), "paint", tag="thigh")
        k.blob(th, (x, 8.8, 0), (1.5, 1.5, 1.5), "wood", "knee_ball", step=0.6)
        k.box(sh, C(x, 2.4, 0, 2.0, 5.6, 2.0), "paint", tag="shin")
        k.box(ft, C(x, 0, 1.0, 2.6, 1.8, 4.2), "black", tag="foot")
    # ---------------------------------------------------------------- torso: a carved block, painted buttons, the key
    to = k.part("torso", (0, 18, 0), (("x", 14), ("z", 6)), "hips")
    k.stack(to, 0, 0, [(18, 6.0, 4.0), (22, 7.0, 4.4), (26, 7.8, 4.6)], "paint", "torso")
    k.box(to, C(0, 22, 0, 8.2, 4.4, 5.0), "motley", tag="tunic")
    for y in (20.0, 23.4):
        k.box(to, C(0, y, 2.35, 1.0, 1.0, 0.3), "red", tag="button")
    k.limb(to, (0, 23, -2.4), (0, 23, -5.0), 0.8, "gilt", "key_shaft")
    k.box(to, C(0, 23, -5.6, 3.6, 2.4, 0.8), "gilt", tag="key_bow")
    # ---------------------------------------------------------------- the head: cracked porcelain, painted cheeks
    hd = k.part("head", (0, 26.4, 0.2), (("x", -14), ("z", 18)), "torso")
    k.blob(hd, (0, 28.8, 0.2), (2.6, 3.0, 2.6), "porcelain", "head", step=0.6)
    k.box(hd, C(-0.6, 28.0, 2.6, 0.4, 3.4, 0.3), "dark", tag="crack")
    for sx in (-1.0, 1.0):
        k.box(hd, C(sx, 29.8, 2.45, 0.8, 0.8, 0.3), "dark", tag="eye_hole")
        k.box(hd, C(sx, 30.0, 2.55, 0.4, 0.4, 0.2), "eye", group="glow", tag="eye")
        k.box(hd, C(sx * 1.6, 28.2, 2.3, 0.8, 0.8, 0.3), "red", tag="cheek")
    k.box(hd, C(0, 27.4, 2.45, 1.6, 0.4, 0.3), "dark", tag="mouth")
    k.box(hd, C(0, 26.6, 2.45, 0.3, 0.8, 0.3), "dark", tag="jaw_line")
    k.box(hd, C(0, 31.6, 0.2, 5.4, 1.0, 5.4), "red", tag="cap")
    k.shard(hd, (0, 32.4, 0.2), (0.3, 1, -0.4), 3.4, 2.6, mat="red", tag="cap")
    # the strings and the cross of wood above
    cr = k.part("cross", (0, 42, 0), (("y", 20),), hd, bone=False)
    k.box(cr, C(0, 41.6, 0, 9.0, 0.8, 0.8), "wood", tag="cross")
    k.box(cr, C(0, 41.6, 0, 0.8, 0.8, 7.0), "wood", tag="cross")
    for (a, b) in (((0, 41.6, 0), (0, 32.6, 0.2)), ((4.2, 41.6, 0), (4.0, 22, 0)), ((-4.2, 41.6, 0), (-4.0, 22, 0)),
                   ((0, 41.6, 3.2), (2.0, 10, 0)), ((0, 41.6, -3.2), (-2.0, 10, 0))):
        k.limb(cr, a, b, 0.15, "cream", "string")
    # ---------------------------------------------------------------- arms: jointed, dangling
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 4.4
        up = k.part("arm_" + nm, (x, 25, 0), (("x", -50 if side > 0 else -20), ("z", side * 20)), "torso")
        fo = k.part("fore_" + nm, (x, 19.4, 0), (("x", -40 if side > 0 else -10),), up)
        hn = k.part("hand_" + nm, (x, 14.0, 0), (), fo)
        k.blob(up, (x, 24.6, 0), (1.4, 1.4, 1.4), "wood", "shoulder_ball", step=0.6)
        k.box(up, C(x, 19.8, 0, 1.8, 4.6, 1.8), "paint", tag="upper_arm")
        k.blob(fo, (x, 19.2, 0), (1.2, 1.2, 1.2), "wood", "elbow_ball", step=0.6)
        k.box(fo, C(x, 14.4, 0, 1.6, 4.6, 1.6), "paint", tag="forearm")
        k.box(hn, C(x, 11.8, 0.2, 2.0, 2.4, 1.4), "porcelain", tag="hand")
        for t in (-0.6, 0, 0.6):
            k.box(hn, C(x + t, 10.0, 0.6, 0.4, 2.0, 0.4), "porcelain", tag="finger")
    k.s.shaders = shaders()
    return k.s, k.parts


MOBS = {
    "circus_puppet": dict(make=circus_puppet, ent=(0.8, 2.4), stats=dict(hp=16, speed=0.28, dmg=4, armor=0, kb=0)),
    "strongman": dict(make=strongman, ent=(1.5, 3.8), stats=dict(hp=72, speed=0.2, dmg=12, armor=3, kb=0.9)),
    "fire_eater": dict(make=fire_eater, ent=(0.9, 2.8), stats=dict(hp=26, speed=0.23, dmg=6, armor=1, kb=0)),
    "knife_juggler": dict(make=knife_juggler, ent=(0.8, 2.7), stats=dict(hp=24, speed=0.34, dmg=6, armor=1, kb=0)),
    "harlequin": dict(make=harlequin, ent=(1.0, 3.1), stats=dict(hp=145, speed=0.27, dmg=10, armor=6, kb=0.5), key=True),
    "ringmaster": dict(make=ringmaster, texel=1, ent=(2.2, 6.4), stats=dict(hp=450, speed=0.23, dmg=15, armor=8, kb=0.9), boss=True),
}
