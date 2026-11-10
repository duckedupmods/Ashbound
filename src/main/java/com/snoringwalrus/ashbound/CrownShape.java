package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;

/**
 * The Crown Gate, the last arena (Act V): what's on the far side of the oldest crack, under the Lord's Keep. A floor of
 * black iron 124 blocks across; the five Fires burning in braziers on a pentagon near its edge, each joined to the middle
 * by a spoke of its own light (stand by one and it mends you); the Founder's anvil-throne at the north; round it all the
 * points of a colossal crown, iron spires leaning out over the void (never over the floor); far off, the sky cracked
 * open in seams of light. A dark red night.
 */
public final class CrownShape {
	private CrownShape() {}

	public static final int R = 62;
	public static final Vec3 BOSS = new Vec3(0.5, 0, 34.5);
	/** the five braziers (relative), for the mending */
	public static final List<Vec3> BRAZIERS = new ArrayList<>();

	private static BlockState b(String id) {
		Block k = BuiltInRegistries.BLOCK.get(ResourceLocation.parse(id.contains(":") ? id : "ashbound:" + id));
		return (k == Blocks.AIR ? Blocks.STONE : k).defaultBlockState();
	}

	public static void blocks(ArenaShape.Sink into) {
		ArenaShape.Sink s = (x, y, z, st) -> {
			if (y >= 0 && Math.abs(x) <= 6 && z >= 27 && z <= 42) return;      // room where he rises
			into.put(x, y, z, st);
		};
		BlockState plate = b("blackiron_plate"), seam = b("soot_tiles"), iron = b("kiln_iron"), bronze = b("bronze_plating"), rock = b("cinder_strata");
		BlockState[] fires = {b("glowing_coals"), b("sea_glow"), b("boiler_glow"), b("witchlight"), b("corona_light")};
		BlockState crack = b("rune_glow");
		Random r = new Random(5);
		for (int x = -R - 1; x <= R + 1; x++)
			for (int z = -R - 1; z <= R + 1; z++) {
				double rr = Math.hypot(x + 0.5, z + 0.5), a = Math.atan2(z + 0.5, x + 0.5);
				if (rr > R + 0.5) continue;
				int bot = -(int) (36 * (1 - Math.pow(rr / (R + 1), 1.4)) + 3 * Math.sin(a * 5)) - 3;
				for (int y = bot; y < -1; y++) if (y < bot + 2 || rr > R - 3 || y > -4) s.put(x, y, z, rock);
				boolean ring = Math.abs(rr - (R - 1.5)) < 1.0 || Math.abs(rr - 9) < 0.6 || Math.abs(rr - 30) < 0.6;
				s.put(x, -1, z, ring ? bronze : Math.floorMod(x, 6) == 0 || Math.floorMod(z, 6) == 0 ? seam : plate);
			}
		// the five Fires: spokes of their light from the middle to their braziers on a pentagon (one at the south, by the landing)
		BRAZIERS.clear();
		for (int i = 0; i < 5; i++) {
			double a = -Math.PI / 2 + i * Math.PI * 2 / 5;
			for (double d = 9.5; d < 53; d += 0.5) s.put((int) Math.round(Math.cos(a) * d), -1, (int) Math.round(Math.sin(a) * d), fires[i]);
			int cx = (int) Math.round(Math.cos(a) * 54), cz = (int) Math.round(Math.sin(a) * 54);
			for (int x = -2; x <= 2; x++)
				for (int z = -2; z <= 2; z++) {
					s.put(cx + x, 0, cz + z, iron);
					if (Math.abs(x) == 2 || Math.abs(z) == 2) s.put(cx + x, 1, cz + z, bronze);
					else s.put(cx + x, 1, cz + z, fires[i]);
				}
			s.put(cx, 2, cz, fires[i]);
			BRAZIERS.add(new Vec3(cx + 0.5, 0, cz + 0.5));
		}
		// the Founder's anvil-throne at the north
		for (int u = -7; u <= 7; u++)
			for (int v = 48; v <= 56; v++)
				for (int y = 0; y < 10; y++) {
					boolean foot = y < 2 && Math.abs(u) <= 6, waist = y >= 2 && y < 5 && Math.abs(u) <= 3 && v >= 50 && v <= 54;
					boolean face = y >= 5 && y < 8 && v >= 49 && v <= 55, back = y >= 8 && Math.abs(u) <= 5 && v >= 54;
					if (foot || waist || face || back) s.put(u, y, v, y == 7 && !back ? bronze : iron);
				}
		// the crown: ten iron spires round it, leaning out over the void, gold-banded, a fire on each point
		for (int i = 0; i < 10; i++) {
			double a = i / 10.0 * Math.PI * 2 + 0.31, d0 = 70;
			int h = 34 + r.nextInt(18);
			for (int y = -8; y < h; y++) {
				double t = Math.max(0, (double) y / h), d = d0 + 9 * t * t;
				int half = (int) Math.round(3.5 * (1 - 0.8 * t));
				int cx = (int) Math.round(Math.cos(a) * d), cz = (int) Math.round(Math.sin(a) * d);
				for (int x = -half; x <= half; x++)
					for (int z = -half; z <= half; z++)
						if (Math.abs(x) + Math.abs(z) <= half + 1) s.put(cx + x, y, cz + z, y % 9 == 0 ? bronze : iron);
				if (y == h - 1) s.put(cx, h, cz, fires[i % 5]);
			}
		}
		// the sky cracked open: seams of light far off round it, upright and jagged
		for (int i = 0; i < 14; i++) {
			double a = r.nextDouble() * Math.PI * 2, d = 112 + r.nextDouble() * 18;
			int x = (int) (Math.cos(a) * d), z = (int) (Math.sin(a) * d), y0 = 10 + r.nextInt(30), len = 20 + r.nextInt(40);
			for (int k = 0; k < len; k++) {
				if (r.nextFloat() < 0.35f) x += r.nextBoolean() ? 1 : -1;
				s.put(x, y0 + k, z, crack);
			}
		}
	}
}
