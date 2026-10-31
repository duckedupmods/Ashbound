package com.snoringwalrus.ashbound.client;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.List;

import org.joml.Vector3f;

import com.mojang.blaze3d.vertex.VertexConsumer;
import com.snoringwalrus.ashbound.Spells;
import com.snoringwalrus.ashbound.client.SpellParticles.Flip;
import com.snoringwalrus.ashbound.client.SpellParticles.Fx;

import net.minecraft.client.Camera;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.particle.TerrainParticle;
import net.minecraft.core.BlockPos;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import static com.snoringwalrus.ashbound.client.SpellFx.add;
import static com.snoringwalrus.ashbound.client.SpellFx.flip;
import static com.snoringwalrus.ashbound.client.SpellFx.floor;
import static com.snoringwalrus.ashbound.client.SpellFx.mix;
import static com.snoringwalrus.ashbound.client.SpellFx.pool;
import static com.snoringwalrus.ashbound.client.SpellFx.rand;
import static com.snoringwalrus.ashbound.client.SpellFx.sparks;
import static com.snoringwalrus.ashbound.client.SpellParticles.BLAST;
import static com.snoringwalrus.ashbound.client.SpellParticles.CRESCENT;
import static com.snoringwalrus.ashbound.client.SpellParticles.INK;
import static com.snoringwalrus.ashbound.client.SpellParticles.ROLL;
import static com.snoringwalrus.ashbound.client.SpellParticles.SHEET;
import static com.snoringwalrus.ashbound.client.SpellParticles.SMOKE;
import static com.snoringwalrus.ashbound.client.SpellParticles.STAR;
import static com.snoringwalrus.ashbound.client.SpellParticles.STREAK;

/**
 * The bigger pieces: decals on the ground, flares, tubes of energy, the healing beam, and the blows made of them. All the
 * fine detail is noise that scrolls and burns away in spell_fx.fsh (modes below); the shapes are simple on purpose, it's
 * how game effects get their look. tools/fxpreview/run.sh shows the shader's modes without the game.
 */
final class FxKit {
	private FxKit() {}

	static final int SLASH = 9, FLOW = 10, RING = 11, CRACK = 12, FLARE = 13, SWIRL = 14, ARC = 15, RUNE = 16, TUBE = 17;
	private static final int WHITE = 0xFFFFFF, DUST = 0x8A7A68, BLACK = 0, GREY = 0x3A3430;

	/** Something flat: a shockwave, cracks, a circle, a vortex; on the ground, or turned to the camera if it's asked. */
	static final class Decal extends Fx {
		final int mode;
		final float radius, peak;
		float hole = -1, spin;
		boolean faces, inward;
		Entity on;
		Vector3f crossU, crossV;

		Decal(ClientLevel level, Vec3 at, int rgb, int mode, float radius, int life, float peak) {
			super(level, at, rgb);
			this.mode = mode;
			this.radius = radius;
			this.peak = peak;
			lifetime = life;
		}

		/** Turned to the camera, with a hole in it for a vortex. */
		Decal facing(float hole) {
			this.hole = hole;
			faces = true;
			return this;
		}

		/** Flat across a line of flight: what something fast leaves in the air behind it. */
		Decal across(Vec3 dir) {
			Vector3f d = new Vector3f((float) dir.x, (float) dir.y, (float) dir.z).normalize();
			crossU = new Vector3f(d).cross(0.31f, 0.91f, 0.27f).normalize();
			crossV = new Vector3f(d).cross(crossU).normalize();
			return this;
		}

		/** Runs backwards: a ring closing on its middle, for something gathering. */
		Decal inward() {
			inward = true;
			return this;
		}

		Decal spun(float s) {
			spin = s;
			return this;
		}

		Decal follows(Entity e) {
			on = e;
			return this;
		}

		@Override
		public void tick() {
			xo = x;
			yo = y;
			zo = z;
			if (age++ >= lifetime) remove();
			if (on != null) setPos(on.getX(), on.getY() + (faces ? on.getBbHeight() : 0.05), on.getZ());
		}

		@Override
		public AABB getRenderBoundingBox(float partial) {
			return super.getRenderBoundingBox(partial).inflate(radius);
		}

		@Override
		public void render(VertexConsumer b, Camera cam, float partial) {
			float t = age + partial, k = Math.min(1, t / lifetime), s = radius * (mode == SWIRL ? 1 - (1 - Math.min(1, t / 8)) * (1 - Math.min(1, t / 8)) : 1);
			param = param(hole >= 0 ? hole : inward ? 1 - k : k);
			float a = peak * (mode == RING || mode == CRACK ? 1 : Math.min(1, t / 3) * Math.min(1, (1 - k) * 4));
			Vector3f c = here(cam, partial);
			if (faces) quad(b, c, SpellParticles.right(cam).mul(s), SpellParticles.up(cam).mul(s), -1, 1, 1, -1, a, mode);
			else if (crossU != null) quad(b, c, new Vector3f(crossU).mul(s), new Vector3f(crossV).mul(s), -1, 1, 1, -1, a, mode);
			else {
				float an = spin * t;
				quad(b, c, new Vector3f(Mth.cos(an) * s, 0, Mth.sin(an) * s), new Vector3f(-Mth.sin(an) * s, 0, Mth.cos(an) * s), -1, 1, 1, -1, a, mode);
			}
		}
	}

	/** A hot star: it arrives at once and only then starts going. */
	static final class Flare extends Fx {
		final float radius, peak;
		final float roll = random.nextFloat() * Mth.TWO_PI * 0.2f;

		Flare(ClientLevel level, Vec3 at, int rgb, float radius, int life, float peak) {
			super(level, at, rgb);
			this.radius = radius;
			this.peak = peak;
			lifetime = life;
			friction = 0;
		}

		@Override
		public void render(VertexConsumer b, Camera cam, float partial) {
			float k = Math.min(1, (age + partial) / lifetime), s = radius * (0.65f + 0.35f * Math.min(1, k * 5)) * (1 - k * 0.3f), a = peak * (1 - k) * (1 - k);
			param = param(k);
			Vector3f r = SpellParticles.right(cam), u = SpellParticles.up(cam), c = here(cam, partial);
			float co = Mth.cos(roll), si = Mth.sin(roll);
			Vector3f side = new Vector3f(r).mul(co * s).add(new Vector3f(u).mul(si * s)), up = new Vector3f(u).mul(co * s).sub(new Vector3f(r).mul(si * s));
			quad(b, c, side, up, -1, 1, 1, -1, a, FLARE);
		}
	}

	/** One sprite that snaps to size and goes: a flash's star, a crescent thrown off a blow. Black colour makes its black twin. */
	static final class Pop extends Fx {
		final int mode;
		final float s0, s1, roll, spin;

		Pop(ClientLevel level, Vec3 at, int rgb, int mode, float s0, float s1, int life, float roll, float spin) {
			super(level, at, rgb);
			this.mode = mode;
			this.s0 = s0;
			this.s1 = s1;
			this.roll = roll;
			this.spin = spin;
			lifetime = life;
			friction = 0;
		}

		@Override
		public void render(VertexConsumer b, Camera cam, float partial) {
			float k = Math.min(1, (age + partial) / lifetime), out = 1 - (1 - k) * (1 - k) * (1 - k), s = Mth.lerp(out, s0, s1), an = roll + spin * out;
			param = param(k);
			float co = Mth.cos(an) * s, si = Mth.sin(an) * s;
			Vector3f r = SpellParticles.right(cam), u = SpellParticles.up(cam);
			quad(b, here(cam, partial), new Vector3f(r).mul(co).add(new Vector3f(u).mul(si)), new Vector3f(u).mul(co).sub(new Vector3f(r).mul(si)), -1, 1, 1, -1, 1, mode);
		}
	}

	/** Nothing to see: what's to happen a few ticks from now, so that the parts of a blow don't all land at once. */
	private static final class Later extends Fx {
		final Runnable run;

		Later(ClientLevel level, int ticks, Runnable run) {
			super(level, Vec3.ZERO, 0);
			this.run = run;
			lifetime = ticks;
		}

		@Override
		public void tick() {
			if (age++ < lifetime) return;
			remove();
			run.run();
		}

		@Override
		public void render(VertexConsumer b, Camera cam, float partial) {}
	}

	/** A bolt's tail: where it's been, as a soft ribbon, a sharp one and a thread, all narrowing away; it pulls in when the bolt's gone. */
	static final class Comet extends Fx {
		private static final int LONG = 16, MOST = 400;
		private static final float SOFT = 0.34f, SHARP = 0.12f, THREAD = 0.025f, CURL = 0.75f;
		final Spells.Bolt bolt;
		final ArrayDeque<Vec3> path = new ArrayDeque<>();
		final int mode, pale;
		final boolean curls;

		Comet(ClientLevel level, Spells.Bolt bolt, int rgb, int mode, boolean curls) {
			super(level, bolt.position(), rgb);
			this.bolt = bolt;
			this.mode = mode;
			this.curls = curls;
			pale = mix(rgb, WHITE, 0.65f);
		}

		@Override
		public void tick() {
			xo = x;
			yo = y;
			zo = z;
			if (age++ >= MOST) remove();
			if (!bolt.isRemoved()) {
				Vec3 at = bolt.position().add(0, 0.2, 0);
				setPos(at.x, at.y, at.z);
				path.addFirst(at);
				if (path.size() > LONG) path.removeLast();
				return;
			}
			path.pollLast();
			path.pollLast();
			if (path.isEmpty()) remove();
		}

		private void tint(int rgb) {
			rCol = (rgb >> 16 & 255) / 255f;
			gCol = (rgb >> 8 & 255) / 255f;
			bCol = (rgb & 255) / 255f;
		}

		@Override
		public void render(VertexConsumer b, Camera cam, float partial) {
			if (path.size() < 2) return;
			float rr = rCol, gg = gCol, bb = bCol, t = age + partial;
			Vec3 c = cam.getPosition();
			int rgb = (int) (rr * 255) << 16 | (int) (gg * 255) << 8 | (int) (bb * 255);
			param = param(0);
			for (int turn = 0; turn < (curls ? 3 : 1); turn++) {
				Vector3f[] pts = new Vector3f[path.size()];
				int i = 0;
				for (Vec3 p : path) {
					float k = i / (float) LONG, an = turn * Mth.TWO_PI / 3 + i * CURL - t * 0.5f, off = curls ? 0.04f + k * 0.5f : 0;
					pts[i++] = new Vector3f((float) (p.x - c.x), (float) (p.y - c.y + Mth.sin(an) * off), (float) (p.z - c.z + Mth.cos(an) * off));
				}
				tint(rgb);
				blade(b, pts, curls ? SOFT * 0.5f : SOFT, 0, 0.75f, 0, mode);
				blade(b, pts, SHARP, 0, 1, 0, mode);
				tint(pale);
				blade(b, pts, THREAD * 2, 0, 1, 0, SpellParticles.STREAK);
			}
			tint(rgb);
		}
	}

	/** One skin of liquid thrown up and open like a flower, its lip torn into peaks; it falls and tears away. */
	static final class Crown extends Fx {
		private static final int ROUND = 48, UP = 5, PEAKS = 7;
		final float r0, r1, high, peak;
		final float[] lip = new float[ROUND + 1];

		Crown(ClientLevel level, Vec3 at, int rgb, float r0, float r1, float high, int life, float peak) {
			super(level, at, rgb);
			this.r0 = r0;
			this.r1 = r1;
			this.high = high;
			this.peak = peak;
			lifetime = life;
			friction = 0;
			RandomSource r = level.getRandom();
			for (int p = 0; p < PEAKS; p++) {
				int n = 5 + r.nextInt(9);
				float ph = r.nextFloat() * Mth.TWO_PI, w = 0.3f + r.nextFloat() * 0.7f;
				for (int i = 0; i <= ROUND; i++) {
					float sw = Math.max(0, Mth.sin(i * Mth.TWO_PI / ROUND * n + ph));
					lip[i] += w * sw * sw * sw * sw * sw * 0.5f;
				}
			}
			for (int i = 0; i <= ROUND; i++) lip[i] += 0.5f;
		}

		@Override
		public AABB getRenderBoundingBox(float partial) {
			return super.getRenderBoundingBox(partial).inflate(r1 + high);
		}

		private void put(VertexConsumer b, Vector3f c, int i, int j, float open, float fall) {
			float t = j / (float) UP, a = i * Mth.TWO_PI / ROUND, r = r0 + (r1 - r0) * open * (float) Math.pow(t, 1.7f);
			float h = high * lip[i] * open * fall * (t - 0.28f * t * t);
			corner(b, new Vector3f(c).add(Mth.cos(a) * r, h, Mth.sin(a) * r), i * 2f / ROUND - 1, t, peak, SHEET);
		}

		@Override
		public void render(VertexConsumer b, Camera cam, float partial) {
			float k = Math.min(1, (age + partial) / lifetime), q = 1 - Math.min(1, k * 1.7f), open = 1 - q * q * q, fall = 1 - 0.45f * k * k;
			param = param(k);
			Vector3f c = here(cam, partial);
			for (int i = 0; i < ROUND; i++)
				for (int j = 0; j < UP; j++) {
					put(b, c, i, j, open, fall);
					put(b, c, i + 1, j, open, fall);
					put(b, c, i + 1, j + 1, open, fall);
					put(b, c, i, j + 1, open, fall);
				}
		}
	}

	/** A tube of energy going up an axis, twisting as it goes; or, spreading, a wall of it running out over the ground. */
	static final class Tube extends Fx {
		private static final int ROUND = 18, UP = 12;
		final Vector3f axis, u, v;
		final float length, r0, r1, twist, peak;
		boolean spreads;
		Entity on;

		Tube(ClientLevel level, Vec3 at, Vec3 axis, int rgb, float length, float r0, float r1, float twist, int life, float peak) {
			super(level, at, rgb);
			this.axis = new Vector3f((float) axis.x, (float) axis.y, (float) axis.z).normalize();
			u = new Vector3f(this.axis).cross(0.31f, 0.91f, 0.27f).normalize();
			v = new Vector3f(this.axis).cross(u).normalize();
			this.length = length;
			this.r0 = r0;
			this.r1 = r1;
			this.twist = twist;
			this.peak = peak;
			lifetime = life;
		}

		Tube spreading() {
			spreads = true;
			return this;
		}

		Tube follows(Entity e) {
			on = e;
			return this;
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
			return super.getRenderBoundingBox(partial).inflate(length + Math.max(r0, r1));
		}

		private void put(VertexConsumer b, Vector3f c, float round, float along, float len, float rad, float a, float t) {
			float an = round * Mth.TWO_PI + twist * along + t * 0.14f;
			Vector3f n = new Vector3f(u).mul(Mth.cos(an)).add(new Vector3f(v).mul(Mth.sin(an)));
			Vector3f p = new Vector3f(c).add(new Vector3f(axis).mul(len * along)).add(new Vector3f(n).mul(rad));
			float face = Math.abs(n.dot(new Vector3f(p).normalize()));
			float ends = Math.min(1, along * 7) * Math.min(1, (1 - along) * 2.5f);
			corner(b, p, round * 2 - 1, along * len, a * ends * (0.2f + 0.8f * face), TUBE);
		}

		@Override
		public void render(VertexConsumer b, Camera cam, float partial) {
			float t = age + partial, k = Math.min(1, t / lifetime), grow = 1 - (1 - Math.min(1, k * 3)) * (1 - Math.min(1, k * 3));
			float len = spreads ? length * (1 - k * 0.7f) : length * grow, a = peak * Math.min(1, t / 2) * Math.min(1, (1 - k) * 3);
			param = param(k * k);
			Vector3f c = here(cam, partial);
			for (int i = 0; i < ROUND; i++)
				for (int j = 0; j < UP; j++) {
					float i0 = i / (float) ROUND, i1 = (i + 1) / (float) ROUND, j0 = j / (float) UP, j1 = (j + 1) / (float) UP;
					float w0 = spreads ? Mth.lerp(1 - (1 - k) * (1 - k), r0, r1) : Mth.lerp(j0, r0, r1), w1 = spreads ? w0 : Mth.lerp(j1, r0, r1);
					put(b, c, i0, j0, len, w0, a, t);
					put(b, c, i1, j0, len, w0, a, t);
					put(b, c, i1, j1, len, w1, a, t);
					put(b, c, i0, j1, len, w1, a, t);
				}
		}
	}

	/** The healer's line to one ally: it leaves the staff, bends with the way they're looking, and pours into the other's chest. */
	static final class HealBeam extends Fx {
		private static final int POINTS = 22, SPARKS = 3;
		private static final float BEND = 0.28f, DRIFT = 0.16f, WIDE = 0.34f, BODY = 0.13f, THREAD = 0.03f, TWIST = 11;
		private static final List<HealBeam> LIVE = new ArrayList<>();
		final Entity from, to;
		final int rgb;

		HealBeam(ClientLevel level, Entity from, Entity to, int rgb, int ticks) {
			super(level, to.position(), rgb);
			this.from = from;
			this.to = to;
			this.rgb = rgb;
			lifetime = ticks;
			LIVE.add(this);
		}

		/** Their line's been cut: out of reach, or behind a wall. */
		static void cut(int from, int to) {
			for (HealBeam h : LIVE) if (h.from.getId() == from && h.to.getId() == to) h.lifetime = Math.min(h.lifetime, h.age + 6);
		}

		@Override
		public void tick() {
			xo = x;
			yo = y;
			zo = z;
			if (age++ >= lifetime || from.isRemoved() || to.isRemoved()) {
				LIVE.remove(this);
				remove();
				return;
			}
			setPos(to.getX(), to.getY(), to.getZ());
			RandomSource r = level.getRandom();
			int c = mix(rgb, WHITE, 0.5f);
			if (age % 2 == 0) {
				double a = r.nextDouble() * Mth.TWO_PI;
				level.addParticle(com.snoringwalrus.ashbound.Vfx.mote(c, 0.03f, 20, -0.04f), true, x + Math.cos(a) * 0.5, y + r.nextDouble() * 1.4, z + Math.sin(a) * 0.5, 0, 0.05, 0);
			}
			if (age % 6 == 0) add(new Decal(level, floor(level, to.position()), c, RING, 1.5f, 14, 0.7f));
			if (age % 8 == 0) halo(level, to.position(), c, to.getBbWidth() + 0.7f, to.getBbHeight() * 1.1f, 3);
			if (age % 3 == 0) rising(level, to.position(), c, 0.7f, 2, 14);
		}

		@Override
		public AABB getRenderBoundingBox(float partial) {
			return new AABB(from.position(), to.position()).inflate(4);
		}

		@Override
		public void render(VertexConsumer b, Camera cam, float partial) {
			Vec3 at = cam.getPosition(), a = SpellFx.tip(from, partial).subtract(at), e = to.getPosition(partial).add(0, to.getBbHeight() * 0.55, 0).subtract(at);
			float t = age + partial, dist = (float) a.distanceTo(e), fade = Math.min(1, t / 3) * Math.min(1, (lifetime - t) / 6);
			Vec3 m = a.add(e).scale(0.5).add(from.getViewVector(partial).scale(dist * BEND)).add(0, Mth.sin(t * 0.13f) * DRIFT, 0);
			Vector3f[] line = new Vector3f[POINTS + 1], one = new Vector3f[POINTS + 1], two = new Vector3f[POINTS + 1];
			for (int i = 0; i <= POINTS; i++) {
				float s = i / (float) POINTS, q = 1 - s;
				Vec3 p = a.scale(q * q).add(m.scale(2 * q * s)).add(e.scale(s * s));
				line[i] = new Vector3f((float) p.x, (float) p.y, (float) p.z);
			}
			for (int i = 0; i <= POINTS; i++) {
				Vector3f d = new Vector3f(line[Math.min(POINTS, i + 1)]).sub(line[Math.max(0, i - 1)]);
				Vector3f side = d.cross(line[i]);
				if (side.lengthSquared() < 1e-8f) side.set(0, 1, 0);
				side.normalize();
				float s = i / (float) POINTS, w = Mth.sin(s * TWIST - t * 0.55f) * 0.11f * Mth.sin(s * Mth.PI);
				one[i] = new Vector3f(line[i]).add(new Vector3f(side).mul(w));
				two[i] = new Vector3f(line[i]).sub(new Vector3f(side).mul(w));
			}
			param = param(0);
			ribbon(b, line, WIDE, fade * 0.42f, fade * 0.5f, FLOW);
			ribbon(b, line, BODY, fade, fade, FLOW);
			strip(b, one, THREAD, fade, fade);
			strip(b, two, THREAD, fade, fade);
			Vector3f r = SpellParticles.right(cam), u = SpellParticles.up(cam);
			float pulse = 1 + 0.15f * Mth.sin(t * 0.6f);
			param = param(0.5f);
			quad(b, line[POINTS], new Vector3f(r).mul(1.1f * pulse), new Vector3f(u).mul(1.1f * pulse), -1, 1, 1, -1, fade, FLARE);
			quad(b, line[0], new Vector3f(r).mul(0.55f), new Vector3f(u).mul(0.55f), -1, 1, 1, -1, fade * 0.8f, FLARE);
			for (int i = 0; i < SPARKS; i++) {   // needles of it running down the line
				int at1 = Math.round(((t * 0.055f + i / (float) SPARKS) % 1) * (POINTS - 3));
				Vector3f[] run = {line[at1], line[at1 + 1], line[at1 + 2], line[at1 + 3]};
				strip(b, run, 0.06f, 0, fade);
			}
		}
	}

	/** A falling star: down from the sky to where it's aimed, shedding flame. */
	static final class Meteor extends Flip {
		final int rgb;

		Meteor(ClientLevel level, Vec3 to, int rgb, int ticks) {
			super(level, to.add(9, 34, 5), new Vec3(-9, -34, -5).scale(1.0 / ticks), rgb, SpellParticles.BLAST, SpellParticles.FIRE, 2.4f, 2.4f, ticks, 1);
			this.rgb = rgb;
			friction = 1;
			lifetime = ticks;
			stretched(1.6f);
		}

		@Override
		public void tick() {
			super.tick();
			Vec3 at = new Vec3(x, y, z), v = new Vec3(xd, yd, zd);
			for (int i = 0; i < 4; i++) flip(level(), SpellParticles.FLAME, SpellParticles.FIRE, rgb, at.subtract(v.scale(i * 0.3)).add(rand(random(), 0).scale(0.5)), v.scale(0.2), 1.3f, 0.5f, 12).stretched(1.8f);
			flip(level(), ROLL, SMOKE, 0x2A2420, at.subtract(v.scale(0.6)), new Vec3(0, 0.03, 0), 1.2f, 2.8f, 30);
		}

		private ClientLevel level() {
			return (ClientLevel) level;
		}

		private RandomSource random() {
			return level.getRandom();
		}
	}

	// ---------------------------------------------------------------- put together

	static void later(ClientLevel l, int ticks, Runnable run) {
		add(new Later(l, ticks, run));
	}

	/** Needles of light (or black) that shoot out and stop. */
	static void streaks(ClientLevel l, Vec3 at, int rgb, int n, double speed, float wide, float length, int life, double up) {
		RandomSource r = l.getRandom();
		for (int i = 0; i < n; i++) {
			Vec3 d = rand(r, up);
			flip(l, 0, STREAK, rgb, at.add(d.scale(0.2)), d.scale(speed * (0.4 + r.nextDouble())), wide, wide * 0.4f, life + r.nextInt(5)).stretched(length).drag(STOPS);
		}
	}

	private static final float STOPS = 0.74f;

	/**
	 * Every blow the same way, because it's how a hit reads. The flash first, the biggest thing there is and gone in three
	 * ticks. Then, a tick later and each a step after the last, a colour star on a black one, a black mass behind it all for
	 * the bright parts to read against, crescents, needles and a ring; then smoke and embers. Only the mass goes on growing,
	 * the brightness only falls. reach is about how far it goes, in blocks.
	 */
	static void impact(ClientLevel l, Vec3 at, int rgb, float reach) {
		RandomSource r = l.getRandom();
		float roll = r.nextFloat() * Mth.TWO_PI;
		add(new Flare(l, at, rgb, reach * 4.2f, 5, 1));
		add(new Pop(l, at, rgb, STAR, reach * 2.8f, reach * 1.7f, 3, roll, 0));
		later(l, 1, () -> {
			flip(l, BLAST, INK, rgb, at, Vec3.ZERO, reach * 1.3f, reach * 2.7f, 12);
			add(new Pop(l, at, BLACK, STAR, reach * 1.9f, reach * 2.4f, 4, roll + 0.4f, 0));
			add(new Pop(l, at, rgb, STAR, reach * 1.4f, reach * 2.1f, 4, roll + 0.4f, 0));
			for (int i = 0; i < 3; i++) {
				float a = roll + i * 2.1f + r.nextFloat() * 0.5f;
				add(new Pop(l, at, BLACK, CRESCENT, reach * 1.25f, reach * 3.1f, 8, a, 0.5f));
				add(new Pop(l, at, mix(rgb, WHITE, 0.25f), CRESCENT, reach * 1.1f, reach * 2.9f, 8, a, 0.5f));
			}
			streaks(l, at, BLACK, 5, 0.9 * reach, 0.09f * reach, 5, 7, 0.3);
			streaks(l, at, mix(rgb, WHITE, 0.4f), 14, 1.1 * reach, 0.07f * reach, 6, 7, 0.3);
			add(new Decal(l, at, mix(rgb, WHITE, 0.6f), RING, reach * 3.4f, 10, 1).facing(-1));
		});
		later(l, 2, () -> {
			for (int i = 0; i < 6; i++) {
				Vec3 d = rand(r, 0.7);
				flip(l, ROLL, SMOKE, i % 2 == 0 ? mix(rgb, GREY, 0.75f) : GREY, at.add(d.scale(0.3 * reach)), d.scale(0.4 * reach), 0.6f * reach, 1.5f * reach, 26).drag(0.8f);
			}
			sparks(l, at, mix(rgb, WHITE, 0.3f), (int) (10 + reach * 10), 0.3 * reach, 0.05f);
		});
	}

	/** The wind-up: needles of light pulled in to a point from all round, a glow swelling on it, a ring closing. */
	static void gather(ClientLevel l, Vec3 at, int rgb, float reach, int ticks) {
		RandomSource r = l.getRandom();
		int pale = mix(rgb, WHITE, 0.5f);
		for (int i = 0, n = (int) (14 + reach * 5); i < n; i++) {
			Vec3 d = rand(r, 0);
			double from = reach * (0.8 + r.nextDouble() * 0.6);
			int life = Math.max(3, (int) (ticks * (0.55f + r.nextFloat() * 0.45f)));
			flip(l, 0, STREAK, pale, at.add(d.scale(from)), d.scale(-from / life), 0.08f, 0.03f, life).stretched(5).drag(1);
		}
		flip(l, 0, SpellParticles.GLOW, rgb, at, Vec3.ZERO, 0.3f, reach * 0.9f, ticks + 2);
		add(new Decal(l, at, pale, RING, reach * 1.6f, ticks, 1).facing(-1).inward());
		later(l, ticks, () -> add(new Pop(l, at, mix(rgb, WHITE, 0.3f), STAR, reach * 0.8f, reach * 0.3f, 2, r.nextFloat() * Mth.TWO_PI, 0)));
	}

	/** A cut: black behind, the colour on it, a thin white edge; drawn over a few ticks, and it throws needles off its head as it goes. */
	static void slash(ClientLevel l, Vec3 at, Vec3 u, Vec3 v, int rgb, float radius, float width, float from, float to, int life) {
		add(new SpellParticles.Arc(l, at, u, v, BLACK, radius + width * 0.1f, width * 1.35f, from, to, life + 2));
		add(new SpellParticles.Arc(l, at, u, v, rgb, radius, width, from, to, life));
		add(new SpellParticles.Arc(l, at, u, v, WHITE, radius - width * 0.1f, width * 0.24f, from, to, life - 2));
		Vec3 pu = u.normalize(), pv = v.normalize();
		int pale = mix(rgb, WHITE, 0.5f);
		for (int i = 0; i < 4; i++) {
			float k = 1 - (1 - (i + 1) / 4f) * (1 - (i + 1) / 4f), an = from + (to - from) * k, sign = Math.signum(to - from);
			Vec3 tip = at.add(pu.scale(Mth.cos(an) * radius)).add(pv.scale(Mth.sin(an) * radius));
			Vec3 ahead = pv.scale(Mth.cos(an) * sign).subtract(pu.scale(Mth.sin(an) * sign));
			later(l, i, () -> {
				RandomSource r = l.getRandom();
				for (int n = 0; n < 3; n++) flip(l, 0, STREAK, pale, tip, ahead.scale(0.5 + r.nextDouble() * 0.7).add(rand(r, 0).scale(0.15)), 0.07f, 0.03f, 6 + r.nextInt(4)).stretched(5).drag(STOPS);
			});
		}
		later(l, Math.max(1, life / 3), () -> {
			Vec3 end = at.add(pu.scale(Mth.cos(to) * radius)).add(pv.scale(Mth.sin(to) * radius));
			add(new Pop(l, end, mix(rgb, WHITE, 0.3f), STAR, width * 1.3f, width * 0.6f, 3, l.getRandom().nextFloat() * Mth.TWO_PI, 0));
		});
	}

	/** Thrown liquid or blood: needles that fly, drop and go, with a few black ones so it isn't all light. Never round beads. */
	static void spray(ClientLevel l, Vec3 at, int rgb, int n, double speed) {
		RandomSource r = l.getRandom();
		for (int i = 0; i < n; i++) {
			Vec3 d = rand(r, 0.8).scale(speed * (0.3 + r.nextDouble()));
			flip(l, 0, STREAK, i % 3 == 0 ? BLACK : rgb, at, d, 0.07f + r.nextFloat() * 0.05f, 0.02f, 12 + r.nextInt(8)).stretched(4).drag(0.93f).falls(0.7f);
		}
	}

	/** A black mass with the colour on its edge, rolling. What dark energy is made of. */
	static void ink(ClientLevel l, Vec3 at, int rgb, int n, float spread, float size, int life) {
		RandomSource r = l.getRandom();
		for (int i = 0; i < n; i++) {
			Vec3 d = rand(r, 0.5);
			flip(l, ROLL, INK, rgb, at.add(d.scale(spread)), d.scale(0.03).add(0, 0.02, 0), size * 0.6f, size * 1.4f, life + r.nextInt(10));
		}
	}

	/** What's left along a line something went down: rings of wind standing across it, one after another. */
	static void wake(ClientLevel l, Vec3 from, Vec3 dir, int rgb, float length, float wide, int n) {
		Vec3 d = dir.normalize();
		for (int i = 0; i < n; i++) {
			Vec3 at = from.add(d.scale(length * (i + 0.5f) / n));
			float size = wide * (1.5f + i * 0.5f / n);
			later(l, i, () -> add(new Decal(l, at, rgb, RING, size, 9, 0.85f).across(d)));
		}
	}

	/** A halo climbing someone: rings across their body, going up. */
	static void halo(ClientLevel l, Vec3 feet, int rgb, float wide, float tall, int n) {
		Vec3 up = new Vec3(0, 1, 0);
		for (int i = 0; i < n; i++) {
			Vec3 at = feet.add(0, tall * (i + 0.5f) / n, 0);
			later(l, i * 2, () -> add(new Decal(l, at, rgb, RING, wide, 11, 0.9f).across(up)));
		}
	}

	/** Needles of light going straight up off the ground, over a patch of it; what a heal looks like from outside. */
	static void rising(ClientLevel l, Vec3 at, int rgb, float reach, int n, int life) {
		RandomSource r = l.getRandom();
		Vec3 f = floor(l, at);
		for (int i = 0; i < n; i++) {
			double a = r.nextDouble() * Mth.TWO_PI, d = Math.sqrt(r.nextDouble()) * reach;
			flip(l, 0, STREAK, rgb, f.add(Math.cos(a) * d, r.nextDouble() * 0.8, Math.sin(a) * d), new Vec3(0, 0.1 + r.nextDouble() * 0.12, 0), 0.05f, 0.02f, life + r.nextInt(10)).stretched(6).drag(0.98f);
		}
	}

	static void flare(ClientLevel l, Vec3 at, int rgb, float size, int life) {
		add(new Flare(l, at, rgb, size, life, 1));
	}

	static void ring(ClientLevel l, Vec3 at, int rgb, float radius, int life) {
		add(new Decal(l, floor(l, at), rgb, RING, radius, life, 1));
	}

	static void rune(ClientLevel l, Vec3 at, int rgb, float radius, int life) {
		add(new Decal(l, floor(l, at).add(0, 0.02, 0), rgb, RUNE, radius, life, 1));
		pool(l, at, rgb, radius * 1.1f, life, 0.3f);
	}

	static void cracks(ClientLevel l, Vec3 at, int rgb, float radius, int life) {
		add(new Decal(l, floor(l, at).add(0, 0.01, 0), rgb, CRACK, radius, life, 1));
	}

	/** Bits of the ground that's actually there, thrown up. */
	static void rocks(ClientLevel l, Vec3 at, int n, double speed) {
		BlockPos under = BlockPos.containing(at.x, floor(l, at).y - 0.6, at.z);
		BlockState s = l.getBlockState(under);
		if (s.isAir()) return;
		RandomSource r = l.getRandom();
		Vec3 f = floor(l, at);
		for (int i = 0; i < n; i++) {
			Vec3 d = rand(r, 1.4).scale(speed * (0.4 + r.nextDouble()));
			TerrainParticle p = new TerrainParticle(l, f.x + d.x, f.y, f.z + d.z, 0, 0, 0, s, under);
			p.setParticleSpeed(d.x, Math.abs(d.y) + 0.12, d.z);
			p.scale(1.5f + r.nextFloat() * 2.5f);
			add(p);
		}
	}

	/** Dust rolling out along the ground. */
	static void dust(ClientLevel l, Vec3 at, float radius, int n) {
		Vec3 f = floor(l, at);
		for (int i = 0; i < n; i++) {
			double a = i * Mth.TWO_PI / n + l.getRandom().nextDouble() * 0.3;
			Vec3 out = new Vec3(Math.cos(a), 0, Math.sin(a));
			flip(l, ROLL, SMOKE, DUST, f.add(out.scale(radius * 0.25)).add(0, 0.3, 0), out.scale(radius * 0.05).add(0, 0.01, 0), radius * 0.2f + 0.5f, radius * 0.3f + 1.2f, 22 + l.getRandom().nextInt(10));
		}
	}

	/** Something very heavy just landed here. */
	static void slam(ClientLevel l, Vec3 at, int rgb, float radius, float heavy) {
		Vec3 f = floor(l, at);
		impact(l, f.add(0, 0.6, 0), rgb, 0.5f + radius * 0.25f);
		cracks(l, at, rgb, radius * 1.2f, 80 + (int) (heavy * 40));
		ring(l, at, mix(rgb, WHITE, 0.6f), radius * 1.3f, 14);
		ring(l, at, rgb, radius, 22);
		add(new Tube(l, f, new Vec3(0, 1, 0), rgb, 1 + heavy, 0.6f, radius, 0, 14, 1).spreading());
		flare(l, f.add(0, 0.5, 0), rgb, radius * 0.9f, 9);
		pool(l, at, rgb, radius * 1.3f, 20, 0.8f);
		rocks(l, at, (int) (10 + radius * 5), 0.3 + heavy * 0.18);
		dust(l, at, radius, 12 + (int) (radius * 2));
		sparks(l, f.add(0, 0.4, 0), rgb, (int) (24 + radius * 6), 0.5 + heavy * 0.2, 0.05f);
		streaks(l, f.add(0, 0.3, 0), mix(rgb, WHITE, 0.4f), (int) (10 + radius * 3), 0.7 + heavy * 0.3, 0.07f, 7, 9, 2.6);
		streaks(l, f.add(0, 0.3, 0), BLACK, (int) (4 + radius), 0.6 + heavy * 0.3, 0.1f, 6, 9, 2.6);
		later(l, 4, () -> ring(l, at, rgb, radius * 0.7f, 18));
	}

	/** A column of it going up to the sky. */
	static void column(ClientLevel l, Vec3 at, int rgb, float tall, float wide, int life, Entity on) {
		Vec3 up = new Vec3(0, 1, 0);
		Tube a = new Tube(l, at, up, rgb, tall, wide, wide * 0.7f, 2.5f, life, 1), b = new Tube(l, at, up, mix(rgb, WHITE, 0.4f), tall * 0.85f, wide * 0.5f, wide * 0.3f, -3.5f, life - 4, 1);
		if (on != null) {
			a.follows(on);
			b.follows(on);
		}
		add(a);
		add(b);
		add(new SpellParticles.Beam(l, at, up.scale(tall), mix(rgb, WHITE, 0.75f), wide * 0.4f, life, 1, on, 0.3f));
		flare(l, at.add(0, 0.4, 0), rgb, wide * 2.4f, life / 2);
		wake(l, at.add(0, tall * 0.1f, 0), up, mix(rgb, WHITE, 0.5f), tall * 0.7f, wide * 1.3f, 4);
		streaks(l, at.add(0, 0.4, 0), mix(rgb, WHITE, 0.4f), 12, 0.9, 0.06f, 7, 9, 3);
	}

	/** A spear of energy along a line, with a cone of it round the middle. */
	static void lance(ClientLevel l, Vec3 from, Vec3 dir, int rgb, float length, float wide, int life) {
		add(new SpellParticles.Beam(l, from, dir.scale(length), BLACK, wide * 1.3f, life, 0.7f, null, 0.4f));
		add(new Tube(l, from, dir, rgb, length, wide * 0.7f, wide * 1.2f, 3, life, 0.9f));
		add(new SpellParticles.Beam(l, from, dir.scale(length), rgb, wide, life, 0.8f, null, 0.5f));
		add(new SpellParticles.Beam(l, from, dir.scale(length), mix(rgb, WHITE, 0.8f), wide * 0.35f, life - 2, 1, null, 0.6f));
		flare(l, from, rgb, wide * 3, 8);
		wake(l, from, dir, mix(rgb, WHITE, 0.5f), length, wide * 1.4f, 4);
		Vec3 end = from.add(dir.normalize().scale(length));
		later(l, 3, () -> {
			add(new Pop(l, end, mix(rgb, WHITE, 0.3f), STAR, wide * 2.6f, wide * 1.2f, 3, l.getRandom().nextFloat() * Mth.TWO_PI, 0));
			streaks(l, end, mix(rgb, WHITE, 0.4f), 8, 0.7, 0.05f, 6, 7, 0);
		});
	}
}
