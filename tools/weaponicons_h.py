"""The bows, drawn over their slot renders (see tools/weaponicons.py). Each starts from the bent frame in
weaponicons_bowkit.py (bulgy, flat or heavy) and gets its own colours, grip, tips and trimmings."""
from weaponicons import I
from weaponicons_bowkit import frame

BULGY = dict(c=(3, 3), thick=1.5, grip=0.2)
FLAT = dict(c=(4.6, 4.6), thick=1.4, grip=0.2)
HEAVY = dict(c=(2.6, 2.6), thick=2.0, grip=0.22)


def bow(name, pal, shape=BULGY, marks=()):
    g = [list(r) for r in frame(**shape)]
    for y, x, c in marks:
        if g[y][x] not in ".w":      # trimmings only ever sit on the limb or its edge
            g[y][x] = c
    I(name, pal, "\n".join("".join(r) for r in g))


# where things sit on the bulgy frame: the grip, the two limbs, the tips
GRIP = [(3, 5), (4, 4), (4, 5), (5, 3), (5, 4), (5, 5)]
UP = [(1, 8), (1, 9), (1, 10), (2, 7), (2, 9), (2, 11)]
DOWN = [(8, 1), (9, 1), (10, 1), (7, 2), (9, 2), (11, 2)]


def at(cells, c):
    return [(y, x, c) for y, x in cells]


bow("hoop_bow", "o=140c06 h=8a5a30 s=6a4222 d=4a2e18 g=2a1a0e t=4a2e18 w=c8b090 i=5a5e68", HEAVY, [(2, 9, "i"), (9, 2, "i"), (3, 7, "i"), (7, 3, "i")])

bow("undertow_bow", "o=0e1408 h=4a6a2a s=2e4a1e d=1e3214 g=8a6a30 t=1e3214 w=c8b090 y=e0f060", BULGY, [(1, 9, "y"), (2, 11, "y"), (8, 1, "y"), (10, 2, "y"), (6, 2, "y")])

bow("noose_bow", "o=0e0e12 h=6a6a62 s=4a4a44 d=34342e g=a89a6a t=34342e w=d8d0b0 r=a08a5a", FLAT, [(12, 3, "r"), (13, 2, "r"), (13, 4, "r"), (14, 3, "r"), (4, 6, "r"), (5, 5, "r")])

bow("long_drop", "o=0e0e10 h=5a564e s=3e3a34 d=2a2824 g=a89a6a t=e0d8b8 w=c8c0a0", FLAT, [(3, 8, "g"), (4, 7, "g"), (8, 3, "g"), (9, 2, "g")])

bow("yewrot_bow", "o=0e1008 h=3a6a2a s=2a4a1e d=1e3414 g=c86030 t=c86030 w=c86030 c=60f0a0", HEAVY, [(8, 2, "c"), (2, 8, "g"), (1, 9, "g")])

bow("antlerbow", "o=2a2414 h=f4ecd0 s=d0c4a0 d=a89c78 g=3a6a2a t=f4ecd0 w=c86030 c=60f0a0", HEAVY, [(4, 4, "c"), (0, 6, "h"), (0, 11, "h"), (6, 0, "h"), (11, 0, "h"), (1, 5, "o"), (5, 1, "o")])

bow("mourners_bow", "o=0e0e14 h=4a4a58 s=2a2a34 d=1a1a22 g=e8e4d8 t=1a1a22 w=e0e0e8 v=b0b8d0", BULGY, at(GRIP, "g") + [(7, 1, "v"), (8, 1, "v")])

bow("requiem", "o=1a1a24 h=e0e4f0 s=a8b0c4 d=6a7088 g=2a2a34 t=fff0a0 w=e8ecf4", BULGY, [(0, 13, "t"), (12, 0, "t")])

bow("tourniquet_bow", "o=1a1e24 h=d8e0e8 s=a0acb8 d=6e7a88 g=8a6a30 t=d8e0e8 w=d8e0e8", HEAVY, at(GRIP, "g"))

bow("suture_bow", "o=1a1814 h=d8ccb0 s=a89c80 d=6a5e48 g=3a2e20 t=d8ccb0 w=8a7a5a y=c0f060", BULGY, [(1, 9, "y"), (2, 7, "y"), (8, 1, "y"), (10, 1, "y"), (7, 2, "y")])

bow("shardstring_bow", "o=1a3040 h=f0faff s=c0dcec d=88b0cc g=d8a840 t=a0e0ff w=ffffff c=a0e0ff", HEAVY, [(0, 9, "c"), (0, 12, "c"), (9, 0, "c"), (12, 0, "c")])

bow("starfall_bow", "o=1a1408 h=fff0a0 s=e0c058 d=a88a30 g=1e2a50 t=ffffff w=d8c070 y=ffffff", BULGY, [(0, 13, "y"), (1, 14, "y"), (13, 0, "y"), (14, 1, "y"), (0, 15, "y"), (15, 0, "y")])

bow("brass_recurve", "o=2a1806 h=e8c058 s=c09838 d=8a6a20 g=8a6a20 t=e8c058 w=d8c070 c=60f0a0", HEAVY, [(4, 4, "c"), (4, 5, "c"), (5, 4, "c")])

bow("steam_arbalest", "o=0e0e12 h=5a5e68 s=3e424c d=2a2c34 g=b08a40 t=3e424c w=8a8e98 c=60f0a0 b=b08a40", HEAVY, [(9, 9, "o"), (9, 10, "c"), (10, 9, "c"), (10, 10, "o"), (8, 9, "b"), (11, 10, "b"), (5, 5, "b"), (6, 6, "b"), (7, 7, "b"), (8, 8, "b")])

bow("bellows_bow", "o=140c06 h=6a4a2a s=4e321a d=34200e g=2a2a30 t=4e321a w=c8b090 e=ffb040", HEAVY, [(1, 10, "e"), (2, 9, "e"), (9, 2, "e"), (11, 1, "e")])

bow("frostbound_longbow", "o=1e3048 h=e0f0ff s=a0c8e8 d=6a98c0 g=2a4060 t=ffffff w=e8f4ff c=a0e0ff", FLAT, [(2, 8, "c"), (8, 2, "c")])

bow("hoarfrost_bow", "o=2a4060 h=ffffff s=c8e4f8 d=90c0e8 g=60c0ff t=ffffff w=ffffff c=a0e0ff", HEAVY, at(GRIP, "c"))

bow("silkstring_bow", "o=0e0e12 h=e0e0e8 s=4a4a54 d=2a2a32 g=8a1c24 t=e0e0e8 w=e8e8f0", BULGY, [(1, 8, "h"), (2, 6, "h"), (6, 1, "h"), (9, 1, "h"), (4, 4, "g")])

bow("webcaster", "o=0e0a14 h=4a3e60 s=2a2440 d=1a1428 g=8a1c24 t=1a1428 w=d8d8e0", BULGY, [(6, 6, "w"), (7, 5, "w"), (5, 7, "w"), (4, 4, "g")])

bow("lampwick_bow", "o=140c06 h=6a4a2a s=4e321a d=34200e g=2a1a0e t=4e321a w=d8c8a0 c=80f0f0 C=40c0c0", BULGY, [(0, 0, "o"), (0, 1, "c"), (0, 2, "o"), (1, 0, "c"), (1, 1, "C"), (1, 2, "c"), (2, 1, "o")])

bow("deep_seam_bow", "o=1a1e24 h=b8f0f0 s=6ac8d0 d=3a8a98 g=8a5a30 t=b8f0f0 w=c8e8f0 b=8a5a30", HEAVY, [(3, 6, "b"), (6, 3, "b"), (4, 5, "b"), (5, 4, "b")])

bow("driftwood_bow", "o=1a1a14 h=b8b4a0 s=8a8674 d=5e5a4c g=2a4a24 t=b8b4a0 w=e0dcc8", BULGY, [(4, 4, "g"), (4, 5, "g")])

bow("shoreline_bow", "o=0e1c18 h=6ab8a0 s=3e8a74 d=2a6050 g=f0f0e8 t=6ab8a0 w=e0e8e0", HEAVY, [(1, 9, "g"), (9, 1, "g")])

bow("ambush_bow", "o=0e0e08 h=6a6450 s=4a4636 d=34302a g=2a2a20 t=4a4636 w=a89a70", HEAVY, [(2, 7, "g"), (3, 6, "g"), (7, 2, "g"), (6, 3, "g")])

bow("gorge_longbow", "o=1a0806 h=c86030 s=8a2a1a d=5a1a10 g=d8b048 t=d8b048 w=d8b048", FLAT)

bow("crowfletch_bow", "o=0e0e14 h=d8d0b8 s=a89c80 d=6a5e48 g=2a2a34 t=2a2a34 w=d8d0b8 k=2a2a34", BULGY, [(0, 9, "k"), (0, 10, "k"), (9, 0, "k"), (10, 0, "k"), (1, 12, "k")])

bow("raven_bow", "o=0e0e14 h=e0dcd0 s=b0aca0 d=7a766a g=3a3a48 t=e0dcd0 w=c8c4b8 k=3a3a48 v=c0a0ff", BULGY, [(0, 9, "k"), (0, 11, "k"), (9, 0, "k"), (11, 0, "k"), (4, 4, "v")])

bow("trick_bow", "o=2a0a0a h=f0ece0 s=c02028 d=8a1418 g=1e3e9a t=e8c058 w=d8b048", BULGY, [(1, 9, "h"), (2, 7, "h"), (7, 2, "h"), (9, 1, "h"), (12, 0, "t")])

bow("calliope_bow", "o=2a0a0a h=e8c058 s=a01c24 d=6a1018 g=e8c058 t=e8c058 w=d8b048", HEAVY, [(0, 5, "h"), (0, 6, "h"), (1, 4, "h"), (5, 0, "h"), (6, 0, "h"), (4, 1, "h"), (2, 3, "h"), (3, 2, "h")])

bow("willow_bow", "o=141a08 h=8aa048 s=5a7030 d=3a4a20 g=4a3018 t=5a7030 w=c8b090 l=6a9a3a", BULGY, [(3, 9, "l"), (4, 8, "l"), (8, 4, "l"), (9, 3, "l"), (6, 6, "l")])

bow("wisp_bow", "o=0e140e h=4a5a3a s=2e3a26 d=1e2a1a g=4a5a3a t=a0f060 w=ffffff c=e0ffd0", BULGY, [(0, 13, "c"), (13, 0, "c"), (1, 13, "o"), (13, 1, "o")])

bow("reed_bow", "o=1a1408 h=d8c060 s=a89040 d=7a6828 g=1e3e9a t=d8c060 w=c8b080 b=1e3e9a", FLAT, [(2, 9, "b"), (3, 7, "b"), (7, 3, "b"), (9, 2, "b")])

bow("horizon_bow", "o=2a1806 h=fff0a0 s=e0b848 d=a07a28 g=1e3e9a t=e0b848 w=e8c058 y=fff8d0", BULGY, [(3, 3, "y"), (2, 4, "y"), (4, 2, "y"), (2, 3, "y"), (3, 2, "y")])

bow("sinew_bow", "o=1e0808 h=d8b0a0 s=8a2a24 d=5a1818 g=e8dcc8 t=8a2a24 w=d8c8b0", HEAVY, [(1, 9, "h"), (2, 8, "h"), (8, 2, "h"), (9, 1, "h")])

bow("tendon_bow", "o=1e0808 h=c84a40 s=8a2420 d=5a1414 g=f0e0d0 t=8a2420 w=f0e0d0", HEAVY, [(2, 7, "g"), (3, 6, "g"), (6, 3, "g"), (7, 2, "g")])

bow("bamboo_bow", "o=0e1408 h=a0c860 s=6a9a3a d=4a6a24 g=8a1c24 t=6a9a3a w=d8b048", BULGY, [(1, 9, "o"), (2, 7, "o"), (7, 2, "o"), (9, 1, "o"), (4, 4, "g")])

bow("moon_gate_bow", "o=1a2420 h=c8e0d8 s=8ab0a4 d=5a8074 g=e0b848 t=e0b848 w=e0b848", dict(c=(1.6, 1.6), thick=1.3, grip=0.2), [(0, 13, "g"), (13, 0, "g")])

bow("thunderhead_bow", "o=0e1424 h=4a6080 s=2e4060 d=1e2c44 g=2e4060 t=1e2c44 w=ffffff y=ffffff", HEAVY, [(1, 13, "y"), (13, 1, "y")])

bow("bolt_of_heaven", "o=0e1424 h=ffffff s=a0d8ff d=4a8ae0 g=2a3a68 t=ffffff w=ffffff", dict(c=(3, 3), thick=1.2, grip=0.2), [(0, 12, "h"), (1, 13, "s"), (13, 1, "s"), (12, 0, "h"), (14, 2, "h")])

bow("crimson_bow", "o=1e0606 h=e8d8c8 s=8a1c24 d=5a1018 g=e8c058 t=e8c058 w=d8b048", BULGY, [(1, 9, "h"), (2, 7, "h"), (6, 1, "h"), (8, 1, "h")])

bow("bloodmoon_bow", "o=1e0606 h=c83030 s=8a1c24 d=5a1018 g=4a0c10 t=8a1c24 w=f0d8d8", HEAVY, [(3, 6, "w"), (5, 4, "w"), (7, 2, "w")])

bow("ember_bow", "o=1a0806 h=e04030 s=a02020 d=6a1414 g=e0b848 t=e0b848 w=e0b848 y=ffc060", BULGY, [(1, 9, "y"), (9, 1, "y"), (4, 4, "y")])

bow("obsidian_longbow", "o=0a0812 h=6a5090 s=3a2e58 d=241c38 g=2a2a34 t=e0b848 w=fff0a0", FLAT, [(2, 9, "t"), (9, 2, "t")])

bow("deepline_bow", "o=0e0e14 h=4a5a6a s=2e3a48 d=1e2834 g=3a4a30 t=1e2834 w=c8b090 y=fff8c0", FLAT, [(14, 13, "y"), (13, 13, "w"), (12, 13, "w"), (11, 13, "w")])

bow("beam_bow", "o=2a2010 h=fff8d0 s=f0d890 d=c8a860 g=b0d0e0 t=fff8d0 w=fff8d0 c=e0f8ff", HEAVY, [(4, 4, "c"), (3, 4, "c"), (4, 3, "c"), (5, 4, "c"), (4, 5, "c"), (3, 5, "o"), (5, 3, "o")])

bow("wingbow", "o=1a1e2a h=f0f0f8 s=c0c4d4 d=8a90a4 g=e0b848 t=f0f0f8 w=d8d8e0", HEAVY, [(0, 7, "h"), (0, 9, "h"), (0, 11, "h"), (7, 0, "h"), (9, 0, "h"), (11, 0, "h")])

bow("penumbra_bow", "o=fff0b0 h=101014 s=0a0a0e d=000000 g=0a0a0e t=0a0a0e w=fff6d0", HEAVY)

bow("dragonbone_bow", "o=2a2414 h=f4ecd0 s=d0c4a0 d=a89c78 g=3a2e20 t=e0b848 w=d8b048", HEAVY, [(1, 9, "g"), (9, 1, "g")])

bow("dragonbreath_bow", "o=1a0806 h=e0a830 s=a07a20 d=6a4a10 g=c02828 t=6a4a10 w=c86030 r=e04030", HEAVY, [(4, 4, "r"), (3, 5, "r"), (5, 3, "r")])

bow("hunters_bow", "o=1a0e06 h=d8a868 s=a87840 d=7a5428 g=4a2c14 t=d8a868 w=e8e0c8", BULGY)

bow("raven_recurve", "o=0e0e14 h=6a6e80 s=3e4254 d=2a2c3a g=1a1a22 t=8a8ea4 w=a8acc0", HEAVY, [(0, 13, "t"), (13, 0, "t"), (0, 14, "o"), (14, 0, "o")])

bow("stormstring", "o=0e1424 h=6a8ab0 s=3e5a80 d=2a3e5c g=2a3e5c t=6a8ab0 w=ffffff y=ffffff", BULGY, [(6, 8, "y"), (8, 6, "y"), (7, 7, "y")])

bow("phoenix_wing", "o=2a0a04 h=ffd060 s=e06020 d=a03810 g=4a2010 t=ffd060 w=e0a040 y=fff0a0", HEAVY, [(0, 7, "y"), (0, 9, "y"), (0, 11, "y"), (7, 0, "y"), (9, 0, "y"), (11, 0, "y"), (1, 6, "y"), (6, 1, "y")])

bow("poachers_bow", "o=14100c h=a8a090 s=7a7262 d=4e483c g=2a1a0e t=4e483c w=c8c0a8", BULGY, [(4, 4, "g"), (5, 4, "g")])

bow("thornbow", "o=1a0808 h=6a2a20 s=4a1e14 d=341410 g=2a1a10 t=4a1e14 w=d87080 r=e04060", HEAVY, [(0, 8, "r"), (1, 11, "r"), (8, 0, "r"), (11, 1, "r")])

bow("kraken_bow", "o=0e0a14 h=8a50c0 s=5a3090 d=3a2060 g=1a1424 t=5a3090 w=d8c0f0 y=f0e080", HEAVY, [(4, 4, "y"), (2, 8, "w"), (8, 2, "w")])

bow("khans_horn", "o=1a1408 h=e0c890 s=b09860 d=7a6838 g=4a3018 t=e8c058 w=f0e8d0", HEAVY, [(0, 13, "t"), (13, 0, "t"), (1, 14, "t"), (14, 1, "t")])

bow("twinstring", "o=2a1806 h=e8c058 s=c09838 d=8a6a20 g=4a3018 t=e8c058 w=c8d8e8", BULGY, [(9, 8, "w"), (8, 9, "w"), (10, 7, "w"), (7, 10, "w"), (11, 6, "w"), (6, 11, "w")])
