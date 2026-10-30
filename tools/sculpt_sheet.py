"""Contact sheet of the per-prop preview tiles: python tools/sculpt_sheet.py SHEET"""
import sys
from PIL import Image, ImageDraw
import os
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "renders")
sheet = sys.argv[1]
tiles = open(os.path.join(R, "sculpt_%s_tiles.txt" % sheet)).read().split("\n")
cols = 4
S = 400
rows = (len(tiles) + cols - 1) // cols
out = Image.new("RGB", (cols * S, rows * S), (30, 30, 34))
d = ImageDraw.Draw(out)
for i, t in enumerate(tiles):
    im = Image.open(t).convert("RGB").resize((S, S))
    out.paste(im, ((i % cols) * S, (i // cols) * S))
    d.text(((i % cols) * S + 8, (i // cols) * S + 6), os.path.basename(t)[5:-4], fill=(255, 255, 255))
out.save(os.path.join(R, "sculpt_%s.png" % sheet))
