"""The three Trades stations (pass 16), our own benches over any mod's stove, keg or stand (Trades.Bench tier 1: up to Epic,
the make-again list): real meshes like the Gate Forge.
  cooks_fire        a ring hearth of dressed stones, logs glowing in it, an iron tripod with a black cauldron hung over the
                    fire, a chopping board at its foot with a knife, a carrot and an onion
  brewers_cask      a hooped oak barrel on its side in a cradle, a brass tap in its head dripping into a tankard on a little
                    shelf, a hop sack leaning on it and a mallet on top
  alchemists_bench  a small oak table: a glass alembic over a spirit burner, its coiled arm into a receiving bottle, a rack
                    of three vials (red, blue, green), a mortar and pestle, a folded recipe sheet
  blender -b -P tools/blender/station_props.py -- [preview]   -> models/mesh/<id>.obj, renders/station_props.png"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "propkit.py"), encoding="utf-8").read())

STONE = mottled("hearth_stone", [(0.0, (0.025, 0.022, 0.02)), (0.6, (0.07, 0.065, 0.06)), (1.0, (0.13, 0.12, 0.11))], 8.0, 0.85)
SOOT = mottled("soot", [(0.0, (0.01, 0.01, 0.01)), (1.0, (0.05, 0.045, 0.04))], 12.0, 0.9)
IRON = rusty("tripod_iron", iron=(0.02, 0.02, 0.022), rust=(0.12, 0.05, 0.02), amount=0.2, rough=0.45)
LOG = wood("logs", [(0.0, (0.06, 0.035, 0.02)), (1.0, (0.2, 0.12, 0.06))], along="X")
EMBER = mat("embers", (1.0, 0.3, 0.04), 0.6, **{"Emission Color": (1.0, 0.36, 0.06, 1), "Emission Strength": 6.0})
FLAME = mat("flame", (1.0, 0.55, 0.12), 0.5, **{"Emission Color": (1.0, 0.6, 0.15, 1), "Emission Strength": 8.0})
OAK = wood("oak", [(0.0, (0.05, 0.028, 0.014)), (1.0, (0.16, 0.095, 0.045))], along="Z")
OAKX = wood("oak_x", [(0.0, (0.05, 0.028, 0.014)), (1.0, (0.16, 0.095, 0.045))], along="X")
BOARD = wood("board", [(0.0, (0.14, 0.09, 0.045)), (1.0, (0.3, 0.2, 0.1))], along="X")
BRASS = mat("brass", (0.62, 0.45, 0.16), 0.3, **{"Metallic": 1.0})
STEEL = mat("steel", (0.5, 0.52, 0.55), 0.3, **{"Metallic": 1.0})
CARROT = mat("carrot", (0.85, 0.32, 0.05), 0.55)
LEAF = mat("leaves", (0.18, 0.42, 0.1), 0.6)
ONION = mat("onion", (0.75, 0.55, 0.32), 0.45)
SACK = mottled("sack", [(0.0, (0.3, 0.24, 0.15)), (1.0, (0.55, 0.46, 0.3))], 30.0, 0.95)
HOPS = mat("hops", (0.42, 0.6, 0.18), 0.7)
ALE = mat("ale", (0.55, 0.32, 0.05), 0.2)
GLASS = glass("alembic_glass", (0.55, 0.75, 0.7), rough=0.04)
RED = mat("vial_red", (0.9, 0.1, 0.15), 0.2, **{"Emission Color": (0.9, 0.1, 0.15, 1), "Emission Strength": 1.5})
BLUE = mat("vial_blue", (0.15, 0.35, 1.0), 0.2, **{"Emission Color": (0.15, 0.35, 1.0, 1), "Emission Strength": 1.5})
GREEN = mat("vial_green", (0.3, 0.9, 0.3), 0.2, **{"Emission Color": (0.3, 0.9, 0.3, 1), "Emission Strength": 1.5})
BREW = mat("alembic_brew", (0.75, 0.3, 1.0), 0.2, **{"Emission Color": (0.7, 0.3, 1.0, 1), "Emission Strength": 2.5})
MARBLE = mottled("mortar", [(0.0, (0.55, 0.54, 0.5)), (1.0, (0.85, 0.84, 0.8))], 6.0, 0.4)
PAPER = mat("paper", (0.85, 0.78, 0.6), 0.8)
STEW = mat("stew", (0.35, 0.16, 0.05), 0.4)
GLOWS.update({EMBER, FLAME, RED, BLUE, GREEN, BREW})


def cooks_fire():
    bm = bmesh.new()
    # the hearth: a ring of nine dressed stones on a sooty floor stone
    cyl(bm, O + Vector((0, 0, 0)), 0.42, 0.03, 1, seg=24)
    for i in range(9):
        a = i / 9 * math.tau
        c = O + Vector((math.cos(a) * 0.36, math.sin(a) * 0.36, 0.03))
        vs = box(bm, c + Vector((-0.07, -0.05, 0)), c + Vector((0.07, 0.05, 0.11 + 0.02 * (i % 3))), 0, bevel=0.025,
                 rot=Matrix.Rotation(a + math.pi / 2, 4, "Z"))
        displace(vs, 0.008, 9.0, i)
    # logs crossed in the middle, glowing underneath, a tongue of flame
    for k, a in enumerate((0.4, -0.5, 1.6)):
        d = Vector((math.cos(a), math.sin(a), 0)) * 0.2
        tube(bm, [O + Vector((0, 0, 0.07 + 0.03 * k)) - d, O + Vector((0, 0, 0.07 + 0.03 * k)) + d], 0.035, 2, sides=7)
    ellipsoid(bm, O + Vector((0, 0, 0.06)), (0.16, 0.16, 0.04), 3)
    for k in range(3):
        a = k * 2.1
        cyl(bm, O + Vector((math.cos(a) * 0.04, math.sin(a) * 0.04, 0.1)), 0.05 - 0.01 * k, 0.16 + 0.04 * (k % 2), 4, seg=7, r2=0.004)
    # the iron tripod and the cauldron hung from its crown
    top = O + Vector((0, 0, 0.95))
    for i in range(3):
        a = i / 3 * math.tau + 0.3
        tube(bm, [O + Vector((math.cos(a) * 0.4, math.sin(a) * 0.4, 0.04)), top], 0.014, 5, sides=6)
    tube(bm, [top, top - Vector((0, 0, 0.32))], 0.006, 5, sides=4)
    lathe(bm, [(0.0, 0.0), (0.1, 0.01), (0.17, 0.08), (0.18, 0.16), (0.16, 0.24), (0.165, 0.26), (0.14, 0.26)], O + Vector((0, 0, 0.36)), 1, seg=20)
    tube(bm, ring(O + Vector((0, 0, 0.63)), 0.13, "X", 16)[8:], 0.006, 5, sides=4)
    ellipsoid(bm, O + Vector((0, 0, 0.6)), (0.14, 0.14, 0.012), 12)
    # the chopping board at the front with its knife and a carrot and an onion
    box(bm, O + Vector((0.1, 0.3, 0.0)), O + Vector((0.42, 0.48, 0.04)), 7, bevel=0.008, rot=Matrix.Rotation(-0.2, 4, "Z"))
    box(bm, O + Vector((0.2, 0.36, 0.04)), O + Vector((0.34, 0.38, 0.046)), 8, bevel=0.002, rot=Matrix.Rotation(-0.2, 4, "Z"))
    box(bm, O + Vector((0.12, 0.36, 0.04)), O + Vector((0.2, 0.38, 0.06)), 2, bevel=0.005, rot=Matrix.Rotation(-0.2, 4, "Z"))
    cyl(bm, O + Vector((0.18, 0.43, 0.065)), 0.02, 0.14, 9, seg=8, r2=0.003, axis="X")
    cyl(bm, O + Vector((0.16, 0.43, 0.065)), 0.012, 0.05, 10, seg=6, r2=0.001, axis="X", cap=True)
    ellipsoid(bm, O + Vector((0.36, 0.42, 0.075)), (0.035, 0.035, 0.035), 11)
    return new_obj("cooks_fire", bm, [STONE, SOOT, LOG, EMBER, FLAME, IRON, SOOT, BOARD, STEEL, CARROT, LEAF, ONION, STEW])


def brewers_cask():
    bm = bmesh.new()
    # the cradle: two notched trestles and their foot boards
    for x in (-0.28, 0.28):
        box(bm, O + Vector((x - 0.05, -0.4, 0.0)), O + Vector((x + 0.05, 0.4, 0.06)), 0, bevel=0.01)
        box(bm, O + Vector((x - 0.04, -0.3, 0.06)), O + Vector((x + 0.04, -0.2, 0.22)), 0, bevel=0.01)
        box(bm, O + Vector((x - 0.04, 0.2, 0.06)), O + Vector((x + 0.04, 0.3, 0.22)), 0, bevel=0.01)
    # the barrel on its side along x: bulged staves, iron hoops, head boards
    prof = [(0.0, -0.4), (0.27, -0.4), (0.31, -0.3), (0.34, -0.1), (0.345, 0.0), (0.34, 0.1), (0.31, 0.3), (0.27, 0.4), (0.0, 0.4)]
    lathe(bm, [(r, h) for r, h in prof], O + Vector((0, 0, 0.5)), 1, seg=28, axis="X")
    for h, r in ((-0.33, 0.3), (-0.2, 0.33), (0.2, 0.33), (0.33, 0.3)):
        tube(bm, ring(O + Vector((h, 0, 0.5)), r + 0.006, "X", 28), 0.01, 2, sides=4, closed=True)
    # the tap in the front head (+x end faces the side; the tap faces +y front on the belly)
    cyl(bm, O + Vector((0.0, 0.34, 0.42)), 0.025, 0.08, 3, seg=10, axis="Y")
    cyl(bm, O + Vector((0.0, 0.42, 0.42)), 0.012, 0.06, 3, seg=8, r2=0.01, axis="Z")
    box(bm, O + Vector((-0.04, 0.405, 0.47)), O + Vector((0.04, 0.425, 0.49)), 3, bevel=0.004)
    # the tankard under it on a little shelf
    box(bm, O + Vector((-0.1, 0.36, 0.2)), O + Vector((0.1, 0.48, 0.23)), 0, bevel=0.006)
    lathe(bm, [(0.0, 0.0), (0.05, 0.0), (0.055, 0.1), (0.05, 0.11)], O + Vector((0.0, 0.42, 0.23)), 4, seg=14)
    ellipsoid(bm, O + Vector((0.0, 0.42, 0.33)), (0.045, 0.045, 0.006), 5)
    tube(bm, [O + Vector((0.05, 0.42, 0.31)), O + Vector((0.085, 0.42, 0.29)), O + Vector((0.085, 0.42, 0.25)), O + Vector((0.05, 0.42, 0.25))], 0.008, 4, sides=4)
    # a hop sack leaning on its back and a mallet on top
    ellipsoid(bm, O + Vector((-0.3, -0.36, 0.2)), (0.12, 0.1, 0.2), 6)
    for k in range(5):
        ellipsoid(bm, O + Vector((-0.3 + 0.04 * (k - 2), -0.33, 0.42 + 0.02 * (k % 2))), (0.03, 0.03, 0.035), 7)
    tube(bm, [O + Vector((-0.15, -0.05, 0.86)), O + Vector((0.15, 0.08, 0.86))], 0.014, 0, sides=6)
    box(bm, O + Vector((0.12, 0.02, 0.82)), O + Vector((0.22, 0.14, 0.9)), 0, bevel=0.01)
    return new_obj("brewers_cask", bm, [OAKX, OAK, IRON, BRASS, STEEL, ALE, SACK, HOPS])


def alchemists_bench():
    bm = bmesh.new()
    # the table: a thick top on four turned legs with a low shelf
    box(bm, O + Vector((-0.46, -0.36, 0.56)), O + Vector((0.46, 0.36, 0.62)), 0, bevel=0.012)
    for sx in (-1, 1):
        for sy in (-1, 1):
            lathe(bm, [(0.03, 0.0), (0.035, 0.05), (0.025, 0.15), (0.035, 0.3), (0.025, 0.45), (0.03, 0.56)], O + Vector((sx * 0.4, sy * 0.3, 0.0)), 1, seg=10)
    box(bm, O + Vector((-0.4, -0.3, 0.14)), O + Vector((0.4, 0.3, 0.17)), 0, bevel=0.006)
    # the spirit burner and the alembic's round flask on a ring stand
    lathe(bm, [(0.0, 0.0), (0.05, 0.0), (0.055, 0.04), (0.02, 0.06)], O + Vector((-0.18, 0.02, 0.62)), 2, seg=14)
    cyl(bm, O + Vector((-0.18, 0.02, 0.68)), 0.014, 0.05, 3, seg=7, r2=0.002)
    tube(bm, ring(O + Vector((-0.18, 0.02, 0.76)), 0.07, "Z", 16), 0.006, 4, sides=4, closed=True)
    for k in range(3):
        a = k / 3 * math.tau
        tube(bm, [O + Vector((-0.18 + math.cos(a) * 0.07, 0.02 + math.sin(a) * 0.07, 0.62)), O + Vector((-0.18 + math.cos(a) * 0.07, 0.02 + math.sin(a) * 0.07, 0.76))], 0.005, 4, sides=4)
    ellipsoid(bm, O + Vector((-0.18, 0.02, 0.84)), (0.09, 0.09, 0.085), 6)
    cyl(bm, O + Vector((-0.18, 0.02, 0.92)), 0.022, 0.1, 5, seg=10)
    # its arm curling down into the receiving bottle
    pts = [O + Vector((-0.18, 0.02, 1.02)), O + Vector((-0.1, 0.02, 1.04)), O + Vector((0.0, 0.03, 1.0)), O + Vector((0.06, 0.04, 0.9)),
           O + Vector((0.1, 0.04, 0.82)), O + Vector((0.12, 0.04, 0.76))]
    tube(bm, pts, 0.012, 5, sides=7)
    lathe(bm, [(0.0, 0.0), (0.06, 0.0), (0.065, 0.06)], O + Vector((0.12, 0.04, 0.62)), 6, seg=14)
    lathe(bm, [(0.065, 0.0), (0.06, 0.02), (0.03, 0.06), (0.018, 0.09), (0.0, 0.09)], O + Vector((0.12, 0.04, 0.68)), 5, seg=14)
    # the vial rack: a little stand of three, each its own colour
    box(bm, O + Vector((0.22, -0.26, 0.62)), O + Vector((0.42, -0.18, 0.64)), 0, bevel=0.004)
    box(bm, O + Vector((0.22, -0.26, 0.7)), O + Vector((0.42, -0.18, 0.72)), 0, bevel=0.004)
    for k, mi in enumerate((7, 8, 9)):
        x = 0.26 + 0.06 * k
        cyl(bm, O + Vector((x, -0.22, 0.64)), 0.019, 0.09, mi, seg=10)
        cyl(bm, O + Vector((x, -0.22, 0.73)), 0.017, 0.03, 5, seg=10)
        cyl(bm, O + Vector((x, -0.22, 0.76)), 0.013, 0.022, 0, seg=8)
    # mortar and pestle, a folded recipe sheet
    lathe(bm, [(0.0, 0.0), (0.06, 0.0), (0.07, 0.05), (0.065, 0.07), (0.05, 0.07), (0.04, 0.02), (0.0, 0.02)], O + Vector((0.3, 0.2, 0.62)), 10, seg=16)
    tube(bm, [O + Vector((0.3, 0.2, 0.66)), O + Vector((0.36, 0.24, 0.76))], 0.012, 10, sides=6)
    box(bm, O + Vector((-0.42, -0.3, 0.62)), O + Vector((-0.26, -0.12, 0.625)), 11, rot=Matrix.Rotation(0.25, 4, "Z"))
    return new_obj("alchemists_bench", bm, [OAK, OAK, BRASS, FLAME, IRON, GLASS, BREW, RED, BLUE, GREEN, MARBLE, PAPER])


run([(cooks_fire, (256, 256)), (brewers_cask, (256, 256)), (alchemists_bench, (256, 256))], GLOWS, "station_props")
