"""Weapons shown as their real 3D model in the inventory, item frames and on the ground, not a picture: each item
model's own "display" gets gui/fixed/ground transforms (the picture perspectives go), laid on Minecraft's classic
diagonal (grip bottom-left, tip top-right), turned a little so the blade's thickness shows, fitted to the slot.

The transform is Minecraft's: v' = T + R S (v - 0.5), the slot spanning -0.5..0.5; R = rotationXYZ of the degrees.

    python tools/gui3d.py [gates...] [--preview]
        --preview   tools/renders/gui3d/sheet_<gate>.png: each weapon as the slot would show it (Blender, headless)
"""
import glob
import json
import math
import os
import subprocess
import sys

GAME = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
A = os.path.join(GAME, "src/main/resources/assets/ashbound")
GEAR = json.load(open(os.path.join(GAME, "src/main/resources/ashbound/gear.json"), encoding="utf-8"))
BLENDER = sorted(glob.glob("E:/Steam/steamapps/common/Blender/blender.exe") + glob.glob("E:/Steam/steamapps/common/Blender/*/blender.exe"))[0]
PREVIEW = os.path.join(GAME, "tools/renders/gui3d")

FILL = 0.94          # of the slot the longest side takes
TURN = 22            # degrees the blade is turned about its length, so its edge shows


def rx(a):
    c, s = math.cos(a), math.sin(a)
    return [[1, 0, 0], [0, c, -s], [0, s, c]]


def ry(a):
    c, s = math.cos(a), math.sin(a)
    return [[c, 0, s], [0, 1, 0], [-s, 0, c]]


def rz(a):
    c, s = math.cos(a), math.sin(a)
    return [[c, -s, 0], [s, c, 0], [0, 0, 1]]


def mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def apply(m, v):
    return [sum(m[i][k] * v[k] for k in range(3)) for i in range(3)]


def euler_xyz(m):
    """degrees (x, y, z) with Rx Ry Rz = m: Minecraft's rotationXYZ"""
    y = math.asin(max(-1, min(1, m[0][2])))
    x = math.atan2(-m[1][2], m[2][2])
    z = math.atan2(-m[0][1], m[0][0])
    return [round(math.degrees(a), 2) for a in (x, y, z)]


def bounds(item):
    vs = [tuple(map(float, l.split()[1:4])) for l in open(os.path.join(A, "models/mesh/%s.obj" % item)) if l.startswith("v ")]
    return [min(v[i] for v in vs) for i in range(3)], [max(v[i] for v in vs) for i in range(3)]


def pose(item, kind):
    """the rotation for this weapon in the slot"""
    lo, hi = bounds(item)
    size = [h - l for l, h in zip(lo, hi)]
    if kind == "shield":
        return mul(rx(math.radians(12)), ry(math.radians(-28)))
    if kind == "bow":
        return ry(math.radians(-10))
    # the blade lies along y; it is seen flat on when its thin side (x or z) points at us
    spin = 90 if size[0] < size[2] else 0
    return mul(rz(math.radians(-45)), ry(math.radians(spin + TURN)))


def fit(item, r):
    lo, hi = bounds(item)
    corners = [[(lo, hi)[(k >> i) & 1][i] - 0.5 for i in range(3)] for k in range(8)]
    pts = [apply(r, c) for c in corners]
    ext = [max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(2)]
    s = min(4.0, FILL / max(ext))
    centre = [(max(p[i] for p in pts) + min(p[i] for p in pts)) / 2 * s for i in range(3)]
    t = [round(-c * 16, 3) for c in centre]
    return s, t


def weapons(gates):
    for d in GEAR:
        if gates and d["gate"] not in gates:
            continue
        for w in d["weapons"]:
            yield d["gate"], w["id"], w["kind"]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    done, prev = 0, []
    for gate, item, kind in weapons(set(args)):
        path = os.path.join(A, "models/item/%s.json" % item)
        if not os.path.exists(path) or not os.path.exists(os.path.join(A, "models/mesh/%s.obj" % item)):
            print("skipped", item)
            continue
        m = json.load(open(path, encoding="utf-8"))
        if m.get("loader") != "neoforge:separate_transforms":
            print("not a 3D item", item)
            continue
        r = pose(item, kind)
        s, t = fit(item, r)
        rot = euler_xyz(r)
        disp = m["base"].setdefault("display", {})
        disp["gui"] = {"rotation": rot, "translation": t, "scale": [round(s, 4)] * 3}
        disp["fixed"] = {"rotation": rot, "translation": t, "scale": [round(s, 4)] * 3}
        g = s * 0.55
        disp["ground"] = {"rotation": rot, "translation": [round(v * 0.55, 3) for v in t[:2]] + [0], "scale": [round(g, 4)] * 3}
        for k in ("gui", "fixed", "ground"):
            m.get("perspectives", {}).pop(k, None)
        m.setdefault("perspectives", {})           # NeoForge's loader needs the key, even empty
        m["gui_light"] = "side"
        json.dump(m, open(path, "w", encoding="utf-8"), indent=1)
        prev.append({"gate": gate, "id": item, "r": r, "s": s, "t": t})
        done += 1
    print("3D in the slot:", done)
    if "--preview" in sys.argv and prev:
        os.makedirs(PREVIEW, exist_ok=True)
        spec = os.path.join(PREVIEW, "batch.json")
        json.dump({"assets": A, "out": PREVIEW, "items": prev}, open(spec, "w"))
        r = subprocess.run([BLENDER, "-b", "-P", os.path.join(GAME, "tools/blender/gui_preview.py"), "--", spec],
                           capture_output=True, text=True)
        print([l for l in r.stdout.splitlines() if l.startswith("sheet")] or r.stderr[-1500:])


if __name__ == "__main__":
    main()
