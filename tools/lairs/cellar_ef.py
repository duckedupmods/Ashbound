"""The Drowned Cellar rebuilt at Epic Fight scale: the same seven places in the same order as the old one
(E:/Ashbound/tools/cellar.py has the story), every space sized for EF's fighting:

    1  the hoist vault     27 x 33, 10 tall              the Sodden Revellers
    2  the rack tunnels    three tunnels 7 wide, 9 tall  the Cask Brute down the middle one
    3  the tasting hall    29 x 41, 14 tall              the Drowned Vintners round the feast table
    4  the tun hall        37 x 53, walkway 9 wide       the Cellar Eels in the black water
    5  the bottle vault    25 x 35, aisles 7 wide        the Barrel Mimic (holds the key)
    6  the sluice          29 x 27, weir 7 wide          the seal: a 7 x 6 sluice gate
    7  the mother cistern  radius 20, 21 tall            the Cask Mother (6 tall)

Travel is toward -z; walk level y 1 down to the tun hall, LOW after it.

    python tools/lairs/cellar_ef.py [shots]     preview (render: blender -b -P E:/Ashbound/tools/blender/preview_struct.py -- gate_cellar_ef <shots>)
    python tools/lairs/cellar_ef.py --game      tools/lairs/stage/.../gate_cellar.bin, then python tools/port_gate.py cellar lair
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import efkit  # noqa: E402
from efkit import K  # noqa: E402
import cellar as C  # noqa: E402
from cellar import A, CBR, WCB, WBR, CFL, COAK, CHOOP, CHEAD, RACK, SLU, LAMP, stairs, slab, chain, fence, bars  # noqa: E402

LOW = -6


class CellarEF(C.Cellar):

    def hoist(self):
        """1: under the cask chute, split casks, ankle water; the Revellers."""
        self.hall(-13, 1, 0, 13, 10, -32, "hoist", vault=3)
        self.marks["tp"] = (0.5, 1.0, -5.5)
        for x in range(-1, 2):
            for z in range(-1, 2):
                for y in range(11, 22):
                    self.carve((x, y, z), "hoist")
        for y in range(5, 22):
            self.put(0, y, -1, chain())
        self.put(0, 4, -1, CHOOP)                        # a cask still hanging off the hoist chain
        self.put(1, 21, 0, CHOOP)
        self.put(-1, 21, 1, "barrel[facing=up,open=false]")
        self.pool(-12, -8, -7, -15, 0)
        self.pool(7, -18, 12, -26, 0)
        self.pool(-10, -24, -5, -29, 0)
        self.pool(-2, -10, 2, -13, 0)
        for (x, z) in ((-12, -2), (-12, -3), (-11, -2), (12, -2), (12, -3), (12, -10), (12, -11), (12, -12),
                       (-12, -19), (-12, -20), (-12, -21), (11, -30), (12, -30)):
            self.cask(x, 1, z)
        for (x, z) in ((-12, -2), (12, -2), (12, -11), (-12, -20)):
            self.cask(x, 2, z)
        for (x, z, f) in ((-4, -12, "east"), (5, -8, "west"), (3, -21, "north"), (-6, -26, "south")):
            self.put(x, 1, z, stairs(f, block=A + "cask_oak_stairs"))
        for (x, z) in ((-3, -16), (4, -15), (-5, -22), (7, -5)):
            self.put(x, 1, z, slab())
        for (x, z) in ((-6, -4), (8, -16), (0, -27)):
            self.put(x, 0, z, WBR)
        for z in (-14, -26):
            self.lamp(0, 13, z, 7)
        for sx in (-1, 1):
            self.mob(A + "sodden_reveller", 5 * sx, 1, -15)
            self.mob(A + "sodden_reveller", 6 * sx, 1, -24)
        self.mob(A + "sodden_reveller", 0, 1, -29)
        self.chest(-12, 1, -31, "east")

    def racks(self):
        """2: three bottle-rack tunnels joined by arches; the Cask Brute down the middle one."""
        z0, z1 = -33, -95
        for cx in (-10, 0, 10):
            self.hall(cx - 3, 1, z0, cx + 3, 7, z1, "racks", vault=2)
        for zc in (-48, -64, -80):
            self.hall(-13, 1, zc, 13, 6, zc - 4, "racks")
        for z in range(z0 - 6, z1, -10):
            for cx in (-10, 0, 10):
                self.lamp(cx, 9, z, 4)
        for (x, z) in ((-12, -56), (12, -72), (-8, -88), (2, -42)):
            self.cask(x, 1, z)
        for (x, z) in ((10, -41), (-10, -69), (0, -59), (0, -86), (-1, -86), (11, -90)):
            self.put(x, 0, z, WBR)
        self.mob(A + "cask_brute", 0, 1, -84, yaw=0)
        for (x, z) in ((-10, -42), (-9, -45), (10, -58), (11, -61), (-10, -86), (0, -52)):
            self.mob(A + "sodden_reveller", x, 1, z)
        self.chest(12, 1, -94, "west")

    def tasting(self):
        """3: the guild hall, the long table laid for a feast nobody finished; the Vintners."""
        z0, z1 = -96, -136
        self.hall(-14, 1, z0, 14, 11, z1, "hall", vault=3)
        r = self.r
        for z in range(-102, -130, -1):
            for x in (-1, 0, 1):
                self.put(x, 1, z, slab("top"))
                self.put(x, 2, z, "red_carpet" if x == 0 else None)
            if z % 2 == 0:
                for sx in (-1, 1):
                    if r.random() < 0.75:
                        self.put(sx * 2, 1, z, stairs("east" if sx < 0 else "west", block="dark_oak_stairs"))
                    elif r.random() < 0.5:
                        self.put(sx * 3, 1, z, stairs("north", "top", block="dark_oak_stairs"))
        for z in (-106, -114, -122):
            self.put(0, 2, z, "barrel[facing=up,open=false]")
        self.put(0, 1, -132, stairs("north", block="dark_oak_stairs"))
        for y in (1, 2):
            self.put(0, y, -133, "dark_oak_planks")
        self.put(0, 3, -133, CHEAD)
        for z in (-106, -118, -130):                     # chandeliers: a big lamp on a long drop, two smaller beside
            self.lamp(0, 14, z, 9)
            for sx in (-1, 1):
                self.lamp(sx * 3, 14, z, 8)
        for z in range(-98, -135, -3):
            for sx in (-1, 1):
                self.cask(sx * 13, 1, z)
                if r.random() < 0.4:
                    self.put(sx * 12, 0, z, WBR)
        for x in range(-3, 4):                           # the arch on into the tun hall
            for y in range(1, 8):
                self.carve((x, y, -137), "tuns")
            self.floor[(x, -137)] = 0
        self.mob(A + "drowned_vintner", -5, 1, -122, yaw=0)
        self.mob(A + "drowned_vintner", 5, 1, -110, yaw=0)
        for (x, z) in ((-5, -104), (6, -112), (-11, -114), (11, -124), (5, -128)):
            self.mob(A + "sodden_reveller", x, 1, z)
        self.chest(-13, 1, -135, "east")

    def tun_hall(self):
        """4: tuns standing in black water, a walkway on piers between them, a stair down to the far landing."""
        z0, z1 = -138, -190
        W = -9
        self.hall(-18, W + 1, z0, 18, 12, z1, "tuns", vault=3)
        B = self.b.B
        for x in range(-18, 19):
            for z in range(z1, z0 + 1):
                self.put(x, W + 1, z, "water")
                self.put(x, W + 2, z, "water")
                self.put(x, W, z, "mud")
                self.floor[(x, z)] = W

        def deck(x, z):
            self.put(x, 0, z, COAK if (x + z) % 3 else slab("top"))
            self.floor[(x, z)] = 0
        for z in range(z0, -172, -1):                    # nine wide, a fence each side: seven clear to fight on
            for x in range(-4, 5):
                deck(x, z)
            for sx in (-4, 4):
                if z % 2 == 0 and z < z0 - 1:
                    self.put(sx, 1, z, fence(north=True, south=True))
        for z in range(-166, -172, -1):                  # the spur to the stair
            for x in range(5, 14):
                deck(x, z)
        for x in range(-4, 14):
            for z in range(-171, z0 + 1):
                if B.get((x, 0, z), "").startswith(A + "cask") and x % 4 == 0 and z % 4 == 0:
                    for y in range(W + 1, 0):
                        self.put(x, y, z, WCB)
        for k in range(1, 7):                            # the stair down the east side, five wide
            z = -171 - k
            for x in range(9, 14):
                self.put(x, -k, z, stairs("south"))
                for y in range(W + 1, -k):
                    self.put(x, y, z, WCB)
                self.floor[(x, z)] = -k
        for x in range(-18, 19):                         # the far landing, dry, across the end of the hall
            for z in range(z1, -177):
                for y in range(W + 1, LOW):
                    self.put(x, y, z, WCB)
                self.put(x, LOW - 1, z, CFL)
                self.floor[(x, z)] = LOW - 1
        for (cx, cz) in ((-11, -147), (11, -147), (-11, -162), (11, -157)):
            self.tun(cx, cz, 4.6, W + 1, 5)
        self.tun(-11, -183, 5.2, LOW, 7)
        for z in range(-141, -172, -6):                  # lamps hung low over the walkway all the way along
            self.lamp(0, 15, z, 10)
        for (x, z) in ((3, -181), (-3, -188), (12, -186)):     # over the far landing
            self.lamp(x, 15, z, 16)
        for (x, z) in ((-15, -142), (15, -153), (-6, -153), (7, -164), (-15, -168), (15, -141), (-7, -172)):
            self.mob(A + "cellar_eel", x, W + 1, z)
        self.mob(A + "sodden_reveller", 1, 1, -150)
        self.mob(A + "sodden_reveller", -1, 1, -161)
        self.chest(-17, LOW, -189, "east")

    def bottle_vault(self):
        """5: aisles of racks near the ceiling, casks at the end - one the Mimic; the Cooper's Shop off the side."""
        z0, z1 = -191, -225
        self.hall(-12, LOW, z0, 12, LOW + 9, z1, "bottles", vault=2)
        for z in (-197, -203, -209, -215):
            for x in range(-11, 12):
                if abs(x) <= 3:
                    continue
                for y in range(LOW, LOW + 6):
                    self.put(x, y, z, RACK if (x + y) % 5 else CHOOP)
        for z in (-200, -212):
            for sx in (-1, 1):
                self.lamp(sx * 7, LOW + 10, z, 5)
        self.lamp(0, LOW + 11, -206, 6)
        for z in (-194, -206, -218):                     # down the side aisles between the rack rows
            for sx in (-1, 1):
                self.lamp(sx * 7, LOW + 10, z, 5)
        for x in range(-11, 12):
            if abs(x) <= 3:
                continue
            self.cask(x, LOW, -224)
            if abs(x) > 6:
                self.cask(x, LOW + 1, -224)
        self.mob(A + "barrel_mimic", 0, LOW, -219, yaw=0)
        for x in (-4, 4):                                # lamps over the casks where the Mimic waits
            self.lamp(x, LOW + 10, -220, 6)
        self.mob(A + "drowned_vintner", 6, LOW, -206, yaw=0)
        self.mob(A + "sodden_reveller", -6, LOW, -200)
        self.mob(A + "sodden_reveller", -7, LOW, -212)
        for z in (-205, -206, -207):                     # the Cooper's Shop, through a door in the west wall
            for y in range(LOW, LOW + 4):
                self.carve((-13, y, z), "cooper")
            self.floor[(-13, z)] = LOW - 1
        self.hall(-26, LOW, -199, -14, LOW + 5, -212, "cooper")
        self.put(-25, LOW, -201, "smithing_table")
        self.put(-25, LOW, -202, "grindstone[face=floor,facing=north]")
        self.put(-25, LOW, -210, "anvil[facing=east]")
        for (x, z) in ((-16, -200), (-17, -200), (-16, -211), (-22, -211)):
            self.put(x, LOW, z, CHOOP)
        for (x, z) in ((-21, -205), (-21, -206), (-21, -207)):
            self.put(x, LOW, z, slab(block=A + "cask_oak_slab"))
        self.lamp(-20, LOW + 5, -206, 1)
        self.chest(-25, LOW, -205, "east")
        self.chest(-25, LOW, -207, "east")

    def sluice(self):
        """6: the river's broken-in channel across the vault, the weir over it, the sluice gate shut."""
        z0, z1 = -226, -252
        self.hall(-14, LOW, z0, 14, LOW + 9, z1, "sluice", vault=2)
        for x in range(-14, 15):
            for z in range(-236, -243, -1):
                if abs(x) <= 3:
                    self.put(x, LOW - 1, z, CFL)
                    self.put(x, LOW - 2, z, WCB)
                    self.put(x, LOW - 3, z, WCB)
                    continue
                for y in (LOW - 1, LOW - 2, LOW - 3):
                    self.put(x, y, z, "water")
                self.put(x, LOW - 4, z, "mud")
        for sx in (-1, 1):
            for z in range(-236, -243, -1):
                for y in range(LOW - 3, LOW + 3):
                    self.put(sx * 15, y, z, bars("z") if y >= LOW else "water")
            for y in range(LOW - 3, LOW + 5):
                self.put(sx * 15, y, -235, SLU)
                self.put(sx * 15, y, -243, SLU)
            for z in range(-235, -244, -1):
                self.put(sx * 15, LOW + 4, z, SLU)
        for (x, z) in ((-11, -230), (11, -248), (12, -248)):
            self.put(x, LOW, z, CHOOP)
        for z in (-230, -248):
            for x in (-6, 0, 6):
                self.lamp(x, LOW + 11, z, 7)
        for sx in (-1, 1):                               # low over the channel either side of the weir
            self.lamp(sx * 9, LOW + 10, -239, 7)
        seal = []                                         # the sluice gate, shut till the Mimic falls
        for x in range(-3, 4):
            for y in range(LOW, LOW + 6):
                self.carve((x, y, z1 - 1), "cistern")
                if not os.environ.get("OPEN_SEAL"):
                    self.put(x, y, z1 - 1, bars("x"))
                seal.append((x, y, z1 - 1))
            self.floor[(x, z1 - 1)] = LOW - 1
        for sx in (-4, 4):
            for y in range(LOW, LOW + 7):
                self.put(sx, y, z1 - 1, SLU)
        for x in range(-4, 5):
            self.put(x, LOW + 6, z1 - 1, SLU)
        self.marks["seal"] = seal
        self.mob(A + "sodden_reveller", -6, LOW, -230)
        self.mob(A + "sodden_reveller", 6, LOW, -231)
        self.mob(A + "drowned_vintner", 0, LOW, -248, yaw=0)
        self.mob(A + "cellar_eel", -9, LOW - 3, -239)
        self.mob(A + "cellar_eel", 9, LOW - 3, -240)

    def cistern(self):
        """7: the round cistern, sluice mouths in the wall, tun-top platforms round the edge; the Cask Mother."""
        cx, cz, R = 0, -282, 20
        H = 21
        for x in range(cx - R, cx + R + 1):
            for z in range(cz - R, cz + R + 1):
                if math.hypot(x - cx, z - cz) <= R + 0.3:
                    for y in range(LOW, LOW + H):
                        self.carve((x, y, z), "cistern")
                    self.floor[(x, z)] = LOW - 1
        for z in range(cz + R - 2, -253):                # the passage in from the gate
            for x in range(-3, 4):
                for y in range(LOW, LOW + 7):
                    self.carve((x, y, z), "cistern")
                self.floor[(x, z)] = LOW - 1
        B = self.b.B
        for dx in range(-2, 3):                          # the drain in the middle: a grate over black water
            for dz in range(-2, 3):
                self.put(cx + dx, LOW - 1, cz + dz, "iron_trapdoor[facing=north,half=top,open=false,powered=false,waterlogged=false]")
                self.put(cx + dx, LOW - 2, cz + dz, "water")
                self.put(cx + dx, LOW - 3, cz + dz, "mud")
        for k in range(6):                               # six tun-top platforms, steps up toward the middle
            a = math.pi / 2 + (k + 0.5) * 2 * math.pi / 6
            px, pz = cx + 14.5 * math.cos(a), cz + 14.5 * math.sin(a)
            for x in range(int(px) - 5, int(px) + 6):
                for z in range(int(pz) - 5, int(pz) + 6):
                    d = math.hypot(x - px, z - pz)
                    if d > 3.6 or math.hypot(x - cx, z - cz) > R:
                        continue
                    self.put(x, LOW, z, CHOOP if d > 2.8 else COAK)
                    self.put(x, LOW + 1, z, COAK)
                    self.put(x, LOW + 2, z, slab())
            ux, uz = -math.cos(a), -math.sin(a)
            ax, az = (0, 1 if uz > 0 else -1) if abs(uz) > abs(ux) else (1 if ux > 0 else -1, 0)
            f = {(0, 1): "north", (0, -1): "south", (1, 0): "west", (-1, 0): "east"}[(ax, az)]
            x, z = int(round(px)), int(round(pz))
            while B.get((x, LOW, z)) in (CHOOP, COAK):
                x, z = x + ax, z + az
            for w in (-2, -1, 0, 1, 2):
                wx, wz = (w, 0) if az else (0, w)
                if B.get((x + wx - ax, LOW, z + wz - az)) in (CHOOP, COAK):
                    self.put(x + wx, LOW + 1, z + wz, stairs(f, block=A + "cask_oak_stairs"))
                    self.put(x + wx + ax, LOW, z + wz + az, stairs(f, block=A + "cask_oak_stairs"))
                    self.put(x + wx, LOW, z + wz, COAK)
        for k in range(4):                               # the sluice mouths: four grated arches, five wide
            a = k * math.pi / 2 + math.pi / 4
            mx, mz = cx + (R + 1) * math.cos(a), cz + (R + 1) * math.sin(a)
            for dx in (-2, -1, 0, 1, 2):
                for y in range(LOW, LOW + 6):
                    x, z = int(round(mx + dx * -math.sin(a))), int(round(mz + dx * math.cos(a)))
                    self.put(x, y, z, bars("z" if abs(math.cos(a)) > 0.5 else "x") if y < LOW + 5 else SLU)
        efkit.dome(self, cx, cz, R, LOW + H - 1, 9, "cistern")
        self.lamp(cx, LOW + H + 8, cz, 22)
        for k in range(6):                               # a lamp low over each tun-top platform
            a = math.pi / 2 + (k + 0.5) * 2 * math.pi / 6
            x, z = int(round(cx + 14.5 * math.cos(a))), int(round(cz + 14.5 * math.sin(a)))
            top = max(y for y in range(LOW, LOW + H + 12) if (x, y, z) in self.air)
            self.lamp(x, top, z, top - (LOW + 8))
        for k in range(6):                               # and a ring of them over the fighting floor
            a = (k + 0.0) * 2 * math.pi / 6
            x, z = int(round(cx + 8 * math.cos(a))), int(round(cz + 8 * math.sin(a)))
            top = max(y for y in range(LOW, LOW + H + 12) if (x, y, z) in self.air)
            self.lamp(x, top, z, top - (LOW + 5))
        for (dx, dz, drop) in ((-7, 5, 8), (8, -4, 10), (3, 9, 7), (-9, -8, 9)):
            top = max(y for y in range(LOW, LOW + H + 12) if (cx + dx, y, cz + dz) in self.air)
            for y in range(top - drop - 3, top + 1):
                self.put(cx + dx, y, cz + dz, chain())
        self.marks["boss"] = (0.5, float(LOW), cz - 8.5)
        self.marks["exit"] = (0.5, float(LOW), cz - 13.5)

    def architecture(self):
        """ribs, piers and arcades: the depth that keeps big rooms from reading as brick boxes"""
        rib = efkit.rib
        for z in (-8, -20):                                          # the hoist vault
            rib(self, "z", z, -13, 13, 6)
        for z in (-43, -55, -72, -86):                               # the rack tunnels, each its own ribs
            for cx in (-10, 0, 10):
                rib(self, "z", z, cx - 3, cx + 3, 4)
        for z in range(-100, -134, -8):                              # the tasting hall: a nave and two aisles
            for sx in (-1, 1):
                efkit.column(self, sx * 8, z, sx * 9, z - 1)
            rib(self, "z", z, -7, 7, 7, pilaster=False)
            rib(self, "z", z, 10, 14, 4)
            rib(self, "z", z, -14, -10, 4)
        for sx in (-1, 1):                                           # ...arcades between the piers
            for z in range(-102, -134, -8):
                rib(self, "x", sx * 8, z - 5, z, 5, pilaster=False)
                rib(self, "x", sx * 9, z - 5, z, 5, thick=1, pilaster=False)
        for z in (-146, -159, -172):                                 # the tun hall, piers up out of the water
            rib(self, "z", z, -18, 18, 4)
        for z in (-197, -203, -209, -215):                           # the bottle vault: arches over the rack rows
            rib(self, "z", z, -12, 12, LOW + 6, thick=1)
        for z in (-234, -244):                                       # the sluice, flanking the channel
            rib(self, "z", z, -14, 14, LOW + 5)
        import math                                                  # the cistern's buttresses
        cx, cz, R = 0, -282, 20
        for k in range(8):
            a = math.radians(22.5 + 45 * k)
            cells = []
            for rr in (R - 1.2, R - 0.4, R + 0.4):
                for w in (-1, 0, 1):
                    x = int(math.floor(cx + rr * math.cos(a) - w * math.sin(a)))
                    z = int(math.floor(cz + rr * math.sin(a) + w * math.cos(a)))
                    cells += [(x, y, z) for y in efkit.plane(self, "z", z, x)[0]]
            efkit.solidify(self, cells)

    def build(self):
        self.hoist()
        self.racks()
        self.tasting()
        self.tun_hall()
        self.bottle_vault()
        self.sluice()
        self.cistern()
        self.architecture()
        efkit.wall_lights(self, {"hoist", "racks", "hall", "tuns", "bottles", "cooper", "sluice"}, A + "cellar_sconce", every=6)
        efkit.wall_lights(self, {"cistern"}, A + "cellar_sconce", every=4)
        dressing = dict(self.b.B)
        self.shell()
        self.b.B.update(dressing)
        self.skin()
        for p in self.air:
            if self.b.B.get(p) in (CBR, "air"):
                del self.b.B[p]
        return self.b


SHOTS = {
    "hoist": ((0, 4, -2), (0, 2, -32), 13),
    "racks": ((0, 3.5, -34), (0, 2, -95), 12),
    "hall": ((0, 5, -97), (0, 1, -136), 13),
    "tuns": ((0, 4, -139), (0, -4, -180), 14),
    "tuns_high": ((14, -3, -188), (0, -6, -150), 14),
    "bottles": ((0, -2, -192), (0, -5, -225), 12),
    "sluice": ((0, -2, -227), (0, -6, -252), 12),
    "cistern": ((0, 0, -256), (0, -6, -290), 14),
}

if __name__ == "__main__":
    T = CellarEF(seed=int(os.environ.get("SEED", "7")))
    b = T.build()
    print("blocks", len(b.B), "mobs", len(T.marks["mobs"]), "chests", len(T.marks["loot"]))
    if "--game" in sys.argv:
        efkit.export(b, "gate_cellar", C.points(T), "cellar_lamp")
        sys.exit(0)
    shots = {k: v for k, v in SHOTS.items() if len(sys.argv) < 2 or k in sys.argv[1:]}
    K.preview(b, "gate_cellar_ef", shots, sun=(30, -30), sky=(0.02, 0.02, 0.025), night=True, fog=0.004)
