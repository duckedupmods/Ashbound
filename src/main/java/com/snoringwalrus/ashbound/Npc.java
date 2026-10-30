package com.snoringwalrus.ashbound;

import java.util.UUID;
import java.util.function.ToDoubleFunction;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MoveTowardsRestrictionGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;

/**
 * A townsperson you can talk to: who they are (KIND, an id in data/ashbound/npc/, which also names their mesh) is
 * synced and saved, with the shop they keep, the spot they keep to and how they spend their day there (their mode:
 * "stand" at a counter or a post, "stroll" round it, "errand" across a whole quarter, "sit" on the bench or chair
 * they were put on). Between times they chat with whoever's near, take a seat, the children play tag (NpcLife).
 * They can't be hurt or pushed and stop to face whoever talks to them. Epic Fight draws and animates them (NpcPatch)
 * on its biped, each with its own mesh from the NPC forge (tools/efmob.py --npc).
 */
public class Npc extends PathfinderMob {
	private static final EntityDataAccessor<String> KIND = SynchedEntityData.defineId(Npc.class, EntityDataSerializers.STRING);
	/** What their body's doing beyond walking and standing (POSE_*), for Epic Fight to show. */
	private static final EntityDataAccessor<Byte> POSE = SynchedEntityData.defineId(Npc.class, EntityDataSerializers.BYTE);
	public static final byte POSE_NONE = 0, POSE_SIT = 1, POSE_KNEEL = 2, POSE_RUN = 3;

	/** Time spent ticking them, server and client side (nanoseconds, for /ashlag). */
	public static long serverNanos, clientNanos;
	/** Far from everyone they only look up once a second: nobody's there to see them. */
	static final double AWAKE = 64;
	private int dozing;

	/** How big each kind is drawn (client side, from npc_scales.json; 1 on the server). */
	public static ToDoubleFunction<String> SCALE = k -> 1;

	private String shop = "";
	String mode = "stand";
	BlockPos home;
	/** Who they're talking to (server side). */
	UUID talkingTo;
	/** Stands in for who they're talking to while they're at the anvil: busy, to all their other habits. */
	private static final UUID FORGING = new UUID(0, 1);
	private int forging;
	private BlockPos forgingAt;
	/** Who they're chatting with, townsfolk among themselves (server side, NpcLife.Chat). */
	Npc partner;
	/** The seat they're on (NpcLife.Sit), and how high its top is. */
	BlockPos seat;
	double seatTop;
	float seatYaw;
	/** The seat they're making for. */
	BlockPos going;
	/** Who they're playing tag with (children), and whether they're it. */
	Npc playmate;
	boolean it;
	/** Ticks left knelt to their herbs or their beds. */
	int kneeling;

	public Npc(EntityType<? extends Npc> type, Level level) {
		super(type, level);
		setPersistenceRequired();
	}

	public static AttributeSupplier.Builder attributes() {
		return PathfinderMob.createMobAttributes().add(Attributes.MAX_HEALTH, 20).add(Attributes.MOVEMENT_SPEED, 0.5)
				.add(Attributes.FOLLOW_RANGE, 40);
	}

	@Override
	protected void defineSynchedData(SynchedEntityData.Builder b) {
		super.defineSynchedData(b);
		b.define(KIND, "townsfolk_3006");
		b.define(POSE, POSE_NONE);
	}

	@Override
	protected net.minecraft.world.entity.ai.navigation.PathNavigation createNavigation(Level level) {
		return new NpcLife.FloorNav(this, level);
	}

	@Override
	protected void registerGoals() {
		goalSelector.addGoal(0, new FloatGoal(this));
		goalSelector.addGoal(1, new NpcLife.Sit(this));
		goalSelector.addGoal(2, new NpcLife.Chat(this));
		goalSelector.addGoal(3, new NpcLife.Play(this));
		goalSelector.addGoal(4, new MoveTowardsRestrictionGoal(this, 0.55) {
			@Override
			public boolean canUse() {
				return free() && super.canUse();
			}
		});
		goalSelector.addGoal(5, new NpcLife.Wander(this));
		// shopkeepers and the leads keep an eye on whoever comes to their counter; everyone else only glances
		goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 5f, 1f) {
			@Override
			public boolean canUse() {
				return free() && getRandom().nextFloat() < (keepsCounter() ? 0.25f : 0.008f) && super.canUse();
			}
		});
		goalSelector.addGoal(7, new LookAtPlayerGoal(this, Npc.class, 6f, 0.03f) {
			@Override
			public boolean canUse() {
				return free() && super.canUse();
			}
		});
		goalSelector.addGoal(8, new RandomLookAroundGoal(this) {
			@Override
			public boolean canUse() {
				return free() && super.canUse();
			}
		});
	}

	/** Who, what they sell, and how they spend their day round where they've been put. */
	public void setup(String kind, String shopId, String how) {
		setKind(kind);
		shop = shopId == null ? "" : shopId;
		mode = how == null ? "stand" : how;
		home = blockPosition();
		keepHome();
	}

	private void keepHome() {
		if (home != null) restrictTo(home, switch (mode) {
			case "errand" -> 40;
			case "stroll" -> 14;
			case "sit" -> 6;
			default -> 2;
		});
	}

	public String kindId() {
		return entityData.get(KIND);
	}

	public Talk.Kind kind() {
		return Talk.kind(kindId());
	}

	public boolean is(String tag) {
		Talk.Kind k = kind();
		return k != null && k.tags().contains(tag);
	}

	public String shopId() {
		return shop.isEmpty() ? kindId() : shop;
	}

	/** Keeps a counter or is someone you come to see: they mind the people in front of them. */
	boolean keepsCounter() {
		return !shop.isEmpty() || is("lead") || !kindId().contains("_");
	}

	public void setKind(String id) {
		entityData.set(KIND, id);
		Talk.Kind k = Talk.kind(id);
		if (k != null) setCustomName(Component.literal(k.name()));
	}

	public byte act() {
		return entityData.get(POSE);
	}

	void setAct(byte p) {
		entityData.set(POSE, p);
	}

	/** Not busy with you, a friend or a seat. */
	boolean free() {
		return talkingTo == null && partner == null && seat == null && playmate == null && going == null && kneeling == 0;
	}

	void kneel(int ticks) {
		kneeling = ticks;
		setAct(POSE_KNEEL);
	}

	// ---------------------------------------------------------------- talking

	@Override
	protected InteractionResult mobInteract(Player player, InteractionHand hand) {
		if (hand != InteractionHand.MAIN_HAND) return InteractionResult.PASS;
		if (player instanceof ServerPlayer sp) greet(sp);
		return InteractionResult.sidedSuccess(level().isClientSide());
	}

	/** Start a conversation with them (whatever they were chatting about can wait; they keep their seat). */
	public void greet(ServerPlayer sp) {
		if (kind() == null) return;
		if (forging > 0) { // busy at the anvil: you can only lend a hand
			if (forgingAt != null) Smithing.join(sp, forgingAt);
			return;
		}
		NpcLife.Chat.part(this);
		talkingTo = sp.getUUID();
		getNavigation().stop();
		Talk.open(sp, this);
	}

	/** Across the anvil from someone at the forge (Smithing): stood there, watching the work, for a while at most. */
	void forge(net.minecraft.world.phys.Vec3 at, BlockPos anvil, int ticks) {
		NpcLife.Chat.part(this);
		NpcLife.Sit.leave(this);
		getNavigation().stop();
		teleportTo(at.x, at.y, at.z);
		forgingAt = anvil;
		forging = ticks;
		talkingTo = FORGING;
	}

	void doneForging() {
		forging = 0;
		forgingAt = null;
		if (FORGING.equals(talkingTo)) stopTalking();
	}

	/** The conversation's over (closed, or they walked off). */
	void stopTalking() {
		talkingTo = null;
	}

	@Override
	public void tick() {
		long t0 = System.nanoTime();
		if (level().isClientSide()) {
			super.tick();
			clientNanos += System.nanoTime() - t0;
			return;
		}
		if (++dozing % 20 != 0 && talkingTo == null && level().getNearestPlayer(this, AWAKE) == null) {
			serverNanos += System.nanoTime() - t0;
			return;
		}
		super.tick();
		live();
		serverNanos += System.nanoTime() - t0;
	}

	private void live() {
		// one stood there as the world was made ("@townsfolk/smith") before the townsfolk were known: which one
		if (kindId().startsWith("@") && tickCount % 20 == 1) {
			String k = Talk.resolve(kindId(), getRandom());
			if (k == null) k = Talk.resolve("@townsfolk", getRandom());
			if (k != null) setKind(k);
		}
		if (seat != null) NpcLife.Sit.hold(this);
		if (kneeling > 0) {
			getNavigation().stop();
			if (--kneeling == 0 || talkingTo != null) {
				kneeling = 0;
				setAct(POSE_NONE);
			}
		}
		if (forging > 0) {
			getNavigation().stop();
			if (forgingAt != null) getLookControl().setLookAt(forgingAt.getX() + 0.5, forgingAt.getY() + 1, forgingAt.getZ() + 0.5);
			if (--forging == 0) doneForging();
			return;
		}
		if (talkingTo != null) {
			Player p = level().getPlayerByUUID(talkingTo);
			if (p == null || p.distanceTo(this) > 7 || !Talk.talking(p, this)) {
				if (p instanceof ServerPlayer sp && Talk.talking(p, this)) Talk.close(sp);
				stopTalking();
			} else {
				getNavigation().stop();
				getLookControl().setLookAt(p, 30f, 30f);
			}
		}
	}

	/** Going for good or only with their chunk, they let go of their seat. */
	@Override
	public void onRemovedFromLevel() {
		NpcLife.Sit.leave(this);
		super.onRemovedFromLevel();
	}

	@Override
	public void remove(RemovalReason why) {
		NpcLife.Chat.part(this);
		super.remove(why);
	}

	// ---------------------------------------------------------------- not to be harmed or moved

	@Override
	public boolean hurt(DamageSource src, float amount) {
		if (src.isCreativePlayer() || src.is(net.minecraft.tags.DamageTypeTags.BYPASSES_INVULNERABILITY)) return super.hurt(src, amount);
		return false;
	}

	@Override
	public boolean isPushable() {
		return false;
	}

	@Override
	protected void doPush(Entity e) {}

	@Override
	protected void pushEntities() {}

	@Override
	public boolean removeWhenFarAway(double dist) {
		return false;
	}

	@Override
	public void addAdditionalSaveData(CompoundTag out) {
		super.addAdditionalSaveData(out);
		out.putString("kind", kindId());
		out.putString("shop", shop);
		out.putString("mode", mode);
		if (home != null) out.putLong("home", home.asLong());
	}

	@Override
	public void readAdditionalSaveData(CompoundTag in) {
		super.readAdditionalSaveData(in);
		if (in.contains("kind")) entityData.set(KIND, in.getString("kind"));
		shop = in.getString("shop");
		mode = in.contains("mode") ? in.getString("mode") : in.getBoolean("stroll") ? "stroll" : "stand";
		if (in.contains("home")) home = BlockPos.of(in.getLong("home"));
		setNoGravity(false);                             // saved off a seat; they'll take it again
		keepHome();
	}
}
