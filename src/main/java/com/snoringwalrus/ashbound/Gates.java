package com.snoringwalrus.ashbound;

import com.mojang.brigadier.arguments.StringArgumentType;

import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ColorParticleOption;
import net.minecraft.core.particles.ParticleType;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.level.material.PushReaction;
import net.minecraft.world.phys.Vec3;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * Gates open by themselves round the world, out of sight of whoever's near (48-144 blocks off), never in the
 * capital or its land. Rarer the deadlier. Nobody is told a rank: its colour is all you get.
 *
 * /ashbound gate [F..SSS] opens one 13 blocks in front of you; /ashbound gate close closes those near you (as if cleared).
 */
public final class Gates {
	private Gates() {}

	static final DeferredRegister<EntityType<?>> ENTITIES = DeferredRegister.create(Registries.ENTITY_TYPE, Ashbound.ID);
	static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(Ashbound.ID);
	static final DeferredRegister<ParticleType<?>> PARTICLES = DeferredRegister.create(Registries.PARTICLE_TYPE, Ashbound.ID);

	/** Its sparks (streaks along their flight) and smoke; the colour rides along (alpha 0xFE = glowing smoke). */
	public static final DeferredHolder<ParticleType<?>, ParticleType<ColorParticleOption>> SPARK = PARTICLES.register("gate_spark", Gates::colourType);
	public static final DeferredHolder<ParticleType<?>, ParticleType<ColorParticleOption>> SMOKE = PARTICLES.register("gate_smoke", Gates::colourType);
	/** the curios' effects (Vfx), drawn the same way */
	public static final DeferredHolder<ParticleType<?>, ParticleType<Vfx.Opt>> CURIO_VFX = PARTICLES.register("curio_vfx", Vfx::type);

	private static ParticleType<ColorParticleOption> colourType() {
		return new ParticleType<>(true) {
			@Override
			public com.mojang.serialization.MapCodec<ColorParticleOption> codec() {
				return ColorParticleOption.codec(this);
			}

			@Override
			public net.minecraft.network.codec.StreamCodec<? super net.minecraft.network.RegistryFriendlyByteBuf, ColorParticleOption> streamCodec() {
				return ColorParticleOption.streamCodec(this);
			}
		};
	}

	public static final DeferredHolder<EntityType<?>, EntityType<GateEntity>> GATE = ENTITIES.register("gate",
			() -> EntityType.Builder.<GateEntity>of(GateEntity::new, MobCategory.MISC).sized(1f, 1f).fireImmune()
					.clientTrackingRange(24).updateInterval(40).build(Ashbound.ID + ":gate"));

	public static final DeferredBlock<GateScorch> SCORCH = BLOCKS.registerBlock("gate_scorch", GateScorch::new, BlockBehaviour.Properties.of()
			.mapColor(MapColor.COLOR_BLACK).noCollission().instabreak().noLootTable().replaceable().randomTicks().noOcclusion()
			.sound(SoundType.SAND).pushReaction(PushReaction.DESTROY).lightLevel(s -> s.getValue(GateScorch.FADING) ? 1 : 5));

	/** How often each rank opens, F to SSS (only ranks with a built dungeon, GateDungeons). */
	private static final double[] ODDS = {30, 24, 17, 12, 8, 5, 2.5, 1, 0.5};
	/** Every 20 s, for each player: this chance of a try. At most this many open round anyone. */
	private static final float CHANCE = 0.08f;
	private static final int NEAR_MAX = 2;

	static void register(IEventBus bus) {
		ENTITIES.register(bus);
		BLOCKS.register(bus);
		PARTICLES.register(bus);
		NeoForge.EVENT_BUS.addListener(Gates::tick);
		NeoForge.EVENT_BUS.addListener((RegisterCommandsEvent e) -> e.getDispatcher().register(Commands.literal("ashbound")
				.requires(c -> c.hasPermission(2))
				.then(Commands.literal("gate")
						.executes(c -> open(c.getSource(), -1))
						.then(Commands.literal("close").executes(c -> closeNear(c.getSource())))
						.then(Commands.argument("rank", StringArgumentType.word())
								.suggests((c, b) -> {
									for (int i = 0; i < GateEntity.RANKS.length; i++) if (GateDungeons.has(i)) b.suggest(GateEntity.RANKS[i]);
									return b.buildFuture();
								})
								.executes(c -> open(c.getSource(), rankOf(StringArgumentType.getString(c, "rank"))))))));
	}

	private static int rankOf(String s) {
		for (int i = 0; i < GateEntity.RANKS.length; i++) if (GateEntity.RANKS[i].equalsIgnoreCase(s)) return i;
		return -1;
	}

	static int roll(RandomSource r) {
		double total = 0;
		for (int i = 0; i < ODDS.length; i++) if (GateDungeons.has(i)) total += ODDS[i];
		double x = r.nextDouble() * total;
		for (int i = 0; i < ODDS.length; i++) if (GateDungeons.has(i) && (x -= ODDS[i]) < 0) return i;
		return 0;
	}

	/** A gate whose foot is at `at`, its face looking along `yaw`. */
	public static GateEntity spawn(ServerLevel level, Vec3 at, float yaw, int rank) {
		GateEntity g = GATE.get().create(level);
		if (g == null) return null;
		g.moveTo(at.x, at.y, at.z, yaw, 0);
		g.setRank(rank);
		g.opened(level.getGameTime());
		level.addFreshEntity(g);
		if (level.dimension() != Lairs.GATES) {                     // the dungeon behind it goes up while it tears open
			String lair = GateDungeons.of(g).lair();
			if (lair != null) Lairs.prepare(level.getServer(), lair);
		}
		return g;
	}

	private static int open(CommandSourceStack src, int rank) {
		ServerPlayer p = src.getPlayer();
		if (p == null) return 0;
		ServerLevel level = src.getLevel();
		Vec3 f = Vec3.directionFromRotation(0, p.getYRot());
		Vec3 at = p.position().add(f.x * 13, 0, f.z * 13);
		if (rank >= 0 && !GateDungeons.has(rank)) {
			src.sendFailure(Component.literal("No dungeon of that rank is built yet."));
			return 0;
		}
		spawn(level, at, p.getYRot() + 180f, rank < 0 ? roll(level.random) : rank);
		return 1;
	}

	private static int closeNear(CommandSourceStack src) {
		var near = src.getLevel().getEntitiesOfClass(GateEntity.class, new net.minecraft.world.phys.AABB(BlockPos.containing(src.getPosition())).inflate(24));
		near.forEach(GateEntity::close);
		src.sendSuccess(() -> Component.literal(near.size() + " gate(s) closing"), false);
		return near.size();
	}

	private static void tick(ServerTickEvent.Post e) {
		if (e.getServer().getTickCount() % 400 != 0) return;
		ServerLevel level = e.getServer().getLevel(Level.OVERWORLD);
		if (level == null) return;
		for (ServerPlayer p : level.players()) {
			if (p.isSpectator() || level.random.nextFloat() > CHANCE) continue;
			int near = level.getEntitiesOfClass(GateEntity.class, p.getBoundingBox().inflate(256, 400, 256), g -> !g.closing()).size();
			if (near < NEAR_MAX) tryOpen(level, p);
		}
	}

	/** Somewhere open, on solid dry ground, with nothing over it, not in the city. */
	private static void tryOpen(ServerLevel level, ServerPlayer p) {
		RandomSource r = level.random;
		for (int tries = 0; tries < 8; tries++) {
			double a = r.nextDouble() * Math.PI * 2, d = 48 + r.nextDouble() * 96;
			int x = Mth.floor(p.getX() + Math.cos(a) * d), z = Mth.floor(p.getZ() + Math.sin(a) * d);
			if (!level.hasChunkAt(new BlockPos(x, 0, z)) || Capital.blocksStructures(new ChunkPos(x >> 4, z >> 4))) continue;
			int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
			BlockPos ground = new BlockPos(x, y - 1, z);
			BlockState g = level.getBlockState(ground);
			if (!g.getFluidState().isEmpty() || !g.isFaceSturdy(level, ground, net.minecraft.core.Direction.UP)) continue;
			if (!clear(level, x, y, z)) continue;
			float yaw = (float) Math.toDegrees(Math.atan2(-(p.getX() - x - 0.5), p.getZ() - z - 0.5));
			spawn(level, new Vec3(x + 0.5, y, z + 0.5), yaw, roll(r));
			return;
		}
	}

	private static boolean clear(ServerLevel level, int x, int y, int z) {
		for (int dx = -3; dx <= 3; dx++)
			for (int dz = -3; dz <= 3; dz++)
				for (int dy = 0; dy <= 11; dy++) {
					BlockState s = level.getBlockState(new BlockPos(x + dx, y + dy, z + dz));
					if (s.is(BlockTags.LEAVES) || s.is(BlockTags.LOGS) || (!s.isAir() && !s.canBeReplaced())) return false;
				}
		return true;
	}
}
