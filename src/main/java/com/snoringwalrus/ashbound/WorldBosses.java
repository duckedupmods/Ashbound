package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.Predicate;

import net.minecraft.ChatFormatting;
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
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.common.Tags;
import net.neoforged.neoforge.event.EventHooks;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.neoforged.neoforge.registries.DeferredItem;

/**
 * The five overworld bosses, fought whenever you like: craft a boss's summon, carry it to open ground of its own land, well
 * away from any town, and use it. The boss rises a little way off (a boss bar of its own, from MobSkills), made at
 * your party's; the party scales it as usual (Balance). Everyone near when it falls gets their own spoils: finds, mats of
 * that rank, often a world weapon, coins, and whatever a quest wanted from it. Left alone too long, it goes back where it
 * came from and the summoner gets the summon back.
 */
public final class WorldBosses {
	private WorldBosses() {}

	/** a boss: its summon, the land it answers in (and how to say so), what it says when it comes */
	record Boss(String kind, String summon, String landName, Predicate<Holder<Biome>> land, String rises) {}

	static final List<Boss> ALL = List.of(
			new Boss("cairn_giant", "cairn_stone", "the mountains",
					b -> b.is(BiomeTags.IS_MOUNTAIN) || b.is(Tags.Biomes.IS_MOUNTAIN) || b.is(Tags.Biomes.IS_WINDSWEPT),
					"The ground heaves. The hillside stands up."),
			new Boss("hart_lord", "harts_horn", "a forest",
					b -> b.is(BiomeTags.IS_FOREST) || b.is(BiomeTags.IS_TAIGA),
					"Far off, a horn answers yours. The trees go quiet."),
			new Boss("saltglass_hydra", "brine_lure", "the coast",
					b -> b.is(BiomeTags.IS_BEACH) || b.is(Tags.Biomes.IS_STONY_SHORES) || b.is(BiomeTags.IS_OCEAN),
					"The tide pulls out all at once. Something comes in with it."),
			new Boss("ironback_scorpion", "rusted_stinger", "the badlands or the desert",
					b -> b.is(BiomeTags.IS_BADLANDS) || b.is(Tags.Biomes.IS_DESERT),
					"The sand starts to slide toward one place. Iron grinds under it."),
			new Boss("rime_lich", "frozen_phylactery", "the snow",
					b -> b.is(Tags.Biomes.IS_SNOWY) || b.is(Tags.Biomes.IS_ICY),
					"The air freezes mid-breath. Someone is walking out of the snow."));

	public static final Map<String, DeferredItem<Item>> SUMMONS = new HashMap<>();

	static {
		for (Boss b : ALL)
			SUMMONS.put(b.summon(), Weapons.ITEMS.registerItem(b.summon(), p -> new Summon(p.rarity(Rarity.EPIC).stacksTo(1), b)));
	}

	static final String TAG = "ashbound_world_boss", RANK = "ashbound_world_boss_rank";
	/** this far from any town at least; no second boss this close to a live one */
	static final int TOWN_FAR = 300, APART = 200;
	/** it goes home when nobody has been within GONE blocks for IDLE ticks */
	private static final int GONE = 96, IDLE = 2400;

	/** a live summoned boss: who called it, with what, and since when it's been alone */
	private static final class Live {
		final Mob mob;
		final UUID by;
		final Boss boss;
		long alone = -1;

		Live(Mob mob, UUID by, Boss boss) {
			this.mob = mob;
			this.by = by;
			this.boss = boss;
		}
	}

	private static final List<Live> LIVE = new ArrayList<>();

	static void init() {
		NeoForge.EVENT_BUS.addListener(WorldBosses::died);
		NeoForge.EVENT_BUS.addListener(WorldBosses::tick);
		NeoForge.EVENT_BUS.addListener(WorldBosses::commands);
	}

	static Boss of(String kind) {
		for (Boss b : ALL) if (b.kind().equals(kind)) return b;
		return null;
	}

	// ---------------------------------------------------------------- the summon

	public static final class Summon extends Item {
		final Boss boss;

		Summon(Properties p, Boss boss) {
			super(p);
			this.boss = boss;
		}

		@Override
		public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
			ItemStack held = player.getItemInHand(hand);
			if (!(level instanceof ServerLevel l) || !(player instanceof ServerPlayer p)) return InteractionResultHolder.sidedSuccess(held, level.isClientSide);
			String why = call(l, p, boss);
			if (why != null) {
				p.displayClientMessage(Component.literal(why).withStyle(ChatFormatting.RED), true);
				return InteractionResultHolder.fail(held);
			}
			if (!p.getAbilities().instabuild) held.shrink(1);
			return InteractionResultHolder.consume(held);
		}

		@Override
		public void appendHoverText(ItemStack stack, TooltipContext ctx, List<Component> tip, TooltipFlag flag) {
			tip.add(Component.literal("Use it on open ground in " + boss.landName() + ",").withStyle(ChatFormatting.GRAY));
			tip.add(Component.literal("far from any town. Bring your party.").withStyle(ChatFormatting.GRAY));
		}
	}

	/** Call the boss for this player: null if it came, else why not. */
	static String call(ServerLevel l, ServerPlayer p, Boss boss) {
		if (l.dimension() != Level.OVERWORLD) return "Nothing answers here. It has to be out in the world.";
		BlockPos at = p.blockPosition();
		if (!boss.land().test(l.getBiome(at))) return "Nothing answers here. Take it to " + boss.landName() + ".";
		if (WorldBeasts.town(at) < TOWN_FAR) return "Too near a town. Go further out, it won't come where people live.";
		for (Live v : LIVE)
			if (v.mob.isAlive() && v.mob.level() == l && v.mob.distanceToSqr(p) < APART * APART) return "Something already answered near here.";
		var type = BuiltInRegistries.ENTITY_TYPE.getOptional(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, boss.kind())).orElse(null);
		if (type == null) return "Nothing answers. (No such boss.)";
		Vec3 spot = spot(l, p, type);
		if (spot == null) return "There's no room for it here. Find open ground.";
		if (!(type.create(l) instanceof Mob m)) return "Nothing answers. (No such boss.)";
		float yaw = (float) (Mth.atan2(p.getZ() - spot.z, p.getX() - spot.x) * Mth.RAD_TO_DEG) - 90f;
		m.moveTo(spot.x, spot.y, spot.z, yaw, 0);
		EventHooks.finalizeMobSpawn(m, l, l.getCurrentDifficultyAt(BlockPos.containing(spot)), MobSpawnType.EVENT, null);
		m.setPersistenceRequired();
		m.addTag(TAG);
		int rank = Mth.clamp(Ranks.party(p), 0, Ranks.LADDER.length() - 1);   // at your party's rank: it's solved at twice a gate boss (balance.py WORLD_BOSSES)
		m.getPersistentData().putInt(RANK, rank);
		Balance.atRank(m, boss.kind(), String.valueOf(Ranks.LADDER.charAt(rank)));
		m.setYHeadRot(yaw);
		l.addFreshEntity(m);
		m.setTarget(p);
		LIVE.add(new Live(m, p.getUUID(), boss));
		// it comes up out of the ground in a burst of dust and a long low sound
		l.sendParticles(ParticleTypes.EXPLOSION_EMITTER, spot.x, spot.y + 1, spot.z, 2, 1.5, 0.5, 1.5, 0);
		l.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, spot.x, spot.y + 0.5, spot.z, 60, 3, 0.5, 3, 0.04);
		l.playSound(null, spot.x, spot.y, spot.z, SoundEvents.WARDEN_EMERGE, SoundSource.HOSTILE, 3f, 0.7f);
		l.playSound(null, spot.x, spot.y, spot.z, SoundEvents.RAID_HORN.value(), SoundSource.HOSTILE, 4f, 0.8f);
		for (ServerPlayer q : l.getEntitiesOfClass(ServerPlayer.class, new AABB(BlockPos.containing(spot)).inflate(80), Player::isAlive)) {
			q.sendSystemMessage(Component.literal(boss.rises()).withStyle(ChatFormatting.GOLD, ChatFormatting.ITALIC));
			q.sendSystemMessage(Component.literal("  ").append(m.getDisplayName()).append(Component.literal(", rank " + Ranks.LADDER.charAt(rank)))
					.withStyle(ChatFormatting.RED));
		}
		return null;
	}

	/** where it rises: on the ground 10 to 16 blocks off, the way you face if it fits, else round you; null if nowhere fits */
	private static Vec3 spot(ServerLevel l, ServerPlayer p, net.minecraft.world.entity.EntityType<?> type) {
		RandomSource r = p.getRandom();
		for (int i = 0; i < 24; i++) {
			double a = Math.toRadians(p.getYRot() + 90) + (i == 0 ? 0 : (r.nextDouble() - 0.5) * Math.PI * (i < 8 ? 0.8 : 2));
			double d = 10 + r.nextDouble() * 6;
			int x = Mth.floor(p.getX() + Math.cos(a) * d), z = Mth.floor(p.getZ() + Math.sin(a) * d);
			int y = l.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
			if (Math.abs(y - p.getY()) > 6) continue;
			BlockPos below = new BlockPos(x, y - 1, z);
			if (!l.getFluidState(below).isEmpty() && !l.getBlockState(below).isFaceSturdy(l, below, net.minecraft.core.Direction.UP)) {
				if (!l.getBiome(below).is(BiomeTags.IS_OCEAN) && !l.getBiome(below).is(BiomeTags.IS_BEACH)) continue;
			}
			Vec3 at = new Vec3(x + 0.5, y, z + 0.5);
			if (l.noCollision(type.getSpawnAABB(at.x, at.y, at.z))) return at;
		}
		return null;
	}

	// ---------------------------------------------------------------- it falls

	private static void died(LivingDeathEvent e) {
		if (!(e.getEntity() instanceof Mob m) || !(m.level() instanceof ServerLevel l) || !m.getTags().contains(TAG)) return;
		LIVE.removeIf(v -> v.mob == m);
		String kind = BuiltInRegistries.ENTITY_TYPE.getKey(m.getType()).getPath();
		int rank = Mth.clamp(m.getPersistentData().getInt(RANK), 0, Ranks.LADDER.length() - 1);
		RandomSource r = l.getRandom();
		for (ServerPlayer p : l.getEntitiesOfClass(ServerPlayer.class, m.getBoundingBox().inflate(64), Player::isAlive)) {
			List<ItemStack> spoils = spoils(p, kind, rank, r);
			String got = Dropped.rain(l, p, spoils, r);
			int coins = Errands.pay(rank)[0] * 3;
			Coins.give(p, coins);
			Coins.setFlag(p, "world_boss_" + kind);
			p.sendSystemMessage(Component.literal("  ").append(m.getDisplayName()).append(Component.literal(" falls.  +" + coins + " coins" + got))
					.withStyle(ChatFormatting.YELLOW));
			p.playNotifySound(SoundEvents.UI_TOAST_CHALLENGE_COMPLETE, SoundSource.PLAYERS, 1f, 1f);
		}
	}

	/** one player's spoils from a world boss of this rank */
	static List<ItemStack> spoils(ServerPlayer p, String kind, int rank, RandomSource r) {
		List<ItemStack> out = new ArrayList<>();
		for (int i = 0; i < 3; i++) out.add(new ItemStack(Ranks.find(p, r)));
		Gear.Dungeon d = Adventurers.any(Adventurers.dungeons(Ranks.LADDER.charAt(rank)), r);
		if (d != null)
			for (String mat : d.mats()) {
				Item it = Gear.item(mat);
				if (it != null) out.add(new ItemStack(it, 2 + r.nextInt(3)));
			}
		if (r.nextFloat() < 0.6f) {
			Item w = WorldArms.pick(r, rank + 2);
			if (w != null) out.add(new ItemStack(w));
		}
		ItemStack trophy = Trophies.of(kind);
		if (!trophy.isEmpty()) out.add(trophy);
		out.addAll(Chains.extra(p, "boss:" + kind));
		return out;
	}

	// ---------------------------------------------------------------- nothing holds it (11/7: two trees held the Hart Lord, cheesed for ever)

	/** Every quarter second: whatever stands in the boss's way at its height, where it's walking or toward what it hunts, it
	 *  smashes (trees, walls, earth; never bedrock, obsidian and the like, or anything that holds things). */
	private static void clear(Mob m) {
		if (!(m.level() instanceof ServerLevel l)) return;
		var target = m.getTarget();
		var move = m.getDeltaMovement();
		net.minecraft.world.phys.Vec3 way = target != null ? target.position().subtract(m.position()) : new net.minecraft.world.phys.Vec3(move.x, 0, move.z);
		way = new net.minecraft.world.phys.Vec3(way.x, 0, way.z);
		boolean pushing = m.horizontalCollision || target != null && way.length() > m.getBbWidth() && move.horizontalDistanceSqr() < 0.0004;
		if (!pushing || way.lengthSqr() < 1e-4) return;
		way = way.normalize();
		var box = m.getBoundingBox().move(way.x * 1.2, 0, way.z * 1.2).inflate(0.4, 0, 0.4);
		int broke = 0;
		for (BlockPos at : BlockPos.betweenClosed(BlockPos.containing(box.minX, box.minY + 0.6, box.minZ), BlockPos.containing(box.maxX, box.maxY + 1, box.maxZ))) {
			if (broke >= 30) break;
			var st = l.getBlockState(at);
			if (st.isAir() || !st.getFluidState().isEmpty() && st.getBlock() instanceof net.minecraft.world.level.block.LiquidBlock) continue;
			float hard = st.getDestroySpeed(l, at);
			if (hard < 0 || hard >= 20 || l.getBlockEntity(at) != null) continue;
			l.destroyBlock(at, false, m);
			broke++;
		}
		if (broke > 0) l.playSound(null, m.blockPosition(), SoundEvents.ZOMBIE_BREAK_WOODEN_DOOR, SoundSource.HOSTILE, 1.2f, 0.6f);
	}

	// ---------------------------------------------------------------- left alone, it goes home

	private static void tick(ServerTickEvent.Post e) {
		if (e.getServer().getTickCount() % 5 == 0) for (Live v : LIVE) if (!v.mob.isRemoved() && v.mob.isAlive()) clear(v.mob);
		if (e.getServer().getTickCount() % 20 != 0 || LIVE.isEmpty()) return;
		for (var it = LIVE.iterator(); it.hasNext();) {
			Live v = it.next();
			if (v.mob.isRemoved() || !v.mob.isAlive()) {
				it.remove();
				continue;
			}
			ServerLevel l = (ServerLevel) v.mob.level();
			boolean near = !l.getEntitiesOfClass(ServerPlayer.class, v.mob.getBoundingBox().inflate(GONE), Player::isAlive).isEmpty();
			long now = l.getGameTime();
			if (near) v.alone = -1;
			else if (v.alone < 0) v.alone = now;
			else if (now - v.alone > IDLE) {
				l.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, v.mob.getX(), v.mob.getY() + 1, v.mob.getZ(), 40, 2, 1, 2, 0.04);
				v.mob.discard();
				it.remove();
				ServerPlayer by = l.getServer().getPlayerList().getPlayer(v.by);
				if (by != null) {
					ItemStack back = new ItemStack(SUMMONS.get(v.boss.summon()).get());
					if (!by.getInventory().add(back)) by.drop(back, false);
					by.sendSystemMessage(Component.literal("Nobody stayed to face it, so it went back. You still have the summon.")
							.withStyle(ChatFormatting.GRAY));
				}
			}
		}
	}

	// ---------------------------------------------------------------- testing

	private static void commands(RegisterCommandsEvent e) {
		e.getDispatcher().register(Commands.literal("ashbound").requires(c -> c.hasPermission(2)).then(Commands.literal("worldboss")
				.then(Commands.argument("kind", com.mojang.brigadier.arguments.StringArgumentType.word()).executes(c -> {
					ServerPlayer p = c.getSource().getPlayerOrException();
					Boss b = of(com.mojang.brigadier.arguments.StringArgumentType.getString(c, "kind"));
					if (b == null) {
						c.getSource().sendFailure(Component.literal("cairn_giant, hart_lord, saltglass_hydra, ironback_scorpion or rime_lich"));
						return 0;
					}
					ItemStack s = new ItemStack(SUMMONS.get(b.summon()).get());
					if (!p.getInventory().add(s)) p.drop(s, false);
					c.getSource().sendSuccess(() -> Component.literal("Gave the summon for " + b.kind()), false);
					return 1;
				}))));
	}
}
