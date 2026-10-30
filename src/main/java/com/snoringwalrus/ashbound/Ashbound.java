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
		Smithing.init();
		ColdForge.init();
		Story.init();
		BattleMode.init();
		Incidents.init();
		Waypoints.init();
		Party.init();
		Weapons.ITEMS.register(bus);
		Armors.all();
		Armors.MATERIALS.register(bus);
		Armors.ITEMS.register(bus);
		Monsters.register(bus);
		Spells.register(bus);
		GateLoot.register();
		SilkMobs.register(bus);
		GateMobs.register(bus);
		Townsfolk.register(bus);
		Guild.init(bus);
		Errands.init(bus);
		Roads.init();
		CityBlocks.init();
		SculptBlocks.init();
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
		Pregen.hook();
		if (FMLEnvironment.dist == Dist.CLIENT) AshboundClient.hooks(bus);
		Tabs.register(bus);
	}
}
