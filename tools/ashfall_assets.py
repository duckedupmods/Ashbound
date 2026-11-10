"""Ashfall night's own pictures (Ashfall.java, client/AshfallSky.java), drawn here pixel by pixel:
the red moon, the ash lying on the ground in four thicknesses, the flakes, and the Cinder's icon.
    python tools/ashfall_assets.py
The fire-mountain on the horizon is a Blender render: blender -b -P tools/blender/ashfall_night.py -- mountain"""
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageFilter

GAME = Path(__file__).resolve().parent.parent
A = GAME / "src/main/resources/assets/ashbound"
ENV = A / "textures/environment"
ENV.mkdir(parents=True, exist_ok=True)


def value_noise(n, cells, seed):
    """tileable smooth noise, n x n, `cells` lattice cells across"""
    r = random.Random(seed)
    g = [[r.random() for _ in range(cells)] for _ in range(cells)]

    def at(x, y):
        fx, fy = x / n * cells, y / n * cells
        x0, y0 = int(fx) % cells, int(fy) % cells
        x1, y1 = (x0 + 1) % cells, (y0 + 1) % cells
        tx, ty = fx - int(fx), fy - int(fy)
        tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
        a = g[y0][x0] * (1 - tx) + g[y0][x1] * tx
        b = g[y1][x0] * (1 - tx) + g[y1][x1] * tx
        return a * (1 - ty) + b * ty
    return [[at(x, y) for x in range(n)] for y in range(n)]


def fractal(n, seed):
    layers = [(value_noise(n, c, seed + c), w) for c, w in ((4, 0.55), (8, 0.28), (16, 0.17))]
    return [[sum(l[y][x] * w for l, w in layers) for x in range(n)] for y in range(n)]


def ground():
    """64 px = 4 blocks, 16 px a block like the blocks under it; each thickness covers more, the same patches growing"""
    n = 64
    f = fractal(n, 7)
    r = random.Random(3)
    speck = [[r.random() for _ in range(n)] for _ in range(n)]
    for i, cover in enumerate((0.3, 0.52, 0.74, 0.97)):
        im = Image.new("RGBA", (n, n))
        px = im.load()
        thresh = 1 - cover
        for y in range(n):
            for x in range(n):
                v = f[y][x] * 0.8 + speck[y][x] * 0.2
                if v < thresh:
                    continue
                deep = min(1.0, (v - thresh) / 0.18)
                g = int(150 + 50 * speck[y][x] - 30 * (1 - deep))
                a = int(255 * min(1.0, 0.55 + 0.45 * deep))
                px[x, y] = (g, int(g * 0.97), int(g * 0.94), a)
        im.save(ENV / ("ashfall_ground_%d.png" % i))


def moon():
    n = 64
    im = Image.new("RGBA", (n, n))
    px = im.load()
    f = fractal(n, 11)
    for y in range(n):
        for x in range(n):
            d = math.hypot(x - n / 2 + 0.5, y - n / 2 + 0.5) / (n / 2)
            if d < 0.42:
                m = 0.78 + 0.22 * f[y][x] - 0.18 * (d / 0.42) ** 3
                a = 255 if d < 0.4 else int(255 * (0.42 - d) / 0.02)
                px[x, y] = (int(255 * m), int(235 * m), int(225 * m), a)
            else:
                # a halo through the ash
                h = max(0.0, 1 - (d - 0.42) / 0.58) ** 2.2
                px[x, y] = (255, 210, 190, int(150 * h))
    im.save(ENV / "ashfall_moon.png")


def flakes():
    out = A / "textures/particle"
    r = random.Random(5)
    for k in range(4):
        im = Image.new("RGBA", (8, 8))
        px = im.load()
        # a ragged little flake: a blob grown from the middle
        cells = {(3, 3), (4, 4), (3, 4), (4, 3)}
        for _ in range(4 + k * 2):
            cx, cy = r.choice(sorted(cells))
            dx, dy = r.choice(((1, 0), (-1, 0), (0, 1), (0, -1)))
            if 1 <= cx + dx <= 6 and 1 <= cy + dy <= 6:
                cells.add((cx + dx, cy + dy))
        for (x, y) in cells:
            g = r.randint(200, 245)
            px[x, y] = (g, g, g, 255)
        im.save(out / ("ash_flake_%d.png" % k))
    (A / "particles/ash_flake.json").write_text(json.dumps({"textures": ["ashbound:ash_flake_%d" % k for k in range(4)]}, indent=2))
    (A / "particles/ash_ember.json").write_text(json.dumps({"textures": ["ashbound:firefly"]}, indent=2))


def cinder():
    """16 px icon: a lump of black cinder, cracked, the cracks still glowing"""
    rows = [
        "................",
        "................",
        "......aab.......",
        "....aabbcba.....",
        "...abbcobbca....",
        "..abcbbooccba...",
        "..bbcoybbcobba..",
        ".abbbooccyobca..",
        ".abcbbbcoobbba..",
        ".bbcoobbbccbba..",
        "..bccyoocbbca...",
        "..abbbcoobba....",
        "...aabbbbaa.....",
        ".....aaaa.......",
        "................",
        "................",
    ]
    pal = {"a": (24, 20, 20), "b": (46, 38, 36), "c": (72, 58, 52), "o": (232, 92, 24), "y": (255, 196, 72)}
    im = Image.new("RGBA", (16, 16))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in pal:
                im.putpixel((x, y), (*pal[ch], 255))
    im.save(A / "textures/item/cinder.png")
    (A / "models/item/cinder.json").write_text(json.dumps({"parent": "minecraft:item/generated", "textures": {"layer0": "ashbound:item/cinder"}}, indent=1))
    lang_p = A / "lang/en_us.json"
    lang = json.load(open(lang_p, encoding="utf-8"))
    lang["item.ashbound.cinder"] = "Cinder"
    lang["item.ashbound.cinder.desc"] = "Fallen still burning on an ashfall night. Six make a Temper Ember."
    json.dump(lang, open(lang_p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    rec = GAME / "src/main/resources/data/ashbound/recipe/temper_ember_from_cinders.json"
    rec.write_text(json.dumps({"type": "minecraft:crafting_shapeless", "category": "misc",
                               "ingredients": [{"item": "ashbound:cinder"}] * 6,
                               "result": {"id": "ashbound:temper_ember", "count": 1}}, indent=1))


if __name__ == "__main__":
    ground()
    moon()
    flakes()
    cinder()
    print("done")
