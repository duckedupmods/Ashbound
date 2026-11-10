package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

import javax.annotation.Nullable;

import net.minecraft.ChatFormatting;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.FloatTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.StandingSignBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.SignBlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.saveddata.SavedData;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.entity.EntityJoinLevelEvent;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;
import net.neoforged.neoforge.event.level.ChunkEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * Legend hunts: the Guild's wanted posters. A poster (WantedPoster) hangs on the post under every road sign (Roads) and on a
 * few house walls round each town's middle; each names a bounty on one Legend, out in its own land 300 to 1000 blocks off,
 * at the rank of whoever first came by. Right-click to take it: it's a favour (Errands) in the Journal and on the compass,
 * pointing at where it was last seen. Nothing's out there till a hunter comes near: the trail first (its tracks on the
 * ground, leading in), then the Legend itself. Slain, every poster of it is stamped SLAIN and anyone who'd taken it is
 * paid at any poster; a few days on, the poster names a new one. Kept in the world's saved data.
 */
final class Bounties {
	private Bounties() {}

	static final String GIVER = "@legend:", TAG = "ashbound_bounty", TRACK_TAG = "ashbound_track";
	/** where a Legend is posted from its poster; how near a hunter must be for it to be there; its trail's reach */
	static final int NEAR = 300, FAR = 1000, SPAWN = 72, TRAIL = 260, POST = 48, TOWN = 96;
	/** days a SLAIN poster stays up before it names a new one */
	static final int REPOST = 3;
	/** a bounty's coins and Guild Points: this many favours of its rank (Errands.pay) */
	static final int COINS_X = 5, GP_X = 3;
	private static final String RANKS = "FEDCBAS";

	static final class Bounty {
		int id, rank;
		String legend = "";
		BlockPos pos = BlockPos.ZERO;
		boolean spawned, slain;
		@Nullable
		UUID mob;
		String slainBy = "";
		long slainDay;

		CompoundTag save() {
			CompoundTag t = new CompoundTag();
			t.putInt("id", id);
			t.putInt("rank", rank);
			t.putString("legend", legend);
			t.put("pos", NbtUtils.writeBlockPos(pos));
			t.putBoolean("spawned", spawned);
			t.putBoolean("slain", slain);
			if (mob != null) t.putUUID("mob", mob);
			t.putString("slain_by", slainBy);
			t.putLong("slain_day", slainDay);
			return t;
		}

		static Bounty load(CompoundTag t) {
			Bounty b = new Bounty();
			b.id = t.getInt("id");
			b.rank = t.getInt("rank");
			b.legend = t.getString("legend");
			b.pos = NbtUtils.readBlockPos(t, "pos").orElse(BlockPos.ZERO);
			b.spawned = t.getBoolean("spawned");
			b.slain = t.getBoolean("slain");
			if (t.hasUUID("mob")) b.mob = t.getUUID("mob");
			b.slainBy = t.getString("slain_by");
			b.slainDay = t.getLong("slain_day");
			return b;
		}

		String giver() {
			return GIVER + id;
		}

		@Nullable
		WorldBeasts.Beast beast() {
			for (WorldBeasts.Beast b : WorldBeasts.ALL)
				if (b.id().equals(legend)) return b;
			return null;
		}

		String name() {
			WorldBeasts.Beast b = beast();
			return b == null ? legend : b.legendName();
		}
	}

	/** Where a poster hangs: its face's middle, the way it looks out, how big; the poster up there now and what it names. */
	static final class Anchor {
		int id, bounty;
		double x, y, z;
		float yaw, scale = 1f;
		@Nullable
		UUID poster;

		CompoundTag save() {
			CompoundTag t = new CompoundTag();
			t.putInt("id", id);
			t.putInt("bounty", bounty);
			ListTag at = new ListTag();
			for (double v : new double[] {x, y, z}) at.add(FloatTag.valueOf((float) v));
			t.put("at", at);
			t.putFloat("yaw", yaw);
			t.putFloat("scale", scale);
			if (poster != null) t.putUUID("poster", poster);
			return t;
		}

		static Anchor load(CompoundTag t) {
			Anchor a = new Anchor();
			a.id = t.getInt("id");
			a.bounty = t.getInt("bounty");
			ListTag at = t.getList("at", Tag.TAG_FLOAT);
			a.x = at.getFloat(0);
			a.y = at.getFloat(1);
			a.z = at.getFloat(2);
			a.yaw = t.getFloat("yaw");
			a.scale = t.contains("scale") ? t.getFloat("scale") : 1f;
			if (t.hasUUID("poster")) a.poster = t.getUUID("poster");
			return a;
		}

		BlockPos block() {
			return BlockPos.containing(x, y, z);
		}
	}

	static final class State extends SavedData {
		final Map<Integer, Bounty> bounties = new HashMap<>();
		final Map<Integer, Anchor> anchors = new LinkedHashMap<>();
		/** towns whose walls have been looked over, "x,z" of their middle */
		final Set<String> towns = new HashSet<>();
		int next = 1;

		@Override
		public CompoundTag save(CompoundTag tag, HolderLookup.Provider reg) {
			ListTag b = new ListTag(), a = new ListTag(), t = new ListTag();
			for (Bounty x : bounties.values()) b.add(x.save());
			for (Anchor x : anchors.values()) a.add(x.save());
			for (String s : towns) t.add(StringTag.valueOf(s));
			tag.put("bounties", b);
			tag.put("anchors", a);
			tag.put("towns", t);
			tag.putInt("next", next);
			return tag;
		}

		static State load(CompoundTag tag, HolderLookup.Provider reg) {
			State st = new State();
			for (Tag t : tag.getList("bounties", Tag.TAG_COMPOUND)) {
				Bounty b = Bounty.load((CompoundTag) t);
				st.bounties.put(b.id, b);
			}
			for (Tag t : tag.getList("anchors", Tag.TAG_COMPOUND)) {
				Anchor a = Anchor.load((CompoundTag) t);
				st.anchors.put(a.id, a);
			}
			for (Tag t : tag.getList("towns", Tag.TAG_STRING)) st.towns.add(t.getAsString());
			st.next = Math.max(1, tag.getInt("next"));
			return st;
		}
	}

	static State state(ServerLevel l) {
		return l.getServer().overworld().getDataStorage().computeIfAbsent(new SavedData.Factory<>(State::new, State::load, null), "ashbound_bounties");
	}

	static int coins(int rank) {
		return Errands.pay(rank)[0] * COINS_X;
	}

	static int points(int rank) {
		return Errands.pay(rank)[1] * GP_X;
	}

	// ---------------------------------------------------------------- where posters hang

	/** An anchor here, unless one's already this close. */
	@Nullable
	static Anchor anchor(ServerLevel l, double x, double y, double z, float yaw, float scale) {
		State st = state(l);
		for (Anchor a : st.anchors.values())
			if ((a.x - x) * (a.x - x) + (a.y - y) * (a.y - y) + (a.z - z) * (a.z - z) < 4) return null;
		Anchor a = new Anchor();
		a.id = st.next++;
		a.x = x;
		a.y = y;
		a.z = z;
		a.yaw = yaw;
		a.scale = scale;
		st.anchors.put(a.id, a);
		st.setDirty();
		return a;
	}

	/** A road's sign (Roads: a dark oak sign on a spruce post, "this way"): a poster nailed to the post under it, facing the same way. */
	static void roadSign(ServerLevel l, BlockPos sign) {
		BlockState s = l.getBlockState(sign);
		if (!(s.getBlock() instanceof StandingSignBlock) || !l.getBlockState(sign.below()).is(Blocks.SPRUCE_FENCE)) return;
		if (!(l.getBlockEntity(sign) instanceof SignBlockEntity e) || !e.getFrontText().getMessage(2, false).getString().equals("this way")) return;
		float yaw = s.getValue(StandingSignBlock.ROTATION) * 22.5f;
		double nx = -Mth.sin(yaw * Mth.DEG_TO_RAD), nz = Mth.cos(yaw * Mth.DEG_TO_RAD);
		BlockPos post = sign.below();
		anchor(l, post.getX() + 0.5 + nx * 0.14, post.getY() + 0.5, post.getZ() + 0.5 + nz * 0.14, yaw, 0.8f);
	}

	private static void chunkLoaded(ChunkEvent.Load e) {
		if (!(e.getLevel() instanceof ServerLevel l) || l.dimension() != Level.OVERWORLD || !(e.getChunk() instanceof LevelChunk c)) return;
		List<BlockPos> signs = new ArrayList<>();
		for (BlockEntity be : c.getBlockEntities().values())
			if (be instanceof SignBlockEntity) signs.add(be.getBlockPos());
		if (!signs.isEmpty()) l.getServer().execute(() -> signs.forEach(p -> roadSign(l, p)));
	}

	/** A few house walls round a town's middle that face its street: a full wall at least three high, the street open in front. */
	static int townWalls(ServerLevel l, Capital.Site s) {
		List<double[]> found = new ArrayList<>();
		int r = 30;
		List<int[]> cols = new ArrayList<>();
		for (int dx = -r; dx <= r; dx++)
			for (int dz = -r; dz <= r; dz++)
				if (dx * dx + dz * dz <= r * r) cols.add(new int[] {dx, dz});
		cols.sort((a, b) -> Integer.compare(a[0] * a[0] + a[1] * a[1], b[0] * b[0] + b[1] * b[1]));
		for (int[] c : cols) {
			if (found.size() >= 3) break;
			int x = s.x + c[0], z = s.z + c[1];
			BlockPos stand = l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, new BlockPos(x, 0, z));
			if (Math.abs(stand.getY() - s.floor) > 10) continue;
			if (!l.getFluidState(stand).isEmpty() || !l.getBlockState(stand).getCollisionShape(l, stand).isEmpty()
					|| !l.getBlockState(stand.above()).getCollisionShape(l, stand.above()).isEmpty()) continue;
			BlockPos floor = stand.below();
			if (!l.getBlockState(floor).isFaceSturdy(l, floor, Direction.UP)) continue;
			for (Direction d : Direction.Plane.HORIZONTAL) {
				BlockPos w = stand.relative(d);
				boolean wall = true;
				for (int k = 0; k < 3 && wall; k++) {
					BlockPos q = w.above(k);
					BlockState b = l.getBlockState(q);
					wall = b.isFaceSturdy(l, q, d.getOpposite()) && b.canOcclude() && !b.is(Blocks.GLASS) && !b.isAir();
				}
				if (!wall) continue;
				double px = w.getX() + 0.5 - d.getStepX() * 0.53, pz = w.getZ() + 0.5 - d.getStepZ() * 0.53;
				if (found.stream().anyMatch(f -> (f[0] - px) * (f[0] - px) + (f[1] - pz) * (f[1] - pz) < 100)) continue;
				found.add(new double[] {px, pz});
				anchor(l, px, stand.getY() + 1.5, pz, d.getOpposite().toYRot(), 1f);
				break;
			}
		}
		return found.size();
	}

	// ---------------------------------------------------------------- the bounties

	/** A new bounty for this anchor: a Legend whose land lies 300..1000 blocks off (one the posters round about don't name
	 * already, if it can), at the rank the one who came by would meet it. */
	static Bounty post(ServerLevel l, Anchor a, ServerPlayer by) {
		State st = state(l);
		RandomSource r = l.getRandom();
		BlockPos from = a.block();
		Map<String, BlockPos> lands = new HashMap<>();
		for (int k = 0; k < 48; k++) {
			double ang = r.nextDouble() * Math.PI * 2, d = NEAR + r.nextDouble() * (FAR - NEAR);
			BlockPos at = new BlockPos((int) (from.getX() + Math.cos(ang) * d), l.getSeaLevel() + 8, (int) (from.getZ() + Math.sin(ang) * d));
			String land = WorldBeasts.land(l.getBiome(at));
			if (land != null && WorldBeasts.town(at) > 220) lands.putIfAbsent(land, at);
		}
		Set<String> near = new HashSet<>();
		for (Anchor o : st.anchors.values())
			if (o != a && st.bounties.get(o.bounty) instanceof Bounty b && !b.slain && (o.x - a.x) * (o.x - a.x) + (o.z - a.z) * (o.z - a.z) < 80 * 80) near.add(b.legend);
		List<WorldBeasts.Beast> pick = new ArrayList<>();
		for (WorldBeasts.Beast b : WorldBeasts.ALL) if (lands.containsKey(b.land()) && !near.contains(b.id())) pick.add(b);
		if (pick.isEmpty()) for (WorldBeasts.Beast b : WorldBeasts.ALL) if (lands.containsKey(b.land())) pick.add(b);
		WorldBeasts.Beast beast = pick.isEmpty() ? WorldBeasts.ALL.get(r.nextInt(WorldBeasts.ALL.size())) : pick.get(r.nextInt(pick.size()));
		BlockPos at = lands.get(beast.land());
		if (at == null) {
			double ang = r.nextDouble() * Math.PI * 2, d = NEAR + r.nextDouble() * (FAR - NEAR);
			at = new BlockPos((int) (from.getX() + Math.cos(ang) * d), l.getSeaLevel() + 8, (int) (from.getZ() + Math.sin(ang) * d));
		}
		Bounty b = new Bounty();
		b.id = st.next++;
		b.legend = beast.id();
		b.pos = at;
		b.rank = WorldBeasts.rankFor(by, at, beast.land(), r);
		st.bounties.put(b.id, b);
		a.bounty = b.id;
		st.setDirty();
		return b;
	}

	/** The poster hanging from this anchor, put up (again) if it's gone, showing what it names. */
	static void hang(ServerLevel l, Anchor a, Bounty b) {
		WantedPoster p = a.poster != null && l.getEntity(a.poster) instanceof WantedPoster w && w.isAlive() ? w : null;
		if (p == null) {
			p = WantedPoster.TYPE.get().create(l);
			if (p == null) return;
			p.hangOn(a.x, a.y, a.z, a.yaw, a.scale);
			p.anchor = a.id;
			if (!l.addFreshEntity(p)) return;
			a.poster = p.getUUID();
			state(l).setDirty();
		}
		p.bounty = b.id;
		if (p.bountyId() != b.id || !p.legend().equals(b.legend) || p.rank() != b.rank || p.slain() != b.slain) p.show(b.legend, b.rank, b.slain);
	}

	/** Which way and how far, as a hunter says it. */
	static String way(BlockPos from, BlockPos to) {
		double dx = to.getX() - from.getX(), dz = to.getZ() - from.getZ();
		String[] dirs = {"south", "south-west", "west", "north-west", "north", "north-east", "east", "south-east"};
		int k = Math.floorMod((int) Math.round(Math.toDegrees(Math.atan2(-dx, dz)) / 45), 8);
		return "about " + (int) (Math.round(Math.hypot(dx, dz) / 50.0) * 50) + " blocks " + dirs[k];
	}

	/** A dead Legend of yours, if you've one to be paid for (any poster pays it). */
	@Nullable
	static Bounty owed(ServerLevel l, ServerPlayer p) {
		for (Bounty b : state(l).bounties.values())
			if (b.slain && Errands.find(p, "fav:" + b.giver()) != null) return b;
		return null;
	}

	/** Someone's read a poster: its screen (client/WantedScreen), with what they can do. */
	static void read(ServerLevel l, WantedPoster poster, ServerPlayer p) {
		State st = state(l);
		Bounty owed = owed(l, p);
		Bounty b = owed != null ? owed : st.bounties.get(poster.bounty);
		if (b == null) return;
		int state = owed != null ? 2 : b.slain ? 3 : Errands.find(p, "fav:" + b.giver()) != null ? 1 : Errands.full(p) ? 4 : 0;
		WorldBeasts.Beast beast = b.beast();
		String land = beast == null ? "the wild" : LANDS.getOrDefault(beast.land(), "the wild");
		PacketDistributor.sendToPlayer(p, new Net.PosterView(poster.getId(), state, List.of(b.rank, coins(b.rank), Guild.of(p).registered() ? points(b.rank) : 0, b.id),
				List.of(b.legend, b.name(), land, way(p.blockPosition(), b.pos), b.slainBy)));
		l.playSound(null, poster.getX(), poster.getY(), poster.getZ(), SoundEvents.BOOK_PAGE_TURN, SoundSource.PLAYERS, 0.6f, 1.2f);
	}

	/** "Take it" or "Claim the bounty" on the poster's screen. */
	static void act(ServerPlayer p, int entity) {
		ServerLevel l = p.serverLevel();
		if (!(l.getEntity(entity) instanceof WantedPoster poster) || poster.distanceToSqr(p) > 8 * 8) return;
		Bounty owed = owed(l, p);
		if (owed != null) {
			Errands.done(p, owed.giver());   // slain while you were away
			Errands.settle(p, owed.giver());
			return;
		}
		Bounty b = state(l).bounties.get(poster.bounty);
		if (b == null || b.slain || Errands.find(p, "fav:" + b.giver()) != null || Errands.full(p)) return;
		WorldBeasts.Beast beast = b.beast();
		String land = beast == null ? "the wild" : LANDS.getOrDefault(beast.land(), "the wild");
		Errands.add(p, new Errands.Errand("legend", Errands.KILL, b.giver(), 1, 0, coins(b.rank), Guild.of(p).registered() ? points(b.rank) : 0, b.giver(),
				"the Guild", b.pos.getX(), b.pos.getZ(), Errands.day(p), "Wanted: " + b.name(),
				"Hunt down " + RANKS.charAt(b.rank) + "-rank " + b.name() + " in " + land + ", then bring word to any wanted poster"));
		Story.pick(p, "fav:" + b.giver());
		p.sendSystemMessage(Component.literal("Last seen in " + land + ", " + way(p.blockPosition(), b.pos) + ". Look for its tracks.").withStyle(ChatFormatting.GRAY, ChatFormatting.ITALIC));
		l.playSound(null, poster.getX(), poster.getY(), poster.getZ(), SoundEvents.PAINTING_BREAK, SoundSource.PLAYERS, 0.9f, 1.4f);
	}

	static final Map<String, String> LANDS = Map.of("snow", "the frozen north", "forest", "the deep woods", "plains", "the open fields",
			"desert", "the dunes", "swamp", "the drowned fens", "jungle", "the jungle", "coast", "the grey coast", "badlands", "the badlands");

	// ---------------------------------------------------------------- out on the hunt

	/** Firm, dry ground near here: the first air over something solid. */
	static BlockPos ground(ServerLevel l, BlockPos at) {
		for (int ring = 0; ring <= 16; ring += 2)
			for (int dx = -ring; dx <= ring; dx += 2)
				for (int dz = -ring; dz <= ring; dz += 2) {
					if (Math.max(Math.abs(dx), Math.abs(dz)) != ring) continue;
					BlockPos top = l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, at.offset(dx, 0, dz));
					if (l.getFluidState(top).isEmpty() && l.getFluidState(top.below()).isEmpty()) return top;
				}
		return l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, at);
	}

	/** The Legend, there when a hunter comes. */
	static void rouse(ServerLevel l, Bounty b, ServerPlayer by) {
		WorldBeasts.Beast beast = b.beast();
		if (beast == null) return;
		BlockPos at = ground(l, b.pos);
		Mob m = WorldBeasts.legend(l, beast, at, b.rank, l.getRandom());
		if (m == null) return;
		m.getPersistentData().putInt(TAG, b.id);
		b.spawned = true;
		b.mob = m.getUUID();
		b.pos = at;
		state(l).setDirty();
		by.displayClientMessage(Component.literal("The ground shakes. " + b.name() + " is close.").withStyle(ChatFormatting.DARK_RED, ChatFormatting.BOLD), true);
	}

	/** Each Legend's mark on the ground: block, how wide, how long, how often it comes in pairs (left, right). */
	private record Print(String block, float wide, float longer, boolean pairs, String first) {}

	private static final Map<String, Print> PRINTS = Map.of(
			"rime_penitent", new Print("minecraft:blue_ice", 0.7f, 1.0f, true, "Frozen footprints, each the size of a cart wheel. Frost still creeps out of them."),
			"old_blackbriar", new Print("minecraft:rooted_dirt", 0.6f, 1.1f, true, "Torn-up roots and earth, as if the forest itself walked through here."),
			"red_plough", new Print("minecraft:coarse_dirt", 0.5f, 2.2f, false, "A deep furrow cut straight across the land. Nothing pulls a plough that big."),
			"sunbreaker", new Print("minecraft:blackstone", 0.8f, 0.9f, true, "Scorched prints, the ground under them burnt black."),
			"grandmother_mire", new Print("minecraft:slime_block", 0.7f, 0.7f, false, "A trail of reeking green ooze. Something old dragged itself through here."),
			"hollow_smile", new Print("minecraft:black_concrete", 0.18f, 1.2f, true, "Long, thin claw marks, far too far apart for anything that walks on two legs."),
			"old_harpoon", new Print("minecraft:prismarine", 0.45f, 1.6f, false, "A wet drag mark, as if a great chain were hauled along the ground."),
			"walking_mountain", new Print("minecraft:cracked_stone_bricks", 1.4f, 1.6f, true, "The ground is cracked in great round prints. Small stones still tumble into them."));

	/** live tracks: the entity and the tick it fades */
	private static final Map<UUID, Long> TRACKS = new HashMap<>();
	private static final Set<String> TOLD = new HashSet<>();

	/** A pair of its prints ahead of you on the way to it. */
	static void trail(ServerLevel l, Bounty b, ServerPlayer p, long now) {
		Print pr = PRINTS.get(b.legend);
		if (pr == null) return;
		double dx = b.pos.getX() + 0.5 - p.getX(), dz = b.pos.getZ() + 0.5 - p.getZ(), d = Math.hypot(dx, dz);
		if (d < 1) return;
		dx /= d;
		dz /= d;
		float yaw = (float) Math.atan2(dx, dz);
		for (int k = 0; k < 2; k++) {
			double ahead = 7 + k * 2.6 + p.getRandom().nextDouble() * 0.6;
			if (ahead > d - 6) break;
			double side = pr.pairs() ? (k == 0 ? 0.55 : -0.55) : 0;
			double x = p.getX() + dx * ahead - dz * side, z = p.getZ() + dz * ahead + dx * side;
			BlockPos top = l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, BlockPos.containing(x, 0, z));
			if (!l.getFluidState(top.below()).isEmpty() || Math.abs(top.getY() - p.getY()) > 6) continue;
			CompoundTag tag = new CompoundTag();
			tag.putString("id", "minecraft:block_display");
			CompoundTag bs = new CompoundTag();
			bs.putString("Name", pr.block());
			tag.put("block_state", bs);
			org.joml.Quaternionf q = new org.joml.Quaternionf().rotationY(yaw + (float) (p.getRandom().nextGaussian() * 0.12));
			CompoundTag tf = new CompoundTag();
			tf.put("left_rotation", floats(q.x, q.y, q.z, q.w));
			tf.put("right_rotation", floats(0, 0, 0, 1));
			tf.put("translation", floats(-pr.wide() / 2, -0.03f, -pr.longer() / 2));
			tf.put("scale", floats(pr.wide(), 0.05f, pr.longer()));
			tag.put("transformation", tf);
			ListTag tags = new ListTag();
			tags.add(StringTag.valueOf(TRACK_TAG));
			tag.put("Tags", tags);
			final double y = top.getY();
			Entity e = EntityType.loadEntityRecursive(tag, l, en -> {
				en.moveTo(x, y, z, 0, 0);
				return en;
			});
			if (e != null && l.addFreshEntity(e)) {
				TRACKS.put(e.getUUID(), now + 1200);
				l.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, Blocks.COARSE_DIRT.defaultBlockState()), x, y + 0.1, z, 4, 0.3, 0.05, 0.3, 0.05);
			}
		}
		if (TOLD.add(p.getUUID() + ":" + b.id)) p.sendSystemMessage(Component.literal(pr.first()).withStyle(ChatFormatting.GRAY, ChatFormatting.ITALIC));
	}

	private static ListTag floats(float... v) {
		ListTag t = new ListTag();
		for (float f : v) t.add(FloatTag.valueOf(f));
		return t;
	}

	/** Tracks left over from a session gone: never kept. */
	private static void joined(EntityJoinLevelEvent e) {
		if (e.loadedFromDisk() && e.getEntity().getTags().contains(TRACK_TAG) && !TRACKS.containsKey(e.getEntity().getUUID())) e.setCanceled(true);
	}

	private static void tick(ServerTickEvent.Post e) {
		var server = e.getServer();
		ServerLevel l = server.overworld();
		long now = server.getTickCount();
		if (now % 20 == 11 && !TRACKS.isEmpty()) {
			for (Iterator<Map.Entry<UUID, Long>> it = TRACKS.entrySet().iterator(); it.hasNext(); ) {
				var t = it.next();
				if (t.getValue() > now) continue;
				Entity tr = l.getEntity(t.getKey());
				if (tr != null) tr.discard();
				it.remove();
			}
		}
		if (now % 40 != 13) return;
		State st = state(l);
		long day = l.getDayTime() / 24000L;
		for (ServerPlayer p : l.players()) {
			if (p.isSpectator()) continue;
			// a town's walls, looked over once, the first time someone comes near its middle
			for (Capital.Site s : Capital.sites) {
				String key = s.x + "," + s.z;
				if (st.towns.contains(key) || Math.hypot(p.getX() - s.x, p.getZ() - s.z) > TOWN || !l.isPositionEntityTicking(new BlockPos(s.x, s.floor, s.z))) continue;
				st.towns.add(key);
				st.setDirty();
				townWalls(l, s);
			}
			// the posters round you, each naming a live bounty (a new one a few days after its Legend fell)
			for (Anchor a : st.anchors.values()) {
				if ((a.x - p.getX()) * (a.x - p.getX()) + (a.z - p.getZ()) * (a.z - p.getZ()) > POST * POST || !l.isPositionEntityTicking(a.block())) continue;
				Bounty b = st.bounties.get(a.bounty);
				if (b == null || b.slain && day - b.slainDay >= REPOST) b = post(l, a, p);
				hang(l, a, b);
			}
			// your hunts: the trail, then the Legend
			for (Bounty b : st.bounties.values()) {
				if (b.slain || Errands.find(p, "fav:" + b.giver()) == null) continue;
				double d = Math.hypot(p.getX() - b.pos.getX(), p.getZ() - b.pos.getZ());
				boolean there = b.spawned && b.mob != null && l.getEntity(b.mob) instanceof Mob m && m.isAlive();
				if (d < SPAWN && !there && l.isPositionEntityTicking(b.pos)) rouse(l, b, p);
				else if (!there && d < TRAIL && d > 18 && now % 80 == 13) trail(l, b, p, now);
			}
		}
	}

	/** A Legend with a bounty on it has fallen: every poster of it stamped, everyone hunting it told to come and be paid. */
	private static void died(LivingDeathEvent e) {
		if (!(e.getEntity().level() instanceof ServerLevel l) || !e.getEntity().getPersistentData().contains(TAG)) return;
		State st = state(l);
		Bounty b = st.bounties.get(e.getEntity().getPersistentData().getInt(TAG));
		if (b == null || b.slain) return;
		b.slain = true;
		b.slainDay = l.getDayTime() / 24000L;
		Entity by = e.getSource().getEntity();
		b.slainBy = by instanceof ServerPlayer p ? p.getGameProfile().getName() : "";
		st.setDirty();
		for (ServerPlayer p : l.getServer().getPlayerList().getPlayers())
			if (Errands.find(p, "fav:" + b.giver()) != null && Errands.done(p, b.giver()))
				p.sendSystemMessage(Component.literal(b.name() + " is slain!").withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD)
						.append(Component.literal(" Bring word to any wanted poster for the bounty.").withStyle(ChatFormatting.GREEN)));
		for (Anchor a : st.anchors.values())
			if (a.bounty == b.id && a.poster != null && l.getEntity(a.poster) instanceof WantedPoster w) w.show(b.legend, b.rank, true);
	}

	private static void commands(RegisterCommandsEvent e) {
		e.getDispatcher().register(Commands.literal("ashbound").requires(c -> c.hasPermission(2)).then(Commands.literal("poster").executes(c -> {
			// a poster on the wall you're looking at (or in front of you), naming a new bounty
			ServerPlayer p = c.getSource().getPlayerOrException();
			ServerLevel l = p.serverLevel();
			Direction f = p.getDirection();
			BlockPos wall = p.blockPosition().above().relative(f, 2);
			Anchor a = anchor(l, wall.getX() + 0.5 - f.getStepX() * 0.53, wall.getY() + 0.5, wall.getZ() + 0.5 - f.getStepZ() * 0.53, f.getOpposite().toYRot(), 1f);
			if (a == null) return 0;
			hang(l, a, post(l, a, p));
			c.getSource().sendSuccess(() -> Component.literal("A wanted poster on the wall ahead"), false);
			return 1;
		})));
	}

	static void init() {
		WantedPoster.TYPE.getId();
		NeoForge.EVENT_BUS.addListener(Bounties::tick);
		NeoForge.EVENT_BUS.addListener(Bounties::died);
		NeoForge.EVENT_BUS.addListener(Bounties::chunkLoaded);
		NeoForge.EVENT_BUS.addListener(Bounties::joined);
		NeoForge.EVENT_BUS.addListener(Bounties::commands);
	}
}
