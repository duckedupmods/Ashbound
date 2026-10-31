"""What's wrong with a monster's Epic Fight mesh, measured: how far it sinks under its feet, and how far each limb stands
from the bone it hangs on (a hand in the air). Reads animmodels/entity/NAME.json; sizes are drawn blocks (times its scale).

    python tools/boss_check.py [ids...]       no ids: the 29 dungeon bosses
"""
import json
import os
import sys

GAME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(GAME, "src/main/resources/assets/ashbound/animmodels/entity/")
JOINTS = ['Root', 'Thigh_R', 'Leg_R', 'Knee_R', 'Thigh_L', 'Leg_L', 'Knee_L', 'Torso', 'Chest', 'Head', 'Shoulder_R',
          'Arm_R', 'Hand_R', 'Tool_R', 'Elbow_R', 'Shoulder_L', 'Arm_L', 'Hand_L', 'Tool_L', 'Elbow_L']
LINKS = [('Root', 'Thigh_R'), ('Root', 'Thigh_L'), ('Thigh_R', 'Leg_R'), ('Thigh_L', 'Leg_L'), ('Root', 'Torso'), ('Torso', 'Chest'),
         ('Chest', 'Head'), ('Chest', 'Arm_R'), ('Chest', 'Arm_L'), ('Arm_R', 'Hand_R'), ('Arm_L', 'Hand_L')]


def load(name):
    v = json.load(open(A + name + ".json", encoding="utf-8"))["vertices"]
    a = v["positions"]["array"]
    pos = [(a[i], a[i + 1], a[i + 2]) for i in range(0, len(a), 3)]
    ix = v["vindices"]["array"]
    return pos, [ix[i * 2] for i in range(len(pos))]


def gap(p, q):
    """closest distance between two vertex sets, on a coarse grid of the second"""
    cell = {}
    for b in q:
        cell.setdefault((int(b[0] * 4), int(b[1] * 4), int(b[2] * 4)), b)
    best = 1e9
    for a in p:
        for b in cell.values():
            d = (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2
            if d < best:
                best = d
    return best ** 0.5


def main():
    rows = json.load(open(os.path.join(GAME, "src/main/resources/ashbound/gate_mobs.json"), encoding="utf-8"))
    names = sys.argv[1:] or [m["id"] for m in rows if m.get("boss")]
    by = {m["id"]: m for m in rows}
    out = {}
    for nm in names:
        m = by[nm]
        if m["rig"] != "biped":
            print("%-16s %s rig, not measured" % (nm, m["rig"]))
            continue
        pos, joint = load(m["mesh"])
        sc = m["scale"]
        ys = sorted(p[2] for p in pos)  # Epic Fight meshes are z up
        byj = {}
        for p, j in zip(pos, joint):
            byj.setdefault(JOINTS[j], []).append(p)
        floor = ys[0] * sc
        bad = []
        for a, b in LINKS:
            if a in byj and b in byj:
                g = gap(byj[b][::3], byj[a]) * sc
                if g > 0.25:
                    bad.append("%s-%s %.1f" % (a, b, g))
            elif b in byj:
                bad.append("%s missing" % a)
        low = sum(1 for y in ys if y < -0.02) / len(ys)
        print("%-16s scale %.2f h %.1f top %5.1f  floor %5.2f (%2d%% of it below)  %s" % (nm, sc, m["h"], ys[-1] * sc, floor, low * 100, "; ".join(bad)))
        out[nm] = {"floor": floor, "below": low, "gaps": bad}
    json.dump(out, open(os.path.join(GAME, "tools/renders/boss_check.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
