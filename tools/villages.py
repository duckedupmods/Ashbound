"""Villages: each one a PLACE, not a cluster of houses - it takes its shape from where it stands (a lake, a gorge, a
cliff, a hill, a giant tree, a mountain's face), so no two read alike. The houses are the capital's approved kit
(houses.py in E:/Ashbound/tools), rolled per village in its own colours and roofs; every village has one landmark
and stays humbler than Highmourn: no curtain walls, no spires, ~25 buildings at most.

    lake     Reedmere: cottages on stilts over a lake, boardwalks out to a round deck with the bell house
    gorge    Archford: houses packed along a stone bridge over a ravine, a mill and its wheel on the river below
    cliff    Stepcliff: terraces stepped up a rock face, stairs zigzagging, a waterfall, a hoist
    hill     Millbrae: a road winding up a round hill, fields in rings at its foot, the windmill on top
    tree     Lumenhollow (elves): rings of decks round a giant tree, bridges to the trees round it
    hold     Anvilgate (dwarfs): a carved gate in a mountain's face, the forge yard, stone houses dug into the slope

    python tools/villages.py lake [more ...]   -> E:/Ashbound/tools/renders/struct/vil_lake.obj (+ shots), then
    E:/Steam/steamapps/common/Blender/blender.exe -b -P E:/Ashbound/tools/blender/preview_struct.py -- vil_lake
x east, y up, z south; the village's ground about y = 0.
"""
import math
import os
import random
import sys

sys.path.insert(0, "E:/Ashbound/tools")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import houses as H  # noqa: E402
import structkit as K  # noqa: E402
import nbtio  # noqa: E402

TREES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../src/main/resources/data/ashbound/structure/tree")
GRASS = "grass_block[snowy=false]"
WATER = "water[level=0]"
FLAG = "ashbound:limestone_flagstones"
H.FULL.update({"ashbound:blue_roof_tile": "ashbound:blue_roof_tiles", "ashbound:green_roof_tile": "ashbound:green_roof_tiles"})
# the kit's doorway sweep matched "rose" anywhere in a name, so it took rose_plaster_timber walls out beside the doors
H.DOORWAY_JUNK = tuple(k for k in H.DOORWAY_JUNK if k != "rose") + ("rose_bush", "wither_rose")

S = None
PROPS = []      # the Blender props stood in the village: (model, x, y, z, yaw, scale) for the preview
G = {}          # (x, z) -> ground height
WET = {}        # (x, z) -> water surface over the ground
CARVED = set()  # cells emptied at or under their column's ground (rooms dug in, tunnels): air in the game, not rock
WALKS = []      # (x, y, z) cells under the rope bridges: an invisible floor in the game
DOORS = []      # (x, y, z) in front of the homes not built by a Plan (elf pods, dwarf houses): the cast's residents
PLANS = []      # every Plan made for this village: its houses' doors and its roads, for the cast


ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../src/main/resources/assets/ashbound")
VOX = "E:/Ashbound/tools/renders/vox"
YAW = {"north": 0, "west": 90, "south": 180, "east": -90}
CORNERED = {"village_bell", "mooring_post", "catch_basket"}     # built in block space at (0.5, -0.5), not round the origin
SPIN = {"windmill_sails": "ashbound:windmill_hub", "water_wheel": "ashbound:wheel_hub", "village_bell": "ashbound:bell_hook"}
# ^ the props that move in game: exported as these hub blocks (VillageSpin.java turns the model), facing the prop's front


def prop(name, x, y, z, face="north"):
    """one of village_props.py's models stood at block (x, y, z), its front turned to `face` (or a yaw in degrees)"""
    off = 0.0 if name in CORNERED else 0.5
    PROPS.append((name, x + off, y, z + off, YAW.get(face, face) if isinstance(face, str) else face, 1.0))


def sync_props():
    """the preview reads models from E:/Ashbound/tools/renders/vox (MODEL_f0.obj + .png): copy ours there"""
    import shutil
    os.makedirs(VOX, exist_ok=True)
    for name in {p[0] for p in PROPS}:
        shutil.copy(os.path.join(ASSETS, "models/mesh", name + ".obj"), os.path.join(VOX, name + "_f0.obj"))
        shutil.copy(os.path.join(ASSETS, "textures/block", name + ".png"), os.path.join(VOX, name + "_f0.png"))


import vplan  # noqa: E402
_plan_init = vplan.Plan.__init__


def _plan_kept(self, *a, **kw):
    _plan_init(self, *a, **kw)
    PLANS.append(self)


vplan.Plan.__init__ = _plan_kept


VAR = 0         # which of a kind's layouts: its own seed and land, turned VAR quarter turns (export writes KIND_VAR+1)


def new(seed):
    global S
    S = K.Build(seed + 7919 * VAR)
    PROPS.clear()
    G.clear()
    WET.clear()
    CARVED.clear()
    WALKS.clear()
    DOORS.clear()
    PLANS.clear()
    put = S.put

    def carving_put(x, y, z, b, nbt=None):
        if b is None and y <= G.get((x, z), -9999):
            CARVED.add((x, y, z))
        put(x, y, z, b, nbt)
    S.put = carving_put


def noise(x, z, s, seed=0):
    """Smooth value noise in -1..1 at scale s."""
    def h(i, j):
        n = (i * 73856093) ^ (j * 19349663) ^ ((seed + 1013 * VAR) * 83492791)
        return random.Random(n).random() * 2 - 1
    fx, fz = x / s, z / s
    i, j = math.floor(fx), math.floor(fz)
    u, v = fx - i, fz - j
    u, v = u * u * (3 - 2 * u), v * v * (3 - 2 * v)
    a, b, c, d = h(i, j), h(i + 1, j), h(i, j + 1), h(i + 1, j + 1)
    return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v


def land(x0, z0, x1, z1, hf, water=None, rock=("stone", "andesite"), bed=(("gravel", 3), ("mud", 2), ("sand", 1)),
         grass=GRASS, steep=2):
    """The ground: turf on the flats, rock where it's steep, a bed and water where it's under `water`."""
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            G[(x, z)] = int(round(hf(x, z)))
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            h = G[(x, z)]
            nb = [G.get((x + dx, z + dz), h) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            cliff = max(abs(v - h) for v in nb) >= steep
            for y in range(min(min(nb), h) - 2, h + 1):
                if y == h:
                    if water is not None and h < water:
                        st = S.pick(*bed)
                    elif cliff:
                        st = S.rnd.choice(rock)
                    else:
                        st = grass
                else:
                    st = S.rnd.choice(rock) if cliff or h - y > 2 else "dirt"
                S.put(x, y, z, st)
            if water is not None and h < water:
                WET[(x, z)] = water
                for y in range(h + 1, water + 1):
                    S.put(x, y, z, WATER)


def gh(x, z):
    return G.get((x, z), 0)


NATURAL = {"grass_block", "dirt", "coarse_dirt", "rooted_dirt", "podzol", "dirt_path", "moss_block", "stone", "andesite", "granite",
           "diorite", "tuff", "gravel", "mud", "sand", "clay", "short_grass", "tall_grass", "fern", "large_fern", "poppy", "dandelion",
           "cornflower", "oxeye_daisy", "azure_bluet", "allium", "lily_of_the_valley", "red_tulip", "orange_tulip", "white_tulip",
           "pink_tulip", "sweet_berry_bush", "pink_petals"}


def _natural(v):
    return v is not None and v.split("[")[0].split(":")[-1] in NATURAL


SOFTGROUND = {"grass_block", "dirt", "coarse_dirt", "rooted_dirt", "podzol", "dirt_path", "moss_block", "short_grass", "tall_grass",
              "fern", "large_fern", "poppy", "dandelion", "cornflower", "oxeye_daisy", "azure_bluet", "allium", "lily_of_the_valley"}


def set_ground(x, z, t):
    """move the ground's top at (x, z) to t: earth piled up under fresh turf, or cut down and re-turfed. Only ever
    earth: a column with rock in the cut, or anything built where the earth would go, is left as it is."""
    g = G[(x, z)]
    if t > g and any(S.get(x, yy, z) is not None and not _natural(S.get(x, yy, z)) for yy in range(g + 1, t + 3)):
        return
    if t < g and any(S.get(x, yy, z) is not None and S.get(x, yy, z).split("[")[0].split(":")[-1] not in SOFTGROUND
                     for yy in range(t + 1, g + 3)):
        return
    if t > g:
        for yy in range(g, t):
            S.put(x, yy, z, "dirt")
        S.put(x, t, z, GRASS)
        for yy in (t + 1, t + 2):
            if _natural(S.get(x, yy, z)):
                S.put(x, yy, z, None)
    elif t < g:
        for yy in range(t + 1, g + 3):
            if _natural(S.get(x, yy, z)):
                S.put(x, yy, z, None)
        S.put(x, t, z, GRASS)
    G[(x, z)] = t


def grade(cells, y, occ=None, reach=5):
    """the land shaped to a house whose floor is at y: level just under it, an earth bank sloping down from the sill
    so no tall footing shows, the slope above cut back off its walls"""
    cs = set(cells)
    for c in cs:
        if c in G and c not in WET:
            set_ground(c[0], c[1], y)
    ring, seen = set(cs), set(cs)
    for d in range(1, reach + 1):
        nxt = set()
        for (a, b) in ring:
            for da in (-1, 0, 1):
                for db in (-1, 0, 1):
                    q = (a + da, b + db)
                    if q not in seen:
                        seen.add(q)
                        nxt.add(q)
        ring = nxt
        for q in ring:
            if q not in G or q in WET or (occ is not None and occ.get(q) in ("house", "landmark", "focus", "field", "deck", "road",
                                                                            "path", "steps", "rail")):
                continue                                         # roads keep their own line: the land meets them, not them it
            g = G[q]
            t = min(max(g, y + 1 - d), y - 1 + d)                     # level with the floor beside it, then easing off
            if occ is not None:
                road = [G[r] for r in ((q[0] + 1, q[1]), (q[0] - 1, q[1]), (q[0], q[1] + 1), (q[0], q[1] - 1))
                        if r in G and occ.get(r) in ("road", "path")]
                if road:
                    t = max(min(t, min(road) + 1), max(road) - 1)
            if t < g and g > y + 3:
                continue                                    # a real rise behind: the house stands into it, no quarry
            if t != g:
                set_ground(q[0], q[1], t)


def lay_tree(name, x, z, y=None, k=0):
    """One of the mod's own tree templates, its trunk's foot at (x, y, z), turned k quarter turns."""
    t = nbtio.read(os.path.join(TREES, name + ".nbt"))
    import json
    off = json.load(open(os.path.join(TREES, "../../tree/offsets.json")))[name]
    pal = []
    for p in t["palette"][2]:
        n = p["Name"]
        props = {a: b for a, b in p.get("Properties", {}).items()}
        pal.append(K.fmt(K.short(n) if n.startswith("minecraft:") else n, props) if props else
                   (K.short(n) if n.startswith("minecraft:") else n))
    y = gh(x, z) + 1 if y is None else y
    for b in t["blocks"][2]:
        px, py, pz = (v.v for v in b["pos"][2])
        st = pal[b["state"].v]
        if st in ("air", "structure_void"):
            continue
        dx, dz = px - off[0], pz - off[2]
        for _ in range(k):
            dx, dz = -dz, dx
        wx, wy, wz = x + dx, y + py - off[1], z + dz
        cur = S.get(wx, wy, wz)
        if cur is None or cur == "air" or "grass" in cur and "block" not in cur:
            S.put(wx, wy, wz, H.turn_state(st, k))


def home(kind, x, z, face, y=None, base="stone", style=None, trade=None):
    """A house of the kit at footprint corner (x, z) facing `face`, its floor at y (default: the highest ground under
    it), stood on a footing ("stone"), on stilts ("stilts", down into the water) or on nothing (None).
    Returns (x0, z0, x1, z1, y)."""
    fn, w, d = H.INN if kind == "inn" else H.KINDS[kind]
    fw, fd = (w, d) if face in ("south", "north") else (d, w)
    cells = [(a, b) for a in range(x, x + fw) for b in range(z, z + fd)]
    if y is None:
        y = max(gh(a, b) for a, b in cells)
    T = K.Build()
    T.rnd = S.rnd
    kw = dict(style or {})
    if trade:
        kw["trade"] = trade
    fn(T, x, z, face, **kw)
    if base == "stone":
        grade(cells, y)
    for a, b in cells:                       # the ground inside cleared to the floor
        for yy in range(y + 1, y + 30):
            if S.get(a, yy, b) is not None:
                S.put(a, yy, b, None)
    for (bx, by, bz), st in T.B.items():
        S.put(bx, by + y, bz, st, T.nbt.get((bx, by, bz)))
    for a, b in cells:
        g = gh(a, b)
        edge = a in (x, x + fw - 1) or b in (z, z + fd - 1)
        if base == "stone":
            for yy in range(g - 1, y):
                S.put(a, yy, b, H.stone(S) if edge else "dirt")
        elif base == "stilts":
            post = (a - x) % 3 == 0 and (b - z) % 3 == 0 or (a in (x, x + fw - 1) and b in (z, z + fd - 1))
            for yy in range(g, y):
                S.put(a, yy, b, "spruce_log[axis=y]" if post else (WATER if (a, b) in WET and yy <= WET[(a, b)] else None))
    return x, z, x + fw - 1, z + fd - 1, y


def finish():
    H.clear_doorways(S)
    H.frame_panes(S)


def fence(x, y, z, wood="spruce"):
    S.put(x, y, z, "%s_fence" % wood)


def lantern_post(x, y, z, h=3, wood="spruce"):
    for k in range(h):
        S.put(x, y + k, z, "%s_fence" % wood)
    S.put(x, y + h, z, "lantern[hanging=false,waterlogged=false]")


def scatter(n, x0, z0, x1, z1, what, clear=lambda x, z: True, tries=400):
    """Up to n of `what` (a callable at x, z) on dry free ground."""
    done = 0
    for _ in range(tries):
        if done >= n:
            break
        x, z = S.rnd.randint(x0, x1), S.rnd.randint(z0, z1)
        if (x, z) in WET or not clear(x, z) or S.get(x, gh(x, z) + 1, z) not in (None, "air"):
            continue
        what(x, z)
        done += 1


def flowers(x, z):
    S.put(x, gh(x, z) + 1, z, S.pick(("short_grass", 8), ("fern", 2), ("poppy", 1), ("dandelion", 1), ("cornflower", 1),
                                     ("oxeye_daisy", 1), ("azure_bluet", 1)))


# ================================================================ Reedmere: the lake village

def bell_house(cx, cz, DY):
    """the lake's landmark on its round deck: an open timber frame, the shingled pyramid roof, the bell hung inside"""
    for dx in (-2, 2):
        for dz in (-2, 2):
            for yy in range(DY + 1, DY + 7):
                S.put(cx + dx, yy, cz + dz, "stripped_spruce_log[axis=y]")
    for x in range(-3, 4):
        for z in range(-3, 4):
            S.put(cx + x, DY + 7, cz + z, "spruce_planks" if max(abs(x), abs(z)) < 3 else H.stairs("spruce", "north", "top"))
    for k in range(4):
        for x in range(-3 + k, 4 - k):
            for z in range(-3 + k, 4 - k):
                if max(abs(x), abs(z)) == 3 - k:
                    S.put(cx + x, DY + 8 + k, cz + z, "ashbound:wood_shingles")
    S.put(cx, DY + 12, cz, "lightning_rod[facing=up,powered=false,waterlogged=false]")
    for x in range(-2, 3):
        S.put(cx + x, DY + 6, cz, "stripped_spruce_log[axis=x]")
    prop("village_bell", cx, DY + 5, cz, "south")            # its hook a whole block: the yoke up in the beam, the bell under it


# the lake village's three plans: the lake (middle, stretch along x and z, reach, its deep end), the deck, the landings
# (a start, the way to walk to find the shore), the branch walks (from: a spine's point, the deck's gate or a walk's point;
# to), the roads out from the first landing (or from a landing: (landing, to)), the beach lanes
LAKE = [
    dict(c=(0, -12), sx=1.2, sz=1.0, R=52, deep=(10, -40), focus=(2, -4), lands=(((0, 47), (0, 1)),),
         branches=((("s", 0, 0.3), (-36, 22)), (("s", 0, 0.55), (32, 18)), (("d", -1, 0), (-34, -24)), (("d", 1, 0), (30, -30)),
                   (("d", 0, -1), (-2, -40)), (("w", 1, 0.5), (-22, 38))),
         roads=((0, (0, 92)),), lanes=((0, (-70, 46)), (0, (68, 52)))),
    # a long lake crossed by a causeway from shore to shore, the deck at its middle, a road away from each landing
    dict(c=(0, -6), sx=1.9, sz=0.9, R=44, deep=(0, -6), focus=(0, -6), lands=(((0, 36), (0, 1)), ((4, -46), (0, -1))),
         branches=((("d", -1, 0), (-62, -10)), (("d", 1, 0), (64, -2)), (("s", 0, 0.5), (-28, 22)), (("s", 1, 0.5), (26, -32)),
                   (("w", 2, 0.6), (-44, -30))),
         roads=((0, (0, 92)), (1, (10, -92))), lanes=((0, (-72, 40)), (0, (72, 44)), (1, (-60, -60)))),
    # the lake off to the north-east, the village round its south-west shore, the deck close in by the landing
    dict(c=(30, -28), sx=1.15, sz=1.0, R=50, deep=(44, -44), focus=(14, -10), lands=(((-6, 12), (-1, 1)),),
         branches=((("d", 0, -1), (22, -58)), (("d", 1, 0), (66, -22)), (("s", 0, 0.5), (34, 14)), (("w", 1, 0.6), (54, -62)),
                   (("d", 1, 0), (48, 4))),
         roads=((0, (-92, 30)), (0, (-26, 92))), lanes=((0, (-58, -46)), (0, (30, 66)))),
]


def lake():
    import vplan
    new(11)
    V_ = LAKE[VAR % 3]
    cx, cz = V_["c"]                             # the lake's middle
    DY = 3                                       # every walk and floor over the water, up on stilts; the water's top is 0

    def hf(x, z):
        r = math.hypot((x - cx) / V_["sx"], (z - cz) / V_["sz"]) + 5 * noise(x, z, 16, 1)
        if r < V_["R"]:
            deep = -1.6 - 4.5 * max(0.0, 1 - math.hypot(x - V_["deep"][0], z - V_["deep"][1]) / 40)
            return deep + 0.8 * noise(x, z, 7, 2) + max(0, r - V_["R"] + 6) * 0.25
        return 0.6 + (r - V_["R"]) * 0.13 + 1.6 * noise(x, z, 22, 3)

    box = (-95, -95, 95, 95)
    land(*box, hf, water=0, bed=(("mud", 3), ("gravel", 2), ("sand", 1), ("clay", 1)))
    focus = V_["focus"]
    pal = dict(cols=(("slate_plaster", 4), ("plaster", 3), ("ochre_plaster", 1)),
               roofs=(("ashbound:wood_shingle", 6), ("ashbound:slate_shingle", 2)),
               woods=(("spruce", 4), ("dark_oak", 2)), shutters=(("ashbound:blue_shutter", 3), ("ashbound:green_shutter", 2), (None, 2)))
    P = vplan.Plan(sys.modules[__name__], box, focus, rings=(15, 34, 70), pal=pal, cap=24, deck=DY, stone=False)
    # the round deck and its bell house
    for a in range(-9, 10):
        for b in range(-9, 10):
            if math.hypot(a, b) <= 8.6:
                P.occ[(focus[0] + a, focus[1] + b)] = "focus"
                S.put(focus[0] + a, DY, focus[1] + b, "spruce_planks")
                if (a + b) % 4 == 0:
                    for yy in range(gh(focus[0] + a, focus[1] + b) + 1, DY):
                        S.put(focus[0] + a, yy, focus[1] + b, "spruce_log[axis=y]")
                if 8.0 < math.hypot(a, b) <= 8.6 and (a, b) not in ((0, 8), (0, -8), (-8, 0), (8, 0)) and abs(a) > 1 and abs(b) > 1:
                    S.put(focus[0] + a, DY + 1, focus[1] + b, "spruce_fence")
    bell_house(*focus, DY)
    # the walks: a spine from each landing on the shore out to the deck's nearest gate, branches wandering off them
    landings, walks = [], []
    for (lx, lz), (ux, uz) in V_["lands"]:
        while (lx, lz) in WET:
            lx, lz = lx + ux, lz + uz
        landings.append(((lx, lz), (ux, uz)))
        gx, gz = max(((1, 0), (-1, 0), (0, 1), (0, -1)), key=lambda g: g[0] * (lx - focus[0]) + g[1] * (lz - focus[1]))
        spine = P.wcurve((lx, lz), (focus[0] + 9 * gx, focus[1] + 9 * gz), 5, len(walks) + 1)
        P.walk(spine)
        walks.append(spine)
    spines = list(walks)
    for frm, to in V_["branches"]:
        if frm[0] == "s":
            q = spines[frm[1]][int(len(spines[frm[1]]) * frm[2])]
        elif frm[0] == "w":
            w_ = walks[min(frm[1], len(walks) - 1)]
            q = w_[int(len(w_) * frm[2])]
        else:
            q = (focus[0] + 9 * frm[1], focus[1] + 9 * frm[2])
        w = P.wcurve((int(q[0]), int(q[1])), to, 4, len(walks))
        P.walk(w)
        walks.append(w)
    spine = spines[0]
    landing = landings[0][0]
    # platforms at the walks' ends: the fishers' work floors
    ends = []
    for w in walks[len(spines):]:
        ex, ez = int(w[-1][0]), int(w[-1][1])
        if (ex, ez) in WET:
            for a in range(-3, 4):
                for b in range(-3, 4):
                    if P.occ.get((ex + a, ez + b)) in (None, "road"):
                        P.occ[(ex + a, ez + b)] = "road"
            ends.append((ex, ez))
    # the shore: the roads in to the landings, the lanes along the beach
    roads = []
    for li, to in V_["roads"]:
        (lx, lz), (ux, uz) = landings[li]
        road = P.route(to, (lx + ux, lz + uz))
        P.road(road, 1.4)
        roads.append(road)
    for li, to in V_["lanes"]:
        (lx, lz), (ux, uz) = landings[li]
        l = P.route((lx + 2 * ux, lz + 2 * uz), to)
        P.road(l, 1.0, "lane")
    road = roads[0]
    FOCUS["lake"] = (landing[0] + 3 * landings[0][1][0], landing[1] + 3 * landings[0][1][1])
    # the houses: round the deck, along the walks, then the shore's cottages and farms
    P.around(10.5, tries=30, n=6, role="mid")
    for w in walks:
        P.frontage(w if w not in spines else list(reversed(w)), start=2, skip=0.2)
    for road in roads:
        P.frontage(list(reversed(road)), start=2, skip=0.3)
    # what the fishers leave about: racks on the end floors, boats tied along the walks, lanterns on posts
    for k, (ex, ez) in enumerate(ends):
        prop("net_rack" if k % 2 == 0 else "fish_rack", ex, DY + 1, ez, "north" if ez > focus[1] else "south")
        prop("catch_basket", ex + 2, DY + 1, ez + 1, "west")
    edge_cells = []
    for w in walks:
        for i_, (x, z) in enumerate(w[::2]):
            x, z = int(round(x)), int(round(z))
            if i_ % 11 == 5:
                for dx, dz in ((2, 0), (-2, 0), (0, 2), (0, -2)):
                    if (x + dx, z + dz) in WET and P.occ.get((x + dx, z + dz)) is None and P.occ.get((x + dx // 2, z + dz // 2)) == "road":
                        prop("lake_lantern", x + dx // 2, DY + 1, z + dz // 2, {(1, 0): "east", (-1, 0): "west", (0, 1): "south", (0, -1): "north"}[(dx // 2, dz // 2)])
                        break
            if i_ % 13 == 9:
                for dx, dz in ((3, 0), (-3, 0), (0, 3), (0, -3)):
                    p = (x + dx, z + dz)
                    if all((p[0] + a, p[1] + b) in WET and P.occ.get((p[0] + a, p[1] + b)) is None for a in (-1, 0, 1) for b in (-2, -1, 0, 1, 2)):
                        prop(S.pick(("punt", 2), ("dugout", 1)), p[0], 0.4, p[1], "north" if dx else "east")
                        for a in (-1, 0, 1):
                            for b in (-2, -1, 0, 1, 2):
                                P.occ[(p[0] + a, p[1] + b)] = "boat"
                        break
    lx, lz = landing
    for (a, b, nm, f) in ((3, 2, "mooring_post", "north"), (-4, 1, "mooring_post", "north"), (5, 4, "eel_traps", "west"),
                          (-6, 4, "reed_sheaves", "south"), (7, 2, "catch_basket", "north"), (-3, 6, "net_rack", "east")):
        if (lx + a, lz + b) not in WET:
            prop(nm, lx + a, gh(lx + a, lz + b) + 1, lz + b, f)
            P.occ[(lx + a, lz + b)] = "clutter"
    P.fields(n=5)
    P.yards()
    P.paths()
    P.street_life(14)
    P.woods(40, names=("willow_large_0", "willow_large_1", "willow_medium_0", "willow_medium_1", "willow_medium_2", "oak_medium_0", "birch_medium_1"))
    P.pave()
    for (x, z), wy in list(WET.items()):                                     # reeds, lilies and weed
        if P.occ.get((x, z)) or S.get(x, 1, z) not in (None, "air") or S.get(x, DY, z) not in (None, "air"):
            continue
        dep = wy - gh(x, z)
        r = S.rnd.random()
        near_shore = any(gh(x + dx, z + dz) >= 1 for dx in (-2, 0, 2) for dz in (-2, 0, 2))
        if near_shore and r < 0.3:
            S.put(x, 1, z, "sugar_cane")
            S.put(x, 0, z, "mud")
        elif dep < 4 and r < 0.03:
            S.put(x, 1, z, "lily_pad")
        elif dep >= 2 and r < 0.12:
            S.put(x, gh(x, z) + 1, z, "seagrass")
    scatter(500, *box, flowers, clear=lambda x, z: P.occ.get((x, z)) is None and gh(x, z) >= 1)
    for (x, z) in list(WET):                                                 # no post standing bare in the water
        logs = [yy for yy in range(gh(x, z) + 1, DY + 3) if S.get(x, yy, z) == "spruce_log[axis=y]"]
        if logs and S.get(x, max(logs) + 1, z) in (None, "air") or logs and S.get(x, max(logs) + 1, z) == WATER:
            for yy in logs:
                S.put(x, yy, z, WATER if yy <= WET[(x, z)] else None)
    finish()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "renders", "villages")
    os.makedirs(out, exist_ok=True)
    P.plan_png(os.path.join(out, "plan_%s.png" % out_name("lake")))
    print("houses", len(P.houses), {r: sum(1 for h in P.houses if h["role"] == r) for r in ("core", "mid", "edge", "farm")})
    return {"approach": ((lx + 3, gh(lx, lz + 12) + 4, lz + 14), (focus[0], 4, focus[1]), 26),
            "wide": ((-20, 34, -70), (2, 2, 0), 24),
            "deck": ((focus[0] + 16, 7, focus[1] + 14), (focus[0], 4, focus[1]), 26),
            "water": ((-40, 3, 10), (5, 3, -6), 24)}


# ================================================================ Archford: the bridge over the gorge

# the gorge village's three plans: where the bridge crosses (z), its arches (middle, radius) and their spring, whether
# its spandrels are pierced and houses crowd it, the toll tower's end (-1 west, 1 east), the mill down on the river
GORGE = [
    dict(bz=0, arches=((0, 15),), spring=8, holes=True, houses=True, tower=-1, mill=(5, -30)),
    dict(bz=-22, arches=((-10, 5), (0, 5), (10, 5)), spring=12, holes=False, houses=False, tower=-1, mill=(5, 32)),   # a viaduct
    dict(bz=26, arches=((-7, 7.5), (7, 7.5)), spring=14, holes=False, houses=True, tower=1, mill=(5, -34)),
]


def gorge():
    import vplan
    import vhouse as VH
    new(23)
    V_ = GORGE[VAR % 3]
    bz, sd = V_["bz"], V_["tower"]               # where the bridge crosses, which end the toll tower guards
    TOP = 30

    def hf(x, z):
        wob = 3 * noise(0, z, 18, 4)
        ax = abs(x - wob)
        if ax >= 14 + 2 * noise(x, z, 9, 5):
            return TOP + 2 * noise(x, z, 24, 6) + max(0, ax - 40) * 0.1
        if ax >= 10:
            return 6 + (ax - 10) * 6 + 3 * noise(x, z, 4, 7)          # the walls, near sheer
        if ax >= 5:
            return 1 + (ax - 5) * 1.0 + noise(x, z, 5, 8)
        return -2

    box = (-95, -95, 95, 95)
    land(*box, hf, water=0, rock=("stone", "andesite", "tuff", "stone"), steep=3,
         bed=(("gravel", 4), ("cobblestone", 1), ("mossy_cobblestone", 1)))
    STONE = (("ashbound:greystone", 8), ("ashbound:mossy_greystone", 2), ("stone_bricks", 1))
    RING = "stone_bricks"
    DECK = TOP + 1                               # the road's level
    pal = dict(cols=(("ochre_plaster", 4), ("rose_plaster", 2), ("plaster", 3)),
               roofs=(("ashbound:clay_roof_tile", 6), ("ashbound:slate_shingle", 2), ("ashbound:wood_shingle", 1)),
               woods=(("oak", 3), ("spruce", 2), ("dark_oak", 1)), shutters=(("ashbound:red_shutter", 3), ("ashbound:green_shutter", 2), (None, 1)))
    P = vplan.Plan(sys.modules[__name__], box, (0, bz), rings=(16, 42, 80), pal=pal, cap=28)

    # the bridge: its round arches over the gorge (the great one's spandrels pierced), the road on top
    spring = V_["spring"]
    for x in range(-22, 23):
        under = [(c_, R) for c_, R in V_["arches"] if abs(x - c_) < R]
        soffit = max((spring + math.sqrt(max(0, R * R - (x - c_) ** 2)) for c_, R in under), default=-99)
        near = any(abs(x - c_) < R + 2 for c_, R in V_["arches"])
        for z in range(bz - 4, bz + 5):
            P.occ[(x, z)] = "road" if abs(z - bz) <= 1 else "landmark"
            for y in range(max(gh(x, z) - 2, -2), DECK):
                if under and y < soffit:
                    continue
                hole = V_["holes"] and any(abs(x - c) <= 2 and math.hypot(x - c, y - (spring + 11)) < 2.4 for c in (-10, 10))
                if hole:
                    continue
                ring = (y < soffit + 2.2) if under else (near and y < spring + 2)
                S.put(x, y, z, RING if ring and abs(z - bz) == 4 else S.pick(*STONE))
    for c_, R in V_["arches"]:
        S.put(c_, spring + R, bz - 4, "ashbound:carved_limestone")
        S.put(c_, spring + R, bz + 4, "ashbound:carved_limestone")
    for x in range(-22, 23):
        for z in range(bz - 4, bz + 5):
            S.put(x, DECK, z, S.pick(("ashbound:greystone", 4), ("cobblestone", 2), ("andesite", 1)) if abs(z - bz) <= 1 else "ashbound:greystone")
    # the houses packed along the bridge, backs out over the drop on oak struts (the core: no yards, no footings)
    for side in ((-1, 1) if V_["houses"] else ()):
        x = -21 + S.rnd.randint(0, 2)
        face = "north" if side == 1 else "south"
        while x < 20:
            T = K.Build()
            T.rnd = S.rnd
            h = VH.compose(T, 0, 0, face, S.pick(("core", 3), ("mid", 1)), pal, stone=False)
            fw = max(a for a, _ in h["cells"]) + 1
            fd = max(b for _, b in h["cells"]) + 1
            if x + fw > 22:
                break
            z0 = bz + 2 if side == 1 else bz - 1 - fd
            P.place(T, h, x, z0, DECK, face, "core", (0, side), fw, fd, footing=False, yard=False)
            far = z0 + fd - 1 if side == 1 else z0
            for a in range(x, x + fw, 3):                        # struts down to the bridge's face
                for k in range(max(0, abs(far) - 4)):
                    zz = bz + ((5 + k) if side == 1 else (-5 - k))
                    S.put(a, DECK - 1, zz, "spruce_planks")
                    yy = DECK - 2 - k
                    if yy > spring + 2:
                        S.put(a, yy, zz - side, "spruce_stairs[facing=%s,half=top,shape=straight,waterlogged=false]" %
                              ("north" if side == 1 else "south"))
                        S.put(a, yy - 1, zz - side, "stripped_spruce_log[axis=y]")
            x += fw + S.rnd.choice((0, 0, 1))
    # the toll tower over the road at the west end (the landmark), the barrier at the east end
    tx = 30 * sd
    for x in range(tx - 4, tx + 5):
        for z in range(bz - 5, bz + 6):
            P.occ[(x, z)] = "landmark" if abs(z - bz) > 1 else "road"
            ring_ = max(abs(x - tx), abs(z - bz)) >= 4
            for y in range(gh(x, z) - 1, DECK + 16):
                if ring_ or y <= DECK - 1 or y in (DECK + 6, DECK + 12):
                    if abs(z - bz) <= 1 and DECK + 1 <= y <= DECK + 4 and abs(x - tx) == 4:
                        continue
                    S.put(x, y, z, S.pick(*STONE))
            if ring_ and (x + z) % 2 == 0:
                S.put(x, DECK + 16, z, S.pick(*STONE))
        for z in range(bz - 1, bz + 2):
            for y in range(DECK + 1, DECK + 5):
                S.put(x, y, z, None)
            S.put(x, DECK, z, "ashbound:greystone")
    for y in (DECK + 9, DECK + 10):
        for (x, z) in ((tx, bz - 4), (tx, bz + 4), (tx - 4, bz), (tx + 4, bz)):
            S.put(x, y, z, "iron_bars[east=false,north=false,south=false,waterlogged=false,west=false]")
    for x in (range(tx - 4, -22) if sd < 0 else range(23, tx + 5)):   # the road from the tower onto the bridge
        for z in range(bz - 1, bz + 2):
            S.put(x, DECK, z, "ashbound:greystone")
    prop("toll_barrier", -24 * sd, gh(-24 * sd, bz + 3) + 1, bz + 3, "east" if sd < 0 else "west")
    # the roads out across the plateaus, and a lane along each rim
    west = P.route(((tx - 6) if sd < 0 else -24, bz), (-92, bz + 8))
    east = P.route((24 if sd < 0 else tx + 6, bz), (92, bz - 6))
    north = P.route((30, bz - 6), (34, -92))
    south = P.route((-30, bz + 7), (-30, 92))
    for rd, w in ((west, 1.5), (east, 1.5), (north, 1.0), (south, 1.0)):
        P.road(rd, w)
    # the mill down on the river, its wheel in the stream, a crane on the rim to haul the flour up, stairs cut down
    mx, mz = V_["mill"]
    for x in range(mx - 1, mx + 9):
        for z in range(mz - 1, mz + 9):
            for y in range(-2, 1):
                S.put(x, y, z, S.pick(*STONE))
            G[(x, z)] = 0
            WET.pop((x, z), None)
    T = K.Build()
    T.rnd = S.rnd
    h = VH.compose(T, 0, 0, "west", "mid", pal)
    P.place(T, h, mx, mz, 0, "west", "mid", (1, 0), 8, 8, footing=False, yard=False)
    prop("water_wheel", mx - 2, 2.6, mz + 4, 90)
    prop("hoist_crane", 13, gh(13, mz + 3) + 1, mz + 3, "west")
    prop("churns_sacks", mx + 2, 1, mz - 2, "south")
    d = -1 if mz < 0 else 1                       # the stairs down to it, from the rim on its side of the bridge
    x, z, y = 12, mz + 22 * (1 if mz < 0 else -1) - d * 0, DECK - 1
    while y > 2:
        for k in range(10):
            if y <= 2:
                break
            zz = z + d * k
            for dx in (0, 1):
                S.put(x + dx, y, zz, "ashbound:greystone_stairs[facing=%s,half=bottom,shape=straight,waterlogged=false]" %
                      ("north" if d == 1 else "south"))
                for yy in range(y + 1, y + 4):
                    S.put(x + dx, yy, zz, None)
                S.put(x + dx, y - 1, zz, S.pick(*STONE))
            S.put(x + 2, y + 1, zz, "ashbound:greystone_wall")
            y -= 1
        z += d * 9
        d = -d
    prop("rope_ladder", -13, TOP - 5, 22 if bz <= 0 else -12, "east")
    prop("lift_basket", -16, gh(-16, -40) + 1, -40, "east")
    # the houses on the plateaus: dense by the bridge ends, farms further out
    FOCUS["gorge"] = (-40, bz + 2)
    if not V_["houses"]:                                          # the viaduct's village gathers round a green at its east end
        green(P, 46, bz + 12)
        P.focus = (46, bz + 12)
        P.around(8.5, tries=40, n=9)
        P.focus = (0, bz)
    for rd in (west, east, north, south):                         # with no houses on the bridge, the ends close up
        P.frontage(rd, start=3 if V_["houses"] else 1, skip=0.2 if V_["houses"] else 0.0)
    P.fields(n=8)
    P.yards()
    P.paths()
    P.street_life(18)
    P.woods(50)
    P.pave()
    scatter(600, *box, flowers, clear=lambda x, z: P.occ.get((x, z)) is None and gh(x, z) >= TOP - 3)
    finish()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "renders", "villages")
    os.makedirs(out, exist_ok=True)
    P.plan_png(os.path.join(out, "plan_%s.png" % out_name("gorge")))
    print("houses", len(P.houses), {r: sum(1 for h in P.houses if h["role"] == r) for r in ("core", "mid", "edge", "farm")})
    return {"wide": ((3, 16, -75), (0, 20, 0), 22), "rim": ((62, 58, 58), (0, 24, 0), 24),
            "road": ((-44 * sd, DECK + 3, bz + 0.5), (10 * sd, DECK + 3, bz + 0.5), 30), "mill": ((-3, 9, -52), (6, 6, -28), 26)}


# ================================================================ Stepcliff: terraces up a rock face

BRICK = (("stone_bricks", 8), ("mossy_stone_bricks", 1), ("cracked_stone_bricks", 1))     # clean masonry, never cobble


# the cliff village's three plans: terraces (rise, how many, how deep, how much the faces bow forward at the ends),
# where the stairs climb (even terraces, odd), the falls' notch, the beacon
CLIFF = [
    dict(lv=14, n=4, deep=22, bow=0.0, stairs=(-30, 24), falls=46, beacon=-4),
    dict(lv=14, n=4, deep=21, bow=0.006, stairs=(26, -28), falls=-52, beacon=8),          # an amphitheatre round the square
    dict(lv=18, n=3, deep=28, bow=0.0, stairs=(-8, 30), falls=-40, beacon=36),            # fewer, taller, deeper
]


def cliff():
    import vplan
    new(41)
    V_ = CLIFF[VAR % 3]
    LV, NT, DEP = V_["lv"], V_["n"], V_["deep"]   # each terrace this much over the one below, how many, how deep

    def zw(j, x):
        """the foot of the wall that rises to terrace j (its face runs east-west, terrace j behind it, north), bowed
        forward at the ends when the plan curves"""
        return 30 - DEP * (j - 1) + V_["bow"] * x * x + 1.6 * noise(x, 0, 14, 40 + j)

    def hf(x, z):
        for j in range(1, NT + 1):
            w = zw(j, x)
            if z > w:
                return LV * (j - 1) + (0.6 * noise(x, z, 12, 50) if j == 1 else 0)
            if z > w - 3:
                return LV * (j - 1) + (w - z) / 3 * LV + noise(x, z, 3, 51)    # the sheer face
        return LV * NT + max(0, zw(NT, x) - 3 - z) * 0.15 + noise(x, z, 16, 52)

    box = (-80, -80, 80, 80)
    land(*box, hf, rock=("stone", "andesite", "tuff", "stone", "cobblestone"), steep=3)
    pal = dict(cols=(("plaster", 4), ("ochre_plaster", 2), ("slate_plaster", 2)),
               roofs=(("ashbound:slate_shingle", 5), ("ashbound:clay_roof_tile", 2), ("ashbound:wood_shingle", 1)),
               woods=(("spruce", 3), ("dark_oak", 2)), shutters=(("ashbound:green_shutter", 3), ("ashbound:blue_shutter", 2), (None, 1)))
    focus = (0, int(zw(2, 0)) - 9)
    P = vplan.Plan(sys.modules[__name__], box, focus, rings=(18, 42, 80), pal=pal, cap=26)
    P.dig = LV + 2                                # houses cut back into the rock behind them
    FLIGHTS.clear()
    CLEAR.clear()
    STONE = (("ashbound:greystone", 8), ("ashbound:mossy_greystone", 2), ("stone_bricks", 1))
    # each terrace's lane along its front, a parapet on the drop; the valley's road in from the south
    lanes = []
    for j in range(0, NT):                                        # 0: the valley's lane at the cliff's foot
        xs = [k * 0.5 for k in range(-132, 133)]                   # half-block steps, as the planner's roads come
        pts = [(x, zw(j, x) - 4.5) for x in xs] if j > 0 else [(x, zw(1, x) + 6) for x in xs]
        P.road(pts, 1.2)
        lanes.append((j, pts))
        if j > 0:
            for x in range(-66, 67):
                z = int(math.floor(zw(j, x) - 3))
                for dz in (0, -1):
                    if gh(x, z + dz) >= LV * j - 1:
                        S.put(x, gh(x, z + dz) + 1, z + dz, "ashbound:greystone_wall")
                        break
    # the stairs: a straight flight three wide cut into each face, a terrace in fourteen steps, solid under it, the rock
    # cut back over it, a stepped cheek wall on the open side, a paved landing through the lip at the top; they switch
    # back, east then west
    for j in range(1, NT + 1):
        x0 = (V_["stairs"][0] if j % 2 == 0 else V_["stairs"][1]) + S.rnd.randint(-4, 4)
        d = 1 if j % 2 == 0 else -1
        y0 = LV * (j - 1)
        xs = [x0 + d * i for i in range(LV + 3)]
        zc = int(round(sum(zw(j, x) for x in xs) / len(xs))) - 2
        rows = (zc - 1, zc, zc + 1)
        walk = {}
        for i in range(LV):
            for zz in rows:
                walk[(x0 + d * i, zz)] = (y0 + i + 1, "stone_brick_stairs[facing=%s,half=bottom,shape=straight,waterlogged=false]"
                                          % ("east" if d > 0 else "west"))
        for k in range(1, 5):                                       # the foot: a paved way in, cut back through the face
            for zz in range(zc - 1, zc + 4):
                if zz > zc + 1 and gh(x0 - d * k, zz) <= y0:
                    continue
                walk[(x0 - d * k, zz)] = (y0, "ashbound:limestone_flagstones")
        xe = x0 + d * LV
        FLIGHTS.append((y0, [(x0 - d * k, zc) for k in range(4, 0, -1)] + [(x0 + d * i, zc) for i in range(LV + 3)]))
        xf = x0 - 2 * d + 0.5                                      # a lane from the foot down to the terrace's own lane,
        zl = zw(j - 1, xf) - 4.5 if j > 1 else zw(1, xf) + 6         # kept clear of yards and trees
        P.road([(xf, zc + 2 + k * 0.5) for k in range(int((zl - zc - 2) * 2) + 1)], 1.2, "lane")
        for xx in (xe, xe + d, xe + 2 * d):                         # the landing, out onto the terrace above
            for zz in range(zc - 5, zc + 2):
                walk[(xx, zz)] = (y0 + LV, "ashbound:limestone_flagstones")
        for (x, zz), (y, st) in walk.items():
            for yy in range(min(gh(x, zz), y) - 1, y):
                S.put(x, yy, zz, S.pick(*BRICK))
            S.put(x, y, zz, st)
            for yy in range(y + 1, max(gh(x, zz), y) + 5):                 # cut open to the sky, no rock roof over it
                S.put(x, yy, zz, None)
            G[(x, zz)] = y
            P.occ[(x, zz)] = "road" if st.endswith("flagstones") else "steps"
            CLEAR.update((x, yy, zz) for yy in range(y + 1, y + 4))
        for (x, zz), (y, st) in walk.items():                        # the cheek wall wherever the side drops away
            for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (x + a, zz + b)
                if q in walk or gh(*q) >= y - 1 or S.get(q[0], y, q[1]) not in (None, "air") and not _natural(S.get(q[0], y, q[1])):
                    continue
                if a == -d and b == 0 and st.endswith("stairs"):
                    continue                                          # the flight's own foot stays open
                for yy in range(gh(*q), y + 1):
                    S.put(q[0], yy, q[1], S.pick(*BRICK))
                S.put(q[0], y + 1, q[1], "stone_brick_wall")
                P.occ.setdefault(q, "steps")
    # the waterfall: down a notch in the east, a pool on each terrace, the plunge pool and the brook to the south
    fx = V_["falls"]
    for j in range(1, NT + 1):
        zb = int(math.floor(zw(j, fx)))
        top = LV * j
        for x in range(fx, fx + 4):                                 # the cascade: water over the whole face of the notch
            for zz in range(zb - 4, zb + 1):
                for yy in range(LV * (j - 1) + 1, gh(x, zz) + 1):
                    S.put(x, yy, zz, "water[level=0]#flow")
                for yy in range(gh(x, zz) - 2, LV * (j - 1) + 1):
                    S.put(x, yy, zz, "stone" if yy < gh(x, zz) else S.get(x, yy, zz))
        for x in range(fx - 1, fx + 4):                              # the pool at its foot
            for zz in range(zb + 1, zb + 5):
                g = LV * (j - 1)
                S.put(x, g, zz, "water[level=0]")
                S.put(x, g - 1, zz, "gravel")
                P.occ[(x, zz)] = "water"
    for zz in range(int(zw(1, fx)) + 5, 80):                        # the brook
        for x in (fx, fx + 1):
            S.put(x, gh(x, zz), zz, "water[level=0]")
            P.occ[(x, zz)] = "water"
            WET[(x, zz)] = gh(x, zz)
    # the beacon on the top lip (the landmark), seen from the whole valley
    bx = V_["beacon"]
    bz = int(zw(NT, bx)) - 6
    yb = max(gh(bx + a, bz + b) for a in range(-3, 4) for b in range(-3, 4))
    for a in range(-3, 4):
        for b in range(-3, 4):
            P.occ[(bx + a, bz + b)] = "landmark"
            ring_ = max(abs(a), abs(b)) >= 2
            for yy in range(gh(bx + a, bz + b) - 1, yb + 16):
                if ring_ or yy <= yb or yy == yb + 15:
                    if not (abs(a) <= 2 and abs(b) <= 2) and yy > yb + 1:
                        continue
                    if max(abs(a), abs(b)) == 2 and yb + 12 <= yy <= yb + 14 and (a == 0 or b == 0):
                        S.put(bx + a, yy, bz + b, H.PANE)
                        continue
                    S.put(bx + a, yy, bz + b, S.pick(*STONE))
    S.put(bx, yb + 1, bz + 2, None)
    S.put(bx, yb + 2, bz + 2, None)
    S.put(bx, yb + 13, bz, "campfire[facing=north,lit=true,signal_fire=false,waterlogged=false]")
    for k in range(4):
        for a in range(-3 + k, 4 - k):
            for b in range(-3 + k, 4 - k):
                if max(abs(a), abs(b)) == 3 - k:
                    S.put(bx + a, yb + 16 + k, bz + b, "ashbound:slate_shingles")
    # the road in from the south, the houses: the plaza's ring first, then each terrace's lane, then the valley's farms
    road = P.route((0, 78), (0, int(zw(1, 0)) + 7))
    P.road(road, 1.5)
    fz = focus[1]
    for a in range(-5, 6):
        for b in range(-3, 4):
            P.occ[(focus[0] + a, fz + b)] = "focus"
            S.put(focus[0] + a, gh(focus[0] + a, fz + b), fz + b, "ashbound:limestone_flagstones")
    prop("well", focus[0], gh(*focus) + 1, fz, "south")
    prop("market_stall", focus[0] + 4, gh(focus[0] + 4, fz) + 1, fz - 1, "south")
    for j, pts in sorted(lanes, key=lambda l: -l[0] % 4):         # terraces first (backs to the rock), then the valley
        P.frontage(pts, sides=(-1,) if j > 0 else (1,), start=2, skip=0.12)
    P.frontage(list(reversed(road)), start=2, skip=0.2)
    # cranes on the lips to haul goods up, a lift on the tallest face, a ladder, the signpost at the foot
    for j, x in [(2, -12), (3, 14), (4, -40)][:NT - 1]:
        zf = int(math.floor(zw(j, x))) - 4
        if P.occ.get((x, zf)) is None:
            prop("hoist_crane", x, gh(x, zf) + 1, zf, "south")
            P.occ[(x, zf)] = "clutter"
    prop("lift_basket", 34, gh(34, int(zw(1, 34)) + 4) + 1, int(zw(1, 34)) + 4, "south")
    prop("rope_ladder", -50, LV - 5, int(zw(2, -50)) + 1, "south")
    prop("signpost", 3, gh(3, int(zw(1, 3)) + 10) + 1, int(zw(1, 3)) + 10, "south")
    P.fields(n=6)
    P.yards()
    P.paths()
    P.street_life(18)
    P.woods(36, names=("oak_medium_0", "oak_medium_1", "pine_medium_0", "pine_medium_1", "birch_medium_0", "oak_small_1"))
    P.pave()
    scatter(500, *box, flowers, clear=lambda x, z: P.occ.get((x, z)) is None)
    finish()
    keep_flights()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "renders", "villages")
    os.makedirs(out, exist_ok=True)
    P.plan_png(os.path.join(out, "plan_%s.png" % out_name("cliff")))
    print("houses", len(P.houses), {r: sum(1 for h in P.houses if h["role"] == r) for r in ("core", "mid", "edge", "farm")})
    return {"stairs": ((36, 16, 50), (16, 7, int(zw(1, 16)) - 2), 24), "wide": ((10, 34, 98), (0, 26, -10), 22), "lane": ((-40, 24, int(zw(2, -40)) - 4), (10, 22, int(zw(2, 10)) - 8), 26),
            "falls": ((72, 24, 64), (47, 26, -12), 26), "high": ((-60, 80, 75), (0, 24, -10), 22)}


# ================================================================ Lumenhollow: the elves' giant tree

EWOOD = (("ashbound:wildwood_wood", 9), ("ashbound:mossy_wildwood_wood", 1))
PALEW = "stripped_birch_log[axis=y]"


CORE = "moss_block"     # the hidden heart of a leaf clump: opaque, so the leaves round it don't draw their inner faces


def blob(cx, cy, cz, r, st, only_empty=False):
    for x in range(math.floor(cx - r), math.ceil(cx + r) + 1):
        for y in range(math.floor(cy - r), math.ceil(cy + r) + 1):
            for z in range(math.floor(cz - r), math.ceil(cz + r) + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 + (z - cz) ** 2 <= r * r:
                    if only_empty and S.get(x, y, z) not in (None, "air"):
                        continue
                    S.put(x, y, z, S.pick(*st) if isinstance(st, tuple) else st)


def limb(pts, r0, r1, st=EWOOD):
    """a branch: spheres swept along the points, thinning from r0 to r1"""
    seg = []
    for a, b in zip(pts, pts[1:]):
        n = max(1, int(math.dist(a, b) / 0.6))
        seg += [tuple(a[k] + (b[k] - a[k]) * i / n for k in range(3)) for i in range(n)]
    seg.append(pts[-1])
    for i, q in enumerate(seg):
        blob(*q, r0 + (r1 - r0) * i / max(1, len(seg) - 1), st)


def clump(cx, cy, cz, rx, ry, rz, seed, accent=None):
    """a cloud of leaves: sunlit on top, shade underneath, hollow inside, ragged at the edge"""
    for x in range(math.floor(cx - rx - 2), math.ceil(cx + rx + 3)):
        for y in range(math.floor(cy - ry - 2), math.ceil(cy + ry + 3)):
            for z in range(math.floor(cz - rz - 2), math.ceil(cz + rz + 3)):
                u, v, w = (x - cx) / rx, (y - cy) / ry, (z - cz) / rz
                d = u * u + v * v + w * w
                lim = 1 + 0.35 * noise(x + y * 7, z - y * 5, 3.5, seed)
                if d > lim or S.get(x, y, z) not in (None, "air"):
                    continue
                if d < 0.42:
                    S.put(x, y, z, CORE)
                    continue
                if v > 0.3:
                    st = S.pick(("ashbound:wildwood_leaves_sunlit", 6), ("ashbound:wildwood_leaves", 2), ("ashbound:wildwood_blossom", 1))
                elif v < -0.3:
                    st = "ashbound:wildwood_leaves_shade"
                else:
                    st = S.pick(("ashbound:wildwood_leaves", 5), ("ashbound:wildwood_leaves_shade", 1))
                if accent and S.rnd.random() < 0.45:
                    st = accent
                S.put(x, y, z, st)


class ETree:
    """a tree of the elves: fluted, twisting trunk on buttress roots, limbs rising out to clouds of leaves"""

    def __init__(self, cx, cz, gy, r0, top, limbs, limb_y, reach, seed, accent=None, roots=7):
        self.cx, self.cz, self.gy, self.r0, self.top = cx, cz, gy, r0, top
        self.cells = set()
        R = self.R
        for y in range(gy - 3, top + 1):
            rr = R(y) * 1.13 + 1
            for x in range(math.floor(cx - rr), math.ceil(cx + rr) + 1):
                for z in range(math.floor(cz - rr), math.ceil(cz + rr) + 1):
                    a = math.atan2(z - cz, x - cx)
                    if math.hypot(x - cx, z - cz) <= R(y) * (1 + 0.12 * math.sin(5 * a + 0.09 * y)):
                        S.put(x, y, z, "ashbound:mossy_wildwood_wood" if y < gy + 6 and S.rnd.random() < 0.35 else S.pick(*EWOOD))
                        self.cells.add((x, z))
        for k in range(roots):                                              # buttress roots
            a = k * 2 * math.pi / roots + 0.3 * noise(k, 0, 1, seed)
            c, s_ = math.cos(a), math.sin(a)
            L = r0 * (0.9 + 0.35 * S.rnd.random())
            pts = [(cx + c * R(gy + 8) * 0.7, gy + 9, cz + s_ * R(gy + 8) * 0.7), (cx + c * (r0 + L * 0.35), gy + 3.5, cz + s_ * (r0 + L * 0.35)),
                   (cx + c * (r0 + L * 0.75), gy + 0.5, cz + s_ * (r0 + L * 0.75)), (cx + c * (r0 + L), gy - 1.5, cz + s_ * (r0 + L))]
            limb(pts, r0 * 0.27, r0 * 0.1, (("ashbound:mossy_wildwood_wood", 2), ("ashbound:wildwood_wood", 3)))
        self.ends = []
        for k in range(limbs):                                              # the limbs and their leaves
            a = k * 2 * math.pi / limbs + 0.5 * noise(k, 3, 1, seed + 1)
            c, s_ = math.cos(a), math.sin(a)
            y0 = limb_y + (k * 7) % 11
            L = reach * (0.8 + 0.35 * S.rnd.random())
            pts = [(cx + c * t * L, y0 + reach * 0.5 * (1 - (1 - t) ** 2), cz + s_ * t * L) for t in (0, 0.2, 0.45, 0.7, 1.0)]
            limb(pts, R(y0) * 0.55, R(y0) * 0.18)
            e = pts[-1]
            m = pts[2]
            side = (-s_ * L * 0.3, 3, c * L * 0.3)
            limb([m, (m[0] + side[0], m[1] + side[1], m[2] + side[2])], R(y0) * 0.25, R(y0) * 0.12)
            ac = accent if accent and k % 3 == 1 else None
            clump(e[0], e[1] + 2, e[2], reach * 0.38, reach * 0.22, reach * 0.38, seed + 10 + k, ac)
            clump(m[0] + side[0], m[1] + 5, m[2] + side[2], reach * 0.28, reach * 0.17, reach * 0.28, seed + 20 + k)
            self.ends.append((a, e))
        clump(cx, top + reach * 0.15, cz, reach * 0.5, reach * 0.28, reach * 0.5, seed + 40)

    def R(self, y):
        h = y - self.gy
        return self.r0 * (0.55 + 0.45 * math.exp(-max(0, h) / (self.r0 * 0.55))) - 0.003 * self.r0 * max(0, h)

    def Rmax(self, y):
        return self.R(y) * 1.13


DECK = {}       # (x, z) -> the elves' floors at that column (a set of y)
RIM = {}        # (x, z, y) -> True for the deck's rail line
GAPS = set()    # (x, z, y) with no rail: where the bridges and stairs come in
BRIDGE = set()  # (x, z) under the bridges' boards


def deck(T, y, W, seed):
    """a ring of pale boards round the trunk, its outline wandering, a rail on its rim, struts underneath"""
    ro = lambda a: T.Rmax(y) + W + 1.6 * noise(8 * math.cos(a), 8 * math.sin(a), 4, seed)
    n = int(T.Rmax(y) + W + 3)
    for x in range(T.cx - n, T.cx + n + 1):
        for z in range(T.cz - n, T.cz + n + 1):
            a = math.atan2(z - T.cz, x - T.cx)
            r = math.hypot(x - T.cx, z - T.cz)
            if r > ro(a) or S.get(x, y, z) and "wildwood_wood" in S.get(x, y, z):
                continue
            rim = r > ro(a) - 1.1
            S.put(x, y, z, "stripped_birch_log[axis=y]" if rim else "birch_planks")
            DECK.setdefault((x, z), set()).add(y)
            for yy in range(y + 1, y + 4):
                if S.get(x, yy, z) and ("leaves" in S.get(x, yy, z) or S.get(x, yy, z) == CORE):
                    S.put(x, yy, z, None)
            if rim:
                RIM[(x, y, z)] = True
    ns = 9 if W >= 7 else 4
    for k in range(ns):                                                     # the struts: from the trunk out to the rim
        a = k * 2 * math.pi / ns + 0.2
        c, s_ = math.cos(a), math.sin(a)
        r1 = ro(a) - 1.5
        limb([(T.cx + c * T.R(y - 9), y - 9, T.cz + s_ * T.R(y - 9)), (T.cx + c * r1 * 0.7, y - 3, T.cz + s_ * r1 * 0.7),
              (T.cx + c * r1, y - 1, T.cz + s_ * r1)], 0.8 if W >= 7 else 0.5, 0.7 if W >= 7 else 0.5, "stripped_birch_wood[axis=y]")
    return ro


def floor_disc(cx, y, cz, r):
    for x in range(math.floor(cx - r), math.ceil(cx + r) + 1):
        for z in range(math.floor(cz - r), math.ceil(cz + r) + 1):
            d = math.hypot(x - cx, z - cz)
            if d <= r:
                rim = d > r - 1
                S.put(x, y, z, "stripped_birch_log[axis=y]" if rim else "birch_planks")
                DECK.setdefault((x, z), set()).add(y)
                if rim:
                    RIM[(x, y, z)] = True


def pod(cx, y, cz, r, door, roof="ashbound:green_roof_tiles", hang=False, n_win=5):
    """an elf's house: a round room of pale boards and birch posts, tall windows, a leaf-dome roof with a spire,
    its door turned toward `door` (an angle)"""
    if not hang:
        floor_disc(cx, y, cz, r + 1.6)
    else:
        for k in range(1, int(r) + 2):                                       # the hanging pod's bowl under the floor
            rr = (r + 0.5) * (1 - (k / (r + 2)) ** 1.4)
            for x in range(math.floor(cx - rr), math.ceil(cx + rr) + 1):
                for z in range(math.floor(cz - rr), math.ceil(cz + rr) + 1):
                    d = math.hypot(x - cx, z - cz)
                    if rr - 1.2 < d <= rr:
                        S.put(x, y - k, z, "stripped_birch_wood[axis=y]" if k % 2 else "birch_planks")
        S.put(cx, y - int(r) - 2, cz, "ashbound:moonglass_lamp")
        floor_disc(cx, y, cz, r + 0.6)
    wh = 4
    for x in range(math.floor(cx - r - 1), math.ceil(cx + r) + 2):
        for z in range(math.floor(cz - r - 1), math.ceil(cz + r) + 2):
            d = math.hypot(x - cx, z - cz)
            a = math.atan2(z - cz, x - cx)
            if d < r - 0.5:
                for yy in range(y + 1, y + wh + 1):
                    S.put(x, yy, z, None)
                S.put(x, y, z, "birch_planks")
            elif d <= r + 0.5:
                da = abs((a - door + math.pi) % (2 * math.pi) - math.pi)
                post = (a * 8 / (2 * math.pi)) % 1 < 0.2
                win = any(abs((a - door - (k + 1) * 2 * math.pi / (n_win + 1) + math.pi) % (2 * math.pi) - math.pi) < 0.22 for k in range(n_win))
                for yy in range(y + 1, y + wh + 1):
                    if da < 0.42 * 4 / max(r, 3) and yy <= y + 3:
                        S.put(x, yy, z, None)
                    elif post:
                        S.put(x, yy, z, PALEW)
                    elif win and y + 2 <= yy <= y + 3:
                        S.put(x, yy, z, H.PANE)
                    else:
                        S.put(x, yy, z, "birch_planks")
    Hr = r + 5
    dome = lambda k: (r + 1.4) * (1 + 0.25 * math.sin(math.pi * k / Hr * 0.8)) * (1 - (k / Hr) ** 1.5)
    for k in range(int(Hr) + 1):                                            # the dome, swelling a little then to a point
        rr = dome(k)
        inner = min(rr - 1.3, dome(k + 1) - 1.3)                            # reaching in under the ring above: no gaps
        for x in range(math.floor(cx - rr - 1), math.ceil(cx + rr) + 2):
            for z in range(math.floor(cz - rr - 1), math.ceil(cz + rr) + 2):
                d = math.hypot(x - cx, z - cz)
                if inner < d <= max(rr, 0.6):
                    st = roof
                    if k == 0 and S.rnd.random() < 0.35:
                        st = "ashbound:wildwood_leaves"
                    S.put(x, y + wh + 1 + k, z, st)
                elif d <= inner:
                    S.put(x, y + wh + 1 + k, z, None)
    S.put(cx, y + wh + 2 + int(Hr), cz, "lightning_rod[facing=up,powered=false,waterlogged=false]")
    S.put(cx, y + wh, cz, "ashbound:moonglass_lamp")
    out = (cx + math.cos(door) * (r + 1), cz + math.sin(door) * (r + 1))
    DOORS.append((out[0], y + 1, out[1]))
    return out


def flight(T, y0, y1, side, ground=False):
    """stairs from floor y0 up to floor y1 on one side of the trunk: one straight flight three wide along the bark (every
    step facing the same way, no winding), a landing at each end, a beam under every step, posts down to whatever is
    below, a rail on each side wherever it drops away; on the ground the foot comes down to the earth where it lands.
    Returns the foot landing's middle."""
    nx, nz = {"south": (0, 1), "west": (-1, 0), "north": (0, -1), "east": (1, 0)}[side]
    tx, tz = -nz, nx                                         # the way up: along the side
    up = {(1, 0): "east", (-1, 0): "west", (0, 1): "south", (0, -1): "north"}[(tx, tz)]
    s = int(math.ceil(T.Rmax((y0 + y1) // 2))) + 1
    at = lambda u, v: (T.cx + tx * u + nx * v, T.cz + tz * u + nz * v)
    if ground:                                               # start from the earth at the foot, not the trunk's floor
        y0 = gh(*at(-((y1 - y0) // 2) - 2, s + 1))
    H = y1 - y0
    u0 = -(H // 2)
    cells = {}
    for v in (s, s + 1, s + 2):
        for u in range(u0 - 3, u0):
            cells[at(u, v)] = (y0, "birch_planks")
        for i in range(1, H):
            cells[at(u0 + i - 1, v)] = (y0 + i, None)
        for u in range(u0 + H - 1, u0 + H + 2):
            cells[at(u, v)] = (y1, "birch_planks")
    step = "birch_stairs[facing=%s,half=bottom,shape=straight,waterlogged=false]" % up
    cells = {c: (y, st or step) for c, (y, st) in cells.items()}
    opn = lambda v: v is None or v == "air" or "light[" in v or v == FIREFLY or any(k in v for k in ("leaves", "blossom", CORE))
    for (x, z), (y, st) in cells.items():
        S.put(x, y, z, st)
        for yy in range(y + 1, y + 4):
            S.put(x, yy, z, None)
        if ground and y == y0:                               # the foot landing on the earth: solid down to it
            for yy in range(gh(x, z) + 1, y):
                S.put(x, yy, z, "stripped_birch_wood[axis=y]")
            G[(x, z)] = min(G[(x, z)], y)
        elif opn(S.get(x, y - 1, z)):
            S.put(x, y - 1, z, "stripped_birch_wood[axis=y]")
    if ground:                                               # a clear way up to the foot, cut through the roots
        for u in range(u0 - 10, u0 - 3):
            for v in (s, s + 1, s + 2):
                x, z = at(u, v)
                for yy in range(gh(x, z) + 1, gh(x, z) + 5):
                    if S.get(x, yy, z) not in (None, "air"):
                        S.put(x, yy, z, None)
    for i in range(0, H + 2, 4):                             # posts under the outer and inner edge, down to what's below
        for v in (s, s + 2):
            x, z = at(u0 + i - 1, v)
            y = cells.get((x, z), (y0, None))[0] - 2
            for yy in range(y, max(y - 48, gh(x, z)), -1):
                if not opn(S.get(x, yy, z)):
                    break
                S.put(x, yy, z, "stripped_birch_log[axis=y]")
    for (x, z), (y, st) in cells.items():                    # the rails: on the sides, and across the head if it's open
        for a, b in ((nx, nz), (-nx, -nz), (tx, tz)):
            q = (x + a, z + b)
            if q in cells or (a, b) == (tx, tz) and y != y1:
                continue
            if all(opn(S.get(q[0], yy, q[1])) for yy in (y - 1, y, y + 1)) and y - 1 > gh(*q):
                S.put(q[0], y, q[1], "stripped_birch_wood[axis=y]")
                S.put(q[0], y + 1, q[1], "birch_fence")
    FLIGHTS.append((y0, [at(u, s + 1) for u in range(u0 - 10 if ground else u0 - 3, u0 + H + 2)]))
    for (x, z), (y, st) in cells.items():
        CLEAR.update((x, yy, z) for yy in range(y + 1, y + 4))
    return at(u0 - 2, s + 1)


FLIGHTS = []    # each tree flight's middle line, foot to head: for the walk check
CLEAR = set()   # the headroom over the flights: whatever's built later (vines, boards) is taken out again


def keep_flights():
    for q in CLEAR:
        if S.get(*q) not in (None, "air"):
            S.put(*q, None)
def bridge(p, q, y):
    """a bridge from p to q on floor y: boards five wide, dead level so its rails run true, the boards running on into
    the decks at both ends (no seam, nothing to fall through); a lantern post each side at both ends. walk_rails()
    rails it with the decks."""
    dx, dz = q[0] - p[0], q[1] - p[1]
    D = math.hypot(dx, dz) or 1
    ux, uz = dx / D, dz / D
    nx, nz = -uz, ux
    surf = set()
    for i in range(int(-2.5 * 4), int((D + 2.5) * 4) + 1):
        sv = i / 4
        for k in range(-9, 10):
            w = k / 4
            if abs(w) <= 2.2:
                surf.add((int(math.floor(p[0] + 0.5 + ux * sv + nx * w)), int(math.floor(p[1] + 0.5 + uz * sv + nz * w))))
    soft = ("leaves", "blossom", "wildwood_wood", "fence", CORE)
    for (x, z) in surf:
        cur = S.get(x, y, z)
        if cur is None or any(k in cur for k in soft):
            S.put(x, y, z, "birch_planks")
        for yy in range(y + 1, y + 4):
            cur = S.get(x, yy, z)
            if cur and any(k in cur for k in soft):
                S.put(x, yy, z, None)
        BRIDGE.add((x, z))
    for sv in (0.5, D - 0.5):                                            # the lantern posts at either end
        for side in (-1, 1):
            x, z = int(math.floor(p[0] + 0.5 + ux * sv + nx * 2.0 * side)), int(math.floor(p[1] + 0.5 + uz * sv + nz * 2.0 * side))
            if (x, z) in surf and S.get(x, y + 1, z) is None:
                S.put(x, y + 1, z, "stripped_birch_log[axis=y]")
                S.put(x, y + 2, z, "stripped_birch_log[axis=y]")
                S.put(x, y + 3, z, "lantern[hanging=false,waterlogged=false]")


def walk_rails(levels):
    """one rail for every raised floor (decks, pod rings, bridges): a fence on each board at the edge of the walkable
    floor where the next cell is a real drop, corner gaps closed so the line is unbroken and nobody slips through;
    nothing where the floor meets a wall, a stair or another floor"""
    plank = ("birch_planks", "stripped_birch_log", "birch_slab", "stripped_birch_wood")
    opn = lambda v: v is None or v == "air" or "light[" in v or v == FIREFLY
    n = 0
    for y in levels:
        F = set()
        for (x, yy, z), v in list(S.B.items()):
            if yy == y and v.split("[")[0] in plank and opn(S.get(x, y + 1, z)) and opn(S.get(x, y + 2, z)):
                F.add((x, z))
        drop = lambda c: opn(S.get(c[0], y, c[1])) and opn(S.get(c[0], y - 1, c[1])) and opn(S.get(c[0], y + 1, c[1]))
        R = {c for c in F if any(drop((c[0] + a, c[1] + b)) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
        for (x, z) in list(R):                                           # close the diagonal gaps
            for a, b in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
                if (x + a, z + b) in R and (x + a, z) not in R and (x, z + b) not in R:
                    for c in ((x + a, z), (x, z + b)):
                        if c in F:
                            R.add(c)
                            break
        for (x, z) in R:
            if opn(S.get(x, y + 1, z)):
                S.put(x, y + 1, z, "birch_fence")
                n += 1
    print("  rails: %d fences" % n)


FIREFLY = "ashbound:fireflies"
N6 = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))


def _leafy(v):
    return v is not None and ("leaves" in v or "blossom" in v)


def leaf_cores():
    """leaves more than two deep turned to the clump's opaque core: nobody sees them, but the game draws every face of
    every leaf, so a canopy of solid leaf clouds is what made the tree crawl. Returns the outermost leaves."""
    B = S.B

    def covered(v):
        return v is not None and (_leafy(v) or v == CORE or "wildwood_wood" in v)
    leaves = [p for p, v in B.items() if _leafy(v)]
    d1 = {p for p in leaves if any(not covered(B.get((p[0] + a, p[1] + b, p[2] + c))) for a, b, c in N6)}
    d2 = {(p[0] + a, p[1] + b, p[2] + c) for p in d1 for a, b, c in N6} - d1
    n = 0
    for p in leaves:
        if p not in d1 and p not in d2:
            B[p] = CORE
            n += 1
    print("  leaves %d -> %d (%d turned to core)" % (len(leaves), len(leaves) - n, n))
    return d1


def glow(d1, lit=0.012):
    """the elves' tree after dark: froglights glowing in the leaves' undersides, glow lichen in patches on the bark,
    glow berries trailing under the boards, fireflies drifting over the floors, the glade and the pool"""
    B, rnd = S.B, S.rnd
    free = lambda q: B.get(q) is None and q[1] > gh(q[0], q[2]) and q not in CARVED
    n = dict(froglight=0, lichen=0, berries=0, fireflies=0)
    for (x, y, z) in d1:
        if free((x, y - 1, z)) and rnd.random() < lit:
            B[(x, y, z)] = S.pick(("pearlescent_froglight[axis=y]", 3), ("verdant_froglight[axis=y]", 2), ("ochre_froglight[axis=y]", 1))
            n["froglight"] += 1
            for k in range(2, 6):
                if rnd.random() < 0.25 and free((x, y - k, z)):
                    B[(x, y - k, z)] = FIREFLY
                    n["fireflies"] += 1
                    break
    for (x, y, z), v in list(B.items()):
        if "wildwood_wood" in v and noise(x + y * 0.7, z - y * 0.7, 5, 77) > 0.3 and rnd.random() < 0.3:
            for a, c, f in ((1, 0, "west"), (-1, 0, "east"), (0, 1, "north"), (0, -1, "south")):
                if free((x + a, y, z + c)):
                    B[(x + a, y, z + c)] = "glow_lichen[%s=true]" % f
                    n["lichen"] += 1
                    break
        elif v.split("[")[0] in ("birch_planks", "birch_slab", "stripped_birch_log", "stripped_birch_wood") and y > gh(x, z) + 5                 and rnd.random() < 0.05 and free((x, y - 1, z)) and free((x, y - 2, z)) and free((x, y - 3, z)):
            k = rnd.randint(1, 3)
            for d in range(1, k):
                B[(x, y - d, z)] = "cave_vines_plant[berries=%s]" % ("true" if rnd.random() < 0.6 else "false")
            B[(x, y - k, z)] = "cave_vines[age=25,berries=true]"
            n["berries"] += 1
    for (x, z), ys in DECK.items():
        for y in ys:
            if (x, y, z) not in RIM and rnd.random() < 0.03:
                q = (x, y + rnd.randint(2, 4), z)
                if free(q):
                    B[q] = FIREFLY
                    n["fireflies"] += 1
    for (x, z), g in G.items():
        r = math.hypot(x, z)
        if (x, z) in WET and rnd.random() < 0.05 or 18 < r < 105 and rnd.random() < 0.012:
            q = (x, max(g, WET.get((x, z), g)) + rnd.randint(1, 3), z)
            if free(q):
                B[q] = FIREFLY
                n["fireflies"] += 1
    print("  glow:", n)


def post_lantern(x, y, z, face):
    """an elf lantern hung from its curling bracket on a three-high birch post standing at (x, y, z): the lamp at head
    height, not down in the grass"""
    for k in range(3):
        S.put(x, y + k, z, "birch_fence")
    fx, fz = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}[face]
    PROPS.append(("elf_lantern", x + 0.5 + fx * 0.45, y + 1.05, z + 0.5 + fz * 0.45, YAW[face], 1.0))


def rails():
    for (x, y, z) in RIM:
        if (x, y, z) in GAPS or S.get(x, y + 1, z) not in (None, "air"):
            continue
        out = any(y not in DECK.get((x + a, z + b), ()) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if out:
            S.put(x, y + 1, z, "birch_fence")


# the tree village's three plans: the sister trees (bearing, distance, which floor they join), the pods on each floor,
# the glade's houses, the moon pool, the way in, the archers' ground, the Hollow's doors, the flights' sides
SEVEN = tuple(round(0.3 + k * 2 * math.pi / 7, 3) for k in range(7))
TREE = [
    dict(seed=5, accent="ashbound:wildwood_leaves_lilac", sisters=((0.2, 66, 1), (1.45, 64, 1), (2.6, 68, 2), (3.75, 64, 2), (5.05, 68, 1)),
         pods=((0.85, 2.4, 3.3, 4.2), (0.4, 1.6, 5.2), (2.0, 4.9)), glade=(0.55, 3.2, 4.25), pool=(40, 46), way=math.pi / 2,
         archery=math.pi - 0.15, hollows=(2.45, 5.6), flights=("south", "west", "north")),
    # a crescent of sisters to the east at two heights, the moon pool west, the way in from the west
    dict(seed=9, accent="ashbound:wildwood_leaves_rose", sisters=((5.0, 62, 1), (5.75, 72, 2), (0.35, 62, 1), (1.0, 72, 2), (1.7, 62, 1)),
         pods=((0.3, 1.9, 2.8, 4.6), (0.9, 2.9, 4.1), (1.5, 3.6)), glade=(2.5, 4.7), pool=(-50, -22), way=math.pi,
         archery=2.05, hollows=(4.4, 0.8), flights=("west", "north", "east")),
    # seven sisters in a full ring, all on the first floor and bridged one to the next, the way in from the east
    dict(seed=13, accent="ashbound:wildwood_leaves_lilac", sisters=tuple((a_, 60, 1) for a_ in SEVEN),
         pods=((0.75, 2.55, 4.34, 5.24), (1.6, 3.4, 0.2), (2.9, 5.6)), glade=(0.75, 2.55, 5.24), pool=(-33, -84), way=0.0,
         archery=3.44, hollows=(2.45, 1.2), flights=("north", "east", "south")),
]


def tree():
    import vplan
    new(57)
    V_ = TREE[VAR % 3]
    DECK.clear()
    FLIGHTS.clear()
    CLEAR.clear()
    RIM.clear()
    GAPS.clear()
    BRIDGE.clear()
    PX, PZ = V_["pool"]                                                   # the moon pool

    def hf(x, z):
        h = 1.6 + 1.0 * noise(x, z, 22, 61) + 0.5 * noise(x, z, 7, 62)
        d = math.hypot(x - PX, z - PZ) + 2 * noise(x, z, 5, 63)
        if d < 12:
            h = min(h, -2.2 + max(0.0, d - 5) * 0.75)
        return h

    box = (-120, -120, 120, 120)
    land(*box, hf, water=0, bed=(("mud", 2), ("gravel", 2), ("clay", 1)))
    gy = gh(0, 0)
    P = vplan.Plan(sys.modules[__name__], box, (0, 0), rings=(25, 95, 115), cap=24)
    # the great tree: its trunk 26 across at the roots, its crown 90 up
    T = ETree(0, 0, gy, 15.0, gy + 92, limbs=8, limb_y=gy + 68, reach=46, seed=V_["seed"], accent=V_["accent"], roots=8)
    for x in range(-36, 37):
        for z in range(-36, 37):
            if any(S.get(x, yy, z) and "wildwood_wood" in S.get(x, yy, z) for yy in (gh(x, z) + 1, gh(x, z) + 2)):
                P.occ[(x, z)] = "landmark"
    # its three floors, each a ring of boards, a straight flight up the trunk's side between each
    L1, L2, L3 = gy + 20, gy + 36, gy + 52
    ro1 = deck(T, L1, 9, 71)
    ro2 = deck(T, L2, 8, 72)
    ro3 = deck(T, L3, 7, 73)
    f1, f2, f3 = V_["flights"]
    sx, sz = flight(T, gy, L1, f1, ground=True)
    flight(T, L1, L2, f2)
    flight(T, L2, L3, f3)
    # the houses on the floors, each on its own bulge of the ring, doors toward the trunk
    homes = 0
    SIS = tuple((a_, D, (L1, L2)[f - 1]) for a_, D, f in V_["sisters"])
    PODS = ((L1, ro1, V_["pods"][0], 4.5), (L2, ro2, V_["pods"][1], 4), (L3, ro3, V_["pods"][2], 3.5))
    for L, ro, angs, r in PODS:
        for a_ in angs:
            d = ro(a_) + r - 0.5
            cx, cz = int(round(math.cos(a_) * d)), int(round(math.sin(a_) * d))
            pod(cx, L, cz, r, a_ + math.pi, roof=S.pick(("ashbound:green_roof_tiles", 3), ("ashbound:blue_roof_tiles", 1)))
            limb([(math.cos(a_) * T.R(L - 9), L - 9, math.sin(a_) * T.R(L - 9)), (cx, L - 1.5, cz)], 0.8, 0.6, "stripped_birch_wood[axis=y]")
            for k in range(-1, 2):
                rr = ro(a_) - 0.5
                GAPS.add((int(round(math.cos(a_ + k * 0.08) * rr)), L, int(round(math.sin(a_ + k * 0.08) * rr))))
            homes += 1
    # two pods hung from the limbs, a bridge to each from the top floor
    taken = [a_ for L, _, angs, _ in PODS[1:] for a_ in angs] + [a_ for a_, _, L in SIS if L == L2]
    sep = lambda a_: min(abs((a_ - b + math.pi) % (2 * math.pi) - math.pi) for b in taken)
    hung = sorted(range(len(T.ends)), key=lambda k: -sep(T.ends[k][0]))[:2]
    print("hung at", [round(T.ends[k][0], 2) for k in hung], [round(sep(T.ends[k][0]), 2) for k in hung])
    for k in hung:
        la, e = T.ends[k]
        d = ro3(la) + 9
        cx, cz = int(round(math.cos(la) * d)), int(round(math.sin(la) * d))
        door = pod(cx, L3, cz, 3, la + math.pi, roof="ashbound:green_roof_tiles", hang=True, n_win=4)
        yy = L3 + 14
        while yy < L3 + 50 and S.get(cx, yy, cz) in (None, "air", "lightning_rod[facing=up,powered=false,waterlogged=false]"):
            S.put(cx, yy, cz, "chain[axis=y,waterlogged=false]")
            yy += 1
        bridge((math.cos(la) * (ro3(la) - 1), math.sin(la) * (ro3(la) - 1)), door, L3)
        homes += 1
    # the sister trees round it, a floor on each at the great tree's first or second floor, bridges across
    sisters = []
    for k, (a_, D, L) in enumerate(SIS):
        x, z = int(round(math.cos(a_) * D)), int(round(math.sin(a_) * D))
        ty = gh(x, z)
        t = ETree(x, z, ty, 4.5, L + 21, limbs=4, limb_y=L + 10, reach=19, seed=80 + k, roots=5,
                  accent="ashbound:wildwood_leaves_rose" if k % 2 else None)
        ros = deck(t, L, 4, 90 + k)
        pa = a_ + math.pi + 0.9 * (1 if k % 2 else -1)
        d = ros(pa) + 3
        pod(int(round(x + math.cos(pa) * d)), L, int(round(z + math.sin(pa) * d)), 3, pa + math.pi)
        homes += 1
        ro = ro1 if L == L1 else ro2
        p = (math.cos(a_) * (ro(a_) - 1), math.sin(a_) * (ro(a_) - 1))
        q = (x - math.cos(a_) * (ros(a_ + math.pi) - 1), z - math.sin(a_) * (ros(a_ + math.pi) - 1))
        bridge(p, q, L)
        sisters.append((x, z, L, t, ros))
        for xx in range(x - 11, x + 12):
            for zz in range(z - 11, z + 12):
                if math.hypot(xx - x, zz - z) < 11:
                    P.occ[(xx, zz)] = "landmark"
    for i in range(len(sisters)):                                         # the sisters joined where they share a floor
        x, z, L, t, ros = sisters[i]
        x2, z2, L2_, t2, ros2 = sisters[(i + 1) % len(sisters)]
        if L == L2_:
            a_ = math.atan2(z2 - z, x2 - x)
            bridge((x + math.cos(a_) * (ros(a_) - 1), z + math.sin(a_) * (ros(a_) - 1)),
                   (x2 - math.cos(a_) * (ros2(a_ + math.pi) - 1), z2 - math.sin(a_) * (ros2(a_ + math.pi) - 1)), L)
    # the Hollow: a room carved into the great tree's foot, its arched door to the south-west, round windows
    for a_ in V_["hollows"]:
        c, s_ = math.cos(a_), math.sin(a_)
        hr = 4.5
        hx, hz = c * (T.R(gy + 2) - hr - 0.5), s_ * (T.R(gy + 2) - hr - 0.5)
        for x in range(math.floor(hx - hr), math.ceil(hx + hr) + 1):
            for z in range(math.floor(hz - hr), math.ceil(hz + hr) + 1):
                if math.hypot(x - hx, z - hz) <= hr:
                    S.put(x, gy, z, "birch_planks")
                    for yy in range(gy + 1, gy + 6 - (1 if math.hypot(x - hx, z - hz) > hr - 1 else 0)):
                        S.put(x, yy, z, None)
        S.put(int(round(hx)), gy + 5, int(round(hz)), "ashbound:moonglass_lamp")
        for t in range(0, int(T.Rmax(gy) + 6)):
            x, z = int(round(hx + c * t)), int(round(hz + s_ * t))
            for w in (-1, 0, 1):
                xx, zz = x + int(round(-s_ * w)), z + int(round(c * w))
                for yy in range(gy + 1, gy + (4 if w else 5)):
                    if S.get(xx, yy, zz) and "wildwood_wood" in S.get(xx, yy, zz):
                        S.put(xx, yy, zz, None)
        homes += 1
    # the glade: the way in from the south under the arch, a ring path round the roots, the moon pool, the archers
    RR = 42
    wa = V_["way"]                                                        # the way in: from the glade's edge on this bearing
    wx, wz = math.cos(wa), math.sin(wa)
    road = P.route((int(wx * 118), int(wz * 118)), (int(wx * (RR + 1)), int(wz * (RR + 1))))
    FOCUS["tree"] = (int(wx * 100), int(wz * 100))
    P.road(road, 1.3)
    ring = [(math.cos(t / 240 * 2 * math.pi) * RR, math.sin(t / 240 * 2 * math.pi) * RR) for t in range(241)]
    P.road(ring, 1.0, "lane")
    line = lambda a, b: [(a[0] + (b[0] - a[0]) * i / (2 * math.dist(a, b)), a[1] + (b[1] - a[1]) * i / (2 * math.dist(a, b)))
                         for i in range(int(2 * math.dist(a, b)) + 1)]
    aa = V_["archery"]
    for to in ((PX - 9, PZ - 9), (math.cos(aa) * 58, math.sin(aa) * 58), (sx, sz)) + tuple((math.cos(h_) * 20, math.sin(h_) * 20) for h_ in V_["hollows"]):
        a_ = math.atan2(to[1], to[0])
        P.road(line((math.cos(a_) * RR, math.sin(a_) * RR), to), 0.9, "lane")
    for (x, z), t in list(P.occ.items()):
        if t == "road" and (x, z) not in WET:
            y = gh(x, z)
            if S.get(x, y + 1, z) is None:
                S.put(x, y, z, S.pick(("dirt_path", 5), ("moss_block", 2), ("ashbound:pale_limestone", 1)))
    out_face = ("east" if wx > 0 else "west") if abs(wx) > abs(wz) else ("south" if wz > 0 else "north")
    ax_, az_ = int(round(wx * 84)), int(round(wz * 84))
    prop("elf_arch", ax_, gh(ax_, az_) + 1, az_, out_face)
    P.occ[(ax_, az_)] = "clutter"
    for k, (x, z) in enumerate(road[::14][1:6]):
        side = 2 if k % 2 else -2
        ox, oz = (side, 0) if abs(wz) >= abs(wx) else (0, side)          # beside the road, facing it
        f_ = {(1, 0): "west", (-1, 0): "east", (0, 1): "north", (0, -1): "south"}[(ox // 2, oz // 2)]
        if k < 2:
            prop("elf_banner", int(x) + ox, gh(int(x) + ox, int(z) + oz) + 1, int(z) + oz, f_)
        else:
            post_lantern(int(x) + ox, gh(int(x) + ox, int(z) + oz) + 1, int(z) + oz, f_)
    prop("moon_basin", PX - 9, gh(PX - 9, PZ - 7) + 1, PZ - 7, "south")
    for (x, z), wy in list(WET.items()):
        if S.rnd.random() < 0.06:
            S.put(x, 1, z, "lily_pad")
    ux, uz = math.cos(aa), math.sin(aa)                                   # the archers' ground, the butts facing in
    inward = ("west" if ux > 0 else "east") if abs(ux) > abs(uz) else ("north" if uz > 0 else "south")
    for k in range(2):
        x, z = int(ux * 66 - uz * (k * 8 - 4)), int(uz * 66 + ux * (k * 8 - 4))
        prop("archery_butts", x, gh(x, z) + 1, z, inward)
    x, z = int(ux * 52 - uz * 10), int(uz * 52 + ux * 10)
    prop("herb_rack", x, gh(x, z) + 1, z, inward)
    x, z = int(ux * 54 + uz * 8), int(uz * 54 - ux * 8)
    prop("elf_banner", x, gh(x, z) + 1, z, inward)
    # three houses down on the glade, at the foot of the roots, each with its herb rack
    for a_ in V_["glade"]:
        x, z = int(math.cos(a_) * 54), int(math.sin(a_) * 54)
        y = max(gh(x + a, z + b) for a in (-4, 0, 4) for b in (-4, 0, 4))
        for xx in range(x - 6, x + 7):
            for zz in range(z - 6, z + 7):
                if math.hypot(xx - x, zz - z) <= 5.6:
                    for yy in range(gh(xx, zz), y):
                        S.put(xx, yy, zz, "ashbound:pale_limestone")
                    P.occ[(xx, zz)] = "house"
        pod(x, y, z, 3.5, a_ + math.pi)
        hx, hz = int(x + math.cos(a_ + 1.2) * 7), int(z + math.sin(a_ + 1.2) * 7)
        prop("herb_rack", hx, gh(hx, hz) + 1, hz, "north")
        homes += 1
    # what hangs off the floors: lanterns on the rims, chimes under the boards, banners at the stair heads
    rim = sorted(RIM)
    for i, (x, y, z) in enumerate(rim):
        if i % 23 == 0 and (x, y, z) not in GAPS and S.get(x, y + 2, z) in (None, "air"):
            a_ = math.atan2(z, x) + math.pi
            post_lantern(x, y + 1, z, ("east" if math.cos(a_) > 0 else "west") if abs(math.cos(a_)) > abs(math.sin(a_)) else ("south" if math.sin(a_) > 0 else "north"))
        elif i % 53 == 7:
            prop("wind_chimes", x, y - 2.0, z, "north")
    for L in (L1, L2, L3):
        x, z = int(math.cos(0.15) * (T.Rmax(L) + 1.5)), int(math.sin(0.15) * (T.Rmax(L) + 1.5))
        prop("elf_banner", x, L + 1, z, "east")
    keep_flights()
    walk_rails((L1, L2, L3))
    P.woods(40, names=("highwood_0", "highwood_3", "highwood_5", "highwood_7", "highwood_9", "highwood_11", "oak_medium_0", "oak_medium_1"))
    for _ in range(40):
        x, z = S.rnd.randint(-90, 90), S.rnd.randint(-90, 90)
        if 30 < math.hypot(x, z) < 90 and P.occ.get((x, z)) is None and (x, z) not in WET:
            lay_tree("bush_%d" % S.rnd.randint(0, 7), x, z, k=S.rnd.randint(0, 3))
            P.occ[(x, z)] = "tree"
    scatter(900, *box, lambda x, z: S.put(x, gh(x, z) + 1, z, S.pick(("short_grass", 8), ("fern", 3), ("allium", 1), ("azure_bluet", 1),
                                                                      ("lily_of_the_valley", 1), ("cornflower", 1))),
            clear=lambda x, z: P.occ.get((x, z)) is None, tries=3000)
    finish()
    glow(leaf_cores())
    keep_flights()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "renders", "villages")
    os.makedirs(out, exist_ok=True)
    P.plan_png(os.path.join(out, "plan_%s.png" % out_name("tree")))
    print("homes", homes, "top", T.top, "floors", L1, L2, L3)
    b0 = sisters[0]
    return {"wide": ((50, 72, 215), (0, 58, 0), 22),
            "glade": ((-26, gy + 5, 98), (0, gy + 38, 0), 20),
            "floor": ((math.cos(0.2) * (ro1(0.2) - 4), L1 + 2.8, math.sin(0.2) * (ro1(0.2) - 4)), (b0[0], L1 + 5, b0[1]), 20),
            "bridges": ((125, L1 + 40, -85), (0, L1 + 18, 0), 22),
            "stairs": ((22, gy + 12, 48), (-2, gy + 10, 18), 26), "stairs2": ((-48, L1 + 8, 26), (-18, L1 + 8, 0), 26)}


# ================================================================ Anvilgate: the dwarves' hold

DSTONE = (("deepslate_bricks", 6), ("polished_deepslate", 2), ("deepslate_tiles", 1))
DIRS = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}


def cardinal(dx, dz):
    return ("east" if dx > 0 else "west") if abs(dx) > abs(dz) else ("south" if dz > 0 else "north")


def dfurnish(cell, y0, hw, D, dd, face):
    """a dwarf home's room: the box bed in a back corner, the hearth opposite with its hood up into the chimney and
    the anvil by it, casks along the back, a chest, a table with a candle and two stools on a rug, barrels by the door"""
    fx, fz = DIRS[face]
    inward, right, left = cardinal(-fx, -fz), cardinal(-fz, fx), cardinal(fz, -fx)
    I0, I1 = -hw + 1, hw - 1
    used = {(dd, 1), (dd, 2)}

    def put(i, j, st, dy=1):
        x, z = cell(i, j)
        S.put(x, y0 + dy, z, st)
        used.add((i, j))
    bed = S.rnd.choice(("red_bed", "brown_bed", "orange_bed", "blue_bed", "green_bed"))
    put(I0, D - 1, "%s[facing=%s,occupied=false,part=head]" % (bed, inward))
    put(I0, D - 2, "%s[facing=%s,occupied=false,part=foot]" % (bed, inward))
    put(I1, D - 1, "furnace[facing=%s,lit=true]" % face)
    for dy in (2, 3, 4):
        put(I1, D - 1, "polished_deepslate" if dy < 4 else "chiseled_deepslate", dy)
    if I1 - 1 > I0:
        put(I1 - 1, D - 1, "anvil[facing=%s]" % right)
    for i in range(I0 + 1, I1 - 1):
        put(i, D - 1, "ashbound:cask_rack[facing=%s]" % face)
    if D - 3 >= 2:
        put(I0, D - 3, "chest[facing=%s,type=single,waterlogged=false]" % right)
    tj = max(2, D // 2)
    for ti in sorted(range(I0 + 1, I1), key=abs):
        if all((ti + k, tj) not in used for k in (-1, 0, 1)) and ti - 1 >= I0 and ti + 1 <= I1:
            for i in range(ti - 1, ti + 2):                                # the rug under it all
                for j in (tj - 1, tj, tj + 1):
                    if (i, j) not in used and j >= 1:
                        x, z = cell(i, j)
                        S.put(x, y0 + 1, z, "red_carpet" if i == ti and j == tj else "brown_carpet")
            put(ti, tj, "dark_oak_slab[type=top,waterlogged=false]")
            put(ti, tj, "candle[candles=%d,lit=true,waterlogged=false]" % S.rnd.randint(1, 3), 2)
            put(ti - 1, tj, H.stairs("dark_oak", left))
            put(ti + 1, tj, H.stairs("dark_oak", right))
            break
    for i in (I0, I1):                                                     # barrels and a workbench by the door
        if (i, 1) not in used and abs(i - dd) > 1:
            put(i, 1, "barrel[facing=up,open=false]")
            put(i, 1, S.pick(("barrel[facing=%s,open=false]" % inward, 2), ("crafting_table", 1), ("decorated_pot[cracked=false,facing=%s,waterlogged=false]" % face, 1)), 2)
    x, z = cell(I0, D - 2)
    S.put(x, y0 + 4, z, "lantern[hanging=true,waterlogged=false]")


def dhouse(cx, cz, face, y0, w, D=6, porch=False, P=None):
    """a dwarf's home dug into a terrace's riser: only its stone front shows, pilasters at the corners, a slab eave,
    a lamp over the door, the chimney poking up through the turf behind; returns the cell in front of its door"""
    fx, fz = DIRS[face]
    tx, tz = -fz, fx
    hw = w // 2
    cell = lambda i, j: (cx + tx * i - fx * j, cz + tz * i - fz * j)
    dd = S.rnd.choice([d for d in range(-hw + 2, hw - 1)] or [0])
    for i in range(-hw, hw + 1):
        for j in range(0, D + 1):
            x, z = cell(i, j)
            wall = j in (0, D) or abs(i) == hw
            S.put(x, y0, z, "polished_deepslate")
            for y in range(y0 + 1, y0 + 5):
                S.put(x, y, z, S.pick(*DSTONE) if wall else None)
            S.put(x, y0 + 5, z, "deepslate_tiles")
            if P:
                P.occ[(x, z)] = "house"
    for i in range(-hw - 1, hw + 2):                                     # the front: the yard before it cleared, the eave
        for j in range(-3, 0):
            x, z = cell(i, j)
            for y in range(y0 + 1, y0 + 6):
                S.put(x, y, z, None)
            if gh(x, z) > y0:
                S.put(x, y0, z, GRASS)
        x, z = cell(i, -1)
        S.put(x, y0 + 5, z, "deepslate_brick_slab[type=top,waterlogged=false]")
        x, z = cell(i, 0)
        S.put(x, y0 + 6, z, "deepslate_brick_wall" if abs(i) <= hw else None)
    for i in (-hw, hw):                                                    # the corner pilasters
        x, z = cell(i, -1)
        for y in range(y0, y0 + 5):
            S.put(x, y, z, "polished_deepslate" if y < y0 + 4 else "chiseled_deepslate")
        S.put(x, y0 + 5, z, "ashbound:gilded_trim" if w >= 8 else "polished_blackstone_bricks")
    x, z = cell(dd, 0)                                                     # the door and its lamp
    inward = cardinal(-fx, -fz)
    S.put(x, y0 + 1, z, "dark_oak_door[facing=%s,half=lower,hinge=left,open=false,powered=false]" % inward)
    S.put(x, y0 + 2, z, "dark_oak_door[facing=%s,half=upper,hinge=left,open=false,powered=false]" % inward)
    S.put(x, y0 + 3, z, "polished_blackstone_bricks")
    lx, lz = cell(dd, -1)
    S.put(lx, y0 + 4, lz, "lantern[hanging=true,waterlogged=false]")
    for i in range(-hw + 1, hw):                                           # windows either side
        if abs(i - dd) >= 2 and abs(i) <= hw - 1 and (i - dd) % 3 == 0:
            x, z = cell(i, 0)
            S.put(x, y0 + 2, z, H.PANE)
            S.put(x, y0 + 3, z, H.PANE)
    x, z = cell(hw - 1, D - 1)                                             # the chimney
    for y in range(y0 + 6, y0 + 9):
        S.put(x, y, z, "deepslate_bricks")
    S.put(x, y0 + 9, z, "campfire[facing=north,lit=true,signal_fire=false,waterlogged=false]")
    ix, iz = cell(0, D // 2)
    S.put(ix, y0 + 4, iz, "lantern[hanging=true,waterlogged=false]")
    dfurnish(cell, y0, hw, D, dd, face)
    if porch:                                                              # a copper-roofed porch on two stone posts
        for i in range(-hw + 1, hw):
            for j in range(-3, 0):
                x, z = cell(i, j)
                S.put(x, y0, z, "polished_deepslate")
                S.put(x, y0 + 4, z, "weathered_cut_copper_slab[type=bottom,waterlogged=false]")
        for i in (-hw + 1, hw - 1):
            x, z = cell(i, -3)
            for y in range(y0 + 1, y0 + 4):
                S.put(x, y, z, "polished_deepslate_wall")
    fx_, fz_ = cell(dd, -2)
    DOORS.append((fx_, y0 + 1, fz_))
    return cell(dd, -2)


# the hold's three plans: the yard's radius, each terrace's depth and rise, how many; how far the face bows round the
# yard; which side the falls come down (the mine opposite); the way in's bearing
HOLD = [
    dict(r0=24, dr=10, step=6, n=5, bow=0.006, m=1, ga=math.pi / 2),
    dict(r0=19, dr=8, step=8, n=5, bow=0.011, m=-1, ga=math.pi / 2 + 0.6),     # deep and narrow, steep terraces
    dict(r0=30, dr=13, step=5, n=4, bow=0.003, m=1, ga=math.pi / 2 - 0.6),     # wide and shallow, broad terraces
]


def hold():
    import vplan
    new(77)
    V_ = HOLD[VAR % 3]
    R0, DR, STEP, NT = V_["r0"], V_["dr"], V_["step"], V_["n"]          # the yard's edge, each terrace's depth and rise, how many
    m, GA = V_["m"], V_["ga"]                                              # which side the falls are, the way in's bearing
    zc = lambda x: -26 - V_["bow"] * x * x                                 # the cliff's foot, bowed round the yard
    gap = lambda a: abs((a - GA + math.pi) % (2 * math.pi) - math.pi)

    def terr(x, z):
        r = math.hypot(x, z)
        if r < R0:
            return 0.0
        k = min(NT, int((r - R0) / DR) + 1)
        h = STEP * k + (r - R0 - NT * DR) * 0.6 + 4 * noise(x, z, 12, 9) if r > R0 + NT * DR else STEP * k
        return h

    def hf(x, z):
        a = math.atan2(z, x)
        h = terr(x, z)
        north = abs((a + math.pi / 2 + math.pi) % (2 * math.pi) - math.pi)
        g = min(1.0, max(0.0, (gap(a) - 0.45) / 0.3), max(0.0, (north - 0.7) / 0.3))
        h = h * g + (0.4 * noise(x, z, 9, 3)) * (1 - g)
        if z < zc(x):                                                      # the mountain's face, sheer, then its slopes
            d = zc(x) - z
            h = max(h, 30 + min(d, 5) * 2 + max(0.0, d - 5) * 0.9 + 5 * noise(x, z, 10, 4) + 10 * noise(x, z, 30, 5) +
                    30 * max(0.0, noise(x, z, 45, 6)))
            if zc(x) - z < 2:
                h = max(h, 30)
        return h

    box = (-95, -95, 95, 95)
    land(*box, hf, rock=("stone", "andesite", "stone", "tuff"), steep=3)
    P = vplan.Plan(sys.modules[__name__], box, (0, 0), rings=(R0, 60, 90), cap=26)
    for x in range(-95, 96):                                               # the mountain solid behind its face (the mine, the shaft)
        for z in range(-95, int(zc(x)) + 1):
            if zc(x) - z < 14:
                for y in range(-1, gh(x, z)):
                    if S.get(x, y, z) is None:
                        S.put(x, y, z, S.pick(("stone", 3), ("andesite", 1)))
    for (x, z), g in list(G.items()):                                     # the terraces' risers dressed as walls
        r = math.hypot(x, z)
        if not (R0 - 1 <= r <= R0 + NT * DR + 1) or z <= zc(x) + 1:
            continue
        lo = min(G.get((x + a, z + b), g) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if g - lo >= 3:
            for y in range(lo + 1, g):
                S.put(x, y, z, S.pick(("stone_bricks", 6), ("mossy_stone_bricks", 2), ("cracked_stone_bricks", 1)))
            S.put(x, g, z, "polished_andesite")
    # the yard: rings of dark paving round the great forge
    for x in range(-R0, R0 + 1):
        for z in range(-R0, R0 + 1):
            r = math.hypot(x, z)
            if r < R0 - 0.5 and z > zc(x):
                S.put(x, 0, z, "polished_deepslate" if int(r) % 5 in (0, 1) else S.pick(("deepslate_tiles", 3), ("stone_bricks", 1)))
                if int(r) == 4 and (x + z) % 4 == 0:
                    S.put(x, 0, z, "ashbound:gold_inlay")
                P.occ[(x, z)] = "focus"
    for x in range(-3, 4):                                                 # the forge's hearth stone and its stack
        for z in range(-3, 4):
            if math.hypot(x, z) <= 3.2:
                S.put(x, 1, z, "polished_deepslate" if math.hypot(x, z) > 2.2 else "deepslate_tiles")
    for y in range(2, 13):
        for x, z in ((-1, -1), (0, -1), (1, -1)):
            S.put(x, y, z - 1, "deepslate_bricks" if y % 4 else "polished_blackstone_bricks")
    S.put(0, 13, -2, "campfire[facing=north,lit=true,signal_fire=true,waterlogged=false]")
    prop("forge_anvil", 0, 2, 1, "south")
    for k in range(6):
        a = k * math.pi / 3 + 0.5
        prop("stone_brazier", int(round(math.cos(a) * 7)), 1, int(round(math.sin(a) * 7)), "north")
    for nm, x, z, f in (("tool_rack", -6, -10, "south"), ("ale_cask", 9, 12, "west"), ("ale_cask", 11, 9, "west"),
                        ("tool_rack", 5, -12, "south"), ("ore_pile", -14, -6, "east")):
        prop(nm, x, gh(x, z) + 1, z, f)
        P.occ[(x, z)] = "clutter"
    # the great gate carved in the face: three stepped orders, pillars with gold capitals, a band of runes, the door
    gz = int(zc(0))
    for x in range(-13, 14):                                               # the dressed surround in the living rock
        for z in range(gz - 6, gz + 1):
            for y in range(0, 26):
                S.put(x, y, z, S.pick(*DSTONE) if z == gz or S.get(x, y, z) is None else S.get(x, y, z))
    ORD = ((9, 20, "polished_deepslate"), (7.5, 18, "deepslate_tiles"), (6, 16, "polished_blackstone_bricks"))
    for k, (hw, T, mat) in enumerate(ORD):                                 # three orders stepping in, shouldered tops
        z = gz - k
        opening = lambda x, y: abs(x) <= hw and 1 <= y <= T - max(0.0, abs(x) - (hw - 3))
        for x in range(-11, 12):
            for y in range(0, 23):
                if opening(x, y):
                    S.put(x, y, z, None)
                elif any(opening(x + a, y + b) for a in (-1, 0, 1) for b in (-1, 0, 1)) and y >= 1:
                    S.put(x, y, z, mat)
                elif k == 0 and y == 0 and abs(x) <= hw:
                    S.put(x, y, z, "polished_deepslate")
    hw, T, _ = ORD[-1]
    for z in (gz - 3, gz - 4):                                             # the porch inside, to the door
        for x in range(-6, 7):
            for y in range(1, T + 1 - max(0, abs(x) - 3)):
                S.put(x, y, z, None)
            S.put(x, 0, z, "deepslate_tiles")
    S.put(0, T + 2, gz, "ashbound:gold_frieze")
    for x in range(-8, 9):
        S.put(x, 0, gz - 5, "deepslate_tiles")
    for sx in (-1, 1):                                                     # the pillars stood out from the face
        for x in (sx * 9, sx * 10, sx * 11):
            for z in range(gz + 1, gz + 4):
                for y in range(0, 25):
                    st = "polished_deepslate"
                    if y in (4, 21):
                        st = "ashbound:gilded_trim"
                    elif y >= 22:
                        st = "chiseled_deepslate"
                    elif y in (10, 13, 16) and z == gz + 3 and x == sx * 10:
                        st = "ashbound:rune_glow"
                    S.put(x, y, z, st)
            S.put(x, 25, gz + 2, "deepslate_tile_slab[type=bottom,waterlogged=false]")
        prop("stone_brazier", sx * 10, 25, gz + 2, "north")
        PROPS[-1] = PROPS[-1][:5] + (1.6,)
    for x in range(-12, 13):                                               # the rune band over it all
        S.put(x, 23, gz, "ashbound:rune_glow" if x % 4 == 0 else "ashbound:rune_band")
        S.put(x, 24, gz + 1, "deepslate_tile_slab[type=bottom,waterlogged=false]")
    for x in (-8, -4, 0, 4, 8):                                            # the halls' windows above
        for y in range(27, 33):
            S.put(x, y, gz, None)
            S.put(x, y, gz - 1, "ashbound:rune_glow" if y in (29, 30) else "polished_blackstone_bricks")
        S.put(x, 33, gz, "chiseled_deepslate")
    PROPS.append(("rune_door", 0.5, 1, gz - 3.2, 180, 2.5))
    for x in range(-8, 9):
        for z in range(gz + 1, gz + 6):
            S.put(x, 0, z, "polished_deepslate" if abs(x) < 6 else "deepslate_tiles")
            P.occ[(x, z)] = "landmark"
    # the falls: down a notch east of the gate, a pool at the foot, a stone channel across the yard and away south
    fx = 20 * m
    fz = int(zc(fx))
    for x in (fx, fx + 1):
        for y in range(-1, gh(x, fz - 2) + 1):
            S.put(x, y, fz, "water[level=0]#flow")
            S.put(x, y, fz - 1, S.pick(*DSTONE))
            S.put(x, y, fz + 1, None)
    # its channel: straight out from the foot across the yard, then beside the way in and out through the gap
    gx_, gz_ = math.cos(GA), math.sin(GA)
    qs = [(gx_ * (R0 + 12) + side * 7 * -gz_, gz_ * (R0 + 12) + side * 7 * gx_) for side in (-1, 1)]
    q = min(qs, key=lambda p_: math.dist(p_, (fx + 0.5, 4)))
    far = (q[0] + gx_ * 140, q[1] + gz_ * 140)
    chan = [(fx + 0.5, fz + 2)] + [(fx + 0.5, z) for z in range(fz + 3, 4)]
    for a_, b_ in (((fx + 0.5, 4), q), (q, far)):
        n_ = int(math.dist(a_, b_) * 2)
        chan += [(a_[0] + (b_[0] - a_[0]) * i / n_, a_[1] + (b_[1] - a_[1]) * i / n_) for i in range(1, n_ + 1)]
    chan = [(x, z) for (x, z) in chan if -96 < x < 96 and -96 < z < 96]
    wet = set()
    for (x, z) in chan:
        for dx in (-1, 0, 1):
            for dz in ((-1, 0, 1) if z > 4 else (0,)):
                wet.add((int(math.floor(x)) + dx, int(math.floor(z)) + dz))
    for (x, z) in wet:
        S.put(x, -2, z, "gravel")
        S.put(x, -1, z, "water[level=0]")
        for y in range(0, gh(x, z) + 1):
            S.put(x, y, z, None)
        WET[(x, z)] = -1
        P.occ[(x, z)] = "water"
    for (x, z) in wet:
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, z + dz)
            if q not in wet:
                S.put(q[0], -1, q[1], "stone_bricks")
                S.put(q[0], 0, q[1], "polished_deepslate" if math.hypot(*q) < R0 else "stone_bricks")
                if gh(*q) > 0 and math.hypot(*q) >= R0:
                    for y in range(1, gh(*q) + 1):
                        S.put(q[0], y, q[1], "stone_bricks")
    for zb in (-6, 16):                                                    # slab bridges over it
        at_ = [x for (x, z) in chan if int(math.floor(z)) == zb]
        if not at_ or math.hypot(at_[0], zb) > R0 - 2:
            continue
        for x in range(int(at_[0]) - 3, int(at_[0]) + 4):
            for z in (zb, zb + 1):
                S.put(x, 0, z, "deepslate_tiles")
    prop("water_wheel", fx, 1.8, 1, 90)
    # the mine: a timbered mouth in the face to the west, rails out to the ore yard, carts and heaps
    mx = -22 * m
    mz = int(zc(mx))
    for x in range(mx - 2, mx + 3):
        for z in range(mz - 8, mz + 1):
            for y in range(1, 5):
                S.put(x, y, z, None)
            S.put(x, 0, z, "gravel")
        for y in range(1, 6):
            S.put(x, y, mz + 1, None)
    for x in (mx - 2, mx + 2):
        for y in range(1, 5):
            S.put(x, y, mz + 1, "stripped_spruce_log[axis=y]")
    for x in range(mx - 3, mx + 4):
        S.put(x, 5, mz + 1, "stripped_spruce_log[axis=x]")
    for k in range(9):
        z = mz - 6 + k * 3
        PROPS.append(("rails", mx + 0.5, 0.95 if z <= mz else 1.0, z + 0.5, 0, 1.0))
        P.occ[(mx, z)] = "road"
    prop("mine_cart", mx, 1, mz - 2, "south")
    prop("mine_cart", mx, 1, mz + 9, "south")
    prop("ore_pile", mx + 3, 1, mz + 5, "east")
    prop("ore_pile", mx - 3, 1, mz + 13, "west")
    prop("tool_rack", mx - 4, 1, mz + 3, "east")
    # the lift up the face to the lookout gallery, the crane over it
    lx = 9 * m
    lz = int(zc(lx)) + 2
    lz -= 2
    for x in range(lx - 2, lx + 3):                                        # its shaft cut in the face, framed in tiles
        for z in range(lz - 2, lz + 2):
            for y in range(1, 41):
                S.put(x, y, z, None if abs(x - lx) < 2 and z > lz - 2 else "deepslate_tiles")
            S.put(x, 0, z, "polished_deepslate")
    prop("lift_cage", lx, 1, lz, "south")
    for x in range(lx - 5, lx + 8):
        for z in range(lz - 6, lz - 1):
            for y in range(41, 45):
                S.put(x, y, z, None)
            S.put(x, 40, z, "polished_deepslate")
        S.put(x, 41, lz - 2, "deepslate_brick_wall")
    prop("hoist_crane", lx + 4, 41, lz - 4, "south")
    prop("stone_brazier", lx - 3, 41, lz - 4, "north")
    # the terraces: stairs climbing between them, the houses dug into each riser facing the yard
    homes = 0
    for k in range(1, NT + 1):
        r = R0 + (k - 1) * DR
        y0 = STEP * (k - 1)
        for a in (0.2 + k * 0.7, 2.6 - k * 0.5, 3.6 + k * 0.4, 5.6 - k * 0.3):
            if gap(a) < 0.8:
                continue
            c, s_ = math.cos(a), math.sin(a)
            if s_ * (r + 6) < zc(c * (r + 6)) + 2:
                continue
            for i in range(STEP):
                for w in (-0.6, 0.6):
                    x, z = int(round(c * (r + i) - s_ * w)), int(round(s_ * (r + i) + c * w))
                    S.put(x, y0 + 1 + i, z, H.stairs("deepslate_brick", cardinal(c, s_)))
                    for yy in range(y0 + 2 + i, y0 + 5 + i):
                        S.put(x, yy, z, None)
                    P.occ[(x, z)] = "road"
    for k in range(1, NT + 1):
        r = R0 + (k - 1) * DR + 0.5
        y0 = STEP * (k - 1)
        a = 0.3 * k
        n_ok = 0
        while a < 0.3 * k + 2 * math.pi and n_ok < 6:
            c, s_ = math.cos(a), math.sin(a)
            x, z = int(round(c * r)), int(round(s_ * r))
            w = S.rnd.choice((5, 7, 7, 9))
            face = cardinal(-c, -s_)
            fxd, fzd = DIRS[face]
            cells = [(x + (-fzd) * i - fxd * j, z + fxd * i - fzd * j) for i in range(-w // 2 - 1, w // 2 + 2) for j in range(-3, 7)]
            ok = gap(a) > 0.85 and all(P.occ.get(q) in (None,) and q not in WET and gh(*q) >= y0 - 1 and
                                       (gh(*q) <= y0 + STEP + 1) for q in cells)
            if ok and all(q[1] > zc(q[0]) + 1 for q in cells):
                door = dhouse(x, z, face, y0, w, porch=S.rnd.random() < 0.35, P=P)
                for q in cells:
                    P.occ.setdefault(q, "yard")
                homes += 1
                n_ok += 1
                if S.rnd.random() < 0.5:
                    dx_, dz_ = DIRS[face]
                    q = (door[0] + (-dz_) * 2, door[1] + dx_ * 2)
                    prop(S.pick(("ale_cask", 2), ("ore_pile", 1), ("tool_rack", 2)), q[0], y0 + 1, q[1], face)
                a += (w + 4) / r
            else:
                a += 1.5 / r
    # the road in from the south through the gap, the signpost, pines on the high terraces and the mountain
    road = [(0.5 + gx_ * r, gz_ * r) for r in range(R0 - 1, 140) if abs(gx_ * r) < 94 and gz_ * r < 94]
    P.road(road, 1.5)
    FOCUS["hold"] = (int(gx_ * 62), int(gz_ * 62))
    for (x, z), t in list(P.occ.items()):
        if t == "road" and (x, z) not in WET and S.get(x, gh(x, z) + 1, z) is None and gh(x, z) <= 1:
            S.put(x, gh(x, z), z, S.pick(("stone_bricks", 4), ("polished_andesite", 2), ("gravel", 1)))
    x, z = int(gx_ * 30 - gz_ * 4), int(gz_ * 30 + gx_ * 4)
    prop("signpost", x, gh(x, z) + 1, z, "south")
    for k in range(4):
        r, w = R0 + k * 6, (-3.5 if k % 2 else 3.5)
        x, z = int(round(gx_ * r - gz_ * w)), int(round(gz_ * r + gx_ * w))
        prop("stone_brazier", x, gh(x, z) + 1, z, "north")
    pines = 0
    for _ in range(4000):
        if pines >= 70:
            break
        x, z = S.rnd.randint(-90, 90), S.rnd.randint(-90, 90)
        r = math.hypot(x, z)
        if r < R0 + DR * 2 or P.occ.get((x, z)) or (x, z) in WET:
            continue
        if any(P.occ.get((x + a, z + b)) in ("house", "yard") for a in (-3, 0, 3) for b in (-3, 0, 3)):
            continue
        nb = [gh(x + a, z + b) for a in (-2, 2) for b in (-2, 2)]
        if max(nb) - min(nb) > 3:
            continue
        lay_tree(S.pick(("pine_medium_0", 2), ("pine_medium_1", 2), ("pine_small_0", 3), ("pine_large_0", 1)), x, z, k=S.rnd.randint(0, 3))
        P.occ[(x, z)] = "tree"
        pines += 1
    scatter(500, *box, lambda x, z: S.put(x, gh(x, z) + 1, z, S.pick(("short_grass", 8), ("fern", 3), ("dandelion", 1), ("cornflower", 1))),
            clear=lambda x, z: P.occ.get((x, z)) is None and S.get(x, gh(x, z), z) == GRASS, tries=3000)
    finish()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "renders", "villages")
    os.makedirs(out, exist_ok=True)
    P.plan_png(os.path.join(out, "plan_%s.png" % out_name("hold")))
    print("homes", homes, "gate z", gz)
    return {"approach": ((3, 6, 70), (0, 16, -10), 22),
            "gate": ((6, 6, gz + 26), (0, 15, gz), 24),
            "terraces": ((-20, 22, -12), (30, 10, 20), 20),
            "wide": ((45, 95, 150), (0, 12, -15), 22),
            "mine": ((-6, 5, mz + 18), (mx, 3, mz), 24)}


# ================================================================ Millbrae: the hill and its windmill

def windmill(cx, cz):
    """A round stone tower on the hill's crown, a shingled cap, four sails on the side facing the village."""
    y0 = max(gh(cx + a, cz + b) for a in range(-5, 6) for b in range(-5, 6))
    STONE = (("ashbound:greystone", 5), ("ashbound:greystone", 3), ("ashbound:mossy_greystone", 1))
    for a in range(-6, 7):
        for b in range(-6, 7):
            d = math.hypot(a, b)
            if d <= 6.3:
                for yy in range(gh(cx + a, cz + b) - 1, y0 + 1):
                    S.put(cx + a, yy, cz + b, S.pick(*STONE) if d > 5.3 else "dirt")
                S.put(cx + a, y0, cz + b, S.pick(("ashbound:greystone", 2), ("coarse_dirt", 2), ("gravel", 1)))
                G[(cx + a, cz + b)] = y0
    top = y0 + 14
    for y in range(y0 + 1, top):
        r = 4.6 - (y - y0) * 0.09
        for a in range(-5, 6):
            for b in range(-5, 6):
                d = math.hypot(a, b)
                if r - 1.1 < d <= r:
                    S.put(cx + a, y, cz + b, "stone_bricks" if y % 5 == 0 else S.pick(*STONE))
    for y in (y0 + 3, y0 + 4, y0 + 8, y0 + 9):                 # windows up the tower
        for (a, b) in ((0, -4), (4, 0), (-4, 0)):
            S.put(cx + a, y, cz + b, H.PANE)
    S.put(cx, y0 + 1, cz + 4, "spruce_door[facing=north,half=lower,hinge=left,open=false,powered=false]")
    S.put(cx, y0 + 2, cz + 4, "spruce_door[facing=north,half=upper,hinge=left,open=false,powered=false]")
    S.put(cx, y0 + 3, cz + 5, "ashbound:wall_lantern[facing=south]")
    for k in range(7):                                          # the cap: a cone of shingles
        r = 4.8 - k * 0.75
        for a in range(-6, 7):
            for b in range(-6, 7):
                d = math.hypot(a, b)
                if r - 1.2 < d <= r:
                    S.put(cx + a, top + k, cz + b, "ashbound:wood_shingles")
    S.put(cx, top + 7, cz, "lightning_rod[facing=up,powered=false,waterlogged=false]")
    hub = (cx, top - 1, cz + 5)
    S.put(hub[0], hub[1], hub[2] - 1, "spruce_log[axis=z]")
    prop("windmill_sails", hub[0], hub[1], hub[2] + 0.6, "south")
    for (a, b) in ((3, 5), (-3, 5), (5, 2)):
        S.put(cx + a, y0 + 1, cz + b, "ashbound:grain_sacks[facing=south]")
    return y0


def green(P, cx, cz, r=7):
    """The village green: turf, the well under its little roof, the great oak, benches, the notice board, a stall."""
    for a in range(-r - 1, r + 2):
        for b in range(-r - 1, r + 2):
            if math.hypot(a, b) <= r + 0.5:
                P.occ[(cx + a, cz + b)] = "focus"
    y = gh(cx, cz)
    for a in range(-1, 2):
        for b in range(-1, 2):
            for yy in range(y - 3, y + 1):
                S.put(cx + a, yy, cz + b, "ashbound:greystone")
    prop("well", cx, y + 1, cz, "south")
    prop("market_stall", cx + 4, gh(cx + 4, cz + 3) + 1, cz + 3, "west")
    prop("market_stall", cx - 3, gh(cx - 3, cz + 5) + 1, cz + 5, "north")
    prop("signpost", cx + 6, gh(cx + 6, cz - 5) + 1, cz - 5, "south")
    lay_tree("oak_medium_2", cx - 5, cz - 3)
    for (a, b, f) in ((3, -4, "north"), (4, -4, "north"), (-4, 4, "south"), (-3, 4, "south")):
        S.put(cx + a, gh(cx + a, cz + b) + 1, cz + b, H.stairs("spruce", f))
    S.put(cx + 6, gh(cx + 6, cz + 1) + 1, cz + 1, "ashbound:notice_planks")
    S.put(cx + 6, gh(cx + 6, cz + 1) + 2, cz + 1, "ashbound:notice_planks")


# the hill village's three plans: the hills (x, z, height, reach, stretch along x, along z), the mill's hill, the green,
# the roads (from, to, width) and the lanes off them (road index, how far along, angle, length)
HILL = [
    dict(hills=((10, -32, 27, 30, 1.0, 1.15),), mill=(10, -32), green=(-6, 24),
         roads=(((2, 86), "in", 1.6), ((-86, 6), "in", 1.6), ("out", (86, 44), 1.4)),
         lanes=((1, 0.55, -2.3, 30), (0, 0.55, 0.4, 26), (2, 0.55, 2.0, 28), (1, 0.55, 2.5, 26))),
    # a street village: one long main street under a ridge, the mill up on the ridge's west shoulder, farms south
    dict(hills=((-6, -46, 25, 30, 0.42, 1.25),), mill=(-30, -46), green=(6, 14),
         roads=(((-88, 22), "in", 1.6), ("out", (88, 8), 1.6), ((14, 88), "in", 1.2)),
         lanes=((0, 0.35, 1.4, 34), (1, 0.4, 1.6, 34), (1, 0.75, 1.2, 30), (0, 0.7, -1.7, 22), (2, 0.6, 0.2, 30))),
    # a crossroads in the valley between two hills: the mill on the big one north-west, a beech hill south-east
    dict(hills=((-48, -44, 26, 26, 1.0, 1.0), (50, 46, 15, 22, 1.2, 0.9)), mill=(-48, -44), green=(6, 2),
         roads=(((0, -88), "in", 1.4), ((-4, 88), "in", 1.4), ((-88, 14), "in", 1.6), ("out", (88, -10), 1.6)),
         lanes=((0, 0.45, 0.2, 30), (1, 0.5, -0.4, 28), (3, 0.5, 1.9, 26), (2, 0.45, 1.3, 30))),
]


def hill():
    import vplan
    new(31)
    V_ = HILL[VAR % 3]
    hx, hz = V_["mill"]

    def hf(x, z):
        top = 0.0
        for k, (cx, cz, ht, reach, sx, sz) in enumerate(V_["hills"]):
            r = math.hypot((x - cx) * sx, (z - cz) * sz) + 5 * noise(x, z, 16, 21 + 7 * k)
            top = max(top, min(ht - 3.0, ht * math.exp(-(r / reach) ** 2)))
        return 1.5 + top + 2.5 * noise(x, z, 28, 22) + noise(x, z, 9, 23)

    box = (-90, -90, 90, 90)
    land(*box, hf)
    focus = V_["green"]
    P = vplan.Plan(sys.modules[__name__], box, focus, rings=(17, 40, 64), cap=26)
    for a in range(-7, 8):                        # the mill's crown kept clear
        for b in range(-7, 8):
            if math.hypot(a, b) <= 7:
                P.occ[(hx + a, hz + b)] = "landmark"
    green(P, *focus)
    mains = []
    for a, b, w in V_["roads"]:                   # each main road from the land's edge to the green's edge, or out
        if a == "out":
            d = math.hypot(b[0] - focus[0], b[1] - focus[1])
            st = (int(focus[0] + 8 * (b[0] - focus[0]) / d), int(focus[1] + 8 * (b[1] - focus[1]) / d))
            rd = P.route(st, b)
        else:
            d = math.hypot(a[0] - focus[0], a[1] - focus[1])
            rd = P.route(a, (int(focus[0] + 8 * (a[0] - focus[0]) / d), int(focus[1] + 8 * (a[1] - focus[1]) / d)))
        P.road(rd, w)
        mains.append((rd, a == "out"))
    dx_, dz_ = hx - focus[0], hz - focus[1]
    d = math.hypot(dx_, dz_)
    up = P.route((int(focus[0] + 8 * dx_ / d), int(focus[1] + 8 * dz_ / d)), (int(hx - 8 * dx_ / d), int(hz - 8 * dz_ / d)), slope=90)
    P.road(up, 1.1, "hill")
    rd0, out0 = mains[0]
    w0 = rd0[-len(rd0) // 4] if out0 else rd0[len(rd0) // 4]
    FOCUS["hill"] = (int(w0[0]), int(w0[1]))                # /ashbound village lands you on the first road in
    lanes = []
    for ri, at, ang, ln in V_["lanes"]:
        base = mains[ri][0]
        a = base[int(len(base) * at)]
        b = (int(a[0] + ln * math.cos(ang)), int(a[1] + ln * math.sin(ang)))
        b = (max(box[0] + 6, min(box[2] - 6, b[0])), max(box[1] + 6, min(box[3] - 6, b[1])))
        if (b[0], b[1]) in WET:
            continue
        l = P.route((int(a[0]), int(a[1])), b)
        P.road(l, 0.9, "lane")
        lanes.append(l)
    # houses: the knot round the green first, the roads into it, then the hill road, then the lanes' farmsteads
    P.around(7.5)
    for rd, out in mains:
        P.frontage(rd if out else list(reversed(rd)), start=6)
    P.frontage(up, start=6, skip=0.35)
    for l in lanes:
        P.frontage(l, start=3, skip=0.2)
    windmill(hx, hz)
    P.fields(n=7)
    P.yards()
    P.paths()
    P.street_life(26)
    P.woods(46)
    P.pave()
    scatter(500, *box, flowers, clear=lambda x, z: P.occ.get((x, z)) is None)
    finish()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "renders", "villages")
    os.makedirs(out, exist_ok=True)
    P.plan_png(os.path.join(out, "plan_%s.png" % out_name("hill")))
    print("houses", len(P.houses), {r: sum(1 for h in P.houses if h["role"] == r) for r in ("core", "mid", "edge", "farm")})
    gy = gh(*focus)
    return {"approach": ((2, gh(2, 70) + 5, 70), (0, gy + 6, 10), 26),
            "green": ((focus[0] + 18, gy + 9, focus[1] + 20), (focus[0], gy + 3, focus[1]), 26),
            "wide": ((85, 60, 105), (0, 8, -5), 24),
            "mill": ((hx - 30, gh(hx, hz) + 6, hz + 30), (hx, gh(hx, hz) + 10, hz), 26)}


# ================================================================ into the game

BIOME = {"lake": 1, "gorge": 2, "hill": 2, "cliff": 2, "tree": 8, "hold": 3}     # Capital.BIOME_IDS, 1 up
GLOW = {"elf_lantern": 13, "lake_lantern": 13, "stone_brazier": 14, "forge_anvil": 12, "moon_basin": 9, "elf_arch": 8}
GAME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(GAME, "src", "main", "resources", "data", "ashbound", "village")
MARGIN = 32


def face_of(yaw):
    return {0: "north", 90: "west", 180: "south", 270: "east"}[int(round(yaw)) % 360 // 90 * 90]


# the props that stand about loose (yards, roadsides, work floors): checked against the blocks round them at export,
# nudged, turned or dropped so none ends up through a wall, a fence or another prop
CLUTTER = {"woodpile", "washing_line", "skeps", "hay_cart", "handcart", "wheelbarrow", "churns_sacks", "scarecrow", "net_rack",
           "fish_rack", "catch_basket", "eel_traps", "reed_sheaves", "ore_pile", "mine_cart", "tool_rack", "ale_cask", "herb_rack",
           "stone_brazier", "archery_butts", "market_stall", "signpost", "well", "elf_banner", "mooring_post", "forge_anvil"}
_BOUNDS = {}
AIRY = ("air", "light[", "short_grass", "tall_grass", "fern", "poppy", "dandelion", "cornflower", "daisy", "bluet", "allium",
        "tulip", "lily_of", "carpet", "snow[", "fireflies", "petals", "glowcap")


def bounds(m):
    """the prop model's extent in blocks: x0, x1, y0, y1, z0, z1 (the OBJs are centred on their origin, feet at 0)"""
    if m not in _BOUNDS:
        v = [list(map(float, ln.split()[1:4])) for ln in open(os.path.join(ASSETS, "models/mesh", m + ".obj")) if ln.startswith("v ")]
        _BOUNDS[m] = (min(a[0] for a in v), max(a[0] for a in v), min(a[1] for a in v), max(a[1] for a in v),
                      min(a[2] for a in v), max(a[2] for a in v))
    return _BOUNDS[m]


def footprint(m, x, y, z, yaw, sc):
    x0, x1, y0, y1, z0, z1 = bounds(m)
    t = math.radians(yaw)
    c, s_ = math.cos(t), math.sin(t)
    pts = [(a * c + b * s_, -a * s_ + b * c) for a in (x0 * sc, x1 * sc) for b in (z0 * sc, z1 * sc)]
    xa, xb = x + min(p[0] for p in pts) + 0.2, x + max(p[0] for p in pts) - 0.2
    za, zb = z + min(p[1] for p in pts) + 0.2, z + max(p[1] for p in pts) - 0.2
    ya, yb = int(math.floor(y + 0.05)), int(math.floor(y + max(0.3, y1 * sc - 0.2)))
    return [(i, j, k) for i in range(int(math.floor(xa)), int(math.floor(xb)) + 1) for k in range(int(math.floor(za)), int(math.floor(zb)) + 1)
            for j in range(ya, yb + 1)]


def _free(q):
    v = S.get(*q)
    if v is None:
        return q[1] > gh(q[0], q[2]) or q in CARVED
    return any(k in v for k in AIRY)


# the props a body can't walk through: invisible barriers fill their footprint (one high, two for the tall ones);
# the thin upright ones only at their foot. Arches, lines, banners, boats and lamps stay open.
BODY = {"woodpile", "skeps", "hay_cart", "handcart", "wheelbarrow", "churns_sacks", "net_rack", "fish_rack", "catch_basket",
        "eel_traps", "reed_sheaves", "ore_pile", "mine_cart", "tool_rack", "ale_cask", "herb_rack", "stone_brazier",
        "archery_butts", "market_stall", "well", "forge_anvil", "covered_wagon", "moon_basin", "lift_cage", "lift_basket"}
POLE = {"signpost", "scarecrow", "mooring_post"}


def body_props():
    n = 0
    for (m, x, y, z, yaw, sc) in PROPS:
        if m in POLE:
            cells = [(int(math.floor(x)), int(math.floor(y + 0.05)), int(math.floor(z)))]
        elif m in BODY:
            tall = (bounds(m)[3] * sc) > 1.3
            base = int(math.floor(y + 0.05))
            cells = [q for q in footprint(m, x, y, z, yaw, sc) if q[1] < base + (2 if tall else 1)]
        else:
            continue
        for q in cells:
            if _free(q) and q not in WALKS:
                S.put(*q, "barrier")
                n += 1
    print("  prop bodies: %d barriers" % n)


def settle_props():
    """every loose prop on clear standing: its whole footprint free (no wall, fence, tree or other prop through it),
    something solid under its middle; else the nearest spot a step or two off, or turned, or a block up or down"""
    taken, kept, moved, dropped = set(), [], 0, []
    tries = [(0, 0)] + [(a, b) for r in (1, 2) for a in range(-r, r + 1) for b in range(-r, r + 1) if max(abs(a), abs(b)) == r]
    for (m, x, y, z, yaw, sc) in PROPS:
        if m not in CLUTTER:
            kept.append((m, x, y, z, yaw, sc))
            continue
        ok = None
        for (a, b) in tries:
            for dy in (0, 1, -1):
                for dyaw in (0, 180, 90, -90):
                    cells = footprint(m, x + a, y + dy, z + b, yaw + dyaw, sc)
                    under = (int(math.floor(x + a)), int(math.floor(y + dy + 0.05)) - 1, int(math.floor(z + b)))
                    if not _free(under) and "water" not in (S.get(*under) or "") and all(_free(q) and q not in taken for q in cells):
                        ok = (m, x + a, y + dy, z + b, yaw + dyaw, sc, cells)
                        break
                if ok:
                    break
            if ok:
                break
        if ok is None:
            dropped.append(m)
            continue
        moved += ok[1:5] != (x, y, z, yaw)
        taken.update(ok[6])
        kept.append(ok[:6])
    PROPS[:] = kept
    print("  props: %d moved clear, %d dropped %s" % (moved, len(dropped), sorted(set(dropped))))


_CW = {"north": "east", "east": "south", "south": "west", "west": "north"}


def turn_cell(x, z):
    """a block's cell turned VAR quarter turns clockwise (seen from above) round the village's origin"""
    for _ in range(VAR % 4):
        x, z = -z - 1, x
    return x, z


def turn_point(x, z):
    for _ in range(VAR % 4):
        x, z = -z, x
    return x, z


def turn_state(n, pr):
    """a block state's properties turned with the village: facings, axes, sign rotations, the sides fences join"""
    if not pr or VAR % 4 == 0:
        return pr
    pr = dict(pr)
    for _ in range(VAR % 4):
        q = {}
        for k, v in pr.items():
            if k in _CW:
                q[_CW[k]] = v
            elif k in ("facing", "horizontal_facing") and v in _CW:
                q[k] = _CW[v]
            elif k == "axis" and v in ("x", "z"):
                q[k] = "z" if v == "x" else "x"
            elif k == "rotation" and v.isdigit():
                q[k] = str((int(v) + 4) % 16)
            elif k == "shape" and any(d in v for d in _CW):        # rails
                w = [_CW.get(p_, p_) for p_ in v.split("_")]
                if w[0] == "ascending":
                    q[k] = "_".join(w)
                elif set(w) in ({"north", "south"}, {"east", "west"}):
                    q[k] = "north_south" if "north" in w else "east_west"
                else:
                    q[k] = "_".join(sorted(w, key=lambda d: d not in ("north", "south")))
            else:
                q[k] = v
        pr = q
    return pr


def out_name(name):
    return name if VAR == 0 else "%s_%d" % (name, VAR + 1)


def export(name):
    """data/ashbound/village/NAME.bin (Capital's CAPT format: the ground's shape, its blocks) and NAME.json (the props,
    stood in as block displays; the moving ones as VillageSpin hubs)"""
    import gzip
    import json
    import struct
    for (x, y, z) in WALKS:                                      # the rope bridges' floors
        if S.get(x, y, z) in (None, "air"):
            S.put(x, y, z, "barrier")
    settle_props()
    body_props()
    props = []
    for (m, x, y, z, yaw, sc) in PROPS:
        if m in SPIN:
            S.put(int(math.floor(x)), int(math.floor(y)), int(math.floor(z)), "%s[facing=%s]" % (SPIN[m], face_of(yaw)))
            continue
        x0, x1, y0, y1, z0, z1 = bounds(m)
        reach = max(x1 - x0, y1 - y0, z1 - z0) * sc
        props.append([m, round(x, 3), round(y, 3), round(z, 3), round(yaw % 360, 1), sc, round(min(2.5, max(0.6, 0.45 + 0.15 * reach)), 2)])
        if m in GLOW:
            q = (int(math.floor(x)), int(math.floor(y)) + 1, int(math.floor(z)))
            if S.get(*q) in (None, "air"):
                S.put(*q, "light[level=%d,waterlogged=false]" % GLOW[m])
    for k, v in list(S.B.items()):
        if v == "air":
            del S.B[k]
    flies = {k: v for k, v in S.B.items() if v == FIREFLY or v.startswith("light[") or v == "barrier" or
             v.split("[")[0] in SPIN.values()}                        # meant to hang in the air: the settle mustn't take them
    for k in flies:
        del S.B[k]
    K.settle(S)
    S.B.update(flies)
    K.connect(S)
    for p in CARVED:
        if p not in S.B:
            S.B[p] = "air"
    G = {turn_cell(*k): v for k, v in globals()["G"].items()}      # the village turned for this layout
    xs = [x for x, z in G]
    zs = [z for x, z in G]
    bx0, bx1, bz0, bz1 = min(xs), max(xs), min(zs), max(zs)
    gx0, gz0 = bx0 - MARGIN, bz0 - MARGIN
    W, D = bx1 - bx0 + 1 + 2 * MARGIN, bz1 - bz0 + 1 + 2 * MARGIN
    T, Mo, Wt, Bl, Bi = bytearray(), bytearray(W * D), bytearray(W * D), bytearray(W * D), bytearray(W * D)
    for j in range(D):
        for i in range(W):
            x, z = gx0 + i, gz0 + j
            cx, cz = min(max(x, bx0), bx1), min(max(z, bz0), bz1)
            d = max(abs(x - cx), abs(z - cz))
            k = j * W + i
            T += struct.pack(">h", G[(cx, cz)])
            Mo[k] = 1 | (4 if d == 0 else 0)                       # CUT_FILL, CLEAR inside the village
            Bl[k] = int(255 * min(1.0, d / (MARGIN - 8)))
            Wt[k] = 255 if d <= MARGIN - 8 else int(255 * (MARGIN - d) / 8)
            Bi[k] = BIOME[name] if d < MARGIN - 4 else 0
    pal, idx, rows = [], {}, []
    for (x, y, z), st in S.B.items():
        flow = st.endswith("#flow")
        n, pr = K.parse(st[:-5] if flow else st)
        if ":" not in n:
            n = "minecraft:" + n
        n = {"minecraft:iron_chain": "minecraft:chain"}.get(n, n)
        if any(k in n for k in ("leaves", "blossom", "needles")):          # never decaying: the leaves of a tree we built
            pr = dict(pr or {})
            pr.update(distance=pr.get("distance", "7"), persistent="true", waterlogged=pr.get("waterlogged", "false"))
        st = K.fmt(n, turn_state(n, pr)) + ("#flow" if flow else "")
        if st not in idx:
            idx[st] = len(pal)
            pal.append(st)
        x, z = turn_cell(x, z)
        rows.append((x >> 4, z >> 4, x, y, z, idx[st]))
    rows.sort()
    missing = sorted({st.split("[")[0] for st in pal if st.startswith("ashbound:") and
                      not os.path.exists(os.path.join(ASSETS, "blockstates", st.split("[")[0][9:].split("#")[0] + ".json"))})
    if missing:
        print("  MISSING BLOCKS:", missing)
    fx, fz = FOCUS.get(name, (0, 0))
    cx_, cz_ = turn_point(fx + 0.5, fz + 0.5)
    points = {"centre": (cx_, gh(fx, fz) + 1.0, cz_)}
    buf = bytearray(b"CAPT") + struct.pack(">iiiii", 2, gx0, gz0, W, D) + T + Mo + Wt + Bl + Bi
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
    os.makedirs(OUTDIR, exist_ok=True)
    out = os.path.join(OUTDIR, out_name(name) + ".bin")
    with gzip.open(out, "wb", compresslevel=6) as f:
        f.write(bytes(buf))
    for pp in props:
        pp[1], pp[3] = (round(c, 3) for c in turn_point(pp[1], pp[3]))
        pp[4] = round((pp[4] - 90 * VAR) % 360, 1)              # a display's yaw turns it the other way round
    with open(os.path.join(OUTDIR, out_name(name) + ".json"), "w", encoding="utf-8") as f:
        json.dump({"props": props}, f)
    print("%s: %d blocks, %d states, %d props, ground %dx%d, %d KB" % (name, len(rows), len(pal), len(props), W, D, os.path.getsize(out) // 1024))


FOCUS = {"lake": (2, 50), "gorge": (-40, 2), "hill": (2, 70), "cliff": (2, 76), "tree": (2, 100), "hold": (2, 62)}   # where /ashbound village lands you



# ================================================================ the villagers (Capital spawns KIND_cast.json)

RACE = {"tree": "@elf", "hold": "@dwarf"}
# who you find at a prop: (selector, how many, how far in front of it); "{r}" is the village's race
AT = {
    "well": [("{r}", 2, 2.0)], "market_stall": [("@townsfolk/merchant", 1, -1.4), ("{r}", 1, 2.2)],
    "signpost": [("{r}", 1, 1.6)], "scarecrow": [("@townsfolk/farmer", 1, 2.0)], "hay_cart": [("@townsfolk/farmer", 1, 2.0)],
    "wheelbarrow": [("@townsfolk/farmer", 1, 1.6)], "woodpile": [("@townsfolk", 1, 1.6)], "washing_line": [("@townsfolk/f", 1, 1.4)],
    "skeps": [("@townsfolk/elder", 1, 1.8)], "churns_sacks": [("@townsfolk/baker", 1, 1.6)], "handcart": [("@townsfolk/merchant", 1, 1.6)],
    "net_rack": [("@townsfolk", 1, 1.6)], "fish_rack": [("@townsfolk", 1, 1.6)], "catch_basket": [("@townsfolk", 1, 1.4)],
    "toll_barrier": [("@townsfolk/guard", 2, 1.6)], "hoist_crane": [("{r}", 1, 2.0)], "lift_basket": [("{r}", 1, 1.6)],
    "forge_anvil": [("@dwarf/smith", 2, 1.8)], "ale_cask": [("@dwarf/brewer", 1, 1.6)], "tool_rack": [("@dwarf/miner", 1, 1.6)],
    "ore_pile": [("@dwarf/miner", 1, 1.8)], "mine_cart": [("@dwarf/miner", 1, 1.8)], "rune_door": [("@dwarf/guard", 2, 3.5)],
    "stone_brazier": [("@dwarf/guard", 1, 1.6)], "lift_cage": [("@dwarf/miner", 1, 2.0)],
    "herb_rack": [("@elf/herbalist", 1, 1.6)], "archery_butts": [("@elf/warden", 2, 9.0)],
    "moon_basin": [("@elf/singer", 2, 2.6), ("@elf/elder", 1, 3.2)],
    "elf_arch": [("@elf/warden", 2, 2.0)], "elf_lantern": [("@elf/lamplighter", 1, 1.4)],
}
CAP = {"stone_brazier": 4, "elf_lantern": 4, "washing_line": 4, "skeps": 2, "scarecrow": 2, "catch_basket": 2, "wheelbarrow": 2}
SOFT = ("grass", "fern", "flower", "poppy", "dandelion", "tulip", "daisy", "orchid", "allium", "bluet", "cornflower",
        "lily_of", "carpet", "rail", "torch", "button", "light[", "snow[", "lantern", "sapling", "petals")


def _open(v):
    return v is None or v in ("air", "cave_air") or any(k in v for k in SOFT)


def _floor(x, y, z):
    v = S.get(x, y, z)
    if v is None:
        return y <= G.get((x, z), -999) and (x, y, z) not in CARVED
    return not _open(v) and not any(k in v for k in ("water", "lava", "fence", "_wall", "pane", "chain", "leaves", "lightning",
                                                     "door", "campfire", "barrier"))


def stand(x, y, z, reach=2):
    """the nearest cell round (x, y, z) a body can stand in: a floor under it, two open cells above, not in water"""
    for r in range(reach + 1):
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if max(abs(dx), abs(dz)) != r:
                    continue
                for dy in (0, 1, -1, 2, -2, 3, -3):
                    cx, cy, cz = x + dx, y + dy, z + dz
                    w = WET.get((cx, cz))
                    if w is not None and cy <= w + 1 and S.get(cx, cy - 1, cz) is None:
                        continue
                    if _floor(cx, cy - 1, cz) and _open(S.get(cx, cy, cz)) and _open(S.get(cx, cy + 1, cz)):
                        return cx, cy, cz
    return None


def cast(name):
    """KIND_cast.json: who lives in the village and where they spend their day - [selector, shop, mode, x, y, z, yaw]"""
    import json
    rnd = random.Random(sum(map(ord, name)))
    race = RACE.get(name, "@townsfolk")
    out, taken = [], set()

    npcs = os.path.join(os.path.dirname(OUTDIR), "npc")
    tagsets = [set(json.load(open(os.path.join(npcs, f), encoding="utf-8")).get("tags", [])) for f in os.listdir(npcs)]

    def known(sel):
        """a selector some NPC answers to (Talk.resolve), else the plain race"""
        want = set(sel.replace("{r}", race)[1:].split("/"))
        return sel if any(want <= t for t in tagsets) else race

    def put(sel, mode, x, y, z, look=None):
        sel = known(sel)
        c = stand(int(math.floor(x)), int(math.floor(y)), int(math.floor(z)))
        if c is None or c in taken:
            return False
        taken.add(c)
        if look is None:
            yaw = rnd.uniform(0, 360)
        else:
            yaw = math.degrees(math.atan2(-(look[0] - c[0] - 0.5), look[1] - c[2] - 0.5)) % 360
        out.append([sel.replace("{r}", race), "", mode, c[0], c[1], c[2], round(yaw, 1)])
        return True
    seen = {}
    for (m, x, y, z, yaw, sc) in PROPS:
        if m not in AT:
            continue
        seen[m] = seen.get(m, 0) + 1
        if seen[m] > CAP.get(m, 99):
            continue
        a = math.radians(yaw)
        fx, fz = -math.sin(a), math.cos(a)                    # the way the prop's front faces (yaw 0 = south)
        for sel, n, d in AT[m]:
            if race != "@townsfolk" and sel.startswith("@townsfolk"):
                sel = race                                    # a dwarf hold has no human farmers
            for k in range(n):
                side = (k - (n - 1) / 2) * 1.6
                put(sel, "stand", x + fx * d - fz * side, y, z + fz * d + fx * side, look=(x, z))
    # residents at their doors, the rest out on the roads and decks
    doors = [(h["door"][0], h["y"] + 1, h["door"][1]) for P in PLANS for h in P.houses] + list(DOORS)
    rnd.shuffle(doors)
    for (x, y, z) in doors[:len(doors) // 3]:
        put(race, "stand", x, y, z)
    walks = []
    for P in PLANS:
        for pts, w, kind in P.roads:
            walks += [(px, gh(int(px), int(pz)) + 1, pz) for px, pz in pts[::6]]
    walks += [(x, max(ys) + 1, z) for (x, z), ys in DECK.items() if (x * 7 + z * 13) % 23 == 0]
    rnd.shuffle(walks)
    want = max(6, len(doors) // 2)
    for (x, y, z) in walks:
        if want <= 0:
            break
        want -= put(race if rnd.random() < 0.8 else race + "/child", "stroll", x, y, z)
    fx, fz = FOCUS.get(name, (0, 0))
    for k in range(3):
        put(race + "/child", "stroll", fx + rnd.uniform(-5, 5), gh(fx, fz) + 1, fz + rnd.uniform(-5, 5))
    for o in out:                                             # turned with the village
        o[3], o[5] = turn_cell(o[3], o[5])
        o[6] = round((o[6] + 90 * VAR) % 360, 1)
    with open(os.path.join(OUTDIR, out_name(name) + "_cast.json"), "w", encoding="utf-8") as f:
        json.dump(out, f)
    print("  cast: %d folk (%s)" % (len(out), ", ".join("%s %d" % (k, sum(1 for o in out if o[0] == k)) for k in sorted({o[0] for o in out}))))

VILLAGES = {"lake": lake, "gorge": gorge, "hill": hill, "cliff": cliff, "tree": tree, "hold": hold}

if __name__ == "__main__":
    if sys.argv[1:2] == ["--export"]:                        # --export [KIND[:VAR] ...]: every kind's three layouts by default
        for arg in sys.argv[2:] or ["%s:%d" % (k, v) for k in VILLAGES for v in range(3)]:
            what, _, v = arg.partition(":")
            for VAR in ([int(v)] if v else range(3)):
                print("== %s layout %d" % (what, VAR + 1))
                VILLAGES[what]()
                sync_props()
                export(what)
                cast(what)
        sys.exit()
    for what in sys.argv[1:]:
        shots = VILLAGES[what]()
        for k, v in list(S.B.items()):
            if v.endswith("#flow"):
                S.B[k] = v[:-5]
        print(what, "blocks", len(S.B))
        sync_props()
        print("props", len(PROPS))
        K.preview(S, "vil_" + what, shots, sun=(40, -130), sky=(0.55, 0.68, 0.85), vox=PROPS)
