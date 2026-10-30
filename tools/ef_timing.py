"""How fast Epic Fight's combo swings really hit (for tools/balance.py). Reads Epic Fight's own jar: each attack
animation's phases (pre-delay, contact, recovery), its BASIS_ATTACK_SPEED / ATTACK_SPEED_FACTOR, damage modifiers, and
its length from the animation json. Epic Fight plays an attack at

    speed = 1 + (s - 1) * factor,  s = attack_speed / basis   (with a basis)   or   length * attack_speed   (without)

so a swing you can follow up at `recovery` (animation seconds) takes recovery / speed real seconds.

    python tools/ef_timing.py     # writes tools/ef_timing.json + prints a table
"""
import json
import re
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tools/ef_timing.json"
JAR = next((Path.home() / ".gradle/caches/modules-2/files-2.1/maven.modrinth/epic-fight").rglob("epic-fight-*-neoforge.jar"))
JAVAP = next(Path("E:/EFTest/jdk").glob("*/bin/javap.exe"))

# the combos each of our weapon types runs (Movesets.java and Epic Fight's presets); dash and air attacks left out
COMBOS = {
    "sword": ["SWORD_AUTO1", "SWORD_AUTO2", "SWORD_AUTO3"],
    "sword_dual": ["SWORD_DUAL_AUTO1", "SWORD_DUAL_AUTO2", "SWORD_DUAL_AUTO3"],
    "dagger": ["DAGGER_AUTO1", "DAGGER_AUTO2", "DAGGER_AUTO3"],
    "dagger_dual": ["DAGGER_DUAL_AUTO1", "DAGGER_DUAL_AUTO2", "DAGGER_DUAL_AUTO3", "DAGGER_DUAL_AUTO4"],
    "spear": ["SPEAR_TWOHAND_AUTO1", "SPEAR_TWOHAND_AUTO2"],
    "spear_1h": ["SPEAR_ONEHAND_AUTO"],
    "greatsword": ["GREATSWORD_AUTO1", "GREATSWORD_AUTO2"],
    "titan": ["SWORD_DUAL_AUTO1", "SWORD_DUAL_AUTO2", "SWORD_DUAL_AUTO3"],  # Titan's Grip: the dual swords' moves
}


def bytecode():
    return subprocess.run([str(JAVAP), "-v", "-c", "-p", "-cp", str(JAR), "yesman.epicfight.gameasset.Animations"],
                          capture_output=True, text=True, encoding="utf-8", errors="replace").stdout


def parse(t):
    bs = {int(m.group(1)): m.group(2) for m in re.finditer(
        r"^\s*(\d+): #\d+ REF_invokeStatic java/lang/invoke/LambdaMetafactory\.metafactory.*?\n\s*Method arguments:\n\s*#\d+ [^\n]*\n"
        r"\s*#\d+ REF_invokeStatic [^.]+\.(lambda\$[\w$]+)", t, re.M | re.S)}
    fields = {}
    for path, k, field in re.findall(r"String (biped/[\w/]+)\n\s*\d+: invokedynamic #\d+,\s+0\s+// InvokeDynamic #(\d+):apply[^\n]*\n"
                                     r"[^\n]*nextAccessor[^\n]*\n\s*\d+: putstatic[^/]*// Field (\w+):", t):
        fields[field] = (path, bs.get(int(k)))
    return fields


def body(t, lam):
    i = t.find(f" {lam}(yesman")
    j = t.find("LineNumberTable", i)
    return t[i:j]


def length(path):
    with zipfile.ZipFile(JAR) as z:
        d = json.loads(z.read(f"assets/epicfight/animmodels/animations/{path}.json"))
    return max(max(j["time"]) for j in d["animation"])


def info(t, fields, name):
    path, lam = fields[name]
    b = body(t, lam)
    # every float in order, and what each property / phase call takes
    toks = re.findall(r"(?:ldc[_w]*\s+#\d+\s+// float ([-\d.E]+)f|fconst_(\d)|(BASIS_ATTACK_SPEED|ATTACK_SPEED_FACTOR|DAMAGE_MODIFIER)"
                      r"|AttackAnimation\$Phase\.\"<init>\"|(multiplier)|(\"<init>\"))", b)
    floats, basis, factor, dmg, phases = [], None, 1.0, [], 0
    pending = None
    for f1, f2, prop, mult, init in toks:
        if f1 or f2:
            v = float(f1 or f2)
            if pending in ("BASIS_ATTACK_SPEED", "ATTACK_SPEED_FACTOR"):
                if pending == "BASIS_ATTACK_SPEED":
                    basis = v
                else:
                    factor = v
                pending = None
            else:
                floats.append(v)
        elif prop:
            pending = prop
        elif mult and floats:
            dmg.append(floats.pop())
    T = length(path)
    # built from phases: (transition, Phase(start, antic, pre-delay, contact, recovery, end) or Phase(start, antic,
    # contact, recovery, end) per hit); else (transition, antic, contact, recovery) or a dash's (.., pre-delay, ..)
    phase_args = [d.count("F") for d in re.findall(r'AttackAnimation\$Phase\."<init>":\((F+)', b)]
    if phase_args:
        phases, k, recovery = len(phase_args), 1, T
        for n in phase_args:
            recovery = floats[k + (4 if n == 6 else 3)]
            k += n
    else:
        n = re.search(r'Animation\."<init>":\((F+)', b).group(1).count("F")
        phases, recovery = 1, floats[n - 1]
    return {"path": path, "length": round(T, 4), "basis": basis, "factor": factor, "recovery": recovery,
            "phases": phases, "damage": dmg or [1.0], "floats": floats[:12]}


def play_speed(a, attack_speed):
    s = attack_speed / a["basis"] if a["basis"] else a["length"] * attack_speed
    return 1 + (s - 1) * a["factor"]


def combo_rate(anims, attack_speed):
    """(hits per second, damage multiplier per hit) spamming the combo"""
    secs = sum(a["recovery"] / play_speed(a, attack_speed) for a in anims)
    hits = sum(a["phases"] for a in anims)
    dmg = sum(sum(a["damage"]) / len(a["damage"]) * a["phases"] for a in anims) / hits
    return hits / secs, dmg


def main():
    t = bytecode()
    fields = parse(t)
    data = {}
    for combo, names in COMBOS.items():
        data[combo] = [info(t, fields, n) | {"name": n} for n in names]
    OUT.write_text(json.dumps(data, indent=1), encoding="utf-8")
    for combo, anims in data.items():
        for a in anims:
            print(f"{combo:12} {a['name']:20} len {a['length']:.2f}  recovery {a['recovery']:.2f}  basis {a['basis']}  "
                  f"factor {a['factor']}  phases {a['phases']}  dmg {a['damage']}  floats {a['floats'][:6]}")


if __name__ == "__main__":
    main()
