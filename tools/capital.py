"""Highmourn, the capital: a walled city round a lake in a mountain valley (one per world, 1,500-3,000 blocks from
spawn).

    python tools/capital.py              -> src/main/resources/data/ashbound/capital/highmourn.bin
    python tools/capital.py --preview    also a top-down map (tools/renders/capital_plan.png)

The land and the city are one: capital_land.py decides the ground's height in every column round the city and the
game sinks that shape into the world while it's made (Capital.java, through the beardifier), easing it back into the
world's own land out past the summits; then it lays the blocks made here. Heights are relative to the valley floor
(Capital.FLOOR in the game); x east, z south, the city's centre at 0, 0, the gate to the south.

    capital_land.py    the ground, the lake, the river, the mountains
    capital_walls.py   the wall, its towers, the gatehouse and barbican
    capital_pair.py    the angel and the devil at the valley's throat
"""
import collections
import json
import gzip
import os
import struct
import sys

sys.path.insert(0, "E:/Ashbound/tools")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import structkit as K  # noqa: E402
import city_highmourn as CH  # noqa: E402
import capital_land as L  # noqa: E402
import capital_walls as WL  # noqa: E402
import capital_pair as PR  # noqa: E402

GAME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(GAME, "src", "main", "resources", "data", "ashbound", "capital", "highmourn.bin")

S = K.Build(41)
put, box, pick = S.put, S.box, S.pick
CH.S, CH.put, CH.box, CH.pick = S, put, box, pick
WL.S, WL.put, WL.pick = S, put, pick
PR.S, PR.put, PR.pick = S, put, pick

WATER = "water[level=0]"
FALLING = "water[level=8]#flow"
RENAME = {"minecraft:iron_chain": "minecraft:chain", "iron_chain": "chain"}
noise = L.noise

# ================================================================ the ground's grid

H = {}                       # (x, z) -> the column's height, for the builders (inside the shaped area)


def grid():
    x0, z0, W, D = L.GRID
    T = bytearray(2 * W * D)
    M = bytearray(W * D)
    Wt = bytearray(W * D)
    Bl = bytearray(W * D)
    Bi = bytearray(W * D)
    hs = [0] * (W * D)
    todo = []
    for j in range(D):
        z = z0 + j
        for i in range(W):
            x = x0 + i
            h, mode, w, b, biome = L.ground(x, z)
            k = j * W + i
            hs[k] = h
            struct.pack_into(">h", T, 2 * k, max(-32000, min(32000, h)))
            M[k] = mode
            Wt[k] = int(round(w * 255))
            Bl[k] = int(round(b * 255))
            if biome is None:
                todo.append(k)
            else:
                Bi[k] = biome
        if j % 100 == 0:
            print("  ground row %d/%d" % (j, D))
    # the slopes' biomes, from how steep and how high they are (the blended edge keeps the world's own)
    for k in todo:
        if Bl[k] > 128:
            continue
        i, j = k % W, k // W
        if 2 <= i < W - 2 and 2 <= j < D - 2:
            slope = max(abs(hs[k + 2] - hs[k - 2]), abs(hs[k + 2 * W] - hs[k - 2 * W])) / 4.0
        else:
            slope = 0.0
        Bi[k] = L.biome_for(hs[k], slope, x0 + i, z0 + j)
    for j in range(D):
        for i in range(W):
            H[(x0 + i, z0 + j)] = hs[j * W + i]
    import pickle
    with open(os.path.join(GAME, "tools", "renders", "capital_ground.pkl"), "wb") as f:
        pickle.dump((L.GRID, hs, bytes(Bi), bytes(M)), f)
    return T, M, Wt, Bl, Bi


# ================================================================ water

def water():
    x0, z0, W, D = L.GRID
    n = 0
    for (x, z), h in H.items():
        e = L.edist(x, z)
        if e > 330:
            continue
        inside = e < 2
        if inside and L.lake_s(x, z) < 1 and L.island_s(x, z) >= 1:
            # the bed: shingle in the shallows (sand in the coves), clay and gravel out in the deep
            cove = noise(x, z, 40, 72) > 0.66
            if h >= -4:
                bed = "sand" if cove else pick(("gravel", 4), ("stone", 1), ("andesite", 1))
            else:
                bed = pick(("gravel", 3), ("clay", 2), ("mud", 1))
            put(x, h, z, bed)
            put(x, h - 1, z, "gravel" if bed != "sand" else "sand")
            for y in range(h + 1, L.WATER_Y + 1):
                put(x, y, z, WATER)
            if L.WATER_Y - h >= 2 and noise(x, z, 4, 74) > 0.7:
                put(x, h + 1, z, "seagrass")
            elif L.WATER_Y - h == 1 and noise(x, z, 5, 75) > 0.8:
                put(x, L.WATER_Y + 1, z, "lily_pad")
            n += 1
        elif inside and L.lake_s(x, z) < 1 and L.island_s(x, z) < 1:
            k = 1 - L.island_s(x, z)
            if k < 0.22:
                # the island's rocky foot: shingle and boulders at the waterline
                for y in range(h - 2, h + 1):
                    put(x, y, z, pick(("stone", 3), ("andesite", 2), ("gravel", 2), ("moss_block", 1 if y == h else 0)))
                if h < L.WATER_Y:
                    for y in range(h + 1, L.WATER_Y + 1):
                        put(x, y, z, WATER)
                elif noise(x, z, 2.0, 91) > 0.8:
                    put(x, h + 1, z, pick(("stone", 2), ("andesite", 1), ("moss_block", 1)))
        elif inside and 1 <= L.lake_s(x, z) < 1.075 and L.QUAY(x, z) is None:
            # the shore: a strip of shingle and boulders between the water and the grass, sandy in the coves,
            # reeds where it's soft; the grass takes over raggedly further up
            s = L.lake_s(x, z)
            reach = 1.006 + 0.07 * noise(x, z, 23, 70) ** 1.5           # how far up the shingle runs here
            if s > reach or noise(x, z, 3, 73) < (s - reach + 0.02) / 0.02:
                if s < 1.012 and noise(x, z, 3, 76) > 0.6:
                    for y in range(h + 1, h + 2 + int(noise(x, z, 1.0, 77) * 3)):
                        put(x, y, z, "sugar_cane")                         # reeds where the grass meets the water
                continue
            cove = noise(x, z, 40, 72) > 0.66
            top = "sand" if cove else pick(("gravel", 5), ("stone", 2), ("andesite", 2), ("moss_block", 1 if s > 1.03 else 0))
            for y in range(h - 2, h + 1):
                put(x, y, z, top if y == h else "sand" if cove else pick(("gravel", 2), ("stone", 1)))
            near = L.lake_s(x, z) < 1.015
            if cove and near and noise(x, z, 3, 76) > 0.55:
                for y in range(h + 1, h + 2 + int(noise(x, z, 1.0, 77) * 3)):
                    put(x, y, z, "sugar_cane")
            elif not cove and noise(x, z, 2.2, 78) > 0.86:
                for dx, dy, dz in ((0, 1, 0), (1, 1, 0), (0, 1, 1), (0, 2, 0), (-1, 1, 0)):
                    if (dx, dy, dz) == (0, 2, 0) or noise(x + dx, z + dz, 1.0, 79) > 0.3:
                        put(x + dx, h + dy, z + dz, pick(("stone", 3), ("andesite", 2), ("moss_block", 1 if dy == 2 else 0)))
        elif L.in_pool(x, z):
            put(x, h, z, "gravel")
            for y in range(h + 1, L.CITADEL):
                put(x, y, z, WATER)
        elif not inside and L.lake_s(x, z, L.LOWER_LAKE, 0.18, 44) < 1:
            put(x, h, z, "sand" if h >= -6 else "gravel")
            for y in range(h + 1, L.WATER_OUT + 1):
                put(x, y, z, WATER)
    # the quay: flagstones along the shore below the lower city, a dressed edge down into the water, lamp posts and
    # bollards along it, steps down to the water in the middle
    for x in range(10, 66):
        for z in range(50, 110):
            q = L.QUAY(x, z)
            if q is None or q < 1:
                continue
            edge = L.lake_s(x - 1, z - 1) < 1 or L.lake_s(x, z - 1) < 1 or L.lake_s(x + 1, z) < 1 or L.lake_s(x - 1, z) < 1
            for y in range(-6, 1):
                put(x, y, z, "deepslate_bricks" if edge else "gravel")
            if edge:
                put(x, 0, z, "polished_deepslate")
                if x % 8 == 0:
                    put(x, 1, z, "polished_blackstone_wall")
                    put(x, 2, z, "polished_blackstone_wall")
                    put(x, 3, z, "lantern[hanging=false,waterlogged=false]")
                elif x % 8 == 4:
                    put(x, 1, z, "deepslate_brick_wall")
            else:
                put(x, 0, z, pick(("ashbound:limestone_flagstones", 6), ("polished_andesite", 1)))
            for y in range(1, 4):
                if S.get(x, y, z) is None:
                    put(x, y, z, "air")
    # the river: into the lake down over the tiers, out of it through the valley, rocky banks along it
    for pts, out in ((L.RIVER_IN, False), (L.RIVER_OUT, True)):
        xs = [p[0] for p in pts]
        zs = [p[1] for p in pts]
        for x in range(min(xs) - 9, max(xs) + 10):
            for z in range(min(zs) - 9, max(zs) + 10):
                if (x, z) not in H:
                    continue
                inside = L.edist(x, z) < 2
                if inside and L.lake_s(x, z) < 1:
                    continue
                if L.lake_s(x, z, L.LOWER_LAKE, 0.18, 44) < 1 or L.in_pool(x, z):
                    continue
                rd = L.poly_d(x, z, pts)
                hw = L.river_hw(x, z, out)
                if rd > hw + 1 or (out and z <= 120 and not inside):
                    continue
                if not inside and z < 0:
                    lvl = L.CITADEL - 1
                else:
                    lvl = round(L.tier_h(x, z, True)) - 1 if inside else L.WATER_OUT
                bottom = H[(x, z)]
                in_moat = L.moat_d(x, z) is not None and L.floor_d(x, z) < 0
                if out and not inside and L.edist(x, z) < 3.5:
                    # the weir just outside the water gate: the city's water spills over a dressed lip down to the
                    # moat and the river beyond, two blocks lower
                    if rd <= hw:
                        for y in range(bottom, -1):
                            put(x, y, z, "polished_deepslate" if y == -2 else "deepslate_bricks")
                        put(x, -1, z, WATER + "#flow")
                    continue
                if in_moat:
                    continue                         # the moat's own (the river runs straight into it)
                if rd > hw:                          # the bank: rough stone up to the ground
                    for y in range(bottom, lvl + 2):
                        put(x, y, z, pick(("stone", 4), ("andesite", 2), ("mossy_stone_bricks", 1 if y < lvl else 0), ("gravel", 1)))
                    continue
                put(x, bottom, z, "gravel")
                for y in range(bottom + 1, lvl + 1):
                    put(x, y, z, WATER)
    # the falls: water on each ledge of the notch, a falling sheet down each drop to the next, rocks along it
    fp = L.falls_path()
    prev = None
    for z in range(L.FALLS_Z0, L.FALLS_Z1 + 1):
        cx, w, lvl, bed = fp[z]
        for x in range(int(cx - w - 1), int(cx + w + 2)):
            if abs(x + 0.5 - cx) > w:
                continue
            split = prev is not None and prev - lvl > 6 and abs(x + 0.5 - cx) < 1.2 and noise(0, lvl, 1.0, 90) > 0.45
            if split:
                # a rock standing up out of the drop, parting the water into two falls
                for y in range(bed, min(prev, lvl + 5) + 1):
                    put(x, y, z, pick(("stone", 3), ("andesite", 2), ("mossy_stone_bricks", 1)))
                put(x, min(prev, lvl + 5) + 1, z, "moss_block")
                continue
            put(x, bed, z, pick(("stone", 3), ("mossy_stone_bricks", 1), ("andesite", 1), ("gravel", 1)))
            put(x, lvl, z, WATER)
            if prev is not None and prev > lvl:
                for y in range(lvl + 1, prev + 1):
                    put(x, y, z, FALLING)
        # boulders on the ledges' lips, either side of the water
        if noise(0, z, 2.3, 86) > 0.62:
            sx = 1 if noise(z, 1, 3, 87) > 0.5 else -1
            bx = int(cx + sx * (w + 1.5))
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    for dy in (0, 1):
                        if abs(dx) + abs(dz) + dy <= 2:
                            put(bx + dx, lvl + dy, z + dz, pick(("moss_block", 1 if dy else 0),
                                                              ("andesite", 2), ("stone", 3), ("mossy_stone_bricks", 1)))
        prev = lvl
    # the last drop into the pool
    cx, w, lvl, bed = fp[L.FALLS_Z1]
    for x in range(int(cx - w), int(cx + w) + 1):
        for y in range(L.CITADEL, lvl + 1):
            if S.get(x, y, L.FALLS_Z1 + 1) is None:
                put(x, y, L.FALLS_Z1 + 1, FALLING)
    print("water: %d lake columns" % n)


# ================================================================ nothing left hanging on air

SIDE = {"north": (0, 0, -1), "south": (0, 0, 1), "east": (1, 0, 0), "west": (-1, 0, 0)}
CHAIN = "chain[axis=y,waterlogged=false]"
N26 = [(dx, dy, dz) for dx in (-1, 0, 1) for dy in (-1, 0, 1) for dz in (-1, 0, 1) if dx or dy or dz]


LOG = None


SCULPTED = set(json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "renders", "sculpt_pieces.json"))))


def unfloat():
    """The last pass over the whole city, so nothing in the game hangs on air: lights stood on nothing hang on a
    chain from what's over them (or go), a wall light or torch with no wall goes, as do plants, candles and carpets
    on nothing and vines touching nothing; then any little clump of blocks touching nothing at all (not the land,
    not the water, not another block, corners counted) goes. Bigger clumps are only reported: those are a builder's
    mistake to fix there."""
    B = S.B

    def name(st):
        return K.short(K.parse(st)[0]) if st else None

    def solid(p):
        st = B.get(p)
        if st is None:
            h = H.get((p[0], p[2]))
            return h is not None and p[1] <= h
        return K._base(st)

    def post(p):
        n = name(B.get(p)) or ""
        return solid(p) or n.endswith(("_fence", "_wall", "chain", "iron_bars")) or n in ("lantern",)

    def hang(p):
        x, y, z = p
        for k in range(1, 9):
            q = (x, y + k, z)
            if solid(q):
                for j in range(1, k):
                    B[(x, y + j, z)] = CHAIN
                return True
            if B.get(q) not in (None, "air"):
                return False
        return False

    def own(p, props):
        """A vine holds by a face it's on, or by its column: the vine over it, if that one holds."""
        x, y, z = p
        return any(solid((x + d[0], y, z + d[2])) for f, d in SIDE.items() if props.get(f) == "true") or             (props.get("up") == "true" and solid((x, y + 1, z)))

    def clings(p, props):
        x, y, z = p
        while True:
            if own((x, y, z), props):
                return True
            st = B.get((x, y + 1, z))
            if name(st) != "vine":
                return False
            y += 1
            props = K.parse(st)[1]

    def reface(p, props):
        """A vine on a curved wall facing past it: turn it onto the side it touches."""
        x, y, z = p
        on = [f for f, d in SIDE.items() if solid((x + d[0], y, z + d[2]))]
        if not on:
            return False
        B[p] = "vine[east=%s,north=%s,south=%s,up=false,west=%s]" % tuple(
            "true" if f in on else "false" for f in ("east", "north", "south", "west"))
        return True

    def slide(p, st, props):
        """A wall light hung on a window: along the wall to the first stone beside it."""
        d = SIDE.get(props.get("facing", "north"), (0, 0, 1))
        t = (d[2], 0, d[0])
        for k in (1, -1, 2, -2):
            q = (p[0] + t[0] * k, p[1], p[2] + t[2] * k)
            if B.get(q) is None and solid((q[0] - d[0], q[1], q[2] - d[2])) and not solid(q):
                del B[p]
                B[q] = st
                return True
        return False

    gone, hung, moved = collections.Counter(), 0, 0
    for _ in range(6):
        drop = []
        for p, st in B.items():
            if st == "air" or st.startswith("water"):
                continue
            k, n, props = K._kind(st)
            x, y, z = p
            below, above = (x, y - 1, z), (x, y + 1, z)
            if n == "wall_lantern" or k in ("wall_torch", "wall_banner", "wall_sign") or n.endswith("wall_lantern"):
                d = SIDE.get(props.get("facing", "north"), (0, 0, 1))
                if not solid((x - d[0], y, z - d[2])):
                    drop.append(p)
            elif k == "lantern":
                if props.get("hanging") == "true":
                    if not (solid(above) or name(B.get(above)) in ("chain", "iron_chain")):
                        drop.append(p)
                elif not post(below):
                    drop.append(p)
            elif k in ("torch", "candle", "cross", "flat") or n == "snow":
                bn = name(B.get(below))
                if not (solid(below) or bn == n or (k in ("candle", "flat") and post(below))
                        or (n in ("lily_pad",) and (B.get(below) or "").startswith("water"))
                        or (k == "cross" and (B.get(below) or "").startswith("water"))):
                    drop.append(p)
            elif n == "vine":
                if not clings(p, props):
                    drop.append(p)
        if not drop:
            break
        for p in drop:
            st = B[p]
            if LOG is not None:
                LOG.append((p, st))
            k, n, props = K._kind(st)
            if n == "wall_lantern" and slide(p, st, props):
                moved += 1
                continue
            if n == "vine" and reface(p, props):
                moved += 1
                continue
            if k == "lantern" and n == "lantern" and hang(p):
                B[p] = "lantern[hanging=true,waterlogged=false]"
                hung += 1
                continue
            gone[n] += 1
            del B[p]
    # reeds only stand with water by their roots (the game pops them otherwise): the rest become tall grass
    cane = lambda q: name(B.get(q)) == "sugar_cane"
    for p in [p for p, st in B.items() if "sugar_cane" in st and not cane((p[0], p[1] - 1, p[2]))]:
        x, y, z = p
        if any((B.get((x + dx, y - 1, z + dz)) or "").startswith("water") for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            continue
        k = 0
        while cane((x, y + k, z)):
            del B[(x, y + k, z)]
            k += 1
        if k >= 2:
            B[(x, y, z)], B[(x, y + 1, z)] = "tall_grass[half=lower]", "tall_grass[half=upper]"
        else:
            B[(x, y, z)] = "short_grass"
        gone["reeds"] += 1
    # clumps touching nothing: everything reached from the land or the water stays
    keep = set()
    q = collections.deque()
    for p, st in B.items():
        if st == "air":
            continue
        h = H.get((p[0], p[2]))
        if h is None or p[1] <= h + 1 or st.startswith("water") or st.split("[", 1)[0][9:] in SCULPTED:
            keep.add(p)                                        # (the sculpted props float on purpose: crystals)
            q.append(p)
    while q:
        x, y, z = q.popleft()
        for dx, dy, dz in N26:
            r = (x + dx, y + dy, z + dz)
            if r not in keep and r in B and B[r] != "air":
                keep.add(r)
                q.append(r)
    loose = {p for p, st in B.items() if st != "air" and p not in keep and K._kind(st)[0] is not None}
    big = []
    while loose:
        g, todo = [], [loose.pop()]
        while todo:
            p = todo.pop()
            g.append(p)
            for d in N26:
                r = (p[0] + d[0], p[1] + d[1], p[2] + d[2])
                if r in loose:
                    loose.remove(r)
                    todo.append(r)
        if len(g) <= 60:
            for p in g:
                gone["clump"] += 1
                del B[p]
        else:
            big.append((len(g), min(g)))
    print("unfloat: %d hung on chains, %d moved onto their wall, gone %s" % (hung, moved, dict(gone.most_common())))
    for n, p in sorted(big, reverse=True):
        print("  STILL FLOATING: %d blocks at %s" % (n, p))


# ================================================================ export

def export(T, M, Wt, Bl, Bi, points):
    pal, idx, rows = [], {}, []
    K.connect(S)
    for (x, y, z), st in S.B.items():
        flow = st.endswith("#flow")
        st0 = st[:-5] if flow else st
        n, props = K.parse(st0)
        n = RENAME.get(n, n)
        if ":" not in n:
            n = "minecraft:" + n
        st = K.fmt(n, props) + ("#flow" if flow else "")
        if st not in idx:
            idx[st] = len(pal)
            pal.append(st)
        rows.append((x >> 4, z >> 4, x, y, z, idx[st]))
    rows.sort()
    x0, z0, W, D = L.GRID
    buf = bytearray(b"CAPT")
    buf += struct.pack(">iiiii", 2, x0, z0, W, D)
    buf += T + M + Wt + Bl + Bi
    buf += struct.pack(">i", len(pal))
    for st in pal:
        e = st.encode("utf-8")
        buf += struct.pack(">H", len(e)) + e
    buf += struct.pack(">i", len(points))
    for k, v in points.items():
        e = k.encode("utf-8")
        buf += struct.pack(">H", len(e)) + e + struct.pack(">ddd", *v)
    buf += struct.pack(">i", len(rows))
    for r in rows:
        buf += struct.pack(">hhhH", r[2], r[3], r[4], r[5])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with gzip.open(OUT, "wb", compresslevel=6) as f:
        f.write(bytes(buf))
    print("highmourn: %d blocks, %d states, %d KB" % (len(rows), len(pal), os.path.getsize(OUT) // 1024))


def preview(T, M, Bi):
    """A top-down map: the shaped ground shaded by height and tinted by biome, the city's blocks over it by their top."""
    from PIL import Image
    x0, z0, W, D = L.GRID
    img = Image.new("RGB", (W, D))
    px = img.load()
    tops = {}
    for (x, y, z), st in S.B.items():
        if st == "air":
            continue
        if (x, z) not in tops or y > tops[(x, z)][0]:
            tops[(x, z)] = (y, st)
    tint = {L.B_PLAINS: (110, 160, 80), L.B_MEADOW: (140, 175, 90), L.B_FOREST: (60, 115, 55), L.B_CHERRY: (215, 140, 170),
            L.B_GROVE: (70, 100, 80), L.B_SNOWY: (235, 238, 245), L.B_STONY: (130, 128, 125), L.B_FLOWERS: (120, 150, 70),
            L.B_JAGGED: (220, 225, 235), L.B_KEEP: (60, 60, 70)}
    for j in range(D):
        for i in range(W):
            k = j * W + i
            h = struct.unpack_from(">h", T, 2 * k)[0]
            hw = struct.unpack_from(">h", T, 2 * (k - 1))[0] if i else h
            shade = max(0.55, min(1.45, 1 + (h - hw) * 0.12))
            c = tint.get(Bi[k], (90, 90, 90)) if M[k] & 3 else (40, 40, 40)
            t = tops.get((x0 + i, z0 + j))
            if t:
                st = t[1]
                c = ((70, 120, 190) if st.startswith("water") else (180, 85, 60) if "clay" in st else (225, 205, 150) if "gilded" in st
                     else (230, 220, 190) if "statue" in st or "limestone" in st else (210, 200, 150) if st.startswith("sand")
                     else (150, 146, 138))
            px[i, j] = tuple(min(255, int(v * shade)) for v in c)
    out = os.path.join(GAME, "tools", "renders", "capital_plan.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    img.save(out)
    print("preview:", out)
    import pickle
    with open(os.path.join(GAME, "tools", "renders", "capital_tops.pkl"), "wb") as f:
        pickle.dump(tops, f)


def homestead_ground(T, M, Wt, Bl, Bi):
    """The homestead's levelled ground into the land grid, so the game shapes the hill to it (no half-cut trees, no
    grass floating where the shelf was cut) and keeps it the city's own: CLEAR (no trees, no caves), meadow. Round it
    a margin kept clear too, at the land's own height."""
    x0, z0, W, D = L.GRID
    n = m = 0
    for (x, z), h in HM.GROUND.items():
        i, j = x - x0, z - z0
        if 0 <= i < W and 0 <= j < D:
            k = j * W + i
            struct.pack_into(">h", T, 2 * k, h)
            M[k] = L.MODE_CUT_FILL | L.CLEAR
            Wt[k], Bl[k], Bi[k] = 255, 0, L.B_MEADOW
            H[(x, z)] = h
            n += 1
    for j in range(D):
        z = z0 + j
        for i in range(W):
            x = x0 + i
            if (x, z) not in HM.GROUND and HM.near(x, z, 24) and Wt[j * W + i]:
                M[j * W + i] |= L.CLEAR
                Bi[j * W + i] = L.B_MEADOW
                m += 1
    print("  homestead ground: %d columns shaped, %d round it kept clear" % (n, m))


if __name__ == "__main__":
    T, M, Wt, Bl, Bi = grid()
    water()
    WL.build(lambda x, z: H.get((x, z), 0))
    PR.build(lambda x, z: H.get((x, z), 0))
    import capital_home as HM                         # (patches structkit so panes join honeystone, before any are joined)
    import capital_city as CY
    CY.S, CY.put, CY.pick = S, S.put, S.pick
    PR.S, PR.put, PR.pick = S, S.put, S.pick
    CY.build(lambda x, z: H.get((x, z), 0))
    HM.build(S, lambda x, z: H.get((x, z), 0))       # the player's manor on the north-west hillside (pass 16)
    homestead_ground(T, M, Wt, Bl, Bi)
    print("built: %d blocks" % len(S.B))
    unfloat()
    import capital_green
    _bare = capital_green.Green.bare
    capital_green.Green.bare = lambda G, x, z: not HM.near(x, z) and _bare(G, x, z)   # no trees on the manor's cut
    capital_green.plant(S, H, S.marks)
    import capital_cast
    capital_cast.keep(S, CY.ROADS, H)
    capital_cast.cast(S, CY.ROADS, CY.GROUND)
    export(T, M, Wt, Bl, Bi, {"gate": (0.5, 1, 380.5), "plaza": (-1.5, 1, 160.5)})
    if "--preview" in sys.argv:
        preview(T, M, Bi)
