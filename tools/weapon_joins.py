"""Are a weapon's parts joined? Reads the exported meshes, splits each into its solid pieces and groups the ones that
touch: a blade hanging off the guard or a gem in the air stands alone. Every piece is a box (convex), so two touch
unless some axis separates them. weld() slides each loose group onto the rest, keeping the design; weaponforge.export
runs it on everything it writes.

    python tools/weapon_joins.py [ids...] [--all] [--fix] [--gap 0.1] [--json out.json]

Without ids it checks the world arms (the loot pool); --all checks every weapon. --fix welds what it finds. Gaps in px
(1/16 block).
"""
import glob
import json
import math
import os
import re
import sys

GAME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(GAME, "src/main/resources/assets/ashbound/models/mesh/")
PX = 1 / 16
TOUCH = 0.1 * PX
SINK = 0.3 * PX  # how far a welded part goes into what it joins


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


class Piece:
    def __init__(self, ids, pts, axes):
        self.ids, self.pts, self.axes = ids, pts, axes
        self.bound()

    def bound(self):
        self.lo = [min(p[i] for p in self.pts) for i in range(3)]
        self.hi = [max(p[i] for p in self.pts) for i in range(3)]

    def move(self, v):
        self.pts = [(p[0] + v[0], p[1] + v[1], p[2] + v[2]) for p in self.pts]
        self.bound()

    def size(self):
        return (self.hi[0] - self.lo[0] + 1e-4) * (self.hi[1] - self.lo[1] + 1e-4) * (self.hi[2] - self.lo[2] + 1e-4)


def read(path):
    """(lines, positions, line number of each position, faces)"""
    lines = open(path, encoding="utf-8").read().split("\n")
    vs, at, faces = [], [], []
    for n, ln in enumerate(lines):
        if ln.startswith("v "):
            vs.append(tuple(float(x) for x in ln.split()[1:4]))
            at.append(n)
        elif ln.startswith("f "):
            faces.append([int(t.split("/")[0]) - 1 for t in ln.split()[1:]])
    return lines, vs, at, faces


def pieces(vs, faces):
    parent = list(range(len(vs)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for f in faces:
        r = find(f[0])
        for i in f[1:]:
            parent[find(i)] = r
    ids, sides = {}, {}
    for i in range(len(vs)):
        ids.setdefault(find(i), []).append(i)
    for f in faces:
        for a, b in zip(f, f[1:] + f[:1]):
            d = tuple(vs[b][i] - vs[a][i] for i in range(3))
            n = math.sqrt(dot(d, d))
            if n > 1e-5:
                u = tuple(c / n for c in d)
                ax = sides.setdefault(find(a), [])
                if not any(abs(dot(u, o)) > 0.999 for o in ax):
                    ax.append(u)
    return [Piece(i, [vs[k] for k in i], sides.get(r, [])[:6]) for r, i in ids.items() if r in sides]


def apart(a, b):
    """(gap, the unit way from a to b): the widest separation over the two boxes' axes, gap <= 0 when they touch"""
    axes = list(a.axes) + list(b.axes)
    for u in a.axes[:3]:
        for v in b.axes[:3]:
            c = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
            n = math.sqrt(dot(c, c))
            if n > 1e-4:
                axes.append(tuple(k / n for k in c))
    worst, way = -1e9, (0, 1, 0)
    for ax in axes:
        x = [dot(p, ax) for p in a.pts]
        y = [dot(p, ax) for p in b.pts]
        d1, d2 = min(y) - max(x), min(x) - max(y)
        if d1 > worst:
            worst, way = d1, ax
        if d2 > worst:
            worst, way = d2, tuple(-k for k in ax)
    return worst, way


def box_gap(a, b):
    """a lower bound on apart(): how far their bounds are"""
    d = [max(a.lo[i] - b.hi[i], b.lo[i] - a.hi[i], 0) for i in range(3)]
    return math.sqrt(dot(d, d))


def groups(ps):
    """touching pieces together, biggest group first"""
    parent = list(range(len(ps)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for i in range(len(ps)):
        for j in range(i + 1, len(ps)):
            if find(i) != find(j) and box_gap(ps[i], ps[j]) <= TOUCH and apart(ps[i], ps[j])[0] <= TOUCH:
                parent[find(i)] = find(j)
    out = {}
    for i, p in enumerate(ps):
        out.setdefault(find(i), []).append(p)
    return sorted(out.values(), key=lambda g: -sum(p.size() for p in g))


def nearest(loose, main):
    """the closest pair's gap and way"""
    best, way = 1e9, None
    for a in loose:
        for b in sorted(main, key=lambda m: box_gap(a, m)):
            if box_gap(a, b) >= best:
                break
            g, w = apart(a, b)
            if g < best:
                best, way = g, w
    return best, way


def weld(path):
    """slide every loose group onto the weapon; returns the moves made, in px (biggest group first)"""
    lines, vs, at, faces = read(path)
    gs = groups(pieces(vs, faces))
    if len(gs) < 2:
        return []
    main, rest, moved = gs[0], gs[1:], []
    while rest:
        rest.sort(key=lambda g: nearest(g, main)[0])
        g = rest.pop(0)
        total = (0.0, 0.0, 0.0)
        for _ in range(8):
            d, way = nearest(g, main)
            if d <= -SINK * 0.5:
                break
            v = tuple(way[i] * (d + SINK) for i in range(3))
            for p in g:
                p.move(v)
            total = tuple(total[i] + v[i] for i in range(3))
        moved.append(round(math.sqrt(dot(total, total)) / PX, 2))
        for p in g:
            for k, q in zip(p.ids, p.pts):
                vs[k] = q
                lines[at[k]] = "v %.5f %.5f %.5f" % q
        main += g
    open(path, "w", encoding="utf-8", newline="").write("\n".join(lines))
    return moved


def check(path):
    lines, vs, at, faces = read(path)
    ps = pieces(vs, faces)
    gs = groups(ps)
    all_size = sum(p.size() for p in ps)
    loose = [{"pieces": len(g), "share": round(sum(p.size() for p in g) / all_size, 4), "gap_px": round(nearest(g, gs[0])[0] / PX, 2)} for g in gs[1:]]
    return {"pieces": len(ps), "loose": loose}


def main():
    argv = sys.argv[1:]
    names = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or argv[i - 1] != "--json")]
    rows = json.load(open(os.path.join(GAME, "src/main/resources/ashbound/world_arms.json"), encoding="utf-8"))
    kinds = {r["id"]: r for r in rows}
    if "--all" in argv:
        names = [os.path.basename(c)[:-5] for c in glob.glob(GAME + "/src/main/resources/data/ashbound/capabilities/weapons/*.json")]
    names = names or list(kinds)
    # a bow's drawn poses and a shield's raised one are their own meshes
    meshes = [os.path.basename(f)[:-4] for nm in names for f in [A + nm + ".obj"] + glob.glob(A + nm + "_pulling_*.obj")]
    report, bad = {}, 0
    for nm in meshes:
        f = A + nm + ".obj"
        if not os.path.exists(f):
            continue
        r = check(f)
        report[nm] = r
        if r["loose"]:
            bad += 1
            big = max(l["gap_px"] for l in r["loose"])
            if "--fix" in argv:
                print("%-30s welded %2d, moved up to %.1f px" % (nm, len(r["loose"]), max(weld(f))))
            else:
                print("%-30s %-10s %-9s loose %2d of %3d, widest gap %.1f px, biggest %.1f%%" % (
                    nm, kinds.get(nm, {}).get("kind", ""), kinds.get(nm, {}).get("rarity", ""), len(r["loose"]), r["pieces"], big,
                    max(l["share"] for l in r["loose"]) * 100))
    print("%d of %d have loose parts" % (bad, len(report)))
    if "--json" in argv:
        json.dump(report, open(argv[argv.index("--json") + 1], "w"), indent=1)


if __name__ == "__main__":
    main()
