"""A chair sit for the townsfolk on the bare skeleton (ef_rest.py, no clip of Epic Fight's): the thighs out over the seat
(tipped DOWN degrees), the shins straight down to the floor, hands on the lap, a slow breath. Written in Epic Fight's clip format.

    python tools/npc_sit.py   -> src/main/resources/assets/ashbound/animmodels/animations/biped/npc_sit.json
"""
import json, math, os
import ef_rest
OUT = os.path.join(os.path.dirname(__file__), '..', 'src', 'main', 'resources', 'assets', 'ashbound', 'animmodels', 'animations', 'biped', 'npc_sit.json')
DOWN = math.radians(24)
BREATH = 4.0                                                # seconds, one in and out
HIPS = 0.724                                                # above the sitter's feet: NpcLife sets them down on the chair, so the shins hang to the floor

def flat(m): return [round(v, 6) for r in m for v in r]
def mul(a, b): return [[sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]
def rot(m): return [r[:3] for r in m[:3]]
def T(m): return [list(r) for r in zip(*m)]
def norm(v):
    l = math.sqrt(sum(c * c for c in v)); return [c / l for c in v]
def arc(a, b):
    """The least turn taking direction a onto b."""
    a, b = norm(a), norm(b)
    ax = [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
    s = math.sqrt(sum(c * c for c in ax)); c = sum(x * y for x, y in zip(a, b))
    if s < 1e-9: return [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    x, y, z = [v / s for v in ax]; t = math.atan2(s, c); C, S = math.cos(t), math.sin(t); V = 1 - C
    return [[C + x*x*V, x*y*V - z*S, x*z*V + y*S], [y*x*V + z*S, C + y*y*V, y*z*V - x*S], [z*x*V - y*S, z*y*V + x*S, C + z*z*V]]
def setrot(m, r):
    out = [list(row) for row in m]
    for i in range(3):
        for j in range(3): out[i][j] = r[i][j]
    return out
def dirof(r): return [r[0][1], r[1][1], r[2][1]]            # where a joint's +y (towards its child) points
def rx(d):
    c, s = math.cos(math.radians(d)), math.sin(math.radians(d)); return [[1, 0, 0], [0, c, -s], [0, s, c]]

R = ef_rest.rest()
root = [list(r) for r in R['Root']]
root[2][3] = HIPS
UP = rot(root)
J = {k: [list(r) for r in v] for k, v in R.items()}
J['Root'] = root
for side, sx in (('R', 1), ('L', -1)):
    # thigh: out over the seat, a touch apart
    w = mul(UP, rot(R['Thigh_' + side]))
    want = [0.06 * sx, math.cos(DOWN), -math.sin(DOWN)]
    Rt = mul(T(UP), mul(arc(dirof(w), want), w))
    # shin: straight down from the knee, the foot a little forward
    w2 = mul(mul(UP, Rt), rot(R['Leg_' + side]))
    Rl = mul(T(mul(UP, Rt)), mul(arc(dirof(w2), [0.02 * sx, 0.1, -1]), w2))
    J['Thigh_' + side] = setrot(R['Thigh_' + side], Rt)
    J['Leg_' + side] = setrot(R['Leg_' + side], Rl)
    J['Knee_' + side] = setrot(R['Knee_' + side], mul(Rl, mul(T(rot(R['Leg_' + side])), rot(R['Knee_' + side]))))
    k = mul(mul(root, J['Thigh_' + side]), J['Leg_' + side])
    foot = mul(k, [[0], [0.375], [0], [1]])
    print(side, 'knee', [round(r[3], 3) for r in k[:3]], 'foot', [round(r[0], 3) for r in foot[:3]])


def upper(lean):
    """arms from the shoulders down to the lap, the chest a little forward on the breath"""
    P = {k: [list(r) for r in v] for k, v in J.items()}
    chest = mul(mul(UP, rot(R['Torso'])), rx(-lean))
    P['Chest'] = setrot(R['Chest'], mul(T(mul(UP, rot(R['Torso']))), chest))
    for side, sx in (('R', 1), ('L', -1)):
        sh = mul(chest, rot(R['Shoulder_' + side]))
        w = mul(sh, rot(R['Arm_' + side]))
        w2 = mul(arc(dirof(w), [0.12 * sx, 0.3, -0.95]), w)
        P['Arm_' + side] = setrot(R['Arm_' + side], mul(T(sh), w2))
        h = mul(w2, rot(R['Hand_' + side]))
        h2 = mul(arc(dirof(h), [-0.1 * sx, 0.9, -0.42]), h)
        loc = mul(T(w2), h2)
        P['Hand_' + side] = setrot(R['Hand_' + side], loc)
        P['Elbow_' + side] = setrot(R['Elbow_' + side], mul(loc, mul(T(rot(R['Hand_' + side])), rot(R['Elbow_' + side]))))
    return P


keys = [(0.0, upper(1.5)), (BREATH / 2, upper(3.5)), (BREATH, upper(1.5))]
anim = [{'name': j, 'time': [t for t, _ in keys], 'transform': [flat(p[j]) for _, p in keys]} for j in R]
json.dump({'animation': anim}, open(OUT, 'w'), indent=1)
