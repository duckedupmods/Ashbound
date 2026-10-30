package com.snoringwalrus.ashbound;

import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;
import java.util.zip.GZIPInputStream;

import com.mojang.brigadier.exceptions.CommandSyntaxException;

import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.blocks.BlockStateParser;
import net.minecraft.core.BlockPos;
import net.minecraft.util.Mth;
import net.minecraft.core.Holder;
import net.minecraft.core.QuartPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BiomeTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.biome.BiomeResolver;
import net.minecraft.world.level.biome.Biomes;
import net.minecraft.world.level.biome.Climate;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.material.FluidState;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.entity.living.FinalizeSpawnEvent;
import net.neoforged.neoforge.event.level.LevelEvent;

/**
 * Highmourn, the capital: one per world, a walled city in a valley 10,000-15,000 blocks from spawn
 * (tools/capital.py makes it: data/ashbound/capital/highmourn.bin).
 *
 * The file holds the land's shape round the city, column by column (a height over FLOOR, how it's shaped: cut and
 * filled to it, or only filled up to it, and how strongly), and the city's blocks. While the world's made, the
 * shape is sunk into the land's density (mixin.BeardifierMixin) and the surface rules are told where the ground now
 * is (mixin.NoiseChunkMixin), so the valley, the tiers and the cliffs are real terrain with grass and stone; then
 * each chunk's blocks are laid instead of its trees and flowers (mixin.ChunkGeneratorMixin), and no other structure
 * or cave is let in (structures, carvers).
 *
 * Out past the summits the shape eases back into the world's own land (the file's blend: the land's own heights are
 * sampled round the edge when the site's picked), so the mountains run on into the world instead of ending in a cut.
 *
 * Where it stands is worked out from the world's seed when the overworld loads, so it's the same every time.
 */
public final class Capital {
	private Capital() {}

	/** The valley floor's height: the file's heights are over this. */
	public static final int FLOOR = 72;
	private static final int CAPITAL_NEAR = 10000, CAPITAL_FAR = 15000;
	/** Villages go out this far every way from spawn, at most one to a SQUARE, kept SQUARE_EDGE in from its sides so two are never close. */
	private static final int RANGE = 20000, SQUARE = 1800, SQUARE_EDGE = 280, TRIES = 8, ROAD_ROUND_CITY = 3500, ROAD_LANE = 1400;
	/** For a name that's been used already. */
	private static final String[] TOWN_AGAIN = {"Old", "Upper", "Lower", "Far", "High", "Little", "West", "East", "North", "South"};
	private static final String[] TOWN_START = {"Ash", "Reed", "Mill", "Thorn", "Elder", "Stone", "Fen", "Hart", "Wren", "Oak", "Bram", "Cold", "Grey", "Harrow", "Kettle", "Lark",
			"Marrow", "Nettle", "Pale", "Rook", "Sorrow", "Tallow", "Under", "Wick"};
	private static final Map<String, String[]> TOWN_END = Map.of("lake", new String[] {"mere", "water"}, "hill", new String[] {"brae", "ton"}, "gorge", new String[] {"ford", "cleft"},
			"cliff", new String[] {"stair", "crag"}, "tree", new String[] {"hollow", "bough"}, "hold", new String[] {"gate", "hold"});
	/** Where to look for sites, by 256-block cells over the map, so the ground doesn't ask every village about every block. */
	private static final int CELL_BITS = 8, CELL_SPAN = (RANGE + 2048) >> CELL_BITS, CELLS = CELL_SPAN * 2;
	private static final Site[] NONE = new Site[0];
	private static volatile Site[][] cells;
	static final int CUT_FILL = 1, FILL = 2, CLEAR = 4, CLEAR_H = 72;
	/** Chunks round the city's shaped ground where no structure may start (their pieces reach this far). */
	static final int STRUCTURE_MARGIN = 7;

	/** The capital in the world being made, or null (no overworld loaded, or no data). */
	static volatile Site site;
	/** Every shaped place in the world being made: the capital, then the villages (tools/villages.py --export). */
	static volatile Site[] sites = new Site[0];
	/** The villages: each kind's file (data/ashbound/village/KIND.bin + .json). */
	static final java.util.List<String> VILLAGES = java.util.List.of("lake", "gorge", "hill", "cliff", "tree", "hold");

	static final class Data {
		int gx0, gz0, gw, gd;
		short[] height;
		/** blend: 0 our height .. 255 the world's own; biome: 0 keep the world's, else BIOMES[id - 1]. */
		byte[] mode, weight, blend, biome;
		BlockState[] palette;
		boolean[] flow;
		final Map<String, double[]> points = new HashMap<>();
		/** Relative chunk (cx, cz packed) -> its blocks: x&15 | z&15 << 4 | (y + 2048) << 8, and the palette index. */
		final Map<Long, int[][]> blocks = new HashMap<>();
		/** Relative chunk -> who stands in it (tools/capital_cast.py): kind, shop, mode, x, y, z in the city's frame. */
		final Map<Long, java.util.List<com.google.gson.JsonArray>> cast = new HashMap<>();
		/** Relative chunk -> the Blender props stood in it as block displays: model, x, y, z, yaw, scale. */
		final Map<Long, java.util.List<com.google.gson.JsonArray>> props = new HashMap<>();
	}

	static final class Site {
		final Data d;
		/** The city's centre (a chunk corner, so the file's chunks are the world's). */
		final int x, z;
		/** The world's height of the file's 0 (the capital's FLOOR; a village's ground where it stands). */
		final int floor;
		/** The kind of place: "highmourn", or a village's kind. */
		final String name;
		/** What it's called. */
		String title;
		/** Over the grid's chunks (cx - cx0, cz - cz0): 1 shaped, 2 cleared (owned), 4 has blocks, 8 no structures. */
		final byte[] chunkFlags;
		final int cx0, cz0, cw, cd;
		/** Each column's height once eased into the world's land round the edge (over FLOOR). */
		short[] eff;
		Holder<Biome>[] biomes;

		Site(Data d, int x, int z) {
			this(d, x, z, FLOOR, "highmourn", "Highmourn");
		}

		Site(Data d, int x, int z, int floor, String name, String title) {
			this.d = d;
			this.x = x;
			this.z = z;
			this.floor = floor;
			this.name = name;
			this.title = title;
			cx0 = Math.floorDiv(x + d.gx0, 16) - STRUCTURE_MARGIN;
			cz0 = Math.floorDiv(z + d.gz0, 16) - STRUCTURE_MARGIN;
			cw = d.gw / 16 + 2 * STRUCTURE_MARGIN + 2;
			cd = d.gd / 16 + 2 * STRUCTURE_MARGIN + 2;
			chunkFlags = new byte[cw * cd];
			for (int j = 0; j < d.gd; j++)
				for (int i = 0; i < d.gw; i++) {
					int k = j * d.gw + i;
					if (d.weight[k] == 0) continue;
					int ci = Math.floorDiv(x + d.gx0 + i, 16) - cx0, cj = Math.floorDiv(z + d.gz0 + j, 16) - cz0;
					chunkFlags[cj * cw + ci] |= 1;
					if ((d.mode[k] & CLEAR) != 0) chunkFlags[cj * cw + ci] |= 2;
				}
			for (long key : d.blocks.keySet()) {
				int ci = Math.floorDiv(x, 16) + ChunkPos.getX(key) - cx0, cj = Math.floorDiv(z, 16) + ChunkPos.getZ(key) - cz0;
				if (ci >= 0 && cj >= 0 && ci < cw && cj < cd) chunkFlags[cj * cw + ci] |= 4;
			}
			byte[] near = chunkFlags.clone();
			for (int j = 0; j < cd; j++)
				for (int i = 0; i < cw; i++) {
					if ((near[j * cw + i] & 1) == 0) continue;
					for (int dj = -STRUCTURE_MARGIN; dj <= STRUCTURE_MARGIN; dj++)
						for (int di = -STRUCTURE_MARGIN; di <= STRUCTURE_MARGIN; di++) {
							int a = i + di, b = j + dj;
							if (a >= 0 && b >= 0 && a < cw && b < cd) chunkFlags[b * cw + a] |= 8;
						}
				}
		}

		int flags(int cx, int cz) {
			int i = cx - cx0, j = cz - cz0;
			return i < 0 || j < 0 || i >= cw || j >= cd ? 0 : chunkFlags[j * cw + i];
		}

		/** The grid's index for world column x, z, or -1. */
		int column(int wx, int wz) {
			int i = wx - x - d.gx0, j = wz - z - d.gz0;
			return i < 0 || j < 0 || i >= d.gw || j >= d.gd ? -1 : j * d.gw + i;
		}
	}

	// ================================================================ the shaping (from the mixins)

	/** The sites that reach the 256-block cell this column's in. */
	static Site[] near(int x, int z) {
		Site[][] g = cells;
		int i = (x >> CELL_BITS) + CELL_SPAN, j = (z >> CELL_BITS) + CELL_SPAN;
		return g == null || i < 0 || j < 0 || i >= CELLS || j >= CELLS ? NONE : g[j * CELLS + i];
	}

	private static Site[][] index(Site[] all) {
		java.util.List<java.util.List<Site>> g = new java.util.ArrayList<>(java.util.Collections.nCopies(CELLS * CELLS, null));
		for (Site s : all)
			for (int j = (s.cz0 * 16 >> CELL_BITS) + CELL_SPAN; j <= ((s.cz0 + s.cd) * 16 >> CELL_BITS) + CELL_SPAN; j++)
				for (int i = (s.cx0 * 16 >> CELL_BITS) + CELL_SPAN; i <= ((s.cx0 + s.cw) * 16 >> CELL_BITS) + CELL_SPAN; i++) {
					if (i < 0 || j < 0 || i >= CELLS || j >= CELLS) continue;
					if (g.get(j * CELLS + i) == null) g.set(j * CELLS + i, new java.util.ArrayList<>());
					g.get(j * CELLS + i).add(s);
				}
		Site[][] out = new Site[CELLS * CELLS][];
		for (int k = 0; k < out.length; k++) out[k] = g.get(k) == null ? NONE : g.get(k).toArray(new Site[0]);
		return out;
	}

	/** Added to the land's density at x, y, z: + below the shaped ground, - above it where it's cut. */
	public static double shape(int x, int y, int z) {
		for (Site s : near(x, z)) {
			int k = s.column(x, z);
			if (k >= 0 && (s.d.weight[k] & 255) != 0) return shape(s, k, y);
		}
		return 0;
	}

	private static double shape(Site s, int k, int y) {
		int w = s.d.weight[k] & 255;
		int mode = s.d.mode[k] & 3;
		double t = s.floor + s.eff[k] + 0.5 - y;
		double v = Math.max(-40, Math.min(40, 2 * t));
		if (mode == FILL && v < 0) return 0;
		return v * (w / 255.0);
	}

	/** Where the ground now is, for the surface rules and the aquifers (raw: where the land alone would have it). */
	public static int surface(int x, int z, int raw) {
		for (Site s : near(x, z)) {
			int k = s.column(x, z);
			if (k >= 0 && (s.d.weight[k] & 255) != 0) return surface(s, k, raw);
		}
		return raw;
	}

	private static int surface(Site s, int k, int raw) {
		int w = s.d.weight[k] & 255;
		int t = s.floor + s.eff[k];
		int mode = s.d.mode[k] & 3;
		if (raw == Integer.MAX_VALUE) return t;
		int target = mode == FILL ? Math.max(raw, t) : t;
		return Math.round(raw + (target - raw) * (w / 255f));
	}

	/** The biomes of a chunk being made: the file's (meadows on the valley floor, forests up the slopes, rock on the
	 *  cliffs, snow on the tops), the world's own out round the edge. */
	public static BiomeResolver biomes(BiomeResolver resolver) {
		Site[] all = sites;
		if (all.length == 0 || all[0].biomes == null) return resolver;
		return (qx, qy, qz, sampler) -> {
			int bx = QuartPos.toBlock(qx) + 2, bz = QuartPos.toBlock(qz) + 2;
			for (Site s : near(bx, bz)) {
				int k = s.column(bx, bz);
				int b = k < 0 ? 0 : s.d.biome[k] & 255;
				if (b > 0 && s.biomes != null && b <= s.biomes.length) return s.biomes[b - 1];
			}
			return resolver.getNoiseBiome(qx, qy, qz, sampler);
		};
	}

	private static int flags(ChunkPos cp) {
		int f = 0;
		for (Site s : near(cp.getMinBlockX(), cp.getMinBlockZ())) f |= s.flags(cp.x, cp.z);
		return f;
	}

	/** The file's biome ids, 1 up. */
	@SuppressWarnings("unchecked")
	private static final net.minecraft.resources.ResourceKey<Biome>[] BIOME_IDS = new net.minecraft.resources.ResourceKey[] {
			Biomes.PLAINS, Biomes.MEADOW, Biomes.FOREST, Biomes.CHERRY_GROVE, Biomes.GROVE, Biomes.SNOWY_SLOPES, Biomes.STONY_PEAKS,
			Biomes.FLOWER_FOREST, Biomes.JAGGED_PEAKS};

	/** No structure starts here: the city and the land round it are its own. */
	public static boolean blocksStructures(ChunkPos cp) {
		return (flags(cp) & 8) != 0;
	}

	/** The city's chunk: its own blocks instead of trees and flowers, and no caves cut into it. */
	public static boolean owns(ChunkPos cp) {
		return (flags(cp) & 2) != 0;
	}

	public static boolean hasBlocks(ChunkPos cp) {
		return (flags(cp) & 4) != 0;
	}

	// ================================================================ laying the city

	/** Turfs the city's ground where the cut left bare rock, then lays the chunk's blocks. */
	public static void place(WorldGenLevel level, ChunkAccess chunk) {
		ChunkPos cp = chunk.getPos();
		for (Site s : near(cp.getMinBlockX(), cp.getMinBlockZ()))
			if ((s.flags(cp.x, cp.z) & 6) != 0) place(s, level, chunk);
	}

	private static void place(Site s, WorldGenLevel level, ChunkAccess chunk) {
		ChunkPos cp = chunk.getPos();
		BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos();
		if ((s.flags(cp.x, cp.z) & 2) != 0)
			for (int dz = 0; dz < 16; dz++)
				for (int dx = 0; dx < 16; dx++) {
					int wx = cp.getMinBlockX() + dx, wz = cp.getMinBlockZ() + dz, k = s.column(wx, wz);
					if (k < 0 || (s.d.mode[k] & CLEAR) == 0) continue;
					int t = s.floor + s.eff[k];
					// where land was cut off over it, the ground's bare rock: turf it
					p.set(wx, t, wz);
					if (bare(chunk.getBlockState(p))) {
						level.setBlock(p, Blocks.GRASS_BLOCK.defaultBlockState(), 2);
						for (int y = t - 1; y >= t - 3; y--) {
							p.set(wx, y, wz);
							if (bare(chunk.getBlockState(p))) level.setBlock(p, Blocks.DIRT.defaultBlockState(), 2);
						}
					}
				}
		long rel = ChunkPos.asLong(cp.x - Math.floorDiv(s.x, 16), cp.z - Math.floorDiv(s.z, 16));
		int[][] b = s.d.blocks.get(rel);
		if (b != null) lay(s, level, chunk, b);
		// the townsfolk who live here, stood in once their floor is down
		var folk = s.d.cast.get(rel);
		if (folk != null)
			for (var e : folk) {
				double x = s.x + e.get(3).getAsInt() + 0.5, y = s.floor + e.get(4).getAsInt(), z = s.z + e.get(5).getAsInt() + 0.5;
				// the land's own rise can leave the ground a block or two over the file's: stand on what's really there
				BlockPos.MutableBlockPos at = new BlockPos.MutableBlockPos(Mth.floor(x), (int) y, Mth.floor(z));
				int up = 0;                                     // (those put on a seat are in it: leave them there)
				while (up <= 3 && !e.get(2).getAsString().equals("sit") && (blocks(level, at) || blocks(level, at.above()))) {
					at.move(0, 1, 0);
					up++;
				}
				if (up > 3) continue;
				y += up;
				float yaw = e.size() > 6 ? e.get(6).getAsFloat() : (float) Math.floorMod((long) (x * 31 + z * 17), 360);
				Talk.spawn(level, e.get(0).getAsString(), e.get(1).getAsString(), e.get(2).getAsString(), x, y, z, yaw);
			}
		var props = s.d.props.get(rel);
		if (props != null)
			for (var e : props) display(level, s, e);
	}

	private static boolean blocks(WorldGenLevel level, BlockPos p) {
		return !level.getBlockState(p).getCollisionShape(level, p).isEmpty() || !level.getFluidState(p).isEmpty();
	}

	/** A Blender prop stood in as a block display: any turn, any size, no hitbox. */
	private static void display(WorldGenLevel level, Site s, com.google.gson.JsonArray e) {
		var block = BuiltInRegistries.BLOCK.get(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, e.get(0).getAsString()));
		if (block == Blocks.AIR) return;
		var d = net.minecraft.world.entity.EntityType.BLOCK_DISPLAY.create(level.getLevel());
		if (d == null) return;
		float yaw = (float) Math.toRadians(e.get(4).getAsDouble()), sc = e.get(5).getAsFloat();
		net.minecraft.nbt.CompoundTag t = new net.minecraft.nbt.CompoundTag(), tr = new net.minecraft.nbt.CompoundTag();
		t.put("block_state", net.minecraft.nbt.NbtUtils.writeBlockState(block.defaultBlockState()));
		tr.put("left_rotation", floats(0, (float) Math.sin(yaw / 2), 0, (float) Math.cos(yaw / 2)));
		tr.put("right_rotation", floats(0, 0, 0, 1));
		tr.put("translation", floats(0, 0, 0));
		tr.put("scale", floats(sc, sc, sc));
		t.put("transformation", tr);
		t.putFloat("view_range", e.size() > 6 ? e.get(6).getAsFloat() : 2.5f);   // small props drawn only near (villages.py sizes it)
		d.load(t);
		d.moveTo(s.x + e.get(1).getAsDouble(), s.floor + e.get(2).getAsDouble(), s.z + e.get(3).getAsDouble(), 0, 0);
		level.addFreshEntity(d);
	}

	private static net.minecraft.nbt.ListTag floats(float... v) {
		net.minecraft.nbt.ListTag l = new net.minecraft.nbt.ListTag();
		for (float f : v) l.add(net.minecraft.nbt.FloatTag.valueOf(f));
		return l;
	}

	private static void lay(Site s, WorldGenLevel level, ChunkAccess chunk, int[][] b) {
		ChunkPos cp = chunk.getPos();
		BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos();
		int[] where = b[0], what = b[1];
		for (int i = 0; i < where.length; i++) {
			int v = where[i];
			p.set(cp.getMinBlockX() + (v & 15), s.floor + (v >> 8) - 2048, cp.getMinBlockZ() + ((v >> 4) & 15));
			BlockState st = s.d.palette[what[i]];
			level.setBlock(p, st, 2);
			if (s.d.flow[what[i]]) {
				FluidState f = st.getFluidState();
				if (!f.isEmpty()) level.scheduleTick(p.immutable(), f.getType(), 1);
			}
		}
	}

	private static boolean bare(BlockState st) {
		return st.is(Blocks.STONE) || st.is(Blocks.DEEPSLATE) || st.is(Blocks.ANDESITE) || st.is(Blocks.DIORITE) || st.is(Blocks.GRANITE)
				|| st.is(Blocks.TUFF) || st.is(Blocks.GRAVEL) || st.is(Blocks.CALCITE) || st.is(Blocks.SNOW_BLOCK) || st.is(Blocks.POWDER_SNOW);
	}

	// ================================================================ the data, and where it goes

	static Data data;

	static Data load() {
		if (data != null) return data;
		return data = read("/data/ashbound/capital/highmourn.bin", "/data/ashbound/capital/cast.json", null);
	}

	static final Map<String, Data> VILLAGE_DATA = new HashMap<>();

	/** A kind's layouts (tools/villages.py exports KIND, KIND_2, KIND_3...): the same village made over, so a world's two
	 *  of a kind aren't twins. */
	static java.util.List<String> layouts(String kind) {
		java.util.List<String> out = new java.util.ArrayList<>();
		for (int i = 1; i <= 9; i++) {
			String n = i == 1 ? kind : kind + "_" + i;
			if (Capital.class.getResource("/data/ashbound/village/" + n + ".bin") != null) out.add(n);
		}
		return out;
	}

	static Data village(String kind) {
		return VILLAGE_DATA.computeIfAbsent(kind, k -> read("/data/ashbound/village/" + k + ".bin", "/data/ashbound/village/" + k + "_cast.json",
				"/data/ashbound/village/" + k + ".json"));
	}

	private static Data read(String path, String castPath, String propsPath) {
		try (InputStream raw = Capital.class.getResourceAsStream(path)) {
			if (raw == null) return null;
			DataInputStream in = new DataInputStream(new GZIPInputStream(raw, 1 << 16));
			byte[] magic = new byte[4];
			in.readFully(magic);
			if (!new String(magic).equals("CAPT")) throw new IOException("not a capital file");
			int version = in.readInt();
			if (version != 2) throw new IOException("capital file version " + version + ", want 2");
			Data d = new Data();
			d.gx0 = in.readInt();
			d.gz0 = in.readInt();
			d.gw = in.readInt();
			d.gd = in.readInt();
			int n = d.gw * d.gd;
			d.height = new short[n];
			for (int i = 0; i < n; i++) d.height[i] = in.readShort();
			d.mode = new byte[n];
			in.readFully(d.mode);
			d.weight = new byte[n];
			in.readFully(d.weight);
			d.blend = new byte[n];
			in.readFully(d.blend);
			d.biome = new byte[n];
			in.readFully(d.biome);
			int np = in.readInt();
			d.palette = new BlockState[np];
			d.flow = new boolean[np];
			for (int i = 0; i < np; i++) {
				String st = in.readUTF();
				if (st.endsWith("#flow")) {
					d.flow[i] = true;
					st = st.substring(0, st.length() - 5);
				}
				try {
					d.palette[i] = BlockStateParser.parseForBlock(BuiltInRegistries.BLOCK.asLookup(), st, false).blockState();
				} catch (CommandSyntaxException e) {
					Ashbound.LOG.warn("capital: unknown block {}", st);
					d.palette[i] = Blocks.AIR.defaultBlockState();
				}
			}
			int npt = in.readInt();
			for (int i = 0; i < npt; i++) d.points.put(in.readUTF(), new double[] {in.readDouble(), in.readDouble(), in.readDouble()});
			int nb = in.readInt();
			Map<Long, int[]> count = new HashMap<>();
			short[] xs = new short[nb], ys = new short[nb], zs = new short[nb];
			char[] is = new char[nb];
			for (int i = 0; i < nb; i++) {
				xs[i] = in.readShort();
				ys[i] = in.readShort();
				zs[i] = in.readShort();
				is[i] = in.readChar();
				count.computeIfAbsent(ChunkPos.asLong(xs[i] >> 4, zs[i] >> 4), k -> new int[1])[0]++;
			}
			Map<Long, int[]> fill = new HashMap<>();
			for (Map.Entry<Long, int[]> e : count.entrySet()) {
				d.blocks.put(e.getKey(), new int[][] {new int[e.getValue()[0]], new int[e.getValue()[0]]});
				fill.put(e.getKey(), new int[1]);
			}
			for (int i = 0; i < nb; i++) {
				long key = ChunkPos.asLong(xs[i] >> 4, zs[i] >> 4);
				int[][] b = d.blocks.get(key);
				int j = fill.get(key)[0]++;
				b[0][j] = (xs[i] & 15) | (zs[i] & 15) << 4 | (ys[i] + 2048) << 8;
				b[1][j] = is[i];
			}
			Ashbound.LOG.info("{}: {} blocks over {} chunks, ground {}x{}", path, nb, d.blocks.size(), d.gw, d.gd);
			if (propsPath != null)
				try (InputStream c = Capital.class.getResourceAsStream(propsPath)) {
					if (c != null)
						for (var e : com.google.gson.JsonParser.parseReader(new java.io.InputStreamReader(c, java.nio.charset.StandardCharsets.UTF_8))
								.getAsJsonObject().getAsJsonArray("props")) {
							var a = e.getAsJsonArray();
							d.props.computeIfAbsent(ChunkPos.asLong(Math.floorDiv((int) Math.floor(a.get(1).getAsDouble()), 16),
									Math.floorDiv((int) Math.floor(a.get(3).getAsDouble()), 16)), k -> new java.util.ArrayList<>()).add(a);
						}
				}
			if (castPath != null) try (InputStream c = Capital.class.getResourceAsStream(castPath)) {
				if (c != null) {
					var all = com.google.gson.JsonParser.parseReader(new java.io.InputStreamReader(c, java.nio.charset.StandardCharsets.UTF_8)).getAsJsonArray();
					for (var e : all) {
						var a = e.getAsJsonArray();
						d.cast.computeIfAbsent(ChunkPos.asLong(a.get(3).getAsInt() >> 4, a.get(5).getAsInt() >> 4), k -> new java.util.ArrayList<>()).add(a);
					}
					Ashbound.LOG.info("{}: {} townsfolk", castPath, all.size());
				}
			}
			return d;
		} catch (IOException e) {
			Ashbound.LOG.error("couldn't read " + path, e);
			return null;
		}
	}

	/** Where in this world it stands: of a few spots 10,000-15,000 out, the one with the most land round it. */
	static Site choose(ServerLevel level, Data d) {
		ChunkGenerator gen = level.getChunkSource().getGenerator();
		Climate.Sampler sampler = level.getChunkSource().randomState().sampler();
		RandomSource r = RandomSource.create(level.getSeed() ^ 0x4869676D6F75726EL);
		int bestX = 0, bestZ = CAPITAL_NEAR, best = -1;
		for (int tries = 0; tries < 40; tries++) {
			double a = r.nextDouble() * Math.PI * 2, dist = CAPITAL_NEAR + r.nextDouble() * (CAPITAL_FAR - CAPITAL_NEAR);
			int x = Math.floorDiv((int) (Math.cos(a) * dist), 16) * 16, z = Math.floorDiv((int) (Math.sin(a) * dist), 16) * 16;
			int land = 0;
			for (int i = -4; i <= 4; i++)
				for (int j = -4; j <= 4; j++) {
					int sx = x + i * 70, sz = z + j * 70;
					Holder<Biome> b = gen.getBiomeSource().getNoiseBiome(QuartPos.fromBlock(sx), QuartPos.fromBlock(FLOOR), QuartPos.fromBlock(sz), sampler);
					if (!b.is(BiomeTags.IS_OCEAN) && !b.is(BiomeTags.IS_DEEP_OCEAN) && !b.is(BiomeTags.IS_RIVER) && !b.is(BiomeTags.IS_BEACH))
						land += (Math.abs(i) <= 2 && Math.abs(j) <= 2) ? 3 : 1;
				}
			if (land > best) {
				best = land;
				bestX = x;
				bestZ = z;
			}
		}
		Ashbound.LOG.info("capital: Highmourn at {}, {} (land {})", bestX, bestZ, best);
		Site s = new Site(d, bestX, bestZ);
		ease(level, s);
		return s;
	}

	/** The site's heights eased into the world's land round its edge: the land's own height (sampled every 16 blocks
	 *  where the file blends, between them bilinear) taken in by each column's blend. Run before the site's live, so the
	 *  samples are the untouched world's. */
	/**
	 * The villages, scattered over the whole map: the map's cut into squares, each gets at most one, somewhere random in it,
	 * of a random kind, on land that's not too broken. A square's own seed decides it, so they can all be worked out at once.
	 */
	static java.util.List<Site> villages(ServerLevel level, Site capital) {
		long t0 = System.currentTimeMillis();
		for (String kind : VILLAGES) for (String l : layouts(kind)) village(l);
		int n = RANGE * 2 / SQUARE;
		java.util.List<Site> out = java.util.stream.IntStream.range(0, n * n).parallel().mapToObj(k -> square(level, capital, k % n, k / n))
				.filter(java.util.Objects::nonNull).toList();
		java.util.Set<String> taken = new java.util.HashSet<>();
		for (Site s : out)
			for (int k = 0; !taken.add(s.title); k++) s.title = TOWN_AGAIN[k % TOWN_AGAIN.length] + " " + s.title.substring(s.title.lastIndexOf(' ') + 1);
		Ashbound.LOG.info("villages: {} over the map in {} ms", out.size(), System.currentTimeMillis() - t0);
		return out;
	}

	private static Site square(ServerLevel level, Site capital, int si, int sj) {
		RandomSource r = RandomSource.create(level.getSeed() ^ 0x56696C6C61676573L ^ (si * 341873128712L + sj * 132897987541L));
		ChunkGenerator gen = level.getChunkSource().getGenerator();
		Climate.Sampler sampler = level.getChunkSource().randomState().sampler();
		var random = level.getChunkSource().randomState();
		String kind = VILLAGES.get(r.nextInt(VILLAGES.size()));
		java.util.List<String> ls = layouts(kind);
		if (ls.isEmpty()) return null;
		Data d = village(ls.get(r.nextInt(ls.size())));
		if (d == null) return null;
		String title = TOWN_START[r.nextInt(TOWN_START.length)] + TOWN_END.get(kind)[r.nextInt(2)];
		for (int tries = 0; tries < TRIES; tries++) {
			int x = Math.floorDiv(-RANGE + si * SQUARE + SQUARE_EDGE + r.nextInt(SQUARE - 2 * SQUARE_EDGE), 16) * 16;
			int z = Math.floorDiv(-RANGE + sj * SQUARE + SQUARE_EDGE + r.nextInt(SQUARE - 2 * SQUARE_EDGE), 16) * 16;
			if (Math.hypot(x, z) < 500 || capital != null && Math.hypot(x - capital.x, z - capital.z) < 900) continue;
			int lo = Integer.MAX_VALUE, hi = Integer.MIN_VALUE;
			boolean wet = false;
			for (int i = -1; i <= 1 && !wet; i++)
				for (int j = -1; j <= 1; j++) {
					int sx = x + i * 90, sz = z + j * 90;
					Holder<Biome> b = gen.getBiomeSource().getNoiseBiome(QuartPos.fromBlock(sx), QuartPos.fromBlock(70), QuartPos.fromBlock(sz), sampler);
					if (b.is(BiomeTags.IS_OCEAN) || b.is(BiomeTags.IS_DEEP_OCEAN) || b.is(BiomeTags.IS_RIVER) || b.is(BiomeTags.IS_BEACH)) {
						wet = true;
						break;
					}
					int h = gen.getBaseHeight(sx, sz, net.minecraft.world.level.levelgen.Heightmap.Types.OCEAN_FLOOR_WG, level, random);
					lo = Math.min(lo, h);
					hi = Math.max(hi, h);
				}
			if (wet || hi - lo > 45 || lo < 64) continue;
			Site s = new Site(d, x, z, Math.max(64, Math.min(130, (lo + hi) / 2 - 1)), kind, title);
			ease(level, s);
			return s;
		}
		return null;
	}

	/** The places on the road network: the capital, the villages round it, and those along the way there from spawn. */
	private static Site[] onRoads(java.util.List<Site> all, Site cap) {
		if (cap == null) return new Site[0];
		double len = Math.hypot(cap.x, cap.z);
		java.util.List<Site> out = new java.util.ArrayList<>();
		for (Site s : all) {
			double along = Math.max(0, Math.min(1, (s.x * cap.x + s.z * cap.z) / (len * len)));
			if (s == cap || Math.hypot(s.x - cap.x, s.z - cap.z) < ROAD_ROUND_CITY || Math.hypot(s.x - cap.x * along, s.z - cap.z * along) < ROAD_LANE) out.add(s);
		}
		return out.toArray(new Site[0]);
	}

	static void ease(ServerLevel level, Site s) {
		long t0 = System.nanoTime();
		Data d = s.d;
		int sw = d.gw / 16 + 2, sd = d.gd / 16 + 2;
		boolean[] need = new boolean[sw * sd];
		for (int j = 0; j < d.gd; j++)
			for (int i = 0; i < d.gw; i++)
				if (d.blend[j * d.gw + i] != 0) {
					int ci = i / 16, cj = j / 16;
					need[cj * sw + ci] = need[cj * sw + ci + 1] = need[(cj + 1) * sw + ci] = need[(cj + 1) * sw + ci + 1] = true;
				}
		int[] v = new int[sw * sd];
		ChunkGenerator gen = level.getChunkSource().getGenerator();
		var random = level.getChunkSource().randomState();
		int[] count = new int[1];
		java.util.stream.IntStream.range(0, sw * sd).parallel().forEach(k -> {
			if (!need[k]) return;
			int wx = s.x + d.gx0 + (k % sw) * 16, wz = s.z + d.gz0 + (k / sw) * 16;
			v[k] = gen.getBaseHeight(wx, wz, net.minecraft.world.level.levelgen.Heightmap.Types.OCEAN_FLOOR_WG, level, random) - 1;
		});
		s.eff = d.height.clone();
		for (int j = 0; j < d.gd; j++)
			for (int i = 0; i < d.gw; i++) {
				int k = j * d.gw + i, b = d.blend[k] & 255;
				if (b == 0) continue;
				int ci = i / 16, cj = j / 16;
				double fx = (i % 16) / 16.0, fz = (j % 16) / 16.0;
				double a = v[cj * sw + ci] + (v[cj * sw + ci + 1] - v[cj * sw + ci]) * fx;
				double c = v[(cj + 1) * sw + ci] + (v[(cj + 1) * sw + ci + 1] - v[(cj + 1) * sw + ci]) * fx;
				double world = a + (c - a) * fz - s.floor;
				s.eff[k] = (short) Math.round(d.height[k] + (world - d.height[k]) * (b / 255.0));
				count[0]++;
			}
		Ashbound.LOG.debug("capital: eased {} columns into the land round it in {} ms", count[0], (System.nanoTime() - t0) / 1_000_000);
	}

	static void register() {
		NeoForge.EVENT_BUS.addListener((LevelEvent.Load e) -> {
			if (e.getLevel() instanceof ServerLevel l && l.dimension() == Level.OVERWORLD) {
				Data d = load();
				Site cap = d == null ? null : choose(l, d);
				java.util.List<Site> all = new java.util.ArrayList<>();
				if (cap != null) all.add(cap);
				all.addAll(villages(l, cap));
				var reg = l.registryAccess().registryOrThrow(Registries.BIOME);
				@SuppressWarnings("unchecked")
				Holder<Biome>[] hs = new Holder[BIOME_IDS.length];
				for (int i = 0; i < hs.length; i++) hs[i] = reg.getHolderOrThrow(BIOME_IDS[i]);
				for (Site s : all) s.biomes = hs;
				site = cap;
				cells = index(all.toArray(new Site[0]));
				sites = all.toArray(new Site[0]);
				Roads.plan(l, onRoads(all, cap));
			}
		});
		NeoForge.EVENT_BUS.addListener((LevelEvent.Unload e) -> {
			if (e.getLevel() instanceof ServerLevel l && l.dimension() == Level.OVERWORLD) {
				site = null;
				cells = null;
				sites = new Site[0];
			}
		});
		NeoForge.EVENT_BUS.addListener(Capital::noMonsters);
		NeoForge.EVENT_BUS.addListener((RegisterCommandsEvent e) -> e.getDispatcher().register(Commands.literal("ashbound")
				.requires(c -> c.hasPermission(2))
				.then(Commands.literal("capital").executes(c -> tp(c.getSource())))
				.then(Commands.literal("village").then(Commands.argument("kind", com.mojang.brigadier.arguments.StringArgumentType.word())
						.suggests((c, b) -> net.minecraft.commands.SharedSuggestionProvider.suggest(VILLAGES, b))
						.executes(c -> village(c.getSource(), com.mojang.brigadier.arguments.StringArgumentType.getString(c, "kind"), 0))
						.then(Commands.argument("n", com.mojang.brigadier.arguments.IntegerArgumentType.integer(1, 9))
								.executes(c -> village(c.getSource(), com.mojang.brigadier.arguments.StringArgumentType.getString(c, "kind"),
										com.mojang.brigadier.arguments.IntegerArgumentType.getInteger(c, "n"))))))));
	}

	/** No monster comes of itself into the city or the land round it (its shaped ground and the margin past it):
	 *  not by night, not from a spawner or a patrol. One summoned by a player (egg, command) still comes. */
	private static void noMonsters(FinalizeSpawnEvent e) {
		if (sites.length == 0 || e.getLevel().getLevel().dimension() != Level.OVERWORLD) return;
		if (!(e.getEntity() instanceof Enemy) && e.getEntity().getType().getCategory() != MobCategory.MONSTER) return;
		MobSpawnType t = e.getSpawnType();
		if (t == MobSpawnType.SPAWN_EGG || t == MobSpawnType.COMMAND || t == MobSpawnType.BUCKET || t == MobSpawnType.DISPENSER) return;
		if ((flags(new ChunkPos(net.minecraft.util.Mth.floor(e.getX()) >> 4, net.minecraft.util.Mth.floor(e.getZ()) >> 4)) & 8) != 0) e.setSpawnCancelled(true);
	}

	private static int tp(CommandSourceStack src) {
		Site s = site;
		if (s == null) {
			src.sendFailure(Component.literal("No capital in this world."));
			return 0;
		}
		double[] g = s.d.points.get("gate");
		ServerLevel l = src.getServer().overworld();
		src.getEntity().teleportTo(l, s.x + g[0], FLOOR + g[1], s.z + g[2], java.util.Set.of(), 180, 0);
		src.sendSuccess(() -> Component.literal("Highmourn, at " + s.x + ", " + s.z), false);
		return 1;
	}

	/** /ashbound village KIND [N]: to that kind's Nth village (in the order the world placed them), or with no N the
	 *  nearest one you're not already in; at its way in. */
	private static int village(CommandSourceStack src, String kind, int n) {
		java.util.List<Site> all = new java.util.ArrayList<>();
		for (Site s : sites)
			if (s.name.equals(kind)) all.add(s);
		if (all.isEmpty()) {
			src.sendFailure(Component.literal("No " + kind + " village in this world."));
			return 0;
		}
		var at = src.getPosition();
		Site best = null;
		if (n > 0) {
			if (n > all.size()) {
				src.sendFailure(Component.literal("This world has " + all.size() + " " + kind + " village" + (all.size() == 1 ? "." : "s.")));
				return 0;
			}
			best = all.get(n - 1);
		} else {
			for (int pass = 0; pass < 2 && best == null; pass++)          // pass 0 passes over the one you're in
				for (Site s : all)
					if ((pass == 1 || Math.hypot(s.x - at.x, s.z - at.z) > 200)
							&& (best == null || Math.hypot(s.x - at.x, s.z - at.z) < Math.hypot(best.x - at.x, best.z - at.z))) best = s;
		}
		Site s = best;
		int k = all.indexOf(s) + 1;
		double[] g = s.d.points.getOrDefault("centre", new double[] {0, 1, 0});
		src.getEntity().teleportTo(src.getServer().overworld(), s.x + g[0], s.floor + g[1], s.z + g[2], java.util.Set.of(), 180, 0);
		src.sendSuccess(() -> Component.literal("The " + kind + " village " + k + " of " + all.size() + ", at " + s.x + ", " + s.z), false);
		return 1;
	}

	/** For the pregen test: the city's centre. */
	static int[] centre() {
		Site s = site;
		return s == null ? null : new int[] {s.x, s.z};
	}
}
