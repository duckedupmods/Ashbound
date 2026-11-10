package com.snoringwalrus.ashbound.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.Thrall;

import java.io.InputStreamReader;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.WeakHashMap;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import org.joml.Matrix3f;
import org.joml.Matrix4f;
import org.joml.Quaternionf;

/**
 * A thrall from tools/voxthralls.py or tools/voxbound.py, posed here like the mounts are. Most have no legs to walk on: they hang in
 * the air and bob, lean into their movement, their fire streams back, and an arm draws up and comes down on each blow. The Gatebreaker
 * and the Riftling walk. Everything that burns is grey in the texture and takes the colour of the staff that called it.
 */
public class ThrallRender extends EntityRenderer<Thrall> {
	private static final float HOVER = 0.25f, BOB = 0.1f, LEAN = 0.5f, STRIDE = 0.75f, STEP = 0.7f, SCUTTLE = 1.6f;
	private static final java.util.Map<String, Float> SIZE = java.util.Map.of("revenant", 0.68f, "champion", 0.92f, "riftblade", 0.62f, "cantor", 0.56f, "gatebreaker", 0.75f, "riftling", 0.42f, "oathwarden", 0.46f, "colossus", 1.0f);

	/**
	 * A blow, keyed (tools/thrall_moves.py): at each key's point through the swing, how far each bone is turned (x, y, z in
	 * degrees) and the body moved ("root", in the model's own blocks). Between keys it eases as the key says: 'o' fast then
	 * slowing (into a coil, out past the hit), 'i' slow then fast (the strike, quickest as it lands), 's' both.
	 */
	private record Blow(float[] at, char[] how, List<Map<String, float[]>> poses) {
		float[] sample(String bone, float a) {
			a = Mth.clamp(a, 0, 1);
			for (int i = 0; i < at.length - 1; i++) {
				if (a > at[i + 1]) continue;
				float f = (a - at[i]) / Math.max(1e-4f, at[i + 1] - at[i]);
				f = switch (how[i + 1]) {
					case 'o' -> 1 - (1 - f) * (1 - f) * (1 - f);
					case 'i' -> f * f * f;
					default -> f * f * (3 - 2 * f);
				};
				float[] p = poses.get(i).get(bone), q = poses.get(i + 1).get(bone);
				if (p == null && q == null) return null;
				float[] out = new float[3];
				for (int j = 0; j < 3; j++) out[j] = Mth.lerp(f, p == null ? 0 : p[j], q == null ? 0 : q[j]);
				return out;
			}
			return null;
		}

		boolean moves(String bone) {
			for (Map<String, float[]> p : poses) if (p.containsKey(bone)) return true;
			return false;
		}
	}

	private static Map<String, List<Blow>> blows;

	private static List<Blow> blows(String model) {
		if (blows == null) {
			blows = new HashMap<>();
			ResourceLocation at = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "mounts/thrall_moves.json");
			try (Reader r = new InputStreamReader(Minecraft.getInstance().getResourceManager().getResourceOrThrow(at).open(), StandardCharsets.UTF_8)) {
				JsonObject all = JsonParser.parseReader(r).getAsJsonObject();
				for (var kind : all.entrySet()) {
					List<Blow> list = new ArrayList<>();
					for (var b : kind.getValue().getAsJsonObject().entrySet()) {
						JsonArray keys = b.getValue().getAsJsonArray();
						float[] times = new float[keys.size()];
						char[] how = new char[keys.size()];
						List<Map<String, float[]>> poses = new ArrayList<>();
						for (int i = 0; i < keys.size(); i++) {
							JsonArray k = keys.get(i).getAsJsonArray();
							times[i] = k.get(0).getAsFloat();
							how[i] = k.size() > 2 ? k.get(2).getAsString().charAt(0) : 's';
							Map<String, float[]> pose = new HashMap<>();
							for (var bone : k.get(1).getAsJsonObject().entrySet()) {
								JsonArray v = bone.getValue().getAsJsonArray();
								pose.put(bone.getKey(), new float[] {v.get(0).getAsFloat(), v.get(1).getAsFloat(), v.get(2).getAsFloat()});
							}
							poses.add(pose);
						}
						list.add(new Blow(times, how, poses));
					}
					blows.put(kind.getKey(), list);
				}
			} catch (java.io.IOException | RuntimeException ex) {
				Ashbound.LOG.warn("No thrall moves: {}", ex.toString());
			}
		}
		return blows.getOrDefault(model, List.of());
	}

	/** Which of its blows each one is in: the next one each time a swing starts. */
	private static final class Turn {
		int n = -1;
		boolean swinging;
	}

	private static final Map<Thrall, Turn> TURNS = new WeakHashMap<>();

	private static Blow blow(Thrall e, float a) {
		List<Blow> list = blows(e.model);
		if (e.blowIndex() >= 0 && e.blowIndex() < list.size()) return a > 0 ? list.get(e.blowIndex()) : null;   // the server picked it
		Turn turn = TURNS.computeIfAbsent(e, k -> new Turn());
		if (a > 0 && !turn.swinging) turn.n++;
		turn.swinging = a > 0;
		return a > 0 && !list.isEmpty() ? list.get(Math.floorMod(e.getId() + turn.n, list.size())) : null;
	}

	/** The strike's smear: where its arms and weapon were a moment back, drawn again in the staff's light, fading. */
	private static final float SMEAR_FROM = 0.45f, SMEAR_TO = 0.66f, ECHO_GAP = 0.025f;
	private static final int ECHOES = 3;
	/** A wraith going fast leaves itself behind: where it was the last few ticks, and how fast is fast (blocks a tick). */
	private static final int TRAIL = 5;
	private static final double DIVING = 0.25;
	private static final Map<Thrall, ArrayDeque<double[]>> WAS = new WeakHashMap<>();

	private static boolean smears(String bone) {
		return bone.startsWith("arm") || bone.startsWith("fore") || bone.equals("blade") || bone.equals("spear") || bone.equals("shield")
				|| bone.equals("sting") || bone.equals("book");
	}

	/** rgb scaled down: drawn added on, darker is fainter */
	private static int fade(int rgb, float f) {
		f *= HudPrefs.fxAlpha();
		return (int) ((rgb >> 16 & 255) * f) << 16 | (int) ((rgb >> 8 & 255) * f) << 8 | (int) ((rgb & 255) * f);
	}

	public ThrallRender(EntityRendererProvider.Context ctx) {
		super(ctx);
		shadowRadius = 0.7f;
	}

	private static String id(Thrall e) {
		return e.model;
	}

	private static boolean walks(String model) {
		return model.equals("gatebreaker") || model.equals("riftling") || model.equals("colossus");
	}

	@Override
	public ResourceLocation getTextureLocation(Thrall e) {
		return ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/entity/mount_" + id(e) + ".png");
	}

	/** Up, back and down: how far through a blow its arm is. */
	private static float blow(float a) {
		return a < 0.35f ? -Mth.sin(a / 0.35f * Mth.HALF_PI) * 1.5f : -1.5f + 2.4f * Mth.sin((a - 0.35f) / 0.65f * Mth.HALF_PI);
	}

	private static void turn(String name, Quaternionf q, float t, float speed, float swing, float headYaw) {
		if (name.equals("torso")) q.rotateX(speed * LEAN + Mth.sin(t * 0.09f) * 0.04f + swing * 0.12f).rotateY(swing * -0.3f);
		else if (name.equals("head")) q.rotateY(headYaw).rotateX(-speed * LEAN * 0.8f);
		else if (name.equals("arm_r")) q.rotateX(swing);
		else if (name.equals("fore_r")) q.rotateX(swing * 0.5f + Mth.sin(t * 0.07f) * 0.06f);
		else if (name.equals("arm_l")) q.rotateX(swing * 0.7f - speed * 0.4f + Mth.sin(t * 0.08f + 1) * 0.08f);
		else if (name.startsWith("arm2_")) q.rotateX(swing * 0.5f + Mth.sin(t * 0.1f + (name.endsWith("l") ? 0 : 2)) * 0.1f);
		else if (name.equals("wheel")) q.rotateZ(t * 0.03f);
		else if (name.equals("book")) q.rotateY(Mth.sin(t * 0.05f) * 0.2f).rotateZ(Mth.sin(t * 0.08f) * 0.1f);
		else if (name.equals("sting")) q.rotateX(swing * 0.5f + Mth.sin(t * 0.14f) * 0.08f);
		else if (name.equals("shield")) q.rotateY(swing * 0.15f);
	}

	/** Heavy legs, or six quick ones in two sets. */
	private static void legs(String model, String name, Quaternionf q, float walk, float speed) {
		if (model.equals("colossus") && name.startsWith("arm_")) {   // on its knuckles: each fist with the leg across from it
			q.rotateX(Mth.sin(walk * STRIDE) * STEP * 0.8f * speed * (name.endsWith("l") ? 1 : -1));
		} else if (model.equals("gatebreaker") || model.equals("colossus")) {
			float s = Mth.sin(walk * STRIDE) * STEP * speed * (name.endsWith("l") ? 1 : -1);
			if (name.startsWith("leg_")) q.rotateX(s);
			else if (name.startsWith("shin_")) q.rotateX(Math.max(0, s));
		} else if (name.startsWith("leg_")) {
			int n = name.charAt(name.length() - 1) - '0' + (name.charAt(name.length() - 2) == 'l' ? 1 : 0);
			q.rotateY(Mth.sin(walk * SCUTTLE + n * Mth.PI) * 0.45f * speed);
		}
	}

	@Override
	public void render(Thrall e, float yaw, float pt, PoseStack ps, MultiBufferSource buf, int light) {
		MountRender.Model m = MountRender.model(id(e));
		float t = e.tickCount + pt, body = Mth.rotLerp(pt, e.yBodyRotO, e.yBodyRot), speed = Math.min(1, e.walkAnimation.speed(pt) * 1.4f);
		float a = e.getAttackAnim(pt);
		Blow keyed = blow(e, a);
		float swing = blow(a), headYaw = Mth.wrapDegrees(Mth.rotLerp(pt, e.yHeadRotO, e.yHeadRot) - body) * Mth.DEG_TO_RAD;
		float k = SIZE.get(e.model) * e.getScale(), walk = e.walkAnimation.position(pt);
		boolean walks = walks(e.model);
		ps.pushPose();
		if (!walks) ps.translate(0, HOVER + Mth.sin(t * 0.1f) * BOB, 0);
		ps.mulPose(Axis.YP.rotationDegrees(-body));
		ps.scale(k, k, k);
		Matrix4f[] world = pose(m, e.model, keyed, a, t, speed, swing, headYaw, walk);
		int frame = (int) (t / 20 * MountRender.FPS) % m.frames(), tint = e.tint();
		float shift = (float) frame / m.frames();
		VertexConsumer lit = buf.getBuffer(RenderType.entityCutoutNoCull(getTextureLocation(e)));
		boolean cracks = e.model.equals("gatebreaker");
		for (int i = 0; i < world.length; i++) {
			MountRender.Bone b = m.bones().get(i);
			ps.pushPose();
			ps.last().pose().mul(world[i]);
			ps.last().normal().mul(new Matrix3f(world[i]));
			MountRender.quads(lit, ps.last(), b.lit(), 0, light, 0, 0, 0xFFFFFF);
			MountRender.quads(lit, ps.last(), b.glow(), 0, LightTexture.FULL_BRIGHT, 0, 0, tint);
			MountRender.quads(lit, ps.last(), b.flame(), shift, LightTexture.FULL_BRIGHT, t, 0.012f, tint);
			ps.popPose();
		}
		if (cracks) {   // what burns in its hide, over the top in the staff's colour
			VertexConsumer hot = buf.getBuffer(RenderType.eyes(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/entity/mount_" + e.model + "_hot.png")));
			for (int i = 0; i < world.length; i++) {
				ps.pushPose();
				ps.last().pose().mul(world[i]);
				ps.last().normal().mul(new Matrix3f(world[i]));
				MountRender.quads(hot, ps.last(), m.bones().get(i).lit(), 0, LightTexture.FULL_BRIGHT, 0, 0, tint);
				ps.popPose();
			}
		}
		if (keyed != null && a > SMEAR_FROM && a < SMEAR_TO) {
			VertexConsumer glow = buf.getBuffer(RenderType.eyes(getTextureLocation(e)));
			for (int n = 1; n <= ECHOES; n++) {
				Matrix4f[] was = pose(m, e.model, keyed, a - n * ECHO_GAP, t, speed, swing, headYaw, walk);
				for (int i = 0; i < was.length; i++)
					if (smears(m.bones().get(i).name())) bone(ps, was[i], glow, m.bones().get(i).lit(), fade(tint, 0.7f / n));
			}
		}
		ps.popPose();
		if (e.model.equals("revenant")) trail(e, m, world, pt, body, k, walks ? 0 : HOVER + Mth.sin(t * 0.1f) * BOB, ps, buf, tint);
		super.render(e, yaw, pt, ps, buf, light);
	}

	private static Matrix4f[] pose(MountRender.Model m, String model, Blow keyed, float a, float t, float speed, float swing, float headYaw, float walk) {
		float[] root = keyed == null ? null : keyed.sample("root", a);
		Matrix4f base = root == null ? new Matrix4f() : new Matrix4f().translate(root[0], root[1], root[2]);
		Matrix4f[] world = new Matrix4f[m.bones().size()];
		Quaternionf q = new Quaternionf();
		for (int i = 0; i < world.length; i++) {
			MountRender.Bone b = m.bones().get(i);
			q.identity();
			if (keyed != null && keyed.moves(b.name())) {   // the blow has this bone: z, then x, then y, as the tool poses it
				float[] r = keyed.sample(b.name(), a);
				if (r != null) q.rotateY(r[1] * Mth.DEG_TO_RAD).rotateX(r[0] * Mth.DEG_TO_RAD).rotateZ(r[2] * Mth.DEG_TO_RAD);
			} else turn(b.name(), q, t, speed, keyed == null && a > 0 ? swing : 0, headYaw);
			if (walks(model)) legs(model, b.name(), q, walk, speed);
			Matrix4f at = new Matrix4f(b.parent() < 0 ? base : world[b.parent()]);
			world[i] = at.translate(b.px(), b.py(), b.pz()).rotate(q).translate(-b.px(), -b.py(), -b.pz());
		}
		return world;
	}

	private static void bone(PoseStack ps, Matrix4f at, VertexConsumer to, float[] quads, int rgb) {
		ps.pushPose();
		ps.last().pose().mul(at);
		ps.last().normal().mul(new Matrix3f(at));
		MountRender.quads(to, ps.last(), quads, 0, LightTexture.FULL_BRIGHT, 0, 0, rgb);
		ps.popPose();
	}

	/** Where it was each of the last few ticks: going as fast as a dive, a ghost of it at each, fainter the older. */
	private void trail(Thrall e, MountRender.Model m, Matrix4f[] world, float pt, float body, float k, float lift, PoseStack ps, MultiBufferSource buf, int tint) {
		ArrayDeque<double[]> was = WAS.computeIfAbsent(e, x -> new ArrayDeque<>());
		if (was.isEmpty() || was.peekFirst()[3] != e.tickCount) {
			was.addFirst(new double[] {e.getX(), e.getY(), e.getZ(), e.tickCount});
			while (was.size() > TRAIL + 1) was.removeLast();
		}
		double x = Mth.lerp(pt, e.xo, e.getX()), y = Mth.lerp(pt, e.yo, e.getY()), z = Mth.lerp(pt, e.zo, e.getZ());
		VertexConsumer glow = buf.getBuffer(RenderType.eyes(getTextureLocation(e)));
		double[] last = null;
		int n = 0;
		for (double[] w : was) {
			if (last != null && Math.sqrt(Math.pow(w[0] - last[0], 2) + Math.pow(w[2] - last[2], 2)) > DIVING) {
				ps.pushPose();
				ps.translate(w[0] - x, w[1] - y + lift, w[2] - z);
				ps.mulPose(Axis.YP.rotationDegrees(-body));
				ps.scale(k, k, k);
				for (int i = 0; i < world.length; i++) bone(ps, world[i], glow, m.bones().get(i).lit(), fade(tint, 0.5f / (1 + n * 0.6f)));
				ps.popPose();
			}
			last = w;
			n++;
		}
	}
}
