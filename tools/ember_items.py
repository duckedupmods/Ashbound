"""The Ember Shard and the First Ember as item meshes in the weapons' frame (centred on 0.5, y up): a splinter of burning
crystal, and the whole Ember held in iron ribs. Faceted solids on a small painted texture.

    python tools/ember_items.py   -> models/mesh + models/item + textures/item + lang
"""
import json, math, os
from PIL import Image
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'main', 'resources', 'assets', 'ashbound')
SWATCH = {'core': (255, 214, 120), 'hot': (250, 140, 48), 'deep': (176, 58, 24), 'iron': (70, 66, 66), 'edge': (130, 124, 120)}
NAMES = list(SWATCH)

def texture(name):
    im = Image.new('RGB', (16 * len(NAMES), 16))
    for i, n in enumerate(NAMES):
        r, g, b = SWATCH[n]
        for x in range(16):
            for y in range(16):
                k = 1 + ((x * 7 + y * 13) % 5 - 2) * 0.03
                im.putpixel((16 * i + x, y), tuple(min(255, int(c * k)) for c in (r, g, b)))
    im.save(os.path.join(A, 'textures', 'item', name + '.png'))

class Mesh:
    def __init__(self):
        self.v, self.f = [], []
    def add(self, verts, faces, col):
        n = len(self.v)
        self.v += verts
        i = NAMES.index(col)
        self.f += [([n + k + 1 for k in f], i) for f in faces]
    def write(self, name):
        out = ['mtllib %s.mtl' % name, '# Ashbound ember item (tools/ember_items.py); item space', 'usemtl tool']
        out += ['v %.5f %.5f %.5f' % p for p in self.v]
        for i in range(len(NAMES)):
            out.append('vt %.4f 0.5' % ((i + 0.5) / len(NAMES)))
        for f, i in self.f:
            out.append('f ' + ' '.join('%d/%d' % (k, i + 1) for k in f))
        open(os.path.join(A, 'models', 'mesh', name + '.obj'), 'w').write('\n'.join(out) + '\n')
        open(os.path.join(A, 'models', 'mesh', name + '.mtl'), 'w').write('newmtl tool\nmap_Kd ashbound:item/%s\n' % name)
        d = json.load(open(os.path.join(A, 'models', 'item', 'ore_hammer.json')))
        d['base']['model'] = 'ashbound:models/mesh/%s.obj' % name
        json.dump(d, open(os.path.join(A, 'models', 'item', name + '.json'), 'w'), indent=1)
        texture(name)

def spindle(m, c, h0, h1, r, col, sides=6, twist=0.0, lean=(0, 0)):
    """A long crystal: a point at each end, widest part of the way along."""
    cx, cy, cz = c
    ring = [(cx + lean[0] + r * math.cos(twist + 2 * math.pi * i / sides), cy, cz + lean[1] + r * math.sin(twist + 2 * math.pi * i / sides)) for i in range(sides)]
    v = ring + [(cx + lean[0] * 2.4, cy + h1, cz + lean[1] * 2.4), (cx, cy - h0, cz)]
    f = []
    for i in range(sides):
        j = (i + 1) % sides
        f.append((j, i, sides))
        f.append((i, j, sides + 1))
    m.add(v, f, col)

def ball(m, c, r, col, n=8, k=6):
    v, f = [], []
    for a in range(1, k):
        for b in range(n):
            th, ph = math.pi * a / k, 2 * math.pi * b / n
            v.append((c[0] + r * math.sin(th) * math.cos(ph), c[1] + r * math.cos(th), c[2] + r * math.sin(th) * math.sin(ph)))
    v += [(c[0], c[1] + r, c[2]), (c[0], c[1] - r, c[2])]
    top, bot = len(v) - 2, len(v) - 1
    for b in range(n):
        d = (b + 1) % n
        f.append((top, d, b))
        f.append((bot, (k - 2) * n + b, (k - 2) * n + d))
        for a in range(k - 2):
            f.append((a * n + b, a * n + d, (a + 1) * n + d, (a + 1) * n + b))
    m.add(v, f, col)

def rib(m, c, r, col, tilt, n=16, w=0.022):
    """An iron hoop round c, tilted about the y axis."""
    v, f = [], []
    ca, sa = math.cos(tilt), math.sin(tilt)
    for i in range(n):
        th = 2 * math.pi * i / n
        x, y = r * math.cos(th), r * math.sin(th)
        for q, (dr, dz) in enumerate(((w, w), (-w, w), (-w, -w), (w, -w))):
            px, py, pz = (r + dr) * math.cos(th), (r + dr) * math.sin(th), dz
            v.append((c[0] + px * ca - pz * sa, c[1] + py, c[2] + px * sa + pz * ca))
    for i in range(n):
        j = (i + 1) % n
        for q in range(4):
            p = (q + 1) % 4
            f.append((i * 4 + q, i * 4 + p, j * 4 + p, j * 4 + q))
    m.add(v, f, col)

s = Mesh()
spindle(s, (0.5, 0.45, 0.5), 0.3, 0.62, 0.15, 'hot', 6, 0.3, (0.04, 0))
spindle(s, (0.56, 0.42, 0.56), 0.16, 0.3, 0.07, 'core', 5, 1.0, (0.05, 0.03))
spindle(s, (0.42, 0.4, 0.46), 0.14, 0.22, 0.06, 'deep', 5, 0.2, (-0.04, 0))
s.write('ember_shard')

e = Mesh()
ball(e, (0.5, 0.5, 0.5), 0.23, 'core')
for k in range(3):
    rib(e, (0.5, 0.5, 0.5), 0.33, 'iron', k * math.pi / 3)
spindle(e, (0.5, 0.84, 0.5), 0.03, 0.12, 0.045, 'edge', 4)
spindle(e, (0.5, 0.16, 0.5), 0.12, 0.03, 0.045, 'edge', 4)
e.write('first_ember')

b = Mesh()
spindle(b, (0.5, 0.42, 0.5), 0.34, 0.1, 0.05, 'iron', 6)
spindle(b, (0.5, 0.56, 0.5), 0.05, 0.3, 0.13, 'iron', 4)
rib(b, (0.5, 0.72, 0.5), 0.13, 'edge', 0.0)
ball(b, (0.5, 0.72, 0.5), 0.07, 'hot')
b.write('founders_brand')

p = os.path.join(A, 'lang', 'en_us.json')
d = json.load(open(p, encoding='utf8'))
d['item.ashbound.ember_shard'] = 'Ember Shard'
d['item.ashbound.first_ember'] = 'First Ember'
for k in ('cold_forge', 'cold_forge_lit'):
    d['block.ashbound.' + k] = 'The Cold Forge'
json.dump(d, open(p, 'w', encoding='utf8'), indent=1, ensure_ascii=False)
