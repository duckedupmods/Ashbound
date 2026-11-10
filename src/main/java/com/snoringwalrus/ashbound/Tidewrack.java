package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import javax.annotation.Nullable;

import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.BiomeTags;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.biome.Biomes;
import net.minecraft.world.level.levelgen.Heightmap;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.EventHooks;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;

/**
 * The Tidewrack (tools/mobs/tidewrack.py): the deep's own monsters, out of the water at night and when it storms. Round a
 * player near the sea, a beach, a river or a swamp, now and then a few come ashore just out of sight: lamprey hounds in
 * packs and merrow raiders on the coasts, reef knights out of the warm seas, net hags up the rivers and in the marshes,
 * once in a while a hullback, and in a thunderstorm, rarely, the Abyss Angler. They breathe water and walk the sea floor,
 * so they come up out of it. When the day's back and dry, the ones nobody's near go back into the sea. Never near a town.
 */
public final class Tidewrack {
	private Tidewrack() {}

	static final String TAG = "ashbound_tidewrack";
	/** per player, ticks between tries; how many may be about one player (more in a storm); how far from a town */
	private static final int EVERY = 400, CAP = 5, CAP_STORM = 8, TOWN_SAFE = 160;
	private static final float CHANCE = 0.55f, ANGLER = 0.05f;
	private static final Map<UUID, Long> NEXT = new HashMap<>();
	private static final List<Mob> LIVE = new ArrayList<>();

	/** what kind of water it is (null: none of theirs) */
	@Nullable
	static String water(ServerLevel l, BlockPos at) {
		Holder<Biome> b = l.getBiome(at);
		if (b.is(Biomes.SWAMP) || b.is(Biomes.MANGROVE_SWAMP) || b.is(BiomeTags.IS_RIVER)) return "river";
		if (b.is(Biomes.WARM_OCEAN) || b.is(Biomes.LUKEWARM_OCEAN) || b.is(Biomes.DEEP_LUKEWARM_OCEAN)) return "reef";
		if (b.is(BiomeTags.IS_OCEAN) || b.is(BiomeTags.IS_BEACH)) return "sea";
		return null;
	}

	private static String pick(RandomSource r, String water) {
		String[] kinds = {"lamprey_hound", "merrow", "reef_knight", "net_hag", "hullback"};
		int[] w = switch (water) {
			case "river" -> new int[] {2, 3, 0, 4, 1};
			case "reef" -> new int[] {3, 3, 4, 1, 1};
			default -> new int[] {4, 4, 1, 1, 1};
		};
		int sum = 0;
		for (int x : w) sum += x;
		int roll = r.nextInt(sum);
		for (int i = 0; i < w.length; i++) if ((roll -= w[i]) < 0) return kinds[i];
		return kinds[0];
	}

	private static int around(ServerLevel l, ServerPlayer p) {
		return l.getEntitiesOfClass(Mob.class, p.getBoundingBox().inflate(64), m -> m.isAlive() && m.getTags().contains(TAG)).size();
	}

	private static void tick(ServerTickEvent.Post e) {
		ServerLevel l = e.getServer().overworld();
		long now = l.getGameTime();
		if (now % 20 != 3) return;
		boolean dark = l.isNight() || l.isRaining();
		for (ServerPlayer p : l.players()) {
			if (p.isSpectator() || p.isCreative()) continue;
			long next = NEXT.getOrDefault(p.getUUID(), now + EVERY);
			if (now < next) {
				NEXT.putIfAbsent(p.getUUID(), next);
				continue;
			}
			NEXT.put(p.getUUID(), now + EVERY);
			if (!dark || l.getRandom().nextFloat() > CHANCE) continue;
			come(l, p, false);
		}
		if (now % 200 == 3) ebb(l);
	}

	/** a few come ashore round p (force: whatever the hour, for testing). How many came. */
	static int come(ServerLevel l, ServerPlayer p, boolean force) {
		if (WorldBeasts.town(p.blockPosition()) < TOWN_SAFE && !force) return 0;
		int cap = l.isThundering() ? CAP_STORM : CAP;
		if (around(l, p) >= cap && !force) return 0;
		RandomSource r = l.getRandom();
		BlockPos at = shore(l, p);
		if (at == null) return 0;
		String water = water(l, at);
		if (water == null) return 0;
		boolean angler = l.isThundering() && r.nextFloat() < ANGLER
				&& l.getEntitiesOfClass(Mob.class, p.getBoundingBox().inflate(200), m -> m.getType().builtInRegistryHolder().key().location().getPath().equals("abyss_angler")).isEmpty();
		String kind = angler ? "abyss_angler" : pick(r, water);
		int n = switch (kind) {
			case "lamprey_hound" -> 2 + r.nextInt(2);
			case "merrow" -> 1 + r.nextInt(2);
			default -> 1;
		};
		int made = 0;
		for (int i = 0; i < n; i++) {
			BlockPos s = i == 0 ? at : at.offset(r.nextInt(5) - 2, 0, r.nextInt(5) - 2);
			s = new BlockPos(s.getX(), l.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, s.getX(), s.getZ()), s.getZ());
			if (spawn(l, p, kind, s)) made++;
		}
		if (angler && made > 0) {                                  // he never comes alone
			for (int i = 0; i < 2; i++) {
				BlockPos s = at.offset(r.nextInt(7) - 3, 0, r.nextInt(7) - 3);
				s = new BlockPos(s.getX(), l.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, s.getX(), s.getZ()), s.getZ());
				spawn(l, p, "merrow", s);
			}
			for (ServerPlayer q : l.players())
				if (q.distanceToSqr(p) < 96 * 96)
					q.displayClientMessage(Component.literal("Something with a light on its head is walking out of the sea...").withStyle(net.minecraft.ChatFormatting.AQUA), true);
		}
		return made;
	}

	/** somewhere 18-36 blocks off at the water's edge (land beside water, or water no deeper than three), out of sight */
	@Nullable
	static BlockPos shore(ServerLevel l, ServerPlayer p) {
		RandomSource r = l.getRandom();
		for (int t = 0; t < 24; t++) {
			double a = r.nextDouble() * Math.PI * 2, d = 18 + r.nextDouble() * 18;
			int x = p.getBlockX() + (int) Math.round(Math.cos(a) * d), z = p.getBlockZ() + (int) Math.round(Math.sin(a) * d);
			if (!l.hasChunkAt(new BlockPos(x, 0, z))) continue;
			int top = l.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
			BlockPos at = new BlockPos(x, top, z);
			if (Math.abs(top - p.getBlockY()) > 14 || water(l, at) == null) continue;
			boolean wet = l.getFluidState(at.below()).is(FluidTags.WATER) || l.getFluidState(at).is(FluidTags.WATER);
			if (wet) {
				int floor = l.getHeight(Heightmap.Types.OCEAN_FLOOR, x, z);
				if (top - floor > 4) continue;                       // too deep to be seen coming
			} else {
				boolean beside = false;
				for (int dx = -3; dx <= 3 && !beside; dx++)
					for (int dz = -3; dz <= 3 && !beside; dz++)
						if (l.getFluidState(at.offset(dx, -1, dz)).is(FluidTags.WATER)) beside = true;
				if (!beside) continue;
			}
			if (l.getNearestPlayer(x + 0.5, top + 1, z + 0.5, 12, false) != null) continue;
			return at;
		}
		return null;
	}

	private static boolean spawn(ServerLevel l, ServerPlayer p, String kind, BlockPos at) {
		EntityType<?> type = BuiltInRegistries.ENTITY_TYPE.getOptional(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, kind)).orElse(null);
		if (type == null) return false;
		Entity e = type.create(l);
		if (!(e instanceof Mob mob)) return false;
		RandomSource r = l.getRandom();
		mob.moveTo(at.getX() + 0.5, at.getY(), at.getZ() + 0.5, r.nextFloat() * 360f, 0f);
		if (!l.noCollision(mob)) return false;
		mob.addTag(TAG);
		mob.addEffect(new MobEffectInstance(MobEffects.WATER_BREATHING, MobEffectInstance.INFINITE_DURATION, 0, false, false));
		var range = mob.getAttribute(Attributes.FOLLOW_RANGE);
		if (range != null && range.getBaseValue() < 32) range.setBaseValue(32);
		EventHooks.finalizeMobSpawn(mob, l, l.getCurrentDifficultyAt(at), MobSpawnType.EVENT, null);
		int best = 1;
		for (ServerPlayer q : l.players()) if (q.distanceToSqr(p) < 64 * 64) best = Math.max(best, Levels.level(q));
		Balance.soften(mob, kind, best);
		l.addFreshEntity(mob);
		LIVE.add(mob);
		l.sendParticles(ParticleTypes.SPLASH, at.getX() + 0.5, at.getY() + 0.5, at.getZ() + 0.5, 20, 0.6, 0.4, 0.6, 0.1);
		l.playSound(null, at, SoundEvents.DROWNED_AMBIENT_WATER, SoundSource.HOSTILE, 1f, 0.6f);
		return true;
	}

	/** the day's back and dry: the ones nobody's near go back into the sea */
	private static void ebb(ServerLevel l) {
		boolean day = !l.isNight() && !l.isRaining();
		LIVE.removeIf(m -> m.isRemoved() || !m.isAlive() || m.level() != l);
		if (!day) return;
		for (Mob m : new ArrayList<>(LIVE))
			if (l.getNearestPlayer(m, 24) == null) {
				l.sendParticles(ParticleTypes.SPLASH, m.getX(), m.getY() + 0.5, m.getZ(), 16, 0.5, 0.4, 0.5, 0.1);
				m.discard();
				LIVE.remove(m);
			}
	}

	private static void commands(RegisterCommandsEvent e) {
		e.getDispatcher().register(Commands.literal("ashbound").requires(c -> c.hasPermission(2)).then(Commands.literal("tidewrack").executes(c -> {
			ServerPlayer p = c.getSource().getPlayerOrException();
			int n = come(p.serverLevel(), p, true);
			c.getSource().sendSuccess(() -> Component.literal(n > 0 ? n + " came out of the water" : "No water's edge near here"), false);
			return n;
		})));
	}

	static void init() {
		NeoForge.EVENT_BUS.addListener(Tidewrack::tick);
		NeoForge.EVENT_BUS.addListener(Tidewrack::commands);
	}
}
