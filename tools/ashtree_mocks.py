"""Mocks for the "Ash Tree" redesign (10/29, after the web research): a painted burning ash tree as the overview
(trunk = Core, 10 branches = the weapon areas, taken nodes glow up the branch, Diablo 4 style) and one area page drawn
as its weapon (Grim Dawn constellations) with ~20 ranked nodes (Last Epoch) coloured by role (Wynncraft).
Writes tools/renders/ashtree_overview.png and ashtree_sword.png.
"""
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
import skilltree as T
import treeicons as I

OUT = Path(__file__).resolve().parent / "renders"
W, H = 1600, 900
F = lambda sz, b=False: ImageFont.truetype("C:/Windows/Fonts/" + ("consolab.ttf" if b else "consola.ttf"), sz)
EMBER, GOLD, IRON, TEXT, DIM = (255, 150, 50), (255, 205, 110), (110, 96, 86), (236, 218, 190), (150, 132, 112)
ROLE = {"stat": ((150, 140, 130), "stat: numbers"), "ember": ((255, 130, 50), "changes a move"),
        "gold": ((255, 210, 100), "new move / skill"), "key": ((220, 50, 60), "keystone: big, with a cost")}


def bezier(p0, p1, p2, p3, n=60):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def limb(d, pts, w0, w1, fill):
    """A tapered branch along a polyline."""
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        a, b = pts[max(0, i - 1)], pts[min(len(pts) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        l = math.hypot(dx, dy) or 1
        nx, ny = -dy / l, dx / l
        w = (w0 + (w1 - w0) * i / (len(pts) - 1)) / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    d.polygon(left + right[::-1], fill=fill)


def background():
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        for x in range(0, W):
            r = math.hypot((x - W / 2) / W, (y - H * 0.95) / H)
            warm = max(0, 1 - r * 1.6)
            px[x, y] = (int(14 + 60 * warm ** 2), int(10 + 22 * warm ** 2), int(10 + 8 * warm ** 2))
    d = ImageDraw.Draw(img)
    rnd = random.Random(5)
    for _ in range(700):  # falling ash
        x, y, g = rnd.uniform(0, W), rnd.uniform(0, H), rnd.randint(40, 80)
        d.rectangle((x, y, x + 1, y + 1), fill=(g, g - 6, g - 12))
    return img


def glow(img, layer, radius=12, gain=1.0):
    blur = layer.filter(ImageFilter.GaussianBlur(radius))
    if gain != 1:
        blur = blur.point(lambda v: min(255, int(v * gain)))
    return ImageChops.add(ImageChops.add(img, blur), layer)


def emblem(img, d, x, y, r, motif, colour, lit, frac):
    d.ellipse((x - r - 6, y - r - 6, x + r + 6, y + r + 6), fill=(20, 15, 13))
    ring = EMBER if lit else (90, 78, 70)
    d.ellipse((x - r, y - r, x + r, y + r), fill=(42, 30, 24) if lit else (28, 22, 19), outline=ring, width=4)
    if frac > 0:  # progress arc
        d.arc((x - r - 5, y - r - 5, x + r + 5, y + r + 5), -90, -90 + 360 * frac, fill=GOLD, width=4)
    s = 4 if r > 40 else 3
    ic = I.icon(motif, colour).resize((16 * s, 16 * s), Image.NEAREST)
    if not lit:
        ic = Image.merge("RGBA", [c.point(lambda v: int(v * 0.55)) for c in ic.split()[:3]] + [ic.split()[3]])
    img.paste(ic, (x - 8 * s, y - 8 * s), ic)


def label(d, x, y, text, sub=None, colour=TEXT):
    f = F(17, True)
    d.text((x - d.textlength(text, f) / 2, y), text, font=f, fill=colour)
    if sub:
        f2 = F(14)
        d.text((x - d.textlength(sub, f2) / 2, y + 20), sub, font=f2, fill=DIM)


def topbar(d, title, sub, right):
    d.rectangle((0, 0, W, 62), fill=(12, 9, 8))
    d.line((0, 62, W, 62), fill=(90, 60, 40), width=2)
    d.text((28, 12), title, font=F(30, True), fill=GOLD)
    d.text((28 + d.textlength(title, F(30, True)) + 20, 22), sub, font=F(16), fill=DIM)
    d.text((W - 28 - d.textlength(right, F(18, True)), 20), right, font=F(18, True), fill=EMBER)


def overview():
    img = background()
    bark = Image.new("RGB", (W, H))
    bd = ImageDraw.Draw(bark)
    lit = Image.new("RGB", (W, H))
    ld = ImageDraw.Draw(lit)
    rnd = random.Random(11)
    areas = T.AREAS
    progress = {"sword": 14 / 22, "shield": 6 / 20, "bow": 2 / 20}
    # roots
    for k in range(9):
        a = math.pi * (0.1 + 0.8 * k / 8)
        end = (800 + math.cos(a) * rnd.uniform(260, 420), 900 + rnd.uniform(-10, 30))
        pts = bezier((800, 800), (800 + math.cos(a) * 80, 850), (end[0], end[1] - 50), end, 30)
        limb(bd, pts, 40, 6, (34, 26, 24))
    trunk = bezier((800, 900), (790, 760), (812, 640), (800, 520), 40)
    limb(bd, trunk, 120, 70, (40, 30, 27))
    ends = []
    for i, a in enumerate(areas):
        ex, ey = 138 + i * 147, 520 - 380 * math.sin(math.pi * (i + 0.5) / len(areas))
        ends.append((int(ex), int(ey)))
        start = (800 + (i - 4.5) * 7, 600 - abs(i - 4.5) * 18)
        pts = bezier(start, (800 + (ex - 800) * 0.15, start[1] - 120), (ex - (ex - 800) * 0.25, ey + 110), (ex, ey + 46))
        limb(bd, pts, 34, 9, (44, 33, 29))
        for t in (0.45, 0.7):  # twigs
            j = int(t * (len(pts) - 1))
            bx, by = pts[j]
            side = rnd.choice((-1, 1))
            tw = bezier((bx, by), (bx + side * 30, by - 30), (bx + side * 60, by - 50), (bx + side * 70, by - 80), 16)
            limb(bd, tw, 8, 2, (40, 30, 27))
            if a["id"] in progress and progress[a["id"]] > t:
                for q in range(len(tw) - 1):
                    ld.line((tw[q], tw[q + 1]), fill=(170, 70, 20), width=2)
        f = progress.get(a["id"], 0)
        if f:
            n = int(f * (len(pts) - 1))
            for q in range(n):
                ld.line((pts[q], pts[q + 1]), fill=(255, 120, 30), width=5)
            # ember nodes along the lit part
            for q in range(0, n, 8):
                x, y = pts[q]
                ld.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(255, 190, 90))
        # unlit nodes along the branch, faint
        for q in range(int(f * (len(pts) - 1)) + 8, len(pts) - 6, 8):
            x, y = pts[q]
            bd.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(70, 58, 52))
    # cracks of fire in the trunk (the Core, all lit)
    for q in range(0, len(trunk) - 1):
        x, y = trunk[q]
        ld.line(((x + math.sin(q * 0.7) * 14, y), (x + math.sin((q + 1) * 0.7) * 14, trunk[q + 1][1])), fill=(255, 110, 25), width=3)
    img = ImageChops.lighter(img, bark)
    img = glow(img, lit, 14, 1.4)
    d = ImageDraw.Draw(img)
    # sparks rising off the lit branches
    for _ in range(260):
        x, y = rnd.uniform(200, 1400), rnd.uniform(80, 880)
        if img.getpixel((int(x), int(y)))[0] > 70 or rnd.random() < 0.05:
            s = rnd.choice((1, 1, 2))
            d.rectangle((x, y - 10, x + s, y - 10 + s), fill=(255, rnd.randint(150, 220), 90))
    emblem(img, d, 800, 760, 56, "flame", "#ff9a40", True, 1.0)
    label(d, 800, 826, "THE CORE", "health  stamina  mana  - 9 / 24", GOLD)
    for (x, y), a in zip(ends, areas):
        f = progress.get(a["id"], 0)
        emblem(img, d, x, y, 44, T.WEAPON_ICON[a["id"]], a["colour"], f > 0, f)
        total = 20 if a["id"] != "sword" else 22
        label(d, x, y + 54, a["name"].upper(), f"{round(f * total)} / {total}", GOLD if f else TEXT)
    topbar(d, "THE ASH TREE", "pick a branch - only the weapon in your hand feeds it", "Lv 24   3 points   [ LEVEL UP ]")
    d.text((28, H - 34), "hover: what the branch gives   click: open it   Esc: close", font=F(15), fill=DIM)
    img.save(OUT / "ashtree_overview.png")


# ---- sword page --------------------------------------------------------------------------------------------------
SWORD = [  # id, role, name, rank, max, x, y, about
    ("grip", "stat", "Grip", 5, 5, 560, 810, "+1.5% sword damage per rank"),
    ("tempo", "stat", "Tempo", 3, 5, 560, 735, "+1.5% attack speed per rank"),
    ("guard_l", "ember", "Riposte", 1, 1, 400, 660, "after a parry, your next hit within 4 s deals +60%"),
    ("guard_l2", "ember", "Disarm", 0, 1, 290, 660, "a riposte knocks the weapon aside: the enemy can't attack for 1.5 s"),
    ("guard_r", "ember", "Flowing Steel", 1, 1, 720, 660, "+15% damage for 3 s after a dodge"),
    ("guard_r2", "gold", "Lunge", 0, 1, 830, 660, "attack right after a dodge: lunge 4 blocks and stab"),
    ("guard", "gold", "Swordmaster", 1, 1, 560, 660, "learn Swordmaster: faster swings"),
    ("gap", "stat", "Find the Gap", 3, 3, 560, 580, "+3% armour negation per rank"),
    ("edge_l", "stat", "Keen Edge", 2, 3, 490, 510, "+2% crit damage per rank"),
    ("edge_r", "stat", "Footwork", 0, 3, 630, 510, "+1.5% move speed with a sword out"),
    ("duel", "ember", "Duelist", 0, 1, 560, 440, "+12% damage while only one enemy is within 8 blocks"),
    ("bleed", "ember", "Open Wounds", 0, 1, 490, 370, "crits make the enemy bleed for 3 s"),
    ("arc", "gold", "Cleaving Arc", 0, 1, 630, 370, "every 3rd swing cuts everything in a wide arc in front"),
    ("fuller", "stat", "Fuller", 0, 5, 560, 300, "+1.5% sword damage per rank"),
    ("flourish", "ember", "Flourish", 0, 1, 560, 225, "a kill refunds the stamina of your last swing"),
    ("tip", "key", "Blade Dance", 0, 1, 560, 130, "every 4th combo hit strikes twice; your first hit on an enemy deals -25%"),
]
LINKS = [("grip", "tempo"), ("tempo", "guard"), ("guard", "guard_l"), ("guard_l", "guard_l2"), ("guard", "guard_r"),
         ("guard_r", "guard_r2"), ("guard", "gap"), ("gap", "edge_l"), ("gap", "edge_r"), ("edge_l", "duel"),
         ("edge_r", "duel"), ("duel", "bleed"), ("duel", "arc"), ("bleed", "fuller"), ("arc", "fuller"),
         ("fuller", "flourish"), ("flourish", "tip")]


def sword_page():
    img = background()
    ghost = Image.new("RGB", (W, H))
    gd = ImageDraw.Draw(ghost)
    # the faint sword picture behind the nodes (the constellation's figure)
    blade = [(560, 70), (610, 150), (610, 610), (510, 610), (510, 150)]
    gd.polygon(blade, outline=(70, 66, 74), width=3)
    gd.line(((560, 120), (560, 600)), fill=(46, 44, 50), width=2)
    gd.rounded_rectangle((250, 640, 870, 680), 18, outline=(70, 66, 74), width=3)
    gd.rectangle((535, 690, 585, 790), outline=(70, 66, 74), width=3)
    gd.ellipse((530, 785, 590, 845), outline=(70, 66, 74), width=3)
    img = ImageChops.add(img, ghost.filter(ImageFilter.GaussianBlur(1)))
    nodes = {n[0]: n for n in SWORD}
    taken = lambda n: n[3] > 0
    lit = Image.new("RGB", (W, H))
    ld = ImageDraw.Draw(lit)
    d = ImageDraw.Draw(img)
    for a, b in LINKS:
        A, B = nodes[a], nodes[b]
        if taken(A) and taken(B):
            ld.line(((A[5], A[6]), (B[5], B[6])), fill=(255, 130, 40), width=5)
        else:
            d.line(((A[5], A[6]), (B[5], B[6])), fill=(78, 66, 58), width=3)
    img = glow(img, lit, 9, 1.2)
    d = ImageDraw.Draw(img)
    hover = "arc"
    for n in SWORD:
        nid, role, name, rank, mx, x, y, about = n
        col = ROLE[role][0]
        have = rank > 0
        r = {"stat": 20, "ember": 26, "gold": 28, "key": 38}[role]
        edge = col if have else tuple(int(c * 0.45) for c in col)
        fill = tuple(int(c * 0.22) for c in col) if have else (26, 21, 18)
        if role == "key":
            pts = [(x + r * math.cos(k * math.pi / 4 + math.pi / 8), y + r * math.sin(k * math.pi / 4 + math.pi / 8)) for k in range(8)]
            d.polygon(pts, fill=fill, outline=edge, width=4)
        elif role == "gold":
            d.polygon([(x, y - r), (x + r, y), (x, y + r), (x - r, y)], fill=fill, outline=edge, width=4)
        else:
            d.ellipse((x - r, y - r, x + r, y + r), fill=fill, outline=edge, width=4 if role == "ember" else 3)
        motif = {"stat": "sword", "ember": "slash", "gold": "star" if "star" in I.M else "sword", "key": "crown"}[role]
        motif = {"grip": "sword", "tempo": "slash", "gap": "crack", "edge_l": "burst", "edge_r": "boot", "fuller": "sword",
                 "flourish": "wind", "guard_l": "shield", "guard_l2": "crack", "guard_r": "wind", "guard_r2": "spear",
                 "bleed": "drop", "duel": "eye", "arc": "slash", "guard": "sword", "tip": "crown"}.get(nid, motif)
        if motif not in I.M:
            motif = "sword"
        s = 2 if role == "stat" else 3 if role != "key" else 4
        ic = I.icon(motif, "#%02x%02x%02x" % col).resize((16 * s, 16 * s), Image.NEAREST)
        if not have:
            ic = Image.merge("RGBA", [c.point(lambda v: int(v * 0.45)) for c in ic.split()[:3]] + [ic.split()[3]])
        img.paste(ic, (x - 8 * s, y - 8 * s), ic)
        if mx > 1:  # rank pips
            for k in range(mx):
                px = x - (mx - 1) * 6 + k * 12
                d.rectangle((px - 4, y + r + 6, px + 4, y + r + 10), fill=GOLD if k < rank else (60, 50, 44))
        f = F(15, role != "stat")
        tx = x + r + 10 if x >= 560 else x - r - 10 - d.textlength(name, f)
        ty = y - 9
        if x == 560:
            tx = x + r + 12
        if y == 660:  # the crossguard row: names go under the nodes
            tx, ty = x - d.textlength(name, f) / 2, y + r + 16
        d.text((tx, ty), name, font=f, fill=TEXT if have else DIM)
        if nid == hover:
            d.ellipse((x - r - 8, y - r - 8, x + r + 8, y + r + 8), outline=GOLD, width=2)
    # side panel: hovered node
    h = nodes[hover]
    x0 = 1060
    d.rectangle((x0, 62, W, H), fill=(18, 13, 11))
    d.line((x0, 62, x0, H), fill=(90, 60, 40), width=2)
    d.text((x0 + 30, 96), h[2].upper(), font=F(28, True), fill=ROLE[h[1]][0])
    d.text((x0 + 30, 134), ROLE[h[1]][1], font=F(15), fill=DIM)
    yy = 176
    words, line = h[7].split(), ""
    for w in words:
        if d.textlength(line + " " + w, F(18)) > 480:
            d.text((x0 + 30, yy), line.strip(), font=F(18), fill=TEXT)
            yy += 26
            line = ""
        line += " " + w
    d.text((x0 + 30, yy), line.strip(), font=F(18), fill=TEXT)
    d.text((x0 + 30, yy + 44), "1 point  -  needs Duelist", font=F(16, True), fill=EMBER)
    d.line((x0 + 30, 330, W - 30, 330), fill=(60, 44, 34), width=1)
    d.text((x0 + 30, 348), "THE BLADE  -  14 / 22", font=F(18, True), fill=GOLD)
    for i, s in enumerate(["+7.5% sword damage", "+4.5% attack speed", "+9% armour negation", "+4% crit damage",
                           "Swordmaster learned", "Riposte, Flowing Steel"]):
        d.text((x0 + 30, 382 + i * 26), s, font=F(16), fill=TEXT)
    d.line((x0 + 30, 560, W - 30, 560), fill=(60, 44, 34), width=1)
    for i, (role, (col, txt)) in enumerate(ROLE.items()):
        y = 586 + i * 34
        if role == "gold":
            d.polygon([(x0 + 42, y - 10), (x0 + 52, y), (x0 + 42, y + 10), (x0 + 32, y)], outline=col, width=3)
        elif role == "key":
            d.regular_polygon((x0 + 42, y, 11), 8, outline=col, width=3)
        else:
            d.ellipse((x0 + 32, y - 10, x0 + 52, y + 10), outline=col, width=3)
        d.text((x0 + 66, y - 9), txt, font=F(16), fill=TEXT)
    d.text((x0 + 30, 740), "stat nodes take up to 5 points", font=F(15), fill=DIM)
    d.text((x0 + 30, 762), "a full branch lights the whole sword", font=F(15), fill=DIM)
    topbar(d, "THE BLADE", "swords - feeds only while a sword is in your hand", "3 points   Esc: back to the tree")
    img.save(OUT / "ashtree_sword.png")


if __name__ == "__main__":
    overview()
    sword_page()
    print("ok")
