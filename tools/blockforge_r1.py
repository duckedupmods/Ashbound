"""The block forge: each Roster v2 dungeon's own masonry, painted as 16x16 textures in Minecraft's style from the
dungeon's ramps, with every model, blockstate, loot table, tag and name, listed in gate_blocks.json (GateBlocks.java
registers them; no new code per dungeon).

A block is (name, painter, args): painters are bricks, ashlar, flags, tiles, rock, strata, planks, plate, crystal,
carved, column (side + end), grate, cracked (a crack and a glow through another block's texture). Families: a name
in STAIRS/SLAB/WALL gets <base>_stairs / _slab / _wall built on it.

    python tools/blockforge.py <gate...> [--sheet]      (sheet -> tools/renders/blocks/<gate>.png)
"""
import json
import math
import os
import random
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import port_weapons as P  # noqa: E402
import port_gate as PG  # noqa: E402

A = P.ASSETS
TEX = A + "textures/block/"
SHEETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "renders", "blocks")


def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def R(*hs):
    return [hexc(h) for h in hs]


def col(ramp, v):
    v = max(0.0, min(0.999, v)) * (len(ramp) - 1)
    i = int(v)
    t = v - i
    a, b = ramp[i], ramp[min(i + 1, len(ramp) - 1)]
    return tuple(int(a[k] + (b[k] - a[k]) * t) for k in range(3))


BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def dith(ramp, v, x, y):
    """ordered dither between ramp steps, the pixel-art way"""
    v = max(0.0, min(0.999, v)) * (len(ramp) - 1)
    i = int(v)
    if v - i > (BAYER[y % 4][x % 4] + 0.5) / 16 and i + 1 < len(ramp):
        i += 1
    return ramp[i]


def smooth(rnd, cell=4):
    """value noise on a wrapping 16x16"""
    n = 16 // cell
    g = [[rnd.random() for _ in range(n)] for _ in range(n)]

    def f(x, y):
        fx, fy = x / cell, y / cell
        x0, y0 = int(fx) % n, int(fy) % n
        x1, y1 = (x0 + 1) % n, (y0 + 1) % n
        tx, ty = fx - int(fx), fy - int(fy)
        tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
        a = g[y0][x0] * (1 - tx) + g[y0][x1] * tx
        b = g[y1][x0] * (1 - tx) + g[y1][x1] * tx
        return a * (1 - ty) + b * ty
    return f


def field(rnd):
    a, b = smooth(rnd, 8), smooth(rnd, 4)
    return lambda x, y: 0.6 * a(x, y) + 0.4 * b(x, y)


def img():
    return Image.new("RGB", (16, 16))


# ---------------------------------------------------------------- painters (each -> one or two images)

def p_bricks(rnd, ramp, mortar, rows=4, run=8, crack=0.0, crust=None, bevel=True):
    im, f = img(), field(rnd)
    h = 16 // rows
    shades = {}
    for y in range(16):
        r = y // h
        off = (r % 2) * (run // 2)
        for x in range(16):
            bx = (x + off) // run
            key = (r, bx % (16 // run))
            if key not in shades:
                shades[key] = rnd.uniform(-0.1, 0.1)
            if y % h == h - 1 or (x + off) % run == run - 1:
                im.putpixel((x, y), dith(mortar, 0.4 + 0.3 * f(x, y), x, y))
                continue
            v = 0.5 + shades[key] + 0.35 * (f(x, y) - 0.5)
            if bevel and y % h == 0:
                v += 0.14
            if bevel and (x + off) % run == 0:
                v += 0.08
            if bevel and y % h == h - 2:
                v -= 0.1
            im.putpixel((x, y), dith(ramp, v, x, y))
    if crack:
        cracks(im, rnd, mortar, crack)
    if crust:
        crusted(im, rnd, *crust)
    return im


def p_ashlar(rnd, ramp, mortar, crust=None):
    """big dressed blocks: two courses, long stones"""
    return p_bricks(rnd, ramp, mortar, rows=2, run=16 if rnd.random() < 0.5 else 8, crust=crust)


def p_flags(rnd, ramp, grout, crust=None):
    """big worn floor flags, irregular joints"""
    im, f = img(), field(rnd)
    cuts_x = [0, rnd.randint(6, 10), 16]
    cuts_y = [0, rnd.randint(5, 11), 16]
    shade = {(i, j): rnd.uniform(-0.12, 0.12) for i in range(2) for j in range(2)}
    for y in range(16):
        for x in range(16):
            i = 0 if x < cuts_x[1] + (1 if y > 8 else 0) else 1
            j = 0 if y < cuts_y[1] else 1
            edge = x in (0, cuts_x[1] + (1 if y > 8 else 0)) or y in (0, cuts_y[1])
            if edge:
                im.putpixel((x, y), dith(grout, 0.35 + 0.3 * f(x, y), x, y))
            else:
                im.putpixel((x, y), dith(ramp, 0.5 + shade[(i, j)] + 0.4 * (f(x, y) - 0.5), x, y))
    if crust:
        crusted(im, rnd, *crust)
    return im


def p_tiles(rnd, ramp, grout, n=4, checker=None):
    im, f = img(), field(rnd)
    s = 16 // n
    for y in range(16):
        for x in range(16):
            if x % s == s - 1 or y % s == s - 1:
                im.putpixel((x, y), dith(grout, 0.4 + 0.2 * f(x, y), x, y))
                continue
            rr = checker if checker and (x // s + y // s) % 2 else ramp
            v = 0.55 + 0.3 * (f(x, y) - 0.5) + (0.12 if x % s == 0 or y % s == 0 else 0)
            im.putpixel((x, y), dith(rr, v, x, y))
    return im


def p_rock(rnd, ramp, fleck=None, spread=0.5, crust=None):
    im, f = img(), field(rnd)
    g = smooth(rnd, 2)
    for y in range(16):
        for x in range(16):
            v = 0.5 + spread * (f(x, y) - 0.5) + 0.25 * (g(x, y) - 0.5)
            im.putpixel((x, y), dith(ramp, v, x, y))
    if fleck:
        fr, n = fleck
        for _ in range(n):
            x, y = rnd.randrange(16), rnd.randrange(16)
            im.putpixel((x, y), col(fr, rnd.random()))
            if rnd.random() < 0.4:
                im.putpixel(((x + 1) % 16, y), col(fr, rnd.random() * 0.6))
    if crust:
        crusted(im, rnd, *crust)
    return im


def p_strata(rnd, ramp, bands=4, crust=None):
    """layered rock: wavy bands of different stone"""
    im, f = img(), field(rnd)
    off = [rnd.uniform(-0.15, 0.15) for _ in range(bands + 1)]
    for y in range(16):
        for x in range(16):
            yy = y + 1.6 * math.sin(x * 0.7 + rnd.random() * 0.01)
            b = int(yy / (16 / bands)) % bands
            v = 0.5 + off[b] + 0.3 * (f(x, y) - 0.5) - (0.18 if int(yy) % (16 // bands) == 0 else 0)
            im.putpixel((x, y), dith(ramp, v, x, y))
    if crust:
        crusted(im, rnd, *crust)
    return im


def p_planks(rnd, ramp, n=4, nails=None, vertical=False):
    im, f = img(), field(rnd)
    s = 16 // n
    sh = [rnd.uniform(-0.12, 0.12) for _ in range(n)]
    for y in range(16):
        for x in range(16):
            a, b = (x, y) if vertical else (y, x)
            k = a // s
            grain = 0.12 * math.sin(b * 0.9 + k * 3 + 2.0 * f(x, y))
            v = 0.5 + sh[k] + grain + 0.2 * (f(x, y) - 0.5)
            if a % s == s - 1:
                v -= 0.32
            if a % s == 0:
                v += 0.1
            im.putpixel((x, y), dith(ramp, v, x, y))
    if nails:
        for k in range(n):
            for b in (2, 13):
                x, y = (k * s + s // 2, b) if vertical else (b, k * s + s // 2)
                im.putpixel((x, y), nails[1])
                im.putpixel((x + (0 if vertical else 1), y + (1 if vertical else 0)), nails[0])
    return im


def p_plate(rnd, ramp, rivet=None, seams=8, rust=None):
    im, f = img(), field(rnd)
    for y in range(16):
        for x in range(16):
            v = 0.5 + 0.25 * (f(x, y) - 0.5) + (0.18 if y % seams == 0 else 0) - (0.22 if y % seams == seams - 1 else 0)
            if x % 16 == 0:
                v += 0.1
            im.putpixel((x, y), dith(ramp, v, x, y))
    for y in range(1, 16, seams):
        for x in (2, 7, 13):
            im.putpixel((x, y + 1), (rivet or ramp)[-1])
            im.putpixel((x, y + 2), (rivet or ramp)[1])
    if rust:
        crusted(im, rnd, rust, 0.3)
    return im


def p_crystal(rnd, ramp, rock=None):
    """facets of a crystal mass (or crystal grown through rock)"""
    im = img()
    pts = [(rnd.uniform(0, 16), rnd.uniform(0, 16), rnd.uniform(0.2, 0.9)) for _ in range(7)]
    for y in range(16):
        for x in range(16):
            d = sorted(((min(abs(x - px), 16 - abs(x - px)) ** 2 + min(abs(y - py), 16 - abs(y - py)) ** 2, v) for px, py, v in pts))
            edge = d[1][0] - d[0][0] < 6
            v = d[0][1] + (0.3 if edge else 0)
            if rock and d[0][1] < 0.35:
                im.putpixel((x, y), dith(rock, 0.4 + v, x, y))
            else:
                im.putpixel((x, y), dith(ramp, v, x, y))
    return im


def p_carved(rnd, ramp, mortar, motif="ring"):
    """a dressed block with a motif cut in it (ring, cross, eye, sun, rune, scale)"""
    im = p_bricks(rnd, ramp, mortar, rows=1, run=16)
    dark = mortar
    cx, cy = 7.5, 7.5
    for y in range(2, 14):
        for x in range(2, 14):
            dx, dy = x - cx, y - cy
            r = math.hypot(dx, dy)
            hit = {"ring": 4.0 < r < 5.6, "cross": abs(dx) < 1 or abs(dy) < 1,
                   "eye": (abs(dy) < 2.6 - abs(dx) * 0.4 and r > 1.4) or r < 1.2,
                   "sun": r < 2.2 or (r < 5.6 and (int(math.degrees(math.atan2(dy, dx)) + 360) % 45) < 9),
                   "rune": (abs(dx) < 1 and abs(dy) < 5) or (abs(dy + dx) < 1 and dy < 0 and abs(dx) < 4) or (abs(dy - dx) < 1 and dy > 0 and abs(dx) < 4),
                   "scale": (int(y / 3) % 2 == 0 and abs(((x + (int(y / 3) % 2) * 2) % 4) - 2) + (y % 3) < 2)}[motif]
            if hit:
                im.putpixel((x, y), dith(dark, 0.3, x, y))
                if x > 2 and y > 2:
                    im.putpixel((x - 1, y - 1), dith(ramp, 0.85, x, y)) if (x - 1, y - 1) != (x, y) else None
    return im


def p_column(rnd, ramp, mortar, flutes=4):
    """a column's side (flutes) and end (a cut ring)"""
    side, end = img(), img()
    f = field(rnd)
    for y in range(16):
        for x in range(16):
            v = 0.5 + 0.25 * (f(x, y) - 0.5) + (0.18 if x % flutes == 1 else 0) - (0.22 if x % flutes == 0 else 0)
            if y in (0, 15):
                v -= 0.1
            side.putpixel((x, y), dith(ramp, v, x, y))
            r = math.hypot(x - 7.5, y - 7.5)
            end.putpixel((x, y), dith(ramp if r < 6.5 else mortar, 0.6 - 0.03 * r + 0.2 * (f(x, y) - 0.5) + (0.15 if 4.5 < r < 5.5 else 0), x, y))
    return side, end


def p_log(rnd, ramp, rings):
    side, end = img(), img()
    cols = [rnd.uniform(-0.15, 0.1) for _ in range(16)]
    for y in range(16):
        for x in range(16):
            side.putpixel((x, y), dith(ramp, 0.5 + cols[x] - (0.2 if (x + y // 5) % 5 == 0 else 0) + rnd.uniform(-0.04, 0.04), x, y))
            r = math.hypot(x - 7.5, y - 7.5)
            end.putpixel((x, y), dith(rings if r < 6.6 else ramp, 0.55 - (0.25 if int(r) % 3 == 0 else 0), x, y))
    return side, end


def p_grate(rnd, ramp, gap):
    im = img()
    for y in range(16):
        for x in range(16):
            frame = x in (0, 15) or y in (0, 15) or x % 5 == 0
            im.putpixel((x, y), dith(ramp, 0.55 + (0.15 if y in (0, 1) else 0), x, y) if frame else dith(gap, 0.3 + 0.3 * rnd.random(), x, y))
    return im


def cracks(im, rnd, ramp, amount):
    for _ in range(int(2 + amount * 5)):
        x, y = rnd.randrange(16), rnd.randrange(16)
        for _ in range(rnd.randint(3, 7)):
            im.putpixel((x % 16, y % 16), dith(ramp, 0.1, x, y))
            x += rnd.choice((-1, 0, 1))
            y += 1


def crusted(im, rnd, ramp, amount):
    """patches of something grown or settled on top (moss, crystal, salt, ash, frost)"""
    f = smooth(rnd, 4)
    for y in range(16):
        for x in range(16):
            if f(x, y) > 1 - amount - (0.2 if y < 5 else 0):
                im.putpixel((x, y), dith(ramp, f(x, y), x, y))


def p_glow(rnd, ramp, base, motif="ring"):
    """a block that gives light: a lamp-stone, a vein, a rune"""
    im = p_rock(rnd, base, spread=0.4)
    if motif == "vein":            # two seams wandering across, a dark halo either side, the light in them
        for k in range(2):
            x, y = rnd.randrange(16), 0
            dx = rnd.choice((-1, 1))
            while y < 16:
                for hx in (-1, 1):
                    im.putpixel(((x + hx) % 16, y), dith(base, 0.12, x, y))
                im.putpixel((x % 16, y), dith(ramp, 0.55 + 0.4 * rnd.random(), x, y))
                if rnd.random() < 0.5:
                    x += dx
                    im.putpixel((x % 16, y), dith(ramp, 0.7, x, y))
                if rnd.random() < 0.2:
                    dx = -dx
                y += 1
        return im
    for y in range(16):
        for x in range(16):
            r = math.hypot(x - 7.5, y - 7.5)
            if (motif == "ring" and (r < 3.2 or 5.2 < r < 6.4)) or (motif == "vein" and abs(math.sin(x * 0.6 + y * 0.35) * 5 - (y - 8)) < 1.3) \
                    or (motif == "full"):
                im.putpixel((x, y), dith(ramp, 0.55 + 0.4 * rnd.random() * (0.3 if motif == "full" else 1), x, y))
    return im


def p_stripes(rnd, a, b, width=4):
    """canvas in two colours, the stripes running up it, a weave, a dark seam at each join"""
    im, f = img(), field(rnd)
    for y in range(16):
        for x in range(16):
            ramp = a if (x // width) % 2 == 0 else b
            v = 0.55 + 0.25 * (f(x, y) - 0.5) + (0.06 if (x + y) % 2 else -0.04) - (0.25 if x % width == 0 else 0)
            im.putpixel((x, y), dith(ramp, v, x, y))
    return im


def p_gear(rnd, ramp, base, rivet=None, teeth=8):
    """a cog set into a riveted panel: rim, teeth, four spokes, a dark hub; lit from the top left"""
    im = p_plate(rnd, base, rivet=rivet, seams=16)
    for y in range(16):
        for x in range(16):
            dx, dy = x - 7.5, y - 7.5
            r = math.hypot(dx, dy)
            a = math.atan2(dy, dx)
            tooth = 5.6 < r < 7.4 and (a * teeth / (2 * math.pi)) % 1 < 0.45
            rim = 4.2 < r <= 5.6
            spoke = r < 4.2 and (abs(dx) < 0.9 or abs(dy) < 0.9)
            if r < 1.8:
                im.putpixel((x, y), base[0])
            elif tooth or rim or spoke or r < 2.6:
                light = 0.62 - 0.05 * (dx + dy) / 7 + (0.15 if (rim and dx + dy < -3) else 0) - (0.18 if (rim and dx + dy > 4) else 0)
                im.putpixel((x, y), dith(ramp, light, x, y))
            elif 4.0 < r < 7.6:
                im.putpixel((x, y), dith(base, 0.12, x, y))      # the cog's shadow in its slot
    return im


def p_lattice(rnd, ramp, lead, panes=4):
    """leaded glass that glows: diamonds of light between dark cames"""
    im = img()
    for y in range(16):
        for x in range(16):
            u, v = (x + y) % panes, (x - y) % panes
            if u == 0 or v == 0:
                im.putpixel((x, y), dith(lead, 0.4 + 0.2 * rnd.random(), x, y))
            else:
                im.putpixel((x, y), dith(ramp, 0.45 + 0.35 * rnd.random(), x, y))
    for k in range(16):
        im.putpixel((k, 0), dith(lead, 0.3, k, 0))
        im.putpixel((k, 15), dith(lead, 0.2, k, 15))
        im.putpixel((0, k), dith(lead, 0.3, 0, k))
        im.putpixel((15, k), dith(lead, 0.2, 15, k))
    return im


def p_pipe(rnd, ramp, band, bore=None):
    """a pipe or a drive shaft (a pillar block): rounded down its length, collared at the joints; its end a bore"""
    side, end = img(), img()
    for y in range(16):
        for x in range(16):
            v = 0.25 + 0.55 * (1 - abs(x - 6.5) / 8.5) + (0.12 if x == 4 else 0) + rnd.uniform(-0.04, 0.04)
            collar = y in (0, 1, 14, 15)
            side.putpixel((x, y), dith(band if collar else ramp, v + (0.1 if y in (0, 14) else 0), x, y))
            r = math.hypot(x - 7.5, y - 7.5)
            end.putpixel((x, y), dith(band, 0.55 - 0.04 * r, x, y) if r > 4.5 else dith(bore or ramp, 0.15 + 0.05 * r, x, y))
    return side, end


PAINT = {"stripes": p_stripes, "bricks": p_bricks, "ashlar": p_ashlar, "flags": p_flags, "tiles": p_tiles, "rock": p_rock, "strata": p_strata,
         "planks": p_planks, "plate": p_plate, "crystal": p_crystal, "carved": p_carved, "column": p_column, "log": p_log,
         "grate": p_grate, "glow": p_glow, "gear": p_gear, "lattice": p_lattice, "pipe": p_pipe}


# ---------------------------------------------------------------- assets

def dump(path, obj):
    P.dump(path, obj)


def write_full(name, tex, end=None):
    t = "ashbound:block/" + name
    if end:
        model = {"parent": "minecraft:block/cube_column", "textures": {"side": t, "end": t + "_top"}}
        dump(A + "models/block/%s.json" % name, model)
        dump(A + "models/block/%s_horizontal.json" % name, {"parent": "minecraft:block/cube_column_horizontal",
                                                              "textures": {"side": t, "end": t + "_top"}})
        dump(A + "blockstates/%s.json" % name, {"variants": {
            "axis=y": {"model": "ashbound:block/" + name},
            "axis=z": {"model": "ashbound:block/%s_horizontal" % name, "x": 90},
            "axis=x": {"model": "ashbound:block/%s_horizontal" % name, "x": 90, "y": 90}}})
    else:
        dump(A + "models/block/%s.json" % name, {"parent": "minecraft:block/cube_all", "textures": {"all": t}})
        dump(A + "blockstates/%s.json" % name, {"variants": {"": {"model": "ashbound:block/" + name}}})
    dump(A + "models/item/%s.json" % name, {"parent": "ashbound:block/" + name})


def write_stairs(name, base):
    t = "ashbound:block/" + base
    tx = {"bottom": t, "top": t, "side": t}
    for suf, parent in (("", "stairs"), ("_inner", "inner_stairs"), ("_outer", "outer_stairs")):
        dump(A + "models/block/%s%s.json" % (name, suf), {"parent": "minecraft:block/" + parent, "textures": tx})
    # the blockstate as a known-good one (a ported stair), the model names swapped
    tpl = open(A + "blockstates/cellar_brick_stairs.json", encoding="utf-8").read()
    dump(A + "blockstates/%s.json" % name, json.loads(tpl.replace("cellar_brick_stairs", name)))
    dump(A + "models/item/%s.json" % name, {"parent": "ashbound:block/" + name})


def write_slab(name, base):
    t = "ashbound:block/" + base
    tx = {"bottom": t, "top": t, "side": t}
    dump(A + "models/block/%s.json" % name, {"parent": "minecraft:block/slab", "textures": tx})
    dump(A + "models/block/%s_top.json" % name, {"parent": "minecraft:block/slab_top", "textures": tx})
    dump(A + "blockstates/%s.json" % name, {"variants": {"type=bottom": {"model": "ashbound:block/" + name},
                                                        "type=top": {"model": "ashbound:block/%s_top" % name},
                                                        "type=double": {"model": "ashbound:block/" + base}}})
    dump(A + "models/item/%s.json" % name, {"parent": "ashbound:block/" + name})


def write_wall(name, base):
    t = "ashbound:block/" + base
    for suf, parent in (("_post", "template_wall_post"), ("_side", "template_wall_side"), ("_side_tall", "template_wall_side_tall"),
                        ("_inventory", "wall_inventory")):
        dump(A + "models/block/%s%s.json" % (name, suf), {"parent": "minecraft:block/" + parent, "textures": {"wall": t}})
    tpl = open(A + "blockstates/cellar_brick_wall.json", encoding="utf-8").read()
    dump(A + "blockstates/%s.json" % name, json.loads(tpl.replace("cellar_brick_wall", name)))
    dump(A + "models/item/%s.json" % name, {"parent": "ashbound:block/%s_inventory" % name})


def loot_slab(name):
    dump(P.DATA + "loot_table/blocks/%s.json" % name, {"type": "minecraft:block", "pools": [{"rolls": 1, "entries": [
        {"type": "minecraft:item", "name": "ashbound:" + name, "functions": [{"function": "minecraft:set_count", "count": 2,
         "conditions": [{"condition": "minecraft:block_state_property", "block": "ashbound:" + name, "properties": {"type": "double"}}]}]}],
        "conditions": [{"condition": "minecraft:survives_explosion"}]}]})


def forge(gate, sheet=False):
    import dforge
    D = dforge.DUNGEONS[gate]
    lang = json.load(open(A + "lang/en_us.json", encoding="utf-8"))
    entries, tools, made, family_walls = [], {}, [], set()
    for b in D["blocks"]:
        name, title, painter, args = b["name"], b["title"], b["paint"], b.get("args", {})
        rnd = random.Random(name)
        out = PAINT[painter](rnd, **args)
        end = None
        if isinstance(out, tuple):
            out, end = out
            end.save(TEX + name + "_top.png")
        out.save(TEX + name + ".png")
        made.append((name, out))
        write_full(name, out, end)
        PG.loot_self(name)
        lang["block.ashbound." + name] = title
        e = {"name": name, "kind": "pillar" if end else "full", "feel": b.get("feel", "minecraft:stone_bricks")}
        if b.get("light"):
            e["light"] = b["light"]
        entries.append(e)
        tools.setdefault(b.get("tool", "pickaxe"), []).append(name)
        for fam in b.get("family", ()):
            fn = "%s_%s" % (b.get("stem", name), fam)
            if fam == "wall":
                family_walls.add(fn)
            {"stairs": write_stairs, "slab": write_slab, "wall": write_wall}[fam](fn, name)
            if fam == "slab":
                loot_slab(fn)
            else:
                PG.loot_self(fn)
            lang["block.ashbound." + fn] = "%s %s" % (b.get("stem_title", title), fam.title() if fam != "stairs" else "Stairs")
            fe = {"name": fn, "kind": fam, "feel": e["feel"]}
            if fam == "stairs":
                fe["base"] = name
            entries.append(fe)
            tools[b.get("tool", "pickaxe")].append(fn)
    P.dump(A + "lang/en_us.json", lang)
    for tool, names in tools.items():
        PG.tag(tool, names)
        walls = [n for n in names if n in family_walls]     # not a cube that's only named "..._wall"
        if walls:
            path = P.DATA.replace("/ashbound/", "/minecraft/") + "tags/block/walls.json"
            have = json.load(open(path, encoding="utf-8"))["values"] if os.path.exists(path) else []
            P.dump(path, {"replace": False, "values": have + ["ashbound:" + n for n in walls if "ashbound:" + n not in have]})
    r = PG.reg("gate_blocks.json") or {"blocks": [], "props": []}
    PG.merge(r["blocks"], entries, "name")
    PG.reg_put("gate_blocks.json", r)
    print("%s: %d blocks (%d with families)" % (gate, len(D["blocks"]), len(entries)))
    if sheet:
        os.makedirs(SHEETS, exist_ok=True)
        n = len(made)
        sh = Image.new("RGB", (n * 136, 136), (30, 32, 36))
        for i, (nm, im) in enumerate(made):
            tile = Image.new("RGB", (128, 128))
            for k in range(4):
                tile.paste(im.resize((64, 64), Image.NEAREST), ((k % 2) * 64, (k // 2) * 64))
            sh.paste(tile, (i * 136 + 4, 4))
        sh.save(os.path.join(SHEETS, gate + ".png"))
        print(os.path.join(SHEETS, gate + ".png"))


if __name__ == "__main__":
    for g in [a for a in sys.argv[1:] if not a.startswith("--")]:
        forge(g, "--sheet" in sys.argv)
