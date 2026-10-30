"""The Clockwork Spire (a world tower, docs/TOWERS.md): blackened iron panels banded in brass, cogs set in the walls,
verdigris steam pipes, amber clock glass, a soot-dark stone footing, boiler light. dforge.py imports this; the
tower itself is tools/towers/clockwork_spire.py."""
from blockforge import R
from dforge import dungeon, B, Pp, common_props

IRON = R("#0c0d10", "#15171b", "#1f2227", "#2a2e34", "#363b42", "#444a52")
IRON_M = R("#060708", "#0b0c0e", "#121418")
BRASS = R("#3a2408", "#5c3a10", "#86581c", "#b07a2a", "#d6a040", "#f2cc72")
BRASS_D = R("#24160a", "#3a2408", "#5c3a10")
STONE = R("#16151a", "#211f25", "#2c2a31", "#38353d", "#46424b", "#55515a")
STONE_M = R("#0a090c", "#121116", "#1a1820")
VERD = R("#10302a", "#184a3e", "#226452", "#3a8a70", "#5cae90")
AMBER = R("#7a3a08", "#b45c10", "#e08a1e", "#ffb53a", "#ffd77a", "#fff2c4")
FIRE = R("#5a1606", "#9a2c08", "#d2520e", "#f68a1c", "#ffc24a", "#fff0b0")
SOOT = R("#1a120c", "#241a12", "#30231a", "#3c2c20", "#4a3828")

dungeon("clockwork_spire",
        blocks=[
            B("spire_footing", "Spire Footing", "ashlar", "minecraft:polished_deepslate", family=("stairs", "slab", "wall"),
              stem="spire_footing", stem_title="Spire Footing", args=dict(ramp=STONE, mortar=STONE_M)),
            B("foundry_bricks", "Foundry Bricks", "bricks", "minecraft:deepslate_bricks", family=("stairs", "slab", "wall"),
              stem="foundry_brick", stem_title="Foundry Brick", args=dict(ramp=STONE, mortar=STONE_M, crust=(SOOT, 0.12))),
            B("blackiron_plate", "Blackiron Plate", "plate", "minecraft:iron_block", family=("stairs", "slab"),
              args=dict(ramp=IRON, rivet=BRASS, seams=8)),
            B("brass_plate", "Brass Plate", "plate", "minecraft:copper_block", family=("stairs", "slab"),
              args=dict(ramp=BRASS, rivet=IRON, seams=8)),
            B("brass_grating", "Brass Grating", "grate", "minecraft:iron_block", family=("slab",), args=dict(ramp=BRASS, gap=IRON_M)),
            B("iron_gear_block", "Iron Cog Panel", "gear", "minecraft:iron_block", args=dict(ramp=IRON, base=IRON, rivet=BRASS)),
            B("brass_gear_block", "Brass Cog Panel", "gear", "minecraft:iron_block", args=dict(ramp=BRASS, base=IRON, rivet=BRASS)),
            B("steam_pipe", "Steam Pipe", "pipe", "minecraft:copper_block", args=dict(ramp=VERD, band=BRASS, bore=IRON_M)),
            B("drive_shaft", "Drive Shaft", "pipe", "minecraft:iron_block", args=dict(ramp=IRON, band=BRASS, bore=BRASS_D)),
            B("clock_glass", "Clock Glass", "lattice", "minecraft:glass", light=12, args=dict(ramp=AMBER, lead=IRON)),
            B("boiler_glow", "Boiler Grate", "glow", "minecraft:magma_block", light=14, args=dict(ramp=FIRE, base=IRON, motif="ring")),
            B("spire_column", "Spire Column", "column", "minecraft:iron_block", args=dict(ramp=IRON, mortar=BRASS, flutes=4)),
            B("gearwright_tiles", "Gearwright Tiles", "tiles", "minecraft:polished_deepslate", family=("slab",),
              stem="gearwright_tile", stem_title="Gearwright Tile", args=dict(ramp=STONE, grout=BRASS_D, n=4)),
            B("soot_planks", "Sooted Planks", "planks", "minecraft:dark_oak_planks", tool="axe", family=("stairs", "slab"),
              stem="soot_plank", stem_title="Sooted Plank", args=dict(ramp=SOOT, n=4)),
        ],
        props=common_props("spire", "Spire", light=13) + [
            Pp("spire_hoard", "hoard", "Horologe's Hoard", sound="wood", color="color_brown", strength=4, light=7)],
        )
