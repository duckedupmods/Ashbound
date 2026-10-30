"""THE gear table: every dungeon's drops, monsters by role, its ten weapons, six boss weapons and four armour sets
(docs/GEAR.md is the human copy). Everything else reads this: the forge's recipes, the loot, the weapon and armour
generators, the item registry (resources/ashbound/gear.json).

    python tools/gear.py          writes gear.json, the weapons' Epic Fight data and the names
"""
import json
import os
import re

GAME = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace('\\', '/') + '/'
ASSETS = GAME + 'src/main/resources/assets/ashbound/'
DATA = GAME + 'src/main/resources/data/ashbound/'
OUT = GAME + 'src/main/resources/ashbound/gear.json'

TYPES = ['sword', 'dagger', 'hammer', 'spear', 'twohander', 'shield', 'bow', 'black', 'white', 'summon']
BOSS_TYPES = ['sword', 'shield', 'heavy', 'dagger', 'bow', 'staff']

# Epic Fight's moveset for a type, damage and attack speed at rank C, impact, armour negation, most targets a swing.
# Damage set against Epic Fight's real swing timing (balance.py PASS 6, 10/29): the greatsword combo hits ~0.8 a second,
# the sword's 2.1, the dagger's 3.3, so a two-hander hits ~2.7x a sword per swing
STATS = {
    'sword': ('sword', 7.5, 1.6, 0.8, 10, 1),
    'dagger': ('dagger', 4.6, 2.4, 0.4, 15, 1),
    'spear': ('spear', 8.5, 1.2, 1.2, 20, 2),
    'hammer': ('greatsword', 18.0, 0.85, 3.2, 30, 3),    # no hammer moveset in Epic Fight: a maul swings like a greatsword
    'twohander': ('greatsword', 20.0, 0.85, 2.8, 20, 3),
    'shield': ('shield', 0, 0, 0, 0, 0),
    'bow': ('bow', 0, 0, 0, 0, 0),
}
LADDER = 'F E D C B A S'.split()
# weapon damage: 1.08x a rank (one rank up ~1.55x harder with the build and the monsters solved to it, tools/balance.py)
SCALE = {'F': 0.8, 'E': 0.864, 'D': 0.933, 'C': 1.008, 'B': 1.088, 'A': 1.175, 'S': 1.269}
IMPACT_SCALE = {'F': 0.80, 'E': 0.87, 'D': 0.93, 'C': 1.0, 'B': 1.08, 'A': 1.16, 'S': 1.25}  # stagger keeps the old gentle ladder
COST_X = {'F': 1.0, 'E': 1.25, 'D': 1.4, 'C': 1.5, 'B': 1.75, 'A': 2.0, 'S': 2.4}
# common, elite, trophy at rank F
COST = {'helm': (10, 1, 1), 'chest': (16, 2, 0), 'legs': (12, 1, 0), 'boots': (8, 1, 0),
        'dagger': (8, 1, 0), 'sword': (12, 1, 0), 'spear': (12, 1, 0), 'bow': (12, 1, 0), 'hammer': (14, 1, 0),
        'shield': (12, 2, 0), 'twohander': (18, 2, 0), 'black': (10, 2, 0), 'white': (10, 2, 0), 'summon': (10, 2, 0)}
# piece names per armour class: helm, chest, legs, boots
PIECES = {'robe': ('hood', 'robe', 'wraps', 'slippers'), 'light': ('hood', 'jerkin', 'breeches', 'boots'),
          'medium': ('helm', 'hauberk', 'tassets', 'boots'), 'heavy': ('helm', 'cuirass', 'greaves', 'sabatons')}
PIECE_NAMES = {'hood': 'Hood', 'robe': 'Robe', 'wraps': 'Wraps', 'slippers': 'Slippers', 'jerkin': 'Jerkin',
               'breeches': 'Breeches', 'boots': 'Boots', 'helm': 'Helm', 'hauberk': 'Hauberk', 'tassets': 'Tassets',
               'cuirass': 'Cuirass', 'greaves': 'Greaves', 'sabatons': 'Sabatons'}

# The armour sets already made (ported from old Ashbound by efarmor.py): their own piece names.
OLD_SETS = {'bilgewader': ('helm', 'coat', 'waders', 'boots'), 'gibbet': ('hood', 'jerkin', 'breeches', 'boots'),
            'rotwarden': ('cowl', 'robe', 'wraps', 'boots'), 'gravewarden': ('helm', 'breastplate', 'tassets', 'boots'),
            'beakmask': ('helm', 'coat', 'breeches', 'boots'), 'faceless': ('mask', 'plate', 'tassets', 'sabatons'),
            'bonewright': ('helm', 'cuirass', 'greaves', 'sabatons'), 'kilnplate': ('helm', 'cuirass', 'tassets', 'boots')}

# The weapons already made in old Ashbound (E:/Ashbound models/mesh), by their ids there.
OLD_WEAPONS = {'Bilge Falchion': 'bilge_falchion', "Cooper's Mallet": 'coopers_mallet', 'Tidebreaker': 'tidebreaker',
               'Gibbet Knives': 'gibbet_knives', 'Gibbet Greatblade': 'gibbet_greatblade', 'Stagtine Spear': 'stagtine_spear',
               'Thornmother': 'thornmother', 'Candlewake': 'candlewake', "Gravewarden's Oath": 'gravewardens_oath',
               'Plague Bonesaw': 'plague_bonesaw', 'Plague Lancets': 'plague_lancets', 'Plague Pestle': 'plague_pestle',
               'Beak Cane': 'beak_cane', 'Plague Amputator': 'plague_amputator', 'Mercy': 'mercy',
               'Faceless Blade': 'faceless_blade', 'Faceless Fang': 'faceless_fang', 'Faceless Maul': 'faceless_maul',
               'Faceless Lance': 'faceless_lance', 'Faceless Greatsword': 'faceless_greatsword', 'Starfell Edge': 'starfell_edge',
               'Bonewright Blade': 'bonewright_blade', 'Bonewright Shiv': 'bonewright_shiv', 'Bonewright Maul': 'bonewright_maul',
               'Bonewright Pike': 'bonewright_pike', 'Bonewright Greatblade': 'bonewright_greatblade',
               'Brasshog Cleaver': 'brasshog_cleaver', 'Kiln Blade': 'kiln_blade', 'Kiln Fang': 'kiln_fang', 'Kiln Maul': 'kiln_maul',
               'Kiln Pike': 'kiln_pike', 'Kiln Greatsword': 'kiln_greatsword', 'Kilnheart': 'kilnheart',
               'Kiln Bulwark': 'kiln_bulwark', 'Kiln Longbow': 'kiln_longbow'}
IN_GAME = {'kiln_blade', 'kiln_fang', 'kiln_maul', 'kiln_pike', 'kiln_greatsword', 'kiln_bulwark', 'kiln_longbow'}

# ------------------------------------------------------------------------------------------------ the dungeons
# mats: (common, elite, trophy) names; mobs: common, elite (the key-holder), casters (drop the elite 10%), boss.
# weapons in TYPES order; boss: in BOSS_TYPES order, (name, kind for "heavy"/"staff"); sets: robe, light, medium, heavy
# as (id, display prefix). The boss staff's school is the boss row's "staff" kind.
D = []


def dungeon(**kw):
    D.append(kw)


dungeon(gate='cellar', rank='F', title='The Drowned Cellar', element='Undertow',
        mats=('Sodden Cork', "Mimic's Tongue", 'Mother of Vinegar'),
        mobs=['sodden_reveller', 'cask_brute', 'drowned_vintner', 'cellar_eel'], elite='barrel_mimic',
        casters=['drowned_vintner'], boss='cask_mother',
        weapons=['Bilge Falchion', 'Spigot Knife', "Cooper's Mallet", 'Bilge Boathook', 'Stave Cleaver', 'Cask-Lid Shield',
                 'Hoop Bow', 'Sourwell Staff', "Mother's Ladle", 'Revel Tap'],
        boss_weapons=[('Lees Sabre',), ("Mother's Lid",), ('Tidebreaker', 'twohander'), ('Corkscrew',), ('Undertow Bow',),
                      ('Sourmother', 'black')],
        sets=[('vintner', "Vintner's"), ('corkrunner', 'Corkrunner'), ('cooper', "Cooper's"), ('bilgewader', 'Bilgewader')],
        summon='sodden_reveller')

dungeon(gate='gallows', rank='F', title='Gallows Hill', element='Strangle',
        mats=("Hangman's Hemp", 'Gibbet Shackle', "The Hangman's Hood"),
        mobs=['the_dropped', 'noose_walker', 'tar_witch', 'cutpurse'], elite='gibbet_knight', casters=['tar_witch'],
        boss='hangman',
        weapons=["Headsman's Sword", 'Gibbet Knives', 'Trapdoor Maul', 'Gibbet Hook', 'Gibbet Greatblade', 'Gibbet Door',
                 'Noose Bow', 'Tar Staff', 'Last Rites', 'Hanging Tree'],
        boss_weapons=[("Hangman's Verdict",), ('Gallows Gate',), ('The Last Drop', 'twohander'), ('Noose-Cutter',),
                      ('The Long Drop',), ('Thirteen Knots', 'summon')],
        sets=[('tarwitch', 'Tarwitch'), ('gibbet', 'Gibbet'), ('headsman', "Headsman's"), ('gallowsguard', 'Gallowsguard')],
        summon='the_dropped')

dungeon(gate='rotwood', rank='F', title='The Rotwood', element='Bloom',
        mats=('Grey Mycelium', 'Stag Velvet', "The Mossking's Crown"),
        mobs=['the_rooted', 'bark_wight', 'rot_seer', 'thorn_crawler'], elite='rot_stag', casters=['rot_seer'],
        boss='mossking',
        weapons=['Rotbranch Blade', 'Thorn Shiv', 'Burl Maul', 'Stagtine Spear', 'Antler Greatblade', 'Shelf-Fungus Shield',
                 'Yewrot Bow', 'Sporeblight', 'Mossheart', 'Rootcaller'],
        boss_weapons=[("Mossking's Briar",), ('Crownbark',), ('Thornmother', 'twohander'), ('Velvet Tine',), ('Antlerbow',),
                      ('Mosscrown', 'white')],
        sets=[('rotwarden', 'Rotwarden'), ('stagrunner', 'Stagrunner'), ('barkwight', 'Barkwight'), ('heartwood', 'Heartwood')],
        summon='the_rooted')

dungeon(gate='crypt', rank='E', title='The Crypt', element='Wax',
        mats=('Corpse Wax', 'Coffin Bracket', "The Abbot's Death-Mask"),
        mobs=['grave_rat', 'ghoul', 'coffin_knight', 'mourner'], elite='gravedigger', casters=['mourner'], boss='pale_abbot',
        weapons=['Vigil Sword', "Gravedigger's Knife", 'Bellmaul', 'Gravespike', 'Candlewake', 'Coffin-Lid Shield',
                 "Mourner's Bow", 'Wickfire', 'Censer of Rest', 'Ghoulbell'],
        boss_weapons=[('Pale Vigil',), ("Abbot's Reliquary",), ("Gravewarden's Oath", 'twohander'), ('Last Candle',),
                      ('Requiem',), ("Abbot's Crozier", 'summon')],
        sets=[('abbot', "Abbot's"), ('mourner', "Mourner's"), ('gravewarden', 'Gravewarden'), ('coffinplate', 'Coffinplate')],
        summon='ghoul')

dungeon(gate='plague', rank='D', title='The Plague Ward', element='Fever',
        mats=('Lime Gauze', 'Beak Resin', "The Surgeon's Lamp"),
        mobs=['bell_leper', 'bloated_patient', 'lime_friar', 'orderly'], elite='plague_doctor', casters=['lime_friar'],
        boss='surgeon',
        weapons=['Plague Bonesaw', 'Plague Lancets', 'Plague Pestle', 'Beak Cane', 'Plague Amputator', 'Quarantine Door',
                 'Tourniquet Bow', 'Miasma Censer', 'Limelight Staff', "Leper's Bell"],
        boss_weapons=[('Mercy',), ("Surgeon's Tray",), ("Surgeon's Probe", 'spear'), ('Scalpel Saint',), ('Suture Bow',),
                      ('Lampbearer', 'white')],
        sets=[('beakmask', 'Beakmask'), ('orderly', "Orderly's"), ('friar', "Friar's"), ('quarantine', 'Quarantine')],
        summon='bell_leper')

dungeon(gate='temple', rank='C', title='The Faceless Temple', element='Crystallize',
        mats=('Mana Shard', 'Stolen Visage', "The Sovereign's Mask"),
        mobs=['sentinel', 'hollow', 'acolyte', 'mask_crawler'], elite='facetaker', casters=['acolyte'], boss='sovereign',
        weapons=['Faceless Blade', 'Faceless Fang', 'Faceless Maul', 'Faceless Lance', 'Faceless Greatsword',
                 'Mirror of No Face', 'Shardstring Bow', 'Shardcaller', 'Veilhealer', 'Maskbearer'],
        boss_weapons=[("Sovereign's Edge",), ('Thousand-Face Aegis',), ('Starfell Edge', 'twohander'), ('Visage Thief',),
                      ('Starfall Bow',), ('Manacrown', 'black')],
        sets=[('acolyte', "Acolyte's"), ('faceless', 'Faceless'), ('sentinel', "Sentinel's"), ('sovereign', 'Sovereign')],
        summon='hollow')

dungeon(gate='ossuary', rank='C', title='The Ossuary Engine', element='Toll',
        mats=('Grave Brass', 'Soul Wick', 'Engine Heart'),
        mobs=['stitched', 'wickling', 'cantor', 'bone_hound'], elite='pallbearer', casters=['cantor'], boss='assembler',
        weapons=['Bonewright Blade', 'Bonewright Shiv', 'Bonewright Maul', 'Bonewright Pike', 'Bonewright Greatblade',
                 'Ribcage Shield', 'Brass Recurve', 'Wickflame', 'Hymn Staff', "Assembler's Crank"],
        boss_weapons=[('Engine Blade',), ('Boilerplate',), ('Brasshog Cleaver', 'twohander'), ('Piston Shiv',),
                      ('Steam Arbalest',), ("Assembler's Heart", 'summon')],
        sets=[('cantor', "Cantor's"), ('stitchhide', 'Stitchhide'), ('bonewright', 'Bonewright'), ('pallbearer', 'Pallbearer')],
        summon='bone_hound')

dungeon(gate='foundry', rank='C', title='The Slag Foundry', element='Brand',
        mats=('Slag Iron', 'Crucible Ember', "Kiln-Father's Brand"),
        mobs=['slagling', 'riveter', 'bellows_priest', 'cinderhusk'], elite='crucible_bearer', casters=['bellows_priest'],
        boss='ossric',
        weapons=['Kiln Blade', 'Kiln Fang', 'Kiln Maul', 'Kiln Pike', 'Kiln Greatsword', 'Kiln Bulwark', 'Kiln Longbow',
                 'Crucible Staff', 'Hearth Staff', 'Slagmother'],
        boss_weapons=[('Brandsteel',), ('Furnace Door',), ('Kilnheart', 'twohander'), ('Ember Fang',), ('Bellows Bow',),
                      ("Ossric's Brand", 'black')],
        sets=[('bellows', 'Bellows'), ('slagrunner', 'Slagrunner'), ('riveter', "Riveter's"), ('kilnplate', 'Kilnplate')],
        summon='slagling')

dungeon(gate='frost', rank='B', title='The Frozen Procession', element='Rime',
        mats=('Rime Shard', 'Frozen Fletch', "The Marshal's Heart"),
        mobs=['frostbound', 'frostbound_archer', 'rime_knight', 'frost_chaplain'], elite='standard_bearer',
        casters=['frost_chaplain'], boss='winter_marshal',
        weapons=['Rime Sword', 'Icicle Dirk', 'Glacier Maul', 'Frostbound Pike', 'Procession Greatsword', 'Glacier Tower',
                 'Frostbound Longbow', 'Blizzard Staff', 'Thaw Staff', 'Banner of the March'],
        boss_weapons=[("Marshal's Sabre",), ('Winter Standard',), ('Wintermarch', 'spear'), ('Frostbite',),
                      ('Hoarfrost Bow',), ('Last Ember', 'white')],
        sets=[('snowshroud', 'Snowshroud'), ('hoarstep', 'Hoarstep'), ('marcher', "Marcher's"), ('rimeguard', 'Rimeguard')],
        summon='frostbound')

dungeon(gate='silk', rank='B', title='The Silk Archive', element='Bind',
        mats=('Silk Thread', 'Ink Gland', "The Queen's Spinneret"),
        mobs=['bound_scholar', 'lector', 'inkbound', 'silk_mite'], elite='weaver', casters=['lector'], boss='silk_queen',
        weapons=["Scrivener's Blade", 'Quill Knife', "Bookbinder's Maul", 'Spindle Spear', 'Folio Cleaver', 'Tome Shield',
                 'Silkstring Bow', 'Inkblot Staff', 'Mending Spool', 'Brood Distaff'],
        boss_weapons=[("Queen's Needle",), ('Cocoon Aegis',), ('Widowmaker', 'twohander'), ('Fang of the Queen',),
                      ('Webcaster',), ('Spinneret Crown', 'summon')],
        sets=[('archivist', "Archivist's"), ('silkrunner', 'Silkrunner'), ('lector', "Lector's"), ('bindplate', 'Bindplate')],
        summon='silk_mite')

# ---------------------------------------------------------------- Roster v2: the 15 built in phase 5 (docs/BUILD_ALL.md)

dungeon(gate='weeping_mine', rank='E', title='The Weeping Mine', element='Vein', colour=0x5fd6c0,
        mats=('Weeping Crystal', "Foreman's Lamp", 'Heart of the Vein'),
        mobs=['shard_crawler', 'cart_golem', 'lamp_miner', 'blind_burrower'], elite='foreman', casters=['lamp_miner'],
        boss='the_vein',
        weapons=['Seam Cutter', 'Pick-Knife', 'Ore Hammer', 'Drill Lance', 'Tunnel Cleaver', 'Minecart Shield',
                 'Lampwick Bow', 'Gloomvein Staff', 'Weeping Lantern', 'Crawler Lamp'],
        boss_weapons=[('Veinsplitter',), ('Bedrock Aegis',), ('Motherlode', 'hammer'), ('Shardfang',), ('Deep Seam Bow',),
                      ('Heartvein', 'black')],
        sets=[('lampwright', "Lampwright's"), ('tunnelrat', 'Tunnelrat'), ('shaftman', "Shaftman's"), ('deepdelver', 'Deepdelver')],
        summon='shard_crawler')

dungeon(gate='tide_chapel', rank='E', title='The Tide Chapel', element='Brine', colour=0x3fa8a0,
        mats=('Barnacle Crust', 'Choir Pearl', "The Drowned Bell's Clapper"),
        mobs=['tide_crab', 'crab_knight', 'tide_priest', 'net_thrower'], elite='barnacle_choir', casters=['tide_priest'],
        boss='drowned_bell',
        weapons=['Wreck Cutlass', 'Barnacle Shiv', 'Anchor Maul', 'Tide Harpoon', 'Keel Greatblade', 'Bell Shield',
                 'Driftwood Bow', 'Kelpblack Staff', 'Chapel Lamp', 'Crabcaller'],
        boss_weapons=[('Longmourn',), ('Bellwall',), ('Toll of the Deep', 'hammer'), ('Pearl Stiletto',), ('Shoreline Bow',),
                      ('Bellringer', 'white')],
        sets=[('tidepriest', "Tidepriest's"), ('netrunner', 'Netrunner'), ('wrackmail', 'Wrackmail'), ('brineclad', 'Brineclad')],
        summon='tide_crab')

dungeon(gate='brigands_gorge', rank='E', title="The Brigand's Gorge", element='Ambush', colour=0xc8743a,
        mats=('Stolen Coin', "Lieutenant's Seal", "The Bandit King's Crown"),
        mobs=['footpad', 'gorge_ogre', 'hedge_hexer', 'knife_dancer'], elite='bandit_lieutenant', casters=['hedge_hexer'],
        boss='red_jack',
        weapons=['Highwayman Sabre', 'Cutthroat Knife', 'Gorge Club', 'Pike of the Pass', 'Ogre Cleaver', 'Toll-Gate Shield',
                 'Ambush Bow', 'Charm Staff', 'Poultice Staff', 'Banditcaller'],
        boss_weapons=[("Red Jack's Sabre",), ('Kingshield',), ('Ransom', 'twohander'), ('Purse-Slitter',), ('Gorge Longbow',),
                      ('Crown of Thieves', 'summon')],
        sets=[('hexer', "Hexer's"), ('outlaw', 'Outlaw'), ('highwayman', "Highwayman's"), ('gorgeguard', 'Gorgeguard')],
        summon='footpad')

dungeon(gate='rookery', rank='D', title='The Rookery', element='Carrion', colour=0x7a6aa8,
        mats=('Black Pinion', "Captain's Talon", "The Raven Mother's Eye"),
        mobs=['carrion_crow', 'crowbrute', 'augur', 'feather_blade'], elite='rook_captain', casters=['augur'],
        boss='raven_mother',
        weapons=['Rook Sabre', 'Talon Knife', 'Beak Hammer', 'Rookery Spear', 'Wingblade', 'Rook Kite Shield',
                 'Crowfletch Bow', 'Omen Staff', 'Carrion Mercy', 'Murder Staff'],
        boss_weapons=[("Mother's Pinion",), ('Black Wing Aegis',), ('Nevermore', 'spear'), ('Eyepick',), ('Raven Bow',),
                      ('The Murder', 'summon')],
        sets=[('augur', "Augur's"), ('featherblade', 'Featherblade'), ('ravenmantle', 'Ravenmantle'), ('rookplate', 'Rookplate')],
        summon='carrion_crow')

dungeon(gate='hollow_circus', rank='D', title='The Hollow Circus', element='Jest', colour=0xe04a6a,
        mats=('Greasepaint', "Harlequin's Bell", "The Ringmaster's Top Hat"),
        mobs=['circus_puppet', 'strongman', 'fire_eater', 'knife_juggler'], elite='harlequin', casters=['fire_eater'],
        boss='ringmaster',
        weapons=['Ringmaster Rapier', 'Juggling Knives', 'Strongman Mallet', 'Lion-Tamer Lance', 'Big-Top Cleaver', 'Target Shield',
                 'Trick Bow', 'Fire-Breath Staff', 'Applause Staff', 'Puppeteer Cross'],
        boss_weapons=[('Showstopper',), ('Grand Ring',), ('Final Act', 'twohander'), ('Knife-Thrower Pick',), ('Calliope Bow',),
                      ('Strings Attached', 'summon')],
        sets=[('fireeater', 'Fire-Eater'), ('motley', 'Motley'), ('ringhand', 'Ringhand'), ('ringiron', 'Ringiron')],
        summon='circus_puppet')

dungeon(gate='mirefen_coven', rank='D', title='The Mirefen Coven', element='Hex', colour=0x6a9a3a,
        mats=('Bog Myrtle', "Matron's Hex-Knot", "Mother Mire's Cauldron Heart"),
        mobs=['mire_thrall', 'bog_troll', 'hag_sister', 'fen_crawler'], elite='coven_matron', casters=['hag_sister'],
        boss='mother_mire',
        weapons=['Reedblade', 'Toad Knife', 'Bog-Oak Maul', 'Eel Spear', 'Mirecleaver', 'Coracle Shield',
                 'Willow Bow', 'Hexbag Staff', 'Swamp Lantern', 'Toadcaller'],
        boss_weapons=[("Matron's Sickle",), ('Cauldron Lid',), ('Drowning Pool', 'hammer'), ("Hag's Nail",), ('Wisp Bow',),
                      ('Coven Broom', 'black')],
        sets=[('hexweave', 'Hexweave'), ('bogrunner', 'Bogrunner'), ('fenwarden', 'Fenwarden'), ('trollhide', 'Trollhide')],
        summon='mire_thrall')

dungeon(gate='sandsunk_tomb', rank='C', title='The Sandsunk Tomb', element='Sunburn', colour=0xf0c040,
        mats=('Tomb Linen', "Guardian's Ankh", "The Sun-King's Scarab"),
        mobs=['tomb_scarab', 'sand_colossus', 'embalmer', 'jackal_runner'], elite='sun_guardian', casters=['embalmer'],
        boss='sun_king',
        weapons=['Khopesh', 'Scarab Dagger', 'Obelisk Maul', 'Sunspear', 'Sickle Greatblade', 'Sun-Disc Shield',
                 'Reed Bow', 'Sandstorm Staff', 'Ankh Staff', 'Canopic Staff'],
        boss_weapons=[('Sunflayer',), ('Solar Aegis',), ("Sun-King's Flail", 'hammer'), ('Scarab Fang',), ('Horizon Bow',),
                      ('Crown of the Sun', 'white')],
        sets=[('linenwrap', 'Linenwrap'), ('jackalrunner', 'Jackalrunner'), ('sunscale', 'Sunscale'), ('tombguard', 'Tombguard')],
        summon='tomb_scarab')

dungeon(gate='fallen_titan', rank='B', title='The Fallen Titan', element='Marrow', colour=0xd04848,
        mats=('Titan Sinew', 'Valve Shard', 'The Heartstring'),
        mobs=['burrow_leech', 'marrow_brute', 'bile_priest', 'sinew_stalker'], elite='heart_warden', casters=['bile_priest'],
        boss='still_heart',
        weapons=['Rib', 'Fangs', 'Knuckle', 'Femur Spear', 'Jawbone', 'Valve Shield',
                 'Sinew Bow', 'Bile Staff', 'Lifeblood Staff', 'Leechcaller'],
        boss_weapons=[('Aorta',), ('Heart Valve',), ('Systole', 'hammer'), ('Fang of the Titan',), ('Tendon Bow',),
                      ('Diastole', 'white')],
        sets=[('bilepriest', "Bile Priest's"), ('sinewrunner', 'Sinewrunner'), ('marrowplate', 'Marrowplate'), ('titanbone', 'Titanbone')],
        summon='burrow_leech')

dungeon(gate='jade_monastery', rank='B', title='The Jade Monastery', element='Jade', colour=0x40c878,
        mats=('Jade Bead', "Abbot's Prayer Wheel", "The Thousand Hands' Seal"),
        mobs=['jade_acolyte', 'stone_lion', 'incense_monk', 'shadow_monk'], elite='fist_abbot', casters=['incense_monk'],
        boss='thousand_hands',
        weapons=['Jade Jian', 'Mantis Knife', 'Prayer Hammer', 'Crescent Spear', 'Guandao', 'Lotus Shield',
                 'Bamboo Bow', 'Ink-Brush Staff', 'Incense Staff', 'Acolyte Bell'],
        boss_weapons=[('Thousand-Hand Jian',), ('Lotus Throne',), ("Heaven's Guandao", 'spear'), ('Jade Fang',), ('Moon-Gate Bow',),
                      ('Prayer of Hands', 'summon')],
        sets=[('incenserobe', 'Incense'), ('jadeguard', 'Jadeguard'), ('lionward', 'Lionward'), ('templeguard', 'Templeguard')],
        summon='jade_acolyte')

dungeon(gate='storm_bastion', rank='A', title='The Storm Bastion', element='Thunder', colour=0x8ab4ff,
        mats=('Storm Glass', "Captain's Rod", "The Abbess's Bell"),
        mobs=['spark_hound', 'thunder_ogre', 'storm_caller', 'gale_knight'], elite='storm_captain', casters=['storm_caller'],
        boss='thunder_abbess',
        weapons=['Gale Sabre', 'Spark Knife', 'Thunder Maul', 'Lightning Rod Spear', 'Stormcleaver', 'Bastion Shield',
                 'Thunderhead Bow', 'Tempest Staff', 'Calm-Eye Staff', 'Sparkcaller'],
        boss_weapons=[("Abbess's Verdict",), ('Lightning Rod Aegis',), ('Skybreaker', 'hammer'), ('Static Fang',), ('Bolt of Heaven',),
                      ('Tempest Bell', 'black')],
        sets=[('stormcaller', "Stormcaller's"), ('galerunner', 'Galerunner'), ('bastionmail', 'Bastionmail'), ('stormhelm', 'Stormhelm')],
        summon='spark_hound')

dungeon(gate='bloodmoon_court', rank='A', title='The Bloodmoon Court', element='Blood', colour=0xb01030,
        mats=('Blood Velvet', "Hound's Collar", "Countess Vael's Heart"),
        mobs=['blood_thrall', 'gorged_butler', 'blood_mage', 'duelist'], elite='counts_hound', casters=['blood_mage'],
        boss='countess_vael',
        weapons=['Court Rapier', 'Fang Dagger', 'Gilded Mace', 'Partisan', "Executioner's Claymore", 'Crest Shield',
                 'Crimson Bow', 'Hemomancer Staff', 'Transfusion Staff', 'Thrallcaller'],
        boss_weapons=[("Countess's Rapier",), ('Velvet Aegis',), ('Kingsplitter', 'twohander'), ("Vael's Fang",), ('Bloodmoon Bow',),
                      ('Crimson Chalice', 'summon')],
        sets=[('sanguine', 'Sanguine'), ('fencer', "Fencer's"), ('courtier', "Courtier's"), ('nightguard', 'Nightguard')],
        summon='blood_thrall')

dungeon(gate='obsidian_labyrinth', rank='A', title='The Obsidian Labyrinth', element='Ember', colour=0xff6a20,
        mats=('Obsidian Shard', "Gatekeeper's Key", "The Minotaur's Horn"),
        mobs=['labyrinth_imp', 'basalt_ogre', 'ember_oracle', 'horned_runner'], elite='gatekeeper', casters=['ember_oracle'],
        boss='minotaur',
        weapons=['Obsidian Blade', 'Glass Shiv', 'Basalt Maul', 'Labyrinth Pike', 'Ninth Gate Axe', 'Maze-Wall Shield',
                 'Ember Bow', 'Cinder Oracle Staff', 'Mending Ember', 'Impcaller'],
        boss_weapons=[('Thread of the Maze',), ('Ninth Gate',), ('Labrys', 'twohander'), ('Horn Shard',), ('Obsidian Longbow',),
                      ("Bull's Crown", 'black')],
        sets=[('oracle', "Oracle's"), ('hornrunner', 'Hornrunner'), ('hornbreaker', 'Hornbreaker'), ('basaltplate', 'Basaltplate')],
        summon='labyrinth_imp')

dungeon(gate='abyssal_lighthouse', rank='S', title='The Abyssal Lighthouse', element='Abyss', colour=0x2a6aff,
        mats=('Deep Pearl', "Angler's Lure", "The Keeper's Lens"),
        mobs=['deep_thing', 'drowned_keeper', 'lamp_siren', 'eyeless'], elite='angler_knight', casters=['lamp_siren'],
        boss='keeper_in_light',
        weapons=['Lightkeeper Sword', 'Lure Knife', 'Foghorn Hammer', 'Angler Spear', 'Leviathan Cleaver', 'Lens Shield',
                 'Deepline Bow', 'Abyss Staff', 'Beacon Staff', 'Deepcaller'],
        boss_weapons=[('Lighthouse Edge',), ('Lens of the Keeper',), ('Pale Lantern', 'spear'), ('Lure Fang',), ('Beam Bow',),
                      ('The Lamp', 'white')],
        sets=[('abysswatch', 'Abysswatch'), ('deepsight', 'Deepsight'), ('lampkeeper', "Lampkeeper's"), ('anglerplate', 'Anglerplate')],
        summon='deep_thing')

dungeon(gate='eclipse_cathedral', rank='S', title='The Eclipse Cathedral', element='Eclipse', colour=0xffd860,
        mats=('Black Gold Leaf', 'Seraph Feather', "The Fallen Seraph's Halo"),
        mobs=['cherub_husk', 'halo_knight', 'ash_choir', 'fallen_blade'], elite='seraph_warden', casters=['ash_choir'],
        boss='fallen_seraph',
        weapons=['Seraph Blade', 'Black Feather', 'Censer Maul', 'Halo Lance', 'Eclipse Greatsword', 'Cathedral Shield',
                 'Wingbow', 'Umbra Staff', 'Corona Staff', 'Cherubcaller'],
        boss_weapons=[('Fallen Grace',), ('Black Sun Aegis',), ('Ashveil Requiem', 'twohander'), ('Last Feather',), ('Penumbra Bow',),
                      ('Totality', 'black')],
        sets=[('ashchoir', 'Ash Choir'), ('fallenblade', 'Fallenblade'), ('haloguard', 'Haloguard'), ('eclipse', 'Eclipse')],
        summon='cherub_husk')

dungeon(gate='wyrms_hoard', rank='S', title="The Wyrm's Hoard", element='Wyrmfire', colour=0xff9a20,
        mats=('Hoard Gold', "Wyrm Priest's Scale", "Ignavar's Heart-Ember"),
        mobs=['kobold', 'hoard_golem', 'ash_cultist', 'drake'], elite='wyrm_priest', casters=['ash_cultist'],
        boss='ignavar',
        weapons=['Drakefang Sword', 'Kobold Shiv', 'Hoard Hammer', 'Drake Lance', 'Wyrmcleaver', 'Gold-Heap Shield',
                 'Dragonbone Bow', 'Cinder Cult Staff', 'Ember Heart Staff', 'Koboldcaller'],
        boss_weapons=[("Ignavar's Claw",), ('Scale of Ignavar',), ('Hoardbreaker', 'hammer'), ('Wyrm Tooth',), ('Dragonbreath Bow',),
                      ('Ash Crown', 'black')],
        sets=[('ashcultist', 'Ash Cultist'), ('scalehide', 'Scalehide'), ('wyrmscale', 'Wyrmscale'), ('hoardplate', 'Hoardplate')],
        summon='kobold')


# ================================================================ world towers (docs/TOWERS.md): a dungeon's kit, no gate

dungeon(gate='clockwork_spire', rank='C', title='The Clockwork Spire', element='Steam', colour=0xffb53a,
        mats=('Brass Cog', 'Mainspring', "The Horologe's Heart"),
        mobs=['cogling', 'brass_sentry', 'steam_hulk', 'tinker_adept'], elite='clockwork_duelist', casters=['tinker_adept'],
        boss='grand_horologe',
        weapons=[], boss_weapons=[],          # no tower weapons: their hoards give the world's (worldarms.py)
        sets=[('horologist', "Horologist's"), ('tinker', "Tinker's"), ('brasswork', 'Brasswork'), ('gearwright', 'Gearwright')],
        summon='cogling')

dungeon(gate='serpent_ziggurat', rank='C', title='The Coiled Spire', element='Venom', colour=0x3ad486,
        mats=('Jade Scale', "Champion's Plume", "The Coiled King's Fang"),
        mobs=['coilspawn', 'scaleguard', 'jaguar_stalker', 'venom_priest'], elite='feathered_champion', casters=['venom_priest'],
        boss='coiled_king',
        weapons=[], boss_weapons=[],          # no tower weapons: their hoards give the world's (worldarms.py)
        sets=[('scaleguard', 'Scaleguard'), ('jaguar', 'Jaguar'), ('venomweave', 'Venomweave'), ('plumed', 'Plumed')],
        summon='coilspawn')

dungeon(gate='rimeholt', rank='B', title='Rimeholt', element='Rime', colour=0x5ab8f4,
        mats=('Hrimstone', 'Winter Wolf Pelt', "Hrimgar's Frozen Heart"),
        mobs=['rime_thrall', 'frost_troll', 'huskarl', 'rune_seer'], elite='winter_wolf', casters=['rune_seer'],
        boss='jarl_hrimgar',
        weapons=[], boss_weapons=[],          # no tower weapons: their hoards give the world's (worldarms.py)
        sets=[('runeseer', 'Runeseer'), ('wolfskin', 'Wolfskin'), ('huskarl', 'Huskarl'), ('giantplate', 'Giantplate')],
        summon='rime_thrall')

dungeon(gate='glass_minaret', rank='B', title='The Glass Minaret', element='Sunfire', colour=0xffc84a,
        mats=('Sun Glass', "Dancer's Bell", "The Sultan's Lamp"),
        mobs=['dune_scorpion', 'glass_golem', 'mirror_guard', 'sandwraith'], elite='blade_dancer', casters=['sandwraith'],
        boss='djinn_sultan',
        weapons=[], boss_weapons=[],          # no tower weapons: their hoards give the world's (worldarms.py)
        sets=[('sandwraith', 'Sandwraith'), ('dancer', "Dancer's"), ('mirrorguard', 'Mirrorguard'), ('sultan', "Sultan's")],
        summon='dune_scorpion')

dungeon(gate='warlords_fang', rank='C', title="The Warlord's Fang", element='Fury', colour=0xff6a2a,
        mats=('Orc Tusk', 'Warg Fang', "Gorrak's War Crown"),
        mobs=['goblin_cutthroat', 'orc_brute', 'orc_raider', 'goblin_shaman'], elite='warg_rider', casters=['goblin_shaman'],
        boss='gorrak',
        weapons=[], boss_weapons=[],          # no tower weapons: their hoards give the world's (worldarms.py)
        sets=[('shaman', 'Shaman'), ('cutthroat', 'Cutthroat'), ('raider', 'Raider'), ('warplate', 'Warplate')],
        summon='goblin_cutthroat')


def slug(name):
    s = name.lower().replace("'s", 's').replace("'", '')
    s = re.sub(r'^the ', '', s)
    return re.sub(r'[^a-z0-9]+', '_', s).strip('_')


def cost(kind, rank):
    c, e, t = COST[kind]
    x = COST_X[rank]
    return {'common': int(round(c * x)), 'elite': int(round(e * x)) if e else 0, 'trophy': t}


def up(rank, n):
    return LADDER[min(len(LADDER) - 1, LADDER.index(rank) + n)]


def build():
    out = []
    for d in D:
        g = dict(gate=d['gate'], rank=d['rank'], title=d['title'], element=d['element'], boss=d['boss'],
                 elite=d['elite'], mobs=d['mobs'], casters=d['casters'], summon=d['summon'])
        if 'colour' in d:
            g['colour'] = d['colour']
        # a Roster v2 dungeon whose lair is built: GateDungeons opens gates onto it (debris: its first blocks)
        if os.path.exists(GAME + 'src/main/resources/data/ashbound/lair/gate_%s.bin' % d['gate']) and 'colour' in d:
            import dforge
            g['lair'] = 'gate_' + d['gate']
            g['debris'] = [b['name'] for b in dforge.DUNGEONS[d['gate']]['blocks'] if b['paint'] not in ('column', 'log')][:5]
        g['mats'] = [{'id': {"The Mossking's Crown": 'mossking_crown'}.get(n, slug(n)), 'name': n, 'role': r} for n, r in zip(d['mats'], ('common', 'elite', 'trophy'))]
        items = []
        for kind, name in zip(TYPES, d['weapons']):
            iid = OLD_WEAPONS.get(name, slug(name))
            items.append(dict(id=iid, name=name, kind=kind, rank=d['rank'], boss=False, cost=cost(kind, d['rank']),
                              old=name in OLD_WEAPONS))
        for slot, row in zip(BOSS_TYPES, d['boss_weapons']):
            name = row[0]
            kind = row[1] if len(row) > 1 else slot
            iid = OLD_WEAPONS.get(name, slug(name))
            items.append(dict(id=iid, name=name, kind=kind, rank=up(d['rank'], 2), boss=True, slot=slot,
                              old=name in OLD_WEAPONS))
        sets = []
        for cls, (sid, prefix) in zip(('robe', 'light', 'medium', 'heavy'), d['sets']):
            parts = OLD_SETS.get(sid, PIECES[cls])
            pieces = []
            for slot, part in zip(('helm', 'chest', 'legs', 'boots'), parts):
                pieces.append(dict(id='%s_%s' % (sid, part), name='%s %s' % (prefix, PIECE_NAMES.get(part, part.title())),
                                   slot=slot, cost=cost(slot, d['rank'])))
            sets.append(dict(id=sid, cls=cls, prefix=prefix, old=sid in OLD_SETS, pieces=pieces))
        g['weapons'] = items
        g['sets'] = sets
        out.append(g)
    return out


def stats(item):
    """damage, speed, impact, negation, strikes for a melee weapon"""
    ef, dmg, spd, imp, neg, strikes = STATS[item['kind']]
    x = SCALE[item['rank']]
    return ef, round(dmg * x * (1.08 if item['boss'] else 1.0), 1), spd, round(imp * IMPACT_SCALE[item['rank']], 2), neg, strikes


def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)


OLD_ITEMS = 'E:/Ashbound/src/main/resources/assets/ashbound/textures/item/'


def outline(src, dst):
    """an icon made solid (no half see-through rim) and outlined in a dark shade of its own edge"""
    from PIL import Image
    im = Image.open(src).convert('RGBA')
    W, H = im.size
    px = im.load()
    solid = {(x, y) for y in range(H) for x in range(W) if px[x, y][3] >= 128}
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    o = out.load()
    for x, y in solid:
        o[x, y] = px[x, y][:3] + (255,)
    for y in range(H):
        for x in range(W):
            if (x, y) in solid:
                continue
            nb = [px[x + dx, y + dy] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if (x + dx, y + dy) in solid]
            if nb:
                o[x, y] = tuple(int(sum(c[i] for c in nb) / len(nb) * 0.18) + 8 for i in range(3)) + (255,)
    out.save(dst)


def mat_items(gear):
    """the drops' item models; their icons from old Ashbound where it made them (the rest: tools/vox_mats.py)"""
    for g in gear:
        for m in g['mats']:
            dst = ASSETS + 'textures/item/%s.png' % m['id']
            if os.path.exists(OLD_ITEMS + m['id'] + '.png') and not os.path.exists(dst):
                outline(OLD_ITEMS + m['id'] + '.png', dst)
            dump(ASSETS + 'models/item/%s.json' % m['id'], {'parent': 'minecraft:item/generated',
                                                            'textures': {'layer0': 'ashbound:item/' + m['id']}})


STAFF_CAP = {'type': 'ashbound:staff', 'attributes': {'common': {'impact': 0.5, 'armor_negation': 0, 'max_strikes': 1}}}   # Movesets.java


def main():
    gear = build()
    mat_items(gear)
    for g in gear:
        for it in g['weapons']:
            if it['kind'] in STATS:
                ef, dmg, spd, imp, neg, strikes = stats(it)
                it['ef'], it['damage'], it['speed'] = ef, dmg, spd
                # our greatsword: Epic Fight's, held up in front between swings (Movesets.java)
                cap = {'type': ('ashbound:' if ef == 'greatsword' else 'epicfight:') + ef}
                if ef not in ('shield', 'bow'):
                    cap['attributes'] = {'common': {'impact': imp, 'armor_negation': neg, 'max_strikes': strikes}}
                dump(DATA + 'capabilities/weapons/%s.json' % it['id'], cap)
            else:
                it['school'] = it['kind']
                dump(DATA + 'capabilities/weapons/%s.json' % it['id'], STAFF_CAP)
    dump(OUT, gear)
    lang = json.load(open(ASSETS + 'lang/en_us.json', encoding='utf-8'))
    for g in gear:
        for m in g['mats']:
            lang['item.ashbound.' + m['id']] = m['name']
        for it in g['weapons']:
            lang['item.ashbound.' + it['id']] = it['name']
        for s in g['sets']:
            for p in s['pieces']:
                lang['item.ashbound.' + p['id']] = p['name']
    for k, v in {'block.ashbound.gate_forge': 'Gate Forge', 'item.ashbound.gate_forge': 'Gate Forge',
                 'attribute.ashbound.spell_power': 'Spell Power', 'attribute.ashbound.max_mana': 'Mana',
                 'attribute.ashbound.mana_regen': 'Mana Regeneration',
                 'item.ashbound.apprentice_black_staff': "Apprentice's Black Staff",
                 'item.ashbound.apprentice_white_staff': "Apprentice's White Staff",
                 'item.ashbound.apprentice_summon_staff': "Apprentice's Summoning Staff",
                 'entity.ashbound.spell_bolt': 'Spell Bolt'}.items():
        lang[k] = v
    dump(ASSETS + 'lang/en_us.json', lang)
    ids = [it['id'] for g in gear for it in g['weapons']] + [m['id'] for g in gear for m in g['mats']] + \
          [p['id'] for g in gear for s in g['sets'] for p in s['pieces']]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    print('dungeons', len(gear), 'weapons', sum(len(g['weapons']) for g in gear), 'sets', sum(len(g['sets']) for g in gear),
          'mats', sum(len(g['mats']) for g in gear), 'duplicate ids', dup)
    import pixicons                     # every rendered icon as pixel art, last
    pixicons.run()


if __name__ == '__main__':
    main()
