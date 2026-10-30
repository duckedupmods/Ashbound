"""The Blightkin: what came out of the vats when the alchemists of the asylums and the swamp-houses got their great
work wrong, who hold the world's asylums, toxic lairs, witch villas and witch huts, built by hand (tools/vox2.py).
Pale mauve flesh stitched with black thread, glass vats and domes, brass and copper tubing, black oilcloth gone
green with spills, and the chartreuse glow of the acid in everything. (Not the Plague Ward's doctors and friars,
not the Mirefen's hags: these are the experiments.)

    acid_slug         swarm   a slug as long as a man, glowing acid sacs along its back, eye-stalks, a trail
    vat_guard         guard   an orderly whose head floats in a glass dome of green fluid, tubes to a tank on his back,
                              a catch-pole with a hook
    vat_brute         brute   a giant mutant still wearing the broken iron cage of its vat, one arm swollen with boils,
                              a head too small for it
    alchemist         caster  the one who made them: a black oilcloth apron, a mask of round green lenses, a bandolier
                              of flasks and a staff with an alembic bubbling at its top
    stitched_stalker  skirm   sewn together out of the failures, a second pair of small arms grafted on its back, long
                              bone claws
    chimera           elite   the great work: two heads, a crab's claw for an arm, a glass tank in its chest where a heart
                              floats, and a surgeon's saw as long as a sword

    python tools/monsterforge.py blightkin --preview ; python tools/mobsheet.py blightkin
"""
import math

import vox2 as X
from vox2 import C, ramp
from serpent_ziggurat import grow
from _folk import lit, eyes, straps, legs, arms, held, quad

FLESH = ramp("#24181c", "#3a2830", "#4e3842", "#644a56", "#7a5e6a", "#927684")
OIL = ramp("#060806", "#0c100c", "#121812", "#1a221a", "#243024")
GLASS = ramp("#0e1a12", "#16281c", "#203a28", "#2c4e36", "#3c6648")
BRASS = ramp("#1e1206", "#38220c", "#583814", "#7a521e", "#9c6c2a", "#be8a3a")
IRON = ramp("#0a0a0c", "#141418", "#1e1e24", "#2a2a32", "#383842")
THREAD = ramp("#040404", "#0a0a0a", "#121212", "#1a1a1a")
BONE = ramp("#3a3428", "#5a5240", "#7c7258", "#9e9476", "#c0b896")
CRAB = ramp("#1a0a06", "#30120a", "#4a1c10", "#662818", "#823622", "#a04830")
SLUG = ramp("#141410", "#22221a", "#323226", "#444434", "#585844")
ACID = ramp("#2a4a02", "#4a7a04", "#7ab80a", "#b4ec1e", "#e0ff6a", "#f8ffd0")
BLOOD = ramp("#2a0408", "#46080e", "#640e16", "#82161e")


def shaders():
    stitched = lambda p, n, i, j, w, h: -0.4 if (i * 3 + j * 7) % 17 == 0 or (j % 9 == 0 and i % 2 == 0) else 0.0
    return {
        "flesh": X.surf(FLESH, 0.5, 1.2, 0.18, 0.06, pattern=stitched),
        "oil": X.surf(OIL, 0.56, 1.4, 0.1, 0.16, rust=(GLASS, 0.24, 0.5)),
        "glass": X.surf(GLASS, 0.62, 1.8, 0.04, 0.34),
        "brass": X.surf(BRASS, 0.56, 1.4, 0.12, 0.24, rust=(GLASS, 0.2, 0.6)),
        "iron": X.surf(IRON, 0.5, 1.4, 0.16, 0.2, rust=(BLOOD, 0.2, 0.5)),
        "thread": X.surf(THREAD, 0.5, 1.0, 0.1, 0.0),
        "bone": X.surf(BONE, 0.56, 1.2, 0.16, 0.12),
        "crab": X.surf(CRAB, 0.56, 1.5, 0.14, 0.24),
        "slug": X.wrinkled(SLUG, 0.6),
        "leather": X.surf(OIL, 0.5, 1.1, 0.2, 0.04),
        "steel": X.surf(IRON, 0.7, 1.6, 0.06, 0.32),
        "acid": X.glow(ACID),
        "eye": X.glow(ACID, 0.86, 0.12),
        "blood": X.surf(BLOOD, 0.5, 1.2, 0.1, 0.0),
        "dark": X.dark(OIL),
    }


GLOWS = {"acid", "eye"}


def stitches(k, part, a, b, n=5):
    """a seam: a dark line with cross-stitches"""
    k.limb(part, a, b, 0.3, "thread", "seam", d=0.3)
    for i in range(n):
        t = (i + 0.5) / n
        p = tuple(a[j] + (b[j] - a[j]) * t for j in range(3))
        k.box(part, C(p[0], p[1] - 0.2, p[2], 1.4, 0.4, 0.4), "thread", tag="stitch")


def tube(k, part, pts, w=1.0, mat="brass"):
    for a, b in zip(pts, pts[1:]):
        k.limb(part, a, b, w, mat, "tube")


def boils(k, part, at, n, r, seed=1):
    cx, cy, cz = at
    for i in range(n):
        a = (i * 2.399 + seed) % (2 * math.pi)
        d = r * ((i * 0.618 + seed * 0.1) % 1)
        s = 0.9 + ((i * 7 + seed) % 3) * 0.4
        k.blob(part, (cx + math.cos(a) * d, cy + math.sin(a) * d * 0.8, cz), (s, s, s * 0.7), "acid" if i % 3 == 0 else "flesh", "boil", step=0.5)


# ================================================================ the Acid Slug (swarm)

def acid_slug():
    """They feed the vats' leavings to the slugs, and the slugs grew. One as long as a man, grey-green and wet, a row
    of sacs along its back swollen with acid that glows through the skin, two eye-stalks, a mouth like a pursed
    sucker, and behind it a trail that smokes."""
    k = X.Kit("acid_slug")
    body, hd, ab, joints = quad(k, "slug", y=5, chest=((0.4, 9, 8), (3, 10, 9), (6, 8.4, 8)), haunch=((0.4, 8, 7), (3, 8.6, 8), (5.4, 7, 7)),
                                leg_w=2.4, foot_w=2.0, front_z=3, back_z=-8, x=3.0, head_at=(0, 5, 6), head_rot=0, claw="slug", foot_len=4.0, knees=(0.4, 0.4))
    k.box(body, C(0, 0, 0, 10.6, 1.6, 12.0), "slug", tag="foot")
    k.box(ab, C(0, 0, -9.0, 9.6, 1.6, 12.0), "slug", tag="foot")
    k.box(ab, C(0, 0, -16.0, 6.0, 1.4, 4.0), "slug", tag="tail")
    k.shard(ab, (0, 1.4, -18.0), (0, 0.1, -1), 3.4, 2.4, mat="slug", tag="tail_tip")
    for i, z in enumerate((2.0, -2.4, -6.8, -11.0)):          # the acid sacs along its back
        part = body if z > -3 else ab
        k.blob(part, (0, 9.4 - i * 0.4, z), (2.8 - i * 0.2, 2.4 - i * 0.2, 2.2), "acid", "acid_sac", step=0.5)
        k.box(part, C(0, 8.0 - i * 0.4, z, 6.2 - i * 0.3, 0.8, 4.6), "slug", tag="sac_rim")
    k.box(ab, C(0, 0.0, -22.0, 4.0, 0.3, 6.0), "acid", tag="smoking_trail")
    k.blob(hd, (0, 5.0, 9.6), (4.0, 3.6, 3.6), "slug", "head", step=0.6)
    k.ring(hd, 0, 4.6, 12.8, 1.6, 0.8, "slug", "sucker", n=10, axis="z")
    k.box(hd, C(0, 3.8, 13.0, 1.6, 1.6, 0.4), "dark", tag="mouth")
    for sx in (-1, 1):
        k.limb(hd, (sx * 1.6, 7.6, 9.6), (sx * 2.8, 13.0, 11.0), 0.9, "slug", "eye_stalk")
        k.blob(hd, (sx * 2.8, 13.4, 11.0), (0.9, 0.9, 0.9), "eye", "eye", step=0.4)
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


# ================================================================ the Vat Guard (guard)

def vat_guard():
    """The asylum's orderlies volunteered first. Their heads float now in glass domes full of green fluid screwed to
    brass collars, fed by tubes from the tank on their backs; black oilcloth coats to the knee, heavy gloves, and the
    catch-pole they used on the inmates - a long pole with a hooked noose of iron at the end."""
    k = X.Kit("vat_guard")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(8, 12.4, 9.4), (14, 11.6, 8.6), (20, 11.0, 8.0)], "oil", "oilcoat", step=1.0)
    k.box(hips, C(0, 19.0, 0, 11.8, 2.0, 8.6), "leather", tag="belt")
    for x, y in ((-3.0, 11.0), (2.6, 14.0)):
        k.box(hips, C(x, y, 4.6, 2.4, 3.0, 0.4), "acid", tag="spill_stain")
    legs(k, hips, 19, 10.4, 3.2, "oil", "oil", knee_mat="iron", lean=-6, bend=8, w=5.0, cuff=True)
    to = k.part("torso", (0, 20, 0), (("x", 6),), "hips")
    k.stack(to, 0, 0, [(20, 11.0, 8.0), (25, 12.4, 8.4), (30, 14.4, 9.0), (33.6, 13.6, 8.4)], "oil", "oilcoat")
    for y in (22.0, 25.0, 28.0):
        k.box(to, C(1.6, y, 4.25, 1.0, 1.0, 0.3), "brass", tag="clasp")
    k.limb(to, (-5.6, 33.0, 4.2), (5.0, 21.0, 4.4), 1.4, "leather", "strap", d=0.5)
    # the tank on the back, a window in it, tubes over the shoulders to the collar
    k.stack(to, 0, -7.0, [(18.0, 7.6, 5.0), (31.0, 7.6, 5.0)], "brass", "tank")
    k.box(to, C(0, 21.0, -9.6, 3.6, 8.0, 0.4), "acid", tag="tank_window")
    for sx in (-1, 1):
        tube(k, to, [(sx * 3.0, 31.0, -6.0), (sx * 4.6, 35.0, -3.0), (sx * 3.6, 34.6, 1.6)], 1.1)
    hd = k.part("head", (0, 33.6, 0.6), (("x", -4),), "torso")
    k.stack(hd, 0, 0.6, [(33.0, 9.0, 9.0), (34.6, 8.4, 8.4)], "brass", "dome_collar")
    for a in range(0, 360, 45):
        r = math.radians(a)
        k.box(hd, C(math.cos(r) * 4.2, 34.0, 0.6 + math.sin(r) * 4.2, 0.9, 0.9, 0.9), "iron", tag="bolt")
    k.blob(hd, (0, 39.6, 0.6), (4.4, 5.0, 4.4), "acid", "dome_fluid", step=0.6)          # the dome, full of the glow
    for i in range(6):                            # the brass ribs of its frame
        a = i * math.pi / 3
        k.limb(hd, (math.cos(a) * 4.5, 35.0, 0.6 + math.sin(a) * 4.5), (math.cos(a) * 4.0, 41.6, 0.6 + math.sin(a) * 4.0), 0.7, "brass", "dome_rib")
        k.limb(hd, (math.cos(a) * 4.0, 41.6, 0.6 + math.sin(a) * 4.0), (0, 44.4, 0.6), 0.7, "brass", "dome_rib")
    k.box(hd, C(0, 36.4, 4.4, 4.0, 4.8, 1.0), "flesh", tag="face_floating")    # the face pressed to the glass
    for sx in (-1, 1):
        k.box(hd, C(sx * 1.1, 39.2, 4.95, 1.0, 0.6, 0.3), "dark", tag="eye_dead")
    k.box(hd, C(0, 37.2, 4.95, 1.6, 0.8, 0.3), "dark", tag="mouth")
    k.box(hd, C(0, 44.4, 0.6, 1.8, 1.4, 1.8), "brass", tag="valve")
    arms(k, to, 7.8, 32, "oil", {1: ((("x", -40), ("z", -8)), (("x", -40),)), -1: ((("x", -50), ("z", 8)), (("x", -40),))}, glove="leather", w=3.8)
    for side in (1, -1):
        k.box(k.parts["fore_" + ("l" if side > 0 else "r")], C(side * 7.8, 16.4, 0, 4.6, 3.0, 4.6), "leather", tag="gauntlet")
    cp = held(k, "catch_pole", "r", (-7.8, 14.0, 0.4), (("x", 100),))
    k.limb(cp, (-7.8, -6.0, 0.4), (-7.8, 30.0, 0.4), 1.4, "iron", "pole")
    for y in (4.0, 8.0):
        k.box(cp, C(-7.8, y, 0.4, 2.0, 1.2, 2.0), "leather", tag="grip_wrap")
    k.ring(cp, -7.8, 33.0, 2.6, 3.0, 0.9, "iron", "noose", n=12, axis="x")
    k.limb(cp, (-7.8, 30.0, 0.4), (-7.8, 31.0, 2.4), 0.9, "iron", "noose_neck")
    k.shard(cp, (-7.8, 36.0, 2.6), (0, 0.2, 1), 3.0, 1.0, mat="iron", tag="hook")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Vat Brute (brute)

def vat_brute():
    """The vat it grew in was too small and it broke out wearing the cage. A giant of stitched mauve flesh, the iron
    bars of the vat still bolted round its chest and bent where it burst them, tubes hanging out of its back, its
    right arm swollen twice the size of the left and crusted with glowing boils, and on top of it all a head far too
    small, mouth open."""
    k = X.Kit("vat_brute")
    hips = k.part("hips", (0, 20, 0))
    k.stack(hips, 0, 0, [(12, 15.0, 10.6), (20, 16.0, 11.4)], "oil", "oil_wraps")
    k.box(hips, C(0, 19.0, 0, 16.6, 2.4, 12.0), "leather", tag="belt")
    legs(k, hips, 19, 10.6, 4.8, "flesh", "flesh", knee_mat=None, lean=-4, bend=6, w=7.0, cuff=False)
    for side in (1, -1):
        stitches(k, k.parts["thigh_" + ("l" if side > 0 else "r")], (side * 4.8 - 2.0, 18.0, 4.0), (side * 4.8 + 1.0, 11.0, 4.0))
    to = k.part("torso", (0, 20, 0), (("x", 12),), "hips")
    k.stack(to, 0, 0, [(20, 16, 11.4), (25, 20, 12.6), (30, 24, 13.6), (34.4, 24, 13.0), (37, 18, 10.6)], "flesh", "chest")
    stitches(k, to, (-6.0, 34.0, 6.9), (5.0, 22.0, 6.4), 7)
    stitches(k, to, (6.0, 33.0, 6.8), (8.0, 25.0, 6.4), 4)
    # the vat cage: iron hoops round it and bars between, bent out at the front where it burst
    for y in (22.0, 30.0):
        k.ring(to, 0, y, 0, 12.4, 1.4, "iron", "cage_hoop", n=18, axis="y")
    for i in range(10):
        a = i * 2 * math.pi / 10
        x, z = math.cos(a) * 12.4, math.sin(a) * 8.0
        bend = 3.0 if abs(a - math.pi / 2) < 0.8 else 0.0
        k.limb(to, (x, 20.0, z), (x * 1.0 + bend * math.cos(a), 33.0, z + bend), 1.2, "iron", "cage_bar")
    for i in range(4):                            # tubes hanging out of its back
        tube(k, to, [(-4.0 + i * 2.6, 32.0, -6.4), (-4.4 + i * 2.6, 26.0, -9.0), (-3.6 + i * 2.8, 18.0, -8.0)], 1.0, "brass" if i % 2 else "oil")
    hd = k.part("head", (0, 37.0, 3.0), (("x", -18),), "torso")
    k.box(hd, C(0, 37.4, 3.4, 5.0, 5.4, 5.0), "flesh", tag="small_head")
    k.box(hd, C(0, 37.8, 5.95, 2.6, 2.0, 0.3), "dark", tag="mouth")
    for sx in (-1, 1):
        k.box(hd, C(sx * 1.2, 40.6, 5.95, 0.8, 0.8, 0.3), "eye", tag="eye")
    stitches(k, hd, (-2.4, 42.6, 3.4), (2.4, 42.8, 3.4), 4)
    arms(k, to, 13.0, 34, "flesh", {1: ((("x", -30), ("z", -10)), (("x", -40),)), -1: ((("x", -50), ("z", 16)), (("x", -30),))}, w=4.8, long=1.1)
    # the right arm: swollen, boiling
    ar, fr = k.parts["arm_r"], k.parts["fore_r"]
    k.blob(ar, (-13.4, 29.0, 0), (5.4, 6.0, 5.4), "flesh", "swollen_arm", step=0.9)
    k.blob(fr, (-13.4, 20.0, 0), (5.8, 6.4, 5.8), "flesh", "swollen_fore", step=0.9)
    boils(k, ar, (-17.0, 30.0, 0), 6, 4.0, seed=2)
    boils(k, fr, (-13.4, 20.0, 5.0), 8, 4.6, seed=5)
    for b in list(k.s.boxes):
        if b.part is k.parts["hand_r"]:
            k.s.boxes.remove(b)
    y = 34 - 8 * 1.1 - 7.6 * 1.1
    k.blob(k.parts["hand_r"], (-13.4, y - 3.6, 0.4), (4.8, 4.4, 5.0), "flesh", "swollen_fist", step=0.8)
    k.ring(k.parts["fore_l"], 13.0, 22.0, 0, 3.0, 1.0, "iron", "shackle", n=10, axis="y")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.3)
    return k.s, k.parts


# ================================================================ the Alchemist (caster)

def alchemist():
    """The alchemists who survived their own work: long black oilcloth aprons over coats burned through in spots, a
    leather mask with two round green lenses and a filter like a beak, a bandolier of flasks of every colour of
    poison, and a staff of brass pipe with an alembic at the top, bubbling, that they pour from."""
    k = X.Kit("alchemist")
    hips = k.part("hips", (0, 21, 0))
    k.stack(hips, 0, 0, [(2, 13.0, 10.6), (10, 11.6, 9.0), (21, 10.6, 7.8)], "oil", "long_coat", step=1.0)
    k.box(hips, C(0, 2.0, 4.8, 8.6, 18.0, 0.8), "leather", tag="apron")
    for x, y in ((-2.6, 6.0), (2.0, 10.0), (0.6, 14.4)):
        k.box(hips, C(x, y, 5.3, 1.8, 1.8, 0.3), "acid", tag="burn_hole")
    for side, nm in ((1, "l"), (-1, "r")):
        th = k.part("thigh_" + nm, (side * 3.0, 20, 0), (), hips)
        sh = k.part("shin_" + nm, (side * 3.0, 11, 0), (), th)
        ft = k.part("foot_" + nm, (side * 3.0, 2.4, 0), (), sh)
        k.box(ft, C(side * 3.0, 0, 3.0, 3.6, 2.0, 5.0), "leather", tag="foot")
    to = k.part("torso", (0, 21, 0), (("x", 10),), "hips")
    k.stack(to, 0, 0, [(21, 10.6, 7.8), (26, 11.0, 7.8), (31, 12.4, 8.2), (34, 11.6, 7.6)], "oil", "coat")
    k.box(to, C(0, 21.0, 4.0, 8.6, 12.0, 0.8), "leather", tag="apron_bib")
    k.limb(to, (6.0, 33.6, 4.6), (-5.6, 21.6, 4.8), 2.0, "leather", "bandolier", d=0.6)
    for i, c in enumerate(("acid", "blood", "glass", "acid", "brass")):
        t = 0.15 + i * 0.17
        p = (6.0 - 11.6 * t, 33.6 - 12.0 * t, 5.4)
        k.box(to, C(p[0], p[1] - 1.8, p[2], 1.4, 2.2, 1.4), c, tag="flask")
        k.box(to, C(p[0], p[1] + 0.4, p[2], 0.7, 0.8, 0.7), "brass", tag="flask_neck")
    hd = k.part("head", (0, 34, 0.6), (("x", -10),), "torso")
    k.box(hd, C(0, 34.4, 0.6, 6.0, 7.0, 6.0), "leather", tag="mask")
    for sx in (-1, 1):                            # the round lenses
        k.ring(hd, sx * 1.5, 37.4, 3.7, 1.2, 0.5, "brass", "lens_rim", n=10, axis="z")
        k.box(hd, C(sx * 1.5, 36.6, 3.7, 1.8, 1.6, 0.4), "eye", tag="eye")
    k.shard(hd, (0, 35.6, 3.6), (0, -0.5, 1), 3.4, 2.2, mat="leather", tag="filter_beak")
    k.box(hd, C(0, 34.0, 5.6, 1.6, 1.0, 1.6), "brass", tag="filter_cap")
    k.blob(hd, (0, 39.2, 0.2), (3.6, 1.4, 3.6), "oil", "hood_top", step=0.6)
    k.box(hd, C(0, 33.0, -2.4, 6.8, 6.0, 1.4), "oil", tag="hood_back")
    arms(k, to, 6.8, 32, "oil", {1: ((("x", -60), ("z", -10)), (("x", -30),)), -1: ((("x", -40), ("z", 8)), (("x", -40),))}, glove="leather", w=3.4)
    k.box(k.parts["hand_l"], C(6.8, 9.0, 1.4, 1.8, 3.0, 1.8), "acid", tag="flask_held")
    st = held(k, "alembic_staff", "r", (-6.8, 14.4, 0.4), (("x", 80),))
    k.limb(st, (-6.8, -6.0, 0.4), (-6.8, 26.0, 0.4), 1.2, "brass", "pipe_staff")
    for y in (0.0, 10.0, 20.0):
        k.box(st, C(-6.8, y, 0.4, 1.8, 1.0, 1.8), "iron", tag="pipe_joint")
    k.blob(st, (-6.8, 29.0, 0.4), (2.6, 2.8, 2.6), "glass", "alembic", step=0.5)
    k.blob(st, (-6.8, 28.4, 0.4), (2.0, 1.8, 2.0), "acid", "alembic_brew", step=0.5)
    k.limb(st, (-6.8, 31.4, 0.4), (-6.8, 33.4, 0.4), 1.0, "glass", "alembic_neck")
    k.limb(st, (-6.8, 33.4, 0.4), (-6.8, 31.6, 4.4), 0.6, "glass", "alembic_spout")
    k.box(st, C(-6.8, 30.6, 4.4, 0.6, 1.0, 0.6), "acid", tag="drip")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Stitched Stalker (skirmisher)

def stitched_stalker():
    """Sewn out of the failures that were left over: a lean thing of mismatched flesh, every seam stitched black, a
    second pair of small arms grafted on its back that won't stop moving, long claws of bone set in its fingers, and
    a sack sewn over its head with one green eye cut in it."""
    k = X.Kit("stitched_stalker")
    hips = k.part("hips", (0, 19, 0))
    k.stack(hips, 0, 0, [(12, 9.6, 7.0), (19, 10.0, 7.2)], "oil", "rags")
    legs(k, hips, 18, 9.8, 3.0, "flesh", "flesh", knee_mat=None, lean=-14, bend=24, w=4.2, cuff=False)
    for side in (1, -1):
        nm = "l" if side > 0 else "r"
        stitches(k, k.parts["thigh_" + nm], (side * 3.0 - 1.6, 17.0, 2.2), (side * 3.0 + 1.4, 11.0, 2.2), 4)
        k.box(k.parts["shin_" + nm], C(side * 3.0, 5.0, 2.3, 4.6, 0.4, 0.3), "thread", tag="seam")
    to = k.part("torso", (0, 19, 0), (("x", 26),), "hips")
    k.stack(to, 0, 0, [(19, 10.0, 7.2), (24, 10.4, 7.2), (28.6, 12.4, 7.8), (31.6, 11.4, 7.2)], "flesh", "torso")
    stitches(k, to, (-4.0, 30.0, 3.8), (3.6, 20.0, 3.8), 6)
    stitches(k, to, (-5.6, 26.0, 3.6), (5.6, 26.6, 3.6), 5)
    for i in range(5):                            # ribs showing under the thin skin
        k.box(to, C(-2.6, 21.0 + i * 1.6, 3.7, 2.4, 0.4, 0.3), "dark", tag="rib_line")
    # the grafted arms on its back
    for sx in (-1, 1):
        a0 = (sx * 3.0, 29.0, -3.6)
        a1 = (sx * 7.4, 31.0, -7.4)
        a2 = (sx * 9.6, 26.0, -6.0)
        k.limb(to, a0, a1, 1.8, "flesh", "graft_arm")
        k.limb(to, a1, a2, 1.6, "flesh", "graft_fore")
        stitches(k, to, (sx * 2.0, 30.0, -3.8), (sx * 4.0, 28.0, -3.8), 3)
        for t in (-0.8, 0.8):
            k.shard(to, a2, (sx * 0.3 + t * 0.2, -1, 0.3), 2.6, 0.5, mat="bone", tag="graft_claw")
    hd = k.part("head", (0, 31.6, 0.6), (("x", -24),), "torso")
    k.box(hd, C(0, 32.0, 0.6, 5.6, 6.6, 5.8), "leather", tag="sack_head")
    k.box(hd, C(0, 31.6, 0.6, 6.2, 1.4, 6.4), "thread", tag="sack_cord")
    k.box(hd, C(1.2, 35.0, 3.55, 1.6, 1.4, 0.3), "eye", tag="eye")             # one green eye cut in it
    stitches(k, hd, (-2.4, 37.8, 3.55), (2.4, 37.4, 3.55), 4)
    stitches(k, hd, (-1.6, 33.0, 3.55), (-1.6, 36.4, 3.55), 2)
    arms(k, to, 6.4, 29, "flesh", {1: ((("x", -20), ("z", 30)), (("x", -60),)), -1: ((("x", -60), ("z", -24)), (("x", -40),))}, glove="flesh", w=3.0, long=1.12)
    for side, nm in ((1, "l"), (-1, "r")):
        x = side * 6.4
        stitches(k, k.parts["arm_" + nm], (x - 1.4, 27.0, 1.6), (x + 1.4, 24.0, 1.6), 3)
        y = 29 - 8 * 1.12 - 7.6 * 1.12
        for t in (-1.0, 0, 1.0):                  # the bone claws
            k.limb(k.parts["hand_" + nm], (x + t, y - 2.6, 1.0), (x + t * 1.2, y - 9.0, 2.4), 0.8, "bone", "bone_claw")
            k.shard(k.parts["hand_" + nm], (x + t * 1.2, y - 9.0, 2.4), (0, -1, 0.3), 2.0, 0.6, mat="bone", tag="claw_tip")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts


# ================================================================ the Chimera (elite)

def chimera():
    """The great work walked out of its vat on the alchemists' last night. A giant sewn from many: two heads on one
    pair of shoulders - a man's, eyes stitched shut, and a beast's, all jaw - a crab's great claw grafted where the
    left arm was, a glass tank set into its chest with a heart floating in it, beating green, tubes in its back, and
    in its right hand the surgeon's saw it took from the table, as long as a sword."""
    k = X.Kit("chimera")
    hips = k.part("hips", (0, 21, 0))
    k.stack(hips, 0, 0, [(12, 13.4, 9.6), (21, 13.6, 9.6)], "oil", "rubber_wraps")
    k.box(hips, C(0, 20.0, 0, 14.4, 2.4, 10.4), "leather", tag="belt")
    for i, x in enumerate((-4.6, 0, 4.6)):
        k.box(hips, C(x, 8.0 + (i % 2) * 2.0, 5.0, 3.4, 12.0 - (i % 2) * 2.0, 0.6), "oil", tag="apron_strip")
    legs(k, hips, 20, 10.8, 3.8, "flesh", "flesh", knee_mat="iron", lean=-6, bend=8, w=6.0, cuff=False)
    for side in (1, -1):
        stitches(k, k.parts["thigh_" + ("l" if side > 0 else "r")], (side * 3.8, 19.0, 3.2), (side * 3.8, 12.0, 3.2), 4)
        k.box(k.parts["shin_" + ("l" if side > 0 else "r")], C(side * 3.8, 1.0, 0, 7.0, 4.0, 7.4), "iron", tag="iron_boot")
    to = k.part("torso", (0, 21, 0), (("x", 8),), "hips")
    k.stack(to, 0, 0, [(21, 13.6, 9.6), (26, 15.6, 10.2), (31, 19.0, 11.0), (35, 19.4, 10.6), (37, 15.0, 8.8)], "flesh", "torso")
    # the tank in the chest: a brass frame, glass, the heart in green fluid
    k.box(to, C(0, 25.0, 5.2, 8.4, 9.0, 1.0), "brass", tag="tank_frame")
    k.box(to, C(0, 25.8, 5.6, 6.6, 7.4, 0.8), "acid", tag="tank_fluid")
    k.blob(to, (0, 29.4, 6.2), (1.8, 2.2, 0.9), "blood", "floating_heart", step=0.5)
    k.box(to, C(0, 26.4, 6.4, 6.0, 6.4, 0.3), "glass", tag="tank_glass")
    for x, y in ((-3.8, 25.4), (3.8, 25.4), (-3.8, 33.4), (3.8, 33.4)):
        k.box(to, C(x, y, 5.8, 1.0, 1.0, 0.6), "iron", tag="bolt")
    stitches(k, to, (-9.0, 34.0, 4.6), (-5.0, 25.0, 5.2), 5)
    stitches(k, to, (9.0, 35.0, 4.4), (5.6, 26.0, 5.2), 5)
    for i in range(3):
        tube(k, to, [(-3.0 + i * 3.0, 34.0, -5.2), (-3.4 + i * 3.4, 30.0, -8.4), (-2.6 + i * 3.6, 22.0, -7.4)], 1.2, "brass" if i != 1 else "oil")
    # two heads: the man's (left), the beast's (right)
    hd = k.part("head", (0, 37.0, 1.0), (("x", -6),), "torso")
    k.box(hd, C(3.4, 37.2, 1.4, 5.6, 6.6, 5.6), "flesh", tag="man_head")
    stitches(k, hd, (1.4, 40.0, 4.25), (5.4, 40.0, 4.25), 3)                     # eyes stitched shut
    k.box(hd, C(3.4, 38.2, 4.25, 2.0, 0.4, 0.3), "dark", tag="man_mouth")
    k.blob(hd, (3.4, 43.0, 1.0), (2.8, 1.2, 2.8), "dark", "man_hair", step=0.5)
    k.box(hd, C(-4.2, 36.0, 2.0, 7.0, 6.4, 7.0), "flesh", tag="beast_head")
    k.box(hd, C(-4.2, 35.0, 6.4, 6.0, 3.6, 4.6), "flesh", tag="beast_snout")
    k.box(hd, C(-4.2, 34.2, 8.2, 5.0, 1.4, 1.4), "dark", tag="beast_maw")
    for t in (-1.8, -0.6, 0.6, 1.8):
        k.shard(hd, (-4.2 + t, 35.6, 8.8), (0, -1, 0.1), 1.8, 0.6, mat="bone", tag="fang")
        k.shard(hd, (-4.2 + t, 34.0, 8.6), (0, 1, 0.1), 1.2, 0.5, mat="bone", tag="fang")
    k.box(hd, C(-5.6, 40.0, 5.55, 1.2, 0.8, 0.3), "eye", tag="eye")
    k.box(hd, C(-2.8, 40.0, 5.55, 1.2, 0.8, 0.3), "eye", tag="eye")
    for sx in (-6.6, -1.8):
        k.shard(hd, (sx, 42.0, 1.6), (0, 1, -0.3), 3.0, 1.2, mat="bone", tag="beast_horn")
    stitches(k, hd, (0, 34.4, 3.0), (0, 42.0, 3.0), 4)
    arms(k, to, 10.6, 34, "flesh", {1: ((("x", -30), ("z", -14)), (("x", -30),)), -1: ((("x", -36), ("z", 16)), (("x", -44),))}, glove="flesh", w=4.4, long=1.08)
    # the crab claw grafted at the left elbow
    for b in list(k.s.boxes):
        if b.part is k.parts["hand_l"] or (b.part is k.parts["fore_l"] and b.tag == "forearm"):
            k.s.boxes.remove(b)
    fo = k.parts["fore_l"]
    stitches(k, fo, (8.6, 25.4, 2.4), (12.6, 25.4, 2.4), 3)
    k.blob(fo, (10.6, 21.0, 0), (3.4, 4.6, 3.4), "crab", "claw_arm", step=0.7)
    k.blob(fo, (10.6, 14.0, 0.6), (4.2, 4.0, 4.4), "crab", "claw_palm", step=0.7)
    k.limb(fo, (10.6, 11.0, 2.4), (10.6, 4.0, 4.6), 3.2, "crab", "claw_finger", d=2.4)
    k.shard(fo, (10.6, 4.0, 4.6), (0, -0.6, 0.8), 2.4, 1.6, mat="crab", tag="claw_point")
    k.limb(fo, (10.6, 11.0, -1.4), (10.6, 5.0, 0.2), 2.4, "crab", "claw_thumb", d=2.0)
    for i in range(4):
        k.box(fo, C(10.6 + (i % 2) * 1.4 - 0.7, 12.0 + i * 1.6, 4.6, 0.8, 0.8, 0.4), "bone", tag="claw_spot")
    # the surgeon's saw in the right hand
    sw = held(k, "bone_saw", "r", (-10.6, 14.0, 0.3), (("x", 78), ("z", -14)))
    k.limb(sw, (-10.6, 6.0, 0.3), (-10.6, 15.0, 0.3), 1.6, "leather", "grip")
    k.box(sw, C(-10.6, 15.0, 0.3, 2.4, 1.4, 3.0), "brass", tag="ferrule")
    k.box(sw, C(-10.6, 16.4, 1.0, 1.0, 26.0, 4.4), "steel", tag="saw_blade")
    k.box(sw, C(-10.6, 16.4, -1.6, 1.6, 26.0, 1.0), "brass", tag="saw_spine")
    for i in range(12):
        k.shard(sw, (-10.6, 17.4 + i * 2.1, 3.2), (0, 0.3, 1), 1.4, 0.8, mat="steel", tag="saw_tooth")
    k.box(sw, C(-10.6, 22.0, 3.2, 1.1, 6.0, 0.3), "blood", tag="blood_on_teeth")
    lit(k, GLOWS)
    k.s.shaders = shaders()
    grow(k, 1.2)
    return k.s, k.parts


MOBS = {
    "acid_slug": dict(make=acid_slug, rig="crawler", ent=(1.0, 1.0), stats=dict(hp=26, speed=0.24, dmg=6, armor=1, kb=0)),
    "vat_guard": dict(make=vat_guard, ent=(0.9, 2.9), stats=dict(hp=60, speed=0.23, dmg=10, armor=8, kb=0.3)),
    "vat_brute": dict(make=vat_brute, ent=(1.9, 4.0), stats=dict(hp=210, speed=0.18, dmg=19, armor=6, kb=1.0)),
    "alchemist": dict(make=alchemist, ent=(0.9, 2.8), stats=dict(hp=38, speed=0.22, dmg=8, armor=2, kb=0)),
    "stitched_stalker": dict(make=stitched_stalker, ent=(0.8, 2.4), stats=dict(hp=42, speed=0.35, dmg=8, armor=2, kb=0)),
    "chimera": dict(make=chimera, ent=(1.2, 3.6), stats=dict(hp=340, speed=0.24, dmg=16, armor=11, kb=0.7), key=True),
}
