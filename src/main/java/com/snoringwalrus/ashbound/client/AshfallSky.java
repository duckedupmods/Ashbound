package com.snoringwalrus.ashbound.client;

import java.util.ArrayList;
import java.util.List;

import org.joml.Matrix4f;
import org.joml.Quaternionf;
import org.joml.Vector3f;

import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.BufferBuilder;
import com.mojang.blaze3d.vertex.BufferUploader;
import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.mojang.blaze3d.vertex.Tesselator;
import com.mojang.blaze3d.vertex.VertexFormat;
import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.Ashfall;

import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.ParticleRenderType;
import net.minecraft.client.particle.SpriteSet;
import net.minecraft.client.particle.TextureSheetParticle;
import net.minecraft.client.renderer.FogRenderer;
import net.minecraft.client.renderer.GameRenderer;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.LightLayer;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.client.event.RegisterParticleProvidersEvent;
import net.neoforged.neoforge.client.event.RenderLevelStageEvent;
import net.neoforged.neoforge.client.event.ViewportEvent;

/**
 * An ashfall night as you see it (Ashfall; tools/blender/ashfall_night.py is the look): a red dome over the sky, mottled
 * by the ash cloud, the moon a dim red coin through it, the fire-mountain that woke far off on the horizon; the fog
 * drawn in, dark red-brown; grey flakes drifting down with a few embers still alight, settling where they land. It rolls in
 * over a minute, and out again at dawn.
 */
@EventBusSubscriber(modid = Ashbound.ID, value = Dist.CLIENT)
public final class AshfallSky {
	private AshfallSky() {}

	private static ResourceLocation tex(String name) {
		return ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/environment/" + name + ".png");
	}

	private static final ResourceLocation WHITE = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/entity/storm_white.png"),
			CLOUDS = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/entity/storm_clouds.png"),
			MOON = tex("ashfall_moon"), MOUNTAIN = tex("ashfall_mountain");
	/** the fire-mountain's bearing (from you, flat), its size on the sky */
	private static final Vector3f MOUNT_DIR = new Vector3f(-0.45f, 0, -1).normalize();
	private static final float MOUNT_W = 64, MOUNT_H = 32, SKY_R = 90;

	/** how much of it there is here now, eased */
	private static float here;
	private static ClientLevel ourLevel;
	private static int nextRumble = 200;

	public static float here() {
		return here;
	}

	// ---------------------------------------------------------------- rolling in and out, the flakes, the far rumble

	@SubscribeEvent
	static void tick(ClientTickEvent.Post e) {
		Minecraft mc = Minecraft.getInstance();
		ClientLevel cl = mc.level;
		if (cl != ourLevel) {
			ourLevel = cl;
			here = 0;
		}
		if (cl == null || mc.player == null || mc.isPaused()) return;
		boolean on = Ashfall.client && cl.dimension() == net.minecraft.world.level.Level.OVERWORLD;
		here = Mth.clamp(here + (on ? 1 / 1200f : -1 / 400f), 0, 1);
		if (here <= 0) return;
		RandomSource r = cl.getRandom();
		Vec3 c = mc.gameRenderer.getMainCamera().getPosition();
		int flakes = Math.round(here * 14);
		for (int i = 0; i < flakes; i++) {
			double x = c.x + (r.nextDouble() - 0.5) * 48, y = c.y - 4 + r.nextDouble() * 24, z = c.z + (r.nextDouble() - 0.5) * 48;
			BlockPos b = BlockPos.containing(x, y, z);
			if (!cl.canSeeSky(b) || !cl.getBlockState(b).isAir()) continue;
			cl.addParticle(Ashfall.FLAKE.get(), x, y, z, 0, 0, 0);
		}
		if (r.nextFloat() < here * 0.45f) {
			double x = c.x + (r.nextDouble() - 0.5) * 36, y = c.y + r.nextDouble() * 14, z = c.z + (r.nextDouble() - 0.5) * 36;
			if (cl.canSeeSky(BlockPos.containing(x, y, z))) cl.addParticle(Ashfall.EMBER.get(), x, y, z, 0, 0, 0);
		}
		if (on && here > 0.5f && --nextRumble <= 0) {
			nextRumble = 500 + r.nextInt(900);
			mc.getSoundManager().play(SimpleSoundInstance.forAmbientAddition(SoundEvents.AMBIENT_BASALT_DELTAS_ADDITIONS.value()));
			if (r.nextBoolean())
				mc.getSoundManager().play(SimpleSoundInstance.forUI(SoundEvents.LIGHTNING_BOLT_THUNDER, 0.3f + r.nextFloat() * 0.15f, 0.12f));
		}
	}

	// ---------------------------------------------------------------- the air

	@SubscribeEvent
	static void fogColour(ViewportEvent.ComputeFogColor e) {
		if (here < 0.01f) return;
		float k = here * 0.88f;
		e.setRed(Mth.lerp(k, e.getRed(), 0.16f));
		e.setGreen(Mth.lerp(k, e.getGreen(), 0.04f));
		e.setBlue(Mth.lerp(k, e.getBlue(), 0.025f));
	}

	@SubscribeEvent
	static void fog(ViewportEvent.RenderFog e) {
		if (here < 0.01f || e.getMode() != FogRenderer.FogMode.FOG_TERRAIN) return;
		float far = e.getFarPlaneDistance(), to = Math.min(far, 110);
		e.setFarPlaneDistance(Mth.lerp(here, far, to));
		e.setNearPlaneDistance(Mth.lerp(here, e.getNearPlaneDistance(), 6));
		e.setCanceled(true);
	}

	// ---------------------------------------------------------------- the sky and the ground

	@SubscribeEvent
	static void draw(RenderLevelStageEvent e) {
		if (here < 0.01f || ShaderPacks.on()) return;
		Minecraft mc = Minecraft.getInstance();
		if (mc.level == null) return;
		if (e.getStage() == RenderLevelStageEvent.Stage.AFTER_SKY) sky(e, mc);
	}

	/** our own model-view: the stack's put to identity so the matrix we hand the vertices is the only one */
	private static void begin() {
		RenderSystem.getModelViewStack().pushMatrix().identity();
		RenderSystem.applyModelViewMatrix();
	}

	private static void end() {
		RenderSystem.getModelViewStack().popMatrix();
		RenderSystem.applyModelViewMatrix();
	}

	private static void sky(RenderLevelStageEvent e, Minecraft mc) {
		Matrix4f m = new Matrix4f(e.getModelViewMatrix());
		float pt = e.getPartialTick().getGameTimeDeltaPartialTick(false), t = mc.level.getGameTime() + pt;
		begin();
		RenderSystem.enableBlend();
		RenderSystem.defaultBlendFunc();
		RenderSystem.depthMask(false);
		RenderSystem.disableDepthTest();
		RenderSystem.disableCull();
		RenderSystem.setShader(GameRenderer::getPositionTexColorShader);
		// the dome: a red glow low down, near black overhead
		RenderSystem.setShaderTexture(0, WHITE);
		dome(m, 0, 0, 0.92f * here, false);
		// the ash cloud over it, drifting
		RenderSystem.setShaderTexture(0, CLOUDS);
		dome(m, t * 0.00004f, t * 0.00002f, 0.55f * here, true);
		// the moon, a red coin through the cloud
		float tod = mc.level.getTimeOfDay(pt);
		Vector3f moon = new Vector3f(0, -1, 0).rotate(new Quaternionf().rotationY((float) Math.toRadians(-90)).rotateX(tod * Mth.TWO_PI));
		if (moon.y > -0.1f) {
			RenderSystem.setShaderTexture(0, MOON);
			billboard(m, moon, 14, 14, 0, 1f, 0.42f, 0.28f, 0.85f * here);
		}
		// the mountain on the horizon, its plume rising into the cloud
		RenderSystem.setShaderTexture(0, MOUNTAIN);
		billboard(m, MOUNT_DIR, MOUNT_W, MOUNT_H, -0.06f, 1f, 1f, 1f, here);
		RenderSystem.enableDepthTest();
		RenderSystem.depthMask(true);
		RenderSystem.enableCull();
		RenderSystem.disableBlend();
		end();
	}

	private static float[] skyColour(float el, boolean cloud) {
		// el: -0.3 .. 1 (sin of the elevation)
		float h = Mth.clamp(el, 0, 1);
		if (cloud) return new float[] {Mth.lerp(h, 0.9f, 0.35f), Mth.lerp(h, 0.28f, 0.07f), Mth.lerp(h, 0.12f, 0.04f)};
		float lo = (float) Math.pow(1 - h, 3);
		return new float[] {Mth.lerp(lo, 0.05f, 0.5f), Mth.lerp(lo, 0.008f, 0.1f), Mth.lerp(lo, 0.006f, 0.045f)};
	}

	private static void dome(Matrix4f m, float du, float dv, float alpha, boolean cloud) {
		BufferBuilder b = Tesselator.getInstance().begin(VertexFormat.Mode.QUADS, DefaultVertexFormat.POSITION_TEX_COLOR);
		int rings = 12, segs = 32;
		for (int j = 0; j < rings; j++) {
			float e0 = Mth.lerp(j / (float) rings, -0.3f, 1f), e1 = Mth.lerp((j + 1f) / rings, -0.3f, 1f);
			for (int i = 0; i < segs; i++) {
				float a0 = i * Mth.TWO_PI / segs, a1 = (i + 1) * Mth.TWO_PI / segs;
				float[][] q = {{e0, a0}, {e1, a0}, {e1, a1}, {e0, a1}};
				for (float[] p : q) {
					float el = p[0], c = Mth.sqrt(Math.max(0, 1 - el * el));
					float x = Mth.cos(p[1]) * c, y = el, z = Mth.sin(p[1]) * c;
					// the cloud seen as a low flat deck: its pattern runs out toward the horizon
					float k = 0.35f / (Math.max(el, 0) + 0.18f);
					float[] col = skyColour(el, cloud);
					float a = alpha * (cloud ? Mth.clamp((el + 0.05f) * 4, 0, 1) : 1);
					b.addVertex(m, x * SKY_R, y * SKY_R, z * SKY_R).setUv(x * k + du, z * k + dv).setColor(col[0], col[1], col[2], a);
				}
			}
		}
		BufferUploader.drawWithShader(b.buildOrThrow());
	}

	/** a picture on the sky in this direction, its foot at `drop` below it (fractions of its height), facing you */
	private static void billboard(Matrix4f m, Vector3f dir, float w, float h, float drop, float r, float g, float bl, float a) {
		Vector3f d = new Vector3f(dir).normalize();
		Vector3f up0 = Math.abs(d.y) > 0.95f ? new Vector3f(1, 0, 0) : new Vector3f(0, 1, 0);
		Vector3f side = new Vector3f(up0).cross(d).normalize(), up = new Vector3f(d).cross(side).normalize();
		Vector3f mid = new Vector3f(d).mul(SKY_R * 0.95f).add(new Vector3f(up).mul(h * (0.5f + drop)));
		BufferBuilder b = Tesselator.getInstance().begin(VertexFormat.Mode.QUADS, DefaultVertexFormat.POSITION_TEX_COLOR);
		float[][] q = {{-1, -1, 0, 1}, {1, -1, 1, 1}, {1, 1, 1, 0}, {-1, 1, 0, 0}};
		for (float[] p : q) {
			Vector3f v = new Vector3f(mid).add(new Vector3f(side).mul(p[0] * w / 2)).add(new Vector3f(up).mul(p[1] * h / 2));
			b.addVertex(m, v.x, v.y, v.z).setUv(p[2], p[3]).setColor(r, g, bl, a);
		}
		BufferUploader.drawWithShader(b.buildOrThrow());
	}

	// ---------------------------------------------------------------- the particles

	@SubscribeEvent
	static void providers(RegisterParticleProvidersEvent e) {
		e.registerSpriteSet(Ashfall.FLAKE.get(), sprites -> (o, level, x, y, z, dx, dy, dz) -> new Flake(level, x, y, z, sprites));
		e.registerSpriteSet(Ashfall.EMBER.get(), sprites -> (o, level, x, y, z, dx, dy, dz) -> new Ember(level, x, y, z, sprites));
	}

	/** A flake of ash: grey, tumbling as it drifts down on the wind, settling where it lands. */
	static final class Flake extends TextureSheetParticle {
		private final float spin;

		Flake(ClientLevel level, double x, double y, double z, SpriteSet sprites) {
			super(level, x, y, z, 0, 0, 0);
			xd = 0.012 + random.nextFloat() * 0.01;
			zd = 0.005 + random.nextFloat() * 0.006;
			yd = -0.025 - random.nextFloat() * 0.025;
			lifetime = 180 + random.nextInt(80);
			friction = 0.99f;
			gravity = 0;
			quadSize = 0.045f + random.nextFloat() * 0.05f;
			spin = (random.nextFloat() - 0.5f) * 0.25f;
			roll = random.nextFloat() * Mth.TWO_PI;
			float g = 0.45f + random.nextFloat() * 0.2f;
			rCol = g;
			gCol = g * 0.97f;
			bCol = g * 0.95f;
			alpha = 0;
			pickSprite(sprites);
		}

		@Override
		public void tick() {
			super.tick();
			oRoll = roll;
			if (onGround) {
				yd = xd = zd = 0;
				if (age < lifetime - 30) age = lifetime - 30;
			} else {
				roll += spin;
				xd += Mth.sin(age * 0.09f + spin * 40) * 0.0008f;
				yd = Math.max(yd - 0.0004, -0.06);
			}
			float fade = Math.min(1, Math.min(age / 12f, (lifetime - age) / 30f));
			alpha = fade * 0.95f;
		}

		@Override
		public ParticleRenderType getRenderType() {
			return ParticleRenderType.PARTICLE_SHEET_TRANSLUCENT;
		}
	}

	/** An ember still alight in the ash: a glowing mote, flickering, drifting down slower than the ash, going out. */
	static final class Ember extends TextureSheetParticle {
		private final float phase;

		Ember(ClientLevel level, double x, double y, double z, SpriteSet sprites) {
			super(level, x, y, z, 0, 0, 0);
			xd = 0.01 + random.nextFloat() * 0.01;
			zd = 0.004 + random.nextFloat() * 0.005;
			yd = -0.012 - random.nextFloat() * 0.012;
			lifetime = 100 + random.nextInt(80);
			friction = 0.985f;
			gravity = 0;
			hasPhysics = false;
			quadSize = 0.03f + random.nextFloat() * 0.025f;
			phase = random.nextFloat() * 6.283f;
			rCol = 1f;
			gCol = 0.42f + random.nextFloat() * 0.2f;
			bCol = 0.12f;
			pickSprite(sprites);
		}

		@Override
		public void tick() {
			super.tick();
			xd += (random.nextFloat() - 0.5f) * 0.003f;
			yd += (random.nextFloat() - 0.45f) * 0.002f;
			float flick = 0.65f + 0.35f * Mth.sin(age * 0.6f + phase);
			float life = 1 - age / (float) lifetime;
			alpha = Math.min(1, age / 8f) * flick * life;
			gCol = 0.25f + 0.35f * life;
		}

		@Override
		protected int getLightColor(float partial) {
			return 0xF000F0;
		}

		@Override
		public ParticleRenderType getRenderType() {
			return ParticleRenderType.PARTICLE_SHEET_TRANSLUCENT;
		}
	}
}
