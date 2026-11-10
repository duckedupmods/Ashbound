package com.snoringwalrus.ashbound;

import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * What a Caller calls, bound to them by {@link Spells}: a revenant, one great champion, or one of the Bound a summon staff calls
 * (Mounts.BOUND, tools/voxbound.py). Tinted the colour of the staff that called it. The drawing is client/ThrallRender; who it fights
 * and follows is Spells.Guard and Spells.Heel.
 */
public class Thrall extends PathfinderMob {
	private static final EntityDataAccessor<Integer> TINT = SynchedEntityData.defineId(Thrall.class, EntityDataSerializers.INT);
	/** which of its blows it's throwing, where the server picks (the Colossus): -1 where the client takes them in turn */
	private static final EntityDataAccessor<Integer> BLOW = SynchedEntityData.defineId(Thrall.class, EntityDataSerializers.INT);
	/** the Colossus's blows, in tools/thrall_moves.py's order */
	private static final String[] COLOSSUS_BLOWS = {"slam", "backhand", "rake", "backhand_l", "roar"};
	/** its slam lands this far ahead and takes in all this far round; its rake hits this many times; its roar pulls from this far, no sooner than every so often */
	private static final double SLAM_AHEAD = 2.2, SLAM_REACH = 3.5, ROAR_REACH = 9, ROAR_PULL = 0.9;
	private static final int RAKES = 3, ROAR_EVERY = 160;
	private long roared = -ROAR_EVERY;
	private static final double CHASE = 1.25;
	private static final float HIT_LOOK = 0.4f;
	private static final double CLEAVE = 2.5, REACH = 3;
	/** A blow's length in ticks, and how far through it the blade comes down (tools/thrall_moves.py times them all alike). */
	private static final int SWING = 16, GREAT_SWING = 24;
	private static final float IMPACT = 0.55f;
	/** A wraith doesn't swing, it dives: off when it's done rearing back, through the one it's after and this far out past. */
	private static final float DIVE = 0.44f;
	private static final double PAST = 1.5, THROW = 0.42, FASTEST = 1.4;
	public final boolean champion;
	/** which of tools/voxthralls.py or tools/voxbound.py it is */
	public final String model;
	private boolean cleaving;
	private LivingEntity striking;
	private int landsIn, divesIn;

	public Thrall(EntityType<? extends Thrall> type, Level level, boolean champion) {
		this(type, level, champion, champion ? "champion" : "revenant");
	}

	public Thrall(EntityType<? extends Thrall> type, Level level, String model) {
		this(type, level, false, model);
	}

	private Thrall(EntityType<? extends Thrall> type, Level level, boolean champion, String model) {
		super(type, level);
		this.champion = champion;
		this.model = model;
	}

	/** the plain thrall, a wraith */
	private boolean dives() {
		return model.equals("revenant");
	}

	/** Swings slow and takes all that's near with it. */
	private boolean heavy() {
		return champion || model.equals("gatebreaker") || colossus();
	}

	/** the Crown of the Hollow King's beast */
	private boolean colossus() {
		return model.equals("colossus");
	}

	public int blowIndex() {
		return entityData.get(BLOW);
	}

	public static AttributeSupplier.Builder attributes(boolean champion) {
		return PathfinderMob.createMobAttributes().add(Attributes.MAX_HEALTH, champion ? 90 : 30).add(Attributes.MOVEMENT_SPEED, champion ? 0.3 : 0.34)
				.add(Attributes.ATTACK_DAMAGE, 4).add(Attributes.FOLLOW_RANGE, 32).add(Attributes.STEP_HEIGHT, 1.1).add(Attributes.KNOCKBACK_RESISTANCE, champion ? 1 : 0.4);
	}

	@Override
	protected void defineSynchedData(SynchedEntityData.Builder b) {
		super.defineSynchedData(b);
		b.define(TINT, 0x9A5AD8);
		b.define(BLOW, -1);
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
		goalSelector.addGoal(2, new MeleeAttackGoal(this, CHASE, true) {
			@Override
			protected void checkAndPerformAttack(LivingEntity target) {
				if (!canPerformAttack(target)) return;
				resetAttackCooldown();
				swing(InteractionHand.MAIN_HAND);
				striking = target;
				landsIn = Math.round(getCurrentSwingDuration() * IMPACT);
				if (dives()) divesIn = Math.round(getCurrentSwingDuration() * DIVE);
				if (colossus()) entityData.set(BLOW, next());
			}
		});
	}

	@Override
	public int getCurrentSwingDuration() {
		return heavy() ? GREAT_SWING : SWING;
	}

	/** The swing's timer is only run for a Monster or a Player, and the arm's drawn from it. */
	@Override
	public void aiStep() {
		updateSwingTime();
		super.aiStep();
		if (divesIn > 0 && --divesIn == 0 && striking != null) {   // thrown at it, hard enough to come out the far side
			Vec3 to = striking.position().subtract(position()).multiply(1, 0, 1);
			double far = to.length() + PAST;
			Vec3 go = to.normalize().scale(Math.min(FASTEST, far * THROW));
			setDeltaMovement(go.x, 0.12, go.z);
			hasImpulse = true;
		}
		if (landsIn > 0 && --landsIn == 0) {
			String how = colossus() && blowIndex() >= 0 ? COLOSSUS_BLOWS[blowIndex()] : "";
			if (how.equals("slam") || how.equals("roar")) land(how);
			else if (striking != null && striking.isAlive() && distanceTo(striking) < getBbWidth() + REACH) {
				doHurtTarget(striking);
				for (int n = 1; how.equals("rake") && n < RAKES && striking.isAlive(); n++) {   // the rib arms: blow on blow
					striking.invulnerableTime = 0;
					doHurtTarget(striking);
				}
			}
			striking = null;
		}
	}

	/** The Colossus's next blow: round its four, the roar put in when it's due and there's a crowd to pull. */
	private int next() {
		long now = level().getGameTime();
		int crowd = level().getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(ROAR_REACH), x -> x instanceof net.minecraft.world.entity.monster.Enemy && x.isAlive()).size();
		if (now - roared > ROAR_EVERY && crowd >= 3) {
			roared = now;
			return COLOSSUS_BLOWS.length - 1;
		}
		return (Math.max(0, blowIndex()) + 1 + random.nextInt(2)) % (COLOSSUS_BLOWS.length - 1);
	}

	/** The slam: both fists into the ground ahead, all round it hit and thrown up. The roar: all near dragged in and held. */
	private void land(String how) {
		if (!(level() instanceof ServerLevel l)) return;
		Vec3 ahead = Vec3.directionFromRotation(0, getYRot()), at = how.equals("slam") ? position().add(ahead.scale(SLAM_AHEAD * getScale())) : position();
		double reach = (how.equals("slam") ? SLAM_REACH : ROAR_REACH) * getScale();
		for (LivingEntity e : l.getEntitiesOfClass(LivingEntity.class, new net.minecraft.world.phys.AABB(at, at).inflate(reach), x -> x instanceof net.minecraft.world.entity.monster.Enemy && x.isAlive())) {
			if (e.distanceTo(this) > reach + getBbWidth()) continue;
			if (how.equals("slam")) {
				cleaving = true;   // one blow, all of them: no cleave on top
				e.invulnerableTime = 0;
				super.doHurtTarget(e);
				cleaving = false;
				e.push(0, 0.55, 0);
			} else {
				Vec3 in = position().subtract(e.position()).multiply(1, 0, 1).normalize().scale(ROAR_PULL);
				e.setDeltaMovement(in.x, 0.25, in.z);
				e.hurtMarked = true;
				e.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.MOVEMENT_SLOWDOWN, 40, 3));
			}
		}
		Spells.skillFx(l, "hammer_wave", at, Vec3.ZERO, (float) reach, null, this);
		l.playSound(null, blockPosition(), how.equals("slam") ? net.minecraft.sounds.SoundEvents.GENERIC_EXPLODE.value() : net.minecraft.sounds.SoundEvents.RAVAGER_ROAR,
				net.minecraft.sounds.SoundSource.HOSTILE, how.equals("slam") ? 0.9f : 1.6f, how.equals("slam") ? 0.6f : 0.7f);
	}

	@Override
	public boolean doHurtTarget(Entity target) {
		boolean hit = super.doHurtTarget(target);
		if (hit && level() instanceof ServerLevel l) {
			Spells.skillFx(l, "hit", target.getBoundingBox().getCenter(), Vec3.ZERO, heavy() ? 1 : HIT_LOOK, null, this);
			if (heavy() && !cleaving) {   // its blade's as long as a house: all that's near the one it hit feel it
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

	/** Thralls pass through what they fight: a pack of them leaning on a boss would walk it into a wall. */
	@Override
	public boolean isPushable() {
		return false;
	}

	@Override
	protected void doPush(Entity e) {}

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
