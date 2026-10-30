"""A lineup of the hall's statues in blocks, for checking them before they go in the hall.

    python tools/heroes_preview.py NAME [NAME...]   -> E:/Ashbound/tools/renders/struct/hm_heroes.obj (+ shots)
    blender -b -P E:/Ashbound/tools/blender/preview_struct.py -- hm_heroes front three
"""
import os
import sys

sys.path.insert(0, "E:/Ashbound/tools")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import structkit as K  # noqa: E402
import capital_pair as PR  # noqa: E402

names = sys.argv[1:]
S = K.Build(41)
x = 0
for n in names:
    fig = PR.figure(n)
    xs = [p[0] for p in fig]
    x -= min(xs)
    for (fx, fy, fz), st in fig.items():
        S.put(x + fx, fy + 1, fz, st)
    x += max(xs) + 4
for gx in range(-6, x + 6):
    for gz in range(-10, 10):
        S.put(gx, 0, gz, "polished_deepslate")
mid, h = x / 2, max(p[1] for p in S.B)
K.preview(S, "hm_heroes", {"front": ((mid, h * 0.6, 3.2 * h + x * 0.45), (mid, h * 0.45, 0), 30),
                           "three": ((mid + x * 0.5, h * 0.9, 2.2 * h + x * 0.3), (mid, h * 0.4, 0), 30)},
          sun=(40, -150), sky=(0.55, 0.68, 0.85))
