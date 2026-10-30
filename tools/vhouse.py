"""Village houses COMPOSED, not stamped (docs/VILLAGES.md rule 4): a main block of its own size, one or two storeys,
its roof gable-on or eaves-on to the road, plus 0-2 additions - a wing (the L), a lean-to (a woodshed or a closed
store), a porch over the door, a barn joined on (farmsteads). Walls, roofs and interiors from the capital's kit
(houses.py, E:/Ashbound/tools) so the villages read as the same world.

    compose(S, x0, z0, face, role, pal) -> dict(cells, door, W, D, top)
        role: "core" (2 storeys, tight), "mid", "edge" (small, 1 storey), "farm" (a barn joined on)
        pal:  the village's palette: dict(cols, roofs, woods, shutters, stone) as weighted tuples
    python tools/vhouse.py   -> a sheet of 16 rolls, E:/Ashbound/tools/renders/struct/vil_houses.obj (+ shots)
"""
import os
import sys

sys.path.insert(0, "E:/Ashbound/tools")
import houses as H  # noqa: E402
import structkit as K  # noqa: E402

PAL = dict(cols=(("plaster", 4), ("ochre_plaster", 3), ("rose_plaster", 1), ("slate_plaster", 2)),
           roofs=(("ashbound:clay_roof_tile", 3), ("ashbound:wood_shingle", 4), ("ashbound:slate_shingle", 2)),
           woods=(("spruce", 3), ("oak", 2), ("dark_oak", 2)), shutters=H.SHUTTERS)


class Sub:
    """A part's own frame inside the house's: (lx, y, lz) offset by (ox, oz); quacks like houses.Frame."""

    def __init__(self, F, ox, oz, w, d):
        self.P, self.S, self.ox, self.oz, self.w, self.d, self.k = F, F.S, ox, oz, w, d, 0

    def put(self, lx, y, lz, st):
        self.P.put(lx + self.ox, y, lz + self.oz, st)

    def get(self, lx, y, lz):
        return self.P.get(lx + self.ox, y, lz + self.oz)

    def free(self, lx, y, lz):
        b = self.get(lx, y, lz)
        return b is None or b == "air"

    def box(self, a0, y0, b0, a1, y1, b1, st):
        for a in range(min(a0, a1), max(a0, a1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for b in range(min(b0, b1), max(b0, b1) + 1):
                    self.put(a, y, b, st)


class Local:
    """The house built facing south at the origin (a Frame that doesn't turn), into its own Build."""

    def __init__(self, rnd):
        self.S = K.Build()
        self.S.rnd = rnd
        self.k = 0

    def put(self, lx, y, lz, st):
        self.S.put(lx, y, lz, st)

    def get(self, lx, y, lz):
        return self.S.get(lx, y, lz)

    def free(self, lx, y, lz):
        b = self.get(lx, y, lz)
        return b is None or b == "air"


def plan(rnd, mw, md, door):
    """A ground floor laid out for the kit's lay(): the bed and chest at the back, the hearth and the kitchen along a
    side, the table and chairs in the middle, a rug before the door; the door's cell and the one inside it clear."""
    w, d = mw - 2, md - 2
    g = [["." for _ in range(w)] for _ in range(d)]
    dx = door - 1
    keep = {(dx, d - 1), (dx, d - 2)}

    def put(x, z, ch):
        if 0 <= x < w and 0 <= z < d and (x, z) not in keep and g[z][x] == ".":
            g[z][x] = ch
            return True
        return False
    left = rnd.random() < 0.5
    bx = 0 if left else w - 1
    put(bx, 0, "H")
    put(bx, 1, "F")
    put(bx + (1 if left else -1), 0, rnd.choice("CnU"))
    kx = w - 1 if left else 0
    for z, ch in zip(range(0, d - 1), rnd.sample("KOQWBbJS", min(4, d - 1))):
        put(kx, z, ch)
    if w >= 4 and d >= 4:
        tx, tz = w // 2, d // 2 - (1 if d > 5 else 0)
        if put(tx, tz, "T"):
            for cx, cz in ((tx - 1, tz), (tx + 1, tz)):
                put(cx, cz, "h")
    put(dx, d - 3, "r")
    for z in range(d):
        for x in range(w):
            if g[z][x] == "." and rnd.random() < 0.06 and (x in (0, w - 1)):
                g[z][x] = "p"
    return ["".join(r) for r in g]


def compose(S, x0, z0, face, role="mid", pal=PAL, grand=False, stone=True):
    r = S.rnd
    pick = S.pick
    st = H.Style(S, col=pick(*pal["cols"]), roof=pick(*pal["roofs"]), grand=grand)
    st.wood = pick(*pal["woods"])
    st.shutter = pick(*pal.get("shutters", H.SHUTTERS))
    st.eaves = r.random() < (0.45 if role != "core" else 0.3)
    two = role == "core" and r.random() < 0.8 or role == "mid" and r.random() < 0.45 or role == "farm" and r.random() < 0.3
    mw = r.choice((5, 6, 7, 7, 8, 9)) if role != "edge" else r.choice((5, 6, 6, 7))
    md = r.choice((6, 7, 8, 9, 10)) if two else r.choice((6, 7, 8))
    if two:
        md = max(md, 8)
    parts = []                                   # (kind, x, z, w, d) in the house's frame, main at (0, 0)
    adds = []
    if role == "farm":
        adds.append("barn")
    n = {"core": r.choice((0, 0, 1)), "mid": r.choice((0, 1, 1, 2)), "edge": r.choice((0, 1, 1)), "farm": r.choice((0, 1))}[role]
    pool = ["wing", "wing", "leanto", "leanto", "porch", "porch"]
    while len(adds) < n + (1 if role == "farm" else 0) and pool:
        a = pool.pop(r.randrange(len(pool)))
        if a not in adds:
            adds.append(a)
    sides = ["left", "right"]
    r.shuffle(sides)
    parts.append(("main", 0, 0, mw, md))
    for a in adds:
        if a in ("wing", "barn") and sides:
            s = sides.pop()
            ww = r.choice((4, 5, 6)) if a == "wing" else r.choice((7, 8, 9))
            wd = min(md, r.choice((5, 6, 7))) if a == "wing" else r.choice((8, 9, 10))
            wz = 0 if r.random() < 0.6 or a == "barn" else md - wd
            if a == "barn":
                wz = md - wd if wd <= md else 0
            wx = mw - 1 if s == "right" else -ww + 1      # sharing the main's side wall
            parts.append((a, wx, wz, ww, wd))
        elif a == "leanto":
            s = sides.pop() if sides and r.random() < 0.6 else "back"
            if s == "back":
                parts.append(("leanto_back", 0, -3, mw, 3))
            else:
                parts.append(("leanto_" + s, mw if s == "right" else -3, 1, 3, md - 2))
        elif a == "porch":
            parts.append(("porch", 0, md, mw, 2))
    # shift so the footprint's corner is (0, 0)
    mx = -min(p[1] for p in parts)
    mz = -min(p[2] for p in parts)
    parts = [(k, x + mx, z + mz, w, d) for k, x, z, w, d in parts]
    W = max(p[1] + p[3] for p in parts)
    D = max(p[2] + p[4] for p in parts)
    L = Local(r)
    main = parts[0]
    door = (mw // 2 if r.random() < 0.6 else r.choice((2, mw - 3))) if mw >= 6 else 2
    door = max(2, min(mw - 3, door))
    # the additions first, the main block over them (its walls win where they meet)
    top_main = 8 if two else 4
    for kind, x, z, w, d in parts[1:]:
        P = Sub(L, x, z, w, d)
        if kind in ("wing", "barn"):
            barn = kind == "barn"
            st2 = H.Style(S, col=st.col, roof=st.roof)
            st2.wood, st2.shutter, st2.pattern = st.wood, st.shutter, "plain" if barn else st.pattern
            P.box(0, 0, 0, w - 1, 0, d - 1, "%s_planks" % st.wood if not barn else "packed_mud")
            if barn or (stone and r.random() < 0.4):
                H.stone_storey(P, st2, 1, d - 1, front_windows=(), rows=4 if not barn else 5)
                tp = 4 if not barn else 5
            else:
                H.framed_storey(P, st2, 1, d - 1, front_windows=set())
                tp = 4
            H.gable_roof(P, st2, tp, d - 1, steep=2 if barn else 1, ridge_x=not st.eaves)
            if barn:                                     # the great doors and the hay in the bay
                cx = w // 2
                for lx in (cx - 1, cx, cx + 1):
                    for y in (1, 2, 3):
                        P.put(lx, y, d - 1, None)
                P.put(cx - 2, 2, d, "%s_trapdoor[facing=south,half=bottom,open=true,powered=false,waterlogged=false]" % st.wood)
                P.put(cx + 2, 2, d, "%s_trapdoor[facing=south,half=bottom,open=true,powered=false,waterlogged=false]" % st.wood)
                for lx in range(1, w - 1):
                    for lz in range(1, 3):
                        for y in range(1, 1 + r.randint(1, 3)):
                            P.put(lx, y, lz, "hay_block[axis=y]")
            else:
                H.lay(P, st2, 1, [r.choice(("BbW", "WBO", "CJb", "SnB"))[:max(1, w - 2)].ljust(w - 2, ".")], x0=1, z0=1)
        elif kind.startswith("leanto"):
            # posts at the outer edge, a single slope falling away from the house, a woodpile or a store under it
            side = kind.split("_")[1]
            mat = st.roof
            for i in range(-1, (w if side == "back" else d) + 1):
                for k in range(4):                       # k: out from the house's wall, the last one the overhang
                    lx, lz, f = {"back": (i, 2 - k, "south"), "right": (k, i, "west"), "left": (2 - k, i, "east")}[side]
                    P.put(lx, 4 - (k + 1) // 2, lz, H.stairs(mat, f))
            outer = [(i, 0) for i in range(w)] if side == "back" else [(w - 1, i) for i in range(d)] if side == "right" else [(0, i) for i in range(d)]
            closed = r.random() < 0.4
            for j, (lx, lz) in enumerate(outer):
                P.put(lx, 0, lz, "%s_planks" % st.wood)
                for y in (1, 2):
                    if j in (0, len(outer) - 1) or j % 3 == 0:
                        P.put(lx, y, lz, "stripped_%s_log[axis=y]" % st.wood)
                    elif closed:
                        P.put(lx, y, lz, "%s_planks" % st.wood)
                    elif y == 1:
                        P.put(lx, y, lz, "%s_log[axis=%s]" % (st.wood, "x" if side == "back" else "z") if r.random() < 0.6 else "barrel[facing=up,open=false]")
        elif kind == "porch":
            cx = door
            for lx in (cx - 1, cx + 1):
                for y in (1, 2, 3):
                    P.put(lx, y, 1, "%s_fence" % st.wood)
            for lx in range(cx - 1, cx + 2):
                P.put(lx, 4, 0, H.FULL.get(st.roof, st.roof))
                P.put(lx, 4, 1, H.stairs(st.roof, "north"))
                P.put(lx, 0, 0, "%s_planks" % st.wood)
                P.put(lx, 0, 1, "%s_planks" % st.wood)
            P.put(cx + 2 if cx + 2 < w else cx - 2, 1, 1, "ashbound:bench[facing=%s]" % ("west" if cx + 2 < w else "east"))
    for (lx, y, lz) in [p for p in L.S.B if main[1] < p[0] < main[1] + mw - 1 and main[2] < p[2] < main[2] + md - 1 and p[1] >= 1]:
        L.S.put(lx, y, lz, None)                 # nothing of the additions inside the main block
    M = Sub(L, main[1], main[2], mw, md)
    M.box(0, 0, 0, mw - 1, 0, md - 1, "%s_planks" % st.wood)
    wins = {p for p in range(1, mw // 2 - (0 if mw % 2 else 1)) if door not in (2 * p, 2 * p + 1)}
    if stone and ((two and r.random() < 0.55) or (role == "edge" and r.random() < 0.35)):
        H.stone_storey(M, st, 1, md - 1, front_windows=tuple(x for x in (1, mw - 2) if abs(x - door) > 1))
    else:
        H.framed_storey(M, st, 1, md - 1, front_windows=wins)
    if two:
        M.box(1, 5, 1, mw - 2, 5, md - 2, "%s_planks" % st.wood)
        H.framed_storey(M, st, 5, md - 1, front_windows={p for p in range(0, mw // 2) if p % 2 == 1 or mw < 7})
    span = md if st.eaves else mw
    H.gable_roof(M, st, top_main, md - 1, steep=r.choice((1, 2, 2)) if span <= 7 else 1, ridge_x=st.eaves)
    H.front_door(M, st, door, md - 1)
    rows = plan(r, mw, md, door)
    try:
        H.lay(M, st, 1, rows, lights=[(mw // 2, md // 2)])
    except Exception:
        pass
    if two:
        if md >= 8:
            sx = 1 if rows[0][0] != "H" else mw - 2
            H.flight(M, st, sx, md - 3, 1, 5, "north")
        H.lay(M, st, 6, ["H" + "." * (mw - 4) + "C", "F" + "." * (mw - 4) + "B"])
    cxs = [1, mw - 2] if not st.eaves else [mw // 2]
    cz = 0 if not st.eaves else r.choice((1, md - 2))
    cx = r.choice(cxs)
    H.chimney(M, cx, cz, 1, H.roof_top(M, cx, cz) + 2)
    # out into the world, turned to face its road
    out = H.Frame(S, x0, z0, W, D, face)
    cells = set()
    top = 0
    for (lx, y, lz), s in L.S.B.items():
        out.put(lx, y, lz, s)
        cells.add(out.world(lx, 0, lz)[0::2])
        top = max(top, y)
    for (lx, y, lz), nb in L.S.nbt.items():
        S.nbt[out.world(lx, y, lz)] = nb
    door_w = out.world(main[1] + door, 0, main[2] + md)
    return dict(cells=cells, door=(door_w[0], door_w[2]), W=W, D=D, top=top, parts=parts, two=two)


def footprint(W, D, face):
    return (W, D) if face in ("south", "north") else (D, W)


if __name__ == "__main__":
    S = K.Build(5)
    x = 0
    roles = ["core", "core", "mid", "mid", "mid", "edge", "edge", "farm"]
    for row in range(2):
        x = 0
        for i, role in enumerate(roles):
            h = compose(S, x, row * 26, "south", role)
            for (a, b) in h["cells"]:
                for yy in (-1,):
                    S.put(a, yy, b, H.stone(S))
            x += max(a for a, _ in h["cells"]) - x + 5
    H.clear_doorways(S)
    H.frame_panes(S)
    for a in range(-10, x + 10):
        for b in range(-12, 60):
            if S.get(a, -1, b) is None:
                S.put(a, -1, b, "grass_block[snowy=false]")
    shots = {"front": ((x / 2, 26, 110), (x / 2, 2, 20), 30), "back": ((x / 2, 30, -60), (x / 2, 2, 20), 30),
             "near": ((40, 9, 46), (30, 3, 26), 30)}
    K.preview(S, "vil_houses", shots, sun=(40, -130), sky=(0.55, 0.68, 0.85))
