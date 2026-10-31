"""The skills' icons and the books that teach them.

    python tools/skill_items.py

Writes textures/gui/skill_icons.png (one 16x16 motif from treeicons.py per skill, in Skills.ALL's order) and, for every
skill book and Awakening Tome, a small 3D item model with a painted 32x32 texture: cover and sigil, pages, brass, gem.
"""
import json
import os
import random
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import treeicons

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "main", "resources", "assets", "ashbound")

# Skills.ALL's order
ICONS = [("shield", "e8c050"), ("sword", "f0e0a0"), ("crack", "ff8a40"), ("greatsword", "e03030"), ("drop", "c01828"), ("wind", "8cd8f0"),
         ("wing", "70b8ff"), ("spear", "ffc850"), ("mask", "8a4ce0"), ("dagger", "60d040"), ("target", "d8f0ff"), ("thorns", "a8b850"),
         ("flame", "ff7a2c"), ("spiral", "7a30d0"), ("sun", "ffe080"), ("bolt", "fff0c0"), ("bone", "c8d0a0"), ("skull", "40e0c8"),
         # the later skills, two to a path
         ("shield", "90d8ff"), ("shield", "ff9040"), ("sword", "ffd870"), ("greatsword", "fff4c0"), ("crack", "e8b060"), ("crack", "ff4020"),
         ("target", "e03030"), ("greatsword", "ff6050"), ("drop", "ff4050"), ("flame", "c01828"), ("wind", "c0f0ff"), ("spiral", "70c8f0"),
         ("spear", "70b8ff"), ("wing", "4080ff"), ("thorns", "ffc850"), ("spear", "fff0a0"), ("mask", "b080ff"), ("dagger", "b060ff"),
         ("drop", "60d040"), ("flame", "90f050"), ("wind", "d8f0ff"), ("sun", "a0e0ff"), ("thorns", "d0a050"), ("target", "c8d850"),
         ("flame", "ffb050"), ("sun", "ff5020"), ("spear", "a050f0"), ("spiral", "4a18a0"), ("sun", "a0ffb0"), ("sun", "fff8e0"),
         ("bolt", "ffe080"), ("bolt", "ffffff"), ("bone", "e8f0c0"), ("skull", "c8d0a0"), ("drop", "40e0c8"), ("skull", "ffe080")]
COLUMNS = 6

# id, cover, trim, gem, sigil (10 rows of 12: # trim colour, * gem colour)
SIGILS = {
    "eye": ["............", "....####....", "..##****##..", ".#**#..#**#.", "#***#..#***#", ".#**#..#**#.", "..##****##..", "....####....", "............", "............"],
    "hammer": ["..########..", "..########..", "..##*##*##..", "..########..", ".....##.....", ".....##.....", ".....##.....", ".....##.....", ".....**.....", "............"],
    "drop": [".....##.....", ".....##.....", "....####....", "...##**##...", "..##****##..", "..##****##..", "..##****##..", "...######...", "....####....", "............"],
    "wing": ["#...........", "##..........", "###.........", "####..##....", ".####.###...", "..##########", "...#########", "....**#####.", ".....*****..", "............"],
    "mask": ["...######...", "..########..", ".##..##..##.", ".#.*.##.*.#.", ".##..##..##.", ".##########.", "..###..###..", "...######...", "....#..#....", "............"],
    "antler": ["#.#......#.#", "#.#.#..#.#.#", ".###....###.", "..##.##.##..", "...##..##...", "...##**##...", "....#**#....", "....####....", ".....##.....", "............"],
    "flame": [".....#......", "....##..#...", "...###.##...", "..#####.#...", ".###*#####..", ".##***####..", ".##****###..", "..#****##...", "...####.....", "............"],
    "halo": ["...######...", "..#......#..", "..#......#..", "...######...", ".....**.....", "...******...", ".....**.....", ".....**.....", ".....**.....", "............"],
    "crown": ["#....##....#", "#.#..##..#.#", "##.#.##.#.##", "##.######.##", "############", "##*##**##*##", "############", "............", "............", "............"],
    "plain": ["............", "....####....", "...#....#...", "..#..**..#..", "..#.****.#..", "..#..**..#..", "...#....#...", "....####....", "............", "............"],
}
BOOKS = [("skill_book_1", (92, 66, 44), (150, 120, 84), (190, 180, 160), "plain"), ("skill_book_2", (40, 84, 56), (170, 150, 90), (96, 224, 128), "plain"),
         ("skill_book_3", (34, 58, 112), (214, 176, 90), (90, 170, 255), "plain"), ("skill_book_4", (70, 34, 104), (226, 186, 96), (190, 110, 255), "plain"),
         ("skill_book_5", (120, 62, 12), (255, 214, 110), (255, 190, 60), "plain")]
TOMES = [("tome_drake", (38, 16, 12), (200, 80, 30), (255, 120, 30), "eye"), ("tome_hammerfall", (40, 26, 16), (210, 140, 60), (255, 170, 70), "hammer"),
         ("tome_communion", (46, 8, 12), (170, 30, 40), (240, 40, 50), "drop"), ("tome_tyrant", (18, 30, 56), (170, 200, 240), (110, 190, 255), "wing"),
         ("tome_noone", (20, 14, 30), (120, 90, 170), (170, 100, 255), "mask"), ("tome_stag", (40, 52, 60), (216, 236, 245), (160, 230, 255), "antler"),
         ("tome_offering", (26, 14, 12), (190, 60, 24), (255, 90, 30), "flame"), ("tome_martyr", (64, 54, 40), (250, 214, 120), (255, 240, 180), "halo"),
         ("tome_crown", (22, 10, 40), (150, 80, 220), (200, 120, 255), "crown")]


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c) + (255,)


def paint(cover, trim, gem, sigil):
    """32x32: cover 0-16 square top left, spine under it, pages to the right, brass and gem in the corner"""
    r = random.Random(sum(cover) * 7 + len(sigil))
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    px = img.load()
    for y in range(16):
        for x in range(16):
            edge = min(x, y, 15 - x, 15 - y)
            grain = 0.9 + r.random() * 0.14 + (0.08 if y < 8 else -0.06)
            px[x, y] = shade(trim, 1.05 if x == y or x == 15 - y else 0.95) if edge == 0 else shade(cover, grain * (0.8 if edge == 1 else 1))
    for x in (1, 14):
        for y in (1, 14):
            px[x, y] = shade(trim, 1.2)
    for row, line in enumerate(SIGILS[sigil]):
        for col, ch in enumerate(line):
            if ch == "#":
                px[2 + col, 3 + row] = shade(trim, 1.1 - row * 0.03)
            elif ch == "*":
                px[2 + col, 3 + row] = shade(gem, 1.25 - row * 0.04)
    for x in range(16):   # the spine and edges
        for y in range(16, 22):
            px[x, y] = shade(cover, 0.7 + r.random() * 0.1) if (x + 2) % 5 else shade(trim, 0.9)
    for x in range(16, 32):   # pages, their edges in fine lines
        for y in range(0, 16):
            px[x, y] = (232, 222, 196, 255) if y % 2 else (196, 182, 150, 255)
    for x in range(16, 24):   # brass
        for y in range(16, 24):
            px[x, y] = shade(trim, 0.9 + (24 - y) * 0.05)
    for x in range(24, 32):   # gem
        for y in range(16, 24):
            px[x, y] = shade(gem, 1.45 - (x + y - 40) * 0.05)
    return img


def box(a, b, face_uv, tex="#t"):
    return {"from": a, "to": b, "faces": {f: {"uv": face_uv[f], "texture": tex} for f in face_uv}}


def model(name):
    # uv in 16ths of the 32 pixel sheet
    cover, spine, pages, brass, gem = [0, 0, 8, 8], [0, 8, 8, 11], [8, 0, 16, 8], [8, 8, 12, 12], [12, 8, 16, 12]
    def all_faces(top, side):
        return {"up": top, "down": side, "north": side, "south": side, "west": side, "east": side}
    els = [box([2, 0.5, 2.5], [14, 1.5, 13.5], all_faces(cover, spine)),                      # the back cover
           box([2.6, 1.5, 3], [13.4, 4.5, 13], all_faces(pages, pages)),                      # the block of pages
           box([2, 4.5, 2.5], [14, 5.5, 13.5], all_faces(cover, spine)),                      # the front cover
           box([1.4, 0.5, 2.5], [2.6, 5.5, 13.5], all_faces(spine, spine))]                   # the spine
    for x, z in ((12.4, 2), (12.4, 12.4), (1.2, 2), (1.2, 12.4)):                             # brass corners
        els.append(box([x, 4.2, z], [x + 2.2, 5.9, z + 1.6], all_faces(brass, brass)))
    els.append(box([13.6, 2.2, 7], [14.8, 5.8, 9.4], all_faces(brass, brass)))                # the clasp
    els.append(box([6.9, 5.5, 7.2], [9.1, 6.3, 9.4], all_faces(gem, gem)))                    # the gem
    return {"credit": "tools/skill_items.py", "gui_light": "front", "textures": {"t": "ashbound:item/" + name, "particle": "ashbound:item/" + name}, "elements": els,
            "display": {"gui": {"rotation": [38, -32, 0], "translation": [0, 0.6, 0], "scale": [0.9, 0.9, 0.9]},
                        "ground": {"translation": [0, 2, 0], "scale": [0.45, 0.45, 0.45]},
                        "thirdperson_righthand": {"rotation": [70, 0, 0], "translation": [0, 3, 1], "scale": [0.5, 0.5, 0.5]},
                        "thirdperson_lefthand": {"rotation": [70, 0, 0], "translation": [0, 3, 1], "scale": [0.5, 0.5, 0.5]},
                        "firstperson_righthand": {"rotation": [0, 60, 15], "translation": [1, 2, 1], "scale": [0.5, 0.5, 0.5]},
                        "firstperson_lefthand": {"rotation": [0, 60, 15], "translation": [1, 2, 1], "scale": [0.5, 0.5, 0.5]},
                        "fixed": {"rotation": [90, 0, 0], "scale": [0.8, 0.8, 0.8]}}}


def main():
    rows = (len(ICONS) + COLUMNS - 1) // COLUMNS
    sheet = Image.new("RGBA", (16 * COLUMNS, 16 * rows), (0, 0, 0, 0))
    for i, (motif, colour) in enumerate(ICONS):
        sheet.paste(treeicons.icon(motif, colour), ((i % COLUMNS) * 16, (i // COLUMNS) * 16))
    sheet.save(os.path.join(ROOT, "textures", "gui", "skill_icons.png"))
    for name, cover, trim, gem, sigil in BOOKS + TOMES:
        paint(cover, trim, gem, sigil).save(os.path.join(ROOT, "textures", "item", name + ".png"))
        with open(os.path.join(ROOT, "models", "item", name + ".json"), "w", newline="\n") as f:
            json.dump(model(name), f)
    print("%d icons, %d books" % (len(ICONS), len(BOOKS + TOMES)))


if __name__ == "__main__":
    main()
