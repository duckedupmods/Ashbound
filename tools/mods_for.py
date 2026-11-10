"""Moves the mods that only work on a player's game in or out of run/mods: a headless test or a server crashes on them.

    python tools/mods_for.py client     before runClient
    python tools/mods_for.py server     before runGameTestServer or runServer
"""
import os
import shutil
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "run")
MODS, HOLD = os.path.join(ROOT, "mods"), os.path.join(ROOT, "mods-client-only")
CLIENT_ONLY = ("MouseTweaks", "mousetweaks", "TravelersTitles", "sodiumdynamiclights", "sodium-options", "sodiumoptions", "reeses-sodium", "entityculling", "EntityCulling",
               "iris-neoforge", "sodium-neoforge", "YouDied", "youdied", "LegendaryTooltips", "ItemBorders", "Prism-", "FancyToasts", "fancytoasts", "fancy_toasts", "drippy",
               "SubtleEffects", "particlerain", "AmbientSounds", "ImmediatelyFast", "Controlling", "Searchables")


def main():
    want = sys.argv[1]
    os.makedirs(HOLD, exist_ok=True)
    src, dst = (HOLD, MODS) if want == "client" else (MODS, HOLD)
    moved = [f for f in os.listdir(src) if f.endswith(".jar") and f.startswith(CLIENT_ONLY)]
    for f in moved:
        shutil.move(os.path.join(src, f), os.path.join(dst, f))
    print("%s: moved %d, %d jars in run/mods" % (want, len(moved), len(os.listdir(MODS)) - (1 if os.path.isdir(os.path.join(MODS, "native")) else 0)))


if __name__ == "__main__":
    main()
