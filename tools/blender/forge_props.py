"""The Gate Forge (GateForge.java) as a real mesh: a squat furnace of dressed dark stone banded in iron, coals
glowing through its grated mouth, a black anvil on its top with a hammer laid across it and tongs hung off the
horn, a little quench trough at its side and a gate-rune ring of hot metal set in its face.

  blender -b -P tools/blender/forge_props.py -- [preview]     -> models/mesh/gate_forge.obj, renders/forge_props.png"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "propkit.py"), encoding="utf-8").read())

STONE = mottled("forge_stone", [(0.0, (0.012, 0.012, 0.014)), (0.6, (0.035, 0.034, 0.036)), (1.0, (0.07, 0.066, 0.064))], 9.0, 0.85)
IRON = rusty("forge_iron", iron=(0.012, 0.012, 0.014), rust=(0.12, 0.04, 0.015), amount=0.2, rough=0.45)
ANVIL = rusty("anvil_iron", iron=(0.02, 0.02, 0.024), rust=(0.12, 0.05, 0.02), amount=0.12, rough=0.35, metal=0.9)
COAL = mat("coals", (0.95, 0.2, 0.02), 0.6, **{"Emission Color": (1.0, 0.32, 0.05, 1), "Emission Strength": 6.0})
RUNE = mat("rune_hot", (1.0, 0.42, 0.06), 0.4, **{"Emission Color": (1.0, 0.5, 0.12, 1), "Emission Strength": 4.0})
HAFT = wood("hammer_haft", [(0.0, (0.03, 0.02, 0.012)), (1.0, (0.12, 0.08, 0.05))], along="X")
WATER = glass("quench", (0.03, 0.05, 0.06), rough=0.05)
GLOWS.update({COAL, RUNE})


def gate_forge():
    bm = bmesh.new()
    # the furnace: a plinth, the body, a cornice; stone blocks with a seam between courses
    box(bm, O + Vector((-0.5, -0.46, 0.0)), O + Vector((0.5, 0.46, 0.1)), 0, bevel=0.02)
    for k, (z0, z1) in enumerate(((0.1, 0.32), (0.32, 0.54))):
        inset = 0.03 + 0.01 * k
        vs = box(bm, O + Vector((-0.46 + inset, -0.42 + inset, z0)), O + Vector((0.46 - inset, 0.42 - inset, z1 - 0.012)), 0, bevel=0.025)
        displace(vs, 0.006, 7.0, k)
    box(bm, O + Vector((-0.47, -0.43, 0.54)), O + Vector((0.47, 0.43, 0.6)), 0, bevel=0.015)
    # iron bands round the courses, corner plates and rivets
    for z in (0.3, 0.52):
        box(bm, O + Vector((-0.45, -0.41, z)), O + Vector((0.45, 0.41, z + 0.035)), 1, bevel=0.006)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(bm, O + Vector((sx * 0.44 - 0.03, sy * 0.4 - 0.03, 0.1)), O + Vector((sx * 0.44 + 0.03, sy * 0.4 + 0.03, 0.56)), 1, bevel=0.008)
    # the mouth on the front (+y): an arched opening, coals inside, three grate bars
    box(bm, O + Vector((-0.2, 0.36, 0.13)), O + Vector((0.2, 0.42, 0.37)), 1, bevel=0.01)
    box(bm, O + Vector((-0.16, 0.33, 0.15)), O + Vector((0.16, 0.425, 0.33)), 2, bevel=0.01)
    for x in (-0.09, 0.0, 0.09):
        cyl(bm, O + Vector((x, 0.43, 0.24)), 0.014, 0.2, 1, seg=8)
    # the gate rune on the cornice front: a hot ring cut by a crack
    tube(bm, ring(O + Vector((0.0, 0.435, 0.455)), 0.06, "Y", 20), 0.01, 3, sides=5, closed=True)
    tube(bm, [O + Vector((0.0, 0.437, 0.4)), O + Vector((0.012, 0.437, 0.44)), O + Vector((-0.01, 0.437, 0.47)), O + Vector((0.0, 0.437, 0.51))], 0.008, 3, sides=4)
    # the anvil on top: a foot, a waist, the face with its horn and a heel
    box(bm, O + Vector((-0.2, -0.13, 0.6)), O + Vector((0.2, 0.13, 0.66)), 4, bevel=0.01)
    box(bm, O + Vector((-0.11, -0.07, 0.66)), O + Vector((0.11, 0.07, 0.76)), 4, bevel=0.012)
    box(bm, O + Vector((-0.26, -0.1, 0.76)), O + Vector((0.2, 0.1, 0.85)), 4, bevel=0.012)
    cyl(bm, O + Vector((0.2, 0.0, 0.805)), 0.05, 0.16, 4, seg=12, r2=0.008, axis="X")
    box(bm, O + Vector((-0.32, -0.06, 0.79)), O + Vector((-0.26, 0.06, 0.85)), 4, bevel=0.008)
    # a hammer laid across the face, tongs hung off the horn
    tube(bm, [O + Vector((-0.2, -0.02, 0.87)), O + Vector((0.12, 0.08, 0.87))], 0.014, 5, sides=6)
    box(bm, O + Vector((-0.27, -0.06, 0.85)), O + Vector((-0.17, 0.02, 0.91)), 1, bevel=0.008)
    for s in (-1, 1):
        tube(bm, [O + Vector((0.3, s * 0.012, 0.82)), O + Vector((0.32, s * 0.02, 0.7)), O + Vector((0.36, s * 0.04, 0.45))], 0.008, 1, sides=4)
    # the quench trough at its left side, half full
    box(bm, O + Vector((-0.5, -0.36, 0.1)), O + Vector((-0.38, 0.1, 0.3)), 1, bevel=0.01)
    box(bm, O + Vector((-0.49, -0.35, 0.2)), O + Vector((-0.39, 0.09, 0.27)), 6)
    return new_obj("gate_forge", bm, [STONE, IRON, COAL, RUNE, ANVIL, HAFT, WATER])


run([(gate_forge, (256, 256))], GLOWS, "forge_props")
