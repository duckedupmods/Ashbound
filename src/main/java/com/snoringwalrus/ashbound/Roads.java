package com.snoringwalrus.ashbound;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.BitSet;
import java.util.HashMap;
import java.util.HashSet;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;
import java.util.Queue;
import java.util.Random;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentLinkedQueue;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.CrossCollisionBlock;
import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.StandingSignBlock;
import net.minecraft.world.level.block.entity.SignBlockEntity;
import net.minecraft.world.level.block.entity.SignText;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.SlabType;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.storage.LevelResource;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.level.ChunkEvent;
import net.neoforged.neoforge.event.server.ServerStoppingEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;

/**
 * The roads between Highmourn and the villages (Capital's sites): the capital's gate out to its nearest village, then
 * each place joined to the nearest one not yet on the network, so every place can be walked to.
 *
 *   - The route: an A* over the land the generator will make, a node every 16 blocks (no chunk need be made), paying
 *     for climbing and for water and going round whatever's built. It runs on its own thread at world load. Rounded
 *     off, it's sampled every half block; the road's height along it is the land's, eased, so it cuts through rises
 *     and runs on a bank over dips, a half slab where it's between two levels, and crosses water on a plank bridge.
 *   - Laying it: the columns it covers are kept per chunk and laid when that chunk's loaded (world/ashbound_roads.json
 *     keeps which are done): flagstones for its first stretch out of a town, a dirt track beyond, ragged at its edges;
 *     grass, flowers, snow and trees cleared off it.
 *   - Beside it: signposts at each end, lamps out of the capital, milestones along the rest.
 *
 * `/ashbound roads` says how far along they are; `/ashbound roads lay` lays them all now.
 */
public final class Roads {
	private Roads() {}

	/** chunk -> column -> {y x2, kind (0 dirt, 1 flagstones, 2 bridge), distance from the middle x10, half width x10}. */
	private static final Map<Long, Map<Long, int[]>> CHUNKS = new ConcurrentHashMap<>();
	private static final List<Spot> SPOTS = new ArrayList<>();
	private static final Set<Long> DONE = new HashSet<>();
	private static final Set<Integer> SPOTS_DONE = new HashSet<>();
	private static final Queue<Long> READY = new ConcurrentLinkedQueue<>();
	private static final List<String> SUMMARY = new ArrayList<>();
	private static volatile boolean planned;
	private static MinecraftServer server;
	private static boolean dirty;
	private static int clock;

	private static final int GRID = 16, MAX_NODES = 240000, ARRIVED = 90;

	/** Something set beside a road: a "sign" (text lines), a "lamp", or a "mile"stone. */
	private record Spot(String kind, int x, int z, double fx, double fz, String[] text) {}

	private record Node(Capital.Site site, double x, double z, String name) {}

	// ================================================================ planning

	/** The land the generator will make, without making it: {top (first air above, water counted), 1 if that's water}. */
	private static final class Land {
		final ServerLevel level;
		final Map<Long, int[]> memo = new ConcurrentHashMap<>();

		Land(ServerLevel level) {
			this.level = level;
		}

		int[] at(int x, int z) {
			return memo.computeIfAbsent(key(x, z), k -> {
				var gen = level.getChunkSource().getGenerator();
				var rs = level.getChunkSource().randomState();
				int top = gen.getBaseHeight(x, z, Heightmap.Types.WORLD_SURFACE_WG, level, rs);
				// open water's only ever at sea level, and each of these is a whole column of noise
				return new int[] {top, top <= gen.getSeaLevel() + 1 && top > gen.getBaseHeight(x, z, Heightmap.Types.OCEAN_FLOOR_WG, level, rs) ? 1 : 0};
			});
		}
	}

	/** The columns of a place that have something built on them. */
	private static final Map<Capital.Data, BitSet> BUILT = new IdentityHashMap<>();

	private static BitSet built(Capital.Site s) {
		return BUILT.computeIfAbsent(s.d, d -> {
			BitSet b = new BitSet(d.gw * d.gd);
			for (var e : d.blocks.entrySet()) {
				int cx = net.minecraft.world.level.ChunkPos.getX(e.getKey()), cz = net.minecraft.world.level.ChunkPos.getZ(e.getKey());
				int[][] v = e.getValue();
				for (int i = 0; i < v[0].length; i++) {
					int y = (v[0][i] >> 8) - 2048;
					if (y < 1 || d.palette[v[1][i]].isAir()) continue;
					int gx = cx * 16 + (v[0][i] & 15) - d.gx0, gz = cz * 16 + (v[0][i] >> 4 & 15) - d.gz0;
					if (gx >= 0 && gz >= 0 && gx < d.gw && gz < d.gd) b.set(gz * d.gw + gx);
				}
			}
			return b;
		});
	}

	/** Which place's built-up ground this column is in, if any. */
	private static boolean isBuilt(Capital.Site[] sites, int x, int z) {
		for (Capital.Site s : Capital.near(x, z)) {
			int k = s.column(x, z);
			if (k >= 0 && built(s).get(k)) return true;
		}
		return false;
	}

	private static boolean nearBuilt(Capital.Site[] sites, int x, int z, int r) {
		for (int dx = -r; dx <= r; dx += r)
			for (int dz = -r; dz <= r; dz += r)
				if (isBuilt(sites, x + dx, z + dz)) return true;
		return false;
	}

	/** Works out the network behind the game's back; chunks loaded meanwhile are caught up with once it's done. */
	static void plan(ServerLevel level, Capital.Site[] sites) {
		server = level.getServer();
		CHUNKS.clear();
		SPOTS.clear();
		SUMMARY.clear();
		READY.clear();
		planned = false;
		load();
		if (sites.length < 2) return;
		Thread t = new Thread(() -> {
			try {
				long t0 = System.currentTimeMillis();
				work(level, sites);
				planned = true;
				Ashbound.LOG.info("Roads: {} over {} chunks, {} things beside them, worked out in {} s ({} chunks already laid)", SUMMARY.size(), CHUNKS.size(), SPOTS.size(),
						(System.currentTimeMillis() - t0) / 1000, DONE.size());
			} catch (Exception e) {
				Ashbound.LOG.error("Couldn't work out the roads", e);
			}
		}, "Ashbound roads");
		t.setDaemon(true);
		t.start();
	}

	private static void work(ServerLevel level, Capital.Site[] sites) {
		List<Node> nodes = new ArrayList<>();
		for (Capital.Site s : sites) {
			double[] g = s.d.points.getOrDefault(s == Capital.site ? "gate" : "centre", new double[] {0, 1, 0});
			nodes.add(new Node(s, s.x + g[0], s.z + g[2], s.title));
		}
		// each place joined to the nearest one not yet on the network, the capital first
		List<Node> on = new ArrayList<>(List.of(nodes.get(0)));
		List<Node> off = new ArrayList<>(nodes.subList(1, nodes.size()));
		List<Node[]> legs = new ArrayList<>();
		while (!off.isEmpty()) {
			Node from = null, to = null;
			double best = Double.MAX_VALUE;
			for (Node a : on)
				for (Node b : off) {
					double d = Math.hypot(a.x() - b.x(), a.z() - b.z());
					if (d < best) {
						best = d;
						from = a;
						to = b;
					}
				}
			legs.add(new Node[] {from, to});
			on.add(to);
			off.remove(to);
		}
		for (Capital.Site s : sites) built(s);
		Ashbound.LOG.info("Roads: working out {} between {} places", legs.size(), sites.length);
		Land land = new Land(level);
		Map<Integer, double[][]> walks = new ConcurrentHashMap<>();
		java.util.stream.IntStream.range(0, legs.size()).parallel().forEach(k -> {
			List<double[]> way = route(land, sites, legs.get(k)[0], legs.get(k)[1]);
			if (way != null) walks.put(k, sample(way));
		});
		for (int k = 0; k < legs.size(); k++) {
			Node a = legs.get(k)[0], b = legs.get(k)[1];
			double[][] s = walks.get(k);
			if (s == null) {
				SUMMARY.add(a.name() + " - " + b.name() + ": no way found");
				Ashbound.LOG.warn("No road from {} to {}", a.name(), b.name());
				continue;
			}
			s = trim(sites, s);
			if (s.length < 40) continue;
			int wet = 0;
			for (double[] q : s) if (land.at((int) Math.floor(q[0]), (int) Math.floor(q[1]))[1] == 1) wet++;
			if (wet > 700) {                                  // 350 blocks of open water: that's not a road
				SUMMARY.add(a.name() + " - " + b.name() + ": too much water");
				continue;
			}
			lay(land, sites, s, a.site() == Capital.site);
			SUMMARY.add(a.name() + " - " + b.name() + ": " + s.length / 2 + " blocks from " + (int) s[0][0] + " " + (int) s[0][1] + ", " + wet / 2 + " over water");
			Ashbound.LOG.info("Road: {}", SUMMARY.get(SUMMARY.size() - 1));
			spotBeside(s, 10, 3.4, 1, "sign", new String[] {b.name().toUpperCase(), s.length / 2 + " blocks", "this way", ""});
			spotBeside(s, s.length - 11, 3.4, -1, "sign", new String[] {a.name().toUpperCase(), s.length / 2 + " blocks", "this way", ""});
			Random r = new Random(level.getSeed() ^ (0x5DEECE66DL * (k + 1)));
			double len = s.length * 0.5;
			if (a.site() == Capital.site)
				for (double m = 24; m < Math.min(170, len - 20); m += 30) spotBeside(s, (int) (m * 2), 2.9, ((int) m / 30) % 2 == 0 ? 1 : -1, "lamp", null);
			for (double m = a.site() == Capital.site ? 260 : 120; m < len - 40; m += 130 + r.nextInt(40)) spotBeside(s, (int) (m * 2), 2.7, r.nextBoolean() ? 1 : -1, "mile", null);
		}
	}

	/** A* from a to b. The ends' own ground can be crossed at a price (the walk's cut off where it's built up); anyone
	 *  else's isn't crossed at all. */
	private static List<double[]> route(Land land, Capital.Site[] sites, Node a, Node b) {
		int sx = Math.floorDiv((int) a.x(), GRID), sz = Math.floorDiv((int) a.z(), GRID), gx = Math.floorDiv((int) b.x(), GRID), gz = Math.floorDiv((int) b.z(), GRID);
		PriorityQueue<double[]> open = new PriorityQueue<>((p, q) -> Double.compare(p[0], q[0]));
		Map<Long, Double> best = new HashMap<>();
		Map<Long, Long> came = new HashMap<>();
		open.add(new double[] {0, sx, sz});
		best.put(key(sx, sz), 0.0);
		int seen = 0;
		while (!open.isEmpty() && seen++ < MAX_NODES) {
			double[] c = open.poll();
			int cx = (int) c[1], cz = (int) c[2];
			// near enough: a place's own ground can be too steep to get a node onto, the last stretch is walked straight
			if (Math.hypot(cx - gx, cz - gz) * GRID < ARRIVED) {
				List<double[]> out = new ArrayList<>();
				out.add(new double[] {b.x(), b.z()});
				long at = key(cx, cz);
				while (came.containsKey(at)) {
					at = came.get(at);
					out.add(0, new double[] {(int) (at >> 32) * GRID + 8.0, (int) at * GRID + 8.0});
				}
				out.set(0, new double[] {a.x(), a.z()});
				return out;
			}
			double g0 = best.get(key(cx, cz));
			int[] here = land.at(cx * GRID + 8, cz * GRID + 8);
			for (int dx = -1; dx <= 1; dx++)
				for (int dz = -1; dz <= 1; dz++) {
					if (dx == 0 && dz == 0) continue;
					int nx = cx + dx, nz = cz + dz, wx = nx * GRID + 8, wz = nz * GRID + 8;
					double step = Math.hypot(dx, dz) * GRID, extra = 0;
					boolean theirs = false;
					for (Capital.Site s : Capital.near(wx, wz)) {
						int k = s.column(wx, wz);
						if (k >= 0 && built(s).get(k)) {
							if (s == a.site() || s == b.site()) extra = 600;
							else theirs = true;
						}
					}
					if (theirs) continue;
					int[] there = land.at(wx, wz);
					int climb = Math.abs(there[0] - here[0]);
					if (climb > 22) continue;
					double g1 = g0 + step + climb * climb * 1.4 + there[1] * 60 + extra;
					long nk = key(nx, nz);
					if (g1 < best.getOrDefault(nk, Double.MAX_VALUE)) {
						best.put(nk, g1);
						came.put(nk, key(cx, cz));
						// a weighted heuristic: not the very best road, but found in a tenth of the looks at the land
						open.add(new double[] {g1 + 1.5 * Math.hypot(nx - gx, nz - gz) * GRID, nx, nz});
					}
				}
		}
		return null;
	}

	/** The road's ends cut back to where the places' buildings begin. */
	private static double[][] trim(Capital.Site[] sites, double[][] s) {
		int a = 0, b = s.length;
		for (int i = 0; i < s.length / 2; i++) if (nearBuilt(sites, (int) Math.floor(s[i][0]), (int) Math.floor(s[i][1]), 4)) a = i + 1;
		for (int i = s.length - 1; i >= s.length / 2; i--) if (nearBuilt(sites, (int) Math.floor(s[i][0]), (int) Math.floor(s[i][1]), 4)) b = i;
		return a < b ? java.util.Arrays.copyOfRange(s, a, b) : new double[0][];
	}

	/** The route rounded off (Chaikin's corners, three times), then a point every half block. */
	private static double[][] sample(List<double[]> way) {
		List<double[]> p = way;
		for (int it = 0; it < 3; it++) {
			List<double[]> q = new ArrayList<>();
			q.add(p.get(0));
			for (int i = 0; i + 1 < p.size(); i++) {
				double[] a = p.get(i), b = p.get(i + 1);
				q.add(new double[] {a[0] * 0.75 + b[0] * 0.25, a[1] * 0.75 + b[1] * 0.25});
				q.add(new double[] {a[0] * 0.25 + b[0] * 0.75, a[1] * 0.25 + b[1] * 0.75});
			}
			q.add(p.get(p.size() - 1));
			p = q;
		}
		List<double[]> out = new ArrayList<>();
		out.add(p.get(0));
		double carry = 0;
		for (int i = 0; i + 1 < p.size(); i++) {
			double[] a = p.get(i), b = p.get(i + 1);
			double len = Math.hypot(b[0] - a[0], b[1] - a[1]);
			double t = 0.5 - carry;
			while (t <= len) {
				out.add(new double[] {a[0] + (b[0] - a[0]) * t / len, a[1] + (b[1] - a[1]) * t / len});
				t += 0.5;
			}
			carry = len - (t - 0.5);
		}
		return out.toArray(new double[0][]);
	}

	/** The road's columns along samples s: its height eased along the land's, flagstones out of the capital. */
	private static void lay(Land land, Capital.Site[] sites, double[][] s, boolean fromCapital) {
		int n = s.length;
		double[] raw = new double[n];
		boolean[] wet = new boolean[n];
		for (int i = 0; i < n; i++) {
			int[] l = land.at((int) Math.floor(s[i][0]), (int) Math.floor(s[i][1]));
			wet[i] = l[1] == 1;
			raw[i] = wet[i] ? l[0] : l[0] - 1;
		}
		double[] y = new double[n];
		for (int i = 0; i < n; i++) {
			double sum = 0;
			int c = 0;
			for (int k = Math.max(0, i - 16); k <= Math.min(n - 1, i + 16); k++) {
				sum += raw[k];
				c++;
			}
			double v = sum / c;
			y[i] = wet[i] ? Math.max(raw[i], Math.min(raw[i] + 2, v)) : Math.max(raw[i] - 3, Math.min(raw[i] + 3, v));
		}
		for (int i = 0; i < n; i++) {
			boolean flags = fromCapital ? i < 400 : i < 60 || i > n - 60;
			double w = wet[i] ? 2.5 : flags ? 2.4 : 1.8;
			int kind = wet[i] ? 2 : flags ? 1 : 0;
			int y2 = (int) Math.round(y[i] * 2);
			for (int x = (int) Math.floor(s[i][0] - w); x <= (int) Math.ceil(s[i][0] + w); x++)
				for (int z = (int) Math.floor(s[i][1] - w); z <= (int) Math.ceil(s[i][1] + w); z++) {
					double dd = Math.hypot(x + 0.5 - s[i][0], z + 0.5 - s[i][1]);
					if (dd > w || isBuilt(sites, x, z)) continue;
					Map<Long, int[]> chunk = CHUNKS.computeIfAbsent(key(x >> 4, z >> 4), k -> new ConcurrentHashMap<>());
					int[] c = chunk.get(key(x, z));
					if (c == null || dd * 10 < c[2]) chunk.put(key(x, z), new int[] {y2, kind, (int) (dd * 10), (int) (w * 10)});
				}
		}
	}

	private static double[] side(double[][] s, int i) {
		int a = Math.max(0, i - 4), b = Math.min(s.length - 1, i + 4);
		double dx = s[b][0] - s[a][0], dz = s[b][1] - s[a][1], l = Math.max(1e-6, Math.hypot(dx, dz));
		return new double[] {-dz / l, dx / l};
	}

	private static void spotBeside(double[][] s, int i, double off, int side, String kind, String[] text) {
		if (i < 0 || i >= s.length) return;
		double[] nv = side(s, i);
		double x = s[i][0] + nv[0] * off * side, z = s[i][1] + nv[1] * off * side;
		SPOTS.add(new Spot(kind, (int) Math.floor(x), (int) Math.floor(z), -nv[0] * side, -nv[1] * side, text));
	}

	// ================================================================ laying it

	private static void loaded(ChunkEvent.Load e) {
		if (!(e.getLevel() instanceof ServerLevel l) || l.dimension() != Level.OVERWORLD || !(e.getChunk() instanceof LevelChunk)) return;
		READY.add(key(e.getChunk().getPos().x, e.getChunk().getPos().z));
	}

	private static void tick(ServerTickEvent.Post e) {
		if (!planned || CHUNKS.isEmpty()) return;
		ServerLevel level = e.getServer().overworld();
		for (int n = 0; n < 24; n++) {
			Long ck = READY.poll();
			if (ck == null) break;
			if (!CHUNKS.containsKey(ck) || DONE.contains(ck) || level.getChunkSource().getChunkNow((int) (ck >> 32), (int) (long) ck) == null) continue;
			layChunk(level, ck);
		}
		// what stands beside the road, as soon as the ground round it is in; stragglers the queue missed
		if (++clock % 2 != 0) return;
		int budget = 3;
		for (var en : CHUNKS.entrySet()) {
			if (budget <= 0) break;
			long ck = en.getKey();
			if (DONE.contains(ck) || level.getChunkSource().getChunkNow((int) (ck >> 32), (int) ck) == null) continue;
			layChunk(level, ck);
			budget--;
		}
		for (int k = 0; k < SPOTS.size() && budget > 0; k++) {
			if (SPOTS_DONE.contains(k)) continue;
			Spot s = SPOTS.get(k);
			if (level.getChunkSource().getChunkNow(s.x() >> 4, s.z() >> 4) == null) continue;
			long ck = key(s.x() >> 4, s.z() >> 4);
			if (CHUNKS.containsKey(ck) && !DONE.contains(ck)) continue;
			spot(level, s);
			SPOTS_DONE.add(k);
			dirty = true;
			budget--;
		}
		if (dirty && clock % 200 == 0) save();
	}

	private static void layChunk(ServerLevel level, long ck) {
		for (var c : CHUNKS.get(ck).entrySet()) column(level, (int) (c.getKey() >> 32), (int) (long) c.getKey(), c.getValue());
		DONE.add(ck);
		dirty = true;
	}

	/** Grass, flowers, snow, saplings, leaves and trunks: what stands on the land, not the land. */
	private static boolean soft(BlockState st) {
		if (st.isAir() || st.is(BlockTags.LEAVES) || st.is(BlockTags.LOGS)) return true;
		if (!st.getFluidState().isEmpty()) return false;
		return st.canBeReplaced() || st.is(Blocks.CACTUS) || st.is(Blocks.SUGAR_CANE) || st.is(Blocks.BAMBOO)
				|| st.is(Blocks.SWEET_BERRY_BUSH) || st.is(Blocks.PUMPKIN) || st.is(Blocks.MELON) || st.is(Blocks.SNOW)
				|| st.is(Blocks.BROWN_MUSHROOM_BLOCK) || st.is(Blocks.RED_MUSHROOM_BLOCK) || st.is(Blocks.MUSHROOM_STEM);
	}

	/** The land's top block at x, z (under whatever stands on it; a water surface counts as land here). */
	private static int groundY(ServerLevel level, int x, int z) {
		BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos(x, level.getHeight(Heightmap.Types.WORLD_SURFACE, x, z) - 1, z);
		while (p.getY() > level.getMinBuildHeight() && soft(level.getBlockState(p))) p.move(0, -1, 0);
		return p.getY();
	}

	private static int hash(int x, int z) {
		int h = x * 73856093 ^ z * 19349663;
		h ^= h >>> 13;
		return (h * 0x5bd1e995) >>> 8;
	}

	private static void set(ServerLevel level, BlockPos p, BlockState st) {
		level.setBlock(p, st, Block.UPDATE_CLIENTS);
	}

	private static void column(ServerLevel level, int x, int z, int[] c) {
		int y = Math.floorDiv(c[0], 2), kind = c[1];
		boolean half = (c[0] & 1) == 1;
		double dist = c[2] / 10.0, w = c[3] / 10.0;
		int h = hash(x, z);
		int gy = groundY(level, x, z);
		BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos(x, gy, z);
		boolean water = level.getFluidState(p).is(FluidTags.WATER);
		if (water && kind == 2) {
			// the bridge: a deck on the water, rails along its sides, posts down to the bed now and then
			int deck = Math.max(y, gy + 1);
			boolean rail = dist >= w - 0.75;
			set(level, p.setY(deck), Blocks.SPRUCE_PLANKS.defaultBlockState());
			for (int k = 1; k <= 3; k++) if (soft(level.getBlockState(p.setY(deck + k)))) set(level, p, Blocks.AIR.defaultBlockState());
			if (rail) {
				set(level, p.setY(deck + 1), fence(level, x, deck + 1, z));
				if (h % 5 == 0)
					for (int yy = deck - 1; yy > level.getMinBuildHeight() && yy > deck - 24; yy--) {
						BlockState st = level.getBlockState(p.setY(yy));
						if (!st.isAir() && st.getFluidState().isEmpty()) break;
						set(level, p, Blocks.SPRUCE_LOG.defaultBlockState());
					}
			}
			return;
		}
		// a ragged edge: here and there the grass keeps the road's shoulder
		boolean shoulder = dist > w - 0.7;
		if (shoulder && h % 3 == 0) return;
		if (Math.abs(y - gy) > 3) {
			y = gy;
			half = false;
		}
		// never through something built: a chest, a barrel, a bed, a sign (a ruin's, a structure's)
		for (int yy = Math.min(y, gy) - 1; yy <= Math.max(y, gy) + 4; yy++)
			if (level.getBlockEntity(p.setY(yy)) != null) return;
		// cut down to it, or bank up to it
		for (int yy = y + 1; yy <= gy; yy++) set(level, p.setY(yy), Blocks.AIR.defaultBlockState());
		for (int yy = gy + 1; yy < y; yy++) set(level, p.setY(yy), (h >> yy & 3) == 0 ? Blocks.COARSE_DIRT.defaultBlockState() : Blocks.DIRT.defaultBlockState());
		set(level, p.setY(y), surface(kind, shoulder, h));
		if (half && !shoulder) set(level, p.setY(y + 1), (kind == 1 ? Blocks.SMOOTH_STONE_SLAB : Blocks.MUD_BRICK_SLAB).defaultBlockState().setValue(SlabBlock.TYPE, SlabType.BOTTOM));
		// clear it: plants, snow and leaves off it; a trunk in its way goes, all the way up
		for (int yy = y + (half && !shoulder ? 2 : 1); yy <= y + 4; yy++) {
			BlockState st = level.getBlockState(p.setY(yy));
			if (st.is(BlockTags.LOGS)) {
				for (int up = yy; up < yy + 40 && level.getBlockState(p.setY(up)).is(BlockTags.LOGS); up++) set(level, p, Blocks.AIR.defaultBlockState());
				p.setY(yy);
			}
			if (soft(level.getBlockState(p.setY(yy))) && !level.getBlockState(p).isAir()) set(level, p, Blocks.AIR.defaultBlockState());
		}
	}

	private static BlockState surface(int kind, boolean shoulder, int h) {
		int r = h % 20;
		if (kind == 1) {
			if (shoulder) return r < 10 ? block("limestone_flagstones") : r < 15 ? Blocks.GRAVEL.defaultBlockState() : Blocks.COARSE_DIRT.defaultBlockState();
			return r < 12 ? block("limestone_flagstones") : r < 17 ? Blocks.POLISHED_ANDESITE.defaultBlockState() : Blocks.SMOOTH_STONE.defaultBlockState();
		}
		if (shoulder) return r < 9 ? Blocks.COARSE_DIRT.defaultBlockState() : r < 15 ? Blocks.DIRT_PATH.defaultBlockState() : Blocks.GRAVEL.defaultBlockState();
		return r < 14 ? Blocks.DIRT_PATH.defaultBlockState() : r < 18 ? Blocks.COARSE_DIRT.defaultBlockState() : Blocks.GRAVEL.defaultBlockState();
	}

	private static BlockState block(String name) {
		return BuiltInRegistries.BLOCK.get(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, name)).defaultBlockState();
	}

	/** A spruce fence joined to the rail and posts round it (only where those neighbours are loaded). */
	private static BlockState fence(ServerLevel level, int x, int y, int z) {
		BlockState f = Blocks.SPRUCE_FENCE.defaultBlockState();
		int[][] d = {{0, -1}, {1, 0}, {0, 1}, {-1, 0}};
		var props = new net.minecraft.world.level.block.state.properties.BooleanProperty[] {CrossCollisionBlock.NORTH, CrossCollisionBlock.EAST, CrossCollisionBlock.SOUTH, CrossCollisionBlock.WEST};
		for (int k = 0; k < 4; k++) {
			int nx = x + d[k][0], nz = z + d[k][1];
			if (level.getChunkSource().getChunkNow(nx >> 4, nz >> 4) == null) continue;
			BlockState n = level.getBlockState(new BlockPos(nx, y, nz));
			boolean join = n.is(BlockTags.FENCES);
			if (!join) {
				Map<Long, int[]> c = CHUNKS.get(key(nx >> 4, nz >> 4));
				int[] col = c == null ? null : c.get(key(nx, nz));
				join = col != null && col[1] == 2 && col[2] / 10.0 >= col[3] / 10.0 - 0.75;
			}
			if (join) f = f.setValue(props[k], true);
			if (n.is(BlockTags.FENCES)) set(level, new BlockPos(nx, y, nz), n.setValue(props[(k + 2) % 4], true));
		}
		return f;
	}

	private static void spot(ServerLevel level, Spot s) {
		int gy = groundY(level, s.x(), s.z());
		BlockPos at = new BlockPos(s.x(), gy, s.z());
		if (!level.getFluidState(at).isEmpty()) return;
		switch (s.kind()) {
			case "sign" -> {
				set(level, at.above(), Blocks.SPRUCE_FENCE.defaultBlockState());
				// the sign faces back the way the road comes
				int rot = Math.floorMod((int) Math.round(Math.toDegrees(Math.atan2(-s.fx(), s.fz())) / 22.5), 16);
				set(level, at.above(2), Blocks.DARK_OAK_SIGN.defaultBlockState().setValue(StandingSignBlock.ROTATION, rot));
				if (level.getBlockEntity(at.above(2)) instanceof SignBlockEntity sign) {
					SignText t = sign.getFrontText();
					for (int k = 0; k < 4 && k < s.text().length; k++) t = t.setMessage(k, Component.literal(s.text()[k]));
					sign.setText(t, true);
					sign.setWaxed(true);
					sign.setChanged();
					level.sendBlockUpdated(at.above(2), sign.getBlockState(), sign.getBlockState(), Block.UPDATE_CLIENTS);
				}
			}
			case "lamp" -> {
				set(level, at.above(), block("hearthstone_bricks"));
				set(level, at.above(2), Blocks.DARK_OAK_FENCE.defaultBlockState());
				set(level, at.above(3), Blocks.DARK_OAK_FENCE.defaultBlockState());
				set(level, at.above(4), Blocks.LANTERN.defaultBlockState());
			}
			case "mile" -> {
				set(level, at.above(), block("hearthstone_bricks"));
				set(level, at.above(2), block("hearthstone_quoin"));
			}
			default -> {}
		}
	}

	// ================================================================ keeping track

	private static long key(int a, int b) {
		return ((long) a << 32) | (b & 0xFFFFFFFFL);
	}

	private static Path file() {
		return server.getWorldPath(LevelResource.ROOT).resolve("ashbound_roads.json");
	}

	private static void load() {
		DONE.clear();
		SPOTS_DONE.clear();
		try {
			if (!Files.exists(file())) return;
			JsonObject j = JsonParser.parseString(Files.readString(file())).getAsJsonObject();
			for (JsonElement e : j.getAsJsonArray("chunks")) DONE.add(e.getAsLong());
			for (JsonElement e : j.getAsJsonArray("spots")) SPOTS_DONE.add(e.getAsInt());
		} catch (Exception e) {
			Ashbound.LOG.warn("Couldn't read the roads file", e);
		}
	}

	private static void save() {
		if (server == null) return;
		JsonObject j = new JsonObject();
		JsonArray c = new JsonArray(), s = new JsonArray();
		DONE.forEach(c::add);
		SPOTS_DONE.forEach(s::add);
		j.add("chunks", c);
		j.add("spots", s);
		try {
			Files.writeString(file(), j.toString());
			dirty = false;
		} catch (Exception e) {
			Ashbound.LOG.warn("Couldn't write the roads file", e);
		}
	}

	static void init() {
		NeoForge.EVENT_BUS.addListener(Roads::tick);
		NeoForge.EVENT_BUS.addListener(Roads::loaded);
		NeoForge.EVENT_BUS.addListener((ServerStoppingEvent e) -> {
			if (dirty) save();
			planned = false;
			CHUNKS.clear();
			SPOTS.clear();
		});
		NeoForge.EVENT_BUS.addListener((RegisterCommandsEvent e) -> e.getDispatcher().register(Commands.literal("ashbound").requires(s -> s.hasPermission(2))
				.then(Commands.literal("roads").then(Commands.literal("lay").executes(c -> {
					// every road and everything beside it, now (the chunks they cross are made if they must be)
					ServerLevel level = c.getSource().getServer().overworld();
					int n = 0;
					for (long ck : new ArrayList<>(CHUNKS.keySet())) {
						if (DONE.contains(ck)) continue;
						level.getChunk((int) (ck >> 32), (int) ck);
						layChunk(level, ck);
						n++;
					}
					int placed = 0;
					for (int k = 0; k < SPOTS.size(); k++) {
						if (SPOTS_DONE.contains(k)) continue;
						Spot s = SPOTS.get(k);
						level.getChunk(s.x() >> 4, s.z() >> 4);
						spot(level, s);
						SPOTS_DONE.add(k);
						placed++;
					}
					save();
					int fn = n, fp = placed;
					c.getSource().sendSuccess(() -> Component.literal("Laid " + fn + " road chunks, " + fp + " things beside them"), true);
					return 1;
				})).executes(c -> {
					long laid = CHUNKS.keySet().stream().filter(DONE::contains).count();
					c.getSource().sendSuccess(() -> Component.literal((planned ? "" : "(still working them out) ") + laid + "/" + CHUNKS.size() + " road chunks laid, "
							+ SPOTS_DONE.size() + "/" + SPOTS.size() + " things beside them"), false);
					for (String s : SUMMARY) c.getSource().sendSuccess(() -> Component.literal("  " + s), false);
					return 1;
				}))));
	}
}
