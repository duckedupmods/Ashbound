package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.EnumSet;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

import javax.annotation.Nullable;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.target.TargetGoal;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.monster.RangedAttackMob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;

/**
 * An adventurer out in the world (Adventurers): one of a party of a few, of one rank, in real gear from the loot pools, who fight
 * whatever monster is near them or is on a player, each by their role: the shieldbearer in front, the blades round the sides and
 * back of it, archers and mages hanging back. They can't hurt players or be hurt by them, and they go once nobody's near.
 */
public class Adventurer extends PathfinderMob implements RangedAttackMob {
	private static final EntityDataAccessor<String> KIND = SynchedEntityData.defineId(Adventurer.class, EntityDataSerializers.STRING);
	private static final EntityDataAccessor<String> ROLE = SynchedEntityData.defineId(Adventurer.class, EntityDataSerializers.STRING);
	private static final EntityDataAccessor<String> RANK = SynchedEntityData.defineId(Adventurer.class, EntityDataSerializers.STRING);
	/** what they're saying over their head right now, "" for nothing (AdventurerTalk) */
	private static final EntityDataAccessor<String> BARK = SynchedEntityData.defineId(Adventurer.class, EntityDataSerializers.STRING);
	/** dead where they fell (Encounters' fallen party): 0 alive, else how they lie (1 on the back, 2 face down, 3 curled on a side) */
	private static final EntityDataAccessor<Integer> FALLEN = SynchedEntityData.defineId(Adventurer.class, EntityDataSerializers.INT);
	/** how far off a line over their head is heard, and how long it stays up */
	static final double HEAR = 20;
	private static final int BARK_TICKS = 80;

	/** who they're with (the same for the whole party), their place in it (0 leads), the party's name */
	UUID party = new UUID(0, 0);
	int slot;
	String partyName = "";
	/** how their weapon is swung (MobMoves' stance), or "bow", or "black"/"white" for mages */
	String fights = "sword";
	/** the dungeon whose element a mage's spells are */
	String gate = "cellar";
	/** ticks with nobody near; ticks since their last fight */
	int alone, calm;
	/** what they're about when not fighting: "roam" (the leader picks somewhere and goes), "camp" (round a fire at home till
	 * morning), "post" (about home, for `stay` ticks, or for good if it's -1: in town) */
	String mode = "roam";
	@Nullable
	BlockPos home;
	int stay = -1;
	/** nobody of the party who's still here comes before them: they lead (looked at now and then, in aiStep) */
	boolean leads = true;
	/** speaking: when their line comes down, and when they'll next say something of their own (game time); when they last cried out */
	private long barkUntil, nextBark, hurtBark;
	/** in a fight, by the last look; the player who pitched in on it; players they've nodded to; players they owe */
	private boolean fighting;
	@Nullable
	UUID helper;
	private final Set<UUID> seen = new HashSet<>(), owed = new HashSet<>();
	/** stopped to talk to someone, for this many ticks */
	private int hold;
	@Nullable
	private UUID heldBy;
	/** what the party would ask of someone ("report", "fetch", "camp"; "" nothing), who's said no to it; where they're headed, if
	 * they've asked you to clear a camp with them */
	String ask = "";
	/** a scene's (Encounters): walking someone to town, hurt too badly to mend on the way; the player they're duelling */
	@Nullable
	UUID escort, duel;
	boolean wounded;
	final Set<UUID> refused = new HashSet<>();
	@Nullable
	BlockPos task;
	/** client: when the line now over their head went up (ms) */
	public long barkSince;

	public Adventurer(EntityType<? extends Adventurer> type, Level level) {
		super(type, level);
		setPersistenceRequired();
	}

	public static AttributeSupplier.Builder attributes() {
		return PathfinderMob.createMobAttributes().add(Attributes.MAX_HEALTH, 40).add(Attributes.MOVEMENT_SPEED, 0.3).add(Attributes.ATTACK_DAMAGE, 1)
				.add(Attributes.FOLLOW_RANGE, 32).add(Attributes.ARMOR, 0)
				.add(yesman.epicfight.registry.entries.EpicFightAttributes.STUN_ARMOR, 0);
	}

	@Override
	protected void defineSynchedData(SynchedEntityData.Builder b) {
		super.defineSynchedData(b);
		b.define(KIND, "");
		b.define(ROLE, "tank");
		b.define(RANK, "F");
		b.define(BARK, "");
		b.define(FALLEN, 0);
	}

	public int fallen() {
		return entityData == null ? 0 : entityData.get(FALLEN);
	}

	/** Dead where they fell: lying still (AdventurerPatch's poses), out of everyone's way, nothing to fight; searched, not talked to. */
	void fallDown(int pose) {
		entityData.set(FALLEN, Math.max(1, Math.min(3, pose)));
		entityData.set(BARK, "");
		setNoAi(true);
		setInvulnerable(true);
		setSilent(true);
		setTarget(null);
		getNavigation().stop();
		refreshDimensions();
	}

	@Override
	public net.minecraft.world.entity.EntityDimensions getDefaultDimensions(net.minecraft.world.entity.Pose pose) {
		return fallen() > 0 ? net.minecraft.world.entity.EntityDimensions.scalable(1.4f, 0.5f) : super.getDefaultDimensions(pose);
	}

	@Override
	public boolean canBeSeenAsEnemy() {
		return fallen() == 0 && super.canBeSeenAsEnemy();
	}

	@Override
	public boolean isPushable() {
		return fallen() == 0 && super.isPushable();
	}

	public String kindId() {
		return entityData.get(KIND);
	}

	public String role() {
		return entityData.get(ROLE);
	}

	public String bark() {
		return entityData.get(BARK);
	}

	@Override
	public void onSyncedDataUpdated(EntityDataAccessor<?> key) {
		super.onSyncedDataUpdated(key);
		if (BARK.equals(key)) barkSince = System.currentTimeMillis();
		if (FALLEN.equals(key)) refreshDimensions();
	}

	public String rank() {
		return entityData.get(RANK);
	}

	void setUp(String kind, String role, String rank) {
		entityData.set(KIND, kind);
		entityData.set(ROLE, role);
		entityData.set(RANK, rank);
	}

	boolean melee() {
		return !fights.equals("bow") && !fights.equals("black") && !fights.equals("white");
	}

	// ---------------------------------------------------------------- goals

	@Override
	protected void registerGoals() {
		goalSelector.addGoal(0, new FloatGoal(this));
		goalSelector.addGoal(3, new Escort());
		goalSelector.addGoal(4, new Follow());
		goalSelector.addGoal(5, new Hold());
		goalSelector.addGoal(6, new Roam());
		goalSelector.addGoal(7, new LookAtPlayerGoal(this, Player.class, 8));
		goalSelector.addGoal(8, new RandomLookAroundGoal(this));
		targetSelector.addGoal(1, new Defend());
	}

	/** The party's others still here. */
	List<Adventurer> mates() {
		if (!(level() instanceof ServerLevel l)) return List.of();
		List<Adventurer> out = new ArrayList<>();
		for (Adventurer a : l.getEntitiesOfClass(Adventurer.class, getBoundingBox().inflate(48), a -> a != this && a.party.equals(party) && a.isAlive()))
			out.add(a);
		return out;
	}

	@Nullable
	Adventurer leader() {
		return mates().stream().min(Comparator.comparingInt(a -> a.slot)).filter(a -> a.slot < slot).orElse(null);
	}

	/** Walking someone to safety: at their heels, not too fast for a wound. */
	final class Escort extends Goal {
		Escort() {
			setFlags(EnumSet.of(Flag.MOVE));
		}

		@Override
		public boolean requiresUpdateEveryTick() {
			return true;
		}

		@Nullable
		private Player who() {
			return escort == null ? null : level().getPlayerByUUID(escort);
		}

		@Override
		public boolean canUse() {
			Player p = who();
			return getTarget() == null && p != null && distanceToSqr(p) > 9 && distanceToSqr(p) < 64 * 64;
		}

		@Override
		public boolean canContinueToUse() {
			return canUse() && !getNavigation().isDone();
		}

		@Override
		public void tick() {
			Player p = who();
			if (p != null && tickCount % 10 == 0) getNavigation().moveTo(p, wounded ? 0.9 : 1.0);
		}
	}

	/** Not fighting: keep near whoever leads, a step behind and to one side. */
	final class Follow extends Goal {
		Follow() {
			setFlags(EnumSet.of(Flag.MOVE));
		}

		@Override
		public boolean requiresUpdateEveryTick() {
			return true;
		}

		@Override
		public boolean canUse() {
			if (getTarget() != null || leads || hold > 0 || mode.equals("camp")) return false;
			Adventurer l = leader();
			return l != null && distanceToSqr(l) > 9;
		}

		@Override
		public boolean canContinueToUse() {
			return canUse() && !getNavigation().isDone();
		}

		@Override
		public void tick() {
			Adventurer l = leader();
			if (l == null || tickCount % 10 != 0) return;
			// far behind after a chase: jog back to them (never a jump: you'd see it)
			double a = Math.toRadians(l.getYRot() + 180 + (slot % 2 == 0 ? 35 : -35) * ((slot + 1) / 2)), d = 2.2;
			getNavigation().moveTo(l.getX() - Math.sin(a) * d, l.getY(), l.getZ() + Math.cos(a) * d, distanceToSqr(l) > 100 ? 1.25 : 0.9);
		}
	}

	/** Whoever leads, out in the wilds: somewhere 40 to 80 blocks off, a little off the way they were already going, on dry ground,
	 * walked in legs of 16 (a path finder sees no farther), then a rest and the next. Any ground: no roads. */
	final class Roam extends Goal {
		@Nullable
		Vec3 dest;
		double heading = Double.NaN;
		int rest, legs;

		Roam() {
			setFlags(EnumSet.of(Flag.MOVE));
		}

		@Override
		public boolean canUse() {
			if (!leads || getTarget() != null || hold > 0 || !mode.equals("roam")) return false;
			if (rest > 0) {
				rest -= 2;   // asked every other tick
				return false;
			}
			// a camp they've asked you to help clear: there, before anywhere of their own
			if (dest == null) dest = task != null ? Vec3.atBottomCenterOf(task) : pick();
			return dest != null;
		}

		@Override
		public boolean canContinueToUse() {
			return leads && getTarget() == null && hold <= 0 && mode.equals("roam") && dest != null;
		}

		@Override
		public void start() {
			legs = 0;
		}

		@Override
		public void tick() {
			if (dest == null) return;
			if (position().distanceToSqr(dest.x, getY(), dest.z) < 25 || legs > 10) {
				dest = null;
				rest = task != null ? 40 : 100 + getRandom().nextInt(400);
				return;
			}
			if (!getNavigation().isDone()) return;
			legs++;
			Vec3 to = new Vec3(dest.x - getX(), 0, dest.z - getZ());
			Vec3 step = position().add(to.normalize().scale(Math.min(16, to.length())));
			BlockPos at = level().getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, BlockPos.containing(step));
			if (!getNavigation().moveTo(at.getX() + 0.5, at.getY(), at.getZ() + 0.5, task != null ? 0.95 : 0.75)) {
				// no way through (a cliff, a lake): turn and pick again
				heading += Math.PI / 2 * (getRandom().nextBoolean() ? 1 : -1);
				dest = null;
			}
		}

		@Nullable
		private Vec3 pick() {
			if (Double.isNaN(heading)) heading = getRandom().nextDouble() * Math.PI * 2;
			for (int k = 0; k < 8; k++) {
				double a = heading + (getRandom().nextDouble() - 0.5) * Math.toRadians(120), d = 40 + getRandom().nextDouble() * 40;
				BlockPos col = BlockPos.containing(getX() + Math.cos(a) * d, 0, getZ() + Math.sin(a) * d);
				if (!level().hasChunkAt(col)) {
					heading += Math.PI * 0.6;
					continue;
				}
				BlockPos top = level().getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, col);
				if (!level().getFluidState(top).isEmpty() || !level().getFluidState(top.below()).isEmpty()) {
					heading += 0.8;
					continue;
				}
				heading = a;
				return Vec3.atBottomCenterOf(top);
			}
			return null;
		}
	}

	/** Camp: each to a place round the fire, facing it, the shieldbearer a few steps further out, looking out. Post: whoever leads
	 * idles about home and the rest keep by them (Follow). */
	final class Hold extends Goal {
		int wait;
		@Nullable
		Vec3 spot;

		Hold() {
			setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
		}

		@Override
		public boolean requiresUpdateEveryTick() {
			return true;
		}

		@Override
		public boolean canUse() {
			return getTarget() == null && hold <= 0 && home != null && (mode.equals("camp") || mode.equals("post") && leads);
		}

		@Override
		public void stop() {
			spot = null;
			wait = 0;
		}

		@Override
		public void tick() {
			if (home == null) return;
			Vec3 fire = Vec3.atBottomCenterOf(home);
			if (mode.equals("camp")) {
				boolean watch = role().equals("tank");
				if (--wait <= 0) {
					wait = 20;
					int n = 1;
					for (Adventurer a : mates()) n = Math.max(n, a.slot + 1);
					n = Math.max(n, slot + 1);
					double a = Math.PI * 2 * slot / n + home.hashCode() % 7, d = watch ? 6 : 2.4;
					spot = fire.add(Math.cos(a) * d, 0, Math.sin(a) * d);
					if (position().distanceToSqr(spot.x, getY(), spot.z) > 0.8) getNavigation().moveTo(spot.x, home.getY(), spot.z, 0.8);
					else getNavigation().stop();
				}
				if (watch) getLookControl().setLookAt(getX() * 2 - fire.x, getEyeY(), getZ() * 2 - fire.z);
				else if (getNavigation().isDone()) getLookControl().setLookAt(fire.x, fire.y + 0.2, fire.z);
			} else if (--wait <= 0) {
				wait = 160 + getRandom().nextInt(240);
				getNavigation().moveTo(fire.x + getRandom().nextInt(17) - 8, home.getY(), fire.z + getRandom().nextInt(17) - 8, 0.6);
			}
		}
	}

	/** What they fight: whatever's on a player or one of them first, then any monster close by that they can see. */
	final class Defend extends TargetGoal {
		Defend() {
			super(Adventurer.this, true);
		}

		/** Minecraft asks a target goal every other tick, which ticks going by the mob's id: a countdown, not tickCount, spaces the looks. */
		private int wait;

		@Override
		public boolean canUse() {
			if (--wait > 0) return false;
			wait = 5;
			LivingEntity t = pick();
			if (t == null) return false;
			setTarget(t);
			return true;
		}

		@Override
		public boolean canContinueToUse() {
			LivingEntity t = getTarget();
			return t != null && t.isAlive() && distanceToSqr(t) < 28 * 28;
		}

		@Nullable
		private LivingEntity pick() {
			if (!(level() instanceof ServerLevel l)) return null;
			// one bout, with whoever took them on
			if (duel != null) {
				Player d = l.getPlayerByUUID(duel);
				return d != null && d.isAlive() && distanceToSqr(d) < 28 * 28 ? d : null;
			}
			// a party fights together: whatever hit them, then what a mate is fighting, then a monster of their own
			LivingEntity hit = getLastHurtByMob();
			if (hit instanceof Enemy && hit.isAlive() && tickCount - getLastHurtByMobTimestamp() < 200) return hit;
			LivingEntity shared = mates().stream().map(Mob::getTarget).filter(t -> t != null && t.isAlive() && distanceToSqr(t) < 28 * 28)
					.min(Comparator.comparingDouble(t -> distanceToSqr(t))).orElse(null);
			if (shared != null) return shared;
			LivingEntity best = null;
			double bestScore = Double.MAX_VALUE;
			for (Mob m : l.getEntitiesOfClass(Mob.class, getBoundingBox().inflate(16), m -> m instanceof Enemy && m.isAlive() && !(m instanceof Creeper && distanceToSqr(m) > 36))) {
				if (!hasLineOfSight(m)) continue;
				LivingEntity on = m.getTarget();
				// someone in danger counts first: a monster on a player or on one of us is as good as twelve blocks closer
				double score = distanceToSqr(m) - (on instanceof Player || on instanceof Adventurer ? 144 : 0);
				if (score < bestScore) {
					bestScore = score;
					best = m;
				}
			}
			return best;
		}
	}

	// ---------------------------------------------------------------- fighting

	/** Melee: their own side of the target, so a party spreads round it instead of piling into one spot. */
	final class Surround extends Goal {
		Surround() {
			setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
		}

		@Override
		public boolean requiresUpdateEveryTick() {
			return true;
		}

		@Override
		public boolean canUse() {
			return getTarget() != null && getTarget().isAlive();
		}

		@Override
		public void tick() {
			LivingEntity t = getTarget();
			if (t == null) return;
			getLookControl().setLookAt(t, 30, 30);
			if (tickCount % 5 != 0) return;
			Vec3 spot = spot(t);
			if (spot.distanceToSqr(position()) < 1.2) getNavigation().stop();
			else getNavigation().moveTo(spot.x, spot.y, spot.z, distanceToSqr(t) > 64 ? 1.25 : 1.0);
		}

		/** Their place round the target: the front for whoever leads in, the rest out to its sides, then behind it. */
		private Vec3 spot(LivingEntity t) {
			List<Adventurer> ring = new ArrayList<>();
			ring.add(Adventurer.this);
			for (Adventurer a : mates()) if (a.melee() && a.getTarget() == t) ring.add(a);
			ring.sort(Comparator.comparingInt((Adventurer a) -> a.role().equals("tank") ? 0 : 1).thenComparingInt(a -> a.slot));
			int i = ring.indexOf(Adventurer.this);
			double[] around = {0, 70, -70, 140, -140, 180};
			Vec3 front = position().subtract(t.position());
			Player p = level().getNearestPlayer(t, 24);
			if (p != null) front = p.position().subtract(t.position());   // the front faces the players
			front = new Vec3(front.x, 0, front.z);
			if (front.lengthSqr() < 1e-4) front = new Vec3(1, 0, 0);
			front = front.normalize().yRot((float) Math.toRadians(around[Math.min(i, around.length - 1)]));
			double d = t.getBbWidth() / 2 + MobMoves.reach(fights) * 0.7;
			return t.position().add(front.scale(d));
		}
	}

	/** Archers and mages: keep 8 to 14 blocks off, closer if they can't see it; mages cast, archers shoot (RangedBowAttackGoal). */
	final class Cast extends Goal {
		int t, backedOff = -999;

		Cast() {
			setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
		}

		@Override
		public boolean requiresUpdateEveryTick() {
			return true;
		}

		@Override
		public boolean canUse() {
			return getTarget() != null && getTarget().isAlive() || fights.equals("white") && hurtFriend() != null;
		}

		@Override
		public void tick() {
			t++;
			LivingEntity target = getTarget();
			if (fights.equals("white")) {
				LivingEntity friend = hurtFriend();
				if (friend != null && t % 40 == 0) mend(friend);
			}
			if (target == null) return;
			getLookControl().setLookAt(target, 30, 30);
			double d = distanceTo(target);
			boolean sees = hasLineOfSight(target);
			if (tickCount % 10 == 0) {
				if (d < 5 && tickCount - backedOff > 60) {
					// too close: back off once, behind whoever's holding the front if there is one, then stand and cast
					backedOff = tickCount;
					Adventurer front = mates().stream().filter(Adventurer::melee).min(Comparator.comparingDouble(m -> m.distanceToSqr(Adventurer.this))).orElse(null);
					Vec3 from = front != null ? front.position() : position();
					Vec3 away = from.subtract(target.position()).multiply(1, 0, 1).normalize().scale(front != null ? 4 : 5).add(from);
					getNavigation().moveTo(away.x, away.y, away.z, 1.15);
				} else if (d > 15 || !sees) getNavigation().moveTo(target, 1.0);
				else if (d >= 5) getNavigation().stop();
			}
			if (sees && d < 18 && t % (fights.equals("black") ? 45 : 75) == 0) bolt(target);
		}
	}

	/** Who near needs healing most: a party mate or a player under 70%, the lowest first. */
	@Nullable
	LivingEntity hurtFriend() {
		if (!(level() instanceof ServerLevel l)) return null;
		return l.getEntitiesOfClass(LivingEntity.class, getBoundingBox().inflate(14), e -> (e instanceof Player p && !p.isSpectator() || e instanceof Adventurer a && a.party.equals(party))
				&& e.isAlive() && e.getHealth() < e.getMaxHealth() * 0.7f).stream().min(Comparator.comparingDouble(e -> e.getHealth() / e.getMaxHealth())).orElse(null);
	}

	private void mend(LivingEntity who) {
		ServerLevel l = (ServerLevel) level();
		MobSkills.anim(this, yesman.epicfight.gameasset.Animations.BIPED_MOB_THROW);
		who.heal(who.getMaxHealth() * 0.18f);
		if (getRandom().nextFloat() < 0.35f) bark("heal", who instanceof Player pl ? pl : null, Map.of("who", who.getName().getString()), false);
		Spells.skillFx(l, "mob_heal:" + gate, position(), Vec3.ZERO, 0, this);
		Spells.skillFx(l, "mob_healed:" + gate, who.position(), Vec3.ZERO, 0, who);
		l.playSound(null, getX(), getY(), getZ(), SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.NEUTRAL, 1f, 1.2f);
	}

	private void bolt(LivingEntity target) {
		ServerLevel l = (ServerLevel) level();
		MobSkills.anim(this, yesman.epicfight.gameasset.Animations.BIPED_MOB_THROW);
		MobBolt b = new MobBolt(MobBolt.TYPE.get(), l);
		b.setOwner(this);
		Vec3 from = getEyePosition();
		// a bolt flies straight at 0.9 a tick: aim where a moving target will be when it gets there
		Vec3 aim = target.getEyePosition().subtract(0, 0.4, 0), step = new Vec3(target.getX() - target.xo, 0, target.getZ() - target.zo);
		for (int k = 0; k < 2; k++) aim = target.getEyePosition().subtract(0, 0.4, 0).add(step.scale(aim.distanceTo(from) / 0.9));
		Vec3 dir = aim.subtract(from).normalize();
		b.setPos(from.x, from.y, from.z);
		b.setDeltaMovement(dir.scale(0.9));
		b.damage = Adventurers.boltDamage(this);
		b.setGate(gate);
		l.addFreshEntity(b);
		l.playSound(null, getX(), getY(), getZ(), SoundEvents.BLAZE_SHOOT, SoundSource.NEUTRAL, 0.6f, 1.3f);
	}

	@Override
	public void performRangedAttack(LivingEntity target, float pull) {
		ItemStack bow = getMainHandItem();
		ItemStack arrow = new ItemStack(Items.ARROW);
		AbstractArrow a = ProjectileUtil.getMobArrow(this, arrow, pull, bow);
		a.setBaseDamage(Adventurers.arrowDamage(this));
		double dx = target.getX() - getX(), dy = target.getY(0.33) - a.getY(), dz = target.getZ() - getZ();
		a.shoot(dx, dy + Math.sqrt(dx * dx + dz * dz) * 0.2, dz, 1.7f, 4);
		a.pickup = AbstractArrow.Pickup.DISALLOWED;
		playSound(SoundEvents.SKELETON_SHOOT, 1f, 1f / (getRandom().nextFloat() * 0.4f + 0.8f));
		level().addFreshEntity(a);
	}

	// ---------------------------------------------------------------- life

	@Override
	public void aiStep() {
		super.aiStep();
		if (level().isClientSide || fallen() > 0) return;
		calm = getTarget() == null ? calm + 1 : 0;
		talk();
		if (tickCount % 20 == 0) leads = leader() == null;
		// a camp breaks at sunup, a stop at a gate when they've seen enough of it; then on they go
		if (leads && tickCount % 100 == 0 && mode.equals("camp") && level().isDay()) breakCamp();
		if (stay > 0 && --stay == 0 && mode.equals("post")) mode = "roam";
		if (role().equals("tank") && tickCount % 40 == 0) guard();
		if (!wounded && calm > 100 && tickCount % 20 == 0 && getHealth() < getMaxHealth()) heal(getMaxHealth() * 0.02f);
		// nobody near for half a minute: gone, as if they'd walked on
		alone = level().getNearestPlayer(this, Adventurers.STAY) == null ? alone + 1 : 0;
		if (alone > 600) discard();
	}

	/** The shieldbearer's job: monsters close by that are on a mage, an archer or a player turn to them instead, now and then. */
	private void guard() {
		if (!(level() instanceof ServerLevel l)) return;
		boolean called = false;
		for (Mob m : l.getEntitiesOfClass(Mob.class, getBoundingBox().inflate(8), m -> m instanceof Enemy && m.isAlive() && m.getTarget() != null && m.getTarget() != this)) {
			LivingEntity on = m.getTarget();
			boolean soft = on instanceof Player || on instanceof Adventurer a && a.party.equals(party) && !a.role().equals("tank");
			if (soft && getRandom().nextFloat() < 0.6f) {
				m.setTarget(this);
				called = true;
			}
		}
		if (called) l.playSound(null, getX(), getY(), getZ(), SoundEvents.SHIELD_BLOCK, SoundSource.NEUTRAL, 0.8f, 0.8f);
	}

	void breakCamp() {
		if (home != null && level().getBlockState(home).is(Blocks.CAMPFIRE)) level().removeBlock(home, false);
		for (Adventurer a : mates()) {
			a.mode = "roam";
			a.home = null;
		}
		mode = "roam";
		home = null;
	}

	/** The last of a camp to go puts its fire out (not when they die: a cold camp with nobody at it tells its own story). */
	@Override
	public void remove(RemovalReason why) {
		if (why == RemovalReason.DISCARDED && mode.equals("camp") && home != null && mates().isEmpty() && level().getBlockState(home).is(Blocks.CAMPFIRE))
			level().removeBlock(home, false);
		super.remove(why);
	}

	// ---------------------------------------------------------------- what they say

	/** One of their lines (AdventurerTalk) over their head, if anyone's near enough to hear it. Only one of a party talks at a
	 * time, and each waits a while before speaking again, unless `now` (an answer, a cry when hurt). */
	void bark(String key, @Nullable Player to, Map<String, String> more, boolean now) {
		if (!(level() instanceof ServerLevel l) || l.getNearestPlayer(this, HEAR) == null) return;
		long t = l.getGameTime();
		List<Adventurer> mates = mates();
		if (!now && (t < nextBark || mates.stream().anyMatch(m -> m.barkUntil > t - 20))) return;
		String s = AdventurerTalk.line(key, this, to, more, getRandom());
		if (s.isEmpty()) return;
		entityData.set(BARK, s);
		barkUntil = t + BARK_TICKS;
		nextBark = t + 400 + getRandom().nextInt(400);
		for (Adventurer m : mates) m.nextBark = Math.max(m.nextBark, t + 240 + getRandom().nextInt(300));
	}

	/** When to say what: going in, coming out (thanks if someone helped), crying out when hurt, nodding to a player, and small talk. */
	private void talk() {
		long t = level().getGameTime();
		if (barkUntil != 0 && t >= barkUntil) {
			entityData.set(BARK, "");
			barkUntil = 0;
		}
		if (hold > 0) {
			hold--;
			Player p = heldBy == null ? null : level().getPlayerByUUID(heldBy);
			if (p != null) getLookControl().setLookAt(p, 30, 30);
		}
		LivingEntity target = getTarget();
		if (target != null && !fighting) {
			fighting = true;
			boolean tank = role().equals("tank");
			if (getRandom().nextFloat() < (tank ? 0.6f : 0.25f)) bark(tank ? "taunt" : "fight", null, Map.of(), false);
		} else if (target == null && fighting && calm > 40) {
			fighting = false;
			Player h = helper == null ? null : level().getPlayerByUUID(helper);
			if (h != null && distanceTo(h) < 32) {
				owed.add(h.getUUID());
				if (leads) bark("thanks", h, Map.of(), true);
			} else if (leads && getRandom().nextFloat() < 0.5f) bark("won", null, Map.of(), false);
			helper = null;
		}
		if (target != null && getHealth() < getMaxHealth() * 0.35f && t - hurtBark > 300) {
			hurtBark = t;
			bark("hurt", null, Map.of(), true);
		}
		if (tickCount % 20 != 0 || !(level() instanceof ServerLevel)) return;
		if (level().getNearestPlayer(this, 10) instanceof ServerPlayer sp && !seen.contains(sp.getUUID()) && hasLineOfSight(sp)) {
			// one of them nods: the rest have seen you too
			seen.add(sp.getUUID());
			for (Adventurer m : mates()) m.seen.add(sp.getUUID());
			if (target == null && hold <= 0) bark(AdventurerTalk.seeing(this, sp), sp, Map.of(), true);
		}
		if (calm > 200 && hold <= 0 && getRandom().nextFloat() < 0.25f) {
			String key = mode.equals("camp") ? "camp_" + AdventurerTalk.tier(this) : mode.equals("post") && stay < 0 ? "town" : "walk_" + AdventurerTalk.tier(this);
			bark(key, null, Map.of(), false);
		}
	}

	/** They owe this player for a fight. */
	boolean owes(Player p) {
		return owed.contains(p.getUUID());
	}

	/** Stop and hear someone out. */
	void hold(Player p) {
		hold = 200;
		heldBy = p.getUUID();
		getNavigation().stop();
	}

	@Override
	protected InteractionResult mobInteract(Player player, InteractionHand hand) {
		if (hand != InteractionHand.MAIN_HAND) return InteractionResult.PASS;
		if (player instanceof ServerPlayer sp) AdventurerTalk.open(sp, this);
		return InteractionResult.sidedSuccess(level().isClientSide());
	}

	@Override
	public boolean isAlliedTo(Entity e) {
		if (duel != null && e.getUUID().equals(duel)) return false;
		return e instanceof Adventurer || e instanceof Player || super.isAlliedTo(e);
	}

	@Override
	public boolean removeWhenFarAway(double dist) {
		return false;
	}

	@Override
	public void die(DamageSource cause) {
		super.die(cause);
		mates().stream().filter(m -> m.distanceToSqr(this) < 24 * 24).findAny()
				.ifPresent(m -> m.bark("mate_down", null, Map.of("who", getName().getString()), true));
		if (level() instanceof ServerLevel l)
			for (Player p : l.players())
				if (p.distanceToSqr(this) < 48 * 48)
					p.displayClientMessage(Component.literal(getName().getString() + " of " + partyName + " has fallen").withStyle(net.minecraft.ChatFormatting.RED), false);
	}

	@Override
	public void addAdditionalSaveData(CompoundTag out) {
		super.addAdditionalSaveData(out);
		out.putString("kind", kindId());
		out.putString("role", role());
		out.putString("rank", rank());
		out.putUUID("party", party);
		out.putInt("slot", slot);
		out.putString("party_name", partyName);
		out.putString("fights", fights);
		out.putString("gate", gate);
		out.putString("mode", mode);
		out.putInt("stay", stay);
		if (home != null) out.put("home", NbtUtils.writeBlockPos(home));
		out.putString("ask", ask);
		if (task != null) out.put("task", NbtUtils.writeBlockPos(task));
	}

	@Override
	public void readAdditionalSaveData(CompoundTag in) {
		super.readAdditionalSaveData(in);
		setUp(in.getString("kind"), in.getString("role"), in.getString("rank"));
		if (in.hasUUID("party")) party = in.getUUID("party");
		slot = in.getInt("slot");
		leads = slot == 0;
		partyName = in.getString("party_name");
		fights = in.getString("fights").isEmpty() ? "sword" : in.getString("fights");
		gate = in.getString("gate").isEmpty() ? "cellar" : in.getString("gate");
		mode = in.getString("mode").isEmpty() ? "roam" : in.getString("mode");
		stay = in.contains("stay") ? in.getInt("stay") : -1;
		home = NbtUtils.readBlockPos(in, "home").orElse(null);
		ask = in.getString("ask");
		task = NbtUtils.readBlockPos(in, "task").orElse(null);
	}
}
