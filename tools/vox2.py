"""Drawing tools for hand-built monsters, the way E:/Ashbound/tools/vox*.py builds them (the Coffin Knight, the Hangman):
not a body - every monster is its own - only the brushes: boxes on parts, limbs between two points, chains, tapered
stacks, rounded blobs, shards and spikes, rivets; and a material maker (rust, drips, crust, lit edges, patterns).

    import vox2 as X
    k = X.Kit("name")
    hips = k.part("hips", (0, 22, 0))
    k.box(hips, C(...), "plate", tag="faulds")
    ...
    k.s.shaders = {...}; return k.s, k.parts
"""
import math
import os
import sys

sys.path.insert(0, 'E:/Ashbound/tools')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import voxsword as V  # noqa: E402
from voxsword import Sword, ramp, shade, fbm, h3  # noqa: E402
from voxboss import Part, PB, C  # noqa: E402
import voxgate as G  # noqa: E402

BIPED = ["hips", "thigh_l", "shin_l", "foot_l", "thigh_r", "shin_r", "foot_r", "torso", "head",
         "arm_l", "fore_l", "hand_l", "arm_r", "fore_r", "hand_r"]


class Kit:
    def __init__(self, name):
        self.s = Sword(name)
        self.parts = {}

    def part(self, name, pivot, rots=(), parent=None, bone=True):
        p = Part(name, pivot, rots, self.parts[parent] if isinstance(parent, str) else parent)
        if bone:
            self.parts[name] = p
        return p

    def box(self, part, box, mat, **kw):
        lo, size = box
        b = PB(part, lo, size, mat, tag=kw.pop("tag", part.name), **kw)
        self.s.boxes.append(b)
        return b

    def limb(self, part, p0, p1, w, mat, tag="limb", d=None, group="lit"):
        G.limb(self.box, part, p0, p1, w, mat, tag, d=d, group=group)

    def chain(self, part, p0, p1, n, mat="iron", tag="chain", w=1.6):
        for k in range(n):
            a = tuple(p0[i] + (p1[i] - p0[i]) * k / n for i in range(3))
            c = tuple(p0[i] + (p1[i] - p0[i]) * (k + 1) / n for i in range(3))
            self.limb(part, a, c, w * (0.6 if k % 2 else 1.0), mat, tag, d=w * (1.0 if k % 2 else 0.6))

    def stack(self, part, cx, cz, layers, mat, tag, step=None):
        """a tapered mass from horizontal slices: layers = [(y, w, d), ...] bottom to top, filled between"""
        for (y0, w0, d0), (y1, w1, d1) in zip(layers, layers[1:]):
            n = max(1, int(round((y1 - y0) / (step or 1.5))))
            for k in range(n):
                t = (k + 0.5) / n
                w, d = w0 + (w1 - w0) * t, d0 + (d1 - d0) * t
                self.box(part, C(cx, y0 + (y1 - y0) * k / n, cz, w, (y1 - y0) / n + 0.05, d), mat, tag=tag)

    def blob(self, part, c, r, mat, tag, step=1.4, cut=None):
        """a rounded mass (an ellipsoid of slices); cut(y) -> False drops a slice"""
        cx, cy, cz = c
        rx, ry, rz = r
        n = max(2, int(2 * ry / step))
        for k in range(n):
            y = cy - ry + (k + 0.5) * 2 * ry / n
            f = math.sqrt(max(0.0, 1 - ((y - cy) / ry) ** 2))
            if f < 0.15 or (cut and not cut(y)):
                continue
            self.box(part, C(cx, y - ry / n, cz, 2 * rx * f, 2 * ry / n + 0.05, 2 * rz * f), mat, tag=tag)

    def shard(self, part, base, d, length, w, mat="crystal", tag="shard", group="lit"):
        """a crystal (or bone, or horn) from base along direction d, narrowing to a point in three steps"""
        n = math.sqrt(sum(c * c for c in d))
        d = tuple(c / n for c in d)
        pts = [tuple(base[i] + d[i] * length * f for i in range(3)) for f in (0, 0.55, 0.85, 1.0)]
        for (a, b), ww in zip(zip(pts, pts[1:]), (w, w * 0.62, w * 0.3)):
            self.limb(part, a, b, ww, mat, tag, group=group)

    def cluster(self, part, at, n, length, w, mat="crystal", seed=1, spread=0.7, up=(0, 1, 0), group="lit"):
        """shards grown out of one place, fanning out round `up`"""
        for k in range(n):
            a = k * 2.399 + seed
            s = spread * (0.3 + 0.7 * h3(k, seed, 1))
            d = (up[0] + math.cos(a) * s, up[1], up[2] + math.sin(a) * s)
            L = length * (0.55 + 0.45 * h3(k, seed, 2))
            base = (at[0] + math.cos(a) * w * 0.5, at[1], at[2] + math.sin(a) * w * 0.5)
            self.shard(part, base, d, L, w * (0.6 + 0.4 * h3(k, seed, 3)), mat, group=group)

    def rivets(self, part, pts, mat="iron", s=0.8):
        for (x, y, z) in pts:
            self.box(part, C(x, y, z, s, s, s), mat, tag="rivet")

    def ring(self, part, cx, cy, cz, r, w, mat, tag, n=12, axis="z"):
        """a ring of n short limbs (a hoop, a halo, a cart wheel), its axis along x, y or z"""
        for k in range(n):
            a0, a1 = k * 2 * math.pi / n, (k + 1) * 2 * math.pi / n

            def at(a):
                u, v = math.cos(a) * r, math.sin(a) * r
                return {"z": (cx + u, cy + v, cz), "x": (cx, cy + v, cz + u), "y": (cx + u, cy, cz + v)}[axis]
            self.limb(part, at(a0), at(a1), w, mat, tag)


# ================================================================ materials

def surf(R, base=0.5, light=1.0, grain=0.16, edge=0.16, rust=None, drip=None, crust=None, stripe=None, pattern=None,
         scale=1.0, holes=False):
    """a material from a ramp. rust=(ramp, amount, freq): patches; drip=(ramp, amount): streaks running down;
    crust=(ramp, amount): on what faces up; stripe=n: a dark line every n texels; pattern(p, n, i, j, w, h) -> offset
    (None: a hole); holes: a torn hem on hanging cloth"""
    def f(p, n, b, key, i, j, w, h, fr):
        x, y, z = (c * scale for c in p)
        if holes and key in ("n", "s", "e", "w") and h > 6 and j > h - 2 - 5 * h3(i // 2, int(b.size[1] * 3), 5):
            return None
        if crust and n[1] > 0.3 and fbm(x * 0.6, y * 0.6, z * 0.6) > 1 - crust[1]:
            return shade(crust[0], 0.45 + 0.4 * fbm(x, y, z), i, j)
        if drip and key not in ("u", "d") and fbm(x * 0.7, y * 0.07, z * 0.7) > 1 - drip[1]:
            return shade(drip[0], 0.35 + 0.4 * n[1] + 0.2 * fbm(x, y, z), i, j)
        if rust and fbm(x * rust[2] + 9, y * rust[2], z * rust[2]) > 1 - rust[1]:
            return shade(rust[0], 0.3 + 0.3 * n[1] + 0.2 * fbm(x * 2, y * 2, z * 2), i, j)
        v = base + light * (0.15 * n[1] + 0.06 * n[2] - 0.07 * (j / max(1, h - 1))) + grain * (fbm(x * 0.6, y * 0.6, z * 0.6) - 0.5)
        if edge and key not in ("u", "d") and (j == 0 or i == 0 or i == w - 1):
            v += edge
        if stripe and i % stripe == 0:
            v -= 0.12
        if pattern:
            d = pattern(p, n, i, j, w, h)
            if d is None:
                return None
            v += d
        return shade(R, v, i, j)
    return f


def glow(R, base=0.62, var=0.34):
    def f(p, n, b, key, i, j, w, h, fr):
        return shade(R, base + var * fbm(p[0] * 0.8, p[1] * 0.8, p[2] * 0.8), i, j)
    return f


def facets(R, dark=0.0):
    """crystal: flat facets in bands of light, a bright rim, a dark core where it is thick"""
    def f(p, n, b, key, i, j, w, h, fr):
        v = 0.42 + 0.3 * (n[0] * 0.4 + n[1] * 0.7 + n[2] * 0.3) + (0.24 if i == 0 or j == 0 else 0) + 0.12 * (((i + j) // 3) % 2) - dark
        return shade(R, v, i, j)
    return f


def veined(R, G_, freq=0.3, width=0.02):
    """rock or flesh with thin glowing seams running through it"""
    def f(p, n, b, key, i, j, w, h, fr):
        x, y, z = p
        if abs(fbm(x * freq + 7, y * freq, z * freq) - 0.5) < width:
            return shade(G_, 0.7 + 0.25 * fbm(x, y, z), i, j)
        v = 0.48 + 0.16 * n[1] + 0.06 * n[2] + 0.28 * (fbm(x * 0.5, y * 0.5, z * 0.5) - 0.5)
        if key not in ("u", "d") and j == 0:
            v += 0.14
        return shade(R, v, i, j)
    return f


def wrinkled(R, freq=1.0):
    """skin in folds: dark creases across it"""
    def f(p, n, b, key, i, j, w, h, fr):
        x, y, z = p
        v = 0.5 + 0.15 * n[1] + 0.2 * (fbm(x * 0.6, y * 0.6, z * 0.6) - 0.5)
        if (j + int(3 * fbm(x * 0.3, y * 0.3, z * 0.3))) % max(2, int(4 / freq)) == 0:
            v -= 0.18
        return shade(R, v, i, j)
    return f


def dark(R):
    def f(p, n, b, key, i, j, w, h, fr):
        return shade(R, 0.02, i, j)
    return f
