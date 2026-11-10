"""The world's beasts, each built by hand (tools/vox2.py): not gate things but what lives out in the wild lands and got
too big and too old and too strange. None of them is an animal you know; each only remembers one. Every one has its
legend: the same kind grown huge and scarred and named, hunted from the posters.

    thornmaw        forest     a boar-bear the size of a cart, a thicket of black thorn grown out of its back, a jaw
                               split four ways, green sap glowing in its wounds
    old_blackbriar  legend     ... a ruined shrine grown up into its back, the briar thick as trees
    gorehorn        plains     a bison-rhino, a crown of six horns, bone plates, broken hunters' spears in its hide
    red_plough      legend     ... red to the horns, dragging the chain and plough of the farm it flattened
    frostjaw        snow       a sabre-tooth the size of a horse, ice tusks to past its chin, ice plates down its spine
    pale_widow      legend     ... a second pair of tusks, old blue ice, a frozen elk carried on her back
    sun_basilisk    desert     a long sand lizard, a frill of sun-bleached bone, eyes like molten glass, sand pouring
    sunbreaker      legend     ... a ruined temple's sun-disc fused into its frill, glass grown down its back
    bogmaw          swamp      a toad-crocodile with a mouth wider than itself, a lantern lure on its brow
    grandmother_mire legend    ... the size of a hut, reeds and skulls all over her, three lures
    vexclaw         jungle     a black panther-thing, four eyes, glowing stripes, four barbed tail-whips
    hollow_smile    legend     ... a grin split back to its ears, the stripes burning
    tidetusk        coast      a walrus-hound out of the surf, great tusks, barnacle armour, kelp, harpoons in its back
    old_harpoon     legend     ... a ship's anchor driven into its back, the chain dragging behind
    cragmaul        badlands   a knuckle-walking ape plated in rock, ore glinting in its back, a skull of stone
    walking_mountain legend    ... crystals and a waterfall running off its shoulders, a pine on its back

    python tools/monsterforge.py world_beasts --preview ; python tools/mobsheet.py world_beasts
"""
import math

import vox2 as X
from vox2 import C, ramp
from serpent_ziggurat import grow

# ================================================================ ramps

DARK = ramp("#07070a", "#0e0e12", "#16161c", "#1e1e26")
GORE = ramp("#100406", "#1e080a", "#2e0c10", "#401418")
BONE = ramp("#3a3428", "#5c5444", "#827a64", "#a8a088", "#cec6ac", "#ece6d0")
IVORY = ramp("#4a4232", "#6e6450", "#968a70", "#bcb094", "#ddd4b8", "#f4eedc")
IRON = ramp("#0a0b0e", "#14161a", "#1e2126", "#2a2e34", "#383d44", "#4a5058")
RUST = ramp("#1a0a04", "#2e1408", "#4a200c", "#683012", "#86421a", "#a45624")
WOOD = ramp("#0e0a07", "#1a130d", "#261c13", "#33261a", "#433223", "#56402c")
ROPE = ramp("#2a2216", "#3e3220", "#54462e", "#6c5c3e", "#867452")
STONE = ramp("#1c1e22", "#2a2d32", "#3a3e44", "#4c5158", "#60666e", "#787e86", "#9298a0")
MOSS = ramp("#0e1608", "#18240c", "#223412", "#2e4618", "#3c5a20", "#4e702a")

# forest
THORNFUR = ramp("#0c0806", "#160f0a", "#21170f", "#2d2015", "#3b2a1c", "#4b3624")
THORN = ramp("#08060a", "#110c12", "#1a131b", "#251b26", "#332533")
SAP = ramp("#1e5a10", "#3a8a18", "#5cc426", "#94ec4a", "#d4ffa0")
# plains
HIDE = ramp("#151110", "#211b18", "#2e2622", "#3d332d", "#4e4239", "#605247")
MANE = ramp("#0e0906", "#18100a", "#23180f", "#2f2015", "#3d2a1c")
HORN = ramp("#0a0908", "#151311", "#211e1a", "#2e2a25", "#3e3832", "#524a42")
BLOOD = ramp("#1a0404", "#2e0606", "#460a0a", "#621010", "#7e1a16", "#9a2620")
EMBER = ramp("#6a1006", "#a0200a", "#d84a12", "#ff8a30", "#ffd08a")
# snow
SNOWFUR = ramp("#3a424c", "#56606a", "#76808a", "#96a0aa", "#b8c0c8", "#dce2e8", "#f2f6f8")
SLATE = ramp("#10141a", "#1a2028", "#262e38", "#323c48")
ICEL = ramp("#2a5a8a", "#3e78aa", "#5a98c8", "#7ab8e0", "#a4d4f0", "#d4eefa")
OLDICE = ramp("#06183a", "#0c2a5c", "#164282", "#2462a8", "#3a86c8", "#68b0e4")
ICE = ramp("#0a2a5a", "#14508e", "#2a84c8", "#5ab8f4", "#a0e0ff", "#e8f8ff")
ELK = ramp("#1a120c", "#2a1e14", "#3a2a1c", "#4c3826", "#604832")
# desert
SANDSCALE = ramp("#2a1c0c", "#433016", "#5e4620", "#7a5e2c", "#987a3c", "#b49650", "#cfb46a")
SAND = ramp("#6a5232", "#8a6e44", "#a88a58", "#c4a66e", "#dcc088")
SUNBONE = ramp("#6e6656", "#8e8670", "#aea68e", "#cac4ac", "#e4dec8", "#f8f4e6")
MEMB = ramp("#3a1e10", "#562c16", "#74401e", "#925628", "#ac6e36")
MOLTEN = ramp("#7a1a02", "#c04004", "#f07a10", "#ffb83a", "#fff0a0")
GLASS = ramp("#1a0e08", "#3a1e0c", "#6a3410", "#a85a1a", "#e09030", "#ffd070")
GOLD = ramp("#3a2604", "#5e400a", "#8a6010", "#b8861c", "#e0ac2c", "#fcd860")
# swamp
BOGSKIN = ramp("#0a0c06", "#12160a", "#1c2010", "#262c16", "#32381c", "#404624")
BELLY = ramp("#3a3418", "#544c24", "#6e6430", "#887c3e", "#a2964e")
LURE = ramp("#6a8a10", "#a0c41c", "#d4f03a", "#f4ff86", "#ffffd8")
REED = ramp("#1e2a0c", "#2e3e12", "#40541a", "#546a22", "#6a822c")
FUNGUS = ramp("#2a1c10", "#4a3218", "#6c4a24", "#8e6634", "#b08646")
# jungle
PANTHER = ramp("#050508", "#0a0a10", "#101018", "#171722", "#1f1f2c")
STRIPE = ramp("#0a4a4a", "#0e7a74", "#16b0a0", "#40e4cc", "#b0fff0")
# coast
SEAHIDE = ramp("#0e1418", "#162026", "#202c34", "#2c3a44", "#3a4a56", "#4a5c68")
BARNACLE = ramp("#3a3a34", "#56564c", "#727266", "#8e8e80", "#aaa89a", "#c8c6b8")
KELP = ramp("#0c1a08", "#14280c", "#1e3810", "#2a4a16", "#365c1c")
SEAEYE = ramp("#4a0a06", "#7a1208", "#b0240c", "#e8501a", "#ff9a5a")
# badlands
ROCK = ramp("#1e1610", "#2e2219", "#3e2f23", "#50402f", "#64513c", "#7a644c", "#927a5e")
APESKIN = ramp("#0a0807", "#13100d", "#1d1814", "#28211b", "#342b23")
ORE = ramp("#5a2a10", "#8a4416", "#b8641e", "#e08a30", "#ffc060")
AMBER = ramp("#6a2e04", "#a85008", "#e07c10", "#ffae30", "#ffe090")
CRYSTAL = ramp("#1a2a4a", "#2a4a7a", "#4278b0", "#6aa8dc", "#a8d8f8", "#e8f8ff")
WATER = ramp("#0a2a4a", "#14467a", "#2a6eaa", "#5a9ed4", "#a0d0f4", "#e8f6ff")
PINE = ramp("#06100a", "#0c1a10", "#122616", "#1a321e", "#224026")


# ================================================================ patterns

def strands(p, n, i, j, w, h):
    return -0.18 if i % 3 == 0 else (0.06 if i % 3 == 1 else 0)


def shag(p, n, i, j, w, h):
    """long matted fur: strands that run down and clump"""
    return -0.22 if (i + int(2 * X.fbm(p[0] * 0.4, p[1] * 0.1, p[2] * 0.4))) % 4 == 0 else 0.05


def tiger(p, n, i, j, w, h):
    """dark stripes across the fur, wavering"""
    s = math.sin(p[2] * 0.55 + 1.6 * X.fbm(p[0] * 0.2, p[1] * 0.3, p[2] * 0.2) * 3)
    return -0.42 if s > 0.72 else (0.04 if i % 3 else -0.08)


def scale_rows(p, n, i, j, w, h):
    row = j // 3
    if j % 3 == 2:
        return -0.22
    if (i + (row % 2) * 2) % 4 == 0:
        return -0.12
    return 0.05 if j % 3 == 0 else 0


def warts(p, n, i, j, w, h):
    v = X.fbm(p[0] * 1.3, p[1] * 1.3, p[2] * 1.3)
    return 0.24 if v > 0.74 else (-0.16 if v < 0.24 else 0)


def plates(p, n, i, j, w, h):
    """rock in plates: dark seams between slabs"""
    return -0.3 if (i % 6 == 0 or j % 5 == 0) else 0.04 * ((i // 6 + j // 5) % 2)


def grain(p, n, i, j, w, h):
    return -0.14 if (i + int(3 * X.fbm(p[0] * 0.3, p[1] * 0.3, p[2] * 0.3))) % 3 == 0 else 0


def shaders(**extra):
    base = {
        "dark": X.dark(DARK),
        "mouth": X.dark(GORE),
        "gums": X.surf(GORE, 0.62, 1.0, 0.2, 0.0),
        "bone": X.surf(BONE, 0.56, 1.2, 0.14, 0.1),
        "ivory": X.surf(IVORY, 0.58, 1.3, 0.12, 0.1, pattern=grain),
        "iron": X.surf(IRON, 0.48, 1.4, 0.16, 0.18, rust=(RUST, 0.35, 0.5)),
        "rust": X.surf(RUST, 0.5, 1.3, 0.24, 0.12),
        "wood": X.surf(WOOD, 0.5, 1.1, 0.2, 0.06, stripe=3),
        "rope": X.surf(ROPE, 0.5, 1.0, 0.2, 0.0, stripe=2),
        "stone": X.surf(STONE, 0.5, 1.3, 0.24, 0.1, crust=(MOSS, 0.28)),
        "moss": X.surf(MOSS, 0.5, 1.2, 0.3, 0.0),
    }
    base.update(extra)
    return base


# ================================================================ brushes (no shared bodies: only the strokes)

def leg(k, parent, joints, nm, jn, hip, knee, ankle, w1, w2, mat, foot=None):
    """one leg on the crawler rig: thigh to knee to ankle on its own bone; foot(lg, ankle) draws the end"""
    lg = k.part(nm, hip, (), parent)
    k.limb(lg, hip, knee, w1, mat, "leg")
    k.limb(lg, knee, ankle, w2, mat, "shin")
    if foot:
        foot(lg, ankle)
    joints[nm] = jn
    return lg


def claws(k, part, at, n, spread, L, w=0.9, fwd=(0, -0.35, 1), mat="dark"):
    for t in range(n):
        o = (t - (n - 1) / 2) * spread
        k.shard(part, (at[0] + o, at[1], at[2]), (fwd[0] + o * 0.08, fwd[1], fwd[2]), L, w, mat=mat, tag="claw")


def teeth(k, part, a, b, n, L, down=True, w=0.7, mat="bone"):
    """a row of teeth between two points, pointing down (upper jaw) or up (lower jaw)"""
    for t in range(n):
        f = (t + 0.5) / n
        p = tuple(a[i] + (b[i] - a[i]) * f for i in range(3))
        k.shard(part, p, (0, -1 if down else 1, 0.05), L * (0.7 + 0.3 * X.h3(t, n, 7)), w, mat=mat, tag="tooth")


def eye(k, part, at, w=1.4, h=0.8, mat="eye"):
    k.box(part, C(at[0], at[1], at[2], w, h, 0.5), mat, group="glow", tag="eye")


def reshape(k, part, f=1.0, d=(0, 0, 0)):
    """scale one part's boxes about its pivot by f, then move them (and the pivot) by d: a bigger head, set forward"""
    pv = part.pivot
    for b in k.s.boxes:
        if b.part is part:
            b.lo = tuple(pv[i] + (b.lo[i] - pv[i]) * f + d[i] for i in range(3))
            b.size = tuple(c * f for c in b.size)
            b.pivot = tuple(pv[i] + (b.pivot[i] - pv[i]) * f + d[i] for i in range(3))
    part.pivot = tuple(pv[i] + d[i] for i in range(3))


def glow_tags(k, *tags):
    for b in k.s.boxes:
        if b.tag in tags:
            b.group = "glow"


def drips(k, part, pts, L, w=0.5, mat="sap"):
    for i, p in enumerate(pts):
        f = 0.5 + 0.5 * X.h3(i, 3, 9)
        k.limb(part, p, (p[0], p[1] - L * f, p[2] + 0.2), w, mat, "drip", group="glow")


def spears(k, part, pts, mat_shaft="wood", mat_head="iron", L=10.0, snapped=()):
    """hunters' spears driven in: (base, direction); a snapped one is short and splintered"""
    for i, (base, d) in enumerate(pts):
        n = math.sqrt(sum(c * c for c in d))
        d = tuple(c / n for c in d)
        ln = L * (0.45 if i in snapped else 1.0) * (0.8 + 0.3 * X.h3(i, 4, 2))
        tip = tuple(base[c] + d[c] * ln for c in range(3))
        k.limb(part, tuple(base[c] - d[c] * 1.2 for c in range(3)), tip, 0.7, mat_shaft, "spear")
        k.box(part, C(base[0], base[1] - 0.6, base[2], 1.6, 1.2, 1.6), "gore", tag="wound")
        if i in snapped:
            k.shard(part, tip, d, 1.2, 0.6, mat=mat_shaft, tag="splinter")
        elif i % 2 == 0:
            k.limb(part, tuple(tip[c] - d[c] * 2.6 for c in range(3)), (tip[0] + 0.4, tip[1] - 2.6, tip[2] - 0.6), 1.2, "rag", "rag")


# ================================================================ Thornmaw (forest)

def thornmaw(name="thornmaw", legend=False):
    """The Thornmaw lay down to die in the old wood a long age ago and the wood grew into it, and it got up again.
    A boar-bear the size of a cart, black-brown fur matted with sap; out of its back a thicket of black thorn, long
    as spears, branching; green sap glowing in the wounds the thorns made coming out. Its jaw opens four ways like
    a flower of bone, a tusk on each lower petal, the throat green-lit inside."""
    k = X.Kit(name)
    J = {"body": "Root", "head": "Head", "abdomen": "Stomach"}
    body = k.part("body", (0, 20, 2))
    k.blob(body, (0, 21, 4), (11.5, 10.5, 12), "fur", "chest", step=1.1)
    k.blob(body, (0, 28.5, 1), (10, 6.5, 10), "fur", "hump", step=1.0)
    k.blob(body, (0, 13.6, 4), (8.4, 3.2, 10), "fur_d", "belly_shadow", step=1.0)
    for sx in (-1, 1):
        k.blob(body, (sx * 8.6, 22, 8), (3.6, 7.2, 5.2), "fur", "shoulder", step=1.0)
    ab = k.part("abdomen", (0, 20, -8), (), "body")
    k.blob(ab, (0, 20.5, -12), (10.4, 9.4, 10.4), "fur", "haunch", step=1.1)
    k.blob(ab, (0, 25.4, -10), (8, 4.6, 8), "fur", "rump", step=1.0)
    k.limb(ab, (0, 20, -21), (0, 15, -24), 2.6, "fur", "tail")
    # the thicket: branching thorn out of the hump and the back, leaning back as if wind-blown
    roots = [(0, 34, 2), (-5, 33, -2), (5, 33, -1), (-3, 31, 6), (4, 31, 7), (0, 29, -10), (-6, 28, -12), (6, 28, -13),
             (-8, 30, 3), (8, 30, 2)]
    for i, r in enumerate(roots):
        part = body if r[2] > -6 else ab
        d = ((r[0]) * 0.12 + (X.h3(i, 1, 1) - 0.5) * 0.5, 1, -0.45 - 0.3 * X.h3(i, 1, 2))
        L = (13 if i < 5 else 9) * (0.8 + 0.4 * X.h3(i, 1, 3)) * (1.25 if legend else 1)
        n = math.sqrt(sum(c * c for c in d))
        d = tuple(c / n for c in d)
        mid = tuple(r[c] + d[c] * L * 0.55 for c in range(3))
        k.limb(part, r, mid, 2.0, "thorn", "briar")
        k.shard(part, mid, (d[0] + 0.15, d[1], d[2] - 0.15), L * 0.55, 1.6, mat="thorn", tag="briar")
        for t in range(3):          # thorns off the branch
            f = 0.25 + t * 0.25
            p = tuple(r[c] + d[c] * L * 0.55 * f for c in range(3))
            sd = (math.cos(i * 2.1 + t * 2.4), 0.3, math.sin(i * 2.1 + t * 2.4))
            k.shard(part, p, sd, 2.4 + X.h3(i, t, 4) * 1.6, 0.6, mat="thorn", tag="thorn")
        k.blob(part, (r[0], r[1] - 0.6, r[2]), (1.6, 0.8, 1.6), "sap", "wound", step=0.6)
    drips(k, body, [(-9, 26, 4), (9.5, 25, 2), (-6, 30, -2), (7, 29, 8)], 6, 0.5)
    drips(k, ab, [(-9, 22, -12), (8, 23, -14)], 5, 0.5)
    for sx in (-1, 1):                  # vines hanging off the flanks
        for z in (6, 0, -6):
            k.limb(body if z > -4 else ab, (sx * 10, 27, z), (sx * 11.4, 16, z - 1), 0.6, "moss", "vine")
    # the head: low and heavy, a boar's snout on a bear's skull, the jaw in four petals
    hd = k.part("head", (0, 21, 14), (("x", 8),), "body")
    k.blob(hd, (0, 22, 17), (7.2, 6.2, 6.4), "fur", "skull", step=0.9)
    k.limb(hd, (-6.4, 25.6, 19), (6.4, 25.6, 19), 2.4, "fur_d", "brow", d=3.0)
    k.box(hd, C(0, 18.6, 24, 6.8, 5.4, 6.6), "fur", tag="snout")
    k.box(hd, C(0, 19.2, 27.4, 5.6, 4.0, 1.0), "hide", tag="nose_disc")
    for sx in (-1, 1):
        k.box(hd, C(sx * 1.3, 20.6, 27.95, 1.2, 1.4, 0.3), "dark", tag="nostril")
        eye(k, hd, (sx * 3.3, 23.6, 22.9), 1.6, 0.8)
        eye(k, hd, (sx * 4.5, 22.0, 22.1), 1.0, 0.6)
        k.shard(hd, (sx * 5.4, 27, 15), (sx * 0.4, 0.8, -0.6), 4.2, 2.2, mat="fur", tag="ear")
        # the four petals of the jaw: two upper at the sides of the snout, two lower opening down and out
        k.limb(hd, (sx * 3.6, 18.8, 21), (sx * 7.2, 15.4, 27.4), 3.0, "bone", "petal_up", d=2.0)
        teeth(k, hd, (sx * 4.2, 17.6, 22), (sx * 6.8, 14.6, 27), 4, 1.8, down=True)
        k.limb(hd, (sx * 2.8, 15.0, 19), (sx * 5.6, 9.6, 25.2), 3.4, "bone", "petal_low", d=2.4)
        teeth(k, hd, (sx * 3.2, 12.4, 21), (sx * 5.2, 9.8, 25), 4, 1.6, down=False)
        k.shard(hd, (sx * 5.4, 11.0, 24.8), (sx * 0.35, 1, 0.5), 7.5 if not legend else 9.5, 1.8, mat="ivory", tag="tusk")
    k.blob(hd, (0, 15.4, 21), (3.6, 2.8, 3.6), "mouth", "throat", step=0.7)
    k.blob(hd, (0, 15.2, 20.6), (2.0, 1.6, 2.4), "sap", "throat_glow", step=0.6)
    k.limb(hd, (0, 14, 22), (0, 10.6, 25), 1.2, "gums", "tongue")
    # four legs: thick, bear-pawed, black claws
    def paw(lg, a):
        k.box(lg, C(a[0], 0, a[2] + 1.0, 5.4, 2.6, 6.4), "fur_d", tag="foot")
        claws(k, lg, (a[0], 0.8, a[2] + 4.0), 4, 1.3, 2.6, 0.8)
    for side, s in ((1, "l"), (-1, "r")):
        leg(k, body, J, "leg_%s0" % s, ("LL" if side > 0 else "RL") + "1", (side * 7.2, 18, 8), (side * 7.8, 9, 9.4),
            (side * 7.6, 1.6, 9), 6.2, 4.6, "fur", paw)
        leg(k, ab, J, "leg_%s1" % s, ("LL" if side > 0 else "RL") + "4", (side * 7.0, 18, -13), (side * 7.6, 9, -15.6),
            (side * 7.4, 1.6, -13.4), 6.4, 4.4, "fur", paw)
    if legend:
        # Old Blackbriar: a shrine of the old wood grown up into its back - two pillars, a broken lintel, a bell
        sh = k.part("shrine", (0, 33, -2), (), body, bone=False)
        for sx in (-1, 1):
            k.box(sh, C(sx * 4.6, 31, -2, 2.6, 11 - (sx + 1) * 1.6, 2.6), "stone", tag="pillar")
            k.box(sh, C(sx * 4.6, 31, -2, 3.4, 1.2, 3.4), "stone", tag="pillar_base")
        k.box(sh, C(-1.0, 41.4, -2, 11.8, 1.8, 3.4), "stone", tag="lintel")
        k.box(sh, C(5.4, 38.0, -2, 4.0, 1.6, 3.0), "stone", tag="lintel_fallen")
        k.limb(sh, (-1, 41.4, -2), (-1, 39.0, -2), 0.3, "rope", "bell_rope")
        k.blob(sh, (-1, 37.4, -2), (1.6, 1.8, 1.6), "rust", "bell", step=0.6)
        k.blob(sh, (0, 32.6, 3.4), (2.2, 2.6, 1.6), "stone", "idol", step=0.7)
        for sx in (-1, 1):
            k.box(sh, C(sx * 0.9, 33.4, 4.9, 0.8, 0.6, 0.3), "sap", group="glow", tag="idol_eye")
        k.blob(sh, (0, 31.6, -2), (7, 1.4, 5), "moss", "shrine_moss", step=0.7)
        k.cluster(body, (0, 31, 8), 5, 9, 1.4, mat="thorn", seed=11, spread=0.8, up=(0, 1, 0.4))
        k.cluster(ab, (0, 28, -16), 5, 8, 1.4, mat="thorn", seed=13, spread=0.8, up=(0, 1, -0.7))
        for sx in (-1, 1):
            k.limb(body, (sx * 8, 14, 10), (sx * 11, 0.6, 14), 1.0, "thorn", "root_trail")
            k.limb(ab, (sx * 8, 14, -14), (sx * 11, 0.6, -20), 1.0, "thorn", "root_trail")
        drips(k, body, [(-3, 31, 6), (4, 31, 7), (0, 33, 2)], 7, 0.6)
        grow(k, 1.35)
    glow_tags(k, "wound", "throat_glow", "eye")
    k.s.shaders = shaders(
        fur=X.surf(THORNFUR, 0.5, 1.2, 0.22, 0.03, crust=(MOSS, 0.2), pattern=shag),
        fur_d=X.surf(THORNFUR, 0.3, 1.0, 0.2, 0.0, pattern=shag),
        hide=X.wrinkled(HIDE, 1.2),
        thorn=X.surf(THORN, 0.5, 1.3, 0.2, 0.12, pattern=grain),
        sap=X.glow(SAP), eye=X.glow(SAP, 0.8, 0.16), gore=X.glow(SAP, 0.4, 0.3),
    )
    return k.s, k.parts, J


# ================================================================ Gorehorn (plains)

def gorehorn(name="gorehorn", legend=False):
    """The herds of the long grass walk round the Gorehorn. A bison's mountain of a shoulder on a rhino's armoured
    hindquarters, the shag of its mane hanging to its knees; bone grown out of it in plates over the shoulders and
    down the spine; a crown of six horns - two great ones sweeping forward, two up off the brow, two on the nose.
    The spears of every party that tried it are still in it."""
    k = X.Kit(name)
    J = {"body": "Root", "head": "Head", "abdomen": "Stomach"}
    body = k.part("body", (0, 22, 2))
    k.blob(body, (0, 22.6, 6), (9.8, 11.4, 9.8), "mane", "chest", step=1.1)
    k.blob(body, (0, 35, 6), (7.6, 8.4, 6.6), "mane", "hump", step=1.0)       # the bison's hump, over the shoulders
    k.blob(body, (0, 27, -3), (7.6, 6.0, 8.0), "mane", "back", step=1.0)
    k.blob(body, (0, 23, 15.4), (7.2, 8.0, 5.0), "mane", "neck", step=1.0)     # the neck: thick, shagged, into the skull
    k.blob(body, (0, 17, 15), (4.6, 4.4, 4.0), "mane", "dewlap", step=0.9)
    for sx in (-1, 1):
        k.blob(body, (sx * 7.6, 19, 9), (3.6, 7.6, 4.8), "mane", "shoulder_shag", step=1.0)
        for z in (11, 7, 3):         # shag hanging toward the knees
            k.shard(body, (sx * 9.0, 15, z), (sx * 0.1, -1, 0.1), 5.6, 2.4, mat="mane", tag="shag")
    ab = k.part("abdomen", (0, 22, -7), (), "body")
    k.blob(ab, (0, 21.5, -11), (7.4, 7.6, 8.8), "hide", "haunch", step=1.1)
    k.limb(ab, (0, 26, -20), (0, 17, -23), 1.4, "hide", "tail")
    k.blob(ab, (0, 16, -23.4), (1.4, 2.4, 1.4), "mane", "tail_tuft", step=0.7)
    # bone plates: a ridge of overlapping slabs from the hump down the spine, each with a spike
    for i, (y, z, w) in enumerate(((42.6, 9, 7), (43, 5, 8), (40.4, 1, 8), (35.6, -3, 7.6), (32.6, -7, 7))):
        k.box(body, C(0, y - 1.4, z, w, 2.0, 4.4), "plate", tag="plate")
        k.box(body, C(0, y + 0.4, z - 0.4, w - 3.0, 1.2, 3.4), "plate", tag="plate_ridge")
        k.shard(body, (0, y + 1.4, z), (0, 1, -0.5), 5.0 - i * 0.6, 2.2, mat="horn", tag="plate_spike")
    for sx in (-1, 1):               # shoulder plates: three bony lames stepping down, spiked
        for t in range(3):
            k.box(body, C(sx * (8.6 + t * 0.9), 31 - t * 3.2, 7 - t * 0.4, 3.2, 2.6, 8.4 - t), "plate", tag="shoulder_plate")
        k.shard(body, (sx * 9.6, 33, 7), (sx * 0.8, 0.8, -0.2), 4.2, 1.8, mat="horn", tag="plate_spike")
    for i, z in enumerate((-12, -16, -20)):
        k.box(ab, C(0, 27.6 - i * 0.8, z, 7 - i, 1.8, 3.6), "plate", tag="plate")
        k.shard(ab, (0, 29.2 - i * 0.8, z), (0, 1, -0.5), 3.0, 1.4, mat="horn", tag="plate_spike")
    spears(k, body, [((-9.6, 27, 2), (-1, 0.5, -0.6)), ((9.4, 25, 6), (1, 0.6, -0.3)), ((-5, 36, -1), (-0.6, 1, -0.7)),
                     ((9.6, 29, -2), (1, 0.3, -0.7))], snapped=(1,), L=14.0)
    spears(k, ab, [((-8.6, 24, -12), (-1, 0.5, -0.4)), ((8.2, 22, -15), (1, 0.6, -0.8)), ((3, 29, -12), (0.4, 1, -0.6))],
           snapped=(0,), L=13.0)
    # the head: low and forward under the hump, the crown of horns
    hd = k.part("head", (0, 22, 15), (("x", 6),), "body")
    k.blob(hd, (0, 22, 21), (6.4, 6.2, 5.4), "mane", "skull", step=0.9)
    k.blob(hd, (0, 27, 20), (5.8, 3.4, 4.2), "mane", "forelock", step=0.8)
    k.box(hd, C(0, 15.6, 26.0, 7.4, 6.6, 6.0), "hide", tag="muzzle")
    k.box(hd, C(0, 15.0, 29.0, 6.0, 4.6, 0.8), "dark", tag="nose")
    k.box(hd, C(0, 11.4, 23.4, 5.6, 3.6, 6.2), "mane", tag="beard")
    for sx in (-1, 1):
        k.box(hd, C(sx * 1.6, 16.8, 29.45, 1.4, 1.6, 0.3), "mouth", tag="nostril")
        eye(k, hd, (sx * 4.0, 21.4, 25.2), 1.4, 0.7)
        k.limb(hd, (sx * 2.6, 22.8, 25.6), (sx * 5.4, 22.2, 24.8), 1.0, "dark", "brow")
        # the two great horns: thick at the root, out wide, then up and forward like a bull's but heavier
        hb = (sx * 5.0, 25, 20)
        h1 = (sx * 13.0, 25.0, 20.6)
        h2 = (sx * 17.4, 29.6, 23.4)
        k.limb(hd, hb, h1, 4.4, "horn", "horn", d=4.0)
        k.limb(hd, h1, h2, 3.6, "horn", "horn", d=3.4)
        k.shard(hd, h2, (sx * 0.1, 0.8, 1), 9.0 if not legend else 11.0, 3.2, mat="horn_tip", tag="horn")
        for t in range(4):           # ridged rings on the horn
            f = 0.2 + t * 0.2
            c = tuple(hb[i] + (h1[i] - hb[i]) * f for i in range(3))
            k.box(hd, C(c[0], c[1] - 2.4, c[2], 1.0, 4.8, 4.6), "dark", tag="horn_ring")
        k.shard(hd, (sx * 2.8, 27.8, 21.4), (sx * 0.35, 1, 0.3), 7.0, 2.0, mat="horn_tip", tag="brow_horn")
        k.blob(hd, (sx * 5.4, 24.8, 20), (2.4, 2.4, 2.4), "horn", "horn_boss", step=0.6)
    k.shard(hd, (0, 21.6, 27.6), (0, 1, 0.7), 9.6, 3.4, mat="horn_tip", tag="nose_horn")
    k.shard(hd, (0, 22.6, 24.8), (0, 1, 0.3), 5.0, 2.2, mat="horn", tag="nose_horn")
    # legs: pillar-thick, cloven black hooves
    def hoof(lg, a):
        k.box(lg, C(a[0], 0, a[2] + 0.3, 5.0, 3.0, 5.4), "horn", tag="foot")
        k.box(lg, C(a[0], 0, a[2] + 2.6, 0.5, 2.4, 0.4), "dark", tag="cleft")
        k.box(lg, C(a[0], 2.8, a[2] + 0.3, 5.6, 1.6, 6.0), "mane", tag="fetlock")
    for side, s in ((1, "l"), (-1, "r")):
        leg(k, body, J, "leg_%s0" % s, ("LL" if side > 0 else "RL") + "1", (side * 6.6, 18, 8), (side * 7.0, 9.4, 8.6),
            (side * 6.8, 2.6, 8.2), 6.0, 4.4, "mane", hoof)
        leg(k, ab, J, "leg_%s1" % s, ("LL" if side > 0 else "RL") + "4", (side * 6.2, 18, -13), (side * 6.6, 9.4, -15.4),
            (side * 6.4, 2.6, -13.2), 5.8, 4.0, "hide", hoof)
    if legend:
        # the Red Plough: red to the horns with the blood of the farm, the chain round its neck and the plough behind
        for b in k.s.boxes:
            if b.tag in ("horn", "nose_horn") and b.mat == "horn_tip":
                b.mat = "blood"
        k.ring(body, 0, 27, 10.6, 9.6, 1.4, "iron", "neck_chain", n=18, axis="z")
        pl = k.part("plough", (0, 18, -24), (), ab, bone=False)
        k.chain(ab, (-7, 23, -2), (-5, 8, -30), 9, "iron", "drag_chain", w=1.4)
        k.chain(ab, (7, 23, -2), (5, 8, -30), 9, "iron", "drag_chain", w=1.4)
        k.limb(pl, (-5, 8, -30), (5, 8, -30), 1.6, "wood", "plough_beam")
        k.limb(pl, (0, 8, -30), (0, 4, -40), 1.8, "wood", "plough_beam")
        k.limb(pl, (0, 6, -36), (0, 0.6, -33), 2.6, "rust", "share", d=0.8)
        k.shard(pl, (0, 0.8, -33), (0, -0.2, 1), 3.6, 2.4, mat="iron", tag="share_tip")
        for sx in (-1, 1):
            k.limb(pl, (0, 5, -38), (sx * 4, 9, -44), 1.2, "wood", "handle")
        k.limb(pl, (-3, 14, -26), (3, 22, -18), 1.2, "wood", "fence_post")   # a fence post through the hide
        for b in k.s.boxes:
            if b.tag in ("wound", "rag"):
                b.mat = "blood"
        k.blob(body, (0, 24, 12), (9, 3, 3), "blood", "blood_breast", step=0.8)
        grow(k, 1.4)
    glow_tags(k, "eye")
    k.s.shaders = shaders(
        mane=X.surf(MANE, 0.5, 1.2, 0.24, 0.02, pattern=shag),
        hide=X.wrinkled(HIDE, 1.1),
        plate=X.surf(BONE, 0.5, 1.3, 0.2, 0.14, pattern=plates),
        horn=X.surf(HORN, 0.5, 1.4, 0.14, 0.14, pattern=grain),
        horn_tip=X.surf(BONE, 0.56, 1.4, 0.1, 0.12, pattern=grain),
        blood=X.surf(BLOOD, 0.5, 1.4, 0.2, 0.1),
        rag=X.surf(BLOOD, 0.55, 1.0, 0.2, 0.0, holes=True),
        gore=X.surf(GORE, 0.5, 1.0, 0.2, 0.0),
        eye=X.glow(EMBER, 0.75, 0.2),
    )
    return k.s, k.parts, J


# ================================================================ Frostjaw (snow)

def frostjaw(name="frostjaw", legend=False):
    """The Frostjaw hunts the passes when the snow comes down so hard the tracks fill behind it. A sabre-tooth the
    size of a horse, long in the back and high in the shoulder, white fur barred with slate; a mane of frost round
    its neck, clear ice grown down its spine in plates; and the sabres - ice, not bone - hanging from its upper jaw
    down past its chin, the cold breathing out between them."""
    k = X.Kit(name)
    J = {"body": "Root", "head": "Head", "abdomen": "Stomach"}
    body = k.part("body", (0, 19, 3))
    k.blob(body, (0, 21, 5), (8.6, 8.8, 10.4), "fur", "chest", step=1.0)
    k.blob(body, (0, 14.6, 5), (6.4, 2.8, 8.6), "fur_w", "belly", step=0.9)
    for sx in (-1, 1):
        k.blob(body, (sx * 6.6, 23, 9), (2.8, 5.0, 4.0), "fur", "shoulder_blade", step=0.8)
    k.blob(body, (0, 25, 11), (8.0, 6.4, 5.0), "frost", "mane", step=0.8)       # the frost mane
    for i in range(10):
        a = i * 2 * math.pi / 10
        k.shard(body, (math.cos(a) * 7, 24 + math.sin(a) * 5.4, 11), (math.cos(a), math.sin(a) + 0.2, -0.6), 4.0, 1.4,
                mat="frost", tag="mane_spike")
    ab = k.part("abdomen", (0, 19, -7), (), "body")
    k.blob(ab, (0, 19.4, -12), (7.6, 7.4, 9.4), "fur", "haunch", step=1.0)
    tail = [(0, 21, -20), (0, 19, -26), (0, 15, -31), (0, 13, -36), (0, 14, -40)]
    for (a, b), w in zip(zip(tail, tail[1:]), (3.2, 2.8, 2.4, 2.0)):
        k.limb(ab, a, b, w, "fur", "tail")
    k.cluster(ab, (0, 14, -40), 3, 3.4, 1.2, mat="ice", seed=5, spread=0.6, up=(0, 0.3, -1))
    # ice plates down the spine: clear, flat, overlapping, leaning back
    for i, z in enumerate((10, 6, 2, -2)):
        k.shard(body, (0, 29 - abs(z - 4) * 0.2, z), (0, 1, -0.5), 6.0 - i * 0.6, 3.0, mat="ice", tag="ice_plate")
        k.shard(body, (0, 28.4, z - 1.4), (0, 1, -0.7), 3.0, 1.6, mat="ice", tag="ice_plate")
    for i, z in enumerate((-8, -12, -16)):
        k.shard(ab, (0, 26.4 - i, z), (0, 1, -0.6), 4.4 - i * 0.6, 2.4, mat="ice", tag="ice_plate")
    # the head: broad, short-faced, the sabres
    hd = k.part("head", (0, 23, 14), (("x", 14),), "body")
    k.blob(hd, (0, 24, 17.4), (5.4, 4.6, 5.0), "fur", "skull", step=0.8)
    k.box(hd, C(0, 21.4, 21.6, 5.4, 4.2, 4.2), "fur_w", tag="muzzle")
    k.box(hd, C(0, 24.2, 23.4, 2.4, 1.6, 0.6), "dark", tag="nose")
    k.limb(hd, (-4.6, 27.0, 20.4), (4.6, 27.0, 20.4), 1.6, "fur", "brow", d=2.4)
    for sx in (-1, 1):
        eye(k, hd, (sx * 2.6, 25.8, 21.55), 1.6, 0.8)
        k.shard(hd, (sx * 4.0, 28.0, 15.6), (sx * 0.5, 0.8, -0.8), 3.4, 2.0, mat="fur", tag="ear")
        k.blob(hd, (sx * 4.8, 22.4, 17.6), (1.6, 2.8, 2.6), "fur_w", "cheek_ruff", step=0.6)
        # the sabres: from the upper jaw down past the chin, curving back a little
        s0 = (sx * 1.9, 21.6, 22.8)
        s1 = (sx * 2.2, 15.6, 23.4)
        k.limb(hd, s0, s1, 1.6, "ice", "sabre", d=1.0)
        k.shard(hd, s1, (0, -1, -0.25), 5.4 if not legend else 6.8, 1.4, mat="ice", tag="sabre")
    k.limb(hd, (0, 20.2, 18.6), (0, 14.6, 22.6), 3.6, "fur_w", "jaw", d=3.2)
    k.limb(hd, (0, 20.8, 19.0), (0, 16.6, 22.8), 3.0, "mouth", "mouth", d=2.6)
    teeth(k, hd, (-1.2, 16.0, 22.6), (1.2, 16.0, 22.6), 3, 1.0, down=False)
    k.blob(hd, (0, 18.4, 21.8), (1.4, 1.0, 1.6), "breath", "frost_breath", step=0.5)
    k.box(hd, C(0, 21.0, 25.6, 4.4, 3.0, 3.6), "fur_w", tag="muzzle")
    k.box(hd, C(0, 23.4, 27.2, 2.4, 1.4, 0.6), "dark", tag="nose")
    reshape(k, hd, 1.3, (0, -1.6, 0.6))
    k.blob(body, (0, 21.6, 14.6), (5.0, 5.2, 3.6), "fur", "neck", step=0.8)
    def paw(lg, a):
        k.box(lg, C(a[0], 0, a[2] + 1.0, 5.6, 2.4, 6.2), "fur_w", tag="foot")
        claws(k, lg, (a[0], 0.6, a[2] + 3.6), 4, 1.1, 2.0, 0.7, mat="ice")
    for side, s in ((1, "l"), (-1, "r")):
        leg(k, body, J, "leg_%s0" % s, ("LL" if side > 0 else "RL") + "1", (side * 5.6, 16, 8), (side * 6.0, 8, 10),
            (side * 5.8, 1.4, 9), 5.8, 4.2, "fur", paw)
        leg(k, ab, J, "leg_%s1" % s, ("LL" if side > 0 else "RL") + "4", (side * 5.6, 17, -13), (side * 6.0, 9, -17),
            (side * 5.8, 1.4, -14), 6.4, 4.0, "fur", paw)
    if legend:
        # the Pale Widow: a second, lower pair of tusks up from the jaw; old blue ice; a frozen elk on her back
        for sx in (-1, 1):
            k.shard(hd, (sx * 1.6, 15.2, 22.4), (sx * 0.2, 1, 0.5), 3.4, 1.0, mat="oldice", tag="low_tusk")
        for b in k.s.boxes:
            if b.mat == "ice" and b.tag in ("ice_plate", "mane_spike"):
                b.mat = "oldice"
        el = k.part("elk", (0, 30, -4), (), body, bone=False)
        k.cluster(el, (0, 28, -2), 7, 7, 2.4, mat="oldice", seed=33, spread=1.0, up=(0, 1, 0))
        k.cluster(el, (0, 28, -7), 6, 6, 2.2, mat="oldice", seed=35, spread=1.0, up=(0, 1, -0.3))
        k.box(el, C(0, 27.6, -4, 8, 1.4, 10), "oldice", tag="ice_crust")
        k.blob(el, (0, 30, -4), (3.4, 2.4, 4.4), "elk", "elk_body", step=0.7)
        k.box(el, C(-4.0, 30.4, 1.8, 3.0, 2.6, 3.4), "elk", tag="elk_head")
        for t, (dx, dz) in enumerate(((-1, 0.5), (-0.6, 1), (0.2, 0.8))):
            k.shard(el, (-4.6, 32.6, 2.0), (dx, 1, dz * 0.3), 4.6 - t * 0.6, 0.7, mat="bone", tag="antler")
            k.shard(el, (-3.0, 32.6, 2.0), (-dx * 0.4 + 0.6, 1, dz * 0.3), 4.2 - t * 0.6, 0.7, mat="bone", tag="antler")
        for sx in (-1, 1):
            k.limb(el, (sx * 1.6, 28, -6), (sx * 3.4, 24, -9), 0.8, "elk", "elk_leg")
        k.cluster(body, (0, 28, 6), 5, 7, 2.0, mat="oldice", seed=21, spread=0.7, up=(0, 1, -0.3))
        grow(k, 1.3)
    glow_tags(k, "eye", "frost_breath")
    k.s.shaders = shaders(
        fur=X.surf(SNOWFUR, 0.56, 1.2, 0.18, 0.02, pattern=tiger),
        fur_w=X.surf(SNOWFUR, 0.66, 1.1, 0.16, 0.0, pattern=strands),
        frost=X.surf(SNOWFUR, 0.74, 1.0, 0.14, 0.0, pattern=shag),
        ice=X.facets(ICEL), oldice=X.facets(OLDICE),
        breath=X.glow(ICE), eye=X.glow(ICE, 0.8, 0.16),
        elk=X.surf(ELK, 0.4, 1.0, 0.2, 0.0, crust=(SNOWFUR, 0.4)),
    )
    return k.s, k.parts, J


# ================================================================ Sun Basilisk (desert)

def sun_basilisk(name="sun_basilisk", legend=False):
    """It lies under the dunes in the heat of the day with only its frill above the sand, like the bones of
    something long dead, and the sand pours off it when it rises. A long, low lizard, sprawled on its legs, its
    scales the colours of the dunes; round its neck a frill of sun-bleached bone spines with hide stretched
    between; its eyes molten glass - the gaze that slows a man's blood."""
    k = X.Kit(name)
    J = {"body": "Root", "head": "Head", "abdomen": "Stomach"}
    body = k.part("body", (0, 10, 2))
    k.blob(body, (0, 11, 3), (7.4, 4.6, 11), "scale", "chest", step=0.8)
    k.blob(body, (0, 7.4, 3), (5.6, 1.6, 9), "belly", "belly", step=0.6)
    ab = k.part("abdomen", (0, 10, -8), (), "body")
    k.blob(ab, (0, 10.6, -12), (6.8, 4.4, 9.4), "scale", "haunch", step=0.8)
    tail = [(0, 11, -20), (1.6, 10, -28), (3.6, 8, -35), (3.0, 6, -42), (0.4, 4.4, -48), (-2, 3.4, -52)]
    for i, ((a, b), w) in enumerate(zip(zip(tail, tail[1:]), (5.4, 4.6, 3.8, 3.0, 2.0))):
        k.limb(ab, a, b, w, "scale", "tail", d=w * 0.8)
        k.shard(ab, (a[0], a[1] + w * 0.4, a[2]), (0, 1, -0.6), 2.0 - i * 0.3, 1.0, mat="bone", tag="scute")
    for z in (12, 8, 4, 0, -4):          # bony scutes along the back
        k.shard(body, (0, 15.2, z), (0, 1, -0.5), 2.6, 1.4, mat="bone", tag="scute")
        for sx in (-1, 1):
            k.box(body, C(sx * 3.4, 14.4, z, 1.6, 0.8, 2.0), "bone", tag="scute_side")
    for z in (-8, -12, -16):
        k.shard(ab, (0, 14.6, z), (0, 1, -0.5), 2.2, 1.2, mat="bone", tag="scute")
    # sand pouring off it
    for i, (x, z) in enumerate(((-6, 8), (6.4, 4), (-5.6, -2), (6, -10), (-6, -14), (2, -18), (-3, 10))):
        part = body if z > -6 else ab
        k.limb(part, (x, 12 - abs(x) * 0.2, z), (x * 1.08, 2 + X.h3(i, 2, 2) * 3, z + 0.6), 0.9, "sand", "sand_fall")
    # the head: a wedge with horned brows, the frill behind it
    hd = k.part("head", (0, 12, 14), (("x", -6),), "body")
    k.blob(hd, (0, 12.8, 18), (4.6, 3.4, 5.4), "scale", "skull", step=0.7)
    k.box(hd, C(0, 10.0, 24, 5.6, 3.2, 7.4), "scale", tag="snout")
    k.box(hd, C(0, 8.0, 23.4, 5.0, 2.0, 7.0), "belly", tag="jaw")
    k.box(hd, C(0, 9.6, 24, 5.8, 0.6, 7.6), "mouth", tag="lip_line")
    teeth(k, hd, (-2.6, 9.8, 21), (-2.6, 9.8, 27.2), 4, 1.0, down=True, w=0.5)
    teeth(k, hd, (2.6, 9.8, 21), (2.6, 9.8, 27.2), 4, 1.0, down=True, w=0.5)
    for sx in (-1, 1):
        k.box(hd, C(sx * 3.6, 14.2, 21, 2.6, 2.0, 2.8), "glassrim", tag="socket")
        eye(k, hd, (sx * 3.6, 14.4, 22.45), 2.2, 1.6)
        k.box(hd, C(sx * 4.95, 14.4, 21.0, 0.4, 1.6, 2.2), "eye", group="glow", tag="eye")
        k.shard(hd, (sx * 3.4, 16.4, 19.4), (sx * 0.4, 0.7, -1), 4.6, 1.4, mat="bone", tag="brow_horn")
        k.box(hd, C(sx * 1.2, 11.6, 27.75, 0.8, 0.6, 0.3), "dark", tag="nostril")
    # the frill: bone spines in a fan, hide between in panels
    fr = k.part("frill", (0, 14, 14), (), hd, bone=False)
    n = 11
    tips = []
    for i in range(n):
        a = math.pi * (0.05 + 0.9 * i / (n - 1))
        L = (12.0 if not legend else 14.0) * (0.75 + 0.25 * math.sin(a))
        d = (math.cos(a), math.sin(a) * 0.9 + 0.1, -0.35)
        tip = (d[0] * L, 13 + d[1] * L, 14 + d[2] * L)
        tips.append(tip)
        k.limb(fr, (d[0] * 2.4, 13 + d[1] * 2.4, 14), tip, 1.2, "sunbone", "frill_spine")
        k.shard(fr, tip, d, 2.4, 0.9, mat="sunbone", tag="frill_tip")
    for i in range(n - 1):              # the membrane: stepped panels between neighbouring spines
        for f in (0.3, 0.55, 0.8):
            a = tuple(tips[i][c] * f + (0, 13, 14)[c] * (1 - f) for c in range(3))
            b = tuple(tips[i + 1][c] * f + (0, 13, 14)[c] * (1 - f) for c in range(3))
            k.limb(fr, a, b, 2.6 * f + 0.6, "memb", "frill_skin", d=0.5)
    def foot(lg, a):
        k.box(lg, C(a[0], 0, a[2] + 0.6, 4.0, 1.4, 4.4), "scale", tag="foot")
        claws(k, lg, (a[0], 0.4, a[2] + 2.8), 4, 1.0, 2.0, 0.6, mat="bone")
    for side, s in ((1, "l"), (-1, "r")):   # sprawled: the knees out to the side
        leg(k, body, J, "leg_%s0" % s, ("LL" if side > 0 else "RL") + "1", (side * 5.6, 10, 8), (side * 11.4, 8, 9.4),
            (side * 11.0, 1.0, 11), 3.8, 3.0, "scale", foot)
        leg(k, ab, J, "leg_%s1" % s, ("LL" if side > 0 else "RL") + "4", (side * 5.6, 10, -13), (side * 12.0, 8.4, -14),
            (side * 11.6, 1.0, -16), 4.2, 3.2, "scale", foot)
    if legend:
        # Sunbreaker: a ruined temple's sun-disc fused into the frill, cracked; glass grown down its back
        sd = k.part("sun_disc", (0, 22, 9), (), hd, bone=False)
        for r in range(6, 0, -1):
            k.ring(sd, 0, 21, 8.4, r * 1.2, 1.4, "gold" if r % 2 else "bronze", "disc", n=8 + r * 2, axis="z")
        k.box(sd, C(0, 19.2, 8.0, 3.6, 3.6, 1.2), "molten", group="glow", tag="disc_heart")
        for i in range(12):
            a = i * math.pi / 6
            k.shard(sd, (math.cos(a) * 7.4, 21 + math.sin(a) * 7.4, 8.4), (math.cos(a), math.sin(a), 0), 3.6, 1.2,
                    mat="gold", tag="disc_ray")
        k.limb(sd, (-2, 27, 8.6), (3, 16, 8.6), 0.6, "dark", "disc_crack")
        for z in (10, 4, -2):
            k.cluster(body, (0, 15, z), 3, 5, 1.4, mat="glass", seed=int(z) + 40, spread=0.6, up=(0, 1, -0.4))
        for z in (-10, -16):
            k.cluster(ab, (0, 14, z), 3, 4, 1.2, mat="glass", seed=int(z) + 60, spread=0.6, up=(0, 1, -0.5))
        grow(k, 1.35)
    glow_tags(k, "eye")
    k.s.shaders = shaders(
        scale=X.surf(SANDSCALE, 0.54, 1.3, 0.16, 0.0, pattern=scale_rows, drip=(SAND, 0.25)),
        belly=X.surf(SAND, 0.5, 1.0, 0.14, 0.0, stripe=2),
        sand=X.surf(SAND, 0.6, 0.8, 0.3, 0.0),
        sunbone=X.surf(SUNBONE, 0.58, 1.3, 0.12, 0.1, pattern=grain),
        memb=X.surf(MEMB, 0.5, 1.0, 0.2, 0.0, holes=True),
        glassrim=X.surf(GLASS, 0.3, 1.0, 0.1, 0.0),
        glass=X.facets(GLASS), molten=X.glow(MOLTEN),
        gold=X.surf(GOLD, 0.56, 1.4, 0.12, 0.2), bronze=X.surf(RUST, 0.56, 1.3, 0.12, 0.16),
        eye=X.glow(MOLTEN, 0.7, 0.28),
    )
    return k.s, k.parts, J


# ================================================================ Bogmaw (swamp)

def bogmaw(name="bogmaw", legend=False):
    """In the black water of the fens a little light bobs over the reeds and people follow it. Under the light is
    the Bogmaw: a toad as broad as a cart, a crocodile's ridged back and tail, warted olive hide gone grey with
    barnacled fungus, and a mouth that opens wider than all of it. The light is the lure on the stalk that grows
    from its brow."""
    k = X.Kit(name)
    J = {"body": "Root", "head": "Head", "abdomen": "Stomach"}
    body = k.part("body", (0, 11, 0))
    k.blob(body, (0, 12, 2), (11.6, 6.6, 10.4), "skin", "chest", step=0.9)
    k.blob(body, (0, 7.6, 3), (10, 2.4, 9), "belly", "belly", step=0.7)
    ab = k.part("abdomen", (0, 11, -7), (), "body")
    k.blob(ab, (0, 12, -10), (11, 6.4, 9.0), "skin", "haunch", step=0.9)
    tail = [(0, 12, -17), (0, 10, -24), (0, 7, -30), (0, 4.4, -34)]
    for i, ((a, b), w) in enumerate(zip(zip(tail, tail[1:]), (6.0, 4.6, 3.0))):
        k.limb(ab, a, b, w, "skin", "tail", d=w * 0.7)
        for sx in (-1, 1):
            k.shard(ab, (sx * w * 0.3, a[1] + w * 0.4, a[2]), (sx * 0.2, 1, -0.4), 1.8, 1.0, mat="osteo", tag="ridge")
    for z in (10, 6, 2, -2):             # crocodile osteoderm rows down the back
        for sx in (-1, 0, 1):
            k.box(body, C(sx * 3.4, 18.2 - abs(sx) * 0.6, z, 2.2, 1.2, 2.6), "osteo", tag="osteoderm")
            k.shard(body, (sx * 3.4, 19.2 - abs(sx) * 0.6, z), (0, 1, -0.3), 1.6, 1.0, mat="osteo", tag="ridge")
    for z in (-8, -12, -16):
        for sx in (-1, 1):
            k.box(ab, C(sx * 2.6, 17.6, z, 2.0, 1.0, 2.4), "osteo", tag="osteoderm")
    for i, (x, y, z) in enumerate(((-8, 15, 4), (7, 16, -2), (-5, 16, -10), (8, 14, -12), (2, 18, 6))):
        part = body if z > -6 else ab                    # bracket fungus and barnacle crusts
        k.box(part, C(x, y, z, 3.4, 0.8, 2.6), "fungus", tag="fungus")
        k.box(part, C(x + 0.4, y + 0.8, z, 2.4, 0.6, 2.0), "fungus", tag="fungus")
    for sx in (-1, 1):                   # weed hanging off the flanks
        for z in (6, 0, -6, -12):
            k.limb(body if z > -6 else ab, (sx * 11, 13, z), (sx * 12, 5, z - 1), 0.7, "reed", "weed")
    # the head: as wide as the body, flat, the mouth half open on a pit of teeth
    hd = k.part("head", (0, 13, 10), (("x", -4),), "body")
    k.box(hd, C(0, 13.6, 17, 22, 4.4, 15), "skin", tag="upper_jaw")
    k.blob(hd, (0, 18.0, 15), (9.4, 1.8, 6.4), "skin", "head_top", step=0.6)
    k.box(hd, C(0, 4.4, 17, 21, 3.4, 14.4), "skin", tag="lower_jaw")
    k.box(hd, C(0, 3.8, 17, 18, 1.4, 13), "belly", tag="throat_pouch")
    k.box(hd, C(0, 7.6, 16.6, 19.4, 6.2, 13), "mouth", tag="maw")
    k.box(hd, C(0, 7.4, 14, 12, 2.0, 8), "gums", tag="tongue")
    for sx in (-1, 1):
        teeth(k, hd, (sx * 10.2, 13.6, 11), (sx * 10.2, 13.6, 23.6), 6, 2.4, down=True, w=0.8)
        teeth(k, hd, (sx * 9.6, 7.8, 11), (sx * 9.6, 7.8, 23.2), 5, 1.8, down=False, w=0.8)
        k.blob(hd, (sx * 6.4, 19.4, 13), (2.6, 2.4, 2.6), "skin", "eye_mound", step=0.6)
        k.box(hd, C(sx * 6.4, 20.6, 15.4, 2.6, 1.2, 0.5), "eye", group="glow", tag="eye")
        k.box(hd, C(sx * 6.4, 20.6, 15.7, 0.5, 1.2, 0.3), "dark", tag="pupil")
    teeth(k, hd, (-9, 13.6, 24.4), (9, 13.6, 24.4), 8, 2.6, down=True, w=0.8)
    teeth(k, hd, (-8.4, 7.8, 24.0), (8.4, 7.8, 24.0), 7, 1.8, down=False, w=0.8)
    # the lure: a fleshy stalk from the brow arching forward, the bulb hanging over the mouth
    def lure(at, tip, s=1.0):
        mid = ((at[0] + tip[0]) / 2, max(at[1], tip[1]) + 5 * s, (at[2] + tip[2]) / 2)
        k.limb(hd, at, mid, 1.2 * s, "skin", "stalk")
        k.limb(hd, mid, tip, 0.9 * s, "skin", "stalk")
        k.blob(hd, (tip[0], tip[1] - 1.6 * s, tip[2]), (1.6 * s, 1.8 * s, 1.6 * s), "lure", "lure", step=0.5)
    lure((0, 19.6, 18), (0, 22, 30))
    def foot(lg, a):
        k.box(lg, C(a[0], 0, a[2] + 1.0, 6.4, 1.4, 6.0), "skin", tag="foot")
        for t in (-2, 0, 2):
            k.box(lg, C(a[0] + t, 0, a[2] + 4.6, 1.2, 0.8, 2.6), "skin", tag="toe")
            k.shard(lg, (a[0] + t, 0.4, a[2] + 5.8), (0, -0.2, 1), 1.2, 0.6, mat="dark", tag="claw")
    for side, s in ((1, "l"), (-1, "r")):   # bowed out, short and thick
        leg(k, body, J, "leg_%s0" % s, ("LL" if side > 0 else "RL") + "1", (side * 9, 10, 6), (side * 13.4, 6, 8),
            (side * 13, 1.0, 9), 5.2, 4.2, "skin", foot)
        leg(k, ab, J, "leg_%s1" % s, ("LL" if side > 0 else "RL") + "4", (side * 9, 10, -11), (side * 14, 7, -10),
            (side * 13.6, 1.0, -13), 6.0, 4.4, "skin", foot)
    if legend:
        # Grandmother Mire: reeds grown out of her, skulls of what followed the light strung on her, three lures
        lure((-5, 19.4, 16), (-8, 20, 27), 0.8)
        lure((5, 19.4, 16), (8, 20, 27), 0.8)
        for i, (x, z) in enumerate(((-6, 6), (5, 2), (-2, -2), (6, -6), (-7, -10), (2, -14), (0, 9))):
            part = body if z > -6 else ab
            k.cluster(part, (x, 17.4, z), 5, 7 + X.h3(i, 9, 9) * 4, 1.0, mat="reed", seed=i + 70, spread=0.4)
        for i, (x, y, z) in enumerate(((-10.6, 12, 4), (10.4, 11, -1), (-10, 11, -10), (10.4, 12, -12), (3, 17.6, -6))):
            part = body if z > -6 else ab
            k.limb(part, (x, y + 4, z), (x, y, z), 0.3, "rope", "skull_string")
            k.box(part, C(x, y - 3.0, z, 2.6, 3.0, 2.6), "bone", tag="skull")
            for sx in (-1, 1):
                k.box(part, C(x + sx * 0.6, y - 1.6, z + 1.3, 0.8, 0.8, 0.2), "dark", tag="socket")
        k.blob(body, (0, 20, 2), (6, 1, 6), "moss", "moss_back", step=0.5)
        grow(k, 1.5)
    glow_tags(k, "eye", "lure")
    k.s.shaders = shaders(
        skin=X.surf(BOGSKIN, 0.54, 1.3, 0.2, 0.0, pattern=warts, crust=(MOSS, 0.2)),
        belly=X.surf(BELLY, 0.5, 1.0, 0.16, 0.0, stripe=2),
        osteo=X.surf(BOGSKIN, 0.66, 1.4, 0.2, 0.1, pattern=plates),
        fungus=X.surf(FUNGUS, 0.56, 1.3, 0.16, 0.14),
        reed=X.surf(REED, 0.5, 1.1, 0.2, 0.0, stripe=3),
        lure=X.glow(LURE), eye=X.glow(LURE, 0.62, 0.2),
    )
    return k.s, k.parts, J


# ================================================================ Vexclaw (jungle)

def vexclaw(name="vexclaw", legend=False):
    """You don't see the Vexclaw. You see its stripes, low in the leaves, the light of them moving - and then four
    eyes open over them. A long black panther-thing, all shoulder and claw, ears laid back like blades, its back
    ridged with spines; four tails that end in barbed bone, lashing; stripes that glow the green of deep water."""
    k = X.Kit(name)
    J = {"body": "Root", "head": "Head", "abdomen": "Stomach"}
    body = k.part("body", (0, 17, 3))
    k.blob(body, (0, 18, 5), (8.2, 8.0, 10.8), "fur", "chest", step=0.9)
    for sx in (-1, 1):
        k.blob(body, (sx * 5.8, 21, 9), (2.6, 4.6, 3.6), "fur", "shoulder_blade", step=0.7)
        k.shard(body, (sx * 5.8, 24.6, 8), (sx * 0.3, 1, -0.5), 3.0, 1.2, mat="barb", tag="shoulder_spine")
    ab = k.part("abdomen", (0, 17, -7), (), "body")
    k.blob(ab, (0, 17, -11), (6.4, 6.4, 9.0), "fur", "haunch", step=0.9)
    for z in (12, 8, 4, 0):
        k.shard(body, (0, 24.8 - abs(z - 6) * 0.2, z), (0, 1, -0.7), 2.4, 1.0, mat="barb", tag="spine")
    for z in (-6, -10, -14):
        k.shard(ab, (0, 22.6, z), (0, 1, -0.7), 2.0, 0.9, mat="barb", tag="spine")
    # the glowing stripes: arcs over the back and flanks
    for i, z in enumerate((12, 8.4, 4.8, 1.2, -2.4)):
        for sx in (-1, 1):
            k.limb(body, (0, 25.4, z), (sx * 7.0, 20, z - 1.2), 0.7, "stripe", "stripe", group="glow")
            k.limb(body, (sx * 7.0, 20, z - 1.2), (sx * 6.2, 14.6, z - 0.4), 0.6, "stripe", "stripe", group="glow")
    for z in (-7, -10.6, -14.2):
        for sx in (-1, 1):
            k.limb(ab, (0, 23.2, z), (sx * 6.2, 17.6, z - 1), 0.7, "stripe", "stripe", group="glow")
    # four tails, lashing apart, each with a barbed bone end
    for t, (sx, sy) in enumerate(((-1, 1), (1, 1), (-1.6, 0.2), (1.6, 0.2))):
        pts = [(sx * 1.0, 18 + sy, -18), (sx * 3.6, 15 + sy, -25), (sx * 6.6, 13 + sy, -31),
               (sx * 9.0, 14 + sy * 2, -37), (sx * 10.0, 17 + sy * 2, -40)]
        for (a, b), w in zip(zip(pts, pts[1:]), (2.2, 1.8, 1.4, 1.1)):
            k.limb(ab, a, b, w, "fur", "tail")
        tip = pts[-1]
        k.shard(ab, tip, (sx * 0.3, 0.6, -0.6), 4.2, 1.6, mat="barb", tag="tail_barb")
        for s2 in (-1, 1):
            k.shard(ab, tip, (sx * 0.4 + s2 * 0.8, 0.2, -0.4), 1.8, 0.7, mat="barb", tag="tail_barb")
        k.box(ab, C(pts[1][0], pts[1][1] + 0.4, pts[1][2], 1.0, 0.5, 1.0), "stripe", group="glow", tag="tail_stripe")
    # the head: narrow, long-fanged, four eyes in two rows, ears laid back like blades
    hd = k.part("head", (0, 21, 14), (("x", 2),), "body")
    k.blob(hd, (0, 21.8, 17), (4.6, 4.0, 4.8), "fur", "skull", step=0.7)
    k.box(hd, C(0, 18.6, 21.4, 4.4, 3.8, 5.4), "fur", tag="muzzle")
    k.box(hd, C(0, 21.2, 23.9, 2.0, 1.2, 0.6), "dark", tag="nose")
    k.limb(hd, (0, 17.4, 18.4), (0, 14.4, 22.6), 3.0, "fur", "jaw", d=3.0)
    k.limb(hd, (0, 18.0, 18.8), (0, 15.8, 23.0), 2.4, "mouth", "mouth", d=2.4)
    for sx in (-1, 1):
        k.shard(hd, (sx * 1.5, 18.8, 23.4), (0, -1, 0.1), 3.6 if not legend else 4.4, 0.8, mat="bone", tag="fang")
        k.shard(hd, (sx * 1.3, 14.8, 22.6), (0, 1, 0.1), 1.6, 0.6, mat="bone", tag="fang")
        eye(k, hd, (sx * 2.2, 23.2, 21.05), 1.4, 0.6)
        eye(k, hd, (sx * 3.0, 21.6, 20.65), 1.2, 0.5)
        k.limb(hd, (sx * 1.0, 24.2, 21), (sx * 3.8, 24.6, 20), 0.8, "fur", "brow")
        k.shard(hd, (sx * 3.4, 24.4, 15.6), (sx * 0.4, 0.3, -1), 5.4, 1.8, mat="fur", tag="ear")
        k.limb(hd, (sx * 4.2, 20, 17), (sx * 5.0, 15.6, 15.4), 1.0, "fur", "whisker_ruff")
    def paw(lg, a):
        k.box(lg, C(a[0], 0, a[2] + 0.8, 4.6, 2.0, 5.2), "fur", tag="foot")
        claws(k, lg, (a[0], 0.6, a[2] + 3.4), 4, 1.0, 2.8 if not legend else 3.4, 0.6, mat="barb")
    for side, s in ((1, "l"), (-1, "r")):
        leg(k, body, J, "leg_%s0" % s, ("LL" if side > 0 else "RL") + "1", (side * 5.6, 14, 8), (side * 7.0, 8.0, 3.6),
            (side * 6.2, 1.2, 11.0), 5.8, 4.0, "fur", paw)
        leg(k, ab, J, "leg_%s1" % s, ("LL" if side > 0 else "RL") + "4", (side * 5.2, 15, -12), (side * 6.0, 10.4, -3.6),
            (side * 5.6, 1.2, -16), 6.6, 3.8, "fur", paw)
    if legend:
        # the Hollow Smile: the jaw split back to the ears, a grin of teeth on both sides, the stripes burning
        for sx in (-1, 1):
            k.limb(hd, (sx * 2.2, 18.6, 22.6), (sx * 4.8, 19.6, 16.6), 1.0, "mouth", "grin")
            teeth(k, hd, (sx * 2.4, 19.2, 22.2), (sx * 4.8, 20.2, 17.2), 6, 1.2, down=True, w=0.5, mat="ivory")
            teeth(k, hd, (sx * 2.4, 18.0, 22.2), (sx * 4.8, 19.0, 17.2), 5, 1.0, down=False, w=0.5, mat="ivory")
            k.limb(hd, (sx * 4.8, 19.6, 16.6), (sx * 5.0, 19.4, 15.8), 0.6, "stripe", "grin_glow", group="glow")
        for i, z in enumerate((10.6, 6.6, 3.0, -0.6)):
            for sx in (-1, 1):
                k.limb(body, (0, 25.4, z), (sx * 7.0, 20, z - 1.2), 0.5, "stripe_hot", "stripe", group="glow")
        k.blob(hd, (0, 24.4, 16), (3.4, 1.0, 3.0), "bone", "brow_mask", step=0.5)
        grow(k, 1.3)
    glow_tags(k, "eye")
    k.s.shaders = shaders(
        fur=X.surf(PANTHER, 0.52, 1.4, 0.16, 0.02, pattern=strands),
        barb=X.surf(BONE, 0.46, 1.3, 0.12, 0.1, pattern=grain),
        stripe=X.glow(STRIPE, 0.56, 0.3), stripe_hot=X.glow(STRIPE, 0.8, 0.18),
        eye=X.glow(STRIPE, 0.86, 0.12),
    )
    return k.s, k.parts, J


# ================================================================ Tidetusk (coast)

def tidetusk(name="tidetusk", legend=False):
    """The whalers' towns on the cold coast tell their children the Tidetusk takes the ones who walk the
    tideline after dark. It comes out of the surf like a seal and runs like a hound: a walrus's great blubbered
    front on a hound's haunches, slick blue-grey hide, barnacles grown over its back into armour, kelp hanging off
    it; tusks as long as oars; and the harpoons of three generations of whalers still in its back."""
    k = X.Kit(name)
    J = {"body": "Root", "head": "Head", "abdomen": "Stomach"}
    body = k.part("body", (0, 18, 2))
    k.blob(body, (0, 17, 4), (13.4, 10.8, 11.8), "hide", "chest", step=1.0)
    for i, (y, r) in enumerate(((22, 10.4), (18, 11.4), (14, 10.6))):     # blubber rolls round the neck
        k.blob(body, (0, y, 13.6 - i * 0.4), (r, 2.4, 3.0), "hide", "roll", step=0.7)
        k.box(body, C(0, y - 2.6, 13.6 - i * 0.4, r * 1.7, 0.6, 5.4), "dark", tag="fold")
    k.blob(body, (0, 11.6, 5), (9, 3.0, 8.6), "hide_l", "belly", step=0.8)
    for sx in (-1, 1):
        for y in (14, 17, 20):          # the fat folds of the front
            k.box(body, C(sx * 9.4, y, 8, 2.4, 0.6, 7), "dark", tag="fold")
    ab = k.part("abdomen", (0, 18, -8), (), "body")
    k.blob(ab, (0, 16, -11), (6.6, 6.8, 7.8), "hide", "haunch", step=0.9)
    k.limb(ab, (0, 18, -19), (0, 12, -23), 2.4, "hide", "tail")
    k.box(ab, C(0, 10.6, -23.4, 6, 1.2, 3.6), "hide", tag="tail_fluke")
    # barnacle armour over the back
    for i, (x, z) in enumerate(((0, 8), (-5, 5), (5, 5), (0, 2), (-6, -1), (6, -1), (-3, -4), (3, -4))):
        y = 27.6 - abs(x) * 0.5 - abs(z - 3) * 0.12
        k.box(body, C(x, y, z, 4.6, 1.6, 4.0), "barnacle", tag="barnacle_plate")
        for t in range(3):
            o = (X.h3(i, t, 1) - 0.5) * 3, (X.h3(i, t, 2) - 0.5) * 3
            k.box(body, C(x + o[0], y + 1.4, z + o[1], 1.4, 1.0 + X.h3(i, t, 3), 1.4), "barnacle", tag="barnacle")
            k.box(body, C(x + o[0], y + 2.2 + X.h3(i, t, 3), z + o[1], 0.6, 0.3, 0.6), "dark", tag="barnacle_mouth")
    for i, z in enumerate((-9, -13, -16)):
        k.box(ab, C(0, 21.6 - i * 1.4, z, 6 - i, 1.4, 3.6), "barnacle", tag="barnacle_plate")
    for sx in (-1, 1):                   # kelp hanging off it in ropes
        for z in (9, 4, -1, -6):
            p = body if z > -4 else ab
            k.limb(p, (sx * 9.6, 24, z), (sx * 11, 14, z - 0.6), 0.9, "kelp", "kelp")
            k.limb(p, (sx * 11, 14, z - 0.6), (sx * 10.6, 9, z + 0.4), 0.7, "kelp", "kelp")
    spears(k, body, [((-4, 28, 0), (-0.4, 1, -0.6)), ((5, 27, -3), (0.6, 1, -0.7)), ((-8, 24, 6), (-1, 0.8, -0.3))],
           mat_shaft="wood", L=12.0)
    for (x, y, z) in ((-4, 28, 0), (5, 27, -3)):
        k.limb(body, (x, y, z), (x * 1.6, 12, z - 6), 0.3, "rope", "harpoon_line")
    # the head: a hound's skull, walrus mustache, the tusks
    hd = k.part("head", (0, 21, 13), (("x", 4),), "body")
    k.blob(hd, (0, 22, 16), (6.0, 5.2, 5.4), "hide", "skull", step=0.8)
    k.box(hd, C(0, 17.4, 21.0, 8.6, 5.4, 5.6), "hide", tag="muzzle")
    k.blob(hd, (0, 18.4, 23.4), (4.6, 2.4, 1.8), "hide_l", "whisker_pad", step=0.5)
    for sx in (-1, 1):
        for t in range(5):              # bristles
            k.limb(hd, (sx * (1 + t * 0.8), 18.6 - t * 0.2, 24.6), (sx * (1.6 + t * 1.2), 16.4 - t * 0.4, 26), 0.3,
                   "ivory", "bristle")
        k.box(hd, C(sx * 1.2, 20.4, 24.0, 1.0, 1.2, 0.4), "dark", tag="nostril")
        eye(k, hd, (sx * 3.4, 23.4, 21.0), 1.2, 0.7)
        k.box(hd, C(sx * 3.4, 22.6, 20.9, 2.0, 2.2, 0.4), "dark", tag="socket")
        k.limb(hd, (sx * 2.6, 17, 22), (sx * 3.4, 9, 24), 2.0, "ivory", "tusk", d=1.8)
        k.shard(hd, (sx * 3.4, 9, 24), (sx * 0.1, -1, 0.5), 8.0 if not legend else 10.0, 1.8, mat="ivory", tag="tusk")
        k.box(hd, C(sx * 3.0, 14.6, 22.8, 2.4, 0.8, 2.4), "dark", tag="tusk_crack")
    k.box(hd, C(0, 14.0, 19.4, 6.0, 2.4, 4.4), "hide_l", tag="jaw")
    k.box(hd, C(0, 15.6, 21.4, 5.4, 0.8, 3.6), "mouth", tag="mouth")
    def flipper(lg, a):                 # the front: a thick clawed flipper-foot
        k.box(lg, C(a[0], 0, a[2] + 1.6, 8.4, 1.8, 9.0), "hide", tag="foot")
        claws(k, lg, (a[0], 0.6, a[2] + 6.0), 4, 1.8, 2.4, 0.9)
    def paw(lg, a):
        k.box(lg, C(a[0], 0, a[2] + 0.8, 5.0, 2.0, 5.4), "hide", tag="foot")
        claws(k, lg, (a[0], 0.6, a[2] + 3.4), 3, 1.3, 1.8, 0.7)
    for side, s in ((1, "l"), (-1, "r")):
        leg(k, body, J, "leg_%s0" % s, ("LL" if side > 0 else "RL") + "1", (side * 9.4, 12, 9), (side * 13.0, 6, 12),
            (side * 12.4, 1.2, 13), 7.6, 6.0, "hide", flipper)
        leg(k, ab, J, "leg_%s1" % s, ("LL" if side > 0 else "RL") + "4", (side * 5.4, 12, -13), (side * 6.0, 6.4, -17),
            (side * 5.6, 1.2, -14), 6.0, 4.4, "hide", paw)
    if legend:
        # Old Harpoon: a ship's anchor driven into its back, the chain dragging behind; more harpoons, older scars
        an = k.part("anchor", (2, 30, -2), (), body, bone=False)
        k.limb(an, (2, 26, -1), (5, 42, -6), 2.2, "iron", "anchor_shank")
        k.limb(an, (2.6, 40, -5), (7.4, 44, -7), 1.4, "iron", "anchor_stock")
        k.limb(an, (2.6, 40, -5), (-2.2, 36, -3), 1.4, "iron", "anchor_stock")
        k.ring(an, 5.4, 44.8, -6.4, 1.6, 0.8, "iron", "anchor_ring", n=8, axis="x")
        for sx in (-1, 1):
            k.limb(an, (2, 27.6, -1), (2 + sx * 5, 30, 0), 1.6, "iron", "anchor_arm")
            k.shard(an, (2 + sx * 5, 30, 0), (sx * 0.3, 1, 0.3), 2.6, 2.4, mat="iron", tag="anchor_fluke")
        k.chain(ab, (5, 44, -6), (6, 20, -18), 7, "iron", "anchor_chain", w=1.4)
        k.chain(ab, (6, 20, -18), (4, 1.0, -36), 8, "iron", "anchor_chain", w=1.4)
        spears(k, ab, [((-4, 24, -12), (-0.4, 1, -0.5)), ((4, 23, -14), (0.6, 1, -0.8))], L=11.0, snapped=(1,))
        for b in k.s.boxes:
            if b.tag == "anchor_shank" or b.tag == "anchor_arm":
                b.mat = "rust"
        for (x, z) in ((-8, 0), (8, 4), (-6, 8)):
            k.limb(body, (x, 26, z - 3), (x * 1.1, 18, z + 2), 0.5, "scar", "scar")
        grow(k, 1.4)
    glow_tags(k, "eye")
    k.s.shaders = shaders(
        hide=X.surf(SEAHIDE, 0.52, 1.5, 0.14, 0.02, crust=(BARNACLE, 0.12)),
        hide_l=X.surf(SEAHIDE, 0.7, 1.2, 0.14, 0.0),
        barnacle=X.surf(BARNACLE, 0.5, 1.4, 0.3, 0.1, pattern=warts),
        kelp=X.surf(KELP, 0.5, 1.2, 0.2, 0.0, stripe=2),
        rag=X.surf(KELP, 0.5, 1.0, 0.2, 0.0, holes=True),
        gore=X.surf(GORE, 0.5, 1.0, 0.2, 0.0),
        scar=X.surf(BARNACLE, 0.7, 1.0, 0.1, 0.0),
        eye=X.glow(SEAEYE, 0.7, 0.24),
    )
    return k.s, k.parts, J


# ================================================================ Cragmaul (badlands)

def cragmaul(name="cragmaul", legend=False):
    """The miners of the red badlands broke into a seam that broke back. The Cragmaul walks on its knuckles like an
    ape the size of a hut, all shoulder and arm, the rock grown over it in plates; copper and gold glint in the
    seams of its back where it has been eating the mountain; its face is a skull of stone with a jaw that grinds,
    and amber light in the pits of its eyes."""
    k = X.Kit(name)
    J = {"body": "Root", "head": "Head", "abdomen": "Stomach"}
    body = k.part("body", (0, 26, 2))
    k.blob(body, (0, 28, 3), (12, 11, 10), "skin", "chest", step=1.1)
    k.blob(body, (0, 37, 0), (11, 6.0, 8.4), "rock", "hump", step=1.0)
    for sx in (-1, 1):                   # the boulder shoulders
        k.blob(body, (sx * 11.6, 34, 4), (5.6, 5.4, 6.0), "rock", "shoulder", step=0.9)
        k.blob(body, (sx * 13.2, 38, 3), (2.6, 2.0, 3.0), "rock", "shoulder_cap", step=0.6)
    for i, (x, y, z) in enumerate(((0, 32, 12), (-6, 26, 12.4), (6, 26, 12.4), (0, 21, 11.6))):   # the chest slabs
        k.box(body, C(x, y, z, 7.0 if x == 0 else 5.4, 5.0, 1.4), "rock", tag="chest_plate")
    ab = k.part("abdomen", (0, 22, -6), (), "body")
    k.blob(ab, (0, 19.4, -9), (9, 7.6, 7.6), "skin", "haunch", step=1.0)
    k.blob(ab, (0, 25, -9), (7.6, 3.4, 6.4), "rock", "rump_plate", step=0.8)
    # ore in the seams of the back
    for i, (x, y, z) in enumerate(((-4, 42, 1), (3, 42.4, -1), (-7, 39, 4), (7, 40, 2), (0, 41, 5), (-2, 38, -5),
                                   (5, 37, -5), (-9, 36, 0))):
        k.box(body, C(x, y, z, 1.6 + X.h3(i, 1, 1), 1.0, 1.4), "ore", tag="ore")
        k.shard(body, (x, y + 0.6, z), (X.h3(i, 2, 2) - 0.5, 1, X.h3(i, 3, 3) - 0.5), 2.0, 1.0, mat="gold", tag="ore")
    for z in (2, -3):
        k.cluster(body, (0, 42.4, z), 3, 4.4, 2.2, mat="rock", seed=int(z) + 80, spread=0.6, up=(0, 1, -0.3))
    # the head: low between the shoulders, a skull of stone
    hd = k.part("head", (0, 31, 11), (("x", 4),), "body")
    k.blob(hd, (0, 32, 14), (5.4, 5.0, 4.6), "skin", "skull_back", step=0.8)
    k.box(hd, C(0, 33.0, 16.6, 10.4, 4.2, 4.4), "rock", tag="brow")
    k.box(hd, C(0, 36.6, 15, 8.4, 2.4, 6), "rock", tag="crown")
    k.box(hd, C(0, 28.4, 17.6, 8.0, 4.8, 3.4), "rock", tag="face")
    for sx in (-1, 1):
        k.box(hd, C(sx * 2.4, 31.0, 19.2, 3.2, 2.4, 0.6), "dark", tag="socket")
        eye(k, hd, (sx * 2.4, 31.4, 19.55), 1.6, 1.2)
        k.box(hd, C(sx * 4.6, 29.4, 18.4, 2.0, 3.0, 2.2), "rock", tag="cheek")
    k.box(hd, C(0, 30.0, 19.4, 1.8, 1.4, 1.2), "rock", tag="nose_ridge")
    k.box(hd, C(0, 23.2, 18, 9.6, 4.4, 4.6), "rock", tag="jaw")              # the underbite
    teeth(k, hd, (-3.6, 27.4, 20.2), (3.6, 27.4, 20.2), 5, 2.2, down=False, w=1.0, mat="stone")
    k.box(hd, C(0, 27.4, 18.6, 7.0, 1.0, 2.6), "mouth", tag="mouth")
    for sx in (-1, 1):
        k.shard(hd, (sx * 4.4, 36.0, 15), (sx * 0.8, 0.6, -0.4), 4.6, 2.2, mat="rock", tag="skull_horn")
    reshape(k, hd, 1.2, (0, 1.4, 5.0))
    k.blob(body, (0, 31, 14), (6.0, 6.0, 4.6), "skin", "neck", step=0.9)
    k.box(body, C(0, 35, 14, 9, 2.4, 6), "rock", tag="neck_plate")
    # front legs are the arms: long, plated, the fists knuckled down
    def fist(lg, a):
        k.blob(lg, (a[0], 3.0, a[2] + 0.6), (3.6, 3.0, 3.4), "skin", "fist", step=0.7)
        for t in (-2.2, -0.8, 0.8, 2.2):
            k.box(lg, C(a[0] + t, 0, a[2] + 2.0, 1.4, 2.0, 1.8), "rock", tag="knuckle")
        k.box(lg, C(a[0], 4.6, a[2] + 0.6, 6.4, 1.8, 5.6), "rock", tag="fist_plate")
    def foot(lg, a):
        k.box(lg, C(a[0], 0, a[2] + 1.0, 5.0, 2.0, 6.0), "skin", tag="foot")
        claws(k, lg, (a[0], 0.6, a[2] + 3.8), 3, 1.4, 1.6, 0.9, mat="stone")
    for side, s in ((1, "l"), (-1, "r")):
        lg = leg(k, body, J, "leg_%s0" % s, ("LL" if side > 0 else "RL") + "1", (side * 12, 32, 5), (side * 15, 18, 9),
                 (side * 13.4, 5.6, 12), 7.0, 6.4, "skin", fist)
        k.box(lg, C(side * 14.2, 10, 10.6, 7.2, 6.4, 6.4), "rock", tag="forearm_plate")
        k.box(lg, C(side * 14.8, 20, 8.6, 7.0, 6.0, 6.4), "rock", tag="elbow_plate")
        k.shard(lg, (side * 15.4, 19, 7), (side * 0.4, 0.2, -1), 3.4, 2.0, mat="rock", tag="elbow_spike")
        leg(k, ab, J, "leg_%s1" % s, ("LL" if side > 0 else "RL") + "4", (side * 6.4, 18, -9), (side * 7.4, 10, -6),
            (side * 7.0, 1.8, -8), 6.0, 4.6, "skin", foot)
    if legend:
        # the Walking Mountain: crystal grown out of its shoulders, a spring running off them, a pine on its back
        for sx in (-1, 1):
            k.cluster(body, (sx * 12, 39, 3), 5, 9, 2.6, mat="crystal", seed=90 + sx, spread=0.6, up=(sx * 0.4, 1, -0.2))
            for t in range(3):          # the water running off the shoulder in falling sheets
                x0 = sx * (14 + t * 0.6)
                k.limb(body, (x0, 37 - t, 2 + t), (x0 + sx * 0.8, 24 - t * 2, 6 + t), 0.8, "water", "falls", group="glow")
            k.blob(body, (sx * 12.6, 39.6, 2), (3.2, 0.8, 3.0), "water", "pool", step=0.4)
        pn = k.part("pine", (-2, 42, -3), (), body, bone=False)
        k.limb(pn, (-2, 42, -3), (-3, 56, -5), 1.6, "wood", "trunk")
        for i, (y, r) in enumerate(((47, 5.0), (50, 4.2), (53, 3.2), (56, 2.0))):
            k.stack(pn, -2.8, -4.6, [(y, r * 2, r * 2), (y + 3.2, 0.6, 0.6)], "pine", "pine", step=0.8)
        k.blob(body, (0, 42.6, 0), (8, 1.0, 6), "moss", "moss_back", step=0.5)
        grow(k, 1.5)
    glow_tags(k, "eye")
    k.s.shaders = shaders(
        skin=X.surf(APESKIN, 0.54, 1.3, 0.2, 0.0, pattern=strands),
        rock=X.veined(ROCK, ORE, 0.24, 0.025),
        ore=X.surf(ORE, 0.6, 1.4, 0.12, 0.2), gold=X.surf(GOLD, 0.6, 1.4, 0.1, 0.24),
        crystal=X.facets(CRYSTAL), water=X.glow(WATER, 0.5, 0.36),
        pine=X.surf(PINE, 0.5, 1.2, 0.24, 0.0),
        eye=X.glow(AMBER, 0.76, 0.2),
    )
    return k.s, k.parts, J


# ================================================================ the roster

def _l(f, n):
    return lambda: f(n, legend=True)


BEAST = dict(rig="crawler")
MOBS = {
    "thornmaw": dict(BEAST, make=thornmaw, ent=(2.4, 2.4), stats=dict(hp=150, speed=0.27, dmg=14, armor=6, kb=0.7)),
    "old_blackbriar": dict(BEAST, make=_l(thornmaw, "old_blackbriar"), ent=(3.2, 3.4), stats=dict(hp=600, speed=0.25, dmg=22, armor=9, kb=1.0), boss=True),
    "gorehorn": dict(BEAST, make=gorehorn, ent=(2.4, 2.8), stats=dict(hp=170, speed=0.3, dmg=16, armor=9, kb=0.9)),
    "red_plough": dict(BEAST, make=_l(gorehorn, "red_plough"), ent=(3.4, 3.8), stats=dict(hp=680, speed=0.28, dmg=24, armor=12, kb=1.0), boss=True),
    "frostjaw": dict(BEAST, make=frostjaw, ent=(1.9, 2.2), stats=dict(hp=120, speed=0.36, dmg=15, armor=4, kb=0.4)),
    "pale_widow": dict(BEAST, make=_l(frostjaw, "pale_widow"), ent=(2.5, 2.9), stats=dict(hp=520, speed=0.35, dmg=23, armor=6, kb=0.8), boss=True),
    "sun_basilisk": dict(BEAST, make=sun_basilisk, ent=(2.2, 1.6), stats=dict(hp=130, speed=0.26, dmg=13, armor=8, kb=0.5)),
    "sunbreaker": dict(BEAST, make=_l(sun_basilisk, "sunbreaker"), ent=(3.0, 2.2), stats=dict(hp=560, speed=0.25, dmg=21, armor=11, kb=0.9), boss=True),
    "bogmaw": dict(BEAST, make=bogmaw, ent=(2.4, 1.6), stats=dict(hp=160, speed=0.22, dmg=15, armor=5, kb=0.8)),
    "grandmother_mire": dict(BEAST, make=_l(bogmaw, "grandmother_mire"), ent=(3.6, 2.6), stats=dict(hp=700, speed=0.21, dmg=24, armor=8, kb=1.0), boss=True),
    "vexclaw": dict(BEAST, make=vexclaw, ent=(1.6, 1.8), stats=dict(hp=100, speed=0.38, dmg=14, armor=3, kb=0.3)),
    "hollow_smile": dict(BEAST, make=_l(vexclaw, "hollow_smile"), ent=(2.1, 2.3), stats=dict(hp=440, speed=0.37, dmg=22, armor=5, kb=0.7), boss=True),
    "tidetusk": dict(BEAST, make=tidetusk, ent=(2.2, 2.2), stats=dict(hp=150, speed=0.28, dmg=15, armor=7, kb=0.7)),
    "old_harpoon": dict(BEAST, make=_l(tidetusk, "old_harpoon"), ent=(3.1, 3.6), stats=dict(hp=640, speed=0.27, dmg=23, armor=10, kb=1.0), boss=True),
    "cragmaul": dict(BEAST, make=cragmaul, ent=(2.4, 2.8), stats=dict(hp=200, speed=0.24, dmg=17, armor=12, kb=1.0)),
    "walking_mountain": dict(BEAST, make=_l(cragmaul, "walking_mountain"), ent=(3.6, 4.6), stats=dict(hp=800, speed=0.22, dmg=26, armor=15, kb=1.0), boss=True),
}
