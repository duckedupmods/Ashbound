"""pose each Legend at the height of its roar for the wanted-poster portrait; writes <name>_portrait_f0.obj/png"""
import sys
sys.path.insert(0, "E:/EFTest/game/tools")
import beastkit as B

ROAR = {"rime_penitent": "toll", "old_blackbriar": "crows", "red_plough": "bellow", "sunbreaker": "glare",
        "grandmother_mire": "cackle", "hollow_smile": "giggle", "old_harpoon": "tide", "walking_mountain": "quake"}
for name, c in ROAR.items():
    m = B.mod(name)
    s0, _ = m.make(name, False)
    lo = B.floor_of(s0)
    clip = m.CLIPS[c]
    ev = clip.get("events", {})
    t = (ev.get("roar") or ev.get("rain") or [clip["len"] * 0.4])[0]
    s, parts = B.posed(name, False, clip, t)
    B.preview_at(s, name + "_portrait", lo)
    tall, long_ = B.height(s0)
    print("%s@%.2f" % (name + "_portrait", max(tall, long_ * 0.62)))
