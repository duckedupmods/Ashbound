package com.snoringwalrus.ashbound;

import java.util.Random;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/**
 * Veyra's Astral Rings (Act IV): three arenas out past the sky, each a disc of eclipse marble 120 blocks across floating
 * in black space full of stars, star-glass shards and two near planets drifting round it (never overhead). Each has its
 * own floor:
 * <ul>
 * <li>MOTH, the Nebula Moth's: a garden of pale lantern pillars (what draws a moth), a great moth sigil in glowing lines;
 * <li>KNIGHT, Halcyr's: constellations drawn across the floor star to star, a ring of broken star-columns, a dais north;
 * <li>MAGUS, the Orrery Magus's: three raised orbit tracks with gaps, small crystal planets on them for cover.
 * </ul>
 */
public final class AstralShape {
	private AstralShape() {}

	public enum Kind { MOTH, KNIGHT, MAGUS }

	public static final int R = 60;
	public static final Vec3 BOSS = new Vec3(0.5, 0, 32.5);

	private static BlockState b(String id) {
		Block k = BuiltInRegistries.BLOCK.get(ResourceLocation.parse(id.contains(":") ? id : "ashbound:" + id));
		return (k == Blocks.AIR ? Blocks.STONE : k).defaultBlockState();
	}

	public static void moth(ArenaShape.Sink s) {
		blocks(s, Kind.MOTH);
	}

	public static void knight(ArenaShape.Sink s) {
		blocks(s, Kind.KNIGHT);
	}

	public static void magus(ArenaShape.Sink s) {
		blocks(s, Kind.MAGUS);
	}

	static void blocks(ArenaShape.Sink into, Kind kind) {
		ArenaShape.Sink s = (x, y, z, st) -> {                      // nothing above the floor where the boss comes
			if (y >= 0 && Math.abs(x) <= 6 && z >= 26 && z <= 40) return;
			into.put(x, y, z, st);
		};
		BlockState marble = b("eclipse_marble"), dark = b("black_marble"), frieze = b("star_frieze"), strata = b("eclipse_strata");
		BlockState column = b("eclipse_column"), line = b("rune_glow"), star = b("corona_light"), glass = b("weeping_crystal_block");
		BlockState crystal = b("mana_crystal_block"), lampStone = b("crystal_rock"), bricks = b("marble_bricks");
		Random r = new Random(kind.ordinal() * 101 + 7);
		// the disc and its root, tapering to a point far below
		for (int x = -R - 1; x <= R + 1; x++)
			for (int z = -R - 1; z <= R + 1; z++) {
				double rr = Math.hypot(x + 0.5, z + 0.5);
				if (rr > R + 0.5) continue;
				int bot = -(int) (30 * Math.pow(1 - rr / (R + 1), 0.8)) - 3;
				for (int y = bot; y < -1; y++) if (y < bot + 2 || rr > R - 2 || y > -4) s.put(x, y, z, strata);
				boolean ring = Math.abs(rr - (R - 1.5)) < 1.0 || Math.abs(rr - 12) < 0.6;
				s.put(x, -1, z, ring ? frieze : Math.floorMod(x + z, 2) == 0 ? marble : dark);
			}
		// a low rim of broken column stubs round the edge
		for (int i = 0; i < 40; i++) {
			double a = i / 40.0 * Math.PI * 2;
			int x = (int) Math.round(Math.cos(a) * (R - 0.5)), z = (int) Math.round(Math.sin(a) * (R - 0.5)), h = 1 + Math.floorMod(ArenaShape.hash(i, 0, kind.ordinal()), 3);
			for (int y = 0; y < h; y++) s.put(x, y, z, column);
		}
		switch (kind) {
			case MOTH -> {
				// lantern pillars in two rings, each topped with cold light
				for (int i = 0; i < 18; i++) {
					double a = i / 18.0 * Math.PI * 2 + (i % 2) * 0.17, d = i % 2 == 0 ? 30 : 48;
					int x = (int) Math.round(Math.cos(a) * d), z = (int) Math.round(Math.sin(a) * d), h = 4 + (i % 3);
					for (int y = 0; y < h; y++) s.put(x, y, z, lampStone);
					s.put(x, h, z, star);
				}
				// the moth sigil: a body down the middle, four wing-loops, in glowing lines in the floor
				for (int z = -20; z <= 20; z++) s.put(0, -1, z, line);
				for (double t = 0; t < Math.PI * 2; t += 0.02)
					for (int sx : new int[] {-1, 1})
						for (int up : new int[] {-1, 1}) {
							double rr = (up > 0 ? 22 : 15) * Math.abs(Math.sin(2 * t));
							int x = (int) Math.round(sx * Math.abs(Math.cos(t)) * rr), z = (int) Math.round(up * Math.abs(Math.sin(t)) * rr);
							s.put(x, -1, z, line);
						}
			}
			case KNIGHT -> {
				// constellations: stars in the floor joined star to star with thin lines of light
				for (int c = 0; c < 6; c++) {
					double ca = c / 6.0 * Math.PI * 2 + 0.3, cd = 20 + r.nextDouble() * 22;
					int px = (int) (Math.cos(ca) * cd), pz = (int) (Math.sin(ca) * cd);
					for (int k = 0; k < 5; k++) {
						int nx = px + r.nextInt(15) - 7, nz = pz + r.nextInt(15) - 7;
						if (Math.hypot(nx, nz) > R - 4) break;
						for (int t = 0; t <= 20; t++) s.put((int) Math.round(px + (nx - px) * t / 20.0), -1, (int) Math.round(pz + (nz - pz) * t / 20.0), line);
						s.put(px, -1, pz, star);
						px = nx;
						pz = nz;
					}
					s.put(px, -1, pz, star);
				}
				// a ring of tall broken star-columns
				for (int i = 0; i < 12; i++) {
					double a = i / 12.0 * Math.PI * 2;
					int x = (int) Math.round(Math.cos(a) * 44), z = (int) Math.round(Math.sin(a) * 44), h = 6 + r.nextInt(10);
					for (int dx = 0; dx <= 1; dx++)
						for (int dz = 0; dz <= 1; dz++)
							for (int y = 0; y < h - (dx + dz) % 2 * r.nextInt(3); y++) s.put(x + dx, y, z + dz, column);
					s.put(x, h, z, star);
				}
				// the dais at the north, three steps
				for (int x = -10; x <= 10; x++)
					for (int z = 42; z <= 54; z++)
						for (int y = 0; y < 3; y++) if (Math.abs(x) <= 10 - y * 2 && z >= 42 + y * 2) s.put(x, y, z, bricks);
			}
			case MAGUS -> {
				// three raised orbit tracks, a block high, with gaps; small crystal planets on them
				int[] radii = {18, 33, 48};
				for (int i = 0; i < radii.length; i++) {
					int rad = radii[i];
					for (double t = 0; t < Math.PI * 2; t += 0.5 / rad) {
						if (Math.floorMod((int) (t * rad / 6), 5) == 0) continue;
						int x = (int) Math.round(Math.cos(t) * rad), z = (int) Math.round(Math.sin(t) * rad);
						s.put(x, 0, z, frieze);
						s.put(x, -1, z, line);
					}
					for (int p = 0; p < 3 + i; p++) {
						double a = r.nextDouble() * Math.PI * 2;
						int cx = (int) Math.round(Math.cos(a) * rad), cz = (int) Math.round(Math.sin(a) * rad), pr = 2 + i;
						for (int x = -pr; x <= pr; x++)
							for (int y = 0; y <= pr * 2; y++)
								for (int z = -pr; z <= pr; z++)
									if (x * x + (y - pr) * (y - pr) + z * z <= pr * pr + 1) s.put(cx + x, y, cz + z, (y + x) % 3 == 0 ? glass : crystal);
					}
				}
				for (int y = 0; y < 2; y++) for (int x = -2; x <= 2; x++) for (int z = -2; z <= 2; z++) if (Math.abs(x) + Math.abs(z) <= 2 && y == 0) s.put(x, -1, z, star);
			}
		}
		// star-glass shards drifting round it, out past the edge, low (never over the disc)
		for (int i = 0; i < 26; i++) {
			double a = r.nextDouble() * Math.PI * 2, d = 78 + r.nextDouble() * 32;
			int cx = (int) (Math.cos(a) * d), cz = (int) (Math.sin(a) * d), cy = -20 + r.nextInt(40), len = 3 + r.nextInt(6);
			for (int k = 0; k < len; k++) {
				s.put(cx, cy + k, cz, glass);
				if (k < len / 2) {
					s.put(cx + 1, cy + k, cz, glass);
					s.put(cx, cy + k, cz + 1, glass);
				}
			}
		}
		// two planets near enough to touch, far out to the sides: hollow spheres, banded
		for (int p = 0; p < 2; p++) {
			double a = (p == 0 ? 0.6 : 3.6) + kind.ordinal() * 0.7, d = 120;
			int cx = (int) (Math.cos(a) * d), cz = (int) (Math.sin(a) * d), cy = p == 0 ? 10 : -25, pr = p == 0 ? 16 : 11;
			BlockState body = p == 0 ? dark : crystal, band = p == 0 ? frieze : glass;
			for (int x = -pr; x <= pr; x++)
				for (int y = -pr; y <= pr; y++)
					for (int z = -pr; z <= pr; z++) {
						double q = Math.sqrt(x * x + y * y + z * z);
						if (q <= pr && q > pr - 1.5) s.put(cx + x, cy + y, cz + z, Math.floorMod(y, 5) == 0 ? band : body);
					}
		}
	}
}
