"""How alike our armour really is: every set's Epic Fight meshes drawn as plain black silhouettes, front and side, then
compared. Two sets that overlap this much read as one set in a different colour. Writes tools/renders/armor_shapes.png
(a sheet of the silhouettes, grouped) and prints the groups.

    python tools/armor_shapes.py [same]        (same = how much overlap counts as the same shape, default 0.9)
"""
import json
import os
import sys

from PIL import Image, ImageDraw

GAME = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
MESH = os.path.join(GAME, "src/main/resources/assets/ashbound/animmodels/armor")
SAME = float(sys.argv[1]) if len(sys.argv) > 1 else 0.9
PX = 40            # to the block
W, H = 3 * PX, 3 * PX


def sets():
    out = []
    for g in json.load(open(os.path.join(GAME, "src/main/resources/ashbound/gear.json"), encoding="utf8")):
        for s in g["sets"]:
            out.append((s["id"], s["cls"], g["gate"], [p["id"] for p in s["pieces"]]))
    for s in json.load(open(os.path.join(GAME, "src/main/resources/ashbound/world_armour.json"), encoding="utf8")):
        out.append((s["id"], s["cls"], "world", [p["id"] for p in s["pieces"]]))
    return out


def draw(ids):
    front, side = Image.new("1", (W, H)), Image.new("1", (W, H))
    fd, sd = ImageDraw.Draw(front), ImageDraw.Draw(side)
    for i in ids:
        v = json.load(open(os.path.join(MESH, i + ".json"), encoding="utf8"))["vertices"]
        pos = v["positions"]["array"]
        for part in v["parts"].values():
            tri = part["array"]
            for t in range(0, len(tri), 9):
                ps = [pos[tri[t + k * 3] * 3:tri[t + k * 3] * 3 + 3] for k in range(3)]
                fd.polygon([(W / 2 + p[0] * PX, H - 4 - p[1] * PX) for p in ps], fill=1)
                sd.polygon([(W / 2 + p[2] * PX, H - 4 - p[1] * PX) for p in ps], fill=1)
    return front, side


def overlap(a, b):
    both = either = 0
    for x, y in zip(a, b):
        both += x & y
        either += x | y
    return both / max(1, either)


def bits(im):
    return [1 if p else 0 for p in im.getdata()]


all_sets = sets()
views = {}
for s in all_sets:
    f, v = draw(s[3])
    views[s[0]] = (f, v, bits(f) + bits(v))
groups = []
for s in all_sets:
    for g in groups:
        if overlap(views[s[0]][2], views[g[0][0]][2]) >= SAME:
            g.append(s)
            break
    else:
        groups.append([s])
groups.sort(key=len, reverse=True)
print("%d sets, %d distinct shapes at %.0f%% overlap" % (len(all_sets), len(groups), SAME * 100))
for g in groups:
    print(len(g), g[0][1], ", ".join(x[0] for x in g[:9]) + (" ..." if len(g) > 9 else ""))

cols, tile = 12, 96
rows = sum((len(g) + cols - 1) // cols for g in groups)
sheet = Image.new("RGB", (cols * tile, rows * tile + len(groups) * 6), (205, 200, 190))
y = 0
for g in groups:
    for k, s in enumerate(g):
        f = views[s[0]][0].convert("L").point(lambda p: 0 if p else 205).resize((tile, tile), Image.BILINEAR)
        sheet.paste(f, ((k % cols) * tile, y + (k // cols) * tile))
    y += ((len(g) + cols - 1) // cols) * tile + 6
os.makedirs(os.path.join(GAME, "tools/renders"), exist_ok=True)
sheet.save(os.path.join(GAME, "tools/renders/armor_shapes.png"))
