"""The Sandsunk Tomb's monsters, each built by hand (tools/vox2.py). The tomb of a sun-king the desert swallowed:
old linen gone brown, beaten gold, lapis and turquoise, sandstone, black basalt for the jackal-god, bronze, and the
hot gold light of the sun he swore would never set on him.

    tomb_scarab    swarm   a scarab as big as a dog, a sun disc held up between its horns, wing cases cracked open on light
    sand_colossus  brute   a tomb statue that walks: a pharaoh's guard in sandstone, cracked open, sand pouring out, an obelisk
    embalmer       caster  the priest who wrapped the king: an ibis mask, bandaged arms, hooks and jars, a censer of natron
    jackal_runner  skirm   a jackal-headed tomb guard, crouched to run, black and gold, a khopesh in each hand
    sun_guardian   elite   the king's last guard: a mummy in gold scale under a falcon helm, a sun-disc shield, the ankh key
    sun_king       boss    the Sun-King: a giant mummy in gold and linen, a death mask, the nemes, a burning sun disc behind
                           his head, the crook and the flail

    python tools/monsterforge.py sandsunk_tomb --preview ; python tools/mobsheet.py sandsunk_tomb
"""
import math

import vox2 as X
from vox2 import C, ramp

LINEN = ramp("#1e160c", "#2e2214", "#42321e", "#58442a", "#6e5838", "#867048")
GOLD = ramp("#3a2606", "#5e400c", "#8a6214", "#b48a24", "#dab43c", "#f4d870")
LAPIS = ramp("#060c22", "#0c1838", "#142650", "#1e386e", "#2c4e90")
TURQ = ramp("#0a2a28", "#124440", "#1e605a", "#2e8078", "#46a096")
SANDST = ramp("#3e2a14", "#5a3e1e", "#76542a", "#946c38", "#ae8648", "#c8a060")
BASALT = ramp("#060606", "#0e0d0c", "#181614", "#22201c", "#2e2a26")
SKIN = ramp("#1a120a", "#2a1c10", "#3a2816", "#4c361e", "#604428")
SUN = ramp("#8a4a0a", "#c4720e", "#f0a020", "#ffd060", "#fff2b0")
BRONZE = ramp("#1e1208", "#3a240e", "#5a3a16", "#7c5420", "#9e6e2c")
SCARAB = ramp("#061210", "#0c221c", "#14362c", "#1e4c3c", "#2c6450", "#447c62")
RED = ramp("#2a0806", "#46100a", "#661a10", "#862818")


def shaders():
    return {
        "linen": X.surf(LINEN, 0.5, 1.0, 0.24, 0.0, stripe=2, holes=True),
        "wrap": X.surf(LINEN, 0.54, 1.0, 0.2, 0.0, stripe=2),
        "gold": X.surf(GOLD, 0.56, 1.4, 0.12, 0.22),
        "lapis": X.surf(LAPIS, 0.5, 1.2, 0.16, 0.1),
        "turq": X.surf(TURQ, 0.5, 1.2, 0.16, 0.1),
        "sandstone": X.surf(SANDST, 0.5, 1.2, 0.3, 0.0, crust=(GOLD, 0.04)),
        "basalt": X.surf(BASALT, 0.52, 1.5, 0.14, 0.2),
        "skin": X.wrinkled(SKIN, 1.2),
        "glow": X.glow(SUN),
        "eye": X.glow(SUN, 0.82, 0.16),
        "bronze": X.surf(BRONZE, 0.52, 1.3, 0.16, 0.18, rust=(TURQ, 0.2, 0.4)),
        "scarab": X.surf(SCARAB, 0.5, 1.6, 0.14, 0.24),
        "red": X.surf(RED, 0.5, 1.0, 0.2, 0.0),
        "dark": X.dark(BASALT),
    }


def bands(k, part, cx, cz, y0, y1, w, d, mat="wrap", step=1.6, tilt=0.4):
    """mummy wrappings: slanted bands round a limb, a dark gap between each"""
    y = y0
    i = 0
    while y < y1:
        k.box(part, C(cx, y, cz, w + 0.3, step * 0.75, d + 0.3), mat, tag="wrap",
              rots=(("z", tilt * 12 * (1 if i % 2 else -1)),), pivot=(cx, y, cz))
        y += step
        i += 1


def nemes(k, part, cx, y, cz, s=1.0):
    """the striped royal headcloth: a hood over the head, lappets down to the chest, a tail behind"""
    for i in range(5):
        k.box(part, C(cx, y + i * 1.2 * s, cz - 0.4 * s, (8.4 - i * 0.6) * s, 1.2 * s, (8.2 - i * 0.5) * s),
              "gold" if i % 2 else "lapis", tag="nemes")
    for sx in (-1, 1):
        for i in range(5):
            k.box(part, C(cx + sx * 4.2 * s, y - 6 * s + i * 1.4 * s, cz + 1.6 * s, 2.2 * s, 1.4 * s, 2.4 * s),
                  "gold" if i % 2 else "lapis", tag="lappet")
    k.box(part, C(cx, y - 4 * s, cz - 4.6 * s, 3.2 * s, 6 * s, 1.0 * s), "lapis", tag="nemes_tail")


def uraeus(k, part, x, y, z, s=1.0):
    """the cobra on the brow, hood spread"""
    k.box(part, C(x, y, z, 1.8 * s, 2.6 * s, 0.8 * s), "gold", tag="uraeus")
    k.box(part, C(x, y + 1.6 * s, z + 0.3 * s, 1.0 * s, 1.4 * s, 1.0 * s), "gold", tag="uraeus")
    k.box(part, C(x, y + 1.0 * s, z + 0.5 * s, 0.6 * s, 0.6 * s, 0.4), "red", tag="uraeus_eye")


# ================================================================ the Sun-King (boss)

def sun_king():
    """He had the priests swear the sun would never set on him, and when the desert came over his tomb he made them
    keep the oath: he is the sun down here. A mummy six blocks high, his linen gone brown and split over a body
    like dried wood, armoured in beaten gold - the collar of lapis and gold across his shoulders, a scarab pectoral
    burning on his chest, gold on his shins and forearms. His face is the gold death mask, eyes of fire, the cobra
    on his brow, the striped nemes over it. Behind his head stands the sun itself: a disc of gold three blocks wide
    with rays like blades, and it burns. He holds the crook and the flail crossed, and the flail's tails are chains
    with sun-weights on them."""
    k = X.Kit("sun_king")
    hips = k.part("hips", (0, 38, 0))
    k.stack(hips, 0, 0, [(30, 18, 12), (38, 19, 12.6)], "wrap", "hips")
    k.box(hips, C(0, 36, 0, 21, 3.4, 14), "gold", tag="belt")
    # the royal kilt: pleated, gold edged, the apron of lapis and gold down the front
    for i in range(9):
        a = math.radians(-120 + i * 30)
        k.box(hips, C(math.sin(a) * 9.4, 20, math.cos(a) * 6.4, 5.4, 16, 1.0), "linen", tag="kilt",
              rots=(("y", -math.degrees(a)),), pivot=(math.sin(a) * 9.4, 28, math.cos(a) * 6.4))
    k.box(hips, C(0, 16, 7.6, 7.0, 20, 1.2), "gold", tag="apron")
    for y in (19, 23, 27, 31):
        k.box(hips, C(0, y, 8.3, 5.4, 1.6, 0.6), "lapis", tag="apron_band")
    k.box(hips, C(0, 16, 8.3, 4.0, 3.0, 0.6), "turq", tag="apron_tip")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 5.4
        th = k.part("thigh_" + nm, (x, 34, 0), (("x", -6), ("z", side * 5)), "hips")
        sh = k.part("shin_" + nm, (x, 18, 0), (("x", 8),), th)
        ft = k.part("foot_" + nm, (x, 4, 0), (("x", -2),), sh)
        k.stack(th, x, 0, [(18, 8.4, 8.6), (26, 9.4, 9.6), (34, 9.0, 9.2)], "wrap", "thigh")
        bands(k, th, x, 0, 18, 34, 8.8, 9.0)
        k.stack(sh, x, 0, [(4, 7.6, 8), (12, 8.4, 8.6), (18, 8.0, 8.2)], "wrap", "shin")
        k.box(sh, C(x, 6, 0.4, 9.2, 10, 9.0), "gold", tag="greave")
        for y in (8, 12):
            k.box(sh, C(x, y, 4.9, 8.0, 1.0, 0.4), "lapis", tag="greave_band")
        k.box(ft, C(x, 0, 2.6, 8.6, 4, 13), "wrap", tag="foot")
        k.box(ft, C(x, 0, 2.6, 9.2, 1.2, 13.6), "gold", tag="sandal")
    # ---------------------------------------------------------------- torso: dried, wrapped, the collar and the pectoral
    to = k.part("torso", (0, 39, 0), (("x", 4),), "hips")
    k.stack(to, 0, 0, [(38, 20, 13), (46, 25, 14), (54, 32, 15), (60, 32, 14)], "wrap", "torso")
    bands(k, to, 0, 0, 38, 50, 20, 13, step=1.8)
    for (x, y) in ((-6, 44), (5, 47), (-3, 51)):            # where the linen has split, the dried body under it
        k.box(to, C(x, y, 6.9, 4.0, 2.6, 0.6), "skin", tag="split")
    for r in range(4):                                       # the broad collar: rows of gold and lapis beads
        R = 9 + r * 2.4
        for a in range(-80, 81, 16):
            ra = math.radians(a)
            k.box(to, C(math.sin(ra) * R, 60 - R * 0.55 * math.cos(ra) * 0.5 - r * 0.6, math.cos(ra) * 6.8 + 0.4,
                        2.6, 1.6, 1.4), "gold" if (r + a // 16) % 2 else "lapis", tag="collar")
    k.box(to, C(0, 47, 7.0, 8.0, 7.0, 1.4), "gold", tag="pectoral")
    k.blob(to, (0, 50.6, 8.0), (2.6, 2.4, 1.4), "turq", "scarab_pectoral", step=0.8)
    k.box(to, C(0, 53.4, 8.0, 3.0, 3.0, 1.0), "glow", group="glow", tag="pectoral_sun")
    for sx in (-1, 1):
        k.limb(to, (sx * 1.6, 50.6, 8.4), (sx * 4.6, 52.6, 8.2), 1.6, "gold", "pectoral_wing", d=0.6)
    # trailing bandages from the back and arms
    for (x, L) in ((-8, 30), (-2, 36), (5, 28), (10, 22)):
        k.limb(to, (x, 56, -6.6), (x * 1.2, 56 - L, -9), 2.4, "linen", "trailing_wrap", d=0.4)
    # the sun disc behind his head: a gold ring with blade-rays, and the fire in it
    sd = k.part("sun_disc", (0, 72, -10), (("x", -6),), to, bone=False)
    k.blob(sd, (0, 72, -11.4), (14, 14, 1.4), "glow", "sun_face", step=1.0)
    k.ring(sd, 0, 72, -10.4, 15, 2.6, "gold", "sun_ring", n=24)
    k.ring(sd, 0, 72, -10.0, 9.4, 1.4, "gold", "sun_ring", n=18)
    for i in range(16):
        a = math.radians(i * 22.5)
        L = 12 if i % 2 else 8
        k.shard(sd, (math.cos(a) * 15.6, 72 + math.sin(a) * 15.6, -10.4), (math.cos(a), math.sin(a), 0), L, 3.2 if i % 2 else 2.2,
                mat="gold", tag="sun_ray")
    k.limb(sd, (0, 58, -8), (0, 66, -10), 2.0, "gold", "disc_mount")
    # ---------------------------------------------------------------- the head: the gold death mask, the nemes, the cobra
    hd = k.part("head", (0, 60, 1), (), "torso")
    k.box(hd, C(0, 60.4, 1.0, 8.4, 10.4, 8.4), "gold", tag="mask")
    k.box(hd, C(0, 66.2, 5.3, 7.4, 1.0, 0.6), "lapis", tag="brow")
    for sx in (-2.0, 2.0):
        k.box(hd, C(sx, 64.2, 5.25, 2.6, 1.4, 0.4), "dark", tag="eye_socket")
        k.box(hd, C(sx, 64.4, 5.45, 2.0, 1.0, 0.3), "eye", group="glow", tag="eye")
        k.box(hd, C(sx + 1.6 * (1 if sx > 0 else -1), 63.6, 5.25, 1.6, 0.5, 0.4), "lapis", tag="kohl")
    k.box(hd, C(0, 62.0, 5.6, 1.8, 2.8, 1.4), "gold", tag="nose")
    k.box(hd, C(0, 61.4, 5.25, 3.0, 0.6, 0.4), "dark", tag="mouth")
    k.box(hd, C(0, 54.6, 4.8, 2.0, 6.0, 1.6), "lapis", tag="beard")
    for y in (55.6, 57.4, 59.2):
        k.box(hd, C(0, y, 5.7, 2.2, 0.6, 0.4), "gold", tag="beard_band")
    nemes(k, hd, 0, 66.6, 1.0, s=1.25)
    uraeus(k, hd, 0, 67.8, 6.4, s=1.3)
    # ---------------------------------------------------------------- arms: crossed, the crook and the flail
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 15
        up = k.part("arm_" + nm, (x, 58, 0), (("x", -40), ("z", side * 8)), "torso")
        fo = k.part("fore_" + nm, (x, 44, 0), (("x", -60), ("y", side * 30)), up)
        hn = k.part("hand_" + nm, (x, 30, 0), (), fo)
        k.blob(up, (x, 57, 0), (6.0, 4.6, 6.4), "gold", "pauldron")
        k.stack(up, x, 0, [(44, 7.0, 7.2), (52, 7.8, 8.0), (58, 8.4, 8.6)], "wrap", "upper_arm")
        bands(k, up, x, 0, 44, 54, 7.4, 7.6)
        k.stack(fo, x, 0, [(31, 6.6, 6.8), (44, 7.0, 7.2)], "wrap", "forearm")
        k.box(fo, C(x, 32, 0, 8.4, 8.0, 8.4), "gold", tag="bracer")
        for y in (34, 37):
            k.box(fo, C(x, y, 0, 8.8, 1.0, 8.8), "lapis", tag="bracer_band")
        k.box(hn, C(x, 25, 0.6, 6.4, 6.0, 6.4), "wrap", tag="hand")
    # the crook in his left: a gold and lapis staff, the hook at the top
    ck = k.part("crook", (15, 27, 1), (("x", 95),), k.parts["hand_l"])
    k.limb(ck, (15, 6, 1), (15, 54, 1), 3.6, "gold", "crook_staff", d=3.6)
    for y in range(10, 52, 6):
        k.box(ck, C(15, y, 1, 4.4, 2.4, 4.4), "lapis", tag="crook_band")
    pts = [(15, 54, 1), (15, 61, 2.6), (15, 63, 7.4), (15, 60, 11.6), (15, 55, 12.4)]
    for (a, b) in zip(pts, pts[1:]):
        k.limb(ck, a, b, 3.6, "gold", "crook_hook", d=3.6)
    # the flail in his right: a short handle, three chains, sun-weights burning on them
    fl = k.part("flail", (-15, 27, 1), (("x", 50),), k.parts["hand_r"])
    k.limb(fl, (-15, 20, 1), (-15, 40, 1), 3.4, "gold", "flail_handle", d=3.4)
    for y in (24, 30, 36):
        k.box(fl, C(-15, y, 1, 4.2, 2.0, 4.2), "lapis", tag="flail_band")
    for i, dx in enumerate((-4, 0, 4)):
        end = (-15 + dx, 22 + i % 2 * 3, 12 + abs(dx))
        k.chain(fl, (-15, 40, 1), end, 5, mat="gold", w=2.2)
        k.blob(fl, (end[0], end[1] - 3.4, end[2]), (3.8, 3.8, 3.8), "glow", "sun_weight", step=0.9)
        for a in range(0, 360, 60):
            r = math.radians(a)
            k.shard(fl, (end[0] + math.cos(r) * 3.6, end[1] - 3.4 + math.sin(r) * 3.6, end[2]), (math.cos(r), math.sin(r), 0),
                    3.6, 1.8, mat="gold", tag="weight_spike")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Sun Guardian (elite, the key)

def sun_guardian():
    """The last of the king's guard, buried at the door alive so he would keep it forever, and he has. A mummy in a
    coat of gold scales, a falcon helm with the wings swept back, a broad sun-disc shield with a burning boss and a
    long bronze spear. The ankh that opens the burial chamber hangs on his chest."""
    k = X.Kit("sun_guardian")
    hips = k.part("hips", (0, 21, 0))
    k.stack(hips, 0, 0, [(15, 12.4, 8.0), (21, 12.4, 8.2)], "wrap", "hips")
    for i, x in enumerate((-4.4, -1.5, 1.5, 4.4)):
        k.box(hips, C(x, 11, 4.4, 2.8, 9, 0.8), "gold" if i % 2 else "lapis", tag="kilt_strip")
    k.box(hips, C(0, 20.4, 0, 13, 1.8, 8.8), "gold", tag="belt")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 3.2
        th = k.part("thigh_" + nm, (x, 20, 0), (("x", -6), ("z", side * 5)), "hips")
        sh = k.part("shin_" + nm, (x, 10.6, 0), (("x", 10),), th)
        ft = k.part("foot_" + nm, (x, 2.4, 0), (("x", -4),), sh)
        k.box(th, C(x, 10.8, 0, 4.8, 9.4, 5.2), "wrap", tag="thigh")
        bands(k, th, x, 0, 11, 20, 4.8, 5.2, step=1.4)
        k.box(sh, C(x, 2.4, 0, 4.8, 8.4, 5.2), "gold", tag="greave")
        k.box(sh, C(x, 6.4, 2.7, 3.6, 0.8, 0.4), "lapis", tag="greave_band")
        k.box(ft, C(x, 0, 1.4, 5.0, 2.6, 8.0), "wrap", tag="foot")
    # ---------------------------------------------------------------- torso: a coat of gold scales, the ankh
    to = k.part("torso", (0, 21, 0), (("x", 4),), "hips")
    k.stack(to, 0, 0, [(21, 12.4, 8.0), (27, 15.0, 9.0), (32, 17.0, 9.6), (35.6, 15.4, 8.6)], "wrap", "torso")
    for r in range(6):                       # overlapping rows of scales, front and back
        y = 22.4 + r * 2.2
        n = 6 + r % 2
        for c in range(n):
            x = -7 + (c + (0.5 if r % 2 else 0)) * 14 / n
            for z in (4.6, -4.6):
                k.box(to, C(x, y, z + (0.2 if z > 0 else -0.2), 2.4, 2.6, 0.7), "gold", tag="scale")
    k.limb(to, (-3.4, 35.4, 4.8), (0, 30.6, 5.6), 0.5, "linen", "ankh_cord")
    k.limb(to, (3.4, 35.4, 4.8), (0, 30.6, 5.6), 0.5, "linen", "ankh_cord")
    k.box(to, C(0, 25.4, 5.8, 1.2, 4.4, 0.8), "glow", group="glow", tag="ankh")
    k.box(to, C(0, 28.6, 5.8, 3.6, 1.0, 0.8), "glow", group="glow", tag="ankh")
    k.ring(to, 0, 31.0, 5.8, 1.4, 0.8, "glow", "ankh_loop", n=8)
    for side in (1, -1):
        k.blob(to, (side * 9.4, 34.6, 0), (4.4, 2.8, 4.8), "gold", "pauldron")
        for i in range(3):
            k.box(to, C(side * (10.4 + i * 0.4), 32.4 - i * 1.8, 0, 6.0, 1.6, 9.0), "lapis" if i % 2 else "gold", tag="lame")
    # ---------------------------------------------------------------- the falcon helm
    hd = k.part("head", (0, 35.6, 0.4), (("x", -4),), "torso")
    k.box(hd, C(0, 35.4, 0.4, 6.8, 7.6, 7.0), "gold", tag="helm")
    k.box(hd, C(0, 38.6, 4.0, 5.6, 2.2, 1.2), "gold", tag="brow")
    k.shard(hd, (0, 39.6, 4.4), (0, -0.7, 1), 5.0, 2.6, mat="gold", tag="beak")
    k.box(hd, C(0, 37.6, 3.95, 5.2, 1.0, 0.4), "dark", tag="visor")
    for sx in (-1.4, 1.4):
        k.box(hd, C(sx, 37.7, 4.05, 1.6, 0.6, 0.3), "eye", group="glow", tag="eye")
        k.box(hd, C(sx * 1.6, 36.6, 4.0, 0.6, 1.4, 0.3), "lapis", tag="falcon_mark")
    for sx in (-1, 1):                       # the wings swept back off the helm
        for i in range(4):
            k.shard(hd, (sx * 3.4, 40 - i * 1.4, 0.4 - i * 0.6), (sx * 0.5, 0.3 - i * 0.1, -1), 6.0 - i * 0.6, 1.6,
                    mat="gold" if i % 2 == 0 else "lapis", tag="helm_wing")
    k.blob(hd, (0, 44.4, -0.6), (2.4, 2.4, 0.6), "glow", "helm_sun", step=0.6)
    # ---------------------------------------------------------------- arms: the sun shield, the spear
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 9.4
        up = k.part("arm_" + nm, (x, 33, 0), (("x", -40 if side > 0 else -30), ("z", side * 10)), "torso")
        fo = k.part("fore_" + nm, (x, 24, 0), (("x", -50 if side > 0 else -60),), up)
        hn = k.part("hand_" + nm, (x, 15.6, 0), (), fo)
        k.box(up, C(x, 24.8, 0, 4.4, 8.6, 4.6), "wrap", tag="arm")
        bands(k, up, x, 0, 25, 33, 4.4, 4.6, step=1.4)
        k.box(fo, C(x, 16.4, 0, 4.8, 8.0, 5.0), "gold", tag="bracer")
        k.box(hn, C(x, 12.6, 0.4, 4.2, 3.8, 4.2), "wrap", tag="hand")
    sh = k.part("shield", (13, 16, 2), (("y", 10),), k.parts["hand_l"])
    k.blob(sh, (13.6, 18, 2), (1.0, 10.4, 10.4), "gold", "shield", step=1.0)
    k.ring(sh, 14.4, 18, 2, 10.0, 1.2, "lapis", "shield_rim", n=20, axis="x")
    k.ring(sh, 14.4, 18, 2, 6.0, 0.8, "gold", "shield_ring", n=16, axis="x")
    k.blob(sh, (14.8, 18, 2), (1.2, 3.4, 3.4), "glow", "shield_sun", step=0.8)
    for i in range(12):
        a = math.radians(i * 30)
        k.box(sh, C(14.7, 18 + math.sin(a) * 5.0 - 0.5, 2 + math.cos(a) * 5.0, 0.4, 1.0, 1.0), "glow", group="glow", tag="shield_ray")
    sp = k.part("spear", (-9.4, 13.6, 0.6), (("x", 80),), k.parts["hand_r"])
    k.limb(sp, (-9.4, -12, 0.6), (-9.4, 38, 0.6), 1.2, "bronze", "shaft")
    for y in (0, 20):
        k.box(sp, C(-9.4, y, 0.6, 1.8, 1.4, 1.8), "gold", tag="shaft_band")
    k.box(sp, C(-9.4, 38, 0.6, 1.0, 9.0, 3.6), "bronze", tag="spear_head")
    k.shard(sp, (-9.4, 47, 0.6), (0, 1, 0), 4.0, 3.6, mat="bronze", tag="spear_head")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Sand Colossus (brute)

def sand_colossus():
    """The statues that lined the king's causeway stood guard for a thousand years, and the sand got into them. This
    one walks: a sandstone guard twice a man's height, the nemes carved on its head, its face worn half away; great
    cracks across its chest and arms, and out of them, all the time, pours sand, lit gold from inside where the
    sun-king's oath is. Lapis inlay still in its collar. It carries the top of an obelisk for a club."""
    k = X.Kit("sand_colossus")
    hips = k.part("hips", (0, 24, 0))
    k.stack(hips, 0, 0, [(17, 16, 11), (24, 17, 11.6)], "sandstone", "hips")
    k.box(hips, C(0, 11, 5.8, 7, 12, 1.4), "sandstone", tag="apron")
    k.box(hips, C(0, 22, 0, 18, 2.4, 12.4), "lapis", tag="belt")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 5.2
        th = k.part("thigh_" + nm, (x, 21, 0), (("x", -6), ("z", side * 6)), "hips")
        sh = k.part("shin_" + nm, (x, 11.6, 0), (("x", 10),), th)
        ft = k.part("foot_" + nm, (x, 3, 0), (("x", -4),), sh)
        k.stack(th, x, 0, [(11.6, 7.6, 7.8), (16, 8.6, 8.8), (21, 8.2, 8.4)], "sandstone", "thigh")
        k.stack(sh, x, 0, [(3, 7.4, 7.6), (11.6, 8.0, 8.2)], "sandstone", "shin")
        k.box(sh, C(x + side * 2, 7, 4.2, 0.8, 4.0, 0.4), "glow", group="glow", tag="crack")
        k.box(ft, C(x, 0, 1.8, 8.6, 3.2, 12), "sandstone", tag="foot")
    # ---------------------------------------------------------------- torso: a block of carved stone, cracked, pouring sand
    to = k.part("torso", (0, 24, 0), (("x", 8),), "hips")
    k.stack(to, 0, 0, [(24, 17, 11.6), (31, 22, 13), (38, 27, 14), (42, 26, 13)], "sandstone", "torso")
    for r in range(3):
        for a in range(-60, 61, 20):
            ra = math.radians(a)
            k.box(to, C(math.sin(ra) * (8 + r * 2.2), 41 - r * 1.8, math.cos(ra) * 6.4 + 0.4, 2.6, 1.6, 1.4),
                  "lapis" if (r + a // 20) % 2 else "gold", tag="collar")
    for (a, b) in (((-6, 38, 7.0), (-2, 31, 7.0)), ((-2, 31, 7.0), (-4, 26, 7.0)), ((5, 36, 7.0), (8, 29, 6.6)), ((-2, 31, 7.0), (4, 28, 7.0))):
        k.limb(to, a, b, 1.2, "glow", "crack", group="glow", d=0.6)
    for (x, z, L) in ((-3, 7.4, 16), (4, 7.2, 12), (8, 6.6, 10)):          # the sand pouring out of it
        k.limb(to, (x, 30, z), (x + 0.4, 30 - L, z + 1.6), 1.6, "sandstone", "sand_fall", d=1.0)
    k.box(to, C(-9, 34, 2, 5.0, 5.0, 4.0), "dark", tag="broken_chunk")
    # ---------------------------------------------------------------- the head: nemes carved in stone, the face worn half away
    hd = k.part("head", (0, 42, 1), (("x", -6),), "torso")
    k.box(hd, C(0, 42, 1, 8.6, 9.6, 8.6), "sandstone", tag="head")
    nemes(k, hd, 0, 48.6, 1.0, s=1.1)
    for i in range(5):           # the nemes is stone too: overpaint the gold and lapis stripes with worn paint
        pass
    k.box(hd, C(-2.0, 46.6, 5.35, 2.6, 1.2, 0.4), "dark", tag="eye_socket")
    k.box(hd, C(-2.0, 46.8, 5.55, 1.8, 0.8, 0.3), "eye", group="glow", tag="eye")
    k.box(hd, C(2.6, 44.0, 4.6, 4.0, 7.0, 1.4), "dark", tag="worn_face")
    k.box(hd, C(2.4, 46.4, 5.0, 1.2, 1.2, 0.6), "eye", group="glow", tag="eye")
    k.box(hd, C(-1.0, 44.4, 5.6, 1.6, 2.2, 1.0), "sandstone", tag="nose")
    k.box(hd, C(0, 38.6, 5.0, 2.0, 4.0, 1.4), "sandstone", tag="beard")
    # ---------------------------------------------------------------- arms: great stone arms, cracked
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 15
        up = k.part("arm_" + nm, (x, 40, 0), (("x", -20 if side > 0 else -80), ("z", side * 10)), "torso")
        fo = k.part("fore_" + nm, (x, 28, 0), (("x", -30 if side > 0 else -40),), up)
        hn = k.part("hand_" + nm, (x, 17, 0), (), fo)
        k.blob(up, (x, 39, 0), (6.0, 4.6, 6.2), "sandstone", "shoulder")
        k.stack(up, x, 0, [(28, 7.0, 7.2), (36, 8.0, 8.2)], "sandstone", "upper_arm")
        k.stack(fo, x, 0, [(17, 7.4, 7.6), (28, 7.8, 8.0)], "sandstone", "forearm")
        k.box(fo, C(x, 20, 0, 8.6, 2.4, 8.8), "lapis", tag="bracelet")
        k.box(up, C(x + side * 3.8, 32, 1, 0.6, 5.0, 1.0), "glow", group="glow", tag="crack")
        k.box(hn, C(x, 11, 0.6, 7.4, 6.4, 7.4), "sandstone", tag="fist")
    # the obelisk club: its tip broken off the causeway, carved, gold-capped
    ob = k.part("obelisk", (-15, 13, 1), (("x", 60),), k.parts["hand_r"])
    k.stack(ob, -15, 1, [(6, 5.4, 5.4), (30, 6.6, 6.6), (40, 5.6, 5.6)], "sandstone", "obelisk")
    k.shard(ob, (-15, 40, 1), (0, 1, 0), 6, 5.6, mat="gold", tag="pyramidion")
    for y in (14, 20, 26, 32):
        k.box(ob, C(-15, y, 4.3, 2.4, 2.4, 0.4), "dark", tag="glyph")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Embalmer (caster)

def embalmer():
    """The embalmers wrapped the king and stayed with him to keep the rites, and keep them still. This one wears the
    ibis mask of the god of the rites, the long curved beak down to its chest; under it a bald, painted, dried
    face. Its arms are wrapped to the shoulder from the work; on its belt hang the hooks and knives and the jars,
    and it swings a censer of burning natron that dries whatever it touches."""
    k = X.Kit("embalmer")
    hips = k.part("hips", (0, 19, 0))
    k.stack(hips, 0, 0, [(2, 11, 8), (12, 10, 7.2), (19, 9.2, 6.6)], "linen", "robe")
    k.box(hips, C(0, 18.6, 0, 10, 1.6, 7.4), "gold", tag="belt")
    for (x, y, L) in ((-4.6, 17, 6), (-3.0, 17, 8), (3.4, 17, 5)):          # hooks and knives
        k.limb(hips, (x, y, 3.6), (x, y - L, 3.8), 0.5, "bronze", "tool")
        k.limb(hips, (x, y - L, 3.8), (x + 0.8, y - L + 1.0, 3.8), 0.5, "bronze", "tool_hook")
    for (x, z) in ((5.4, 1.6), (4.4, -2.6)):
        k.box(hips, C(x, 12.4, z, 2.0, 3.6, 2.0), "sandstone", tag="jar")
        k.box(hips, C(x, 16.0, z, 1.6, 1.2, 1.6), "gold", tag="jar_lid")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.4
        th = k.part("thigh_" + nm, (x, 19, 0), (("x", -4),), "hips")
        sh = k.part("shin_" + nm, (x, 10, 0), (("x", 6),), th)
        ft = k.part("foot_" + nm, (x, 2, 0), (), sh)
        k.box(ft, C(x, 0, 1.4, 3.0, 2.0, 5.2), "wrap", tag="foot")
    # ---------------------------------------------------------------- torso: a priest's leopard-pelt sash over the linen
    to = k.part("torso", (0, 19, 0), (("x", 12),), "hips")
    k.stack(to, 0, 0, [(19, 9.2, 6.6), (25, 11.0, 7.0), (31, 12.4, 7.0)], "linen", "robe")
    k.limb(to, (5.4, 31, 3.4), (-4.0, 19.6, 3.8), 3.4, "gold", "sash", d=0.6)
    for (x, y) in ((3.4, 28.4), (1.0, 25.4), (-1.6, 22.6)):
        k.box(to, C(x, y, 4.0, 1.0, 1.0, 0.4), "dark", tag="sash_spot")
    for r in range(2):
        for a in range(-60, 61, 30):
            ra = math.radians(a)
            k.box(to, C(math.sin(ra) * (4.4 + r * 1.6), 30.4 - r * 1.2, math.cos(ra) * 3.4 + 0.2, 1.6, 1.2, 1.0),
                  "lapis" if (r + a // 30) % 2 else "turq", tag="collar")
    # ---------------------------------------------------------------- the head: the ibis mask, the long beak
    hd = k.part("head", (0, 31, 0.6), (("x", -6),), "torso")
    k.box(hd, C(0, 31.0, 0.6, 5.4, 6.0, 5.6), "skin", tag="face")
    k.box(hd, C(0, 35.2, 0.6, 6.0, 3.4, 6.2), "basalt", tag="ibis_head")
    k.box(hd, C(0, 34.4, 3.4, 3.6, 2.4, 2.6), "basalt", tag="ibis_face")
    pts = [(0, 35.4, 4.6), (0, 34.0, 7.4), (0, 31.2, 9.6), (0, 27.6, 10.4), (0, 24.6, 10.0)]
    for (a, b), w in zip(zip(pts, pts[1:]), (1.8, 1.5, 1.2, 0.8)):
        k.limb(hd, a, b, w, "basalt", "ibis_beak")
    for sx in (-1.6, 1.6):
        k.box(hd, C(sx, 35.6, 3.4, 1.2, 1.0, 0.4), "eye", group="glow", tag="eye")
        k.box(hd, C(sx * 1.4, 33.0, 2.0, 2.4, 6.0, 2.2), "lapis", tag="ibis_lappet")
    # ---------------------------------------------------------------- arms: wrapped to the shoulder, the censer
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 7.0
        up = k.part("arm_" + nm, (x, 29.6, 0), (("x", -60 if side > 0 else -40), ("z", side * 10)), "torso")
        fo = k.part("fore_" + nm, (x, 21.6, 0), (("x", -50 if side > 0 else -40),), up)
        hn = k.part("hand_" + nm, (x, 13.8, 0), (), fo)
        k.box(up, C(x, 21.4, 0, 3.2, 8.4, 3.4), "wrap", tag="arm")
        bands(k, up, x, 0, 22, 30, 3.2, 3.4, step=1.2)
        k.box(fo, C(x, 14.0, 0, 2.8, 7.6, 3.0), "wrap", tag="forearm")
        bands(k, fo, x, 0, 14, 21, 2.8, 3.0, step=1.2)
        k.box(hn, C(x, 11.4, 0.4, 2.6, 2.6, 2.6), "skin", tag="hand")
        if side > 0:
            k.limb(hn, (x, 11.4, 1.4), (x, 7.0, 4.0), 0.6, "bronze", "brain_hook")
            k.limb(hn, (x, 7.0, 4.0), (x, 8.0, 5.4), 0.6, "bronze", "brain_hook")
    cn = k.part("censer", (-7, 11, 1), (("x", 20),), k.parts["hand_r"])
    k.chain(cn, (-7, 11, 1), (-7, 3, 2), 4, mat="gold", w=0.8)
    k.blob(cn, (-7, 0.8, 2), (2.4, 2.2, 2.4), "gold", "censer", step=0.7)
    k.box(cn, C(-7, 0.6, 2, 3.4, 1.0, 3.4), "glow", group="glow", tag="censer_fire")
    for (x, z, L) in ((-0.6, 0.4, 5), (0.8, -0.4, 4), (0, 0, 6)):
        k.limb(cn, (-7 + x, 3, 2 + z), (-7 + x * 2, 3 + L, 2 + z * 3), 1.0, "linen", "natron_smoke", d=1.0)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Jackal Runner (skirmisher)

def jackal_runner():
    """The tomb's hounds, the jackal-god's own: tall, lean, black as basalt, a jackal's head with the long muzzle and
    the high ears, gold at the collar and wrists and in the eyes. Its legs bend like a dog's and it runs low, a
    khopesh - the sickle-sword - in each hand."""
    k = X.Kit("jackal_runner")
    hips = k.part("hips", (0, 19, 0))
    k.box(hips, C(0, 16.6, 0, 7.6, 3.6, 5.0), "basalt", tag="hips")
    k.box(hips, C(0, 12, 2.4, 7.0, 7, 1.0), "linen", tag="kilt")
    k.box(hips, C(0, 12, 3.0, 2.6, 7, 0.6), "gold", tag="kilt_apron")
    k.box(hips, C(0, 18.8, 0, 8.2, 1.4, 5.6), "gold", tag="belt")
    tail = [(0, 17, -2.6), (0, 14, -6), (0, 9, -8), (0, 5, -8.6)]
    for (a, b), w in zip(zip(tail, tail[1:]), (2.0, 1.6, 1.2)):
        k.limb(hips, a, b, w, "basalt", "tail")
    for side, nm in ((1, "l"), (-1, "r")):       # dog's legs: thigh forward, shin back, a long foot
        x = side * 2.4
        th = k.part("thigh_" + nm, (x, 19, 0), (("x", -30), ("z", side * 6)), "hips")
        sh = k.part("shin_" + nm, (x, 12, 0), (("x", 60),), th)
        ft = k.part("foot_" + nm, (x, 5, 0), (("x", -34),), sh)
        k.stack(th, x, 0, [(12, 3.2, 3.6), (16, 4.0, 4.4), (19, 3.6, 4.0)], "basalt", "thigh")
        k.box(sh, C(x, 5, -0.4, 2.4, 7.0, 2.6), "basalt", tag="shin")
        k.box(ft, C(x, 0, 0.6, 2.4, 5.0, 2.4), "basalt", tag="foot")
        k.box(ft, C(x, 0, 1.6, 3.0, 1.4, 3.6), "basalt", tag="foot")
        for t in (-0.8, 0.8):
            k.shard(ft, (x + t, 0.4, 3.2), (0, -0.3, 1), 1.4, 0.6, mat="gold", tag="foot")
    # ---------------------------------------------------------------- torso: lean, pitched forward to run
    to = k.part("torso", (0, 19, 0), (("x", 30),), "hips")
    k.stack(to, 0, 0, [(19, 7.6, 5.0), (24, 9.0, 5.8), (29, 10.8, 6.0)], "basalt", "torso")
    for r in range(2):
        for a in range(-60, 61, 30):
            ra = math.radians(a)
            k.box(to, C(math.sin(ra) * (4.4 + r * 1.6), 29.4 - r * 1.2, math.cos(ra) * 3.2 + 0.2, 1.6, 1.2, 1.0),
                  "gold" if (r + a // 30) % 2 else "lapis", tag="collar")
    # ---------------------------------------------------------------- the head: the jackal, muzzle and ears
    hd = k.part("head", (0, 29.6, 0.8), (("x", -26),), "torso")
    k.box(hd, C(0, 30.4, 0.6, 4.6, 4.8, 5.0), "basalt", tag="head")
    k.box(hd, C(0, 30.2, 4.6, 2.6, 2.4, 4.4), "basalt", tag="muzzle")
    k.box(hd, C(0, 30.0, 7.6, 2.0, 1.8, 2.0), "basalt", tag="muzzle")
    k.box(hd, C(0, 31.6, 8.4, 1.2, 0.8, 0.6), "dark", tag="nose")
    k.box(hd, C(0, 29.8, 6.4, 2.4, 0.4, 4.0), "dark", tag="jaw_line")
    for t in (-0.8, 0.8):
        k.shard(hd, (t, 30.0, 8.2), (0, -1, 0.1), 1.0, 0.4, mat="gold", tag="tooth")
    for sx in (-1.4, 1.4):
        k.box(hd, C(sx, 33.0, 3.15, 1.0, 0.6, 0.3), "eye", group="glow", tag="eye")
        k.shard(hd, (sx * 1.2, 34.6, 0.0), (sx * 0.15, 1, -0.2), 5.4, 1.8, mat="basalt", tag="ear")
        k.box(hd, C(sx * 1.4, 36.4, 0.4, 0.8, 2.4, 0.3), "gold", tag="ear_inner")
    # ---------------------------------------------------------------- arms and the two khopeshes
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 5.8
        up = k.part("arm_" + nm, (x, 27.4, 0), (("x", -40 if side > 0 else -70), ("z", side * 18)), "torso")
        fo = k.part("fore_" + nm, (x, 20.6, 0), (("x", -60 if side > 0 else -20),), up)
        hn = k.part("hand_" + nm, (x, 13.6, 0), (), fo)
        k.box(up, C(x, 20.8, 0, 2.8, 7.0, 3.0), "basalt", tag="arm")
        k.box(fo, C(x, 13.8, 0, 2.6, 7.2, 2.8), "basalt", tag="forearm")
        k.box(fo, C(x, 15.4, 0, 3.2, 2.0, 3.4), "gold", tag="bracer")
        k.box(hn, C(x, 11.2, 0.3, 2.4, 2.6, 2.4), "basalt", tag="hand")
        kh = k.part("khopesh_" + nm, (x, 12.2, 0.4), (("x", 80),), hn)
        k.box(kh, C(x, 9.6, 0.4, 0.9, 4.4, 0.9), "gold", tag="grip")
        k.box(kh, C(x, 13.8, 0.4, 0.6, 6.0, 1.4), "bronze", tag="blade")
        pts = [(x, 19.6, 0.6), (x, 22.6, 2.0), (x, 23.4, 4.8), (x, 21.6, 7.0), (x, 18.8, 7.4)]
        for (a, b), w in zip(zip(pts, pts[1:]), (2.4, 2.2, 1.8, 1.2)):
            k.limb(kh, a, b, w, "bronze", "khopesh_hook", d=0.5)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Tomb Scarab (swarm, on the spider)

def tomb_scarab():
    """The beetles that rolled the sun across the sky in the king's paintings, grown in his dark to the size of a
    dog: green-black and gold-shot shells, a sun disc held up between two horns on its head, jagged mandibles, and
    its wing cases split open on wings of light. Six legs, toothed, that dig."""
    k = X.Kit("tomb_scarab")
    body = k.part("body", (0, 6, 0))
    k.blob(body, (0, 6, 0), (5.4, 2.8, 4.4), "scarab", "thorax")
    k.box(body, C(0, 8.4, 1.2, 9.0, 0.8, 4.0), "gold", tag="thorax_rim")
    hd = k.part("head", (0, 6, 4.2), (), "body")
    k.blob(hd, (0, 5.6, 6.2), (3.6, 2.0, 2.4), "scarab", "head")
    for sx in (-1, 1):
        k.box(hd, C(sx * 2.0, 6.4, 8.0, 1.0, 0.8, 0.6), "eye", group="glow", tag="eye")
        k.shard(hd, (sx * 1.4, 4.4, 8.0), (sx * 0.5, -0.2, 1), 3.6, 1.2, mat="scarab", tag="mandible")
        k.shard(hd, (sx * 1.2, 7.6, 7.0), (sx * 0.3, 1, 0.2), 4.4, 1.4, mat="scarab", tag="horn")
    k.blob(hd, (0, 13.6, 7.6), (3.2, 3.2, 0.8), "glow", "sun_disc", step=0.7)
    k.ring(hd, 0, 13.6, 7.6, 3.4, 0.8, "gold", "sun_ring", n=14)
    ab = k.part("abdomen", (0, 6, -3), (("x", -6),), "body")
    k.blob(ab, (0, 6.4, -7.4), (6.4, 4.0, 6.4), "dark", "abdomen")
    for sx in (-1, 1):           # the wing cases, split open, the wings of light under them
        cs = k.part("elytron%d" % (sx > 0), (sx * 0.6, 9.6, -3.0), (("z", sx * 22), ("y", sx * 10)), ab, bone=False)
        k.blob(cs, (sx * 3.4, 9.6, -7.6), (3.4, 1.6, 6.4), "scarab", "elytron", step=0.8)
        k.box(cs, C(sx * 3.4, 10.6, -7.6, 1.0, 0.6, 12.4), "gold", tag="elytron_seam")
        k.box(ab, C(sx * 2.4, 9.0, -9.0, 4.4, 0.6, 9.0), "glow", group="glow", tag="wing_light")
    joints = {"body": "Root", "head": "Head", "abdomen": "Stomach"}
    for side, s in ((1, "l"), (-1, "r")):
        for i, (z, j) in enumerate(((2.4, 1), (0.0, 2), (-2.4, 4))):
            nm = "leg_%s%d" % (s, i)
            lg = k.part(nm, (side * 4.6, 5, z), (("y", -side * (i - 1) * 30),), "body")
            knee = (side * 8.6, 7.6, z)
            k.limb(lg, (side * 4.6, 5.0, z), knee, 1.6, "scarab", "femur")
            k.limb(lg, knee, (side * 11.0, 0.6, z), 1.2, "scarab", "foot")
            for t in (0.3, 0.6):
                p = (side * (8.6 + 2.4 * t), 7.6 - 7.0 * t, z)
                k.shard(lg, p, (side * 1, 0.2, 0), 1.2, 0.6, mat="gold", tag="leg_tooth")
            joints[nm] = ("LL" if side > 0 else "RL") + str(j)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


MOBS = {
    "tomb_scarab": dict(make=tomb_scarab, rig="crawler", ent=(1.1, 0.8), stats=dict(hp=22, speed=0.32, dmg=5, armor=5, kb=0)),
    "sand_colossus": dict(make=sand_colossus, ent=(1.6, 4.0), stats=dict(hp=95, speed=0.18, dmg=13, armor=10, kb=1.0)),
    "embalmer": dict(make=embalmer, ent=(0.9, 2.9), stats=dict(hp=34, speed=0.21, dmg=6, armor=2, kb=0)),
    "jackal_runner": dict(make=jackal_runner, ent=(0.9, 2.7), stats=dict(hp=30, speed=0.35, dmg=7, armor=3, kb=0)),
    "sun_guardian": dict(make=sun_guardian, ent=(1.2, 3.3), stats=dict(hp=180, speed=0.22, dmg=12, armor=10, kb=0.6), key=True),
    "sun_king": dict(make=sun_king, texel=1, ent=(2.6, 6.6), stats=dict(hp=520, speed=0.21, dmg=18, armor=10, kb=1.0), boss=True),
}
