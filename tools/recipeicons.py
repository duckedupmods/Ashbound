"""The three recipe pages' icons (16x16, hand-placed): a curled parchment page, ink lines, the trade's wax seal.
python tools/recipeicons.py  ->  assets/ashbound/textures/item/recipe_{meal,brew,elixir}.png + item models"""
import json, os
from PIL import Image

ROOT = os.path.join(os.path.dirname(__file__), "..", "src", "main", "resources", "assets", "ashbound")
PAGE = [
    "................",
    "...oooooooooo...",
    "..oDdddddddddo..",
    "..oDPPPPPPPPDo..",
    "...oPkkkkkPPo...",
    "...oPPPPPPPPo...",
    "...oPkkkkkkPo...",
    "...oPPPPPPPPo...",
    "...oPkkkkPPPo...",
    "...oPPPPPPPPo...",
    "...oPkkkkkPPo...",
    "...oPPPPPPsso...",
    "..oDPPPPPsSSso..",
    "..oDddddsSHSso..",
    "...ooooooSSoo...",
    ".........oo.....",
]
BASE = {"o": (46, 30, 20), "D": (150, 112, 70), "d": (196, 158, 104), "P": (232, 210, 160), "k": (92, 66, 44)}
SEALS = {"meal": [(120, 30, 20), (190, 60, 36), (240, 140, 90)],
         "brew": [(120, 74, 18), (200, 132, 40), (250, 206, 120)],
         "elixir": [(64, 30, 100), (130, 70, 190), (200, 160, 250)]}
for kind, (s_dark, s_mid, s_hi) in SEALS.items():
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    pal = dict(BASE, s=s_dark, S=s_mid, H=s_hi)
    for y, row in enumerate(PAGE):
        for x, ch in enumerate(row):
            if ch in pal: im.putpixel((x, y), pal[ch] + (255,))
    im.save(os.path.join(ROOT, "textures", "item", f"recipe_{kind}.png"))
    with open(os.path.join(ROOT, "models", "item", f"recipe_{kind}.json"), "w") as f:
        json.dump({"parent": "minecraft:item/generated", "textures": {"layer0": f"ashbound:item/recipe_{kind}"}}, f, indent=1)
print("ok")
