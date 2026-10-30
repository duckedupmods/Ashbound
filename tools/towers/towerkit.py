"""What every world tower shares (the Clockwork Spire worked it out; the rest build on this): block-state helpers, the
inside stair flights that climb along alternate walls, the keep-out round them, rooms placed so they never block a
stair, the foremen and crews on every floor, light, coffers, the walk check, and the export into the game (template,
foot offset, marks for TowerSites.java, loot).

A tower module makes a Tower, builds its shell with t.put, then calls t.interior(...), t.lights(...), t.export().
"""
import json
import math
import os
import sys
from collections import deque

sys.path.insert(0, "E:/Ashbound/tools")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import structkit as K  # noqa: E402

A = "ashbound:"
GAME = "E:/EFTest/game/src/main/resources/"
FACE = ["east", "south", "west", "north"]
RAIL = dict(up="true", north="none", south="none", east="none", west="none", waterlogged="false")


def s(name, **p):
    n = name if ":" in name else A + name
    return n + ("[" + ",".join("%s=%s" % kv for kv in p.items()) + "]" if p else "")


def slab(name, half="bottom"):
    return s(name + "_slab", type=half, waterlogged="false")


def stairs(name, facing, half="bottom", shape="straight"):
    return s(name + "_stairs", facing=facing, half=half, shape=shape, waterlogged="false")


def wall(name):
    return s(name + "_wall", **RAIL)


def rot(x, z, q):
    for _ in range(q % 4):
        x, z = -z, x
    return x, z


def side_xy(side, along, out):
    return {"north": (along, -out), "south": (along, out), "east": (out, along), "west": (-out, along)}[side]


def opposite(side):
    return {"north": "south", "south": "north", "east": "west", "west": "east"}[side]


def oct_d(x, z):
    return max(abs(x), abs(z), (abs(x) + abs(z)) * 0.7071)


class Tower:
    """name: the structure (and its marks file); short: its loot tables' name (tower_<short>); gate: its gear.json
    entry; brick: the stair stem (<brick>_stairs, <brick>_wall) and fill: the solid under the steps; px: its props'
    prefix (<px>_lantern, <px>_chain, <px>_coffer, <px>_hoard); floors: each floor's walking level; deck: the roof's"""

    def __init__(self, name, short, gate, brick, fill, px, floors, deck, glow, goods=()):
        self.name, self.short, self.gate = name, short, gate
        self.brick, self.fill, self.px = brick, fill, px
        self.floors, self.deck, self.glow = floors, deck, glow
        self.goods = goods
        self.b = K.Build(7)
        self.marks = {"mobs": [], "foremen": [], "chests": [], "seals": [], "boss": None, "reward": None,
                      "hoard": px + "_hoard", "loot": "chests/tower_%s_boss" % short}
        self.guard = set()
        self.biomes = []
        self.origins = None       # each floor's centre (a tower whose stages lean); None: all at (0, 0)
        self.shift = (0, 0)       # while a room is built: its floor's centre

    # ---------------------------------------------------------------- putting blocks
    def origin(self, i):
        return self.origins[i] if self.origins else (0, 0)

    def put(self, x, y, z, st, nbt=None):
        x, z = x + self.shift[0], z + self.shift[1]
        if self.guard and (x, z) in self.guard and st is not None:
            return
        self.b.put(x, y, z, st, nbt)

    def get(self, x, y, z):
        return self.b.get(x, y, z)

    def lantern(self, hanging=False):
        return s(self.px + "_lantern", hanging="true" if hanging else "false", waterlogged="false")

    # ---------------------------------------------------------------- the stairs inside
    def side(self, i):
        """flights climb along the north wall eastward, then the south wall westward, and so on"""
        return 0 if i % 2 == 0 else 2

    def flight(self, f, q, steps, x0=-5, o=(0, 0)):
        """a straight stair three wide along a wall from floor f, turned q quarter-turns; the floor above opened over
        its upper part with a rail round the opening; a stringer and rail on its open side, lanterns on the rail"""
        put = self.b.put

        def rot(x, z, q_):
            for _ in range(q_ % 4):
                x, z = -z, x
            return x + o[0], z + o[1]
        for k in range(steps):
            for zz in (-6, -5, -4):
                x, z = rot(x0 + k, zz, q)
                for y in range(f, f + k):
                    put(x, y, z, s(self.fill))
                put(x, f + k, z, stairs(self.brick, FACE[q % 4]))
                for y in range(f + k + 1, f + k + 4):
                    put(x, y, z, None)
        top = f + steps
        for k in range(steps):
            x, z = rot(x0 + k, -3, q)
            for y in range(f, min(f + k, top - 2) + 1):
                put(x, y, z, s(self.fill))
            if f + k + 1 <= top - 2:
                put(x, f + k + 1, z, wall(self.brick))
                if k % 4 == 2 and f + k + 2 <= top - 3:
                    put(x, f + k + 2, z, self.lantern())
        for k in range(steps // 3, steps - 1):          # the last step is the upper floor's own level
            for zz in (-6, -5, -4):
                x, z = rot(x0 + k, zz, q)
                put(x, top - 1, z, None)
            x, z = rot(x0 + k, -3, q)
            put(x, top, z, wall(self.brick))
        for zz in (-6, -5, -4):
            x, z = rot(x0 + steps // 3 - 1, zz, q)
            put(x, top, z, wall(self.brick))

    def steps_of(self, i):
        f = self.floors[i]
        return (10, -5) if i < len(self.floors) - 1 else (self.deck - f, -5 - (self.deck - f - 10) // 2)

    def stair_cols(self, i):
        """the columns floor i's stair needs kept clear, and those round the opening it comes up through"""
        if i < 0:
            return set(), set()
        steps, x0 = self.steps_of(i)
        ox, oz = self.origin(i)
        own = {(a + ox, b + oz) for a, b in (rot(x0 + k, zz, self.side(i)) for k in range(-1, steps + 2) for zz in range(-7, -2))}
        above = {(a + ox, b + oz) for a, b in (rot(x0 + k, zz, self.side(i)) for k in range(steps // 3 - 2, steps + 3)
                                               for zz in range(-7, -1))}
        return own, above

    def keep(self, i):
        return self.stair_cols(i)[0] | (self.stair_cols(i - 1)[1] if i else set())

    def interior(self, rooms, crews, foremen, boss, reward, ring):
        """stairs on every floor, then each floor's room (kept off the stairs), its crew round a ring of radius
        ring(f), its foreman; the boss and its hoard's place on the roof"""
        for i, f in enumerate(self.floors):
            steps, x0 = self.steps_of(i)
            self.flight(f, self.side(i), steps, x0, self.origin(i))
        for i, f in enumerate(self.floors):
            self.guard = self.keep(i)
            self.shift = self.origin(i)
            try:
                rooms[i](self, f)
            finally:
                self.guard = set()
                self.shift = (0, 0)
            a = ring(f)
            ox, oz = self.origin(i)
            for k, kind in enumerate(crews[i]):
                ang = math.radians(60 + k * 70)
                self.marks["mobs"].append([round(math.cos(ang) * a) + ox, f, round(math.sin(ang) * a) + oz, kind])
            self.marks["foremen"].append([ox, f, round(a * 0.7) + oz, foremen[i]])
        self.marks["boss"] = list(boss)
        self.marks["reward"] = list(reward)

    def chest(self, x, y, z):
        self.marks["chests"].append([x + self.shift[0], y, z + self.shift[1]])

    # ---------------------------------------------------------------- light
    def floor_lights(self, inside, tiles, every=4, roof=None):
        """a glow block every few blocks in each floor slab (it lights the room and the ceiling under it), kept off
        the stairs, their openings and the middle; inside(x, z, f) says what's indoors; tiles: what a floor is made of"""
        for i, f in enumerate(self.floors):
            keep = self.keep(i)
            for x in range(-30, 31):
                for z in range(-30, 31):
                    if x % every != 2 or z % every != 2 or (x, z) in keep or max(abs(x), abs(z)) <= 1:
                        continue
                    under = str(self.b.get(x, f - 1, z))
                    if inside(x, z, f) and any(t in under for t in tiles) and self.b.get(x, f, z) is None:
                        self.b.put(x, f - 1, z, s(self.glow))
        if roof:
            for x in range(-30, 31):
                for z in range(-30, 31):
                    if x % 5 == 0 and z % 5 == 0 and roof(x, z) and max(abs(x), abs(z)) > 2 and \
                            any(t in str(self.b.get(x, self.deck - 1, z)) for t in tiles) and self.b.get(x, self.deck, z) is None:
                        self.b.put(x, self.deck - 1, z, s(self.glow))

    def hang_lanterns(self, r_of, n=8):
        """lanterns on chains under every ceiling round a ring, kept off the stairs"""
        for i, f in enumerate(self.floors):
            ceil = (self.floors[i + 1] - 1) if i + 1 < len(self.floors) else self.deck - 1
            keep = self.keep(i)
            r = r_of(f)
            ox, oz = self.origin(i)
            for k in range(n):
                ang = math.radians(180 / n + 360 / n * k)
                x, z = round(math.cos(ang) * r) + ox, round(math.sin(ang) * r) + oz
                if (x, z) in keep or self.b.get(x, ceil, z) is None or self.b.get(x, ceil - 1, z) is not None:
                    continue
                drop = 2 if ceil - f > 10 else 1
                for y in range(ceil - drop, ceil):
                    self.b.put(x, y, z, s(self.px + "_chain", axis="y", waterlogged="false"))
                self.b.put(x, ceil - drop - 1, z, self.lantern(True))

    # ---------------------------------------------------------------- checks
    def walk(self, start, reach=40):
        """can you walk from the door to the roof without jumping? (stairs climb a block; drops up to 3)"""
        B = self.b.B

        def free(x, y, z):
            st = B.get((x, y, z))
            return st is None or "cave_air" in st

        def stand(x, y, z):
            below = B.get((x, y - 1, z))
            return below is not None and "cave_air" not in below and "_wall" not in below and "minecraft:water" not in below \
                and free(x, y, z) and free(x, y + 1, z)

        seen, todo = {start}, deque([start])
        while todo:
            x, y, z = todo.popleft()
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, nz = x + dx, z + dz
                for ny in (y, y + 1, y - 1, y - 2, y - 3):
                    if ny == y + 1 and "_stairs" not in str(B.get((nx, y, nz))):
                        continue
                    if stand(nx, ny, nz) and abs(nx) < reach and abs(nz) < reach and (nx, ny, nz) not in seen:
                        seen.add((nx, ny, nz))
                        todo.append((nx, ny, nz))
                        break
        ok = True
        for f in self.floors + [self.deck]:
            got = any(p[1] == f for p in seen)
            ok &= got
            print("floor", f, "reached" if got else "NOT reached")
        return ok

    # ---------------------------------------------------------------- into the game
    def coffers(self):
        for x, y, z in self.marks["chests"]:
            if self.b.get(x, y, z) is None and self.b.get(x, y - 1, z) is not None:
                self.b.put(x, y, z, s(self.px + "_coffer", facing="north", waterlogged="false"),
                           {"LootTable": "ashbound:chests/tower_" + self.short})

    def hollow(self, inside, top):
        """cave air (the placer keeps it, unlike air) wherever inside(x, y, z) and nothing is built, so a hill the
        tower is set into is cut back instead of filling its rooms"""
        for y in range(0, top):
            for x in range(-34, 35):
                for z in range(-34, 35):
                    if (x, y, z) not in self.b.B and inside(x, y, z):
                        self.b.B[(x, y, z)] = "minecraft:cave_air"

    def export(self, hollow_inside, top):
        self.coffers()
        K.connect(self.b)
        self.hollow(hollow_inside, top)
        B = self.b.B
        ground = getattr(self, "_ground", "grass_block").split("[")[0]
        for q in [q for q, st in B.items() if "grass_block" in st or (q[1] == -1 and ground in st)]:
            del B[q]
        xs, ys, zs = zip(*B)
        mn = (min(xs), min(ys), min(zs))
        size = [max(xs) - mn[0] + 1, max(ys) - mn[1] + 1, max(zs) - mn[2] + 1]
        pal, idx, blocks = [], {}, []
        for p in sorted(B, key=lambda q: (q[1], q[2], q[0])):
            st = B[p]
            if st not in idx:
                idx[st] = len(pal)
                name_, props = K.parse(st)
                e = {"Name": name_}
                if props:
                    e["Properties"] = dict(props)
                pal.append(e)
            e = {"pos": [p[0] - mn[0], p[1] - mn[1], p[2] - mn[2]], "state": idx[st]}
            if p in self.b.nbt:
                e["nbt"] = self.b.nbt[p]
            blocks.append(e)
        root = {"DataVersion": 3955, "size": size, "palette": pal, "blocks": blocks, "entities": []}
        path = GAME + "data/ashbound/structure/tower/%s.nbt" % self.name
        os.makedirs(os.path.dirname(path), exist_ok=True)
        K.write_nbt(path, root)
        foot = [0 - mn[0], -1 - mn[1], 0 - mn[2]]       # the ground block under the door's axis
        op = GAME + "data/ashbound/tree/offsets.json"
        offs = json.load(open(op))
        offs[self.name] = foot
        json.dump(offs, open(op, "w"), indent=2)
        marks = dict(self.marks, foot="marks are in the tower's own frame: (0, 0, 0) stands on the ground block at the foot")
        mp = GAME + "data/ashbound/tower/%s.json" % self.name
        os.makedirs(os.path.dirname(mp), exist_ok=True)
        json.dump(marks, open(mp, "w"), indent=1)
        print("template", size, len(blocks), "blocks,", len(pal), "states,", os.path.getsize(path) // 1024, "KB; foot", foot)
        import towerloot
        towerloot.write(self.short, self.gate, goods=self.goods)
        self.structure()

    def structure(self):
        """its worldgen structure (placed by Trees.GiantTree) in the towers' set, in its biomes (self.biomes)"""
        tag = GAME + "data/ashbound/tags/worldgen/biome/has_structure/%s.json" % self.name
        json.dump({"replace": False, "values": [{"id": b, "required": False} for b in self.biomes]}, open(tag, "w"), indent=1)
        d = GAME + "data/ashbound/worldgen/"
        json.dump({"type": "ashbound:giant_tree", "template": "ashbound:tower/" + self.name, "spread": 6, "reach": 18, "tries": 13,
                   "biomes": "#ashbound:has_structure/" + self.name, "spawn_overrides": {}, "step": "surface_structures",
                   "terrain_adaptation": "none"}, open(d + "structure/%s.json" % self.name, "w"), indent=1)
        sp = d + "structure_set/towers.json"
        st = json.load(open(sp))
        names = [e["structure"] for e in st["structures"]]
        if "ashbound:" + self.name not in names:
            st["structures"].append({"structure": "ashbound:" + self.name, "weight": 1})
            json.dump(st, open(sp, "w"), indent=1)

    def ground(self, r=48, block="grass_block[snowy=false]"):
        self._ground = block
        for x in range(-r, r + 1):
            for z in range(-r, r + 1):
                if math.hypot(x, z) < r and self.b.get(x, -1, z) is None:
                    self.b.put(x, -1, z, block)
