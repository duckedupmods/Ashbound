"""The Curios slot panel in the Ashbound look (docs/RELICS.md): Curios' own GUI sheets recoloured pixel for pixel, every
shape where it was, its greys turned to charred iron with fine ash grain, its blue and purple accents to ember. Written
to assets/curios/... in our mod, which loads after Curios (neoforge.mods.toml) so ours are the ones drawn.

    python tools/curios_ui.py
"""
import glob
import os
import random
import zipfile

from PIL import Image

GAME = "E:/EFTest/game/"
OUT = GAME + "src/main/resources/assets/curios/textures/gui/curios/"
JAR = glob.glob(os.path.expanduser("~") + "/.gradle/caches/modules-2/files-2.1/maven.modrinth/curios/*/*/curios-*.jar")[0]

# their exact colours -> ours (AshUi: BLACK 050404, LINE 3D3833, EMBER E8742C, EMBER_LT F0A050)
MAP = {
    (198, 198, 198): (43, 37, 34),     # the panel: char
    (139, 139, 139): (22, 18, 16),     # a slot's well
    (85, 85, 85): (17, 14, 12),        # bevel in shadow
    (255, 255, 255): (96, 86, 76),     # bevel in light: worn iron
    (0, 0, 0): (5, 4, 4),              # outline
    (55, 55, 55): (11, 9, 8),          # a slot's shadowed edge
    (43, 43, 43): (30, 25, 22),
    (46, 45, 48): (28, 23, 21),
    (33, 33, 33): (14, 11, 10),
    (115, 115, 115): (61, 56, 51),
    (118, 118, 118): (61, 56, 51),
    (147, 147, 147): (78, 70, 62),
    (130, 139, 192): (232, 116, 44),   # the picked page: ember
    (52, 62, 117): (122, 46, 14),
    (136, 146, 201): (120, 52, 22),    # hovered buttons: a warm glow
    (68, 73, 100): (60, 24, 10),
    (175, 182, 218): (200, 110, 50),
    # the highlighted Curios button: gold -> ember
    (66, 49, 0): (90, 34, 8), (202, 158, 35): (232, 116, 44), (246, 222, 155): (246, 190, 120), (224, 184, 71): (240, 160, 80),
    # the cosmetic toggle's purple -> ember
    (63, 0, 99): (80, 28, 6), (88, 0, 140): (130, 46, 10), (110, 0, 174): (190, 76, 20), (135, 31, 196): (232, 116, 44),
    (191, 119, 234): (246, 180, 110),
}
GRAIN = {(43, 37, 34): 3, (22, 18, 16): 2}   # a little ash grain on the char and in the wells


def lum_fallback(c):
    """a colour not in MAP: onto the char ramp by its brightness"""
    l = (c[0] * 3 + c[1] * 6 + c[2]) / 10 / 255
    return (int(5 + 91 * l), int(4 + 82 * l), int(4 + 72 * l))


def recolour(im, seed):
    rnd = random.Random(seed)
    im = im.convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            c = MAP.get((r, g, b)) or lum_fallback((r, g, b))
            j = GRAIN.get(c, 0)
            if j:
                d = rnd.randint(-j, j)
                c = tuple(max(0, v + d) for v in c)
            px[x, y] = (*c, a)
    return im


def main():
    os.makedirs(OUT, exist_ok=True)
    with zipfile.ZipFile(JAR) as z:
        for name in z.namelist():
            if name.startswith("assets/curios/textures/gui/curios/") and name.endswith(".png"):
                im = Image.open(z.open(name))
                out = recolour(im, name)
                out.save(OUT + os.path.basename(name))
                print("recoloured", os.path.basename(name), im.size)


if __name__ == "__main__":
    main()
