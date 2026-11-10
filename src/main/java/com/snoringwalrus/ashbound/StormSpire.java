package com.snoringwalrus.ashbound;

import java.util.UUID;

import javax.annotation.Nullable;

import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.AABB;

/**
 * A storm spire (SkyCracks): a jagged pillar of the storm's dungeon's own blocks burst up out of the ground, a white-hot core
 * at its top that the storm keeps feeding lightning (client/StormSpireRenderer). The spires hold the storm's eye open: break
 * them all (hp, at the foot, where you can reach) and it collapses.
 */
public class StormSpire extends Entity {
	private static final EntityDataAccessor<Integer> SEED = SynchedEntityData.defineId(StormSpire.class, EntityDataSerializers.INT);
	private static final EntityDataAccessor<Float> TALL = SynchedEntityData.defineId(StormSpire.class, EntityDataSerializers.FLOAT);
	private static final EntityDataAccessor<Float> HURT = SynchedEntityData.defineId(StormSpire.class, EntityDataSerializers.FLOAT);
	/** the storm's entity id, so the client can build it from that dungeon's blocks */
	private static final EntityDataAccessor<Integer> STORM = SynchedEntityData.defineId(StormSpire.class, EntityDataSerializers.INT);
	/** how long it takes to burst up out of the ground */
	public static final int RISE = 40;

	/** server: the storm it holds open; how much breaking it still takes, and took to begin with */
	@Nullable
	UUID crack;
	float hp, hpMax;
	/** client: when it was last struck (for the flash) */
	public long struck;

	public StormSpire(EntityType<? extends StormSpire> type, Level level) {
		super(type, level);
	}

	@Override
	protected void defineSynchedData(SynchedEntityData.Builder b) {
		b.define(SEED, 0);
		b.define(TALL, 16f);
		b.define(HURT, 0f);
		b.define(STORM, -1);
	}

	public int seed() {
		return entityData.get(SEED);
	}

	/** Blocks tall. */
	public float tall() {
		return entityData.get(TALL);
	}

	/** How broken it is, 0..1. */
	public float broken() {
		return entityData.get(HURT);
	}

	@Nullable
	public SkyCrack storm() {
		return level().getEntity(entityData.get(STORM)) instanceof SkyCrack c ? c : null;
	}

	void setUp(int seed, float tall, float hp, SkyCrack storm) {
		entityData.set(SEED, seed);
		entityData.set(TALL, tall);
		entityData.set(STORM, storm.getId());
		this.hp = this.hpMax = hp;
		this.crack = storm.getUUID();
	}

	@Override
	public void onSyncedDataUpdated(EntityDataAccessor<?> key) {
		super.onSyncedDataUpdated(key);
		if (HURT.equals(key)) struck = System.currentTimeMillis();
	}

	@Override
	public void tick() {
		super.tick();
		if (!(level() instanceof ServerLevel l)) return;
		if (tickCount < RISE && tickCount % 4 == 0) {
			// bursting up: the ground breaking round its foot
			l.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, l.getBlockState(blockPosition().below()).isAir() ? Blocks.DIRT.defaultBlockState()
					: l.getBlockState(blockPosition().below())), getX(), getY() + 0.3, getZ(), 14, 1.4, 0.2, 1.4, 0.15);
			if (tickCount == 0) {
				l.playSound(null, getX(), getY(), getZ(), SoundEvents.GENERIC_EXPLODE.value(), SoundSource.HOSTILE, 1.6f, 0.5f);
				l.playSound(null, getX(), getY(), getZ(), SoundEvents.DEEPSLATE_BREAK, SoundSource.HOSTILE, 2.5f, 0.5f);
			}
		}
		if (tickCount % 70 == 35) l.playSound(null, getX(), getY() + tall(), getZ(), SoundEvents.BEACON_AMBIENT, SoundSource.HOSTILE, 2f, 0.5f);
		if (crack == null || !SkyCracks.LIVE.containsKey(crack)) discard();
	}

	@Override
	public boolean isPickable() {
		return isAlive() && tickCount >= RISE;
	}

	@Override
	public boolean hurt(DamageSource src, float amount) {
		if (level().isClientSide || isRemoved() || tickCount < RISE) return false;
		Entity by = src.getEntity();
		if (!(by instanceof Player) && !(by instanceof Adventurer)) return false;
		hp -= amount;
		entityData.set(HURT, 1 - Math.max(0, hp) / Math.max(1, hpMax));
		ServerLevel l = (ServerLevel) level();
		l.playSound(null, getX(), getY() + 1, getZ(), SoundEvents.DEEPSLATE_HIT, SoundSource.HOSTILE, 1.8f, 0.5f + random.nextFloat() * 0.2f);
		l.playSound(null, getX(), getY() + 1, getZ(), SoundEvents.AMETHYST_BLOCK_HIT, SoundSource.HOSTILE, 1.2f, 0.5f);
		if (hp <= 0) {
			l.playSound(null, getX(), getY() + 2, getZ(), SoundEvents.GENERIC_EXPLODE.value(), SoundSource.HOSTILE, 2.5f, 0.6f);
			l.playSound(null, getX(), getY() + tall(), getZ(), SoundEvents.BEACON_DEACTIVATE, SoundSource.HOSTILE, 3f, 0.5f);
			l.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, Blocks.DEEPSLATE_BRICKS.defaultBlockState()), getX(), getY() + tall() * 0.4, getZ(), 60, 1.2,
					tall() * 0.3, 1.2, 0.2);
			discard();
			SkyCracks.anchorBroken(l, this);
		}
		return true;
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
		return getBoundingBox().expandTowards(0, tall(), 0).inflate(6);
	}

	@Override
	protected void readAdditionalSaveData(CompoundTag tag) {}

	@Override
	protected void addAdditionalSaveData(CompoundTag tag) {}
}
