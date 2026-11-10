package com.snoringwalrus.ashbound.mixin;

import com.snoringwalrus.ashbound.client.TossedFx;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.item.ItemEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** The outline round gear on the ground (Dropped) comes up in the colour of whoever threw it, not white. */
@Mixin(Entity.class)
public abstract class TossedGlowMixin {
	@Inject(method = "getTeamColor", at = @At("HEAD"), cancellable = true)
	private void ashbound$rarity(CallbackInfoReturnable<Integer> cir) {
		if ((Object) this instanceof ItemEntity it) cir.setReturnValue(TossedFx.colour(it) & 0xFFFFFF);
		else if (com.snoringwalrus.ashbound.client.HudPrefs.glowsForMe((Entity) (Object) this)) cir.setReturnValue(0x6FE08A);
	}
}
