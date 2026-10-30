"""Textured Blender previews of parts of Highmourn (walls, gate, kings) on their own ground.

    python tools/capital_preview.py walls        -> E:/Ashbound/tools/renders/struct/hm_walls.obj (+ shots)
    E:/Steam/steamapps/common/Blender/blender.exe -b -P E:/Ashbound/tools/blender/preview_struct.py -- hm_walls [shot ...]
"""
import os
import sys

sys.path.insert(0, "E:/Ashbound/tools")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import structkit as K  # noqa: E402
import city_highmourn as CH  # noqa: E402
import capital_land as L  # noqa: E402
import capital_walls as WL  # noqa: E402
import capital_kings as KG  # noqa: E402
import capital_pair as PR  # noqa: E402
import capital_city as CY  # noqa: E402

S = K.Build(41)
CH.S, CH.put, CH.box, CH.pick = S, S.put, S.box, S.pick
WL.S, WL.put, WL.pick = S, S.put, S.pick
KG.S, KG.put, KG.pick = S, S.put, S.pick
PR.S, PR.put, PR.pick = S, S.put, S.pick
CY.S, CY.put, CY.pick = S, S.put, S.pick


def ground_box(x0, z0, x1, z1):
    """The land's surface in the box as blocks (grass, stone up the slopes, water already laid by the builders)."""
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            h = L.ground(x, z)[0]
            for y in range(h - 2, h + 1):
                if (x, y, z) not in S.B:
                    S.put(x, y, z, "grass_block[snowy=false]" if y == h else "dirt")


SHOTS = {
    "walls": {
        "gate": ((-30, 12, 300), (0, 30, 180), 22),
        "bridge": ((-40, 3, 199), (0, -2, 197), 22),
        "gateair": ((-60, 50, 260), (0, 4, 196), 24),
        "deck": ((0, 9, 236), (0, 4, 186), 24),
        "front": ((-20, 4, 250), (-4, 40, 180), 24),
        "wall": ((-60, 6, 260), (-110, 30, 160), 22),
        "barbican": ((-40, 6, 250), (0, 16, 200), 20),
        "curtain": ((-150, 10, 230), (-120, 24, 150), 22),
        "aerial": ((-160, 120, 330), (-20, 10, 140), 26),
        "inside": ((40, 10, 90), (60, 26, 150), 22),
        "tower": ((-95, 40, 210), (-74, 40, 167), 20),
    },
    "river": {
        "weir": ((128, 10, 178), (150, -2, 138), 24),
        "gate": ((175, 25, 190), (148, 6, 140), 24),
    },
    "falls": {
        "front": ((70, 70, -60), (70, 90, -200), 26),
        "pool": ((100, 58, -150), (70, 62, -200), 24),
        "side": ((125, 80, -130), (70, 100, -205), 26),
        "far": ((40, 60, 40), (70, 100, -200), 28),
    },
    "lake": {
        "shore": ((20, 12, -40), (90, 0, 20), 24),
        "aerial": ((-10, 90, 140), (100, 0, 20), 26),
        "beach": ((60, 6, 110), (100, 0, 60), 24),
    },
    "pair": {
        "road": ((10, 14, 660), (10, 105, 322), 24),
        "angel": ((-96, 80, 540), (-96, 100, 322), 26),
        "devil": ((118, 80, 540), (118, 100, 322), 26),
        "under": ((8, 14, 352), (8, 118, 322), 18),
        "aerial": ((-120, 170, 520), (10, 60, 322), 24),
        "aface": ((-96, 166, 392), (-96, 158, 322), 24),
        "dface": ((118, 166, 392), (118, 156, 322), 24),
    },
    "city": {
        "gate": ((0, 6, 171), (-8, 5, 130), 24),
        "high": ((-2, 3, 152), (-14, 5, 122), 22),
        "market": ((-16, 8, 123), (-32, 3, 86), 24),
        "fountain": ((-21, 9, 124), (-21, 17, 92), 24),
        "maiden": ((-21, 13, 108), (-21, 12, 92), 24),
        "lane": ((-50, 4, 97), (-110, 5, 94), 22),
        "aerial": ((40, 80, 175), (-40, 0, 100), 24),
        "horn": ((-120, 42, 72), (-165, 0, 38), 26),
        "horngate": ((-108, 4, 41), (-140, 6, 40), 26),
        "soup": ((-147, 12, 52), (-160, 2, 40), 30),
        "ashrow": ((-176, 3, 37), (-200, 4, 36), 24),
        "backs": ((-60, 45, 165), (-60, 0, 120), 24),
        "plan": ((-45, 170, 101), (-45, 0, 100), 30),
        "plan2": ((-75, 330, 96), (-75, 0, 95), 30),
        "green": ((-86, 9, 131), (-108, 7, 119), 24),
        "inn": ((-95, 4, 123), (-112, 8, 120), 24),
        "lakeq": ((150, 55, 150), (105, 0, 62), 28),
        "stilts": ((80, 5, 66), (90, 2, 92), 24),
        "row": ((70, 4, 106), (88, 4, 86), 24),
        "beacon": ((126, 3, 82), (128, 21, 36), 30),
        "watermill": ((172, 4, 101), (156, 3, 101), 26),
        "quay": ((52, 9, 58), (30, 2, 82), 24),
        "mill": ((30, 4, 93), (55, 5, 124), 22),
        "wall": ((-52, 4, 48), (-95, 5, 55), 22),
        "terrace": ((0, 40, -10), (0, 30, -105), 28),
        "guild": ((-30, 24, -70), (0, 40, -104), 30),
        "hall": ((14, 22, -80), (-4, 26, -104), 26),
        "stair": ((0, 5, -54), (0, 16, -84), 24),
        "skyline": ((70, 30, 50), (0, 52, -104), 30),
        "yard": ((-56, 38, -78), (-56, 20, -110), 26),
        "gatehall": ((-6, 25, -103), (-20, 22, -116), 24),
        "trophy": ((7, 26, -110), (21, 27, -110), 14),
        "trophy2": ((8, 25, -103), (20, 25, -112), 14),
        "walkw": ((-90, 26, -80), (-130, 24, -100), 24),
        "citstair": ((16, 34, -124), (0, 52, -152), 20),
        "bankw": ((-120, 18, -15), (-120, 8, -80), 22),
        "bankc": ((-50, 9, -48), (-80, 9, -78), 24),
        "wards": ((-40, 70, 50), (-120, 0, -25), 18),
        "forge": ((-62, 16, -8), (-92, 8, -50), 22),
        "hearth": ((-92, 34, 34), (-120, 2, 0), 22),
        "wardtop": ((-115, 190, 10), (-115, 0, -14), 16),
        "herofront": ((0, 74, -150), (0, 62, -201), 20),
        "herohall": ((0, 54, -214), (0, 50, -250), 14),
        "citadel": ((40, 80, 30), (0, 72, -165), 26),
        "court": ((0, 76, -140), (0, 52, -176), 18),
        "keep": ((-26, 82, -112), (-54, 62, -168), 22),
        "sanct": ((36, 82, -112), (40, 60, -168), 22),
        "apse": ((84, 52, -148), (56, 56, -169), 22),
        "citwall": ((-60, 30, -118), (-60, 50, -155), 22),
    },
    "kings": {
        "road": ((10, 8, 470), (10, 60, 322), 26),
        "west": ((-30, 30, 380), (-50, 70, 322), 24),
        "face": ((-42, 92, 372), (-50, 84, 322), 20),
        "front": ((-50, 60, 440), (-50, 62, 322), 24),
        "hand": ((-10, 100, 372), (-71, 100, 335), 22),
        "high": ((10, 140, 520), (10, 40, 300), 26),
    },
}

if __name__ == "__main__":
    what = sys.argv[1]
    if what == "walls":
        segs = WL.segments()
        for A, B, n, i in segs:
            if max(A[0], B[0]) > -200 and min(A[0], B[0]) < 120 and max(A[1], B[1]) > 60:
                WL.curtain(A, B, n, i, 0)
        for a, plan, h, sgn, k, hw in WL.TOWERS:
            x, z = WL.ell_pt(a)
            if -200 < x < 120 and z > 60:
                WL.tower(x, z, plan, h, 0, (x / L.RX ** 2, z / L.RZ ** 2), hw=hw)
        WL.gatehouse()
        WL.moat()
        ground_box(-200, 40, 120, 340)
    elif what in ("river", "falls", "lake", "city"):
        import capital as C
        S = C.S
        WL.S, WL.put, WL.pick = S, S.put, S.pick
        box = {"river": (90, 90, 210, 230), "falls": (20, -330, 120, -40), "lake": (-30, -80, 230, 120),
               "city": (-215, -262, 215, 200)}[what]
        for x in range(box[0], box[2] + 1):
            for z in range(box[1], box[3] + 1):
                C.H[(x, z)] = L.ground(x, z)[0]
        C.water()
        for A, B, n, i in WL.segments():
            if max(A[0], B[0]) > box[0] and min(A[0], B[0]) < box[2] and max(A[1], B[1]) > box[1] and min(A[1], B[1]) < box[3]:
                WL.curtain(A, B, n, i, 0)
        WL.moat()
        if what == "city":
            WL.gatehouse()
            CY.S, CY.put, CY.pick = S, S.put, S.pick
            PR.S, PR.put, PR.pick = S, S.put, S.pick
            CY.build(lambda x, z: C.H.get((x, z), 0))
            C.unfloat()
        for x in range(box[0], box[2] + 1):
            for z in range(box[1], box[3] + 1):
                h = C.H[(x, z)]
                nb = [C.H.get((x + dx, z + dz), h) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))]
                steep = max(abs(v - h) for v in nb) >= 2
                for y in range(min(min(nb), h) - 1, h + 1):
                    if (x, y, z) not in S.B:
                        S.put(x, y, z, "stone" if steep or h - y > 3 else "grass_block[snowy=false]" if y == h else "dirt")
    elif what == "pair":
        PR.build(lambda x, z: L.ground(x, z)[0])
        ground_box(-260, 220, 290, 680)
    elif what == "kings":
        KG.build(lambda x, z: L.ground(x, z)[0])
        ground_box(-110, 260, 140, 520)
    for k, v in list(S.B.items()):
        if v.endswith("#flow"):
            S.B[k] = v[:-5]
    print("blocks", len(S.B))
    sun = {"falls": (30, 35), "lake": (40, 20)}.get(what, (40, -130))
    K.preview(S, "hm_" + what, SHOTS[what], sun=sun, sky=(0.55, 0.68, 0.85))
