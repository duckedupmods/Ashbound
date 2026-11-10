"""python tools/beasts/sheet.py <name> [<name> ...]: the four rest views of each (beastkit rest renders) cropped into
tools/renders/beasts/<name>_model.png, and with several names a lineup of their three-quarter views."""
import sys
from pathlib import Path

from PIL import Image

VOX = Path("E:/Ashbound/tools/renders/vox")
OUT = Path(__file__).resolve().parent.parent / "renders" / "beasts"


def crop(name, view):
    return Image.open(VOX / ("%s_rest_%s.png" % (name, view))).convert("RGB").crop((130, 200, 510, 620)).resize((266, 294))


def main():
    names = sys.argv[1:]
    OUT.mkdir(parents=True, exist_ok=True)
    for n in names:
        out = Image.new("RGB", (266 * 4, 294), (40, 44, 52))
        for i, v in enumerate(("front", "threequarter", "side", "dusk")):
            out.paste(crop(n, v), (i * 266, 0))
        out.save(OUT / ("%s_model.png" % n))
        print(OUT / ("%s_model.png" % n))
    if len(names) > 1:
        cols = min(4, len(names))
        rows = (len(names) + cols - 1) // cols
        out = Image.new("RGB", (266 * cols, 294 * rows), (40, 44, 52))
        for i, n in enumerate(names):
            out.paste(crop(n, "threequarter"), ((i % cols) * 266, (i // cols) * 294))
        out.save(OUT / "legends_lineup.png")
        print(OUT / "legends_lineup.png")


if __name__ == "__main__":
    main()
