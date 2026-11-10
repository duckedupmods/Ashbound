"""Wanted posters for the 8 Legends: inked portrait on torn parchment, 128x176 (the game texture), plus a sheet x3."""
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps, ImageChops

S = Path(sys.argv[1])
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
W, H = 128, 176
F = "C:/Windows/Fonts/"

LEGENDS = [  # id, name lines, last seen, ink tint
    ("rime_penitent", ["THE RIME", "PENITENT"], "the frozen north", (120, 160, 200)),
    ("old_blackbriar", ["OLD", "BLACKBRIAR"], "the deep woods", (90, 130, 70)),
    ("red_plough", ["THE RED", "PLOUGH"], "the open fields", (170, 70, 40)),
    ("sunbreaker", ["SUN-", "BREAKER"], "the dunes", (200, 160, 50)),
    ("grandmother_mire", ["GRANDMOTHER", "MIRE"], "the drowned fens", (90, 140, 90)),
    ("hollow_smile", ["THE HOLLOW", "SMILE"], "the jungle canopy", (60, 170, 160)),
    ("old_harpoon", ["OLD", "HARPOON"], "the grey coast", (90, 120, 150)),
    ("walking_mountain", ["THE WALKING", "MOUNTAIN"], "the red badlands", (180, 100, 60)),
]

PAPER = [(232, 214, 172), (221, 199, 152), (204, 180, 132), (184, 158, 112)]
INK = [(38, 26, 18), (66, 46, 30), (102, 74, 48), (146, 112, 76), (190, 158, 114), (226, 206, 164)]


def parchment(seed):
    r = random.Random(seed)
    im = Image.new("RGB", (W, H), PAPER[0])
    px = im.load()
    for y in range(H):
        for x in range(W):
            n = r.random() * 0.12
            # darker toward the edges, a sun-browned look
            e = min(x, y, W - 1 - x, H - 1 - y) / 18
            e = max(0.0, 1 - e) * 0.35
            k = min(3, int((n + e) * 6))
            px[x, y] = PAPER[k]
    d = ImageDraw.Draw(im)
    for _ in range(4):  # water stains
        cx, cy, rr = r.randint(10, W - 10), r.randint(10, H - 10), r.randint(6, 16)
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=PAPER[2])
    mask = Image.new("L", (W, H), 255)
    md = ImageDraw.Draw(mask)
    for x in range(W):  # torn top and bottom
        md.line((x, 0, x, r.choice((0, 0, 1, 1, 2))), fill=0)
        md.line((x, H - 1 - r.choice((0, 0, 1, 2, 3)), x, H), fill=0)
    for y in range(H):
        md.line((0, y, r.choice((0, 0, 1, 1)), y), fill=0)
        md.line((W - 1 - r.choice((0, 0, 1, 2)), y, W, y), fill=0)
    md.polygon(((W - 14, H), (W, H - 20), (W, H)), fill=0)  # a corner torn off
    return im, mask


def ink(portrait, tint, box):
    """the render as a woodcut print: sepia in a few ink tones, the Legend's colour kept faintly"""
    a = portrait.getchannel("A")
    bb = a.getbbox()
    portrait, a = portrait.crop(bb), a.crop(bb)
    bw, bh = box
    k = min(bw / portrait.width, bh / portrait.height)
    size = (max(1, int(portrait.width * k)), max(1, int(portrait.height * k)))
    portrait = portrait.resize(size, Image.LANCZOS)
    a = a.resize(size, Image.LANCZOS).point(lambda v: 255 if v > 110 else 0)
    g = ImageOps.autocontrast(portrait.convert("L"), cutoff=2)
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    gp, op, ap, cp = g.load(), out.load(), a.load(), portrait.load()
    for y in range(size[1]):
        for x in range(size[0]):
            if not ap[x, y]:
                continue
            v = gp[x, y] / 255
            i = min(len(INK) - 2, int(v ** 1.15 * (len(INK) - 1)))
            c = INK[i]
            src = cp[x, y]
            mix = 0.28 if i >= 2 else 0.12
            c = tuple(int(c[j] * (1 - mix) + (src[j] * 0.5 + tint[j] * 0.5) * mix) for j in range(3))
            op[x, y] = c + (255,)
    # an ink outline round the silhouette
    edge = a.filter(ImageFilter.MaxFilter(3))
    line = Image.new("RGBA", size, INK[0] + (255,))
    base = Image.new("RGBA", size, (0, 0, 0, 0))
    base.paste(line, (0, 0), ImageChops.subtract(edge, a))
    base.alpha_composite(out)
    return base


def text_center(d, y, s, font, fill):
    w = d.textlength(s, font=font)
    d.text(((W - w) / 2, y), s, font=font, fill=fill)


def poster(i, lid, lines, seen, tint, rank="C", bounty="400"):
    im, mask = parchment(i * 7 + 3)
    d = ImageDraw.Draw(im)
    big = ImageFont.truetype(F + "georgiab.ttf", 19)
    mid = ImageFont.truetype(F + "georgiab.ttf", 10)
    small = ImageFont.truetype(F + "georgia.ttf", 8)
    smallb = ImageFont.truetype(F + "georgiab.ttf", 8)
    text_center(d, 4, "WANTED", big, (120, 28, 20))
    d.line((14, 27, W - 14, 27), fill=INK[1])
    text_center(d, 28, "BY ORDER OF THE GUILD", small, INK[1])
    # the portrait in a ruled frame
    fx0, fy0, fx1, fy1 = 10, 41, W - 10, 121
    d.rectangle((fx0, fy0, fx1, fy1), fill=PAPER[1], outline=INK[0])
    d.rectangle((fx0 + 2, fy0 + 2, fx1 - 2, fy1 - 2), outline=INK[2])
    p = ink(Image.open(S / ("%s.png" % lid)).convert("RGBA"), tint, (fx1 - fx0 - 8, fy1 - fy0 - 6))
    im.paste(p, ((W - p.width) // 2, fy1 - 3 - p.height), p)
    y = 124
    for ln in lines:
        text_center(d, y, ln, mid, INK[0])
        y += 11
    text_center(d, y + 1, "last seen in " + seen, small, INK[2])
    d.line((22, y + 13, W - 22, y + 13), fill=INK[3])
    text_center(d, y + 15, "REWARD  " + bounty + "  COINS", smallb, (120, 28, 20))
    # the rank stamped in red, tilted, over the portrait's corner
    st = Image.new("RGBA", (30, 30), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    red = (150, 30, 24, 220)
    sd.ellipse((1, 1, 28, 28), outline=red, width=2)
    sd.ellipse((5, 5, 24, 24), outline=red, width=1)
    rf = ImageFont.truetype(F + "georgiab.ttf", 14)
    sd.text((15 - sd.textlength(rank, font=rf) / 2, 6), rank, font=rf, fill=red)
    st = st.rotate(-14, resample=Image.NEAREST)
    im.paste(st, (fx1 - 27, fy1 - 24), st)
    # the nail
    d.ellipse((W // 2 - 3, 1, W // 2 + 2, 6), fill=(70, 70, 76), outline=INK[0])
    im = im.convert("RGBA")
    im.putalpha(mask)
    return im


ims = []
for i, (lid, lines, seen, tint) in enumerate(LEGENDS):
    p = poster(i, lid, lines, seen, tint)
    p.save(OUT / ("wanted_%s.png" % lid))
    ims.append(p)
# the game's textures: one per Legend per rank, the bounty baked in (Bounties.REWARD), and the SLAIN stamp laid over
if len(sys.argv) > 3:
    TEX = Path(sys.argv[3])
    TEX.mkdir(parents=True, exist_ok=True)
    REWARD = {"F": "150", "E": "300", "D": "550", "C": "1,100", "B": "1,900", "A": "4,000", "S": "7,500"}
    for i, (lid, lines, seen, tint) in enumerate(LEGENDS):
        for rk, pay in REWARD.items():
            poster(i, lid, lines, seen, tint, rk, pay).save(TEX / ("%s_%s.png" % (lid, rk.lower())))
    sl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    big = Image.new("RGBA", (150, 44), (0, 0, 0, 0))
    bd = ImageDraw.Draw(big)
    red = (150, 24, 18, 235)
    bd.rectangle((2, 2, 147, 41), outline=red, width=3)
    f = ImageFont.truetype(F + "georgiab.ttf", 30)
    bd.text((75 - bd.textlength("SLAIN", font=f) / 2, 4), "SLAIN", font=f, fill=red)
    rng = random.Random(9)
    px = big.load()
    for _ in range(900):  # a worn stamp: ink missing in specks
        x, y = rng.randrange(150), rng.randrange(44)
        if px[x, y][3]:
            px[x, y] = (0, 0, 0, 0)
    big = big.rotate(28, expand=True, resample=Image.BICUBIC)
    sl.paste(big, ((W - big.width) // 2, 70 - big.height // 2), big)
    sl.save(TEX / "slain.png")
    # what's left on the nail when a hunter tears it down: the top strip, its bottom edge ripped (WantedPosterRenderer.TORN rows)
    TORN = 34
    top = Image.open(TEX / "rime_penitent_f.png").convert("RGBA")
    rr = random.Random(5)
    tp = top.load()
    edge = TORN - 8
    for x in range(W):
        edge = max(TORN - 14, min(TORN - 1, edge + rr.choice((-2, -1, -1, 0, 1, 1, 2))))
        for y in range(edge, H):
            tp[x, y] = (0, 0, 0, 0)
        if tp[x, edge - 1][3]:
            tp[x, edge - 1] = PAPER[3] + (255,)   # the torn fibres show lighter than the ink, darker than the paper
    top.save(TEX / "torn.png")
    print("textures:", len(list(TEX.glob("*.png"))))
k, gap = 3, 18
sheet = Image.new("RGB", (4 * (W * k + gap) + gap, 2 * (H * k + gap) + gap), (58, 44, 34))
# a timber board behind them
sd = ImageDraw.Draw(sheet)
for y in range(0, sheet.height, 26):
    sd.line((0, y, sheet.width, y), fill=(44, 32, 24), width=2)
for i, p in enumerate(ims):
    big = p.resize((W * k, H * k), Image.NEAREST)
    x, y = gap + (i % 4) * (W * k + gap), gap + (i // 4) * (H * k + gap)
    sheet.paste(big, (x, y), big)
sheet.save(OUT / "wanted_sheet.png")
print(OUT / "wanted_sheet.png")
