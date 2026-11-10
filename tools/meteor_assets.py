"""Meteor fall's own pictures and data (Meteors.java, MeteorShard, client/MeteorRenderer), drawn here pixel by pixel:
the shard's crystal and its glowing veins, the crater's blocks (glassed ground, scorched earth, charred log), the
Shardglass icon; plus their block states, models, loot, tags, recipe and names.
    python tools/meteor_assets.py
The look is tools/blender/meteor_fall.py (renders in tools/renders/meteor)."""
import json
import math
import random
from pathlib import Path

from PIL import Image

GAME = Path(__file__).resolve().parent.parent
A = GAME / "src/main/resources/assets/ashbound"
D = GAME / "src/main/resources/data"
ENT = A / "textures/entity/meteor"
ENT.mkdir(parents=True, exist_ok=True)


def clamp(v):
    return max(0, min(255, int(v)))


def shard():
    """the crystal: 32 px round (u: 6 faces), 64 px up; near-black violet facets, a lighter edge where faces meet,
    faint grain up it. The glow layer: veins wandering up it, white (tinted the gate's colour in game), black elsewhere."""
    W, H = 32, 64
    r = random.Random(4)
    body = Image.new("RGBA", (W, H))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    bp, gp = body.load(), glow.load()
    for y in range(H):
        for x in range(W):
            face = x * 6 // W
            fx = (x * 6 / W) - face
            edge = 1.0 if fx < 0.09 or fx > 0.91 else 0.0
            shade = 0.85 + 0.15 * math.sin(face * 1.7) + r.uniform(-0.06, 0.06)
            grain = 0.06 * math.sin(x * 2.3 + y * 0.35)
            v = (14 + 26 * edge) * shade + grain * 40
            bp[x, y] = (clamp(v * 0.95), clamp(v * 0.85), clamp(v * 1.35 + 6), 255)
    # veins: a few lines wandering up each face, branching now and then
    for face in range(6):
        for k in range(2):
            x = face * W / 6 + r.uniform(1, W / 6 - 1)
            for y in range(H - 1, -1, -1):
                x += r.uniform(-0.7, 0.7)
                x = min(max(x, face * W / 6 + 0.5), (face + 1) * W / 6 - 1.5)
                ix = int(x)
                core = 1.0 if (y + k * 7) % 23 < 19 else 0.45
                for dx, a in ((0, 1.0), (-1, 0.35), (1, 0.35)):
                    xx = ix + dx
                    if 0 <= xx < W:
                        old = gp[xx, y][0]
                        gp[xx, y] = (clamp(old + 255 * a * core),) * 3 + (255,)
                if r.random() < 0.05:
                    bx = ix
                    for yy in range(y, max(-1, y - r.randint(3, 8)), -1):
                        bx += r.choice((-1, 1))
                        if 0 <= bx < W:
                            gp[bx, yy] = (clamp(gp[bx, yy][0] + 150),) * 3 + (255,)
    # a faint glow from inside, all over (so it never reads as flat black)
    for y in range(H):
        for x in range(W):
            g = gp[x, y][0]
            gp[x, y] = (clamp(g + 18),) * 3 + (255,)
            # the veins show a little in the body too
            if g > 120:
                b = bp[x, y]
                bp[x, y] = (clamp(b[0] + 40), clamp(b[1] + 30), clamp(b[2] + 60), 255)
    body.save(ENT / "shard.png")
    glow.save(ENT / "shard_glow.png")


def block_tex(name, fn, n=16, seed=1):
    r = random.Random(seed)
    im = Image.new("RGBA", (n, n))
    px = im.load()
    for y in range(n):
        for x in range(n):
            px[x, y] = fn(x, y, r)
    out = A / "textures/block"
    im.save(out / (name + ".png"))


def cracks(seed, n=16):
    """a little net of cracks: wandering lines from a few points"""
    r = random.Random(seed)
    m = [[0] * n for _ in range(n)]
    for _ in range(4):
        x, y = r.randrange(n), r.randrange(n)
        dx, dy = r.choice(((1, 0), (0, 1), (1, 1), (1, -1)))
        for _ in range(r.randint(6, 12)):
            m[y % n][x % n] = 1
            if r.random() < 0.35:
                dx, dy = r.choice(((1, 0), (0, 1), (1, 1), (1, -1), (-1, 1)))
            x += dx
            y += dy
    return m


def blocks():
    cr = cracks(9)
    # glassed ground: black glass with a little sheen, cracks glowing hot orange through it
    def glassed(x, y, r):
        if cr[y][x]:
            hot = r.random()
            return (255, clamp(120 + 90 * hot), clamp(30 + 40 * hot), 255)
        nb = sum(cr[(y + dy) % 16][(x + dx) % 16] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if nb:
            return (110, 34, 12, 255)
        v = 10 + r.randint(0, 10) + (14 if (x + y) % 7 == 0 else 0)
        return (clamp(v * 1.1), clamp(v * 0.9), clamp(v * 1.4), 255)
    block_tex("glassed_ground", glassed, seed=3)

    def scorched(x, y, r):
        v = r.choice((24, 28, 32, 36, 40, 30))
        if r.random() < 0.08:
            v = 70 + r.randint(0, 20)        # ash specks
        return (clamp(v * 1.05), clamp(v * 0.95), clamp(v * 0.9), 255)
    block_tex("scorched_earth", scorched, seed=5)

    def charred_side(x, y, r):
        # bark split in long cracks, charred black, a few lighter ash rings
        line = (x * 5 + (y // 5)) % 4 == 0
        v = 18 + r.randint(0, 10) - (8 if line else 0)
        if r.random() < 0.05:
            v = 64
        return (clamp(v * 1.05), clamp(v * 0.95), clamp(v * 0.9), 255)
    block_tex("charred_log", charred_side, seed=6)

    def charred_top(x, y, r):
        d = math.hypot(x - 7.5, y - 7.5)
        if d > 7:
            v = 20 + r.randint(0, 8)
        else:
            v = 40 + 18 * (int(d) % 2) + r.randint(-6, 6)
        return (clamp(v * 1.05), clamp(v * 0.95), clamp(v * 0.88), 255)
    block_tex("charred_log_top", charred_top, seed=7)


def shardglass_icon():
    """16 px: a long dark crystal splinter, a vein of violet light down it"""
    rows = [
        "................",
        "...........aa...",
        "..........abva..",
        ".........abvba..",
        "........abvbba..",
        ".......abvbba...",
        "......abvwba....",
        ".....abvbba.....",
        "....abvbba......",
        "...abwvba.......",
        "...abvbba.......",
        "..abvbba........",
        "..abbba.........",
        "...aaa..........",
        "................",
        "................",
    ]
    pal = {"a": (22, 16, 30), "b": (52, 36, 72), "v": (166, 92, 255), "w": (236, 214, 255)}
    im = Image.new("RGBA", (16, 16))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in pal:
                im.putpixel((x, y), (*pal[ch], 255))
    im.save(A / "textures/item/shardglass.png")


def wj(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=1))


def data():
    for name in ("glassed_ground", "scorched_earth"):
        wj(A / "blockstates" / (name + ".json"), {"variants": {"": {"model": "ashbound:block/" + name}}})
        wj(A / "models/block" / (name + ".json"), {"parent": "minecraft:block/cube_all", "textures": {"all": "ashbound:block/" + name}})
        wj(A / "models/item" / (name + ".json"), {"parent": "ashbound:block/" + name})
    wj(A / "blockstates/charred_log.json", {"variants": {
        "axis=y": {"model": "ashbound:block/charred_log"},
        "axis=z": {"model": "ashbound:block/charred_log", "x": 90},
        "axis=x": {"model": "ashbound:block/charred_log", "x": 90, "y": 90}}})
    wj(A / "models/block/charred_log.json", {"parent": "minecraft:block/cube_column",
                                             "textures": {"end": "ashbound:block/charred_log_top", "side": "ashbound:block/charred_log"}})
    wj(A / "models/item/charred_log.json", {"parent": "ashbound:block/charred_log"})
    wj(A / "models/item/shardglass.json", {"parent": "minecraft:item/generated", "textures": {"layer0": "ashbound:item/shardglass"}})
    # loot: glassed ground gives Shardglass now and then, else crumbles to scorched earth
    lt = D / "ashbound/loot_table/blocks"
    wj(lt / "glassed_ground.json", {"type": "minecraft:block", "pools": [{"rolls": 1, "entries": [{"type": "minecraft:alternatives", "children": [
        {"type": "minecraft:item", "name": "ashbound:shardglass", "conditions": [{"condition": "minecraft:random_chance", "chance": 0.35}]},
        {"type": "minecraft:item", "name": "ashbound:scorched_earth"}]}], "conditions": [{"condition": "minecraft:survives_explosion"}]}]})
    for name in ("scorched_earth", "charred_log"):
        wj(lt / (name + ".json"), {"type": "minecraft:block", "pools": [{"rolls": 1, "entries": [{"type": "minecraft:item", "name": "ashbound:" + name}],
                                                                         "conditions": [{"condition": "minecraft:survives_explosion"}]}]})
    # tags: the right tool for each
    for tag, name in (("mineable/pickaxe", "glassed_ground"), ("mineable/shovel", "scorched_earth"), ("mineable/axe", "charred_log"),
                      ("logs_that_burn", "charred_log")):
        p = D / "minecraft/tags/block" / (tag + ".json")
        t = json.loads(p.read_text()) if p.exists() else {"replace": False, "values": []}
        if "ashbound:" + name not in t["values"]:
            t["values"].append("ashbound:" + name)
        wj(p, t)
    wj(D / "ashbound/recipe/temper_ember_from_shardglass.json", {"type": "minecraft:crafting_shapeless", "category": "misc",
                                                                   "ingredients": [{"item": "ashbound:shardglass"}] * 4,
                                                                   "result": {"id": "ashbound:temper_ember", "count": 1}})
    lang_p = A / "lang/en_us.json"
    lang = json.load(open(lang_p, encoding="utf-8"))
    lang.update({
        "block.ashbound.glassed_ground": "Glassed Ground",
        "block.ashbound.scorched_earth": "Scorched Earth",
        "block.ashbound.charred_log": "Charred Log",
        "item.ashbound.shardglass": "Shardglass",
        "item.ashbound.shardglass.desc": "A splinter of a broken gate's crystal ring. Four make a Temper Ember.",
        "entity.ashbound.meteor_shard": "Gate-Shard",
    })
    json.dump(lang, open(lang_p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    shard()
    blocks()
    shardglass_icon()
    data()
    print("done")
