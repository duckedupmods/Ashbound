package com.snoringwalrus.ashbound.mixin;

import com.snoringwalrus.ashbound.Net;
import com.snoringwalrus.ashbound.client.CurioKeys;

import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import yesman.epicfight.api.client.camera.EpicFightCameraAPI;

/**
 * Epic Fight's lock-on. Its own key only ever finds monsters, so friends in a fight stop locking on to each other; the party has a
 * key of its own (CurioKeys.LOCK_PARTY). And whatever's under the crosshair isn't lit up: the outline shows through walls.
 */
@Mixin(value = EpicFightCameraAPI.class, remap = false)
public abstract class LockOnMixin {
	@Inject(method = "predicateFocusableEntity", at = @At("HEAD"), cancellable = true, require = 0)
	private void ashbound$whoCounts(Entity e, CallbackInfoReturnable<Boolean> ci) {
		if (!CurioKeys.partyLock) {
			if (e instanceof Player) ci.setReturnValue(false);
		} else if (!(e instanceof Player p) || Net.clientParty.stream().noneMatch(m -> m.name().equals(p.getName().getString()))) ci.setReturnValue(false);
	}

	@Inject(method = "shouldHighlightTarget", at = @At("HEAD"), cancellable = true, require = 0)
	private void ashbound$noOutline(Entity e, CallbackInfoReturnable<Boolean> ci) {
		ci.setReturnValue(false);
	}
}
