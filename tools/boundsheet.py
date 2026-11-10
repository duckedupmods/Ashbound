"""The Bound side by side: three-quarter and side of each, for a yes or no (tools/voxbound.py, blender/preview_mob.py)."""
import os

from PIL import Image, ImageDraw, ImageFont

VOX = "E:/Ashbound/tools/renders/vox/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "bound_v3.png")
NAMES = (("riftblade", "Blades: Riftblade"), ("cantor", "Mages: Hollow Cantor"), ("gatebreaker", "Brute: Gatebreaker"), ("riftling", "Swarm: Riftling"), ("oathwarden", "Warband: Oathwarden"))
VIEWS = ("threequarter", "front", "side")


def main():
    w, h = 384, 384
    s = Image.new("RGB", (len(VIEWS) * w, len(NAMES) * (h + 28)), (10, 10, 12))
    d = ImageDraw.Draw(s)
    font = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 18)
    for y, (n, title) in enumerate(NAMES):
        d.text((8, y * (h + 28) + 4), title, fill=(232, 200, 160), font=font)
        for x, v in enumerate(VIEWS):
            p = VOX + "mount_%s_%s.png" % (n, v)
            if os.path.exists(p):
                s.paste(Image.open(p).convert("RGB").resize((w, h), Image.LANCZOS), (x * w, y * (h + 28) + 28))
    s.save(OUT)
    print("sheet", s.size)


if __name__ == "__main__":
    main()
