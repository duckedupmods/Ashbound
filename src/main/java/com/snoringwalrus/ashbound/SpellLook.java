package com.snoringwalrus.ashbound;

/**
 * How each dungeon's magic moves and hits. Seven families cover the thirty elements (concepts: tools/blender/vfx_mage.py);
 * an element is its family in its dungeon's own colour.
 */
public final class SpellLook {
	private SpellLook() {}

	public enum Family { FLAME, SHARD, LIGHTNING, LIQUID, ROT, VOID, THREAD }

	/** what's drawn when no dungeon's named: the white school's gold */
	public static final int GOLD = 0xFFC850;

	public static Family of(String gate) {
		return switch (gate) {
			case "crypt", "foundry", "obsidian_labyrinth", "wyrms_hoard", "sandsunk_tomb", "glass_minaret", "warlords_fang" -> Family.FLAME;
			case "frost", "rimeholt", "temple", "jade_monastery", "weeping_mine", "fallen_titan" -> Family.SHARD;
			case "storm_bastion", "clockwork_spire", "ossuary" -> Family.LIGHTNING;
			case "bloodmoon_court", "cellar", "tide_chapel", "plague" -> Family.LIQUID;
			case "rotwood", "serpent_ziggurat", "mirefen_coven", "rookery" -> Family.ROT;
			case "silk", "hollow_circus" -> Family.THREAD;
			default -> Family.VOID;
		};
	}

	public static int colour(String gate) {
		Gear.Dungeon d = gate.isEmpty() ? null : Gear.of(gate);
		return d == null ? GOLD : d.colour();
	}
}
