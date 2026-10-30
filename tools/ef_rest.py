"""The biped skeleton standing at rest: Epic Fight's joint offsets as 4x4 rows by joint name. A clip in its format has to
state them, so they're read from its armature. Tools read this and never a clip of theirs (all rights reserved)."""
import glob
import json
import os
import zipfile

JAR = glob.glob(os.path.expanduser("~/.gradle/caches/modules-2/files-2.1/maven.modrinth/epic-fight/21.17.3.1-mc1.21.1-neoforge/*/epic-fight-*-neoforge.jar"))[0]


def rest():
    a = json.loads(zipfile.ZipFile(JAR).read("assets/epicfight/animmodels/entity/biped.json"))["armature"]
    out = {}

    def walk(j):
        t = j["transform"]
        out[j["name"]] = [t[i * 4:i * 4 + 4] for i in range(4)]
        for c in j.get("children", []):
            walk(c)
    walk(a["hierarchy"][0])
    return out
