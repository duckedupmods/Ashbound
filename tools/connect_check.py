"""Is every piece of a hand-built monster attached? Puts each box in the rest pose (its own turn, its part's, the
parents'), joins boxes that touch, and lists every group cut off from the main body - a head floating off its neck,
a horn hanging in the air, a tail that doesn't meet the rump.

    python tools/connect_check.py <mobs module | monster name ...> [--gap 0.3]
"""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "mobs"))
sys.path.insert(0, HERE)
sys.path.insert(0, 'E:/Ashbound/tools')


def aabb(b):
    pts = [b.world((i, j, k)) for i in (0, 1) for j in (0, 1) for k in (0, 1)]
    return tuple(min(p[a] for p in pts) for a in range(3)), tuple(max(p[a] for p in pts) for a in range(3))


def loose(s, gap=0.3):
    boxes = [b for b in s.boxes if b.tag != "speck"]
    bb = [aabb(b) for b in boxes]
    n = len(boxes)
    up = list(range(n))

    def find(i):
        while up[i] != i:
            up[i] = up[up[i]]
            i = up[i]
        return i
    order = sorted(range(n), key=lambda i: bb[i][0][0])
    for a_i, i in enumerate(order):
        lo_i, hi_i = bb[i]
        for j in order[a_i + 1:]:
            lo_j, hi_j = bb[j]
            if lo_j[0] > hi_i[0] + gap:
                break
            if all(lo_j[a] <= hi_i[a] + gap and lo_i[a] <= hi_j[a] + gap for a in range(3)):
                up[find(i)] = find(j)
    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    main = max(groups.values(), key=len)
    out = []
    for g in groups.values():
        if g is main:
            continue
        tags = sorted({boxes[i].tag for i in g})
        c = [sum((bb[i][0][a] + bb[i][1][a]) / 2 for i in g) / len(g) for a in range(3)]
        out.append((len(g), tags, c))
    return sorted(out, key=lambda o: -o[0])


def main():
    gap = float(sys.argv[sys.argv.index("--gap") + 1]) if "--gap" in sys.argv else 0.3
    args = [a for a in sys.argv[1:] if not a.startswith("--") and a != str(gap)]
    todo = []
    for a in args:
        if os.path.exists(os.path.join(HERE, "mobs", a + ".py")):
            mod = importlib.import_module(a)
            todo += list(mod.MOBS.items())
        else:
            import forge_specs as FS
            todo.append((a, FS.SPECS[a]))
    bad = 0
    for name, spec in todo:
        s = spec["make"]()[0]
        lo = loose(s, gap)
        print("%-18s %s" % (name, "ok" if not lo else "%d loose" % len(lo)))
        for cnt, tags, c in lo:
            print("    %3d boxes  at (%.1f, %.1f, %.1f)  %s" % (cnt, c[0], c[1], c[2], ", ".join(tags)[:90]))
        bad += bool(lo)
    print("%d of %d have loose pieces" % (bad, len(todo)))


if __name__ == "__main__":
    main()
