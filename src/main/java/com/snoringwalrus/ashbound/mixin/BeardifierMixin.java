package com.snoringwalrus.ashbound.mixin;

import com.snoringwalrus.ashbound.Capital;
import net.minecraft.world.level.levelgen.Beardifier;
import net.minecraft.world.level.levelgen.DensityFunction;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** The capital's valley, tiers and cliffs, sunk into the land with the structures' own beards (Capital.shape). */
@Mixin(Beardifier.class)
public class BeardifierMixin {
	@Inject(method = "compute", at = @At("RETURN"), cancellable = true)
	private void ashbound$capital(DensityFunction.FunctionContext ctx, CallbackInfoReturnable<Double> cir) {
		double v = Capital.shape(ctx.blockX(), ctx.blockY(), ctx.blockZ());
		if (v != 0) cir.setReturnValue(cir.getReturnValueD() + v);
	}
}
