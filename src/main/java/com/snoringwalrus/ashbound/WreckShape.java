package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/**
 * The Graveyard of Ships, the Wreck-Mother's arena (tools/blender/wreck_arena.py is the look): a floor 124 blocks across
 * made of a dozen wrecked decks the sea has jammed together, each wreck's planks running their own way, hull rails
 * between them, holes stove in down to the sea, three masts lying across it and cannons and capstans for cover; a broken
 * hull rim round it with five gaps where the waves wash in; four masts still standing at the rim with torn sails and cold
 * lanterns; a black sea all round, and out in it a ring of ship's ribs curling up out of the water. Open to the sky. A
 * compass rose of brass in the middle where the party lands. Same every time (fixed seeds).
 */
public final class WreckShape {
	private WreckShape() {}

	public static final int R_DECK = 62, R_RIM = 66, SEA = -4, R_SEA = 112;
	static final double[] GAPS = {0.9, 2.2, 3.4, 4.6, 5.7};
	/** she comes up at the north rim, facing the rose */
	public static final Vec3 BOSS = new Vec3(0.5, 0, 44.5);
	/** the standing masts' lanterns (for their light) */
	public static final List<Vec3> LAMPS = new ArrayList<>();

	private static BlockState b(String id) {
		Block k = BuiltInRegistries.BLOCK.get(ResourceLocation.parse(id.contains(":") ? id : "ashbound:" + id));
		return (k == Blocks.AIR ? Blocks.STONE : k).defaultBlockState();
	}

	private static BlockState axis(BlockState s, Direction.Axis a) {
		return s.hasProperty(RotatedPillarBlock.AXIS) ? s.setValue(RotatedPillarBlock.AXIS, a) : s;
	}

	static boolean gap(double a) {
		for (double g : GAPS) if (Math.abs(wrap(a - g)) * R_RIM < 4) return true;
		return false;
	}

	public static void blocks(ArenaShape.Sink into) {
		// nothing above the deck where she comes up
		ArenaShape.Sink s = (x, y, z, st) -> {
			if (y >= 0 && Math.abs(x) <= 7 && z >= 36 && z <= 52) return;
			into.put(x, y, z, st);
		};
		BlockState[] deck = {b("wreck_planks"), b("tarred_planks"), b("driftwood_planks"), b("rotten_planks")};
		BlockState rail = b("wreck_beam"), hull = b("rotten_planks"), barn = b("barnacled_stone"), log = b("driftwood_log");
		BlockState rib = b("whalebone_block"), brass = b("tide_brass"), plate = b("brass_plate"), lamp = b("sea_glow"), sail = b("linen_sheet");
		BlockState rock = b("tide_rock"), sand = b("drowned_sand"), water = Blocks.WATER.defaultBlockState();
		Random r = new Random(53);
		// a dozen wrecks: each owns the patch nearest its seed, its planks running its own way
		double[][] seeds = new double[12][3];
		for (int i = 0; i < 12; i++) seeds[i] = new double[] {i == 0 ? 0 : r.nextDouble() * 100 - 50, i == 0 ? 0 : r.nextDouble() * 100 - 50, r.nextDouble() * Math.PI};
		List<double[]> holes = new ArrayList<>();
		for (int i = 0; i < 10; i++) {
			double[] h = {r.nextDouble() * 96 - 48, r.nextDouble() * 96 - 48, 2 + r.nextDouble() * 2.2};
			if (Math.hypot(h[0], h[1]) > 14) holes.add(h);
		}
		for (int x = -R_SEA; x <= R_SEA; x++)
			for (int z = -R_SEA; z <= R_SEA; z++) {
				double rr = Math.hypot(x + 0.5, z + 0.5), a = Math.atan2(z + 0.5, x + 0.5);
				if (rr > R_SEA + 0.5) continue;
				if (rr > R_SEA - 1.5) {                                    // a reef round the sea's edge holds it in
					for (int y = SEA - 2; y <= SEA + (ArenaShape.hash(x, 2, z) & 1); y++) s.put(x, y, z, rock);
					continue;
				}
				if (rr > R_RIM + 0.5) {                                    // the sea: two deep over a black bed
					s.put(x, SEA - 2, z, (ArenaShape.hash(x, 1, z) & 3) == 0 ? sand : rock);
					s.put(x, SEA - 1, z, water);
					s.put(x, SEA, z, water);
					continue;
				}
				// the hulls under it all, down into the sea (only their skin: the inside's never seen)
				int bot = SEA - 8 + (int) Math.round(3 * Math.sin(a * 3 + rr * 0.1));
				boolean hole = false;
				for (double[] h : holes) if (Math.hypot(x - h[0], z - h[1]) < h[2]) hole = true;
				if (rr < R_DECK && hole) {
					s.put(x, SEA - 2, z, rock);
					s.put(x, SEA - 1, z, water);
					s.put(x, SEA, z, water);
					continue;
				}
				for (int y = bot; y < -1; y++)
					if (y < bot + 2 || rr > R_RIM - 3 || y >= SEA - 2) s.put(x, y, z, y <= SEA + 1 && rr > R_RIM - 3 ? barn : hull);   // solid by the waterline: no sea gets in
				if (rr < R_DECK) {
					int best = 0;
					double d0 = 1e9, d1 = 1e9;
					for (int i = 0; i < 12; i++) {
						double d = Math.hypot(x - seeds[i][0], z - seeds[i][1]);
						if (d < d0) {
							d1 = d0;
							d0 = d;
							best = i;
						} else if (d < d1) d1 = d;
					}
					if (d1 - d0 < 1.2 && best != 0 && ((int) rr % 9) > 1) {     // a hull rail between two decks, gaps to cross
						s.put(x, -1, z, rail);
						s.put(x, 0, z, rail);
						continue;
					}
					double t = seeds[best][2];
					int stripe = (int) Math.floor((x + 0.5) * Math.cos(t) + (z + 0.5) * Math.sin(t));
					s.put(x, -1, z, deck[Math.floorMod(stripe + best, best % 2 == 0 ? 3 : 4)]);
				} else {
					if (gap(a)) {                                          // the waves wash in here
						s.put(x, -1, z, deck[2]);
						continue;
					}
					int hh = (int) (2 + 5 * (0.5 + 0.5 * Math.sin(a * 7 + 1.3)) + 2 * (0.5 + 0.5 * Math.sin(a * 19)));
					for (int y = -1; y < hh; y++) s.put(x, y, z, y == hh - 1 ? rail : hull);
				}
			}
		// the compass rose where the party lands
		for (int x = -7; x <= 7; x++)
			for (int z = -7; z <= 7; z++) {
				double rr = Math.hypot(x + 0.5, z + 0.5), a = Math.atan2(z + 0.5, x + 0.5);
				double f = ((a * 4 / Math.PI) % 1.0 + 1.0) % 1.0, pt = Math.min(f, 1 - f);    // 0 on each of the eight points
				if (Math.abs(rr - 6.2) < 0.55 || rr < 6.0 && pt < 0.12 * (6.0 - rr) / 6.0 + 0.02)
					s.put(x, -1, z, brass);
			}
		// three masts lying across the deck
		for (int i = 0; i < 3; i++) {
			double a = r.nextDouble() * Math.PI * 2, d = 22 + r.nextDouble() * 18;
			double cx = Math.cos(a) * d, cz = Math.sin(a) * d, dx = Math.cos(a + 1.6), dz = Math.sin(a + 1.6), len = 12 + r.nextDouble() * 4;
			Direction.Axis ax = Math.abs(dx) > Math.abs(dz) ? Direction.Axis.X : Direction.Axis.Z;
			for (double k = -len; k <= len; k += 0.5)
				for (int u = -1; u <= 1; u++)
					for (int v = 0; v <= 2; v++) {
						if (u * u + (v - 1) * (v - 1) > 2) continue;
						int x = (int) Math.round(cx + dx * k - dz * u), z = (int) Math.round(cz + dz * k + dx * u);
						s.put(x, v, z, axis(log, ax));
					}
		}
		// cannons and capstans
		for (int i = 0; i < 8; i++) {
			double a = i / 8.0 * Math.PI * 2 + (r.nextDouble() - 0.5) * 0.4, d = 30 + r.nextDouble() * 18;
			int cx = (int) Math.round(Math.cos(a) * d), cz = (int) Math.round(Math.sin(a) * d);
			if (i % 2 == 0) {
				for (int x = -2; x <= 2; x++)
					for (int z = -2; z <= 2; z++)
						if (x * x + z * z <= 5) for (int y = 0; y < 3; y++) s.put(cx + x, y, cz + z, y < 2 ? axis(rail, Direction.Axis.Y) : plate);
			} else {
				double ca = Math.cos(a + Math.PI), sa = Math.sin(a + Math.PI);
				for (int u = -2; u <= 4; u++)
					for (int v = -1; v <= 1; v++)
						for (int y = 0; y <= 1; y++) {
							if (u > 1 && (v != 0 || y > 0)) continue;
							s.put((int) Math.round(cx + u * ca - v * sa), y, (int) Math.round(cz + u * sa + v * ca), u > -1 ? plate : hull);
						}
			}
		}
		// the masts still standing at the rim: yards, a crow's nest, torn sails, a cold lantern
		LAMPS.clear();
		for (int i = 0; i < 4; i++) {
			double a = i / 4.0 * Math.PI * 2 + 0.5;
			int cx = (int) (Math.cos(a) * 57), cz = (int) (Math.sin(a) * 57), h = 40 + r.nextInt(16);
			double lx = Math.cos(a) * 0.08, lz = Math.sin(a) * 0.08;               // leaning out a little
			for (int y = -1; y < h; y++)
				for (int dx = 0; dx <= 1; dx++)
					for (int dz = 0; dz <= 1; dz++) s.put(cx + dx + (int) (lx * y), y, cz + dz + (int) (lz * y), axis(log, Direction.Axis.Y));
			double sx = -Math.sin(a), sz = Math.cos(a);
			for (int yz : new int[] {(int) (h * 0.55), (int) (h * 0.85)}) {
				Direction.Axis ax = Math.abs(sx) > Math.abs(sz) ? Direction.Axis.X : Direction.Axis.Z;
				for (int k = -9; k <= 9; k++) s.put((int) Math.round(cx + lx * yz + sx * k), yz, (int) Math.round(cz + lz * yz + sz * k), axis(log, ax));
				// the sail hanging off the yard, torn: ragged lengths
				for (int k = -8; k <= 8; k++) {
					int len = Math.abs(k) < 7 ? 4 + Math.floorMod(ArenaShape.hash(k, yz, i), 10) : 2 + Math.floorMod(ArenaShape.hash(k, yz, i), 4);
					for (int y = yz - 1; y > yz - 1 - len && y > 2; y--)
						if (Math.floorMod(ArenaShape.hash(k, y, i), 9) != 0) s.put((int) Math.round(cx + lx * yz + sx * k + Math.cos(a)), y, (int) Math.round(cz + lz * yz + sz * k + Math.sin(a)), sail);
				}
			}
			int nest = (int) (h * 0.92);
			for (int dx = -2; dx <= 3; dx++)
				for (int dz = -2; dz <= 3; dz++)
					if (dx == -2 || dx == 3 || dz == -2 || dz == 3) s.put(cx + dx + (int) (lx * nest), nest, cz + dz + (int) (lz * nest), rail);
			int ly = (int) (h * 0.6);
			int lxx = cx + (int) (lx * ly) + (int) Math.round(Math.cos(a) * 2), lzz = cz + (int) (lz * ly) + (int) Math.round(Math.sin(a) * 2);
			s.put(lxx, ly, lzz, lamp);
			LAMPS.add(new Vec3(lxx + 0.5, ly, lzz + 0.5));
		}
		// cold lanterns along the rails
		Random lr = new Random(7);
		for (int i = 0; i < 10; i++) {
			double a = lr.nextDouble() * Math.PI * 2, d = 20 + lr.nextDouble() * 38;
			int x = (int) Math.round(Math.cos(a) * d), z = (int) Math.round(Math.sin(a) * d);
			s.put(x, 0, z, lamp);
		}
		// the ring of ship's ribs out in the sea, curling up and out (never over the deck)
		for (int i = 0; i < 16; i++) {
			double a = i / 16.0 * Math.PI * 2 + (r.nextDouble() - 0.5) * 0.16, d0 = 84 + r.nextDouble() * 16;
			int h = 18 + r.nextInt(17);
			for (double side : new double[] {-0.06, 0.06})
				for (int y = SEA - 2; y < SEA + h; y++) {
					double t = (double) (y - SEA) / h, d = d0 + 10 * t * t, aa = a + side * (1 - 0.6 * t);
					for (int k = 0; k <= 1; k++) s.put((int) (Math.cos(aa) * (d + k)), y, (int) (Math.sin(aa) * (d + k)), rib);
				}
		}
	}

	private static double wrap(double a) {
		while (a > Math.PI) a -= Math.PI * 2;
		while (a < -Math.PI) a += Math.PI * 2;
		return a;
	}
}
