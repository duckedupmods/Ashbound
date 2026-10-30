package com.snoringwalrus.ashbound;

import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;

/**
 * The dungeons a gate can open onto: only the ones built (docs/DUNGEONS.md), so a rank with none never opens.
 * Which one lies behind a gate is picked from its rank's list by its id, so client and server agree. The chunks
 * hanging round the tear are bits of that place it ripped through. Vanilla stand-ins until each dungeon's own
 * blocks are ported from E:\Ashbound.
 */
public final class GateDungeons {
	private GateDungeons() {}

	/** lair: its block file in data/ashbound/lair (Lairs), or null while it's only in E:\Ashbound. */
	public record Dungeon(String name, BlockState[] debris, String lair) {}

	private static Dungeon d(String name, Block... blocks) {
		return d(name, null, blocks);
	}

	private static Dungeon d(String name, String lair, Block... blocks) {
		BlockState[] s = new BlockState[blocks.length];
		for (int i = 0; i < blocks.length; i++) s[i] = blocks[i].defaultBlockState();
		return new Dungeon(name, s, lair);
	}

	/** A ported gate's own blocks (GateBlocks), by name. */
	private static Block[] own(String... names) {
		java.util.List<Block> b = new java.util.ArrayList<>();
		for (String n : names) {
			var have = GateBlocks.ALL.get(n);
			if (have != null) b.add(have.get());
			else Ashbound.LOG.warn("gate debris: no block {}", n);
		}
		return b.toArray(new Block[0]);
	}

	private static final Dungeon[] NONE = {};
	// first loaded by the gate command or a gate's tick, long after the registries are filled, so the ported
	// dungeons' own blocks can be named here
	/** Per rank, F to SSS. */
	private static final Dungeon[][] BUILT = {
			{d("The Drowned Cellar", "gate_cellar", own("cellar_brick", "cask_hoop", "cask_oak", "wet_cellar_brick", "mouldy_brick")),
					d("Gallows Hill", "gate_gallows", own("gallows_timber", "hill_fieldstone", "tarred_planks", "hill_earth", "dead_turf")),
					d("The Rotwood", "gate_rotwood", own("rotwood_bark", "rot_loam", "glowcap", "root_wall", "spore_moss"))},
			{d("The Crypt", "gate_crypt", own("crypt_stone", "crypt_bricks", "crypt_tiles", "grave_soil", "grave_wax"))},
			{d("The Plague Ward", "gate_plague", own("ward_bricks", "limewash", "tar_planks", "ward_tiles", "stained_limewash"))},
			{d("The Faceless Temple", "gate_temple", own("temple_bricks", "temple_stone", "abyss_stone", "temple_tiles", "cracked_temple_bricks")),
					d("The Ossuary Engine", "gate_ossuary", own("bone_bricks", "skull_wall", "brass_plating", "engine_floor", "marrow_rock")),
					d("The Slag Foundry", "gate_foundry", own("soot_bricks", "black_slate", "kiln_iron", "cold_slag", "rusted_kiln_iron"))},
			{d("The Silk Archive", "gate_silk", SilkBlocks.ARCHIVE_STONE.get(), SilkBlocks.ARCHIVE_SHELVES.get(), SilkBlocks.SILK_WALL.get(),
					SilkBlocks.WALNUT_PANEL.get(), SilkProps.SILK_WEB.get()),
					d("The Frozen Procession", "gate_frost", own("glacier_ice", "rime_stone", "icebound_bricks", "frost_flagstones", "packed_rime"))},
			NONE, NONE, NONE,
			{d("The Fallen Moon", Blocks.CALCITE, Blocks.SMOOTH_BASALT, Blocks.TUFF, Blocks.POLISHED_DIORITE)}};

	private static final String RANKS = "FEDCBAS";
	private static Dungeon[][] all;

	/** The hand-listed ones above, then every Roster v2 dungeon gear.json says has its lair built (tools/newgate.py). */
	private static Dungeon[][] all() {
		if (all != null) return all;
		java.util.List<java.util.List<Dungeon>> per = new java.util.ArrayList<>();
		for (Dungeon[] r : BUILT) per.add(new java.util.ArrayList<>(java.util.Arrays.asList(r)));
		try (java.io.InputStream in = GateDungeons.class.getResourceAsStream("/ashbound/gear.json")) {
			if (in != null) {
				for (com.google.gson.JsonElement el : com.google.gson.JsonParser.parseReader(
						new java.io.InputStreamReader(in, java.nio.charset.StandardCharsets.UTF_8)).getAsJsonArray()) {
					com.google.gson.JsonObject g = el.getAsJsonObject();
					if (!g.has("lair")) continue;
					int rank = RANKS.indexOf(g.get("rank").getAsString().charAt(0));
					com.google.gson.JsonArray deb = g.getAsJsonArray("debris");
					String[] names = new String[deb.size()];
					for (int i = 0; i < names.length; i++) names[i] = deb.get(i).getAsString();
					if (rank >= 0) per.get(rank).add(d(g.get("title").getAsString(), g.get("lair").getAsString(), own(names)));
				}
			}
		} catch (Exception e) {
			Ashbound.LOG.error("roster v2 dungeons not loaded", e);
		}
		Dungeon[][] out = new Dungeon[per.size()][];
		for (int i = 0; i < out.length; i++) out[i] = per.get(i).toArray(new Dungeon[0]);
		return all = out;
	}

	public static boolean has(int rank) {
		return rank >= 0 && rank < all().length && all()[rank].length > 0;
	}

	public static Dungeon of(GateEntity g) {
		Dungeon[][] a = all();
		Dungeon[] ranks = a[Math.min(g.rank(), a.length - 1)];
		if (ranks.length == 0) ranks = a[0];
		return ranks[(int) Math.floorMod(g.getUUID().getMostSignificantBits(), ranks.length)];
	}
}
