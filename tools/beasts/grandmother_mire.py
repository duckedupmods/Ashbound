"""Grandmother Mire: the swamp's Legend. A bog hag the size of a cottage, bent double over her hump: reed hair hanging
over a hooked nose and a grin full of teeth, one eye lit through it; rotten skirts to the mud, leeches fat on her arms;
she leans on a crooked staff hung with lanterns, and in each a soul. Biped (legendkit)."""
import math

from legendkit import X, C, ramp, W, grow, legs, arms, BIPED  # noqa: F401

GROW = 1.5
HITBOX = (3.0, 5.4)
IS_LEGEND = True
STATS = dict(hp=560, speed=0.24, dmg=20, armor=6, kb=0.9)
EGG, SPOTS = 0x32381c, 0x9ae8c8
HAGSKIN = ramp("#2a3022", "#3c4430", "#50583e", "#646e4c", "#7a845c", "#909a6e")
RAG = ramp("#0e0c08", "#18140e", "#221d14", "#2e271b", "#3a3222")
SOUL = ramp("#1a6a5a", "#2ea88c", "#5ad8b8", "#a0f4dc", "#e4fff6")
LEECH = ramp("#060406", "#0e0a0e", "#181018", "#241824", "#34203a")


def grandmother_mire(name="grandmother_mire", legend=False):
    k = X.Kit(name)
    hips = k.part("hips", (0, 24, 0))
    k.blob(hips, (0, 25, 0), (10, 4.6, 8), "rag", "waist", step=1.0)
    for i in range(14):                                  # her skirts, rotten, down to the mud
        a = i * 2 * math.pi / 14
        top = (math.cos(a) * 9.6, 25, math.sin(a) * 7.6)
        bot = (math.cos(a) * (13 + (i % 3)), 1.2 + (i % 4) * 0.8, math.sin(a) * (11 + (i % 2)))
        k.limb(hips, top, bot, 4.4, "rag", "skirt", d=1.4)
        if i % 3 == 0:
            k.limb(hips, (bot[0] * 0.95, bot[1] + 6, bot[2] * 0.95), (bot[0] * 1.02, bot[1] - 0.4, bot[2] * 1.02), 1.0, "reed", "weed", d=0.8)

    def foot(ft, sx, an):
        k.box(ft, C(an[0], 0, an[2] + 2.6, 6.4, 2.6, 11), "skin", tag="foot")
        for t in range(3):
            k.shard(ft, (an[0] + (t - 1) * 2, 0.8, an[2] + 7.6), (0, -0.2, 1), 2.4, 1.0, mat="nail", tag="toenail")
    legs(k, hips, 6, 24, (7, 13, 2), (7, 4, 0), 7.4, 6.4, "skin", foot)

    # ---- bent double over her hump, a shawl of moss
    ch = k.part("chest", (0, 28, 0), (("x", 34),), hips)
    k.stack(ch, 0, 0, [(28, 16, 12), (34, 20, 14), (40, 22, 15), (46, 20, 14), (50, 14, 11)], "rag", "torso", step=0.9)
    k.blob(ch, (0, 44, -6), (10, 8.4, 8), "skin", "hump", step=0.9)
    for (x, y, z) in ((-4, 48, -10), (3, 45, -12), (-1, 40, -11)):     # warts on the hump
        k.blob(ch, (x, y, z), (1.4, 1.4, 1.2), "wart", "wart", step=0.5)
    k.blob(ch, (0, 46.5, -1), (12.6, 2.6, 9), "moss", "shawl", step=0.7)
    for i in range(9):
        a = math.pi * (0.05 + 0.9 * i / 8)
        k.limb(ch, (-math.cos(a) * 13, 45, math.sin(a) * 7), (-math.cos(a) * 14, 38 - (i % 3) * 2, math.sin(a) * 8.4), 2.2, "moss", "shawl", d=1.2)
    # a necklace of little bones
    for i in range(7):
        a = math.pi * (0.2 + 0.6 * i / 6)
        k.shard(ch, (-math.cos(a) * 7, 45, 6 + math.sin(a) * 2.4), (0, -1, 0.2), 2.4, 0.9, mat="bone", tag="charm")

    # ---- the head: hooked nose, a grin of teeth, reed hair over it, one eye lit through
    hd = k.part("head", (0, 49, 6), (("x", -32),), ch)
    k.blob(hd, (0, 52, 9), (6.4, 7.0, 6.2), "skin", "head", step=0.6)
    k.limb(hd, (0, 54, 14.4), (0, 51, 19.5), 3.0, "skin", "nose", d=2.8)
    k.limb(hd, (0, 51, 19.5), (0, 45.5, 21.5), 2.4, "skin", "nose", d=2.2)
    k.blob(hd, (0, 46.8, 21.0), (1.6, 1.6, 1.4), "wart", "nose_wart", step=0.5)
    k.box(hd, C(0, 46.2, 14.4, 9.6, 3.0, 1.4), "dark", tag="grin")
    for t in range(7):
        k.shard(hd, (-4.2 + t * 1.4, 49.0, 15.0), (0, -1, 0.1), 1.8 + (t % 2) * 0.7, 0.8, mat="nail", tag="tooth")
    for sx in (-1, 1):
        k.box(hd, C(sx * 2.8, 53.2, 14.6, 2.6, 2.2, 1.0), "dark", tag="socket")
    W.eye(k, hd, (-2.8, 53.8, 15.2), 1.6, 1.1)
    k.box(hd, C(2.8, 54.4, 15.2, 2.6, 0.8, 0.4), "skin", tag="lid")
    for i in range(16):                                  # the hair: reeds and weed hanging over her face and back
        a = i * 2 * math.pi / 16
        if math.sin(a) > 0.2:                            # nothing over her face: the hair hangs at the sides and back
            continue
        top = (math.cos(a) * 5.6, 58.2, 9 + math.sin(a) * 5.6)
        bot = (math.cos(a) * 8.6, 36 + (i % 3) * 2, 9 + math.sin(a) * 7.6)
        k.limb(hd, top, bot, 1.8, "reed" if i % 3 else "moss", "hair", d=1.3)
    for sx in (-1, 1):                                   # two long locks down past her cheeks
        k.limb(hd, (sx * 5.8, 57, 12), (sx * 7.4, 40, 15), 1.6, "reed", "hair", d=1.2)
    k.ring(hd, 0, 58.6, 9, 5.0, 1.4, "reed", "reed_crown", n=12, axis="y")

    # ---- long thin arms, leeches fat on them; a claw, and the lantern staff
    def upper(up, sx):
        k.blob(up, (sx * 15.6, 38, 4.6), (1.6, 2.6, 1.6), "leech", "leech", step=0.5)

    def fore(low, sx):
        for (y, dz) in ((28, 1.6), (24, -1.2)):
            k.blob(low, (sx * 18.6, y, 7 + dz), (1.4, 2.4, 1.4), "leech", "leech", step=0.5)

    def hand(h, sx, wr):
        k.blob(h, (wr[0], wr[1] - 2, wr[2] + 0.6), (2.8, 2.6, 3.0), "skin", "palm", step=0.6)
        if sx > 0:                                       # the left: long fingers, black nails
            for i, a in enumerate((-0.5, -0.15, 0.2, 0.55)):
                base = (wr[0] + math.sin(a) * 2.4, wr[1] - 3.6, wr[2] + 2)
                tip = (wr[0] + math.sin(a) * 4.6, wr[1] - 11, wr[2] + 6)
                k.limb(h, base, tip, 1.1, "skin", "finger", d=1.1)
                k.shard(h, tip, (0, -0.8, 0.6), 2.2, 0.8, mat="nail", tag="nail")
        else:                                            # the right closed round her staff
            k.box(h, C(wr[0], wr[1] - 5, wr[2] + 0.6, 5, 4, 5), "skin", tag="fist")
    arms(k, ch, (13, 44, 2), (17, 32, 6), (18, 20, 8), 5.0, 4.4, "skin", hand, hunch=34, upper=upper, fore=fore)

    # the staff: crooked blackthorn, taller than her, a hook at the top hung with soul lanterns
    sh = k.parts["ar_hand"]
    base, top = (-18, 1.0, 10), (-19, 56, 9)
    mid = (-16.6, 30, 11)
    k.limb(sh, base, mid, 2.2, "staff", "staff", d=2.2)
    k.limb(sh, mid, top, 2.2, "staff", "staff", d=2.2)
    hook = [(-19, 56, 9), (-21, 61, 10), (-25, 62.5, 11), (-29, 60, 12), (-30, 56, 12.6)]
    for a, b in zip(hook, hook[1:]):
        k.limb(sh, a, b, 1.8, "staff", "staff_hook", d=1.8)
    for i, (lx, drop) in enumerate(((-22.5, 6), (-26.5, 9), (-30, 5))):     # three lanterns on chains
        hy = 62.6 if i == 1 else (61.6 if i == 0 else 56)
        k.chain(sh, (lx, hy - 0.4, 11.2), (lx, hy - drop, 11.2), 3, "iron", w=1.0)
        cy = hy - drop - 4.6
        k.box(sh, C(lx, cy, 11.2, 3.6, 4.6, 3.6), "soul", tag="soul", group="glow")
        for (ox, oz) in ((-1.8, -1.8), (1.8, -1.8), (-1.8, 1.8), (1.8, 1.8)):
            k.box(sh, C(lx + ox, cy, 11.2 + oz, 0.7, 4.6, 0.7), "iron", tag="cage")
        k.box(sh, C(lx, cy + 4.4, 11.2, 4.2, 0.9, 4.2), "iron", tag="cage")
        k.box(sh, C(lx, cy - 0.5, 11.2, 4.2, 0.9, 4.2), "iron", tag="cage")

    W.glow_tags(k, "eye", "soul")
    grow(k, GROW * (1.25 if legend else 1.0))
    k.s.shaders = W.shaders(
        skin=X.surf(HAGSKIN, 0.5, 1.2, 0.22, 0.06, crust=(W.BOGSKIN, 0.3)),
        rag=X.surf(RAG, 0.5, 1.1, 0.22, 0.02, stripe=2, drip=(W.BOGSKIN, 0.3)),
        reed=X.surf(W.REED, 0.5, 1.1, 0.2, 0.0, stripe=2),
        wart=X.surf(W.BELLY, 0.42, 1.0, 0.2, 0.0),
        nail=X.surf(W.HORN, 0.55, 1.2, 0.1, 0.06),
        leech=X.surf(LEECH, 0.5, 1.6, 0.08, 0.2),
        staff=X.surf(W.THORN, 0.55, 1.2, 0.2, 0.1, stripe=3),
        soul=X.glow(SOUL, 0.66, 0.3), eye=X.glow(W.LURE, 0.8, 0.16),
    )
    return k.s, k.parts


BONES = list(BIPED)
make = grandmother_mire
LEGEND = None
import legendkit as L

# her staff swung, a soul lantern thrown, the bog breathed on you, the cackle; under 60% the bog boils up round her
CLIPS = L.fitted("grandmother_mire", {
    "idle": L.idle(),
    "walk": L.walk(52, 16, 44, 2.6, 1.2),
    "run": L.walk(34, 24, 54, 3.8, 1.5),
    "staff": L.sweep(38, 20, reach=7.0, arc=150, dmg=1.1, range=[0, 7]),
    "lantern": L.mirror(L.throw(44, 26, item=1, dmg=1.0, throw=1.4, range=[7, 22], cool=160)),
    "bog": L.breath(64, 20, 52, reach=9.0, arc=50, dmg=0.08, elem=2, range=[3, 9], cool=260),
    "cackle": L.roar(46, 18, reach=8.0, elem=6),
    "boil": L.slam2(50, 28, front=0, radius=6.5, dmg=1.5, phase=2, cool=360, elem=2),
    "hurt": L.hurt(),
    "death": L.death_kneel(),
})
