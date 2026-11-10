package com.snoringwalrus.ashbound.client;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.Beast;
import com.snoringwalrus.ashbound.BeastClips;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.AABB;
import org.joml.Matrix4f;
import org.joml.Quaternionf;
import org.joml.Vector3f;

/**
 * A world beast drawn from its rig (tools/beastkit.py: models/entity/beast/NAME/rig.json and an .obj a bone, textures/entity/
 * beast/NAME.png) and posed from its clips (BeastClips) every frame: idle, walk (or stalk) and run blended by how fast it's
 * going, its gait's phase from how far it has walked; an attack it's doing laid over that, eased in and out; a flinch when
 * it's hit; its death in place of everything. The head follows what it's looking at. Bones posed as the old BossRig did:
 * parent x (pivot + offset) x turn x rest x -pivot.
 */
public class BeastRender extends EntityRenderer<Beast> {
	private static final int FULL_BRIGHT = 0xF000F0;
	private static final Map<String, Rig> RIGS = new HashMap<>();

	public BeastRender(EntityRendererProvider.Context ctx) {
		super(ctx);
		shadowRadius = 1.2f;
		shadowStrength = 0.8f;
	}

	static final class Bone {
		String name;
		int parent = -1;
		Vector3f pivot, offset;
		Quaternionf rest;
		float[] lit = new float[0], glow = new float[0];
	}

	static final class Rig {
		final List<Bone> bones = new ArrayList<>();
		float ground;
	}

	private static Rig rig(String name) {
		return RIGS.computeIfAbsent(name, n -> {
			Rig r = new Rig();
			String dir = "models/entity/beast/" + n + "/";
			try (Reader rd = new InputStreamReader(Minecraft.getInstance().getResourceManager()
					.getResourceOrThrow(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, dir + "rig.json")).open(), StandardCharsets.UTF_8)) {
				JsonObject j = JsonParser.parseReader(rd).getAsJsonObject();
				r.ground = j.get("ground").getAsFloat();
				Map<String, Integer> index = new HashMap<>();
				for (JsonElement el : j.getAsJsonArray("bones")) {
					JsonObject o = el.getAsJsonObject();
					Bone b = new Bone();
					b.name = o.get("name").getAsString();
					if (!o.get("parent").isJsonNull()) b.parent = index.get(o.get("parent").getAsString());
					b.pivot = vec(o.getAsJsonArray("pivot"));
					b.offset = vec(o.getAsJsonArray("offset"));
					JsonArray q = o.getAsJsonArray("rest");
					b.rest = new Quaternionf(q.get(0).getAsFloat(), q.get(1).getAsFloat(), q.get(2).getAsFloat(), q.get(3).getAsFloat());
					if (o.get("mesh").getAsBoolean()) obj(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, dir + b.name + ".obj"), b);
					index.put(b.name, r.bones.size());
					r.bones.add(b);
				}
			} catch (Exception e) {
				Ashbound.LOG.error("beast rig " + n + " not loaded", e);
				r.bones.clear();
			}
			return r;
		});
	}

	/** an .obj of triangles, one vertex a corner (x y z u v nx ny nz); group "glow" drawn full bright */
	private static void obj(ResourceLocation id, Bone b) throws Exception {
		List<float[]> v = new ArrayList<>(), vt = new ArrayList<>(), vn = new ArrayList<>();
		List<Float> lit = new ArrayList<>(), glow = new ArrayList<>();
		List<Float> into = lit;
		try (BufferedReader r = new BufferedReader(new InputStreamReader(Minecraft.getInstance().getResourceManager().getResourceOrThrow(id).open(), StandardCharsets.UTF_8))) {
			String line;
			while ((line = r.readLine()) != null) {
				String[] p = line.trim().split("\\s+");
				switch (p[0]) {
					case "v" -> v.add(new float[] {f(p[1]), f(p[2]), f(p[3])});
					case "vt" -> vt.add(new float[] {f(p[1]), 1 - f(p[2])});
					case "vn" -> vn.add(new float[] {f(p[1]), f(p[2]), f(p[3])});
					case "g", "o" -> into = p.length > 1 && (p[1].startsWith("glow") || p[1].startsWith("fire")) ? glow : lit;
					case "f" -> {
						for (int k = 2; k + 1 < p.length; k++)
							for (String c : new String[] {p[1], p[k], p[k + 1]}) {
								String[] ix = c.split("/");
								float[] pos = v.get(Integer.parseInt(ix[0]) - 1);
								float[] uv = ix.length > 1 && !ix[1].isEmpty() ? vt.get(Integer.parseInt(ix[1]) - 1) : new float[2];
								float[] n = ix.length > 2 ? vn.get(Integer.parseInt(ix[2]) - 1) : new float[] {0, 1, 0};
								into.add(pos[0]); into.add(pos[1]); into.add(pos[2]);
								into.add(uv[0]); into.add(uv[1]);
								into.add(n[0]); into.add(n[1]); into.add(n[2]);
							}
					}
					default -> {}
				}
			}
		}
		b.lit = arr(lit);
		b.glow = arr(glow);
	}

	@Override
	public ResourceLocation getTextureLocation(Beast e) {
		return ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/entity/beast/" + e.kind.rig() + ".png");
	}

	@Override
	public boolean shouldRender(Beast e, net.minecraft.client.renderer.culling.Frustum f, double x, double y, double z) {
		AABB box = e.getBoundingBox().inflate(e.getBbWidth() * 1.6, e.getBbHeight() * 0.5, e.getBbWidth() * 1.6);
		return e.shouldRender(x, y, z) && (e.noCulling || f.isVisible(box));
	}

	@Override
	public void render(Beast e, float yaw, float pt, PoseStack ps, MultiBufferSource buf, int light) {
		Rig r = rig(e.kind.rig());
		if (!r.bones.isEmpty()) {
			Map<String, float[]> pose = new HashMap<>();
			float[] hips = new float[3];
			pose(e, pt, pose, hips);
			int n = r.bones.size();
			Matrix4f[] world = new Matrix4f[n];
			for (int i = 0; i < n; i++) {
				Bone b = r.bones.get(i);
				Matrix4f parent = b.parent < 0 ? new Matrix4f() : world[b.parent];
				float[] t = pose.get(b.name);
				Quaternionf delta = t == null ? new Quaternionf()
						: new Quaternionf().rotationXYZ(t[0] * Mth.DEG_TO_RAD, t[1] * Mth.DEG_TO_RAD, t[2] * Mth.DEG_TO_RAD);
				Vector3f at = new Vector3f(b.pivot).add(b.offset);
				if (b.parent < 0) at.add(hips[0], hips[1], hips[2]);
				world[i] = new Matrix4f(parent).translate(at).rotate(delta).rotate(b.rest).translate(-b.pivot.x, -b.pivot.y, -b.pivot.z);
			}
			ps.pushPose();
			ps.mulPose(Axis.YP.rotationDegrees(-Mth.rotLerp(pt, e.yBodyRotO, e.yBodyRot)));
			ps.translate(0, -r.ground, 0);
			int overlay = OverlayTexture.pack(OverlayTexture.u(0), OverlayTexture.v(e.hurtTime > 0 && e.deathTime == 0));
			VertexConsumer lit = buf.getBuffer(RenderType.entityCutoutNoCull(getTextureLocation(e)));
			for (int i = 0; i < n; i++) {
				Bone b = r.bones.get(i);
				ps.pushPose();
				ps.mulPose(world[i]);
				emit(ps.last(), lit, b.lit, light, overlay);
				emit(ps.last(), lit, b.glow, FULL_BRIGHT, overlay);
				ps.popPose();
			}
			ps.popPose();
		}
		super.render(e, yaw, pt, ps, buf, light);
	}

	// ---------------------------------------------------------------- the pose

	/** how fast it's going (blocks a tick) and the blend between idle, walk and run that goes with it */
	private static void pose(Beast e, float pt, Map<String, float[]> pose, float[] hips) {
		BeastClips.Set cs = e.clips;
		if (e.deathTime > 0) {
			BeastClips.Clip d = cs.get("death");
			if (d != null) {
				add(d, Math.min(d.len, e.deathTime + pt), 1, pose, hips);
				return;
			}
		}
		double speed = Math.hypot(e.getX() - e.xo, e.getZ() - e.zo);
		float dist = Mth.lerp(pt, e.travelledO, e.travelled), age = e.tickCount + pt;
		BeastClips.Clip idle = cs.get("idle"), walk = cs.get(e.stalking() && cs.get("stalk") != null ? "stalk" : "walk"), run = cs.get("run");
		float wWalk = (float) Mth.clamp((speed - 0.015) / 0.05, 0, 1);
		float wRun = run == null ? 0 : (float) Mth.clamp((speed - 0.17) / 0.08, 0, 1);
		if (e.stalking()) wRun = 0;
		float wIdle = 1 - wWalk;
		wWalk *= 1 - wRun;
		if (idle != null && wIdle > 0) add(idle, age, wIdle, pose, hips);
		if (walk != null && wWalk > 0) add(walk, dist / Math.max(0.1f, walk.stride) * walk.len, wWalk, pose, hips);
		if (run != null && wRun > 0) add(run, dist / Math.max(0.1f, run.stride) * run.len, wRun, pose, hips);
		// the head follows what it looks at
		float look = Mth.wrapDegrees(Mth.rotLerp(pt, e.yHeadRotO, e.yHeadRot) - Mth.rotLerp(pt, e.yBodyRotO, e.yBodyRot));
		look = Mth.clamp(look, -45, 45);
		float pitch = Mth.clamp(Mth.lerp(pt, e.xRotO, e.getXRot()), -25, 25);
		BeastClips.Clip act = e.acting();
		float t = e.actTime(pt);
		if (act != null) {      // eased in over 3 ticks and out over the last 4: the attack replaces the gait
			float w = Math.min(1, Math.min(t / 3f, (act.len - t) / 4f));
			w = Math.max(0, w);
			scale(pose, hips, 1 - w);
			add(act, t, w, pose, hips);
			look *= 1 - w;
			pitch *= 1 - w;
		} else if (e.hurtTime > 0 && cs.get("hurt") != null) {
			BeastClips.Clip h = cs.get("hurt");
			add(h, h.len - e.hurtTime + pt, 1, pose, hips);
		}
		turn(pose, "neck", pitch * 0.4f, look * 0.4f);
		turn(pose, "head", pitch * 0.6f, look * 0.6f);
	}

	private static void add(BeastClips.Clip c, float t, float w, Map<String, float[]> pose, float[] hips) {
		float[] v = new float[3];
		for (String b : c.boneNames()) {
			c.bone(b, t, v);
			for (int i = 0; i < 3; i++) v[i] = net.minecraft.util.Mth.wrapDegrees(v[i]);      // a spin of whole turns blends out as no turn
			float[] p = pose.computeIfAbsent(b, k -> new float[3]);
			p[0] += v[0] * w;
			p[1] += v[1] * w;
			p[2] += v[2] * w;
		}
		c.hips(t, v);
		hips[0] += v[0] * w;
		hips[1] += v[1] * w;
		hips[2] += v[2] * w;
	}

	private static void scale(Map<String, float[]> pose, float[] hips, float k) {
		for (float[] p : pose.values())
			for (int i = 0; i < 3; i++) p[i] *= k;
		for (int i = 0; i < 3; i++) hips[i] *= k;
	}

	private static void turn(Map<String, float[]> pose, String bone, float x, float y) {
		float[] p = pose.computeIfAbsent(bone, k -> new float[3]);
		p[0] += x;
		p[1] -= y;
	}

	private static void emit(PoseStack.Pose p, VertexConsumer vc, float[] a, int light, int overlay) {
		for (int t = 0; t + 24 <= a.length; t += 24)
			for (int c = 0; c < 4; c++) {
				int i = t + Math.min(c, 2) * 8;
				vc.addVertex(p, a[i], a[i + 1], a[i + 2]).setColor(-1).setUv(a[i + 3], a[i + 4]).setOverlay(overlay).setLight(light)
						.setNormal(p, a[i + 5], a[i + 6], a[i + 7]);
			}
	}

	private static float f(String s) {
		return Float.parseFloat(s);
	}

	private static float[] arr(List<Float> l) {
		float[] a = new float[l.size()];
		for (int i = 0; i < a.length; i++) a[i] = l.get(i);
		return a;
	}

	private static Vector3f vec(JsonArray a) {
		return new Vector3f(a.get(0).getAsFloat(), a.get(1).getAsFloat(), a.get(2).getAsFloat());
	}
}
