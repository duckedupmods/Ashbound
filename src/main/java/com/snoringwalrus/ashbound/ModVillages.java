package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.LongArrayTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.BiomeTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.npc.Villager;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureStart;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.phys.AABB;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;

/**
 * The other mods' villages (CTOV, Towns and Towers, Tidal Towns, Villages and Pillages, vanilla's own) get our people too, by the land
 * they stand on: dwarves in the mountains, snow and taiga, elves in the forests, jungles and swamps, demons in the deserts, badlands
 * and savanna, humans everywhere else. The villagers stay for their trades. A village is settled once, the first time a player walks
 * into it with all of it loaded; our own six villages and the capital never see a mod village (Capital.blocksStructures).
 */
public final class ModVillages {
	private ModVillages() {}

	/** Fewest and most of ours in a village, and how many per villager there. */
	private static final int FEWEST = 5, MOST = 12, EVERY = 40;
	private static final double PER_VILLAGER = 1.2;

	public static boolean village(ResourceLocation id) {
		if (id == null || id.getNamespace().equals(Ashbound.ID)) return false;
		String path = id.getPath();
		return path.substring(path.lastIndexOf('/') + 1).startsWith("village");
	}

	/** Who lives where: a biome's race. */
	public static String race(Holder<Biome> b, ResourceLocation structure) {
		String name = b.unwrapKey().map(k -> k.location().getPath()).orElse("") + " " + structure.getPath();
		// names first: vanilla counts meadows and cherry groves as mountains
		if (any(name, "desert", "badlands", "savanna", "mesa", "dune", "canyon", "outback", "ashen", "volcan", "arid")) return "demon";
		if (any(name, "forest", "jungle", "cherry", "swamp", "bayou", "mangrove", "wood", "bamboo", "rainforest", "mushroom", "witch")) return "elf";
		if (any(name, "snow", "frozen", "ice", "tundra", "alpine", "peak", "mountain", "taiga", "grove", "slope", "highland", "glacier", "christmas")) return "dwarf";
		if (any(name, "meadow", "plains", "beach", "ocean", "river", "coast")) return "human";
		if (b.is(BiomeTags.IS_BADLANDS) || b.is(BiomeTags.IS_SAVANNA)) return "demon";
		if (b.is(BiomeTags.IS_FOREST) || b.is(BiomeTags.IS_JUNGLE)) return "elf";
		if (b.is(BiomeTags.IS_MOUNTAIN) || b.is(BiomeTags.IS_TAIGA)) return "dwarf";
		return "human";
	}

	private static boolean any(String s, String... words) {
		for (String w : words) if (s.contains(w)) return true;
		return false;
	}

	/** Who to call for, by race: a couple of the trades, then anyone. */
	static String who(String race, int i) {
		String tag = race.equals("human") ? "townsfolk" : race;
		String[] firsts = switch (race) {
			case "dwarf" -> new String[] {"smith", "guard", "miner"};
			case "elf" -> new String[] {"warden", "herbalist", "singer"};
			case "demon" -> new String[] {"smith", "cook", "fence"};
			default -> new String[] {"merchant", "guard", "farmer"};
		};
		return i < firsts.length ? "@" + tag + "/" + firsts[i] : "@" + tag;
	}

	static final class State extends SavedData {
		final Set<Long> settled = new HashSet<>();

		static State load(CompoundTag t, HolderLookup.Provider reg) {
			State s = new State();
			for (long l : t.getLongArray("settled")) s.settled.add(l);
			return s;
		}

		@Override
		public CompoundTag save(CompoundTag t, HolderLookup.Provider reg) {
			t.put("settled", new LongArrayTag(new ArrayList<>(settled)));
			return t;
		}
	}

	private static State state(ServerLevel l) {
		return l.getDataStorage().computeIfAbsent(new SavedData.Factory<>(State::new, State::load, null), "ashbound_mod_villages");
	}

	private static void look(ServerPlayer p) {
		ServerLevel l = p.serverLevel();
		if (l.dimension() != Level.OVERWORLD) return;
		BlockPos at = p.blockPosition();
		var reg = l.registryAccess().registryOrThrow(Registries.STRUCTURE);
		for (Structure s : l.structureManager().getAllStructuresAt(at).keySet()) {
			ResourceLocation id = reg.getKey(s);
			if (!village(id)) continue;
			StructureStart start = l.structureManager().getStructureAt(at, s);
			if (!start.isValid()) continue;
			long key = start.getChunkPos().toLong();
			State st = state(l);
			if (st.settled.contains(key) || !loaded(l, start.getBoundingBox())) continue;
			st.settled.add(key);
			st.setDirty();
			settle(l, start.getBoundingBox(), id);
		}
	}

	private static boolean loaded(ServerLevel l, BoundingBox b) {
		for (int x = b.minX() >> 4; x <= b.maxX() >> 4; x++)
			for (int z = b.minZ() >> 4; z <= b.maxZ() >> 4; z++)
				if (!l.hasChunk(x, z)) return false;
		return true;
	}

	/** Our people into one village: beside its villagers first, then on open ground inside it. */
	static int settle(ServerLevel l, BoundingBox b, ResourceLocation id) {
		BlockPos mid = b.getCenter();
		String race = race(l.getBiome(mid), id);
		AABB box = new AABB(b.minX(), b.minY() - 4, b.minZ(), b.maxX() + 1, b.maxY() + 4, b.maxZ() + 1);
		List<Villager> villagers = l.getEntitiesOfClass(Villager.class, box);
		int n = Math.max(FEWEST, Math.min(MOST, (int) Math.round(villagers.size() * PER_VILLAGER)));
		RandomSource rnd = l.random;
		int made = 0;
		for (int i = 0, tries = 0; made < n && tries < n * 12; tries++) {
			BlockPos near = i < villagers.size() ? villagers.get(i).blockPosition().offset(rnd.nextInt(5) - 2, 0, rnd.nextInt(5) - 2)
					: new BlockPos(b.minX() + rnd.nextInt(b.getXSpan()), mid.getY(), b.minZ() + rnd.nextInt(b.getZSpan()));
			BlockPos ground = ground(l, near, b);
			if (ground == null) continue;
			if (Talk.spawn(l, who(race, i), "", "stroll", ground.getX() + 0.5, ground.getY(), ground.getZ() + 0.5, rnd.nextFloat() * 360) != null) made++;
			i++;
		}
		Ashbound.LOG.info("Settled {} {} in {} at {}", made, race, id, mid);
		return made;
	}

	/** Standing room on top of the ground at this column, inside the village's height. */
	private static BlockPos ground(ServerLevel l, BlockPos at, BoundingBox b) {
		int y = l.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, at.getX(), at.getZ());
		if (y < b.minY() - 3 || y > b.maxY() + 3) return null;
		BlockPos feet = new BlockPos(at.getX(), y, at.getZ());
		BlockState under = l.getBlockState(feet.below());
		if (!under.isFaceSturdy(l, feet.below(), net.minecraft.core.Direction.UP) || !under.getFluidState().isEmpty()) return null;
		if (!l.getBlockState(feet).getCollisionShape(l, feet).isEmpty() || !l.getBlockState(feet.above()).getCollisionShape(l, feet.above()).isEmpty()) return null;
		if (!l.getFluidState(feet).isEmpty()) return null;
		return feet;
	}

	/** /ashbound village here: settles the village you're standing in again (a test, or after a mod update). */
	private static void commands(net.neoforged.neoforge.event.RegisterCommandsEvent e) {
		e.getDispatcher().register(net.minecraft.commands.Commands.literal("ashbound").requires(c -> c.hasPermission(2))
				.then(net.minecraft.commands.Commands.literal("village").then(net.minecraft.commands.Commands.literal("here").executes(c -> {
					ServerPlayer p = c.getSource().getPlayerOrException();
					ServerLevel l = p.serverLevel();
					var reg = l.registryAccess().registryOrThrow(Registries.STRUCTURE);
					for (Structure s : l.structureManager().getAllStructuresAt(p.blockPosition()).keySet()) {
						ResourceLocation id = reg.getKey(s);
						StructureStart start = l.structureManager().getStructureAt(p.blockPosition(), s);
						if (!village(id) || !start.isValid()) continue;
						int n = settle(l, start.getBoundingBox(), id);
						c.getSource().sendSuccess(() -> net.minecraft.network.chat.Component.literal(n + " " + race(l.getBiome(start.getBoundingBox().getCenter()), id)
								+ " settled in " + id), false);
						return 1;
					}
					c.getSource().sendFailure(net.minecraft.network.chat.Component.literal("No other mod's village here"));
					return 0;
				}))));
	}

	public static void register() {
		NeoForge.EVENT_BUS.addListener(ModVillages::commands);
		NeoForge.EVENT_BUS.addListener((PlayerTickEvent.Post e) -> {
			if (e.getEntity() instanceof ServerPlayer p && p.tickCount % EVERY == 0 && !p.isSpectator()) look(p);
		});
	}
}
