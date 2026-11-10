"""The cube townsfolk (tools/mcstyle.py) onto Epic Fight's biped, so its animations move them.

Every NPC shares Epic Fight's one skeleton, whose joints sit where a player's do: hips at 12 px, neck at 24, the
elbow cut at 18, the knee at 6. So each body plan is scaled to land its hips on the biped's (a dwarf's short legs are
stretched a little, its long body left to hang over them), its arms to a player's length, its head kept whole, and
drawn at its own size again in game (npc_scales.json). Limbs are cut at the elbow and knee and each half weighted to
its joint, the body blended from Torso to Chest as Epic Fight's own player mesh is.

    python tools/mcexport.py ID...          preview meshes in tools/renders/mc/ef/ (rendered by blender/mc_ef_look.py)
    python tools/mcexport.py ID... --install    into the mod: animmodels/entity/npc/ID.json + textures/entity/npc/ID.png
"""
import json
import math
import os
import sys

import mcstyle as M
import port_weapons as P

JOINTS = ['Root', 'Thigh_R', 'Leg_R', 'Knee_R', 'Thigh_L', 'Leg_L', 'Knee_L', 'Torso', 'Chest', 'Head', 'Shoulder_R',
          'Arm_R', 'Hand_R', 'Tool_R', 'Elbow_R', 'Shoulder_L', 'Arm_L', 'Hand_L', 'Tool_L', 'Elbow_L']
J = {n: i for i, n in enumerate(JOINTS)}
HIP, NECK, ELBOW, KNEE = 12.0, 24.0, 18.0, 6.0          # Epic Fight's biped, in px
PARTS = ['head', 'torso', 'rightArm', 'leftArm', 'rightLeg', 'leftLeg', 'hat', 'jacket', 'rightSleeve', 'leftSleeve',
         'rightPants', 'leftPants']
PART_OF = {'leg_r': 'rightLeg', 'leg_l': 'leftLeg', 'arm_r': 'rightArm', 'arm_l': 'leftArm', 'cane': 'rightArm', 'hand_r': 'rightArm',
           'hand_l': 'leftArm', 'shoulder_r': 'rightArm', 'shoulder_l': 'leftArm', 'body': 'torso', 'hips': 'torso', 'back': 'torso',
           'hip': 'torso', 'head': 'head'}
PREVIEW = M.OUT / 'ef'


class Fit:
    """where a body plan's px land on the biped"""
    def __init__(self, f):
        bw, bh, bd = f.plan['body']
        lw, lh, ld = f.plan['leg']
        aw, ah, ad = f.plan['arm']
        kl, kb = HIP / lh, (NECK - HIP) / bh
        self.k = k = kl if kl / kb < 1.3 else math.sqrt(kl * kb)      # a dwarf: halfway between its legs and body
        self.sl = kl / k                                               # legs reach the hips
        self.sb = max(1.0, (NECK - HIP) / (bh * k))                    # a short body stretched to the neck, a long one hangs
        self.sa = (NECK - HIP) / (ah * k)                              # arms a player's length, so hands hold where its hands are
        self.lh, self.hy = lh, lh + bh
        if f.slim and f.race != 'dwarf':
            aw = min(aw, 3)
        self.arm_x = (bw / 2 + aw / 2) * k
        pose = f.s.get('pose') or {}
        self.turns = {s: TURNS.get(pose.get(s)) for s in ('r', 'l')}

    def turn(self, side, p):
        """a forearm's set pose (holding something up, hands clasped or folded), about its elbow"""
        t = self.turns.get(side)
        if not t:
            return p
        pitch, yaw, lift = t
        ex = (-1 if side == 'r' else 1) * self.arm_x
        x, y, z = p[0] - ex, p[1] - ELBOW, p[2]
        a = math.radians(pitch)
        y, z = y * math.cos(a) - z * math.sin(a), y * math.sin(a) + z * math.cos(a)
        b = math.radians(yaw if side == 'r' else -yaw)
        x, z = x * math.cos(b) + z * math.sin(b), -x * math.sin(b) + z * math.cos(b)
        return x + ex, y + ELBOW + (lift if side == 'r' else 0), z

    def place(self, kind, p):
        x, y, z = p
        k = self.k
        if kind in ('leg', 'cane'):
            yf = y * k * self.sl
        elif kind in ('body', 'hips'):
            yf = NECK - (self.hy - y) * k * self.sb
        elif kind == 'arm':
            yf = NECK - (self.hy - y) * k * self.sa
        else:
            yf = NECK + (y - self.hy) * k
        return x * k, yf, z * k

    def cuts(self, bone):
        """the cut through a limb in its own (unturned) px, and the joints above and below it"""
        s = bone[-1].upper()
        if bone.startswith('leg'):
            return KNEE / (self.k * self.sl), 'Thigh_' + s, 'Leg_' + s
        if bone.startswith('arm'):
            return self.hy - (NECK - ELBOW) / (self.k * self.sa), 'Arm_' + s, 'Hand_' + s
        return None


# forearm poses: (degrees forward, degrees inward, px the right one rides higher so folded arms don't meet)
TURNS = {'hold': (-40, 0, 0), 'clasp': (-70, 42, 0), 'fold': (-88, 58, 1.2)}
# rigid things: bone -> (how their anchor moves, the joint they ride)
RIGID = {'hand_r': ('arm', 'Hand_R'), 'hand_l': ('arm', 'Hand_L'), 'shoulder_r': ('arm', 'Arm_R'), 'shoulder_l': ('arm', 'Arm_L'),
         'back': ('body', 'Chest'), 'hip': ('body', 'Torso')}


def stooped(b, p):
    st = getattr(b, 'stoop', None)
    if not st:
        return p
    (px_, py, pz), deg = st
    a = math.radians(deg)
    y, z = p[1] - py, p[2] - pz
    return [p[0], y * math.cos(a) - z * math.sin(a) + py, y * math.sin(a) + z * math.cos(a) + pz]


def chest(yf):
    """how much of the body at this height moves with the chest rather than the waist"""
    return max(0.0, min(1.0, (yf - 13.0) / 9.0))


SIDES = ('right', 'front', 'left', 'back')


def pieces(b, cut):
    """the box's faces, cut across at local y = cut (each half closed with a cap): (half, face, corners, uv)"""
    x0, y0, z0 = (b.lo[i] - b.inflate for i in range(3))
    x1, y1, z1 = (b.lo[i] + b.size[i] + b.inflate for i in range(3))
    reg = b.regions()
    ys = [y0, y1] if cut is None or not (y0 + 0.01 < cut < y1 - 0.01) else [y0, cut, y1]
    out = []

    def corners(face, ya, yb):
        return {"front": [(x0, yb, z1), (x1, yb, z1), (x1, ya, z1), (x0, ya, z1)],
                "right": [(x0, yb, z0), (x0, yb, z1), (x0, ya, z1), (x0, ya, z0)],
                "left": [(x1, yb, z1), (x1, yb, z0), (x1, ya, z0), (x1, ya, z1)],
                "back": [(x1, yb, z0), (x0, yb, z0), (x0, ya, z0), (x1, ya, z0)],
                "top": [(x0, yb, z0), (x1, yb, z0), (x1, yb, z1), (x0, yb, z1)],
                "bottom": [(x0, ya, z1), (x1, ya, z1), (x1, ya, z0), (x0, ya, z0)]}[face]

    def vt(v, fh, y):
        return v + (y1 - y) / (y1 - y0) * fh
    for n in range(len(ys) - 1):
        ya, yb = ys[n], ys[n + 1]
        half = 'upper' if n == len(ys) - 2 and len(ys) == 3 else 'lower' if len(ys) == 3 else 'whole'
        for f in SIDES + ('top', 'bottom'):
            u, v, fw, fh = reg[f]
            if fw == 0 or fh == 0:
                continue
            if f == 'top' and n != len(ys) - 2 or f == 'bottom' and n != 0:
                # a cap where the limb is cut: the colour of the front at that height
                fu, fv, ffw, ffh = reg['front']
                y = yb if f == 'top' else ya
                tv = min(fv + ffh - 0.5, max(fv + 0.5, math.floor(vt(fv, ffh, y)) + 0.5))
                tu = fu + ffw / 2
                uv = [(tu, tv)] * 4
            elif f in SIDES:
                ta, tb = vt(v, fh, yb), vt(v, fh, ya)
                uv = [(u, ta), (u + fw, ta), (u + fw, tb), (u, tb)]
            else:
                uv = [(u, v), (u + fw, v), (u + fw, v + fh), (u, v + fh)]
            if b.mirror:
                uv = [uv[1], uv[0], uv[3], uv[2]]
            mid = ((x0 + x1) / 2, (ya + yb) / 2, (z0 + z1) / 2)
            out.append((half, f, corners(f, ya, yb), uv, mid))
    return out


def mesh(f, name):
    """(Epic Fight mesh json, texture, the scale it's drawn back at)"""
    m, img, _ = f.model(name)
    W, H = img.size
    fit = Fit(f)
    pos, uvs, nrm, wts = [], [], [], [1.0]
    pkey, ukey, nkey, wkey = {}, {}, {}, {1.0: 0}
    parts = {p: [] for p in PARTS}

    def index(table, lst, key):
        i = table.get(key)
        if i is None:
            i = table[key] = len(lst)
            lst.append(key)
        return i

    def weight(w):
        w = round(w, 3)
        if w not in wkey:
            wkey[w] = len(wts)
            wts.append(w)
        return wkey[w]
    for b in m.boxes:
        bone = getattr(b, 'bone', 'head')
        kind = bone.split('_')[0]
        rigid = RIGID.get(bone)
        c = None if rigid else fit.cuts(bone)
        side = bone[-1] if bone in ('hand_r', 'hand_l') or bone.startswith('arm_') else None
        if rigid:
            a0 = stooped(b, b.anchor)
            af = fit.place(rigid[0], a0)
            if side:                      # carried along by the forearm's pose, but not turned with it (a staff stays upright)
                af = fit.turn(side, af)

            def where(p):
                w = b.world(p)
                return [af[i] + (w[i] - a0[i]) * fit.k for i in range(3)]
        for half, face, cs, uv, mid in pieces(b, c[0] if c else None):
            if rigid:
                ps, ctr = [where(p) for p in cs], where(mid)
            else:
                ps = [fit.place(kind, b.world(p)) for p in cs]
                ctr = fit.place(kind, b.world(mid))
                if side and half == 'lower':
                    ps, ctr = [fit.turn(side, p) for p in ps], fit.turn(side, ctr)
            e1 = [ps[1][i] - ps[0][i] for i in range(3)]
            e2 = [ps[2][i] - ps[0][i] for i in range(3)]
            n = [e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0]]
            ln = math.sqrt(sum(a * a for a in n)) or 1.0
            n = [a / ln for a in n]
            cen = [sum(p[i] for p in ps) / 4 for i in range(3)]
            if sum(n[i] * (cen[i] - ctr[i]) for i in range(3)) < 0:
                ps, uv, n = ps[::-1], uv[::-1], [-a for a in n]
            ids = []
            for p, (u, v) in zip(ps, uv):
                if rigid:
                    js = ((J[rigid[1]], 1.0),)
                elif kind == 'body':
                    t = chest(p[1])
                    js = ((J['Torso'], 1 - t), (J['Chest'], t)) if 0 < t < 1 else (((J['Chest'] if t >= 1 else J['Torso']), 1.0),)
                elif kind == 'hips':
                    js = ((J['Root'], 1.0),)
                elif kind == 'cane':
                    js = ((J['Hand_R'], 1.0),)
                elif c:
                    js = ((J[c[1] if half == 'upper' else c[2]], 1.0),)
                else:
                    js = ((J['Head'], 1.0),)
                key = (round(-p[0] / 16, 5), round(p[2] / 16, 5), round(p[1] / 16, 5), tuple((j, weight(w)) for j, w in js))
                pi = index(pkey, pos, key)
                ui = index(ukey, uvs, (round(u / W, 6), round(v / H, 6)))
                ni = index(nkey, nrm, (round(-n[0], 4), round(n[2], 4), round(n[1], 4)))
                ids.append((pi, ui, ni))
            for tri in ((0, 1, 2), (0, 2, 3)):
                for t in tri:
                    parts[PART_OF.get(bone, 'head')] += list(ids[t])
    for p in PARTS:
        if not parts[p]:
            parts[p] = [0, 0, 0] * 3
    vi = [a for p in pos for jw in p[3] for a in jw]
    out = {'vertices': {
        'positions': {'stride': 3, 'count': len(pos), 'array': [c for p in pos for c in p[:3]]},
        'uvs': {'stride': 2, 'count': len(uvs), 'array': [c for u in uvs for c in u]},
        'normals': {'stride': 3, 'count': len(nrm), 'array': [c for n in nrm for c in n]},
        'vcounts': {'stride': 1, 'count': len(pos), 'array': [len(p[3]) for p in pos]},
        'weights': {'stride': 1, 'count': len(wts), 'array': wts},
        'vindices': {'stride': 1, 'count': len(vi), 'array': vi},
        'parts': {p: {'stride': 3, 'count': len(a) // 3, 'array': a} for p, a in parts.items()},
    }}
    return out, img, round(1 / fit.k, 4)


def export(id_, f, install=False):
    out, img, sc = mesh(f, id_)
    if install:
        P.dump(P.ASSETS + 'animmodels/entity/npc/%s.json' % id_, out)
        os.makedirs(P.ASSETS + 'textures/entity/npc', exist_ok=True)
        img.save(P.ASSETS + 'textures/entity/npc/%s.png' % id_)
    else:
        PREVIEW.mkdir(parents=True, exist_ok=True)
        json.dump(out, open(PREVIEW / (id_ + '.json'), 'w'))
        img.save(PREVIEW / (id_ + '.png'))
    n = out['vertices']
    print(id_, n['positions']['count'], 'verts', sum(len(p['array']) for p in n['parts'].values()) // 9, 'tris, scale', sc)
    return sc


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    install = '--install' in sys.argv
    cast = dict(M.sample()) if not args or args == ['sample'] else {a: M.folk(a) for a in args}
    scales = {nm: export(nm, f, install) for nm, f in cast.items()}
    json.dump(scales, open((PREVIEW if not install else M.OUT) / 'scales.json', 'w'), indent=1)
