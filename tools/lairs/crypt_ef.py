"""The Crypt rebuilt at Epic Fight scale: the same walk down under the abbey as the old one
(E:/Ashbound/tools/crypt.py has the story). The big rooms already stood tall enough (the standing dead 8, the chapel
10, the nave 14 for the 7.6-tall Pale Abbot); the halls between them were the trouble:

    3  the niche halls   corridors 5 wide and 7 tall (were 3 and 5), the niches in walls a block further out
       passages          6 tall everywhere (were 4), so a Coffin Knight follows you through them

    python tools/lairs/crypt_ef.py [shots]     preview (blender -b -P E:/Ashbound/tools/blender/preview_struct.py -- gate_crypt_ef <shots>)
    python tools/lairs/crypt_ef.py --game      stage the bin, then python tools/port_gate.py crypt lair
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import efkit  # noqa: E402
from efkit import K  # noqa: E402
import crypt as C0  # noqa: E402
from crypt import A, NF, VIGIL, candle  # noqa: E402


class CryptEF(C0.Crypt):

    def hall(self, x0, z0, x1, z1, fl, h, zone, vault=0):
        if zone == "pass":
            h = max(h, 6)
        super().hall(x0, z0, x1, z1, fl, h, zone, vault)

    def descend(self, x0, x1, c0, n, fl, h, zone, d=(0, -1), block=A + "crypt_stone_stairs"):
        return super().descend(x0, x1, c0, n, fl, max(h, 6), zone, d, block)

    def niche_halls(self):
        """3: a grid of corridors walled in burial niches, five wide and seven tall; the Ghouls feeding."""
        F = self.stair_end
        assert F == NF, F
        self.hall(-2, -40, 2, -78, F, 7, "niches", vault=1)
        for zc in (-47, -61, -74):
            self.hall(-14, zc + 2, 14, zc - 2, F, 7, "niches", vault=1)
        for xc in (-12, 12):
            self.hall(xc - 2, -45, xc + 2, -76, F, 7, "niches", vault=1)
        self.hall(-19, -52, -15, -57, F, 5, "niches")                       # a dead-end vault off the west walk
        r = self.r
        for z in range(-41, -78, -2):                                       # some niches open, the dead in them
            for sx in (-3, 3):
                if r.random() < 0.45 and not any(abs(z - zc) <= 3 for zc in (-47, -61, -74)):
                    y = F + r.choice((2, 4, 6))
                    self.carve((sx, y, z), "niches")
                    self.put(sx, y, z, r.choice(("skeleton_skull[rotation=%d]" % (4 if sx < 0 else 12), "bone_block[axis=x]",
                                                  "light_gray_carpet", candle(r.randint(1, 3)))))
        for zc in (-47, -61, -74):                                          # candles at the crossings, lanterns over them
            for xc in (0, -12, 12):
                for (dx, dz) in ((-2, 2), (2, -2), (-2, -2), (2, 2)):
                    self.put(xc + dx, F + 1, zc + dz, candle(r.randint(2, 4)))
                self.lamp(xc, F + 8, zc, 2)
        for z in range(-50, -74, -4):                                       # and down the walks between
            for xc in (-12, 0, 12):
                if any(abs(z - zc) <= 2 for zc in (-47, -61, -74)):
                    continue
                self.put(xc + (2 if z % 8 else -2), F + 1, z, VIGIL)
                self.lamp(xc, F + 8, z, 2)
        for z in (-53, -56):
            self.put(-18, F + 1, z, "light_gray_carpet")
            self.put(-17, F + 1, z, "light_gray_carpet")
        self.wax(-19, F, -57, 1, lit=1.0)
        self.chest(-19, F + 1, -54, "east")
        for (x, z) in ((0, -52), (-12, -66), (12, -55), (5, -74)):
            self.mob(A + "ghoul", x, F + 1, z)
        for (x, z) in ((-7, -61), (-6, -60), (8, -47), (9, -46)):
            self.mob(A + "grave_rat", x, F + 1, z)


    def build(self):
        self.lychyard()
        self.candle_stair()
        self.niche_halls()
        self.standing_dead()
        self.weeping_chapel()
        self.sextons_yard()
        self.nave()
        # lanterns on poles over the open graves and the churchyard, where the candles don't reach
        pole = lambda x, fl, z: self.pole_lamp(x, fl, z)  # noqa: E731
        efkit.light_grid(self, {"sexton"}, pole, every=6, keep_clear=lambda x, z: abs(x) <= 2, phase=(3, 1))
        efkit.light_grid(self, {"yard", "ruin"}, pole, every=6, keep_clear=lambda x, z: abs(x) <= 1, phase=(3, 2))
        dressing = dict(self.b.B)
        self.shell()
        self.b.B.update(dressing)
        self.open_yard()
        self.skin()
        for (x, z) in sorted(self.bank_cols):
            inner = any((x + dx, z + dz) in self.yard_cols for dx in (-1, 0, 1) for dz in (-1, 0, 1))
            if inner and self.b.B.get((x, C0.YARD_TOP, z)) and (x, C0.YARD_TOP + 1, z) not in self.b.B:
                self.put(x, C0.YARD_TOP + 1, z, "iron_bars[east=false,north=false,south=false,waterlogged=false,west=false]")
        for p in self.air:
            if self.b.B.get(p) == "air":
                del self.b.B[p]
        return self.b


SHOTS = dict(C0.SHOTS)

if __name__ == "__main__":
    T = CryptEF(seed=int(os.environ.get("SEED", "7")))
    b = T.build()
    print("blocks", len(b.B), "mobs", len(T.marks["mobs"]), "chests", len(T.marks["loot"]))
    if "--game" in sys.argv:
        K.settle(b, keep_islands=40, report=False)
        cols = T.yard_cols | T.bank_cols
        for (x, z) in cols:
            b.B.setdefault((x, C0.LID, z), "minecraft:barrier")
        ring = {(x + dx, z + dz) for (x, z) in cols for dx in (-1, 0, 1) for dz in (-1, 0, 1)} - cols
        for (x, z) in ring:
            for y in range(C0.YARD_TOP, C0.LID + 1):
                b.B.setdefault((x, y, z), "minecraft:barrier")
        efkit.export(b, "gate_crypt", C0.points(T), "vigil_candles")
        sys.exit(0)
    shots = {k: v for k, v in SHOTS.items() if len(sys.argv) < 2 or k in sys.argv[1:]}
    K.preview(b, "gate_crypt_ef", shots, sun=(24, -60), sky=(0.14, 0.14, 0.17), night=True, fog=0.004)
