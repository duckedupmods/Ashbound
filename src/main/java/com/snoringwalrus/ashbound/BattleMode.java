package com.snoringwalrus.ashbound;

import net.minecraft.server.level.ServerPlayer;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;
import yesman.epicfight.world.capabilities.EpicFightCapabilities;
import yesman.epicfight.world.capabilities.entitypatch.player.ServerPlayerPatch;
import yesman.epicfight.world.gamerule.EpicFightGameRules;

/**
 * There's no Minecraft mode here: everyone is in Epic Fight's battle mode all the time and its switch is off (the key is
 * unbound in client/CurioKeys). Mining still works, looking at a block with the config's ADAPTIVE behaviour.
 */
public final class BattleMode {
	private BattleMode() {}

	static void init() {
		NeoForge.EVENT_BUS.addListener((ServerStartedEvent e) ->
				EpicFightGameRules.CAN_SWITCH_PLAYER_MODE.setRuleValue(e.getServer().overworld(), false));
		NeoForge.EVENT_BUS.addListener((PlayerTickEvent.Post e) -> {
			if (!(e.getEntity() instanceof ServerPlayer p) || p.tickCount % 20 != 0) return;
			ServerPlayerPatch pp = EpicFightCapabilities.getEntityPatch(p, ServerPlayerPatch.class);
			if (pp != null && pp.isVanillaMode()) pp.toEpicFightMode(true);
		});
	}
}
