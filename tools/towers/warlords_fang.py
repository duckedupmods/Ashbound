"""The Warlord's Fang (docs/TOWERS.md, the badlands and dark woods) in blocks: an orc war-tower raised crooked on a
crag of red rock. Its stages are stacked skew, each turned and shoved a little off the one below; timber hoardings
on log braces jut off it, iron spikes bristle, war banners hang, skulls ride on poles; the way in is a gate in the
rock framed like a jaw. On the roof the war drum and the bonfire, and over them a great curved tusk rising off the
tower's corner and arching across the arena, a smaller one answering it - the tower is a beast's jaw.

    python tools/towers/warlords_fang.py [shots...] [cut] [walk] [export]
    E:/Steam/steamapps/common/Blender/blender.exe -b -P E:/Ashbound/tools/blender/preview_struct.py -- tower_fang [shots...]
"""
import math
import sys

import towerkit as TK
from towerkit import K, s, slab, stairs, wall

K.GLOW.update({"war_fire": 1.6})

FLOORS = [6, 16, 26, 36, 46, 56]
DECK = 66
HWS = [13.5, 13, 12.5, 12.5, 12, 11.5]   # each stage's half-width: it tapers
TURN = [0, 6, -3, 7, -2, 5]               # each stage's skew, degrees
SHOVE = [(0, 0), (1, -1), (1, -2), (2, -3), (3, -3), (4, -4)]   # and it leans, more each stage
HW = 12.5

t = TK.Tower("warlords_fang", "fang", "warlords_fang", brick="fang_stone", fill="fang_stone", px="fang",
             floors=FLOORS, deck=DECK, glow="war_fire", goods=[("minecraft:leather", 4, 2, 6), ("minecraft:iron_nugget", 4, 4, 12)])
t.origins = SHOVE
t.biomes = ["minecraft:badlands", "minecraft:wooded_badlands", "minecraft:eroded_badlands", "minecraft:dark_forest"]
put, get = t.put, t.get


def noise(x, y, z):
    return ((x * 73856093) ^ (y * 19349663) ^ (z * 83492791)) % 100


def stage(y):
    for k in range(len(FLOORS) - 1, -1, -1):
        if y >= FLOORS[k] - 1:
            return k
    return 0


def local(x, z, k):
    """a point in stage k's own skewed frame"""
    a = math.radians(TURN[k])
    ox, oz = SHOVE[k]
    px, pz = x - ox, z - oz
    return px * math.cos(a) + pz * math.sin(a), -px * math.sin(a) + pz * math.cos(a)


def sq(x, z, k):
    """distance out from stage k's centre in its own frame, scaled so its wall is always at HW"""
    u, v = local(x, z, k)
    f = HW / HWS[k]
    return max(abs(u), abs(v)) * f, u * f, v * f


# ---------------------------------------------------------------- the crag

def crag():
    for x in range(-26, 27):
        for z in range(-26, 27):
            phi = math.atan2(z, x)
            rr = math.hypot(x, z)
            edge = 21 + 2.5 * math.sin(phi * 3 + 0.7) + 1.5 * math.sin(phi * 7)
            # high at the back, low at the front where the gate is
            hgt = 8 + 5 * (0.5 - 0.5 * math.sin(phi)) + 2 * math.sin(phi * 5 + 1)
            for y in range(-8, int(hgt) + 1):
                slope = edge - max(0, y - 2) * 0.8
                if rr <= slope:
                    out = rr > slope - 1.2
                    put(x, y, z, s("crag_rock") if out or noise(x, y, z) < 70 else s("crag_ashlar"))
    # the gate: a passage cut south into the rock to the first floor, a jaw round its mouth
    for x in range(-3, 4):
        for z in range(9, 27):
            for y in range(6, 13):
                if y <= 12 - (abs(x) == 3):
                    put(x, y, z, None)
            put(x, 5, z, s("fang_flags"))
            for y in range(-8, 5):
                put(x, y, z, s("crag_ashlar"))
    for k in range(7):                          # steps up from the ground to the gate's floor
        z = 27 + k
        for x in range(-3, 4):
            for y in range(-8, 5 - k):
                put(x, y, z, s("crag_ashlar"))
            put(x, 5 - k, z, stairs("fang_stone", "north"))
            for y in range(6 - k, 12 - k):
                put(x, y, z, None)
        for cx in (-4, 4):
            for y in range(-8, 6 - k):
                put(cx, y, z, s("crag_rock"))
    jaw(26)


def jaw(z0):
    """two great tusks rising either side of the gate's mouth and curving in over it like a jaw"""
    for sx in (-1, 1):
        tusk((sx * 5.5, 4, z0 + 1), (sx * 7.5, 15, z0 + 3), (sx * 0.3, 15, z0 + 1), 2.2, root="crag_rock")
        tusk((sx * 7.5, 4, z0 - 1), (sx * 9.5, 11, z0 + 2), (sx * 5.5, 13, z0 + 1), 1.4, root="crag_rock")


# ---------------------------------------------------------------- the crooked tower

def tower():
    for y in range(6, 24):                      # hollow the rock out of the lower stages
        k = stage(y)
        for x in range(-17, 18):
            for z in range(-17, 18):
                if sq(x, z, k)[0] <= HW - 2.5:
                    put(x, y, z, None)
    for y in range(6, DECK):
        k = stage(y)
        rel = y - (FLOORS[k] - 1)
        for x in range(-17, 18):
            for z in range(-17, 18):
                d, u, v = sq(x, z, k)
                if HW - 1 < d <= HW:
                    corner = abs(abs(u) - abs(v)) < 1.4 and min(abs(u), abs(v)) > HW - 2
                    if corner:
                        put(x, y, z, s("war_log", axis="y"))
                    elif rel == 0:
                        put(x, y, z, s("crag_ashlar"))
                    elif rel in (5, 6) and (round(u) + round(v)) % 7 == 0:
                        put(x, y, z, s("spiked_iron"))
                    else:
                        put(x, y, z, s("fang_stone") if noise(x, y, z) < 78 or y > 30 else s("crag_rock"))
                elif HW - 3 < d <= HW - 1:
                    put(x, y, z, s("fang_stone"))
        # where this stage overhangs the one below, its own floor shows as a rough ledge
    for i, f in enumerate(FLOORS):
        for x in range(-17, 18):
            for z in range(-17, 18):
                d, u, v = sq(x, z, i)
                if d <= HW - 2.5:
                    put(x, f - 1, z, s("fang_flags"))
                elif d <= HW and get(x, f - 1, z) is None:
                    put(x, f - 1, z, s("crag_ashlar"))
    # arrow slits
    for i, f in enumerate(FLOORS):
        for side in range(4):
            for along in (-5, 5):
                for y in range(f + 2, f + 7):
                    for dep in range(int(HWS[i]) - 3, int(HWS[i]) + 1):
                        u, v = [(along, dep), (dep, along), (along, -dep), (-dep, along)][side]
                        a = math.radians(TURN[i])
                        ox, oz = SHOVE[i]
                        x = round(u * math.cos(a) - v * math.sin(a) + ox)
                        z = round(u * math.sin(a) + v * math.cos(a) + oz)
                        if i == 0 and side == 0:
                            continue
                        if get(x, y, z) is not None and "log" not in str(get(x, y, z)):
                            put(x, y, z, None)


def spikes():
    """iron-tipped stakes bristling off the walls, angled out and down"""
    for i, f in enumerate(FLOORS):
        for side in range(4):
            for along in range(-9, 10, 3):
                if noise(along, f, side) % 3:
                    continue
                y = f + 3 + noise(f, along, side) % 4
                for k in range(0, 5):
                    w = HWS[i] - 0.5 + k
                    u, v = [(along, w), (w, along), (along, -w), (-w, along)][side]
                    a = math.radians(TURN[i])
                    ox, oz = SHOVE[i]
                    x = round(u * math.cos(a) - v * math.sin(a) + ox)
                    z = round(u * math.sin(a) + v * math.cos(a) + oz)
                    if get(x, y, z) is None:
                        put(x, y, z, s("spiked_iron") if k == 4 else s("war_log", axis="x" if side % 2 else "z"))


def hoarding(i):
    """a timber gallery round stage i's top, on raking log braces, sharpened stakes along its rail, a war banner
    hanging off each side"""
    f = FLOORS[i]
    top = (FLOORS[i + 1] if i + 1 < len(FLOORS) else DECK) - 1
    for x in range(-19, 20):
        for z in range(-19, 20):
            d, u, v = sq(x, z, i)
            if HW < d <= HW + 3.5:
                put(x, top, z, s("war_timber"))
                if HW + 2.5 < d:
                    put(x, top + 1, z, slab("war_timber") if (round(u) + round(v)) % 2 else s("war_log", axis="y"))
                    if (round(u) + round(v)) % 4 == 0:
                        put(x, top + 2, z, wall("fang_stone"))
            along = round(v) if abs(u) > abs(v) else round(u)
            if along % 4 == 0 and HW < d <= HW + 2.5:     # posts down the wall, knee braces out under the gallery
                if d <= HW + 1.2:
                    for k in range(1, 5):
                        put(x, top - k, z, s("war_log", axis="y"))
                else:
                    for k in (1, 2):
                        put(x, top - k, z, s("war_log", axis="y"))
    for side in range(4):                              # banners
        for along in (-6, 6):
            e = HWS[i] + 2.8
            u, v = [(along, e), (e, along), (along, -e), (-e, along)][side]
            a = math.radians(TURN[i])
            ox, oz = SHOVE[i]
            for w in (0, 1):
                uu, vv = (u + w, v) if side % 2 == 0 else (u, v + w)
                x = round(uu * math.cos(a) - vv * math.sin(a) + ox)
                z = round(uu * math.sin(a) + vv * math.cos(a) + oz)
                for y in range(top - 9, top):
                    if get(x, y, z) is None:
                        put(x, y, z, s("war_hide"))
                put(x, top - 10, z, slab("war_timber", "top") if get(x, top - 10, z) is None else get(x, top - 10, z))


# ---------------------------------------------------------------- the roof, the drum and the tusks

def roof():
    k = len(FLOORS) - 1
    for x in range(-18, 19):
        for z in range(-18, 19):
            d, u, v = sq(x, z, k)
            if d <= HW + 2:
                put(x, DECK - 1, z, s("fang_flags") if d <= HW - 1 else s("crag_ashlar"))
            if HW + 1 < d <= HW + 2:
                put(x, DECK, z, s("fang_stone") if (round(u) + round(v)) % 3 else wall("fang_stone"))
                if (round(u) + round(v)) % 3 == 0:
                    put(x, DECK + 1, z, s("spiked_iron"))
            if HW < d <= HW + 2:                      # corbels under the overhang
                for y in range(DECK - 3, DECK - 1):
                    if (round(u) + round(v)) % 3 == 0:
                        put(x, y, z, s("war_log", axis="y"))
    # the war drum: a great hide drum on log legs at the back
    cx, cz = 0, -8
    for y in range(DECK, DECK + 6):
        for x in range(cx - 4, cx + 5):
            for z in range(cz - 4, cz + 5):
                r = math.hypot(x - cx, z - cz)
                if y < DECK + 2:
                    if r <= 3.6 and abs(x - cx) == abs(z - cz) and r > 2:
                        put(x, y, z, s("war_log", axis="y"))
                elif r <= 3.6:
                    put(x, y, z, s("war_hide") if y == DECK + 5 else s("war_log", axis="y") if r > 2.8 and (x + z) % 2 else s("war_timber") if r > 2.8 else None)
    for x in range(cx - 3, cx + 4):
        for z in range(cz - 3, cz + 4):
            if math.hypot(x - cx, z - cz) <= 3.2:
                put(x, DECK + 5, z, s("war_hide"))
    # the bonfire in front, skull poles round the arena
    for x in range(-2, 3):
        for z in range(3, 8):
            if abs(x) + abs(z - 5) <= 2:
                put(x, DECK, z, s("war_fire") if abs(x) + abs(z - 5) <= 1 else s("crag_rock"))
    for k2 in range(8):
        a = math.radians(22.5 + 45 * k2)
        x, z = round(math.cos(a) * (HW - 2)), round(math.sin(a) * (HW - 2))
        for y in range(DECK, DECK + 4):
            put(x, y, z, s("war_log", axis="y"))
        put(x, DECK + 4, z, s("fang_bone_pile"))


def tusk(p0, p1, p2, r0, n=400, root="spiked_iron"):
    """a curved tusk along a quadratic bezier, thick at the root and coming to a point"""
    done = set()
    for i in range(n + 1):
        u = i / n
        c = [(1 - u) ** 2 * p0[k] + 2 * (1 - u) * u * p1[k] + u * u * p2[k] for k in range(3)]
        r = max(0.45, r0 * (1 - u) ** 0.8)
        R = int(r) + 2
        for x in range(int(c[0]) - R, int(c[0]) + R + 1):
            for y in range(int(c[1]) - R, int(c[1]) + R + 1):
                for z in range(int(c[2]) - R, int(c[2]) + R + 1):
                    if (x, y, z) in done:
                        continue
                    if math.dist((x, y, z), c) <= r:
                        done.add((x, y, z))
                        put(x, y, z, s("tusk_bone") if u > 0.06 else s(root))


def tusks():
    k = len(FLOORS) - 1
    a = math.radians(TURN[k])
    ox, oz = SHOVE[k]

    def at(u, v, y):
        return (u * math.cos(a) - v * math.sin(a) + ox, y, u * math.sin(a) + v * math.cos(a) + oz)
    # the great tusk: out of the north-east corner, up, and arching across over the arena toward the south-west
    tusk(at(10, -10, DECK - 4), at(18, -18, DECK + 40), at(-10, 10, DECK + 12), 6.0, n=600)
    # the lesser one, off the south-east corner, curling up and back
    tusk(at(10, 10, DECK - 3), at(17, 16, DECK + 14), at(9, 3, DECK + 20), 3.0)
    for (u, v) in ((10, -10), (10, 10)):             # iron bands where they grow out of the stone
        for y in (DECK - 1, DECK):
            for du in range(-4, 5):
                for dv in range(-4, 5):
                    if 3.6 < math.hypot(du, dv) <= 4.8:
                        p = at(u + du, v + dv, y)
                        if get(round(p[0]), y, round(p[2])) is None:
                            put(round(p[0]), y, round(p[2]), s("spiked_iron"))


def skull():
    """a great horned beast's skull nailed over the gate: a heavy brow over deep sockets with an ember far back in
    each, a long tapering snout with its nose-holes and a row of teeth, and horns sweeping out and up"""
    cx, cy, cz = 0, 26, 13
    for x in range(-8, 9):
        for y in range(cy - 8, cy + 8):
            for z in range(cz - 2, cz + 11):
                dx, dy, dz = x - cx, y - cy, z - cz
                w = 6.2 - max(0, dy - 3) * 0.9
                cran = abs(dx) <= w and -1 <= dy <= 6 and -1 <= dz <= 5 - max(0, dy - 4)
                brow = 2.5 <= dy <= 3.8 and abs(dx) <= 6.4 and dz <= 6
                sw = 3.2 - max(0, dz - 5) * 0.28
                snout = abs(dx) <= sw and -6 <= dy <= -1 + (1 if dz < 5 else 0) and 0 <= dz <= 10
                if not (cran or brow or snout):
                    continue
                sock = math.hypot(abs(dx) - 3.0, dy - 1.2) < 1.7 and dy < 2.5
                nose = abs(abs(dx) - 1.0) < 0.6 and -3 <= dy <= -2 and dz >= 9
                if sock and dz >= 1:
                    put(x, y, z, None)
                elif sock:
                    put(x, y, z, s("crag_rock"))
                elif nose:
                    put(x, y, z, None)
                else:
                    put(x, y, z, s("tusk_bone"))
    for sx in (-1, 1):                           # teeth down off the snout's edge
        for z in range(cz + 3, cz + 10, 2):
            put(sx * 3 if z < cz + 7 else sx * 2, cy - 7, z, s("tusk_bone"))
        tusk((sx * 5.5, cy + 3, cz + 1), (sx * 15, cy + 1, cz + 2), (sx * 13, cy + 13, cz + 7), 2.4, root="tusk_bone")
    for x in range(-2, 3):                       # the iron it's nailed up with
        put(x, cy + 7, cz - 1, s("spiked_iron"))


def banners():
    k = len(FLOORS) - 1
    for (u, v) in ((-10, -10), (-10, 10), (10, 10)):
        a = math.radians(TURN[k])
        ox, oz = SHOVE[k]
        x = round(u * math.cos(a) - v * math.sin(a) + ox)
        z = round(u * math.sin(a) + v * math.cos(a) + oz)
        for y in range(DECK, DECK + 14):
            put(x, y, z, s("war_log", axis="y"))
        put(x, DECK + 14, z, s("fang_bone_pile"))
        for y in range(DECK + 6, DECK + 13):    # a hide flag off the pole
            for w in (1, 2, 3):
                put(x + w, y, z, s("war_hide"))


# ---------------------------------------------------------------- inside: the rooms

def mess(t, f):
    for z in range(1, 9):                      # rough tables and a stewpot
        for x in (-5, 5):
            put(x, f, z, s("war_timber") if z in (1, 8) else slab("war_timber", "top"))
    for x in range(-1, 2):
        for z in range(3, 6):
            put(x, f, z, s("spiked_iron") if abs(x) == 1 or z in (3, 5) else s("war_fire"))
    t.chest(-8, f, 8)


def pens(t, f):
    for x in range(-8, 9, 4):                  # log cages
        for z in range(4, 10):
            for y in (f, f + 1, f + 2):
                if z in (4, 9) or x in (-8, 8):
                    if (x + z) % 2 == 0:
                        put(x, y, z, s("war_log", axis="y"))
        put(x, f + 3, 4, slab("war_timber"))
    t.chest(0, f, 7)


def smithy(t, f):
    for x in range(4, 9):
        for z in range(3, 8):
            edge = x in (4, 8) or z in (3, 7)
            put(x, f, z, s("crag_ashlar") if edge else s("war_fire"))
    for x in (-3, -2):
        put(x, f, 5, s("spiked_iron"))
        put(x, f + 1, 5, slab("spiked_iron"))
    for z in range(2, 9, 3):                   # a rack of cleavers
        for y in range(f, f + 3):
            put(-8, y, z, s("war_log", axis="y"))
    t.chest(-6, f, 8)


def shaman(t, f):
    for k in range(6):                         # bone heaps round a fire
        a = math.radians(60 * k)
        x, z = round(math.cos(a) * 5), round(math.sin(a) * 5) + 3
        put(x, f, z, s("fang_bone_pile"))
        if k % 2 == 0:
            put(x, f + 1, z, s("fang_bone_pile"))
    put(0, f - 1, 3, s("war_fire"))
    for x in range(-1, 2):
        for z in range(2, 5):
            if abs(x) + abs(z - 3) == 1:
                put(x, f, z, slab("crag_ashlar"))
    t.chest(0, f, 8)


def trophy(t, f):
    for x in (-8, 8):                          # skulls on poles, banners between
        for z in (0, 4, 8):
            for y in range(f, f + 4):
                put(x, y, z, s("war_log", axis="y"))
            put(x, f + 4, z, s("fang_bone_pile"))
    for z in (2, 6):
        for y in range(f + 2, f + 8):
            put(-9, y, z, s("war_hide"))
            put(9, y, z, s("war_hide"))
    t.chest(0, f, 7)


def war_room(t, f):
    for x in range(-3, 4):                     # a map table of planks on logs
        for z in range(3, 7):
            put(x, f, z, s("war_log", axis="y") if abs(x) == 3 and z in (3, 6) else None)
            put(x, f + 1, z, s("war_timber"))
    t.chest(0, f, 9)


ROOMS = [mess, pens, smithy, shaman, trophy, war_room]
CREWS = [["goblin_cutthroat", "goblin_cutthroat", "orc_brute"], ["goblin_cutthroat", "goblin_cutthroat", "goblin_cutthroat", "orc_raider"],
         ["orc_brute", "orc_raider"], ["goblin_shaman", "goblin_shaman", "goblin_cutthroat"], ["orc_raider", "orc_brute"],
         ["orc_raider", "goblin_shaman", "orc_brute"]]
FOREMEN = ["orc_raider", "orc_brute", "orc_raider", "goblin_shaman", "orc_brute", "warg_rider"]


def build():
    crag()
    tower()
    for i in (1, 3):
        hoarding(i)
    spikes()
    roof()
    tusks()
    skull()
    banners()
    for x in range(-3, 4):                       # the gate's passage through the tower's front wall
        for y in range(6, 13):
            for z in range(8, 16):
                if y <= 12 - (abs(x) == 3):
                    put(x, y, z, None)
    t.interior(ROOMS, CREWS, FOREMEN, boss=[0, DECK, 0, "gorrak"], reward=[5, DECK, -5], ring=lambda f: HW - 6)
    t.ground(52, "coarse_dirt")


def inside(x, z, f):
    return sq(x, z, stage(f))[0] <= HW - 4


def hollow_inside(x, y, z):
    if 0 <= y < 20:
        return math.hypot(x, z) <= 30
    if y < DECK:
        return sq(x, z, stage(y))[0] <= HW - 3
    return math.hypot(x, z) <= 22


build()
if "cut" in sys.argv:
    for q in [q for q in t.b.B if q[0] > 0 and q[2] > 0 and q[1] >= 0]:
        del t.b.B[q]

SHOTS = {
    "front": ((0, 40, 140), (0, 46, 0), 24),
    "three": ((-95, 65, 100), (0, 50, 0), 26),
    "back": ((95, 70, -90), (0, 52, 0), 26),
    "low": ((14, 3, 52), (0, 34, 0), 18),
    "deck": ((-34, 100, 40), (0, 76, 0), 22),
    "cut": ((80, 60, 90), (0, 36, 0), 28),
}

if __name__ == "__main__":
    want = [a for a in sys.argv[1:] if a in SHOTS]
    print("blocks", len(t.b.B))
    if "walk" in sys.argv:
        t.walk((0, 0, 35))
    if "export" in sys.argv:
        t.floor_lights(inside, ("fang_flags",), roof=lambda x, z: sq(x, z, len(FLOORS) - 1)[0] <= HW - 2)
        t.hang_lanterns(lambda f: HW - 6)
        t.export(hollow_inside, DECK + 46)
    elif "cut" in sys.argv:
        K.preview(t.b, "tower_fang_cut", {"cut": SHOTS["cut"]}, sun=(50, -120))
    elif "walk" not in sys.argv:
        K.preview(t.b, "tower_fang", {k: v for k, v in SHOTS.items() if (not want or k in want) and k != "cut"}, sun=(50, -120))
