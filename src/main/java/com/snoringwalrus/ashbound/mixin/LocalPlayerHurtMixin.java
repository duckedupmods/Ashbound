package com.snoringwalrus.ashbound.mixin;

import com.snoringwalrus.ashbound.Net;

import net.minecraft.client.player.LocalPlayer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** The client plays any drop in your health as a hit (red flash, flinch). Just after a piece with max health on it
 *  came off (Net.QuietHealth) the drop is only the lower max: set it quietly. */
@Mixin(LocalPlayer.class)
public abstract class LocalPlayerHurtMixin {
	@Inject(method = "hurtTo", at = @At("HEAD"), cancellable = true)
	private void ashbound$quiet(float health, CallbackInfo ci) {
		LocalPlayer self = (LocalPlayer) (Object) this;
		if (System.currentTimeMillis() > Net.quietUntil || health >= self.getHealth()) return;
		Net.quietUntil = 0;
		self.setHealth(health);
		ci.cancel();
	}
}
