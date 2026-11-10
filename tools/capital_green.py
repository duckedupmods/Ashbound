"""Highmourn's planting: run after the whole city's built (capital.py), it finds every patch of turf nothing stands on
and plants it, so no stretch of the city reads empty:

  - trees: the wildwood's own templates (data/ashbound/structure/tree, the world's approved trees), the biggest
    that fits each opening, never into a wall, a roof or a doorway, their crowns over a street only above head height;
    oak, pale and blossom in the streets, birch and willow by the water, pine and oak in groves outside the walls
  - bushes: the wildwood's bush templates in the openings too small for a tree, the sculpted rose bushes and
    hydrangeas (tools/blender/school_sculpt.py) in beds against the house fronts
  - the ground: grass, ferns and tall grass in drifts, flowers in patches of one kind, rose bushes, lilacs and
    peonies along the walls, a boulder now and then out in the meadows
  - doorsteps: a clipped bay in a pot or a tub of flowers beside some of the doors onto the streets

Everything's decided from the city's own blocks and the ground's heights, so it's the same every build.
"""
import json
import math
import os
import sys
from collections import deque

import capital_land as L
import city_trees as CT
import nbtio

GAME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TREES = os.path.join(GAME, "src", "main", "resources", "data", "ashbound", "structure", "tree")
OFFSETS = json.load(open(os.path.join(GAME, "src", "main", "resources", "data", "ashbound", "tree", "offsets.json")))
noise = L.noise

SOIL = {"grass_block", "dirt", "coarse_dirt", "podzol", "moss_block", "rooted_dirt"}
SOFT = ("short_grass", "tall_grass", "fern", "large_fern", "poppy", "dandelion", "cornflower", "oxeye_daisy", "allium",
        "azure_bluet", "tulip", "lily_of_the_valley", "blue_orchid", "lilac", "rose_bush", "peony", "sweet_berry_bush",
        "air", "cave_air", "snow")
OUTSIDE = 64                       # how far out past the walls the meadows and groves go
IN_TREES = {                       # inside the walls: (kind, sizes) by where it stands; tools/city_trees.py grows them
    "street": (("linden", "linden", "cherry", "linden", "maple", "birch"), ("medium", "small")),
    "water": (("willow", "birch", "willow"), ("medium", "small")),
}
OUT_TREES = (("oak", "linden", "birch", "cherry", "pine"), ("large", "medium", "small"))   # pine: the wildwood's


def soft(st):
    if st is None:
        return True
    n = st.split("[")[0].split(":")[-1]
    return any(n == s or n.endswith(s) for s in SOFT)


# ================================================================ the templates

_T = {}


def template(name):
    """(blocks [(x, y, z, state)] relative to the trunk's foot, half-width) for a tree template, cached."""
    if name in _T:
        return _T[name]
    t = nbtio.read(os.path.join(TREES, name + ".nbt"))
    pal = []
    for p in t["palette"][2]:
        n = p["Name"]
        n = n[len("minecraft:"):] if n.startswith("minecraft:") else n
        props = p.get("Properties")
        if props:
            props = dict(props)
            if "distance" in props:
                props["distance"] = "7"
                props["persistent"] = "true"
            n += "[" + ",".join("%s=%s" % kv for kv in sorted(props.items())) + "]"
        pal.append(n)
    ox, oy, oz = OFFSETS[name]
    out = []
    for b in t["blocks"][2]:
        x, y, z = (v.v for v in b["pos"][2])
        st = pal[b["state"].v]
        if st.split("[")[0] in ("air", "structure_void"):
            continue
        out.append((x - ox, y - oy, z - oz, st))
    leaves = [y for _, y, _, st in out if "leaves" in st or "needles" in st or "blossom" in st]
    if leaves:                                  # a birch's bare leader over its crown reads as a stray block
        out = [b for b in out if b[1] <= max(leaves) or "leaves" in b[3] or "needles" in b[3]]
    # the offsets mark the root flare's middle, not the trunk: stand the template on its trunk's first layer above
    # the ground, so the turf the planting checked is the turf the trunk rises from
    foot = [(x, z) for x, y, z, st in out if y == 1 and ("log" in st or "wood" in st)]
    if foot:
        cx = round(sum(x for x, _ in foot) / len(foot))
        cz = round(sum(z for _, z in foot) / len(foot))
        out = [(x - cx, y, z - cz, st) for x, y, z, st in out]
    r = max(max(abs(x), abs(z)) for x, _, z, _ in out)
    _T[name] = (out, r)
    return _T[name]


def grown(kind, size, v):
    """One of Highmourn's own trees (tools/city_trees.py), cached like the templates."""
    k = ("grown", kind, size, v)
    if k not in _T:
        _T[k] = CT.grow(kind, size, v)
    return _T[k]


def turned(blocks, q):
    out = []
    for x, y, z, st in blocks:
        for _ in range(q):
            x, z = -z, x
        if q % 2 and "axis=x" in st:
            st = st.replace("axis=x", "axis=z")
        elif q % 2 and "axis=z" in st:
            st = st.replace("axis=z", "axis=x")
        out.append((x, y, z, st))
    return out


# ================================================================ the planting

class Green:
    def __init__(self, S, H, marks):
        self.S, self.H = S, H
        self.B = S.B
        self.planted = set()       # columns a tree, bush or prop now stands on (nothing else goes there)
        self.trunks = {}           # (x >> 4, z >> 4) -> [(x, z, r)]
        self.n = {"trees": 0, "bushes": 0, "props": 0, "plants": 0, "boulders": 0}
        self.cols = {}             # (x, z) -> the column's blocks above ground: set of y
        for (x, y, z), st in self.B.items():
            if (not soft(st) or "water" in st) and st.split("[")[0] not in SOIL:
                self.cols.setdefault((x, z), set()).add(y)
        self.doors = set()
        for (x, y, z), st in self.B.items():
            n = st.split("[")[0]
            if n.endswith("_door") or n.endswith("_gate") or "portal" in n:
                for dx in range(-2, 3):
                    for dz in range(-2, 3):
                        if abs(dx) + abs(dz) <= 2:
                            self.doors.add((x + dx, z + dz))
        for v in marks.values():
            x, z = int(v[0]), int(v[2])
            for dx in range(-2, 3):
                for dz in range(-2, 3):
                    self.doors.add((x + dx, z + dz))

    def g(self, x, z):
        return self.H.get((x, z), 0)

    def bare(self, x, z):
        """Turf with nothing standing on it, its ground block soil (or left to the game's turf)."""
        if (x, z) in self.planted:
            return False
        g = self.g(x, z)
        ys = self.cols.get((x, z))
        if ys and any(y >= g for y in ys):
            return False
        st = self.B.get((x, g, z))
        if st is not None and st.split("[")[0] not in SOIL:
            return False
        for y in range(g - 2, g + 1):
            s = self.B.get((x, y, z))
            if s is not None and "water" in s:
                return False
        return True

    def zone(self, x, z):
        """'in' inside the walls, 'out' on the valley floor round them, None where nothing's to be planted."""
        e = L.edist(x, z)
        if e < -2:
            return "in"
        if e < 4 or e > OUTSIDE or L.floor_d(x, z) > 0 or L.in_plaza(x, z):
            return None
        if abs(x) <= 22 and L.GATE_Z - 4 <= z <= L.GATE_Z + 64:
            return None                                       # the gate's apron and the road to it
        md = L.moat_d(x, z)
        if md is not None and md < 3:
            return None
        return "out"

    # ---------------------------------------------------------------- a tree or a bush from its template

    def fits(self, x0, z0, blocks, street_clear=4):
        g0 = self.g(x0, z0)
        for x, y, z, st in blocks:
            X, Y, Z = x0 + x, g0 + y, z0 + z
            if (X, Z) in self.doors and y < 5:
                return False
            ys = self.cols.get((X, Z))
            g = self.g(X, Z)
            wood = "log" in st or "wood" in st
            if wood and y <= 1 and (x, z) != (0, 0) and not self.bare(X, Z):
                return False                                     # trunk or root on paving, a step or a kerb
            if Y <= g:
                if wood and y >= 1:
                    return False                                 # a bough into a bank
                continue
            if ys:
                if any(abs(yy - Y) <= 1 for yy in ys):
                    return False                                 # into a wall or a roof
                if Y - g < street_clear and any(yy <= g for yy in ys):
                    return False                                 # over a paved way, not above head height
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nys = self.cols.get((X + dx, Z + dz))
                if nys and any(abs(yy - Y) <= 0 and yy > self.g(X + dx, Z + dz) for yy in nys):
                    return False                                 # touching a wall
            if (X, Z) in self.planted and Y - g < 3:
                return False
        return True

    def stamp(self, x0, z0, blocks):
        g0 = self.g(x0, z0)
        for x, y, z, st in blocks:
            X, Y, Z = x0 + x, g0 + y, z0 + z
            if Y <= self.g(X, Z):
                old = self.B.get((X, Y, Z))
                if old is not None and old.split("[")[0] not in SOIL:
                    continue
            elif not soft(self.B.get((X, Y, Z))):
                continue
            self.S.put(X, Y, Z, st)
            self.cols.setdefault((X, Z), set()).add(Y)
        for x, y, z, _ in blocks:
            if y <= 2:
                self.planted.add((x0 + x, z0 + z))

    def crowded(self, x, z, r):
        for i in range((x >> 4) - 2, (x >> 4) + 3):
            for j in range((z >> 4) - 2, (z >> 4) + 3):
                for tx, tz, tr in self.trunks.get((i, j), ()):
                    if math.hypot(x - tx, z - tz) < (r + tr) * 0.7:
                        return True
        return False

    def tree(self, x, z, kinds, sizes, salt, room):
        """The biggest of sizes that fits here (one try a size: a kind and a variant picked from where it stands)."""
        for s in sizes:
            if room < {"large": 5, "medium": 3, "small": 2}[s]:
                continue
            kind = kinds[int(noise(x, z, 9, salt) * 7919) % len(kinds)]
            name = "%s_%s_%d" % (kind, s, (x * 7 + z * 13) % 3)
            if kind in CT.SPECIES:
                blocks, r = grown(kind, s, (x * 7 + z * 13) % 3)
            elif name in OFFSETS:
                blocks, r = template(name)
            else:
                continue
            if self.crowded(x, z, r):
                continue
            tb = turned(blocks, (x * 5 + z * 3) % 4)
            if self.fits(x, z, tb):
                self.stamp(x, z, tb)
                self.trunks.setdefault((x >> 4, z >> 4), []).append((x, z, r))
                self.n["trees"] += 1
                return True
        return False

    def bush(self, x, z):
        for v in range(2):
            name = "bush_%d" % ((v * 3 + x * 3 + z * 5) % 8)
            blocks, r = template(name)
            tb = turned(blocks, (x + z) % 4)
            if self.fits(x, z, tb, street_clear=99):
                self.stamp(x, z, tb)
                self.n["bushes"] += 1
                return True
        return False

    def prop(self, name, x, z, facing="north"):
        g = self.g(x, z)
        self.S.put(x, g + 1, z, "ashbound:%s[facing=%s,piece=0]" % (name, facing))
        self.cols.setdefault((x, z), set()).add(g + 1)
        self.planted.add((x, z))
        self.n["props"] += 1


def openness(G, cells):
    """Each bare cell's distance to the nearest cell that isn't (four-way steps)."""
    d = {}
    q = deque()
    for (x, z) in cells:
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, z + dz) not in cells:
                d[(x, z)] = 1
                q.append((x, z))
                break
    while q:
        x, z = q.popleft()
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            c = (x + dx, z + dz)
            if c in cells and c not in d:
                d[c] = d[(x, z)] + 1
                q.append(c)
    return d


FLOWERS = ("poppy", "dandelion", "cornflower", "oxeye_daisy", "allium", "azure_bluet", "red_tulip", "white_tulip",
           "pink_tulip", "orange_tulip", "lily_of_the_valley", "blue_orchid")
TALL = ("lilac", "rose_bush", "peony")


def by_house(G, x, z):
    """Next to a house's wall (a block stood above the ground beside it)."""
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ys = G.cols.get((x + dx, z + dz))
        g = G.g(x + dx, z + dz)
        if ys and any(g < y <= g + 3 for y in ys):
            return True
    return False


def by_water(G, x, z, r=6):
    for dx in range(-r, r + 1, 2):
        for dz in range(-r, r + 1, 2):
            s = G.B.get((x + dx, G.g(x + dx, z + dz), z + dz)) or G.B.get((x + dx, G.g(x + dx, z + dz) + 1, z + dz))
            if s is not None and s.startswith("water"):
                return True
    return False


def plant(S, H, marks):
    G = Green(S, H, marks)
    x0, z0, W, D = L.GRID
    cells, zones = set(), {}
    for x in range(x0, x0 + W):
        for z in range(z0, z0 + D):
            if (x, z) not in H:
                continue
            zn = G.zone(x, z)
            if zn and G.bare(x, z):
                cells.add((x, z))
                zones[(x, z)] = zn
    d = openness(G, cells)
    print("green: %d bare columns (%d inside the walls)" % (len(cells), sum(1 for v in zones.values() if v == "in")))
    order = sorted(cells, key=lambda c: -d[c] * 1000 + int(noise(c[0], c[1], 1.7, 901) * 997))
    # trees, the most open places first
    for (x, z) in order:
        if (x, z) in G.planted or (x, z) in G.doors or not G.bare(x, z):
            continue
        o = d[(x, z)]
        if zones[(x, z)] == "in":
            if o < 3 or noise(x, z, 5, 902) < 0.35:
                continue
            kinds, sizes = IN_TREES["water" if by_water(G, x, z) else "street"]
            if o >= 6:
                sizes = ("large",) + sizes if noise(x, z, 30, 903) > 0.55 else sizes
            G.tree(x, z, kinds, sizes, 910, o)
        elif L.edist(x, z) > 24:                          # a meadow under the walls, so they read from the road
            grove = noise(x, z, 40, 904)
            fade = L.smooth(36, OUTSIDE, L.edist(x, z))          # thinning out to the edge, no hard rim
            p = noise(x, z, 4, 905)
            if (grove > 0.52 and p > 0.3 + fade * 0.65) or p > 0.94 + fade * 0.05:
                kinds = ("willow", "birch") if by_water(G, x, z, 10) else OUT_TREES[0]
                G.tree(x, z, kinds, OUT_TREES[1] if grove > 0.6 else OUT_TREES[1][1:], 920, o)
    # bushes in what's left that's wide enough, beds of sculpted bushes along the house fronts
    for (x, z) in order:
        if (x, z) in G.planted or (x, z) in G.doors or not G.bare(x, z):
            continue
        o = d[(x, z)]
        h = noise(x, z, 3, 930)
        if zones[(x, z)] == "in" and by_house(G, x, z):
            if h > 0.84:
                G.prop("rose_bush" if noise(x, z, 9, 931) > 0.5 else "hydrangea", x, z, ("north", "east", "south", "west")[(x + z) % 4])
        elif o >= 2 and h > (0.6 if zones[(x, z)] == "in" else 0.8 + 0.15 * L.smooth(36, OUTSIDE, L.edist(x, z))):
            G.bush(x, z)
        elif zones[(x, z)] == "out" and h < 0.035 and o >= 3:
            blocks, _ = template("boulder_%d" % ((x + z) % 6))
            tb = turned(blocks, x % 4)
            if G.fits(x, z, tb, street_clear=99):
                G.stamp(x, z, tb)
                G.n["boulders"] += 1
    # the ground: grass in drifts, flowers in patches of one kind, tall flowers along the walls
    for (x, z) in cells:
        if (x, z) in G.planted or not G.bare(x, z):
            continue
        g = G.g(x, z)
        if (x, g + 1, z) in G.B:
            continue
        drift = noise(x, z, 6, 940)
        patch = noise(x, z, 5, 941)
        r = noise(x, z, 0.9, 942)
        st = None
        if by_house(G, x, z) and (x, z) not in G.doors and r > 0.82:
            t = TALL[int(noise(x, z, 7, 943) * 2.99)]
            st = [(0, t + "[half=lower]"), (1, t + "[half=upper]")]
        elif patch > 0.68 and r > 0.35:
            st = [(0, FLOWERS[int(noise(x, z, 11, 944) * 11.99)])]
        elif drift > 0.45 and r > 0.3:
            if r > 0.9 and drift > 0.6:
                st = [(0, "tall_grass[half=lower]"), (1, "tall_grass[half=upper]")]
            elif r > 0.8:
                st = [(0, "fern")]
            else:
                st = [(0, "short_grass")]
        elif r > 0.93:
            st = [(0, "short_grass")]
        if st:
            if any((x, g + 1 + dy, z) in G.B for dy, _ in st):
                continue
            for dy, s in st:
                S.put(x, g + 1 + dy, z, s)
            G.n["plants"] += 1
    squares(G)
    doorsteps(G)
    print("green: %(trees)d trees, %(bushes)d bushes, %(boulders)d boulders, %(props)d potted and bedded, %(plants)d plants" % G.n)


def squares(G):
    """Trees in raised beds round the edges of the wide squares and avenues: three in from the paving's edge, where
    the paving runs at least six deep, never in front of a door."""
    x0, z0, W, D = L.GRID
    paved = set()
    for (x, z), ys in G.cols.items():
        if G.zone(x, z) != "in" or (x, z) in G.doors:
            continue
        g = G.g(x, z)
        if g in ys and not any(y > g for y in ys):
            paved.add((x, z))
    d = openness(G, paved)
    wide = {c for c, v in d.items() if v >= 6}
    near = set()
    for (x, z) in wide:
        for dx in range(-4, 5):
            for dz in range(-4, 5):
                near.add((x + dx, z + dz))
    n = 0
    for (x, z) in sorted(paved, key=lambda c: int(noise(c[0], c[1], 1.3, 960) * 9973)):
        if d[(x, z)] != 3 or (x, z) not in near:
            continue
        bed = [(x + dx, z + dz) for dx in (-1, 0, 1) for dz in (-1, 0, 1)]
        if any(c not in paved or d[c] < 2 or G.g(*c) != G.g(x, z) for c in bed):
            continue
        if G.crowded(x, z, 3):
            continue
        blocks, r = grown(("linden", "cherry", "linden", "maple")[int(noise(x, z, 20, 961) * 3.99)], "small", (x + z) % 3)
        rel = {(c[0] - x, c[1] - z) for c in bed}
        # stood on the bed's turf, its lowest boughs pruned off over the paving (head height kept)
        tb = [(bx, by + 1, bz, st) for bx, by, bz, st in turned(blocks, (x + 2 * z) % 4)
              if ((bx, bz) in rel and by >= 1) or ((bx, bz) not in rel and by >= 3)]
        if not G.fits(x, z, [b for b in tb if (b[0], b[2]) not in rel or b[1] > 4]):
            continue
        g = G.g(x, z)
        for (bx, bz) in bed:
            rim = (bx, bz) != (x, z)
            G.S.put(bx, g, bz, "dirt" if not rim else "ashbound:greystone")
            G.S.put(bx, g + 1, bz, "ashbound:greystone_slab[type=bottom,waterlogged=false]" if rim else "grass_block[snowy=false]")
            G.cols.setdefault((bx, bz), set()).add(g + 1)
            G.planted.add((bx, bz))
        G.stamp(x, z, tb)
        G.trunks.setdefault((x >> 4, z >> 4), []).append((x, z, 6))
        n += 1
    G.n["trees"] += n
    print("green: %d trees in beds round the squares" % n)


def doorsteps(G):
    """A bay in a pot or a tub of flowers beside some of the street doors: on the paving, against the wall, never
    in front of the door, the way past it kept."""
    seen = set()
    for (x, y, z), st in list(G.B.items()):
        if not st.split("[")[0].endswith("_door") or "half=lower" not in st:
            continue
        f = st.split("facing=")[1].split(",")[0].split("]")[0]
        if (x, z) in seen or noise(x, z, 2, 950) < 0.55:
            continue
        seen.add((x, z))
        fx, fz = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}[f]
        sx, sz = -fz, fx                                      # along the wall
        for side in ((1, -1) if (x + z) % 2 else (-1, 1)):
            px, pz = x + fx + sx * side, z + fz + sz * side
            g = G.g(px, pz)
            ok = True
            for cx, cz in ((px, pz), (px + fx, pz + fz), (px + fx * 2, pz + fz * 2)):
                ys = G.cols.get((cx, cz))
                if not ys or any(yy > G.g(cx, cz) for yy in ys) or abs(G.g(cx, cz) - y + 1) > 0:
                    ok = False                                # paved, nothing on it, level with the door's sill
            ys = G.cols.get((x + sx * side, z + sz * side))
            if not ok or not ys or not any(yy >= y for yy in ys):
                continue                                      # a wall behind it
            if (px, y, pz) in G.B and G.B[(px, y, pz)] not in ("air",):
                continue
            name = "topiary_pot" if noise(px, pz, 3, 951) > 0.5 else "flower_tub"
            G.S.put(px, y, pz, "ashbound:%s[facing=%s,piece=0]" % (name, f))
            if name == "topiary_pot":
                if (px, y + 1, pz) in G.B and G.B[(px, y + 1, pz)] != "air":
                    G.S.put(px, y, pz, "ashbound:flower_tub[facing=%s,piece=0]" % f)
                else:
                    G.S.put(px, y + 1, pz, "ashbound:topiary_pot[facing=%s,piece=1]" % f)
            G.cols.setdefault((px, pz), set()).update({y, y + 1})
            G.n["props"] += 1
            break


if __name__ == "__main__":
    sys.exit("run by capital.py")
