# The Ash Tree (10/29, built, redesigned same day, untested in game)

`python tools/skilltree.py [--preview]` writes `src/main/resources/ashbound/skill_tree.json` (+ the concept sheet
`tools/renders/skilltree.png`). Never edit the json by hand. `python tools/balance.py` checks it (pass 4).

- 359 nodes: the Core (health, stamina, dodges, movement, mana) and 10 weapon areas, each hanging off the Core
  (the bridges between neighbouring areas were removed in the redesign). 50 notables, 10 keystones (one at a time), 18 Epic Fight skills unlocked by notables.
- One point per level. **Levels are bought with Ash in the tree** (K -> "Level up"); the HUD says when one is ready.
  Take a node next to one you have (click); take one back for 30 + 10 x level Ash (right-click) if the rest stays
  joined; "Reset tree" takes back everything for 50 x level Ash.
- Weapon-area stats and mechanics only count while you hold that weapon (a shield in either hand). Core nodes always
  count. Keystone drawbacks in `always` (Shadow Step / Glass Cannon health, Unbreakable move speed) are always on.
- **The tree is the only skill screen:** K opens it in place of Epic Fight's, skill books don't open and are taken
  out of drops. Everyone has Roll and Guard; a notable's skill is learned and equipped when taken; clicking an
  unlocked skill toggles it (to choose between two dodges, or more passives than slots).
- Code: `Passives.java` (data, points, Epic Fight learn/equip, stats as attribute modifiers, every fx),
  `client/TreeScreen.java`, `Net.Tree` / `Net.TreeAct`, staff hooks in `Spells.java`, Ash% in `Levels.java`.
- Budget: a small node is worth ~1.1-1.4 ("% more damage or survivability"), every area totals 32-37.

Honest notes:
- **Titan's Grip** is not dual-wielding yet: two-handers swing faster and harder, and each swing costs more stamina.
  True two-in-each-hand needs Epic Fight dual-wield animations for greatswords, which is its own job.
- Block/parry effects (Riposte, Thorns of Iron, Taunt, Unbreakable, guard%) hang on Epic Fight's incoming-damage
  hook at low priority. If they don't fire in game, the hook order is the first thing to check.

## The screen (redesign 10/29)

The first version (one big zoomable web) felt cramped, lagged zoomed out and lost its icons. Four mock-ups were made
(`tools/tree_mocks.py` -> `tools/renders/tree_mock_1..4.png`: pages, constellations, boards, wheel); built the mix of
2 + 1:
- **Overview:** a night sky, the Core in the middle, the 10 areas as big emblems with points spent and their notables
  as little lights. Click one to open its page.
- **Page:** tabs for all 11 areas down the left; the branch top-down from its Core entry node to the keystone, fitted
  to the screen (scroll/drag still work); an info panel on the right (the hovered node, or what the page gives you).
  Esc goes back to the overview.
- Page layouts come from `skilltree.py pages()` (each area rotated so it runs down), stored as `page` per area in the
  json with the area's emblem `icon`. Links are one rotated quad each (the lag was thousands of little squares).
- Icons: `tools/treeicons.py` (16x16 ASCII silhouettes, auto outline + bevel, corner badges) baked into
  `textures/gui/tree_icons.png`; contact sheet `tools/renders/tree_icons.png`. Sidestep's footprints are still small;
  the hammer icon reads as a blob at tab size.

## v2: the Ash Tree remake (10/29, after web research)

Research (Diablo 4, Last Epoch, Grim Dawn, Wynncraft, Veilguard, GDKeys "Keys to Meaningful Skill Trees", GMTK): the
old tree felt bad because ~80% of its 359 nodes were +2% filler and the screen had no picture. v2:

- **149 nodes.** Each weapon area is 14 nodes / 27 points: 5 stat nodes with ranks (5,5,3,3,3), 4 old notables,
  3 new "verb" nodes, 1 keystone. The Core is the start + 8 stat nodes (x5) + 10 notables (50 points). Total 320
  points vs ~99 at level 100, so builds have to choose.
- **Roles** (shape + colour): stat = round grey, ember = round orange (changes a move), gold = diamond (new move or
  Epic Fight skill), key = red octagon. Frames baked smooth in `textures/gui/tree_frames.png` by skilltree.py.
- **Every branch opens straight off the start**, same shape of choices in each (SLOTS/SLOT_LINKS): entry, hub with two
  sides, a fork that joins, the tip. Keystones need 16 points in their area (`key_need`).
- **Pages are drawn as the weapon** (FIGURES in skilltree.py: slot positions + the faint outline), Grim Dawn style; the
  outline brightens as the area fills.
- **Overview = a burning ash tree** (overview() in skilltree.py -> `overview` in the json): trunk = Core, a branch to
  each emblem; points spent climb the branch as fire with sparks; gold progress dots round each emblem.
- **Ranks** are stored by listing a node once per point in TAKEN (old saves: unknown ids dropped, points back).
- **30 new mechanics** in Passives.java (+ aegis/radiance in Spells.heal): disarm cleave flourish lunge execute vanish
  concuss shatter momentum pin whirl charge rage sunder last_stand bash guardian retaliate pierce fire_arrow point_blank
  static siphon surge aegis smite radiance harvest frenzy bone_armour. "Stun" = slowness VI + weakness V (not EF's
  stun). Piercing Shot splashes 60% around the target (arrow pierce level is private in 1.21.1).
- Mocks: tools/ashtree_mocks.py; all pages sheet: `python tools/skilltree.py --preview` -> tools/renders/skilltree.png.
- **Art from Blender (10/29):** the overview painting is `tools/blender/tree_ui.py` (a charred thorny ash on the
  overview paths, Cycles; output -> `textures/gui/tree_bg.png`), the node frames are `tools/blender/tree_frames.py`
  (5 roles x locked/open/taken, packed at 128px into `tree_frames.png` by skilltree.py frames()). The game draws the
  fire, sparks, emblem icons and progress dots on top. Icons are still the 16px treeicons ones (next).
- **Titan's Grip is a real dual wield now (10/29):** Movesets.java registers a `titan_grip` conditional (ONE_HAND style
  when Passives.titanGrip(p) and the off hand holds a two-hander) with a `greatsword_dual` moveset borrowed from Epic
  Fight's dual swords (hold/run/guard/autos/dash/air slash, Dancing Edge innate). The price: while the keystone is taken,
  every other weapon's hits and arrows are cancelled and staffs won't cast (Passives.titanLocked). The client knows its
  own tree (Passives.clientSelf); other players' stance is taken on trust. Shields aren't locked yet.
