"""The Clockwork Spire (docs/TOWERS.md) in blocks: a stepped footing, an octagonal iron shaft banded in brass with cogs
turning in its walls and steam pipes up its corners, a square clock stage with a great face each side and a turret
at each corner, and on top a gear-shaped platform on radial brackets - the boss's arena - round a drive-shaft mast
with a caged boiler heart. Floors inside every 10 blocks round the drive shaft.

    python tools/towers/clockwork_spire.py [shots...]
    E:/Steam/steamapps/common/Blender/blender.exe -b -P E:/Ashbound/tools/blender/preview_struct.py -- tower_clockwork [shots...]
"""
import math
import os
import sys

sys.path.insert(0, "E:/Ashbound/tools")
import structkit as K  # noqa: E402

K.GLOW.update({"clock_glass": 0.8, "boiler_glow": 1.6})

A = "ashbound:"
b = K.Build(7)
put = b.put

SHAFT_TOP = 56         # the octagon gives way to the square clock stage
STAGE_TOP = 81         # the clock stage's walls run up to the deck's underside
DECK = 82              # the roof platform's floor
FLOORS = [6, 16, 26, 36, 46, 56, 66]
APOTHEM = 12           # the shaft's half-width below TAPER, one less above
TAPER = 36
STAGE = 13             # the clock stage's half-width
CLOCK_Y = 67


def ap(y):
    return APOTHEM if y < TAPER else APOTHEM - 1


def corner(x, z, a):
    """on one of the octagon's eight corners (22.5 + 45k degrees): the pilasters stand there"""
    ang = math.atan2(z, x)
    k = round((ang - math.radians(22.5)) / math.radians(45))
    c = math.radians(22.5) + k * math.radians(45)
    return abs(math.hypot(x, z) * math.sin(ang - c)) < 1.3
DECK_R = 20.5


def s(name, **p):
    n = name if ":" in name else A + name
    return n + ("[" + ",".join("%s=%s" % kv for kv in p.items()) + "]" if p else "")


def oct_d(x, z):
    return max(abs(x), abs(z), (abs(x) + abs(z)) * 0.7071)


def slab(name, half="bottom"):
    return s(name + "_slab", type=half, waterlogged="false")


def stairs(name, facing, half="bottom"):
    return s(name + "_stairs", facing=facing, half=half, shape="straight", waterlogged="false")


def facing_out(x, z):
    return ("east" if x > 0 else "west") if abs(x) >= abs(z) else ("south" if z > 0 else "north")


# ---------------------------------------------------------------- the footing

def footing():
    for x in range(-18, 19):
        for z in range(-18, 19):
            d = oct_d(x, z)
            for y in range(0, 6):
                a = 18.5 if y < 3 else 16.5 if y < 5 else 15
                if d <= a:
                    edge = d > a - 1
                    put(x, y, z, s("spire_footing") if (y < 3 or edge) else s("foundry_bricks"))
            if 15 < d <= 16:
                put(x, 5, z, slab("spire_footing"))
            if 18.5 < d <= 19.5:
                put(x, 0, z, slab("spire_footing"))
            for y in range(-3, 0):
                if d <= 19.5:
                    put(x, y, z, s("spire_footing"))
    # the stair up to the door, on the south
    for k in range(6):
        for x in range(-3, 4):
            z = 16 + k
            for y in range(0, 5 - k):
                put(x, y, z, s("spire_footing"))
            put(x, 5 - k, z, stairs("spire_footing", "north"))
        for cx in (-4, 4):
            for y in range(-3, 5 - k):
                put(cx, y, 16 + k, s("spire_footing"))
            put(cx, 5 - k, 16 + k, s("spire_footing_wall", **RAIL))
            if k in (0, 5):
                put(cx, 6 - k, 16 + k, s("spire_lantern", hanging="false", waterlogged="false"))


# ---------------------------------------------------------------- the shaft

def shaft():
    for y in range(6, SHAFT_TOP):
        a = ap(y)
        band = y in FLOORS or y == TAPER - 1
        under = any(y - f == 1 for f in FLOORS)
        for x in range(-a - 1, a + 2):
            for z in range(-a - 1, a + 2):
                d = oct_d(x, z)
                if a - 1 < d <= a:                 # the skin: bands and corner pilasters proud, panels set back
                    if band:
                        put(x, y, z, s("brass_plate"))
                    elif corner(x, z, a) and any(y - f == 5 for f in FLOORS):
                        put(x, y, z, s("boiler_glow"))
                    elif under or corner(x, z, a):
                        put(x, y, z, s("spire_column", axis="y"))
                elif a - 2 < d <= a - 1:
                    put(x, y, z, s("blackiron_plate"))
                elif a - 3 < d <= a - 2:
                    put(x, y, z, s("foundry_bricks"))
                elif a < d <= a + 1 and any(y - f == 2 for f in FLOORS):
                    put(x, y, z, slab("blackiron_plate", "top"))           # a lip above each band
    # lancet windows: three a side on the cardinal faces, mid-floor, clear leaded glass to let the day in, an
    # amber-lit transom at the head of each
    for f in FLOORS:
        if f >= SHAFT_TOP:
            continue
        for side in ("north", "south", "east", "west"):
            for off in (-3, 0, 3):
                if off == 0 and side == "south" and f == FLOORS[0]:
                    continue                    # the door is there
                a = ap(f + 5)
                for y in range(f + 3, f + 9):
                    x, z = side_xy(side, off, a - 1)
                    put(x, y, z, s("clock_glass") if y == f + 8 else s("leaded_glass_pane"))
                    for k in (0, 1):
                        x, z = side_xy(side, off + k * (1 if off > 0 else -1) * 0, a - 2)
                        put(x, y, z, None)
                    for e in (-1, 1):
                        x, z = side_xy(side, off + e, a)
                        put(x, y, z, s("blackiron_plate"))
                x, z = side_xy(side, off, a)
                put(x, f + 9, z, s("blackiron_plate"))
                x, z = side_xy(side, off, a + 1)
                put(x, f + 2, z, slab("blackiron_plate", "top"))
                put(x, f + 9, z, stairs("blackiron_plate", opposite(side), "top"))


def side_xy(side, along, out):
    return {"north": (along, -out), "south": (along, out), "east": (out, along), "west": (-out, along)}[side]


def opposite(side):
    return {"north": "south", "south": "north", "east": "west", "west": "east"}[side]


def door():
    for x in range(-2, 3):
        for y in range(6, 13):
            top = 12 - (1 if abs(x) == 2 else 0)
            for z in range(APOTHEM - 3, APOTHEM + 2):
                if y <= top:
                    put(x, y, z, None)
    for x in range(-3, 4):
        put(x, 13, APOTHEM + 1, s("brass_plate"))
        put(x, 14, APOTHEM + 1, slab("brass_plate"))
    for y in range(6, 13):
        put(-3, y, APOTHEM + 1, s("spire_column", axis="y"))
        put(3, y, APOTHEM + 1, s("spire_column", axis="y"))
    put(0, 15, APOTHEM + 1, s("brass_gear_block"))
    for z in (APOTHEM - 2, APOTHEM + 1):
        put(0, 12, z, s("spire_lantern", hanging="true", waterlogged="false"))


def gear(cx, cy, plane, at, r=5.2, mat="brass_plate"):
    """a great cog half-sunk in a wall: a one-block rim, chunky teeth two blocks wide, four spokes, a shaft hub, in
    the plane x = at or z = at; the dark panel behind shows between the spokes"""
    teeth = max(6, round(2 * math.pi * r / 4))
    for u in range(-8, 9):
        for v in range(-8, 9):
            rr = math.hypot(u, v)
            a = math.atan2(v, u)
            tooth = r - 0.5 < rr <= r + 1.1 and (a * teeth / (2 * math.pi) + 0.25) % 1 < 0.5
            rim = r - 1.5 < rr <= r - 0.5
            spoke = rr <= r - 1.5 and (abs(u) < 0.6 or abs(v) < 0.6)
            p = (at, cy + v, cx + u) if plane == "x" else (cx + u, cy + v, at)
            if rr < 1.2:
                put(*p, s("drive_shaft", axis="x" if plane == "x" else "z"))
            elif tooth or rim:
                put(*p, s(mat))
            elif spoke:
                put(*p, s("blackiron_plate"))


def gears():
    gear(0, 26, "z", APOTHEM, r=5.4)
    gear(0, 31, "x", APOTHEM, r=4.4)
    gear(0, 42, "z", -APOTHEM + 1, r=4.6)
    gear(0, 22, "x", -APOTHEM, r=5.6)


def pipes():
    for sx in (-1, 1):
        for sz in (-1, 1):
            for y in range(1, SHAFT_TOP + 1):
                k = next(k for k in range(4, 14) if oct_d(k, k) > ap(y))
                x, z = k * sx, k * sz
                if b.get(x, y, z) is None or "pipe" in str(b.get(x, y, z)):
                    put(x, y, z, s("steam_pipe", axis="y"))
                if y % 7 == 6:
                    put(x - sx, y, z, s("brass_plate"))
                    put(x, y, z - sz, s("brass_plate"))
                if y == TAPER:                  # where the shaft steps in, the pipe jogs in with it
                    put(x + sx, y - 1, z + sz, s("brass_plate"))


# ---------------------------------------------------------------- the clock stage

def stage():
    h = STAGE
    for y in range(SHAFT_TOP, STAGE_TOP + 1):
        for x in range(-h, h + 1):
            for z in range(-h, h + 1):
                edge = max(abs(x), abs(z))
                if edge == h:
                    band = y in (SHAFT_TOP, STAGE_TOP)
                    put(x, y, z, s("brass_plate") if band else s("blackiron_plate"))
                elif edge == h - 1:
                    put(x, y, z, s("foundry_bricks"))
    # the shoulder where the octagon meets the square
    for x in range(-h - 1, h + 2):
        for z in range(-h - 1, h + 2):
            if max(abs(x), abs(z)) == h + 1:
                put(x, SHAFT_TOP, z, slab("blackiron_plate", "top"))
                put(x, STAGE_TOP, z, slab("brass_plate", "top"))
            if oct_d(x, z) > ap(SHAFT_TOP - 1) and max(abs(x), abs(z)) <= h:
                put(x, SHAFT_TOP - 1, z, stairs("blackiron_plate", "north", "top") if False else slab("blackiron_plate", "top"))
    # turrets at the corners, up through the deck to pointed caps
    for sx in (-1, 1):
        for sz in (-1, 1):
            for y in range(SHAFT_TOP - 4, DECK + 9):
                for dx in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        x, z = sx * h + dx, sz * h + dz
                        corner = abs(dx) + abs(dz) == 2
                        put(x, y, z, s("spire_column", axis="y") if corner else s("blackiron_plate"))
            for k, y in enumerate(range(DECK + 9, DECK + 15)):
                r = max(0, 2 - k // 2)
                for dx in range(-r, r + 1):
                    for dz in range(-r, r + 1):
                        put(sx * h + dx, y, sz * h + dz, s("brass_plate") if k % 2 else s("blackiron_plate"))
            put(sx * h, DECK + 15, sz * h, s("spire_column", axis="y"))
            put(sx * h, DECK + 16, sz * h, s("spire_column", axis="y"))
            put(sx * h, DECK + 17, sz * h, s("boiler_glow"))


def clock(side, cy=CLOCK_Y, r=8.6):
    """a great face set into the wall: a brass rim proud of it, the amber glass a block back, iron hour marks and
    hands flush with the wall in front of the glass"""
    h = STAGE
    for u in range(-10, 11):
        for v in range(-10, 11):
            rr = math.hypot(u, v)
            if rr > r + 0.6:
                continue
            y = cy + v
            front, skin, back = (side_xy(side, u, k) for k in (h + 1, h, h - 1))
            if rr > r - 0.6:
                put(*(front[0], y, front[1]), s("brass_plate"))
                put(*(skin[0], y, skin[1]), s("brass_plate"))
                continue
            put(back[0], y, back[1], s("clock_glass"))
            a = math.degrees(math.atan2(v, u)) % 360
            off = min(a % 30, 30 - a % 30) * math.pi / 180 * rr        # blocks off the nearest hour line
            long_ = min(a % 90, 90 - a % 90) < 15
            mark = off < 0.55 and rr > r - (2.6 if long_ else 1.6)
            put(skin[0], y, skin[1], s("blackiron_plate") if mark else None)
    # hands: hour toward ten, minute toward two, a brass boss on the arbour
    for ang, ln in ((150, 4.4), (60, 6.6)):
        for t in range(0, int(ln * 3) + 1):
            u = round(math.cos(math.radians(ang)) * t / 3)
            v = round(math.sin(math.radians(ang)) * t / 3)
            x, z = side_xy(side, u, h)
            put(x, cy + v, z, s("blackiron_plate"))
    x, z = side_xy(side, 0, h + 1)
    put(x, cy, z, s("brass_gear_block"))
    x, z = side_xy(side, 0, h)
    put(x, cy, z, s("brass_plate"))


def buttresses():
    """eight stepped buttresses at the shaft's corners, the footing's stone, up to the second band"""
    for y in range(6, 19):
        depth = 3 if y < 10 else 2 if y < 15 else 1
        for x in range(-17, 18):
            for z in range(-17, 18):
                d = oct_d(x, z)
                if APOTHEM < d <= APOTHEM + depth and corner(x, z, APOTHEM) and b.get(x, y, z) is None:
                    top = y in (9, 14, 18)
                    put(x, y, z, slab("spire_footing") if top and d > APOTHEM + depth - 1 else s("spire_footing"))


# ---------------------------------------------------------------- the deck and its mast

def deck():
    # radial brackets under the deck, and its underside
    for y in range(DECK - 12, DECK):
        for x in range(-22, 23):
            for z in range(-22, 23):
                rr = math.hypot(x, z)
                if max(abs(x), abs(z)) <= STAGE:
                    continue
                a = math.degrees(math.atan2(z, x)) % 45
                fin = (a < 4 or a > 41) and rr <= STAGE + 1 + (y - (DECK - 12) + 1) * 0.75
                if fin and rr < DECK_R:
                    put(x, y, z, s("blackiron_plate"))
                if y == DECK - 1 and rr < DECK_R:
                    put(x, y, z, s("blackiron_plate"))
    teeth = 18
    for x in range(-24, 25):
        for z in range(-24, 25):
            rr = math.hypot(x, z)
            a = math.atan2(z, x)
            if rr <= DECK_R:
                ring = int(rr) % 6
                put(x, DECK, z, s("brass_plate") if rr > DECK_R - 1.2 else s("gearwright_tiles") if ring in (0, 1, 2, 3) else s("brass_grating"))
                if DECK_R - 1.2 < rr <= DECK_R:
                    put(x, DECK - 1, z, s("brass_plate"))
            elif rr <= DECK_R + 2 and (a * teeth / (2 * math.pi)) % 1 < 0.5:
                put(x, DECK, z, s("brass_plate"))
                put(x, DECK - 1, z, s("brass_plate"))
                if rr > DECK_R + 1:
                    put(x, DECK + 1, z, s("foundry_brick_wall", up="true", north="none", south="none", east="none", west="none",
                                          waterlogged="false"))
                    if int(a * teeth / (2 * math.pi) + teeth) % 2 == 0:
                        put(x, DECK + 2, z, s("spire_lantern", hanging="false", waterlogged="false"))
    for k in range(8):
        ang = math.radians(22.5 + 45 * k)
        for r in (7.5, 13.5):
            put(round(math.cos(ang) * r), DECK, round(math.sin(ang) * r), s("boiler_glow"))
    # the mast: the drive shaft up out of the deck, a caged boiler heart, a spike
    for y in range(DECK + 1, DECK + 14):
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                put(dx, y, dz, s("drive_shaft", axis="y") if abs(dx) + abs(dz) < 2 else s("blackiron_plate"))
    heart = DECK + 17
    for x in range(-4, 5):
        for y in range(heart - 4, heart + 5):
            for z in range(-4, 5):
                rr = math.sqrt(x * x + (y - heart) ** 2 + z * z)
                if rr <= 1.8:
                    put(x, y, z, s("boiler_glow"))
                elif 3.4 < rr <= 4.2 and (abs(x) <= 0 or abs(z) <= 0 or y == heart):
                    put(x, y, z, s("brass_plate"))
    for k in range(-4, 5):             # the shaft runs on through the heart, spokes tie the cage to it
        put(0, heart + k, 0, s("drive_shaft", axis="y") if abs(k) > 1 else s("boiler_glow"))
        put(k, heart, 0, s("drive_shaft", axis="x") if abs(k) > 1 else s("boiler_glow"))
        put(0, heart, k, s("drive_shaft", axis="z") if abs(k) > 1 else s("boiler_glow"))
    for y in range(heart + 4, heart + 12):
        put(0, y, 0, s("spire_column", axis="y") if y < heart + 10 else s("brass_plate"))


# ---------------------------------------------------------------- inside: floors round the drive shaft

def floors():
    for f in FLOORS:
        top = SHAFT_TOP if f < SHAFT_TOP else STAGE_TOP
        for x in range(-STAGE, STAGE + 1):
            for z in range(-STAGE, STAGE + 1):
                inside = oct_d(x, z) <= APOTHEM - 2 if f < SHAFT_TOP else max(abs(x), abs(z)) <= STAGE - 2
                if inside:
                    put(x, f - 1, z, s("gearwright_tiles"))
        del top
    for y in range(5, DECK):
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                put(dx, y, dz, s("drive_shaft", axis="y") if abs(dx) + abs(dz) < 2 else s("brass_plate"))


# ---------------------------------------------------------------- inside: stairs, rooms, and where things go

MARKS = {"mobs": [], "foremen": [], "chests": [], "seals": [], "boss": None}
FACE = ["east", "south", "west", "north"]
RAIL = dict(up="true", north="none", south="none", east="none", west="none", waterlogged="false")


def rot(x, z, q):
    for _ in range(q % 4):
        x, z = -z, x
    return x, z


def flight(f, q, steps, x0=-5):
    """a straight stair three wide along a wall, rising a block a step from floor f, turned q quarter-turns; the
    floor above opened over its upper part with a rail round the opening; the seal's place at the top"""
    for k in range(steps):
        for zz in (-6, -5, -4):
            x, z = rot(x0 + k, zz, q)
            for y in range(f, f + k):
                put(x, y, z, s("foundry_bricks"))
            put(x, f + k, z, stairs("foundry_brick", FACE[q % 4]))
            for y in range(f + k + 1, f + k + 4):
                put(x, y, z, None)
    top = f + steps
    for k in range(steps):
        x, z = rot(x0 + k, -3, q)
        for y in range(f, min(f + k, top - 2) + 1):
            put(x, y, z, s("foundry_bricks"))
        if f + k + 1 <= top - 2:
            put(x, f + k + 1, z, s("foundry_brick_wall", **RAIL))
            if k % 4 == 2 and f + k + 2 <= top - 3:
                put(x, f + k + 2, z, s("spire_lantern", hanging="false", waterlogged="false"))
    for k in range(steps // 3, steps - 1):          # the last step is the upper floor's own level
        for zz in (-6, -5, -4):
            x, z = rot(x0 + k, zz, q)
            put(x, top - 1, z, None)
        x, z = rot(x0 + k, -3, q)
        put(x, top, z, s("foundry_brick_wall", **RAIL))
    for zz in (-6, -5, -4):
        x, z = rot(x0 + steps // 3 - 1, zz, q)
        put(x, top, z, s("foundry_brick_wall", **RAIL))


def boilers(f):
    for cx in (-5, 5):
        cz = 4
        for y in range(f, f + 8):
            for x in range(cx - 3, cx + 4):
                for z in range(cz - 3, cz + 4):
                    rr = math.hypot(x - cx, z - cz)
                    if rr <= 2.6:
                        put(x, y, z, s("blackiron_plate") if y in (f + 2, f + 6) else s("brass_plate"))
        for x in range(cx - 1, cx + 2):
            put(x, f, cz - 3, s("boiler_glow"))
            put(x, f + 1, cz - 3, s("boiler_glow"))
        put(cx, f + 8, cz, s("steam_pipe", axis="y"))
    MARKS["chests"].append([-4, f, 8])


def foundry(f):
    for cx, cz in ((-4, 4), (4, 4)):
        for x in range(cx - 2, cx + 3):
            for z in range(cz - 2, cz + 3):
                edge = max(abs(x - cx), abs(z - cz)) == 2
                put(x, f, z, s("foundry_bricks") if edge else s("boiler_glow"))
    MARKS["chests"].append([0, f, 7])


def assembly(f):
    for cx, cz in ((-6, 2), (-2, 6), (3, 6), (6, 1)):
        for y in range(f, f + 5):
            for dx in (-1, 1):
                put(cx + dx, y, cz, s("spire_column", axis="y"))
        for dx in (-1, 0, 1):
            put(cx + dx, f + 5, cz, s("blackiron_plate"))
        MARKS["mobs"].append([cx, f, cz - 1, "brass_sentry"])
    MARKS["chests"].append([0, f, 7])


def archive(f):
    a = ap(f + 2)
    for x in range(-a, a + 1):
        for z in range(-a, a + 1):
            if a - 4 < oct_d(x, z) <= a - 3 and z > -2:
                for y in range(f, f + 4):
                    put(x, y, z, s("soot_planks") if y != f + 2 else slab("soot_plank", "top"))
    for cx, cz in ((-3, 3), (3, 3)):
        for dx in (-1, 0, 1):
            for dz in (0, 1):
                put(cx + dx, f + 1, cz + dz, slab("soot_plank", "top"))
        put(cx - 1, f, cz, s("spire_column", axis="y"))
        put(cx + 1, f, cz + 1, s("spire_column", axis="y"))
    MARKS["chests"].append([0, f, 6])


def disc(cx, y, cz, r, mat):
    teeth = max(6, round(2 * math.pi * r / 4))
    for x in range(int(cx - r - 2), int(cx + r + 3)):
        for z in range(int(cz - r - 2), int(cz + r + 3)):
            rr = math.hypot(x - cx, z - cz)
            a = math.atan2(z - cz, x - cx)
            if rr <= r or (rr <= r + 1.1 and (a * teeth / (2 * math.pi)) % 1 < 0.5):
                put(x, y, z, s(mat) if rr > r - 1 or rr < 1 else s("brass_grating"))


def gear_hall(f):
    for cx, cz, h, r in ((-4, 4, 3, 3.4), (4, 3, 6, 3.0)):
        for y in range(f, f + h):
            put(cx, y, cz, s("drive_shaft", axis="y"))
        disc(cx, f + h, cz, r, "brass_plate")
    MARKS["chests"].append([4, f + 7, 3])


def clock_room(f):
    for cx in (-5, 5):
        gear(0, f + 5, "x", cx, r=3.0)
    MARKS["chests"].append([0, f, 8])


def pendulum(f):
    for y in range(f + 6, DECK - 1):
        put(0, y, 7, s("drive_shaft", axis="y"))
    for u in range(-3, 4):
        for v in range(-3, 4):
            if math.hypot(u, v) <= 2.7:
                put(u, f + 3 + v, 7, s("brass_plate") if math.hypot(u, v) > 1.5 else s("blackiron_plate"))
    MARKS["chests"].append([-8, f, 8])


ROOMS = [boilers, foundry, assembly, archive, gear_hall, clock_room, pendulum]
CREW = [["cogling", "cogling", "brass_sentry"], ["steam_hulk", "cogling"], ["brass_sentry", "cogling"],
        ["tinker_adept", "tinker_adept", "brass_sentry"], ["cogling", "cogling", "cogling", "tinker_adept"],
        ["brass_sentry", "steam_hulk"], ["steam_hulk", "brass_sentry", "tinker_adept"]]


def side(i):
    """the stairs climb along the north wall eastward, then the south wall westward, and so on: each floor is
    crossed to reach the next flight"""
    return 0 if i % 2 == 0 else 2


def stair_cols(i):
    """the columns floor i's stair needs kept clear, and those round the opening it comes up through"""
    f = FLOORS[i]
    steps, x0 = (10, -5) if i < len(FLOORS) - 1 else (DECK + 1 - f, -9)
    own = {rot(x0 + k, zz, side(i)) for k in range(-1, steps + 2) for zz in range(-7, -2)}
    above = {rot(x0 + k, zz, side(i)) for k in range(steps // 3 - 2, steps + 3) for zz in range(-7, -1)}
    return own, above


def guarded(x, y, z, st, nbt=None):
    if (x, z) in GUARD:
        return
    b.put(x, y, z, st, nbt)


GUARD = set()


def interior():
    global put, GUARD
    for i, f in enumerate(FLOORS):
        if i < len(FLOORS) - 1:
            flight(f, side(i), 10)
        else:
            flight(f, side(i), DECK + 1 - f, x0=-9)
    for i, f in enumerate(FLOORS):
        GUARD = stair_cols(i)[0] | (stair_cols(i - 1)[1] if i else set())
        put = guarded
        try:
            ROOMS[i](f)
        finally:
            put = b.put
        a = ap(f + 2) - 4 if f < SHAFT_TOP else STAGE - 3
        for k, kind in enumerate(CREW[i]):
            ang = math.radians(60 + k * 70)
            MARKS["mobs"].append([round(math.cos(ang) * a), f, round(math.sin(ang) * a), kind])
        MARKS["foremen"].append([0, f, round(a * 0.7), "clockwork_duelist" if i == 5 else ["brass_sentry", "steam_hulk"][i % 2]])
    MARKS["boss"] = [0, DECK + 1, 10, "grand_horologe"]
    MARKS["reward"] = [0, DECK + 1, 4]


def ground():
    for x in range(-48, 49):
        for z in range(-48, 49):
            if math.hypot(x, z) < 48 and b.get(x, -1, z) is None:
                put(x, -1, z, "grass_block[snowy=false]")


footing()
floors()
shaft()
door()
gears()
buttresses()
pipes()
stage()
for sd in ("north", "south", "east", "west"):
    clock(sd)
deck()
interior()
ground()
if "cut" in sys.argv:                     # the cutaway: a quarter of the tower taken off to show the floors
    for q in [q for q in b.B if q[0] > 0 and q[2] > 0 and q[1] >= 0]:
        del b.B[q]

SHOTS = {
    "front": ((0, 30, 120), (0, 48, 0), 24),
    "three": ((-80, 55, 85), (0, 50, 0), 26),
    "low": ((12, 2, 40), (0, 40, 0), 18),
    "deck": ((-30, 95, 30), (0, 76, 0), 20),
    "clock": ((-18, 62, 38), (0, 67, 13), 26),
    "night": ((-80, 55, 85), (0, 50, 0), 26),
    "cut": ((70, 50, 80), (0, 44, 0), 28),
    "cuthigh": ((40, 80, 46), (0, 70, 0), 24),
}

if __name__ == "__main__":
    want = sys.argv[1:]
    print("blocks", len(b.B))
    if "cut" in want:
        K.preview(b, "tower_clockwork_cut", {k: SHOTS[k] for k in ("cut", "cuthigh")}, sun=(55, -135))
    elif "night" in want:
        K.preview(b, "tower_clockwork_night", {"night": SHOTS["night"]}, sun=(30, -30), sky=(0.03, 0.03, 0.06), night=True)
    else:
        K.preview(b, "tower_clockwork", {k: v for k, v in SHOTS.items() if (not want or k in want) and k != "night"}, sun=(55, -135))


def walk():
    """can you walk from the door to the deck without jumping? (stairs climb a block; drops up to 3)"""
    from collections import deque
    B = b.B

    def free(x, y, z):
        st = B.get((x, y, z))
        return st is None or "_slab[type=bottom" in st and False

    def stand(x, y, z):
        below = B.get((x, y - 1, z))
        return below is not None and "_wall" not in below and free(x, y, z) and free(x, y + 1, z)

    start = (0, 6, APOTHEM + 2)
    seen, todo = {start}, deque([start])
    while todo:
        x, y, z = todo.popleft()
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, nz = x + dx, z + dz
            for ny in (y, y + 1, y - 1, y - 2, y - 3):
                if ny == y + 1 and "_stairs" not in str(B.get((nx, y, nz))):
                    continue
                if stand(nx, ny, nz) and abs(nx) < 30 and abs(nz) < 30 and (nx, ny, nz) not in seen:
                    seen.add((nx, ny, nz))
                    todo.append((nx, ny, nz))
                    break
    for f in FLOORS + [DECK + 1]:
        print("floor", f, "reached" if any(p[1] == f for p in seen) else "NOT reached")


if "walk" in sys.argv:
    walk()


# ---------------------------------------------------------------- into the game

GAME = "E:/EFTest/game/src/main/resources/"
LOOT = "ashbound:chests/tower_clockwork"


def lanterns():
    """lanterns on chains under every ceiling, kept off the stairs"""
    for i, f in enumerate(FLOORS):
        ceil = (FLOORS[i + 1] - 1) if i + 1 < len(FLOORS) else DECK - 1
        keep = stair_cols(i)[0] | (stair_cols(i - 1)[1] if i else set())
        r = (ap(f + 2) - 5) if f < SHAFT_TOP else STAGE - 5
        for k in range(8):
            ang = math.radians(22.5 + 45 * k)
            x, z = round(math.cos(ang) * r), round(math.sin(ang) * r)
            if (x, z) in keep or b.get(x, ceil, z) is None or b.get(x, ceil - 1, z) is not None:
                continue
            drop = 2 if ceil - f > 10 else 1
            for y in range(ceil - drop, ceil):
                put(x, y, z, s("spire_chain", axis="y", waterlogged="false"))
            put(x, ceil - drop - 1, z, s("spire_lantern", hanging="true", waterlogged="false"))


def sconces():
    """fire grates two high in the inner wall on the four diagonal faces of every shaft floor"""
    for i, f in enumerate(FLOORS):
        if f >= SHAFT_TOP:
            continue
        keep = stair_cols(i)[0] | (stair_cols(i - 1)[1] if i else set())
        a = ap(f + 2)
        k = 7 if a == APOTHEM else 6
        for sx in (-1, 1):
            for sz in (-1, 1):
                x, z = sx * k, sz * k
                if (x, z) in keep or (x - sx, z - sz) in keep:
                    continue
                for y in (f + 2, f + 3):
                    put(x, y, z, s("boiler_glow"))


def floor_lights():
    """a grate every four blocks in each floor slab (it lights the floor and the ceiling of the room under it), kept
    off the stairs, their openings and the drive shaft"""
    for i, f in enumerate(FLOORS):
        keep = stair_cols(i)[0] | (stair_cols(i - 1)[1] if i else set())
        for x in range(-12, 13):
            for z in range(-12, 13):
                if x % 4 != 2 or z % 4 != 2 or (x, z) in keep or max(abs(x), abs(z)) <= 2:
                    continue
                inside = oct_d(x, z) <= APOTHEM - 4 if f < SHAFT_TOP else max(abs(x), abs(z)) <= STAGE - 3
                under = str(b.get(x, f - 1, z))
                if inside and ("gearwright_tiles" in under or "blackiron_plate_slab[type=top" in under) and b.get(x, f, z) is None:
                    put(x, f - 1, z, s("boiler_glow"))
    for x in range(-18, 19):                    # and the roof
        for z in range(-18, 19):
            if x % 5 == 0 and z % 5 == 0 and math.hypot(x, z) <= DECK_R - 3 and max(abs(x), abs(z)) > 2                     and "gearwright_tiles" in str(b.get(x, DECK, z)):
                put(x, DECK, z, s("boiler_glow"))


def coffers():
    for x, y, z in MARKS["chests"]:
        if b.get(x, y, z) is None and b.get(x, y - 1, z) is not None:
            put(x, y, z, s("spire_coffer", facing="north", waterlogged="false"), {"LootTable": LOOT})


def foundation():
    """the footing carried down into the ground, so on a slope it stands on a plinth, never on air"""
    for x in range(-20, 21):
        for z in range(-20, 21):
            if oct_d(x, z) <= 19.5:
                for y in range(-9, -3):
                    put(x, y, z, s("spire_footing"))


def hollow():
    """cave air (the placer keeps it, unlike air) in every room and round the footing, so a hill the tower is set
    into is cut back instead of filling its floors"""
    for y in range(0, DECK + 30):
        for x in range(-24, 25):
            for z in range(-24, 25):
                if (x, y, z) in b.B:
                    continue
                inside = (oct_d(x, z) <= ap(y) - 3 and 6 <= y < SHAFT_TOP) or \
                         (max(abs(x), abs(z)) <= STAGE - 2 and SHAFT_TOP <= y < DECK) or \
                         (y >= 0 and oct_d(x, z) <= 23 and y < 30) or (y > DECK and math.hypot(x, z) <= 23)
                if inside:
                    b.B[(x, y, z)] = "minecraft:cave_air"


def export():
    lanterns()
    sconces()
    floor_lights()
    coffers()
    foundation()
    K.connect(b)
    hollow()
    for q in [q for q, st in b.B.items() if "grass_block" in st]:
        del b.B[q]
    xs, ys, zs = zip(*b.B)
    mn = (min(xs), min(ys), min(zs))
    size = [max(xs) - mn[0] + 1, max(ys) - mn[1] + 1, max(zs) - mn[2] + 1]
    pal, idx, blocks = [], {}, []
    for p in sorted(b.B, key=lambda q: (q[1], q[2], q[0])):
        st = b.B[p]
        if st not in idx:
            idx[st] = len(pal)
            name_, props = K.parse(st)
            e = {"Name": name_}
            if props:
                e["Properties"] = dict(props)
            pal.append(e)
        e = {"pos": [p[0] - mn[0], p[1] - mn[1], p[2] - mn[2]], "state": idx[st]}
        if p in b.nbt:
            e["nbt"] = b.nbt[p]
        blocks.append(e)
    root = {"DataVersion": 3955, "size": size, "palette": pal, "blocks": blocks, "entities": []}
    path = GAME + "data/ashbound/structure/tower/clockwork_spire.nbt"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    K.write_nbt(path, root)
    foot = [0 - mn[0], -1 - mn[1], 0 - mn[2]]       # the ground block under the door's axis
    op = GAME + "data/ashbound/tree/offsets.json"
    offs = json.load(open(op))
    offs["clockwork_spire"] = foot
    json.dump(offs, open(op, "w"), indent=2)
    # where things go, from the same foot: the tower's runtime reads these
    marks = dict(MARKS, foot="marks are in the tower's own frame: (0, 0, 0) stands on the ground block at the foot")
    mp = GAME + "data/ashbound/tower/clockwork_spire.json"
    os.makedirs(os.path.dirname(mp), exist_ok=True)
    json.dump(marks, open(mp, "w"), indent=1)
    print("template", size, len(blocks), "blocks,", len(pal), "states,", os.path.getsize(path) // 1024, "KB; foot", foot)
    loot()


def loot():
    """the floor coffers and the Horologe's hoard (towerloot.py: no dungeon gear, the world's weapons)"""
    import towerloot
    towerloot.write("clockwork", "clockwork_spire", goods=[("minecraft:copper_ingot", 4, 3, 9), ("minecraft:redstone", 3, 2, 8)])


if "export" in sys.argv:
    import json
    export()
