"""Roster v2 dungeons' props as real meshes (propkit.py bakes and writes them): the shapes every dungeon needs
(its lantern, chain, bars for the seal, the coffer that holds the loot) made in that dungeon's own materials, and the
props only it has (UNIQUE). Names: <prefix>_lantern, <prefix>_chain, <prefix>_bars(_post/_side), <prefix>_coffer.

  blender -b -P tools/blender/kit_props.py -- <gate> [preview] [fast] [names...]
    preview -> tools/renders/<gate>_props.png"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "propkit.py"), encoding="utf-8").read())

GATE = ARGS[0]
ONLY = [a for a in ARGS[1:] if a not in ("preview", "fast")]


def lin(c):
    """sRGB hex -> linear colour, so the palettes read like the block textures"""
    c = c.lstrip("#")
    return tuple(((int(c[i:i + 2], 16) / 255) ** 2.2) for i in (0, 2, 4))


def stops(*hs):
    n = len(hs) - 1
    return [(k / n, lin(h)) for k, h in enumerate(hs)]


# ---------------------------------------------------------------- each dungeon's materials

PALETTES = {
    "serpent_ziggurat": dict(prefix="coil", metal=("#3a2606", "#8a6214"), accent=("#105238", "#18704c", "#3ab47e"),
                             wood=("#1c140c", "#3a2a1a", "#5c482c"), glow="#3ad486", stone=("#383d32", "#6a7160"),
                             cloth=("#561610", "#92281c")),
    "rimeholt": dict(prefix="rime", metal=("#16191e", "#68a4c6"), accent=("#2a8ad8", "#5ab8f4", "#c8dcea"),
                     wood=("#140e0a", "#2a2016", "#463626"), glow="#5ab8f4", stone=("#1c222c", "#3b4555"),
                     cloth=("#8a8a84", "#c6c6bc")),
    "glass_minaret": dict(prefix="minaret", metal=("#4a300e", "#bc8a38"), accent=("#18767e", "#3cbab8", "#f4d870"),
                          wood=("#2a1408", "#542e16", "#86502a"), glow="#ffc84a", stone=("#866848", "#d2b48a"),
                          cloth=("#105660", "#24989c")),
    "warlords_fang": dict(prefix="fang", metal=("#1e1612", "#7a3c18"), accent=("#6a6050", "#a89c82", "#dcd2b8"),
                          wood=("#1c120a", "#3a2818", "#5e462a"), glow="#ff8a1c", stone=("#521e14", "#a04a2e"),
                          cloth=("#5a100a", "#16100c")),
    "clockwork_spire": dict(prefix="spire", metal=("#15171b", "#86581c"), accent=("#5c3a10", "#b07a2a", "#f2cc72"),
                            wood=("#1a120c", "#30231a", "#4a3828"), glow="#ffb53a", stone=("#211f25", "#46424b"),
                            cloth=("#3a1a12", "#6a3020")),
    "weeping_mine": dict(prefix="mine", metal=("#1a1a1c", "#3a2414"), accent=("#5a361c", "#a0622e", "#c88444"),
                         wood=("#1a120c", "#382617", "#5e4229"), glow="#7ce8d8", stone=("#1d2128", "#3f4652"),
                         cloth=("#2a241c", "#55493c")),
    "tide_chapel": dict(prefix="tide", metal=("#1e2414", "#3e7a64"), accent=("#2e3420", "#5a5a36", "#7a7444"),
                        wood=("#2a2622", "#4c4640", "#726a60"), glow="#b4e4e6", stone=("#2a3634", "#5a6c68"),
                        cloth=("#1e3a20", "#40703e")),
    "brigands_gorge": dict(prefix="gorge", metal=("#16161a", "#6a3418"), accent=("#7a4c10", "#a87018", "#ecbc34"),
                           wood=("#1e140c", "#40301c", "#6a5232"), glow="#ffa04a", stone=("#52261a", "#a45a3a"),
                           cloth=("#44100a", "#82261a")),
    "rookery": dict(prefix="rook", metal=("#0c0c10", "#2a2430"), accent=("#5a5446", "#9a927c", "#d8d0b8"),
                    wood=("#0c0a0a", "#201a1a", "#3a3030"), glow="#9a84d4", stone=("#16161c", "#34343e"),
                    cloth=("#3e3620", "#867846")),
    "hollow_circus": dict(prefix="circus", metal=("#1a1418", "#3a2a1a"), accent=("#7a4c10", "#d0961f", "#ffdc6a"),
                          wood=("#2e1810", "#583222", "#70422e"), glow="#ffc870", stone=("#2a202a", "#463848"),
                          cloth=("#741a24", "#b03242")),
    "mirefen_coven": dict(prefix="mire", metal=("#101010", "#2a2a14"), accent=("#544c34", "#8a7e5a", "#a69a70"),
                          wood=("#1e1a12", "#3c3424", "#62563c"), glow="#7ce04a", stone=("#24281e", "#4e5844"),
                          cloth=("#2c4a16", "#527c28")),
    "sandsunk_tomb": dict(prefix="tomb", metal=("#2a1a08", "#8a6214"), accent=("#8a6214", "#dab43c", "#f4d870"),
                          wood=("#2a160a", "#563018", "#86522a"), glow="#ffb030", stone=("#76542a", "#c8a060"),
                          cloth=("#122048", "#3a5ca4")),
    "fallen_titan": dict(prefix="titan", metal=("#2a2418", "#5a1010"), accent=("#6a6250", "#aaa286", "#e2dcc4"),
                         wood=("#3a2418", "#6a4a34", "#92806e"), glow="#78d030", stone=("#5e1010", "#ae3a2e"),
                         cloth=("#7a3038", "#b45c5c")),
    "jade_monastery": dict(prefix="jade", metal=("#14181a", "#1c5c38"), accent=("#8a6214", "#dab43c", "#f4d870"),
                           wood=("#460a08", "#821c12", "#9e2a1a"), glow="#9af0c0", stone=("#68665e", "#b6b4a6"),
                           cloth=("#1c5c38", "#3e9660")),
    "storm_bastion": dict(prefix="storm", metal=("#181a1e", "#2a705c"), accent=("#1c5446", "#3e8c74", "#5aa88e"),
                          wood=("#0e0c0a", "#221c16", "#3a3026"), glow="#7ab0ff", stone=("#222a32", "#485664"),
                          cloth=("#1c283a", "#364a68")),
    "bloodmoon_court": dict(prefix="court", metal=("#44444c", "#2a2a30"), accent=("#606068", "#a0a0a8", "#c4c4cc"),
                            wood=("#0e0806", "#22140e", "#3a241a"), glow="#ff5a60", stone=("#0e0c0e", "#2e2830"),
                            cloth=("#32060c", "#7e1422")),
    "obsidian_labyrinth": dict(prefix="maze", metal=("#442410", "#824a24"), accent=("#62361a", "#a2602e", "#c07a3c"),
                               wood=("#0e0c0c", "#221e1c", "#3a3330"), glow="#ff8a20", stone=("#0a0614", "#241a34"),
                               cloth=("#6a1004", "#b02a06")),
    "abyssal_lighthouse": dict(prefix="abyss", metal=("#34260e", "#204840"), accent=("#4c3816", "#80622c", "#a07c3a"),
                               wood=("#061412", "#102c28", "#204840"), glow="#ffc870", stone=("#0e1418", "#26323a"),
                               cloth=("#2a2416", "#4a4028")),
    "eclipse_cathedral": dict(prefix="eclipse", metal=("#2e2008", "#6a4c16"), accent=("#4a340e", "#8e6820", "#dcb44a"),
                              wood=("#08070a", "#18151a", "#2a252c"), glow="#fff0b0", stone=("#0a0a0e", "#24242e"),
                              cloth=("#1e1c1a", "#383532")),
    "wyrms_hoard": dict(prefix="hoard", metal=("#5e400a", "#b8861c"), accent=("#8a6010", "#e0ac2c", "#fcd860"),
                        wood=("#1a120c", "#2e2016", "#463222"), glow="#ff9a20", stone=("#100e10", "#302a26"),
                        cloth=("#5a1004", "#a02a06")),
}

PAL = PALETTES[GATE]
PX = PAL["prefix"]
IRON = rusty(PX + "_iron", iron=lin(PAL["metal"][0]), rust=lin(PAL["metal"][1]), amount=0.55, rough=0.5)
ACC = mottled(PX + "_accent", stops(*PAL["accent"]), 6.0, 0.4, **{"Metallic": 0.8})
WOOD = wood(PX + "_wood", stops(*PAL["wood"]), along="Z")
WOODX = wood(PX + "_wood_x", stops(*PAL["wood"]), along="X")
GLASS = glass(PX + "_glass", lin(PAL["glow"]), glow=4.0)
STONE = mottled(PX + "_stone", stops(*PAL["stone"]), 6.0, 0.8)
CLOTH = mottled(PX + "_cloth", stops(*PAL["cloth"]), 14.0, 0.9)
DARK = mat(PX + "_dark", (0.01, 0.01, 0.01), 0.9)
GLOWS.update({GLASS})
LIFT.update({PX + "_lantern": 1.0})


# ---------------------------------------------------------------- the shapes every dungeon has

def lantern():
    """a caged lantern: a base, glowing panes, four posts, a stepped roof, a ring and its chain to the ceiling"""
    bm = bmesh.new()
    c = O + Vector((0, 0, 0.1))
    box(bm, c + Vector((-0.14, -0.14, 0)), c + Vector((0.14, 0.14, 0.05)), 0, bevel=0.01)
    box(bm, c + Vector((-0.1, -0.1, 0.05)), c + Vector((0.1, 0.1, 0.33)), 1, bevel=0.005)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(bm, c + Vector((sx * 0.12 - 0.016, sy * 0.12 - 0.016, 0.05)), c + Vector((sx * 0.12 + 0.016, sy * 0.12 + 0.016, 0.34)), 2, bevel=0.004)
    for z in (0.12, 0.26):
        box(bm, c + Vector((-0.125, -0.125, z)), c + Vector((0.125, 0.125, z + 0.02)), 0)
    lathe(bm, [(0.17, 0.33), (0.17, 0.37), (0.09, 0.46), (0.035, 0.5), (0.0, 0.5)], c, 0, 4)
    tube(bm, ring(c + Vector((0, 0, 0.55)), 0.04, "Y", 12), 0.012, 0, sides=4, closed=True)
    links(bm, c + Vector((0, 0, 0.58)), O + Vector((0, 0, 1.0)), 0, w=0.05, r=0.012)
    return new_obj(PX + "_lantern", bm, [IRON, GLASS, ACC])


def chain():
    bm = bmesh.new()
    links(bm, O, O + Vector((0, 0, 1.0)), 0, w=0.075, r=0.02)
    return new_obj(PX + "_chain", bm, [IRON])


def bars_post():
    bm = bmesh.new()
    cyl(bm, O, 0.055, 1.0, 0, seg=10)
    for z in (0.0, 0.47, 0.92):
        cyl(bm, O + Vector((0, 0, z)), 0.075, 0.08, 1, seg=10)
    return new_obj(PX + "_bars_post", bm, [IRON, ACC])


def bars_side():
    bm = bmesh.new()
    for y in (-0.34, -0.17):
        cyl(bm, Vector((0.5, y, 0.0)), 0.045, 1.0, 0, seg=8)
        for z in (0.2, 0.8):
            cyl(bm, Vector((0.5, y, z)), 0.055, 0.04, 1, seg=8)
    box(bm, Vector((0.47, -0.5, 0.43)), Vector((0.53, 0.0, 0.51)), 0, bevel=0.008)
    return new_obj(PX + "_bars_side", bm, [IRON, ACC])


def coffer():
    """the loot: a banded chest on feet, a lock plate, the corners shod"""
    bm = bmesh.new()
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(bm, O + Vector((sx * 0.36 - 0.06, sy * 0.24 - 0.06, 0)), O + Vector((sx * 0.36 + 0.06, sy * 0.24 + 0.06, 0.08)), 1, bevel=0.01)
    box(bm, O + Vector((-0.43, -0.3, 0.08)), O + Vector((0.43, 0.3, 0.5)), 0, bevel=0.02)
    lid = lathe(bm, [(0.0, -0.44), (0.3, -0.44), (0.3, 0.44), (0.0, 0.44)], O + Vector((0, 0, 0.5)), 0, 12, "X")
    for rg in lid:
        for v in rg:
            if v.co.z < O.z + 0.5:
                v.co.z = O.z + 0.5
            v.co.z = O.z + 0.5 + (v.co.z - O.z - 0.5) * 0.55
    for x in (-0.3, 0.0, 0.3):
        box(bm, O + Vector((x - 0.035, -0.31, 0.08)), O + Vector((x + 0.035, 0.31, 0.51)), 1, bevel=0.005)
    box(bm, O + Vector((-0.08, 0.29, 0.3)), O + Vector((0.08, 0.33, 0.48)), 2, bevel=0.006)
    box(bm, O + Vector((-0.025, 0.32, 0.34)), O + Vector((0.025, 0.34, 0.4)), 3)
    return new_obj(PX + "_coffer", bm, [WOOD, IRON, ACC, DARK])


def hoard():
    """the boss's hoard: a great chest two blocks wide on clawed feet, its domed lid strapped in the accent metal, iron
    corners and bands studded with rivets, ring handles at the ends, a big cog lock on the front with the glow in it"""
    bm = bmesh.new()
    W, D, H = 0.94, 0.42, 0.72            # half-width, half-depth, the body's top
    for sx in (-1, 1):                     # clawed feet: a block and three toes forward
        for sy in (-1, 1):
            fx, fy = sx * (W - 0.1), sy * (D - 0.08)
            box(bm, O + Vector((fx - 0.09, fy - 0.08, 0)), O + Vector((fx + 0.09, fy + 0.08, 0.14)), 1, bevel=0.015)
            for t in (-1, 0, 1):
                box(bm, O + Vector((fx + t * 0.055 - 0.022, fy + sy * 0.06, 0)), O + Vector((fx + t * 0.055 + 0.022, fy + sy * 0.13, 0.05)), 2, bevel=0.01)
    box(bm, O + Vector((-W, -D, 0.12)), O + Vector((W, D, H)), 0, bevel=0.025)                     # the body
    for z0, z1 in ((0.12, 0.2), (H - 0.07, H + 0.01)):                                               # iron bands
        box(bm, O + Vector((-W - 0.015, -D - 0.015, z0)), O + Vector((W + 0.015, D + 0.015, z1)), 1, bevel=0.01)
    for sx in (-1, 1):                                                                               # iron corners
        for sy in (-1, 1):
            box(bm, O + Vector((sx * W - 0.07, sy * D - 0.07, 0.12)), O + Vector((sx * W + 0.07, sy * D + 0.07, H + 0.02)), 1, bevel=0.012)
            box(bm, O + Vector((sx * W - 0.085, sy * D - 0.085, H - 0.02)), O + Vector((sx * W + 0.085, sy * D + 0.085, H + 0.05)), 2, bevel=0.012)
    # the domed lid, a half drum along X
    lid = lathe(bm, [(0.0, -W), (D, -W), (D, W), (0.0, W)], O + Vector((0, 0, H)), 0, 20, "X")
    for rg in lid:
        for v in rg:
            v.co.z = O.z + H + max(0.0, v.co.z - O.z - H) * 0.9
    for x in (-W + 0.02, W - 0.04):                                                                  # its iron end rims
        rim = lathe(bm, [(0.0, 0.0), (D + 0.02, 0.0), (D + 0.02, 0.04), (0.0, 0.04)], O + Vector((x - 0.0, 0, H)), 1, 20, "X")
        for rg in rim:
            for v in rg:
                v.co.z = O.z + H + max(0.0, v.co.z - O.z - H) * 0.9
    for x in (-0.62, -0.22, 0.22, 0.62):                                                             # accent straps
        box(bm, O + Vector((x - 0.05, -D - 0.022, 0.14)), O + Vector((x + 0.05, D + 0.022, H)), 2, bevel=0.008)
        strap = lathe(bm, [(0.0, -0.05), (D + 0.025, -0.05), (D + 0.025, 0.05), (0.0, 0.05)], O + Vector((x, 0, H)), 2, 20, "X")
        for rg in strap:
            for v in rg:
                v.co.z = O.z + H + max(0.0, v.co.z - O.z - H) * 0.9
        for z in (0.26, 0.42, 0.58):
            cyl(bm, O + Vector((x, D + 0.02, z)), 0.018, 0.02, 1, seg=8, axis="Y")
    box(bm, O + Vector((-W + 0.05, -0.05, H + D * 0.9 - 0.02)), O + Vector((W - 0.05, 0.05, H + D * 0.9 + 0.05)), 2, bevel=0.015)  # ridge
    for sx in (-1, 1):                                                                               # ring handles
        x = sx * (W + 0.03)
        box(bm, O + Vector((x - 0.025, -0.08, 0.44)), O + Vector((x + 0.025, 0.08, 0.52)), 1, bevel=0.008)
        tube(bm, [O + Vector((x + sx * 0.06, 0.12 * math.cos(t), 0.42 - 0.12 * math.sin(t))) for t in [k * math.pi / 8 for k in range(9)]], 0.022, 2, sides=6)
    # the cog lock on the front: a toothed brass wheel, a dark ring, the glow at its heart, a keyhole under
    fy = D + 0.02
    cyl(bm, O + Vector((0, fy, 0.45)), 0.2, 0.05, 2, seg=24, axis="Y")
    for k in range(12):
        a = k * math.pi / 6
        cx, cz = math.cos(a) * 0.22, 0.45 + math.sin(a) * 0.22
        box(bm, O + Vector((cx - 0.035, fy, cz - 0.035)), O + Vector((cx + 0.035, fy + 0.05, cz + 0.035)), 2,
            rot=Matrix.Rotation(-a, 3, "Y"))
    cyl(bm, O + Vector((0, fy + 0.04, 0.45)), 0.12, 0.03, 3, seg=20, axis="Y")
    ellipsoid(bm, O + Vector((0, fy + 0.07, 0.45)), (0.075, 0.04, 0.075), 4, seg=12)
    box(bm, O + Vector((-0.11, fy - 0.01, 0.62)), O + Vector((0.11, fy + 0.05, H + 0.06)), 1, bevel=0.01)     # the hasp
    box(bm, O + Vector((-0.02, fy + 0.04, 0.18)), O + Vector((0.02, fy + 0.06, 0.28)), 3)                      # keyhole
    return new_obj(PX + "_hoard", bm, [WOOD, IRON, ACC, DARK, GLASS])


# ---------------------------------------------------------------- the Weeping Mine's own

def crystal_spray(bm, c, n, size, seed, mi):
    import random
    rnd = random.Random(seed)
    for k in range(n):
        a = rnd.uniform(0, 6.28)
        tilt = rnd.uniform(0.0, 0.7)
        d = Vector((math.cos(a) * math.sin(tilt), math.sin(a) * math.sin(tilt), math.cos(tilt)))
        L = size * rnd.uniform(0.5, 1.0)
        r = L * rnd.uniform(0.14, 0.22)
        base = c + Vector((math.cos(a), math.sin(a), 0)) * rnd.uniform(0, size * 0.25)
        tube(bm, [base, base + d * L * 0.8, base + d * L], lambda t: r * (1 - t) ** 0.6 + 0.004, mi, sides=6)


def crystal_cluster():
    """weeping crystal grown up from the floor, the light inside it"""
    bm = bmesh.new()
    displace([v for v in ellipsoid(bm, O + Vector((0, 0, 0.02)), (0.3, 0.26, 0.1), 1, seg=10)], 0.03, 6, 2) if False else None
    ellipsoid(bm, O + Vector((0, 0, 0.0)), (0.32, 0.28, 0.1), 1, seg=10)
    crystal_spray(bm, O + Vector((0, 0, 0.04)), 7, 0.85, 3, 0)
    return new_obj("weeping_cluster", bm, [GLASS, STONE])


def minecart():
    """a mine cart heaped with ore and crystal, on its wheels"""
    bm = bmesh.new()
    box(bm, O + Vector((-0.4, -0.3, 0.12)), O + Vector((0.4, 0.3, 0.62)), 0, bevel=0.02)
    for y in (-0.31, 0.31):
        box(bm, O + Vector((-0.42, y - 0.02, 0.56)), O + Vector((0.42, y + 0.02, 0.64)), 1, bevel=0.005)
    for sx in (-0.26, 0.26):
        for sy in (-0.32, 0.32):
            cyl(bm, O + Vector((sx, sy, 0.12)), 0.11, 0.04, 0, seg=12, axis="Y")
    box(bm, O + Vector((-0.36, -0.26, 0.5)), O + Vector((0.36, 0.26, 0.66)), 2, bevel=0.02)
    for k, (x, y) in enumerate(((-0.2, -0.1), (0.15, 0.1), (0.05, -0.12))):
        ellipsoid(bm, O + Vector((x, y, 0.68)), (0.12, 0.1, 0.08), 2, seg=8)
    crystal_spray(bm, O + Vector((0.1, 0.05, 0.66)), 4, 0.35, 9, 3)
    return new_obj("minecart", bm, [IRON, ACC, STONE, GLASS])


def mine_rail():
    """a length of track: two rails on sleepers, laid along the block (north-south)"""
    bm = bmesh.new()
    for k in range(3):
        y = -0.5 + 0.17 + k * 0.33
        box(bm, Vector((0.12, y - 0.06, 0.0)), Vector((0.88, y + 0.06, 0.05)), 1, bevel=0.01)
    for x in (0.3, 0.7):
        box(bm, Vector((x - 0.025, -1.0, 0.05)), Vector((x + 0.025, 0.0, 0.11)), 0, bevel=0.005)
    return new_obj("mine_rail", bm, [IRON, WOODX])


def ore_sacks():
    """sacks of ore heaped on a pallet, a pick leant against them"""
    bm = bmesh.new()
    box(bm, O + Vector((-0.42, -0.35, 0)), O + Vector((0.42, 0.35, 0.06)), 0, bevel=0.01)
    for (x, y, s) in ((-0.2, -0.1, 1.0), (0.18, -0.08, 0.9), (0.0, 0.16, 0.95), (-0.02, -0.02, 0.8)):
        ellipsoid(bm, O + Vector((x, y, 0.06 + 0.17 * s + (0.18 if s == 0.8 else 0))), (0.19 * s, 0.17 * s, 0.17 * s), 1, seg=10)
    tube(bm, [O + Vector((0.36, 0.2, 0.05)), O + Vector((0.3, 0.26, 0.7))], 0.018, 0, sides=6)
    box(bm, O + Vector((0.18, 0.2, 0.66)), O + Vector((0.44, 0.32, 0.72)), 2, bevel=0.01)
    return new_obj("ore_sacks", bm, [WOOD, CLOTH, IRON])


# ---------------------------------------------------------------- the Tide Chapel's own

def drowned_pew():
    """a church pew swollen with the sea: a seat, a high back to the north, carved ends, barnacles on its feet"""
    bm = bmesh.new()
    box(bm, Vector((0.02, -0.82, 0.36)), Vector((0.98, -0.22, 0.42)), 0, bevel=0.01)
    box(bm, Vector((0.02, -0.88, 0.42)), Vector((0.98, -0.8, 0.98)), 0, bevel=0.01)
    for x in (0.02, 0.9):
        box(bm, Vector((x, -0.88, 0.0)), Vector((x + 0.08, -0.18, 0.62)), 0, bevel=0.015)
        ellipsoid(bm, Vector((x + 0.04, -0.2, 0.62)), (0.05, 0.05, 0.05), 0, seg=8)
    for (x, y) in ((0.1, -0.3), (0.86, -0.75), (0.5, -0.86), (0.2, -0.84)):
        ellipsoid(bm, Vector((x, y, 0.05)), (0.05, 0.05, 0.04), 1, seg=6)
    return new_obj("drowned_pew", bm, [WOOD, STONE])


def kelp_strand():
    """kelp risen from the flooded floor, three fronds waving"""
    bm = bmesh.new()
    for k, (x, y, h, ph) in enumerate(((0.0, 0.0, 1.0, 0.0), (0.12, 0.08, 0.8, 1.7), (-0.1, -0.06, 0.65, 3.1))):
        pts = [O + Vector((x + 0.07 * math.sin(ph + t * 6), y + 0.05 * math.cos(ph + t * 5), t * h)) for t in (i / 10 for i in range(11))]
        tube(bm, pts, lambda t: 0.035 * (1 - t * 0.7), 0, sides=5)
        for j in range(3, 10, 2):
            p = pts[j]
            box(bm, p + Vector((-0.06, -0.008, 0)), p + Vector((0.06, 0.008, 0.08)), 0)
    return new_obj("kelp_strand", bm, [CLOTH])


def clam_heap():
    """a heap of opened clams and shells, a pearl or two still glowing in them"""
    import random
    rnd = random.Random(7)
    bm = bmesh.new()
    ellipsoid(bm, O + Vector((0, 0, 0.02)), (0.38, 0.34, 0.12), 1, seg=10)
    for k in range(9):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.05, 0.3)
        c = O + Vector((math.cos(a) * r, math.sin(a) * r, 0.1 + rnd.uniform(0, 0.12)))
        ellipsoid(bm, c, (0.1, 0.08, 0.03), 0, rot=(Matrix.Rotation(a, 3, "Z") @ Matrix.Rotation(rnd.uniform(-0.6, 0.6), 3, "X")), seg=8)
        if k % 3 == 0:
            ellipsoid(bm, c + Vector((0, 0, 0.04)), (0.03, 0.03, 0.03), 2, seg=6)
    return new_obj("clam_heap", bm, [STONE, ACC, GLASS])


def chapel_font():
    """the chapel's font, the sea standing in it and glowing"""
    bm = bmesh.new()
    lathe(bm, [(0.2, 0.0), (0.24, 0.04), (0.12, 0.14), (0.1, 0.5), (0.18, 0.56), (0.36, 0.7), (0.38, 0.84), (0.3, 0.86)], O, 0, 16)
    cyl(bm, O + Vector((0, 0, 0.78)), 0.3, 0.02, 1, seg=16)
    for k in range(5):
        a = k * 1.25
        ellipsoid(bm, O + Vector((math.cos(a) * 0.36, math.sin(a) * 0.36, 0.72)), (0.04, 0.04, 0.03), 2, seg=6)
    return new_obj("chapel_font", bm, [STONE, GLASS, ACC])


# ---------------------------------------------------------------- the Brigand's Gorge's own

def loot_pile():
    """stolen coin heaped up, a goblet and a crown dropped on it"""
    import random
    rnd = random.Random(11)
    bm = bmesh.new()
    ellipsoid(bm, O + Vector((0, 0, 0.0)), (0.4, 0.36, 0.2), 0, seg=12)
    for k in range(14):
        a, r = rnd.uniform(0, 6.28), rnd.uniform(0.05, 0.38)
        cyl(bm, O + Vector((math.cos(a) * r, math.sin(a) * r, 0.12 + 0.1 * (1 - r / 0.4))), 0.05, 0.012, 0, seg=10)
    lathe(bm, [(0.05, 0.0), (0.02, 0.04), (0.02, 0.14), (0.07, 0.2), (0.07, 0.26)], O + Vector((0.18, -0.1, 0.16)), 0, 10)
    tube(bm, ring(O + Vector((-0.14, 0.12, 0.24)), 0.09, "Z", 12), 0.02, 0, sides=5, closed=True)
    for k in range(5):
        a = k * 1.256
        cyl(bm, O + Vector((-0.14 + math.cos(a) * 0.09, 0.12 + math.sin(a) * 0.09, 0.24)), 0.012, 0.06, 0, seg=5)
    ellipsoid(bm, O + Vector((-0.14, 0.03, 0.27)), (0.025, 0.025, 0.025), 1, seg=6)
    return new_obj("loot_pile", bm, [ACC, GLASS])


def gorge_campfire():
    """a bandits' fire: a ring of red stones, logs crossed, the coals glowing"""
    import random
    rnd = random.Random(5)
    bm = bmesh.new()
    for k in range(9):
        a = k * 6.28 / 9
        ellipsoid(bm, O + Vector((math.cos(a) * 0.36, math.sin(a) * 0.36, 0.05)), (0.09, 0.08, 0.07), 2, seg=7)
    for a in (0.3, 1.9, 3.3):
        d = Vector((math.cos(a), math.sin(a), 0))
        tube(bm, [O - d * 0.28 + Vector((0, 0, 0.05)), O + d * 0.28 + Vector((0, 0, 0.12))], 0.05, 0, sides=6)
    ellipsoid(bm, O + Vector((0, 0, 0.04)), (0.2, 0.2, 0.05), 1, seg=8)
    for k in range(4):
        a = k * 1.6
        tube(bm, [O + Vector((math.cos(a) * 0.08, math.sin(a) * 0.08, 0.06)), O + Vector((math.cos(a) * 0.03, math.sin(a) * 0.03, 0.34))],
             lambda t: 0.06 * (1 - t) + 0.005, 1, sides=5)
    return new_obj("gorge_campfire", bm, [WOOD, GLASS, STONE])


def gorge_weapon_rack():
    """a rack against the wall: two posts, two rails, spears and a sword leant in it"""
    bm = bmesh.new()
    for x in (0.08, 0.92):
        box(bm, Vector((x - 0.04, -0.62, 0.0)), Vector((x + 0.04, -0.54, 1.0)), 0, bevel=0.01)
    for z in (0.3, 0.8):
        box(bm, Vector((0.04, -0.62, z)), Vector((0.96, -0.54, z + 0.06)), 0, bevel=0.01)
    for k, x in enumerate((0.25, 0.42, 0.6, 0.78)):
        tube(bm, [Vector((x, -0.48, 0.0)), Vector((x + 0.02, -0.6, 0.98))], 0.016, 0, sides=5)
        tube(bm, [Vector((x + 0.02, -0.6, 0.98)), Vector((x + 0.025, -0.62, 1.12))], lambda t: 0.035 * (1 - t) + 0.004, 1, sides=4)
    return new_obj("gorge_weapon_rack", bm, [WOOD, IRON])


def bandit_tent():
    """a lean-to of red cloth on two poles, its back to the north, a bedroll under it"""
    bm = bmesh.new()
    for x in (0.08, 0.92):
        tube(bm, [Vector((x, -0.1, 0.0)), Vector((x, -0.1, 0.86))], 0.025, 0, sides=6)
    nu, nv = 10, 8
    rows = []
    for j in range(nv + 1):
        row = []
        for i in range(nu + 1):
            u, v = i / nu, j / nv
            row.append(bm.verts.new(Vector((0.04 + 0.92 * u, -0.1 - 0.82 * v, 0.88 - 0.84 * v + 0.03 * math.sin(u * 9) * v))))
        rows.append(row)
    for j in range(nv):
        for i in range(nu):
            bm.faces.new((rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i])).material_index = 1
    box(bm, Vector((0.2, -0.75, 0.0)), Vector((0.8, -0.3, 0.08)), 2, bevel=0.03)
    return new_obj("bandit_tent", bm, [WOOD, CLOTH, CLOTH])


# ---------------------------------------------------------------- the Rookery's own

def crow_nest():
    """a crow's nest on the floor: a ring of sticks, black feathers in it, a bone or two"""
    import random
    rnd = random.Random(3)
    bm = bmesh.new()
    for k in range(26):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.22, 0.38)
        c = O + Vector((math.cos(a) * r, math.sin(a) * r, rnd.uniform(0.03, 0.2)))
        d = Vector((-math.sin(a), math.cos(a), rnd.uniform(-0.2, 0.2))) * rnd.uniform(0.12, 0.22)
        tube(bm, [c - d, c + d], 0.014, 1, sides=4)
    ellipsoid(bm, O + Vector((0, 0, 0.04)), (0.26, 0.26, 0.05), 1, seg=10)
    for k in range(5):
        a = rnd.uniform(0, 6.28)
        c = O + Vector((math.cos(a) * 0.12, math.sin(a) * 0.12, 0.1))
        box(bm, c + Vector((-0.06, -0.01, 0)), c + Vector((0.06, 0.01, 0.02)), 2)
    tube(bm, [O + Vector((-0.1, 0.05, 0.1)), O + Vector((0.12, -0.04, 0.12))], 0.018, 0, sides=5)
    return new_obj("crow_nest", bm, [ACC, WOOD, DARK])


def crow_perch():
    """a T-perch of black wood, talon-scored, a skull tied on it"""
    bm = bmesh.new()
    box(bm, O + Vector((-0.18, -0.18, 0)), O + Vector((0.18, 0.18, 0.06)), 1, bevel=0.01)
    cyl(bm, O, 0.04, 0.95, 0, seg=8)
    cyl(bm, O + Vector((-0.38, 0, 0.88)), 0.035, 0.76, 0, seg=8, axis="X")
    ellipsoid(bm, O + Vector((0, 0.06, 0.6)), (0.08, 0.07, 0.08), 2, seg=8)
    return new_obj("crow_perch", bm, [WOOD, STONE, ACC])


def bone_chimes():
    """bones and a crow skull strung from a ring, hung from the ceiling"""
    bm = bmesh.new()
    tube(bm, ring(O + Vector((0, 0, 0.8)), 0.16, "Z", 14), 0.014, 1, sides=4, closed=True)
    for k in range(6):
        a = k * 1.047
        c = O + Vector((math.cos(a) * 0.16, math.sin(a) * 0.16, 0.8))
        L = 0.25 + 0.1 * (k % 3)
        tube(bm, [c, c - Vector((0, 0, L))], 0.004, 1, sides=3)
        cyl(bm, c - Vector((0, 0, L + 0.14)), 0.02, 0.14, 0, seg=6)
    tube(bm, [O + Vector((0, 0, 0.8)), O + Vector((0, 0, 1.0))], 0.01, 1, sides=4)
    return new_obj("bone_chimes", bm, [ACC, IRON])


def omen_altar():
    """a black stone altar, an eye of omen glowing in its bowl"""
    bm = bmesh.new()
    lathe(bm, [(0.34, 0.0), (0.36, 0.08), (0.22, 0.16), (0.18, 0.6), (0.3, 0.7), (0.36, 0.84), (0.3, 0.86)], O, 0, 8)
    ellipsoid(bm, O + Vector((0, 0, 0.84)), (0.16, 0.16, 0.08), 1, seg=10)
    for k in range(6):
        a = k * 1.047
        box(bm, O + Vector((math.cos(a) * 0.32 - 0.02, math.sin(a) * 0.32 - 0.02, 0.84)), O + Vector((math.cos(a) * 0.32 + 0.02, math.sin(a) * 0.32 + 0.02, 0.98)), 2)
    return new_obj("omen_altar", bm, [STONE, GLASS, ACC])


# ---------------------------------------------------------------- the Hollow Circus's own

CREAM_C = mottled("circus_cream", stops("#857258", "#bca882", "#d6c49c"), 10.0, 0.8)


def circus_drum():
    """a performer's drum-pedestal: red sides, gilt rims, a star on top"""
    bm = bmesh.new()
    cyl(bm, O, 0.4, 0.68, 4, seg=24)
    for z in (0.0, 0.62):
        cyl(bm, O + Vector((0, 0, z)), 0.42, 0.06, 1, seg=24)
    cyl(bm, O + Vector((0, 0, 0.68)), 0.36, 0.02, 2, seg=24)
    for k in range(5):
        a = k * 1.2566
        box(bm, O + Vector((math.cos(a) * 0.16 - 0.03, math.sin(a) * 0.16 - 0.03, 0.7)), O + Vector((math.cos(a) * 0.16 + 0.03, math.sin(a) * 0.16 + 0.03, 0.72)), 1)
    return new_obj("circus_drum", bm, [WOOD, ACC, CREAM_C, IRON, CLOTH])


def circus_cage():
    """a menagerie cage on wheels: gilt bars, a red roof, something's bones inside"""
    bm = bmesh.new()
    box(bm, O + Vector((-0.48, -0.4, 0.08)), O + Vector((0.48, 0.4, 0.16)), 0, bevel=0.01)
    box(bm, O + Vector((-0.5, -0.42, 0.9)), O + Vector((0.5, 0.42, 1.0)), 2, bevel=0.01)
    for k in range(9):
        x = -0.44 + k * 0.11
        for y in (-0.38, 0.38):
            cyl(bm, O + Vector((x, y, 0.16)), 0.014, 0.74, 1, seg=6)
    for y in (-0.27, -0.16, -0.05, 0.06, 0.17, 0.28):
        for x in (-0.44, 0.44):
            cyl(bm, O + Vector((x, y, 0.16)), 0.014, 0.74, 1, seg=6)
    for sx in (-0.36, 0.36):
        cyl(bm, O + Vector((sx, -0.42, 0.08)), 0.08, 0.04, 0, seg=12, axis="Y")
        cyl(bm, O + Vector((sx, 0.38, 0.08)), 0.08, 0.04, 0, seg=12, axis="Y")
    ellipsoid(bm, O + Vector((0.1, 0.05, 0.22)), (0.12, 0.08, 0.06), 3, seg=8)
    return new_obj("circus_cage", bm, [WOOD, ACC, CLOTH, CREAM_C])


def circus_tent():
    """a striped sideshow booth: a peaked roof of red and cream on four poles, a curtain hung at the back"""
    bm = bmesh.new()
    for sx in (0.08, 0.92):
        for sy in (-0.08, -0.92):
            tube(bm, [Vector((sx, sy, 0.0)), Vector((sx, sy, 0.7))], 0.025, 0, sides=6)
    n = 8
    for k in range(n):
        x0, x1 = 0.04 + 0.92 * k / n, 0.04 + 0.92 * (k + 1) / n
        verts = [bm.verts.new(Vector((x0, -0.04, 0.7))), bm.verts.new(Vector((x1, -0.04, 0.7))),
                 bm.verts.new(Vector((x1, -0.5, 0.92))), bm.verts.new(Vector((x0, -0.5, 0.92)))]
        bm.faces.new(verts).material_index = 1 + k % 2
        verts = [bm.verts.new(Vector((x0, -0.5, 0.92))), bm.verts.new(Vector((x1, -0.5, 0.92))),
                 bm.verts.new(Vector((x1, -0.96, 0.7))), bm.verts.new(Vector((x0, -0.96, 0.7)))]
        bm.faces.new(verts).material_index = 1 + k % 2
    box(bm, Vector((0.06, -0.94, 0.0)), Vector((0.94, -0.9, 0.7)), 1)
    ellipsoid(bm, Vector((0.5, -0.5, 0.95)), (0.04, 0.04, 0.05), 3, seg=8)
    return new_obj("circus_tent", bm, [WOOD, CLOTH, CREAM_C, ACC])


def juggling_clubs():
    """juggling clubs dropped where the juggler fell"""
    bm = bmesh.new()
    for k, (x, y, a) in enumerate(((-0.2, -0.1, 0.4), (0.15, 0.12, 2.1), (0.05, -0.2, 3.6))):
        d = Vector((math.cos(a), math.sin(a), 0))
        lathe(bm, [(0.0, -0.18), (0.03, -0.18), (0.05, -0.04), (0.06, 0.08), (0.03, 0.16), (0.0, 0.18)],
              O + Vector((x, y, 0.06)), 1 + k % 2, 10, "X")
    return new_obj("juggling_clubs", bm, [WOOD, CLOTH, CREAM_C])


# ---------------------------------------------------------------- the Mirefen Coven's own

def coven_cauldron():
    """a black iron cauldron on three legs over a peat fire, the brew glowing green"""
    bm = bmesh.new()
    lathe(bm, [(0.0, 0.12), (0.2, 0.13), (0.34, 0.24), (0.38, 0.42), (0.34, 0.6), (0.36, 0.64), (0.3, 0.64)], O, 0, 20)
    cyl(bm, O + Vector((0, 0, 0.56)), 0.31, 0.03, 1, seg=20)
    for k in range(3):
        a = k * 2.094
        tube(bm, [O + Vector((math.cos(a) * 0.22, math.sin(a) * 0.22, 0.18)), O + Vector((math.cos(a) * 0.3, math.sin(a) * 0.3, 0.0))], 0.03, 0, sides=5)
    for k in range(3):
        a = k * 2.094 + 0.5
        ellipsoid(bm, O + Vector((math.cos(a) * 0.1, math.sin(a) * 0.1, 0.62)), (0.04, 0.04, 0.04), 1, seg=6)
    ellipsoid(bm, O + Vector((0, 0, 0.04)), (0.2, 0.2, 0.04), 3, seg=8)
    return new_obj("coven_cauldron", bm, [IRON, GLASS, ACC, WOOD])


def hag_effigy():
    """a twig effigy: a stick figure bound in moss-rope, antlers for a head, a rag skirt"""
    bm = bmesh.new()
    tube(bm, [O, O + Vector((0, 0, 0.9))], 0.025, 0, sides=5)
    tube(bm, [O + Vector((-0.3, 0, 0.62)), O + Vector((0.3, 0, 0.66))], 0.02, 0, sides=5)
    for s in (-1, 1):
        tube(bm, [O + Vector((0, 0, 0.88)), O + Vector((s * 0.16, 0, 1.0)), O + Vector((s * 0.22, 0, 1.08))], 0.012, 1, sides=4)
    lathe(bm, [(0.0, 0.34), (0.12, 0.36), (0.2, 0.18), (0.22, 0.1), (0.0, 0.1)], O, 2, 8)
    ellipsoid(bm, O + Vector((0, 0, 0.8)), (0.07, 0.06, 0.08), 1, seg=8)
    return new_obj("hag_effigy", bm, [WOOD, ACC, CLOTH])


def fen_toadstools():
    """a ring of red-capped toadstools, their gills faintly glowing"""
    import random
    rnd = random.Random(9)
    bm = bmesh.new()
    for k in range(6):
        a, r = rnd.uniform(0, 6.28), rnd.uniform(0.0, 0.3)
        c = O + Vector((math.cos(a) * r, math.sin(a) * r, 0))
        h = rnd.uniform(0.15, 0.5)
        cyl(bm, c, 0.03 + h * 0.06, h, 0, seg=8)
        ellipsoid(bm, c + Vector((0, 0, h)), (0.1 + h * 0.2, 0.1 + h * 0.2, 0.05 + h * 0.08), 1, seg=10)
        cyl(bm, c + Vector((0, 0, h - 0.02)), 0.08 + h * 0.18, 0.02, 2, seg=10)
    return new_obj("fen_toadstools", bm, [ACC, CLOTH_RED, GLASS])


def fen_reeds():
    """reeds and bulrushes up out of the mud"""
    import random
    rnd = random.Random(4)
    bm = bmesh.new()
    for k in range(12):
        a, r = rnd.uniform(0, 6.28), rnd.uniform(0.0, 0.3)
        c = O + Vector((math.cos(a) * r, math.sin(a) * r, 0))
        h = rnd.uniform(0.55, 1.0)
        lean = Vector((rnd.uniform(-0.1, 0.1), rnd.uniform(-0.1, 0.1), 0))
        tube(bm, [c, c + lean * 0.5 + Vector((0, 0, h * 0.5)), c + lean + Vector((0, 0, h))], lambda t: 0.012 * (1 - t) + 0.003, 0, sides=4)
        if k % 3 == 0:
            cyl(bm, c + lean * 0.85 + Vector((0, 0, h * 0.78)), 0.022, 0.12, 1, seg=6)
    return new_obj("fen_reeds", bm, [CLOTH, WOOD])


# ---------------------------------------------------------------- the Sandsunk Tomb's own

def canopic_jars():
    """four canopic jars on a step, each lid a head - jackal, hawk, ape, man - in gold"""
    bm = bmesh.new()
    box(bm, Vector((0.12, -0.88, 0.0)), Vector((0.88, -0.12, 0.06)), 0, bevel=0.01)
    for k, (x, y) in enumerate(((0.3, -0.3), (0.7, -0.3), (0.3, -0.7), (0.7, -0.7))):
        c = Vector((x, y, 0.06))
        lathe(bm, [(0.0, 0.0), (0.08, 0.0), (0.12, 0.08), (0.13, 0.22), (0.1, 0.36), (0.07, 0.38)], c, 0, 14)
        ellipsoid(bm, c + Vector((0, 0, 0.44)), (0.08, 0.08, 0.08), 1, seg=10)
        if k == 0:
            for s in (-1, 1):
                tube(bm, [c + Vector((s * 0.04, 0, 0.48)), c + Vector((s * 0.05, 0, 0.6))], 0.018, 1, sides=4)
        if k == 1:
            tube(bm, [c + Vector((0, 0.06, 0.44)), c + Vector((0, 0.13, 0.41))], 0.025, 1, sides=4)
        cyl(bm, c + Vector((0, 0, 0.24)), 0.135, 0.03, 2, seg=14)
    return new_obj("canopic_jars", bm, [STONE, ACC, CLOTH])


def sarcophagus():
    """a stone sarcophagus, its lid carved with the sleeper: gold mask, crossed arms, a lapis collar"""
    bm = bmesh.new()
    box(bm, Vector((0.04, -0.94, 0.0)), Vector((0.96, -0.06, 0.5)), 0, bevel=0.03)
    box(bm, Vector((0.06, -0.92, 0.5)), Vector((0.94, -0.08, 0.6)), 0, bevel=0.03)
    ellipsoid(bm, Vector((0.5, -0.24, 0.66)), (0.16, 0.14, 0.1), 1, seg=12)
    box(bm, Vector((0.36, -0.42, 0.6)), Vector((0.64, -0.36, 0.68)), 2, bevel=0.01)
    for s in (-1, 1):
        tube(bm, [Vector((0.5 + s * 0.16, -0.5, 0.64)), Vector((0.5 - s * 0.1, -0.62, 0.66))], 0.04, 1, sides=6)
    for x in (0.04, 0.96):
        for y in (-0.3, -0.5, -0.7):
            box(bm, Vector((x - 0.01, y - 0.06, 0.12)), Vector((x + 0.01, y + 0.06, 0.38)), 2)
    return new_obj("sarcophagus", bm, [STONE, ACC, CLOTH])


def sun_brazier():
    """a tall gold brazier on three lion legs, the sun-fire burning in the bowl"""
    bm = bmesh.new()
    for k in range(3):
        a = k * 2.094
        tube(bm, [O + Vector((math.cos(a) * 0.26, math.sin(a) * 0.26, 0.0)), O + Vector((math.cos(a) * 0.1, math.sin(a) * 0.1, 0.5))], 0.035, 0, sides=6)
        ellipsoid(bm, O + Vector((math.cos(a) * 0.27, math.sin(a) * 0.27, 0.03)), (0.05, 0.05, 0.03), 0, seg=6)
    cyl(bm, O + Vector((0, 0, 0.45)), 0.06, 0.25, 0, seg=10)
    lathe(bm, [(0.06, 0.68), (0.2, 0.72), (0.3, 0.84), (0.32, 0.9), (0.28, 0.9)], O, 0, 18)
    ellipsoid(bm, O + Vector((0, 0, 0.9)), (0.24, 0.24, 0.08), 1, seg=12)
    for k in range(5):
        a = k * 1.256
        tube(bm, [O + Vector((math.cos(a) * 0.1, math.sin(a) * 0.1, 0.92)), O + Vector((math.cos(a) * 0.04, math.sin(a) * 0.04, 1.0))], 0.04, 1, sides=4)
    return new_obj("sun_brazier", bm, [ACC, GLASS])


def jackal_statue():
    """a black jackal on a plinth, sitting up, ears tall, a gold collar"""
    bm = bmesh.new()
    box(bm, Vector((0.2, -0.8, 0.0)), Vector((0.8, -0.2, 0.18)), 2, bevel=0.02)
    ellipsoid(bm, Vector((0.5, -0.56, 0.34)), (0.14, 0.2, 0.16), 0, seg=12)
    ellipsoid(bm, Vector((0.5, -0.42, 0.52)), (0.1, 0.1, 0.18), 0, seg=10)
    ellipsoid(bm, Vector((0.5, -0.3, 0.74)), (0.08, 0.1, 0.08), 0, seg=10)
    tube(bm, [Vector((0.5, -0.24, 0.74)), Vector((0.5, -0.04, 0.69))], lambda t: 0.045 * (1 - t * 0.5), 0, sides=6)
    for s in (-1, 1):
        tube(bm, [Vector((0.5 + s * 0.04, -0.32, 0.8)), Vector((0.5 + s * 0.07, -0.33, 0.9))], lambda t: 0.035 * (1 - t * 0.8), 0, sides=4)
        tube(bm, [Vector((0.5 + s * 0.08, -0.36, 0.2)), Vector((0.5 + s * 0.08, -0.3, 0.46))], 0.03, 0, sides=5)
    tube(bm, ring(Vector((0.5, -0.4, 0.62)), 0.1, "Z", 12), 0.02, 1, sides=4, closed=True)
    return new_obj("jackal_statue", bm, [DARK, ACC, STONE])


# ---------------------------------------------------------------- the Fallen Titan's own

def breathing_sac():
    """a lung-sac swelling out of the floor, veined, a bile light inside it"""
    bm = bmesh.new()
    ellipsoid(bm, O + Vector((0, 0, 0.36)), (0.4, 0.36, 0.38), 0, seg=16)
    for k in range(6):
        a = k * 1.05
        tube(bm, [O + Vector((math.cos(a) * 0.1, math.sin(a) * 0.1, 0.72)), O + Vector((math.cos(a) * 0.36, math.sin(a) * 0.34, 0.5)),
                  O + Vector((math.cos(a) * 0.4, math.sin(a) * 0.38, 0.2))], 0.018, 1, sides=4)
    ellipsoid(bm, O + Vector((0.12, -0.1, 0.42)), (0.12, 0.12, 0.12), 2, seg=8)
    return new_obj("breathing_sac", bm, [CLOTH, STONE, GLASS])


def rib_spur():
    """bone spurs of the titan's ribs breaking up through the flesh"""
    bm = bmesh.new()
    for k, (x, y, h, lean) in enumerate(((0.0, 0.0, 0.95, 0.15), (0.2, 0.12, 0.6, -0.2), (-0.18, 0.1, 0.5, 0.25), (0.1, -0.2, 0.4, 0.1))):
        b = O + Vector((x, y, 0))
        tube(bm, [b, b + Vector((lean * 0.5, 0, h * 0.6)), b + Vector((lean, 0.05, h))], lambda t: 0.08 * (1 - t * 0.85), 0, sides=7)
    ellipsoid(bm, O + Vector((0, 0, 0.02)), (0.34, 0.3, 0.06), 1, seg=10)
    return new_obj("rib_spur", bm, [mottled("titan_ivory", stops("#6a6250", "#aaa286", "#e2dcc4"), 8.0, 0.6), STONE])


def eaten_armour():
    """the armour of an eaten army, corroded in a heap: a helm, a breastplate, a shield, a sword"""
    bm = bmesh.new()
    ellipsoid(bm, O + Vector((0, 0, 0.0)), (0.44, 0.4, 0.12), 1, seg=12)
    lathe(bm, [(0.0, 0.32), (0.12, 0.3), (0.15, 0.2), (0.15, 0.08), (0.0, 0.08)], O + Vector((-0.18, 0.1, 0)), 0, 12)
    box(bm, Vector((0.44, -0.62, 0.06)), Vector((0.78, -0.36, 0.16)), 0, bevel=0.03)
    cyl(bm, O + Vector((0.12, 0.18, 0.08)), 0.2, 0.04, 0, seg=16, axis="Z")
    box(bm, Vector((0.1, -0.9, 0.1)), Vector((0.9, -0.84, 0.13)), 0)
    return new_obj("eaten_armour", bm, [IRON, STONE])


def artery_root():
    """an artery rooted in the floor, thick as a leg, climbing up out of sight and pulsing"""
    bm = bmesh.new()
    for k in range(3):
        a = k * 2.094 + 0.4
        tube(bm, [O + Vector((math.cos(a) * 0.36, math.sin(a) * 0.36, 0.0)), O + Vector((math.cos(a) * 0.12, math.sin(a) * 0.12, 0.3)),
                  O + Vector((0, 0, 0.5))], lambda t: 0.08 * (1 - t * 0.4), 0, sides=7)
    tube(bm, [O + Vector((0, 0, 0.45)), O + Vector((0.06, 0.04, 0.75)), O + Vector((0, 0, 1.0))], 0.11, 0, sides=8)
    for z in (0.55, 0.8):
        cyl(bm, O + Vector((0.02, 0.02, z)), 0.125, 0.03, 1, seg=10)
    return new_obj("artery_root", bm, [STONE, GLASS])


# ---------------------------------------------------------------- the Jade Monastery's own

def incense_burner():
    """a bronze incense burner on three legs, a pierced lid, the smoke a jade glow"""
    bm = bmesh.new()
    lathe(bm, [(0.0, 0.16), (0.24, 0.18), (0.34, 0.3), (0.36, 0.46), (0.3, 0.56), (0.0, 0.56)], O, 0, 20)
    for k in range(3):
        a = k * 2.094
        tube(bm, [O + Vector((math.cos(a) * 0.2, math.sin(a) * 0.2, 0.2)), O + Vector((math.cos(a) * 0.3, math.sin(a) * 0.3, 0.0))], 0.04, 0, sides=6)
    lathe(bm, [(0.0, 0.56), (0.26, 0.58), (0.18, 0.7), (0.06, 0.78), (0.04, 0.86), (0.0, 0.88)], O, 1, 16)
    for k in range(2):
        a = k * 3.14
        tube(bm, ring(O + Vector((math.cos(a) * 0.38, math.sin(a) * 0.38, 0.48)), 0.07, "X" if k else "X", 10), 0.02, 1, sides=4, closed=True)
    ellipsoid(bm, O + Vector((0, 0, 0.98)), (0.08, 0.08, 0.12), 2, seg=8)
    return new_obj("incense_burner", bm, [IRON, ACC, GLASS])


def prayer_wheel():
    """a prayer wheel on a post: a gold drum with the sutra round it, a red cap"""
    bm = bmesh.new()
    cyl(bm, O, 0.04, 0.95, 0, seg=8)
    cyl(bm, O + Vector((0, 0, 0.36)), 0.2, 0.42, 1, seg=20)
    for z in (0.44, 0.56, 0.68):
        cyl(bm, O + Vector((0, 0, z)), 0.205, 0.03, 2, seg=20)
    lathe(bm, [(0.0, 0.78), (0.22, 0.78), (0.14, 0.86), (0.0, 0.92)], O, 3, 16)
    cyl(bm, O, 0.14, 0.06, 0, seg=12)
    return new_obj("prayer_wheel", bm, [WOOD, ACC, GLASS, mottled("jade_red", stops("#460a08", "#821c12", "#9e2a1a"), 8.0, 0.5)])


def stone_lantern():
    """a granite temple lantern: a foot, a post, the light box with its windows, a curved roof, a bead on top"""
    bm = bmesh.new()
    cyl(bm, O, 0.24, 0.08, 0, seg=8)
    cyl(bm, O + Vector((0, 0, 0.08)), 0.08, 0.36, 0, seg=8)
    box(bm, O + Vector((-0.2, -0.2, 0.44)), O + Vector((0.2, 0.2, 0.48)), 0, bevel=0.01)
    box(bm, O + Vector((-0.15, -0.15, 0.48)), O + Vector((0.15, 0.15, 0.7)), 1)
    for s in (-1, 1):
        box(bm, O + Vector((-0.17, s * 0.15 - 0.02, 0.48)), O + Vector((-0.11, s * 0.15 + 0.02, 0.7)), 0)
        box(bm, O + Vector((0.11, s * 0.15 - 0.02, 0.48)), O + Vector((0.17, s * 0.15 + 0.02, 0.7)), 0)
    lathe(bm, [(0.0, 0.7), (0.32, 0.7), (0.3, 0.76), (0.12, 0.86), (0.0, 0.88)], O, 0, 8)
    ellipsoid(bm, O + Vector((0, 0, 0.92)), (0.05, 0.05, 0.06), 0, seg=8)
    return new_obj("stone_lantern", bm, [STONE, GLASS])


def temple_bell():
    """a bronze temple bell gone green, hung in a lacquered frame, the striker log beside it"""
    bm = bmesh.new()
    for s in (-1, 1):
        box(bm, O + Vector((s * 0.4 - 0.04, -0.04, 0.0)), O + Vector((s * 0.4 + 0.04, 0.04, 1.0)), 0)
    box(bm, O + Vector((-0.46, -0.05, 0.94)), O + Vector((0.46, 0.05, 1.0)), 0)
    lathe(bm, [(0.0, 0.88), (0.12, 0.88), (0.2, 0.8), (0.22, 0.4), (0.25, 0.3), (0.0, 0.3)], O, 1, 20)
    for z in (0.5, 0.7):
        cyl(bm, O + Vector((0, 0, z)), 0.225, 0.02, 2, seg=20)
    tube(bm, [O + Vector((-0.34, 0.16, 0.5)), O + Vector((0.34, 0.16, 0.5))], 0.04, 0, sides=6)
    return new_obj("temple_bell", bm, [WOOD, CLOTH, ACC])


# ---------------------------------------------------------------- the Storm Bastion's own

def lightning_rod():
    """a copper lightning rod on a stone foot, three prongs at the top, a glass bead where the bolt lands"""
    bm = bmesh.new()
    cyl(bm, O, 0.16, 0.12, 1, seg=8)
    cyl(bm, O + Vector((0, 0, 0.12)), 0.025, 0.86, 0, seg=8)
    for z in (0.3, 0.55):
        cyl(bm, O + Vector((0, 0, z)), 0.05, 0.03, 0, seg=8)
    for k in range(3):
        a = k * 2.094
        tube(bm, [O + Vector((0, 0, 0.9)), O + Vector((math.cos(a) * 0.08, math.sin(a) * 0.08, 0.98))], 0.012, 0, sides=4)
    ellipsoid(bm, O + Vector((0, 0, 0.92)), (0.035, 0.035, 0.035), 2, seg=8)
    return new_obj("lightning_rod", bm, [ACC, STONE, GLASS])


def storm_orb():
    """a storm caught in a glass orb, held in a copper claw on an iron stand"""
    bm = bmesh.new()
    cyl(bm, O, 0.22, 0.06, 0, seg=10)
    cyl(bm, O + Vector((0, 0, 0.06)), 0.05, 0.5, 0, seg=8)
    for k in range(4):
        a = k * 1.571
        tube(bm, [O + Vector((0, 0, 0.54)), O + Vector((math.cos(a) * 0.2, math.sin(a) * 0.2, 0.68)),
                  O + Vector((math.cos(a) * 0.16, math.sin(a) * 0.16, 0.86))], 0.02, 1, sides=4)
    ellipsoid(bm, O + Vector((0, 0, 0.76)), (0.19, 0.19, 0.19), 2, seg=14)
    return new_obj("storm_orb", bm, [IRON, ACC, GLASS])


def weather_vane():
    """a copper weather vane: a rooster gone green on a crossed compass, on a post"""
    bm = bmesh.new()
    cyl(bm, O, 0.03, 0.9, 0, seg=6)
    for a in (0, 1.571):
        tube(bm, [O + Vector((math.cos(a) * -0.24, math.sin(a) * -0.24, 0.62)), O + Vector((math.cos(a) * 0.24, math.sin(a) * 0.24, 0.62))], 0.012, 0, sides=4)
    box(bm, O + Vector((-0.2, -0.01, 0.82)), O + Vector((0.12, 0.01, 0.9)), 0)
    box(bm, O + Vector((0.06, -0.01, 0.86)), O + Vector((0.14, 0.01, 1.0)), 0)
    box(bm, O + Vector((-0.26, -0.01, 0.84)), O + Vector((-0.16, 0.01, 0.98)), 0)
    return new_obj("weather_vane", bm, [ACC])


def rope_coil():
    """a coil of tarred rope on the boards, a hook through it"""
    bm = bmesh.new()
    for k in range(4):
        tube(bm, ring(O + Vector((0, 0, 0.04 + k * 0.06)), 0.3 - k * 0.03, "Z", 18), 0.035, 0, sides=5, closed=True)
    tube(bm, [O + Vector((0.2, 0, 0.3)), O + Vector((0.3, 0.05, 0.2)), O + Vector((0.32, 0.05, 0.1))], 0.02, 1, sides=4)
    return new_obj("rope_coil", bm, [CLOTH, IRON])


# ---------------------------------------------------------------- the Bloodmoon Court's own

def kneeling_statue():
    """a black marble servant kneeling, head bowed, holding up an empty silver tray"""
    bm = bmesh.new()
    box(bm, Vector((0.14, -0.86, 0.0)), Vector((0.86, -0.14, 0.1)), 0, bevel=0.02)
    ellipsoid(bm, Vector((0.5, -0.62, 0.22)), (0.2, 0.18, 0.12), 0, seg=10)
    ellipsoid(bm, Vector((0.5, -0.5, 0.42)), (0.16, 0.12, 0.2), 0, seg=10)
    ellipsoid(bm, Vector((0.5, -0.36, 0.6)), (0.08, 0.08, 0.09), 0, seg=10)
    for s in (-1, 1):
        tube(bm, [Vector((0.5 + s * 0.15, -0.48, 0.52)), Vector((0.5 + s * 0.17, -0.3, 0.6)), Vector((0.5 + s * 0.12, -0.2, 0.78))], 0.04, 0, sides=6)
    cyl(bm, Vector((0.5, -0.2, 0.8)), 0.2, 0.025, 1, seg=16)
    return new_obj("kneeling_statue", bm, [STONE, ACC])


def blood_cask():
    """a cask of blood on its side in a cradle, a silver tap, a dark drip"""
    bm = bmesh.new()
    lathe(bm, [(0.0, -0.4), (0.3, -0.4), (0.36, -0.2), (0.38, 0.0), (0.36, 0.2), (0.3, 0.4), (0.0, 0.4)], O + Vector((0, 0, 0.42)), 0, 20, "X")
    for x in (-0.3, -0.12, 0.12, 0.3):
        cyl(bm, O + Vector((x, 0, 0.42)), 0.37 - abs(x) * 0.12, 0.03, 1, seg=20, axis="X")
    for x in (-0.24, 0.24):
        box(bm, O + Vector((x - 0.04, -0.34, 0.0)), O + Vector((x + 0.04, 0.34, 0.12)), 0)
    tube(bm, [O + Vector((0.42, 0, 0.42)), O + Vector((0.5, 0, 0.42)), O + Vector((0.5, 0, 0.36))], 0.025, 1, sides=6)
    ellipsoid(bm, O + Vector((0.5, 0, 0.02)), (0.08, 0.08, 0.01), 2, seg=8)
    return new_obj("blood_cask", bm, [WOOD, ACC, GLASS])


def candelabra():
    """a tall silver candelabra, five arms, the candles burning red"""
    bm = bmesh.new()
    cyl(bm, O, 0.16, 0.05, 0, seg=12)
    cyl(bm, O + Vector((0, 0, 0.05)), 0.03, 0.7, 0, seg=8)
    for k in range(4):
        a = k * 1.571 + 0.785
        tube(bm, [O + Vector((0, 0, 0.6)), O + Vector((math.cos(a) * 0.18, math.sin(a) * 0.18, 0.66)),
                  O + Vector((math.cos(a) * 0.2, math.sin(a) * 0.2, 0.76))], 0.018, 0, sides=5)
    for (x, y) in ((0, 0),) + tuple((math.cos(k * 1.571 + 0.785) * 0.2, math.sin(k * 1.571 + 0.785) * 0.2) for k in range(4)):
        cyl(bm, O + Vector((x, y, 0.76)), 0.025, 0.12, 1, seg=8)
        ellipsoid(bm, O + Vector((x, y, 0.92)), (0.018, 0.018, 0.035), 2, seg=6)
    return new_obj("candelabra", bm, [ACC, mat("court_wax", (0.6, 0.55, 0.5), 0.5), GLASS])


def court_mirror():
    """a tall gilt mirror against the wall, cracked, the glass dark red"""
    bm = bmesh.new()
    box(bm, Vector((0.08, -0.62, 0.0)), Vector((0.92, -0.38, 0.06)), 0)
    for (x0, z0, x1, z1) in ((0.1, 0.06, 0.9, 0.14), (0.1, 0.9, 0.9, 1.0), (0.1, 0.06, 0.18, 1.0), (0.82, 0.06, 0.9, 1.0)):
        box(bm, Vector((x0, -0.54, z0)), Vector((x1, -0.42, z1)), 0, bevel=0.015)
    box(bm, Vector((0.18, -0.5, 0.14)), Vector((0.82, -0.46, 0.9)), 1)
    ellipsoid(bm, Vector((0.5, -0.48, 1.0)), (0.2, 0.04, 0.08), 0, seg=10)
    for yy in (-0.505, -0.455):
        tube(bm, [Vector((0.3, yy, 0.7)), Vector((0.46, yy, 0.5)), Vector((0.4, yy, 0.3))], 0.006, 2, sides=4)
    return new_obj("court_mirror", bm, [mottled("court_gilt", stops("#5e400c", "#b48a24", "#dab43c"), 6.0, 0.4, **{"Metallic": 0.8}), GLASS, DARK])


# ---------------------------------------------------------------- the Obsidian Labyrinth's own

def ember_brazier():
    """a bronze bowl on a basalt drum, heaped with embers, bull horns cast on its rim"""
    bm = bmesh.new()
    cyl(bm, O, 0.22, 0.44, 0, seg=6)
    lathe(bm, [(0.08, 0.44), (0.28, 0.5), (0.4, 0.66), (0.42, 0.72), (0.36, 0.72)], O, 1, 18)
    ellipsoid(bm, O + Vector((0, 0, 0.7)), (0.34, 0.34, 0.08), 2, seg=12)
    for s in (-1, 1):
        tube(bm, [O + Vector((s * 0.4, 0, 0.7)), O + Vector((s * 0.52, 0, 0.8)), O + Vector((s * 0.5, 0, 0.94))], lambda t: 0.04 * (1 - t * 0.7), 1, sides=6)
    return new_obj("ember_brazier", bm, [STONE, ACC, GLASS])


def bull_skull():
    """a bull's skull on the floor, the horns long and black, a bronze ring through the nose"""
    bm = bmesh.new()
    ellipsoid(bm, Vector((0.5, -0.5, 0.2)), (0.16, 0.24, 0.16), 0, seg=12)
    ellipsoid(bm, Vector((0.5, -0.24, 0.14)), (0.1, 0.14, 0.1), 0, seg=10)
    for s in (-1, 1):
        ellipsoid(bm, Vector((0.5 + s * 0.08, -0.4, 0.24)), (0.035, 0.035, 0.035), 3, seg=6)
        tube(bm, [Vector((0.5 + s * 0.14, -0.58, 0.28)), Vector((0.5 + s * 0.34, -0.6, 0.34)), Vector((0.5 + s * 0.44, -0.5, 0.56))],
             lambda t: 0.05 * (1 - t * 0.8), 1, sides=7)
    tube(bm, ring(Vector((0.5, -0.12, 0.1)), 0.05, "Y", 10), 0.012, 2, sides=4, closed=True)
    return new_obj("bull_skull", bm, [mottled("maze_bone", stops("#5a5240", "#9e9476", "#c0b896"), 8.0, 0.6), DARK, ACC, DARK])


def cinder_pile():
    """a heap of cinders still glowing at the heart"""
    import random
    rnd = random.Random(5)
    bm = bmesh.new()
    ellipsoid(bm, O + Vector((0, 0, 0.0)), (0.42, 0.4, 0.16), 0, seg=10)
    for k in range(10):
        a, r = rnd.uniform(0, 6.28), rnd.uniform(0.05, 0.36)
        ellipsoid(bm, O + Vector((math.cos(a) * r, math.sin(a) * r, 0.08 + rnd.uniform(0, 0.08))), (0.06, 0.05, 0.04), 0 if k % 3 else 1, seg=6)
    return new_obj("cinder_pile", bm, [STONE, GLASS])


def thread_spool():
    """the red thread of the maze, wound on a bronze spool, a length of it running off"""
    bm = bmesh.new()
    cyl(bm, O, 0.2, 0.04, 0, seg=14)
    cyl(bm, O + Vector((0, 0, 0.04)), 0.12, 0.5, 1, seg=14)
    cyl(bm, O + Vector((0, 0, 0.54)), 0.2, 0.04, 0, seg=14)
    tube(bm, [O + Vector((0.12, 0, 0.3)), O + Vector((0.3, 0.1, 0.1)), O + Vector((0.45, 0.2, 0.01))], 0.012, 1, sides=4)
    return new_obj("thread_spool", bm, [ACC, CLOTH])


# ---------------------------------------------------------------- the Abyssal Lighthouse's own

def oil_barrels():
    """two barrels of lamp oil and a can, the wood gone teal, brass hoops"""
    bm = bmesh.new()
    for (x, y, h) in ((-0.18, -0.1, 0.62), (0.2, 0.14, 0.5)):
        c = O + Vector((x, y, 0))
        lathe(bm, [(0.0, 0.0), (0.17, 0.0), (0.2, h * 0.5), (0.17, h), (0.0, h)], c, 0, 16)
        for z in (0.08, h - 0.08):
            cyl(bm, c + Vector((0, 0, z - 0.015)), 0.19, 0.03, 1, seg=16)
    cyl(bm, O + Vector((0.24, -0.24, 0)), 0.07, 0.2, 1, seg=10)
    tube(bm, [O + Vector((0.24, -0.24, 0.2)), O + Vector((0.3, -0.24, 0.26))], 0.015, 1, sides=4)
    return new_obj("oil_barrels", bm, [WOOD, ACC])


def rope_net():
    """a fishing net hung from the ceiling, corks and a glass float caught in it"""
    bm = bmesh.new()
    for k in range(5):
        x = -0.4 + k * 0.2
        tube(bm, [O + Vector((x, 0, 1.0)), O + Vector((x + 0.04, 0.02, 0.5)), O + Vector((x * 0.8, 0.04, 0.1))], 0.008, 0, sides=4)
    for k in range(5):
        z = 0.9 - k * 0.18
        tube(bm, [O + Vector((-0.42, 0.02, z)), O + Vector((0.42, 0.02, z - 0.04))], 0.008, 0, sides=4)
    for (x, z) in ((-0.2, 0.3), (0.24, 0.5), (0.0, 0.14)):
        ellipsoid(bm, O + Vector((x, 0.04, z)), (0.05, 0.05, 0.04), 1, seg=6)
    ellipsoid(bm, O + Vector((0.1, 0.06, 0.66)), (0.08, 0.08, 0.08), 2, seg=10)
    return new_obj("rope_net", bm, [CLOTH, WOOD, GLASS])


def ship_wheel():
    """a ship's wheel off a wreck, standing on its post, the spokes broken"""
    bm = bmesh.new()
    box(bm, Vector((0.42, -0.56, 0.0)), Vector((0.58, -0.44, 0.5)), 0)
    tube(bm, ring(Vector((0.5, -0.5, 0.62)), 0.3, "Y", 24), 0.03, 0, sides=6, closed=True)
    for k in range(8):
        a = k * 0.785
        L = 0.42 if k % 3 else 0.3
        tube(bm, [Vector((0.5, -0.5, 0.62)), Vector((0.5 + math.cos(a) * L, -0.5, 0.62 + math.sin(a) * L))], 0.02, 0, sides=5)
    cyl(bm, Vector((0.5, -0.5, 0.62)), 0.06, 0.08, 1, seg=10, axis="Y")
    return new_obj("ship_wheel", bm, [WOOD, ACC])


def diving_helmet():
    """a brass diving helmet on the rock, the porthole cracked, something pale still inside"""
    bm = bmesh.new()
    ellipsoid(bm, O + Vector((0, 0, 0.3)), (0.26, 0.26, 0.26), 0, seg=16)
    cyl(bm, O + Vector((0, 0, 0.0)), 0.3, 0.1, 0, seg=16)
    for a in (0, 1.571, 3.14):
        cyl(bm, O + Vector((math.cos(a) * 0.2, math.sin(a) * 0.2, 0.32)), 0.1, 0.08, 0, seg=12, axis="X" if a in (0, 3.14) else "Y")
    ellipsoid(bm, O + Vector((0.24, 0, 0.32)), (0.03, 0.08, 0.08), 1, seg=10)
    return new_obj("diving_helmet", bm, [ACC, GLASS])


# ---------------------------------------------------------------- the Eclipse Cathedral's own

def ash_censer():
    """a tall gilt censer on three legs, the bowl pierced, white-gold coals and ash spilling"""
    bm = bmesh.new()
    for k in range(3):
        a = k * 2.094
        tube(bm, [O + Vector((math.cos(a) * 0.26, math.sin(a) * 0.26, 0.0)), O + Vector((math.cos(a) * 0.12, math.sin(a) * 0.12, 0.5))], 0.025, 1, sides=5)
    lathe(bm, [(0.04, 0.48), (0.2, 0.52), (0.3, 0.66), (0.3, 0.74), (0.24, 0.76)], O, 1, 18)
    ellipsoid(bm, O + Vector((0, 0, 0.74)), (0.24, 0.24, 0.05), 2, seg=12)
    lathe(bm, [(0.22, 0.78), (0.18, 0.86), (0.06, 0.94), (0.0, 0.98)], O, 1, 14)
    for k in range(6):
        a = k * 1.047
        ellipsoid(bm, O + Vector((math.cos(a) * 0.29, math.sin(a) * 0.29, 0.68)), (0.025, 0.025, 0.03), 2, seg=6)
    return new_obj("ash_censer", bm, [STONE, ACC, GLASS])


def fallen_angel():
    """an angel of black stone knelt on the floor, head bowed into its hands, one great wing raised and torn, the other
    broken off and lying beside it, its gilt halo slipped down over the bowed head"""
    bm = bmesh.new()
    box(bm, Vector((0.08, -0.92, 0.0)), Vector((0.92, -0.08, 0.06)), 0)
    c = Vector((0.5, -0.46, 0.06))
    lathe(bm, [(0.0, 0.0), (0.24, 0.0), (0.22, 0.12), (0.17, 0.3), (0.13, 0.46), (0.1, 0.56), (0.0, 0.58)], c, 1, 16)   # the robe, kneeling
    ellipsoid(bm, c + Vector((0, -0.06, 0.58)), (0.14, 0.11, 0.1), 1, seg=12)                                      # the shoulders
    ellipsoid(bm, c + Vector((0, -0.16, 0.62)), (0.07, 0.075, 0.085), 1, seg=12)                                   # the bowed head
    tube(bm, ring(c + Vector((0, -0.2, 0.72)), 0.1, "Y", 18), 0.014, 2, sides=5, closed=True)                       # the halo
    for s in (-1, 1):                                                                                               # arms up to the face
        tube(bm, [c + Vector((s * 0.13, -0.04, 0.6)), c + Vector((s * 0.12, -0.18, 0.46)), c + Vector((s * 0.04, -0.24, 0.6))], 0.035, 1, sides=6)
    root = c + Vector((0.08, 0.08, 0.6))                                                                            # the raised wing
    bone = [root, root + Vector((0.18, 0.06, 0.2)), root + Vector((0.3, 0.1, 0.36)), root + Vector((0.34, 0.12, 0.3))]
    tube(bm, bone, lambda t: 0.05 * (1 - t * 0.6), 1, sides=6)
    for k in range(8):
        f = k / 7.0
        seg = min(2, int(f * 3))
        p0 = bone[seg].lerp(bone[seg + 1], f * 3 - seg)
        L = 0.28 + 0.26 * f if k != 5 else 0.12                                                                    # one feather torn short
        tube(bm, [p0, p0 + Vector((0.02 + f * 0.04, 0.03, -L))], lambda t: 0.045 * (1 - t * 0.75), 1, sides=4)
    tube(bm, [c + Vector((-0.08, 0.08, 0.6)), c + Vector((-0.16, 0.12, 0.66))], 0.05, 1, sides=6)                  # the stump
    for k in range(5):                                                                                              # the broken wing on the floor
        tube(bm, [c + Vector((-0.34 + k * 0.04, 0.34, 0.03)), c + Vector((-0.18 + k * 0.02, 0.08 - k * 0.05, 0.05))],
             lambda t: 0.04 * (1 - t * 0.6), 1, sides=4)
    return new_obj("fallen_angel", bm, [STONE, mottled("eclipse_marble", stops("#0e0e14", "#2a2a34", "#4a4a58"), 6.0, 0.5), ACC])


def black_pew():
    """a pew of black wood, its end carved with a gilt sun, ash on the seat"""
    bm = bmesh.new()
    box(bm, Vector((0.02, -0.72, 0.36)), Vector((0.98, -0.3, 0.42)), 0)
    box(bm, Vector((0.02, -0.3, 0.36)), Vector((0.98, -0.24, 0.78)), 0)
    for x in (0.02, 0.9):
        box(bm, Vector((x, -0.74, 0.0)), Vector((x + 0.08, -0.22, 0.72)), 0)
        cyl(bm, Vector((x + 0.04, -0.5, 0.6)), 0.08, 0.02, 1, seg=12, axis="X")
    box(bm, Vector((0.1, -0.7, 0.42)), Vector((0.9, -0.34, 0.43)), 2)
    return new_obj("black_pew", bm, [WOOD, ACC, CLOTH])


def feather_drift():
    """a drift of black feathers and ash on the floor"""
    import random
    rnd = random.Random(11)
    bm = bmesh.new()
    ellipsoid(bm, O + Vector((0, 0, 0.0)), (0.44, 0.42, 0.04), 1, seg=10)
    for k in range(18):
        a, r = rnd.uniform(0, 6.28), rnd.uniform(0.0, 0.42)
        p0 = O + Vector((math.cos(a) * r, math.sin(a) * r, 0.04))
        b = rnd.uniform(0, 6.28)
        tube(bm, [p0, p0 + Vector((math.cos(b) * 0.16, math.sin(b) * 0.16, 0.03))], lambda t: 0.03 * (1 - t * 0.8), 0, sides=3)
    return new_obj("feather_drift", bm, [mottled("eclipse_feather", stops("#050506", "#121218", "#24242c"), 10.0, 0.6), CLOTH])


# ---------------------------------------------------------------- the Wyrm's Hoard's own

def gold_pile():
    """a heap of coins with a goblet, a crown and a sword hilt sticking out of it"""
    import random
    rnd = random.Random(3)
    bm = bmesh.new()
    ellipsoid(bm, O + Vector((0, 0, 0.0)), (0.48, 0.46, 0.34), 0, seg=14)
    for k in range(26):
        a, r = rnd.uniform(0, 6.28), rnd.uniform(0.1, 0.5)
        z = max(0.01, 0.32 * (1 - (r / 0.5) ** 2))
        cyl(bm, O + Vector((math.cos(a) * r, math.sin(a) * r, z + 0.01)), 0.055, 0.016, 1, seg=10)
    lathe(bm, [(0.0, 0.0), (0.06, 0.0), (0.02, 0.04), (0.02, 0.14), (0.08, 0.18), (0.09, 0.28), (0.0, 0.22)], O + Vector((0.18, -0.1, 0.24)), 1, 12)
    cyl(bm, O + Vector((-0.16, 0.08, 0.28)), 0.12, 0.06, 1, seg=14)
    for k in range(6):
        a = k * 1.047
        tube(bm, [O + Vector((-0.16 + math.cos(a) * 0.12, 0.08 + math.sin(a) * 0.12, 0.34)), O + Vector((-0.16 + math.cos(a) * 0.12, 0.08 + math.sin(a) * 0.12, 0.42))], lambda t: 0.02 * (1 - t * 0.8), 1, sides=4)
        ellipsoid(bm, O + Vector((-0.16 + math.cos(a + 0.5) * 0.125, 0.08 + math.sin(a + 0.5) * 0.125, 0.31)), (0.018, 0.018, 0.018), 2, seg=6)
    tube(bm, [O + Vector((0.04, 0.22, 0.2)), O + Vector((0.08, 0.28, 0.5))], 0.02, 3, sides=6)
    box(bm, O + Vector((0.0, 0.18, 0.4)), O + Vector((0.16, 0.34, 0.43)), 1)
    return new_obj("gold_pile", bm, [mottled("hoard_heap", stops("#8a6010", "#e0ac2c", "#fcd860"), 14.0, 0.7), ACC, CLOTH, WOOD])


def dragon_egg():
    """a dragon's egg turned to stone in the ash, the shell in plates, fire showing through the cracks"""
    bm = bmesh.new()
    lathe(bm, [(0.0, 0.0), (0.16, 0.04), (0.26, 0.22), (0.27, 0.4), (0.22, 0.62), (0.12, 0.8), (0.0, 0.86)], O + Vector((0, 0, 0.04)), 0, 20)
    for k in range(7):
        a = k * 0.9
        z = 0.2 + (k % 3) * 0.2
        tube(bm, [O + Vector((math.cos(a) * 0.27, math.sin(a) * 0.27, z)), O + Vector((math.cos(a + 0.3) * 0.26, math.sin(a + 0.3) * 0.26, z + 0.14))], 0.012, 1, sides=4)
    ellipsoid(bm, O + Vector((0, 0, 0.02)), (0.3, 0.3, 0.05), 2, seg=12)
    return new_obj("dragon_egg", bm, [mottled("hoard_eggshell", stops("#100c0a", "#2a2018", "#4a3a2a"), 7.0, 0.5), GLASS, STONE])


def wyrm_skull():
    """the skull of a drake, long-jawed, horned, teeth like knives, gold coins in the eye sockets"""
    bm = bmesh.new()
    c = Vector((0.5, -0.5, 0.0))
    ellipsoid(bm, c + Vector((0, 0.2, 0.24)), (0.2, 0.22, 0.18), 0, seg=12)
    box(bm, c + Vector((-0.11, -0.48, 0.08)), c + Vector((0.11, 0.06, 0.24)), 0)
    box(bm, c + Vector((-0.09, -0.44, 0.0)), c + Vector((0.09, 0.0, 0.08)), 0)
    for k in range(6):
        y = -0.42 + k * 0.08
        for s in (-1, 1):
            tube(bm, [c + Vector((s * 0.1, y, 0.1)), c + Vector((s * 0.1, y, 0.03))], lambda t: 0.018 * (1 - t * 0.8), 2, sides=4)
    for s in (-1, 1):
        cyl(bm, c + Vector((s * 0.1, 0.06, 0.3)), 0.05, 0.02, 1, seg=10, axis="X")
        tube(bm, [c + Vector((s * 0.14, 0.3, 0.36)), c + Vector((s * 0.3, 0.46, 0.5)), c + Vector((s * 0.34, 0.64, 0.58))], lambda t: 0.06 * (1 - t * 0.85), 2, sides=6)
    return new_obj("wyrm_skull", bm, [mottled("hoard_bone", stops("#5c5240", "#9c9076", "#bcb094"), 8.0, 0.6), ACC, DARK])


def kobold_totem():
    """a kobold totem: a pole of charred wood with a dragon head carved on top, coins nailed on, a candle burning"""
    bm = bmesh.new()
    cyl(bm, O, 0.07, 0.72, 0, seg=8)
    ellipsoid(bm, O + Vector((0, 0.04, 0.78)), (0.1, 0.14, 0.09), 0, seg=10)
    box(bm, O + Vector((-0.05, 0.1, 0.72)), O + Vector((0.05, 0.26, 0.8)), 0)
    for s in (-1, 1):
        tube(bm, [O + Vector((s * 0.06, -0.04, 0.84)), O + Vector((s * 0.12, -0.12, 0.96))], lambda t: 0.025 * (1 - t * 0.8), 2, sides=5)
    for k in range(5):
        a = k * 1.25
        cyl(bm, O + Vector((math.cos(a) * 0.072, math.sin(a) * 0.072, 0.2 + k * 0.09)), 0.035, 0.01, 1, seg=8, axis="X" if k % 2 else "Y")
    cyl(bm, O + Vector((0, 0.0, 0.86)), 0.025, 0.08, 3, seg=8)
    ellipsoid(bm, O + Vector((0, 0.0, 0.97)), (0.02, 0.02, 0.035), 4, seg=6)
    return new_obj("kobold_totem", bm, [WOOD, CLOTH, ACC, mottled("hoard_wax", stops("#a08a6a", "#d8c8a0", "#f0e4c0"), 6.0, 0.4), GLASS])


CLOTH_RED = mottled("mire_cap_red", stops("#4a0e08", "#8a1e10", "#b8301a"), 10.0, 0.7)

MAKE_COMMON = [(lantern, (128, 128)), (chain, (64, 64)), (bars_post, (64, 64)), (bars_side, (64, 64)), (coffer, (256, 256))]
UNIQUE = {
    "clockwork_spire": [(hoard, (512, 512))],
    "serpent_ziggurat": [(hoard, (512, 512))],
    "rimeholt": [(hoard, (512, 512))],
    "glass_minaret": [(hoard, (512, 512))],
    "warlords_fang": [(hoard, (512, 512))],
    "weeping_mine": [(crystal_cluster, (256, 256)), (minecart, (256, 256)), (mine_rail, (128, 128)), (ore_sacks, (256, 256))],
    "brigands_gorge": [(loot_pile, (256, 256)), (gorge_campfire, (256, 256)), (gorge_weapon_rack, (256, 256)), (bandit_tent, (256, 256))],
    "rookery": [(crow_nest, (256, 256)), (crow_perch, (128, 128)), (bone_chimes, (128, 128)), (omen_altar, (256, 256))],
    "hollow_circus": [(circus_drum, (256, 256)), (circus_cage, (256, 256)), (circus_tent, (256, 256)), (juggling_clubs, (128, 128))],
    "mirefen_coven": [(coven_cauldron, (256, 256)), (hag_effigy, (128, 128)), (fen_toadstools, (128, 128)), (fen_reeds, (128, 128))],
    "sandsunk_tomb": [(canopic_jars, (256, 256)), (sarcophagus, (256, 256)), (sun_brazier, (128, 128)), (jackal_statue, (256, 256))],
    "fallen_titan": [(breathing_sac, (256, 256)), (rib_spur, (128, 128)), (eaten_armour, (256, 256)), (artery_root, (128, 128))],
    "jade_monastery": [(incense_burner, (256, 256)), (prayer_wheel, (128, 128)), (stone_lantern, (128, 128)), (temple_bell, (256, 256))],
    "storm_bastion": [(lightning_rod, (128, 128)), (storm_orb, (128, 128)), (weather_vane, (128, 128)), (rope_coil, (128, 128))],
    "bloodmoon_court": [(kneeling_statue, (256, 256)), (blood_cask, (256, 256)), (candelabra, (128, 128)), (court_mirror, (256, 256))],
    "obsidian_labyrinth": [(ember_brazier, (256, 256)), (bull_skull, (256, 256)), (cinder_pile, (128, 128)), (thread_spool, (128, 128))],
    "abyssal_lighthouse": [(oil_barrels, (256, 256)), (rope_net, (128, 128)), (ship_wheel, (256, 256)), (diving_helmet, (128, 128))],
    "eclipse_cathedral": [(ash_censer, (256, 256)), (fallen_angel, (256, 256)), (black_pew, (256, 256)), (feather_drift, (128, 128))],
    "wyrms_hoard": [(gold_pile, (256, 256)), (dragon_egg, (256, 256)), (wyrm_skull, (256, 256)), (kobold_totem, (128, 128))],
    "tide_chapel": [(drowned_pew, (256, 256)), (kelp_strand, (128, 128)), (clam_heap, (256, 256)), (chapel_font, (256, 256))],
}
run(MAKE_COMMON + UNIQUE.get(GATE, []), GLOWS, GATE + "_props")
