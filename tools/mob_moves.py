"""How every gate monster fights: its stance (the weapon it swings, so Epic Fight's moves for it) and its own skills
(MobSkills.java), a boss's unlocking phase by phase ("skill@2" from 66% health, "@3" from 33%). Written to
/ashbound/mob_moves.json; MobMoves.java builds each one's combat from it, its reach grown with its size.

    python tools/mob_moves.py

Stances: sword, dual (two blades), greatsword, longsword, rapier, sabre, spear, dagger, twin_daggers, axe,
twin_axes, maul (two-handed blunt), fist, claw (feral, bare hands), caster (keeps its distance), tool, crawler,
crab (a crawler that swings its claws low, CrabClips, never rears like a spider).
Skills: leap, slam, charge, spin, quake, roar, pull, blink, dash, pounce, burrow, bolt, volley, rain, lightning,
cloud, breath, beam, summon:<kind>, heal. A monster's bolts, clouds and breath are its dungeon's element.
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../src/main/resources/ashbound/mob_moves.json")

# gate: {monster: "stance skill skill ... [shield]"}
MOVES = {
    "cellar": {
        "sodden_reveller": "claw charge",
        "cask_brute": "maul slam charge",
        "drowned_vintner": "dagger cloud dash",
        "cellar_eel": "crawler pounce",
        "barrel_mimic": "crawler pounce slam roar",
        "cask_mother": "maul slam cloud charge summon:sodden_reveller@2 rain@2 quake@3 roar@3",
    },
    "gallows": {
        "the_dropped": "claw pounce",
        "noose_walker": "claw pull charge",
        "tar_witch": "caster bolt cloud",
        "cutpurse": "twin_daggers blink dash",
        "gibbet_knight": "greatsword leap slam shield",
        "hangman": "greatsword pull leap slam@2 summon:the_dropped@2 spin@3 roar@3",
    },
    "rotwood": {
        "the_rooted": "claw pull",
        "bark_wight": "maul slam quake",
        "rot_seer": "caster bolt cloud heal",
        "thorn_crawler": "crawler pounce volley",
        "rot_stag": "crawler charge pounce roar",
        "mossking": "maul quake slam cloud summon:the_rooted@2 roar@2 rain@3 charge@3",
    },
    "crypt": {
        "grave_rat": "claw pounce",
        "ghoul": "claw pounce dash",
        "coffin_knight": "greatsword slam charge shield",
        "mourner": "caster bolt roar",
        "gravedigger": "spear quake summon:ghoul slam",
        "pale_abbot": "caster volley blink rain summon:mourner@2 beam@2 lightning@3 roar@3",
    },
    "plague": {
        "bell_leper": "tool roar cloud",
        "bloated_patient": "fist charge cloud",
        "lime_friar": "caster bolt cloud",
        "orderly": "maul charge slam",
        "plague_doctor": "caster cloud volley blink",
        "surgeon": "twin_daggers blink spin volley pull@2 summon:orderly@2 rain@3 dash@3",
    },
    "foundry": {
        "slagling": "claw pounce",
        "riveter": "tool bolt dash",
        "bellows_priest": "caster breath bolt",
        "crucible_bearer": "maul slam breath charge",
        "ossric": "maul slam quake breath rain@2 summon:slagling@2 charge@2 leap@3 roar@3",
    },
    "ossuary": {
        "stitched": "fist charge",
        "wickling": "claw pounce",
        "cantor": "caster roar bolt",
        "bone_hound": "claw pounce charge",
        "pallbearer": "maul slam charge shield",
        "assembler": "fist slam volley charge summon:wickling@2 quake@2 rain@3 roar@3",
    },
    "frost": {
        "frostbound": "sword dash",
        "frostbound_archer": "caster volley",
        "rime_knight": "longsword charge shield",
        "frost_chaplain": "caster bolt heal",
        "standard_bearer": "spear roar charge",
        "winter_marshal": "greatsword leap spin breath summon:frostbound@2 rain@2 roar@3 quake@3",
    },
    "temple": {
        "sentinel": "greatsword slam shield",
        "hollow": "claw pounce",
        "acolyte": "caster bolt",
        "facetaker": "twin_daggers blink pull",
        "mask_crawler": "crawler pounce",
        "sovereign": "longsword beam blink volley summon:hollow@2 rain@2 spin@3 lightning@3",
    },
    "weeping_mine": {
        "shard_crawler": "crawler pounce volley",
        "cart_golem": "fist charge slam",
        "lamp_miner": "spear cloud dash",
        "blind_burrower": "claw burrow pounce",
        "foreman": "maul slam quake roar",
        "the_vein": "fist quake volley slam summon:shard_crawler@2 rain@2 burrow@3 charge@3",
    },
    "tide_chapel": {
        "tide_crab": "crawler pounce",
        "crab_knight": "sword charge shield",
        "tide_priest": "caster bolt heal cloud",
        "net_thrower": "spear bolt pull",
        "barnacle_choir": "maul roar slam summon:tide_crab",
        "drowned_bell": "maul slam roar pull summon:tide_crab@2 quake@2 rain@3 charge@3",
    },
    "brigands_gorge": {
        "footpad": "twin_daggers blink dash",
        "gorge_ogre": "maul slam charge",
        "hedge_hexer": "caster bolt cloud",
        "knife_dancer": "twin_daggers spin volley",
        "bandit_lieutenant": "spear charge spin roar",
        "red_jack": "twin_axes pull spin volley leap@2 summon:footpad@2 dash@3 roar@3",
    },
    "rookery": {
        "carrion_crow": "claw pounce blink",
        "crowbrute": "maul slam charge",
        "augur": "caster volley cloud",
        "feather_blade": "dual dash spin",
        "rook_captain": "sword charge roar shield",
        "raven_mother": "claw rain volley blink summon:carrion_crow@2 pull@2 roar@3 lightning@3",
    },
    "hollow_circus": {
        "circus_puppet": "claw pounce",
        "strongman": "maul slam charge",
        "fire_eater": "caster breath bolt",
        "knife_juggler": "dagger volley blink",
        "harlequin": "dual blink spin dash",
        "ringmaster": "caster pull volley summon:circus_puppet blink@2 rain@2 roar@3 lightning@3",
    },
    "mirefen_coven": {
        "mire_thrall": "claw pounce",
        "bog_troll": "maul slam charge",
        "hag_sister": "spear bolt cloud",
        "fen_crawler": "crawler pounce cloud",
        "coven_matron": "caster cloud summon:mire_thrall heal",
        "mother_mire": "caster rain cloud pull summon:mire_thrall@2 quake@2 beam@3 roar@3",
    },
    "sandsunk_tomb": {
        "tomb_scarab": "crawler pounce",
        "sand_colossus": "maul slam quake",
        "embalmer": "caster cloud bolt",
        "jackal_runner": "dual dash leap",
        "sun_guardian": "spear charge beam shield",
        "sun_king": "caster beam rain summon:tomb_scarab volley@2 slam@2 blink@3 lightning@3",
    },
    "fallen_titan": {
        "burrow_leech": "crawler burrow pounce",
        "marrow_brute": "fist charge slam",
        "bile_priest": "spear cloud bolt",
        "sinew_stalker": "claw blink pounce pull",
        "heart_warden": "sword charge slam shield",
        "still_heart": "crawler roar volley summon:burrow_leech@2 rain@2 quake@3 charge@3",
    },
    "jade_monastery": {
        "jade_acolyte": "spear dash spin",
        "stone_lion": "claw charge pounce roar",
        "incense_monk": "caster cloud bolt heal",
        "shadow_monk": "twin_daggers blink pull spin",
        "fist_abbot": "fist dash charge quake",
        "thousand_hands": "dual spin blink volley summon:shadow_monk@2 rain@2 dash@3 lightning@3",
    },
    "storm_bastion": {
        "spark_hound": "crawler pounce charge",
        "thunder_ogre": "maul slam lightning",
        "storm_caller": "caster lightning volley",
        "gale_knight": "sabre dash blink spin",
        "storm_captain": "spear charge lightning shield",
        "thunder_abbess": "spear lightning roar beam summon:spark_hound@2 rain@2 blink@3 quake@3",
    },
    "bloodmoon_court": {
        "blood_thrall": "dagger pounce dash",
        "gorged_butler": "twin_daggers charge spin",
        "blood_mage": "caster bolt volley heal",
        "duelist": "rapier dash blink",
        "counts_hound": "crawler pounce charge roar",
        "countess_vael": "sword pull blink volley summon:blood_thrall@2 rain@2 spin@3 heal@3",
    },
    "obsidian_labyrinth": {
        "labyrinth_imp": "claw pounce bolt blink",
        "basalt_ogre": "maul slam quake",
        "ember_oracle": "caster bolt rain",
        "horned_runner": "twin_axes charge dash",
        "gatekeeper": "sword charge slam shield",
        "minotaur": "greatsword charge leap slam quake@2 roar@2 spin@3 rain@3",
    },
    "abyssal_lighthouse": {
        "deep_thing": "crawler pounce pull",
        "drowned_keeper": "maul slam pull",
        "lamp_siren": "caster roar bolt",
        "eyeless": "claw pounce blink",
        "angler_knight": "spear pull charge shield",
        "keeper_in_light": "caster beam pull summon:deep_thing rain@2 volley@2 roar@3 lightning@3",
    },
    "eclipse_cathedral": {
        "cherub_husk": "claw pounce bolt",
        "halo_knight": "maul slam cloud",
        "ash_choir": "caster roar volley heal",
        "fallen_blade": "dual dash spin blink",
        "seraph_warden": "longsword leap breath spin",
        "fallen_seraph": "greatsword beam leap spin rain@2 summon:cherub_husk@2 blink@2 volley@3 lightning@3",
    },
    "clockwork_spire": {
        "cogling": "crawler pounce spin",
        "brass_sentry": "spear charge pull shield",
        "steam_hulk": "fist slam charge cloud",
        "tinker_adept": "caster bolt lightning heal summon:cogling",
        "clockwork_duelist": "dual dash blink spin",
        "grand_horologe": "maul slam charge leap summon:cogling@2 breath@2 rain@2 lightning@3 spin@3 quake@3",
    },
    "serpent_ziggurat": {
        "coilspawn": "crawler pounce bolt",
        "scaleguard": "spear charge pull shield",
        "jaguar_stalker": "greatsword leap slam pounce",
        "venom_priest": "caster bolt cloud heal summon:coilspawn",
        "feathered_champion": "dual dash leap spin blink",
        "coiled_king": "spear slam charge spin summon:coilspawn@2 breath@2 cloud@2 rain@3 beam@3 quake@3",
    },
    "rimeholt": {
        "rime_thrall": "dagger dash pounce",
        "frost_troll": "maul slam charge quake",
        "huskarl": "axe charge pull shield",
        "rune_seer": "caster bolt lightning heal summon:rime_thrall",
        "winter_wolf": "crawler pounce breath charge roar",
        "jarl_hrimgar": "greatsword slam charge leap summon:rime_thrall@2 breath@2 quake@2 rain@3 roar@3 spin@3",
    },
    "glass_minaret": {
        "dune_scorpion": "crawler pounce bolt",
        "glass_golem": "fist slam charge quake",
        "mirror_guard": "spear charge pull shield",
        "sandwraith": "caster bolt cloud blink summon:dune_scorpion",
        "blade_dancer": "dual dash blink spin volley",
        "djinn_sultan": "greatsword beam blink spin summon:dune_scorpion@2 rain@2 cloud@2 lightning@3 breath@3 quake@3",
    },
    "black_banner": {
        "banner_hound": "crawler pounce dash",
        "deserter": "spear charge pull",
        "arbalest": "caster bolt volley",
        "hatchetman": "twin_axes dash leap volley",
        "anvil_breaker": "maul slam quake charge",
        "banner_captain": "greatsword leap slam spin roar summon:banner_hound",
    },
    "barrow_host": {
        "ossipede": "crawler pounce dash",
        "barrow_wight": "sword charge slam shield",
        "mound_brute": "maul slam quake roar",
        "wailing_shroud": "caster bolt roar cloud",
        "barrow_reaper": "dual dash leap spin",
        "barrow_king": "greatsword leap slam spin roar summon:barrow_wight",
    },
    "world_bosses": {
        "cairn_giant": "maul slam quake charge roar@2 rain@2 leap@3",
        "hart_lord": "axe charge leap spin roar@2 summon:thorn_beetle@2 dash@3",
        "saltglass_hydra": "crawler pounce breath bolt@2 volley@2 roar@3",
        "ironback_scorpion": "crawler pounce charge pull@2 cloud@2 burrow@3",
        "rime_lich": "caster bolt cloud blink summon:crawling_convict@2 rain@2 beam@3",
    },
    "crown_gate": {
        "founder_king": "maul slam quake charge leap breath@2 summon:slagling@2 rain@2 roar@3 lightning@3 beam@3",
    },
    "astral": {
        "nebula_moth": "crawler pounce cloud blink bolt@2 rain@2 roar@3 lightning@3",
        "constellation_knight": "spear charge leap spin slam@2 lightning@2 roar@3 beam@3",
        "orrery_magus": "caster bolt beam blink rain@2 summon:void_mite@2 lightning@3 roar@3",
    },
    "grey_fold": {
        "ash_shepherd": "spear pull leap slam summon:ashwalker blink@2 cloud@2 roar@3 summon:ash_herald@3",
    },
    "sunken_fire": {
        "wreck_mother": "crab slam charge pull quake summon:lamprey_hound@2 rain@2 roar@3 summon:merrow@3",
    },
    "tidewrack": {
        "lamprey_hound": "crawler pounce pull",
        "merrow": "spear dash pull charge",
        "reef_knight": "sword charge slam shield",
        "net_hag": "caster pull bolt cloud",
        "hullback": "maul slam quake charge roar",
        "abyss_angler": "spear leap spin pull roar summon:merrow",
    },
    "drowned_corsairs": {
        "kraken_spawn": "crawler pounce pull",
        "drowned_corsair": "dual dash pull spin",
        "harpooner": "spear pull charge volley",
        "anchor_hauler": "maul slam quake charge",
        "tide_caller": "caster bolt rain cloud",
        "dread_captain": "sword pull spin leap roar summon:kraken_spawn",
    },
    "deep_delvers": {
        "drill_mole": "crawler charge burrow",
        "delver": "axe charge slam",
        "blaster": "caster volley bolt dash",
        "tunnel_rat": "twin_axes dash pounce",
        "steam_driller": "maul slam charge quake",
        "pit_boss": "spear charge leap spin roar summon:drill_mole",
    },
    "sporefolk": {
        "spore_tick": "crawler pounce cloud",
        "capguard": "spear charge pull shield",
        "sporemaw": "fist slam quake cloud",
        "morel_shaman": "caster cloud bolt heal",
        "inkcap_stalker": "dual dash pounce spin",
        "elder_cap": "greatsword slam spin cloud roar summon:spore_tick",
    },
    "sky_legion": {
        "harpy": "claw pounce dash",
        "hoplite": "spear charge pull shield",
        "talos": "fist slam quake charge roar",
        "oracle": "caster beam bolt heal",
        "peltast": "spear volley dash",
        "gryphon_rider": "crawler charge pounce leap roar",
    },
    "salt_cursed": {
        "bone_hyena": "crawler pounce dash",
        "salt_legionary": "sword charge slam shield",
        "dune_behemoth": "maul slam quake charge",
        "vulture_priest": "caster cloud bolt summon:bone_hyena",
        "sand_reaver": "twin_daggers dash blink spin",
        "salt_khan": "spear spin leap charge roar summon:salt_legionary",
    },
    "thornborn": {
        "thorn_beetle": "crawler pounce charge",
        "briar_warden": "spear charge pull shield",
        "bramble_brute": "fist slam quake roar",
        "bloom_witch": "caster cloud bolt heal",
        "thorn_dancer": "dual pull spin dash",
        "rose_knight": "greatsword leap slam spin roar summon:thorn_beetle",
    },
    "rimebound": {
        "crawling_convict": "crawler pounce pull",
        "jailer": "sword charge slam",
        "glacier_hulk": "fist slam quake charge",
        "cold_chaplain": "caster bolt cloud rain",
        "icicle_shiv": "twin_daggers dash blink spin",
        "rime_warden": "maul pull slam spin roar summon:crawling_convict",
    },
    "blightkin": {
        "acid_slug": "crawler cloud pounce",
        "vat_guard": "spear pull charge",
        "vat_brute": "fist slam charge cloud roar",
        "alchemist": "caster volley cloud bolt",
        "stitched_stalker": "claw pounce dash spin",
        "chimera": "greatsword slam spin pull cloud roar summon:acid_slug",
    },
    "hollow_order": {
        "hollow_squire": "dagger dash pounce",
        "hollow_knight": "longsword charge slam shield",
        "siege_knight": "maul slam charge quake shield",
        "hollow_chaplain": "caster beam bolt heal",
        "hollow_destrier": "crawler charge pounce",
        "grand_master": "greatsword leap slam spin roar summon:hollow_squire",
    },
    "broodmothers": {
        "brood_mite": "crawler pounce dash",
        "hive_soldier": "spear charge pull",
        "hive_juggernaut": "fist charge slam quake",
        "spitter": "caster volley cloud bolt",
        "mantis_reaper": "dual leap dash spin",
        "brood_queen": "crawler charge pounce cloud roar summon:brood_mite",
    },
    "ash_legion": {
        "ash_salamander": "crawler pounce breath",
        "ash_legionary": "sword charge slam shield",
        "basalt_brute": "maul slam quake charge",
        "ash_augur": "caster bolt rain beam",
        "ash_lictor": "twin_axes dash leap spin",
        "ash_centurion": "greatsword leap slam spin roar summon:ash_legionary",
    },
    "voidborn": {
        "void_mite": "crawler pounce blink",
        "void_sentinel": "spear charge pull shield",
        "shulk_brute": "fist slam quake beam",
        "rift_seer": "caster blink beam volley",
        "phase_blade": "dual blink dash spin",
        "void_herald": "spear blink leap spin beam roar summon:void_mite",
    },
    "warlords_fang": {
        "goblin_cutthroat": "twin_daggers dash pounce",
        "orc_brute": "maul slam charge roar",
        "orc_raider": "axe charge pull shield",
        "goblin_shaman": "caster bolt roar heal summon:goblin_cutthroat",
        "warg_rider": "crawler pounce charge volley roar",
        "gorrak": "greatsword slam charge leap roar summon:goblin_cutthroat@2 quake@2 spin@2 rain@3 volley@3",
    },
    "ashwalkers": {
        "ashwalker": "claw pounce dash",
        "cinder_hulk": "fist slam charge quake",
        "ash_herald": "caster bolt rain cloud",
    },
    "wyrms_hoard": {
        "kobold": "tool dash pounce",
        "hoard_golem": "fist slam charge quake",
        "ash_cultist": "caster bolt cloud",
        "drake": "crawler pounce breath",
        "wyrm_priest": "caster breath rain summon:kobold heal",
        "ignavar": "crawler breath pounce roar rain@2 summon:drake@2 charge@2 quake@3 leap@3",
    },
}

STANCES = {"sword", "crab", "dual", "greatsword", "longsword", "rapier", "sabre", "spear", "dagger", "twin_daggers", "axe",
           "twin_axes", "maul", "fist", "claw", "caster", "tool", "crawler"}
SKILLS = {"leap", "slam", "charge", "spin", "quake", "roar", "pull", "blink", "dash", "pounce", "burrow", "bolt", "volley",
          "rain", "lightning", "cloud", "breath", "beam", "summon", "heal"}


def main():
    kinds = {k["id"]: k for k in json.load(open(os.path.join(os.path.dirname(OUT), "gate_mobs.json"), encoding="utf-8"))}
    out = {}
    for gate, mobs in MOVES.items():
        for mid, line in mobs.items():
            words = line.split()
            stance, rest = words[0], words[1:]
            assert stance in STANCES, (mid, stance)
            assert mid in kinds, mid
            spider = kinds[mid]["rig"] == "spider"
            assert (stance in ("crawler", "crab")) == spider, (mid, "crawler/crab stance must match the spider rig")
            skills = []
            for w in rest:
                if w == "shield":
                    continue
                name, _, phase = w.partition("@")
                name, _, arg = name.partition(":")
                assert name in SKILLS, (mid, name)
                if arg:
                    assert arg in kinds, (mid, arg)
                skills.append({"name": name, "arg": arg, "phase": int(phase or 1)})
            out[mid] = {"gate": gate, "stance": stance, "skills": skills, "shield": "shield" in rest}
    missing = sorted(set(kinds) - set(out))
    json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1)
    print("mob moves:", len(out), "monsters", "| no moves:", missing)


if __name__ == "__main__":
    main()
