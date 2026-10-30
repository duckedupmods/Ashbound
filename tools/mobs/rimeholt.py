"""Rimeholt's monsters, the Rimebound, each built by hand (tools/vox2.py). A jarl of the frost giants took the black
keep for his hall and the winter came with him: his dead huskarls still keep its doors, the drowned and the frozen rise
as his thralls, his trolls haul his ice and his seers read the runes for him. Black iron, tarred wood and leather,
grey wolf fur and white, blue wool; frost crusted on everything that faces up, ice growing out of them in crystals,
and the blue of rune-light burning in their eyes.

    rime_thrall     swarm   a draugr: a frozen corpse in rotted mail, a broken helm, a beard of icicles, a seax
    frost_troll     brute   a hunched blue-grey troll with ice crystals growing from its back, tusks, a broken
                            manacle on one wrist, a pine trunk bound in iron and ice for a club
    huskarl         guard   the jarl's dead hearth-guard: a spectacle helm with frost spikes on its crest, mail to the
                            knees, a wolf-pelt mantle, a painted round shield and a bearded axe
    rune_seer       caster  a hunched seeress under a white wolf's pelt, its jaws over her brow, a veil of bone beads,
                            a rune-ring staff with ice at its heart
    winter_wolf     elite   a white dire wolf the size of a horse, ice crystals down its spine, frost burning in its
                            jaws, a black iron collar cut with runes
    jarl_hrimgar    boss    the frost giant jarl: a beard of ice to his belt, a crown of ice spikes, rune-scars burning
                            on his bare chest, a wolf-pelt mantle, ice grown from his shoulders, a black greataxe

    python tools/monsterforge.py rimeholt --preview ; python tools/mobsheet.py rimeholt
"""
import math

import vox2 as X
from vox2 import C, ramp
from serpent_ziggurat import tube, disc, _along, grow

IRON = ramp("#08090c", "#101318", "#191d24", "#232831", "#2e343f", "#3c4350", "#525a68")
FROST = ramp("#4a5866", "#6c7c8c", "#8ea0b0", "#b0c2d0", "#d0e0ea", "#eef6fa")
ICEL = ramp("#2a5a8a", "#3e78aa", "#5a98c8", "#7ab8e0", "#a4d4f0", "#d4eefa")
ICE = ramp("#0a2a5a", "#14508e", "#2a84c8", "#5ab8f4", "#a0e0ff", "#e8f8ff")
FUR = ramp("#1a1a1e", "#2a2a30", "#3c3c44", "#52525c", "#6c6c76", "#8c8c96", "#b0b0ba")
FURW = ramp("#525a64", "#707a84", "#909aa4", "#b0b8c2", "#ced6de", "#eaf0f4")
DEAD = ramp("#161c22", "#212a32", "#2e3842", "#3c4854", "#4e5a66", "#64707c")
TROLL = ramp("#121a1e", "#1c262c", "#28343c", "#36444e", "#465662", "#5a6a78")
LEATHER = ramp("#120c08", "#1c140e", "#281c14", "#36261a", "#463222")
WOOD = ramp("#0c0a08", "#16110d", "#211913", "#2d2219", "#3b2d21")
WOOL = ramp("#0a1020", "#121c30", "#1a2844", "#24365a", "#304670")
BONE = ramp("#3a3428", "#5c5444", "#827a64", "#a8a088", "#cec6ac", "#ece6d0")
BRONZE = ramp("#1e1206", "#34200c", "#523414", "#704a1e", "#8e6228", "#ae7e38")
GORE = ramp("#06080c", "#0c1016", "#141a22", "#1c2430")


def mail(p, n, i, j, w, h):
    return -0.26 if (i + j) % 2 == 0 else 0.06


def strands(p, n, i, j, w, h):
    return -0.18 if i % 3 == 0 else (0.06 if i % 3 == 1 else 0)


def shaders():
    crust = (FROST, 0.3)
    return {
        "iron": X.surf(IRON, 0.5, 1.4, 0.14, 0.22, crust=crust),
        "mail": X.surf(IRON, 0.52, 1.3, 0.1, 0.0, crust=(FROST, 0.18), pattern=mail),
        "frost": X.surf(FROST, 0.56, 1.2, 0.14, 0.12),
        "ice": X.facets(ICEL),
        "rune": X.glow(ICE),
        "eye": X.glow(ICE, 0.8, 0.16),
        "fur": X.surf(FUR, 0.5, 1.2, 0.22, 0.04, crust=(FROST, 0.24), pattern=strands),
        "fur_w": X.surf(FURW, 0.52, 1.2, 0.2, 0.04, pattern=strands),
        "dead": X.wrinkled(DEAD, 0.9),
        "troll": X.surf(TROLL, 0.5, 1.3, 0.26, 0.06, crust=(FROST, 0.26)),
        "leather": X.surf(LEATHER, 0.5, 1.1, 0.2, 0.06),
        "wood": X.surf(WOOD, 0.5, 1.1, 0.2, 0.08, stripe=4, crust=(FROST, 0.2)),
        "wool": X.surf(WOOL, 0.5, 1.0, 0.2, 0.0, holes=True),
        "bone": X.surf(BONE, 0.54, 1.2, 0.14, 0.12),
        "bronze": X.surf(BRONZE, 0.5, 1.4, 0.12, 0.22),
        "paint": X.surf(FROST, 0.62, 1.0, 0.1, 0.0),
        "mouth": X.dark(GORE),
        "dark": X.dark(IRON),
    }


# ================================================================ shared brushes

def icicles(k, part, pts, L, w=0.9, seed=1):
    """icicles hanging from each point, their lengths uneven"""
    for i, p in enumerate(pts):
        f = 0.5 + 0.5 * X.h3(i, seed, 3)
        k.shard(part, p, (0, -1, 0.02), L * f, w * (0.7 + 0.3 * f), mat="ice", tag="icicle")


def ice_beard(k, part, x, y, z, w, L, n=None, mat="frost"):
    """a beard frozen solid: a mass under the jaw, strands down it, every strand ending in an icicle"""
    n = n or max(3, int(w / 1.2))
    k.box(part, C(x, y - L * 0.35, z, w, L * 0.35, 2.0), mat, tag="beard")
    for i in range(n):
        t = (i + 0.5) / n
        bx = x - w / 2 + w * t
        ll = L * (1.0 - 0.55 * abs(t - 0.5) * 2) * (0.85 + 0.15 * X.h3(i, 3, 1))
        k.limb(part, (bx, y - L * 0.2, z + 0.4), (bx * 0.85 + x * 0.15, y - ll * 0.8, z + 0.8), 1.3, mat, "beard_strand")
        k.shard(part, (bx * 0.85 + x * 0.15, y - ll * 0.8, z + 0.8), (0, -1, 0.05), ll * 0.35, 1.1, mat="ice", tag="icicle")


def crystals(k, part, at, n, length, w, up=(0, 1, 0), seed=1, spread=0.6):
    """ice crystals grown out of a back or a shoulder: a cluster of hexagon-ish shards, a few small ones round them"""
    k.cluster(part, at, n, length, w, mat="ice", seed=seed, spread=spread, up=up)
    k.cluster(part, at, n, length * 0.45, w * 0.55, mat="ice", seed=seed + 7, spread=spread * 1.6, up=up)


def swirl_shield(k, part, c, r, face=1):
    """a painted round shield facing +x (face 1) or -x: blue boards, a white swirl of four arms, an iron rim and boss"""
    cx, cy, cz = c
    disc(k, part, c, r, "x", "wool", "shield", thick=1.4)
    for i in range(1, 7):                          # the planks
        z = cz - r + i * 2 * r / 7
        h = math.sqrt(max(0.0, r * r - (z - cz) ** 2))
        k.box(part, C(cx + face * 0.72, cy - h, z, 0.2, 2 * h, 0.2), "dark", tag="plank")
    for arm in range(4):
        pts = []
        for s in range(9):
            rr = 1.8 + s * (r - 2.6) / 8
            a = arm * math.pi / 2 + rr * 0.2
            pts.append((cx + face * 0.85, cy + math.sin(a) * rr, cz + math.cos(a) * rr))
        for a, b in zip(pts, pts[1:]):
            k.limb(part, a, b, 1.8, "paint", "swirl", d=0.3)
    for a in range(20):
        a0, a1 = a * math.pi / 10, (a + 1) * math.pi / 10
        k.limb(part, (cx + face * 0.4, cy + math.sin(a0) * r, cz + math.cos(a0) * r), (cx + face * 0.4, cy + math.sin(a1) * r, cz + math.cos(a1) * r), 1.2, "iron", "rim")
    k.blob(part, (cx + face * 1.0, cy, cz), (1.4, 2.2, 2.2), "iron", "boss", step=0.6)


# ================================================================ the Rime Thrall (swarm)

def rime_thrall():
    """What the jarl drowned in the fjord under the keep comes back up through the ice. A draugr: a gaunt blue-grey
    corpse hunched in rotted mail, a broken iron cap on its skull, a beard frozen into icicles, its jaw hanging open,
    the blue rune-light burning in its sockets, frost thick on its shoulders; a notched seax in its fist."""
    k = X.Kit("rime_thrall")
    hips = k.part("hips", (0, 19, 0))
    k.stack(hips, 0, 0, [(12, 10.0, 7.0), (19, 10.4, 7.2)], "mail", "mail_skirt")
    k.box(hips, C(0, 18.0, 0, 11.0, 1.4, 7.8), "leather", tag="belt")
    for i, x in enumerate((-4.4, -2.0, 0.6, 3.2)):       # the rotten hem in tatters
        k.box(hips, C(x, 9.6 + (i % 2) * 1.2, 3.4, 1.8, 2.6, 0.6), "mail", tag="tatter")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.8
        th = k.part("thigh_" + nm, (x, 18, 0), (("x", -10), ("z", side * 6)), "hips")
        sh = k.part("shin_" + nm, (x, 10, 0), (("x", 18),), th)
        ft = k.part("foot_" + nm, (x, 2.4, 0), (("x", -8),), sh)
        k.limb(th, (x, 17.6, 0), (x, 10.4, 0), 3.4, "dead", "thigh")
        k.limb(sh, (x, 10, 0), (x, 2.6, 0), 3.0, "dead", "shin")
        for y in (4.0, 6.0, 8.0):
            k.box(sh, C(x, y, 0, 3.6, 0.8, 3.6), "leather", tag="wrap")
        k.box(ft, C(x, 0, 1.2, 3.4, 2.2, 5.4), "dead", tag="foot")
        for t in (-1.0, 0, 1.0):
            k.shard(ft, (x + t, 0.8, 3.8), (0, -0.3, 1), 1.4, 0.5, mat="bone", tag="toe")
    # ---------------------------------------------------------------- torso: hunched, ribs through the rotted mail
    to = k.part("torso", (0, 19, 0), (("x", 24),), "hips")
    k.stack(to, 0, 0, [(19, 9.6, 6.4), (24, 9.8, 6.0), (29, 12.6, 7.0), (33, 12.0, 6.4)], "dead", "chest")
    for y in (22.6, 24.6, 26.6):
        k.box(to, C(0, y, 2.6, 8.4, 0.8, 1.0), "dark", tag="rib_gap")
    k.stack(to, 0, -0.4, [(26, 13.0, 7.6), (33.4, 12.6, 7.0)], "mail", "byrnie")
    k.box(to, C(1.6, 26, 3.3, 4.4, 3.6, 0.6), "dead", tag="torn")
    for sx in (-1, 1):
        k.blob(to, (sx * 5.0, 32.6, 0), (2.6, 1.4, 3.4), "frost", "frost_shoulder", step=0.6)
    k.limb(to, (-2.0, 24.0, 12.0), (1.6, 30.0, -10.0), 1.6, "ice", "ice_spear")   # what killed it, still in it
    k.shard(to, (-2.0, 24.0, 12.0), (-0.16, -0.27, 1), 3.0, 1.6, mat="ice", tag="ice_spear_tip")
    k.blob(to, (0, 27.0, 2.6), (1.6, 1.6, 1.0), "rune", "frozen_heart", step=0.6)
    for b in k.s.boxes:
        if b.tag == "frozen_heart":
            b.group = "glow"
    icicles(k, to, [(x, 26, 3.8) for x in (-5.4, -3.4, 4.6)] + [(x, 26, -3.6) for x in (-4, 0, 4)], 4.0, 0.8)
    # ---------------------------------------------------------------- the head: a broken cap, a frozen beard
    hd = k.part("head", (0, 33, 1.0), (("x", -22),), "torso")
    k.box(hd, C(0, 33.4, 1.0, 5.0, 5.8, 5.0), "dead", tag="skull")
    k.box(hd, C(0, 36.4, 3.4, 4.8, 0.9, 0.6), "dead", tag="brow")
    for sx in (-1, 1):
        k.box(hd, C(sx * 1.2, 35.0, 3.3, 1.6, 1.4, 0.6), "dark", tag="socket")
        k.box(hd, C(sx * 1.2, 35.3, 3.5, 0.9, 0.7, 0.4), "eye", group="glow", tag="eye")
        k.box(hd, C(sx * 2.0, 33.0, 3.25, 0.7, 1.4, 0.4), "dark", tag="cheek")
    k.box(hd, C(0, 32.6, 3.3, 3.2, 1.2, 0.5), "mouth", tag="mouth")
    for x in (-1.0, 0, 1.0):
        k.box(hd, C(x, 33.3, 3.45, 0.5, 0.6, 0.4), "bone", tag="teeth")
    k.box(hd, C(0, 31.0, 1.8, 4.0, 1.2, 3.4), "dead", tag="jaw")
    ice_beard(k, hd, 0, 31.4, 3.0, 4.6, 9.0, n=5)
    k.blob(hd, (0, 37.0, 1.0), (3.0, 1.8, 3.0), "iron", "cap", step=0.6)
    k.box(hd, C(0, 35.6, 3.6, 0.9, 3.0, 0.6), "iron", tag="nasal")
    k.box(hd, C(1.8, 37.2, 2.2, 1.6, 1.4, 1.6), "dead", tag="cap_break")
    k.limb(hd, (-2.6, 37.6, 0.6), (-5.4, 39.4, 0.2), 1.4, "bone", "horn")       # one horn left on the broken cap
    k.shard(hd, (-5.4, 39.4, 0.2), (-0.3, 1, -0.2), 3.4, 1.2, mat="bone", tag="horn")
    k.box(hd, C(2.6, 37.4, 0.6, 0.8, 1.4, 0.8), "bone", tag="horn_stump")
    for i, x in enumerate((-2.4, -1.2, 0, 1.2, 2.4)):    # frozen hair hanging from under the cap
        k.limb(hd, (x, 35.8, -1.6), (x * 1.2, 28.6 - (i % 2) * 1.6, -2.4), 1.0, "frost", "hair")
    # ---------------------------------------------------------------- arms: long, clawed, a seax
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 7.0
        up = k.part("arm_" + nm, (x, 31, 0), (("x", -30 if side > 0 else -50), ("z", side * 12)), "torso")
        fo = k.part("fore_" + nm, (x, 23.4, 0), (("x", -30 if side > 0 else -50),), up)
        hn = k.part("hand_" + nm, (x, 16, 0), (), fo)
        k.limb(up, (x, 30.6, 0), (x, 24, 0), 2.6, "dead", "upper_arm")
        k.box(up, C(x, 28.6, 0, 3.6, 2.4, 3.6), "mail", tag="sleeve")
        k.limb(fo, (x, 23.4, 0), (x, 16.6, 0), 2.4, "dead", "forearm")
        k.box(fo, C(x, 17.4, 0, 3.0, 2.6, 3.0), "leather", tag="bracer")
        icicles(k, fo, [(x, 22.6, -1.4)], 3.6, 0.8, seed=side + 4)
        k.box(hn, C(x, 13.6, 0.4, 2.4, 2.8, 2.6), "dead", tag="hand")
        for t in (-0.8, 0, 0.8):
            k.shard(hn, (x + t, 13.8, 1.6), (0, -1, 0.6), 2.2, 0.5, mat="bone", tag="nail")
    sx_ = k.part("seax", (-7.0, 14.4, 0.4), (("x", 80),), k.parts["hand_r"], bone=False)
    k.limb(sx_, (-7.0, 11.8, 0.4), (-7.0, 15.6, 0.4), 1.2, "leather", "grip")
    k.box(sx_, C(-7.0, 15.4, 0.4, 1.4, 0.8, 2.4), "bronze", tag="guard")
    for i in range(7):                            # a broken-backed seax: straight edge, the back angled down to the point
        y = 16.2 + i * 1.6
        w = 2.6 if i < 5 else 2.6 - (i - 4) * 0.8
        k.box(sx_, C(-7.0, y, 0.4 + (2.6 - w) / 2, 0.6, 1.65, w), "iron", tag="blade")
    k.box(sx_, C(-7.0, 18.6, 1.4, 0.65, 1.0, 0.8), "dark", tag="notch")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Frost Troll (brute)

def frost_troll():
    """The jarl keeps trolls the way men keep oxen. A hunched mountain of blue-grey hide gone hard as slate, the ice
    growing out of its back and shoulders in crystals as long as a man's arm, a long jaw with two tusks over the lip
    and a beard of frost; arms that hang to its knuckles, a broken manacle and its chain still on one wrist, and in the
    other fist a whole pine trunk bound in iron with ice frozen round its head."""
    k = X.Kit("frost_troll")
    hips = k.part("hips", (0, 22, 0))
    k.stack(hips, 0, 0, [(15, 17, 13), (22, 19, 14)], "troll", "pelvis")
    k.stack(hips, 0, 0, [(12, 19.6, 14.6), (21, 20.4, 15.2)], "fur", "loin_pelt")
    k.box(hips, C(0, 20.4, 0, 21, 1.8, 15.6), "leather", tag="belt")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 6.4
        th = k.part("thigh_" + nm, (x, 19, 0), (("x", -14), ("z", side * 12)), "hips")
        sh = k.part("shin_" + nm, (x, 11, 0), (("x", 22),), th)
        ft = k.part("foot_" + nm, (x, 3.4, 0), (("x", -8),), sh)
        k.stack(th, x, 0, [(10.6, 9.2, 9.6), (19, 10.6, 11.0)], "troll", "thigh")
        k.stack(sh, x, 0, [(3.4, 8.4, 9.0), (8, 9.6, 10.0), (11, 9.0, 9.6)], "troll", "calf")
        k.box(ft, C(x, 0, 2.4, 10.4, 3.6, 13.0), "troll", tag="foot")
        for t in (-3.0, 0, 3.0):
            k.shard(ft, (x + t, 1.4, 8.4), (0, -0.4, 1), 2.6, 1.6, mat="bone", tag="toe_claw")
    # ---------------------------------------------------------------- torso: a hunched mountain, ice from its back
    to = k.part("torso", (0, 22, 0), (("x", 30),), "hips")
    k.stack(to, 0, -1, [(22, 19, 14), (28, 24, 16), (35, 30, 18.4), (42, 32, 17.6), (47, 25, 14.4)], "troll", "body", step=1.2)
    k.blob(to, (0, 30, 6.0), (10.4, 8.0, 4.0), "troll", "gut", step=1.0)
    for y in (28, 31, 34):
        k.box(to, C(0, y, 9.6 - (y - 28) * 0.4, 9.0, 0.8, 1.0), "dark", tag="gut_fold")
    crystals(k, to, (0, 46, -6), 6, 16, 3.6, up=(0, 0.7, -0.7), seed=2)
    for sx in (-1, 1):
        crystals(k, to, (sx * 12, 46, -2), 4, 11, 3.0, up=(sx * 0.5, 0.9, -0.3), seed=5 + sx)
        crystals(k, to, (sx * 7, 40, -8.4), 3, 9, 2.6, up=(sx * 0.4, 0.4, -0.9), seed=9 + sx)
    # ---------------------------------------------------------------- the head: slung low and forward, tusked
    hd = k.part("head", (0, 44, 6), (("x", -30),), "torso")
    k.box(hd, C(0, 42.0, 7.4, 10.4, 8.6, 9.6), "troll", tag="skull")
    k.box(hd, C(0, 48.4, 10.0, 11.4, 2.4, 5.2), "troll", tag="brow")
    for sx in (-1, 1):
        k.box(hd, C(sx * 2.6, 46.4, 12.0, 2.0, 1.2, 0.8), "dark", tag="socket")
        k.box(hd, C(sx * 2.6, 46.6, 12.3, 1.2, 0.7, 0.6), "eye", group="glow", tag="eye")
        k.shard(hd, (sx * 5.4, 47.4, 6.4), (sx, 0.4, -0.4), 3.6, 1.6, mat="troll", tag="ear")
        k.shard(hd, (sx * 3.0, 40.6, 13.2), (sx * 0.2, 1, 0.3), 5.0, 1.6, mat="bone", tag="tusk")
    k.box(hd, C(0, 43.6, 12.2, 3.6, 3.4, 3.0), "troll", tag="nose")
    k.box(hd, C(0, 38.4, 8.6, 11.0, 3.4, 9.0), "troll", tag="jaw")
    k.box(hd, C(0, 41.2, 12.6, 7.4, 1.0, 0.8), "mouth", tag="mouth")
    for x in (-2.0, -0.6, 0.8, 2.2):
        k.shard(hd, (x, 41.0, 13.0), (0, 1, 0.2), 1.4, 0.7, mat="bone", tag="tooth")
    ice_beard(k, hd, 0, 38.4, 11.4, 9.6, 10.0, n=7)
    crystals(k, hd, (0, 49.6, 7), 3, 6, 2.0, up=(0, 1, -0.3), seed=4)
    # ---------------------------------------------------------------- arms: to the knuckles, the trunk club
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 17.6
        up = k.part("arm_" + nm, (x, 42, 0), (("x", -10 if side > 0 else -30), ("z", side * 14)), "torso")
        fo = k.part("fore_" + nm, (x, 28, 0), (("x", -34 if side > 0 else -40),), up)
        hn = k.part("hand_" + nm, (x, 14, 0), (), fo)
        k.blob(up, (x - side * 1.0, 42, 0), (7.0, 5.6, 7.4), "troll", "shoulder", step=1.0)
        k.limb(up, (x, 40, 0), (x, 29, 0), 7.4, "troll", "upper_arm")
        k.stack(fo, x, 0, [(15, 8.6, 9.0), (22, 10.4, 10.6), (28, 8.4, 8.6)], "troll", "forearm")
        k.box(hn, C(x, 7.6, 0.6, 9.4, 7.6, 9.8), "troll", tag="fist")
        for t in (-3.0, -1.0, 1.0, 3.0):
            k.box(hn, C(x + t, 6.6, 5.2, 1.8, 2.4, 1.8), "troll", tag="knuckle")
            k.shard(hn, (x + t, 7.6, 6.0), (0, -1, 0.6), 1.8, 0.9, mat="bone", tag="nail")
    k.box(k.parts["fore_l"], C(17.6, 15.4, 0, 11.0, 3.4, 11.0), "iron", tag="manacle")
    k.chain(k.parts["fore_l"], (20.6, 16, 3.6), (22, 2, 6.6), 6, mat="iron", w=1.6)
    cl = k.part("club", (-17.6, 10.6, 0.6), (("x", 74),), k.parts["hand_r"], bone=False)
    k.limb(cl, (-17.6, 2, 0.6), (-17.6, 30, 0.6), 4.2, "wood", "trunk")
    k.stack(cl, -17.6, 0.6, [(28, 6.0, 6.0), (40, 8.4, 8.4), (48, 7.4, 7.4)], "wood", "trunk_head")
    for y in (12, 22, 32, 42):
        k.box(cl, C(-17.6, y, 0.6, 7.0 + (y - 12) * 0.08, 1.4, 7.0 + (y - 12) * 0.08), "iron", tag="band")
    for a in range(0, 360, 60):                   # branch stubs and iron spikes round its head
        r = math.radians(a)
        k.shard(cl, (-17.6 + math.cos(r) * 3.6, 38 + (a % 120) * 0.04, 0.6 + math.sin(r) * 3.6), (math.cos(r), 0.3, math.sin(r)), 4.0, 1.6,
                mat="iron" if a % 120 else "wood", tag="spike")
    k.blob(cl, (-17.6, 44, 0.6), (5.4, 4.4, 5.4), "ice", "ice_cap", step=0.9)
    crystals(k, cl, (-17.6, 47, 0.6), 4, 8, 2.4, up=(0, 1, 0), seed=12)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Huskarl (guard)

def huskarl():
    """The jarl's hearth-guard died at his door and stayed there. A tall warrior in mail to the knees under a mantle
    of grey wolf pelt, an iron spectacle helm with a mail curtain and frost spikes standing on its crest, nothing
    behind the eye-rings but two blue fires and nothing under them but a beard of ice; a painted round shield, blue
    boards and a white swirl, and a bearded axe rimed white."""
    k = X.Kit("huskarl")
    hips = k.part("hips", (0, 22, 0))
    k.stack(hips, 0, 0, [(10, 12.6, 8.8), (22, 12.2, 8.2)], "mail", "mail_skirt")
    k.box(hips, C(0, 20.6, 0, 13.2, 1.8, 9.0), "leather", tag="belt")
    k.box(hips, C(0, 20.4, 4.6, 2.6, 2.2, 0.6), "bronze", tag="buckle")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 3.4
        th = k.part("thigh_" + nm, (x, 21, 0), (("x", -4), ("z", side * 4)), "hips")
        sh = k.part("shin_" + nm, (x, 11.4, 0), (("x", 6),), th)
        ft = k.part("foot_" + nm, (x, 2.8, 0), (("x", -2),), sh)
        k.stack(th, x, 0, [(11.6, 4.8, 5.2), (20, 5.6, 6.0)], "wool", "trouser")
        k.stack(sh, x, 0, [(3, 4.4, 4.8), (11.4, 4.8, 5.2)], "leather", "wrap")
        for y in (4.4, 6.4, 8.4, 10.4):
            k.box(sh, C(x, y, 0, 5.0, 0.6, 5.4), "wool", tag="wrap_band")
        k.box(sh, C(x, 2.6, 0, 6.0, 1.8, 6.4), "fur", tag="boot_fur")
        k.box(ft, C(x, 0, 1.4, 5.2, 2.6, 7.6), "leather", tag="foot")
    # ---------------------------------------------------------------- torso: mail, the wolf-pelt mantle
    to = k.part("torso", (0, 22, 0), (("x", 4),), "hips")
    k.stack(to, 0, 0, [(22, 12.2, 8.2), (27, 14, 8.6), (32, 17.6, 9.6), (37, 19.6, 9.8), (39.4, 15, 8.2)], "mail", "byrnie")
    k.limb(to, (7.6, 37.4, 4.8), (-6.4, 23, 4.6), 1.8, "leather", "baldric", d=0.6)
    for sx in (-1, 1):                            # iron lamellar over the shoulders, frosted
        for i in range(3):
            k.box(to, C(sx * (9.8 + i * 0.3), 35.4 - i * 1.7, 0, 5.6, 1.6, 9.6), "iron", tag="lame")
    k.stack(to, 0, -0.4, [(36, 21.6, 11.4), (40.4, 17.6, 10.6)], "fur", "mantle")
    cape = k.part("cape", (0, 39, -5), (("x", 6),), to, bone=False)
    k.stack(cape, 0, -5.6, [(8, 17.6, 1.2), (24, 18.6, 1.2), (39, 18.0, 1.4)], "fur", "cape")
    for i in range(-4, 5):                        # the ragged hem
        k.shard(cape, (i * 2.0, 8.4, -5.6), (0, -1, 0), 2.0 + (i % 3) * 1.0, 1.6, mat="fur", tag="hem")
    wh = k.part("wolf_head", (6.6, 40, 2), (), to, bone=False)
    k.box(wh, C(6.6, 39.6, 2.4, 4.6, 3.4, 5.6), "fur", tag="pelt_head")
    k.box(wh, C(6.6, 39.4, 6.0, 3.0, 2.0, 3.0), "fur", tag="pelt_snout")
    k.box(wh, C(7.0, 41.0, 4.8, 0.8, 0.6, 0.6), "dark", tag="pelt_eye")
    for t in (-0.8, 0.8):
        k.shard(wh, (6.6 + t, 39.6, 8.6), (0, -1, 0.1), 1.4, 0.5, mat="bone", tag="pelt_fang")
    # ---------------------------------------------------------------- the spectacle helm, the ice beard
    hd = k.part("head", (0, 39, 0.6), (("x", -4),), "torso")
    k.box(hd, C(0, 38.4, 0.6, 5.6, 6.6, 5.6), "dark", tag="face")
    k.blob(hd, (0, 43.4, 0.6), (3.6, 3.2, 3.8), "iron", "helm", step=0.6)
    k.box(hd, C(0, 42.6, 0.6, 7.4, 1.0, 7.6), "bronze", tag="brow_band")
    k.box(hd, C(0, 43.4, 0.6, 0.9, 4.2, 7.8), "bronze", tag="crest")
    for i in range(4):                            # frost spikes along the crest
        k.shard(hd, (0, 46.2 - abs(i - 1.5) * 0.6, 3.0 - i * 1.6), (0, 1, -0.3), 3.2 - abs(i - 1.5) * 0.6, 1.3, mat="ice", tag="crest_spike")
    for sx in (-1, 1):                            # the spectacles: iron rings round the eyes, a nasal
        k.box(hd, C(sx * 1.4, 40.2, 3.45, 2.2, 2.0, 0.7), "iron", tag="spectacle")
        k.box(hd, C(sx * 1.4, 40.7, 3.9, 1.2, 1.0, 0.4), "eye", group="glow", tag="eye")
        k.box(hd, C(sx * 3.0, 37.4, 1.0, 0.9, 5.0, 5.0), "iron", tag="cheek_guard")
    k.box(hd, C(0, 38.0, 3.5, 0.9, 4.4, 0.8), "iron", tag="nasal")
    k.stack(hd, 0, 0.2, [(34.6, 7.8, 7.4), (37.4, 7.4, 7.0)], "mail", "aventail")
    ice_beard(k, hd, 0, 37.4, 3.4, 4.8, 8.0, n=5)
    # ---------------------------------------------------------------- arms: the round shield, the bearded axe
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 10.4
        up = k.part("arm_" + nm, (x, 36, 0), (("x", -34 if side > 0 else -24), ("z", side * 10)), "torso")
        fo = k.part("fore_" + nm, (x, 27, 0), (("x", -56 if side > 0 else -72),), up)
        hn = k.part("hand_" + nm, (x, 18, 0), (), fo)
        k.limb(up, (x, 35, 0), (x, 27.6, 0), 4.0, "mail", "upper_arm")
        k.limb(fo, (x, 26.6, 0), (x, 19.4, 0), 3.6, "leather", "forearm")
        k.box(fo, C(x, 19.6, 0, 4.2, 5.0, 4.2), "iron", tag="bracer")
        k.box(hn, C(x, 15.6, 0.4, 3.6, 3.2, 3.8), "leather", tag="glove")
    sh = k.part("shield", (14, 17, 2), (("y", 8),), k.parts["hand_l"], bone=False)
    swirl_shield(k, sh, (15.0, 17.5, 2.0), 9.2)
    icicles(k, sh, [(15.4, 17.5 - 9.0, 2.0 + z) for z in (-3.0, -0.6, 2.0, 4.4)], 3.6, 0.9, seed=3)
    ax = k.part("axe", (-10.4, 15.6, 0.6), (("x", 84),), k.parts["hand_r"], bone=False)
    k.limb(ax, (-10.4, 6, 0.6), (-10.4, 38, 0.6), 1.4, "wood", "haft")
    for y in (8, 30):
        k.box(ax, C(-10.4, y, 0.6, 1.9, 1.0, 1.9), "iron", tag="haft_band")
    for i in range(8):                            # the bearded head: narrow at the eye, the beard dropping below
        y = 30.4 + i * 1.1
        lo = 1.8 + 0.9 * max(0, 4 - i) * (1 if i < 4 else 0)
        w = 2.0 + i * 0.55
        k.box(ax, C(-10.4, y - (lo - 1.8) * 0.6, 2.2 + w / 2, 0.9, 1.15 + (lo - 1.8) * 0.6, w), "iron", tag="axe_head")
    k.box(ax, C(-10.4, 26.8, 3.2 + 3.2, 0.9, 12.0, 0.9), "frost", tag="edge")
    k.box(ax, C(-10.4, 37.4, -0.2, 1.6, 1.6, 1.6), "iron", tag="poll")
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Rune Seer (caster)

def rune_seer():
    """The jarl's seeress reads his fate in bones and keeps the runes that hold the winter in the keep. She stoops
    under a whole white wolf's pelt, the beast's upper jaw over her brow and its paws crossed at her throat; a veil of
    bone beads hides her face but not the blue light of her eyes. Her staff is twisted ash with an iron ring at its
    head hung with rune discs round a heart of ice, and the runes she speaks burn in the air."""
    k = X.Kit("rune_seer")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(16, 10.4, 7.2), (20, 10.6, 7.2)], "wool", "waist")
    robe = k.part("robe", (0, 20, 0), (), "hips", bone=False)
    k.stack(robe, 0, -0.6, [(0.6, 15.0, 12.0), (8, 13.0, 10.0), (16, 11.0, 8.0), (20, 10.6, 7.4)], "wool", "robe")
    k.box(robe, C(0, 0.6, -0.6, 15.4, 1.2, 12.4), "fur_w", tag="hem")
    for i in range(-3, 4):                        # charms down the front: bones, teeth, a rune stone
        x = i * 1.8
        for y in range(18, 8 + abs(i), -2):
            k.box(robe, C(x, y, 4.6 + (18 - y) * 0.14, 0.9, 1.6 if i % 2 else 1.0, 0.8), "bone", tag="charm")
        k.box(robe, C(x, 7.6 + abs(i), 5.8, 1.4, 1.4, 0.6), "rune" if i % 3 == 0 else "frost", tag="charm_stone")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 2.8
        th = k.part("thigh_" + nm, (x, 19, 0), (), "hips")
        sh = k.part("shin_" + nm, (x, 10.4, 0), (), th)
        ft = k.part("foot_" + nm, (x, 2.4, 0), (), sh)
        k.box(ft, C(x, 0, 2.6, 3.8, 1.8, 5.4), "fur", tag="foot")
    # ---------------------------------------------------------------- torso: stooped under the white wolf's pelt
    to = k.part("torso", (0, 20, 0), (("x", 18),), "hips")
    k.stack(to, 0, 0, [(20, 10.4, 7.0), (25, 11.0, 7.0), (30, 13.0, 7.6), (34, 11.6, 7.0)], "wool", "chest")
    k.stack(to, 0, -0.8, [(14, 17, 11), (26, 17.6, 11.6), (33, 16.4, 10.8), (36, 12, 9.6)], "fur_w", "pelt")
    k.box(to, C(0, 22, 4.6, 6.0, 12.0, 1.4), "wool", tag="front")
    for sx in (-1, 1):                            # the wolf's forelegs crossed at her throat
        k.limb(to, (sx * 6.4, 34.6, 2.4), (-sx * 1.6, 31.4, 6.0), 2.4, "fur_w", "pelt_leg")
        for t in (-0.6, 0.6):
            k.shard(to, (-sx * 1.6 + t, 31.0, 6.8), (0, -1, 0.4), 1.4, 0.5, mat="dark", tag="pelt_claw")
    for i in range(7):                            # necklaces: teeth and rune stones
        a = math.radians(-60 + i * 20)
        k.box(to, C(math.sin(a) * 4.4, 29.0 - math.cos(a) * 1.4, 5.0, 0.9, 1.6, 0.8), "rune" if i == 3 else "bone", tag="necklace")
    # ---------------------------------------------------------------- the head: the wolf's jaws over her brow, a bead veil
    hd = k.part("head", (0, 34, 1.0), (("x", -14),), "torso")
    k.box(hd, C(0, 34.0, 1.0, 5.2, 6.0, 5.2), "dark", tag="face")
    for sx in (-1, 1):
        k.box(hd, C(sx * 1.2, 37.2, 3.55, 1.2, 0.7, 0.3), "eye", group="glow", tag="eye")
    for i in range(7):                            # the veil of bone beads
        x = -2.4 + i * 0.8
        for y in (35.4, 34.0, 32.6, 31.2):
            k.box(hd, C(x, y - (i % 2) * 0.5, 4.0, 0.5, 0.9, 0.5), "bone", tag="veil")
    k.blob(hd, (0, 38.6, 0.6), (4.4, 3.4, 4.6), "fur_w", "wolf_skull", step=0.7)
    k.box(hd, C(0, 37.6, 5.0, 4.4, 2.6, 5.6), "fur_w", tag="wolf_snout")
    k.box(hd, C(0, 39.6, 10.2, 1.6, 1.0, 0.8), "dark", tag="wolf_nose")
    for sx in (-1, 1):
        k.shard(hd, (sx * 1.4, 37.6, 9.8), (0, -1, 0.05), 2.2, 0.7, mat="bone", tag="wolf_fang")
        k.box(hd, C(sx * 2.0, 40.2, 4.4, 1.0, 0.6, 0.6), "dark", tag="wolf_eye")
        k.shard(hd, (sx * 2.6, 41.2, -0.6), (sx * 0.2, 1, -0.4), 3.4, 1.6, mat="fur_w", tag="wolf_ear")
    # ---------------------------------------------------------------- arms: the rune-ring staff, a rune burning in her hand
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 7.0
        up = k.part("arm_" + nm, (x, 32, 0), (("x", -56 if side > 0 else -20), ("z", side * 12)), "torso")
        fo = k.part("fore_" + nm, (x, 25, 0), (("x", -30 if side > 0 else -60),), up)
        hn = k.part("hand_" + nm, (x, 18, 0), (), fo)
        k.limb(up, (x, 31.4, 0), (x, 25.6, 0), 3.2, "fur_w", "sleeve")
        k.limb(fo, (x, 25, 0), (x, 19, 0), 2.6, "wool", "forearm")
        k.box(fo, C(x, 19.4, 0, 3.2, 1.6, 3.2), "bronze", tag="arm_ring")
        k.box(hn, C(x, 15.8, 0.4, 2.2, 3.0, 2.4), "dead", tag="hand")
        for t in (-0.6, 0.6):
            k.shard(hn, (x + t, 16.0, 1.4), (0, -1, 0.5), 2.0, 0.5, mat="bone", tag="nail")
    rn = k.part("rune_cast", (7.0, 13, 3), (), k.parts["hand_l"], bone=False)
    for (dx, dy, dz) in ((0, 0, 0), (-0.8, 2.6, -0.4), (0.8, 4.6, 0.4)):  # three runes burning in the air over her palm
        k.box(rn, C(7.0 + dx, 12.0 + dy, 3.2 + dz, 1.8, 0.4, 0.4), "rune", group="glow", tag="rune")
        k.box(rn, C(7.0 + dx, 11.2 + dy, 3.2 + dz, 0.4, 1.8, 0.4), "rune", group="glow", tag="rune")
        k.box(rn, C(7.0 + dx + 0.5, 12.2 + dy, 3.2 + dz, 0.4, 1.0, 0.4), "rune", group="glow", tag="rune")
    st = k.part("staff", (-7.0, 15.6, 0.6), (("x", 80),), k.parts["hand_r"], bone=False)
    for i in range(23):                           # twisted ash
        y = -6 + i * 2.0
        o = math.sin(i * 0.7) * 0.5
        k.box(st, C(-7.0 + o, y, 0.6 - o, 1.5, 2.1, 1.5), "wood", tag="staff")
    ring_c = (-7.0, 45.0, 0.6)
    for a in range(16):
        a0, a1 = a * math.pi / 8, (a + 1) * math.pi / 8
        k.limb(st, (ring_c[0], ring_c[1] + math.sin(a0) * 5.0, ring_c[2] + math.cos(a0) * 5.0),
               (ring_c[0], ring_c[1] + math.sin(a1) * 5.0, ring_c[2] + math.cos(a1) * 5.0), 1.0, "iron", "ring")
    for a in range(0, 360, 45):                   # rune discs of bone hung round the ring, a rune lit on each
        r = math.radians(a)
        y, z = ring_c[1] + math.sin(r) * 5.0, ring_c[2] + math.cos(r) * 5.0
        disc(k, st, (ring_c[0], y - 1.4, z), 1.2, "x", "bone", "rune_disc", thick=0.5)
        k.box(st, C(ring_c[0] + 0.3, y - 2.0, z, 0.3, 1.2, 0.3), "rune", group="glow", tag="disc_rune")
    k.box(st, C(-7.0, 39.4, 0.6, 1.4, 1.6, 1.4), "iron", tag="ring_post")
    crystals(k, st, (-7.0, 42.0, 0.6), 3, 6, 1.8, up=(0, 1, 0), seed=21)
    k.blob(st, (-7.0, 45.0, 0.6), (1.4, 1.6, 1.4), "rune", "heart", step=0.6)
    for b in k.s.boxes:
        if b.tag == "heart":
            b.group = "glow"
    for z in (-0.6, 0.6):
        k.chain(st, (-7.0, 40.0, z), (-7.0 + z * 2, 33, z * 3), 4, mat="iron", w=0.7)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Winter Wolf (elite, crawler)

def winter_wolf():
    """The jarl's hound keeps the stair to his hall. A white wolf the size of a horse, its ruff heavy with frost, ice
    grown down its spine in crystals; a black iron collar cut with runes that burn blue, its jaws open on fangs as
    long as daggers and the cold pouring out of its throat like light."""
    k = X.Kit("winter_wolf")
    body = k.part("body", (0, 17, 0))
    k.stack(body, 0, 1, [(9, 12, 16), (15, 15, 18), (22, 13, 16)], "fur_w", "chest", step=1.2)
    k.blob(body, (0, 19, 6), (8.4, 6.4, 6.4), "fur_w", "ruff", step=1.0)
    k.box(body, C(0, 9, 1, 11.4, 1.4, 14), "fur", tag="belly_shadow")
    for z, s in ((6, 1.0), (2, 1.2), (-2, 1.0), (-6, 0.8)):  # the ice along its spine
        k.cluster(body, (0, 22, z), 3, 7.0 * s, 2.0 * s, mat="ice", seed=int(z + 30), spread=0.5, up=(0, 1, -0.3))
    hd = k.part("head", (0, 19, 10), (("x", -12),), "body")
    k.ring(hd, 0, 16.6, 8.6, 5.6, 1.8, "iron", "collar", n=16, axis="z")
    for a in range(0, 360, 60):
        r = math.radians(a)
        k.box(hd, C(math.cos(r) * 5.6, 16.6 + math.sin(r) * 5.6 - 0.6, 9.5, 1.0, 1.2, 0.6), "rune", group="glow", tag="collar_rune")
    k.box(hd, C(0, 15.4, 13.4, 7.6, 7.2, 7.0), "fur_w", tag="head")
    k.blob(hd, (0, 19.6, 13.0), (3.6, 2.6, 3.6), "fur_w", "crown", step=0.7)
    for sx in (-1, 1):
        k.blob(hd, (sx * 4.2, 16.0, 12.4), (2.0, 3.4, 3.0), "fur_w", "cheek_ruff", step=0.7)
    k.box(hd, C(0, 16.0, 19.8, 4.4, 3.4, 7.0), "fur_w", tag="muzzle")
    k.box(hd, C(0, 18.6, 18.0, 3.4, 1.4, 3.6), "fur_w", tag="muzzle_bridge")
    k.box(hd, C(0, 18.6, 26.6, 2.0, 1.4, 0.8), "dark", tag="nose")
    k.limb(hd, (0, 14.0, 14.6), (0, 10.6, 24.6), 3.8, "fur_w", "jaw", d=4.0)
    k.limb(hd, (0, 15.2, 15.6), (0, 13.6, 25.0), 3.4, "mouth", "mouth", d=3.6)
    k.blob(hd, (0, 14.4, 22.0), (1.6, 1.2, 3.0), "rune", "frost_breath", step=0.6)
    for t in (-1.6, -0.6, 0.6, 1.6):
        k.shard(hd, (t, 16.2, 26.2 - abs(t) * 0.8), (0, -1, 0.05), 2.8 if abs(t) > 1 else 1.4, 0.7, mat="bone", tag="fang")
        k.shard(hd, (t, 11.4, 24.4 - abs(t) * 0.8), (0, 1, 0.1), 1.6 if abs(t) > 1 else 1.0, 0.6, mat="bone", tag="fang")
    for sx in (-1, 1):
        k.box(hd, C(sx * 2.4, 19.0, 16.75, 1.8, 0.7, 0.4), "eye", group="glow", tag="eye")
        k.limb(hd, (sx * 1.0, 19.9, 17.2), (sx * 3.4, 20.8, 16.4), 0.9, "fur", "brow")
        k.shard(hd, (sx * 2.6, 21.6, 11.4), (sx * 0.25, 0.8, -0.8), 4.8, 2.2, mat="fur_w", tag="ear")
    for b in k.s.boxes:
        if b.tag == "frost_breath":
            b.group = "glow"
    ab = k.part("abdomen", (0, 17, -8), (), "body")
    k.stack(ab, 0, -11, [(10, 9, 10), (15, 10.6, 11), (20, 9, 10)], "fur_w", "haunch")
    for z, s in ((-10, 0.8), (-14, 0.6)):
        k.cluster(ab, (0, 20, z), 2, 5.0 * s, 1.8 * s, mat="ice", seed=int(z + 50), spread=0.5, up=(0, 1, -0.5))
    tail = [(0, 18, -16), (0, 17, -21), (0, 14, -26), (0, 12, -29)]
    for (a, b), w in zip(zip(tail, tail[1:]), (4.0, 3.6, 2.6)):
        k.limb(ab, a, b, w, "fur_w", "tail")
    joints = {"body": "Root", "head": "Head", "abdomen": "Stomach"}
    for side, s in ((1, "l"), (-1, "r")):
        for i, (z, j, part) in enumerate(((6, 1, body), (-11, 4, ab))):
            nm = "leg_%s%d" % (s, i)
            lg = k.part(nm, (side * 5.4, 14, z), (), part)
            kn = (side * 6.0, 7.0, z + (1.6 if i == 0 else -2.8))
            k.limb(lg, (side * 5.4, 14, z), kn, 4.0, "fur_w", "leg")
            k.limb(lg, kn, (side * 6.0, 0.8, z + (0.8 if i == 0 else 0.4)), 3.0, "fur_w", "foot")
            k.box(lg, C(side * 6.0, 0, z + 1.4, 4.4, 1.8, 5.6), "fur_w", tag="foot")
            for t in (-1.2, 0, 1.2):
                k.shard(lg, (side * 6.0 + t, 0.6, z + 4.0), (0, -0.3, 1), 1.8, 0.7, mat="dark", tag="foot")
            joints[nm] = ("LL" if side > 0 else "RL") + str(j)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


# ================================================================ Jarl Hrimgar (boss)

def jarl_hrimgar():
    """The frost giant who took Rimeholt for his hall waits on its roof by his throne of ice. Ten blocks of him: a
    beard of ice hanging to his belt, white hair blown back, a crown of ice spikes in a band of black iron; a bare
    chest scarred with runes that burn blue, a harness of black lamellar, a white wolf's pelt for a mantle with the
    head on his shoulder; ice grown from his shoulders like the crystals that split his keep. His greataxe is black
    iron, its two bits edged with ice, as long as he is tall."""
    k = X.Kit("jarl_hrimgar")
    hips = k.part("hips", (0, 30, 0))
    k.stack(hips, 0, 0, [(22, 22, 15), (30, 24, 16)], "fur", "pelvis")
    k.box(hips, C(0, 28.6, 0, 26, 2.6, 17.4), "leather", tag="belt")
    disc(k, hips, (0, 30.0, 8.9), 3.0, "z", "bronze", "buckle", thick=1.0)
    k.box(hips, C(0, 29.6, 9.5, 2.4, 0.6, 0.4), "rune", group="glow", tag="buckle_rune")
    for x in (-9, -4.5, 0, 4.5, 9):               # a war-skirt of black lamellar strips
        k.stack(hips, x, 7.0 if abs(x) < 6 else 5.6, [(12, 4.2, 1.2), (28, 4.4, 1.2)], "iron", "skirt")
        for y in (16, 20, 24):
            k.box(hips, C(x, y, 7.8 if abs(x) < 6 else 6.4, 4.6, 0.5, 0.6), "dark", tag="lace")
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 7.4
        th = k.part("thigh_" + nm, (x, 28, 0), (("x", -6), ("z", side * 8)), "hips")
        sh = k.part("shin_" + nm, (x, 15.6, 0), (("x", 10),), th)
        ft = k.part("foot_" + nm, (x, 4, 0), (("x", -4),), sh)
        k.stack(th, x, 0, [(15.6, 9.6, 10.0), (28, 11.4, 11.8)], "wool", "thigh")
        k.stack(sh, x, 0, [(4, 10.0, 10.6), (15.6, 9.6, 10.2)], "fur", "boot")
        for y in (6, 9, 12):
            k.box(sh, C(x, y, 0, 10.6, 0.8, 11.0), "leather", tag="boot_band")
        k.box(sh, C(x, 6, 4.6, 8.0, 9.6, 1.6), "iron", tag="greave")
        k.box(ft, C(x, 0, 2.0, 11.4, 4.0, 16), "leather", tag="foot")
        k.box(ft, C(x, 3.4, 2.0, 11.8, 1.0, 16.2), "frost", tag="boot_frost")
    # ---------------------------------------------------------------- torso: bare, rune-scarred, the black harness
    to = k.part("torso", (0, 30, 0), (("x", 6),), "hips")
    k.stack(to, 0, 0, [(30, 24, 16), (36, 27, 17), (44, 34, 18.6), (52, 38, 18.6), (57, 31, 15.6)], "dead", "chest", step=1.2)
    for y in (33, 36):                            # the belly's slabs
        k.box(to, C(0, y, 8.6, 10.4, 0.6, 0.8), "dark", tag="ab_line")
    k.box(to, C(0, 41.4, 9.4, 18, 0.8, 0.8), "dark", tag="pec_line")
    for (p0, p1) in (((-3, 50, 9.4), (-9, 42, 9.6)), ((-9, 42, 9.6), (-6, 34, 8.8)), ((4, 49, 9.4), (10, 44, 9.6)),
                     ((10, 44, 9.6), (7, 37, 9.0)), ((7, 37, 9.0), (2, 33, 8.8)), ((0, 52, 9.2), (0, 45, 9.6))):
        k.limb(to, p0, p1, 0.8, "rune", "rune_scar", group="glow")
    k.limb(to, (15, 55, 8.6), (-11, 31, 9.4), 3.2, "iron", "harness", d=1.4)
    k.limb(to, (-15, 55, 8.6), (11, 31, 9.4), 3.2, "iron", "harness", d=1.4)
    disc(k, to, (0, 44.6, 10.0), 3.2, "z", "iron", "harness_boss", thick=1.2)
    k.box(to, C(0, 44.0, 10.8, 2.2, 1.2, 0.4), "rune", group="glow", tag="harness_rune")
    for sx in (-1, 1):                            # black iron pauldrons, rounded, two lames under each
        k.blob(to, (sx * 19.0, 55.0, 0), (7.4, 4.6, 8.6), "iron", "pauldron", step=0.9)
        for i in range(2):
            k.box(to, C(sx * (19.6 + i * 0.5), 49.6 - i * 2.4, 0, 8.6, 2.2, 14.6), "iron", tag="lame")
        k.shard(to, (sx * 20.4, 58.6, -1.0), (sx * 0.5, 1, -0.3), 6.0, 2.6, mat="iron", tag="pauldron_spike")
    k.blob(to, (0, 56.6, -2.0), (15.0, 3.6, 10.6), "fur_w", "mantle", step=0.9)
    cape = k.part("cape", (0, 57, -9), (("x", 4),), to, bone=False)
    k.stack(cape, 0, -9.6, [(12, 28, 1.6), (36, 30, 1.6), (57, 28, 1.8)], "fur", "cape")
    for i in range(-6, 7):
        k.shard(cape, (i * 2.2, 12.4, -9.6), (0, -1, 0), 3.0 + (i % 3) * 1.6, 2.4, mat="fur", tag="hem")
    wh = k.part("wolf_head", (14, 59, 2), (), to, bone=False)
    k.box(wh, C(14, 58.4, 2.6, 8.4, 6.2, 10.0), "fur_w", tag="pelt_head")
    k.box(wh, C(14, 58.2, 9.4, 5.2, 3.6, 5.4), "fur_w", tag="pelt_snout")
    for t in (-1.4, 1.4):
        k.shard(wh, (14 + t, 58.4, 14.4), (0, -1, 0.1), 2.6, 0.9, mat="bone", tag="pelt_fang")
        k.shard(wh, (14 + t * 1.6, 64.0, 0.4), (t * 0.2, 1, -0.4), 4.0, 2.0, mat="fur_w", tag="pelt_ear")
    k.box(wh, C(16.2, 61.4, 7.0, 1.2, 0.8, 0.6), "eye", group="glow", tag="pelt_eye")
    for sx, s in ((-1, 1.0), (1, 0.7)):           # the ice grown out of his shoulders
        crystals(k, to, (sx * 16, 58, -4), 5, 22 * s, 5.0 * s, up=(sx * 0.4, 1, -0.4), seed=31 + sx)
    crystals(k, to, (0, 54, -10), 4, 16, 4.2, up=(0, 0.8, -0.8), seed=37)
    # ---------------------------------------------------------------- the head: ice beard, ice crown
    hd = k.part("head", (0, 57, 2), (("x", -6),), "torso")
    k.blob(hd, (0, 63.4, 1.6), (6.4, 7.6, 6.6), "dead", "skull", step=0.9)
    k.box(hd, C(0, 56.6, 2.6, 10.6, 5.0, 9.6), "dead", tag="jaw")
    k.limb(hd, (-6.4, 66.6, 7.2), (6.4, 66.6, 7.2), 2.6, "dead", "brow", d=3.2)
    for sx in (-1, 1):
        k.box(hd, C(sx * 2.8, 63.8, 7.6, 3.4, 2.2, 0.8), "dark", tag="socket")
        k.box(hd, C(sx * 2.8, 64.2, 8.0, 2.6, 1.2, 0.5), "eye", group="glow", tag="eye")
        k.box(hd, C(sx * 6.6, 61.4, 2.0, 1.6, 4.4, 3.4), "dead", tag="ear")
        k.limb(hd, (sx * 1.2, 66.0, 8.4), (sx * 5.4, 67.6, 7.6), 1.2, "frost", "eyebrow")
    k.box(hd, C(0, 60.4, 7.6, 3.6, 5.0, 3.2), "dead", tag="nose")
    k.limb(hd, (-6.2, 59.0, 8.2), (6.2, 59.0, 8.2), 1.8, "frost", "moustache")
    for sx in (-1, 1):
        k.limb(hd, (sx * 5.6, 59.0, 8.2), (sx * 7.6, 51.0, 8.4), 1.8, "frost", "moustache")
    # the beard: a frozen wedge down over his chest to his belt, two braids bound in bronze, icicles off its end
    k.stack(hd, 0, 7.6, [(36, 5.0, 3.0), (44, 10.4, 4.4), (52, 13.6, 5.6), (58, 12.6, 5.0)], "frost", "beard")
    for i in range(-4, 5):
        k.box(hd, C(i * 1.4, 40 + abs(i) * 1.2, 9.6 + (0.4 if i % 2 else 0), 0.5, 14 - abs(i) * 1.0, 0.4), "ice", tag="beard_streak")
    for sx in (-1, 1):
        k.limb(hd, (sx * 5.4, 50, 8.6), (sx * 4.0, 32, 9.0), 2.2, "frost", "braid")
        for y in (44, 38):
            k.box(hd, C(sx * (4.0 + (y - 32) * 0.08), y, 8.8, 3.0, 1.4, 3.0), "bronze", tag="braid_ring")
    icicles(k, hd, [(x, 36.4 + abs(x) * 0.6, 7.6) for x in (-2.4, -1.2, 0, 1.2, 2.4)] + [(sx * 4.0, 32, 9.0) for sx in (-1, 1)], 7.0, 1.4, seed=8)
    k.stack(hd, 0, -1.6, [(56, 14.4, 11.0), (69, 14.0, 12.0), (71.4, 11.6, 10)], "frost", "hair")
    for i in range(-3, 4):                        # hair blown back over the mantle
        k.limb(hd, (i * 1.8, 68, -6), (i * 2.4, 54, -11), 2.0, "frost", "hair_lock")
    k.box(hd, C(0, 69.6, 2.0, 14.2, 2.2, 13.6), "iron", tag="crown")
    for i, x in enumerate((-6, -3.6, -1.2, 1.2, 3.6, 6)):
        k.shard(hd, (x, 71.6, 7.0 - abs(x) * 0.4), (x * 0.06, 1, 0.1), 8.0 - abs(x) * 0.6 + (2 if i in (2, 3) else 0), 2.0, mat="ice", tag="crown_spike")
    for z in (-1, -5):
        for x in (-6, 6):
            k.shard(hd, (x, 71.6, z), (x * 0.08, 1, -0.2), 5.6, 1.8, mat="ice", tag="crown_spike")
    k.box(hd, C(0, 70.2, 8.9, 2.0, 1.2, 0.4), "rune", group="glow", tag="crown_rune")
    # ---------------------------------------------------------------- arms: the greataxe in both hands
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 21.0
        up = k.part("arm_" + nm, (x, 53, 0), (("x", -30), ("z", side * 10)), "torso")
        fo = k.part("fore_" + nm, (x, 38, 0), (("x", -64 if side > 0 else -50), ("y", side * 24)), up)
        hn = k.part("hand_" + nm, (x, 23, 0), (), fo)
        k.blob(up, (x - side * 1.0, 53, 0), (7.6, 6.0, 8.0), "dead", "shoulder", step=1.0)
        k.limb(up, (x, 51, 0), (x, 39, 0), 8.4, "dead", "upper_arm")
        k.box(up, C(x, 44, 0, 9.2, 2.0, 9.2), "bronze", tag="arm_ring")
        k.limb(up, (x, 50, 4.4), (x - side * 1.6, 41, 4.4), 0.8, "rune", "arm_rune", group="glow")
        k.limb(fo, (x, 37.6, 0), (x, 25.4, 0), 7.6, "dead", "forearm")
        k.box(fo, C(x, 25.0, 0, 8.8, 8.0, 8.8), "iron", tag="vambrace")
        for y in (27, 30):
            k.box(fo, C(x, y, 0, 9.4, 0.8, 9.4), "frost", tag="vambrace_frost")
        k.box(hn, C(x, 18.4, 0.6, 7.6, 6.4, 8.0), "leather", tag="gauntlet")
    ax = k.part("greataxe", (-21, 20.4, 0.6), (("x", 66),), k.parts["hand_r"], bone=False)
    k.limb(ax, (-21, -12, 0.6), (-21, 70, 0.6), 2.8, "wood", "haft")
    for y in (-10, 8, 26, 44):
        k.box(ax, C(-21, y, 0.6, 3.8, 2.2, 3.8), "iron", tag="haft_band")
    k.chain(ax, (-21, -10, 2.4), (-19, -18, 4.0), 3, mat="iron", w=1.2)
    # one great bearded bit: a crescent whose horns sweep past the socket, edged with ice; a spike behind
    rows = 22
    for i in range(rows):
        t_ = i / (rows - 1)
        y = 44 + i * 1.6
        z_out = 1.6 + 4.0 + 15.0 * math.sin(t_ * math.pi) ** 0.5
        off = abs(t_ - 0.5)
        z_in = 1.6 if off < 0.2 else 1.6 + (off - 0.2) / 0.3 * (z_out - 4.0)
        if z_out - z_in < 1.0:
            continue
        k.box(ax, C(-21, y, 0.6 + (z_in + z_out) / 2 - 0.7, 1.6, 1.65, z_out - z_in - 1.4), "iron", tag="bit")
        k.box(ax, C(-21, y, 0.6 + z_out - 0.7, 1.9, 1.65, 1.6), "ice", tag="bit_edge")
    k.box(ax, C(-21, 52, 0.6, 3.6, 12, 4.2), "iron", tag="socket")
    k.limb(ax, (-21, 56, 4.6), (-21, 62, 10.6), 0.9, "rune", "bit_rune", group="glow")
    k.limb(ax, (-21, 62, 10.6), (-21, 66, 6.6), 0.9, "rune", "bit_rune", group="glow")
    k.shard(ax, (-21, 58, -1.4), (0, 0.15, -1), 9.0, 3.0, mat="iron", tag="back_spike")
    k.shard(ax, (-21, 74, 0.6), (0, 1, 0), 7.0, 2.4, mat="ice", tag="spike")
    legs = {id(k.parts[n]) for n in k.parts if n.split("_")[0] in ("thigh", "shin", "foot")}
    lift, f = 9.0, 1.3
    for b in k.s.boxes:
        if id(b.part) in legs:
            b.lo = (b.lo[0], b.lo[1] * f, b.lo[2])
            b.size = (b.size[0], b.size[1] * f, b.size[2])
            b.pivot = (b.pivot[0], b.pivot[1] * f, b.pivot[2])
        else:
            b.lo = (b.lo[0], b.lo[1] + lift, b.lo[2])
            b.pivot = (b.pivot[0], b.pivot[1] + lift, b.pivot[2])
    seen = set()
    for b in k.s.boxes:
        seen.add(id(b.part))
    for p in list(k.parts.values()) + [b.part for b in k.s.boxes]:
        if id(p) in seen and getattr(p, "_lifted", False):
            continue
        if getattr(p, "_lifted", False):
            continue
        p.pivot = (p.pivot[0], p.pivot[1] * f, p.pivot[2]) if id(p) in legs else (p.pivot[0], p.pivot[1] + lift, p.pivot[2])
        p._lifted = True
    grow(k, 1.45)
    k.s.shaders = shaders()
    return k.s, k.parts


MOBS = {
    "rime_thrall": dict(make=rime_thrall, ent=(0.9, 2.6), stats=dict(hp=30, speed=0.26, dmg=8, armor=4, kb=0)),
    "frost_troll": dict(make=frost_troll, ent=(2.1, 4.2), stats=dict(hp=200, speed=0.2, dmg=22, armor=12, kb=1.0)),
    "huskarl": dict(make=huskarl, ent=(1.2, 3.3), stats=dict(hp=96, speed=0.24, dmg=14, armor=13, kb=0.6)),
    "rune_seer": dict(make=rune_seer, ent=(0.9, 2.8), stats=dict(hp=52, speed=0.22, dmg=9, armor=3, kb=0)),
    "winter_wolf": dict(make=winter_wolf, rig="crawler", ent=(2.2, 2.6), stats=dict(hp=320, speed=0.38, dmg=18, armor=8, kb=0.7), key=True),
    "jarl_hrimgar": dict(make=jarl_hrimgar, texel=1, ent=(3.8, 9.6), stats=dict(hp=1300, speed=0.21, dmg=30, armor=16, kb=1.0), boss=True),
}
