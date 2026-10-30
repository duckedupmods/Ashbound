"""The world's weapons: found in tower hoards, world chests and on elites, never crafted. Not sets: every one is its own
thing, with its own metals, its own glow and its own mark (a wolf's teeth, a molten core, a crescent, wings...).
The plain finds look decent, the rare ones fine, the epic ones dangerous and the legendaries spectacular.

Each is weaponforge.py's template for its type (sword, dagger, hammer, spear, two-hander, shield, bow, the three
staffs) dressed by a One theme: palettes picked by name from PAL, an emblem and a trim picked from the motifs below.

    python tools/worldarms.py [ids or rarities...] [--sheet]    meshes + textures into the assets; --sheet renders them
"""
import glob
import json
import math
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import weaponforge as W  # noqa: E402
from voxsword import ramp  # noqa: E402
from weaponforge import Theme, bx, chainp, ring_xy, seg  # noqa: E402

# ---------------------------------------------------------------- palettes, by name

PAL = {
    # metals
    "steel": ramp("#2a2e34", "#3e444c", "#565e68", "#727c86", "#929ca6", "#b4bec6", "#d4dce2", "#f0f4f6"),
    "worn_iron": ramp("#1c1a18", "#2a2724", "#3a3632", "#4c4741", "#605a52", "#787066", "#928a7e", "#aea698"),
    "bronze": ramp("#2a1606", "#432410", "#5e3618", "#7c4c22", "#9c6630", "#bc8444", "#d8a462", "#f0c88a"),
    "black_steel": ramp("#08080a", "#101014", "#18181e", "#22222a", "#2e2e38", "#3e3e4a", "#54545f", "#70707c"),
    "night": ramp("#060a1a", "#0a1228", "#101c3c", "#182a54", "#22386c", "#304a86", "#4a66a8", "#7a96d0"),
    "crimson": ramp("#1a0406", "#2e080c", "#460c12", "#62121a", "#801c22", "#a02a2c", "#c4443c", "#e8705c"),
    "white_gold": ramp("#6a5a3a", "#8c7a52", "#b09c6c", "#cec08a", "#e6dcae", "#f6f0d2", "#fffbec", "#ffffff"),
    "ice": ramp("#0e2a3a", "#164058", "#205a78", "#2e7898", "#4a9cbc", "#78c0da", "#b0e0f0", "#e8f8ff"),
    "obsidian": ramp("#050406", "#0c0a0e", "#141118", "#1c1822", "#26202e", "#30283a", "#3e344a", "#4e425c"),
    "bone": ramp("#3a3428", "#544c3c", "#706652", "#8e846c", "#aca286", "#c8bea4", "#e0d8c0", "#f4eedc"),
    "venom": ramp("#0a1a0c", "#122a14", "#1c3e1c", "#285426", "#366c30", "#4a883c", "#68a650", "#94c870"),
    "storm": ramp("#141a22", "#1e2630", "#2a3442", "#384454", "#485668", "#5c6c80", "#7a8a9e", "#a2b0c2"),
    # trims, wraps, woods
    "gold": ramp("#4a2e08", "#7a4c10", "#a87018", "#d0961f", "#ecbc34", "#ffdc6a"),
    "silver": ramp("#4a5058", "#6a727c", "#8e98a2", "#b4bec8", "#d8e0e8", "#f4f8fc"),
    "brass": ramp("#3a2410", "#5a3c1a", "#7c5626", "#a07436", "#c4964c", "#e2b868"),
    "copper": ramp("#2a1208", "#46200e", "#663016", "#88441e", "#ac5a28", "#d07a3a"),
    "iron": ramp("#16181c", "#22262c", "#30353c", "#40464e", "#525962", "#666e78"),
    "dark_iron": ramp("#0a0a0c", "#121216", "#1a1a20", "#24242c", "#2e2e38", "#3a3a46"),
    "red_cloth": ramp("#2a0606", "#460c0a", "#621410", "#801e16", "#a02a1e"),
    "brown_leather": ramp("#1e120a", "#2e1c10", "#422a18", "#583a22", "#704c2e"),
    "black_leather": ramp("#0a0808", "#141010", "#1e1818", "#2a2222", "#362c2c"),
    "green_cloth": ramp("#0a1a0c", "#122a14", "#1c3e1e", "#28542a", "#346c36"),
    "purple_cloth": ramp("#140a1c", "#20102c", "#2e1840", "#3e2256", "#502e6c"),
    "blue_cloth": ramp("#0a0e20", "#121a34", "#1c264a", "#283462", "#36447a"),
    "white_cloth": ramp("#8a8476", "#a8a292", "#c4beae", "#dcd8ca", "#eeeadf"),
    "fur": ramp("#2a2420", "#3e3630", "#544a42", "#6c6056", "#86786c"),
    "oak": ramp("#2a1c10", "#3c2a18", "#523a22", "#6a4c2e", "#82603a", "#9a7448"),
    "ash_wood": ramp("#1a1612", "#2a241e", "#3a322a", "#4c4238", "#605446", "#766856"),
    "dark_wood": ramp("#0e0a08", "#18120e", "#221a14", "#2e241c", "#3a2e24", "#48382c"),
    "pale_wood": ramp("#4a3e2e", "#64543e", "#806c50", "#9c8664", "#b8a07a", "#d2bc94"),
    "charred": ramp("#080606", "#100c0a", "#1a1410", "#241c16", "#30261c", "#3c3024"),
    # glows
    "g_ember": ramp("#3a0804", "#701204", "#a82406", "#e04a0a", "#ff7a1c", "#ffb04a", "#ffe08a", "#fff6d0"),
    "g_frost": ramp("#103870", "#1a5aa8", "#2a8ed8", "#4cb8f4", "#7cd8ff", "#b4ecff", "#eafaff"),
    "g_venom": ramp("#0e3a0a", "#1a6014", "#2c8a1e", "#4ab82c", "#7ce04a", "#b4f480", "#e8ffd0"),
    "g_void": ramp("#3a0a6a", "#5a14a0", "#7e26d4", "#a24cf4", "#c27cff", "#e0b4ff", "#f8ecff"),
    "g_blood": ramp("#3a0206", "#64060c", "#940c14", "#c41a20", "#ec3a34", "#ff7a66", "#ffd0c4"),
    "g_holy": ramp("#a07a20", "#d0a838", "#f0cc5a", "#ffe48a", "#fff0bc", "#fffae4", "#ffffff"),
    "g_star": ramp("#4a5aa0", "#6a80d0", "#94acf0", "#bcd0ff", "#dce8ff", "#f2f6ff", "#ffffff"),
    "g_storm": ramp("#2a5aa0", "#3c86d0", "#5cb0f0", "#8cd4ff", "#bcecff", "#e4f8ff", "#ffffff"),
    "g_ghost": ramp("#0a4a3a", "#147a5e", "#22a886", "#46d4aa", "#86f0cc", "#c4ffe8", "#f0fff8"),
    "g_phoenix": ramp("#a03404", "#d85a08", "#ff8a1a", "#ffb43c", "#ffd474", "#ffecb4", "#fffbe8"),
    "g_moon": ramp("#5a6a8a", "#7a8cac", "#9eaecc", "#c2cee4", "#dee6f4", "#f2f6fc", "#ffffff"),
    "g_plain": ramp("#2a3a2a", "#3e523e", "#566e56", "#728c72", "#90aa90", "#b4ccb4", "#dcecdc"),
    # the second forty: the mod structures' factions (brigands, corsairs, delvers, the Sky and Ash Legions...)
    "rust": ramp("#1a0c06", "#2c140a", "#42200e", "#5a2e14", "#74401c", "#8e5426", "#a86c34", "#c48a4a"),
    "sea_bronze": ramp("#0e2420", "#163a32", "#245046", "#356a58", "#4e8a6e", "#72a88a", "#9cc6a8", "#c8e4cc"),
    "sandstone": ramp("#3a2a18", "#5a4428", "#7a5e3a", "#9a7a4e", "#b89866", "#d2b484", "#e6cea4", "#f6e6c8"),
    "chitin": ramp("#0a0c06", "#141a0c", "#1e2814", "#2a381c", "#384a26", "#4a5e30", "#60763c", "#7a8e4c"),
    "basalt": ramp("#0c0e10", "#16191c", "#20242a", "#2a3038", "#343c46", "#404a56", "#4e5a68", "#5e6c7c"),
    "tarnished": ramp("#1c201e", "#2c3230", "#3e4644", "#525a58", "#68706c", "#828a84", "#a0a6a0", "#c0c4bc"),
    "cap": ramp("#2a0e0a", "#46160e", "#642214", "#86301c", "#a84428", "#c85e3a", "#e0845a", "#f2b088"),
    "ink": ramp("#06080c", "#0c1016", "#121a22", "#1a2430", "#22303e", "#2c3e4e", "#3a5062", "#4c6478"),
    "thornwood": ramp("#0e140a", "#18200e", "#222c14", "#2e3a1a", "#3a4a22", "#4a5c2c"),
    "rose_cloth": ramp("#2a0610", "#460a1a", "#641226", "#821c34", "#a02a44"),
    "sand_cloth": ramp("#5a4630", "#76603e", "#927a52", "#ae9668", "#c8b282"),
    "sea_cloth": ramp("#0a1e22", "#103038", "#18444e", "#225a66", "#2e727e"),
    "g_teal": ramp("#063a3a", "#0a6060", "#10908a", "#1ec4b4", "#4ae8d4", "#9cfaec", "#e0fff8"),
    "g_acid": ramp("#3a4a04", "#5a7008", "#86a010", "#b4d018", "#dcf040", "#f4ff90", "#fcffe0"),
    "g_spore": ramp("#4a0a3a", "#741460", "#a42488", "#d03cb0", "#f070d0", "#ffb0ec", "#fff0fc"),
    "g_rose": ramp("#4a0410", "#7a0a1c", "#aa142c", "#d82844", "#f4506a", "#ff90a0", "#ffe0e6"),
    "g_sea": ramp("#04304a", "#0a5070", "#108098", "#20b0c0", "#50d8dc", "#a0f4f0", "#e8fffc"),
    "g_sand": ramp("#5a3a08", "#8a5e10", "#b8861c", "#e0b030", "#f8d460", "#fff0a8", "#fffbe8"),
    "g_aurora": ramp("#103a6a", "#1a6a8a", "#22a08a", "#3ad08a", "#80f0a8", "#c4ffd8", "#f0fff6"),
    "g_soul": ramp("#10204a", "#1a3a7a", "#2a5aaa", "#4a86d4", "#80b4f0", "#c0dcff", "#f0f8ff"),
}


# ---------------------------------------------------------------- marks: emblems (at the guard / head / staff top)

def e_stud(s, cx, y, size, z):
    bx(s, cx, y - size * 0.35, 0, size * 0.6, size * 0.6, z * 0.8, "acc")


def e_gem(s, cx, y, size, z):
    bx(s, cx, y - size * 0.45, 0, size * 0.7, size * 0.8, z * 0.8, "acc")
    bx(s, cx, y - size * 0.32, 0, size * 0.36, size * 0.5, z * 1.05, "glow", glow=True)


def e_skull(s, cx, y, size, z):
    bx(s, cx, y - size * 0.5, 0, size * 0.8, size * 0.7, z * 0.9, "acc")
    bx(s, cx, y - size * 0.75, 0, size * 0.5, size * 0.3, z * 0.8, "acc")
    for sx in (-1, 1):
        bx(s, cx + sx * size * 0.18, y - size * 0.4, 0, size * 0.2, size * 0.2, z * 1.0, "glow", glow=True)


def e_wings(s, cx, y, size, z):
    e_gem(s, cx, y, size * 0.8, z)
    for sx in (-1, 1):
        for k, (a, l) in enumerate(((0.45, 1.1), (0.25, 0.95), (0.05, 0.75))):
            seg(s, (cx + sx * size * 0.25, y - size * 0.2 - k * size * 0.18),
                (cx + sx * size * (0.25 + l), y - size * 0.2 - k * size * 0.18 + size * a * 1.4), size * 0.17, z * 0.6, "acc")


def e_sun(s, cx, y, size, z):
    for k in range(8):
        a = k * math.pi / 4
        rr = 0.95 if k % 2 == 0 else 0.7
        seg(s, (cx + math.cos(a) * size * 0.3, y - size * 0.2 + math.sin(a) * size * 0.3),
            (cx + math.cos(a) * size * rr, y - size * 0.2 + math.sin(a) * size * rr), size * 0.16, z * 0.6, "acc")
    bx(s, cx, y - size * 0.5, 0, size * 0.62, size * 0.62, z * 1.05, "glow", glow=True)


def e_crescent(s, cx, y, size, z):
    n = 9
    for k in range(n):
        a = math.pi * (0.15 + 0.7 * k / (n - 1)) + math.pi
        p = (cx + math.cos(a) * size * 0.7, y + size * 0.2 + math.sin(a) * size * 0.7)
        bx(s, p[0], p[1] - size * 0.12, 0, size * 0.26, size * 0.26, z * 0.7, "acc")
    bx(s, cx, y - size * 0.35, 0, size * 0.32, size * 0.32, z * 1.05, "glow", glow=True)


def e_eye(s, cx, y, size, z):
    ring_xy(s, cx, y - size * 0.2, size * 0.55, size * 0.14, "acc", 10, depth=z * 0.7)
    bx(s, cx, y - size * 0.45, 0, size * 0.8, size * 0.5, z * 0.9, "dark")
    bx(s, cx, y - size * 0.38, 0, size * 0.36, size * 0.36, z * 1.05, "glow", glow=True)


def e_lion(s, cx, y, size, z):
    ring_xy(s, cx, y - size * 0.15, size * 0.55, size * 0.22, "acc", 12, depth=z * 0.75)
    bx(s, cx, y - size * 0.5, 0, size * 0.62, size * 0.7, z * 0.95, "acc")
    bx(s, cx, y - size * 0.62, 0, size * 0.3, size * 0.2, z * 1.05, "dark")


def e_claw(s, cx, y, size, z):
    bx(s, cx, y - size * 0.45, 0, size * 0.6, size * 0.6, z * 0.8, "acc")
    for k in (-1, 0, 1):
        seg(s, (cx + k * size * 0.25, y - size * 0.1), (cx + k * size * 0.45, y + size * 0.55), size * 0.16, z * 0.6, "acc")
    bx(s, cx, y - size * 0.3, 0, size * 0.25, size * 0.25, z * 1.0, "glow", glow=True)


def e_feathers(s, cx, y, size, z):
    for k in range(5):
        a = math.radians(-60 + k * 30)
        seg(s, (cx, y - size * 0.4), (cx + math.sin(a) * size, y - size * 0.4 + math.cos(a) * size * 0.9), size * 0.22, z * 0.5,
            "glow" if k % 2 else "acc", glow=bool(k % 2))
    bx(s, cx, y - size * 0.55, 0, size * 0.4, size * 0.4, z * 0.9, "acc")


def e_crystal(s, cx, y, size, z):
    for dx, a, h in ((0, 0, 1.0), (-0.3, 22, 0.7), (0.3, -22, 0.75)):
        bx(s, cx + dx * size, y - size * 0.4, 0, size * 0.28, size * h, z * 0.9, "glow", glow=True, rots=(("z", a),),
           pivot=(cx + dx * size, y - size * 0.4, 0))


def e_crown(s, cx, y, size, z):
    bx(s, cx, y - size * 0.55, 0, size * 1.0, size * 0.3, z * 0.9, "acc")
    for k in (-1, 0, 1):
        bx(s, cx + k * size * 0.38, y - size * 0.25, 0, size * 0.2, size * (0.55 if k == 0 else 0.4), z * 0.8, "acc")
        bx(s, cx + k * size * 0.38, y + size * (0.32 if k == 0 else 0.17), 0, size * 0.2, size * 0.2, z * 0.9, "glow", glow=True)


def e_anchor(s, cx, y, size, z):
    bx(s, cx, y - size * 0.7, 0, size * 0.22, size * 1.1, z * 0.8, "acc")
    bx(s, cx, y + size * 0.15, 0, size * 0.6, size * 0.18, z * 0.8, "acc")
    ring_xy(s, cx, y + size * 0.55, size * 0.18, size * 0.1, "acc", 8, depth=z * 0.7)
    for sx in (-1, 1):
        seg(s, (cx, y - size * 0.7), (cx + sx * size * 0.55, y - size * 0.35), size * 0.18, z * 0.75, "acc")
        seg(s, (cx + sx * size * 0.55, y - size * 0.35), (cx + sx * size * 0.62, y - size * 0.05), size * 0.14, z * 0.75, "acc")
    bx(s, cx, y - size * 0.25, 0, size * 0.2, size * 0.2, z * 1.0, "glow", glow=True)


def e_rose(s, cx, y, size, z):
    for k in range(5):   # petals round a glowing heart
        a = 2 * math.pi * k / 5 + 0.3
        bx(s, cx + math.cos(a) * size * 0.3, y - size * 0.45 + math.sin(a) * size * 0.3, 0, size * 0.45, size * 0.45, z * 0.8, "acc")
    bx(s, cx, y - size * 0.4, 0, size * 0.36, size * 0.36, z * 1.05, "glow", glow=True)
    for sx in (-1, 1):
        seg(s, (cx + sx * size * 0.3, y - size * 0.7), (cx + sx * size * 0.75, y - size * 0.95), size * 0.16, z * 0.6, "dark")


def e_mushroom(s, cx, y, size, z):
    bx(s, cx, y - size * 0.8, 0, size * 0.3, size * 0.55, z * 0.8, "acc")
    for k, w in enumerate((1.0, 0.8, 0.5)):
        bx(s, cx, y - size * 0.3 + k * size * 0.18, 0, size * w, size * 0.2, z * 0.9, "glow" if k == 0 else "acc", glow=k == 0)


def e_horns(s, cx, y, size, z):
    bx(s, cx, y - size * 0.5, 0, size * 0.6, size * 0.6, z * 0.9, "acc")
    for sx in (-1, 1):
        chainp(s, (cx + sx * size * 0.3, y - size * 0.1), [(size * 0.4, -sx * 70, size * 0.24, z * 0.6), (size * 0.35, -sx * 150, size * 0.18, z * 0.5),
                                                          (size * 0.25, sx * 150, size * 0.12, z * 0.4)], "acc")
    bx(s, cx, y - size * 0.35, 0, size * 0.24, size * 0.24, z * 1.0, "glow", glow=True)


EMBLEMS = {"stud": e_stud, "gem": e_gem, "skull": e_skull, "wings": e_wings, "sun": e_sun, "crescent": e_crescent,
           "eye": e_eye, "lion": e_lion, "claw": e_claw, "feathers": e_feathers, "crystal": e_crystal, "crown": e_crown,
           "anchor": e_anchor, "rose": e_rose, "mushroom": e_mushroom, "horns": e_horns}


# ---------------------------------------------------------------- marks: trims (along the blade / head, and the grip)

def t_plain(s, where, y0, y1, half, thick):
    if where == "blade":
        bx(s, 0, y0 + 1, 0, 0.7, (y1 - y0) * 0.6, thick + 0.05, "dark")


def t_wrap(s, where, y0, y1, half, thick):
    if where not in ("blade", "head"):
        for k in range(3):
            seg(s, (-half - 0.2, y0 + 0.8 + k * 1.6), (half + 0.2, y0 + 1.6 + k * 1.6), 0.45, thick + 0.2, "wrap")
    else:
        t_plain(s, where, y0, y1, half, thick)


def t_teeth(s, where, y0, y1, half, thick):
    if where in ("blade", "head"):
        y = y0 + 1.5
        while y < y1 - 2:
            seg(s, (half - 0.2, y), (half + 1.0, y + 0.9), 0.7, thick * 0.8, "blade")
            y += 2.0
    t_wrap(s, "haft", y0, y1, half, thick) if where not in ("blade", "head") else None


def t_core(s, where, y0, y1, half, thick):
    """a molten/glowing core down the blade, cracks off it"""
    if where in ("blade", "head"):
        bx(s, 0, y0 + 0.8, 0, max(0.8, half * 0.45), (y1 - y0) * 0.8, thick + 0.1, "glow", glow=True)
        for k in range(3):
            yy = y0 + 2 + k * (y1 - y0) * 0.25
            seg(s, (0, yy), ((1 if k % 2 else -1) * half * 0.8, yy + 1.2), 0.45, thick + 0.08, "glow", glow=True)
    else:
        bx(s, 0, y0 + (y1 - y0) * 0.5, 0, half * 2 + 0.4, 0.6, thick + 0.25, "glow", glow=True, tag="band")


def t_runes(s, where, y0, y1, half, thick):
    if where in ("blade", "head"):
        yy, k = y0 + 1.2, 0
        while yy < y1 - 1.5:
            bx(s, (0.3 if k % 3 == 0 else -0.3), yy, 0, 0.5 if k % 2 else 0.9, 1.0, thick + 0.08, "glow", glow=True)
            yy += 1.7
            k += 1
    else:
        for k in range(2):
            bx(s, 0, y0 + 1 + k * 2.4, 0, half * 2 + 0.4, 0.6, thick + 0.25, "glow", glow=True, tag="band")


def t_stars(s, where, y0, y1, half, thick):
    if where in ("blade", "head"):
        for k, (fx, fy) in enumerate(((0.3, 0.12), (-0.35, 0.28), (0.1, 0.42), (0.4, 0.55), (-0.25, 0.68), (0.15, 0.82))):
            sz = 0.8 if k % 2 else 0.55
            bx(s, fx * half, y0 + (y1 - y0) * fy, 0, sz, sz, thick + 0.1, "glow", glow=True)
    else:
        bx(s, 0, y0 + 0.6, 0, half * 2 + 0.5, 0.7, thick + 0.3, "acc", tag="band")


def t_filigree(s, where, y0, y1, half, thick):
    if where in ("blade", "head"):
        n = 4
        for k in range(n):
            yy = y0 + 1 + k * (y1 - y0 - 2) / n
            seg(s, (-half * 0.45, yy), (half * 0.45, yy + (y1 - y0) / n * 0.6), 0.4, thick + 0.08, "acc")
            seg(s, (half * 0.45, yy + (y1 - y0) / n * 0.3), (-half * 0.45, yy + (y1 - y0) / n * 0.9), 0.4, thick + 0.08, "acc")
    else:
        bx(s, 0, y0 + (y1 - y0) * 0.3, 0, half * 2 + 0.5, 0.7, thick + 0.3, "acc", tag="band")
        bx(s, 0, y0 + (y1 - y0) * 0.7, 0, half * 2 + 0.5, 0.7, thick + 0.3, "acc", tag="band")


def t_frost(s, where, y0, y1, half, thick):
    if where in ("blade", "head"):
        for k in range(3):
            yy = y0 + 1.5 + k * (y1 - y0) * 0.28
            bx(s, half + 0.4, yy, 0, 0.9, 2.0, thick * 0.9, "glow", glow=True, rots=(("z", -25),), pivot=(half + 0.4, yy, 0))
    else:
        bx(s, 0, y0 + 1, 0, half * 2 + 0.5, 1.0, thick + 0.4, "glow", glow=True, tag="band")


def t_lightning(s, where, y0, y1, half, thick):
    if where in ("blade", "head"):
        pts = [(0, y0 + 0.8)]
        k = 0
        while pts[-1][1] < y1 - 2:
            k += 1
            pts.append(((half * 0.5) * (1 if k % 2 else -1), pts[-1][1] + 2.0))
        for a, b in zip(pts, pts[1:]):
            seg(s, a, b, 0.6, thick + 0.1, "glow", glow=True)
    else:
        for k in range(3):
            bx(s, 0, y0 + 0.8 + k * 1.8, 0, half * 2 + 0.3, 0.5, thick + 0.25, "acc", tag="band")


def t_vines(s, where, y0, y1, half, thick):
    y, side = y0 + 0.5, 1
    while y < y1 - 1.5:
        seg(s, (-side * (half + 0.2), y), (side * (half + 0.2), y + 1.8), 0.5, thick + 0.25, "acc")
        bx(s, side * (half + 0.4), y + 1.6, 0, 0.9, 0.7, thick * 0.6, "glow", glow=True)
        y += 2.4
        side = -side


def t_bone(s, where, y0, y1, half, thick):
    y = y0 + 1
    while y < y1 - 1:
        bx(s, 0, y, 0, half * 2 + 0.5, 0.8, thick + 0.3, "acc", tag="knuckle")
        y += 2.6


def t_spikes(s, where, y0, y1, half, thick):
    if where in ("blade", "head"):
        for k in range(4):
            yy = y0 + 1.5 + k * (y1 - y0) * 0.22
            for sx in (-1, 1):
                seg(s, (sx * half * 0.9, yy), (sx * (half + 1.4), yy + 1.4), 0.7, thick * 0.9, "acc")
        bx(s, 0, y0 + 0.8, 0, 0.7, (y1 - y0) * 0.75, thick + 0.1, "glow", glow=True)
    else:
        t_bone(s, where, y0, y1, half, thick)


def t_drip(s, where, y0, y1, half, thick):
    if where in ("blade", "head"):
        for k in range(4):
            yy = y0 + 1.5 + k * (y1 - y0) * 0.22
            bx(s, (half - 0.3) * (1 if k % 2 else -0.6), yy, 0, 0.6, 1.2 + (k % 2) * 0.6, thick + 0.1, "glow", glow=True)
    else:
        t_wrap(s, where, y0, y1, half, thick)


def t_tassel(s, where, y0, y1, half, thick):
    if where not in ("blade", "head"):
        seg(s, (half, y0 + 0.5), (half + 1.4, y0 - 2.4), 0.6, 0.6, "wrap")
        seg(s, (half + 0.3, y0 + 0.5), (half + 2.0, y0 - 1.8), 0.5, 0.5, "wrap")
    t_wrap(s, where, y0, y1, half, thick)


TRIMS = {"plain": t_plain, "wrap": t_wrap, "teeth": t_teeth, "core": t_core, "runes": t_runes, "stars": t_stars,
         "filigree": t_filigree, "frost": t_frost, "lightning": t_lightning, "vines": t_vines, "bone": t_bone,
         "spikes": t_spikes, "drip": t_drip, "tassel": t_tassel}


class One(Theme):
    """one weapon's own look"""

    def __init__(self, iid, blade, dark, wrap, wood, glow, acc, emblem, trim, scars=0.04):
        super().__init__(iid, blade=PAL[blade], dark=PAL[dark], wrap=PAL[wrap], wood=PAL[wood], glow=PAL[glow], acc=PAL[acc],
                         scars=scars)
        self._emblem, self._trim = EMBLEMS[emblem], TRIMS[trim]

    def emblem(self, s, cx, y, size, z, boss):
        self._emblem(s, cx, y, size, z)

    def trim(self, s, where, y0, y1, half, thick, boss, seed):
        self._trim(s, where, y0, y1, half, thick)


# ---------------------------------------------------------------- the roster
# id, name, type, rarity, shape hints, (blade, dark, wrap, wood, glow, acc), emblem, trim, what it is
ARMS = [
    # swords
    ("hedge_knights_sword", "Hedge Knight's Sword", "sword", "uncommon", {"shape": "straight", "guard": "cross"},
     ("steel", "iron", "red_cloth", "oak", "g_plain", "brass"), "stud", "tassel", "a wandering knight's honest blade, a red tassel"),
    ("wolfbiter", "Wolfbiter", "sword", "rare", {"shape": "straight", "guard": "cross"},
     ("worn_iron", "dark_iron", "fur", "ash_wood", "g_frost", "silver"), "claw", "teeth", "wolf fangs set along one edge, a fur grip"),
    ("emberwake", "Emberwake", "sword", "epic", {"shape": "falchion", "guard": "emblem"},
     ("black_steel", "dark_iron", "black_leather", "charred", "g_ember", "copper"), "skull", "core", "black steel cracked over a molten heart"),
    ("starfall", "Starfall", "sword", "legendary", {"shape": "straight", "guard": "emblem"},
     ("night", "dark_iron", "blue_cloth", "dark_wood", "g_star", "silver"), "crescent", "stars", "a night sky forged into a blade, stars burning in it"),
    # daggers
    ("cutpurse_knife", "Cutpurse Knife", "dagger", "uncommon", {"shape": "straight"},
     ("bronze", "iron", "brown_leather", "oak", "g_plain", "brass"), "stud", "wrap", "a thief's short bronze knife"),
    ("vipers_kiss", "Viper's Kiss", "dagger", "rare", {"shape": "curved"},
     ("venom", "dark_iron", "green_cloth", "dark_wood", "g_venom", "bronze"), "gem", "drip", "a curved green blade that weeps venom"),
    ("shadowfang", "Shadowfang", "dagger", "epic", {"shape": "curved", "guard": "emblem"},
     ("obsidian", "dark_iron", "purple_cloth", "charred", "g_void", "dark_iron"), "eye", "runes", "a fang of night, void runes down it"),
    ("bloodmoon_kris", "Bloodmoon Kris", "dagger", "legendary", {"shape": "wavy", "guard": "emblem"},
     ("crimson", "dark_iron", "black_leather", "bone", "g_blood", "gold"), "crescent", "drip", "a waved crimson kris under a blood-red moon"),
    # hammers
    ("smiths_hammer", "Smith's Hammer", "hammer", "uncommon", {"shape": "block"},
     ("worn_iron", "iron", "brown_leather", "oak", "g_plain", "iron"), "stud", "wrap", "a blacksmith's hammer taken to war"),
    ("frostmaul", "Frostmaul", "hammer", "rare", {"shape": "spiked"},
     ("ice", "storm", "blue_cloth", "pale_wood", "g_frost", "silver"), "crystal", "frost", "a head of never-melting ice"),
    ("thunderhead", "Thunderhead", "hammer", "epic", {"shape": "bell"},
     ("storm", "dark_iron", "black_leather", "dark_wood", "g_storm", "brass"), "eye", "lightning", "a storm cloud caught in iron, lightning crawling on it"),
    ("worldbreaker", "Worldbreaker", "hammer", "legendary", {"shape": "barrel"},
     ("obsidian", "dark_iron", "red_cloth", "charred", "g_ember", "gold"), "crown", "spikes", "a mountain of obsidian with magma in its veins"),
    # spears
    ("boar_spear", "Boar Spear", "spear", "uncommon", {"shape": "leaf"},
     ("steel", "iron", "brown_leather", "ash_wood", "g_plain", "iron"), "stud", "wrap", "a hunter's leaf blade on ash"),
    ("gilded_partisan", "Gilded Partisan", "spear", "rare", {"shape": "halberd"},
     ("steel", "iron", "red_cloth", "dark_wood", "g_holy", "gold"), "lion", "filigree", "a palace guard's partisan, gold worked up the head"),
    ("wyrmtongue", "Wyrmtongue", "spear", "epic", {"shape": "glaive"},
     ("black_steel", "dark_iron", "purple_cloth", "dark_wood", "g_void", "copper"), "claw", "runes", "a wyrm's forked tongue on a black haft"),
    ("heavens_lance", "Heaven's Lance", "spear", "legendary", {"shape": "spike"},
     ("white_gold", "gold", "white_cloth", "pale_wood", "g_holy", "gold"), "wings", "core", "a lance of light with white-gold wings"),
    # two-handers
    ("mercenarys_zweihander", "Mercenary's Zweihander", "twohander", "uncommon", {"shape": "straight"},
     ("steel", "iron", "black_leather", "oak", "g_plain", "iron"), "stud", "plain", "a sellsword's long blade, plain and honest"),
    ("headsmans_cleaver", "Headsman's Cleaver", "twohander", "rare", {"shape": "cleaver"},
     ("worn_iron", "dark_iron", "black_leather", "dark_wood", "g_blood", "iron"), "skull", "drip", "a broad executioner's cleaver, never cleaned"),
    ("grave_reaver", "Grave Reaver", "twohander", "epic", {"shape": "flamberge", "guard": "emblem"},
     ("bone", "dark_iron", "black_leather", "bone", "g_ghost", "bone"), "skull", "bone", "a blade of bone with the dead's green fire in it"),
    ("dragonspine", "Dragonspine", "twohander", "legendary", {"shape": "spiked", "guard": "emblem"},
     ("crimson", "obsidian", "red_cloth", "charred", "g_phoenix", "gold"), "claw", "spikes", "a dragon's spine pulled out still burning"),
    # shields
    ("oak_round_shield", "Oak Round Shield", "shield", "uncommon", {"shape": "round"},
     ("iron", "iron", "brown_leather", "oak", "g_plain", "iron"), "stud", "plain", "planks and an iron rim, it does the job"),
    ("lion_crest", "Lion Crest", "shield", "rare", {"shape": "heater"},
     ("steel", "iron", "red_cloth", "red_cloth", "g_holy", "gold"), "lion", "filigree", "a knight's heater with a gold lion"),
    ("mirror_of_ash", "Mirror of Ash", "shield", "epic", {"shape": "kite"},
     ("black_steel", "dark_iron", "black_leather", "charred", "g_ember", "copper"), "eye", "core", "a black kite shield with a fire behind its eye"),
    ("aegis_of_dawn", "Aegis of Dawn", "shield", "legendary", {"shape": "tower"},
     ("white_gold", "gold", "white_cloth", "pale_wood", "g_holy", "gold"), "sun", "filigree", "a tower of white gold with the sunrise on it"),
    # bows
    ("hunters_bow", "Hunter's Bow", "bow", "uncommon", {},
     ("oak", "iron", "brown_leather", "oak", "g_plain", "iron"), "stud", "wrap", "yew and gut string, a hunter's bow"),
    ("raven_recurve", "Raven Recurve", "bow", "rare", {},
     ("black_leather", "dark_iron", "black_leather", "dark_wood", "g_moon", "silver"), "feathers", "wrap", "black recurve with raven feathers"),
    ("stormstring", "Stormstring", "bow", "epic", {},
     ("storm", "dark_iron", "blue_cloth", "storm", "g_storm", "brass"), "crystal", "lightning", "a bow strung with a strand of lightning"),
    ("phoenix_wing", "Phoenix Wing", "bow", "legendary", {},
     ("crimson", "gold", "red_cloth", "crimson", "g_phoenix", "gold"), "feathers", "core", "a phoenix's burning wing bent into a bow"),
    # black staffs
    ("charred_branch", "Charred Branch", "black", "uncommon", {},
     ("charred", "iron", "brown_leather", "charred", "g_ember", "iron"), "stud", "wrap", "a burnt branch that still smoulders"),
    ("ember_rod", "Ember Rod", "black", "rare", {},
     ("copper", "dark_iron", "red_cloth", "dark_wood", "g_ember", "copper"), "gem", "core", "a copper rod with a coal in its cage"),
    ("void_eye_staff", "Void Eye Staff", "black", "epic", {},
     ("obsidian", "dark_iron", "purple_cloth", "obsidian", "g_void", "dark_iron"), "eye", "runes", "a staff that stares back"),
    ("last_star", "The Last Star", "black", "legendary", {},
     ("night", "dark_iron", "blue_cloth", "night", "g_star", "silver"), "crescent", "stars", "the last star of the sky, caught in a crescent"),
    # white staffs
    ("pilgrims_staff", "Pilgrim's Staff", "white", "uncommon", {},
     ("pale_wood", "iron", "white_cloth", "pale_wood", "g_holy", "brass"), "stud", "tassel", "a walking staff worn smooth by roads"),
    ("moonpetal_staff", "Moonpetal Staff", "white", "rare", {},
     ("pale_wood", "silver", "blue_cloth", "pale_wood", "g_moon", "silver"), "crescent", "vines", "silver vines and moon-white petals"),
    ("seraph_staff", "Seraph Staff", "white", "epic", {},
     ("white_gold", "gold", "white_cloth", "pale_wood", "g_holy", "gold"), "wings", "filigree", "an angel's wings round a holy flame"),
    ("sunspire", "Sunspire", "white", "legendary", {},
     ("white_gold", "gold", "white_cloth", "white_gold", "g_phoenix", "gold"), "sun", "core", "a spire of gold carrying the noon sun"),
    # summon staffs
    ("bone_rattle", "Bone Rattle", "summon", "uncommon", {},
     ("bone", "iron", "brown_leather", "bone", "g_ghost", "bone"), "skull", "bone", "a shaman's rattle of knuckle bones"),
    ("raven_totem", "Raven Totem", "summon", "rare", {},
     ("dark_wood", "dark_iron", "black_leather", "dark_wood", "g_moon", "silver"), "feathers", "wrap", "a totem the ravens answer"),
    ("lichcaller", "Lichcaller", "summon", "epic", {},
     ("bone", "obsidian", "purple_cloth", "obsidian", "g_ghost", "bone"), "skull", "runes", "a lich's staff, the dead's green fire in its skull"),
    ("hollow_kings_crown", "Crown of the Hollow King", "summon", "legendary", {},
     ("obsidian", "gold", "purple_cloth", "obsidian", "g_void", "gold"), "crown", "stars", "a dead king's crown on a staff, his court still kneels"),

    # ======== the second forty: what the factions of the great ruins carry (Brigands, Corsairs, Delvers, Sporefolk,
    # the Sky and Ash Legions, the Salt-Cursed, Thornborn, Rimebound, Blightkin, the Fallen Order, the Brood, Voidborn)
    # swords
    ("brigands_falchion", "Brigand's Falchion", "sword", "uncommon", {"shape": "falchion", "guard": "cross"},
     ("rust", "iron", "red_cloth", "oak", "g_plain", "iron"), "stud", "wrap", "a hill bandit's chopping blade, more rust than steel"),
    ("corsairs_cutlass", "Corsair's Cutlass", "sword", "rare", {"shape": "curved", "guard": "swept"},
     ("steel", "sea_bronze", "sea_cloth", "dark_wood", "g_sea", "brass"), "anchor", "wrap", "a drowned captain's cutlass, the sea still in its guard"),
    ("thornheart", "Thornheart", "sword", "epic", {"shape": "leaf", "guard": "emblem"},
     ("thornwood", "dark_iron", "rose_cloth", "thornwood", "g_rose", "rose_cloth"), "rose", "vines", "a blade of braided briar with a rose blooming at its heart"),
    ("chainsworn", "Chainsworn", "sword", "legendary", {"shape": "straight", "guard": "emblem"},
     ("tarnished", "dark_iron", "blue_cloth", "dark_wood", "g_soul", "silver"), "crown", "runes", "the Fallen Order's oath-blade, bound in chains, a knight's soul in its reliquary"),
    # daggers
    ("tunnel_rats_shiv", "Tunnel Rat's Shiv", "dagger", "uncommon", {"shape": "stiletto"},
     ("worn_iron", "iron", "brown_leather", "oak", "g_plain", "copper"), "stud", "wrap", "a sharpened drill bit on a rag grip"),
    ("gillblade", "Gillblade", "dagger", "rare", {"shape": "curved"},
     ("cap", "dark_iron", "brown_leather", "thornwood", "g_spore", "bone"), "mushroom", "drip", "a sporefolk sickle, gills under its edge breathing spores"),
    ("mantis_talon", "Mantis Talon", "dagger", "epic", {"shape": "curved", "guard": "emblem"},
     ("venom", "dark_iron", "black_leather", "chitin", "g_venom", "chitin"), "claw", "teeth", "a brood reaper's foreleg, its hooked edge saw-toothed"),
    ("void_splinter", "Void Splinter", "dagger", "legendary", {"shape": "stiletto", "guard": "emblem"},
     ("obsidian", "dark_iron", "purple_cloth", "obsidian", "g_void", "silver"), "eye", "runes", "a blade of the void, broken into shards that float in line"),
    # hammers
    ("miners_maul", "Miner's Maul", "hammer", "uncommon", {"shape": "block"},
     ("worn_iron", "iron", "brown_leather", "oak", "g_ember", "copper"), "stud", "wrap", "a delver's sledge, a lamp-hook still on its haft"),
    ("barnacle_maul", "Barnacle Maul", "hammer", "rare", {"shape": "barrel"},
     ("sea_bronze", "sea_bronze", "sea_cloth", "dark_wood", "g_sea", "sea_bronze"), "anchor", "bone", "a ship's capstan, crusted with barnacles, on a mast-spar"),
    ("rockgrinder", "Rockgrinder", "hammer", "epic", {"shape": "block"},
     ("rust", "dark_iron", "black_leather", "dark_wood", "g_ember", "brass"), "gem", "core", "a steam driller's engine: a drill for a face, a boiler for a heart"),
    ("legions_pillar", "Legion's Pillar", "hammer", "legendary", {"shape": "block"},
     ("basalt", "obsidian", "black_leather", "charred", "g_teal", "gold"), "horns", "core", "a basalt column torn from the Ash Legion's gate, teal fire in its joins"),
    # spears
    ("whalers_harpoon", "Whaler's Harpoon", "spear", "uncommon", {"shape": "hook"},
     ("worn_iron", "iron", "sea_cloth", "oak", "g_plain", "iron"), "stud", "tassel", "a barbed iron harpoon, its line still knotted on"),
    ("dune_pilum", "Dune Pilum", "spear", "rare", {"shape": "needle"},
     ("bronze", "bronze", "sand_cloth", "pale_wood", "g_sand", "gold"), "sun", "filigree", "a salt legionary's javelin, bronze bright from the sand"),
    ("wardens_bardiche", "Warden's Bardiche", "spear", "epic", {"shape": "halberd"},
     ("black_steel", "dark_iron", "fur", "dark_wood", "g_frost", "ice"), "crystal", "frost", "the Rime Warden's bardiche: a black crescent rimed in ice, the cell keys still hung on it"),
    ("tidecallers_trident", "Tidecaller's Trident", "spear", "legendary", {"shape": "spike"},
     ("sea_bronze", "sea_bronze", "sea_cloth", "dark_wood", "g_sea", "gold"), "anchor", "core", "a drowned god's trident, a whirlpool turning round its tines"),
    # two-handers
    ("barrowsteel_greatsword", "Barrowsteel Greatsword", "twohander", "uncommon", {"shape": "straight"},
     ("worn_iron", "dark_iron", "fur", "oak", "g_ghost", "bronze"), "stud", "plain", "an old warrior's greatsword, dug out of a barrow mound"),
    ("dune_cleaver", "Dune Cleaver", "twohander", "rare", {"shape": "cleaver"},
     ("bronze", "dark_iron", "sand_cloth", "dark_wood", "g_sand", "gold"), "sun", "runes", "a broad bronze cleaver of the Salt Khan's riders"),
    ("chimera_jaw", "Chimera Jaw", "twohander", "epic", {"shape": "cleaver", "guard": "emblem"},
     ("bone", "dark_iron", "black_leather", "bone", "g_acid", "brass"), "skull", "drip", "a vat-grown beast's jawbone, teeth down both edges, acid between them"),
    ("kingsbarrow", "Kingsbarrow", "twohander", "legendary", {"shape": "straight", "guard": "emblem"},
     ("black_steel", "dark_iron", "fur", "dark_wood", "g_soul", "gold"), "crown", "runes", "the Barrow King's greatsword, his crowned dead still riding its edge"),
    # shields
    ("raiders_targe", "Raider's Targe", "shield", "uncommon", {"shape": "round"},
     ("rust", "iron", "brown_leather", "oak", "g_plain", "iron"), "stud", "plain", "a bandit's targe, a spike in its boss"),
    ("legion_scutum", "Legion Scutum", "shield", "rare", {"shape": "tower"},
     ("bronze", "bronze", "red_cloth", "red_cloth", "g_sand", "gold"), "sun", "filigree", "a legionary's curved scutum, a gold sun on red"),
    ("brood_carapace", "Brood Carapace", "shield", "epic", {"shape": "kite"},
     ("chitin", "dark_iron", "black_leather", "chitin", "g_venom", "chitin"), "eye", "spikes", "a hive soldier's back-plate, mandibles at its brow, eyes that still watch"),
    ("gryphon_aegis", "Gryphon Aegis", "shield", "legendary", {"shape": "round"},
     ("bronze", "bronze", "white_cloth", "pale_wood", "g_storm", "gold"), "wings", "filigree", "the Sky Legion's bronze aspis, a gryphon's head on it and its wings spread"),
    # bows
    ("poachers_bow", "Poacher's Bow", "bow", "uncommon", {},
     ("ash_wood", "iron", "fur", "ash_wood", "g_plain", "iron"), "stud", "wrap", "a short bow wrapped in rabbit fur"),
    ("thornbow", "Thornbow", "bow", "rare", {},
     ("thornwood", "dark_iron", "rose_cloth", "thornwood", "g_rose", "rose_cloth"), "rose", "vines", "a living briar bent into a bow, roses on its limbs"),
    ("kraken_bow", "Kraken Bow", "bow", "epic", {},
     ("ink", "sea_bronze", "sea_cloth", "ink", "g_sea", "sea_bronze"), "eye", "drip", "two kraken arms for limbs, suckers down them, an ink-black eye at the grip"),
    ("khans_horn", "The Khan's Horn", "bow", "legendary", {},
     ("bone", "gold", "sand_cloth", "bone", "g_sand", "gold"), "sun", "filigree", "the Salt Khan's great horn bow, ram's horns curling at its tips, a sandstorm in its string"),
    # black staffs
    ("vat_stirrer", "Vat Stirrer", "black", "uncommon", {},
     ("brass", "iron", "brown_leather", "dark_wood", "g_acid", "brass"), "stud", "drip", "an alchemist's stirring rod, still dripping"),
    ("augurs_rod", "Augur's Rod", "black", "rare", {},
     ("basalt", "obsidian", "black_leather", "basalt", "g_teal", "gold"), "horns", "core", "an Ash Legion augur's rod, teal fire in a basalt cage"),
    ("alembic_of_ruin", "Alembic of Ruin", "black", "epic", {},
     ("brass", "dark_iron", "black_leather", "dark_wood", "g_venom", "copper"), "gem", "drip", "a glass alembic of boiling acid in brass coils"),
    ("riftcaller", "Riftcaller", "black", "legendary", {},
     ("obsidian", "dark_iron", "purple_cloth", "obsidian", "g_void", "silver"), "eye", "stars", "the Void Herald's staff: a broken ring with the void between its halves"),
    # white staffs
    ("censer_staff", "Censer Staff", "white", "uncommon", {},
     ("tarnished", "iron", "white_cloth", "dark_wood", "g_holy", "brass"), "stud", "tassel", "a chaplain's censer on a pole, its smoke still sweet"),
    ("oracles_laurel", "Oracle's Laurel", "white", "rare", {},
     ("white_gold", "bronze", "white_cloth", "pale_wood", "g_holy", "gold"), "crown", "vines", "a Sky Legion oracle's staff, a gold laurel round its light"),
    ("everbloom", "Everbloom", "white", "epic", {},
     ("thornwood", "dark_iron", "rose_cloth", "thornwood", "g_rose", "rose_cloth"), "rose", "vines", "a rose that never stops opening, its petals light"),
    ("auroras_vigil", "Aurora's Vigil", "white", "legendary", {},
     ("ice", "silver", "white_cloth", "ice", "g_aurora", "silver"), "crystal", "frost", "an ice crown on a staff, the northern lights hanging from it"),
    # summon staffs
    ("kennel_crook", "Kennel Crook", "summon", "uncommon", {},
     ("worn_iron", "iron", "red_cloth", "oak", "g_ghost", "iron"), "claw", "wrap", "a hound master's crook, a collar hung on it"),
    ("broodcaller", "Broodcaller", "summon", "rare", {},
     ("chitin", "dark_iron", "black_leather", "chitin", "g_venom", "chitin"), "eye", "drip", "an egg sac on a stalk; something inside answers"),
    ("sporemother", "Sporemother", "summon", "epic", {},
     ("cap", "dark_iron", "brown_leather", "thornwood", "g_spore", "bone"), "mushroom", "vines", "an elder cap's staff, a cluster of glowing caps and its spore-children hanging"),
    ("bone_gate", "The Bone Gate", "summon", "legendary", {},
     ("bone", "obsidian", "black_leather", "bone", "g_soul", "bone"), "skull", "bone", "an arch of bones on a staff; the dead reach out of it"),
]

RARITY_ORDER = ["uncommon", "rare", "epic", "legendary"]
RANK = {"uncommon": "D", "rare": "C", "epic": "B", "legendary": "A"}   # where each stands on the dungeon ladder
# whose element a staff casts (its bolt, its heal's colour, what it summons): by its glow, a few by name
HOME = {"g_ember": "foundry", "g_phoenix": "obsidian_labyrinth", "g_frost": "frost", "g_void": "silk", "g_star": "temple",
        "g_moon": "temple", "g_holy": "crypt", "g_ghost": "ossuary", "g_storm": "storm_bastion", "g_venom": "plague",
        "g_blood": "bloodmoon_court", "g_plain": "brigands_gorge", "g_teal": "obsidian_labyrinth", "g_acid": "plague",
        "g_spore": "mirefen_coven", "g_rose": "rotwood", "g_sea": "tide_chapel", "g_sand": "sandsunk_tomb",
        "g_aurora": "frost", "g_soul": "crypt"}
HOME_BY_ID = {"raven_totem": "rookery", "hollow_kings_crown": "temple", "kennel_crook": "brigands_gorge",
              "broodcaller": "silk", "bone_gate": "ossuary"}


def items(only=()):
    for iid, name, kind, rar, hint, pal, emb, trim, about in ARMS:
        if only and iid not in only and rar not in only and kind not in only:
            continue
        th = One(iid, *pal, emb, trim, scars=0.06 if rar == "uncommon" else 0.03)
        yield rar, th, {"id": iid, "name": name, "kind": kind, "boss": rar in ("epic", "legendary")}, hint


def to_game():
    """everything the mod needs: meshes, item models (3D in the slot), Epic Fight capabilities, names, world_arms.json"""
    import gear as G
    import gui3d
    import worldarms_hero as H
    flat = lambda p: (p[0] / 16, p[1] / 16, p[2] / 16)  # noqa: E731
    out, lang = [], json.load(open(W.ASSETS + "lang/en_us.json", encoding="utf-8"))
    for iid, name, kind, rar, hint, pal, emb, trim, about in ARMS:
        th = One(iid, *pal, emb, trim, scars=0.06 if rar == "uncommon" else 0.03)
        it = {"id": iid, "name": name, "kind": kind, "boss": rar in ("epic", "legendary")}
        W.HINTS[iid] = hint
        hero = iid in H.HERO
        s = H.build(th, it) if hero else W.build(th, it)[0]
        if kind == "shield":
            W.export(s, iid, flat, preview=False)
            W.model(iid, iid, W.held("shield.json"), iid, [{"predicate": {"minecraft:blocking": 1}, "model": "ashbound:item/%s_blocking" % iid}])
            W.model(iid + "_blocking", iid, W.held("shield_blocking.json"), iid)
        elif kind == "bow":
            if hero:
                on_bow(s)
            W.export(s, iid, flat, preview=False)
            overrides = []
            for n, (pull, at) in enumerate([(0.35, None), (0.7, 0.65), (1.0, 0.9)]):
                nm = "%s_pulling_%d" % (iid, n)
                bb = H.build(th, it, pull=pull, arrow=True, name=nm) if hero else W.bow(th, dict(it, **hint), 0, it["boss"], pull, True, nm)
                if hero:
                    on_bow(bb)
                bb.shaders = th.shaders
                W.export(bb, nm, flat, preview=False)
                W.model(nm, nm, W.held("bow.json"), iid)
                pred = {"minecraft:pulling": 1}
                if at:
                    pred["minecraft:pull"] = at
                overrides.append({"predicate": pred, "model": "ashbound:item/" + nm})
            W.model(iid, iid, W.held("bow.json"), iid, overrides)
        else:
            W.export(s, iid, preview=False)
            W.model(iid, iid, W.DISPLAY_2H if kind == "twohander" else W.DISPLAY_1H, iid)
        # 3D in the slot, as gui3d does it
        path = W.ASSETS + "models/item/%s.json" % iid
        m = json.load(open(path, encoding="utf-8"))
        r = gui3d.pose(iid, kind)
        sc, tr = gui3d.fit(iid, r)
        rot = gui3d.euler_xyz(r)
        disp = m["base"].setdefault("display", {})
        disp["gui"] = disp["fixed"] = {"rotation": rot, "translation": tr, "scale": [round(sc, 4)] * 3}
        disp["ground"] = {"rotation": rot, "translation": [round(v * 0.55, 3) for v in tr[:2]] + [0], "scale": [round(sc * 0.55, 4)] * 3}
        m["perspectives"] = {}
        m["gui_light"] = "side"
        json.dump(m, open(path, "w", encoding="utf-8"), indent=1)
        rank = RANK[rar]
        row = {"id": iid, "name": name, "kind": kind, "rarity": rar, "rank": rank, "about": about,
               "home": HOME_BY_ID.get(iid, HOME[pal[4]])}
        if kind in G.STATS:
            ef, dmg, spd, imp, neg, strikes = G.stats({"kind": kind, "rank": rank, "boss": rar == "legendary"})
            row["damage"], row["speed"] = dmg, spd
            cap = {"type": ("ashbound:" if ef == "greatsword" else "epicfight:") + ef}
            if ef not in ("shield", "bow"):
                cap["attributes"] = {"common": {"impact": imp, "armor_negation": neg, "max_strikes": strikes}}
            G.dump(G.DATA + "capabilities/weapons/%s.json" % iid, cap)
        else:
            G.dump(G.DATA + "capabilities/weapons/%s.json" % iid, G.STAFF_CAP)
        out.append(row)
        lang["item.ashbound." + iid] = name
        print("game", rar, iid)
    # the drawn bows and raised shields are never in a slot: no picture perspectives (there are no picture icons)
    for row in out:
        for extra in glob.glob(W.ASSETS + "models/item/%s_*.json" % row["id"]):
            m = json.load(open(extra, encoding="utf-8"))
            if "perspectives" in m:
                m["perspectives"] = {}
                json.dump(m, open(extra, "w", encoding="utf-8"), indent=1)
    G.dump(os.path.join(W.GAME, "src/main/resources/ashbound/world_arms.json"), out)
    G.dump(W.ASSETS + "lang/en_us.json", lang)


def on_bow(s):
    """a hero bow's emblems are drawn on a blade's plane (z 0): put them on the bow's (W.BZ), or they float half a block off"""
    for b in s.boxes:
        if b.lo[2] + b.size[2] / 2 < W.BZ / 2:
            b.lo, b.pivot = (b.lo[0], b.lo[1], b.lo[2] + W.BZ), (b.pivot[0], b.pivot[1], b.pivot[2] + W.BZ)


def main():
    if "--export" in sys.argv:
        return to_game()
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    done = []
    for rar, th, it, hint in items(only):
        W.HINTS[it["id"]] = hint
        import worldarms_hero as H
        s = H.build(th, it) if it["id"] in H.HERO else W.build(th, it)[0]
        flat = (lambda p: (p[0] / 16, p[1] / 16, p[2] / 16)) if it["kind"] in ("shield", "bow") else W.TO_ITEM
        tris = W.export(s, it["id"], flat, preview=False)
        done.append((rar, it))
        print(rar, it["id"], tris, "tris")
    if "--sheet" in sys.argv:
        import gui3d
        prev = []
        # one row a rarity, the types in the same column order
        kinds = ["sword", "dagger", "hammer", "spear", "twohander", "shield", "bow", "black", "white", "summon"]
        done.sort(key=lambda d: (RARITY_ORDER.index(d[0]), kinds.index(d[1]["kind"])))
        for rar, it in done:
            r = gui3d.pose(it["id"], it["kind"])
            sc, t = gui3d.fit(it["id"], r)
            prev.append({"gate": "worldarms", "id": it["id"], "r": r, "s": sc, "t": t})
        out = os.path.join(W.GAME, "tools/renders/worldarms")
        os.makedirs(out, exist_ok=True)
        spec = os.path.join(out, "batch.json")
        json.dump({"assets": W.ASSETS, "out": out, "items": prev, "res": 192, "cols": 10}, open(spec, "w"))
        r = subprocess.run([W.BLENDER, "-b", "-P", os.path.join(W.GAME, "tools/blender/gui_preview.py"), "--", spec],
                           capture_output=True, text=True)
        print([l for l in r.stdout.splitlines() if l.startswith("sheet")] or r.stderr[-1500:])


if __name__ == "__main__":
    main()
