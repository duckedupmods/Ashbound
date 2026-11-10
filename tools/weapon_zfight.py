"""Faces that fight: two faces of a weapon mesh lying in the same plane, facing the same way, overlapping - in game
their textures flicker as the camera moves. Lists them per mesh (and how much area overlaps).

    python tools/weapon_zfight.py [ids...]      (default: every mesh in assets/ashbound/models/mesh)
"""
import glob
import os
import sys
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MESH = os.path.join(ROOT, "src", "main", "resources", "assets", "ashbound", "models", "mesh")


def load(path):
    vs, faces, obj = [], [], ""
    for line in open(path, encoding="utf-8"):
        if line.startswith("v "):
            vs.append(tuple(float(t) for t in line.split()[1:4]))
        elif line.startswith(("o ", "g ")):
            obj = line.split(maxsplit=1)[1].strip()
        elif line.startswith("f "):
            idx = [int(t.split("/")[0]) for t in line.split()[1:]]
            faces.append(([vs[i - 1 if i > 0 else i] for i in idx], obj))
    return faces


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def area2(poly):
    return abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))) / 2


def clip(subject, clipper):
    """Sutherland-Hodgman: subject polygon clipped by a convex clipper (both 2D, anticlockwise)"""
    out = subject
    for i in range(len(clipper)):
        a, b = clipper[i], clipper[(i + 1) % len(clipper)]
        inp, out = out, []
        if not inp:
            break

        def inside(p):
            return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) >= -1e-9

        def meet(p, q):
            x1, y1, x2, y2 = p[0], p[1], q[0], q[1]
            x3, y3, x4, y4 = a[0], a[1], b[0], b[1]
            den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            if abs(den) < 1e-12:
                return q
            t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
            return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
        for j in range(len(inp)):
            p, q = inp[j], inp[(j + 1) % len(inp)]
            if inside(q):
                if not inside(p):
                    out.append(meet(p, q))
                out.append(q)
            elif inside(p):
                out.append(meet(p, q))
    return out


def ccw(poly):
    s = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))
    return poly if s > 0 else poly[::-1]


def fights(path, eps=1e-4, least=1e-4):
    planes = defaultdict(list)
    for pts, obj in load(path):
        if len(pts) < 3:
            continue
        n = cross(sub(pts[1], pts[0]), sub(pts[2], pts[0]))
        l = dot(n, n) ** 0.5
        if l < 1e-12:
            continue
        n = (n[0] / l, n[1] / l, n[2] / l)
        key = (round(n[0], 3), round(n[1], 3), round(n[2], 3), round(dot(n, pts[0]) / eps) * eps)
        planes[key].append((pts, obj, n))
    found = []
    for key, fs in planes.items():
        if len(fs) < 2:
            continue
        n = fs[0][2]
        # a 2D frame in the plane
        u = cross(n, (0, 0, 1) if abs(n[2]) < 0.9 else (1, 0, 0))
        lu = dot(u, u) ** 0.5
        u = (u[0] / lu, u[1] / lu, u[2] / lu)
        v = cross(n, u)
        flat = [(ccw([(dot(p, u), dot(p, v)) for p in pts]), obj) for pts, obj, _ in fs]
        for i in range(len(flat)):
            for j in range(i + 1, len(flat)):
                a, b = flat[i][0], flat[j][0]
                if (max(p[0] for p in a) <= min(p[0] for p in b) or max(p[0] for p in b) <= min(p[0] for p in a)
                        or max(p[1] for p in a) <= min(p[1] for p in b) or max(p[1] for p in b) <= min(p[1] for p in a)):
                    continue
                c = clip(a, b)
                if len(c) >= 3 and area2(c) > least:
                    found.append((flat[i][1], flat[j][1], area2(c)))
    return found


def fix(path, eps=0.0016, passes=6):
    """Pulls them apart: of each fighting pair, the smaller face moves out along its normal by eps (its box grows that
    hair on that side, so nothing cracks); a face sharing corners with its rival gets corners of its own. Repeats with
    a bigger step while any are left (three faces in one plane). Returns how many pairs are left."""
    left = 0
    for k in range(passes):
        lines = open(path, encoding="utf-8").read().split("\n")
        vs, faces = [], []          # faces: (line index, [vertex indices], [rest of each token])
        for i, line in enumerate(lines):
            if line.startswith("v "):
                vs.append([float(t) for t in line.split()[1:4]])
            elif line.startswith("f "):
                toks = line.split()[1:]
                faces.append((i, [int(t.split("/")[0]) - 1 for t in toks], ["/" + t.split("/", 1)[1] if "/" in t else "" for t in toks]))
        planes = defaultdict(list)
        plane_of = {}
        for fi, (_, idx, _) in enumerate(faces):
            pts = [tuple(vs[j]) for j in idx]
            if len(pts) < 3:
                continue
            n = cross(sub(pts[1], pts[0]), sub(pts[2], pts[0]))
            l = dot(n, n) ** 0.5
            if l < 1e-12:
                continue
            n = (n[0] / l, n[1] / l, n[2] / l)
            key = (round(n[0], 3), round(n[1], 3), round(n[2], 3), round(dot(n, pts[0]) / 1e-4))
            planes[key].append((fi, n))
            plane_of[fi] = key
        move = {}
        for fs in planes.values():
            if len(fs) < 2:
                continue
            n = fs[0][1]
            u = cross(n, (0, 0, 1) if abs(n[2]) < 0.9 else (1, 0, 0))
            lu = dot(u, u) ** 0.5
            u = (u[0] / lu, u[1] / lu, u[2] / lu)
            v = cross(n, u)
            flat = [(fi, ccw([(dot(vs[j], u), dot(vs[j], v)) for j in faces[fi][1]])) for fi, _ in fs]
            for a in range(len(flat)):
                for b in range(a + 1, len(flat)):
                    fa, pa = flat[a]
                    fb, pb = flat[b]
                    if (max(p[0] for p in pa) <= min(p[0] for p in pb) or max(p[0] for p in pb) <= min(p[0] for p in pa)
                            or max(p[1] for p in pa) <= min(p[1] for p in pb) or max(p[1] for p in pb) <= min(p[1] for p in pa)):
                        continue
                    c = clip(pa, pb)
                    if len(c) < 3 or area2(c) <= 1e-4:
                        continue
                    small = fa if area2(pa) <= area2(pb) else fb
                    if small not in move:
                        move[small] = n
        if not move:
            return 0
        left = len(move)
        step = eps * (k + 1)
        # a corner shared with a face in the same plane that stays put (its rival) is split off; corners shared only
        # with the box's other sides just move, so the box grows on that side
        users = defaultdict(set)
        for fi, (_, idx, _) in enumerate(faces):
            for j in idx:
                users[j].add(fi)
        for fi, n in move.items():
            line_i, idx, rest = faces[fi]
            new_idx = []
            for j in idx:
                if any(o != fi and plane_of.get(o) == plane_of[fi] and o not in move for o in users[j]):
                    vs.append(list(vs[j]))
                    j = len(vs) - 1
                new_idx.append(j)
            faces[fi] = (line_i, new_idx, rest)
        shift = defaultdict(set)
        for fi, n in move.items():
            for j in faces[fi][1]:
                shift[j].add(n)
        for j, ns in shift.items():
            for n in ns:
                vs[j] = [vs[j][0] + n[0] * step, vs[j][1] + n[1] * step, vs[j][2] + n[2] * step]
        # write back: vertices first (in order), the faces with their new corners
        out, vi = [], 0
        for line in lines:
            if line.startswith("v "):
                continue
            out.append(line)
        head = [l for l in out if l.startswith(("mtllib", "#"))]
        body = [l for l in out if not l.startswith(("mtllib", "#"))]
        face_line = {line_i: (idx, rest) for line_i, idx, rest in faces}
        # rebuild body with faces replaced (match by original order of "f " lines)
        f_iter = iter(sorted(face_line.items()))
        rebuilt = []
        for l in body:
            if l.startswith("f "):
                _, (idx, rest) = next(f_iter)
                rebuilt.append("f " + " ".join("%d%s" % (j + 1, r) for j, r in zip(idx, rest)))
            else:
                rebuilt.append(l)
        verts = ["v %.5f %.5f %.5f" % tuple(p) for p in vs]
        open(path, "w", encoding="utf-8").write("\n".join(head + verts + rebuilt))
    return left


def main():
    args = sys.argv[1:]
    do_fix = "--fix" in args
    ids = [a for a in args if not a.startswith("--")]
    paths = [os.path.join(MESH, i + ".obj") for i in ids] if ids else sorted(glob.glob(os.path.join(MESH, "*.obj")))
    if do_fix:
        for p in paths:
            fix(p)
    bad = 0
    for p in paths:
        f = fights(p)
        if f:
            bad += 1
            total = sum(a for _, _, a in f)
            parts = sorted({tuple(sorted((x, y))) for x, y, _ in f})
            print("%-34s %4d pairs, %.4f area  %s" % (os.path.basename(p)[:-4], len(f), total, parts[:4]))
    print("%d of %d meshes have fighting faces" % (bad, len(paths)))


if __name__ == "__main__":
    main()
