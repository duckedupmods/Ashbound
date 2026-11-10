"""Hand-drawn 16x16 icons for everything that isn't a weapon or armour: relics, drops, forge things, the Bag and the Ration
Pouch, the creative tabs. Each batch in tools/itemicons_*.py is I(name, palette, grid) like the weapon batches, drawn over
the item's own render (tools/renders/icon_ref_curio for the OBJ ones, the old 10/29 icon for the rest), built by Aseprite
into tools/icons_hand. tools/renders/icon_test/item_<batch>.png shows them big and at slot size with the old one beside.
--game puts them in:
  - a flat item: its texture is replaced;
  - an OBJ item: the slot shows the icon, the hand keeps the model (and a model that was painted with item/<id>.png gets
    that texture moved to item/<id>_3d.png first, so the icon doesn't land on it);
  - a builtin one (the Bag, the Ration Pouch): wrapped so the slot shows the icon and the rest is still the 3D pouch.

    python tools/itemicons.py a [--game] [id...]
"""
import importlib
import json
import os
import shutil
import sys

from PIL import Image

GAME = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(GAME, "tools"))
import weaponicons as W  # noqa: E402
from handicons import OUT, TEST, ITEMS  # noqa: E402

A = os.path.join(GAME, "src/main/resources/assets/ashbound")
MODELS, MESH = os.path.join(A, "models/item"), os.path.join(A, "models/mesh")
REF = os.path.join(GAME, "tools/renders/icon_ref_curio")
I = W.I

# a band seen from a little above, lit from the top left: s light, S mid, d shade; four rows above it for what it carries
RING = """
...ooossSSooo...
..osSo....oSdo..
.osSo......oddo.
.oso........odo.
osSo........oddo
osSo........oddo
.oso........odo.
.osSo......oddo.
..oSSoo..ooddo..
...ooSSSdddoo...
.....oooooo.....
"""
# a cord loop in q, whatever hangs off it under
CORD = """
.....oooooo.....
....oq....qo....
....oq....qo....
.....oq..qo.....
......oqqo......
"""


def ring(name, pal, top):
    I(name, pal, top + RING)


def pendant(name, pal, charm):
    I(name, pal, CORD + charm)


def own_texture(iid):
    """an OBJ painted with the very texture the icon goes to: move its paint aside"""
    for f in os.listdir(MESH):
        if not f.endswith(".mtl"):
            continue
        p = os.path.join(MESH, f)
        s = open(p, encoding="utf-8").read()
        if "map_Kd ashbound:item/%s\n" % iid in s + "\n":
            src, dst = os.path.join(ITEMS, iid + ".png"), os.path.join(ITEMS, iid + "_3d.png")
            if not os.path.exists(dst):
                shutil.copy(src, dst)
            open(p, "w", encoding="utf-8").write(s.replace("map_Kd ashbound:item/%s" % iid, "map_Kd ashbound:item/%s_3d" % iid))


def in_game(iid):
    p = os.path.join(MODELS, iid + ".json")
    icon = {"parent": "minecraft:item/generated", "textures": {"layer0": "ashbound:item/" + iid}}
    if not os.path.exists(p):
        json.dump(icon, open(p, "w", encoding="utf-8"), indent=1)
        return
    m = json.load(open(p, encoding="utf-8"))
    if m.get("loader") == "neoforge:separate_transforms":
        W.in_game(iid)
    elif m.get("parent") == "builtin/entity":
        json.dump({"loader": "neoforge:separate_transforms", "gui_light": "front", "base": m, "perspectives": {"gui": icon}},
                  open(p, "w", encoding="utf-8"), indent=1)
    elif m.get("textures", {}).get("layer0") != "ashbound:item/" + iid:
        json.dump(icon, open(p, "w", encoding="utf-8"), indent=1)


def sheet(path, names):
    tile, slot, gap, cols = 96, 36, 8, 5
    per = tile * 2 + slot + gap * 3
    rows = (len(names) + cols - 1) // cols
    im = Image.new("RGBA", (cols * (per + gap) + 8, rows * (tile + gap) + 8), (139, 139, 139, 255))
    for i, n in enumerate(names):
        x0, y0 = 8 + (i % cols) * (per + gap), 8 + (i // cols) * (tile + gap)
        ic = Image.open(os.path.join(OUT, n + ".png")).convert("RGBA")
        big = ic.resize((tile, tile), Image.NEAREST)
        im.paste(big, (x0, y0), big)
        ref = os.path.join(REF, n + ".png")
        ref = ref if os.path.exists(ref) else os.path.join(ITEMS, n + ".png")
        if os.path.exists(ref):
            r = Image.open(ref).convert("RGBA")
            r = r.crop(r.getbbox() or (0, 0, r.width, r.height))
            if r.width > 1 and r.height > 1:
                k = tile / max(r.size)
                r = r.resize((max(1, int(r.width * k)), max(1, int(r.height * k))), Image.NEAREST if r.width <= 32 else Image.LANCZOS)
                im.paste(r, (x0 + tile + gap, y0), r)
        sm = ic.resize((slot, slot), Image.NEAREST)
        sx, sy = x0 + tile * 2 + gap * 2, y0 + 2
        im.paste((198, 198, 198, 255), (sx - 2, sy - 2, sx + slot + 2, sy + slot + 2))
        im.paste(sm, (sx, sy), sm)
    im.save(path)


def main():
    args = sys.argv[1:]
    game = "--game" in args
    args = [a for a in args if a != "--game"]
    batch, only = args[0], args[1:]
    sys.modules["itemicons"] = sys.modules[__name__]
    importlib.import_module("itemicons_" + batch)
    names = only or list(W.ICONS)
    W.build(names)
    sheet(os.path.join(TEST, "item_%s.png" % batch), names)
    if game:
        for n in names:
            if os.path.exists(os.path.join(ITEMS, n + ".png")):
                own_texture(n)
            shutil.copy(os.path.join(OUT, n + ".png"), os.path.join(ITEMS, n + ".png"))
            in_game(n)
    print("drew", len(names), "icons", "into the game" if game else "")


if __name__ == "__main__":
    main()
