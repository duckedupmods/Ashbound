# Villages: research and rules (10/29)

The user's complaint about the first concepts: houses in rows, copy-pasted. Why it happened:
- equal gaps;
- the same setback from the walk;
- the same four rectangular kit houses;
- the same facing;
- nothing between the houses.

## What real villages do

Sources: Wikipedia, "Nucleated village"; Historic England (planned green villages); Essex Design Guide (settlement
characteristics); Emilien et al. 2012, "Procedural Generation of Villages on Arbitrary Terrains"; the GDMC
settlement challenge report (arXiv 2103.14950); builder guides.

- **A focus first.** The village grows from one focus: a river crossing, a church or hall, a junction, a green. The
  houses radiate out along the roads that meet there. The core is dense and the edge thins out into scattered
  farmsteads.
- **Roads first, then plots, then houses.** Routes follow the land (contours, the easy line). Plots are carved off
  them, and each house adapts to its slope (Emilien 2012; GDMC). Roads are drawn first, as the skeleton.
- **The plot, not the house, is the unit.** Each house faces the road at the front of a long, narrow plot. The yard,
  garden, shed or croft lies behind it, and the plot widths vary.
- **Real villages mix types.** Most are "polyfocal": a dense knot, a line along a road, a loose cluster, all in one
  place. Planned green villages have two rows facing a broad green, but even those vary the plots behind.
- **Variety without chaos.** One palette per village, so walls and roofs agree. The variety is in footprints (L, T,
  wings, lean-tos), rooflines, asymmetry, and the clutter of life (pots, vines, woodpiles), never in the materials.

## Rules for our generator

1. **Site → focus → roads.** Pick the focus from the site: the crossing, the deck, the green, the gate. The main
   road runs through it along the land's easy line, gently curved. Lanes branch off it and end at farmsteads.
   Footpaths take shortcuts.
2. **Density falls off from the focus.**
   - In the core, houses stand shoulder to shoulder, 2 storeys, some joined in pairs or terraces.
   - In the middle ring, houses sit 3-8 apart with yards.
   - At the edge are farmsteads: a house, a barn and a yard round a court, with fields behind.
   - Plus 1-2 outliers (a mill, a hut, a shrine).
3. **Plots.** Each house gets a plot that runs off the road, of varying width, so the street front never shows equal
   gaps. The setback varies by 0-3, and some houses are set at a slight angle to the road. Behind the house goes a
   garden, a shed, a woodpile, a washing line or a croft, fenced or hedged.
4. **Houses are composed, not stamped.**
   - The main block has a random length and depth, 1-2 storeys.
   - It gets 0-2 additions: a wing (L or T), a lean-to, a porch, an attached barn or shed, a dormer, an outside stair.
   - The roof turns gable-on or eaves-on to the road; chimneys go on varying sides.
   - The village palette (one wall colour family, one roof family plus a rare accent) keeps it reading as one place.
5. **Between the houses:** fruit trees, hedges, low fieldstone walls, gates, carts, barrels, haystacks, wells,
   benches, a pump. Never bare grass between buildings.
6. **The landmark** (mill, bell house, shrine, tower) stands on the high point or at the end of the main road's bend,
   so you see it as you walk in. One per village.
7. **Terrain.** Houses step with the ground on footings that show. On slopes they turn their eaves along the contour
   and get terraces with retaining walls. Nothing gets flattened wholesale.
8. **Below the capital.** At most ~25 buildings, no curtain walls, no spires.

## Process

- Plan view first (road graph, plots, density rings), rendered top-down, then the 3D build.
- Judge it from walking height, coming in along the road. The top view is only for checking the plan.
