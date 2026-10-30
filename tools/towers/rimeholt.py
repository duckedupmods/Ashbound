"""Rimeholt, the Giant's Keep (docs/TOWERS.md, the snows) in blocks: a frost giant's round keep of blue-black granite
cut to a giant's scale, on a crag of frost-split rock. Leaning buttresses ride up it like ribs, rune bands burn cold
blue round every floor, icicles hang off every course - and the keep is being split open by ice: great glowing
crystals burst out of its walls, and a crown of ice spikes rises round its roof, where the Jarl's ice throne stands.

    python tools/towers/rimeholt.py [shots...] [cut] [walk] [export]
    E:/Steam/steamapps/common/Blender/blender.exe -b -P E:/Ashbound/tools/blender/preview_struct.py -- tower_rimeholt [shots...]
"""
import math
import sys

import towerkit as TK
from towerkit import K, s, slab, stairs, wall

K.GLOW.update({"rune_glow": 1.4, "ice_glow": 1.1, "rune_band": 0.25})

FLOORS = [6, 16, 26, 36, 46, 56]
DECK = 66
R = 14.5                    # the keep's outer radius above the batter
INNER = 11                  # the rooms reach this radius

t = TK.Tower("rimeholt", "rimeholt", "rimeholt", brick="rime_brick", fill="rime_bricks", px="rime",
             floors=FLOORS, deck=DECK, glow="rune_glow", goods=[("minecraft:packed_ice", 4, 2, 6), ("minecraft:cooked_salmon", 4, 2, 6)])
t.biomes = ["minecraft:snowy_plains", "minecraft:snowy_taiga", "minecraft:grove", "minecraft:snowy_slopes",
            "minecraft:frozen_peaks", "minecraft:jagged_peaks", "minecraft:ice_spikes"]
put, get = t.put, t.get


def frost(x, y, z):
    v = math.sin(x * 0.29 + y * 0.21) + math.sin(z * 0.33 - y * 0.17) + math.sin((x + z) * 0.23 - y * 0.09)
    return v > 1.5


def rad(y):
    """the keep's radius at a height: battered out at the foot"""
    return R + max(0.0, (16 - y) * 0.22) if y < 16 else R


# ---------------------------------------------------------------- the crag it stands on

def crag():
    for x in range(-24, 25):
        for z in range(-24, 25):
            d = math.hypot(x, z) + 1.6 * math.sin(math.atan2(z, x) * 5) + 0.8 * math.sin(math.atan2(z, x) * 11 + 1)
            for y in range(-8, 6):
                a = 21.5 - max(0, y - 1) * 0.9
                if d <= a:
                    put(x, y, z, s("frost_granite") if frost(x, y, z) or d > a - 1 else s("giant_granite"))
    for k in range(7):                          # the stair up to the door, giant steps on a ramp
        z = 17 + k
        for x in range(-4, 5):
            for y in range(-8, 5 - k):
                put(x, y, z, s("giant_granite"))
            put(x, 5 - k, z, stairs("giant_granite", "north"))
            for y in range(6 - k, 13 - k):
                put(x, y, z, None)
        for cx in (-5, 5):
            for y in range(-8, 6 - k):
                put(cx, y, z, s("rime_bricks"))
            put(cx, 6 - k, z, wall("rime_brick"))
    for cx in (-6, 6):
        for y in range(-1, 3):
            put(cx, y, 24, s("giant_column"))
        put(cx, 3, 24, s("rune_glow"))


# ---------------------------------------------------------------- the keep

def keep():
    for y in range(6, DECK):
        rel = (y - 6) % 10
        r = rad(y)
        for x in range(-18, 19):
            for z in range(-18, 19):
                d = math.hypot(x, z)
                if r - 1 < d <= r:
                    if rel == 0:
                        put(x, y, z, s("rune_band") if int(math.degrees(math.atan2(z, x)) + 360) % 30 < 15 else s("giant_granite"))
                    elif rel == 9:
                        put(x, y, z, s("giant_granite"))
                    else:
                        put(x, y, z, s("frost_granite") if frost(x, y, z) else s("rime_bricks"))
                elif r - 3 < d <= r - 1:
                    put(x, y, z, s("rime_bricks"))
                elif r < d <= r + 1 and rel in (0, 9):      # a giant's cornice and a plinth course
                    put(x, y, z, slab("giant_granite", "bottom" if rel == 0 else "top") if rel == 9 else s("giant_granite"))
    # icicles under every cornice
    for f in FLOORS[1:] + [DECK]:
        for k in range(48):
            if k % 3 == 1:
                continue
            a = 2 * math.pi * k / 48
            x, z = round(math.cos(a) * (R + 0.6)), round(math.sin(a) * (R + 0.6))
            if math.hypot(x, z) <= R or get(x, f - 1, z) is None:
                continue
            ln = 1 + (k * 7) % 4
            for dy in range(1, ln + 1):
                if get(x, f - 1 - dy, z) is None:
                    put(x, f - 1 - dy, z, wall("pale_ice"))


def buttresses():
    """six leaning ribs of granite, fat at the foot, climbing to the third floor"""
    for k in range(6):
        a = math.radians(30 + 60 * k)
        if abs(math.degrees(a) - 90) < 20:
            continue                               # not over the door
        ca, sa = math.cos(a), math.sin(a)
        for y in range(0, 40):
            reach = R + 5.5 * (1 - y / 40) ** 1.3
            for x in range(-24, 25):
                for z in range(-24, 25):
                    along = x * ca + z * sa
                    side = abs(-x * sa + z * ca)
                    if R - 1 < along <= reach and side <= 1.6 - y / 60:
                        top = along > reach - 1
                        put(x, y, z, slab("giant_granite") if top and y % 3 == 2 else s("giant_granite") if side > 0.9 else s("rime_bricks"))


def windows():
    for f in FLOORS:
        for k in range(8):
            a = math.radians(22.5 + 45 * k)
            if f == FLOORS[0] and abs(math.degrees(a) - 90) < 30:
                continue
            for y in range(f + 2, f + 8):
                for dd in (R - 3, R - 2, R - 1, R):
                    put(round(math.cos(a) * dd), y, round(math.sin(a) * dd), None)
            put(round(math.cos(a) * R), f + 8, round(math.sin(a) * R), s("rune_glow"))


def door():
    for x in range(-3, 4):
        for y in range(6, 15):
            top = 14 - (1 if abs(x) == 3 else 0)
            for z in range(10, 18):
                if y <= top:
                    put(x, y, z, None)
    for y in range(6, 15):
        for x in (-4, 4):
            put(x, y, 15, s("giant_column"))
    for x in range(-5, 6):
        put(x, 15, 15, s("rune_band") if abs(x) < 4 else s("giant_granite"))
        put(x, 16, 15, s("giant_granite"))
    put(0, 14, 12, t.lantern(True))


# ---------------------------------------------------------------- the ice

def crystal(base, d, length, r0, glow=True):
    """a six-sided ice prism from base along d, tapering to a point over its last third; a glowing seam up one face"""
    dx, dy, dz = d
    n = math.sqrt(dx * dx + dy * dy + dz * dz)
    dx, dy, dz = dx / n, dy / n, dz / n
    # two axes across it
    ux, uy, uz = (-dz, 0, dx) if abs(dy) < 0.9 else (1, 0, 0)
    un = math.sqrt(ux * ux + uy * uy + uz * uz)
    ux, uy, uz = ux / un, uy / un, uz / un
    vx, vy, vz = dy * uz - dz * uy, dz * ux - dx * uz, dx * uy - dy * ux
    bx, by, bz = base
    span = int(length + r0) + 2
    for x in range(int(bx) - span, int(bx) + span + 1):
        for y in range(int(by) - span, int(by) + span + 1):
            for z in range(int(bz) - span, int(bz) + span + 1):
                px, py, pz = x - bx, y - by, z - bz
                a = px * dx + py * dy + pz * dz
                if not 0 <= a <= length:
                    continue
                u = px * ux + py * uy + pz * uz
                v = px * vx + py * vy + pz * vz
                hexd = max(abs(u), abs(u * 0.5 + v * 0.866), abs(u * 0.5 - v * 0.866)) / 0.866
                r = r0 if a < length * 0.62 else r0 * (length - a) / (length * 0.38)
                if hexd <= r:
                    seam = glow and abs(v) < 0.7 and u > r * 0.55
                    put(x, y, z, s("ice_glow") if seam or hexd < r - 1.6 else s("pale_ice"))


ICE = [   # (angle deg, height, out-lean, up-lean, length, radius)
    (200, 22, 1.0, 0.55, 20, 3.2), (215, 18, 1.0, 0.2, 13, 2.2), (190, 27, 1.0, 1.2, 15, 2.4),
    (330, 38, 1.0, 0.7, 22, 3.4), (345, 34, 1.0, 0.25, 14, 2.3), (315, 44, 1.0, 1.4, 13, 2.0),
    (60, 50, 1.0, 0.9, 17, 2.8), (40, 55, 1.0, 0.45, 12, 2.0), (130, 30, 1.0, 0.5, 11, 1.8),
    (250, 8, 1.0, 0.3, 12, 2.6), (20, 10, 1.0, 0.5, 10, 2.2),
    (275, 30, 1.0, 0.8, 24, 3.8), (285, 26, 1.0, 0.1, 12, 2.2), (262, 35, 1.0, 1.6, 14, 2.2),
    (150, 46, 1.0, 0.7, 18, 3.0), (165, 50, 1.0, 1.5, 12, 2.0), (110, 14, 1.0, 0.6, 9, 1.8),
]


def ice():
    for (ang, y, out, up, ln, r0) in ICE:
        a = math.radians(ang)
        base = (math.cos(a) * (R - 2.5), y, math.sin(a) * (R - 2.5))
        crystal(base, (math.cos(a) * out, up, math.sin(a) * out), ln, r0)
        # the wall cracked round where it burst: frost-split stone
        for x in range(round(base[0]) - 5, round(base[0]) + 6):
            for z in range(round(base[2]) - 5, round(base[2]) + 6):
                for yy in range(y - 5, y + 6):
                    d = math.hypot(x, z)
                    if R - 1 < d <= R and math.dist((x, yy, z), base) < r0 + 3.2 and "rime_bricks" in str(get(x, yy, z)):
                        put(x, yy, z, s("frost_granite"))


# ---------------------------------------------------------------- the roof: the ice crown and the Jarl's throne

def roof():
    RR = R + 2.5
    for x in range(-19, 20):
        for z in range(-19, 20):
            d = math.hypot(x, z)
            if d <= RR:
                put(x, DECK - 1, z, s("giant_granite") if d > RR - 1.2 else s("rune_band") if abs(d - 7) < 0.6 else s("frost_flags"))
            if R < d <= RR - 0.5:                          # corbels under the overhang
                for y in range(DECK - 4, DECK - 1):
                    if int(math.degrees(math.atan2(z, x)) + 360) % 20 < 6 and d <= R + (y - DECK + 5) * 0.9:
                        put(x, y, z, s("giant_granite"))
            if RR - 1.2 < d <= RR:
                put(x, DECK, z, wall("giant_granite") if (x + z) % 2 else s("giant_granite"))
    # the crown: ice spikes round the rim, leaning out, every other one tall
    for k in range(12):
        a = math.radians(15 + 30 * k)
        tall = k % 2 == 0
        base = (math.cos(a) * (RR - 1.5), DECK - 1, math.sin(a) * (RR - 1.5))
        crystal(base, (math.cos(a) * 0.35, 1, math.sin(a) * 0.35), 22 if tall else 12, 2.2 if tall else 1.5, glow=tall)
    # the Jarl's throne on the north side: an ice seat for a giant, its back a burst of crystals
    for x in range(-5, 6):
        for z in range(-14, -8):
            for y in range(DECK, DECK + 4):
                if y == DECK + 3 and z > -12 and abs(x) < 4:
                    continue                                 # the seat
                if y < DECK + 3 or abs(x) >= 4 or z <= -12:
                    put(x, y, z, s("giant_granite") if y == DECK else s("pale_ice"))
    for x in range(-4, 5):
        for y in range(DECK + 3, DECK + 13):
            put(x, y, -13, s("pale_ice") if abs(x) > 1 else s("ice_glow"))
    for (dx, up, ln) in ((-1, 1, 14), (1, 1, 14), (0, 1, 18), (-1.2, 0.6, 10), (1.2, 0.6, 10)):
        crystal((dx * 2.5, DECK + 10, -13), (dx * 0.4, up, -0.25), ln, 1.6)
    for sx in (-1, 1):
        for z in range(-12, -8):
            put(sx * 5, DECK + 4, z, s("white_fur"))
    for x in range(-3, 4):                                   # a bearskin thrown over the seat
        for z in range(-11, -8):
            put(x, DECK + 3, z, s("white_fur") if (x + z) % 3 else slab("pale_ice"))


# ---------------------------------------------------------------- inside: the rooms

def mead_hall(t, f):
    for z in range(-1, 9):                     # a giant's long table and benches
        for x in (-1, 0, 1):
            put(x, f, z, s("tarred_pine") if z in (-1, 8) else slab("tarred_pine", "top"))
            put(x, f + 1, z, slab("tarred_pine") if x == 0 and z % 3 == 0 else None)
        for x in (-3, 3):
            put(x, f, z, slab("tarred_pine"))
    for sx in (-1, 1):                         # the hearths
        for z in range(2, 6):
            put(sx * 8, f, z, s("rune_glow") if z in (3, 4) else s("giant_granite"))
    t.chest(-6, f, 8)


def forge(t, f):
    for x in range(-2, 3):                     # the ice anvil on a granite block
        for z in range(4, 7):
            put(x, f, z, s("giant_granite"))
            put(x, f + 1, z, s("pale_ice") if abs(x) < 2 else None)
    put(0, f + 2, 5, slab("pale_ice"))
    for x in range(5, 9):                      # a forge of rune fire
        for z in range(3, 8):
            edge = x in (5, 8) or z in (3, 7)
            put(x, f, z, s("rime_bricks") if edge else s("rune_glow"))
    t.chest(-7, f, 5)


def kennel(t, f):
    for x in range(-8, 9, 4):                 # pens of pine rails
        for z in range(5, 10):
            put(x, f, z, wall("rime_brick"))
        put(x, f + 1, 5, slab("tarred_pine"))
    for x in range(-8, 9):
        if x % 4:
            put(x, f, 5, slab("tarred_pine"))
            for z in range(6, 10):
                if (x + z) % 3 == 0:
                    put(x, f, z, slab("tarred_pine"))
    t.chest(7, f, -1)


def rune_room(t, f):
    for k in range(8):                         # standing rune stones in a ring
        a = math.radians(45 * k + 22.5)
        x, z = round(math.cos(a) * 6), round(math.sin(a) * 6) + 2
        for y in range(f, f + 4):
            put(x, y, z, s("rune_band") if y == f + 2 else s("giant_granite"))
        put(x, f + 4, z, s("rune_glow"))
    put(0, f - 1, 2, s("ice_glow"))
    t.chest(0, f, 2)


def trophies(t, f):
    for x in (-7, 7):                          # mammoth tusks in pairs on the walls
        for z in (0, 6):
            for y in range(f, f + 6):
                put(x, y, z + (1 if y > f + 3 else 0) * (1 if x > 0 else -1) * 0, s("white_fur") if y == f else s("pale_ice"))
    t.chest(0, f, 8)


def approach(t, f):
    for x in (-5, 5):
        for z in (0, 4, 8):
            for y in range(f, f + 9):
                put(x, y, z, s("giant_column"))
    t.chest(0, f, 9)


ROOMS = [mead_hall, forge, kennel, rune_room, trophies, approach]
CREWS = [["rime_thrall", "rime_thrall", "huskarl"], ["frost_troll", "rime_thrall"], ["rime_thrall", "rime_thrall", "rime_thrall", "rune_seer"],
         ["rune_seer", "rune_seer", "huskarl"], ["frost_troll", "huskarl"], ["huskarl", "frost_troll", "rune_seer"]]
FOREMEN = ["huskarl", "frost_troll", "huskarl", "rune_seer", "frost_troll", "winter_wolf"]


def floors():
    for f in FLOORS:
        for x in range(-13, 14):
            for z in range(-13, 14):
                if math.hypot(x, z) <= INNER + 0.5:
                    put(x, f - 1, z, s("frost_flags"))


def build():
    crag()
    floors()
    keep()
    buttresses()
    windows()
    door()
    roof()
    t.interior(ROOMS, CREWS, FOREMEN, boss=[0, DECK, -4, "jarl_hrimgar"], reward=[0, DECK, 6], ring=lambda f: INNER - 3)
    ice()
    for x in range(-3, 4):                       # nothing may close the door
        for y in range(6, 14):
            for z in range(10, 17):
                if y <= 14 - (abs(x) == 3):
                    put(x, y, z, None)
    t.ground(52, "snow_block")


def inside(x, z, f):
    return math.hypot(x, z) <= INNER - 0.5


def hollow_inside(x, y, z):
    d = math.hypot(x, z)
    if 0 <= y < 30:
        return d <= 26
    if y < DECK:
        return d <= INNER
    return d <= 22


build()
if "cut" in sys.argv:
    for q in [q for q in t.b.B if q[0] > 0 and q[2] > 0 and q[1] >= 0]:
        del t.b.B[q]

SHOTS = {
    "front": ((0, 40, 130), (0, 44, 0), 24),
    "three": ((-90, 62, 92), (0, 46, 0), 26),
    "back": ((90, 70, -80), (0, 50, 0), 26),
    "low": ((14, 3, 46), (0, 34, 0), 18),
    "deck": ((-30, 96, 40), (0, 72, 0), 22),
    "cut": ((80, 60, 90), (0, 36, 0), 28),
}

if __name__ == "__main__":
    want = [a for a in sys.argv[1:] if a in SHOTS]
    print("blocks", len(t.b.B))
    if "walk" in sys.argv:
        t.walk((0, 0, 26))
    if "export" in sys.argv:
        t.floor_lights(inside, ("frost_flags",), roof=lambda x, z: math.hypot(x, z) <= R - 1)
        t.hang_lanterns(lambda f: INNER - 3)
        t.export(hollow_inside, DECK + 34)
    elif "cut" in sys.argv:
        K.preview(t.b, "tower_rimeholt_cut", {"cut": SHOTS["cut"]}, sun=(40, -135))
    elif "walk" not in sys.argv:
        K.preview(t.b, "tower_rimeholt", {k: v for k, v in SHOTS.items() if (not want or k in want) and k != "cut"}, sun=(40, -135))
