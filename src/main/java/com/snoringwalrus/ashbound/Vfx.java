package com.snoringwalrus.ashbound;

import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import io.netty.buffer.ByteBuf;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleType;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.registries.DeferredHolder;

/**
 * The curios' and relics' effects (CurioFx), drawn with the gate's soft shader particles (client/CurioParticles):
 * wisps (soft puffs that swell and fade, lit by the world or glowing) and motes (hot streaks along their flight, cooling
 * from white to their colour). Each effect is built from a few shapes here: a burst, wisps round a body, a ring, an
 * implosion, an arc between two points, drips.
 */
public final class Vfx {
	private Vfx() {}

	public static final int GLOW = 1, STREAK = 2, RING = 4, BOLT = 8;

	/** one particle: its colour, size (blocks), life (ticks), gravity (negative rises) and flags */
	public record Opt(int rgb, float size, int life, float gravity, int flags) implements ParticleOptions {
		@Override
		public ParticleType<?> getType() {
			return TYPE.get();
		}

		public boolean glow() {
			return (flags & GLOW) != 0;
		}

		public boolean streak() {
			return (flags & STREAK) != 0;
		}

		public boolean ring() {
			return (flags & RING) != 0;
		}

		public boolean bolt() {
			return (flags & BOLT) != 0;
		}
	}

	private static final MapCodec<Opt> CODEC = RecordCodecBuilder.mapCodec(i -> i.group(
			Codec.INT.fieldOf("rgb").forGetter(Opt::rgb), Codec.FLOAT.fieldOf("size").forGetter(Opt::size),
			Codec.INT.fieldOf("life").forGetter(Opt::life), Codec.FLOAT.fieldOf("gravity").forGetter(Opt::gravity),
			Codec.INT.fieldOf("flags").forGetter(Opt::flags)).apply(i, Opt::new));
	private static final StreamCodec<ByteBuf, Opt> STREAM = StreamCodec.composite(ByteBufCodecs.INT, Opt::rgb, ByteBufCodecs.FLOAT, Opt::size,
			ByteBufCodecs.VAR_INT, Opt::life, ByteBufCodecs.FLOAT, Opt::gravity, ByteBufCodecs.VAR_INT, Opt::flags, Opt::new);

	/** registered with the gate's particles (Gates.CURIO_VFX) */
	public static final DeferredHolder<ParticleType<?>, ParticleType<Opt>> TYPE = Gates.CURIO_VFX;

	static ParticleType<Opt> type() {
		return new ParticleType<>(true) {
			@Override
			public MapCodec<Opt> codec() {
				return CODEC;
			}

			@Override
			public StreamCodec<? super RegistryFriendlyByteBuf, Opt> streamCodec() {
				return STREAM;
			}
		};
	}


	/** a soft puff; glowing ones ignore the world's light */
	public static Opt wisp(int rgb, float size, int life, float gravity, boolean glow) {
		return new Opt(rgb, size, life, gravity, glow ? GLOW : 0);
	}

	/** a hot streak, always glowing */
	public static Opt mote(int rgb, float size, int life, float gravity) {
		return new Opt(rgb, size, life, gravity, GLOW | STREAK);
	}

	/** a flat glowing ring on the ground: band half-width, life, how fast it grows (blocks a tick) */
	public static Opt band(int rgb, float width, int life, float grow) {
		return new Opt(rgb, width, life, grow, GLOW | RING);
	}

	// ---------------------------------------------------------------- shapes

	/** a glowing ring lying flat at a point, starting at this radius and growing as its band says */
	public static void groundRing(ServerLevel l, Vec3 at, double radius, Opt band) {
		l.sendParticles(band, at.x, at.y, at.z, 0, radius, 0, 0, 1);
	}

	/** a lightning ribbon from a to b: a white core in a sheath of its colour, flickering for its life */
	public static void bolt(ServerLevel l, Vec3 a, Vec3 b, int rgb, float width, int life) {
		Vec3 d = b.subtract(a);
		l.sendParticles(new Opt(rgb, width, life, 0, GLOW | BOLT), a.x, a.y, a.z, 0, d.x, d.y, d.z, 1);
	}

	private static void send(ServerLevel l, Opt o, double x, double y, double z, double vx, double vy, double vz) {
		l.sendParticles(o, x, y, z, 0, vx, vy, vz, 1);
	}

	private static Vec3 dir(RandomSource r) {
		Vec3 v = new Vec3(r.nextGaussian(), r.nextGaussian(), r.nextGaussian());
		return v.lengthSqr() < 1e-6 ? new Vec3(0, 1, 0) : v.normalize();
	}

	/** n flying out from a point at about this speed */
	public static void burst(ServerLevel l, Vec3 at, Opt o, int n, double speed) {
		RandomSource r = l.getRandom();
		for (int i = 0; i < n; i++) {
			Vec3 v = dir(r).scale(speed * (0.5 + r.nextDouble()));
			send(l, o, at.x, at.y, at.z, v.x, v.y, v.z);
		}
	}

	/** n from random points on a body, drifting out and up a little */
	public static void around(LivingEntity e, Opt o, int n, double speed) {
		if (!(e.level() instanceof ServerLevel l)) return;
		RandomSource r = l.getRandom();
		double w = e.getBbWidth() * 0.6, h = e.getBbHeight();
		for (int i = 0; i < n; i++) {
			double x = e.getX() + (r.nextDouble() - 0.5) * 2 * w, y = e.getY() + r.nextDouble() * h, z = e.getZ() + (r.nextDouble() - 0.5) * 2 * w;
			Vec3 v = new Vec3(x - e.getX(), 0.3, z - e.getZ()).normalize().scale(speed);
			send(l, o, x, y, z, v.x, v.y, v.z);
		}
	}

	/** the middle of a body */
	public static Vec3 chest(LivingEntity e) {
		return e.position().add(0, e.getBbHeight() * 0.6, 0);
	}

	/** n round a flat ring, pushed outward (0: a still ring) */
	public static void ring(ServerLevel l, Vec3 at, double radius, Opt o, int n, double out) {
		double turn = l.getRandom().nextDouble() * Math.PI * 2;
		for (int i = 0; i < n; i++) {
			double a = turn + i * Math.PI * 2 / n;
			double cx = Math.cos(a), cz = Math.sin(a);
			send(l, o, at.x + cx * radius, at.y, at.z + cz * radius, cx * out, 0.01, cz * out);
		}
	}

	/** n from a sphere round a point, rushing in to it over about their life */
	public static void implode(ServerLevel l, Vec3 at, double radius, Opt o, int n) {
		RandomSource r = l.getRandom();
		for (int i = 0; i < n; i++) {
			Vec3 d = dir(r);
			Vec3 p = at.add(d.scale(radius));
			Vec3 v = d.scale(-radius / Math.max(4, o.life() * 0.6));
			send(l, o, p.x, p.y, p.z, v.x, v.y, v.z);
		}
	}

	/** a jagged line from a to b: motes along it, each kicked a little sideways */
	public static void arc(ServerLevel l, Vec3 a, Vec3 b, Opt o, int n, double jag) {
		RandomSource r = l.getRandom();
		Vec3 along = b.subtract(a);
		for (int i = 0; i <= n; i++) {
			Vec3 p = a.add(along.scale(i / (double) n)).add(dir(r).scale(jag * Math.sin(Math.PI * i / n)));
			Vec3 v = along.normalize().scale(0.05).add(dir(r).scale(0.02));
			send(l, o, p.x, p.y, p.z, v.x, v.y, v.z);
		}
	}

	/** n falling from under a body's middle (drips) */
	public static void drip(LivingEntity e, Opt o, int n) {
		if (!(e.level() instanceof ServerLevel l)) return;
		RandomSource r = l.getRandom();
		for (int i = 0; i < n; i++) {
			double w = e.getBbWidth() * 0.5;
			send(l, o, e.getX() + (r.nextDouble() - 0.5) * 2 * w, e.getY() + e.getBbHeight() * (0.3 + 0.5 * r.nextDouble()),
					e.getZ() + (r.nextDouble() - 0.5) * 2 * w, 0, -0.02, 0);
		}
	}

	/** n rising slowly off a body (auras, blessings) */
	public static void rise(LivingEntity e, Opt o, int n) {
		if (!(e.level() instanceof ServerLevel l)) return;
		RandomSource r = l.getRandom();
		double w = e.getBbWidth() * 0.55;
		for (int i = 0; i < n; i++)
			send(l, o, e.getX() + (r.nextDouble() - 0.5) * 2 * w, e.getY() + r.nextDouble() * e.getBbHeight() * 0.8,
					e.getZ() + (r.nextDouble() - 0.5) * 2 * w, 0, 0.03 + r.nextDouble() * 0.03, 0);
	}
}
