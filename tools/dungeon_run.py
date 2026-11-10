"""The camera's way through a whole dungeon for the intro's quick run (client/DungeonRun): a walkable route from its
arrival point ("tp") to its boss, found on the block file (seals opened), smoothed, at eye height, one point a block.

    python tools/dungeon_run.py [lair]      -> src/main/resources/data/ashbound/lair/<lair>_run.json
"""
import heapq
import json
import math
import os
import sys

sys.path.insert(0, "E:/Ashbound/tools")
import structkit as K  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# blocks you pass through (or wade): everything else stops you
SOFT = ("minecraft:water", "minecraft:iron_chain", "minecraft:red_carpet", "minecraft:light", "minecraft:cobweb")


def soft(st):
    return st is None or st.startswith(SOFT) or "carpet" in st or "_button" in st or "torch" in st


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "gate_cellar"
    K.ROOT = ROOT
    blocks, pts = K.read_lair(name)
    for k, p in pts.items():
        if k.startswith("seal:"):
            blocks.pop((math.floor(p[0]), math.floor(p[1]), math.floor(p[2])), None)

    def stand(x, y, z):
        below = blocks.get((x, y - 1, z))
        return (soft(blocks.get((x, y, z))) and soft(blocks.get((x, y + 1, z))) and soft(blocks.get((x, y + 2, z)))
                and below is not None and not below.startswith(("minecraft:iron_chain",)))

    def cell(p):
        x, y, z = math.floor(p[0]), math.floor(p[1]), math.floor(p[2])
        for dy in (0, 1, -1, 2, -2):
            if stand(x, y + dy, z):
                return (x, y + dy, z)
        raise SystemExit("no standing cell at %s" % (p,))
    start, goal = cell(pts["tp"]), cell(pts["boss"])
    # its monsters stand along the halls: the camera keeps this far off them (it went straight through them)
    mobs = [p for k, p in pts.items() if k.startswith("mob:")]
    CLEAR, WIDE = 1.6, 3.0

    def crowd(c):
        """how close the nearest monster is to this cell (blocks, across; only ones about level with it)"""
        x, y, z = c[0] + 0.5, c[1], c[2] + 0.5
        return min([math.hypot(m[0] - x, m[2] - z) for m in mobs if abs(m[1] - y) < 3] or [99])

    def near_wall(c):
        x, y, z = c
        return sum(not soft(blocks.get((x + dx, y + 1, z + dz))) for dx in (-1, 0, 1) for dz in (-1, 0, 1))

    # A*: a step costs more beside walls, so the route keeps to the middle of halls
    open_ = [(0, start)]
    came, cost = {start: None}, {start: 0}
    while open_:
        _, c = heapq.heappop(open_)
        if c == goal:
            break
        x, y, z = c
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            for dy in (0, 1, -1, -2, -3):
                n = (x + dx, y + dy, z + dz)
                if not stand(*n) or (crowd(n) < CLEAR and n != goal):
                    continue
                if dy > 0 and not soft(blocks.get((x, y + 3, z))):
                    continue
                step = math.sqrt(dx * dx + dz * dz) + abs(dy) * 0.5 + near_wall(n) * 0.35 + max(0, WIDE - crowd(n)) * 1.5
                nc = cost[c] + step
                if nc < cost.get(n, 1e18):
                    cost[n] = nc
                    came[n] = c
                    heapq.heappush(open_, (nc + abs(goal[0] - n[0]) + abs(goal[1] - n[1]) + abs(goal[2] - n[2]), n))
                break
    if goal not in came:
        raise SystemExit("no way from tp to the boss")
    path = []
    c = goal
    while c:
        path.append(c)
        c = came[c]
    path.reverse()
    pts3 = [(x + 0.5, y + 1.7, z + 0.5) for x, y, z in path]
    def clear(p):
        """the camera's head here: nothing solid round it, no monster on top of it"""
        for dx in (-0.3, 0.3):
            for dz in (-0.3, 0.3):
                for dy in (-0.3, 0.3):
                    if not soft(blocks.get((math.floor(p[0] + dx), math.floor(p[1] + dy), math.floor(p[2] + dz)))):
                        return False
        return min([math.hypot(m[0] - p[0], m[2] - p[2]) for m in mobs if abs(m[1] - (p[1] - 1.7)) < 3] or [99]) >= CLEAR

    def seen(a, b):
        return all(clear(tuple(a[k] + (b[k] - a[k]) * f / 4 for k in range(3))) for f in range(5))

    # smooth three times, but a point that smoothing would put in a wall or a monster (or cut a corner through one) stays put
    for _ in range(3):
        sm = list(pts3)
        for i in range(1, len(pts3) - 1):
            win = pts3[max(0, i - 4):i + 5]
            p = tuple(sum(q[k] for q in win) / len(win) for k in range(3))
            if clear(p) and seen(sm[i - 1], p):
                sm[i] = p
        pts3 = sm
    out, acc = [pts3[0]], 0.0
    for a, b in zip(pts3, pts3[1:]):
        d = math.dist(a, b)
        acc += d
        while acc >= 1.0:
            acc -= 1.0
            t = 1 - acc / d if d > 0 else 1
            out.append(tuple(a[k] + (b[k] - a[k]) * t for k in range(3)))
    out.append(pts3[-1])
    dst = os.path.join(ROOT, "src", "main", "resources", "data", "ashbound", "lair", name + "_run.json")
    with open(dst, "w") as f:
        json.dump({"path": [[round(v, 2) for v in p] for p in out]}, f)
    bad = sum(not clear(p) for p in out)
    near = min(min([math.hypot(m[0] - p[0], m[2] - p[2]) for m in mobs if abs(m[1] - (p[1] - 1.7)) < 3] or [99]) for p in out[:-8])
    print("route", len(out), "blocks ->", dst, "| points in a wall or a monster:", bad, "| nearest monster %.1f" % near)


if __name__ == "__main__":
    main()
