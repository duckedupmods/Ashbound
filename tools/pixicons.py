"""Our item icons as Minecraft-style pixel art: every icon the tools render (weapons and drops 64 px from
weaponforge/vox_mats, armour 64 px from blender/armor_icons.py) brought down to 32x32 - 2x2 blocks taken by their
median tone (no smeared in-between colours), lone pixels dropped, a dozen colours, the shape's own edge darkened into
the outline every vanilla item has. The 64 px renders are kept (tools/renders/icons64, tools/renders/icons) so this
can run again and again; gear.py runs it last.

    python tools/pixicons.py [item...]          (all when none is named)
"""
import colorsys
import os
import shutil
import sys

from PIL import Image

GAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ITEMS = os.path.join(GAME, "src/main/resources/assets/ashbound/textures/item")
KEEP = os.path.join(GAME, "tools/renders/icons64")         # the weapons' and drops' renders, as they came
ARMOUR = os.path.join(GAME, "tools/renders/icons")          # armor_icons.py writes here
SIZE, COLOURS = 32, 12
SIDES = ((1, 0), (-1, 0), (0, 1), (0, -1))


def pixelize(im, size=SIZE, colours=COLOURS):
    im = im.convert("RGBA")
    f = max(1, im.width // size)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    src, dst = im.load(), out.load()
    for y in range(size):
        for x in range(size):
            ps = [src[x * f + i, y * f + j] for i in range(f) for j in range(f)]
            op = sorted((p for p in ps if p[3] > 110), key=lambda p: sum(p[:3]))
            if len(op) * 2 >= len(ps):
                dst[x, y] = op[len(op) // 2][:3] + (255,)

    def inside(x, y):
        return 0 <= x < size and 0 <= y < size and dst[x, y][3]

    for y in range(size):
        for x in range(size):
            if dst[x, y][3] and not any(inside(x + dx, y + dy) for dx, dy in SIDES):
                dst[x, y] = (0, 0, 0, 0)
    # a few colours, a little more contrast and colour than a soft render has
    rgb = Image.new("RGB", (size, size))
    rp = rgb.load()
    for y in range(size):
        for x in range(size):
            if dst[x, y][3]:
                h, l, s = colorsys.rgb_to_hls(*(c / 255 for c in dst[x, y][:3]))
                r, g, b = colorsys.hls_to_rgb(h, min(1, max(0, 0.5 + (l - 0.5) * 1.18)), min(1, s * 1.15))
                rp[x, y] = (int(r * 255), int(g * 255), int(b * 255))
    q = rgb.quantize(colors=colours, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB").load()
    for y in range(size):
        for x in range(size):
            if dst[x, y][3]:
                dst[x, y] = q[x, y] + (255,)
    edge = [(x, y) for y in range(size) for x in range(size) if dst[x, y][3] and not all(inside(x + dx, y + dy) for dx, dy in SIDES)]
    for x, y in edge:
        h, l, s = colorsys.rgb_to_hls(*(c / 255 for c in dst[x, y][:3]))
        r, g, b = colorsys.hls_to_rgb(h, min(l, 0.16) if l > 0.08 else l * 0.6, min(1, s * 1.1))
        dst[x, y] = (int(r * 255), int(g * 255), int(b * 255), 255)
    return out


def source(name):
    """the 64 px render an icon comes from, or None (a hand-drawn one, left alone)"""
    for d in (ARMOUR, KEEP):
        p = os.path.join(d, name + ".png")
        if os.path.exists(p) and Image.open(p).width >= 2 * SIZE:
            return p
    p = os.path.join(ITEMS, name + ".png")
    if Image.open(p).width >= 2 * SIZE:                      # a fresh render: keep it before it's brought down
        os.makedirs(KEEP, exist_ok=True)
        shutil.copyfile(p, os.path.join(KEEP, name + ".png"))
        return os.path.join(KEEP, name + ".png")
    return None


def run(only=()):
    done = 0
    for f in sorted(os.listdir(ITEMS)):
        name = f[:-4]
        if not f.endswith(".png") or name.endswith("_3d") or (only and name not in only):
            continue
        src = source(name)
        if src:
            pixelize(Image.open(src)).save(os.path.join(ITEMS, f))
            done += 1
    print("pixel icons:", done)


if __name__ == "__main__":
    run(set(sys.argv[1:]))
