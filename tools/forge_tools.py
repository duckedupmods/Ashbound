"""The forge's own hand tools as item meshes in the weapons' frame (handle up the y axis, centred on 0.5, gripped near
y 0.4): the smith's hammer and the tailor's needle, each a few boxes on a small painted texture.

    python tools/forge_tools.py   -> models/mesh + models/item + textures/item + lang
"""
import json, os
from PIL import Image
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'main', 'resources', 'assets', 'ashbound')
SWATCH = {'iron': (86, 88, 94), 'edge': (150, 152, 158), 'ash': (92, 62, 40), 'grip': (46, 30, 22), 'bone': (214, 202, 176), 'steel': (176, 182, 192), 'red': (150, 52, 34)}
NAMES = list(SWATCH)

def texture(name):
    im = Image.new('RGB', (16 * len(NAMES), 16))
    for i, n in enumerate(NAMES):
        r, g, b = SWATCH[n]
        for x in range(16):
            for y in range(16):
                k = 1 + ((x * 7 + y * 13) % 5 - 2) * 0.025 - (0.08 if x in (0, 15) or y in (0, 15) else 0)
                im.putpixel((16 * i + x, y), tuple(min(255, int(c * k)) for c in (r, g, b)))
    im.save(os.path.join(A, 'textures', 'item', name + '.png'))

def mesh(name, boxes):
    out, n = ['mtllib %s.mtl' % name, '# Ashbound forge tool (tools/forge_tools.py); item space', 'usemtl tool'], 0
    faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    uv = []
    for x0, y0, z0, x1, y1, z1, col in boxes:
        c = [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1), (x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)]
        out += ['v %.5f %.5f %.5f' % p for p in c]
        i = NAMES.index(col); u0, u1 = (i + 0.2) / len(NAMES), (i + 0.8) / len(NAMES)
        uv.append((u0, u1))
    for i, (u0, u1) in enumerate(uv):
        out += ['vt %.4f 0.2' % u0, 'vt %.4f 0.2' % u1, 'vt %.4f 0.8' % u1, 'vt %.4f 0.8' % u0]
    for i in range(len(boxes)):
        for f in faces:
            out.append('f ' + ' '.join('%d/%d' % (8 * i + f[k] + 1, 4 * i + k + 1) for k in range(4)))
    open(os.path.join(A, 'models', 'mesh', name + '.obj'), 'w').write('\n'.join(out) + '\n')
    open(os.path.join(A, 'models', 'mesh', name + '.mtl'), 'w').write('newmtl tool\nmap_Kd ashbound:item/%s\n' % name)
    d = json.load(open(os.path.join(A, 'models', 'item', 'ore_hammer.json')))
    d['base']['model'] = 'ashbound:models/mesh/%s.obj' % name
    json.dump(d, open(os.path.join(A, 'models', 'item', name + '.json'), 'w'), indent=1)
    texture(name)

mesh('smith_hammer', [
    (0.46, -0.10, 0.46, 0.54, 0.86, 0.54, 'ash'),
    (0.445, 0.22, 0.445, 0.555, 0.52, 0.555, 'grip'),
    (0.30, 0.80, 0.39, 0.74, 1.02, 0.61, 'iron'),
    (0.74, 0.83, 0.42, 0.80, 0.99, 0.58, 'edge'),
    (0.22, 0.86, 0.45, 0.30, 0.96, 0.55, 'edge'),
])
mesh('tailor_needle', [
    (0.485, 0.10, 0.485, 0.515, 0.92, 0.515, 'steel'),
    (0.47, 0.82, 0.47, 0.53, 0.86, 0.53, 'edge'),
    (0.455, 0.14, 0.455, 0.545, 0.40, 0.545, 'bone'),
    (0.44, 0.36, 0.44, 0.56, 0.40, 0.56, 'red'),
])
p = os.path.join(A, 'lang', 'en_us.json')
s = json.load(open(p, encoding='utf8'))
s['item.ashbound.smith_hammer'] = "Smith's Hammer"; s['item.ashbound.tailor_needle'] = "Tailor's Needle"
json.dump(s, open(p, 'w', encoding='utf8'), indent=1, ensure_ascii=False)
