"""The dungeon seen through a sky crack (concept): a gate's first hall cut out of its lair (round its arrival point "tp",
reaching in to -z as it faces north) and exported with its textures for tools/blender/sky_crack.py.
  python tools/sky_dungeon.py <lair> [wide deep tall]  ->  E:/Ashbound/tools/renders/struct/sky_<lair>.obj (+ _tex, _lights)"""
import gzip
import os
import struct
import sys

sys.path.insert(0, "E:/Ashbound/tools")
import structkit as K  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
LAIRS = os.path.join(HERE, "..", "src", "main", "resources", "data", "ashbound", "lair")


def read(name):
    d = gzip.open(os.path.join(LAIRS, name + ".bin")).read()
    assert d[:4] == b"KILN"
    o = [4]

    def take(f, n):
        v = struct.unpack(f, d[o[0]:o[0] + n])
        o[0] += n
        return v

    def text():
        n = take(">H", 2)[0]
        o[0] += n
        return d[o[0] - n:o[0]].decode("utf-8")
    pal = [text() for _ in range(take(">H", 2)[0])]
    pts = {}
    for _ in range(take(">H", 2)[0]):
        k = text()
        pts[k] = take(">ddd", 24)
    blocks = {}
    for _ in range(take(">i", 4)[0]):
        x, y, z, i = take(">hhhH", 8)
        blocks[(x, y, z)] = pal[i]
    return blocks, pts


def main():
    lair = sys.argv[1] if len(sys.argv) > 1 else "gate_crypt"
    wide, deep, tall = (int(v) for v in sys.argv[2:5]) if len(sys.argv) > 4 else (26, 46, 22)
    blocks, pts = read(lair)
    tx, ty, tz = (int(v // 1) for v in pts["tp"])
    # cut just under its roof: the first solid block over the arrival point's neighbourhood, lowest of them
    def solid_at(x, y, z):
        st = blocks.get((x, y, z), "air")
        return st not in ("minecraft:air", "air") and "candle" not in st and "lantern" not in st
    roofs = []
    for dx in range(-6, 7, 3):
        for dz in range(-12, 1, 3):
            for y in range(ty + 2, ty + 60):
                if solid_at(tx + dx, y, tz + dz):
                    roofs.append(y)
                    break
    if roofs:
        tall = min(tall, sorted(roofs)[len(roofs) // 3] - ty - 1)
    print("cut at", tall, "over the floor")
    b = K.Build()
    n = 0
    for (x, y, z), st in blocks.items():
        if abs(x - tx) <= wide and ty - 4 <= y <= ty + tall and tz - deep <= z <= tz + 4 and st not in ("minecraft:air", "air") and "bedrock" not in st:
            # the arrival point at the origin, in Minecraft axes
            b.B[(x - tx, y - ty, z - tz)] = st
            n += 1
    print(lair, "tp", (tx, ty, tz), n, "blocks")
    K.preview(b, "sky_" + lair, {})


main()
