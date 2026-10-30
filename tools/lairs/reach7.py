"""Walk a dungeon layout from its tp on foot (up only by stairs/slabs, no hopping onto blocks - add
--loose to allow 1-block hops; down 3): prints NO for any mob, chest,
boss or exit it cannot reach.   python tools/reach_check.py ossuary Ossuary"""
import sys, collections
sys.path.insert(0, r'E:\Ashbound\tools')
import importlib
O = importlib.import_module([a for a in sys.argv[1:] if a[0] != '-'][0] if len(sys.argv) > 1 else 'ossuary')
_a = [a for a in sys.argv[1:] if a[0] != '-']
_seed = int(__import__("os").environ.get("SEED", "7"))
T = O.ForgeLair(_a[1], seed=_seed) if _a[0] == "forge_lair" else getattr(O, _a[1] if len(_a) > 1 else 'Ossuary')(seed=_seed)
b = T.build()
B = b.B
SOFT = ("chain", "torch", "soul_fire", "air")
def free(p):
    s = B.get(p)
    if s is None:
        return True
    n = s.split("[")[0].split(":")[-1]
    return n == "air" or any(k in n for k in SOFT if k != "air") or ("trapdoor" in s and "open=true" in s)
def walk(p):
    x, y, z = p
    return free(p) and free((x, y + 1, z)) and not free((x, y - 1, z))
LOOSE = "--loose" in sys.argv
tp = T.marks["tp"]
start = (int(tp[0] // 1), int(tp[1]), int(tp[2] // 1))
seen = {start}
q = collections.deque([start])
while q:
    x, y, z = q.popleft()
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        for dy in (1, 0, -1, -2, -3):
            n = (x + dx, y + dy, z + dz)
            if n in seen:
                continue
            if dy == 1 and (not free((x, y + 2, z)) or not (LOOSE or any(k in (B.get((x + dx, y, z + dz)) or "") for k in ("stairs", "slab")))):
                continue
            if dy < 0 and not all(free((x + dx, y + k, z + dz)) for k in range(dy + 1, 2)):
                continue
            if walk(n):
                seen.add(n); q.append(n)
                break
print("reached", len(seen))
def near(p):
    x, y, z = int(p[0] // 1), int(p[1]), int(p[2] // 1)
    return any((x + a, y + c, z + d) in seen for a in (-1, 0, 1) for d in (-1, 0, 1) for c in (-1, 0, 1))
for i, (kind, p, yaw, decor) in enumerate(T.marks["mobs"]):
    if "wickling" in kind: continue
    print(("ok  " if near(p) else "NO  ") + kind, p)
for k in ("boss", "exit"):
    print(("ok  " if near(T.marks[k]) else "NO  ") + k, T.marks[k])
for p in T.marks["loot"]:
    print(("ok  " if near(p) else "NO  ") + "chest", p)
# lowest z reached
print("min z reached", min(s[2] for s in seen))
