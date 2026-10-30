"""Shared bits for the dungeons rebuilt at Epic Fight scale. The old E:/Ashbound generators (structkit, the place
helpers, the skins) do the building; these files resize the places for EF's monsters: elites stand 3-4 blocks
tall, bosses 5-13, and every fight needs room to roll and swing.

    corridors   7 wide, 7 tall at least          fight rooms   ~25 wide, 10+ tall
    arches      5 wide, 6 tall                   boss arenas   radius 20, headroom twice the boss

Bins go to tools/lairs/stage/... in the old format; port_gate.py reads them from there instead of E:/Ashbound and
swaps in our blocks as before."""
import os
import sys

OLD_TOOLS = "E:/Ashbound/tools"
sys.path.insert(0, OLD_TOOLS)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import structkit as K  # noqa: E402

STAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stage")
RENDER = "E:/Ashbound/tools/renders/struct"


def export(b, name, pts, check):
    """the bin, and its meta from the old dungeon's: built_check moved onto a `check` block of the new layout
    (a lamp, say), clear_top raised to the new roof"""
    import json
    root = K.ROOT
    K.ROOT = STAGE
    try:
        K.export_lair(b, name, pts)
    finally:
        K.ROOT = root
    d = os.path.join(STAGE, "src/main/resources/data/ashbound/lair")
    meta = json.load(open(os.path.join(root, "src/main/resources/data/ashbound/lair", name + ".json"), encoding="utf-8"))
    hits = sorted(p for p, st in b.B.items() if check in st)
    meta["built_check"] = [[hits[0][0], hits[0][1], hits[0][2], "ashbound:" + check]]
    meta["clear_top"] = max(meta.get("clear_top", 0), max(p[1] for p in b.B) + 2)
    json.dump(meta, open(os.path.join(d, name + ".json"), "w", encoding="utf-8"), indent=1)
    print("staged", os.path.join(d, name + ".bin"), "clear_top", meta["clear_top"])


# ---------------------------------------------------------------- architecture: room for EF needs depth, not bare boxes

def solidify(T, cells):
    """give carved air back to the rock (the skin then faces it in the room's own masonry)"""
    for p in cells:
        if p in T.air:
            T.air.discard(p)
            T.zone.pop(p, None)
            T.b.B.pop(p, None)


def plane(T, axis, at, u):
    """the air cells of one column in a cross-section: axis "z" = the plane z=at running along x"""
    x, z = (u, at) if axis == "z" else (at, u)
    return sorted(y for y in range(-80, 120) if (x, y, z) in T.air), x, z


def rib(T, axis, at, lo, hi, spring, thick=2, pilaster=True):
    """a transverse arch across a room: in the plane at `at` (thick deep), everything above a round arch springing
    at y `spring` from lo..hi goes back to stone; pilasters down the two walls where they stand against rock"""
    import math
    half = (hi - lo + 1) / 2.0
    c = lo + half
    for k in range(thick):
        a = at - k
        tops = [plane(T, axis, a, u)[0] for u in range(lo, hi + 1)]
        ytop = max((ys[-1] for ys in tops if ys), default=spring)
        rise = ytop - spring
        out = []
        for u in range(lo, hi + 1):
            ys, x, z = plane(T, axis, a, u)
            d = abs(u + 0.5 - c) / half
            arch = spring + rise * math.sqrt(max(0.0, 1 - d * d)) - 1.2
            out += [(x, y, z) for y in ys if y > arch]
            edge = u in (lo, hi)
            if edge and pilaster:
                bx, bz = (u - 1 if u == lo else u + 1, a) if axis == "z" else (a, u - 1 if u == lo else u + 1)
                if ys and (bx, ys[0], bz) not in T.air:
                    out += [(x, y, z) for y in ys]
        solidify(T, out)


def column(T, x0, z0, x1, z1):
    """a free-standing pier, floor to vault"""
    out = []
    for x in range(min(x0, x1), max(x0, x1) + 1):
        for z in range(min(z0, z1), max(z0, z1) + 1):
            out += [(x, y, z) for y in plane(T, "z", z, x)[0]]
    solidify(T, out)


def dome(T, cx, cz, R, y_top, rise, zone):
    """lift a round room's flat ceiling into a shallow dome"""
    import math
    for x in range(int(cx - R) - 1, int(cx + R) + 2):
        for z in range(int(cz - R) - 1, int(cz + R) + 2):
            d = math.hypot(x + 0.5 - cx, z + 0.5 - cz) / R
            if d >= 1:
                continue
            for y in range(y_top + 1, y_top + 1 + int(rise * math.sqrt(1 - d * d))):
                T.carve((x, y, z), zone)


# ---------------------------------------------------------------- light: each dungeon's mood (lightcheck.py judges it)
# (mood, most of the floor allowed black %, least of it lit 8+ %). The gates have no sky and no ambient light.
MOOD = {
    "cellar": ("dim", 35, 35),     # drowned vaults: pools of amber lamplight, black water and stretches between
    "gallows": ("lit", 15, 55),    # a hanging town at night: tallow lamps and tar fires on every street
    "rotwood": ("glow", 25, 45),   # the forest lit by its own glowcaps, darker under the canopy
    "crypt": ("lit", 10, 65),      # an abbey of a thousand candles
    "plague": ("lit", 10, 65),     # a ward lit hard and white by lime lamps
    "foundry": ("lit", 10, 65),    # fire everywhere, molten channels
    "ossuary": ("dark", 50, 25),   # bone pits in the dark: only soul fire, the way finds itself lamp to lamp
    "frost": ("lit", 10, 65),      # ice and snow throwing back every lantern
    "temple": ("dark", 55, 20),    # the abyss: crystals and nothing else, the faceless come out of the black
}


SIDES = {(1, 0): "west", (-1, 0): "east", (0, 1): "north", (0, -1): "south"}   # wall on that side -> faces away


def sconce(T, p, state):
    """a wall lamp at p, its back to whichever side has wall (none: nothing put)"""
    x, y, z = p
    for (dx, dz), f in SIDES.items():
        if (x + dx, y, z + dz) not in T.air:
            T.put(x, y, z, "%s[facing=%s]" % (state, f))
            return True
    return False


def wall_lights(T, zones, state, every=6, dy=2):
    """sconces round the walls (and piers) of the zones at head height (dy over the walk level), one every `every`
    blocks along each wall, never two side by side, never on something already put there"""
    B = T.b.B
    taken = set()
    for (x, y, z) in sorted(T.air):
        if T.zone.get((x, y, z)) not in zones or (x, z) not in T.floor or y != T.floor[(x, z)] + 1 + dy:
            continue
        if (x, y, z) in B or (x, y - dy - 1, z) in T.air:
            continue
        walls = [(dx, dz) for (dx, dz) in SIDES if (x + dx, y, z + dz) not in T.air]
        if len(walls) != 1:
            continue
        dx, dz = walls[0]
        along = z if dx else x
        if along % every or any((x + a, y, z + b) in taken for a in (-2, -1, 0, 1, 2) for b in (-2, -1, 0, 1, 2)):
            continue
        if sconce(T, (x, y, z), state):
            taken.add((x, y, z))
    return len(taken)


def light_grid(T, zones, make, every=8, keep_clear=None, phase=(0, 0)):
    """lamps on a grid over the open floor of the zones: make(x, floor, z) puts one (a post lamp, say) wherever the
    grid falls on bare floor with four blocks of air over it and nothing put within a block of it; keep_clear(x, z)
    True keeps a spot free (the middle of a lane)"""
    B = T.b.B
    n = 0
    for (x, z), fl in sorted(T.floor.items()):
        if (x - phase[0]) % every or (z - phase[1]) % every:
            continue
        if T.zone.get((x, fl + 1, z)) not in zones or (keep_clear and keep_clear(x, z)):
            continue
        if any((x, y, z) not in T.air for y in range(fl + 1, fl + 5)):
            continue
        if any((x + dx, y, z + dz) in B for dx in (-1, 0, 1) for dz in (-1, 0, 1) for y in (fl, fl + 1, fl + 2)
               if (dx, dz) != (0, 0) or y > fl):
            continue
        if T.floor.get((x + 1, z)) != fl or T.floor.get((x - 1, z)) != fl or T.floor.get((x, z + 1)) != fl or T.floor.get((x, z - 1)) != fl:
            continue     # not on a stair or a step
        make(x, fl, z)
        n += 1
    return n


def floors(T):
    """every column's floor: the one a place recorded, else the top of the solid under its lowest carved air"""
    out = {}
    for (x, y, z) in T.air:
        if (x, y - 1, z) not in T.air:
            out[(x, z)] = min(out.get((x, z), y - 1), y - 1)
    out.update(T.floor)
    return out


def hang_grid(T, zones, lamp, chain, every=7, height=5, keep_clear=None, phase=(0, 0)):
    """lamps hung on chains from the ceiling on a grid over the zones' floor, each `height` over the floor (high
    enough for EF's big ones to pass under; lamps and chains are no obstacle to them in game)"""
    B = T.b.B
    n = 0
    for (x, z), fl in sorted(floors(T).items()):
        if (x - phase[0]) % every or (z - phase[1]) % every:
            continue
        if T.zone.get((x, fl + 1, z)) not in zones or (keep_clear and keep_clear(x, z)):
            continue
        y = fl + 1
        while (x, y + 1, z) in T.air:
            y += 1
        if y < fl + height + 1 or any((x, yy, z) in B for yy in range(fl + 1, y + 1)):
            continue
        for yy in range(fl + height + 1, y + 1):
            B[(x, yy, z)] = chain
        B[(x, fl + height, z)] = lamp
        n += 1
    return n
