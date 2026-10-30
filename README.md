# Ashbound

A dark-fantasy gate-dungeon mod for Minecraft 1.21.1 (NeoForge), built on Epic Fight. By Ducked Up Mods.

Alpha 0.1. Start a new world: updates may change world generation and saved data.

## What's in it

- Ranked gates, F to S: dungeons with their own monsters, bosses, gear and materials
- Hand-built towers, a capital city, villages, roads and raised terrain
- A guild with a rank card and a request board, a linear story and a journal
- 10 weapon types, 4 armour classes, three staff schools with their own spell effects, relics and curios
- A skill tree, levels, a forge with a rhythm minigame, and parties of up to 8

## Requirements

Minecraft 1.21.1, NeoForge 21.1, Epic Fight 21.17, Curios, Waystones (which needs Balm).

## Building

Java 21. Put the Waystones jar named in `build.gradle` in `run/mods`, then:

    ./gradlew build

The Python and Blender scripts in `tools/` generate most of the data and models. Several expect local paths and extracted game files, so
they may need adjusting. Files they generate are already in `src/main/resources`.

## Licence

Ashbound's code is GPL-3.0: see `LICENSE`. Parts of it are ported from Epic Fight's GPL-3.0 code. `TEMPLATE_LICENSE.txt` covers the
NeoForge MDK template. See `CREDITS.md`.
