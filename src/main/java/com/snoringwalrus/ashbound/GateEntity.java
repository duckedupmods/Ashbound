package com.snoringwalrus.ashbound;

import java.util.function.Consumer;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LightBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * A gate: an oval torn in the air, hanging over a scorched patch of ground, a beam over it to the clouds.
 * Its colour is the only clue to how deadly the dungeon behind it is (COLOUR, F to SSS); nothing ever names it.
 *
 * Its life, in game ticks: a hairline of light tears down the air, cracks running off it (0..CRACK); it bursts
 * open with a flash and a shockwave and swells to full size (CRACK..CRACK+OPEN), the beam punching up out of its
 * top; it stands (until LIFE, or until it's cleared), then closes: burns hotter, drags its rocks in and squeezes
 * shut sideways like an eye (0..SHUT), collapses to a star and bangs (BANG), the beam drains away, gone (GONE).
 * While open, an invisible light block at its heart lights the ground round it.
 * The server keeps the time each began; the client (GateRenderer, GateFx) draws every frame of it from those.
 */
public class GateEntity extends Entity {
	/** Half the tear's width (at its widest, roughly) and height, and how high its middle hangs over its foot (blocks;
	 *  the tear's real outline is client/GateRift). */
	public static final float RX = 1.5f, RY = 4.9f, MID = 5.0f;
	/** Opening: a hairline cracks (0..CRACK), tears open (..+OPEN). Closing: its lips pull shut by SHUT, bang at BANG. */
	public static final int CRACK = 30, OPEN = 16, SHUT = 44, BANG = 52, GONE = 100;
	/** Two Minecraft days, then it closes by itself (later: it breaks, and what's inside comes out). */
	public static final long LIFE = 48000;

	/** F E D C B A S SS SSS. From S up the hole is black and the colour is only its rim. */
	public static final int[] COLOUR = {0xCDD2DC, 0x46E678, 0x3C8CFF, 0xA55AFF, 0xFFA01E, 0xFF2D2D, 0xFF1E1E, 0xBE46FF, 0xFFECBE};
	public static final String[] RANKS = {"F", "E", "D", "C", "B", "A", "S", "SS", "SSS"};

	public static boolean dark(int rank) {
		return rank >= 6;
	}

	public static boolean lightning(int rank) {
		return rank >= 7;
	}

	public static boolean bleeds(int rank) {
		return rank == 8;
	}

	private static final EntityDataAccessor<Integer> RANK = SynchedEntityData.defineId(GateEntity.class, EntityDataSerializers.INT);
	private static final EntityDataAccessor<Long> OPENED = SynchedEntityData.defineId(GateEntity.class, EntityDataSerializers.LONG);
	private static final EntityDataAccessor<Long> CLOSED = SynchedEntityData.defineId(GateEntity.class, EntityDataSerializers.LONG);

	/** The client's side: its sparks and flashes (GateFx sets it). */
	public static Consumer<GateEntity> clientTick = g -> {};

	private int stage;
	private int pushed;
	private BlockPos lamp;
	/** A way out, standing inside a dungeon: it never closes by itself, and walking into it takes you home. */
	private boolean out;

	public GateEntity(EntityType<? extends GateEntity> type, Level level) {
		super(type, level);
		noPhysics = true;
		setNoGravity(true);
	}

	@Override
	protected void defineSynchedData(SynchedEntityData.Builder b) {
		b.define(RANK, 0);
		b.define(OPENED, 0L);
		b.define(CLOSED, -1L);
	}

	public int rank() {
		return entityData.get(RANK);
	}

	public void setRank(int r) {
		entityData.set(RANK, Mth.clamp(r, 0, 8));
	}

	public long opened() {
		return entityData.get(OPENED);
	}

	public long closed() {
		return entityData.get(CLOSED);
	}

	public boolean closing() {
		return closed() >= 0;
	}

	/** Its face looks this way (and the other way: it's the same from both sides). */
	public Vec3 facing() {
		return Vec3.directionFromRotation(0, getYRot());
	}

	public Vec3 middle() {
		return position().add(0, MID, 0);
	}

	void opened(long when) {
		entityData.set(OPENED, when);
	}

	void makeWayOut() {
		out = true;
	}

	public boolean wayOut() {
		return out;
	}

	/** Cleared (or its time's up): it starts closing. */
	public void close() {
		if (!closing()) entityData.set(CLOSED, level().getGameTime());
	}

	@Override
	public void tick() {
		super.tick();
		if (level().isClientSide) {
			clientTick.accept(this);
			return;
		}
		ServerLevel level = (ServerLevel) level();
		long now = level.getGameTime(), age = now - opened();
		if (stage == 0) {
			stage = 1;
			if (age < CRACK) {
				sound(SoundEvents.GLASS_BREAK, 2f, 0.4f);
				sound(SoundEvents.AMETHYST_BLOCK_RESONATE, 3f, 0.5f);
				sound(SoundEvents.LIGHTNING_BOLT_THUNDER, 1.5f, 1.7f);
			}
		}
		if (stage == 1 && age >= CRACK) {
			stage = 2;
			if (age < CRACK + OPEN) shatter(level);
		}
		if (!closing()) {
			if (stage == 2 && age % 90 == 0) {
				sound(SoundEvents.BEACON_AMBIENT, 2.5f, dark(rank()) ? 0.5f : 0.7f);
				sound(SoundEvents.PORTAL_AMBIENT, 1f, 0.5f);
			}
			if (age > LIFE && !out) close();
			if (stage == 2) touch(level);
			return;
		}
		long c = now - closed();
		if (stage == 2) {
			stage = 3;
			sound(SoundEvents.BEACON_DEACTIVATE, 3f, 0.5f);
			sound(SoundEvents.RESPAWN_ANCHOR_DEPLETE.value(), 2f, 0.6f);
		}
		if (stage == 3 && c >= BANG) {
			stage = 4;
			bang(level);
		}
		if (c >= GONE) discard();
	}

	/** Light the ground round it: an invisible light block at its heart, if that's open air. */
	private void light(ServerLevel level) {
		BlockPos at = BlockPos.containing(middle()).below(2);
		if (!level.getBlockState(at).isAir()) return;
		level.setBlock(at, Blocks.LIGHT.defaultBlockState().setValue(LightBlock.LEVEL, 15), 3);
		lamp = at;
	}

	private void unlight() {
		if (lamp != null && level().getBlockState(lamp).is(Blocks.LIGHT)) level().setBlock(lamp, Blocks.AIR.defaultBlockState(), 3);
		lamp = null;
	}

	@Override
	public void remove(RemovalReason why) {
		if (!level().isClientSide && why.shouldDestroy()) unlight();
		super.remove(why);
	}

	private void sound(SoundEvent s, float volume, float pitch) {
		level().playSound(null, getX(), getY() + MID, getZ(), s, SoundSource.AMBIENT, volume, pitch);
	}

	/** It bursts open: the sound of it, the ground under it burnt, its light lit (the sight of it is the client's). */
	private void shatter(ServerLevel level) {
		sound(SoundEvents.GLASS_BREAK, 3f, 0.55f);
		sound(SoundEvents.WARDEN_SONIC_BOOM, 2f, 0.7f);
		sound(SoundEvents.BEACON_ACTIVATE, 3f, 0.5f);
		sound(SoundEvents.ELDER_GUARDIAN_CURSE, 0.6f, 0.5f);
		scorch(level);
		light(level);
	}

	private void scorch(ServerLevel level) {
		BlockState burnt = Gates.SCORCH.get().defaultBlockState().setValue(GateScorch.RANK, rank());
		int foot = Mth.floor(getY());
		var r = level.random;
		for (int dx = -6; dx <= 6; dx++)
			for (int dz = -6; dz <= 6; dz++) {
				double d = Math.sqrt(dx * dx + dz * dz) + r.nextDouble() * 2.2;
				if (d > 6.5) continue;
				int x = Mth.floor(getX()) + dx, z = Mth.floor(getZ()) + dz;
				int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
				if (Math.abs(y - foot) > 3) continue;
				BlockPos at = new BlockPos(x, y, z);
				BlockState here = level.getBlockState(at);
				if (!(here.isAir() || here.canBeReplaced()) || !here.getFluidState().isEmpty()) continue;
				if (!burnt.canSurvive(level, at)) continue;
				level.setBlock(at, burnt, 3);
			}
	}

	/** Shut: a shockwave that throws everything near back (the flash and the rest are drawn by the client). */
	private void bang(ServerLevel level) {
		Vec3 m = middle();
		sound(SoundEvents.WARDEN_SONIC_BOOM, 3f, 0.5f);
		sound(SoundEvents.GENERIC_EXPLODE.value(), 1.5f, 0.6f);
		sound(SoundEvents.AMETHYST_CLUSTER_BREAK, 3f, 0.5f);
		unlight();
		for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, new AABB(m, m).inflate(10))) {
			Vec3 away = e.position().subtract(position()).multiply(1, 0, 1);
			double d = away.length();
			if (d > 10) continue;
			Vec3 push = (d < 0.1 ? facing() : away.scale(1 / d)).scale(1.4 * (1 - d / 10));
			e.push(push.x, 0.35 * (1 - d / 10), push.z);
			e.hurtMarked = true;
		}
	}

	/** Until there's a dungeon behind it: its face throws back whoever walks into it. */
	private void touch(ServerLevel level) {
		if (pushed > 0) pushed--;
		Vec3 m = middle(), f = facing(), side = new Vec3(f.z, 0, -f.x);
		for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, new AABB(m, m).inflate(RX + 1, RY + 1, RX + 1))) {
			Vec3 d = p.position().add(0, p.getBbHeight() / 2, 0).subtract(m);
			double z = d.dot(f), x = d.dot(side), y = d.y;
			if (Math.abs(z) > 0.6 || (x * x) / (RX * RX) + (y * y) / (RY * RY) > 1) continue;
			if (out) {
				Lairs.leave(p);                                      // the way home
				continue;
			}
			String lair = GateDungeons.of(this).lair();
			if (lair != null) {
				Lairs.enter(p, lair);                                // there's a dungeon behind it: in you go
				continue;
			}
			Vec3 back = f.scale(z >= 0 ? 0.9 : -0.9);
			p.push(back.x, 0.25, back.z);
			p.hurtMarked = true;
			if (pushed == 0) {
				pushed = 20;
				sound(SoundEvents.SHULKER_BULLET_HURT, 1.5f, 0.5f);
			}
		}
	}

	@Override
	protected void readAdditionalSaveData(CompoundTag tag) {
		setRank(tag.getInt("rank"));
		entityData.set(OPENED, tag.getLong("opened"));
		entityData.set(CLOSED, tag.contains("closed") ? tag.getLong("closed") : -1L);
		stage = closing() ? 3 : 2;
		if (tag.contains("lamp")) lamp = BlockPos.of(tag.getLong("lamp"));
		out = tag.getBoolean("out");
	}

	@Override
	protected void addAdditionalSaveData(CompoundTag tag) {
		tag.putInt("rank", rank());
		tag.putLong("opened", opened());
		if (closing()) tag.putLong("closed", closed());
		if (lamp != null) tag.putLong("lamp", lamp.asLong());
		if (out) tag.putBoolean("out", true);
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
	public boolean canBeCollidedWith() {
		return false;
	}

	@Override
	public boolean shouldRenderAtSqrDistance(double d) {
		return d < 400 * 400;
	}

	/** The beam reaches the clouds: it's drawn whenever any of it is on screen. */
	@Override
	public AABB getBoundingBoxForCulling() {
		return getBoundingBox().inflate(10, 0, 10).expandTowards(0, 300, 0);
	}
}
