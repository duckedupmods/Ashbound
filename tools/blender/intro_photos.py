"""Hob's photographs for the intro: old black-and-white prints of a gate and a dungeon, the tear the only thing in colour
(the colour's your only warning). Made from tools/blender/gate_window.py's passes in tools/renders/gate/gw, no new renders.
  blender -b -P tools/blender/intro_photos.py   ->  tools/renders/photos/*.png (the prints) + sheet.png
"""
import os

import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
GW = os.path.abspath(os.path.join(HERE, "..", "renders", "gate", "gw"))
OUT = os.path.abspath(os.path.join(HERE, "..", "renders", "photos"))
os.makedirs(OUT, exist_ok=True)

# the print: picture area, white border, a deeper strip at the bottom
PW, PH, SIDE, TOP, BOTTOM = 640, 360, 22, 22, 72
PAPER = np.array([0.93, 0.91, 0.86], dtype=np.float32)
# (name, kind, shot, tear colour, how strong its glow came out, rim only)
PRINTS = [
    ("photo_f", "gate", "hero", (0.80, 0.84, 0.92), 0.38, False),
    ("photo_e", "gate", "side", (0.27, 0.90, 0.47), 1, False),
    ("photo_d", "gate", "near", (0.24, 0.55, 1.0), 0.5, False),
]
# where the game reads them (client/Photos draws the caption on the bottom strip)
GAME = "E:/EFTest/game/src/main/resources/assets/ashbound/textures/gui/photos"


def load(name):
    im = bpy.data.images.load(os.path.join(GW, name))
    a = np.array(im.pixels[:], dtype=np.float32).reshape(im.size[1], im.size[0], 4)
    return a[::-1]   # Blender keeps the bottom row first: work top first


def to_lin(a):
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def to_srgb(a):
    a = np.clip(a, 0, 1)
    return np.where(a <= 0.0031308, a * 12.92, 1.055 * a ** (1 / 2.4) - 0.055)


def blur(a, r):
    for _ in range(3):
        p = np.pad(a, ((r + 1, r), (0, 0), (0, 0)), mode="edge")
        c = np.cumsum(p, 0)
        a = (c[2 * r + 1:] - c[:-2 * r - 1]) / (2 * r + 1)
        p = np.pad(a, ((0, 0), (r + 1, r), (0, 0)), mode="edge")
        c = np.cumsum(p, 1)
        a = (c[:, 2 * r + 1:] - c[:, :-2 * r - 1]) / (2 * r + 1)
    return a


def grey(rgb):
    return (rgb[..., 0:1] * 0.3 + rgb[..., 1:2] * 0.59 + rgb[..., 2:3] * 0.11)


def resize(a, w, h):
    """Box-filtered down to w x h (the passes are 1600 x 900, the same 16:9)."""
    H, W = a.shape[:2]
    ys = (np.arange(h + 1) * H / h).astype(int)
    xs = (np.arange(w + 1) * W / w).astype(int)
    c = np.cumsum(np.cumsum(np.pad(a, ((1, 0), (1, 0), (0, 0))), 0), 1)
    s = c[ys[1:]][:, xs[1:]] - c[ys[:-1]][:, xs[1:]] - c[ys[1:]][:, xs[:-1]] + c[ys[:-1]][:, xs[:-1]]
    area = ((ys[1:] - ys[:-1])[:, None] * (xs[1:] - xs[:-1])[None, :])[..., None]
    return s / area


def gate(shot, tint, rim):
    base, thru = to_lin(load("gw_out_%s.png" % shot)[..., :3]), to_lin(load("gw_in_%s.png" % shot)[..., :3])
    rf = load("rift_F_%s.exr" % shot)
    mk = load("mask_%s.exr" % shot)[..., 3:4]
    deep = np.clip((blur(mk, 14) - 0.5) * 2.2, 0, 1) * mk
    seen = thru * (0.25 + 0.75 * deep)
    if rim:
        seen = seen * 0.06   # the black ones: nothing to see in there
    glow = np.clip(grey(rf[..., :3]), 0, None) * (1 - 0.92 * deep)
    alpha = rf[..., 3:4] * (1 - 0.92 * deep)
    if rim:
        # the black ones: dark right through, and only the very lip burns, no halo
        base = base * (1 - 0.85 * np.clip(blur(mk, 4) * 1.4, 0, 1))
        glow = (1 - np.exp(-glow)) ** 7 * 2.2
        alpha = alpha * 0
    world = grey(base * (1 - mk) + seen * mk)
    t = np.array(tint, dtype=np.float32)
    return world, glow, alpha, t


def develop(name, kind, shot, tint, strength, rim, seed):
    rng = np.random.default_rng(seed)
    if kind == "hall":
        mono = grey(to_lin(load(shot)[..., :3]))
        glow = alpha = None
    else:
        mono, glow, alpha, t = gate(shot, tint, rim)
        glow, alpha = glow * strength, alpha * strength
    mono = resize(mono, PW, PH)
    # the film: a little soft, contrast pushed, a warm-grey tone, grain, a dark falloff to the corners
    v = to_srgb(mono * 1.25)[..., 0]
    v = np.clip((v - 0.5) * 1.28 + 0.5, 0, 1)
    v = blur(v[..., None], 1)[..., 0]
    yy, xx = np.mgrid[0:PH, 0:PW]
    r = np.sqrt(((xx - PW / 2) / (PW / 2)) ** 2 + ((yy - PH / 2) / (PH / 2)) ** 2)
    v = v * (1 - 0.42 * np.clip(r - 0.45, 0, 1) ** 1.5)
    v = v + rng.normal(0, 0.045, v.shape) + blur(rng.normal(0, 0.08, (PH, PW, 1)), 2)[..., 0]
    # dust and a hair or two caught on the print
    for _ in range(int(rng.integers(20, 40))):
        y, x = rng.integers(0, PH), rng.integers(0, PW)
        v[max(0, y - 1):y + 1, max(0, x - 1):x + 1] = rng.choice([0.05, 0.95])
    for _ in range(2):
        y0, x0, ang, ln = rng.integers(0, PH), rng.integers(0, PW), rng.uniform(0, np.pi), rng.integers(30, 90)
        for k in range(ln):
            y, x = int(y0 + np.sin(ang + k * 0.03) * k), int(x0 + np.cos(ang + k * 0.03) * k)
            if 0 <= y < PH and 0 <= x < PW:
                v[y, x] = v[y, x] * 0.4 + 0.95 * 0.6
    v = np.clip(v, 0, 1)
    tone = np.stack([v * 1.02 + 0.01, v * 0.99 + 0.005, v * 0.92], axis=2)   # silver print, a touch warm
    if glow is not None:
        g = resize(glow, PW, PH)
        a = np.clip(resize(alpha, PW, PH), 0, 1)
        bloom = blur(g, 6) * 0.6 + blur(g, 18) * 0.35
        col = 1 - np.exp(-(g + bloom) * 1.6)   # the colour the old film caught, soft and bleeding
        lit = t[None, None, :] * col + (1 - np.exp(-g * 0.5)) * 0.25
        tone = tone * (1 - np.clip(a + col * 0.6, 0, 1) * 0.7) + lit
    tone = np.clip(tone, 0, 1)
    # the paper: a cream border, a deeper strip at the bottom, faintly yellowed and worn at its edges
    W, H = PW + 2 * SIDE, PH + TOP + BOTTOM
    paper = np.ones((H, W, 3), dtype=np.float32) * PAPER
    py, px = np.mgrid[0:H, 0:W]
    edge = np.minimum(np.minimum(px, W - 1 - px), np.minimum(py, H - 1 - py))
    paper = paper * (1 - 0.1 * np.exp(-edge / 6.0))[..., None] - blur(rng.normal(0, 0.02, (H, W, 1)), 3)
    paper[TOP:TOP + PH, SIDE:SIDE + PW] = tone
    out = np.concatenate([np.clip(paper, 0, 1), np.ones((H, W, 1), dtype=np.float32)], axis=2)
    im = bpy.data.images.new(name, W, H)
    im.pixels[:] = out[::-1].ravel()   # images go bottom row first
    im.filepath_raw = os.path.join(OUT, name + ".png")
    im.file_format = "PNG"
    im.save()
    print("WROTE", im.filepath_raw)
    os.makedirs(GAME, exist_ok=True)
    im.filepath_raw = os.path.join(GAME, name.replace("photo_", "") + ".png")
    im.save()
    return out


prints = []
for i, (name, kind, shot, tint, strength, rim) in enumerate(PRINTS):
    prints.append(develop(name, kind, shot, tint, strength, rim, i + 7))

# a sheet of them on a dark table, for a look before anything goes in the game
cols = 3
w, h = prints[0].shape[1], prints[0].shape[0]
gap = 24
rows = (len(prints) + cols - 1) // cols
sheet = np.ones((rows * (h + gap) + gap, cols * (w + gap) + gap, 4), dtype=np.float32)
sheet[..., :3] = (0.09, 0.075, 0.065)
for i, p in enumerate(prints):
    r, c = divmod(i, cols)
    y, x = gap + r * (h + gap), gap + c * (w + gap)
    sheet[y:y + h, x:x + w] = p
im = bpy.data.images.new("sheet", sheet.shape[1], sheet.shape[0])
im.pixels[:] = sheet[::-1].ravel()
im.filepath_raw = os.path.join(OUT, "sheet.png")
im.file_format = "PNG"
im.save()
print("WROTE", im.filepath_raw)
