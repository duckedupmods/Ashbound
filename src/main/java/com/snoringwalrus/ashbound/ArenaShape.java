package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.List;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.CampfireBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/**
 * The Ashen Ring's shape (tools/blender/arena_ring.py is the look), the same for the server that builds it and the client
 * that draws its crowd: a round of sand ringed by a wall with a gate in each quarter, stands climbing outward to an
 * outer wall of three storeys of arches (broken down on its south-west), all on a hanging root of rock in the night sky
 * over the clouds. Each run has its own Ring, a slot SPACING apart along x.
 */
public final class ArenaShape {
	private ArenaShape() {}

	public static final int FLOOR = 230, SPACING = 512, SLOTS = 4;
	public static final int R_SAND = 24, R_WALL = 26, R_TIERS = 44, R_OUT = 47, WALL_H = 6, TOP = 24, GATE_HALF = 2, GATE_H = 6, TUNNEL = 8;
	/** the four gates, as angles (N, E, S, W in the world: -z, +x, +z, -x) */
	public static final double[] GATES = {-Math.PI / 2, 0, Math.PI / 2, Math.PI};

	public static BlockPos origin(int slot) {
		return new BlockPos(slot * SPACING, FLOOR, 0);
	}

	/** How much of the outer wall is broken down at this angle, 0..1. */
	static double ruined(double a) {
		return Math.pow(Math.max(0, Math.sin(a + 3.5)), 3);
	}

	static boolean inGate(double a, double r) {
		for (double g : GATES) if (Math.abs(Mth.wrapDegrees(Math.toDegrees(a - g))) * Math.PI / 180 * r < GATE_HALF + 0.6) return true;
		return false;
	}

	/** The stands' height (over the floor) at radius r. */
	static int tier(double r) {
		int step = (int) ((r - R_WALL) / 2);
		return WALL_H + step + step / 2;
	}

	/** Sum of a cheap hash, for which rock and where. */
	static int hash(int x, int y, int z) {
		int h = x * 73856093 ^ y * 19349663 ^ z * 83492791;
		return (h ^ (h >>> 13)) * 0x5bd1e995;
	}

	public interface Sink {
		void put(int x, int y, int z, BlockState s);
	}

	private static BlockState block(String id) {
		Block b = BuiltInRegistries.BLOCK.get(ResourceLocation.parse(id));
		return (b == Blocks.AIR ? Blocks.STONE_BRICKS : b).defaultBlockState();
	}

	/** Every block of a Ring, relative to its origin (the middle of the sand's top). */
	public static void blocks(Sink s) {
		BlockState sand = Arena.SAND.get().defaultBlockState(), rune = Arena.RUNE.get().defaultBlockState();
		BlockState stone = block("ashbound:limestone_bricks"), trim = block("ashbound:carved_limestone"), seat = block("ashbound:limestone_flagstones");
		BlockState pillar = block("ashbound:limestone_pillar"), rock = Blocks.STONE.defaultBlockState(), rock2 = Blocks.ANDESITE.defaultBlockState();
		BlockState fire = Blocks.SOUL_CAMPFIRE.defaultBlockState().setValue(CampfireBlock.LIT, true), light = Blocks.LIGHT.defaultBlockState();
		for (int x = -R_OUT - 2; x <= R_OUT + 2; x++)
			for (int z = -R_OUT - 2; z <= R_OUT + 2; z++) {
				double r = Math.hypot(x + 0.5, z + 0.5), a = Math.atan2(z + 0.5, x + 0.5);
				if (r > R_OUT + 0.5) {
					// pilasters between the arches
					double seg = ((a * (R_OUT - 2)) % 6.0 + 6) % 6;
					if (r < R_OUT + 1.6 && (seg < 0.7 || seg > 5.3)) {
						int hh = (int) (TOP - ruined(a) * (TOP - 10));
						for (int y = 0; y < hh - 1; y++) s.put(x, y, z, y % 9 == 8 ? trim : pillar);
					}
					continue;
				}
				// the rock it hangs on: deeper toward the middle, ragged
				int bot = -(int) (30 * (1 - Math.pow(r / (R_OUT + 1), 1.6)) + 4 * Math.sin(a * 5) * (1 - r / R_OUT) + (hash(x, 0, z) & 3));
				for (int y = bot; y < -1; y++) s.put(x, y, z, (hash(x, y, z) & 7) == 0 ? rock2 : rock);
				if (r < R_SAND) {
					s.put(x, -1, z, r < 5.5 && (r > 4.5 || r < 1.5 || (Math.abs(x) == Math.abs(z) && r < 4.5) || ((x == 0 || z == 0) && r > 2.5)) ? rune : sand);
					continue;
				}
				s.put(x, -1, z, stone);
				boolean gate = inGate(a, r);
				if (r < R_WALL) {
					for (int y = 0; y <= WALL_H; y++) {
						if (gate && y < GATE_H) continue;
						s.put(x, y, z, y == WALL_H ? trim : stone);
					}
					continue;
				}
				if (r < R_TIERS) {
					int h = tier(r);
					boolean tunnel = gate && r < R_WALL + TUNNEL;
					for (int y = 0; y <= h; y++) {
						if (tunnel && y < GATE_H) continue;
						s.put(x, y, z, y == h ? seat : stone);
					}
					// lights hid in the seat rows, so the crowd is seen
					if ((hash(x, 1, z) & 15) == 0) s.put(x, h + 2, z, light);
					continue;
				}
				// the outer wall: three storeys of round-headed arches, broken down on one side
				int hh = (int) (TOP - ruined(a) * (TOP - 10) - (hash(x, 2, z) & 1) * ruined(a) * 2);
				double seg = ((a * (R_OUT - 2)) % 6.0 + 6) % 6;
				for (int y = 0; y <= hh; y++) {
					boolean arch = false;
					if (r > R_OUT - 1.5)
						for (int[] st : new int[][] {{0, 4}, {8, 3}, {16, 3}}) {
							int zb = st[0], tall = st[1];
							if (y >= zb && y < zb + tall && Math.abs(seg - 3) < 1.9) arch = true;
							else if (y >= zb + tall && (seg - 3) * (seg - 3) + (y - zb - tall) * (y - zb - tall) < 1.9 * 1.9) arch = true;
						}
					if (arch && y > 0) continue;
					s.put(x, y, z, y == 7 || y == 15 || y == hh ? trim : stone);
				}
			}
		// the tunnels behind the gates: a back wall, so nothing's seen through
		for (double g : GATES)
			for (int w = -GATE_HALF - 1; w <= GATE_HALF + 1; w++)
				for (int y = 0; y < GATE_H; y++) {
					int rr = R_WALL + TUNNEL;
					int x = (int) Math.round(Math.cos(g) * rr - Math.sin(g) * w), z = (int) Math.round(Math.sin(g) * rr + Math.cos(g) * w);
					s.put(x, y, z, stone);
				}
		// spirit braziers round the sand
		for (Vec3 b : braziers()) {
			int x = Mth.floor(b.x), z = Mth.floor(b.z);
			s.put(x, 0, z, pillar);
			s.put(x, 1, z, fire);
		}
	}

	public static List<Vec3> braziers() {
		List<Vec3> out = new ArrayList<>();
		for (int i = 0; i < 12; i++) {
			double a = i / 12.0 * Math.PI * 2 + Math.PI / 12;
			out.add(new Vec3(Math.cos(a) * (R_SAND - 1.5), 0, Math.sin(a) * (R_SAND - 1.5)));
		}
		return out;
	}

	/** The mouth of gate i, on the sand just in front of it, and the way out of it (unit, toward the middle). */
	public static Vec3 gate(int i) {
		double g = GATES[i];
		return new Vec3(Math.cos(g) * (R_SAND + 1.5), 0, Math.sin(g) * (R_SAND + 1.5));
	}

	/** Where monsters come out of gate i: back in its tunnel. */
	public static Vec3 lair(int i) {
		double g = GATES[i];
		return new Vec3(Math.cos(g) * (R_WALL + 3), 0, Math.sin(g) * (R_WALL + 3));
	}

	/** The seats, each a block the crowd sits on (relative to the origin): every seat-row block that's open over it. */
	public static List<int[]> seats() {
		List<int[]> out = new ArrayList<>();
		for (int x = -R_TIERS; x <= R_TIERS; x++)
			for (int z = -R_TIERS; z <= R_TIERS; z++) {
				double r = Math.hypot(x + 0.5, z + 0.5);
				if (r < R_WALL || r >= R_TIERS) continue;
				double a = Math.atan2(z + 0.5, x + 0.5);
				if (inGate(a, r) && r < R_WALL + TUNNEL + 1) continue;
				// the tier's front row of each step only, so they don't stand in each other
				if (tier(r) == tier(r - 1)) continue;
				out.add(new int[] {x, tier(r) + 1, z});
			}
		return out;
	}

	/** Where the fallen watch from: high on the south stands. */
	public static Vec3 stands() {
		return new Vec3(0.5, tier(R_TIERS - 1) + 3, R_TIERS - 2.5);
	}

	public static Direction facing(int i) {
		return switch (i) {
			case 0 -> Direction.SOUTH;
			case 1 -> Direction.WEST;
			case 2 -> Direction.NORTH;
			default -> Direction.EAST;
		};
	}
}
