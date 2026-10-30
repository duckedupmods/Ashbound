"""Gallows Hill rebuilt at Epic Fight scale: the same seven places up the same hill as the old one
(E:/Ashbound/tools/gallows.py has the story). The hill is open to the sky, so headroom was never the trouble; the
lanes were: posts stood inside 7-wide lanes and left five blocks to fight a 3.6-tall Gibbet Knight in.

    2  hangman's road    9 wide, the gibbet posts on the banks, nooses out over the lane
    5  the cage walk     11 wide, the cages at its edges
    6  the long drop     7 wide, 9 tall, the scaffold gate 7 x 5
    7  the great gallows radius 20 round a 23 x 23 scaffold

    python tools/lairs/gallows_ef.py [shots]     preview (blender -b -P E:/Ashbound/tools/blender/preview_struct.py -- gate_gallows_ef <shots>)
    python tools/lairs/gallows_ef.py --game      stage the bin, then python tools/port_gate.py gallows lair
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import efkit  # noqa: E402
from efkit import K  # noqa: E402
import gallows as G  # noqa: E402
from gallows import A, GTIM, TARP, HEMP, GIRON, LAMP, stairs, slab, chain, fence, bars, trapdoor  # noqa: E402

DECK = G.DECK


class GallowsEF(G.Gallows):

    def road(self):
        """2: the sunken lane up the hill, nooses out over it from posts on its banks; the Noose-Walker at the top."""
        f = self.climb(-4, 4, -25, -75, 0, 6, 12, "road")
        self.road_top = f
        for k, z in enumerate(range(-28, -74, -6)):
            fl = self.floor.get((0, z), 0)
            side = -1 if k % 2 else 1
            for y in range(fl + 1, fl + 3):          # the post's foot cut into the bank
                self.carve((side * 5, y, z), "road")
            ex, ez = self.gibbet(side * 5, fl + 1, z, (-side, 0), length=2, h=9, drop=2 + k % 2)
            if k % 2 == 0 and z > -66:
                self.mob(A + "the_dropped", ex, fl + 1, ez)
        for (x, z) in ((-5, -33), (5, -45), (-5, -57)):
            fl = self.floor.get((0, z), 0)
            self.put(x, fl + 2, z, G.NOTICE)
        for (x, z) in ((2, -40), (-2, -62)):
            fl = self.floor.get((0, z), 0)
            self.put(x, fl + 1, z, HEMP)
        self.mob(A + "noose_walker", 0, f + 1, -71, yaw=0)
        self.mob(A + "the_dropped", -2, self.floor.get((0, -66), 0) + 1, -66)
        self.mob(A + "the_dropped", 2, self.floor.get((0, -68), 0) + 1, -68)

    def cage_walk(self):
        """5: the ridge path, eleven wide, gibbet cages along both its edges; the Gibbet Knight at its end."""
        f = self.climb(-5, 5, -135, -170, self.market_top, 4, 10, "cage", every=8)
        self.cage_top = f
        for k, z in enumerate(range(-138, -168, -5)):
            fl = self.floor.get((0, z), 0)
            for side in (-1, 1):
                for y in range(fl + 1, fl + 3):
                    self.carve((side * 6, y, z), "cage")
                self.gibbet(side * 6, fl + 1, z, (-side, 0), length=1, h=8, cage=True, drop=1)
            self.lamp(6 if k % 2 else -6, fl + 4, z - 2)
            self.post_lamp(-4 if k % 2 else 4, fl, z - 3, h=2)
        for (x, z) in ((-2, -146), (2, -159)):
            self.mob(A + "the_dropped", x, self.floor.get((0, z), 0) + 1, z)
        self.mob(A + "gibbet_knight", 0, f + 1, -167, yaw=0)

    def long_drop(self):
        """6: the timber stair up the scaffold's cliff, seven wide; the scaffold gate (the seal) at its head."""
        F = self.cage_top
        f = self.climb(-3, 3, -171, -179, F, 8, 9, "drop", block=A + "gallows_timber_stairs", every=1)
        self.area(-3, -180, 3, -187, f, 9, "drop")
        self.drop_top = f
        for z in range(-171, -180):
            fl = self.floor.get((0, z), 0)
            for sx in (-4, 4):
                if z % 2 == 0:
                    self.put(sx, fl + 2, z, fence())
        for sx in (-3, 3):
            self.lamp(sx, f + 5, -183)
            self.lamp(sx, self.floor.get((0, -175), F) + 5, -175)
        seal = []
        z = -187
        for x in range(-3, 4):
            for y in range(f + 1, f + 6):
                if not os.environ.get("OPEN_SEAL"):
                    self.put(x, y, z, bars("x"))
                seal.append((x, y, z))
        for sx in (-4, 4):
            for y in range(f + 1, f + 7):
                self.put(sx, y, z, GIRON)
        for x in range(-4, 5):
            self.put(x, f + 6, z, GIRON)
        self.marks["seal"] = seal

    def great_gallows(self):
        """7: the hilltop, radius 20; the raised scaffold, 23 x 23; the great beam, twelve nooses, trapdoors."""
        F = self.drop_top
        cz, R = -209, 20
        for x in range(-R, R + 1):
            for z in range(cz - R, cz + R + 1):
                if math.hypot(x, z - cz) <= R + 0.3:
                    self.area(x, z, x, z, F, 26, "arena")
        self.area(-3, -188, 3, cz + R, F, 9, "arena")
        X0, X1, Z0, Z1 = -11, 11, cz + 11, cz - 11
        traps = []
        holes = [(-7, cz + 5), (6, cz + 6), (-8, cz - 5), (7, cz - 4), (-1, cz - 8), (0, cz + 1)]
        hole = {(hx + dx, hz + dz) for (hx, hz) in holes for dx in (0, 1) for dz in (0, -1)}
        for x in range(X0, X1 + 1):
            for z in range(Z1, Z0 + 1):
                if (x, z) in hole:
                    self.put(x, DECK, z, trapdoor("top", f="north", block="dark_oak_trapdoor"))
                    traps.append((x, DECK, z))
                    continue
                edge = x in (X0, X1) or z in (Z0, Z1)
                self.put(x, DECK, z, GTIM if edge else (TARP if (x * 3 + z) % 7 == 0 else slab("top", block=A + "gallows_timber_slab")))
                if (x - X0) % 5 == 0 and (z - Z1) % 5 == 0 and (x, z) not in hole:
                    for y in range(F + 1, DECK):
                        self.put(x, y, z, GTIM)
        for (x, _, z) in traps:
            for y in range(F + 1, DECK):
                if self.b.B.get((x, y, z)) == GTIM:
                    del self.b.B[(x, y, z)]
        self.marks["trap"] = traps
        for x in range(X0, X1 + 1):
            for z in range(Z1, Z0 + 1):
                if (x in (X0, X1) or z in (Z0, Z1)) and not (z == Z0 and abs(x) <= 3):
                    if (x + z) % 2 == 0:
                        self.put(x, DECK + 1, z, fence())
        for k in range(1, DECK - F + 1):                         # the stair up the south face, seven wide
            z = Z0 + 1 + (DECK - F) - k
            for x in range(-3, 4):
                self.put(x, F + k, z, stairs("north"))
                for y in range(F + 1, F + k):
                    self.put(x, y, z, GTIM)
        for k in range(1, DECK - F + 1):                         # and up the east, so a fall is never far from a way up
            x = X1 + 1 + (DECK - F) - k
            for z in range(cz - 3, cz + 1):
                self.put(x, F + k, z, stairs("west"))
                for y in range(F + 1, F + k):
                    self.put(x, y, z, GTIM)
        BY = DECK + 14
        for sx in (-10, 10):
            for y in range(DECK + 1, BY + 1):
                self.put(sx, y, cz, GTIM)
            self.put(sx - (1 if sx > 0 else -1), BY - 1, cz, stairs("east" if sx > 0 else "west", "top"))
        for x in range(-13, 14):
            self.put(x, BY + 1, cz, GTIM)
        for k in range(12):
            x = -9 + k + (2 if k >= 6 else 0) - (1 if k >= 6 else 0)
            if abs(x) >= 10:
                continue
            for y in range(BY - 3 - k % 3, BY + 1):
                self.put(x, y, cz, chain())
            self.put(x, BY - 4 - k % 3, cz, HEMP if k % 4 == 0 else chain())
        self.put(-9, DECK + 1, cz + 2, "lever[face=floor,facing=south,powered=false]")
        self.put(5, DECK + 1, cz + 8, "stripped_dark_oak_log[axis=y]")
        self.put(6, DECK + 1, cz + 8, "barrel[facing=up,open=true]")
        for k in range(12):                                      # tallow lamps round the hilltop on posts
            a = k * 2 * math.pi / 12 + 0.2
            x, z = int(round(18 * math.cos(a))), int(round(cz + 18 * math.sin(a)))
            for y in range(F + 1, F + 4):
                self.put(x, y, z, GTIM)
            self.put(x, F + 4, z, LAMP)
        for (x, z) in ((-5, cz - 2), (5, cz + 3), (0, cz + 7), (-3, cz - 9), (8, cz - 8), (-8, cz + 8)):
            self.put(x, DECK - 1, z, LAMP)                       # under the deck, for whoever falls through
        for (x, z) in ((-6, cz + 6), (6, cz - 6), (6, cz + 6), (-6, cz - 6)):
            self.post_lamp(x, DECK, z, h=2)                      # on the deck, round the fight
        for sx in (-10, 10):
            self.put(sx, BY - 4, cz + 1, LAMP)
        for (x, z) in ((-15, cz + 7), (15, cz - 8), (-4, cz + 3), (4, cz - 6)):
            self.mob(A + "the_dropped", x, F + 1, z, decor=True)
        self.marks["boss"] = (0.5, float(DECK + 1), cz - 4.5)
        self.marks["exit"] = (0.5, float(DECK + 1), cz - 8.5)


    def build(self):
        self.colzone = {}
        self.crossroads()
        self.road()
        self.tarworks()
        self.market()
        self.cage_walk()
        self.long_drop()
        self.great_gallows()
        # the hill at night: tallow lamps on posts across every open stretch, off the middle of the lanes
        for z in range(-27, -75, -3):                            # both edges of the hangman's road
            for sx in (-4, 4):
                fl = self.floor.get((sx, z))
                if fl is not None and not any((sx, y, z) in self.b.B for y in range(fl + 1, fl + 5)):
                    self.post_lamp(sx, fl, z, h=2)
        for (x, z) in ((-8, -3), (8, -3), (-9, -16), (9, -18), (-3, -21), (4, -22), (-3, -8), (3, -15)):
            if not any((x + dx, 1, z + dz) in self.b.B for dx in (-1, 0, 1) for dz in (-1, 0, 1)):
                self.post_lamp(x, 0, z, h=2)
        lamp = lambda x, fl, z: self.post_lamp(x, fl, z, h=2)  # noqa: E731
        efkit.light_grid(self, {"cross", "market"}, lamp, every=7, keep_clear=lambda x, z: abs(x) <= 1, phase=(3, 2))
        efkit.light_grid(self, {"tar"}, lamp, every=5, keep_clear=lambda x, z: abs(x) <= 1, phase=(3, 2))
        efkit.light_grid(self, {"road"}, lamp, every=5, keep_clear=lambda x, z: abs(x) <= 2, phase=(1, 0))
        efkit.light_grid(self, {"arena"}, lamp, every=7, keep_clear=lambda x, z: abs(x) <= 3, phase=(3, 2))
        dressing = dict(self.b.B)
        self.shell()
        self.b.B.update(dressing)
        self.open_sky()
        self.skin()
        for p in self.air:
            if self.b.B.get(p) in ("air", G.HEARTH) and p not in dressing:
                del self.b.B[p]
        return self.b


SHOTS = dict(G.SHOTS)
SHOTS.update({"arena": ((0, 31, -186), (0, 25, -214), 16), "cage": ((0, 13, -136), (0, 13, -170), 13)})

if __name__ == "__main__":
    T = GallowsEF(seed=int(os.environ.get("SEED", "7")))
    b = T.build()
    print("blocks", len(b.B), "mobs", len(T.marks["mobs"]), "chests", len(T.marks["loot"]), "traps", len(T.marks["trap"]))
    if "--game" in sys.argv:
        top = max(p[1] for p in b.B) + 2                         # the open sky: a barrier lid, invisible walls to it
        high = {}
        for (x, y, z) in b.B:
            high[(x, z)] = max(high.get((x, z), -99), y)
        for (x, z), h in high.items():
            edge = any((x + dx, z + dz) not in high for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            for y in range(h + 1 if edge else top, top + 1):
                b.B[(x, y, z)] = "minecraft:barrier"
        efkit.export(b, "gate_gallows", G.points(T), "tallow_lamp")
        sys.exit(0)
    shots = {k: v for k, v in SHOTS.items() if len(sys.argv) < 2 or k in sys.argv[1:]}
    K.preview(b, "gate_gallows_ef", shots, sun=(30, -30), sky=(0.05, 0.04, 0.07), night=True, fog=0.004)
