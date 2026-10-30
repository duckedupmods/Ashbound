"""The Glass Minaret (docs/TOWERS.md, the desert) in blocks: a djinn's needle. A square base of sun-bleached
sandstone with a great tiled arch on every face and a slim turret on every corner; out of it a fluted shaft that
twists as it climbs, its turquoise ridges spiralling round it, girdled with brass balconies on stepped corbels;
on top a drum ringed with sun mirrors under a huge onion dome of brass and amber glass, a gold crescent on its spike.
The Djinn Sultan holds court under the dome.

    python tools/towers/glass_minaret.py [shots...] [cut] [walk] [export]
    E:/Steam/steamapps/common/Blender/blender.exe -b -P E:/Ashbound/tools/blender/preview_struct.py -- tower_minaret [shots...]
"""
import math
import sys

import towerkit as TK
from towerkit import K, s, slab, stairs, wall, side_xy

K.GLOW.update({"sun_glow": 1.6, "brass_screen": 0.7})

FLOORS = [6, 16, 26, 36, 46, 56, 66]
DECK = 76
BASE = 15                   # the square base's half-width (the first floor)
BASE_TOP = 16
SR = 11.0                   # the shaft's radius to the fluting's valleys
DOME_R = 14.5

t = TK.Tower("glass_minaret", "minaret", "glass_minaret", brick="minaret_brick", fill="minaret_bricks", px="minaret",
             floors=FLOORS, deck=DECK, glow="sun_glow", goods=[("minecraft:gold_ingot", 4, 2, 6), ("minecraft:lapis_lazuli", 3, 3, 9)])
t.biomes = ["minecraft:desert"]
put, get = t.put, t.get


def inner(f):
    return BASE - 3 if f < BASE_TOP else SR - 2.5


# ---------------------------------------------------------------- the plinth and the square base

def plinth():
    for x in range(-BASE - 4, BASE + 5):
        for z in range(-BASE - 4, BASE + 5):
            d = max(abs(x), abs(z))
            for y in range(-6, 6):
                a = BASE + 3 if y < 3 else BASE + 2
                if d <= a:
                    put(x, y, z, s("sun_sandstone") if d > a - 1 else s("minaret_bricks"))
            if d == BASE + 3:
                put(x, 3, z, slab("sun_sandstone"))
            if d == BASE + 2:
                put(x, 6, z, wall("minaret_brick") if (x + z) % 2 else slab("minaret_brick"))
    for k in range(7):
        z = BASE + 3 + 7 - k
        for x in range(-4, 5):
            for y in range(-6, k - 1):
                put(x, y, z, s("minaret_bricks"))
            put(x, k - 1, z, stairs("sun_sandstone", "north"))
            for y in range(k, k + 5):
                put(x, y, z, None)
        for cx in (-5, 5):
            for y in range(-6, k + 1):
                put(cx, y, z, s("sun_sandstone"))
            put(cx, k + 1, z, wall("minaret_brick"))
    for x in range(-4, 5):                    # the stair runs on over the plinth's step to its top
        for y in range(3, 6):
            put(x, y, BASE + 3, s("minaret_bricks"))
        put(x, 6, BASE + 2, None)
        put(x, 6, BASE + 3, None)


def base():
    h = BASE
    for y in range(6, BASE_TOP):
        rel = (y - 6) % 10
        for x in range(-h, h + 1):
            for z in range(-h, h + 1):
                d = max(abs(x), abs(z))
                if d == h:
                    put(x, y, z, s("turquoise_tiles") if rel == 0 else s("star_frieze") if rel == 9 else s("sun_sandstone"))
                elif h - 3 < d < h:
                    put(x, y, z, s("minaret_bricks"))
        if y in (BASE_TOP - 1,):
            for x in range(-h - 1, h + 2):
                for z in range(-h - 1, h + 2):
                    if max(abs(x), abs(z)) == h + 1:
                        put(x, y, z, slab("sun_sandstone", "top"))
    # crenellated parapet with merlons like little flames
    for x in range(-h, h + 1):
        for z in range(-h, h + 1):
            if max(abs(x), abs(z)) == h:
                put(x, BASE_TOP, z, s("sun_sandstone") if (x + z) % 3 else wall("minaret_brick"))
                if (x + z) % 3 == 0:
                    put(x, BASE_TOP + 1, z, slab("sun_sandstone"))
    for side in ("north", "south", "east", "west"):
        iwan(side)
    for sx in (-1, 1):
        for sz in (-1, 1):
            turret(sx * h, sz * h)


def iwan(side):
    """a great pointed arch set into the face: a recess lined in turquoise, a star frieze round it, a screen at its back"""
    h = BASE
    W, H = 4, 8                  # half-width, height to the arch's point
    for along in range(-W - 1, W + 2):
        for y in range(6, 6 + H + 2):
            u = abs(along)
            # a pointed arch: straight jambs to 2/3 the height, then two arcs meeting at the point
            spring = 6 + H * 0.6
            if y < spring:
                inside_arch = u < W
            else:
                cx = W - 5.0                          # the arc centres sit across the opening
                inside_arch = math.hypot(u - cx, y - spring) < 5.0 and u < W
            frame = not inside_arch and (u <= W + 1) and (y < spring + 5)
            for dep in range(h - 2, h + 1):
                x, z = side_xy(side, along, dep)
                if inside_arch:
                    put(x, y, z, None if dep > h - 2 else (s("brass_screen") if side != "south" else None))
                elif frame and dep == h:
                    put(x, y, z, s("star_frieze") if u == W + 1 or y >= spring + 4 else s("turquoise_tiles"))
    for along in range(-W, W + 1):                 # the recess's floor in tile
        x, z = side_xy(side, along, h - 1)
        put(x, 5, z, s("turquoise_tiles"))


def turret(cx, cz):
    for y in range(0, BASE_TOP + 6):
        for x in range(cx - 3, cx + 4):
            for z in range(cz - 3, cz + 4):
                d = math.hypot(x - cx, z - cz)
                if d <= 2.6:
                    band = y % 6 == 0
                    put(x, y, z, s("turquoise_tiles") if band else s("minaret_column") if d > 1.6 else s("minaret_bricks"))
    top = BASE_TOP + 6
    for k, r in enumerate((3.2, 3.0, 2.5, 1.8, 1.0)):           # a little onion
        for x in range(cx - 4, cx + 5):
            for z in range(cz - 4, cz + 5):
                if math.hypot(x - cx, z - cz) <= r:
                    put(x, top + k, z, s("dome_brass"))
    put(cx, top + 5, cz, s("gold_inlay"))
    put(cx, top + 6, cz, wall("minaret_brick"))
    put(cx, top - 1, cz, s("sun_glow"))


# ---------------------------------------------------------------- the twisting shaft

def twist(y):
    return math.radians(2.3 * (y - BASE_TOP))


def shaft():
    for y in range(BASE_TOP - 3, DECK - 4):
        rel = (y - 6) % 10
        tw = twist(y)
        for x in range(-15, 16):
            for z in range(-15, 16):
                rho = math.hypot(x, z)
                phi = math.atan2(z, x)
                flute = 0.5 + 0.5 * math.cos(16 * (phi - tw))       # sixteen flutes, turning as they climb
                rs = SR + 1.6 * flute
                if rs - 1.2 < rho <= rs:
                    if rel == 0:
                        put(x, y, z, s("gold_inlay"))
                    elif rel == 1:
                        put(x, y, z, s("star_frieze"))
                    else:
                        put(x, y, z, s("turquoise_tiles") if flute > 0.55 else s("sun_sandstone"))
                elif SR - 2.6 < rho <= rs - 1.2:
                    put(x, y, z, s("minaret_bricks"))
    # windows: a slim pointed slit on four sides each floor, a screen in it
    for f in FLOORS:
        if f < BASE_TOP:
            continue
        for k in range(4):
            a = math.radians(45 + 90 * k)
            for y in range(f + 2, f + 7):
                for dd in range(int(SR) - 3, int(SR) + 3):
                    x, z = round(math.cos(a) * dd), round(math.sin(a) * dd)
                    if get(x, y, z) is not None:
                        put(x, y, z, s("brass_screen") if dd >= SR - 0.5 and y < f + 6 else None if y < f + 6 else get(x, y, z))


def balcony(f):
    """a brass-railed balcony round the shaft at floor f, on three stepped courses of corbels, doors out to it"""
    for x in range(-17, 18):
        for z in range(-17, 18):
            rho = math.hypot(x, z)
            for k, (r0, r1) in enumerate(((SR + 0.5, SR + 2.0), (SR + 0.5, SR + 3.0), (SR + 0.5, SR + 4.0))):
                y = f - 4 + k
                if r0 < rho <= r1 and get(x, y, z) is None:
                    put(x, y, z, stairs("sun_sandstone", outward(x, z), "top") if rho > r1 - 1 else s("sun_sandstone"))
            if SR < rho <= SR + 4.6:
                put(x, f - 1, z, s("dome_brass") if rho > SR + 3.6 else s("bazaar_flags"))
            if SR + 3.6 < rho <= SR + 4.6:
                put(x, f, z, wall("minaret_brick"))
                if (x * 3 + z * 7) % 11 == 0:
                    put(x, f + 1, z, t.lantern())
    for k in range(4):                     # doors out to it
        a = math.radians(90 * k)
        for y in range(f, f + 4):
            for dd in range(int(SR) - 3, int(SR) + 2):
                put(round(math.cos(a) * dd), y, round(math.sin(a) * dd), None)


def outward(x, z):
    return ("east" if x > 0 else "west") if abs(x) >= abs(z) else ("south" if z > 0 else "north")


# ---------------------------------------------------------------- the drum and the dome

def dome():
    # corbels flaring the shaft out to the court's floor
    for y in range(DECK - 6, DECK):
        r_out = SR + 1.6 + (y - (DECK - 6)) * 0.6
        for x in range(-18, 19):
            for z in range(-18, 19):
                rho = math.hypot(x, z)
                if SR < rho <= r_out:
                    put(x, y, z, s("star_frieze") if y == DECK - 1 else stairs("sun_sandstone", outward(x, z), "top")
                        if rho > r_out - 1 else s("sun_sandstone"))
                elif SR - 2.6 < rho <= SR:
                    put(x, y, z, s("minaret_bricks"))
    CR = 15.0                     # the court's radius
    for x in range(-17, 18):
        for z in range(-17, 18):
            rho = math.hypot(x, z)
            if rho <= CR:
                put(x, DECK - 1, z, s("gold_inlay") if CR - 1 < rho else s("turquoise_tiles") if int(rho) % 4 == 0 else s("bazaar_flags"))
            if CR - 1 < rho <= CR:
                put(x, DECK, z, wall("minaret_brick"))
    # the arcade: eight pairs of columns, pointed arches between them, open to the sky
    AR = 12.5
    top = DECK + 11
    for k in range(8):
        a = math.radians(22.5 + 45 * k)
        for dx in (-0.12, 0.12):
            x, z = round(math.cos(a + dx) * AR), round(math.sin(a + dx) * AR)
            for y in range(DECK, top):
                put(x, y, z, s("minaret_column") if y < top - 1 else s("gold_inlay"))
    spring = DECK + 6
    for y in range(spring, top + 2):
        for x in range(-15, 16):
            for z in range(-15, 16):
                rho = math.hypot(x, z)
                if AR - 1 < rho <= AR + 0.4:
                    a = (math.degrees(math.atan2(z, x)) - 22.5) % 45       # 0 at a column pair, 22.5 mid-span
                    off = min(a, 45 - a) / 22.5                            # 0 at the column, 1 mid-span
                    if y >= top or y > spring + 4.6 * (1 - off ** 1.6):
                        put(x, y, z, s("turquoise_tiles") if y == top + 1 else s("star_frieze") if y == top else s("sun_sandstone"))
    # the onion: turquoise tile with gold ribs, swelling past the arcade then drawing in to a point
    y0 = top + 3
    for x in range(-15, 16):
        for z in range(-15, 16):
            if math.hypot(x, z) <= AR + 0.4:
                put(x, top + 2, z, s("sun_sandstone") if math.hypot(x, z) > AR - 1.2 else s("star_frieze"))
    for h in range(0, 24):
        if h < 7:
            r = AR + 1.8 * math.sin(h / 7 * math.pi / 2)
        else:
            r = max(0.6, (AR + 1.8) * (1 - ((h - 7) / 17) ** 1.4))
        y = y0 + h
        for x in range(-16, 17):
            for z in range(-16, 17):
                rho = math.hypot(x, z)
                if r - 1.4 < rho <= r:
                    a = (math.degrees(math.atan2(z, x)) + 360) % 30
                    put(x, y, z, s("gold_inlay") if a < 4 or h > 19 else s("turquoise_tiles"))
    tip = y0 + 24
    for y in range(tip - 2, tip + 6):
        put(0, y, 0, s("gold_inlay"))
    cy = tip + 9                               # the crescent: a gold ring with a bite out of it
    moon = {(u, v) for u in range(-5, 6) for v in range(-5, 6)
            if 2.6 < math.hypot(u, v) <= 4.2 and math.hypot(u - 1.8, v - 1.0) > 3.2}
    for (u, v) in moon:
        if sum((u + du, v + dv) in moon for du, dv in ((1, 0), (-1, 0), (0, 1), (0, -1))) >= 1:
            put(u, cy + v, 0, s("gold_inlay"))
    for y in range(tip + 6, cy - 3):
        put(0, y, 0, s("gold_inlay"))
    for k in range(8):                         # sun mirrors burning on the court's rim
        a = math.radians(45 * k)
        x, z = round(math.cos(a) * (CR - 0.5)), round(math.sin(a) * (CR - 0.5))
        put(x, DECK, z, s("minaret_column"))
        put(x, DECK + 1, z, s("sun_glow"))
    for x in range(-2, 3):                     # a glow under the dome's crown
        for z in range(-2, 3):
            if abs(x) + abs(z) <= 2:
                put(x, top + 2, z, s("sun_glow"))


# ---------------------------------------------------------------- inside: the rooms

def bazaar(t, f):
    for x in range(-8, 9, 4):                  # stalls: cedar counters under striped awnings
        if x == 0:
            continue
        for z in (4, 5):
            put(x, f, z, s("cedar_planks"))
        for y in (f, f + 1, f + 2):
            put(x, y, 6, wall("minaret_brick"))
        for z in (4, 5, 6):
            put(x, f + 3, z, s("turquoise_tiles") if z == 4 else slab("cedar_plank", "top") if z == 5 else s("cedar_planks"))
    for x in range(-2, 3):                     # a rug in the middle
        for z in range(0, 3):
            put(x, f - 1, z, s("star_frieze") if abs(x) == 2 or z in (0, 2) else s("turquoise_tiles"))
    t.chest(9, f, 9)


def mirror_hall(t, f):
    for x in (-9, 9):
        for z in range(-1, 10, 3):
            for y in range(f, f + 6):
                put(x, y, z, s("dome_brass") if y == f + 5 else s("brass_screen"))
    t.chest(0, f, 9)


def library(t, f):
    a = inner(f)
    for k in range(16):
        ang = math.radians(k * 22.5)
        x, z = round(math.cos(ang) * (a - 0.5)), round(math.sin(ang) * (a - 0.5))
        if z < -2:
            continue
        for y in range(f, f + 4):
            put(x, y, z, s("cedar_planks") if y % 2 == f % 2 else slab("cedar_plank", "top"))
    t.chest(0, f, 5)


def sand_clock(t, f):
    for y in range(f, f + 8):                  # a great hourglass of brass and screen
        r = abs(y - (f + 3.5)) * 0.6 + 0.6
        for x in range(-3, 4):
            for z in range(1, 8):
                d = math.hypot(x, z - 4)
                if r - 1 < d <= r:
                    put(x, y, z, s("brass_screen"))
        if y in (f, f + 7):
            for x in range(-3, 4):
                for z in range(1, 8):
                    if math.hypot(x, z - 4) <= 3:
                        put(x, y, z, s("dome_brass"))
    t.chest(-5, f, 5)


def glass_garden(t, f):
    for (x, z, h) in ((-5, 3, 4), (5, 3, 5), (-3, 7, 3), (3, 7, 4), (0, 5, 6)):
        for y in range(f, f + h):
            put(x, y, z, wall("minaret_brick"))
        put(x, f + h, z, s("brass_screen"))
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            put(x + dx, f + h, z + dz, slab("turquoise_tile", "top"))
    t.chest(0, f, 1)


def guard_hall(t, f):
    for x in (-5, 5):
        for z in (0, 5):
            for y in range(f, f + 9):
                put(x, y, z, s("minaret_column"))
    t.chest(0, f, 7)


def treasury(t, f):
    for (x, z) in ((-5, 4), (5, 4), (-3, 7), (3, 7)):     # heaps of gold under brass lamps
        put(x, f, z, s("gold_inlay"))
        put(x, f + 1, z, slab("turquoise_tile"))
    t.chest(0, f, 6)
    t.chest(-6, f, 0)


ROOMS = [bazaar, mirror_hall, library, sand_clock, glass_garden, treasury, guard_hall]
CREWS = [["mirror_guard", "dune_scorpion", "dune_scorpion"], ["mirror_guard", "sandwraith"],
         ["sandwraith", "dune_scorpion", "dune_scorpion"], ["glass_golem", "dune_scorpion"], ["glass_golem", "sandwraith"],
         ["glass_golem", "mirror_guard"], ["mirror_guard", "mirror_guard", "sandwraith"]]
FOREMEN = ["mirror_guard", "glass_golem", "mirror_guard", "glass_golem", "sandwraith", "glass_golem", "blade_dancer"]


def floors():
    for f in FLOORS:
        for x in range(-BASE, BASE + 1):
            for z in range(-BASE, BASE + 1):
                if (f < BASE_TOP and max(abs(x), abs(z)) <= BASE - 2) or (f >= BASE_TOP and math.hypot(x, z) <= SR - 1.5):
                    put(x, f - 1, z, s("bazaar_flags"))


def build():
    plinth()
    floors()
    base()
    shaft()
    for f in (36, 56):
        balcony(f)
    dome()
    door_clear()
    t.interior(ROOMS, CREWS, FOREMEN, boss=[0, DECK, 0, "djinn_sultan"], reward=[0, DECK, -8], ring=lambda f: inner(f) - 3)
    t.ground(52, "sand")


def door_clear():
    for x in range(-2, 3):
        for y in range(6, 13):
            for z in range(BASE - 3, BASE + 2):
                put(x, y, z, None)


def inside(x, z, f):
    return max(abs(x), abs(z)) <= BASE - 3 if f < BASE_TOP else math.hypot(x, z) <= SR - 3


def hollow_inside(x, y, z):
    if 0 <= y < 30:
        return max(abs(x), abs(z)) <= BASE + 9
    if y < DECK:
        return math.hypot(x, z) <= SR - 2
    return math.hypot(x, z) <= DOME_R + 3


build()
if "cut" in sys.argv:
    for q in [q for q in t.b.B if q[0] > 0 and q[2] > 0 and q[1] >= 0]:
        del t.b.B[q]

SHOTS = {
    "front": ((0, 55, 170), (0, 62, 0), 24),
    "three": ((-115, 85, 120), (0, 62, 0), 26),
    "back": ((115, 90, -110), (0, 64, 0), 26),
    "low": ((14, 3, 50), (0, 40, 0), 18),
    "dome": ((-40, 112, 48), (0, 90, 0), 22),
    "cut": ((90, 70, 100), (0, 46, 0), 28),
}

if __name__ == "__main__":
    want = [a for a in sys.argv[1:] if a in SHOTS]
    print("blocks", len(t.b.B))
    if "walk" in sys.argv:
        t.walk((0, 0, BASE + 12))
    if "export" in sys.argv:
        t.floor_lights(inside, ("bazaar_flags",), roof=lambda x, z: math.hypot(x, z) <= DOME_R - 2)
        t.hang_lanterns(lambda f: inner(f) - 3)
        t.export(hollow_inside, DECK + 50)
    elif "cut" in sys.argv:
        K.preview(t.b, "tower_minaret_cut", {"cut": SHOTS["cut"]}, sun=(55, -135))
    elif "walk" not in sys.argv:
        K.preview(t.b, "tower_minaret", {k: v for k, v in SHOTS.items() if (not want or k in want) and k != "cut"}, sun=(55, -135))
