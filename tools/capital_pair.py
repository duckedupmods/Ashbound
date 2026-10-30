"""The angel and the devil at the valley's throat: two colossi about 130 blocks tall where the valley pinches in, one
either side of the road, facing down the valley at whoever comes up it.

The angel (west): white marble, a warrior with her sword raised and her wings spread, a still pool round her plinth.
The devil (east): black stone, horned, wings raised, hulking, fire in the cracks of him, lava round his plinth. They
stand free on tall plinths a little in front of the gorge, on level paved ground, nothing round them to hide them.

The figures are generated meshes (TRELLIS text-to-3D from our own prompts, E:/Tools/TRELLIS) sampled on the block
grid in Blender (tools/blender/mesh_vox.py), each block carrying a shade baked from ambient occlusion. Here the
shade is smoothed over the surface, stretched over the statue's own range and painted the way builders texture big
surfaces: a palette of lightness bands, light to dark, each band two to four blocks of about the same lightness but
different textures, the block within a band chosen by broad patches (like veins and weathering in stone, never
single random blocks), the step from one band to the next ordered-dithered so it's a deliberate transition.
Heights over the valley floor (capital_land's FLOOR); x east, z south.
"""
import json
import math
import os

import capital_land as L
import colourpal as CP

S = put = pick = None         # set by capital.py (its Build)

STONE = "ashbound:statue_stone"
PALE = "ashbound:pale_limestone"

PAIR_Z = 322                  # the throat
ANGEL_X, DEVIL_X = -96, 118   # either side of the road (x ~10), far enough apart that their wings don't touch
PED = 10                      # the plinth's top over the floor

# lightness bands, light to dark: [(block, weight), ...] - measured with tools/blockpal.py (L* in the comments)
TIERS = {
    "angel": [                                                                   # white marble
        [("smooth_quartz", 4), ("quartz_block", 2), ("quartz_pillar[axis=y]", 1)],         # 92
        [("calcite", 3), ("bone_block[axis=y]", 1), ("smooth_quartz", 1)],                 # 89
        [("white_concrete", 3), (PALE, 2)],                                                # 83
        [("polished_diorite", 2), ("diorite", 1), ("white_concrete", 1)],                  # 77
        [(STONE, 3), ("clay", 1), ("smooth_stone", 2)],                                    # 67
        [("andesite", 3), ("polished_andesite", 1), ("stone", 1)],                         # 56
        [("stone", 2), ("dead_tube_coral_block", 1), ("andesite", 1)],                     # 52
        [("tuff", 2), ("polished_tuff", 2)],                                               # 44
        [("cyan_terracotta", 2), ("polished_tuff", 1)],                                    # 39
    ],
    "devil": [                                                                   # black stone
        [("tuff", 2), ("polished_tuff", 2)],                                               # 45
        [("cyan_terracotta", 2), ("deepslate", 1)],                                        # 37
        [("deepslate", 2), ("cobbled_deepslate", 2), ("smooth_basalt", 1)],                # 33
        [("polished_deepslate", 2), ("smooth_basalt", 2), ("basalt[axis=y]", 1)],          # 31
        [("deepslate_tiles", 2), ("mud", 1), ("gray_concrete", 1)],                        # 24
        [("polished_blackstone", 2), ("cracked_deepslate_tiles", 1), ("deepslate_tiles", 1)],  # 21
        [("blackstone", 3), ("polished_blackstone", 1)],                                   # 15
    ],
}
SLAB_OF = {"smooth_quartz": "smooth_quartz_slab", "quartz_block": "quartz_slab", "smooth_stone": "smooth_stone_slab",
           "andesite": "andesite_slab", "polished_andesite": "polished_andesite_slab", "stone": "stone_slab",
           "diorite": "diorite_slab", "polished_diorite": "polished_diorite_slab", "tuff": "tuff_slab",
           "polished_tuff": "polished_tuff_slab", "cobbled_deepslate": "cobbled_deepslate_slab",
           "polished_deepslate": "polished_deepslate_slab", "deepslate_tiles": "deepslate_tile_slab",
           "polished_blackstone": "polished_blackstone_slab", "blackstone": "blackstone_slab",
           STONE: "ashbound:statue_stone_slab", PALE: "ashbound:pale_limestone_slab",
           "sandstone": "sandstone_slab", "smooth_sandstone": "smooth_sandstone_slab", "cut_sandstone": "cut_sandstone_slab",
           "red_sandstone": "red_sandstone_slab", "smooth_red_sandstone": "smooth_red_sandstone_slab",
           "bricks": "brick_slab", "mud_bricks": "mud_brick_slab", "granite": "granite_slab",
           "polished_granite": "polished_granite_slab", "nether_bricks": "nether_brick_slab",
           "red_nether_bricks": "red_nether_brick_slab", "end_stone_bricks": "end_stone_brick_slab",
           "prismarine": "prismarine_slab", "prismarine_bricks": "prismarine_brick_slab",
           "dark_prismarine": "dark_prismarine_slab", "purpur_block": "purpur_slab", "waxed_cut_copper": "waxed_cut_copper_slab"}
GAMMA = {"angel": 1.0, "devil": 1.5}   # >1 pushes a statue toward the dark end of its bands
PAINT_TOP = {"angel": 93.0, "devil": 72.0, "fountain": 92.0}     # the lightness the brightest paint (96th percentile) is stretched to
PAINT_CHROMA = {"angel": 1.25, "devil": 1.1, "fountain": 1.2}
BAYER = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))

CELLS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "renders", "%s_cells.json")
_CACHE = {}


def patch(x, y, z, seed):
    """Broad 3D patches, 0..1: which texture of a band a block takes."""
    return 0.5 * (L.noise(x + z * 0.61, y - z * 0.37, 7, seed) + L.noise(z - x * 0.43, y * 0.9 + x * 0.29, 11, seed + 1))


def pick_block(band, v):
    total = sum(w for _, w in band)
    acc = 0.0
    for b, w in band:
        acc += w / total
        if v <= acc:
            return b
    return band[-1][0]


def largest_piece(cells):
    """Only the cells joined to the main body (26-connected): bits the mesher left floating are dropped."""
    where = {(c[0], c[1], c[2]): i for i, c in enumerate(cells)}
    seen, best = set(), []
    for start in where:
        if start in seen:
            continue
        group, stack = [], [start]
        seen.add(start)
        while stack:
            x, y, z = stack.pop()
            group.append((x, y, z))
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        n = (x + dx, y + dy, z + dz)
                        if n in where and n not in seen:
                            seen.add(n)
                            stack.append(n)
        if len(group) > len(best):
            best = group
    print("  kept the main body: %d of %d cells" % (len(best), len(cells)))
    return [cells[where[c]] for c in best]


def figure(who):
    """{(x, y, z): state} for the angel or the devil, soles at y 0, centred on 0, 0, facing +z."""
    if who in _CACHE:
        return _CACHE[who]
    with open(CELLS % who) as f:
        cells = json.load(f)["cells"]
    tiers = TIERS.get(who)
    cells = largest_piece(cells)
    # smooth the baked shade over the surface (a generated mesh's AO is noisy); the hidden layer behind has none
    have = {(x, y, z) for x, y, z, *_ in cells}
    N6 = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
    shade = {(x, y, z): sh for x, y, z, part, sh, *_ in cells
             if any((x + a, y + b, z + c) not in have for a, b, c in N6)}
    for _ in range(2):
        nxt = {}
        for (x, y, z), sh in shade.items():
            acc, n = sh * 2, 2
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        v = shade.get((x + dx, y + dy, z + dz))
                        if v is not None and (dx or dy or dz):
                            acc, n = acc + v, n + 1
            nxt[(x, y, z)] = acc / n
        shade = nxt
    vals = sorted(shade.values())
    lo, hi = vals[len(vals) // 25], vals[len(vals) * 24 // 25]
    top = max(c[1] for c in cells)
    out, slabs = {}, []
    if len(cells[0]) > 7:                              # a repainted mesh: every block matched to its colour
        paint(who, cells, shade, lo, hi, out, slabs)
    else:
        for x, y, z, part, sh, ny, slab in cells:
            s = shade.get((x, y, z))
            if s is None:                              # hidden: anything dark will do
                out[(x, y, z)] = tiers[-1][0][0]
                continue
            lit = max(0.0, min(1.0, (s - lo) / max(1e-6, hi - lo))) ** GAMMA[who]
            t = (1.0 - lit) * (len(tiers) - 1)
            k = int(t)
            if t - k > (BAYER[(x + 2 * z) % 4][y % 4] + 0.5) / 16:   # ordered dither into the next band down
                k += 1
            k = min(k, len(tiers) - 1)
            st = pick_block(tiers[k], patch(x, y, z, 410 + k))
            # the devil burns from inside: magma in his deepest cracks on the body, never the plinth or the wingtips
            if who == "devil" and lit < 0.05 and 0.15 * top < y < 0.8 * top and patch(x, y, z, 455) > 0.45:
                st = "magma_block"
            out[(x, y, z)] = st
            if slab:
                slabs.append((x, y + 1, z, st))
    for x, y, z, st in slabs:
        if (x, y, z) not in out and st in SLAB_OF:
            out[(x, y, z)] = SLAB_OF[st] + "[type=bottom,waterlogged=false]"
    smooth_steps(out)
    if who == "angel":
        halo(out)
    _CACHE[who] = out
    return out


STAIR_OF = {"smooth_quartz": "smooth_quartz_stairs", "quartz_block": "quartz_stairs", "stone": "stone_stairs",
            "andesite": "andesite_stairs", "polished_andesite": "polished_andesite_stairs", "diorite": "diorite_stairs",
            "polished_diorite": "polished_diorite_stairs", "granite": "granite_stairs",
            "polished_granite": "polished_granite_stairs", "tuff": "tuff_stairs", "polished_tuff": "polished_tuff_stairs",
            "cobbled_deepslate": "cobbled_deepslate_stairs", "polished_deepslate": "polished_deepslate_stairs",
            "deepslate_tiles": "deepslate_tile_stairs", "blackstone": "blackstone_stairs",
            "polished_blackstone": "polished_blackstone_stairs", "sandstone": "sandstone_stairs",
            "smooth_sandstone": "smooth_sandstone_stairs", "red_sandstone": "red_sandstone_stairs",
            "smooth_red_sandstone": "smooth_red_sandstone_stairs", "bricks": "brick_stairs", "mud_bricks": "mud_brick_stairs",
            "nether_bricks": "nether_brick_stairs", "red_nether_bricks": "red_nether_brick_stairs",
            "end_stone_bricks": "end_stone_brick_stairs", "prismarine": "prismarine_stairs",
            "prismarine_bricks": "prismarine_brick_stairs", "dark_prismarine": "dark_prismarine_stairs",
            "purpur_block": "purpur_stairs", "waxed_cut_copper": "waxed_cut_copper_stairs",
            STONE: "ashbound:statue_stone_stairs", PALE: "ashbound:pale_limestone_stairs"}
# the angel is marble and gold only: no brown, pink, blue or mud the generator's dim paint would pull in
ONLY = {"angel": ("smooth_quartz", "quartz_block", "quartz_bricks", "calcite", "bone_block", "white_concrete", PALE,
                  STONE, "clay", "smooth_stone", "andesite", "polished_andesite", "stone", "light_gray_concrete",
                  "iron_block", "gold_block", "ashbound:gilded_tiles",
                  "yellow_terracotta", "smooth_sandstone", "cut_sandstone"),
        # the market fountain's maiden: marble, a sky-blue robe shading to teal, a bronze jar, gilt hems
        "fountain": ("smooth_quartz", "quartz_block", "calcite", "white_concrete", PALE, STONE, "smooth_stone",
                     "polished_andesite", "light_gray_concrete", "clay", "light_blue_terracotta", "light_blue_concrete",
                     "cyan_terracotta", "waxed_weathered_copper", "waxed_cut_copper", "waxed_copper_block", "gold_block",
                     "ashbound:gilded_tiles", "yellow_terracotta")}
FACING = {(1, 0): "east", (-1, 0): "west", (0, 1): "south", (0, -1): "north"}


def smooth_steps(out):
    """Stairs where the block surface steps: an empty cell sitting on (or hanging under) the statue with a wall of it on
    exactly one side gets a stair leaning into that wall, so slopes and overhangs ramp instead of jagging. The stair
    takes the block of the cell it rests on, so the colour carries on."""
    solid = {k for k, v in out.items() if "[" not in v or v.startswith(("quartz_pillar", "bone_block", "basalt"))}
    adds = {}
    for (x, y, z) in solid:
        for dy, half in ((1, "bottom"), (-1, "top")):
            p = (x, y + dy, z)
            if p in out or p in adds:
                continue
            walls = [d for d in FACING if (x + d[0], y + dy, z + d[1]) in solid]
            if len(walls) != 1:
                continue
            d = walls[0]
            if (x - d[0], y + dy, z - d[1]) in out:            # boxed in on the open side too: leave it
                continue
            st = STAIR_OF.get(out[(x, y, z)])
            if st:
                adds[p] = "%s[facing=%s,half=%s,shape=straight,waterlogged=false]" % (st, FACING[d], half)
    out.update(adds)
    print("  stairs:", len(adds))


def halo(out):
    """A glowing gold ring standing behind the angel's head, fixed to the back of it by a short gold spoke."""
    top = max(y for (x, y, z) in out if abs(x) <= 8)
    head = [(x, y, z) for (x, y, z) in out if abs(x) <= 8 and y >= top - 12]
    hx = round(sum(c[0] for c in head) / len(head))
    hy = top - 6
    back = min(z for (x, y, z) in head)              # the back of the head (the figure faces +z)
    hz = back - 4
    R = 16
    n = 0
    for a in range(720):
        t = math.radians(a / 2)
        for dr in (-1.0, -0.5, 0.0, 0.5, 1.0):
            x, y = hx + round((R + dr) * math.cos(t)), hy + round((R + dr) * math.sin(t))
            if (x, y, hz) not in out:
                out[(x, y, hz)] = "ochre_froglight[axis=z]" if (a // 24) % 5 else "gold_block"
                n += 1
    for z in range(hz + 1, back):                     # the spoke into the back of the head
        out.setdefault((hx, hy, z), "gold_block")
    print("  halo: %d blocks round (%d, %d) at z %d" % (n, hx, hy, hz))


def paint(who, cells, shade, lo, hi, out, slabs):
    """The painted statue: the mesh's own colours (smoothed over the surface so the generator's noise goes), darkened
    in the crevices by the baked shade, each block the nearest in colour (colourpal), the in-between colours an
    ordered dither of two blocks. Hot colours on the devil (fire, the eyes, the lava in him) become glowing blocks."""
    surf = {(c[0], c[1], c[2]): CP.lab(c[7]) for c in cells if (c[0], c[1], c[2]) in shade}
    # the generator paints dim: stretch each statue so its brightest paint reaches its own top lightness, and lift
    # the colour a little (dull gold reads as mud in blocks)
    ls = sorted(v[0] for v in surf.values())
    gain = PAINT_TOP.get(who, 90.0) / max(1.0, ls[len(ls) * 96 // 100])
    surf = {k: (min(97.0, v[0] * gain), v[1] * PAINT_CHROMA.get(who, 1.2), v[2] * PAINT_CHROMA.get(who, 1.2)) for k, v in surf.items()}
    for _ in range(3):
        nxt = {}
        for (x, y, z), v in surf.items():
            acc, n = [v[0] * 2, v[1] * 2, v[2] * 2], 2
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        w = surf.get((x + dx, y + dy, z + dz))
                        if w is not None and (dx or dy or dz):
                            acc = [acc[0] + w[0], acc[1] + w[1], acc[2] + w[2]]
                            n += 1
            nxt[(x, y, z)] = (acc[0] / n, acc[1] / n, acc[2] / n)
        surf = nxt
    fill = "blackstone" if who == "devil" else "smooth_stone"
    for x, y, z, part, sh, ny, slab, rgb in cells:
        c = surf.get((x, y, z))
        if c is None:                                  # hidden behind the shell
            out[(x, y, z)] = fill
            continue
        lit = max(0.0, min(1.0, (shade[(x, y, z)] - lo) / max(1e-6, hi - lo)))
        Lp, a, b = c
        hot = who == "devil" and a > 14 and b > 30 and Lp > 62     # only the hottest paint glows (flames, cracks)
        if who != "devil" and b > 8 and a > -6:        # the gilding: the generator paints it thin and dull - make it gold
            g = min(1.0, (b - 8) / 12)
            Lp, a, b = min(90.0, Lp + 14.0 * g), a, b * (1 + 0.9 * g)
        if who == "fountain":                          # the generator tints her all murky teal: marble skin, sky-blue robe
            if Lp > 66:
                Lp, a, b = min(95.0, Lp + 18.0), a * 0.25, b * 0.25
            elif a < -4:
                Lp, a, b = min(88.0, Lp + 16.0), a * 0.5, min(b * 1.5, -16.0)
        # marble stays bright in its folds; the devil's black stone goes deep
        k = 0.6 + 0.5 * lit if who == "devil" else 0.78 + 0.27 * lit
        L2 = min(98.0, Lp * k)
        ch = (L2 / max(Lp, 1.0)) ** 0.6
        d = (BAYER[(x + 2 * z) % 4][y % 4] + 0.5) / 16 - 0.5     # a faint ordered dither, lightness only: clean
        want = (L2 + 1.5 * d, a * ch, b * ch)                    # bands, no checkerboard
        if who == "angel" and z >= 20 and x <= -18 and y >= 128:   # her raised blade shines
            st = "pearlescent_froglight[axis=y]"
        elif hot:
            st = CP.match((Lp, a, b), patch(x, y, z, 470), glow=True,
                          only=("magma_block", "shroomlight", "ochre_froglight", "glowstone"))
        else:
            st = CP.match(want, patch(x, y, z, 410), only=ONLY.get(who))
        out[(x, y, z)] = st
        if slab:
            slabs.append((x, y + 1, z, st))


def placed(who):
    """The figure's cells in the world."""
    cx = ANGEL_X if who == "angel" else DEVIL_X
    return {(cx + x, PED + 1 + y, PAIR_Z + z): st for (x, y, z), st in figure(who).items()}


def footprint(who):
    """Half-sizes (x, z) and centre z of the statue's base, for the plinth."""
    base = [(x, z) for (x, y, z) in figure(who) if y < 10]
    xs, zs = [p[0] for p in base], [p[1] for p in base]
    return (max(xs) - min(xs)) / 2 + 7, (max(zs) - min(zs)) / 2 + 7, (max(zs) + min(zs)) / 2


# ================================================================ the plinth, the pool, the paving

def plinth(kx, kz, ground, devil, A, B, zc):
    """A tall stepped plinth of dressed dark stone (rounded corners, a carved band under the cap), ringed by a
    trench - a still pool round her, lava round him - and a paved apron out to the grass."""
    def q(xr, zr, grow):
        return (abs(xr) / (A + grow)) ** 4 + (abs(zr - zc) / (B + grow)) ** 4
    liquid = "lava" if devil else "water"
    R = int(max(A, B) + 18)
    for xr in range(-R, R + 1):
        for zr in range(int(zc) - R, int(zc) + R + 1):
            x, z = kx + xr, kz + zr
            g = ground(x, z)
            if q(xr, zr, 0) <= 1:                       # the core, up to the statue's feet
                for y in range(g - 3, PED + 1):
                    band = y == PED - 2
                    put(x, y, z, "polished_deepslate" if y == PED else "chiseled_deepslate" if band else
                        "deepslate_tiles" if (y + (xr + zr) // 4) % 5 == 0 else "deepslate_bricks")
            elif q(xr, zr, 3) <= 1:                     # the upper step
                for y in range(g - 3, PED - 3):
                    put(x, y, z, "polished_deepslate" if y == PED - 4 else "deepslate_bricks")
            elif q(xr, zr, 6) <= 1:                     # the lower step
                for y in range(g - 3, PED - 6):
                    put(x, y, z, "polished_deepslate" if y == PED - 7 else "deepslate_bricks")
            elif q(xr, zr, 9) <= 1:                     # the trench: two deep, the liquid level with the paving
                put(x, -2, z, "deepslate_bricks" if not devil else "basalt[axis=y]")
                for y in (-1, 0):
                    put(x, y, z, liquid)
                for y in range(1, g + 2):
                    put(x, y, z, None)
            elif q(xr, zr, 10) <= 1:                    # its kerb
                for y in range(-2, 1):
                    put(x, y, z, "polished_blackstone_bricks")
                put(x, 1, z, "polished_blackstone_slab[type=bottom,waterlogged=false]")
                for y in range(2, g + 2):
                    put(x, y, z, None)
            elif q(xr, zr, 16) <= 1:                    # the paved apron
                v = L.noise(x * 0.7, z * 0.7, 3, 307)
                put(x, 0, z, "polished_deepslate" if v > 0.62 else "deepslate_tiles" if v > 0.3 else "cracked_deepslate_tiles")
                put(x, -1, z, "stone")
                for y in range(1, g + 2):
                    put(x, y, z, None)


def stand(who, ground):
    devil = who == "devil"
    kx = DEVIL_X if devil else ANGEL_X
    A, B, zc = footprint(who)
    plinth(kx, PAIR_Z, ground, devil, A, B, zc)
    for (x, y, z), st in placed(who).items():
        put(x, y, z, st)
    # braziers on the plinth's front corners: blue soul fire for her, fire for him
    fire = "campfire" if devil else "soul_campfire"
    for sx in (-1, 1):
        x, z = kx + sx * int(A - 3), PAIR_Z + int(zc + B - 3)
        while S.get(x, PED, z) is None and abs(x - kx) > 2:   # in off the rounded corner, onto the plinth's top
            x, z = x - sx, z - 1
        put(x, PED + 1, z, "polished_blackstone_wall")
        put(x, PED + 2, z, fire + "[facing=south,lit=true,signal_fire=false,waterlogged=false]")


def build(ground):
    for who in ("angel", "devil"):
        stand(who, ground)
    print("pair: angel %d, devil %d blocks" % (len(figure("angel")), len(figure("devil"))))
