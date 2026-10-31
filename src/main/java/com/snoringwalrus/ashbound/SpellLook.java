package com.snoringwalrus.ashbound;

/**
 * How each dungeon's magic moves and hits. Seven families cover the thirty elements (concepts: tools/blender/vfx_mage.py);
 * an element is its family in its dungeon's own colour.
 */
public final class SpellLook {
	private SpellLook() {}

	public enum Family { FLAME, SHARD, LIGHTNING, LIQUID, ROT, VOID, THREAD, HEX }

	/** what's drawn when no dungeon's named: the white school's gold */
	public static final int GOLD = 0xFFC850;

	/** the plain black staff's own magic, which isn't any dungeon's: black fire with a red rim */
	public static final String HEX = "hex";
	private static final int HEX_RIM = 0xD8140C;
	/** the plain summoner's staff: not any dungeon's either, the cold of what it calls */
	public static final String GRAVE = "grave";
	private static final int GRAVE_RIM = 0x48D8B0;

	public static Family of(String gate) {
		return switch (gate) {
			case HEX -> Family.HEX;
			case GRAVE -> Family.VOID;
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
		if (gate.equals(HEX)) return HEX_RIM;
		if (gate.equals(GRAVE)) return GRAVE_RIM;
		if (gate.equals("clockwork_spire")) return 0xffb53a;   // the tower's boiler amber (docs/TOWERS.md)
		Gear.Dungeon d = gate.isEmpty() ? null : Gear.of(gate);
		return d == null ? GOLD : d.colour();
	}
}
