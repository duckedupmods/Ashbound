"""Hand-drawn 16x16 weapon icons. Each weapon in tools/weaponicons_*.py is a palette and one pixel grid drawn over its
slot render, built by Aseprite into tools/icons_hand/<id>.aseprite + .png. tools/renders/icon_test/weapon_<batch>.png
shows them big and at slot size. --game puts them in: the 2D icon in the slot, the 3D model in the hand, on the ground
and in frames.

    python tools/weaponicons.py a [--game] [id...]
"""
import importlib
import json
import os
import shutil
import subprocess
import sys

from PIL import Image

GAME = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(GAME, "tools"))
from armoricons import tinted  # noqa: E402
from handicons import ASEPRITE, ITEMS, LUA, OUT, TEST, rgb  # noqa: E402

ICONS = {}
MODELS = os.path.join(GAME, "src/main/resources/assets/ashbound/models/item")


def I(name, pal, grid):
    rows = [r.ljust(16, ".") for r in grid.split()]
    rows += ["." * 16] * (16 - len(rows))
    ICONS[name] = (dict(p.split("=") for p in ("k=120c12 " + pal).split()), rows)


def in_game(iid):
    """the slot shows the drawn icon; the bow's draw stages and the raised shield keep showing the same one"""
    icon = {"parent": "minecraft:item/generated", "textures": {"layer0": "ashbound:item/" + iid}}
    for nm in [iid, iid + "_blocking"] + ["%s_pulling_%d" % (iid, n) for n in range(3)]:
        p = os.path.join(MODELS, nm + ".json")
        if not os.path.exists(p):
            continue
        m = json.load(open(p, encoding="utf-8"))
        m["gui_light"] = "front"
        m.setdefault("perspectives", {})["gui"] = icon
        m["perspectives"].pop("fixed", None)
        m["perspectives"].pop("ground", None)
        json.dump(m, open(p, "w", encoding="utf-8"), indent=1)


def sheet(path, names):
    tile, slot, gap = 96, 36, 8
    cols = 6
    per = tile + slot + gap * 2
    rows = (len(names) + cols - 1) // cols
    im = Image.new("RGBA", (cols * (per + gap) + 8, rows * (tile + gap) + 8), (139, 139, 139, 255))
    for i, n in enumerate(names):
        x0, y0 = 8 + (i % cols) * (per + gap), 8 + (i // cols) * (tile + gap)
        ic = Image.open(os.path.join(OUT, n + ".png")).convert("RGBA")
        big = ic.resize((tile, tile), Image.NEAREST)
        im.paste(big, (x0, y0), big)
        sm = ic.resize((slot, slot), Image.NEAREST)
        sx, sy = x0 + tile + gap, y0 + 2
        im.paste((198, 198, 198, 255), (sx - 2, sy - 2, sx + slot + 2, sy + slot + 2))
        im.paste(sm, (sx, sy), sm)
    im.save(path)


def main():
    args = sys.argv[1:]
    game = "--game" in args
    args = [a for a in args if a != "--game"]
    batch, only = args[0], args[1:]
    sys.modules["weaponicons"] = sys.modules[__name__]
    importlib.import_module("weaponicons_" + batch)
    names = only or list(ICONS)
    spec = build(names)
    sheet(os.path.join(TEST, "weapon_%s.png" % batch), names)
    if game:
        for n in names:
            shutil.copy(os.path.join(OUT, n + ".png"), os.path.join(ITEMS, n + ".png"))
            in_game(n)
    print("drew", len(spec), "icons", "into the game" if game else "")


def build(names):
    """checks each grid and has Aseprite draw them into tools/icons_hand"""
    os.makedirs(OUT, exist_ok=True)
    spec = []
    for n in names:
        pal, grid = ICONS[n]
        if len(grid) != 16 or any(len(r) != 16 for r in grid):
            raise SystemExit("%s: bad grid, %d rows, off at %s" % (n, len(grid), [(i, len(r)) for i, r in enumerate(grid) if len(r) != 16]))
        for c in set("".join(grid)) - set(".k"):
            if c not in pal:
                raise SystemExit("%s: no colour %s" % (n, c))
        px, edge = [], tinted(grid, pal)
        for y, r in enumerate(grid):
            for x, c in enumerate(r):
                if c != ".":
                    px.append([x, y, *edge.get((x, y), rgb(pal[c]))])
        spec.append({"ase": os.path.join(OUT, n + ".aseprite"), "png": os.path.join(OUT, n + ".png"), "px": px})
    sp, lua = os.path.join(OUT, "_spec.json"), os.path.join(OUT, "_build.lua")
    json.dump(spec, open(sp, "w"))
    open(lua, "w").write(LUA)
    r = subprocess.run([ASEPRITE, "-b", "--script-param", "spec=" + sp, "--script", lua], capture_output=True, text=True)
    if r.returncode or r.stdout.strip() or r.stderr.strip():
        print("aseprite:", r.returncode, r.stdout[-500:], r.stderr[-500:])
    return spec


if __name__ == "__main__":
    main()
