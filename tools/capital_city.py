"""Highmourn's lower city inside the walls: streets of houses and shops from the approved house kit (houses.py in
E:/Ashbound/tools: timber-framed, plastered, every room furnished), the market and its fountain. Built a district at a
time; heights are over the valley floor, the lower city's ground at 0 (a house's floor replaces the turf there),
x east, z south, the gate to the south.

Laid out the way a grown medieval town is (see the research notes in the session): the streets first, as gentle
curves whose width breathes, then the houses packed along them shoulder to shoulder, each set to the street's edge
where it stands (so the fronts step with the curve), a narrow alley now and then, and the long plot behind every
house a yard, a garden, a shed or a well behind a fence. The road's stone follows its use: setts down the high street
with a gutter in the crown, the market in pale flagstone in rings round the fountain, the lanes in trodden earth.

    step 1   High Street from the Gate of Oaths, widening into the market (the fountain, its stalls), North Street
             on toward the lake shore, Market Lane west, Gate Row either side inside the wall, Lake Lane to the beach
    step 2   the blocks between filled: Cooper's Lane south from Market Lane through the green (a great oak, a well,
             the inn and its stable yard facing it) to Gate Row, a back lane behind the yards into the market, Wall
             Lane and Chapel Lane north of Market Lane, Mill Lane along the lake to Gate Row East, and orchards and
             allotments in what's still open behind the houses
    step 3   the lake quarter: Fishers' Row along the south shore, its cottages on posts over the shallows off a
             boardwalk, jetties and skiffs, a boathouse; the long pier out to the island and its beacon; piers, smacks
             and fish stalls on the quay; the mill on the river where it leaves the lake
    step 4   the guild terrace, 20 up: Stair Street from the market to the grand stair up the bank; the Guild Square
             (its seal in the paving, notice boards, banners); the guild hall over the passage north, its belfry with
             the clock, bells and a dark spire, the gate hall and the trophy hall inside; the training yard west of
             it, the quartermaster and the smithy east; the Terrace Walk wall to wall along the bank's top, a
             balustrade on the lip, a bridge over the river, the terrace's grander houses along it
    step 5   the citadel, 44 up: the Stair of Champions from Guild Lane with the eight champions' plinths; the
             curtain on the lip with its round towers and the water gate; the gatehouse; the court with the Ash
             Warden's plinth; the Lord's Keep (great hall, throne, donjon and spire) west; the Sanctuary of Embers
             (nave, rose, spire, the apse open on the falls' pool) east; the lord's garden
"""
import collections
import json
import os
import math
import sys

sys.path.insert(0, "E:/Ashbound/tools")
import houses as H  # noqa: E402
H.DOORWAY_JUNK = tuple(k for k in H.DOORWAY_JUNK if k != "rose") + ("rose_bush", "wither_rose")   # not rose_plaster walls
import structkit as K  # noqa: E402


# ---------------------------------------------------------------- the houses' own stone (dforge_highmourn.py)
# Every house rolls its Style right after its Frame: the Style picks a stone to suit its plaster and roof (a hash of
# where it stands, so no other roll moves), and the Frame lays that stone wherever the kit lays greystone (bricks)
# or stone bricks (quoins and the sill course).
HOUSE_STONE = {      # plaster -> (stone, weight): the plaster no longer shows, it only spreads the stones round
    "plaster": (("hearthstone", 3), ("ashstone", 2), ("rosestone", 1)),
    "ochre_plaster": (("honeystone", 3), ("hearthstone", 1)),
    "rose_plaster": (("rosestone", 3), ("ashstone", 1)),
    "slate_plaster": (("duskstone", 3), ("ashstone", 1)),
}
HORNSEND = (-208, 18, -126, 62)
HOUSE_STONE_SWAP = (     # kit block -> our block, % the stone (longest names first)
    ("ashbound:mossy_greystone_stairs", "ashbound:%s_brick_stairs"),
    ("ashbound:mossy_greystone_slab", "ashbound:%s_brick_slab"),
    ("ashbound:mossy_greystone_wall", "ashbound:%s_brick_wall"),
    ("ashbound:mossy_greystone", "ashbound:cracked_%s_bricks"),
    ("ashbound:greystone_stairs", "ashbound:%s_brick_stairs"),
    ("ashbound:greystone_slab", "ashbound:%s_brick_slab"),
    ("ashbound:greystone_wall", "ashbound:%s_brick_wall"),
    ("ashbound:greystone", "ashbound:%s_bricks"),
    ("minecraft:stone_brick_stairs", "ashbound:%s_brick_stairs"),
    ("minecraft:stone_brick_slab", "ashbound:%s_brick_slab"),
    ("minecraft:stone_brick_wall", "ashbound:%s_brick_wall"),
    ("minecraft:cracked_stone_bricks", "ashbound:cracked_%s_bricks"),
    ("minecraft:mossy_stone_bricks", "ashbound:cracked_%s_bricks"),
    ("minecraft:stone_bricks", "ashbound:%s_quoin"),
)
_frame_init, _frame_put, _style_init = H.Frame.__init__, H.Frame.put, H.Style.__init__


def _hs_frame_init(self, S, *a, **kw):
    _frame_init(self, S, *a, **kw)
    self.stone = None
    S._house_frame = self


def in_hornsend(x, z):
    """The outcast quarter: the back land between Tanners' Lane and Wall Lane, under the west wall."""
    return HORNSEND[0] <= x <= HORNSEND[2] and HORNSEND[1] <= z <= HORNSEND[3]


def _hs_style_init(self, S, *a, **kw):
    _style_init(self, S, *a, **kw)
    F = getattr(S, "_house_frame", None)
    if F is None or F.stone is not None:
        return
    pick = HOUSE_STONE.get(self.col, HOUSE_STONE["plaster"])
    if in_hornsend(F.ox, F.oz):
        pick = (("ashstone", 2), ("duskstone", 3))
    if "blue" in str(self.roof) or "slate" in str(self.roof):
        pick = pick + (("duskstone", 2),)
    h = (F.ox * 73856093 ^ F.oz * 19349663) % sum(w for _, w in pick)
    for name, w in pick:
        if h < w:
            F.stone = name
            break
        h -= w


PLASTER_WALLS = ("plaster", "ochre_plaster", "rose_plaster", "slate_plaster", "ashen_plaster")


def _hs_put(self, lx, y, lz, state):
    if state is not None and self.stone:
        base = state.split("[")[0]
        full = base if ":" in base else "minecraft:" + base
        n = full.split(":")[1]
        if n.endswith("plaster_timber") or n in PLASTER_WALLS:
            # no painted frames: the walls go up in the house's stone, quoins up the corners, the odd cracked brick
            corner = lx in (0, self.w - 1) and lz in (0, self.d - 1, self.d - 2)
            h = (self.ox * 31 + self.oz * 17 + lx * 7 + y * 13 + lz * 3) % 23
            state = "ashbound:%s_quoin" % self.stone if corner and y % 2 == 0 else                 "ashbound:cracked_%s_bricks" % self.stone if h == 0 else "ashbound:%s_bricks" % self.stone
            _frame_put(self, lx, y, lz, state)
            return
        for old, new in HOUSE_STONE_SWAP:
            if full == old:
                state = (new % self.stone) + state[len(base):]
                break
    _frame_put(self, lx, y, lz, state)


H.Frame.__init__, H.Frame.put, H.Style.__init__ = _hs_frame_init, _hs_put, _hs_style_init
import capital_land as L  # noqa: E402
import capital_pair as PR  # noqa: E402

S = put = pick = None         # set by capital.py (its Build)
GROUND = None                 # ground(x, z), set by build()

FLAG = "ashbound:limestone_flagstones"
LIGHT = "light[level=15,waterlogged=false]"
WATER = "water[level=0]"

# the kit's roofs, plus the glazed tiles for a few of the grander houses
H.FULL.update({"ashbound:blue_roof_tile": "ashbound:blue_roof_tiles", "ashbound:green_roof_tile": "ashbound:green_roof_tiles"})
ROOFS = (("ashbound:clay_roof_tile", 6), ("ashbound:wood_shingle", 3), ("ashbound:slate_shingle", 3),
         ("ashbound:blue_roof_tile", 1), ("ashbound:green_roof_tile", 1))
MAIN_MIX = (("house", 3), ("townhouse", 3))        # homes: the shops all stand round the market
MARKET_MIX = (("shop", 4), ("townhouse", 4), ("house", 2))
LANE_MIX = (("house", 4), ("cottage", 4), ("townhouse", 1))
TRADES = ("general", "baker", "apothecary", "books")
SHOP_MIX = (("shop", 1),)            # the market's ring: shops only, trades in turn
ROW_TRADES = ("general", "baker", "tailor", "apothecary", "grocer", "books", "chandler", "fishmonger")
ROW_I = [0]

FOUNTAIN = (-30, 92)
BASIN_R = 8
# the Moonwell Priestess's pieces: (x, y, z, piece) from her feet (ported from E:/Ashbound with port_city.py)
ELF_PIECES = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "renders", "elf_statue_pieces.json")))
RANK = {"market": 3, "square": 3, "hearth": 3, "main": 2, "walk": 2, "green": 2, "lane": 1, "alley": 0}
GREEN = (-100, 121)           # the green on Cooper's Lane, the inn on its west side
GREEN_R = 8


def noise(x, z, scale, seed):
    return L.noise(x, z, scale, seed)


# ================================================================ streets

class Road:
    """A street: a Catmull-Rom curve through its points, its width eased between the widths given at them.
    cells: (x, z) -> u, 0 on the crown to 1 at the edge."""

    def __init__(self, name, kind, pts, widths, gutter=False):
        self.name, self.kind, self.gutter = name, kind, gutter
        self.samples = []                       # (x, z, half width, tx, tz, fraction along)
        P = [pts[0]] + list(pts) + [pts[-1]]
        Wd = [widths[0]] + list(widths) + [widths[-1]]
        raw = []
        for i in range(1, len(P) - 2):
            n = max(4, int(math.dist(P[i], P[i + 1]) * 4))
            for k in range(n):
                t = k / n
                raw.append((cr(P[i - 1][0], P[i][0], P[i + 1][0], P[i + 2][0], t),
                            cr(P[i - 1][1], P[i][1], P[i + 1][1], P[i + 2][1], t),
                            max(1.5, cr(Wd[i - 1], Wd[i], Wd[i + 1], Wd[i + 2], t) / 2)))
        raw.append((pts[-1][0], pts[-1][1], widths[-1] / 2))
        total = sum(math.dist(raw[i][:2], raw[i + 1][:2]) for i in range(len(raw) - 1)) or 1
        run = 0.0
        for i, (x, z, hw) in enumerate(raw):
            a, b = raw[max(0, i - 2)], raw[min(len(raw) - 1, i + 2)]
            tx, tz = b[0] - a[0], b[1] - a[1]
            m = math.hypot(tx, tz) or 1
            if i:
                run += math.dist(raw[i - 1][:2], (x, z))
            self.samples.append((x, z, hw, tx / m, tz / m, run / total))
        self.cells = {}
        for x, z, hw, _, _, _ in self.samples:
            for cx in range(math.floor(x - hw), math.ceil(x + hw) + 1):
                for cz in range(math.floor(z - hw), math.ceil(z + hw) + 1):
                    u = math.hypot(cx - x, cz - z) / hw
                    if u <= 1 and u < self.cells.get((cx, cz), 9):
                        self.cells[(cx, cz)] = u


def cr(p0, p1, p2, p3, t):
    return 0.5 * (2 * p1 + (p2 - p0) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (3 * p1 - p0 - 3 * p2 + p3) * t ** 3)


ROADS = []
ROAD = {}                     # (x, z) -> (road, u), the highest-ranked street wins where two meet
YARD = set()
FRONT = set()                 # the strips between house fronts and the street, and under the jetties
ALLEY = set()
CLAIM = set()                 # ground a set piece keeps for itself: no house is put on it


def add_road(*a, **kw):
    r = Road(*a, **kw)
    ROADS.append(r)
    for c, u in r.cells.items():
        old = ROAD.get(c)
        if old is None or RANK[r.kind] > RANK[old[0].kind] or (r.kind == old[0].kind and u < old[1]):
            ROAD[c] = (r, u)
    return r


def near_kind(x, z, kind, rad):
    return any(ROAD.get((x + dx, z + dz), (None,))[0] is not None and ROAD[(x + dx, z + dz)][0].kind == kind
               for dx in range(-rad, rad + 1, 2) for dz in range(-rad, rad + 1, 2))


# ================================================================ ground and paving

def wet(x, z):
    return any("water" in (S.B.get((x, y, z)) or "") for y in (-1, 0, 1))


def built(x, z, y0=1, y1=4):
    return any((x, y, z) in S.B for y in range(y0, y1 + 1))


def in_town(x, z):
    """Inside the curtain wall with a lane's width to spare (the pomerium kept clear behind the wall)."""
    return (x / (L.RX - 14)) ** 2 + (z / (L.RZ - 12)) ** 2 < 1


def open_ground(x, z):
    """Flat lower-city ground with nothing on it."""
    return GROUND(x, z) == 0 and not wet(x, z) and not built(x, z, 0, 4)


THIN = ("fence", "lantern", "chain", "torch", "bars", "pane", "sign", "banner", "rod", "leaves", "wall", "candle")


def masonry(x, z):
    """A set piece's wall here (not a house's, not a post, a fence or a lamp)."""
    for y in (2, 3):
        st = S.B.get((x, y, z))
        if st and st != "air" and OWNER.get((x, y, z)) is None and not any(t in st for t in THIN):
            return True
    return False


def plot_ok(x0, z0, x1, z1, clear=2):
    """Open ground for a house, off the streets, alleys, yards and fore-courts, and standing clear of the set
    pieces: never wall to wall with a hall, a tower or a workshop, only with other houses."""
    if not all(open_ground(x, z) and (x, z) not in ROAD and (x, z) not in ALLEY and (x, z) not in YARD
               and (x, z) not in FRONT and (x, z) not in CLAIM and in_town(x, z)
               for x in range(x0, x1 + 1) for z in range(z0, z1 + 1)):
        return False
    return not any(masonry(x, z) for x in range(x0 - clear, x1 + clear + 1) for z in range(z0 - clear, z1 + clear + 1)
                   if not (x0 <= x <= x1 and z0 <= z <= z1))


def pave(x, z, st):
    if GROUND(x, z) != 0 or wet(x, z) or (x, 0, z) in S.B:
        return False
    put(x, 0, z, st)
    put(x, -1, z, "stone" if not any(k in st for k in ("dirt", "mud", "grass")) else "dirt")
    return True


SLAB = "%s_slab[type=bottom,waterlogged=false]"


def setts(x, z, u, edge=False):
    """The high street: stone setts in soft drifts of andesite and plain stone (all within a few L* of each other,
    so it reads as one worn surface, never a patchwork), cracked and mossy setts where few feet go."""
    a = noise(x, z, 7, 301)
    b = noise(x * 1.7, z * 1.7, 3, 302)
    if b > 0.86:
        return "cracked_stone_bricks"
    if edge or u > 0.82:
        if b < 0.16:
            return "mossy_stone_bricks"
        return "polished_andesite" if a > 0.45 else "stone_bricks"
    if a > 0.64:
        return "andesite" if b > 0.4 else "stone"
    if a < 0.3 and b > 0.5:
        return "polished_andesite"
    return "stone_bricks"


def market_stone(x, z, u):
    """The market: pale flagstone in drifts, laid in rings round the fountain; the rim blends into the setts."""
    if u > 0.9:
        return setts(x, z, 1)
    fx, fz = FOUNTAIN
    r = math.hypot(x - fx, z - fz)
    if r > BASIN_R + 3 and int(r) % 7 == 0:
        return "smooth_stone"
    a = noise(x, z, 8, 311)
    b = noise(x * 1.5, z * 1.5, 3, 312)
    if b > 0.9:
        return "ashbound:pale_limestone"
    if a > 0.62:
        return "ashbound:statue_stone"
    return FLAG


def earth(x, z, u, kind):
    """A lane: a trodden path down its middle, coarser earth toward the sides along a wavering line, broad patches
    of packed mud, gravel where it meets the stone streets, grass coming in at the edges. None leaves the turf."""
    if near_kind(x, z, "main", 3) or near_kind(x, z, "market", 3):
        return "gravel" if noise(x, z, 4, 322) > 0.35 else "stone"
    if kind == "alley":
        return "packed_mud" if noise(x, z, 5, 324) > 0.45 else "coarse_dirt"
    e = u + 0.4 * (noise(x, z, 5, 321) - 0.5)
    if e > 0.88 and noise(x, z, 4, 325) > 0.4:
        return None
    if e > 0.62:
        return "coarse_dirt"
    if noise(x, z, 11, 326) > 0.68:
        return "packed_mud"
    return "dirt_path"


def pave_roads():
    for (x, z), (r, u) in ROAD.items():
        if r.kind == "market":
            st = market_stone(x, z, u)
        elif r.kind == "main":
            st = "polished_andesite" if r.gutter and u < 0.07 else setts(x, z, u)      # a flush gutter: a sunk one read as holes
        elif r.kind == "green":
            st = green_path(x, z)
        elif r.kind in ("walk", "square"):
            st = walk_stone(x, z, u, r.kind)
        elif r.kind == "hearth":
            st = hearth_stone(x, z, u)
        else:
            st = earth(x, z, u, r.kind)
        if st:
            pave(x, z, st)
        elif r.kind == "green":
            if GROUND(x, z) == 0 and not built(x, z, 1, 1) and noise(x, z, 2, 351) > 0.5:
                put(x, 1, z, pick(("short_grass", 6), ("dandelion", 1), ("poppy", 1), ("oxeye_daisy", 1), ("cornflower", 1)))
        elif GROUND(x, z) == 0 and not wet(x, z) and (x, 1, z) not in S.B and noise(x, z, 2, 323) > 0.55:
            put(x, 1, z, "short_grass")
    for (x, z) in ALLEY:
        pave(x, z, earth(x, z, 0.5, "alley"))
    for (x, z) in FRONT:
        r = nearest_road(x, z)
        if r is None or r.kind in ("main", "market"):
            pave(x, z, setts(x, z, 1, edge=True))
        elif r.kind in ("walk", "square", "hearth"):
            pave(x, z, FLAG)
        else:
            pave(x, z, "stone_bricks" if noise(x, z, 4, 331) > 0.4 else "packed_mud")


def shoulders():
    """Where a house's flank or a corner stands back from a street, the strip between them is paved too."""
    walls = {(x, z) for (x, y, z) in OWNER if y == 1}
    near = {(x + dx, z + dz) for (x, z) in walls for dx in range(-6, 7) for dz in range(-6, 7)}
    for (x, z) in list(ROAD):
        for dx in range(-4, 5):
            for dz in range(-4, 5):
                c = (x + dx, z + dz)
                if c in near and c not in ROAD and c not in FRONT and c not in ALLEY and c not in YARD                         and open_ground(*c):
                    FRONT.add(c)


def nearest_road(x, z):
    for rad in range(1, 6):
        for dx in range(-rad, rad + 1):
            for dz in (-rad, rad):
                for c in ((x + dx, z + dz), (x + dz, z + dx)):
                    if c in ROAD:
                        return ROAD[c][0]
    return None


# ================================================================ street furniture

def lamp(x, z, axis):
    """The twin-arm street lamp, its glow cells beside the lanterns."""
    if GROUND(x, z) != 0 or wet(x, z) or built(x, z, 1, 4):
        return
    for p in range(3):
        put(x, 1 + p, z, "ashbound:street_lamp[axis=%s,part=%d]" % (axis, p))
    dx, dz = (1, 0) if axis == "x" else (0, 1)
    for s in (-1, 1):
        if (x + s * dx, 2, z + s * dz) not in S.B:
            put(x + s * dx, 2, z + s * dz, LIGHT)


def bench(x, z, facing):
    """A bench, its sitter looking `facing` (the back is on the other side)."""
    if GROUND(x, z) == 0 and not built(x, z, 1, 2):
        put(x, 1, z, "ashbound:bench[facing=%s]" % facing)


def seat(x, z, fx, fz):
    """A bench at x, z, looking at fx, fz (the fountain, the table, the yard it's for)."""
    dx, dz = fx - x, fz - z
    bench(x, z, ("east" if dx > 0 else "west") if abs(dx) > abs(dz) else ("south" if dz > 0 else "north"))


def planter(cx, cz, tree=True):
    """A raised greystone bed with grass, flowers and a small blossoming tree."""
    for x in range(cx - 2, cx + 3):
        for z in range(cz - 2, cz + 3):
            if GROUND(x, z) != 0 or wet(x, z) or built(x, z, 0, 4):
                return
    for x in range(cx - 2, cx + 3):
        for z in range(cz - 2, cz + 3):
            rim = abs(x - cx) == 2 or abs(z - cz) == 2
            put(x, 0, z, "ashbound:greystone" if rim else "dirt")
            put(x, 1, z, "ashbound:greystone_slab[type=bottom,waterlogged=false]" if rim else "grass_block[snowy=false]")
            if not rim and (x, z) != (cx, cz):
                put(x, 2, z, pick(("poppy", 2), ("cornflower", 2), ("oxeye_daisy", 2), ("allium", 1), ("short_grass", 3)))
    if tree:
        small_tree(cx, 2, cz, "cherry")


def small_tree(cx, y0, cz, wood="cherry", h=4):
    leaves = {"cherry": "cherry_leaves", "oak": "oak_leaves", "birch": "birch_leaves"}[wood]
    for y in range(y0, y0 + h):
        put(cx, y, cz, "%s_log[axis=y]" % wood)
    top = y0 + h - 1
    for x in range(cx - 2, cx + 3):
        for z in range(cz - 2, cz + 3):
            for y in range(top - 1, top + 3):
                r = math.sqrt((x - cx) ** 2 + (z - cz) ** 2 + ((y - top - 0.4) * 1.3) ** 2)
                if r < 2.6 + 0.4 * noise(x * 3 + y, z * 3, 2, 70) and (x, y, z) not in S.B:
                    put(x, y, z, "%s[distance=1,persistent=true,waterlogged=false]" % leaves)


# ================================================================ houses

OWNER = {}
LOG = []
HOUSES = [0]
FENCES = set()


def is_roof(st):
    return isinstance(st, str) and ("roof_tile" in st or "shingle" in st)


def build_house(fn, corner, face, kw):
    """One house from the kit. Its neighbours stand wall to wall with it, so its eaves stop at their walls: a roof
    block never goes into another house's wall, and nothing of another house is taken away."""
    HOUSES[0] += 1
    hid = HOUSES[0]
    if in_hornsend(*corner):
        kw = dict(kw, roof="ashbound:slate_shingle", eaves=False)
    orig = S.put

    def guarded(x, y, z, st, nbt=None):
        k = (x, y, z)
        o = OWNER.get(k)
        if o is not None and o != hid:
            prev = S.B.get(k)
            if st is None or (is_roof(st) and not is_roof(prev)):
                return
        OWNER[k] = hid
        orig(x, y, z, st, nbt)

    S.put = guarded
    try:
        fn(S, corner[0], corner[1], face, **kw)
    finally:
        S.put = orig


# side: (axis the street runs along, the way out from the crown toward the houses, the way their doors face)
SIDES = {"w": ("z", -1, "east"), "e": ("z", 1, "west"), "n": ("x", -1, "south"), "s": ("x", 1, "north")}


def edge_fronts(road, side, f0=0.0, f1=1.0):
    """For each row across the street (z for a street along z, x for one along x): the first cell past the
    street's outer edge on that side, read from its cells, so a market's wedge or a curve is followed as it is."""
    axis, sgn, _ = SIDES[side]
    lo = {}
    for (x, z) in road.cells:
        a, b = (z, x) if axis == "z" else (x, z)
        if a not in lo or (b - lo[a]) * sgn > 0:
            lo[a] = b
    return {a: b + sgn for a, b in lo.items()}


def frontage(road, side, mix, f0=0.0, f1=1.0, alley=0.12, yards=(8, 15), eaves=0.25, step=4, trades=None):
    """Houses shoulder to shoulder down one side of a street, each brought up to the street's edge where it stands
    (a block's set-back now and then), an alley between them every so often, a yard behind each. Shops take their
    trades in turn from `trades` when it's given (so neighbours differ), else at random."""
    axis, sgn, face = SIDES[side]
    front = edge_fronts(road, side, f0, f1)
    if not front:
        return 0
    rnd = S.rnd
    t, end = min(front), max(front)
    n, last = 0, None
    while t <= end:
        kinds = [k for k, _ in mix]
        first = pick(*mix)
        kinds.remove(first)
        rnd.shuffle(kinds)
        done = False
        for kind in [first] + kinds:
            fn, w, d = H.KINDS[kind]
            span = range(t, t + w)
            if any(a not in front for a in span):
                continue
            F = (min if sgn < 0 else max)(front[a] for a in span)
            if max(abs(front[a] - F) for a in span) > step:
                continue                                    # the street turns too sharply here for one house
            F += sgn * (1 if rnd.random() < 0.3 else 0)
            b0, b1 = (F - d + 1, F) if sgn < 0 else (F, F + d - 1)
            box = (b0, t, b1, t + w - 1) if axis == "z" else (t, b0, t + w - 1, b1)
            if not plot_ok(*box):
                continue
            kw = {"roof": pick(*ROOFS), "eaves": kind != "cottage" and rnd.random() < eaves}
            if kind == "shop":
                if trades:
                    kw["trade"] = trades[ROW_I[0] % len(trades)]
                    ROW_I[0] += 1
                else:
                    kw["trade"] = rnd.choice(TRADES)
            build_house(fn, (box[0], box[1]), face, kw)
            LOG.append((road.name, side, kind, box, F, {k: front[k] for k in span}))
            # pave from the house to the street, and under its jetties
            for a in span:
                b = F
                while b != front[a] and abs(b - F) < 8:
                    b -= sgn
                    FRONT.add((b, a) if axis == "z" else (a, b))
                for k in range(d):
                    c = (F + sgn * k, a) if axis == "z" else (a, F + sgn * k)
                    if (c[0], 0, c[1]) not in S.B:
                        FRONT.add(c)
            back = b0 - 1 if sgn < 0 else b1 + 1
            joined = last is not None and last["end"] == t
            yard(axis, sgn, t, w, back, rnd.randint(*yards), fence_near=not joined)
            last = {"end": t + w}
            n += 1
            t += w
            if rnd.random() < alley:
                g = rnd.choice((2, 3))
                for a in range(t, t + g):
                    if a in front:
                        for k in range(front[a], back + sgn * 12, sgn):
                            c = (k, a) if axis == "z" else (a, k)
                            if c not in ROAD and open_ground(*c):
                                ALLEY.add(c)
                t += g
                last = None
            done = True
            break
        if not done:
            t += 1
            last = None
    return n


# ---------------------------------------------------------------- the plots behind

def fence_at(x, z, y=1):
    if GROUND(x, z) == 0 and not wet(x, z) and not built(x, z, 1, 1) and (x, z) not in ROAD and (x, z) not in ALLEY:
        put(x, y, z, "spruce_fence")
        FENCES.add((x, y, z))


def connect_fences():
    """The game lays the city without neighbour updates, so the fences' arms are set here."""
    solid = ("planks", "log", "stone", "brick", "timber", "plaster", "fence_gate")
    for (x, y, z) in FENCES:
        if not (S.B.get((x, y, z)) or "").startswith("spruce_fence"):
            continue
        arm = {}
        for d, (dx, dz) in (("north", (0, -1)), ("south", (0, 1)), ("east", (1, 0)), ("west", (-1, 0))):
            nb = S.B.get((x + dx, y, z + dz)) or ""
            arm[d] = "true" if (nb.startswith("spruce_fence") or any(s in nb for s in solid)) and "slab" not in nb else "false"
        put(x, y, z, "spruce_fence[east=%s,north=%s,south=%s,waterlogged=false,west=%s]"
            % (arm["east"], arm["north"], arm["south"], arm["west"]))


def yard(axis, sgn, t, w, back, depth, fence_near=True):
    """The long plot behind a house: as deep as the open ground allows (up to `depth`), fenced from its
    neighbours and at the back, with a few of: a kitchen garden, a lean-to shed, a woodpile, a well, a fruit tree,
    a flower bed, barrels and a composter."""
    def world(i, k):                      # i across the plot (0..w-1, along the street), k back from the house
        a, b = t + i, back + sgn * k
        return (b, a) if axis == "z" else (a, b)

    D = 0
    while D < depth and all(open_ground(*world(i, D)) and world(i, D) not in ROAD and world(i, D) not in ALLEY
                            and world(i, D) not in YARD and in_town(*world(i, D)) for i in range(w)):
        D += 1
    if D < 4:
        return
    rnd = S.rnd
    for i in range(w):
        for k in range(D):
            YARD.add(world(i, k))
    # fences: the near side (unless the last plot's far fence is there), the far side, the back with a gate
    for k in range(D):
        if fence_near:
            fence_at(*world(0, k))
        fence_at(*world(w - 1, k))
    gate = rnd.randint(1, w - 2)
    for i in range(w):
        x, z = world(i, D - 1)
        if i == gate:
            ga = "x" if axis == "z" else "z"
            put(x, 1, z, "spruce_fence_gate[facing=%s,in_wall=false,open=false,powered=false]"
                % ("east" if ga == "x" else "south"))
        else:
            fence_at(x, z)
    # a trodden path from the house's back to the gate
    for k in range(D - 1):
        x, z = world(gate, k)
        put(x, 0, z, "dirt_path" if noise(x, z, 2, 341) > 0.3 else "coarse_dirt")
    free = [(i, k) for i in range(1, w - 1) for k in range(D - 1) if i != gate]
    taken = set()

    def claim(cells):
        if all(c in free and c not in taken for c in cells):
            taken.update(cells)
            return True
        return False

    things = ["garden", "garden", "shed", "wood", "tree", "flowers", "barrels", "well"]
    rnd.shuffle(things)
    for thing in things[:3]:
        if thing == "garden" and D >= 6:
            cells = [(i, k) for i in range(1, w - 1) for k in range(2, D - 2) if abs(i - gate) > 0]
            cells = [c for c in cells if c not in taken]
            if len(cells) >= 6 and claim(cells):
                crop = rnd.choice(("carrots[age=7]", "potatoes[age=7]", "beetroots[age=3]", "wheat[age=7]", "cabbage"))
                for i, k in cells:
                    x, z = world(i, k)
                    if k % 2 == 0 or crop == "cabbage":
                        put(x, 0, z, "farmland[moisture=7]")
                        put(x, 1, z, "beetroots[age=2]" if crop == "cabbage" else crop)
                    else:
                        put(x, 0, z, "coarse_dirt")
        elif thing == "shed":
            i0 = 1 if gate > 2 else w - 4
            cells = [(i, k) for i in range(i0, i0 + 3) for k in (D - 3, D - 2)]
            if i0 >= 1 and i0 + 2 <= w - 2 and claim(cells):
                for i, k in cells:
                    x, z = world(i, k)
                    put(x, 0, z, "spruce_planks")
                    if k == D - 2:
                        put(x, 1, z, "spruce_planks")
                        put(x, 2, z, "spruce_planks")
                    elif i in (i0, i0 + 2):
                        put(x, 1, z, "spruce_fence")
                        put(x, 2, z, "spruce_fence")
                        FENCES.update({(x, 1, z), (x, 2, z)})
                    put(x, 3, z, "spruce_slab[type=bottom,waterlogged=false]")
                x, z = world(i0 + 1, D - 3)
                put(x, 1, z, rnd.choice(("barrel[facing=up,open=false]", "hay_block[axis=y]", "composter[level=4]")))
                x, z = world(i0, D - 3)
                put(x, 1, z, "spruce_fence")
        elif thing == "wood":
            k = D - 2
            cells = [(i, k) for i in range(1, w - 1) if i != gate][:3]
            if len(cells) == 3 and claim(cells):
                for n, (i, kk) in enumerate(cells):
                    x, z = world(i, kk)
                    log = "stripped_spruce_log[axis=%s]" % ("z" if axis == "z" else "x")
                    put(x, 1, z, log)
                    if n < 2:
                        put(x, 2, z, log)
        elif thing == "tree" and D >= 6:
            i, k = (1 if gate > 2 else w - 2), D // 2
            cells = [(i + di, k + dk) for di in (-1, 0, 1) for dk in (-1, 0, 1)]
            cells = [c for c in cells if 1 <= c[0] <= w - 2]
            if claim(cells):
                x, z = world(i, k)
                small_tree(x, 1, z, rnd.choice(("oak", "birch", "cherry")), h=rnd.randint(3, 5))
        elif thing == "flowers":
            cells = [(i, 0) for i in range(1, w - 1) if i != gate]
            if claim(cells):
                for i, k in cells:
                    x, z = world(i, k)
                    put(x, 1, z, pick(("poppy", 2), ("cornflower", 2), ("oxeye_daisy", 2), ("allium", 1),
                                      ("rose_bush[half=lower]", 0), ("azure_bluet", 2), ("short_grass", 2)))
        elif thing == "barrels":
            cells = [(1, 0), (1, 1)] if gate != 1 else [(w - 2, 0), (w - 2, 1)]
            if claim(cells):
                for n, (i, k) in enumerate(cells):
                    x, z = world(i, k)
                    put(x, 1, z, "barrel[facing=up,open=false]" if n == 0 else "composter[level=3]")
        elif thing == "well" and w >= 7 and D >= 7:
            ci = 2 if gate > 3 else w - 3
            ck = D // 2
            cells = [(ci + di, ck + dk) for di in (-1, 0, 1) for dk in (-1, 0, 1)]
            if claim(cells):
                for di in (-1, 0, 1):
                    for dk in (-1, 0, 1):
                        x, z = world(ci + di, ck + dk)
                        if di == 0 and dk == 0:
                            for y in range(-3, 1):
                                put(x, y, z, WATER)
                            put(x, -4, z, "ashbound:greystone")
                        else:
                            put(x, 0, z, "ashbound:greystone")
                            put(x, 1, z, "ashbound:greystone_wall" if (di and dk) else "ashbound:greystone_slab[type=bottom,waterlogged=false]")
                for di in (-1, 1):
                    x, z = world(ci + di, ck - 1)
                    for y in (2, 3):
                        put(x, y, z, "spruce_fence")
                        FENCES.add((x, y, z))
                for di in (-1, 0, 1):
                    for dk in (-1, 0, 1):
                        x, z = world(ci + di, ck + dk)
                        put(x, 4, z, "spruce_slab[type=bottom,waterlogged=false]")


# ================================================================ the market

def octo(x, z):
    """Distance in an octagon (a round basin laid in blocks reads cleaner with straight sides)."""
    return max(abs(x), abs(z), (abs(x) + abs(z)) / 1.3)


def fountain():
    """The fountain, laid in clean pale stone: an octagonal basin with a ledge to sit on and the Moonwell Priestess
    standing in it."""
    fx, fz = FOUNTAIN
    PL, SL = "ashbound:pale_limestone", "ashbound:pale_limestone_slab[type=bottom,waterlogged=false]"
    Q, QS = "smooth_quartz", "smooth_quartz_slab[type=bottom,waterlogged=false]"
    flow = "water[level=0]#flow"
    for x in range(-BASIN_R - 2, BASIN_R + 3):
        for z in range(-BASIN_R - 2, BASIN_R + 3):
            r = octo(x, z)
            X, Z = fx + x, fz + z
            if r > BASIN_R + 1.5:
                continue
            put(X, -1, Z, "smooth_stone")
            if r > BASIN_R + 0.5:                         # a low step round it
                put(X, 0, Z, "polished_andesite")
                put(X, 1, Z, SL)
            elif r > BASIN_R - 0.5:                       # the rim, a seat's height
                put(X, 0, Z, PL)
                put(X, 1, Z, "ashbound:carved_limestone" if (x == 0 or z == 0) else PL)
                put(X, 2, Z, SL)
            else:
                put(X, -2, Z, "smooth_stone")
                put(X, -1, Z, WATER)
                put(X, 0, Z, WATER)
                put(X, 1, Z, WATER)
                if noise(X * 3, Z * 3, 3, 81) > 0.8 and r > 6:
                    put(X, 2, Z, "lily_pad")
    # the Moonwell Priestess (E:/Ashbound tools/elfstatue.py) on a low pedestal rising out of the water, her basin held
    # overhead pouring moonwater back into the fountain; sea lanterns in the basin floor light her from below
    for x in range(-3, 4):
        for z in range(-3, 4):
            if octo(x, z) <= 2.5:
                for y in (-1, 0):
                    put(fx + x, y, fz + z, PL)
                put(fx + x, 1, fz + z, "ashbound:carved_limestone")
    for k in range(10):
        a = k * math.pi / 5
        put(fx + round(5.5 * math.cos(a)), -2, fz + round(5.5 * math.sin(a)), "sea_lantern")
    for px, py, pz, k in ELF_PIECES:
        put(fx + px, 2 + py, fz + pz, "ashbound:elf_statue[piece=%d]" % k)     # she faces south, down High Street
    print("  fountain: priestess %d pieces" % len(ELF_PIECES))


def stall_cells(bx, bz, facing):
    """A stall's 18 parts from its base (the counter's middle) as PropBlock.Stall lays them: (x, y, z, part)."""
    step = {"north": (0, -1), "east": (1, 0), "south": (0, 1), "west": (-1, 0)}
    right = {"north": "east", "east": "south", "south": "west", "west": "north"}[facing]
    back = {"north": "south", "south": "north", "east": "west", "west": "east"}[facing]
    cells = []
    for p in range(18):
        dx, dy, bk = p % 3 - 1, p // 3 % 3, p // 9 * 2
        x = bx + step[right][0] * dx + step[back][0] * bk
        z = bz + step[right][1] * dx + step[back][1] * bk
        cells.append((x, 1 + dy, z, p))
    return cells


def stall_fits(bx, bz, facing):
    return not any(ROAD.get((x, z), (None,))[0] is None or ROAD[(x, z)][0].kind != "market" or ROAD[(x, z)][1] > 0.8
                   or built(x, z, 0, 3) for x, _, z, _ in stall_cells(bx, bz, facing))


def stall(bx, bz, facing, trade, check=True):
    """A market stall, its counter looking `facing` (where the buyers stand)."""
    if check and not stall_fits(bx, bz, facing):
        return False
    for x, y, z, p in stall_cells(bx, bz, facing):
        put(x, y, z, "ashbound:stall_%s[facing=%s,part=%d]" % (trade, facing, p))
    return True


def market_dressing():
    """The fountain in the middle of the market, lamps and benches round the basin, the square kept open (the shops
    round it do the selling)."""
    fountain()
    fx, fz = FOUNTAIN
    for a in range(4):
        ang = math.radians(45 + 90 * a)
        lamp(round(fx + (BASIN_R + 4) * math.cos(ang)), round(fz + (BASIN_R + 4) * math.sin(ang)), "x" if a % 2 else "z")
    for dx, dz in ((0, -BASIN_R - 3), (0, BASIN_R + 3), (-BASIN_R - 3, 0), (BASIN_R + 3, 0)):
        for s in (-2, 2):                               # looking at the fountain, their backs to the market
            if dx == 0:
                bench(fx + s, fz + dz, "south" if dz < 0 else "north")
            else:
                bench(fx + dx, fz + s, "east" if dx < 0 else "west")


# ---------------------------------------------------------------- every street lit

GLOW = {"lantern": 15, "soul_lantern": 10, "torch": 14, "wall_torch": 14, "soul_torch": 10, "soul_wall_torch": 10,
        "campfire": 15, "soul_campfire": 10, "glowstone": 15, "sea_lantern": 15, "shroomlight": 15, "jack_o_lantern": 15,
        "lava": 15, "fire": 15, "magma_block": 3, "end_rod": 14, "beacon": 15, "ochre_froglight": 15,
        "verdant_froglight": 15, "pearlescent_froglight": 15, "wall_lantern": 14, "candle_rack": 12,
        "lit_leaded_glass_pane": 11, "street_lamp": 15, "stall_lanterns": 15, "stall_candles": 12, "vigil_candles": 9}
CLEAR = ("cross", "flat", "lantern", "torch", "wall_torch", "chain", "candle", "pane", "fence", "banner", "wall_banner",
         "sign", "wall_sign", "wall", "gate", "trapdoor", "door", "ladder")


def glow(st):
    n, props = K.parse(st)
    n = K.short(n)
    if n == "light":
        return int(props.get("level", 15))
    if n.endswith("candle"):
        return 3 * int(props.get("candles", 1)) if props.get("lit") == "true" else 0
    if n in ("campfire", "soul_campfire") and props.get("lit") == "false":
        return 0
    return GLOW.get(n, 0)


LAMP_EVERY = {"market": 11, "square": 11, "hearth": 12, "main": 13, "walk": 13, "green": 14, "lane": 15, "alley": 0}
POST_GAP = 9                  # lamp posts stand at least this far apart
STEP = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}


def approaches():
    """The ground before every way in - each door (both sides), every arch, passage and gate - kept clear: three
    cells out and one either side of the opening."""
    B = S.B
    keep = set()

    def mark(x, z, dx, dz, depth=3):
        for k in range(depth + 1):
            for l in (-1, 0, 1):
                keep.add((x + dx * k + dz * l, z + dz * k + dx * l))
    for (x, y, z), st in B.items():
        if "_door[" in st and "half=lower" in st and "trapdoor" not in st:
            dx, dz = STEP[st.split("facing=")[1].split(",")[0].split("]")[0]]
            mark(x, z, dx, dz)
            mark(x, z, -dx, -dz)

    def walk(x, z, g):
        return all(B.get((x, y, z)) in (None, "air", LIGHT) or "carpet" in B[(x, y, z)] for y in (g + 1, g + 2))

    def covered(x, z, g):
        return any(K.solid(B.get((x, y, z))) and "leaves" not in B[(x, y, z)] for y in range(g + 3, g + 9))
    cols = {(x + a, z + b) for r in ROADS for (x, z) in r.cells for a in (-4, 0, 4) for b in (-4, 0, 4)}
    for x, z in cols:
        if (x, z) in FRONT:
            continue                                       # under a jetty, not a way in
        g = GROUND(x, z)
        if not (walk(x, z, g) and covered(x, z, g)):
            continue
        for dx, dz in STEP.values():
            q = (x + dx, z + dz)
            if GROUND(*q) == g and walk(q[0], q[1], g) and not covered(q[0], q[1], g):
                mark(q[0], q[1], dx, dz)
    return keep


def light_streets():
    """Every street lit the way a town lights them: a light every few doors down each street, on alternate sides -
    a lantern on a house front where the slot has a bare stretch of wall, else a post on the kerb - and never one
    before a door, an arch or a passage, out in a junction, or crowding a bench or a stall. A slot that already has a
    light near it (a door lantern, a square's own lamps) is left as it is."""
    B = S.B
    keep = approaches()
    roadc = set(ROAD)

    def ground_free(x, z, g, h):
        return all(B.get((x, y, z)) in (None, "air") for y in range(g + 1, g + h + 1))

    def remove_post(x, z):
        g = GROUND(x, z)
        for y in range(g + 1, g + 4):
            if "street_lamp" in (B.get((x, y, z)) or ""):
                B[(x, y, z)] = "air"
        for dx, dz in STEP.values():
            if B.get((x + dx, g + 2, z + dz)) == LIGHT:
                B[(x + dx, g + 2, z + dz)] = "air"
    posts_at = []
    pruned = 0
    for (x, y, z), st in list(B.items()):
        if st.startswith("ashbound:street_lamp") and "part=0" in st:
            if (x, z) in keep:                 # a post set down before a way in by a set piece: it goes
                remove_post(x, z)
                pruned += 1
            else:
                posts_at.append((x, z))
    lights = list(posts_at)
    for (x, y, z), st in B.items():
        n = st.split("[")[0]
        if (n.endswith("wall_lantern") or n.endswith(":lantern") or n == "lantern" or "brazier" in n) \
                and (x, z) not in posts_at and y - GROUND(x, z) <= 5:
            lights.append((x, z))

    def lit(x, z, rad):
        return any(abs(x - a) + abs(z - b) <= rad for a, b in lights)

    def post_at(x, z, axis):
        """A post on the kerb: at the street's edge (ground that isn't street beside it), clear of everything."""
        g = GROUND(x, z)
        if (x, z) in keep or wet(x, z) or (x, z) in YARD or not ground_free(x, z, g, 4):
            return False
        if not any((x + dx, z + dz) not in roadc and GROUND(x + dx, z + dz) >= g for dx, dz in STEP.values()):
            return False                       # out in the street or a junction, not at its edge
        if any(abs(x - a) + abs(z - b) < POST_GAP for a, b in posts_at):
            return False
        if any(B.get((x + a, g + 1, z + b)) not in (None, "air") and (x + a, z + b) not in YARD
               and "carpet" not in B[(x + a, g + 1, z + b)] for a in (-1, 0, 1) for b in (-1, 0, 1) if (a, b) != (0, 0)):
            return False                       # not crowding a bench, a stall, a crate or a wall's foot
        if any("_stairs" in (B.get((x + a, y, z + b)) or "") for a in range(-2, 3) for b in range(-2, 3)
               for y in range(g, g + 3)):
            return False                       # never in the way of a flight's foot or head
        dx, dz = (1, 0) if axis == "x" else (0, 1)
        for p in range(3):
            B[(x, g + 1 + p, z)] = "ashbound:street_lamp[axis=%s,part=%d]" % (axis, p)
        for s in (-1, 1):
            q = (x + s * dx, g + 2, z + s * dz)
            if B.get(q) in (None, "air") and q[1] > GROUND(q[0], q[2]):
                B[q] = LIGHT
        posts_at.append((x, z))
        lights.append((x, z))
        return True

    def on_front(x, z, nx, nz):
        """A lantern on the house front past the kerb at x, z (looking out along nx, nz): on a pier of bare wall,
        not over a door or a window, nor beside a sign."""
        g = GROUND(x, z)
        for r in (1, 2, 3):
            wx, wz = x + nx * r, z + nz * r
            wall = B.get((wx, g + 3, wz))
            if wall is None or wall == "air":
                continue
            cx, cz = wx - nx, wz - nz
            q = (cx, g + 3, cz)
            if not K.solid(wall) or B.get(q) not in (None, "air") or GROUND(cx, cz) != g:
                return False
            ax, az = abs(nz), abs(nx)               # along the wall
            for k in (-1, 0, 1):
                for y in (g + 1, g + 2, g + 3, g + 4):
                    k_, n_ = K._kind(B.get((wx + ax * k, y, wz + az * k)) or "air")[:2]
                    if k_ in ("door", "pane") or "glass" in n_ or "shutter" in n_:
                        return False
            if any(B.get((cx + ax * k, g + 3, cz + az * k)) not in (None, "air") for k in (-1, 1)):
                return False                         # a sign, a bracket, a lantern already
            face = "east" if nx < 0 else "west" if nx > 0 else "south" if nz < 0 else "north"
            B[q] = "ashbound:wall_lantern[facing=%s]" % face
            lights.append((cx, cz))
            return True
        return False
    posts = fronts = 0
    for r in sorted(ROADS, key=lambda r: -RANK[r.kind]):
        every = LAMP_EVERY.get(r.kind, 0)
        if not every:
            continue
        run, nxt, side = 0.0, every / 2, 1
        sm = r.samples
        for i in range(1, len(sm)):
            run += math.dist(sm[i - 1][:2], sm[i][:2])
            if run < nxt:
                continue
            nxt += every
            px, pz = sm[i][:2]
            if lit(round(px), round(pz), every // 2 + 1):
                continue                         # a door lantern, a square's lamps already light this stretch
            done = False
            for di in (0, 4, -4, 8, -8, 12, -12):         # a sample is a quarter block: up to 3 blocks along
                j = i + di
                if not 0 <= j < len(sm):
                    continue
                qx, qz, hw, tx, tz, _ = sm[j]
                axis = "x" if abs(tz) > abs(tx) else "z"
                for s in (side, -side):
                    nx, nz = -tz * s, tx * s                 # the normal out to this side
                    ex, ez = round(qx + nx * (hw - 0.5)), round(qz + nz * (hw - 0.5))
                    n4x, n4z = (round(nx), 0) if abs(nx) >= abs(nz) else (0, round(nz))
                    if (ex, ez) not in r.cells:
                        continue
                    if on_front(ex, ez, n4x, n4z):
                        fronts += 1
                        done = True
                    elif post_at(ex, ez, axis):
                        posts += 1
                        done = True
                    if done:
                        side = -s
                        break
                if done:
                    break
    print("  lit: %d lamp posts, %d lanterns on house fronts; %d posts taken out of doorways" % (posts, fronts, pruned))


# ================================================================ the green and the inn

def green_path(x, z):
    """The paths worn across the green: north to south with the lane, west to the inn's door, east to the back lane."""
    cx, cz = GREEN
    edge = noise(x, z, 3, 352)
    if abs(x - cx) <= 1 or (x < cx and abs(z - cz) <= 1) or (x > cx and abs(z - cz - 2) <= 1):
        return "coarse_dirt" if edge > 0.7 else "dirt_path"
    return None


def big_tree(cx, cz, h=7):
    """The green's oak: a thick trunk, four boughs and a broad crown."""
    leaf = "oak_leaves[distance=1,persistent=true,waterlogged=false]"
    for y in range(1, h + 1):
        put(cx, y, cz, "oak_log[axis=y]")
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):         # root flare
        put(cx + dx, 1, cz + dz, "oak_wood[axis=y]")
    blobs = [(cx, h + 2, cz, 4.6)]
    for k, (dx, dz) in enumerate(((1, 1), (-1, 1), (1, -1), (-1, -1))):
        y0 = h - 2 + k % 2
        for i in (1, 2, 3):
            put(cx + dx * i, y0 + (i > 1), cz + dz * i, "oak_log[axis=%s]" % ("x" if k % 2 else "z"))
        blobs.append((cx + dx * 3, y0 + 3, cz + dz * 3, 3.0))
    for bx, by, bz, r in blobs:
        R = int(r) + 1
        for x in range(bx - R, bx + R + 1):
            for z in range(bz - R, bz + R + 1):
                for y in range(by - R, by + R + 1):
                    d = math.sqrt((x - bx) ** 2 + ((y - by) * 1.35) ** 2 + (z - bz) ** 2)
                    if d < r + 0.6 * (noise(x * 3 + y, z * 3 - y, 2, 353) - 0.5) and (x, y, z) not in S.B:
                        put(x, y, z, leaf)


def well(cx, cz):
    """A round well: a greystone kerb, water deep in it, two posts and a little shingle roof over the windlass."""
    for x in range(cx - 1, cx + 2):
        for z in range(cz - 1, cz + 2):
            if (x, z) == (cx, cz):
                for y in range(-3, 1):
                    put(x, y, z, WATER)
                put(x, -4, z, "ashbound:greystone")
            else:
                put(x, 0, z, "ashbound:greystone")
                put(x, 1, z, "ashbound:greystone_wall" if (x - cx) * (z - cz) else "ashbound:greystone")
    for x in (cx - 1, cx + 1):
        for y in (2, 3):
            put(x, y, cz, "spruce_fence")
            FENCES.add((x, y, cz))
    put(cx, 3, cz, "spruce_fence")
    FENCES.add((cx, 3, cz))
    for x in range(cx - 1, cx + 2):
        put(x, 4, cz - 1, "ashbound:wood_shingle_stairs[facing=south,half=bottom,shape=straight,waterlogged=false]")
        put(x, 4, cz + 1, "ashbound:wood_shingle_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]")
        put(x, 4, cz, "ashbound:wood_shingles")
    put(cx, 2, cz, "chain[axis=y,waterlogged=false]")


def outdoor_table(x, z):
    """A cask stood on end out in front of the inn for a table, a candle on it, a bench either side."""
    if any(built(x, z + d, 1, 2) for d in (-1, 0, 1)):
        return
    put(x, 1, z, "barrel[facing=up,open=false]")
    put(x, 2, z, "candle[candles=2,lit=true,waterlogged=false]")
    seat(x, z - 1, x, z)
    seat(x, z + 1, x, z)


def stable(x0, z0, x1, z1):
    """The inn's stable yard behind it: a fenced paddock with a gate, a lean-to stable of stalls along the north
    fence (plank back, log posts, a slab roof), hay and a trough."""
    if not plot_ok(x0, z0, x1, z1):
        return False
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            YARD.add((x, z))
            if x in (x0, x1) or z in (z0, z1):
                fence_at(x, z)
            elif noise(x, z, 3, 361) > 0.55:
                put(x, 0, z, "coarse_dirt")
    put((x0 + x1) // 2, 1, z1, "spruce_fence_gate[facing=south,in_wall=false,open=false,powered=false]")
    for x in range(x0 + 1, x1):                      # the stable
        for y in (1, 2, 3):
            put(x, y, z0 + 1, "spruce_planks")
        for z in range(z0 + 1, z0 + 5):
            put(x, 4, z, "spruce_slab[type=top,waterlogged=false]")
            if z > z0 + 1:
                put(x, 0, z, "coarse_dirt")
        if (x - x0 - 1) % 3 == 0 or x == x1 - 1:
            for y in (1, 2, 3):
                put(x, y, z0 + 4, "spruce_log[axis=y]")
            for z in (z0 + 2, z0 + 3):
                put(x, 1, z, "spruce_fence")
                FENCES.add((x, 1, z))
        elif (x - x0) % 3 == 0:
            put(x, 1, z0 + 2, "hay_block[axis=y]")
        else:
            put(x, 1, z0 + 2, "hay_block[axis=x]" if noise(x, z0, 2, 362) > 0.5 else "composter[level=4]")
    put(x0 + 2, 1, z1 - 2, "water_cauldron[level=3]")
    put(x1 - 2, 1, z1 - 2, "hay_block[axis=y]")
    put(x1 - 2, 2, z1 - 2, "hay_block[axis=y]")
    return True


def inn_and_green(green):
    """The green and the inn facing it across the grass from the west, its stable yard behind."""
    cx, cz = GREEN
    big_tree(cx + 4, cz - 4)
    well(cx + 4, cz + 5)
    for bx, bz, f in ((cx + 4, cz - 1, "south"), (cx + 1, cz - 4, "west"), (cx + 7, cz - 4, "east")):
        bench(bx, bz, f)                               # round the tree, backs to its trunk, looking out over the green
    lamp(cx - 2, cz + 7, "x")
    fn, w, d = H.INN
    front = min(x for (x, z) in green.cells) - 1     # the inn's jetty comes up to the grass
    x0, z0 = front - d + 1, cz - w // 2
    if plot_ok(x0, z0, front, z0 + w - 1):
        build_house(fn, (x0, z0), "east", {"roof": "ashbound:clay_roof_tile", "col": "ochre_plaster",
                                           "shutter": "ashbound:green_shutter"})
        LOG.append(("the inn", "w", "inn", (x0, z0, front, z0 + w - 1), front, {}))
        for z in range(z0, z0 + w):                   # under the jetties
            for x in range(front - 2, front + 1):
                if (x, 0, z) not in S.B:
                    FRONT.add((x, z))
        stable(x0 - 11, z0, x0 - 1, z0 + w - 1)
        print("  the inn at %d, %d" % (x0, z0))
    else:
        print("  no room for the inn at %d, %d" % (x0, z0))
    for z in (cz - 4, cz + 3):
        outdoor_table(front + 3, z)


def fill_gaps(x0=-210, x1=5, z0=40, z1=175, T=6):
    """Whatever's still open behind the houses becomes orchard or allotment: the open ground is cut in tiles, joined
    tiles make a plot, each fenced round with a gate toward the nearest street."""
    def free(x, z):
        return (open_ground(x, z) and in_town(x, z) and (x, z) not in ROAD and (x, z) not in FRONT
                and (x, z) not in ALLEY and (x, z) not in YARD)
    tiles = set()
    for tx in range(x0, x1, T):
        for tz in range(z0, z1, T):
            if all(free(x, z) for x in range(tx - 1, tx + T + 1) for z in range(tz - 1, tz + T + 1)):
                tiles.add((tx, tz))
    seen, plots = set(), []
    for t in sorted(tiles):
        if t in seen:
            continue
        group, stack = [], [t]
        seen.add(t)
        while stack:
            a = stack.pop()
            group.append(a)
            for dx, dz in ((T, 0), (-T, 0), (0, T), (0, -T)):
                n = (a[0] + dx, a[1] + dz)
                if n in tiles and n not in seen:
                    seen.add(n)
                    stack.append(n)
        if len(group) >= 2:
            plots.append(group)
    for group in plots:
        cells = {(x, z) for tx, tz in group for x in range(tx, tx + T) for z in range(tz, tz + T)}
        edge = {c for c in cells if any((c[0] + dx, c[1] + dz) not in cells for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
        mx = sum(c[0] for c in cells) / len(cells)
        mz = sum(c[1] for c in cells) / len(cells)
        orchard = noise(mx, mz, 40, 371) > 0.45
        YARD.update(cells)
        for c in edge:
            fence_at(*c)
        # the gate: the edge cell nearest a street (not a corner)
        near = [r for r in ROAD if min(abs(r[0] - c[0]) + abs(r[1] - c[1]) for c in ((mx, mz),)) < 60]

        def to_road(c):
            return min((abs(c[0] - r[0]) + abs(c[1] - r[1]) for r in near), default=999)
        sides = [c for c in edge if ((c[0] + 1, c[1]) in edge and (c[0] - 1, c[1]) in edge)
                 or ((c[0], c[1] + 1) in edge and (c[0], c[1] - 1) in edge)]
        best = min(sides or edge, key=to_road)
        horiz = (best[0] + 1, best[1]) in edge and (best[0] - 1, best[1]) in edge
        put(best[0], 1, best[1], "spruce_fence_gate[facing=%s,in_wall=false,open=false,powered=false]"
            % ("south" if horiz else "east"))
        inner = cells - edge
        if orchard:
            woods = ("oak", "birch", "cherry") if noise(mx, mz, 30, 372) > 0.5 else ("oak", "oak", "birch")
            for (x, z) in sorted(inner):
                if x % 5 == 2 and (z + 2 * ((x // 5) % 2)) % 5 == 2 and \
                        all((x + dx, z + dz) in inner for dx in (-1, 1) for dz in (-1, 1)):
                    small_tree(x, 1, z, woods[int(noise(x, z, 2, 373) * 2.99)], h=3 + (noise(x, z, 3, 374) > 0.6))
            for (x, z) in inner:
                if noise(x, z, 2, 375) > 0.62 and (x, 1, z) not in S.B:
                    put(x, 1, z, pick(("short_grass", 5), ("dandelion", 1), ("poppy", 1), ("azure_bluet", 1)))
        else:
            crops = ("carrots[age=7]", "potatoes[age=7]", "beetroots[age=3]", "wheat[age=7]", "wheat[age=5]")
            for (x, z) in inner:
                if all((x + dx, z + dz) in inner for dx in (-1, 0, 1) for dz in (-1, 0, 1)):
                    if z % 4 == 0:
                        put(x, 0, z, "dirt_path")
                    else:
                        put(x, 0, z, "farmland[moisture=7]")
                        put(x, -1, z, "dirt")
                        put(x, 1, z, crops[int(noise(x // 6 * 6, z // 4 * 4, 3, 376) * 4.99)])
        print("  %s of %d tiles at %d, %d" % ("orchard" if orchard else "allotments", len(group), mx, mz))


# ================================================================ the lake quarter

SHORE = {}
STILTS = (64, 79, 94, 107, 138)  # the fishers' cottages out on their posts (their west walls)
BOATHOUSE = 116
PIER_X = 128                  # the long pier out to the island
MILL = (145, 97)              # the mill's north-west corner on the river's west bank, its wheel in the river


def shore_z(x):
    """The south shore of the lake at x: its southernmost wet column."""
    if x not in SHORE:
        z = 140
        while z > -60 and L.lake_s(x, z) >= 1:
            z -= 1
        SHORE[x] = z
    return SHORE[x]


class Lift:
    """A Build seen dy blocks higher (houses put up on posts), greystone footings turned to timber sills."""

    def __init__(self, S, dy):
        self.S, self.dy = S, dy

    def __getattr__(self, k):
        return getattr(self.S, k)

    def put(self, x, y, z, st, nbt=None):
        if isinstance(st, str) and y == 1 and "greystone" in st:
            st = "stripped_spruce_log[axis=y]"
        self.S.put(x, y + self.dy, z, st, nbt)

    def get(self, x, y, z):
        return self.S.get(x, y + self.dy, z)


class Moor:
    """Where a ship from settlements.py is put: one lower (its waterline at our water), never over the land."""

    def put(self, x, y, z, st):
        y -= 1
        if y <= L.WATER_Y and not (wet(x, z) or (x, L.WATER_Y, z) in S.B):
            return
        put(x, y, z, st)


def ship(kind, x, z, k, seed):
    import random
    import settlements as ST
    sh = {"skiff": ST.skiff, "smack": ST.smack}[kind]("pine", random.Random(seed))
    sh.onto(Moor(), x, z, k)


def post(x, z, top=0, wood="spruce"):
    """A log post from the lake bed (or the ground) up to `top`."""
    for y in range(GROUND(x, z) + 1, top + 1):
        put(x, y, z, "%s_log[axis=y]" % wood)


def deck(x, z, y=0, edge=False):
    put(x, y, z, "stripped_spruce_log[axis=x]" if edge else "spruce_planks")
    for yy in range(y + 1, y + 4):
        if S.get(x, yy, z) in ("sugar_cane", "short_grass", "lily_pad"):
            put(x, yy, z, None)


def stilt_house(x0):
    """A fisher's cottage up on posts over the shallows, its door to the boardwalk, a step up to it."""
    kind = H.cottage if S.rnd.random() < 0.7 else H.house
    w, d = (6, 8) if kind is H.cottage else (7, 9)
    front = min(shore_z(x) for x in range(x0, x0 + w)) - 3
    z0 = front - d + 1
    HOUSES[0] += 1
    kind(Lift(S, 2), x0, z0, "south")
    for x in range(x0, x0 + w):
        for z in range(z0, front + 1):
            if x in (x0, x0 + w - 1, x0 + w // 2) and (z - z0) % 3 == 0 or z == front and x in (x0, x0 + w - 1):
                post(x, z, 1)
    put(x0 + 2, 1, front + 1, "spruce_planks")
    put(x0 + 2, 2, front + 1, "spruce_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]")
    put(x0 + 2, 1, front + 2, "spruce_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]")
    S.marks["fisher:%d" % x0] = (x0 + 2, 1, front + 3)
    return front, w


def boardwalk(fronts):
    """Planks on posts along the waterline from the quay's end to the mill, the cottages' steps off it."""
    for x in range(60, 145):
        sz = shore_z(x)
        z0 = fronts[x] + 1 if x in fronts else sz - 2
        for z in range(z0, sz + 2):
            if (x, z) in ROAD or built(x, z, 1, 2):
                continue
            deck(x, z, edge=(z == z0 and x not in fronts))
        if x % 4 == 0 and x not in fronts:
            post(x, z0, 0)
        if x % 12 == 6 and x not in fronts:
            put(x, 1, z0, "spruce_fence")
            put(x, 2, z0, "lantern[hanging=false,waterlogged=false]")
        elif x % 12 == 0 and x not in fronts and S.rnd.random() < 0.7:
            put(x, 1, z0 + 1, pick(("barrel[facing=up,open=false]", 2), ("ashbound:fish_crate[facing=south]", 2)))
            if S.rnd.random() < 0.5:
                put(x + 1, 1, z0 + 1, "ashbound:fish_crate[facing=south]")


def jetty(x, z1, n=6):
    """A finger jetty two planks wide out north from the boardwalk at z1, a skiff tied up alongside."""
    for z in range(z1 - n, z1 + 1):
        for dx in (0, 1):
            deck(x + dx, z)
        if (z1 - z) % 3 == 0:
            post(x, z, 0)
            post(x + 1, z, 0)
    put(x, 1, z1 - n, "spruce_fence")
    put(x, 2, z1 - n, "lantern[hanging=false,waterlogged=false]")
    ship("skiff", x + 4, z1 - n // 2 - 1, 0 if S.rnd.random() < 0.5 else 2, x)


def drying_rack(x, z):
    """Two posts and a pole, fish hung under it on trapdoors."""
    put(x, 1, z, "spruce_fence")
    put(x + 2, 1, z, "spruce_fence")
    for dx in range(3):
        put(x + dx, 2, z, "stripped_spruce_log[axis=x]")
    put(x + 1, 1, z, "spruce_trapdoor[facing=south,half=top,open=true,powered=false,waterlogged=false]")


def boathouse(x0, front):
    """Open to the lake at its north end over a slip, a skiff in it, the shore end walled with a door."""
    w, d = 7, 10
    z0 = front - d + 1
    F = H.Frame(S, x0, z0, w, d, "south")
    st = H.Style(S, roof="ashbound:wood_shingle", shutter=None, flowers=False)
    for lx in range(w):
        for lz in range(d):
            x, _, z = F.world(lx, 0, lz)
            side = lx in (0, w - 1)
            if side or lz == d - 1:
                post(x, z, 0) if lz % 3 == 0 or lz == d - 1 else None
                F.put(lx, 0, lz, "spruce_planks")
                for y in range(1, 5):                   # up to the eave the roof sits on
                    F.put(lx, y, lz, "spruce_log[axis=y]" if lz % 3 == 0 or lz == d - 1 else "spruce_planks")
    for y in range(1, 3):
        F.put(3, y, d - 1, None)
    F.put(3, 1, d - 1, "spruce_door[facing=south,half=lower,hinge=left,open=false,powered=false]")
    F.put(3, 2, d - 1, "spruce_door[facing=south,half=upper,hinge=left,open=false,powered=false]")
    for lz in range(d - 3, d - 1):
        for lx in range(1, w - 1):
            F.put(lx, 0, lz, "spruce_planks")
    H.gable_roof(F, st, 4, d - 1, steep=2)
    F.put(1, 1, d - 2, "barrel[facing=up,open=false]")
    F.put(w - 2, 1, d - 2, "ashbound:fish_crate[facing=north]")
    F.put(3, 3, 4, "lantern[hanging=true,waterlogged=false]")
    ship("skiff", x0 + 3, z0 + 3, 0, x0 * 7)


def island_pier():
    """The long pier from the boardwalk out to the island, lanterns down it, a resting place halfway."""
    z1 = shore_z(PIER_X) - 2
    z = z1
    while L.island_s(PIER_X, z) >= 1.0 and z > -40:
        z -= 1
    land = z
    mid = (land + z1) // 2
    for z in range(land - 1, z1 + 1):
        wide = abs(z - mid) <= 2
        for x in range(PIER_X - (3 if wide else 1), PIER_X + (4 if wide else 2)):
            if GROUND(x, z) < 0:
                deck(x, z, edge=False)
        if (z1 - z) % 4 == 0 and not wide:
            post(PIER_X - 1, z, 0)
            post(PIER_X + 1, z, 0)
        if (z1 - z) % 10 == 5:
            s = 1 if (z1 - z) % 20 == 5 else -1
            put(PIER_X + s, 1, z, "spruce_fence")
            put(PIER_X + s, 2, z, "lantern[hanging=false,waterlogged=false]")
    for x in (PIER_X - 3, PIER_X + 3):
        for z in (mid - 2, mid + 2):
            post(x, z, 0)
        put(x, 1, mid - 1, "ashbound:bench[facing=%s]" % ("east" if x < PIER_X else "west"))
        put(x, 1, mid + 1, "ashbound:bench[facing=%s]" % ("east" if x < PIER_X else "west"))
    ship("smack", PIER_X + 6, mid + 5, 0, 77)
    return land


def beacon(cx, cz, land):
    """The island's beacon: a round tower in pale limestone on a battered foot, a corbelled gallery, an open lantern
    stage with its fire, a slate spire; a path up to it from the pier."""
    gy = GROUND(cx, cz)
    low = min(GROUND(cx + dx, cz + dz) for dx in range(-7, 8) for dz in range(-7, 8))
    top = gy + 20
    for dx in range(-7, 8):
        for dz in range(-7, 8):
            r = math.hypot(dx, dz)
            x, z = cx + dx, cz + dz
            if r <= 6.4:                                   # the platform round its foot, the rock above it cut back
                for y in range(min(low, GROUND(x, z)) - 1, gy + 1):
                    put(x, y, z, "ashbound:limestone_bricks" if r > 5.5 else FLAG if y == gy else "ashbound:pale_limestone")
                for y in range(gy + 1, GROUND(x, z) + 1):
                    put(x, y, z, "air")
            if r > 5.4:
                continue
            for y in range(gy + 1, top + 1):
                k = y - gy
                ro = 4.9 if k <= 2 else 4.4 if k <= 3 else 4.0
                if r > ro + 0.4:
                    continue
                if r <= 2.6:
                    put(x, y, z, "air")
                    continue
                band = k in (8, 15)
                st = pick(("ashbound:limestone_bricks", 10), ("ashbound:mossy_limestone_bricks", 3 if k < 6 else 0),
                          ("ashbound:cracked_limestone_bricks", 1))
                if band or k <= 2:
                    st = "ashbound:pale_limestone"
                put(x, y, z, st)
            if 4.3 < r <= 5.4:
                put(x, top - 1, z, "ashbound:pale_limestone_stairs[facing=%s,half=top,shape=straight,waterlogged=false]"
                    % (("west" if dx > 0 else "east") if abs(dx) >= abs(dz) else ("north" if dz > 0 else "south")))
            for y in range(top, top + 1):
                put(x, y, z, "ashbound:pale_limestone")
            if 4.4 < r <= 5.4:
                put(x, top + 1, z, "ashbound:limestone_brick_wall")
    # slit windows up the shaft, the door to the south, a ladder up the north wall inside
    for k in (5, 11, 17):
        for dx, dz in ((0, 4), (4, 0), (0, -4), (-4, 0)):
            put(cx + dx, gy + k, cz + dz, "ashbound:leaded_glass_pane")
            put(cx + dx, gy + k + 1, cz + dz, "ashbound:leaded_glass_pane")
    for dz in range(3, 6):
        put(cx, gy + 1, cz + dz, "air")
        put(cx, gy + 2, cz + dz, "air")
    put(cx, gy + 1, cz + 4, "spruce_door[facing=north,half=lower,hinge=left,open=false,powered=false]")
    put(cx, gy + 2, cz + 4, "spruce_door[facing=north,half=upper,hinge=left,open=false,powered=false]")
    put(cx, gy + 3, cz + 5, "ashbound:wall_lantern[facing=south]")
    for y in range(gy + 1, top + 1):
        put(cx, y, cz - 2, "ladder[facing=south,waterlogged=false]")
    put(cx, top, cz - 1, "air")
    put(cx, top, cz - 2, "ladder[facing=south,waterlogged=false]")
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            if (dx, dz) != (0, -1) and (dx, dz) != (0, -2):
                put(cx + dx, top, cz + dz, "ashbound:pale_limestone")
    # the lantern stage: eight slim piers round the fire in its hearth, a cornice, a slate spire over it
    for y in range(top + 1, top + 5):
        for dx, dz in ((-3, -1), (-3, 1), (3, -1), (3, 1), (-1, -3), (1, -3), (-1, 3), (1, 3)):
            put(cx + dx, y, cz + dz, "ashbound:limestone_pillar[axis=y]")
    for dx in range(-1, 2):
        for dz in range(-1, 2):
            put(cx + dx, top + 1, cz + dz, "netherrack" if (dx, dz) != (0, 0) else "magma_block")
            put(cx + dx, top + 2, cz + dz, "fire[age=0,east=false,north=false,south=false,up=false,west=false]"
                if abs(dx) + abs(dz) != 2 else "campfire[facing=north,lit=true,signal_fire=false,waterlogged=false]")
    put(cx, top + 4, cz, LIGHT)
    for dx in range(-4, 5):
        for dz in range(-4, 5):
            r = math.hypot(dx, dz)
            if r <= 3.7:
                put(cx + dx, top + 5, cz + dz, "ashbound:pale_limestone" if r > 2.6 else "ashbound:limestone_bricks")
            elif r <= 4.5:
                put(cx + dx, top + 5, cz + dz, "ashbound:pale_limestone_slab[type=bottom,waterlogged=false]")
    for k in range(10):
        y = top + 6 + k
        rr = 3.4 * (1 - k / 10.0) ** 1.2
        for dx in range(-4, 5):
            for dz in range(-4, 5):
                r = math.hypot(dx, dz)
                if r <= rr + 0.3 and (r > rr - 1.2 or k == 0):
                    put(cx + dx, y, cz + dz, "deepslate_tiles")
    put(cx, top + 16, cz, "deepslate_tile_wall")
    put(cx, top + 17, cz, "lightning_rod[facing=up,powered=false,waterlogged=false]")
    # the path up from the pier, a few pines and boulders round it
    ph = gy + 1                                     # the first step flush with the platform's rim, just outside it
    for z in range(cz + 7, land + 2):
        nh = max(GROUND(cx, z), ph - 1)
        for dx in (-1, 0, 1):
            x = cx + dx
            for y in range(GROUND(x, z), nh):
                put(x, y, z, "ashbound:pale_limestone")
            for y in range(nh + 1, nh + 5):
                if GROUND(x, z) >= y:
                    put(x, y, z, "air")
            put(x, nh, z, "ashbound:pale_limestone_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]"
                if nh < ph else pick(("dirt_path", 4), ("coarse_dirt", 1), ("gravel", 1)) if GROUND(x, z) >= 0 else FLAG)
        ph = nh
    for a in (40, 130, 220, 300):
        r = 9.5
        x, z = round(cx + r * math.cos(math.radians(a))), round(cz + r * math.sin(math.radians(a)))
        if GROUND(x, z) >= 0:
            pine(x, GROUND(x, z) + 1, z, 6 + a % 3)


def pine(cx, y0, cz, h=7):
    for y in range(y0, y0 + h):
        put(cx, y, cz, "spruce_log[axis=y]")
    for y in range(y0 + 2, y0 + h + 2):
        rr = 2.6 * (1 - (y - y0 - 2) / (h + 0.5)) + (0.5 if (y - y0) % 2 else 0)
        for dx in range(-3, 4):
            for dz in range(-3, 4):
                if (dx or dz or y >= y0 + h) and math.hypot(dx, dz) <= rr and (cx + dx, y, cz + dz) not in S.B:
                    put(cx + dx, y, cz + dz, "spruce_leaves[distance=1,persistent=true,waterlogged=false]")


def mill():
    """The watermill on the river where it leaves the lake: greystone below, timber above, its door to Fishers'
    Row, the wheel turning in the river off its east wall, the millstones and the sacks inside."""
    x0, z0 = MILL
    w, d = 9, 11
    F = H.Frame(S, x0, z0, w, d, "west")
    st = H.Style(S, roof="ashbound:wood_shingle", shutter="ashbound:green_shutter", flowers=False)
    g = d - 1
    plank = "%s_planks" % st.wood
    HOUSES[0] += 1
    for lx in range(w):
        for lz in range(d):
            x, _, z = F.world(lx, 0, lz)
            for y in range(GROUND(x, z), 0):
                put(x, y, z, H.stone(S))
    F.box(0, 0, 0, w - 1, 0, g, plank)
    H.stone_storey(F, st, 1, g, front_windows=(1, 7))
    F.box(1, 5, 1, w - 2, 5, g, plank)
    H.framed_storey(F, st, 5, g)
    H.gable_roof(F, st, 8, g, steep=2)
    H.front_door(F, st, 4, g)
    H.sign(F, 6, g, 3)
    # the millstones on their bed, the hopper over them, sacks and barrels
    for lx in (3, 4, 5):
        for lz in (3, 4, 5):
            F.put(lx, 1, lz, "smooth_stone_slab[type=double,waterlogged=false]" if (lx, lz) != (4, 4) else "grindstone[face=floor,facing=north]")
    F.put(4, 2, 4, "hopper[enabled=true,facing=down]")
    F.put(4, 4, 4, "spruce_log[axis=y]")
    F.put(4, 3, 4, "spruce_fence")
    for lx, lz in ((1, 1), (2, 1), (1, 2), (7, 7), (7, 8)):
        F.put(lx, 1, lz, "ashbound:grain_sacks")
    F.put(1, 2, 1, "ashbound:grain_sacks")
    for lx, lz in ((7, 1), (7, 2)):
        F.put(lx, 1, lz, "barrel[facing=up,open=false]")
    F.put(4, 3, 7, "lantern[hanging=true,waterlogged=false]")
    for y in range(1, 6):
        F.put(1, y, 7, "ladder[facing=east,waterlogged=false]")
    F.put(1, 5, 7, None)
    # the wheel: an axle out of the east wall to a hub, two rims on four spokes each, paddles across between them,
    # its foot down in the river
    ex = x0 + d                                         # just past the east wall
    cz, cy, R = z0 + w // 2, 2, 5.6
    for x in range(ex, ex + 4):
        put(x, cy, cz, "stripped_dark_oak_log[axis=x]")
    rim = "stripped_spruce_wood[axis=x]"
    for dy in range(-7, 8):
        for dz in range(-7, 8):
            corners = [math.hypot(dy + a, dz + b) for a in (-0.5, 0.5) for b in (-0.5, 0.5)]
            ring = min(corners) <= R <= max(corners)    # the circle passes through this cell: an unbroken rim
            r = math.hypot(dy, dz)
            spoke = (dy == 0 or dz == 0 or abs(dy) == abs(dz)) and 0 < r < R - 0.6
            y, z = cy + dy, cz + dz
            for x in (ex + 1, ex + 3):
                if ring:
                    put(x, y, z, rim)
                elif spoke:
                    put(x, y, z, "spruce_log[axis=%s]" % ("y" if dz == 0 else "z") if dy == 0 or dz == 0 else rim)
            ang = math.degrees(math.atan2(dy, dz)) % 30
            if ring and r >= R - 0.2 and (ang < 8 or ang > 22):
                put(ex + 2, y, z, plank)
    put(ex + 4, cy, cz, "dark_oak_log[axis=x]")
    print("  the mill at %d, %d" % (x0, z0))


def quay_market():
    """Fish stalls along the quay's landward edge facing the water, crates and barrels by them, scales."""
    n = 0
    taken = []
    for x in range(14, 62):
        for z in range(66, 104):
            q = L.QUAY(x, z)
            if q is None or q < 1.03 or any(math.dist((x, z), p) < 9 for p in taken):
                continue
            cells = [(x + dx, z + dz) for dx in (-1, 0, 1) for dz in (0, 1, 2)]
            if any((L.QUAY(cx, cz) or 0) < 1.0 or (cx, cz) in ROAD or
                   any(S.get(cx, y, cz) not in (None, "air") for y in (1, 2, 3)) for cx, cz in cells):
                continue
            # the counter to the land, where the buyers walk; the fishmonger's back to the water
            for cx_, y, cz_, p in stall_cells(x, z + 2, "south"):
                put(cx_, y, cz_, "ashbound:stall_fish[facing=south,part=%d]" % p)
            put(x + 2, 1, z + 2, "ashbound:fish_crate[facing=south]")
            put(x - 2, 1, z + 1, "barrel[facing=up,open=false]")
            if n % 2 == 0:
                put(x + 2, 1, z + 1, "ashbound:merchant_scales[facing=south]")
            S.marks["fishmonger:%d:%d" % (x, z)] = (x, 1, z + 1)
            taken.append((x, z))
            n += 1
    print("  quay: %d fish stalls" % n)


def quay_piers():
    """Three piers out north from the quay's dressed edge, a smack tied up at each."""
    for px in (24, 40, 54):
        zs = [z for z in range(30, 120) if L.QUAY(px, z) is not None and L.QUAY(px, z) >= 1]
        if not zs:
            continue
        z1 = min(zs)
        n = 15
        for z in range(z1 - n, z1):
            for x in range(px - 1, px + 2):
                deck(x, z, edge=False)
            if (z1 - z) % 4 == 0:
                post(px - 1, z, 0)
                post(px + 1, z, 0)
        put(px - 1, 1, z1 - n, "spruce_fence")
        put(px - 1, 2, z1 - n, "lantern[hanging=false,waterlogged=false]")
        put(px + 1, 1, z1 - n, "barrel[facing=up,open=false]")
        ship("smack", px + 5, z1 - n + 6, 0 if px % 16 else 2, px)


def lake_quarter():
    """Fishers' Row: cottages on posts over the shallows, the boardwalk, jetties and skiffs, the boathouse, the long
    pier to the island and its beacon, piers and fish stalls on the quay, boats out on the water, the mill."""
    fronts = {}
    for x0 in STILTS:
        f, w = stilt_house(x0)
        for x in range(x0, x0 + w):
            fronts[x] = f
    bf = min(shore_z(x) for x in range(BOATHOUSE, BOATHOUSE + 7)) - 3
    boathouse(BOATHOUSE, bf)
    for x in range(BOATHOUSE, BOATHOUSE + 7):
        fronts[x] = bf
    land = island_pier()
    boardwalk(fronts)
    for x0 in (64, 79, 94, 138):
        jetty(x0 + 8, shore_z(x0 + 8) - 3)
    beacon(L.ISLAND[0], L.ISLAND[1], land)
    quay_piers()
    quay_market()
    for kind, x, z, k in (("skiff", 64, 40, 1), ("skiff", 96, 62, 3), ("skiff", 160, 30, 2), ("smack", 76, 30, 1)):
        ship(kind, x, z, k, x * 31 + z)
    mill()
    print("  fishers' row: %d cottages on posts" % len(STILTS))


# ================================================================ the guild terrace

LB, PL, GS = "ashbound:limestone_bricks", "ashbound:pale_limestone", "ashbound:greystone"
BODY, PLINTH = "stone_bricks", "polished_andesite"     # the guild's masonry: clean stone bricks, pale dressings
SLATE = "ashbound:slate_shingles"
TERRACE_MIX = (("townhouse", 5), ("house", 3))
HALL = (-24, -121, 24, -100)          # the guild hall: x0, z at its back, x1, z at its front (south, to the square)
TOWER = (-6, -110, 6, -98)            # its belfry, over the passage through the hall
YARD_T = (-76, -124, -36, -96)        # the training yard
QM = 32                               # the quartermaster's shop and the smithy beside it (west wall)


def stairs(mat, facing, half="bottom"):
    return "%s_stairs[facing=%s,half=%s,shape=straight,waterlogged=false]" % (mat, facing, half)


def tslab(mat):
    return "%s_slab[type=top,waterlogged=false]" % mat


TURN = {"north": "south", "south": "north", "east": "west", "west": "east"}


class ShiftB:
    """The Build's blocks seen dy higher."""

    def __init__(self, B, dy):
        self.B_, self.dy = B, dy

    def get(self, k, d=None):
        return self.B_.get((k[0], k[1] + self.dy, k[2]), d)

    def __contains__(self, k):
        return (k[0], k[1] + self.dy, k[2]) in self.B_

    def __len__(self):
        return len(self.B_)


class ShiftMarks:
    def __init__(self, m, dy):
        self.m, self.dy = m, dy

    def __setitem__(self, k, p):
        self.m[k] = (p[0], p[1] + self.dy, p[2])


class Shift:
    """The Build seen dy blocks higher, so the terrace's ground is at 0 as the lower city's is and the streets, the
    house kit and the paving all work up there unchanged."""

    def __init__(self, S, dy):
        self.S, self.dy = S, dy
        self.B = ShiftB(S.B, dy)
        self.marks = ShiftMarks(S.marks, dy)

    def __getattr__(self, k):
        return getattr(self.S, k)

    def put(self, x, y, z, st, nbt=None):
        self.S.put(x, y + self.dy, z, st, nbt)

    def get(self, x, y, z):
        return self.S.get(x, y + self.dy, z)


HEADS = []        # the top step of each grand stair (world y): put back if the paving above is laid over it


class tier:
    """with tier(20): ... builds with the terrace's ground as 0."""

    def __init__(self, dy):
        self.dy = dy

    def __enter__(self):
        global S, put, GROUND
        self.saved = S, put, GROUND
        g0 = GROUND
        S = Shift(S, self.dy)
        put = S.put
        GROUND = lambda x, z: g0(x, z) - self.dy

    def __exit__(self, *a):
        global S, put, GROUND
        S, put, GROUND = self.saved


def grand_stair(cx, z0, hw, rise=L.TERRACE, newels=True):
    """A straight flight up a bank, one step a block from the foot at z0 northward (the bank's own curve cut into or
    built out to it), its cheeks in pale limestone with a rail, lamps on the newels, braziers at the foot."""
    for i in range(0, rise + 2):                # the foot, a step a block up to the bank's top, a landing flush with it
        z = z0 - i
        for dx in range(-hw - 2, hw + 3):
            x = cx + dx
            g = GROUND(x, z)
            low = min(g, GROUND(x, z + 1), GROUND(x, z - 1)) - 2
            edge = abs(dx) - hw          # 1 the inner cheek, 2 the outer
            top = min(i, rise) if edge <= 0 else min(i, rise) + (1 if edge == 1 else 0)
            for y in range(low, top):
                put(x, y, z, BODY if edge == 2 else LB if edge > 0 or y < top - 1 else PL)
            if 0 < i <= rise and edge <= 0:
                mat = "ashbound:limestone_brick" if abs(dx) <= 1 else "stone_brick" if abs(dx) == hw else "ashbound:pale_limestone"
                put(x, i, z, stairs(mat, "north"))
                if i == rise:
                    HEADS.append((x, i + getattr(S, "dy", 0), z, stairs(mat, "north")))
            elif edge <= 0:
                put(x, min(i, rise), z, FLAG)
            elif edge == 1:
                put(x, top, z, PL)
                put(x, top + 1, z, "ashbound:pale_limestone_wall")
            else:
                put(x, top, z, stairs("stone_brick", "north") if 0 < i <= rise else BODY)
            for y in range(top + (2 if edge == 1 else 1), max(g, top) + 5):
                if (x, y, z) not in S.B:
                    put(x, y, z, "air")
        if newels and (i % 5 == 0 or i == rise + 1):
            ii = min(i, rise)
            for s in (-1, 1):
                x = cx + s * (hw + 1)
                for y in range(ii + 1, ii + 3):
                    put(x, y, z, PL)
                put(x, ii + 3, z, "ashbound:carved_limestone")
                put(x, ii + 4, z, "lantern[hanging=false,waterlogged=false]")
    # the foot: two braziers on plinths either side
    for s in (-1, 1):
        for dx in (hw + 1, hw + 2):
            for dz in (0, 1):
                x, z = cx + s * dx, z0 + dz
                for y in range(GROUND(x, z) + 1, 3):
                    put(x, y, z, PL)
                put(x, 3, z, "ashbound:carved_limestone")
        put(cx + s * (hw + 2), 4, z0, "campfire[facing=south,lit=true,signal_fire=false,waterlogged=false]")


def walk_stone(x, z, u, kind):
    """The terrace's paving: pale flagstone, a kerb of limestone bricks, the guild's seal in rings on the square."""
    if kind == "square":
        r = math.hypot(x, (z + 91) * 1.3)
        if r < 1.2:
            return "ashbound:gilded_tiles"
        if r < 7.5:
            return (PL, "ashbound:statue_stone", "polished_andesite")[int(r * 0.8) % 3]
        if r < 8.5:
            return "ashbound:gilded_tile_slab[type=bottom,waterlogged=false]" if int(math.degrees(math.atan2(z + 91, x))) % 30 < 4 else LB
    if u > 0.86:
        return LB
    b = noise(x, z, 6, 401)
    if b > 0.7:
        return "ashbound:statue_stone"
    if b < 0.18:
        return PL
    return FLAG


def lip_parapet():
    """A balustrade where the terrace's paving meets the bank's edge, so the lake's view is had leaning on it."""
    for (x, z), (r, u) in ROAD.items():
        if r.kind not in ("walk", "square") or GROUND(x, z) != 0 or wet(x, z) or abs(x) <= 9 and r.kind == "square":
            continue
        if GROUND(x, z + 1) < 0 or GROUND(x, z + 2) < -1:
            if not built(x, z, 1, 1):
                put(x, 1, z, "ashbound:pale_limestone_wall")
                if (x * 7 + z) % 11 == 0:
                    put(x, 1, z, PL)
                    put(x, 2, z, "lantern[hanging=false,waterlogged=false]")


# ---------------------------------------------------------------- the hall

def window(face, c, o, i, y0, y1, out):
    """A tall pointed window in a two-thick wall: its opening in the outer layer (index o) with pale jambs, a sill
    and an arch, the glass set back in the inner layer (i). face 'x' runs along x (a front or back), 'z' along z."""
    def at(a, y, d):
        return (a, y, d) if face == "x" else (d, y, a)
    lo, hi = ("west", "east") if face == "x" else ("north", "south")
    for a in range(c - 1, c + 2):
        for y in range(y0, y1 + 1):
            put(*at(a, y, o), "air")
            put(*at(a, y, i), "ashbound:leaded_glass_pane")
        put(*at(a, y0 - 1, o), stairs("ashbound:pale_limestone", TURN[out]))
    put(*at(c, y1 + 1, o), "air")
    put(*at(c, y1 + 1, i), "ashbound:leaded_glass_pane")
    put(*at(c - 1, y1 + 1, o), stairs("ashbound:pale_limestone", lo, "top"))
    put(*at(c + 1, y1 + 1, o), stairs("ashbound:pale_limestone", hi, "top"))
    put(*at(c, y1 + 2, o), PL)


def wall_stone(y, quoin=False):
    if y <= 2:
        return PLINTH
    if y in (3, 13) or quoin and y % 2 == 0:
        return PL
    return pick((BODY, 40), ("cracked_stone_bricks", 1), ("mossy_stone_bricks", 1 if y < 6 else 0))


def turret(cx, cz, y0, y1, r=2.3, cone=10, mat="deepslate_tiles"):
    """A round corner turret corbelled out from y0, its shaft to y1, a pointed cone over it."""
    for dx in range(-4, 5):
        for dz in range(-4, 5):
            d = math.hypot(dx + 0.5 - (cx % 1), dz + 0.5 - (cz % 1))
            x, z = math.floor(cx) + dx, math.floor(cz) + dz
            for y in range(y0, y1 + 1):
                ro = r - 1.0 if y == y0 else r - 0.5 if y == y0 + 1 else r
                if d <= ro:
                    put(x, y, z, PL if y in (y0, y1) or (y - y0) % 6 == 5 else BODY)
            if r < d <= r + 0.9:
                put(x, y1, z, stairs("ashbound:pale_limestone", "north" if abs(dz) >= abs(dx) and dz > 0 else
                                     "south" if abs(dz) >= abs(dx) else "west" if dx > 0 else "east", "top"))
            for k in range(cone):
                rr = (r + 0.6) * (1 - k / cone) ** 1.1
                if d <= rr + 0.2 and (d > rr - 1.3 or k == 0):
                    put(x, y1 + 1 + k, z, mat)
    for k, (dx, dz) in enumerate(((0, 1), (1, 0), (0, -1), (-1, 0))):
        x, z = math.floor(cx) + round(dx * r), math.floor(cz) + round(dz * r)
        put(x, y0 + 4 + 3 * (k % 2), z, "ashbound:leaded_glass_pane")
    top = y1 + cone + 1
    put(math.floor(cx), top - 1, math.floor(cz), "ashbound:gilded_tiles")
    put(math.floor(cx), top, math.floor(cz), "end_rod[facing=up]")


def octo(dx, dz):
    return max(abs(dx), abs(dz), (abs(dx) + abs(dz)) / 1.42)


def guild_hall():
    """The adventurers' guild: a long hall in pale limestone under a steep slate roof, crow-stepped gables, corner
    turrets, and over the passage through its middle a belfry with a clock, its bells, a gallery and a tall dark spire.
    The west wing is the gate hall (the gate board, the clerks' counter, tables, a hearth), the east the trophy hall."""
    X0, Z0, X1, Z1 = HALL
    TX0, TZ0, TX1, TZ1 = TOWER
    EAVE = 14

    def outer(x, z):
        return x in (X0, X1) or z in (Z0, Z1)

    def in_tower(x, z):
        return TX0 <= x <= TX1 and TZ0 <= z <= TZ1

    def passage(dx, y):
        return abs(dx) <= 2 and y <= 6 or abs(dx) <= 1 and y == 7 or dx == 0 and y == 8

    # the ground made good: a flagstone apron round it, footings under it
    for x in range(X0 - 3, X1 + 4):
        for z in range(Z0 - 3, Z1 + 4):
            for y in (-2, -1):
                put(x, y, z, GS)
            put(x, 0, z, FLAG)
            for y in range(1, 6):
                if S.get(x, y, z) is None:
                    put(x, y, z, "air")
    # the walls
    for x in range(X0, X1 + 1):
        for z in range(Z0, Z1 + 1):
            shell = x in (X0, X0 + 1, X1 - 1, X1) or z in (Z0, Z0 + 1, Z1 - 1, Z1)
            if in_tower(x, z):
                continue
            quoin = x in (X0, X1) and z in (Z0, Z0 + 1, Z1 - 1, Z1) or z in (Z0, Z1) and x in (X0 + 1, X1 - 1)
            for y in range(1, EAVE + 1):
                if abs(x) <= 2 and passage(x, y):
                    put(x, y, z, "air")
                elif shell:
                    put(x, y, z, wall_stone(y, quoin))
                elif abs(x) == 3 and y <= 10 or abs(x) <= 2 and y <= 9:
                    put(x, y, z, BODY if y > 2 else PLINTH)       # the passage's walls and vault behind the tower
                else:
                    put(x, y, z, "air")
            put(x, 0, z, FLAG)
    # the battered plinth all round, a cornice at the eaves on the long sides
    for x in range(X0 - 1, X1 + 2):
        for z in range(Z0 - 1, Z1 + 2):
            if X0 <= x <= X1 and Z0 <= z <= Z1 or in_tower(x, z):
                continue
            f = "south" if z < Z0 else "north" if z > Z1 else "east" if x < X0 else "west"
            if not (abs(x) <= 2 and z < Z0):      # never across the passage out the back, to the court
                put(x, 1, z, stairs("polished_andesite", f))
            if Z0 <= z <= Z1 or X0 <= x <= X1 and not TX0 - 1 <= x <= TX1 + 1:
                if z < Z0 or z > Z1:
                    put(x, EAVE, z, stairs("ashbound:pale_limestone", f, "top"))
    # buttresses on the long sides and the gable ends
    for bx in (-18, -12, 12, 18):
        for sgn, zf in ((1, Z1), (-1, Z0)):
            for k in (1, 2):
                z = zf + sgn * k
                for y in range(1, (8 if k == 2 else 12)):
                    put(bx, y, z, PLINTH if y <= 2 else BODY)
                put(bx, 8 if k == 2 else 12, z, stairs("stone_brick", "north" if sgn > 0 else "south"))
    for bx in (-18, -12, 12, 18):
        for y, st in ((12, PL), (13, PL), (14, PL), (15, PL), (16, "ashbound:pale_limestone_wall"),
                      (17, "ashbound:pale_limestone_wall"), (18, "end_rod[facing=up]")):
            put(bx, y, Z1 + 1, st)
    for bz in (-114, -107):
        for sgn, xf in ((1, X1), (-1, X0)):
            for k in (1, 2):
                x = xf + sgn * k
                for y in range(1, (8 if k == 2 else 12)):
                    put(x, y, bz, PLINTH if y <= 2 else BODY)
                put(x, 8 if k == 2 else 12, bz, stairs("stone_brick", "west" if sgn > 0 else "east"))
    # windows: the front and the east wing's back, the gable ends either side of the hearth / the trophy wall
    for c in (-21, -15, -9, 9, 15, 21):
        if abs(c) == 15:                          # each wing's own door off the square, a window over it
            portal("x", c, Z1, Z1 - 1, w=1, h=4)
            window("x", c, Z1, Z1 - 1, 8, 10, "south")
            for d in (-2, 2):
                put(c + d, 4, Z1 + 1, "ashbound:wall_lantern[facing=south]")
        else:
            window("x", c, Z1, Z1 - 1, 4, 9, "south")
    for c in (-117, -104):
        window("z", c, X0, X0 + 1, 4, 9, "west")
        window("z", c, X1, X1 - 1, 4, 9, "east")
    # the roof: slate, a full course under every row of stairs, crow-stepped gables at the ends standing over it
    for k in range(12):
        y = 15 + k
        for x in range(X0 + 2, X1 - 1):
            for z, f in ((Z1 + 1 - k, "north"), (Z0 - 1 + k, "south")):
                put(x, y, z, stairs("ashbound:slate_shingle", f))
                if k:
                    put(x, y - 1, z, SLATE)
    for x in (X0, X0 + 1, X1 - 1, X1):
        for z in range(Z0, Z1 + 1):
            k = min(z - Z0, Z1 - z)
            yt = 18 + 2 * (k // 2)
            for y in range(EAVE + 1, yt + 1):
                put(x, y, z, PL if y == yt else BODY)
            if x in (X0, X1):
                put(x, yt + 1, z, SLAB % "ashbound:pale_limestone")
    for s in (-1, 1):
        for z in (-111, -110):
            for y in range(28, 31):
                put(s * 24, y, z, PL)
        put(s * 24, 31, -111, stairs("ashbound:pale_limestone", "south"))
        put(s * 24, 31, -110, stairs("ashbound:pale_limestone", "north"))
    # dormers on the front slope, either wing
    for c in (-20, -14, 14, 20):
        for z in range(Z1 - 1, Z1 - 7, -1):
            for dx in (-1, 0, 1):
                for y in (17, 18, 19):
                    put(c + dx, y, z, PL if abs(dx) == 1 or z < Z1 - 1 else "ashbound:leaded_glass_pane")
                put(c + dx, 16, z, PL)
            put(c - 2, 19, z, stairs("ashbound:slate_shingle", "east"))
            put(c + 2, 19, z, stairs("ashbound:slate_shingle", "west"))
            put(c - 1, 20, z, stairs("ashbound:slate_shingle", "east"))
            put(c + 1, 20, z, stairs("ashbound:slate_shingle", "west"))
            put(c, 20, z, SLATE)
            put(c, 21, z, SLAB % "ashbound:slate_shingle")
    # the west gable's chimney from the hearth, smoking
    for x in (X0 - 1, X0):
        for z in (-111, -110):
            for y in range(EAVE - 2, 34):
                put(x, y, z, BODY if y < 32 else PL)
    put(X0 - 1, 34, -111, "campfire[facing=north,lit=true,signal_fire=false,waterlogged=false]")
    # turrets at the front corners
    for s in (-1, 1):
        turret(s * (X1 + 1) + 0.5, Z1 + 1.5, 8, 20, 2.3, 11)
    # ---------------------------------------------------------------- the belfry
    TOP = 35
    zc = (TZ0 + TZ1) // 2
    for x in range(TX0, TX1 + 1):
        for z in range(TZ0, TZ1 + 1):
            shell = x in (TX0, TX0 + 1, TX1 - 1, TX1) or z in (TZ0, TZ0 + 1, TZ1 - 1, TZ1)
            quoin = x in (TX0, TX1) and z in (TZ0, TZ1)
            for y in range(1, TOP + 1):
                if passage(x, y):
                    put(x, y, z, "air")
                elif shell:
                    st = wall_stone(y, quoin)
                    put(x, y, z, PL if y in (16, 26) else st)
                elif y <= 9 or y in (10, 26) and abs(x) <= 4:
                    put(x, y, z, BODY if y <= 9 else "spruce_planks")
                elif y == TOP:
                    put(x, y, z, PL)
                else:
                    put(x, y, z, "air")
    for z in range(TZ1, Z0 - 1, -1):             # the passage's vault ribs and its lanterns
        if (z - TZ1) % 4 == 2:
            for dx in range(-2, 3):
                y = 7 if abs(dx) == 2 else 8 if abs(dx) == 1 else 9
                put(dx, y, z, PL)
            put(0, 8, z, "chain[axis=y,waterlogged=false]")
            put(0, 7, z, "lantern[hanging=true,waterlogged=false]")
    for dx, y in ((-3, 1), (-3, 2), (-3, 3), (-3, 4), (-3, 5), (-3, 6), (-2, 7), (-1, 8), (0, 9), (1, 8), (2, 7),
                  (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6)):
        put(dx, y, TZ1, PL)                       # the archivolts front and back
        put(dx, y, Z0, PL)
    for s in (-1, 1):                             # arches off the passage into either wing
        for z in range(-116, -113):
            for y in range(1, 5):
                put(s * 3, y, z, "air")
        put(s * 3, 5, -116, stairs("stone_brick", "north", "top"))
        put(s * 3, 5, -114, stairs("stone_brick", "south", "top"))
    window("x", 0, TZ1, TZ1 - 1, 11, 14, "south")
    def opening(dx, y, g):
        """The passage's pointed arch grown g blocks all round."""
        w = 2 + g
        return abs(dx) < w and y <= 6 + w - abs(dx) or abs(dx) == w and y <= 6

    for d in (1, 2):                              # the portal: a recessed arch in two orders, pinnacles either side
        z = TZ1 + d
        for dx in range(-5, 6):
            for y in range(1, 12):
                if opening(dx, y, d):
                    continue
                ring = d == 2 and opening(dx, y, d + 1)
                put(dx, y, z, PL if ring or y == 11 else BODY if y > 2 else PLINTH)
        for dx in range(-5, 6):
            put(dx, 11, z + 1 if d == 2 else z, stairs("ashbound:pale_limestone", "north") if d == 2 else PL)
            if d == 2:
                put(dx, 12, z, "ashbound:pale_limestone_wall")
    for s in (-1, 1):
        for d in (1, 2, 3):
            for y in range(1, 12):
                put(s * 5, y, TZ1 + d, BODY if y > 2 else PLINTH)
        for y, st in ((12, PL), (13, "ashbound:pale_limestone_wall"), (14, "ashbound:pale_limestone_wall"), (15, "end_rod[facing=up]")):
            put(s * 5, y, TZ1 + 3, st)
    put(0, 10, TZ1 + 3, "red_wall_banner[facing=south]")
    sculpt("guild_crest", -2, TZ1 + 3, "south", y=12)     # the guild's arms over the arch (tools/blender/civic_sculpt.py)
    # the clock (tools/blender/civic_sculpt.py): its dial stood out from the face, the hands turned to the world's time
    sculpt("clock_face", -4, TZ1 + 1, "south", y=17)
    put(0, 21, TZ1 + 2, "ashbound:clock_hands[facing=south]")
    # clasping buttresses at the tower's front corners
    for s in (-1, 1):
        for x, z in ((s * 7, TZ1), (s * 7, TZ1 + 1), (s * 6, TZ1 + 1), (s * 8, TZ1), (s * 7, TZ1 - 1)):
            yt = 24 if (abs(x) == 8 or z == TZ1 + 1 and abs(x) == 7) else 30
            for y in range(1, yt):
                put(x, y, z, PLINTH if y <= 2 else BODY)
            put(x, yt, z, stairs("stone_brick", "north" if z > TZ1 else "west" if s > 0 else "east"))
    # the belfry stage: two pointed openings a face, the bells hung from a beam
    for y in range(28, 34):
        for a in (-4, -3, -2, 2, 3, 4):
            if y == 33 and abs(a) != 3:
                continue
            for d in (0, 1):
                put(a, y, TZ1 - d, "air")
                put(a, y, TZ0 + d, "air")
                put(TX0 + d, y, zc + a, "air")
                put(TX1 - d, y, zc + a, "air")
    for a in (-4, -3, -2, 2, 3, 4):
        put(a, 27, TZ1, "ashbound:pale_limestone_wall")
        put(a, 27, TZ0, "ashbound:pale_limestone_wall")
        put(TX0, 27, zc + a, "ashbound:pale_limestone_wall")
        put(TX1, 27, zc + a, "ashbound:pale_limestone_wall")
    for x in range(-4, 5):
        put(x, 32, zc, "dark_oak_log[axis=x]")
    for x in (-2, 0, 2):
        put(x, 31, zc, "bell[attachment=ceiling,facing=south,powered=false]")
    put(0, 30, zc - 2, LIGHT)
    # the corbelled gallery, its parapet, the corner turrets
    for x in range(TX0 - 1, TX1 + 2):
        for z in range(TZ0 - 1, TZ1 + 2):
            if TX0 <= x <= TX1 and TZ0 <= z <= TZ1:
                continue
            f = "south" if z < TZ0 else "north" if z > TZ1 else "east" if x < TX0 else "west"
            put(x, TOP - 1, z, stairs("ashbound:pale_limestone", f, "top"))
            put(x, TOP, z, PL)
            put(x, TOP + 1, z, "ashbound:pale_limestone_wall")
    for x, z in ((TX0, TZ0), (TX1, TZ0), (TX0, TZ1), (TX1, TZ1)):
        turret(x + 0.5, z + 0.5, TOP - 3, TOP + 6, 1.7, 9)
    # the octagonal lantern and the spire
    for dx in range(-6, 7):
        for dz in range(-6, 7):
            o = octo(dx, dz)
            x, z = dx, zc + dz
            for y in range(TOP + 1, TOP + 10):
                if 3.6 < o <= 4.6:
                    lanc = y in range(TOP + 3, TOP + 8) and (dx == 0 or dz == 0 or abs(dx) == abs(dz))
                    put(x, y, z, "ashbound:leaded_glass_pane" if lanc else PL if y in (TOP + 1, TOP + 9) else BODY)
                elif o <= 3.6:
                    put(x, y, z, "air" if y > TOP + 1 else PL)
            if 4.6 < o <= 5.6:
                put(x, TOP + 9, z, stairs("ashbound:pale_limestone", "north" if abs(dz) >= abs(dx) and dz > 0 else
                                          "south" if abs(dz) >= abs(dx) else "west" if dx > 0 else "east", "top"))
            if o <= 3.6:
                put(x, TOP + 2, z, LIGHT if (dx, dz) == (0, 0) else "air")
    H_SP = 32
    for k in range(H_SP):
        y = TOP + 10 + k
        rr = 5.4 * (1 - k / H_SP) ** 1.05
        for dx in range(-6, 7):
            for dz in range(-6, 7):
                o = octo(dx, dz)
                if o <= rr + 0.3 and (o > rr - 1.3 or k == 0):
                    band = k in (9, 19)
                    put(dx, y, zc + dz, "ashbound:gilded_tiles" if k == 9 else
                        "polished_blackstone_bricks" if band else "deepslate_tiles")
    for vx, vz, f in ((0, 1, "south"), (0, -1, "north"), (1, 0, "east"), (-1, 0, "west")):
        k = 4
        y = TOP + 10 + k
        rr = 5.4 * (1 - k / H_SP) ** 1.05
        n = round(rr) + 1
        for a in (-1, 0, 1):
            px, pz = vx * n + vz * a, zc + vz * n + vx * a
            put(px, y, pz, "ashbound:leaded_glass_pane" if a == 0 else PL)
            put(px, y + 1, pz, "ashbound:leaded_glass_pane" if a == 0 else PL)
            back = (px - vx, pz - vz)
            put(back[0], y, back[1], "air" if a == 0 else "deepslate_tiles")
        side = ("west", "east") if vz else ("north", "south")
        px, pz = vx * n, zc + vz * n
        put(px - abs(vz), y + 2, pz - abs(vx), stairs("deepslate_tile", side[1]))
        put(px + abs(vz), y + 2, pz + abs(vx), stairs("deepslate_tile", side[0]))
        put(px, y + 2, pz, "deepslate_tiles")
        put(px, y + 3, pz, SLAB % "deepslate_tile")
    put(0, TOP + 10 + H_SP, zc, "ashbound:gilded_tiles")
    put(0, TOP + 11 + H_SP, zc, "end_rod[facing=up]")
    hall_inside()
    S.marks["guild_belfry"] = (0, TOP + 1, zc - 6)


def chandelier(x, z, y_top, y):
    """Lanterns on a cross of chain, hung on a chain from whatever's over it (a tie beam, the roof)."""
    top = y + 1
    while top < y + 30 and S.get(x, top, z) in (None, "air"):
        top += 1
    for yy in range(y + 1, top):
        put(x, yy, z, "chain[axis=y,waterlogged=false]")
    put(x, y, z, "lantern[hanging=true,waterlogged=false]")
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        put(x + dx, y + 1, z + dz, "chain[axis=%s,waterlogged=false]" % ("x" if dx else "z"))
        put(x + dx, y, z + dz, "lantern[hanging=true,waterlogged=false]")
    put(x, y - 1, z, LIGHT)


def guild_lamp(x, z, y=9):
    """A guild chandelier (tools/blender/civic_sculpt.py) centred over x, z, hung on a chain from whatever's over it."""
    sculpt("guild_chandelier", x - 1, z - 1, "south", y=y)
    top = y + 2
    while top < y + 30 and S.get(x, top, z) in (None, "air"):
        top += 1
    for yy in range(y + 2, top):
        put(x, yy, z, "chain[axis=y,waterlogged=false]")


def hall_inside():
    """The guild inside, furnished with its own pieces (tools/blender/civic_sculpt.py): a lobby under the belfry with
    wide arches into both wings. West, the Hall of Quests: the gate board under the guild's arms, the clerks' counter
    waist high before it (the clerks spoken to across it), trestle tables and chairs, the hearth, arms by the walls.
    East, the Adventurers' Rest: kegs racked under the trophies, the bar and its stools, round tables. Oak parquet,
    panelled walls, a wheel of candles over every table and light hidden in the air so no corner's dark."""
    X0, Z0, X1, Z1 = HALL
    TX0, TZ0, TX1, TZ1 = TOWER

    def inside(x, z):
        return 4 <= abs(x) <= 22 and Z0 + 2 <= z <= Z1 - 2 and not (TX0 <= x <= TX1 and z >= TZ0)

    # ---- the lobby: the belfry's base hollowed, an arch each side into the wings, the passage running on behind
    LZ0, LZ1, LZC = TZ0 + 2, TZ1 - 2, (TZ0 + TZ1) // 2 + 1
    for x in range(TX0 + 2, TX1 - 1):
        for z in range(LZ0, LZ1 + 1):
            for y in range(1, 8):
                put(x, y, z, "air")
            put(x, 8, z, PL)
            edge = abs(x) == TX1 - 2 or z in (LZ0, LZ1)
            put(x, 0, z, "polished_andesite" if edge else PL if (x + z) % 2 else "smooth_stone")
            if abs(x) <= 1:
                put(x, 1, z, "red_carpet")
    for s in (-1, 1):
        for x in (s * (TX1 - 1), s * TX1):
            for z in range(LZC - 2, LZC + 3):
                k = abs(z - LZC)
                for y in range(1, 8):
                    if y <= 5 or y == 6 and k <= 1 or y == 7 and k == 0:
                        put(x, y, z, "air")
                    else:
                        put(x, y, z, PL)
                put(x, 0, z, "polished_andesite")
        f = "east" if s < 0 else "west"
        for z in (LZ0, LZ1):
            put(s * (TX1 - 2), 6, z, "red_wall_banner[facing=%s]" % f)
        for z in (LZC - 3, LZC + 3):
            put(s * (TX1 - 2), 4, z, "ashbound:wall_lantern[facing=%s]" % f)
    guild_lamp(0, LZC, 5)
    # roof trusses: a tie beam across each bay at the eaves, a king post to the ridge
    for bx in (-18, -12, 12, 18):
        for z in range(Z0 + 2, Z1 - 1):
            put(bx, 14, z, "dark_oak_log[axis=z]")
        for y in range(15, 26):
            put(bx, y, -111, "dark_oak_log[axis=y]")
        for k in range(1, 11):
            put(bx, 14 + k, Z1 - 1 - k, "dark_oak_log[axis=z]")
            put(bx, 14 + k, Z0 + 1 + k, "dark_oak_log[axis=z]")
    # the floors: oak parquet in squares; the walls panelled in dark oak to a rail
    for x in range(-22, 23):
        for z in range(Z0 + 2, Z1 - 1):
            if inside(x, z):
                put(x, 0, z, "dark_oak_planks" if (x // 2 + z // 2) % 2 else "spruce_planks")
    walls = ([(x, Z0 + 1) for x in range(-22, 23) if abs(x) >= 4] + [(x, Z1 - 1) for x in range(-22, 23) if abs(x) >= 7]
             + [(s * 23, z) for s in (-1, 1) for z in range(Z0 + 2, Z1 - 1)])
    for x, z in walls:
        for y in (1, 2, 3):
            st = S.get(x, y, z)
            if not st or st == "air" or "glass" in st or "pane" in st:
                continue
            post = (x + z) % 4 == 0
            put(x, y, z, "stripped_dark_oak_log[axis=y]" if post else
                ("stripped_dark_oak_log[axis=%s]" % ("x" if abs(x) != 23 else "z")) if y == 3 else "dark_oak_planks")
    # ---- the Hall of Quests (west wing)
    zb = Z0 + 2                                       # just inside the back wall
    sculpt("guild_board", -21, zb, "south", y=2)
    sculpt("guild_crest", -19, zb, "south", y=9)
    for x, col in ((-21, "red"), (-12, "yellow")):
        put(x, 10, zb, "%s_wall_banner[facing=south]" % col)
    for x in (-10, -8, -6):
        sculpt("scroll_shelf", x, zb, "south")
    for x in (-21, -15):                              # the counter, waist high, the clerks behind it
        sculpt("guild_counter", x, zb + 3, "south")
    for x in (-18, -12):
        S.marks["guild_clerk:%d" % x] = (x, 1, zb + 2)
    S.marks["gate_board"] = (-15, 1, zb + 4)
    for x in range(-21, -8):                          # a rug before the counter, a runner from the door to it
        for z in (zb + 4, zb + 5):
            put(x, 1, z, "red_carpet")
    for z in range(zb + 6, Z1 - 1):
        put(-15, 1, z, "red_carpet")
    # the hearth in the west gable
    for z in range(-113, -108):
        for y in range(1, 14):
            if not (z in (-112, -111, -110) and y <= 3):
                put(X0 + 2, y, z, BODY if y != 4 else PL)
        put(X0 + 3, 4, z, stairs("ashbound:pale_limestone", "west", "top"))
    for z in (-112, -111, -110):
        put(X0 + 1, 1, z, "bricks")
        put(X0 + 2, 0, z, "smooth_stone")
    put(X0 + 2, 1, -111, "campfire[facing=east,lit=true,signal_fire=false,waterlogged=false]")
    put(X0 + 2, 1, -112, "iron_bars")
    put(X0 + 2, 1, -110, "iron_bars")
    for z in (-113, -109):
        put(X0 + 3, 5, z, "candle[candles=3,lit=true,waterlogged=false]")
    sculpt("weapon_rack", -22, -107, "east")
    sculpt("armour_stand", -22, -104, "east")
    # trestle tables either side of the aisle from the door, chairs along them
    for tx in (-20, -13):
        for tz in (-112, -107):
            sculpt("trestle_table", tx, tz, "south")
            for x in range(tx, tx + 3):
                sculpt("guild_chair", x, tz - 1, "south")
                sculpt("guild_chair", x, tz + 2, "north")
            guild_lamp(tx + 1, tz)
            S.marks["adventurers:%d:%d" % (tx, tz)] = (tx, 1, tz + 2)
    guild_lamp(-15, zb + 2)
    for x in (-18, -12):
        put(x, 5, Z1 - 2, "ashbound:wall_lantern[facing=north]")
    for z in (-115, -106):
        put(X0 + 2, 5, z, "ashbound:wall_lantern[facing=east]")
    # ---- the Adventurers' Rest (east wing): kegs racked under the trophies, the bar before them
    for k, x in enumerate((5, 9, 13, 17)):
        sculpt("keg_rack", x, Z0 + 2, "south")
        sculpt("trophy_skull", x + 1, Z0 + 2, "south", y=4)
        put(x + 3, 6, Z0 + 2, "%s_wall_banner[facing=south]" % ("black" if k % 2 else "red"))
    zc = Z0 + 4                                       # the bar
    for x in (7, 11, 15):
        sculpt("tavern_bar", x, zc, "south")
    for x in range(7, 19, 2):
        sculpt("bar_stool", x, zc + 1, "north")
    S.marks["guild_barkeep"] = (13, 1, zc - 1)
    for tx in (9, 15):                                # round tables, a pair of chairs either side
        for tz in (-112, -107):
            sculpt("round_table", tx, tz, "south")
            for x in (tx, tx + 1):
                sculpt("guild_chair", x, tz - 1, "south")
                sculpt("guild_chair", x, tz + 2, "north")
            guild_lamp(tx + 1, tz + 1)
    guild_lamp(13, zc)
    for x, kind in ((9, "weapon_rack"), (12, "armour_stand"), (18, "armour_stand"), (20, "weapon_rack")):
        sculpt(kind, x, Z1 - 2, "north")              # arms along the front wall
    skull(X1 - 3, 7, -110)
    for x in (12, 18):
        put(x, 5, Z1 - 2, "ashbound:wall_lantern[facing=north]")
    for z in (-116, -103):
        put(X1 - 2, 5, z, "ashbound:wall_lantern[facing=west]")
    S.marks["guild_master"] = (13, 1, -109)
    # light in the air of both wings, so the far corners aren't dark
    for x in range(-21, 22, 4):
        for z in range(Z0 + 3, Z1 - 1, 4):
            if inside(x, z) and S.get(x, 6, z) in (None, "air"):
                put(x, 6, z, LIGHT)


def skull(cx, cy, cz):
    """The trophy hall's prize, mounted on the east wall: a great bull skull in bone, deep black sockets, its dark
    horns sweeping out and up, on a dark oak shield."""
    cells = {}
    for dx in range(-4, 1):
        for dy in range(-6, 5):
            for dz in range(-3, 4):
                if 1 <= dy <= 3:                           # the brow, wide
                    hw, depth = 3.0 - 0.6 * (dy == 3), 2.2
                elif -6 <= dy < 1:                         # the face narrowing into the muzzle, which juts out
                    hw, depth = 1.0 + (dy + 6) * 0.2, 1.4 + (1 - dy) * 0.35
                else:
                    continue
                if abs(dz) <= hw and -dx <= depth:
                    cells[(dx, dy, dz)] = "bone_block[axis=y]"
    for dz in (-2, 2):                                     # the sockets, two deep
        for dx in range(-4, 0):
            if (dx, 1, dz) in cells:
                cells[(dx, 1, dz)] = "coal_block"
    for dz in (-1, 1):
        for dx in range(-5, 0):
            if (dx, -5, dz) in cells and (dx - 1, -5, dz) not in cells:
                cells[(dx, -5, dz)] = "coal_block"
    for s_ in (-1, 1):                                     # the horns
        for t in range(30):
            a = t / 29
            hz = s_ * (2.6 + 4.2 * math.sin(a * 1.5))
            hy = 3.0 + 0.6 * a + 4.0 * a ** 3
            hx = -1.0 - 1.6 * a ** 2
            rad = 1.1 * (1 - a) + 0.4
            for dx in range(-4, 1):
                for dy in range(1, 9):
                    for dz in range(-8, 9):
                        if math.dist((dx, dy, dz), (hx, hy, hz)) <= rad:
                            cells[(dx, dy, dz)] = "dripstone_block" if a < 0.8 else "polished_basalt[axis=y]"
    for (dx, dy, dz), st in cells.items():
        put(cx + dx, cy + dy, cz + dz, st)
    for dy in range(-5, 5):                                # the shield it's mounted on
        for dz in range(-4, 5):
            e = (dz / 4.4) ** 2 + ((dy + 0.5) / 5.2) ** 2
            if e <= 1:
                put(cx + 1, cy + dy, cz + dz, "dark_oak_planks" if e < 0.7 else "stripped_dark_oak_log[axis=y]")


# ---------------------------------------------------------------- the square before it

def gate_board(cx, z, face="south"):
    """A freestanding notice board under its own little roof, the bounties pinned on both sides."""
    for x in range(cx - 3, cx + 4):
        post = abs(x - cx) == 3
        for y in range(1, 6):
            if post:
                put(x, y, z, "stripped_dark_oak_log[axis=y]")
            elif 2 <= y <= 4:
                put(x, y, z, "dark_oak_planks")
                for sz, f in ((z + 1, "south"), (z - 1, "north")):
                    if noise(x * 5 + sz, y * 5, 2, 421) > 0.35:
                        put(x, y, sz, "birch_trapdoor[facing=%s,half=bottom,open=true,powered=false,waterlogged=false]" % f)
        put(x, 6, z + 1, stairs("dark_oak", "north"))
        put(x, 6, z - 1, stairs("dark_oak", "south"))
        put(x, 6, z, "dark_oak_planks")
        put(x, 7, z, SLAB % "dark_oak")
        put(x, 5, z, "dark_oak_planks" if not post else "stripped_dark_oak_log[axis=y]")
    put(cx, 5, z + 1, "lantern[hanging=true,waterlogged=false]")
    S.marks["bounty_board:%d" % cx] = (cx, 1, z + 2)


def banner_pole(x, z, col):
    put(x, 1, z, PL)
    for y in range(2, 8):
        put(x, y, z, "dark_oak_fence")
    put(x, 8, z, "%s_banner[rotation=0]" % col)


def guild_square():
    for s in (-1, 1):
        gate_board(s * 15, -94)
        banner_pole(s * 9, -98, "red")
        banner_pole(s * 21, -98, "blue")
        planter(s * 19, -88)
        seat(s * 15, -87, 0, -87)                       # a pair under each planter's tree, looking across the square
        seat(s * 15, -89, 0, -89)
        lamp(s * 15, -84, "z")
        lamp(s * 12, -97, "z")


# ---------------------------------------------------------------- the training yard

def dummy(x, z, facing="south"):
    put(x, 1, z, "spruce_fence")
    put(x, 2, z, "hay_block[axis=y]")
    put(x, 3, z, "brown_wool")
    for dx in (-1, 1):
        put(x + dx, 2, z, "spruce_fence")


def training_yard():
    """Where the guild's recruits learn: trodden earth inside a fence on stone footings, straw dummies, a sparring
    ring, archery butts down the east side, an open-sided armoury along the back."""
    x0, z0, x1, z1 = YARD_T
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            if GROUND(x, z) != 0 or wet(x, z):
                continue
            edge = x in (x0, x1) or z in (z0, z1)
            e = noise(x, z, 6, 441)
            put(x, 0, z, PLINTH if edge else "packed_mud" if e > 0.68 else "gravel" if e < 0.16 else
                "dirt_path" if noise(x, z, 3, 442) > 0.8 else "coarse_dirt")
            YARD.add((x, z))
            if edge:
                gate = z == z1 and abs(x - (x0 + x1) // 2) <= 1
                if gate:
                    continue
                post = (x - x0) % 4 == 0 and (z - z0) % 4 == 0 or x in (x0, x1) and z in (z0, z1)
                put(x, 1, z, "stripped_spruce_log[axis=y]" if post else "spruce_fence")
                if post:
                    put(x, 2, z, "stripped_spruce_log[axis=y]")
    gx = (x0 + x1) // 2
    for s in (-2, 2):
        for y in (1, 2, 3, 4):
            put(gx + s, y, z1, "stripped_spruce_log[axis=y]")
        put(gx + s, 5, z1, "lantern[hanging=false,waterlogged=false]")
        banner_pole(gx + s * 2, z1 + 1, "red")
    for x in range(gx - 1, gx + 2):
        put(x, 4, z1, "stripped_spruce_log[axis=x]")
    # dummies in rows in the west part
    for x in range(x0 + 4, x0 + 17, 4):
        for z in (z1 - 6, z1 - 13):
            dummy(x, z)
    S.marks["trainer"] = (x0 + 10, 1, z1 - 3)
    # the sparring ring
    rx, rz = x0 + 24, (z0 + z1) // 2 + 1
    for dx in range(-7, 8):
        for dz in range(-7, 8):
            r = math.hypot(dx, dz)
            if r <= 6.5:
                put(rx + dx, 0, rz + dz, FLAG if r < 5.5 else "ashbound:statue_stone")
            if 5.5 <= r <= 6.5 and (int(math.degrees(math.atan2(dz, dx))) + 360) % 45 > 8:
                put(rx + dx, 1, rz + dz, SLAB % "stone_brick")
    for k in range(8):
        a = k * math.pi / 4 + 0.39
        x, z = round(rx + 8.2 * math.cos(a)), round(rz + 8.2 * math.sin(a))
        dx, dz = rx - x, rz - z
        bench(x, z, ("east" if dx > 0 else "west") if abs(dx) > abs(dz) else ("south" if dz > 0 else "north"))
    S.marks["sparring:1"] = (rx - 2, 1, rz)
    S.marks["sparring:2"] = (rx + 2, 1, rz)
    # the archery range: a line to shoot from, butts with their targets at the far end
    for x in range(x1 - 9, x1 - 1):
        put(x, 1, z1 - 4, "spruce_fence" if x % 3 else "hay_block[axis=x]")
        if x % 3 == 1:
            put(x, 1, z0 + 5, "hay_block[axis=y]")
            put(x, 2, z0 + 5, "target[power=0]")
            put(x, 1, z0 + 4, "hay_block[axis=x]")
            put(x, 2, z0 + 4, "hay_block[axis=x]")
            put(x, 3, z0 + 4, "hay_block[axis=x]")
    S.marks["archer"] = (x1 - 5, 1, z1 - 3)
    # the armoury along the back: posts, a lean-to roof, racks and the smith's tools under it
    for x in range(x0 + 1, x0 + 20):
        for z in (z0 + 1, z0 + 2, z0 + 3):
            put(x, 0, z, "spruce_planks")
        for y in range(1, 6):
            put(x, y, z0, GS if y <= 1 else "ashbound:plaster_timber" if x % 4 else "stripped_spruce_log[axis=y]")
        if (x - x0) % 4 == 1:
            for y in range(1, 3):
                put(x, y, z0 + 3, "stripped_spruce_log[axis=y]")
        for j in range(4):
            put(x, 6 - j, z0 + j, stairs("ashbound:wood_shingle", "north"))
            if 0 < j < 3:
                put(x, 5 - j, z0 + j, "ashbound:wood_shingles")
        k = (x - x0) % 6
        item = ("anvil[facing=east]", "barrel[facing=up,open=false]", "grindstone[face=floor,facing=north]",
                "lightning_rod[facing=up,powered=false,waterlogged=false]", "smithing_table", "chest[facing=south,type=single,waterlogged=false]")[k]
        put(x, 1, z0 + 1, item)
        if k == 3:
            put(x, 2, z0 + 1, "lightning_rod[facing=up,powered=false,waterlogged=false]")
    S.marks["armourer"] = (x0 + 10, 1, z0 + 2)


# ---------------------------------------------------------------- the quartermaster and the smithy

def quartermaster(front):
    """Brann Holt's shop on the Terrace Walk east of the hall, and an open smithy beside it."""
    x0 = QM
    build_house(H.shop, (x0, front - 9), "south", {"trade": "general", "roof": "ashbound:slate_shingle", "eaves": False})
    S.marks["quartermaster"] = (x0 + 3, 1, front - 4)
    sx = x0 + 8
    for x in range(sx, sx + 9):
        for z in range(front - 8, front + 1):
            put(x, 0, z, pick(("ashbound:greystone", 3), ("packed_mud", 1), ("gravel", 1)))
            for y in range(1, 6):
                if S.get(x, y, z) is None:
                    put(x, y, z, "air")
    for x, z in ((sx, front), (sx + 8, front), (sx, front - 8), (sx + 8, front - 8), (sx + 4, front), (sx + 4, front - 8)):
        for y in range(1, 5):
            put(x, y, z, "stripped_spruce_log[axis=y]")
    for k in range(5):
        for x in range(sx - 1, sx + 10):
            put(x, 5 + k, front + 1 - k, stairs("ashbound:wood_shingle", "north"))
            put(x, 5 + k, front - 9 + k, stairs("ashbound:wood_shingle", "south"))
            if k:
                put(x, 4 + k, front + 1 - k, "ashbound:wood_shingles")
                put(x, 4 + k, front - 9 + k, "ashbound:wood_shingles")
    for x in range(sx - 1, sx + 10):
        put(x, 9, front - 4, "ashbound:wood_shingles")
        put(x, 10, front - 4, SLAB % "ashbound:wood_shingle")
    # the forge: a stone hearth with its hood and chimney, the anvil, the quench, the grindstone, the racks
    for x in range(sx + 5, sx + 8):
        for z in range(front - 8, front - 5):
            for y in range(1, 3):
                put(x, y, z, "ashbound:greystone" if (x, z) != (sx + 6, front - 7) or y == 1 else "air")
        for y in range(3, 12):
            if y > 4 or (x != sx + 6):
                put(x, y, front - 8, "ashbound:greystone")
    put(sx + 6, 2, front - 7, "lava_cauldron")
    put(sx + 6, 2, front - 6, "blast_furnace[facing=south,lit=true]")
    put(sx + 6, 3, front - 7, "air")
    for x in range(sx + 5, sx + 8):
        put(x, 3, front - 6, stairs("ashbound:greystone", "north", "top"))
        put(x, 4, front - 7, "ashbound:greystone")
    put(sx + 6, 1, front - 4, "anvil[facing=east]")
    put(sx + 3, 1, front - 4, "water_cauldron[level=3]")
    put(sx + 2, 1, front - 7, "grindstone[face=floor,facing=east]")
    put(sx + 1, 1, front - 7, "smithing_table")
    put(sx + 1, 1, front - 6, "barrel[facing=up,open=false]")
    for z in range(front - 6, front - 1):
        put(sx + 8, 1, z, "lightning_rod[facing=up,powered=false,waterlogged=false]" if z % 2 else "barrel[facing=up,open=false]")
    for y in range(5, 9):
        put(sx + 4, y, front - 4, "chain[axis=y,waterlogged=false]")
    put(sx + 4, 4, front - 4, "lantern[hanging=true,waterlogged=false]")
    S.marks["smith"] = (sx + 5, 1, front - 4)


def bridge_over(road):
    """Where the walk crosses the river: a stone deck on the banks, parapets, a lantern each end."""
    cells = [(x, z) for (x, z) in road.cells if wet(x, z)]
    if not cells:
        return
    xs = [x for x, _ in cells]
    for x in range(min(xs) - 2, max(xs) + 3):
        zs = [z for (cx, z), (r, u) in ROAD.items() if cx == x and r is road]
        if not zs:
            continue
        for z in range(min(zs), max(zs) + 1):
            put(x, 0, z, "stone_bricks" if noise(x, z, 3, 431) > 0.3 else "polished_andesite")
        for z in (min(zs) - 1, max(zs) + 1):
            put(x, 0, z, "stone_bricks")
            put(x, 1, z, "stone_brick_wall")
    for x in (min(xs) - 2, max(xs) + 2):
        zs = [z for (cx, z), (r, u) in ROAD.items() if cx == x and r is road]
        if zs:
            for z in (min(zs) - 1, max(zs) + 1):
                put(x, 1, z, "stone_bricks")
                put(x, 2, z, "lantern[hanging=false,waterlogged=false]")


def walk_z(x):
    """The Terrace Walk's line: along the terrace a few blocks in from the top of the bank."""
    z = round(L.z_terrace(x)) - 16
    while GROUND(x, z) < 0 and z > -170:
        z -= 1
    return z - 3


def terrace():
    """Step 4: the guild terrace, 20 over the lower city."""
    grand_stair(0, -64, 7)
    FRONT.clear()
    ALLEY.clear()
    FENCES.clear()
    with tier(L.TERRACE):
        R = {}
        R["square"] = add_road("the Guild Square", "square", [(-13, -91), (13, -91)], [17, 17])
        R["walk_w"] = add_road("the Terrace Walk", "walk", [(-20, -89)] + [(x, walk_z(x)) for x in (-40, -70, -100, -125, -150)],
                               [7] * 6)
        R["walk_e"] = add_road("the Terrace Walk east", "walk", [(20, -89)] + [(x, walk_z(x)) for x in (40, 70, 100, 125, 150)],
                               [7] * 6)
        R["back"] = add_road("Guild Lane", "lane", [(0, -122), (0, -126), (-14, -127), (-30, -126), (-30, -110), (-30, -91)],
                             [5] * 6)
        guild_hall()
        guild_square()
        training_yard()
        qfront = min(z for (x, z) in R["walk_e"].cells if x in range(QM, QM + 17)) - 1
        quartermaster(qfront)
        bridge_over(R["walk_e"])
        n = 0
        for r in ("walk_w", "walk_e"):
            n += frontage(R[r], "n", TERRACE_MIX, alley=0.1, yards=(6, 12))
        print("  the terrace: %d houses" % n)
        lip_parapet()
        shoulders()
        fill_gaps(-200, 200, -160, -80)
        pave_roads()
        connect_fences()


# ---------------------------------------------------------------- the bank's terraces

def bank_walls():
    """The terrace bank's retaining walls (its steps from capital_land.BANK_STEPS): dressed stone faces with a plinth
    course and a pale coping, a low parapet, buttresses on a rhythm, ivy down the faces, a flight of steps along each
    face now and then, and the terraces between them planted."""
    N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
    face, at = {}, {}
    for x in range(-215, 216):
        zt = int(L.z_terrace(x))
        for z in range(zt + 3, zt - 25, -1):
            g = GROUND(x, z)
            if L.edist(x, z) >= 2 or not 0 < g <= L.TERRACE or wet(x, z) or (x, z) in CLAIM:
                continue                              # (a set piece cut into the bank keeps its own face)
            lows = [(GROUND(x + dx, z + dz), (dx, dz)) for dx, dz in N4 if not wet(x + dx, z + dz)]
            if not lows:
                continue
            low, out = min(lows)
            if g - low >= 2 and not (L.bank_smooth(x, z) and all(L.bank_smooth(x + dx, z + dz) for dx, dz in N4)):
                face[(x, z)] = (max(low, 0), g, out)
                if out == (0, 1):
                    at.setdefault((x, g), z)
    # the flights: one along a face every 40-odd blocks, climbing east, two wide on the lower terrace
    flight, nf = set(), 0
    for (x, g), z in sorted(at.items()):
        low = face[(x, z)][0]
        h = g - low
        if (x + 13 * g) % 43 or any((x + k, g) not in at for k in range(h + 2)):
            continue
        cells = [(x + k, at[(x + k, g)]) for k in range(h)]
        head = [(x + k, at[(x + k, g)]) for k in (h, h + 1)]
        Z = max(c[1] for c in cells + head)          # one straight line out from the face's southernmost cell
        if any(abs(c[0]) <= L.STAIR_HW + 3 or GROUND(c[0], Z + 3) != low or built(c[0], c[1] + 1, low + 1, low + 3)
               for c in cells + head):
            continue
        for k, (fx, fz) in enumerate(cells):
            y = low + k + 1
            for z in range(fz + 1, Z + 3):
                for yy in range(low + 1, y):
                    put(fx, yy, z, BODY)
                put(fx, y, z, stairs("stone_brick", "east"))
                for yy in range(y + 1, y + 4):
                    put(fx, yy, z, "air")
                flight.add((fx, z))
            for yy in range(low + 1, y + 1):
                put(fx, yy, Z + 3, BODY if yy < y else PL)
            if k >= 2:
                put(fx, y + 1, Z + 3, "stone_brick_wall")
            flight.add((fx, Z + 3))
        # a landing at the head, flush with the terrace, railed on its far side, so the last step doesn't run off
        for k, (lx, lz) in enumerate(head):
            for z in range(lz + 1, Z + 4):
                for yy in range(low + 1, g):
                    put(lx, yy, z, BODY)
                put(lx, g, z, PL)
                for yy in range(g + 1, g + 4):
                    if z < Z + 3 or k:
                        put(lx, yy, z, "air")
                if k or z == Z + 3:
                    put(lx, g + 1, z, "stone_brick_wall")
                flight.add((lx, z))
        tx, tz = cells[-1]
        nf += 1
        for k in (h - 1, h):                          # the landing: the parapet left open at the flight's head
            flight.add((x + k, at.get((x + k, g), tz)))
    for (x, z), (low, g, out) in face.items():
        for y in range(low + 1, g + 1):
            if y == g:
                st = PL
            elif y == low + 1:
                st = PLINTH
            else:
                st = pick((BODY, 40), ("cracked_stone_bricks", 1), ("mossy_stone_bricks", 2 if y < low + 3 else 0))
            put(x, y, z, st)
        put(x, low, z, PLINTH)
        if (x, z) in flight:
            continue
        lip = g == L.TERRACE and any((x, g + 1, z - d) in S.B for d in (0, 1, 2))
        if not lip:
            if out == (0, 1) and x % 9 == 0:
                put(x, g + 1, z, PL)
                if x % 18 == 0:
                    put(x, g + 2, z, "lantern[hanging=false,waterlogged=false]")
            else:
                put(x, g + 1, z, "ashbound:pale_limestone_wall")
        ox, oz = x + out[0], z + out[1]
        if (ox, oz) in flight or (ox, oz) in face:
            continue
        if out == (0, 1) and x % 9 == 0 and g - low >= 4:
            # a buttress: a pier against the face, its top weathered back in a stair
            for y in range(low + 1, g - 1):
                put(ox, y, oz, BODY if y > low + 1 else PLINTH)
            put(ox, g - 1, oz, stairs("stone_brick", "north"))
        elif noise(x, z, 5, 461) > 0.58:
            side = {(0, 1): "north", (0, -1): "south", (1, 0): "west", (-1, 0): "east"}[out]
            for y in range(g, max(low, g - 1 - int(noise(x, z, 2, 462) * (g - low))), -1):
                if (ox, y, oz) not in S.B:
                    put(ox, y, oz, "vine[%s=true]" % side)
    # the terraces between the faces: grass, flowers, box shrubs and a cherry or a birch where there's room
    flowers = (("short_grass", 10), ("poppy", 1), ("cornflower", 1), ("oxeye_daisy", 1), ("allium", 1), ("azure_bluet", 1),
               ("lily_of_the_valley", 1))
    for x in range(-212, 213):
        zt = int(L.z_terrace(x))
        for z in range(zt + 1, zt - 21, -1):
            g = GROUND(x, z)
            if g not in (7, 14) or L.edist(x, z) >= 2 or (x, z) in face or (x, z) in flight or wet(x, z) \
                    or built(x, z, g + 1, g + 2) or L.bank_smooth(x, z):
                continue
            n = noise(x, z, 4, 463)
            if n > 0.8 and all(GROUND(x + dx, z + dz) == g and (x + dx, z + dz) not in face
                               for dx in (-2, 0, 2) for dz in (-2, 0, 2)) and (x * 5 + z * 3) % 7 == 0:
                small_tree(x, g + 1, z, "cherry" if noise(x, z, 30, 464) > 0.5 else "birch", h=4)
            elif n < 0.22:
                put(x, g + 1, z, "azalea_leaves[distance=1,persistent=true,waterlogged=false]"
                    if noise(x, z, 3, 465) > 0.5 else "flowering_azalea_leaves[distance=1,persistent=true,waterlogged=false]")
            elif noise(x, z, 2, 466) > 0.55:
                put(x, g + 1, z, pick(*flowers))
    print("  the bank: %d face columns, %d flights" % (len(face), nf))


# ================================================================ the Forge and Hearth wards

HEARTH = (-118, 2)                    # the Hearth Square's well
HEARTH_R = 11
BATH = (-132, -30, -112, -16)         # the bathhouse on the square's north side: x0, z at its back, x1, z at its front
SHRINE = (-129, 15)                   # the wayside shrine on the square's south-west corner
FORGE_MIX = (("smithy", 3), ("cooperage", 1), ("house", 3), ("townhouse", 2))
HEARTH_MIX = (("house", 4), ("cottage", 3), ("townhouse", 2))


def workshop(S_, x0, z0, face, trade="smith", **kw):
    """A craftsman's shop open on the street, 8 wide and 9 deep: stone side and back walls, the front open between
    oak posts under a timbered gable, the trade's hearth or bench at the back. trade: smith (the hearth with its hood
    and chimney, the anvil, the quench, a grindstone) or cooper (staves, hoops and casks, the firing pit)."""
    w, d = 8, 9
    F = H.Frame(S_, x0, z0, w, d, face)
    st = H.Style(S_, **kw)
    g = d - 1
    for lx in range(w):
        for lz in range(d):
            F.put(lx, 0, lz, FLAG if lz < g else "stone_bricks")
            wall = lx in (0, w - 1) or lz == 0
            for y in range(1, 5):
                F.put(lx, y, lz, (PLINTH if y == 1 else BODY if y < 4 else "stripped_spruce_log[axis=z]"
                                  if lx in (0, w - 1) else "stripped_spruce_log[axis=x]") if wall else "air")
    for lx in (0, w - 1):
        for y in range(1, 4):
            F.put(lx, y, g, "stripped_spruce_log[axis=y]")
    for lx in range(1, w - 1):
        F.put(lx, 4, g, "stripped_spruce_log[axis=x]")
    top = H.gable_roof(F, st, 4, g)
    F.put(4, top - 2, 4, "chain[axis=y,waterlogged=false]")
    F.put(4, top - 3, 4, H.HANG)
    if trade == "smith":
        for lx in range(3, 6):
            for lz in range(1, 3):
                for y in (1, 2):
                    F.put(lx, y, lz, "stone_bricks" if (lx, lz) != (4, 1) or y == 1 else "air")
            F.put(lx, 3, 2, stairs("stone_brick", "north", "top"))
            F.put(lx, 4, 1, "bricks")
        F.put(4, 2, 1, "lava_cauldron")
        F.put(4, 1, 2, "blast_furnace[facing=south,lit=true]")
        H.chimney(F, 4, 0, 5, top + 2)
        F.put(3, 1, 5, "anvil[facing=east]")
        F.put(5, 1, 5, "water_cauldron[level=3]")
        F.put(6, 1, 2, "grindstone[face=floor,facing=east]")
        F.put(1, 1, 2, "smithing_table")
        F.put(1, 1, 3, "barrel[facing=up,open=false]")
        F.put(1, 1, 4, "chest[facing=east,type=single,waterlogged=false]")
        for lz in (5, 6):
            F.put(6, 1, lz, "barrel[facing=up,open=false]")
            F.put(6, 2, lz, "iron_bars[east=false,north=true,south=true,waterlogged=false,west=false]")
        S_.marks["smith:%d:%d" % (x0, z0)] = F.world(4, 1, 4)
    else:
        for lx, lz, n in ((1, 1, 3), (2, 1, 2), (1, 2, 2), (6, 1, 3), (6, 2, 1), (5, 1, 2)):
            for y in range(1, n + 1):
                F.put(lx, y, lz, "barrel[facing=%s,open=false]" % ("up" if y % 2 else "north"))
        for lx in range(3, 5):
            F.put(lx, 1, 1, "stripped_spruce_log[axis=x]")
            F.put(lx, 2, 1, "stripped_spruce_log[axis=x]")
            F.put(lx, 3, 1, "spruce_slab[type=bottom,waterlogged=false]")
        F.put(4, 1, 4, "campfire[facing=south,lit=true,signal_fire=false,waterlogged=false]")
        F.put(3, 1, 4, "barrel[facing=east,open=false]")
        F.put(2, 1, 5, "crafting_table")
        F.put(5, 1, 5, "spruce_slab[type=bottom,waterlogged=false]")
        F.put(1, 1, 6, "chest[facing=east,type=single,waterlogged=false]")
        H.chimney(F, 4, 0, 5, top + 1)
        S_.marks["cooper:%d:%d" % (x0, z0)] = F.world(3, 1, 5)
    return F


H.KINDS["smithy"] = (lambda S_, x0, z0, face, **kw: workshop(S_, x0, z0, face, "smith", **kw), 8, 9)
H.KINDS["cooperage"] = (lambda S_, x0, z0, face, **kw: workshop(S_, x0, z0, face, "cooper", **kw), 8, 9)


def hearth_stone(x, z, u):
    """The Hearth Square: flagstone in rings round the well, a pale band every few, setts at the rim."""
    if u > 0.88:
        return setts(x, z, 1)
    r = math.hypot(x - HEARTH[0], z - HEARTH[1])
    if r < 3.5:
        return LB
    if int(r) in (5, 9):
        return PL
    return "ashbound:statue_stone" if noise(x, z, 6, 471) > 0.72 else FLAG


def road_band(road, x0, x1, north=True):
    """The street's edge over x0..x1: its northmost (or southmost) cell's z in each column."""
    zs = [z for (x, z) in road.cells if x0 <= x <= x1]
    return min(zs) if north else max(zs)


def free_box(x0, z0, x1, z1):
    bad = sum(1 for x in range(x0, x1 + 1) for z in range(z0, z1 + 1)
              if (x, z) in ROAD or GROUND(x, z) != 0 or wet(x, z) or built(x, z, 1, 3) or not in_town(x, z))
    return bad


def hearth_square():
    """The ward's square: the well under its roof in the middle, benches and planters round it, a few stalls, lamps."""
    cx, cz = HEARTH
    well(cx, cz)
    for dx, dz, f in ((3, 0, "west"), (-3, 0, "east"), (0, 3, "north"), (0, -3, "south")):
        bench(cx + dx, cz + dz, f)
    for dx, dz in ((7, 6), (-7, 6), (7, -6), (-7, -6)):
        planter(cx + dx, cz + dz, tree=(dx > 0) == (dz > 0))
    for dx, dz, axis in ((10, 0, "z"), (-10, 0, "z"), (0, 10, "x")):
        lamp(cx + dx, cz + dz, axis)
    stall(cx - 4, cz + 8, "north", "baker")
    stall(cx + 4, cz + 8, "north", "general")
    S.marks["hearth_well"] = (cx + 2, 1, cz + 1)


def bathhouse():
    """The bathhouse on the square: a stone hall, its door south under a pale arch. Inside, the warm pool sunk in pale
    stone and blue tile, three bronze lions pouring into it from the north wall, a cold plunge at the west end, the
    copper boiler in the north-east corner piping heat to the water, oak tubs and towel benches by the door, steam
    braziers and potted ferns, pale piers holding the roof over the water."""
    X0, Z0, X1, Z1 = BATH
    cx = (X0 + X1) // 2
    ground_works(X0, Z0, X1, Z1, 16, margin=1)
    gothic_hall(X0, Z0, X1, Z1, 11, [X0 + 4, cx, X1 - 4], deep=1)
    portal("x", cx, Z1, Z1 - 1, w=1, h=4)
    for x in (cx - 1, cx, cx + 1):
        put(x, 0, Z1 + 1, FLAG)
    ix0, iz0, ix1, iz1 = X0 + 2, Z0 + 2, X1 - 2, Z1 - 2
    for x in range(ix0, ix1 + 1):                        # floor: pale flags in a blue-tiled border
        for z in range(iz0, iz1 + 1):
            put(x, 0, z, "light_blue_terracotta" if x in (ix0, ix1) or z in (iz0, iz1) else PL if (x + z) % 2 else FLAG)
    # the warm pool, against the north wall under the lions: water a step down, two deep, tiled
    px0, pz0, px1, pz1 = ix0 + 4, iz0, ix1 - 4, iz0 + 6
    for x in range(px0 - 1, px1 + 2):
        for z in range(pz0, pz1 + 2):
            rim = x in (px0 - 1, px1 + 1) or z == pz1 + 1
            for y in (1, 2, 3):
                put(x, y, z, "air")
            if rim:
                put(x, 0, z, "ashbound:carved_limestone" if x in (px0 - 1, px1 + 1) and z == pz1 + 1 else PL)
                for y in (-1, -2, -3):
                    put(x, y, z, "cyan_terracotta")
            else:
                put(x, 0, z, "air")
                put(x, -1, z, WATER)
                put(x, -2, z, WATER)
                put(x, -3, z, "soul_sand" if (x - px0) % 4 == 1 and z == pz0 + 3 else "cyan_terracotta" if (x + z) % 2 else "light_blue_terracotta")
            put(x, -4, z, "stone_bricks")
    for x in (cx - 1, cx, cx + 1):                      # steps down at its south end
        put(x, 0, pz1, stairs("ashbound:pale_limestone", "south"))
        put(x, -1, pz1, PL)
        put(x, -1, pz1 - 1, stairs("ashbound:pale_limestone", "south"))
        put(x, -2, pz1 - 1, PL)
    for x in (cx - 3, cx, cx + 3):                      # the lions on the north wall, pouring
        sculpt("lion_spout", x, iz0, "south", y=0)
    # pale piers at the pool's corners, chandeliers between them
    for x, z in ((px0 - 1, pz1 + 1), (px1 + 1, pz1 + 1)):
        for y in range(1, 11):
            put(x, y, z, PL if y not in (1, 10) else "ashbound:carved_limestone")
        put(x, 11, z, PL)
    for x in (cx - 3, cx + 3):
        chandelier(x, pz0 + 3, 11, 7)
    # the cold plunge at the west end, rimmed in pale stone over packed ice
    for x in range(ix0, ix0 + 3):
        for z in range(iz0, iz0 + 5):
            edge = x == ix0 + 2 or z == iz0 + 4
            put(x, 0, z, PL if edge else WATER)
            if not edge:
                put(x, -1, z, "packed_ice")
    # the boiler in the north-east corner, its pipe along the wall to the pool
    sculpt("bath_boiler", ix1 - 1, iz0, "west")
    put(px1 + 2, 1, iz0, "lightning_rod[facing=west,powered=false,waterlogged=false]")
    # tubs, benches, braziers and ferns
    sculpt("bath_tub", ix1 - 1, iz1 - 3, "west")
    sculpt("bath_tub", ix1 - 1, iz1 - 1, "west")
    sculpt("towel_bench", ix0, iz1, "north")
    sculpt("towel_bench", ix0 + 3, iz1, "north")
    sculpt("towel_bench", ix1 - 4, iz1, "north")
    for x, z in ((ix0, iz0 + 6), (ix1, iz1 - 5)):
        sculpt("steam_brazier", x, z)
    for x in (cx - 2, cx + 2):
        sculpt("bath_plant", x, iz1)
    put(ix0 + 2, 1, iz1, "barrel[facing=up,open=false]")
    for x in (ix0 + 3, ix0 + 5):
        put(x, 1, iz0 + 6, "white_carpet")
    S.marks["bathkeeper"] = (cx + 2, 1, Z1 - 3)


def shrine(cx, cz):
    """A wayside shrine: a stepped plinth, four pale piers under a little slate pyramid, an ember bowl on the altar
    between them, candles and flowers left at its foot."""
    for dx in range(-3, 4):
        for dz in range(-3, 4):
            ring = max(abs(dx), abs(dz))
            put(cx + dx, 0, cz + dz, LB if ring < 3 else FLAG)
            put(cx + dx, -1, cz + dz, "stone")
            if ring == 3:
                continue
            put(cx + dx, 1, cz + dz, SLAB % "stone_brick" if ring == 2 else PL)
    for dx in (-2, 2):
        for dz in (-2, 2):
            for y in range(1, 5):
                put(cx + dx, y, cz + dz, PL if y < 4 else "ashbound:carved_limestone")
    put(cx, 2, cz, "polished_andesite")
    put(cx, 3, cz, "campfire[facing=south,lit=true,signal_fire=false,waterlogged=false]")
    for dx, dz in ((-1, 1), (1, 1), (-1, -1), (1, -1)):
        put(cx + dx, 2, cz + dz, "candle[candles=%d,lit=true,waterlogged=false]" % (2 + (dx > 0)))
    for k in range(4):
        r = 3 - k
        y = 5 + k
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if max(abs(dx), abs(dz)) == r:
                    f = "south" if dz == -r else "north" if dz == r else "east" if dx == -r else "west"
                    put(cx + dx, y, cz + dz, stairs("ashbound:slate_shingle", f) if r else SLATE)
                elif k:
                    put(cx + dx, y, cz + dz, SLATE)
    put(cx, 9, cz, "end_rod[facing=up]")
    for dx, dz in ((-3, 0), (3, 0), (0, 3)):
        if (cx + dx, 1, cz + dz) not in S.B:
            put(cx + dx, 1, cz + dz, pick(*[(f, 1) for f in H.FLOWERS]))
    S.marks["shrine_keeper"] = (cx, 1, cz + 3)


def masons_yard(road_s, road_n):
    """The masons' yard under the bank: a low wall round it with a gate to Forge Street, cut stone stacked on pallets,
    a timber gantry with a block slung from it, stonecutters, a column half dressed, the lodge in the corner."""
    X0, X1 = -176, -140
    Z1 = road_band(road_s, X0, X1) - 2
    Z0 = road_band(road_n, X0, X1, north=False) + 2
    if Z1 - Z0 < 12:
        print("  (no room for the masons' yard: %d deep)" % (Z1 - Z0))
        return
    gx = (X0 + X1) // 2
    for x in range(X0, X1 + 1):
        for z in range(Z0, Z1 + 1):
            if GROUND(x, z) != 0 or wet(x, z):
                continue
            edge = x in (X0, X1) or z in (Z0, Z1)
            pave(x, z, "gravel" if noise(x, z, 4, 481) > 0.55 else "andesite" if noise(x, z, 3, 482) > 0.6 else "stone")
            if edge and not (z == Z1 and abs(x - gx) <= 2) and not built(x, z, 1, 1):
                pier = (x - X0) % 6 == 0 or z in (Z0, Z1) and x in (X0, X1)
                put(x, 1, z, BODY if pier else "stone_brick_wall")
                if pier:
                    put(x, 2, z, PL)
    YARD.update((x, z) for x in range(X0, X1 + 1) for z in range(Z0, Z1 + 1))
    fn, w, d = H.KINDS["cottage"]
    build_house(fn, (X0 + 2, Z1 - w - 1), "east", {"roof": "ashbound:slate_shingle"})
    stones = (BODY, PL, "smooth_stone", "polished_andesite", LB, "ashbound:statue_stone")
    for i, x in enumerate(range(X0 + 13, X1 - 2, 4)):
        for z in (Z0 + 3, Z0 + 7):
            if z > Z1 - 4 or (abs(x - gx) < 6 and z == Z0 + 7):
                continue
            st = stones[(i + z) % len(stones)]
            n = 2 + (i + z) % 2
            for dx in (0, 1):
                for dz in (0, 1):
                    put(x + dx, 1, z + dz, "spruce_slab[type=bottom,waterlogged=false]")
                    for y in range(2, n + 1 + (dx + dz == 0)):
                        put(x + dx, y, z + dz, st)
    # the gantry: two posts and a beam, a block slung on a chain
    gz = Z0 + 9
    for x in (gx - 3, gx + 3):
        for y in range(1, 10):
            put(x, y, gz, "spruce_log[axis=y]")
    for x in range(gx - 3, gx + 4):
        put(x, 10, gz, "spruce_log[axis=x]")
    for y in range(5, 10):
        put(gx, y, gz, "chain[axis=y,waterlogged=false]")
    put(gx, 4, gz, PL)
    put(gx, 1, gz + 1, "stonecutter[facing=south]")
    put(gx - 5, 1, Z1 - 3, "stonecutter[facing=south]")
    put(gx + 5, 1, Z1 - 3, "grindstone[face=floor,facing=south]")
    for y, st in ((1, PL), (2, PL), (3, "ashbound:carved_limestone")):
        put(X1 - 4, y, Z1 - 4, st)
    for x in range(X1 - 8, X1 - 5):
        put(x, 1, Z1 - 3, "ashbound:pale_limestone_wall" if x != X1 - 6 else PL)
    S.marks["mason"] = (gx + 1, 1, gz + 2)
    S.marks["mason_hand"] = (gx - 4, 1, Z1 - 4)
    print("  the masons' yard at %d..%d, z %d..%d" % (X0, X1, Z0, Z1))


def hide_rack(x, z, wools):
    """A drying frame: two posts and a pole, hides (or dyed cloth) hung from it."""
    put(x, 1, z, "spruce_fence")
    put(x, 2, z, "spruce_fence")
    put(x + len(wools) + 1, 1, z, "spruce_fence")
    put(x + len(wools) + 1, 2, z, "spruce_fence")
    FENCES.update({(x, 1, z), (x, 2, z), (x + len(wools) + 1, 1, z), (x + len(wools) + 1, 2, z)})
    for dx in range(len(wools) + 2):
        put(x + dx, 3, z, "stripped_spruce_log[axis=x]")
    for dx, wl in enumerate(wools):
        put(x + dx + 1, 2, z, wl)


def tannery(road):
    """The tannery at the ward's far end, downwind behind the lane: soaking pits in rows (lime, bark, water), the
    hides on frames, a scraping beam, barrels of bark, the tanner's cottage."""
    X0, X1 = -198, -176
    Z1 = road_band(road, X0, X1) - 2
    Z0 = Z1 - 18
    cells = [(x, z) for x in range(X0, X1 + 1) for z in range(Z0, Z1 + 1)
             if GROUND(x, z) == 0 and in_town(x, z) and not wet(x, z) and not built(x, z, 1, 3) and (x, z) not in ROAD]
    if len(cells) < 200:
        print("  (no room for the tannery)")
        return
    YARD.update(cells)
    cs = set(cells)
    for (x, z) in cells:
        pave(x, z, "packed_mud" if noise(x, z, 4, 491) > 0.4 else "coarse_dirt")
    fills = (WATER, "mud", WATER, "water_cauldron[level=3]")
    k = 0
    for px in range(X0 + 2, X1 - 3, 4):
        for pz in (Z0 + 3, Z0 + 7):
            if not all((px + dx, pz + dz) in cs for dx in range(-1, 3) for dz in range(-1, 3)):
                continue
            for dx in range(-1, 3):
                for dz in range(-1, 3):
                    rim = dx in (-1, 2) or dz in (-1, 2)
                    put(px + dx, 0, pz + dz, "stone_bricks" if rim else fills[k % 3])
                    if not rim:
                        put(px + dx, -1, pz + dz, "stone_bricks")
            k += 1
    hides = ("brown_wool", "white_wool", "brown_wool", "light_gray_wool")
    for i, z in enumerate(range(Z0 + 11, Z1 - 1, 3)):
        x = X0 + 2 + i % 2
        if all((x + dx, z) in cs for dx in range(6)):
            hide_rack(x, z, [hides[(i + j) % 4] for j in range(4)])
    for z in range(Z0 + 11, Z1 - 1, 2):
        x = X1 - 3
        if (x, z) in cs and not built(x, z, 1, 1):
            put(x, 1, z, "barrel[facing=up,open=false]")
            if z % 4 == 1:
                put(x, 2, z, "barrel[facing=up,open=false]")
    S.marks["tanner"] = (X0 + 10, 1, Z0 + 10)
    print("  the tannery at %d..%d, z %d..%d" % (X0, X1, Z0, Z1))


def dyers(road):
    """The dyers on the strip by the river below the bank: cloth drying on frames in every colour, vats, the dye
    house by the water."""
    colours = ("red_wool", "yellow_wool", "blue_wool", "orange_wool", "green_wool", "purple_wool", "cyan_wool", "magenta_wool")
    n = 0
    for x in range(14, 58, 8):
        zs = [z for (cx, z) in road.cells if cx == x]
        if not zs:
            continue
        for z in range(max(zs) + 2, max(zs) + 9, 3):
            if all(open_ground(x + dx, z) and (x + dx, z) not in ROAD for dx in range(7)):
                hide_rack(x, z, [colours[(n + j) % 8] for j in range(5)])
                n += 1
                if open_ground(x + 7, z + 1):
                    put(x + 7, 1, z + 1, "water_cauldron[level=3]")
    for x, z in ((60, -56), (61, -55)):
        if open_ground(x, z):
            put(x, 1, z, "barrel[facing=up,open=false]")
    S.marks["dyer"] = (36, 1, max(z for (cx, z) in road.cells if cx == 36) + 1)
    print("  the dyers: %d frames" % n)


def wards(R):
    """Step 6: the Forge Ward and the Hearth Ward in the field between the lower city and the terrace bank."""
    hearth_square()
    bathhouse()
    shrine(*SHRINE)
    foundry(R["forge"], R["underbank"])
    masons_yard(R["forge"], R["underbank"])
    tannery(R["tanners"])
    dyers(R["dyers"])
    n = 0
    for side in "ns":
        n += frontage(R["forge"], side, FORGE_MIX, alley=0.12)
        n += frontage(R["ember"], side, HEARTH_MIX, alley=0.15)
        n += frontage(R["tanners"], side, HEARTH_MIX, alley=0.15)
    for side in "we":
        n += frontage(R["bellows"], side, FORGE_MIX, alley=0.1, step=6)
        n += frontage(R["hearth"], side, HEARTH_MIX, alley=0.12)
    for side in "ens":
        n += frontage(R["hsq"], side, HEARTH_MIX, alley=0, step=8, yards=(5, 9))
    n += frontage(R["underbank"], "s", HEARTH_MIX, alley=0.2, yards=(5, 10))
    print("  the wards: %d houses" % n)
    return n


# ================================================================ the citadel

CIT_Z = -127                          # the Stair of Champions' foot, on Guild Lane
CIT_HW = 5                            # its half-width
GATE = (-9, -161, 9, -152)            # the gatehouse: x0, z at its back, x1, z at its front (on the lip)
WARDEN = (0, -177)                    # the Ash Warden's plinth (the statue is its own pass)
KEEP = (-76, -172, -41, -160)         # the Lord's Keep: its great hall
DONJON = (-40, -178, -28, -166)       # and its donjon on the court
NAVE = (30, -175, 54, -163)           # the Sanctuary of Embers: its nave, the apse east of it at the falls' pool
STOWER = (21, -173, 29, -165)         # and its west tower on the court
CHAMPIONS = ("guardian", "hammer", "greatsword", "daggers", "archer", "black_mage", "white_mage", "summoner")
LIP = {}


def ground_works(x0, z0, x1, z1, top, margin=2):
    """Footings and a flagstone apron under a building, the ground cut away over it (into the cliff's foot)."""
    for x in range(x0 - margin, x1 + margin + 1):
        for z in range(z0 - margin, z1 + margin + 1):
            for y in (-2, -1):
                put(x, y, z, GS)
            put(x, 0, z, FLAG)
            inside = x0 <= x <= x1 and z0 <= z <= z1
            for y in range(1, top + 1 if inside else max(1, GROUND(x, z)) + 4):
                if S.get(x, y, z) is None:
                    put(x, y, z, "air")


def portal(face, c, o, i, w=1, h=5, ring=True):
    """A pointed doorway through a two-thick wall, a pale ring round it on the outer face."""
    def at(a, y, d):
        return (a, y, d) if face == "x" else (d, y, a)

    def open_(a, y, g=0):
        k = abs(a - c)
        return k <= w + g and y <= h or k < w + g and y <= h + w + g - k
    for a in range(c - w - 2, c + w + 3):
        for y in range(1, h + w + 4):
            if open_(a, y):
                put(*at(a, y, o), "air")
                put(*at(a, y, i), "air")
            elif ring and open_(a, y, 1):
                put(*at(a, y, o), PL)
    out = o + (o - i)                                      # the plinth's stair across the sill: a step up, then a drop
    for a in range(c - w, c + w + 1):
        if "stairs" in (S.get(*at(a, 1, out)) or ""):
            put(*at(a, 1, out), "air")


def gothic_hall(X0, Z0, X1, Z1, eave, bays, deep=2, pinnacles=False, front_only=False):
    """A long hall in the guild's masonry, its ridge along x: two-thick walls, a battered plinth, buttresses between
    the bays with a tall window in each, a steep slate roof, crow-stepped gables. Returns the ridge's height."""
    zc = (Z0 + Z1) / 2
    for x in range(X0, X1 + 1):
        for z in range(Z0, Z1 + 1):
            shell = x in (X0, X0 + 1, X1 - 1, X1) or z in (Z0, Z0 + 1, Z1 - 1, Z1)
            quoin = x in (X0, X1) and z in (Z0, Z0 + 1, Z1 - 1, Z1) or z in (Z0, Z1) and x in (X0 + 1, X1 - 1)
            for y in range(1, eave + 1):
                put(x, y, z, wall_stone(y, quoin) if shell else "air")
            put(x, 0, z, FLAG)
    for x in range(X0 - 1, X1 + 2):
        for z in range(Z0 - 1, Z1 + 2):
            if X0 <= x <= X1 and Z0 <= z <= Z1:
                continue
            f = "south" if z < Z0 else "north" if z > Z1 else "east" if x < X0 else "west"
            put(x, 1, z, stairs("polished_andesite", f))
            if X0 <= x <= X1:
                put(x, eave, z, stairs("ashbound:pale_limestone", f, "top"))
    # buttresses between the bays, stepped back as they rise
    for i in range(len(bays) - 1):
        bx = (bays[i] + bays[i + 1]) // 2
        for sgn, zf in ((1, Z1), (-1, Z0)):
            if front_only and sgn < 0:
                continue
            for k in range(1, deep + 1):
                z = zf + sgn * k
                yt = eave - 2 - 4 * (k - 1)
                for y in range(1, yt):
                    put(bx, y, z, PLINTH if y <= 2 else BODY)
                put(bx, yt, z, stairs("stone_brick", "north" if sgn > 0 else "south"))
            if pinnacles:
                for y, st in ((eave - 2, PL), (eave - 1, PL), (eave, PL), (eave + 1, PL),
                              (eave + 2, "ashbound:pale_limestone_wall"), (eave + 3, "ashbound:pale_limestone_wall"),
                              (eave + 4, "end_rod[facing=up]")):
                    put(bx, y, zf + sgn, st)
    for c in bays:
        window("x", c, Z1, Z1 - 1, 4, eave - 5, "south")
        if not front_only:
            window("x", c, Z0, Z0 + 1, 4, eave - 5, "north")
    # the roof: slate, a full course under every row, the ridge capped where the hall's an odd number deep
    n = (Z1 - Z0 + 3) // 2
    for k in range(n):
        y = eave + 1 + k
        for x in range(X0 + 2, X1 - 1):
            for z, f in ((Z1 + 1 - k, "north"), (Z0 - 1 + k, "south")):
                put(x, y, z, stairs("ashbound:slate_shingle", f))
                if k:
                    put(x, y - 1, z, SLATE)
    if (Z1 - Z0) % 2 == 0:
        for x in range(X0 + 2, X1 - 1):
            put(x, eave + n - 1, int(zc), SLATE)
            put(x, eave + n, int(zc), SLAB % "ashbound:slate_shingle")
    for x in (X0, X0 + 1, X1 - 1, X1):
        for z in range(Z0, Z1 + 1):
            k = min(z - Z0, Z1 - z)
            yt = eave + 4 + 2 * (k // 2)
            for y in range(eave + 1, yt + 1):
                put(x, y, z, PL if y == yt else BODY)
            if x in (X0, X1):
                put(x, yt + 1, z, SLAB % "ashbound:pale_limestone")
    return eave + n


def trusses(X0, Z0, X1, Z1, eave, xs):
    for x in xs:
        for z in range(Z0 + 2, Z1 - 1):
            put(x, eave, z, "dark_oak_log[axis=z]")
        zc = (Z0 + Z1) // 2
        for y in range(eave + 1, eave + (Z1 - Z0) // 2):
            put(x, y, zc, "dark_oak_log[axis=y]")


def spire(cx, cz, y0, r=5.4, h=32, lucarnes=True):
    """The guild belfry's crown made general: an octagonal lantern with lancets, a tall dark spire banded in gilt and
    blackstone over it, lucarnes on its four faces, a gilded finial."""
    ro, ri = r - 0.8, r - 1.8
    R = int(r) + 2
    for dx in range(-R, R + 1):
        for dz in range(-R, R + 1):
            o = octo(dx, dz)
            x, z = cx + dx, cz + dz
            if o <= ro:
                put(x, y0, z, PL)                       # its footing: the lantern stands on it, not on air
            for y in range(y0 + 1, y0 + 10):
                if ri < o <= ro:
                    lanc = y in range(y0 + 3, y0 + 8) and (dx == 0 or dz == 0 or abs(dx) == abs(dz))
                    put(x, y, z, "ashbound:leaded_glass_pane" if lanc else PL if y in (y0 + 1, y0 + 9) else BODY)
                elif o <= ri:
                    put(x, y, z, "air" if y > y0 + 1 else PL)
            if ro < o <= ro + 1:
                put(x, y0 + 9, z, stairs("ashbound:pale_limestone", "north" if abs(dz) >= abs(dx) and dz > 0 else
                                         "south" if abs(dz) >= abs(dx) else "west" if dx > 0 else "east", "top"))
            if o <= ri:
                put(x, y0 + 2, z, LIGHT if (dx, dz) == (0, 0) else "air")
    for k in range(h):
        y = y0 + 10 + k
        rr = r * (1 - k / h) ** 1.05
        for dx in range(-R, R + 1):
            for dz in range(-R, R + 1):
                o = octo(dx, dz)
                if o <= rr + 0.3 and (o > rr - 1.3 or k == 0):
                    put(cx + dx, y, cz + dz, "ashbound:gilded_tiles" if k == h * 9 // 32 else
                        "polished_blackstone_bricks" if k == h * 19 // 32 else "deepslate_tiles")
    if lucarnes:
        k = 4
        y = y0 + 10 + k
        n = round(r * (1 - k / h) ** 1.05) + 1
        for vx, vz in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            for a in (-1, 0, 1):
                px, pz = cx + vx * n + vz * a, cz + vz * n + vx * a
                put(px, y, pz, "ashbound:leaded_glass_pane" if a == 0 else PL)
                put(px, y + 1, pz, "ashbound:leaded_glass_pane" if a == 0 else PL)
                put(px - vx, y, pz - vz, "air" if a == 0 else "deepslate_tiles")
            side = ("west", "east") if vz else ("north", "south")
            px, pz = cx + vx * n, cz + vz * n
            put(px - abs(vz), y + 2, pz - abs(vx), stairs("deepslate_tile", side[1]))
            put(px + abs(vz), y + 2, pz + abs(vx), stairs("deepslate_tile", side[0]))
            put(px, y + 2, pz, "deepslate_tiles")
            put(px, y + 3, pz, SLAB % "deepslate_tile")
    put(cx, y0 + 10 + h, cz, "ashbound:gilded_tiles")
    put(cx, y0 + 11 + h, cz, "end_rod[facing=up]")


def square_tower(X0, Z0, X1, Z1, top, stages, faces="nsew"):
    """A square tower's shaft: two-thick walls with pale bands at its floors, a window or two a face each stage, a
    corbelled gallery round its top with a parapet and a turret at each corner. Returns its centre."""
    cx, cz = (X0 + X1) // 2, (Z0 + Z1) // 2
    for x in range(X0, X1 + 1):
        for z in range(Z0, Z1 + 1):
            shell = x in (X0, X0 + 1, X1 - 1, X1) or z in (Z0, Z0 + 1, Z1 - 1, Z1)
            quoin = x in (X0, X1) and z in (Z0, Z1)
            for y in range(1, top + 1):
                if shell:
                    put(x, y, z, PL if y in stages or y == top else wall_stone(min(y, 12), quoin))
                elif y in stages:
                    put(x, y, z, "spruce_planks")
                elif y == top:
                    put(x, y, z, PL)
                else:
                    put(x, y, z, "air")
            put(x, 0, z, FLAG)
    # a ladder up the inside of the west wall, through the floors
    for y in range(1, top):
        put(X0 + 2, y, Z0 + 2, "ladder[facing=east,waterlogged=false]")
    half = (X1 - X0) // 2
    for s0, s1 in zip((0,) + tuple(stages), tuple(stages) + (top,)):
        y0, y1 = s0 + 3, s1 - 4
        if y1 - y0 < 2:
            continue
        cs = (0,) if half < 6 or s0 > 20 else (-3, 3)
        for c in cs:
            if "s" in faces:
                window("x", cx + c, Z1, Z1 - 1, y0, y1, "south")
            if "n" in faces:
                window("x", cx + c, Z0, Z0 + 1, y0, y1, "north")
            if "e" in faces and s0 > 0:
                window("z", cz + c, X1, X1 - 1, y0, y1, "east")
            if "w" in faces and s0 > 0:
                window("z", cz + c, X0, X0 + 1, y0, y1, "west")
    for x in range(X0 - 1, X1 + 2):
        for z in range(Z0 - 1, Z1 + 2):
            if X0 <= x <= X1 and Z0 <= z <= Z1:
                continue
            f = "south" if z < Z0 else "north" if z > Z1 else "east" if x < X0 else "west"
            put(x, 1, z, stairs("polished_andesite", f))
            put(x, top - 1, z, stairs("ashbound:pale_limestone", f, "top"))
            put(x, top, z, PL)
            put(x, top + 1, z, "ashbound:pale_limestone_wall")
    # clasping buttresses at the corners, stepped
    for sx, xx in ((-1, X0), (1, X1)):
        for sz, zz in ((-1, Z0), (1, Z1)):
            for (x, z), yt in (((xx + sx, zz), top - 12), ((xx, zz + sz), top - 12), ((xx + sx, zz + sz), top - 20)):
                for y in range(1, yt):
                    put(x, y, z, PLINTH if y <= 2 else BODY)
                put(x, yt, z, stairs("stone_brick", "west" if x > X1 else "east" if x < X0 else
                                     "north" if z > Z1 else "south"))
    for x, z in ((X0, Z0), (X1, Z0), (X0, Z1), (X1, Z1)):
        turret(x + 0.5, z + 0.5, top - 3, top + 6, 1.7, 9)
    return cx, cz


# ---------------------------------------------------------------- the stair and the wall

def champion_plinth(cx, cz, y0, role, face):
    """A champion's plinth beside the stair: a stepped base, a pale-capped shaft for the statue, braziers on the
    base's two corners by the stair."""
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            x, z = cx + dx, cz + dz
            edge = max(abs(dx), abs(dz)) == 2
            for y in range(min(GROUND(x, z), y0) - 2, y0 + 1):
                put(x, y, z, PLINTH if y < y0 - 1 else BODY)
            if edge:
                f = "south" if dz < 0 and abs(dz) >= abs(dx) else "north" if abs(dz) >= abs(dx) else \
                    "east" if dx < 0 else "west"
                put(x, y0 + 1, z, PL if abs(dx) == abs(dz) else stairs("ashbound:pale_limestone", f))
            else:
                for y in range(y0 + 1, y0 + 4):
                    put(x, y, z, BODY if y < y0 + 3 else PL)
                put(x, y0 + 4, z, "ashbound:carved_limestone" if (dx, dz) == (0, 0) else PL)
            for y in range(y0 + 1, y0 + 6):
                if (x, y, z) not in S.B:
                    put(x, y, z, "air")
    sx = 1 if face == "east" else -1
    for dz in (-2, 2):
        put(cx + 2 * sx, y0 + 2, cz + dz, "campfire[facing=south,lit=true,signal_fire=false,waterlogged=false]")
    S.marks["champion:" + role] = (cx, y0 + 5, cz)


def stair_of_champions():
    """Step 5's climb: a grand stair from Guild Lane up the citadel's bank, the eight champions on plinths beside it."""
    rise = L.CITADEL - L.TERRACE
    grand_stair(0, CIT_Z, CIT_HW, rise=rise)
    k = 0
    for i in (5, 10, 15, 19):
        for s in (-1, 1):
            champion_plinth(s * 10, CIT_Z - i, i, CHAMPIONS[k], "west" if s > 0 else "east")
            k += 1


def lip_line():
    """The citadel's lip: the southernmost cell of its flat at each x, smoothed (in the citadel's frame)."""
    raw = {}
    for x in range(-112, 104):
        z = round(L.z_citadel(x)) - 14
        while z > -192 and GROUND(x, z) < 0:
            z -= 1
        if z > -175:
            raw[x] = z
    xs = sorted(raw)
    for x in range(-106, 99):
        near = [raw[a] for a in range(x - 4, x + 5) if a in raw]
        if near:
            LIP[x] = round(sum(near) / len(near))
    # over the river the line's carried straight across from bank to bank
    for x in range(-106, 99):
        if x not in LIP:
            lo = max([a for a in LIP if a < x], default=None)
            hi = min([a for a in LIP if a > x], default=None)
            if lo is not None and hi is not None:
                LIP[x] = round(LIP[lo] + (LIP[hi] - LIP[lo]) * (x - lo) / (hi - lo))
    return xs


def water_top(x, z):
    """The water's top in a column of the citadel's frame (None if it's dry)."""
    for y in range(1, -10, -1):
        if (S.get(x, y, z) or "").startswith("water"):
            return y
    return None


WALK = 9                              # the curtain's wall walk


def curtain_wall():
    """The citadel's curtain on its lip: a battered skirt down the bank, a body in the guild's masonry, a corbelled
    crenellated parapet, round towers on it with tall dark cones, an arched water gate where the river leaves."""
    lip_line()
    wet_x = [x for x in LIP if any(water_top(x, LIP[x] + d) is not None for d in (-2, 0, 2))]
    w0, w1 = (min(wet_x), max(wet_x)) if wet_x else (None, None)
    for x in sorted(LIP):
        if abs(x) <= GATE[2]:
            continue
        zl = LIP[x]
        zs = range(zl - 2, max(zl, LIP.get(x - 1, zl), LIP.get(x + 1, zl)) + 1)
        river = w0 is not None and w0 - 1 <= x <= w1 + 1
        wt = max([t for t in (water_top(x, z) for z in range(zl - 3, zl + 4)) if t is not None], default=None)
        if river and wt is not None:
            xc, hs = (w0 + w1) / 2, (w1 - w0) / 2 + 1.5
            arch = min(WALK - 3, wt + 2 + int(1.4 * (hs - abs(x - xc))))
        else:
            arch = None
        for z in zs:
            outer = z == zs[-1]
            base = min(GROUND(x, z), 0) - 2
            for y in range(base, WALK + 1):
                if arch is not None and y <= arch:
                    if y > wt and z == zl - 1:
                        put(x, y, z, "iron_bars[waterlogged=false]")
                    continue
                if y == WALK:
                    put(x, y, z, FLAG if not outer else BODY)
                else:
                    put(x, y, z, PLINTH if y <= 0 else PL if y == 3 or arch is not None and y == arch + 1
                        else pick((BODY, 40), ("cracked_stone_bricks", 1), ("mossy_stone_bricks", 1 if y < 4 else 0)))
            for y in range(WALK + 1, WALK + 4):
                if (x, y, z) not in S.B:
                    put(x, y, z, "air")
        zo = zs[-1] + 1
        # the battered skirt down the bank
        if arch is None:
            for d in (0, 1, 2):
                z = zo + d
                g = GROUND(x, z)
                yt = 2 - 2 * d
                if g < yt:
                    for y in range(g - 2, yt):
                        put(x, y, z, PLINTH)
                    put(x, yt, z, stairs("polished_andesite", "north"))
        # corbels, the parapet stood out on them, merlons
        put(x, WALK - 1, zo, stairs("ashbound:pale_limestone", "north", "top"))
        if x % 3 == 0:
            put(x, WALK - 2, zo, stairs("ashbound:pale_limestone", "north", "top"))
        for y in (WALK, WALK + 1):
            put(x, y, zo, BODY)
        if x % 4 in (0, 1):
            put(x, WALK + 2, zo, BODY)
            put(x, WALK + 3, zo, SLAB % "ashbound:pale_limestone")
        else:
            put(x, WALK + 2, zo, SLAB % "ashbound:pale_limestone")
        put(x, WALK + 1, zl - 2, "ashbound:pale_limestone_wall")
        if x % 12 == 0 and arch is None:
            put(x, WALK + 2, zl - 2, "lantern[hanging=false,waterlogged=false]")
    # the towers: the gate's pair is the gatehouse's, then along the curtain both ways, either side of the river
    # mixed as the city walls' are: round under cones of different heights, octagons and squares with flat
    # crenellated tops and a lookout turret, a square pair either side of the water gate
    kinds = {-103: ("round", 24, 5.5, 19), -80: ("oct", 16, 4.5, 0), -52: ("round", 18, 4.5, 12),
             -27: ("oct", 21, 5.0, 0), 27: ("oct", 21, 5.0, 0), 50: ("round", 18, 4.5, 12), 97: ("round", 26, 5.5, 20)}
    if w0 is not None:
        kinds[w0 - 6] = kinds[w1 + 6] = ("square", 22, 4.5, 0)
    for t, (shape, top, r, cone) in sorted(kinds.items()):
        if t in LIP:
            wall_tower(t, LIP[t] + 1, top, r, cone, shape)
    return w0, w1


def wall_tower(cx, cz, top, r=4.5, cone=15, shape="round"):
    """A tower on the curtain from the bank's foot (round, octagonal or square): a solid base, slit windows, its door
    onto the wall walk either side, a corbelled crenellated top, and over it a tall dark cone set in from it or (with
    no cone) a flat fighting top with a lookout turret and a beacon."""
    R = int(r) + 2

    def dist(dx, dz):
        return math.hypot(dx, dz) if shape == "round" else octo(dx, dz) if shape == "oct" else max(abs(dx), abs(dz))
    for dx in range(-R, R + 1):
        for dz in range(-R, R + 1):
            d = dist(dx, dz)
            x, z = cx + dx, cz + dz
            if d <= r:
                g = min(GROUND(x, z), 0)
                shell = d > r - 1.7
                for y in range(g - 2, top + 1):
                    if not shell and 0 < y < top and y != WALK:
                        put(x, y, z, "air")
                    elif not shell:
                        put(x, y, z, "spruce_planks" if y == WALK else PL)
                    else:
                        put(x, y, z, PLINTH if y <= min(g + 2, 1) else PL if y in (WALK - 6, WALK, top) else
                            pick((BODY, 40), ("cracked_stone_bricks", 1)))
            elif d <= r + 1:
                f = "north" if abs(dz) >= abs(dx) and dz > 0 else "south" if abs(dz) >= abs(dx) else \
                    "west" if dx > 0 else "east"
                put(x, top - 1, z, stairs("ashbound:pale_limestone", f, "top"))
                put(x, top, z, PL)
                merlon = math.degrees(math.atan2(dz, dx)) % 45 < 22 if shape == "round" else (dx + dz) % 3 != 0
                put(x, top + 1, z, BODY)
                put(x, top + 2, z, BODY if merlon else SLAB % "ashbound:pale_limestone")
    # slits a few ways round, two heights
    for k, a in enumerate((90, 30, 150, 60, 120)):
        x, z = cx + round(r * math.cos(math.radians(a))), cz + round(r * math.sin(math.radians(a)))
        for y in ((3, 4) if k % 2 else (13, 14)):
            put(x, y, z, "ashbound:leaded_glass_pane")
    # doors from the wall walk, east and west
    for sx in (-1, 1):
        for d in range(int(r) - 1, int(r) + 1):
            x = cx + sx * d
            if x not in LIP:
                continue
            for z in (LIP[x] - 2, LIP[x] - 1):
                for y in (WALK + 1, WALK + 2):
                    put(x, y, z, "air")
                put(x, WALK, z, "spruce_planks")
    put(cx, WALK + 3, cz, LIGHT)
    if not cone:
        turret(cx + 0.5, cz - 1.5, top + 1, top + 7, 1.7, 8)
        put(cx, top + 1, cz + 2, "ashbound:carved_limestone")
        put(cx, top + 2, cz + 2, "campfire[facing=south,lit=true,signal_fire=false,waterlogged=false]")
        return
    for k in range(cone):
        rr = (r - 0.3) * (1 - k / cone) ** 1.1
        for dx in range(-R, R + 1):
            for dz in range(-R, R + 1):
                d = dist(dx, dz)
                if d <= rr + 0.2 and (d > rr - 1.3 or k == 0):
                    put(cx + dx, top + 1 + k, cz + dz, "deepslate_tiles")
    put(cx, top + cone, cz, "ashbound:gilded_tiles")
    put(cx, top + cone + 1, cz, "end_rod[facing=up]")


# ---------------------------------------------------------------- the gate

def gatehouse():
    """The citadel's gate at the stair's head: a block over a vaulted passage with a raised portcullis, a machicolated
    parapet, the realm's crest over the arch, two round towers clasping it."""
    X0, Z0, X1, Z1 = GATE
    TOP = 18

    def passage(dx, y, g=0):
        w = 3 + g
        return abs(dx) <= w and y <= 6 or abs(dx) < w and y <= 6 + w - abs(dx)
    ground_works(X0, Z0, X1, Z1, TOP + 3, 1)
    for x in range(X0, X1 + 1):
        for z in range(Z0, Z1 + 1):
            dx = x
            shell = x in (X0, X0 + 1, X1 - 1, X1) or z in (Z0, Z0 + 1, Z1 - 1, Z1)
            for y in range(-3, TOP + 1):
                if y <= 0:
                    put(x, y, z, FLAG if y == 0 else GS)
                elif passage(dx, y):
                    put(x, y, z, "air")
                elif shell or abs(dx) <= 4 or y == TOP:
                    put(x, y, z, PL if y in (3, TOP) else wall_stone(y))
                elif y == 9:
                    put(x, y, z, "spruce_planks")
                else:
                    put(x, y, z, "air")
    # the vault's ribs and lanterns, the murder holes over it
    for z in range(Z1 - 1, Z0, -3):
        for dx in range(-3, 4):
            put(dx, 6 + 3 - abs(dx) if abs(dx) < 3 else 6, z, PL)
        put(0, 9, z, "chain[axis=y,waterlogged=false]")
        put(0, 8, z, "lantern[hanging=true,waterlogged=false]")
    # the guard rooms either side open on the passage
    for s in (-1, 1):
        for z in range(-158, -155):
            for y in range(1, 4):
                put(s * 4, y, z, "air")
        put(s * 6, 1, -159, "barrel[facing=up,open=false]")
        put(s * 7, 1, -159, "barrel[facing=up,open=false]")
        put(s * 6, 4, -157, "lantern[hanging=true,waterlogged=false]")    # chained to the ceiling by unfloat()
        S.marks["gate_guard:%d" % (1 if s < 0 else 2)] = (s * 6, 1, -156)
    for s, z in ((-1, Z1 + 1), (1, Z1 + 1)):
        S.marks["gate_guard:%d" % (3 if s < 0 else 4)] = (s * 5, 1, z)
    # the arch's two orders, the portcullis drawn up into its slot, the drip over it
    for z, g in ((Z1, 1), (Z0, 1)):
        for dx in range(-6, 7):
            for y in range(1, 12):
                if not passage(dx, y) and passage(dx, y, g):
                    put(dx, y, z, PL)
    for dx in range(-3, 4):
        for y in range(1, 10):
            if passage(dx, y) and y >= 6 + (3 - abs(dx)) - 1 and y > 5:
                put(dx, y, Z1 - 2, "iron_bars[waterlogged=false]")
        put(dx, 11, Z1 + 1, stairs("ashbound:pale_limestone", "north"))
    # the crest: a gilded sun on a pale field, the realm's banner under it
    for dx in range(-2, 3):
        for y in range(11, 16):
            r = math.hypot(dx, y - 13)
            put(dx, y, Z1, "ashbound:gilded_tiles" if r < 1.2 else "ashbound:carved_limestone" if r < 2.3 else PL)
    put(0, 10, Z1 + 1, "red_wall_banner[facing=south]")
    # machicolations front and back, merlons all round, the roof walk
    for x in range(X0 - 1, X1 + 2):
        for z, f in ((Z1 + 1, "north"), (Z0 - 1, "south")):
            put(x, TOP - 2, z, stairs("ashbound:pale_limestone", f, "top"))
            for y in (TOP - 1, TOP):
                put(x, y, z, BODY)
            put(x, TOP + 1, z, BODY if x % 4 in (0, 1) else SLAB % "ashbound:pale_limestone")
    for x in range(X0, X1 + 1):
        for z in range(Z0, Z1 + 1):
            put(x, TOP, z, FLAG if X0 < x < X1 and Z0 < z < Z1 else PL)
    for s in (-1, 1):
        wall_tower(s * 12, Z1 - 1, 24, 4.5, 17)
        for y, st in ((TOP + 1, PL), (TOP + 2, "ashbound:pale_limestone_wall"), (TOP + 3, "ashbound:pale_limestone_wall"),
                      (TOP + 4, "end_rod[facing=up]")):
            put(s * 3, y, Z1 + 1, st)
    # a little bell-cote on the roof walk over the arch
    for dx in (-1, 1):
        for y in range(TOP + 1, TOP + 5):
            put(dx, y, Z1 - 2, PL)
    put(0, TOP + 5, Z1 - 2, PL)
    put(0, TOP + 4, Z1 - 2, "bell[attachment=ceiling,facing=south,powered=false]")
    for dx in (-1, 0, 1):
        put(dx, TOP + 6, Z1 - 2, SLAB % "deepslate_tile")


# ---------------------------------------------------------------- the keep

def lords_keep():
    """The Lord's Keep: a great hall along the citadel's west, its throne at the far end, and a tall donjon on the
    court with its own gallery and spire, the tallest thing in the city."""
    X0, Z0, X1, Z1 = KEEP
    EAVE = 16
    ground_works(X0, Z0, X1, Z1, 34)
    bays = list(range(X0 + 4, X1 - 2, 6))
    gothic_hall(X0, Z0, X1, Z1, EAVE, bays, pinnacles=True)
    trusses(X0, Z0, X1, Z1, EAVE, [(bays[i] + bays[i + 1]) // 2 for i in range(len(bays) - 1)])
    zc = (Z0 + Z1) // 2
    # the hearth on the back wall, between two windows
    for dx in range(-1, 2):
        for y in range(1, 7):
            put(-57 + dx, y, Z0 + 2, PL if abs(dx) == 1 or y == 6 else BODY if y > 3 else "air")
        put(-57 + dx, 6, Z0 + 3, stairs("ashbound:pale_limestone", "north", "top"))
    put(-57, 1, Z0 + 2, "campfire[facing=south,lit=true,signal_fire=false,waterlogged=false]")
    for y in range(EAVE - 2, EAVE + 14):
        put(-58, y, Z0, BODY if y < EAVE + 12 else PL)
        put(-57, y, Z0, BODY if y < EAVE + 12 else PL)
    put(-58, EAVE + 14, Z0, "campfire[facing=north,lit=true,signal_fire=false,waterlogged=false]")
    # the dais and the throne at the west end
    for x in range(X0 + 2, X0 + 6):
        for z in range(Z0 + 2, Z1 - 1):
            put(x, 1, z, "ashbound:pale_limestone" if x < X0 + 5 else stairs("ashbound:pale_limestone", "west"))
    tx = X0 + 3
    put(tx, 2, zc, stairs("dark_oak", "west"))
    put(tx - 1, 2, zc, "ashbound:gilded_tiles")
    put(tx - 1, 3, zc, "ashbound:gilded_tiles")
    put(tx - 1, 4, zc, "ashbound:carved_limestone")
    for dz in (-1, 1):
        put(tx, 2, zc + dz, "ashbound:gilded_tile_slab[type=bottom,waterlogged=false]")
        put(tx - 1, 2, zc + dz, "dark_oak_planks")
        put(tx - 1, 3, zc + dz, "dark_oak_planks")
    for dz in (-3, 3):
        for y in range(2, 9):
            put(X0 + 2, y, zc + dz, "air")
        put(X0 + 2, 8, zc + dz, "red_wall_banner[facing=east]")
    S.marks["lord"] = (tx, 2, zc)
    S.marks["steward"] = (tx + 3, 2, zc + 2)
    # the red runner down the hall, long tables either side, banners between the windows, chandeliers
    for x in range(X0 + 6, X1 - 1):
        for z in (zc - 1, zc, zc + 1):
            put(x, 1, z, "red_carpet")
    for z in (zc - 4, zc + 4):
        for x in range(X0 + 9, X1 - 5):
            put(x, 1, z, "dark_oak_planks" if x % 7 == 0 else "dark_oak_slab[type=top,waterlogged=false]")
            if x % 7 and x % 3 == 0:
                put(x, 2, z, "candle[candles=2,lit=true,waterlogged=false]")
        for x in range(X0 + 9, X1 - 5):
            for zz in (z - 1, z + 1):
                if Z0 + 1 < zz < Z1 - 1:
                    put(x, 1, zz, "spruce_slab[type=bottom,waterlogged=false]")
    for i in range(len(bays) - 1):
        bx = (bays[i] + bays[i + 1]) // 2
        put(bx, 8, Z0 + 2, "red_wall_banner[facing=south]")
        put(bx, 8, Z1 - 2, "red_wall_banner[facing=north]")
        chandelier(bx, zc, EAVE, EAVE - 4)
    for k, x in enumerate((X1 - 6, X1 - 4)):
        S.marks["keep_guard:%d" % (k + 1)] = (x, 1, Z1 - 3)
    # the donjon, joined on through the hall's east gable
    DX0, DZ0, DX1, DZ1 = DONJON
    ground_works(DX0, DZ0, DX1, DZ1, 50, 1)
    TOP = 44
    cx, cz = square_tower(DX0, DZ0, DX1, DZ1, TOP, (10, 19, 28, 37))
    for x in range(X1 - 1, DX0 + 2):
        for y in range(1, 5):
            put(x, y, -169, "air")
        put(x, 0, -169, FLAG)
    portal("z", cz, DX1, DX1 - 1, 1, 5)                  # onto the court
    for s in (-1, 1):
        put(DX1 + 1, 2, cz + 3 * s, "ashbound:pale_limestone")
        put(DX1 + 1, 3, cz + 3 * s, "lantern[hanging=false,waterlogged=false]")
    put(DX1 + 1, 7, cz, "red_wall_banner[facing=east]")
    S.marks["keep_captain"] = (cx + 2, 1, cz)
    spire(cx, cz, TOP + 1, 5.4, 34)


# ---------------------------------------------------------------- the sanctuary

def rose(face_x, cz, cy, r=4.2):
    """A rose window: warm stained glass in a pale ring, eight pale spokes, a gilded eye."""
    for dz in range(-5, 6):
        for dy in range(-5, 6):
            d = math.hypot(dz, dy)
            z, y = cz + dz, cy + dy
            if d <= r - 0.7:
                spoke = d > 1.2 and (dz == 0 or dy == 0 or abs(dz) == abs(dy))
                glass = ("orange", "red", "yellow")[int(d * 1.3 + (math.atan2(dy, dz) + 4) * 2) % 3]
                put(face_x, y, z, "ashbound:gilded_tiles" if d <= 0.8 else PL if spoke else
                    "%s_stained_glass_pane" % glass)
                put(face_x + 1, y, z, "air")
            elif d <= r + 0.3:
                put(face_x, y, z, PL)


def sanctuary():
    """The Sanctuary of Embers: a tall nave on flying-stepped buttresses with pinnacles, a west tower on the court
    with a rose window over a deep portal and its own spire, the apse at the east end open on the falls' pool, the
    ember burning on its altar."""
    X0, Z0, X1, Z1 = NAVE
    EAVE = 18
    zc = (Z0 + Z1) // 2
    TX0, TZ0, TX1, TZ1 = STOWER
    ground_works(TX0, Z0, X1, Z1, 36)
    bays = [33, 39, 45, 51]
    ridge = gothic_hall(X0, Z0, X1, Z1, EAVE, bays, deep=3, pinnacles=True)
    trusses(X0, Z0, X1, Z1, EAVE, [36, 42, 48])
    # the apse: a half round east of the nave, open on the pool between its piers, a half cone of slate over it
    ax, R0 = X1 + 1, 6.5
    for x in range(X1 - 1, X1 + 9):
        for z in range(Z0 - 1, Z1 + 2):
            d = math.hypot(x - ax + 0.5, z - zc)
            if x < ax or d > R0 + 0.5:
                continue
            ang = math.degrees(math.atan2(z - zc, x - ax + 0.5))
            pier = abs(((ang + 90) % 36) - 18) > 12
            for y in range(-4, 0):
                put(x, y, z, GS)
            put(x, 0, z, FLAG if d <= R0 - 1.6 else PL)
            for y in range(1, EAVE + 1):
                if d <= R0 - 1.6:
                    put(x, y, z, "air")
                elif pier or y > 11 or y in (1,):
                    put(x, y, z, wall_stone(y) if y > 1 else PLINTH)
                elif y == 11 or y == 10 and abs(((ang + 90) % 36) - 18) > 6:
                    put(x, y, z, PL)
                else:
                    put(x, y, z, "air" if y > 1 else PLINTH)
            if d > R0 - 0.6:
                put(x, EAVE, z, stairs("ashbound:pale_limestone", "west" if abs(z - zc) < 3 else
                                       "north" if z > zc else "south", "top"))
            for k in range(9):
                rr = (R0 + 0.4) * (1 - k / 9) ** 0.9
                if d <= rr + 0.2 and (d > rr - 1.4 or k == 0):
                    put(x, EAVE + 1 + k, z, SLATE)
    for z in range(Z0 + 2, Z1 - 1):                     # the chancel arch through the nave's east end
        for y in range(1, EAVE - 2):
            if abs(z - zc) <= 3 and y <= 10 or abs(z - zc) <= 2 and y <= 12 or abs(z - zc) <= 1 and y <= 13:
                for x in (X1 - 1, X1):
                    put(x, y, z, "air")
    # the ember on its altar in the apse, candles, the pool beyond
    for dz in (-1, 0, 1):
        put(X1 + 2, 1, zc + dz, PL)
        put(X1 + 2, 2, zc + dz, "ashbound:gilded_tile_slab[type=bottom,waterlogged=false]" if dz else "ashbound:gilded_tiles")
    put(X1 + 2, 3, zc, "campfire[facing=west,lit=true,signal_fire=false,waterlogged=false]")
    for dz in (-1, 1):
        put(X1 + 2, 3, zc + dz, "candle[candles=3,lit=true,waterlogged=false]")
    for dz in (-3, 3):
        put(X1 + 1, 1, zc + dz, "ashbound:carved_limestone")
        put(X1 + 1, 2, zc + dz, "magma_block")
        put(X1 + 1, 3, zc + dz, "campfire[facing=west,lit=true,signal_fire=false,waterlogged=false]")
    S.marks["priest"] = (X1 + 1, 1, zc)
    S.marks["acolyte"] = (X1 - 3, 1, zc + 3)
    # pews either side of an ember-red aisle, chandeliers over it
    for x in range(X0 + 3, X1 - 4):
        for z in range(Z0 + 2, Z1 - 1):
            if abs(z - zc) <= 1:
                put(x, 1, z, "orange_carpet")
            elif x % 2 == 0:
                put(x, 1, z, stairs("spruce", "west"))
    for x in (36, 42, 48):
        chandelier(x, zc, EAVE, EAVE - 5)
    # the west tower: the portal in two orders, the rose over it, the belfry stage, its spire
    TOP = 34
    for x in range(TX0, TX1 + 1):
        for z in range(TZ0, TZ1 + 1):
            for y in (-2, -1):
                put(x, y, z, GS)
    cx, cz = square_tower(TX0, TZ0, TX1, TZ1, TOP, (24,), faces="ns")
    for x in range(TX1 - 1, X0 + 2):
        for z in range(cz - 2, cz + 3):
            for y in range(1, 9):
                put(x, y, z, "air")
            put(x, 0, z, FLAG)
    def door(dz, y, g):
        w = 2 + g
        return abs(dz) <= w and y <= 7 or abs(dz) < w and y <= 7 + w - abs(dz)
    for dz in range(-5, 6):
        for y in range(1, 13):
            if door(dz, y, 0):
                put(TX0, y, cz + dz, "air")
                put(TX0 + 1, y, cz + dz, "air")
            for g in (1, 2):
                if not door(dz, y, g) and door(dz, y, 3):
                    put(TX0 - g, y, cz + dz, PL if door(dz, y, g + 1) else BODY if y > 2 else PLINTH)
    rose(TX0, cz, 17, 3.5)
    for s in (-1, 1):
        for y in range(1, 17):
            st = PLINTH if y <= 2 else BODY if y < 13 else PL if y == 13 else "ashbound:pale_limestone_wall" if y < 16                 else "end_rod[facing=up]"
            put(TX0 - 3, y, cz + 4 * s, st)
    for y in range(26, 32):                              # the belfry stage's openings
        for a in (-1, 0, 1):
            for d in (0, 1):
                put(TX0 + d, y, cz + a, "air")
                put(TX1 - d, y, cz + a, "air")
                put(cx + a, y, TZ0 + d, "air")
                put(cx + a, y, TZ1 - d, "air")
    for x in range(TX0 + 1, TX1):                         # the bell's beam, wall to wall over the openings
        put(x, 32, cz, "stripped_dark_oak_log[axis=x]")
    put(cx, 31, cz, "bell[attachment=ceiling,facing=west,powered=false]")
    spire(cx, cz, TOP + 1, 4.4, 30)
    return ridge


# ---------------------------------------------------------------- the court

HFACE = -201                          # the Hall of Heroes: its rock-cut front's face, in the cliff behind the Warden
HEROES = (-18, -251, 18, -213)        # the hall in the mountain: x0, z at its end, x1, z at its door
HBAYS = (-216, -222, -228, -234, -240)  # the piers' z down the hall (the bays between them)


def vault_top(d, w, s, r=1.4):
    """A pointed vault's soffit over an offset d from its middle: half-width w, springing at s, the arcs' radius r*w."""
    R = r * w
    d = abs(d)
    if d > w:
        return s - 1
    return s + math.sqrt(max(0.0, R * R - (d - (w - R)) ** 2))


def pointed(dx, y, w, h):
    """Inside a pointed opening of half-width w whose jambs stand h high."""
    return y >= 1 and abs(dx) <= w and y <= h + vault_top(dx, w + 0.5, 0) - 0.3


def relic(x, z, k, face):
    """A relic in its alcove: a dark pedestal, the hero's keepsake on it, candles, the hero's colour hung over it."""
    things = ("wither_skeleton_skull[rotation=%d]", "decorated_pot[cracked=false,facing=%s,waterlogged=false]",
              "skeleton_skull[rotation=%d]", "bell[attachment=floor,facing=%s,powered=false]",
              "lectern[facing=%s,has_book=true,powered=false]", "heavy_core[waterlogged=false]")
    rot = {"east": 12, "west": 4, "north": 8, "south": 0}[face]
    put(x, 1, z, "polished_andesite")
    t = things[k % len(things)]
    put(x, 2, z, t % rot if "rotation" in t else t % face if "%s" in t else t)
    colours = ("red", "blue", "green", "yellow", "purple", "white", "orange", "cyan", "black", "light_blue")
    return colours[k % len(colours)]


def hall_of_heroes():
    """Behind the Ash Warden, on the line of the stair and the gate: a forecourt cut into the cliff's foot, the
    hall's front carved in the rock face (pilasters, a portal of three orders, two great niches for the colossi of
    the first heroes, a frieze of candle niches, a cornice), a vaulted vestibule, then the Hall of Heroes in the
    mountain: a tall pointed nave on arcades of piers, the past heroes' statues down it, aisles with their tombs and
    relic alcoves, and at the far end the dais with the undying ember under the niche of the first of them."""
    X0, Z0, X1, Z1 = HEROES
    # ---- the forecourt: the cliff's foot cut back to the face, its sides dressed
    for x in range(-27, 28):
        for z in range(HFACE + 1, -182):
            g = GROUND(x, z)
            if g <= 0:
                continue
            if abs(x) >= 25:
                for y in range(1, min(g, 40) + 1):
                    put(x, y, z, PLINTH if y <= 2 else PL if y % 8 == 0 else BODY)
                if g <= 40:
                    put(x, g + 1, z, "ashbound:pale_limestone_wall")
                continue
            for y in range(1, g + 3):
                put(x, y, z, "air")
            put(x, 0, z, court_stone(x, z) if abs(x) > 2 else LB if abs(x) < 2 else PL)
            put(x, -1, z, "stone")
    # ---- the front: three thick, carved in the face
    top = 38
    for x in range(-24, 25):
        for z in (HFACE, HFACE - 1, HFACE - 2):
            for y in range(1, top + 1):
                put(x, y, z, PLINTH if y <= 2 else PL if y in (3, 30) else BODY)
            for y in range(top + 1, top + 6):          # the rock over the cornice, made good
                if GROUND(x, z) < y:
                    break
                put(x, y, z, BODY)
    for x in range(-24, 25):
        put(x, top, HFACE + 1, stairs("ashbound:pale_limestone", "south", "top"))
        put(x, 30, HFACE + 1, stairs("ashbound:pale_limestone", "south", "top"))
        put(x, 1, HFACE + 1, stairs("polished_andesite", "north"))      # its high side to the wall
        if x % 2 == 0:
            put(x, top + 1, HFACE, PL)
    for px in (-24, -23, -9, -8, 8, 9, 23, 24):       # pilasters, a block proud, carved caps
        for y in range(2, top):
            put(px, y, HFACE + 1, "ashbound:carved_limestone" if y in (29, 30, 31) else PL if y == 2 else BODY)
    # the great niches either side for the colossi: four deep, framed in tiles, crowned in gilt
    for s in (-1, 1):
        nx = s * 16
        for x in range(nx - 7, nx + 8):
            for y in range(1, 33):
                for z in (HFACE - 3, HFACE - 4, HFACE - 5):
                    put(x, y, z, BODY)
        for x in range(nx - 6, nx + 7):
            for y in range(4, 32):
                dx = x - nx
                if pointed(dx, y - 3, 5, 18):
                    for z in range(HFACE - 3, HFACE + 1):
                        put(x, y, z, "air")
                elif pointed(dx, y - 3, 6, 18):
                    put(x, y, HFACE, "ashbound:gilded_tiles" if y > 25 else PL)
                    put(x, y, HFACE + 1, "ashbound:carved_limestone" if y < 4 or y > 25 else BODY)
        for x in range(nx - 4, nx + 5):
            for z in range(HFACE - 3, HFACE + 3):
                for y in range(1, 4):
                    put(x, y, z, PLINTH if y < 3 else PL)
        put(nx, 3, HFACE + 2, "ashbound:gilded_tiles")
        S.marks["hero_colossus:%s" % ("w" if s < 0 else "e")] = (nx, 4, HFACE - 1)
        brazier(nx - 6, HFACE + 4, 2)
        brazier(nx + 6, HFACE + 4, 2)
    # the portal: three orders stepping in, a gilded keystone
    for k, (z, ring) in enumerate(((HFACE, PL), (HFACE - 1, "ashbound:carved_limestone"), (HFACE - 2, LB))):
        w = 6 - k
        for x in range(-9, 10):
            for y in range(1, 30):
                if pointed(x, y, w, 15):
                    put(x, y, z, "air")
                elif pointed(x, y, w + 1, 15):
                    put(x, y, z, ring)
    # the porch before it: side walls, a tall pointed arch, a steep blackstone gable with a gilt roundel, pinnacles
    pz0, pz1 = HFACE + 1, HFACE + 6
    for x in range(-10, 11):
        for z in range(pz0, pz1 + 1):
            for y in range(1, 27):
                if pointed(x, y, 7, 15):
                    put(x, y, z, "air")
                else:
                    put(x, y, z, PLINTH if y <= 2 else PL if y in (16, 26) else BODY)
            put(x, 0, z, LB if abs(x) <= 1 else FLAG)
    for x in range(-8, 9):
        for y in range(1, 27):
            if not pointed(x, y, 7, 15) and pointed(x, y, 8, 15):
                put(x, y, pz1, "ashbound:carved_limestone")
                put(x, y, pz1 + 1, PL)
    put(0, max(y for y in range(1, 30) if pointed(0, y, 8, 15)) + 1, pz1 + 1, "ashbound:gilded_tiles")
    for k in range(12):
        y = 27 + k
        for z in range(pz0, pz1 + 2):
            for x in range(-11 + k, 12 - k):
                edge = abs(x) == 11 - k
                if edge:
                    put(x, y, z, stairs("ashbound:slate_shingle", "east" if x < 0 else "west"))
                elif z >= pz1:
                    put(x, y, z, BODY if z == pz1 else PL if abs(x) == 10 - k else BODY)
                else:
                    put(x, y, z, SLATE)
    for dx, dy in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
        put(dx, 31 + dy, pz1 + 1, "ashbound:gilded_tiles")
    for sx in (-11, 11):
        for y in range(1, 42):
            st = PLINTH if y <= 2 else "ashbound:carved_limestone" if y in (16, 27) else BODY if y < 34 else                 "ashbound:pale_limestone_wall" if y < 41 else "end_rod[facing=up]"
            put(sx, y, pz1 + 1, st)
        for y in range(26, 36, 3):                       # crockets up the pinnacle's face
            put(sx, y, pz1 + 2, stairs("stone_brick", "south"))
    # banners in the heroes' colours under the cornice, and the great braziers before the porch
    colours = ("red", "blue", "yellow", "green", "purple", "white", "orange", "cyan")
    for k, x in enumerate((-21, -18, -15, -12, 12, 15, 18, 21)):
        put(x, 36, HFACE + 1, "%s_wall_banner[facing=south]" % colours[k])
    for sx in (-14, 14):
        bz = pz1 + 4
        for x in range(sx - 1, sx + 2):
            for z in range(bz - 1, bz + 2):
                for y in range(1, 4):
                    put(x, y, z, PLINTH if y == 1 else BODY)
                put(x, 4, z, PL)
                put(x, 5, z, "magma_block")
        put(sx, 6, bz, "campfire[facing=south,lit=true,signal_fire=false,waterlogged=false]")
        for x, z in ((sx - 1, bz - 1), (sx + 1, bz - 1), (sx - 1, bz + 1), (sx + 1, bz + 1)):
            put(x, 6, z, "campfire[facing=south,lit=true,signal_fire=false,waterlogged=false]")
    # ---- the vestibule: a pointed barrel vault from the portal to the hall
    for z in range(Z1 + 1, HFACE - 2):
        for x in range(-9, 10):
            for y in range(0, 24):
                inside = pointed(x, y, 5, 13)
                if inside:
                    put(x, y, z, "air")
                elif pointed(x, y, 7, 13) or y == 0:
                    put(x, y, z, BODY if y else "polished_andesite")
            put(x, 0, z, "polished_andesite" if abs(x) > 1 else LB)
        if z % 4 == 0:
            for s in (-1, 1):
                put(s * 5, 4, z, "ashbound:wall_lantern[facing=%s]" % ("east" if s < 0 else "west"))
    # ---- the hall: the shell, then the nave, the aisles and the arcades carved out of it
    NW, A0, A1 = 6.5, 9, 14.5          # the nave's half-width; the aisles from 9 to 14.5 out, the arcades between

    def soffit(x):
        dx = abs(x)
        if dx <= NW:
            return vault_top(x, NW, 18)
        if A0 <= dx <= A1:
            return vault_top(dx - (A0 + A1) / 2, (A1 - A0) / 2 + 0.1, 10)
        return None
    for x in range(X0 - 2, X1 + 3):
        for z in range(Z0 - 3, Z1 + 1):
            for y in range(-1, 32):
                put(x, y, z, BODY if y > 0 else "stone_bricks" if y < 0 else "polished_andesite")
    for x in range(X0, X1 + 1):
        dx = abs(x)
        for z in range(Z0, Z1):
            t = soffit(x) or 0
            for y in range(1, int(t) + 1):
                put(x, y, z, "air")
            # the floor: polished dark slabs, a border of bricks along the arcades, a gilt line down the middle
            if dx <= NW:
                put(x, 0, z, "ashbound:gilded_tiles" if dx == 0 and z % 2 == 0 else "polished_andesite" if dx < 5 else "deepslate_tiles")
            elif dx >= A0:
                put(x, 0, z, "deepslate_tiles" if (x + z) % 2 else "polished_andesite")
    for x in range(-6, 7):                           # the way in from the vestibule through the hall's front wall
        for y in range(1, 20):
            if pointed(x, y, 5, 13):
                put(x, y, Z1, "air")
    # the arcades: the wall between nave and aisles left standing at the piers, opened in pointed arches between
    for s in (-1, 1):
        for z in range(Z0, Z1):
            pier = any(abs(z - b) <= 1 for b in HBAYS)
            for x in (s * 7, s * 8):
                for y in range(1, 19):
                    put(x, y, z, BODY if pier or y > 13 or not open_arch(z, y) else "air")
                    if pier and y in (1, 2):
                        put(x, y, z, PLINTH)
                    if pier and y == 13:
                        put(x, y, z, "ashbound:carved_limestone")
    # the vault's ribs over each pier, and the bosses gilded
    for b in HBAYS:
        for x in range(X0, X1 + 1):
            if soffit(x) is None:
                continue
            put(x, int(soffit(x)) + 1, b, "ashbound:gilded_tiles" if abs(x) <= NW else PL)
    # relic alcoves in the outer walls, a tomb before each in the aisle; the heroes' statues down the nave
    k = 0
    bays = [(HBAYS[i] + HBAYS[i + 1]) // 2 for i in range(len(HBAYS) - 1)]
    for zc in sorted(bays):
        for s in (-1, 1):
            face = "east" if s < 0 else "west"
            ax = s * 15
            for z in range(zc - 1, zc + 2):
                for y in range(1, 8):
                    if pointed(z - zc, y, 1, 5):
                        put(ax, y, z, "air")
                        put(ax + s, y, z, "air")
                    elif pointed(z - zc, y, 2, 5):
                        put(ax, y, z, PL)
            colour = relic(ax + s, zc, k, face)
            for dz in (-1, 1):                           # the pedestal's shoulders, candles on them
                put(ax + s, 1, zc + dz, "polished_andesite")
                put(ax + s, 2, zc + dz, "candle[candles=2,lit=true,waterlogged=false]")
            put(ax - s, 9, zc, "%s_wall_banner[facing=%s]" % (colour, face))
            for z in range(zc - 1, zc + 2):
                put(ax, 8, z, "ashbound:gilded_tiles")
            # the tomb: a dark chest on a plinth, its lid in tiles, a gilded plate at its head, candles
            tx = s * 11
            for x in range(tx - 1, tx + 2):
                for z in range(zc - 2, zc + 3):
                    put(x, 1, z, PLINTH)
                    put(x, 2, z, BODY if abs(x - tx) == 1 or abs(z - zc) == 2 else "ashbound:carved_limestone")
                    put(x, 3, z, SLAB % "ashbound:pale_limestone")
            put(tx, 2, zc + 3, "ashbound:gilded_tiles")
            put(tx + s * 2, 1, zc - 2, "ashbound:vigil_candles")
            put(tx - s * 2, 1, zc + 2, "ashbound:vigil_candles")
            k += 1
    hero = 0
    for b in HBAYS:
        for s in (-1, 1):
            x = s * 5
            for dz in (-1, 0, 1):
                for dx in (0, s):
                    put(x + dx, 1, b + dz, PLINTH)
                    put(x + dx, 2, b + dz, PL)
            put(x - s, 1, b, stairs("polished_andesite", "east" if s > 0 else "west"))
            S.marks["hero:%d" % hero] = (x, 3, b)
            hero += 1
    for zc in bays:
        for s in (-1, 1):
            put(s * 6, 16, zc, "%s_wall_banner[facing=%s]" % (colours[(zc + s) % len(colours)], "east" if s < 0 else "west"))
            for dz in (-3, 3):
                put(s * 14, 6, zc + dz, "ashbound:wall_lantern[facing=%s]" % ("east" if s < 0 else "west"))
                put(s * 9, 8, zc + dz, "ashbound:wall_lantern[facing=%s]" % ("west" if s < 0 else "east"))
    # the runner down the nave to the dais, chandeliers in each bay
    for z in range(Z0 + 10, Z1 + 1):
        for x in (-1, 0, 1):
            if S.B.get((x, 1, z)) in (None, "air"):
                put(x, 1, z, "red_carpet")
    for zc in bays:
        guild_lamp(0, zc, 13)                            # the guild's own chandeliers, a wheel of candles per bay
        put(0, 12, zc, LIGHT)
    # the dais at the far end: three steps, the undying ember in its basin, the first hero's niche over it
    for i, z in enumerate(range(Z0 + 9, Z0 + 6, -1)):
        for x in range(-6, 7):
            for y in range(1, i + 2):
                put(x, y, z, "polished_andesite")
            put(x, i + 1, z, stairs("polished_andesite", "north"))
    for z in range(Z0, Z0 + 7):
        for x in range(-6, 7):
            for y in range(1, 4):
                put(x, y, z, "polished_andesite")
            put(x, 3, z, "ashbound:statue_stone" if (x + z) % 2 else "polished_andesite")
    ex, ez = 0, Z0 + 5
    for x in range(ex - 1, ex + 2):
        for z in range(ez - 1, ez + 2):
            put(x, 4, z, PL)
            put(x, 5, z, "magma_block" if (x, z) != (ex, ez) else "campfire[facing=south,lit=true,signal_fire=false,waterlogged=false]")
    for x, z in ((ex - 2, ez - 1), (ex + 2, ez - 1), (ex - 2, ez + 1), (ex + 2, ez + 1)):
        put(x, 4, z, "ashbound:candle_rack[facing=south]")
    for x in range(-5, 6):                           # the first hero's niche in the end wall
        for y in range(4, 24):
            if pointed(x, y - 3, 4, 13):
                put(x, y, Z0 - 1, "air")
                put(x, y, Z0 - 2, "air")
            elif pointed(x, y - 3, 5, 13):
                put(x, y, Z0 - 1, "ashbound:gilded_tiles" if y > 15 else PL)
    S.marks["hero:first"] = (0, 4, Z0)
    for s in (-1, 1):
        put(s * 11, 6, Z0, "%s_wall_banner[facing=south]" % ("red" if s < 0 else "orange"))
        brazier(s * 5, Z0 + 1, 3)
    S.marks["hall_warden:1"] = (-3, 1, Z1 + 3)
    S.marks["hall_warden:2"] = (3, 1, Z1 + 3)
    S.marks["hall_keeper"] = (3, 4, Z0 + 3)
    print("  the hall of heroes: front at z %d, hall %d..%d, %d heroes' plinths, %d relics" % (HFACE, Z1, Z0, hero, k))


def open_arch(z, y):
    """The arcade between two piers: open under a pointed arch springing at 9 over the bay's middle."""
    for i in range(len(HBAYS) + 1):
        a = HBAYS[i - 1] if i else HEROES[3] + 2
        b = HBAYS[i] if i < len(HBAYS) else HEROES[1] - 2
        if b + 1 < z < a - 1:
            c = (a + b) / 2
            w = (a - b) / 2 - 2
            return y <= 9 or y <= 9 + vault_top(z - c, w + 0.5, 0) - 0.3
    return False


def brazier(x, z, h=2):
    for y in range(1, h + 1):
        put(x, y, z, PL if y < h else "ashbound:carved_limestone")
    put(x, h + 1, z, "campfire[facing=south,lit=true,signal_fire=false,waterlogged=false]")


def warden_plinth():
    """The Ash Warden's plinth: an octagon in stepped tiers, a gilded plaque on its face, braziers round its foot."""
    cx, cz = WARDEN
    for dx in range(-10, 11):
        for dz in range(-10, 11):
            o = octo(dx, dz)
            x, z = cx + dx, cz + dz
            if o > 9.4:
                continue
            for y in range(-2, 1):
                put(x, y, z, GS if y < 0 else FLAG)
            f = "south" if dz < 0 and abs(dz) >= abs(dx) else "north" if abs(dz) >= abs(dx) else \
                "east" if dx < 0 else "west"
            if o > 8.4:
                put(x, 1, z, stairs("polished_andesite", f))
            elif o > 7.4:
                put(x, 1, z, PLINTH)
                put(x, 2, z, stairs("ashbound:pale_limestone", f))
            else:
                for y in range(1, 9):
                    put(x, y, z, PLINTH if y <= 2 else PL if y in (3, 8) else BODY)
                if o > 6.4:
                    put(x, 9, z, stairs("ashbound:pale_limestone", f))
                else:
                    put(x, 9, z, PL)
            for y in range(10, 14):
                if (x, y, z) not in S.B:
                    put(x, y, z, "air")
    for dx in range(-2, 3):
        for y in (5, 6):
            put(cx + dx, y, cz + 7, "ashbound:gilded_tiles" if abs(dx) < 2 else PL)
    for dx, dz in ((-5, 5), (5, 5), (-5, -5), (5, -5)):
        put(cx + dx, 9, cz + dz, "ashbound:carved_limestone")
        put(cx + dx, 10, cz + dz, "campfire[facing=south,lit=true,signal_fire=false,waterlogged=false]")
    # the Warden's blade (tools/blender/civic_sculpt.py) driven into its top, point first
    sculpt("warden_blade", cx - 5, cz - 2, "south", y=10)
    S.marks["warden"] = (cx, 10, cz)


def court_stone(x, z):
    """The court's paving: the processional way from the gate in limestone bricks, rings round the Warden's plinth,
    flagstone with pale drifts elsewhere."""
    cx, cz = WARDEN
    r = math.hypot(x - cx, z - cz)
    if abs(x) <= 2 and z > cz:
        return LB if abs(x) < 2 else PL
    if 10 < r < 11:
        return LB
    if 11 <= r < 13.5:
        return (PL, "ashbound:statue_stone")[int(math.degrees(math.atan2(z - cz, x - cx)) // 15) % 2]
    return walk_stone(x, z, 0, "walk")


def court():
    warden_plinth()
    for z in range(-162, -168, -4):
        for s in (-1, 1):
            brazier(s * 4, z)
    for s in (-1, 1):
        planter(s * 15, -165)
        bench(s * 15, -168, "north")
        lamp(s * 8, -163, "x")
        for z in (-171, -181):
            lamp(s * 16, z, "z")
    # the paving, over the flat between the curtain and the cliff's foot
    for x in range(-106, 99):
        zl = LIP.get(x)
        if zl is None:
            continue
        for z in range(zl - 3, -192, -1):
            if GROUND(x, z) != 0 or wet(x, z) or (x, 0, z) in S.B:
                continue
            if x < -80 or x > 62:
                continue
            put(x, 0, z, court_stone(x, z))
            put(x, -1, z, "stone")


def keep_garden():
    """The lord's garden west of the hall: box hedges round gravel walks, a small fountain, blossom trees, benches
    along the curtain where the lake's view is."""
    cx, cz = -92, -164
    for x in range(-106, -78):
        zl = LIP.get(x)
        if zl is None:
            continue
        for z in range(zl - 3, -175, -1):
            if GROUND(x, z) != 0 or wet(x, z) or (x, 0, z) in S.B or built(x, z, 1, 3):
                continue
            path = abs(x - cx) <= 1 or abs(z - cz) <= 1
            ring = 4 < math.hypot(x - cx, z - cz) < 6
            put(x, 0, z, "gravel" if path or ring else "grass_block[snowy=false]")
            put(x, -1, z, "stone" if path or ring else "dirt")
            if not path and not ring and (x + z) % 7 and noise(x, z, 3, 501) > 0.35:
                put(x, 1, z, "oak_leaves[distance=1,persistent=true,waterlogged=false]")
            elif not path and not ring and noise(x, z, 2, 502) > 0.7:
                put(x, 1, z, pick(("poppy", 2), ("cornflower", 2), ("oxeye_daisy", 1), ("lily_of_the_valley", 1)))
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            rim = max(abs(dx), abs(dz)) == 2
            put(cx + dx, 0, cz + dz, PL)
            put(cx + dx, 1, cz + dz, SLAB % "ashbound:pale_limestone" if rim else WATER)
    put(cx, 1, cz, PL)
    put(cx, 2, cz, "ashbound:carved_limestone")
    put(cx, 3, cz, WATER + "#flow")
    for x, z in ((-100, -165), (-85, -166), (-104, -164)):
        if GROUND(x, z) == 0:
            small_tree(x, 1, z, "cherry", 5)
    for x in range(-102, -80, 5):
        z = LIP.get(x)
        if z is not None:
            bench(x, z - 3, "south")


# the citadel's built in the walls' masonry: the same code as the guild's, its blocks swapped as they're laid
DARK = {"cracked_stone_bricks": "cracked_deepslate_bricks", "mossy_stone_bricks": "cracked_deepslate_bricks",
        "polished_andesite": "polished_deepslate", "polished_andesite_stairs": "polished_deepslate_stairs",
        "ashbound:pale_limestone": "deepslate_tiles", "ashbound:pale_limestone_stairs": "deepslate_tile_stairs",
        "ashbound:pale_limestone_slab": "deepslate_tile_slab", "ashbound:pale_limestone_wall": "polished_blackstone_wall",
        "ashbound:carved_limestone": "chiseled_deepslate", "ashbound:limestone_bricks": "deepslate_bricks",
        "ashbound:limestone_brick_stairs": "polished_blackstone_brick_stairs", "ashbound:greystone": "polished_deepslate",
        "ashbound:statue_stone": "polished_deepslate", "stone_brick_stairs": "deepslate_brick_stairs",
        "stone_brick_wall": "deepslate_brick_wall", "stone_brick_slab": "deepslate_brick_slab",
        "ashbound:slate_shingle_stairs": "polished_blackstone_brick_stairs",
        "ashbound:slate_shingles": "polished_blackstone_bricks",
        "ashbound:slate_shingle_slab": "polished_blackstone_brick_slab", "deepslate_tiles": "polished_blackstone_bricks",
        "deepslate_tile_stairs": "polished_blackstone_brick_stairs", "deepslate_tile_slab": "polished_blackstone_brick_slab",
        "polished_blackstone_bricks": "polished_blackstone", "ashbound:leaded_glass_pane": "light_gray_stained_glass_pane",
        "end_rod": "polished_blackstone_wall"}
PAVING = {FLAG, LB, PL, "ashbound:statue_stone", "ashbound:gilded_tiles", "gravel", "stone", "dirt"}


def dark(st, y):
    if not st or y <= 0 and st in PAVING:
        return st
    name, _, props = st.partition("[")
    if name == "stone_bricks":
        return pick(("deepslate_bricks", 16), ("deepslate_tiles", 3), ("cracked_deepslate_bricks", 1),
                    ("polished_deepslate", 1))
    if name not in DARK:
        return st
    if name == "end_rod" or "wall" in DARK[name]:
        return DARK[name]
    return DARK[name] + ("[" + props if props else "")


class Dark:
    """The Build with the walls' palette laid in place of the guild's."""

    def __init__(self, S):
        self.S = S

    def __getattr__(self, k):
        return getattr(self.S, k)

    def put(self, x, y, z, st, nbt=None):
        self.S.put(x, y, z, dark(st, y), nbt)

    def get(self, x, y, z):
        return self.S.get(x, y, z)


class dark_masonry:
    def __enter__(self):
        global S, put
        self.saved = S, put
        S = Dark(S)
        put = S.put

    def __exit__(self, *a):
        global S, put
        S, put = self.saved


# the Ashforge's masonry: the walls' dark stone, its roofs in verdigris copper, its windows lit like the fire inside
FORGE_MAP = {"ashbound:slate_shingle_stairs": "waxed_weathered_cut_copper_stairs", "ashbound:slate_shingles": "waxed_weathered_cut_copper",
             "ashbound:slate_shingle_slab": "waxed_weathered_cut_copper_slab", "ashbound:leaded_glass_pane": "orange_stained_glass_pane"}
COPPER = "waxed_weathered_cut_copper"
BLK, BLKB = "polished_blackstone", "polished_blackstone_bricks"


def forged(st, y):
    if st:
        name, _, props = st.partition("[")
        if name in FORGE_MAP:
            return FORGE_MAP[name] + ("[" + props if props else "")
    return dark(st, y)


class Forged(Dark):
    def put(self, x, y, z, st, nbt=None):
        self.S.put(x, y, z, forged(st, y), nbt)


class forge_masonry:
    def __enter__(self):
        global S, put
        self.saved = S, put
        S = Forged(S)
        put = S.put

    def __exit__(self, *a):
        global S, put
        S, put = self.saved


def forge_tower(cx, cz, r, h, cone=0, crown=False, body="bricks", band=BLKB, every=5):
    """A round tower in the forge's dark stone and firebrick from the ground: battered at its foot, banded in
    blackstone, glowing slits up it; a verdigris copper cone over it, or a corbelled crown smoking from its fires."""
    R = int(r) + 3
    for dx in range(-R, R + 1):
        for dz in range(-R, R + 1):
            x, z = math.floor(cx) + dx, math.floor(cz) + dz
            d = math.hypot(x + 0.5 - cx, z + 0.5 - cz)
            for y in range(1, h + 1):
                rr = r + max(0.0, 0.8 - y * 0.2)
                if d <= rr:
                    edge = d > rr - 1.2
                    put(x, y, z, (band if y % every == 0 else BLKB if y <= 2 else body if edge else "polished_deepslate"))
            if r < d <= r + 0.95:
                put(x, h, z, stairs("polished_blackstone_brick", "north" if abs(dz) >= abs(dx) and z + 0.5 > cz else
                                    "south" if abs(dz) >= abs(dx) else "west" if x + 0.5 > cx else "east", "top"))
                if crown and (dx + dz) % 2 == 0:
                    put(x, h + 1, z, "polished_blackstone_wall")
            if cone:
                for k in range(cone):
                    rr = (r + 0.7) * (1 - k / cone) ** 1.15
                    if d <= rr + 0.2 and (d > rr - 1.3 or k == 0):
                        put(x, h + 1 + k, z, COPPER)
            elif crown and d <= r - 0.8:
                put(x, h, z, "magma_block")
                if (dx + dz) % 2 == 0 and d <= r - 1.2:
                    put(x, h + 1, z, "campfire[facing=north,lit=true,signal_fire=true,waterlogged=false]")
    for k, (dx, dz) in enumerate(((0, 1), (1, 0), (0, -1), (-1, 0))):
        x, z = math.floor(cx + dx * (r - 0.3)), math.floor(cz + dz * (r - 0.3))
        for y in (5 + 4 * (k % 2), 6 + 4 * (k % 2), 13 + 3 * (k % 2), 14 + 3 * (k % 2)):
            if y < h - 1:
                put(x, y, z, "orange_stained_glass_pane")
    if cone:
        put(math.floor(cx), h + cone, math.floor(cz), "waxed_cut_copper")
        put(math.floor(cx), h + cone + 1, math.floor(cz), "end_rod[facing=up]")


def great_furnace(cx, Z0):
    """The Ashforge's heart against the nave's back wall: a stepped mass of blackstone banded in copper, its arched
    mouth glowing through an iron grate, a hood stepping into a square brick chimney that rises through the roof
    and turns into a round stack, banded and vented, to a smoking crown high over the ward."""
    fx0, fx1, fz0, fz1 = cx - 5, cx + 5, Z0 + 2, Z0 + 7
    for x in range(fx0, fx1 + 1):
        for z in range(fz0, fz1 + 1):
            put(x, 0, z, BLK)
            for y in range(1, 10):
                face = z == fz1 or x in (fx0, fx1)
                corner = x in (fx0, fx1) and z == fz1
                put(x, y, z, "chiseled_polished_blackstone" if corner and y % 3 == 0 else
                    "waxed_cut_copper" if face and y in (4, 8) else BLKB)
    for x in range(fx0 - 1, fx1 + 2):
        put(x, 1, fz1 + 1, stairs("polished_blackstone_brick", "north"))
    for z in range(fz0, fz1 + 1):
        put(fx0 - 1, 1, z, stairs("polished_blackstone_brick", "east"))
        put(fx1 + 1, 1, z, stairs("polished_blackstone_brick", "west"))

    def mouth(dx, y, g=0):
        return abs(dx) <= 2 + g and y <= 4 or abs(dx) <= 1 + g and y == 5 or abs(dx) <= g and y == 6
    for x in range(cx - 4, cx + 5):
        dx = x - cx
        for y in range(1, 9):
            if mouth(dx, y):
                put(x, y, fz1, "air")                                              # the arched recess
                put(x, y, fz1 - 1, "iron_bars[east=true,north=false,south=false,waterlogged=false,west=true]")
                for z in (fz1 - 2, fz1 - 3):                                      # the oven behind the grate
                    put(x, y, z, "lava[level=0]" if y == 1 else "air")
                put(x, y, fz1 - 4, "magma_block" if y <= 3 else "bricks")
            elif mouth(dx, y, 1):
                put(x, y, fz1, "bricks")
                for z in (fz1 - 2, fz1 - 3):
                    put(x, y, z, "bricks")
    put(cx, 7, fz1, "chiseled_polished_blackstone")
    # the hood, stepping in to the chimney
    for x in range(fx0 - 1, fx1 + 2):
        for z in range(fz0, fz1 + 2):
            edge = x in (fx0 - 1, fx1 + 1) or z == fz1 + 1
            put(x, 10, z, stairs("polished_blackstone_brick", "south" if z == fz1 + 1 else "east" if x == fx0 - 1 else "west", "top")
                if edge else BLKB)
    for x in range(fx0, fx1 + 1):
        for z in range(fz0, fz1 + 1):
            inner = cx - 4 <= x <= cx + 4 and z < fz1
            put(x, 11, z, BLKB if inner else stairs("polished_blackstone_brick", "north" if z == fz1 else
                                                    "east" if x < cx else "west"))
    # the square chimney through the roof
    for x in range(cx - 4, cx + 5):
        for z in range(Z0, Z0 + 7):
            for y in range(12, 30):
                quoin = x in (cx - 4, cx + 4) and z in (Z0, Z0 + 6)
                vent = y % 6 in (2, 3) and (x == cx and z == Z0 + 6 or z == Z0 + 3 and x in (cx - 4, cx + 4))
                put(x, y, z, "magma_block" if vent else BLKB if quoin or y % 6 == 0 else "deepslate_bricks")
    # the furnace stack: an octagon of blackstone tapering from a corbelled collar, seams of fire up its faces,
    # copper bands, a crown of spikes round the fires at its top
    czs = Z0 + 3
    TOP = 50
    for dx in range(-7, 8):
        for dz in range(-7, 8):
            o = octo(dx, dz)
            x, z = cx + dx, czs + dz
            if o <= 5.4 and not (abs(dx) <= 4 and abs(dz) <= 3):
                put(x, 29, z, stairs("polished_blackstone_brick", "north" if dz > 0 and abs(dz) >= abs(dx) else
                                     "south" if abs(dz) >= abs(dx) else "west" if dx > 0 else "east", "top"))
            for y in range(30, TOP):
                r = 4.9 - 1.4 * (y - 30) / (TOP - 30)
                if o <= r:
                    seam = o > r - 1 and (dx == 0 or dz == 0) and y % 7 != 0
                    put(x, y, z, "magma_block" if seam else "waxed_cut_copper" if y in (35, 42) else
                        "chiseled_polished_blackstone" if y % 7 == 0 else BLKB)
            if 3.0 < o <= 4.6:
                put(x, TOP, z, stairs("polished_blackstone_brick", "north" if dz > 0 and abs(dz) >= abs(dx) else
                                      "south" if abs(dz) >= abs(dx) else "west" if dx > 0 else "east", "top"))
                if (dx + dz) % 2 == 0:
                    put(x, TOP + 1, z, "polished_blackstone_wall")
                if abs(dx) == abs(dz) == 3 or {abs(dx), abs(dz)} == {0, 4}:
                    for y in range(TOP + 1, TOP + 4):
                        put(x, y, z, "polished_blackstone_wall")
            elif o <= 3.0:
                put(x, TOP, z, "magma_block" if o > 1.2 else BLKB)
                if o <= 2.4 and (dx + dz) % 2 == 0:
                    put(x, TOP + 1, z, "campfire[facing=north,lit=true,signal_fire=true,waterlogged=false]")


def cold_vault():
    """The vault the Ashforge was raised on, older than the city: pale old masonry where everything above is dark, a
    stair down from the armoury's south wall, ribs and piers round a long room, the Cold Forge at its north end facing
    the door. Lit only by a few cold lanterns: nobody has tended it. It's a pit: a broad stair goes down from the door to
    a floor deep and wide enough for what the Forge's trial calls up (13 tall)."""
    x0, x1, z0, z1 = -143, -115, -90, -53
    FL, CE = -18, -1

    def old():
        return pick(("stone_bricks", 11), ("cracked_stone_bricks", 2))
    for x in range(x0 - 1, x1 + 2):
        for z in range(z0 - 1, z1 + 2):
            wall = x in (x0 - 1, x1 + 1) or z in (z0 - 1, z1 + 1)
            for y in range(FL, CE + 1):
                put(x, y, z, old() if wall or y == CE else "air")
            put(x, FL, z, old() if wall else "polished_andesite" if (x + z) % 2 else "smooth_stone")
            put(x, FL - 1, z, "stone_bricks")
    # piers down both long walls, a rib over the room from each pair, a chiselled band at springing height
    for z in range(z0 + 2, z1, 5):
        for x in (x0, x1):
            for y in range(FL + 1, CE):
                put(x, y, z, "chiseled_stone_bricks" if y == FL + 1 or y == CE - 3 else "polished_andesite")
                put(x, y, z + 1, "chiseled_stone_bricks" if y == FL + 1 or y == CE - 3 else "polished_andesite")
        for x in range(x0, x1 + 1):
            for k in (z, z + 1):
                put(x, CE - 1, k, "stone_bricks")
        for k in (z, z + 1):
            put(x0 + 1, CE - 2, k, stairs("stone_brick", "west", "top"))
            put(x1 - 1, CE - 2, k, stairs("stone_brick", "east", "top"))
    for x in (x0 + 5, x1 - 5):                                # cold lanterns, nobody's tended them
        for z in range(z0 + 7, z1 - 4, 10):
            put(x, CE - 1, z, "chain[axis=y,waterlogged=false]")
            put(x, CE - 2, z, "chain[axis=y,waterlogged=false]")
            put(x, CE - 3, z, "soul_lantern[hanging=true,waterlogged=false]")
    # the stair, down westward along the armoury's south wall, its landing against the vault's door
    SX, Z = -119, (-51, -50)
    for i in range(10):
        x = SX - i
        for z in Z:
            put(x, -i, z, stairs("stone_brick", "east"))
            put(x, -i - 1, z, "stone_bricks")
            for y in range(-i + 1, 1):
                put(x, y, z, "air")
    for x in range(SX - 11, SX + 1):
        for y in range(-11, 0):
            put(x, y, -52, old())
            put(x, y, -49, old())
    for z in Z:
        for x in (SX - 11, SX - 10):
            put(x, -10, z, "stone_bricks")
            for y in range(-9, 1):
                put(x, y, z, "air")
        for y in range(-10, 1):
            put(SX - 12, y, z, old())
    for x in range(SX - 11, SX):                              # a rail round the stairhead
        put(x, 1, -52, "polished_blackstone_wall")
    for z in (*Z, -52):
        put(SX - 12, 1, z, "polished_blackstone_wall")
    for x in (SX - 11, SX - 10):                              # the door
        for y in range(-9, -6):
            put(x, y, -52, "air")
    put(SX - 11, -6, -52, stairs("stone_brick", "east", "top"))
    put(SX - 10, -6, -52, stairs("stone_brick", "west", "top"))
    # the great stair down from the door to the pit's floor
    for i in range(8):
        z, y = z1 - i, -10 - i
        for x in range(-133, -125):
            for k in range(FL + 1, y):
                put(x, k, z, "stone_bricks")
            put(x, y, z, stairs("stone_brick", "south"))
        for x in (-134, -125):
            for k in range(FL + 1, y + 1):
                put(x, k, z, old())
            put(x, y + 1, z, "stone_brick_wall")
    sculpt("cold_forge", -133, z0 + 1, "south", y=FL + 1)


def foundry(road_s, road_n):
    """The Ashforge, the guild's great forge under the bank, at the head of Bellows Lane: a dark hall banded in copper
    under verdigris roofs. Its gate porch between two round towers carries the guild's crest; inside, the great
    furnace glows through its grate at the back of the nave, its stack rising high over the ward; giant bellows
    either side of it, the Founders' Anvil (it smiths) before its mouth between two glowing runs of molten metal,
    great hearths (they smith), anvils (they repair), troughs and grindstones (they grind), crucibles hung in chains.
    West of the nave the armoury (armour on its stands, racks, the smithing benches), east the smelting hall (the
    pour from the blast towers, the crucible, the trip hammer, ore carts), two smoking blast towers at its end."""
    cx, Z0, Z1 = -104, -63, -46
    X0, X1 = -132, -76
    NX0, NX1 = cx - 12, cx + 12
    PX0, PX1, PZ1 = cx - 5, cx + 5, Z1 + 4                 # the gate porch, its front on the forecourt
    if road_band(road_s, PX0 - 4, PX1 + 4) <= PZ1 + 1 or road_band(road_n, X0, X1, north=False) >= Z0 - 1:
        print("  (no room for the Ashforge)")
        return
    ground_works(X0 - 4, Z0, X1 + 7, Z1, 34, margin=1)
    E_N, E_S = 16, 11                                       # the nave's eave and the side halls'
    with forge_masonry():
        gothic_hall(X0, Z0 + 1, NX0 + 1, Z1 - 1, E_S, [X0 + 4, NX0 - 3])
        gothic_hall(NX1 - 1, Z0 + 1, X1, Z1 - 1, E_S, [NX1 + 3, X1 - 4])
        gothic_hall(NX0, Z0, NX1, Z1, E_N, [NX0 + 3, NX1 - 3], deep=2, pinnacles=True, front_only=True)
        for z in (Z0 + 5, Z1 - 5):                           # arches from the nave into the side halls
            portal("z", z, NX0, NX0 + 1, w=2, h=6, ring=False)
            portal("z", z, NX1, NX1 - 1, w=2, h=6, ring=False)
        for o, i, out in ((NX0, NX0 + 1, "west"), (NX1, NX1 - 1, "east")):
            window("z", (Z0 + Z1) // 2, o, i, E_S + 10, E_S + 13, out)    # a lit window in each nave gable
        trusses(NX0, Z0, NX1, Z1, E_N, (NX0 + 3, NX0 + 6, NX1 - 6, NX1 - 3))
        trusses(X0, Z0 + 1, NX0 + 1, Z1 - 1, E_S, (X0 + 6, X0 + 11))
        trusses(NX1 - 1, Z0 + 1, X1, Z1 - 1, E_S, (X1 - 11, X1 - 6))
    for z in range(Z0 + 3, Z1 - 2):                          # the nave's plinth step, left inside the side halls
        for x in (NX0 - 1, NX1 + 1):
            put(x, 1, z, "air")
    for x in range(NX0 + 2, NX1 - 1):                        # the nave's front windows, behind the porch towers
        for z in (Z1 - 1, Z1):
            for y in range(3, E_N - 2):
                if S.get(x, y, z) in ("air", None) or "glass" in (S.get(x, y, z) or ""):
                    put(x, y, z, "deepslate_bricks")
    # floors: blackstone in the nave, deepslate tiles in the halls
    for x in range(X0 + 2, X1 - 1):
        for z in range(Z0 + 2, Z1 - 1):
            if S.get(x, 1, z) in ("air", None):
                nave = NX0 + 2 <= x <= NX1 - 2
                put(x, 0, z, (BLKB if nave else "deepslate_tiles") if (x + z) % 7 else "polished_deepslate")
    # the gate porch: two thick walls, the gate and the crest over it, a copper roof ridged back into the nave's
    E_P = 18
    for x in range(PX0, PX1 + 1):
        for z in range(Z1 + 1, PZ1 + 1):
            shell = x in (PX0, PX0 + 1, PX1 - 1, PX1) or z in (PZ1 - 1, PZ1)
            for y in range(1, E_P + 1):
                put(x, y, z, ("polished_deepslate" if y <= 2 else BLKB if y in (3, E_P) else
                              pick(("deepslate_bricks", 12), ("deepslate_tiles", 2), ("cracked_deepslate_bricks", 1))) if shell else "air")
            put(x, 0, z, BLKB)
    with forge_masonry():
        portal("x", cx, Z1, Z1 - 1, w=3, h=9, ring=False)

    def gate(k, y, g=0):
        return k <= 3 + g and y <= 9 or k < 3 + g and y <= 12 + g - k
    for x in range(cx - 6, cx + 7):
        k = abs(x - cx)
        for y in range(1, 17):
            if gate(k, y):
                put(x, y, PZ1, "air")
                put(x, y, PZ1 - 1, "air")
            elif gate(k, y, 1):
                put(x, y, PZ1, "bricks")
            elif gate(k, y, 2) and y > 9:
                put(x, y, PZ1, "waxed_cut_copper")
    for x in range(PX0, PX1 + 1):
        k = min(x - PX0, PX1 - x)
        yt = E_P + 4 + 2 * (k // 2)
        for z in (PZ1 - 1, PZ1):
            for y in range(E_P + 1, yt + 1):
                put(x, y, z, BLKB if y == yt else "deepslate_bricks")
        put(x, yt + 1, PZ1, "polished_blackstone_brick_slab[type=bottom,waterlogged=false]")
    sculpt("forge_crest", cx - 2, PZ1 + 1, "south", y=15)
    put(cx, E_P + 9, PZ1, "chiseled_polished_blackstone")
    put(cx, E_P + 9, PZ1 - 1, "chiseled_polished_blackstone")
    put(cx, E_P + 10, PZ1, "campfire[facing=south,lit=true,signal_fire=false,waterlogged=false]")
    for x in (cx - 2, cx + 2):                               # lanterns hung in the gate passage
        for y in range(9, E_P + 1):
            put(x, y, Z1 + 2, "chain[axis=y,waterlogged=false]")
        put(x, 8, Z1 + 2, "lantern[hanging=true,waterlogged=false]")
    for k in range((PX1 - PX0 + 2) // 2 + 1):               # the porch roof, ridged back into the nave's (the valley)
        y = E_P + 1 + k
        for z in range(PZ1 - 2, Z1 - 7, -1):
            if y < E_N + 1 + (Z1 + 1 - z):
                continue
            for x, f in ((PX0 - 1 + k, "east"), (PX1 + 1 - k, "west")):
                put(x, y, z, stairs(COPPER, f) if x != cx else COPPER)
                if k:
                    put(x, y - 1, z, COPPER)
    # the gate towers either side of the porch
    for tx in (PX0 - 1.5, PX1 + 2.5):
        forge_tower(tx, PZ1 - 0.5, 2.2, 24, cone=11, body="deepslate_bricks", band="waxed_cut_copper", every=8)
    great_furnace(cx, Z0)
    # either side of the furnace its bellows; before it the Founders' Anvil between two runs of molten metal
    sculpt("great_bellows", cx - 8, Z0 + 5, "east")
    sculpt("great_bellows", cx + 6, Z0 + 5, "west")
    for x in (cx - 4, cx + 4):
        for z in range(Z0 + 8, Z1 - 1):
            put(x, 0, z, "orange_stained_glass")
            put(x, -1, z, "lava[level=0]")
            put(x, -2, z, BLK)
            for dx in (-1, 1):
                put(x + dx, -1, z, BLK)
    put(cx - 4, -1, Z1 - 1, BLK)
    put(cx + 4, -1, Z1 - 1, BLK)
    for x in range(cx - 3, cx + 4):
        for z in range(Z0 + 8, Z0 + 13):
            put(x, 0, z, "chiseled_polished_blackstone" if abs(x - cx) == 3 and z in (Z0 + 8, Z0 + 12) else BLK)
    sculpt("master_anvil", cx - 1, Z0 + 10, "south")
    sculpt("great_hearth", NX0 + 2, Z0 + 8, "south")
    sculpt("great_hearth", NX1 - 5, Z0 + 8, "south")
    sculpt("smith_anvil", NX0 + 4, Z1 - 5, "south")
    sculpt("quench_trough", NX0 + 5, Z1 - 5, "south")
    sculpt("grindstone_wheel", NX1 - 6, Z1 - 5, "south")
    sculpt("smith_anvil", NX1 - 4, Z1 - 5, "south")
    for x, kind in ((NX0 + 2, "weapon_rack"), (NX0 + 5, "tool_wall"), (NX1 - 6, "tool_wall"), (NX1 - 3, "weapon_rack")):
        sculpt(kind, x, Z1 - 2, "north")
    for x in (NX0 + 6, NX1 - 6):                             # crucibles of molten metal hung from the trusses
        for y in range(10, E_N):
            put(x, y, Z1 - 5, "chain[axis=y,waterlogged=false]")
        put(x, 9, Z1 - 5, "lava_cauldron")
    for x, z in ((NX0 + 3, Z1 - 8), (NX1 - 3, Z1 - 8), (cx, Z1 - 3)):
        chandelier(x, z, E_N, 10)
    # the armoury (west): armour on its stands along the back, racks on the end wall, the smithing benches
    ax0, ax1, az0, az1 = X0 + 2, NX0 - 1, Z0 + 3, Z1 - 3
    for x in range(ax0 + 1, ax1 - 1, 2):
        sculpt("armour_stand", x, az0, "south")
    for z, kind in ((az0 + 1, "weapon_rack"), (az0 + 4, "weapon_rack"), (az0 + 7, "tool_wall")):
        sculpt(kind, ax0, z, "east")
    for x in range(ax0 + 4, ax0 + 7):
        put(x, 1, az0 + 5, "smithing_table")
    sculpt("smith_anvil", ax0 + 8, az0 + 5, "south")
    sculpt("grindstone_wheel", ax0 + 9, az0 + 5, "south")
    for x, st in ((ax0 + 4, "loom[facing=north]"), (ax0 + 5, "barrel[facing=up,open=false]"), (ax0 + 6, "chest[facing=north,type=single,waterlogged=false]"),
                  (ax0 + 9, "smithing_table"), (ax0 + 10, "barrel[facing=up,open=false]")):
        put(x, 1, az1, st)
    chandelier((ax0 + ax1) // 2, (az0 + az1) // 2 + 1, E_S, 8)
    for x in (ax0 + 2, ax1 - 2):                             # its fireplace stack
        put(x, 1, az0 - 1, "furnace[facing=south,lit=true]")
    for x in range(ax0 + 2, ax0 + 4):
        for z in (Z0 + 1, Z0 + 2):
            for y in range(1, E_S + 12):
                if not (z == Z0 + 2 and y == 1):
                    put(x, y, z, "bricks" if y % 6 else BLKB)
        put(x, E_S + 12, Z0 + 1, "campfire[facing=north,lit=true,signal_fire=true,waterlogged=false]")
    # the smelting hall (east): the pour from the blast towers, the crucible, ingots, the trip hammer, ore carts
    sx0, sx1, sz0, sz1 = NX1 + 1, X1 - 2, Z0 + 3, Z1 - 3
    sculpt("molten_spout", sx0 + 1, sz0, "south")
    sculpt("crucible_gantry", sx0 + 5, sz0, "south")
    for x in (sx0 + 7, sx0 + 8):
        sculpt("ingot_stack", x, sz0, "south")
    for z in range(sz0 + 1, sz1, 3):                         # the blast towers' mouths in the end wall
        put(sx1, 1, z, "blast_furnace[facing=west,lit=true]")
        put(sx1, 2, z, "bricks")
    sculpt("trip_hammer", sx0 + 1, sz1 - 3, "south")
    sculpt("ore_cart", sx1 - 3, sz0 + 3, "south")
    sculpt("ore_cart", sx1 - 3, sz0 + 7, "south")
    for z in (sz0 + 5, sz0 + 6, sz0 + 9, sz0 + 10):
        put(sx1 - 3, 1, z, "rail[shape=north_south,waterlogged=false]")
    for z, kind in ((sz0 + 2, "ore_bin"), (sz0 + 5, "coal_bin"), (sz0 + 8, "ore_bin")):
        sculpt(kind, sx1 - 1, z, "west")
    chandelier((sx0 + sx1) // 2, (sz0 + sz1) // 2, E_S, 8)
    forge_tower(X1 + 3.5, Z0 + 6.5, 3.0, 21, crown=True)
    forge_tower(X1 + 3.5, Z1 - 4.5, 3.0, 21, crown=True)
    forge_tower(X0 - 1.5, Z1 - 3.5, 2.8, 22, cone=12, body="deepslate_bricks", band="waxed_cut_copper", every=8)
    # the forecourt: setts to the street, ore and coal by the gate
    for x in range(X0 - 4, X1 + 7):
        edge = min((z for (xx, z) in road_s.cells if xx == x), default=Z1 + 6)
        for z in range(Z1 + 1, edge):
            if (x, z) not in ROAD and S.get(x, 1, z) in (None, "air"):
                FRONT.add((x, z))
    for x, z, kind in ((PX0 - 6, PZ1 + 1, "ore_bin"), (PX0 - 7, PZ1 + 1, "coal_bin"), (PX1 + 6, PZ1 + 1, "ingot_stack"),
                       (PX1 + 7, PZ1 + 1, "ore_bin")):
        sculpt(kind, x, z, "south")
    S.marks["founder"] = (cx, 1, Z1 - 3)
    put(cx + 3, 1, Z1 - 3, "ashbound:gate_forge[facing=north]")      # where the gates' drops are worked, by Wendel's hand
    S.marks["foundry_hand:1"] = (ax0 + 7, 1, az0 + 3)
    S.marks["foundry_hand:2"] = (sx0 + 6, 1, sz0 + 4)
    cold_vault()
    print("  the Ashforge at %d..%d, z %d..%d" % (X0, X1, Z0, PZ1))


def citadel():
    """Step 5: the citadel, 44 over the lower city (the Ash Warden himself is his own pass)."""
    with tier(L.TERRACE), dark_masonry():
        stair_of_champions()
    with tier(L.CITADEL), dark_masonry():
        w0, w1 = curtain_wall()
        gatehouse()
        lords_keep()
        sanctuary()
        hall_of_heroes()
        court()
        keep_garden()
        connect_fences()
    for x, y, z, st in HEADS:
        if "_stairs" not in (S.B.get((x, y, z)) or ""):
            put(x, y, z, st)
            for yy in (y + 1, y + 2):
                if K._base(S.B.get((x, yy, z)) or "air"):
                    put(x, yy, z, "air")
        print("  the citadel: wall %d..%d, water gate %s..%s" % (min(LIP), max(LIP), w0, w1))


# ================================================================ the sculpted props

SCULPT = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "renders", "sculpt_pieces.json")))
QTURN = {"north": 0, "east": 1, "south": 2, "west": 3}


def sculpt(name, x0, z0, facing="north", y=1):
    """A sculpted prop (tools/sculpt.py) stood with its footprint's north-west corner at x0, z0 once turned, its foot
    on y, its front looking `facing`. Returns the footprint (x0, z0, x1, z1)."""
    info = SCULPT[name]
    q = QTURN[facing]
    w, h, d = info["size"]

    def turn(x, z):
        for _ in range(q):
            x, z = -z - 1, x
        return x, z
    ends = [turn(0, 0), turn(w - 1, d - 1)]
    mx, mz = min(e[0] for e in ends), min(e[1] for e in ends)
    for cx, cy, cz, idx in info["pieces"]:
        x, z = turn(cx, cz)
        put(x0 + x - mx, y + cy, z0 + z - mz, "ashbound:%s[facing=%s,piece=%d]" % (name, facing, idx))
    W, D = (w, d) if q % 2 == 0 else (d, w)
    return x0, z0, x0 + W - 1, z0 + D - 1


def shop_sign(F, trade, lx, y, lz):
    """A shop's trade sign (tools/blender/civic_sculpt.py) hung out over the street from its jetty, lx, y, lz being
    the cell by the wall in the house's own coordinates."""
    a, b = F.world(lx, y, lz), F.world(lx, y, lz + 1)
    sculpt("sign_" + trade, min(a[0], b[0]), min(a[2], b[2]), F.face, y)


H.SHOP_SIGN = shop_sign

# the Arcanum's masonry: the guild's stone in warm limestone, its slate in deep blue tile
ARC_MAP = {"ashbound:slate_shingles": "ashbound:blue_roof_tiles", "ashbound:slate_shingle_stairs": "ashbound:blue_roof_tile_stairs",
           "ashbound:slate_shingle_slab": "ashbound:blue_roof_tile_slab", "deepslate_tiles": "ashbound:blue_roof_tiles"}


def arcane(st, y):
    if not st:
        return st
    name, _, props = st.partition("[")
    if name == "stone_bricks" and y > 0:
        return pick(("ashbound:limestone_bricks", 16), ("ashbound:cracked_limestone_bricks", 1), ("ashbound:mossy_limestone_bricks", 1))
    if name in ARC_MAP:
        return ARC_MAP[name] + ("[" + props if props else "")
    return st


class Arcane:
    def __init__(self, S):
        self.S = S

    def __getattr__(self, k):
        return getattr(self.S, k)

    def put(self, x, y, z, st, nbt=None):
        self.S.put(x, y, z, arcane(st, y), nbt)

    def get(self, x, y, z):
        return self.S.get(x, y, z)


class arcane_masonry:
    def __enter__(self):
        global S, put
        self.saved = S, put
        S = Arcane(S)
        put = S.put

    def __exit__(self, *a):
        global S, put
        S, put = self.saved


# ================================================================ the Arcanum: the mages' college and its Spire

AZ = -66                              # the college's axis, west to east: the gate, the court, the Spire Gate, the Spire
ARC_GATE = (88, 97)                   # the gatehouse: x at its outer face, x at its inner (the court's west side)
ARC_HALL = (98, -80, 152, -72)        # the Hall of Lectures, the court's north range: x0, z at its back, x1, z at its front
ARC_GARTH = (98, -71, 152, -61)       # the Great Court
ARC_LIB = (98, -60, 152, -53)         # the south range on the lake: x0, z at its front (the court), x1, z at its back
ARC_PARTS = (124, 138)                # its partitions: the Novices' Hall west, the library, the alchemists east
ARC_DOORS = (111, 135, 145)           # the south range's three doors
ARC_EAST = 153                        # the court's east wall, the Spire Gate in it
ARC_TOWER = (182, AZ)                 # the Spire's axis
ARC_YARD = (158, -50, 186, -34)       # the practice yard, south of the Spire's walk
ARC_GREEN = (190, -50, 202, -40)      # the herb house
GATE_Z = AZ
PURPLE = "purple_stained_glass_pane"


def arc_floor(x, z):
    return PL if (x + z) % 6 == 0 else FLAG


def hall_of_lectures():
    """The court's north range: the great lecture hall, its spire on the ridge, the master's dais at the east end, a
    summoning circle before it, pews down the hall."""
    X0, Z0, X1, Z1 = ARC_HALL
    cx, cz = (X0 + X1) // 2, (Z0 + Z1) // 2
    ground_works(X0, Z0, X1, Z1, 24, margin=1)
    for x in range(X0 - 1, X1 + 2):                     # the bank cut behind it made good: solid to the terrace's top
        g = max(GROUND(x, Z0 - 1), GROUND(x, Z0 - 2))
        if g > 0:
            for y in range(1, g):
                put(x, y, Z0 - 1, BODY)
            put(x, g, Z0 - 1, PL)
    with arcane_masonry():
        ridge = gothic_hall(X0, Z0, X1, Z1, 14, list(range(X0 + 4, X1 - 2, 6)), deep=2, pinnacles=True)
        portal("x", cx, Z1, Z1 - 1, w=2, h=7)
        spire(cx, cz, ridge - 1, r=3.4, h=20, lucarnes=False)
    for x in range(X0 + 2, X1 - 1):
        for z in range(Z0 + 2, Z1 - 1):
            put(x, 0, z, arc_floor(x, z))
    trusses(X0, Z0, X1, Z1, 14, range(X0 + 7, X1 - 3, 6))
    for x in range(X1 - 7, X1 - 1):                     # the dais
        for z in range(Z0 + 2, Z1 - 1):
            put(x, 1, z, "polished_andesite" if x > X1 - 7 else stairs("polished_andesite", "east"))
    sculpt("arcane_lectern", X1 - 4, cz, "west", y=2)
    sculpt("scroll_shelf", X1 - 2, Z0 + 2, "west", y=2)
    sculpt("scroll_shelf", X1 - 2, Z1 - 3, "west", y=2)
    sculpt("celestial_globe", X1 - 3, Z0 + 2, "west", y=2)
    sculpt("arcane_brazier", X1 - 6, Z0 + 2, "west", y=2)
    sculpt("arcane_brazier", X1 - 6, Z1 - 2, "west", y=2)
    sculpt("rune_circle", X1 - 13, cz - 2, "west")
    # the class: rows of desks with a chair behind each, all facing the master's dais, an aisle down the middle
    # and a cross aisle at the door; the slate board high on the end wall over the shelves, the master's desk
    for x in range(X1 - 16, X0 + 3, -3):
        if abs(x - cx) <= 2 or abs(x - 1 - cx) <= 2:
            continue
        for z in range(Z0 + 2, Z1 - 1):
            if z != cz:
                sculpt("school_desk", x, z, "east")
                sculpt("school_chair", x - 1, z, "east")
    sculpt("rune_board", X1 - 2, cz - 1, "west", y=5)
    sculpt("master_desk", X1 - 6, cz - 1, "west", y=2)
    for x in range(X0 + 9, X1 - 8, 12):
        chandelier(x, cz, 14, 10)
    sculpt("scroll_shelf", X0 + 2, Z0 + 2, "east")
    sculpt("scroll_shelf", X0 + 2, Z1 - 3, "east")
    S.marks["arcanum_lecturer"] = (X1 - 5, 2, cz + 1)


def south_range():
    """The range along the lake: the Novices' Hall where every new student sleeps (beds, chests, the registrar's desk),
    the library with the enchanting lectern ringed by shelves, the alchemists' benches and stills."""
    X0, Z0, X1, Z1 = ARC_LIB
    P1, P2 = ARC_PARTS
    ground_works(X0, Z0, X1, Z1, 20, margin=1)
    with arcane_masonry():
        gothic_hall(X0, Z0, X1, Z1, 12, list(range(X0 + 4, X1 - 2, 6)), deep=1, pinnacles=True)
        for x in ARC_DOORS:
            portal("x", x, Z0, Z0 + 1, w=1, h=5)
        for px, door in ((P1, None), (P2, None)):
            for z in range(Z0 + 2, Z1 - 1):
                for y in range(1, 12):
                    put(px, y, z, "air" if z in (Z0 + 2, Z0 + 3) and y <= 3 else "stone_bricks")
    iz0, iz1 = Z0 + 2, Z1 - 2
    for x in range(X0 + 2, X1 - 1):
        for z in range(iz0, iz1 + 1):
            put(x, 0, z, arc_floor(x, z))
    trusses(X0, Z0, X1, Z1, 12, range(X0 + 6, X1 - 3, 6))
    # the Novices' Hall: a bed for each new student along the lake wall, a chest at each, a runner down the middle
    for k, x in enumerate(range(X0 + 3, P1 - 1, 2)):
        put(x, 1, iz1, "purple_bed[facing=south,occupied=false,part=head]")
        put(x, 1, iz1 - 1, "purple_bed[facing=south,occupied=false,part=foot]")
        put(x + 1, 1, iz1, "chest[facing=north,type=single,waterlogged=false]")
        put(x + 1, 2, iz1, "candle[candles=1,lit=true,waterlogged=false]" if k % 2 else "air")
    for x in range(X0 + 2, P1):
        put(x, 1, iz0, "purple_carpet" if x not in (ARC_DOORS[0] - 1, ARC_DOORS[0], ARC_DOORS[0] + 1) else "air")
    sculpt("arcane_lectern", ARC_DOORS[0] + 3, iz0, "north")
    sculpt("scroll_shelf", X0 + 2, iz1 - 2, "east")
    sculpt("arcane_brazier", P1 - 1, iz0)
    for x in range(X0 + 6, P1 - 2, 9):
        chandelier(x, (iz0 + iz1) // 2, 12, 8)
    S.marks["arcanum_start"] = (ARC_DOORS[0], 1, iz0 + 1)
    S.marks["novice_master"] = (ARC_DOORS[0] + 3, 1, iz0 + 1)
    # the library: the enchanting lectern with its shelves round it, open to the door
    lx, lz = ARC_DOORS[1], iz0 + 1
    sculpt("arcane_lectern", lx, lz, "north")
    for dx in range(-2, 3):
        for dz in (0, 1, 2):
            if (abs(dx) == 2 or dz == 2) and lz + dz <= iz1:
                for y in (1, 2):
                    put(lx + dx, y, lz + dz, "bookshelf")
    for x in (P1 + 1, P1 + 4):
        sculpt("scroll_shelf", x, iz1, "north")
    chandelier(lx, lz, 12, 8)
    S.marks["arcanum_librarian"] = (lx + 3, 1, iz0)
    # the alchemists: benches with their stills, a brewing stand, potion shelves, a pylon of the Art
    ax = ARC_DOORS[2]
    sculpt("alchemy_table", ax - 4, iz1, "north")
    sculpt("alchemy_table", ax + 3, iz1, "north")
    sculpt("crystal_pylon", X1 - 2, iz0)
    for x in (P2 + 1, P2 + 2):
        put(x, 1, iz1, "ashbound:potion_shelf[facing=north]")
        put(x, 2, iz1, "ashbound:potion_shelf[facing=north]")
    put(ax - 1, 1, iz1, "brewing_stand[has_bottle_0=true,has_bottle_1=false,has_bottle_2=true]")
    put(ax + 1, 1, iz1, "cauldron")
    chandelier(ax, (iz0 + iz1) // 2, 12, 8)
    S.marks["arcanum_alchemist"] = (ax, 1, iz0 + 1)


def college_gate():
    """The college's gate where Arcanum Way comes off the bridge: a tall square gatehouse, a vaulted gate hall through
    it, a lancet over each arch, purple banners, two round towers on its outer corners with blue cones."""
    G0, G1 = ARC_GATE
    Z0, Z1 = ARC_GARTH[1], ARC_GARTH[3]
    top = 15
    ground_works(G0, Z0, G1, Z1, top + 2, margin=1)
    with arcane_masonry():
        for x in range(G0, G1 + 1):
            for z in range(Z0, Z1 + 1):
                wall = x - G0 < 2 or G1 - x < 2 or z - Z0 < 2 or Z1 - z < 2
                put(x, 0, z, FLAG)
                for y in range(1, top + 1):
                    put(x, y, z, wall_stone(y, quoin=(x in (G0, G1) and z in (Z0, Z1))) if wall else
                        ("air" if y < top else PL))
                corner = x in (G0, G1) or z in (Z0, Z1)
                if corner:
                    put(x, top + 1, z, PL if (x + z) % 2 == 0 else "air")
        for o, i in ((G0, G0 + 1), (G1, G1 - 1)):
            portal("z", AZ, o, i, w=1, h=7)
            window("z", AZ, o, i, 10, 12, "west" if o == G0 else "east")
        for z in (AZ - 3, AZ + 3):
            for x in (G0 - 1, G1 + 1):
                put(x, 8, z, "purple_wall_banner[facing=%s]" % ("west" if x < G0 else "east"))
                put(x, 5, z, "ashbound:wall_lantern[facing=%s]" % ("west" if x < G0 else "east"))
        for z in (Z0 - 0.5, Z1 + 1.5):
            turret(G0 + 0.5, z, 1, top + 5, r=2.8, cone=12, mat="ashbound:blue_roof_tiles")
    for x in range(G0 + 2, G1 - 1):                     # the gate hall: flagged, a lantern hung from its vault
        for z in range(Z0 + 2, Z1 - 1):
            put(x, 0, z, arc_floor(x, z))
    chandelier((G0 + G1) // 2, AZ, top - 1, 9)
    for x in (G0 + 3, G1 - 3):
        seat(x, AZ - 3, x, AZ)
        seat(x, AZ + 3, x, AZ)
    S.marks["arcanum_porter"] = (G0 + 4, 1, AZ - 2)


def spire_gate():
    """The court's east wall, the Spire Gate through it on the axis, a turret at each end with a blue cone."""
    x0 = ARC_EAST
    Z0, Z1 = ARC_GARTH[1], ARC_GARTH[3]
    with arcane_masonry():
        for x in (x0, x0 + 1):
            for z in range(Z0, Z1 + 1):
                put(x, 0, z, FLAG)
                for y in range(1, 10):
                    put(x, y, z, wall_stone(y))
                put(x, 10, z, PL if z % 2 == 0 else "air")
        portal("z", AZ, x0 + 1, x0, w=1, h=5)
        for z in (Z0 - 0.5, Z1 + 1.5):
            turret(x0 + 2.5, z, 1, 15, r=2.2, cone=10, mat="ashbound:blue_roof_tiles")
    for z in (AZ - 2, AZ + 2):
        put(x0 + 2, 4, z, "ashbound:wall_lantern[facing=east]")
        put(x0 - 1, 4, z, "ashbound:wall_lantern[facing=west]")


def garth():
    """The Great Court: flagged walks on the axis and to every door, the circle where first-years learn the sigils
    in the middle with a crystal pylon at each corner, beds of flowers, little blossom trees, benches round the
    circle, lamps in pairs down the axis."""
    gx0, gz0, gx1, gz1 = ARC_GARTH
    cx, cz = (ARC_HALL[0] + ARC_HALL[2]) // 2, AZ
    doors = {cx} | set(ARC_DOORS)
    for x in range(gx0, gx1 + 1):
        for z in range(gz0, gz1 + 1):
            walk = abs(z - cz) <= 1 or z in (gz0, gz1) or any(abs(x - d) <= 1 for d in doors)
            if (x, 1, z) not in S.B:
                put(x, 0, z, FLAG if walk else "grass_block[snowy=false]")
            if not walk and (x, 1, z) not in S.B and z in (gz0 + 1, gz1 - 1):
                put(x, 1, z, ("allium", "cornflower", "lily_of_the_valley", "azure_bluet")[(x // 2) % 4])
    sculpt("rune_circle", cx - 2, cz - 2)
    for dx, dz in ((-4, -3), (4, -3), (-4, 3), (4, 3)):
        sculpt("crystal_pylon", cx + dx, cz + dz)
    for s in (-1, 1):
        seat(cx + s * 6, cz - 3, cx, cz)
        seat(cx + s * 6, cz + 3, cx, cz)
        for k in (12, 24):
            x = cx + s * k
            small_tree(x, 1, cz - 3, "cherry", 4)
            small_tree(x, 1, cz + 3, "cherry", 4)
        for k in (8, 18):
            lamp(cx + s * k, cz - 2, "x")
            lamp(cx + s * k, cz + 2, "x")


def practice_yard():
    """Where the students throw their first fires: a beaten yard, a row of warded targets, a casting circle, witch-fire
    braziers at its corners and a low wall round it, open to the Spire's walk."""
    X0, Z0, X1, Z1 = ARC_YARD
    mx = (X0 + X1) // 2
    for x in range(X0, X1 + 1):
        for z in range(Z0, Z1 + 1):
            edge = x in (X0, X1) or z in (Z0, Z1)
            put(x, 0, z, pick(("packed_mud", 3), ("coarse_dirt", 2), ("gravel", 1)) if not edge else "polished_andesite")
            put(x, -1, z, "dirt")
            for y in range(1, 6):
                if S.get(x, y, z) is None:
                    put(x, y, z, "air")
            if edge and not (z == Z0 and abs(x - mx) <= 1):
                put(x, 1, z, "ashbound:pale_limestone_wall")
    for z in range(Z0 + 3, Z1 - 2, 4):
        sculpt("rune_target", X1 - 2, z, "west")
    sculpt("rune_circle", X0 + 4, (Z0 + Z1) // 2 - 2)
    for x, z in ((X0 + 1, Z0 + 1), (X1 - 1, Z0 + 1), (X0 + 1, Z1 - 1), (X1 - 1, Z1 - 1)):
        sculpt("arcane_brazier", x, z)
    for z in range(Z0 + 4, Z1 - 3, 5):
        seat(X0 + 1, z, X1, z)
    S.marks["mage_trainer:black"] = (X1 - 5, 1, Z0 + 6)
    S.marks["mage_trainer:white"] = (X0 + 7, 1, (Z0 + Z1) // 2)
    S.marks["mage_trainer:summon"] = (X1 - 5, 1, Z1 - 6)


def herb_house():
    """A glasshouse of herbs on a stone sill: beds of flowers and ferns, a channel of water, potted ferns."""
    X0, Z0, X1, Z1 = ARC_GREEN
    for x in range(X0, X1 + 1):
        for z in range(Z0, Z1 + 1):
            put(x, 0, z, FLAG)
            put(x, -1, z, "stone")
            wall = x in (X0, X1) or z in (Z0, Z1)
            for y in range(1, 6):
                if wall:
                    put(x, y, z, "polished_andesite" if y == 1 else "glass_pane" if y < 5 else "ashbound:pale_limestone_slab[type=bottom,waterlogged=false]")
                else:
                    put(x, y, z, "air")
    cz = (Z0 + Z1) // 2
    for x in range(X0 + 1, X1):
        for k in range(1, (Z1 - Z0) // 2 + 1):
            for z in (Z0 + k, Z1 - k):
                put(x, 5 + min(k, 4), z, "glass")
        put(x, 9, cz, "ashbound:pale_limestone_slab[type=bottom,waterlogged=false]")
    for x in (X0, X1):
        for z in range(Z0 + 1, Z1):
            k = min(z - Z0, Z1 - z)
            for y in range(5, 6 + min(k, 4)):
                put(x, y, z, "glass_pane")
    for x in range(X0 + 2, X1 - 1):
        for z in range(Z0 + 2, Z1 - 1):
            if z == cz:
                put(x, 0, z, WATER)
                continue
            put(x, 0, z, "grass_block[snowy=false]" if (x + z) % 5 else "moss_block")
            put(x, 1, z, pick(("fern", 3), ("allium", 1), ("blue_orchid", 1), ("azure_bluet", 1), ("lily_of_the_valley", 1),
                              ("sweet_berry_bush[age=2]", 1)))
    for x in (X0 + 1, X1 - 1):
        for z in (Z0 + 1, Z1 - 1):
            put(x, 1, z, "air")
            sculpt("bath_plant", x, z)
    for z in (cz - 1, cz, cz + 1):
        for y in (1, 2, 3):
            put(X0, y, z, "air")
    put(X0 + 1, 1, cz, FLAG)
    S.marks["arcanum_herbalist"] = (X0 + 2, 1, cz - 1)


SPIRE_TOP = 72                         # the observatory deck's floor
SPIRE_FLOORS = (0, 12, 24, 36, 48, 60)


def tower_stage(y):
    """(outer, inner) radius of the Spire's shaft at height y."""
    if y <= 24:
        return 12.4, 10.4
    if y <= 48:
        return 11.6, 9.6
    return 10.8, 8.8


def mage_tower():
    """The Spire of the Arcanum: a great pale round tower in three stages, mirror-true about its axis, gold rings at
    its setbacks, eight purple lancets on every floor, buttresses round its foot. Up its heart a stair hall: on every
    floor two straight flights of six with a landing between (a full block wide and three across, walls both sides,
    a solid ramp under the first and a soffit under the second), past the library, the alchemists' study, the orrery,
    the archmage's study and the crystal chamber to the observatory deck, the stair's head-house on the deck carrying
    a slender blue spire, the crystal crown floating at its point."""
    cx, cz = ARC_TOWER
    T = SPIRE_TOP
    LB = "ashbound:limestone_bricks"

    def d(x, z):
        return math.hypot(x - cx, z - cz)

    def wall_mat(y):
        return PL if y % 12 in (0, 1) or y <= 2 else \
            pick((LB, 14), ("ashbound:pale_limestone", 3), ("ashbound:cracked_limestone_bricks", 1))
    # the plinth, stepped, the ground cleared round it
    for x in range(cx - 16, cx + 17):
        for z in range(cz - 16, cz + 17):
            r = d(x, z)
            if r <= 15.5:
                for y in (-2, -1):
                    put(x, y, z, "stone")
                put(x, 0, z, PL if r > 14.4 or int(r) % 3 == 0 else FLAG)
                for y in range(1, 9):
                    if S.get(x, y, z) is None:
                        put(x, y, z, "air")
            if 12.4 < r <= 13.6:
                put(x, 1, z, SLAB % "ashbound:pale_limestone")
    # the shaft
    for y in range(1, T + 1):
        ro, ri = tower_stage(y)
        for x in range(cx - 13, cx + 14):
            for z in range(cz - 13, cz + 14):
                r = d(x, z)
                if ri < r <= ro:
                    put(x, y, z, "ashbound:gilded_tiles" if y in (24, 48) and r > ro - 1 else wall_mat(y))
                elif r <= ri:
                    put(x, y, z, "air")
    for y, (r0, r1) in ((25, (11.6, 12.8)), (49, (10.8, 12.0))):   # blue skirts over the setbacks
        for x in range(cx - 13, cx + 14):
            for z in range(cz - 13, cz + 14):
                if r0 < d(x, z) <= r1:
                    dx, dz = cx - x, cz - z
                    f = ("east" if dx > 0 else "west") if abs(dx) >= abs(dz) else ("south" if dz > 0 else "north")
                    put(x, y, z, stairs("ashbound:blue_roof_tile", f))
    angles = [math.pi / 8 + k * math.pi / 4 for k in range(8)]       # between the lancets
    for a in angles:                                                 # buttresses round the first stage
        for t, top in ((12.9, 20), (13.8, 14)):
            x, z = cx + round(math.cos(a) * t), cz + round(math.sin(a) * t)
            for y in range(1, top + 1):
                put(x, y, z, PLINTH if y <= 2 else LB)
            put(x, top + 1, z, SLAB % "ashbound:pale_limestone")
    for a in angles:                                                 # pale ribs up the shaft
        for y in range(21, T - 3):
            ro, ri = tower_stage(y)
            x, z = cx + round(math.cos(a) * (ro + 0.6)), cz + round(math.sin(a) * (ro + 0.6))
            if d(x, z) > ro:
                put(x, y, z, PL if y % 12 not in (0, 1) else "ashbound:carved_limestone")
    # the stair hall: its box x cx-5..cx+5, z cz-4..cz+4; flights on rows N (cz-3..cz-1) going east and rows S
    # (cz+1..cz+3) going west, the spine wall between on cz, the landing at the east end, the floor's own landing
    # at the west end inside a wide arch
    RN, RS = range(cz - 3, cz), range(cz + 1, cz + 4)
    hole = {(x, z) for x in range(cx - 2, cx + 3) for z in RS}
    box = {(x, z) for x in range(cx - 5, cx + 6) for z in range(cz - 4, cz + 5)}
    for L in SPIRE_FLOORS + (T,):                                    # floors, the deck wider
        ro, ri = tower_stage(L + 1)
        for x in range(cx - 13, cx + 14):
            for z in range(cz - 13, cz + 14):
                if d(x, z) <= ri + (2.4 if L == T else 0) and not (L and (x, z) in hole):
                    put(x, L, z, arc_floor(x, z) if L == 0 else "ashbound:limestone_flagstones")
    for L in SPIRE_FLOORS:
        top = L + 12
        for (x, z) in box:
            edge = x == cx + 5 or z in (cz - 4, cz + 4)
            spine = z == cz and cx - 3 <= x <= cx + 2
            west = x == cx - 5
            for y in range(L + 1, top):
                if edge or spine:
                    put(x, y, z, PL if y in (L + 1, top - 1) else LB)
                elif west:
                    open_ = abs(z - cz) <= 3 and y <= L + 4
                    put(x, y, z, "air" if open_ else PL if y == L + 5 else LB)
        for z in (cz - 3, cz + 3):                                   # the arch's shoulders
            put(cx - 5, L + 4, z, stairs("ashbound:pale_limestone", "north" if z < cz else "south", "top"))
        for k in range(6):                                           # the first flight, on its solid ramp
            x, y = cx - 3 + k, L + 1 + k
            for z in RN:
                for yy in range(L + 1, y):
                    put(x, yy, z, LB)
                put(x, y, z, stairs("ashbound:pale_limestone", "east"))
                for yy in range(y + 1, y + 4):
                    put(x, yy, z, "air")
        for x in (cx + 3, cx + 4):                                   # the landing on its pier
            for z in range(cz - 3, cz + 4):
                for yy in range(L + 1, L + 6):
                    put(x, yy, z, LB)
                put(x, L + 6, z, PL)
                for yy in range(L + 7, L + 10):
                    put(x, yy, z, "air")
        for k in range(6):                                           # the second flight, a soffit under it
            x, y = cx + 2 - k, L + 7 + k
            for z in RS:
                put(x, y, z, stairs("ashbound:pale_limestone", "west"))
                put(x, y - 1, z, stairs("ashbound:pale_limestone", "east", "top"))
                for yy in range(y + 1, y + 4):
                    put(x, yy, z, "air")
        put(cx + 4, L + 9, cz, LIGHT)                                # light in the stair hall
        put(cx - 4, L + 3, cz, LIGHT)
        for x, z, f in ((cx, cz - 5, "north"), (cx, cz + 5, "south"), (cx + 6, cz, "east")):
            put(x, L + 4, z, "ashbound:wall_lantern[facing=%s]" % f)
        for x, z in ((cx - 7, cz - 7), (cx + 7, cz - 7), (cx - 7, cz + 7), (cx + 7, cz + 7)):
            if d(x, z) <= tower_stage(L + 1)[1] - 0.5:
                put(x, L + 6, z, LIGHT)
    # the door, west on the axis toward the Spire Gate: a tall pointed arch with a pale ring, lanterns either side
    for x in range(cx - 13, cx - 9):
        for z in range(cz - 1, cz + 2):
            for y in range(1, 7 + (z == cz)):
                put(x, y, z, "air")
    for z in range(cz - 2, cz + 3):
        for y in range(1, 9):
            if (abs(z - cz) == 2 and y <= 7) or (abs(z - cz) == 1 and y == 7) or (z == cz and y == 8):
                put(cx - 13, y, z, PL if y < 7 or z != cz else "ashbound:carved_limestone")
    put(cx - 13, 9, cz, "ashbound:carved_limestone")
    for z in (cz - 3, cz + 3):
        put(cx - 13, 5, z, "ashbound:wall_lantern[facing=west]")
    for z in range(cz - 1, cz + 2):
        put(cx - 13, 0, z, FLAG)
        put(cx - 14, 1, z, "air")
    # eight lancets on every floor, the same on every floor so the tower reads true: three lights of purple glass,
    # pale jambs, a pointed head
    for n, L in enumerate(SPIRE_FLOORS):
        ro, ri = tower_stage(L + 3)
        for k in range(8):
            a = k * math.pi / 4
            if n == 0 and k == 4:
                continue                                             # the door's side
            ux, uz = math.cos(a), math.sin(a)
            tx, tz = -uz, ux
            for t in range(int(ri) - 1, int(ro) + 2):
                for sgn in (-2, -1, 0, 1, 2):
                    x, z = cx + round(ux * (t + 0.5) + tx * sgn), cz + round(uz * (t + 0.5) + tz * sgn)
                    if not ri < d(x, z) <= ro:
                        continue
                    if abs(sgn) == 2:
                        for y in range(L + 2, L + 11):
                            put(x, y, z, PL if y < L + 10 else "ashbound:carved_limestone")
                        continue
                    for y in range(L + 3, L + 9 + (sgn == 0)):
                        put(x, y, z, PURPLE)
                    put(x, L + 2, z, PL)
                    put(x, L + 9 + (sgn == 0), z, PL)
                    put(x, L + 10 + (sgn == 0), z, "ashbound:carved_limestone" if sgn == 0 else PL)
    # the rooms, against the outer wall, the walk round the stair hall kept clear
    f0, f1, f2, f3, f4, f5 = (L + 1 for L in SPIRE_FLOORS)
    for z in (cz - 3, cz + 3):                                       # the entrance hall
        sculpt("arcane_brazier", cx - 8, z, y=f0)
    sculpt("crystal_pylon", cx, cz - 9, y=f0)
    sculpt("crystal_pylon", cx, cz + 9, y=f0)
    sculpt("scroll_shelf", cx + 9, cz - 1, "west", y=f0)
    S.marks["arcanum_tower_ground"] = (cx - 8, f0, cz - 5)
    sculpt("scroll_shelf", cx - 1, cz - 9, "south", y=f1)           # the library
    sculpt("scroll_shelf", cx - 1, cz + 9, "north", y=f1)
    sculpt("scroll_shelf", cx + 9, cz - 1, "west", y=f1)
    sculpt("arcane_lectern", cx - 7, cz - 6, "south", y=f1)
    for x in (cx - 3, cx - 1, cx + 1, cx + 3):                       # reading desks either side of the stair hall
        sculpt("school_desk", x, cz - 6, "north", y=f1)
        sculpt("school_chair", x, cz - 5, "north", y=f1)
        sculpt("school_desk", x, cz + 6, "south", y=f1)
        sculpt("school_chair", x, cz + 5, "south", y=f1)
    sculpt("arcane_brazier", cx + 6, cz + 7, y=f1)
    sculpt("alchemy_table", cx - 1, cz - 8, "south", y=f2)           # the alchemists' study
    sculpt("alchemy_table", cx - 1, cz + 8, "north", y=f2)
    sculpt("celestial_globe", cx + 8, cz, "west", y=f2)
    sculpt("crystal_pylon", cx + 6, cz - 6, y=f2)
    sculpt("crystal_pylon", cx + 6, cz + 6, y=f2)
    sculpt("arcane_orrery", cx + 6, cz - 1, "west", y=f3)            # the orrery, a lesson round it
    for x in range(cx + 6, cx + 10):
        sculpt("school_chair", x, cz - 4, "south", y=f3)
        sculpt("school_chair", x, cz + 4, "north", y=f3)
    sculpt("master_desk", cx + 9, cz - 1, "west", y=f3)
    sculpt("arcane_brazier", cx, cz - 8, y=f3)
    sculpt("arcane_brazier", cx, cz + 8, y=f3)
    sculpt("arcane_lectern", cx + 7, cz, "west", y=f4)               # the archmage's study
    sculpt("scroll_shelf", cx - 1, cz - 8, "south", y=f4)
    sculpt("scroll_shelf", cx - 1, cz + 8, "north", y=f4)
    sculpt("arcane_brazier", cx + 5, cz - 6, y=f4)
    sculpt("arcane_brazier", cx + 5, cz + 6, y=f4)
    S.marks["archmage"] = (cx + 6, f4, cz + 2)
    for x, z in ((cx + 5, cz - 6), (cx + 5, cz + 6), (cx - 6, cz - 6), (cx - 6, cz + 6)):
        sculpt("crystal_pylon", x, z, y=f5)                          # the crystal chamber
    # the deck: corbelled out, a crenellated parapet, four turrets on its rim
    def inward(x, z):
        dx, dz = cx - x, cz - z
        return ("east" if dx > 0 else "west") if abs(dx) >= abs(dz) else ("south" if dz > 0 else "north")
    for y in range(T - 3, T + 1):
        ro = 10.8 + (y - (T - 3)) * 0.47
        for x in range(cx - 14, cx + 15):
            for z in range(cz - 14, cz + 15):
                r = d(x, z)
                if 10.6 < r <= ro:
                    put(x, y, z, stairs("ashbound:pale_limestone", inward(x, z), "top") if y < T and r > ro - 0.7 else PL)
    for x in range(cx - 14, cx + 15):
        for z in range(cz - 14, cz + 15):
            r = d(x, z)
            if 11.4 < r <= 12.2:
                put(x, T + 1, z, PL)
                if (round(math.degrees(math.atan2(z - cz, x - cx))) // 12) % 2 == 0:
                    put(x, T + 2, z, "ashbound:pale_limestone_wall")
    with arcane_masonry():
        for sx in (-1, 1):
            for sz in (-1, 1):
                turret(cx + sx * 8 + 0.5, cz + sz * 8 + 0.5, T - 2, T + 6, r=2.0, cone=9, mat="ashbound:blue_roof_tiles")
    # the stair's head-house on the deck, its door west, the spire standing on it
    for (x, z) in box:
        edge = x in (cx - 5, cx + 5) or z in (cz - 4, cz + 4)
        for y in range(T + 1, T + 7):
            if edge:
                door = x == cx - 5 and abs(z - cz) <= 1 and y <= T + 3
                put(x, y, z, "air" if door else PL if y in (T + 1, T + 6) else LB)
            elif z == cz and cx - 3 <= x <= cx + 2:
                put(x, y, z, LB)
        put(x, T + 7, z, PL)
    for z in RS:                                                     # a rail at the stair's head
        put(cx + 3, T + 1, z, "ashbound:pale_limestone_wall")
    put(cx - 6, T + 4, cz - 2, "ashbound:wall_lantern[facing=west]")
    put(cx - 6, T + 4, cz + 2, "ashbound:wall_lantern[facing=west]")
    # the spire, banded in gilt, its steps eased with stairs, a gilt needle at its point
    base, H_ = T + 8, 34
    rad = [max(0.6, 4.4 * (1 - k / H_) ** 1.2 + 0.2) for k in range(H_ + 1)]
    for k in range(H_):
        for x in range(cx - 5, cx + 6):
            for z in range(cz - 5, cz + 6):
                r = d(x, z)
                if r <= rad[k] and (r > rad[k] - 1.4 or k == 0):
                    put(x, base + k, z, "ashbound:gilded_tiles" if k in (6, 16, 25) or k >= H_ - 2 else "ashbound:blue_roof_tiles")
        if k + 1 < H_:
            for x in range(cx - 5, cx + 6):
                for z in range(cz - 5, cz + 6):
                    r = d(x, z)
                    if rad[k + 1] < r <= rad[k] and r > rad[k] - 1.4:
                        put(x, base + k + 1, z, stairs("ashbound:blue_roof_tile", inward(x, z)))
    tip = base + H_
    put(cx, tip, cz, "ashbound:gilded_tiles")
    put(cx, tip + 1, cz, "end_rod[facing=up]")
    sculpt("crystal_crown", cx - 3, cz - 3, y=tip + 3)
    sculpt("brass_telescope", cx + 7, cz - 1, "east", y=T + 1)
    sculpt("celestial_globe", cx, cz - 8, "south", y=T + 1)
    print("  the Spire of the Arcanum: deck at %d, crown at %d" % (T, tip + 3))


def arcanum_paths():
    """The walk from the Spire Gate to the Spire's door on the axis, lamps in pairs, crystal pylons at its ends; a
    branch south to the practice yard, another round to the herb house."""
    cx, cz = ARC_TOWER
    door = cx - 13
    for x in range(ARC_EAST + 2, door):
        for z in range(AZ - 2, AZ + 3):
            put(x, 0, z, PL if abs(z - AZ) == 2 else FLAG)
    for x in (ARC_EAST + 5, door - 3):
        lamp(x, AZ - 3, "z")
        lamp(x, AZ + 3, "z")
    mx = (ARC_YARD[0] + ARC_YARD[2]) // 2
    for z in range(AZ + 3, ARC_YARD[1]):
        for x in (mx - 1, mx, mx + 1):
            put(x, 0, z, FLAG)
    gz = (ARC_GREEN[1] + ARC_GREEN[3]) // 2
    for x in range(ARC_YARD[2] + 1, ARC_GREEN[0]):
        for z in (gz - 1, gz, gz + 1):
            put(x, 0, z, FLAG)
    # Arcanum Way's last stretch off the bridge to the gate, flagged
    for x in range(ARC_GATE[0] - 6, ARC_GATE[0]):
        for z in range(AZ - 2, AZ + 3):
            put(x, 0, z, FLAG)


def arcanum_lawn():
    """Blossom trees along the Spire's walk and the lawn between the court and the yard, flowers under them."""
    for i, (x, z) in enumerate(((160, AZ - 8), (166, AZ - 8), (160, AZ + 8), (166, AZ + 8),
                                      (154, -46), (199, -58), (199, -74))):
        if any(S.get(x, y, z) not in (None, "air") for y in (1, 2)):
            continue
        small_tree(x, 1, z, ("cherry", "birch")[i % 2], 5)
        for dx, dz in ((2, 0), (-2, 0), (0, 2), (0, -2), (1, 1), (-1, -1)):
            if (x + dx, 1, z + dz) not in S.B:
                put(x + dx, 1, z + dz, ("allium", "cornflower", "lily_of_the_valley", "azure_bluet")[(dx * 3 + dz + i) % 4])


def arcanum(R):
    """Step 7: the Arcanum on the lake's north shore across the river, where new students arrive: Arcanum Way off its
    bridge into the gatehouse, the Great Court between the Hall of Lectures and the range on the lake (the Novices'
    Hall, the library, the alchemists), the Spire Gate, the walk to the Spire, the practice yard and the herb house."""
    bridge_over(R["arcane"])
    college_gate()
    hall_of_lectures()
    south_range()
    spire_gate()
    garth()
    mage_tower()
    practice_yard()
    herb_house()
    arcanum_paths()
    arcanum_lawn()
    X0, Z0 = ARC_GATE[0] - 7, ARC_HALL[1] - 1                  # no houses anywhere in the college's grounds
    for x in range(X0, ARC_GREEN[2] + 3):
        for z in range(Z0, ARC_YARD[3] + 3):
            CLAIM.add((x, z))
    print("  the Arcanum: gate at x %d, Spire at %d, %d" % (ARC_GATE[0], *ARC_TOWER))
    return 0


# ================================================================ Hornsend, the outcast quarter

HORN_YARD = (-158, 41)                # the Soup Yard's well
HORN_YARD_R = 8
HORN_MIX = (("cottage", 5), ("house", 3))


def horn_gate(x, z):
    """Where Ash Row leaves Hearth Ward: two squat pillars and a lintel across the lane, a pair of horns on it in
    the quarter's own stone. No gates hung: the city never gave them any."""
    st = "ashbound:duskstone_bricks"
    for s_ in (-1, 1):
        for dz in (3, 4):
            for y in range(1, 7):
                put(x, y, z + s_ * dz, "ashbound:duskstone_quoin" if y % 2 else st)
                put(x + 1, y, z + s_ * dz, st)
    for dz in range(-4, 5):
        for dx in (0, 1):
            put(x + dx, 7, z + dz, st)
            put(x + dx, 8, z + dz, "ashbound:duskstone_brick_slab[type=bottom,waterlogged=false]")
    for s_ in (-1, 1):                    # the horns: out past the lintel's ends and curving up, every block on the last
        for dx in (0, 1):
            for dz, y in ((4, 8), (5, 8), (5, 7), (6, 8), (6, 9), (7, 9), (7, 10), (7, 11), (7, 12), (6, 12), (6, 13)):
                if dx == 0 or y < 11:
                    put(x + dx, y, z + s_ * dz, st)
    put(x, 6, z, "soul_lantern[hanging=true,waterlogged=false]")
    # the stones the city threw: a low wall of them either side of the gate, and they're proud of it
    for s_ in (-1, 1):
        for dz in range(5, 13):
            if open_ground(x, z + s_ * dz) and (x, z + s_ * dz) not in ROAD:
                put(x, 1, z + s_ * dz, "ashbound:cracked_duskstone_bricks" if dz % 3 == 0 else st)
                if dz % 4:
                    put(x, 2, z + s_ * dz, "ashbound:duskstone_brick_wall[east=none,north=none,south=none,up=true,waterlogged=false,west=none]")


def hornsend(R):
    """Three streets the city forgot it owned: dark low houses shoulder to shoulder, the Soup Yard with its well and
    long tables, soul-flame lamps, the Finder's door and the tinker's stall."""
    cx, cz = HORN_YARD
    well(cx, cz)
    for dx, dz in ((-5, -4), (5, -4), (-5, 4), (5, 4)):
        outdoor_table(cx + dx, cz + dz)
    # the soup: a great pot over the embers, its cook behind it, and the tinker's anvil across the yard
    put(cx - 2, 1, cz + 6, "campfire[facing=north,lit=true,signal_fire=false,waterlogged=false]")
    put(cx - 2, 2, cz + 6, "water_cauldron[level=3]")
    put(cx - 1, 1, cz + 6, "barrel[facing=up,open=false]")
    put(cx - 3, 1, cz + 6, "barrel[facing=up,open=false]")
    put(cx + 3, 1, cz - 6, "anvil[facing=east]")
    put(cx + 4, 1, cz - 6, "barrel[facing=up,open=false]")
    S.marks["horn_cook"] = (cx - 2, 1, cz + 4)
    S.marks["horn_cook:2"] = (cx + 6, 1, cz)
    S.marks["horn_tinker"] = (cx + 3, 1, cz - 4)
    S.marks["horn_elder"] = (cx - 3, 1, cz - 2)
    S.marks["horn_fence"] = (-196, 1, 36)
    horn_gate(-127, 40)
    n = 0
    for side in "ns":
        n += frontage(R["ash"], side, HORN_MIX, alley=0.25, step=4, yards=(4, 8), eaves=0)
    for r in ("stepdown", "hornlane"):
        for side in "we":
            n += frontage(R[r], side, HORN_MIX, alley=0.25, step=4, yards=(4, 8), eaves=0)
    print("  Hornsend: %d houses" % n)
    return n


def hornsend_lamps():
    """The city's lamps burn soul-blue down here: nobody's paid for the oil, and this burns on anything."""
    n = 0
    for k, st in list(S.B.items()):
        if st.startswith("lantern") and in_hornsend(k[0], k[2]):
            S.B[k] = "soul_" + st
            n += 1
    print("  Hornsend: %d lamps" % n)


# ================================================================ the plan

def plan():
    """The streets (x east, z south; the gate's passage ends at z 173)."""
    ROADS.clear()
    ROAD.clear()
    R = {}
    R["high"] = add_road("High Street", "main", [(0, 175), (0, 163), (-3, 151), (-8, 139), (-13, 128)],
                         [17, 13, 10, 9, 10], gutter=True)
    R["market"] = add_road("the market", "market", [(-13, 130), (-19, 117), (-27, 103), (-30, 90), (-29, 78), (-25, 67)],
                           [10, 22, 36, 42, 30, 11])
    R["north"] = add_road("North Street", "main", [(-25, 68), (-22, 56), (-17, 43), (-13, 30)], [10, 9, 9, 9], gutter=True)
    R["lane"] = add_road("Market Lane", "lane", [(-47, 97), (-70, 100), (-95, 96), (-120, 91), (-150, 95), (-178, 100)],
                         [7, 6, 6, 6, 6, 6])
    R["lake"] = add_road("Lake Lane", "lane", [(-10, 84), (2, 80), (16, 74)], [6, 5, 5])
    R["row_w"] = add_road("Gate Row", "lane", [(-6, 151), (-30, 155), (-60, 152), (-90, 144), (-118, 133)], [6, 5, 5, 5, 5])
    R["row_e"] = add_road("Gate Row East", "lane", [(5, 150), (30, 146), (58, 138), (86, 127)], [6, 5, 5, 5])
    # step 2
    cx, cz = GREEN
    R["green"] = add_road("the green", "green", [(cx, cz), (cx, cz)], [2 * GREEN_R + 1] * 2)
    R["cooper_n"] = add_road("Cooper's Lane", "lane", [(-97, 98), (-99, 106), (cx, cz - GREEN_R + 1)], [5, 5, 5])
    R["cooper_s"] = add_road("Cooper's Lane south", "lane", [(cx, cz + GREEN_R - 1), (-97, 136), (-93, 143)], [5, 5, 5])
    R["back"] = add_road("Back Lane", "alley", [(cx + GREEN_R - 1, cz + 2), (-78, 126), (-60, 125), (-44, 120), (-33, 117)],
                         [3, 3, 3, 3, 3])
    R["wall"] = add_road("Wall Lane", "lane", [(-24, 52), (-50, 48), (-80, 52), (-110, 57), (-140, 65), (-170, 78)],
                         [6, 6, 5, 5, 5, 5])
    R["chapel"] = add_road("Chapel Lane", "lane", [(-121, 93), (-118, 80), (-113, 66), (-110, 57)], [5, 5, 5, 5])
    R["mill"] = add_road("Mill Lane", "lane", [(16, 76), (28, 92), (44, 108), (55, 124), (58, 138)], [5, 5, 5, 5, 5])
    # step 3
    R["shore"] = add_road("Fishers' Row", "lane", [(40, 106), (56, 103)] + [(x, shore_z(x) + 4) for x in (72, 94, 116, 134)]
                          + [(143, 101)], [5] * 7)
    # step 4: up from the market's north end to the foot of the guild terrace's grand stair
    R["stair"] = add_road("Stair Street", "main", [(-13, 31), (-21, 8), (-18, -18), (-9, -42), (0, -58), (0, -63)],
                          [9, 10, 10, 11, 14, 15], gutter=True)
    # step 6: the Forge Ward along Forge Street under the bank, the Hearth Ward round its square, the dyers east
    hx, hz = HEARTH
    R["forge"] = add_road("Forge Street", "main", [(-19, -14), (-45, -24), (-80, -30), (-115, -36), (-150, -44), (-184, -54)],
                          [9, 8, 8, 8, 7, 6], gutter=True)
    R["underbank"] = add_road("Under-Bank Lane", "lane", [(x, round(L.z_terrace(x)) + 3) for x in (-54, -80, -108, -136, -165, -194)],
                              [5] * 6)
    R["hsq"] = add_road("the Hearth Square", "hearth", [(hx, hz), (hx, hz)], [2 * HEARTH_R + 1] * 2)
    R["bellows"] = add_road("Bellows Lane", "lane", [(hx + 9, hz - 8), (-106, -20), (-104, -32)], [5, 5, 5])
    R["hearth"] = add_road("Hearth Lane", "lane", [(hx + 2, hz + 10), (-112, 35), (-110, 55)], [5, 5, 5])
    R["ember"] = add_road("Ember Row", "lane", [(hx + 10, hz + 2), (-80, 4), (-52, 6), (-24, 8)], [5, 5, 5, 5])
    R["tanners"] = add_road("Tanners' Lane", "lane", [(hx - 10, hz), (-160, -2), (-198, -8)], [5, 5, 5])
    R["dyers"] = add_road("Dyers' Walk", "lane", [(6, -59), (34, -60), (64, -60)], [4, 4, 4])
    # Hornsend, the outcast quarter: Ash Row off Hearth Lane under the west wall, the Soup Yard halfway down it, Stepdown
    # Alley to Wall Lane, Horn Lane up to the tanners
    hy = HORN_YARD
    R["ash"] = add_road("Ash Row", "lane", [(-112, 38), (-128, 40), (-145, 41), hy, (-172, 38), (-188, 37), (-203, 35)], [5] * 7)
    R["hyard"] = add_road("the Soup Yard", "hearth", [hy, hy], [2 * HORN_YARD_R + 1] * 2)
    R["stepdown"] = add_road("Stepdown Alley", "lane", [(-172, 38), (-171, 55), (-170, 76)], [4, 4, 4])
    R["hornlane"] = add_road("Horn Lane", "lane", [(-188, 37), (-192, 20), (-197, -5)], [4, 4, 4])
    # step 7: on over the river to the Arcanum
    R["arcane"] = add_road("Arcanum Way", "lane", [(64, -60), (76, -63), (87, -66)], [4, 5, 5])
    return R


def build(ground):
    global GROUND
    GROUND = ground
    before = len(S.B)
    OWNER.clear()
    FENCES.clear()
    FRONT.clear()
    ALLEY.clear()
    CLAIM.clear()
    YARD.clear()
    LOG.clear()
    R = plan()
    # the set pieces first, so the houses fit round them
    market_dressing()
    inn_and_green(R["green"])
    lake_quarter()
    n = arcanum(R)
    n += hornsend(R)
    ROW_I[0] = 0
    for side in "wesn":
        n += frontage(R["market"], side, SHOP_MIX, alley=0.05, step=8, trades=ROW_TRADES)
    for r in ("high", "north"):
        n += frontage(R[r], "w", MAIN_MIX, alley=0.06)
        n += frontage(R[r], "e", MAIN_MIX, alley=0.06)
    for side in "ens":
        n += frontage(R["green"], side, LANE_MIX, alley=0, step=8, yards=(5, 9))
    for r in ("lane", "row_w", "row_e"):
        n += frontage(R[r], "n", LANE_MIX, alley=0.18)
        n += frontage(R[r], "s", LANE_MIX, alley=0.18)
    n += frontage(R["lake"], "n", LANE_MIX)
    n += frontage(R["lake"], "s", LANE_MIX)
    for r in ("cooper_n", "cooper_s", "chapel"):
        n += frontage(R[r], "w", LANE_MIX, alley=0.15)
        n += frontage(R[r], "e", LANE_MIX, alley=0.15)
    n += frontage(R["wall"], "n", LANE_MIX, alley=0.18)
    n += frontage(R["wall"], "s", LANE_MIX, alley=0.18)
    n += frontage(R["mill"], "w", LANE_MIX, alley=0.15, step=6)
    n += frontage(R["mill"], "e", LANE_MIX, alley=0.15, step=6)
    n += frontage(R["shore"], "s", LANE_MIX, alley=0.15, step=6)
    n += frontage(R["stair"], "w", MAIN_MIX, alley=0.1)
    n += frontage(R["stair"], "e", MAIN_MIX, alley=0.1)
    n += wards(R)
    print("  %d houses" % n)
    shoulders()
    fill_gaps()
    fill_gaps(-212, -44, -100, 40)
    pave_roads()
    connect_fences()
    terrace()
    bank_walls()
    citadel()
    import capital_heroes as HR
    HR.S = S
    HR.SCULPT = sculpt
    HR.build()
    light_streets()
    hornsend_lamps()
    print("  %d things cleared out of doorways" % H.clear_doorways(S))
    print("  %d stub panes framed" % H.frame_panes(S))
    print("city: %d blocks" % (len(S.B) - before))
