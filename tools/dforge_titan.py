"""The Fallen Titan (B): the gate opens inside a giant who fell before the age of men - the Maw between its teeth,
the Throat spiralling down, the Lungs and the bronchi between them, the Rib Cathedral, the Stomach's acid lake, the
Spine Road to the valve door, and the Heart Chamber where the Still Heart hangs. Raw muscle, pale sinew, yellow fat,
ivory rib and bile-green. dforge.py imports this."""
from blockforge import R
from dforge import dungeon, B, Pp, common_props

MUSCLE = R("#2a0606", "#420a0a", "#5e1010", "#7a1a18", "#962822", "#ae3a2e")
SINEW = R("#5a4a3e", "#76645a", "#92806e", "#ae9c88", "#c8b8a2", "#e0d2bc")
FAT = R("#4a3a10", "#6a5418", "#8a7024", "#a88c34", "#c4a84a")
BONE = R("#4a4436", "#6a6250", "#8a826a", "#aaa286", "#c8c0a4", "#e2dcc4")
BONE_M = R("#2a2418", "#3a3222", "#4a402c")
CART = R("#4a5458", "#646e72", "#7e888c", "#9aa2a4", "#b4bcbc")
BILE = R("#1a4a0a", "#2a7010", "#44a018", "#78d030", "#b8f080")
BLOOD = R("#5a0408", "#8a0a10", "#c01a1a", "#ee3a2a", "#ff7a5a")
GUM = R("#3a1418", "#5a2026", "#7a3038", "#9a4448", "#b45c5c")
DARKFLESH = R("#120202", "#1e0404", "#2a0808", "#380c0c", "#461212")

dungeon("fallen_titan",
        blocks=[
            B("titan_muscle", "Titan Muscle", "strata", "minecraft:mud", tool="shovel", args=dict(ramp=MUSCLE, bands=6)),
            B("titan_sinew_wall", "Titan Sinew Wall", "planks", "minecraft:mushroom_stem", tool="axe", args=dict(ramp=SINEW, n=8, vertical=True)),
            B("titan_fat", "Titan Fat", "rock", "minecraft:honeycomb_block", tool="shovel", args=dict(ramp=FAT, spread=0.6)),
            B("titan_gum", "Titan Gum", "rock", "minecraft:mud", tool="shovel", args=dict(ramp=GUM, spread=0.5)),
            B("titan_bone", "Titan Bone", "ashlar", "minecraft:bone_block", args=dict(ramp=BONE, mortar=BONE_M)),
            B("rib_bone", "Titan Rib", "column", "minecraft:bone_block", args=dict(ramp=BONE, mortar=BONE_M, flutes=3)),
            B("cartilage", "Cartilage Plates", "bricks", "minecraft:calcite", family=("stairs", "slab", "wall"), stem="cartilage",
              stem_title="Cartilage", args=dict(ramp=CART, mortar=BONE_M, rows=3, run=6)),
            B("cartilage_flags", "Cartilage Floor", "flags", "minecraft:calcite", family=("slab",), stem="cartilage_flag",
              stem_title="Cartilage Floor", args=dict(ramp=CART, grout=BONE_M)),
            B("bile_glow", "Bile Bladder", "glow", "minecraft:verdant_froglight", light=11, args=dict(ramp=BILE, base=FAT, motif="vein")),
            B("artery_wall", "Artery Wall", "glow", "minecraft:redstone_lamp", light=9, args=dict(ramp=BLOOD, base=MUSCLE, motif="vein")),
            B("dead_flesh", "Dead Flesh", "rock", "minecraft:mud", tool="shovel", args=dict(ramp=DARKFLESH, spread=0.5)),
        ],
        props=common_props("titan", "Titan", metal_color="color_red", wood_color="color_red") + [
            Pp("breathing_sac", "plain", "Breathing Sac", box=[1, 0, 1, 15, 14, 15], sound="slime_block", color="color_pink",
               strength=1, light=6),
            Pp("rib_spur", "plain", "Rib Spur", box=[2, 0, 2, 14, 16, 14], sound="bone_block", color="sand", strength=2, solid=False),
            Pp("eaten_armour", "plain", "Eaten Armour", box=[0, 0, 0, 16, 8, 16], sound="metal", color="metal", strength=2),
            Pp("artery_root", "plain", "Artery Root", box=[3, 0, 3, 13, 16, 13], sound="slime_block", color="color_red",
               strength=1.5, light=5, solid=False),
        ],
        seal_words="A clot of flesh seals the valve door", broken_words="The clot tears and the valve opens",
        layout=dict(
            palette=dict(
                hall_floor=[("cartilage_flags", 3), ("titan_bone", 1)], hall_wall=[("titan_muscle", 4), ("titan_sinew_wall", 2),
                                                                                    ("artery_wall", 1)],
                hall_ceil=[("titan_muscle", 2), ("titan_sinew_wall", 1)],
                cave_floor=[("titan_gum", 3), ("titan_fat", 2)], cave_wall=[("titan_muscle", 4), ("titan_fat", 2), ("dead_flesh", 1)],
                cave_ceil=[("titan_muscle", 3), ("dead_flesh", 1)],
                arena_floor=[("cartilage_flags", 2), ("titan_muscle", 2)], arena_wall=[("titan_muscle", 3), ("artery_wall", 2),
                                                                                       ("titan_sinew_wall", 1)],
                bridge=[("cartilage_flags", 1)], rail="cartilage_wall",
                fill="dead_flesh", pillar="rib_bone", stairs="cartilage_stairs", slab="cartilage_slab",
                lamp="titan_lantern", chain="titan_chain", bars="titan_bars", coffer="titan_coffer", vein="bile_glow"),
            seal=6, lamp_every=7, lamp_height=6, veins=0.04,
            rooms=[
                dict(name="the maw", kind="cave", w=29, len=30, h=16,
                     dress=[("clusters", dict(name="rib_spur", chance=0.03))], mobs=[("burrow_leech", 5)]),
                dict(name="the throat", kind="descent", to=-10, gap=6),
                dict(name="the lungs", kind="chasm", w=33, len=40, h=16, drop=14, mobs=[("sinew_stalker", 3), ("burrow_leech", 3)]),
                dict(name="the rib cathedral", kind="hall", w=31, len=44, h=20, chest=True,
                     dress=[("frames", dict(every=5)), ("clusters", dict(name="rib_spur", chance=0.02))],
                     mobs=[("marrow_brute", 2), ("sinew_stalker", 2)]),
                dict(name="the stomach", kind="cave", w=35, len=40, h=18, chest=True,
                     dress=["pools", ("scatter", dict(name="eaten_armour", n=8))],
                     mobs=[("bile_priest", 3), ("burrow_leech", 4)], decor=[("burrow_leech", 2)]),
                dict(name="the spine road", kind="hall", w=19, len=40, h=13, elite="heart_warden",
                     dress=[("frames", dict(every=4)), ("scatter", dict(name="artery_root", n=4))], mobs=[("marrow_brute", 1)]),
                dict(name="the heart chamber", kind="round", w=47, len=47, h=26, chest=True, ring=12,
                     dress=[("scatter", dict(name="artery_root", n=10)), ("clusters", dict(name="breathing_sac", chance=0.02))]),
            ]),
        )
