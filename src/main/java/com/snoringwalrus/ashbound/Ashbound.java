package com.snoringwalrus.ashbound;

import org.slf4j.Logger;

import com.mojang.logging.LogUtils;

import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.loading.FMLEnvironment;

/** Ashbound as an Epic Fight add-on: gates, ranked dungeons and bosses, fought with Epic Fight. */
@Mod(Ashbound.ID)
public final class Ashbound {
	public static final String ID = "ashbound";
	public static final Logger LOG = LogUtils.getLogger();

	public Ashbound(IEventBus bus) {
		Gear.init();
		Joined.init();
		JoinedSkills.init();
		WorldArms.init();
		Curios.init();
		CurioFx.register();
		GateForge.init();
		Stations.init();
		Kitchen.init();
		Smithing.init();
		ColdForge.init();
		Story.init();
		Intro.init();
		Threat.init();
		BattleMode.init();
		Incidents.init();
		Waypoints.init();
		Marks.init();
		Party.init();
		Classes.init();
		Ashfall.init();
		Meteors.init();
		Downed.init();
		Arena.init();
		BossArenas.init();
		Tidewrack.init();
		WorldBosses.init();
		Weapons.ITEMS.register(bus);
		Armors.all();
		Armors.MATERIALS.register(bus);
		Armors.ITEMS.register(bus);
		Monsters.register(bus);
		Spells.register(bus);
		Ranks.register(bus);
		GateLoot.register();
		SilkMobs.register(bus);
		GateMobs.register(bus);
		Beast.register(bus);
		Mounts.register(bus);
		Bag.register(bus);
		Trades.register(bus);
		Adventurers.register(bus);
		ModVillages.register();
		Rations.register();
		Dropped.register();
		StaffSpells.register();
		Meters.register();
		Skills.register();
		Forms.register();
		Books.register();
		Townsfolk.register(bus);
		Intro.register(bus);
		Guild.init(bus);
		Errands.init(bus);
		Chains.init(bus);
		Roads.init();
		CityBlocks.init();
		SculptBlocks.init();
		Trophies.init();
		SilkBlocks.init();
		SilkProps.init();
		VillageSpin.init();
		Fireflies.init();
		GateBlocks.init();
		ClockHands.TYPES.register(bus);
		WorldBlocks.BLOCKS.register(bus);
		Trees.register(bus);
		Capital.register();
		Gates.register(bus);
		Lairs.register();
		Cheats.register();
		Movesets.register(bus);
		TowerSites.register();
		Balance.register();
		Levels.register(bus);
		Passives.register(bus);
		Haunts.register();
		Slumber.register();
		MobMoves.register();
		MobSkills.register();
		Pregen.hook();
		if (FMLEnvironment.dist == Dist.CLIENT) AshboundClient.hooks(bus);
		Tabs.register(bus);
	}
}
