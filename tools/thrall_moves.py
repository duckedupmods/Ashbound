"""How the summons fight: each thrall kind's blows as keyed poses, the way the player's weapon moves are full-body (torso
turned into it, the arm drawn back and brought through, a step into the hit), written to
assets/ashbound/mounts/thrall_moves.json for client/ThrallRender. A thrall throws its kind's blows in turn.

A blow is keyed over 0..1 of its swing (Thrall: 16 ticks, 24 for the Champion and the Gatebreaker); the hit lands at 0.55.
Each kind below is written as three poses (drawn back, arriving, carried through) and timed by timed(): it draws back and
slows into a coil, snaps through in a tick or two (eased in, so it's fastest at the hit), holds there while the hit lands
(the hit-stop), carries on through and only then comes home. A key's third field is how it gets there from the one before:
"o" fast then slowing, "i" slow then fast, "s" both (the default). Each key turns bones in degrees (x forward/back, y round the body,
z out to the side; applied z, then x, then y, so an arm raised level by x then swings level by y) and moves the whole body
(root: x left, y up, z forward, in blocks of the model before its scale). Bones a key leaves out are at rest.

    python tools/thrall_moves.py                      writes the json
    python tools/thrall_moves.py --preview [kind...]  also draws tools/renders/thrall_moves/<kind>.png, every blow at its keys
"""
import json
import math
import os
import sys

GAME = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ASSETS = os.path.join(GAME, "src/main/resources/assets/ashbound")
OUT = os.path.join(ASSETS, "mounts/thrall_moves.json")
PREVIEW = os.path.join(GAME, "tools/renders/thrall_moves")


def mirror(keys):
    """the same blow from the other side: l and r swap, turns round the body and out to the side flip"""
    out = []
    for t, pose in keys:
        p = {}
        for bone, v in pose.items():
            name = bone
            if bone.endswith("_l") or bone.endswith("_r"):
                name = bone[:-1] + ("r" if bone.endswith("_l") else "l")
            elif bone[:-1].endswith("_l") or bone[:-1].endswith("_r"):     # leg_l0
                name = bone[:-2] + ("r" if bone[-2] == "l" else "l") + bone[-1]
            if bone == "root":
                p[name] = [-v[0], v[1], v[2]]
            else:
                p[name] = [v[0], -v[1], -v[2]]
        out.append([t, p])
    return out


# Where each one's parts point at rest (from the models): arms hang, forearms reach forward; the Champion's blade stands up out of
# its fist (so the wrist, "blade", turns it level with the forearm for a cut, and the elbow straightens the forearm along the
# arm); the Oathwarden's spear trails back from its hand (turned round, "spear" y 180, for a thrust); the Riftblade's blades are
# its forearms; the Riftling's sting curls up off its back (x forward brings it over); the Gatebreaker's fists hang to the ground.

# ---- the Champion: a great blade in the right hand, and it means it ----
CHAMPION = {
    "cleave": [
        [0.0, {}],
        [0.35, {"torso": [-15, -20, 0], "arm_r": [-170, 0, -10], "fore_r": [-20, 0, 0], "arm_l": [-60, 0, 20], "head": [-10, 0, 0], "root": [0, 0, -0.1]}],
        [0.55, {"torso": [30, 10, 0], "arm_r": [-75, 0, 0], "fore_r": [80, 0, 0], "blade": [90, 0, 0], "arm_l": [-20, 0, 15], "head": [15, 0, 0], "root": [0, -0.05, 0.4]}],
        [0.72, {"torso": [35, 12, 0], "arm_r": [-25, 0, 0], "fore_r": [80, 0, 0], "blade": [90, 0, 0], "arm_l": [-10, 0, 15], "head": [15, 0, 0], "root": [0, -0.05, 0.45]}],
        [1.0, {}],
    ],
    "sweep": [
        [0.0, {}],
        [0.35, {"torso": [-5, -40, 0], "arm_r": [-90, -80, 0], "fore_r": [85, 0, 0], "blade": [90, 0, 0], "arm_l": [-30, 0, 20], "head": [0, 20, 0]}],
        [0.55, {"torso": [10, 25, 0], "arm_r": [-90, 20, 0], "fore_r": [85, 0, 0], "blade": [90, 0, 0], "arm_l": [-20, 0, 20], "head": [0, -10, 0], "root": [0, 0, 0.25]}],
        [0.72, {"torso": [10, 45, 0], "arm_r": [-85, 70, 0], "fore_r": [85, 0, 0], "blade": [90, 0, 0], "arm_l": [-15, 0, 20], "head": [0, -20, 0], "root": [0, 0, 0.3]}],
        [1.0, {}],
    ],
    "rising": [
        [0.0, {}],
        [0.32, {"torso": [25, -25, 0], "arm_r": [30, -20, 0], "fore_r": [85, 0, 0], "blade": [90, 0, 0], "arm_l": [-30, 0, 25], "root": [0, -0.12, 0]}],
        [0.55, {"torso": [-20, 10, 0], "arm_r": [-140, 0, 0], "fore_r": [85, 0, 0], "blade": [90, 0, 0], "arm_l": [-50, 0, 30], "head": [-15, 0, 0], "root": [0, 0.15, 0.2]}],
        [0.72, {"torso": [-25, 12, 0], "arm_r": [-165, 0, 0], "fore_r": [85, 0, 0], "blade": [90, 0, 0], "arm_l": [-40, 0, 30], "head": [-15, 0, 0], "root": [0, 0.12, 0.22]}],
        [1.0, {}],
    ],
}

# ---- the Revenant, the plain thrall: a wraith, it doesn't trade blows, it rears back and dives through you claws first
# (Thrall throws it at the one it's after, so the body flies; these are what it does with itself on the way) ----
REVENANT = {
    "dive": [
        [0.0, {}],
        [0.35, {"torso": [-25, 0, 0], "arm_r": [-150, 0, -25], "arm_l": [-150, 0, 25], "fore_r": [-30, 0, 0], "fore_l": [-30, 0, 0], "head": [-15, 0, 0], "root": [0, 0.2, -0.3]}],
        [0.55, {"torso": [55, 0, 0], "arm_r": [-115, 0, -10], "arm_l": [-115, 0, 10], "fore_r": [15, 0, 0], "fore_l": [15, 0, 0], "head": [-35, 0, 0], "root": [0, -0.1, 0.5]}],
        [0.72, {"torso": [58, 0, 0], "arm_r": [-75, 0, -20], "arm_l": [-75, 0, 20], "fore_r": [30, 0, 0], "fore_l": [30, 0, 0], "head": [-35, 0, 0], "root": [0, -0.1, 0.55]}],
        [1.0, {}],
    ],
    "rend": [
        [0.0, {}],
        [0.35, {"torso": [-15, -35, 0], "arm_r": [-170, -30, -30], "fore_r": [-25, 0, 0], "arm_l": [-40, 0, 25], "head": [-10, 15, 0], "root": [0, 0.15, -0.25]}],
        [0.55, {"torso": [45, 30, 0], "arm_r": [-95, 40, 0], "fore_r": [30, 0, 0], "arm_l": [-30, 0, 30], "head": [-30, -10, 0], "root": [0, -0.08, 0.45]}],
        [0.72, {"torso": [48, 40, 0], "arm_r": [-70, 60, 10], "fore_r": [35, 0, 0], "arm_l": [-25, 0, 30], "head": [-30, -15, 0], "root": [0, -0.08, 0.5]}],
        [1.0, {}],
    ],
}
REVENANT["rend_l"] = mirror(REVENANT["rend"])
REVENANT = {k: REVENANT[k] for k in ("dive", "rend", "rend_l")}

# ---- the Riftblade: four arms, four blades, it crosses them ----
RIFTBLADE = {
    "cross": [
        [0.0, {}],
        [0.35, {"torso": [-5, -30, 0], "arm_r": [-60, -40, -40], "fore_r": [-30, 0, 0], "arm2_r": [-40, -50, -50], "fore2_r": [-20, 0, 0], "arm_l": [-20, 0, 20], "arm2_l": [-10, 0, 20], "root": [0, 0, -0.05]}],
        [0.55, {"torso": [15, 30, 0], "arm_r": [-20, 40, 30], "fore_r": [50, 0, 0], "arm2_r": [-10, 45, 25], "fore2_r": [30, 0, 0], "arm_l": [-30, 10, 10], "arm2_l": [-20, 10, 10], "root": [0, 0, 0.35]}],
        [0.72, {"torso": [18, 35, 0], "arm_r": [-10, 50, 35], "fore_r": [55, 0, 0], "arm2_r": [-5, 55, 30], "fore2_r": [35, 0, 0], "arm_l": [-30, 10, 10], "arm2_l": [-20, 10, 10], "root": [0, 0, 0.38]}],
        [1.0, {}],
    ],
    "scissor": [
        [0.0, {}],
        [0.35, {"torso": [-10, 0, 0], "arm_r": [-70, -70, -30], "arm2_r": [-50, -70, -40], "arm_l": [-70, 70, 30], "arm2_l": [-50, 70, 40], "fore_r": [-20, 0, 0], "fore_l": [-20, 0, 0]}],
        [0.55, {"torso": [15, 0, 0], "arm_r": [-80, 40, 0], "arm2_r": [-60, 35, -10], "arm_l": [-80, -40, 0], "arm2_l": [-60, -35, 10], "fore_r": [30, 0, 0], "fore_l": [30, 0, 0], "root": [0, 0, 0.3]}],
        [0.72, {"torso": [15, 0, 0], "arm_r": [-75, 55, 0], "arm2_r": [-55, 50, -5], "arm_l": [-75, -55, 0], "arm2_l": [-55, -50, 5], "fore_r": [35, 0, 0], "fore_l": [35, 0, 0], "root": [0, 0, 0.32]}],
        [1.0, {}],
    ],
}
RIFTBLADE["cross_l"] = mirror(RIFTBLADE["cross"])
RIFTBLADE = {k: RIFTBLADE[k] for k in ("cross", "scissor", "cross_l")}

# ---- the Cantor: it sings at you; the book stays by the left hand, the right draws the blow up and pushes it out ----
CANTOR = {
    "push": [
        [0.0, {}],
        [0.35, {"torso": [-15, -15, 0], "arm_r": [-160, 0, -20], "fore_r": [-20, 0, 0], "book": [-20, 0, 0], "head": [-20, 0, 0], "root": [0, 0.1, -0.05]}],
        [0.55, {"torso": [15, 10, 0], "arm_r": [-85, 0, 0], "fore_r": [80, 0, 0], "book": [5, 0, 0], "head": [10, 0, 0], "root": [0, 0.05, 0.2]}],
        [0.72, {"torso": [18, 12, 0], "arm_r": [-88, 5, 0], "fore_r": [80, 0, 0], "book": [5, 0, 0], "head": [10, 0, 0], "root": [0, 0.05, 0.22]}],
        [1.0, {}],
    ],
    "smite": [
        [0.0, {}],
        [0.35, {"torso": [-10, -20, 0], "arm_r": [-175, 0, -15], "fore_r": [-10, 0, 0], "book": [-25, 0, 0], "head": [-25, 0, 0], "root": [0, 0.12, 0]}],
        [0.55, {"torso": [25, 10, 0], "arm_r": [-55, 0, -5], "fore_r": [60, 0, 0], "book": [5, 0, 0], "head": [15, 0, 0], "root": [0, 0, 0.15]}],
        [0.72, {"torso": [28, 12, 0], "arm_r": [-35, 0, 0], "fore_r": [60, 0, 0], "head": [15, 0, 0], "root": [0, 0, 0.15]}],
        [1.0, {}],
    ],
}

# ---- the Gatebreaker: walks, and hits the ground hard enough to feel it ----
GATEBREAKER = {
    "slam": [
        [0.0, {}],
        [0.35, {"torso": [-20, 0, 0], "arm_r": [-170, 0, -10], "arm_l": [-170, 0, 10], "fore_r": [-20, 0, 0], "fore_l": [-20, 0, 0], "head": [-15, 0, 0], "root": [0, 0.08, 0]}],
        [0.55, {"torso": [40, 0, 0], "arm_r": [-40, 0, 0], "arm_l": [-40, 0, 0], "head": [10, 0, 0], "leg_l": [-25, 0, 0], "shin_l": [40, 0, 0], "leg_r": [-25, 0, 0], "shin_r": [40, 0, 0], "root": [0, -0.2, 0.2]}],
        [0.72, {"torso": [42, 0, 0], "arm_r": [-30, 0, 5], "arm_l": [-30, 0, -5], "head": [10, 0, 0], "leg_l": [-25, 0, 0], "shin_l": [40, 0, 0], "leg_r": [-25, 0, 0], "shin_r": [40, 0, 0], "root": [0, -0.2, 0.22]}],
        [1.0, {}],
    ],
    "haymaker": [
        [0.0, {}],
        [0.35, {"torso": [-5, -40, 0], "arm_r": [30, -30, -30], "fore_r": [-70, 0, 0], "arm_l": [-40, 0, 20], "leg_l": [-20, 0, 0], "shin_l": [15, 0, 0], "root": [0, 0, -0.05]}],
        [0.55, {"torso": [15, 35, 0], "arm_r": [-90, 40, 0], "fore_r": [-5, 0, 0], "arm_l": [-20, 0, 15], "leg_r": [20, 0, 0], "leg_l": [-25, 0, 0], "shin_l": [20, 0, 0], "root": [0, -0.05, 0.3]}],
        [0.72, {"torso": [18, 45, 0], "arm_r": [-80, 60, 0], "arm_l": [-15, 0, 15], "leg_r": [20, 0, 0], "leg_l": [-25, 0, 0], "shin_l": [20, 0, 0], "root": [0, -0.05, 0.32]}],
        [1.0, {}],
    ],
}
GATEBREAKER["haymaker_l"] = mirror(GATEBREAKER["haymaker"])
GATEBREAKER = {k: GATEBREAKER[k] for k in ("slam", "haymaker", "haymaker_l")}

# ---- the Riftling: rears up on its back legs, and the sting comes over its head ----
RIFTLING = {
    "sting": [
        [0.0, {}],
        [0.35, {"torso": [-15, 0, 0], "sting": [-25, 0, 0], "leg_l0": [0, 0, 35], "leg_r0": [0, 0, -35], "head": [-10, 0, 0], "root": [0, 0.05, -0.08]}],
        [0.55, {"torso": [15, 0, 0], "sting": [75, 0, 0], "leg_l0": [0, 0, 10], "leg_r0": [0, 0, -10], "head": [10, 0, 0], "root": [0, -0.03, 0.3]}],
        [0.72, {"torso": [18, 0, 0], "sting": [80, 0, 0], "head": [10, 0, 0], "root": [0, -0.03, 0.32]}],
        [1.0, {}],
    ],
    "pounce": [
        [0.0, {}],
        [0.32, {"torso": [-30, 0, 0], "leg_l0": [0, 0, 45], "leg_r0": [0, 0, -45], "leg_l1": [0, 0, 25], "leg_r1": [0, 0, -25], "head": [-15, 0, 0], "sting": [-20, 0, 0], "root": [0, 0.12, -0.05]}],
        [0.55, {"torso": [25, 0, 0], "leg_l0": [0, -30, -10], "leg_r0": [0, 30, 10], "head": [20, 0, 0], "sting": [30, 0, 0], "root": [0, 0, 0.45]}],
        [0.72, {"torso": [20, 0, 0], "leg_l0": [0, -30, -10], "leg_r0": [0, 30, 10], "head": [15, 0, 0], "sting": [30, 0, 0], "root": [0, 0, 0.45]}],
        [1.0, {}],
    ],
}

# ---- the Oathwarden: shield on the left, spear on the right, and it fights like it was taught ----
OATHWARDEN = {
    "thrust": [
        [0.0, {}],
        [0.3, {"torso": [-5, -30, 0], "arm_r": [30, 0, -10], "spear": [0, 180, 0], "arm_l": [-60, 20, 10], "root": [0, 0, -0.1]}],
        [0.55, {"torso": [15, 20, 0], "arm_r": [-75, 0, 0], "fore_r": [75, 0, 0], "spear": [0, 180, 0], "arm_l": [-55, 10, 10], "head": [5, 0, 0], "root": [0, 0, 0.45]}],
        [0.72, {"torso": [15, 22, 0], "arm_r": [-78, 0, 0], "fore_r": [78, 0, 0], "spear": [0, 180, 0], "arm_l": [-55, 10, 10], "head": [5, 0, 0], "root": [0, 0, 0.48]}],
        [1.0, {}],
    ],
    "bash": [
        [0.0, {}],
        [0.35, {"torso": [-5, 30, 0], "arm_l": [-30, 0, 30], "fore_l": [-20, 0, 0], "arm_r": [-20, 0, -20], "root": [0, 0, -0.08]}],
        [0.55, {"torso": [15, -25, 0], "arm_l": [-80, -15, 0], "fore_l": [40, 0, 0], "arm_r": [-15, 0, -15], "head": [10, 0, 0], "root": [0, 0, 0.4]}],
        [0.72, {"torso": [15, -30, 0], "arm_l": [-82, -20, 0], "fore_l": [40, 0, 0], "arm_r": [-10, 0, -15], "head": [10, 0, 0], "root": [0, 0, 0.42]}],
        [1.0, {}],
    ],
    "low_thrust": [
        [0.0, {}],
        [0.3, {"torso": [10, -35, 0], "arm_r": [35, 0, -10], "spear": [0, 180, 0], "arm_l": [-60, 20, 10], "root": [0, -0.1, -0.1]}],
        [0.55, {"torso": [28, 20, 0], "arm_r": [-55, 0, 0], "fore_r": [55, 0, 0], "spear": [0, 180, 0], "arm_l": [-50, 10, 10], "head": [-10, 0, 0], "root": [0, -0.15, 0.5]}],
        [0.72, {"torso": [30, 22, 0], "arm_r": [-55, 0, 0], "fore_r": [58, 0, 0], "spear": [0, 180, 0], "arm_l": [-50, 10, 10], "head": [-10, 0, 0], "root": [0, -0.15, 0.52]}],
        [1.0, {}],
    ],
}

# ---- the Ossuary Colossus (the Crown's beast): hunched on its knuckles; it rears up to bring both fists down, backhands with
# one great arm, rakes with the two from its ribs, and roars ----
COLOSSUS = {
    "slam": [
        [0.0, {}],
        [0.35, {"torso": [-35, 0, 0], "arm_r": [-160, 0, -10], "arm_l": [-160, 0, 10], "fore_r": [-30, 0, 0], "fore_l": [-30, 0, 0], "head": [-15, 0, 0], "jaw": [20, 0, 0],
                "leg_l": [-15, 0, 0], "leg_r": [-15, 0, 0], "shin_l": [10, 0, 0], "shin_r": [10, 0, 0], "root": [0, 0.1, -0.2]}],
        [0.55, {"torso": [25, 0, 0], "arm_r": [-45, 0, 0], "arm_l": [-45, 0, 0], "fore_r": [-10, 0, 0], "fore_l": [-10, 0, 0], "head": [10, 0, 0], "jaw": [5, 0, 0],
                "leg_l": [-25, 0, 0], "leg_r": [-25, 0, 0], "shin_l": [35, 0, 0], "shin_r": [35, 0, 0], "root": [0, -0.15, 0.4]}],
        [0.72, {"torso": [28, 0, 0], "arm_r": [-35, 0, 0], "arm_l": [-35, 0, 0], "fore_r": [-10, 0, 0], "fore_l": [-10, 0, 0], "head": [10, 0, 0], "jaw": [5, 0, 0],
                "leg_l": [-25, 0, 0], "leg_r": [-25, 0, 0], "shin_l": [35, 0, 0], "shin_r": [35, 0, 0], "root": [0, -0.18, 0.45]}],
        [1.0, {}],
    ],
    "backhand": [
        [0.0, {}],
        [0.35, {"torso": [-5, -40, 0], "arm_r": [-70, -70, -20], "fore_r": [-20, 0, 0], "arm_l": [-10, 0, 10], "head": [0, 20, 0], "root": [0, 0, -0.1]}],
        [0.55, {"torso": [10, 35, 0], "arm_r": [-80, 40, 0], "fore_r": [-10, 0, 0], "arm_l": [-10, 0, 15], "head": [0, -15, 0], "root": [0, 0, 0.3]}],
        [0.72, {"torso": [10, 45, 0], "arm_r": [-75, 70, 10], "fore_r": [-10, 0, 0], "arm_l": [-10, 0, 15], "head": [0, -20, 0], "root": [0, 0, 0.32]}],
        [1.0, {}],
    ],
    "rake": [
        [0.0, {}],
        [0.35, {"torso": [-10, 0, 0], "arm2_r": [-120, 0, -20], "arm2_l": [-120, 0, 20], "fore2_r": [-40, 0, 0], "fore2_l": [-40, 0, 0], "jaw": [15, 0, 0], "root": [0, 0.05, -0.1]}],
        [0.55, {"torso": [15, 0, 0], "arm2_r": [-40, 30, 0], "arm2_l": [-40, -30, 0], "fore2_r": [20, 0, 0], "fore2_l": [20, 0, 0], "jaw": [5, 0, 0], "root": [0, 0, 0.3]}],
        [0.72, {"torso": [16, 0, 0], "arm2_r": [-20, 45, 0], "arm2_l": [-20, -45, 0], "fore2_r": [25, 0, 0], "fore2_l": [25, 0, 0], "jaw": [5, 0, 0], "root": [0, 0, 0.32]}],
        [1.0, {}],
    ],
    "roar": [
        [0.0, {}],
        [0.35, {"torso": [-10, 0, 0], "head": [12, 0, 0], "arm_r": [-12, 0, 6], "arm_l": [-12, 0, -6], "root": [0, -0.05, 0]}],
        [0.55, {"torso": [-40, 0, 0], "head": [-35, 0, 0], "jaw": [35, 0, 0], "arm_r": [-40, 0, -40], "arm_l": [-40, 0, 40], "arm2_r": [-60, 0, -40], "arm2_l": [-60, 0, 40], "root": [0, 0.15, 0]}],
        [0.72, {"torso": [-42, 0, 0], "head": [-38, 0, 0], "jaw": [38, 0, 0], "arm_r": [-42, 0, -42], "arm_l": [-42, 0, 42], "arm2_r": [-62, 0, -42], "arm2_l": [-62, 0, 42], "root": [0, 0.16, 0]}],
        [1.0, {}],
    ],
}
COLOSSUS["backhand_l"] = mirror(COLOSSUS["backhand"])
# the order Thrall.COLOSSUS_BLOWS names them in: the server picks the blow (each does its own thing) and says which
COLOSSUS = {k: COLOSSUS[k] for k in ("slam", "backhand", "rake", "backhand_l", "roar")}


def timed(keys, through=2.2):
    """three poses (keys[1] drawn back, keys[2] arriving, keys[3] a little past) into the whole blow: the coil pulls 12% further
    back than the draw, and what it does past the hit is pushed on to through times as far"""
    wind, hit, past = keys[1][1], keys[2][1], keys[3][1]
    bones = set(wind) | set(hit) | set(past)
    coil = {b: [v * 1.12 for v in wind.get(b, [0, 0, 0])] for b in bones}
    on = {}
    for b in bones:
        h, f = hit.get(b, [0, 0, 0]), past.get(b, [0, 0, 0])
        on[b] = [h[j] + (f[j] - h[j]) * through for j in range(3)]
    return [[0.0, {}], [0.28, wind, "o"], [0.44, coil, "s"], [0.53, hit, "i"], [0.62, hit, "s"], [0.78, on, "o"], [1.0, {}, "s"]]


# a cleave stops in the ground in front of it, it doesn't wrap round
THROUGH = {"cleave": 1.0}
for blows in (CHAMPION, REVENANT, RIFTBLADE, CANTOR, GATEBREAKER, RIFTLING, OATHWARDEN, COLOSSUS):
    for name in blows:
        blows[name] = timed(blows[name], THROUGH.get(name, 2.2))

MOVES = {"champion": CHAMPION, "revenant": REVENANT, "riftblade": RIFTBLADE, "cantor": CANTOR, "gatebreaker": GATEBREAKER,
         "riftling": RIFTLING, "oathwarden": OATHWARDEN, "colossus": COLOSSUS}


def check():
    for kind, blows in MOVES.items():
        bones = {b["name"] for b in json.load(open(os.path.join(ASSETS, "mounts", kind + ".json")))["bones"]} | {"root"}
        for name, keys in blows.items():
            ts = [k[0] for k in keys]
            assert ts == sorted(ts) and ts[0] == 0 and ts[-1] == 1, (kind, name, ts)
            for k in keys:
                t, pose = k[0], k[1]
                assert len(k) == 2 or k[2] in ("o", "i", "s"), (kind, name, k[2])
                for b in pose:
                    assert b in bones, (kind, name, t, b)


# ---- preview: the model posed in Python the way ThrallRender poses it, flat-shaded from its own texture ----
def quat_axis(ax, deg):
    a = math.radians(deg) / 2
    s = math.sin(a)
    return (math.cos(a), s if ax == 0 else 0, s if ax == 1 else 0, s if ax == 2 else 0)


def qmul(a, b):
    w1, x1, y1, z1 = a
    w2, x2, y2, z2 = b
    return (w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2, w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
            w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2, w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2)


def qmat(q):
    w, x, y, z = q
    return [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w), 0],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w), 0],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y), 0], [0, 0, 0, 1]]


def mm(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def tr(x, y, z):
    return [[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z], [0, 0, 0, 1]]


def ease(f, how):
    """as ThrallRender.Blow eases"""
    if how == "o":
        return 1 - (1 - f) ** 3
    if how == "i":
        return f * f * f
    return f * f * (3 - 2 * f)


def pose_at(keys, t):
    """the pose between the two keys either side of t, eased"""
    for i in range(len(keys) - 1):
        t0, p0 = keys[i][:2]
        t1, p1 = keys[i + 1][:2]
        if t0 <= t <= t1:
            f = (t - t0) / (t1 - t0) if t1 > t0 else 0
            f = ease(f, keys[i + 1][2] if len(keys[i + 1]) > 2 else "s")
            out = {}
            for b in set(p0) | set(p1):
                a, c = p0.get(b, [0, 0, 0]), p1.get(b, [0, 0, 0])
                out[b] = [a[j] + (c[j] - a[j]) * f for j in range(3)]
            return out
    return {}


def draw(kind, blows):
    from PIL import Image, ImageDraw
    model = json.load(open(os.path.join(ASSETS, "mounts", kind + ".json")))
    tex = Image.open(os.path.join(ASSETS, "textures/entity/mount_%s.png" % kind)).convert("RGBA")
    times = [0.0, 0.28, 0.44, 0.53, 0.78]
    shots = [(t, v) for v in (-35, -90) for t in times]     # from the front right, then straight from its right
    S, pad = 170, 10
    sheet = Image.new("RGB", (len(shots) * S + pad * 2, len(blows) * (S + 18) + pad * 2), (54, 52, 60))
    dr = ImageDraw.Draw(sheet)
    for row, (name, keys) in enumerate(blows.items()):
        dr.text((pad, pad + row * (S + 18)), name, fill=(230, 220, 200))
        for col, (t, deg) in enumerate(shots):
            paint(dr, model, tex, pose_at(keys, t), deg, S, pad + col * S + S / 2, pad + row * (S + 18) + 18 + S - 24)
            dr.text((pad + col * S + 4, pad + row * (S + 18) + 18), "%.2f %s" % (t, "side" if deg == -90 else ""), fill=(180, 180, 190))
    os.makedirs(PREVIEW, exist_ok=True)
    sheet.save(os.path.join(PREVIEW, kind + ".png"))


def gif(kind, blows, ticks):
    """every blow side by side at its real speed (60 frames a second, as the game draws it), a beat of rest between"""
    from PIL import Image, ImageDraw
    model = json.load(open(os.path.join(ASSETS, "mounts", kind + ".json")))
    tex = Image.open(os.path.join(ASSETS, "textures/entity/mount_%s.png" % kind)).convert("RGBA")
    S, fps = 200, 30
    n = round(ticks / 20 * fps)
    frames = []
    for i in range(n + fps // 2):
        img = Image.new("RGB", (len(blows) * S, S + 16), (54, 52, 60))
        dr = ImageDraw.Draw(img)
        t = min(1.0, i / n)
        for col, (name, keys) in enumerate(blows.items()):
            paint(dr, model, tex, pose_at(keys, t), -50, S, col * S + S / 2, S - 14)
            dr.text((col * S + 4, S), name, fill=(230, 220, 200))
        frames.append(img)
    os.makedirs(PREVIEW, exist_ok=True)
    frames[0].save(os.path.join(PREVIEW, kind + ".gif"), save_all=True, append_images=frames[1:], duration=1000 // fps, loop=0)


def paint(dr, model, tex, pose, deg, S, ox, oy):
    pitch = math.radians(10)
    if True:
        if True:
            view = math.radians(deg)
            cy, sy = math.cos(view), math.sin(view)
            world = {}
            polys = []
            for b in model["bones"]:
                r = pose.get(b["name"], [0, 0, 0])
                if len(r) == 4:   # a turn given straight as a quaternion (w, x, y, z)
                    q = tuple(r)
                else:
                    rx, ry, rz = r
                    q = qmul(qmul(quat_axis(1, ry), quat_axis(0, rx)), quat_axis(2, rz))
                px, py, pz = b["pivot"]
                parent = world[b["parent"]] if b["parent"] else tr(*pose.get("root", [0, 0, 0]))
                m = mm(mm(mm(parent, tr(px, py, pz)), qmat(q)), tr(-px, -py, -pz))
                world[b["name"]] = m
                for part in ("lit", "flame", "glow"):
                    v = b[part]
                    for i in range(0, len(v), 23):
                        pts, uv = [], [0, 0]
                        for c in range(4):
                            x, y, z, u, w = v[i + c * 5:i + c * 5 + 5]
                            pts.append((m[0][0] * x + m[0][1] * y + m[0][2] * z + m[0][3],
                                        m[1][0] * x + m[1][1] * y + m[1][2] * z + m[1][3],
                                        m[2][0] * x + m[2][1] * y + m[2][2] * z + m[2][3]))
                            uv[0] += u / 4
                            uv[1] += w / 4
                        nx, ny, nz = v[i + 20:i + 23]
                        n = (m[0][0] * nx + m[0][1] * ny + m[0][2] * nz, m[1][0] * nx + m[1][1] * ny + m[1][2] * nz,
                             m[2][0] * nx + m[2][1] * ny + m[2][2] * nz)
                        polys.append((pts, uv, n, part))
            # camera: turn round y, tip down, look along -z
            proj = []
            for pts, uv, n, part in polys:
                sp, depth = [], 0
                for X, Y, Z in pts:
                    x1, z1 = X * cy + Z * sy, -X * sy + Z * cy
                    y2, z2 = Y * math.cos(pitch) - z1 * math.sin(pitch), Y * math.sin(pitch) + z1 * math.cos(pitch)
                    sp.append((x1, y2))
                    depth += z2
                proj.append((depth / 4, sp, uv, n, part))
            proj.sort(key=lambda p: p[0])
            k = (S - 30) / 6.5
            for depth, sp, uv, n, part in proj:
                c = tex.getpixel((min(tex.width - 1, int(uv[0] * tex.width)), min(tex.height - 1, int(uv[1] * tex.height))))
                if c[3] < 30:
                    continue
                light = 0.55 + 0.45 * max(0, n[0] * 0.3 + n[1] * 0.8 + n[2] * 0.5)
                if part != "lit":
                    light = 1.1
                    c = (150, 110, 230, 255) if sum(c[:3]) > 300 else c
                dr.polygon([(ox + x * k, oy - y * k) for x, y in sp], fill=tuple(min(255, int(v * light)) for v in c[:3]))


def main():
    check()
    json.dump(MOVES, open(OUT, "w", encoding="utf-8"), separators=(",", ":"))
    print("wrote", OUT, {k: list(v) for k, v in MOVES.items()})
    if "--preview" in sys.argv:
        only = [a for a in sys.argv[1:] if not a.startswith("--")]
        for kind, blows in MOVES.items():
            if only and kind not in only:
                continue
            draw(kind, blows)
            gif(kind, blows, 24 if kind in ("champion", "gatebreaker", "colossus") else 16)
            print("drew", kind)


if __name__ == "__main__":
    main()
