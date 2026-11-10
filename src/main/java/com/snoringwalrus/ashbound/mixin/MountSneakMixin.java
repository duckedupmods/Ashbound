package com.snoringwalrus.ashbound.mixin;

import com.snoringwalrus.ashbound.Mount;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Sneaking would throw you straight off; a mount takes that itself, so you get off as it does with the key. See Mount.leave. And the
 * jump key is the mount's: a rider who brushes something solid would otherwise jump too, and Epic Fight would play it, in the saddle.
 */
@Mixin(Player.class)
public abstract class MountSneakMixin {
	@Inject(method = "wantsToStopRiding", at = @At("HEAD"), cancellable = true)
	private void ashbound$mount(CallbackInfoReturnable<Boolean> cir) {
		if (((Player) (Object) this).getVehicle() instanceof Mount) cir.setReturnValue(false);
	}

	@Inject(method = "jumpFromGround", at = @At("HEAD"), cancellable = true)
	private void ashbound$noJump(CallbackInfo ci) {
		if (((Player) (Object) this).getVehicle() instanceof Mount) ci.cancel();
	}
}
