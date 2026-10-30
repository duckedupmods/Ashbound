"""The Black Banner's monsters, the brigands who hold the world's big ruins (bandit towers, outposts, forts, camps),
each built by hand (tools/vox2.py). Once a lord's company; they went unpaid one winter too many, hanged their
captain from his own gate and kept the colours: mustard yellow and black, and on every tabard and shield the Black
Hand, the print of the hand that hanged him. Blackened leather and dented steel, mail gone brown, dirty yellow cloth,
brass where they've looted it, the amber of their eyes in the shadow of their helms.

    banner_hound    swarm   a war mastiff in a spiked collar and a yellow barding with the Hand on it, an iron
                            muzzle-cage hanging open off its jaw
    deserter        guard   a soldier who kept his kit: a kettle hat pulled down to the eyes, a mail coif, a steel
                            bevor over the mouth, the yellow tabard torn, a bill-hook as tall as he is
    arbalest        ranged  a crossbowman in a hounskull: a visor drawn out to a pig's snout, a brigandine studded
                            with brass, a heavy windlass crossbow, the pavise on his back painted with the Hand
    hatchetman      skirm   bare-armed in a black hood and a black iron devil's mask with stubs of horns, a harness
                            of straps and throwing axes, two bearded hatchets
    anvil_breaker   brute   the company's giant: plates of three dead men's armour beaten over him, a great sallet
                            with a slit, chains round his forearms and a smith's anvil on a pole for a maul
    banner_captain  elite   the one who took the captain's place: blackened plate edged in brass, an armet under a
                            storm of black plumes, a wolf-fur mantle, the Hand on his cloak, a flamberge

    python tools/monsterforge.py black_banner --preview ; python tools/mobsheet.py black_banner
"""
import math

import vox2 as X
from vox2 import C, ramp
from serpent_ziggurat import grow

OCHRE = ramp("#2a1e06", "#44320a", "#644a10", "#866418", "#a47e22", "#c09a32")
BLACKC = ramp("#08080a", "#0e0e10", "#151417", "#1c1b1f", "#252328", "#2e2c32")
LEATHER = ramp("#0e0a08", "#17110d", "#211813", "#2c2019", "#3a2a20", "#4a3628")
STEEL = ramp("#0a0b0d", "#121418", "#1b1e23", "#262a31", "#333841", "#444a55", "#5c6370")
BLADE = ramp("#1e232a", "#323a44", "#4c5664", "#6c7888", "#929eae", "#bcc6d2", "#e0e6ee")
MAIL = ramp("#100e0c", "#1c1814", "#28221c", "#362e24", "#463c2e")
RUST = ramp("#140a06", "#24120a", "#361c10", "#4a2816", "#60361e")
BRASS = ramp("#241806", "#3e2c0c", "#5e4414", "#80601e", "#a4802c", "#c8a444")
SKIN = ramp("#3a261c", "#583a2a", "#76503a", "#946a4e", "#b08464", "#c89e7e")
FUR = ramp("#1e1c1a", "#302c28", "#46403a", "#5e564e", "#7a7064", "#9a8e80")
DOG = ramp("#140e0a", "#22180f", "#322216", "#442e1e", "#583c28", "#6e4e34")
WOOD = ramp("#0e0a07", "#18110c", "#241a12", "#322418", "#40301f")
AMBER = ramp("#5a2a04", "#8a4a08", "#c07a12", "#f0a828", "#ffd060", "#fff0b0")
GORE = ramp("#0a0606", "#140c0c", "#201414", "#2c1c1a")


def _mail(p, n, i, j, w, h):
    """rings: a dark stitch in rows, each row offset"""
    return -0.2 if (i + (j % 2)) % 2 == 0 and j % 2 == 0 else 0.05


def shaders():
    return {
        "ochre": X.surf(OCHRE, 0.5, 1.1, 0.22, 0.04, holes=True, drip=(LEATHER, 0.12)),
        "black": X.surf(BLACKC, 0.5, 1.0, 0.18, 0.02, holes=True),
        "leather": X.surf(LEATHER, 0.5, 1.2, 0.22, 0.08),
        "steel": X.surf(STEEL, 0.54, 1.5, 0.12, 0.26, rust=(RUST, 0.16, 0.5)),
        "iron": X.surf(STEEL, 0.5, 1.4, 0.14, 0.22, rust=(RUST, 0.3, 0.5)),
        "blacksteel": X.surf(STEEL, 0.36, 1.5, 0.1, 0.3),
        "blade": X.surf(BLADE, 0.56, 1.6, 0.06, 0.34),
        "mail": X.surf(MAIL, 0.5, 1.2, 0.1, 0.0, pattern=_mail),
        "rust": X.surf(RUST, 0.5, 1.3, 0.22, 0.14),
        "brass": X.surf(BRASS, 0.56, 1.4, 0.12, 0.22),
        "skin": X.wrinkled(SKIN, 0.4),
        "fur": X.surf(FUR, 0.5, 1.0, 0.28, 0.0, stripe=2),
        "dog": X.surf(DOG, 0.5, 1.1, 0.26, 0.02, pattern=lambda p, n, i, j, w, h: -0.12 if i % 3 == 0 else 0.03),
        "wood": X.surf(WOOD, 0.5, 1.0, 0.2, 0.06, stripe=3),
        "sigil": X.surf(BLACKC, 0.3, 0.8, 0.04, 0.0),
        "eye": X.glow(AMBER, 0.8, 0.16),
        "ember": X.glow(AMBER),
        "mouth": X.dark(GORE),
        "dark": X.dark(BLACKC),
    }


GLOWS = {"eye", "ember"}


def lit(k):
    for b in k.s.boxes:
        if b.mat in GLOWS:
            b.group = "glow"


# ================================================================ shared brushes

def black_hand(k, part, c, s=1.0, facing=1, axis="z"):
    """the company's mark: a black hand print, fingers up, painted on yellow. facing: which way the face points
    along its axis; axis 'z' (on a chest or a shield facing front) or 'x' (on a flank)"""
    cx, cy, cz = c

    def at(dx, y, sx, sy):
        if axis == "z":
            return C(cx + dx, y, cz, sx, sy, 0.3)
        return C(cx, y, cz + dx * facing, 0.3, sy, sx)
    k.box(part, at(0, cy - 1.4 * s, 3.2 * s, 3.0 * s), "sigil", tag="hand_mark")
    for i, (dx, L) in enumerate(((-1.2, 2.2), (-0.4, 2.8), (0.4, 3.0), (1.2, 2.4))):
        k.box(part, at(dx * s, cy + 1.5 * s, 0.6 * s, L * s), "sigil", tag="hand_mark")
    k.box(part, at(-2.2 * s, cy - 0.6 * s, 1.4 * s, 0.7 * s), "sigil", tag="hand_mark")
    for i in range(3):                            # paint run down from the palm
        k.box(part, at((-0.9 + i * 0.9) * s, cy - (2.4 + i % 2 * 1.2) * s, 0.4 * s, (1.2 + i % 2 * 1.2) * s), "sigil", tag="hand_drip")


def straps(k, part, a, b, w=1.0, mat="leather"):
    k.limb(part, a, b, w, mat, "strap", d=0.5)


def eyes(k, part, y, z, gap=1.5, w=1.1):
    for sx in (-1, 1):
        k.box(part, C(sx * gap, y, z, w, 0.6, 0.3), "eye", tag="eye")


def legs(k, hips, top, knee, x, hose="black", boot="leather", knee_mat="steel", lean=-6, bend=8, th_w=5.4):
    """two legs for a man: hose, knee cop, boot"""
    for side, nm in ((1, "l"), (-1, "r")):
        xx = side * x
        th = k.part("thigh_" + nm, (xx, top, 0), (("x", lean), ("z", side * 3)), hips)
        sh = k.part("shin_" + nm, (xx, knee, 0), (("x", bend),), th)
        ft = k.part("foot_" + nm, (xx, 2.4, 0), (("x", -2),), sh)
        k.stack(th, xx, 0, [(knee + 0.2, th_w - 0.6, th_w - 0.2), (top, th_w + 0.4, th_w + 0.8)], hose, "hose")
        k.box(th, C(xx, knee - 0.8, 1.2, th_w - 0.4, 2.4, th_w - 0.8), knee_mat, tag="knee")
        k.shard(th, (xx, knee + 0.4, th_w * 0.5 + 0.8), (0, 0.4, 1), 1.4, 1.0, mat=knee_mat, tag="knee_point")
        k.stack(sh, xx, 0, [(2.4, th_w - 0.6, th_w - 0.2), (knee, th_w, th_w + 0.4)], boot, "boot")
        k.box(sh, C(xx, knee - 1.8, 0, th_w + 0.8, 2.0, th_w + 1.2), boot, tag="boot_cuff")
        k.box(sh, C(xx, 5.0, 0, th_w + 0.2, 0.8, th_w + 0.6), "brass" if boot == "leather" else "leather", tag="boot_strap")
        k.box(ft, C(xx, 0, 1.4, th_w, 2.6, th_w + 2.4), boot, tag="foot")
        k.box(ft, C(xx, 0, th_w * 0.5 + 2.2, th_w - 0.8, 1.6, 1.2), "steel" if knee_mat == "steel" else boot, tag="foot")


def arms(k, to, x, top, mat, rots, sleeve=None, glove="leather", w=4.0):
    """two arms; rots: {side: (arm rots, fore rots)}"""
    for side, nm in ((1, "l"), (-1, "r")):
        xx = side * x
        ar, fr = rots[side]
        up = k.part("arm_" + nm, (xx, top, 0), ar, to)
        fo = k.part("fore_" + nm, (xx, top - 8, 0), fr, up)
        hn = k.part("hand_" + nm, (xx, top - 15.6, 0), (), fo)
        k.limb(up, (xx, top - 0.6, 0), (xx, top - 7.6, 0), w, sleeve or mat, "upper_arm")
        k.limb(fo, (xx, top - 8.2, 0), (xx, top - 14.6, 0), w - 0.4, mat, "forearm")
        k.box(hn, C(xx, top - 18.4, 0.3, w - 0.4, 3.4, w), glove, tag="glove")


# ================================================================ the Banner Hound (swarm)

def banner_hound():
    """The company runs mastiffs ahead of it: broad as a barrel, jowls and scars, a collar of iron spikes, a yellow
    barding over the back with the Black Hand on each flank, and the iron muzzle-cage they only close on it in
    town, hanging open off its jaw on a broken strap."""
    k = X.Kit("banner_hound")
    body = k.part("body", (0, 14, 0))
    k.stack(body, 0, 1, [(7, 11, 13), (12, 14, 15), (18, 12.4, 13.6)], "dog", "chest", step=1.2)
    k.box(body, C(0, 7.4, 1, 10, 1.2, 12), "leather", tag="belly_shadow")
    # the barding: a yellow cloth over the back, black-hemmed, the Hand on each flank
    k.box(body, C(0, 17.6, -0.4, 14.4, 1.4, 14.6), "ochre", tag="barding")
    for sx in (-1, 1):
        k.box(body, C(sx * 7.3, 10.2, -0.4, 0.8, 8.4, 14.6), "ochre", tag="barding")
        k.box(body, C(sx * 7.4, 10.0, -0.4, 0.9, 1.0, 14.8), "black", tag="barding_hem")
        for z in (-5, 0, 5):
            k.box(body, C(sx * 7.5, 8.6, z, 1.0, 1.8, 2.6), "black", tag="barding_tab")
        black_hand(k, body, (sx * 7.8, 14.0, 0.6), 0.9, facing=sx, axis="x")
    k.box(body, C(0, 18.9, -0.4, 2.0, 0.6, 14.6), "black", tag="barding_stripe")
    hd = k.part("head", (0, 16, 8), (("x", -6),), "body")
    # the collar: thick leather, a ring of iron spikes standing out of it
    k.ring(hd, 0, 14.2, 7.4, 6.0, 2.2, "leather", "collar", n=16, axis="z")
    for a in range(0, 360, 36):
        r = math.radians(a)
        k.shard(hd, (math.cos(r) * 6.4, 14.2 + math.sin(r) * 6.4, 7.6), (math.cos(r), math.sin(r), 0.2), 2.6, 1.0, mat="steel", tag="collar_spike")
    k.ring(hd, 0, 8.4, 8.6, 1.2, 0.6, "brass", "collar_ring", n=8, axis="x")
    k.box(hd, C(0, 12.4, 11.4, 8.6, 8.0, 7.4), "dog", tag="head")
    k.blob(hd, (0, 18.6, 11.0), (3.8, 1.8, 3.6), "dog", "brow_mass", step=0.7)
    for sx in (-1, 1):                            # the jowls hanging, cropped ears
        k.blob(hd, (sx * 3.6, 11.4, 15.8), (1.8, 2.6, 2.6), "dog", "jowl", step=0.6)
        k.box(hd, C(sx * 3.4, 20.0, 9.6, 1.8, 2.4, 1.6), "dog", tag="ear")
        k.box(hd, C(sx * 2.3, 17.2, 15.2, 1.6, 0.7, 0.4), "eye", tag="eye")
        k.limb(hd, (sx * 0.8, 18.4, 15.0), (sx * 3.6, 17.8, 14.8), 1.0, "dog", "brow")
    k.box(hd, C(0, 12.8, 15.6, 5.8, 4.4, 4.4), "dog", tag="muzzle")
    k.box(hd, C(0, 16.4, 19.6, 2.4, 1.2, 0.6), "dark", tag="nose")
    k.box(hd, C(-1.2, 14.0, 13.0, 0.5, 4.0, 0.4), "mouth", tag="scar")
    k.limb(hd, (0, 11.4, 12.4), (0, 9.0, 19.4), 5.0, "dog", "jaw", d=3.0)
    k.limb(hd, (0, 12.4, 13.0), (0, 11.0, 19.4), 4.4, "mouth", "mouth", d=2.6)
    for t in (-2.0, -0.7, 0.7, 2.0):
        k.shard(hd, (t, 12.8, 19.6), (0, -1, 0.05), 2.4 if abs(t) > 1 else 1.2, 0.7, mat="steel" if t == -2.0 else "dark", tag="fang")
        k.shard(hd, (t, 9.8, 19.0), (0, 1, 0.1), 1.8 if abs(t) > 1 else 1.0, 0.6, mat="dark", tag="fang")
    for b in k.s.boxes:                           # fangs: bone-pale, not black
        if b.tag == "fang" and b.mat == "dark":
            b.mat = "brass"
    # the muzzle cage, open, swinging under the jaw off one strap
    cg = k.part("cage", (0, 9.0, 14.0), (("x", 28),), hd, bone=False)
    for x in (-2.6, 0, 2.6):
        k.limb(cg, (x, 9.0, 14.0), (x, 4.6, 19.0), 0.6, "steel", "cage_bar")
    for t in (0.4, 0.9):
        k.limb(cg, (-2.8, 9.0 - 4.4 * t, 14.0 + 5.0 * t), (2.8, 9.0 - 4.4 * t, 14.0 + 5.0 * t), 0.6, "steel", "cage_hoop")
    straps(k, hd, (3.6, 12.6, 12.0), (3.0, 9.6, 14.6), 0.8)
    ab = k.part("abdomen", (0, 14, -6), (), "body")
    k.stack(ab, 0, -9, [(8, 10.6, 10), (12.6, 12, 11), (17, 10.4, 9.6)], "dog", "haunch")
    k.box(ab, C(0, 16.4, -9.0, 12.4, 1.2, 10.6), "ochre", tag="barding")
    k.box(ab, C(0, 17.0, -9.0, 2.0, 0.6, 10.6), "black", tag="barding_stripe")
    tail = [(0, 16, -14), (0, 17.6, -17), (0, 18.6, -19)]
    for (a, b), w in zip(zip(tail, tail[1:]), (2.6, 2.0)):
        k.limb(ab, a, b, w, "dog", "tail")
    joints = {"body": "Root", "head": "Head", "abdomen": "Stomach"}
    for side, s in ((1, "l"), (-1, "r")):
        for i, (z, j, part) in enumerate(((5, 1, body), (-9, 4, ab))):
            nm = "leg_%s%d" % (s, i)
            lg = k.part(nm, (side * 5.0, 11, z), (), part)
            kn = (side * 5.6, 5.6, z + (1.4 if i == 0 else -2.4))
            k.limb(lg, (side * 5.0, 11, z), kn, 4.4, "dog", "leg")
            k.limb(lg, kn, (side * 5.6, 0.8, z + (0.8 if i == 0 else 0.4)), 3.4, "dog", "foot")
            k.box(lg, C(side * 5.6, 0, z + 1.4, 4.6, 1.8, 5.4), "dog", tag="foot")
            for t in (-1.2, 0, 1.2):
                k.shard(lg, (side * 5.6 + t, 0.6, z + 3.8), (0, -0.3, 1), 1.4, 0.6, mat="dark", tag="foot")
            joints[nm] = ("LL" if side > 0 else "RL") + str(j)
    lit(k)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


# ================================================================ the Deserter (guard)

def deserter():
    """The Banner's rank and file kept their soldiers' kit and lost everything else. A kettle hat pulled down so
    low the eyes are two embers under its brim, a mail coif, a steel bevor over the mouth, the yellow tabard torn
    to the waist with the Black Hand on it, mail gone brown under it, and a bill-hook: a blade, a spike and a hook
    for pulling riders off horses, on a pole as tall as he is."""
    k = X.Kit("deserter")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(11, 11.8, 8.2), (20, 11.2, 7.6)], "mail", "mail_skirt")
    for z, lean in ((4.3, 5), (-4.3, -5)):        # the tabard's skirts, front and back, torn into tails
        tp = k.part("tabard_" + ("f" if z > 0 else "b"), (0, 20, z), (("x", lean),), hips, bone=False)
        for i, x in enumerate((-3.6, -1.2, 1.2, 3.6)):
            L = (11.0, 13.0, 10.0, 12.4)[i]
            k.box(tp, C(x, 20 - L, z, 2.4, L, 0.7), "ochre" if z > 0 else "black", tag="tabard")
        k.box(tp, C(0, 19.0, z + 0.1, 9.8, 1.2, 0.8), "black", tag="tabard_hem")
    k.box(hips, C(0, 19.2, 0, 12.4, 1.8, 8.8), "leather", tag="belt")
    k.box(hips, C(0, 19.0, 4.5, 2.0, 2.2, 0.6), "brass", tag="buckle")
    k.box(hips, C(-6.4, 13.4, -1.0, 1.4, 6.0, 1.8), "leather", tag="sheath")
    k.box(hips, C(-6.4, 19.4, -1.0, 1.6, 2.4, 1.4), "brass", tag="dagger_pommel")
    legs(k, hips, 19, 10.4, 3.4)
    to = k.part("torso", (0, 20, 0), (("x", 5),), "hips")
    k.stack(to, 0, 0, [(20, 11.4, 7.8), (25, 12.8, 8.2), (30, 15.0, 8.8), (34, 15.4, 8.4)], "mail", "hauberk")
    k.box(to, C(0, 20.4, 4.2, 10.4, 12.6, 0.8), "ochre", tag="tabard")
    k.box(to, C(0, 20.4, -4.4, 10.4, 12.6, 0.8), "black", tag="tabard")
    for sx in (-1, 1):
        k.box(to, C(sx * 5.4, 20.4, 0, 0.8, 12.6, 9.0), "black", tag="tabard_side")
    k.box(to, C(3.4, 28.0, 4.7, 2.0, 4.0, 0.3), "dark", tag="tear")
    black_hand(k, to, (-0.6, 27.0, 4.7), 1.0)
    straps(k, to, (6.4, 33.6, 4.4), (-5.4, 21.0, 4.8), 1.2)   # a baldric across it
    for sx in (-1, 1):                            # spaulders: three lames, the yellow cloth tied under them
        for i in range(3):
            k.box(to, C(sx * (8.0 + i * 0.4), 33.4 - i * 2.0, 0, 5.4 - i * 0.6, 1.8, 8.4 - i * 0.6), "steel", tag="spaulder")
        k.box(to, C(sx * 8.6, 28.4, 0, 4.4, 1.6, 5.2), "ochre", tag="armband")
    k.box(to, C(0, 33.6, 1.0, 8.4, 2.4, 8.4), "mail", tag="coif_neck")
    hd = k.part("head", (0, 34, 0.6), (("x", -4),), "torso")
    k.box(hd, C(0, 34.4, 0.8, 6.6, 6.8, 6.6), "skin", tag="face")
    k.box(hd, C(0, 34.2, 0.6, 7.6, 7.4, 7.0), "mail", tag="coif")          # the coif round it (the face shows through the front)
    k.box(hd, C(0, 37.6, 4.05, 5.2, 2.6, 0.4), "skin", tag="face_front")
    k.box(hd, C(0, 38.5, 4.25, 5.4, 1.0, 0.3), "dark", tag="brim_shadow")
    eyes(k, hd, 38.0, 4.3, 1.4, 1.2)
    k.box(hd, C(0, 33.0, 2.0, 8.4, 4.4, 5.2), "steel", tag="bevor")        # steel up over the mouth
    k.box(hd, C(0, 37.2, 4.8, 8.0, 0.6, 0.4), "steel", tag="bevor_edge")
    for x in (-2.2, 0, 2.2):
        k.box(hd, C(x, 34.6, 4.65, 0.8, 0.8, 0.3), "dark", tag="breath")
    # the kettle hat: a low dome and a broad brim tipped down over the eyes
    k.blob(hd, (0, 41.6, 0.6), (4.2, 2.2, 4.2), "steel", "hat_crown", step=0.6)
    br = k.part("brim", (0, 40.2, 0.6), (("x", 8),), hd, bone=False)
    k.box(br, C(0, 40.0, 0.6, 14.0, 0.8, 14.0), "steel", tag="brim")
    k.box(br, C(0, 39.6, 0.6, 14.6, 0.5, 14.6), "rust", tag="brim_edge")
    k.box(hd, C(0, 40.6, 0.6, 9.0, 1.0, 9.0), "brass", tag="hat_band")
    k.box(hd, C(3.6, 41.0, 3.6, 1.6, 1.6, 0.4), "dark", tag="dent")
    arms(k, to, 8.4, 32, "mail", {1: ((("x", -30), ("z", 10)), (("x", -48),)), -1: ((("x", -44), ("z", -6)), (("x", -40),))},
         sleeve="mail")
    for side in (1, -1):
        k.box(k.parts["fore_" + ("l" if side > 0 else "r")], C(side * 8.4, 17.6, 0, 4.6, 5.0, 4.6), "steel", tag="vambrace")
    # the bill-hook: held in both hands, the head high and forward
    bl = k.part("bill", (-8.4, 14.6, 0.4), (("x", 104), ("z", 6)), k.parts["hand_r"], bone=False)
    k.limb(bl, (-8.4, -6.0, 0.4), (-8.4, 40.0, 0.4), 1.4, "wood", "pole")
    for y in (8.0, 20.0, 30.0):
        k.box(bl, C(-8.4, y, 0.4, 1.8, 1.0, 1.8), "leather", tag="pole_wrap")
    k.box(bl, C(-8.4, -7.0, 0.4, 1.8, 1.6, 1.8), "steel", tag="butt_cap")
    k.box(bl, C(-8.4, 38.0, 0.4, 2.0, 3.0, 2.0), "steel", tag="socket")
    k.box(bl, C(-8.4, 41.0, 2.4, 1.0, 9.0, 4.4), "blade", tag="bill_blade")   # the broad blade, curving forward at its top
    k.box(bl, C(-8.4, 46.6, 4.6, 1.0, 3.0, 2.4), "blade", tag="bill_blade")
    k.box(bl, C(-8.4, 41.0, 4.4, 1.1, 8.0, 0.6), "blade", tag="edge")
    k.shard(bl, (-8.4, 44.0, 0.4), (0, 1, 0), 9.0, 1.4, mat="blade", tag="top_spike")
    k.shard(bl, (-8.4, 42.0, -0.4), (0, 0.5, -1), 4.4, 1.2, mat="steel", tag="back_hook")
    k.shard(bl, (-8.4, 41.0, 4.4), (0, -0.4, 1), 3.4, 1.0, mat="steel", tag="lug")
    k.box(bl, C(-8.4, 34.4, 0.4, 0.3, 3.4, 2.6), "ochre", tag="pennon")
    lit(k)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Arbalest (ranged)

def arbalest():
    """The Banner's crossbowmen shoot from behind the pavises they carry on their backs. A hounskull bascinet with
    its visor drawn out into a pig's snout, pierced for breath, and a slit across the eyes; a brigandine of black
    leather studded with brass rivets, a quiver of bolts at the hip, and a heavy steel crossbow with a windlass
    on its butt - they wind it in their sleep."""
    k = X.Kit("arbalest")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(12.4, 11.4, 8.0), (20, 11.0, 7.4)], "leather", "brigandine_skirt")
    for x in (-3.6, 0, 3.6):
        k.box(hips, C(x, 14.0, 3.9, 0.7, 0.7, 0.4), "brass", tag="rivet")
    k.box(hips, C(0, 19.2, 0, 12.2, 1.8, 8.6), "leather", tag="belt")
    k.box(hips, C(0, 13.0, 4.0, 4.2, 7.4, 0.6), "ochre", tag="tabard_tail")
    # the quiver, bolts' fletchings standing out of it
    k.box(hips, C(6.8, 10.0, -1.4, 3.0, 9.6, 3.4), "leather", tag="quiver")
    for i in range(5):
        k.box(hips, C(6.2 + (i % 3) * 0.6, 19.6, -2.6 + i * 0.6, 0.5, 2.0 + (i % 2) * 0.6, 0.5), "ochre" if i % 2 else "black", tag="fletching")
    legs(k, hips, 19, 10.4, 3.4, hose="leather")
    to = k.part("torso", (0, 20, 0), (("x", 6),), "hips")
    k.stack(to, 0, 0, [(20, 11.4, 7.8), (25, 12.6, 8.4), (30, 14.4, 9.0), (34, 14.8, 8.6)], "leather", "brigandine")
    for y in (22, 25, 28, 31):                    # rows of brass rivets holding the plates inside it
        for x in (-4.6, -2.3, 0, 2.3, 4.6):
            k.box(to, C(x + (y % 2) * 0.6, y, 4.3 + (y - 22) * 0.08, 0.7, 0.7, 0.4), "brass", tag="rivet")
    k.box(to, C(0, 32.4, 0, 12.0, 2.0, 9.2), "mail", tag="mail_collar")
    for sx in (-1, 1):
        k.blob(to, (sx * 7.8, 32.0, 0), (2.8, 2.2, 3.4), "leather", "shoulder", step=0.7)
    straps(k, to, (5.6, 33.6, 4.6), (-5.4, 21.0, 4.6), 1.2)
    # the pavise on his back: a tall shield, yellow, the Black Hand on it, black at its rim
    pv = k.part("pavise", (0, 30, -5.6), (("x", -6),), to, bone=False)
    k.box(pv, C(0, 13.6, -6.2, 13.0, 23.0, 1.2), "ochre", tag="pavise")
    k.box(pv, C(0, 13.4, -6.2, 13.8, 0.9, 1.4), "black", tag="pavise_rim")
    k.box(pv, C(0, 36.2, -6.2, 13.8, 0.9, 1.4), "black", tag="pavise_rim")
    for sx in (-1, 1):
        k.box(pv, C(sx * 6.8, 13.4, -6.2, 0.9, 23.6, 1.4), "black", tag="pavise_rim")
    k.box(pv, C(0, 13.6, -6.0, 3.4, 23.0, 1.4), "ochre", tag="pavise_ridge")
    black_hand(k, pv, (0, 26.0, -6.95), 1.4)
    k.box(pv, C(0, 26.0, -6.9, 0.3, 0.3, 0.3), "sigil", tag="hand_mark")
    for i in range(3):                            # bolts stuck in it from the last fight
        k.shard(pv, (-4.0 + i * 3.4, 19.0 + i * 4.4, -6.9), (0.2 - i * 0.1, 0.1, -1), 5.0, 0.6, mat="wood", tag="stuck_bolt")
    # the hounskull: a round skull, the visor drawn out into a snout
    hd = k.part("head", (0, 34, 0.6), (("x", -4),), "torso")
    k.blob(hd, (0, 38.6, 0.4), (4.0, 4.6, 4.2), "steel", "bascinet", step=0.6)
    k.shard(hd, (0, 42.6, -0.4), (0, 1, -0.5), 2.6, 2.0, mat="steel", tag="bascinet_point")
    k.box(hd, C(0, 33.2, 0.4, 9.0, 2.4, 8.4), "mail", tag="aventail")
    k.shard(hd, (0, 37.4, 3.0), (0, -0.15, 1), 6.4, 5.4, mat="steel", tag="snout")
    k.box(hd, C(0, 38.8, 4.2, 6.6, 0.7, 0.6), "dark", tag="sight")
    eyes(k, hd, 38.85, 4.5, 1.5, 1.0)
    for i in range(6):
        k.box(hd, C(-1.2 + (i % 3) * 1.2, 36.0 - (i // 3) * 1.1, 6.6 - (i // 3) * 0.2, 0.5, 0.5, 0.4), "dark", tag="breath")
    for sx in (-1, 1):
        k.box(hd, C(sx * 4.4, 38.4, 1.4, 0.6, 1.4, 1.4), "brass", tag="visor_pivot")
    k.box(hd, C(0, 43.0, -0.2, 0.6, 1.4, 0.6), "brass", tag="crest_pin")
    arms(k, to, 8.0, 32, "leather", {1: ((("x", -44), ("z", -14)), (("x", -46),)), -1: ((("x", -40), ("z", 16)), (("x", -50),))})
    # the crossbow, aimed forward from the hip: modelled hanging from the right hand, turned forward by its part
    cb = k.part("crossbow", (-8.0, 14.4, 0.3), (("x", 92), ("z", -14)), k.parts["hand_r"], bone=False)
    k.box(cb, C(-6.0, 6.0, 0.3, 2.4, 20.0, 2.8), "wood", tag="stock")
    k.box(cb, C(-6.0, 4.0, 0.3, 3.0, 4.0, 4.0), "wood", tag="butt")
    k.box(cb, C(-6.0, 6.0, -1.3, 1.0, 20.0, 0.6), "dark", tag="groove")
    k.box(cb, C(-6.0, 22.0, 0.3, 2.8, 4.0, 3.2), "steel", tag="nose")
    for sx in (-1, 1):                            # the steel prod, its tips swept back
        k.limb(cb, (-6.0, 23.4, 0.3), (-6.0 + sx * 7.0, 22.6, 0.3), 1.6, "steel", "prod", d=1.6)
        k.limb(cb, (-6.0 + sx * 7.0, 22.6, 0.3), (-6.0 + sx * 10.4, 20.6, 0.3), 1.2, "steel", "prod", d=1.2)
        k.limb(cb, (-6.0 + sx * 10.2, 20.6, -0.4), (-6.0, 14.0, -1.6), 0.4, "dark", "string")
    k.box(cb, C(-6.0, 13.0, -2.6, 1.0, 13.0, 1.0), "wood", tag="bolt")
    k.shard(cb, (-6.0, 25.8, -2.6), (0, 1, 0), 2.6, 1.2, mat="steel", tag="bolt_head")
    k.box(cb, C(-6.0, 13.0, -2.2, 0.3, 2.4, 1.6), "ochre", tag="bolt_fletch")
    k.box(cb, C(-6.0, 22.6, 2.2, 1.4, 1.6, 1.6), "steel", tag="stirrup")
    k.ring(cb, -6.0, 26.4, 0.3, 2.2, 0.6, "steel", "stirrup", n=8, axis="x")
    k.box(cb, C(-6.0, 9.4, 2.2, 1.0, 4.0, 1.0), "steel", tag="trigger")
    k.ring(cb, -6.0, 3.6, 0.3, 2.4, 0.8, "brass", "windlass", n=10, axis="x")   # the windlass at the butt
    for sx in (-1, 1):
        k.limb(cb, (-6.0, 3.6, 0.3), (-6.0 + sx * 3.6, 3.0, 0.3), 0.8, "steel", "crank")
        k.box(cb, C(-6.0 + sx * 3.8, 2.2, 0.3, 1.2, 1.8, 1.2), "wood", tag="crank_knob")
    lit(k)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Hatchetman (skirmisher)

def hatchetman():
    """The ones the Banner sends in first. Bare arms roped with scars, a black hood, under it a mask of black
    iron hammered into a devil's face - stubs of horns, a grin cut through it, amber eyes - a harness of straps
    across the chest hung with throwing axes, and in each fist a bearded hatchet."""
    k = X.Kit("hatchetman")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(13, 10.6, 7.4), (20, 10.4, 7.2)], "leather", "breeches")
    k.box(hips, C(0, 19.0, 0, 11.6, 2.0, 8.2), "leather", tag="belt")
    k.box(hips, C(0, 18.8, 4.2, 2.0, 2.4, 0.6), "steel", tag="buckle")
    for i, x in enumerate((-3.0, 0.0, 3.0)):      # a ragged black sash knotted at the hip, its tails long
        k.box(hips, C(x + 1.0, 8.0 + i, -3.8, 2.4, 12.0 - i, 0.6), "black", tag="sash_tail")
    k.box(hips, C(4.6, 14.6, 4.0, 3.4, 4.4, 0.6), "ochre", tag="loincloth")
    for sx in (-1, 1):                            # throwing axes hung at the belt
        k.box(hips, C(sx * 5.8, 12.0, 1.6, 0.8, 7.0, 0.8), "wood", tag="belt_axe")
        k.box(hips, C(sx * 5.8, 17.0, 3.0, 0.6, 2.8, 2.6), "steel", tag="belt_axe_head")
    legs(k, hips, 19, 10.4, 3.2, hose="leather", knee_mat="leather", lean=-10, bend=14, th_w=5.0)
    for side in (1, -1):                          # leg wraps
        nm = "shin_" + ("l" if side > 0 else "r")
        for y in (4.0, 6.4, 8.8):
            k.box(k.parts[nm], C(side * 3.2, y, 0, 5.6, 0.8, 5.8), "black", tag="leg_wrap")
    to = k.part("torso", (0, 20, 0), (("x", 14),), "hips")
    k.stack(to, 0, 0, [(20, 10.4, 7.0), (25, 11.6, 7.4), (30, 13.8, 8.0), (34, 14.0, 7.6)], "skin", "chest")
    for y in (24.0, 27.0):                        # the belly's lines
        k.box(to, C(0, y, 3.75, 7.0, 0.4, 0.3), "mouth", tag="abs")
    k.box(to, C(0, 21.0, 3.76, 0.4, 8.0, 0.3), "mouth", tag="abs")
    for sx in (-1, 1):                            # the harness: two straps crossed, axes riding on them
        a, b = (sx * 6.4, 34.0, 4.0), (-sx * 5.2, 20.4, 4.0)
        straps(k, to, a, b, 1.6)
        k.box(to, C(-sx * 2.0, 24.2, 4.4, 0.8, 5.4, 0.8), "wood", tag="harness_axe")
        k.box(to, C(-sx * 2.0, 28.4, 4.7, 2.2, 2.0, 0.6), "steel", tag="harness_axe_head")
        k.limb(to, (sx * 6.4, 34.0, 4.0), (sx * 6.4, 34.0, -4.0), 1.6, "leather", "strap", d=0.8)
    k.box(to, C(0, 28.0, 4.5, 2.6, 2.6, 0.6), "steel", tag="harness_ring")
    k.box(to, C(2.6, 25.0, 3.8, 0.4, 6.0, 0.3), "mouth", tag="scar")
    black_hand(k, to, (3.0, 30.0, 4.0), 0.9)                     # the Hand, painted on his own chest
    for sx in (-1, 1):
        k.blob(to, (sx * 7.4, 32.4, 0), (2.6, 2.0, 3.0), "leather", "shoulder_pad", step=0.7)
    hd = k.part("head", (0, 34, 0.6), (("x", -12),), "torso")
    k.box(hd, C(0, 34.4, 0.6, 6.4, 7.0, 6.6), "skin", tag="head")
    # the devil mask: black iron over the whole face, heavy brows, a grin cut through it, horn stubs
    k.box(hd, C(0, 34.2, 3.8, 6.8, 7.4, 1.4), "blacksteel", tag="mask")
    k.box(hd, C(0, 38.6, 4.6, 7.2, 1.2, 1.2), "blacksteel", tag="mask_brow")
    k.box(hd, C(0, 36.6, 4.6, 1.6, 2.2, 1.4), "blacksteel", tag="mask_nose")
    eyes(k, hd, 38.0, 4.55, 1.6, 1.4)
    for sx in (-1, 1):
        k.box(hd, C(sx * 1.6, 37.7, 4.5, 1.8, 1.2, 0.2), "dark", tag="socket")
        k.limb(hd, (sx * 2.6, 39.6, 3.6), (sx * 4.4, 42.4, 2.4), 1.6, "blacksteel", "horn")
        k.shard(hd, (sx * 4.4, 42.4, 2.4), (sx * 0.2, 0.6, -0.8), 3.4, 1.3, mat="blacksteel", tag="horn")
        k.box(hd, C(sx * 3.6, 34.6, 4.0, 0.8, 1.0, 0.8), "brass", tag="mask_rivet")
    k.box(hd, C(0, 34.8, 4.55, 4.6, 0.8, 0.2), "mouth", tag="grin")
    for x in (-1.6, -0.5, 0.5, 1.6):              # its iron teeth
        k.box(hd, C(x, 34.8, 4.6, 0.5, 0.8, 0.2), "steel", tag="mask_teeth")
    k.shard(hd, (0, 34.4, 4.4), (0, -1, 0.4), 2.4, 2.0, mat="blacksteel", tag="mask_chin")
    # the hood over it, falling to the shoulders
    k.blob(hd, (0, 38.6, -0.2), (4.4, 4.0, 4.6), "black", "hood", step=0.6)
    k.box(hd, C(0, 33.0, -1.0, 9.6, 3.4, 7.0), "black", tag="hood_drape")
    k.box(hd, C(0, 42.0, 2.6, 7.6, 1.0, 2.6), "black", tag="hood_peak")
    arms(k, to, 7.6, 32, "skin", {1: ((("x", -18), ("z", 26)), (("x", -64),)), -1: ((("x", 18), ("z", -30)), (("x", -40),))})
    for side in (1, -1):
        nm = "fore_" + ("l" if side > 0 else "r")
        for y in (18.6, 20.6):
            k.box(k.parts[nm], C(side * 7.6, y, 0, 4.4, 1.2, 4.4), "leather", tag="bracer")
        k.box(k.parts["arm_" + ("l" if side > 0 else "r")], C(side * 7.6, 27.4, 1.6, 0.4, 3.0, 0.3), "mouth", tag="scar")
    k.box(k.parts["arm_l"], C(7.6, 28.6, 0, 4.6, 1.8, 4.6), "ochre", tag="armband")
    k.box(k.parts["arm_l"], C(9.6, 25.0, 0.6, 0.6, 4.0, 1.2), "ochre", tag="armband_tail")
    for side, nm in ((1, "l"), (-1, "r")):        # the hatchets: short hafts, bearded heads
        x = side * 7.6
        ht = k.part("hatchet_" + nm, (x, 14.4, 0.3), (("x", 70 if side > 0 else 40),), k.parts["hand_" + nm], bone=False)
        k.limb(ht, (x, 10.0, 0.3), (x, 32.0, 0.3), 1.5, "wood", "haft")
        k.box(ht, C(x, 9.0, 0.3, 1.8, 1.6, 1.8), "steel", tag="haft_cap")
        k.box(ht, C(x, 27.4, 0.3, 2.2, 4.4, 2.2), "steel", tag="eye")
        k.box(ht, C(x, 27.0, 2.4, 1.2, 5.0, 3.0), "blade", tag="axe_head")
        k.box(ht, C(x, 21.6, 4.4, 1.2, 10.4, 2.6), "blade", tag="beard")
        k.box(ht, C(x, 21.6, 7.0, 1.3, 10.4, 0.7), "blade", tag="edge")
        k.shard(ht, (x, 29.6, -0.8), (0, 0, -1), 3.4, 1.4, mat="steel", tag="back_spike")
        k.box(ht, C(x, 28.2, 1.6, 1.4, 0.6, 2.0), "ochre", tag="axe_rag")
        for y in (13.0, 15.0):
            k.box(ht, C(x, y, 0.3, 1.6, 1.0, 1.6), "black", tag="grip_wrap")
    for b in k.s.boxes:                           # the hatchet eyes aren't eyes
        if b.tag == "eye" and b.mat == "steel":
            b.tag = "axe_eye"
    lit(k)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Anvil Breaker (brute)

def anvil_breaker():
    """The company's giant took the armour off three dead men and had it beaten over him in whatever order it
    fitted: a great sallet with its tail down his back and a slit he sees through, mismatched plates, a yellow plate
    he painted himself, chains wrapped round both forearms, and for a weapon the smith's anvil from the first town
    they burned, on an iron-banded pole."""
    k = X.Kit("anvil_breaker")
    hips = k.part("hips", (0, 21, 0))
    k.stack(hips, 0, 0, [(12, 14.4, 10.0), (21, 14.0, 9.6)], "mail", "mail_skirt")
    k.box(hips, C(0, 20.2, 0, 15.0, 2.4, 10.6), "leather", tag="belt")
    k.box(hips, C(0, 19.8, 5.4, 3.4, 3.2, 0.6), "brass", tag="buckle")
    for x, m in ((-4.6, "steel"), (0, "rust"), (4.6, "ochre")):   # three faulds, none of them a pair
        k.box(hips, C(x, 13.0, 5.2, 4.2, 7.4, 1.0), m, tag="fauld")
    legs(k, hips, 20, 11.0, 4.4, hose="leather", lean=-4, bend=6, th_w=6.6)
    for side in (1, -1):
        nm = "shin_" + ("l" if side > 0 else "r")
        k.box(k.parts[nm], C(side * 4.4, 3.0, 2.6, 6.0, 7.4, 1.6), "steel", tag="greave")
    to = k.part("torso", (0, 21, 0), (("x", 10),), "hips")
    k.stack(to, 0, 0, [(21, 14.2, 9.8), (26, 16.4, 10.6), (31, 20.4, 11.6), (35, 21.4, 11.2), (37.4, 17.0, 9.6)], "leather", "jack")
    # the breastplate (one man's), a plackart over it (another's), a yellow lame he painted
    k.blob(to, (0, 29.4, 2.6), (8.4, 6.2, 4.0), "steel", "breastplate", step=0.8)
    k.box(to, C(0, 22.4, 5.0, 12.4, 4.6, 1.6), "rust", tag="plackart")
    k.box(to, C(0, 26.6, 6.2, 9.6, 1.6, 1.0), "ochre", tag="painted_lame")
    black_hand(k, to, (0, 31.6, 6.9), 1.1)
    for x in (-5.4, 5.4):
        k.box(to, C(x, 22.8, 5.9, 0.8, 0.8, 0.6), "brass", tag="rivet")
    k.box(to, C(-3.6, 33.0, 6.6, 2.0, 0.6, 0.4), "dark", tag="dent")
    for sx in (-1, 1):                            # pauldrons: two plates either side, and on the left a spiked boss
        k.blob(to, (sx * 11.6, 35.4, 0), (5.6, 3.6, 6.4), "steel" if sx > 0 else "rust", "pauldron", step=0.8)
        k.box(to, C(sx * 12.4, 31.4, 0, 6.6, 1.8, 11.0), "steel", tag="lame")
        k.box(to, C(sx * 12.8, 29.4, 0, 6.0, 1.6, 10.2), "rust", tag="lame")
    for i in range(4):
        k.shard(to, (11.4 + i * 1.2, 38.4, -3.0 + i * 2.0), (0.5, 1, 0), 3.6, 1.6, mat="steel", tag="pauldron_spike")
    k.box(to, C(0, 36.6, -0.6, 10.4, 3.0, 9.4), "mail", tag="mail_collar")
    k.box(to, C(0, 22.0, -5.6, 12.0, 14.0, 0.8), "black", tag="cloak_back")
    hd = k.part("head", (0, 37.6, 0.4), (("x", -10),), "torso")
    k.box(hd, C(0, 37.4, 0.6, 7.4, 6.4, 7.0), "skin", tag="neck_face")
    # the great sallet: a deep bowl swept back into a long tail, the slit across the front, a bevor under it
    k.blob(hd, (0, 42.2, 0.6), (5.2, 4.0, 5.4), "steel", "sallet", step=0.7)
    k.box(hd, C(0, 38.6, -2.2, 10.4, 3.4, 6.0), "steel", tag="sallet_tail")
    k.shard(hd, (0, 39.6, -4.4), (0, -0.5, -1), 6.0, 7.0, mat="steel", tag="sallet_tail")
    k.box(hd, C(0, 41.4, 5.4, 9.6, 0.8, 0.6), "dark", tag="slit")
    eyes(k, hd, 41.5, 5.75, 1.8, 1.4)
    k.box(hd, C(0, 36.4, 2.8, 9.2, 4.8, 5.4), "rust", tag="bevor")
    k.box(hd, C(0, 46.0, 0.4, 1.2, 1.6, 8.4), "steel", tag="sallet_ridge")
    k.shard(hd, (5.0, 44.0, 1.0), (1, 0.6, 0), 4.6, 2.0, mat="steel", tag="horn")
    k.shard(hd, (-5.0, 44.0, 1.0), (-1, 0.6, 0), 1.8, 2.0, mat="steel", tag="horn_broken")
    for x in (-3.6, 3.6):
        k.box(hd, C(x, 43.0, 5.4, 1.0, 1.0, 0.6), "brass", tag="rivet")
    arms(k, to, 12.0, 34, "skin", {1: ((("x", -56), ("z", -8)), (("x", -40),)), -1: ((("x", -62), ("z", 10)), (("x", -30),))}, w=6.0)
    for side in (1, -1):                          # chains wound round the forearms, a vambrace over the elbow
        x = side * 12.0
        fo = k.parts["fore_" + ("l" if side > 0 else "r")]
        for y in (21.0, 23.0, 25.0):
            k.ring(fo, x, y, 0, 3.2, 0.8, "steel", "chain_wrap", n=10, axis="y")
        k.box(fo, C(x, 25.6, 0, 6.6, 1.8, 6.6), "rust", tag="couter")
        k.box(k.parts["hand_" + ("l" if side > 0 else "r")], C(x, 15.0, 0.3, 6.0, 4.4, 6.4), "steel", tag="gauntlet")
        k.box(k.parts["arm_" + ("l" if side > 0 else "r")], C(x, 27.4, 2.6, 0.5, 4.0, 0.4), "mouth", tag="scar")
    k.chain(to, (12.0, 22.0, 3.4), (8.0, 14.0, 4.4), 5, w=1.2)       # a loose end hanging
    # the anvil maul: the pole across both hands, the anvil high over his right shoulder
    mp = k.part("maul", (-12.0, 16.0, 0.4), (("x", 150), ("z", 14)), k.parts["hand_r"], bone=False)
    k.limb(mp, (-12.0, 6.0, 0.4), (-12.0, 40.0, 0.4), 2.2, "wood", "pole")
    for y in (12.0, 22.0, 32.0):
        k.box(mp, C(-12.0, y, 0.4, 2.8, 1.4, 2.8), "steel", tag="band")
    k.box(mp, C(-12.0, 4.6, 0.4, 3.0, 2.0, 3.0), "steel", tag="pole_cap")
    k.box(mp, C(-12.0, 38.6, 0.4, 3.4, 3.4, 3.4), "steel", tag="socket")
    # the anvil: base, waist, face, the horn out one side and the heel square the other
    ay = 41.6
    k.box(mp, C(-12.0, ay, 0.4, 7.4, 2.6, 6.6), "steel", tag="anvil_base")
    k.box(mp, C(-12.0, ay + 2.6, 0.4, 5.0, 2.8, 4.6), "steel", tag="anvil_waist")
    k.box(mp, C(-12.0, ay + 5.4, 0.4, 7.0, 3.6, 13.0), "steel", tag="anvil_face")
    k.box(mp, C(-12.0, ay + 8.9, 0.4, 7.2, 0.5, 13.2), "steel", tag="anvil_top")
    k.shard(mp, (-12.0, ay + 6.8, 6.8), (0, 0.15, 1), 9.0, 5.2, mat="steel", tag="anvil_horn")
    k.box(mp, C(-12.0, ay + 7.0, -5.8, 1.6, 1.6, 1.0), "dark", tag="hardy_hole")
    k.box(mp, C(-12.0, ay + 5.4, -6.1, 7.4, 3.6, 0.4), "rust", tag="anvil_heel")
    for z in (-3.0, 2.0):
        k.box(mp, C(-8.3, ay + 6.4, z, 0.4, 1.6, 2.0), "rust", tag="pitting")
    lit(k)
    k.s.shaders = shaders()
    grow(k, 1.3)
    return k.s, k.parts


# ================================================================ the Banner Captain (elite)

def banner_captain():
    """The man who took the hanged captain's place wears the plate of the lords he's robbed since: blackened
    steel, every edge in brass, an armet under a storm of black plumes with a visor pierced in a snarl and the
    amber of his eyes behind it; a wolf-fur mantle, a yellow sash, a black cloak with the Hand on it, and a
    flamberge as tall as him, the wave of its blade catching the light all along."""
    k = X.Kit("banner_captain")
    hips = k.part("hips", (0, 21, 0))
    k.stack(hips, 0, 0, [(12, 12.4, 8.6), (21, 12.0, 8.2)], "mail", "mail_skirt")
    for i, y in enumerate((17.6, 14.4)):          # tassets: two lames each side, brass-edged
        for sx in (-1, 1):
            k.box(hips, C(sx * 3.4, y, 4.4 + i * 0.3, 5.4, 3.6, 1.0), "blacksteel", tag="tasset")
            k.box(hips, C(sx * 3.4, y, 4.95 + i * 0.3, 5.6, 0.6, 0.4), "brass", tag="tasset_edge")
    k.box(hips, C(0, 20.2, 0, 13.0, 1.8, 9.2), "leather", tag="belt")
    k.box(hips, C(-6.6, 13.8, 0, 1.4, 6.6, 2.2), "leather", tag="scabbard")
    legs(k, hips, 20, 10.8, 3.6, hose="blacksteel", boot="blacksteel", knee_mat="brass", lean=-6, bend=8, th_w=5.8)
    to = k.part("torso", (0, 21, 0), (("x", 5),), "hips")
    k.stack(to, 0, 0, [(21, 12.0, 8.4), (26, 13.6, 9.0), (31, 16.6, 9.8), (35, 17.2, 9.4)], "blacksteel", "cuirass")
    k.blob(to, (0, 30.0, 2.4), (7.0, 5.6, 3.6), "blacksteel", "breastplate", step=0.7)
    k.box(to, C(0, 25.6, 5.4, 1.2, 8.4, 0.8), "brass", tag="ridge")
    for y in (22.0, 24.4):
        k.box(to, C(0, y, 4.4, 11.6, 1.4, 1.0), "blacksteel", tag="fauld")
        k.box(to, C(0, y + 1.0, 4.95, 11.8, 0.4, 0.3), "brass", tag="fauld_edge")
    straps(k, to, (7.4, 35.0, 5.0), (-6.4, 21.4, 5.4), 2.4, mat="ochre")      # the yellow sash across it
    k.box(to, C(-6.4, 18.0, 5.4, 2.6, 4.6, 0.6), "ochre", tag="sash_knot")
    # the mantle: wolf fur heaped on the shoulders, the head of the wolf on the left
    k.blob(to, (0, 35.6, -0.4), (10.4, 2.8, 6.4), "fur", "mantle", step=0.8)
    for sx in (-1, 1):
        k.blob(to, (sx * 9.4, 34.4, 0), (4.8, 3.6, 5.6), "blacksteel", "pauldron", step=0.7)
        k.box(to, C(sx * 10.0, 31.0, 0, 6.4, 1.6, 9.4), "blacksteel", tag="lame")
        k.box(to, C(sx * 10.0, 32.4, 0, 6.6, 0.5, 9.6), "brass", tag="lame_edge")
        k.shard(to, (sx * 11.0, 37.4, 0), (sx * 0.3, 1, 0), 2.6, 1.6, mat="brass", tag="pauldron_point")
    k.box(to, C(7.0, 37.4, 3.6, 3.8, 2.6, 3.4), "fur", tag="wolf_head")
    k.shard(to, (7.0, 38.0, 6.6), (0, -0.2, 1), 2.6, 2.0, mat="fur", tag="wolf_snout")
    for x in (5.8, 8.2):
        k.shard(to, (x, 39.8, 3.4), (0, 1, -0.2), 1.6, 1.0, mat="fur", tag="wolf_ear")
    # the cloak, long, black, the Hand on it in yellow-ringed black
    cl = k.part("cloak", (0, 35, -5.2), (("x", 6),), to, bone=False)
    for i, x in enumerate((-4.8, -1.6, 1.6, 4.8)):
        k.box(cl, C(x, 5.0 - (i % 2) * 1.6, -5.8, 3.4, 30.0 + (i % 2) * 1.6, 0.8), "black", tag="cloak")
    k.box(cl, C(0, 22.0, -6.3, 8.4, 8.4, 0.3), "ochre", tag="cloak_field")
    black_hand(k, cl, (0, 26.6, -6.55), 1.2)
    k.box(cl, C(0, 26.6, -6.5, 0.3, 0.3, 0.3), "sigil", tag="hand_mark")
    # the armet: a rounded skull, the visor pierced in a snarl, plumes
    hd = k.part("head", (0, 36.4, 0.6), (("x", -4),), "torso")
    k.blob(hd, (0, 40.8, 0.4), (3.7, 4.0, 3.9), "blacksteel", "armet", step=0.6)
    k.shard(hd, (0, 38.6, 3.0), (0, -0.15, 1), 4.6, 5.8, mat="blacksteel", tag="visor")
    k.box(hd, C(0, 40.4, 4.0, 6.4, 0.7, 0.6), "dark", tag="sight")
    eyes(k, hd, 40.45, 4.35, 1.4, 1.2)
    k.box(hd, C(0, 41.2, 4.1, 6.8, 0.5, 0.5), "brass", tag="visor_edge")
    for i, (x, y) in enumerate(((-1.6, 36.6), (-0.5, 36.2), (0.5, 36.2), (1.6, 36.6))):   # the snarl
        k.box(hd, C(x, y + 1.0, 6.0 - abs(x) * 0.5, 0.5, 1.2, 0.4), "dark", tag="snarl")
    k.box(hd, C(0, 34.4, 1.0, 8.6, 2.4, 8.0), "blacksteel", tag="gorget")
    k.box(hd, C(0, 35.6, 1.0, 8.8, 0.5, 8.2), "brass", tag="gorget_edge")
    k.box(hd, C(0, 44.6, 0.0, 1.4, 1.0, 7.2), "brass", tag="comb")
    k.box(hd, C(0, 44.0, -2.6, 2.0, 2.4, 2.0), "brass", tag="plume_holder")
    for i in range(7):                            # black plumes: up and back, falling over
        a = math.radians(-50 + i * 17)
        p0 = (math.sin(a) * 1.4, 45.4, -2.8)
        p1 = (math.sin(a) * 6.0, 49.0 + (3 - abs(i - 3)) * 1.2, -6.0 - abs(math.cos(a)) * 2.0)
        p2 = (math.sin(a) * 8.6, 46.4 + (3 - abs(i - 3)) * 0.6, -11.0)
        k.limb(hd, p0, p1, 1.8, "black", "plume", d=0.8)
        k.limb(hd, p1, p2, 1.4, "black", "plume", d=0.6)
    arms(k, to, 9.4, 33, "blacksteel", {1: ((("x", -30), ("z", -26)), (("x", -40),)), -1: ((("x", -30), ("z", 24)), (("x", -42),))})
    for side in (1, -1):
        nm = "l" if side > 0 else "r"
        x = side * 9.4
        k.box(k.parts["fore_" + nm], C(x, 23.6, 0, 5.0, 1.8, 5.0), "brass", tag="couter")
        k.box(k.parts["hand_" + nm], C(x, 14.4, 0.3, 4.6, 4.0, 5.0), "blacksteel", tag="gauntlet")
        k.box(k.parts["hand_" + nm], C(x, 17.8, 0.3, 5.2, 1.2, 5.4), "brass", tag="cuff_edge")
    # the flamberge, held upright before him in both hands
    fl = k.part("flamberge", (-9.4, 15.4, 0.3), (("x", 76), ("z", -18)), k.parts["hand_r"], bone=False)
    k.limb(fl, (-9.4, 7.0, 0.3), (-9.4, 19.0, 0.3), 1.6, "leather", "grip")
    k.box(fl, C(-9.4, 5.6, 0.3, 2.6, 2.0, 2.6), "brass", tag="pommel")
    k.box(fl, C(-9.4, 19.0, 0.3, 10.4, 1.6, 2.0), "brass", tag="quillon")
    for sx in (-1, 1):
        k.ring(fl, -9.4 + sx * 5.8, 20.0, 0.3, 1.0, 0.5, "brass", "quillon_ring", n=6, axis="z")
    k.box(fl, C(-9.4, 20.6, 0.3, 2.4, 4.0, 1.4), "steel", tag="ricasso")
    for sz in (-1, 1):
        k.shard(fl, (-9.4 + sz * 1.4, 23.0, 0.3), (sz, -0.2, 0), 1.8, 0.8, mat="brass", tag="parry_lug")
    for i in range(10):                           # the wavy blade, flat to the front: each step pushed side to side
        y = 24.6 + i * 2.6
        dx = math.sin(i * 1.3) * 0.8
        w = 3.8 - i * 0.12
        k.box(fl, C(-9.4 + dx, y, 0.3, w, 2.65, 1.0), "blade", tag="flamberge_blade")
        for sx in (-1, 1):
            k.box(fl, C(-9.4 + dx + sx * (w * 0.5 - 0.2), y, 0.3, 0.5, 2.65, 1.1), "blade", tag="edge")
    k.box(fl, C(-9.4, 25.0, 0.8, 0.6, 22.0, 0.3), "dark", tag="fuller")
    k.shard(fl, (-9.4, 50.6, 0.3), (0, 1, 0), 4.0, 2.6, mat="blade", tag="blade_tip")
    lit(k)
    k.s.shaders = shaders()
    grow(k, 1.12)
    return k.s, k.parts


MOBS = {
    "banner_hound": dict(make=banner_hound, rig="crawler", ent=(1.2, 1.4), stats=dict(hp=30, speed=0.36, dmg=7, armor=2, kb=0)),
    "deserter": dict(make=deserter, ent=(0.9, 2.8), stats=dict(hp=60, speed=0.25, dmg=9, armor=8, kb=0.3)),
    "arbalest": dict(make=arbalest, ent=(0.9, 2.8), stats=dict(hp=40, speed=0.22, dmg=8, armor=5, kb=0)),
    "hatchetman": dict(make=hatchetman, ent=(0.8, 2.7), stats=dict(hp=44, speed=0.33, dmg=8, armor=3, kb=0)),
    "anvil_breaker": dict(make=anvil_breaker, ent=(1.6, 3.8), stats=dict(hp=170, speed=0.2, dmg=18, armor=9, kb=1.0)),
    "banner_captain": dict(make=banner_captain, ent=(1.1, 3.2), stats=dict(hp=320, speed=0.25, dmg=15, armor=12, kb=0.6), key=True),
}
