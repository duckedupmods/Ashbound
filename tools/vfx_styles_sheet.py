"""The staff styles side by side (blender/vfx_styles.py), in colour, and with the colour taken out to check each still reads by its shape."""
import os
import sys

from PIL import Image, ImageDraw, ImageFont, ImageOps

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from vfx_mage_sheet import bloom

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "renders", "vfx_styles") + os.sep
ROWS = (("Black", ("bolt", "orb", "rune", "lance", "fan", "fall")), ("White", ("circle", "rain", "mend", "spring", "flask")),
        ("Summon", ("blades", "mages", "brute", "swarm", "band")))


def sheet(grey, out):
    cols, w, h = 4, 480, 270
    tiles = [(group + ": " + n.capitalize(), n) for group, names in ROWS for n in names if os.path.exists(DIR + n + ".png")]
    rows = (len(tiles) + cols - 1) // cols
    s = Image.new("RGB", (cols * w, rows * (h + 28)), (8, 8, 10))
    d = ImageDraw.Draw(s)
    font = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 16)
    for i, (title, n) in enumerate(tiles):
        im = bloom(Image.open(DIR + n + ".png").convert("RGB"))
        if grey:
            im = ImageOps.grayscale(im).convert("RGB")
        x, y = i % cols * w, i // cols * (h + 28)
        s.paste(im.resize((w, h), Image.LANCZOS), (x, y + 28))
        d.text((x + 8, y + 5), title, fill=(232, 200, 160), font=font)
    s.save(DIR + out)


if __name__ == "__main__":
    sheet(False, "sheet.png")
    sheet(True, "sheet_grey.png")
    print("sheets done")
