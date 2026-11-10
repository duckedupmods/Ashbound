"""The Sunken Fire's keeper: the Wreck-Mother (Act II's boss, fought in the Graveyard of Ships, tools/blender/wreck_arena.py).

    wreck_mother   boss   a crab the size of a house that crawled into a galleon's hull and wears it upside down: the
                          keel along her back, barnacles and kelp all over the planks, gunports glowing cold from the
                          light inside her, a broken mast and its torn sail out of her stern, an anchor dragging on its
                          chain; under the hull's lip, eyes on stalks and a maw of mandibles; two great claws, the
                          right one bigger and barnacled like a rock, three spiked legs a side

    python tools/monsterforge.py sunken_fire --preview ; python tools/mobsheet.py sunken_fire
    python tools/connect_check.py sunken_fire
"""
import math

import vox2 as X
from vox2 import C, ramp
from serpent_ziggurat import grow
from _folk import lit
from tidewrack import Cc, barnacles, anemone, branch

HULL = ramp("#0a0806", "#140f0b", "#1e1710", "#2a2016", "#382a1c", "#463424")
SHELL = ramp("#06080c", "#0c1016", "#141a22", "#1e2630", "#2a3440", "#384452")
UNDER = ramp("#2a2420", "#3e3630", "#544a42", "#6c6056", "#86786a")
BARN = ramp("#3e403c", "#5c5e58", "#7c7e76", "#9c9e94", "#bcbcb0")
KELP = ramp("#060a06", "#0c140c", "#121e10", "#1a2a16", "#24381e")
IRON = ramp("#0c0c0e", "#16161a", "#222228", "#303038", "#40404a")
SAIL = ramp("#2a2a26", "#3c3c36", "#504e46", "#66625a", "#7e7a70")
ORANGE = ramp("#3a1406", "#5c200a", "#82300e", "#a84416", "#cc5c22", "#ec7c34")
VIOLET = ramp("#1a0a24", "#2c1238", "#401c50", "#56286a", "#703686", "#8c48a2")
LURE = ramp("#06304a", "#0c5878", "#1a84a8", "#3cb4dc", "#8ee0f8", "#e2faff")
TAR = ramp("#020406", "#06080c", "#0a0e12", "#10141a")


def shaders():
    return {
        "hull": X.surf(HULL, 0.5, 1.1, 0.24, 0.08, stripe=2, crust=(BARN, 0.22)),
        "shell": X.wrinkled(SHELL, 0.7),
        "under": X.surf(UNDER, 0.5, 1.1, 0.18, 0.1, stripe=3),
        "barnacle": X.surf(BARN, 0.56, 1.4, 0.3, 0.2, pattern=lambda p, n, i, j, w, h: 0.2 if (i * 3 + j * 5) % 7 == 0 else -0.04),
        "kelp": X.surf(KELP, 0.5, 1.0, 0.3, 0.0, stripe=2, holes=True),
        "iron": X.surf(IRON, 0.5, 1.4, 0.2, 0.22, crust=(BARN, 0.2)),
        "sail": X.surf(SAIL, 0.5, 1.0, 0.3, 0.02, holes=True),
        "orange": X.surf(ORANGE, 0.55, 1.3, 0.26, 0.16),
        "violet": X.surf(VIOLET, 0.55, 1.3, 0.26, 0.14),
        "lure": X.glow(LURE),
        "eye": X.glow(LURE, 0.84, 0.14),
        "dark": X.dark(TAR),
    }


GLOWS = {"lure", "eye"}


def limb3(k, part, pts, ws, mat, tag):
    for (a, b), w in zip(zip(pts, pts[1:]), ws):
        k.limb(part, a, b, w, mat, tag)


def wreck_mother():
    k = X.Kit("wreck_mother")
    Y = 16.0                                         # the body's middle
    body = k.part("body", (0, Y, 0))
    hd = k.part("head", (0, Y, 14), (("x", 0),), "body")
    ab = k.part("abdomen", (0, Y, -10), (), "body")
    joints = {"body": "Root", "head": "Head", "abdomen": "Stomach"}
    # the crab under it all: a broad flat carapace, pale under
    k.blob(body, (0, Y, 2), (17, 6, 14), "shell", "carapace", step=1.2)
    k.box(body, Cc(0, Y - 5.0, 2, 26, 2.0, 22), "under", tag="belly")
    k.blob(ab, (0, Y - 1, -12), (13, 5, 8), "shell", "carapace_back", step=1.2)
    # the hull she wears, upside down: an arch over her from bow to stern, the keel along the top
    for zi in range(-12, 13):
        z = zi * 1.6
        t = abs(z + 2) / 21.0
        hw = 21.0 * math.sqrt(max(0.0, 1 - t ** 2.6))
        if hw < 2:
            continue
        part = body if z > -6 else ab
        n = 7
        for i in range(n):
            x0 = -hw + 2 * hw * i / n
            x1 = -hw + 2 * hw * (i + 1) / n
            xm = (x0 + x1) / 2
            top = Y + 4 + 15 * math.sqrt(max(0.0, 1 - (xm / hw) ** 2)) * (1 - 0.3 * t)
            k.box(part, Cc(xm, (Y + 2 + top) / 2, z, x1 - x0 + 0.1, top - (Y + 2), 1.7), "hull", tag="hull")
        # the gunwale's edge, low, and the gunports along it
        for sx in (-1, 1):
            k.box(part, Cc(sx * (hw - 0.3), Y + 2.6, z, 1.4, 1.6, 1.7), "hull", tag="gunwale")
            if zi % 4 == 0 and abs(z) < 14:
                k.box(part, Cc(sx * (hw * 0.93), Y + 6.4, z, 1.0, 2.0, 1.6), "dark", tag="gunport")
                k.box(part, Cc(sx * (hw * 0.95), Y + 6.4, z, 0.6, 1.2, 1.0), "lure", tag="gunport_light")
        top = Y + 4 + 15 * (1 - 0.3 * t)
        k.box(part, Cc(0, top + 0.8, z, 2.0, 2.0, 1.7), "iron" if zi % 5 == 0 else "hull", tag="keel")
    # barnacles, kelp and coral over the planks
    for i in range(10):
        z = -14 + i * 3.2
        x = (-1) ** i * (4 + (i * 7) % 9)
        t = abs(z + 2) / 21.0
        hw = 21.0 * math.sqrt(max(0.0, 1 - t ** 2.6))
        yy = Y + 4 + 15 * math.sqrt(max(0.0, 1 - (x / hw) ** 2)) * (1 - 0.3 * t) - 0.6
        barnacles(k, body if z > -6 else ab, (x, yy, z), 6, 1.6, seed=i, z_out=1.0)
    for z, x in ((6, -8), (-2, 10), (-10, -4)):
        branch(k, body if z > -6 else ab, (x, Y + 15.5, z), (0.3 * (1 if x > 0 else -1), 1, 0.2), 1.4)
    anemone(k, body, (9, Y + 16.4, 8), 1.4, "violet", seed=1)
    anemone(k, ab, (-7, Y + 15.4, -12), 1.2, "orange", seed=2)
    for i in range(12):                              # kelp hanging off the gunwales
        a = i / 12 * 2 * math.pi
        x, z = math.cos(a) * 19, math.sin(a) * 17 - 2
        k.limb(body if z > -6 else ab, (x, Y + 2.6, z), (x * 1.05, Y - 6 - (i % 3) * 2, z * 1.04), 0.9, "kelp", "kelp")
    # the broken mast out of her stern, its torn sail, and an anchor on its chain
    limb3(k, ab, [(0, Y + 12, -16), (2, Y + 22, -24), (3, Y + 30, -28)], (2.4, 1.8), "hull", "mast")
    k.limb(ab, (-6, Y + 26, -26), (10, Y + 25, -27), 1.0, "hull", "yard")
    for i in range(7):
        x = -5 + i * 2.2
        L = 5 + (i * 5) % 7
        k.box(ab, Cc(x, Y + 25 - L / 2, -26.6, 2.2, L, 0.5), "sail", tag="sail")
    for i in range(8):
        k.box(ab, Cc(-12 - i * 0.3, Y + 1 - i * 1.9, -16 - i * 0.45, 1.0, 2.4, 0.8 if i % 2 else 1.6), "iron", tag="chain")
    k.limb(ab, (-14.4, Y - 12.5, -19.6), (-14.4, Y - 18, -19.6), 1.4, "iron", "anchor")
    k.limb(ab, (-18, Y - 18, -19.6), (-10.8, Y - 18, -19.6), 1.2, "iron", "anchor")
    for sx in (-1, 1):
        k.shard(ab, (-14.4 + sx * 3.6, Y - 18, -19.6), (sx * 0.5, 1, 0), 2.6, 1.0, mat="iron", tag="anchor_fluke")
    # under the bow: eyes on stalks, mandibles, the cold light deep in her mouth
    k.box(hd, Cc(0, Y - 1, 16.5, 14, 6, 4), "shell", tag="face")
    for sx in (-1, 1):
        k.limb(hd, (sx * 4.0, Y + 1, 17.0), (sx * 5.0, Y + 6, 19.0), 1.0, "shell", "eye_stalk")
        k.blob(hd, (sx * 5.0, Y + 7, 19.2), (1.3, 1.3, 1.3), "eye", "eye", step=0.5)
        for j in range(3):
            k.limb(hd, (sx * (1.5 + j * 1.6), Y - 2.5, 18.2), (sx * (1.0 + j * 1.2), Y - 6.5 - j, 20.5), 0.8, "under", "mandible")
    k.box(hd, Cc(0, Y - 1.4, 18.7, 6, 2.6, 0.4), "dark", tag="maw")
    k.box(hd, Cc(0, Y - 1.4, 18.8, 3.6, 1.2, 0.3), "lure", tag="maw_light")
    # the legs: three a side, a crab's (11/7: the spider's sticks were rejected): thick armoured segments out under the
    # gunwale, a high hard knee, a second bend, and a black-tipped dactyl driven into the ground; plates and spines on each
    for side, s in ((1, "L"), (-1, "R")):
        for j, z in ((2, 5.0), (3, -3.0), (4, -11.0)):
            nm = "leg_%s%d" % (s.lower(), j)
            part_of = body if j < 4 else ab
            lg = k.part(nm, (side * 13, Y - 2, z), (), part_of)
            dz = 3 if j == 2 else -1 if j == 3 else -5
            base = (side * 13, Y - 2, z)
            knee = (side * 23, Y + 5, z + dz)
            wrist = (side * 31, Y - 4, z + dz * 1.6)
            foot = (side * 34, 0.4, z + dz * 2.0)
            limb3(k, lg, [base, knee, wrist, foot], (7.4, 6.0, 4.0), "shell", "leg")
            # armour: a plate along the top of each segment, a hard knob at each bend, spines on the upper edge
            for a0, a1, w in ((base, knee, 7.4), (knee, wrist, 6.0)):
                mid = tuple((a0[i] + a1[i]) / 2 for i in range(3))
                k.blob(lg, (mid[0], mid[1] + w * 0.45, mid[2]), (w * 0.62, w * 0.36, w * 0.62), "shell", "leg_plate", step=0.9)
                for t in (0.3, 0.7):
                    q = tuple(a0[i] + (a1[i] - a0[i]) * t for i in range(3))
                    k.shard(lg, (q[0], q[1] + w * 0.5, q[2]), (side * 0.3, 1, 0), 2.2, 0.9, mat="dark", tag="leg_spike")
            k.blob(lg, knee, (4.4, 4.4, 4.4), "shell", "knee", step=0.9)
            k.blob(lg, wrist, (3.4, 3.4, 3.4), "shell", "knee", step=0.9)
            k.shard(lg, foot, (0, -1, 0), 2.6, 2.4, mat="dark", tag="foot")
            barnacles(k, lg, (knee[0], knee[1] + 2.4, knee[2]), 5, 1.4, seed=j + side)
            joints[nm] = s + "L" + str(j)
    # the claws on the front legs (11/7 remake): short heavy arms folded in front of the face, each ending in a crab's chela,
    # a swollen palm and two thick fingers with teeth on their inner edges; the right one bigger, barnacled like a rock
    for side, s in ((1, "L"), (-1, "R")):
        big = side < 0
        f = 1.35 if big else 1.0
        nm = "leg_%s1" % s.lower()
        cl = k.part(nm, (side * 10, Y - 1, 12), (), body)
        shoulder = (side * 10, Y - 1, 12)
        elbow = (side * 21, Y + 3, 18)
        wrist = (side * 15, Y, 25)
        limb3(k, cl, [shoulder, elbow, wrist], (6.2 * f, 5.4 * f), "shell", "claw_arm")
        k.blob(cl, elbow, (3.8 * f, 3.8 * f, 3.8 * f), "shell", "claw_elbow", step=0.9)
        palm = (wrist[0], wrist[1] + 1.0 * f, wrist[2] + 5.0 * f)
        k.blob(cl, palm, (5.6 * f, 5.2 * f, 7.0 * f), "shell", "claw_palm", step=0.9)
        root_top = (palm[0], palm[1] + 2.4 * f, palm[2] + 5.5 * f)
        root_low = (palm[0], palm[1] - 2.6 * f, palm[2] + 5.0 * f)
        tip_top = (palm[0] - side * 1.6 * f, palm[1] + 0.4 * f, palm[2] + 14.0 * f)
        tip_low = (palm[0] - side * 1.0 * f, palm[1] - 1.6 * f, palm[2] + 12.0 * f)
        k.limb(cl, root_top, tip_top, 3.6 * f, "shell", "pincer")
        k.limb(cl, root_low, tip_low, 3.0 * f, "shell", "pincer")
        k.shard(cl, tip_top, (0, -0.4, 1), 2.0 * f, 1.4 * f, mat="dark", tag="pincer_tip")
        k.shard(cl, tip_low, (0, 0.3, 1), 1.8 * f, 1.2 * f, mat="dark", tag="pincer_tip")
        for i in range(4):                           # teeth along both fingers' inner edges
            t = 0.2 + i * 0.18
            q = tuple(root_top[a] + (tip_top[a] - root_top[a]) * t for a in range(3))
            k.shard(cl, (q[0], q[1] - 1.4 * f, q[2]), (0, -1, 0.2), 1.2 * f, 0.7 * f, mat="under", tag="pincer_tooth")
            q = tuple(root_low[a] + (tip_low[a] - root_low[a]) * t for a in range(3))
            k.shard(cl, (q[0], q[1] + 1.2 * f, q[2]), (0, 1, 0.2), 1.0 * f, 0.6 * f, mat="under", tag="pincer_tooth")
        for t in (0.35, 0.7):                        # spines along the arm's top
            q = tuple(elbow[a] + (wrist[a] - elbow[a]) * t for a in range(3))
            k.shard(cl, (q[0], q[1] + 2.8 * f, q[2]), (side * 0.3, 1, 0), 2.0 * f, 0.8, mat="dark", tag="claw_spike")
        if big:
            barnacles(k, cl, (palm[0], palm[1] + 4.4 * f, palm[2]), 12, 3.4, seed=11, z_out=1.0)
            branch(k, cl, (palm[0] - 2, palm[1] + 4.6 * f, palm[2] - 2), (-0.4, 1, 0.2), 1.0)
        joints[nm] = s + "L1"
    lit(k, GLOWS)
    k.s.shaders = shaders()
    return k.s, k.parts, joints


MOBS = {
    # grow: she's drawn at a crab's proportions and scaled up in the game 2.3 times (11/7: "make it bigger, not that little crab")
    "wreck_mother": dict(make=wreck_mother, rig="crawler", ent=(13.0, 13.0), grow=2.3, boss=True,
                         stats=dict(hp=1200, speed=0.2, dmg=22, armor=14, kb=1.0)),
}
