"""The VFX concept renders (tools/blender/vfx_concepts.py) with a bloom pass, laid out on one sheet with their names.

    python tools/vfx_sheet.py            -> tools/renders/vfx/sheet.png (+ <name>_bloom.png)
"""
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

DIR = "E:/EFTest/game/tools/renders/vfx/"
TITLES = {"blight": "Blight Vial - rot", "brand": "Legion's Brand", "lightning": "Stormspire Lodestone", "frost": "Rime Band / Hourglass",
          "void": "Void Pearl / Rift Key", "coal": "Kiln-Father's Coal", "warhorn": "Warhorn of the Last Keep", "acorn": "Rotwood Acorn",
          "holy": "Pale Abbot's Wick", "plume": "Gryphon Plume"}


def bloom(im):
    """bright parts spread into a soft glow: a wide and a tight blur of what's over the threshold, screened back on"""
    rgb = im.convert("RGB")
    hi = rgb.point(lambda v: max(0, (v - 150)) * 255 // 105)
    out = rgb
    for radius, k in ((24, 0.8), (6, 0.6)):
        g = hi.filter(ImageFilter.GaussianBlur(radius)).point(lambda v: int(v * k))
        out = ImageChops.screen(out, g)
    return out


def main():
    names = [n for n in TITLES if os.path.exists(DIR + n + ".png")]
    tiles = []
    for n in names:
        b = bloom(Image.open(DIR + n + ".png"))
        b.save(DIR + n + "_bloom.png")
        tiles.append((n, b))
    cols = 5 if len(tiles) > 4 else len(tiles)
    rows = (len(tiles) + cols - 1) // cols
    w = 400
    sheet = Image.new("RGB", (cols * w, rows * (w + 34)), (8, 8, 10))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 20)
    except OSError:
        font = ImageFont.load_default()
    for i, (n, b) in enumerate(tiles):
        x, y = i % cols * w, i // cols * (w + 34)
        sheet.paste(b.resize((w, w), Image.LANCZOS), (x, y + 34))
        d.text((x + 10, y + 6), TITLES[n], fill=(232, 200, 160), font=font)
    sheet.save(DIR + "sheet.png")
    print("sheet", len(tiles))


if __name__ == "__main__":
    main()
