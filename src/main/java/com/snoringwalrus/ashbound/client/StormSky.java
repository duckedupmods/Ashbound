package com.snoringwalrus.ashbound.client;

import org.joml.Matrix4f;
import org.joml.Quaternionf;
import org.joml.Vector3f;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.GateEntity;
import com.snoringwalrus.ashbound.SkyCrack;

import net.minecraft.client.Camera;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.renderer.FogRenderer;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.client.event.ViewportEvent;

/**
 * A gate storm as you see it from under it (SkyCracks): the clouds (tools/blender/storm_clouds.py, baked looking up at the
 * deck of gate_storm.py) laid on three discs over the eye, each turning at its own speed so the spiral moves; the rain
 * and the dark (the client's own rain and thunder, while you're under it, put back when you leave); the fog drawn in
 * and dimmed; and the flash when its lightning strikes, lighting the clouds and the fog.
 */
@EventBusSubscriber(modid = Ashbound.ID, value = Dist.CLIENT)
public final class StormSky {
	private StormSky() {}

	private static final ResourceLocation FUNNEL = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/entity/storm_funnel.png");
	private static final ResourceLocation WHITE = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/entity/storm_white.png");
	private static final ResourceLocation CLOUDS = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/entity/storm_clouds.png");
	/** the discs: radius, height over the eye, turn per tick (radians), how solid */
	private static final float[][] LAYERS = {{175, -SkyCrack.DECK + 6, 0.0007f, 0.9f}, {150, -SkyCrack.DECK + 2, 0.0012f, 0.8f}, {120, -SkyCrack.DECK - 2, 0.002f, 0.65f}};
	private static final int RINGS = 8, SEGS = 40;
	/** under it within IN blocks (flat, from the eye), none of it past OUT */
	private static final float IN = 120, OUT = 230;
	/** how long it takes to roll in (ticks after it opens) */
	private static final int ROLL_IN = 240;

	/** how much of a storm is over you now, eased; the flash of its lightning, and its colour */
	private static float here, flash;
	private static int flashRgb = 0xFF3020;
	/** the weather the server gave, kept while ours is shown */
	private static boolean ours;
	private static float keptRain, keptThunder;
	private static ClientLevel ourLevel;

	/** How much of this one there is: rolling in as it opens, blowing away as it closes. */
	static float strength(SkyCrack g, float partial) {
		long now = g.level().getGameTime();
		if (g.closing()) return Mth.clamp(1 - (now - g.closed() + partial) / GateEntity.GONE, 0, 1);
		return Mth.clamp((now - g.opened() + partial) / ROLL_IN, 0, 1);
	}

	/** Lightning struck dist blocks from you, in the gate's colour. */
	static void strike(double dist, int rgb) {
		float k = (float) Mth.clamp(1 - dist / 260, 0, 1);
		if (k <= flash) return;
		flash = k;
		flashRgb = rgb;
		GateFx.flash(k * 0.09f, rgb);
	}

	public static float flash() {
		return flash;
	}

	@SubscribeEvent
	static void tick(ClientTickEvent.Post e) {
		Minecraft mc = Minecraft.getInstance();
		flash *= 0.62f;
		ClientLevel cl = mc.level;
		if (cl != ourLevel) {
			ours = false;
			ourLevel = cl;
			here = 0;
		}
		if (cl == null || mc.player == null) return;
		float want = 0;
		for (Entity en : cl.entitiesForRendering()) {
			if (!(en instanceof SkyCrack g)) continue;
			double dx = en.getX() - mc.player.getX(), dz = en.getZ() - mc.player.getZ();
			float near = (float) Mth.clamp((OUT - Math.sqrt(dx * dx + dz * dz)) / (OUT - IN), 0, 1);
			want = Math.max(want, near * strength(g, 0));
		}
		here += (want - here) * 0.04f;
		if (here > 0.01f) {
			if (!ours) {
				keptRain = cl.getRainLevel(1);
				keptThunder = cl.getThunderLevel(1);
				ours = true;
			}
			cl.setRainLevel(Math.max(keptRain, here));
			cl.setThunderLevel(Math.max(keptThunder, here));
		} else if (ours) {
			cl.setRainLevel(keptRain);
			cl.setThunderLevel(keptThunder);
			ours = false;
			here = 0;
		}
	}

	/** The air under it: dark, grey with the gate's red in it, lit up when lightning strikes. */
	@SubscribeEvent
	static void fogColour(ViewportEvent.ComputeFogColor e) {
		if (here < 0.01f && flash < 0.01f) return;
		float k = here * 0.8f;
		float r = Mth.lerp(k, e.getRed(), 0.11f), g = Mth.lerp(k, e.getGreen(), 0.085f), b = Mth.lerp(k, e.getBlue(), 0.09f);
		float f = flash * 0.55f * here;
		e.setRed(Math.min(1, r + f * ((flashRgb >> 16 & 255) / 255f)));
		e.setGreen(Math.min(1, g + f * ((flashRgb >> 8 & 255) / 255f)));
		e.setBlue(Math.min(1, b + f * ((flashRgb & 255) / 255f)));
	}

	/** The fog drawn in a little, so the far land goes grey under it. */
	@SubscribeEvent
	static void fog(ViewportEvent.RenderFog e) {
		if (here < 0.01f || e.getMode() != FogRenderer.FogMode.FOG_TERRAIN) return;
		float far = e.getFarPlaneDistance(), to = Math.min(far, 180);
		e.setFarPlaneDistance(Mth.lerp(here, far, to));
		e.setNearPlaneDistance(Mth.lerp(here, e.getNearPlaneDistance(), to * 0.15f));
		e.setCanceled(true);
	}

	/** the funnel: its foot (under the eye, at the cloud base) and its top (round the tear), and how wide at each */
	private static final float F_BOT = -SkyCrack.DECK - 2, F_TOP = 0, R_BOT = 44, R_TOP = 24;
	/** its walls, back to front: radius shrink, how far the streaks wind round it going up, turn per tick, how solid, how red */
	private static final float[][] WALLS = {{0, 2.5f, 0.004f, 1f, 0.8f}, {4, 4.5f, 0.007f, 0.8f, 1f}, {8, 7f, 0.011f, 0.55f, 1f}};
	private static final int F_RINGS = 14, F_SEGS = 48;

	/** The funnel's radius at height y (eye frame): a flared horn, wide where it meets the deck, tight round the tear. */
	static float funnelRadius(float y, float shrink) {
		float h = Mth.clamp((y - F_BOT) / (F_TOP - F_BOT), 0, 1);
		return R_TOP - shrink * 0.5f + (R_BOT - R_TOP - shrink) * (float) Math.pow(1 - h, 1.8) + 1.5f * Mth.sin(h * Mth.PI);
	}

	/**
	 * The storm over its eye (drawn from GateRenderer, in the gate's frame: origin at its feet; tools/blender/gate_storm_eye.py
	 * is the look): the deck of cloud below the eye, a funnel of cloud climbing from it to the tear (a solid dark back
	 * wall, then streaked walls turning faster the further in, lit red toward the tear), a dark lid round the tear's top,
	 * red wisps turning in its mouth, and lightning crawling down the funnel now and then.
	 */
	static void clouds(SkyCrack g, float partial, PoseStack pose, MultiBufferSource buffers) {
		float s = strength(g, partial);
		if (s <= 0.01f) return;
		float t = g.level().getGameTime() + partial;
		float lit = 0.5f + 0.75f * flash;
		int c = GateEntity.COLOUR[Mth.clamp(g.rank(), 0, GateEntity.COLOUR.length - 1)];
		float cr = (c >> 16 & 255) / 255f, cg = (c >> 8 & 255) / 255f, cb = (c & 255) / 255f;
		pose.pushPose();
		pose.translate(0, GateEntity.MID, 0);
		PoseStack.Pose at = pose.last();

		// the deck: rings round the funnel's foot out to its rim, fading in where they meet the funnel
		VertexConsumer v = buffers.getBuffer(RenderType.entityTranslucent(CLOUDS));
		for (float[] lay : LAYERS) {
			float rad = lay[0] * (0.35f + 0.65f * s), y = lay[1], turn = t * lay[2], a = lay[3] * Math.min(1, s * 1.5f);
			float in = funnelRadius(y, 0) - 3;
			for (int j = 0; j < RINGS; j++) {
				float r0 = in + (rad - in) * j / RINGS, r1 = in + (rad - in) * (j + 1) / RINGS;
				for (int i = 0; i < SEGS; i++) {
					float a0 = i * Mth.TWO_PI / SEGS, a1 = (i + 1) * Mth.TWO_PI / SEGS;
					float[][] q = {{r0, a0}, {r1, a0}, {r1, a1}, {r0, a1}};
					for (int side = 0; side < 2; side++)
						for (int k = 0; k < 4; k++) {
							float[] p = q[side == 0 ? k : 3 - k];
							float rr = p[0] / rad, ang = p[1];
							float u = 0.5f + 0.5f * rr * Mth.cos(ang + turn), w = 0.5f + 0.5f * rr * Mth.sin(ang + turn);
							float yy = y - rr * rr * 6, fade = p[0] <= in + 0.01f ? 0 : 1;
							v.addVertex(at, p[0] * Mth.cos(ang), yy, p[0] * Mth.sin(ang)).setColor(lit, lit, lit, a * fade).setUv(u, w)
									.setOverlay(OverlayTexture.NO_OVERLAY).setLight(LightTexture.FULL_BRIGHT).setNormal(at, 0, 1, 0);
						}
				}
			}
		}

		// the funnel's back wall and the lid over it: solid, so no sky shows through the walls in front
		VertexConsumer solid = buffers.getBuffer(RenderType.entitySolid(WHITE));
		float grow = Math.min(1, s * 1.3f);
		for (int j = 0; j < F_RINGS; j++) {
			float y0 = Mth.lerp(j / (float) F_RINGS, F_BOT + 6, F_TOP + 0.3f), y1 = Mth.lerp((j + 1f) / F_RINGS, F_BOT + 6, F_TOP + 0.3f);
			float r0 = funnelRadius(y0, -3) * grow, r1 = funnelRadius(y1, -3) * grow;
			float h0 = (y0 - F_BOT) / (F_TOP - F_BOT), h1 = (y1 - F_BOT) / (F_TOP - F_BOT);
			for (int i = 0; i < F_SEGS; i++) {
				float a0 = i * Mth.TWO_PI / F_SEGS, a1 = (i + 1) * Mth.TWO_PI / F_SEGS;
				float[][] q = {{r0, y0, a0, h0}, {r1, y1, a0, h1}, {r1, y1, a1, h1}, {r0, y0, a1, h0}};
				for (int side = 0; side < 2; side++)
					for (int k = 0; k < 4; k++) {
						float[] p = q[side == 0 ? k : 3 - k];
						float red = (float) Math.pow(p[3], 4) * 0.7f;
						solid.addVertex(at, p[0] * Mth.cos(p[2]), p[1], p[0] * Mth.sin(p[2]))
								.setColor(Mth.lerp(red, 0.07f, cr) * lit, Mth.lerp(red, 0.065f, cg * 0.5f) * lit, Mth.lerp(red, 0.075f, cb * 0.5f) * lit, 1f)
								.setUv(0.5f, 0.5f).setOverlay(OverlayTexture.NO_OVERLAY).setLight(LightTexture.FULL_BRIGHT).setNormal(at, 0, 1, 0);
					}
			}
		}
		float lidR = (R_TOP + 4) * grow;
		for (int i = 0; i < F_SEGS; i++) {
			float a0 = i * Mth.TWO_PI / F_SEGS, a1 = (i + 1) * Mth.TWO_PI / F_SEGS;
			float[][] q = {{0, a0}, {lidR, a0}, {lidR, a1}, {0, a1}};
			for (int side = 0; side < 2; side++)
				for (int k = 0; k < 4; k++) {
					float[] p = q[side == 0 ? k : 3 - k];
					solid.addVertex(at, p[0] * Mth.cos(p[1]), F_TOP + 0.6f, p[0] * Mth.sin(p[1])).setColor(0.05f, 0.015f, 0.015f, 1f).setUv(0.5f, 0.5f)
							.setOverlay(OverlayTexture.NO_OVERLAY).setLight(LightTexture.FULL_BRIGHT).setNormal(at, 0, 1, 0);
				}
		}

		// the streaked walls, turning faster the further in, the streaks climbing toward the tear
		VertexConsumer f = buffers.getBuffer(RenderType.entityTranslucent(FUNNEL));
		for (float[] wall : WALLS) {
			float y0w = F_BOT + wall[0];
			for (int j = 0; j < F_RINGS; j++) {
				float y0 = Mth.lerp(j / (float) F_RINGS, y0w, F_TOP), y1 = Mth.lerp((j + 1f) / F_RINGS, y0w, F_TOP);
				for (int i = 0; i < F_SEGS; i++) {
					float a0 = i * Mth.TWO_PI / F_SEGS, a1 = (i + 1) * Mth.TWO_PI / F_SEGS;
					float[][] q = {{y0, a0, i}, {y1, a0, i}, {y1, a1, i + 1}, {y0, a1, i + 1}};
					for (int side = 0; side < 2; side++)
						for (int k = 0; k < 4; k++) {
							float[] p = q[side == 0 ? k : 3 - k];
							float h = (p[0] - F_BOT) / (F_TOP - F_BOT), r = funnelRadius(p[0], wall[0]) * grow;
							float u = p[2] / F_SEGS * 3 + h * wall[1] + t * wall[2], w = h * 1.4f - t * wall[2] * 0.6f;
							// frayed out at its foot, thinning into the tear at its top, red toward it
							float a = wall[3] * Mth.clamp(h / 0.35f, 0, 1) * Mth.clamp((1.02f - h) / 0.15f, 0, 1) * Math.min(1, s * 1.5f);
							float red = (float) Math.pow(h, 3) * wall[4];
							float gr = 0.42f * lit;
							f.addVertex(at, r * Mth.cos(p[1]), p[0], r * Mth.sin(p[1]))
									.setColor(Math.min(1, Mth.lerp(red, gr, cr * 1.1f + 0.15f)), Mth.lerp(red, gr, cg * 0.6f + 0.05f), Mth.lerp(red, gr, cb * 0.6f + 0.05f), a)
									.setUv(u, w).setOverlay(OverlayTexture.NO_OVERLAY).setLight(LightTexture.FULL_BRIGHT).setNormal(at, 0, 1, 0);
						}
				}
			}
		}
		// red wisps turning in the tear's mouth, just under it: they slide across the dungeon as you move
		for (int n = 0; n < 2; n++) {
			float y = F_TOP - 0.8f - n * 1.6f, rad = (R_TOP - 4 - n * 3) * grow, turn = t * (n == 0 ? 0.02f : -0.013f);
			for (int i = 0; i < F_SEGS; i++) {
				float a0 = i * Mth.TWO_PI / F_SEGS, a1 = (i + 1) * Mth.TWO_PI / F_SEGS;
				float[][] q = {{0, a0}, {rad, a0}, {rad, a1}, {0, a1}};
				for (int side = 0; side < 2; side++)
					for (int k = 0; k < 4; k++) {
						float[] p = q[side == 0 ? k : 3 - k];
						float rr = p[0] / Math.max(1, rad);
						f.addVertex(at, p[0] * Mth.cos(p[1]), y, p[0] * Mth.sin(p[1])).setColor(Math.min(1, cr * 1.2f + 0.1f), cg * 0.5f, cb * 0.5f, 0.4f * (1 - rr) * s)
								.setUv(rr * 0.8f + n * 0.37f, (p[1] + turn) / Mth.TWO_PI * 2).setOverlay(OverlayTexture.NO_OVERLAY)
								.setLight(LightTexture.FULL_BRIGHT).setNormal(at, 0, 1, 0);
					}
			}
		}

		// lightning crawling down the funnel wall, now and then
		int beat = (int) (t / 17), in = (int) t - beat * 17;
		if (s > 0.6f && in < 5 && StormStrikeRenderer.hash(g.getUUID().getLeastSignificantBits(), beat) < 0.6f) {
			Camera cam = Minecraft.getInstance().gameRenderer.getMainCamera();
			Vector3f eye = new Vector3f((float) (cam.getPosition().x - g.getX()), (float) (cam.getPosition().y - g.getY() - GateEntity.MID),
					(float) (cam.getPosition().z - g.getZ()));
			GateRenderer.Glow gl = new GateRenderer.Glow(buffers.getBuffer(GateRenderer.Types.GLOW), new Matrix4f(at.pose()), eye, cam.rotation(), new Quaternionf());
			long k = g.getUUID().getMostSignificantBits() * 31 + beat;
			float ang = StormStrikeRenderer.hash(k, 1) * Mth.TWO_PI, on = in == 2 ? 0.3f : 0.9f;
			float hot = 0.75f;
			Vector3f p = null;
			for (int j = 0; j <= 12; j++) {
				float y = Mth.lerp(j / 12f, F_TOP - 0.5f, F_BOT + 8);
				ang += (StormStrikeRenderer.hash(k, 10 + j) - 0.3f) * 0.25f;
				float r = funnelRadius(y, 8) * grow - 0.6f;
				Vector3f q = new Vector3f(r * Mth.cos(ang), y + (StormStrikeRenderer.hash(k, 30 + j) - 0.5f) * 1.2f, r * Mth.sin(ang));
				if (p != null) {
					gl.line(p, q, 1.8f, cr, cg, cb, 0.5f * on);
					gl.line(p, q, 0.4f, Math.min(1, cr * 0.3f + hot), Math.min(1, cg * 0.3f + hot), Math.min(1, cb * 0.3f + hot), on);
				}
				p = q;
			}
		}
		pose.popPose();
	}
}
