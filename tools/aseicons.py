"""Our item icons, made in Aseprite the way Minecraft's own are drawn (Blockbench's Minecraft style guide): 16x16,
the grip in the bottom-left corner and the blade on a clean 45 degree line, a darker outline shaded with the light
(lighter on the top-left, darkest bottom-right), a few hue-shifted tones per colour, light from the top left. Every
icon is its own weapon: shape and colours are read off the item's real model.

Each icon is an Aseprite sprite (tools/icons_ase/<id>.aseprite) with its own layers (body, glow, outline) and its
palette, built by Aseprite and exported by it to the game's PNG. A sprite someone has edited by hand is never drawn
over: the game PNG is exported from that sprite instead.

  1. tools/blender/flat_icons.py renders three flat passes of the model (colour, facing, glow), 112 px square;
  2. the model is laid on the icon's diagonal from the bottom-left corner, as long as its kind is (a dagger short,
     a two-hander corner to corner), its width to the same scale; each icon pixel reads the model under it;
  3. the blade's two edges are evened out along the diagonal so its 45 degree steps run clean;
  4. colours fall into a few families, each a hue-shifted ramp; a pixel's tone = how it faces the light + its own
     paint + its edge (top-left lit, bottom-right shaded);
  5. Aseprite builds the layered sprite and exports the PNG.

    python tools/aseicons.py [gates...] [--sheet] [--write]
        --sheet   tools/renders/aseicons/sheet_<gate>.png: new icons big beside the old, and in a hotbar at GUI scale 3
        --write   puts them in the game (textures/item/<id>.png); without it only the previews are made
"""
import colorsys
import glob
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw

GAME = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ITEMS = os.path.join(GAME, "src/main/resources/assets/ashbound/textures/item")
FLAT = os.path.join(GAME, "tools/renders/flat")
PREVIEW = os.path.join(GAME, "tools/renders/aseicons")
ASE_DIR = os.path.join(GAME, "tools/icons_ase")
MADE = os.path.join(ASE_DIR, "_made.json")          # the sprites as this tool last wrote them: any other is a hand edit
ASEPRITE = "E:/Steam/steamapps/common/Aseprite/Aseprite.exe"
BLENDER = sorted(glob.glob("E:/Steam/steamapps/common/Blender/blender.exe") + glob.glob("E:/Steam/steamapps/common/Blender/*/blender.exe"))[0]
GEAR = json.load(open(os.path.join(GAME, "src/main/resources/ashbound/gear.json"), encoding="utf-8"))
KIND = {w["id"]: w["kind"] for d in GEAR for w in d["weapons"]}

RES, SIZE = 112, 16
COVER = 0.42                          # how much of a pixel's patch the model must fill to be drawn
LIGHT = (-0.45, 0.55, 0.70)          # camera space: from the top left, towards the viewer
STEPS = (-0.25, -0.13, 0.0, 0.12, 0.23)
# how far along the diagonal a kind reaches from the bottom-left corner (x - y: -13 there, 13 at the top-right)
SPAN = {"twohander": 26, "spear": 26, "black": 26, "white": 26, "summon": 26, "sword": 24, "hammer": 24, "dagger": 18}
START = -13                          # the pixel (1, 14), inside the outline


def weapon_batch(gates):
    out = []
    for d in GEAR:
        if gates and d["gate"] not in gates:
            continue
        for w in d["weapons"]:
            k, i = w["kind"], w["id"]
            if k == "shield":
                out.append((i, 18, 10, False, False))
            elif k == "bow":
                out.append((i, 0, 0, True, False))
                out += [("%s_pulling_%d" % (i, n), 0, 0, True, False) for n in range(3)]
            else:
                out.append((i, 0, 0, False, True))
    return out


def flat(batch):
    todo = [b for b in batch if os.path.exists("E:/Ashbound/tools/renders/vox/%s_f0.obj" % b[0])]
    for b in batch:
        if b not in todo:
            print("no model for", b[0])
    spec = os.path.join(FLAT, "batch.json")
    os.makedirs(FLAT, exist_ok=True)
    json.dump(todo, open(spec, "w"))
    subprocess.run([BLENDER, "-b", "-P", os.path.join(GAME, "tools/blender/flat_icons.py"), "--", spec, FLAT],
                   check=True, capture_output=True)
    return [b[0] for b in todo]


# ---------------------------------------------------------------- colour

def lum(c):
    return (0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) / 255


def unsrgb(v):
    """the passes are written through the sRGB curve; the facing wants its linear value back"""
    v /= 255
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def dist(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def families(colours, k=5, merge=34):
    """a few colour families: farthest-point seeds, a few k-means rounds, near ones merged"""
    seeds = [max(colours, key=lambda c: sum(colours[0]) - sum(c))]
    while len(seeds) < min(k, len(set(colours))):
        far = max(colours, key=lambda c: min(dist(c, s) for s in seeds))
        if min(dist(far, s) for s in seeds) < merge:
            break
        seeds.append(far)
    for _ in range(6):
        groups = [[] for _ in seeds]
        for c in colours:
            groups[min(range(len(seeds)), key=lambda i: dist(c, seeds[i]))].append(c)
        seeds = [tuple(sum(c[j] for c in g) / len(g) for j in range(3)) if g else s for g, s in zip(groups, seeds)]
    out = []
    for s in seeds:
        if all(dist(s, o) >= merge for o in out):
            out.append(s)
    return out


def shift_hue(h, to, by):
    d = ((to - h + 0.5) % 1.0) - 0.5
    return (h + max(-by, min(by, d))) % 1.0


def hls(c, h=None, l=None, s=None):
    hh, ll, ss = colorsys.rgb_to_hls(*(x / 255 for x in c))
    r, g, b = colorsys.hls_to_rgb(hh if h is None else h(hh), ll if l is None else l(ll), ss if s is None else s(ss))
    return (round(r * 255), round(g * 255), round(b * 255))


def ramp(c, glow=False):
    """five tones of a colour: shadows cooler and a little richer, lights warmer and paler"""
    h, l, s = colorsys.rgb_to_hls(*(x / 255 for x in c))
    l = min(0.78, max(0.22 if not glow else 0.45, l))
    out = []
    for dl in STEPS:
        if glow:
            dl = dl * 0.6 + 0.08
        hh = shift_hue(h, 0.68, 0.035) if dl < 0 else shift_hue(h, 0.14, 0.03) if dl > 0 else h
        ss = min(1, s * (1.12 if dl < 0 else 0.86 if dl > 0.15 else 1.0) * (1.25 if glow else 1.0))
        r, g, b = colorsys.hls_to_rgb(hh, min(0.95, max(0.05, l + dl)), ss)
        out.append((round(r * 255), round(g * 255), round(b * 255)))
    return out


def dark_outline(c):
    return hls(c, h=lambda h: shift_hue(h, 0.68, 0.04), l=lambda l: min(0.12, l * 0.38), s=lambda s: min(1, s * 0.8))


def lit_outline(c):
    """the outline on the side the light comes from: still well darker than the body, but its own colour"""
    return hls(c, h=lambda h: shift_hue(h, 0.68, 0.03), l=lambda l: max(0.14, min(0.3, l * 0.55)), s=lambda s: min(1, s * 0.95))


# ---------------------------------------------------------------- reading the model

class Passes:
    def __init__(self, name, mirror=True):
        # a melee weapon's passes come out mirrored (the tip top-left): flipped, so the grip sits bottom-left
        self.mirror = mirror
        flip = lambda f, mode: (lambda im: im.transpose(Image.FLIP_LEFT_RIGHT) if mirror else im)(  # noqa: E731
            Image.open(os.path.join(FLAT, name + f)).convert(mode)).load()
        self.alb, self.nrm, self.glw = flip("_alb.png", "RGBA"), flip("_nrm.png", "RGB"), flip("_glw.png", "RGBA")
        self.solid = [(x, y) for y in range(RES) for x in range(RES) if self.alb[x, y][3] > 128]

    def patch(self, cx, cy, r):
        """what the model shows in the square of half-size r round (cx, cy): None when too little of it"""
        ps = [(x, y) for x in range(int(cx - r + 0.5), int(cx + r + 0.5)) for y in range(int(cy - r + 0.5), int(cy + r + 0.5))
              if 0 <= x < RES and 0 <= y < RES]
        if not ps:
            return None
        op = [p for p in ps if self.alb[p][3] > 128]
        if len(op) < max(1, len(ps) * COVER):
            return None
        col = sorted((self.alb[p][:3] for p in op), key=lum)[len(op) // 2]
        n = [sum(unsrgb(self.nrm[p][j]) for p in op) / len(op) * 2 - 1 for j in range(3)]
        n[2] = -n[2]          # Blender's camera space looks down -z: facing us is -z there
        if self.mirror:
            n[0] = -n[0]
        glow = sum(1 for p in op if self.glw[p][0] > 128) * 2 > len(op)
        return dict(c=col, n=n, glow=glow)


def diagonal(name, kind):
    """a melee weapon on Minecraft's diagonal: grip at the bottom-left, its length the kind's, width to scale"""
    m = Passes(name)
    if not m.solid:
        return {}
    S = sorted(x - y for x, y in m.solid)
    P = sorted(x + y for x, y in m.solid)
    s0, s1, p0 = S[0], S[-1], P[len(P) // 2]
    span = SPAN.get(kind, 24)
    f = (s1 - s0) / span                      # render pixels to one icon pixel
    grid = {}
    for y in range(1, SIZE - 1):
        for x in range(1, SIZE - 1):
            s, p = x - y, x + y
            rs, rp = s0 + (s - START) * f, p0 + (p - 15) * f
            got = m.patch((rs + rp) / 2 + 0.5, (rp - rs) / 2 + 0.5, f / 2)
            if got:
                grid[x, y] = got
    return even_edges(grid)


def even_edges(grid):
    """along the diagonal, a lone one-pixel bump or notch in the blade's edge goes: its steps run clean"""
    rows = {}
    for (x, y) in grid:
        rows.setdefault((x - y - START) // 2, set()).add(x + y - 15)
    lo, hi = {}, {}
    for i, ks in rows.items():
        k0 = min(ks, key=abs)
        a = b = k0
        while a - 1 in ks:
            a -= 1
        while b + 1 in ks:
            b += 1
        lo[i], hi[i] = a, b
    def pixel(i, k):
        # the pixel on layer k at step i (x - y has the parity of 15 + k)
        s = START + 2 * i + ((15 + k - START) % 2)
        p = 15 + k
        return ((s + p) // 2, (p - s) // 2)
    for edge, sign in ((lo, -1), (hi, 1)):
        for i in sorted(edge):
            if i - 1 in edge and i + 1 in edge and edge[i - 1] == edge[i + 1] and abs(edge[i] - edge[i - 1]) == 1:
                want = edge[i - 1]
                if (want - edge[i]) * sign > 0:          # a notch: fill it from the pixel inside
                    src = grid.get(pixel(i, edge[i]))
                    at = pixel(i, want)
                    if src and 1 <= at[0] < SIZE - 1 and 1 <= at[1] < SIZE - 1:
                        grid[at] = dict(src)
                else:                                    # a bump: shave it
                    grid.pop(pixel(i, edge[i]), None)
                edge[i] = want
    return grid


def framed(name):
    """a shield or a bow as it's framed: the 112 px render read 14 x 14, inside the outline"""
    m = Passes(name, mirror=False)
    grid = {}
    for y in range(14):
        for x in range(14):
            got = m.patch(x * 8 + 4, y * 8 + 4, 4)
            if got:
                grid[x + 1, y + 1] = got
    for (x, y) in list(grid):
        if not any((x + dx, y + dy) in grid for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy):
            del grid[x, y]
    return grid


# ---------------------------------------------------------------- painting

def paint(grid):
    """the layers: body and glow pixels, and the outline round them, shaded with the light"""
    layers = {"body": {}, "glow": {}, "outline": {}}
    if not grid:
        return layers
    fams = families([g["c"] for g in grid.values()])
    ramps = [ramp(f) for f in fams]
    glows = [ramp(f, True) for f in fams]
    ln = sum(v * v for v in LIGHT) ** 0.5
    L = [v / ln for v in LIGHT]
    fam_of = {}
    for (x, y), g in grid.items():
        fi = min(range(len(fams)), key=lambda i: dist(g["c"], fams[i]))
        fam_of[x, y] = fi
        facing = sum(a * b for a, b in zip(g["n"], L))
        own = (lum(g["c"]) - lum(fams[fi])) / 0.12
        v = (facing - 0.72) * 3.2 + own * 0.6
        lit = (x - 1, y) not in grid or (x, y - 1) not in grid
        dark = (x + 1, y) not in grid or (x, y + 1) not in grid
        if lit and not dark:
            v += 0.9
        elif dark and not lit:
            v -= 0.9
        t = max(0, min(4, round(2 + v)))
        if g["glow"]:
            layers["glow"][x, y] = glows[fi][max(2, t)]
        else:
            layers["body"][x, y] = ramps[fi][t]
    for y in range(SIZE):
        for x in range(SIZE):
            if (x, y) in grid:
                continue
            after = [fam_of[q] for q in ((x + 1, y), (x, y + 1)) if q in fam_of]      # the shape lies right/below: lit side
            before = [fam_of[q] for q in ((x - 1, y), (x, y - 1)) if q in fam_of]
            if before:
                layers["outline"][x, y] = dark_outline(min((fams[f] for f in before), key=lum))
            elif after:
                layers["outline"][x, y] = lit_outline(min((fams[f] for f in after), key=lum))
    return layers


# ---------------------------------------------------------------- Aseprite

LUA = r'''
local items = json.decode(io.open(app.params["spec"]):read("a"))
for _, it in ipairs(items) do
  local spr = Sprite(16, 16, ColorMode.RGB)
  local pal = Palette(#it.palette + 1)
  pal:setColor(0, Color{ r = 0, g = 0, b = 0, a = 0 })
  for i, c in ipairs(it.palette) do pal:setColor(i, Color{ r = c[1], g = c[2], b = c[3], a = 255 }) end
  spr:setPalette(pal)
  local first = true
  for _, L in ipairs(it.layers) do
    local layer
    if first then layer = spr.layers[1]; first = false else layer = spr:newLayer() end
    layer.name = L.name
    local img = Image(16, 16, ColorMode.RGB)
    for _, p in ipairs(L.px) do
      img:drawPixel(p[1], p[2], app.pixelColor.rgba(p[3], p[4], p[5], 255))
    end
    spr:newCel(layer, 1, img, Point(0, 0))
  end
  spr:saveAs(it.ase)
  spr:saveCopyAs(it.png)
  spr:close()
end
local list = io.open(app.params["export"]):read("a")
for line in list:gmatch("[^\n]+") do
  local src, dst = line:match("([^|]+)|([^|]+)")
  local spr = app.open(src)
  if spr then spr:saveCopyAs(dst); spr:close() end
end
'''


def aseprite(drawn, exports):
    """Aseprite builds each drawn sprite (layers, palette) and exports it; hand-edited sprites are only exported"""
    spec = []
    for name, layers, png in drawn:
        pal = sorted({c for L in layers.values() for c in L.values()}, key=lum)
        spec.append({"ase": os.path.join(ASE_DIR, name + ".aseprite"), "png": png, "palette": [list(c) for c in pal],
                     "layers": [{"name": ln, "px": [[x, y, *c] for (x, y), c in layers[ln].items()]}
                                for ln in ("body", "glow", "outline") if layers[ln]]})
    os.makedirs(ASE_DIR, exist_ok=True)
    sp, ex, lua = (os.path.join(FLAT, n) for n in ("ase_spec.json", "ase_export.txt", "ase_build.lua"))
    json.dump(spec, open(sp, "w"))
    open(ex, "w").write("".join("%s|%s\n" % e for e in exports) or "\n")
    open(lua, "w").write(LUA)
    r = subprocess.run([ASEPRITE, "-b", "--script-param", "spec=" + sp, "--script-param", "export=" + ex, "--script", lua],
                       capture_output=True, text=True)
    if r.returncode or r.stderr.strip() or r.stdout.strip():
        print("aseprite:", r.returncode, r.stdout[-800:], r.stderr[-800:])


def hand_edited(name, made):
    p = os.path.join(ASE_DIR, name + ".aseprite")
    return os.path.exists(p) and name in made and abs(os.path.getmtime(p) - made[name]) > 1


def sheet(title, names):
    cols = 8
    rows = (len(names) + cols - 1) // cols
    tile = 136
    bar = 3 * 20
    out = Image.new("RGBA", (cols * tile * 2, rows * tile + 40 + bar * ((len(names) + 8) // 9) + 10), (30, 28, 30, 255))
    d = ImageDraw.Draw(out)
    d.text((8, 12), title + "   (left: new 16 px, right: old)", fill=(220, 210, 200, 255))
    for k, n in enumerate(names):
        x, y = (k % cols) * tile * 2, 40 + (k // cols) * tile
        new = Image.open(os.path.join(PREVIEW, n + ".png")).convert("RGBA").resize((128, 128), Image.NEAREST)
        out.paste(new, (x + 4, y), new)
        old = os.path.join(ITEMS, n + ".png")
        if os.path.exists(old):
            o = Image.open(old).convert("RGBA").resize((128, 128), Image.NEAREST)
            out.paste(o, (x + tile + 4, y), o)
    y0 = 40 + rows * tile + 6
    for k, n in enumerate(names):
        x, y = 8 + (k % 9) * bar, y0 + (k // 9) * bar
        d.rectangle([x, y, x + bar - 2, y + bar - 2], fill=(139, 139, 139, 255), outline=(55, 55, 55, 255), width=3)
        new = Image.open(os.path.join(PREVIEW, n + ".png")).convert("RGBA").resize((48, 48), Image.NEAREST)
        out.paste(new, (x + 5, y + 5), new)
    path = os.path.join(PREVIEW, "sheet_%s.png" % title)
    out.save(path)
    return path


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    gates = {d["gate"] for d in GEAR}
    want = [a for a in args if a in gates]
    names = flat(weapon_batch(want))
    os.makedirs(PREVIEW, exist_ok=True)
    made = json.load(open(MADE)) if os.path.exists(MADE) else {}
    drawn, exports = [], []
    for n in names:
        png = os.path.join(PREVIEW, n + ".png")
        if hand_edited(n, made):
            exports.append((os.path.join(ASE_DIR, n + ".aseprite"), png))
            continue
        kind = KIND.get(n.split("_pulling_")[0], "bow")
        grid = framed(n) if kind in ("shield", "bow") else diagonal(n, kind)
        drawn.append((n, paint(grid), png))
    aseprite(drawn, exports)
    for n, _l, _p in drawn:
        p = os.path.join(ASE_DIR, n + ".aseprite")
        if os.path.exists(p):
            made[n] = os.path.getmtime(p)
    json.dump(made, open(MADE, "w"), indent=0)
    if "--write" in sys.argv:
        for n in names:
            Image.open(os.path.join(PREVIEW, n + ".png")).save(os.path.join(ITEMS, n + ".png"))
    if "--sheet" in sys.argv:
        for g in (want or sorted(gates)):
            ids = [w["id"] for d in GEAR if d["gate"] == g for w in d["weapons"] if w["id"] in names]
            print(sheet(g, ids))
    print("icons:", len(names), "| drawn:", len(drawn), "| hand-edited, kept:", len(exports))


if __name__ == "__main__":
    main()
