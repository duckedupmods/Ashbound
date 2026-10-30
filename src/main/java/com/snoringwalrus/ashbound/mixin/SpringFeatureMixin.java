package com.snoringwalrus.ashbound.mixin;

import com.snoringwalrus.ashbound.Capital;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.SpringFeature;
import net.minecraft.world.level.levelgen.feature.configurations.SpringConfiguration;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** No springs in the rock round the capital: the cut cliffs would run with stray water and lava over the city. */
@Mixin(SpringFeature.class)
public class SpringFeatureMixin {
	@Inject(method = "place", at = @At("HEAD"), cancellable = true)
	private void ashbound$noSprings(FeaturePlaceContext<SpringConfiguration> ctx, CallbackInfoReturnable<Boolean> cir) {
		if (Capital.blocksStructures(new ChunkPos(ctx.origin()))) cir.setReturnValue(false);
	}
}
