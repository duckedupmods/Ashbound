"""The Ashbound logo: tools/blender/logo.py's picture with bloom, a thin cut-corner iron frame and the name.

    python tools/logo.py     -> tools/renders/logo/logo.png (1024) + logo_400.png
"""
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vfx_sheet import bloom

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "renders", "logo", "")
FONT = "C:/Windows/Fonts/palab.ttf"
S = 2048          # worked at twice the size, so edges come down clean
CUT = 150         # the corners
BAND = 62         # the frame
EMBER, GOLD, CHAR = (232, 92, 28), (255, 222, 160), (11, 8, 9)


def cut_rect(x0, y0, x1, y1, c):
    return [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c)]


def word(text, size, spread):
    """the word as a mask, its letters spaced out by hand"""
    f = ImageFont.truetype(FONT, size)
    w = sum(f.getlength(c) for c in text) + spread * (len(text) - 1)
    m = Image.new("L", (int(w) + 40, int(size * 1.4)), 0)
    d = ImageDraw.Draw(m)
    x = 20.0
    for c in text:
        d.text((x, 0), c, font=f, fill=255)
        x += f.getlength(c) + spread
    return m.crop(m.getbbox())


def main():
    pic = bloom(Image.open(DIR + "picture.png")).resize((S, S), Image.LANCZOS)
    # the bottom falls into the dark for the name
    shade = Image.new("L", (S, S), 0)
    ImageDraw.Draw(shade).rectangle((0, 1650, S, S), fill=255)
    out = Image.composite(Image.new("RGB", (S, S), CHAR), pic, shade.filter(ImageFilter.GaussianBlur(70)))

    m = word("ASHBOUND", 250, 26)
    k = (S - 2 * BAND - 190) / m.width
    if k < 1:
        m = m.resize((int(m.width * k), int(m.height * k)), Image.LANCZOS)
    wx, wy = (S - m.width) // 2, 1745
    full = Image.new("L", (S, S), 0)
    full.paste(m, (wx, wy))
    for radius, gain in ((46, 0.75), (14, 0.7)):
        glow = Image.new("RGB", (S, S), (0, 0, 0))
        glow.paste(EMBER, (0, 0), full.filter(ImageFilter.GaussianBlur(radius)).point(lambda v: int(v * gain)))
        out = ImageChops.screen(out, glow)
    grad = Image.new("RGB", (S, S))
    gd = ImageDraw.Draw(grad)
    for y in range(wy, wy + m.height):
        t = (y - wy) / m.height
        gd.line((0, y, S, y), fill=tuple(int(GOLD[c] + (EMBER[c] - GOLD[c]) * t ** 1.5) for c in range(3)))
    out.paste(grad, (0, 0), full)

    # the frame: iron a shade lit from the top, a line of ember inside it
    hole = cut_rect(BAND, BAND, S - BAND, S - BAND, CUT)
    mask = Image.new("L", (S, S), 255)
    ImageDraw.Draw(mask).polygon(hole, fill=0)
    iron = Image.new("RGB", (S, S))
    id_ = ImageDraw.Draw(iron)
    for y in range(S):
        v = 62 - 36 * y / S
        id_.line((0, y, S, y), fill=(int(v), int(v * 0.9), int(v * 0.86)))
    out.paste(iron, (0, 0), mask)
    d = ImageDraw.Draw(out)
    d.line(hole + [hole[0]], fill=(6, 4, 5), width=12)
    inner = cut_rect(BAND + 13, BAND + 13, S - BAND - 13, S - BAND - 13, CUT - 5)
    d.line(inner + [inner[0]], fill=(150, 56, 20), width=5)
    corner = cut_rect(0, 0, S, S, CUT + BAND / 2)
    edge = Image.new("L", (S, S), 255)
    ImageDraw.Draw(edge).polygon(corner, fill=0)
    out.paste(Image.new("RGB", (S, S), CHAR), (0, 0), edge)

    big = out.resize((1024, 1024), Image.LANCZOS)
    big.save(DIR + "logo.png", optimize=True)
    big.resize((400, 400), Image.LANCZOS).save(DIR + "logo_400.png", optimize=True)
    print("ok")


if __name__ == "__main__":
    main()
