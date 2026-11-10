"""Every dungeon's weapons, from the gear table (tools/gear.py), in the chunky style of the approved Kiln line
(E:/Ashbound/tools/voxsword.py boxes and pixel shaders). A weapon is its TYPE's template (sword, dagger, hammer,
spear, two-hander, shield, bow, the three staffs) in its DUNGEON's theme: the gate's metals and leathers, its
glow, its emblem (a cask head, a noose, antlers, a candle, a beak, a blank mask, a skull, an anvil, a snow
crystal, a spider) and its trim (hoops, rope, fungus, wax drips, stitches, crystals, saw teeth, hot seams,
icicles, silk). The name picks the shape (a boathook, a cleaver, a bell for a maul head); boss weapons come out
bigger, with more glow and the emblem worked in larger.

The old weapons (`*` in GEAR.md) are copied over from E:/Ashbound as they were.

    python tools/weaponforge.py [gates or ids...] [--icons] [--sheet]
        writes models/mesh/<id>.obj, textures/item/<id>_3d.png, the item models; --icons renders the menu icons
        (Blender, batched), --sheet a contact sheet per gate in tools/renders/weapons_<gate>.png
"""
import json
import math
import os
import shutil
import subprocess
import sys
import zlib

sys.path.insert(0, 'E:/Ashbound/tools')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image  # noqa: E402

import voxsword as V  # noqa: E402
from voxsword import Sword, C, ramp, shade, fbm, h3, metal_shader, wrap_shader  # noqa: E402
import gear as G  # noqa: E402

GAME = G.GAME
ASSETS = G.ASSETS
OLD = 'E:/Ashbound/src/main/resources/assets/ashbound/'
VOX = 'E:/Ashbound/tools/renders/vox/'
BLENDER = 'E:/Steam/steamapps/common/Blender/blender.exe'
TO_ITEM = V.to_item


# ================================================================== shaders shared by every theme

def wood_shader(R):
    def sh(p, n, b, key, i, j, w, h, fr):
        x, y, z = p
        along = y if key in ("n", "s", "e", "w") else x
        v = 0.5 + 0.18 * math.sin(x * 3.1 + z * 2.3 + fbm(x * 0.5, y * 0.12, z * 0.5) * 6) + 0.1 * (fbm(x, y * 0.3, z) - 0.5)
        if key == "u":
            v += 0.08
        if i == 0 or j == 0:
            v += 0.1
        if i == w - 1 or j == h - 1:
            v -= 0.14
        return shade(R, v, i, j)
    return sh


def matte_shader(R, spots=0.0, spot_ramp=None):
    def sh(p, n, b, key, i, j, w, h, fr):
        x, y, z = p
        v = 0.5 + 0.12 * n[1] + 0.22 * (fbm(x * 0.8, y * 0.8, z * 0.8) - 0.5)
        if i == 0 or j == 0:
            v += 0.1
        if i == w - 1 or j == h - 1:
            v -= 0.14
        if spots and fbm(x * 1.3 + 7, y * 1.3, z * 1.3) > 1 - spots:
            return shade(spot_ramp or R, 0.3, i, j)
        return shade(R, v, i, j)
    return sh


def glow_shader(R, base=0.58, var=0.32):
    def sh(p, n, b, key, i, j, w, h, fr):
        return shade(R, base + var * fbm(p[0] * 0.8, p[1] * 0.8 + fr * 0.5, p[2] * 0.8), i, j)
    return sh


def void_shader(R):
    def sh(p, n, b, key, i, j, w, h, fr):
        return shade(R, 0.02, i, j)
    return sh


# ================================================================== themes

class Theme:
    """a gate's look: ramps for blade/dark/wrap/wood/glow/acc, its emblem and trim"""

    def __init__(self, gate, blade, dark, wrap, wood, glow, acc, band=None, scars=0.04):
        self.gate = gate
        self.R = dict(blade=blade, dark=dark, wrap=wrap, wood=wood, glow=glow, acc=acc)
        self.shaders = {
            "blade": metal_shader(blade, scars=scars), "dark": metal_shader(dark), "wrap": wrap_shader(wrap, band=band or dark[3]),
            "wood": wood_shader(wood), "glow": glow_shader(glow), "white": glow_shader(glow, 0.86, 0.12),
            "acc": matte_shader(acc), "void": void_shader(dark), "gold": metal_shader(GOLD),
        }

    def emblem(self, s, cx, y, size, z, boss):
        pass

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        """decoration along a blade/haft between y0..y1 (half = half its width)"""
        pass


GOLD = ramp("#4a2e08", "#7a4c10", "#a87018", "#d0961f", "#ecbc34", "#ffdc6a", "#fff2b8")


def bx(s, cx, y0, cz, sx, sy, sz, mat, glow=False, rots=(), pivot=None, tag=None):
    kw = {"group": "fire"} if glow else {}
    if rots:
        kw["rots"] = rots
        kw["pivot"] = pivot if pivot is not None else (cx, y0, cz)
    return s.add(C(cx, y0, cz, sx, sy, sz), mat, tag=tag, **kw)


def ring_xy(s, cx, cy, r, thick, mat, n=12, glow=False, z=0.0, depth=None):
    """a closed ring in the blade's plane, its segments overlapping so it reads solid"""
    n = max(n, int(r * 3))
    pts = [(cx + math.cos(2 * math.pi * k / n) * r, cy + math.sin(2 * math.pi * k / n) * r) for k in range(n)]
    for k in range(n):
        a, b = pts[k], pts[(k + 1) % n]
        ex = ((b[0] - a[0]) * 0.15, (b[1] - a[1]) * 0.15)
        seg(s, (a[0] - ex[0], a[1] - ex[1]), (b[0] + ex[0], b[1] + ex[1]), thick, depth or thick, mat, z, glow)


def seg(s, a, b, w, d, mat, z=0.0, glow=False, tag=None):
    """a box from point a to b (x, y px)"""
    dx, dy = b[0] - a[0], b[1] - a[1]
    ln = math.hypot(dx, dy)
    ang = math.degrees(math.atan2(-dx, dy))
    kw = {"group": "fire"} if glow else {}
    s.add(((a[0] - w / 2, a[1], z - d / 2), (w, ln + 0.05, d)), mat, rots=(("z", ang),), pivot=(a[0], a[1], z), tag=tag, **kw)


# ---------------------------------------------------------------- the ten gates

class Cellar(Theme):
    def __init__(self):
        super().__init__("cellar",
                         blade=ramp("#1a2422", "#2a3836", "#3e504c", "#566c66", "#728a82", "#94aaa0", "#bcccc2", "#e0ebe2"),
                         dark=ramp("#140c08", "#24150c", "#3a2212", "#56321a", "#744424", "#8e5a32"),
                         wrap=ramp("#0e0b08", "#1c1610", "#2c2218", "#3e3022", "#52402c"),
                         wood=ramp("#1a0e06", "#2a180c", "#3c2412", "#52321a", "#6a4424", "#845832"),
                         glow=ramp("#2a3204", "#4a5a08", "#728a10", "#a0bc22", "#c8e04a", "#e8f68a", "#faffd0"),
                         acc=ramp("#3e2814", "#5a3c1e", "#7a5430", "#9a7044", "#bc8e5c", "#d8ac7a"))

    def emblem(self, s, cx, y, size, z, boss):
        # a cask head: an oak disc in an iron hoop, the bung corked
        r = size / 2
        bx(s, cx, y - r * 0.8, 0, size * 0.9, size * 1.6 * 0.5 + r * 0.6, z, "wood")
        ring_xy(s, cx, y, r * 0.95, size * 0.16, "dark", 12, depth=z + 0.2)
        bx(s, cx, y - size * 0.12, 0, size * 0.3, size * 0.26, z + 0.6, "acc", tag="cork")
        if boss:
            bx(s, cx, y - size * 0.06, 0, size * 0.14, size * 0.14, z + 0.8, "glow", glow=True)

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        # iron hoops round it and vinegar weeping from a crack
        n = 2 if where != "haft" else 3
        for k in range(n):
            y = y0 + (y1 - y0) * (0.15 + 0.6 * k / max(1, n - 1))
            bx(s, 0, y, 0, half * 2 + 0.5, 0.8, thick + 0.3, "dark", tag="hoop")
        if where == "blade":
            bx(s, -half * 0.4, y0 + (y1 - y0) * 0.3, 0, 0.6, (y1 - y0) * 0.35, thick + 0.06, "glow", glow=True)


class Gallows(Theme):
    def __init__(self):
        super().__init__("gallows",
                         blade=ramp("#0c0c0e", "#16161a", "#222228", "#303038", "#42424c", "#5a5a66", "#7c7c88", "#a6a6b0"),
                         dark=ramp("#100e0c", "#1c1814", "#2a241e", "#3a3229", "#4e4436", "#665a48"),
                         wrap=ramp("#4a3c24", "#66543a", "#857052", "#a48c6a", "#c2aa86"),
                         wood=ramp("#1a1814", "#2a2620", "#3c362e", "#504a40", "#686054", "#80786a"),
                         glow=ramp("#3a0c02", "#6a1a04", "#a03208", "#d85a12", "#ff8a2a", "#ffbe6a", "#ffeac0"),
                         acc=ramp("#3a2e1a", "#56462a", "#76623e", "#988254", "#b8a070", "#d8c290"),
                         band=None)

    def noose(self, s, cx, y, size, z, glow=False):
        # a hemp noose: the loop and its coiled knot above
        ring_xy(s, cx, y, size * 0.42, size * 0.18, "acc", 12, glow=glow, depth=z)
        for k in range(4):
            bx(s, cx, y + size * 0.42 + k * size * 0.17, 0, size * 0.34, size * 0.15, z + 0.2, "wrap")
        bx(s, cx, y + size * 1.1, 0, size * 0.12, size * 0.5, z * 0.8, "acc")

    def emblem(self, s, cx, y, size, z, boss):
        self.noose(s, cx, y, size, z)
        if boss:
            bx(s, cx, y - size * 0.1, 0, size * 0.3, size * 0.3, z - 0.2, "glow", glow=True)

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        # hemp lashed round it, tar burning in the crack, a nail through
        for k in range(3):
            bx(s, 0, y0 + 0.4 + k * 0.9, 0, half * 2 + 0.4, 0.7, thick + 0.25, "wrap")
        if where == "blade":
            seg(s, (0.2, y0 + (y1 - y0) * 0.45), (-0.4, y0 + (y1 - y0) * 0.8), 0.6, thick + 0.06, "glow", glow=True)
            bx(s, half * 0.5, y0 + (y1 - y0) * 0.6, 0, 0.7, 0.7, thick + 0.4, "dark", tag="nail")


class Rotwood(Theme):
    def __init__(self):
        super().__init__("rotwood",
                         blade=ramp("#2e2618", "#4a3e28", "#6a5c3e", "#8c7c58", "#ae9e78", "#cec09a", "#e8dcbc", "#fbf4e0"),
                         dark=ramp("#0e0a08", "#1a1410", "#281e16", "#38291e", "#4a3828", "#5e4834"),
                         wrap=ramp("#1a2410", "#2a3a18", "#3e5424", "#567032", "#6e8a44"),
                         wood=ramp("#140e0a", "#22180e", "#342414", "#48321c", "#5c4226", "#725434"),
                         glow=ramp("#063a2e", "#0e6a50", "#1a9a70", "#36c890", "#6ef0b4", "#b4ffd8", "#f0fff6"),
                         acc=ramp("#4a1e08", "#6e3010", "#94461c", "#b8602a", "#d47e3e", "#ecaa6a"))

    def antler(self, s, cx, y, size, side):
        from voxsword import chain
        chain(s, (cx, y), [(size * 0.5, side * 35, size * 0.18, size * 0.18), (size * 0.45, side * 10, size * 0.15, size * 0.15),
                           (size * 0.35, -side * 20, size * 0.11, size * 0.11)], "blade", tag="antler")
        chain(s, (cx + side * size * 0.25, y + size * 0.3), [(size * 0.3, side * 70, size * 0.1, size * 0.1)], "blade", tag="tine")

    def emblem(self, s, cx, y, size, z, boss):
        bx(s, cx, y - size * 0.15, 0, size * 0.35, size * 0.35, z, "dark")
        for side in (1, -1):
            self.antler(s, cx, y, size * (1.3 if boss else 1.0), side)
        if boss:
            bx(s, cx, y - size * 0.05, 0, size * 0.2, size * 0.2, z + 0.3, "glow", glow=True)

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        # shelf fungus off one side, glowcaps on the other, moss in the joins
        for k in range(2 if where != "haft" else 3):
            y = y0 + (y1 - y0) * (0.2 + 0.3 * k)
            side = 1 if (k + seed) % 2 else -1
            bx(s, side * (half + 0.9), y, 0, 2.0, 0.7, thick + 1.4, "acc", tag="fungus")
            bx(s, side * (half + 0.5), y + 0.7, 0, 1.2, 0.5, thick + 0.8, "acc", tag="fungus")
        bx(s, -half * 0.6, y0 + (y1 - y0) * 0.65, 0.0, 0.8, 0.8, thick + 0.5, "glow", glow=True)
        bx(s, -half * 0.6, y0 + (y1 - y0) * 0.65 + 0.8, 0.0, 1.4, 0.5, thick + 1.0, "glow", glow=True)
        bx(s, 0, y0, 0, half * 2 + 0.3, 0.6, thick + 0.3, "wrap", tag="moss")


class Crypt(Theme):
    def __init__(self):
        super().__init__("crypt",
                         blade=ramp("#24262c", "#3a3d46", "#545864", "#727786", "#959aa8", "#b8bcc8", "#dcdfe6", "#f6f7fa"),
                         dark=ramp("#08080a", "#101014", "#1a1a20", "#26262e", "#34343e", "#46464f"),
                         wrap=ramp("#0c0408", "#180a10", "#26101a", "#361626", "#481e32"),
                         wood=ramp("#0c0908", "#16110e", "#221a14", "#30241c", "#403024", "#523e2e"),
                         glow=ramp("#5a2e04", "#a05a0a", "#e09a1e", "#ffc84a", "#ffe08a", "#fff4c8", "#ffffff"),
                         acc=ramp("#8a8068", "#a89e84", "#c4bba0", "#dad2b8", "#ece6d0", "#faf6e8"))

    def candle(self, s, cx, y, size, z):
        bx(s, cx, y, 0, size * 0.36, size * 0.8, size * 0.36, "acc", tag="wax")
        bx(s, cx + size * 0.12, y + size * 0.3, 0, size * 0.16, size * 0.5, size * 0.42, "acc", tag="drip")
        bx(s, cx, y + size * 0.8, 0, size * 0.12, size * 0.14, size * 0.12, "void")
        bx(s, cx, y + size * 0.9, 0, size * 0.22, size * 0.36, size * 0.22, "white", glow=True, tag="flame")

    def emblem(self, s, cx, y, size, z, boss):
        bx(s, cx, y - size * 0.15, 0, size * 0.8, size * 0.15, z, "dark")
        self.candle(s, cx, y, size * 0.9, z)
        if boss:
            for side in (1, -1):
                self.candle(s, cx + side * size * 0.4, y - size * 0.1, size * 0.6, z)

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        # corpse wax dripped down from the guard and dried in runs
        for k, f in enumerate((0.0, 0.33, 0.7)):
            x = -half + 0.4 + (2 * half - 0.8) * f
            ln = (y1 - y0) * (0.18 + 0.12 * ((k + seed) % 3))
            bx(s, x, y0, 0, 0.7, ln, thick + 0.2, "acc", tag="wax")
            bx(s, x, y0, 0, 0.9, 0.6, thick + 0.3, "acc", tag="wax")
        if where != "blade":
            self.candle(s, half + 0.8, y0, 2.0, thick)


class Plague(Theme):
    def __init__(self):
        super().__init__("plague",
                         blade=ramp("#2a2e30", "#424a4c", "#5e686a", "#7e898a", "#a0aaa9", "#c2cac8", "#e0e6e2", "#f8fbf8"),
                         dark=ramp("#2a1a06", "#4a300c", "#6e4a14", "#946620", "#b88430", "#d8a648"),
                         wrap=ramp("#5e5844", "#7e7860", "#9e9880", "#bab49c", "#d4d0ba"),
                         wood=ramp("#100a06", "#1c120a", "#2a1c10", "#3a2818", "#4c3622", "#60462e"),
                         glow=ramp("#1a3a04", "#2e6206", "#4e900e", "#7ec41e", "#aee84a", "#dcff96", "#f6ffe0"),
                         acc=ramp("#140a06", "#22120a", "#341c10", "#482818", "#5e3622", "#78482e"),
                         scars=0.02)

    def beak(self, s, cx, y, size, z):
        bx(s, cx, y, 0, size * 0.7, size * 0.7, z, "acc", tag="mask")
        for k in range(4):
            w = size * (0.5 - k * 0.11)
            bx(s, cx + size * 0.35 + k * size * 0.22, y + size * 0.1 - k * size * 0.07, 0, size * 0.26, w, w, "acc", tag="beak")
        for side in (1, -1):
            bx(s, cx - size * 0.1, y + size * 0.42, side * z * 0.5, size * 0.22, size * 0.2, 0.3, "glow", glow=True, tag="lens")

    def emblem(self, s, cx, y, size, z, boss):
        self.beak(s, cx, y, size * (1.25 if boss else 1.0), z)

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        # lime gauze bound on, brass clamps, a vial of green clipped to it
        for k in range(2):
            bx(s, 0, y0 + 0.5 + k * 1.1, 0, half * 2 + 0.5, 0.9, thick + 0.3, "wrap", tag="gauze")
        bx(s, 0, y0 + (y1 - y0) * 0.55, 0, half * 2 + 0.3, 0.6, thick + 0.4, "dark", tag="clamp")
        if where != "blade" or boss:
            bx(s, half + 0.9, y0 + (y1 - y0) * 0.3, 0, 1.0, 2.2, 1.0, "glow", glow=True, tag="vial")
            bx(s, half + 0.9, y0 + (y1 - y0) * 0.3 + 2.2, 0, 0.7, 0.5, 0.7, "dark")


class Temple(Theme):
    def __init__(self):
        super().__init__("temple",
                         blade=ramp("#5a5650", "#7a756e", "#9a958c", "#b6b1a8", "#ccc8c0", "#e0ddd6", "#f0eee8", "#ffffff"),
                         dark=ramp("#06060a", "#0c0c14", "#14141e", "#1e1e2a", "#2a2a38", "#3a3a4a"),
                         wrap=ramp("#060a18", "#0e1430", "#1a2244", "#2c3a66", "#46569a"),
                         wood=ramp("#06060a", "#0c0c12", "#14141c", "#1e1e28", "#282836", "#343444"),
                         glow=ramp("#0e3a5a", "#1e6a96", "#3aa6dc", "#6ad2ff", "#a6eaff", "#dcfaff", "#ffffff"),
                         acc=GOLD)

    def mask(self, s, cx, y, size, z):
        bx(s, cx, y, 0, size * 0.8, size, z, "blade", tag="mask")
        bx(s, cx, y + size * 0.15, 0, size * 0.62, size * 0.9, z + 0.3, "blade", tag="mask")
        bx(s, cx, y + size * 0.5, 0, size * 0.55, size * 0.08, z + 0.4, "dark", tag="slit")

    def emblem(self, s, cx, y, size, z, boss):
        self.mask(s, cx, y, size, z)
        if boss:
            for side in (1, -1):
                seg(s, (cx + side * size * 0.4, y + size * 0.4), (cx + side * size * 0.9, y + size * 1.2), size * 0.2, z * 0.7, "glow", glow=True)

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        # mana crystals grown out of it, gold leaf inlay
        for k in range(2 + (1 if boss else 0)):
            y = y0 + (y1 - y0) * (0.25 + 0.25 * k)
            side = 1 if (k + seed) % 2 else -1
            seg(s, (side * half, y), (side * (half + 1.6), y + 2.0), 1.0, 1.0, "glow", glow=True)
        bx(s, 0, y0, 0, half * 2 + 0.3, 0.6, thick + 0.2, "gold")


class Ossuary(Theme):
    def __init__(self):
        super().__init__("ossuary",
                         blade=ramp("#0c0d10", "#15171b", "#1f2228", "#2a2e36", "#383d47", "#4c525e", "#6c7380", "#9aa1ae"),
                         dark=ramp("#2a1c0a", "#4a3414", "#6e4e20", "#94702e", "#ba9444", "#dcbc6a", "#f2dc9a"),
                         wrap=ramp("#120c08", "#1e140e", "#2c1e14", "#3c2a1c", "#4e3826"),
                         wood=ramp("#30281d", "#4a3f2f", "#6a5c44", "#8c7c5c", "#ae9c76", "#cbbb92"),
                         glow=ramp("#0c3a20", "#167a40", "#2ab866", "#6ee6a0", "#c0ffd8", "#f0fff6"),
                         acc=ramp("#30281d", "#4a3f2f", "#6a5c44", "#8c7c5c", "#ae9c76", "#cbbb92", "#e2d6b0"),
                         scars=0.06)

    def skull(self, s, cx, y, size, z):
        bx(s, cx, y + size * 0.25, 0, size, size * 0.75, z, "acc", tag="skull")
        bx(s, cx, y, 0, size * 0.62, size * 0.3, z * 0.85, "acc", tag="skull")
        for side in (1, -1):
            bx(s, cx + side * size * 0.2, y + size * 0.46, 0, size * 0.24, size * 0.2, z + 0.1, "glow", glow=True, tag="socket")

    def emblem(self, s, cx, y, size, z, boss):
        # a cog behind a skull
        for k in range(8):
            a = k * math.pi / 4
            bx(s, cx + math.cos(a) * size * 0.62, y + size * 0.35 + math.sin(a) * size * 0.62 - 0.5, 0, 1.0, 1.0, z - 0.2, "dark")
        self.skull(s, cx, y, size * (0.8 if not boss else 1.0), z)

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        # saw teeth up one edge, brass rivets, a pane of soul glass
        if where == "blade":
            y = y0 + 1
            while y < y1 - 2:
                seg(s, (half - 0.1, y), (half + 1.0, y + 1.0), 0.7, thick * 0.8, "blade")
                y += 1.8
            bx(s, -half * 0.3, y0 + (y1 - y0) * 0.3, 0, 1.0, (y1 - y0) * 0.3, thick + 0.08, "glow", glow=True)
        for y in (y0 + 0.8, y0 + (y1 - y0) * 0.7):
            bx(s, -half + 0.6, y, 0, 0.7, 0.7, thick + 0.3, "dark", tag="rivet")


class Foundry(Theme):
    def __init__(self):
        super().__init__("foundry",
                         blade=ramp("#0c0b0a", "#161412", "#211e1b", "#2d2925", "#3b3631", "#4f4842", "#6a625a", "#948a80"),
                         dark=ramp("#100f0e", "#1b1917", "#272421", "#34302c", "#47413b", "#5e564e", "#7a7065"),
                         wrap=ramp("#120a06", "#1d110a", "#2a1a0f", "#3a2516", "#4c321e"),
                         wood=ramp("#100f0e", "#1b1917", "#272421", "#34302c", "#47413b", "#5e564e"),
                         glow=ramp("#3a0804", "#701204", "#a82406", "#e04a0a", "#ff7a1c", "#ffb04a", "#ffe08a", "#fff6d0"),
                         acc=ramp("#0c0b0a", "#161412", "#211e1b", "#2d2925", "#3b3631", "#4f4842"), scars=0.06)

    def emblem(self, s, cx, y, size, z, boss):
        # the Kiln's anvil
        bx(s, cx + size * 0.1, y + size * 0.62, 0, size * 1.1, size * 0.28, z, "dark")
        bx(s, cx - size * 0.62, y + size * 0.68, 0, size * 0.3, size * 0.16, z * 0.9, "dark")
        bx(s, cx + size * 0.1, y + size * 0.3, 0, size * 0.36, size * 0.34, z * 0.9, "dark")
        bx(s, cx + size * 0.1, y, 0, size * 0.76, size * 0.3, z, "dark")
        if boss:
            bx(s, cx + size * 0.1, y + size * 0.86, 0, size * 0.8, size * 0.12, z + 0.1, "white", glow=True)

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        # a seam that never cooled and nails along it
        if where == "blade":
            bx(s, 0, y0 + 1, 0, 0.8, (y1 - y0) * 0.55, thick + 0.06, "glow", glow=True)
            bx(s, 0.3, y0 + 1 + (y1 - y0) * 0.55, 0, 0.6, (y1 - y0) * 0.25, thick + 0.06, "glow", glow=True)
        y = y0 + 1.5
        while y < y1 - 1:
            bx(s, half * 0.55, y, 0, 0.7, 0.7, thick + 0.15, "dark", tag="nail")
            y += 3.5


class Frost(Theme):
    def __init__(self):
        super().__init__("frost",
                         blade=ramp("#1e3a50", "#2e5470", "#46749a", "#6698be", "#8cbcdc", "#b6dcf0", "#dcf2fc", "#ffffff"),
                         dark=ramp("#141a22", "#202a36", "#2e3a4a", "#3e4e62", "#54687e", "#70869c"),
                         wrap=ramp("#8a929a", "#a6aeb6", "#c0c8ce", "#d8dee2", "#eef2f4"),
                         wood=ramp("#2a3036", "#3a424a", "#4c565e", "#606a72", "#767f86", "#8e969c"),
                         glow=ramp("#0e3a5a", "#1e6a96", "#3fa0d0", "#6fc8f0", "#9ad8ff", "#d4f0ff", "#ffffff"),
                         acc=ramp("#6a2020", "#8a2a26", "#a83a30", "#c44e3e", "#d86a54"))

    def crystal(self, s, cx, y, size, z, glow=True):
        for a in range(0, 180, 60):
            bx(s, cx, y - size / 2, 0, size * 0.18, size, z, "glow", glow=glow, rots=(("z", a),), pivot=(cx, y, 0))

    def emblem(self, s, cx, y, size, z, boss):
        # the procession's pennant on a crossbar, a snow crystal on it
        bx(s, cx, y + size * 0.5, 0, size * 1.1, size * 0.15, z * 0.6, "dark")
        bx(s, cx, y - size * 0.4, 0, size * 0.8, size * 0.9, z * 0.4, "acc", tag="pennant")
        self.crystal(s, cx, y, size * (0.75 if boss else 0.55), z * 0.6 + 0.2)

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        # rime crusted on the edges, icicles hanging off whatever sticks out
        for side in (1, -1):
            bx(s, side * (half - 0.25), y0 + 1, 0, 0.6, (y1 - y0) * (0.5 if side > 0 else 0.3), thick + 0.1, "white", glow=True)
        for k in range(3):
            x = -half + 0.5 + k * (2 * half - 1) / 2
            bx(s, x, y0 - 1.6 - k * 0.4, 0, 0.6, 1.6 + k * 0.4, 0.6, "glow", glow=True, tag="icicle")


class Silk(Theme):
    def __init__(self):
        super().__init__("silk",
                         blade=ramp("#1a1824", "#2a2638", "#3c3650", "#52496a", "#6e6488", "#9086aa", "#b8b0cc", "#e2dcec"),
                         dark=ramp("#060508", "#0e0c12", "#18141e", "#24202c", "#322c3c", "#443c50"),
                         wrap=ramp("#2a040a", "#4a0a14", "#6e1220", "#8a1424", "#a8283a"),
                         wood=ramp("#140c08", "#22140c", "#321e12", "#442a1a", "#583824", "#6e482e"),
                         glow=ramp("#2a0a4a", "#4a1a7a", "#7036b0", "#9a5ae0", "#c08cff", "#e4c8ff", "#faf2ff"),
                         acc=ramp("#8a8478", "#a8a294", "#c4bfb2", "#dcd8cc", "#eeebe2", "#fbfaf6"))

    def spider(self, s, cx, y, size, z):
        bx(s, cx, y, 0, size * 0.5, size * 0.6, z, "dark", tag="body")
        bx(s, cx, y + size * 0.6, 0, size * 0.34, size * 0.3, z * 0.8, "dark", tag="head")
        bx(s, cx, y + size * 0.15, 0, size * 0.18, size * 0.3, z + 0.1, "glow", glow=True, tag="mark")
        for side in (1, -1):
            for k in range(3):
                seg(s, (cx + side * size * 0.2, y + size * (0.2 + 0.18 * k)), (cx + side * size * 0.75, y + size * (0.45 + 0.1 * k - 0.15 * (k == 0))),
                    size * 0.08, size * 0.08, "dark")

    def emblem(self, s, cx, y, size, z, boss):
        self.spider(s, cx, y, size * (1.2 if boss else 0.9), z)

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        # silk thread wound round and trailing, a page tab, ink in the fuller
        for k in range(4):
            seg(s, (-half - 0.2, y0 + 0.5 + k * 0.8), (half + 0.2, y0 + 1.0 + k * 0.8), 0.35, thick + 0.25, "acc")
        seg(s, (half + 0.1, y0 + 3.2), (half + 1.6, y0 - 1.2), 0.3, 0.3, "acc")
        if where == "blade":
            bx(s, 0, y0 + 4, 0, 0.7, (y1 - y0) * 0.45, thick + 0.06, "glow", glow=True)


THEMES = {t.gate: t for t in (Cellar(), Gallows(), Rotwood(), Crypt(), Plague(), Temple(), Ossuary(), Foundry(), Frost(), Silk())}


# ================================================================== the type templates (px; the hand at the origin)

def rnd(seed, k):
    return h3(seed, k, 17)


def chainp(s, start, segs, mat, z=0.0, glow=False):
    from voxsword import chain
    return chain(s, start, segs, mat, z=z, group="fire" if glow else "lit")


def guard(s, th, y, width, thick, style, boss):
    """the crossguard: a heavy bar with the gate's emblem set in the middle, in one of three shapes"""
    t = thick + 1.2
    if style == "swept":
        bx(s, 0, y, 0, 3.6, 2.0, t, "dark", tag="guard")
        for side in (1, -1):
            chainp(s, (side * 1.4, y + 1.0), [(width * 0.28, side * 70, 1.5, t - 0.2), (width * 0.22, side * 25, 1.3, t - 0.3),
                                               (width * 0.12, -side * 15, 1.1, t - 0.4)], "dark")
    elif style == "disc":
        bx(s, 0, y, 0, width * 0.75, 2.0, width * 0.6, "dark", tag="guard")
        bx(s, 0, y + 2.0, 0, width * 0.5, 0.8, width * 0.4, "dark")
    else:
        bx(s, 0, y, 0, width, 1.8, t, "dark", tag="guard")
        for side in (1, -1):   # the quillon ends turned up
            bx(s, side * (width / 2 - 0.7), y + 1.6, 0, 1.4, 1.6, t, "dark")
            bx(s, side * (width / 2 - 0.7), y - 0.8, 0, 1.0, 0.9, t - 0.3, "dark")
    th.emblem(s, 0, y + (2.4 if style == "disc" else 0.5), 3.6 if not boss else 4.6, t + 0.6, boss)


def pommel(s, th, y, style, boss):
    if style == "ring":
        ring_xy(s, 0, y - 2.0, 1.6, 0.9, "dark", depth=1.4)
    elif style == "block":
        bx(s, 0, y - 2.4, 0, 2.8, 2.4, 2.8, "dark", tag="pommel")
        bx(s, 0, y - 3.0, 0, 1.6, 0.7, 1.6, "dark")
    else:
        bx(s, 0, y - 1.6, 0, 2.6, 1.6, 2.6, "dark", tag="pommel")
        bx(s, 0, y - 2.6, 0, 1.8, 1.0, 1.8, "dark")
    if boss:
        bx(s, 0, y - 1.4, 0, 1.0, 1.0, 3.0, "glow", glow=True)


def blade_body(s, y0, y1, wfn, thick, mat="blade", cxf=None, step=1.6, spine=True):
    """a blade in steps; a darker spine ridge down its middle so the faces aren't flat"""
    y = y0
    while y < y1 - 0.05:
        h = min(step, y1 - y)
        t = (y + h / 2 - y0) / max(0.01, y1 - y0)
        w = max(0.6, round(wfn(t) * 4) / 4)
        c = cxf(t) if cxf else 0.0
        s.add(C(c, y, 0, w, h + 0.02, thick), mat, tag="blade")
        if spine and w > 1.6:
            s.add(C(c, y, 0, max(0.5, w * 0.22), h + 0.02, thick + 0.3), "dark" if mat == "blade" else mat, tag="spine")
        y += h


def tip(s, x, y, w, thick, n=3, step=1.3, lean=0.0):
    for k in range(n):
        f = 1 - (k + 1) / (n + 1)
        bx(s, x + lean * k, y, 0, max(0.5, w * f), step, thick * (1 - 0.15 * k), "blade", tag="blade")
        y += step
    return y


def sword(th, it, seed, boss):
    s = Sword(it["id"])
    L = 19.0 + 3 * rnd(seed, 1) + (3.5 if boss else 0)
    w0 = 4.0 + 0.8 * rnd(seed, 2) + (0.8 if boss else 0)
    style = it.get("shape") or ["straight", "falchion", "leaf", "curved"][int(rnd(seed, 3) * 4)]
    y0 = 4.4
    if style == "falchion":
        wfn, cxf = (lambda t: w0 * (0.9 + 0.5 * t)), (lambda t: 0.7 * t)
    elif style == "leaf":
        wfn, cxf = (lambda t: w0 * (0.85 + 0.4 * math.sin(t * math.pi))), None
    elif style == "curved":
        wfn, cxf = (lambda t: w0 * (1 - 0.2 * t)), (lambda t: 2.4 * t * t)
    else:
        wfn, cxf = (lambda t: w0 * (1 - 0.15 * t)), None
    bx(s, 0, y0 - 0.6, 0, w0 * 0.7, 1.8, 1.6, "dark", tag="ricasso")
    blade_body(s, y0 + 1.2, y0 + L, wfn, 1.2, cxf=cxf)
    tip(s, cxf(1) if cxf else 0, y0 + L, wfn(1), 1.2, lean=0.5 if style == "falchion" else 0.3 if style == "curved" else 0)
    th.trim(s, "blade", y0 + 1.2, y0 + L, w0 / 2, 1.2, boss, seed)
    if boss:
        bx(s, 0, y0 + 2, 0, 0.8, L * 0.7, 1.56, "glow", glow=True, tag="fuller")
    guard(s, th, 2.0, w0 + 4.2 + (1.6 if boss else 0), 1.2, it.get("guard") or ["cross", "swept", "cross"][int(rnd(seed, 4) * 3)], boss)
    bx(s, 0, -4.6, 0, 2.0, 6.8, 2.0, "wrap", tag="grip")
    pommel(s, th, -4.6, ["ring", "block", "cap"][int(rnd(seed, 5) * 3)], boss)
    return s


def dagger(th, it, seed, boss):
    s = Sword(it["id"])
    L = 10.5 + 2 * rnd(seed, 1) + (2.5 if boss else 0)
    w0 = 3.0 + 0.6 * rnd(seed, 2)
    style = it.get("shape") or ["straight", "curved", "stiletto", "wavy"][int(rnd(seed, 3) * 4)]
    y0 = 3.2
    if style == "spiral":
        # a corkscrew: a thick helix wound round a core
        bx(s, 0, y0, 0, 0.9, L, 0.9, "dark")
        prev = None
        for k in range(int(L / 0.7)):
            a = math.radians(k * 40)
            p = (math.sin(a) * 1.6, y0 + k * 0.7)
            if prev:
                seg(s, prev, p, 1.0, 1.2, "blade", z=math.cos(a) * 0.9)
            prev = p
        bx(s, prev[0], prev[1], 0, 0.6, 1.4, 0.6, "blade")
    else:
        if style == "curved":
            wfn, cxf = (lambda t: w0 * (1 - 0.45 * t)), (lambda t: 2.0 * t * t)
        elif style == "stiletto":
            wfn, cxf = (lambda t: w0 * 0.65 * (1 - 0.5 * t)), None
        elif style == "wavy":
            wfn, cxf = (lambda t: w0 * (1 - 0.4 * t)), (lambda t: 0.7 * math.sin(t * 9))
        else:
            wfn, cxf = (lambda t: w0 * (1 - 0.35 * t)), None
        blade_body(s, y0, y0 + L, wfn, 1.1, cxf=cxf, step=1.2)
        tip(s, cxf(1) if cxf else 0, y0 + L, wfn(1), 1.0, n=2, step=1.2, lean=0.4 if style == "curved" else 0)
    th.trim(s, "blade", y0 + 0.4, y0 + L, w0 / 2, 1.1, boss, seed)
    if boss:
        bx(s, w0 / 2 - 0.3, y0, 0, 0.5, L * 0.8, 1.16, "glow", glow=True, tag="edge")
    guard(s, th, 1.0, w0 + 3.0, 1.1, it.get("guard") or ["cross", "disc", "swept"][int(rnd(seed, 4) * 3)], boss)
    bx(s, 0, -3.6, 0, 1.9, 4.6, 1.9, "wrap", tag="grip")
    pommel(s, th, -3.6, ["ring", "cap", "block"][int(rnd(seed, 5) * 3)], boss)
    return s


def haft(s, th, y0, y1, w=1.8, mat="wood"):
    bx(s, 0, y0, 0, w, y1 - y0, w, mat, tag="haft")


def hammer(th, it, seed, boss):
    s = Sword(it["id"])
    top = 12.0 + (1.0 if boss else 0)
    haft(s, th, -12.0, top + 1, 2.0, "wood")
    bx(s, 0, -6.0, 0, 2.4, 7.0, 2.4, "wrap", tag="grip")
    bx(s, 0, -13.6, 0, 3.0, 2.0, 3.0, "dark", tag="pommel")
    for y in (2.0, 6.0):
        bx(s, 0, y, 0, 2.6, 1.0, 2.6, "dark", tag="band")
    style = it.get("shape") or ["block", "barrel", "spiked", "block"][int(rnd(seed, 3) * 4)]
    W, H, D = (12.0, 8.0, 7.0) if not boss else (14.0, 9.0, 8.0)
    cy = top + 2.0
    if style == "barrel":   # a cooper's drum of a head, hooped
        for k in range(6):
            r = D * (0.82 + 0.18 * math.sin(k / 5 * math.pi))
            bx(s, -W / 2 + 0.9 + k * (W - 1.8) / 6 + (W - 1.8) / 12, cy - r / 2, 0, (W - 1.8) / 6 + 0.05, r, r, "wood")
        for x in (-W / 2 + 1.4, 0.0, W / 2 - 1.4):
            bx(s, x, cy - D / 2 - 0.4, 0, 1.0, D + 0.8, D + 0.8, "dark", tag="band")
        for x in (-W / 2, W / 2):
            bx(s, x, cy - D * 0.35, 0, 0.8, D * 0.7, D * 0.7, "dark")
    elif style == "bell":
        for k, w in enumerate((3.4, 5.4, 7.0, 8.4, 9.4, 10.0)):
            bx(s, 0, top - 2 + k * 1.6, 0, w, 1.7, w, "dark")
        bx(s, 0, top - 2.4, 0, 10.6, 0.8, 10.6, "dark", tag="lip")
        bx(s, 0, top - 4.2, 0, 2.2, 2.0, 2.2, "acc", tag="clapper")
        bx(s, 0, top + 7.6, 0, 2.6, 1.6, 2.6, "dark")
    elif style == "pestle":
        bx(s, 0, top, 0, 5.4, 9.0, 5.4, "acc")
        bx(s, 0, top + 9, 0, 7.0, 2.4, 7.0, "acc")
        bx(s, 0, top + 2, 0, 6.0, 1.0, 6.0, "dark", tag="band")
    else:
        bx(s, 0, cy - H / 2, 0, W, H, D, "blade", tag="head")
        bx(s, 0, cy - H / 2 - 0.6, 0, 4.0, H + 1.2, D + 0.8, "dark", tag="eye")
        for x in (-W / 2 + 1.2, W / 2 - 1.2):
            bx(s, x, cy - H / 2 - 0.4, 0, 1.2, H + 0.8, D + 0.6, "dark", tag="band")
        if style == "spiked":
            for x in (-3.6, 0.0, 3.6):
                chainp(s, (x, cy + H / 2), [(2.0, 0, 1.6, 1.6), (1.6, 0, 0.8, 0.8)], "dark")
            for side in (1, -1):
                chainp(s, (side * W / 2, cy), [(2.2, -side * 90, 1.4, 1.4), (1.4, -side * 90, 0.7, 0.7)], "dark")
        else:
            bx(s, W / 2 + 0.4, cy - H / 2 + 0.6, 0, 1.0, H - 1.2, D - 1.2, "glow", glow=True, tag="face")
            bx(s, -W / 2 - 0.6, cy - H / 2 + 0.8, 0, 1.2, H - 1.6, D - 1.6, "dark", tag="face")
    if style in ("bell", "pestle"):
        th.emblem(s, 0, top - 7.0, 3.6, 3.0, boss)
    else:
        th.emblem(s, 0, cy - 1.8, 4.4 if not boss else 5.4, D + 0.6, boss)
    th.trim(s, "haft", -1.0, top - 3, 1.0, 2.0, boss, seed)
    return s


def spear(th, it, seed, boss):
    s = Sword(it["id"])
    top = 14.0
    haft(s, th, -24.0, top + 1, 1.8, "wood")
    bx(s, 0, -4.0, 0, 2.2, 8.0, 2.2, "wrap", tag="grip")
    bx(s, 0, -25.6, 0, 2.6, 2.0, 2.6, "dark", tag="butt")
    for y in (-16.0, 6.0):
        bx(s, 0, y, 0, 2.4, 1.0, 2.4, "dark", tag="band")
    bx(s, 0, top, 0, 2.8, 3.4, 2.8, "dark", tag="socket")
    bx(s, 0, top + 3.0, 0, 4.0, 1.2, 2.4, "dark", tag="collar")
    style = it.get("shape") or ["leaf", "spike", "glaive", "leaf"][int(rnd(seed, 3) * 4)]
    y = top + 4.2
    big = 1.2 if boss else 1.0
    if style == "hook":
        blade_body(s, y, y + 10 * big, lambda t: 3.0 * (1 - 0.55 * t), 1.2)
        yy = tip(s, 0, y + 10 * big, 1.6, 1.2, n=2)
        chainp(s, (1.4, y + 1.0), [(3.4, -75, 1.6, 1.2), (2.8, -15, 1.4, 1.1), (2.0, 40, 1.2, 1.0), (1.2, 90, 0.9, 0.9)], "blade")
    elif style == "glaive":
        blade_body(s, y, y + 13 * big, lambda t: 4.4 * (0.75 + 0.45 * math.sin(t * math.pi)), 1.2, cxf=lambda t: 1.8 * t * t)
        yy = tip(s, 1.8, y + 13 * big, 3.0, 1.2, lean=0.4)
    elif style == "halberd":
        blade_body(s, y, y + 12 * big, lambda t: 2.4 * (1 - 0.6 * t), 1.2)
        yy = tip(s, 0, y + 12 * big, 1.4, 1.2, n=2)
        for k in range(5):
            bx(s, 2.0 + k * 1.1, y + 0.5 + k * 0.3, 0, 1.15, 7.5 - k * 1.1, 1.2, "blade")
        bx(s, 2.0 + 5 * 1.1, y + 1.5, 0, 0.7, 5.0, 1.26, "glow", glow=True)
        chainp(s, (-1.4, y + 2.0), [(3.0, 70, 1.4, 1.2), (2.0, 120, 1.0, 1.0)], "blade")
    elif style == "needle":
        blade_body(s, y, y + 15 * big, lambda t: 1.6 * (1 - 0.55 * t), 1.2, spine=False)
        yy = tip(s, 0, y + 15 * big, 0.8, 1.0, n=2)
        for k in range(3):
            seg(s, (0.5, y + 3 + k * 3.4), (2.0, y + 1.8 + k * 3.4), 0.7, 0.7, "blade")
            seg(s, (-0.5, y + 4.6 + k * 3.4), (-2.0, y + 3.4 + k * 3.4), 0.7, 0.7, "blade")
    elif style == "spike":
        blade_body(s, y, y + 14 * big, lambda t: 2.8 * (1 - 0.7 * t), 2.2, spine=False)
        yy = tip(s, 0, y + 14 * big, 1.2, 1.6, n=2)
        for side in (1, -1):
            chainp(s, (side * 1.4, y + 0.4), [(2.6, -side * 55, 1.1, 1.1), (1.6, -side * 20, 0.7, 0.7)], "blade")
    else:
        blade_body(s, y, y + 13 * big, lambda t: 4.6 * big * (0.5 + 0.65 * math.sin(min(1, t * 1.25) * math.pi * 0.85)), 1.2)
        yy = tip(s, 0, y + 13 * big, 2.0, 1.2)
    th.trim(s, "blade", y, yy - 1, 1.6, 1.2, boss, seed)
    th.emblem(s, 0, top - 4.0, 3.2 if not boss else 4.2, 3.0, boss)
    if boss:
        bx(s, 0, y + 1, 0, 0.7, (yy - y) * 0.6, 1.56, "glow", glow=True)
    return s


def twohander(th, it, seed, boss):
    s = Sword(it["id"])
    style = it.get("shape") or ["straight", "cleaver", "flamberge", "straight"][int(rnd(seed, 3) * 4)]
    if style == "axe":
        haft(s, th, -12.0, 22.0, 2.2, "wood")
        bx(s, 0, -8.4, 0, 2.6, 12.0, 2.6, "wrap", tag="grip")
        bx(s, 0, -13.8, 0, 3.0, 2.0, 3.0, "dark")
        for k in range(9):
            h = 3.4 + 10.0 * math.sin(k / 8 * math.pi * 0.9 + 0.2)
            bx(s, 1.4 + k * 1.25, 15.0 - h / 2 + k * 0.3, 0, 1.3, h, 1.4, "blade", tag="blade")
        bx(s, 1.4 + 9 * 1.25 - 0.4, 15.0 - 6.0 + 2.4, 0, 0.8, 12.0, 1.46, "glow" if boss else "blade", glow=boss)
        bx(s, 0, 9.0, 0, 3.4, 9.0, 2.6, "dark", tag="cheek")
        chainp(s, (-1.4, 13.0), [(3.0, 80, 1.6, 1.4), (2.0, 120, 1.0, 1.0)], "blade")
        th.emblem(s, 0, 20.0, 4.4, 3.0, boss)
        th.trim(s, "haft", 0.0, 8.0, 1.1, 2.2, boss, seed)
        return s
    L = 25.0 + 3 * rnd(seed, 1) + (4 if boss else 0)
    w0 = 6.4 + 1.2 * rnd(seed, 2) + (0.8 if boss else 0)
    y0 = 6.0
    if style == "cleaver":
        wfn, cxf = (lambda t: w0 * (1.15 + 0.15 * t)), (lambda t: 0.9 * t)
    elif style == "flamberge":
        wfn, cxf = (lambda t: w0 * (0.9 - 0.25 * t)), (lambda t: 0.8 * math.sin(t * 14))
    else:
        wfn, cxf = (lambda t: w0 * (1 - 0.15 * t)), None
    bx(s, 0, y0 - 0.4, 0, w0 * 0.6, 2.4, 2.2, "dark", tag="ricasso")
    blade_body(s, y0 + 2.0, y0 + L, wfn, 1.7, cxf=cxf, step=2.0)
    tx = cxf(1) if cxf else 0
    if style == "cleaver":
        bx(s, tx + 0.6, y0 + L, 0, wfn(1) * 0.85, 1.6, 1.6, "blade", tag="blade")
        bx(s, tx - wfn(1) * 0.3, y0 + L + 1.6, 0, wfn(1) * 0.3, 1.2, 1.5, "blade", tag="blade")
    else:
        tip(s, tx, y0 + L, wfn(1), 1.6, n=3, step=1.6)
    th.trim(s, "blade", y0 + 2.0, y0 + L, w0 / 2, 1.7, boss, seed)
    if boss:
        for side in (1, -1):
            bx(s, side * (w0 / 2 - 0.4), y0 + L * 0.35, 0, 0.6, L * 0.55, 1.76, "glow", glow=True, tag="edge")
    gw = w0 + 5.0 + (2 if boss else 0)
    guard(s, th, 2.6, gw, 1.9, it.get("guard") or ["cross", "swept"][int(rnd(seed, 4) * 2)], boss)
    V.grip(s, "wrap", "dark")
    bx(s, 0, -12.8, 0, 3.4, 2.8, 3.4, "dark", tag="pommel")
    if boss:
        bx(s, 0, -12.0, 0, 1.6, 1.2, 3.6, "glow", glow=True)
    return s


def staff(th, it, seed, boss, school):
    s = Sword(it["id"])
    top = 12.0
    haft(s, th, -18.0, top, 2.0, "wood")
    bx(s, 0, -4.0, 0, 2.4, 8.0, 2.4, "wrap", tag="grip")
    bx(s, 0, -19.8, 0, 2.6, 2.0, 2.6, "dark", tag="shoe")
    for y in (-12.0, 5.0):
        bx(s, 0, y, 0, 2.6, 1.0, 2.6, "dark", tag="band")
    big = 1.25 if boss else 1.0
    bx(s, 0, top - 1.0, 0, 3.4, 2.2, 3.4, "dark", tag="collar")
    if school == "black":
        # an iron claw round a burning orb of the gate's element, a spike up through it
        oy = top + 3.2 * big
        bx(s, 0, oy - 2.6 * big, 0, 5.2 * big, 5.2 * big, 5.2 * big, "glow", glow=True, tag="orb")
        bx(s, 0, oy - 1.6 * big, 0, 3.2 * big, 3.2 * big, 5.6 * big, "white", glow=True)
        for side in (1, -1):
            chainp(s, (side * 1.4, top + 1.0), [(3.2 * big, side * 40, 1.4, 1.6), (3.6 * big, -side * 10, 1.2, 1.4),
                                                (2.4 * big, -side * 45, 1.0, 1.2), (1.4 * big, -side * 80, 0.8, 0.9)], "dark")
        chainp(s, (0, oy + 2.4 * big), [(2.6 * big, 0, 1.2, 1.2), (2.0 * big, 0, 0.6, 0.6)], "dark")
        th.emblem(s, 0, top - 6.0, 3.4 * big, 3.0, boss)
    elif school == "white":
        # a ring held up on the haft, a lamp hung in it, pale light
        R = 5.0 * big
        ring_xy(s, 0, top + 1.2 + R, R, 1.4, "gold" if boss else "dark", depth=1.8)
        bx(s, 0, top + 1.2 + 2 * R - 2.0, 0, 0.6, 2.0, 0.6, "dark", tag="chain")
        lamp_y = top + 1.2 + R - 1.4
        bx(s, 0, lamp_y, 0, 3.2 * big, 3.2 * big, 3.2 * big, "white", glow=True, tag="lamp")
        for dy in (-0.4, 3.2 * big - 0.2):
            bx(s, 0, lamp_y + dy, 0, 3.8 * big, 0.7, 3.8 * big, "dark")
        for sx in (-1, 1):
            for sz in (-1, 1):
                bx(s, sx * 1.6 * big, lamp_y, sz * 1.6 * big, 0.5, 3.2 * big, 0.5, "dark")
        th.emblem(s, 0, top + 2.4 + 2 * R, 2.8 * big, 2.0, boss)
        th.emblem(s, 0, top - 6.0, 3.0, 3.0, boss)
    else:
        # a crook bent over, charms and the gate's emblem hung off it on chains
        end = chainp(s, (0, top), [(4.0 * big, 0, 2.0, 2.0), (3.4 * big, 40, 1.9, 1.9), (3.0 * big, 95, 1.8, 1.8),
                                    (2.6 * big, 150, 1.6, 1.6)], "wood")
        for k, (x, ln) in enumerate(((end[0], 2.4), (-1.8 * big, 3.6))):
            bx(s, x, top + 5.6 * big - ln, 0, 0.5, ln, 0.5, "dark", tag="chain")
        th.emblem(s, end[0], top + 5.6 * big - 2.4 - 3.6 * big, 3.2 * big, 2.2, boss)
        bx(s, -1.8 * big, top + 5.6 * big - 3.6 - 1.8, 0, 1.8, 1.8, 1.8, "glow", glow=True, tag="charm")
        for k in range(3):
            bx(s, 0, top + 0.8 + k * 1.0, 0, 2.6 - 0.3 * k, 0.6, 2.6 - 0.3 * k, "acc", tag="charm_cord")
    th.trim(s, "haft", 2.0, top - 2, 1.0, 2.0, boss, seed)
    return s


def shield(th, it, seed, boss):
    """in vanilla shield space: handle at the origin, the face toward +z, px"""
    s = Sword(it["id"])
    style = it.get("shape") or ["kite", "round", "tower", "heater"][int(rnd(seed, 3) * 4)]
    F = 2.2
    big = 1.1 if boss else 1.0
    face = "wood" if style in ("round", "tower") else "blade"
    if style == "round":
        R = 11.0 * big
        x = -R
        k = 0
        while x < R - 0.1:   # planks running up and down, each a touch proud of the next
            w = 2.6
            hh = math.sqrt(max(0.0, R * R - (x + w / 2) ** 2))
            if hh > 1:
                bx(s, x + w / 2, -hh - 1.0, 1.4 + (0.15 if k % 2 else 0), w - 0.15, 2 * hh, F - 0.4, face, tag="plank")
            x += w
            k += 1
        ring_xy(s, 0, -1.0, R - 0.4, 1.4, "dark", depth=F + 0.6, z=1.6)
        ring_xy(s, 0, -1.0, R * 0.62, 1.0, "dark", depth=F + 0.5, z=1.6)
    else:
        if style == "tower":
            rows = [(y, y + 2, 15.0 * big) for y in range(-13, 13, 2)]
        elif style == "heater":
            rows = [(y, y + 2, 15.0 * big * (1 if y > -3 else max(0.25, 1 - (-3 - y) / 11))) for y in range(-12, 11, 2)]
        else:  # kite
            rows = [(y, y + 2, 14.0 * big * (1 if y > 3 else max(0.2, 1 - (3 - y) / 16))) for y in range(-13, 11, 2)]
        for (y0, y1, w) in rows:
            bx(s, 0, y0, 1.4, w, y1 - y0 + 0.02, F - 0.4, face, tag="plate")
            for side in (1, -1):
                bx(s, side * (w / 2 - 0.6), y0, 1.6, 1.4, y1 - y0 + 0.02, F + 0.4, "dark", tag="rim")
        topr = rows[-1]
        bx(s, 0, topr[1] - 0.8, 1.6, topr[2], 1.4, F + 0.4, "dark", tag="rim")
        if style == "tower":
            for y in (-9.0, 7.0):
                bx(s, 0, y, 2.6, 15.0 * big, 1.2, 0.8, "dark", tag="strap")
                for x in (-5.0, 0.0, 5.0):
                    bx(s, x, y + 0.1, 3.2, 1.0, 1.0, 0.6, "dark", tag="stud")
        else:
            bx(s, 0, -10.0, 2.6, 1.2, 18.0, 0.7, "dark", tag="spine")
    # the boss, and the gate's emblem big on the face
    bx(s, 0, -3.4, 2.8, 5.6, 5.6, 1.4, "dark", tag="boss")
    th.emblem(s, 0, -2.0, 6.6 * big, 2.0, boss)
    th.trim(s, "shield", -8.0, 8.0, 4.0, 5.0, boss, seed)
    if boss:
        ring_xy(s, 0, -1.0, 4.4, 0.6, "white", glow=True, depth=0.5, z=3.6)
    bx(s, 0, -3.0, -5.0, 2.0, 6.0, 1.2, "wrap", tag="handle")
    for y0 in (-3.0, 2.0):
        bx(s, 0, y0, -2.0, 2.0, 1.0, 6.0, "dark", tag="handle_arm")
    return s


# the bow: Kiln geometry (voxkiln_gear), in the gate's materials with its trim at the grip
O = (8.0, 8.0)
U = (0.651, 0.759)
A = (-0.759, 0.651)
BL, BULGE, BZ = 9.0, 3.4, 8.0


def bow_at(s_, pull):
    k = pull
    bend = BULGE * (1 - s_ * s_) + 0.35 * k * abs(s_)
    curl = 1.4 * max(0.0, abs(s_) - 0.82) / 0.18
    along = s_ * BL * (1 - 0.05 * k)
    fwd = bend + curl - 0.9 * k * s_ * s_
    return (O[0] + U[0] * along + A[0] * fwd, O[1] + U[1] * along + A[1] * fwd)


def bow(th, it, seed, boss, pull=0.0, arrow=False, name=None):
    s = Sword(name or it["id"])
    n = 12
    for i in range(n):
        s0, s1 = -1 + 2 * i / n, -1 + 2 * (i + 1) / n
        p0, p1 = bow_at(s0, pull), bow_at(s1, pull)
        t = abs((s0 + s1) / 2)
        w = (2.0 if boss else 1.8) - 0.9 * t
        seg(s, p0, p1, w, 1.5, "wood" if th.gate in ("cellar", "gallows", "rotwood", "silk", "crypt") else "blade", BZ, tag="limb")
        if i % 3 == 1 and 0.2 < t < 0.85:
            q0 = (p0[0] - A[0] * w * 0.3, p0[1] - A[1] * w * 0.3)
            q1 = (p1[0] - A[0] * w * 0.3, p1[1] - A[1] * w * 0.3)
            seg(s, q0, q1, 0.45, 1.56, "glow", BZ, glow=True)
    for tip in (-1, 1):   # the tips capped in the gate's dark metal
        c = bow_at(tip * 0.96, pull)
        bx(s, c[0], c[1] - 0.6, BZ, 1.4, 1.2, 1.7, "dark")
    g0, g1 = bow_at(-0.16, pull), bow_at(0.16, pull)
    seg(s, g0, g1, 2.4, 2.0, "wrap", BZ, tag="grip")
    gc = bow_at(0.0, pull)
    first = len(s.boxes)
    th.emblem(s, gc[0] + A[0] * 1.6, gc[1] + A[1] * 1.6 - 1.0, 2.2 if not boss else 3.0, 2.4, boss)
    for b in s.boxes[first:]:   # emblems are drawn on a blade's plane (z 0); the bow's is BZ, or it floats half a block off
        b.lo, b.pivot = (b.lo[0], b.lo[1], b.lo[2] + BZ), (b.pivot[0], b.pivot[1], b.pivot[2] + BZ)
    t0, t1 = bow_at(-1, pull), bow_at(1, pull)
    mid = ((t0[0] + t1[0]) / 2, (t0[1] + t1[1]) / 2)
    nock = (mid[0] - A[0] * 4.2 * pull, mid[1] - A[1] * 4.2 * pull)
    seg(s, t0, nock, 0.35, 0.35, "acc", BZ)
    seg(s, nock, t1, 0.35, 0.35, "acc", BZ)
    if arrow:
        head = (nock[0] + A[0] * 14.0, nock[1] + A[1] * 14.0)
        seg(s, nock, head, 0.5, 0.5, "wood", BZ + 0.6)
        tip = (head[0] + A[0] * 2.2, head[1] + A[1] * 2.2)
        seg(s, head, tip, 1.3, 0.6, "blade", BZ + 0.6)
        seg(s, nock, (nock[0] + A[0] * 2.4, nock[1] + A[1] * 2.4), 1.2, 0.3, "glow", BZ + 0.6, glow=True)
    return s


# ================================================================== per-weapon shape hints (from the names)

HINTS = {
    'bilge_boathook': {'shape': 'hook'}, 'stave_cleaver': {'shape': 'cleaver'}, 'cask_lid_shield': {'shape': 'round'},
    'spigot_knife': {'shape': 'straight', 'guard': 'disc'}, 'lees_sabre': {'shape': 'curved', 'guard': 'swept'},
    'mothers_lid': {'shape': 'round'}, 'corkscrew': {'shape': 'spiral'},
    'headsmans_sword': {'shape': 'straight', 'guard': 'cross'}, 'trapdoor_maul': {'shape': 'block'},
    'gibbet_hook': {'shape': 'hook'}, 'gibbet_door': {'shape': 'tower'}, 'hangmans_verdict': {'shape': 'falchion', 'guard': 'emblem'},
    'gallows_gate': {'shape': 'tower'}, 'the_last_drop': {'shape': 'axe'}, 'noose_cutter': {'shape': 'curved'},
    'rotbranch_blade': {'shape': 'leaf'}, 'thorn_shiv': {'shape': 'stiletto'}, 'burl_maul': {'shape': 'barrel'},
    'antler_greatblade': {'shape': 'flamberge'}, 'shelf_fungus_shield': {'shape': 'round'}, 'mosskings_briar': {'shape': 'leaf', 'guard': 'emblem'},
    'crownbark': {'shape': 'heater'}, 'velvet_tine': {'shape': 'curved'},
    'vigil_sword': {'shape': 'straight', 'guard': 'cross'}, 'gravediggers_knife': {'shape': 'straight'}, 'bellmaul': {'shape': 'bell'},
    'gravespike': {'shape': 'spike'}, 'coffin_lid_shield': {'shape': 'tower'}, 'pale_vigil': {'shape': 'straight', 'guard': 'emblem'},
    'abbots_reliquary': {'shape': 'heater'}, 'last_candle': {'shape': 'stiletto'},
    'quarantine_door': {'shape': 'tower'}, 'surgeons_tray': {'shape': 'kite'}, 'surgeons_probe': {'shape': 'needle'},
    'scalpel_saint': {'shape': 'stiletto'},
    'mirror_of_no_face': {'shape': 'round'}, 'sovereigns_edge': {'shape': 'straight', 'guard': 'emblem'},
    'thousand_face_aegis': {'shape': 'kite'}, 'visage_thief': {'shape': 'wavy'},
    'ribcage_shield': {'shape': 'heater'}, 'engine_blade': {'shape': 'falchion', 'guard': 'emblem'}, 'boilerplate': {'shape': 'tower'},
    'piston_shiv': {'shape': 'straight'},
    'brandsteel': {'shape': 'straight', 'guard': 'emblem'}, 'furnace_door': {'shape': 'tower'}, 'ember_fang': {'shape': 'curved'},
    'rime_sword': {'shape': 'straight'}, 'icicle_dirk': {'shape': 'stiletto'}, 'glacier_maul': {'shape': 'spiked'},
    'frostbound_pike': {'shape': 'spike'}, 'procession_greatsword': {'shape': 'straight', 'guard': 'emblem'},
    'glacier_tower': {'shape': 'tower'}, 'marshals_sabre': {'shape': 'curved', 'guard': 'swept'},
    'winter_standard': {'shape': 'kite'}, 'wintermarch': {'shape': 'halberd'}, 'frostbite': {'shape': 'wavy'},
    'scriveners_blade': {'shape': 'straight', 'guard': 'swept'}, 'quill_knife': {'shape': 'stiletto'},
    'bookbinders_maul': {'shape': 'block'}, 'spindle_spear': {'shape': 'needle'}, 'folio_cleaver': {'shape': 'cleaver'},
    'tome_shield': {'shape': 'tower'}, 'queens_needle': {'shape': 'stiletto', 'guard': 'emblem'}, 'cocoon_aegis': {'shape': 'round'},
    'widowmaker': {'shape': 'flamberge'}, 'fang_of_the_queen': {'shape': 'curved'},
    'plague_pestle': {'shape': 'pestle'}, 'coopers_mallet': {'shape': 'barrel'},
}

# the Roster v2 dungeons' themes and hints (weapon_themes_v2.py)
sys.modules.setdefault('weaponforge', sys.modules[__name__])   # run as a script: the themes import this module, not a second copy
import weapon_themes_v2 as _v2  # noqa: E402
THEMES.update(_v2.THEMES)
HINTS.update(_v2.HINTS)

TYPE_BUILD = {'sword': sword, 'dagger': dagger, 'hammer': hammer, 'spear': spear, 'twohander': twohander}


def build(th, it):
    seed = zlib.crc32(it['id'].encode()) & 0xFFFF
    spec = dict(it, **HINTS.get(it['id'], {}))
    k = it['kind']
    boss = it['boss']
    if k in ('black', 'white', 'summon'):
        s = staff(th, spec, seed, boss, k)
    elif k == 'shield':
        s = shield(th, spec, seed, boss)
    elif k == 'bow':
        s = bow(th, spec, seed, boss)
    else:
        s = TYPE_BUILD[k](th, spec, seed, boss)
    s.shaders = th.shaders
    return s, seed, spec


# ================================================================== writing it out

def material(name, path):
    lines = ['mtllib %s.mtl' % name]
    for l in open(path, encoding='utf-8').read().splitlines():
        if l.startswith(('mtllib', 'usemtl')):
            continue
        lines.append(l)
        if l.startswith('g '):
            lines.append('usemtl ' + ('glow' if l.split()[1] == 'fire' else 'blade'))
    open(path, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    tex = 'ashbound:item/%s_3d' % name
    open(path[:-4] + '.mtl', 'w', encoding='utf-8').write(
        'newmtl blade\nKa 0 0 0\nmap_Kd %s\n\nnewmtl glow\nKa 1 1 1\nmap_Kd %s\n' % (tex, tex))


def hand_made():
    """the weapons tools/weaponsets.py owns; the templates leave them alone"""
    import weaponsets as WS
    if not WS.DESIGNS:
        WS.load_designs()
    return WS.DESIGNS


def export(s, mesh, to_item=TO_ITEM, preview=True, join=True, force=False):
    if not force and mesh.split('_pulling_')[0] in hand_made():
        return 0
    img, tris = s.build()
    img.save(ASSETS + 'textures/item/%s_3d.png' % mesh)
    V.to_item = to_item
    path = ASSETS + 'models/mesh/%s.obj' % mesh
    V.write_obj(V.Path(path), tris)
    if join:   # nothing of a weapon hangs in the air (curios' chains and charms may)
        import weapon_joins
        weapon_joins.weld(path)
    import weapon_zfight          # overlapping boxes' faces in one plane flicker in game: pulled a hair apart
    weapon_zfight.fix(path)
    material(mesh, path)
    if preview:   # the copy the icon renders read (preview_vox's folder)
        img.save(VOX + '%s_f0.png' % mesh)
        V.write_obj(V.Path(VOX + '%s_f0.obj' % mesh), tris)
    V.to_item = TO_ITEM
    return sum(len(t) for t in tris.values())


DISPLAY_1H = {"thirdperson_righthand": {"rotation": [0, -90, 0], "translation": [0, 0.5, 0.5], "scale": [0.62, 0.62, 0.62]},
              "thirdperson_lefthand": {"rotation": [0, -90, 0], "translation": [0, 0.5, 0.5], "scale": [0.62, 0.62, 0.62]},
              "firstperson_righthand": {"rotation": [0, -90, 25], "translation": [1.13, 3.2, 1.13], "scale": [0.496, 0.496, 0.496]},
              "firstperson_lefthand": {"rotation": [0, 90, -25], "translation": [1.13, 3.2, 1.13], "scale": [0.496, 0.496, 0.496]}}
DISPLAY_2H = {k: {"rotation": [0, -90, 0], "translation": [0, 0.5, 0.5], "scale": [0.62, 0.62, 0.62]}
              for k in ("thirdperson_righthand", "thirdperson_lefthand", "firstperson_righthand", "firstperson_lefthand")}


def model(name, mesh, display, icon_name, overrides=None):
    icon = {'parent': 'minecraft:item/generated', 'textures': {'layer0': 'ashbound:item/' + icon_name}}
    m = {'loader': 'neoforge:separate_transforms', 'gui_light': 'front',
         'base': {'loader': 'neoforge:obj', 'model': 'ashbound:models/mesh/%s.obj' % mesh, 'flip_v': True, 'display': display},
         'perspectives': {k: icon for k in ('gui', 'ground', 'fixed')}}
    if overrides:
        m['overrides'] = overrides
    G.dump(ASSETS + 'models/item/%s.json' % name, m)


def held(f):
    import voxkiln_gear as KG
    return KG.held(f)


def make(th, it, icons):
    """one weapon: its mesh(es), texture(s), item model(s); queue its icon(s) (name, yaw, pitch, fixed, diagonal)"""
    s, seed, spec = build(th, it)
    k, iid = it['kind'], it['id']
    if k == 'shield':
        export(s, iid, lambda p: (p[0] / 16, p[1] / 16, p[2] / 16))
        model(iid, iid, held('shield.json'), iid, [{'predicate': {'minecraft:blocking': 1}, 'model': 'ashbound:item/%s_blocking' % iid}])
        model(iid + '_blocking', iid, held('shield_blocking.json'), iid)
        icons.append((iid, 18, 10, False, False, (0.5, 0.5)))
    elif k == 'bow':
        sprite = lambda p: (p[0] / 16, p[1] / 16, p[2] / 16)  # noqa: E731
        export(s, iid, sprite)
        icons.append((iid, 0, 0, True, False, None))
        overrides = []
        for n, (pull, at_pull) in enumerate([(0.35, None), (0.7, 0.65), (1.0, 0.9)]):
            nm = '%s_pulling_%d' % (iid, n)
            bb = bow(th, spec, seed, it['boss'], pull, True, nm)
            bb.shaders = th.shaders
            export(bb, nm, sprite)
            icons.append((nm, 0, 0, True, False, None))
            model(nm, nm, held('bow.json'), nm)
            pred = {'minecraft:pulling': 1}
            if at_pull:
                pred['minecraft:pull'] = at_pull
            overrides.append({'predicate': pred, 'model': 'ashbound:item/' + nm})
        model(iid, iid, held('bow.json'), iid, overrides)
    else:
        export(s, iid)
        model(iid, iid, DISPLAY_2H if k in ('twohander',) else DISPLAY_1H, iid)
        icons.append((iid, 0, 0, False, True, None))


def port_old(it, icons_done):
    """an old Ashbound weapon, as it was (mesh, textures, hand pose); its icon outlined like the rest"""
    iid = it['id']
    src = OLD
    if not os.path.exists(src + 'models/mesh/%s.obj' % iid):
        return False
    shutil.copy(src + 'models/mesh/%s.obj' % iid, ASSETS + 'models/mesh/%s.obj' % iid)
    material(iid, ASSETS + 'models/mesh/%s.obj' % iid)
    shutil.copy(src + 'textures/item/%s_3d.png' % iid, ASSETS + 'textures/item/%s_3d.png' % iid)
    w, h = Image.open(ASSETS + 'textures/item/%s_3d.png' % iid).size
    if h >= 512:   # the old glowing ones are 8 frames stacked: without the .mcmeta the UVs land on the wrong rows
        with open(ASSETS + 'textures/item/%s_3d.png.mcmeta' % iid, 'w', encoding='utf-8') as f:
            json.dump({'animation': {'frametime': 3, 'interpolate': True, 'width': w, 'height': h // 8}}, f)
    if os.path.exists(src + 'textures/item/%s.png' % iid):
        G.outline(src + 'textures/item/%s.png' % iid, ASSETS + 'textures/item/%s.png' % iid)
        icons_done.add(iid)
    try:
        disp = json.load(open(src + 'models/item/%s_held.json' % iid, encoding='utf-8')).get('display', DISPLAY_1H)
    except FileNotFoundError:
        disp = DISPLAY_2H if it['kind'] == 'twohander' else DISPLAY_1H
    model(iid, iid, disp, iid)
    return True


# ---------------------------------------------------------------- icons: one Blender run for a whole batch

def render_icons(icons):
    if not icons:
        return
    spec = os.path.join(GAME, 'tools', 'renders', 'icon_batch.json')
    json.dump(icons, open(spec, 'w'))
    subprocess.run([BLENDER, '-b', '-P', GAME + 'tools/blender/weapon_icons.py', '--', spec], check=True, capture_output=True)
    for (name, *_rest) in icons:
        big = VOX + 'icon_%s_big.png' % name
        if not os.path.exists(big):
            print('no icon render for', name)
            continue
        sm = Image.open(big).convert('RGBA').resize((64, 64), Image.LANCZOS)
        tmp = VOX + 'icon_%s_64.png' % name
        sm.save(tmp)
        G.outline(tmp, ASSETS + 'textures/item/%s.png' % name)


def sheet(gate, ids):
    """the gate's weapons' icons side by side, big, to judge them"""
    tiles = [Image.open(ASSETS + 'textures/item/%s.png' % i).convert('RGBA') for i in ids if os.path.exists(ASSETS + 'textures/item/%s.png' % i)]
    if not tiles:
        return
    cols = 8
    rows = (len(tiles) + cols - 1) // cols
    out = Image.new('RGBA', (cols * 136, rows * 136), (34, 30, 28, 255))
    for k, t in enumerate(tiles):
        out.paste(t.resize((128, 128), Image.NEAREST), ((k % cols) * 136 + 4, (k // cols) * 136 + 4), t.resize((128, 128), Image.NEAREST))
    os.makedirs(GAME + 'tools/renders', exist_ok=True)
    out.save(GAME + 'tools/renders/weapons_%s.png' % gate)


KEEP = {'kiln_bulwark', 'kiln_longbow'}   # made by tools/voxkiln_gear.py, approved as they are

# ---------------------------------------------------------------- the drops old Ashbound didn't make

def mat_models():
    fr, sk = THEMES['frost'], THEMES['silk']
    out = []
    s = Sword('rime_shard')                     # a cluster of ice crystals off a frozen marcher
    for (x, z, h, w, lean) in ((0, 0, 9, 2.4, 0), (-2.2, 0.6, 6, 1.8, 25), (2.0, -0.4, 7, 1.9, -20), (0.8, 1.8, 5, 1.4, -8)):
        bx(s, x, 0, z, w, h, w, "glow", glow=True, rots=(("z", lean),), pivot=(x, 0, z))
        bx(s, x, 0, z, w * 0.5, h * 0.8, w * 0.5 + 0.1, "white", glow=True, rots=(("z", lean),), pivot=(x, 0, z))
    bx(s, 0, -1, 0, 6, 1.4, 4, "dark")
    out.append((s, fr))
    s = Sword('frozen_fletch')                  # an arrow's fletching, iced over
    bx(s, 0, -6, 0, 0.8, 14, 0.8, "wood")
    for side in (1, -1):
        for k in range(4):
            seg(s, (0, -4 + k * 2.0), (side * 2.6, -5.2 + k * 2.0), 1.6, 0.4, "acc")
    for k in range(3):
        bx(s, (k - 1) * 1.6, -6.6 + k * 1.4, 0, 0.6, 2.0, 0.6, "glow", glow=True)
    bx(s, 0, 8, 0, 1.6, 2.2, 0.6, "blade")
    out.append((s, fr))
    s = Sword('marshals_heart')                 # the Winter Marshal's heart, frozen round the last ember
    bx(s, 0, 0, 0, 7.0, 6.0, 5.0, "glow", glow=True)
    for side in (1, -1):
        bx(s, side * 1.8, 5.6, 0, 3.0, 2.4, 4.2, "glow", glow=True)
    bx(s, 0, -1.6, 0, 3.0, 2.0, 3.0, "glow", glow=True)
    bx(s, 0, 2.0, 0, 3.0, 3.0, 5.6, "acc", tag="ember")
    for (x, y) in ((-2.6, 7.6), (2.4, 7.4), (0, 8.0)):
        bx(s, x, y, 0, 0.8, 2.4, 0.8, "white", glow=True)
    out.append((s, fr))
    s = Sword('silk_thread')                    # a spool of the Archive's silk
    bx(s, 0, 0, 0, 6.0, 1.2, 6.0, "wood")
    bx(s, 0, 7.0, 0, 6.0, 1.2, 6.0, "wood")
    bx(s, 0, 1.2, 0, 4.6, 5.8, 4.6, "acc")
    for k in range(5):
        bx(s, 0, 1.6 + k * 1.1, 0, 4.9, 0.4, 4.9, "acc")
    seg(s, (2.3, 3.0), (5.0, -1.0), 0.4, 0.4, "acc")
    out.append((s, sk))
    s = Sword('ink_gland')                      # a lector's ink gland, still glowing
    bx(s, 0, 0, 0, 5.4, 6.0, 4.6, "dark")
    bx(s, 0, 1.0, 0, 3.6, 4.0, 4.9, "glow", glow=True)
    bx(s, 0, 6.0, 0, 2.0, 2.4, 2.0, "dark")
    bx(s, 0.4, 8.4, 0, 1.0, 1.4, 1.0, "glow", glow=True)
    for side in (1, -1):
        seg(s, (side * 2.4, 0.6), (side * 4.0, -1.6), 0.7, 0.7, "dark")
    out.append((s, sk))
    s = Sword('queens_spinneret')               # the Silk Queen's spinneret: chitin, silk still drawn out of it
    for k, w in enumerate((5.4, 4.6, 3.8, 3.0, 2.2)):
        bx(s, 0, k * 1.8, 0, w, 1.9, w, "dark")
        bx(s, 0, k * 1.8 + 0.3, 0, w + 0.3, 0.5, w + 0.3, "blade")
    for side in (1, -1):
        seg(s, (side * 0.6, 9.0), (side * 2.6, 13.0), 0.4, 0.4, "acc")
    bx(s, 0, 9.0, 0, 1.4, 1.4, 1.4, "glow", glow=True)
    out.append((s, sk))
    out += [(fn(), THEMES[g]) for g, fn in _v2.MATS]
    return out


APPRENTICE = [{'id': 'apprentice_%s_staff' % k, 'kind': k, 'boss': False} for k in ('black', 'white', 'summon')]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    gear = json.load(open(G.OUT, encoding='utf-8'))
    icons, done = [], set()
    for g in gear:
        th = THEMES.get(g['gate'])
        todo = [it for it in g['weapons'] if (not args or g['gate'] in args or it['id'] in args) and it['id'] not in hand_made()]
        if th is None:              # a Roster v2 dungeon whose theme isn't written yet
            continue
        for it in todo:
            if it['id'] in KEEP:
                continue
            if it.get('old'):
                if port_old(it, done):
                    print('ported', it['id'])
                    continue
            make(th, it, icons)
            print('made', it['id'])
    if not args or 'apprentice' in args:
        for it in APPRENTICE:
            make(THEMES['crypt'] if it['kind'] == 'white' else THEMES['gallows'] if it['kind'] == 'summon' else THEMES['foundry'], it, icons)
    if not args or 'mats' in args:
        for m, th in mat_models():
            m.shaders = th.shaders
            export(m, m.name)
            icons.append((m.name, 25, 15, False, False, None))
    if '--icons' in sys.argv:
        render_icons(icons)
    if '--sheet' in sys.argv or '--icons' in sys.argv:
        for g in gear:
            if (not args or g['gate'] in args) and g['gate'] in THEMES:
                sheet(g['gate'], [it['id'] for it in g['weapons']])


if __name__ == '__main__':
    main()
