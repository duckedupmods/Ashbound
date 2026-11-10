"""The spears, drawn over their slot renders (see tools/weaponicons.py). Every one shares the same long diagonal shaft;
the heads, bands and hangings are each their own."""
from weaponicons import I

SHAFT = ["........owo", ".......owo", "......owo", ".....owo", "....owo", "...owo", "..owo", ".owo", "owo", "go"]


def sp(name, pal, top, marks=(), shaft=None):
    rows = [r.ljust(16, ".") for r in top.split()]
    rows += [r.ljust(16, ".") for r in (shaft or SHAFT)][len(rows) - 6:]
    rows = [list(r) for r in rows[:16]]
    for y, x, c in marks:
        rows[y][x] = c
    pal += "" if " g=" in " " + pal else " g=7a6a4a"   # the shoe on the butt
    I(name, pal, "\n".join("".join(r) for r in rows))


sp("bilge_boathook", "o=1a1208 h=a8c0bc s=6a8a86 w=5a3a1e g=b08a40", """
.............ooo
............ohso
.........o.ohoo.
........oho.so..
.........oohso..
.........oso....
""", [(9, 6, "g"), (11, 4, "g")])

sp("gibbet_hook", "o=0e0e12 h=4a4e58 s=2e323a w=3a2a1c g=8a8a90", """
..........oooo
.........ohhsso
.........ooo.oso
..............so
.........oho.os.
.........ohooo..
""", [(6, 8, "g")])

sp("stagtine_spear", "o=1a1408 h=e8e0c0 s=b8ac88 w=4a3018 g=4a6a34", """
...........o.o.h
..........ohoh.s
.........oo.ohs
.........ohoohso
..........ohsso.
.........ogsoo..
""", [(7, 7, "g"), (8, 6, "g")])

sp("gravespike", "o=1e2430 h=e0e8f0 s=a0b0c4 m=6a7a90 w=c8d0dc d=2a2e38", """
..............oh
.........ohoohs.
..........ohhso.
...........ohso.
..........oshso.
.........oho.o..
""", [(9, 6, "d"), (10, 5, "d")])

sp("beak_cane", "o=1a1208 h=f0f0f0 s=c0c4c8 c=a0e0b0 w=3a2614 g=b08a40", """
..............oh
.............ohs
..........ooohs.
.........ohccoo.
.........ochco..
..........oo....
""", [(15, 0, "g")])

sp("surgeons_probe", "o=2a3040 h=ffffff s=c8d0dc w=d8dce4 g=c0a048 c=a0f060", """
..............oh
.............hs.
............os..
...........oso..
..........gco...
.........og.....
""", [(9, 6, "g")])

sp("faceless_lance", "o=2a2e3c h=ffffff s=e0e4ec m=b0b8c8 w=1e2438 g=d0a040", """
.............ooh
...........oohhs
..........ohhsso
.........ohhssmo
.........ohsmmo.
.........goooo..
""")

sp("bonewright_pike", "o=2a2414 h=f0e4b8 s=c8b888 m=9a8a5a w=d8ccb0 g=b08a40", """
..............oh
...........o.ohs
............ohsm
...........ohsmo
.........hohsmo.
..........oso...
""", [(8, 7, "s"), (10, 5, "s"), (12, 3, "s")])

sp("kiln_pike", "o=14100e y=fff8c0 e=ffc050 r=f07018 R=b03a10 w=1e1c20", """
..............yy
............yeyy
............eeyo
...........rreo.
..........rRro..
.........oRo....
""", [(6, 8, "R")])

sp("frostbound_pike", "o=2a3e58 h=ffffff y=e0f0ff s=b0d4ec m=7ab0d8 w=3e5a78", """
.............oyh
...........oohys
..........ohyysm
.........oyhysmo
.........ohysmo.
..........yoo...
""", [(9, 6, "y"), (11, 4, "y")])

sp("wintermarch", "o=1e2a40 h=ffffff y=c0e0f8 s=8ab8e0 r=8a2020 R=5a1414 w=2e3e5a", """
.............oyh
............ohys
...........ohsso
..........rRhso.
........rRrRRo..
.......rRrRRo...
""", [(6, 6, "r"), (6, 7, "R"), (7, 5, "R"), (7, 6, "r"), (8, 4, "r")])

sp("spindle_spear", "o=1a1420 h=d8d0f0 s=a090d0 v=c080ff w=4a1a20 g=f0ece4", """
..............vh
.............vs.
............vs..
..........gggs..
..........gggo..
..........ogo...
""", [(7, 6, "w"), (7, 8, "o")])

sp("drill_lance", "o=14141a h=c8d0e0 s=8a92a8 c=d08040 w=3a2414", """
..............oh
.............ohs
............ohso
...........ohcso
...........occo.
..........oco...
""")

sp("tide_harpoon", "o=1a2a2a h=d0e0dc s=8aa8a4 m=5a7a76 w=3e4a44 c=c8f0e0", """
.............ooh
............ohhs
............osso
..........ohsso.
.........ooosc..
..........oso...
""", [(8, 5, "c"), (9, 5, "o")])

sp("pike_of_the_pass", "o=1a0e08 h=e8e0d0 s=b8ac98 r=8a2a1a R=5a1a10 w=3a2414", """
..............oh
.............ohs
...........hhhso
..........ohhso.
........rRroo...
.........Ro.....
""", [(6, 7, "R")])

sp("rookery_spear", "o=0e0e14 h=a0a8c0 s=5a6078 r=c02028 k=1a1a24 w=e0dcc8", """
..............oh
.............ohs
............ohs.
.........kkrso..
........kkkro...
.........kk.....
""", [(6, 7, "k")])

sp("nevermore", "o=0e0e14 k=1a1a24 n=2e2e3c h=e0d8ff v=b080ff w=1e1e2c", """
..........k.k.kh
.........kkkkkh.
.........nkkkhk.
........knhvkkkk
.........nvvkk..
..........nn....
""")

sp("lion_tamer_lance", "s=c8c0b0 o=2a0a0a y=fff0a0 g=f0c040 G=b08020 r=c02028 w=7a1418 h=f0ece4", """
.............ooh
.........r.r.ohs
..........yygyso
.........rgGGgyr
.........yGgGgr.
.........rgygyr.
""", [(6, 7, "h"), (8, 6, "g")])

sp("eel_spear", "o=0e1410 h=b8c8c0 s=7a8a84 m=4a5a54 w=263028 g=4a6a40", """
...........o.o.o
..........oho.ho
..........osohso
...........oohso
..........ohso..
.........ogo....
""", [(8, 6, "g")])

sp("sunspear", "o=2a1806 y=fff8c0 g=f0c040 G=b08020 b=1e3e9a B=142868 w=1e3e9a", """
..............yy
.............yg.
..........y.gG..
........yoGgGy..
.......yGbBbGo..
........yBbBGy..
""", [(6, 7, "y"), (6, 9, "G"), (9, 5, "g")])

sp("femur_spear", "o=2a2418 h=ffffff s=e0dccc m=b0a890 r=8a1c24 w=f0ece0", """
.............ooh
............ohhs
...........ohsso
..........ohssmo
..........rrsmo.
..........oro...
""", [(15, 0, "w"), (14, 0, "w")])

sp("crescent_spear", "o=1a2420 h=b8d0c8 s=7a9890 m=4a6a62 w=5a1a1a g=d8b048", """
.............ooh
............ohhs
...........ohsso
..........ohssmo
..........gsmmo.
.........ogoo...
""", [(15, 0, "s"), (14, 1, "s"), (13, 1, "o"), (15, 1, "o")])

sp("heavens_guandao", "o=1a1e20 h=c8d8d8 s=8aa8a8 m=5a7878 w=5a1414 g=d8b048 r=c02028", """
............ooo
...........ohhso
..........ohssso
.........ohssmo.
.........gsmmo..
........ogroo...
""", [(7, 7, "r"), (8, 7, "r")])

sp("lightning_rod_spear", "o=1a1408 h=ffffff b=a0e0ff g=c89848 G=8a6428 w=8a6a30", """
.............o.o
............ogGg
............ogGo
..........ogbGo.
..........obgo..
.........obo....
""", [(7, 6, "G"), (8, 7, "G")])

sp("partisan", "o=14141c h=c8ccd8 s=8a8ea4 r=a01c24 R=641018 w=2a1a14", """
..............oh
.............ohs
..........o.ohs.
..........hohso.
..........oRsoh.
.........oRro...
""")

sp("labyrinth_pike", "o=0e0e14 h=c0c4d8 s=7a7e94 g=d8b048 w=3a2414 k=1a1a24", """
..............oh
.............ohs
.........k..ohs.
..........kggso.
.........kgkko..
..........kk....
""", [(15, 0, "g")])

sp("angler_spear", "o=0e1418 h=8aa0b0 s=4a6070 y=fff8c0 w=1e2a34 k=141c22", """
.............ooy
............o..y
...........o....
..........o.....
.........oso....
..........o.....
""", [(9, 6, "k"), (9, 7, "k"), (10, 5, "k")])

sp("pale_lantern", "o=1a2430 h=e0e8f0 s=8aa0b8 c=a0f0ff w=2a3848", """
.............ooh
............ooso
...........o..o.
..........o.....
.........oso....
..........o.....
""", [(9, 8, "o"), (10, 8, "c"), (11, 8, "o"), (10, 9, "c"), (11, 9, "o"), (9, 9, "o")])

sp("halo_lance", "o=2a2a38 h=ffffff s=e0e4ec y=fff0a0 g=e0b848 w=d8dce4", """
..............oh
...........g.ohs
..........g.ohs.
.........gyyhsg.
..........ohsg..
.........ogg....
""", [(8, 6, "g"), (7, 8, "g"), (8, 8, "y")])

sp("drake_lance", "o=1a0806 h=ff8040 r=d84a24 R=8a2418 g=d8b048 w=1a1414", """
...........h..oh
..........oro.hr
...........oorR.
..........orRo..
.........gRo....
........oggo....
""")

sp("boar_spear", "o=14141c h=d0d8e0 s=8a96a8 m=5a6478 w=4a2c16 k=1e1e24", """
.............ooh
............ohhs
...........ohsso
..........ohssmo
.........kkosmo.
..........okk...
""")

sp("gilded_partisan", "o=2a1806 y=fff8c0 g=f0c040 G=b08020 b=1e2a60 w=1e2a60", """
..............oy
...........g.oyg
..........gooygo
..........oyggo.
..........gGgo..
.........ogo....
""", [(8, 6, "g"), (10, 4, "g")])

sp("wyrmtongue", "o=1a0806 r=e04a24 R=a02818 Q=6a1810 y=ffc060 w=1a1414 g=d8b048", """
..........o....o
.........oro..or
..........orooR.
...........orRo.
..........oQRo..
.........ogg....
""", [(7, 8, "Q")])

sp("heavens_lance", "o=2a2a38 h=ffffff y=fff0a0 s=e0e4ec w=e8ecf4 g=e0b848", """
.......h..h..oyh
........h.h.oyh.
.........hhhyyho
..........yyhoh.
........hhyhh.h.
.......h.gohh...
""", [(7, 7, "g")])

sp("whalers_harpoon", "o=14141c h=8a8e98 s=5a5e68 w=2a2a30 c=e0dcc0", """
..............oh
.............ohs
............ohs.
...........oo.o.
..........os....
.........oso....
""", [(9, 5, "c"), (10, 4, "c"), (11, 4, "c"), (12, 3, "c"), (11, 3, "c")])

sp("dune_pilum", "o=2a1c0a h=e0c890 s=b0905c w=8a6a3a g=d8b048", """
..............oh
.............oh.
............os..
...........os...
..........oso...
.........ogo....
""", [(10, 5, "g")])

sp("wardens_bardiche", "o=0e1420 h=c0d0e0 s=7a90a8 k=1e2a3a K=34485e w=1e2a3a", """
.............o.o
............ohoh
...........okKhs
..........okKKKo
.........okKKKo.
.........okkko..
""")

sp("tidecallers_trident", "o=1a1808 g=e0c858 G=a88a28 y=fff8c0 w=2a3a34", """
...........o.o.o
..........ogogog
..........ogGgGo
..........oGgGo.
.........ogGgo..
.........ogo....
""", [(8, 6, "g")])

sp("unison", "o=2a2410 h=ffffff s=c8d8e8 g=d8b048 G=9a7a28 w=6a4a2a", """
..............oh
............ghs.
...........gohg.
..........ghoog.
.........gGsg...
.........oGg....
""", [(7, 7, "g"), (9, 5, "g"), (10, 5, "G"), (11, 3, "g")])
