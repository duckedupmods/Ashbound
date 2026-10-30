"""The Rotwood rebuilt at Epic Fight scale: the same walk north through the dead wood as the old one
(E:/Ashbound/tools/rotwood.py has the story). The rows, the shelfwood and the hollow already had room; the two fights
with the big ones didn't:

    6  the antler glade      radius 16 (was 12) for the 3.8-tall Rot Stag, the Root Gate 7 wide
    7  the mossking's court  radius 22 (was 18), 30 tall, for the 8-tall Mossking; the throne pushed back

    python tools/lairs/rotwood_ef.py [shots]     preview (blender -b -P E:/Ashbound/tools/blender/preview_struct.py -- gate_rotwood_ef <shots>)
    python tools/lairs/rotwood_ef.py --game      stage the bin, then python tools/port_gate.py rotwood lair
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import efkit  # noqa: E402
from efkit import K  # noqa: E402
import rotwood as R0  # noqa: E402
from rotwood import A, RBARK, SHELF, GCAP, SMOSS, stairs, slab  # noqa: E402

F_GLADE = R0.F_GLADE
GLADE_Z, GLADE_R = -219, 16
COURT_Z, COURT_R = -265, 22


class RotwoodEF(R0.Rotwood):

    def glade(self):
        """6: the antler glade, radius 16, ringed with standing stones; the Rot Stag; the Root Gate north, 7 wide."""
        F = F_GLADE
        cz, R = GLADE_Z, GLADE_R
        for x in range(-R, R + 1):
            for z in range(cz - R, cz + R + 1):
                if math.hypot(x, z - cz) <= R + 0.3:
                    self.area(x, z, x, z, F, 16, "glade")
        self.area(-3, cz + R, 3, -202, F, 9, "glade")              # joined to the gully's head
        for k in range(11):
            a = k * 2 * math.pi / 11 + 0.3
            x, z = int(round(12.5 * math.cos(a))), int(round(cz + 12.5 * math.sin(a)))
            if abs(x) <= 3:
                continue
            h = 3 + (k * 7) % 3
            for y in range(F + 1, F + 1 + h):
                self.put(x, y, z, R0.GSTONE)
            self.put(x, F + 1 + h, z, slab(block=A + "glade_stone_slab"))
            self.put(x + (1 if x > 0 else -1), F + 1, z, SMOSS)
            self.put(x, F + 2 + h, z, GCAP)                         # a glowcap grown on every stone's top
        for (x, z) in ((-4, cz + 5), (5, cz - 4), (0, cz - 9), (-8, cz - 5), (8, cz + 6), (-9, cz + 8), (3, cz + 10),
                       (-2, cz), (9, cz - 9), (-12, cz - 2)):
            self.put(x, F + 1, z, GCAP)
        self.mob(A + "rot_stag", 0, F + 1, cz - 2, yaw=0)
        self.chest(-14, F + 1, cz - 4, "east")
        self.area(-3, cz - R - 1, 3, cz - R - 6, F, 8, "glade")
        seal = []
        z = cz - R - 3
        for x in range(-3, 4):
            for y in range(F + 1, F + 7):
                if not os.environ.get("OPEN_SEAL"):
                    self.put(x, y, z, R0.RWALL)
                seal.append((x, y, z))
        for sx in (-4, 4):
            for y in range(F + 1, F + 9):
                self.put(sx, y, z, RBARK)
        for x in range(-4, 5):
            self.put(x, F + 7, z, RBARK)
            self.put(x, F + 8, z, RBARK if abs(x) < 4 else None)
        self.marks["seal"] = seal

    def court(self):
        """7: the mossking's court, radius 22: fallen giants round the edge, the throne stump at the north."""
        F = F_GLADE
        cz, R = COURT_Z, COURT_R
        for x in range(-R, R + 1):
            for z in range(cz - R, cz + R + 1):
                if math.hypot(x, z - cz) <= R + 0.3:
                    self.area(x, z, x, z, F, 30, "arena")
        self.area(-3, GLADE_Z - GLADE_R - 6, 3, cz + R, F, 9, "arena")
        for (a0, ln) in ((0.5, 15), (1.9, 12), (3.6, 13), (5.0, 11)):
            for k in range(ln):
                a = a0 + k / 19.5
                x, z = int(round(19.5 * math.cos(a))), int(round(cz + 19.5 * math.sin(a)))
                for dy in (1, 2, 3):
                    self.put(x, F + dy, z, RBARK)
                if k % 3 == 1:
                    self.put(x, F + 4, z, SHELF if k % 2 else GCAP)
        tz = cz - 15
        for x in range(-6, 7):
            for z in range(tz - 6, tz + 5):
                if math.hypot(x, (z - tz) * 1.1) > 6.3:
                    continue
                for y in range(F + 1, F + 9 - (1 if abs(x) > 4 else 0)):
                    seat = abs(x) <= 1 and z >= tz + 2 and y >= F + 3
                    if not seat:
                        self.put(x, y, z, RBARK)
        for x in (-1, 0, 1):
            self.put(x, F + 3, tz + 2, stairs("north", block=A + "rotwood_plank_stairs"))
        for (sx, h) in ((-4, 4), (4, 4), (-2, 3), (2, 3)):
            for y in range(F + 9, F + 9 + h):
                self.put(sx, y, tz - 2, RBARK)
        for k in range(6):
            a = math.pi * 0.15 + k * math.pi * 0.14
            self.line((6 * math.cos(a), F + 1, tz + 6 * math.sin(a) * 0.2), (13 * math.cos(a), F + 1, tz + 13 * math.sin(a) * 0.4), RBARK)
        for (x, z) in ((-7, tz + 3), (7, tz + 3), (-12, cz + 8), (12, cz + 9), (-15, cz - 3), (15, cz - 4),
                       (-4, tz + 6), (4, tz + 6), (-2, tz + 4), (2, tz + 4), (-8, cz + 14), (8, cz + 15), (0, cz + 6),
                       (-10, cz), (10, cz + 1), (-5, cz - 6), (6, cz - 7)):
            self.put(x, F + 1, z, GCAP)
        for (x, y, z) in ((-5, F + 5, tz + 3), (5, F + 6, tz + 3), (-3, F + 7, tz + 5), (3, F + 4, tz + 5), (0, F + 8, tz + 5),
                          (-6, F + 3, tz), (6, F + 4, tz - 1)):
            if self.b.B.get((x, y, z)) == RBARK:
                self.put(x, y, z, GCAP)
        for (x, z, h) in ((-12, cz + 9, 15), (13, cz + 5, 14), (-15, cz - 8, 13), (15, cz - 9, 12)):
            self.giant_cap(x, F, z, h, 4)
        self.marks["boss"] = (0.5, float(F + 1), cz - 5.5)
        self.marks["exit"] = (0.5, float(F + 1), cz - 9.5)


    def build(self):
        self.colzone = {}
        self.camp()
        self.grey_rows()
        self.shelfwood()
        self.ravine()
        self.hollow()
        self.gully()
        self.glade()
        self.court()
        # the wood's own light: glowcaps sprung up wherever the ground's open and dark
        cap = lambda x, fl, z: self.put(x, fl + 1, z, GCAP)  # noqa: E731
        efkit.light_grid(self, {"camp", "glade", "hollow"}, cap, every=6, keep_clear=lambda x, z: abs(x) <= 1, phase=(2, 1))
        efkit.light_grid(self, {"gully"}, cap, every=4, keep_clear=lambda x, z: abs(x) <= 1, phase=(3, 0))
        efkit.light_grid(self, {"gully"}, cap, every=4, keep_clear=lambda x, z: abs(x) <= 1, phase=(1, 2))
        efkit.light_grid(self, {"arena"}, cap, every=7, keep_clear=lambda x, z: abs(x) <= 2, phase=(3, 3))
        dressing = dict(self.b.B)
        self.shell()
        self.b.B.update(dressing)
        self.open_sky()
        self.skin()
        for p in self.air:
            if self.b.B.get(p) in ("air", R0.RLOAM) and p not in dressing:
                del self.b.B[p]
        return self.b


SHOTS = dict(R0.SHOTS)
SHOTS.update({"glade": ((0, 21, -202), (0, 15, -228), 15), "arena": ((0, 24, -241), (0, 18, -278), 17)})

if __name__ == "__main__":
    T = RotwoodEF(seed=int(os.environ.get("SEED", "7")))
    b = T.build()
    print("blocks", len(b.B), "mobs", len(T.marks["mobs"]), "chests", len(T.marks["loot"]))
    if "--game" in sys.argv:
        K.settle(b, keep_islands=40, report=False)
        top = max(p[1] for p in b.B) + 2
        bottom = min(p[1] for p in b.B) - 10
        low = {}
        for (x, y, z) in b.B:
            low[(x, z)] = min(low.get((x, z), 999), y)
        ground = {c for c in T.floor if c in low}
        todo = list(ground)
        while todo:
            x, z = todo.pop()
            for n in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)):
                if n in low and n not in ground and low[n] <= low[(x, z)] + 2:
                    ground.add(n)
                    todo.append(n)
        for (x, z) in ground:
            b.B.setdefault((x, top, z), "minecraft:barrier")
        ring = {(x + dx, z + dz) for (x, z) in ground for dx in (-1, 0, 1) for dz in (-1, 0, 1)} - ground
        for p in [p for p in b.B if (p[0], p[2]) not in ground and (p[0], p[2]) not in ring]:
            del b.B[p]
        for (x, z) in ring:
            for y in range(bottom, top + 1):
                b.B.setdefault((x, y, z), "minecraft:barrier")
        efkit.export(b, "gate_rotwood", R0.points(T), "glowcap")
        sys.exit(0)
    shots = {k: v for k, v in SHOTS.items() if len(sys.argv) < 2 or k in sys.argv[1:]}
    K.preview(b, "gate_rotwood_ef", shots, sun=(30, -30), sky=(0.04, 0.03, 0.06), night=True, fog=0.004)
