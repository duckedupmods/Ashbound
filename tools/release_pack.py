"""The two zips for a release, from exactly the mods the game is tested with (run/mods plus the ones build.gradle pulls
from Modrinth for the dev run), one copy of each mod (the newest when two jars carry the same mod id):

  Ashbound-<v>-Friends.zip   mods/ (all of them + the Ashbound jar), shaderpacks/Emberlight, config/iris.properties,
                             READ ME FIRST.txt: unzip over an empty CurseForge/Prism instance's folder
  Ashbound-<v>-Server.zip    mods/ without the client-only ones (mods_for.CLIENT_ONLY, the set the headless tests run,
                             and the ones exaroton choked on), start.sh/.bat, user_jvm_args, server.properties, README

    python tools/release_pack.py            (after ./gradlew jar; writes into E:/EFTest/release)
"""
import glob
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.dirname(HERE)
REL = os.path.join(os.path.dirname(GAME), "release")
sys.path.insert(0, HERE)
import mods_for  # noqa: E402

CACHE = os.path.expanduser("~/.gradle/caches/modules-2/files-2.1/maven.modrinth")
# client-only beyond mods_for's list: what a Linux server (exaroton) refused to start with
SERVER_DROP = mods_for.CLIENT_ONLY + ("Controlling", "Searchables", "notutorial")


def version():
    for line in open(os.path.join(GAME, "gradle.properties"), encoding="utf-8"):
        if line.startswith("mod_version="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no mod_version")


def neo():
    for line in open(os.path.join(GAME, "gradle.properties"), encoding="utf-8"):
        if line.startswith("neo_version="):
            return line.split("=", 1)[1].strip()


def gradle_mods():
    """the runtime mods build.gradle takes from Modrinth (the dev run loads them as well as run/mods)"""
    out = []
    for m in re.finditer(r'^\s*(?:runtimeOnly|implementation)\s+"maven\.modrinth:([^:]+):([^"]+)"', open(os.path.join(GAME, "build.gradle"), encoding="utf-8").read(), re.M):
        jars = [j for j in glob.glob(os.path.join(CACHE, m.group(1), m.group(2), "*", "*.jar")) if "sources" not in j]
        if jars:
            out.append(jars[0])
        else:
            print("  missing from the gradle cache:", m.group(1), m.group(2))
    return out


def ident(jar):
    """(mod id, version, display name) from a jar's mods.toml"""
    try:
        with zipfile.ZipFile(jar) as z:
            names = z.namelist()
            toml = next((n for n in ("META-INF/neoforge.mods.toml", "META-INF/mods.toml") if n in names), None)
            if toml is None:
                return None
            t = z.read(toml).decode("utf-8", "replace")
            # either quote, a [[mods]] table or an inline one (Modrinth's datapack jars: Dungeons and Taverns)
            mid = re.search(r'modId\s*=\s*["\']([^"\']+)["\']', t)
            ver = re.search(r'(?:^|[\s,{])version\s*=\s*["\']([^"\']+)["\']', t[mid.start():] if mid else t, re.M)
            v = ver.group(1) if ver else "0"
            if "${" in v and "META-INF/MANIFEST.MF" in names:
                mf = re.search(r"Implementation-Version:\s*(\S+)", z.read("META-INF/MANIFEST.MF").decode("utf-8", "replace"))
                v = mf.group(1) if mf else v
            return mid.group(1) if mid else None, v
    except zipfile.BadZipFile:
        return None


def vkey(v):
    return [int(x) if x.isdigit() else x for x in re.split(r"[.+\-_]", v)] if v else []


def collect():
    """{mod id: (jar path, name in the zip)}: run/mods first, a gradle copy only if it's newer"""
    mods = {}
    for jar in sorted(glob.glob(os.path.join(mods_for.MODS, "*.jar")) + glob.glob(os.path.join(mods_for.HOLD, "*.jar"))):
        i = ident(jar)
        key = i[0] if i and i[0] else os.path.basename(jar)
        mods[key] = (jar, os.path.basename(jar), i[1] if i else "")
    for jar in gradle_mods():
        i = ident(jar)
        if not i or not i[0]:
            print("  no mod id in", jar)
            continue
        mid, v = i
        name = "%s-%s.jar" % (mid, v)
        if mid in mods:
            try:
                newer = vkey(v) > vkey(mods[mid][2])
            except TypeError:
                newer = False
            if not newer:
                continue
        mods[mid] = (jar, name, v)
    return mods


FRIENDS_README = """Ashbound {v}: everything for the friends' game

1. Make a NEW, empty instance for Minecraft 1.21.1 on NeoForge {neo} (CurseForge: Create Custom Profile; Prism works too).
2. Open its folder (CurseForge: right-click the profile > Open Folder).
3. Unzip everything in this zip into that folder, so mods, shaderpacks and config land in it.
4. Give it about 8 GB of memory (CurseForge settings > Minecraft > Java Settings) and start it.

This zip holds every mod the game is tested with ({n} jars), so don't add the old Emberfall mods on top.
Emberlight shaders are on; K turns them off and on.
Everyone on the server has to be on Ashbound {v}, and the server needs a NEW world.
"""

SERVER_README = """Ashbound server pack {v}
Minecraft 1.21.1, NeoForge {neo}, Java 21, about 8 GB of memory.

On your own machine:
  1. Unzip into an empty folder.
  2. Run start.sh (Linux) or start.bat (Windows). The first run stops and asks you to accept the EULA.
  3. Read https://aka.ms/MinecraftEULA, set eula=true in eula.txt, run it again.

On a host (exaroton and the like): pick NeoForge {neo} for Minecraft 1.21.1, delete the old mods folder, upload this
mods folder and server.properties, and start it.

Start a NEW world. Client-only mods are left out on purpose: players get them from the friends zip.
"""

START_SH = """#!/bin/sh
# First run installs NeoForge {neo} here, every run starts the server. Needs Java 21.
if [ ! -f run.sh ]; then
  curl -fL -o neoforge-installer.jar "https://maven.neoforged.net/releases/net/neoforged/neoforge/{neo}/neoforge-{neo}-installer.jar" || exit 1
  java -jar neoforge-installer.jar --install-server || exit 1
  rm -f neoforge-installer.jar
fi
exec sh run.sh nogui
"""

START_BAT = """@echo off
rem First run installs NeoForge {neo} here, every run starts the server. Needs Java 21.
if not exist run.bat (
  curl -fL -o neoforge-installer.jar "https://maven.neoforged.net/releases/net/neoforged/neoforge/{neo}/neoforge-{neo}-installer.jar" || exit /b 1
  java -jar neoforge-installer.jar --install-server || exit /b 1
  del neoforge-installer.jar
)
call run.bat nogui
"""

IRIS = """enableShaders=true
shaderPack=Ashbound-Emberlight-1.0.zip
allowUnknownShaders=false
colorSpace=SRGB
disableUpdateMessage=false
enableDebugOptions=false
maxShadowRenderDistance=32
"""


def main():
    v, nv = version(), neo()
    ours = os.path.join(GAME, "build", "libs", "ashbound-%s.jar" % v)
    if not os.path.exists(ours):
        raise SystemExit("build the jar first: " + ours)
    mods = collect()
    names = sorted(mods.values(), key=lambda m: m[1].lower())
    server = [m for m in names if not m[1].startswith(SERVER_DROP)]
    shader = os.path.join(REL, "Ashbound-Emberlight-1.0.zip")
    friends_zip = os.path.join(REL, "Ashbound-%s-Friends.zip" % v)
    with zipfile.ZipFile(friends_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        z.write(ours, "mods/ashbound-%s.jar" % v)
        for jar, name, _ in names:
            z.write(jar, "mods/" + name)
        z.write(shader, "shaderpacks/Ashbound-Emberlight-1.0.zip")
        z.writestr("config/iris.properties", IRIS)
        z.writestr("READ ME FIRST.txt", FRIENDS_README.format(v=v, neo=nv, n=len(names) + 1))
    server_zip = os.path.join(REL, "Ashbound-%s-Server.zip" % v)
    with zipfile.ZipFile(server_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        z.write(ours, "mods/ashbound-%s.jar" % v)
        for jar, name, _ in server:
            z.write(jar, "mods/" + name)
        for n, text in (("start.sh", START_SH), ("start.bat", START_BAT), ("README.txt", SERVER_README)):
            zi = zipfile.ZipInfo(n)
            zi.external_attr = (0o755 if n == "start.sh" else 0o644) << 16
            z.writestr(zi, text.format(v=v, neo=nv))
        z.writestr("user_jvm_args.txt", "-Xms4G\n-Xmx8G\n")
        z.writestr("server.properties", "allow-flight=true\nmax-tick-time=-1\nmotd=Ashbound\n")
    with open(os.path.join(REL, "MODS-%s.txt" % v), "w", encoding="utf-8") as f:
        f.write("Ashbound %s: %d mods for players, %d on the server (+ Ashbound itself)\n\n" % (v, len(names), len(server)))
        for jar, name, _ in names:
            f.write(("    " if (jar, name, _) in server else "  C ") + name + "\n")
        f.write("\nC = client only, left out of the server pack\n")
    for p in (friends_zip, server_zip):
        print("%s  %.0f MB" % (p, os.path.getsize(p) / 1e6))
    print("players: %d mods, server: %d mods (+ ashbound)" % (len(names), len(server)))


if __name__ == "__main__":
    main()
