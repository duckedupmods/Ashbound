package com.snoringwalrus.ashbound;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;

import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.SharedSuggestionProvider;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.QuartPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.WorldGenRegion;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.FeatureConfiguration;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructurePiece;
import net.minecraft.world.level.levelgen.structure.StructureType;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceSerializationContext;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType;
import net.minecraft.world.level.levelgen.structure.templatesystem.BlockIgnoreProcessor;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructurePlaceSettings;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureProcessor;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureProcessorType;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplate;
import net.minecraft.world.phys.Vec3;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * Our trees in place of vanilla's (made by E:/Ashbound's tools/forest.py and tools/trees.py, brought over by
 * tools/port_world.py): every tree is a template (data/ashbound/structure/tree/NAME.nbt) stood with its trunk on the
 * ground, turned any of four ways; where its trunk sits in the template is in data/ashbound/tree/offsets.json.
 *
 *   - TreeFeature ("ashbound:tree"): a weighted pick of templates. data/ashbound/worldgen/configured_feature holds
 *     the mixes (oak, forest, birch, gloom, pine...); vanilla's per-biome tree placements and the features its
 *     saplings grow are swapped for ours in data/minecraft/worldgen (so forests, and planted saplings, grow ours).
 *   - GiantTree ("ashbound:giant_tree"): the Elder Warden, the Pale Weeper, the Burned Colossus and the wildwood's
 *     highwoods, too big for a feature, so a structure laid down a chunk at a time.
 *
 * `/ashbound tree NAME` stands one where you are (oak_large_0, elder...).
 */
public final class Trees {
	private Trees() {}

	private static final Map<String, BlockPos> OFFSETS = new ConcurrentHashMap<>();

	/** Where the trunk's foot is in the tree's template (null: no such tree). */
	static BlockPos offset(ResourceLocation template) {
		if (OFFSETS.isEmpty()) {
			try (InputStream in = Trees.class.getResourceAsStream("/data/ashbound/tree/offsets.json")) {
				JsonObject o = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
				for (var e : o.entrySet()) {
					JsonArray a = e.getValue().getAsJsonArray();
					OFFSETS.put(e.getKey(), new BlockPos(a.get(0).getAsInt(), a.get(1).getAsInt(), a.get(2).getAsInt()));
				}
			} catch (Exception e) {
				Ashbound.LOG.error("tree offsets won't load", e);
			}
		}
		String path = template.getPath();
		return OFFSETS.get(path.substring(path.lastIndexOf('/') + 1));
	}

	/** Stand a tree with its trunk's foot at `ground` (the ground block), the part of it inside `box` (null: all). */
	static boolean put(WorldGenLevel level, ResourceLocation template, BlockPos ground, Rotation rot, BoundingBox box, RandomSource random) {
		BlockPos off = offset(template);
		Optional<StructureTemplate> t = level.getLevel().getStructureManager().get(template);
		if (off == null || t.isEmpty()) {
			Ashbound.LOG.error("no tree {}", template);
			return false;
		}
		StructurePlaceSettings settings = settings(off, rot);
		if (box != null) settings.setBoundingBox(box);
		BlockPos corner = ground.subtract(off);
		boolean ok = t.get().placeInWorld(level, corner, corner, settings, random, Block.UPDATE_CLIENTS);
		if (ok) roots(level, t.get().getBoundingBox(settings, corner), ground.getY(), box);
		return ok;
	}

	/** Natural ground in a template (a tree's mossy foot, a ruin's patch of bank). */
	static boolean soil(BlockState s) {
		return s.is(Blocks.GRASS_BLOCK) || s.is(Blocks.DIRT) || s.is(Blocks.COARSE_DIRT) || s.is(Blocks.PODZOL) || s.is(Blocks.ROOTED_DIRT)
				|| s.is(Blocks.MOSS_BLOCK) || s.is(Blocks.DIRT_PATH) || s.is(Blocks.MUD) || s.is(Blocks.MYCELIUM);
	}

	/**
	 * A template's ground only where there's land to lay it on: over air or water (the bank lower than the
	 * template thought, a cliff's edge) it's left out, so no slab of turf hangs in the air.
	 */
	static final class OnLand extends StructureProcessor {
		static final OnLand INSTANCE = new OnLand();
		static final MapCodec<OnLand> CODEC = MapCodec.unit(INSTANCE);

		@Override
		public StructureTemplate.StructureBlockInfo processBlock(LevelReader level, BlockPos a, BlockPos b, StructureTemplate.StructureBlockInfo raw,
				StructureTemplate.StructureBlockInfo info, StructurePlaceSettings settings) {
			if (info == null || !soil(info.state())) return info;
			BlockPos p = info.pos();
			BoundingBox box = settings.getBoundingBox();
			if (box != null && !box.isInside(p)) return info;      // not laid here: the world past the box isn't ours to read
			if (land(level.getBlockState(p)) || land(level.getBlockState(p.below()))) return info;
			return null;
		}

		private static boolean land(BlockState s) {
			return !s.isAir() && s.getFluidState().isEmpty() && !s.canBeReplaced() && !s.is(BlockTags.LEAVES) && !s.is(BlockTags.LOGS);
		}

		@Override
		protected StructureProcessorType<?> getType() {
			return ON_LAND.get();
		}
	}

	/**
	 * A tree stood at a drop's edge (a cliff, a bank) has the foot of its trunk and its root flare out over the air:
	 * every wood block of its lowest layers with nothing under it sends a root down to the ground, so it clings to the
	 * edge instead of hanging off it; one that doesn't reach ends in hanging roots.
	 */
	private static void roots(WorldGenLevel level, BoundingBox tb, int foot, BoundingBox box) {
		int xa = tb.minX(), xb = tb.maxX(), za = tb.minZ(), zb = tb.maxZ();
		if (box != null) {
			xa = Math.max(xa, box.minX());
			xb = Math.min(xb, box.maxX());
			za = Math.max(za, box.minZ());
			zb = Math.min(zb, box.maxZ());
		}
		BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos();
		for (int x = xa; x <= xb; x++)
			for (int z = za; z <= zb; z++)
				for (int y = Math.max(tb.minY(), foot - 2); y <= foot + 2; y++) {
					BlockState s = level.getBlockState(p.set(x, y, z));
					if (!s.is(BlockTags.LOGS)) continue;
					BlockState under = level.getBlockState(p.set(x, y - 1, z));
					if (!under.isAir() && !under.canBeReplaced()) continue;
					BlockState root = s.hasProperty(RotatedPillarBlock.AXIS) ? s.setValue(RotatedPillarBlock.AXIS, Direction.Axis.Y) : s;
					int yy = y - 1, n = 0;
					for (; n < 28 && yy > level.getMinBuildHeight(); yy--, n++) {
						BlockState t = level.getBlockState(p.set(x, yy, z));
						if (!t.isAir() && !t.canBeReplaced() || !t.getFluidState().isEmpty()) break;
						level.setBlock(p, root, Block.UPDATE_CLIENTS);
					}
					if (n == 28 && level.getBlockState(p.set(x, yy, z)).isAir())
						level.setBlock(p, Blocks.HANGING_ROOTS.defaultBlockState(), Block.UPDATE_CLIENTS);
				}
	}

	private static StructurePlaceSettings settings(BlockPos off, Rotation rot) {
		// a tree's air is nothing: it doesn't clear what stood round it
		return new StructurePlaceSettings().setRotation(rot).setRotationPivot(new BlockPos(off.getX(), 0, off.getZ()))
				.setIgnoreEntities(true).setKnownShape(true).addProcessor(BlockIgnoreProcessor.STRUCTURE_AND_AIR)
				.addProcessor(OnLand.INSTANCE);
	}

	/** While the world's being made, a feature may only touch its own chunk and the ring round it. */
	private static BoundingBox writable(WorldGenLevel level) {
		if (!(level instanceof WorldGenRegion r)) return null;
		ChunkPos c = r.getCenter();
		// one block in from the ring's edge: placing a block looks at its neighbours, which mustn't be past it
		return new BoundingBox(c.getMinBlockX() - 15, level.getMinBuildHeight(), c.getMinBlockZ() - 15,
				c.getMaxBlockX() + 15, level.getMaxBuildHeight(), c.getMaxBlockZ() + 15);
	}

	// ================================================================ the forests

	public record Entry(ResourceLocation template, int weight) {
		static final Codec<Entry> CODEC = RecordCodecBuilder.create(i -> i.group(
				ResourceLocation.CODEC.fieldOf("template").forGetter(Entry::template),
				Codec.INT.optionalFieldOf("weight", 1).forGetter(Entry::weight)
		).apply(i, Entry::new));
	}

	/** Which trees a forest grows; `hardy`: on any solid ground (a swamp's mud under the water, the badlands' sand), not only a sapling's. */
	public record Mix(List<Entry> trees, boolean hardy) implements FeatureConfiguration {
		public static final Codec<Mix> CODEC = RecordCodecBuilder.create(i -> i.group(
				Entry.CODEC.listOf().fieldOf("trees").forGetter(Mix::trees),
				Codec.BOOL.optionalFieldOf("hardy", false).forGetter(Mix::hardy)
		).apply(i, Mix::new));
	}

	/** One tree from a weighted list, on dirt or grass with room for its trunk and no other trunk right by it. */
	public static final class TreeFeature extends Feature<Mix> {
		TreeFeature() {
			super(Mix.CODEC);
		}

		@Override
		public boolean place(FeaturePlaceContext<Mix> ctx) {
			WorldGenLevel level = ctx.level();
			BlockPos pos = ctx.origin();
			List<Entry> trees = ctx.config().trees();
			if (trees.isEmpty()) return false;
			if (ctx.config().hardy()) {
				BlockState ground = level.getBlockState(pos.below());
				if (!ground.isFaceSturdy(level, pos.below(), Direction.UP) || ground.is(BlockTags.LEAVES) || ground.is(BlockTags.LOGS)) return false;
			} else if (!Blocks.OAK_SAPLING.defaultBlockState().canSurvive(level, pos)) return false;
			for (int k = 0; k < 4; k++) {
				BlockState s = level.getBlockState(pos.above(k));
				// a sapling growing stands where its tree goes
				if (!s.isAir() && !s.canBeReplaced() && !s.is(BlockTags.SAPLINGS)) return false;
			}
			for (int dx = -3; dx <= 3; dx += 3)
				for (int dz = -3; dz <= 3; dz += 3)
					if ((dx != 0 || dz != 0) && level.getBlockState(pos.offset(dx, 2, dz)).is(BlockTags.LOGS)) return false;
			RandomSource random = ctx.random();
			int total = 0;
			for (Entry e : trees) total += e.weight();
			int roll = random.nextInt(Math.max(1, total));
			Entry pick = trees.get(0);
			for (Entry e : trees) {
				if ((roll -= e.weight()) < 0) {
					pick = e;
					break;
				}
			}
			return put(level, pick.template(), pos.below(), Rotation.getRandom(random), writable(level), random);
		}
	}

	// ================================================================ the giants

	public static final class GiantTree extends Structure {
		public static final MapCodec<GiantTree> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
				settingsCodec(i),
				ResourceLocation.CODEC.fieldOf("template").forGetter(s -> s.template),
				Codec.INT.optionalFieldOf("spread", 7).forGetter(s -> s.spread),
				Codec.INT.optionalFieldOf("reach", 9).forGetter(s -> s.reach),
				Codec.INT.optionalFieldOf("tries", 1).forGetter(s -> s.tries)
		).apply(i, GiantTree::new));

		final ResourceLocation template;
		/** How far the land round its foot may rise and fall. */
		final int spread;
		/** How far out the land's checked. */
		final int reach;
		/** How many spots round the chunk it tries before giving up (towers look about for flat ground; trees just take the one). */
		final int tries;

		GiantTree(StructureSettings settings, ResourceLocation template, int spread, int reach, int tries) {
			super(settings);
			this.template = template;
			this.spread = spread;
			this.reach = reach;
			this.tries = tries;
		}

		/** the chunk's middle, then a ring 32 out, then one 64 out */
		private static final int[][] SPOTS = {{0, 0}, {32, 0}, {0, 32}, {-32, 0}, {0, -32}, {32, 32}, {-32, 32}, {32, -32}, {-32, -32},
				{64, 0}, {0, 64}, {-64, 0}, {0, -64}};

		@Override
		public StructureType<?> type() {
			return GIANT_TREE.get();
		}

		/** The biome first: it's cheap, the heights below aren't (each one works out a whole noise column). */
		private static boolean biomeFits(GenerationContext ctx, int x, int z) {
			for (int y = ctx.chunkGenerator().getSeaLevel(); y <= 192; y += 32)
				if (ctx.validBiome().test(ctx.biomeSource().getNoiseBiome(QuartPos.fromBlock(x), QuartPos.fromBlock(y), QuartPos.fromBlock(z),
						ctx.randomState().sampler()))) return true;
			return false;
		}

		@Override
		protected Optional<GenerationStub> findGenerationPoint(GenerationContext ctx) {
			BlockPos off = offset(template);
			if (off == null) return Optional.empty();
			ChunkPos cp = ctx.chunkPos();
			for (int t = 0; t < Math.min(tries, SPOTS.length); t++) {
				Optional<GenerationStub> stub = at(ctx, off, cp.getMiddleBlockX() + SPOTS[t][0], cp.getMiddleBlockZ() + SPOTS[t][1]);
				if (stub.isPresent()) return stub;
			}
			return Optional.empty();
		}

		private Optional<GenerationStub> at(GenerationContext ctx, BlockPos off, int ox, int oz) {
			if (!biomeFits(ctx, ox, oz)) return Optional.empty();
			ChunkGenerator gen = ctx.chunkGenerator();
			// dry land, flat enough round the foot
			int lo = Integer.MAX_VALUE, hi = Integer.MIN_VALUE, y0 = 0;
			for (int k = 0; k < 5; k++) {
				int x = ox, z = oz;
				if (k > 0) {
					double a = k * Math.PI / 2;
					x += (int) (Math.cos(a) * reach);
					z += (int) (Math.sin(a) * reach);
				}
				int top = gen.getBaseHeight(x, z, Heightmap.Types.WORLD_SURFACE_WG, ctx.heightAccessor(), ctx.randomState());
				if (k == 0) {
					if (top != gen.getBaseHeight(x, z, Heightmap.Types.OCEAN_FLOOR_WG, ctx.heightAccessor(), ctx.randomState())) return Optional.empty();
					y0 = top - 1;
				}
				lo = Math.min(lo, top);
				hi = Math.max(hi, top);
				if (hi - lo > spread) return Optional.empty();
			}
			if (y0 < gen.getSeaLevel()) return Optional.empty();
			Rotation rot = Rotation.getRandom(ctx.random());
			BlockPos ground = new BlockPos(ox, y0, oz);
			StructureTemplate t = ctx.structureTemplateManager().getOrCreate(template);
			BoundingBox bb = t.getBoundingBox(settings(off, rot), ground.subtract(off));
			int fy = y0;
			return Optional.of(new GenerationStub(ground, b -> {
				for (int i = bb.minX() >> 4; i <= bb.maxX() >> 4; i++)
					for (int k = bb.minZ() >> 4; k <= bb.maxZ() >> 4; k++)
						b.addPiece(new Piece(template, ox, fy, oz, rot, i, k, bb.minY(), bb.maxY()));
			}));
		}
	}

	/** One chunk of a giant tree. */
	public static final class Piece extends StructurePiece {
		final ResourceLocation template;
		final int ox, y0, oz;           // the foot (TowerSites reads where a tower stands from these)
		final Rotation rot;

		Piece(ResourceLocation template, int ox, int y0, int oz, Rotation rot, int chx, int chz, int minY, int maxY) {
			super(PIECE.get(), 0, new BoundingBox(chx * 16, minY, chz * 16, chx * 16 + 15, maxY, chz * 16 + 15));
			this.template = template;
			this.ox = ox;
			this.y0 = y0;
			this.oz = oz;
			this.rot = rot;
		}

		Piece(CompoundTag tag) {
			super(PIECE.get(), tag);
			template = ResourceLocation.parse(tag.contains("template") ? tag.getString("template") : "ashbound:tree/elder");
			ox = tag.getInt("ox");
			y0 = tag.getInt("y0");
			oz = tag.getInt("oz");
			rot = Rotation.values()[Math.floorMod(tag.getInt("rot"), 4)];
		}

		@Override
		protected void addAdditionalSaveData(StructurePieceSerializationContext ctx, CompoundTag tag) {
			tag.putString("template", template.toString());
			tag.putInt("ox", ox);
			tag.putInt("y0", y0);
			tag.putInt("oz", oz);
			tag.putInt("rot", rot.ordinal());
		}

		@Override
		public void postProcess(WorldGenLevel level, StructureManager structures, ChunkGenerator gen, RandomSource random,
				BoundingBox chunkBox, ChunkPos chunk, BlockPos pivot) {
			put(level, template, new BlockPos(ox, y0, oz), rot, chunkBox, random);
		}
	}

	// ================================================================ setup

	static final DeferredRegister<Feature<?>> FEATURES = DeferredRegister.create(Registries.FEATURE, Ashbound.ID);
	static final DeferredRegister<StructureType<?>> STRUCTURES = DeferredRegister.create(Registries.STRUCTURE_TYPE, Ashbound.ID);
	static final DeferredRegister<StructurePieceType> PIECES = DeferredRegister.create(Registries.STRUCTURE_PIECE, Ashbound.ID);
	static final DeferredRegister<StructureProcessorType<?>> PROCESSORS = DeferredRegister.create(Registries.STRUCTURE_PROCESSOR, Ashbound.ID);

	static final DeferredHolder<Feature<?>, TreeFeature> TREE = FEATURES.register("tree", TreeFeature::new);
	static final DeferredHolder<StructureType<?>, StructureType<GiantTree>> GIANT_TREE = STRUCTURES.register("giant_tree", () -> () -> GiantTree.CODEC);
	static final DeferredHolder<StructurePieceType, StructurePieceType> PIECE = PIECES.register("giant_tree_piece",
			() -> (StructurePieceType.ContextlessType) Piece::new);
	static final DeferredHolder<StructureProcessorType<?>, StructureProcessorType<OnLand>> ON_LAND = PROCESSORS.register("on_land",
			() -> () -> OnLand.CODEC);

	private static int spawn(CommandSourceStack src, String name) {
		// a tower's template sits in structure/tower/ (towers stand the way giant trees do: docs/TOWERS.md)
		String folder = Trees.class.getResource("/data/ashbound/structure/tower/" + name + ".nbt") != null ? "tower/" : "tree/";
		ResourceLocation id = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, folder + name);
		if (offset(id) == null) {
			src.sendFailure(Component.literal("No tree " + name));
			return 0;
		}
		ServerLevel level = src.getLevel();
		Vec3 at = src.getPosition();
		BlockPos ground = BlockPos.containing(at).below();
		put(level, id, ground, Rotation.NONE, null, level.getRandom());
		if (folder.equals("tower/")) TowerSites.placed(level, name, ground, Rotation.NONE);
		src.sendSuccess(() -> Component.literal("Tree " + name + " at " + ground.toShortString()), true);
		return 1;
	}

	static void register(IEventBus bus) {
		FEATURES.register(bus);
		STRUCTURES.register(bus);
		PIECES.register(bus);
		PROCESSORS.register(bus);
		NeoForge.EVENT_BUS.addListener((RegisterCommandsEvent e) -> e.getDispatcher().register(Commands.literal("ashbound")
				.requires(s -> s.hasPermission(2))
				.then(Commands.literal("tree").then(Commands.argument("name", StringArgumentType.word())
						.suggests((c, b) -> {
							offset(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "tree/elder"));
							return SharedSuggestionProvider.suggest(new ArrayList<>(OFFSETS.keySet()), b);
						})
						.executes(c -> spawn(c.getSource(), StringArgumentType.getString(c, "name")))))));
	}
}
