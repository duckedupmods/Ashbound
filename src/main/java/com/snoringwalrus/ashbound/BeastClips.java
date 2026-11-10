package com.snoringwalrus.ashbound;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

/**
 * A beast's animations (tools/beastkit.py writes /ashbound/beasts/NAME.json from tools/beasts/NAME.py): read by the server
 * for when its blows land (events, reach, arc) and by the client to pose it. Every key is a turn in degrees on top of the
 * rest pose (x, y, z) at a tick, eased between keys; hips move the whole body (blocks).
 */
public final class BeastClips {
	public static final class Clip {
		public final String name;
		public final int len;
		public final boolean loop;
		public final float stride;
		final Map<String, float[][]> bones = new HashMap<>();
		float[][] hips = new float[0][];
		public final Map<String, int[]> events = new HashMap<>();
		public final Map<String, float[]> nums = new HashMap<>();

		Clip(String name, JsonObject o) {
			this.name = name;
			len = o.get("len").getAsInt();
			loop = o.has("loop") && o.get("loop").getAsBoolean();
			stride = o.has("stride") ? o.get("stride").getAsFloat() : 0;
			for (Map.Entry<String, JsonElement> e : o.getAsJsonObject("bones").entrySet()) bones.put(e.getKey(), keys(e.getValue().getAsJsonArray()));
			if (o.has("hips")) hips = keys(o.getAsJsonArray("hips"));
			if (o.has("events"))
				for (Map.Entry<String, JsonElement> e : o.getAsJsonObject("events").entrySet()) {
					JsonArray a = e.getValue().getAsJsonArray();
					int[] ts = new int[a.size()];
					for (int i = 0; i < ts.length; i++) ts[i] = a.get(i).getAsInt();
					events.put(e.getKey(), ts);
				}
			for (Map.Entry<String, JsonElement> e : o.entrySet()) {
				if (e.getValue().isJsonPrimitive() && e.getValue().getAsJsonPrimitive().isNumber() && !e.getKey().equals("len") && !e.getKey().equals("stride"))
					nums.put(e.getKey(), new float[] {e.getValue().getAsFloat()});
				else if (e.getValue().isJsonArray() && !e.getKey().equals("hips")) {
					JsonArray a = e.getValue().getAsJsonArray();
					if (!a.isEmpty() && a.get(0).isJsonPrimitive()) {
						float[] v = new float[a.size()];
						for (int i = 0; i < v.length; i++) v[i] = a.get(i).getAsFloat();
						nums.put(e.getKey(), v);
					}
				}
			}
		}

		public float num(String k, float or) {
			float[] v = nums.get(k);
			return v == null ? or : v[0];
		}

		public float[] nums(String k) {
			return nums.get(k);
		}

		public boolean at(String event, int t) {
			int[] ts = events.get(event);
			if (ts == null) return false;
			for (int x : ts) if (x == t) return true;
			return false;
		}

		public boolean has(String event) {
			return events.containsKey(event);
		}

		public java.util.Set<String> boneNames() {
			return bones.keySet();
		}

		/** a bone's turn at t (ticks, fractions allowed) */
		public void bone(String b, float t, float[] out) {
			sample(bones.get(b), t, out);
		}

		public void hips(float t, float[] out) {
			sample(hips, t, out);
		}

		private void sample(float[][] k, float t, float[] out) {
			out[0] = out[1] = out[2] = 0;
			if (k == null || k.length == 0) return;
			if (loop) {
				t %= len;
				if (t < 0) t += len;
			}
			if (t <= k[0][0] && !loop) {
				copy(k[0], out);
				return;
			}
			for (int i = 0; i < k.length; i++) {
				float[] a = k[i];
				float[] b;
				float tb;
				if (i + 1 < k.length) {
					b = k[i + 1];
					tb = b[0];
				} else if (loop) {
					b = k[0];
					tb = k[0][0] + len;
				} else {
					copy(a, out);
					return;
				}
				float ta = a[0];
				if (t < ta && i == 0 && loop) {   // before the first key of a loop: between the last and the first
					float[] l = k[k.length - 1];
					float f = ease((t + len - l[0]) / Math.max(1e-4f, ta + len - l[0]));
					for (int c = 0; c < 3; c++) out[c] = l[c + 1] + (a[c + 1] - l[c + 1]) * f;
					return;
				}
				if (t >= ta && t <= tb) {
					float f = ease((t - ta) / Math.max(1e-4f, tb - ta));
					for (int c = 0; c < 3; c++) out[c] = a[c + 1] + (b[c + 1] - a[c + 1]) * f;
					return;
				}
			}
			copy(k[k.length - 1], out);
		}

		private static void copy(float[] k, float[] out) {
			out[0] = k[1];
			out[1] = k[2];
			out[2] = k[3];
		}

		private static float ease(float f) {
			f = Math.max(0, Math.min(1, f));
			return f * f * (3 - 2 * f);
		}

		private static float[][] keys(JsonArray a) {
			float[][] k = new float[a.size()][];
			for (int i = 0; i < k.length; i++) {
				JsonArray r = a.get(i).getAsJsonArray();
				k[i] = new float[] {r.get(0).getAsFloat(), r.get(1).getAsFloat(), r.get(2).getAsFloat(), r.get(3).getAsFloat()};
			}
			return k;
		}
	}

	public static final class Set {
		public final Map<String, Clip> clips = new LinkedHashMap<>();
		public final List<String> names = new ArrayList<>();
		public float height = 2, length = 3;

		public Clip get(String n) {
			return clips.get(n);
		}

		public int index(String n) {
			return names.indexOf(n);
		}

		public Clip at(int i) {
			return i < 0 || i >= names.size() ? null : clips.get(names.get(i));
		}
	}

	private static final Map<String, Set> SETS = new ConcurrentHashMap<>();
	private static final Set EMPTY = new Set();

	private BeastClips() {}

	/** the clips of a Legend (by its rig: rime_penitent), loaded once */
	public static Set of(String rig) {
		return SETS.computeIfAbsent(rig, r -> {
			try (InputStream in = BeastClips.class.getResourceAsStream("/ashbound/beasts/" + r + ".json")) {
				if (in == null) return EMPTY;
				JsonObject o = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
				Set s = new Set();
				s.height = o.has("height") ? o.get("height").getAsFloat() : 2;
				s.length = o.has("length") ? o.get("length").getAsFloat() : 3;
				for (Map.Entry<String, JsonElement> e : o.getAsJsonObject("clips").entrySet()) {
					s.clips.put(e.getKey(), new Clip(e.getKey(), e.getValue().getAsJsonObject()));
					s.names.add(e.getKey());
				}
				return s;
			} catch (Exception e) {
				Ashbound.LOG.error("beast clips " + r + " not loaded", e);
				return EMPTY;
			}
		});
	}
}
