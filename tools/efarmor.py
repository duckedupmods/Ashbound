"""Puts Ashbound's armour sets on Epic Fight's body.

Our sets are chunky meshes, one per vanilla bone (E:/Ashbound/.../models/entity/SET/PIECE_BONE.obj, made by
tools/voxarmor*.py), sized on the vanilla player. Epic Fight draws armour from a skinned mesh of its own
(assets/<ns>/animmodels/armor/<item>.json, looked up by the item's id), in the same player-sized space. So each
piece only needs its vertices weighted to Epic Fight's joints: the body blends Torso into Chest up the spine,
arms bend at the elbow (Arm / Hand), legs and boots at the knee (Thigh / Leg). The set's texture goes where the
armour layer texture lives, so Epic Fight finds it.

Also writes the item models and icons, Epic Fight's armour data (stun armour, weight), the names, and the
generated list in Armors.java (the stats come from the set's class and rank there).

    python tools/efarmor.py [sets...]
    blender -b -P tools/blender/armor_icons.py -- [sets...]; python tools/efarmor.py icons [sets...]
"""
import json
import random
import statistics
import sys

try:
    from PIL import Image
except ImportError:      # Blender's Python, which only wants the tables (tools/blender/armor_preview.py)
    Image = None

import port_weapons as P

SRC = 'E:/Ashbound/src/main/resources/assets/ashbound/'
NEW = P.GAME + 'tools/armor_src/'          # the sets tools/armorforge.py makes


def src(name):
    """where a set's per-bone meshes and atlas are: old Ashbound's, or armorforge's"""
    rig = SRC + 'models/entity/%s/rig.json' % name
    if P.os.path.exists(rig) and 'helm_head' in open(rig, encoding='utf-8').read():
        return SRC
    return NEW            # (an old monster of the same name has a rig there too, with no armour bones)
JAVA = P.GAME + 'src/main/java/com/snoringwalrus/ashbound/Armors.java'

JOINTS = ['Root', 'Thigh_R', 'Leg_R', 'Knee_R', 'Thigh_L', 'Leg_L', 'Knee_L', 'Torso', 'Chest', 'Head', 'Shoulder_R',
          'Arm_R', 'Hand_R', 'Tool_R', 'Elbow_R', 'Shoulder_L', 'Arm_L', 'Hand_L', 'Tool_L', 'Elbow_L']
J = {n: i for i, n in enumerate(JOINTS)}
ELBOW, KNEE = 1.125, 0.37          # where Epic Fight's own armour splits the limbs (blocks above the feet)
SPINE = (0.75, 1.5)                # the body is all Torso below, all Chest above, blended between
# Epic Fight's own player skin blends the spine in these steps (height, share on Chest); armour copies them so it
# twists with the body under it
SPINE_STEPS = [(0.712, 0.0), (0.849, 0.25), (0.987, 0.25), (1.125, 0.5), (1.263, 0.74), (1.401, 0.77), (1.538, 1.0)]
# the arms swing through the space beside the body from x 0.25 out: a body piece wider than SIDE, or an arm piece
# reaching in past SLEEVE, cuts through the other when the arms swing, so the extra bulk there is squeezed in
SIDE, SLEEVE = 0.272, 0.255
HIP, TAILS = 0.72, 0.8             # where coat tails start, and how much of a thigh's swing they take at the hem

# set, dungeon, rank, class, its four pieces (helm, chest, legs, boots)
SETS = []
# every set in the gear table (tools/gear.py): the 8 old ones and the ones tools/armorforge.py makes
for _g in json.load(open(P.GAME + 'src/main/resources/ashbound/gear.json', encoding='utf-8')):
    for _st in _g['sets']:
        SETS.append((_st['id'], _g['gate'], _g['rank'], _st['cls'].upper(), tuple(p['id'][len(_st['id']) + 1:] for p in _st['pieces'])))

# and the world's found sets (tools/worldarmour.py)
_W = P.GAME + 'src/main/resources/ashbound/world_armour.json'
if P.os.path.exists(_W):
    for _st in json.load(open(_W, encoding='utf-8')):
        SETS.append((_st['id'], 'world', _st['rank'], _st['cls'].upper(), tuple(p['id'][len(_st['id']) + 1:] for p in _st['pieces'])))

# a full set's Epic Fight stun armour and weight per class at rank C (Armors.java has the vanilla side)
EF = {'ROBE': (3, 1.5), 'LIGHT': (10, 4), 'MEDIUM': (30, 8), 'HEAVY': (60, 14)}
RANK = {'F': 0.80, 'E': 0.87, 'D': 0.93, 'C': 1.00, 'B': 1.08, 'A': 1.16, 'S': 1.25}
SHARE = (0.15, 0.40, 0.30, 0.15)   # helm, chest, legs, boots


def weights(piece, bone, x, y):
    """the joints (and how much of each) a vertex at height y on this bone follows"""
    side = 'L' if bone.endswith('_l') else 'R'
    if piece == 'helm':
        return [('Head', 1.0)]
    if bone == 'body' and y < HIP:
        # a coat's tails below the hip go with the legs, the further down the more, so a stride parts them
        # instead of the thighs pushing through; the middle seam follows both legs
        t = TAILS * min(1.0, (HIP - y) / 0.3)
        if abs(x) < 0.02:
            return [('Torso', round(1 - t, 2)), ('Thigh_L', round(t / 2, 2)), ('Thigh_R', round(t / 2, 2))]
        return [('Torso', round(1 - t, 2)), ('Thigh_L' if x > 0 else 'Thigh_R', round(t, 2))]
    if bone == 'body':
        t = spine(y)
        return [(j, w) for j, w in (('Torso', round(1 - t, 2)), ('Chest', round(t, 2))) if w > 0]
    if bone.startswith('arm'):
        return [(('Arm_' if y >= ELBOW else 'Hand_') + side, 1.0)]
    if bone.startswith('leg'):
        return [(('Thigh_' if y >= KNEE else 'Leg_') + side, 1.0)]
    return [('Chest', 1.0)]        # extras riding on the body (the Bonewright's cog)


def spine(y):
    """how much of a body vertex at height y follows Chest rather than Torso"""
    if y <= SPINE_STEPS[0][0]:
        return 0.0
    for (y0, w0), (y1, w1) in zip(SPINE_STEPS, SPINE_STEPS[1:]):
        if y <= y1:
            return w0 + (w1 - w0) * (y - y0) / (y1 - y0)
    return 1.0


def squeeze(v, lo, hi, edge):
    """v's distance past `lo` scaled so its furthest reach `edge` lands on `hi` (both sides of the middle)"""
    a = abs(v)
    if edge <= hi or a <= lo:
        return v
    return (lo + (a - lo) * (hi - lo) / (edge - lo)) * (1 if v > 0 else -1)


def fit(bone, v):
    """the piece's vertices pulled clear of where the arms swing (see SIDE and SLEEVE)"""
    if bone == 'body':
        edge = max(abs(x) for x, y, z in v if y > HIP + 0.13) if v else 0
        out = []
        for x, y, z in v:
            k = min(1.0, max(0.0, (y - HIP) / 0.13))   # full above the waist, none on the tails
            out.append((x + (squeeze(x, 0.2, SIDE, edge) - x) * k, y, z))
        return out
    if bone.startswith('arm'):
        sgn = 1 if bone.endswith('_l') else -1
        inner = min(sgn * x for x, y, z in v)
        if inner >= SLEEVE:
            return v
        return [((SLEEVE + (sgn * x - inner) * (0.32 - SLEEVE) / (0.32 - inner)) * sgn if sgn * x < 0.32 else x, y, z) for x, y, z in v]
    return v


# Under each set's chunky pieces sits a lining shaped and weighted like Epic Fight's own armour (and its player
# skin): a closed sleeve round every covered body part, just outside the skin's outer layer, with the extra ring
# at the elbow and knee that their Elbow / Knee joints bend. The chunky pieces leave gaps (a bare upper arm,
# a hard split at the elbow); the lining makes sure no pose shows skin through them.
SWATCHES = P.GAME + 'tools/renders/icons/linings.json'   # where each set's lining cloth sits on its sheet (the icons leave it out)
SW = 16                            # a cloth swatch's size in texels; the sets are painted 16 texels to the block


def ring(z, ws):
    return z, (lambda x, y: ws)


def limb(upper, lower, joint, z0, z1):
    """a limb's rings, bending at Epic Fight's elbow / knee (JOINT at height z) like its own armour does"""
    z = KNEE_EF if upper.startswith('Thigh') else ELBOW
    return [ring(z0, ((lower, 1.0),)), ring(z - 0.001, ((lower, 1.0),)), ring(z, ((joint, 1.0),)),
            ring(z + 0.001, ((upper, 1.0),)), ring(z1, ((upper, 1.0),))]


KNEE_EF = 0.375


def rect(x0, x1, y0, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def lining(piece):
    """[(part, outline, rings, caps)] in Epic Fight's frame (x right, y forward, z up) for a piece's lining"""
    if piece == 'chest':
        torso = [ring(z, tuple((j, w) for j, w in (('Torso', round(1 - c, 2)), ('Chest', c)) if w > 0)) for z, c in SPINE_STEPS]
        out = [('torso', rect(-0.268, 0.268, -0.138, 0.138), torso, 'tb')]
        for s, part in ((1, 'rightArm'), (-1, 'leftArm')):
            S = 'R' if s > 0 else 'L'
            xs = sorted((0.239 * s, 0.512 * s))
            out.append((part, rect(xs[0], xs[1], -0.137, 0.137), limb('Arm_' + S, 'Hand_' + S, 'Elbow_' + S, 0.722, 1.528), 'tb'))
        return out
    if piece == 'legs':
        waist = [ring(z, tuple((j, w) for j, w in (('Torso', round(1 - spine(z), 2)), ('Chest', round(spine(z), 2))) if w > 0)) for z in (0.70, 0.86)]
        out = [('noGroups', rect(-0.262, 0.262, -0.134, 0.134), waist, '')]
        for s in (1, -1):
            S = 'R' if s > 0 else 'L'
            xs = sorted((-0.004 * s, 0.258 * s))
            out.append(('noGroups', rect(xs[0], xs[1], -0.134, 0.134), limb('Thigh_' + S, 'Leg_' + S, 'Knee_' + S, 0.0, 0.772), 'b'))
        return out
    if piece == 'boots':
        out = []
        for s in (1, -1):
            S = 'R' if s > 0 else 'L'
            xs = sorted((-0.006 * s, 0.270 * s))
            out.append(('noGroups', rect(xs[0], xs[1], -0.142, 0.142), limb('Thigh_' + S, 'Leg_' + S, 'Knee_' + S, -0.02, 0.44), 'b'))
        return out
    return []


# a robe's skirt, waist to ankle round both legs: (height, half width, half depth). Below the hip it follows the
# thighs (the left half the left leg, the middle seam both), the further down the more, so a stride opens it
ROBE = [(0.84, 0.292, 0.170), (0.66, 0.305, 0.185), (0.48, 0.318, 0.200), (0.31, 0.332, 0.215), (0.15, 0.345, 0.228)]


def skirt():
    def follow(x, y, z):
        t = round(0.85 * min(1.0, max(0.0, (0.78 - z) / 0.35)), 2)
        if t == 0:
            return (('Torso', 1.0),)
        if abs(x) < 0.01:
            return (('Torso', round(1 - t, 2)), ('Thigh_L', round(t / 2, 3)), ('Thigh_R', round(t / 2, 3)))
        return (('Torso', round(1 - t, 2)), ('Thigh_R' if x > 0 else 'Thigh_L', t))
    rings = []
    for z, hx, hy in reversed(ROBE):
        pts = [(-hx, -hy), (0.0, -hy), (hx, -hy), (hx, hy), (0.0, hy), (-hx, hy)]
        rings.append((z, pts, follow))
    return rings


def tube(part, outline, rings, caps, swatch):
    """triangles [(part, ((pos, uv, normal, weights) x3))] of a closed sleeve through RINGS, OUTLINE going round
    anticlockwise seen from above; each face takes the swatch at 16 texels to the block, its bottom on the
    swatch's bottom row (a robe's hem)"""
    sx, sy = swatch
    if outline is not None:
        rings = [(z, outline, (lambda f: lambda x, y, z: f(x, y))(f)) for z, f in rings]
    zlo = rings[0][0]
    tris = []

    def vert(p, z, u, v, n, f):
        return (round(p[0], 5), round(p[1], 5), round(z, 5)), ((sx + min(u, SW - 0.01)) / 256, (sy + SW - min(v, SW - 0.01)) / 256), n, f(p[0], p[1], z)

    for (za, pa, fa), (zb, pb, fb) in zip(rings, rings[1:]):
        for k in range(len(pa)):
            a0, a1, b0, b1 = pa[k], pa[(k + 1) % len(pa)], pb[k], pb[(k + 1) % len(pb)]
            dx, dy = a1[0] - a0[0], a1[1] - a0[1]
            l = (dx * dx + dy * dy) ** 0.5
            n = (round(dy / l, 4), round(-dx / l, 4), 0.0)
            la, lb = l * SW, ((b1[0] - b0[0]) ** 2 + (b1[1] - b0[1]) ** 2) ** 0.5 * SW
            q = [vert(a0, za, 0, (za - zlo) * SW, n, fa), vert(a1, za, la, (za - zlo) * SW, n, fa),
                 vert(b1, zb, lb, (zb - zlo) * SW, n, fb), vert(b0, zb, 0, (zb - zlo) * SW, n, fb)]
            tris += [(part, (q[0], q[1], q[2])), (part, (q[0], q[2], q[3]))]
    for c, (z, pts, f) in (('b', rings[0]), ('t', rings[-1])):
        if c in caps:
            x0, y0 = min(p[0] for p in pts), min(p[1] for p in pts)
            n = (0.0, 0.0, 1.0 if c == 't' else -1.0)
            vs = [vert(p, z, (p[0] - x0) * SW, (p[1] - y0) * SW, n, f) for p in pts]
            tris += [(part, (vs[0], vs[k], vs[k + 1])) for k in range(1, len(vs) - 1)]
    return tris


# --- the set's texture sheet ---------------------------------------------------------------------------------

def lum(c):
    return 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]


def pale(c):
    return c[3] >= 128 and lum(c) > 130 and (max(c[:3]) - min(c[:3])) < 0.38 * max(c[:3])


def despeckle(im, most=5):
    """the old sheets are flecked with small pale spots (wax, bone dust) that read as white dots on the armour:
    each clump of up to MOST pale texels sitting on darker cloth or plate takes the colour round it; bigger pale
    patches (bone, steel, a mask) stay"""
    W, H = im.size
    src, px = im.copy().load(), im.load()
    seen, n = set(), 0
    for y in range(H):
        for x in range(W):
            if (x, y) in seen or not pale(src[x, y]):
                continue
            clump, todo = [], [(x, y)]
            seen.add((x, y))
            while todo:
                p = todo.pop()
                clump.append(p)
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        q = (p[0] + dx, p[1] + dy)
                        if 0 <= q[0] < W and 0 <= q[1] < H and q not in seen and pale(src[q]):
                            seen.add(q)
                            todo.append(q)
            if len(clump) > most:
                continue
            inside = set(clump)
            ring = [src[p[0] + dx, p[1] + dy] for p in clump for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                    if 0 <= p[0] + dx < W and 0 <= p[1] + dy < H and (p[0] + dx, p[1] + dy) not in inside
                    and src[p[0] + dx, p[1] + dy][3] >= 128]
            if len(ring) < 3 or statistics.median(lum(d) for d in ring) > min(lum(src[p]) for p in clump) - 45:
                continue
            ring.sort(key=lum)
            for p in clump:
                px[p] = ring[len(ring) // 2]
            n += len(clump)
    return n


def free_spots(im, count, size=SW + 6):
    """top-left corners of COUNT empty squares on the sheet, with room round them for the padding"""
    W, H = im.size
    a = im.split()[3].load()
    taken, out = set(), []
    for y in range(H - size, -1, -size):
        for x in range(0, W - size + 1, size):
            if all(a[x + i, y + j] == 0 for i in range(size) for j in range(size)):
                out.append((x + 3, y + 3))
                if len(out) == count:
                    return out
    raise SystemExit('no room on the sheet for the cloth swatches')


def paint(im, at, colour, rng, robe=None):
    """a swatch of cloth: COLOUR with a little weave and mottling; a robe's gets pleats and a trimmed hem"""
    px = im.load()
    for j in range(SW):
        for i in range(SW):
            k = 1 + rng.uniform(-0.05, 0.05) - (0.03 if i % 2 else 0)
            c = colour
            if robe:
                k *= 1 + 0.09 * (1 if i % 5 in (1, 2) else -1 if i % 5 == 4 else 0)
                if j >= SW - 2:
                    c = robe
                elif j == SW - 3:
                    k *= 0.6
            px[at[0] + i, at[1] + j] = tuple(max(0, min(255, int(v * k))) for v in c) + (255,)


def pad(im, used, rounds=2):
    """grows every face's colours out into the empty texels round it, so a texel read right on a seam is never
    see-through (a pinhole at the seam is skin showing); texels inside a face keep any cut-out they have"""
    W, H = im.size
    for _ in range(rounds):
        src, px = im.copy().load(), im.load()
        for y in range(H):
            for x in range(W):
                if src[x, y][3] >= 128 or (x, y) in used:
                    continue
                nb = [src[x + dx, y + dy] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1))
                      if 0 <= x + dx < W and 0 <= y + dy < H and src[x + dx, y + dy][3] >= 128]
                if nb:
                    px[x, y] = tuple(sum(c[i] for c in nb) // len(nb) for i in range(3)) + (255,)


def used_texels(meshes):
    """the texels inside any face's UV box"""
    out = set()
    for m in meshes:
        U = m['vertices']['uvs']['array']
        for p in m['vertices']['parts'].values():
            a = p['array']
            for t in range(0, len(a), 9):
                us = [U[2 * a[t + o + 1]] * 256 for o in (0, 3, 6)]
                vs = [U[2 * a[t + o + 1] + 1] * 256 for o in (0, 3, 6)]
                for x in range(int(min(us) + 0.5), int(max(us) + 0.5)):
                    for y in range(int(min(vs) + 0.5), int(max(vs) + 0.5)):
                        out.add((x, y))
    return out


def colours(im):
    """the set's cloth colour (its median texel, a shade lighter) and its accent (its most coloured texels)"""
    px = [c for c in im.get_flattened_data() if c[3] >= 128]
    px.sort(key=lum)
    base = px[len(px) // 2][:3]
    sat = [c for c in px if max(c[:3]) > 60 and (max(c[:3]) - min(c[:3])) > 0.45 * max(c[:3])]
    if len(sat) > len(px) * 0.02:
        sat.sort(key=lum)
        accent = sat[len(sat) // 2][:3]
    else:
        accent = tuple(min(255, int(v * 1.6) + 20) for v in base)
    return base, accent


PART = {'helm': lambda b: 'head', 'chest': lambda b: {'arm_l': 'leftArm', 'arm_r': 'rightArm'}.get(b, 'torso'),
        'legs': lambda b: 'noGroups', 'boots': lambda b: 'noGroups'}


def mesh(name, piece, files, extra=()):
    """one piece's skinned mesh in Epic Fight's format, from the OBJs of its bones (and EXTRA triangles already
    in Epic Fight's frame: the lining, a robe's skirt)"""
    pos, uvs, nrm, wts, vc, vi = [], [], [], [], [], []
    pkey, ukey, nkey, wkey = {}, {}, {}, {}
    parts = {}

    def index(table, lst, key):
        i = table.get(key)
        if i is None:
            i = table[key] = len(lst)
            lst.append(key)
        return i

    for f in files:
        bone = f[len(piece) + 1:]
        part = PART[piece](bone)
        v, vt, vn, tris = load_obj(src(name) + 'models/entity/%s/%s.obj' % (name, f))
        v = fit(bone, v)
        for tri in tris:
            for (a, t, n) in tri:
                x, y, z = v[a]
                ws = tuple(weights(piece, bone, x, y))
                # our frame (x to the wearer's left, y up, z forward) -> Epic Fight's (x right, y forward, z up)
                key = (round(-x, 5), round(z, 5), round(y, 5), ws)
                k = len(pos)
                pi = index(pkey, pos, key)
                if pi == k:
                    vc.append(len(ws))
                    for j, w in ws:
                        vi += [J[j], index(wkey, wts, w)]
                u, w = vt[t]
                ui = index(ukey, uvs, (round(u, 6), round(1 - w, 6)))
                nx, ny, nz = vn[n]
                ni = index(nkey, nrm, (round(-nx, 4), round(nz, 4), round(ny, 4)))
                parts.setdefault(part, []).extend([pi, ui, ni])
    for part, tri in extra:
        for p, uv, n, ws in tri:
            k = len(pos)
            pi = index(pkey, pos, p + (ws,))
            if pi == k:
                vc.append(len(ws))
                for j, w in ws:
                    vi += [J[j], index(wkey, wts, w)]
            ui = index(ukey, uvs, (round(uv[0], 6), round(uv[1], 6)))
            ni = index(nkey, nrm, n)
            parts.setdefault(part, []).extend([pi, ui, ni])
    return {'vertices': {
        'positions': {'stride': 3, 'count': len(pos), 'array': [c for p in pos for c in p[:3]]},
        'uvs': {'stride': 2, 'count': len(uvs), 'array': [c for u in uvs for c in u]},
        'normals': {'stride': 3, 'count': len(nrm), 'array': [c for n in nrm for c in n]},
        'vcounts': {'stride': 1, 'count': len(vc), 'array': vc},
        'weights': {'stride': 1, 'count': len(wts), 'array': wts},
        'vindices': {'stride': 1, 'count': len(vi), 'array': vi},
        'parts': {p: {'stride': 3, 'count': len(a) // 3, 'array': a} for p, a in parts.items()},
    }}


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


def port(name, rank, cls, items, lang, names):
    bones = [b['name'] for b in json.load(open(src(name) + 'models/entity/%s/rig.json' % name, encoding='utf-8'))['bones']]
    stun, weight = EF[cls]
    sheet = Image.open(src(name) + 'textures/entity/%s.png' % name).convert('RGBA')
    if src(name) == SRC:    # old Ashbound's soft renders left pale flecks; armorforge's sheets are clean
        print('  %d white flecks cleaned' % despeckle(sheet))
    base, accent = colours(sheet)
    rng = random.Random(name)
    cloth, robe = free_spots(sheet, 2)
    swatch = json.load(open(SWATCHES)) if P.os.path.exists(SWATCHES) else {}
    swatch[name] = cloth
    P.dump(SWATCHES, swatch)
    paint(sheet, cloth, tuple(int(v * 0.72) for v in base), rng)
    if cls == 'ROBE':
        paint(sheet, robe, tuple(min(255, int(v * 1.1)) for v in base), rng, robe=accent)
    meshes = []
    for piece, item, share in zip(('helm', 'chest', 'legs', 'boots'), items, SHARE):
        item = name + '_' + item
        files = [b for b in bones if b.startswith(piece + '_')]
        extra = [t for part, outline, rings, caps in lining(piece) for t in tube(part, outline, rings, caps, cloth)]
        if piece == 'chest' and cls == 'ROBE':
            extra += tube('torso', None, skirt(), '', robe)
        out = mesh(name, piece, files, extra)
        meshes.append(out)
        P.dump(P.ASSETS + 'animmodels/armor/%s.json' % item, out)
        P.dump(P.ASSETS + 'models/item/%s.json' % item, {'parent': 'minecraft:item/generated', 'textures': {'layer0': 'ashbound:item/' + item}})
        P.dump(P.DATA + 'capabilities/armors/%s.json' % item, {'attributes': {
            'stun_armor': round(stun * share * RANK[rank], 2), 'weight': round(weight * share * RANK[rank], 2)}})
        lang['item.ashbound.' + item] = names.get('item.ashbound.' + item, lang.get('item.ashbound.' + item, item))
        print('  %-26s %5d verts %5d tris' % (item, out['vertices']['positions']['count'],
                                              sum(p['count'] for p in out['vertices']['parts'].values()) // 3))
    pad(sheet, used_texels(meshes))
    P.os.makedirs(P.ASSETS + 'textures/models/armor', exist_ok=True)
    for layer in (1, 2):
        sheet.save(P.ASSETS + 'textures/models/armor/%s_layer_%d.png' % (name, layer))


def icons(only):
    """the icons tools/blender/armor_icons.py rendered, brought down to pixel art like the game's own items
    (tools/pixicons.py)"""
    import pixicons
    pixicons.run({name + '_' + it for name, _, _, _, items in SETS if not only or name in only for it in items})


def main(only):
    names = json.load(open(SRC + 'lang/en_us.json', encoding='utf-8'))
    lang = json.load(open(P.ASSETS + 'lang/en_us.json', encoding='utf-8'))
    for name, dungeon, rank, cls, items in SETS:
        if not only or name in only:
            print(name, rank, cls)
            port(name, rank, cls, items, lang, names)
    P.dump(P.ASSETS + 'lang/en_us.json', lang)
    # Armors.java registers the sets from gear.json (tools/gear.py), which also names them


if __name__ == '__main__':
    if sys.argv[1:2] == ['icons']:
        icons(sys.argv[2:])
    else:
        main(sys.argv[1:])
