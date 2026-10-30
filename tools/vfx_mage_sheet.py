"""The mage concept renders (tools/blender/vfx_mage.py) with vfx_sheet's bloom, on one sheet with their names.

    python tools/vfx_mage_sheet.py       -> tools/renders/vfx_mage/sheet.png (+ <name>_bloom.png)
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from vfx_sheet import bloom

DIR = "E:/EFTest/game/tools/renders/vfx_mage/"
TITLES = {"flame": "Black: flame (Brand, Ember, Wyrmfire, Sunfire, Wax, Fury)", "shard": "Black: shard (Rime, Crystal, Jade, Vein, Marrow)",
          "lightning": "Black: lightning (Thunder, Steam, Toll)", "liquid": "Black: liquid (Blood, Undertow, Brine, Fever)",
          "rot": "Black: rot (Bloom, Venom, Hex, Carrion)", "void": "Black: void (Abyss, Eclipse, Strangle, Ambush)", "thread": "Black: thread (Bind, Jest)",
          "overload": "Overload: every sixth bolt", "heal": "White: heal", "radiance": "White: Radiance", "summon": "Summoner: the circle opens",
          "accord_bolts": "Joined R: three braided bolts", "accord_heal": "Joined R: the great guard", "accord_summon": "Joined R: the host"}


def main():
    tiles = []
    for n, title in TITLES.items():
        if os.path.exists(DIR + n + ".png"):
            b = bloom(Image.open(DIR + n + ".png"))
            b.save(DIR + n + "_bloom.png")
            tiles.append((title, b))
    cols, w, h = 3, 640, 360
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * w, rows * (h + 34)), (8, 8, 10))
    d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 18)
    for i, (title, b) in enumerate(tiles):
        x, y = i % cols * w, i // cols * (h + 34)
        sheet.paste(b.resize((w, h), Image.LANCZOS), (x, y + 34))
        d.text((x + 10, y + 7), title, fill=(232, 200, 160), font=font)
    sheet.save(DIR + "sheet.png")
    print("sheet", len(tiles))


if __name__ == "__main__":
    main()
