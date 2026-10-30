package com.snoringwalrus.ashbound.client;

import org.joml.Vector3f;

import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.BufferBuilder;
import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.mojang.blaze3d.vertex.Tesselator;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.blaze3d.vertex.VertexFormat;
import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.Gates;

import net.minecraft.client.Camera;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.ParticleRenderType;
import net.minecraft.client.particle.SpriteSet;
import net.minecraft.client.particle.TextureSheetParticle;
import net.minecraft.client.renderer.texture.TextureManager;
import net.minecraft.core.particles.ColorParticleOption;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.RegisterParticleProvidersEvent;

/** The gate's sparks and smoke (spawned by GateFx). */
@EventBusSubscriber(modid = Ashbound.ID, value = Dist.CLIENT)
public final class GateParticles {
	private GateParticles() {}

	/** Drawn by gate_particle.fsh from noise, not the sprite: soft edges, no alpha-test cutout, no depth writes. */
	static final ParticleRenderType SOFT = new ParticleRenderType() {
		@Override
		public BufferBuilder begin(Tesselator tesselator, TextureManager textures) {
			RenderSystem.enableBlend();
			RenderSystem.defaultBlendFunc();
			RenderSystem.depthMask(false);
			RenderSystem.setShader(() -> GateShaders.particle);
			return tesselator.begin(VertexFormat.Mode.QUADS, DefaultVertexFormat.POSITION_COLOR_TEX_LIGHTMAP);
		}

		@Override
		public String toString() {
			return "ASHBOUND_GATE_SOFT";
		}
	};

	@SubscribeEvent
	static void providers(RegisterParticleProvidersEvent e) {
		e.registerSpriteSet(Gates.SPARK.get(), sprites -> (o, level, x, y, z, dx, dy, dz) -> new Spark(level, x, y, z, dx, dy, dz, o, sprites));
		e.registerSpriteSet(Gates.SMOKE.get(), sprites -> (o, level, x, y, z, dx, dy, dz) -> new Smoke(level, x, y, z, dx, dy, dz, o, sprites));
		e.registerSpriteSet(com.snoringwalrus.ashbound.Fireflies.MOTE.get(), sprites -> (o, level, x, y, z, dx, dy, dz) -> new Firefly(level, x, y, z, sprites));
	}

	/** A firefly (from Fireflies' blocks): a soft mote, full bright, that wanders slowly, bobs and blinks. */
	static final class Firefly extends TextureSheetParticle {
		private final float phase, rate;

		Firefly(ClientLevel level, double x, double y, double z, SpriteSet sprites) {
			super(level, x, y, z, 0, 0, 0);
			xd = (random.nextFloat() - 0.5f) * 0.02f;
			yd = (random.nextFloat() - 0.5f) * 0.01f;
			zd = (random.nextFloat() - 0.5f) * 0.02f;
			lifetime = 90 + random.nextInt(110);
			friction = 0.96f;
			gravity = 0;
			hasPhysics = false;
			quadSize = 0.045f + random.nextFloat() * 0.03f;
			phase = random.nextFloat() * 6.283f;
			rate = 0.12f + random.nextFloat() * 0.1f;
			float warm = random.nextFloat();
			rCol = 0.72f + warm * 0.25f;
			gCol = 1.0f;
			bCol = 0.35f + (1 - warm) * 0.2f;
			alpha = 0;
			pickSprite(sprites);
		}

		@Override
		public void tick() {
			super.tick();
			xd += (random.nextFloat() - 0.5f) * 0.004f;
			yd += (random.nextFloat() - 0.5f) * 0.002f + Mth.sin(age * 0.07f + phase) * 0.0006f;
			zd += (random.nextFloat() - 0.5f) * 0.004f;
			float blink = 0.5f + 0.5f * Mth.sin(age * rate + phase);
			float fade = Math.min(1, Math.min(age / 20f, (lifetime - age) / 20f));
			alpha = fade * (0.25f + 0.75f * blink * blink);
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

	/** A hot sliver: drawn as a streak along its flight, white-hot cooling to its colour, full bright. */
	static final class Spark extends TextureSheetParticle {
		private final float r0, g0, b0;

		Spark(ClientLevel level, double x, double y, double z, double dx, double dy, double dz, ColorParticleOption o, SpriteSet sprites) {
			super(level, x, y, z, 0, 0, 0);
			xd = dx;
			yd = dy;
			zd = dz;
			r0 = o.getRed();
			g0 = o.getGreen();
			b0 = o.getBlue();
			lifetime = 8 + random.nextInt(10);
			friction = 0.9f;
			gravity = 0.05f;
			hasPhysics = false;
			quadSize = 0.035f + random.nextFloat() * 0.03f;
			pickSprite(sprites);
		}

		@Override
		public void tick() {
			super.tick();
			float k = (float) age / lifetime;
			rCol = Mth.lerp(k, 0.5f + r0 * 0.5f, r0);
			gCol = Mth.lerp(k, 0.47f + g0 * 0.5f, g0);
			bCol = Mth.lerp(k, 0.44f + b0 * 0.5f, b0);
			alpha = 1 - k * k;
		}

		@Override
		public void render(VertexConsumer buffer, Camera camera, float partial) {
			Vec3 cam = camera.getPosition();
			float x = (float) (Mth.lerp(partial, xo, this.x) - cam.x), y = (float) (Mth.lerp(partial, yo, this.y) - cam.y),
					z = (float) (Mth.lerp(partial, zo, this.z) - cam.z);
			Vector3f v = new Vector3f((float) xd, (float) yd, (float) zd);
			float speed = v.length();
			if (speed < 1e-4f) v.set(0, 0.01f, 0);
			Vector3f tail = new Vector3f(v).mul(-Math.min(6f, 2.5f + speed * 10));
			Vector3f side = new Vector3f(v).cross(x, y, z);
			if (side.lengthSquared() < 1e-10f) return;
			side.normalize(quadSize);
			int light = 0xF000F0;
			// head at v 0, tail at v 1; the head pokes a little ahead so its tip is rounded off too
			Vector3f nose = new Vector3f(tail).mul(-0.12f);
			buffer.addVertex(x + nose.x - side.x, y + nose.y - side.y, z + nose.z - side.z).setUv(-3, 0).setColor(rCol, gCol, bCol, alpha).setLight(light);
			buffer.addVertex(x + nose.x + side.x, y + nose.y + side.y, z + nose.z + side.z).setUv(-1, 0).setColor(rCol, gCol, bCol, alpha).setLight(light);
			buffer.addVertex(x + tail.x + side.x, y + tail.y + side.y, z + tail.z + side.z).setUv(-1, 1).setColor(rCol, gCol, bCol, alpha * 0.3f).setLight(light);
			buffer.addVertex(x + tail.x - side.x, y + tail.y - side.y, z + tail.z - side.z).setUv(-3, 1).setColor(rCol, gCol, bCol, alpha * 0.3f).setLight(light);
		}

		@Override
		public ParticleRenderType getRenderType() {
			return SOFT;
		}
	}

	/** A soft puff that swells, turns and rises; near the rim it glows (lit by the gate, not the world). */
	static final class Smoke extends TextureSheetParticle {
		private final boolean glowing;
		private final float size, spin, peak;
		/** Which puff of noise (the shader reads it back from the u range). */
		private final int shape;

		Smoke(ClientLevel level, double x, double y, double z, double dx, double dy, double dz, ColorParticleOption o, SpriteSet sprites) {
			super(level, x, y, z, 0, 0, 0);
			xd = dx;
			yd = dy;
			zd = dz;
			rCol = o.getRed();
			gCol = o.getGreen();
			bCol = o.getBlue();
			glowing = o.getAlpha() < 0.999f;
			lifetime = 40 + random.nextInt(40);
			friction = 0.94f;
			gravity = -0.012f;
			hasPhysics = false;
			size = 0.9f + random.nextFloat() * 1.3f;
			spin = (random.nextFloat() - 0.5f) * 0.06f;
			peak = glowing ? 0.4f : 0.55f;
			roll = random.nextFloat() * Mth.TWO_PI;
			shape = random.nextInt(64);
			pickSprite(sprites);
			alpha = 0;
		}

		@Override
		public void tick() {
			super.tick();
			oRoll = roll;
			roll += spin;
			float k = (float) age / lifetime;
			quadSize = size * (0.4f + k * 1.4f);
			alpha = peak * Math.min(1, k * 6) * (1 - k);
		}

		@Override
		protected float getU0() {
			return shape * 2;
		}

		@Override
		protected float getU1() {
			return shape * 2 + 1;
		}

		@Override
		protected float getV0() {
			return 0;
		}

		@Override
		protected float getV1() {
			return 1;
		}

		@Override
		protected int getLightColor(float partial) {
			return glowing ? 0xF000F0 : super.getLightColor(partial);
		}

		@Override
		public ParticleRenderType getRenderType() {
			return SOFT;
		}
	}
}
