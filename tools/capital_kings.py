"""The two kings in the gorge: stone colossi 95 blocks tall carved into great rock pillars where the valley's throat
pinches in, one either side of the road and the river, facing down the valley at whoever comes up it. Each holds his
outer hand up, palm out (stop, and be known), the other resting on the pommel of a greatsword grounded before his
feet; crowned, bearded, cloaked.

The figures are sculpted, not stacked: a body made of smooth 3D shapes (capsules, ellipsoids, rounded cones) blended
into each other, then turned into blocks, only a shell of it kept, slabs laid on its upward faces to soften the
steps. Each stands in a pointed niche cut into its pillar, the niche's back dark so the pale stone reads against it.

Heights over the valley floor (capital_land's FLOOR); x east, z south.
"""
import json
import math
import os

import capital_land as L

S = put = pick = None         # set by capital.py (its Build)

STONE = "ashbound:statue_stone"
STONE_SLAB = "ashbound:statue_stone_slab[type=bottom,waterlogged=false]"
GILT = "ashbound:gilded_tiles"
BLADE = "ashbound:pale_limestone"
BACK = "polished_deepslate"
RIM = "polished_blackstone_bricks"

KING_Z = 322                  # the throat
KINGS = ((-50, -1), (70, 1))  # (x, side of the raised hand): each raises the hand away from the road
PED = 10                      # the pedestal's top over the floor
NICHE_HALF, NICHE_SPRING, NICHE_RISE = 32, 110, 22
PILLAR_TOP = 150

noise = L.noise


# ================================================================ shapes

def length(x, y, z):
    return math.sqrt(x * x + y * y + z * z)


def smin(a, b, k):
    h = max(0.0, min(1.0, 0.5 + 0.5 * (b - a) / k))
    return b + (a - b) * h - k * h * (1 - h)


def sph(p, c, r):
    return length(p[0] - c[0], p[1] - c[1], p[2] - c[2]) - r


def ell(p, c, r):
    """An ellipsoid (a fair distance near its surface, which is all a shell needs)."""
    k0 = length((p[0] - c[0]) / r[0], (p[1] - c[1]) / r[1], (p[2] - c[2]) / r[2])
    return (k0 - 1.0) * min(r)


def cone(p, a, b, ra, rb):
    """A capsule whose radius runs from ra at a to rb at b."""
    bx, by, bz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    px, py, pz = p[0] - a[0], p[1] - a[1], p[2] - a[2]
    bb = bx * bx + by * by + bz * bz
    t = max(0.0, min(1.0, (px * bx + py * by + pz * bz) / bb))
    return length(px - bx * t, py - by * t, pz - bz * t) - (ra + (rb - ra) * t)


def box(p, c, h, rr=0.0):
    qx, qy, qz = abs(p[0] - c[0]) - h[0], abs(p[1] - c[1]) - h[1], abs(p[2] - c[2]) - h[2]
    return length(max(qx, 0.0), max(qy, 0.0), max(qz, 0.0)) + min(max(qx, qy, qz), 0.0) - rr


# ================================================================ the king

# each part's stone, as a ramp from lit (first) to shadowed (last): the shading's painted with the blocks, the way the
# great statue builds do it, so the figure reads in any light
# each part's stone, as a ramp from lit (first) to shadowed (last): the shading's painted with the blocks, the way the
# great statue builds do it, so the figure reads in any light. Picked with tools/blockpal.py off the real textures:
# smooth ones only (gritty diorite and the like speckle a shaded surface), roughly even steps in lightness (CIE L*
# in the comments), nothing that falls (concrete powder)
PALE = "ashbound:pale_limestone"
RAMPS = {
    #        92               82    70     65              57          53       43
    "skin": ["smooth_quartz", PALE, STONE, "smooth_stone", "andesite", "stone", "polished_tuff"],
    #        90 (lined, like strands)  85  70  65  53  43
    "hair": ["bone_block[axis=y]", "white_concrete", STONE, "smooth_stone", "stone", "polished_tuff"],
    "robe": [PALE, STONE, "smooth_stone", "andesite", "stone", "polished_tuff", "cyan_terracotta"],
    #          65              57          53       43               38                 31
    "armour": ["smooth_stone", "andesite", "stone", "polished_tuff", "cyan_terracotta", "polished_deepslate"],
    "cloak": ["stone", "polished_tuff", "cyan_terracotta", "polished_deepslate", "deepslate_tiles"],
    "blade": ["iron_block", "white_concrete", "smooth_stone", "andesite"],
    "gilt": ["gold_block", GILT, GILT, "yellow_terracotta"],
}
SLABS = {"smooth_quartz", "smooth_stone", "andesite", "stone", "polished_tuff", "polished_deepslate", STONE, PALE}


def king_sdf(x, y, z, s):
    """(distance to the figure, {part: distance}) at x, y, z (y up from his soles, z toward his front), s the side of
    his raised hand."""
    p = (x, y, z)
    o = -s
    g = {}
    d = 1e9

    def add(part, v, k):
        nonlocal d
        if v < g.get(part, 1e9):
            g[part] = v
        d = smin(d, v, k) if k else min(d, v)
    th = math.atan2(x, z)
    # the robe: a heavy pleated skirt flaring from the waist to the ground, its hem turned up over his feet
    fold = max(0.0, (48 - y) / 48.0)
    robe = cone((x, y, z * 1.35), (0, 50, 0), (0, 0.5, 0), 9.5, 15.5) - 0.9 * fold * math.sin(13 * th)
    robe = smin(robe, max(cone((x, y, z * 1.3), (0, 4.0, 0), (0, 1.0, 0), 15.2, 16.4), abs(y - 2.5) - 1.6), 0.8)
    add("robe", robe, 0)
    for fx in (-5.0, 5.0):
        add("armour", ell(p, (fx, 1.6, 8.0), (3.2, 2.2, 5.0)), 1.5)
    # a tabard hanging down his front, gilded at its hem
    tab = box(p, (0, 30, 9.6 + max(0.0, (40 - y)) * 0.05), (5.0, 18.0, 0.9), 0.4)
    add("robe", tab, 0.6)
    # the body: a belted waist, a breastplate with its ridge and lames, pauldrons of three plates each
    add("armour", ell(p, (0, 51, 0), (10.0, 7.0, 7.8)), 3.0)
    add("armour", ell(p, (0, 62, 0.5), (12.5, 12.0, 8.5)), 4.0)
    add("armour", ell(p, (0, 62.5, 8.6), (1.1, 9.0, 1.2)), 0.8)                     # the breastplate's ridge
    for ly in (53.5, 56.5):
        add("armour", max(ell(p, (0, ly, 0.3), (11.0, 1.1, 8.6)), -z), 0.4)          # the lames over the belly
    for sx in (-1, 1):
        for i, (dx, dy, r) in enumerate(((13.3, 71.5, (6.6, 3.6, 6.8)), (14.6, 68.8, (7.0, 2.8, 7.2)),
                                          (15.5, 66.3, (7.0, 2.3, 7.2)))):
            add("armour", ell(p, (sx * dx, dy, 0.2), r), 0.5 if i else 2.5)
        add("gilt", max(ell(p, (sx * 13.3, 72.6, 0.2), (6.9, 1.0, 7.1)), 72.0 - y), 0)   # their gilded rims
    cloak = cone(p, (0, 72, -4.5), (o * 3.0, 1, -11.0), 13.5, 19.0) - 0.9 * math.sin(9 * th) * max(0.0, (70 - y) / 70.0)
    add("cloak", max(cloak, z + 0.5), 2.5)
    # neck, head with its brow, nose, cheekbones and sunk eyes; the long braided beard and moustache; hair behind
    add("skin", cone(p, (0, 71, 0), (0, 77, 0.8), 3.9, 3.6), 1.5)
    head = ell(p, (0, 82.5, 1.0), (5.7, 7.0, 6.1))
    head = smin(head, ell(p, (0, 81.6, 6.9), (1.3, 2.3, 1.7)), 0.8)                 # the nose
    head = smin(head, ell(p, (0, 84.6, 5.7), (4.8, 1.2, 1.6)), 0.8)                 # the brow
    for cx_ in (-3.2, 3.2):
        head = smin(head, ell(p, (cx_, 81.4, 5.0), (1.6, 1.2, 1.4)), 0.8)          # the cheekbones
    for ex in (-2.3, 2.3):
        head = max(head, -sph(p, (ex, 83.2, 7.0), 1.6))                             # the eyes, deep under the brow
    add("skin", head, 1.0)
    beard = cone(p, (0, 78.0, 5.8), (0, 62.0, 10.4), 4.6, 1.6) + 0.35 * math.sin(x * 2.4 + y * 0.3)
    add("hair", beard, 1.2)
    for bx in (-1.6, 1.6):
        add("hair", cone(p, (bx, 64.0, 10.0), (bx * 1.2, 55.0, 10.6), 1.3, 0.8), 0.6)   # its two braids
        add("gilt", sph(p, (bx * 1.2, 54.6, 10.6), 1.0), 0)                             # gold beads on their ends
    for mx in (-1, 1):
        add("hair", cone(p, (mx * 0.8, 79.4, 7.4), (mx * 4.2, 76.6, 6.6), 1.2, 0.7), 0.5)   # the moustache
    add("hair", cone(p, (0, 85, -3.0), (0, 69, -6.0), 5.6, 6.2) + 0.3 * math.sin(th * 14), 1.5)
    add("hair", ell(p, (0, 86.0, 0.6), (5.9, 3.2, 6.0)), 1.0)
    # the raised arm: up and forward, gauntleted to the wrist, the open hand palm out at the height of his crown
    sh = (s * 13.5, 69.0, 0.0)
    el = (s * 20.0, 75.0, 8.0)
    wr = (s * 20.0, 86.0, 15.0)
    add("armour", cone(p, sh, el, 4.4, 3.7), 1.5)
    add("armour", sph(p, el, 4.3), 0.8)                                               # the elbow cop
    add("armour", cone(p, el, wr, 3.7, 3.1), 1.2)
    add("armour", cone(p, (s * 20.0, 82.0, 13.0), (s * 20.0, 85.6, 14.8), 3.9, 3.7), 0.5)   # the gauntlet's cuff
    hc = (s * 20.0, 90.0, 16.4)
    add("skin", box(p, hc, (2.3, 2.6, 0.7), 0.8), 1.0)
    for i, fx in enumerate((-1.6, -0.5, 0.6, 1.7)):
        top = 95.7 if i in (1, 2) else 94.9
        add("skin", cone(p, (hc[0] + s * fx, 92.0, 16.4), (hc[0] + s * fx, top, 16.6), 0.75, 0.6), 0.4)
    add("skin", cone(p, (hc[0] - s * 2.6, 88.5, 16.2), (hc[0] - s * 4.3, 91.5, 16.8), 0.85, 0.65), 0.4)
    # the sword arm: down and in, the gauntleted hand resting on the pommel before him
    sh2 = (o * 13.5, 69.0, 0.0)
    el2 = (o * 16.0, 57.0, 5.0)
    wr2 = (o * 3.5, 52.0, 13.5)
    add("armour", cone(p, sh2, el2, 4.4, 3.7), 1.5)
    add("armour", sph(p, el2, 4.3), 0.8)
    add("armour", cone(p, el2, wr2, 3.7, 3.1), 1.2)
    add("armour", ell(p, (o * 0.4, 52.0, 15.0), (3.6, 2.8, 3.4)), 1.0)
    # the sword: a fullered blade down to the ground before his feet
    blade = box(p, (0, 25.0, 16.0), (2.6, 18.0, 0.8), 0.2)
    blade = min(blade, cone(p, (0, 7.5, 16.0), (0, 0.6, 16.0), 2.7, 0.3))
    blade = max(blade, -box(p, (0, 27.0, 17.0), (0.6, 14.0, 0.5)))                     # the fuller
    add("blade", max(blade, abs(z - 16.0) - 0.9), 0)
    gilt = box(p, (0, 44.0, 16.0), (8.5, 1.0, 1.2), 0.3)
    for gx in (-1, 1):
        gilt = min(gilt, sph(p, (gx * 9.0, 44.8, 16.0), 1.5))                          # the guard's knobbed ends
    gilt = min(gilt, cone(p, (0, 44.5, 16.0), (0, 48.5, 16.0), 1.2, 1.2))
    gilt = min(gilt, sph(p, (0, 49.3, 16.0), 1.9))
    # the crown: a band round his brow, seven tall points
    gilt = min(gilt, max(abs(length(x, 0, z - 1.0) - 6.0) - 1.0, abs(y - 87.0) - 1.6))
    for i in range(7):
        a = math.radians(-90 + i * 30)
        tall = 95.5 if i == 3 else 94.0 if i in (2, 4) else 92.5
        gilt = min(gilt, cone(p, (math.sin(a) * 6.0, 88.0, 1.0 + math.cos(a) * 6.0),
                              (math.sin(a) * 5.7, tall, 1.0 + math.cos(a) * 5.7), 1.1, 0.25))
    gilt = min(gilt, max(abs(length(x, 0, z) - 10.4) - 0.8, abs(y - 49.5) - 1.1))     # the belt
    gilt = min(gilt, box(p, (0, 49.5, 10.4), (2.0, 1.8, 0.8), 0.3))                   # its buckle
    gilt = min(gilt, max(tab, abs(y - 13.5) - 0.9) - 0.15)                            # the tabard's hem
    add("gilt", gilt, 0)
    return d, g


def _normal(x, y, z, s):
    e = 0.6
    return (king_sdf(x + e, y, z, s)[0] - king_sdf(x - e, y, z, s)[0],
            king_sdf(x, y + e, z, s)[0] - king_sdf(x, y - e, z, s)[0],
            king_sdf(x, y, z + e, s)[0] - king_sdf(x, y, z - e, s)[0])


_CACHE = {}


CELLS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "renders", "king_cells.json")


def king_cells(s):
    """{(x, y, z): state} for a king, his soles at y 0, centred on 0, 0. The figure's sculpted as a mesh in Blender
    (tools/blender/king_sculpt.py) and sampled on the block grid there, each block coming with its part and a shade
    baked from ambient occlusion and the sky; here the shade picks the block off its part's ramp. Mirrored for the
    king whose raised hand is on the west."""
    if s in _CACHE:
        return _CACHE[s]
    if -s in _CACHE:
        _CACHE[s] = {(-1 - x, y, z): st for (x, y, z), st in _CACHE[-s].items()}
        return _CACHE[s]
    with open(CELLS) as f:
        cells = json.load(f)["cells"]
    out = {}
    slabs = []
    for x, y, z, part, shade, ny, slab in cells:
        lit = (shade - 0.1) / 0.65 + 0.03 * (L.noise(x * 3.1, y * 2.3 + z * 1.7, 2, 311) - 0.5)
        ramp = RAMPS[part]
        k = int(round((1.0 - max(0.0, min(1.0, lit))) * (len(ramp) - 1)))
        st = ramp[max(0, min(len(ramp) - 1, k))]
        out[(x, y, z)] = st
        if slab:
            slabs.append((x, y + 1, z, st))
    for x, y, z, st in slabs:
        if (x, y, z) not in out and st in SLABS:
            out[(x, y, z)] = st + "_slab[type=bottom,waterlogged=false]"
    if s < 0:
        out = {(-1 - x, y, z): st for (x, y, z), st in out.items()}
    _CACHE[s] = out
    return out


# ================================================================ the pillar, the niche, the pedestal

def pointed(ax, half, rise):
    if ax > half:
        return -999
    rc = half * 1.6
    return math.sqrt(max(0.0, rc * rc - (ax + rc - half) ** 2)) * rise / math.sqrt(rc * rc - (rc - half) ** 2)


def pillar(kx, kz, s, ground):
    """The rock the king is carved from: a great buttress of the gorge wall, its top falling outward into the
    mountain, a pointed niche cut into its face, dark at the back."""
    cols = {}
    for xr in range(-36, 72):
        for zr in range(-38, 10):
            out = xr * s                       # outward, away from the road
            if out < -33:
                continue
            x, z = kx + xr, kz + zr
            g = ground(x, z)
            n = 4.0 * L.snoise(x, z, 9, 301) + 2.0 * L.snoise(x, z, 4, 302)
            top = PILLAR_TOP + n - max(0.0, out - 22) * 2.0 - ((zr + 14) / 22.0) ** 2 * 26
            # the inner side and the front rounded off a little, rough
            edge = min(out + 33, 10 - zr, zr + 38) + 5 * L.snoise(x * 0.5, z * 0.5, 6, 303)
            if edge < 7:
                top -= (7 - edge) * 9
            top = int(top)
            if top <= g:
                continue
            niche = None
            if abs(xr) < NICHE_HALF and zr > -16:
                niche = (PED + 1 if zr > -12 else 1, int(NICHE_SPRING + pointed(abs(xr), NICHE_HALF, NICHE_RISE)))
            cols[(x, z)] = (g - 6, top, niche)

    def solid(x, y, z):
        c = cols.get((x, z))
        if c is None or not (c[0] <= y <= c[1]):
            return False
        nz = c[2]
        return not (nz and nz[0] <= y <= nz[1])
    for (x, z), (b, top, nz) in cols.items():
        zr = z - kz
        for y in range(b, top + 1):
            if not solid(x, y, z):
                continue
            exposed = (y >= top - 2 or not solid(x + 1, y, z) or not solid(x - 1, y, z) or not solid(x, y, z + 1)
                       or not solid(x, y, z - 1) or not solid(x, y + 1, z))
            if not exposed:
                continue
            xr = x - kx
            near_niche = abs(xr) < NICHE_HALF + 3 and zr > -19 and y < NICHE_SPRING + NICHE_RISE + 4
            if near_niche and zr <= -12:
                put(x, y, z, BACK)
            elif near_niche and zr >= 5 and abs(xr) >= NICHE_HALF - 1 and not (nz and y > nz[1] + 3):
                put(x, y, z, RIM)
            elif near_niche and zr >= 5 and nz is None and y > NICHE_SPRING - 2:
                put(x, y, z, RIM)
            elif y >= top - 1 and L.noise(x, z, 3, 304) > 0.45 and y < 140:
                put(x, y, z, "moss_block")
            else:
                band = L.noise(x * 0.3 + z * 0.2, y * 0.6, 7, 305)
                put(x, y, z, "tuff" if band > 0.72 else "smooth_basalt" if band < 0.16 else "deepslate")
    # the pedestal: dressed dark stone stepped out of the niche floor
    for xr in range(-18, 19):
        for zr in range(-12, 22):
            x, z = kx + xr, kz + zr
            step = 0 if zr <= 14 and abs(xr) <= 15 else 1 if zr <= 17 and abs(xr) <= 17 else 2
            if step == 2 and (zr > 21 or abs(xr) > 18):
                continue
            top = PED - step * 3
            for y in range(ground(x, z) - 3, top + 1):
                put(x, y, z, "deepslate_bricks" if y < top else "polished_deepslate")


def king(kx, kz, s, ground):
    pillar(kx, kz, s, ground)
    for (x, y, z), st in king_cells(s).items():
        put(kx + x, PED + 1 + y, kz + z, st)
    # braziers at the pedestal's front corners
    for sx in (-1, 1):
        x, z = kx + sx * 13, kz + 12
        put(x, PED + 1, z, "polished_blackstone_wall")
        put(x, PED + 2, z, "campfire[facing=south,lit=true,signal_fire=false,waterlogged=false]")


def build(ground):
    for kx, s in KINGS:
        king(kx, KING_Z, s, ground)
    print("kings: %d blocks each" % len(king_cells(1)))
