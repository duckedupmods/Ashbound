"""The smith's clips on Epic Fight's biped, written as its own clip format: forge_ready (hammer up, tongs on the work,
held between blows), forge_strike (the blow lands in 0.07 s so it's on your click, then back up) and forge_tap (the
master's small taps). Poses are world directions (x to the right hand, y forward, z up) on the bare skeleton:
ef_rest.py reads its joint offsets, never one of Epic Fight's clips (those are all rights reserved).

    python tools/forge_clips.py   -> assets/ashbound/animmodels/animations/biped/forge_*.json
"""
import json, math, os
import ef_rest
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'main', 'resources', 'assets', 'ashbound', 'animmodels', 'animations', 'biped')

def M(t): return [t[i*4:i*4+4] for i in range(4)]
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
def dirof(r): return [r[0][1], r[1][1], r[2][1]]          # where a joint's +y (towards its child) points
def rx(d):
    c, s = math.cos(math.radians(d)), math.sin(math.radians(d)); return [[1, 0, 0], [0, c, -s], [0, s, c]]
def rz(d):
    c, s = math.cos(math.radians(d)), math.sin(math.radians(d)); return [[c, -s, 0], [s, c, 0], [0, 0, 1]]

IDLE = ef_rest.rest()                                      # the skeleton standing, arms out
UP = rot(IDLE['Root'])                                     # the hips square to the front
# which way an item in the hand points, in Tool_R's frame: forward with the arm hanging at rest
def _item_axis():
    w = mul(mul(mul(mul(UP, rot(IDLE['Torso'])), rot(IDLE['Chest'])), rot(IDLE['Shoulder_R'])), rot(IDLE['Arm_R']))
    w = mul(arc(dirof(w), [0, 0, -1]), w)                  # the arm down
    h = mul(w, rot(IDLE['Hand_R']))
    w = mul(mul(arc(dirof(h), [0, 0, -1]), h), rot(IDLE['Tool_R']))
    best = max(range(3), key=lambda k: abs(w[1][k]))
    s = 1 if w[1][best] > 0 else -1
    return [s if k == best else 0 for k in range(3)]
ITEM = _item_axis()


def pose(hips, lean, twist, nod, r_arm, r_fore, r_item, l_arm, l_fore):
    """lean forward and twist (degrees) shared between the waist and chest; arms as world directions."""
    J = {k: [list(r) for r in v] for k, v in IDLE.items()}
    root = setrot(IDLE['Root'], UP); root[2][3] = IDLE['Root'][2][3] + hips
    J['Root'] = root
    half = mul(rz(twist / 2), mul(rx(-lean / 2), UP)); full = mul(rz(twist), mul(rx(-lean), UP))
    J['Torso'] = setrot(IDLE['Torso'], mul(T(UP), half))
    J['Chest'] = setrot(IDLE['Chest'], mul(T(half), full))
    J['Head'] = setrot(IDLE['Head'], mul(T(full), mul(rx(-nod), mul(rz(-twist * 0.6), UP))))
    for side, arm, fore in (('R', r_arm, r_fore), ('L', l_arm, l_fore)):
        sh = mul(full, rot(IDLE['Shoulder_' + side]))
        w = mul(sh, rot(IDLE['Arm_' + side]))
        w2 = mul(arc(dirof(w), arm), w)
        J['Arm_' + side] = setrot(IDLE['Arm_' + side], mul(T(sh), w2))
        h = mul(w2, rot(IDLE['Hand_' + side]))
        h2 = mul(arc(dirof(h), fore), h)
        loc = mul(T(w2), h2)
        J['Hand_' + side] = setrot(IDLE['Hand_' + side], loc)
        J['Elbow_' + side] = setrot(IDLE['Elbow_' + side], mul(loc, mul(T(rot(IDLE['Hand_' + side])), rot(IDLE['Elbow_' + side]))))
        if side == 'R' and r_item:
            tw = mul(h2, rot(IDLE['Tool_R']))
            now = [sum(tw[i][k] * ITEM[k] for k in range(3)) for i in range(3)]
            tw2 = mul(arc(now, r_item), tw)
            J['Tool_R'] = setrot(IDLE['Tool_R'], mul(T(h2), tw2))
    return J


def hand(J):
    m = mul(mul(mul(mul(J['Root'], J['Torso']), J['Chest']), J['Shoulder_R']), J['Arm_R'])
    m = mul(mul(m, J['Hand_R']), J['Tool_R'])
    return [round(r[3], 2) for r in m[:3]]


def write(name, keys):
    joints = list(IDLE)
    anim = [{'name': j, 'time': [t for t, _ in keys], 'transform': [flat(p[j]) for _, p in keys]} for j in joints]
    with open(os.path.join(OUT, name + '.json'), 'w') as f:
        json.dump({'animation': anim}, f)
    print(name, 'keys', [t for t, _ in keys], 'hand', [hand(p) for _, p in keys])


UPPER = dict(l_arm=(-0.1, 0.6, -0.8), l_fore=(0.25, 0.95, -0.2))
READY = pose(0, -6, -16, 22, (0.45, -0.25, 0.86), (0.05, 0.35, 0.93), (0, -0.8, 0.6), **UPPER)
BACK = pose(-0.01, -8, -18, 22, (0.47, -0.3, 0.83), (0.04, 0.26, 0.96), (0, -0.88, 0.47), **UPPER)
LAND = pose(-0.05, 20, 8, 30, (0.12, 0.8, -0.58), (0.0, 0.9, -0.44), (0, 0.97, -0.25), **UPPER)
BOUNCE = pose(-0.04, 14, 4, 28, (0.2, 0.75, -0.1), (0.05, 0.8, 0.3), (0, 0.6, 0.8), **UPPER)
write('forge_ready', [(0.0, READY), (0.8, BACK), (1.6, READY)])
write('forge_strike', [(0.0, READY), (0.07, LAND), (0.11, LAND), (0.22, BOUNCE), (0.42, READY)])

STAND = pose(0, 6, 0, 26, (0.3, 0.35, -0.88), (0.1, 0.8, 0.3), (0, 0.5, 0.86), **UPPER)
TAP = pose(-0.01, 9, 0, 28, (0.25, 0.5, -0.83), (0.05, 0.92, -0.38), (0, 0.97, -0.2), **UPPER)
write('forge_tap', [(0.0, STAND), (0.05, TAP), (0.1, TAP), (0.28, STAND)])
write('forge_low', [(0.0, STAND), (0.8, pose(-0.01, 7, 0, 27, (0.3, 0.37, -0.87), (0.1, 0.82, 0.26), (0, 0.55, 0.83), **UPPER)), (1.6, STAND)])
