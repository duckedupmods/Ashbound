"""Makes a monster's Epic Fight mesh hold together when it moves. efmob.py lands each limb on its joint and gives every
vertex one bone, so limbs can stand off their joints (a hand in the air) and robes swing as one stiff block through the
floor. This works on the finished mesh, so it needs no sources and keeps the look:

  gather  anything floating within an arm (a weapon off its hand) is slid onto it
  reach   each limb is drawn out to the joint it turns on, and its parent out to meet it; the far end stays put
  bend    what lies around a joint is shared by the bones either side, so an elbow bends rather than parts
  hang    what hangs below the hips (robes, skirts, cloaks) follows the thighs more the lower it is
  wield   a weapon that hangs from the hand is turned to lie along Epic Fight's grip, as a held item does, and its length
          goes into gate_mobs.json as "reach" (GateMobs.Kind): the swing then hits with what you see

    python tools/efskin.py [ids...] [--all]      no ids: the dungeon bosses; --all: every biped monster; originals kept in tools/renders/mesh_before_skin
"""
import glob
import json
import math
import os
import shutil
import sys
import zipfile

GAME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(GAME, "src/main/resources/assets/ashbound/animmodels/entity/")
KEEP = os.path.join(GAME, "tools/renders/mesh_before_skin/")
REACH = 0.015   # a limb this close to its joint is on it
TOUCH = 0.004   # boxes this close touch
FADE = 0.45     # how far along a limb the reach fades out
BEND = 0.09     # how far either side of a joint it's shared
HANG = 1.5      # how quickly a robe goes over to the thighs


def armature():
    """joint -> where it stands in the bind pose, and its parent"""
    jar = glob.glob(os.path.expanduser("~/.gradle/caches/modules-2/files-2.1/maven.modrinth/epic-fight/*/*/epic-fight-*.jar"))[0]
    d = json.loads(zipfile.ZipFile(jar).read("assets/epicfight/animmodels/entity/biped.json"))["armature"]
    at, parent = {}, {}

    def mul(a, b):
        return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]

    def walk(h, up, par):
        t = h["transform"]
        m = mul(up, [t[0:4], t[4:8], t[8:12], t[12:16]])
        at[h["name"]] = (m[0][3], m[1][3], m[2][3])
        parent[h["name"]] = par
        for c in h.get("children", []):
            walk(c, m, h["name"])

    for h in d["hierarchy"]:
        walk(h, [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], None)
    return d["joints"], at, parent


JOINTS, AT, PARENT = armature()
GRIP = (0.0, 0.995, -0.092)   # the way a held weapon points: Tool_R and Tool_L's -z in the bind pose
UNARMED = ("caster", "fist", "claw", "crawler")   # these keep Epic Fight's own reach, and what they carry where it hangs
MOUNTED = ("winter_marshal", "bone_hound", "grave_rat")   # efmob.mounted: only the rider is skinned, the mount's legs are nowhere near the biped's joints
OWN_PATCH = ["cinderhusk", "scholar", "lector", "inkbound"]   # bipeds with patches of their own: skinned, but not in gate_mobs.json
LONG = 0.35     # a hand reaching further than this from its grip holds a weapon
MIN_REACH = 0.8
# parent bone, child bone, the joint they turn about
LINKS = [("Root", "Thigh_R", "Thigh_R"), ("Root", "Thigh_L", "Thigh_L"), ("Thigh_R", "Leg_R", "Leg_R"), ("Thigh_L", "Leg_L", "Leg_L"),
         ("Root", "Torso", "Torso"), ("Torso", "Chest", "Chest"), ("Chest", "Head", "Head"),
         ("Chest", "Arm_R", "Arm_R"), ("Chest", "Arm_L", "Arm_L"), ("Arm_R", "Hand_R", "Hand_R"), ("Arm_L", "Hand_L", "Hand_L")]


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def length(a):
    return math.sqrt(dot(a, a))


def boxes(ids, tris):
    """the group's vertices as solid boxes: vertices on one triangle belong together"""
    parent = {i: i for i in ids}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for t in tris:
        if t[0] in parent and t[1] in parent and t[2] in parent:
            r = find(t[0])
            parent[find(t[1])] = r
            parent[find(t[2])] = r
    out = {}
    for i in ids:
        out.setdefault(find(i), []).append(i)
    return list(out.values())


def nearest(box, pos, a):
    """the closest point of a box's bounds to a"""
    return tuple(max(min(pos[i][k] for i in box), min(a[k], max(pos[i][k] for i in box))) for k in range(3))


def reach(ids, pos, tris, a, far):
    """draws the group out to point a; vertices fade from all of the move to none, `far` away. Returns the move's size."""
    if not ids:
        return 0.0
    best, r = 1e9, None
    for box in boxes(ids, tris):
        q = nearest(box, pos, a)
        d = length(sub(q, a))
        if d < best:
            best, r = d, q
    if best < REACH:
        return best
    c = sub(a, r)
    for i in ids:
        f = max(0.0, 1 - length(sub(pos[i], r)) / far)
        f = f * f * (3 - 2 * f)
        pos[i] = (pos[i][0] + c[0] * f, pos[i][1] + c[1] * f, pos[i][2] + c[2] * f)
    return best


def gather(ids, pos, tris, a):
    """whatever floats within a bone's group is slid onto the rest of it, starting from what's nearest the joint"""
    bs = boxes(ids, tris)
    if len(bs) < 2:
        return 0.0
    lo = [[min(pos[i][k] for i in b) for k in range(3)] for b in bs]
    hi = [[max(pos[i][k] for i in b) for k in range(3)] for b in bs]
    parent = list(range(len(bs)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in range(len(bs)):
        for j in range(i + 1, len(bs)):
            if all(lo[i][k] <= hi[j][k] + TOUCH and lo[j][k] <= hi[i][k] + TOUCH for k in range(3)):
                parent[find(i)] = find(j)
    clusters = {}
    for i in range(len(bs)):
        clusters.setdefault(find(i), []).append(i)
    if len(clusters) < 2:
        return 0.0
    near = lambda c: min(length(sub(nearest(bs[i], pos, a), a)) for i in c)  # noqa: E731
    rest = sorted(clusters.values(), key=near)
    main, rest, most = list(rest[0]), rest[1:], 0.0

    def move(c):
        """the shortest slide putting cluster c on main"""
        best = None
        for i in c:
            for j in main:
                v = [(lo[j][k] - hi[i][k] + TOUCH if lo[j][k] > hi[i][k] else hi[j][k] - lo[i][k] - TOUCH if hi[j][k] < lo[i][k] else 0.0) for k in range(3)]
                if best is None or dot(v, v) < dot(best, best):
                    best = v
        return best

    while rest:
        rest.sort(key=lambda c: dot(move(c), move(c)))
        c = rest.pop(0)
        v = move(c)
        most = max(most, length(v))
        for i in c:
            for k in range(3):
                lo[i][k] += v[k]
                hi[i][k] += v[k]
            for q in bs[i]:
                pos[q] = (pos[q][0] + v[0], pos[q][1] + v[1], pos[q][2] + v[2])
        main += c
    return most


def turn(p, axis, ang):
    """p about a unit axis through the origin"""
    c, s, d = math.cos(ang), math.sin(ang), dot(axis, p) * (1 - math.cos(ang))
    x = (axis[1] * p[2] - axis[2] * p[1], axis[2] * p[0] - axis[0] * p[2], axis[0] * p[1] - axis[1] * p[0])
    return tuple(p[i] * c + x[i] * s + axis[i] * d for i in range(3))


def wield(ids, pos, tris, tool):
    """turns what's held below the wrist onto the grip; returns how far the weapon reaches from the hand"""
    if not ids:
        return 0.0
    tip = max(ids, key=lambda i: length(sub(pos[i], tool)))
    w = sub(pos[tip], tool)
    n = length(w)
    if n < LONG:
        return 0.0
    w = (w[0] / n, w[1] / n, w[2] / n)
    ang = math.acos(max(-1.0, min(1.0, dot(w, GRIP))))
    if ang < math.radians(35):
        return n
    a = (w[1] * GRIP[2] - w[2] * GRIP[1], w[2] * GRIP[0] - w[0] * GRIP[2], w[0] * GRIP[1] - w[1] * GRIP[0])
    k = length(a)
    a = (a[0] / k, a[1] / k, a[2] / k)
    for box in boxes(ids, tris):
        if sum(pos[i][2] for i in box) / len(box) < tool[2] + 0.03:
            for i in box:
                q = turn(sub(pos[i], tool), a, ang)
                pos[i] = (q[0] + tool[0], q[1] + tool[1], q[2] + tool[2])
    return n


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def skin(pos, tris, joint, armed, mount=False):
    groups = {}
    for i, j in enumerate(joint):
        groups.setdefault(JOINTS[j], []).append(i)
    moved = {}
    for s in "RL":   # only an arm: a cloak or a wing may touch the body through another bone, or stand off it on purpose
        d = gather(groups.get("Arm_" + s, []) + groups.get("Hand_" + s, []), pos, tris, AT["Hand_" + s])
        if d > 0:
            moved["arm " + s + " gathered"] = round(d, 3)
    links = LINKS[5:] if mount else LINKS
    for up, down, at in links:
        a = AT[at]
        for g in (down, up):
            d = reach(groups.get(g, []), pos, tris, a, FADE)
            if d >= REACH:
                moved[g + ">" + at] = round(d, 3)
    reach_of = 0.0
    if armed:
        for s in "RL":
            reach_of = max(reach_of, wield(groups.get("Hand_" + s, []), pos, tris, AT["Tool_" + s]))
    weights = [{JOINTS[j]: 1.0} for j in joint]
    # bend: around each joint, parent and child share
    for up, down, at in links:
        a = AT[at]
        if down not in groups or up not in groups:
            continue
        way = sub(AT[at], AT[PARENT[at]])
        if length(way) < 1e-4:
            way = (0, 0, 1)
        n = length(way)
        way = (way[0] / n, way[1] / n, way[2] / n)
        for g, side in ((up, 1), (down, -1)):
            for i in groups[g]:
                off = sub(pos[i], a)
                if length(off) > BEND * 2.4:
                    continue
                t = dot(off, way) * side   # > 0: past the joint, on the other bone's side
                share = 0.5 * smooth(1 + t / BEND)
                if share > 0.01:
                    weights[i] = {g: 1 - share, (down if side > 0 else up): share}
    # hang: what's below the hips goes over to the thighs
    hip = AT["Thigh_R"][2]
    if mount:   # the body leans on Root far from the biped's legs: its own legs run from it to them, and never part
        for g in ("Thigh_R", "Thigh_L", "Leg_R", "Leg_L"):
            for i in groups.get(g, []):
                f = smooth((hip - pos[i][2]) / hip)
                weights[i] = {g: f, "Root": 1 - f} if f > 0.01 else {"Root": 1.0}
    wide = max(0.1, abs(AT["Thigh_R"][0]) * 1.3)
    for g in () if mount else ("Root", "Torso", "Chest"):
        for i in groups.get(g, []):
            drop = hip - pos[i][2]
            if drop <= 0.02:
                continue
            f = min(0.95, smooth(drop / hip * HANG))
            left = 0.5 + 0.5 * max(-1.0, min(1.0, pos[i][0] / wide)) * (1 if AT["Thigh_L"][0] > 0 else -1)
            w = {"Root": 1 - f}
            if left > 0.02:
                w["Thigh_L"] = f * left
            if left < 0.98:
                w["Thigh_R"] = f * (1 - left)
            weights[i] = w
    return weights, moved, reach_of


def pack(weights):
    """Epic Fight's form: per vertex a count, then (joint, index into a shared weight table) pairs"""
    table, keys, vc, vi = [], {}, [], []
    for w in weights:
        top = sorted(w.items(), key=lambda kv: -kv[1])[:3]
        s = sum(v for _, v in top)
        vc.append(len(top))
        for j, v in top:
            k = round(v / s, 3)
            if k not in keys:
                keys[k] = len(table)
                table.append(k)
            vi += [JOINTS.index(j), keys[k]]
    return table, vc, vi


def run(name, armed=False):
    """returns how far its weapon reaches from the hand, in mesh units (0: not armed)"""
    f = A + name + ".json"
    os.makedirs(KEEP, exist_ok=True)
    src = KEEP + name + ".json"
    if not os.path.exists(src):
        shutil.copy(f, src)
    d = json.load(open(src, encoding="utf-8"))
    v = d["vertices"]
    a = v["positions"]["array"]
    pos = [tuple(a[i:i + 3]) for i in range(0, len(a), 3)]
    ix = v["vindices"]["array"]
    joint = [ix[i * 2] for i in range(len(pos))]
    tris = []
    for part in v["parts"].values():
        t = part["array"]
        tris += [(t[i], t[i + 3], t[i + 6]) for i in range(0, len(t), 9)]
    weights, moved, reach_of = skin(pos, tris, joint, armed, name in MOUNTED)
    table, vc, vi = pack(weights)
    v["positions"]["array"] = [round(c, 5) for p in pos for c in p]
    v["weights"] = {"stride": 1, "count": len(table), "array": table}
    v["vcounts"] = {"stride": 1, "count": len(vc), "array": vc}
    v["vindices"] = {"stride": 1, "count": len(vi), "array": vi}
    json.dump(d, open(f, "w", encoding="utf-8"), separators=(",", ":"))
    print(name, "drew out", len(moved), "limbs, most", max(moved.values(), default=0), "| shared verts", sum(1 for n in vc if n > 1), "of", len(vc), "| reach", round(reach_of, 2))
    return reach_of


def main():
    rows = json.load(open(os.path.join(GAME, "src/main/resources/ashbound/gate_mobs.json"), encoding="utf-8"))
    moves = json.load(open(os.path.join(GAME, "src/main/resources/ashbound/mob_moves.json"), encoding="utf-8"))
    names = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--all" in sys.argv:
        names = [m["id"] for m in rows if m["rig"] == "biped"] + OWN_PATCH
    else:
        names = names or [m["id"] for m in rows if m.get("boss") and m["rig"] == "biped"]
    for m in rows:
        if m["id"] in names:
            armed = moves[m["id"]]["stance"] not in UNARMED
            r = run(m["mesh"], armed)
            if armed:
                m["reach"] = round(max(MIN_REACH, r), 3)
    for n in OWN_PATCH:
        if n in names:
            run(n)
    with open(os.path.join(GAME, "src/main/resources/ashbound/gate_mobs.json"), "w", encoding="utf-8", newline="\n") as out:
        json.dump(rows, out, indent=1)


if __name__ == "__main__":
    main()
