"""Shields, in vanilla shield space: the handle at the origin, the face toward +z, about 15 wide and 26 tall. kiln_bulwark stays."""
import math

from voxsword import ramp
from weaponsets import design, qb, path, P, L, disc, ring, rect, wave, Mask, flat, fire, staves, steel, honed, bone, gem, at, lit, wrap, stripes, facet_of
from weaponsets_a import BRASS, GOLD, IRON, LEATHER
from weaponsets_c import shard
from weaponsets_d import RUBY, SILVER, feathers, stroke
from weaponsets_e import CORK, HORN, IVORY, RAG

Z = 1.4   # the face plane


def grip_(k, mat="wrap", arm="dark"):
    k.box(0, -3.0, -5.0, 2.0, 6.0, 1.2, mat, tag="handle")
    for y in (-3.0, 2.0):
        k.box(0, y, -2.0, 2.0, 1.0, 6.0, arm, tag="handle_arm")


def body(k, m, face, rim=None, F=1.6, band=1.2):
    """the board and its rim"""
    k.plate(m, F, face, z=Z)
    if rim:
        k.plate(m - m.inset(band), F + 0.8, rim, z=Z)


def on(k, m, d, mat, up=1.2, glow=False):
    """a part laid on the face, up px proud of the board's plane"""
    k.plate(m, d, mat, z=Z + up, glow=glow)


def kite(w=7.4, top=12, bottom=-14, shoulder=6):
    return P((-w, top), (w, top), (w, shoulder), (0, bottom), (-w, shoulder))


def heater(w=7.6, top=12, bottom=-13):
    return P(path((-w, top), (w, top), (w, 4), qb((w, -4), (4, -10), (0, bottom), 8), qb((0, bottom), (-4, -10), (-w, -4), 8), (-w, 4)))


def rivets(k, pts, mat="edge", s=1.0, up=1.4):
    for x, y in pts:
        k.box(x, y - s / 2, Z + up, s, s, 0.6, mat)


@design("cask_lid_shield")
def cask_lid_shield(k):
    """a barrel head with a handle nailed on: oak staves, a chalked mark, the iron hoop and the bung still in it"""
    R = k.theme("cellar")
    k.mat(oak=staves(R["wood"], 2.6, 0.6), cork=flat(CORK, 0.56, 0.3), chalk=flat(ramp("#a0a090", "#c8c8b8", "#e8e8d8"), 0.5))
    m = disc(0, 0, 11.4, 24)
    body(k, m, "oak", "dark")
    on(k, disc(-3.6, 3, 1.5, 10), 1.6, "cork", 0.8)
    on(k, L([(1, -5), (5, -1)], 0.5) + L([(5, -5), (1, -1)], 0.5), 0.4, "chalk", 0.8)
    grip_(k)


@design("mothers_lid")
def mothers_lid(k):
    """the Cask Mother's great lid: a brewing vat's iron-hooped head, the tap wrenched through its middle and vinegar weeping green from every seam"""
    R = k.theme("cellar")
    k.mat(oak=staves(R["wood"], 2.0, 0.56), hoop=flat(R["dark"], 0.62), brass=flat(BRASS, 0.64), iron=flat(IRON, 0.7))
    m = disc(0, 0, 13, 28)
    body(k, m, "oak", "hoop", band=1.6)
    for x in (-8, -4, 0, 4, 8):
        on(k, L([(x + 0.8, 10), (x + 0.8, -10)], 0.5) & m.inset(1.6), 0.3, "glow", 0.8, glow=True)
    on(k, ring(0, 0, 8.4, 7.2), 1.0, "hoop", 0.9)
    on(k, disc(0, 0, 3.0, 12), 1.8, "brass", 1.0)
    k.box(0, -1.0, Z + 2.5, 2.0, 2.0, 2.6, "brass")
    k.box(0, 1.0, Z + 3.4, 1.2, 1.4, 1.2, "iron")
    k.box(0, 2.4, Z + 3.4, 5.4, 0.9, 0.9, "iron")
    grip_(k)


@design("gibbet_door")
def gibbet_door(k):
    """the door of the condemned cell, off its hinges: black planks, strap iron, a barred grate at eye level"""
    R = k.theme("gallows", base=0.5)
    k.mat(oak=staves(R["wood"], 2.4, 0.56), iron=flat(R["blade"], 0.6, bevel=0.14))
    m = P((-7.6, 13), (7.6, 13), (7.6, -13), (-7.6, -13))
    win = rect(-3.4, 4, 3.4, 9)
    body(k, m - win, "oak")
    for y in (-10, 1.6):
        on(k, rect(-7.6, y, 6, y + 1.8) + disc(6, y + 0.9, 1.4, 8), 0.5, "iron", 1.0)
        rivets(k, [(-5, y + 0.9), (-1, y + 0.9), (3, y + 0.9)], "edge", 0.8, 1.3)
    for x in (-2, 0, 2):
        k.box(x, 4, Z, 0.7, 5, 0.7, "iron")
    k.box(0, 6.2, Z, 6.8, 0.6, 0.7, "iron")
    on(k, rect(-4.4, 3, 4.4, 10) - win, 0.5, "iron", 1.0)
    grip_(k)


@design("gallows_gate")
def gallows_gate(k):
    """the gate of Gallows Hill: a gibbet's iron cage flattened into a wall, the bars curved round the shape of the last occupant, a noose knotted through the crown"""
    R = k.theme("gallows", base=0.5)
    k.mat(iron=flat(R["blade"], 0.6, bevel=0.14), rope=flat(R["acc"], 0.6), bone=bone(IVORY, 0.66), oak=staves(R["wood"], 2.4, 0.5))
    m = P(path((-8.4, 9), qb((-8.4, 14), (8.4, 14), (8.4, 9), 8), (8.4, -14), (-8.4, -14)))
    k.plate(m, 1.0, "oak", z=0.8)
    for x in (-6.4, -3.2, 0, 3.2, 6.4):
        k.plate(rect(x - 0.6, -14, x + 0.6, 13 - abs(x) * 0.4), 1.4, "iron", z=2.0)
    for y in (-11, -3, 5):
        k.plate(rect(-8.6, y, 8.6, y + 1.2), 1.8, "iron", z=2.0)
    on(k, m - m.inset(1.2), 2.2, "iron", 0.4)
    on(k, disc(0, 7, 2.6, 10), 1.8, "bone", 1.0)
    on(k, disc(-0.9, 7.4, 0.7, 6) + disc(0.9, 7.4, 0.7, 6), 0.3, "glow", 1.9, glow=True)
    on(k, ring(0, 0, 4.0, 3.0) - rect(-1, 3, 1, 5), 0.8, "rope", 1.6)
    grip_(k)


@design("shelf_fungus_shield")
def shelf_fungus_shield(k):
    """a bracket fungus the width of a tree, cut away whole: growth rings in rust and cream, a soft ruffled lip, moss where it left the bark"""
    R = k.theme("rotwood")
    rings = ramp("#4a1e08", "#6e3010", "#94461c", "#b8602a", "#d47e3e", "#ecaa6a", "#f6dcb0")

    def cap(p, n, b, key, i, j, w, h, fr):
        d = math.hypot(p[0], p[1] + 7)
        return at(rings, 0.2 + 0.7 * ((d / 3.0) % 1.0) * 0.5 + d * 0.022 + lit(key, i, j, w, h) * 0.4)

    k.mat(cap=cap, lip=flat(rings, 0.92, bevel=0.04), moss=flat(R["wrap"], 0.6))
    out = []
    for j in range(40):
        a = 2 * math.pi * j / 40
        r_ = 12.6 + 0.9 * math.sin(a * 9)
        out.append((math.cos(a) * r_, math.sin(a) * r_ * 0.96 - 0.6))
    m = Mask().poly(out)
    body(k, m, "cap", "lip", F=2.0, band=1.0)
    on(k, P((-5, -13.6), (5, -13.6), (6, -10), (2.6, -11), (0, -8.4), (-2.6, -11), (-6, -10)), 0.8, "moss", 1.2)
    grip_(k)


@design("crownbark")
def crownbark(k):
    """a whole plate of the Mossking's bark, thick as a door, an antler crown rising off its top, moss in the cracks and glowcaps coming up through them"""
    R = k.theme("rotwood")
    k.mat(bark=staves(R["wood"], 2.0, 0.6), moss=flat(R["wrap"], 0.6), bone=bone(R["blade"], 0.68))
    m = heater(8.4, 10, -14)
    body(k, m, "bark", F=2.6)
    for pts in (((-5, 8), (-3, 3), (-5, -3), (-3, -8)), ((1, 9), (3, 4), (1, -2), (3, -7)), ((5, 7), (6, 2), (5, -3))):
        on(k, L(list(pts), 1.1), 0.5, "moss", 1.2)
    for s_ in (1, -1):
        rack = stroke((s_ * 2, 9), (s_ * 9, 10), (s_ * 8, 17), 1.5) + stroke((s_ * 6, 11), (s_ * 11, 12), (s_ * 12, 15.6), 1.0) + stroke((s_ * 4, 10), (s_ * 2.6, 13), (s_ * 3.6, 16), 0.9)
        k.plate(rack, 2.0, "bone", z=Z)
    for x, y in ((-3, -1), (3, 1), (0, -8)):
        on(k, rect(x - 0.4, y, x + 0.4, y + 1.4) + rect(x - 1.2, y + 1.2, x + 1.2, y + 2), 1.0, "glow", 1.6, glow=True)
    grip_(k)


@design("coffin_lid_shield")
def coffin_lid_shield(k):
    """a coffin lid, the old six-sided kind: wide at the shoulder, an iron cross laid on it, name plate, and the scratches on the inside are not shown"""
    R = k.theme("crypt")
    k.mat(oak=staves(R["wood"], 3.0, 0.6), iron=flat(R["blade"], 0.62, bevel=0.14), plate=flat(GOLD, 0.5))
    m = P((-5, 14), (5, 14), (8, 6), (4.6, -14), (-4.6, -14), (-8, 6))
    body(k, m, "oak", "dark", band=0.8)
    on(k, rect(-0.9, -9, 0.9, 11) + rect(-4.6, 3.4, 4.6, 5.2), 0.7, "iron", 1.0)
    on(k, rect(-2.2, -6.4, 2.2, -4.2), 0.3, "plate", 1.3)
    rivets(k, [(-3.8, 12), (3.8, 12), (-3.6, -12), (3.6, -12)], "edge", 0.9)
    grip_(k)


@design("abbots_reliquary")
def abbots_reliquary(k):
    """the Pale Abbot's: a gilded lancet arch with a crystal door, a saint's finger bone lit by one candle inside, pearls and wax down the frame"""
    R = k.theme("crypt", base=0.56)
    k.mat(gold=flat(GOLD, 0.64, bevel=0.14), glass=flat(ramp("#2a2418", "#3a3020", "#4a3e2a"), 0.5, bevel=0.1), wax=flat(R["acc"], 0.72, bevel=0.1), bone=flat(IVORY, 0.8))
    m = P(path((-8, -14), (8, -14), (8, 2), qb((8, 9), (3, 12), (0, 16), 8), qb((0, 16), (-3, 12), (-8, 9), 8), (-8, 2)))
    body(k, m, "gold")
    win = P(path((-5, -11), (5, -11), (5, 2), qb((5, 7), (2, 9), (0, 12), 6), qb((0, 12), (-2, 9), (-5, 7), 6), (-5, 2)))
    on(k, win, 0.3, "glass", 0.9)
    on(k, m - win, 2.2, "gold", 0.6)
    on(k, rect(-0.7, -9, 0.7, 0) + disc(0, 0, 1.0, 8), 0.4, "bone", 1.2)
    on(k, P(path(qb((3, -5), (1.8, -3), (3, -0.4), 5), qb((3, -0.4), (4.2, -3), (3, -5), 5))), 0.3, "glow", 1.3, glow=True)
    on(k, rect(2.4, -9, 3.6, -5), 0.4, "wax", 1.2)
    on(k, L([(0, -11), (0, 12)], 0.4) + L([(-5, 1.4), (5, 1.4)], 0.4), 0.4, "gold", 1.4)
    on(k, P((-8.4, 1), (-6, 1), (-6.4, -7), (-7.6, -4)), 0.6, "wax", 1.8)
    grip_(k)


@design("quarantine_door")
def quarantine_door(k):
    """a door from the Ward with a red cross daubed on it and boards nailed across; somebody is still knocking"""
    R = k.theme("plague")
    k.mat(oak=staves(ramp("#4a4238", "#625a4c", "#7c7260", "#968c78", "#b0a68e"), 2.6, 0.6), red=flat(ramp("#3a0806", "#5a100a", "#7e1a10", "#a02618"), 0.6, 0.2), board=staves(ramp("#2a1c10", "#3e2a18", "#543a22"), 12, 0.6), nail=flat(IRON, 0.7), iron=flat(R["dark"], 0.6))
    m = rect(-7.6, -13, 7.6, 13)
    body(k, m, "oak")
    on(k, rect(-1.6, -9, 1.6, 9) + rect(-6, -1.6, 6, 1.6), 0.2, "red", 0.82)
    for (a, b) in (((-8, -7), (8, -4)), ((-8, 8), (8, 4))):
        on(k, L([a, b], 2.2), 0.7, "board", 1.1)
        k.box(a[0] + 2, a[1] + (b[1] - a[1]) / 8 - 0.5, Z + 1.5, 0.9, 0.9, 0.4, "nail")
        k.box(b[0] - 2, b[1] - (b[1] - a[1]) / 8 - 0.5, Z + 1.5, 0.9, 0.9, 0.4, "nail")
    grip_(k)


@design("surgeons_tray")
def surgeons_tray(k):
    """a great kidney-shaped steel tray with a rolled lip, and strapped across it the tools: saw, tongs, a lancet, a little green bottle"""
    R = k.theme("plague", base=0.6)
    k.mat(tray=flat(R["blade"], 0.6, bevel=0.1), lip=flat(R["blade"], 0.84, bevel=0.06), brass=flat(R["dark"], 0.6), strap=flat(LEATHER, 0.7, bevel=0.1), tool=flat(R["blade"], 0.92, bevel=0.02))
    m = P(path(qb((-3, 13), (-11, 11), (-9, 0), 8), qb((-9, 0), (-11, -11), (-3, -13), 8), qb((-3, -13), (9, -14), (10, -7), 6), qb((10, -7), (5, -5), (4, 0), 5), qb((4, 0), (5, 5), (10, 7), 5), qb((10, 7), (9, 14), (-3, 13), 6)))
    body(k, m, "tray", "lip", band=1.0)
    on(k, L([(-6, -9), (-6, 9)], 1.2) + P((-5.4, -9), (-3.4, -9), (-5.4, 7)), 0.4, "tool", 1.0)
    on(k, L([(-1, -9), (-1, 9)], 0.6), 0.4, "tool", 1.0)
    on(k, ring(-1, 10.0, 1.2, 0.5), 0.4, "tool", 1.0)
    on(k, L([(1.6, -9), (1.8, 2)], 0.7) + L([(3.4, -9), (2.4, 2)], 0.7), 0.4, "brass", 1.0)
    on(k, rect(4.6, 4, 7.0, 9), 1.6, "glow", 1.6, glow=True)
    on(k, rect(5.2, 9, 6.4, 10.4), 1.0, "strap", 1.6)
    on(k, rect(-9, -3, 8, -1.6), 0.5, "strap", 1.4)
    grip_(k)


@design("mirror_of_no_face")
def mirror_of_no_face(k):
    """an old silver mirror, its gold frame cut with eyes all shut: look in it and there is the room, the torchlight, everything but you"""
    R = k.theme("temple", base=0.72)

    def glass(p, n, b, key, i, j, w, h, fr):
        return at(ramp("#6a7a88", "#8ea0ae", "#b4c6d2", "#dceaf2", "#ffffff"), 0.34 + 0.28 * math.sin((p[0] + p[1]) * 0.3) + lit(key, i, j, w, h) * 0.3 + (0.3 if -3 < p[0] - p[1] * 0.6 < -1 else 0))

    k.mat(glass=glass, gold=flat(R["acc"], 0.62, bevel=0.14))
    m = disc(0, 0, 12, 28)
    body(k, m, "glass", "gold", F=1.4, band=1.8)
    for j in range(8):
        a = j * math.pi / 4
        x, y = math.cos(a) * 11, math.sin(a) * 11
        on(k, disc(x, y, 1.1, 8), 0.5, "gold", 1.6)
    grip_(k)


@design("thousand_face_aegis")
def thousand_face_aegis(k):
    """a kite of white stone paved with small blank faces, rank on rank, the eyes of the central one open and burning blue"""
    R = k.theme("temple", base=0.72)
    k.mat(stone=flat(R["blade"], 0.5, bevel=0.1), face=flat(R["blade"], 0.86, bevel=0.06), gold=flat(R["acc"], 0.64))
    m = kite(8, 13, -15, 5)
    body(k, m, "stone", "gold", band=1.0)
    for r_, y in enumerate((9.4, 5.6, 1.8, -2, -5.8, -9.6)):
        hw = 6.4 - max(0, r_ - 2) * 1.5
        n = max(1, int(hw * 2 / 2.8))
        for j in range(n):
            x = (j - (n - 1) / 2) * 2.8
            on(k, P((x - 1.1, y + 1.6), (x + 1.1, y + 1.6), (x + 0.8, y - 0.8), (x, y - 1.6), (x - 0.8, y - 0.8)), 0.5, "face", 1.0)
            on(k, rect(x - 0.7, y + 0.3, x - 0.2, y + 0.6) + rect(x + 0.2, y + 0.3, x + 0.7, y + 0.6), 0.1, "dark", 1.3)
    on(k, rect(-1.4, 2.0, -0.4, 2.8) + rect(0.4, 2.0, 1.4, 2.8), 0.2, "glow", 1.4, glow=True)
    grip_(k)


@design("ribcage_shield")
def ribcage_shield(k):
    """a ribcage laid open and wired flat, gaps you could put a blade through and a soul lamp hung where the heart was"""
    R = k.theme("ossuary", base=0.5)
    k.mat(bone=bone(R["acc"], 0.68), edgeb=flat(R["acc"], 0.86, bevel=0.06), brass=flat(R["dark"], 0.62), hot=fire(R["glow"], 0.3, 0.7))
    k.plate(rect(-1.8, -13, 1.8, 13), 2.2, "bone", z=Z)
    for j in range(6):
        y = 11 - j * 4
        w = 8.6 - abs(j - 2) * 0.7
        for s_ in (1, -1):
            k.plate(stroke((s_ * 1.4, y), (s_ * (w + 1), y + 0.6), (s_ * w, y - 3.2), 1.4), 1.6, "edgeb", z=Z)
    k.plate(rect(-6.6, -3, -5.6, 3) + rect(5.6, -3, 6.6, 3), 1.0, "brass", z=Z)
    on(k, disc(0, 0, 2.6, 10), 2.0, "hot", 1.0, glow=True)
    on(k, ring(0, 0, 3.2, 2.4), 2.4, "brass", 0.8)
    grip_(k)


@design("boilerplate")
def boilerplate(k):
    """the front of an engine's boiler: rivets by the hundred, a pressure gauge on the wrong side of safe, a spigot hissing soul fire"""
    R = k.theme("ossuary", base=0.5)
    k.mat(iron=flat(R["blade"], 0.5, bevel=0.14), brass=flat(R["dark"], 0.64), gauge=flat(ramp("#c8c0a8", "#e8e0c8", "#fff8e8"), 0.7), red=flat(RUBY, 0.56))
    m = P(path(qb((-8, 13), (0, 15), (8, 13), 6), (8, -13), qb((8, -13), (0, -15), (-8, -13), 6)))
    body(k, m, "iron", "brass", band=0.8, F=2.2)
    pts = [(x, y) for y in (10.6, -10.8) for x in (-5.4, -2.7, 0, 2.7, 5.4)] + [(x, y) for x in (-6.4, 6.4) for y in (6, 2, -2, -6)]
    rivets(k, pts, "brass", 0.8, 1.6)
    on(k, ring(0, 3, 4.2, 3.4), 0.8, "brass", 1.2)
    on(k, disc(0, 3, 3.4, 14), 0.3, "gauge", 1.3)
    on(k, L([(0, 3), (2.6, 0.8)], 0.5), 0.2, "red", 1.5)
    for a in range(0, 200, 40):
        r = math.radians(a - 10)
        on(k, L([(math.cos(r) * 2.6, 3 + math.sin(r) * 2.6), (math.cos(r) * 3.2, 3 + math.sin(r) * 3.2)], 0.4), 0.1, "dark", 1.4)
    on(k, rect(-3, -8, 3, -3.6), 0.5, "glow", 1.2, glow=True)
    for x in (-1.6, 0, 1.6):
        on(k, rect(x - 0.3, -8, x + 0.3, -3.6), 0.5, "brass", 1.4)
    grip_(k)


@design("furnace_door")
def furnace_door(k):
    """the Foundry's firebox door, cast iron, swung off its pins: an arched grille of bars and behind them the fire, still going"""
    R = k.theme("foundry", base=0.46)
    k.mat(iron=flat(ramp("#14120f", "#221f1b", "#332f2a", "#46403a", "#5e564e", "#7a7065"), 0.62, bevel=0.14))
    m = P(path((-8.4, -13), (8.4, -13), (8.4, 4), qb((8.4, 12), (0, 15), (-8.4, 12), 8), (-8.4, 4)))
    win = P(path((-5.6, -6), (5.6, -6), (5.6, 4), qb((5.6, 9), (0, 11), (-5.6, 9), 6), (-5.6, 4)))
    body(k, m - win, "iron", F=2.4)
    k.plate(win, 0.8, "glow", glow=True, z=Z)
    for x in (-3.8, -1.3, 1.3, 3.8):
        k.plate(rect(x - 0.5, -6, x + 0.5, 10.4 - abs(x) * 0.6), 2.2, "iron", z=Z)
    on(k, rect(-8.6, -11, 8.6, -8.6), 0.6, "iron", 1.3)
    k.box(9.2, -2, Z, 1.2, 4, 1.8, "iron")
    k.box(-9.4, -10, Z, 1.8, 2.2, 2.2, "iron")
    k.box(-9.4, 6, Z, 1.8, 2.2, 2.2, "iron")
    rivets(k, [(-6, -10), (-2, -10), (2, -10), (6, -10)], "edge", 0.9, 1.6)
    grip_(k)


@design("glacier_tower")
def glacier_tower(k):
    """a wall of the old ice cut with a saw: jagged at the top where it broke, an iron frame freezing into it, cold light down inside"""
    R = k.theme("frost", base=0.54)
    k.mat(ice=flat(R["glow"], 0.62, bevel=0.14), white=flat(R["glow"], 0.92, bevel=0.04), iron=flat(R["dark"], 0.6, bevel=0.14))
    m = P((-8, -14), (8, -14), (8, 9), (6, 15), (4, 11), (1.6, 16.6), (-1, 11.4), (-4, 14.6), (-6, 10), (-8, 12))
    body(k, m, "ice", F=2.4)
    for pts in (((-6, 8), (-1, 0), (-4, -7)), ((5, 7), (1, -2), (5, -9)), ((-1, 0), (1, -2))):
        on(k, L(list(pts), 0.6), 0.2, "white", 1.3)
    on(k, rect(-8.4, -14.4, 8.4, -11.6) + rect(-8.6, -14, -7, 6) + rect(7, -14, 8.6, 6), 1.6, "iron", 1.0)
    grip_(k)


@design("winter_standard")
def winter_standard(k):
    """the Marshal's banner frozen into a shield: red swallowtail cloth gone hard as plate, a silver crystal big on it, an iron crossbar and a fringe of icicles"""
    R = k.theme("frost", base=0.54)
    k.mat(red=flat(R["acc"], 0.6, bevel=0.1), silver=flat(R["blade"], 0.72, bevel=0.1), white=flat(R["glow"], 0.92, bevel=0.04), ice=flat(R["glow"], 0.7, bevel=0.14))
    m = P((-8.4, 13), (8.4, 13), (8.4, -14), (3.6, -8.4), (0, -13), (-3.6, -8.4), (-8.4, -14))
    body(k, m, "red", F=1.4)
    k.plate(rect(-10.4, 12.4, 10.4, 14.4), 2.0, "silver", z=Z)
    for s_ in (1, -1):
        k.plate(disc(s_ * 10.8, 13.4, 1.4, 8), 2.2, "silver", z=Z)
    for a in (0, 60, 120):
        r = math.radians(a)
        c, s_ = math.cos(r), math.sin(r)
        on(k, L([(-c * 6.2, 1 - s_ * 6.2), (c * 6.2, 1 + s_ * 6.2)], 1.0), 0.5, "white", 0.9)
        for f in (0.62, -0.62):
            bx, by = c * 6.2 * f, 1 + s_ * 6.2 * f
            on(k, L([(bx - s_ * 1.8 + c * f, by + c * 1.8 + s_ * f), (bx, by), (bx + s_ * 1.8 + c * f, by - c * 1.8 + s_ * f)], 0.6), 0.5, "white", 0.9)
    on(k, rect(-8.4, 9.4, 8.4, 10.2) + rect(-8.4, -9.6, -7.2, 9.4) + rect(7.2, -9.6, 8.4, 9.4), 0.4, "silver", 0.9)
    for x, ln in ((-7, 4), (-3, 2.6), (3.6, 3.6), (7, 2.8)):
        k.plate(P((x - 0.7, -10.0), (x + 0.7, -10.0), (x, -10 - ln)), 1.0, "ice", z=Z)
    grip_(k)


@design("tome_shield")
def tome_shield(k):
    """the heaviest law the Archive holds, shut and clasped, corners shod in brass, a square of silk over the title that you are told not to lift"""
    R = k.theme("silk", base=0.5)
    cover = ramp("#1a0408", "#2e0a10", "#4a1018", "#661a22", "#842a30")
    k.mat(cover=flat(cover, 0.56, bevel=0.1), brass=flat(BRASS, 0.66), page=stripes(ramp("#a89e84", "#c4bba0", "#dad2b8"), ramp("#7a7058", "#948a70", "#ada388"), 0.5, 0.0, 0.5), silk=flat(R["acc"], 0.9, bevel=0.04))
    m = rect(-8, -13, 8, 13)
    body(k, m, "cover", F=1.2)
    k.box(0.4, -12.6, Z - 1.4, 15.4, 25, 2.0, "page")
    k.plate(rect(-8.4, -13, -6.4, 13), 3.4, "cover", z=Z - 0.8)
    for x in (-7, 7):
        for y in (-11, 11):
            s_ = 1 if x > 0 else -1
            t_ = 1 if y > 0 else -1
            on(k, P((x + s_ * 1.4, y + t_ * 2.4), (x - s_ * 2, y + t_ * 2.4), (x + s_ * 1.4, y - t_ * 1)), 0.6, "brass", 0.8)
    on(k, rect(-3.6, -1, 3.6, 7), 0.4, "silk", 0.8)
    on(k, ring(0, 3, 2.6, 2.0) + rect(-0.3, 0, 0.3, 6), 0.1, "glow", 1.0, glow=True)
    on(k, rect(5.6, -3, 10, -1), 1.0, "brass", 0.8)
    grip_(k)


@design("cocoon_aegis")
def cocoon_aegis(k):
    """a cocoon spun tight as felt, thread by thread, a shape folded up inside with its light still on, a few strands of silk blowing off"""
    R = k.theme("silk", base=0.5)
    silk = ramp("#8a8478", "#a8a294", "#c4bfb2", "#dcd8cc", "#eeebe2", "#fbfaf6")

    def spun(p, n, b, key, i, j, w, h, fr):
        return at(silk, 0.56 + lit(key, i, j, w, h) + 0.2 * math.sin(p[1] * 2.4 + p[0] * 0.8 + 0.8 * math.sin(p[0] * 0.5)))

    k.mat(spun=spun, thread=flat(silk, 0.9, bevel=0))
    m = wave(lambda t: 0.0, lambda t: 9.4 * math.sin((t * 0.92 + 0.04) * math.pi) ** 0.7, 14, -15, 28)
    body(k, m, "spun", F=3.0)
    on(k, wave(lambda t: 0, lambda t: 3.4 * math.sin((t * 0.92 + 0.04) * math.pi) ** 0.6, 9, -9, 20), 0.3, "glow", 0.0 + 1.5, glow=True)
    for a, c, b in (((8, 4), (13, 3), (12, -6)), ((-8, -3), (-13, -5), (-11, -12))):
        k.plate(stroke(a, c, b, 0.4), 0.4, "thread", z=Z)
    grip_(k)


@design("minecart_shield")
def minecart_shield(k):
    """the end plate of a mine cart with one wheel still on: riveted iron, a tally chalked on it and teal ore in the dents"""
    R = k.theme("weeping_mine", base=0.5)
    k.mat(iron=flat(R["blade"], 0.5, bevel=0.14), copper=flat(R["acc"], 0.6), wheel=flat(IRON, 0.66, bevel=0.14), chalk=flat(ramp("#a0a090", "#c8c8b8", "#e8e8d8"), 0.5))
    m = P((-9.4, 11), (9.4, 11), (7.6, -9), (-7.6, -9))
    body(k, m, "iron", "copper", band=1.0, F=2.0)
    rivets(k, [(-7, 9), (-3.5, 9), (0, 9), (3.5, 9), (7, 9), (-5.8, -7), (5.8, -7), (0, -7)], "edge", 0.9, 1.5)
    for x in (-3, -1.6, -0.2, 1.2):
        on(k, rect(x, 1, x + 0.4, 5.4), 0.2, "chalk", 1.2)
    on(k, L([(-3.6, 1.4), (2.0, 4.6)], 0.4), 0.2, "chalk", 1.3)
    for s_ in (1, -1):
        k.plate(disc(s_ * 5.6, -11, 3.2, 14) - disc(s_ * 5.6, -11, 1.8, 10), 1.6, "wheel", z=Z)
        k.plate(disc(s_ * 5.6, -11, 1.0, 8), 2.0, "wheel", z=Z)
    on(k, shard(4, -2, 4, -20, 1.8) + shard(-5, 0, 3, 30, 1.4), 1.0, "glow", 1.1, glow=True)
    grip_(k)


@design("bedrock_aegis")
def bedrock_aegis(k):
    """a piece of the world's floor: rock too dark to shade, its underside broken, one crystal vein as thick as a thumb burning across it"""
    R = k.theme("weeping_mine", base=0.5)
    rock = ramp("#08080a", "#101014", "#18181e", "#22222a", "#303038", "#444450")
    k.mat(rock=flat(rock, 0.56, 0.3, bevel=0.2), crystal=flat(R["glow"], 0.72, bevel=0.14))
    m = P((-9, 12), (-2, 14), (6, 13), (10, 7), (9, -3), (10, -8), (5, -14), (-1, -12), (-5, -15), (-9, -9), (-10, 2))
    body(k, m, "rock", F=3.4)
    for pts in (((-8, 8), (-2, 6), (0, 0), (5, -2), (9, -7)), ((0, 0), (-3, -6), (-5, -13))):
        on(k, L(list(pts), 1.3), 0.4, "glow", 1.6, glow=True)
    on(k, shard(0, 0, 8.6, -30, 3.2) + shard(-1, 1, 6.4, 34, 2.4), 2.0, "crystal", 1.8)
    grip_(k)


@design("bell_shield")
def bell_shield(k):
    """a chapel bell cut down the middle and beaten flat: you can still read the founder's band and when it's struck the whole arm rings"""
    R = k.theme("tide_chapel", base=0.5)
    bronze = ramp("#1a1c10", "#2c3018", "#44482a", "#5e6438", "#7c8448", "#a0a860", "#c8c884")
    k.mat(bell=flat(bronze, 0.56, bevel=0.1), band=flat(bronze, 0.82), pearl=flat(R["glow"], 0.86), crust=flat(R["acc"], 0.72))
    m = P(path((-3.6, 12), qb((0, 14), (0, 14), (3.6, 12), 2), qb((6, 9), (6, 0), (10.6, -11), 8), (10.6, -11), (11, -14), (-11, -14), (-10.6, -11), qb((-6, 0), (-6, 9), (-3.6, 12), 8)))
    body(k, m, "bell", F=2.2)
    on(k, rect(-7, 3.4, 7, 4.8) + rect(-10, -10.4, 10, -9), 0.5, "band", 1.1)
    k.plate(ring(0, 13.6, 2.0, 1.0), 1.4, "bell", z=Z)
    on(k, disc(0, -4, 2.0, 10), 1.2, "pearl", 1.3)
    on(k, disc(-5, -7, 1.0, 8) + disc(6.4, -6, 0.8, 8), 0.8, "crust", 1.1)
    grip_(k)


@design("bellwall")
def bellwall(k):
    """five drowned bells bolted to one bronze plate, each with its own note: raise it and the Chapel's tide comes in behind you"""
    R = k.theme("tide_chapel", base=0.5)
    bronze = ramp("#1a1c10", "#2c3018", "#44482a", "#5e6438", "#7c8448", "#a0a860", "#c8c884")
    k.mat(plate=flat(R["blade"], 0.4, bevel=0.12), bell=flat(bronze, 0.62, bevel=0.14), rim=flat(bronze, 0.84), pearl=fire(R["glow"], 0.5, 0.5), kelp=flat(R["wrap"], 0.56))
    m = P((-9, 13), (9, 13), (9, -6), (0, -15), (-9, -6))
    body(k, m, "plate", "bell", band=1.0)
    for x, y, s_ in ((-4.4, 6, 1.0), (4.4, 6, 1.0), (0, 4.6, 1.2), (-3.0, -3.4, 0.86), (3.0, -3.4, 0.86)):
        b = P(path((x - 1.1 * s_, y + 4 * s_), (x + 1.1 * s_, y + 4 * s_), qb((x + 2.4 * s_, y + 2), (x + 2.4 * s_, y - 1), (x + 3.6 * s_, y - 2.6 * s_), 4), (x - 3.6 * s_, y - 2.6 * s_), qb((x - 2.4 * s_, y - 1), (x - 2.4 * s_, y + 2), (x - 1.1 * s_, y + 4 * s_), 4)))
        on(k, b, 1.6, "bell", 1.2)
        on(k, rect(x - 3.2 * s_, y - 2.4 * s_, x + 3.2 * s_, y - 1.8 * s_), 0.5, "rim", 1.9)
        on(k, disc(x, y - 3.2 * s_, 0.7, 6), 0.8, "pearl", 1.6, glow=True)
    on(k, wave(lambda t: 8 + math.sin(t * 7), lambda t: 0.6, 13, -2, 12), 0.5, "kelp", 1.4)
    grip_(k)


@design("toll_gate_shield")
def toll_gate_shield(k):
    """a section of the gate at the head of the pass: spiked rough logs, a coin slot cut in the crossbar and a tin sign saying what you owe"""
    R = k.theme("brigands_gorge", base=0.5)
    k.mat(logw=staves(R["wood"], 3.0, 0.6), red=flat(R["wrap"], 0.6), iron=flat(IRON, 0.66), coin=flat(GOLD, 0.7), tin=flat(ramp("#6a6a70", "#8e8e96", "#b4b4bc"), 0.6))
    m = Mask()
    for x in (-7.5, -4.5, -1.5, 1.5, 4.5, 7.5):
        m = m + P((x - 1.5, -13), (x + 1.5, -13), (x + 1.5, 10), (x, 13.6 + (x % 3)), (x - 1.5, 10))
    body(k, m, "logw", F=2.2)
    on(k, rect(-9.4, 2, 9.4, 5.6) + rect(-9.4, -9, 9.4, -6.4), 0.8, "red", 1.1)
    on(k, rect(-3, 3.4, 3, 4.2), 0.2, "dark", 1.5)
    on(k, disc(0, -2, 1.5, 10), 0.4, "coin", 1.3)
    rivets(k, [(-7.5, 3.8), (7.5, 3.8), (-4.5, -7.8), (4.5, -7.8)], "iron", 0.9, 1.5)
    grip_(k)


@design("kingshield")
def kingshield(k):
    """Red Jack's arms, stolen from four other kings: quartered and painted over, a crown on top, a sabre and a noose crossed behind"""
    R = k.theme("brigands_gorge", base=0.5)
    k.mat(red=flat(R["wrap"], 0.6, bevel=0.1), black=flat(IRON, 0.5, bevel=0.1), gold=flat(GOLD, 0.66, bevel=0.14), gem=gem(RUBY), blade2=flat(SILVER, 0.7))
    m = heater(8.0, 11, -14)
    k.plate(L([(-12, -12), (11, 15)], 1.1), 0.8, "blade2", z=0.6)
    k.plate(L([(12, -12), (-11, 15)], 1.1), 0.8, "blade2", z=0.6)
    body(k, m & rect(-9, -2, 0, 12) + (m & rect(0, -15, 9, -2)), "red", F=1.6)
    body(k, m & rect(0, -2, 9, 12) + (m & rect(-9, -15, 0, -2)), "black", F=1.6)
    on(k, m - m.inset(1.0), 2.2, "gold", 0.4)
    on(k, rect(-0.6, -14, 0.6, 11) + rect(-8, -2.6, 8, -1.4), 0.4, "gold", 0.9)
    k.plate(P((-6, 10.6), (6, 10.6), (7, 16), (3.4, 12.6), (0, 17), (-3.4, 12.6), (-7, 16)), 2.2, "gold", z=Z)
    on(k, disc(0, -2, 1.6, 10), 0.6, "gem", 1.1)
    grip_(k)


@design("rook_kite_shield")
def rook_kite_shield(k):
    """a black kite shingled in pinions from the point up, each feather tipped pale, one white feather where the heart would be"""
    R = k.theme("rookery", base=0.46, edge=0.7)
    k.mat(board=flat(R["dark"], 0.5), f1=flat(R["blade"], 0.42, bevel=0.14), f2=flat(R["blade"], 0.56, bevel=0.14), white=flat(R["acc"], 0.86, bevel=0.06), iron=flat(R["acc"], 0.5))
    m = kite(8, 13, -15, 5)
    body(k, m, "board", "iron", band=0.8)
    for r_, y in enumerate((11, 7.4, 3.8, 0.2, -3.4, -7, -10.6)):
        hw = 7 - max(0, r_ - 2) * 1.3
        n = max(1, int(hw * 2 / 2.6))
        for j in range(n):
            x = (j - (n - 1) / 2) * 2.6 + (r_ % 2) * 0.4
            pl = P((x - 1.3, y + 2), (x + 1.3, y + 2), (x + 1.3, y - 1.4), (x, y - 3.6), (x - 1.3, y - 1.4)) & m.inset(0.8)
            on(k, pl, 0.4, "f2" if (j + r_) % 2 else "f1", 1.0 + (6 - r_) * 0.06)
    on(k, P((-1.2, 3), (1.2, 3), (1.2, 0), (0, -2.8), (-1.2, 0)), 0.3, "white", 1.6)
    grip_(k)


@design("black_wing_aegis")
def black_wing_aegis(k):
    """two great wings folded forward until the tips cross, a pale rook's eye open in the gap between them"""
    R = k.theme("rookery", base=0.46)
    k.mat(f1=flat(R["blade"], 0.4, bevel=0.14), f2=flat(R["blade"], 0.54, bevel=0.14), bone=bone(R["acc"], 0.7), eye=fire(R["glow"], 0.4, 0.6))
    k.plate(heater(6, 11, -12), 1.2, "f1", z=0.8)
    for s_ in (1, -1):
        k.plate(stroke((s_ * 9, 12), (s_ * 14, 2), (-s_ * 2, -16), 1.8, 12), 2.2, "bone", z=Z)
        for j in range(7):
            t = j / 7
            ax = s_ * (9 + 3.6 * math.sin(t * 2.2)) * (1 - t ** 3)
            ay = 12 - t * 26
            k.plate(P((ax, ay), (ax - s_ * 2, ay + 2), (ax - s_ * (11 - j * 0.8), ay + 3.6 - j * 0.3), (ax - s_ * 9, ay + 0.2)), 0.7, "f2" if j % 2 else "f1", z=Z + 0.5 + j * 0.05)
    on(k, disc(0, 8.8, 2.2, 10), 0.6, "bone", 1.4)
    on(k, disc(0, 8.8, 1.2, 8), 0.6, "eye", 1.6, glow=True)
    grip_(k)


@design("target_shield")
def target_shield(k):
    """the thrower's target: red and white rings, a lot of old holes, and three knives still in it"""
    k.theme("hollow_circus", base=0.6)
    red = ramp("#2a0408", "#4e0810", "#7a1018", "#a81c20", "#d0302a", "#ee5a44")
    cream = ramp("#6a5a44", "#8e7c60", "#b4a282", "#d6c8a8", "#efe4c8", "#fff8e8")

    def rings(p, n, b, key, i, j, w, h, fr):
        d = math.hypot(p[0], p[1])
        return at(red if int(d / 2.4) % 2 else cream, 0.62 + lit(key, i, j, w, h) * 0.4)

    k.mat(rings=rings, gold=flat(GOLD, 0.64, bevel=0.12), knife=flat(SILVER, 0.7), hilt=flat(red, 0.6))
    body(k, disc(0, 0, 12, 26), "rings", "gold", band=0.9)
    for a, b in (((3, 4), (7, 11)), ((-5, -2), (-12, 1)), ((1, -6), (4, -13))):
        k.seg(a, b, 0.6, 0.6, "knife", z=Z + 3)
        dx, dy = (b[0] - a[0]), (b[1] - a[1])
        k.box(a[0], a[1], Z + 2.0, 0.7, 0.7, 2.4, "knife")
        k.seg((b[0], b[1]), (b[0] + dx * 0.35, b[1] + dy * 0.35), 1.2, 1.2, "hilt", z=Z + 3)
    grip_(k)


@design("grand_ring")
def grand_ring(k):
    """the centre ring, whole: a hoop of fire round a red curtain, gold stars, and the Ringmaster's top hat where the crest would go"""
    R = k.theme("hollow_circus", base=0.6)
    red = ramp("#2a0408", "#4e0810", "#7a1018", "#a81c20", "#d0302a", "#ee5a44")

    def curtain(p, n, b, key, i, j, w, h, fr):
        return at(red, 0.5 + lit(key, i, j, w, h) + 0.2 * math.sin(p[0] * 2.2))

    k.mat(curtain=curtain, gold=flat(GOLD, 0.64, bevel=0.14), flame=fire(ramp("#a02206", "#e04a0a", "#ff8a1c", "#ffc84a", "#fff0b0"), 0.1, 0.9), hat=flat(ramp("#08060c", "#121016", "#1c1822", "#2a2432", "#3e3648"), 0.56, bevel=0.14))
    m = disc(0, 0, 11, 26)
    body(k, m, "curtain", "gold", band=1.2)
    for j in range(16):
        a = 2 * math.pi * j / 16
        t_ = (-math.sin(a), math.cos(a))
        o = (math.cos(a) * 10.4, math.sin(a) * 10.4)
        ln = 15 if j % 2 else 13.4
        k.plate(P((o[0] + t_[0] * 2, o[1] + t_[1] * 2), (math.cos(a) * ln - 0.6, math.sin(a) * ln + 1.4), (o[0] - t_[0] * 2, o[1] - t_[1] * 2)), 1.4, "flame", z=Z, glow=True)
    on(k, rect(-3.4, -2, 3.4, 3.6) + rect(-5.6, -3, 5.6, -1.8), 0.8, "hat", 1.0)
    on(k, rect(-3.4, -1.6, 3.4, -0.4), 0.8, "curtain", 1.2)
    for x, y in ((-6, 5), (6, 5), (0, 7), (-4, -7), (4, -7)):
        star = P(*[(x + math.cos(a * math.pi / 5 + math.pi / 2) * (1.2 if a % 2 == 0 else 0.5), y + math.sin(a * math.pi / 5 + math.pi / 2) * (1.2 if a % 2 == 0 else 0.5)) for a in range(10)])
        on(k, star, 0.3, "gold", 0.9)
    grip_(k)


@design("coracle_shield")
def coracle_shield(k):
    """a marsh coracle, hide stretched over a basket, patched and smelling of it: a bone paddle bound across the back and reeds trailing"""
    R = k.theme("mirefen_coven", base=0.5)
    wick = ramp("#3a3414", "#5a5220", "#7c7230", "#a09844", "#c4bc60")

    def weave(p, n, b, key, i, j, w, h, fr):
        return at(wick, 0.5 + lit(key, i, j, w, h) + (0.2 if (int((p[0] + 20) / 1.5) + int((p[1] + 20) / 1.5)) % 2 else -0.14))

    k.mat(weave=weave, hide=flat(ramp("#2c2214", "#44341e", "#5e4a2c", "#78603c"), 0.56, 0.3, bevel=0.1), bone=bone(R["acc"], 0.7), reed=flat(wick, 0.7))
    m = disc(0, 0, 12, 24)
    body(k, m, "weave", "hide", band=1.4, F=2.0)
    on(k, P((-4, 7), (3, 8), (5, 2), (0, 0), (-5, 2)), 0.4, "hide", 1.1)
    for x, y in ((-3, 7.4), (2.4, 7.8), (4.4, 2), (-4.4, 2.2)):
        on(k, disc(x, y, 0.4, 5), 0.3, "bone", 1.4)
    on(k, L([(-11, -9), (11, 9)], 1.2), 0.6, "bone", 1.5)
    k.plate(wave(lambda t: 12.4 + 1.1 * math.sin(t * 7), lambda t: 0.5, 2, -11, 10), 0.4, "reed", z=Z)
    grip_(k)


@design("cauldron_lid")
def cauldron_lid(k):
    """the coven's own lid, hexed shut: black iron, a ring of green sigils, a skull for its knob and the steam coming out of it uncomfortably shaped"""
    R = k.theme("mirefen_coven", base=0.5)
    k.mat(iron=flat(IRON, 0.62, bevel=0.1), bone=bone(R["acc"], 0.72), steam=flat(ramp("#2a4a2a", "#4a7a3a", "#88b868"), 0.5))
    m = disc(0, 0, 12, 28)
    body(k, m, "iron", F=2.0)
    k.plate(ring(0, 0, 12.8, 11.4), 1.4, "iron", z=Z - 0.4)
    for j in range(10):
        a = j * math.pi / 5
        x, y = math.cos(a) * 8.6, math.sin(a) * 8.6
        on(k, L([(x - 0.9, y - 0.8), (x + 0.6, y + 0.9), (x + 0.9, y - 0.6), (x - 0.5, y + 0.6)], 0.5), 0.2, "glow", 1.0, glow=True)
    on(k, disc(0, 0, 3.2, 12), 2.6, "bone", 1.3)
    on(k, disc(-1.1, 0.5, 0.8, 6) + disc(1.1, 0.5, 0.8, 6), 0.3, "glow", 2.7, glow=True)
    on(k, rect(-1.2, -3.6, 1.2, -2.4), 1.8, "bone", 1.1)
    grip_(k)


@design("sun_disc_shield")
def sun_disc_shield(k):
    """a sheet of beaten gold in the shape of noon, lapis bands inside, the rays cut short and hammered sharp"""
    k.theme("sandsunk_tomb", base=0.56)
    lapis = ramp("#081a4a", "#0e2a6e", "#163e96", "#2458c0", "#4a84e0")
    k.mat(gold=flat(GOLD, 0.66, bevel=0.1), dgold=flat(GOLD, 0.44, bevel=0.1), lapis=flat(lapis, 0.56))
    m = disc(0, 0, 10, 26)
    for j in range(16):
        a = 2 * math.pi * j / 16
        ln = 14 if j % 2 else 12.2
        m = m + P((math.cos(a - 0.2) * 9.6, math.sin(a - 0.2) * 9.6), (math.cos(a) * ln, math.sin(a) * ln), (math.cos(a + 0.2) * 9.6, math.sin(a + 0.2) * 9.6))
    body(k, m, "gold", F=1.6)
    on(k, ring(0, 0, 8.6, 7.2), 0.5, "lapis", 0.9)
    on(k, ring(0, 0, 6.2, 5.4), 0.5, "dgold", 0.9)
    on(k, disc(0, 0, 3.2, 14), 0.8, "gold", 1.0)
    grip_(k)


@design("solar_aegis")
def solar_aegis(k):
    """the winged sun of the old kings: a great disc with two uraeus cobras, wings of gold and lapis spreading wider than a man's shoulders"""
    k.theme("sandsunk_tomb", base=0.56)
    lapis = ramp("#081a4a", "#0e2a6e", "#163e96", "#2458c0", "#4a84e0")
    k.mat(gold=flat(GOLD, 0.66, bevel=0.12), lapis=flat(lapis, 0.56, bevel=0.1), teal=flat(ramp("#04181a", "#082c30", "#104a4e", "#1c7070", "#38a09a"), 0.6, bevel=0.1), sun=fire(ramp("#e07010", "#ffa81c", "#ffd84a", "#fff4a8"), 0.3, 0.7))
    for s_ in (1, -1):
        for j, (y0, ln, mat) in enumerate(((8, 15.4, "gold"), (5, 13.6, "lapis"), (2, 12, "teal"), (-1, 10, "gold"), (-4, 8, "lapis"))):
            w = P(path((s_ * 2, y0 + 2), qb((s_ * ln * 0.6, y0 + 3.8), (s_ * ln * 0.9, y0 + 3), (s_ * (ln + 3), y0 - 1), 6), (s_ * (ln + 3), y0 - 1), qb((s_ * ln * 0.8, y0 - 0.8), (s_ * ln * 0.5, y0 - 1), (s_ * 2, y0 - 1), 6)))
            k.plate(w, 1.0, mat, z=Z + 0.2 - j * 0.1)
    k.plate(heater(6, 11, -14), 1.6, "gold", z=Z - 0.4)
    on(k, disc(0, 5, 5.0, 16), 0.8, "lapis", 0.8)
    on(k, disc(0, 5, 3.8, 14), 1.0, "sun", 1.0, glow=True)
    for s_ in (1, -1):
        on(k, stroke((s_ * 5, 4), (s_ * 6.4, 8), (s_ * 4.6, 10.6), 0.8) + disc(s_ * 4.4, 11, 0.9, 6), 0.6, "teal", 1.2)
    on(k, rect(-0.7, -10, 0.7, -1), 0.5, "lapis", 0.8)
    grip_(k)


@design("valve_shield")
def valve_shield(k):
    """a valve from the Titan's heart: three pale cusps meeting in a Y, a ring of cartilage, the chordae hanging behind it"""
    k.theme("fallen_titan", base=0.5)
    meat = ramp("#2a0608", "#4a0c10", "#6e161a", "#942428", "#b83c3a", "#d8625a")
    k.mat(cusp=flat(ramp("#a89478", "#c4b094", "#dccab0", "#efe4cc"), 0.6, bevel=0.1), ringc=flat(IVORY, 0.78, bevel=0.1), meat=flat(meat, 0.5, 0.2), hot=fire(meat, 0.5, 0.5))
    m = disc(0, 0, 12, 26)
    body(k, m, "meat", "ringc", band=1.8, F=2.0)
    for a in (90, 210, 330):
        r = math.radians(a)
        d = (math.cos(r), math.sin(r))
        t_ = (-d[1], d[0])
        cusp = P((0, 0), (d[0] * 5.4 + t_[0] * 5.2, d[1] * 5.4 + t_[1] * 5.2), (d[0] * 9.6, d[1] * 9.6), (d[0] * 5.4 - t_[0] * 5.2, d[1] * 5.4 - t_[1] * 5.2))
        on(k, cusp & disc(0, 0, 10, 24), 0.8, "cusp", 1.0)
    for a in (30, 150, 270):
        r = math.radians(a)
        on(k, L([(0, 0), (math.cos(r) * 10, math.sin(r) * 10)], 0.5), 0.8, "hot", 1.1, glow=True)
    grip_(k)


@design("heart_valve")
def heart_valve(k):
    """the great valve, torn out with a piece of the chamber wall: raw red muscle round pale cusps, opening and closing a slit of light, arteries jutting from its rim"""
    meat = ramp("#2a0608", "#4a0c10", "#6e161a", "#942428", "#b83c3a", "#d8625a", "#f09a8a")

    def muscle(p, n, b, key, i, j, w, h, fr):
        return at(meat, 0.5 + lit(key, i, j, w, h) + 0.14 * math.sin(p[0] * 1.8 + p[1] * 1.1))

    k.mat(muscle=muscle, cusp=flat(ramp("#a89478", "#c4b094", "#dccab0", "#efe4cc"), 0.66, bevel=0.1), hot=fire(ramp("#e02830", "#ff6a5a", "#ffc0a8", "#ffffff"), 0.3, 0.7), vessel=flat(meat, 0.4, bevel=0.1), fat=flat(ramp("#a07c34", "#d0ae56", "#ecd488", "#faeec4"), 0.6, 0.3), wrap=flat(meat, 0.5), dark=flat(meat, 0.3))
    m = disc(0, 0, 12.4, 14) + disc(-3, 5, 11, 12) + disc(3, -5, 10.6, 12)
    k.plate(m, 3.0, "muscle", z=Z)
    for s_ in (1, -1):
        on(k, P((0, 8), (s_ * 7, 3), (s_ * 7, -3), (0, -8)), 0.8, "cusp", 1.4)
    on(k, P((-0.8, 9), (0.8, 9), (0.8, -9), (-0.8, -9)), 1.0, "hot", 1.5, glow=True)
    for a, b in (((-11, 8), (-16, 13)), ((10, 10), (15, 14)), ((12, -7), (17, -6))):
        k.plate(L([a, b], 2.6), 2.4, "vessel", z=Z)
        k.plate(disc(b[0], b[1], 1.0, 8), 2.6, "hot", z=Z, glow=True)
    on(k, L(qb((-9, -3), (-4, -10), (6, -10), 8), 0.8), 0.4, "fat", 1.4)
    grip_(k)


@design("lotus_shield")
def lotus_shield(k):
    """an open lotus of jade from above: three ranks of petals and a gold seed head at its heart"""
    R = k.theme("jade_monastery", base=0.56)
    k.mat(jade=flat(R["blade"], 0.5, bevel=0.14), j2=flat(R["blade"], 0.66, bevel=0.14), j3=flat(R["blade"], 0.82, bevel=0.1), gold=flat(GOLD, 0.64, bevel=0.14))
    for rank, (n, ln, w, mat, up) in enumerate(((9, 13.4, 3.6, "jade", 0.0), (7, 10.0, 3.2, "j2", 0.5), (5, 6.6, 2.4, "j3", 1.0))):
        for j in range(n):
            a = 2 * math.pi * (j + rank * 0.5) / n
            d, t_ = (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a))
            p_ = P((0, 0), (d[0] * ln * 0.6 + t_[0] * w, d[1] * ln * 0.6 + t_[1] * w), (d[0] * ln, d[1] * ln), (d[0] * ln * 0.6 - t_[0] * w, d[1] * ln * 0.6 - t_[1] * w))
            k.plate(p_, 1.0, mat, z=Z + up)
    on(k, disc(0, 0, 2.6, 12), 1.0, "gold", 2.0)
    grip_(k)


@design("lotus_throne")
def lotus_throne(k):
    """the Thousand-Handed One's seat: a lotus base in gold and jade, a halo of arms fanned out behind it, each hand open, the seat itself empty"""
    R = k.theme("jade_monastery", base=0.56)
    k.mat(jade=flat(R["blade"], 0.62, bevel=0.14), gold=flat(GOLD, 0.64, bevel=0.14), hand=flat(GOLD, 0.78, bevel=0.1), halo=fire(GOLD, 0.4, 0.6), void=flat(R["dark"], 0.3))
    k.plate(heater(7, 12, -8), 1.2, "void", z=Z - 0.2)
    for j in range(11):
        a = math.radians(-20 + j * 22)
        d = (math.cos(a), math.sin(a))
        o = (d[0] * 4, 2 + d[1] * 4)
        e = (d[0] * 12.4, 2 + d[1] * 12.4)
        m = L([o, e], 1.0) + disc(e[0], e[1], 1.2, 8)
        for f in (-0.5, 0, 0.5):
            m = m + L([e, (e[0] + math.cos(a + f) * 2.6, e[1] + math.sin(a + f) * 2.6)], 0.6)
        k.plate(m, 0.8, "hand", z=Z)
    k.plate(ring(0, 2, 11.4, 10.6) & rect(-13, -4, 13, 15), 0.7, "halo", z=Z + 0.4, glow=True)
    for rank, y in enumerate((-13, -9.4, -6)):
        n = 7 - rank
        for j in range(n):
            x = (j - (n - 1) / 2) * (3.2 - rank * 0.1)
            on(k, P((x - 1.6, y), (x + 1.6, y), (x + 1.2, y + 3), (x, y + 4.6), (x - 1.2, y + 3)), 0.6, "gold" if (j + rank) % 2 else "jade", 1.0 + rank * 0.2)
    grip_(k)


@design("bastion_shield")
def bastion_shield(k):
    """a wall of the Bastion with its battlements on: dressed storm-grey ashlar, an arrow slit and a lit window a long way up"""
    R = k.theme("storm_bastion", base=0.5)
    stone = ramp("#141a22", "#1e2630", "#2a3442", "#384454", "#485668", "#5c6c80", "#7a8a9e")

    def ashlar(p, n, b, key, i, j, w, h, fr):
        rw = int(math.floor((p[1] + 20) / 3))
        x = p[0] + (rw % 2) * 2
        v = 0.6 + lit(key, i, j, w, h) + 0.1 * (rw % 3 - 1) * 0.5
        if (p[1] + 20) % 3 < 0.5 or (x + 40) % 4.6 < 0.5:
            v -= 0.3
        return at(stone, v)

    k.mat(ashlar=ashlar, cap=flat(stone, 0.8, bevel=0.1))
    m = rect(-8, -13, 8, 10)
    for x in (-8, -3.4, 1.4, 5.8):
        m = m + rect(x, 10, x + 2.4, 13.6)
    body(k, m, "ashlar", F=2.6)
    on(k, rect(-0.7, -7, 0.7, 1), 0.3, "dark", 1.2)
    on(k, rect(-2.2, -3.6, 2.2, -2.8), 0.3, "dark", 1.2)
    on(k, rect(-4, 5, -2.4, 7.6) + rect(2.4, 5, 4, 7.6), 0.3, "glow", 1.2, glow=True)
    on(k, rect(-8.6, 8.8, 8.6, 10), 0.6, "cap", 1.4)
    grip_(k)


@design("lightning_rod_aegis")
def lightning_rod_aegis(k):
    """a storm iron kite with a real lightning rod bolted up its spine: copper coiled at the boss, and a bolt pinned forked across the face"""
    R = k.theme("storm_bastion", base=0.5)
    k.mat(iron=flat(R["blade"], 0.52, bevel=0.12), copper=flat(ramp("#3a1a08", "#6a3414", "#9c5a24", "#c8843c", "#e8a860"), 0.62, bevel=0.1), white=flat(R["glow"], 0.92, bevel=0.02))
    m = kite(8, 12, -14, 4)
    body(k, m, "iron", "dark", band=1.0)
    k.plate(rect(-0.8, -12, 0.8, 14) + P((-1.4, 14), (1.4, 14), (0, 17.6)), 1.4, "copper", z=Z + 1.2)
    for y in (-6, 2):
        for j in range(5):
            on(k, rect(-2.8, y + j * 0.7, 2.8, y + j * 0.7 + 0.5), 1.2, "copper", 1.4)
    on(k, L([(-7, 9), (-3, 4), (-5, 2), (0, -2), (-2, -3), (2, -11)], 0.8) + L([(-3, 4), (3, 8), (1.6, 4), (7, 6)], 0.6), 0.3, "white", 1.0, glow=True)
    grip_(k)


@design("crest_shield")
def crest_shield(k):
    """a Court gentleman's arms: a black heater with a silver crescent and a red bat, gold fretting at the edge"""
    R = k.theme("bloodmoon_court", base=0.5)
    k.mat(black=flat(ramp("#14040a", "#280a12", "#42101c", "#5e1a28"), 0.5, bevel=0.1), gold=flat(GOLD, 0.62, bevel=0.14), moon=flat(SILVER, 0.76), bat=flat(RUBY, 0.56, bevel=0.1))
    m = heater(7.8, 12, -13)
    body(k, m, "black", "gold", band=0.9)
    on(k, disc(0, 2, 7.2, 20) - disc(0, 3.8, 6.8, 20), 0.3, "moon", 1.0)
    bat = P((0, 6), (1, 7.4), (1.8, 5.8), (6.6, 7), (5, 4.6), (3.6, 4.8), (2.6, 3.4), (1, 3.8), (0, 1.8), (-1, 3.8), (-2.6, 3.4), (-3.6, 4.8), (-5, 4.6), (-6.6, 7), (-1.8, 5.8), (-1, 7.4))
    on(k, bat, 0.3, "bat", 1.0)
    grip_(k)


@design("velvet_aegis")
def velvet_aegis(k):
    """the Countess's chair back, more or less: deep buttoned red velvet in a carved black frame, one drop of something else on it"""
    R = k.theme("bloodmoon_court", base=0.5)

    def tuft(p, n, b, key, i, j, w, h, fr):
        return at(RUBY_V, 0.5 + lit(key, i, j, w, h) + 0.24 * math.cos(p[0] * 1.3) * math.cos(p[1] * 1.3))

    RUBY_V = ramp("#2a0408", "#46080e", "#640e14", "#84161c", "#a4242a")
    k.mat(tuft=tuft, frame=flat(ramp("#0a0608", "#161014", "#241a20", "#34262e"), 0.66, bevel=0.14), gold=flat(GOLD, 0.7), hot=fire(RUBY, 0.3, 0.6))
    m = P(path((-8, -13), (8, -13), (8, 6), qb((8, 13), (3, 12), (0, 15.4), 8), qb((0, 15.4), (-3, 12), (-8, 13), 8), (-8, 6)))
    k.plate(m.inset(1.2), 2.4, "tuft", z=Z)
    k.plate(m - m.inset(1.2), 2.8, "frame", z=Z)
    for y in (-9.6, -4.8, 0, 4.8, 9.6):
        for x in (-4.8, 0, 4.8):
            k.plate(disc(x + (2.4 if int(y / 4.8) % 2 else 0), y, 0.5, 6) & m.inset(1.6), 2.9, "gold", z=Z)
    on(k, P(path(qb((2.6, 2.6), (1.4, 0), (2.6, -1), 5), qb((2.6, -1), (3.8, 0), (2.6, 2.6), 5))), 0.4, "hot", 1.2, glow=True)
    grip_(k)


@design("maze_wall_shield")
def maze_wall_shield(k):
    """a block cut from the Labyrinth's wall, its passages shown in plan on the surface, a thread of gold following one of them to nowhere"""
    R = k.theme("obsidian_labyrinth", base=0.46)
    k.mat(stone=flat(R["blade"], 0.42, 0.14, bevel=0.1), gold=flat(GOLD, 0.68), wall=flat(R["blade"], 0.68, bevel=0.1))
    m = rect(-8, -13, 8, 13)
    body(k, m, "stone", "wall", band=0.9, F=2.2)
    plan = Mask()
    for (x0, y0, x1, y1) in ((-6, 10, 5, 11), (-6, -11, -5, 10), (-3.6, -8, -2.6, 8), (-3.6, 7.4, 3, 8.4), (2, -3, 3, 8), (-1.2, -5.4, 3.6, -4.4), (5, -11, 6, 6), (-6, -11, 2, -10), (-1.2, -5, -0.2, 5), (-1.2, 4.8, 0.8, 5.6)):
        plan = plan + rect(x0, y0, x1, y1)
    on(k, plan, 0.6, "wall", 1.0)
    on(k, L([(-4.4, -12), (-4.4, 9), (4, 9), (4, -2), (0.6, -2), (0.6, 3)], 0.4), 0.2, "gold", 1.3)
    grip_(k)


@design("ninth_gate")
def ninth_gate(k):
    """the last door: two black leaves meeting in a line of light, a great ring knocker in each, the bronze bull's skull over the lintel"""
    R = k.theme("obsidian_labyrinth", base=0.46)
    k.mat(door=flat(R["blade"], 0.42, bevel=0.1), bronze=flat(BRASS, 0.62, bevel=0.14), bone=bone(IVORY, 0.7), hot=fire(GOLD, 0.5, 0.5))
    m = P(path((-9, -14), (9, -14), (9, 8), qb((9, 14), (0, 16), (-9, 14), 8)))
    body(k, m, "door", "bronze", band=1.0, F=2.4)
    k.plate(rect(-0.4, -14, 0.4, 14.4), 2.5, "hot", z=Z, glow=True)
    for x in (-5, 5):
        on(k, ring(x, -2, 2.6, 1.6), 0.5, "bronze", 1.6)
        on(k, disc(x, 0.6, 0.9, 8), 0.8, "bronze", 1.5)
        rivets(k, [(x - 3, 8), (x, 8), (x + 3, 8), (x - 3, -10), (x, -10), (x + 3, -10)], "bronze", 0.8, 1.5)
    on(k, P((-2.6, 12.6), (2.6, 12.6), (1.4, 8.2), (-1.4, 8.2)), 0.8, "bone", 1.5)
    for s_ in (1, -1):
        on(k, stroke((s_ * 2, 12.4), (s_ * 6.6, 12), (s_ * 7, 16.6), 1.0), 0.6, "bone", 1.5)
    grip_(k)


def fresnel(k, r0, steps=5):
    for j in range(steps):
        r_ = r0 * (1 - j / steps)
        on(k, ring(0, 0, r_, r_ - r0 / steps + 0.4), 0.6 + j * 0.2, "lens" if j % 2 else "lens2", 0.8 + j * 0.05)


@design("lens_shield")
def lens_shield(k):
    """one bull's-eye panel out of the great Fresnel lens: stepped rings of thick sea-green glass in a brass frame, and light still caught in the middle"""
    R = k.theme("abyssal_lighthouse", base=0.5)
    k.mat(lens=flat(ramp("#4a8a90", "#74b8bc", "#a4dcde", "#d8f8f8"), 0.5, bevel=0.2), lens2=flat(ramp("#2a6a70", "#4a9aa0", "#7cc0c4", "#a4dcde"), 0.5, bevel=0.2), brass=flat(BRASS, 0.64), hot=fire(R["glow"], 0.5, 0.5))
    m = rect(-9, -11.4, 9, 11.4)
    body(k, m, "brass", F=1.2)
    k.plate(m - m.inset(1), 2.6, "brass", z=Z)
    fresnel(k, 9)
    on(k, disc(0, 0, 1.8, 10), 1.6, "hot", 1.4, glow=True)
    rivets(k, [(-8, -10.4), (8, -10.4), (-8, 10.4), (8, 10.4)], "brass", 1.0, 1.4)
    grip_(k)


@design("lens_of_the_keeper")
def lens_of_the_keeper(k):
    """the whole lens, and the thing that came up to look into it: a round of burning glass with black tentacles curled over the rim, feeling for the seam"""
    R = k.theme("abyssal_lighthouse", base=0.5)
    fish = ramp("#08060e", "#10101a", "#1a1a2a", "#28283e", "#3a3a56")
    k.mat(lens=flat(ramp("#b08a3a", "#e0bc60", "#fce09a", "#fff8d8"), 0.6, bevel=0.2), lens2=flat(ramp("#8a6a2a", "#c09a48", "#e8c878", "#fce09a"), 0.6, bevel=0.2), iron=flat(IRON, 0.7), hot=fire(ramp("#ffd878", "#fff4c8", "#ffffff"), 0.4, 0.6), tent=flat(fish, 0.56, bevel=0.1), sucker=flat(R["glow"], 0.8))
    m = disc(0, 0, 12.4, 28)
    body(k, m, "iron", F=1.4)
    k.plate(m - m.inset(1.2), 2.8, "iron", z=Z)
    fresnel(k, 11)
    on(k, disc(0, 0, 2.0, 12), 1.6, "hot", 1.4, glow=True)
    for a0, sw, ln in ((200, 60, 12), (330, -70, 11), (100, 40, 9)):
        pts = []
        for j in range(12):
            t = j / 11
            a = math.radians(a0 + sw * t)
            r_ = 14.4 - ln * t
            pts.append((math.cos(a) * r_, math.sin(a) * r_))
        for j, (p_, q) in enumerate(zip(pts, pts[1:])):
            k.seg(p_, q, 2.6 - j * 0.2, 1.8, "tent", z=Z + 2.2)
            if j % 3 == 1:
                k.box(p_[0], p_[1] - 0.3, Z + 3.1, 0.6, 0.6, 0.3, "sucker")
    grip_(k)


@design("cathedral_shield")
def cathedral_shield(k):
    """a rose window from the nave, stone tracery and all: twelve petals of stained glass, deep blue and gold, still lit from somewhere behind"""
    k.theme("eclipse_cathedral", base=0.5)
    blue = ramp("#0a1a5a", "#14308a", "#2050c0", "#4a84e8")
    red = ramp("#5a0a14", "#8a1420", "#c02a30", "#f05a50")
    gold = ramp("#7a5a10", "#b88a1c", "#e8c040", "#fff0a0")

    def glass(p, n, b, key, i, j, w, h, fr):
        a = (math.atan2(p[1], p[0]) + math.pi) / (2 * math.pi) * 12
        d = math.hypot(p[0], p[1])
        R_ = (blue, red, gold)[(int(a) + (1 if d > 7 else 0)) % 3]
        return at(R_, 0.3 + 0.5 * ((a % 1) - 0.5) ** 2 * 4)

    k.mat(glass=glass, stone=flat(ramp("#4a4a54", "#6a6a74", "#8c8c96", "#b0b0ba", "#d0d0d8"), 0.56, bevel=0.14))
    m = disc(0, 0, 12.4, 28)
    k.plate(m, 0.8, "glass", z=Z, glow=True)
    k.plate(m - m.inset(1.4), 3.0, "stone", z=Z)
    for j in range(12):
        a = j * math.pi / 6
        k.plate(L([(math.cos(a) * 2, math.sin(a) * 2), (math.cos(a) * 11.4, math.sin(a) * 11.4)], 0.8), 2.2, "stone", z=Z)
    k.plate(ring(0, 0, 7.4, 6.6) + ring(0, 0, 2.6, 1.8), 2.4, "stone", z=Z)
    grip_(k)


@design("black_sun_aegis")
def black_sun_aegis(k):
    """the eclipse at totality: a perfectly black disc, its corona streaming out in long uneven tongues"""
    k.theme("eclipse_cathedral", base=0.5)
    k.mat(void=flat(ramp("#000000", "#040408", "#0a0a10"), 0.4, bevel=0.1), corona=fire(ramp("#d0a040", "#ffe08a", "#fff6d0", "#ffffff"), 0.2, 0.8), rim=fire(ramp("#fff6d0", "#ffffff"), 0.4, 0.6))
    m = Mask()
    for j in range(20):
        a = 2 * math.pi * j / 20 + 0.2 * math.sin(j * 2.3)
        ln = 13.4 + 3.4 * math.sin(j * 1.7) ** 2
        m = m + P((math.cos(a - 0.2) * 10.6, math.sin(a - 0.2) * 10.6), (math.cos(a) * ln, math.sin(a) * ln), (math.cos(a + 0.2) * 10.6, math.sin(a + 0.2) * 10.6))
    k.plate(m, 0.8, "corona", z=Z, glow=True)
    k.plate(ring(0, 0, 11.4, 10.4), 1.2, "rim", z=Z, glow=True)
    k.plate(disc(0, 0, 10.6, 26), 2.4, "void", z=Z)
    grip_(k)


@design("gold_heap_shield")
def gold_heap_shield(k):
    """coins, and more coins, run together in the Wyrm's breath into one lumpy plate: goblets and a crown half sunk in it, a ruby here and there"""
    k.theme("wyrms_hoard", base=0.6)
    k.mat(gold=flat(GOLD, 0.56, 0.2, bevel=0.1), coin=flat(GOLD, 0.74, bevel=0.14), gem=gem(RUBY), bluegem=gem(ramp("#0a2a6a", "#144aa0", "#2a7ae0", "#7ab4ff", "#d0e8ff")))
    m = P((-9, 8), (-6, 12), (0, 13.6), (6, 12), (9, 8), (8.6, -6), (5, -12), (0, -14), (-5, -12), (-8.6, -6))
    body(k, m, "gold", F=2.2)
    pts = [(-5, 8), (-1, 10), (4, 9), (6, 4), (-6, 3), (-2, 5), (2, 4), (-4, -1), (0, 0), (5, -1), (-5, -6), (-1, -5), (3, -6), (0, -10), (-3, -9.4), (3.4, -10)]
    for j, (x, y) in enumerate(pts):
        on(k, disc(x, y, 1.9, 10) - disc(x, y, 1.1, 8) + disc(x, y, 0.5, 5), 0.5 + (j % 3) * 0.2, "coin", 1.1 + (j % 3) * 0.14)
    on(k, disc(-2, 1.6, 1.4, 8), 1.2, "gem", 1.2)
    on(k, disc(4, 5.8, 1.1, 8), 1.2, "bluegem", 1.2)
    grip_(k)


@design("scale_of_ignavar")
def scale_of_ignavar(k):
    """one scale off the Wyrm's breast, and that's the whole shield: a leaf of red-gold horn with a raised keel, ember in the growth lines, the root still bleeding light"""
    k.theme("wyrms_hoard", base=0.6)
    red = ramp("#1a0406", "#34080a", "#561010", "#7a1a14", "#a42c1a", "#cc4a24", "#f07a3a")

    def scale(p, n, b, key, i, j, w, h, fr):
        return at(red, 0.4 + (p[1] + 14) * 0.022 + lit(key, i, j, w, h) + (0.14 if p[0] < 0 else -0.08) + 0.08 * math.sin(math.hypot(p[0], p[1] + 14) * 1.5))

    k.mat(scale=scale, keel=flat(GOLD, 0.66, bevel=0.14), hot=fire(ramp("#7a1406", "#c0300a", "#ff6a14", "#ffb040", "#ffe8a0"), 0.3, 0.7))
    m = P(path(qb((0, 16), (-13, 6), (-9, -7), 10), qb((-9, -7), (-5, -13), (0, -15), 6), qb((0, -15), (5, -13), (9, -7), 6), qb((9, -7), (13, 6), (0, 16), 10)))
    body(k, m, "scale", "keel", band=0.7, F=2.4)
    on(k, P((0, 13), (1.6, 0), (0, -13), (-1.6, 0)), 1.2, "keel", 1.1)
    for r_ in (8, 12):
        on(k, (disc(0, 15, r_ + 0.4, 20) - disc(0, 15, r_, 20)) & m.inset(1.2), 0.2, "hot", 1.3, glow=True)
    grip_(k)


# ---------------------------------------------------------------- the world's

@design("oak_round_shield")
def oak_round_shield(k):
    """planks, an iron rim, a boss. It does the job"""
    k.mat(oak=staves(ramp("#3a2410", "#52341c", "#6e4826", "#8c6034", "#a87a48"), 2.8, 0.56), iron=flat(IRON, 0.7, bevel=0.14), dark=flat(IRON, 0.66), wrap=wrap(LEATHER, IRON[1], 5))
    m = disc(0, 0, 11, 26)
    body(k, m, "oak", "iron", band=1.1)
    on(k, disc(0, 0, 2.9, 12), 1.6, "iron", 1.2)
    rivets(k, [(math.cos(a * math.pi / 4) * 9.7, math.sin(a * math.pi / 4) * 9.7) for a in range(8)], "dark", 0.8, 1.6)
    grip_(k)


@design("lion_crest")
def lion_crest(k):
    """a knight's heater in blue with a gold lion rampant, a little wind-worn"""
    blue = ramp("#0a1838", "#102450", "#18346e", "#22488c", "#3060a8")
    k.mat(blue=flat(blue, 0.56, bevel=0.1), gold=flat(GOLD, 0.68, bevel=0.12), dark=flat(IRON, 0.66), wrap=wrap(LEATHER, IRON[1], 5), silver=flat(SILVER, 0.6))
    m = heater(7.8, 12, -13)
    body(k, m, "blue", "silver", band=0.9)
    lion = P((-1.4, 5), (1, 6), (2.4, 8.6), (3.6, 6.6), (4.6, 7.4), (3.0, 4.4), (3.6, 2.8), (5.0, 2.0), (3.4, 1.0), (1.6, 1.6), (2.4, -3), (3.4, -6.6), (1.6, -5.4), (0.2, -2.8), (-1.6, -6.0), (-3.4, -5.6), (-2.2, -1), (-3.6, 2), (-5.4, 0.4), (-5.2, 3), (-3.2, 3.8))
    on(k, lion, 0.5, "gold", 1.0)
    on(k, L([(-3.4, 1.8), (-6.2, 3.6), (-6.2, 7)], 0.5), 0.4, "gold", 1.0)
    grip_(k)


@design("mirror_of_ash")
def mirror_of_ash(k):
    """a black glass kite with a fire behind the eye cut in it: it looks back"""
    black = ramp("#08080a", "#101014", "#18181e", "#22222a", "#2e2e38")
    ember = ramp("#7a1406", "#c0300a", "#ff6a14", "#ffb040", "#ffe8a0", "#fffbe0")
    k.mat(black=flat(black, 0.6, bevel=0.14), iron=flat(IRON, 0.66, bevel=0.14), hot=fire(ember, 0.3, 0.7), dark=flat(IRON, 0.66), wrap=wrap(LEATHER, IRON[1], 5))
    m = kite(8, 13, -15, 5)
    eye = P(path(qb((-6, 3), (0, 8.4), (6, 3), 8), qb((6, 3), (0, -2.4), (-6, 3), 8)))
    body(k, m - eye, "black", "iron", band=1.0, F=2.0)
    k.plate(eye, 1.0, "hot", z=Z, glow=True)
    k.plate(disc(0, 3, 2.0, 12) - rect(-0.4, 0, 0.4, 6), 1.6, "black", z=Z)
    for pts in (((-6, 3), (-5, -3), (-3, -8)), ((6, 3), (4, -4), (1, -10))):
        on(k, L(list(pts), 0.5), 0.2, "hot", 1.2, glow=True)
    grip_(k)


@design("aegis_of_dawn")
def aegis_of_dawn(k):
    """a tower of white gold, the sun coming up across its lower half, rays running to the rim, the top still night blue with one star"""
    pale = ramp("#6a5a3a", "#8c7a52", "#b09c6c", "#cec08a", "#e6dcae", "#f6f0d2", "#fffbec", "#ffffff")
    night = ramp("#0a1838", "#142858", "#1e3a7a")
    k.mat(pale=flat(pale, 0.72, bevel=0.1), gold=flat(GOLD, 0.66, bevel=0.14), sun=fire(ramp("#ff8a1c", "#ffc84a", "#fff0b0", "#ffffff"), 0.3, 0.7), night=flat(night, 0.5, bevel=0.04), ray=flat(GOLD, 0.8), star=fire(ramp("#ffffff", "#ffffff"), 0.5, 0.5), dark=flat(GOLD, 0.5), wrap=wrap(LEATHER, GOLD[3], 5))
    m = P(path((-8.4, -15), (8.4, -15), (8.4, 9), qb((8.4, 14), (0, 17), (-8.4, 14), 6)))
    body(k, m, "pale", "gold", band=1.1, F=2.0)
    on(k, (m.inset(1.1)) & rect(-9, 2, 9, 17), 0.2, "night", 0.9)
    for j in range(9):
        a = math.radians(j * 22.5)
        on(k, P((math.cos(a - 0.08) * 5.4, -3 + math.sin(a - 0.08) * 5.4), (math.cos(a) * 13, -3 + math.sin(a) * 13), (math.cos(a + 0.08) * 5.4, -3 + math.sin(a + 0.08) * 5.4)) & m.inset(1.1), 0.2, "ray", 1.0)
    on(k, disc(0, -3, 5.2, 18) & rect(-9, -3, 9, 9), 0.5, "sun", 1.0, glow=True)
    on(k, rect(-7, -4, 7, -3), 0.5, "gold", 1.1)
    on(k, P((0, 13), (0.7, 11.2), (2.4, 10.6), (0.7, 10), (0, 8.2), (-0.7, 10), (-2.4, 10.6), (-0.7, 11.2)), 0.2, "star", 1.2, glow=True)
    grip_(k)


@design("raiders_targe")
def raiders_targe(k):
    """a bandit's little round targe of studded hide, a long spike through the boss so it's a second weapon"""
    k.mat(hide=flat(ramp("#2a1a0e", "#3e2816", "#543820", "#6c4a2c"), 0.56, 0.2, bevel=0.1), iron=flat(IRON, 0.7, bevel=0.14), spike=flat(SILVER, 0.56, bevel=0.1), red=flat(ramp("#2a0606", "#4a0c0a", "#741612"), 0.6), dark=flat(IRON, 0.66), wrap=wrap(LEATHER, IRON[1], 5))
    m = disc(0, 0, 9, 22)
    body(k, m, "hide", "iron", band=0.9)
    rivets(k, [(math.cos(a * math.pi / 4) * r_, math.sin(a * math.pi / 4) * r_) for a in range(8) for r_ in (4.4, 6.8)], "iron", 0.8, 1.2)
    on(k, disc(0, 0, 2.4, 10), 1.4, "iron", 1.2)
    for j, w in enumerate((1.8, 1.3, 0.8, 0.4)):
        k.box(0, -w / 2, Z + 2.6 + j * 1.6, w, w, 1.7, "spike")
    grip_(k)


@design("legion_scutum")
def legion_scutum(k):
    """a legionary's great curved scutum: red, gold sun on the boss, gold bolts running out to the corners, bronze at the edge. The face really curves"""
    red = ramp("#2a0606", "#4a0c0a", "#741612", "#9c2218", "#c23a26")
    k.mat(red=flat(red, 0.6, bevel=0.1), gold=flat(GOLD, 0.68, bevel=0.1), bronze=flat(BRASS, 0.62, bevel=0.14), dark=flat(IRON, 0.66), wrap=wrap(LEATHER, IRON[1], 5))
    for j in range(9):
        x = -8 + j * 1.8
        z = Z + 1.4 - (x / 8) ** 2 * 2.4
        k.box(x + 0.9, -14, z, 1.85, 28, 1.4, "red")
        k.box(x + 0.9, 13.0, z, 1.85, 1.2, 1.8, "bronze")
        k.box(x + 0.9, -14.4, z, 1.85, 1.2, 1.8, "bronze")
    on(k, disc(0, 0, 3.6, 12), 1.6, "bronze", 1.6)
    on(k, disc(0, 0, 2.2, 10), 1.8, "gold", 1.6)
    for s_ in (1, -1):
        for t_ in (1, -1):
            on(k, L([(s_ * 2.6, t_ * 2.8), (s_ * 4.2, t_ * 5.4), (s_ * 3.0, t_ * 6), (s_ * 6, t_ * 11)], 0.7), 0.5, "gold", 1.2 - abs(s_) * 0.2)
    grip_(k)


@design("brood_carapace")
def brood_carapace(k):
    """the back plate of a hive soldier, wing cases shut along the middle, its mandibles left on at the brow, a row of dead eyes that still seem to follow you"""
    chitin = ramp("#0c0a14", "#181420", "#262034", "#362c4a", "#4a3e66", "#6a5a90", "#9080c0")
    k.mat(chitin=flat(chitin, 0.56, bevel=0.14), seam=flat(chitin, 0.1), mand=flat(chitin, 0.74, bevel=0.2), eye=fire(ramp("#3a6a2a", "#5a9a3a", "#88c850", "#c0f080"), 0.4, 0.6), dark=flat(chitin, 0.5), wrap=wrap(chitin, chitin[0], 4))
    m = P(path(qb((0, 11), (-11, 10), (-9, -4), 8), qb((-9, -4), (-7, -12), (0, -15), 6), qb((0, -15), (7, -12), (9, -4), 6), qb((9, -4), (11, 10), (0, 11), 8)))
    body(k, m, "chitin", F=2.8)
    on(k, rect(-0.4, -15, 0.4, 11), 0.2, "seam", 1.4)
    for s_ in (1, -1):
        for y in (-2, -7):
            on(k, stroke((s_ * 8, y + 3), (s_ * 4, y + 0.6), (s_ * 1, y + 3.4), 0.5), 0.2, "seam", 1.4)
        k.plate(P(path((s_ * 1, 10), qb((s_ * 5, 14), (s_ * 5, 18), (s_ * 0.6, 21), 6), (s_ * 0.6, 21), qb((s_ * 2.6, 17), (s_ * 2, 14), (s_ * 1, 13.4), 6))), 2.0, "mand", z=Z)
    for x in (-5.6, -2, 2, 5.6):
        on(k, disc(x, 7.2, 1.0, 8), 1.0, "eye", 1.1, glow=True)
    grip_(k)


@design("gryphon_aegis")
def gryphon_aegis(k):
    """the Sky Legion's bronze aspis: a gryphon's head stands out from the middle, its wings spread round the rim, a gold sky behind it"""
    bronze = ramp("#2a1606", "#432410", "#5e3618", "#7c4c22", "#9c6630", "#bc8444", "#d8a462", "#f0c88a")
    k.mat(bronze=flat(bronze, 0.56, bevel=0.1), gold=flat(GOLD, 0.68, bevel=0.14), feather=flat(bronze, 0.76, bevel=0.14), eye=gem(RUBY), dark=flat(IRON, 0.66), wrap=wrap(LEATHER, GOLD[3], 5))
    m = disc(0, 0, 13, 28)
    body(k, m, "bronze", "gold", band=1.3, F=2.0)
    for s_ in (1, -1):
        on(k, feathers(s_, -1, 7, 11.4, 120, 1.2) & disc(0, 0, 11.6, 24), 0.6, "feather", 1.1)
    h = P(path((-2.8, -5), qb((-5, 3), (-1, 7), (3, 5.4), 6), (3, 5.4), (6.4, 1.2), (3.4, 2.0), qb((2.4, -1), (3, -3), (2.8, -5), 4)))
    on(k, h, 1.8, "gold", 1.4)
    on(k, P((-3, 5), (-5, 9), (-1, 7)), 1.0, "gold", 1.6)
    on(k, disc(0.8, 3.6, 0.7, 6), 0.4, "eye", 2.4)
    grip_(k)


@design("the_closed_hand")
def the_closed_hand(k):
    """the shield is a fist: one great gauntlet closed and held out, iron on the back of it, gold across the knuckles"""
    fe = ramp("#2a2e34", "#3e444c", "#565e68", "#727c86", "#929ca6", "#b4bec6", "#d4dce2")
    k.mat(plate=flat(fe, 0.56, bevel=0.14), gold=flat(GOLD, 0.66, bevel=0.14), hot=fire(ramp("#ffb040", "#ffe8a0", "#fffbe0", "#ffffff"), 0.4, 0.6), dark=flat(IRON, 0.66), wrap=wrap(LEATHER, GOLD[3], 4))
    body(k, P((-8, -13), (8, -13), (9, 6), (-9, 6)), "plate", F=2.6)
    for j, x in enumerate((-6.6, -2.2, 2.2, 6.6)):
        k.plate(P((x - 2.1, 4), (x + 2.1, 4), (x + 2.1, 12.6 - abs(j - 1.5) * 0.6), (x, 14 - abs(j - 1.5) * 0.6), (x - 2.1, 12.6 - abs(j - 1.5) * 0.6)), 3.4, "plate", z=Z)
        on(k, rect(x - 1.8, 8, x + 1.8, 10.2), 0.8, "gold", 1.6)
    on(k, P((-9, 3), (-3, 2.4), (2, -2), (0, -5), (-5, -4), (-10, -1)), 1.2, "plate", 1.8)
    on(k, rect(-7, -10, 7, -7.6), 0.6, "gold", 1.2)
    on(k, rect(-0.5, -13, 0.5, 2), 0.2, "hot", 1.5, glow=True)
    grip_(k)
