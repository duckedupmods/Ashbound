package com.snoringwalrus.ashbound.client;

import org.joml.Matrix4f;
import org.joml.Quaternionf;
import org.joml.Vector3f;

import com.mojang.blaze3d.vertex.PoseStack;
import com.snoringwalrus.ashbound.GateEntity;
import com.snoringwalrus.ashbound.StormStrike;

import net.minecraft.client.Camera;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;

/**
 * A gate storm's lightning (StormStrike), in its gate's colour with a white-hot heart: first a ring glowing on the ground
 * where it'll come down, brighter and tighter as it charges; then the bolt out of the cloud, flickering for a few
 * ticks, branching; then the ground where it hit glowing and dying away. Nothing but light: no particles, no fire.
 */
public class StormStrikeRenderer extends EntityRenderer<StormStrike> {
	private static final ResourceLocation NONE = ResourceLocation.withDefaultNamespace("textures/misc/white.png");
	private static final int BOLT = 9;

	public StormStrikeRenderer(EntityRendererProvider.Context ctx) {
		super(ctx);
		shadowRadius = 0;
	}

	@Override
	public ResourceLocation getTextureLocation(StormStrike s) {
		return NONE;
	}

	static float hash(long seed, int i) {
		long h = seed * 6364136223846793005L + i * 1442695040888963407L;
		h ^= h >>> 33;
		h *= 0xff51afd7ed558ccdL;
		h ^= h >>> 33;
		return (h & 0xFFFFFF) / (float) 0x1000000;
	}

	@Override
	public void render(StormStrike e, float yaw, float partial, PoseStack pose, MultiBufferSource buffers, int light) {
		float t = e.tickCount - 1 + partial;
		int charge = e.charge();
		int c = GateEntity.COLOUR[Mth.clamp(e.rank(), 0, GateEntity.COLOUR.length - 1)];
		float r = (c >> 16 & 255) / 255f, g = (c >> 8 & 255) / 255f, b = (c & 255) / 255f;
		Camera cam = Minecraft.getInstance().gameRenderer.getMainCamera();
		Vector3f eye = new Vector3f((float) (cam.getPosition().x - e.getX()), (float) (cam.getPosition().y - e.getY()), (float) (cam.getPosition().z - e.getZ()));
		GateRenderer.Glow gl = new GateRenderer.Glow(buffers.getBuffer(GateRenderer.Types.GLOW), new Matrix4f(pose.last().pose()), eye, cam.rotation(),
				new Quaternionf());
		if (t >= charge && !e.flashed) {
			e.flashed = true;
			StormSky.strike(eye.length(), c);
		}

		if (t < charge) {
			// charging: a ring on the ground, tightening and brightening, flickering toward the end
			float k = t / charge, flick = k > 0.6f ? 0.7f + 0.3f * hash(e.seed(), (int) t) : 1;
			float rad = StormStrike.REACH * (1.6f - 0.5f * k);
			ground(gl, rad, r, g, b, (0.25f + 0.6f * k) * flick);
			ground(gl, rad * 0.4f, hot(r), hot(g), hot(b), 0.5f * k * flick);
			return;
		}
		float after = t - charge;
		if (after < BOLT) {
			// the bolt: on, off, on again, fading
			int step = (int) after;
			float on = step == 3 || step == 4 ? 0.25f : 1f - Math.max(0, after - 5) / (BOLT - 5);
			bolt(gl, e.seed() + (step >= 5 ? 1 : 0), e.top(), r, g, b, on);
		}
		// the scorch where it hit, glowing and dying
		float fade = 1 - Mth.clamp(after / StormStrike.AFTER, 0, 1);
		if (!e.harmless() || after < 12) ground(gl, StormStrike.REACH * 1.2f, r, g, b, fade * fade * (e.harmless() ? 0.5f : 0.8f));
	}

	private static float hot(float c) {
		return Math.min(1, c * 0.3f + 0.75f);
	}

	private static void ground(GateRenderer.Glow gl, float rad, float r, float g, float b, float a) {
		gl.quad(new Vector3f(0, 0.06f, 0), new Vector3f(rad, 0, 0), new Vector3f(0, 0, rad), r, g, b, a, 0);
	}

	/** Out of the cloud, top blocks up, down to the ground here: a jagged line, a white core in a coloured glow, forks off it. */
	static void bolt(GateRenderer.Glow gl, long seed, float top, float r, float g, float b, float on) {
		int n = 22;
		float x = (hash(seed, 1) - 0.5f) * 16, z = (hash(seed, 2) - 0.5f) * 16;
		Vector3f p = new Vector3f(x, top, z);
		for (int i = 1; i <= n; i++) {
			float k = i / (float) n;
			float jx = i == n ? 0 : (hash(seed, 10 + i) - 0.5f) * 3.2f, jz = i == n ? 0 : (hash(seed, 40 + i) - 0.5f) * 3.2f;
			Vector3f q = new Vector3f(Mth.lerp(k, x, 0) + jx, top * (1 - k), Mth.lerp(k, z, 0) + jz);
			line(gl, p, q, 1f, r, g, b, on);
			if (i < n - 2 && hash(seed, 70 + i) < 0.18f) {
				// a fork, wandering off and dying
				Vector3f f = new Vector3f(q);
				float ang = hash(seed, 90 + i) * Mth.TWO_PI;
				for (int j = 0; j < 5; j++) {
					Vector3f fq = new Vector3f(f).add(Mth.cos(ang) * 1.6f, -1.4f - hash(seed, 120 + i * 7 + j) * 1.4f, Mth.sin(ang) * 1.6f);
					ang += (hash(seed, 150 + i * 7 + j) - 0.5f) * 1.4f;
					line(gl, f, fq, 0.55f * (1 - j / 5f), r, g, b, on);
					f = fq;
				}
			}
			p = q;
		}
	}

	private static void line(GateRenderer.Glow gl, Vector3f p, Vector3f q, float w, float r, float g, float b, float on) {
		gl.line(p, q, 2.4f * w, r, g, b, 0.55f * on);
		gl.line(p, q, 0.5f * w, hot(r), hot(g), hot(b), on);
	}

	@Override
	public boolean shouldRender(StormStrike e, net.minecraft.client.renderer.culling.Frustum f, double x, double y, double z) {
		return true;
	}
}
