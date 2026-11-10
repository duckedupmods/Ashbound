"""The dead of a fallen party (Encounters' "fallen" scene): three still poses on the bare skeleton (ef_rest.py, no clip of
Epic Fight's), lying on the ground the way the fallen lie: on the back with an arm flung out, face down reaching, curled
on one side. Written in Epic Fight's clip format; --sheet draws them as stick figures (top and side) to check.

    python tools/fallen_pose.py [--sheet]
        -> src/main/resources/assets/ashbound/animmodels/animations/biped/fallen_{back,front,side}.json
        -> tools/renders/fallen_poses.png (--sheet)

The armature's frame: z up, y the way the body faces standing, x its right.
"""
import json, math, os, sys
import ef_rest

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, '..', 'src', 'main', 'resources', 'assets', 'ashbound', 'animmodels', 'animations', 'biped')


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
def ry(d):
    c, s = math.cos(math.radians(d)), math.sin(math.radians(d)); return [[c, 0, s], [0, 1, 0], [-s, 0, c]]
def rz(d):
    c, s = math.cos(math.radians(d)), math.sin(math.radians(d)); return [[c, -s, 0], [s, c, 0], [0, 0, 1]]

R = ef_rest.rest()
PARENT = {'Thigh_R': 'Root', 'Leg_R': 'Thigh_R', 'Knee_R': 'Thigh_R', 'Thigh_L': 'Root', 'Leg_L': 'Thigh_L', 'Knee_L': 'Thigh_L',
          'Torso': 'Root', 'Chest': 'Torso', 'Head': 'Chest', 'Shoulder_R': 'Chest', 'Arm_R': 'Shoulder_R', 'Hand_R': 'Arm_R',
          'Tool_R': 'Hand_R', 'Elbow_R': 'Arm_R', 'Shoulder_L': 'Chest', 'Arm_L': 'Shoulder_L', 'Hand_L': 'Arm_L', 'Tool_L': 'Hand_L',
          'Elbow_L': 'Arm_L'}


def world(J, j):
    m = J[j]
    while j in PARENT:
        j = PARENT[j]; m = mul(J[j], m)
    return m


def pose(turn, lift, shift, aims, head=(0, 0), chest=0):
    """turn: the root's turn off standing; lift: the hips' height off the ground; shift: along y so the body's middle is
    over the entity's feet; aims: joint -> the way it should point (world); head: (turn about the neck, nod); chest: twist."""
    J = {k: [list(r) for r in v] for k, v in R.items()}
    root = setrot(R['Root'], mul(turn, rot(R['Root'])))
    root[1][3] = shift
    root[2][3] = lift
    J['Root'] = root
    if chest:
        J['Chest'] = setrot(R['Chest'], mul(rot(R['Chest']), ry(chest)))
    J['Head'] = setrot(R['Head'], mul(rot(R['Head']), mul(ry(head[0]), rx(head[1]))))
    for j in ('Thigh_R', 'Leg_R', 'Thigh_L', 'Leg_L', 'Arm_R', 'Hand_R', 'Arm_L', 'Hand_L'):
        if j not in aims: continue
        pw = rot(world(J, PARENT[j]))
        w = mul(pw, rot(R[j]))
        J[j] = setrot(R[j], mul(T(pw), mul(arc(dirof(w), aims[j]), w)))
    # the joints that only bend the skin follow their limb, as in npc_sit
    for s in ('R', 'L'):
        J['Knee_' + s] = setrot(R['Knee_' + s], mul(rot(J['Leg_' + s]), mul(T(rot(R['Leg_' + s])), rot(R['Knee_' + s]))))
        J['Elbow_' + s] = setrot(R['Elbow_' + s], mul(rot(J['Hand_' + s]), mul(T(rot(R['Hand_' + s])), rot(R['Elbow_' + s]))))
    return J


# on the back, head away along -y, face up: an arm flung out, the other across the belly, a knee fallen out
BACK = pose(rx(90), 0.17, 0.3, {
    'Arm_R': [0.92, 0.3, -0.2], 'Hand_R': [0.7, -0.68, -0.1],
    'Arm_L': [-0.3, 0.93, -0.15], 'Hand_L': [0.62, 0.62, 0.45],
    'Thigh_R': [0.22, 0.97, -0.08], 'Leg_R': [0.18, 0.98, -0.1],
    'Thigh_L': [-0.5, 0.82, 0.25], 'Leg_L': [-0.05, 0.95, -0.3]}, head=(68, 8))
# face down, head along +y: one arm reaching on ahead, the other back at the side, a leg drawn up
FRONT = pose(rx(-90), 0.15, -0.3, {
    'Arm_R': [0.35, 0.93, -0.08], 'Hand_R': [0.12, 0.99, -0.05],
    'Arm_L': [-0.35, -0.93, -0.1], 'Hand_L': [-0.15, -0.97, 0.15],
    'Thigh_R': [0.12, -0.99, -0.05], 'Leg_R': [0.08, -0.99, -0.02],
    'Thigh_L': [-0.65, -0.74, -0.05], 'Leg_L': [-0.15, -0.95, 0.25]}, head=(-70, 0))
# on the right side, curled: knees up, arms in front, the head tipped down (front is +x, head along -y)
SIDE = pose(mul(ry(90), rx(90)), 0.42, 0.25, {
    'Arm_R': [0.85, 0.3, -0.2], 'Hand_R': [0.75, -0.62, -0.15],
    'Arm_L': [0.6, 0.55, -0.55], 'Hand_L': [0.8, 0.3, -0.5],
    'Thigh_R': [0.75, 0.55, -0.35], 'Leg_R': [-0.35, 0.9, -0.1],
    'Thigh_L': [0.7, 0.6, -0.3], 'Leg_L': [-0.3, 0.93, -0.15]}, head=(0, -22), chest=10)

POSES = {'fallen_back': BACK, 'fallen_front': FRONT, 'fallen_side': SIDE}


def write():
    for name, J in POSES.items():
        anim = [{'name': j, 'time': [0.0, 4.0], 'transform': [flat(J[j]), flat(J[j])]} for j in R]
        with open(os.path.join(OUT, name + '.json'), 'w') as f:
            json.dump({'animation': anim}, f, indent=1)
        low = min(world(J, j)[2][3] for j in R)
        print(name, 'lowest joint', round(low, 3), 'hips', round(J['Root'][2][3], 3))


BONES = [('Root', 'Torso'), ('Torso', 'Chest'), ('Chest', 'Head'), ('Chest', 'Shoulder_R'), ('Shoulder_R', 'Arm_R'), ('Arm_R', 'Hand_R'),
         ('Hand_R', 'Tool_R'), ('Chest', 'Shoulder_L'), ('Shoulder_L', 'Arm_L'), ('Arm_L', 'Hand_L'), ('Hand_L', 'Tool_L'),
         ('Root', 'Thigh_R'), ('Thigh_R', 'Leg_R'), ('Root', 'Thigh_L'), ('Thigh_L', 'Leg_L')]
TIPS = {'Head': 0.45, 'Leg_R': 0.375, 'Leg_L': 0.375}


def sheet():
    from PIL import Image, ImageDraw
    S, W = 150, 330
    img = Image.new('RGB', (W * 3, W * 2), (24, 26, 30))
    d = ImageDraw.Draw(img)
    for col, (name, J) in enumerate(POSES.items()):
        pts = {j: [world(J, j)[i][3] for i in range(3)] for j in R}
        for j, ln in TIPS.items():
            w = world(J, j)
            pts[j + '_tip'] = [w[i][3] + w[i][1] * ln for i in range(3)]
        bones = BONES + [(j, j + '_tip') for j in TIPS]
        for row, (u, v, lab) in enumerate(((0, 1, 'top (x, y)'), (1, 2, 'side (y, z)'))):
            ox, oy = col * W + W // 2, row * W + W // 2
            if row == 1: d.line((col * W, oy, col * W + W, oy), fill=(80, 70, 50))   # the ground
            def P(p): return (ox + p[u] * S, oy - p[v] * S) if row == 1 else (ox + p[u] * S, oy - p[v] * S)
            for a, b in bones:
                left = a.endswith('_L') or b.endswith('_L') or b.startswith('Leg_L') or b.startswith('Thigh_L')
                d.line(P(pts[a]) + P(pts[b]), fill=(120, 170, 255) if left else (255, 170, 110), width=4)
            hx, hy = P(pts['Head_tip'])
            d.ellipse((hx - 10, hy - 10, hx + 10, hy + 10), outline=(240, 240, 240), width=2)
            d.text((col * W + 8, row * W + 8), name + '  ' + lab, fill=(220, 220, 220))
    out = os.path.join(HERE, 'renders', 'fallen_poses.png')
    img.save(out)
    print(out)


write()
if '--sheet' in sys.argv: sheet()
