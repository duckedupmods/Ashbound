"""The CurseForge modpack zip for Ashbound Emberfall, without the app: manifest.json pointing at each mod's CurseForge file,
modlist.html, and overrides (the Emberlight shader pack, switched on). Built from the app profile's own list
(Instances/Ashbound Emberfall/minecraftinstance.json) plus the mods that were only ever copied in by hand, at the exact
versions the game is tested with. Mods with no NeoForge 1.21.1 file on CurseForge (Noisium: archived; Spelunkery:
Modrinth only) are left out, and the server pack made here leaves them out too so players can join.

    python tools/cf_pack.py <Ashbound's CurseForge file ID> [pack version]
        -> E:/EFTest/release/Ashbound-Emberfall-<v>.zip and Ashbound-Emberfall-<v>-Server.zip

The file ID is the number at the end of the Ashbound 1.0.x file's page URL on CurseForge (the file must be approved first).
"""
import html
import json
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.dirname(HERE)
REL = os.path.join(os.path.dirname(GAME), "release")
PROFILE = os.path.expanduser("~/curseforge/minecraft/Instances/Ashbound Emberfall/minecraftinstance.json")
ASHBOUND = 1775193
NEO = "21.1.264"
DROP = {930207: "Noisium (archived on CurseForge)", 790530: "Spelunkery (no NeoForge 1.21.1 file on CurseForge)"}
DROP_JARS = ("noisium", "spelunkery")

# copied into the profile by hand, never linked: the CurseForge file of the exact version we test (looked up 11/10)
EXTRA = [
    ("Biomes O' Plenty", 220318, 8288121), ("TerraBlender (NeoForge)", 940057, 6054947), ("GlitchCore", 955399, 8109792),
    ("EpicFight-Extra", 1434276, 8681592), ("EpheroLib", 885449, 5872111), ("Kotlin for Forge", 351264, 8335665),
    ("[Let's Do] Camping", 1072398, 9205308), ("[Let's Do] Alpine Whispers", 1399928, 9149574),
    ("Controlling", 250398, 6368976), ("Searchables", 858542, 5831692),
]

IRIS = """enableShaders=true
shaderPack=Ashbound-Emberlight-1.0.zip
allowUnknownShaders=false
colorSpace=SRGB
disableUpdateMessage=false
enableDebugOptions=false
maxShadowRenderDistance=32
"""


def main():
    if len(sys.argv) < 2 or not sys.argv[1].isdigit():
        raise SystemExit(__doc__)
    ash_file, version = int(sys.argv[1]), sys.argv[2] if len(sys.argv) > 2 else "1.1.0"
    prof = json.load(open(PROFILE, encoding="utf-8"))
    mods = {}
    for a in prof["installedAddons"]:
        pid, f = a["addonID"], a.get("installedFile") or {}
        if pid in DROP or pid == ASHBOUND or not f.get("id"):
            continue
        mods[pid] = (a.get("name") or f.get("displayName") or str(pid), f["id"])
    for name, pid, fid in EXTRA:
        mods[pid] = (name, fid)
    mods[ASHBOUND] = ("Ashbound", ash_file)
    manifest = {
        "minecraft": {"version": "1.21.1", "modLoaders": [{"id": "neoforge-" + NEO, "primary": True}]},
        "manifestType": "minecraftModpack",
        "manifestVersion": 1,
        "name": "Ashbound Emberfall",
        "version": version,
        "author": "Ducked Up Mods",
        "files": [{"projectID": pid, "fileID": fid, "required": True} for pid, (_, fid) in sorted(mods.items(), key=lambda m: m[1][0].lower())],
        "overrides": "overrides",
    }
    rows = "\n".join('<li><a href="https://www.curseforge.com/projects/%d">%s</a></li>' % (pid, html.escape(n))
                     for pid, (n, _) in sorted(mods.items(), key=lambda m: m[1][0].lower()))
    out = os.path.join(REL, "Ashbound-Emberfall-%s.zip" % version)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("manifest.json", json.dumps(manifest, indent=2))
        z.writestr("modlist.html", "<ul>\n" + rows + "\n</ul>\n")
        z.write(os.path.join(REL, "Ashbound-Emberlight-1.0.zip"), "overrides/shaderpacks/Ashbound-Emberlight-1.0.zip")
        z.writestr("overrides/config/iris.properties", IRIS)
    print(out, "%d mods" % len(mods), "%.1f MB" % (os.path.getsize(out) / 1e6))
    # the server pack to go with it: the release server zip without what the pack leaves out
    mv = [l.split("=", 1)[1].strip() for l in open(os.path.join(GAME, "gradle.properties"), encoding="utf-8") if l.startswith("mod_version=")][0]
    src = os.path.join(REL, "Ashbound-%s-Server.zip" % mv)
    dst = os.path.join(REL, "Ashbound-Emberfall-%s-Server.zip" % version)
    kept = dropped = 0
    with zipfile.ZipFile(src) as zi, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zo:
        for info in zi.infolist():
            base = os.path.basename(info.filename).lower()
            if info.filename.startswith("mods/") and base.startswith(DROP_JARS):
                dropped += 1
                continue
            zo.writestr(info, zi.read(info.filename))
            kept += info.filename.startswith("mods/") and base.endswith(".jar")
        zo.writestr("VERSION.txt", "Ashbound Emberfall %s server pack (Ashbound %s, NeoForge %s)\n" % (version, mv, NEO))
    print(dst, "%d mods (dropped %d)" % (kept, dropped), "%.0f MB" % (os.path.getsize(dst) / 1e6))
    for pid, why in DROP.items():
        print("  left out:", why)


if __name__ == "__main__":
    main()
