"""The lair forge: a Roster v2 dungeon's layout built from its spec (tools/dforge.py, "layout") at Epic Fight scale,
the way the hand-made ones were (E:/Ashbound/tools/temple.py carving, structkit export), so every new dungeon is a
chain of rooms toward -z joined by walkable passes, one pass barred till the elite falls (the seal), side niches with
the coffers, lamps hung through it, the boss's arena last.

Room kinds:
    hall     a built room: walls, floor and vault in the dungeon's masonry, piers down both sides
    cave     a lumpy cavern, flat-floored
    round    a round arena (the boss's, usually): a ring of piers, tiers optional
    chasm    a cavern over a deep drop, a bridge 7 wide across it on piers
    descent  a broad stair down (or up) between two levels, framed
Passes between rooms: 7 wide, 7 tall, the floor stepping by stairs when the levels differ, bending sideways when
the rooms' centres do.

    python tools/lairs/forge_lair.py <gate> [shots...]     preview (blender -b -P E:/Ashbound/tools/blender/preview_struct.py -- gate_<gate> <shots>)
    python tools/lairs/forge_lair.py <gate> --game         stage it, then python tools/newgate.py <gate> lair
    OPEN_SEAL=1 ... reach7.py forge_lair <gate>             the walk check (reach7 takes a module + class or a gate)
"""
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import efkit  # noqa: E402
from efkit import K  # noqa: E402
import temple as T0  # noqa: E402

A = "ashbound:"
HALF = 3            # a pass is 7 wide: centre +-3
PASS_H = 7


def st(name, **props):
    """a block state string: our block (no namespace given) or a vanilla one"""
    n = name if ":" in name else A + name
    if not props:
        return n
    return n + "[" + ",".join("%s=%s" % kv for kv in sorted(props.items())) + "]"


class ForgeLair(T0.Temple):

    def __init__(self, gate, seed=7):
        super().__init__(seed=seed)
        import dforge
        self.gate = gate
        self.D = dforge.DUNGEONS[gate]
        # a dungeon's own block named "..._wall" (Titan Sinew Wall) is a full cube, not a wall to connect
        K.CUBE_WALLS.update(b["name"] for d in dforge.DUNGEONS.values() for b in d["blocks"] if b["name"].endswith("_wall"))
        self.L = self.D["layout"]
        self.pal = self.L["palette"]
        self.rooms = []           # built: dict(kind, cx, fl, z0, z1, w, ...)
        self.seal_cells = []

    # ---------------------------------------------------------------- palette

    def pick(self, key):
        opts = self.pal[key]
        if isinstance(opts, str):
            return st(opts)
        tot = sum(w for _, w in opts)
        r = self.r.random() * tot
        for b, w in opts:
            r -= w
            if r <= 0:
                return st(b)
        return st(opts[-1][0])

    def stairs(self, facing, half="bottom"):
        return st(self.pal["stairs"], facing=facing, half=half, shape="straight", waterlogged="false")

    def slab(self, t="bottom"):
        return st(self.pal["slab"], type=t, waterlogged="false")

    def lamp(self, hanging=True):
        return st(self.pal["lamp"], hanging="true" if hanging else "false", waterlogged="false")

    def chain(self, axis="y"):
        return st(self.pal["chain"], axis=axis, waterlogged="false")

    def bars(self, ew=True):
        return st(self.pal["bars"], east="true" if ew else "false", west="true" if ew else "false",
                  north="false" if ew else "true", south="false" if ew else "true", waterlogged="false")

    def pillar(self):
        return st(self.pal["pillar"], axis="y")

    def prop(self, name, facing=None):
        return st(name, facing=facing) if facing else st(name)

    # ---------------------------------------------------------------- carving the rooms

    def hall(self, R):
        cx, fl, z0, z1, w, h = R["cx"], R["fl"], R["z0"], R["z1"], R["w"], R["h"]
        x0, x1 = cx - w // 2, cx + w // 2
        self.room(x0, fl + 1, z0, x1, fl + h, z1, zone=R.get("zone", "hall"), vault=R.get("vault", 2))
        for x in range(x0, x1 + 1):
            for z in range(z1, z0 + 1):
                self.floor[(x, z)] = fl
        every = R.get("piers", 6)
        if every:
            for z in range(z0 - 3, z1 + 2, -every):           # piers down both walls, a beam across the vault
                for x in (x0, x1):
                    for y in range(fl + 1, fl + h + 1):
                        self.put(x, y, z, self.pillar())
                if R.get("beams", True):
                    for x in range(x0, x1 + 1):
                        self.put(x, fl + h + 1, z, self.pillar().replace("axis=y", "axis=x"))

    def cave(self, R):
        cx, fl, z0, z1, w, h = R["cx"], R["fl"], R["z0"], R["z1"], R["w"], R["h"]
        zc = (z0 + z1) / 2
        self.blob((cx, fl + h * 0.45, zc), w / 2, h / 2 + 1, (z0 - z1) / 2 + 1, fl, zone=R.get("zone", "cave"),
                  rough=R.get("rough", 0.14))
        for z in range(z1, z0 + 1):                 # a walkway the whole length (the blob pinches in at its ends)
            for x in range(cx - HALF, cx + HALF + 1):
                for y in range(fl + 1, fl + PASS_H + 1):
                    self.carve((x, y, z), R.get("zone", "cave"))
                self.floor[(x, z)] = fl

    def round(self, R):
        cx, fl, z0, z1, w, h = R["cx"], R["fl"], R["z0"], R["z1"], R["w"], R["h"]
        rad = w / 2
        cz = (z0 + z1) / 2
        zone = R.get("zone", "arena")
        for x in range(int(cx - rad) - 1, int(cx + rad) + 2):
            for z in range(int(cz - rad) - 1, int(cz + rad) + 2):
                d = math.hypot(x - cx, z - cz)
                if d <= rad + 0.3:
                    top = fl + h - int(max(0, d - rad * 0.55) * 0.6)      # a dome
                    for y in range(fl + 1, top + 1):
                        self.carve((x, y, z), zone)
                    self.floor[(x, z)] = fl
        for z in range(z1, z0 + 1):                 # the way in and on
            for x in range(cx - HALF, cx + HALF + 1):
                if abs(z - cz) > rad - 2:
                    for y in range(fl + 1, fl + PASS_H + 1):
                        self.carve((x, y, z), zone)
                    self.floor[(x, z)] = fl
        n = R.get("ring", 10)
        for k in range(n):                           # a ring of piers inside the wall
            a = k * 2 * math.pi / n + math.pi / n
            px, pz = int(round(cx + (rad - 2.5) * math.sin(a))), int(round(cz + (rad - 2.5) * math.cos(a)))
            if abs(px - cx) <= HALF + 1 and abs(abs(pz - cz) - rad) < 4:
                continue
            for y in range(fl + 1, fl + h - 2):
                self.put(px, y, pz, self.pillar())

    def chasm(self, R):
        cx, fl, z0, z1, w, h = R["cx"], R["fl"], R["z0"], R["z1"], R["w"], R["h"]
        drop = R.get("drop", 24)
        zc = (z0 + z1) / 2
        zone = R.get("zone", "cave")
        before = set(self.air)
        self.blob((cx, fl - drop / 2 + h / 3, zc), w / 2, (drop + h) / 2, (z0 - z1) / 2 + 1, fl - drop, zone=zone, rough=0.16)
        for (x, y, z) in self.air - before:         # nothing of this drop past the bridge's ends (other rooms untouched)
            if y <= fl and not (z1 + 1 <= z <= z0 - 1):
                self.air.discard((x, y, z))
                del self.zone[(x, y, z)]
        B = self.b.B
        for z in range(z1, z0 + 1):
            for x in range(cx - HALF, cx + HALF + 1):
                B[(x, fl, z)] = self.pick("bridge")
                B[(x, fl - 1, z)] = self.slab("top")
                self.floor[(x, z)] = fl
                for y in range(fl + 1, fl + PASS_H + 1):
                    self.carve((x, y, z), zone)
            for x in (cx - HALF - 1, cx + HALF + 1):
                B[(x, fl, z)] = self.pick("bridge")
                B[(x, fl + 1, z)] = st(self.pal["rail"], east="none", west="none", north="low", south="low", up="true", waterlogged="false") \
                    if self.r.random() < 0.8 else self.pick("bridge")
        for z in range(z0 - 4, z1 + 2, -7):           # piers down to the floor of the drop
            for x in (cx - HALF - 1, cx + HALF + 1):
                for y in range(fl - drop, fl):
                    B[(x, y, z)] = self.pillar()
                B[(x, fl + 1, z)] = self.pick("bridge")
                B[(x, fl + 2, z)] = self.lamp(False)
        R["drop_floor"] = fl - drop

    def descent(self, R):
        """a broad framed stair from fl down to fl2 (R['to']), 7 wide, along -z"""
        cx, fl, z0, fl2 = R["cx"], R["fl"], R["z0"], R["to"]
        dy = fl - fl2
        steps = abs(dy)
        zone = R.get("zone", "hall")
        B = self.b.B
        z = z0
        for k in range(R.get("landing", 3)):
            for x in range(cx - HALF, cx + HALF + 1):
                for y in range(fl + 1, fl + PASS_H + 2):
                    self.carve((x, y, z), zone)
                self.floor[(x, z)] = fl
            z -= 1
        y = fl
        for k in range(steps):
            if dy > 0:                       # down toward -z: each stair sits at the floor it leaves, rising to the south
                sy, face, y = y, "south", y - 1
            else:                            # up toward -z: each stair one above the last, rising to the north
                y += 1
                sy, face = y, "north"
            for x in range(cx - HALF, cx + HALF + 1):
                for yy in range(sy + 1, sy + PASS_H + 2):
                    self.carve((x, yy, z), zone)
                    B.pop((x, yy, z), None)
                B[(x, sy, z)] = self.stairs(face)
                self.floor[(x, z)] = sy
            if k % 4 == 0:
                for x in (cx - HALF - 1, cx + HALF + 1):
                    for yy in range(sy, sy + PASS_H + 1):
                        B[(x, yy, z)] = self.pillar()
            z -= 1
        for k in range(R.get("landing", 3)):
            for x in range(cx - HALF, cx + HALF + 1):
                for yy in range(fl2 + 1, fl2 + PASS_H + 2):
                    self.carve((x, yy, z), zone)
                self.floor[(x, z)] = fl2
            z -= 1
        R["z1"] = z + 1
        R["fl_out"] = fl2

    def passage(self, a, b, zone):
        """a pass from room a's far end to room b's near end: straight, bent sideways if their centres differ"""
        xa, fa, za = a["cx"], a.get("fl_out", a["fl"]), a["z1"]
        xb, fb, zb = b["cx"], b["fl"], b["z0"]
        zm = (za + zb) // 2
        B = self.b.B

        def cut(x, z, fl):
            for dx in range(-HALF, HALF + 1):
                for y in range(fl + 1, fl + PASS_H + 1):
                    self.carve((x + dx, y, z), zone)
                    if B.get((x + dx, y, z)) and "stairs" not in B[(x + dx, y, z)]:
                        B.pop((x + dx, y, z), None)
                if (x + dx, z) not in self.floor:
                    self.floor[(x + dx, z)] = fl
        for z in range(zm, za + 1):
            cut(xa, z, fa)
        for x in range(min(xa, xb), max(xa, xb) + 1):
            cut(x, zm, fa)
            cut(x, zm + 1, fa)
            cut(x, zm - 1, fa)
        for z in range(zb, zm + 1):
            cut(xb, z, fa)
        if fb != fa:
            raise SystemExit("rooms %s -> %s differ in floor; put a descent between them" % (a.get("name"), b.get("name")))

    # ---------------------------------------------------------------- dressing

    def floor_cells(self, R, margin=1, avoid_path=False):
        cells = []
        for (x, z), fl in self.floor.items():
            if fl != R.get("fl_out", R["fl"]) and fl != R["fl"]:
                continue
            if not (R["z1"] + margin <= z <= R["z0"] - margin):
                continue
            if abs(x - R["cx"]) > R["w"] // 2 - margin:
                continue
            if avoid_path and abs(x - R["cx"]) <= HALF:
                continue
            if all((x, fl + k, z) in self.air for k in (1, 2, 3)) and self.b.B.get((x, fl + 1, z)) is None                     and (x, fl, z) not in self.air:
                cells.append((x, fl, z))
        self.r.shuffle(cells)
        return cells

    def scatter(self, R, name, n, facing=None, avoid_path=True, spacing=3, wall_only=False):
        placed = []
        for (x, fl, z) in self.floor_cells(R, avoid_path=avoid_path):
            if len(placed) >= n:
                break
            if any(abs(x - px) < spacing and abs(z - pz) < spacing for px, pz in placed):
                continue
            if wall_only and all((x + dx, fl + 1, z + dz) in self.air for dx, dz in ((2, 0), (-2, 0), (0, 2), (0, -2))):
                continue
            kind = {p["name"]: p["kind"] for p in self.D.get("props", [])}.get(name)
            if kind in ("facing", "coffer"):
                f = facing if facing not in (None, "none") else self.r.choice(("north", "south", "east", "west"))
                self.put(x, fl + 1, z, self.prop(name, f))
            else:
                self.put(x, fl + 1, z, st(name))
            placed.append((x, z))
        return placed

    def clusters(self, R, name, chance=0.02):
        """a prop grown out of the floor at the walls (crystals, fungus, bones)"""
        for (x, fl, z) in self.floor_cells(R, avoid_path=True):
            near_wall = any((x + dx, fl + 1, z + dz) not in self.air for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            if near_wall and self.r.random() < chance * 8:
                self.put(x, fl + 1, z, st(name))

    def pools(self, R, n=4, size=3, liquid="water"):
        """sunk pools in the floor off the walkway: the floor block itself turned to water (or lava)"""
        cells = self.floor_cells(R, margin=2, avoid_path=True)
        for (x, fl, z) in cells[:n]:
            for dx in range(-size, size + 1):
                for dz in range(-size, size + 1):
                    q = (x + dx, z + dz)
                    if dx * dx + dz * dz > size * size + 1 or abs(x + dx - R["cx"]) <= HALF + 1 or self.floor.get(q) != fl:
                        continue
                    if (x + dx, fl + 1, z + dz) in self.air and self.b.B.get((x + dx, fl + 1, z + dz)) is None:
                        self.put(x + dx, fl, z + dz, liquid if ":" in liquid else "minecraft:" + liquid)

    def rails(self, R, name):
        for (x, z), fl in list(self.floor.items()):
            if x == R["cx"] + 2 and R["z1"] <= z <= R["z0"] and fl == R["fl"] and self.b.B.get((x, fl + 1, z)) is None:
                self.put(x, fl + 1, z, st(name, facing="north"))

    def frames(self, R, every=5):
        """timber or stone frames across a room or cave: posts on the walls, a lintel over the way"""
        cx, fl = R["cx"], R["fl"]
        h = min(R["h"], 8)
        for z in range(R["z0"] - 2, R["z1"] + 1, -every):
            xs = [x for x in range(cx - R["w"] // 2, cx + R["w"] // 2 + 1) if (x, fl + 1, z) in self.air]
            if not xs:
                continue
            lo, hi = min(xs), max(xs)
            if hi - lo < 6:
                continue
            for x in (lo, hi):
                for y in range(fl + 1, fl + h):
                    self.put(x, y, z, self.pillar())
            for x in range(lo, hi + 1):
                if (x, fl + h, z) in self.air:
                    self.put(x, fl + h, z, self.pillar().replace("axis=y", "axis=x"))
            for x in (lo, hi):
                for y in range(fl + h, fl + h + 6):
                    if (x, y, z) in self.air:
                        self.put(x, y, z, self.pillar())
                    else:
                        break

    def veins(self, chance=0.05):
        """after the skin: some cave wall turned to the glowing seam"""
        if "vein" not in self.pal:
            return
        B = self.b.B
        for (x, y, z) in self.air:
            if self.zone[(x, y, z)] not in ("cave", "chasm"):
                continue
            for d in ((1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1), (0, 1, 0)):
                q = (x + d[0], y + d[1], z + d[2])
                if q not in self.air and q in B and self.r.random() < chance and B[q] in self.wall_set:
                    B[q] = st(self.pal["vein"])

    # ---------------------------------------------------------------- the skin

    def skin(self):
        B = self.b.B
        z_of = {}
        for key in ("hall", "cave", "arena"):
            z_of[key] = (self.pal.get(key + "_floor", self.pal.get("hall_floor")), self.pal.get(key + "_wall", self.pal.get("hall_wall")),
                         self.pal.get(key + "_ceil", self.pal.get(key + "_wall", self.pal.get("hall_wall"))))
        self.wall_set = set()
        for (x, y, z) in self.air:
            zn = self.zone[(x, y, z)]
            fl, wl, cl = z_of.get(zn, z_of["cave" if zn in ("chasm",) else "hall"])
            for d in ((1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1), (0, 1, 0), (0, -1, 0)):
                q = (x + d[0], y + d[1], z + d[2])
                if B.get(q) != "rock":
                    continue
                key = fl if d[1] == -1 else (cl if d[1] == 1 else wl)
                s = self._pick(key)
                B[q] = s
                if d[1] == 0:
                    self.wall_set.add(s)
        for p, s in list(B.items()):
            if s == "rock":
                B[p] = st(self.pal["fill"])

    def _pick(self, opts):
        if isinstance(opts, str):
            return st(opts)
        tot = sum(w for _, w in opts)
        r = self.r.random() * tot
        for b, w in opts:
            r -= w
            if r <= 0:
                return st(b)
        return st(opts[-1][0])

    # ---------------------------------------------------------------- the whole run

    def build(self):
        L = self.L
        z = 0
        prev = None
        for i, spec in enumerate(L["rooms"]):
            R = dict(spec)
            R.setdefault("cx", 0)
            R.setdefault("w", 21)
            R.setdefault("h", 12)
            R["fl"] = prev.get("fl_out", prev["fl"]) if prev and "fl" not in spec else spec.get("fl", 0)
            gap = 0 if i == 0 else R.get("gap", 8)
            R["z0"] = z - gap
            if R["kind"] != "descent":
                R["z1"] = R["z0"] - R["len"]
            getattr(self, R["kind"])(R)
            if prev is not None:
                self.passage(prev, R, R.get("pass_zone", "hall"))
                if i == L.get("seal"):
                    self.seal(prev, R)
            self.rooms.append(R)
            prev = R
            z = R["z1"]
        first, last = self.rooms[0], self.rooms[-1]
        self.marks["tp"] = (first["cx"] + 0.5, float(first["fl"] + 1), first["z0"] - 3.5)
        bz = (last["z0"] + last["z1"]) / 2
        self.marks["boss"] = (last["cx"] + 0.5, float(last["fl"] + 1), last["z1"] + last["w"] * 0.18 + 2.5)
        self.marks["exit"] = (last["cx"] + 0.5, float(last["fl"] + 1), bz + 0.5)
        for R in self.rooms:
            self.dress(R)
        self.coffers()
        self.populate()
        lamp = self.lamp(True)
        efkit.hang_grid(self, {"hall", "cave", "arena", "chasm"}, lamp, self.chain(), every=L.get("lamp_every", 6),
                        height=L.get("lamp_height", 6), phase=(3, 2))
        dressing = dict(self.b.B)
        self.shell()
        self.b.B.update(dressing)
        self.skin()
        self.veins(L.get("veins", 0.04))
        for p in self.air:
            if self.b.B.get(p) == "air":
                del self.b.B[p]
        return self.b

    def seal(self, a, b):
        """bars across the pass into room b, opened when the key-holder falls"""
        x, fl, z = b["cx"], b["fl"], b["z0"] + 1
        B = self.b.B
        cells = []
        for dx in range(-HALF, HALF + 1):
            for y in range(fl + 1, fl + PASS_H + 1):
                self.carve((x + dx, y, z), "hall")
                if not os.environ.get("OPEN_SEAL"):
                    B[(x + dx, y, z)] = self.bars(True)
                cells.append((x + dx, y, z))
        for y in range(fl + 1, fl + PASS_H + 2):        # a gate frame in the masonry
            for dx in (-HALF - 1, HALF + 1):
                B[(x + dx, y, z)] = self.pillar()
        for dx in range(-HALF - 1, HALF + 2):
            B[(x + dx, fl + PASS_H + 1, z)] = self.pillar().replace("axis=y", "axis=x")
        self.marks["seal"] = cells

    def dress(self, R):
        for d in R.get("dress", ()):
            kind, arg = (d, {}) if isinstance(d, str) else (d[0], d[1] if len(d) > 1 else {})
            if kind == "frames":
                self.frames(R, **arg)
            elif kind == "rails":
                self.rails(R, self.L["rail_prop"])
            elif kind == "scatter":
                self.scatter(R, **arg)
            elif kind == "clusters":
                self.clusters(R, **arg)
            elif kind == "pools":
                self.pools(R, **arg)

    def coffers(self):
        """niches off the side of some rooms, a coffer at the back of each"""
        for i, R in enumerate(self.rooms):
            if not R.get("chest"):
                continue
            side = 1 if i % 2 else -1
            zc = (R["z0"] + R["z1"]) // 2
            wall = R["cx"]                       # out from the middle to wherever this room's wall really is
            while (wall + side, R["fl"] + 1, zc) in self.air:
                wall += side
            for dx in range(1, 6):
                for dz in range(-2, 3):
                    for y in range(R["fl"] + 1, R["fl"] + 5):
                        self.carve((wall + side * dx, y, zc + dz), R.get("zone", "hall") if R["kind"] != "chasm" else "cave")
                    self.floor[(wall + side * dx, zc + dz)] = R["fl"]
            self.chest(wall + side * 5, R["fl"] + 1, zc, "west" if side > 0 else "east")
            self.b.B[(wall + side * 5, R["fl"] + 1, zc)] = st(self.pal["coffer"], facing="west" if side > 0 else "east")
            self.b.B[(wall + side * 4, R["fl"] + 4, zc)] = self.lamp(True)

    def populate(self):
        for i, R in enumerate(self.rooms):
            for (mid, n) in R.get("mobs", ()):
                cells = self.floor_cells(R, margin=2)
                placed = []
                for (x, fl, z) in cells:
                    if len(placed) >= n:
                        break
                    if any(abs(x - px) < 3 and abs(z - pz) < 3 for px, pz in placed):
                        continue
                    self.mob(A + mid, x, fl + 1, z, yaw=0)
                    placed.append((x, z))
            if R.get("elite"):
                zc = R["z1"] + 4
                self.mob(A + R["elite"], R["cx"], R["fl"] + 1, zc, yaw=0)
            if R.get("decor"):
                for (mid, n) in R["decor"]:
                    for (x, fl, z) in self.floor_cells(R, margin=2, avoid_path=True)[:n]:
                        self.mob(A + mid, x, fl + 1, z, yaw=self.r.choice((0, 90, 180, 270)), decor=True)


def points(t):
    pts = {"tp": t.marks["tp"], "boss": t.marks["boss"], "exit": t.marks["exit"]}
    for i, (kind, p, yaw, decor) in enumerate(t.marks["mobs"]):
        key = "mob:%s:%d" % (kind, i)
        if yaw is not None:
            key += "@%d" % yaw
            if decor:
                key += "!"
        pts[key] = p
    for i, p in enumerate(t.marks["loot"]):
        pts["loot:%d" % i] = p
    for i, p in enumerate(t.marks.get("seal", [])):
        pts["seal:%d" % i] = p
    return pts


ORIGINS = {}   # gate -> x of its test origin (each lair has its own stretch of the gates dimension)


def export(T, b):
    """stage the bin and write its meta (no old dungeon to copy one from)"""
    import gear_meta
    name = "gate_" + T.gate
    root = K.ROOT
    K.ROOT = efkit.STAGE
    try:
        K.export_lair(b, name, points(T))
    finally:
        K.ROOT = root
    d = os.path.join(efkit.STAGE, "src/main/resources/data/ashbound/lair")
    meta = gear_meta.meta(T.gate)
    hits = sorted(p for p, s in b.B.items() if s.split("[")[0] == st(T.pal["fill"]))
    meta["built_check"] = [[hits[0][0], hits[0][1], hits[0][2], st(T.pal["fill"])]]
    meta["clear_top"] = max(p[1] for p in b.B) + 2
    json.dump(meta, open(os.path.join(d, name + ".json"), "w", encoding="utf-8"), indent=1)
    print("staged", name, "clear_top", meta["clear_top"])


def shots(T):
    out = {}
    for i, R in enumerate(T.rooms):
        z0 = R["z0"] - 2
        out["r%d" % i] = ((R["cx"], R["fl"] + 4.5, z0), (R["cx"], R["fl"] + 2, R["z1"]), 14)
    return out


if __name__ == "__main__":
    gate = sys.argv[1]
    T = ForgeLair(gate, seed=int(os.environ.get("SEED", "7")))
    b = T.build()
    print("blocks", len(b.B), "mobs", len(T.marks["mobs"]), "chests", len(T.marks["loot"]), "rooms", len(T.rooms))
    if "--game" in sys.argv:
        export(T, b)
        sys.exit(0)
    # the previewer draws blocks, not our prop meshes: stand vanilla look-alikes in for them
    STAND = {"lantern": "lantern[hanging=true,waterlogged=false]", "chain": "chain[axis=y,waterlogged=false]",
             "bars": "iron_bars[east=true,north=false,south=false,waterlogged=false,west=true]", "coffer": "chest[facing=north,type=single,waterlogged=false]",
             "facing": "barrel[facing=up,open=false]", "plain": "amethyst_cluster[facing=up,waterlogged=false]"}
    kinds = {A + p["name"]: p["kind"] for p in T.D.get("props", [])}
    for q, s in list(b.B.items()):
        k = kinds.get(s.split("[")[0])
        if k:
            b.B[q] = STAND.get(k, "barrel[facing=up,open=false]")
    S = shots(T)
    want = sys.argv[2:]
    S = {k: v for k, v in S.items() if not want or k in want}
    K.preview(b, "gate_" + gate, S, sun=(30, -30), sky=(0.02, 0.02, 0.03), night=True, fog=0.004)
