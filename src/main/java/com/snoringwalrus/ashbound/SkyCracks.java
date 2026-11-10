package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import javax.annotation.Nullable;

import com.mojang.brigadier.arguments.IntegerArgumentType;

import net.minecraft.ChatFormatting;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.entity.EntityJoinLevelEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;

/**
 * The gate storms (tools/blender/gate_storm.py is the look): now and then, for a party out in the wilds, a wild gate tears
 * open as a storm ahead of them. Dark cloud rolls in and turns round an eye (the gate itself, SkyCrack, lying face-down
 * under the clouds, the dungeon seen through it), rain falls and the light goes (client/StormSky), and lightning in the
 * gate's colour strikes round the party (StormStrike): a warning ring, the strike, a scorched patch (never fire: forests
 * stay standing) and the dungeon's own monsters climbing out of it. Storm spires (StormSpire), pillars of the dungeon's
 * blocks fed by the lightning, burst up round the eye and hold it open: break them all, then finish what came out of it, and
 * the storm collapses: coins and GP to everyone there, and a last strike beside each of them bursts their own loot out
 * of the ground (finds, the dungeon's mats, now and then one of its weapons). Left alone it blows itself out after
 * half an hour, or after 2.5 minutes with nobody within 500 blocks; what came out of it stays.
 * Rolled per party of players (Party.fightKey); nothing of it is kept across a restart.
 */
final class SkyCracks {
	private SkyCracks() {}

	static final String TAG = "ashbound_skycrack";
	/** the first after 20 to 30 minutes out, then every 40 to 60; it lasts at most 30 minutes, and ends after EMPTY ticks with nobody within FAR_GONE */
	private static final int FIRST = 24000, EVERY = 48000, MORE = 24000, RETRY = 3600, LIFE = 36000, FAR_GONE = 500, EMPTY = 3000;
	/** what came out of it still counts while it's within this of the eye (flat) */
	private static final int STRAY = 200;
	/** how high over the ground the eye is, and how far ahead of you it comes in */
	static final int HIGH = 64, NEAR = 70, FAR = 115;
	/** the ground under the storm (blocks out from the eye), and where its spires stand */
	static final int UNDER = 150, SPIRE_NEAR = 16, SPIRE_FAR = 32;
	/** strikes at the party every 30 seconds, a little faster each time; harmless ones off under the storm every 3 to 7 */
	private static final int WAVE = 600, WAVE_LEAST = 340, FAR_STRIKE = 60, FAR_MORE = 80;
	private static final String RANKS = "FEDCBAS";
	private static final Map<Object, Long> NEXT = new HashMap<>();
	static final Map<UUID, Crack> LIVE = new HashMap<>();

	/** One raging in the world: who it's for, what comes out of it, and how it's going. */
	static final class Crack {
		final int rank, players;
		@Nullable
		final Object group;
		final int anchors;
		final BlockPos ground;
		@Nullable
		final Gear.Dungeon dungeon;
		final List<String> monsters;
		long nextWave, nextFar, lastNear;
		int waves, placed, left;
		/** finishing: the spires are down, what came out of it is being put down */
		boolean won, raised, finishing;
		final List<UUID> spires = new ArrayList<>(), mobs = new ArrayList<>();

		Crack(int rank, int players, @Nullable Object group, BlockPos ground, @Nullable Gear.Dungeon dungeon) {
			this.rank = rank;
			this.players = Math.max(1, players);
			this.group = group;
			this.anchors = 3 + Math.min(3, this.players - 1);
			this.ground = ground;
			this.dungeon = dungeon;
			this.monsters = dungeon == null ? List.of() : dungeon.mobs();
		}
	}

	// ---------------------------------------------------------------- the storm coming in

	@Nullable
	static SkyCrack open(ServerLevel l, BlockPos ground, int rank, int players, @Nullable Object group, RandomSource r) {
		SkyCrack c = Gates.SKY_CRACK.get().create(l);
		if (c == null) return null;
		c.moveTo(ground.getX() + 0.5, ground.getY() + HIGH - GateEntity.MID, ground.getZ() + 0.5, r.nextFloat() * 360f, 0);
		// face-down under the clouds: you look up into it
		c.lay(r.nextFloat() * 360f, 90);
		c.setRank(Mth.clamp(rank, 0, 6));
		c.opened(l.getGameTime());
		c.addTag(TAG);
		if (!l.addFreshEntity(c)) return null;
		Crack k = new Crack(c.rank(), players, group, ground, dungeon(c, r));
		k.lastNear = l.getGameTime();
		k.nextWave = l.getGameTime() + GateEntity.CRACK + GateEntity.OPEN + 200;
		k.nextFar = l.getGameTime() + 40;
		LIVE.put(c.getUUID(), k);
		sound(l, c, SoundEvents.LIGHTNING_BOLT_THUNDER, 14f, 0.45f);
		sound(l, c, SoundEvents.WARDEN_SONIC_BOOM, 8f, 0.5f);
		for (ServerPlayer p : near(l, c, 400))
			p.displayClientMessage(Component.literal("A gate storm rolls in, " + dir(p, c.middle()) + "!").withStyle(ChatFormatting.RED, ChatFormatting.BOLD), true);
		return c;
	}

	/** The dungeon seen through its eye: its monsters climb out of the strikes, its mats are in the loot. */
	@Nullable
	private static Gear.Dungeon dungeon(SkyCrack c, RandomSource r) {
		String lair = GateDungeons.of(c).lair();
		Gear.Dungeon d = lair == null ? null : Gear.of(lair.startsWith("gate_") ? lair.substring(5) : lair);
		if (d == null || d.mobs().isEmpty()) d = Adventurers.any(Adventurers.dungeons(RANKS.charAt(Math.min(6, c.rank()))), r);
		return d;
	}

	private static String dir(ServerPlayer p, Vec3 at) {
		double dx = at.x - p.getX(), dz = at.z - p.getZ();
		String[] dirs = {"east", "south-east", "south", "south-west", "west", "north-west", "north", "north-east"};
		return "to the " + dirs[Math.floorMod((int) Math.round(Math.atan2(dz, dx) / (Math.PI / 4)), 8)];
	}

	private static void sound(ServerLevel l, Entity at, SoundEvent s, float volume, float pitch) {
		Vec3 m = at instanceof GateEntity g ? g.middle() : at.position();
		l.playSound(null, m.x, m.y, m.z, s, SoundSource.HOSTILE, volume, pitch);
	}

	static List<ServerPlayer> near(ServerLevel l, GateEntity c, double reach) {
		List<ServerPlayer> out = new ArrayList<>();
		Vec3 m = c.middle();
		for (ServerPlayer p : l.players()) if (!p.isSpectator() && p.position().distanceToSqr(m) < reach * reach) out.add(p);
		return out;
	}

	/** Players on the ground under it (counted flat, out from the eye). */
	static List<ServerPlayer> under(ServerLevel l, GateEntity c) {
		List<ServerPlayer> out = new ArrayList<>();
		for (ServerPlayer p : l.players()) {
			double dx = p.getX() - c.getX(), dz = p.getZ() - c.getZ();
			if (!p.isSpectator() && !p.isCreative() && dx * dx + dz * dz < UNDER * UNDER && Math.abs(p.getY() - c.getY()) < 120) out.add(p);
		}
		return out;
	}

	// ---------------------------------------------------------------- while it rages (GateEntity.tick)

	static void tick(SkyCrack c) {
		if (!(c.level() instanceof ServerLevel l)) return;
		Crack k = LIVE.get(c.getUUID());
		if (k == null) {
			c.discard();
			return;
		}
		long now = l.getGameTime(), age = now - c.opened();
		if (c.closing()) {
			long t = now - c.closed();
			if (t == 0) {
				sound(l, c, SoundEvents.BEACON_DEACTIVATE, 8f, 0.4f);
				sound(l, c, SoundEvents.LIGHTNING_BOLT_THUNDER, 10f, 0.4f);
			}
			if (t == GateEntity.BANG) sound(l, c, SoundEvents.GENERIC_EXPLODE.value(), 10f, 0.5f);
			if (t >= GateEntity.GONE) {
				clear(l, k);
				LIVE.remove(c.getUUID());
				c.discard();
			}
			return;
		}
		if (age % 90 == 0) sound(l, c, SoundEvents.PORTAL_AMBIENT, 6f, 0.4f);
		if (!near(l, c, FAR_GONE).isEmpty()) k.lastNear = now;
		if (age > LIFE || now - k.lastNear > EMPTY) {
			for (ServerPlayer p : near(l, c, FAR_GONE))
				p.displayClientMessage(Component.literal("The storm blows itself out. What came out of it stays.").withStyle(ChatFormatting.GRAY), true);
			c.close();
			return;
		}
		RandomSource r = l.getRandom();
		if (k.finishing) {
			alive(l, c, k);
			if (k.mobs.isEmpty()) {
				finish(l, c, k, r);
				return;
			}
			if (age % 60 == 0) for (ServerPlayer p : near(l, c, 250))
				p.displayClientMessage(Component.literal("Finish them: " + k.mobs.size() + " left").withStyle(ChatFormatting.GOLD), true);
		}
		if (!k.raised && age >= GateEntity.CRACK + GateEntity.OPEN + 60) raise(l, c, k, r);
		if (now >= k.nextFar) {
			farStrike(l, c, k, r);
			k.nextFar = now + FAR_STRIKE + r.nextInt(FAR_MORE);
		}
		if (age % 20 == 0) {
			if (!k.finishing) alive(l, c, k);
			Spells.glowLast(l, k.mobs, k.finishing);
		}
		if (k.raised && !k.finishing && now >= k.nextWave) {
			wave(l, c, k, r);
			k.nextWave = now + Math.max(WAVE_LEAST, WAVE - k.waves * 30);
		}
	}

	/** The spires bursting up round the eye, the storm's lightning feeding them. */
	static void raise(ServerLevel l, SkyCrack c, Crack k, RandomSource r) {
		k.raised = true;
		float start = r.nextFloat() * Mth.TWO_PI;
		for (int i = 0; i < k.anchors; i++) {
			for (int tries = 0; tries < 8; tries++) {
				double a = start + i * Mth.TWO_PI / k.anchors + (r.nextDouble() - 0.5) * 0.7, d = SPIRE_NEAR + r.nextDouble() * (SPIRE_FAR - SPIRE_NEAR);
				BlockPos col = BlockPos.containing(c.getX() + Math.cos(a) * d, 0, c.getZ() + Math.sin(a) * d);
				if (!l.hasChunkAt(col)) continue;
				BlockPos top = l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, col);
				if (!l.getFluidState(top.below()).isEmpty() && tries < 7) continue;
				StormSpire s = Gates.STORM_SPIRE.get().create(l);
				if (s == null) return;
				float hp = (float) (40 * (1 + k.rank) * Math.sqrt(k.players));
				s.setUp(r.nextInt(), 14 + r.nextFloat() * 9, hp, c);
				s.moveTo(top.getX() + 0.5, top.getY(), top.getZ() + 0.5, r.nextFloat() * 360, 0);
				s.addTag(TAG);
				if (l.addFreshEntity(s)) {
					k.spires.add(s.getUUID());
					k.placed++;
					k.left++;
				}
				break;
			}
		}
		for (ServerPlayer p : near(l, c, 300))
			p.sendSystemMessage(Component.literal("Storm spires burst from the ground, holding the eye open. Break them and the storm dies.")
					.withStyle(ChatFormatting.GOLD));
	}

	/** Lightning at the party: near a few of them (never right on them: the ring gives a moment to get clear). */
	static void wave(ServerLevel l, SkyCrack c, Crack k, RandomSource r) {
		k.waves++;
		List<ServerPlayer> at = under(l, c);
		int n = Math.min(3, 1 + (k.players - 1) / 2);
		for (int i = 0; i < n; i++) {
			Vec3 near = at.isEmpty() ? new Vec3(c.getX(), k.ground.getY(), c.getZ()) : at.get(r.nextInt(at.size())).position();
			double a = r.nextDouble() * Math.PI * 2, d = 5 + r.nextDouble() * 10;
			strike(l, c, k, near.x + Math.cos(a) * d, near.z + Math.sin(a) * d, false, r);
		}
	}

	/** One off under the storm, for the look of it. */
	static void farStrike(ServerLevel l, SkyCrack c, Crack k, RandomSource r) {
		double a = r.nextDouble() * Math.PI * 2, d = 20 + r.nextDouble() * (UNDER - 40);
		strike(l, c, k, c.getX() + Math.cos(a) * d, c.getZ() + Math.sin(a) * d, true, r);
	}

	@Nullable
	static StormStrike strike(ServerLevel l, SkyCrack c, Crack k, double x, double z, boolean harmless, RandomSource r) {
		BlockPos col = BlockPos.containing(x, 0, z);
		if (!l.hasChunkAt(col)) return null;
		BlockPos top = l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, col);
		StormStrike s = Gates.STORM_STRIKE.get().create(l);
		if (s == null) return null;
		float cloud = (float) (c.getY() + GateEntity.MID - SkyCrack.DECK - top.getY() + 2);
		s.setUp(r.nextInt(), c.rank(), harmless, Math.max(20, cloud), 4 + 3 * k.rank, c.getUUID());
		s.moveTo(x, top.getY(), z, 0, 0);
		s.addTag(TAG);
		return l.addFreshEntity(s) ? s : null;
	}

	/** Out of a strike's scorch: the dungeon's monsters, hauling themselves up out of the ground. */
	static void climbOut(ServerLevel l, StormStrike s) {
		Crack k = s.crack == null ? null : LIVE.get(s.crack);
		if (k == null || k.won || k.monsters.isEmpty()) return;
		k.mobs.removeIf(u -> !(l.getEntity(u) instanceof Mob m) || !m.isAlive());
		int most = 8 + 2 * k.players;
		RandomSource r = l.getRandom();
		int count = Math.min(most - k.mobs.size(), 2 + (k.players > 2 ? 1 : 0) + k.rank / 4);
		for (int i = 0; i < count; i++) {
			Mob m = Encounters.monster(l, Adventurers.any(k.monsters, r), s.blockPosition(), 1.5, r);
			if (m == null) continue;
			m.addTag(TAG);
			if (!l.addFreshEntity(m)) continue;
			k.mobs.add(m.getUUID());
			Player p = l.getNearestPlayer(m.getX(), m.getY(), m.getZ(), 64, false);
			if (p != null && !p.isCreative()) m.setTarget(p);
		}
		l.playSound(null, s.getX(), s.getY(), s.getZ(), SoundEvents.ROOTED_DIRT_BREAK, SoundSource.HOSTILE, 2f, 0.5f);
		l.playSound(null, s.getX(), s.getY(), s.getZ(), SoundEvents.ZOMBIE_BREAK_WOODEN_DOOR, SoundSource.HOSTILE, 0.8f, 0.5f);
	}

	/** A spire's broken (StormSpire.hurt): when the last one goes, the storm collapses and pays. */
	static void anchorBroken(ServerLevel l, StormSpire s) {
		Crack k = s.crack == null ? null : LIVE.get(s.crack);
		if (k == null || k.won) return;
		k.left = Math.max(0, k.left - 1);
		Entity e = l.getEntity(s.crack);
		if (!(e instanceof SkyCrack c)) return;
		if (k.left > 0) {
			for (ServerPlayer p : near(l, c, 250))
				p.displayClientMessage(Component.literal("A storm spire falls! " + k.left + " left.").withStyle(ChatFormatting.GOLD), true);
			return;
		}
		// the eye's held by nothing now: it stops striking, and what came out of it has to be put down
		k.finishing = true;
		alive(l, c, k);
		if (k.mobs.isEmpty()) {
			finish(l, c, k, l.getRandom());
			return;
		}
		for (ServerPlayer p : near(l, c, 250))
			p.sendSystemMessage(Component.literal("The last spire falls and the eye falters! Finish the " + k.mobs.size() + " still out.")
					.withStyle(ChatFormatting.GOLD));
	}

	/** What came out of it and still counts: alive, loaded, not wandered far off. */
	private static void alive(ServerLevel l, SkyCrack c, Crack k) {
		k.mobs.removeIf(u -> !(l.getEntity(u) instanceof Mob m) || !m.isAlive()
				|| (m.getX() - c.getX()) * (m.getX() - c.getX()) + (m.getZ() - c.getZ()) * (m.getZ() - c.getZ()) > STRAY * STRAY);
	}

	/** Collapsed: everyone who was there paid like a gate run of its rank, and a last strike beside each of them bursts
	 *  their own loot out of the ground (theirs alone to pick up, glowing so it's found). */
	static void finish(ServerLevel l, SkyCrack c, Crack k, RandomSource r) {
		k.won = true;
		c.close();
		int[] pay = Errands.pay(k.rank);
		for (ServerPlayer p : near(l, c, 250)) {
			int coins = pay[0] * 3, gp = Guild.of(p).registered() ? pay[1] * 3 : 0;
			Coins.give(p, coins);
			if (gp > 0) Guild.points(p, gp);
			double a = r.nextDouble() * Math.PI * 2;
			double x = p.getX() + Math.cos(a) * 3, z = p.getZ() + Math.sin(a) * 3;
			strike(l, c, k, x, z, true, r);
			// out of the eye: it falls from just over their head (Dropped.rain)
			List<ItemStack> share = new java.util.ArrayList<>(loot(p, k, r));
			share.addAll(Chains.extra(p, "storm"));
			String got = Dropped.rain(l, p, share, r);
			StringBuilder b = new StringBuilder("  +" + coins + " coins" + (gp > 0 ? ", +" + gp + " GP" : "") + got);
			p.sendSystemMessage(Component.literal("The storm collapses! Its loot falls out of the sky around you.").withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD));
			p.sendSystemMessage(Component.literal(b.toString()).withStyle(ChatFormatting.YELLOW));
		}
	}

	/** One player's share: a find of their rank (half the time two), the storm's dungeon's mats (its rarer ones now and
	 *  then), and once in a while one of its weapons. */
	static List<ItemStack> loot(ServerPlayer p, Crack k, RandomSource r) {
		List<ItemStack> out = new ArrayList<>();
		out.add(new ItemStack(Ranks.find(p, r)));
		if (r.nextFloat() < 0.5f) out.add(new ItemStack(Ranks.find(p, r)));
		Gear.Dungeon d = k.dungeon;
		if (d == null) return out;
		mat(out, d, 0, 2 + r.nextInt(3));
		if (r.nextFloat() < 0.5f) mat(out, d, 1, 1 + r.nextInt(2));
		if (r.nextFloat() < 0.12f) mat(out, d, 2, 1);
		if (r.nextFloat() < 0.06f) {
			List<Gear.Weapon> arms = d.weapons().stream().filter(w -> !w.boss()).toList();
			var it = arms.isEmpty() ? null : Gear.item(arms.get(r.nextInt(arms.size())).id());
			if (it != null) out.add(new ItemStack(it));
		}
		return out;
	}

	private static void mat(List<ItemStack> out, Gear.Dungeon d, int which, int n) {
		if (d.mats().length <= which) return;
		var it = Gear.item(d.mats()[which]);
		if (it != null) out.add(new ItemStack(it, n));
	}

	/** Gone: its spires crumble; what came out of it is just monsters now. */
	private static void clear(ServerLevel l, Crack k) {
		for (UUID u : k.spires) {
			Entity e = l.getEntity(u);
			if (e != null) e.discard();
		}
		for (UUID u : k.mobs) if (l.getEntity(u) instanceof Mob m) m.setPersistenceRequired();
	}

	// ---------------------------------------------------------------- when and where

	/** Ahead of whoever it's for, somewhere they'll see it: 70 to 115 blocks off, on dry land outside any town. */
	@Nullable
	static BlockPos spot(ServerLevel l, ServerPlayer p, RandomSource r) {
		for (int k = 0; k < 12; k++) {
			double a = Math.toRadians(p.getYRot() + 90 + (r.nextDouble() - 0.5) * 100), d = NEAR + r.nextDouble() * (FAR - NEAR);
			BlockPos col = BlockPos.containing(p.getX() + Math.cos(a) * d, 0, p.getZ() + Math.sin(a) * d);
			if (!l.hasChunkAt(col)) continue;
			BlockPos top = l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, col);
			if (!l.getFluidState(top.below()).isEmpty() || Adventurers.town(top) != null) continue;
			return top;
		}
		return null;
	}

	private static void spawner(ServerTickEvent.Post e) {
		var server = e.getServer();
		if (server.getTickCount() % 200 != 0) return;
		ServerLevel l = server.overworld();
		RandomSource r = l.getRandom();
		long now = l.getGameTime();
		Map<Object, List<ServerPlayer>> groups = new java.util.LinkedHashMap<>();
		for (ServerPlayer p : l.players()) if (!p.isSpectator()) groups.computeIfAbsent(com.snoringwalrus.ashbound.Party.fightKey(p), x -> new ArrayList<>()).add(p);
		for (var g : groups.entrySet()) {
			Object key = g.getKey();
			Long next = NEXT.get(key);
			if (next == null) {
				NEXT.put(key, now + FIRST + r.nextInt(MORE / 2));
				continue;
			}
			if (now < next || LIVE.values().stream().anyMatch(k -> key.equals(k.group))) continue;
			ServerPlayer p = g.getValue().get(r.nextInt(g.getValue().size()));
			if (Adventurers.town(p.blockPosition()) != null || p.getY() < l.getSeaLevel() - 10 || !l.canSeeSky(p.blockPosition())) {
				NEXT.put(key, now + RETRY);
				continue;
			}
			int with = (int) g.getValue().stream().filter(o -> o.distanceTo(p) < 64).count();
			BlockPos at = spot(l, p, r);
			SkyCrack c = at == null ? null : open(l, at, Ranks.party(p), with, key, r);
			NEXT.put(key, now + (c == null ? RETRY : EVERY + r.nextInt(MORE)));
		}
	}

	/** Nothing of one outlives the session it was in. */
	private static void join(EntityJoinLevelEvent e) {
		if (e.loadedFromDisk() && (e.getEntity() instanceof SkyCrack || e.getEntity() instanceof StormSpire || e.getEntity() instanceof StormStrike))
			e.setCanceled(true);
	}

	private static void commands(RegisterCommandsEvent e) {
		for (String name : new String[] {"storm", "skycrack"})
			e.getDispatcher().register(Commands.literal("ashbound").requires(s -> s.hasPermission(2)).then(Commands.literal(name)
					.executes(c -> make(c.getSource().getPlayerOrException(), -1))
					.then(Commands.literal("win").executes(c -> winNearest(c.getSource().getPlayerOrException())))
					.then(Commands.argument("rank", IntegerArgumentType.integer(0, 6)).executes(c -> make(c.getSource().getPlayerOrException(), IntegerArgumentType.getInteger(c, "rank"))))));
	}

	/** `/ashbound storm win`: the nearest storm beaten on the spot, as if its spires and monsters were all put down. */
	private static int winNearest(ServerPlayer p) {
		ServerLevel l = p.serverLevel();
		SkyCrack best = null;
		Crack bk = null;
		for (var e : LIVE.entrySet()) {
			if (e.getValue().won || !(l.getEntity(e.getKey()) instanceof SkyCrack c) || c.closing()) continue;
			if (best == null || c.distanceToSqr(p) < best.distanceToSqr(p)) {
				best = c;
				bk = e.getValue();
			}
		}
		if (best == null) {
			p.sendSystemMessage(Component.literal("No gate storm raging here"));
			return 0;
		}
		for (UUID u : bk.spires) {
			Entity e = l.getEntity(u);
			if (e != null) e.discard();
		}
		for (UUID u : bk.mobs) if (l.getEntity(u) instanceof Mob m) m.kill();
		bk.left = 0;
		bk.finishing = true;
		bk.mobs.clear();
		finish(l, best, bk, l.getRandom());
		return 1;
	}

	private static int make(ServerPlayer p, int rank) {
		BlockPos at = spot(p.serverLevel(), p, p.getRandom());
		if (at == null) {
			p.sendSystemMessage(Component.literal("No open ground ahead for a storm"));
			return 0;
		}
		return open(p.serverLevel(), at, rank < 0 ? Ranks.party(p) : rank, 1, com.snoringwalrus.ashbound.Party.fightKey(p), p.getRandom()) == null ? 0 : 1;
	}

	static void init() {
		NeoForge.EVENT_BUS.addListener(SkyCracks::spawner);
		NeoForge.EVENT_BUS.addListener(SkyCracks::commands);
		NeoForge.EVENT_BUS.addListener(SkyCracks::join);
	}
}
