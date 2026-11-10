package com.snoringwalrus.ashbound;

import java.util.UUID;

import javax.annotation.Nullable;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.AABB;

/**
 * A lightning strike out of a gate storm (SkyCracks), in the storm's colour (client/StormStrikeRenderer). It warns first,
 * a ring glowing on the ground (CHARGE ticks, long enough to step out of it), then strikes: whatever stands in it is
 * hurt, the ground under it is scorched (GateScorch: char, never fire), and a moment later the dungeon's monsters climb
 * out of it. A harmless one strikes somewhere off under the storm, for the look of it and the thunder.
 */
public class StormStrike extends Entity {
	private static final EntityDataAccessor<Integer> SEED = SynchedEntityData.defineId(StormStrike.class, EntityDataSerializers.INT);
	private static final EntityDataAccessor<Integer> RANK = SynchedEntityData.defineId(StormStrike.class, EntityDataSerializers.INT);
	private static final EntityDataAccessor<Boolean> HARMLESS = SynchedEntityData.defineId(StormStrike.class, EntityDataSerializers.BOOLEAN);
	/** how far up the cloud it comes out of is */
	private static final EntityDataAccessor<Float> TOP = SynchedEntityData.defineId(StormStrike.class, EntityDataSerializers.FLOAT);
	public static final int CHARGE = 30, CLIMB = 12, AFTER = 60;
	public static final float REACH = 3f;

	@Nullable
	UUID crack;
	float hit;
	/** client: the flash was given */
	public boolean flashed;

	public StormStrike(EntityType<? extends StormStrike> type, Level level) {
		super(type, level);
	}

	@Override
	protected void defineSynchedData(SynchedEntityData.Builder b) {
		b.define(SEED, 0);
		b.define(RANK, 0);
		b.define(HARMLESS, false);
		b.define(TOP, 40f);
	}

	public int seed() {
		return entityData.get(SEED);
	}

	public int rank() {
		return entityData.get(RANK);
	}

	public boolean harmless() {
		return entityData.get(HARMLESS);
	}

	public float top() {
		return entityData.get(TOP);
	}

	/** Ticks of warning before it strikes (none for a harmless one far off). */
	public int charge() {
		return harmless() ? 0 : CHARGE;
	}

	void setUp(int seed, int rank, boolean harmless, float top, float hit, UUID crack) {
		entityData.set(SEED, seed);
		entityData.set(RANK, rank);
		entityData.set(HARMLESS, harmless);
		entityData.set(TOP, top);
		this.hit = hit;
		this.crack = crack;
	}

	@Override
	public void tick() {
		super.tick();
		if (!(level() instanceof ServerLevel l)) return;
		int t = tickCount - 1;
		if (t == charge()) strike(l);
		if (!harmless() && t == charge() + CLIMB) SkyCracks.climbOut(l, this);
		if (t == 4 && !harmless()) l.playSound(null, getX(), getY(), getZ(), SoundEvents.BEACON_POWER_SELECT, SoundSource.HOSTILE, 1.5f, 1.6f);
		if (t >= charge() + AFTER) discard();
	}

	private void strike(ServerLevel l) {
		float far = harmless() ? 0.6f : 1f;
		l.playSound(null, getX(), getY(), getZ(), SoundEvents.LIGHTNING_BOLT_THUNDER, SoundSource.WEATHER, 8f * far, 0.6f + random.nextFloat() * 0.2f);
		l.playSound(null, getX(), getY(), getZ(), SoundEvents.LIGHTNING_BOLT_IMPACT, SoundSource.WEATHER, 3f * far, 0.5f);
		if (harmless()) return;
		BlockPos at = blockPosition();
		l.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, l.getBlockState(at.below()).isAir() ? Blocks.DIRT.defaultBlockState() : l.getBlockState(at.below())),
				getX(), getY() + 0.3, getZ(), 40, 1.2, 0.3, 1.2, 0.25);
		l.sendParticles(ParticleTypes.LARGE_SMOKE, getX(), getY() + 0.5, getZ(), 12, 0.8, 0.4, 0.8, 0.02);
		for (LivingEntity e : l.getEntitiesOfClass(LivingEntity.class, new AABB(position(), position()).inflate(REACH, 3, REACH)))
			if (!(e instanceof Adventurer) && !e.getTags().contains(SkyCracks.TAG) && e.distanceToSqr(this) < REACH * REACH * 1.6)
				e.hurt(l.damageSources().lightningBolt(), hit);
		GateEntity.scorchPatch(l, getX(), getZ(), Math.round((float) getY()), rank(), 2.6);
	}

	@Override
	public boolean isPickable() {
		return false;
	}

	@Override
	public boolean isPushable() {
		return false;
	}

	@Override
	public boolean shouldRenderAtSqrDistance(double d) {
		return d < 400 * 400;
	}

	@Override
	public AABB getBoundingBoxForCulling() {
		return getBoundingBox().expandTowards(0, top(), 0).inflate(8);
	}

	@Override
	protected void readAdditionalSaveData(CompoundTag tag) {}

	@Override
	protected void addAdditionalSaveData(CompoundTag tag) {}
}
