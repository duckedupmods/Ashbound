"""The passive skill tree (docs/SKILLTREE.md): the player Core in the middle, one area per weapon type around it.

    python tools/skilltree.py            # writes src/main/resources/ashbound/skill_tree.json + prints a summary
    python tools/skilltree.py --preview  # also renders tools/renders/skilltree.png (the concept sheet)

Every node is data: stats are attribute bonuses (applied by Passives.java, weapon ones only while you hold that kind),
`fx` names a mechanic coded in Passives.java, `ef` an Epic Fight skill the node unlocks. Power (docs/BALANCE.md):
a small node ~1, a notable 4-5, a keystone ~15 minus its drawback; balance.py checks the areas against each other.
"""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src/main/resources/ashbound/skill_tree.json"
PNG = ROOT / "tools/renders/skilltree.png"

# ---------------------------------------------------------------------------------------------------------------
# The player Core: health, stamina, dodges, movement, mana. Everyone passes through it.
CORE = {
    "name": "The Core", "colour": "#d8c8b0",
    "start": {"name": "Ashborn", "about": "where every path starts: Roll and Guard", "ef": "roll", "stats": {}},
    "smalls": [
        ("Vigour", {"health%": 1.5}), ("Deep Lungs", {"stamina": 0.5}), ("Second Breath", {"stamina_regen%": 4}),
        ("Light Step", {"move%": 1.5}), ("Hardened", {"armour": 0.4}), ("Footing", {"stun_armour": 1}),
        ("Focus", {"mana": 4}), ("Calm Mind", {"mana_regen%": 1.5}),
    ],
    "notables": [
        {"name": "Sidestep", "about": "unlocks Step: a short, quick dodge", "ef": "step", "stats": {"stamina": 1}},
        {"name": "Emergency Escape", "about": "dodge out of a hit or an attack, even with no stamina", "ef": "emergency_escape"},
        {"name": "Twin Leap", "about": "unlocks Phantom Ascent: jump again in mid-air", "ef": "phantom_ascent"},
        {"name": "Adrenaline", "about": "stamina starts coming back the moment you kill", "ef": "adrenaline_fiend", "stats": {"stamina": 1}},
        {"name": "Pillager", "about": "a kill gives back a third of your missing stamina", "ef": "stamina_pillager"},
        {"name": "Adaptive Skin", "about": "resist the kind of damage that hit you last", "ef": "adaptive_skin"},
        {"name": "Second Wind", "about": "once every 3 minutes a killing blow leaves you at 1 health and 2 s untouchable",
         "fx": "second_wind"},
        {"name": "Iron Constitution", "about": "+5% health, +1 stun armour", "stats": {"health%": 5, "stun_armour": 1}},
        {"name": "Fleetfoot", "about": "+6% move speed, armour weighs a third less", "stats": {"move%": 6, "weight%": -33}},
        {"name": "Ash Hunger", "about": "+10% Ash from kills, heal 1 health on each kill", "stats": {"ash%": 10}, "fx": "kill_heal"},
    ],
}

# One area per weapon type. smalls cycle along the trunk and the clusters; weapon stats only count while you hold it.
AREAS = [
    {"id": "sword", "name": "The Blade", "colour": "#e0e4ec", "smalls": [
        ("Edge", {"dmg%": 1.5}), ("Tempo", {"speed%": 1.5}), ("Find the Gap", {"negation%": 3})],
     "notables": [
        {"name": "Swordmaster", "about": "unlocks Swordmaster: faster swings", "ef": "swordmaster", "stats": {"speed%": 4}},
        {"name": "Riposte", "about": "after a parry, your next hit within 4 s deals +60%", "fx": "riposte"},
        {"name": "Flowing Steel", "about": "+15% damage for 3 s after a dodge", "fx": "flow_after_dodge"},
        {"name": "Duelist", "about": "+12% damage while only one enemy is within 8 blocks", "fx": "duelist"}],
     "keystone": {"name": "Blade Dance", "about": "every 4th hit of a combo strikes twice; your first hit on an enemy deals -25%",
                  "fx": "blade_dance"}},
    {"id": "dagger", "name": "The Shadow", "colour": "#8a7ab8", "smalls": [
        ("Quick Hands", {"speed%": 1.5}), ("Sharp", {"dmg%": 1.5}), ("Light on Your Feet", {"move%": 1.5})],
     "notables": [
        {"name": "Technician", "about": "unlocks Technician: a dodge right before a hit gives stamina back", "ef": "technician"},
        {"name": "Backstab", "about": "+40% damage from behind", "fx": "backstab"},
        {"name": "Venom Edge", "about": "your hits poison for 2 s", "fx": "venom"},
        {"name": "Catharsis", "about": "unlocks Catharsis: dodging attacks charges your weapon", "ef": "catharsis"}],
     "keystone": {"name": "Shadow Step", "about": "a dodge that slips a melee hit makes your next hit within 4 s deal double; -20% max health",
                  "fx": "shadow_step", "always": {"health%": -20}}},
    {"id": "hammer", "name": "The Anvil", "colour": "#c08a50", "smalls": [
        ("Heavy Head", {"dmg%": 1.5}), ("Impact", {"impact": 0.3}), ("Braced", {"stun_armour": 1})],
     "notables": [
        {"name": "Meteor Slam", "about": "unlocks Meteor Slam: crash down from a jump", "ef": "meteor_slam"},
        {"name": "Bonebreaker", "about": "+0.8 impact: staggered enemies stay down longer", "stats": {"impact": 0.8}},
        {"name": "Aftershock", "about": "a hit that kills sends a 3-block shockwave for 40% damage", "fx": "aftershock"},
        {"name": "Unmoved", "about": "+4 stun armour", "stats": {"stun_armour": 4}}],
     "keystone": {"name": "Earthshaker", "about": "every hit sends a small shockwave (25%); -15% attack speed", "fx": "earthshaker",
                  "stats": {"speed%": -15}}},
    {"id": "spear", "name": "The Reach", "colour": "#7ab07a", "smalls": [
        ("Point", {"dmg%": 1.5}), ("Long Arm", {"reach": 0.1}), ("Pierce", {"negation%": 3})],
     "notables": [
        {"name": "Revelation", "about": "unlocks Revelation: guards and dodges build stacks for a sure hit", "ef": "revelation"},
        {"name": "Skewer", "about": "+1 enemy hit per swing", "stats": {"strikes": 1}},
        {"name": "Vault", "about": "unlocks Demolition Leap: launch yourself forward", "ef": "demolition_leap"},
        {"name": "Keep Away", "about": "+0.5 knockback; +10% damage to enemies 2.5 blocks or more away", "stats": {"knockback": 0.5},
         "fx": "keep_away"}],
     "keystone": {"name": "Impaler", "about": "+1 reach, +3 enemies per swing; only while your off-hand is empty",
                  "fx": "impaler"}},
    {"id": "twohander", "name": "The Titan", "colour": "#c05a4a", "smalls": [
        ("Weight of Steel", {"dmg%": 1.5}), ("Grit", {"stamina": 0.5}), ("Cleave", {"negation%": 3})],
     "notables": [
        {"name": "Berserker", "about": "unlocks Berserker: more damage and speed the less health you have", "ef": "berserker"},
        {"name": "Endurance", "about": "unlocks Endurance: shrug off a hit while winding up", "ef": "endurance"},
        {"name": "Forbidden Strength", "about": "unlocks Forbidden Strength: pay health when out of stamina", "ef": "forbidden_strength"},
        {"name": "Wide Arc", "about": "+1 enemy hit per swing, +3% damage", "stats": {"strikes": 1, "dmg%": 3}}],
     "keystone": {"name": "Titan's Grip", "about": "hold a two-hander in each hand and swing both: each hit deals 25% less "
                  "but they come much faster (about +25% damage a second); every swing costs 0.5 more stamina, and no "
                  "other weapon works for you while you have it", "fx": "titans_grip"}},
    {"id": "shield", "name": "The Wall", "colour": "#6a8ab8", "smalls": [
        ("Bulwark", {"armour": 0.4}), ("Stand Firm", {"stun_armour": 1}), ("Guard", {"guard%": 3})],
     "notables": [
        {"name": "Parrying", "about": "unlocks Parrying: a timed guard costs nothing and stops arrows", "ef": "parrying"},
        {"name": "Impact Guard", "about": "unlocks Impact Guard: guard fire, magic and explosions", "ef": "impact_guard"},
        {"name": "Taunt", "about": "blocking a hit makes monsters within 8 blocks come at you, every 5 s (for the party's tank)",
         "fx": "taunt"},
        {"name": "Thorns of Iron", "about": "blocked melee hits throw back 30% of their damage", "fx": "reflect"}],
     "keystone": {"name": "Unbreakable", "about": "the first hit you block every 4 s costs no stamina; -15% move speed",
                  "fx": "unbreakable", "always": {"move%": -15}}},
    {"id": "bow", "name": "The Hunt", "colour": "#a8b060", "smalls": [
        ("Draw Strength", {"arrow%": 1.5}), ("Fletching", {"velocity%": 3}), ("Light Step", {"move%": 1.5})],
     "notables": [
        {"name": "Hunter's Mark", "about": "a fully drawn hit marks the target: it takes +15% from everyone for 6 s", "fx": "mark"},
        {"name": "Volley", "about": "every 5th arrow splits into three", "fx": "volley"},
        {"name": "Steady Aim", "about": "+20% arrow damage when shot standing still", "fx": "steady"},
        {"name": "Skirmisher", "about": "+15% arrow damage for 3 s after a dodge", "fx": "flow_after_dodge"}],
     "keystone": {"name": "Deadeye", "about": "fully drawn arrows deal +50%; arrows shot on the move deal -30%",
                  "fx": "deadeye"}},
    {"id": "black", "name": "The Storm", "colour": "#5a6ae0", "smalls": [
        ("Power", {"spell%": 1.5}), ("Font", {"mana_regen%": 1.5}), ("Reserves", {"mana": 4})],
     "notables": [
        {"name": "Overload", "about": "every 6th bolt bursts on hit (3 blocks)", "fx": "overload"},
        {"name": "Lingering Curse", "about": "your element's effect lasts twice as long", "fx": "long_effects"},
        {"name": "Mana Shield", "about": "a fifth of damage taken comes off your mana first", "fx": "mana_shield"},
        {"name": "Spellweaver", "about": "+12% spell power while above 80% mana", "fx": "spellweaver"}],
     "keystone": {"name": "Glass Cannon", "about": "+40% spell power; -30% max health", "fx": "glass_cannon",
                  "stats": {"spell%": 40}, "always": {"health%": -30}}},
    {"id": "white", "name": "The Light", "colour": "#f0e0a0", "smalls": [
        ("Grace", {"heal%": 1.5}), ("Font", {"mana_regen%": 1.5}), ("Ward", {"armour": 0.3})],
     "notables": [
        {"name": "Mending Aura", "about": "your heals reach 12 blocks instead of 8 and are 15% stronger", "fx": "heal_chain"},
        {"name": "Blessing", "about": "whoever you heal deals +10% damage for 5 s", "fx": "blessing"},
        {"name": "Purify", "about": "your heals clear poison, wither and slowness", "fx": "purify"},
        {"name": "Sanctuary", "about": "a heal leaves a glowing circle that heals for 4 s", "fx": "sanctuary"}],
     "keystone": {"name": "Martyr", "about": "heals are 50% stronger; with no mana a heal costs your own health",
                  "fx": "martyr"}},
    {"id": "summon", "name": "The Legion", "colour": "#9ac0a0", "smalls": [
        ("Bound Flesh", {"thrall_hp%": 3}), ("Command", {"thrall_dmg%": 1.5}), ("Reserves", {"mana": 4})],
     "notables": [
        {"name": "Pack Tactics", "about": "each thrall deals +5% for every other thrall", "fx": "pack"},
        {"name": "Death Pact", "about": "a thrall that dies heals you for 3", "fx": "death_pact"},
        {"name": "Long Service", "about": "thralls stay 50% longer", "fx": "long_thralls"},
        {"name": "Bigger Bones", "about": "+15% thrall health", "stats": {"thrall_hp%": 15}}],
     "keystone": {"name": "Legion", "about": "up to six thralls; each deals -30%", "fx": "legion"}},
]

# ---------------------------------------------------------------------------------------------------------------
# The Ash Tree v2 (10/29, after looking at Diablo 4, Last Epoch, Grim Dawn, Wynncraft): each area is ~14 nodes drawn
# on its weapon's picture. Stat nodes take several points (ranks); every other node does something you can name.
# Roles: stat (numbers), ember (changes a move), gold (a new move or skill), key (a keystone, with a cost).
KEY_NEED = 16  # points spent in an area before its keystone opens

# per area: two more stat nodes beside the three smalls, and three new nodes that do something (fx in Passives.java)
EXTRA = {
    "sword": {"stats": [("Footwork", {"move%": 1.5}), ("Poise", {"stun_armour": 1})], "verbs": [
        {"name": "Disarm", "about": "a riposte knocks the weapon aside: the enemy is weakened and slowed for 2 s", "fx": "disarm"},
        {"name": "Cleaving Arc", "about": "every 3rd hit also cuts everything within 2.5 blocks of the target for 50%", "fx": "cleave", "gold": True},
        {"name": "Flourish", "about": "a kill gives back 3 stamina", "fx": "flourish"}]},
    "dagger": {"stats": [("Slip", {"stamina_regen%": 4}), ("Needle", {"negation%": 3})], "verbs": [
        {"name": "Shadow Lunge", "about": "attack within 1 s of a dodge to dash forward into the hit", "fx": "lunge", "gold": True},
        {"name": "Execute", "about": "+50% damage to enemies below 30% health", "fx": "execute"},
        {"name": "Vanish", "about": "a kill turns you invisible for 3 s and monsters near you lose track of you", "fx": "vanish"}]},
    "hammer": {"stats": [("Thick Arms", {"stamina": 0.5}), ("Crush", {"negation%": 3})], "verbs": [
        {"name": "Concussion", "about": "every 4th hit stuns the target for 1 s", "fx": "concuss", "gold": True},
        {"name": "Shatter", "about": "+30% damage to slowed or stunned enemies", "fx": "shatter"},
        {"name": "Momentum", "about": "each hit in a combo deals 5% more, up to +25%", "fx": "momentum"}]},
    "spear": {"stats": [("Footing", {"stun_armour": 1}), ("Quick Jab", {"speed%": 1.5})], "verbs": [
        {"name": "Pin", "about": "hitting an enemy 3 or more blocks away pins it: slowed hard for 2 s", "fx": "pin"},
        {"name": "Whirl", "about": "every 5th hit sweeps everything within 3 blocks for 50%", "fx": "whirl", "gold": True},
        {"name": "Charge", "about": "+40% damage on hits while sprinting", "fx": "charge"}]},
    "twohander": {"stats": [("Iron Hide", {"armour": 0.4}), ("Swing Through", {"speed%": 1.5})], "verbs": [
        {"name": "Rage", "about": "each hit you take gives +5% damage for 6 s, up to +20%", "fx": "rage"},
        {"name": "Sunder", "about": "every 3rd hit deals +40%", "fx": "sunder"},
        {"name": "Last Stand", "about": "below 30% health you take 25% less damage", "fx": "last_stand"}]},
    "shield": {"stats": [("Iron Skin", {"health%": 1.5}), ("Hold", {"stamina": 0.5})], "verbs": [
        {"name": "Shield Bash", "about": "after a block, your next hit within 3 s deals +25% and stuns for 1 s", "fx": "bash", "gold": True},
        {"name": "Guardian", "about": "players within 6 blocks of you take 10% less damage", "fx": "guardian"},
        {"name": "Retaliate", "about": "a block gives +20% damage for 3 s", "fx": "retaliate"}]},
    "bow": {"stats": [("Hunter's Lungs", {"stamina": 0.5}), ("Keen Eye", {"arrow%": 1.5})], "verbs": [
        {"name": "Piercing Shot", "about": "fully drawn arrows tear through: enemies beside the target take 60%", "fx": "pierce", "gold": True},
        {"name": "Fire Arrow", "about": "every 4th arrow sets its target on fire", "fx": "fire_arrow"},
        {"name": "Point Blank", "about": "+25% arrow damage to enemies within 6 blocks", "fx": "point_blank"}]},
    "black": {"stats": [("Ward", {"armour": 0.3}), ("Attunement", {"spell%": 1.5})], "verbs": [
        {"name": "Static", "about": "monsters that hit you in melee take 3 lightning damage", "fx": "static"},
        {"name": "Siphon", "about": "a kill gives back 6 mana", "fx": "siphon"},
        {"name": "Arcane Surge", "about": "+30% spell power while your mana is full", "fx": "surge"}]},
    "white": {"stats": [("Reserves", {"mana": 4}), ("Devotion", {"health%": 1.5})], "verbs": [
        {"name": "Aegis", "about": "your heals also give 4 absorption for 10 s", "fx": "aegis"},
        {"name": "Smite", "about": "+30% damage to undead, from anything you do", "fx": "smite"},
        {"name": "Radiance", "about": "your heal burns monsters in its reach for half its strength", "fx": "radiance", "gold": True}]},
    "summon": {"stats": [("Font", {"mana_regen%": 1.5}), ("Grave Tithe", {"thrall_dmg%": 1.5})], "verbs": [
        {"name": "Soul Harvest", "about": "a kill heals your thralls for 4", "fx": "harvest"},
        {"name": "Frenzy", "about": "your thralls deal +20% for 5 s after you hit something", "fx": "frenzy"},
        {"name": "Bone Armour", "about": "+1 armour for each thrall you have", "fx": "bone_armour"}]},
}
RANKS = [5, 5, 3, 3, 3]  # the five stat nodes' ranks: S0 S1 S2 S3 S4

# every area's branch has the same shape of choices: entry, a hub with two sides, a fork that joins again, the tip
SLOTS = ["S0", "S1", "N0", "N1", "V0", "N2", "V1", "S2", "S3", "S4", "N3", "V2", "K"]
SLOT_LINKS = [("S0", "S1"), ("S1", "N0"), ("N0", "N1"), ("N1", "V0"), ("N0", "N2"), ("N2", "V1"), ("N0", "S2"),
              ("S2", "S3"), ("S2", "S4"), ("S3", "N3"), ("S4", "N3"), ("N3", "V2"), ("V2", "K")]


def circle(cx, cy, r, n=28):
    return [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n + 1)]


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]


# each area's picture: where each slot sits (page units, the tip up) and the faint outline drawn behind (Grim Dawn)
FIGURES = {
    "sword": ({"S0": (0, 700), "S1": (0, 610), "N0": (0, 520), "N1": (-140, 520), "V0": (-260, 520), "N2": (140, 520),
               "V1": (260, 520), "S2": (0, 430), "S3": (-62, 345), "S4": (62, 345), "N3": (0, 260), "V2": (0, 165), "K": (0, 55)},
              [[(0, -10), (95, 90), (95, 480), (-95, 480), (-95, 90), (0, -10)], [(0, 40), (0, 470)], rect(-310, 495, 310, 545),
               rect(-26, 550, 26, 665), circle(0, 700, 38)]),
    "dagger": ({"S0": (0, 640), "S1": (0, 555), "N0": (0, 470), "N1": (-125, 440), "V0": (-215, 365), "N2": (125, 440),
                "V1": (215, 365), "S2": (0, 385), "S3": (-58, 300), "S4": (58, 300), "N3": (0, 225), "V2": (0, 135), "K": (0, 35)},
               [[(0, -20), (90, 130), (75, 425), (-75, 425), (-90, 130), (0, -20)], [(-250, 330), (-170, 430), (0, 455), (170, 430), (250, 330)],
                [(-245, 350), (-165, 450), (0, 478), (165, 450), (245, 350)], rect(-24, 480, 24, 600), circle(0, 640, 34)]),
    "hammer": ({"S0": (0, 720), "S1": (0, 620), "N0": (0, 520), "N1": (-150, 470), "V0": (-195, 270), "N2": (150, 470),
                "V1": (195, 270), "S2": (0, 410), "S3": (-95, 300), "S4": (95, 300), "N3": (0, 255), "V2": (0, 140), "K": (0, 35)},
               [rect(-255, 185, 255, 370), [(-60, 185), (0, -20), (60, 185)], rect(-22, 370, 22, 760), [(-22, 470), (-150, 470)],
                [(22, 470), (150, 470)]]),
    "spear": ({"S0": (0, 770), "S1": (0, 660), "N0": (0, 550), "N1": (-115, 485), "V0": (-115, 375), "N2": (115, 485),
               "V1": (115, 375), "S2": (0, 440), "S3": (-60, 335), "S4": (60, 335), "N3": (0, 245), "V2": (0, 150), "K": (0, 45)},
              [[(0, -10), (72, 110), (52, 245), (0, 280), (-52, 245), (-72, 110), (0, -10)], [(-14, 285), (-14, 800)], [(14, 285), (14, 800)],
               [(-70, 290), (70, 290)], [(0, 300), (-115, 360), (-115, 500)], [(0, 300), (115, 360), (115, 500)]]),
    "twohander": ({"S0": (0, 770), "S1": (0, 680), "N0": (0, 590), "N1": (-150, 590), "V0": (-275, 565), "N2": (150, 590),
                   "V1": (275, 565), "S2": (0, 490), "S3": (-75, 395), "S4": (75, 395), "N3": (0, 300), "V2": (0, 190), "K": (0, 70)},
                  [[(0, -20), (120, 90), (120, 555), (-120, 555), (-120, 90), (0, -20)], [(0, 40), (0, 540)],
                   [(-330, 545), (-300, 565), (300, 565), (330, 545)], [(-330, 620), (-300, 615), (300, 615), (330, 620)], rect(-30, 620, 30, 735),
                   circle(0, 770, 40)]),
    "shield": ({"S0": (0, 610), "S1": (0, 515), "N0": (0, 420), "N1": (-145, 380), "V0": (-175, 240), "N2": (145, 380),
                "V1": (175, 240), "S2": (0, 320), "S3": (-80, 230), "S4": (80, 230), "N3": (0, 150), "V2": (0, 55), "K": (0, -45)},
               [[(-250, -60), (250, -60), (262, 260), (0, 690), (-262, 260), (-250, -60)],
                [(-222, -32), (222, -32), (232, 255), (0, 640), (-232, 255), (-222, -32)]]),
    "bow": ({"S0": (40, 690), "S1": (-60, 590), "N0": (-115, 470), "N1": (60, 540), "V0": (190, 470), "N2": (-255, 350),
             "V1": (-375, 350), "S2": (-130, 350), "S3": (-105, 225), "S4": (60, 250), "N3": (-60, 115), "V2": (10, 30), "K": (60, -45)},
            [[(60, -50), (-40, 60), (-110, 200), (-135, 350), (-110, 500), (-40, 640), (60, 750)], [(60, -50), (60, 750)],
             [(160, 350), (-400, 350)], [(-400, 350), (-370, 335), (-370, 365), (-400, 350)]]),
    "black": ({"S0": (0, 760), "S1": (0, 650), "N0": (0, 540), "N1": (-125, 500), "V0": (-210, 405), "N2": (125, 500),
               "V1": (210, 405), "S2": (0, 430), "S3": (-75, 335), "S4": (75, 335), "N3": (0, 255), "V2": (0, 150), "K": (0, 35)},
              [rect(-12, 300, 12, 790), circle(0, 185, 105), [(0, 300), (-95, 170)], [(0, 300), (95, 170)],
               [(-40, 470), (-120, 430), (-100, 420), (-230, 350)], [(40, 470), (120, 430), (100, 420), (230, 350)]]),
    "white": ({"S0": (0, 750), "S1": (0, 645), "N0": (0, 525), "N1": (-145, 525), "V0": (-270, 525), "N2": (145, 525),
               "V1": (270, 525), "S2": (0, 410), "S3": (-112, 290), "S4": (112, 290), "N3": (0, 240), "V2": (0, 140), "K": (0, 30)},
              [circle(0, 240, 125), rect(-24, 365, 24, 790), rect(-310, 500, 310, 550)]),
    "summon": ({"S0": (0, 705), "S1": (0, 610), "N0": (0, 500), "N1": (-110, 420), "V0": (-205, 300), "N2": (110, 420),
                "V1": (205, 300), "S2": (0, 385), "S3": (-90, 255), "S4": (90, 255), "N3": (0, 175), "V2": (0, 80), "K": (0, -25)},
               [circle(0, 280, 235, 36), [(-150, 470), (-140, 650), (140, 650), (150, 470)], circle(-100, 385, 55),
                circle(100, 385, 55), [(-160, 75), (-105, -40), (-50, 40), (0, -70), (50, 40), (105, -40), (160, 75)]]),
}

# the Core: the start in the middle, its eight stats round it, the ten notables outside them; drawn as a flame
CORE_FIGURE = [[(0, -360), (90, -230), (190, -170), (270, 10), (250, 200), (140, 330), (0, 370), (-140, 330), (-250, 200),
                (-270, 10), (-190, -170), (-90, -230), (0, -360)]]


class Tree:
    def __init__(self):
        self.nodes, self.links = {}, set()

    def add(self, nid, kind, role, name, x, y, area, about="", stats=None, fx=None, ef=None, always=None, ranks=1):
        """stats count while you hold the area's weapon (the Core's always), times the ranks taken; always: a
        keystone's drawback, held or not"""
        self.nodes[nid] = {"id": nid, "kind": kind, "role": role, "max": ranks, "name": name, "x": round(x, 1),
                           "y": round(y, 1), "area": area, "about": about, "stats": stats or {}, "always": always or {},
                           "fx": fx, "ef": ef}
        return nid

    def link(self, a, b):
        self.links.add(tuple(sorted((a, b))))


def describe(stats):
    names = {"health%": "% health", "stamina": " max stamina", "stamina_regen%": "% stamina regen", "move%": "% move speed",
             "armour": " armour", "stun_armour": " stun armour", "mana": " max mana", "mana_regen%": "% mana regen",
             "dmg%": "% damage", "speed%": "% attack speed", "negation%": "% armour negation", "impact": " impact",
             "reach": " reach", "strikes": " enemies per swing", "guard%": "% less stamina when guarding",
             "arrow%": "% arrow damage", "velocity%": "% arrow speed", "weight%": "% armour weight", "knockback": " knockback", "spell%": "% spell power", "heal%": "% healing",
             "thrall_hp%": "% thrall health", "thrall_dmg%": "% thrall damage", "ash%": "% Ash"}
    return ", ".join(f"+{v:g}{names[k]}" for k, v in stats.items())


def role_of(nb):
    return "gold" if nb.get("ef") or nb.get("gold") else "ember"


def build():
    t = Tree()
    c = CORE
    t.add("core_start", "start", "gold", c["start"]["name"], 0, 0, "core", c["start"]["about"], ef=c["start"]["ef"])
    stat_ids = []
    for i, (name, st) in enumerate(c["smalls"]):
        a = i * math.pi / 4 - math.pi / 2 + math.pi / 8
        stat_ids.append(t.add(f"core_s{i}", "small", "stat", name, 135 * math.cos(a), 135 * math.sin(a) * 1.1, "core",
                              stats=st, ranks=5))
    for i in range(8):
        t.link(stat_ids[i], stat_ids[(i + 1) % 8])
        if i % 2 == 0:
            t.link("core_start", stat_ids[i])
    for i, nb in enumerate(c["notables"]):
        a = i * 2 * math.pi / 10 - math.pi / 2
        x, y = 255 * math.cos(a), 255 * math.sin(a) * 1.1
        nid = t.add(f"core_n{i}", "notable", role_of(nb), nb["name"], x, y, "core", nb["about"], nb.get("stats"),
                    nb.get("fx"), nb.get("ef"))
        near = min(stat_ids, key=lambda s: (t.nodes[s]["x"] - x) ** 2 + (t.nodes[s]["y"] - y) ** 2)
        t.link(near, nid)
    for ar in AREAS:
        aid, ex = ar["id"], EXTRA[ar["id"]]
        pos, _ = FIGURES[aid]
        stats = list(ar["smalls"]) + ex["stats"]
        content = {"N0": ar["notables"][0], "N1": ar["notables"][1], "N2": ar["notables"][2], "N3": ar["notables"][3],
                   "V0": ex["verbs"][0], "V1": ex["verbs"][1], "V2": ex["verbs"][2]}
        for slot in SLOTS:
            x, y = pos[slot]
            nid = f"{aid}_{slot.lower()}"
            if slot[0] == "S":
                i = int(slot[1])
                name, st = stats[i]
                t.add(nid, "small", "stat", name, x, y, aid, stats=st, ranks=RANKS[i])
            elif slot == "K":
                ks = ar["keystone"]
                t.add(nid, "keystone", "key", ks["name"], x, y, aid, ks["about"], ks.get("stats"), ks["fx"], always=ks.get("always"))
            else:
                nb = content[slot]
                t.add(nid, "notable", role_of(nb), nb["name"], x, y, aid, nb["about"], nb.get("stats"), nb.get("fx"), nb.get("ef"))
        for a, b in SLOT_LINKS:
            t.link(f"{aid}_{a.lower()}", f"{aid}_{b.lower()}")
        t.link("core_start", f"{aid}_s0")  # every branch opens straight off the trunk
    for nd in t.nodes.values():
        if nd["kind"] == "small":
            nd["about"] = describe(nd["stats"]) + " per point"
    return t


def area_points(t, area):
    return sum(n["max"] for n in t.nodes.values() if n["area"] == area and n["kind"] != "start")

# --- icons (tools/treeicons.py) ---------------------------------------------------------------------------------------
ATLAS = ROOT / "src/main/resources/assets/ashbound/textures/gui/tree_icons.png"
WEAPON_ICON = {"sword": "sword", "dagger": "dagger", "hammer": "hammer", "spear": "spear", "twohander": "greatsword",
               "shield": "shield", "bow": "bow", "black": "flame", "white": "cross", "summon": "skull"}
STAT_ICON = {"health%": "heart", "stamina": "wind", "stamina_regen%": ("wind", "plus"), "move%": "boot", "armour": "chest",
             "stun_armour": "pillar", "mana": "crystal", "mana_regen%": ("drop", "plus"), "speed%": "slash",
             "negation%": "crack", "impact": "burst", "reach": "spear", "guard%": "shield", "arrow%": "arrow",
             "velocity%": "feather", "spell%": "flame", "heal%": "cross", "thrall_hp%": ("skull", "plus"), "thrall_dmg%": "claw"}
# the Core's stats each keep their own colour (health red, mana blue...), not the Core's pale one
STAT_COLOUR = {"health%": "#e05050", "stamina": "#70c060", "stamina_regen%": "#90d070", "move%": "#d0b080",
               "armour": "#a8b0c0", "stun_armour": "#b09070", "mana": "#5a7ae0", "mana_regen%": "#70a0f0"}
CORE_SPECIAL = "#f0b860"
SPECIAL_ICON = {
    "Ashborn": "flame", "Sidestep": "footprints", "Emergency Escape": ("wind", "star"), "Twin Leap": "wing",
    "Adrenaline": "bolt", "Pillager": "hand", "Adaptive Skin": ("chest", "plus"), "Second Wind": ("heart", "star"),
    "Iron Constitution": ("pillar", "plus"), "Fleetfoot": ("boot", "up"), "Ash Hunger": ("flame", "up"),
    "Swordmaster": ("sword", "star"), "Riposte": "cross_swords", "Flowing Steel": "slash", "Duelist": "eye", "Blade Dance": "spiral",
    "Technician": "hourglass", "Backstab": ("dagger", "x"), "Venom Edge": "vial", "Catharsis": "moon", "Shadow Step": "mask",
    "Meteor Slam": "burst", "Bonebreaker": "bone", "Aftershock": "wave", "Unmoved": "pillar", "Earthshaker": "mountain",
    "Revelation": ("eye", "star"), "Skewer": ("spear", "plus"), "Vault": ("wing", "up"), "Keep Away": "hand", "Impaler": ("spear", "star"),
    "Berserker": "skull", "Endurance": ("chest", "star"), "Forbidden Strength": ("drop", "x"), "Wide Arc": ("slash", "plus"),
    "Titan's Grip": "fist",
    "Parrying": ("shield", "x"), "Impact Guard": ("burst", "plus"), "Taunt": "horn", "Thorns of Iron": "thorns", "Unbreakable": ("shield", "star"),
    "Hunter's Mark": "target", "Volley": "volley", "Steady Aim": "eye", "Skirmisher": ("arrow", "up"), "Deadeye": ("target", "star"),
    "Overload": "bolt", "Lingering Curse": "spiral", "Mana Shield": ("shield", "plus"), "Spellweaver": ("crystal", "star"), "Glass Cannon": "crack",
    "Mending Aura": "ring", "Blessing": "sun", "Purify": ("drop", "plus"), "Sanctuary": ("ring", "star"), "Martyr": ("heart", "x"),
    "Pack Tactics": "claw", "Death Pact": ("skull", "x"), "Long Service": "hourglass", "Bigger Bones": "bone", "Legion": "crown",
}


def icon_key(nd, colours):
    """(motif, badge, colour) for a node"""
    if nd["kind"] != "small":
        m = SPECIAL_ICON[nd["name"]]
        colour = CORE_SPECIAL if nd["area"] == "core" else colours[nd["area"]]
    else:
        stat = next(iter(nd["stats"]))
        m = WEAPON_ICON[nd["area"]] if stat == "dmg%" else STAT_ICON[stat]
        colour = STAT_COLOUR.get(stat, colours[nd["area"]]) if nd["area"] == "core" else colours[nd["area"]]
    motif, badge = (m, None) if isinstance(m, str) else m
    return motif, badge, colour


def icons(t):
    """bakes every node's icon into one atlas (16 to a row) and gives each node its cell"""
    import treeicons
    from PIL import Image
    colours = {a["id"]: a["colour"] for a in AREAS}
    colours["core"] = CORE["colour"]
    cells, specials = {}, []
    for nd in t.nodes.values():
        k = icon_key(nd, colours)
        if k not in cells:
            cells[k] = len(cells)
        nd["icon"] = cells[k]
        if nd["kind"] != "small":
            specials.append((nd["name"], treeicons.icon(k[0], k[2], k[1])))
    # each area's emblem (its weapon) for the overview and the tabs
    area_icon = {}
    for aid, col in colours.items():
        k = ("flame", None, CORE_SPECIAL) if aid == "core" else (WEAPON_ICON[aid], None, col)
        if k not in cells:
            cells[k] = len(cells)
        area_icon[aid] = cells[k]
    rows = (len(cells) + 15) // 16
    atlas = Image.new("RGBA", (256, 16 * rows), (0, 0, 0, 0))
    for k, i in cells.items():
        ic = treeicons.icon(k[0], k[2], k[1])
        atlas.paste(ic, ((i % 16) * 16, (i // 16) * 16), ic)
    ATLAS.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(ATLAS)
    treeicons.sheet(specials, ROOT / "tools/renders/tree_icons.png")
    return rows, area_icon


SPECIAL_ICON.update({
    "Disarm": ("hand", "x"), "Cleaving Arc": ("slash", "star"), "Flourish": ("wind", "up"),
    "Shadow Lunge": ("boot", "star"), "Execute": ("dagger", "star"), "Vanish": ("mask", "plus"),
    "Concussion": ("burst", "star"), "Shatter": ("crack", "plus"), "Momentum": ("wave", "up"),
    "Pin": ("spear", "x"), "Whirl": ("spiral", "plus"), "Charge": ("boot", "up"),
    "Rage": ("flame", "up"), "Sunder": ("greatsword", "x"), "Last Stand": ("pillar", "star"),
    "Shield Bash": ("shield", "up"), "Guardian": ("ring", "plus"), "Retaliate": ("fist", "up"),
    "Piercing Shot": ("arrow", "plus"), "Fire Arrow": ("flame", "x"), "Point Blank": ("target", "plus"),
    "Static": ("bolt", "x"), "Siphon": ("crystal", "up"), "Arcane Surge": ("bolt", "up"),
    "Aegis": ("ring", "x"), "Smite": ("sun", "up"), "Radiance": ("sun", "star"),
    "Soul Harvest": ("skull", "up"), "Frenzy": ("claw", "up"), "Bone Armour": ("bone", "plus"),
})


# --- the overview: a burning ash tree (trunk = the Core, a branch to each area's emblem), in a 1600x900 space ------
def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        u = i / n
        a, b, c, d = (1 - u) ** 3, 3 * u * (1 - u) ** 2, 3 * u * u * (1 - u), u ** 3
        out.append([round(a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], 1), round(a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1], 1)])
    return out


def overview():
    import random
    rnd = random.Random(11)
    bark, branches, emblems = [], {}, {}
    for k in range(9):  # roots
        a = math.pi * (0.1 + 0.8 * k / 8)
        end = (800 + math.cos(a) * rnd.uniform(260, 420), 900 + rnd.uniform(-10, 30))
        bark.append({"pts": bezier((800, 800), (800 + math.cos(a) * 80, 850), (end[0], end[1] - 50), end, 12), "w": [40, 6]})
    trunk = {"pts": bezier((800, 900), (790, 760), (812, 640), (800, 520), 16), "w": [120, 70]}
    n = len(AREAS)
    for i, ar in enumerate(AREAS):
        ex, ey = 138 + i * 147, 520 - 380 * math.sin(math.pi * (i + 0.5) / n)
        emblems[ar["id"]] = [round(ex, 1), round(ey, 1)]
        st = (800 + (i - 4.5) * 7, 600 - abs(i - 4.5) * 18)
        pts = bezier(st, (800 + (ex - 800) * 0.15, st[1] - 120), (ex - (ex - 800) * 0.25, ey + 110), (ex, ey + 6), 24)
        branches[ar["id"]] = {"pts": pts, "w": [34, 12]}
        for u in (0.45, 0.7):  # twigs
            bx, by = pts[int(u * (len(pts) - 1))]
            side = rnd.choice((-1, 1))
            bark.append({"pts": bezier((bx, by), (bx + side * 30, by - 30), (bx + side * 60, by - 50), (bx + side * 70, by - 80), 6), "w": [8, 2]})
    return {"core": [800, 760], "trunk": trunk, "bark": bark, "branches": branches, "emblems": emblems}


# --- node frames: round, diamond and octagon sprites, baked smooth (textures/gui/tree_frames.png) -----------------------
FRAMES = ROOT / "src/main/resources/assets/ashbound/textures/gui/tree_frames.png"
# per role: (locked edge, open edge, taken edge, taken fill); rows in the sheet: stat ember gold key emblem
FRAME_COLOURS = {
    "stat": ((78, 70, 64), (176, 150, 120), (224, 214, 200), (64, 56, 50)),
    "ember": ((96, 54, 28), (210, 118, 50), (255, 146, 54), (76, 36, 14)),
    "gold": ((96, 80, 38), (216, 176, 84), (255, 218, 116), (76, 60, 22)),
    "key": ((96, 28, 34), (196, 64, 64), (244, 76, 76), (76, 16, 22)),
    "emblem": ((92, 80, 72), (190, 150, 110), (255, 150, 50), (44, 31, 24)),
}


RENDERED = ROOT / "tools/renders/frames"  # tools/blender/tree_frames.py


def frames():
    """128px cells: columns locked / open / taken, then a soft glow (row 0) and a plain disc (row 1). The frames are the
    Blender renders when they're there (tools/blender/tree_frames.py), else flat drawn ones."""
    from PIL import Image, ImageDraw, ImageFilter
    S, K = 128, 2
    sheet = Image.new("RGBA", (S * 4, S * 5), (0, 0, 0, 0))
    for row, role in enumerate(FRAME_COLOURS):
        if all((RENDERED / f"{role}_{st}.png").exists() for st in ("locked", "open", "taken")):
            for col, st in enumerate(("locked", "open", "taken")):
                im = Image.open(RENDERED / f"{role}_{st}.png").convert("RGBA").resize((S, S), Image.LANCZOS)
                sheet.paste(im, (col * S, row * S))
            continue
        locked, open_, taken, fill = FRAME_COLOURS[role]
        for col, (edge, inner) in enumerate(((locked, (26, 21, 18)), (open_, (34, 27, 22)), (taken, fill))):
            big = Image.new("RGBA", (S * K, S * K), (0, 0, 0, 0))
            d = ImageDraw.Draw(big)
            m, c, w = 4 * K, S * K / 2, 5 * K if role != "stat" else 4 * K
            r = c - m
            if role == "gold":
                shape = [(c, m), (S * K - m, c), (c, S * K - m), (m, c)]
            elif role == "key":
                shape = [(c + r * math.cos(k * math.pi / 4 + math.pi / 8), c + r * math.sin(k * math.pi / 4 + math.pi / 8)) for k in range(8)]
            else:
                shape = None
            # a dark rim outside, the coloured edge, the fill; a lighter top half on the edge for a bit of bevel
            if shape:
                d.polygon(shape, fill=(14, 10, 9, 255))
                inset = lambda f: [(c + (x - c) * f, c + (y - c) * f) for x, y in shape]
                d.polygon(inset(0.93), fill=edge + (255,))
                d.polygon(inset(0.93 - w / r), fill=inner + (255,))
            else:
                d.ellipse((m, m, S * K - m, S * K - m), fill=(14, 10, 9, 255))
                d.ellipse((m + 2 * K, m + 2 * K, S * K - m - 2 * K, S * K - m - 2 * K), fill=edge + (255,))
                d.ellipse((m + 2 * K + w, m + 2 * K + w, S * K - m - 2 * K - w, S * K - m - 2 * K - w), fill=inner + (255,))
            hi = Image.new("RGBA", big.size, (0, 0, 0, 0))
            ImageDraw.Draw(hi).rectangle((0, 0, S * K, c * 0.9), fill=(255, 255, 255, 34))
            mask = big.split()[3]
            big = Image.alpha_composite(big, Image.composite(hi, Image.new("RGBA", big.size, (0, 0, 0, 0)), mask))
            sheet.paste(big.resize((S, S), Image.LANCZOS), (col * S, row * S))
    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gp = glow.load()
    for y in range(S):
        for x in range(S):
            r = math.hypot(x - S / 2 + 0.5, y - S / 2 + 0.5) / (S / 2)
            gp[x, y] = (255, 255, 255, int(255 * max(0, 1 - r) ** 2))
    sheet.paste(glow, (3 * S, 0))
    disc = Image.new("RGBA", (S * K, S * K), (0, 0, 0, 0))
    ImageDraw.Draw(disc).ellipse((0, 0, S * K - 1, S * K - 1), fill=(255, 255, 255, 255))
    sheet.paste(disc.resize((S, S), Image.LANCZOS), (3 * S, S))
    FRAMES.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(FRAMES)


# each area's emblem: one of the mod's own weapons, rendered by tools/blender/tree_emblems.py (the Core: an ember heart)
EMBLEM_MODEL = {"core": "core", "sword": "abbesss_verdict", "dagger": "last_feather", "hammer": "skybreaker",
                "spear": "pale_lantern", "twohander": "ashveil_requiem", "shield": "velvet_aegis", "bow": "penumbra_bow",
                "black": "tempest_bell", "white": "lamp", "summon": "prayer_of_hands"}
EMBLEMS = ROOT / "src/main/resources/assets/ashbound/textures/gui/tree_emblems.png"


def emblems():
    """packs the emblem renders, brightened a little and with a faint warm outline so they stand off the dark socket,
    into 128px cells (4 to a row); returns each area's cell"""
    from PIL import Image, ImageChops, ImageEnhance, ImageFilter
    S = 128
    order = list(EMBLEM_MODEL)
    sheet = Image.new("RGBA", (S * 4, S * ((len(order) + 3) // 4)), (0, 0, 0, 0))
    for k, aid in enumerate(order):
        im = Image.open(ROOT / f"tools/renders/emblems/{EMBLEM_MODEL[aid]}.png").convert("RGBA").resize((S - 12, S - 12), Image.LANCZOS)
        if aid != "core":
            rgb = ImageEnhance.Brightness(im.convert("RGB")).enhance(1.7)
            im = Image.merge("RGBA", (*rgb.split(), im.split()[3]))
        cell = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        cell.paste(im, (6, 6), im)
        halo = cell.split()[3].filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(3)).point(lambda v: int(v * 0.55))
        glow = Image.new("RGBA", (S, S), (255, 176, 96, 0))
        glow.putalpha(halo)
        sheet.alpha_composite(Image.alpha_composite(glow, cell), ((k % 4) * S, (k // 4) * S))
    sheet.save(EMBLEMS)
    return {aid: k for k, aid in enumerate(order)}


def export(t):
    rows, area_icon = icons(t)
    frames()
    emblem = emblems()
    figure = {a["id"]: [[list(p) for p in line] for line in FIGURES[a["id"]][1]] for a in AREAS}
    figure["core"] = [[list(p) for p in line] for line in CORE_FIGURE]
    page = lambda aid: {k: [n["x"], n["y"]] for k, n in t.nodes.items() if n["area"] == aid}
    data = {"_about": "written by tools/skilltree.py; don't edit", "start": "core_start", "icon_rows": rows, "key_need": KEY_NEED,
            "areas": [{"id": "core", "name": CORE["name"], "colour": CORE["colour"], "icon": area_icon["core"], "emblem": emblem["core"], "page": page("core"),
                       "figure": figure["core"], "points": area_points(t, "core")}] +
                     [{"id": a["id"], "name": a["name"], "colour": a["colour"], "icon": area_icon[a["id"]], "emblem": emblem[a["id"]], "page": page(a["id"]),
                       "figure": figure[a["id"]], "points": area_points(t, a["id"])} for a in AREAS],
            "overview": overview(), "nodes": list(t.nodes.values()), "links": [list(l) for l in sorted(t.links)]}
    OUT.write_text(json.dumps(data, indent=1), encoding="utf-8")


def summary(t):
    kinds = {}
    for nd in t.nodes.values():
        kinds[nd["role"]] = kinds.get(nd["role"], 0) + 1
    ef = [nd["ef"] for nd in t.nodes.values() if nd["ef"]]
    print(f"{len(t.nodes)} nodes ({', '.join(f'{v} {k}' for k, v in kinds.items())}), {len(t.links)} links, "
          f"{len(ef)} Epic Fight skills")
    print("points to fill: " + ", ".join(f"{a} {area_points(t, a)}" for a in ["core"] + [a["id"] for a in AREAS]) +
          f"; total {sum(n['max'] for n in t.nodes.values() if n['kind'] != 'start')}; keystones need {KEY_NEED} in their area")
    fx = sorted({n["fx"] for n in t.nodes.values() if n["fx"]})
    print(f"{len(fx)} mechanics: {' '.join(fx)}")


def preview(t):
    """every page drawn small on one sheet, with the real frames and icons (tools/renders/skilltree.png)"""
    from PIL import Image, ImageDraw, ImageFont
    import treeicons
    font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 13)
    big = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 20)
    sheet = Image.open(FRAMES)
    cw, ch = 520, 470
    img = Image.new("RGB", (cw * 4, ch * 3), (16, 12, 11))
    d = ImageDraw.Draw(img)
    colours = {a["id"]: a["colour"] for a in AREAS}
    colours["core"] = CORE["colour"]
    order = ["core"] + [a["id"] for a in AREAS]
    roles = list(FRAME_COLOURS)
    for i, aid in enumerate(order):
        ox, oy = (i % 4) * cw, (i // 4) * ch
        ids = [k for k, n in t.nodes.items() if n["area"] == aid]
        figs = CORE_FIGURE if aid == "core" else FIGURES[aid][1]
        allp = [(t.nodes[k]["x"], t.nodes[k]["y"]) for k in ids] + [p for line in figs for p in line]
        x0, x1 = min(p[0] for p in allp), max(p[0] for p in allp)
        y0, y1 = min(p[1] for p in allp), max(p[1] for p in allp)
        sc = min((cw - 60) / (x1 - x0), (ch - 80) / (y1 - y0))
        P = lambda x, y: (ox + cw / 2 + (x - (x0 + x1) / 2) * sc, oy + 40 + (ch - 50) / 2 + (y - (y0 + y1) / 2) * sc)
        h = colours[aid]
        dim = tuple(int(int(h[j:j + 2], 16) * 0.32) for j in (1, 3, 5))
        for line in figs:
            d.line([P(*p) for p in line], fill=dim, width=2)
        for a, b in t.links:
            if a in ids and b in ids:
                d.line([P(t.nodes[a]["x"], t.nodes[a]["y"]), P(t.nodes[b]["x"], t.nodes[b]["y"])], fill=(84, 70, 60), width=2)
        for k in ids:
            n = t.nodes[k]
            x, y = P(n["x"], n["y"])
            s = {"stat": 30, "ember": 38, "gold": 40, "key": 50}[n["role"]]
            fr = sheet.crop((64, roles.index(n["role"]) * 64, 128, roles.index(n["role"]) * 64 + 64)).resize((s, s), Image.LANCZOS)
            img.paste(fr, (int(x - s / 2), int(y - s / 2)), fr)
            motif, badge, col = icon_key(n, colours)
            ic = treeicons.icon(motif, col, badge).resize((s // 16 * 16 // 2 * 1 if s < 32 else 32,) * 2, Image.NEAREST)
            img.paste(ic, (int(x - ic.size[0] / 2), int(y - ic.size[1] / 2)), ic)
            label = n["name"] + (f" 0/{n['max']}" if n["max"] > 1 else "")
            d.text((x - d.textlength(label, font) / 2, y + s / 2 + 2), label, font=font, fill=(220, 204, 180))
        d.text((ox + 12, oy + 8), f"{(CORE['name'] if aid == 'core' else next(a['name'] for a in AREAS if a['id'] == aid)).upper()}"
               f"  {area_points(t, aid)} pts", font=big, fill=(255, 190, 100))
    PNG.parent.mkdir(parents=True, exist_ok=True)
    img.save(PNG)
    print("wrote", PNG)


if __name__ == "__main__":
    tree = build()
    export(tree)
    summary(tree)
    if "--preview" in sys.argv:
        preview(tree)
