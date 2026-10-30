package com.snoringwalrus.ashbound.client;

import org.joml.Vector3f;

import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.platform.GlStateManager;
import com.mojang.blaze3d.vertex.BufferBuilder;
import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.mojang.blaze3d.vertex.Tesselator;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.blaze3d.vertex.VertexFormat;
import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.SpellLook;
import com.snoringwalrus.ashbound.Spells;

import net.minecraft.client.Camera;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.Particle;
import net.minecraft.client.particle.ParticleRenderType;
import net.minecraft.client.renderer.texture.TextureManager;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * The pieces the mage's magic is drawn with (SpellFx puts them together): flipbooks of Cycles fire and smoke from one
 * atlas (tools/vfx_atlas.py), spell circles, beams, crystal, beads of liquid, black holes, domes. All go through
 * spell_fx.fsh, whose modes are the constants here; the lightmap slot carries the mode, these aren't lit by the world.
 */
final class SpellParticles {
	private SpellParticles() {}

	static final int FIRE = 0, SMOKE = 1, CIRCLE = 2, DROP = 3, HOLE = 4, CRYSTAL = 5, STREAK = 6, GLOW = 7, PLAIN = 8;
	/** the atlas's flipbooks */
	static final int BLAST = 0, FLAME = 1, ROLL = 2;

	private static final ResourceLocation ATLAS = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/vfx/spell.png");
	private static final float CELL = 1 / 8f;

	static final ParticleRenderType TYPE = new ParticleRenderType() {
		@Override
		public BufferBuilder begin(Tesselator tesselator, TextureManager textures) {
			RenderSystem.enableBlend();
			RenderSystem.blendFunc(GlStateManager.SourceFactor.ONE, GlStateManager.DestFactor.ONE_MINUS_SRC_ALPHA);
			RenderSystem.depthMask(false);
			RenderSystem.disableCull();
			RenderSystem.setShader(() -> GateShaders.spell);
			RenderSystem.setShaderTexture(0, ATLAS);
			return tesselator.begin(VertexFormat.Mode.QUADS, DefaultVertexFormat.POSITION_COLOR_TEX_LIGHTMAP);
		}

		@Override
		public String toString() {
			return "ASHBOUND_SPELL";
		}
	};

	/** Anything of ours: its colour, no collision unless it asks, and never culled for being large. */
	abstract static class Fx extends Particle {
		Fx(ClientLevel level, Vec3 at, int rgb) {
			super(level, at.x, at.y, at.z);
			rCol = (rgb >> 16 & 255) / 255f;
			gCol = (rgb >> 8 & 255) / 255f;
			bCol = (rgb & 255) / 255f;
			hasPhysics = false;
			gravity = 0;
			friction = 0.96f;
		}

		final void corner(VertexConsumer b, Vector3f p, float u, float v, float a, int mode) {
			b.addVertex(p.x, p.y, p.z).setUv(u, v).setColor(rCol, gCol, bCol, a).setLight(mode);
		}

		final Vector3f here(Camera cam, float partial) {
			Vec3 c = cam.getPosition();
			return new Vector3f((float) (Mth.lerp(partial, xo, x) - c.x), (float) (Mth.lerp(partial, yo, y) - c.y), (float) (Mth.lerp(partial, zo, z) - c.z));
		}

		/** A quad round a centre, spanned by two half-axes. */
		final void quad(VertexConsumer b, Vector3f c, Vector3f side, Vector3f up, float u0, float v0, float u1, float v1, float a, int mode) {
			corner(b, new Vector3f(c).sub(side).sub(up), u0, v1, a, mode);
			corner(b, new Vector3f(c).sub(side).add(up), u0, v0, a, mode);
			corner(b, new Vector3f(c).add(side).add(up), u1, v0, a, mode);
			corner(b, new Vector3f(c).add(side).sub(up), u1, v1, a, mode);
		}

		/** A flipbook's frame, or a quad of a drawn mode. */
		final void frame(VertexConsumer b, Vector3f c, Vector3f side, Vector3f up, int sheet, int mode, float k, float a) {
			if (mode > CIRCLE) {
				quad(b, c, side, up, -1, 1, 1, -1, a, mode);
				return;
			}
			int f = Mth.clamp((int) (k * 16), 0, 15);
			float u = (sheet == FLAME ? 0.5f : 0) + (f % 4) * CELL, v = (sheet == ROLL ? 0.5f : 0) + (f / 4) * CELL;
			quad(b, c, side, up, u, v, u + CELL, v + CELL, a, mode);
		}

		/** A line of points as a ribbon turned to the camera, soft across it; a fades along it from a0 to a1. */
		final void strip(VertexConsumer b, Vector3f[] pts, float width, float a0, float a1) {
			for (int i = 0; i + 1 < pts.length; i++) {
				Vector3f p = pts[i], q = pts[i + 1];
				Vector3f side = new Vector3f(q).sub(p).cross(new Vector3f(p).add(q).mul(0.5f));
				if (side.lengthSquared() < 1e-10f) continue;
				side.normalize(width);
				float s = a0 + (a1 - a0) * i / (pts.length - 1f), t = a0 + (a1 - a0) * (i + 1) / (pts.length - 1f);
				corner(b, new Vector3f(p).sub(side), -1, 0, s, STREAK);
				corner(b, new Vector3f(p).add(side), 1, 0, s, STREAK);
				corner(b, new Vector3f(q).add(side), 1, 0, t, STREAK);
				corner(b, new Vector3f(q).sub(side), -1, 0, t, STREAK);
			}
		}

		@Override
		public AABB getRenderBoundingBox(float partial) {
			return new AABB(x, y, z, x, y, z).inflate(24);
		}

		@Override
		public ParticleRenderType getRenderType() {
			return TYPE;
		}
	}

	static Vector3f right(Camera c) {
		return new Vector3f(1, 0, 0).rotate(c.rotation());
	}

	static Vector3f up(Camera c) {
		return new Vector3f(0, 1, 0).rotate(c.rotation());
	}

	/** A billboard: a flipbook playing once over its life, or a drawn mode; along its flight if it's stretched. */
	static class Flip extends Fx {
		final int sheet, mode;
		final float s0, s1, peak;
		float stretch = 1, roll0;

		Flip(ClientLevel level, Vec3 at, Vec3 v, int rgb, int sheet, int mode, float s0, float s1, int life, float peak) {
			super(level, at, rgb);
			xd = v.x;
			yd = v.y;
			zd = v.z;
			this.sheet = sheet;
			this.mode = mode;
			this.s0 = s0;
			this.s1 = s1;
			this.peak = peak;
			lifetime = Math.max(2, Math.round(life * (0.85f + random.nextFloat() * 0.3f)));
			roll0 = random.nextFloat() * Mth.TWO_PI;
		}

		Flip stretched(float s) {
			stretch = s;
			return this;
		}

		float fade(float k) {
			return Math.min(1, k * 8) * (mode == SMOKE ? 1 - k * k : 1 - k * k * k);
		}

		@Override
		public void render(VertexConsumer b, Camera cam, float partial) {
			float k = Math.min(1, (age + partial) / lifetime), size = Mth.lerp(k, s0, s1);
			Vector3f c = here(cam, partial), side, up;
			if (stretch != 1 && xd * xd + yd * yd + zd * zd > 1e-6) {   // the flame's tip trails back along its flight
				up = new Vector3f((float) -xd, (float) -yd, (float) -zd).normalize(size * stretch);
				side = new Vector3f(up).cross(c);
				if (side.lengthSquared() < 1e-10f) return;
				side.normalize(size);
			} else {
				float co = Mth.cos(roll0), si = Mth.sin(roll0);
				Vector3f r = right(cam), u = up(cam);
				side = new Vector3f(r).mul(co * size).add(new Vector3f(u).mul(si * size));
				up = new Vector3f(u).mul(co * size).sub(new Vector3f(r).mul(si * size));
			}
			frame(b, c, side, up, sheet, mode, k, peak * fade(k));
		}
	}

	/** A flame going round a point, dragged into it. */
	static final class Orbit extends Flip {
		final Vec3 mid;
		final float tilt;
		float angle, radius;

		Orbit(ClientLevel level, Vec3 mid, float radius, float angle, float tilt, int rgb, float size, int life) {
			super(level, mid, Vec3.ZERO, rgb, FLAME, FIRE, size, size * 0.6f, life, 0.9f);
			this.mid = mid;
			this.radius = radius;
			this.angle = angle;
			this.tilt = tilt;
			place();
			xo = x;
			yo = y;
			zo = z;
		}

		private void place() {
			double c = Math.cos(angle) * radius, s = Math.sin(angle) * radius;
			setPos(mid.x + c, mid.y + s * Math.sin(tilt), mid.z + s * Math.cos(tilt));
		}

		@Override
		public void tick() {
			xo = x;
			yo = y;
			zo = z;
			if (age++ >= lifetime) remove();
			angle += 0.38f;
			radius *= 0.97f;
			double ox = x, oy = y, oz = z;
			place();
			xd = x - ox;
			yd = y - oy;
			zd = z - oz;
			stretch = 1.5f;
		}
	}

	/** A flat thing on the ground: a spell circle or a pool of light, opening, turning, fading. */
	static final class Flat extends Fx {
		final int mode;
		final float radius, spin, peak;

		Flat(ClientLevel level, Vec3 at, int rgb, int mode, float radius, int life, float spin, float peak) {
			super(level, at, rgb);
			this.mode = mode;
			this.radius = radius;
			this.spin = spin;
			this.peak = peak;
			lifetime = life;
		}

		@Override
		public void tick() {
			xo = x;
			yo = y;
			zo = z;
			if (age++ >= lifetime) remove();
		}

		@Override
		public void render(VertexConsumer b, Camera cam, float partial) {
			float t = age + partial, k = t / lifetime, open = 1 - (1 - Math.min(1, t / 7)) * (1 - Math.min(1, t / 7)) * (1 - Math.min(1, t / 7));
			float r = radius * (mode == CIRCLE ? open : 0.5f + 0.5f * open), a = spin * t;
			Vector3f side = new Vector3f(Mth.cos(a) * r, 0, Mth.sin(a) * r), up = new Vector3f(-Mth.sin(a) * r, 0, Mth.cos(a) * r);
			float alpha = peak * Math.min(1, t / 4) * Math.min(1, (1 - k) * 4);
			if (mode == CIRCLE) quad(b, here(cam, partial), side, up, 0.5f, 0.5f, 1, 1, alpha, CIRCLE);
			else quad(b, here(cam, partial), side, up, -1, 1, 1, -1, alpha, mode);
		}
	}

	/** A shaft of light between two points, or standing on someone; gone at the far end. */
	static final class Beam extends Fx {
		final Entity on;
		final Vec3 reach;
		final float width, peak, fall;

		Beam(ClientLevel level, Vec3 at, Vec3 reach, int rgb, float width, int life, float peak, Entity on, float fall) {
			super(level, at, rgb);
			this.reach = reach;
			this.width = width;
			this.peak = peak;
			this.on = on;
			this.fall = fall;
			lifetime = life;
		}

		@Override
		public void tick() {
			xo = x;
			yo = y;
			zo = z;
			if (age++ >= lifetime) remove();
			if (on != null) setPos(on.getX(), on.getY(), on.getZ());
		}

		@Override
		public AABB getRenderBoundingBox(float partial) {
			return super.getRenderBoundingBox(partial).inflate(reach.length());
		}

		@Override
		public void render(VertexConsumer b, Camera cam, float partial) {
			float t = age + partial, k = t / lifetime, a = peak * Math.min(1, t / 3) * (1 - k * k);
			Vector3f p = here(cam, partial), q = new Vector3f(p).add((float) reach.x, (float) reach.y, (float) reach.z);
			Vector3f m = new Vector3f(p).lerp(q, 0.5f);
			strip(b, new Vector3f[] {p, m, q}, width * Math.min(1, t / 2 + 0.3f), a, a * fall);
		}
	}

	/** A bead of liquid, flying and falling, drawn out along its flight; gone when it lands. */
	static final class Bead extends Flip {
		Bead(ClientLevel level, Vec3 at, Vec3 v, int rgb, float size, int life) {
			super(level, at, v, rgb, 0, DROP, size, size * 0.7f, life, 1);
			hasPhysics = true;
			gravity = 0.85f;
			friction = 0.985f;
			stretched(1.6f);
			setSize(0.05f, 0.05f);
		}

		@Override
		public void tick() {
			super.tick();
			if (onGround) remove();
		}

		@Override
		float fade(float k) {
			return 1;
		}
	}

	/** A spike of crystal growing from a point along an axis, then gone. */
	static final class Spike extends Fx {
		final Vector3f axis;
		final float wide;
		final int hold;
		boolean grown;

		Spike(ClientLevel level, Vec3 at, Vec3 axis, int rgb, float wide, int life) {
			super(level, at, rgb);
			this.axis = new Vector3f((float) axis.x, (float) axis.y, (float) axis.z);
			this.wide = wide;
			hold = life;
			lifetime = life;
		}

		@Override
		public void tick() {
			xo = x;
			yo = y;
			zo = z;
			if (age++ >= lifetime) remove();
		}

		@Override
		public void render(VertexConsumer b, Camera cam, float partial) {
			float t = age + partial, grow = Math.min(1, t / 3), a = Math.min(1, (1 - t / lifetime) * 5);
			crystal(this, b, here(cam, partial), new Vector3f(axis).mul(grow), wide * grow, a);
		}
	}

	/** Six-sided spike: base at c, point at c + axis. Each face's brightness is how far round it is from the light. */
	static void crystal(Fx f, VertexConsumer b, Vector3f c, Vector3f axis, float wide, float a) {
		Vector3f n = new Vector3f(axis).normalize();
		Vector3f s = new Vector3f(n).cross(0.31f, 0.91f, 0.27f);
		if (s.lengthSquared() < 1e-6f) s.set(1, 0, 0);
		s.normalize(wide);
		Vector3f t = new Vector3f(n).cross(s).normalize(wide);
		Vector3f tip = new Vector3f(c).add(axis), belly = new Vector3f(c).add(new Vector3f(axis).mul(0.12f));
		for (int i = 0; i < 6; i++) {
			float a0 = i * Mth.TWO_PI / 6, a1 = (i + 1) * Mth.TWO_PI / 6, lit = 0.5f + 0.5f * Mth.cos(a0 + 0.5f);
			Vector3f p = new Vector3f(belly).add(new Vector3f(s).mul(Mth.cos(a0))).add(new Vector3f(t).mul(Mth.sin(a0)));
			Vector3f q = new Vector3f(belly).add(new Vector3f(s).mul(Mth.cos(a1))).add(new Vector3f(t).mul(Mth.sin(a1)));
			f.corner(b, p, lit, 0, a, CRYSTAL);
			f.corner(b, q, lit, 0, a, CRYSTAL);
			f.corner(b, tip, lit, 0, a, CRYSTAL);
			f.corner(b, tip, lit, 0, a, CRYSTAL);
			f.corner(b, p, lit * 0.7f, 0, a, CRYSTAL);
			f.corner(b, q, lit * 0.7f, 0, a, CRYSTAL);
			f.corner(b, c, lit * 0.7f, 0, a, CRYSTAL);
			f.corner(b, c, lit * 0.7f, 0, a, CRYSTAL);
		}
	}

	/** A dome of light: bright only where you see it edge on, with ribs running up it. */
	static final class Dome extends Fx {
		final float radius;
		static final int ROUND = 32, UP = 10, RIBS = 16;

		Dome(ClientLevel level, Vec3 at, int rgb, float radius, int life) {
			super(level, at, rgb);
			this.radius = radius;
			lifetime = life;
		}

		@Override
		public void tick() {
			xo = x;
			yo = y;
			zo = z;
			if (age++ >= lifetime) remove();
		}

		@Override
		public AABB getRenderBoundingBox(float partial) {
			return super.getRenderBoundingBox(partial).inflate(radius);
		}

		private Vector3f on(Vector3f c, float r, int round, float up) {
			float a = round * Mth.TWO_PI / ROUND, e = up * Mth.HALF_PI, h = Mth.cos(e) * r;
			return new Vector3f(c).add(Mth.cos(a) * h, Mth.sin(e) * r, Mth.sin(a) * h);
		}

		private float rim(Vector3f p, Vector3f c) {
			float n = new Vector3f(p).sub(c).normalize().dot(new Vector3f(p).normalize());
			return (float) Math.pow(1 - Math.abs(n), 2.5);
		}

		@Override
		public void render(VertexConsumer b, Camera cam, float partial) {
			float t = age + partial, grow = 1 - (1 - Math.min(1, t / 8)) * (1 - Math.min(1, t / 8)), r = radius * grow;
			float a = Math.min(1, (1 - t / lifetime) * 3);
			Vector3f c = here(cam, partial);
			for (int i = 0; i < ROUND; i++)
				for (int j = 0; j < UP; j++) {
					Vector3f p = on(c, r, i, j / (float) UP), q = on(c, r, i + 1, j / (float) UP), s = on(c, r, i + 1, (j + 1) / (float) UP), u = on(c, r, i, (j + 1) / (float) UP);
					corner(b, p, 0, 0, a * rim(p, c), PLAIN);
					corner(b, q, 0, 0, a * rim(q, c), PLAIN);
					corner(b, s, 0, 0, a * rim(s, c), PLAIN);
					corner(b, u, 0, 0, a * rim(u, c), PLAIN);
				}
			for (int i = 0; i < RIBS; i++) {
				Vector3f[] rib = new Vector3f[UP + 1];
				for (int j = 0; j <= UP; j++) rib[j] = on(c, r, i * ROUND / RIBS, j / (float) UP);
				strip(b, rib, 0.05f, a * 0.8f, a * 0.5f);
			}
		}
	}

	/** Silk: strands from a caster to a bolt in flight, or wound round what it caught. */
	static final class Silk extends Fx {
		final Entity from, to;
		final float turns, phase, wide;
		Vec3 last;

		Silk(ClientLevel level, Entity from, Entity to, int rgb, float turns, float phase, float wide) {
			super(level, to.position(), rgb);
			this.from = from;
			this.to = to;
			this.turns = turns;
			this.phase = phase;
			this.wide = wide;
			lifetime = 70;
		}

		@Override
		public void tick() {
			xo = x;
			yo = y;
			zo = z;
			if (age++ >= lifetime) remove();
			if (to.isRemoved()) lifetime = Math.min(lifetime, age + 7);
			else last = to.position();
		}

		@Override
		public AABB getRenderBoundingBox(float partial) {
			return super.getRenderBoundingBox(partial).inflate(40);
		}

		@Override
		public void render(VertexConsumer b, Camera cam, float partial) {
			if (last == null) return;
			Vec3 c = cam.getPosition(), a = from.getEyePosition(partial).add(0, -0.4, 0).subtract(c), e = last.add(0, 0.2, 0).subtract(c);
			Vector3f[] pts = new Vector3f[33];
			Vec3 d = e.subtract(a);
			Vec3 s = d.cross(new Vec3(0, 1, 0)).normalize(), u = s.cross(d).normalize();
			float t = age + partial;
			for (int i = 0; i <= 32; i++) {
				float k = i / 32f, r = wide * Mth.sqrt(Mth.sin(Mth.PI * k)), w = phase + (k * turns + t * 0.03f) * Mth.TWO_PI;
				Vec3 p = a.add(d.scale(k)).add(s.scale(Mth.cos(w) * r)).add(u.scale(Mth.sin(w) * r));
				pts[i] = new Vector3f((float) p.x, (float) p.y, (float) p.z);
			}
			float fade = Math.min(1, (lifetime - t) / 7f);
			strip(b, pts, 0.03f, fade, fade);
			strip(b, pts, 0.11f, fade * 0.3f, fade * 0.3f);
		}
	}

	/** Rings of silk round someone, tightening. */
	static final class Bound extends Fx {
		final Entity on;

		Bound(ClientLevel level, Entity on, int rgb, int life) {
			super(level, on.position(), rgb);
			this.on = on;
			lifetime = life;
		}

		@Override
		public void tick() {
			xo = x;
			yo = y;
			zo = z;
			if (age++ >= lifetime || !on.isAlive()) remove();
			setPos(on.getX(), on.getY(), on.getZ());
		}

		@Override
		public void render(VertexConsumer b, Camera cam, float partial) {
			float t = age + partial, tight = 1 + 0.9f * Math.max(0, 1 - t / 6), a = Math.min(1, (lifetime - t) / 8f);
			Vector3f c = here(cam, partial);
			float h = on.getBbHeight(), w = on.getBbWidth() * 0.72f * tight;
			for (int i = 0; i < 9; i++) {
				float y = h * (i + 0.5f) / 9, ta = Mth.sin(i * 2.3f) * 0.34f, tb = Mth.cos(i * 1.7f) * 0.34f;
				Vector3f[] loop = new Vector3f[25];
				for (int j = 0; j <= 24; j++) {
					float an = j * Mth.TWO_PI / 24, cx = Mth.cos(an) * w, cz = Mth.sin(an) * w;
					loop[j] = new Vector3f(c).add(cx, y + cx * ta + cz * tb, cz);
				}
				strip(b, loop, 0.022f, a, a);
			}
		}
	}

	/** What the bolt itself looks like: stays on it for as long as it flies. */
	static final class Head extends Fx {
		final Spells.Bolt bolt;
		final SpellLook.Family family;

		Head(ClientLevel level, Spells.Bolt bolt, int rgb) {
			super(level, bolt.position(), rgb);
			this.bolt = bolt;
			family = SpellLook.of(bolt.gate());
			lifetime = 100;
		}

		@Override
		public void tick() {
			if (bolt.isRemoved() || age++ >= lifetime) remove();
		}

		@Override
		public void render(VertexConsumer b, Camera cam, float partial) {
			Vec3 cp = cam.getPosition(), at = bolt.getPosition(partial).add(0, 0.2, 0).subtract(cp), v = bolt.getDeltaMovement();
			Vector3f c = new Vector3f((float) at.x, (float) at.y, (float) at.z);
			Vector3f r = right(cam), u = up(cam);
			float k = ((age + partial) * 0.09f) % 0.4f + 0.08f;
			switch (family) {
				case SHARD -> {
					Vector3f ax = new Vector3f((float) v.x, (float) v.y, (float) v.z).normalize(1.6f);
					crystal(this, b, new Vector3f(c).sub(new Vector3f(ax).mul(0.75f)), ax, 0.17f, 1);
					frame(b, c, new Vector3f(r).mul(0.8f), new Vector3f(u).mul(0.8f), 0, GLOW, 0, 0.5f);
				}
				case LIQUID -> {
					Vector3f ax = new Vector3f((float) v.x, (float) v.y, (float) v.z).normalize(0.62f);
					Vector3f side = new Vector3f(ax).cross(c).normalize(0.34f);
					frame(b, c, side, ax, 0, DROP, 0, 1);
				}
				case VOID -> {
					frame(b, c, new Vector3f(r).mul(0.85f), new Vector3f(u).mul(0.85f), 0, HOLE, 0, 1);
					frame(b, c, new Vector3f(r).mul(1.1f), new Vector3f(u).mul(1.1f), 0, GLOW, 0, 0.45f);
				}
				case THREAD -> frame(b, c, new Vector3f(r).mul(0.5f), new Vector3f(u).mul(0.5f), 0, GLOW, 0, 1);
				default -> {
					float size = family == SpellLook.Family.LIGHTNING ? 0.7f : 0.85f;
					frame(b, c, new Vector3f(r).mul(size * 1.6f), new Vector3f(u).mul(size * 1.6f), 0, GLOW, 0, 0.5f);
					frame(b, c, new Vector3f(r).mul(size), new Vector3f(u).mul(size), BLAST, FIRE, k, 1);
				}
			}
		}
	}
}
