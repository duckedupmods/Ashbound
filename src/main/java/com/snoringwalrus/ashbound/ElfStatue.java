package com.snoringwalrus.ashbound;

/** Written by tools/elfstatue.py: the Moonwell Priestess's pieces and which of them hold moonwater (and glow). */
public final class ElfStatue {
	public static final int PIECES = 291;
	private static final java.util.BitSet GLOW = new java.util.BitSet();

	static {
		for (int i : new int[] {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 33, 34, 60, 61, 62, 63, 64, 111, 112, 113, 114, 115, 165, 166, 167, 168, 169, 219, 220, 221, 222, 223, 250, 251, 252, 253, 254, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 289, 290}) GLOW.set(i);
	}

	private ElfStatue() {}

	public static boolean glows(int piece) {
		return GLOW.get(piece);
	}
}
