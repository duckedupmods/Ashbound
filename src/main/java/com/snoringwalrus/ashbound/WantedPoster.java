package com.snoringwalrus.ashbound;

import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.Pose;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.neoforged.neoforge.registries.DeferredHolder;

/**
 * A wanted poster (Bounties): a Legend's portrait on parchment, nailed to a road sign's post or a house wall near a town's
 * middle (client/WantedPosterRenderer). It names one bounty; right-click to take it, or to be paid for one you've slain.
 * It hangs on nothing in the world (no block is changed): its yaw is the way its face looks out.
 */
public class WantedPoster extends Entity {
	static final DeferredHolder<EntityType<?>, EntityType<WantedPoster>> TYPE = Monsters.ENTITIES.register("wanted_poster",
			() -> EntityType.Builder.<WantedPoster>of(WantedPoster::new, MobCategory.MISC).sized(0.9f, 1.25f).fireImmune()
					.clientTrackingRange(10).updateInterval(200).build(Ashbound.ID + ":wanted_poster"));
	/** blocks wide; its height is the texture's 176/128 of that */
	public static final float WIDE = 1.0f, TALL = WIDE * 176 / 128f;

	private static final EntityDataAccessor<String> LEGEND = SynchedEntityData.defineId(WantedPoster.class, EntityDataSerializers.STRING);
	private static final EntityDataAccessor<Integer> RANK = SynchedEntityData.defineId(WantedPoster.class, EntityDataSerializers.INT);
	private static final EntityDataAccessor<Boolean> SLAIN = SynchedEntityData.defineId(WantedPoster.class, EntityDataSerializers.BOOLEAN);
	private static final EntityDataAccessor<Float> SCALE = SynchedEntityData.defineId(WantedPoster.class, EntityDataSerializers.FLOAT);
	/** the bounty it names, so a hunter who's taken it sees it torn down (client) */
	private static final EntityDataAccessor<Integer> BOUNTY = SynchedEntityData.defineId(WantedPoster.class, EntityDataSerializers.INT);

	/** server: the bounty it names (Bounties), the anchor it hangs from */
	int bounty, anchor = -1;

	public WantedPoster(EntityType<? extends WantedPoster> type, Level level) {
		super(type, level);
		noPhysics = true;
	}

	@Override
	protected void defineSynchedData(SynchedEntityData.Builder b) {
		b.define(LEGEND, "rime_penitent");
		b.define(RANK, 0);
		b.define(SLAIN, false);
		b.define(SCALE, 1f);
		b.define(BOUNTY, 0);
	}

	public String legend() {
		return entityData.get(LEGEND);
	}

	public int rank() {
		return entityData.get(RANK);
	}

	public boolean slain() {
		return entityData.get(SLAIN);
	}

	public int bountyId() {
		return entityData.get(BOUNTY);
	}

	public float scale() {
		return entityData.get(SCALE);
	}

	/** the way its face looks out of the wall */
	public Direction facing() {
		return Direction.fromYRot(getYRot());
	}

	void show(String legend, int rank, boolean slain) {
		entityData.set(BOUNTY, bounty);
		entityData.set(LEGEND, legend);
		entityData.set(RANK, rank);
		entityData.set(SLAIN, slain);
	}

	void hangOn(double x, double y, double z, float yaw, float scale) {
		setYRot(yaw);
		entityData.set(SCALE, scale);
		setPos(x, y, z);
	}

	@Override
	protected AABB makeBoundingBox() {
		// flat against its wall: thin across the way it faces, as wide and tall as the paper
		float s = entityData == null ? 1f : scale();
		double w = WIDE * s / 2, h = TALL * s / 2, t = 0.0625;
		Direction f = Direction.fromYRot(getYRot());
		double hx = f.getAxis() == Direction.Axis.X ? t : w, hz = f.getAxis() == Direction.Axis.Z ? t : w;
		return new AABB(getX() - hx, getY() - h, getZ() - hz, getX() + hx, getY() + h, getZ() + hz);
	}

	@Override
	public void onSyncedDataUpdated(EntityDataAccessor<?> key) {
		super.onSyncedDataUpdated(key);
		if (SCALE.equals(key)) setBoundingBox(makeBoundingBox());
	}

	@Override
	public void setYRot(float yaw) {
		super.setYRot(yaw);
		if (entityData != null) setBoundingBox(makeBoundingBox());
	}

	@Override
	public EntityDimensions getDimensions(Pose pose) {
		return EntityDimensions.fixed(WIDE * scale(), TALL * scale());
	}

	@Override
	public void tick() {
		// nailed up: it never moves, and does nothing on its own (Bounties keeps it up to date)
	}

	@Override
	public boolean isPickable() {
		return !isRemoved();
	}

	@Override
	public boolean isPushable() {
		return false;
	}

	@Override
	public boolean hurt(DamageSource src, float amount) {
		return false;   // the guild's; nobody tears it down
	}

	@Override
	public InteractionResult interact(Player p, InteractionHand hand) {
		if (hand != InteractionHand.MAIN_HAND) return InteractionResult.PASS;
		if (p instanceof ServerPlayer sp && level() instanceof ServerLevel l) Bounties.read(l, this, sp);
		return InteractionResult.sidedSuccess(level().isClientSide);
	}

	@Override
	protected void readAdditionalSaveData(CompoundTag t) {
		bounty = t.getInt("bounty");
		anchor = t.contains("anchor") ? t.getInt("anchor") : -1;
		show(t.getString("legend"), t.getInt("rank"), t.getBoolean("slain"));
		entityData.set(SCALE, t.contains("scale") ? t.getFloat("scale") : 1f);
		setBoundingBox(makeBoundingBox());
	}

	@Override
	protected void addAdditionalSaveData(CompoundTag t) {
		t.putInt("bounty", bounty);
		t.putInt("anchor", anchor);
		t.putString("legend", legend());
		t.putInt("rank", rank());
		t.putBoolean("slain", slain());
		t.putFloat("scale", scale());
	}
}
