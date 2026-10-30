"""Puts one of Ashbound's monsters on Epic Fight's biped skeleton, so Epic Fight animates it.

Our monsters are chunky meshes, one per bone of their own rig (E:/Ashbound/.../models/entity/NAME/). Epic
Fight's animations drive its biped armature (epicfight:entity/biped), whose joints sit where a player's do. So
each of our bones is fitted onto a biped joint: scaled down to player size, its pivot moved onto the joint, its
length stretched to the joint's, and every vertex weighted to that joint. The monster keeps its own look; it is
drawn bigger again in game (CinderhuskPatch's scale). Writes assets/ashbound/animmodels/entity/NAME.json in
Epic Fight's mesh format and copies the texture.

    python tools/efmob.py cinderhusk
"""
import json
import shutil
import sys

import port_weapons as P

SRC = 'E:/Ashbound/src/main/resources/assets/ashbound/'
FOLK = P.os.path.dirname(P.os.path.abspath(__file__)).replace(chr(92), '/') + '/folk_src/'   # folkforge.py's remade townsfolk

# Epic Fight's biped joints, in the order its armature lists them (the ids its meshes are weighted by)
JOINTS = ['Root', 'Thigh_R', 'Leg_R', 'Knee_R', 'Thigh_L', 'Leg_L', 'Knee_L', 'Torso', 'Chest', 'Head', 'Shoulder_R',
          'Arm_R', 'Hand_R', 'Tool_R', 'Elbow_R', 'Shoulder_L', 'Arm_L', 'Hand_L', 'Tool_L', 'Elbow_L']
J = {n: i for i, n in enumerate(JOINTS)}

# where those joints stand at rest, in our rigs' frame (blocks; x to the monster's left, y up, z forward)
AT = {'Root': 0.764, 'Torso': 0.814, 'Chest': 1.114, 'Head': 1.514, 'Arm': 1.394, 'Hand': 1.094, 'Tool': 0.822,
      'Thigh': 0.761, 'Leg': 0.386, 'arm_x': 0.375, 'leg_x': 0.125}

# each monster: bone -> (joint, mesh part, the biped point its pivot lands on, stretch along its length)
# a joint of None splits the bone between Torso and Chest at the chest's height
RIGS = {
    'cinderhusk': {
        'hips': ('Root', 'torso', (0, AT['Root']), 1.0),
        'torso': (None, 'torso', (0, AT['Torso']), 1.18),
        'head': ('Head', 'head', (0, AT['Head']), 1.0),
        'arm_r': ('Arm_R', 'rightArm', (-AT['arm_x'], AT['Arm']), 0.98),
        'fore_r': ('Hand_R', 'rightArm', (-AT['arm_x'], AT['Hand']), 0.72),
        'hand_r': ('Hand_R', 'rightArm', 'fore_r', 0.72),
        'arm_l': ('Arm_L', 'leftArm', (AT['arm_x'], AT['Arm']), 0.98),
        'fore_l': ('Hand_L', 'leftArm', (AT['arm_x'], AT['Hand']), 0.72),
        'hand_l': ('Hand_L', 'leftArm', 'fore_l', 0.72),
        'thigh_r': ('Thigh_R', 'rightLeg', (-AT['leg_x'], AT['Thigh']), 1.15),
        'shin_r': ('Leg_R', 'rightLeg', (-AT['leg_x'], AT['Leg']), 0.95),
        'foot_r': ('Leg_R', 'rightLeg', 'shin_r', 0.95),
        'thigh_l': ('Thigh_L', 'leftLeg', (AT['leg_x'], AT['Thigh']), 1.15),
        'shin_l': ('Leg_L', 'leftLeg', (AT['leg_x'], AT['Leg']), 0.95),
        'foot_l': ('Leg_L', 'leftLeg', 'shin_l', 0.95),
    },
}
def biped(name, extra=None, over=None):
    """A two-legged rig fitted the usual way: each limb's pivot on its biped joint, stretched to the joint's length.
    extra: more bones, bone -> (joint, part, the bone it rides on)."""
    bones = {b['name']: b for b in json.load(open(SRC + 'models/entity/%s/rig.json' % name, encoding='utf-8'))['bones']}
    k = AT['Root'] / bones['hips']['pivot'][1]

    def y(b):
        return bones[b]['pivot'][1]

    def fit(want, top, bot):
        if top not in bones or (bot and bot not in bones):   # a rig without that bone (a stump, a hand under a cloak)
            return 1.0
        return max(0.6, min(1.5, want / max(0.05, k * (y(top) - (y(bot) if bot else 0)))))
    rig = {'hips': ('Root', 'torso', (0, AT['Root']), 1.0),
           'torso': (None, 'torso', (0, AT['Torso']), fit(AT['Head'] - AT['Torso'], 'head', 'torso')),
           'head': ('Head', 'head', (0, AT['Head']), 1.0)}
    for s, side, sx in (('r', 'R', -1), ('l', 'L', 1)):
        arm, leg = ('rightArm', 'rightLeg') if s == 'r' else ('leftArm', 'leftLeg')
        rig['arm_' + s] = ('Arm_' + side, arm, (sx * AT['arm_x'], AT['Arm']), fit(AT['Arm'] - AT['Hand'], 'arm_' + s, 'fore_' + s))
        rig['fore_' + s] = ('Hand_' + side, arm, (sx * AT['arm_x'], AT['Hand']), fit(AT['Hand'] - AT['Tool'], 'fore_' + s, 'hand_' + s))
        rig['hand_' + s] = ('Hand_' + side, arm, 'fore_' + s, rig['fore_' + s][3])
        rig['thigh_' + s] = ('Thigh_' + side, leg, (sx * AT['leg_x'], AT['Thigh']), fit(AT['Thigh'] - AT['Leg'], 'thigh_' + s, 'shin_' + s))
        rig['shin_' + s] = ('Leg_' + side, leg, (sx * AT['leg_x'], AT['Leg']), fit(AT['Leg'], 'shin_' + s, None))
        rig['foot_' + s] = ('Leg_' + side, leg, 'shin_' + s, rig['shin_' + s][3])
    for b, (joint, part, on) in (extra or {}).items():
        rig[b] = (joint, part, on, rig[on][3])
    rig.update(over or {})
    return {b: v for b, v in rig.items() if b in bones}


# Epic Fight's spider: one joint per leg (no knee), front pair 1 to back pair 4, L on the spider's left
SPIDER_JOINTS = ['Root', 'Head', 'Stomach', 'RL4', 'RL2', 'RL3', 'RL1', 'LL4', 'LL2', 'LL3', 'LL1']
SPIDER_PARTS = ['middleStomach', 'head', 'rightLeg1', 'rightLeg2', 'rightLeg3', 'rightLeg4', 'bottomStomach',
                'leftLeg1', 'leftLeg2', 'leftLeg3', 'leftLeg4']
SPIDER_ROOT = 0.481   # its Root joint's height
# each spider: bone -> joint (legs and shins go to their leg's joint by name); the body is scaled as one piece
SPIDERS = {
    'mite': {'body': 'Root', 'head': 'Head', 'abdomen': 'Stomach'},
    'silkqueen': {'body': 'Root', 'head': 'Head', 'fang_l': 'Head', 'fang_r': 'Head', 'abdomen': 'Stomach'},
    # the woman on the weaver's front rides its head joint, so she lunges with every bite
    'weaver': {'body': 'Root', 'abdomen': 'Stomach', 'torso': 'Head', 'head': 'Head', 'hair': 'Head',
               'arm_l': 'Head', 'fore_l': 'Head', 'hand_l': 'Head', 'arm_r': 'Head', 'fore_r': 'Head', 'hand_r': 'Head'},
}


def export_spider(name):
    """A spider kept whole, scaled down about its body so the body sits where Epic Fight's spider's does, every
    vertex weighted to the joint its bone moves with."""
    rig = json.load(open(SRC + 'models/entity/%s/rig.json' % name, encoding='utf-8'))
    pv = next(b for b in rig['bones'] if b['name'] == 'body')['pivot']
    k = SPIDER_ROOT / pv[1]
    J2 = {n: i for i, n in enumerate(SPIDER_JOINTS)}
    pos, uvs, nrm = [], [], []
    pkey, ukey, nkey = {}, {}, {}
    parts = {p: [] for p in SPIDER_PARTS}

    def index(table, lst, key):
        i = table.get(key)
        if i is None:
            i = table[key] = len(lst)
            lst.append(key)
        return i
    for b in rig['bones']:
        bone = b['name']
        if bone[:4] in ('leg_', 'shin'):
            side, n = bone.split('_')[1][0], bone[-1]
            joint = ('LL' if side == 'l' else 'RL') + n
            part = ('leftLeg' if side == 'l' else 'rightLeg') + n
        else:
            joint = SPIDERS[name].get(bone, 'Root')
            part = {'Root': 'middleStomach', 'Head': 'head', 'Stomach': 'bottomStomach'}[joint]
        v, vt, vn, tris = load_obj(SRC + 'models/entity/%s/%s.obj' % (name, bone))
        for tri in tris:
            for (vi, ti, ni) in tri:
                x, y, z = v[vi]
                mx, my, mz = (x - pv[0]) * k, SPIDER_ROOT + (y - pv[1]) * k, (z - pv[2]) * k
                pi = index(pkey, pos, (round(-mx, 5), round(mz, 5), round(my, 5), J2[joint]))
                u, w = vt[ti]
                ui = index(ukey, uvs, (round(u, 6), round(1 - w, 6)))
                nx, ny, nz = vn[ni]
                ni2 = index(nkey, nrm, (round(-nx, 4), round(nz, 4), round(ny, 4)))
                parts[part] += [pi, ui, ni2]
    write(name, pos, uvs, nrm, parts, SPIDER_PARTS, k)


def write(name, pos, uvs, nrm, parts, names, k):
    for p in names:
        if not parts[p]:
            parts[p] = [0, 0, 0] * 3   # an empty triangle: nothing to draw, but the part exists
    out = {'vertices': {
        'positions': {'stride': 3, 'count': len(pos), 'array': [c for p in pos for c in p[:3]]},
        'uvs': {'stride': 2, 'count': len(uvs), 'array': [c for u in uvs for c in u]},
        'normals': {'stride': 3, 'count': len(nrm), 'array': [c for n in nrm for c in n]},
        'vcounts': {'stride': 1, 'count': len(pos), 'array': [1] * len(pos)},
        'weights': {'stride': 1, 'count': 1, 'array': [1.0]},
        'vindices': {'stride': 1, 'count': len(pos) * 2, 'array': [c for p in pos for c in (p[3], 0)]},
        'parts': {p: {'stride': 3, 'count': len(a) // 3, 'array': a} for p, a in parts.items()},
    }}
    P.dump(P.ASSETS + 'animmodels/entity/%s.json' % name, out)
    P.os.makedirs(P.ASSETS + 'textures/entity', exist_ok=True)
    shutil.copy(SRC + 'textures/entity/%s.png' % name, P.ASSETS + 'textures/entity/%s.png' % name)
    print(name, len(pos), 'verts', sum(len(a) for a in parts.values()) // 9, 'tris, scale back', round(1 / k, 3))


# the Silk Archive's two-legged ones (tools/voxscholar.py and the rest in E:/Ashbound, --export first)
RIGS['scholar'] = biped('scholar', {'skirt': ('Root', 'torso', 'hips'), 'jaw': ('Head', 'head', 'head'),
                                    'leg_l1': ('Chest', 'torso', 'torso'), 'leg_r1': ('Chest', 'torso', 'torso'),
                                    'leg_l2': ('Chest', 'torso', 'torso'), 'leg_r2': ('Chest', 'torso', 'torso'),
                                    'tome': ('Hand_R', 'rightArm', 'fore_r')})
# the lector's four arms hold its book up: each upper arm kept whole on its shoulder, the lower pair on the chest
RIGS['lector'] = biped('lector', {'robe': ('Root', 'torso', 'hips'), 'book': ('Chest', 'torso', 'torso'),
                                  'arm2_l': ('Chest', 'torso', 'torso'), 'fore2_l': ('Chest', 'torso', 'torso'),
                                  'hand2_l': ('Chest', 'torso', 'torso'), 'arm2_r': ('Chest', 'torso', 'torso'),
                                  'fore2_r': ('Chest', 'torso', 'torso'), 'hand2_r': ('Chest', 'torso', 'torso')})
for _s, _side in (('l', 'L'), ('r', 'R')):
    _arm = 'leftArm' if _s == 'l' else 'rightArm'
    RIGS['lector']['fore_' + _s] = ('Arm_' + _side, _arm, 'arm_' + _s, RIGS['lector']['arm_' + _s][3])
    RIGS['lector']['hand_' + _s] = ('Arm_' + _side, _arm, 'arm_' + _s, RIGS['lector']['arm_' + _s][3])
RIGS['inkbound'] = biped('inkbound', {'lance': ('Hand_R', 'rightArm', 'fore_r')})


# the parts Epic Fight's humanoid meshes look up; the ones we don't have get an empty stand-in
PARTS = ['head', 'torso', 'rightArm', 'leftArm', 'rightLeg', 'leftLeg', 'hat', 'jacket', 'rightSleeve', 'leftSleeve',
         'rightPants', 'leftPants']


def load_obj(path):
    v, vt, vn, tris = [], [], [], []
    for l in open(path, encoding='utf-8'):
        p = l.split()
        if not p:
            continue
        if p[0] == 'v':
            v.append(tuple(map(float, p[1:4])))
        elif p[0] == 'vt':
            vt.append(tuple(map(float, p[1:3])))
        elif p[0] == 'vn':
            vn.append(tuple(map(float, p[1:4])))
        elif p[0] == 'f':
            ix = [tuple(int(a) - 1 for a in c.split('/')) for c in p[1:]]
            for k in range(1, len(ix) - 1):
                tris.append((ix[0], ix[k], ix[k + 1]))
    return v, vt, vn, tris


def export(name):
    rig = json.load(open(SRC + 'models/entity/%s/rig.json' % name, encoding='utf-8'))
    bones = {b['name']: b for b in rig['bones']}
    hip_y = bones['hips']['pivot'][1]
    k = AT['Root'] / hip_y   # down to player size
    pos, uvs, nrm, weights_of = [], [], [], []
    pkey, ukey, nkey = {}, {}, {}
    parts = {p: [] for p in PARTS}

    def index(table, lst, key):
        i = table.get(key)
        if i is None:
            i = table[key] = len(lst)
            lst.append(key)
        return i

    for bone, (joint, part, target, stretch) in RIGS[name].items():
        b = bones[bone]
        # a bone riding on another (a hand on its forearm) is placed exactly as that one is
        frame = bones[target] if isinstance(target, str) else b
        land = RIGS[name][target][2] if isinstance(target, str) else target
        pv = frame['pivot']
        v, vt, vn, tris = load_obj(SRC + 'models/entity/%s/%s.obj' % (name, bone))
        for tri in tris:
            for (vi, ti, ni) in tri:
                x, y, z = v[vi]
                # into the biped's place: scaled about our pivot, stretched along the bone, the pivot onto the joint
                mx = land[0] + (x - pv[0]) * k
                my = land[1] + (y - pv[1]) * k * stretch
                mz = (z - pv[2]) * k
                j = joint if joint else ('Torso' if my < AT['Chest'] else 'Chest')
                # our frame -> Blender's, which Epic Fight's meshes are written in: x right, y forward, z up
                p = (round(-mx, 5), round(mz, 5), round(my, 5), J[j])
                pi = index(pkey, pos, p)
                u, w = vt[ti]
                ui = index(ukey, uvs, (round(u, 6), round(1 - w, 6)))
                nx, ny, nz = vn[ni]
                ni2 = index(nkey, nrm, (round(-nx, 4), round(nz, 4), round(ny, 4)))
                parts[part] += [pi, ui, ni2]
    for p in PARTS:
        if not parts[p]:
            parts[p] = [0, 0, 0] * 3   # an empty triangle: nothing to draw, but the part exists
    out = {'vertices': {
        'positions': {'stride': 3, 'count': len(pos), 'array': [c for p in pos for c in p[:3]]},
        'uvs': {'stride': 2, 'count': len(uvs), 'array': [c for u in uvs for c in u]},
        'normals': {'stride': 3, 'count': len(nrm), 'array': [c for n in nrm for c in n]},
        'vcounts': {'stride': 1, 'count': len(pos), 'array': [1] * len(pos)},
        'weights': {'stride': 1, 'count': 1, 'array': [1.0]},
        'vindices': {'stride': 1, 'count': len(pos) * 2, 'array': [c for p in pos for c in (p[3], 0)]},
        'parts': {p: {'stride': 3, 'count': len(a) // 3, 'array': a} for p, a in parts.items()},
    }}
    P.dump(P.ASSETS + 'animmodels/entity/%s.json' % name, out)
    P.os.makedirs(P.ASSETS + 'textures/entity', exist_ok=True)
    shutil.copy(SRC + 'textures/entity/%s.png' % name, P.ASSETS + 'textures/entity/%s.png' % name)
    print(name, len(pos), 'verts', sum(len(a) for a in parts.values()) // 9, 'tris, scale back', round(1 / k, 3))


# ---------------------------------------------------------------- townsfolk (tools/npcgen.py --export)

# the city's leads, rolled in the forge and kept under a name of their own
LEADS = {'adventurer_s_36848002': 'guild_master', 'adventurer_ss_36619001': 'archmage', 'townsfolk_56403004': 'forgemaster'}


def qrot(q, v):
    """v turned by the quaternion q (x, y, z, w)."""
    x, y, z, w = q
    vx, vy, vz = v
    tx, ty, tz = 2 * (y * vz - z * vy), 2 * (z * vx - x * vz), 2 * (x * vy - y * vx)
    return (vx + w * tx + y * tz - z * ty, vy + w * ty + z * tx - x * tz, vz + w * tz + x * ty - y * tx)


def npc_rig(rig):
    """The forge's rigs all share one skeleton but not one build (a child is half an adult's height, its head
    big): each bone is scaled with the whole body down to player size, its pivot set on its biped joint's
    height, and stretched along its length to reach the next joint - so Epic Fight's swings bend it where its
    own joints are. Sideways the body keeps its own width (the biped's turns that matter are fore and aft)."""
    b = {x['name']: x['pivot'] for x in rig['bones']}
    k = AT['Root'] / b['hips'][1]
    ground = rig.get('ground', 0.0)

    def st(top, bot, want):
        return want / max(1e-3, (top - bot) * k)
    out = {
        'hips': ('Root', 'torso', AT['Root'], 1.0),
        'torso': (None, 'torso', AT['Torso'], st(b['head'][1], b['torso'][1], AT['Head'] - AT['Torso'])),
        'head': ('Head', 'head', AT['Head'], 1.0),
        'back': ('Chest', 'torso', 'torso', None),
    }
    for s, side, J_ in (('r', 'right', '_R'), ('l', 'left', '_L')):
        out['arm_' + s] = ('Arm' + J_, side + 'Arm', AT['Arm'], st(b['arm_' + s][1], b['fore_' + s][1], AT['Arm'] - AT['Hand']))
        out['fore_' + s] = ('Hand' + J_, side + 'Arm', AT['Hand'], st(b['fore_' + s][1], b['hand_' + s][1], AT['Hand'] - AT['Tool']))
        out['hand_' + s] = ('Hand' + J_, side + 'Arm', 'fore_' + s, None)
        out['thigh_' + s] = ('Thigh' + J_, side + 'Leg', AT['Thigh'], st(b['thigh_' + s][1], b['shin_' + s][1], AT['Thigh'] - AT['Leg']))
        out['shin_' + s] = ('Leg' + J_, side + 'Leg', AT['Leg'], st(b['shin_' + s][1], ground, AT['Leg']))
        out['foot_' + s] = ('Leg' + J_, side + 'Leg', 'shin_' + s, None)
    return out, k


def export_npc(name):
    SRC = FOLK if P.os.path.exists(FOLK + 'models/entity/%s/rig.json' % name) else globals()['SRC']
    rig = json.load(open(SRC + 'models/entity/%s/rig.json' % name, encoding='utf-8'))
    bones = {b['name']: b for b in rig['bones']}
    plan, k = npc_rig(rig)
    pos, uvs, nrm = [], [], []
    pkey, ukey, nkey = {}, {}, {}
    parts = {p: [] for p in PARTS}

    def index(table, lst, key):
        i = table.get(key)
        if i is None:
            i = table[key] = len(lst)
            lst.append(key)
        return i
    def placing(bone):
        joint, part, land, stretch = plan[bone]
        if isinstance(land, str):                   # riding on another bone: placed exactly as that one is
            joint = joint if joint != 'Chest' else None
            _, _, land_y, stretch = plan[land]
            return joint, part, land_y, stretch, bones[land]['pivot']
        return joint, part, land, stretch, bones[bone]['pivot']

    def place(bone, x, y, z):
        _, _, land_y, stretch, pv = placing(bone)
        return [x * k, land_y + (y - pv[1]) * k * stretch, (z - pv[2]) * k]

    def chain(bone):
        """The forge's rest pose (an arm raised to hold a staff upright) from this bone up: each one's turn about
        its own joint, as placed, so what it holds comes out as it was drawn rather than through the shoulder."""
        out = []
        while bone in plan:
            q = bones[bone].get('rest', [0, 0, 0, 1])
            if abs(q[3]) < 0.99999:
                out.append((q, place(bone, *bones[bone]['pivot'])))
            bone = bones[bone].get('parent')
        return out
    for bone, b in bones.items():
        if bone not in plan or not b.get('mesh', True) or bone == 'drawn':
            continue
        joint, part, land_y, stretch, pv = placing(bone)
        turns = chain(bone)
        path = SRC + 'models/entity/%s/%s.obj' % (name, bone)
        if not P.os.path.exists(path):
            continue
        v, vt, vn, tris = load_obj(path)
        for tri in tris:
            for (vi, ti, ni) in tri:
                mx, my, mz = place(bone, *v[vi])
                nx, ny, nz = vn[ni]
                for q, at in turns:
                    mx, my, mz = [a + c for a, c in zip(qrot(q, (mx - at[0], my - at[1], mz - at[2])), at)]
                    nx, ny, nz = qrot(q, (nx, ny, nz))
                j = joint if joint else ('Torso' if my < AT['Chest'] else 'Chest')
                p = (round(-mx, 5), round(mz, 5), round(my, 5), J[j])
                pi = index(pkey, pos, p)
                u, w = vt[ti]
                ui = index(ukey, uvs, (round(u, 6), round(1 - w, 6)))
                nx, ny, nz = vn[ni]
                ni2 = index(nkey, nrm, (round(-nx, 4), round(nz, 4), round(ny, 4)))
                parts[part] += [pi, ui, ni2]
    for p in PARTS:
        if not parts[p]:
            parts[p] = [0, 0, 0] * 3
    out = {'vertices': {
        'positions': {'stride': 3, 'count': len(pos), 'array': [c for p in pos for c in p[:3]]},
        'uvs': {'stride': 2, 'count': len(uvs), 'array': [c for u in uvs for c in u]},
        'normals': {'stride': 3, 'count': len(nrm), 'array': [c for n in nrm for c in n]},
        'vcounts': {'stride': 1, 'count': len(pos), 'array': [1] * len(pos)},
        'weights': {'stride': 1, 'count': 1, 'array': [1.0]},
        'vindices': {'stride': 1, 'count': len(pos) * 2, 'array': [c for p in pos for c in (p[3], 0)]},
        'parts': {p: {'stride': 3, 'count': len(a) // 3, 'array': a} for p, a in parts.items()},
    }}
    to = LEADS.get(name, name)
    P.dump(P.ASSETS + 'animmodels/entity/npc/%s.json' % to, out)
    P.os.makedirs(P.ASSETS + 'textures/entity/npc', exist_ok=True)
    shutil.copy(SRC + 'textures/entity/%s.png' % name, P.ASSETS + 'textures/entity/npc/%s.png' % to)
    return to, round(1 / k, 4)


def export_npcs():
    """Every NPC the forge (and the hand-made leads) put in the old mod: mesh, texture, conversation, and the
    scale each is drawn back up (or down) at."""
    data = 'E:/Ashbound/src/main/resources/data/ashbound/npc/'
    dst = P.GAME + 'src/main/resources/data/ashbound/npc/'
    P.os.makedirs(dst, exist_ok=True)
    scales = {}
    for f in sorted(P.os.listdir(data)):
        name = f[:-5]
        to, sc = export_npc(name)
        scales[to] = sc
        own = P.os.path.join(P.GAME, 'tools', 'npc_talk', to + '.json')
        conv = json.load(open(own if P.os.path.exists(own) else data + f, encoding='utf-8'))
        if name in LEADS:
            conv['tags'] = ['lead']                  # never picked for a crowd
        P.dump(dst + to + '.json', conv)
    for f in sorted(P.os.listdir(FOLK + '../npc_specs')):          # folkforge.py --roll: the villages' races
        name = f[:-5]
        to, sc = export_npc(name)
        scales[to] = sc
        P.dump(dst + to + '.json', json.load(open(P.os.path.join(P.GAME, 'tools', 'npc_talk', to + '.json'), encoding='utf-8')))
    P.dump(P.ASSETS + 'npc_scales.json', scales)
    print(len(scales), 'NPCs; scales', min(scales.values()), '..', max(scales.values()))


if __name__ == '__main__':
    if sys.argv[1:2] == ['--npc']:
        export_npcs()
        sys.exit()
    for n in sys.argv[1:] or list(RIGS) + list(SPIDERS):
        export_spider(n) if n in SPIDERS else export(n)
