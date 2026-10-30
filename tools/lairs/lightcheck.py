"""How lit a gate dungeon is where people walk and fight. The gates dimension has no sky light and no ambient light,
so a block nothing lights is black. Spreads block light the way Minecraft does (15 at the source, one less per
step, full blocks stop it, water costs an extra step) over the ported bin, then reports the floor:

    dark  0-3  black in game         dim  4-7  shapes, no detail         lit  8+  a fight you can read

    python tools/lairs/lightcheck.py [gates...]        (the ported bins in src/main/resources/data/ashbound/lair)
    python tools/lairs/lightcheck.py cellar --bands     per 25-block stretch along the run, to find the dark spots

Each dungeon has a MOOD (efkit.MOOD) the numbers are judged against."""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(GAME, "tools"))
sys.path.insert(0, HERE)
from port_gate import read_bin  # noqa: E402

FEEL_LIGHT = {"minecraft:shroomlight": 15, "minecraft:sea_lantern": 15, "minecraft:glowstone": 15, "minecraft:magma_block": 3,
              "minecraft:amethyst_block": 0, "minecraft:jack_o_lantern": 15, "minecraft:ochre_froglight": 15}
VANILLA = {"lava": 15, "lantern": 15, "soul_lantern": 10, "torch": 14, "wall_torch": 14, "campfire": 15, "soul_campfire": 10,
           "fire": 15, "soul_fire": 10, "sea_lantern": 15, "glowstone": 15, "shroomlight": 15, "magma_block": 3}
OPAQUE_KINDS = ("full", "pillar")


def registry():
    r = json.load(open(os.path.join(GAME, "src/main/resources/ashbound/gate_blocks.json"), encoding="utf-8"))
    light, opaque = {}, set()
    for b in r["blocks"] + r["props"]:
        n = "ashbound:" + b["name"]
        lv = b.get("light", FEEL_LIGHT.get(b.get("feel"), 0))
        if lv:
            light[n] = lv
        if b in r["blocks"] and b["kind"] in OPAQUE_KINDS and lv == 0:
            opaque.add(n)
    return light, opaque


def measure(gate, bands=False):
    from efkit import MOOD
    light_of, opaque = registry()
    B, P = read_bin(os.path.join(GAME, "src/main/resources/data/ashbound/lair", "gate_%s.bin" % gate))
    name = {p: s.split("[")[0] for p, s in B.items()}

    def blocks_light(p):
        n = name.get(p)
        if n is None:
            return False
        short = n.split(":")[1]
        return n in opaque or short in ("bedrock", "stone") or (n.startswith("minecraft:") and short.endswith(("bricks", "_block", "planks", "stone")) and short not in VANILLA)

    L = {}
    buckets = collections.defaultdict(list)
    for p, n in name.items():
        lv = light_of.get(n, 0) or (VANILLA.get(n.split(":")[1], 0) if n.startswith("minecraft:") else 0)
        if lv:
            L[p] = lv
            buckets[lv].append(p)
    for lv in range(15, 1, -1):
        for p in buckets[lv]:
            if L.get(p, 0) != lv:
                continue
            for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
                q = (p[0] + d[0], p[1] + d[1], p[2] + d[2])
                if blocks_light(q):
                    continue
                nl = lv - (2 if name.get(q) == "minecraft:water" else 1)
                if nl > L.get(q, 0):
                    L[q] = nl
                    buckets[nl].append(q)

    def solid(p):
        n = name.get(p)
        return n is not None and n not in ("minecraft:water", "minecraft:lava") and "air" not in n

    walk = [(x, y + 1, z) for (x, y, z) in B if solid((x, y, z)) and not solid((x, y + 1, z)) and not solid((x, y + 2, z))
            and name.get((x, y + 1, z)) not in ("minecraft:lava", "minecraft:water") and any(solid((x, yy, z)) for yy in range(y + 3, y + 90))]
    # only the floor you can get to on foot from where the gate drops you (an open hill's bank tops don't count)
    W = set(walk)
    tp = P.get("tp")
    if tp:
        start = (int(tp[0] // 1), int(tp[1]), int(tp[2] // 1))
        seen, todo = {start} & W or {min(W, key=lambda q: (q[0] - start[0]) ** 2 + (q[1] - start[1]) ** 2 + (q[2] - start[2]) ** 2)}, []
        todo = list(seen)
        while todo:
            x, y, z = todo.pop()
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                for dy in (1, 0, -1, -2, -3):
                    q = (x + dx, y + dy, z + dz)
                    if q in W and q not in seen:
                        seen.add(q)
                        todo.append(q)
                        break
        walk = [q for q in walk if q in seen]
    lv = [L.get(p, 0) for p in walk]
    n = max(1, len(lv))
    dark = sum(v <= 3 for v in lv) / n
    dim = sum(4 <= v <= 7 for v in lv) / n
    lit = sum(v >= 8 for v in lv) / n
    spawns = [L.get((int(v[0] // 1), int(v[1]), int(v[2] // 1)), 0) for k, v in P.items() if k.startswith("mob:") or k == "boss"]
    mood = MOOD.get(gate, ("?", 0, 0))
    print("%-8s %-6s floor %5d  dark %3d%%  dim %3d%%  lit %3d%%  mean %4.1f   spawns dark %d/%d   target dark <= %d%%, lit >= %d%%" % (
        gate, mood[0], len(lv), dark * 100, dim * 100, lit * 100, sum(lv) / n, sum(s <= 3 for s in spawns), len(spawns), mood[1], mood[2]))
    if bands:
        for k, v in P.items():
            if (k.startswith("mob:") or k == "boss") and L.get((int(v[0] // 1), int(v[1]), int(v[2] // 1)), 0) <= 3:
                print("   dark spawn", k, tuple(int(c) for c in v))
        by = collections.defaultdict(list)
        for p, v in zip(walk, lv):
            by[p[2] // 25 * 25].append(v)
        for z in sorted(by, reverse=True):
            a = by[z]
            print("   z %5d..%5d  floor %5d  dark %3d%%  lit %3d%%" % (z + 24, z, len(a), 100 * sum(v <= 3 for v in a) / len(a), 100 * sum(v >= 8 for v in a) / len(a)))
    return dark, lit


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")] or "cellar gallows rotwood crypt plague foundry ossuary frost temple".split()
    for g in args:
        measure(g, "--bands" in sys.argv)
