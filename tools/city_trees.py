"""Highmourn's own trees, grown from code the way the good builders shape them (not the wildwood's templates, which stay
out in the world): a trunk that flares into roots and tapers, real branches in wood turned along their way, and a crown
of several rounded clusters on the branch tips with gaps between them, shaded in three leaves (the sunlit top, the
leaf body, the shade underneath), so it reads as a tree from the street and not a stack of plates.

    kinds: linden (the streets' green), cherry (blossom), maple (autumn, now and then), birch and willow (by water),
           oak (the big ones out in the meadows)
    grow(kind, size, variant) -> ([(x, y, z, state)] relative to the trunk's foot, y 0 = the ground layer, half-width)

The same list format as capital_green.template, so the planting treats them the same.
"""
import math
import random
import zlib

LEAF = "[distance=7,persistent=true,waterlogged=false]"


def L(name):
    return "ashbound:" + name + LEAF


SPECIES = {
    # bark, (shade, body, sunlit), sprinkle (leaf, chance), shape
    "linden": dict(wood="ashbound:wildwood_wood", moss="ashbound:mossy_wildwood_wood",
                   leaves=(L("wildwood_leaves_shade"), L("wildwood_leaves"), L("wildwood_leaves_sunlit")), sprinkle=None),
    "oak": dict(wood="ashbound:wildwood_wood", moss="ashbound:mossy_wildwood_wood",
                leaves=(L("wildwood_leaves_shade"), L("wildwood_leaves"), L("wildwood_leaves_sunlit")), sprinkle=None),
    "maple": dict(wood="ashbound:wildwood_wood", moss="ashbound:mossy_wildwood_wood",
                  leaves=(L("wildwood_leaves_crimson"), L("wildwood_leaves_crimson"), L("wildwood_leaves_amber")),
                  sprinkle=(L("wildwood_leaves_rose"), 0.06)),
    "cherry": dict(wood="ashbound:wildwood_wood", moss="ashbound:mossy_wildwood_wood",
                   leaves=(L("wildwood_leaves_rose"), L("wildwood_leaves_rose"), L("wildwood_leaves_rose")),
                   sprinkle=(L("wildwood_blossom"), 0.08)),
    "birch": dict(wood="birch_wood", moss="birch_wood",
                  leaves=(L("wildwood_leaves"), L("wildwood_leaves_sunlit"), L("wildwood_leaves_sunlit")),
                  sprinkle=(L("wildwood_leaves_amber"), 0.07)),
    "willow": dict(wood="ashbound:wildwood_wood", moss="ashbound:mossy_wildwood_wood",
                   leaves=(L("wildwood_leaves_shade"), L("wildwood_leaves"), L("wildwood_leaves_sunlit")), sprinkle=None),
}

# size -> (clear trunk under the crown, crown radius, branches)
SIZES = {
    "linden": {"small": (4, 2.8, 3), "medium": (5, 3.8, 4), "large": (6, 5.0, 5)},
    "oak": {"small": (3, 3.2, 3), "medium": (4, 4.6, 5), "large": (5, 6.4, 6)},
    "maple": {"small": (4, 3.0, 3), "medium": (5, 4.0, 4), "large": (6, 5.2, 5)},
    "cherry": {"small": (3, 3.4, 3), "medium": (4, 4.6, 4), "large": (4, 5.8, 5)},
    "birch": {"small": (4, 2.0, 2), "medium": (6, 2.6, 3), "large": (8, 3.2, 3)},
    "willow": {"small": (4, 3.4, 4), "medium": (5, 4.6, 5), "large": (6, 6.0, 6)},
}


class Tree:
    def __init__(self, seed):
        self.r = random.Random(seed)
        self.B = {}
        self.seed = seed

    def wood(self, x, y, z, st, axis="y"):
        k = (round(x), round(y), round(z))
        if k in self.B and "leaves" not in self.B[k] and "blossom" not in self.B[k]:
            return
        self.B[k] = st + "[axis=%s]" % axis

    def leaf(self, k):
        if k not in self.B:
            self.B[k] = "LEAF"

    def limb(self, a, b, st):
        """Wood from a to b, each block turned along the limb's way."""
        dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        n = max(1, int(max(abs(dx), abs(dy), abs(dz)) * 2))
        ax = "y" if abs(dy) >= max(abs(dx), abs(dz)) * 0.8 else ("x" if abs(dx) > abs(dz) else "z")
        for i in range(n + 1):
            t = i / n
            self.wood(a[0] + dx * t, a[1] + dy * t, a[2] + dz * t, st, ax)

    def noise(self, x, y, z):
        s = self.seed * 0.37
        return (math.sin(x * 1.31 + s) + math.sin(z * 1.17 - s * 1.3) + math.sin(y * 1.71 + x * 0.6 + s * 0.7)) / 3

    def blob(self, c, rx, ry, rz, rough=0.28):
        """A rounded cluster of leaves, its surface bumped by a smooth noise (not speckled)."""
        for x in range(int(c[0] - rx - 1), int(c[0] + rx + 2)):
            for y in range(int(c[1] - ry - 1), int(c[1] + ry + 2)):
                for z in range(int(c[2] - rz - 1), int(c[2] + rz + 2)):
                    d = ((x - c[0]) / rx) ** 2 + ((y - c[1]) / ry) ** 2 + ((z - c[2]) / rz) ** 2
                    if d < 1 + rough * self.noise(x, y, z):
                        self.leaf((x, y, z))


def grow(kind, size, variant):
    sp = SPECIES[kind]
    clear, R, nb = SIZES[kind][size]
    t = Tree(zlib.crc32(("%s_%s_%d" % (kind, size, variant)).encode()) & 0xFFFF)
    r = t.r
    wood, moss = sp["wood"], sp["moss"]
    big = size != "small"

    # ---- roots: a flare in the ground layer and one above, stubs reaching out
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        if big or r.random() < 0.5:
            t.wood(dx, 0, dz, moss if r.random() < 0.5 else wood, "x" if dx else "z")
        if big and r.random() < 0.7:
            t.wood(dx * 2, 0, dz * 2, wood, "x" if dx else "z")
        if size == "large" and r.random() < 0.8:
            t.wood(dx, 1, dz, moss if r.random() < 0.4 else wood, "y")

    tips = []
    fork = None
    if kind == "birch":
        # two or three slim stems, each its own narrow crown
        stems = 1 if size == "small" else r.choice((2, 3))
        for s in range(stems):
            a = s / stems * math.tau + r.random()
            lean = 0 if stems == 1 else 0.18
            top = clear + int(R * 2) + r.randint(0, 2) - s
            px, pz = 0.0, 0.0
            for y in range(0, top + 1):
                if y > 1:
                    px, pz = math.cos(a) * lean * (y - 1), math.sin(a) * lean * (y - 1)
                t.wood(px, y, pz, wood)
            tips.append(((px, top - R * 0.6, pz), R * 0.85, R * 1.3, R * 0.85))
            tips.append(((px + math.cos(a) * 0.8, top - R * 1.6, pz + math.sin(a) * 0.8), R * 0.9, R * 0.8, R * 0.9))
    else:
        # ---- the trunk: straight-ish with a slight lean, splitting into branches at the crown's foot
        lean = r.uniform(0, math.tau)
        lx, lz = math.cos(lean) * 0.12, math.sin(lean) * 0.12
        fork = clear + (1 if kind in ("linden", "maple") else 0)
        top = (0.0, 0.0)
        for y in range(0, fork + 1):
            top = (lx * y, lz * y)
            t.wood(top[0], y, top[1], moss if y < 2 and r.random() < 0.5 else wood)
        if size == "large" or (size == "medium" and kind in ("oak", "willow")):   # a thick old foot: a flare round it
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                hgt = r.randint(1, 2 if size == "medium" else 3)
                for y in range(0, hgt + 1):
                    t.wood(dx, y, dz, moss if r.random() < 0.35 else wood)
        base = (top[0], fork, top[1])
        # the leader carries on up for the tall kinds
        if kind in ("linden", "maple", "oak", "willow"):
            lead = (base[0] + lx * 3, fork + R * (0.9 if kind != "oak" else 0.6), base[2] + lz * 3)
            t.limb(base, lead, wood)
            tips.append((lead, R * 0.75, R * 0.6, R * 0.75))
        spread = {"cherry": 1.15, "oak": 1.05, "willow": 0.9}.get(kind, 0.75)
        rise = {"cherry": 0.45, "oak": 0.5, "willow": 0.6}.get(kind, 0.9)
        a0 = r.uniform(0, math.tau)
        for i in range(nb):
            a = a0 + i / nb * math.tau + r.uniform(-0.35, 0.35)
            start_y = fork - (r.uniform(0, 1.2) if kind in ("cherry", "oak") else 0)
            s = (base[0], start_y, base[2])
            ln = R * spread * r.uniform(0.8, 1.1)
            e = (s[0] + math.cos(a) * ln, s[1] + ln * rise + r.uniform(0, 1), s[2] + math.sin(a) * ln)
            mid = (s[0] + (e[0] - s[0]) * 0.55, s[1] + (e[1] - s[1]) * 0.35, s[2] + (e[2] - s[2]) * 0.55)
            t.limb(s, mid, wood)
            t.limb(mid, e, wood)
            tips.append((e, R * 0.62, R * (0.5 if kind == "cherry" else 0.42 if kind == "willow" else 0.62), R * 0.62))

    # ---- the crown: a cluster on every tip, a body joining them so it reads as one canopy with notches
    for c, rx, ry, rz in tips:
        t.blob(c, rx, ry, rz)
    if kind != "birch":
        cy = sum(c[1] for c, *_ in tips) / len(tips)
        body = 0.72 if kind != "cherry" else 0.8
        t.blob((0, cy, 0), R * body, R * (0.4 if kind == "willow" else 0.55), R * body, rough=0.2)
        if kind == "cherry":                                        # a soft dome over the spread
            t.blob((0, cy + R * 0.45, 0), R * 0.55, R * 0.45, R * 0.55, rough=0.25)

    leaves = [k for k, v in t.B.items() if v == "LEAF"]

    # ---- the willow's curtains: single strands off the crown's rim, of many lengths, ending well above the ground
    if kind == "willow":
        ys = [k[1] for k in leaves]
        floor = min(ys)
        top = max(ys)
        rim = [k for k in leaves if math.hypot(k[0], k[2]) > R * 0.7]
        seen = set()
        for k in sorted(rim, key=lambda k: k[1]):
            if (k[0], k[2]) in seen:
                continue
            seen.add((k[0], k[2]))
            if (k[0] * 7 + k[2] * 13 + (k[0] * k[2])) % 3:
                continue
            below = (k[0], k[1] - 1, k[2])
            if below in t.B:
                continue
            n = r.randint(max(2, int(k[1] * 0.35)), max(3, int(k[1] - 2)))
            for j in range(1, n + 1):
                if k[1] - j < 2:
                    break
                t.leaf((k[0], k[1] - j, k[2]))
        leaves = [k for k, v in t.B.items() if v == "LEAF"]

    # ---- trim: no lone leaves (they read as noise), nothing under head height over the trunk's walk
    def nbrs(k):
        return sum((k[0] + dx, k[1] + dy, k[2] + dz) in t.B for dx, dy, dz in
                   ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)))
    for _ in range(2):
        for k in [k for k, v in t.B.items() if v == "LEAF" and nbrs(k) < 2 and kind != "willow"]:
            del t.B[k]
    low = 3 if size == "small" else 4
    for k in [k for k, v in t.B.items() if v == "LEAF" and k[1] < low and kind not in ("willow",)]:
        del t.B[k]
    # a bowl under the crown: high by the trunk, low at the rim, so the limbs are seen leaving the trunk
    if fork is not None:
        lift = 1.5 if kind in ("linden", "maple", "oak") else 0.8
        for k in [k for k, v in t.B.items() if v == "LEAF"]:
            d = math.hypot(k[0], k[2]) / R
            if kind == "willow" and d > 0.68:
                continue
            if k[1] < fork + lift - d * 2.2:
                del t.B[k]

    # ---- shade: the sunlit leaves where the sky sees them, the shade underneath and deep inside, the body between
    shade, body, sun = sp["leaves"]
    out = []
    for k, v in t.B.items():
        if v != "LEAF":
            out.append((k[0], k[1], k[2], v))
            continue
        sky = all((k[0], k[1] + j, k[2]) not in t.B for j in range(1, 4))
        under = (k[0], k[1] - 1, k[2]) not in t.B and (k[0], k[1] + 1, k[2]) in t.B
        h = (k[0] * 73856093 ^ k[1] * 19349663 ^ k[2] * 83492791) & 1023
        if sky and h % 10 < 8:
            st = sun
        elif under or (nbrs(k) == 6 and h % 4 == 0):
            st = shade
        else:
            st = body
        if sp["sprinkle"] and h / 1024 < sp["sprinkle"][1]:
            st = sp["sprinkle"][0]
        out.append((k[0], k[1], k[2], st))
    rr = max(max(abs(x), abs(z)) for x, _, z, _ in out)
    return out, rr


KINDS = ("linden", "cherry", "maple", "birch", "willow", "oak")

if __name__ == "__main__":
    for k in KINDS:
        for s in ("small", "medium", "large"):
            b, rr = grow(k, s, 0)
            print(k, s, len(b), "r", rr, "h", max(y for _, y, _, _ in b))
