"""Mock-ups of other ways to lay out the Ash Tree (10/29: the big zoomable web felt cramped, lagged zoomed out, and
lost its icons). Writes tools/renders/tree_mock_{1..4}.png. Uses the real icons and the approved UI look: dark
char, falling ash, cut-corner iron frames, ember accents.
"""
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
import skilltree as T
import treeicons as I

OUT = Path(__file__).resolve().parent / "renders"
W, H = 1600, 900
F = lambda sz, b=False: ImageFont.truetype("C:/Windows/Fonts/" + ("consolab.ttf" if b else "consola.ttf"), sz)
EMBER, IRON, TEXT, DIM = (255, 170, 70), (110, 96, 86), (232, 214, 186), (150, 132, 112)
AREAS = [("core", "The Core", T.CORE["colour"], "flame")] + [(a["id"], a["name"], a["colour"], T.WEAPON_ICON[a["id"]]) for a in T.AREAS]


def hexc(h, f=1.0):
    return tuple(min(255, int(int(h[i:i + 2], 16) * f)) for i in (1, 3, 5))


def canvas():
    img = Image.new("RGB", (W, H), (16, 12, 11))
    d = ImageDraw.Draw(img)
    rnd = random.Random(3)
    for _ in range(900):
        x, y, g = rnd.uniform(0, W), rnd.uniform(0, H), rnd.randint(34, 64)
        d.rectangle((x, y, x + 1, y + 1), fill=(g, g - 8, g - 14))
    return img, d


def frame(d, x0, y0, x1, y1, cut=10, fill=(26, 20, 17), edge=IRON, w=3):
    pts = [(x0 + cut, y0), (x1 - cut, y0), (x1, y0 + cut), (x1, y1 - cut), (x1 - cut, y1), (x0 + cut, y1), (x0, y1 - cut), (x0, y0 + cut)]
    d.polygon(pts, fill=fill, outline=edge, width=w)


def icon(img, motif, colour, x, y, scale, badge=None, dim=1.0):
    ic = I.icon(motif, colour, badge).resize((16 * scale, 16 * scale), Image.NEAREST)
    if dim < 1:
        px = ic.load()
        for j in range(ic.size[1]):
            for i in range(ic.size[0]):
                r, g, b, a = px[i, j]
                px[i, j] = (int(r * dim), int(g * dim), int(b * dim), a)
    img.paste(ic, (int(x - 8 * scale), int(y - 8 * scale)), ic)


def node(img, d, x, y, kind, motif, colour, badge=None, have=False, can=False, label=None):
    s = {"small": 18, "notable": 30, "keystone": 42}[kind]
    edge = EMBER if have else (200, 130, 60) if can else (70, 58, 50)
    bg = (60, 38, 22) if have else (30, 24, 20)
    if kind == "keystone":
        pts = [(x + s * math.cos(k * math.pi / 4 + math.pi / 8), y + s * math.sin(k * math.pi / 4 + math.pi / 8)) for k in range(8)]
        d.polygon(pts, fill=bg, outline=(255, 200, 100) if have else edge, width=4)
    else:
        frame(d, x - s, y - s, x + s, y + s, cut=6 if kind == "notable" else 4, fill=bg, edge=edge, w=3 if kind == "notable" else 2)
    icon(img, motif, colour, x, y, 2 if kind == "small" else 3 if kind == "notable" else 4, badge, 1.0 if have else 0.75 if can else 0.45)
    if label:
        f = F(15, kind != "small")
        tw = d.textlength(label, font=f)
        d.text((x - tw / 2, y + s + 6), label, font=f, fill=TEXT if have or can else DIM)


def topbar(d, title, sub):
    d.rectangle((0, 0, W, 54), fill=(22, 16, 13))
    d.line([(0, 54), (W, 54)], fill=(140, 76, 30), width=3)
    d.text((24, 12), title, font=F(28, True), fill=EMBER)
    d.text((24 + d.textlength(title, font=F(28, True)) + 24, 20), sub, font=F(16), fill=TEXT)
    for i, (lab, on) in enumerate((("Level up  1 820 Ash", True), ("Reset tree", False))):
        x = W - 420 + i * 220
        frame(d, x, 10, x + 200, 44, cut=6, fill=(70, 40, 18) if on else (34, 26, 22), edge=EMBER if on else IRON)
        tw = d.textlength(lab, font=F(16, True))
        d.text((x + 100 - tw / 2, 18), lab, font=F(16, True), fill=TEXT)


def caption(d, text):
    d.rectangle((0, H - 34, W, H), fill=(10, 8, 7))
    d.text((24, H - 27), text, font=F(16), fill=DIM)


def area_nodes(aid):
    """the area's notables and keystone, from the real tree data"""
    if aid == "core":
        return [(n["name"], T.SPECIAL_ICON[n["name"]]) for n in T.CORE["notables"]], None
    a = next(a for a in T.AREAS if a["id"] == aid)
    return [(n["name"], T.SPECIAL_ICON[n["name"]]) for n in a["notables"]], (a["keystone"]["name"], T.SPECIAL_ICON[a["keystone"]["name"]])


def split(m):
    return (m, None) if isinstance(m, str) else m


# --------------------------------------------------------------------------------------------- 1: one page per area
def mock_pages():
    img, d = canvas()
    topbar(d, "THE ASH TREE", "Level 24   Points 3   Ash 1 820 / 1 820")
    # tabs down the left: one per area, its weapon's icon
    for i, (aid, name, col, motif) in enumerate(AREAS):
        y = 74 + i * 68
        on = aid == "sword"
        frame(d, 16, y, 76, y + 60, cut=8, fill=(64, 40, 22) if on else (28, 22, 19), edge=EMBER if on else IRON)
        icon(img, motif, col if aid != "core" else T.CORE_SPECIAL, 46, y + 30, 3, dim=1 if on else 0.7)
        pts = {"core": 9, "sword": 11, "shield": 4}.get(aid, 0)
        if pts:
            d.text((62, y + 40), str(pts), font=F(14, True), fill=EMBER)
    frame(d, 96, 70, 1180, H - 46, cut=14)
    d.text((124, 86), "THE BLADE", font=F(30, True), fill=hexc("#e0e4ec"))
    d.text((124, 124), "11 points here   counts while you hold a sword", font=F(15), fill=DIM)
    # a tiered tree, top to bottom: 5 rows, the keystone at the foot
    col = "#e0e4ec"
    notes, key = area_nodes("sword")
    cx = 640
    rows = [
        [("small", "sword", None, "Edge")],
        [("small", "slash", None, "Tempo"), ("small", "crack", None, "Find the Gap"), ("small", "sword", None, "Edge")],
        [("notable",) + split(notes[0][1]) + (notes[0][0],), ("small", "slash", None, "Tempo"), ("notable",) + split(notes[1][1]) + (notes[1][0],)],
        [("small", "crack", None, "Find the Gap"), ("small", "sword", None, "Edge"), ("small", "slash", None, "Tempo"), ("small", "sword", None, "Edge")],
        [("notable",) + split(notes[2][1]) + (notes[2][0],), ("small", "crack", None, "Find the Gap"), ("notable",) + split(notes[3][1]) + (notes[3][0],)],
        [("keystone",) + split(key[1]) + (key[0],)],
    ]
    pos = []
    for r, row in enumerate(rows):
        y = 210 + r * 108
        n = len(row)
        pos.append([(cx + (i - (n - 1) / 2) * 230, y) for i in range(n)])
    have = {(0, 0), (1, 0), (1, 1), (2, 0), (2, 1), (3, 0), (3, 1)}
    for r in range(len(rows) - 1):
        for i, (x, y) in enumerate(pos[r]):
            for j, (x2, y2) in enumerate(pos[r + 1]):
                if abs(x - x2) < 260:
                    lit = (r, i) in have and (r + 1, j) in have
                    d.line([(x, y), (x2, y2)], fill=EMBER if lit else (70, 60, 52), width=4 if lit else 3)
    for r, row in enumerate(rows):
        for i, (kind, motif, badge, label) in enumerate(row):
            x, y = pos[r][i]
            h = (r, i) in have
            can = not h and any((r - 1, j) in have and abs(pos[r - 1][j][0] - x) < 260 for j in range(len(pos[r - 1]))) if r else False
            node(img, d, x, y, kind, motif, col, badge, h, can, label)
    # the side panel: what's under the cursor
    frame(d, 1196, 70, W - 16, H - 46, cut=14)
    icon(img, "cross_swords", col, 1300, 150, 5)
    d.text((1370, 120), "Riposte", font=F(26, True), fill=hexc(col))
    d.text((1370, 156), "Notable", font=F(16), fill=EMBER)
    y = 230
    for ln in ("After a parry, your next hit", "within 4 s deals +60%.", "", "Counts while you hold a sword.", "", "Click: take it (1 point)"):
        d.text((1220, y), ln, font=F(17), fill=TEXT if "Click" not in ln else (120, 220, 120))
        y += 28
    d.text((1220, 520), "YOUR BUILD", font=F(18, True), fill=EMBER)
    for k, ln in enumerate(("+6% sword damage", "+4% attack speed", "+6% armour negation", "Swordmaster (Epic Fight)", "Flowing Steel")):
        d.text((1220, 552 + k * 26), ln, font=F(16), fill=TEXT)
    caption(d, "1  PAGES: one page per area, tabs down the side with each weapon's icon and the points spent there. "
               "Nodes are big, no zooming, no lag.")
    img.save(OUT / "tree_mock_1.png")


# --------------------------------------------------------------------------------------------- 2: constellations
def mock_stars():
    img = Image.new("RGB", (W, H), (8, 8, 16))
    d = ImageDraw.Draw(img)
    rnd = random.Random(11)
    for _ in range(1400):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        g = rnd.randint(40, 140)
        d.point((x, y), fill=(g, g, min(255, g + 30)))
    for r in range(300, 0, -5):
        k = 1 - r / 300
        d.ellipse((W / 2 - r, H / 2 + 20 - r, W / 2 + r, H / 2 + 20 + r), fill=(int(8 + 40 * k), int(8 + 16 * k), int(16 + 6 * k)))
    topbar(d, "THE ASH TREE", "the Core in the middle, ten constellations round it; zoom in on one to see its stars")
    cx, cy = W / 2, H / 2 + 20
    node(img, d, cx, cy, "keystone", "flame", T.CORE_SPECIAL, None, True, False, "The Core")
    for i, (aid, name, col, motif) in enumerate(AREAS[1:]):
        a = i * 2 * math.pi / 10 - math.pi / 2
        # a small constellation: 5-6 stars in a shape, its emblem in the middle
        ex, ey = cx + 330 * math.cos(a), cy + 300 * math.sin(a)
        d.line([(cx + 60 * math.cos(a), cy + 60 * math.sin(a)), (ex - 40 * math.cos(a), ey - 40 * math.sin(a))], fill=hexc(col, 0.4), width=2)
        rr = random.Random(i)
        stars = [(ex + rr.uniform(-80, 80), ey + rr.uniform(-60, 60)) for _ in range(6)]
        for s1, s2 in zip(stars, stars[1:]):
            d.line([s1, s2], fill=hexc(col, 0.5), width=2)
        for sx, sy in stars:
            d.ellipse((sx - 4, sy - 4, sx + 4, sy + 4), fill=hexc(col))
        frame(d, ex - 34, ey - 34, ex + 34, ey + 34, cut=10, fill=(20, 18, 30), edge=hexc(col, 0.9))
        icon(img, motif, col, ex, ey, 3)
        tw = d.textlength(name.upper(), font=F(17, True))
        d.text((ex - tw / 2, ey + 40), name.upper(), font=F(17, True), fill=hexc(col))
    caption(d, "2  CONSTELLATIONS: the overview is 11 big emblems (no tiny nodes); click one and the camera flies into "
               "that constellation, its stars big with their icons.")
    img.save(OUT / "tree_mock_2.png")


# --------------------------------------------------------------------------------------------- 3: boards
def mock_boards():
    img, d = canvas()
    topbar(d, "THE ASH TREE", "boards of tiles: the Core board in the middle, a weapon board through each gate")
    cell = 64
    def board(ox, oy, n, aid, col, motif, full=True):
        frame(d, ox - 10, oy - 10, ox + n * cell + 10, oy + n * cell + 10, cut=12, fill=(24, 19, 16))
        notes, key = area_nodes(aid)
        rr = random.Random(hash(aid) & 999)
        for j in range(n):
            for i in range(n):
                x, y = ox + i * cell + cell / 2, oy + j * cell + cell / 2
                if not full and rr.random() < 0.25:
                    continue
                centre = i == n // 2 and j == n // 2
                corner = (i, j) in ((0, 0), (n - 1, 0), (0, n - 1), (n - 1, n - 1))
                have = abs(i - n // 2) + abs(j - n // 2) <= 1 and aid in ("core", "sword")
                if centre:
                    node(img, d, x, y, "keystone" if aid != "core" else "notable", split(key[1])[0] if key else "flame", col, None, have)
                elif corner:
                    m = notes[(i > 0) + 2 * (j > 0)][1]
                    node(img, d, x, y, "notable", split(m)[0], col, split(m)[1], False, have)
                else:
                    stat = ["sword", "slash", "crack"][(i * 3 + j) % 3] if aid == "sword" else ["heart", "wind", "boot", "crystal"][(i + j) % 4]
                    node(img, d, x, y, "small", stat if aid == "sword" else stat, col if aid != "core" else T.STAT_COLOUR[
                        {"heart": "health%", "wind": "stamina", "boot": "move%", "crystal": "mana"}[stat]] if aid == "core" else col, None, have,
                         not have and abs(i - n // 2) + abs(j - n // 2) == 2)
        d.text((ox, oy - 40), [a[1] for a in AREAS if a[0] == aid][0].upper(), font=F(20, True), fill=hexc(col))
    board(560, 250, 7, "core", T.CORE_SPECIAL, "flame")
    board(1080, 250, 5, "sword", "#e0e4ec", "sword")
    d.line([(1018, 474), (1070, 474)], fill=EMBER, width=6)
    frame(d, 1020, 452, 1068, 496, cut=6, fill=(70, 40, 18), edge=EMBER)
    for k, (aid, name, col, motif) in enumerate(AREAS[2:6]):
        x = 60 + (k % 2) * 220
        y = 260 + (k // 2) * 240
        frame(d, x, y, x + 180, y + 180, cut=12, fill=(22, 18, 15), edge=hexc(col, 0.6))
        icon(img, motif, col, x + 90, y + 80, 5, dim=0.6)
        tw = d.textlength(name, font=F(16, True))
        d.text((x + 90 - tw / 2, y + 140), name, font=F(16, True), fill=hexc(col, 0.8))
    caption(d, "3  BOARDS: square boards of tiles you light up from a gate (Diablo IV style). Whole boards zoom as one "
               "picture, so no lag and the icons stay.")
    img.save(OUT / "tree_mock_3.png")


# --------------------------------------------------------------------------------------------- 4: the wheel
def mock_wheel():
    img, d = canvas()
    topbar(d, "THE ASH TREE", "pick a slice of the wheel, its branch opens on the right")
    cx, cy, R = 430, 480, 330
    for i, (aid, name, col, motif) in enumerate(AREAS[1:]):
        a0, a1 = i * 36 - 90 - 17, i * 36 - 90 + 17
        on = aid == "shield"
        d.pieslice((cx - R, cy - R, cx + R, cy + R), a0, a1, fill=hexc(col, 0.45 if on else 0.18), outline=hexc(col, 0.8), width=3)
        a = math.radians(i * 36 - 90)
        x, y = cx + R * 0.68 * math.cos(a), cy + R * 0.68 * math.sin(a)
        icon(img, motif, col, x, y, 4 if on else 3, dim=1 if on else 0.75)
        d.text((x - 8, y + 30), str([11, 0, 0, 2, 0, 4, 0, 0, 0, 0][i]), font=F(15, True), fill=EMBER)
    d.ellipse((cx - 90, cy - 90, cx + 90, cy + 90), fill=(40, 28, 20), outline=EMBER, width=4)
    icon(img, "flame", T.CORE_SPECIAL, cx, cy - 10, 5)
    d.text((cx - 38, cy + 40), "THE CORE", font=F(15, True), fill=TEXT)
    # the opened branch: a clean left-to-right path with notables hanging off it
    frame(d, 820, 80, W - 20, H - 50, cut=14)
    col = "#6a8ab8"
    d.text((850, 100), "THE WALL", font=F(30, True), fill=hexc(col))
    d.text((850, 140), "4 points here   counts while you hold a shield", font=F(15), fill=DIM)
    notes, key = area_nodes("shield")
    path = [(880 + k * 92, 470) for k in range(8)]
    for p1, p2 in zip(path, path[1:]):
        d.line([p1, p2], fill=EMBER if p2[0] < 1150 else (70, 60, 52), width=4)
    stats = [("chest", "Bulwark"), ("pillar", "Stand Firm"), ("shield", "Guard")]
    for k, (x, y) in enumerate(path):
        m, lab = stats[k % 3]
        node(img, d, x, y, "small", m, col, None, x < 1150, 1150 <= x < 1240)
    for k, (nm, m) in enumerate(notes):
        x = 880 + (1 + 2 * k) * 92
        y = 470 + (-150 if k % 2 == 0 else 150)
        d.line([(x, 470), (x, y)], fill=(70, 60, 52), width=3)
        node(img, d, x, y, "notable", split(m)[0], col, split(m)[1], k == 0, k == 1, nm)
    d.line([path[-1], (W - 90, 470)], fill=(70, 60, 52), width=3)
    node(img, d, W - 90, 470, "keystone", split(key[1])[0], col, split(key[1])[1], False, False, key[0])
    caption(d, "4  WHEEL: the overview is a wheel of 10 slices round the Core; the chosen slice's branch opens big on "
               "the right as one clean path with notables hanging off it.")
    img.save(OUT / "tree_mock_4.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    mock_pages()
    mock_stars()
    mock_boards()
    mock_wheel()
    print("wrote", ", ".join(f"tree_mock_{i}.png" for i in range(1, 5)))
