package com.snoringwalrus.ashbound;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import net.minecraft.core.Direction;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

/**
 * Tight hitboxes for the modelled props (tools/prop_shapes.py packs them from the block models), so
 * the things on a counter no longer block a click on whoever stands behind it. Boxes are given for a
 * prop facing north and turned like the model.
 */
final class PropShapes {
	private static final Map<String, int[]> BOXES = load();
	private static final Map<String, VoxelShape[]> CACHE = new ConcurrentHashMap<>();

	private PropShapes() {}

	private static Map<String, int[]> load() {
		Map<String, int[]> out = new HashMap<>();
		try (InputStream in = PropShapes.class.getResourceAsStream("/ashbound/prop_shapes.txt")) {
			if (in == null) return out;
			BufferedReader r = new BufferedReader(new InputStreamReader(in, StandardCharsets.UTF_8));
			for (String line; (line = r.readLine()) != null; ) {
				String[] t = line.trim().split(" ");
				if (t.length < 2) continue;
				int[] b = new int[t.length - 2];
				for (int i = 0; i < b.length; i++) b[i] = Integer.parseInt(t[i + 2]);
				out.put(t[0] + "/" + t[1], b);
			}
		} catch (Exception e) {
			Ashbound.LOG.warn("prop hitboxes not loaded", e);
		}
		return out;
	}

	/** Part p of the block, facing f; the fallback when the prop has no packed boxes. */
	static VoxelShape of(Block block, int part, Direction f, VoxelShape fallback) {
		String key = BuiltInRegistries.BLOCK.getKey(block).getPath() + "/" + part;
		VoxelShape[] turned = CACHE.computeIfAbsent(key, k -> {
			int[] b = BOXES.get(k);
			if (b == null) return new VoxelShape[0];
			VoxelShape[] s = new VoxelShape[4];
			for (Direction d : Direction.Plane.HORIZONTAL) {
				VoxelShape v = Shapes.empty();
				for (int i = 0; i + 5 < b.length; i += 6)
					v = Shapes.or(v, PropBlock.Stall.turned(d, b[i], b[i + 1], b[i + 2], b[i + 3], b[i + 4], b[i + 5]));
				s[d.get2DDataValue()] = v.optimize();
			}
			return s;
		});
		return turned.length == 0 ? fallback : turned[f.get2DDataValue()];
	}
}
