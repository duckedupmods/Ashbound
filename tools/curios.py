"""Curios and relics (docs/RELICS.md): 20 rings, 20 amulets, 20 charms and 16 relics, built in the weapons' chunky box
style (voxsword boxes + weaponforge shaders), each in its faction's metals, cloths and glow. Concept stage: the models
are written to tools/renders/curios (not the game) and rendered to a sheet for approval.

    python tools/curios.py [ids or slots...] [--sheet]     -> tools/renders/curios/mesh/*, tools/renders/curios.png
    python tools/curios.py --export     meshes, item models, names, curios.json, Curios slots + tags into the mod
"""
import json
import math
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import worldarms as WA  # noqa: E402
import weaponforge as W  # noqa: E402
import voxsword as V  # noqa: E402
from voxsword import Sword  # noqa: E402
from weaponforge import Theme, bx, ring_xy, seg  # noqa: E402

PAL = WA.PAL
OUT = os.path.join(W.GAME, "tools/renders/curios")

# faction -> (blade = main metal, dark, wrap, wood, glow, acc)
LOOK = {
    "Brigands": ("worn_iron", "dark_iron", "brown_leather", "oak", "g_blood", "brass"),
    "Delvers": ("copper", "iron", "brown_leather", "oak", "g_ember", "brass"),
    "Corsairs": ("sea_bronze", "dark_iron", "blue_cloth", "dark_wood", "g_sea", "gold"),
    "Fallen Order": ("tarnished", "dark_iron", "white_cloth", "dark_wood", "g_holy", "silver"),
    "Salt-Cursed": ("sandstone", "bronze", "white_cloth", "pale_wood", "g_sand", "gold"),
    "Brood": ("chitin", "black_steel", "green_cloth", "dark_wood", "g_acid", "bone"),
    "Rimebound": ("ice", "storm", "blue_cloth", "pale_wood", "g_frost", "silver"),
    "Sky Legion": ("white_gold", "steel", "white_cloth", "pale_wood", "g_storm", "gold"),
    "Ash Legion": ("black_steel", "charred", "red_cloth", "charred", "g_teal", "copper"),
    "Thornborn": ("venom", "dark_wood", "green_cloth", "oak", "g_rose", "bone"),
    "Sporefolk": ("venom", "fur", "purple_cloth", "pale_wood", "g_spore", "bone"),
    "Grave-born": ("bone", "dark_iron", "black_leather", "ash_wood", "g_ghost", "tarnished"),
    "Voidborn": ("obsidian", "black_steel", "purple_cloth", "charred", "g_void", "silver"),
    "Blightkin": ("rust", "dark_iron", "green_cloth", "dark_wood", "g_venom", "bone"),
    "Foundry": ("black_steel", "charred", "black_leather", "charred", "g_ember", "copper"),
    "Crypt": ("bone", "tarnished", "white_cloth", "pale_wood", "g_holy", "gold"),
    "Gallows Hill": ("worn_iron", "dark_iron", "pale_wood", "ash_wood", "g_ghost", "rust"),
    "Drowned Cellar": ("bronze", "dark_iron", "brown_leather", "oak", "g_sea", "brass"),
    "Rotwood": ("venom", "dark_wood", "green_cloth", "oak", "g_aurora", "bone"),
    "Silk Archive": ("tarnished", "obsidian", "white_cloth", "dark_wood", "g_void", "silver"),
    "Stormspire": ("storm", "basalt", "blue_cloth", "dark_wood", "g_storm", "brass"),
    "Last Keep": ("steel", "iron", "red_cloth", "oak", "g_ember", "bone"),
}
FROM = {"Stormspire": "tower hoards", "Last Keep": "tower hoards"}


def theme(iid, faction, over):
    pal = dict(zip(("blade", "dark", "wrap", "wood", "glow", "acc"), LOOK[faction]))
    pal.update(over or {})
    return Theme(iid, **{k: PAL[v] for k, v in pal.items()})


# ================================================================== parts

def ball(s, cx, cy, r, mat, z=0.0, glow=False, n=5, squash=1.0):
    """a stepped sphere (slices along y)"""
    h = 2 * r / n
    for k in range(n):
        ym = -r + h * (k + 0.5)
        w = 2 * math.sqrt(max(r * r - ym * ym, 0.04 * r * r))
        bx(s, cx, cy + (ym - h / 2) * squash, z, w, h * squash + 0.04, w, mat, glow)


def disc(s, cx, cy, r, d, mat, z=0.0, glow=False):
    """a flat round plate facing the viewer"""
    n = max(4, int(r * 2.2))
    h = 2 * r / n
    for k in range(n):
        ym = -r + h * (k + 0.5)
        w = 2 * math.sqrt(max(r * r - ym * ym, 0.05 * r * r))
        bx(s, cx, cy + ym - h / 2, z, w, h + 0.04, d, mat, glow)


def slices(s, cx, top, widths, h, mat, z=0.0, glow=False, depth=1.0):
    """a turned shape from the top down (bottle, teardrop, acorn)"""
    for k, w in enumerate(widths):
        bx(s, cx, top - (k + 1) * h, z, w, h + 0.04, w * depth, mat, glow)


def band(s, r=5.0, t=1.4, d=2.0, mat="blade", cx=0.0, cy=0.0, z=0.0):
    ring_xy(s, cx, cy, r, t, mat, n=max(16, int(r * 4)), z=z, depth=d)


def spikes(s, cx, cy, r, n, ln, w, mat, a0=0.0, arc=360.0, z=0.0, glow=False):
    for k in range(n):
        a = math.radians(a0 + (arc * k / n if arc >= 360 else arc * k / max(1, n - 1)))
        c, sn = math.cos(a), math.sin(a)
        seg(s, (cx + c * r, cy + sn * r), (cx + c * (r + ln * 0.6), cy + sn * (r + ln * 0.6)), w, w, mat, z, glow)
        seg(s, (cx + c * (r + ln * 0.5), cy + sn * (r + ln * 0.5)), (cx + c * (r + ln), cy + sn * (r + ln)), w * 0.5, w * 0.5, mat, z, glow)


def path(s, pts, widths, mat, z=0.0, glow=False, depth=None):
    """a bent tube through pts, widths tapering"""
    for k in range(len(pts) - 1):
        w = widths[min(k, len(widths) - 1)]
        seg(s, pts[k], pts[k + 1], w, depth if depth else w, mat, z, glow)


def gem(s, x, y, size, z=0.0, cup="acc", glow="glow"):
    """a cut stone in a cup with four prongs"""
    bx(s, x, y - size * 0.2, z, size * 1.4, size * 0.55, size * 1.4, cup)
    bx(s, x, y, z, size, size, size, glow, glow=True)
    bx(s, x, y + size * 0.2, z + size * 0.15, size * 0.45, size * 0.5, size * 0.8, "white", glow=True)
    for sx in (-1, 1):
        for sz in (-1, 1):
            bx(s, x + sx * size * 0.5, y - size * 0.1, z + sz * size * 0.5, size * 0.22, size * 0.7, size * 0.22, cup)


def flame(s, x, y, sz, z=0.0):
    bx(s, x, y, z, sz * 0.75, sz * 0.6, sz * 0.75, "glow", glow=True)
    bx(s, x, y + sz * 0.5, z, sz * 0.5, sz * 0.6, sz * 0.5, "glow", glow=True)
    bx(s, x + sz * 0.05, y + sz * 0.95, z, sz * 0.22, sz * 0.5, sz * 0.22, "glow", glow=True)
    bx(s, x, y + sz * 0.1, z, sz * 0.38, sz * 0.55, sz * 0.82, "white", glow=True)


def skull(s, x, y, size, z=0.0, mat="blade", eyes=None):
    bx(s, x, y + size * 0.3, z, size, size * 0.75, size * 0.9, mat)
    bx(s, x, y, z, size * 0.62, size * 0.4, size * 0.75, mat)
    for sx in (-1, 1):
        bx(s, x + sx * size * 0.22, y + size * 0.42, z + size * 0.42, size * 0.26, size * 0.24, 0.3,
           eyes or "dark", glow=bool(eyes))
    bx(s, x, y + size * 0.24, z + size * 0.4, size * 0.12, size * 0.14, 0.3, "dark")
    for k in range(3):
        bx(s, x + (k - 1) * size * 0.16, y + size * 0.04, z + size * 0.36, size * 0.08, size * 0.2, 0.3, "dark")


def mushroom(s, x, y, w, z=0.0, cap="wrap", stem="wood"):
    bx(s, x, y, z, w * 0.32, w * 0.45, w * 0.32, stem)
    bx(s, x, y + w * 0.4, z, w, w * 0.3, w, cap)
    bx(s, x, y + w * 0.68, z, w * 0.62, w * 0.22, w * 0.62, cap)
    for dx, dy in ((-0.28, 0.5), (0.22, 0.56), (0.02, 0.8)):
        bx(s, x + dx * w, y + dy * w, z + w * 0.42, w * 0.14, w * 0.14, w * 0.2, "glow", glow=True)


def heart(s, x, y, size, mat, z=0.0):
    for sx in (-1, 1):
        ball(s, x + sx * size * 0.24, y, size * 0.3, mat, z)
    for k in range(4):
        bx(s, x, y - size * 0.18 * (k + 1), z, size * (0.92 - 0.22 * k), size * 0.2, size * 0.5, mat)


def necklace(s, mat="dark", beads=None, w=0.5, cy=5.0, rx=3.8, ry=4.2):
    """a chain (or a bead string) over the top, hanging to a bail at (0, 0); the pendant hangs below y 0.
    Worn (WORN["amulet"] set): a V lying flat on the chest from the bail up to the collar, where it runs under the head"""
    if WORN.get("amulet"):
        k = WORN["amulet"]
        top = (NECK_X / k, COLLAR_DROP / k + 0.6)
        n = 9
        for sgn in (-1, 1):
            # a slight outward bow, like a real chain lying over a chest
            pts = [(sgn * (0.6 + (top[0] - 0.6) * t + 0.7 * math.sin(math.pi * t)), 0.4 + (top[1] - 0.4) * t)
                   for t in (i / n for i in range(n + 1))]
            for i in range(n):
                if beads:
                    size, bmat, every = beads
                    m = "glow" if every and i % every == 0 else bmat
                    bx(s, pts[i][0], pts[i][1] - size / 2, 0, size, size, size, m, glow=m == "glow")
                else:
                    seg(s, pts[i], pts[i + 1], w * (1.7 if i % 2 else 0.8), w * (0.8 if i % 2 else 1.7), mat)
        ring_xy(s, 0, 0, 0.8, 0.45, mat, n=8)
        return
    n = 18
    a0, a1 = -62, 242
    pts = [(rx * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * k / n)))
           for k in range(n + 1)]
    for k in range(n):
        if beads:
            size, bmat, every = beads
            m = "glow" if every and k % every == 0 else bmat
            bx(s, pts[k][0], pts[k][1] - size / 2, 0, size, size, size, m, glow=m == "glow")
        else:
            seg(s, pts[k], pts[k + 1], w * (1.7 if k % 2 else 0.8), w * (0.8 if k % 2 else 1.7), mat)
    for p in (pts[0], pts[-1]):
        seg(s, p, (0, 0.4), w, w, mat)
    ring_xy(s, 0, 0, 0.8, 0.45, mat, n=8)


# ------------------------------------------------------------------ worn on the body (client/WornCurios.java)
# Model units are Minecraft pixels; a worn piece is drawn at this size. The amulet's chain is rebuilt for it (necklace).
WORN_SCALE = {"ring": 0.45, "amulet": 0.6, "charm": 0.45, "relic": 0.4}
WORN = {}            # set while building the worn amulets: {"amulet": scale}
NECK_X = 2.2         # px either side of the middle where the chain meets the collar (under the head)
COLLAR_DROP = 4.0    # px from the bail up to the top of the chest


def rots_box(s, cx, y0, cz, sx, sy, sz, mat, rots, pivot, glow=False):
    bx(s, cx, y0, cz, sx, sy, sz, mat, glow, rots=rots, pivot=pivot)


# ================================================================== rings (band r~5 round (0, 0), the setting on top)

def r_knuckle(s):
    band(s, 5, 1.7, 2.6)
    bx(s, 0, 4.0, 0, 6.6, 2.6, 3.4, "dark")
    for x in (-2.2, 0, 2.2):
        bx(s, x, 6.5, 0, 1.4, 1.1, 1.4, "acc")
        bx(s, x, 7.5, 0, 0.7, 0.6, 0.7, "acc")


def r_tunnel(s):
    band(s, 4.8, 1.1, 1.6)
    for a in (35, 145, 215, 325):
        c, sn = math.cos(math.radians(a)), math.sin(math.radians(a))
        bx(s, c * 5.4, sn * 5.4 - 0.4, 0, 0.8, 0.8, 0.8, "acc")
    gem(s, 0, 5.0, 1.6)


def r_gravedigger(s):
    band(s, 4.9, 1.3, 1.8, "acc")
    skull(s, 0, 4.2, 3.6)


def r_spore(s):
    band(s, 4.8, 1.2, 1.8)
    mushroom(s, -0.6, 4.4, 4.0)
    mushroom(s, 2.2, 4.4, 2.2)


def r_bowstring(s):
    band(s, 4.6, 1.4, 4.2)
    band(s, 4.75, 1.6, 0.6, "wrap")
    gem(s, 0, 5.4, 1.4)


def r_thumb(s):
    band(s, 5, 1.8, 3.8, "dark")
    for k in range(10):
        a = math.radians(36 * k + 18)
        for z in (-1.4, 1.4):
            bx(s, math.cos(a) * 5.9, math.sin(a) * 5.9 - 0.35, z, 0.7, 0.7, 0.7, "blade")


def r_bone_knot(s):
    band(s, 4.8, 1.3, 1.8)
    for a in (40, 90, 140, 220, 320):
        c, sn = math.cos(math.radians(a)), math.sin(math.radians(a))
        ball(s, c * 4.9, sn * 4.9, 1.25, "blade", n=4)
        seg(s, (c * 4.0, sn * 4.0), (c * 5.9, sn * 5.9), 0.5, 2.2, "dark")


def r_doubloon(s):
    band(s, 4.8, 1.3, 1.8, "acc")
    disc(s, 0, 7.0, 3.3, 1.0, "gold")
    disc(s, 0, 7.0, 2.5, 1.25, "acc")
    skull(s, 0, 6.0, 2.0, z=0.55, mat="gold")


def r_signet(s):
    band(s, 5, 1.5, 2.2)
    bx(s, 0, 3.8, 0, 4.8, 3.6, 2.6, "blade")
    bx(s, 0, 4.4, 1.3, 0.8, 2.4, 0.4, "acc")
    bx(s, 0, 5.4, 1.3, 2.4, 0.8, 0.4, "acc")


def r_ember_coil(s):
    for z, r in ((-1.3, 4.6), (0, 5.0), (1.3, 4.6)):
        band(s, r, 0.9, 1.0, z=z)
    bx(s, 0, 4.4, 0, 2.6, 1.6, 2.6, "acc")
    flame(s, 0, 5.8, 2.6)


def r_briar(s):
    band(s, 4.8, 1.2, 1.8, "wood")
    spikes(s, 0, 0, 5.3, 11, 1.8, 0.6, "dark", a0=10)
    for k in range(5):
        a = 2 * math.pi * k / 5 + 0.3
        bx(s, math.cos(a) * 0.9, 5.6 + math.sin(a) * 0.9, 0, 1.3, 1.3, 1.3, "glow", glow=True)
    bx(s, 0, 5.6, 0.2, 1.1, 1.1, 1.6, "white", glow=True)


def r_frostbite(s):
    band(s, 5, 1.4, 2.0, "dark")
    for a, b, w in (((-1.2, 4.4), (-2.6, 8.4), 1.4), ((0, 4.4), (0.2, 9.6), 1.8), ((1.2, 4.4), (2.8, 7.8), 1.3)):
        seg(s, a, b, w, w, "glow", glow=True)
        seg(s, a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), w * 0.5, w * 1.1, "white", glow=True)


def r_hollow_eye(s):
    band(s, 4.9, 1.4, 2.0)
    bx(s, 0, 3.9, 0, 5.0, 3.0, 2.2, "acc")
    bx(s, 0, 4.6, 0.4, 3.8, 1.7, 1.7, "white", glow=True)
    bx(s, 0, 4.7, 1.25, 1.1, 1.5, 0.3, "void")
    bx(s, 0, 4.9, 1.4, 0.5, 0.5, 0.3, "glow", glow=True)


def r_salt_khan(s):
    band(s, 5, 1.9, 2.8, "acc")
    bx(s, 0, 4.0, 0, 4.6, 5.0, 3.4, "blade")
    bx(s, 0, 8.8, 0, 5.4, 0.9, 3.8, "acc")
    disc(s, 0, 6.6, 1.3, 0.5, "glow", z=1.7, glow=True)
    for k in range(8):
        a = math.radians(45 * k)
        seg(s, (math.cos(a) * 1.5, 6.6 + math.sin(a) * 1.5), (math.cos(a) * 2.1, 6.6 + math.sin(a) * 2.1), 0.45, 0.4, "acc", z=1.75)
    for sx in (-1, 1):
        bx(s, sx * 2.9, 4.6, 0, 1.2, 2.2, 1.2, "acc")


def r_chitin(s):
    for k in range(12):
        a, b = math.radians(30 * k), math.radians(30 * k + 34)
        seg(s, (math.cos(a) * 5, math.sin(a) * 5), (math.cos(b) * 5, math.sin(b) * 5), 1.7, 2.6, "blade")
        seg(s, (math.cos(a) * 5.7, math.sin(a) * 5.7), (math.cos(a + 0.25) * 5.7, math.sin(a + 0.25) * 5.7), 0.5, 2.0, "acc")
    for sx in (-1, 1):
        path(s, [(sx * 2.0, 4.4), (sx * 2.4, 6.6), (sx * 1.6, 8.6), (sx * 0.5, 9.2)], [1.2, 0.9, 0.6], "acc")
    gem(s, 0, 6.2, 1.9)


def r_rime_band(s):
    for z in (-1.0, 1.0):
        band(s, 5, 1.0, 0.9, "acc", z=z)
    band(s, 4.9, 1.2, 1.2, "blade")
    spikes(s, 0, 0, 5.4, 7, 2.2, 0.8, "glow", a0=25, arc=130, glow=True)
    spikes(s, 0, 0, 5.4, 5, 1.6, 0.7, "glow", a0=215, arc=110, glow=True)
    gem(s, 0, 5.8, 2.0)


def r_gyre(s):
    band(s, 5, 1.4, 2.0)
    bx(s, 0, 4.4, 0, 1.2, 1.8, 1.2, "acc")
    ring_xy(s, 0, 8.0, 2.4, 0.6, "acc", n=12)
    for k in range(14):
        a = 2 * math.pi * k / 14
        bx(s, math.cos(a) * 2.4, 7.7, math.sin(a) * 2.4, 0.7, 0.6, 0.7, "gold")
    ball(s, 0, 8.0, 1.3, "glow", glow=True, n=4)


def r_drowned(s):
    band(s, 5, 1.8, 2.6)
    for sx in (-1, 1):
        pts = [(sx * 5.4, -1.5), (sx * 5.9, 1.4), (sx * 5.0, 4.4), (sx * 3.4, 6.6), (sx * 1.8, 8.0), (sx * 2.4, 9.8)]
        path(s, pts, [1.6, 1.5, 1.3, 1.1, 0.8], "blade", z=0.6)
        for p in pts[1:4]:
            bx(s, p[0] * 0.98, p[1] - 0.3, 1.3, 0.55, 0.55, 0.4, "acc")
    for x, y in ((-1.8, 10.6), (0, 11.4), (1.8, 10.6)):
        seg(s, (x * 0.6, 9.4), (x, y), 0.7, 0.7, "acc", z=-1.2)
    ball(s, 0, 8.4, 2.3, "glow", glow=True)
    bx(s, -0.6, 8.8, 1.4, 1.0, 1.0, 0.6, "white", glow=True)


def r_ninth_pyre(s):
    band(s, 5, 1.8, 2.4)
    for k in range(9):
        a = math.radians(-10 + 200 * k / 8)
        flame(s, math.cos(a) * 6.0, math.sin(a) * 6.0 - 0.6, 1.4)
    bx(s, 0, 4.4, 0, 3.0, 2.4, 2.8, "acc")
    flame(s, 0, 6.6, 3.4)


def r_oathring(s):
    band(s, 5, 1.6, 3.0)
    bx(s, 0, 3.8, 0, 5.4, 4.0, 1.8, "acc")
    bx(s, 0, 2.8, 0, 3.4, 1.2, 1.7, "acc")
    bx(s, 0, 7.6, 0, 6.0, 0.8, 2.0, "gold")
    for sx in (-1, 1):
        bx(s, sx * 2.8, 3.6, 0, 0.7, 4.6, 2.0, "gold")
        seg(s, (sx * 2.8, 7.6), (sx * 4.6, 10.2), 0.9, 0.9, "gold")
        seg(s, (sx * 3.6, 8.8), (sx * 3.4, 10.6), 0.6, 0.6, "gold")
    bx(s, 0, 3.6, 0.95, 0.9, 3.6, 0.3, "glow", glow=True)
    bx(s, 0, 5.6, 0.95, 3.0, 0.9, 0.3, "glow", glow=True)


# ================================================================== amulets (chain over the top, pendant below y 0)

def a_wolf_tooth(s):
    necklace(s, "wrap", w=0.55)
    for x, ln, lean in ((-2.4, 3.6, -0.9), (0, 5.2, 0), (2.4, 3.6, 0.9)):
        path(s, [(x, 0.2), (x + lean * 0.5, -ln * 0.6), (x + lean, -ln)], [1.5, 0.9], "acc")
    for x in (-1.2, 1.2):
        bx(s, x, -0.4, 0, 0.9, 0.9, 0.9, "gold")


def a_miner(s):
    necklace(s, "dark")
    disc(s, 0, -3.8, 3.4, 1.0, "blade")
    ring_xy(s, 0, -3.8, 3.4, 0.7, "acc", n=16, depth=1.3)
    for sgn in (-1, 1):
        seg(s, (-2.0 * sgn, -6.0), (2.0 * sgn, -1.6), 0.6, 0.4, "dark", z=0.6)
        seg(s, (1.4 * sgn, -1.2), (2.6 * sgn, -2.4), 1.2, 0.4, "dark", z=0.6)
    gem(s, 0, -4.2, 1.0, z=0.6)


def a_shell(s):
    necklace(s, "wrap", w=0.55)
    for k in range(9):
        a = math.radians(205 + 130 * k / 8)
        seg(s, (0, -0.6), (math.cos(a) * 5.2, -0.6 + math.sin(a) * 5.2), 1.3, 0.9 + 0.3 * (k % 2), "acc" if k % 2 else "blade")
    bx(s, 0, -1.6, 0, 2.6, 1.6, 1.6, "blade")
    ball(s, 0, -3.2, 1.0, "glow", z=0.9, glow=True, n=3)


def a_grave_candle(s):
    necklace(s, "dark")
    bx(s, 0, -1.6, 0, 3.6, 1.0, 3.6, "acc")
    bx(s, 0, -8.4, 0, 3.8, 1.0, 3.8, "acc")
    for sx in (-1, 1):
        for sz in (-1, 1):
            bx(s, sx * 1.5, -7.6, sz * 1.5, 0.5, 6.2, 0.5, "dark")
    bx(s, 0, -7.4, 0, 1.4, 3.0, 1.4, "blade")
    flame(s, 0, -4.4, 1.3)


def a_spore_beads(s):
    necklace(s, beads=(1.0, "wrap", 4))
    mushroom(s, 0, -4.8, 3.8)
    mushroom(s, -2.2, -4.0, 1.9)
    mushroom(s, 2.0, -3.6, 1.6)
    bx(s, 0, -1.2, 0, 0.6, 1.6, 0.6, "dark")


def a_thorn_choker(s):
    ring_xy(s, 0, 4.0, 5.2, 1.1, "wood", n=22, depth=1.4)
    spikes(s, 0, 4.0, 5.6, 14, 1.7, 0.55, "dark", a0=5)
    for k in range(5):
        a = 2 * math.pi * k / 5 + 0.3
        bx(s, math.cos(a) * 1.0, -1.6 + math.sin(a) * 1.0, 0.6, 1.4, 1.4, 1.4, "glow", glow=True)
    bx(s, 0, -1.6, 0.9, 1.2, 1.2, 1.6, "white", glow=True)
    for sx in (-1, 1):
        seg(s, (sx * 0.8, -2.4), (sx * 2.2, -3.6), 0.9, 0.5, "blade", z=0.4)


def a_ash_beads(s):
    necklace(s, beads=(1.0, "wood", 0))
    bx(s, 0, -1.6, 0, 1.8, 1.8, 1.8, "acc")
    for x in (-0.8, -0.3, 0.3, 0.8):
        seg(s, (x * 0.6, -1.6), (x * 1.4, -6.2), 0.45, 0.45, "wrap")
    ball(s, 0, -3.4, 0.9, "glow", z=0.8, glow=True, n=3)


def a_moonpetal(s):
    necklace(s, "acc")
    disc(s, 0, -3.8, 3.2, 1.4, "blade")
    for k in range(6):
        a = math.radians(60 * k + 90)
        seg(s, (math.cos(a) * 2.6, -3.8 + math.sin(a) * 2.6), (math.cos(a) * 3.8, -3.8 + math.sin(a) * 3.8), 1.4, 1.0, "acc")
    disc(s, 0, -3.8, 1.8, 0.5, "glow", z=0.8, glow=True)
    disc(s, 0.9, -3.4, 1.5, 0.5, "blade", z=1.0)


def a_sun_disc(s):
    necklace(s, "acc")
    disc(s, 0, -4.4, 2.7, 1.2, "acc")
    for k in range(12):
        a = math.radians(30 * k)
        ln = 4.4 if k % 2 else 3.6
        seg(s, (math.cos(a) * 2.4, -4.4 + math.sin(a) * 2.4), (math.cos(a) * ln, -4.4 + math.sin(a) * ln), 0.8, 0.8, "acc")
    disc(s, 0, -4.4, 1.6, 0.5, "glow", z=0.7, glow=True)


def a_frozen_tear(s):
    necklace(s, "acc")
    bx(s, 0, -1.6, 0, 2.2, 1.2, 2.2, "acc")
    slices(s, 0, -1.4, [1.2, 2.0, 2.8, 3.3, 3.4, 3.1, 2.4, 1.2], 0.9, "glow", glow=True)
    slices(s, -0.3, -2.2, [0.8, 1.4, 1.6, 1.2], 0.9, "white", z=0.9, glow=True, depth=0.6)


def a_brood_fang(s):
    necklace(s, "wrap", w=0.55)
    path(s, [(0, -0.4), (0.8, -3.2), (0.5, -5.8), (-0.6, -7.8), (-2.0, -9.0)], [2.6, 2.1, 1.5, 0.8], "acc")
    bx(s, 0, -1.4, 0, 3.0, 1.2, 3.0, "wrap")
    for y in (-10.2, -11.6):
        bx(s, -2.2, y, 0, 0.7, 0.9, 0.7, "glow", glow=True)


def a_pyx(s):
    necklace(s, "acc")
    bx(s, 0, -6.4, 0, 4.2, 4.6, 3.2, "blade")
    bx(s, 0, -1.8, 0, 4.6, 1.0, 3.6, "acc")
    bx(s, 0, -2.1, 0, 4.3, 0.35, 3.3, "glow", glow=True)
    bx(s, 0, -5.8, 1.65, 0.8, 3.4, 0.3, "gold")
    bx(s, 0, -4.6, 1.65, 2.4, 0.8, 0.3, "gold")
    for sx in (-1, 1):
        bx(s, sx * 1.7, -7.2, 0, 0.8, 0.8, 3.4, "acc")


def a_void_shard(s):
    necklace(s, "wrap", w=0.55)
    bx(s, 0, -1.6, 0, 2.4, 1.2, 2.0, "acc")
    for a, b, w in (((0, -1.0), (0.5, -9.0), 2.2), ((-0.6, -2.4), (-2.6, -6.4), 1.3), ((0.8, -3.2), (2.4, -6.8), 1.1)):
        seg(s, a, b, w, w, "glow", glow=True)
        seg(s, a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), w * 0.45, w * 1.1, "white", glow=True)


def a_augur(s):
    necklace(s, "acc")
    bx(s, 0, -2.0, 0, 3.6, 1.2, 3.6, "acc")
    bx(s, 0, -8.4, 0, 3.0, 1.0, 3.0, "acc")
    for k in range(6):
        a = 2 * math.pi * k / 6
        bx(s, math.cos(a) * 1.6, -7.6, math.sin(a) * 1.6, 0.5, 5.8, 0.5, "dark")
    ball(s, 0, -4.8, 1.6, "glow", glow=True, n=4)
    for sx in (-1, 1):
        path(s, [(sx * 0.8, -8.6), (sx * 1.8, -10.6), (sx * 2.4, -12.4)], [1.1, 0.7], "wrap")


def a_briar_heart(s):
    necklace(s, "wood", w=0.6)
    heart(s, 0, -2.6, 6.0, "wood")
    seg(s, (-2.2, -2.2), (1.4, -5.6), 0.5, 0.6, "glow", z=1.4, glow=True)
    for a, b in (((-3.4, -1.0), (3.0, -4.6)), ((-2.8, -5.2), (2.6, -1.8))):
        seg(s, a, b, 0.6, 0.6, "dark", z=1.7)
        for t in (0.25, 0.5, 0.75):
            x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            bx(s, x, y, 2.0, 0.4, 0.9, 0.5, "dark")


def a_gryphon_torc(s):
    n = 20
    pts = [(5.6 * math.cos(math.radians(-58 + 296 * k / n)), 4.4 + 5.2 * math.sin(math.radians(-58 + 296 * k / n))) for k in range(n + 1)]
    for k in range(n):
        seg(s, pts[k], pts[k + 1], 1.7, 1.7, "acc" if k % 2 else "blade")
    for p, sx in ((pts[0], 1), (pts[-1], -1)):
        bx(s, p[0], p[1] - 1.6, 0, 2.4, 2.4, 2.4, "blade")
        seg(s, (p[0], p[1] - 1.2), (p[0] - sx * 1.6, p[1] - 2.6), 1.0, 1.0, "acc")
        bx(s, p[0] + sx * 0.4, p[1] - 0.6, 1.1, 0.6, 0.6, 0.5, "glow", glow=True)
        seg(s, (p[0] + sx * 0.6, p[1]), (p[0] + sx * 1.6, p[1] + 1.4), 0.7, 0.6, "blade")


def a_gorget(s):
    for k, r in enumerate((4.8, 6.2, 7.6)):
        m = 10
        pts = [(r * math.cos(math.radians(198 + 144 * j / m)), 5.6 + r * math.sin(math.radians(198 + 144 * j / m))) for j in range(m + 1)]
        for j in range(m):
            seg(s, pts[j], pts[j + 1], 1.5, 1.2 + 0.25 * k, "blade", z=-0.3 * k)
        bx(s, pts[0][0], pts[0][1] - 0.4, 0.4, 0.6, 0.6, 1.6, "gold")
        bx(s, pts[-1][0], pts[-1][1] - 0.4, 0.4, 0.6, 0.6, 1.6, "gold")
    gem(s, 0, -1.6, 1.8, z=0.6)
    for sx in (-1, 1):
        seg(s, (sx * 7.4, 3.4), (sx * 5.0, 8.4), 1.2, 0.5, "wrap")


def a_last_vigil(s):
    necklace(s, "acc")
    bx(s, 0, -2.0, 0, 3.4, 1.4, 3.4, "gold")
    bx(s, 0, -9.0, 0, 3.4, 1.2, 3.4, "gold")
    seg(s, (0, -9.0), (0, -11.0), 1.4, 1.4, "gold")
    for sx in (-1, 1):
        for sz in (-1, 1):
            bx(s, sx * 1.3, -7.8, sz * 1.3, 0.5, 5.8, 0.5, "acc")
    ball(s, 0, -5.0, 1.5, "glow", glow=True, n=4)
    for sx in (-1, 1):
        for k, (ln, ang) in enumerate(((4.6, 40), (3.8, 20), (3.0, 2))):
            a = math.radians(ang)
            seg(s, (sx * 1.6, -2.4 - k * 1.0), (sx * (1.6 + math.cos(a) * ln), -2.4 - k * 1.0 + math.sin(a) * ln), 1.1, 0.6, "wrap")


def a_hive_heart(s):
    necklace(s, "dark")
    heart(s, 0, -2.8, 6.4, "blade")
    for x, y in ((-1.6, -2.4), (0, -2.0), (1.6, -2.4), (-0.8, -3.8), (0.8, -3.8), (0, -5.2)):
        bx(s, x, y, 1.6, 0.9, 0.9, 0.4, "glow", glow=True)
    for sx in (-1, 1):
        for k in range(3):
            path(s, [(sx * 2.6, -2.8 - k * 1.2), (sx * 4.2, -2.0 - k * 1.4), (sx * 4.8, -4.0 - k * 1.2)], [0.5, 0.4], "dark")


def a_censer(s):
    necklace(s, "acc", cy=5.6)
    bx(s, 0, -1.8, 0, 1.4, 1.2, 1.4, "acc")
    ball(s, 0, -5.4, 3.0, "dark", n=6)
    for k in range(8):
        a = 2 * math.pi * k / 8
        bx(s, math.sin(a) * 2.8, -5.8, math.cos(a) * 2.8, 0.7, 0.8, 0.7, "glow", glow=True)
    bx(s, 0, -3.0, 0, 2.6, 0.9, 2.6, "acc")
    bx(s, 0, -9.0, 0, 1.8, 0.9, 1.8, "acc")
    ring_xy(s, 0, -5.4, 4.6, 0.5, "glow", n=20, glow=True, z=-2.2)
    for x, y in ((-0.6, -1.0), (0.4, 0.4), (-0.2, 1.8)):
        bx(s, x + 2.6, y - 1.6, 1.0, 0.9, 0.9, 0.9, "white", glow=True)


# ================================================================== charms (small objects, ~10 px)

def c_rabbit_foot(s):
    bx(s, 0, -2, 0, 3.0, 6.0, 3.0, "wrap")
    bx(s, 0, -4.4, 0.6, 3.4, 2.6, 4.2, "wrap")
    for x in (-1.0, 0, 1.0):
        seg(s, (x, -4.6), (x * 1.2, -5.8), 0.5, 0.5, "acc", z=2.4)
    bx(s, 0, 3.6, 0, 3.4, 1.4, 3.4, "gold")
    ring_xy(s, 0, 6.0, 1.1, 0.5, "gold", n=8)


def c_lamp(s):
    bx(s, 0, -5, 0, 4.6, 1.2, 4.6, "dark")
    bx(s, 0, -3.8, 0, 3.4, 4.6, 3.4, "glow", glow=True)
    bx(s, 0, -3.0, 0, 1.6, 2.4, 3.6, "white", glow=True)
    for sx in (-1, 1):
        for sz in (-1, 1):
            bx(s, sx * 1.8, -3.8, sz * 1.8, 0.7, 4.6, 0.7, "blade")
    bx(s, 0, 0.8, 0, 4.4, 1.0, 4.4, "blade")
    bx(s, 0, 1.8, 0, 2.6, 1.0, 2.6, "blade")
    ring_xy(s, 0, 4.0, 1.6, 0.5, "dark", n=10)


def c_dice(s):
    for cx, cy, rots, pips in ((-1.9, -1.6, (("y", 25), ("z", 10)), ((0, 0),)), (1.8, 0.4, (("z", -20), ("x", 15)), ((-0.8, 0.8), (0.8, -0.8), (0, 0)))):
        piv = (cx, cy + 1.6, 0)
        bx(s, cx, cy, 0, 3.2, 3.2, 3.2, "acc", rots=rots, pivot=piv)
        for px, py in pips:
            bx(s, cx + px, cy + 1.4 + py, 1.55, 0.6, 0.6, 0.3, "dark", rots=rots, pivot=piv)


def c_knucklebone(s):
    bx(s, 0, -1.2, 0, 4.4, 2.4, 2.4, "acc")
    for sx in (-1, 1):
        ball(s, sx * 2.6, 0, 1.6, "acc", n=4)
    bx(s, 0, -0.4, 1.1, 1.0, 1.0, 0.4, "dark")
    ring_xy(s, 0, 2.6, 1.4, 0.5, "wrap", n=10)
    path(s, [(0, 4.0), (-1.2, 7.4), (0.6, 9.4)], [0.5], "wrap")


def c_twigs(s):
    for a, b in (((-1.6, -6), (-0.6, 6.4)), ((-0.4, -6.4), (0.2, 7.2)), ((0.8, -6), (1.0, 6.6)), ((1.8, -5.6), (2.6, 5.4)), ((-2.4, -5.4), (-2.6, 5.0))):
        seg(s, a, b, 0.8, 0.8, "wood")
    for y in (-1.6, 1.4):
        bx(s, 0, y, 0, 5.8, 1.1, 1.8, "wrap")
    for x, y, d in ((-0.6, 4.2, -1), (1.0, 3.0, 1), (-2.6, 2.4, -1), (2.6, -3.0, 1)):
        seg(s, (x, y), (x + d * 1.0, y + 0.6), 0.4, 0.4, "dark")
    seg(s, (0.2, 6.6), (2.8, 8.4), 1.4, 0.4, "blade")
    seg(s, (-0.6, 6.0), (-2.6, 7.8), 1.2, 0.4, "blade")


def c_hare_tail(s):
    ball(s, 0, -1, 3.0, "wrap", n=6)
    for x, y, z in ((-2.6, 0.6, 0.6), (2.4, -1.4, 0.8), (0.6, 1.8, 1.8), (-1.2, -3.2, 1.6), (1.6, 1.0, -1.8)):
        bx(s, x, y - 0.6, z, 1.4, 1.2, 1.4, "wrap")
    bx(s, 0, 1.8, 0, 2.2, 1.2, 2.2, "acc")
    ring_xy(s, 0, 4.0, 1.1, 0.5, "acc", n=8)


def c_token(s):
    disc(s, 0, 0, 3.6, 0.9, "blade")
    ring_xy(s, 0, 0, 3.6, 0.6, "acc", n=16, depth=1.2)
    ring_xy(s, 0, 4.4, 1.1, 0.5, "acc", n=8)
    ring_xy(s, 0, 0, 1.6, 0.45, "glow", n=10, glow=True, z=0.55, depth=0.3)
    bx(s, 0, -1.6, 0.55, 0.5, 3.2, 0.3, "glow", glow=True)
    bx(s, 0, -0.25, 0.55, 3.2, 0.5, 0.3, "glow", glow=True)


def c_spore_pouch(s):
    slices(s, 0, 2.0, [3.2, 4.4, 5.0, 5.2, 5.0, 4.4, 3.2], 1.0, "wrap")
    bx(s, 0, 1.6, 0, 2.4, 1.0, 2.4, "dark")
    for x in (-0.8, 0, 0.8):
        bx(s, x, 2.6, 0, 0.7, 1.4, 0.7, "wrap")
    path(s, [(1.0, 2.0), (2.6, 1.2), (2.8, -0.6)], [0.4], "acc", z=1.4)
    for x, y in ((-1.4, 4.6), (0.6, 5.6), (1.8, 4.0), (-0.2, 7.0)):
        bx(s, x, y, 0, 0.7, 0.7, 0.7, "glow", glow=True)


def c_harpy_feather(s):
    seg(s, (0, -7), (1.6, 8), 0.55, 0.55, "acc")
    for k in range(10):
        t = k / 9
        x, y = 0.15 + 1.45 * t, -4.6 + 12.0 * t
        ln = 2.8 * math.sin(math.pi * (0.15 + 0.8 * t))
        for sd in (-1, 1):
            seg(s, (x, y), (x + sd * ln, y - 1.4), 0.9, 0.35, "wrap" if k % 3 else "blade")
    bx(s, 0.0, -7.6, 0, 0.9, 1.6, 0.9, "glow", glow=True)


def c_purse(s):
    slices(s, 0, 2.2, [3.0, 4.6, 5.4, 5.6, 5.2, 4.2], 1.0, "wrap")
    bx(s, 0, 1.8, 0, 2.6, 1.0, 2.6, "dark")
    bx(s, 0, 2.8, 0, 3.2, 1.0, 3.2, "wrap")
    for x, y, z in ((3.6, -4.2, 1.0), (4.6, -3.6, -0.6), (3.0, -2.6, 2.0)):
        disc(s, x, y, 1.2, 0.4, "gold", z=z)
    bx(s, 0, -1.6, 2.6, 1.4, 1.4, 0.4, "gold")


def c_void_marble(s):
    bx(s, 0, -4.6, 0, 3.6, 1.2, 3.6, "acc")
    ball(s, 0, 0, 2.9, "glow", glow=True, n=6)
    bx(s, -0.8, 0.6, 1.6, 1.2, 1.2, 1.2, "white", glow=True)
    for k in range(4):
        a = 2 * math.pi * k / 4 + 0.6
        c, sn = math.cos(a), math.sin(a)
        for (y0, r0), (y1, r1) in (((-3.6, 1.4), (-1.6, 3.1)), ((-1.6, 3.1), (0.6, 2.8))):
            bx(s, c * (r0 + r1) / 2, y0, sn * (r0 + r1) / 2, 0.6, y1 - y0 + 0.2, 0.6, "acc")


def c_salt_ward(s):
    for ang in (0, 60, 120):
        bx(s, 0, -3.4, 0, 3.6, 6.8, 1.0, "acc", rots=(("z", ang),), pivot=(0, 0, 0))
    disc(s, 0, 0, 2.2, 1.2, "blade")
    for ang in (0, 60, 120):
        bx(s, 0, -1.6, 0.65, 0.4, 3.2, 0.3, "glow", glow=True, rots=(("z", ang),), pivot=(0, 0, 0.65))
    ring_xy(s, 0, 4.6, 1.0, 0.5, "acc", n=8)


def c_grub_lantern(s):
    bx(s, 0, -5, 0, 4.4, 1.0, 4.4, "dark")
    bx(s, 0, 1.0, 0, 4.8, 1.4, 4.8, "blade")
    for sx in (-1, 1):
        for sz in (-1, 1):
            bx(s, sx * 1.9, -4.0, sz * 1.9, 0.5, 5.0, 0.5, "acc")
    for k, (x, y) in enumerate(((-0.8, -3.6), (0, -2.4), (0.6, -1.2), (0.2, 0))):
        ball(s, x, y, 0.85 - 0.08 * k, "glow", glow=True, n=3)
    path(s, [(-2.0, 2.4), (-1.2, 4.2), (1.2, 4.2), (2.0, 2.4)], [0.5], "dark")


def c_kraken_eye(s):
    ball(s, 0, 0, 3.0, "acc", n=6)
    disc(s, 0, 0.2, 1.6, 0.5, "glow", z=2.7, glow=True)
    bx(s, 0, -0.9, 3.0, 0.5, 2.2, 0.3, "void")
    ring_xy(s, 0, 0, 3.2, 0.7, "blade", n=16, depth=1.4, z=0.8)
    for x, d in ((-1.8, -1), (0, 0), (1.8, 1)):
        path(s, [(x, -3.0), (x + d * 0.8, -5.2), (x + d * 2.2, -6.0), (x + d * 2.6, -4.8)], [1.0, 0.8, 0.5], "blade")


def c_compass(s):
    disc(s, 0, 0, 3.6, 1.6, "acc")
    disc(s, 0, 0, 2.8, 0.4, "wrap", z=0.75)
    seg(s, (0, 0), (1.4, 2.0), 0.7, 0.3, "glow", z=1.0, glow=True)
    seg(s, (0, 0), (-1.4, -2.0), 0.7, 0.3, "dark", z=1.0)
    bx(s, 0, -0.35, 1.05, 0.6, 0.6, 0.3, "gold")
    for k in range(4):
        a = math.radians(90 * k)
        bx(s, math.cos(a) * 2.4, math.sin(a) * 2.4 - 0.2, 0.9, 0.4, 0.4, 0.3, "gold")
    bx(s, 0, 3.4, 0, 1.4, 1.2, 1.4, "acc")
    ring_xy(s, 0, 5.4, 1.2, 0.5, "acc", n=8)


def c_blight_vial(s):
    slices(s, 0, 0.6, [3.0, 4.0, 4.4, 4.4, 4.0, 3.0], 1.0, "glow", glow=True)
    bx(s, 0, 0.4, 0, 1.6, 2.6, 1.6, "dark")
    bx(s, 0, 2.8, 0, 2.0, 1.4, 2.0, "wood")
    skull(s, 0, -3.8, 1.8, z=1.7, mat="acc")
    bx(s, -1.0, -4.2, 2.1, 0.6, 0.6, 0.4, "white", glow=True)


def c_finger_bone(s):
    for y in (-6.0, 4.0):
        bx(s, 0, y, 0, 3.0, 1.2, 3.0, "acc")
    for sx in (-1, 1):
        for sz in (-1, 1):
            bx(s, sx * 1.2, -4.8, sz * 1.2, 0.4, 8.8, 0.4, "acc")
    for k, (a, b) in enumerate((((0, -4.4), (0.2, -1.6)), ((0.2, -1.4), (-0.2, 0.8)), ((-0.2, 1.0), (0.1, 3.0)))):
        seg(s, a, b, 1.1 - 0.15 * k, 1.1 - 0.15 * k, "blade")
        bx(s, b[0], b[1] - 0.3, 0, 1.3 - 0.15 * k, 0.6, 1.3 - 0.15 * k, "blade")
    for x, y in ((-0.8, -2.8), (0.7, 0), (-0.5, 2.0)):
        bx(s, x, y, 0.6, 0.5, 0.5, 0.5, "glow", glow=True)
    ring_xy(s, 0, 6.2, 1.0, 0.5, "acc", n=8)


def c_gryphon_plume(s):
    for ang, mat, ln in ((-28, "blade", 11), (0, "acc", 14), (28, "blade", 11)):
        a = math.radians(90 + ang)
        tip = (math.cos(a) * ln, -4 + math.sin(a) * ln)
        seg(s, (0, -4), tip, 0.5, 0.5, "acc")
        for k in range(8):
            t = 0.15 + 0.85 * k / 7
            x, y = math.cos(a) * ln * t, -4 + math.sin(a) * ln * t
            w = 2.4 * math.sin(math.pi * t)
            for sd in (-1, 1):
                bb = a + sd * math.radians(55)
                seg(s, (x, y), (x + math.cos(bb) * w - math.cos(a) * 1.0, y + math.sin(bb) * w - math.sin(a) * 1.0), 0.9, 0.35, mat)
        if ang == 0:
            seg(s, (0, -2), (0, 8), 0.6, 0.7, "glow", glow=True)
    gem(s, 0, -4.6, 1.8)


def c_last_pick(s):
    seg(s, (0, -7), (0, 5.6), 1.1, 1.1, "wood")
    for y in (-6.0, -4.4):
        bx(s, 0, y, 0, 1.5, 0.8, 1.5, "wrap")
    path(s, [(0, 6), (-2.6, 5.8), (-5.0, 4.6), (-6.4, 3.0)], [1.9, 1.5, 1.0], "blade")
    path(s, [(0, 6), (2.6, 5.8), (5.0, 4.6), (6.4, 3.0)], [1.9, 1.5, 1.0], "blade")
    bx(s, 0, 5.0, 0, 2.4, 2.4, 2.4, "dark")
    for sx in (-1, 1):
        seg(s, (sx * 5.2, 4.3), (sx * 6.5, 2.8), 0.7, 1.2, "glow", glow=True)
    bx(s, 0, 5.6, 1.25, 0.9, 1.2, 0.3, "glow", glow=True)


def c_rift_key(s):
    ring_xy(s, 0, 5.4, 2.4, 0.9, "acc", n=14, depth=1.2)
    ball(s, 0, 5.4, 1.0, "glow", glow=True, n=3)
    bx(s, 0, -5.6, 0, 1.1, 9.0, 1.1, "acc")
    bx(s, 0, 2.2, 0, 2.2, 1.0, 1.6, "acc")
    for y, w in ((-5.6, 2.8), (-4.0, 2.2)):
        bx(s, 1.6, y, 0, w, 1.0, 0.9, "glow", glow=True)
    for x, y, a in ((3.6, -3.0, 20), (4.4, -5.6, -30), (3.0, -7.4, 45)):
        bx(s, x, y, 0, 0.8, 1.4, 0.6, "glow", glow=True, rots=(("z", a),), pivot=(x, y, 0))


# ================================================================== relics (bigger, ~14 px)

def x_barrow_signet(s):
    band(s, 5.4, 2.2, 3.2, "acc")
    skull(s, 0, 4.6, 5.4, eyes="glow")
    for k in range(5):
        x = (k - 2) * 1.3
        seg(s, (x, 8.4), (x * 1.15, 10.4 + (0.8 if k == 2 else 0)), 0.9, 0.9, "gold")
    bx(s, 0, 8.2, 0, 6.0, 0.8, 3.0, "gold")


def x_hourglass(s):
    for y in (10.0, -1.4):
        bx(s, 0, y, 0, 7.4, 1.3, 4.2, "acc")
    for x, z in ((-2.9, 1.4), (2.9, 1.4), (0, -1.6)):
        bx(s, x, -0.2, z, 0.8, 10.2, 0.8, "dark")
    slices(s, 0, 10.0, [4.6, 4.2, 3.2, 1.8, 0.9], 1.0, "glow", glow=True)
    slices(s, 0, 5.0, [0.9, 1.8, 3.2, 4.2, 4.6], 1.0, "glow", glow=True)
    slices(s, 0, 1.6, [2.4, 3.6], 0.8, "white", glow=True)


def x_void_pearl(s):
    bx(s, 0, -6.4, 0, 4.4, 1.4, 4.4, "dark")
    ball(s, 0, 0, 3.8, "glow", glow=True, n=7)
    bx(s, -1.2, 1.0, 2.2, 1.6, 1.6, 1.4, "white", glow=True)
    for k in range(4):
        a = 2 * math.pi * k / 4 + 0.5
        c, sn = math.cos(a), math.sin(a)
        pts = [(-5.0, 1.6), (-3.2, 3.9), (-0.4, 4.1), (1.8, 3.0)]
        for (y0, r0), (y1, r1) in zip(pts, pts[1:]):
            bx(s, c * (r0 + r1) / 2, y0, sn * (r0 + r1) / 2, 0.8, y1 - y0 + 0.3, 0.8, "acc")
    for x, y, z in ((5.4, 2.0, 0), (-5.6, -1.0, 1.0), (2.0, 5.6, -1.4), (-2.6, -4.6, 2.0)):
        bx(s, x, y, z, 0.9, 0.9, 0.9, "glow", glow=True, rots=(("z", 45),), pivot=(x, y, z))


def x_mantis_molt(s):
    bx(s, 0, 2.0, 0, 2.6, 4.2, 2.4, "blade")
    bx(s, 0, 6.2, 0, 2.0, 1.2, 1.8, "blade")
    bx(s, 0, 7.4, 0, 3.4, 1.6, 1.8, "blade")
    for sx in (-1, 1):
        bx(s, sx * 1.3, 7.8, 0.9, 0.9, 0.9, 0.5, "glow", glow=True)
        seg(s, (sx * 0.6, 9.0), (sx * 2.2, 11.4), 0.4, 0.4, "acc")
        path(s, [(sx * 1.2, 5.2), (sx * 4.2, 7.6), (sx * 5.0, 3.6), (sx * 3.6, 1.2)], [1.2, 1.0, 0.7], "acc")
        for t in (0.3, 0.6):
            x, y = sx * (5.0 - 1.4 * t), 3.6 - 2.4 * t
            seg(s, (x, y), (x - sx * 0.9, y + 0.5), 0.35, 0.35, "acc")
    for k, w in enumerate((2.8, 3.2, 3.0, 2.4, 1.6)):
        bx(s, 0, 0.4 - k * 1.5, 0, w, 1.4, w * 0.8, "blade" if k % 2 == 0 else "dark")
    seg(s, (0, 6.0), (0, -6.0), 0.4, 0.4, "glow", z=1.3, glow=True)


def x_spore_heart(s):
    heart(s, 0, 2.0, 9.0, "acc")
    for a, b in (((-2.6, 3.0), (1.0, -3.4)), ((2.6, 2.6), (-0.4, -1.8)), ((-0.6, 4.0), (0.4, 0.8))):
        seg(s, a, b, 0.5, 0.4, "glow", z=2.4, glow=True)
    mushroom(s, -2.0, 4.4, 3.6)
    mushroom(s, 1.8, 4.8, 2.6)
    mushroom(s, 3.6, 1.2, 1.8)


def x_brand(s):
    seg(s, (-5.0, -8.0), (2.4, 4.4), 1.0, 1.0, "dark")
    path(s, [(-5.6, -9.0), (-4.2, -6.6)], [1.8], "wrap")
    path(s, [(-4.6, -7.4), (-3.6, -5.6)], [1.8], "wrap")
    ring_xy(s, 3.2, 6.0, 2.8, 0.9, "blade", n=14, depth=1.3)
    bx(s, 3.2, 3.6, 0, 0.9, 4.8, 1.3, "blade")
    bx(s, 3.2, 5.6, 0, 4.8, 0.9, 1.3, "blade")
    ring_xy(s, 3.2, 6.0, 2.8, 0.4, "glow", n=14, glow=True, z=0.7, depth=0.3)
    flame(s, 2.4, 8.4, 2.4)
    flame(s, 4.4, 8.0, 1.8)


def x_rose(s):
    path(s, [(0, -9.0), (0.6, -5.0), (-0.4, -1.0), (0, 2.6)], [1.0], "blade")
    for y, d in ((-7.4, 1), (-5.6, -1), (-3.2, 1), (-1.4, -1)):
        seg(s, (0.1, y), (0.1 + d * 1.1, y + 0.6), 0.4, 0.4, "dark")
    for sx, y in ((1, -4.4), (-1, -2.2)):
        seg(s, (0, y), (sx * 3.4, y + 1.6), 1.6, 0.4, "blade")
    for k in range(7):
        a = 2 * math.pi * k / 7
        bx(s, math.cos(a) * 2.0, 4.0 + math.sin(a) * 2.0, -0.4, 2.6, 2.6, 2.6, "acc", rots=(("z", 20 * k),), pivot=(math.cos(a) * 2.0, 5.3 + math.sin(a) * 2.0, -0.4))
    for k in range(5):
        a = 2 * math.pi * k / 5 + 0.4
        bx(s, math.cos(a) * 1.0, 4.4 + math.sin(a) * 1.0, 0.8, 1.8, 1.8, 1.8, "acc")
    ball(s, 0, 5.2, 1.0, "glow", z=1.6, glow=True, n=3)


def x_gland(s):
    ball(s, 0, 0, 4.0, "acc", n=7)
    for (a, b), m in ((((-3.0, 1.6), (0.6, -2.6)), "glow"), (((2.8, 2.0), (-0.6, -0.8)), "white"), (((0.4, 3.6), (2.0, -2.8)), "glow")):
        seg(s, a, b, 0.6, 0.4, m, z=3.4, glow=True)
    for y in (-1.6, 1.6):
        ring_xy(s, 0, 0, 4.1 - abs(y) * 0.25, 0.5, "dark", n=16, depth=4.0)
    bx(s, 0, 3.6, 0, 1.8, 2.4, 1.8, "dark")
    bx(s, 0, 5.8, 0, 2.6, 0.8, 2.6, "dark")


def x_coal(s):
    for x, y, z, w, h, d, a in ((0, -3.6, 0, 7.0, 6.4, 5.0, 8), (-2.0, -0.4, 0.4, 4.4, 4.4, 4.0, -18), (2.2, -1.6, -0.2, 3.8, 5.0, 4.0, 26)):
        bx(s, x, y, z, w, h, d, "dark", rots=(("z", a),), pivot=(x, y + h / 2, z))
    for a, b in (((-3.0, 1.4), (0.2, -1.2)), ((0.2, -1.2), (2.6, 1.6)), ((0.2, -1.2), (-0.6, -4.6)), ((2.6, 1.6), (3.2, -2.4))):
        seg(s, a, b, 0.6, 0.6, "glow", z=2.5, glow=True)
    for y in (-2.0, 1.4):
        bx(s, 0, y, 0, 8.4, 0.9, 5.6, "blade")
    for sx in (-1, 1):
        bx(s, sx * 4.0, -2.0, 0, 1.0, 4.4, 1.0, "blade")


def x_wick(s):
    bx(s, 0, -6.4, 0, 7.6, 1.0, 7.6, "gold")
    ring_xy(s, 4.8, -5.8, 1.4, 0.5, "gold", n=8)
    bx(s, 0, -5.4, 0, 3.6, 9.4, 3.6, "blade")
    for x, z, ln in ((-1.4, 1.9, 3.4), (0.6, 1.9, 5.0), (1.9, -0.4, 2.6), (-1.9, -1.0, 4.0)):
        bx(s, x, 4.0 - ln, z, 0.8, ln, 0.6, "blade")
    bx(s, 0, 4.0, 0, 0.4, 1.0, 0.4, "dark")
    flame(s, 0, 4.8, 2.6)


def x_noose(s):
    ring_xy(s, 0, -3.0, 4.4, 1.4, "wrap", n=20, depth=1.4)
    for k in range(6):
        bx(s, 0, 1.0 + k * 1.1, 0, 2.8, 1.0, 2.8, "wrap")
        bx(s, 0, 1.8 + k * 1.1, 0, 3.0, 0.25, 3.0, "dark")
    path(s, [(0, 7.6), (0.8, 10.0), (2.0, 12.4)], [1.4], "wrap")
    for x, y in ((-5.4, -1.2), (5.0, -4.6), (-3.2, -7.6), (3.6, 1.0)):
        bx(s, x, y, 0.4, 0.8, 1.2, 0.8, "glow", glow=True)


def x_tap(s):
    bx(s, 0, -7.0, -1.6, 9.0, 12.0, 1.8, "wood")
    for y in (-5.6, 3.0):
        bx(s, 0, y, -1.6, 9.4, 1.0, 2.2, "acc")
    bx(s, 0, -0.6, 1.0, 2.6, 2.6, 4.4, "acc")
    bx(s, 0, -3.6, 2.6, 1.8, 3.2, 1.8, "acc")
    bx(s, 0, 2.0, 1.0, 0.9, 2.0, 0.9, "acc")
    bx(s, 0, 3.8, 1.0, 4.0, 0.9, 0.9, "acc")
    for y in (-5.0, -6.6):
        bx(s, 0, y, 2.6, 0.8, 0.9, 0.8, "glow", glow=True)


def x_acorn(s):
    slices(s, 0, 2.4, [5.0, 5.6, 5.6, 5.2, 4.6, 3.6, 2.4, 1.0], 1.15, "wood")
    bx(s, 0, 1.8, 0, 6.6, 2.4, 6.6, "dark")
    bx(s, 0, 4.2, 0, 4.6, 1.2, 4.6, "dark")
    seg(s, (0, 5.2), (0.8, 7.6), 0.9, 0.9, "dark")
    for x, z in ((-2.8, 2.0), (2.0, 2.8), (3.0, -1.0), (-1.0, 3.2), (0.6, -3.0)):
        bx(s, x, 3.6, z, 1.4, 1.0, 1.4, "blade")
    ring_xy(s, 0, -3.0, 1.4, 0.4, "glow", n=10, glow=True, z=2.85, depth=0.3)
    bx(s, 0, -4.8, 2.85, 0.4, 3.6, 0.3, "glow", glow=True)


def x_spindle(s):
    seg(s, (0, -9.0), (0, 9.0), 0.9, 0.9, "wood")
    bx(s, 0, -7.6, 0, 5.4, 1.3, 5.4, "blade")
    slices(s, 0, 4.0, [2.2, 3.6, 4.4, 4.6, 4.4, 3.6, 2.2], 1.0, "wrap")
    for k in range(5):
        bx(s, 0, -2.6 + k * 1.2, 0, 4.7 - abs(k - 2) * 0.5, 0.2, 4.7 - abs(k - 2) * 0.5, "acc")
    ball(s, 0, 6.4, 1.3, "dark", n=4)
    bx(s, 0, 6.6, 1.2, 1.0, 0.5, 0.4, "glow", glow=True)
    for sx in (-1, 1):
        for k in range(3):
            path(s, [(sx * 0.8, 6.2 + k * 0.5), (sx * 2.4, 7.4 + k * 0.4), (sx * 3.0, 5.6 + k * 0.6)], [0.35], "dark")
    path(s, [(2.2, 1.0), (4.2, -1.4), (4.6, -5.0)], [0.3], "wrap")


def x_lodestone(s):
    for x, y, z, w, h, d, a in ((0, -5.4, 0, 6.6, 9.0, 5.4, 6), (-1.6, 1.6, 0.4, 4.0, 4.6, 4.0, -22), (1.8, 2.4, -0.2, 3.0, 4.4, 3.4, 28)):
        bx(s, x, y, z, w, h, d, "dark", rots=(("z", a),), pivot=(x, y + h / 2, z))
    for y in (-3.6, 0.2):
        bx(s, 0, y, 0, 7.6, 1.0, 6.2, "blade")
        for sx in (-1, 1):
            bx(s, sx * 3.7, y + 0.1, 3.0, 0.7, 0.7, 0.7, "acc")
    path(s, [(-2.2, 3.6), (-0.4, 1.4), (-1.6, -0.8), (0.8, -3.2), (-0.2, -5.6)], [0.6], "glow", z=2.8, glow=True)
    for x, y in ((3.6, 6.0), (-3.4, 5.2), (4.6, -1.2)):
        seg(s, (x, y), (x + 0.8, y + 1.2), 0.4, 0.4, "glow", glow=True)


def x_warhorn(s):
    n = 9
    pts, ws = [], []
    for k in range(n + 1):
        t = k / n
        a = math.radians(200 - 150 * t)
        pts.append((math.cos(a) * 6.0 + 0.5, math.sin(a) * 6.0 - 1.0))
        ws.append(1.0 + 3.6 * t ** 1.6)
    path(s, pts, ws[1:], "acc")
    for k in (2, 5, 8):
        (x0, y0), (x1, y1) = pts[k], pts[k + 1]
        ln = math.hypot(x1 - x0, y1 - y0)
        nx, ny = -(y1 - y0) / ln, (x1 - x0) / ln
        x, y, w = (x0 + x1) / 2, (y0 + y1) / 2, ws[k] * 0.62 + 0.3
        seg(s, (x - nx * w, y - ny * w), (x + nx * w, y + ny * w), 0.9, ws[k] + 0.4, "blade")
    ex, ey = pts[-1]
    disc(s, ex + 0.6, ey + 0.4, 2.8, 1.2, "gold", z=0.2)
    disc(s, ex + 0.6, ey + 0.4, 2.0, 1.4, "glow", z=0.25, glow=True)
    path(s, [(pts[1][0], pts[1][1] - 0.6), (-1.0, -6.4), (3.4, -6.6), (pts[7][0], pts[7][1] - 1.6)], [0.7], "wrap")


# ================================================================== the roster (docs/RELICS.md)
# id, name, slot, rarity, faction, builder, palette overrides
ITEMS = [
    ("brigands_knuckle_ring", "Brigand's Knuckle-Ring", "ring", "U", "Brigands", r_knuckle, None),
    ("tunnel_rats_band", "Tunnel Rat's Band", "ring", "U", "Delvers", r_tunnel, None),
    ("gravediggers_loop", "Gravedigger's Loop", "ring", "U", "Grave-born", r_gravedigger, None),
    ("spore_stained_ring", "Spore-Stained Ring", "ring", "U", "Sporefolk", r_spore, {"blade": "tarnished"}),
    ("bowstring_ring", "Bowstring Ring", "ring", "U", "Sky Legion", r_bowstring, {"blade": "bone", "wrap": "brown_leather"}),
    ("iron_thumb_ring", "Iron Thumb-Ring", "ring", "U", "Fallen Order", r_thumb, {"dark": "worn_iron"}),
    ("knotted_bone_ring", "Knotted Bone Ring", "ring", "U", "Blightkin", r_bone_knot, {"blade": "bone"}),
    ("corsairs_doubloon", "Corsair's Doubloon", "ring", "R", "Corsairs", r_doubloon, None),
    ("tarnished_signet", "Tarnished Signet", "ring", "R", "Fallen Order", r_signet, None),
    ("ember_coil", "Ember Coil", "ring", "R", "Ash Legion", r_ember_coil, None),
    ("briar_band", "Briar Band", "ring", "R", "Thornborn", r_briar, None),
    ("frostbitten_ring", "Frostbitten Ring", "ring", "R", "Rimebound", r_frostbite, None),
    ("hollow_eye_ring", "Hollow-Eye Ring", "ring", "R", "Voidborn", r_hollow_eye, None),
    ("salt_khans_seal", "Salt Khan's Seal", "ring", "E", "Salt-Cursed", r_salt_khan, None),
    ("chitin_loop", "Chitin Loop", "ring", "E", "Brood", r_chitin, None),
    ("rime_band", "Rime Band", "ring", "E", "Rimebound", r_rime_band, None),
    ("marksmans_gyre", "Marksman's Gyre", "ring", "E", "Sky Legion", r_gyre, None),
    ("ring_of_the_drowned_god", "Ring of the Drowned God", "ring", "L", "Corsairs", r_drowned, None),
    ("ring_of_the_ninth_pyre", "Ring of the Ninth Pyre", "ring", "L", "Ash Legion", r_ninth_pyre, None),
    ("wardens_oathring", "Warden's Oathring", "ring", "L", "Fallen Order", r_oathring, None),

    ("wolf_tooth_necklace", "Wolf-Tooth Necklace", "amulet", "U", "Brigands", a_wolf_tooth, {"acc": "bone"}),
    ("miners_medallion", "Miner's Medallion", "amulet", "U", "Delvers", a_miner, None),
    ("shell_pendant", "Shell Pendant", "amulet", "U", "Corsairs", a_shell, {"acc": "bone", "blade": "pale_wood"}),
    ("grave_candle_pendant", "Grave Candle Pendant", "amulet", "U", "Grave-born", a_grave_candle, None),
    ("spore_bead_string", "Spore Bead String", "amulet", "U", "Sporefolk", a_spore_beads, None),
    ("thorn_choker", "Thorn Choker", "amulet", "U", "Thornborn", a_thorn_choker, None),
    ("ash_prayer_beads", "Ash Prayer Beads", "amulet", "U", "Ash Legion", a_ash_beads, None),
    ("moonpetal_locket", "Moonpetal Locket", "amulet", "R", "Sky Legion", a_moonpetal, {"glow": "g_moon", "blade": "silver"}),
    ("legion_sun_disc", "Legion Sun-Disc", "amulet", "R", "Salt-Cursed", a_sun_disc, None),
    ("frozen_tear", "Frozen Tear", "amulet", "R", "Rimebound", a_frozen_tear, None),
    ("brood_mothers_fang", "Brood Mother's Fang", "amulet", "R", "Brood", a_brood_fang, None),
    ("gilded_pyx", "Gilded Pyx", "amulet", "R", "Fallen Order", a_pyx, None),
    ("void_glass_shard", "Void-Glass Shard", "amulet", "R", "Voidborn", a_void_shard, None),
    ("augurs_ember", "Augur's Ember", "amulet", "E", "Ash Legion", a_augur, None),
    ("briar_heart", "Briar Heart", "amulet", "E", "Thornborn", a_briar_heart, None),
    ("gryphon_torc", "Gryphon Torc", "amulet", "E", "Sky Legion", a_gryphon_torc, None),
    ("bulwark_gorget", "Bulwark Gorget", "amulet", "E", "Fallen Order", a_gorget, {"wrap": "brown_leather"}),
    ("last_vigil_reliquary", "Last Vigil Reliquary", "amulet", "L", "Fallen Order", a_last_vigil, None),
    ("heart_of_the_hive", "Heart of the Hive", "amulet", "L", "Brood", a_hive_heart, None),
    ("salt_saints_censer", "Salt Saint's Censer", "amulet", "L", "Salt-Cursed", a_censer, None),

    ("poachers_rabbit_foot", "Poacher's Rabbit Foot", "charm", "U", "Brigands", c_rabbit_foot, {"wrap": "fur", "acc": "bone"}),
    ("delvers_lamp", "Delver's Lamp", "charm", "U", "Delvers", c_lamp, None),
    ("loaded_dice", "Loaded Dice", "charm", "U", "Corsairs", c_dice, {"acc": "bone"}),
    ("knucklebone_charm", "Knucklebone Charm", "charm", "U", "Grave-born", c_knucklebone, {"acc": "bone"}),
    ("bundle_of_briar_twigs", "Bundle of Briar Twigs", "charm", "U", "Thornborn", c_twigs, {"wrap": "brown_leather"}),
    ("snow_hares_tail", "Snow Hare's Tail", "charm", "U", "Rimebound", c_hare_tail, {"wrap": "white_cloth"}),
    ("ash_stamped_token", "Ash-Stamped Token", "charm", "U", "Ash Legion", c_token, None),
    ("spore_pouch", "Spore Pouch", "charm", "R", "Sporefolk", c_spore_pouch, None),
    ("harpy_feather", "Harpy Feather", "charm", "R", "Sky Legion", c_harpy_feather, {"blade": "fur"}),
    ("smugglers_purse", "Smuggler's Purse", "charm", "R", "Brigands", c_purse, None),
    ("void_marble", "Void Marble", "charm", "R", "Voidborn", c_void_marble, None),
    ("salt_ward", "Salt Ward", "charm", "R", "Salt-Cursed", c_salt_ward, None),
    ("grub_lantern", "Grub Lantern", "charm", "R", "Brood", c_grub_lantern, None),
    ("kraken_eye", "Kraken Eye", "charm", "E", "Corsairs", c_kraken_eye, {"acc": "bone"}),
    ("corsairs_compass", "Corsair's Compass", "charm", "E", "Corsairs", c_compass, None),
    ("blight_vial", "Blight Vial", "charm", "E", "Blightkin", c_blight_vial, None),
    ("reliquary_finger_bone", "Reliquary Finger-Bone", "charm", "E", "Grave-born", c_finger_bone, None),
    ("gryphon_plume", "Gryphon Plume", "charm", "L", "Sky Legion", c_gryphon_plume, None),
    ("delvers_last_pick", "Delver's Last Pick", "charm", "L", "Delvers", c_last_pick, None),
    ("rift_key", "Rift Key", "charm", "L", "Voidborn", c_rift_key, None),

    ("barrow_kings_signet", "Barrow King's Signet", "relic", "L", "Grave-born", x_barrow_signet, None),
    ("rime_hourglass", "Rime Hourglass", "relic", "L", "Rimebound", x_hourglass, None),
    ("void_pearl", "Void Pearl", "relic", "L", "Voidborn", x_void_pearl, None),
    ("mantis_molt", "Mantis Molt", "relic", "L", "Brood", x_mantis_molt, None),
    ("spore_heart", "Spore Heart", "relic", "L", "Sporefolk", x_spore_heart, {"acc": "crimson"}),
    ("legions_brand", "Legion's Brand", "relic", "L", "Ash Legion", x_brand, None),
    ("thornborn_rose", "Thornborn Rose", "relic", "L", "Thornborn", x_rose, {"acc": "crimson"}),
    ("chimera_gland", "Chimera Gland", "relic", "L", "Blightkin", x_gland, {"acc": "venom"}),
    ("kiln_fathers_coal", "Kiln-Father's Coal", "relic", "L", "Foundry", x_coal, None),
    ("pale_abbots_wick", "Pale Abbot's Wick", "relic", "L", "Crypt", x_wick, None),
    ("hangmans_noose", "Hangman's Noose", "relic", "L", "Gallows Hill", x_noose, None),
    ("cask_mothers_tap", "Cask Mother's Tap", "relic", "L", "Drowned Cellar", x_tap, None),
    ("mosskings_acorn", "Mossking's Acorn", "relic", "L", "Rotwood", x_acorn, None),
    ("silk_matrons_spindle", "Silk Matron's Spindle", "relic", "L", "Silk Archive", x_spindle, None),
    ("stormspire_lodestone", "Stormspire Lodestone", "relic", "L", "Stormspire", x_lodestone, None),
    ("warhorn_of_the_last_keep", "Warhorn of the Last Keep", "relic", "L", "Last Keep", x_warhorn, None),
]

RARITY = {"U": ("Uncommon", (85, 255, 85)), "R": ("Rare", (85, 205, 255)), "E": ("Epic", (200, 120, 255)),
          "L": ("Legendary", (255, 170, 40))}
SLOTS = [("ring", "Rings"), ("amulet", "Amulets"), ("charm", "Charms"), ("relic", "Relics")]


def build(spec):
    iid, name, slot, rar, faction, fn, over = spec
    s = Sword(iid)
    fn(s)
    s.shaders = theme(iid, faction, over).shaders
    return s


def export(s, folder):
    img, tris = s.build()
    os.makedirs(folder, exist_ok=True)
    img.save(os.path.join(folder, "%s_3d.png" % s.name))
    V.write_obj(V.Path(os.path.join(folder, "%s.obj" % s.name)), tris)
    return sum(len(t) for t in tris.values())


def sheet(specs):
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 15)
    small = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 12)
    big = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 26)
    T, cols, lab = 176, 10, 40
    blocks = []
    for slot, title in SLOTS:
        here = [sp for sp in specs if sp[2] == slot]
        if here:
            blocks.append((title, here))
    H = sum(44 + ((len(h) + cols - 1) // cols) * (T + lab) for _, h in blocks) + 20
    out = Image.new("RGB", (cols * T + 40, H), (22, 19, 18))
    d = ImageDraw.Draw(out)
    y = 12
    for title, here in blocks:
        d.text((20, y), title, font=big, fill=(236, 200, 150))
        y += 44
        for k, (iid, name, slot, rar, faction, fn, over) in enumerate(here):
            x0, y0 = 20 + (k % cols) * T, y + (k // cols) * (T + lab)
            col = RARITY[rar][1]
            d.rectangle([x0 + 4, y0 + 4, x0 + T - 4, y0 + T - 4], fill=(38, 33, 31), outline=tuple(c // 2 for c in col), width=2)
            p = os.path.join(OUT, "shot_%s.png" % iid)
            if os.path.exists(p):
                im = Image.open(p).convert("RGBA").resize((T - 16, T - 16), Image.LANCZOS)
                out.paste(im, (x0 + 8, y0 + 8), im)
            d.text((x0 + 6, y0 + T - 2), name, font=font, fill=col)
            d.text((x0 + 6, y0 + T + 16), "%s · %s" % (RARITY[rar][0], FROM.get(faction, faction)), font=small, fill=(160, 150, 140))
        y += ((len(here) + cols - 1) // cols) * (T + lab)
    path = os.path.join(W.GAME, "tools/renders/curios.png")
    out.save(path)
    print("sheet", path)


# ================================================================== into the game

# stats per item (keys as the mod reads them; % keys are percent) and what an epic / legendary / relic does
S = {
    "brigands_knuckle_ring": {"dmg%": 3}, "tunnel_rats_band": {"move%": 5}, "gravediggers_loop": {"armour%": 6},
    "spore_stained_ring": {"mana_regen%": 3}, "bowstring_ring": {"arrow%": 3}, "iron_thumb_ring": {"kb%": 10},
    "knotted_bone_ring": {"thrall_dmg%": 3}, "corsairs_doubloon": {"luck": 1, "move%": 4},
    "tarnished_signet": {"armour%": 6, "kb%": 6}, "ember_coil": {"spell%": 3, "mana_regen%": 2},
    "briar_band": {"heal%": 3, "health%": 2}, "frostbitten_ring": {"health%": 3, "tough%": 3},
    "hollow_eye_ring": {"speed%": 5, "health%": -1}, "salt_khans_seal": {"dmg%": 4, "speed%": 2},
    "chitin_loop": {"tough%": 5, "speed%": 5}, "rime_band": {"health%": 4, "armour%": 4},
    "marksmans_gyre": {"arrow%": 6}, "ring_of_the_drowned_god": {"armour%": 4, "health%": 4},
    "ring_of_the_ninth_pyre": {"spell%": 4, "mana_regen%": 2}, "wardens_oathring": {"armour%": 7, "kb%": 9},
    "wolf_tooth_necklace": {"health%": 3}, "miners_medallion": {"tough%": 10}, "shell_pendant": {"mana": 12},
    "grave_candle_pendant": {"heal%": 3}, "spore_bead_string": {"mana_regen%": 3}, "thorn_choker": {"armour%": 6},
    "ash_prayer_beads": {"spell%": 3}, "moonpetal_locket": {"mana": 4, "mana_regen%": 3},
    "legion_sun_disc": {"spell%": 3, "health%": 2}, "frozen_tear": {"health%": 4, "kb%": 2},
    "brood_mothers_fang": {"thrall_dmg%": 3, "thrall_hp%": 3}, "gilded_pyx": {"heal%": 4, "mana": 4},
    "void_glass_shard": {"spell%": 6, "health%": -1.5}, "augurs_ember": {"spell%": 6},
    "briar_heart": {"health%": 3, "mana_regen%": 3}, "gryphon_torc": {"speed%": 4, "move%": 4},
    "bulwark_gorget": {"armour%": 8, "tough%": 8}, "last_vigil_reliquary": {"spell%": 3, "health%": 3},
    "heart_of_the_hive": {"thrall_dmg%": 4, "health%": 2}, "salt_saints_censer": {"heal%": 4, "mana": 4},
    "poachers_rabbit_foot": {"luck": 1.5}, "delvers_lamp": {"tough%": 10}, "loaded_dice": {"coins%": 10},
    "knucklebone_charm": {"ash%": 6}, "bundle_of_briar_twigs": {"stamina_regen%": 10},
    "snow_hares_tail": {"safe_fall": 6}, "ash_stamped_token": {"elite_dmg%": 6},
    "spore_pouch": {"health%": 2, "mana_regen%": 3}, "harpy_feather": {"safe_fall": 5, "move%": 3},
    "smugglers_purse": {"coins%": 11, "luck": 0.5}, "void_marble": {"stamina_regen%": 6, "dodge_cost%": 10},
    "salt_ward": {"poison_short%": 25, "health%": 2}, "grub_lantern": {"tough%": 15},
    "kraken_eye": {"oxygen": 3, "swim%": 45}, "corsairs_compass": {"luck": 1.5, "move%": 5},
    "blight_vial": {"health%": 6}, "reliquary_finger_bone": {"ash%": 12}, "gryphon_plume": {"move%": 10},
    "delvers_last_pick": {"tough%": 8, "mining%": 26}, "rift_key": {"move%": 10}, "barrow_kings_signet": {"health%": 3},
    "rime_hourglass": {"armour%": 6}, "void_pearl": {"move%": 5}, "mantis_molt": {"speed%": 3},
    "spore_heart": {"health%": 3}, "legions_brand": {"dmg%": 3}, "thornborn_rose": {"armour%": 6},
    "chimera_gland": {"health%": 3}, "kiln_fathers_coal": {"dmg%": 3}, "pale_abbots_wick": {"heal%": 3},
    "hangmans_noose": {"kb%": 10}, "cask_mothers_tap": {"health%": 3}, "mosskings_acorn": {"tough%": 10},
    "silk_matrons_spindle": {"move%": 5}, "stormspire_lodestone": {"speed%": 3},
    "warhorn_of_the_last_keep": {"health%": 3},
}
FX = {
    "salt_khans_seal": "Kills give +10% move speed for 3 s",
    "chitin_loop": "Every 5th hit gives back a little stamina",
    "rime_band": "Whoever hits you is slowed for 1 s (10 s cooldown)",
    "marksmans_gyre": "Fully drawn arrows go through one enemy",
    "ring_of_the_drowned_god": "Breathe underwater and swim fast; +15% damage while wet",
    "ring_of_the_ninth_pyre": "Every 4th spell costs no mana and hits 50% harder",
    "wardens_oathring": "A blocked hit taunts enemies within 8 blocks and gives 2 hearts of absorption (8 s cooldown)",
    "augurs_ember": "Spells set the target on fire for 2 s",
    "briar_heart": "Each kill heals half a heart",
    "gryphon_torc": "Dodges cost 25% less stamina",
    "bulwark_gorget": "+20% threat: monsters pick you first",
    "last_vigil_reliquary": "Below 30% health a soul shield absorbs 6 hearts (2 min cooldown)",
    "heart_of_the_hive": "A thrall that dies bursts into 3 broodlings for 8 s",
    "salt_saints_censer": "Your heals also clear one bad effect and give the ally +20% damage for 3 s",
    "grub_lantern": "Night vision underground",
    "kraken_eye": "Monsters in water glow for you",
    "corsairs_compass": "Points to the nearest unlooted structure chest",
    "blight_vial": "Immune to poison; your hits rot the foe for 3 s (a quarter of the hit, undead too)",
    "reliquary_finger_bone": "Undead deal 10% less damage to you",
    "gryphon_plume": "Double jump; slow fall while holding jump",
    "delvers_last_pick": "Mined ore: 20% chance of a double drop; breaking ore shows ore within 6 blocks for 5 s (30 s cooldown)",
    "rift_key": "Mark a spot; use again to rift back to it (5 min cooldown)",
    "barrow_kings_signet": "Kills are souls; at 10 / 8 / 6 souls a ghost warrior fights with you for 15 / 20 / 25 s (III: two ghosts)",
    "rime_hourglass": "A killing blow freezes you in ice for 2 s, then you stand up at 30 / 40 / 50% health (10 / 8 / 6 min cooldown)",
    "void_pearl": "Dodges blink 3 blocks further and leave a rift that slows for 2 / 3 / 4 s (III: it also hurts)",
    "mantis_molt": "A dodge that slips an attack gives back 50 / 75 / 100% of its stamina; your next hit staggers",
    "spore_heart": "Getting hit puffs poison spores round you (5 / 4 / 3 s cooldown; III: bigger cloud)",
    "legions_brand": "Every 3rd combo hit bursts into teal fire for 30 / 45 / 60% extra damage",
    "thornborn_rose": "Hits heal 3 / 4 / 5% of the damage dealt; blocking reflects 10 / 15 / 20%",
    "chimera_gland": "Each kill gives a random buff for 6 / 8 / 10 s (III: two at once)",
    "kiln_fathers_coal": "[V] Become molten for 6 / 8 / 10 s: hits burn, +15 / 20 / 25% damage, immune to fire (90 s cooldown)",
    "pale_abbots_wick": "[V] A candle ward (6 blocks): allies inside heal 0.5 / 0.75 / 1 heart a second for 5 s (60 s cooldown)",
    "hangmans_noose": "[V] Yank one enemy to you and stun it 1 / 1.5 / 2 s; bosses aren't stunned (20 s cooldown)",
    "cask_mothers_tap": "Potions you drink also work on allies within 6 / 8 / 10 blocks at 50 / 75 / 100%",
    "mosskings_acorn": "[V] Roots burst up and hold enemies within 4 blocks for 2 / 2.5 / 3 s (40 s cooldown)",
    "silk_matrons_spindle": "Dodging leaves a web: the first enemy in it is bound for 1 / 1.5 / 2 s (6 s cooldown)",
    "stormspire_lodestone": "Every 10 / 8 / 6 s your next hit calls lightning that jumps to 2 / 3 / 4 enemies",
    "warhorn_of_the_last_keep": "[V] Party within 12 blocks gets +10 / 15 / 20% damage and +25% knockback resistance for 10 s (60 s cooldown)",
}
SLOT_TAG = {"ring": "ring", "amulet": "necklace", "charm": "charm", "relic": "relic"}
SLOT_POSE = {"ring": (38, -24), "amulet": (8, -22), "charm": (12, -28), "relic": (12, -30)}   # tip back, yaw (deg)


def to_game():
    import gui3d
    lang = json.load(open(W.ASSETS + "lang/en_us.json", encoding="utf-8"))
    rows, tags = [], {}
    for sp in ITEMS:
        iid, name, slot, rar, faction, fn, over = sp
        W.export(build(sp), iid, preview=False)
        tip, yaw = SLOT_POSE[slot]
        r = gui3d.mul(gui3d.rx(math.radians(tip)), gui3d.ry(math.radians(yaw)))
        sc, tr = gui3d.fit(iid, r)
        rot = gui3d.euler_xyz(r)
        disp = {"gui": {"rotation": rot, "translation": tr, "scale": [round(sc, 4)] * 3},
                "ground": {"rotation": rot, "translation": [round(v * 0.5, 3) for v in tr[:2]] + [0], "scale": [round(sc * 0.5, 4)] * 3},
                "fixed": {"rotation": rot, "translation": tr, "scale": [round(sc, 4)] * 3}}
        for hand in ("thirdperson_righthand", "thirdperson_lefthand", "firstperson_righthand", "firstperson_lefthand"):
            disp[hand] = {"rotation": rot, "translation": [0, 2, 0], "scale": [round(sc * 0.4, 4)] * 3}
        W.G.dump(W.ASSETS + "models/item/%s.json" % iid,
                 {"loader": "neoforge:separate_transforms", "gui_light": "side",
                  "base": {"loader": "neoforge:obj", "model": "ashbound:models/mesh/%s.obj" % iid, "flip_v": True, "display": disp},
                  "perspectives": {}})
        lang["item.ashbound." + iid] = name
        # as worn (client/WornCurios.java): amulets get their own mesh with the chain laid on the chest
        mesh = iid
        if slot == "amulet":
            mesh = iid + "_worn"
            W.export(build_worn(sp), mesh, preview=False)
            W.G.dump(W.ASSETS + "models/item/%s.json" % mesh,
                     {"loader": "neoforge:obj", "model": "ashbound:models/mesh/%s.obj" % mesh, "flip_v": True})
        lo, hi = mesh_bounds(mesh)
        rows.append({"id": iid, "name": name, "slot": slot, "rarity": RARITY[rar][0].lower(), "faction": FROM.get(faction, faction),
                     "stats": S[iid], "effect": FX.get(iid, ""),
                     "worn": {"model": mesh, "scale": WORN_SCALE[slot],
                              "top": [round((lo[0] + hi[0]) / 2, 3), round(hi[1], 3), round((lo[2] + hi[2]) / 2, 3)],
                              "depth": round(hi[2] - lo[2], 3)}})
        tags.setdefault(SLOT_TAG[slot], []).append("ashbound:" + iid)
        print("game", rar, iid)
    res = os.path.join(W.GAME, "src/main/resources/")
    W.G.dump(res + "ashbound/curios.json", rows)
    for tag, ids in tags.items():
        W.G.dump(res + "data/curios/tags/item/%s.json" % tag, {"replace": False, "values": ids})
    # the slots a player gets: two rings, an amulet, a charm and our relic slot
    W.G.dump(res + "data/ashbound/curios/slots/ring.json", {"size": 2})
    W.G.dump(res + "data/ashbound/curios/slots/relic.json",
             {"size": 1, "order": 90, "icon": "ashbound:slot/empty_relic_slot", "validators": ["curios:tag"]})
    W.G.dump(res + "data/ashbound/curios/entities/ashbound_player.json",
             {"entities": ["player"], "slots": ["ring", "necklace", "charm", "relic"]})
    lang["key.ashbound.relic_power"] = "Relic power (sneak: Rift Key)"
    lang["key.categories.ashbound"] = "Ashbound"
    lang["curios.identifier.relic"] = "Relic"
    lang["curios.modifiers.relic"] = "When worn as a relic:"
    W.G.dump(W.ASSETS + "lang/en_us.json", lang)
    relic_icon()


def mesh_bounds(mesh):
    """a written mesh's bounds back in model pixels (voxsword.to_item undone)"""
    vs = [tuple(map(float, l.split()[1:4])) for l in open(W.ASSETS + "models/mesh/%s.obj" % mesh) if l.startswith("v ")]
    px = [((x - 0.5) * 16, (y - 6.25 / 16) * 16 + 0.8, (z - 0.5) * 16) for x, y, z in vs]
    return [min(p[i] for p in px) for i in range(3)], [max(p[i] for p in px) for i in range(3)]


def relic_icon():
    """the empty relic slot: a faint eight-pointed star, like Curios' own slot outlines"""
    from PIL import Image
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = im.load()
    for k in range(-5, 6):
        px[8 + k, 8] = px[8, 8 + k] = (55, 55, 55, 255)
    for k in range(-3, 4):
        px[8 + k, 8 + k] = px[8 + k, 8 - k] = (55, 55, 55, 255)
    os.makedirs(W.ASSETS + "textures/slot", exist_ok=True)
    im.save(W.ASSETS + "textures/slot/empty_relic_slot.png")


def build_worn(spec):
    """the piece as drawn on the body: amulets with their chain laid on the chest, the rest as they are"""
    WORN.clear()
    if spec[2] == "amulet":
        WORN["amulet"] = WORN_SCALE["amulet"]
    try:
        s = build(spec)
        if WORN:
            s.name = spec[0] + "_worn"
        return s
    finally:
        WORN.clear()


def worn_concept(ids):
    """tools/renders/curios/worn_*.png: a player wearing an amulet, two rings, a charm and a relic"""
    mesh = os.path.join(OUT, "mesh")
    pieces, rings = [], 0
    for iid in ids:
        sp = next(sp for sp in ITEMS if sp[0] == iid)
        s = build_worn(sp)
        export(s, mesh)
        pieces.append({"obj": os.path.join(mesh, s.name + ".obj"), "png": os.path.join(mesh, s.name + "_3d.png"),
                       "slot": sp[2], "scale": WORN_SCALE[sp[2]], "index": rings if sp[2] == "ring" else 0})
        rings += sp[2] == "ring"
    job = os.path.join(OUT, "worn.json")
    json.dump({"res": 640, "out": OUT, "pieces": pieces}, open(job, "w"))
    r = subprocess.run([W.BLENDER, "-b", "-P", os.path.join(W.GAME, "tools/blender/curio_worn.py"), "--", job],
                       capture_output=True, text=True)
    print(r.stdout[-600:] if r.returncode == 0 else r.stderr[-3000:] + r.stdout[-3000:])


def main():
    if "--export" in sys.argv:
        return to_game()
    if "--worn" in sys.argv:
        return worn_concept([a for a in sys.argv[1:] if not a.startswith("--")] or
                            ["miners_medallion", "brigands_knuckle_ring", "rime_band", "blight_vial", "warhorn_of_the_last_keep"])
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    specs = [sp for sp in ITEMS if not only or sp[0] in only or sp[2] in only]
    mesh = os.path.join(OUT, "mesh")
    for sp in specs:
        print(sp[3], sp[0], export(build(sp), mesh), "tris")
    if "--sheet" in sys.argv:
        job = os.path.join(OUT, "batch.json")
        json.dump({"mesh": mesh, "out": OUT, "items": [[sp[0], sp[2]] for sp in specs], "res": 320}, open(job, "w"))
        r = subprocess.run([W.BLENDER, "-b", "-P", os.path.join(W.GAME, "tools/blender/curio_shots.py"), "--", job],
                           capture_output=True, text=True)
        if r.returncode:
            print(r.stderr[-2000:])
        sheet(ITEMS)


if __name__ == "__main__":
    main()
