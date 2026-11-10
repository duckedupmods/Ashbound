package com.snoringwalrus.ashbound;

import java.util.UUID;

import javax.annotation.Nullable;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * A gate-shard (Meteors; tools/blender/meteor_fall.py is the look): a piece of a broken gate's crystal ring. It stands where
 * it will land from the start; for the first FALL ticks the client draws it coming down out of the sky along `from`
 * (client/MeteorRenderer: the fireball, the trail, the smoke). Then it hits, and stands leaning in its crater, dark
 * crystal with its gate's colour in the veins, smoke climbing off it. Hit it to wake it: its three veins break one by
 * one, each with a heat pulse, while its gate's monsters crawl out of the cracks.
 */
public class MeteorShard extends Entity {
	private static final EntityDataAccessor<Integer> SEED = SynchedEntityData.defineId(MeteorShard.class, EntityDataSerializers.INT);
	private static final EntityDataAccessor<Integer> RANK = SynchedEntityData.defineId(MeteorShard.class, EntityDataSerializers.INT);
	/** 0 falling, 1 landed (smoking), 2 awake (fighting), 3 shattering, 4 gone dark */
	private static final EntityDataAccessor<Integer> PHASE = SynchedEntityData.defineId(MeteorShard.class, EntityDataSerializers.INT);
	private static final EntityDataAccessor<Integer> VEINS = SynchedEntityData.defineId(MeteorShard.class, EntityDataSerializers.INT);
	private static final EntityDataAccessor<Float> HURT = SynchedEntityData.defineId(MeteorShard.class, EntityDataSerializers.FLOAT);
	/** where it falls from, relative to where it lands */
	private static final EntityDataAccessor<Float> FX = SynchedEntityData.defineId(MeteorShard.class, EntityDataSerializers.FLOAT),
			FY = SynchedEntityData.defineId(MeteorShard.class, EntityDataSerializers.FLOAT), FZ = SynchedEntityData.defineId(MeteorShard.class, EntityDataSerializers.FLOAT);
	/** the time it started falling (game time), so a client that sees it late still draws it in the right place */
	private static final EntityDataAccessor<Long> START = SynchedEntityData.defineId(MeteorShard.class, EntityDataSerializers.LONG);

	public static final int FALLING = 0, LANDED = 1, AWAKE = 2, SHATTER = 3, DARK = 4;
	/** how long it takes to come down; how long it takes to burst once its last vein goes */
	public static final int FALL = 150, BURST = 24;

	/** server: which fall it is (Meteors.LIVE), and what breaking its current vein still takes */
	@Nullable
	UUID fall;
	float hp, hpMax;
	/** client: when it was last struck (for the flash) */
	public long struck;
	long phaseAt;

	public MeteorShard(EntityType<? extends MeteorShard> type, Level level) {
		super(type, level);
		noPhysics = true;
	}

	@Override
	protected void defineSynchedData(SynchedEntityData.Builder b) {
		b.define(SEED, 0);
		b.define(RANK, 0);
		b.define(PHASE, FALLING);
		b.define(VEINS, 3);
		b.define(HURT, 0f);
		b.define(FX, 0f);
		b.define(FY, 0f);
		b.define(FZ, 0f);
		b.define(START, 0L);
	}

	public int seed() {
		return entityData.get(SEED);
	}

	public int rank() {
		return entityData.get(RANK);
	}

	public int phase() {
		return entityData.get(PHASE);
	}

	public int veins() {
		return entityData.get(VEINS);
	}

	/** How broken its current vein is, 0..1. */
	public float broken() {
		return entityData.get(HURT);
	}

	public long start() {
		return entityData.get(START);
	}

	void setUp(int seed, int rank, Vec3 from, long now) {
		entityData.set(SEED, seed);
		entityData.set(RANK, Mth.clamp(rank, 0, 8));
		entityData.set(FX, (float) from.x);
		entityData.set(FY, (float) from.y);
		entityData.set(FZ, (float) from.z);
		entityData.set(START, now);
	}

	void phase(int p) {
		entityData.set(PHASE, p);
		phaseAt = level().getGameTime();
	}

	void veins(int n, float hp) {
		entityData.set(VEINS, n);
		entityData.set(HURT, 0f);
		this.hp = this.hpMax = hp;
	}

	/** 0 when it starts falling, 1 when it hits. */
	public float fallen(float pt) {
		return Mth.clamp((level().getGameTime() - start() + pt) / FALL, 0, 1);
	}

	/** Where the falling head is now, relative to where it lands: it comes in on a straight line, speeding up. */
	public Vec3 head(float pt) {
		float t = fallen(pt);
		float k = 1 - (float) Math.pow(t, 1.35);
		return new Vec3(entityData.get(FX) * k, entityData.get(FY) * k, entityData.get(FZ) * k);
	}

	/** The way it's going (unit), from where it fell toward where it lands. */
	public Vec3 heading() {
		return new Vec3(-entityData.get(FX), -entityData.get(FY), -entityData.get(FZ)).normalize();
	}

	@Override
	public void onSyncedDataUpdated(EntityDataAccessor<?> key) {
		super.onSyncedDataUpdated(key);
		if (HURT.equals(key) || VEINS.equals(key)) struck = System.currentTimeMillis();
	}

	@Override
	public void tick() {
		super.tick();
		if (level().isClientSide) {
			com.snoringwalrus.ashbound.client.MeteorFx.tick(this);
			return;
		}
		ServerLevel l = (ServerLevel) level();
		if (fall == null || !Meteors.LIVE.containsKey(fall)) {
			discard();
			return;
		}
		Meteors.tick(l, this);
	}

	@Override
	public boolean isPickable() {
		int p = phase();
		return isAlive() && (p == LANDED || p == AWAKE);
	}

	@Override
	public boolean hurt(DamageSource src, float amount) {
		if (level().isClientSide || isRemoved() || !isPickable()) return false;
		Entity by = src.getEntity();
		if (!(by instanceof Player) && !(by instanceof Adventurer)) return false;
		ServerLevel l = (ServerLevel) level();
		if (phase() == LANDED) Meteors.wake(l, this);
		hp -= amount;
		entityData.set(HURT, 1 - Math.max(0, hp) / Math.max(1, hpMax));
		l.playSound(null, getX(), getY() + 2, getZ(), SoundEvents.AMETHYST_BLOCK_HIT, SoundSource.HOSTILE, 2.2f, 0.45f + random.nextFloat() * 0.15f);
		l.playSound(null, getX(), getY() + 1, getZ(), SoundEvents.DEEPSLATE_HIT, SoundSource.HOSTILE, 1.4f, 0.5f);
		l.sendParticles(ParticleTypes.ELECTRIC_SPARK, getX(), getY() + 2.5, getZ(), 10, 0.8, 1.2, 0.8, 0.3);
		if (hp <= 0) Meteors.veinBroken(l, this);
		return true;
	}

	@Override
	public boolean isPushable() {
		return false;
	}

	@Override
	public boolean shouldRenderAtSqrDistance(double d) {
		return d < 640 * 640;
	}

	@Override
	public AABB getBoundingBoxForCulling() {
		// while it falls, the whole path across the sky
		AABB b = getBoundingBox().inflate(8);
		if (phase() == FALLING) b = b.minmax(b.move(entityData.get(FX), entityData.get(FY), entityData.get(FZ)).inflate(20));
		else b = b.expandTowards(0, 60, 0);
		return b;
	}

	@Override
	protected void readAdditionalSaveData(CompoundTag tag) {}

	@Override
	protected void addAdditionalSaveData(CompoundTag tag) {}
}
