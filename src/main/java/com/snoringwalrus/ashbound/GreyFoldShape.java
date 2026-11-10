package com.snoringwalrus.ashbound;

import java.util.Random;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/**
 * The Grey Fold, the Ash Shepherd's arena (tools/blender/ash_arena.py is the look): a burnt hill-town's square torn out
 * of the world and floating in a red ash-sky. Flagstones 120 blocks across, worn into rings, half under drifts of ash; a
 * dry fountain in the middle where the party lands; round the edge the roofless shells of burnt houses, their windows
 * still glowing like embers (cover); dead trees, arcs of charred fold-hurdles, iron lamp posts with coals in them; the
 * great fallen bell at the north end, where the Shepherd walks in; the island's edge ragged, a rock root under it. Open to
 * the sky. Same every time (fixed seeds).
 */
public final class GreyFoldShape {
	private GreyFoldShape() {}

	public static final int R_SQ = 60, R_EDGE = 64;
	/** he walks in from the bell, facing the fountain */
	public static final Vec3 BOSS = new Vec3(0.5, 0, 34.5);

	private static BlockState b(String id) {
		Block k = BuiltInRegistries.BLOCK.get(ResourceLocation.parse(id.contains(":") ? id : "ashbound:" + id));
		return (k == Blocks.AIR ? Blocks.STONE : k).defaultBlockState();
	}

	static double edge(double a) {
		return R_EDGE - 3 * (0.5 + 0.5 * Math.sin(a * 5 + 0.7)) - 2 * (0.5 + 0.5 * Math.sin(a * 13));
	}

	public static void blocks(ArenaShape.Sink into) {
		java.util.Map<Long, BlockState> all = new java.util.LinkedHashMap<>();
		// nothing above the ground where he comes in
		ArenaShape.Sink s = (x, y, z, st) -> {
			if (y >= 0 && Math.abs(x) <= 5 && z >= 28 && z <= 41) return;
			all.put(net.minecraft.core.BlockPos.asLong(x, y, z), st);
		};
		raise(s);
		// last, whatever's left hanging in the air (a stray branch end, a wall corner turned off the grid) comes away
		for (boolean again = true; again; ) {
			again = false;
			for (var it = all.entrySet().iterator(); it.hasNext(); ) {
				var p = net.minecraft.core.BlockPos.of(it.next().getKey());
				if (p.getY() < 1 || all.containsKey(p.below().asLong())) continue;
				boolean held = false;
				for (var d : net.minecraft.core.Direction.Plane.HORIZONTAL) if (all.containsKey(p.relative(d).asLong())) held = true;
				if (!held) {
					it.remove();
					again = true;
				}
			}
		}
		for (var e : all.entrySet()) {
			var p = net.minecraft.core.BlockPos.of(e.getKey());
			into.put(p.getX(), p.getY(), p.getZ(), e.getValue());
		}
	}

	private static void raise(ArenaShape.Sink s) {
		BlockState rock = b("cinder_strata"), flag = b("ashen_flags"), flag2 = b("gorge_flags"), kerb = b("ashstone_quoin"), ash = b("ash_bank");
		BlockState wall = b("ashstone_bricks"), cracked = b("cracked_ashstone_bricks"), timber = b("soot_planks"), coal = b("glowing_coals");
		BlockState hurdle = b("soot_planks"), hurdleTop = b("soot_plank_slab"), iron = b("kiln_iron"), bronze = b("bell_bronze");
		Random r = new Random(91);
		for (int x = -R_EDGE - 1; x <= R_EDGE + 1; x++)
			for (int z = -R_EDGE - 1; z <= R_EDGE + 1; z++) {
				double rr = Math.hypot(x + 0.5, z + 0.5), a = Math.atan2(z + 0.5, x + 0.5), er = edge(a);
				if (rr > er) continue;
				// the rock root it was torn up with, deep in the middle, ragged; only its skin
				int bot = -(int) (44 * (1 - Math.pow(rr / (R_EDGE + 1), 1.6)) + 4 * Math.sin(a * 4) + (ArenaShape.hash(x, 0, z) & 3)) - 2;
				for (int y = bot; y < -1; y++) if (y < bot + 3 || rr > er - 3 || y > -4) s.put(x, y, z, rock);
				boolean ring = Math.abs(rr - 18) < 1.2 || Math.abs(rr - 34) < 1.0;
				s.put(x, -1, z, ring ? kerb : Math.floorMod(x * 7 + z * 13, 5) == 0 ? flag2 : flag);
				double drift = Math.sin(x * 0.21 + z * 0.13) + Math.sin(x * 0.07 - z * 0.19) * 1.3 + (ArenaShape.hash(x, 5, z) & 7) / 14.0;
				if ((drift > 1.0 || rr > er - 6 && (ArenaShape.hash(x, 6, z) & 3) != 0) && rr > 10) s.put(x, 0, z, ash);
			}
		// the dry fountain: a low round basin, ash in the bottom
		for (int x = -10; x <= 10; x++)
			for (int z = -10; z <= 10; z++) {
				double rr = Math.hypot(x + 0.5, z + 0.5);
				if (rr > 8.2 && rr < 9.6) {
					s.put(x, 0, z, kerb);
					if (Math.floorMod(x + z, 6) != 0) s.put(x, 1, z, kerb);          // broken in places: ways in
				}
			}
		// the burnt houses round the edge (none at the north, where the bell lies)
		for (int i = 0; i < 11; i++) {
			double a = i / 11.0 * Math.PI * 2 + (r.nextDouble() - 0.5) * 0.2;
			double north = Math.abs(((a - Math.PI / 2) + Math.PI) % (Math.PI * 2) - Math.PI);
			if (north < 0.35) continue;
			double d = 47 + r.nextDouble() * 6;
			house(s, Math.cos(a) * d, Math.sin(a) * d, a + Math.PI / 2, 4 + r.nextInt(3), 3 + r.nextInt(2), 7 + r.nextInt(5), wall, cracked, timber, coal, r);
		}
		// dead trees
		for (int i = 0; i < 9; i++) {
			double a = r.nextDouble() * Math.PI * 2, d = 24 + r.nextDouble() * 18;
			int cx = (int) (Math.cos(a) * d), cz = (int) (Math.sin(a) * d), h = 8 + r.nextInt(6);
			if (Math.abs(cx) <= 6 && cz >= 26) continue;
			for (int y = 0; y < h; y++) s.put(cx, y, cz, timber);
			for (int k = 0; k < 4; k++) {
				double ba = r.nextDouble() * Math.PI * 2;
				int y0 = h / 2 + r.nextInt(Math.max(1, h / 2)), len = 3 + r.nextInt(4);
				line(s, cx, y0, cz, (int) Math.round(cx + Math.cos(ba) * len), y0 + len / 2, (int) Math.round(cz + Math.sin(ba) * len), timber);
			}
		}
		// the fold: arcs of charred hurdles, gaps to go through
		for (int k = 0; k < 3; k++) {
			double a0 = r.nextDouble() * Math.PI * 2, d = 24 + r.nextDouble() * 14;
			for (int t = 0; t < 26; t++) {
				if (t % 7 == 6) continue;
				double a = a0 + t / d;
				int x = (int) Math.round(Math.cos(a) * d), z = (int) Math.round(Math.sin(a) * d);
				s.put(x, 0, z, hurdle);
				if (t % 3 == 0) s.put(x, 1, z, hurdleTop);
			}
		}
		// lamp posts, coals burning in them
		for (int i = 0; i < 10; i++) {
			double a = i / 10.0 * Math.PI * 2 + 0.3, d = i % 2 == 1 ? 26 : 40;
			int x = (int) (Math.cos(a) * d), z = (int) (Math.sin(a) * d);
			for (int y = 0; y < 4; y++) s.put(x, y, z, iron);
			s.put(x, 4, z, coal);
		}
		// the great fallen bell on its side at the north, cracked open at the lip
		for (int x = -7; x <= 7; x++)
			for (int z = -6; z <= 6; z++)
				for (int y = 0; y < 12; y++) {
					double rr = Math.hypot(x, y - 5.5), prof = 4.5 + (z + 6) / 12.0 * 3.2;
					if (rr > prof - 1.8 && rr < prof + 0.2 && !(z > 4 && rr < prof - 0.6)) s.put(x, y, 50 + z, bronze);
				}
	}

	private static void house(ArenaShape.Sink s, double cx, double cz, double turn, int w, int d, int h, BlockState wall, BlockState cracked,
			BlockState timber, BlockState coal, Random r) {
		double ca = Math.cos(turn), sa = Math.sin(turn);
		for (int u = -w; u <= w; u++)
			for (int v = -d; v <= d; v++) {
				if (Math.abs(u) != w && Math.abs(v) != d) continue;
				int top = top(u, v, h, cx);
				for (int y = 0; y < top; y++) {
					boolean win = (y == 2 || y == 3) && Math.floorMod(u, 3) == 0 && Math.abs(u) < w && Math.abs(v) == d;
					boolean door = Math.abs(u) <= 1 && v == -d && y < 3;
					if (door) continue;
					BlockState st = win ? coal : y == top - 1 && r.nextFloat() < 0.3f ? timber : (ArenaShape.hash(u, y, v) & 3) == 0 ? cracked : wall;
					s.put((int) Math.round(cx + u * ca - v * sa), y, (int) Math.round(cz + u * sa + v * ca), st);
				}
			}
		for (int k = 0; k < 2; k++) {                       // charred beams across what was the roof
			int uu = -w + 1 + r.nextInt(Math.max(1, 2 * w - 1));
			int y = Math.min(top(uu, -d, h, cx), top(uu, d, h, cx));      // resting on what's left of both walls
			if (y < 3) continue;
			for (int v = -d; v <= d; v++) s.put((int) Math.round(cx + uu * ca - v * sa), y, (int) Math.round(cz + uu * sa + v * ca), timber);
		}
	}

	/** a branch from one block to another, one step along one axis at a time, so every block touches the last face to face */
	private static void line(ArenaShape.Sink s, int x, int y, int z, int tx, int ty, int tz, BlockState st) {
		while (x != tx || y != ty || z != tz) {
			int dx = tx - x, dy = ty - y, dz = tz - z;
			if (Math.abs(dx) >= Math.abs(dz) && Math.abs(dx) >= Math.abs(dy) * 2) x += Integer.signum(dx);
			else if (Math.abs(dz) >= Math.abs(dy) * 2) z += Integer.signum(dz);
			else y += Integer.signum(dy);
			s.put(x, y, z, st);
		}
	}

	/** how high a burnt wall still stands here */
	private static int top(int u, int v, int h, double cx) {
		return h - (int) (Math.abs(Math.sin(u * 0.9 + v * 0.7 + cx)) * h * 0.6);
	}
}
