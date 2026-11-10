package com.snoringwalrus.ashbound;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;

/**
 * Hob Tarrant's wagon with Bramble in the shafts (Intro), drawn by client/WagonRender from tools/mcstyle_props.py's cube
 * models. It stands where it was put, facing down the road: no gravity, nothing pushes it, nothing hurts it. Its yaw is
 * the entity's own and saved with it.
 */
public class Wagon extends Entity {
	public Wagon(EntityType<? extends Wagon> type, Level level) {
		super(type, level);
		noPhysics = true;
		setNoGravity(true);
		setInvulnerable(true);
	}

	@Override
	protected void defineSynchedData(SynchedEntityData.Builder b) {}

	@Override
	protected void readAdditionalSaveData(CompoundTag tag) {}

	@Override
	protected void addAdditionalSaveData(CompoundTag tag) {}

	@Override
	public boolean hurt(DamageSource source, float amount) {
		return false;
	}

	@Override
	public boolean isPickable() {
		return false;
	}

	@Override
	public boolean isPushable() {
		return false;
	}

	/** Bramble and the shafts reach well past the wagon's own box: culled by that, the lot vanished at the screen's edge. */
	@Override
	public net.minecraft.world.phys.AABB getBoundingBoxForCulling() {
		return getBoundingBox().inflate(4.5, 1.5, 4.5);
	}

	@Override
	public boolean shouldRenderAtSqrDistance(double d) {
		return d < 160 * 160;
	}
}
