"""A village's plan, the way real ones grow (docs/VILLAGES.md): the focus first, roads along the land's easy line to
it, then plots carved off the roads - dense round the focus, yards in the middle ring, farmsteads at the edge - each
house composed (vhouse.py) and set to face its road, its yard behind it, life between the houses.

Works on villages.py's ground (G heights, WET water) and Build S; draws a plan view with plan_png().
"""
import heapq
import math

from PIL import Image, ImageDraw

import houses as H
import structkit as K
import vhouse as VH

DIRS8 = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]


class Plan:
    def __init__(self, V, box, focus, rings=(18, 40, 62), pal=VH.PAL, cap=24, deck=None, stone=True):
        self.deck = deck             # houses and walks over water stand at this level, on stilts
        self.stone = stone           # stone ground floors allowed (not over a lake)
        self.dig = 0                 # > 0: houses may be cut this deep into rising rock behind them (cliff terraces)
        self.walkcells = set()
        self.V, self.S = V, V.S
        self.box, self.focus, self.rings, self.pal, self.cap = box, focus, rings, pal, cap
        self.occ = {}                # (x, z) -> road | house | yard | focus | field | landmark
        self.roads = []              # (pts, width, kind)
        self.houses = []             # dict(x0, z0, cells, role, face, y, door)
        self.trees = []

    # ------------------------------------------------------------ helpers
    def g(self, x, z):
        return self.V.G.get((x, z), 0)

    def inside(self, x, z):
        x0, z0, x1, z1 = self.box
        return x0 + 2 <= x <= x1 - 2 and z0 + 2 <= z <= z1 - 2

    def ring(self, x, z):
        d = math.hypot(x - self.focus[0], z - self.focus[1])
        for name, r in zip(("core", "mid", "edge"), self.rings):
            if d < r:
                return name
        return "out"

    # ------------------------------------------------------------ roads
    def route(self, a, b, slope=30.0, reuse=0.35):
        """A* from a to b over the ground: steep steps cost dearly (the road winds), water is shut, an existing
        road is cheap (roads join and share)."""
        S = self.S
        open_ = [(0, a)]
        came, cost = {a: None}, {a: 0.0}
        while open_:
            _, cur = heapq.heappop(open_)
            if cur == b:
                break
            for dx, dz in DIRS8:
                nx, nz = cur[0] + dx, cur[1] + dz
                if not self.inside(nx, nz) or (nx, nz) in self.V.WET:
                    continue
                t = self.occ.get((nx, nz))
                if t in ("house", "landmark", "field"):
                    continue
                d = 1.414 if dx and dz else 1.0
                dh = abs(self.g(nx, nz) - self.g(*cur))
                c = d * (1 + slope * (dh / d) ** 2) * (reuse if t == "road" else 1.0)
                c *= 1 + 0.25 * self.V.noise(nx, nz, 7, 9) ** 2
                nc = cost[cur] + c
                if nc < cost.get((nx, nz), 1e18):
                    cost[(nx, nz)] = nc
                    came[(nx, nz)] = cur
                    heapq.heappush(open_, (nc + math.hypot(b[0] - nx, b[1] - nz), (nx, nz)))
        path, p = [], b
        while p is not None:
            path.append(p)
            p = came.get(p)
        path.reverse()
        # smooth: every 3rd node, then two Chaikin passes, back to 1-block steps
        pts = [path[0]] + path[3:-1:3] + [path[-1]]
        for _ in range(2):
            q = [pts[0]]
            for i in range(len(pts) - 1):
                (x0, z0), (x1, z1) = pts[i], pts[i + 1]
                q += [(0.75 * x0 + 0.25 * x1, 0.75 * z0 + 0.25 * z1), (0.25 * x0 + 0.75 * x1, 0.25 * z0 + 0.75 * z1)]
            q.append(pts[-1])
            pts = q
        out = []
        for i in range(len(pts) - 1):
            (x0, z0), (x1, z1) = pts[i], pts[i + 1]
            n = max(1, int(math.hypot(x1 - x0, z1 - z0) * 2))
            for k in range(n):
                out.append((x0 + (x1 - x0) * k / n, z0 + (z1 - z0) * k / n))
        out.append(pts[-1])
        return out

    def road(self, pts, width=1.5, kind="main"):
        self.roads.append((pts, width, kind))
        for (x, z) in pts:
            r = width + 0.4 * self.V.noise(x, z, 6, 11)
            for a in range(int(x - r - 1), int(x + r + 2)):
                for b in range(int(z - r - 1), int(z + r + 2)):
                    if math.hypot(a + 0.5 - x, b + 0.5 - z) <= r and self.occ.get((a, b)) in (None, "yard"):
                        self.occ[(a, b)] = "road"

    def wcurve(self, a, b, wob=4.0, seed=0):
        """a wandering line from a to b in 1-block steps (boardwalks, which needn't follow the land)"""
        r = self.S.rnd
        (x0, z0), (x1, z1) = a, b
        L = math.hypot(x1 - x0, z1 - z0) or 1
        nx, nz = -(z1 - z0) / L, (x1 - x0) / L
        n = max(2, int(L / 9))
        pts = [(x0, z0)] + [(x0 + (x1 - x0) * k / n + nx * r.uniform(-wob, wob), z0 + (z1 - z0) * k / n + nz * r.uniform(-wob, wob))
                            for k in range(1, n)] + [(x1, z1)]
        for _ in range(3):
            q = [pts[0]]
            for i in range(len(pts) - 1):
                (p0, q0), (p1, q1) = pts[i], pts[i + 1]
                q += [(0.75 * p0 + 0.25 * p1, 0.75 * q0 + 0.25 * q1), (0.25 * p0 + 0.75 * p1, 0.25 * q0 + 0.75 * q1)]
            q.append(pts[-1])
            pts = q
        out = []
        for i in range(len(pts) - 1):
            (p0, q0), (p1, q1) = pts[i], pts[i + 1]
            m = max(1, int(math.hypot(p1 - p0, q1 - q0) * 2))
            out += [(p0 + (p1 - p0) * k / m, q0 + (q1 - q0) * k / m) for k in range(m)]
        return out + [pts[-1]]

    def walk(self, pts, width=1.6):
        """a boardwalk: like a road, but over the water it's planks on posts with a rail"""
        before = {p for p, t in self.occ.items() if t == "road"}
        self.road(pts, width, "walk")
        self.walkcells |= {p for p, t in self.occ.items() if t == "road"} - before

    def pave(self):
        """Lay the roads on the ground: setts round the focus, trodden earth further out, grass in the crown of a lane."""
        S = self.S
        for (a, b), t in list(self.occ.items()):
            low = (a, b) in self.walkcells and self.deck is not None and self.g(a, b) < self.deck
            if t not in ("road", "path") or ((a, b) not in self.V.WET and not low) or self.deck is None:
                continue
            y = self.deck                                # planks over the water, posts, a rail on the open edge
            S.put(a, y, b, "spruce_planks")
            if (a * 3 + b * 5) % 7 == 0:
                for yy in range(self.g(a, b) + 1, y):
                    S.put(a, yy, b, "spruce_log[axis=y]")
            for dx in (-1, 0, 1):                       # the rail stands on its own boards just outside the walk,
                for dz in (-1, 0, 1):                   # corners and all, so the whole walk's width stays free
                    q = (a + dx, b + dz)
                    if (dx or dz) and self.occ.get(q) is None and q in self.V.WET:
                        S.put(q[0], y, q[1], "spruce_planks")
                        S.put(q[0], y + 1, q[1], "spruce_fence")
                        self.occ[q] = "rail"
        for (a, b) in self.walkcells:                   # where a raised walk meets the land: steps down to the ground
            if self.deck is None or (a, b) in self.V.WET or self.g(a, b) >= self.deck:
                continue
            for dx, dz, f in ((1, 0, "west"), (-1, 0, "east"), (0, 1, "north"), (0, -1, "south")):
                q = (a + dx, b + dz)
                if self.occ.get(q) == "road" and q not in self.walkcells:
                    for k in range(1, self.deck - self.g(*q) + 1):
                        qq = (a + dx * k, b + dz * k)
                        if self.deck - k > self.g(*qq):
                            S.put(qq[0], self.deck - k + 1, qq[1], H.stairs("spruce", f))
                            for yy in range(self.g(*qq) + 1, self.deck - k + 1):
                                S.put(qq[0], yy, qq[1], "spruce_planks")
        for (a, b), t in self.occ.items():
            if t != "road" or ((a, b) in self.V.WET and self.deck is not None) or (a, b) in self.walkcells and self.deck is not None and self.g(a, b) < self.deck:
                continue
            y = self.g(a, b)
            rg = self.ring(a, b)
            if rg == "core":
                st = S.pick(("ashbound:limestone_flagstones", 3), ("ashbound:greystone", 3), ("cobblestone", 2), ("andesite", 1))
            elif rg == "mid":
                st = S.pick(("dirt_path", 6), ("coarse_dirt", 2), ("gravel", 1), ("ashbound:greystone", 1))
            else:
                st = S.pick(("dirt_path", 5), ("coarse_dirt", 3), ("grass_block[snowy=false]", 1))
            S.put(a, y, b, st)
            for yy in range(y + 1, y + 4):
                c = S.get(a, yy, b)
                if c and not c.startswith("ashbound:") and ("grass" in c or "fern" in c or c in ("poppy", "dandelion")):
                    S.put(a, yy, b, None)
            up = [q for q in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)) if self.occ.get(q) == "road" and self.g(*q) == y + 1]
            if up and S.get(a, y + 1, b) in (None, "air"):        # a half step where the road climbs a block
                S.put(a, y + 1, b, ("ashbound:pale_limestone_slab[type=bottom,waterlogged=false]" if rg == "core"
                                    else "mud_brick_slab[type=bottom,waterlogged=false]"))

    # ------------------------------------------------------------ plots
    def fits(self, cells, margin, yard_ok):
        ys = []
        for (a, b) in cells:
            if not self.inside(a, b) or ((a, b) in self.V.WET and self.deck is None):
                return None
            ys.append(self.g(a, b))
            for dx in range(-margin, margin + 1):
                for dz in range(-margin, margin + 1):
                    t = self.occ.get((a + dx, b + dz))
                    if t in ("road", "house", "focus", "field", "landmark", "steps"):
                        return None
            if self.occ.get((a, b)) == "yard" and not yard_ok:
                return None
        wet = [c for c in cells if c in self.V.WET]
        if wet and self.deck is not None:
            dry = [self.g(*c) for c in cells if c not in self.V.WET]
            return max([self.deck] + dry) if not dry or max(dry) - self.deck <= 2 else None
        if self.dig and max(ys) - min(ys) > 6:
            floor = sorted(ys)[len(ys) // 3]
            return floor if max(ys) - floor <= self.dig and floor - min(ys) <= 2 else None
        if max(ys) - min(ys) > 7:
            return None
        return max(ys) - min(2, (max(ys) - min(ys)) // 2)      # sunk into the slope; place() grades the land to it

    def frontage(self, pts, sides=(1, -1), skip=0.15, start=4, stop=4, roles=None):
        """Houses along a road, both sides, each facing it; gaps and setbacks by ring; their yards behind."""
        S = self.S
        n = len(pts)
        for side in sides:
            s = start * 2 + S.rnd.randint(0, 6)
            while s < n - stop * 2 and len(self.houses) < self.cap:
                i = int(s)
                x, z = pts[i]
                j = min(n - 1, i + 4)
                tx, tz = pts[j][0] - pts[max(0, i - 4)][0], pts[j][1] - pts[max(0, i - 4)][1]
                L = math.hypot(tx, tz) or 1
                tx, tz = tx / L, tz / L
                nx, nz = -tz * side, tx * side                   # out from the road to this side
                rg = self.ring(x, z)
                if rg == "out" or (roles and rg not in roles) or S.rnd.random() < skip:
                    s += 8 + S.rnd.randint(0, 10)
                    continue
                face = ("west" if nx > 0 else "east") if abs(nx) > abs(nz) else ("north" if nz > 0 else "south")
                role = rg if rg != "edge" or S.rnd.random() < 0.6 else "farm"
                T = K.Build()
                T.rnd = S.rnd
                h = VH.compose(T, 0, 0, face, role, self.pal, stone=self.stone)
                fw = max(a for a, _ in h["cells"]) + 1
                fd = max(b for _, b in h["cells"]) + 1
                along = fw if face in ("north", "south") else fd
                deep = fd if face in ("north", "south") else fw
                back = {"core": (1, 2), "mid": (2, 4), "edge": (2, 5)}.get(rg, (2, 4))
                set_ = S.rnd.randint(*back)
                for extra in (0, 1, 2, 3, 4):        # pushed back off the road until it's clear
                    cx = x + nx * (2.6 + set_ + extra + deep / 2)
                    cz = z + nz * (2.6 + set_ + extra + deep / 2)
                    x0, z0 = int(round(cx - fw / 2)), int(round(cz - fd / 2))
                    cells = [(a + x0, b + z0) for a, b in h["cells"]]
                    y = self.fits(cells, 0 if rg == "core" else 1, rg == "core")
                    if y is not None:
                        break
                if y is None:
                    s += 3
                    continue
                self.place(T, h, x0, z0, y, face, role, (nx, nz), along, deep)
                gap = {"core": (0, 2), "mid": (4, 9), "edge": (10, 20)}[rg]
                s += (along + S.rnd.randint(*gap)) * 2

    def around(self, r0, tries=40, n=99, role="core"):
        """The green village's knot: houses shoulder to shoulder round the focus, each facing it across the green."""
        S = self.S
        fx, fz = self.focus
        a = S.rnd.random() * 6.283
        for _ in range(tries):
            if len(self.houses) >= self.cap:
                break
            a += 0.18 + S.rnd.random() * 0.25
            ox, oz = math.cos(a), math.sin(a)
            face = ("west" if ox > 0 else "east") if abs(ox) > abs(oz) else ("north" if oz > 0 else "south")
            T = K.Build()
            T.rnd = S.rnd
            if n <= 0:
                break
            h = VH.compose(T, 0, 0, face, role, self.pal, stone=self.stone)
            fw = max(p for p, _ in h["cells"]) + 1
            fd = max(q for _, q in h["cells"]) + 1
            deep = fd if face in ("north", "south") else fw
            for extra in (0, 1, 2, 3):
                cx, cz = fx + ox * (r0 + 1.5 + extra + deep / 2), fz + oz * (r0 + 1.5 + extra + deep / 2)
                x0, z0 = int(round(cx - fw / 2)), int(round(cz - fd / 2))
                cells = [(p + x0, q + z0) for p, q in h["cells"]]
                y = self.fits(cells, 0, True)
                if y is not None:
                    self.place(T, h, x0, z0, y, face, role, (ox, oz), fw if face in ("north", "south") else fd, deep)
                    n -= 1
                    break

    def place(self, T, h, x0, z0, y, face, role, out, along, deep, footing=True, yard=True):
        S, V = self.S, self.V
        cells = [(a + x0, b + z0) for a, b in h["cells"]]
        cs = set(cells)
        if footing and not any(c in V.WET for c in cells):
            V.grade(cells, y, self.occ)
        for (a, b) in cells:                     # the ground under it cleared, a footing down to the land
            for yy in range(y + 1, y + 40):
                if S.get(a, yy, b) is not None:
                    S.put(a, yy, b, None)
        for (bx, by, bz), st in T.B.items():
            S.put(bx + x0, by + y, bz + z0, st, T.nbt.get((bx, by, bz)))
        for (a, b) in cells:
            g = self.g(a, b)
            edge = any((a + dx, b + dz) not in cs for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            self.occ[(a, b)] = "house"
            if not footing:
                continue
            if (a, b) in V.WET:                          # a frame on stilts down to the lake bed, the water left round them
                floored = S.get(a, y, b) not in (None, "air")
                out_x = (a + 1, b) not in cs or (a - 1, b) not in cs
                out_z = (a, b + 1) not in cs or (a, b - 1) not in cs
                rim = floored and any(S.get(a + dx, y, b + dz) in (None, "air") or (a + dx, b + dz) not in cs
                                      for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                post = rim and ((a + b) % 2 == 0 or (out_x and out_z))
                for yy in range(g + 1, y - 1):
                    S.put(a, yy, b, "spruce_log[axis=y]" if post else ("water[level=0]" if yy <= V.WET[(a, b)] else None))
                if post:
                    S.put(a, y - 1, b, "spruce_log[axis=y]")
                elif rim:                                # the sill beam round under the floor
                    S.put(a, y - 1, b, "stripped_spruce_log[axis=%s]" % ("z" if out_x and not out_z else "x"))
                else:
                    S.put(a, y - 1, b, "water[level=0]" if y - 1 <= V.WET[(a, b)] else None)
                continue
            for yy in range(g - 1, y):
                S.put(a, yy, b, H.stone(S) if edge else "dirt")
            self.occ[(a, b)] = "house"
        door = (h["door"][0] + x0, h["door"][1] + z0)
        self.steps(door, y, face, cs)
        self.houses.append(dict(x0=x0, z0=z0, cells=cells, role=role, face=face, y=y, door=door, out=out,
                                along=along, deep=deep, two=h["two"]))
        # the path from the door out to the road
        dx, dz = -out[0], -out[1]
        px, pz = door
        last = None
        for k in range(12):
            c = (round(px), round(pz))
            if last and last[0] != c[0] and last[1] != c[1] and (c[0], last[1]) not in cs and self.occ.get((c[0], last[1])) != "road":
                self.occ[(c[0], last[1])] = "path"               # no corner-to-corner steps: a body can't squeeze through
            if self.occ.get(c) == "road":
                break
            if c not in cs:
                self.occ[c] = "path"
            last = c
            px, pz = px + dx, pz + dz
        if not yard:
            self.houses[-1]["yard"] = []
            return
        # the yard behind: a clean rectangle square to the house, only as deep as stays clear (a ragged lot is what made
        # the fences into mazes)
        bx, bz = {"north": (0, 1), "south": (0, -1), "east": (-1, 0), "west": (1, 0)}[face]       # the back, away from the road
        ydeep = {"core": 4, "mid": 8, "edge": 10, "farm": 12}.get(role, 6) + S.rnd.randint(0, 3)
        xs = [a for a, _ in cells]
        zs = [b for _, b in cells]
        ext = S.rnd.randint(0, 1)
        if bx == 0:
            us = range(min(xs) - ext, max(xs) + ext + 1)
            base = max(zs) if bz > 0 else min(zs)
            cell = lambda u, v: (u, base + bz * v)
        else:
            us = range(min(zs) - ext, max(zs) + ext + 1)
            base = max(xs) if bx > 0 else min(xs)
            cell = lambda u, v: (base + bx * v, u)
        mid = (us[0] + us[-1]) / 2
        yard = []
        for v in range(1, ydeep + 1):
            row = [cell(u, v) for u in us]
            if not all(self.inside(*c) and self.occ.get(c) is None and c not in V.WET for c in row):
                break
            yard += [(c[0], c[1], u - mid, v) for c, u in zip(row, us)]
        if len(yard) < 3 * len(us):
            yard = []
        for a, b, u, v in yard:
            self.occ[(a, b)] = "yard"
        self.houses[-1]["yard"] = yard

    def steps(self, door, y, face, cs):
        """front steps: from the sill (or the porch's edge) a flight three wide down to the ground, greystone stairs
        on a solid fill, so no door stands a block or more over the land with nothing to climb"""
        S, V = self.S, self.V
        dx, dz = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}[face]
        tx, tz = -dz, dx
        x, z = door
        while (x + dx, z + dz) in cs or S.get(x + dx, y, z + dz) not in (None, "air") and not V._natural(S.get(x + dx, y, z + dz)):
            x, z = x + dx, z + dz                              # out over the porch's boards to their edge
            if abs(x - door[0]) + abs(z - door[1]) > 4:
                return
        h = y                                                  # the next stair's height: its top meets the floor at y + 1
        k = 1
        while h > self.g(x + dx * k, z + dz * k) and k <= 8:
            for w in (-1, 0, 1):
                c = (x + dx * k + tx * w, z + dz * k + tz * w)
                if c in V.WET or self.occ.get(c) in ("house", "focus", "landmark") or c in cs:
                    continue
                cur = S.get(c[0], h, c[1])
                if cur is not None and not V._natural(cur):
                    continue
                S.put(c[0], h, c[1], "%s_stairs[facing=%s,half=bottom,shape=straight,waterlogged=false]"
                      % ("stone_brick" if S.rnd.random() < 0.85 else "mossy_stone_brick", {(0, -1): "south", (0, 1): "north", (1, 0): "west", (-1, 0): "east"}[(dx, dz)]))
                for yy in range(self.g(*c) + 1, h):
                    S.put(c[0], yy, c[1], "stone_bricks")
                for yy in (h + 1, h + 2):
                    if V._natural(S.get(c[0], yy, c[1])):
                        S.put(c[0], yy, c[1], None)
                if self.occ.get(c) in (None, "yard", "path"):
                    self.occ[c] = "steps"
            h -= 1
            k += 1

    # ------------------------------------------------------------ life
    def yards(self):
        """What's behind each house: a kitchen garden, a woodpile, a fruit tree, a washing line, a haystack, hives;
        a fence or a low wall round the lot."""
        S = self.S
        for hs in self.houses:
            yard = hs.get("yard", [])
            if not yard:
                continue
            cells = {(a, b) for a, b, _, _ in yard}
            kind = S.pick(("fence", 3), ("wall", 2), ("hedge", 2), ("open", 2))
            u0, u1, vmax = min(u for _, _, u, _ in yard), max(u for _, _, u, _ in yard), max(v for _, _, _, v in yard)
            for a, b, u, v in yard:                  # the three far sides, a gate in the middle of the back
                y = self.g(a, b) + 1
                edge = u in (u0, u1) or v == vmax
                gate = v == vmax and abs(u) < 0.6
                if edge and not gate and kind != "open" and self.occ.get((a, b)) == "yard":
                    S.put(a, y, b, {"fence": "spruce_fence", "wall": "ashbound:greystone_wall",
                                    "hedge": "azalea_leaves[distance=1,persistent=true,waterlogged=false]"}[kind])
            things = S.rnd.sample(["garden", "garden", "woodpile", "tree", "tree", "line", "hay", "hives", "well"], 3)
            if hs["role"] == "farm":
                things += ["hay", "hay"]
            inner = [(a, b, u, v) for a, b, u, v in yard if all((a + dx, b + dz) in cells for dx in (-1, 0, 1) for dz in (-1, 0, 1))]
            S.rnd.shuffle(inner)
            used = set()
            for t in things:
                for a, b, u, v in inner:
                    if (a, b) in used:
                        continue
                    y = self.g(a, b) + 1
                    if t == "garden":
                        for da in range(-1, 2):
                            for db in range(-1, 2):
                                p = (a + da, b + db)
                                if p in cells and p not in used:
                                    yy = self.g(*p)
                                    S.put(p[0], yy, p[1], "farmland[moisture=7]")
                                    S.put(p[0], yy + 1, p[1], S.pick(("carrots[age=7]", 2), ("potatoes[age=7]", 2), ("beetroots[age=3]", 1),
                                                                      ("wheat[age=7]", 1), ("rose_bush[half=lower]", 0)))
                                    used.add(p)
                    elif t == "woodpile":                  # the Blender woodpile, the chopping block by it
                        self.V.prop("woodpile", a, y, b, hs["face"])
                        used.update({(a + da, b + db) for da in (-1, 0, 1, 2) for db in (-1, 0, 1)})
                    elif t == "tree":
                        self.V.lay_tree(S.rnd.choice(["oak_small_0", "oak_small_1", "blood_small_0", "birch_small_1", "oak_small_2"]), a, b)
                        used.add((a, b))
                    elif t == "line":
                        self.V.prop("washing_line", a, y, b, hs["face"])
                        used.update({(a + da, b + db) for da in (-2, -1, 0, 1, 2) for db in (-2, -1, 0, 1, 2)})
                    elif t == "hay":
                        if hs["role"] == "farm" and "cart" not in used:
                            self.V.prop("hay_cart", a, y, b, S.rnd.choice(("north", "south", "east", "west")))
                            used.add("cart")
                        else:
                            S.put(a, y, b, "hay_block[axis=y]")
                            if S.rnd.random() < 0.5:
                                S.put(a, y + 1, b, "hay_block[axis=x]")
                        used.update({(a + da, b + db) for da in (-1, 0, 1) for db in (-2, -1, 0, 1, 2)})
                    elif t == "hives":
                        self.V.prop("skeps", a, y, b, hs["face"])
                        used.update({(a + da, b + db) for da in (-1, 0, 1) for db in (-1, 0, 1)})
                    elif t == "well":
                        S.put(a, y - 1, b, "water[level=0]")
                        for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            S.put(a + da, y, b + db, "ashbound:greystone_wall")
                        used.add((a, b))
                    break
            # flowers and the odd pot by the door
            for a, b, u, v in yard:
                if (a, b) not in used and S.rnd.random() < 0.12:
                    y = self.g(a, b) + 1
                    if S.get(a, y, b) is None:
                        S.put(a, y, b, S.pick(("short_grass", 6), ("poppy", 1), ("cornflower", 1), ("oxeye_daisy", 1), ("allium", 1)))

    def paths(self):
        S = self.S
        for (a, b), t in self.occ.items():
            if t == "path" and not ((a, b) in self.V.WET and self.deck is not None):
                S.put(a, self.g(a, b), b, S.pick(("ashbound:limestone_flagstones", 3), ("dirt_path", 2), ("gravel", 1)))

    def street_life(self, n=30):
        """Carts, barrels, crates and hay by the roads near the focus; lamp posts along the core's roads."""
        S = self.S
        cells = [p for p, t in self.occ.items() if t is None or t == "road"]
        roadside = [p for p, t in self.occ.items() if t == "road" and self.ring(*p) in ("core", "mid")]
        S.rnd.shuffle(roadside)
        done = 0
        for (a, b) in roadside:
            if done >= n:
                break
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                p = (a + dx, b + dz)
                if self.occ.get(p) is None and p not in self.V.WET and S.get(p[0], self.g(*p) + 1, p[1]) in (None, "short_grass"):
                    y = self.g(*p) + 1
                    t = S.pick(("lamp", 3), ("barrel", 2), ("crate", 1), ("hay", 1), ("bench", 1), ("cart", 2))
                    if t == "lamp":
                        if self.ring(*p) != "core":
                            continue
                        for k in range(3):
                            S.put(p[0], y + k, p[1], "spruce_fence")
                        S.put(p[0], y + 3, p[1], "lantern[hanging=false,waterlogged=false]")
                    elif t == "barrel":
                        S.put(p[0], y, p[1], "barrel[facing=up,open=false]")
                    elif t == "crate":
                        S.put(p[0], y, p[1], "ashbound:produce_crate[facing=%s]" % S.rnd.choice(("north", "east")))
                    elif t == "hay":
                        S.put(p[0], y, p[1], "hay_block[axis=y]")
                    elif t == "cart":                            # a handcart, a barrow or churns left by the way
                        face = ("east" if dx else "south") if (dx > 0 or dz > 0) else ("west" if dx else "north")
                        self.V.prop(S.pick(("handcart", 2), ("wheelbarrow", 2), ("churns_sacks", 2)), p[0], y, p[1], face)
                    else:
                        S.put(p[0], y, p[1], H.stairs("spruce", S.rnd.choice(("north", "south", "east", "west"))))
                    self.occ[p] = "clutter"
                    done += 1
                    break

    def fields(self, n=6, size=(9, 14)):
        """Fenced fields on open land at the edge, long side along the slope's contour, a farm track to them."""
        S = self.S
        x0, z0, x1, z1 = self.box
        made = 0
        for _ in range(400):
            if made >= n:
                break
            w, d = S.rnd.randint(*size), S.rnd.randint(7, 10)
            if S.rnd.random() < 0.5:
                w, d = d, w
            farms = [h for h in self.houses if h["role"] in ("farm", "edge")]
            if farms and S.rnd.random() < 0.85:            # next to a farmstead, beyond its yard
                h = S.rnd.choice(farms)
                cx = sum(a for a, _ in h["cells"]) / len(h["cells"]) + h["out"][0] * S.rnd.randint(10, 20) + S.rnd.randint(-8, 8)
                cz = sum(b for _, b in h["cells"]) / len(h["cells"]) + h["out"][1] * S.rnd.randint(10, 20) + S.rnd.randint(-8, 8)
                a, b = int(cx - w / 2), int(cz - d / 2)
            else:
                a, b = S.rnd.randint(x0 + 3, x1 - w - 3), S.rnd.randint(z0 + 3, z1 - d - 3)
            if not (self.inside(a, b) and self.inside(a + w, b + d)) or self.ring(a + w // 2, b + d // 2) not in ("edge", "out"):
                continue
            cells = [(a + i, b + j) for i in range(w) for j in range(d)]
            if any(self.occ.get((p[0] + dx, p[1] + dz)) for p in cells for dx in (-1, 1) for dz in (-1, 1)):
                continue
            hs = [self.g(*p) for p in cells]
            if max(hs) - min(hs) > 3 or any(p in self.V.WET for p in cells):
                continue
            crop = S.pick(("wheat[age=7]", 4), ("carrots[age=7]", 1), ("potatoes[age=7]", 1), ("beetroots[age=3]", 1))
            for (p, q) in cells:
                y = self.g(p, q)
                self.occ[(p, q)] = "field"
                edge = p in (a, a + w - 1) or q in (b, b + d - 1)
                if edge:
                    S.put(p, y + 1, q, "oak_fence")
                elif (p - a) % 5 == 0 if w > d else (q - b) % 5 == 0:
                    S.put(p, y, q, "water[level=0]")
                else:
                    S.put(p, y, q, "farmland[moisture=7]")
                    S.put(p, y + 1, q, crop)
                for yy in range(y + 2, y + 30):
                    if S.get(p, yy, q):
                        S.put(p, yy, q, None)
            if S.rnd.random() < 0.55:
                self.V.prop("scarecrow", a + w // 2, self.g(a + w // 2, b + d // 2) + 1, b + d // 2, S.rnd.choice(("north", "south", "east", "west")))
            made += 1

    def woods(self, n=40, names=("oak_medium_0", "oak_medium_1", "oak_medium_2", "oak_medium_0", "birch_medium_0", "birch_medium_1",
                                 "oak_small_1", "birch_small_0")):
        """Trees thicker toward the edge: the village sits in a clearing."""
        S = self.S
        x0, z0, x1, z1 = self.box
        made = 0
        for _ in range(3000):
            if made >= n:
                break
            a, b = S.rnd.randint(x0 + 6, x1 - 6), S.rnd.randint(z0 + 6, z1 - 6)
            d = math.hypot(a - self.focus[0], b - self.focus[1])
            if d < self.rings[1] * 0.8 or S.rnd.random() > min(1, (d - self.rings[1] * 0.8) / 30):
                continue
            if any(self.occ.get((a + dx, b + dz)) for dx in range(-5, 6, 2) for dz in range(-5, 6, 2)) or (a, b) in self.V.WET:
                continue
            self.V.lay_tree(S.rnd.choice(names), a, b, k=S.rnd.randint(0, 3))
            self.occ[(a, b)] = "tree"
            self.trees.append((a, b))
            made += 1

    # ------------------------------------------------------------ the plan drawn from above
    def plan_png(self, path, scale=5):
        x0, z0, x1, z1 = self.box
        W, Hh = (x1 - x0 + 1) * scale, (z1 - z0 + 1) * scale
        im = Image.new("RGB", (W, Hh), (120, 150, 95))
        dr = ImageDraw.Draw(im)
        col = {"road": (175, 140, 95), "path": (205, 190, 160), "yard": (150, 175, 110), "focus": (190, 200, 140),
               "field": (215, 195, 110), "landmark": (150, 60, 50), "clutter": (120, 100, 80), "tree": (40, 90, 40)}
        hc = {"core": (180, 70, 60), "mid": (200, 120, 70), "edge": (210, 160, 90), "farm": (160, 120, 80)}
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                g = self.g(x, z)
                c = (70, 110, 160) if (x, z) in self.V.WET else (int(110 + g * 3), int(145 + g * 2), int(90 + g))
                t = self.occ.get((x, z))
                if t in col:
                    c = col[t]
                X, Z = (x - x0) * scale, (z - z0) * scale
                dr.rectangle([X, Z, X + scale - 1, Z + scale - 1], fill=c)
                if g % 4 == 0 and self.g(x + 1, z) != g:
                    dr.rectangle([X, Z, X + 1, Z + scale - 1], fill=(90, 110, 75))
        for hs in self.houses:
            for (a, b) in hs["cells"]:
                X, Z = (a - x0) * scale, (b - z0) * scale
                dr.rectangle([X, Z, X + scale - 1, Z + scale - 1], fill=hc[hs["role"]])
            a, b = hs["door"]
            X, Z = (a - x0) * scale, (b - z0) * scale
            dr.rectangle([X, Z, X + scale - 1, Z + scale - 1], fill=(40, 30, 20))
        for r in self.rings:
            fx, fz = (self.focus[0] - x0) * scale, (self.focus[1] - z0) * scale
            dr.ellipse([fx - r * scale, fz - r * scale, fx + r * scale, fz + r * scale], outline=(255, 255, 255))
        im.save(path)
