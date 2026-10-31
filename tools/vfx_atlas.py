"""The spell particles' one texture: the flipbooks (tools/blender/vfx_flip.py) and the spell circle, 2048 square.

    python tools/vfx_atlas.py        -> src/main/resources/assets/ashbound/textures/vfx/spell.png, tools/renders/vfx_flip/atlas_preview.png

Top left the blast, top right the flame, bottom left the smoke, 4 x 4 frames of 256 each; bottom right the circle, 1024.
Red holds the value (a fire's heat, smoke's light), alpha how much of it there is.
"""
import math
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = "E:/EFTest/game/"
SRC = ROOT + "tools/renders/vfx_flip/"
OUT = ROOT + "src/main/resources/assets/ashbound/textures/vfx/spell.png"
CELL = 256
SMOKE_LEVEL = 0.56


def fire_frame(path):
    """grey heat on black: the edge fades with the heat, the frame's own edge fades to nothing"""
    v = Image.open(path).convert("L")
    return Image.merge("RGBA", (v, v, v, v.point(lambda x: min(255, x * 3)))), v


def smoke_frame(path):
    """the shader multiplies this by 2.4, so the lit side sits just under that or its shading burns out; a small median takes the renderer's speckle out"""
    im = Image.open(path).convert("RGBA")
    v = im.convert("L").filter(ImageFilter.MedianFilter(3)).point(lambda x: int(x * SMOKE_LEVEL))
    return Image.merge("RGBA", (v, v, v, im.getchannel("A").filter(ImageFilter.MedianFilter(3))))


def edge_mask():
    """a soft window: nothing may touch a cell's edge or the billboard's square shows"""
    m = Image.new("L", (CELL, CELL), 0)
    ImageDraw.Draw(m).ellipse((10, 10, CELL - 11, CELL - 11), fill=255)
    return m.filter(ImageFilter.GaussianBlur(9))


def sheet(atlas, name, ox, oy, smoke):
    mask = edge_mask()
    for f in range(16):
        path = SRC + "%s_%02d.png" % (name, f)
        im = smoke_frame(path) if smoke else fire_frame(path)[0]
        im.putalpha(ImageChops.multiply(im.getchannel("A"), mask))
        atlas.paste(im, (ox + f % 4 * CELL, oy + f // 4 * CELL))


def circle(size=1024, ss=2, seed=4):
    """rings, a band of writing, a seven-point star, little rings at its points; soft-glowing like the concept's"""
    n = size * ss
    im = Image.new("L", (n, n), 0)
    d = ImageDraw.Draw(im)
    c, r = n / 2, n * 0.47
    R = random.Random(seed)

    def ring(k, w):
        rr = r * k
        d.ellipse((c - rr, c - rr, c + rr, c + rr), outline=255, width=int(w * ss))

    for k, w in ((1.0, 7), (0.86, 3), (0.58, 4), (0.22, 3)):
        ring(k, w)
    pts = [(c + math.cos(i * 3 / 7 * math.tau - math.pi / 2) * r * 0.86, c + math.sin(i * 3 / 7 * math.tau - math.pi / 2) * r * 0.86) for i in range(8)]
    d.line(pts, fill=255, width=3 * ss, joint="curve")
    for i in range(7):
        a = i / 7 * math.tau - math.pi / 2
        x, y, rr = c + math.cos(a) * r * 0.72, c + math.sin(a) * r * 0.72, r * 0.075
        d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=255, width=3 * ss)
    for i in range(60):   # the writing
        if R.random() > 0.84:
            continue
        a = i / 60 * math.tau
        r0, r1 = r * (0.89 + R.random() * 0.02), r * (0.95 + R.random() * 0.03)
        wide = R.uniform(0.006, 0.02)
        pts = [(c + math.cos(a + s * wide) * q, c + math.sin(a + s * wide) * q) for s, q in ((-1, r0), (1, r0), (1, r1), (-1, r1))]
        d.polygon(pts, fill=255)
    lines = im.resize((size, size), Image.LANCZOS)
    glow = lines.filter(ImageFilter.GaussianBlur(16)).point(lambda v: min(255, v * 3))
    tight = lines.filter(ImageFilter.GaussianBlur(3)).point(lambda v: min(255, v * 2))
    a = ImageChops.lighter(ImageChops.lighter(lines, tight), glow)
    return Image.merge("RGBA", (lines, lines, lines, a))


def main():
    atlas = Image.new("RGBA", (2048, 2048), (0, 0, 0, 0))
    sheet(atlas, "blast", 0, 0, False)
    sheet(atlas, "flame", 1024, 0, False)
    sheet(atlas, "smoke", 0, 1024, True)
    atlas.paste(circle(), (1024, 1024))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    atlas.save(OUT, optimize=True)
    open(OUT + ".mcmeta", "w").write('{"texture": {"blur": true}}\n')
    back = Image.new("RGBA", atlas.size, (10, 10, 14, 255))
    back.alpha_composite(atlas)
    back.convert("RGB").resize((1024, 1024), Image.LANCZOS).save(SRC + "atlas_preview.png")
    print("atlas", os.path.getsize(OUT) // 1024, "KB")


if __name__ == "__main__":
    main()
