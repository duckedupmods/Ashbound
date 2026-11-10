"""Hand-drawn 16x16 item icons: each is a pixel grid and a palette, built by Aseprite into a layered-free sprite
(tools/icons_hand/<id>.aseprite + .png), and tools/renders/icon_test/hand.png shows them big and in a slot.
Nothing goes in the game until it's asked for.

    python tools/handicons.py [item...]
"""
import json
import os
import subprocess
import sys

from PIL import Image

GAME = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ASEPRITE = "E:/Steam/steamapps/common/Aseprite/Aseprite.exe"
OUT = os.path.join(GAME, "tools/icons_hand")
TEST = os.path.join(GAME, "tools/renders/icon_test")
ITEMS = os.path.join(GAME, "src/main/resources/assets/ashbound/textures/item")

ICONS = {
    "kiln_blade": ({"o": "4a2c38", "O": "2a1a24", "h": "e0d6e0", "s": "968a98", "m": "625868", "d": "3f3744", "y": "ffe27a", "e": "ff9a1e", "r": "c8400e", "g": "f2c14e", "G": "a8701f", "w": "5c2f22", "W": "8a4e34"}, [
        ".............ooo",
        "............ohyo",
        "...........ohyeo",
        "..........ohsero",
        ".........ohsrdo.",
        "........ohsedo..",
        ".......ohmrdo...",
        "......ohsedo....",
        ".....ohmrdo.....",
        "..oo.ohedo......",
        ".oggoohdo.......",
        ".oGggmdo........",
        "..ooGggo........",
        "..oWooGo........",
        ".oWwo.oo........",
        "oyeo............",
    ]),
    "kilnplate_helm": ({"o": "3a2c3c", "h": "c4b8c0", "s": "8c808c", "m": "5e5260", "d": "403644", "y": "ffe27a", "e": "ff9a1e", "r": "c8400e", "g": "f2c14e", "G": "a8701f"}, [
        "..oo........oo..",
        ".oyeo......oeyo.",
        ".osmo......osdo.",
        ".ohmo.oooo.osdo.",
        "..ohoohhssoosdo.",
        "..ohhsssssmmdo..",
        ".ogggggGgGgGGGo.",
        ".ohsmmmmmmmmddo.",
        "ohsooooooooooddo",
        "ohsoyoyoyoyooddo",
        "ohmoeoeoeoeooddo",
        "ohmorororoeooddo",
        ".omoooooooooodo.",
        ".oGgo......oGGo.",
        "..ooo......ooo..",
        "................",
    ]),
    "snowshroud_robe": ({"o": "54507e", "w": "ffffff", "f": "dfe5f2", "c": "aeb8d4", "b": "7f8db5", "r": "e8483a", "R": "a82838", "y": "ffe27a", "g": "f2c14e", "G": "a8701f"}, [
        "................",
        "..oooo....oooo..",
        ".owwwfoooofccbo.",
        "owwffcRrrRccbbbo",
        "offcocryyrcocbbo",
        "ooooofryyrcooooo",
        "....owfrrRco....",
        "....owfRRRco....",
        "....oGgGgGGo....",
        "...owwfccbbbo...",
        "...owfwccbcbo...",
        "..owfwfccbcbbo..",
        "..owwfcfcbcbbo..",
        ".owwffcfccbcbbo.",
        ".oRrrrrrRRRRRRo.",
        "..oooooooooooo..",
    ]),
}

LUA = r'''
local items = json.decode(io.open(app.params["spec"]):read("a"))
for _, it in ipairs(items) do
  local spr = Sprite(16, 16, ColorMode.RGB)
  local img = Image(16, 16, ColorMode.RGB)
  for _, p in ipairs(it.px) do
    img:drawPixel(p[1], p[2], app.pixelColor.rgba(p[3], p[4], p[5], 255))
  end
  spr:newCel(spr.layers[1], 1, img, Point(0, 0))
  spr.layers[1].name = "icon"
  spr:saveAs(it.ase)
  spr:saveCopyAs(it.png)
  spr:close()
end
'''


def rgb(h):
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def main():
    names = sys.argv[1:] or list(ICONS)
    os.makedirs(OUT, exist_ok=True)
    spec = []
    for n in names:
        pal, rows = ICONS[n]
        if len(rows) != 16 or any(len(r) != 16 for r in rows):
            raise SystemExit("%s: bad grid %s" % (n, [len(r) for r in rows]))
        px = [[x, y, *rgb(pal[c])] for y, r in enumerate(rows) for x, c in enumerate(r) if c != "."]
        spec.append({"ase": os.path.join(OUT, n + ".aseprite"), "png": os.path.join(OUT, n + ".png"), "px": px})
    sp, lua = os.path.join(OUT, "_spec.json"), os.path.join(OUT, "_build.lua")
    json.dump(spec, open(sp, "w"))
    open(lua, "w").write(LUA)
    r = subprocess.run([ASEPRITE, "-b", "--script-param", "spec=" + sp, "--script", lua], capture_output=True, text=True)
    if r.returncode or r.stdout.strip() or r.stderr.strip():
        print("aseprite:", r.returncode, r.stdout[-500:], r.stderr[-500:])
    tile, bar = 192, 72
    sheet = Image.new("RGBA", (len(names) * (tile * 2 + 12) + 12, tile + bar + 24), (139, 139, 139, 255))
    for i, n in enumerate(names):
        x = 12 + i * (tile * 2 + 12)
        new = Image.open(os.path.join(OUT, n + ".png")).convert("RGBA")
        big = new.resize((tile, tile), Image.NEAREST)
        sheet.paste(big, (x, 8), big)
        old = os.path.join(ITEMS, n + ".png")
        if os.path.exists(old):
            o = Image.open(old).convert("RGBA").resize((tile, tile), Image.NEAREST)
            sheet.paste(o, (x + tile, 8), o)
        slot = new.resize((48, 48), Image.NEAREST)
        sheet.paste(slot, (x + 12, tile + 20), slot)
    sheet.save(os.path.join(TEST, "hand.png"))
    print("drew", names)


if __name__ == "__main__":
    main()
