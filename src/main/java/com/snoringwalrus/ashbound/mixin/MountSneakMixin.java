package com.snoringwalrus.ashbound.mixin;

import com.snoringwalrus.ashbound.Mount;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Sneaking would throw you straight off; a mount takes that itself, so you get off as it does with the key. See Mount.leave. */
@Mixin(Player.class)
public abstract class MountSneakMixin {
	@Inject(method = "wantsToStopRiding", at = @At("HEAD"), cancellable = true)
	private void ashbound$mount(CallbackInfoReturnable<Boolean> cir) {
		if (((Player) (Object) this).getVehicle() instanceof Mount) cir.setReturnValue(false);
	}
}
