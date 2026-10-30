package com.snoringwalrus.ashbound.client;

import com.mojang.blaze3d.vertex.VertexConsumer;
import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.Vfx;
import net.minecraft.client.Camera;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.ParticleRenderType;
import net.minecraft.client.particle.SpriteSet;
import net.minecraft.client.particle.TextureSheetParticle;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.RegisterParticleProvidersEvent;
import org.joml.Vector3f;

/**
 * The curios' effects (Vfx): the gate's soft particles (GateParticles, gate_particle.fsh) sized and timed per effect.
 * A wisp swells, turns and fades (glowing or lit by the world); a mote is a hot streak along its flight, white cooling
 * to its colour.
 */
@EventBusSubscriber(modid = Ashbound.ID, value = Dist.CLIENT)
public final class CurioParticles {
	private CurioParticles() {}

	@SubscribeEvent
	static void providers(RegisterParticleProvidersEvent e) {
		e.registerSpriteSet(Vfx.TYPE.get(), sprites -> (o, level, x, y, z, dx, dy, dz) -> new Bit(level, x, y, z, dx, dy, dz, o, sprites));
	}

	static final class Bit extends TextureSheetParticle {
		private final boolean glowing, streak, ring, bolt;
		private final float r0, g0, b0, size, spin, peak;
		private final int shape;
		/** a ring: its radius and growth a tick, its brightness round the band (broken up); a bolt: where it ends */
		private float radius, grow;
		private float[] patches;
		private double bx, by, bz;

		Bit(ClientLevel level, double x, double y, double z, double dx, double dy, double dz, Vfx.Opt o, SpriteSet sprites) {
			super(level, x, y, z, 0, 0, 0);
			xd = dx;
			yd = dy;
			zd = dz;
			r0 = (o.rgb() >> 16 & 255) / 255f;
			g0 = (o.rgb() >> 8 & 255) / 255f;
			b0 = (o.rgb() & 255) / 255f;
			rCol = r0;
			gCol = g0;
			bCol = b0;
			glowing = o.glow();
			streak = o.streak();
			ring = o.ring();
			bolt = o.bolt();
			lifetime = Math.max(2, Math.round(o.life() * (0.75f + random.nextFloat() * 0.5f)));
			gravity = o.gravity();
			friction = streak ? 0.9f : 0.93f;
			hasPhysics = false;
			size = o.size() * (0.8f + random.nextFloat() * 0.4f);
			quadSize = size;
			spin = (random.nextFloat() - 0.5f) * 0.08f;
			peak = glowing ? 0.55f : 0.7f;
			roll = random.nextFloat() * Mth.TWO_PI;
			shape = random.nextInt(64);
			pickSprite(sprites);
			alpha = streak ? 1 : 0;
			if (ring) {
				radius = (float) dx;
				grow = o.gravity();
				gravity = 0;
				lifetime = o.life();
				patches = new float[48];
				float w = random.nextFloat();
				for (int i = 0; i < patches.length; i++) {   // a slow wander round the ring: bright runs and gaps
					w = Mth.clamp(w + (random.nextFloat() - 0.5f) * 0.5f, 0, 1);
					patches[i] = 0.25f + 0.75f * w;
				}
			}
			if (bolt) {
				bx = dx;
				by = dy;
				bz = dz;
				lifetime = o.life();
			}
			if (ring || bolt) {
				xd = yd = zd = 0;
				alpha = 1;
			}
		}

		@Override
		public net.minecraft.world.phys.AABB getRenderBoundingBox(float partial) {
			if (ring) return new net.minecraft.world.phys.AABB(x, y, z, x, y, z).inflate(radius + grow * lifetime + size + 1);
			if (bolt) return new net.minecraft.world.phys.AABB(x, y, z, x + bx, y + by, z + bz).inflate(1);
			return super.getRenderBoundingBox(partial);
		}

		@Override
		public void tick() {
			super.tick();
			float k = (float) age / lifetime;
			if (ring) {
				radius += grow;
				// white-hot as it flares, its colour as it spreads, fading out
				float h = Math.max(0, 1 - k * 3);
				rCol = Mth.lerp(h, r0, 0.6f + r0 * 0.4f);
				gCol = Mth.lerp(h, g0, 0.6f + g0 * 0.4f);
				bCol = Mth.lerp(h, b0, 0.6f + b0 * 0.4f);
				alpha = Math.min(1, k * 8) * (1 - k * k);
				return;
			}
			if (bolt) {
				alpha = (age % 2 == 0 ? 1f : 0.7f) * (1 - k * k);
				return;
			}
			if (streak) {
				rCol = Mth.lerp(k, 0.55f + r0 * 0.45f, r0);
				gCol = Mth.lerp(k, 0.55f + g0 * 0.45f, g0);
				bCol = Mth.lerp(k, 0.55f + b0 * 0.45f, b0);
				alpha = 1 - k * k;
				return;
			}
			oRoll = roll;
			roll += spin;
			quadSize = size * (0.45f + k * 1.1f);
			alpha = peak * Math.min(1, k * 5) * (1 - k);
		}

		@Override
		public void render(VertexConsumer buffer, Camera camera, float partial) {
			if (ring) {
				renderRing(buffer, camera, partial);
				return;
			}
			if (bolt) {
				renderBolt(buffer, camera);
				return;
			}
			if (!streak) {
				super.render(buffer, camera, partial);
				return;
			}
			Vec3 cam = camera.getPosition();
			float x = (float) (Mth.lerp(partial, xo, this.x) - cam.x), y = (float) (Mth.lerp(partial, yo, this.y) - cam.y),
					z = (float) (Mth.lerp(partial, zo, this.z) - cam.z);
			Vector3f v = new Vector3f((float) xd, (float) yd, (float) zd);
			float speed = v.length();
			if (speed < 1e-4f) v.set(0, 0.01f, 0);
			Vector3f tail = new Vector3f(v).mul(-Math.min(5f, 1.5f + speed * 8));
			Vector3f side = new Vector3f(v).cross(x, y, z);
			if (side.lengthSquared() < 1e-10f) return;
			side.normalize(quadSize);
			int light = 0xF000F0;
			Vector3f nose = new Vector3f(tail).mul(-0.12f);
			buffer.addVertex(x + nose.x - side.x, y + nose.y - side.y, z + nose.z - side.z).setUv(-3, 0).setColor(rCol, gCol, bCol, alpha).setLight(light);
			buffer.addVertex(x + nose.x + side.x, y + nose.y + side.y, z + nose.z + side.z).setUv(-1, 0).setColor(rCol, gCol, bCol, alpha).setLight(light);
			buffer.addVertex(x + tail.x + side.x, y + tail.y + side.y, z + tail.z + side.z).setUv(-1, 1).setColor(rCol, gCol, bCol, alpha * 0.3f).setLight(light);
			buffer.addVertex(x + tail.x - side.x, y + tail.y - side.y, z + tail.z - side.z).setUv(-3, 1).setColor(rCol, gCol, bCol, alpha * 0.3f).setLight(light);
		}

		/** a flat band round the centre: soft across it (the shader's streak mode, u -3..-1, v held at full) */
		private void renderRing(VertexConsumer buffer, Camera camera, float partial) {
			Vec3 cam = camera.getPosition();
			float cx = (float) (x - cam.x), cy = (float) (y - cam.y), cz = (float) (z - cam.z);
			float r = radius + grow * partial, w = size, v = 0.2f;
			int n = patches.length, light = 0xF000F0;
			for (int i = 0; i < n; i++) {
				float a0 = Mth.TWO_PI * i / n, a1 = Mth.TWO_PI * (i + 1) / n;
				float c0 = Mth.cos(a0), s0 = Mth.sin(a0), c1 = Mth.cos(a1), s1 = Mth.sin(a1);
				float p0 = alpha * patches[i], p1 = alpha * patches[(i + 1) % n];
				for (int side = 0; side < 2; side++) {   // both faces: seen from above and below
					float ro = side == 0 ? r + w : r - w, ri = side == 0 ? r - w : r + w, uo = side == 0 ? -3 : -1, ui = side == 0 ? -1 : -3;
					buffer.addVertex(cx + c0 * ro, cy, cz + s0 * ro).setUv(uo, v).setColor(rCol, gCol, bCol, p0).setLight(light);
					buffer.addVertex(cx + c1 * ro, cy, cz + s1 * ro).setUv(uo, v).setColor(rCol, gCol, bCol, p1).setLight(light);
					buffer.addVertex(cx + c1 * ri, cy, cz + s1 * ri).setUv(ui, v).setColor(rCol, gCol, bCol, p1).setLight(light);
					buffer.addVertex(cx + c0 * ri, cy, cz + s0 * ri).setUv(ui, v).setColor(rCol, gCol, bCol, p0).setLight(light);
				}
			}
		}

		/** a jagged ribbon facing the camera, new kinks every other tick: a white core in a wider sheath */
		private void renderBolt(VertexConsumer buffer, Camera camera) {
			Vec3 cam = camera.getPosition();
			net.minecraft.util.RandomSource rnd = net.minecraft.util.RandomSource.create(shape * 31L + age / 2);
			int n = 10;
			Vector3f[] pts = new Vector3f[n + 1];
			Vector3f along = new Vector3f((float) bx, (float) by, (float) bz);
			float jag = Math.min(0.6f, along.length() * 0.12f);
			for (int i = 0; i <= n; i++) {
				float t = i / (float) n, k = Mth.sin(Mth.PI * t) * jag;
				pts[i] = new Vector3f((float) (x - cam.x), (float) (y - cam.y), (float) (z - cam.z)).add(new Vector3f(along).mul(t))
						.add((rnd.nextFloat() - 0.5f) * 2 * k, (rnd.nextFloat() - 0.5f) * 2 * k, (rnd.nextFloat() - 0.5f) * 2 * k);
			}
			int light = 0xF000F0;
			for (int pass = 0; pass < 2; pass++) {
				float w = pass == 0 ? size * 3.5f : size;
				float r = pass == 0 ? rCol : 0.9f, g = pass == 0 ? gCol : 0.96f, b = pass == 0 ? bCol : 1f, a = pass == 0 ? alpha * 0.55f : alpha;
				for (int i = 0; i < n; i++) {
					Vector3f p = pts[i], q = pts[i + 1];
					Vector3f side = new Vector3f(q).sub(p).cross(new Vector3f(p).add(q).mul(0.5f));
					if (side.lengthSquared() < 1e-10f) continue;
					side.normalize(w);
					buffer.addVertex(p.x - side.x, p.y - side.y, p.z - side.z).setUv(-3, 0.2f).setColor(r, g, b, a).setLight(light);
					buffer.addVertex(p.x + side.x, p.y + side.y, p.z + side.z).setUv(-1, 0.2f).setColor(r, g, b, a).setLight(light);
					buffer.addVertex(q.x + side.x, q.y + side.y, q.z + side.z).setUv(-1, 0.2f).setColor(r, g, b, a).setLight(light);
					buffer.addVertex(q.x - side.x, q.y - side.y, q.z - side.z).setUv(-3, 0.2f).setColor(r, g, b, a).setLight(light);
				}
			}
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
			return GateParticles.SOFT;
		}
	}
}
