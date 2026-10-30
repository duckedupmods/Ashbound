"""The Obsidian Labyrinth (A): a maze cut in the nether whose walls move - the gate cave, the first turns, the ember
pit, the shifting halls, the oracle's well, the ninth door where the Gatekeeper stands, the stair down to the heart,
and the bull's arena where the Minotaur waits. Black glass, basalt, bronze, and the magma under it all.
dforge.py imports this."""
from blockforge import R
from dforge import dungeon, B, Pp, common_props

OBSID = R("#04020a", "#0a0614", "#120c1e", "#1a1228", "#241a34", "#302442")
OBSID_M = R("#000000", "#020104", "#06040a")
BASALT = R("#0e0c0c", "#181514", "#221e1c", "#2e2826", "#3a3330", "#48403c")
BRONZE = R("#2a1608", "#442410", "#62361a", "#824a24", "#a2602e", "#c07a3c")
MAGMA = R("#6a1004", "#b02a06", "#e05a0c", "#ff8a20", "#ffc860")
CINDER = R("#1a0e0a", "#26140e", "#341c12", "#442618", "#56301e")
ASH = R("#2a2624", "#3a3532", "#4c4642", "#5e5752")

dungeon("obsidian_labyrinth",
        blocks=[
            B("maze_obsidian", "Maze Obsidian", "bricks", "minecraft:obsidian", family=("stairs", "slab", "wall"), stem="maze_obsidian",
              stem_title="Maze Obsidian", args=dict(ramp=OBSID, mortar=OBSID_M, rows=4, run=8)),
            B("obsidian_ashlar", "Obsidian Ashlar", "ashlar", "minecraft:obsidian", args=dict(ramp=OBSID, mortar=OBSID_M)),
            B("labyrinth_basalt", "Labyrinth Basalt", "rock", "minecraft:basalt", args=dict(ramp=BASALT, spread=0.6, crust=(ASH, 0.08))),
            B("cinder_strata", "Cinder Strata", "strata", "minecraft:blackstone", args=dict(ramp=CINDER, bands=5)),
            B("maze_flags", "Maze Flagstones", "flags", "minecraft:polished_basalt", family=("slab",), stem="maze_flag",
              stem_title="Maze Flag", args=dict(ramp=BASALT, grout=OBSID_M)),
            B("maze_carving", "Maze Carving", "carved", "minecraft:chiseled_polished_blackstone", args=dict(ramp=OBSID, mortar=BRONZE, motif="rune")),
            B("bronze_plating", "Bronze Plating", "plate", "minecraft:copper_block", args=dict(ramp=BRONZE, rivet=OBSID, seams=8)),
            B("basalt_pillar", "Basalt Pillar", "column", "minecraft:polished_basalt", args=dict(ramp=BASALT, mortar=BRONZE, flutes=6)),
            B("magma_seam", "Magma Seam", "glow", "minecraft:magma_block", light=12, args=dict(ramp=MAGMA, base=BASALT, motif="vein")),
            B("bronze_grate", "Bronze Grate", "grate", "minecraft:copper_grate", args=dict(ramp=BRONZE, gap=MAGMA)),
        ],
        props=common_props("maze", "Labyrinth", metal_color="color_orange", wood_color="color_black") + [
            Pp("ember_brazier", "plain", "Ember Brazier", box=[2, 0, 2, 14, 14, 14], sound="metal", color="color_orange", strength=3, light=14),
            Pp("bull_skull", "facing", "Bull Skull", box=[1, 0, 3, 15, 12, 13], sound="bone_block", color="sand", strength=2),
            Pp("cinder_pile", "plain", "Cinder Pile", box=[1, 0, 1, 15, 6, 15], sound="tuff", color="color_black", strength=1, light=5),
            Pp("thread_spool", "plain", "Thread Spool", box=[4, 0, 4, 12, 10, 12], sound="wool", color="color_red", strength=0.5),
        ],
        seal_words="The Gatekeeper's key locks the ninth gate", broken_words="The key turns and the ninth gate grinds open",
        layout=dict(
            palette=dict(
                hall_floor=[("maze_flags", 3), ("bronze_grate", 1)], hall_wall=[("maze_obsidian", 4), ("obsidian_ashlar", 2),
                                                                                  ("maze_carving", 1)],
                hall_ceil=[("obsidian_ashlar", 2), ("bronze_plating", 1)],
                cave_floor=[("labyrinth_basalt", 3), ("cinder_strata", 1)], cave_wall=[("labyrinth_basalt", 3), ("cinder_strata", 2)],
                cave_ceil=[("labyrinth_basalt", 3)],
                arena_floor=[("maze_flags", 3), ("bronze_grate", 1)], arena_wall=[("maze_obsidian", 3), ("maze_carving", 2),
                                                                                  ("magma_seam", 1)],
                bridge=[("bronze_grate", 1), ("maze_flags", 1)], rail="maze_obsidian_wall",
                fill="labyrinth_basalt", pillar="basalt_pillar", stairs="maze_obsidian_stairs", slab="maze_obsidian_slab",
                lamp="maze_lantern", chain="maze_chain", bars="maze_bars", coffer="maze_coffer", vein="magma_seam"),
            seal=6, lamp_every=6, lamp_height=6, veins=0.04,
            rooms=[
                dict(name="the gate cave", kind="cave", w=27, len=30, h=16,
                     dress=[("clusters", dict(name="cinder_pile", chance=0.03))], mobs=[("labyrinth_imp", 5)]),
                dict(name="the first turns", kind="hall", w=19, len=40, h=12, chest=True,
                     dress=[("frames", dict(every=4)), ("scatter", dict(name="ember_brazier", n=4)), ("scatter", dict(name="thread_spool", n=2))],
                     mobs=[("horned_runner", 3), ("labyrinth_imp", 2)]),
                dict(name="the ember pit", kind="chasm", w=33, len=38, h=18, drop=20, mobs=[("labyrinth_imp", 4)]),
                dict(name="the shifting halls", kind="hall", w=29, len=40, h=14, chest=True,
                     dress=[("frames", dict(every=5)), ("scatter", dict(name="bull_skull", n=6)), ("scatter", dict(name="ember_brazier", n=3))],
                     mobs=[("basalt_ogre", 1), ("horned_runner", 3), ("ember_oracle", 1)], decor=[("labyrinth_imp", 2)]),
                dict(name="the oracle's well", kind="cave", w=31, len=34, h=18, chest=True,
                     dress=[("clusters", dict(name="cinder_pile", chance=0.04)), ("scatter", dict(name="ember_brazier", n=4))],
                     mobs=[("ember_oracle", 2), ("basalt_ogre", 1)]),
                dict(name="the ninth door", kind="hall", w=23, len=26, h=16, elite="gatekeeper",
                     dress=[("scatter", dict(name="ember_brazier", n=4)), ("scatter", dict(name="bull_skull", n=2))],
                     mobs=[("horned_runner", 2)]),
                dict(name="the stair to the heart", kind="descent", to=-14, gap=6),
                dict(name="the bull's arena", kind="round", w=47, len=47, h=26, chest=True, ring=12,
                     dress=[("scatter", dict(name="bull_skull", n=8)), ("scatter", dict(name="ember_brazier", n=6)),
                            ("clusters", dict(name="cinder_pile", chance=0.02))]),
            ]),
        )
