package com.snoringwalrus.ashbound;

import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * What a Caller calls, bound to them by {@link Spells}: a revenant, or one great champion. Tinted the colour of the staff
 * that called it. The drawing is client/ThrallRender; who it fights and follows is Spells.Guard and Spells.Heel.
 */
public class Thrall extends PathfinderMob {
	private static final EntityDataAccessor<Integer> TINT = SynchedEntityData.defineId(Thrall.class, EntityDataSerializers.INT);
	private static final double CHASE = 1.25;
	private static final float HIT_LOOK = 0.4f;
	private static final double CLEAVE = 2.5;
	public final boolean champion;
	private boolean cleaving;

	public Thrall(EntityType<? extends Thrall> type, Level level, boolean champion) {
		super(type, level);
		this.champion = champion;
	}

	public static AttributeSupplier.Builder attributes(boolean champion) {
		return PathfinderMob.createMobAttributes().add(Attributes.MAX_HEALTH, champion ? 90 : 30).add(Attributes.MOVEMENT_SPEED, champion ? 0.3 : 0.34)
				.add(Attributes.ATTACK_DAMAGE, 4).add(Attributes.FOLLOW_RANGE, 32).add(Attributes.STEP_HEIGHT, 1.1).add(Attributes.KNOCKBACK_RESISTANCE, champion ? 1 : 0.4);
	}

	@Override
	protected void defineSynchedData(SynchedEntityData.Builder b) {
		super.defineSynchedData(b);
		b.define(TINT, 0x9A5AD8);
	}

	public int tint() {
		return entityData.get(TINT);
	}

	void tint(int rgb) {
		entityData.set(TINT, rgb);
	}

	@Override
	protected void registerGoals() {
		goalSelector.addGoal(0, new FloatGoal(this));
		goalSelector.addGoal(2, new MeleeAttackGoal(this, CHASE, true));
	}

	@Override
	public boolean doHurtTarget(Entity target) {
		boolean hit = super.doHurtTarget(target);
		if (hit && level() instanceof ServerLevel l) {
			Spells.skillFx(l, "hit", target.getBoundingBox().getCenter(), Vec3.ZERO, champion ? 1 : HIT_LOOK, null);
			if (champion && !cleaving) {   // its blade's as long as a house: all that's near the one it hit feel it
				cleaving = true;
				for (var e : l.getEntitiesOfClass(net.minecraft.world.entity.LivingEntity.class, target.getBoundingBox().inflate(CLEAVE), x -> x instanceof net.minecraft.world.entity.monster.Enemy && x != target && x.isAlive()))
					super.doHurtTarget(e);
				cleaving = false;
			}
		}
		return hit;
	}

	@Override
	public void tick() {
		super.tick();
		if (level().isClientSide && tickCount % 3 == 0)
			level().addParticle(Vfx.wisp(tint(), champion ? 0.5f : 0.3f, 16, -0.02f, true), getX() + (random.nextDouble() - 0.5) * getBbWidth(), getY() + 0.2, getZ() + (random.nextDouble() - 0.5) * getBbWidth(), 0, 0.02, 0);
	}

	@Override
	public boolean causeFallDamage(float distance, float mult, DamageSource source) {
		return false;
	}

	@Override
	protected boolean shouldDespawnInPeaceful() {
		return false;
	}

	@Override
	public boolean removeWhenFarAway(double distance) {
		return false;
	}
}
