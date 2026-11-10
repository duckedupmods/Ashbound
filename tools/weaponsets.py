"""Every weapon by hand, the way armorsets.py does armour: no type templates, each one its own silhouette.

A shape is a Mask, a grid of half pixels (one texel each) filled from polygons, so a blade can hook back on itself,
have holes cut in it, grow fingers. forge() stacks a mask in steps: a thin bright edge, a thicker body split into two
facets along its ridge, so a blade has a real cross-section instead of being a flat box. Same space as weaponforge:
px, the hand at the origin, the blade up +y, its faces in the x-y plane.

    python tools/weaponsets.py [ids or gates...] [--look]     meshes, textures, item models, slot pose
        --look   tools/renders/weapon_new/<first id>.png, each weapon upright and as the slot shows it (Blender)

Designs live in weaponsets_a.py on, each a function under @design("id"). The first colour of a ramp is its darkest.
"""
import importlib
import json
import math
import os
import subprocess
import sys

sys.path.insert(0, 'E:/Ashbound/tools')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voxsword as V  # noqa: E402
from voxsword import Sword, C, h3, ramp  # noqa: E402

GRID = 2                 # cells per px; one cell is one texel
DESIGNS = {}


def design(iid, **kw):
    def wrap(fn):
        DESIGNS[iid] = fn
        return fn
    return wrap


# ================================================================== curves

def qb(a, c, b, n=8):
    """a quadratic curve a..b pulled toward c, without its end b, so curves chain"""
    return [((1 - t) ** 2 * a[0] + 2 * t * (1 - t) * c[0] + t * t * b[0],
             (1 - t) ** 2 * a[1] + 2 * t * (1 - t) * c[1] + t * t * b[1]) for t in (k / n for k in range(n))]


def path(*parts):
    """points and qb lists run together into one polygon"""
    out = []
    for p in parts:
        if isinstance(p, list):
            out += p
        else:
            out.append(p)
    return out


def line(pts, w):
    """a polygon for a stroke of width w along pts (hands-off cracks, veins, inlays)"""
    left, right = [], []
    for k, p in enumerate(pts):
        a, b = pts[max(0, k - 1)], pts[min(len(pts) - 1, k + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln * w / 2, dx / ln * w / 2
        left.append((p[0] + nx, p[1] + ny))
        right.append((p[0] - nx, p[1] - ny))
    return left + right[::-1]


# ================================================================== masks

class Mask:
    """half-pixel cells, kept as a set of (ix, iy): a cell's corner is (ix/GRID, iy/GRID)"""

    def __init__(self, cells=None):
        self.c = set(cells or ())

    def poly(self, pts):
        """even-odd fill: a cell is in when its centre is"""
        ys = [p[1] for p in pts]
        for iy in range(int(math.floor(min(ys) * GRID)), int(math.ceil(max(ys) * GRID)) + 1):
            y = (iy + 0.5) / GRID
            xs = []
            for k in range(len(pts)):
                a, b = pts[k], pts[(k + 1) % len(pts)]
                if (a[1] <= y) != (b[1] <= y):
                    xs.append(a[0] + (y - a[1]) / (b[1] - a[1]) * (b[0] - a[0]))
            xs.sort()
            for l, r in zip(xs[::2], xs[1::2]):
                for ix in range(int(math.ceil(l * GRID - 0.5)), int(math.ceil(r * GRID - 0.5))):
                    self.c.add((ix, iy))
        return self

    def __add__(self, o):
        return Mask(self.c | o.c)

    def __sub__(self, o):
        return Mask(self.c - o.c)

    def __and__(self, o):
        return Mask(self.c & o.c)

    def inset(self, px):
        """eat px in from every edge"""
        c = self.c
        for _ in range(int(round(px * GRID))):
            c = {p for p in c if all((p[0] + a, p[1] + b) in c for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
        return Mask(c)

    def rows(self):
        """the fewest stacks of identical runs: [(ix0, ix1, iy0, iy1, whole-row xl, xr)]"""
        by = {}
        for ix, iy in self.c:
            by.setdefault(iy, []).append(ix)
        rects, open_ = [], {}
        for iy in sorted(by):
            xs = sorted(by[iy])
            runs, a = [], xs[0]
            for p, q in zip(xs, xs[1:] + [None]):
                if q != p + 1:
                    runs.append((a, p + 1))
                    a = q
            next_open = {}
            for run in runs:
                if run in open_ and open_[run][3] == iy:
                    r = open_[run]
                    r[3] = iy + 1
                    next_open[run] = r
                else:
                    r = [run[0], run[1], iy, iy + 1]
                    rects.append(r)
                    next_open[run] = r
            open_ = next_open
        return rects


def P(*pts):
    return Mask().poly(path(*pts))


def L(pts, w):
    return Mask().poly(line(pts, w))


def disc(cx, cy, r, n=20):
    return Mask().poly([(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)])


def ring(cx, cy, r, hole):
    return disc(cx, cy, r) - disc(cx, cy, hole)


def rect(x0, y0, x1, y1):
    return P((x0, y0), (x1, y0), (x1, y1), (x0, y1))


def wave(cx, hw, y0, y1, n=28):
    """a shape up a wandering centre line: cx(t), half width hw(t), t 0..1 from y0 to y1"""
    ts = [j / n for j in range(n + 1)]
    return P([(cx(t) - hw(t), y0 + t * (y1 - y0)) for t in ts] + [(cx(t) + hw(t), y0 + t * (y1 - y0)) for t in ts[::-1]])


def taper(w0, w1, y0, y1, tip, cx=0.0):
    """a plain straight blade: half width w0 to w1, then the point"""
    return P((cx - w0, y0), (cx + w0, y0), (cx + w1, y1), (cx, tip), (cx - w1, y1))


# ================================================================== paint: flat colour bands, never dither

def at(R, v):
    return R[max(0, min(len(R) - 1, int(v * len(R))))]


def facet_of(p, b):
    """-1..1 across the run this box belongs to"""
    span = getattr(b, "span", None)
    if not span or span[1] <= span[0]:
        return 0.0
    return 2 * (p[0] - span[0]) / (span[1] - span[0]) - 1


def lit(key, i, j, w, h):
    """the same top light on every material: faces plain, top and left bright, under and right dark"""
    return {"n": 0.0, "s": -0.04, "u": 0.2, "d": -0.26, "e": -0.1, "w": 0.1}[key]


def steel(R, base=0.5, ridge=0.14, sheen=0.1, scars=0.0):
    """a forged face: two facets meeting at the ridge, long diagonal glints, a few honing scratches"""
    def sh(p, n, b, key, i, j, w, h, fr):
        x, y, z = p
        v = base + lit(key, i, j, w, h)
        if key in "ns":
            f = facet_of(p, b)
            r = getattr(b, "ridge", 0.0)
            v += ridge if f < r else -ridge
            v += sheen * math.sin((y + x * 1.6) * 0.42)
            if scars and h3(int(y * 2), int(x * 2), 7) < scars:
                v -= 0.2
        return at(R, v)
    return sh


def honed(R, base=0.74):
    """the bright edge: pale on the face, paler at the very top"""
    def sh(p, n, b, key, i, j, w, h, fr):
        return at(R, base + lit(key, i, j, w, h) + 0.05 * math.sin(p[1] * 0.5))
    return sh


def flat(R, base=0.5, grain=0.0, bevel=0.1):
    """a plain worked part: lit, edges caught"""
    def sh(p, n, b, key, i, j, w, h, fr):
        v = base + lit(key, i, j, w, h)
        if i == 0 or j == 0:
            v += bevel
        if i == w - 1 or j == h - 1:
            v -= bevel
        if grain:
            v += grain * (h3(int(p[0] * 2), int(p[1] * 0.5), int(p[2] * 2)) - 0.5)
        return at(R, v)
    return sh


def bone(R, base=0.62):
    """bone: long straight grain, pits, a darker root"""
    def sh(p, n, b, key, i, j, w, h, fr):
        x, y, z = p
        v = base + lit(key, i, j, w, h) + 0.08 * math.sin(facet_of(p, b) * 4.0 + y * 0.12)
        if key in "ns":
            v += 0.12 * (1 if facet_of(p, b) < -0.1 else -0.6)
            if h3(int(y * 0.7), int(x * 2), 3) < 0.05:
                v -= 0.25
        return at(R, v)
    return sh


def staves(R, width=2.0, base=0.5):
    """wood as straight staves running up it, a dark line between"""
    def sh(p, n, b, key, i, j, w, h, fr):
        x, y, z = p
        k = math.floor(x / width)
        v = base + lit(key, i, j, w, h) + 0.14 * (h3(k, 3, 9) - 0.5)
        if (x / width - k) < 0.2:
            v -= 0.22
        return at(R, v)
    return sh


def wrap(R, band=None, turn=6):
    """leather or cord wound round in diagonal turns"""
    def sh(p, n, b, key, i, j, w, h, fr):
        if key in "ud":
            return R[1]
        around = (p[0] if key in "ns" else p[2]) * 2
        k = (int(p[1] * 2) + int(around)) % turn
        if k == 0:
            return band or R[0]
        return at(R, 0.82 - k * 0.1 + (0.06 if key in "wn" else -0.08))
    return sh


def heat(R, y0, y1, base=0.0, span=1.0):
    """colour by height: y0 the ramp's bottom, y1 its top (a blade heating toward its tip, a stain rising)"""
    def sh(p, n, b, key, i, j, w, h, fr):
        t = (p[1] - y0) / (y1 - y0)
        return at(R, base + span * t + lit(key, i, j, w, h) * 0.3)
    return sh


def fire(R, base=0.55, span=0.4):
    """a glowing part, white hot down its middle"""
    def sh(p, n, b, key, i, j, w, h, fr):
        return at(R, base + span * (1 - abs(facet_of(p, b))) + 0.08 * math.sin(p[1] * 1.3))
    return sh


def gem(R):
    """a cut stone: facets by quadrant, one hard glint"""
    def sh(p, n, b, key, i, j, w, h, fr):
        u, t = (i + 0.5) / w, (j + 0.5) / h
        v = 0.3 + 0.4 * (1 - t) + (0.15 if u < 0.5 else -0.1)
        if u < 0.34 and t < 0.34:
            v = 1.0
        return at(R, v)
    return sh


def stripes(A, B_, every=4.0, lean=1.0, base=0.55):
    """two painted bands chasing round a part"""
    def sh(p, n, b, key, i, j, w, h, fr):
        v = base + lit(key, i, j, w, h) + (0.12 if facet_of(p, b) < 0 else -0.08)
        k = int(math.floor((p[1] + p[0] * lean) / every))
        return at(A if k % 2 else B_, v)
    return sh


# ================================================================== the kit

class Kit:
    def __init__(self, iid, **shaders):
        self.s = Sword(iid)
        self.s.shaders = dict(shaders)
        self.pull, self.arrow = 0.0, False       # a bow's draw

    def mat(self, **shaders):
        self.s.shaders.update(shaders)

    def plate(self, m, depth, mat, z=0.0, glow=False, ridge=0.0, tag="plate"):
        """a mask stood up to depth round plane z"""
        cells = m.c
        for r in m.rows():
            x0, x1, y0, y1 = r[0] / GRID, r[1] / GRID, r[2] / GRID, r[3] / GRID
            skip = []
            if all((ix, r[3]) in cells for ix in range(r[0], r[1])):
                skip.append("u")
            if all((ix, r[2] - 1) in cells for ix in range(r[0], r[1])):
                skip.append("d")
            kw = {"group": "fire"} if glow else {}
            b = self.s.add(((x0, y0, z - depth / 2), (x1 - x0, y1 - y0, depth)), mat, skip=tuple(skip), tag=tag, **kw)
            b.span, b.ridge = (x0, x1), ridge
        return self

    def forge(self, m, thick=1.8, edge=0.5, body="blade", rim="edge", step=2, ridge=0.0, z=0.0):
        """a blade in steps: the whole shape thin and bright, the body inside it thicker and two-faceted.
        step = how many px of edge before the body starts, in half pixels"""
        self.plate(m, edge * 2 if thick < 1.2 else thick * 0.5, rim, z, tag="edge")
        self.plate(m.inset(step / GRID), thick, body, z, ridge=ridge, tag="blade")
        return self

    def inlay(self, m, thick, mat, z=0.0, glow=False, proud=0.06):
        """laid on both faces, a hair proud"""
        return self.plate(m, thick + proud, mat, z, glow=glow, tag="inlay")

    def box(self, cx, y0, cz, sx, sy, sz, mat, glow=False, rots=(), pivot=None, tag=None):
        kw = {"group": "fire"} if glow else {}
        if rots:
            kw["rots"] = rots
            kw["pivot"] = pivot if pivot is not None else (cx, y0, cz)
        return self.s.add(C(cx, y0, cz, sx, sy, sz), mat, tag=tag, **kw)

    def grip(self, y0, y1, w=2.0, mat="wrap"):
        return self.box(0, y0, 0, w, y1 - y0, w, mat, tag="grip")

    def seg(self, a, b, w, d, mat, z=0.0, glow=False):
        """a box from point a to b"""
        dx, dy = b[0] - a[0], b[1] - a[1]
        kw = {"group": "fire"} if glow else {}
        self.s.add(((a[0] - w / 2, a[1], z - d / 2), (w, math.hypot(dx, dy) + 0.05, d)), mat, rots=(("z", math.degrees(math.atan2(-dx, dy))),), pivot=(a[0], a[1], z), **kw)

    def theme(self, gate, base=0.5, ridge=0.13, scars=0.02, edge=0.78):
        """a gate's colours as the usual materials; returns its ramps for anything custom"""
        import weaponforge as W
        R = W.THEMES[gate].R
        self.mat(blade=steel(R["blade"], base, ridge, scars=scars), edge=honed(R["blade"], edge), dark=flat(R["dark"], 0.55),
                 wrap=wrap(R["wrap"], R["dark"][1]), wood=staves(R["wood"]), glow=fire(R["glow"], 0.35, 0.6), acc=flat(R["acc"], 0.55))
        return R


# ================================================================== the fire moving

FRAMES = 8               # a weapon with fire parts gets this many frames, its glow rolling up them like the armour's


def rolling(sh):
    """the fire's brightness running up the part frame by frame; everything else painted once"""
    once = {}

    def out(p, n, b, key, i, j, w, h, fr):
        if b.group != "fire":
            k = (id(b), key, i, j)
            if k not in once:
                once[k] = sh(p, n, b, key, i, j, w, h, 0)
            return once[k]
        c = sh(p, n, b, key, i, j, w, h, fr)
        if c is None:
            return c
        t = math.sin(2 * math.pi * (fr / FRAMES - p[1] / 12 + p[0] / 23))
        rgb = c[:3]
        if t > 0:
            rgb = [v + (hot - v) * 0.4 * t for v, hot in zip(rgb, (255, 246, 214))]
        else:
            rgb = [v * (1 + 0.32 * t) for v in rgb]
        return tuple(int(round(v)) for v in rgb) + tuple(c[3:])
    return out


def export(s, nm, *a):
    """weaponforge's export, the fire animated: frames stacked in the sheet plus the .mcmeta that plays them"""
    import weaponforge as W
    from PIL import Image
    s.frames = FRAMES if any(b.group == "fire" for b in s.boxes) else 1
    if s.frames > 1:
        s.shaders = {m: rolling(sh) for m, sh in s.shaders.items()}
    W.export(s, nm, *a, force=True)
    meta = W.ASSETS + "textures/item/%s_3d.png.mcmeta" % nm
    if s.frames > 1:
        w, h = Image.open(W.ASSETS + "textures/item/%s_3d.png" % nm).size
        with open(meta, "w", encoding="utf-8") as f:
            json.dump({"animation": {"frametime": 3, "interpolate": True, "width": w, "height": h // s.frames}}, f)
        f0 = W.VOX + "%s_f0.png" % nm           # the renders read one frame
        Image.open(f0).crop((0, 0, w, h // s.frames)).save(f0)
    elif os.path.exists(meta):
        os.remove(meta)


# ================================================================== building

def catalogue():
    """id -> (gate, item) from the gear table and the world's arms"""
    import gear as G
    out = {}
    for g in json.load(open(G.OUT, encoding="utf-8")):
        for it in g["weapons"]:
            out[it["id"]] = (g["gate"], it)
    for s_ in ("black", "white", "summon"):
        out["apprentice_%s_staff" % s_] = ("apprentice", {"id": "apprentice_%s_staff" % s_, "kind": s_})
    for gate, f in (("world", "world_arms.json"), ("joined", "joined.json")):
        arms = json.load(open(os.path.join(G.GAME, "src/main/resources/ashbound", f), encoding="utf-8"))
        for it in arms if isinstance(arms, list) else arms.get("weapons", arms.get("arms", [])):
            if "id" in it and "kind" in it:
                out.setdefault(it["id"], (gate, it))
    return out


def load_designs():
    here = os.path.dirname(os.path.abspath(__file__))
    for f in sorted(os.listdir(here)):
        if f.startswith("weaponsets_") and f.endswith(".py"):
            importlib.import_module(f[:-3])


def make(iid, cat):
    import gui3d
    import weaponforge as W
    gate, it = cat[iid]
    k = Kit(iid)
    DESIGNS[iid](k)
    kind = it["kind"]
    p = os.path.join(gui3d.A, "models/item/%s.json" % iid)
    flat_ = lambda q: (q[0] / 16, q[1] / 16, q[2] / 16)  # noqa: E731   shields and bows sit in vanilla item space
    if kind == "shield":
        export(k.s, iid, flat_)
        def pose_of(path_):      # the hand pose stays what it was
            return {n: v for n, v in json.load(open(path_, encoding="utf-8"))["base"]["display"].items() if "person" in n}
        block = os.path.join(gui3d.A, "models/item/%s_blocking.json" % iid)
        W.model(iid + "_blocking", iid, pose_of(block), iid)
        W.model(iid, iid, pose_of(p), iid, [{"predicate": {"minecraft:blocking": 1}, "model": "ashbound:item/%s_blocking" % iid}])
    elif kind == "bow":
        def pose_of(path_):
            return {n: v for n, v in json.load(open(path_, encoding="utf-8"))["base"]["display"].items() if "person" in n}
        export(k.s, iid, flat_)
        overrides, hand = [], pose_of(p)
        for n, (pull, at_pull) in enumerate(((0.35, None), (0.7, 0.65), (1.0, 0.9))):
            nm = "%s_pulling_%d" % (iid, n)
            kk = Kit(nm)
            kk.pull, kk.arrow = pull, True
            DESIGNS[iid](kk)
            export(kk.s, nm, flat_)
            W.model(nm, nm, hand, nm)
            pred = {"minecraft:pulling": 1}
            if at_pull:
                pred["minecraft:pull"] = at_pull
            overrides.append({"predicate": pred, "model": "ashbound:item/" + nm})
        W.model(iid, iid, hand, iid, overrides)
    else:
        export(k.s, iid)
        held = None              # the hand pose stays what it was
        if os.path.exists(p):
            held = {n: v for n, v in json.load(open(p, encoding="utf-8")).get("base", {}).get("display", {}).items() if "person" in n}
        W.model(iid, iid, held or (W.DISPLAY_2H if kind == "twohander" else W.DISPLAY_1H), iid)
    m = json.load(open(p, encoding="utf-8"))
    r = gui3d.pose(iid, kind)
    sc, t = gui3d.fit(iid, r)
    rot = gui3d.euler_xyz(r)
    disp = m["base"].setdefault("display", {})
    disp["gui"] = {"rotation": rot, "translation": t, "scale": [round(sc, 4)] * 3}
    disp["fixed"] = {"rotation": rot, "translation": t, "scale": [round(sc, 4)] * 3}
    disp["ground"] = {"rotation": rot, "translation": [round(v * 0.55, 3) for v in t[:2]] + [0], "scale": [round(sc * 0.55, 4)] * 3}
    for n in ("gui", "ground", "fixed"):
        m.get("perspectives", {}).pop(n, None)
    m.setdefault("perspectives", {})
    m["gui_light"] = "side"
    json.dump(m, open(p, "w", encoding="utf-8"), indent=1)
    if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons_hand", iid + ".png")):
        import weaponicons
        weaponicons.in_game(iid)
    return {"id": iid, "kind": kind, "r": r, "s": sc, "t": t, "boxes": len(k.s.boxes)}


def main():
    import gui3d
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    load_designs()
    cat = catalogue()
    todo = [i for i in DESIGNS if not args or i in args or (i in cat and cat[i][0] in args)]
    done = []
    for iid in todo:
        d = make(iid, cat)
        done.append(d)
        print("made", iid, d["boxes"], "boxes")
    if "--look" in sys.argv and done:
        out = os.path.join(gui3d.GAME, "tools/renders/weapon_new")
        os.makedirs(out, exist_ok=True)
        spec = os.path.join(out, "batch.json")
        json.dump({"assets": gui3d.A, "out": out, "items": done, "name": done[0]["id"]}, open(spec, "w"))
        r = subprocess.run([gui3d.BLENDER, "-b", "-P", os.path.join(gui3d.GAME, "tools/blender/weapon_look.py"), "--", spec],
                           capture_output=True, text=True)
        print([l for l in r.stdout.splitlines() if l.startswith("sheet")] or r.stderr[-1500:] or r.stdout[-1500:])


if __name__ == "__main__":
    sys.modules.setdefault("weaponsets", sys.modules[__name__])
    main()
