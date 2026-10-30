"""The gates' look in files: the scorched ground's textures (char + the cracks that glow in the gate's colour),
its model and blockstate, and the names. Run: python tools/gate_assets.py"""
import json, math, os, random
from PIL import Image

ROOT = os.path.join(os.path.dirname(__file__), "..", "src", "main", "resources", "assets", "ashbound")
N = 32


def noise(seed):
    rnd = random.Random(seed)
    g = [[rnd.random() for _ in range(N)] for _ in range(N)]

    def at(x, y):
        # smooth, tiling: average of a wrapped neighbourhood
        s = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                s += g[(y + dy) % N][(x + dx) % N]
        return s / 9
    return at


def char(seed):
    """Blackened ground: soot, darker at random blots, edges eaten away so tiles don't read as squares."""
    a, b = noise(seed), noise(seed + 1)
    img = Image.new("RGBA", (N, N))
    for y in range(N):
        for x in range(N):
            n = a(x, y) * 0.7 + b(x * 2 % N, y * 2 % N) * 0.3
            v = int(14 + n * 22)
            alpha = int(150 + n * 105) if n > 0.33 else int(n * 300)
            img.putpixel((x, y), (v, int(v * 0.92), int(v * 0.88), max(0, min(255, alpha))))
    return img


def cracks(seed):
    """Jagged glowing cracks that run off every edge, so neighbours join up."""
    rnd = random.Random(seed)
    img = Image.new("RGBA", (N, N), (0, 0, 0, 0))

    def put(x, y, a):
        x %= N
        y %= N
        old = img.getpixel((x, y))[3]
        if a > old:
            img.putpixel((x, y), (255, 255, 255, a))

    for _ in range(3):
        x, y = rnd.uniform(0, N), rnd.uniform(0, N)
        ang = rnd.uniform(0, math.tau)
        for _ in range(46):
            ang += rnd.uniform(-0.7, 0.7)
            x += math.cos(ang)
            y += math.sin(ang)
            put(int(x), int(y), 255)
            put(int(x) + 1, int(y), 90)
            if rnd.random() < 0.08:  # a branch
                bx, by, ba = x, y, ang + rnd.choice((-1, 1)) * 1.1
                for _ in range(rnd.randint(4, 9)):
                    ba += rnd.uniform(-0.5, 0.5)
                    bx += math.cos(ba)
                    by += math.sin(ba)
                    put(int(bx), int(by), 200)
    return img


def spark():
    """A soft hot sliver: bright down the middle, fading to the sides (stretched along the flight in game)."""
    img = Image.new("RGBA", (8, 16))
    for y in range(16):
        for x in range(8):
            d = abs(x - 3.5) / 3.5
            a = max(0.0, 1 - d) ** 1.8
            img.putpixel((x, y), (255, 255, 255, int(255 * a)))
    return img


def puff(seed):
    """A soft, lumpy puff of smoke: noise cut by a round falloff, alpha only (tinted in game)."""
    rnd = random.Random(seed)
    S = 32
    blobs = [(rnd.uniform(9, 23), rnd.uniform(9, 23), rnd.uniform(5, 10)) for _ in range(6)]
    a_n = noise(seed + 50)
    img = Image.new("RGBA", (S, S))
    for y in range(S):
        for x in range(S):
            v = 0.0
            for bx, by, br in blobs:
                d = math.hypot(x - bx, y - by) / br
                v = max(v, max(0.0, 1 - d * d))
            edge = max(0.0, 1 - math.hypot(x - 15.5, y - 15.5) / 15.5)
            v = v * (0.55 + 0.45 * a_n(x, y)) * min(1.0, edge * 2.2)
            g = int(200 + 55 * a_n((x * 2) % N, (y * 2) % N))
            img.putpixel((x, y), (g, g, g, int(255 * min(1.0, v))))
    return img


def write(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def main():
    tex = os.path.join(ROOT, "textures", "block")
    os.makedirs(tex, exist_ok=True)
    char(7).save(os.path.join(tex, "gate_scorch.png"))
    cracks(11).save(os.path.join(tex, "gate_scorch_cracks.png"))
    ptex = os.path.join(ROOT, "textures", "particle")
    os.makedirs(ptex, exist_ok=True)
    spark().save(os.path.join(ptex, "gate_spark.png"))
    for i in range(4):
        puff(100 + i).save(os.path.join(ptex, "gate_smoke_%d.png" % i))
    pdir = os.path.join(ROOT, "particles")
    os.makedirs(pdir, exist_ok=True)
    write(os.path.join(pdir, "gate_spark.json"), {"textures": ["ashbound:gate_spark"]})
    write(os.path.join(pdir, "gate_smoke.json"), {"textures": ["ashbound:gate_smoke_%d" % i for i in range(4)]})
    model = {
        "parent": "block/block",
        "render_type": "minecraft:translucent",
        "ambientocclusion": False,
        "textures": {"particle": "ashbound:block/gate_scorch", "char": "ashbound:block/gate_scorch",
                     "cracks": "ashbound:block/gate_scorch_cracks"},
        "elements": [
            {"from": [0, 0, 0], "to": [16, 0.2, 16],
             "faces": {"up": {"uv": [0, 0, 16, 16], "texture": "#char"}}},
            {"from": [0, 0.25, 0], "to": [16, 0.25, 16], "shade": False,
             "faces": {"up": {"uv": [0, 0, 16, 16], "texture": "#cracks", "tintindex": 0,
                              "neoforge_data": {"block_light": 15, "sky_light": 15}}}},
        ],
    }
    write(os.path.join(ROOT, "models", "block", "gate_scorch.json"), model)
    write(os.path.join(ROOT, "blockstates", "gate_scorch.json"),
          {"variants": {"": [{"model": "ashbound:block/gate_scorch", "y": r} for r in (0, 90, 180, 270)]}})
    lang_path = os.path.join(ROOT, "lang", "en_us.json")
    with open(lang_path, encoding="utf-8") as f:
        lang = json.load(f)
    lang["entity.ashbound.gate"] = "Gate"
    lang["block.ashbound.gate_scorch"] = "Scorched Ground"
    write(lang_path, lang)
    print("gate assets written")


if __name__ == "__main__":
    main()
