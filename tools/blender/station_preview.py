"""The three Trades stations (tools/stationprops.py) as the game draws them, through sculpt_preview's renderer: one block
each, its own model file. Tiles in tools/renders/tile_<id>.png, joined into tools/renders/stations_mc.png.
    blender -b -P tools/blender/station_preview.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "sculpt_preview.py"), encoding="utf-8").read()
src = src.replace('PIECES = json.load(open(os.path.join(GAME, "tools", "renders", "sculpt_pieces.json")))',
                  'PIECES = {n: {"size": [1, 1, 1], "pieces": [[0, 0, 0, 0]]} for n in ("cooks_fire", "brewers_cask", "alchemists_bench")}')
src = src.replace('"%s_%d.json" % (name, idx)', '"%s.json" % name')
src = src.replace("\nmain()\n", "\n")
sys.argv = [sys.argv[0], "--", "stations", "cooks_fire", "brewers_cask", "alchemists_bench"]
exec(compile(src, "sculpt_preview.py", "exec"))
main()
