"""What the cube townsfolk carry and wear over their clothes (tools/mcstyle.py's Folk): weapons and tools in the
hand, shields, things on the back and the belt, props, headwear, armour pieces, the cut of the top, face marks and
builds - all read from the NPC forge's spec, so a guard reads as a guard and a smith as a smith.

Boxes are in the model's px (x to its left, y up, z forward, feet at 0). Rigid things carry an anchor and a bone:
tools/mcexport.py moves the anchor with the body and keeps the thing whole (hand_r/hand_l ride the forearm,
back the chest, hip the waist, shoulder_r/shoulder_l the upper arm)."""
import math

import mcstyle as M
from mcstyle import GOLD, flat, hairy, lit, look, mix, ramp5, rgb, tint

WOOD = ramp5("#7a5230")
DARKWOOD = ramp5("#4a3020")
STRAW = ramp5("#d8b456")
LINEN = None
PARCH = ramp5("#e8dcb8")


def metal(f):
    rk = f.s.get("rank")
    name = M.LOOKS["ranks"][rk]["metal"] if rk in M.LOOKS["ranks"] else "iron"
    return [rgb(x) for x in M.LOOKS["metal"].get(name, M.LOOKS["metal"]["iron"])]


def trim(f):
    rk = f.s.get("rank")
    name = M.LOOKS["ranks"][rk].get("trim") if rk in M.LOOKS["ranks"] else None
    return [rgb(x) for x in M.LOOKS["metal"][name]] if name in M.LOOKS["metal"] else None


def glow(f):
    role = f.s.get("role")
    name = {"white_mage": "holy", "black_mage": "violet", "acolyte": "holy"}.get(role, "lamp")
    if role == "black_mage" and f.acc[2] in (look("cloth", "wine")[2], look("cloth", "red")[2], look("cloth", "oxblood")[2]):
        name = "red"
    return [rgb(x) for x in M.LOOKS["glow"][name]]


def edged(R, base=2, edge=1):
    """a material with a darker rim on every face, so small things keep their shape"""
    def p(face, i, j, fw, fh):
        c = lit(face, j, fh, R, base)
        if fw > 2 and fh > 2 and (i in (0, fw - 1) or j in (0, fh - 1)):
            return tint(c, 0.8)
        return c
    return p


def bands(R, band, every=3, base=2):
    """a material crossed by bands (hoops on a bucket, rings on a staff)"""
    def p(face, i, j, fw, fh):
        if face not in ("top", "bottom") and j % every == 0:
            return lit(face, j, fh, band, 2)
        return lit(face, j, fh, R, base)
    return p


def shining(R):
    """glowing glass: a bright core, a darker rim"""
    def p(face, i, j, fw, fh):
        if fw > 2 and fh > 2 and (i in (0, fw - 1) or j in (0, fh - 1)):
            return R[2]
        return R[4] if (i + j) % 3 == 0 else R[3]
    return p


# ================================================================== builds

BUILDS = {"broad": dict(body=(9, 12, 5), leg=(4.5, 12, 4.5), arm=(4, 12, 4)),
          "stout": dict(body=(10, 11, 6), leg=(5, 11, 5), arm=(4, 11, 4))}


def build(f):
    """broad and stout bodies for grown humans and demons (dwarves are stout already, elves stay slim)"""
    b = f.s.get("build")
    if b in BUILDS and f.age in ("adult", "elder") and f.race in (None, "human", "demon"):
        plan = dict(BUILDS[b])
        if f.race == "demon":
            plan["body"] = (plan["body"][0] + 0.5, plan["body"][1] + (1 if b == "broad" else 1), plan["body"][2])
            plan["leg"] = (plan["leg"][0], plan["leg"][1] + 1, plan["leg"][2])
            plan["arm"] = (plan["arm"][0], plan["arm"][1] + 1, plan["arm"][2])
        if f.age == "elder":
            plan = {k: (v[0], v[1] - 1, v[2]) for k, v in plan.items()}
            plan["hunch"] = f.plan.get("hunch", 0)
        f.plan.update(plan)


# ================================================================== paint over the clothes

def body(f, base):
    """the cut of the top and what's worn over it"""
    o = f.s["outfit"]
    kind = o.get("top", "tunic")
    overs = o.get("overs", [])
    top, acc, lea, S = f.top, f.acc, f.lea, f.skin
    MT = metal(f)
    TR = trim(f) or GOLD

    def p(face, i, j, fw, fh):
        c = base(face, i, j, fw, fh)
        mid = fw / 2
        belt = round(fh * 0.68)
        side = face in ("front", "back")
        if face in ("top", "bottom"):
            if kind in ("mail", "cuirass"):
                return MT[3] if face == "top" else MT[1]
            return c
        # the diagonal bands first: they lie over everything
        if side and ("sash" in overs or "strap" in overs):
            d = (i - j * fw / fh * 0.9) if face == "front" else (fw - 1 - i - j * fw / fh * 0.9)
            if 0 <= d + fw * 0.15 < 2 and j < belt + 1:
                return lit(face, j, fh, acc if "sash" in overs else lea, 3 if "sash" in overs else 2)
        if side and "satchel" in overs and abs((fw - 1 - i if face == "front" else i) - j * fw / fh * 0.9 - 1) < 0.7 and j < belt:
            return lea[2]
        if side and "tabard" in overs and 1 <= i < fw - 1 and j >= 1:
            if face == "front" and j in (3, 4) and mid - 1 <= i < mid + 1:
                return TR[3]                                   # the badge
            if face == "front" and j == 4 and i in (int(mid) - 2, int(mid) + 1):
                return TR[2]
            if j == belt:
                return lea[2]
            return lit(face, j, fh, acc, 2) if i not in (1, fw - 2) else acc[1]
        if face == "front" and "bodice" in overs and 2 <= j <= belt and mid - 2 <= i < mid + 2:
            if mid - 1 <= i < mid + 1:
                return (acc[3] if (j % 2) else lea[1])
            return lea[2]
        if face == "front" and "leather_apron" in overs and (j >= 2 and mid - 3 <= i < mid + 3 or j < 2 and i in (int(mid) - 3, int(mid) + 2)):
            return lea[3] if j == 2 else lit(face, j, fh, lea, 2)
        if face == "front" and "vials" in overs and j == belt - 1 and i in (1, 2, fw - 3):
            return [rgb("#e04040"), rgb("#40c0e0"), rgb("#60e070")][i % 3]
        if "patch" in overs and face == "front" and (i, j) in ((1, belt - 2), (2, belt - 2), (1, belt - 1), (2, belt - 1)):
            return tint(acc[2], 0.9) if kind not in ("mail", "cuirass") else c
        # the cut of the top
        if kind == "mail":
            if j == belt and (face != "front" or not (mid - 1 <= i < mid + 1)):
                return lea[2] if face != "back" else lea[1]
            if face == "front" and j == 0 and mid - 1 <= i < mid + 1:
                return S[3]
            k = 2 + (0.5 if face == "front" else 0) - (0.6 if face == "back" else 0)
            k += 0.5 if j == 0 else 0
            v = MT[max(0, min(4, int(round(k))))]
            return tint(v, 0.84) if (i + j) % 2 else v
        if kind == "cuirass":
            if j == belt:
                return lea[2]
            if j > belt:
                return lit(face, j, fh, MT, 2) if (j - belt) % 2 else MT[1]
            if face == "front" and mid - 1 <= i < mid + 1:
                return MT[4]                                   # the ridge down the breastplate
            if j == 0:
                return TR[3]
            return lit(face, j, fh, MT, 2 if face == "front" else 1)
        if kind == "jerkin":
            if face == "front" and mid - 1 <= i < mid + 1 and j < belt:
                return S[2] if j < 2 else (lea[4] if (j + i) % 2 else lea[1])
            if j == belt:
                return lea[0]
            return lit(face, j, fh, lea, 2) if not (i in (0, fw - 1) and side) else lea[1]
        if kind == "gambeson":
            if j % 3 == 2 or i % 3 == 0 and side:
                return tint(c, 0.8)
            return c
        if kind in ("shirt", "blouse"):
            if face == "front" and j <= 1 and mid - 1 <= i < mid + 1:
                return S[3] if j == 0 else S[2]
            if kind == "blouse" and j == 0:
                return tint(top[4], 1.04)
            if kind == "blouse" and face == "front" and 2 <= j <= 4 and mid - 1 <= i < mid + 1 and j % 2 == 0:
                return acc[3]
        if kind == "dress" and face == "front" and j < belt and mid - 2 <= i < mid + 2 and j >= 2:
            return acc[3] if mid - 1 <= i < mid + 1 and j % 2 == 0 else top[3]          # a laced bodice
        return c
    return p


def arms(f, base):
    o = f.s["outfit"]
    overs = o.get("overs", [])
    kind = o.get("top")
    MT = metal(f)
    sl = o.get("sleeves", "long")

    def p(face, i, j, fw, fh):
        c = base(face, i, j, fw, fh)
        if "gauntlets" in overs and j >= fh - 3:
            return lit(face, j, fh, MT, 2) if face != "bottom" else MT[1]
        if "bracers" in overs and fh - 6 <= j < fh - 3 and face != "top":
            return f.lea[3] if j == fh - 6 else lit(face, j, fh, f.lea, 2)
        if kind == "mail" and sl == "long" and j < fh - 3 and face not in ("top", "bottom"):
            v = lit(face, j, fh, MT, 2)
            return tint(v, 0.84) if (i + j) % 2 else v
        if kind == "cuirass" and j < fh // 3 and face not in ("bottom",):
            return lit(face, j, fh, MT, 2)
        return c
    return p


def legs(f, base):
    overs = f.s["outfit"].get("overs", [])
    MT = metal(f)

    def p(face, i, j, fw, fh):
        c = base(face, i, j, fw, fh)
        if "greaves" in overs and face in ("front", "left", "right") and fh * 0.5 <= j < fh - max(2, round(fh * 0.25)):
            return lit(face, j, fh, MT, 2) if not (face == "front" and i == fw // 2) else MT[4]
        return c
    return p


def face(f, i, j, c):
    """marks on the face (None: leave it to the face painter)"""
    fc = f.s["face"]
    marks = fc.get("marks", [])
    S = f.skin
    if "blindfold" in marks and j in (3, 4):
        return f.acc[2] if j == 4 else f.acc[3]
    if "patch_r" in marks:
        if j == 4 and i in (1, 2) or j == 3 and i in (0, 1, 2) or j == 2 and i in (3, 4, 5, 6, 7):
            return (24, 20, 20) if j >= 3 else f.lea[1]
    if "scar" in marks and i == 5 and 2 <= j <= 5 and j != 4:
        return mix(S[2], (180, 80, 80), 0.45)
    if "scar_cheek" in marks and (i, j) in ((6, 5), (7, 6), (5, 6)):
        return mix(S[2], (180, 80, 80), 0.45)
    if "warpaint" in marks and j == 5 and i in (0, 1, 2, 5, 6, 7):
        return f.acc[2]
    if "wrinkles" in marks and (i, j) in ((0, 4), (7, 4)):
        return S[2]
    if f.s.get("beard") == "stubble" and (j == 7 or j == 6 and i in (0, 1, 2, 5, 6, 7)):
        return mix(c, f.hair[1], 0.35)
    return None


# ================================================================== the things they carry

def held(f, side, item):
    """an item in a hand (side 'r' or 'l'); 'hold' carries it upright before them, else it hangs at the side"""
    P = f.plan
    bw, bh, bd = P["body"]
    aw, ah, ad = P["arm"]
    if f.slim and f.race != "dwarf":
        aw = min(aw, 3)
    hy = P["leg"][1] + bh
    sx = -1 if side == "r" else 1
    cx = sx * (bw / 2 + aw / 2)
    ay = hy - ah + 1.0
    A = (cx, ay, 0.0)
    bone = "hand_" + side
    up = (f.s.get("pose") or {}).get(side) == "hold"
    down = not up and item in ("mace", "axe", "hammer")      # hanging at the side, head down
    MT, add = metal(f), f.add

    def put(nm, lo, size, paint, rot=(), pivot=None, inflate=0.0):
        if down:
            lo = (lo[0], -lo[1] - size[1], lo[2])
            rot = tuple((a, -d) if a in ("x", "z") else (a, d) for a, d in rot)
            pivot = (pivot[0], -pivot[1], pivot[2]) if pivot else None
        add(nm, (cx + lo[0], ay + lo[1], lo[2]), size, paint, inflate, rot, (cx + pivot[0], ay + pivot[1], pivot[2]) if pivot else None,
            True, bone=bone, anchor=A)

    def shaft(lo_y, hi_y, R=WOOD, w=1.0, z=1.6):
        put("shaft", (-w / 2, lo_y, z - w / 2), (w, hi_y - lo_y, w), flat(R, 2))
    z = 1.6 if up else ad / 2 + 0.6 if item in ("staff", "spear") else 0.0    # long things before the fist, clear of the forearm
    if item == "staff":
        G = glow(f)
        shaft(-9, 20, DARKWOOD if f.s.get("role") == "black_mage" else WOOD, 1.2, z)
        put("collar", (-1, 19, z - 1), (2, 1.2, 2), flat(MT, 3))
        put("prong", (-1.8, 20, z - 0.4), (0.8, 3.4, 0.8), flat(MT, 2))
        put("prong", (1.0, 20, z - 0.4), (0.8, 3.4, 0.8), flat(MT, 2))
        put("orb", (-1.25, 20.4, z - 1.25), (2.5, 2.5, 2.5), shining(G))
    elif item == "spear":
        shaft(-10, 22, WOOD, 1.0, z)
        put("collar", (-0.8, 21.5, z - 0.8), (1.6, 1.2, 1.6), flat(MT, 2))
        put("tip", (-0.9, 22.5, z - 0.3), (1.8, 4.5, 0.6), edged(MT, 3))
        put("tip", (-0.5, 26.8, z - 0.3), (1.0, 1.2, 0.6), flat(MT, 4))
    elif item == "sword":
        if up:
            put("grip", (-0.5, -1, z - 0.5), (1, 3.5, 1), flat(f.lea, 2))
            put("guard", (-2, 2.5, z - 0.7), (4, 1, 1.4), flat(MT, 3))
            put("blade", (-0.8, 3.5, z - 0.3), (1.6, 12, 0.6), edged(MT, 3))
            put("pommel", (-0.7, -2, z - 0.7), (1.4, 1, 1.4), flat(MT, 2))
        else:
            rot, pv = (("x", -25),), (0, 0, 0)
            put("grip", (-0.5, -2, -0.5), (1, 3.5, 1), flat(f.lea, 2), rot, pv)
            put("guard", (-0.7, -3, -2), (1.4, 1, 4), flat(MT, 3), rot, pv)
            put("blade", (-0.3, -15, -0.8), (0.6, 12, 1.6), edged(MT, 3), rot, pv)
            put("pommel", (-0.7, 1.5, -0.7), (1.4, 1, 1.4), flat(MT, 2), rot, pv)
    elif item == "mace":
        shaft(-3, 8, DARKWOOD, 1.0, z)
        put("head", (-1.5, 7, z - 1.5), (3, 3, 3), edged(MT, 3))
        for dx, dz in ((-2.1, -0.4), (1.3, -0.4)):
            put("flange", (dx, 7.3, z + dz), (0.8, 2.4, 0.8), flat(MT, 2))
        for dz in (-2.1, 1.3):
            put("flange", (-0.4, 7.3, z + dz), (0.8, 2.4, 0.8), flat(MT, 2))
    elif item == "axe":
        shaft(-3, 12, WOOD, 1.0, z)
        put("head", (-0.3, 9, z + 0.4), (0.6, 3.6, 3.4), edged(MT, 3))
        put("head", (-0.3, 8.4, z + 2.6), (0.6, 4.8, 1.2), flat(MT, 4))
    elif item == "hammer":
        shaft(-3, 9, WOOD, 1.0, z)
        put("head", (-1.2, 8, z - 2), (2.4, 2.4, 4.4), edged(ramp5("#5a5a62"), 2))
        put("face", (-1.3, 7.9, z + 2.3), (2.6, 2.6, 0.4), flat(ramp5("#8a8a92"), 3))
    elif item == "lantern":
        L = [rgb(x) for x in M.LOOKS["glow"]["lamp"]]
        put("bail", (-0.4, -2.5, -0.4), (0.8, 2.5, 0.8), flat(MT, 1))
        put("cap", (-1.8, -3.6, -1.8), (3.6, 1.1, 3.6), flat(ramp5("#3a3a40"), 2))
        put("lamp", (-1.5, -7.6, -1.5), (3, 4, 3), shining(L))
        put("base", (-1.8, -8.6, -1.8), (3.6, 1.0, 3.6), flat(ramp5("#3a3a40"), 2))
    elif item == "mug":
        put("mug", (-1.2, -1.5, 0.5), (2.4, 3, 2.4), bands(WOOD, MT, 2))
        put("foam", (-1.2, 1.5, 0.5), (2.4, 0.6, 2.4), flat(ramp5("#f0e8d0"), 3))
    elif item == "bucket":
        put("bail", (-0.3, -2.4, -0.3), (0.6, 2.4, 0.6), flat(MT, 1))
        put("bucket", (-2, -6.8, -2), (4, 4.4, 4), bands(WOOD, MT, 3))
        put("water", (-1.8, -2.6, -1.8), (3.6, 0.3, 3.6), flat(ramp5("#3a78b0"), 3))
    elif item in ("book", "tome"):
        cov = ramp5("#6a2a2a") if f.s.get("role") != "white_mage" else ramp5("#e0d8c0")
        put("book", (-0.6 if not up else -1.5, -3, -1.6 if not up else z - 0.6), (1.2, 4, 3.2) if not up else (3, 4, 1.2), edged(cov, 2))
    elif item == "cane":
        put("cane", (-0.5, -ay, 1.2), (1, ay + 1.5, 1), flat(WOOD, 2))
        put("cane", (-0.5, 0.5, -0.8), (1, 1, 3), flat(WOOD, 2))
    elif item == "bread":
        put("bread", (-1.4, -2.6, -2.5), (2.8, 2.4, 5), edged(ramp5("#c08a40"), 3))
    elif item == "basket":
        put("basket", (-2.5, -6.5, -2), (5, 3.5, 4), bands(STRAW, ramp5("#a07a30"), 2))
        put("handle", (-0.4, -3, -0.4), (0.8, 3, 0.8), flat(STRAW, 2))
        put("apples", (-2, -3.2, -1.5), (4, 0.6, 3), lambda fc, i, j, fw, fh: rgb("#c03030") if (i + j) % 2 else rgb("#60a040"))
    elif item == "doll":
        put("doll", (-1, -3.5, 0.6), (2, 2.5, 1.4), flat(ramp5("#c06080"), 2))
        put("doll", (-0.9, -1.2, 0.6), (1.8, 1.8, 1.4), flat(ramp5("#f0c8a0"), 3))
    elif item == "flowers":
        put("stems", (-0.6, -1, z + 0.2), (1.2, 4.5, 1.2), flat(ramp5("#3a8030"), 2))
        for k, (dx, dz, col) in enumerate(((-1.4, -0.6, "#e04060"), (0.4, -0.6, "#f0d040"), (-0.5, 0.9, "#c070e0"))):
            put("bloom", (dx, 3.2 + (k % 2) * 0.6, z + dz), (1.4, 1.4, 1.4), flat(ramp5(col), 3))


def shield(f):
    P = f.plan
    bw, bh, bd = P["body"]
    aw, ah, ad = P["arm"]
    hy = P["leg"][1] + bh
    x0 = bw / 2 + aw
    ay = hy - ah + 1.0
    A = (bw / 2 + aw / 2, ay, 0.0)
    MT, TR = metal(f), trim(f) or GOLD
    acc = f.acc

    def face_(fc, i, j, fw, fh):
        if fc in ("top", "bottom", "right", "front", "back"):
            return MT[2]
        if i in (0, fw - 1) or j == 0:
            return MT[3]
        if i == fw // 2 or j == 3:
            return TR[3]                                     # a cross over the field
        return lit("front", j, fh, acc, 2)
    for lo, size in (((x0, ay - 0.5, -3.5), (1, 6, 7)), ((x0, ay - 2.5, -2.5), (1, 2, 5)), ((x0, ay - 3.5, -1.5), (1, 1, 3))):
        f.add("shield", lo, size, face_, 0, (), None, True, bone="hand_l", anchor=A)


def back(f, item):
    P = f.plan
    bw, bh, bd = P["body"]
    lh = P["leg"][1]
    hy = lh + bh
    zb = -bd / 2
    A = (0.0, hy - 3, zb)

    def put(nm, lo, size, paint, rot=(), pivot=None):
        f.add(nm, lo, size, paint, 0, rot, pivot, True, bone="back", anchor=A)
    if item in ("quiver", "bow_quiver"):
        rot = (("z", -20),)
        pv = (1, hy - 6, zb - 1.5)
        put("quiver", (-0.5, hy - 10, zb - 2.8), (3, 9, 2.6), edged(f.lea, 2), rot, pv)
        for k, col in enumerate(("#f0f0e8", "#c03030", "#f0f0e8")):
            put("fletch", (-0.2 + k * 0.9, hy - 1, zb - 2.3), (0.7, 2, 1.4), flat(ramp5(col), 3), rot, pv)
    if item == "bow_quiver":
        cx, cy, r = -1.0, hy - 6, 8.0
        for k in range(7):                                      # the bow's limbs, an arc across the back
            th = math.radians(-60 + 20 * k)
            x, y = cx + r * math.sin(th) * 0.35, cy + r * math.cos(th) * 0 + r * math.sin(th)
            put("bow", (x - 0.6 - 3, y - 1.5, zb - 0.9), (1.2, 3.2, 1.0), flat(WOOD, 2), (("z", -math.degrees(th) * 0.4 + 20),), (x - 3, y, zb - 0.4))
    elif item == "greatsword":
        rot, pv = (("z", 32),), (0, hy - 6, zb - 1)
        MT = metal(f)
        put("blade", (-1.5, hy - 22, zb - 1.4), (3, 16, 0.8), edged(MT, 3), rot, pv)
        put("guard", (-3.5, hy - 6, zb - 1.6), (7, 1.2, 1.2), flat(trim(f) or MT, 3), rot, pv)
        put("grip", (-0.6, hy - 4.8, zb - 1.6), (1.2, 4.5, 1.2), flat(f.lea, 2), rot, pv)
        put("pommel", (-0.9, hy - 0.4, zb - 1.7), (1.8, 1.4, 1.4), flat(trim(f) or MT, 3), rot, pv)
    elif item == "sack":
        L = look("cloth", "linen")
        put("sack", (-3, hy - 10, zb - 3.6), (6.5, 8, 3.6), edged(L, 2), (("z", 8),), (0, hy - 6, zb))
        put("tie", (-1, hy - 2.2, zb - 2.6), (2, 2, 2), flat(L, 3), (("z", 8),), (0, hy - 6, zb))
    elif item == "pack":
        put("pack", (-3.5, hy - 10, zb - 3.2), (7, 8.5, 3.2), edged(f.lea, 2))
        put("flap", (-3.6, hy - 4.5, zb - 3.4), (7.2, 3.2, 3.4), flat(f.acc, 2))
        put("roll", (-4.5, hy - 1.6, zb - 2.8), (9, 2.4, 2.4), bands(look("cloth", "grey"), f.lea, 3))


def hip(f, item):
    P = f.plan
    bw, bh, bd = P["body"]
    lh = P["leg"][1]
    belt = lh + bh - round(bh * 0.68) - 0.5
    MT = metal(f)

    def put(nm, lo, size, paint, rot=(), pivot=None, a=None):
        f.add(nm, lo, size, paint, 0, rot, pivot, True, bone="hip", anchor=a or (lo[0], belt, 0.0))
    if item == "sword":
        x = bw / 2 + 0.2
        rot, pv = (("x", -28),), (x, belt, 0)
        put("scabbard", (x, belt - 11, -0.8), (1.2, 11, 1.6), edged(f.lea, 2), rot, pv)
        put("chape", (x - 0.1, belt - 11.6, -0.9), (1.4, 1.2, 1.8), flat(MT, 2), rot, pv)
        put("guard", (x - 0.2, belt, -1.8), (1.6, 0.9, 3.6), flat(MT, 3), rot, pv)
        put("grip", (x + 0.1, belt + 0.9, -0.5), (1, 3, 1), flat(f.lea, 1), rot, pv)
    elif item == "knife":
        x = -bw / 2 - 0.9
        put("knife", (x, belt - 4, 0.4), (1, 4, 1.4), edged(f.lea, 2))
        put("knife", (x - 0.1, belt, 0.5), (1.2, 1.8, 1.2), flat(WOOD, 2))
    elif item == "daggers":
        for sx in (-1, 1):
            rot, pv = (("z", sx * 35),), (sx * 1.5, belt, -bd / 2)
            put("dagger", (sx * 1.5 - 0.6, belt - 4, -bd / 2 - 1.2), (1.2, 5, 1.0), edged(f.lea, 2), rot, pv)
            put("dagger", (sx * 1.5 - 0.5, belt + 1, -bd / 2 - 1.1), (1.0, 2, 0.8), flat(MT, 3), rot, pv)
    elif item == "tome":
        x = -bw / 2 - 1.3
        cov = ramp5("#4a2a5a") if f.s.get("role") == "black_mage" else ramp5("#6a2a2a")
        put("tome", (x, belt - 4.5, -1.6), (1.3, 4, 3.2), edged(cov, 2))
        put("chain", (x + 0.3, belt - 0.6, -0.3), (0.6, 0.8, 0.6), flat(GOLD, 3))


def kitten(f):
    """a kitten on the left shoulder"""
    P = f.plan
    bw = P["body"][0]
    aw = P["arm"][0]
    hy = P["leg"][1] + P["body"][1]
    x = bw / 2 - 0.5
    A = (x, hy, 0.0)
    K = ramp5("#e09040")

    def put(nm, lo, size, paint):
        f.add(nm, lo, size, paint, 0, (), None, True, bone="back", anchor=A)
    put("kitten", (x - 0.2, hy, -1.8), (2.6, 2.2, 3.6), flat(K, 2))
    put("kitten", (x - 0.4, hy + 1.6, 0.8), (3, 2.6, 2.4), lambda fc, i, j, fw, fh: (20, 20, 20) if fc == "front" and j == 1 and i in (0, 2) else lit(fc, j, fh, K, 3))
    put("kitten", (x - 0.4, hy + 4.2, 1.6), (0.8, 0.8, 0.8), flat(K, 2))
    put("kitten", (x + 1.8, hy + 4.2, 1.6), (0.8, 0.8, 0.8), flat(K, 2))
    put("kitten", (x + 0.8, hy - 2.5, -2.2), (0.8, 3, 0.8), flat(K, 1))


# ================================================================== headwear and over-garments

def headwear(f, hy):
    hw = f.s.get("headwear")
    top = hy + 8
    MT = metal(f)
    add = f.add
    if hw == "witch_hat":
        R = f.top if f.top[2] != f.acc[2] else look("cloth", "black")
        add("hat", (-6.5, top - 0.5, -6.5), (13, 1, 13), flat(R, 2))
        add("hat", (-4.2, top + 0.5, -4.2), (8.4, 1.4, 8.4), flat(f.acc if f.acc[2] != R[2] else look("cloth", "plum"), 3))
        add("hat", (-3.6, top + 1.9, -3.8), (7.2, 3, 7.2), flat(R, 2))
        add("hat", (-2.6, top + 4.6, -3.3), (5.2, 3, 5.2), flat(R, 2), 0, (("x", -10),), (0, top + 4.6, -0.7))
        add("hat", (-1.6, top + 7.0, -3.4), (3.2, 2.8, 3.2), flat(R, 2), 0, (("x", -24),), (0, top + 7.0, -1.8))
        add("hat", (-1.0, top + 8.8, -4.8), (2, 2, 2), flat(R, 3), 0, (("x", -48),), (0, top + 8.8, -3.8))
    elif hw == "helm":
        def helm(face, i, j, fw, fh):
            if face == "bottom":
                return None
            if face == "top":
                return MT[3] if (i + j) % 5 else MT[4]
            if face == "front":
                if j <= 1:
                    return MT[3] if j == 0 else MT[2]
                if i in (3, 4) and j <= 5:
                    return MT[3]                                 # the nasal
                return None
            if j < 6 if face == "back" else j < 4:
                return lit(face, j, fh, MT, 2) if j != 1 else MT[1]
            if face in ("left", "right") and j < 6 and (i < 3 if face == "right" else i > 4):
                return lit(face, j, fh, MT, 2)                   # the cheek guards' backs
            return None
        add("helm", (-4, hy, -4), (8, 8, 8), helm, 0.55)
        add("helm", (-0.8, top + 0.5, -2), (1.6, 1.2, 4), flat(MT, 3))
    elif hw in ("headscarf",):
        R = f.acc

        def scarf(face, i, j, fw, fh):
            if face == "bottom":
                return None
            if face == "top":
                return R[3]
            if face == "front":
                return lit(face, j, fh, R, 2) if j <= 1 or i in (0, 7) and j < 6 else None
            if face == "back":
                return lit(face, j, fh, R, 2)
            return lit(face, j, fh, R, 2) if j < 7 else None
        add("scarf", (-4, hy, -4), (8, 8, 8), scarf, 0.5)
        add("knot", (-1, hy + 0.5, -5.2), (2, 2, 1.2), flat(R, 2))
    elif hw == "straw_hat":
        add("hat", (-6.5, top - 0.5, -6.5), (13, 1, 13), edged(STRAW, 2))
        add("hat", (-4.2, top + 0.5, -4.2), (8.4, 2.6, 8.4), flat(STRAW, 2))
        add("hat", (-4.3, top + 0.5, -4.3), (8.6, 0.8, 8.6), flat(f.acc, 2))
    elif hw == "circlet" and f.race != "elf":
        T = trim(f) or GOLD

        def circ(face, i, j, fw, fh):
            if face in ("top", "bottom") or j != 1:
                return None
            if face == "front" and i in (3, 4):
                return f.acc[4]
            return T[3] if i % 3 else T[2]
        add("circlet", (-4, hy, -4), (8, 8, 8), circ, 0.5)
    elif hw == "bow" and f.age != "kid":
        R = f.acc
        add("bow", (-1, top - 0.5, -5), (2, 2, 1.2), flat(R, 3))
        add("bow", (-3, top - 0.2, -5), (2, 1.6, 1), flat(R, 2))
        add("bow", (1, top - 0.2, -5), (2, 1.6, 1), flat(R, 2))
    elif hw == "bandana":
        add("knot", (-1, hy + 5.2, -5.2), (2, 1.6, 1.2), flat(f.acc, 2))
        add("knot", (-0.5, hy + 3.2, -5.0), (1, 2.2, 0.8), flat(f.acc, 1))
    elif hw == "candles":                                       # a silver band crowned with three lit candles
        T = [rgb(x) for x in M.LOOKS["metal"]["silver"]]
        F = [rgb(x) for x in M.LOOKS["glow"]["lamp"]]

        def band(face, i, j, fw, fh):
            return None if face in ("top", "bottom") or j != 0 else T[3] if i % 2 else T[2]
        add("band", (-4, hy, -4), (8, 8, 8), band, 0.5)
        for dx, h in ((-3, 3.0), (-0.75, 4.0), (1.5, 3.0)):
            add("candle", (dx, top + 0.5, -0.75), (1.5, h, 1.5), flat(ramp5("#ece6d4"), 3))
            add("flame", (dx + 0.35, top + 0.5 + h, -0.4), (0.8, 1.4, 0.8), shining(F))
    elif hw == "goggles":                                       # pushed up on the brow
        add("goggle_band", (-4, hy + 6, -4), (8, 1, 8), lambda fc, i, j, fw, fh: None if fc in ("top", "bottom") else f.lea[1], 0.45)
        for dx in (-3.2, 0.4):
            add("goggle", (dx, hy + 5.6, 4.1), (2.8, 1.8, 1), edged([rgb("#6a4a20"), rgb("#9a7030"), rgb("#c8a050"), rgb("#e0c070"), rgb("#f0e0a0")], 2))
    elif hw == "fur_hood":                                      # a fur hood with the stag's stubby antlers
        R = ramp5("#5a4632")

        def hood(face, i, j, fw, fh):
            if face == "bottom":
                return None
            if face == "front" and 1 <= i <= 6 and j >= 2:
                return None
            c = lit(face, j, fh, R, 2)
            return tint(c, 1.12) if (i * 3 + j) % 5 == 0 else c
        add("hood", (-4, hy, -4), (8, 8, 8), hood, 0.6)
        for sx in (-1, 1):
            add("antler", (sx * 2.6 - 0.5, top + 0.4, -1), (1, 3, 1), flat(ramp5("#c8b090"), 3), 0, (("z", -sx * 18),), (sx * 2.6, top, -0.5))
            add("antler", (sx * 3.4 - 0.5, top + 2.2, -1), (1, 1.6, 1), flat(ramp5("#c8b090"), 3), 0, (("z", -sx * 50),), (sx * 2.6, top, -0.5))


def overs(f, hy):
    o = f.s["outfit"]
    ov = o.get("overs", [])
    P = f.plan
    bw, bh, bd = P["body"]
    aw, ah, ad = P["arm"]
    if f.slim and f.race != "dwarf":
        aw = min(aw, 3)
    lh = P["leg"][1]
    MT, TR = metal(f), trim(f)
    belt = hy - round(bh * 0.68)
    add = f.add
    if "mantle" in ov:
        R = f.acc if f.acc[2] != f.top[2] else look("cloth", "linen")
        A = (0.0, hy - 2, 0.0)
        add("mantle", (-bw / 2 - 1, hy - 3.5, -bd / 2 - 0.8), (bw + 2, 3.8, bd + 1.6),
            lambda fc, i, j, fw, fh: (R[3] if fc == "top" else None if fc == "bottom" else (TR or GOLD)[3] if j == fh - 1 else lit(fc, j, fh, R, 2)),
            0, (), None, True, bone="back", anchor=A)
    for side, sx in (("r", -1), ("l", 1)):
        if "pauldrons" in ov or "pauldron_l" in ov and side == "l":
            x = sx * (bw / 2 + aw / 2)
            A = (x, hy - 2, 0.0)
            add("pauldron", (x - aw / 2 - 0.8, hy - 3.4, -ad / 2 - 0.8), (aw + 1.6, 3.6, ad + 1.6),
                lambda fc, i, j, fw, fh: None if fc == "bottom" else MT[4] if j == 0 and fc != "top" else (TR[3] if TR and j == fh - 1 else lit(fc, j, fh, MT, 2)),
                0, (), None, True, bone="shoulder_" + side, anchor=A)
    if "cape" in ov or "cloak" in ov:
        R = f.acc if "cape" in ov else (look("cloth", "brown") if f.top[2] == f.acc[2] else f.top)
        A = (0.0, hy - 2, -bd / 2)
        drop = bh + lh * 0.6
        add("cape", (-bw / 2 - 0.5, hy - drop, -bd / 2 - 1.1), (bw + 1, drop, 0.9),
            lambda fc, i, j, fw, fh: lit(fc, j, fh, R, 2) if not (fc == "back" and j == fh - 1) else R[1],
            0, (("x", -4),), (0, hy, -bd / 2), True, bone="back", anchor=A)
    if "hood_down" in ov or "cloak" in ov:
        R = f.top
        add("hood", (-3, hy - 1.5, -bd / 2 - 2.4), (6, 3, 2.4), flat(R, 2), 0, (), None, True, bone="back", anchor=(0.0, hy - 1, -bd / 2))
    if "scarf" in ov:
        add("scarf", (-bw / 2 - 0.5, hy - 1.2, -bd / 2 - 0.5), (bw + 1, 1.6, bd + 1), flat(f.acc, 2), 0, (), None, True,
            bone="back", anchor=(0.0, hy - 1, 0.0))
    if "satchel" in ov:
        add("satchel", (bw / 2 - 0.4, belt - 3.5, -1), (1.8, 3.5, 3), edged(f.lea, 2), 0, (), None, True, bone="hip", anchor=(bw / 2, belt, 0.0))
    for k in ("leather_apron", "apron", "tabard"):
        if k in ov:
            R = f.lea if k == "leather_apron" else look("cloth", "linen") if k == "apron" else f.acc
            w = bw - 2 if k != "tabard" else bw - 2
            ln = lh * (0.62 if k != "tabard" else 0.55)
            add("apron", (-w / 2, belt - ln, bd / 2 + 0.05), (w, ln, 0.5),
                lambda fc, i, j, fw, fh, R=R: lit(fc, j, fh, R, 2) if not (fc == "front" and j == fh - 1) else R[1],
                0, (), None, True, bone="hip", anchor=(0.0, belt, bd / 2))
            if k == "tabard":
                add("apron", (-w / 2, belt - ln, -bd / 2 - 0.55), (w, ln, 0.5), flat(R, 1), 0, (), None, True, bone="hip", anchor=(0.0, belt, -bd / 2))
            break
    if "tassets" in ov:
        for side, x in (("r", -P["leg"][0]), ("l", 0.0)):
            add("tasset", (x - 0.2, lh - 4, -P["leg"][2] / 2 - 0.3), (P["leg"][0] + 0.4, 4, P["leg"][2] + 0.6),
                lambda fc, i, j, fw, fh: None if fc in ("top", "bottom") else lit(fc, j, fh, MT, 2) if j % 2 == 0 else MT[1],
                0, (), None, False, bone="leg_" + side)


def gear(f, hy):
    """everything above, from the spec"""
    s = f.s
    headwear(f, hy)
    overs(f, hy)
    w = s.get("weapon")
    if w:
        held(f, "r", w)
    if s.get("offhand") == "shield":
        shield(f)
    if s.get("back"):
        back(f, s["back"])
    if s.get("hip"):
        hip(f, s["hip"])
    pr = s.get("prop")
    if pr == "kitten":
        kitten(f)
    elif pr:
        held(f, "l", pr)
