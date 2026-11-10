package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

import javax.annotation.Nullable;

import com.mojang.brigadier.arguments.StringArgumentType;

import net.minecraft.ChatFormatting;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.BiomeTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.AABB;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.common.Tags;
import net.neoforged.neoforge.event.EventHooks;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.entity.living.LivingDropsEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;

/**
 * The world's beasts (tools/mobs/world_beasts.py): one kind to each land, out in the wild where nobody lives, at a
 * rank you can read over its head. Near a town they're no worse than E; out in the wild they come at your party's
 * rank, sometimes one above (more often in the hard lands), now and then one below. A beast is a fight like a gate's
 * elite and pays like one; it drops finds of its rank, the rank's materials and sometimes a world weapon.
 *
 * Each beast has its legend (the same kind grown huge, scarred and named): they come with the hunts (posters, trails);
 * for now only by command.
 */
final class WorldBeasts {
	static final String TAG = "ashbound_beast", RANK = "ashbound_beast_rank";
	private static final String RANKS = "FEDCBAS";

	/** a beast, its land and its legend */
	record Beast(String id, String land, String legend, String legendName) {}

	static final List<Beast> ALL = List.of(
			new Beast("old_blackbriar", "forest", "old_blackbriar", "Old Blackbriar"),
			new Beast("red_plough", "plains", "red_plough", "The Red Plough"),
			new Beast("rime_penitent", "snow", "rime_penitent", "The Rime Penitent"),
			new Beast("sunbreaker", "desert", "sunbreaker", "Sunbreaker"),
			new Beast("grandmother_mire", "swamp", "grandmother_mire", "Grandmother Mire"),
			new Beast("hollow_smile", "jungle", "hollow_smile", "The Hollow Smile"),
			new Beast("old_harpoon", "coast", "old_harpoon", "Old Harpoon"),
			new Beast("walking_mountain", "badlands", "walking_mountain", "The Walking Mountain"));
	static final Set<String> IDS = new HashSet<>();
	static {
		for (Beast b : ALL) {
			IDS.add(b.id());
			IDS.add(b.legend());
		}
	}

	/** checks every EVERY ticks per player after FIRST; a Legend CHANCE of the time when none is within NONE_WITHIN; after one's come,
	 * none for REST. A wild one's a rare surprise (about one in 20-30 minutes out in the wild): the posters (Bounties) are how you go looking. */
	private static final int FIRST = 6000, EVERY = 1200, REST = 18000, NONE_WITHIN = 160, NEAR = 56, FAR = 96;
	private static final float CHANCE = 0.08f;
	/** no beast this close to a town; within TOWN_TAME of one they're E at worst; past WILD from any, one rank higher more often */
	private static final int TOWN_SAFE = 220, TOWN_TAME = 500, WILD = 1500;
	/** left alone this long with nobody within GONE blocks, it goes back into the wild */
	private static final int GONE = 200, IDLE = 2400;
	private static final Map<UUID, Long> NEXT = new HashMap<>();
	private static final Map<UUID, Long> ALONE = new HashMap<>();
	private static final List<Mob> LIVE = new ArrayList<>();

	private WorldBeasts() {}

	/** which land a biome is (null: none of ours lives there) */
	@Nullable
	static String land(Holder<Biome> b) {
		if (b.is(BiomeTags.IS_OCEAN) || b.is(BiomeTags.IS_DEEP_OCEAN) || b.is(BiomeTags.IS_RIVER)) return null;
		if (b.is(Tags.Biomes.IS_SNOWY) || b.is(Tags.Biomes.IS_ICY)) return "snow";
		if (b.is(BiomeTags.IS_BADLANDS) || b.is(Tags.Biomes.IS_MOUNTAIN_PEAK) || b.is(Tags.Biomes.IS_WINDSWEPT)) return "badlands";
		if (b.is(Tags.Biomes.IS_DESERT)) return "desert";
		if (b.is(Tags.Biomes.IS_SWAMP)) return "swamp";
		if (b.is(BiomeTags.IS_JUNGLE)) return "jungle";
		if (b.is(BiomeTags.IS_BEACH) || b.is(Tags.Biomes.IS_STONY_SHORES)) return "coast";
		if (b.is(Tags.Biomes.IS_PLAINS) || b.is(BiomeTags.IS_SAVANNA)) return "plains";
		if (b.is(BiomeTags.IS_FOREST) || b.is(BiomeTags.IS_TAIGA)) return "forest";
		return null;
	}

	@Nullable
	static Beast of(String land) {
		for (Beast b : ALL)
			if (b.land().equals(land)) return b;
		return null;
	}

	/** how far the nearest town is */
	static double town(BlockPos at) {
		double best = Double.MAX_VALUE;
		for (Capital.Site s : Capital.sites)
			best = Math.min(best, Math.hypot(s.x - at.getX(), s.z - at.getZ()));
		return best;
	}

	/** the rank a beast comes at here, for this player's party */
	static int rankFor(ServerPlayer p, BlockPos at, String land, RandomSource r) {
		int rank = Ranks.party(p);
		double t = town(at);
		boolean hard = land.equals("snow") || land.equals("badlands") || land.equals("jungle") || land.equals("swamp");
		float up = (hard ? 0.25f : 0.12f) + (t > WILD ? 0.15f : 0f);
		float roll = r.nextFloat();
		if (roll < up) rank++;
		else if (roll > 0.9f) rank--;
		if (t < TOWN_TAME) rank = Math.min(rank, 1);
		// F to A in the wild; an S (or higher) party meets them at S. Never above S, never S for a party below it
		return Math.max(0, Math.min(Ranks.party(p) >= 6 ? 6 : 5, rank));
	}

	/** One beast (or a pair of gorehorns) at a rank: its name over its head, the rank's strength. */
	@Nullable
	static Mob spawn(ServerLevel l, String id, BlockPos at, int rank, RandomSource r) {
		var type = BuiltInRegistries.ENTITY_TYPE.getOptional(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, id)).orElse(null);
		if (type == null || !(type.create(l) instanceof Mob m)) return null;
		m.moveTo(at.getX() + 0.5, at.getY(), at.getZ() + 0.5, r.nextFloat() * 360f, 0);
		EventHooks.finalizeMobSpawn(m, l, l.getCurrentDifficultyAt(at), MobSpawnType.EVENT, null);
		m.setPersistenceRequired();
		String rk = RANKS.substring(rank, rank + 1);
		Balance.atRank(m, id, rk);
		m.addTag(TAG);
		m.getPersistentData().putInt(RANK, rank);
		m.setCustomName(nameplate(m, rank, null));
		m.setCustomNameVisible(true);
		l.addFreshEntity(m);
		return m;
	}

	/** "[C] Thornmaw", the rank coloured: grey to gold to red as it climbs */
	static Component nameplate(Mob m, int rank, @Nullable String name) {
		ChatFormatting c = switch (rank) {
			case 0, 1 -> ChatFormatting.GRAY;
			case 2 -> ChatFormatting.WHITE;
			case 3 -> ChatFormatting.YELLOW;
			case 4 -> ChatFormatting.GOLD;
			case 5 -> ChatFormatting.RED;
			default -> ChatFormatting.DARK_RED;
		};
		return Component.literal("[" + RANKS.charAt(rank) + "] ").withStyle(c, ChatFormatting.BOLD)
				.append(name != null ? Component.literal(name).withStyle(ChatFormatting.DARK_RED, ChatFormatting.BOLD)
						: m.getType().getDescription().copy().withStyle(ChatFormatting.WHITE));
	}

	/** A legend at a rank: its name, the strength of a boss, more health for every player who's come for it. */
	@Nullable
	static Mob legend(ServerLevel l, Beast b, BlockPos at, int rank, RandomSource r) {
		Mob m = spawn(l, b.legend(), at, rank, r);
		if (m == null) return null;
		int players = l.getEntitiesOfClass(ServerPlayer.class, new AABB(at).inflate(48), p -> !p.isSpectator()).size();
		var hp = m.getAttribute(Attributes.MAX_HEALTH);
		if (hp != null && players > 1)
			hp.addPermanentModifier(new AttributeModifier(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "legend_party"), 0.5 * (players - 1),
					AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL));
		m.setHealth(m.getMaxHealth());
		m.setCustomName(nameplate(m, rank, b.legendName()));
		return m;
	}

	// ---------------------------------------------------------------- the wild

	private static void tick(ServerTickEvent.Post e) {
		var server = e.getServer();
		long now = server.getTickCount();
		if (now % 100 != 31) return;
		ServerLevel l = server.overworld();
		roam(l, now);
		for (ServerPlayer p : l.players()) {
			if (p.isSpectator() || p.isCreative()) continue;
			long next = NEXT.computeIfAbsent(p.getUUID(), u -> now + FIRST);
			if (now < next) continue;
			NEXT.put(p.getUUID(), now + EVERY);
			RandomSource r = p.getRandom();
			if (r.nextFloat() > CHANCE * (Ashfall.on(l) ? 3 : 1)) continue;   // an ashfall night wakes them
			if (!l.getEntitiesOfClass(Mob.class, p.getBoundingBox().inflate(NONE_WITHIN), m -> m.getTags().contains(TAG)).isEmpty()) continue;
			if (tryNear(l, p, r) != null) NEXT.put(p.getUUID(), now + REST);
		}
	}

	/** a spot NEAR-FAR off in the wild with one of ours living there; a beast of that land */
	@Nullable
	static Mob tryNear(ServerLevel l, ServerPlayer p, RandomSource r) {
		for (int tries = 0; tries < 6; tries++) {
			double a = r.nextDouble() * Math.PI * 2, d = NEAR + r.nextDouble() * (FAR - NEAR);
			BlockPos top = l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
					p.blockPosition().offset((int) Math.round(Math.cos(a) * d), 0, (int) Math.round(Math.sin(a) * d)));
			if (!l.getFluidState(top.below()).isEmpty() || !l.getFluidState(top).isEmpty()) continue;
			if (town(top) < TOWN_SAFE) continue;
			String land = land(l.getBiome(top));
			Beast b = land == null ? null : of(land);
			// only the Legends remade on their own skeletons come out on their own; the old spider ones wait for theirs
			if (b == null || !com.snoringwalrus.ashbound.Beast.KINDS.containsKey(b.id())) continue;
			int rank = rankFor(p, top, land, r);
			if (b.id().equals(b.legend())) return legend(l, b, top, rank, r);
			Mob m = spawn(l, b.id(), top, rank, r);
			if (m != null && b.id().equals("gorehorn") && r.nextFloat() < 0.35f)   // gorehorns walk in pairs
				spawn(l, b.id(), top.offset(3, 0, 2), rank, r);
			return m;
		}
		return null;
	}

	/** beasts nobody's near go back to the wild */
	private static void roam(ServerLevel l, long now) {
		for (Iterator<Mob> it = LIVE.iterator(); it.hasNext(); ) {
			Mob m = it.next();
			if (m.isRemoved()) {
				it.remove();
				ALONE.remove(m.getUUID());
				continue;
			}
			boolean near = l.getNearestPlayer(m, GONE) != null;
			if (near || m.getTarget() != null) {
				ALONE.remove(m.getUUID());
				continue;
			}
			long since = ALONE.computeIfAbsent(m.getUUID(), u -> now);
			if (now - since > IDLE) {
				m.discard();
				it.remove();
				ALONE.remove(m.getUUID());
			}
		}
	}

	// ---------------------------------------------------------------- what it leaves

	private static void drops(LivingDropsEvent e) {
		if (!(e.getEntity() instanceof Mob m) || !m.getTags().contains(TAG) || !(m.level() instanceof ServerLevel l)) return;
		if (!(e.getSource().getEntity() instanceof ServerPlayer p)) return;
		RandomSource r = m.getRandom();
		int rank = m.getPersistentData().getInt(RANK);
		String kind = m.getType().builtInRegistryHolder().key().location().getPath();
		boolean legend = ALL.stream().anyMatch(b -> b.legend().equals(kind));
		List<ItemStack> out = new ArrayList<>();
		int finds = legend ? 3 + r.nextInt(2) : 1 + (r.nextFloat() < 0.5f ? 1 : 0);
		for (int i = 0; i < finds; i++) out.add(new ItemStack(Ranks.find(p, r)));
		Gear.Dungeon d = Adventurers.any(Adventurers.dungeons(RANKS.charAt(rank)), r);
		if (d != null && d.mats().length > 0) {
			var it = Gear.item(d.mats()[0]);
			if (it != null) out.add(new ItemStack(it, (legend ? 4 : 1) + r.nextInt(3)));
			if (d.mats().length > 1 && r.nextFloat() < (legend ? 1f : 0.35f)) {
				var it2 = Gear.item(d.mats()[1]);
				if (it2 != null) out.add(new ItemStack(it2, 1 + r.nextInt(legend ? 3 : 1)));
			}
		}
		if (r.nextFloat() < (legend ? 0.8f : 0.2f)) {
			var w = WorldArms.pick(r, rank + (legend ? 2 : 1));
			if (w != null) out.add(new ItemStack(w));
		}
		ItemStack trophy = Trophies.of(kind);   // the piece of it you take home
		if (legend && !trophy.isEmpty()) out.add(trophy);
		for (ItemStack s : out) e.getDrops().add(new ItemEntity(l, m.getX(), m.getY() + 1, m.getZ(), s));
	}

	// ---------------------------------------------------------------- testing

	private static void commands(RegisterCommandsEvent e) {
		e.getDispatcher().register(Commands.literal("ashbound").requires(c -> c.hasPermission(2)).then(Commands.literal("legend")
				.executes(c -> {
					ServerPlayer p = c.getSource().getPlayerOrException();
					Mob m = tryNear(p.serverLevel(), p, p.getRandom());
					if (m == null) c.getSource().sendFailure(Component.literal("No Legend's land near here (or a town's too close)"));
					else c.getSource().sendSuccess(() -> Component.literal("A ").append(m.getCustomName()).append(" " + (int) m.distanceTo(p) + " blocks off"), false);
					return m == null ? 0 : 1;
				})
				.then(Commands.argument("id", StringArgumentType.word()).suggests((c, b) -> {
					for (String id : IDS) b.suggest(id);
					return b.buildFuture();
				}).executes(c -> here(c.getSource().getPlayerOrException(), StringArgumentType.getString(c, "id"), -1, c.getSource()))
						.then(Commands.argument("rank", StringArgumentType.word()).suggests((c, b) -> {
							for (char ch : "FEDCBAS".toCharArray()) b.suggest(String.valueOf(ch));
							return b.buildFuture();
						}).executes(c -> here(c.getSource().getPlayerOrException(), StringArgumentType.getString(c, "id"),
								RANKS.indexOf(StringArgumentType.getString(c, "rank").toUpperCase()), c.getSource()))))));
	}

	/** /ashbound legend <id> [rank]: one ahead of you, at your party's rank unless named */
	private static int here(ServerPlayer p, String id, int rank, net.minecraft.commands.CommandSourceStack src) {
		ServerLevel l = p.serverLevel();
		if (rank < 0) rank = Ranks.party(p);
		BlockPos at = l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, BlockPos.containing(p.position().add(p.getLookAngle().multiply(12, 0, 12))));
		Mob m = null;
		for (Beast b : ALL) {
			if (b.legend().equals(id)) m = legend(l, b, at, rank, p.getRandom());
			else if (b.id().equals(id)) m = spawn(l, id, at, Math.min(rank, 5), p.getRandom());
		}
		if (m == null) {
			src.sendFailure(Component.literal("No Legend called " + id));
			return 0;
		}
		Mob made = m;
		src.sendSuccess(() -> Component.literal("Here: ").append(made.getCustomName()), false);
		return 1;
	}

	static boolean is(Entity e) {
		return e.getTags().contains(TAG);
	}

	static void init() {
		NeoForge.EVENT_BUS.addListener(WorldBeasts::tick);
		NeoForge.EVENT_BUS.addListener(WorldBeasts::drops);
		NeoForge.EVENT_BUS.addListener(WorldBeasts::commands);
		NeoForge.EVENT_BUS.addListener((net.neoforged.neoforge.event.entity.EntityJoinLevelEvent e) -> {
			if (!e.getLevel().isClientSide && e.getEntity() instanceof Mob m && is(m) && !LIVE.contains(m)) LIVE.add(m);   // ones saved with the world
		});
	}
}
