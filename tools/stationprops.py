"""The three Trades stations (pass 16) in Minecraft's own style: block models of boxes in pixels and 16x16 textures, like a
campfire or a brewing stand, our own textures (no vanilla ones). Trades.Bench tier 1: up to Epic, the make-again list.

  cooks_fire        a hearth ring of stones round crossed logs and embers, campfire flames, an oak A-frame with an iron
                    crossbar and a black pot of stew on a chain
  brewers_cask      an oak barrel on its side (stepped so it reads round) in iron hoops on two trestles, a brass tap with a
                    tankard under it, a mallet on top
  alchemists_bench  an oak table: a glowing flask over a little burner, its arm into a receiving bottle, a rack of three
                    vials, a mortar and pestle, a recipe sheet

Every model looks north (-z): its front, the side you stand at.
    python tools/stationprops.py      -> textures, models, blockstates, item models, loot, names
    blender -b -P tools/blender/station_preview.py      -> tools/renders/stations_mc.png
"""
import json
import math
import random
import sys

sys.path.insert(0, "E:/Ashbound/tools")
from siteblocks import img, smooth, grain, col, fill, put  # noqa: E402
from lampmodel import box, element  # noqa: E402
import port_weapons as P  # noqa: E402

A = P.ASSETS
TEXDIR = A + "textures/block/"
FACING_Y = {"north": 0, "east": 90, "south": 180, "west": 270}

STONE = [(52, 50, 50), (70, 67, 66), (88, 85, 82), (106, 102, 98), (124, 120, 114), (142, 138, 130)]
OAK = [(58, 38, 20), (78, 52, 28), (98, 66, 36), (118, 80, 44), (138, 96, 54), (156, 112, 64)]
BARK = [(34, 24, 16), (48, 34, 22), (62, 45, 30), (78, 58, 38), (94, 70, 46)]
IRON = [(20, 20, 22), (32, 32, 35), (46, 46, 50), (62, 62, 66), (80, 80, 86), (104, 104, 110)]
BRASS = [(96, 66, 20), (130, 92, 30), (168, 124, 44), (204, 160, 70), (236, 200, 110)]
FIRE = [(150, 40, 8), (210, 80, 14), (246, 130, 24), (255, 186, 60), (255, 230, 140)]
STEW = [(72, 34, 12), (98, 48, 18), (124, 66, 26), (150, 88, 36), (176, 112, 50)]
ALE = [(110, 64, 10), (150, 92, 18), (190, 124, 30), (222, 160, 52)]
BREW = [(70, 20, 110), (104, 36, 156), (140, 64, 200), (178, 104, 236), (214, 160, 255)]
MARBLE = [(150, 148, 142), (176, 174, 168), (200, 198, 192), (222, 220, 214)]
PAPER = [(170, 152, 112), (196, 178, 136), (218, 202, 160), (236, 224, 186)]


def tex_stone(seed=1201):
    """Dressed hearth stones: soft mottling, a dark mortar seam round the edge, soot creeping up from below."""
    im = img()
    sm, g = smooth(seed, 4), grain(seed + 1)
    fill(im, STONE, lambda x, y: 0.5 + (sm[y][x] - 0.5) * 0.4 + (g[y][x] - 0.5) * 0.18 - max(0, y - 10) * 0.05)
    for i in range(16):
        put(im, i, 0, col(STONE, 0.12))
        put(im, 0, i, col(STONE, 0.15))
    return im


def tex_oak(seed=1202):
    """Oak planks: two boards, grain lines along them, a darker gap between, a nail at each end."""
    r = random.Random(seed)
    im = img()
    g = grain(seed)
    fill(im, OAK, lambda x, y: 0.55 + (g[y][x] - 0.5) * 0.12 - (0.18 if (y * 7 + r.randrange(3)) % 5 == 0 else 0))
    for x in range(16):
        put(im, x, 7, col(OAK, 0.08))
        put(im, x, 15, col(OAK, 0.08))
    for (x, y) in ((1, 3), (14, 3), (1, 11), (14, 11)):
        put(im, x, y, col(IRON, 0.5))
    return im


def tex_cask_end(seed=1203):
    """A barrel's head: boards across, a ring of iron round the rim, a bung in the middle."""
    im = tex_oak(seed)
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            if 6.6 < d < 7.8:
                put(im, x, y, col(IRON, 0.45 if (x + y) % 3 else 0.6))
            elif d >= 7.8:
                put(im, x, y, col(OAK, 0.1))
    for y in range(7, 9):
        for x in range(7, 9):
            put(im, x, y, col(BARK, 0.3))
    return im


def tex_bark(seed=1204):
    """Log bark: deep vertical furrows."""
    im = img()
    g, sm = grain(seed), smooth(seed + 2, 2)
    fill(im, BARK, lambda x, y: 0.55 + (sm[y][x] - 0.5) * 0.3 + (g[y][x] - 0.5) * 0.2 - (0.35 if (x + (y // 4)) % 4 == 0 else 0))
    return im


def tex_iron(seed=1205):
    """Black iron: dull, a little rust, rivets in the corners."""
    im = img()
    sm, g = smooth(seed, 4), grain(seed + 1)
    fill(im, IRON, lambda x, y: 0.42 + (sm[y][x] - 0.5) * 0.3 + (g[y][x] - 0.5) * 0.12)
    for y in range(16):
        for x in range(16):
            if sm[(y + 7) % 16][(x + 3) % 16] > 0.78:
                put(im, x, y, (92, 52, 28, 255))
    for (x, y) in ((2, 2), (13, 2), (2, 13), (13, 13)):
        put(im, x, y, col(IRON, 0.95))
    return im


def tex_flat(ramp, seed, lo=0.35, spread=0.4, shine=None):
    im = img()
    sm, g = smooth(seed, 4), grain(seed + 1)
    fill(im, ramp, lambda x, y: lo + (sm[y][x] - 0.5) * spread + (g[y][x] - 0.5) * 0.15)
    if shine:
        for (x, y) in shine:
            put(im, x, y, col(ramp, 0.98))
    return im


def tex_flame(seed=1206):
    """Campfire flames on a clear ground: three tongues, white-gold at the heart, red at the tips."""
    im = img()
    for y in range(16):
        for x in range(16):
            im.putpixel((x, y), (0, 0, 0, 0))
    r = random.Random(seed)
    for cx, h in ((4, 10), (8, 14), (12, 9)):
        for y in range(16 - h, 16):
            t = (y - (16 - h)) / h
            w = 0.6 + 2.2 * t
            for x in range(16):
                dx = abs(x - cx - math.sin(y * 0.9 + cx) * 0.6)
                if dx < w:
                    put(im, x, y, col(FIRE, 0.25 + 0.7 * t * (1 - dx / w * 0.5) + r.uniform(-0.05, 0.05)))
    return im


def tex_glass(seed=1207):
    """Clear glass: a pale rim and one bright glint, the rest see-through."""
    im = img()
    for y in range(16):
        for x in range(16):
            edge = x in (0, 15) or y in (0, 15)
            im.putpixel((x, y), (214, 236, 236, 200) if edge else (200, 230, 230, 40))
    for (x, y) in ((3, 3), (4, 3), (3, 4)):
        im.putpixel((x, y), (255, 255, 255, 230))
    return im


TEXTURES = {
    "station_stone": tex_stone, "station_oak": tex_oak, "station_cask_end": tex_cask_end, "station_bark": tex_bark,
    "station_iron": tex_iron, "station_flame": tex_flame, "station_glass": tex_glass,
    "station_brass": lambda: tex_flat(BRASS, 1210, 0.55, 0.35, ((4, 4), (5, 4))),
    "station_ember": lambda: tex_flat(FIRE, 1211, 0.45, 0.6),
    "station_stew": lambda: tex_flat(STEW, 1212, 0.5, 0.5, ((5, 6), (10, 9), (7, 12))),
    "station_ale": lambda: tex_flat(ALE, 1213, 0.55, 0.3, ((3, 3),)),
    "station_brew": lambda: tex_flat(BREW, 1214, 0.55, 0.45, ((4, 4), (5, 4), (4, 5))),
    "station_red": lambda: tex_flat([(110, 10, 20), (170, 20, 34), (220, 50, 60), (250, 110, 110)], 1215, 0.55, 0.3, ((5, 4),)),
    "station_blue": lambda: tex_flat([(16, 36, 120), (30, 70, 190), (70, 120, 240), (140, 180, 255)], 1216, 0.55, 0.3, ((5, 4),)),
    "station_green": lambda: tex_flat([(20, 90, 30), (40, 150, 50), (90, 210, 90), (160, 250, 150)], 1217, 0.55, 0.3, ((5, 4),)),
    "station_marble": lambda: tex_flat(MARBLE, 1218, 0.55, 0.3),
    "station_paper": lambda: tex_flat(PAPER, 1219, 0.6, 0.2),
}
T = {k.replace("station_", ""): k for k in TEXTURES}


def b(a, c, tex, rot=None, glow=0, ends=None):
    """a box in pixels; ends: another texture for its east and west faces (a barrel's heads)"""
    x = box(a, c, tex, rot=rot, glow=glow)
    if ends:
        x["ends"] = ends
    return x


def ry(o, ang):
    return {"origin": list(o), "axis": "y", "angle": ang}


def rz(o, ang):
    return {"origin": list(o), "axis": "z", "angle": ang}


def cooks_fire():
    B = [b((1, 0, 1), (15, 1, 15), "stone")]
    for i, (x, z) in enumerate(((1, 1), (6.5, 0.5), (12, 1), (12.5, 6.5), (12, 12), (6.5, 12.5), (1, 12), (0.5, 6.5))):
        B.append(b((x, 1, z), (x + 3, 2.5 + (i % 3) * 0.5, z + 3), "stone"))
    for ang in (45, -45):                                                       # two logs crossed in the ring
        B.append(b((3, 1, 7), (13, 3, 9), "bark", rot=ry((8, 2, 8), ang)))
    B.append(b((5, 1, 5), (11, 1.6, 11), "ember", glow=12))
    for ang in (45, -45):                                                       # the flames, crossed like a campfire's
        B.append(b((8, 1, 2), (8, 8, 14), "flame", rot=ry((8, 4, 8), ang), glow=15))
    for x in (1.5, 13.5):                                                       # the A-frame and its iron bar
        B.append(b((x, 1, 7), (x + 1, 15, 9), "bark"))
    B.append(b((1, 14, 7.5), (15, 15, 8.5), "iron"))
    B.append(b((7.6, 10.5, 7.6), (8.4, 14, 8.4), "iron"))                         # the chain
    B.append(b((4.5, 6, 4.5), (11.5, 9.5, 11.5), "iron"))                        # the pot, its rim, the stew
    B.append(b((5.5, 5, 5.5), (10.5, 6, 10.5), "iron"))
    for (a, c) in (((4, 9.5, 4), (12, 10.5, 5)), ((4, 9.5, 11), (12, 10.5, 12)), ((4, 9.5, 5), (5, 10.5, 11)), ((11, 9.5, 5), (12, 10.5, 11))):
        B.append(b(a, c, "iron"))
    B.append(b((5, 9.5, 5), (11, 10, 11), "stew"))
    B.append(b((6, 10.5, 7.7), (10, 11, 8.3), "iron"))                           # the pot's bail
    return B


def brewers_cask():
    B = []
    for x in (2, 12):                                                           # two trestles
        B += [b((x, 0, 2), (x + 2, 1, 14), "oak"), b((x, 1, 2.5), (x + 2, 4, 4.5), "oak"), b((x, 1, 11.5), (x + 2, 4, 13.5), "oak")]
    # the barrel on its side along x: three boxes stepped so it reads round, heads on the ends
    for (a, c) in (((1, 3.5, 4), (15, 14.5, 12)), ((1, 4.5, 3), (15, 13.5, 13)), ((1, 6, 2.5), (15, 12, 13.5))):
        B.append(b(a, c, "oak", ends="cask_end"))
    for x in (3, 12):                                                           # iron hoops round it
        B += [b((x, 3.3, 3.8), (x + 1, 14.7, 12.2), "iron"), b((x, 4.3, 2.8), (x + 1, 13.7, 13.2), "iron"), b((x, 5.8, 2.3), (x + 1, 12.2, 13.7), "iron")]
    B += [b((7, 7, 1), (9, 8.5, 2.6), "brass"), b((7.5, 5.5, 1), (8.5, 7, 2), "brass"), b((7.2, 8.5, 1.4), (8.8, 9.3, 2), "brass")]   # the tap
    B += [b((6.2, 0, 0.2), (9.8, 4, 3.4), "oak"), b((6.1, 1.2, 0.1), (9.9, 1.8, 3.5), "iron"), b((6.7, 3.6, 0.7), (9.3, 4.05, 2.9), "ale"), b((9.8, 1, 1.3), (10.8, 3, 2.3), "oak")]  # the tankard
    B += [b((4, 14.5, 7.5), (11, 15.5, 8.5), "oak"), b((10, 14.5, 6), (13, 16.5, 10), "bark")]   # a mallet on top
    return B


def alchemists_bench():
    B = [b((0, 12, 1), (16, 14, 15), "oak"), b((1, 3, 2), (15, 4, 14), "oak")]
    for (x, z) in ((1, 2), (13, 2), (1, 12), (13, 12)):
        B.append(b((x, 0, z), (x + 2, 12, z + 2), "oak"))
    B += [b((3, 14, 6), (6, 15, 9), "brass"), b((4.2, 15, 7.2), (4.8, 16.5, 7.8), "flame", glow=15)]   # the burner
    B += [b((2.5, 16.5, 5), (6.5, 20.5, 9), "brew", glow=10), b((3, 16, 5.5), (6, 17, 8.5), "brass"),   # the flask on its ring
          b((4, 20.5, 6.5), (5, 23, 7.5), "glass"), b((4, 22, 6.5), (11, 23, 7.5), "glass", rot=rz((4.5, 22.5, 7), -22.5))]
    B += [b((10, 14, 5.5), (13, 17, 8.5), "glass"), b((10.3, 14, 5.8), (12.7, 15.8, 8.2), "brew", glow=8),   # the receiving bottle
          b((11, 17, 6.5), (12, 18.5, 7.5), "glass")]
    B.append(b((9, 14, 11), (15, 15, 13), "oak"))                               # the vial rack
    for x, t in ((9.8, "red"), (11.8, "blue"), (13.8, "green")):
        B += [b((x - 0.7, 15, 11.3), (x + 0.7, 18, 12.7), t, glow=6), b((x - 0.5, 18, 11.5), (x + 0.5, 18.8, 12.5), "oak")]
    B += [b((2, 14, 11), (5.5, 16, 14), "marble"), b((3, 15.5, 12), (4, 19, 13), "marble", rot=rz((3.5, 16, 12.5), 22.5))]   # mortar, pestle
    B.append(b((6.5, 14, 2), (10.5, 14.2, 5.5), "paper", rot=ry((8.5, 14, 3.7), 22.5)))   # the recipe sheet
    return B


def el(bx):
    e = element(bx)
    for f, fd in e["faces"].items():
        fd["texture"] = "#" + bx["tex"]
    if bx.get("ends"):
        for f in ("east", "west"):
            e["faces"][f]["texture"] = "#" + bx["ends"]
            e["faces"][f]["uv"] = [0, 0, 16, 16]
    if bx["tex"] == "flame":
        for f in ("east", "west"):
            e["faces"][f]["uv"] = [0, 0, 16, 16]
        for f in ("north", "south", "up", "down"):
            e["faces"].pop(f, None)
    return e


def model(name, boxes, particle):
    used = sorted(set(x["tex"] for x in boxes) | set(x["ends"] for x in boxes if x.get("ends")))
    tex = {t: "ashbound:block/" + T[t] for t in used}
    tex["particle"] = "ashbound:block/" + T[particle]
    for x in boxes:
        for v in x["from"] + x["to"]:
            assert -16 <= v <= 32, (name, x)
        if x["rot"]:
            assert x["rot"]["angle"] in (-45, -22.5, 0, 22.5, 45), (name, x["rot"])
    m = {"ambientocclusion": False, "render_type": "minecraft:cutout", "textures": tex, "elements": [el(x) for x in boxes]}
    P.dump(A + "models/block/%s.json" % name, m)


NAMES = {"cooks_fire": "Cook's Fire", "brewers_cask": "Brewer's Cask", "alchemists_bench": "Alchemist's Bench"}
BUILD = {"cooks_fire": (cooks_fire, "stone"), "brewers_cask": (brewers_cask, "oak"), "alchemists_bench": (alchemists_bench, "oak")}


def main():
    for n, fn in TEXTURES.items():
        fn().save(TEXDIR + n + ".png")
    for n, (fn, part) in BUILD.items():
        model(n, fn(), part)
        P.dump(A + "blockstates/%s.json" % n, {"variants": {"facing=%s" % f: dict({"model": "ashbound:block/" + n}, **({"y": y} if y else {}))
                                                             for f, y in FACING_Y.items()}})
        P.dump(A + "models/item/%s.json" % n, {"parent": "ashbound:block/" + n})
        P.dump(P.DATA + "loot_table/blocks/%s.json" % n, {"type": "minecraft:block", "pools": [{"rolls": 1, "entries": [
            {"type": "minecraft:item", "name": "ashbound:" + n}], "conditions": [{"condition": "minecraft:survives_explosion"}]}]})
    for n in NAMES:                                  # the manor's own (tier 2): the same models, fixed in the house, no item
        P.dump(A + "blockstates/home_%s.json" % n, {"variants": {"facing=%s" % f: dict({"model": "ashbound:block/" + n}, **({"y": y} if y else {}))
                                                                  for f, y in FACING_Y.items()}})
    lang = json.load(open(A + "lang/en_us.json", encoding="utf-8"))
    lang.update({"block.ashbound." + n: t for n, t in NAMES.items()})
    lang.update({"block.ashbound.home_" + n: "Manor " + t for n, t in NAMES.items()})
    P.dump(A + "lang/en_us.json", lang)
    import os
    path = P.GAME + "src/main/resources/data/minecraft/tags/block/mineable/axe.json"  # the cask and the bench; the fire is stone (pickaxe)
    have = json.load(open(path, encoding="utf-8"))["values"] if os.path.exists(path) else []
    P.dump(path, {"replace": False, "values": have + ["ashbound:" + n for n in NAMES if "ashbound:" + n not in have]})
    print("stations: %d blocks (+%d manor), %d textures" % (len(NAMES), len(NAMES), len(TEXTURES)))


if __name__ == "__main__":
    main()
