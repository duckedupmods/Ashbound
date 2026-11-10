package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import javax.annotation.Nullable;

import com.mojang.brigadier.arguments.StringArgumentType;

import net.minecraft.ChatFormatting;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.EventHooks;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.entity.EntityJoinLevelEvent;
import net.neoforged.neoforge.event.entity.living.LivingChangeTargetEvent;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * Wild encounters: now and then, out in the wilds (no roads), a party of players comes on a scene. A caravan under attack
 * (save it: the trader pays and sells to you), deserters who want a toll (pay, talk them down, or fight), a wounded hunter
 * to walk into the nearest town with things on your heels, a wandering duelist who wants one bout with your best,
 * to yielding, or a party that didn't make it: dead round a cold fire, what killed them still about, a torn map on one of them
 * (Treasure). Rolled per party of players (Party.fightKey), never per player; nothing of it is kept: whatever's left of a
 * scene when the world loads again is cleared away. Lines are adventurer_lines.json's "caravan_", "deserter_", "hunter_"
 * and "duel_" keys.
 */
final class Encounters {
	private Encounters() {}

	static final String TAG = "ashbound_encounter";
	static final List<String> KINDS = List.of("caravan", "deserters", "hunter", "duelist", "fallen");
	private static final double[] WEIGHT = {0.25, 0.2, 0.15, 0.2, 0.2};
	private static final String RANKS = "FEDCBAS";
	/** the first after 5 minutes out, then every 10 to 15; a scene lasts at most 10 minutes; gone once nobody's within 160 */
	private static final int FIRST = 6000, EVERY = 12000, MORE = 6000, RETRY = 1200, LAST = 12000, GONE = 160;
	/** how far off a scene's set: far enough not to see it appear, near enough to hear it */
	private static final int NEAR = 40, FAR = 70, CLOSE = 30;
	/** a hunter's only offered with a town this close; a duel's to yielding at this share of health */
	private static final int TOWN_NEAR = 700;
	private static final float YIELD = 0.15f, FIND = 0.5f;
	private static final List<String> WARES = List.of("trade_general", "alchemist", "trade_smith", "trade_books");
	private static final List<String> MEN = List.of("footpad", "knife_dancer", "hedge_hexer");
	private static final Map<Object, Long> NEXT = new HashMap<>();
	static final List<Scene> LIVE = new ArrayList<>();

	// ---------------------------------------------------------------- a scene

	abstract static class Scene {
		final String kind, id = UUID.randomUUID().toString().substring(0, 8);
		final ServerLevel l;
		final BlockPos at;
		final int rank, players;
		@Nullable
		final Object group;
		final long born;
		final List<UUID> ents = new ArrayList<>();
		long endAt = -1;
		boolean over;

		Scene(String kind, ServerLevel l, BlockPos at, int rank, int players, @Nullable Object group) {
			this.kind = kind;
			this.l = l;
			this.at = at;
			this.rank = Math.max(0, Math.min(6, rank));
			this.players = Math.max(1, players);
			this.group = group;
			this.born = l.getGameTime();
		}

		/** Put it there; false if it can't be (and whatever was made is cleared). */
		abstract boolean start(RandomSource r);

		/** Once a second. */
		abstract void tick(RandomSource r);

		char rankChar() {
			return RANKS.charAt(rank);
		}

		String tag() {
			return TAG + ":" + id;
		}

		@Nullable
		Entity get(@Nullable UUID u) {
			return u == null ? null : l.getEntity(u);
		}

		<T extends Entity> T keep(T e) {
			e.addTag(TAG);
			e.addTag(tag());
			ents.add(e.getUUID());
			return e;
		}

		List<ServerPlayer> near(double r) {
			List<ServerPlayer> out = new ArrayList<>();
			for (ServerPlayer p : l.players()) if (!p.isSpectator() && p.distanceToSqr(Vec3.atCenterOf(at)) < r * r) out.add(p);
			return out;
		}

		void end() {
			if (over) return;
			over = true;
			for (UUID u : ents) {
				Entity e = l.getEntity(u);
				if (e != null && e.isAlive() && !(e instanceof Player)) e.discard();
			}
		}

		/** Paid out to each player near, by the scene's rank: coin, Guild Points if registered, and as often as not a find. */
		void pay(Iterable<ServerPlayer> who, double mul, String from, String line) {
			int[] pay = Errands.pay(rank);
			for (ServerPlayer p : who) {
				int coins = (int) Math.round(pay[0] * mul), gp = Guild.of(p).registered() ? (int) Math.round(pay[1] * mul) : 0;
				Coins.give(p, coins);
				if (gp > 0) Guild.points(p, gp);
				ItemStack gift = p.getRandom().nextFloat() < FIND ? new ItemStack(Ranks.find(p, p.getRandom())) : ItemStack.EMPTY;
				if (!gift.isEmpty()) p.getInventory().placeItemBackInInventory(gift.copy());
				say(p, from, line);
				p.sendSystemMessage(Component.literal("  +" + coins + " coins" + (gp > 0 ? ", +" + gp + " GP" : "") + (gift.isEmpty() ? "" : ", " + gift.getHoverName().getString()))
						.withStyle(ChatFormatting.YELLOW));
			}
		}
	}

	static void say(ServerPlayer p, String who, String line) {
		p.sendSystemMessage(Component.literal(who + ": ").withStyle(ChatFormatting.GOLD).append(Component.literal(line).withStyle(ChatFormatting.WHITE)));
	}

	/** One of a key's lines, filled in. */
	static String line(String key, Map<String, String> more, RandomSource r) {
		List<String> l = AdventurerTalk.LINES.getOrDefault(key, List.of());
		if (l.isEmpty()) return "";
		String s = l.get(r.nextInt(l.size()));
		for (var e : more.entrySet()) s = s.replace("{" + e.getKey() + "}", e.getValue());
		return s;
	}

	@Nullable
	static Mob monster(ServerLevel l, String id, BlockPos near, double far, RandomSource r) {
		var type = BuiltInRegistries.ENTITY_TYPE.getOptional(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, id)).orElse(null);
		if (type == null || !(type.create(l) instanceof Mob m)) return null;
		double a = r.nextDouble() * Math.PI * 2, d = far * (0.5 + 0.5 * r.nextDouble());
		BlockPos top = l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, near.offset((int) Math.round(Math.cos(a) * d), 0, (int) Math.round(Math.sin(a) * d)));
		m.moveTo(top.getX() + 0.5, top.getY(), top.getZ() + 0.5, r.nextFloat() * 360f, 0);
		EventHooks.finalizeMobSpawn(m, l, l.getCurrentDifficultyAt(top), MobSpawnType.EVENT, null);
		m.setPersistenceRequired();
		return m;
	}

	/** One of the adventurers on their own: someone of a party near this rank, in one of these roles if there's one. */
	@Nullable
	static Adventurer loner(ServerLevel l, BlockPos at, int rank, List<String> roles, RandomSource r) {
		List<Adventurers.Party> pool = Adventurers.PARTIES.stream().filter(p -> Math.abs(RANKS.indexOf(p.rank()) - rank) <= 1).toList();
		if (pool.isEmpty()) pool = Adventurers.PARTIES;
		if (pool.isEmpty()) return null;
		Adventurers.Party p = pool.get(r.nextInt(pool.size()));
		List<Adventurers.Member> fit = p.members().stream().filter(m -> roles.contains(m.role())).toList();
		if (fit.isEmpty()) fit = p.members();
		Adventurers.Member m = fit.get(r.nextInt(fit.size()));
		List<Adventurer> made = Adventurers.spawn(l, at, new Adventurers.Party(p.name(), RANKS.charAt(rank), p.colour(), List.of(m)));
		if (made.isEmpty()) return null;
		Adventurer a = made.get(0);
		a.ask = "";
		a.mode = "post";
		a.home = a.blockPosition();
		a.stay = -1;
		return a;
	}

	// ---------------------------------------------------------------- a caravan under attack

	static final class Caravan extends Scene {
		@Nullable
		UUID trader;
		final List<UUID> foes = new ArrayList<>(), guards = new ArrayList<>();
		boolean heard, saved;

		Caravan(ServerLevel l, BlockPos at, int rank, int players, @Nullable Object group) {
			super("caravan", l, at, rank, players, group);
		}

		@Override
		boolean start(RandomSource r) {
			float yaw = r.nextFloat() * 360f;
			Wagon w = Intro.WAGON.get().create(l);
			if (w == null) return false;
			w.moveTo(at.getX() + 0.5, at.getY(), at.getZ() + 0.5, yaw, 0);
			w.setYRot(yaw);
			l.addFreshEntity(keep(w));
			double side = Math.toRadians(yaw + 90);
			Npc n = Talk.spawn(l, "@townsfolk", WARES.get(r.nextInt(WARES.size())), "stand", at.getX() + 0.5 + Math.cos(side) * 3, at.getY(), at.getZ() + 0.5 + Math.sin(side) * 3, yaw);
			if (n != null) trader = keep(n).getUUID();
			// whoever they hired to guard it: a party a little under the players'
			int gr = Math.max(0, rank - 1);
			List<Adventurers.Party> hired = Adventurers.PARTIES.stream().filter(p -> RANKS.indexOf(p.rank()) <= gr).toList();
			if (hired.isEmpty()) hired = Adventurers.PARTIES;
			List<Adventurer> gs = hired.isEmpty() ? List.of() : Adventurers.spawn(l, at.offset(-(int) Math.round(Math.cos(side) * 3), 0, -(int) Math.round(Math.sin(side) * 3)), hired.get(r.nextInt(hired.size())), 3);
			for (Adventurer g : gs) {
				keep(g);
				g.ask = "";
				g.mode = "post";
				g.home = at;
				g.stay = -1;
				guards.add(g.getUUID());
			}
			Gear.Dungeon d = Adventurers.any(Adventurers.dungeons(rankChar()), r);
			if (d == null) {
				end();
				return false;
			}
			int count = 3 + Math.min(3, players - 1) + r.nextInt(2);
			for (int k = 0; k < count; k++) {
				Mob m = monster(l, Adventurers.any(d.mobs(), r), at, 9, r);
				if (m == null || !l.addFreshEntity(keep(m))) continue;
				foes.add(m.getUUID());
				if (!gs.isEmpty()) {
					Adventurer g = gs.get(r.nextInt(gs.size()));
					m.setTarget(g);
					g.setTarget(m);
				}
			}
			if (foes.isEmpty()) {
				end();
				return false;
			}
			return true;
		}

		@Override
		void tick(RandomSource r) {
			if (!heard && !near(80).isEmpty()) {
				heard = true;
				for (ServerPlayer p : near(80)) p.displayClientMessage(Component.literal(line("caravan_hear", Map.of(), r)).withStyle(ChatFormatting.GRAY), true);
			}
			boolean left = foes.stream().map(this::get).anyMatch(e -> e != null && e.isAlive());
			if (!left && !saved) {
				saved = true;
				Entity t = get(trader);
				List<ServerPlayer> who = near(48);
				// nobody came: the guards saw them off on their own, or didn't
				if (!who.isEmpty()) pay(who, 1.0, t == null ? "The trader" : t.getName().getString(), line("caravan_thanks", Map.of(), r));
				endAt = l.getGameTime() + 2400;
			}
		}
	}

	// ---------------------------------------------------------------- deserters at a toll

	static final class Deserters extends Scene {
		@Nullable
		UUID boss;
		final List<UUID> men = new ArrayList<>();
		boolean parley = true, warned, gone, paid;
		int toll;

		Deserters(ServerLevel l, BlockPos at, int rank, int players, @Nullable Object group) {
			super("deserters", l, at, rank, players, group);
		}

		@Override
		boolean start(RandomSource r) {
			toll = Math.max(5, (int) Math.round(Errands.pay(rank)[0] * 0.8 * (0.8 + 0.1 * players)));
			List<String> who = new ArrayList<>();
			who.add("bandit_lieutenant");
			int n = 2 + Math.min(3, players - 1);
			for (int k = 0; k < n; k++) who.add(MEN.get(r.nextInt(MEN.size())));
			if (rank >= 3 || players >= 4) who.add("gorge_ogre");
			for (int k = 0; k < who.size(); k++) {
				Mob m = monster(l, who.get(k), at, k == 0 ? 0 : 5, r);
				if (m == null) continue;
				Balance.atRank(m, who.get(k), String.valueOf(rankChar()));
				if (m instanceof PathfinderMob pm) pm.restrictTo(at, 6);
				if (!l.addFreshEntity(keep(m))) continue;
				men.add(m.getUUID());
				if (k == 0) boss = m.getUUID();
			}
			if (boss == null) {
				end();
				return false;
			}
			return true;
		}

		String bossName() {
			Entity b = get(boss);
			return b == null ? "The deserter" : b.getName().getString();
		}

		@Override
		void tick(RandomSource r) {
			if (!warned && !near(16).isEmpty()) {
				warned = true;
				for (ServerPlayer p : near(32)) say(p, bossName(), line("deserter_warn", Map.of("toll", String.valueOf(toll)), r));
			}
			boolean left = men.stream().map(this::get).anyMatch(e -> e != null && e.isAlive());
			if (!left && !paid && !gone) {
				paid = true;
				List<ServerPlayer> who = near(48);
				if (!who.isEmpty()) pay(who, 1.2, "Their purse", line("deserter_purse", Map.of(), r));
				endAt = l.getGameTime() + 600;
			}
		}

		/** Steel, then: they come for whoever's nearest. */
		void fight() {
			if (!parley) return;
			parley = false;
			for (UUID u : men)
				if (get(u) instanceof Mob m) {
					if (m instanceof PathfinderMob pm) pm.clearRestriction();
					Player p = l.getNearestPlayer(m, 32);
					if (p != null && !p.isCreative()) m.setTarget(p);
				}
		}

		/** Paid or talked down: they take themselves off, and are gone. */
		void leave() {
			parley = false;
			gone = true;
			for (UUID u : men)
				if (get(u) instanceof Mob m) {
					if (m instanceof PathfinderMob pm) pm.clearRestriction();
					Vec3 away = m.position().subtract(Vec3.atCenterOf(at)).normalize().scale(30);
					m.getNavigation().moveTo(m.getX() + away.x, m.getY(), m.getZ() + away.z, 1.0);
				}
			endAt = l.getGameTime() + 200;
		}
	}

	// ---------------------------------------------------------------- a wounded hunter

	static final class Hunter extends Scene {
		@Nullable
		UUID hunter, with;
		@Nullable
		Capital.Site town;
		int waves;
		long nextWave;
		boolean called, safe, lost;

		Hunter(ServerLevel l, BlockPos at, int rank, int players, @Nullable Object group) {
			super("hunter", l, at, rank, players, group);
		}

		@Override
		boolean start(RandomSource r) {
			double best = TOWN_NEAR;
			for (Capital.Site s : Capital.sites) {
				double d = Math.hypot(s.x - at.getX(), s.z - at.getZ());
				if (d < best) {
					best = d;
					town = s;
				}
			}
			if (town == null) return false;
			Adventurer a = loner(l, at, Math.max(0, rank - 1), List.of("ranger", "rogue", "striker"), r);
			if (a == null) return false;
			keep(a);
			a.wounded = true;
			a.setHealth(a.getMaxHealth() * 0.3f);
			hunter = a.getUUID();
			return true;
		}

		@Override
		void tick(RandomSource r) {
			if (!(get(hunter) instanceof Adventurer a) || !a.isAlive()) {
				if (!lost && with != null && l.getPlayerByUUID(with) instanceof ServerPlayer p)
					p.sendSystemMessage(Component.literal(line("hunter_lost", Map.of(), r)).withStyle(ChatFormatting.GRAY));
				lost = true;
				end();
				return;
			}
			if (!called && l.getNearestPlayer(a, 10) != null) {
				called = true;
				a.bark("hunter_help", null, Map.of(), true);
			}
			if (with == null || safe) return;
			if (Adventurers.town(a.blockPosition()) != null) {
				safe = true;
				a.escort = null;
				a.wounded = false;
				a.mode = "post";
				a.home = a.blockPosition();
				List<ServerPlayer> who = new ArrayList<>();
				for (ServerPlayer p : l.players()) if (p.distanceTo(a) < 48) who.add(p);
				pay(who, 1.5, a.getName().getString(), line("hunter_safe", Map.of(), r));
				endAt = l.getGameTime() + 1200;
				return;
			}
			// things on your heels: a few, from behind, out of sight
			long now = l.getGameTime();
			if (now >= nextWave && waves < 4) {
				waves++;
				nextWave = now + 600 + r.nextInt(300);
				Gear.Dungeon d = Adventurers.any(Adventurers.dungeons(rankChar()), r);
				BlockPos from = d == null ? null : Adventurers.out(l, a.position(), 22, 32, 16, r);
				if (from == null) return;
				int n = 2 + (players > 2 ? 1 : 0);
				for (int k = 0; k < n; k++) {
					Mob m = monster(l, Adventurers.any(d.mobs(), r), from, 3, r);
					if (m == null || !l.addFreshEntity(keep(m))) continue;
					m.setTarget(a);
				}
				for (ServerPlayer p : l.players()) if (p.distanceTo(a) < 48) p.displayClientMessage(Component.literal(line("hunter_wave", Map.of(), r)).withStyle(ChatFormatting.RED), true);
			}
		}
	}

	// ---------------------------------------------------------------- a wandering duelist

	static final class Duelist extends Scene {
		@Nullable
		UUID duelist;
		boolean called, done;

		Duelist(ServerLevel l, BlockPos at, int rank, int players, @Nullable Object group) {
			super("duelist", l, at, rank, players, group);
		}

		@Override
		boolean start(RandomSource r) {
			Adventurer a = loner(l, at, Math.min(6, rank + 1), List.of("striker", "lancer", "rogue", "breaker"), r);
			if (a == null) return false;
			keep(a);
			duelist = a.getUUID();
			return true;
		}

		@Override
		void tick(RandomSource r) {
			if (!(get(duelist) instanceof Adventurer a) || !a.isAlive()) {
				end();
				return;
			}
			if (!called && l.getNearestPlayer(a, 12) != null) {
				called = true;
				a.bark("duel_call", l.getNearestPlayer(a, 12), Map.of(), true);
			}
			// whoever took them on walked off: it's off
			if (a.duel != null && !(l.getPlayerByUUID(a.duel) instanceof Player p && p.isAlive() && p.distanceTo(a) < 32)) {
				a.duel = null;
				a.setTarget(null);
			}
		}
	}

	// ---------------------------------------------------------------- a fallen party

	static final class Fallen extends Scene {
		final List<UUID> dead = new ArrayList<>(), foes = new ArrayList<>();
		final java.util.Set<UUID> searched = new java.util.HashSet<>();
		/** the one with the map on them */
		@Nullable
		UUID holder;
		String party = "", gate = "";
		/** what's left of their camp, taken away with them */
		final List<BlockPos> placed = new ArrayList<>();
		boolean heard;

		Fallen(ServerLevel l, BlockPos at, int rank, int players, @Nullable Object group) {
			super("fallen", l, at, rank, players, group);
		}

		@Override
		boolean start(RandomSource r) {
			Gear.Dungeon d = Adventurers.any(Adventurers.dungeons(rankChar()), r);
			List<Adventurers.Party> pool = Adventurers.PARTIES.stream().filter(p -> Math.abs(RANKS.indexOf(p.rank()) - rank) <= 1).toList();
			if (pool.isEmpty()) pool = Adventurers.PARTIES;
			if (d == null || pool.isEmpty()) return false;
			gate = d.gate();
			Adventurers.Party p = pool.get(r.nextInt(pool.size()));
			party = p.name();
			List<Adventurer> made = Adventurers.spawn(l, at, new Adventurers.Party(p.name(), rankChar(), p.colour(), p.members()), 2 + r.nextInt(3));
			if (made.isEmpty()) return false;
			for (Adventurer a : made) {
				keep(a);
				a.ask = "";
				a.mode = "post";
				a.home = at;
				a.stay = -1;
				// where each fell: round the fire, a few steps out, now and then one further off (they ran)
				double ang = r.nextDouble() * Math.PI * 2, far = 1.8 + r.nextDouble() * (r.nextFloat() < 0.3f ? 4 : 2);
				BlockPos to = l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, at.offset((int) Math.round(Math.cos(ang) * far), 0, (int) Math.round(Math.sin(ang) * far)));
				float yaw = r.nextFloat() * 360f;
				a.moveTo(to.getX() + 0.5, to.getY(), to.getZ() + 0.5, yaw, 0);
				a.setYBodyRot(yaw);
				a.setYHeadRot(yaw);
				a.fallDown(1 + r.nextInt(3));
				dead.add(a.getUUID());
			}
			holder = dead.get(r.nextInt(dead.size()));
			// the cold fire and their tent
			put(at, block("dead_campfire", net.minecraft.world.level.block.Blocks.CAMPFIRE.defaultBlockState().setValue(net.minecraft.world.level.block.CampfireBlock.LIT, false)));
			double side = r.nextDouble() * Math.PI * 2;
			BlockPos tent = l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, at.offset((int) Math.round(Math.cos(side) * 4), 0, (int) Math.round(Math.sin(side) * 4)));
			net.minecraft.world.level.block.state.BlockState ts = block("bandit_tent", null);
			if (ts != null) put(tent, facing(ts, net.minecraft.core.Direction.Plane.HORIZONTAL.getRandomDirection(r)));
			// what killed them, most times still about
			if (r.nextFloat() < 0.75f) {
				int n = 2 + Math.min(3, players - 1) + r.nextInt(2);
				for (int k = 0; k < n; k++) {
					String id = Adventurers.any(d.mobs(), r);
					Mob m = monster(l, id, at, 12, r);
					if (m == null) continue;
					Balance.atRank(m, id, String.valueOf(rankChar()));
					if (m instanceof PathfinderMob pm) pm.restrictTo(at, 14);
					if (l.addFreshEntity(keep(m))) foes.add(m.getUUID());
				}
			}
			return true;
		}

		private static net.minecraft.world.level.block.state.BlockState block(String id, net.minecraft.world.level.block.state.BlockState fallback) {
			var b = BuiltInRegistries.BLOCK.getOptional(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, id)).orElse(null);
			return b == null ? fallback : b.defaultBlockState();
		}

		private static net.minecraft.world.level.block.state.BlockState facing(net.minecraft.world.level.block.state.BlockState s, net.minecraft.core.Direction d) {
			var f = net.minecraft.world.level.block.state.properties.BlockStateProperties.HORIZONTAL_FACING;
			return s.hasProperty(f) ? s.setValue(f, d) : s;
		}

		private void put(BlockPos p, @Nullable net.minecraft.world.level.block.state.BlockState s) {
			if (s == null || !l.getBlockState(p).canBeReplaced() || l.getBlockState(p.below()).getCollisionShape(l, p.below()).isEmpty()) return;
			l.setBlock(p, s, 3);
			placed.add(p);
		}

		boolean foesNear(Entity by, double r) {
			return foes.stream().map(this::get).anyMatch(e -> e instanceof LivingEntity le && le.isAlive() && le.distanceTo(by) < r);
		}

		@Override
		void tick(RandomSource r) {
			if (!heard && !near(64).isEmpty()) {
				heard = true;
				for (ServerPlayer p : near(64)) p.displayClientMessage(Component.literal(line("fallen_hear", Map.of(), r)).withStyle(ChatFormatting.GRAY), true);
			}
			// the last of the smoke off their fire (smoke only: nothing burns)
			if (!placed.isEmpty() && !near(64).isEmpty())
				l.sendParticles(net.minecraft.core.particles.ParticleTypes.CAMPFIRE_COSY_SMOKE, at.getX() + 0.5, at.getY() + 0.4, at.getZ() + 0.5, 1, 0.15, 0.05, 0.15, 0.005);
			if (endAt < 0 && searched.size() >= dead.size()) endAt = l.getGameTime() + 2400;
		}

		/** Gone with them: their fire and tent. */
		@Override
		void end() {
			if (over) return;
			super.end();
			for (BlockPos p : placed) {
				var s = l.getBlockState(p);
				if (BuiltInRegistries.BLOCK.getKey(s.getBlock()).getNamespace().equals(Ashbound.ID) || s.is(net.minecraft.world.level.block.Blocks.CAMPFIRE))
					l.removeBlock(p, false);
			}
		}

		/** Turning one of them over: a few coins, now and then something they wore, and the map on whoever had it. Not with
		 * what killed them still close. */
		void search(ServerPlayer p, Adventurer a) {
			RandomSource r = p.getRandom();
			if (foesNear(a, 24)) {
				p.displayClientMessage(Component.literal(line("fallen_foes", Map.of(), r)).withStyle(ChatFormatting.RED), true);
				return;
			}
			if (!searched.add(a.getUUID())) {
				p.displayClientMessage(Component.literal("Nothing more on " + a.getName().getString() + ".").withStyle(ChatFormatting.GRAY), true);
				return;
			}
			String who = a.getName().getString();
			p.sendSystemMessage(Component.literal(line("fallen_search", Map.of("who", who, "party", AdventurerTalk.the(party, false)), r)).withStyle(ChatFormatting.GRAY));
			int coins = Math.max(1, (int) Math.round(Errands.pay(rank)[0] * 0.3 * (0.5 + r.nextDouble())));
			Coins.give(p, coins);
			StringBuilder b = new StringBuilder("  +" + coins + " coins");
			if (r.nextFloat() < 0.35f) {
				List<EquipmentSlot> worn = new ArrayList<>();
				for (EquipmentSlot s : new EquipmentSlot[] {EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET, EquipmentSlot.MAINHAND})
					if (!a.getItemBySlot(s).isEmpty()) worn.add(s);
				if (!worn.isEmpty()) {
					EquipmentSlot s = worn.get(r.nextInt(worn.size()));
					ItemStack it = a.getItemBySlot(s).copy();
					a.setItemSlot(s, ItemStack.EMPTY);
					p.getInventory().placeItemBackInInventory(it.copy());
					b.append(", ").append(it.getHoverName().getString());
				}
			}
			if (a.getUUID().equals(holder)) {
				p.getInventory().placeItemBackInInventory(Treasure.map(l, at, rank, gate, party, r, Treasure.NEAR, Treasure.FAR));
				p.sendSystemMessage(Component.literal(line("fallen_map", Map.of("who", who), r)).withStyle(ChatFormatting.GOLD));
				b.append(", a torn map");
			}
			p.sendSystemMessage(Component.literal(b.toString()).withStyle(ChatFormatting.YELLOW));
			l.playSound(null, a.getX(), a.getY(), a.getZ(), net.minecraft.sounds.SoundEvents.ARMOR_EQUIP_LEATHER.value(), net.minecraft.sounds.SoundSource.PLAYERS, 0.8f, 0.8f);
		}
	}

	// ---------------------------------------------------------------- talking

	private record Session(int entity, Scene scene, List<String> acts) {}

	private static final Map<UUID, Session> SESSIONS = new HashMap<>();

	@Nullable
	static Scene of(Entity e) {
		for (Scene s : LIVE) if (!s.over && s.ents.contains(e.getUUID())) return s;
		return null;
	}

	private static void send(ServerPlayer p, Entity e, Scene s, String title, String text, List<String> labels, List<String> acts) {
		SESSIONS.put(p.getUUID(), new Session(e.getId(), s, acts));
		PacketDistributor.sendToPlayer(p, new Net.NpcTalk(e.getId(), e.getName().getString(), title, text, labels));
	}

	private static void close(ServerPlayer p) {
		if (SESSIONS.remove(p.getUUID()) != null) PacketDistributor.sendToPlayer(p, new Net.NpcTalk(-1, "", "", "", List.of()));
	}

	/** Talking to an adventurer who's part of a scene (the hunter, the duelist): true if it's ours to answer (AdventurerTalk.open asks). */
	static boolean talk(ServerPlayer p, Adventurer a) {
		Scene s = of(a);
		RandomSource r = p.getRandom();
		if (s instanceof Hunter h) {
			if (h.safe) a.bark("hunter_after", p, Map.of(), true);
			else if (h.with != null) a.bark("hunter_on", p, Map.of(), true);
			else {
				Map<String, String> w = new HashMap<>();
				double dx = h.town.x - a.getX(), dz = h.town.z - a.getZ();
				String[] dirs = {"east", "south-east", "south", "south-west", "west", "north-west", "north", "north-east"};
				w.put("dir", dirs[Math.floorMod((int) Math.round(Math.atan2(dz, dx) / (Math.PI / 4)), 8)]);
				w.put("far", String.valueOf(Math.max(50, Math.round(Math.hypot(dx, dz) / 50) * 50)));
				w.put("town", h.town.title);
				send(p, a, s, "wounded, of the " + a.partyName, line("hunter_ask", w, r), List.of("I'll get you there.", "I can't, I'm sorry."), List.of("escort", "no"));
			}
			return true;
		}
		if (s instanceof Fallen f) {
			if (a.fallen() > 0) f.search(p, a);
			return true;
		}
		if (s instanceof Duelist d) {
			if (d.done) a.bark("bye", p, Map.of(), true);
			else if (a.duel != null) a.bark("duel_on", p, Map.of(), true);
			else send(p, a, s, a.rank() + "-rank duelist", AdventurerTalk.line("duel_ask", a, p, Map.of(), r), List.of("Accept the duel.", "Not today."), List.of("duel", "no"));
			return true;
		}
		return s != null;
	}

	/** Right-click on the deserters' captain. */
	private static void interact(PlayerInteractEvent.EntityInteract e) {
		if (!(e.getEntity() instanceof ServerPlayer p) || e.getHand() != net.minecraft.world.InteractionHand.MAIN_HAND) return;
		if (!(of(e.getTarget()) instanceof Deserters d) || !e.getTarget().getUUID().equals(d.boss)) return;
		e.setCanceled(true);
		if (!d.parley) return;
		RandomSource r = p.getRandom();
		List<String> labels = new ArrayList<>(), acts = new ArrayList<>();
		if (Coins.of(p) >= d.toll) {
			labels.add("Pay the toll (" + d.toll + " coins).");
			acts.add("toll");
		}
		labels.add("Talk them down.");
		acts.add("talk");
		labels.add("Draw steel.");
		acts.add("fight");
		send(p, e.getTarget(), d, "Guild deserters", line("deserter_ask", Map.of("toll", String.valueOf(d.toll)), r), labels, acts);
	}

	/** An option picked on the talk screen: true if it was one of ours (Talk.onPick asks). */
	static boolean pick(Net.NpcPick msg, ServerPlayer p) {
		Session s = SESSIONS.get(p.getUUID());
		if (s == null || s.entity() != msg.entity()) return false;
		Entity e = p.level().getEntity(msg.entity());
		if (e == null || s.scene().over || e.distanceTo(p) > 10 || msg.option() < 0 || msg.option() >= s.acts().size()) {
			if (msg.option() < 0) SESSIONS.remove(p.getUUID());
			else close(p);
			return true;
		}
		RandomSource r = p.getRandom();
		String act = s.acts().get(msg.option());
		close(p);
		switch (s.scene()) {
			case Deserters d -> {
				if (!d.parley) return true;
				switch (act) {
					case "toll" -> {
						if (Coins.pay(p, d.toll)) {
							for (ServerPlayer o : d.near(32)) say(o, d.bossName(), line("deserter_paid", Map.of(), r));
							d.leave();
						} else d.fight();
					}
					case "talk" -> {
						// more of you, and higher than they'd like: the likelier they back off
						float chance = 0.3f + 0.1f * Math.min(4, d.near(32).size()) + 0.1f * Math.max(0, Ranks.party(p) - d.rank);
						boolean ok = r.nextFloat() < chance;
						for (ServerPlayer o : d.near(32)) say(o, d.bossName(), line(ok ? "deserter_talked" : "deserter_failed", Map.of(), r));
						if (ok) d.leave();
						else d.fight();
					}
					default -> {
						for (ServerPlayer o : d.near(32)) say(o, d.bossName(), line("deserter_fight", Map.of(), r));
						d.fight();
					}
				}
			}
			case Hunter h -> {
				if (!(e instanceof Adventurer a)) return true;
				if (act.equals("escort") && h.with == null) {
					h.with = p.getUUID();
					a.escort = p.getUUID();
					a.mode = "escort";
					a.home = null;
					h.nextWave = h.l.getGameTime() + 300;
					a.bark("hunter_go", p, Map.of(), true);
				} else a.bark("hunter_no", p, Map.of(), true);
			}
			case Duelist d -> {
				if (!(e instanceof Adventurer a)) return true;
				if (act.equals("duel") && !d.done && a.duel == null) {
					a.duel = p.getUUID();
					a.home = null;
					a.mode = "duel";
					a.setTarget(p);
					a.bark("duel_start", p, Map.of(), true);
					p.displayClientMessage(Component.literal("Duel! To yielding: whoever drops under " + Math.round(YIELD * 100) + "% health loses.").withStyle(ChatFormatting.GOLD), true);
				} else a.bark("duel_no", p, Map.of(), true);
			}
			default -> {}
		}
		return true;
	}

	// ---------------------------------------------------------------- the duel

	/** A blow between a duelist and whoever took them on: true if it's the duel's (Adventurers.hurt then lets it land). Either drops
	 * under YIELD: the blow's stopped and the duel's over. */
	static boolean duel(LivingIncomingDamageEvent e, @Nullable Entity by) {
		if (e.getEntity() instanceof Adventurer a && a.duel != null && by instanceof ServerPlayer p && a.duel.equals(p.getUUID())) {
			if (a.getHealth() - e.getAmount() < a.getMaxHealth() * YIELD) {
				e.setCanceled(true);
				duelOver(a, p, true);
			}
			return true;
		}
		if (by instanceof Adventurer a && a.duel != null && e.getEntity() instanceof ServerPlayer p && a.duel.equals(p.getUUID())) {
			if (p.getHealth() - e.getAmount() < p.getMaxHealth() * YIELD) {
				e.setCanceled(true);
				duelOver(a, p, false);
			}
			return true;
		}
		return false;
	}

	static void duelOver(Adventurer a, ServerPlayer p, boolean won) {
		a.duel = null;
		a.setTarget(null);
		a.mode = "post";
		a.home = a.blockPosition();
		RandomSource r = p.getRandom();
		Scene s = of(a);
		if (s instanceof Duelist d) {
			d.done = true;
			d.endAt = d.l.getGameTime() + 600;
		}
		if (won) {
			a.bark("duel_yield", p, Map.of(), true);
			// their own blade: they said it'd be yours
			ItemStack blade = a.getMainHandItem().copy();
			if (!blade.isEmpty()) {
				a.setItemSlot(EquipmentSlot.MAINHAND, ItemStack.EMPTY);
				p.getInventory().placeItemBackInInventory(blade);
				p.sendSystemMessage(Component.literal(a.getName().getString() + " hands you their " + blade.getHoverName().getString() + ".").withStyle(ChatFormatting.GOLD));
			}
			int coins = (int) Math.round(Errands.pay(Math.max(0, "FEDCBAS".indexOf(a.rank())))[0] * 0.5);
			Coins.give(p, coins);
			p.sendSystemMessage(Component.literal("  +" + coins + " coins").withStyle(ChatFormatting.YELLOW));
		} else a.bark("duel_win", p, Map.of(), true);
	}

	// ---------------------------------------------------------------- where and when

	static Scene make(String kind, ServerLevel l, BlockPos at, int rank, int players, @Nullable Object group) {
		return switch (kind) {
			case "caravan" -> new Caravan(l, at, rank, players, group);
			case "deserters" -> new Deserters(l, at, rank, players, group);
			case "hunter" -> new Hunter(l, at, rank, players, group);
			case "fallen" -> new Fallen(l, at, rank, players, group);
			default -> new Duelist(l, at, rank, players, group);
		};
	}

	/** Set a scene going; null if it couldn't be. */
	@Nullable
	static Scene begin(String kind, ServerLevel l, BlockPos at, int rank, int players, @Nullable Object group, RandomSource r) {
		Scene s = make(kind, l, at, rank, players, group);
		if (!s.start(r)) {
			s.end();
			return null;
		}
		LIVE.add(s);
		return s;
	}

	private static String roll(RandomSource r) {
		double x = r.nextDouble(), sum = 0;
		for (int i = 0; i < KINDS.size(); i++) if (x < (sum += WEIGHT[i])) return KINDS.get(i);
		return KINDS.get(0);
	}

	private static void tick(ServerTickEvent.Post e) {
		var server = e.getServer();
		if (server.getTickCount() % 20 != 0) return;
		ServerLevel l = server.overworld();
		RandomSource r = l.getRandom();
		long now = l.getGameTime();
		for (Scene s : new ArrayList<>(LIVE)) {
			if (!s.over) {
				s.tick(r);
				boolean nobody = s.near(GONE).isEmpty();
				if (nobody || s.endAt >= 0 && now >= s.endAt || now - s.born > LAST && s.near(48).isEmpty()) s.end();
			}
			if (s.over) LIVE.remove(s);
		}
		if (server.getTickCount() % 100 != 0) return;
		Map<Object, List<ServerPlayer>> groups = new java.util.LinkedHashMap<>();
		for (ServerPlayer p : l.players()) if (!p.isSpectator()) groups.computeIfAbsent(com.snoringwalrus.ashbound.Party.fightKey(p), k -> new ArrayList<>()).add(p);
		for (var g : groups.entrySet()) {
			Object key = g.getKey();
			Long next = NEXT.get(key);
			if (next == null) {
				NEXT.put(key, now + FIRST + r.nextInt(MORE));
				continue;
			}
			if (now < next || LIVE.stream().anyMatch(s -> key.equals(s.group))) continue;
			ServerPlayer p = g.getValue().get(r.nextInt(g.getValue().size()));
			if (Adventurers.town(p.blockPosition()) != null || p.getY() < l.getSeaLevel() - 10) {
				NEXT.put(key, now + RETRY);
				continue;
			}
			int with = (int) g.getValue().stream().filter(o -> o.distanceTo(p) < 64).count();
			BlockPos at = Adventurers.out(l, p.position(), NEAR, FAR, CLOSE, r);
			Scene s = at == null || Adventurers.town(at) != null ? null : begin(roll(r), l, at, Ranks.party(p), with, key, r);
			NEXT.put(key, now + (s == null ? RETRY : EVERY + r.nextInt(MORE)));
		}
	}

	// ---------------------------------------------------------------- the rules

	/** Deserters parleying don't go for anyone. */
	private static void target(LivingChangeTargetEvent e) {
		if (e.getNewAboutToBeSetTarget() instanceof Player && of(e.getEntity()) instanceof Deserters d && d.parley) e.setCanceled(true);
	}

	/** Hit one of them while they're talking terms: that's your answer. */
	private static void struck(LivingIncomingDamageEvent e) {
		Entity by = e.getSource().getEntity();
		if (by instanceof Projectile pr) by = pr.getOwner();
		if (by instanceof Player && of(e.getEntity()) instanceof Deserters d && d.parley) d.fight();
	}

	/** Nothing of a scene outlives the session it was in. */
	private static void join(EntityJoinLevelEvent e) {
		if (e.loadedFromDisk() && e.getEntity().getTags().contains(TAG)) e.setCanceled(true);
	}

	private static void commands(RegisterCommandsEvent e) {
		var kind = Commands.argument("kind", StringArgumentType.word()).suggests((c, b) -> {
			KINDS.forEach(b::suggest);
			return b.buildFuture();
		});
		e.getDispatcher().register(Commands.literal("ashbound").requires(s -> s.hasPermission(2)).then(Commands.literal("encounter").then(kind.executes(c -> {
			ServerPlayer p = c.getSource().getPlayerOrException();
			String k = StringArgumentType.getString(c, "kind");
			if (!KINDS.contains(k)) {
				c.getSource().sendFailure(Component.literal("One of " + KINDS));
				return 0;
			}
			Vec3 look = p.getLookAngle().multiply(1, 0, 1).normalize().scale(20);
			BlockPos at = p.serverLevel().getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, BlockPos.containing(p.position().add(look)));
			Scene s = begin(k, p.serverLevel(), at, Ranks.party(p), 1, com.snoringwalrus.ashbound.Party.fightKey(p), p.getRandom());
			if (s == null) c.getSource().sendFailure(Component.literal("Couldn't set a " + k + " there" + (k.equals("hunter") ? " (no town within " + TOWN_NEAR + ")" : "")));
			else c.getSource().sendSuccess(() -> Component.literal("A " + k + " ahead"), false);
			return s == null ? 0 : 1;
		}))));
	}

	static void init() {
		NeoForge.EVENT_BUS.addListener(Encounters::tick);
		NeoForge.EVENT_BUS.addListener(Encounters::target);
		NeoForge.EVENT_BUS.addListener(Encounters::struck);
		NeoForge.EVENT_BUS.addListener(Encounters::join);
		NeoForge.EVENT_BUS.addListener(Encounters::interact);
		NeoForge.EVENT_BUS.addListener(Encounters::commands);
	}
}
