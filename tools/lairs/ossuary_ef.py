"""The Ossuary Engine rebuilt at Epic Fight scale: the same descent as the old one (E:/Ashbound/tools/ossuary.py has
the story). Its big rooms (the nave, the works, the chapel, the assembly hall) stand tall enough; the ways between
them and two walks were built for a vanilla player:

    halls between places     7 wide, 7 tall (were 3 x 4)
    the furnace bridge       the catwalk over the soul fire 5 wide (was 3), its chains moved out
    the pallbearers' crypt   17 wide, 9 tall (was 13 x 6), the sarcophagi drawn apart so the Pallbearer has the
                             middle to fight in

    python tools/lairs/ossuary_ef.py [shots]     preview (blender -b -P E:/Ashbound/tools/blender/preview_struct.py -- gate_ossuary_ef <shots>)
    python tools/lairs/ossuary_ef.py --game      stage the bin, then python tools/port_gate.py ossuary lair
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import efkit  # noqa: E402
from efkit import K  # noqa: E402
import ossuary as O0  # noqa: E402
from ossuary import A, BB, SKULL, FEMUR, BRASS, LAMP, GRATE, DARKB, stairs, chain  # noqa: E402

W = 3


class OssuaryEF(O0.Ossuary):

    def hall(self, x, y, z0, z1, zone="crypt"):
        """A straight hallway from z0 down to z1 (floor at y, 7 wide, 7 high): femur ribs and a brass-capped arch
        every third block, soul lamps between, skull slabs down the floor, a framed portal at each end."""
        B = self.b.B
        for z in range(z1, z0 + 1):
            for dx in range(-W, W + 1):
                for yy in range(y + 1, y + 8):
                    self.carve((x + dx, yy, z), zone)
                    B.pop((x + dx, yy, z), None)
                B[(x + dx, y, z)] = SKULL if (z - z1) % 4 == 0 and dx == 0 else BB
            k = z0 - z
            rib = k % 3 == 0
            for side in (-1, 1):
                wx = x + side * (W + 1)
                for yy in range(y + 1, y + 8):
                    if rib:
                        B[(wx, yy, z)] = BRASS if yy == y + 1 else FEMUR
                    else:
                        B[(wx, yy, z)] = LAMP if (yy == y + 4 and k % 3 == 1) else {y + 1: DARKB, y + 2: SKULL}.get(yy, BB)
                if rib:
                    B[(x + side * W, y + 7, z)] = stairs("west" if side < 0 else "east", half="top")
            for dx in range(-W, W + 1):
                B[(x + dx, y + 8, z)] = BRASS if rib else DARKB
        for z in (z0, z1):
            for side in (-1, 1):
                for yy in range(y + 1, y + 9):
                    B[(x + side * (W + 1), yy, z)] = BRASS if yy in (y + 1, y + 8) else FEMUR
            for dx in range(-W, W + 1):
                B[(x + dx, y + 8, z)] = SKULL if dx == 0 else BRASS

    def furnace_bridge(self):
        """4: the old shaft and catwalk, the catwalk widened to five and its chains moved out to the new edge."""
        super().furnace_bridge()
        x0, y0, z0 = self.sort_out
        z1 = z0 - 34
        B = self.b.B
        path = [(0, z0 - 1), (0, z0 - 7), (-7, z0 - 7), (-7, z0 - 16), (6, z0 - 16), (6, z0 - 26), (0, z0 - 26), (0, z1)]
        for (x, z) in path:                                      # the old chains came down on the old edge
            for yy in range(y0 + 1, y0 + 11):
                if "chain" in B.get((x + 2 if x <= 0 else x - 2, yy, z), ""):
                    del B[(x + 2 if x <= 0 else x - 2, yy, z)]
        for (ax, az), (bx, bz) in zip(path, path[1:]):
            for x in range(min(ax, bx) - 2, max(ax, bx) + 3):
                for z in range(min(az, bz) - 2, max(az, bz) + 3):
                    B[(x, y0, z)] = GRATE
        for (x, z) in path:
            for yy in range(y0 + 1, y0 + 11):
                B[(x + 3 if x <= 0 else x - 3, yy, z)] = chain()
        for x in range(-3, 4):
            for yy in range(y0 + 1, y0 + 8):
                self.carve((x, yy, z1 - 1), "crypt")

    def crypt(self):
        """5: the pallbearers' crypt, 17 wide: coffins standing in the walls, the Pallbearer before the sarcophagi."""
        x0, y0, z0 = self.bridge_out
        z1 = z0 - 28
        self.room(-8, y0 + 1, z0 - 1, 8, y0 + 9, z1, zone="crypt", vault=2)
        B, r = self.b.B, self.r
        for z in range(z1, z0):
            for x in range(-2, 3):
                B[(x, y0, z)] = SKULL if z % 4 == 0 and x == 0 else BB
        for z in range(z0 - 3, z1 + 3, -3):
            for side in (-9, 9):
                self.put(side, y0 + 1, z, "stripped_dark_oak_log[axis=y]")
                self.put(side, y0 + 2, z, BRASS if r.random() < 0.3 else "stripped_dark_oak_log[axis=y]")
                self.put(side, y0 + 3, z, "dark_oak_log[axis=y]")
                self.put(side, y0 + 4, z, SKULL)
            for side in (-7, 7):
                self.put(side, y0 + 1, z - 1, "candle[candles=%d,lit=true,waterlogged=false]" % r.randint(1, 4))
        for z in range(z0 - 6, z1 + 3, -6):
            self.lantern(0, y0 + 11, z, 5)
            for sx in (-5, 5):
                self.lantern(sx, y0 + 10, z - 3, 4)
        for z in range(z0 - 4, z1 + 3, -6):
            for side in (-9, 9):
                self.put(side, y0 + 5, z, LAMP)
        for side in (-1, 1):
            for ax in range(4, 8):
                for z in (z1, z1 + 1, z1 + 2, z1 + 3):
                    B[(side * ax, y0 + 1, z)] = DARKB
            self.sarcophagus(side * 5, y0 + 2, z1 + 2)
            self.put(side * 7, y0 + 2, z1 + 3, LAMP)
        self.chest(7, y0 + 2, z1 + 1, "west")
        self.mob(A + "pallbearer", 0, y0 + 1, z1 + 7, yaw=0)
        self.hall(0, y0, z1 - 1, z1 - 9)
        self.crypt_out = (0, y0, z1 - 9)


SHOTS = dict(O0.SHOTS)

if __name__ == "__main__":
    T = OssuaryEF(seed=int(os.environ.get("SEED", "7")))
    b = T.build()
    print("blocks", len(b.B), "mobs", len(T.marks["mobs"]), "chests", len(T.marks["loot"]))
    if "--game" in sys.argv:
        efkit.export(b, "gate_ossuary", O0.points(T), "soul_lamp")
        sys.exit(0)
    shots = {k: v for k, v in SHOTS.items() if len(sys.argv) < 2 or k in sys.argv[1:]}
    K.preview(b, "gate_ossuary_ef", shots, sun=(30, -30), sky=(0.02, 0.025, 0.02), night=True, fog=0.004)
