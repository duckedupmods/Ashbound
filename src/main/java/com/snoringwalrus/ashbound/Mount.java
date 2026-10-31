package com.snoringwalrus.ashbound;

import java.util.HashMap;
import java.util.Map;

import com.snoringwalrus.ashbound.mixin.JumpingAccessor;
import com.snoringwalrus.ashbound.mixin.VehicleFloatAccessor;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * What {@link Mounts} calls up: no goals, no drops, no save, driven by its rider on the rider's client as a horse is. It lasts
 * as long as someone is on it. The client keeps its own stride (position and speed from how far it really moved), because a
 * rider's client drives it and everyone else only sees it arrive in steps.
 *
 * Getting on and off is a move, not a cut. It appears beside you and rears, and you vault up as it comes down; to get off it stops,
 * you drop to the side you came from, and only then does it toss its head and fade. The rider stays a passenger all the way
 * through, carried along that arc by getPassengerAttachmentPoint, so nobody jumps from one place to another.
 *
 * A mount with Wings (Mounts.TRACKS) takes to the air: jump, then jump again up there. Hold jump to climb; forward goes where you
 * look. Its wind runs out after a while and it comes down in a long glide, and fills again on the ground. A Stormdrake glides down
 * like that from the start. At the last rank of Wings the wind never runs out, on any mount. A second person climbs up behind by right-clicking the
 * mount or whoever's riding it; the one in front steers.
 */
public class Mount extends Mob {
	/** ticks a new mount waits for its rider, how long it grows in, the vault up, the hop down, the fade, and how long it rears */
	private static final int WAIT = 10, APPEAR = 7, VAULT = 11, HOP = 9, FADE = 14, REAR = 15;
	/** the arc: how far beside the mount a rider stands, and how high over the saddle line the vault goes (blocks) */
	static final double BESIDE = 1.5;
	private static final double OVER = 0.45;
	private static final EntityDataAccessor<Boolean> LEAVING = SynchedEntityData.defineId(Mount.class, EntityDataSerializers.BOOLEAN);
	/** which side the rider gets on or off: 1 its left, -1 its right, 0 straight up and down */
	private static final EntityDataAccessor<Integer> SIDE = SynchedEntityData.defineId(Mount.class, EntityDataSerializers.INT);
	/** in the air: blocks a tick forward, the drake's and the others', climbing, hanging still, and the fall with no wind left */
	private static final double SOAR = 1.0, FLY = 0.72, CLIMB = 0.4, HANG = -0.03, SINK = -0.1;
	/** how many ticks on the ground fill the wind; how many it holds depends on Wings */
	private static final float FILL_TICKS = 300;
	/** the rider's wind, kept here because the mount itself is gone each time they get off */
	public static float wind = 1;
	/** the second seat: how far behind the first, in blocks */
	private static final double BEHIND = 0.85;
	private static final int SOFT_LANDING = 160;
	/** a charge needs this share of top speed, and hits each monster this often (ticks) */
	private static final double CHARGE_AT = 0.75;
	private static final int CHARGE_EVERY = 20;
	private static final double CHARGE_DAMAGE = 1.5, CHARGE_SHOVE = 1.6;
	/** It builds up through its gaits: the share of top speed from a standstill, how much it gains a tick, and its top turn in degrees a tick. */
	private static final float FROM_REST = 0.35f, BUILD_UP = 0.03f, TURN_FAST = 16, TURN_FLAT_OUT = 9;
	/** Off the ground this many ticks before the legs tuck, so a step down isn't a leap. */
	private static final int AIRBORNE = 3;

	public final Mounts.Kind kind;
	private final Map<Integer, Integer> charged = new HashMap<>();
	private double lastX, lastZ;
	private int left, faded;
	private boolean jumpHeld;
	private float pace;
	private int offGround;

	// the client's own stride, see the class comment: stride counts leg cycles, gait goes 0 to 1 with speed, turn and look in radians
	public float stride, strideO, gait, gaitO, air, airO, turn, turnO, look, lookO;
	public boolean gliding;

	public Mount(EntityType<Mount> type, Level level) {
		super(type, level);
		kind = Mounts.ofType(type);
		noCulling = true;
		setPersistenceRequired();
	}

	static AttributeSupplier.Builder attributes(Mounts.Kind k) {
		return Mob.createMobAttributes().add(Attributes.MAX_HEALTH, 20).add(Attributes.MOVEMENT_SPEED, k.speed()).add(Attributes.STEP_HEIGHT, k.step());
	}

	@Override
	protected void defineSynchedData(SynchedEntityData.Builder b) {
		super.defineSynchedData(b);
		b.define(LEAVING, false);
		b.define(SIDE, 0);
	}

	void side(int side) {
		entityData.set(SIDE, side);
	}

	private boolean leaving() {
		return entityData.get(LEAVING);
	}

	/** Sound and light when it's called: a ring running out along the ground from under it. */
	void arrive() {
		if (!(level() instanceof ServerLevel sl)) return;
		for (int i = 0; i < 28; i++) {
			double a = i * Math.PI * 2 / 28;
			sl.sendParticles(trail(), getX() + Math.cos(a) * 0.7, getY() + 0.1, getZ() + Math.sin(a) * 0.7, 0, Math.cos(a), 0.05, Math.sin(a), 0.16);
		}
		sl.sendParticles(trail(), getX(), getY() + 1, getZ(), 30, 0.6, 0.8, 0.6, 0.03);
		sl.playSound(null, getX(), getY(), getZ(), SoundEvents.EVOKER_CAST_SPELL, SoundSource.PLAYERS, 0.9f, 0.7f);
	}

	/** Getting off, by the key or by sneaking. On the ground it's the hop; in the air or the water you just let go. */
	void leave() {
		if (leaving() || !(getFirstPassenger() instanceof Player p)) return;
		if (!onGround() || isInWater()) {
			entityData.set(LEAVING, true);
			left = HOP;
			letGo(p);
			return;
		}
		entityData.set(SIDE, clear(p, 1) ? 1 : clear(p, -1) ? -1 : 0);
		entityData.set(LEAVING, true);
		level().playSound(null, getX(), getY(), getZ(), SoundEvents.ARMOR_EQUIP_LEATHER.value(), SoundSource.PLAYERS, 0.8f, 1);
	}

	/** Someone letting go in the air comes down softly: you can't always pick where a mount lands. */
	private void letGo(Player p) {
		if (!onGround() && !isInWater()) p.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.SLOW_FALLING, SOFT_LANDING));
		p.stopRiding();
	}

	/** The one behind getting down: only them, the mount stays with its rider. */
	void hopOff(Player p) {
		letGo(p);
	}

	/** Up behind the rider, if there's a seat. */
	boolean board(Player p) {
		if (leaving() || p.isPassenger() || p == getFirstPassenger() || !canAddPassenger(p) || !isVehicle()) return false;
		return p.startRiding(this, true);
	}

	@Override
	protected boolean canAddPassenger(Entity e) {
		return getPassengers().size() < 2;
	}

	@Override
	protected net.minecraft.world.InteractionResult mobInteract(Player p, net.minecraft.world.InteractionHand hand) {
		if (hand != net.minecraft.world.InteractionHand.MAIN_HAND || leaving() || p.isPassenger() || getPassengers().size() != 1) return net.minecraft.world.InteractionResult.PASS;
		if (!level().isClientSide) board(p);
		return net.minecraft.world.InteractionResult.sidedSuccess(level().isClientSide);
	}

	private boolean clear(Player p, int side) {
		Vec3 to = new Vec3(side * BESIDE, 0, 0).yRot(-getYRot() * Mth.DEG_TO_RAD).add(position());
		return level().noCollision(p, p.getBoundingBox().move(to.subtract(p.position())));
	}

	/** How far into the saddle the rider is: 0 on the ground beside it, 1 sitting. */
	private float seated() {
		return Mth.clamp(leaving() ? 1 - (float) left / HOP : (float) tickCount / VAULT, 0, 1);
	}

	private boolean busy() {
		return leaving() || tickCount < VAULT;
	}

	/** Its size now, of its full size: grows in past full and settles, shrinks away at the end. */
	public float size(float pt) {
		float x = Mth.clamp((tickCount + pt) / APPEAR, 0, 1) - 1;
		float grown = 1 + 2.70158f * x * x * x + 1.70158f * x * x;
		float gone = faded > 0 ? Mth.clamp((faded + pt) / FADE, 0, 1) : 0;
		return (0.5f + 0.5f * grown) * (1 - gone * gone);
	}

	/** How far up it's rearing, 0 to 1: as it arrives, and a smaller toss once its rider is off. */
	public float rear(float pt) {
		float in = Mth.clamp((tickCount + pt) / REAR, 0, 1), out = Mth.clamp((faded + pt) / FADE, 0, 1);
		return Mth.sin(in * Mth.PI) + (faded > 0 ? Mth.sin(out * Mth.PI) * 0.6f : 0);
	}

	private ParticleOptions trail() {
		return switch (kind.id()) {
			case "ashmane" -> ParticleTypes.FLAME;
			case "rimehorn" -> ParticleTypes.SNOWFLAKE;
			case "gravefang" -> ParticleTypes.SOUL_FIRE_FLAME;
			case "thornback" -> ParticleTypes.SPORE_BLOSSOM_AIR;
			default -> ParticleTypes.ELECTRIC_SPARK;
		};
	}

	@Override
	public void tick() {
		super.tick();
		if (leaving()) {
			if (left < HOP) left++;
			if (!isVehicle()) faded++;
		}
		if (level().isClientSide) {
			strideO = stride;
			gaitO = gait;
			airO = air;
			turnO = turn;
			lookO = look;
			double moved = Math.hypot(getX() - xo, getZ() - zo);
			gait += ((float) Math.min(1, moved / (kind.speed() * 2.2)) - gait) * 0.2f;
			stride += (float) moved / Mth.lerp(gait, kind.strideWalk(), kind.strideRun());
			offGround = onGround() ? 0 : offGround + 1;
			air += ((offGround > AIRBORNE ? 1 : 0) - air) * 0.25f;
			turn += (Mth.clamp(Mth.wrapDegrees(yBodyRot - yBodyRotO) * Mth.DEG_TO_RAD * 2.5f, -0.8f, 0.8f) - turn) * 0.2f;
			float wanted = getFirstPassenger() instanceof Player p ? Mth.clamp(Mth.wrapDegrees(p.getYRot() - yBodyRot) * Mth.DEG_TO_RAD, -0.9f, 0.9f) : 0;
			look += (wanted - look) * 0.2f;
			if (random.nextFloat() < 0.1f + gait * 0.5f)
				level().addParticle(trail(), getX() + (random.nextDouble() - 0.5) * kind.w(), getY() + 0.2 + random.nextDouble() * 0.5, getZ() + (random.nextDouble() - 0.5) * kind.w(), 0, 0.02, 0);
			for (int i = 0; faded > 0 && i < 3; i++)
				level().addParticle(trail(), getX() + (random.nextDouble() - 0.5) * kind.w() * 1.6, getY() + random.nextDouble() * kind.h() * 1.4, getZ() + (random.nextDouble() - 0.5) * kind.w() * 1.6, 0, 0.05, 0);
			return;
		}
		Player rider = getFirstPassenger() instanceof Player p ? p : null;
		if (rider == null && !leaving() && tickCount > WAIT) {
			left = HOP;
			entityData.set(LEAVING, true);
		}
		if (rider != null && !leaving() && tickCount > VAULT && rider.isShiftKeyDown()) leave();
		if (getPassengers().size() > 1 && getPassengers().get(1) instanceof Player behind && behind.isShiftKeyDown()) hopOff(behind);
		if (rider instanceof ServerPlayer sp) ((VehicleFloatAccessor) sp.connection).ashbound$floating(0);
		if (tickCount == VAULT) level().playSound(null, getX(), getY(), getZ(), SoundEvents.HORSE_LAND, SoundSource.PLAYERS, 0.7f, 0.8f);
		if (rider != null && leaving() && left >= HOP) {
			letGo(rider);
			level().playSound(null, getX(), getY(), getZ(), SoundEvents.EVOKER_CAST_SPELL, SoundSource.PLAYERS, 0.5f, 1.3f);
		}
		if (faded >= FADE) {
			discard();
			return;
		}
		if (kind.charges() && rider != null) charge(rider);
		lastX = getX();
		lastZ = getZ();
	}

	/** Thornback at full tilt: what's in the way takes the rider's weapon damage and goes flying. */
	private void charge(Player p) {
		double vx = getX() - lastX, vz = getZ() - lastZ, v = Math.hypot(vx, vz);
		if (tickCount < 2 || v < kind.speed() * 2.2 * CHARGE_AT) return;
		int now = tickCount;
		charged.values().removeIf(t -> now - t > CHARGE_EVERY);
		for (LivingEntity e : level().getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(0.6), x -> x instanceof Enemy && x.isAlive())) {
			if (charged.putIfAbsent(e.getId(), now) != null) continue;
			e.hurt(damageSources().playerAttack(p), (float) (p.getAttributeValue(Attributes.ATTACK_DAMAGE) * CHARGE_DAMAGE));
			e.knockback(CHARGE_SHOVE, -vx / v, -vz / v);
			level().playSound(null, e.getX(), e.getY(), e.getZ(), SoundEvents.PLAYER_ATTACK_KNOCKBACK, SoundSource.PLAYERS, 1, 0.7f);
		}
	}

	@Override
	public LivingEntity getControllingPassenger() {
		return getFirstPassenger() instanceof Player p ? p : null;
	}

	@Override
	protected void tickRidden(Player p, Vec3 in) {
		super.tickRidden(p, in);
		yBodyRot = yHeadRot = getYRot();
		if (busy()) {
			pace = 0;
			return;
		}
		// it turns as an animal does, in an arc; the rider can look further than it has come round
		float most = Mth.lerp(pace, TURN_FAST, TURN_FLAT_OUT);
		setRot(getYRot() + Mth.clamp(Mth.wrapDegrees(p.getYRot() - getYRot()), -most, most), 0);
		yBodyRot = yHeadRot = getYRot();
		pace = p.zza > 0 ? Math.min(1, pace + BUILD_UP) : Math.max(0, pace - BUILD_UP * 4);
		boolean jump = ((JumpingAccessor) p).ashbound$jumping();
		Vec3 v = getDeltaMovement();
		if (isInWater()) {
			setDeltaMovement(v.x, Math.min(0.12, v.y + 0.06), v.z);
			gliding = false;
		} else if (onGround()) {
			gliding = false;
			wind = Math.min(1, wind + 1 / FILL_TICKS);
			if (jump && !jumpHeld) {
				setDeltaMovement(v.x, kind.jump() * Mounts.jumpFor(p), v.z);
				hasImpulse = true;
			}
		} else {
			if (jump && !jumpHeld && (kind.glides() || Mounts.airTicks(p) > 0)) gliding = true;
			if (gliding) fly(p, jump);
		}
		jumpHeld = jump;
	}

	/** Up here it goes at the rider's word, not by what its legs last did. */
	private void fly(Player p, boolean climbing) {
		int air = Mounts.airTicks(p);
		boolean tireless = Mounts.tireless(p), forward = p.zza > 0;
		if (!tireless && air > 0) wind = Math.max(0, wind - 1f / air);
		boolean lift = air > 0 && (tireless || wind > 0);
		double speed = (kind.glides() ? SOAR : FLY) * Mth.lerp(pace, FROM_REST, 1);
		Vec3 f = Vec3.directionFromRotation(0, getYRot()), look = Vec3.directionFromRotation(p.getXRot(), getYRot());
		double up = !lift ? SINK : climbing ? CLIMB : forward ? look.y * speed : HANG;
		double ahead = forward ? (lift ? Math.hypot(look.x, look.z) : 1) * speed : 0;
		setDeltaMovement(f.x * ahead, up, f.z * ahead);
		hasImpulse = true;
	}

	@Override
	protected Vec3 getRiddenInput(Player p, Vec3 in) {
		float forward = p.zza;
		if (busy()) return Vec3.ZERO;
		return new Vec3(p.xxa * 0.5f, 0, forward <= 0 ? forward * 0.3f : forward);
	}

	@Override
	protected float getRiddenSpeed(Player p) {
		return (float) getAttributeValue(Attributes.MOVEMENT_SPEED) * Mth.lerp(pace, FROM_REST, 1) * Mounts.speedFor(p);
	}

	@Override
	protected Vec3 getPassengerAttachmentPoint(Entity rider, EntityDimensions size, float scale) {
		if (getPassengers().indexOf(rider) > 0)   // the seat behind: no vault, they just climb up
			return new Vec3(0, kind.seatY() * kind.scale() + 0.05, (kind.seatZ() * kind.scale() - BEHIND)).yRot(-getYRot() * Mth.DEG_TO_RAD);
		float a = seated(), e = a * a * (3 - 2 * a);
		double foot = rider.getVehicleAttachmentPoint(this).y, seat = kind.seatY() * kind.scale() + 0.1;
		double y = Mth.lerp(e, foot, seat) + Math.sin(a * Math.PI) * OVER;
		return new Vec3((1 - e) * entityData.get(SIDE) * BESIDE, y, kind.seatZ() * kind.scale() * e).yRot(-getYRot() * Mth.DEG_TO_RAD);
	}

	/** The arc has already put the rider where they should end up. */
	@Override
	public Vec3 getDismountLocationForPassenger(LivingEntity rider) {
		return rider.position();
	}

	@Override
	public boolean hurt(DamageSource src, float amount) {
		return src.is(DamageTypeTags.BYPASSES_INVULNERABILITY) && super.hurt(src, amount);
	}

	/** So someone can right-click their way up behind the rider. It still can't be struck. */
	@Override
	public boolean isPickable() {
		return !leaving();
	}

	@Override
	public boolean isPushable() {
		return false;
	}

	@Override
	public boolean isAttackable() {
		return false;
	}

	@Override
	public boolean canBeLeashed() {
		return false;
	}

	@Override
	public boolean dismountsUnderwater() {
		return false;
	}

	@Override
	public boolean causeFallDamage(float dist, float mult, DamageSource src) {
		return false;
	}

	@Override
	public boolean shouldRenderAtSqrDistance(double d) {
		return d < 256 * 256;
	}
}
