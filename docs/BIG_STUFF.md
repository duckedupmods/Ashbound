# The big stuff

The user's list, 10/31, after the first friends session. Tick items off as they're approved in game.

- [ ] 1. **Skills.** Different skills for players to learn in the skill tree, by specialization.
  - Skill books drop from dungeons: different skills for different classes, with ranks and rarity, so players get OP later on or get lucky with a good one early. Awesome-looking books, and an animation when learning a skill.
  - 10/31 user's idea, from an anime: a rare book for your specialization unlocks new skills but takes other things away, like a tank with a fiery dragon form that turns him into a glass cannon, usable only at 30% health. Proposed as Awakening Tomes: rare boss drop, one read at a time, a form with a trigger, a gift and a price, replaces the book-only ultimates. Details not approved yet.
- [ ] 2. **VFX.** Better VFX for everything: every skill, every mage skill. Search Google for references first.
- [ ] 3. **Mage staffs.** Staffs become "boosting" staffs that boost their class.
- [ ] 4. **Summons.** Remake the summoned mobs; they look awful.
  - 10/31 got the rig fix with everyone else (no flying limbs, bending robes). Their designs are unchanged, so this is not the remake yet.
  - (boss rig) 10/31 first in-game test: Winter Marshal was fully broken and bosses barely walked. Marshal, Bone Hound and Grave Rat rebuilt on `efmob.mounted` (four-legged, the rider as the biped); bosses chase at 3.7 blocks/s (`MobMoves.chase`), walk straight at you with no path (`MobMoves.press`), step 1.6 high.
  - (boss rig) 10/31 Winter Marshal's horse approved in game by the user. `client/MountPose.java` + `mixin/MountPoseMixin.java` keep the body level and trot the legs (`GateMobs.ON_ALL_FOURS`); `efmob.BENDS` tips its neck and head forward. Not yet checked in game: chase speed on the other bosses, weapon hit reach, Bone Hound and Grave Rat, the zweihander.
- [ ] 5. **Loot weapons.** Remake the weapons in the loot pool; a lot of them have parts not connected to the handle or to each other.
  - 10/31 joins fixed on all 490 weapons (167 meshes had loose parts, 0 now), designs kept. `tools/weapon_joins.py` checks; `weaponforge.export` welds on every export. Old meshes in tools/renders/mesh_before_weld. Not seen in game yet.
- [ ] 6. **Dungeon bosses.** Remake them: some sit half in the ground because of their textures, have flying hands, or hit badly with their weapons.
  - 10/31 the 27 two-legged bosses fixed, designs kept: limbs on their joints, elbows/knees/hips bend, robes follow the legs, weapons turned onto the grip, swing hit box = the weapon you see (`reach` in gate_mobs.json, MobMoves.collider). `tools/efskin.py` does it, run it again after any efmob/port_gate export; `tools/boss_check.py` and `tools/blender/boss_pose.py` measure and render. Originals in tools/renders/mesh_before_skin. Run on all 225 two-legged monsters too (`efskin.py --all`), summons included since they are dungeon monsters; the 134 armed gate monsters got weapon-sized hit boxes. Gather is limited to arms, or it shortens capes and crushes wings. The spider-bodied 36 (bosses still_heart, ignavar) and townsfolk not touched. 13/13 headless; not seen in game yet, party balance of shorter reach untested.
- [ ] 7. **Mounts.** Choose one of five mounts at the start, with the class. They must be spectacular.
  - 10/31 concepts: Ashmane (burning warhorse, fastest), Rimehorn (ice stag, highest jump), Gravefang (bone dire wolf, climbs ledges), Thornback (moss boar, charges through enemies), Stormdrake (lightning wyvern, glides). Models in `tools/voxmounts.py`, sheet in docs/mounts_v3.png, approved by the user. Riding, the H key, the chooser after the class and the renderer are built; not seen in game yet.
  - 10/31 first test: centering, gaits, chooser lag and getting on and off fixed in source; second test running, verdict pending.

10/31 evening: items 1-4 built, 18/18 headless, none of it seen in game. Skills.java (18 paths, one skill each, ranks I-V), Forms.java (9 Tomes), Books.java (5 book rarities, boss drops), client/SkillScreen (N), SkillHud, TomeScreen, SkillFx (a look per skill, wings and auras, camera kick, screen flash, the book scene), Thrall + ThrallRender + tools/voxthralls.py (revenant, champion), tools/skill_items.py (icons, 3D books), staff boosts and held skills, balance notes in docs/BALANCE.md. Still short of the plan: 2 more skills per path (54 total), per-form model changes, new sounds, monster skill VFX in MobSkills.

10/31: the game loads with all of it, no crash; in-world test running, verdict pending. Proposed next: 2 more skills per path (36), unlocked at levels 15 and 30, unanswered.

10/31 after the first skill test: G opened Curios and locked on because three keys shared it; lock-on moved to O, Curios off (config/ashbound-keys-2.done). White staff on one ally is now a beam (Spells.beam, FxKit.HealBeam): five pulses over 2.5s, cut if they leave reach, pick by looking at them + G, or step through the party. 54 skills: three per path at levels 5, 15, 30 (SkillArts.java). A book of a skill you don't have and your path won't teach makes you give one up for good (Skills.replace, client/ReplaceScreen); your own path's later skill comes early from a book. New VFX: spell_fx.fsh modes 9-17 (slash, flow, ring, crack, flare, swirl, arc, rune, tube), client/FxKit, speed lines, FOV punch, real ground chunks. `tools/fxpreview/run.sh` compiles the shader and renders every mode without the game.

10/31 user feedback, not built yet: one skill chosen at each of levels 5, 15 and 30, not all of a path at once.

Plan: finish everything here, then build 0.1.2 and playtest with friends tonight. The public jar on CurseForge still lacks the mining fix.

10/31 VFX round 2, from adnvli/vfxskill's craft notes: FxKit.impact (flash, star + black twin, black mass, crescents, needles, ring, smoke), Comet tails, shed rings, black fire for the plain black staff (SpellLook.HEX), liquid as a torn Crown with mist, no glossy drops. Headless 20/20, shader sheet checked, not yet seen in game. Skill choices at 5/15/30 still not started.

## 10/31 evening: VFX for everything, skill choices

VFX round 3, built, compiles, 20/20 headless, not seen in game:
- Kit (FxKit): gather (wind-up), slash (black, colour, white edge, sheds needles, drawn over ticks), spray (needles, not beads), ink, wake, halo, rising. Column, lance, slam, spikes all upgraded, so every skill got them.
- All 54 skills, Forms, heal and summon circles, heal beam, ward: reworked per class (SkillFx.play). Biggest blows get an impact frame (one tick near black, then the colour). The screen flash and speed lines now fade with distance.
- Monster skills: no vanilla particles left in MobSkills. Everything goes through SkillFx.monster ("mob_what:gate"), in the dungeon's colour. Slams, leaps, lightning, rain and burrows show a real circle on the ground where they land.
- Apprentice summoner's staff has its own cold look (SpellLook.GRAVE), no more Cellar green. Thralls tinted to match.
- Test: /ashbound skill try ID, /ashbound spell mob_slam (mob_tell, mob_quake, mob_roar, mob_strike, mob_thunder, mob_cloud, mob_breath, mob_beam, mob_pull, mob_blink, mob_summon, mob_heal, mob_phase), /ashbound spell grave.
- Not done: true hit-stop, new smoke textures, real bloom (Veil, needs a yes), new Cycles flipbooks.

Skill choices, built, tested headless, screen not seen in game:
- Levels 5, 20, 35 (Skills.UNLOCK; the numbers are one line, balance later). At each you choose one of two, one from each path, so 8 builds a class.
- A book teaches a skill early if you've not chosen on its level, and that uses the level. Otherwise the old replace-a-skill screen.
- Old saves keep what they know (Skills.settle). Changing class wipes the old class's skills (Skills.keepOwn).

## 10/31 night: the left-outs, party 15%, Pass 8

- Bloom: client/Bloom.java + spell_post shader. No Veil: vertices are written twice, the copy drawn into its own small target with the world's depth, blurred, added over the frame. Only effects glow, smoke doesn't. Blur shader checked in tools/fxpreview, the pipeline itself unseen in game.
- Hit-stop: HitStop.java + mixin/AnimationPlayerMixin on Epic Fight's AnimationPlayer. Player's own blows hold attacker and victim 1-3 ticks, repaid at double speed. Mixin load tested headless, feel unseen.
- Smoke: new Cycles flipbook (tools/blender/vfx_flip.py smoke), atlas rebuilt.
- Party +15% and Pass 8: docs/BALANCE.md. 22/22 headless.
