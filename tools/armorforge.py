"""Every dungeon's four armour sets from the gear table (tools/gear.py), for the ones old Ashbound didn't make: a
CLASS template (robe, light, medium, heavy) in the DUNGEON's theme from tools/weaponforge.py (its metals, cloth,
glow, its emblem worked into the helm and the chest, its trim on the shoulders). Built like old Ashbound's sets
(E:/Ashbound/tools/voxarmor*.py: chunky boxes on the vanilla player's bones, painted per texel) and exported the
same way into tools/armor_src/, where tools/efarmor.py picks them up and puts them on Epic Fight's body.

    robe    a deep hood with the emblem on its brow, a robe with a stole down the front (efarmor adds the skirt),
            a shoulder mantle, wide sleeves; cloth wraps, soft boots
    light   a hood and a half mask, a leather jerkin with straps and small shoulder cops, breeches with knee
            pads and pouches, tall buckled boots
    medium  an open helm with cheek plates, mail with a breastplate over it, rounded pauldrons, bracers;
            tassets over mail, plated boots
    heavy   a great helm with a visor slit and a crest, a cuirass, layered pauldrons with the gate's trim,
            gorget and vambraces; cuisses and greaves with knee cops, sabatons

Units: 1 = 1/16 block, feet at 0, facing +z, right hand -x (as voxarmor.py).

    python tools/armorforge.py [sets or gates...]        then python tools/efarmor.py <sets>
"""
import json
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, 'E:/Ashbound/tools')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import voxsword as V  # noqa: E402
from voxsword import Sword, ramp, shade, fbm, h3, metal_shader, wrap_shader  # noqa: E402
from voxboss import Part, PB, C  # noqa: E402
import voxmob as M  # noqa: E402
import gear as G  # noqa: E402
import weaponforge as W  # noqa: E402
import armorsets as AS  # noqa: E402

OUT = Path(G.GAME) / 'tools' / 'armor_src'
PLAYER = {"head": (0, 24, 0), "body": (0, 24, 0), "arm_r": (-5, 22, 0), "arm_l": (5, 22, 0),
          "leg_r": (-1.9, 12, 0), "leg_l": (1.9, 12, 0)}
PIECES = {"helm": ("head",), "chest": ("body", "arm_r", "arm_l"), "legs": ("leg_r", "leg_l"), "boots": ("leg_r", "leg_l")}
BONES = ["%s_%s" % (p, b) for p, bs in PIECES.items() for b in bs]

# each gate's cloth (robes, hoods, sashes) and leather
CLOTH = {
    "cellar": ramp("#1a1210", "#2c1e1a", "#44302a", "#5e4238", "#7a5848"),
    "gallows": ramp("#0e0e10", "#18181c", "#24242a", "#32323a", "#44444e"),
    "rotwood": ramp("#141c0e", "#202e16", "#30441e", "#425a28", "#587434"),
    "crypt": ramp("#0a0a0e", "#141418", "#202026", "#2e2e36", "#404048"),
    "plague": ramp("#2a2418", "#3e3624", "#564c34", "#706446", "#8c805c"),
    "temple": ramp("#0e0e18", "#18182a", "#24243e", "#323256", "#444472"),
    "ossuary": ramp("#1a140e", "#2a2016", "#3c2e20", "#4e3e2c", "#64503a"),
    "foundry": ramp("#140a06", "#22120a", "#341c10", "#482818", "#5e3622"),
    "frost": ramp("#5a646e", "#76808a", "#949ea6", "#b4bcc2", "#d2d8dc"),
    "silk": ramp("#2a040a", "#420a14", "#5e1220", "#7a1a2c", "#982a3c"),
    # Roster v2
    "weeping_mine": ramp("#14181c", "#20262c", "#2c343c", "#3a444e", "#4c5862"),
    "tide_chapel": ramp("#0c2224", "#143438", "#1e4a4e", "#2a6266", "#3a7c80"),
    "brigands_gorge": ramp("#2a0e08", "#44180e", "#622416", "#80321e", "#a04428"),
    "rookery": ramp("#08080c", "#121218", "#1c1c26", "#282836", "#383848"),
    "hollow_circus": ramp("#2a0610", "#4a0c1c", "#6e142a", "#94203a", "#bc3050"),
    "mirefen_coven": ramp("#141a0c", "#1e2812", "#2a381a", "#384a22", "#4a602e"),
    "sandsunk_tomb": ramp("#4a3e2a", "#6a5a3e", "#8c7a56", "#ae9c74", "#d0c096"),
    "fallen_titan": ramp("#2a0c0c", "#441414", "#621e1c", "#802a26", "#a03a32"),
    "jade_monastery": ramp("#0a2418", "#123824", "#1a4e32", "#246642", "#308054"),
    "storm_bastion": ramp("#101826", "#18243a", "#22324e", "#2e4264", "#3c547c"),
    "bloodmoon_court": ramp("#200408", "#3a0810", "#580c18", "#781222", "#981c30"),
    "obsidian_labyrinth": ramp("#100a10", "#1c121c", "#2a1a28", "#3a2436", "#4c3046"),
    "abyssal_lighthouse": ramp("#060c18", "#0c1628", "#14223c", "#1e3054", "#2a406e"),
    "eclipse_cathedral": ramp("#0c0a08", "#18140e", "#262016", "#362e20", "#4a3e2c"),
    "wyrms_hoard": ramp("#2a1004", "#441a08", "#62280c", "#843812", "#a84c1a"),
    "clockwork_spire": ramp("#2a1806", "#4a2c0c", "#6e4616", "#966222", "#bc8434"),
    "serpent_ziggurat": ramp("#04140e", "#0a2418", "#123a26", "#1c5636", "#2a7446"),
    "rimeholt": ramp("#0a1020", "#121c30", "#1a2844", "#24365a", "#304670"),
    "glass_minaret": ramp("#200408", "#3a080e", "#5a0e16", "#7e1620", "#a42230"),
    "warlords_fang": ramp("#1e140c", "#2e1e12", "#40281a", "#543622", "#6a462c"),
}
EXTRAS = {}      # set -> fn(s, parts, add, mount, theme), filled in by tools/worldarmour.py
LEATHER = ramp("#120a06", "#1e120a", "#2c1c10", "#3c2818", "#503622")


def mail_shader(R):
    def sh(p, n, b, key, i, j, w, h, fr):
        ring = (i % 2 == 0) ^ (j % 2 == 0)
        v = 0.55 + (0.12 if ring else -0.1) + 0.08 * n[1] + 0.06 * (h3(i, j, 3) - 0.5)
        if j == 0:
            v += 0.08
        return shade(R, v, i, j)
    return sh


def cloth_shader(R):
    def sh(p, n, b, key, i, j, w, h, fr):
        x, y, z = p
        v = 0.5 + 0.1 * n[1] + 0.06 * ((i + j) % 2) + 0.16 * (fbm(x * 0.5, y * 0.5, z * 0.5) - 0.5)
        if j == 0:
            v += 0.1
        if j == h - 1:
            v -= 0.16
        return shade(R, v, i, j)
    return sh


class Mount:
    """lets the weapon themes' emblem and trim draw onto a body part: their boxes moved by `off` and hung on it"""

    def __init__(self, s, part, off, flip=False):
        self.s, self.part, self.off = s, part, off
        self.boxes = s.boxes

    def add(self, lo_size, mat, tag=None, group="lit", rots=(), pivot=None, **kw):
        lo, size = lo_size
        lo = tuple(lo[k] + self.off[k] for k in range(3))
        if pivot is not None:
            pivot = tuple(pivot[k] + self.off[k] for k in range(3))
        b = PB(self.part, lo, size, mat, tag=tag or "deco", group=group, rots=rots, pivot=pivot)
        self.s.boxes.append(b)
        return b


def build(gate, cls, name):
    th = W.THEMES[gate]
    s = Sword(name)
    bone = {n: Part(n, pv) for n, pv in PLAYER.items()}
    parts = {}
    for piece, bs in PIECES.items():
        for b in bs:
            parts["%s_%s" % (piece, b)] = Part("%s_%s" % (piece, b), PLAYER[b], (), bone[b])

    def add(part, box, mat, **kw):
        lo, size = box
        b = PB(part, lo, size, mat, tag=kw.pop("tag", part.name), **kw)
        s.boxes.append(b)
        return b

    def emblem(part, x, y, z, size, depth=1.0, boss=False):
        th.emblem(Mount(s, part, (x, 0, z)), 0, y, size, depth, boss)

    if name in AS.DESIGNS:
        parts["chest_back"] = Part("chest_back", PLAYER["body"], (), bone["body"])
        for sd in ("r", "l"):
            parts["chest_shoulder_" + sd] = Part("chest_shoulder_" + sd, PLAYER["arm_" + sd], (), bone["arm_" + sd])
        AS.DESIGNS[name](AS.Kit(parts, add))
        return finish(s, parts, gate, th)

    seed = sum(map(ord, name))
    heavy = cls == "heavy"

    # ================================================================ helm
    h = parts["helm_head"]
    if cls == "robe":
        add(h, C(0, 23.8, -0.6, 9.4, 9.2, 9.0), "cloth", tag="hood")
        add(h, C(0, 33.0, -1.4, 7.8, 1.4, 7.2), "cloth", tag="hood")
        add(h, C(0, 34.2, -3.0, 4.4, 1.6, 3.6), "cloth", tag="peak")
        add(h, C(0, 30.6, 4.0, 9.6, 2.4, 1.4), "cloth", tag="brim")
        for side in (1, -1):
            add(h, C(side * 4.4, 23.6, 3.2, 1.2, 7.4, 2.0), "cloth", tag="hood_side")
        add(h, C(0, 22.0, -1.0, 10.2, 2.6, 9.4), "cloth", tag="collar")
        emblem(h, 0, 31.0, 4.85, 2.4, 0.8)
    elif cls == "light":
        add(h, C(0, 24.4, -0.4, 9.0, 8.4, 8.8), "cloth", tag="hood")
        add(h, C(0, 32.6, -1.0, 7.6, 1.2, 7.4), "cloth", tag="hood")
        add(h, C(0, 23.4, 3.9, 8.8, 3.4, 1.2), "leather", tag="mask")
        add(h, C(0, 26.6, 4.3, 8.6, 0.5, 0.6), "dark", tag="mask_edge")
        add(h, C(0, 22.6, -0.6, 9.8, 2.0, 9.2), "leather", tag="cowl")
        emblem(h, 0, 23.8, 4.7, 1.8, 0.6)
    elif cls == "medium":
        add(h, C(0, 28.4, -0.2, 9.4, 4.4, 9.2), "blade", tag="cap")
        add(h, C(0, 32.6, -0.4, 8.0, 1.2, 8.0), "blade", tag="cap")
        add(h, C(0, 28.0, -0.2, 10.4, 1.0, 10.2), "dark", tag="brim")
        for side in (1, -1):
            add(h, C(side * 4.5, 23.4, 1.0, 1.0, 5.0, 6.6), "blade", tag="cheek")
        add(h, C(0, 23.0, -4.4, 9.0, 5.4, 1.0), "mail", tag="aventail")
        add(h, C(0, 33.6, -0.4, 1.2, 1.0, 8.4), "dark", tag="ridge")
        emblem(h, 0, 29.2, 4.9, 2.0, 0.9)
    else:
        add(h, C(0, 23.2, -0.2, 10.0, 10.2, 10.0), "blade", tag="greathelm")
        add(h, C(0, 33.4, -0.2, 8.6, 1.0, 8.6), "blade", tag="crown")
        add(h, C(0, 27.6, 4.9, 8.8, 1.0, 0.6), "void", tag="slit")
        for k in range(3):
            add(h, C(0, 24.0 + k * 1.1, 5.0, 1.0 + 1.6 * k, 0.5, 0.5), "dark", tag="breaths")
        add(h, C(0, 23.2, 5.0, 1.6, 10.0, 0.8), "dark", tag="nasal")
        add(h, C(0, 22.4, -0.2, 11.0, 1.4, 11.0), "dark", tag="gorget")
        emblem(h, 0, 30.4, 5.0, 1.8, 1.4, boss=True)
    if gate == "rotwood" and cls != "light":
        for side in (1, -1):
            th.antler(Mount(s, h, (0, 0, 0)), side * 4.6, 31.0, 6.0, side)
    if gate == "frost" and cls in ("heavy", "medium"):
        add(h, C(0, 34.4, -0.4, 1.4, 2.6, 8.2), "acc", tag="plume")
    if gate == "ossuary" and heavy:
        for side in (1, -1):
            V.chain(Mount(s, h, (0, 0, 0)), (side * 5.0, 31.0), [(2.2, -side * 60, 1.4, 1.4), (1.8, -side * 20, 1.0, 1.0)], "acc", z=0.0)

    # ================================================================ chest
    c = parts["chest_body"]
    if cls == "robe":
        add(c, C(0, 12.0, 0, 9.0, 12.2, 5.0), "cloth", tag="robe")
        add(c, C(0, 12.4, 0, 9.8, 1.6, 5.6), "leather", tag="sash")
        add(c, C(1.8, 11.2, 2.7, 1.8, 3.0, 0.6), "leather", tag="sash_tail")
        for x in (-1.6, 1.6):
            add(c, C(x, 12.0, 2.6, 1.6, 11.6, 0.6), "acc" if gate in ("crypt", "silk", "frost") else "cloth", tag="stole")
        add(c, C(0, 21.0, 0, 11.0, 3.2, 6.0), "cloth", tag="mantle")
        add(c, C(0, 20.2, 0, 11.6, 1.0, 6.4), "dark", tag="mantle_edge")
        emblem(c, 0, 16.6, 2.9, 3.4, 0.8)
    elif cls == "light":
        add(c, C(0, 12.0, 0, 9.0, 12.0, 5.0), "leather", tag="jerkin")
        add(c, C(0, 12.0, 0, 9.4, 1.2, 5.4), "dark", tag="belt")
        for a in (-1, 1):   # a bandolier across
            for k in range(6):
                add(c, C(-3.4 * a + a * k * 1.3, 13.4 + k * 1.7, 2.6, 1.6, 1.4, 0.6), "leather", tag="strap")
        add(c, C(2.8, 11.0, 2.8, 2.4, 2.0, 1.0), "leather", tag="pouch")
        add(c, C(0, 22.4, 0, 9.6, 1.8, 5.6), "cloth", tag="collar")
        emblem(c, -1.6, 18.6, 2.9, 2.2, 0.6)
    elif cls == "medium":
        add(c, C(0, 11.6, 0, 9.2, 12.4, 5.2), "mail", tag="mail")
        add(c, C(0, 14.4, 0.4, 8.6, 8.4, 5.0), "blade", tag="breastplate")
        add(c, C(0, 12.0, 0, 9.8, 1.4, 5.8), "leather", tag="belt")
        add(c, C(0, 22.4, 0, 9.8, 1.6, 5.8), "dark", tag="gorget")
        emblem(c, 0, 17.0, 3.0, 4.0, 1.0)
    else:
        add(c, C(0, 11.4, 0, 9.6, 12.6, 5.8), "blade", tag="cuirass")
        add(c, C(0, 15.0, 0.4, 7.6, 7.2, 5.8), "blade", tag="plackart")
        for y in (12.2, 14.6):
            add(c, C(0, y, 0, 10.0, 0.9, 6.2), "dark", tag="lame")
        add(c, C(0, 22.6, 0, 10.4, 2.2, 6.4), "dark", tag="gorget")
        add(c, C(0, 13.4, 3.15, 1.2, 9.0, 0.6), "dark", tag="ridge")
        emblem(c, 0, 17.4, 3.4, 4.6, 1.2, boss=True)
    th.trim(Mount(s, c, (0, 0, -3.2)), "chest", 13.0, 22.0, 3.6, 1.0, heavy, seed)

    for side, b in ((-1, "arm_r"), (1, "arm_l")):
        a = parts["chest_" + b]
        x = side * 6.0
        if cls == "robe":
            add(a, C(x, 13.0, 0, 4.8, 9.6, 4.8), "cloth", tag="sleeve")
            add(a, C(x, 12.0, 0, 5.8, 2.0, 5.8), "cloth", tag="cuff")
            add(a, C(x, 12.6, 0, 6.0, 0.6, 6.0), "acc" if gate in ("crypt", "silk") else "dark", tag="cuff_edge")
            add(a, C(x + side * 0.3, 19.6, 0, 5.4, 3.0, 5.4), "cloth", tag="mantle")
        elif cls == "light":
            add(a, C(x, 13.4, 0, 4.6, 4.0, 4.6), "leather", tag="bracer")
            for yy in (14.0, 16.0):
                add(a, C(x, yy, 0, 4.9, 0.5, 4.9), "dark", tag="buckle")
            add(a, C(x + side * 0.3, 20.2, 0, 5.0, 2.8, 5.0), "leather", tag="cop")
        elif cls == "medium":
            add(a, C(x, 12.4, 0, 4.6, 9.0, 4.6), "mail", tag="sleeve")
            add(a, C(x, 13.0, 0, 5.0, 4.0, 5.0), "blade", tag="bracer")
            add(a, C(x + side * 0.4, 19.4, 0, 5.6, 4.0, 5.6), "blade", tag="pauldron")
            add(a, C(x + side * 0.6, 19.0, 0, 6.0, 0.8, 6.0), "dark", tag="pauldron_edge")
        else:
            add(a, C(x, 12.2, 0, 5.0, 5.0, 5.0), "blade", tag="vambrace")
            add(a, C(x, 12.0, 0, 5.4, 1.0, 5.4), "dark", tag="vambrace_edge")
            for k, (dy, w) in enumerate(((0.0, 6.4), (-1.6, 6.0), (-3.0, 5.6))):
                add(a, C(x + side * 0.6, 20.0 + dy, 0, w, 2.2 if k == 0 else 1.8, w), "blade" if k % 2 == 0 else "dark", tag="pauldron")
            add(a, C(x + side * 0.6, 22.2, 0, 5.2, 1.4, 5.2), "dark", tag="pauldron_top")
            # each gate's mark on the heavy shoulders
            if gate in ("foundry", "frost", "temple", "silk", "ossuary"):
                for k in range(3):
                    V.chain(Mount(s, a, (0, 0, 0)), (x + side * (1.0 + k * 1.2), 23.4), [(2.0 - 0.4 * k, -side * 15, 1.0, 1.0), (1.4 - 0.3 * k, -side * 10, 0.6, 0.6)],
                            "glow" if gate in ("temple", "frost") else "dark", z=0.0, group="fire" if gate in ("temple", "frost") else "lit")
            emblem(a, x + side * 0.6, 19.2, 3.25, 2.4, 0.8)
        if cls in ("medium", "heavy") or gate in ("rotwood", "crypt"):
            th.trim(Mount(s, a, (x, 0, 0)), "shoulder", 18.4, 22.0, 2.6, 5.6, heavy, seed + (side > 0))

    # ================================================================ legs
    for side, b in ((-1, "leg_r"), (1, "leg_l")):
        g = parts["legs_" + b]
        x = side * 1.95
        if cls == "robe":
            add(g, C(x, 2.4, 0, 4.4, 9.4, 4.4), "cloth", tag="wrap")
            for yy in (3.4, 6.0, 8.6):
                add(g, C(x, yy, 0, 4.6, 0.5, 4.6), "leather", tag="binding")
        elif cls == "light":
            add(g, C(x, 2.4, 0, 4.4, 9.6, 4.4), "cloth", tag="breeches")
            add(g, C(x, 5.0, 2.3, 3.0, 2.8, 0.8), "leather", tag="kneepad")
            add(g, C(x + side * 2.3, 8.0, 0, 0.9, 2.2, 2.2), "leather", tag="pouch")
            add(g, C(x, 10.6, 0, 4.7, 1.0, 4.7), "leather", tag="belt")
        elif cls == "medium":
            add(g, C(x, 2.4, 0, 4.4, 9.6, 4.4), "mail", tag="mail")
            add(g, C(x, 7.0, 0.3, 4.8, 4.6, 4.8), "blade", tag="tasset")
            add(g, C(x, 6.8, 0.3, 5.0, 0.6, 5.0), "dark", tag="tasset_edge")
            add(g, C(x, 4.0, 2.3, 2.6, 2.4, 0.8), "blade", tag="knee")
        else:
            add(g, C(x, 2.2, 0, 4.8, 9.8, 4.8), "blade", tag="cuisse")
            for yy in (9.6, 8.2):
                add(g, C(x, yy, 0.2, 5.2, 1.2, 5.2), "dark", tag="lame")
            add(g, C(x, 4.0, 2.4, 3.2, 3.0, 1.2), "blade", tag="knee_cop")
            add(g, C(x, 4.8, 3.0, 1.4, 1.4, 0.6), "glow", group="fire", tag="knee_gem")
            add(g, C(x, 2.0, 2.5, 1.0, 6.0, 0.4), "dark", tag="ridge")

    # ================================================================ boots
    for side, b in ((-1, "leg_r"), (1, "leg_l")):
        o = parts["boots_" + b]
        x = side * 1.95
        if cls == "robe":
            add(o, C(x, 0, 0.2, 4.6, 3.0, 5.0), "leather", tag="boot")
            add(o, C(x, 2.6, 0, 4.8, 0.8, 4.8), "cloth", tag="cuff")
            add(o, C(x, 0, 0.2, 4.8, 0.5, 5.4), "dark", tag="sole")
        elif cls == "light":
            add(o, C(x, 0, 0.2, 4.6, 4.6, 5.0), "leather", tag="boot")
            add(o, C(x, 4.4, 0, 5.0, 1.2, 5.0), "leather", tag="cuff")
            for yy in (1.6, 3.0):
                add(o, C(x, yy, 0.2, 4.8, 0.5, 5.2), "dark", tag="buckle")
            add(o, C(x, 0, 0.2, 4.8, 0.5, 5.6), "dark", tag="sole")
        else:
            add(o, C(x, 0, 0.3, 4.9, 3.6, 5.4), "blade", tag="boot")
            add(o, C(x, 3.4, 0, 5.2, 1.0, 5.2), "dark", tag="cuff")
            add(o, C(x, 0, 0.6, 5.0, 1.6, 6.0 if heavy else 5.6), "blade", tag="toe")
            add(o, C(x, 0, 0.2, 5.1, 0.5, 6.2 if heavy else 5.8), "dark", tag="sole")
            if heavy:
                for k in range(3):
                    add(o, C(x, 1.6 + k * 0.6, 2.9 + k * 0.1, 4.6 - k * 0.6, 0.5, 0.6), "dark", tag="sabaton")

    if gate in EXTRAS:      # a set's own hand-built pieces (tools/worldarmour.py: crowns, wings, blades...)
        EXTRAS[gate](s, parts, add, lambda part, off=(0, 0, 0): Mount(s, part, off), th)

    return finish(s, parts, gate, th)


def finish(s, parts, gate, th):
    sh = dict(th.shaders)
    sh["cloth"] = cloth_shader(CLOTH[gate])
    sh["leather"] = W.matte_shader(LEATHER)
    sh["mail"] = mail_shader(th.R["blade"])
    if s.name in AS.PAINT:
        sh.update(AS.shaders(s))
    s.shaders = sh
    return s, parts


def export(gate, cls, name):
    M.ASSETS = OUT
    V.T = 2
    s, parts = build(gate, cls, name)
    M.export(s, parts, name, BONES + (["chest_back", "chest_shoulder_r", "chest_shoulder_l"] if name in AS.DESIGNS else []), {}, ground_tags=("boot", "sole"))
    roomy(name)
    if name in AS.DESIGNS:
        done = OUT / 'designed.json'
        names = set(json.loads(done.read_text())) if done.exists() else set()
        done.write_text(json.dumps(sorted(names | {name})))
        fx = Path(G.GAME) / 'src/main/resources/ashbound/armor_fx.json'
        worn = json.loads(fx.read_text()) if fx.exists() else {}
        worn[name] = AS.FRAMES
        fx.write_text(json.dumps(worn, indent=0, sort_keys=True))


def roomy(name, size=256):
    """grow the atlas to a square sheet (efarmor paints the lining's cloth into its free space), the meshes' v
    coordinates squeezed to match so every face keeps its texels"""
    from PIL import Image
    tex = OUT / 'textures' / 'entity' / (name + '.png')
    im = Image.open(tex).convert('RGBA')
    H = im.size[1]
    if H >= size:        # a busy set fills even that: it gets one more step
        size *= 2
    big = Image.new('RGBA', (im.size[0], size), (0, 0, 0, 0))
    big.paste(im, (0, 0))
    big.save(tex)
    k = H / size
    for f in (OUT / 'models' / 'entity' / name).glob('*.obj'):
        out = []
        for l in f.read_text(encoding='utf-8').splitlines():
            if l.startswith('vt '):
                u, v = map(float, l.split()[1:3])
                l = 'vt %.5f %.5f' % (u, 1 - (1 - v) * k)
            out.append(l)
        f.write_text('\n'.join(out) + '\n', encoding='utf-8')


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    gear = json.load(open(G.OUT, encoding='utf-8'))
    for g in gear:
        for st in g['sets']:
            if st['old'] and st['id'] not in AS.DESIGNS:
                continue
            if args and st['id'] not in args and g['gate'] not in args:
                continue
            if g['gate'] not in W.THEMES:      # its weapon theme (weapon_themes_v2.py) isn't written yet
                continue
            export(g['gate'], st['cls'], st['id'])


if __name__ == '__main__':
    main()
