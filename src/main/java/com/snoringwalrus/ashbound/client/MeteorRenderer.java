package com.snoringwalrus.ashbound.client;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

import org.joml.Matrix4f;
import org.joml.Quaternionf;
import org.joml.Vector3f;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.GateEntity;
import com.snoringwalrus.ashbound.MeteorShard;

import net.minecraft.client.Camera;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.culling.Frustum;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;

/**
 * A gate-shard (MeteorShard; tools/blender/meteor_fall.py is the look): a cluster of dark hex crystals off one broken
 * root, a big one leaning and six smaller sprayed round it, veins of its gate's colour glowing in them (shard_glow,
 * drawn added). Three of the small ones are its veins: each goes when its vein breaks. Falling, it's small in the
 * middle of a fireball (glows in layers, white at the heart) with a burning streak behind it; the smoke and sparks
 * are particles (MeteorFx).
 */
public class MeteorRenderer extends EntityRenderer<MeteorShard> {
	private static final ResourceLocation TEX = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/entity/meteor/shard.png"),
			GLOW = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/entity/meteor/shard_glow.png");
	private static final Map<Integer, List<Crystal>> SHAPES = new HashMap<>();

	/** One crystal: its quads (4 corners of x y z u v nx ny nz each), and which vein it is (-1 none). */
	record Crystal(float[] quads, int vein) {}

	public MeteorRenderer(EntityRendererProvider.Context ctx) {
		super(ctx);
		shadowRadius = 0;
	}

	@Override
	public ResourceLocation getTextureLocation(MeteorShard s) {
		return TEX;
	}

	static List<Crystal> shape(int seed) {
		return SHAPES.computeIfAbsent(seed, k -> {
			Random r = new Random(k);
			List<Crystal> out = new ArrayList<>();
			// the big one leans 18 to 30 degrees, the rest spray round it from the same root
			Vector3f main = new Vector3f(0, 1, 0).rotateX((18 + r.nextFloat() * 12) * Mth.DEG_TO_RAD).rotateY(r.nextFloat() * Mth.TWO_PI);
			out.add(new Crystal(crystal(r, new Vector3f(0, -0.8f, 0), main, 6.6f, 1.15f), -1));
			float[] lens = new float[6];
			for (int i = 0; i < 6; i++) lens[i] = 1.8f + r.nextFloat() * 2.2f;
			for (int i = 0; i < 6; i++) {
				Vector3f ax = new Vector3f(main).rotateX((r.nextFloat() - 0.5f) * 1.7f).rotateZ((r.nextFloat() - 0.5f) * 1.7f);
				if (ax.y < 0.25f) ax.y = 0.25f;
				ax.normalize();
				Vector3f root = new Vector3f((r.nextFloat() - 0.5f) * 1.6f, -0.4f + r.nextFloat() * 0.5f, (r.nextFloat() - 0.5f) * 1.6f);
				// the three longest of the small ones are its veins
				int rankOf = 0;
				for (int j = 0; j < 6; j++) if (lens[j] > lens[i]) rankOf++;
				out.add(new Crystal(crystal(r, root, ax, lens[i], 0.35f + lens[i] * 0.1f), rankOf < 3 ? rankOf : -1));
			}
			return out;
		});
	}

	/** A hex prism with a pointed tip, along `axis` from `root`; uv: u round it, v up it. */
	private static float[] crystal(Random r, Vector3f root, Vector3f axis, float len, float rad) {
		int sides = 6;
		Quaternionf q = new Quaternionf().rotationTo(0, 1, 0, axis.x, axis.y, axis.z);
		float[][] zs = {{0f, rad * 1.05f}, {0.72f, rad * 0.92f}, {0.86f, rad * 0.55f}};
		Vector3f[][] ring = new Vector3f[3][sides];
		float spin = r.nextFloat() * Mth.TWO_PI;
		for (int j = 0; j < 3; j++)
			for (int i = 0; i < sides; i++) {
				float a = spin + i * Mth.TWO_PI / sides + (r.nextFloat() - 0.5f) * 0.24f;
				float rr = zs[j][1] * (0.88f + r.nextFloat() * 0.22f);
				ring[j][i] = new Vector3f(Mth.cos(a) * rr, zs[j][0] * len, Mth.sin(a) * rr).rotate(q).add(root);
			}
		Vector3f tip = new Vector3f((r.nextFloat() - 0.5f) * 0.3f * rad, len, (r.nextFloat() - 0.5f) * 0.3f * rad).rotate(q).add(root);
		List<Float> f = new ArrayList<>();
		for (int j = 0; j < 2; j++)
			for (int i = 0; i < sides; i++) {
				int n = (i + 1) % sides;
				quad(f, ring[j][i], ring[j][n], ring[j + 1][n], ring[j + 1][i], i / (float) sides, (i + 1) / (float) sides, zs[j][0], zs[j + 1][0]);
			}
		for (int i = 0; i < sides; i++) {
			int n = (i + 1) % sides;
			quad(f, ring[2][i], ring[2][n], tip, tip, i / (float) sides, (i + 1) / (float) sides, 0.86f, 1f);
		}
		float[] a = new float[f.size()];
		for (int i = 0; i < a.length; i++) a[i] = f.get(i);
		return a;
	}

	private static void quad(List<Float> f, Vector3f a, Vector3f b, Vector3f c, Vector3f d, float u0, float u1, float v0, float v1) {
		Vector3f n = new Vector3f(b).sub(a).cross(new Vector3f(d).sub(a));
		if (n.lengthSquared() < 1e-8f) n = new Vector3f(c).sub(a).cross(new Vector3f(d).sub(b));
		n.normalize();
		// the outside is the side facing away from the crystal's own middle line: wound so
		Vector3f[] p = {a, b, c, d};
		float[][] uv = {{u0, 1 - v0}, {u1, 1 - v0}, {u1, 1 - v1}, {u0, 1 - v1}};
		for (int i = 0; i < 4; i++) {
			f.add(p[i].x);
			f.add(p[i].y);
			f.add(p[i].z);
			f.add(uv[i][0]);
			f.add(uv[i][1]);
			f.add(n.x);
			f.add(n.y);
			f.add(n.z);
		}
	}

	private static void emit(PoseStack.Pose p, VertexConsumer vc, float[] a, int light, int overlay, int argb) {
		for (int i = 0; i + 8 <= a.length; i += 8)
			vc.addVertex(p, a[i], a[i + 1], a[i + 2]).setColor(argb).setUv(a[i + 3], a[i + 4]).setOverlay(overlay).setLight(light)
					.setNormal(p, a[i + 5], a[i + 6], a[i + 7]);
	}

	private static int argb(float a, float r, float g, float b) {
		return ((int) (Mth.clamp(a, 0, 1) * 255) << 24) | ((int) (Mth.clamp(r, 0, 1) * 255) << 16) | ((int) (Mth.clamp(g, 0, 1) * 255) << 8)
				| (int) (Mth.clamp(b, 0, 1) * 255);
	}

	@Override
	public void render(MeteorShard e, float yaw, float pt, PoseStack pose, MultiBufferSource buffers, int light) {
		int phase = e.phase();
		float t = e.tickCount + pt;
		int col = GateEntity.COLOUR[Mth.clamp(e.rank(), 0, GateEntity.COLOUR.length - 1)];
		float r = (col >> 16 & 255) / 255f, g = (col >> 8 & 255) / 255f, b = (col & 255) / 255f;
		boolean hit = System.currentTimeMillis() - e.struck < 220;
		Camera cam = Minecraft.getInstance().gameRenderer.getMainCamera();
		pose.pushPose();
		float scale = 1f;
		if (phase == MeteorShard.FALLING) {
			if (e.fallen(pt) >= 1) {
				pose.popPose();
				return;
			}
			Vec3 h = e.head(pt);
			pose.translate(h.x, h.y, h.z);
			fireball(e, pose, buffers, cam, h, t);
			// the crystal inside it, tip first along its way
			Vec3 dir = e.heading();
			pose.mulPose(new Quaternionf().rotationTo(0, 1, 0, (float) dir.x, (float) dir.y, (float) dir.z));
			scale = 0.45f;
		} else if (phase == MeteorShard.SHATTER) {
			scale = 1f + 0.05f * Mth.sin(t * 3f);      // shaking itself apart
		}
		pose.scale(scale, scale, scale);
		int veins = e.veins();
		boolean dark = phase == MeteorShard.DARK;
		float pulse = 0.75f + 0.25f * Mth.sin(t * (phase == MeteorShard.AWAKE ? 0.25f : 0.08f));
		float bright = dark ? 0.08f : phase == MeteorShard.SHATTER ? 1.4f : (0.55f + 0.15f * veins) * pulse;
		if (hit) bright = 1.5f;
		VertexConsumer body = buffers.getBuffer(RenderType.entityCutoutNoCull(TEX));
		VertexConsumer glow = buffers.getBuffer(RenderType.eyes(GLOW));
		int overlay = OverlayTexture.NO_OVERLAY;
		int tint = argb(1, 0.55f + r * 0.25f, 0.55f + g * 0.25f, 0.6f + b * 0.25f);
		int lit = phase == MeteorShard.FALLING ? LightTexture.FULL_BRIGHT : light;
		for (Crystal c : shape(e.seed())) {
			// a vein that's broken is gone (vein 0 goes first)
			if (c.vein() >= 0 && c.vein() < 3 - veins && phase != MeteorShard.FALLING) continue;
			emit(pose.last(), body, c.quads(), lit, overlay, tint);
			float k = c.vein() >= 0 ? bright * 1.25f : bright;
			emit(pose.last(), glow, c.quads(), LightTexture.FULL_BRIGHT, overlay, argb(1, r * k, g * k, b * k));
		}
		pose.popPose();
		// landed: a glow round its foot in the gate's colour, still hot
		if (phase == MeteorShard.LANDED || phase == MeteorShard.AWAKE || phase == MeteorShard.SHATTER) {
			Vector3f eye = new Vector3f((float) (cam.getPosition().x - e.getX()), (float) (cam.getPosition().y - e.getY()), (float) (cam.getPosition().z - e.getZ()));
			GateRenderer.Glow gl = new GateRenderer.Glow(buffers.getBuffer(GateRenderer.Types.GLOW), new Matrix4f(pose.last().pose()), eye, cam.rotation(), new Quaternionf());
			gl.spot(0, 2.5f, 0, 5.5f * pulse, r, g, b, 0.22f * Math.min(1, bright), 0);
			gl.spot(0, 0.6f, 0, 3.2f, 1f, 0.45f, 0.12f, 0.35f, 0);
		}
	}

	/** The fireball: glows in layers, white at the heart, flickering; a burning streak back along where it came from. */
	private static void fireball(MeteorShard e, PoseStack pose, MultiBufferSource buffers, Camera cam, Vec3 h, float t) {
		Vector3f eye = new Vector3f((float) (cam.getPosition().x - e.getX() - h.x), (float) (cam.getPosition().y - e.getY() - h.y),
				(float) (cam.getPosition().z - e.getZ() - h.z));
		GateRenderer.Glow gl = new GateRenderer.Glow(buffers.getBuffer(GateRenderer.Types.GLOW), new Matrix4f(pose.last().pose()), eye, cam.rotation(), new Quaternionf());
		float fl = 0.9f + 0.1f * Mth.sin(t * 2.1f) + 0.05f * Mth.sin(t * 5.3f);
		gl.spot(0, 0, 0, 16f * fl, 1f, 0.35f, 0.08f, 0.35f, 0);
		gl.spot(0, 0, 0, 8.5f * fl, 1f, 0.55f, 0.2f, 0.7f, 0);
		gl.spot(0, 0, 0, 4.2f * fl, 1f, 0.85f, 0.6f, 0.95f, 0);
		gl.spot(0, 0, 0, 2.0f, 1f, 1f, 0.95f, 1f, 0);
		Vec3 back = e.heading().scale(-1);
		// the streak: hot and thin at the head, widening and going red behind
		float[][] seg = {{0, 6, 3.2f, 1f, 0.9f, 0.7f, 0.9f}, {6, 18, 4.5f, 1f, 0.6f, 0.25f, 0.7f}, {18, 40, 6f, 1f, 0.38f, 0.1f, 0.45f},
				{40, 75, 7f, 0.8f, 0.2f, 0.05f, 0.22f}};
		for (float[] s : seg) {
			Vector3f p = new Vector3f((float) back.x * s[0], (float) back.y * s[0], (float) back.z * s[0]);
			Vector3f q = new Vector3f((float) back.x * s[1], (float) back.y * s[1], (float) back.z * s[1]);
			gl.line(p, q, s[2], s[3], s[4], s[5], s[6]);
		}
	}

	@Override
	public boolean shouldRender(MeteorShard e, Frustum f, double x, double y, double z) {
		return true;
	}
}
