"""The townsfolk remade: the old forge's NPCs (E:/Ashbound/tools/npc/kept, npcparts.Forge) read the same - names,
colours, outfits, faces - but built with volume and lit like objects, not painted on flat boxes ("paper").

  shading  each box is lit like a rounded thing: brighter on top and in front, darker round its sides and at its
           foot (contact shadow), a bright lip on top; clean steps of a longer ramp, no dither speckle
  body     a chest wider than the waist, shoulder caps, a collar, a front placket; skirts and robes flare in tiers,
           tunic hems kick out, sleeves end in cuffs, boots in turned-down cuffs and toe caps
  hair     a domed crown, a back that flips out at the ends, the fringe in separate strands, side locks tapering,
           strands down the hair and the anime highlight ring round the crown

    python tools/folkforge.py --preview id ...      -> tools/folk_src (efmob reads it) + a lineup render
    python tools/folkforge.py --export              -> every kept NPC, then python tools/efmob.py --npc
    python tools/folkforge.py --roll dwarf|elf|demon COUNT SEED -> tools/npc_specs + npc_talk (then --export)
    python tools/folkforge.py --hands [name ...]    -> the eight hand-made folk, relit (then efmob --npc)
"""
import colorsys
import json
import math
import os
import sys
from pathlib import Path

sys.path.insert(0, 'E:/Ashbound/tools')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import voxsword as V  # noqa: E402
from voxsword import ramp  # noqa: E402
from voxboss import C  # noqa: E402
import voxtownsfolk as TF  # noqa: E402
import voxfolk  # noqa: E402
import npcparts  # noqa: E402
from npcparts import LOOKS, Forge  # noqa: E402

OUT = Path(os.path.dirname(os.path.abspath(__file__))) / 'folk_src'
KEPT = Path('E:/Ashbound/tools/npc/kept')
SIDES = ('n', 's', 'e', 'w')


def tone(hx, n=8, lo=0.4, hi=1.45):
    """the old forge's ramp round one colour, two steps longer so light can fall off smoothly"""
    r, g, b = (int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    out = []
    for k in range(n):
        t = k / (n - 1)
        hh = (h + 0.025 * (0.5 - t)) % 1.0                      # shadows lean warm-cool like painted light
        rr, gg, bb = colorsys.hsv_to_rgb(hh, min(1, s * (1.2 - 0.4 * t)), min(1, v * (lo + (hi - lo) * t)))
        out.append("#%02x%02x%02x" % (round(rr * 255), round(gg * 255), round(bb * 255)))
    return ramp(*out)


def step(R, v):
    return R[max(0, min(len(R) - 1, int(v * len(R))))]


def lit(n, key, i, j, w, h, round_=0.16, foot=0.12, lip=0.1):
    """light on a box face: from above and in front, a rounded fall-off across its width, the foot in shadow"""
    v = 0.17 * n[1] + 0.08 * n[2]
    if key in SIDES:
        t = (2 * i + 1) / max(1, w) - 1                        # -1..1 across the face
        v -= round_ * t * t
        v -= 0.07 * j / max(1, h - 1)
        if j == 0 and h > 2:
            v += lip
        elif j == h - 1 and h > 2:
            v -= foot
    elif key == 'u':
        t = max(abs((2 * i + 1) / max(1, w) - 1), abs((2 * j + 1) / max(1, h) - 1))
        v -= 0.6 * round_ * t * t
    return v


def soft(R, base=0.5, folds=0.0, **kw):
    """cloth/leather/wood: lit like a rounded object; folds: soft vertical folds on long hanging cloth"""
    def f(p, n, b, key, i, j, w, h, fr):
        v = base + lit(n, key, i, j, w, h, **kw)
        if folds and key in SIDES and h > 8 and j > 0.3 * h:
            x, _, z = p
            u = (x if key in ('n', 's') else z) / 2.6 + 0.37
            if u - math.floor(u) < 0.22:                        # a pleat's shadow, straight down
                v -= folds
        return step(R, v)
    return f


def plate(R):
    """armour: brighter and harder than cloth, a polished rim all round"""
    def f(p, n, b, key, i, j, w, h, fr):
        v = 0.42 + lit(n, key, i, j, w, h, round_=0.22, foot=0.16, lip=0.0) + 0.06 * n[1]
        if key in SIDES and (i == 0 or i == w - 1 or j == 0):
            v += 0.2
        return step(R, v)
    return f


def mail(R):
    def f(p, n, b, key, i, j, w, h, fr):
        ring = (i + (j // 2) % 2) % 2 == 0 and j % 2 == 0
        return step(R, (0.48 if ring else 0.3) + lit(n, key, i, j, w, h))
    return f


class Hair:
    """hair: strands down it, the highlight ring round the crown (its height set once the head is built)"""
    def __init__(self, R):
        self.R, self.ring = R, None

    def __call__(self, p, n, b, key, i, j, w, h, fr):
        v = 0.5 + lit(n, key, i, j, w, h, round_=0.2, foot=0.1, lip=0.06)
        if key in SIDES:
            x, y, z = p
            u = x if key in ('n', 's') else z
            v -= 0.09 * (round(u * 4 + 0.3 * math.sin(y * 0.9)) % 3 == 0)
            if self.ring is not None and abs(y - self.ring) < 0.4 and n[2] > -0.5:
                v += 0.26
        return step(self.R, v)


def skin(R):
    def f(p, n, b, key, i, j, w, h, fr):
        return step(R, 0.55 + lit(n, key, i, j, w, h, round_=0.12, foot=0.08, lip=0.0) * 0.8)
    return f


# Hornsend's skins, added to the forge's own
LOOKS["skin"].update({
    "ember": ["#4a1a16", "#6a2820", "#8a382a", "#a44836", "#b85a44", "#c86e56"],
    "char": ["#2a2428", "#3a3236", "#4c4246", "#5e5256", "#706468", "#82767a"],
    "dusk": ["#2e2038", "#402c4c", "#543a60", "#684a74", "#7a5a86", "#8c6c98"],
})
HEAD = {"kid": 1.08, "teen": 1.18, "adult": 1.2, "elder": 1.16}
SPECS = Path(os.path.dirname(os.path.abspath(__file__))) / 'npc_specs'       # rolled here: the villages' races
RECIPES = Path(os.path.dirname(os.path.abspath(__file__))) / 'npc_recipes'


def race_age(race, a):
    """npcparts.AGES for a race: a dwarf short in the leg and wide everywhere, an elf long and slender"""
    a = dict(a)
    if race == "dwarf":
        a["hip"] *= 0.66
        a["lx"] += 0.35
        a["lw"] += 0.6
        a["lo"] = (a["lo"][0] * 0.95, a["lo"][1] * 1.18, a["lo"][2] * 1.22)
        a["up"] = (a["up"][0] * 0.98, a["up"][1] * 1.22, a["up"][2] * 1.2)
        a["skull"] = (a["skull"][0] * 1.08, a["skull"][1], a["skull"][2] * 1.04)
        a["arm"] = (a["arm"][0] + 0.5, a["arm"][1] + 0.5, a["arm"][2] * 1.08)
        a["hand"] = tuple(h + 0.3 for h in a["hand"])
        a["boot"] = (a["boot"][0] * 0.8, a["boot"][1] + 0.2, a["boot"][2] + 0.4)
        a["neck_w"] += 0.8
    elif race == "elf":
        a["hip"] *= 1.1
        a["lw"] -= 0.2
        a["lo"] = (a["lo"][0] * 1.05, a["lo"][1] * 0.92, a["lo"][2] * 0.92)
        a["up"] = (a["up"][0] * 1.08, a["up"][1] * 0.94, a["up"][2] * 0.92)
        a["skull"] = (a["skull"][0] * 0.96, a["skull"][1] * 1.04, a["skull"][2])
        a["arm"] = (a["arm"][0] - 0.2, a["arm"][1] - 0.2, a["arm"][2] * 1.04)
    elif race == "demon":
        a["lw"] -= 0.1
        a["up"] = (a["up"][0] * 1.04, a["up"][1] * 0.97, a["up"][2] * 0.96)
        a["arm"] = (a["arm"][0] - 0.1, a["arm"][1] - 0.1, a["arm"][2] * 1.02)
    return a


class Forge2(Forge):
    def __init__(self, spec, dx=0.0):
        super().__init__(spec, dx)
        self.race = spec.get("race")
        if self.race:
            keep = npcparts.AGES[spec["age"]]
            npcparts.AGES[spec["age"]] = race_age(self.race, keep)
            try:
                self.B = npcparts.body(spec["age"], spec["sex"], spec["build"])
            finally:
                npcparts.AGES[spec["age"]] = keep
        g = HEAD[spec["age"]]                                    # a bigger head: the cute, readable proportion
        sw, sh, sd = self.B["skull"]
        self.B["skull"] = (round(sw * g * 4) / 4, round(sh * g * 4) / 4, round(sd * g * 4) / 4)

    def colors(self):
        super().colors()
        sp, L = self.spec, LOOKS
        col = sp["outfit"]["colors"]
        top, bottom, accent = (tone(L["cloth"][col[k]]) for k in ("top", "bottom", "accent"))
        leather = tone(L["leather"][col["leather"]], lo=0.42, hi=1.35)
        metal_name = self.rank["metal"] if self.rank else col.get("metal", "iron")
        METAL = tone(L["metal"][metal_name][len(L["metal"][metal_name]) // 2], lo=0.35, hi=1.6)
        trim = (self.rank and self.rank["trim"]) or col.get("trim", "bronze")
        TRIM = tone(L["metal"][trim][len(L["metal"][trim]) // 2], lo=0.4, hi=1.55)
        SK = L["skin"][sp["skin"]]
        SKIN = tone(SK[len(SK) // 2 + 1], n=7, lo=0.6, hi=1.18)
        HR = L["hair"][sp["hair"]["color"]]
        self.hair = Hair(tone(HR[len(HR) // 2], lo=0.38, hi=1.6))
        self.sh.update({
            "skin": skin(SKIN), "hair": self.hair, "fringe": self.hair,
            "top": soft(top, folds=0.05), "top_q": soft(top, 0.5), "bottom": soft(bottom),
            "accent": soft(accent, folds=0.05), "accent_knit": soft(accent, 0.52),
            "leather": soft(leather), "boot": soft(leather, 0.42), "sole": soft(leather, 0.18, round_=0.0),
            "glove": soft(leather, 0.4), "stocking": soft(tone("#2e2a33"), 0.45),
            "armor": plate(METAL), "mail": mail(METAL), "trim": plate(TRIM),
            "wood": soft(tone("#523820"), 0.5), "dark": soft(tone("#2a2420", lo=0.5, hi=1.2), 0.3),
        })

    def head_(self, torso):
        head = super().head_(torso)
        sk = next(b for b in self.k.s.boxes if b.tag == "skull")
        self.hair.ring = sk.lo[1] + sk.size[1] * 0.8
        return head

    def enrich(self):
        """volume on the old forge's flat boxes, by what each box is"""
        k, B, sp = self.k, self.B, self.spec
        o = sp["outfit"]
        new = []

        def add(b, box, mat=None, tag=None, **kw):
            new.append((b.part, box, mat or b.mat, tag or b.tag, kw))

        def C_of(b):
            (x0, y0, z0), (w, h, d) = b.lo, b.size
            return x0 + w / 2, y0, z0 + d / 2, w, h, d

        for b in list(k.s.boxes):
            t = b.tag
            if t in ("cloak", "tabard", "apron", "bodice", "hood", "scarf", "shawl_end", "scarf_tail", "sash_end", "lock", "fringe") or (t == "hair" and min(b.size) < 0.9):
                # nothing hangs as thin as paper
                th = 1.0 if t not in ("fringe", "lock") else 0.8
                ax = min(range(3), key=lambda a: b.size[a])
                if b.size[ax] < th and ax != 1:
                    grow = th - b.size[ax]
                    side = -1 if b.lo[ax] + b.size[ax] / 2 < 0 else 1    # grow inward, towards the body
                    lo = list(b.lo); sz = list(b.size)
                    sz[ax] = th
                    if side > 0:
                        lo[ax] -= grow
                    b.lo, b.size = tuple(lo), tuple(sz)
                    if not b.rots:
                        b.pivot = b.lo
            if b.rots:
                continue
            cx, y0, cz, w, h, d = C_of(b)
            if t == "torso_up":
                # shoulders: a yoke across the top a little wider, the chest forward, the collar round the neck
                add(b, C(cx, y0 + h * 0.55, cz, w + 0.6, h * 0.45, d + 0.3))
                add(b, C(cx, y0 + h * 0.15, cz + d / 2, w - 1.6, h * 0.6, 0.5))
                if b.mat in ("top", "top_q"):
                    add(b, C(cx, y0 + h - 0.6, cz + 0.2, B["neck_w"] + 1.4, 1.0, d - 0.6), "accent" if o["top"] in ("tunic", "blouse", "robe", "dress") else b.mat, "collar")
                    if o["top"] in ("shirt", "tunic", "coat", "robe", "jerkin", "gambeson"):
                        add(b, C(cx, y0 - B["lo_h"] + 0.2, cz + d / 2 + 0.05, 0.8, h + B["lo_h"] - 1.2, 0.3), "dark" if o["top"] != "robe" else "trim", "placket")
            elif t == "torso_lo":
                b.lo = (b.lo[0] + 0.3, b.lo[1], b.lo[2] + 0.2)          # the waist in
                b.size = (w - 0.6, h, d - 0.4)
            elif t in ("skirt",) and h > 6:
                # tiers flaring out towards the hem
                # an A-line: the lower half a little wider, the hem wider again
                add(b, C(cx, y0, cz, w + 0.5, h * 0.5, d + 0.5), tag="skirt_tier")
                add(b, C(cx, y0, cz, w + 0.9, 1.0, d + 0.9), tag="skirt_tier")
            elif t == "skirt":
                add(b, C(cx, y0, cz, w + 0.8, min(1.4, h * 0.4), d + 0.8), tag="hem_kick")
            elif t == "hem":
                b.size = (w + 0.8, h, d + 0.8)
                b.lo = (b.lo[0] - 0.4, b.lo[1], b.lo[2] - 0.4)
            elif t == "upper" and b.mat not in ("skin",):
                add(b, C(cx, y0 + h - 1.6, cz, w + 0.7, 1.8, w + 0.7), tag="shoulder")
            elif t == "forearm" and b.mat not in ("skin",):
                bell = o["top"] in ("robe", "dress")
                add(b, C(cx, y0 - (0.6 if bell else 0.0), cz, w + (1.6 if bell else 0.7), 1.4 if bell else 1.0, w + (1.6 if bell else 0.7)), tag="cuff")
            elif t == "boot_top":
                add(b, C(cx, y0 + h - 0.2, cz, w + 0.5, 1.0, d + 0.5), tag="boot_cuff")
            elif t == "boot":
                add(b, C(cx, y0, cz + d / 2 - 0.6, w - 0.4, h * 0.7, 1.4), tag="toe")
            elif t == "belt":
                add(b, C(cx - w * 0.3, y0 - 2.2, cz + d / 2 - 0.2, 1.8, 2.2, 1.0), "leather", "pouch")
            elif t == "fringe":
                # strands of uneven length instead of one plate
                k.s.boxes.remove(b)
                n_ = max(3, round(w / 1.4))
                sw = w / n_
                for q in range(n_):
                    ln = h * (0.55 + 0.45 * ((q * 7 + 3) % 5) / 4)
                    add(b, C(b.lo[0] + sw * (q + 0.5), y0 + h - ln, cz + (0.15 if q % 2 else 0), sw + 0.15, ln, d + 0.2), "hair", "fringe")
            elif t == "lock":
                add(b, C(cx, y0 - 1.2, cz, w * 0.6, 1.4, d * 0.8), "hair", "lock_tip")
            elif t == "hair" and h <= 1.7 and w > 5:
                # the crown: a dome on the cap
                add(b, C(cx, y0 + h - 0.1, cz - 0.2, w - 1.6, 0.9, d - 1.6), "hair", "crown")
            elif t == "hair" and d < 1.0 and h > 3:
                # the back flips out at its ends
                add(b, C(cx, y0 - 0.2, cz - 0.3, w + 0.6, 1.4, d + 0.6), "hair", "flip")
        self.race_parts(add)
        for part, box, mat, tag, kw in new:
            k.add(part, box, mat, tag=tag, **kw)

    def race_parts(self, add):
        k, sp = self.k, self.spec
        if self.race == "elf":
            for b in [b for b in k.s.boxes if b.tag == "ear"]:
                # long ears pointing out and up from where the round ones were, tapering to a tip
                (x0, y0, z0), (w, h, d) = b.lo, b.size
                side = 1 if x0 > 0 else -1
                ex, ey, ez = (x0 if side < 0 else x0 + w), y0 + h * 0.45, z0 + d / 2 - 0.2
                turn = (("z", side * 30), ("y", side * 22))
                add(b, C(ex + side * 1.4, ey - 0.6, ez, 3.0, 1.4, 0.6), "skin", "ear_tip", rots=turn, pivot=(ex, ey, ez))
                add(b, C(ex + side * 3.4, ey - 0.4, ez, 1.4, 0.8, 0.5), "skin", "ear_tip", rots=turn, pivot=(ex, ey, ez))
        if self.race == "demon":
            sk = next(b for b in k.s.boxes if b.tag == "skull")
            (x0, y0, z0), (w, h, d) = sk.lo, sk.size
            g = 0.5 if sp["age"] == "kid" else 0.8
            top, zc = y0 + h - 2.2, z0 + d * 0.6
            # two thick horns from the temples: out, curving up, the tips turning in, each length from the last one's end
            for side in (1, -1):
                x, y = side * (w / 2 - 0.3), top
                for ln, wd, lean, tag in ((3.0, 2.5, 42, "horn"), (2.8, 1.9, 16, "horn"), (2.4, 1.3, -10, "horn"), (1.8, 0.7, -28, "horn_tip")):
                    ln, wd = ln * g, wd * g
                    add(sk, C(x, y, zc, wd, ln + 0.3, wd), "dark", tag, rots=(("z", -side * lean), ), pivot=(x, y, zc))
                    x += side * ln * math.sin(math.radians(lean))
                    y += ln * math.cos(math.radians(lean))
            # the tail, from the small of the back, out and down, a spade at its end
            pelvis = next(b for b in k.s.boxes if b.tag == "torso_lo")
            (hx, hy, hz), (hw, hh, hd) = pelvis.lo, pelvis.size
            bz, by = hz, hy + hh * 0.3
            for i in range(4):
                sz = (1.4 - i * 0.16) * g
                add(pelvis, C(0, by - i * 1.9 * g, bz - 0.8 - i * 1.5 * g, sz, 2.2 * g, sz + 0.8), "skin", "tail")
            add(pelvis, C(0, by - 8.4 * g, bz - 6.6 * g, 2.6 * g, 2.4 * g, 0.8 * g), "dark", "tail_tip")
        if self.race == "dwarf":
            for b in [b for b in k.s.boxes if b.tag == "nose"]:
                b.lo = (b.lo[0] - 0.25, b.lo[1] - 0.3, b.lo[2])
                b.size = (b.size[0] + 0.5, b.size[1] + 0.5, b.size[2] + 0.4)
                b.pivot = b.lo
            if sp["sex"] == "m" and sp["age"] in ("adult", "elder"):
                sk = next(b for b in k.s.boxes if b.tag == "skull")
                (x0, y0, z0), (w, h, d) = sk.lo, sk.size
                fz = z0 + d
                head = sk.part
                # the beard: a great mass from the cheeks down over the chest, two braids with rings at the ends
                add(sk, C(0, y0 - 6.2, fz - 0.6, w - 0.4, 6.0 + h * 0.3, 1.8), "hair", "beard")
                add(sk, C(0, y0 - 7.2, fz - 0.2, w - 2.2, 1.4, 1.4), "hair", "beard")
                for side in (1, -1):
                    add(sk, C(side * (w / 2 - 0.5), y0 - 1.0, fz - 1.4, 1.0, h * 0.5 + 1.0, 2.8), "hair", "sideburn")
                    bx = side * 1.3
                    add(sk, C(bx, y0 - 10.2, fz + 0.1, 1.2, 3.2, 1.2), "hair", "beard_braid")
                    add(sk, C(bx, y0 - 9.0, fz + 0.1, 1.5, 0.7, 1.5), "trim", "beard_ring")
                add(sk, C(0, y0 + h * 0.18, fz + 0.1, w * 0.62, 0.9, 0.6), "hair", "moustache")

    def build(self):
        self.colors()
        hips = self.legs()
        self.lower(hips)
        torso = self.torso(hips)
        self.arms_(torso)
        self.held()
        self.carried(hips, torso)
        self.drawn()
        self.head_(torso)
        self.enrich()
        used = {b.mat for b in self.k.s.boxes}
        self.k.s.shaders = {m: f for m, f in self.sh.items() if m in used}
        missing = used - set(self.k.s.shaders)
        assert not missing, missing
        return self.k


def export_one(sp):
    """as npcgen.export_one, into tools/folk_src instead of the old mod"""
    import voxelf
    V.T = npcparts.T
    voxelf.ASSETS = TF.ASSETS = OUT
    k = Forge2(sp).build()
    voxelf.NAME = sp["id"]
    base = voxelf.BONES
    voxelf.BONES = base + [n for n in ("back", "drawn") if n in k.parts]
    try:
        voxelf.export(k.s, k.parts)
    finally:
        voxelf.BONES = base
    sk = next(b for b in k.s.boxes if b.tag == "skull")
    hand = next(b for b in k.s.boxes if b.tag == "hand" and b.part is k.parts["hand_r"])
    k.rig_points(sp["id"], sk.lo[1] + sk.size[1] * 0.55, sk.lo[2] + sk.size[2], hand.lo[1] + hand.size[1] / 2)


HANDS = {"quartermaster": ("voxquartermaster", "brann"), "smith": ("voxsmith", "hesta"), "hunter": ("voxhunter", "garrick"),
         "receptionist": ("voxelf", "elowen"), "alchemist": ("voxtownsfolk", None), "fence": ("voxtownsfolk", None),
         "innkeeper": ("voxtownsfolk", None), "priestess": ("voxtownsfolk", None)}


def export_hands(names=None):
    """The eight hand-made folk keep their own builders (E:/Ashbound/tools/vox*.py, untouched) but are relit: their
    shaders' dither and noise blotches go, each box gets the rounded fall-off, foot shadow and lip of the rest."""
    import importlib
    import voxelf
    V.T = 4
    mods = {m: importlib.import_module(m) for m, _ in HANDS.values()}
    every = [voxelf, TF, voxfolk, V] + list(mods.values())
    keep = [(m, a, getattr(m, a)) for m in every for a in ("shade", "fbm", "ASSETS") if hasattr(m, a)]

    def cap(r, v, x, y):
        return ("cap", r, v)
    build = V.Sword.build

    def relit(self, *a, **kw):
        def wrap(f):
            def g(p, n, b, key, i, j, w, h, fr):
                out = f(p, n, b, key, i, j, w, h, fr)
                if isinstance(out, tuple) and len(out) == 3 and out[0] == "cap":
                    _, R, v = out
                    v += 0.8 * lit((0, 0, 0), key, i, j, w, h, round_=0.18, foot=0.12, lip=0.08)
                    return R[max(0, min(len(R) - 1, round(v * (len(R) - 1))))]
                return out
            return g
        self.shaders = {m: wrap(f) for m, f in self.shaders.items()}
        return build(self, *a, **kw)
    try:
        for m, a, _ in keep:
            setattr(m, a, {"shade": cap, "fbm": lambda *q: 0.5, "ASSETS": OUT}[a])
        V.Sword.build = relit
        for name in names or HANDS:
            mod, fn = HANDS[name]
            M = mods[mod]
            if fn is None:
                M.export(name)
            elif mod == "voxelf":
                M.NAME = name
                M.export(*M.elowen(with_player=False))
            else:
                M.export(*getattr(M, fn)())
            print("relit", name)
    finally:
        V.Sword.build = build
        for m, a, v in keep:
            setattr(m, a, v)


HAIR = {
    "dwarf": {"kid": {"f": {"braid": 2, "twintails": 1, "bob": 1}, "m": {"shaggy": 2, "short": 1}},
              "teen": {"f": {"braid": 3, "ponytail": 1}, "m": {"shaggy": 2, "short": 1}},
              "adult": {"f": {"braid": 3, "bun": 2, "twintails": 1}, "m": {"bald": 2, "short": 2, "shaggy": 2, "topknot": 1}},
              "elder": {"f": {"bun": 3, "braid": 1}, "m": {"bald": 3, "short": 1}}},
    "elf": {"kid": {"f": {"long": 2, "twintails": 1, "braid": 1}, "m": {"bob": 2, "shaggy": 1}},
            "teen": {"f": {"long": 3, "braid": 1, "ponytail": 1}, "m": {"long": 2, "shaggy": 1}},
            "adult": {"f": {"long": 4, "braid": 2, "ponytail": 1}, "m": {"long": 3, "ponytail": 2, "short": 1}},
            "elder": {"f": {"long": 2, "bun": 1}, "m": {"long": 2, "short": 1}}},
    "demon": {"kid": {"f": {"bob": 2, "twintails": 1}, "m": {"shaggy": 2, "short": 1}},
              "teen": {"f": {"ponytail": 2, "bob": 1}, "m": {"shaggy": 2, "short": 1}},
              "adult": {"f": {"ponytail": 2, "bun": 2, "braid": 1, "long": 1}, "m": {"short": 3, "shaggy": 2, "topknot": 1}},
              "elder": {"f": {"bun": 2, "long": 1}, "m": {"short": 2, "bald": 1}}},
}


def roll_race(race, count, seed):
    """count new folk of a race from npc_recipes/RACE.json (the old forge's roll, the race's names and hair), with
    their conversations (tools/npc_talk, tagged @RACE/@role) - kept in npc_specs"""
    import random
    import npcgen
    recipe = json.loads((RECIPES / (race + ".json")).read_text(encoding="utf-8"))
    recipe.setdefault("hair_style", HAIR[race])
    names = recipe["names"]
    SPECS.mkdir(exist_ok=True)
    talk = Path(os.path.dirname(os.path.abspath(__file__))) / 'npc_talk'
    used = set()
    for i in range(count):
        sp = npcgen.roll(recipe, i, seed * 1000 + i)
        rng = random.Random(sp["seed"])
        for _ in range(30):
            first = rng.choice(names["kid"] if sp["age"] == "kid" else names[sp["sex"]])
            if first not in used:
                break
        used.add(first)
        sp["name"] = first if sp["age"] == "kid" else first + " " + rng.choice(names["surname"])
        sp["race"] = race
        if race == "dwarf" and sp["sex"] == "m" and sp["age"] in ("adult", "elder"):
            sp["beard"] = None                  # the dwarf beard is built whole by race_parts
            sp["face"]["nose_box"] = True
        if race == "dwarf":
            sp["face"]["nose_box"] = sp["age"] != "kid"
        (SPECS / (sp["id"] + ".json")).write_text(json.dumps(sp, indent=1), encoding="utf-8")
        conv = npcgen.conversation(sp, random.Random(sp["seed"] + 1))
        conv["tags"] = conv["tags"] + [race]
        (talk / (sp["id"] + ".json")).write_text(json.dumps(conv, indent=1), encoding="utf-8")
        print("rolled", sp["id"], sp["name"], "-", sp["title"], sp["age"], sp["sex"], sp["build"])


def specs(ids=None):
    for f in sorted(KEPT.glob("*.json")) + sorted(SPECS.glob("*.json")):
        sp = json.loads(f.read_text(encoding="utf-8"))
        if not ids or sp["id"] in ids:
            yield sp


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['--roll']:
        roll_race(a[1], int(a[2]), int(a[3]))
    if a[:1] == ['--hands']:
        export_hands(a[1:] or None)
    if a[:1] == ['--preview'] or a[:1] == ['--export']:
        for sp in specs(a[1:] if a[0] == '--preview' else None):
            export_one(sp)
            print("built", sp["id"], sp["name"])
