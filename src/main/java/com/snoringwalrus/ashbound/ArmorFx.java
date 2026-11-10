package com.snoringwalrus.ashbound;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

import com.google.gson.JsonParser;

import net.minecraft.resources.ResourceLocation;

/**
 * What a designed armour set does while worn, from /ashbound/armor_fx.json (tools/armorsets.py): its fire flickers through
 * a run of sheets, which Epic Fight asks for every frame.
 */
public final class ArmorFx {
	private ArmorFx() {}

	private static final long FRAME_MS = 110;
	private static final Map<String, ResourceLocation[]> SETS = load();

	private static Map<String, ResourceLocation[]> load() {
		Map<String, ResourceLocation[]> out = new HashMap<>();
		try (InputStream in = ArmorFx.class.getResourceAsStream("/ashbound/armor_fx.json")) {
			if (in == null) return out;
			for (var e : JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject().entrySet()) {
				ResourceLocation[] sheets = new ResourceLocation[e.getValue().getAsInt()];
				for (int i = 0; i < sheets.length; i++)
					sheets[i] = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/models/armor/" + e.getKey() + "_fr" + i + ".png");
				out.put(e.getKey(), sheets);
			}
		} catch (java.io.IOException ex) {
			throw new IllegalStateException(ex);
		}
		return out;
	}

	/** This moment's sheet for a set, or null for a set with no fire of its own. */
	static ResourceLocation sheet(String set) {
		ResourceLocation[] sheets = SETS.get(set);
		return sheets == null ? null : sheets[(int) (System.currentTimeMillis() / FRAME_MS % sheets.length)];
	}
}
