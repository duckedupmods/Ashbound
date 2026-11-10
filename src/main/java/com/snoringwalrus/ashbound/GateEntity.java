package com.snoringwalrus.ashbound;

import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Consumer;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.nbt.Tag;
import net.minecraft.tags.BlockTags;
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
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * A gate: a crack torn in the air, the dungeon behind it bleeding onto the ground round its foot (bleed), its first
 * hall seen through it and the world seen back through a way out (client/GateWindow).
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
	public static final float RX = 3.0f, RY = 4.9f, MID = 5.0f;
	/** How much wider the tear is drawn than its outline in client/GateRift (so you can see through it). */
	public static final float WIDE = 2.0f;
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
	private static final EntityDataAccessor<Boolean> OUT = SynchedEntityData.defineId(GateEntity.class, EntityDataSerializers.BOOLEAN);

	/** The client's side: its sparks and flashes (GateFx sets it). */
	public static Consumer<GateEntity> clientTick = g -> {};

	private int stage;
	private int pushed;
	private BlockPos lamp;
	/** The blocks its ground took (bleed): what each was, and what it put there; put back when it's gone. */
	private final Map<Long, BlockState> was = new LinkedHashMap<>(), now = new HashMap<>();

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
		b.define(OUT, false);
	}

	/** One that only this client sees, tearing open now (IntroScene): it's never added on the server, so nothing's behind it. */
	public static GateEntity vision(Level level, Vec3 at, float yaw, int rank) {
		GateEntity g = Gates.GATE.get().create(level);
		if (g == null) return null;
		g.moveTo(at.x, at.y, at.z, yaw, 0);
		g.setRank(rank);
		g.opened(level.getGameTime());
		return g;
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

	public void opened(long when) {
		entityData.set(OPENED, when);
	}

	/** A way out, standing inside a dungeon: it never closes by itself, and walking into it takes you home (the client
	 *  shows the world you came from through it). */
	public void makeWayOut() {
		entityData.set(OUT, true);
	}

	public boolean wayOut() {
		return entityData.get(OUT);
	}

	/** Cleared (or its time's up): it starts closing. */
	public void close() {
		if (!closing()) entityData.set(CLOSED, level().getGameTime());
	}

	/** One torn open in the sky (SkyCrack): drawn the same, but what it does is SkyCracks'. */
	public boolean sky() {
		return false;
	}

	@Override
	public void tick() {
		super.tick();
		if (sky()) {
			if (level().isClientSide) clientTick.accept(this);
			else SkyCracks.tick((SkyCrack) this);
			return;
		}
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
			if (age > LIFE && !wayOut()) close();
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
		if (!level().isClientSide && why.shouldDestroy()) {
			unlight();
			restore((ServerLevel) level());
		}
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
		Set<Long> kept = wayOut() ? Set.of() : bleed(level);
		scorch(level, kept);
		light(level);
	}

	// ---------------------------------------------------------------- the ground it breaks

	/** What a dungeon bleeds onto the ground: its floor blocks (weighted as they lie round its arrival point), a stair
	 *  of its own for the buckled edges (or none), and whether it's wet. */
	private record Floor(BlockState[] blocks, BlockState stair, boolean wet) {}

	private static final Map<String, Floor> FLOORS = new ConcurrentHashMap<>();

	private static Floor floor(String lair, BlockState[] debris) {
		if (lair == null) return new Floor(debris, null, false);
		return FLOORS.computeIfAbsent(lair, k -> {
			Vec3 tp = Lairs.points(k).getOrDefault("tp", Vec3.ZERO);
			int fy = Mth.floor(tp.y) - 1, tx = Mth.floor(tp.x), tz = Mth.floor(tp.z);
			java.util.List<BlockState> under = new java.util.ArrayList<>();
			BlockState[] stair = {null};
			boolean[] wet = {false};
			Lairs.blocks(k, (x, y, z, st) -> {
				if (st.getBlock() instanceof StairBlock && stair[0] == null) stair[0] = st.getBlock().defaultBlockState();
				if (st.is(Blocks.WATER)) wet[0] = true;
				if (y == fy && Math.abs(x - tx) <= 7 && z <= tz + 1 && z >= tz - 14 && !st.hasBlockEntity()
						&& st.isCollisionShapeFullBlock(net.minecraft.world.level.EmptyBlockGetter.INSTANCE, BlockPos.ZERO))
					under.add(st);
			});
			return new Floor(under.isEmpty() ? debris : under.toArray(new BlockState[0]), stair[0], wet[0]);
		});
	}

	private static boolean natural(BlockState s) {
		return s.is(BlockTags.DIRT) || s.is(BlockTags.SAND) || s.is(BlockTags.BASE_STONE_OVERWORLD) || s.is(Blocks.GRAVEL)
				|| s.is(Blocks.SNOW_BLOCK) || s.is(Blocks.MUD) || s.is(Blocks.CLAY) || s.is(Blocks.DIRT_PATH);
	}

	private static float hash(long seed, int i) {
		long h = seed * 6364136223846793005L + i * 1442695040888963407L;
		h ^= h >>> 33;
		h *= 0xff51afd7ed558ccdL;
		h ^= h >>> 33;
		return (h & 0xFFFFFF) / (float) 0x1000000;
	}

	/** Changes one block, remembering what was there (never one holding a block entity). */
	private void set(ServerLevel level, BlockPos p, BlockState s) {
		if (level.getBlockEntity(p) != null) return;
		long k = p.asLong();
		was.putIfAbsent(k, level.getBlockState(p));
		now.put(k, s);
		level.setBlock(p, s, 3);
	}

	/** Gone: its ground goes back as it was, where nobody has changed it since (its fissure's char counts as its own). */
	private void restore(ServerLevel level) {
		for (var e : was.entrySet()) {
			BlockPos p = BlockPos.of(e.getKey());
			if (!level.isLoaded(p)) continue;
			BlockState here = level.getBlockState(p), mine = now.get(e.getKey());
			if (here == mine || here.is(Gates.SCORCH.get()) || here.isAir() && mine != null && !mine.isAir()) level.setBlock(p, e.getValue(), 3);
		}
		was.clear();
		now.clear();
	}

	/**
	 * The dungeon bleeding through round its foot (the look of tools/gate_window.py): its own floor in a ragged patch under
	 * the tear, a fissure across its foot burning in the rank colour, the floor buckled up along it, its water seeping out
	 * in puddles if it's a wet one, and a trodden path off its face. Natural ground only, never anything built.
	 * Returns the columns it took, which the char then leaves alone.
	 */
	private Set<Long> bleed(ServerLevel level) {
		GateDungeons.Dungeon dg = GateDungeons.of(this);
		Floor fl = floor(dg.lair(), dg.debris());
		long seed = getUUID().getMostSignificantBits();
		Vec3 f = facing();
		double fx = f.x, fz = f.z, rx = -fz, rz = fx;
		BlockPos foot = blockPosition();
		Set<Long> took = new HashSet<>();
		java.util.List<BlockPos> puddles = new java.util.ArrayList<>();
		BlockState burnt = Gates.SCORCH.get().defaultBlockState().setValue(GateScorch.RANK, rank());
		for (int dx = -15; dx <= 15; dx++)
			for (int dz = -15; dz <= 15; dz++) {
				double a = dx * rx + dz * rz, b = dx * fx + dz * fz;          // across its face, and out of it
				if (Math.abs(a) > 10 || b < -9 || b > 15) continue;
				int x = foot.getX() + dx, z = foot.getZ() + dz;
				int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z) - 1;
				if (Math.abs(y - (foot.getY() - 1)) > 2) continue;
				BlockPos at = new BlockPos(x, y, z), up = at.above();
				BlockState ground = level.getBlockState(at), above = level.getBlockState(up);
				if (!natural(ground) || !(above.isAir() || above.canBeReplaced()) || !above.getFluidState().isEmpty()) continue;
				int i = (dx + 16) * 40 + dz + 16;
				// the fissure: a jagged line across its foot
				double crack = 1.1 * Math.sin(a * 0.9 + hash(seed, 1) * 6) * hash(seed, 2) + 0.6 * Math.sin(a * 2.3 + hash(seed, 3) * 6);
				double off = b - crack;
				boolean inFissure = Math.abs(a) <= 7.5 && Math.abs(off) < 0.55;
				double ang = Math.atan2(b, a);
				double rr = 4.2 + 1.2 * Math.sin(ang * 3 + hash(seed, 4) * 6) + 0.7 * Math.sin(ang * 7 + hash(seed, 5) * 6) + (hash(seed, 100 + i) - 0.5) * 0.8;
				boolean apron = Math.hypot(a * 0.85, b * 1.15) < rr;
				double wob = 1.2 * Math.sin(b * 0.35 + hash(seed, 6) * 6);
				boolean path = b >= 2 && b <= 14 && Math.abs(a - wob) < 1.1 + (hash(seed, 200 + i) - 0.5) * 0.6;
				boolean pathEdge = !path && b >= 2 && b <= 14 && Math.abs(a - wob) < 2.0;
				if (!inFissure && !apron && !path && !(pathEdge && hash(seed, 300 + i) < 0.5)) continue;
				long col = BlockPos.asLong(x, 0, z);
				if (inFissure) {
					// dug a block deep, its floor burning
					BlockPos below = at.below();
					if (!level.getBlockState(below).isFaceSturdy(level, below, Direction.UP)) continue;
					if (!above.isAir()) set(level, up, Blocks.AIR.defaultBlockState());
					set(level, at, burnt);
					took.add(col);
					continue;
				}
				if (apron) {
					if (!above.isAir()) set(level, up, Blocks.AIR.defaultBlockState());
					set(level, at, fl.blocks()[(int) (hash(seed, 400 + i) * fl.blocks().length)]);
					took.add(col);
					// buckled up toward the crack, in runs with gaps
					if (Math.abs(off) < 1.6 && hash(seed, 500 + i) < 0.45) {
						double sg = -Math.signum(off);
						Direction toCrack = Direction.getNearest(fx * sg, 0, fz * sg);
						if (fl.stair() != null) set(level, up, fl.stair().setValue(StairBlock.FACING, toCrack));
						else if (hash(seed, 600 + i) < 0.5) set(level, up, fl.blocks()[(int) (hash(seed, 700 + i) * fl.blocks().length)]);
					} else if (fl.wet() && hash(seed, 800 + i) < 0.08) puddles.add(at);
					continue;
				}
				if (ground.is(BlockTags.DIRT) || ground.is(Blocks.DIRT_PATH)) {
					if (!above.isAir()) set(level, up, Blocks.AIR.defaultBlockState());
					set(level, at, path && hash(seed, 900 + i) < 0.85 ? Blocks.DIRT_PATH.defaultBlockState() : Blocks.COARSE_DIRT.defaultBlockState());
					took.add(col);
				}
			}
		// the dungeon's water seeping up, only where it's held in on every side
		for (BlockPos at : puddles) {
			boolean held = level.getBlockState(at.below()).isFaceSturdy(level, at.below(), Direction.UP);
			for (Direction d : Direction.Plane.HORIZONTAL) held &= level.getBlockState(at.relative(d)).isFaceSturdy(level, at.relative(d), d.getOpposite());
			if (held && level.getBlockState(at.above()).isAir()) set(level, at, Blocks.WATER.defaultBlockState());
		}
		return took;
	}

	private void scorch(ServerLevel level, Set<Long> kept) {
		scorch(level, getX(), getZ(), Mth.floor(getY()), rank(), 6.5, kept);
	}

	/** A patch of char round (x, z) on the ground near height foot, about radius across (a storm's lightning strike). */
	static void scorchPatch(ServerLevel level, double x, double z, int foot, int rank, double radius) {
		scorch(level, x, z, foot, rank, radius, Set.of());
	}

	private static void scorch(ServerLevel level, double cx, double cz, int foot, int rank, double radius, Set<Long> kept) {
		BlockState burnt = Gates.SCORCH.get().defaultBlockState().setValue(GateScorch.RANK, rank);
		var r = level.random;
		int reach = (int) Math.ceil(radius);
		for (int dx = -reach; dx <= reach; dx++)
			for (int dz = -reach; dz <= reach; dz++) {
				double d = Math.sqrt(dx * dx + dz * dz) + r.nextDouble() * radius * 0.34;
				if (d > radius) continue;
				int x = Mth.floor(cx) + dx, z = Mth.floor(cz) + dz;
				if (kept.contains(BlockPos.asLong(x, 0, z))) continue;
				int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
				if (Math.abs(y - foot) > 3) continue;
				BlockPos at = new BlockPos(x, y, z);
				BlockState here = level.getBlockState(at);
				if (!(here.isAir() || here.canBeReplaced()) || !here.getFluidState().isEmpty()) continue;
				if (!burnt.canSurvive(level, at)) continue;
				level.setBlock(at, burnt, 3);
				for (Direction way : Direction.Plane.HORIZONTAL) {
					charUp(level, at, way, burnt);
					charDown(level, at, way, burnt);
				}
			}
	}

	/** The char on a face: the cell in front of it takes that side. */
	private static void burn(ServerLevel level, BlockPos cell, Direction way, BlockState burnt) {
		BlockState there = level.getBlockState(cell);
		BlockState s = there.is(burnt.getBlock()) ? there : !there.isAir() && !there.canBeReplaced() || !there.getFluidState().isEmpty() ? null
				: burnt.setValue(GateScorch.FLOOR, false);
		if (s != null && GateScorch.holds(level, cell, way)) level.setBlock(cell, s.setValue(GateScorch.side(way), true), 3);
	}

	/** Ground rising beside the burnt patch: up its face. */
	private static void charUp(ServerLevel level, BlockPos at, Direction way, BlockState burnt) {
		for (int up = 0; up < GateScorch.CLIMB; up++) {
			BlockPos cell = at.above(up);
			if (!GateScorch.holds(level, cell, way)) return;
			burn(level, cell, way, burnt);
		}
	}

	/** Ground dropping away beside it: down the bank, from the air in front of it. */
	private static void charDown(ServerLevel level, BlockPos at, Direction way, BlockState burnt) {
		for (int down = 1; down <= GateScorch.CLIMB; down++) {
			BlockPos cell = at.below(down).relative(way);
			if (!GateScorch.holds(level, cell, way.getOpposite())) return;
			burn(level, cell, way.getOpposite(), burnt);
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
			if (wayOut()) {
				if (!BossArenas.through(this, p)) Lairs.leave(p);   // the way home (a boss arena's door, or a dungeon's way out)
				continue;
			}
			String lair = GateDungeons.of(this).lair();
			if (lair != null) {
				Lairs.enter(p, lair, this);                          // there's a dungeon behind it: in you go
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
		entityData.set(OUT, tag.getBoolean("out"));
		was.clear();
		now.clear();
		var blocks = level().holderLookup(Registries.BLOCK);
		for (Tag t : tag.getList("ground", Tag.TAG_COMPOUND)) {
			CompoundTag c = (CompoundTag) t;
			was.put(c.getLong("p"), NbtUtils.readBlockState(blocks, c.getCompound("was")));
			now.put(c.getLong("p"), NbtUtils.readBlockState(blocks, c.getCompound("now")));
		}
	}

	@Override
	protected void addAdditionalSaveData(CompoundTag tag) {
		tag.putInt("rank", rank());
		tag.putLong("opened", opened());
		if (closing()) tag.putLong("closed", closed());
		if (lamp != null) tag.putLong("lamp", lamp.asLong());
		if (wayOut()) tag.putBoolean("out", true);
		if (!was.isEmpty()) {
			ListTag l = new ListTag();
			for (var e : was.entrySet()) {
				CompoundTag c = new CompoundTag();
				c.putLong("p", e.getKey());
				c.put("was", NbtUtils.writeBlockState(e.getValue()));
				c.put("now", NbtUtils.writeBlockState(now.getOrDefault(e.getKey(), Blocks.AIR.defaultBlockState())));
				l.add(c);
			}
			tag.put("ground", l);
		}
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
