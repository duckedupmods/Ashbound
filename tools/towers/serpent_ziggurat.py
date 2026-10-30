"""The Coiled Spire (docs/TOWERS.md: the serpent cult's tower, jungle and swamp) in blocks: a mossy octagonal temple
tower banded with gold friezes, and round it a colossal stone serpent. Its tail lies by the door; its body coils
twice round the shaft as it climbs; its neck rears off the roof and its hooded head hangs over the boss's arena,
jaws open, jade eyes burning. The jungle grows out of its coils. Inside, six floors round the stairs.

    python tools/towers/serpent_ziggurat.py [shots...] [cut] [walk] [export]
    E:/Steam/steamapps/common/Blender/blender.exe -b -P E:/Ashbound/tools/blender/preview_struct.py -- tower_ziggurat [shots...]
"""
import math
import sys

import towerkit as TK
from towerkit import K, s, slab, stairs, wall, side_xy, oct_d

K.GLOW.update({"jade_fire": 1.4, "jade_block": 0.5})

FLOORS = [6, 16, 26, 36, 46, 56]
DECK = 66
AP = 13                     # the shaft's apothem
INNER = AP - 3              # the rooms reach oct_d INNER
COIL_R = 15.6               # the serpent's body winds round at this radius
BODY = 3.3                  # and is this thick (its radius)

t = TK.Tower("serpent_ziggurat", "ziggurat", "serpent_ziggurat", brick="temple_brick", fill="temple_bricks", px="coil",
             floors=FLOORS, deck=DECK, glow="jade_fire", goods=[("minecraft:emerald", 4, 1, 4), ("minecraft:cocoa_beans", 3, 2, 6)])
t.biomes = ["minecraft:jungle", "minecraft:sparse_jungle", "minecraft:bamboo_jungle", "minecraft:swamp", "minecraft:mangrove_swamp"]
put, get = t.put, t.get


def moss(x, y, z):
    """broad patches where the jungle has taken the stone, thicker low down; never speckle"""
    v = math.sin(x * 0.31 + y * 0.17) + math.sin(z * 0.27 - y * 0.23) + math.sin((x - z) * 0.19 + y * 0.11)
    return v > 1.7 - (0.6 if y < 16 else 0)


def stone(x, y, z):
    return s("overgrown_limestone") if moss(x, y, z) else s("temple_limestone")


def corner(x, z):
    ang = math.atan2(z, x)
    k = round((ang - math.radians(22.5)) / math.radians(45))
    c = math.radians(22.5) + k * math.radians(45)
    return abs(math.hypot(x, z) * math.sin(ang - c)) < 1.3


def inward(x, z):
    return ("west" if x > 0 else "east") if abs(x) >= abs(z) else ("north" if z > 0 else "south")


def diag(x, z):
    return abs(abs(x) - abs(z)) <= 1 and abs(x) > 6


# ---------------------------------------------------------------- the footing

def footing():
    for x in range(-22, 23):
        for z in range(-22, 23):
            d = oct_d(x, z)
            for y in range(-6, 6):
                a = 20.5 if y < 2 else 18.5 if y < 4 else 16.5
                if d <= a:
                    put(x, y, z, stone(x, y, z) if d > a - 1 else s("temple_bricks"))
            for y, a in ((2, 20.5), (4, 18.5)):
                if a - 1 < d <= a:
                    put(x, y, z, stairs("temple_limestone", inward(x, z)) if not diag(x, z) else slab("temple_limestone"))
    for k in range(6):                          # the stair up to the door, its cheeks solid to the ground
        z = 17 + k
        for x in range(-3, 4):
            for y in range(-6, 5 - k):
                put(x, y, z, s("temple_bricks"))
            put(x, 5 - k, z, stairs("temple_limestone", "north"))
            for y in range(6 - k, 11 - k):
                put(x, y, z, None)
        for cx in (-4, 4):
            for y in range(-6, 6 - k):
                put(cx, y, z, s("temple_limestone"))
            put(cx, 6 - k, z, wall("temple_limestone"))
    for cx in (-5, 5):                          # jade braziers at the stair's foot
        for y in range(0, 2):
            put(cx, y, 23, s("temple_column"))
        put(cx, 2, 23, s("jade_fire"))


# ---------------------------------------------------------------- the shaft

def shaft():
    for y in range(6, DECK):
        rel = (y - 6) % 10
        band = rel == 0
        for x in range(-AP - 1, AP + 2):
            for z in range(-AP - 1, AP + 2):
                d = oct_d(x, z)
                if AP - 1 < d <= AP:               # the skin: pilasters at the corners, panels set back between
                    if band:
                        put(x, y, z, s("gold_frieze"))
                    elif rel == 1:
                        put(x, y, z, s("serpent_carving") if (x + z) % 3 == 0 else s("temple_limestone"))
                    elif corner(x, z):
                        put(x, y, z, s("temple_column"))
                    elif rel == 9:
                        put(x, y, z, s("temple_limestone"))
                elif AP - 2 < d <= AP - 1:
                    put(x, y, z, stone(x, y, z) if not corner(x, z) else s("temple_column"))
                elif AP - 3 < d <= AP - 2:
                    put(x, y, z, s("temple_bricks"))
                elif AP < d <= AP + 1 and rel in (1, 9):  # a cornice over each band and a lip under it
                    put(x, y, z, slab("temple_limestone", "bottom" if rel == 1 else "top"))
    # windows: two tall slits a side on the four cardinal faces, a jade lamp over each
    for f in FLOORS:
        for side in ("north", "south", "east", "west"):
            for off in (-4, 4):
                if side == "south" and f == FLOORS[0]:
                    continue
                for y in range(f + 3, f + 8):
                    for dep in (AP - 2, AP - 1, AP):
                        x, z = side_xy(side, off, dep)
                        put(x, y, z, None)
                x, z = side_xy(side, off, AP)
                put(x, f + 8, z, s("jade_fire"))


def door():
    for x in range(-2, 3):
        for y in range(6, 13):
            top = 12 - (1 if abs(x) == 2 else 0)
            for z in range(AP - 3, AP + 3):
                if y <= top:
                    put(x, y, z, None)
    for x in range(-3, 4):
        put(x, 13, AP + 1, s("gold_frieze"))
        put(x, 14, AP + 1, slab("temple_limestone"))
    for y in range(6, 13):
        for x in (-3, 3):
            put(x, y, AP + 1, s("temple_column"))
    put(0, 15, AP + 1, s("serpent_carving"))
    put(0, 12, AP - 2, t.lantern(True))


# ---------------------------------------------------------------- the serpent

def curve():
    """the serpent's spine: (point, radius, outward unit) samples, tail to head-root"""
    pts = []
    a0, turns = math.radians(122), 2.25
    y0, y1 = 7.0, DECK + 1.5
    n = 900
    for i in range(n + 1):
        u = i / n
        a = a0 + u * turns * 2 * math.pi
        y = y0 + (y1 - y0) * u
        rad = BODY * min(1.0, 0.25 + u * 6) if u < 0.12 else BODY
        pts.append(((math.cos(a) * COIL_R, y, math.sin(a) * COIL_R), rad, (math.cos(a), 0, math.sin(a))))
    # the neck: off the roof edge, rising and leaning in over the arena
    a_end = a0 + turns * 2 * math.pi
    m = 260
    for i in range(1, m + 1):
        u = i / m
        r = COIL_R - 5.5 * u ** 2
        a = a_end + 0.35 * u
        y = DECK + 1.5 + 20 * math.sin(u * math.pi / 2) ** 0.8
        rad = BODY - 0.2 * u
        pts.append(((math.cos(a) * r, y, math.sin(a) * r), rad, (math.cos(a), 0, math.sin(a))))
    return pts


def serpent():
    """sweep a ball along the spine; every block keeps the nearest sample, so it knows if it's belly, flank or back"""
    best = {}
    pts = curve()
    for i, (c, rad, out) in enumerate(pts):
        cx, cy, cz = c
        R = int(rad) + 2
        for x in range(int(cx) - R, int(cx) + R + 1):
            for y in range(int(cy) - R, int(cy) + R + 1):
                for z in range(int(cz) - R, int(cz) + R + 1):
                    d = math.dist((x, y, z), c)
                    if d <= rad and (best.get((x, y, z)) is None or d < best[(x, y, z)][0]):
                        best[(x, y, z)] = (d, i, rad, c, out)
    for (x, y, z), (d, i, rad, c, out) in best.items():
        vx, vy, vz = x - c[0], y - c[1], z - c[2]
        o = (vx * out[0] + vz * out[2]) / max(0.5, rad)
        up = vy / max(0.5, rad)
        if d < rad - 1.6:
            put(x, y, z, s("temple_bricks"))                       # the core, unseen
            continue
        band = (i // 7) % 4
        if o < -0.55 and i < 900:
            st = s("jade_tiles")                                    # the belly against the tower, pale scales
        elif up > 0.55:
            st = s("gold_frieze") if band == 0 or (band == 2 and abs(vx * out[2] - vz * out[0]) < 1) else s("overgrown_limestone")
        elif abs(up) < 0.5 and band in (0, 2):
            st = s("serpent_carving")                               # the flank's scale rows
        else:
            st = s("overgrown_limestone")
        put(x, y, z, st)
    return pts


def head(pts):
    """the hooded head on the neck's end, bent forward and down over the arena, its jaw dropped"""
    (nx, ny, nz), rad, out = pts[-1]
    fx, fz = -nx, -nz
    ln = math.hypot(fx, fz)
    fx, fz = fx / ln, fz / ln
    tilt = math.radians(28)
    F = (fx * math.cos(tilt), -math.sin(tilt), fz * math.cos(tilt))
    Rt = (-fz, 0, fx)
    U = (F[1] * Rt[2] - F[2] * Rt[1], F[2] * Rt[0] - F[0] * Rt[2], F[0] * Rt[1] - F[1] * Rt[0])
    if U[1] < 0:
        U = tuple(-v for v in U)
    O = (nx, ny, nz)

    def local(x, y, z):
        v = (x - O[0], y - O[1], z - O[2])
        return (sum(v[k] * F[k] for k in range(3)), sum(v[k] * Rt[k] for k in range(3)), sum(v[k] * U[k] for k in range(3)))

    # the hood: a broad upright shield spread from the neck below the head, facing the arena, two jade spectacles
    Fh = (fx, 0, fz)

    def hlocal(x, y, z):
        v = (x - O[0], y - O[1], z - O[2])
        return v[0] * Fh[0] + v[2] * Fh[2], v[0] * Rt[0] + v[2] * Rt[2], v[1]

    for x in range(int(nx) - 16, int(nx) + 17):
        for y in range(int(ny) - 16, int(ny) + 14):
            for z in range(int(nz) - 16, int(nz) + 17):
                ah, bh, ch = hlocal(x, y, z)
                # a teardrop: out of the neck at the bottom, widest a third of the way up, closing under the head
                if -14 <= ch <= 1:
                    u = (ch + 14) / 15
                    hw = 3.0 + 7.5 * math.sin(min(1.0, u / 0.55) * math.pi / 2) if u < 0.55 else 10.5 - 6.5 * ((u - 0.55) / 0.45) ** 1.5
                    bow = 0.5 * (bh / max(1.0, hw)) ** 2 * 2.4            # its edges curl forward a little
                    if abs(bh) <= hw and -2.2 + bow < ah < 0.6 + bow:
                        front = ah > -0.6 + bow
                        rim = abs(bh) > hw - 1.1
                        spec = any(1.0 < math.hypot(bh - sb * 4.4, ch + 6.5) < 2.2 for sb in (-1, 1))
                        if front and spec:
                            put(x, y, z, s("jade_fire"))
                        elif front and abs(bh) <= 1.6:
                            put(x, y, z, s("jade_tiles"))                 # the throat's pale scales
                        elif front and not rim and int(ch) % 4 == 0 and abs(bh) > 2.6:
                            put(x, y, z, s("gold_frieze"))                # gold bars across the hood
                        else:
                            put(x, y, z, s("temple_limestone") if rim else stone(x, y, z))
                        continue
                a, b, c = local(x, y, z)
                w = 4.4 - 1.8 * max(0.0, a) / 12
                skull = -2 <= a <= 12 and abs(b) <= w and -0.3 <= c <= 3.6 - 0.16 * a
                jaw = 0 <= a <= 11 and abs(b) <= w - 0.4 and (-3.6 - 0.25 * a) <= c <= (-2.0 - 0.15 * a)
                if skull:
                    put(x, y, z, s("gold_frieze") if c > 2.3 - 0.14 * a and abs(b) < 1 else s("temple_limestone"))
                elif jaw:
                    put(x, y, z, s("temple_bricks") if c > -2.6 - 0.15 * a else s("temple_limestone"))
    for sb in (-1, 1):
        for da in (5.5, 6.5):                       # eyes
            p = [O[k] + F[k] * da + Rt[k] * sb * 3.4 + U[k] * 1.8 for k in range(3)]
            put(round(p[0]), round(p[1]), round(p[2]), s("jade_fire"))
        tip = [O[k] + F[k] * 10.4 + Rt[k] * sb * 1.6 - U[k] * 0.6 for k in range(3)]
        for dy in range(0, 3):                      # fangs
            put(round(tip[0]), round(tip[1]) - dy, round(tip[2]), wall("temple_limestone"))
    for da in range(2, 10):                         # the tongue, lying in the dropped jaw
        p = [O[k] + F[k] * da - U[k] * (1.6 + 0.15 * da) for k in range(3)]
        put(round(p[0]), round(p[1]), round(p[2]), s("jade_block"))
    th = [O[k] + F[k] * 4 - U[k] * 1.0 for k in range(3)]
    put(round(th[0]), round(th[1]), round(th[2]), s("jade_fire"))      # the throat glows


# ---------------------------------------------------------------- the roof and the jungle

def deck():
    R = AP + 3.5
    for x in range(-18, 19):
        for z in range(-18, 19):
            d = oct_d(x, z)
            if d <= R:
                put(x, DECK - 1, z, s("gold_frieze") if R - 1 < d else s("jade_tiles") if int(d) % 5 else s("temple_limestone"))
                if R - 1 < d:
                    put(x, DECK - 2, z, s("temple_limestone"))
                    put(x, DECK, z, wall("temple_limestone") if (x + z) % 3 else s("temple_column"))
            if AP < d <= R - 1:                      # corbels under the overhang
                for y in range(DECK - 4, DECK - 1):
                    if corner(x, z) and d <= AP + (y - DECK + 5):
                        put(x, y, z, s("temple_limestone"))
    for k in range(8):
        ang = math.radians(22.5 + 45 * k)
        x, z = round(math.cos(ang) * (R - 1.6)), round(math.sin(ang) * (R - 1.6))
        for y in (DECK, DECK + 1):
            put(x, y, z, s("temple_column"))
        put(x, DECK + 2, z, s("jade_fire"))


def tree(x0, y0, z0, h, crown=3.4):
    """a jungle tree: a straight trunk on buttress roots, its crown two flat spreading layers, leaves trailing off
    their rims"""
    for y in range(y0, y0 + h):
        put(x0, y, z0, s("root_wood", axis="y"))
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        for dy in range(2):
            if get(x0 + dx, y0 + dy, z0 + dz) is None:
                put(x0 + dx, y0 + dy, z0 + dz, s("root_wood", axis="y"))
    layers = ((y0 + h - 3, crown * 0.75, 1), (y0 + h, crown, 2)) if h > 5 else ((y0 + h, crown, 2),)
    for ly, R, thick in layers:
        for x in range(x0 - 7, x0 + 8):
            for z in range(z0 - 7, z0 + 8):
                d = math.hypot(x - x0, z - z0) + 0.6 * math.sin(x * 1.7 + z * 2.3)
                for y in range(ly, ly + thick):
                    if d <= R - (y - ly) * 1.2 and get(x, y, z) is None:
                        put(x, y, z, s("wildwood_leaves_sunlit" if y == ly + thick - 1 else "wildwood_leaves"))
                if R - 1.2 < d <= R and (x * 7 + z * 3) % 4 == 0:          # trailing leaves off the rim
                    for y in range(ly - 2, ly):
                        if get(x, y, z) is None:
                            put(x, y, z, s("wildwood_leaves_shade"))
        if ly > y0 + 1:
            for dx, dz in ((1, 1), (-1, -1), (1, -1)):                  # boughs out to it
                put(x0 + dx, ly - 1, z0 + dz, s("root_wood", axis="x"))


def jungle(pts):
    """trees rooted on the coils where they ride out from the wall, and round the footing"""
    for i in range(80, 880, 140):
        (x, y, z), rad, out = pts[i]
        top = round(y + rad)
        bx, bz = round(x + out[0] * 0.8), round(z + out[2] * 0.8)
        if get(bx, top, bz) is None and get(bx, top - 1, bz) is not None:
            tree(bx, top, bz, 5 + i % 3, crown=3.6)
    for k, ang in enumerate((35, 150, 215, 320)):
        a = math.radians(ang)
        x, z = round(math.cos(a) * 18), round(math.sin(a) * 18)
        tree(x, 6 if oct_d(x, z) <= 16.5 else 4 if oct_d(x, z) <= 18.5 else 2, z, 9 + k % 3, crown=5.2)


# ---------------------------------------------------------------- inside: the rooms

def offerings(t, f):
    for sx in (-1, 1):                         # two pools of still water, jade braziers by them
        for x in range(3, 8):
            for z in range(1, 7):
                edge = x in (3, 7) or z in (1, 6)
                put(sx * x, f, z, slab("temple_limestone") if edge else "minecraft:water[level=0]")
        put(sx * 8, f, 0, s("temple_column"))
        put(sx * 8, f + 1, 0, s("jade_fire"))
    for x in range(-1, 2):
        put(x, f, -1, s("gold_frieze"))
    t.chest(0, f + 1, -1)


def serpent_pit(t, f):
    for x in range(-7, 8):
        for z in range(-4, 9):
            r = math.hypot(x, z - 2)
            if 4.6 < r <= 5.8 and not (abs(x) <= 1 or abs(z - 2) <= 1):
                put(x, f, z, s("temple_bricks"))
                put(x, f + 1, z, wall("temple_brick"))
            elif r <= 1.8 and (x + z) % 2 == 0:
                put(x, f - 1, z, s("jade_fire"))
    t.chest(-7, f, 6)


def barracks(t, f):
    for x in (-7, -4, 4, 7):                   # bunks: stone shelves with red blankets
        for z in range(2, 6):
            put(x, f, z, slab("temple_brick", "top"))
            put(x, f + 1, z, s("red_plaster") if z < 5 else slab("temple_limestone"))
    for x in (-2, 0, 2):                       # weapon racks: posts and a bar
        for y in range(f, f + 3):
            put(x, y, 8, s("root_wood", axis="y"))
        put(x, f + 3, 8, s("temple_limestone"))
    t.chest(6, f, 7)


def garden(t, f):
    for x in range(-10, 11):                  # the floor gone to moss
        for z in range(-10, 11):
            if moss(x, f, z * 2) and "jade_tiles" in str(get(x, f - 1, z)):
                put(x, f - 1, z, s("overgrown_limestone"))
    for cx, cz in ((-5, 4), (5, 4), (0, 8)):  # trees grown up through the floor, their crowns under the ceiling
        for y in range(f, f + 6):
            put(cx, y, cz, s("root_wood", axis="y"))
        for x in range(cx - 3, cx + 4):
            for z in range(cz - 3, cz + 4):
                for y in (f + 6, f + 7, f + 8):
                    if math.hypot(x - cx, z - cz) <= (3.0 if y < f + 8 else 2.0) and get(x, y, z) is None:
                        put(x, y, z, s("wildwood_leaves" if (x + z + y) % 3 else "wildwood_leaves_sunlit"))
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            put(cx + dx, f, cz + dz, s("root_wood", axis="x" if dx else "z"))
    t.chest(-7, f, -1)


def sanctum(t, f):
    for sx in (-1, 1):
        for x in range(2, 7):
            for z in range(1, 7):
                edge = x in (2, 6) or z in (1, 6)
                put(sx * x, f, z, s("jade_block") if edge else "minecraft:water[level=0]")
        put(sx * 4, f - 1, 3, s("jade_fire"))
    for x in range(-1, 2):
        for z in range(8, 10):
            put(x, f, z, s("gold_frieze"))
    put(0, f + 1, 9, s("jade_fire"))
    t.chest(0, f, 6)


def champion(t, f):
    for x in (-5, 5):
        for z in (-1, 3, 7):
            for y in range(f, f + 9):
                put(x, y, z, s("temple_column"))
            put(x, f + 8, z, s("gold_frieze"))
    t.chest(0, f, 8)


ROOMS = [offerings, serpent_pit, barracks, garden, sanctum, champion]
CREWS = [["scaleguard", "scaleguard", "coilspawn"], ["coilspawn", "coilspawn", "coilspawn", "coilspawn"],
         ["scaleguard", "jaguar_stalker", "scaleguard"], ["jaguar_stalker", "jaguar_stalker", "coilspawn"],
         ["venom_priest", "venom_priest", "scaleguard"], ["scaleguard", "jaguar_stalker", "venom_priest"]]
FOREMEN = ["scaleguard", "jaguar_stalker", "scaleguard", "jaguar_stalker", "venom_priest", "feathered_champion"]


def floors():
    for f in FLOORS:
        for x in range(-AP, AP + 1):
            for z in range(-AP, AP + 1):
                if oct_d(x, z) <= INNER:
                    put(x, f - 1, z, s("jade_tiles"))


def build():
    footing()
    floors()
    shaft()
    door()
    deck()
    t.interior(ROOMS, CREWS, FOREMEN, boss=[0, DECK, 2, "coiled_king"], reward=[0, DECK, -6], ring=lambda f: INNER - 3)
    pts = serpent()
    head(pts)
    jungle(pts)
    for x in range(-2, 3):                       # the coils may not close the door
        for y in range(6, 13):
            for z in range(AP - 3, AP + 5):
                if y <= 12 - (abs(x) == 2) and get(x, y, z) is not None:
                    put(x, y, z, None)
    t.ground(52)


def inside(x, z, f):
    return oct_d(x, z) <= INNER - 1


def hollow_inside(x, y, z):
    d = oct_d(x, z)
    if 0 <= y < 30:
        return d <= 24
    if y < DECK:
        return d <= INNER
    return math.hypot(x, z) <= 20


build()
if "cut" in sys.argv:
    for q in [q for q in t.b.B if q[0] > 0 and q[2] > 0 and q[1] >= 0]:
        del t.b.B[q]

SHOTS = {
    "front": ((0, 40, 130), (0, 44, 0), 24),
    "three": ((-90, 62, 92), (0, 46, 0), 26),
    "back": ((90, 70, -80), (0, 50, 0), 26),
    "low": ((14, 3, 44), (0, 34, 0), 18),
    "deck": ((-34, 92, 38), (0, 72, 0), 22),
    "cut": ((80, 60, 90), (0, 36, 0), 28),
    "face": ((50, 84, 30), (-8, 80, 0), 26),
}

if __name__ == "__main__":
    want = [a for a in sys.argv[1:] if a in SHOTS]
    print("blocks", len(t.b.B))
    if "walk" in sys.argv:
        t.walk((0, 6, AP + 4))
    if "export" in sys.argv:
        t.floor_lights(inside, ("jade_tiles",), roof=lambda x, z: oct_d(x, z) <= AP)
        t.hang_lanterns(lambda f: INNER - 3)
        t.export(hollow_inside, DECK + 30)
    elif "cut" in sys.argv:
        K.preview(t.b, "tower_ziggurat_cut", {"cut": SHOTS["cut"]}, sun=(55, -135))
    elif "walk" not in sys.argv:
        K.preview(t.b, "tower_ziggurat", {k: v for k, v in SHOTS.items() if (not want or k in want) and k != "cut"}, sun=(55, -135))
