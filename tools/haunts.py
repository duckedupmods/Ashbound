"""Which monsters hold which of the modpack's structures (Haunts.java reads /ashbound/haunts.json).

A faction is a tools/mobs/<faction>.py file: its monsters with how often each turns up, and its elite, who comes once
per garrison in the big places. A structure is named exactly (dungeons_arise:bandit_towers) or by a prefix ending in
* (towns_and_towers:pillager_outpost_*). The mod's own monsters (and vanilla's) stay; ours come as well.

    python tools/haunts.py
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../src/main/resources/ashbound/haunts.json")

FACTIONS = {
    "black_banner": dict(
        mobs={"banner_hound": 4, "deserter": 4, "hatchetman": 3, "arbalest": 3, "anvil_breaker": 1},
        elite="banner_captain",
        structures=[
            "dungeons_arise:bandit_towers", "dungeons_arise:bandit_village",
            "dungeons_arise:illager_campsite", "dungeons_arise:illager_fort", "dungeons_arise:illager_windmill",
            "nova_structures:illager_camp", "nova_structures:illager_hideout", "nova_structures:illager_manor",
            "nova_structures:ruin_town", "nova_structures:wild_ruin", "nova_structures:remnant_*",
            "towns_and_towers:pillager_outpost_*",
        ]),
    "barrow_host": dict(
        mobs={"ossipede": 4, "barrow_wight": 4, "barrow_reaper": 3, "wailing_shroud": 2, "mound_brute": 1},
        elite="barrow_king",
        structures=[
            "nova_structures:creeping_crypt",
            "nova_structures:undead_crypt",
            "nova_structures:remnant_graveyard",
            "nova_structures:remnant_birch_graveyard",
            "betterdungeons:skeleton_dungeon",
            "betterdungeons:zombie_dungeon",
            "betterdungeons:small_dungeon",
            "betterstrongholds:stronghold",
            "cataclysm:abandoned_spire",
        ]),
    "drowned_corsairs": dict(
        mobs={"kraken_spawn": 4, "drowned_corsair": 4, "harpooner": 3, "tide_caller": 2, "anchor_hauler": 1},
        elite="dread_captain",
        structures=[
            "dungeons_arise:undead_pirate_ship",
            "dungeons_arise:illager_corsair",
            "dungeons_arise:illager_galley",
            "dungeons_arise:lighthouse",
            "towns_and_towers:wreckage_ocean",
            "cataclysm:sunken_city",
            "betteroceanmonuments:ocean_monument",
            "nova_structures:conduit_ruin",
            "nova_structures:trident_trial_monument",
        ]),
    "deep_delvers": dict(
        mobs={"drill_mole": 3, "delver": 4, "tunnel_rat": 3, "blaster": 3, "steam_driller": 1},
        elite="pit_boss",
        structures=[
            "dungeons_arise:foundry",
            "dungeons_arise:mining_complex",
            "dungeons_arise:mining_system",
            "dungeons_arise:scorched_mines",
            "cataclysm:ancient_factory",
            "nova_structures:bunker",
            "nova_structures:deepslate_camp",
            "nova_structures:badlands_miner_outpost",
            "nova_structures:remnant_miner_hut",
        ]),
    "sporefolk": dict(
        mobs={"spore_tick": 4, "capguard": 4, "inkcap_stalker": 3, "morel_shaman": 2, "sporemaw": 1},
        elite="elder_cap",
        structures=[
            "dungeons_arise:giant_mushroom",
            "dungeons_arise:mushroom_house",
            "dungeons_arise:mushroom_mines",
            "dungeons_arise:mushroom_village",
        ]),
    "sky_legion": dict(
        mobs={"harpy": 4, "hoplite": 4, "peltast": 3, "oracle": 2, "talos": 1},
        elite="gryphon_rider",
        structures=[
            "dungeons_arise:heavenly_challenger",
            "dungeons_arise:heavenly_conqueror",
            "dungeons_arise:heavenly_rider",
            "dungeons_arise:aviary",
            "dungeons_arise:small_blimp",
            "dungeons_arise:coliseum",
            "dungeons_arise:typhon",
            "dungeons_arise:ceryneian_hind",
        ]),
    "salt_cursed": dict(
        mobs={"bone_hyena": 4, "salt_legionary": 4, "sand_reaver": 3, "vulture_priest": 2, "dune_behemoth": 1},
        elite="salt_khan",
        structures=[
            "cataclysm:cursed_pyramid",
            "cataclysm:desert_site",
            "cataclysm:desert_temple",
            "cataclysm:desert_occupied_village",
            "nova_structures:desert_ruins",
            "nova_structures:remnant_desert_remnant",
            "dungeons_arise:shiraz_palace",
            "towns_and_towers:mimic_desert",
        ]),
    "thornborn": dict(
        mobs={"thorn_beetle": 4, "briar_warden": 4, "thorn_dancer": 3, "bloom_witch": 2, "bramble_brute": 1},
        elite="rose_knight",
        structures=[
            "dungeons_arise:jungle_tree_house",
            "dungeons_arise:thornborn_towers",
            "dungeons_arise:kisegi_sanctuary",
            "dungeons_arise:keep_kayra",
            "dungeons_arise:abandoned_temple",
            "nova_structures:jungle_ruins",
        ]),
    "rimebound": dict(
        mobs={"crawling_convict": 4, "jailer": 4, "icicle_shiv": 3, "cold_chaplain": 2, "glacier_hulk": 1},
        elite="rime_warden",
        structures=[
            "cataclysm:frosted_prison",
            "nova_structures:stray_fort",
        ]),
    "blightkin": dict(
        mobs={"acid_slug": 4, "vat_guard": 4, "stitched_stalker": 3, "alchemist": 2, "vat_brute": 1},
        elite="chimera",
        structures=[
            "dungeons_arise:plague_asylum",
            "nova_structures:toxic_lair",
            "nova_structures:witch_villa",
            "nova_structures:mangrove_witch_hut",
        ]),
    "hollow_order": dict(
        mobs={"hollow_squire": 4, "hollow_knight": 4, "hollow_destrier": 2, "hollow_chaplain": 2, "siege_knight": 1},
        elite="grand_master",
        structures=[
            "tlc:lost_castle",
            "nova_structures:lone_citadel",
            "nova_structures:remnant_taiga_castle",
            "cataclysm:ruined_citadel",
            "cataclysm:acropolis",
            "dungeons_arise:monastery",
        ]),
    "broodmothers": dict(
        mobs={"brood_mite": 5, "hive_soldier": 4, "mantis_reaper": 3, "spitter": 2, "hive_juggernaut": 1},
        elite="brood_queen",
        structures=[
            "betterdungeons:spider_dungeon",
            "cataclysm:amethyst_nest",
            "dungeons_arise:mechanical_nest",
            "dungeons_arise:infested_temple",
        ]),
    "ash_legion": dict(
        mobs={"ash_salamander": 4, "ash_legionary": 4, "ash_lictor": 3, "ash_augur": 2, "basalt_brute": 1},
        elite="ash_centurion",
        structures=[
            "betterfortresses:fortress",
            "nova_structures:nether_keep",
            "nova_structures:nether_port",
            "nova_structures:nether_skeleton_tower_*",
            "nova_structures:piglin_camp",
            "nova_structures:piglin_donjon",
            "nova_structures:piglin_outstation",
            "nova_structures:skeleton_camp_*",
            "cataclysm:burning_arena",
            "cataclysm:soul_black_smith",
            "betterdungeons:small_nether_dungeon",
        ]),
    "voidborn": dict(
        mobs={"void_mite": 4, "void_sentinel": 4, "phase_blade": 3, "rift_seer": 2, "shulk_brute": 1},
        elite="void_herald",
        structures=[
            "nova_structures:end_castle",
            "nova_structures:end_lighthouse",
            "nova_structures:end_ship",
        ]),
}


def main():
    structures = {}
    for f, d in FACTIONS.items():
        for s in d["structures"]:
            assert s not in structures, "%s is held by %s already" % (s, structures[s])
            structures[s] = f
    out = {"factions": {f: dict(mobs=d["mobs"], elite=d["elite"]) for f, d in FACTIONS.items()}, "structures": structures}
    json.dump(out, open(OUT, "w"), indent=1)
    print("haunts: %d factions, %d structure names" % (len(FACTIONS), len(structures)))


if __name__ == "__main__":
    main()
