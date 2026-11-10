"""Hand-drawn 16x16 armour icons. Each set in tools/armoricons_*.py is a palette and 4 pixel grids (helm, chest, legs,
boots) drawn from that set's model, built by Aseprite into tools/icons_hand/<id>.aseprite + .png.
tools/renders/icon_test/armour_<batch>.png shows them big and at slot size. --game copies them over the item textures.

    python tools/armoricons.py a [--game] [set...]
"""
import colorsys
import importlib
import json
import os
import shutil
import subprocess
import sys

from PIL import Image

GAME = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(GAME, "tools"))
from handicons import ASEPRITE, ITEMS, LUA, OUT, TEST, rgb  # noqa: E402

SETS = {}

# legs and boots that are plain blocks on the model too, in the set's own h s m d
LEGS = """
................
.oooooo..oooooo.
ohsssmdoohssmmdo
ohsmmmdoohmmmmdo
osmmmmdoosmmmmdo
osmmmddoosmmmddo
osmmmddoosmmmddo
osmmmddoosmmmddo
osmmmddoosmmmddo
osmmmddoosmmmddo
osmmdddoosmmdddo
osmmdddoosmmdddo
ommddddoommddddo
odddkkkoodddkkko
.oooooo..oooooo.
................
"""
BOOTS = """
................
................
................
.oooooo..oooooo.
ohsmmdoohsmmddo.
osmmddoosmmdddo.
osmmddoosmmdddo.
ommdddoommddddo.
okkkkkookkkkkko.
.ooooo..oooooo..
................
................
................
................
................
................
"""


def S(name, pal, grids):
    pal = "k=120c12 " + pal
    SETS[name] = (dict(p.split("=") for p in pal.split()), grids.split())


def tinted(rows, pal):
    """the outline takes the colour of what it wraps: letter o becomes a dark, saturated shade of its brightest
    neighbour, so gold edges brown, steel edges blue. k stays a true dark, for cavities."""
    out = {}
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c != "o":
                continue
            near = [rows[v][u] for u, v in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)) if 0 <= u < 16 and 0 <= v < 16]
            near = [rgb(pal[n]) for n in near if n not in ".ok"]
            if not near:
                out[x, y] = rgb(pal["o"])
                continue
            h, s, v = colorsys.rgb_to_hsv(*[i / 255 for i in max(near, key=sum)])
            out[x, y] = [round(i * 255) for i in colorsys.hsv_to_rgb(h, min(1, s * 1.05 + 0.15), max(0.13, min(0.34, v * 0.38)))]
    return out


def pieces():
    out = {}
    for g in json.load(open(os.path.join(GAME, "src/main/resources/ashbound/gear.json"), encoding="utf8")):
        for st in g["sets"]:
            out[st["id"]] = [p["id"] for p in st["pieces"]]
    for st in json.load(open(os.path.join(GAME, "src/main/resources/ashbound/world_armour.json"), encoding="utf8")):
        out[st["id"]] = [p["id"] for p in st["pieces"]]
    return out


def sheet(path, names, ids):
    tile, slot, gap = 96, 36, 8
    cols = 2
    per = 4 * tile + 3 * gap + slot * 2 + 3 * gap
    rows = (len(names) + cols - 1) // cols
    im = Image.new("RGBA", (cols * (per + 24) + 8, rows * (tile + gap + 8) + 8), (139, 139, 139, 255))
    for i, n in enumerate(names):
        x0, y0 = 12 + (i % cols) * (per + 24), 8 + (i // cols) * (tile + gap + 8)
        for j, it in enumerate(ids[n]):
            ic = Image.open(os.path.join(OUT, it + ".png")).convert("RGBA")
            big = ic.resize((tile, tile), Image.NEAREST)
            im.paste(big, (x0 + j * (tile + gap), y0), big)
            sm = ic.resize((slot, slot), Image.NEAREST)
            sx, sy = x0 + 4 * (tile + gap) + (j % 2) * (slot + gap), y0 + (j // 2) * (slot + gap)
            im.paste((198, 198, 198, 255), (sx - 2, sy - 2, sx + slot + 2, sy + slot + 2))
            im.paste(sm, (sx, sy), sm)
    im.save(path)


def main():
    args = sys.argv[1:]
    game = "--game" in args
    args = [a for a in args if a != "--game"]
    batch, only = args[0], args[1:]
    sys.modules["armoricons"] = sys.modules[__name__]
    importlib.import_module("armoricons_" + batch)
    ids = pieces()
    names = only or list(SETS)
    os.makedirs(OUT, exist_ok=True)
    spec = []
    for n in names:
        pal, rows = SETS[n]
        if len(rows) != 64 or any(len(r) != 16 for r in rows):
            raise SystemExit("%s: bad grid, %d rows, off at %s" % (n, len(rows), [(i, len(r)) for i, r in enumerate(rows) if len(r) != 16]))
        for j, it in enumerate(ids[n]):
            px, grid = [], rows[j * 16:j * 16 + 16]
            for c in set("".join(grid)) - set(".k"):
                if c not in pal:
                    raise SystemExit("%s: no colour %s" % (it, c))
            edge = tinted(grid, pal)
            for y, r in enumerate(grid):
                for x, c in enumerate(r):
                    if c != ".":
                        px.append([x, y, *edge.get((x, y), rgb(pal[c]))])
            spec.append({"ase": os.path.join(OUT, it + ".aseprite"), "png": os.path.join(OUT, it + ".png"), "px": px})
    sp, lua = os.path.join(OUT, "_spec.json"), os.path.join(OUT, "_build.lua")
    json.dump(spec, open(sp, "w"))
    open(lua, "w").write(LUA)
    r = subprocess.run([ASEPRITE, "-b", "--script-param", "spec=" + sp, "--script", lua], capture_output=True, text=True)
    if r.returncode or r.stdout.strip() or r.stderr.strip():
        print("aseprite:", r.returncode, r.stdout[-500:], r.stderr[-500:])
    sheet(os.path.join(TEST, "armour_%s.png" % batch), names, ids)
    if game:
        for n in names:
            for it in ids[n]:
                shutil.copy(os.path.join(OUT, it + ".png"), os.path.join(ITEMS, it + ".png"))
    print("drew", len(spec), "icons", "into the game" if game else "")


if __name__ == "__main__":
    main()
