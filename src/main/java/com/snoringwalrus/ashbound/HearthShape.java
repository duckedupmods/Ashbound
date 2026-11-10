package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Random;
import java.util.Set;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/**
 * The Kiln-Father's Hearth, Ossric's arena (tools/blender/ossric_arena.py is the look): a round hearth of black iron plates
 * 120 blocks across, cracked with glowing fissures, the Founder's Brand burned into its middle where the party lands; six
 * anvils the size of houses on it; a channel of molten slag round it (it burns), spilling off the edge in four falls; a
 * low soot-brick rim; nine kiln chimneys on spurs of rock out in the void, smoking. Open to the sky. Same every time
 * (a fixed seed), so a slot is raised once.
 */
public final class HearthShape {
	private HearthShape() {}

	public static final int R_FLOOR = 60, R_SLAG = 65, R_RIM = 69;
	/** where the slag channel runs out over the edge (radians round the hearth) */
	static final double[] SPILLS = {0.6, 2.4, 3.9, 5.3};
	/** Ossric comes up here, facing the Brand */
	public static final Vec3 BOSS = new Vec3(0.5, 0, 30.5);

	private static BlockState b(String id) {
		Block k = BuiltInRegistries.BLOCK.get(ResourceLocation.parse(id.contains(":") ? id : "ashbound:" + id));
		return (k == Blocks.AIR ? Blocks.STONE : k).defaultBlockState();
	}

	/** The chimney mouths, relative to the origin (for their smoke). */
	public static final List<Vec3> STACKS = new ArrayList<>();

	public static void blocks(ArenaShape.Sink s) {
		BlockState plate = b("blackiron_plate"), seam = b("soot_tiles"), crack = b("magma_seam"), slag = b("glowing_coals");
		BlockState crust = b("cold_slag"), brick = b("soot_bricks"), trim = b("kiln_iron"), rock = b("cinder_strata");
		BlockState rock2 = b("minecraft:blackstone"), iron = b("kiln_iron"), steel = b("minecraft:iron_block");
		Random r = new Random(31);
		// the fissures: random walks out from near the middle, forking
		Set<Long> cracks = new HashSet<>();
		for (int i = 0; i < 10; i++) {
			double a0 = i / 10.0 * Math.PI * 2 + (r.nextDouble() - 0.5) * 0.4;
			List<double[]> stack = new ArrayList<>();
			stack.add(new double[] {Math.cos(a0) * 7, Math.sin(a0) * 7, a0, 1});
			while (!stack.isEmpty()) {
				double[] w = stack.remove(stack.size() - 1);
				double x = w[0], z = w[1], a = w[2], life = w[3];
				int steps = (int) ((28 + r.nextDouble() * 24) * life);
				for (int k = 0; k < steps; k++) {
					a += r.nextGaussian() * 0.28;
					x += Math.cos(a);
					z += Math.sin(a);
					if (Math.hypot(x, z) > R_FLOOR - 2) break;
					cracks.add(key((int) Math.floor(x), (int) Math.floor(z)));
					if (r.nextDouble() < 0.035 && life > 0.4) stack.add(new double[] {x, z, a + (r.nextBoolean() ? 1 : -1) * (0.5 + r.nextDouble() * 0.5), life * 0.6});
				}
			}
		}
		for (int x = -R_RIM - 1; x <= R_RIM + 1; x++)
			for (int z = -R_RIM - 1; z <= R_RIM + 1; z++) {
				double rr = Math.hypot(x + 0.5, z + 0.5), a = Math.atan2(z + 0.5, x + 0.5);
				if (rr > R_RIM + 0.5) continue;
				// the rock root it hangs on, deep in the middle, ragged; hollow inside (only its skin is ever seen)
				int bot = -(int) (40 * (1 - Math.pow(rr / (R_RIM + 1), 1.5)) + 4 * Math.sin(a * 5) + (ArenaShape.hash(x, 0, z) & 1)) - 3;
				for (int y = bot; y < -2; y++)
					if (y < bot + 3 || y >= -5 || rr > R_RIM - 3) s.put(x, y, z, (ArenaShape.hash(x, y, z) & 7) == 0 ? rock2 : rock);
				if (rr < R_FLOOR) {
					boolean sm = Math.floorMod(x, 5) == 0 || Math.floorMod(z, 5) == 0;
					s.put(x, -1, z, cracks.contains(key(x, z)) ? crack : sm ? seam : plate);
					s.put(x, -2, z, rock);
				} else if (rr < R_SLAG) {
					s.put(x, -3, z, (ArenaShape.hash(x, 3, z) % 20) == 0 ? crust : slag);
					s.put(x, -4, z, rock);
					s.put(x, -2, z, Blocks.AIR.defaultBlockState());
				} else {
					boolean spill = false;
					for (double g : SPILLS) if (Math.abs(wrap(a - g)) * R_RIM < 3) spill = true;
					if (spill) {
						s.put(x, -3, z, slag);
						s.put(x, -4, z, rock);
						continue;
					}
					double seg = ((a * R_RIM) % 11.0 + 11) % 11;
					int hh = seg > 1.4 ? 2 : 4;                                       // a pier every 11 blocks
					for (int y = -2; y < hh; y++) s.put(x, y, z, y == hh - 1 ? trim : brick);
				}
			}
		// the Brand: a ring and three bars crossing
		for (int x = -6; x <= 6; x++)
			for (int z = -6; z <= 6; z++) {
				double rr = Math.hypot(x + 0.5, z + 0.5);
				boolean bar = false;
				for (double t : new double[] {0, Math.PI / 3, 2 * Math.PI / 3})
					if (Math.abs((x + 0.5) * Math.sin(t) - (z + 0.5) * Math.cos(t)) < 0.6 && rr < 4.6) bar = true;
				if (Math.abs(rr - 5.2) < 0.55 || bar) s.put(x, -1, z, slag);
			}
		// the anvils
		for (int i = 0; i < 6; i++) {
			double a = i / 6.0 * Math.PI * 2 + Math.PI / 6;
			anvil(s, Math.cos(a) * 40, Math.sin(a) * 40, a + Math.PI / 2 + (i % 2 == 1 ? 0.2 : -0.2), iron, steel, crack);
		}
		// the slag falls off the spills
		for (double g : SPILLS)
			for (int k = 0; k < 60; k++) {
				double t = k / 59.0, d = R_RIM + 1 + 6 * Math.pow(t, 0.6);
				int y = -3 - k, half = (int) Math.round(2.4 * (1 - 0.5 * t));
				int cx = (int) Math.round(Math.cos(g) * d), cz = (int) Math.round(Math.sin(g) * d);
				for (int dx = -half; dx <= half; dx++)
					for (int dz = -half; dz <= half; dz++) if (dx * dx + dz * dz <= half * half + 1) s.put(cx + dx, y, cz + dz, slag);
			}
		// the chimneys, out in the void on their spurs
		STACKS.clear();
		Random cr = new Random(77);
		for (int i = 0; i < 9; i++) {
			double a = i / 9.0 * Math.PI * 2 + 0.4 + (cr.nextDouble() - 0.5) * 0.3, d = 84 + cr.nextDouble() * 16;
			int h = 55 + cr.nextInt(36), base = -14 + cr.nextInt(11);
			int cx = (int) Math.round(Math.cos(a) * d), cz = (int) Math.round(Math.sin(a) * d);
			chimney(s, cx, cz, h, base, brick, trim, slag, rock, rock2);
			STACKS.add(new Vec3(cx + 0.5, base + h, cz + 0.5));
		}
	}

	private static long key(int x, int z) {
		return ((long) x << 32) ^ (z & 0xffffffffL);
	}

	private static double wrap(double a) {
		while (a > Math.PI) a -= Math.PI * 2;
		while (a < -Math.PI) a += Math.PI * 2;
		return a;
	}

	private static void anvil(ArenaShape.Sink s, double cx, double cz, double turn, BlockState iron, BlockState steel, BlockState hole) {
		double ca = Math.cos(turn), sa = Math.sin(turn);
		record P(ArenaShape.Sink s, double cx, double cz, double ca, double sa) {
			void put(int u, int v, int y, BlockState st) {
				s.put((int) Math.round(cx + u * ca - v * sa), y, (int) Math.round(cz + u * sa + v * ca), st);
			}
		}
		P p = new P(s, cx, cz, ca, sa);
		for (int u = -5; u <= 5; u++) for (int v = -3; v <= 3; v++) for (int y = 0; y < 2; y++) p.put(u, v, y, iron);
		for (int u = -3; u <= 3; u++) for (int v = -2; v <= 2; v++) for (int y = 2; y < 5; y++) p.put(u, v, y, iron);
		for (int u = -7; u <= 7; u++) for (int v = -3; v <= 3; v++) for (int y = 5; y < 9; y++) p.put(u, v, y, y == 8 ? steel : iron);
		for (int u = 8; u <= 12; u++) {
			double t = (u - 7) / 6.0;
			for (int v = -3; v <= 3; v++)
				for (int y = 5; y < 9; y++)
					if (Math.abs(v) <= 3 * (1 - t) + 0.3 && (8 - y) <= 3.5 * (1 - t) + 0.3) p.put(u, v, y, y == 8 ? steel : iron);
		}
		p.put(-6, 0, 8, hole);
		p.put(-7, 0, 8, hole);
	}

	private static void chimney(ArenaShape.Sink s, int cx, int cz, int h, int base, BlockState brick, BlockState band, BlockState mouth,
			BlockState rock, BlockState rock2) {
		for (int y = base - 18; y < base; y++) {
			double rr = 5 * (1 - (base - y) / 20.0);
			for (int x = (int) (cx - rr - 2); x <= cx + rr + 2; x++)
				for (int z = (int) (cz - rr - 2); z <= cz + rr + 2; z++)
					if (Math.hypot(x - cx, z - cz) < rr + 2) s.put(x, y, z, (ArenaShape.hash(x, y, z) & 7) == 0 ? rock2 : rock);
		}
		for (int y = base; y < base + h; y++) {
			int half = y < base + 4 || y >= base + h - 3 ? 4 : 3;
			for (int x = cx - half; x <= cx + half; x++)
				for (int z = cz - half; z <= cz + half; z++) {
					boolean edge = Math.abs(x - cx) == half || Math.abs(z - cz) == half;
					if (!edge) {
						if (y == base + h - 2) s.put(x, y, z, mouth);
						continue;
					}
					s.put(x, y, z, (y - base) % 12 == 0 || y == base + h - 1 ? band : brick);
				}
		}
	}
}
