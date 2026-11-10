"""Concept for the gate remake: a gate you can see INTO (the dungeon's first hall through the tear) and, from inside,
OUT of (the world you came from through the way-out tear), plus the ground the tear breaks: the dungeon's own floor
bleeding into the grass round its foot, a fissure glowing in the rank colour, earth heaved up along it, the
dungeon's water seeping out, its stones hanging in the air, and a trodden path to it.

Builds the block scenes with structkit (tools/renders/struct/gw_*.obj in E:/Ashbound), then
tools/blender/gate_window.py renders the passes and tools/gate_window_comp.py puts them together.

    python tools/gate_window.py            -> the scenes + shots
Everything is placed in the GATE FRAME: O = the ground under the tear's middle, the tear in the plane z = O.z, its
face looking +z. Shots are given relative to O.
"""
import json
import math
import os
import random
import sys

sys.path.insert(0, "E:/Ashbound/tools")
import structkit as K  # noqa: E402

LAIR = "gate_cellar"
O_OUT = (0.0, 0.0, 0.6)           # outside: grass top at y 0, the tear's plane at z 0.6
TP = (0.5, 1.0, -4.5)             # the cellar's arrival point
O_IN = (0.5, 1.0, -3.5)           # the entry tear just behind it, facing back up the hall... seen from the world
EXIT = (0.5, -6.0, -214.5)        # the way-out tear in the boss vault
O_EXIT = (0.5, -6.0, -214.5)

# relative to O: camera, look, lens
SHOTS = {
    "hero": ((-2.6, 1.9, 14.0), (0.3, 3.9, 0.0), 30),
    "side": ((7.5, 1.8, 8.5), (-0.3, 4.2, 0.0), 24),
    "near": ((-1.4, 1.7, 6.0), (0.0, 3.8, 0.0), 24),
    "exit": ((-4.0, 1.7, 13.5), (0.3, 4.6, 0.0), 26),
}
# the quick run through the whole cellar for the cinematic (absolute cellar coordinates): camera, look
RUN = {
    "run1": ((0.5, 3.2, -6.0), (0.5, 2.6, -30.0), 30),
    "run2": ((-3.0, 3.4, -40.0), (2.0, 1.8, -62.0), 30),
    "run3": ((4.0, 3.6, -70.0), (-2.0, 1.8, -92.0), 28),
    "run4": ((-2.0, -2.6, -132.0), (1.0, -5.2, -160.0), 28),
    "run5": ((0.5, -2.2, -192.0), (0.5, -3.0, -212.0), 26),
}

rnd = random.Random(7)


def noise(x, z):
    return (math.sin(x * 0.19 + 1.3) * 1.1 + math.cos(z * 0.15 + 0.4) * 0.9 + math.sin((x - z) * 0.08) * 1.6)


def outside(back=False):
    """The meadow round the gate. back=True: only what lies in front of the tear (seen from inside, through the
    way-out), without the gate's own debris."""
    b = K.Build(seed=3)
    R = 46
    path = []                               # the trodden path: from far off in +z to the gate's foot
    x = 6.0
    for z in range(44, 3, -1):
        x += math.sin(z * 0.21) * 0.35 - x * 0.04
        path.append((x, z))
    pathset = {}
    for px, pz in path:
        for dx in range(-2, 3):
            w = abs(dx) + rnd.uniform(-0.5, 0.6)
            pathset[(round(px + dx), pz)] = "path" if w < 1.4 else ("edge" if w < 2.3 else None)

    def ground(x, z):
        d = math.hypot(x, z)
        h = noise(x, z)
        flat = min(1.0, max(0.0, (d - 9) / 14))
        near_path = min((abs(x - px) + abs(z - pz) * 0.2 for px, pz in path), default=99)
        flat = min(flat, max(0.0, (near_path - 3) / 8) if near_path < 11 else flat)
        return round(h * flat * 0.8)

    # the apron the dungeon's floor bleeds into: a ragged blob under the tear
    def apron(x, z):
        a = math.atan2(z, x)
        r = 4.2 + 1.2 * math.sin(a * 3 + 0.7) + 0.7 * math.sin(a * 7 + 2.1) + rnd.uniform(-0.4, 0.4)
        return math.hypot(x * 0.85, z * 1.15) < r

    # the fissure: one jagged crack across the tear's foot (the tear stands on it)
    fis = {}
    for sgn in (-1, 1):
        x, z = 0, 0.0
        while abs(x) < 8:
            x += sgn
            if rnd.random() < 0.35:
                z += rnd.choice((-1, 1))
            z = max(-2, min(2, z))
            fis[(x, round(z))] = 1
    fis[(0, 0)] = 1
    # the floor either side buckled up toward it, in runs with gaps
    lips = {}
    for (fx, fz) in list(fis):
        for side, face in ((1, "north"), (-1, "south")):
            c = (fx, fz + side)
            if c not in fis and rnd.random() < 0.4:
                lips[c] = face
    puddles = {(-3, 2), (-4, 2), (-3, 3), (2, -3), (3, -3), (3, 3)}

    for x in range(-R, R):
        for z in range(-R, R + 12):
            if back and z < 1:
                continue
            g = ground(x, z)
            top = "minecraft:grass_block[snowy=false]"
            near = abs(x) < 11 and abs(z) < 11
            if near and apron(x, z):
                top = rnd.choice(("ashbound:cellar_flags",) * 5 + ("ashbound:cellar_brick", "ashbound:wet_cellar_brick"))
            elif near and math.hypot(x, z) < 7.5 and rnd.random() < 0.5:
                top = rnd.choice(("minecraft:coarse_dirt", "minecraft:coarse_dirt", "ashbound:cellar_silt", "minecraft:mud"))
            p = pathset.get((x, z))
            if p == "path":
                top = "minecraft:dirt_path"
            elif p == "edge" and rnd.random() < 0.6:
                top = rnd.choice(("minecraft:coarse_dirt", "minecraft:gravel", "minecraft:dirt_path"))
            for y in range(g - 4, g):
                b.put(x, y, z, "minecraft:dirt" if y > g - 3 else "minecraft:stone")
            if not back and near and (x, z) in fis:
                # a trench a block deep, its floor burning in the rank colour
                b.put(x, g - 1, z, None)
                b.put(x, g - 2, z, "minecraft:magma_block")
                continue
            if not back and near and (x, z) in puddles:
                b.put(x, g - 1, z, "minecraft:water[level=0]")
                continue
            b.put(x, g - 1, z, top)
            if not back and near and (x, z) in lips:
                if apron(x, z):
                    b.put(x, g, z, "ashbound:cellar_flag_stairs[facing=%s,half=bottom,shape=straight,waterlogged=false]" % lips[(x, z)])
                    continue
            if top.startswith("minecraft:grass") and rnd.random() < 0.28:
                b.put(x, g, z, rnd.choice(("minecraft:short_grass",) * 6 + ("minecraft:poppy", "minecraft:dandelion",
                                                                             "minecraft:cornflower", "minecraft:fern")))
    if not back:
        # a cask burst out of the floor, a tipped barrel, a heap of the vault's bricks
        b.put(-5, 0, 1, "minecraft:barrel[facing=east,open=true]")
        b.put(4, 0, -2, "ashbound:cellar_brick")
        b.put(4, 1, -2, "ashbound:cask_oak_slab[type=bottom,waterlogged=false]")
        b.put(5, 0, -2, "ashbound:cask_oak_slab[type=bottom,waterlogged=false]")
        b.put(4, 0, -3, "ashbound:wet_cellar_brick")
        b.fis = sorted(fis)
    # trees for scale, behind and to the sides
    for tx, tz in ((-17, -10), (-24, 6), (15, -16), (22, 3), (-9, -26), (9, -30), (-30, -20), (28, -24), (-20, 24), (24, 26), (-5, 27), (6, 33), (-13, 38), (14, 41)):
        if back and tz < 1:
            continue
        g = ground(tx, tz)
        hgt = rnd.randint(5, 7)
        for y in range(g, g + hgt):
            b.put(tx, y, tz, "minecraft:oak_log[axis=y]")
        for dx in range(-3, 4):
            for dz in range(-3, 4):
                for dy in range(hgt - 3, hgt + 2):
                    r = abs(dx) + abs(dz) + max(0, dy - hgt + 1) * 1.5
                    if r < 4.2 - rnd.random() * 0.8 and (dx or dz or dy >= hgt):
                        b.put(tx + dx, g + dy, tz + dz, "minecraft:oak_leaves[persistent=true,distance=1,waterlogged=false]")
    return b


def cellar(clip_z=None):
    blocks, pts = K.read_lair(LAIR)
    b = K.Build()
    for (x, y, z), st in blocks.items():
        if clip_z is not None and z > clip_z:
            continue
        b.put(x, y, z, st)
    return b, pts


def lamps(name, b):
    """The cellar's own lamps light it (structkit doesn't know them)."""
    L = [["lamp", x + 0.5, y + 0.5, z + 0.5] for (x, y, z), st in b.B.items() if st.startswith("ashbound:cellar_lamp")]
    with open(os.path.join(K.OUT, name + "_lights.json"), "w") as f:
        json.dump(L, f)


def add(a, r):
    return [a[0] + r[0], a[1] + r[1], a[2] + r[2]]


def rot180(o, r):
    return [o[0] - r[0], o[1] + r[1], o[2] - r[2]]


def main():
    # the shots each scene is rendered with; the comp script pairs them up
    out_shots, back_shots, in_shots, cel_shots = {}, {}, {}, {}
    for name, (cam, look, lens) in SHOTS.items():
        if name == "exit":
            # base: the boss vault looking at the way-out; through it, the world, seen from the gate looking out
            cel_shots["exit"] = (add(O_EXIT, cam), add(O_EXIT, look), lens)
            back_shots["exit"] = (rot180(O_OUT, cam), rot180(O_OUT, look), lens)
        else:
            out_shots[name] = (add(O_OUT, cam), add(O_OUT, look), lens)
            in_shots[name] = (add(O_IN, cam), add(O_IN, look), lens)
    for name, spec in RUN.items():
        cel_shots[name] = spec
    which = sys.argv[1:] or ["out", "back", "in", "cel"]
    if "out" in which:
        o = outside()
        K.preview(o, "gw_out", out_shots, sun=(9, -40), sky=(0.3, 0.33, 0.48))
        with open(os.path.join(K.OUT, "gw_out_lights.json"), "w") as f:
            json.dump([["fis", x + 0.5, -1.2, z + 0.5] for x, z in o.fis[::2]], f)
    if "back" in which:
        K.preview(outside(back=True), "gw_back", back_shots, sun=(9, -40), sky=(0.3, 0.33, 0.48))
    if "in" in which:
        b, _ = cellar(clip_z=O_IN[2] - 1.5)
        K.preview(b, "gw_in", in_shots, sun=(40, 0), sky=(0.01, 0.012, 0.02), night=False)
        lamps("gw_in", b)
    if "cel" in which:
        b, _ = cellar()
        K.preview(b, "gw_cel", cel_shots, sun=(40, 0), sky=(0.01, 0.012, 0.02), night=False)
        lamps("gw_cel", b)
    with open("E:/EFTest/game/tools/renders/gate/gw_shots.json", "w") as f:
        json.dump({"shots": SHOTS, "o_out": O_OUT, "o_in": O_IN, "o_exit": O_EXIT}, f, indent=1)
    print("ok")


if __name__ == "__main__":
    main()
