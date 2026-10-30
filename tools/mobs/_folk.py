"""Shared anatomy for the world factions' monsters (tools/mobs/<faction>.py): legs, arms, eyes, a four-legged
crawler's frame, wings. Only the bones and their proportions live here; what makes each monster itself - its
armour, its face, its weapon - is built by hand in its own file. (Files starting with _ aren't factions.)"""
import math

from vox2 import C


def lit(k, glows):
    for b in k.s.boxes:
        if b.mat in glows:
            b.group = "glow"


def eyes(k, part, y, z, gap=1.5, w=1.1, mat="eye", h=0.6):
    for sx in (-1, 1):
        k.box(part, C(sx * gap, y, z, w, h, 0.3), mat, tag="eye")


def straps(k, part, a, b, w=1.0, mat="leather"):
    k.limb(part, a, b, w, mat, "strap", d=0.5)


def legs(k, hips, top, knee, x, hose, boot, knee_mat=None, lean=-6, bend=8, w=5.4, cuff=True, toe=None, splay=3):
    """a biped's two legs: thighs (hose), knees (knee_mat, or none), shins (boot), feet (tagged foot)"""
    for side, nm in ((1, "l"), (-1, "r")):
        xx = side * x
        th = k.part("thigh_" + nm, (xx, top, 0), (("x", lean), ("z", side * splay)), hips)
        sh = k.part("shin_" + nm, (xx, knee, 0), (("x", bend),), th)
        ft = k.part("foot_" + nm, (xx, 2.4, 0), (("x", -2),), sh)
        k.stack(th, xx, 0, [(knee + 0.2, w - 0.6, w - 0.2), (top, w + 0.4, w + 0.8)], hose, "thigh")
        if knee_mat:
            k.box(th, C(xx, knee - 0.8, 1.2, w - 0.4, 2.4, w - 0.8), knee_mat, tag="knee")
        k.stack(sh, xx, 0, [(2.4, w - 0.6, w - 0.2), (knee, w, w + 0.4)], boot, "shin")
        if cuff:
            k.box(sh, C(xx, knee - 1.8, 0, w + 0.8, 2.0, w + 1.2), boot, tag="cuff")
        k.box(ft, C(xx, 0, 1.4, w, 2.6, w + 2.4), boot, tag="foot")
        if toe:
            k.box(ft, C(xx, 0, w * 0.5 + 2.2, w - 0.8, 1.6, 1.2), toe, tag="foot")


def arms(k, to, x, top, mat, rots, sleeve=None, glove=None, w=4.0, long=1.0):
    """two arms hanging from `top` at +-x; rots: {1: (arm rots, fore rots), -1: (...)}; long stretches them"""
    for side, nm in ((1, "l"), (-1, "r")):
        xx = side * x
        ar, fr = rots[side]
        a, f = 8 * long, 7.6 * long
        up = k.part("arm_" + nm, (xx, top, 0), ar, to)
        fo = k.part("fore_" + nm, (xx, top - a, 0), fr, up)
        hn = k.part("hand_" + nm, (xx, top - a - f, 0), (), fo)
        k.limb(up, (xx, top - 0.6, 0), (xx, top - a + 0.4, 0), w, sleeve or mat, "upper_arm")
        k.limb(fo, (xx, top - a - 0.2, 0), (xx, top - a - f + 1.0, 0), w - 0.4, mat, "forearm")
        k.box(hn, C(xx, top - a - f - 2.8, 0.3, w - 0.4, 3.4, w), glove or mat, tag="hand")


def held(k, name, hand_side, at, rots):
    """a weapon's part in a hand ('l'/'r'): model it hanging straight up from the hand at `at`, turned by `rots`"""
    return k.part(name, at, rots, k.parts["hand_" + hand_side], bone=False)


def quad(k, body_mat, y=14, chest=((7, 11, 13), (12, 14, 15), (18, 12.4, 13.6)), haunch=((8, 10.6, 10), (12.6, 12, 11), (17, 10.4, 9.6)),
         leg_w=4.4, foot_w=3.4, front_z=5, back_z=-9, x=5.0, leg_mat=None, head_at=(0, 16, 8), head_rot=-6, claw="dark",
         knees=None, foot_len=5.4):
    """a four-legged crawler's frame (body -> Root, head -> Head, abdomen -> Stomach, four legs). Returns
    (body, head, abdomen, joints); dress them after."""
    lm = leg_mat or body_mat
    body = k.part("body", (0, y, 0))
    k.stack(body, 0, 1, list(chest), body_mat, "chest", step=1.2)
    hd = k.part("head", head_at, (("x", head_rot),), "body")
    ab = k.part("abdomen", (0, y, back_z + 3), (), "body")
    k.stack(ab, 0, back_z, list(haunch), body_mat, "haunch")
    joints = {"body": "Root", "head": "Head", "abdomen": "Stomach"}
    for side, s in ((1, "l"), (-1, "r")):
        for i, (z, j, part) in enumerate(((front_z, 1, body), (back_z, 4, ab))):
            nm = "leg_%s%d" % (s, i)
            top = y - 3
            lg = k.part(nm, (side * x, top, z), (), part)
            kz = knees[i] if knees else (1.4 if i == 0 else -2.4)
            kn = (side * (x + 0.6), top * 0.5, z + kz)
            k.limb(lg, (side * x, top, z), kn, leg_w, lm, "leg")
            k.limb(lg, kn, (side * (x + 0.6), 0.8, z + 0.6), foot_w, lm, "foot")
            k.box(lg, C(side * (x + 0.6), 0, z + 1.4, foot_w + 1.2, 1.8, foot_len), lm, tag="foot")
            for t in (-1.2, 0, 1.2):
                k.shard(lg, (side * (x + 0.6) + t, 0.6, z + 1.4 + foot_len * 0.5 + 1.0), (0, -0.3, 1), 1.4, 0.6, mat=claw, tag="foot")
            joints[nm] = ("LL" if side > 0 else "RL") + str(j)
    return body, hd, ab, joints


def wing(k, part, root, side, span, mat, membrane=None, ribs=4, up=0.5, back=0.4, drop=10.0, feather=True, tag="wing"):
    """a wing from `root` out to one side: a bony arm out and up, then feathers (or a membrane) hanging from it"""
    rx, ry, rz = root
    tip = (rx + side * span, ry + span * up, rz - span * back)
    mid = (rx + side * span * 0.45, ry + span * up * 0.8, rz - span * back * 0.3)
    k.limb(part, root, mid, 2.0, mat, tag + "_arm")
    k.limb(part, mid, tip, 1.4, mat, tag + "_arm")
    for i in range(ribs + 1):
        t = i / ribs
        a = mid if t < 0.5 else tip
        p = (rx + side * span * (0.15 + 0.85 * t), ry + span * up * (0.3 + 0.7 * t), rz - span * back * t)
        L = drop * (1.0 - 0.45 * t) + 2.0
        if feather:
            k.limb(part, p, (p[0] + side * 1.2, p[1] - L, p[2] - 1.0), 2.2 - t * 0.6, membrane or mat, tag, d=0.5)
        else:
            k.limb(part, p, (p[0] + side * 0.6, p[1] - L, p[2] - 0.6), 0.8, mat, tag + "_rib")
            if i < ribs:
                q = (rx + side * span * (0.15 + 0.85 * (i + 1) / ribs), p[1], p[2])
                k.box(part, C((p[0] + q[0]) * 0.5, p[1] - L * 0.9, p[2] - 0.3, abs(q[0] - p[0]) + 0.4, L * 0.9, 0.4), membrane or mat, tag=tag + "_skin")
    return tip


def ring_of(k, part, c, r, n, fn):
    """call fn(x, y, z, angle) at n points round a horizontal ring"""
    cx, cy, cz = c
    for i in range(n):
        a = i * 2 * math.pi / n
        fn(cx + math.cos(a) * r, cy, cz + math.sin(a) * r, a)
