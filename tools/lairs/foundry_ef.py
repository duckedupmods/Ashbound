"""The Slag Foundry rebuilt at Epic Fight scale: the same run down through the works as the old one
(E:/Ashbound/tools/foundry.py has the story). The halls themselves were big; what joined them and the walks through
them were built for a vanilla player:

    halls between places   7 wide, 7 tall (were 3 x 4), the lava gutters at their sides
    the quench stair       7 wide
    the chain hall         the gantry over the molten lake 7 wide (was 3: one knock and you were in it)
    the kiln heart         roof raised 6 (21 at the wall, 28 in the middle) for Ossric's 13; the chains go up with it

    python tools/lairs/foundry_ef.py [shots]     preview (blender -b -P E:/Ashbound/tools/blender/preview_struct.py -- gate_foundry_ef <shots>)
    python tools/lairs/foundry_ef.py --game      stage the bin, then python tools/port_gate.py foundry lair
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import efkit  # noqa: E402
from efkit import K  # noqa: E402
import foundry as F0  # noqa: E402
from foundry import A, DB, CHISEL, GRATE, LAVA, KI, RKI, SEAR, DARK, MAGMA, stairs, chain, bars  # noqa: E402

W = 3            # a hall's half width


class FoundryEF(F0.Foundry):

    def hall(self, x, y, z0, z1):
        """A straight hall from z0 down to z1 (floor at y, 7 wide, 7 high): iron ribs every fourth block, glowing
        seams between, lava in gutters under grates at both sides of the floor, an iron portal at each end."""
        B = self.b.B
        for z in range(z1, z0 + 1):
            for dx in range(-W, W + 1):
                for yy in range(y + 1, y + 8):
                    self.carve((x + dx, yy, z), "foundry")
                    B.pop((x + dx, yy, z), None)
                B[(x + dx, y, z)] = CHISEL if z % 4 == 0 and dx == 0 else DB
                B[(x + dx, y - 1, z)] = DB
            for side in (-1, 1):
                B[(x + side * W, y, z)] = GRATE
                B[(x + side * W, y - 1, z)] = LAVA
                B[(x + side * W, y - 2, z)] = DB
                B[(x + side * (W + 1), y - 1, z)] = DB
            rib = (z0 - z) % 4 == 0
            for side in (-1, 1):
                wx = x + side * (W + 1)
                for yy in range(y, y + 8):
                    B[(wx, yy, z)] = KI if rib else (SEAR if yy == y + 3 else (RKI if yy == y + 1 else DB))
                if rib:
                    B[(x + side * W, y + 7, z)] = stairs("west" if side < 0 else "east", half="top", block="polished_blackstone_stairs")
            for dx in range(-W, W + 1):
                B[(x + dx, y + 8, z)] = KI if rib else DARK
            if (z0 - z) % 6 == 3:
                for yy in (y + 8,):
                    B[(x, yy - 1, z)] = chain()
                B[(x, y + 6, z)] = "lantern[hanging=true,waterlogged=false]"
        for z in (z0, z1):
            for side in (-1, 1):
                for yy in range(y, y + 9):
                    B[(x + side * (W + 1), yy, z)] = KI
            for dx in range(-W, W + 1):
                B[(x + dx, y + 8, z)] = CHISEL if dx == 0 else KI

    def chain_hall(self):
        """3: a gantry 7 wide over a lake of molten iron, crucibles round it, rails under the roof."""
        _, y0, gz = self.cast_out
        z0, z1 = gz - 1, gz - 41
        lake = y0 - 20
        self.room(-14, lake + 1, z0, 14, y0 + 16, z1, zone="foundry")
        B = self.b.B
        top = y0 + 16
        for x in range(-14, 15):
            for z in range(z1, z0 + 1):
                B[(x, lake, z)] = LAVA
        for z in range(z1, z0 + 1):
            for x in range(-3, 4):
                B[(x, y0, z)] = GRATE
            k = z0 - z
            if k % 5 == 0:
                for x in range(-4, 5):
                    B[(x, y0 - 1, z)] = KI
                for side in (-4, 4):
                    B[(side, y0, z)] = KI
                    for yy in range(y0 + 1, top):
                        B[(side, yy, z)] = chain()
            else:
                for side in (-4, 4):
                    B[(side, y0, z)] = KI
                    B[(side, y0 + 1, z)] = bars("z")
        for (side, pz) in ((1, z0 - 12), (-1, z0 - 28)):
            for ax in range(4, 8):
                for dz in (-1, 0, 1):
                    B[(side * ax, y0, pz + dz)] = GRATE
                    B[(side * ax, y0 + 1, pz + dz)] = "air"
            for ax in range(8, 13):
                for z in range(pz - 2, pz + 3):
                    B[(side * ax, y0, z)] = KI if ax in (8, 12) or abs(z - pz) == 2 else DB
                    B[(side * ax, y0 - 1, z)] = RKI
            for yy in range(lake + 1, y0 - 1):
                B[(side * 10, yy, pz)] = KI if yy % 4 else DB
            self.crucible(side * 10, y0 + 7, pz, 1, chains_to=top)
        for (cx, cy, cz) in ((-10, y0 - 6, z0 - 8), (10, y0 - 4, z0 - 22), (-9, y0 - 3, z0 - 36), (11, y0 - 8, z0 - 34)):
            self.crucible(cx, cy, cz, 1, chains_to=top)
        self.crucible(0, y0 + 9, z0 - 20, 2, chains_to=top)
        for (x, z) in ((-13, z0 - 2), (13, z0 - 2), (-13, z1 + 2), (13, z1 + 2), (-13, z0 - 20), (13, z0 - 20)):
            for yy in range(lake, top + 1):
                B[(x, yy, z)] = MAGMA if yy % 6 == 1 else (KI if yy % 6 == 0 else DB)
        for z in range(z1, z0 + 1):
            for x in (-8, 8):
                B[(x, top - 1, z)] = chain("z")
        self.mob(A + "riveter", 10, y0 + 1, z0 - 12, yaw=90)
        self.mob(A + "riveter", -10, y0 + 1, z0 - 28, yaw=270)
        self.mob(A + "cinderhusk", 0, y0 + 1, z0 - 24, yaw=0)
        self.chest(11, y0 + 1, z0 - 14, "west")
        self.hall(0, y0, z1 - 1, z1 - 10)
        self.chain_out = (0, y0, z1 - 10)

    def quench_pits(self):
        """4: the stair down 7 wide, then the old pits (water tanks, blades hung in them; the Crucible Bearer)."""
        _, y1, gz = self.chain_out
        B = self.b.B
        for k in range(6):
            for x in range(-3, 4):
                for yy in range(y1 - k, y1 + 8 - k):
                    self.carve((x, yy, gz - 1 - k), "foundry")
                    B.pop((x, yy, gz - 1 - k), None)
                B[(x, y1 - 1 - k, gz - 1 - k)] = stairs("south")
            for side in (-4, 4):
                for yy in range(y1 - 1 - k, y1 + 8 - k):
                    B[(side, yy, gz - 1 - k)] = KI if k % 3 == 0 else DB
        stair = {p: B[p] for p in list(B) if gz - 7 < p[2] <= gz - 1 and -4 <= p[0] <= 4}
        # the rest as the old one builds it (its own 3-wide stair carved again over ours, then ours put back)
        super().quench_pits()
        for x in range(-4, 5):
            for z in range(gz - 6, gz):
                for y in range(y1 - 8, y1 + 9):
                    if (x, y, z) not in stair:
                        B.pop((x, y, z), None)
        B.update(stair)

    def kiln_heart(self):
        """5: the old round hall, its roof raised 6 for Ossric; every chain hung from it carried up to the new roof."""
        super().kiln_heart()
        B = self.b.B
        cols = {}
        for (x, y, z) in self.air:
            if self.zone.get((x, y, z)) == "arena":
                cols[(x, z)] = max(cols.get((x, z), y), y)
        for (x, z), top in cols.items():
            for y in range(top + 1, top + 7):
                self.carve((x, y, z), "arena")
            if (x, top, z) in B and "chain" in B[(x, top, z)]:
                for yy in range(top + 1, top + 7):
                    B[(x, yy, z)] = B[(x, top, z)]


    def build(self):
        self.slag_gate()
        self.casting_floor()
        self.chain_hall()
        self.quench_pits()
        self.kiln_heart()
        # braziers across the slag cavern, where only the pools glowed
        fire = lambda x, fl, z: self.brazier(x, fl + 1, z, "north")  # noqa: E731
        efkit.light_grid(self, {"slag"}, fire, every=6, keep_clear=lambda x, z: abs(x) <= 2, phase=(3, 1))
        dressing = dict(self.b.B)
        self.shell()
        self.b.B.update(dressing)
        self.skin()
        for p in self.air:
            if self.b.B.get(p) in ("blackstone", "air"):
                del self.b.B[p]
        return self.b


SHOTS = dict(F0.SHOTS)

if __name__ == "__main__":
    T = FoundryEF(seed=int(os.environ.get("SEED", "7")))
    b = T.build()
    print("blocks", len(b.B), "mobs", len(T.marks["mobs"]), "chests", len(T.marks["loot"]))
    if "--game" in sys.argv:
        efkit.export(b, "gate_foundry", F0.points(T), "brazier")
        sys.exit(0)
    shots = {k: v for k, v in SHOTS.items() if len(sys.argv) < 2 or k in sys.argv[1:]}
    K.preview(b, "gate_foundry_ef", shots, sun=(30, -30), sky=(0.03, 0.015, 0.01), night=True, fog=0.004)
