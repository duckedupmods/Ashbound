"""The Faceless Temple rebuilt at Epic Fight scale: the same straight run as the old one (E:/Ashbound/tools/temple.py
has the story). The cavern, the hall of statues and the throne room had room; two stretches didn't:

    5  the abyss         the bridge over the drop 5 wide (was 3; the Mask Crawlers come up over its edges)
    6  the sealed door   19 wide, 11 tall, 18 long (was 13 x 8 x 12) for the Facetaker and two Sentinels; its
                         doorways 7 wide, 7 tall

    python tools/lairs/temple_ef.py [shots]     preview (blender -b -P E:/Ashbound/tools/blender/preview_struct.py -- gate_temple_ef <shots>)
    python tools/lairs/temple_ef.py --game      stage the bin, then python tools/port_gate.py temple lair
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import efkit  # noqa: E402
from efkit import K  # noqa: E402
import temple as T0  # noqa: E402
from temple import A, TB, CTB, ABYSS, GILD, CARVED, CRYB, crystal, slab  # noqa: E402

DOOR_Z = -215


class TempleEF(T0.Temple):

    def cavern(self):
        """3: the old cavern; its front stair stopped a block short of the threshold, so a last step up to it"""
        super().cavern()
        for x in range(-7, 8):
            self.put(x, 0, self.front_z + 2, T0.stairs("north"))

    def throne_room(self):
        """7: the old throne room; the dais's steps turned to face the way you climb them (north)"""
        super().throne_room()
        for k in range(3):
            for x in range(-8 + k, 9 - k):
                self.put(x, k + 1, -247 - 2 * k, T0.stairs("north"))

    def abyss(self):
        z0, z1 = self.hall_z[1] - 1, -197
        self.abyss_z = (z0, z1)
        self.blob((0, -6, (z0 + z1) / 2), 15, 22, 15, -30, zone="abyss", rough=0.15)
        for (x, y, z) in list(self.air):
            if self.zone[(x, y, z)] == "abyss" and not (z1 <= z <= z0):
                self.air.discard((x, y, z))
                del self.zone[(x, y, z)]
        for x in range(-3, 4):
            for y in range(1, 8):
                self.carve((x, y, z0 + 1), "temple")
        for z in range(z1, z0 + 2):                      # the bridge, five wide, broken walls for rails
            for x in range(-2, 3):
                self.put(x, 0, z, TB if self.r.random() > 0.08 else CTB)
                self.put(x, -1, z, slab("top"))
            for x in (-3, 3):
                self.put(x, 0, z, TB)
                if self.r.random() < 0.6:
                    self.put(x, 1, z, A + "temple_brick_wall[east=none,north=low,south=low,up=true,waterlogged=false,west=none]")
        for z in range(z1 + 2, z0, -6):
            for x in (-3, 3):
                for y in range(-4, 0):
                    self.put(x, y, z, TB)
        for (x, y, z) in list(self.air):
            if self.zone[(x, y, z)] == "abyss" and y == -29 and self.r.random() < 0.3:
                self.put(x, y, z, crystal("up"))
        for x in range(-12, 13):
            for z in range(z1, z0 + 1):
                if self.b.B.get((x, -30, z)) == ABYSS and self.r.random() < 0.25:
                    self.put(x, -30, z, CRYB)
        for k in range(3):
            self.mob(A + "hollow", self.r.choice((-1, 0, 1)), 1, z1 + 2 + k * 2)
        for k in range(4):
            self.mob(A + "mask_crawler", (-2, 2, 0, -1)[k], 1, z1 + 9 + k * 2)

    def sealed_door(self):
        z0, z1 = self.abyss_z[1] - 1, DOOR_Z
        self.door_z = z1
        self.room(-9, 1, z0, 9, 11, z1, vault=1)
        for z in range(z1, z0 + 1):
            for x in range(-2, 3):
                self.put(x, 0, z, ABYSS)
        for x in (-8, 8):
            self.brazier(x, 1, z0 - 2, "south")
            self.brazier(x, 1, z1 + 4, "north")
        for sx in (-6, 6):
            self.put(sx, 0, z1 + 4, GILD)
            self.mob(A + "sentinel", sx, 1, z1 + 4, yaw=0)
        self.mob(A + "facetaker", 0, 1, z1 + 9, yaw=0)
        for x in range(-3, 4):
            for y in range(1, 8):
                self.carve((x, y, z0 + 1), "temple")
        for x in range(-3, 4):
            for y in range(1, 10):
                self.carve((x, y, z1 - 1), "temple")
                self.carve((x, y, z1 - 2), "temple")
        for y in range(0, 11):
            for x in (-4, 4):
                self.put(x, y, z1, GILD)
        for x in range(-4, 5):
            self.put(x, 10, z1, GILD)
            self.put(x, 11, z1, CARVED)


SHOTS = dict(T0.SHOTS)

if __name__ == "__main__":
    T = TempleEF(seed=int(os.environ.get("SEED", "3")))
    b = T.build()
    print("blocks", len(b.B), "mobs", len(T.marks["mobs"]), "chests", len(T.marks["loot"]))
    if "--game" in sys.argv:
        efkit.export(b, "gate_temple", T0.points(T), "brazier")
        sys.exit(0)
    shots = {k: v for k, v in SHOTS.items() if len(sys.argv) < 2 or k in sys.argv[1:]}
    K.preview(b, "gate_temple_ef", shots, sun=(30, -30), sky=(0.02, 0.02, 0.035), night=True, fog=0.004)
