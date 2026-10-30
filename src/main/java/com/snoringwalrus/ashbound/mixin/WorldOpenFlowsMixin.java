package com.snoringwalrus.ashbound.mixin;

import com.mojang.serialization.Lifecycle;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.worldselection.CreateWorldScreen;
import net.minecraft.client.gui.screens.worldselection.WorldOpenFlows;
import net.minecraft.world.level.storage.LevelStorageSource;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Our terrain and dimensions are datapack worldgen, which vanilla marks "experimental": no warning when making a
 *  world, and no "make a backup?" when opening one for that reason (an old customized world still asks). */
@Mixin(WorldOpenFlows.class)
public abstract class WorldOpenFlowsMixin {
	@Inject(method = "confirmWorldCreation", at = @At("HEAD"), cancellable = true)
	private static void ashbound$noExperimentalWarning(Minecraft mc, CreateWorldScreen screen, Lifecycle lifecycle, Runnable loadWorld,
			boolean skipWarnings, CallbackInfo ci) {
		if (lifecycle == Lifecycle.experimental()) {
			loadWorld.run();
			ci.cancel();
		}
	}

	@Inject(method = "askForBackup", at = @At("HEAD"), cancellable = true)
	private void ashbound$noExperimentalBackup(LevelStorageSource.LevelStorageAccess levelStorage, boolean customized, Runnable loadLevel,
			Runnable onCancel, CallbackInfo ci) {
		if (!customized) {
			loadLevel.run();
			ci.cancel();
		}
	}
}
