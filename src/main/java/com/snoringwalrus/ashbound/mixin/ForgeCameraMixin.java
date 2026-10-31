package com.snoringwalrus.ashbound.mixin;

import com.snoringwalrus.ashbound.client.ForgeScene;

import net.minecraft.client.Camera;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.phys.Vec3;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** At the anvil the camera stands to the side, where you can see both smiths at the work (ForgeScene). */
@Mixin(Camera.class)
public abstract class ForgeCameraMixin {
	@Shadow
	protected abstract void setPosition(Vec3 pos);

	@Shadow
	protected abstract void setRotation(float yRot, float xRot);

	@Inject(method = "setup", at = @At("RETURN"))
	private void ashbound$forge(BlockGetter level, Entity entity, boolean detached, boolean mirror, float partialTick, CallbackInfo ci) {
		if (com.snoringwalrus.ashbound.client.IntroScene.on()) {
			com.snoringwalrus.ashbound.client.IntroScene.frame(partialTick);
			setPosition(com.snoringwalrus.ashbound.client.IntroScene.eye());
			setRotation(com.snoringwalrus.ashbound.client.IntroScene.yaw(), com.snoringwalrus.ashbound.client.IntroScene.pitch());
			return;
		}
		if (com.snoringwalrus.ashbound.client.ColdScene.on()) {
			setPosition(com.snoringwalrus.ashbound.client.ColdScene.eye());
			setRotation(com.snoringwalrus.ashbound.client.ColdScene.yaw(), com.snoringwalrus.ashbound.client.ColdScene.pitch());
			return;
		}
		if (!ForgeScene.on()) return;
		setPosition(ForgeScene.eye());
		setRotation(ForgeScene.yaw(), ForgeScene.pitch());
	}
}
