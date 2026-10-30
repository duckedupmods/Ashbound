"""The Frozen Procession rebuilt at Epic Fight scale: the same long road as the old one (E:/Ashbound/tools/frost.py has
the story). The glacier halls were big enough; what changed is the host that waits in them, and the ways between:

    1  the watch gate       its gate out 7 wide, 7 tall (was 5 x 5)
    2  the long march       the ranks now hold Rime Knights; a Frost Chaplain keeps each of the road's fires
    3  the fallen standard  the Standard Bearer holds the camp, the host's key on him; two Rime Knights and a
                            Chaplain stand with him
    4  the bridge of ranks  7 wide (was 5), a gate wall across its near end, barred till the Bearer falls (the
                            "seal"); Rime Knights on the far ledge with the archers
    5  the marshal's field  its way in 7 wide and 7 tall

    python tools/lairs/frost_ef.py [shots]     preview (blender -b -P E:/Ashbound/tools/blender/preview_struct.py -- gate_frost_ef <shots>)
    python tools/lairs/frost_ef.py --game      stage the bin, then python tools/port_gate.py frost lair
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import efkit  # noqa: E402
from efkit import K  # noqa: E402
import frost as F0  # noqa: E402
from frost import A, IBR, FLAG, slab  # noqa: E402

SEAL_Z = -188
BARS = "iron_bars[east=true,north=false,south=false,waterlogged=false,west=true]"


class FrostEF(F0.Frost):

    def mob_at(self, kind, x, y, z, yaw=0, decor=False):
        self.mob(A + kind, x, y, z, yaw=yaw, decor=decor)

    def watch_gate(self):
        super().watch_gate()
        for x in range(-3, 4):
            for y in range(1, 8):
                for z in (-17, -18):
                    self.carve((x, y, z), "fort")
                    self.b.B.pop((x, y, z), None)
        for x in (-3, 3):                                # what's left of the portcullis, hung at the sides
            for y in range(5, 8):
                self.put(x, y, -17, BARS)

    def long_march(self):
        super().long_march()
        z0, z1 = self.march_z
        r = self.r
        # the heavy line: Rime Knights in the front rank, a few of them already thawing
        for z in range(z0 - 10, z1 + 10, -12):
            side = 1 if (z // 12) % 2 else -1
            self.mob_at("rime_knight", side * 6, 1, z - 2, yaw=180, decor=r.random() > 0.35)
        # lamp posts the host carried, set closer down both road edges (the old ones every 16 left it black between)
        for z in range(z0 - 4, z1 + 4, -8):
            side = 1 if (z // 8) % 2 else -1
            if all(abs(z - fz) > 2 for fz in (-48, -84, -118)) and not self.b.B.get((side * 4, 1, z)):
                self.lamp_post(side * 4, 1, z)
        # a Chaplain keeping each fire
        for z in (-48, -84, -118):
            self.mob_at("frost_chaplain", 2, 1, z - 2, yaw=0)

    def fallen_standard(self):
        super().fallen_standard()
        # the tents raised to EF height: walls to 2, roof slopes 3 and 4, room under them to reach the chests
        fence = "spruce_fence[east=false,north=false,south=false,waterlogged=false,west=false]"
        for (tx, tz) in ((-10, -160), (9, -165), (-9, -176), (10, -178)):
            for dx in range(-2, 3):
                for dz in range(-2, 3):
                    for y in range(1, 5):
                        if self.b.B.get((tx + dx, y, tz + dz)) == "white_wool":
                            del self.b.B[(tx + dx, y, tz + dz)]
                    for y in ((1, 2) if abs(dx) == 2 else (4 - abs(dx),)):
                        self.put(tx + dx, y, tz + dz, "white_wool")
            for dz in (-2, 2):
                for y in (1, 2, 3):
                    self.put(tx, y, tz + dz, fence)
        # the Bearer stands over the fallen standard, the host's key on him
        self.mob_at("standard_bearer", 0, 1, -179, yaw=0)
        self.mob_at("rime_knight", -5, 1, -176, yaw=0)
        self.mob_at("rime_knight", 5, 1, -176, yaw=0)
        self.mob_at("frost_chaplain", 0, 1, -184, yaw=0)

    def bridge(self):
        z0, z1 = -186, -228
        super().bridge()
        B, r = self.b.B, self.r
        for z in range(z1, z0 + 1):                       # the deck widened to seven, the rail a block out
            for x in range(-3, 4):
                B[(x, 0, z)] = IBR
                B[(x, -1, z)] = slab("top")
                for y in (1, 2):
                    if B.get((x, y, z), "").startswith(A + "icebound_brick_wall") or B.get((x, y, z), "").startswith("snow"):
                        del B[(x, y, z)]
            for x in (-4, 4):
                B[(x, 0, z)] = IBR
                B[(x, -1, z)] = slab("top")
                B[(x, 1, z)] = A + "icebound_brick_wall[east=none,north=low,south=low,up=true,waterlogged=false,west=none]" if r.random() < 0.7 else "snow[layers=2]"
                for y in range(1, 9):
                    self.carve((x, y, z), "glacier")
        for z in range(z0 - 4, z1 + 2, -7):               # the piers and lantern posts moved out with it
            for x in (-4, 4):
                for y in range(-26, 0):
                    B[(x, y, z)] = IBR
                B[(x, 1, z)] = IBR
                B[(x, 2, z)] = "lantern[hanging=false,waterlogged=false]"
            for x in (-3, 3):
                if "lantern" in B.get((x, 2, z), ""):
                    del B[(x, 2, z)]
                if B.get((x, 1, z)) == IBR:
                    del B[(x, 1, z)]
        # the archers that held the far ledge brought onto the road's end, where a sword can reach them
        self.marks["mobs"] = [m for m in self.marks["mobs"] if not (m[0].endswith("frostbound_archer") and abs(m[1][0]) > 5 and m[1][2] < z1)]
        for x in (-3, 3):
            self.mob_at("frostbound_archer", x, 1, z1 + 4, yaw=0)
        self.mob_at("rime_knight", -2, 1, z1 - 3, yaw=0)
        self.mob_at("rime_knight", 2, 1, z1 - 5, yaw=0)

    def gate_wall(self):
        """a wall of ice brick across the bridge's near end, a 7 x 7 door in it, barred till the Bearer falls"""
        B = self.b.B
        door = {(x, y) for x in range(-3, 4) for y in range(1, 8)}
        for z in (SEAL_Z, SEAL_Z - 1):
            for (x, y, zz) in list(self.air):
                if zz == z and y >= 1 and (x, y) not in door:
                    B[(x, y, z)] = IBR
            for x in range(-4, 5):
                for y in range(1, 9):
                    if (x, y) not in door:
                        B[(x, y, z)] = IBR
        for x in range(-4, 5):
            B[(x, 8, SEAL_Z + 1)] = A + "icebound_brick_stairs[facing=north,half=top,shape=straight,waterlogged=false]"
        seal = []
        for (x, y) in sorted(door):
            self.carve((x, y, SEAL_Z), "glacier")
            self.carve((x, y, SEAL_Z - 1), "glacier")
            B.pop((x, y, SEAL_Z - 1), None)
            B.pop((x, y, SEAL_Z), None)
            if not os.environ.get("OPEN_SEAL"):
                B[(x, y, SEAL_Z)] = BARS
            seal.append((x, y, SEAL_Z))
        self.marks["seal"] = seal
        for x in (-6, 6):                                 # a fire each side of the door, if the cave reaches that far
            if (x, 1, SEAL_Z + 3) in self.air:
                self.fire(x, 1, SEAL_Z + 3)

    def field(self):
        super().field()
        z0 = -232
        for x in range(-3, 4):
            for y in range(1, 8):
                for z in (z0 + 1, z0 + 2):
                    self.carve((x, y, z), "glacier")
                    self.b.B.pop((x, y, z), None)

    def build(self):
        self.watch_gate()
        self.long_march()
        self.fallen_standard()
        self.bridge()
        self.field()
        for (za, zb) in ((-146, -156), (-178, -197), (-221, -234)):
            self.room(-3, 1, za, 3, 7, zb, zone="glacier")
            for z in range(zb, za + 1):
                for x in range(-3, 4):
                    if self.b.B.get((x, 0, z)) is None:
                        self.put(x, 0, z, FLAG)
                    for y in range(1, 8):
                        if self.b.B.get((x, y, z)) in ("white_wool", "packed_ice", IBR) and abs(x) <= 3:
                            del self.b.B[(x, y, z)]
        self.gate_wall()
        # lanterns hung on chains under the ice the length of the road, over the camp and the parade ground
        efkit.hang_grid(self, {"fort", "glacier"}, "lantern[hanging=true,waterlogged=false]", "chain[axis=y,waterlogged=false]",
                        every=5, height=5, phase=(2, 2))
        dressing = dict(self.b.B)
        self.shell()
        self.b.B.update(dressing)
        self.skin()
        for p in self.air:
            if self.b.B.get(p) == F0.GICE:
                del self.b.B[p]
        return self.b


def points(t):
    pts = F0.points(t)
    for i, p in enumerate(t.marks.get("seal", [])):
        pts["seal:%d" % i] = p
    return pts


SHOTS = dict(F0.SHOTS)
SHOTS["seal"] = ((0, 4, -170), (0, 3, -190), 14)

if __name__ == "__main__":
    T = FrostEF(seed=int(os.environ.get("SEED", "7")))
    b = T.build()
    live = sum(1 for m in T.marks["mobs"] if not m[3])
    print("blocks", len(b.B), "mobs", len(T.marks["mobs"]), "live", live, "chests", len(T.marks["loot"]))
    if "--game" in sys.argv:
        efkit.export(b, "gate_frost", points(T), "icebound_bricks")
        sys.exit(0)
    shots = {k: v for k, v in SHOTS.items() if len(sys.argv) < 2 or k in sys.argv[1:]}
    K.preview(b, "gate_frost_ef", shots, sun=(30, -30), sky=(0.02, 0.03, 0.05), night=True, fog=0.006)
