"""The crab's claw strike on Epic Fight's spider skeleton (11/7: the Wreck-Mother reared up on two legs to bite like a spider;
a crab stays low and swings its claws). Poses are turns of the front legs (LL1, RL1: the claws) about the body's own axes,
made from the skeleton's rest (read from Epic Fight's spider armature, never one of their clips).

  0.00  rest
  0.30  wind-up: both claws lifted high and opened, the body sunk back a little
  0.40  the blow: the claws slam forward and down and pinch in, the body lunges after them
  0.55  held in the ground
  0.90  back to rest

    python tools/crab_clips.py   -> assets/ashbound/animmodels/animations/spider/crab_claw.json
"""
import glob
import json
import math
import os
import zipfile

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "main", "resources", "assets", "ashbound", "animmodels", "animations", "spider")
JAR = glob.glob(os.path.expanduser("~/.gradle/caches/modules-2/files-2.1/maven.modrinth/epic-fight/*/*/epic-fight-*.jar"))[0]


def rest():
    """Each joint's rest transform (row-major 4x4, its parent's frame), from the spider armature."""
    with zipfile.ZipFile(JAR) as z:
        arm = json.loads(z.read("assets/epicfight/animmodels/entity/spider.json"))["armature"]
    out = {}

    def walk(j):
        out[j["name"]] = j["transform"]
        for c in j.get("children", []):
            walk(c)
    for r in arm["hierarchy"]:
        walk(r)
    return out


def M(t):
    return [t[i * 4:i * 4 + 4] for i in range(4)]


def flat(m):
    return [round(v, 6) for r in m for v in r]


def mul3(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def rx(d):
    c, s = math.cos(math.radians(d)), math.sin(math.radians(d))
    return [[1, 0, 0], [0, c, -s], [0, s, c]]


def ry(d):
    c, s = math.cos(math.radians(d)), math.sin(math.radians(d))
    return [[c, 0, s], [0, 1, 0], [-s, 0, c]]


def turned(t, q):
    """A joint turned about its own pivot by q (in its parent's frame: the body's, +y up, -z forward, +x its right)."""
    m = M(t)
    r = mul3(q, [row[:3] for row in m[:3]])
    return flat([r[0] + [m[0][3]], r[1] + [m[1][3]], r[2] + [m[2][3]], m[3]])


def moved(t, dx=0.0, dy=0.0, dz=0.0):
    m = M(t)
    m[0][3] += dx
    m[1][3] += dy
    m[2][3] += dz
    return flat(m)


def main():
    R = rest()
    times = [0.0, 0.30, 0.40, 0.55, 0.90]
    # (lift about x, open/close about y) per key; + lift raises the tips, + open turns a right claw outward
    claw = [(0, 0), (55, 18), (-22, -20), (-18, -16), (0, 0)]
    # the body (Root, in the model's own frame: z up, +y forward): back and down on the wind-up, forward on the blow
    body = [(0, 0), (-0.05, -0.02), (0.12, -0.04), (0.10, -0.035), (0, 0)]
    anim = []
    for name, t in R.items():
        frames = []
        for k in range(len(times)):
            if name in ("RL1", "LL1"):
                lift, opn = claw[k]
                side = 1 if name == "RL1" else -1
                frames.append(turned(t, mul3(ry(-side * opn), rx(lift))))
            elif name == "Root":
                fwd, down = body[k]
                frames.append(moved(t, dy=fwd, dz=down))
            elif name == "Head":
                frames.append(turned(t, rx([0, 8, -6, -4, 0][k])))
            else:
                frames.append(flat(M(t)))
        anim.append({"name": name, "time": times, "transform": frames})
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "crab_claw.json"), "w", encoding="utf-8") as f:
        json.dump({"animation": anim}, f)
    print("crab_claw:", len(anim), "joints,", times[-1], "s")


if __name__ == "__main__":
    main()
