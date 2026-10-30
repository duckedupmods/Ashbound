"""Render monsterforge previews in Blender (background) and lay them out on one sheet.

    python tools/mobsheet.py <gate|name...> [--side] [--out path.png]
    (run python tools/monsterforge.py <same> --preview first)
"""
import os
import subprocess
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, 'E:/Ashbound/tools')
import forge_specs as FS  # noqa: E402

BLENDER = "E:/Steam/steamapps/common/Blender/blender.exe"
VOX = "E:/Ashbound/tools/renders/vox/"
SHEETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "renders", "mobs")


def height(n):
    s = FS.SPECS[n]
    if "ent" in s:
        return max(2.0 if s.get("rig") else 1.4, s["ent"][1])
    if s.get("rig") in ("crawler", "beast"):
        return max(1.2, 2.0 * s.get("size", 1.0))
    return 2.9 * s.get("build", {}).get("size", 1.0)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
    if out in args:
        args.remove(out)
    names = []
    for a in args:
        names += FS.by_gate(a) if a in FS.GATES else [a]
    subprocess.run([BLENDER, "-b", "-P", "E:/Ashbound/tools/blender/preview_mob.py", "--"] +
                   ["%s@%.1f" % (n, height(n)) for n in names], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    views = ["threequarter"] + (["side"] if "--side" in sys.argv else ["front"])
    ims = [[Image.open(VOX + "%s_%s.png" % (n, v)).convert("RGBA") for n in names] for v in views]
    w, h = ims[0][0].size
    sheet = Image.new("RGB", (w * len(names), h * len(views)), (40, 44, 52))
    for r, row in enumerate(ims):
        for c, im in enumerate(row):
            sheet.paste(im, (c * w, r * h), im)
    os.makedirs(SHEETS, exist_ok=True)
    path = out or os.path.join(SHEETS, "%s.png" % ("_".join(args)[:60]))
    sheet.resize((w * len(names) // 2, h * len(views) // 2)).save(path)
    print(path)


if __name__ == "__main__":
    main()
