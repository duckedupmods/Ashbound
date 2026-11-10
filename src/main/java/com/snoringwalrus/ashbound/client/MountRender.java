package com.snoringwalrus.ashbound.client;

import java.io.InputStreamReader;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.Mount;
import com.snoringwalrus.ashbound.Mounts;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import org.joml.Matrix3f;
import org.joml.Matrix4f;
import org.joml.Quaternionf;
import org.joml.Vector3f;

/**
 * Draws a mount from tools/voxmounts.py's export: named bones, each turned about world axes through its pivot, all of it worked
 * out here each frame (there's no skeleton to share with Epic Fight's, and no clips).
 *
 * The gaits are a real animal's. Each foot has a stance, planted and sliding back in a straight line, and a quicker swing with
 * the joint folded. A walk places the feet one at a time, a trot in diagonal pairs, a gallop in a run of four. Hips and chest ride
 * up and down on what the legs are doing, the head and neck pump in time with the gait, and the head stays level through it.
 */
public class MountRender extends EntityRenderer<Mount> {
	/** one quad is four corners of x y z u v, then the normal */
	private static final int CORNER = 5, QUAD = CORNER * 4 + 3;
	static final int FPS = 8;
	private static final float TAU = Mth.PI * 2;
	private static final Map<String, Model> MODELS = new ConcurrentHashMap<>();
	private static final Map<String, float[]> BOXES = new ConcurrentHashMap<>();

	/** when each foot starts its stride, of one: left hind, left fore, right hind, right fore */
	private static final float[] WALK = {0, 0.25f, 0.5f, 0.75f}, TROT = {0, 0.5f, 0.5f, 1}, GALLOP = {0, 0.4f, 0.1f, 0.5f}, ROTARY = {0, 0.55f, 0.1f, 0.45f};
	/** how long a foot stays down, of one stride */
	private static final float DUTY_WALK = 0.65f, DUTY_TROT = 0.45f, DUTY_RUN = 0.28f;

	record Bone(String name, int parent, float px, float py, float pz, float[] lit, float[] glow, float[] flame) {}

	record Model(List<Bone> bones, int frames) {}

	/**
	 * How a flying pet's wings sit in its model, so each opens its own way: a bird's hang folded at its sides, a moth's lie flat, a
	 * drake's stand up. open is the turn out to the middle of the beat, reach how far either side of that it goes, tilt how far it
	 * leans nose down in the air, and lean how much more at a full pace.
	 */
	private enum Wings {
		NONE(0, 0, 0, 0), BIRD(1.45f, 0.5f, 0.35f, 0.5f), MOTH(0.25f, 0.6f, 0, 0.2f), DRAKE(-0.6f, 0.45f, 0.2f, 0.35f);

		final float open, reach, tilt, lean;

		Wings(float open, float reach, float tilt, float lean) {
			this.open = open;
			this.reach = reach;
			this.tilt = tilt;
			this.lean = lean;
		}

		static Wings of(Model m) {
			boolean bird = false, moth = false, any = false;
			for (Bone b : m.bones) {
				bird |= b.name.equals("fore_l");
				moth |= b.name.equals("arm_low_l");
				any |= b.name.equals("arm_l");
			}
			return bird ? BIRD : moth ? MOTH : any ? DRAKE : NONE;
		}
	}

	/** a pet's wingbeat, turns a tick */
	private static final float BEAT = 0.85f;

	/** This frame's gait, worked out once and read by every bone. */
	private static final class Now {
		float t, p, move, walk, trot, run, air, turn, look, duty, pitch, neck, low, spine, rear, flap;
		boolean twoLegs, glide;
		float[] run4;
		/** a flying pet's wings, none on a mount */
		Wings wings = Wings.NONE;
	}

	public MountRender(EntityRendererProvider.Context ctx) {
		super(ctx);
		shadowRadius = 0.9f;
	}

	private static float[] floats(JsonArray a) {
		float[] out = new float[a.size()];
		for (int i = 0; i < out.length; i++) out[i] = a.get(i).getAsFloat();
		return out;
	}

	static Model model(String id) {
		return MODELS.computeIfAbsent(id, k -> {
			ResourceLocation at = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "mounts/" + id + ".json");
			try (Reader r = new InputStreamReader(Minecraft.getInstance().getResourceManager().getResourceOrThrow(at).open(), StandardCharsets.UTF_8)) {
				JsonObject o = JsonParser.parseReader(r).getAsJsonObject();
				List<Bone> bones = new ArrayList<>();
				Map<String, Integer> index = new HashMap<>();
				for (var e : o.getAsJsonArray("bones")) {
					JsonObject b = e.getAsJsonObject();
					float[] p = floats(b.getAsJsonArray("pivot"));
					int parent = b.get("parent").isJsonNull() ? -1 : index.get(b.get("parent").getAsString());
					index.put(b.get("name").getAsString(), bones.size());
					bones.add(new Bone(b.get("name").getAsString(), parent, p[0], p[1], p[2], floats(b.getAsJsonArray("lit")), floats(b.getAsJsonArray("glow")), floats(b.getAsJsonArray("flame"))));
				}
				return new Model(bones, o.get("frames").getAsInt());
			} catch (java.io.IOException ex) {
				throw new IllegalStateException(at.toString(), ex);
			}
		});
	}

	/** Reads every model off the render thread, so the first look at one doesn't stall a frame. */
	public static void preload() {
		CompletableFuture.runAsync(() -> Mounts.ALL.forEach(k -> model(k.id())));
	}

	public static boolean ready(String id) {
		return MODELS.containsKey(id);
	}

	private static ResourceLocation texture(Mount e, String end) {
		return ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/entity/mount_" + e.kind.id() + end + ".png");
	}

	@Override
	public ResourceLocation getTextureLocation(Mount e) {
		return texture(e, "");
	}

	@Override
	public void render(Mount e, float yaw, float pt, PoseStack ps, MultiBufferSource buf, int light) {
		if (ready(e.kind.id())) {
			ps.pushPose();
			ps.translate(0, Mth.lerp(pt, e.sagO, e.sag), 0);
			ps.mulPose(Axis.YP.rotationDegrees(-Mth.rotLerp(pt, e.yBodyRotO, e.yBodyRot)));
			float k = e.kind.scale() * e.size(pt);
			ps.scale(k, k, k);
			draw(e, pt, ps, buf, light);
			ps.popPose();
		} else {
			preload();
		}
		super.render(e, yaw, pt, ps, buf, light);
	}

	/** For a screen: at the model's own size, its middle where the pose stack is, so it turns on the spot. */
	public static void show(Mount e, float pt, PoseStack ps, MultiBufferSource buf) {
		float[] b = box(e);
		ps.pushPose();
		ps.translate(-b[0], -b[1], -b[2]);
		draw(e, pt, ps, buf, LightTexture.FULL_BRIGHT);
		ps.popPose();
	}

	/** The mount standing: middle x, y, z, then how far it reaches from that middle sideways and up. */
	public static float[] box(Mount e) {
		return BOXES.computeIfAbsent(e.kind.id(), id -> {
			Model m = model(id);
			Matrix4f[] world = pose(m, stand(e));
			float[] lo = {1e9f, 1e9f, 1e9f}, hi = {-1e9f, -1e9f, -1e9f};
			Vector3f v = new Vector3f();
			for (int i = 0; i < world.length; i++) {
				Bone b = m.bones.get(i);
				for (float[] a : new float[][] {b.lit, b.glow, b.flame})
					for (int q = 0; q < a.length; q += QUAD)
						for (int c = 0; c < 4; c++) {
							world[i].transformPosition(a[q + c * CORNER], a[q + c * CORNER + 1], a[q + c * CORNER + 2], v);
							for (int k = 0; k < 3; k++) {
								lo[k] = Math.min(lo[k], v.get(k));
								hi[k] = Math.max(hi[k], v.get(k));
							}
						}
			}
			return new float[] {(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, (lo[2] + hi[2]) / 2, (float) Math.hypot(hi[0] - lo[0], hi[2] - lo[2]) / 2, (hi[1] - lo[1]) / 2};
		});
	}

	private static Now stand(Mount e) {
		Now n = new Now();
		n.twoLegs = e.kind.glides();
		n.walk = 1;
		n.duty = DUTY_WALK;
		n.run4 = GALLOP;
		return n;
	}

	private static float blend(Now n, float walk, float trot, float run) {
		return walk * n.walk + trot * n.trot + run * n.run;
	}

	private static Now now(Mount e, float pt) {
		Now n = new Now();
		float g = Mth.lerp(pt, e.gaitO, e.gait);
		String id = e.kind.id();
		n.t = e.tickCount + pt;
		n.p = Mth.frac(Mth.lerp(pt, e.strideO, e.stride));
		n.air = Mth.lerp(pt, e.airO, e.air);
		n.turn = Mth.lerp(pt, e.turnO, e.turn);
		n.look = Mth.lerp(pt, e.lookO, e.look);
		n.twoLegs = e.kind.glides();
		n.glide = e.soaring();
		n.flap = Mth.lerp(pt, e.flapO, e.flap);
		// the gaits are what its legs are doing on the ground: in the air none of that bounces the body
		float ground = 1 - n.air;
		n.move = Math.min(1, g * 5) * ground;
		n.run = Mth.clamp((g - 0.6f) / 0.25f, 0, 1) * ground;
		n.trot = (Mth.clamp((g - 0.22f) / 0.2f, 0, 1) - Mth.clamp((g - 0.6f) / 0.25f, 0, 1)) * ground;
		n.walk = 1 - n.run - n.trot;
		n.duty = blend(n, DUTY_WALK, DUTY_TROT, DUTY_RUN);
		n.run4 = id.equals("gravefang") ? ROTARY : GALLOP;
		n.low = switch (id) {
			case "ashmane" -> 0.2f;
			case "gravefang" -> 0.14f;
			case "rimehorn" -> 0.1f;
			default -> 0;
		};
		n.spine = id.equals("gravefang") ? 0.2f : id.equals("rimehorn") ? 0.08f : 0.05f;
		n.rear = e.rear(pt) * (id.equals("thornback") ? 0.14f : id.equals("stormdrake") ? 0.2f : 0.36f);
		// a gallop rocks the whole body, nose down as the forelegs land and up as the hind legs come through
		// and it leans into a flight of steps, nose up climbing them
		n.pitch = n.run * Mth.sin(TAU * (n.p - 0.15f)) * 0.075f + n.walk * n.move * Mth.sin(TAU * 2 * n.p) * 0.012f - 0.07f * n.air + (float) Mth.lerp(pt, e.sagO, e.sag) * 0.3f;
		// the walk nods twice a stride, the trot holds the head still, the gallop pumps once
		n.neck = n.move * (n.walk * Mth.sin(TAU * 2 * (n.p - 0.05f)) * 0.045f + n.run * Mth.sin(TAU * (n.p - 0.35f)) * 0.07f);
		return n;
	}

	/** A leg at p of its stride: returns how far forward (1) or back (-1) it is; flex[0] gets how folded it is. */
	private static float leg(float p, float duty, float[] flex) {
		if (p < duty) {
			flex[0] = 0;
			return 1 - 2 * p / duty;
		}
		float s = (p - duty) / (1 - duty);
		flex[0] = Mth.sin(s * Mth.PI);
		return -1 + 2 * s * s * (3 - 2 * s);
	}

	/** The pose of one bone, as a turn about its pivot. */
	private static void turn(Now n, String name, Quaternionf q, float[] move, float[] flex) {
		switch (name) {
			case "hips" -> {
				float bounce = n.move * (n.walk * Mth.cos(TAU * 2 * n.p) * 0.018f + n.trot * Mth.cos(TAU * 2 * n.p) * 0.05f + n.run * Mth.sin(TAU * (n.p - 0.1f)) * 0.06f);
				float sway = n.twoLegs ? Mth.sin(TAU * n.p) * 0.09f * n.move : 0;
				q.rotationXYZ(n.pitch - n.rear, sway, n.turn * 0.5f * (n.trot + n.run));
				// the rock is about the middle of the body, not the hips
				move[1] = bounce + n.pitch * 0.5f + Mth.sin(n.t * 0.05f) * 0.012f * (1 - n.move);
			}
			case "torso" -> q.rotationX(n.run * Mth.sin(TAU * (n.p - 0.4f)) * n.spine);
			// a model faces +z with its left at +x, so turning right is a negative turn about y
			case "neck", "neck0" -> q.rotationXYZ(n.neck + n.low * n.run + n.rear * 0.4f + Mth.sin(n.t * 0.05f) * 0.02f, -n.look * 0.3f - n.turn * 0.5f, 0);
			case "neck2" -> q.rotationY(-n.look * 0.15f);
			case "neck1", "neck3", "neck4" -> q.rotationXYZ(Mth.sin(TAU * 2 * n.p - name.charAt(4) * 0.9f) * 0.02f * n.move, -n.look * 0.12f, 0);
			// the head holds level while everything under it moves: that's what makes it read as alive
			case "head" -> q.rotationXYZ(-(n.pitch - n.rear * 0.6f + n.neck + n.low * n.run) * 0.8f + Mth.sin(n.t * 0.05f + 2) * 0.025f, -n.look * 0.45f - n.turn * 0.4f, 0);
			case "jaw" -> q.rotationX(-Math.max(0, Mth.sin(n.t * 0.04f)) * 0.14f - 0.2f * n.run);
			case "tail" -> q.rotationXYZ(-0.14f * n.run + n.move * Mth.sin(TAU * n.p) * 0.05f, Mth.sin(n.t * 0.08f) * 0.14f - n.turn * 0.7f, 0);
			default -> {
				if (name.startsWith("tails")) {
					int i = name.charAt(5) - '0';
					q.rotationY(Mth.sin(n.t * 0.08f - i * 0.7f) * 0.05f + Mth.sin(TAU * n.p - i * 0.6f) * 0.07f * n.move - n.turn * 0.12f);
					return;
				}
				boolean left = name.endsWith("_l");
				float side = left ? 1 : -1;
				boolean up = name.startsWith("thigh_") || name.startsWith("arm_"), low = name.startsWith("shin_") || name.startsWith("fore_"), foot = name.startsWith("foot_") || name.startsWith("hand_");
				boolean hind = name.startsWith("thigh_") || name.startsWith("shin_") || name.startsWith("foot_");
				if (n.wings != Wings.NONE && !hind) {
					// a lower wing and a wingtip each come a little after the wing in front of them
					float beat = Mth.sin(n.t * BEAT - (name.startsWith("arm_low") ? 0.6f : 0));
					if (up) q.rotationZ(side * (n.wings.open + beat * n.wings.reach * (0.8f + 0.2f * n.move)));
					else if (low) q.rotationZ(side * Mth.sin(n.t * BEAT - 1.1f) * 0.5f);
					return;
				}
				if (n.twoLegs && !hind) {
					// the wings: folded up walking, flat to glide, beating when it jumps or holds itself up
					float strong = n.glide ? n.flap : 1, beat = Mth.lerp(strong, Mth.sin(n.t * 0.1f) * 0.05f, Mth.sin(n.t * 0.6f) * 0.5f), open = Math.min(1, Math.max(n.air, n.rear * 5));
					if (up) q.rotationZ(side * ((1 - open) * (0.62f + Mth.sin(n.t * 0.05f) * 0.025f + 0.07f * n.move * Mth.sin(TAU * n.p)) + open * (beat - 0.32f)));
					else if (foot) q.rotationZ(side * -((1 - open) * 2.05f + open * Mth.lerp(strong, 0.04f, 0.4f) * Mth.sin(n.t * 0.6f + 1.1f)));
					return;
				}
				if (!up && !low && !foot) return;
				float start = n.twoLegs ? (left ? 0 : 0.5f) : stride(n, (hind ? 0 : 1) + (left ? 0 : 2));
				float reach = leg(Mth.frac(n.p + start), n.twoLegs ? Math.max(0.4f, n.duty) : n.duty, flex);
				float swing = n.move * (1 - n.air) * blend(n, hind ? 0.28f : 0.32f, hind ? 0.4f : 0.44f, hind ? 0.62f : 0.74f);
				float bend = n.move * (1 - n.air) * flex[0] * blend(n, hind ? 0.75f : 0.95f, hind ? 0.95f : 1.2f, hind ? 1.15f : 1.5f);
				if (n.twoLegs) swing *= 1.2f;
				// rearing, the hind legs stay under it and the forelegs paw the air
				float paw = hind ? 0 : Mth.sin(n.t * (left ? 0.9f : 1.1f)) * 0.5f;
				if (up) q.rotationX(-reach * swing + (hind ? 0.5f : -0.62f) * n.air + n.rear * (hind ? 1 : -1.9f + paw));
				else if (low) q.rotationX(bend + (hind ? 0.1f : 0.85f) * n.air + (hind ? 0 : n.rear * 3.2f));
				else q.rotationX(bend * 0.6f + 0.4f * n.air);
			}
		}
	}

	private static float stride(Now n, int leg) {
		return n.walk * WALK[leg] + n.trot * TROT[leg] + n.run * n.run4[leg];
	}

	private static Matrix4f[] pose(Model m, Now now) {
		int n = m.bones.size();
		Matrix4f[] world = new Matrix4f[n];
		Quaternionf q = new Quaternionf();
		float[] move = new float[3], flex = new float[1];
		for (int i = 0; i < n; i++) {
			Bone b = m.bones.get(i);
			q.identity();
			move[0] = move[1] = move[2] = 0;
			turn(now, b.name, q, move, flex);
			Matrix4f w = b.parent < 0 ? new Matrix4f() : new Matrix4f(world[b.parent]);
			world[i] = w.translate(b.px + move[0], b.py + move[1], b.pz + move[2]).rotate(q).translate(-b.px, -b.py, -b.pz);
		}
		return world;
	}

	private static void draw(Mount e, float pt, PoseStack ps, MultiBufferSource buf, int light) {
		Model m = model(e.kind.id());
		Now now = now(e, pt);
		Matrix4f[] world = pose(m, now);
		int frame = (int) (now.t / 20 * FPS) % m.frames;
		bones(m, world, texture(e, ""), (float) frame / m.frames, now.t, ps, buf, light);
		if (!e.kind.burns()) return;
		// what burns under the hide keeps burning at night
		VertexConsumer hot = buf.getBuffer(RenderType.eyes(texture(e, "_hot")));
		for (int i = 0; i < world.length; i++) {
			ps.pushPose();
			ps.last().pose().mul(world[i]);
			ps.last().normal().mul(new Matrix3f(world[i]));
			quads(hot, ps.last(), m.bones.get(i).lit, 0, LightTexture.FULL_BRIGHT, 0, 0);
			ps.popPose();
		}
	}

	private static void bones(Model m, Matrix4f[] world, ResourceLocation texture, float shift, float t, PoseStack ps, MultiBufferSource buf, int light) {
		VertexConsumer lit = buf.getBuffer(RenderType.entityCutoutNoCull(texture));
		for (int i = 0; i < world.length; i++) {
			Bone b = m.bones.get(i);
			ps.pushPose();
			ps.last().pose().mul(world[i]);
			ps.last().normal().mul(new Matrix3f(world[i]));
			quads(lit, ps.last(), b.lit, 0, light, 0, 0);
			quads(lit, ps.last(), b.glow, 0, LightTexture.FULL_BRIGHT, 0, 0);
			quads(lit, ps.last(), b.flame, shift, LightTexture.FULL_BRIGHT, t, 0.012f);
			ps.popPose();
		}
	}

	/** A pet (client/PetRender), standing on the pose stack: a walking pace from 0 to 1, or its wings going, with no Mount behind it. */
	static void pet(String id, float t, float stride, float pace, boolean flap, float look, PoseStack ps, MultiBufferSource buf, int light) {
		Model m = model("pet_" + id);
		Now n = new Now();
		n.t = t;
		n.p = Mth.frac(stride);
		n.move = pace;
		n.walk = 1;
		n.duty = DUTY_WALK;
		n.run4 = GALLOP;
		n.look = look;
		n.twoLegs = flap;
		n.air = flap ? 1 : 0;
		if (flap) {
			n.wings = Wings.of(m);
			n.pitch = n.wings.tilt + n.wings.lean * pace;
		}
		bones(m, pose(m, n), ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/entity/mount_pet_" + id + ".png"), (float) ((int) (t / 20 * FPS) % m.frames) / m.frames, t, ps, buf, light);
	}

	private static void quads(VertexConsumer to, PoseStack.Pose at, float[] v, float shift, int light, float t, float wave) {
		quads(to, at, v, shift, light, t, wave, 0xFFFFFF);
	}

	static void quads(VertexConsumer to, PoseStack.Pose at, float[] v, float shift, int light, float t, float wave, int rgb) {
		int red = rgb >> 16 & 255, green = rgb >> 8 & 255, blue = rgb & 255;
		for (int q = 0; q < v.length; q += QUAD) {
			float nx = v[q + CORNER * 4], ny = v[q + CORNER * 4 + 1], nz = v[q + CORNER * 4 + 2];
			for (int c = 0; c < 4; c++) {
				int o = q + c * CORNER;
				float x = v[o], y = v[o + 1], z = v[o + 2];
				if (wave > 0) {
					float s = Mth.sin(t * 0.35f + (y + z) * 5);
					x += s * wave * 4;
					y += Mth.cos(t * 0.3f + z * 6) * wave;
				}
				to.addVertex(at, x, y, z).setColor(red, green, blue, 255).setUv(v[o + 3], v[o + 4] + shift)
						.setOverlay(OverlayTexture.NO_OVERLAY).setLight(light).setNormal(at, nx, ny, nz);
			}
		}
	}
}
