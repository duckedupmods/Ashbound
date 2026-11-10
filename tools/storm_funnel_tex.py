"""The gate storm's funnel wall (client/StormSky): cloud streaks wound round the funnel, tiling both ways (u round it, v up
it), grey with alpha for how thick the cloud is; tinted and lit red toward the tear in game. Plain python value noise.
  python tools/storm_funnel_tex.py  ->  src/main/resources/assets/ashbound/textures/entity/storm_funnel.png"""
import math
import os
import random

from PIL import Image, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "main", "resources", "assets", "ashbound", "textures", "entity",
                   "storm_funnel.png")
W = H = 256
r = random.Random(17)


def grid(gx, gy):
    return [[r.random() for _ in range(gx)] for _ in range(gy)]


def sample(g, x, y):
    """Smooth value noise on a wrapping grid; x, y in grid cells."""
    gy, gx = len(g), len(g[0])
    x0, y0 = int(math.floor(x)), int(math.floor(y))
    fx, fy = x - x0, y - y0
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a = g[y0 % gy][x0 % gx]
    b = g[y0 % gy][(x0 + 1) % gx]
    c = g[(y0 + 1) % gy][x0 % gx]
    d = g[(y0 + 1) % gy][(x0 + 1) % gx]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


# streaks run round the funnel (along u): few cells across u, many up v; octaves double both
octs = [(grid(4 * 2 ** o, 12 * 2 ** o), 0.55 ** o) for o in range(5)]
warp = grid(6, 6)
img = Image.new("RGBA", (W, H))
px = img.load()
for y in range(H):
    for x in range(W):
        u, v = x / W, y / H
        # a little wobble so the streaks aren't ruler-straight
        wv = v + (sample(warp, u * 6, v * 6) - 0.5) * 0.08
        n = sum(w * sample(g, u * len(g[0]), wv * len(g)) for g, w in octs) / sum(w for _, w in octs)
        a = min(1.0, max(0.0, (n - 0.36) / 0.3))
        a = a * a * (3 - 2 * a)
        shade = 0.55 + 0.45 * min(1.0, max(0.0, (n - 0.3) / 0.5))
        c = int(255 * shade)
        px[x, y] = (c, c, min(255, c + 6), int(255 * a))
img.save(OUT)
print("wrote", OUT)
