"""The Kiln line's shield and bow, in the chunky style of tools/voxkiln_weapons.py (Ashbound's tools):

    kiln_bulwark   shield: a heavy kite of slag iron, banded rim, soot-black rivets, a furnace grate in the
                   middle that glows through its bars, the Kiln's anvil stamped under it
    kiln_longbow   bow: recurve limbs of blackened iron with ember cracks, a chain-wrapped grip; drawn in
                   three stages, an iron-headed arrow on the string

Built where vanilla builds its own, so its hand poses (and Epic Fight's guard and aim) fit: the shield in the
shield model's space (handle at the origin, the face toward +z), the bow lying in the 16x16 item sprite's plane.
Writes the meshes, their textures and icons, item models, Epic Fight data and names into this add-on.

    python tools/voxkiln_gear.py
"""
import json
import math
import sys

sys.path.insert(0, 'E:/Ashbound/tools')
from PIL import Image  # noqa: E402

import voxsword as V  # noqa: E402
import voxkiln_weapons as K  # noqa: E402
from voxsword import Sword, C, ramp, shade, rot  # noqa: E402

import port_weapons as P  # noqa: E402

CORD = ramp("#2a2420", "#4a3f36", "#6e6052", "#9a8a78")
SHAFT = ramp("#1d140c", "#2e2015", "#43301f", "#5a422b")


def shaders():
    sh = K.shaders()
    sh["cord"] = V.wrap_shader(CORD)
    sh["shaft"] = V.wrap_shader(SHAFT)
    return sh


def seg(s, a, b, w, d, mat, z, group="lit", tag=None):
    """A box from point a to point b (x/y px), w wide, d deep, centred on z."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    ln = math.hypot(dx, dy)
    ang = math.degrees(math.atan2(-dx, dy))
    s.add(((a[0] - w / 2, a[1], z - d / 2), (w, ln + 0.05, d)), mat, rots=(("z", ang),), pivot=(a[0], a[1], z), group=group, tag=tag)


# ================================================================== the shield (vanilla shield space, px)

def kiln_bulwark():
    s = Sword("kiln_bulwark")
    F = 2.0   # the face of the plate
    # the kite: square shoulders, tapering to a point under the grate
    rows = [(9.0, 11.0, 13.0), (7.0, 9.0, 13.0), (5.0, 7.0, 13.0), (3.0, 5.0, 12.6), (1.0, 3.0, 12.2), (-1.0, 1.0, 11.6),
            (-3.0, -1.0, 10.6), (-5.0, -3.0, 9.2), (-7.0, -5.0, 7.4), (-9.0, -7.0, 5.2), (-11.0, -9.0, 2.8)]
    for (y0, y1, w) in rows:
        s.add(((-w / 2, y0, 1.0), (w, y1 - y0 + 0.02, F - 1.0 + 0.2)), "black", tag="plate")
        # the banded rim down both edges
        for side in (1, -1):
            s.add(((side * w / 2 - (1.2 if side > 0 else 0), y0, 0.7), (1.2, y1 - y0 + 0.02, 2.0)), "iron", tag="rim")
    s.add(((-6.7, 10.4, 0.7), (13.4, 1.2, 2.0)), "iron", tag="rim")
    s.add(((-0.8, -11.6, 0.7), (1.6, 1.4, 2.0)), "iron", tag="tip")
    # soot-black rivets round the rim
    for (y0, y1, w) in rows[::2]:
        for side in (1, -1):
            s.add(((side * (w / 2 - 0.6) - 0.45, (y0 + y1) / 2 - 0.45, 2.6), (0.9, 0.9, 0.5)), "black", tag="rivet")
    for x in (-4.0, 0.0, 4.0):
        s.add(((x - 0.45, 10.55, 2.6), (0.9, 0.9, 0.5)), "black", tag="rivet")
    # the furnace grate: an iron frame, fire behind three bars
    s.add(((-3.6, -0.2, F + 0.15), (7.2, 7.4, 0.9)), "iron", tag="grate_frame")
    s.add(((-2.6, 0.8, F + 0.2), (5.2, 5.4, 0.9)), "hot", group="fire", tag="fire")
    s.add(((-1.4, 2.0, F + 0.25), (2.8, 2.8, 0.9)), "white", group="fire", tag="fire_core")
    for x in (-1.8, 0.0, 1.8):
        s.add(((x - 0.4, 0.4, F + 0.9), (0.8, 6.6, 0.6)), "iron", tag="bar")
    s.add(((-3.0, 6.6, F + 0.9), (6.0, 0.7, 0.6)), "iron", tag="bar")
    s.add(((-3.0, -0.1, F + 0.9), (6.0, 0.7, 0.6)), "iron", tag="bar")
    # the Kiln's anvil stamped under it
    a, y = 3.2, -5.6
    s.add(((-a * 0.45, y + a * 0.62, F + 0.15), (a * 1.1, a * 0.28, 0.5)), "iron", tag="anvil")
    s.add(((-a * 0.8, y + a * 0.68, F + 0.15), (a * 0.3, a * 0.16, 0.45)), "iron", tag="anvil")
    s.add(((-a * 0.08, y + a * 0.3, F + 0.15), (a * 0.36, a * 0.34, 0.45)), "iron", tag="anvil")
    s.add(((-a * 0.28, y, F + 0.15), (a * 0.76, a * 0.3, 0.5)), "iron", tag="anvil")
    # a crack of heat down from the grate
    s.add(((-0.3, -4.4, F + 0.05), (0.6, 4.0, 0.3)), "hot", group="fire", tag="crack")
    # the handle behind (where vanilla's is), leather-wrapped
    s.add(((-1.0, -3.0, -5.0), (2.0, 6.0, 1.2)), "wrap", tag="handle")
    for y0 in (-3.0, 2.0):
        s.add(((-1.0, y0, -5.0), (2.0, 1.0, 6.0)), "iron", tag="handle_arm")
    s.shaders = shaders()
    return s


# ================================================================== the bow (item sprite space, px)

O = (8.0, 8.0)                       # the middle of the line between the tips
U = (0.651, 0.759)                   # along the bow, tip to tip
A = (-0.759, 0.651)                  # forward, toward where the arrow flies
L, BULGE, Z = 9.0, 3.4, 8.0


def at(s, pull):
    """A point on the limbs at s = -1..1 (0 the grip); drawn, the limbs bend back and in."""
    k = pull
    bend = BULGE * (1 - s * s) + 0.35 * k * abs(s)
    curl = 1.4 * max(0.0, abs(s) - 0.82) / 0.18          # the recurve: the tips flip forward again
    along = s * L * (1 - 0.05 * k)
    back = 0.9 * k * s * s
    fwd = bend + curl - back
    return (O[0] + U[0] * along + A[0] * fwd, O[1] + U[1] * along + A[1] * fwd)


def kiln_longbow(pull=0.0, arrow=False, name="kiln_longbow"):
    s = Sword(name)
    n = 12
    for i in range(n):
        s0, s1 = -1 + 2 * i / n, -1 + 2 * (i + 1) / n
        p0, p1 = at(s0, pull), at(s1, pull)
        t = abs((s0 + s1) / 2)
        w = 1.9 - 0.9 * t
        seg(s, p0, p1, w, 1.5, "black", Z, tag="limb")
        # ember cracks along the limbs' backs, every other piece
        if i % 2 and 0.15 < t < 0.85:
            q0 = (p0[0] - A[0] * w * 0.3, p0[1] - A[1] * w * 0.3)
            q1 = (p1[0] - A[0] * w * 0.3, p1[1] - A[1] * w * 0.3)
            seg(s, q0, q1, 0.45, 1.56, "hot", Z, group="fire", tag="ember")
    # the grip, chain-wrapped
    g0, g1 = at(-0.16, pull), at(0.16, pull)
    seg(s, g0, g1, 2.4, 2.0, "wrap", Z, tag="grip")
    for t in (-0.12, 0.0, 0.12):
        c = at(t, pull)
        seg(s, (c[0] - U[0] * 0.3, c[1] - U[1] * 0.3), (c[0] + U[0] * 0.3, c[1] + U[1] * 0.3), 2.8, 2.3, "iron", Z, tag="chain")
    # the string, tip to tip through the nock, drawn back with the pull
    t0, t1 = at(-1, pull), at(1, pull)
    mid = ((t0[0] + t1[0]) / 2, (t0[1] + t1[1]) / 2)
    nock = (mid[0] - A[0] * 4.2 * pull, mid[1] - A[1] * 4.2 * pull)
    seg(s, t0, nock, 0.35, 0.35, "cord", Z, tag="string")
    seg(s, nock, t1, 0.35, 0.35, "cord", Z, tag="string")
    if arrow:
        head = (nock[0] + A[0] * 14.0, nock[1] + A[1] * 14.0)
        seg(s, nock, head, 0.5, 0.5, "shaft", Z + 0.6, tag="arrow")
        tip = (head[0] + A[0] * 2.2, head[1] + A[1] * 2.2)
        seg(s, head, tip, 1.3, 0.6, "iron", Z + 0.6, tag="arrowhead")
        seg(s, nock, (nock[0] + A[0] * 2.4, nock[1] + A[1] * 2.4), 1.2, 0.3, "hot", Z + 0.6, group="fire", tag="fletch")
    s.shaders = shaders()
    return s


# ================================================================== writing it out

BLENDER = 'E:/Steam/steamapps/common/Blender/blender.exe'


def icon(mesh, yaw, pitch, fixed=False, offset=(0.0, 0.0)):
    """The menu icon, the way Ashbound's weapon icons are made (tools/vox_icon.py): a Blender render of
    the model, shrunk to 64 px with hard alpha."""
    import shutil
    import subprocess
    vox = 'E:/Ashbound/tools/renders/vox/'
    out = []
    for l in open(P.ASSETS + 'models/mesh/%s.obj' % mesh, encoding='utf-8'):
        if l.startswith('v '):
            x, y, z = map(float, l.split()[1:])
            l = 'v %.5f %.5f %.5f\n' % (x + offset[0], y, z + offset[1])
        out.append(l)
    open(vox + 'icon_%s_f0.obj' % mesh, 'w', encoding='utf-8').write(''.join(out))
    shutil.copy(P.ASSETS + 'textures/item/%s_3d.png' % mesh, vox + 'icon_%s_f0.png' % mesh)
    big = vox + 'icon_%s_big.png' % mesh
    subprocess.run([BLENDER, '-b', '-P', P.GAME + 'tools/blender_icon.py', '--', 'icon_' + mesh, str(yaw), str(pitch), big]
                   + (['fixed'] if fixed else []), check=True, capture_output=True)
    sm = Image.open(big).convert('RGBA').resize((64, 64), Image.LANCZOS)
    px = sm.load()
    for y in range(64):
        for x in range(64):
            r, g, b, a = px[x, y]
            if a < 110:
                px[x, y] = (0, 0, 0, 0)
            else:
                k = 255 / a
                px[x, y] = (min(255, int(r * k)), min(255, int(g * k)), min(255, int(b * k)), 255)
    sm.save(P.ASSETS + 'textures/item/%s.png' % mesh)


def export(s, mesh_name, to_item):
    img, tris = s.build()
    img.save(P.ASSETS + 'textures/item/%s_3d.png' % mesh_name)
    V.to_item = to_item
    path = P.ASSETS + 'models/mesh/%s.obj' % mesh_name
    V.write_obj(V.Path(path), tris)
    P.material(mesh_name, path)
    return sum(len(t) for t in tris.values())


def model(name, mesh, display, icon_name, overrides=None):
    icon_model = {'parent': 'minecraft:item/generated', 'textures': {'layer0': 'ashbound:item/' + icon_name}}
    m = {'loader': 'neoforge:separate_transforms', 'gui_light': 'front',
         'base': {'loader': 'neoforge:obj', 'model': 'ashbound:models/mesh/%s.obj' % mesh, 'flip_v': True, 'display': display},
         'perspectives': {k: icon_model for k in ('gui', 'ground', 'fixed')}}
    if overrides:
        m['overrides'] = overrides
    P.dump(P.ASSETS + 'models/item/%s.json' % name, m)


VAN = 'run/van/assets/minecraft/models/item/'


def held(f):
    """Vanilla's hand poses for its own shield or bow."""
    d = json.load(open(VAN + f))['display']
    return {k: v for k, v in d.items() if k.startswith(('thirdperson', 'firstperson'))}


SHIELD_HELD, SHIELD_BLOCK, BOW_HELD = held('shield.json'), held('shield_blocking.json'), held('bow.json')


def main():
    lang = json.load(open(P.ASSETS + 'lang/en_us.json', encoding='utf-8'))
    # the shield: vanilla shield model space, in blocks
    s = kiln_bulwark()
    print('kiln_bulwark tris', export(s, 'kiln_bulwark', lambda p: (p[0] / 16, p[1] / 16, p[2] / 16)))
    icon('kiln_bulwark', 18, 10, offset=(0.5, 0.5))
    model('kiln_bulwark', 'kiln_bulwark', SHIELD_HELD, 'kiln_bulwark',
          [{'predicate': {'minecraft:blocking': 1}, 'model': 'ashbound:item/kiln_bulwark_blocking'}])
    model('kiln_bulwark_blocking', 'kiln_bulwark', SHIELD_BLOCK, 'kiln_bulwark')
    P.dump(P.DATA + 'capabilities/weapons/kiln_bulwark.json', {'type': 'epicfight:shield'})
    lang['item.ashbound.kiln_bulwark'] = 'Kiln Bulwark'
    # the bow: the item sprite's plane, in blocks
    sprite = lambda p: (p[0] / 16, p[1] / 16, p[2] / 16)  # noqa: E731
    b = kiln_longbow()
    print('kiln_longbow tris', export(b, 'kiln_longbow', sprite))
    icon('kiln_longbow', 0, 0, fixed=True)
    stages = [(0.35, None), (0.7, 0.65), (1.0, 0.9)]
    overrides = []
    for k, (pull, at_pull) in enumerate(stages):
        nm = 'kiln_longbow_pulling_%d' % k
        bb = kiln_longbow(pull, arrow=True, name=nm)
        export(bb, nm, sprite)
        icon(nm, 0, 0, fixed=True)
        model(nm, nm, BOW_HELD, nm)
        pred = {'minecraft:pulling': 1}
        if at_pull:
            pred['minecraft:pull'] = at_pull
        overrides.append({'predicate': pred, 'model': 'ashbound:item/' + nm})
    model('kiln_longbow', 'kiln_longbow', BOW_HELD, 'kiln_longbow', overrides)
    P.dump(P.DATA + 'capabilities/weapons/kiln_longbow.json', {'type': 'epicfight:bow'})
    lang['item.ashbound.kiln_longbow'] = 'Kiln Longbow'
    P.dump(P.ASSETS + 'lang/en_us.json', lang)


if __name__ == '__main__':
    main()
