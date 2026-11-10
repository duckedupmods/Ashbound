"""Checks Highmourn's planting never gets in the players' way: builds the city as capital.py does, plants it, and
lists every tree block that's low over a paved way (under 4 above it), near a door under head height, or put where a
solid block of the city stood.
    python tools/green_check.py
"""
import capital as C
import capital_city as CY
import capital_green as G

T, M, Wt, Bl, Bi = C.grid()
C.water()
C.WL.build(lambda x, z: C.H.get((x, z), 0))
C.PR.build(lambda x, z: C.H.get((x, z), 0))
CY.S, CY.put, CY.pick = C.S, C.S.put, C.S.pick
C.PR.S, C.PR.put, C.PR.pick = C.S, C.S.put, C.S.pick
CY.build(lambda x, z: C.H.get((x, z), 0))
C.unfloat()
before = dict(C.S.B)
G.plant(C.S, C.H, C.S.marks)
H = C.H
paved = {}
for (x, y, z), st in before.items():
    n = st.split("[")[0].split(":")[-1]
    if not G.soft(st) and n not in G.SOIL and "water" not in st and y <= H.get((x, z), 0) + 1:
        paved[(x, z)] = True
doors = set()
for (x, y, z), st in before.items():
    n = st.split("[")[0]
    if n.endswith("_door"):
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                doors.add((x + dx, z + dz))
bad = {"low over paving": [], "at a door": [], "replaced a solid block": []}
for k, st in C.S.B.items():
    if before.get(k) == st:
        continue
    n = st.split("[")[0]
    if "leaves" not in n and "wood" not in n and "blossom" not in n:
        continue
    x, y, z = k
    g = H.get((x, z), 0)
    old = before.get(k)
    if old is not None and not G.soft(old) and old.split("[")[0].split(":")[-1] not in G.SOIL:
        bad["replaced a solid block"].append((k, old, st))
    bed = "greystone_slab" in C.S.B.get((x, g + 1, z), "") or C.S.B.get((x, g + 1, z), "").startswith("grass_block")
    if (x, z) in paved and 0 < y - g < 4 and not bed:
        bad["low over paving"].append((k, st))
    if (x, z) in doors and 0 < y - g < 4:
        bad["at a door"].append((k, st))
for w, l in bad.items():
    print(w, len(l), l[:6])
