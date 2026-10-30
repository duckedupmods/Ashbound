"""The Plague Ward rebuilt at Epic Fight scale: the same run down through the house as the old one
(E:/Ashbound/tools/plague.py has the story). The yard, the long ward and the bathhouse had room for their patients;
the last two places didn't:

    5  the morgue           15 wide, 9 tall (was 11 x 6, and the slabs left a 3-wide aisle for the Plague Doctor)
    6  the surgery theatre  radius 18 (was 15), the pit 13 across the tiers' foot, 20 tall, the way in 7 wide

    python tools/lairs/plague_ef.py [shots]     preview (blender -b -P E:/Ashbound/tools/blender/preview_struct.py -- gate_plague_ef <shots>)
    python tools/lairs/plague_ef.py --game      stage the bin, then python tools/port_gate.py plague lair
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import efkit  # noqa: E402
from efkit import K  # noqa: E402
import plague as P0  # noqa: E402
from plague import A, LAMP, TPL, VG, chain, bars  # noqa: E402

Y0 = -14
THEATRE_Z, THEATRE_R = -206, 18


class WardEF(P0.Ward):

    def morgue(self):
        """5: drawers down both walls, slabs with the dead on them; the Plague Doctor, and the bars he has the key to."""
        y0 = Y0
        z0, z1 = -163, -186
        self.room(-7, y0 + 1, z0, 7, y0 + 9, z1, zone="morgue", vault=1)
        for x in range(-7, 8):
            for z in range(z1, z0 + 1):
                self.floor[(x, z)] = y0
        for z in range(z0, z1 - 1, -1):
            for side in (-1, 1):
                for y in range(y0 + 1, y0 + 7):
                    if z % 2 == 0:
                        self.put(side * 7, y, z, "iron_trapdoor[facing=%s,half=bottom,open=true,powered=false,waterlogged=false]" % ("east" if side < 0 else "west"))
        for z in range(z0 - 3, z1 + 3, -5):
            for sx in (-4, 4):
                for k in range(2):
                    self.put(sx, y0 + 1, z - k, "smooth_stone_slab[type=top,waterlogged=false]")
                    self.put(sx, y0 + 2, z - k, "light_gray_carpet")
            self.lamp(0, y0 + 9, z, 2)
            for sx in (-6, 6):
                self.lamp(sx, y0 + 9, z - 2, 2)
        seal = []
        for x in range(-3, 4):
            for y in range(y0 + 1, y0 + 7):
                self.carve((x, y, z1 - 1), "theatre")
                if not os.environ.get("OPEN_SEAL"):
                    self.put(x, y, z1 - 1, bars("x"))
                seal.append((x, y, z1 - 1))
        self.marks["seal"] = seal
        self.mob(A + "plague_doctor", 0, y0 + 1, z1 + 4, yaw=0)
        self.mob(A + "orderly", -2, y0 + 1, -170, yaw=0)
        self.mob(A + "bell_leper", 2, y0 + 1, -174)
        self.chest(-6, y0 + 1, z1 + 1, "east")

    def theatre(self):
        """6: the surgery theatre, radius 18: a round pit, tiers of watchers, the slab, the great lamp; the Surgeon."""
        y0 = Y0
        cx, cz, R = 0, THEATRE_Z, THEATRE_R
        for x in range(cx - R, cx + R + 1):
            for z in range(cz - R, cz + R + 1):
                d = math.hypot(x - cx, z - cz)
                if d <= R + 0.3:
                    for y in range(y0 + 1, y0 + 21):
                        self.carve((x, y, z), "theatre")
                    self.floor[(x, z)] = y0
        for z in range(cz + R - 2, -186):
            for x in range(-3, 4):
                for y in range(y0 + 1, y0 + 8):
                    self.carve((x, y, z), "theatre")
                self.floor[(x, z)] = y0
        B, r = self.b.B, self.r
        for x in range(cx - R, cx + R + 1):
            for z in range(cz - R, cz + R + 1):
                d = math.hypot(x - cx, z - cz)
                tier = int(d - 13.5) + 1 if d >= 13.5 else 0
                if tier <= 0 or d > R + 0.3:
                    continue
                if z >= cz + 12 and abs(x) <= 3:
                    continue                                  # the way in, through the tiers
                for y in range(y0 + 1, y0 + tier + 1):
                    B[(x, y, z)] = TPL
                if r.random() < 0.22:
                    B[(x, y0 + tier + 1, z)] = "light_gray_carpet"
        for z in (cz - 1, cz, cz + 1):
            B[(cx, y0 + 1, z)] = "smooth_stone_slab[type=top,waterlogged=false]" if z == cz else "polished_deepslate"
            B[(cx, y0 + 2, z)] = "light_gray_carpet" if z != cz + 1 else "white_carpet"
        B[(cx + 2, y0 + 1, cz)] = "cauldron"
        B[(cx - 2, y0 + 1, cz - 1)] = "cauldron"
        B[(cx - 2, y0 + 1, cz + 1)] = "smithing_table"
        for dx in (-1, 0, 1):                                 # the great lamp, hung high over the Surgeon's reach
            for dz in (-1, 0, 1):
                self.put(cx + dx, y0 + 13, cz + dz, LAMP if (dx + dz) % 2 == 0 else VG)
        for (dx, dz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            for y in range(y0 + 14, y0 + 21):
                self.put(cx + dx, y, cz + dz, chain())
        for k in range(12):                                   # lamps round the wall over the top tier
            ang = k * 2 * math.pi / 12 + 0.3
            x, z = int(round(cx + 18.6 * math.cos(ang))), int(round(cz + 18.6 * math.sin(ang)))
            self.put(x, y0 + 9, z, LAMP)
        for k in range(6):                                    # and a ring hung low over the pit's edge
            ang = k * 2 * math.pi / 6
            x, z = int(round(cx + 9 * math.cos(ang))), int(round(cz + 9 * math.sin(ang)))
            for y in range(y0 + 9, y0 + 21):
                self.put(x, y, z, chain())
            self.put(x, y0 + 8, z, LAMP)
        self.marks["boss"] = (0.5, float(y0 + 1), cz - 7.5)
        self.marks["exit"] = (0.5, float(y0 + 1), cz - 11.5)


    def build(self):
        self.yard()
        self.long_ward()
        self.apothecary()
        self.bathhouse()
        self.morgue()
        self.theatre()
        # the ward lit hard and white: lime lamps hung all over, high enough to pass under
        efkit.hang_grid(self, {"yard", "ward", "bath", "morgue", "apoth"}, LAMP, chain(), every=5, height=4, phase=(2, 2))
        efkit.hang_grid(self, {"bath"}, LAMP, chain(), every=5, height=4, phase=(0, 0))
        efkit.hang_grid(self, {"theatre"}, LAMP, chain(), every=7, height=8, phase=(3, 3))
        dressing = dict(self.b.B)
        self.shell()
        self.b.B.update(dressing)
        self.skin()
        for p in self.air:
            if self.b.B.get(p) in ("stone_bricks", "air"):
                del self.b.B[p]
        return self.b


SHOTS = dict(P0.SHOTS)

if __name__ == "__main__":
    T = WardEF(seed=int(os.environ.get("SEED", "7")))
    b = T.build()
    print("blocks", len(b.B), "mobs", len(T.marks["mobs"]), "chests", len(T.marks["loot"]))
    if "--game" in sys.argv:
        efkit.export(b, "gate_plague", P0.points(T), "lime_lamp")
        sys.exit(0)
    shots = {k: v for k, v in SHOTS.items() if len(sys.argv) < 2 or k in sys.argv[1:]}
    K.preview(b, "gate_plague_ef", shots, sun=(30, -30), sky=(0.02, 0.02, 0.025), night=True, fog=0.004)
