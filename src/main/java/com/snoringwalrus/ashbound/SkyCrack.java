package com.snoringwalrus.ashbound;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;

/**
 * A gate storm's eye (SkyCracks, tools/blender/gate_storm.py is the look): a wild gate torn open high over the land,
 * drawn by GateRenderer as a gate SCALE times over lying face-down (`tilt` 90, turned `roll` about its face) under the
 * storm's clouds (client/StormSky), the dungeon seen through it. Its timeline is a gate's; what it does is SkyCracks'.
 */
public class SkyCrack extends GateEntity {
	public static final float SCALE = 4.5f;
	/** how far under its middle the storm's cloud base hangs (client/StormSky); the funnel climbs from there to it */
	public static final float DECK = 20f;
	private static final EntityDataAccessor<Float> ROLL = SynchedEntityData.defineId(SkyCrack.class, EntityDataSerializers.FLOAT);
	private static final EntityDataAccessor<Float> TILT = SynchedEntityData.defineId(SkyCrack.class, EntityDataSerializers.FLOAT);

	public SkyCrack(EntityType<? extends SkyCrack> type, Level level) {
		super(type, level);
	}

	@Override
	protected void defineSynchedData(SynchedEntityData.Builder b) {
		super.defineSynchedData(b);
		b.define(ROLL, 70f);
		b.define(TILT, 60f);
	}

	/** Degrees its length is turned from upright, about its face. */
	public float roll() {
		return entityData.get(ROLL);
	}

	/** Degrees its face is tipped down toward the ground. */
	public float tilt() {
		return entityData.get(TILT);
	}

	void lay(float roll, float tilt) {
		entityData.set(ROLL, roll);
		entityData.set(TILT, tilt);
	}

	@Override
	public boolean sky() {
		return true;
	}

	@Override
	public boolean shouldRenderAtSqrDistance(double d) {
		return d < 640 * 640;
	}

	@Override
	public AABB getBoundingBoxForCulling() {
		// its clouds reach well out past the tear
		return getBoundingBox().move(0, MID, 0).inflate(190);
	}

	@Override
	protected void readAdditionalSaveData(CompoundTag tag) {
		super.readAdditionalSaveData(tag);
	}
}
