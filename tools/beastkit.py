"""The world beasts on their own skeletons (not Epic Fight's spider): build, check, export into the game, and animate.

A beast is tools/beasts/<name>.py: make(name, legend) -> (s, parts), BONES, and CLIPS (its animations). A clip is
    {"len": ticks, "loop": bool, "stride": blocks a loop covers (walk/run), "bones": {bone: [[t, x, y, z], ...]},
     "hips": [[t, dx, dy, dz], ...] (blocks), "events": {"hit": [t, ...], ...}, + whatever the server reads (reach...)}
turns in degrees on top of the rest pose (z, then y, then x, as BeastRig poses them), eased between keys.

    python tools/beastkit.py <name> check            every piece attached (connect_check)
    python tools/beastkit.py <name> rest             a background render of it standing
    python tools/beastkit.py <name> frames [clip..]  strips of each clip, rendered side and three-quarter
    python tools/beastkit.py <name> export           rig + meshes + texture into the game, clips into resources
"""
import importlib
import json
import math
import os
import subprocess
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "beasts"))
sys.path.insert(0, os.path.join(HERE, "mobs"))
sys.path.insert(0, "E:/Ashbound/tools")

import voxmob as M  # noqa: E402
import voxsword as V  # noqa: E402
from voxboss import mat_mul, mat_rots, UNIT  # noqa: E402
import connect_check as CC  # noqa: E402

GAME = Path(HERE).parent
ASSETS = GAME / "src/main/resources/assets/ashbound"
CLIPS_OUT = GAME / "src/main/resources/ashbound/beasts"
BLENDER = "E:/Steam/steamapps/common/Blender/blender.exe"
VOX = Path("E:/Ashbound/tools/renders/vox")
SHEETS = Path(HERE) / "renders" / "beasts"


def mod(name):
    return importlib.import_module(name.replace("legend_", ""))


# ---------------------------------------------------------------- clips

def ease(f):
    return f * f * (3 - 2 * f)


def sample(keys, t, loop_len=None):
    """the value at tick t from [[t, a, b, c], ...]: eased between neighbouring keys (wrapping if it loops)"""
    if not keys:
        return (0.0, 0.0, 0.0)
    if loop_len:
        t = t % loop_len
        keys = keys + [[keys[0][0] + loop_len] + list(keys[0][1:])]
    if t <= keys[0][0]:
        return tuple(keys[0][1:])
    for a, b in zip(keys, keys[1:]):
        if a[0] <= t <= b[0]:
            f = ease((t - a[0]) / max(1e-6, b[0] - a[0]))
            return tuple(a[i] + (b[i] - a[i]) * f for i in (1, 2, 3))
    return tuple(keys[-1][1:])


def pose_at(clip, t):
    L = clip["len"] if clip.get("loop") else None
    rot = {b: sample(k, t, L) for b, k in clip["bones"].items()}
    hips = sample(clip.get("hips", []), t, L)
    return rot, hips


def wave(n, length, amp, phase=0.0, base=(0, 0, 0), axis=0, step=4, extra=None):
    """keys for a loop: base plus amp*sin round the loop on one axis (phase in loops); extra(f) -> (dx, dy, dz)"""
    out = []
    for t in range(0, length, step):
        f = t / length
        v = list(base)
        v[axis] += amp * math.sin(2 * math.pi * (f + phase))
        if extra:
            for i, d in enumerate(extra(f)):
                v[i] += d
        out.append([t] + [round(c, 2) for c in v])
    return out


# ---------------------------------------------------------------- posing the model (previews)

def posed(name, legend, clip, t):
    m = mod(name)
    s, parts = m.make(name, legend)
    rot, hips = pose_at(clip, t)
    for bone, (x, y, z) in rot.items():
        if bone in parts and (x or y or z):
            parts[bone].m = mat_mul(mat_rots((("z", z), ("y", y), ("x", x))), parts[bone].m)
    root = next(p for p in parts.values() if p.parent is None)
    root.move = tuple(c * UNIT for c in hips)
    return s, parts


def floor_of(s, tags=("foot",)):
    return min(p[1] for b in s.boxes if b.tag in tags for p in CC.aabb(b))


def preview_at(s, name, lo):
    """M.preview, but on the rest pose's floor (as the game draws it) instead of re-grounding every frame"""
    M.PREVIEW.mkdir(parents=True, exist_ok=True)
    img, tris = s.build()
    V.to_item = lambda p: (p[0] / UNIT, (p[1] - lo) / UNIT, p[2] / UNIT)
    img.save(M.PREVIEW / ("%s_f0.png" % name))
    V.write_obj(M.PREVIEW / ("%s_f0.obj" % name), tris)


def feet(name, legend, clips, step=2):
    """how high each paw's sole is over the rest floor (blocks) through each clip: - is through the ground"""
    m = mod(name)
    s0, p0 = m.make(name, legend)
    lo = floor_of(s0)
    paws = [n for n, pt in p0.items() if any(b.part is pt and b.tag == "foot" for b in s0.boxes)]
    for c in clips or list(m.CLIPS):
        clip = m.CLIPS[c]
        print("%s (%d ticks)" % (c, clip["len"]))
        for t in range(0, clip["len"] + 1, step):
            s, parts = posed(name, legend, clip, t)
            row = []
            for pw in paws:
                ys = [p[1] for b in s.boxes if b.part is parts[pw] and b.tag == "foot" for p in CC.aabb(b)]
                row.append("%s %+5.2f" % (pw[:3], (min(ys) - lo) / UNIT))
            top = max(p[1] for b in s.boxes for p in CC.aabb(b))
            print("  t%3d  %s   top %.1f" % (t, "  ".join(row), (top - lo) / UNIT))


def fit(name, legend, clip_name, air=(), k=1.0):
    """hips keys that put the lowest paw on the floor at every key tick (ticks inside an air (a, b) range keep theirs);
    printed back in the units the clip was keyed in (divided by k, the beast's own scale-up)"""
    m = mod(name)
    clip = m.CLIPS[clip_name]
    s0, _ = m.make(name, legend)
    lo = floor_of(s0)
    ticks = sorted({int(kk[0]) for ks in clip["bones"].values() for kk in ks} | {int(kk[0]) for kk in clip.get("hips", [])} | {clip["len"]})
    out = []
    for t in ticks:
        x, y, z = sample(clip.get("hips", []), t)
        if not any(a <= t <= b for a, b in air):
            s, parts = posed(name, legend, clip, t)
            low = min(p[1] for b in s.boxes if b.tag == "foot" for p in CC.aabb(b))
            y -= (low - lo) / UNIT
        out.append([t, round(x / k, 3), round(y / k, 3), round(z / k, 3)])
    print(clip_name, "hips=" + json.dumps(out))
    return out


def fitall(name, legend=False):
    """every move's hips fitted to the floor, saved as tools/beasts/<name>_fit.json (legendkit.fitted reads it)"""
    m = mod(name)
    air = getattr(m, "AIR", {})
    out = {}
    for n, c in m.CLIPS.items():
        if c.get("loop") or n in ("hurt", "death"):
            continue
        out[n] = fit(name, legend, n, air.get(n, ()), getattr(m, "K", 1.0))
    (Path(HERE) / "beasts" / (name + "_fit.json")).write_text(json.dumps(out), encoding="utf-8")


def render(names, h):
    subprocess.run([BLENDER, "-b", "-P", "E:/Ashbound/tools/blender/preview_mob.py", "--"] + ["%s@%.1f" % (n, h) for n in names],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def height(s):
    lo = min(p[1] for b in s.boxes for p in CC.aabb(b))
    hi = max(p[1] for b in s.boxes for p in CC.aabb(b))
    z0 = min(p[2] for b in s.boxes for p in CC.aabb(b))
    z1 = max(p[2] for b in s.boxes for p in CC.aabb(b))
    return (hi - lo) / UNIT, (z1 - z0) / UNIT


def frames(name, legend, clips, n=6):
    from PIL import Image
    m = mod(name)
    todo = clips or list(m.CLIPS)
    s0, _ = m.make(name, legend)
    tall, long_ = height(s0)
    lo = floor_of(s0)
    h = max(tall, long_ * 0.62) * 1.25
    rows = []
    for c in todo:
        clip = m.CLIPS[c]
        k = n if not clip.get("loop") else min(n, 8)
        ts = [round(clip["len"] * i / (k - (0 if clip.get("loop") else 1)), 1) for i in range(k)]
        names = []
        for i, t in enumerate(ts):
            s, parts = posed(name, legend, clip, t)
            nm = "%s_pose_%s_%02d" % (name, c, i)
            preview_at(s, nm, lo)
            names.append(nm)
        render(names, h)
        rows.append((c, ts, names))
    SHEETS.mkdir(parents=True, exist_ok=True)
    for view in ("side", "threequarter"):
        ims = [[Image.open(VOX / ("%s_%s.png" % (nm, view))).convert("RGB") for nm in names] for _, _, names in rows]
        w, hh = ims[0][0].size
        cols = max(len(r) for r in ims)
        sheet = Image.new("RGB", (w * cols // 2, hh * len(ims) // 2), (40, 44, 52))
        for r, row in enumerate(ims):
            for c, im in enumerate(row):
                sheet.paste(im.resize((w // 2, hh // 2)), (c * w // 2, r * hh // 2))
        out = SHEETS / ("%s_%s_%s.png" % (name + ("_legend" if legend else ""), "_".join(todo)[:40], view))
        sheet.save(out)
        print(out)


# ---------------------------------------------------------------- into the game

def scaled(clips, k):
    """a legend's clips: the same turns, its body's moves and its reach as much bigger as it is"""
    if k == 1:
        return clips
    import copy
    out = copy.deepcopy(clips)
    for c in out.values():
        c["hips"] = [[t, x * k, y * k, z * k] for t, x, y, z in c.get("hips", [])]
        if "stride" in c:
            c["stride"] = round(c["stride"] * k, 2)
        for key in ("reach", "range", "leap", "radius", "front", "throw"):
            if key in c:
                c[key] = [round(v * k, 2) for v in c[key]] if isinstance(c[key], list) else round(c[key] * k, 2)
    return out


def export(name, legend):
    m = mod(name)
    rig = (m.LEGEND if legend and m.LEGEND else name)
    s, parts = m.make(rig, legend)
    M.ASSETS = ASSETS
    (ASSETS / "textures/entity/beast").mkdir(parents=True, exist_ok=True)
    pts = {}
    for tag, key in (("frost_breath", "mouth"), ("eye", "eyes")):
        bx = [b for b in s.boxes if b.tag == tag]
        if bx:
            c = [sum(b.lo[i] + b.size[i] / 2 for b in bx) / len(bx) for i in range(3)]
            bone = next(n for n, p in parts.items() if p is bx[0].part)
            pts[key] = (bone, tuple(c))
    M.export(s, parts, "beast/" + rig, m.BONES, pts, ground_tags=("foot",))
    # its numbers: off the spider list (gate_mobs.json, where the first port put it) into beasts.json (Beast.java)
    res = GAME / "src/main/resources/ashbound"
    gm = json.loads((res / "gate_mobs.json").read_text(encoding="utf-8"))
    old = next((g for g in gm if g["id"] == rig), None)
    if old:
        gm = [g for g in gm if g["id"] != rig]
        (res / "gate_mobs.json").write_text(json.dumps(gm, indent=1), encoding="utf-8")
    import world_beasts as WB
    st = getattr(m, "STATS", None) or WB.MOBS[rig]["stats"]
    is_legend = legend or getattr(m, "IS_LEGEND", False)
    tall, long_ = height(s)
    bj = res / "beasts.json"
    beasts = json.loads(bj.read_text(encoding="utf-8")) if bj.exists() else {}
    prev = beasts.get(rig, {})
    hb = getattr(m, "HITBOX", None) or (round(min(tall, long_ * 0.42), 1), round(tall * 0.92, 1))
    beasts[rig] = {"rig": rig, "w": hb[0], "h": hb[1], "hp": st["hp"], "speed": st["speed"],
                   "dmg": st["dmg"], "armor": st["armor"], "kb": st["kb"], "legend": is_legend,
                   "egg": getattr(m, "EGG", None) or (old or prev).get("egg", 0x888888),
                   "spots": getattr(m, "SPOTS", None) or (old or prev).get("spots", 0x222222)}
    bj.write_text(json.dumps(beasts, indent=1), encoding="utf-8")
    CLIPS_OUT.mkdir(parents=True, exist_ok=True)
    tall, long_ = height(s)
    (CLIPS_OUT / (rig + ".json")).write_text(json.dumps({"_about": "written by tools/beastkit.py from tools/beasts/%s.py" % name,
                                                          "height": round(tall, 2), "length": round(long_, 2),
                                                          "clips": scaled(m.CLIPS, getattr(m, "LEGEND_SCALE", 1.6) if legend else 1)}, indent=1), encoding="utf-8")
    print("%s: %.1f blocks tall, %.1f long, %d clips" % (rig, tall, long_, len(m.CLIPS)))


def main():
    name, what = sys.argv[1], sys.argv[2]
    legend = "--legend" in sys.argv
    rest = [a for a in sys.argv[3:] if not a.startswith("--")]
    m = mod(name)
    if what == "check":
        s, _ = m.make(name, legend)
        lo = CC.loose(s)
        print("%s: %s" % (name, "ok" if not lo else lo))
    elif what == "rest":
        s, _ = m.make(name, legend)
        tall, long_ = height(s)
        nm = "%s_rest%s" % (name, "_legend" if legend else "")
        M.preview(s, nm, ground_tags=("foot",))
        render([nm], max(tall, long_ * 0.62) * 1.15)
        print(VOX / (nm + "_threequarter.png"), "%.1f tall %.1f long" % (tall, long_))
    elif what == "frames":
        frames(name, legend, rest)
    elif what == "fit":
        air = [tuple(int(v) for v in a.split("-")) for a in sys.argv[4:] if "-" in a and not a.startswith("--")]
        fit(name, legend, rest[0], air, getattr(m, "K", 1.0))
    elif what == "fitall":
        fitall(name, legend)
    elif what == "feet":
        feet(name, legend, rest)
    elif what == "export":
        export(name, legend)


if __name__ == "__main__":
    main()
