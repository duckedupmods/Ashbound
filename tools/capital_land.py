"""Highmourn's land: the valley floor and its tiers, the lake, the river and the falls, and the mountains round it.

Heights are over the valley floor (Capital.FLOOR in the game); x east, z south, the city's centre at 0, 0, the gate
to the south. ground(x, z) gives each column its shape; the game cuts and fills the world's own land to it and, out
past the summits, eases it back into the world's own heights (the file's blend), so nothing ends in a sheer cut.

The look aimed for: a lake town against forested slopes (Hallstatt) with a cliff and falls at its head
(Lauterbrunnen), the mountains narrowing to a gorge down the valley where the two kings stand.
"""
import math

import city_highmourn as CH  # noqa: E402  (for its value noise)

noise = CH.noise

RX, RZ = 225, 180            # the wall's line: about this ellipse round the centre
GATE_Z = RZ
TERRACE, CITADEL = 20, 44
THROAT_Z = 322               # the gorge down the valley, where the kings stand
GRID = (-576, -576, 1152, 1216)   # x0, z0, width, depth of the shaped ground
MODE_NONE, MODE_CUT_FILL, MODE_FILL = 0, 1, 2
CLEAR = 4                    # mode flag: the city's own ground (no trees or caves, turfed)
BLEND0, BLEND1 = 250, 340    # out past the wall's line: eased from ours into the world's own heights
EDGE = 350                   # and the shaping's let go of here

# biome ids in the file (Capital.java maps them)
B_KEEP, B_PLAINS, B_MEADOW, B_FOREST, B_CHERRY, B_GROVE, B_SNOWY, B_STONY, B_FLOWERS, B_JAGGED = range(10)
WATER_Y = -1                 # the top water block of the lake and the river inside the walls
WATER_OUT = -3               # and outside them: the moat, the river on down the valley, the lower lake (a weir between)


def smooth(e0, e1, v):
    t = max(0.0, min(1.0, (v - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def snoise(x, z, scale, seed):
    """Value noise centred on 0, -1..1."""
    return noise(x, z, scale, seed) * 2 - 1


def smin(a, b, k):
    h = max(0.0, min(1.0, 0.5 + 0.5 * (b - a) / k))
    return b + (a - b) * h - k * h * (1 - h)


def edist(x, z):
    """Signed distance out from the wall's ellipse (radially): < 0 inside."""
    r = math.hypot(x, z)
    if r < 1e-6:
        return -min(RX, RZ)
    c, s = x / r, z / r
    return r - 1 / math.sqrt((c / RX) ** 2 + (s / RZ) ** 2)


def on_ellipse(x, z):
    """The point on the wall's ellipse straight out from the centre through x, z."""
    r = math.hypot(x, z)
    if r < 1e-6:
        return 0.0, RZ
    c, s = x / r, z / r
    R = 1 / math.sqrt((c / RX) ** 2 + (s / RZ) ** 2)
    return c * R, s * R


# ================================================================ the city's tiers

def z_terrace(x):
    return -62 - 0.0009 * x * x + 5 * snoise(x, 0, 37, 31)


def z_citadel(x):
    return -128 - 0.0012 * x * x + 5 * snoise(x, 0, 41, 32)


STAIR_HW = 9                 # the grand stairs' half-width (they climb straight, the banks either side curve)


BANK_STEPS = ((0.30, 7), (0.64, 7), (0.98, 6))   # the terrace bank's retaining walls: where (0..1 up it), how high


def bank_smooth(x, z):
    """Where the terrace bank keeps its plain slope: the grand stair, and the river's channel down it."""
    return abs(x) <= STAIR_HW + 1 or poly_d(x, z, RIVER_IN) <= river_hw(x, z, False) + 7


def tier_h(x, z, plain=False):
    """The city's ground: the lower city 0, the bank up to the terrace +20 stepped in three walled terraces (a plain
    slope at the stair and the river, or everywhere with plain), a grassy bank up to the citadel +44."""
    zt, zc = z_terrace(x), z_citadel(x)
    st = abs(x) <= STAIR_HW + 1
    lin = (lambda e0, e1, v: max(0.0, min(1.0, (v - e0) / (e1 - e0)))) if st else smooth
    up = (CITADEL - TERRACE) * lin(zc, zc - 24, z)
    if plain or bank_smooth(x, z):
        return TERRACE * lin(zt, zt - 20, z) + up
    u = (zt - z) / 20
    j = 0.035 * snoise(x, 0, 23, 33)
    return sum(h for (u0, h) in BANK_STEPS if u >= u0 + j * (u0 < 0.9)) + up


# ================================================================ water

def seg_dist(px, pz, a, b):
    ax, az = a
    bx, bz = b
    dx, dz = bx - ax, bz - az
    L2 = dx * dx + dz * dz
    t = max(0.0, min(1.0, ((px - ax) * dx + (pz - az) * dz) / L2))
    return math.hypot(px - ax - dx * t, pz - az - dz * t)


def poly_d(x, z, pts):
    return min(seg_dist(x, z, pts[i], pts[i + 1]) for i in range(len(pts) - 1))


# down from the falls' pool on the citadel, over the two banks, into the lake
RIVER_IN = [(70, -170), (71, -160), (72, -148), (74, -128), (77, -104), (74, -80), (76, -58), (80, -32)]
# out of the lake, through the water gate, down the valley between the kings, to the lower lake
RIVER_OUT = [(166, 70), (156, 112), (147, 150), (128, 192), (88, 238), (40, 262), (12, 290), (5, 322), (8, 360), (16, 392)]
LAKE = (100, 24, 106, 76)             # centre, radii (its shore wanders round this)
ISLAND = (128, 36, 17)
LOWER_LAKE = (14, 420, 58, 36)
POOL = (70, -171, 10, 7)             # at the falls' foot, cut into the cliff's toe


def lake_s(x, z, lake=LAKE, wob=0.13, seed=41):
    """< 1 inside the lake: the ellipse's radius fraction, its shore wobbled."""
    q = math.sqrt(((x - lake[0]) / lake[2]) ** 2 + ((z - lake[1]) / lake[3]) ** 2)
    return q * (1 + wob * snoise(x, z, 34, seed))


def QUAY(x, z):
    """The quay along the lake's south-west shore below the lower city (its shore-fraction there, else None)."""
    if 12 <= x <= 62 and z >= 55:
        s = lake_s(x, z)
        if 0.9 <= s < 1.075:
            return s
    return None


def island_s(x, z):
    return math.hypot(x - ISLAND[0], z - ISLAND[1]) / ISLAND[2] * (1 + 0.25 * snoise(x, z, 9, 43))


def in_pool(x, z):
    return ((x - POOL[0]) / POOL[2]) ** 2 + ((z - POOL[1]) / POOL[3]) ** 2 <= 1


def river_hw(x, z, out):
    if out:
        return 4 + 2 * smooth(150, 300, z)
    return 3


# ================================================================ the walls' line (the wall itself is capital_walls.py)

LEDGE = 34                   # open ground between the wall and the foot of the slopes, south of the middle


def ledge(z):
    return LEDGE * smooth(-70, 40, z)


MOAT_BED = -10               # the moat's bed (its water's top is WATER_OUT), stone revetments down to it


def moat_d(x, z):
    """The moat's band out from the wall's line, on the open south side (else None)."""
    if z < 60:
        return None
    d = edist(x, z)
    return d if 9 <= d <= 23 else None


# ================================================================ the mountains

def corridor_hw(z):
    """Half-width of the open valley south of the gate: wide meadows, then the gorge at the kings, then wide again."""
    return 62 + 58 * smooth(THROAT_Z, 210, z) + 74 * smooth(THROAT_Z, 440, z)


def floor_d(x, z):
    """Distance out from the open valley floor (the city with its ledge, and the valley down to the south)."""
    de = edist(x, z) - ledge(z)
    if z < 150:
        dc = max(abs(x) - corridor_hw(150), 150 - z)
    else:
        dc = abs(x - 16 * snoise(0, z, 97, 23)) - corridor_hw(z) * (1 + 0.12 * snoise(x, z, 61, 24))
    return smin(de, dc, 30)


def _profile(slopes):
    """Heights along d (0..700) from a slope table [(d, slope), ...], linearly between."""
    out, h = [], 0.0
    for d in range(701):
        for i in range(len(slopes) - 1):
            if slopes[i][0] <= d <= slopes[i + 1][0]:
                (d0, s0), (d1, s1) = slopes[i], slopes[i + 1]
                s = s0 + (s1 - s0) * (d - d0) / (d1 - d0)
                break
        else:
            s = slopes[-1][1]
        out.append(h)
        h += s
    return out


# forested slopes: gentle feet, steepening up to the crags, a rounded top, falling away behind
PROF_SLOPE = _profile([(0, 0.2), (50, 0.55), (140, 1.0), (190, 1.25), (226, 0.05), (240, -0.2), (330, -0.8), (700, -0.8)])
# the cliffs at the valley's head and in the gorge: a band of rock about 110 high, a forested shelf over it (the falls
# come off its edge), the mountain going on up behind
PROF_CLIFF = _profile([(0, 0.6), (5, 2.6), (40, 2.2), (55, 0.5), (70, 0.15), (110, 0.25), (140, 1.1), (200, 1.3), (235, 0.1),
                       (260, -0.3), (330, -0.8), (700, -0.8)])
CLIFF_TOP_D = 52             # where the cliff band ends on the forested shelf above it
FALLS_LIP_Z = round(-RZ * math.sqrt(1 - (70 / RX) ** 2)) - CLIFF_TOP_D    # the falls' lip, on the cliff's top edge
FALLS_LIP_H = 0              # (set below, from the profile)


def prof(table, d):
    if d <= 0:
        return 0.0
    i = int(d)
    if i >= 700:
        return table[700]
    return table[i] + (table[i + 1] - table[i]) * (d - i)


FALLS_LIP_H = round(CITADEL + prof(PROF_CLIFF, CLIFF_TOP_D)) - 6


def cliffness(x, z):
    """1 where the land rises as cliffs (the head of the valley, the gorge's sides), 0 on the forested slopes."""
    head = smooth(-30, -110, z) * smooth(175, 110, abs(x))
    gorge = smooth(48, 18, abs(z - THROAT_Z)) * smooth(140, 70, abs(x))
    return max(head, gorge)


def base_h(x, z):
    """The valley floor's height at the foot of the slope nearest x, z (the tier it rises from)."""
    if z > 0:
        return 0.0
    px, pz = on_ellipse(x, z)
    return tier_h(px * 0.97, pz * 0.97, True)


# saddles through the ring, east and west (the roads out will take them): direction from the centre, how wide
PASSES = [((1.0, -0.15), 46.0), ((-1.0, 0.1), 40.0)]


def mountain(x, z, d):
    """The land rising from the valley floor at distance d out from it."""
    cf = cliffness(x, z)
    dw = (d + 26 * snoise(x, z, 83, 21) * smooth(0, 40, d) - 18 * snoise(x, z, 151, 22) * smooth(20, 90, d)
          + 55 * snoise(x, z, 230, 25) * smooth(30, 120, d))
    h = prof(PROF_SLOPE, dw) * (1 - cf) + prof(PROF_CLIFF, dw) * cf
    out = smooth(0, 30, dw)
    # gullies down the slopes, wandering ledges, lumps, and the peaks over it all
    g = (1 - abs(snoise(x, z, 47, 7))) ** 6
    h -= 24 * g * smooth(25, 140, dw) * (1 - 0.6 * cf)
    step = 9.0
    frac = (h / step) % 1.0
    terr = math.floor(h / step) * step + step * smooth(0.55, 1.0, frac)
    h += (terr - h) * (0.45 + 0.35 * cf) * smooth(15, 50, dw) * noise(x, z, 61, 8)
    h += (8 * snoise(x, z, 29, 9) + 3 * snoise(x, z, 11, 10)) * out
    h += max(0.0, snoise(x, z, 117, 3) + 0.15) * 95 * smooth(110, 200, dw)
    for (ux, uz), wdt in PASSES:
        n = math.hypot(ux, uz)
        along = (x * ux + z * uz) / n
        if along > 0:
            perp = abs(x * uz - z * ux) / n
            h = 34 + (h - 34) * (1 - 0.8 * math.exp(-(perp / wdt) ** 2)) if h > 34 else h
    return base_h(x, z) + h * out


# ================================================================ the falls

# The stream comes off the shelf above the cliff and down its face in a notch it has worn into the rock: a run of
# short ledges, each a little pool, the water dropping from one to the next, into the plunge pool at the cliff's toe.
FALLS_Z0 = FALLS_LIP_Z - 70          # where the stream's bed starts, up on the shelf
FALLS_Z1 = POOL[1] - POOL[3] + 2     # and where the last drop lands, in the pool
_FALLS = {}


def falls_path():
    """z -> (centre x, half-width, the water's level there, the bed under it); worked out once."""
    if _FALLS:
        return _FALLS
    zs = list(range(FALLS_Z0, FALLS_Z1 + 1))
    px = {z: 70 + 3.5 * snoise(0, z, 31, 77) + 1.5 * snoise(0, z, 11, 78) for z in zs}
    hc = {}
    for z in zs:
        d = floor_d(px[z], z)
        hc[z] = recess(px[z], z, mountain(px[z], z, d)) if d > 0 else CITADEL
    # cut into ledges: long gentle steps up on the shelf, short ones (and big drops) down the cliff
    lv = None
    i, k = 0, 0
    while i < len(zs):
        steep = hc[zs[i]] - hc[zs[min(i + 4, len(zs) - 1)]] > 6
        n = (3 + int(noise(k, 0, 1.0, 79) * 3)) if steep else (3 + int(noise(k, 0, 1.0, 80) * 3))
        run = zs[i:i + n]
        level = math.floor(min(hc[z] for z in run)) - (3 if steep else 2)
        if lv is not None:
            level = min(level, lv - 1)
        level = max(level, CITADEL - 1)
        for z in run:
            w = (2.2 + 1.3 * noise(0, z, 13, 81)) * (1.0 if not steep else 1.6 + 0.6 * noise(k, 1, 1.0, 83))
            _FALLS[z] = (px[z], w, level, level - 1)
        lv = level
        i += n
        k += 1
    return _FALLS


def recess(x, z, h):
    """The cliff pushed back in a bowl round the falls (the water's worn it away), fluted into rough ribs."""
    dx = x + 0.5 - 70
    if abs(dx) > 40 or not FALLS_Z0 <= z <= FALLS_Z1 + 6:
        return h
    band = smooth(CITADEL + 4, CITADEL + 30, h) * smooth(CITADEL + 125, CITADEL + 95, h)
    g = math.exp(-(dx / 15.0) ** 2)
    rib = 5 * snoise(x, h * 0.15, 6, 88) + 3 * snoise(x, h * 0.4, 3, 89)
    return max(CITADEL + 1.0, h - band * (24 * g + rib * min(1.0, 2.5 * g)))


def falls_cut(x, z, h):
    """The ground's height round the falls: the bowl, and the notch the water runs in (None away from it)."""
    if not FALLS_Z0 <= z <= FALLS_Z1 + 6 or abs(x - 70) > 41:
        return None
    hr = recess(x, z, h)
    if z > FALLS_Z1:
        return round(hr)
    f = falls_path()[z]
    dx = abs(x + 0.5 - f[0])
    if dx <= f[1]:
        return f[3]
    # the notch's sides: rough rock rising from the water's edge to the cliff, steep at first
    wall = f[2] + 1 + (dx - f[1]) * (2.6 + 1.2 * noise(x, z, 4, 82))
    return round(min(hr, wall))


# ================================================================ the ground, column by column

PLAZA = (-185, THROAT_Z - 50, 210, THROAT_Z + 75)   # the open, level ground round the angel and the devil
PLAZA_FADE = 34


def in_plaza(x, z):
    return PLAZA[0] <= x <= PLAZA[2] and PLAZA[1] <= z <= PLAZA[3]


def plaza(x, z, h):
    """Lower the land round the statues to the valley floor so nothing hides them, easing back up over PLAZA_FADE."""
    dx = max(PLAZA[0] - x, 0, x - PLAZA[2])
    dz = max(PLAZA[1] - z, 0, z - PLAZA[3])
    d = math.hypot(dx, dz)
    if d >= PLAZA_FADE or h <= 0:
        return h
    return min(h, h * smooth(0, PLAZA_FADE, d) ** 1.5)


def ground(x, z):
    """(height, mode, weight 0..1, blend toward the world's own height 0..1, biome id)."""
    e = edist(x, z)
    if e >= EDGE:
        return 0, MODE_NONE, 0.0, 1.0, B_KEEP
    w = 1.0 if e < EDGE - 14 else (EDGE - e) / 14.0
    b = smooth(BLEND0, BLEND1, e)

    if in_pool(x, z):
        return CITADEL - 6, MODE_CUT_FILL | CLEAR, 1.0, 0.0, B_PLAINS
    inside = e < 2
    if inside:
        h = tier_h(x, z)
        s = lake_s(x, z)
        if s < 1:
            if island_s(x, z) < 1:
                k = 1 - island_s(x, z)
                return round(-0.5 + 9 * k ** 1.6 + 2.5 * snoise(x, z, 7, 45) * k), MODE_CUT_FILL | CLEAR, 1.0, 0.0, B_PLAINS
            inward = (1 - s) * min(LAKE[2], LAKE[3])
            deep = -4 if QUAY(x, z) is not None else 99
            return min(deep, round(WATER_Y - min(11.0, 1.0 + inward * 0.2))), MODE_CUT_FILL | CLEAR, 1.0, 0.0, B_PLAINS
        if poly_d(x, z, RIVER_IN) <= river_hw(x, z, False) + 1 or poly_d(x, z, RIVER_OUT) <= river_hw(x, z, True) + 1:
            return round(h) - 4, MODE_CUT_FILL | CLEAR, 1.0, 0.0, B_PLAINS
        return round(h), MODE_CUT_FILL | CLEAR, 1.0, 0.0, B_PLAINS

    # the open ground outside: the moat, the river and the lower lake, the valley floor and the slopes
    md = moat_d(x, z)
    if md is not None and floor_d(x, z) < 0:
        return MOAT_BED, MODE_CUT_FILL | CLEAR, 1.0, 0.0, B_PLAINS
    if abs(x) <= 18 and GATE_Z <= z <= GATE_Z + 60:
        return 0, MODE_CUT_FILL | CLEAR, 1.0, 0.0, B_PLAINS     # the gate's apron, level with its floors
    if lake_s(x, z, LOWER_LAKE, 0.18, 44) < 1:
        inward = (1 - lake_s(x, z, LOWER_LAKE, 0.18, 44)) * LOWER_LAKE[3]
        return round(WATER_OUT - min(8.0, 1.5 + inward * 0.3)), MODE_CUT_FILL, w, b, B_PLAINS
    pl = CLEAR if in_plaza(x, z) else 0                      # no trees anywhere round the statues
    rd = poly_d(x, z, RIVER_OUT)
    if rd <= river_hw(x, z, True) + 1 and z > 120:
        return WATER_OUT - 3, MODE_CUT_FILL | pl, w, b, B_PLAINS
    d = floor_d(x, z)
    if d <= 0:
        # the valley floor: a gentle swell, a little lower by the river
        h = 1.2 * noise(x, z, 41, 51) - 1.0 * smooth(18, 6, rd)
        return round(plaza(x, z, h)), MODE_CUT_FILL | pl, w, b, B_PLAINS
    h = mountain(x, z, d)
    c = falls_cut(x, z, h)
    if c is not None:
        return c, MODE_CUT_FILL | pl, w, b, B_STONY
    return round(plaza(x, z, h)), MODE_CUT_FILL | pl, w, b, None      # the biome's worked out from the slope, after


def biome_for(h, slope, x, z):
    if h > 232:
        return B_JAGGED if slope > 1.4 else B_SNOWY
    if slope > 1.55 or (slope > 1.2 and h > 130):
        return B_STONY
    if h > 185:
        return B_GROVE
    if h > 100:
        n = noise(x, z, 70, 61)
        return B_MEADOW if n > 0.42 else B_FOREST if n > 0.25 or h < 140 else B_GROVE
    n = noise(x, z, 90, 62)
    if h < 14 and n < 0.4:
        return B_PLAINS
    return B_CHERRY if n > 0.78 else B_FLOWERS if n > 0.62 else B_FOREST
