package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

import com.mojang.brigadier.arguments.StringArgumentType;
import net.minecraft.ChatFormatting;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.SharedSuggestionProvider;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.ClickEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.HoverEvent;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.saveddata.SavedData;
import net.neoforged.fml.loading.FMLLoader;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * Parties: up to eight who play together, kept with the world. You can't hurt each other, a quest step one of you does
 * is done for all of you (Story.mark) and a request one of you takes or reports is taken or reported by all (Guild), and
 * a share of what dies goes to members a little further off. Someone offline gets what they missed when they're back.
 * What you face still grows by who's actually near it (Balance), party or not.
 *
 * The leader can make anyone a commander, who may invite, kick plain members and take from the party's bank; anyone can pay in, and
 * the bank keeps its last few lines so everyone sees who did what. When a party breaks up the last one left gets what's in it.
 *
 *   /party invite NAME, /party accept, /party decline, /party leave, /party kick NAME, /party
 */
final class Party {
	private Party() {}

	static final int MAX = 8;
	/** How far off a member still shares a kill's Ash, coins and drop rolls. */
	static final double SHARE = 64;
	/** What came down the party's line as a request to settle, not a quest step. */
	static final String REQUEST = "req:";
	private static final int INVITE_TICKS = 20 * 60, EVERY = 10, NEAR = 128, LEDGER = 6;

	private static final class Group {
		UUID leader;
		final Map<UUID, String> names = new LinkedHashMap<>();
		final Map<UUID, Set<String>> owed = new HashMap<>();
		final Set<UUID> commanders = new HashSet<>();
		int bank;
		final List<String> ledger = new ArrayList<>();

		int role(UUID u) {
			return u.equals(leader) ? Net.PartyCard.LEADER : commanders.contains(u) ? Net.PartyCard.COMMANDER : Net.PartyCard.MEMBER;
		}
	}

	private record Invite(UUID from, long until) {}

	private static final Map<UUID, Invite> INVITES = new HashMap<>();
	private static final Map<UUID, Long> PINGED = new HashMap<>();
	private static final int PING_GAP = 10;

	/** Dev runs only (/partytest), to try the screens alone: stand-ins by id, each health, top and how near. Never in a release. */
	private static final Map<UUID, float[]> STAND_INS = new HashMap<>();
	private static final String[][] CAST = {{"Test_Mira", "1"}, {"Test_Bram", "0"}, {"Test_Sela", "0"}, {"Test_Odo", "0"}, {"Test_Wren", "0"}};
	private static final float[][] CAST_HP = {{38, 40, 1}, {9, 30, 1}, {24, 24, 0}, {60, 70, 1}, {-1, 20, 0}};
	static final String GUEST = "Test_Guest";
	private static final Set<UUID> ASKED = new HashSet<>();

	private static final class State extends SavedData {
		final Map<UUID, Group> of = new HashMap<>();
		/** A broken-up party's bank, waiting for someone who was offline when it went. */
		final Map<UUID, Integer> unpaid = new HashMap<>();

		@Override
		public CompoundTag save(CompoundTag tag, HolderLookup.Provider reg) {
			ListTag groups = new ListTag();
			for (Group g : new HashSet<>(of.values())) {
				CompoundTag t = new CompoundTag();
				t.putUUID("leader", g.leader);
				ListTag members = new ListTag();
				g.names.forEach((u, name) -> {
					CompoundTag m = new CompoundTag();
					m.putUUID("id", u);
					m.putString("name", name);
					ListTag owed = new ListTag();
					for (String s : g.owed.getOrDefault(u, Set.of())) owed.add(StringTag.valueOf(s));
					m.put("owed", owed);
					m.putBoolean("commander", g.commanders.contains(u));
					members.add(m);
				});
				t.put("members", members);
				t.putInt("bank", g.bank);
				ListTag ledger = new ListTag();
				for (String line : g.ledger) ledger.add(StringTag.valueOf(line));
				t.put("ledger", ledger);
				groups.add(t);
			}
			tag.put("groups", groups);
			ListTag unpaid = new ListTag();
			this.unpaid.forEach((u, coins) -> {
				CompoundTag t = new CompoundTag();
				t.putUUID("id", u);
				t.putInt("coins", coins);
				unpaid.add(t);
			});
			tag.put("unpaid", unpaid);
			return tag;
		}

		static State load(CompoundTag tag, HolderLookup.Provider reg) {
			State s = new State();
			for (Tag e : tag.getList("groups", Tag.TAG_COMPOUND)) {
				CompoundTag t = (CompoundTag) e;
				Group g = new Group();
				g.leader = t.getUUID("leader");
				g.bank = t.getInt("bank");
				for (Tag line : t.getList("ledger", Tag.TAG_STRING)) g.ledger.add(line.getAsString());
				for (Tag me : t.getList("members", Tag.TAG_COMPOUND)) {
					CompoundTag m = (CompoundTag) me;
					UUID u = m.getUUID("id");
					g.names.put(u, m.getString("name"));
					Set<String> owed = new LinkedHashSet<>();
					for (Tag o : m.getList("owed", Tag.TAG_STRING)) owed.add(o.getAsString());
					if (!owed.isEmpty()) g.owed.put(u, owed);
					if (m.getBoolean("commander")) g.commanders.add(u);
					s.of.put(u, g);
				}
			}
			for (Tag e : tag.getList("unpaid", Tag.TAG_COMPOUND)) s.unpaid.put(((CompoundTag) e).getUUID("id"), ((CompoundTag) e).getInt("coins"));
			return s;
		}
	}

	private static State state(MinecraftServer server) {
		return server.overworld().getDataStorage().computeIfAbsent(new SavedData.Factory<>(State::new, State::load, null), "ashbound_party");
	}

	private static Group group(ServerPlayer p) {
		return state(p.server).of.get(p.getUUID());
	}

	/** What p's fights are kept under (Meters): their party, or themselves alone. */
	static Object fightKey(ServerPlayer p) {
		Group g = group(p);
		return g != null ? g : p.getUUID();
	}

	// ---------------------------------------------------------------- asking

	static boolean same(ServerPlayer a, ServerPlayer b) {
		Group g = group(a);
		return g != null && g == group(b);
	}

	/** Your party's other members who are online. */
	static List<ServerPlayer> others(ServerPlayer p) {
		List<ServerPlayer> out = new ArrayList<>();
		Group g = group(p);
		if (g == null) return out;
		for (UUID u : g.names.keySet()) {
			ServerPlayer o = u.equals(p.getUUID()) ? null : p.server.getPlayerList().getPlayer(u);
			if (o != null) out.add(o);
		}
		return out;
	}

	/** Who p shares with, online or not, by name: p first, and only p if they're alone. */
	static Map<UUID, String> circle(ServerPlayer p) {
		Map<UUID, String> out = new LinkedHashMap<>();
		out.put(p.getUUID(), name(p));
		Group g = group(p);
		if (g != null) out.putAll(g.names);
		return out;
	}

	/** These players and everyone online in their parties, each once. */
	static Set<ServerPlayer> with(Collection<ServerPlayer> there) {
		Set<ServerPlayer> out = new LinkedHashSet<>(there);
		for (ServerPlayer p : there) out.addAll(others(p));
		return out;
	}

	/** Members of these players' parties in the same world within `reach` of one of them, and not among them. */
	static List<ServerPlayer> alongside(Collection<? extends Player> there, double reach) {
		Set<ServerPlayer> out = new LinkedHashSet<>();
		for (Player p : there) {
			if (!(p instanceof ServerPlayer sp)) continue;
			for (ServerPlayer o : others(sp))
				if (!there.contains(o) && !o.isSpectator() && o.isAlive() && o.level() == p.level() && o.distanceTo(p) <= reach) out.add(o);
		}
		return new ArrayList<>(out);
	}

	// ---------------------------------------------------------------- quests

	/** Steps that stay yours: a guild card you'd otherwise never sign for, and the Cold Forge, whose steps are things in your own hands. */
	static boolean personal(String path) {
		return path.equals("story/registered") || path.startsWith("story/rank_") || path.startsWith("cold/");
	}

	/** Something done by p, for the rest of the party: now if they're here, or when they're back. */
	static void share(ServerPlayer p, String what) {
		State st = state(p.server);
		Group g = st.of.get(p.getUUID());
		if (g == null || personal(what)) return;
		for (UUID u : g.names.keySet()) {
			if (u.equals(p.getUUID())) continue;
			ServerPlayer o = p.server.getPlayerList().getPlayer(u);
			if (o != null) receive(o, what);
			else if (g.owed.computeIfAbsent(u, k -> new LinkedHashSet<>()).add(what)) st.setDirty();
		}
	}

	private static void receive(ServerPlayer p, String what) {
		if (what.startsWith(REQUEST)) Guild.settle(p, what.substring(REQUEST.length()));
		else Story.own(p, what);
	}

	/** Back online, or anywhere else a member turns up: what they're owed. */
	static void arrive(ServerPlayer p) {
		State st = state(p.server);
		Integer unpaid = st.unpaid.remove(p.getUUID());
		if (unpaid != null) {
			Coins.give(p, unpaid);
			p.sendSystemMessage(Component.literal("Your old party's bank came to you: " + unpaid + " coins").withStyle(ChatFormatting.GOLD));
			st.setDirty();
		}
		Group g = st.of.get(p.getUUID());
		if (g == null) return;
		g.names.put(p.getUUID(), p.getScoreboardName());
		Set<String> owed = g.owed.remove(p.getUUID());
		st.setDirty();
		if (owed != null) for (String s : owed) receive(p, s);
	}

	// ---------------------------------------------------------------- commands

	static void init() {
		NeoForge.EVENT_BUS.addListener((RegisterCommandsEvent e) -> e.getDispatcher().register(Commands.literal("party")
				.executes(c -> list(c.getSource()))
				.then(Commands.literal("invite").then(Commands.argument("player", EntityArgument.player())
						.executes(c -> invite(c.getSource(), EntityArgument.getPlayer(c, "player")))))
				.then(Commands.literal("accept").executes(c -> accept(c.getSource())))
				.then(Commands.literal("decline").executes(c -> decline(c.getSource())))
				.then(Commands.literal("leave").executes(c -> leave(c.getSource())))
				.then(Commands.literal("kick").then(Commands.argument("player", StringArgumentType.word())
						.suggests((c, b) -> {
							ServerPlayer p = c.getSource().getPlayer();
							Group g = p == null ? null : group(p);
							return SharedSuggestionProvider.suggest(g == null ? List.of() : g.names.values(), b);
						})
						.executes(c -> kick(c.getSource(), StringArgumentType.getString(c, "player")))))));
		if (!FMLLoader.isProduction()) NeoForge.EVENT_BUS.addListener((RegisterCommandsEvent e) -> e.getDispatcher().register(Commands.literal("partytest")
				.executes(c -> testParty(c.getSource().getPlayerOrException()))
				.then(Commands.literal("invited").executes(c -> {
					ServerPlayer p = c.getSource().getPlayerOrException();
					if (group(p) != null) remove(p.server, p.getUUID(), " left the party");
					ASKED.add(p.getUUID());
					board(p);
					return 1;
				}))));
		NeoForge.EVENT_BUS.addListener((LivingIncomingDamageEvent e) -> {
			if (e.getEntity() instanceof ServerPlayer hurt && e.getSource().getEntity() instanceof ServerPlayer by && by != hurt && same(by, hurt)) e.setCanceled(true);
		});
		NeoForge.EVENT_BUS.addListener((PlayerEvent.PlayerLoggedInEvent e) -> {
			if (e.getEntity() instanceof ServerPlayer p) arrive(p);
		});
		NeoForge.EVENT_BUS.addListener((ServerTickEvent.Post e) -> {
			if (e.getServer().getTickCount() % EVERY != 0) return;
			for (Group g : new HashSet<>(state(e.getServer()).of.values())) sync(e.getServer(), g);
		});
		NeoForge.EVENT_BUS.addListener((PlayerEvent.PlayerLoggedOutEvent e) -> PINGED.remove(e.getEntity().getUUID()));
	}

	private static ServerPlayer me(CommandSourceStack src) {
		ServerPlayer p = src.getPlayer();
		if (p == null) src.sendFailure(Component.literal("Only a player can be in a party"));
		return p;
	}

	private static int invite(CommandSourceStack src, ServerPlayer who) {
		ServerPlayer p = me(src);
		if (p == null) return 0;
		if (who == p) return fail(p, "You can't invite yourself");
		Group g = group(p);
		if (g != null && g.role(p.getUUID()) == Net.PartyCard.MEMBER) return fail(p, "Only the leader or a commander can invite");
		if (g != null && g.names.size() >= MAX) return fail(p, "Your party is full (" + MAX + ")");
		if (group(who) != null) return fail(p, name(who) + " is already in a party");
		INVITES.put(who.getUUID(), new Invite(p.getUUID(), p.level().getGameTime() + INVITE_TICKS));
		p.sendSystemMessage(Component.literal("Invited " + name(who) + " to your party").withStyle(ChatFormatting.GRAY));
		MutableComponent yes = Component.literal("[Accept]").withStyle(s -> s.withColor(ChatFormatting.GREEN).withBold(true)
				.withClickEvent(new ClickEvent(ClickEvent.Action.RUN_COMMAND, "/party accept"))
				.withHoverEvent(new HoverEvent(HoverEvent.Action.SHOW_TEXT, Component.literal("Join the party"))));
		MutableComponent no = Component.literal("[Decline]").withStyle(s -> s.withColor(ChatFormatting.RED)
				.withClickEvent(new ClickEvent(ClickEvent.Action.RUN_COMMAND, "/party decline")));
		who.sendSystemMessage(Component.literal(name(p)).withStyle(ChatFormatting.GOLD)
				.append(Component.literal(" invites you to their party  ").withStyle(ChatFormatting.GRAY)).append(yes).append(" ").append(no));
		who.level().playSound(null, who.blockPosition(), SoundEvents.NOTE_BLOCK_BELL.value(), SoundSource.PLAYERS, 0.6f, 1.2f);
		board(who);
		return 1;
	}

	private static int accept(CommandSourceStack src) {
		ServerPlayer p = me(src);
		if (p == null) return 0;
		if (ASKED.remove(p.getUUID())) return testParty(p);
		Invite inv = INVITES.remove(p.getUUID());
		if (inv == null || p.level().getGameTime() > inv.until) return fail(p, "Nobody has invited you (or the invite ran out)");
		if (group(p) != null) return fail(p, "Leave your party first");
		ServerPlayer from = p.server.getPlayerList().getPlayer(inv.from);
		if (from == null) return fail(p, "They've gone");
		if (!form(from, p)) return fail(p, "That party is full");
		return 1;
	}

	/** p joins host's party, one's started if host has none. */
	static boolean form(ServerPlayer host, ServerPlayer p) {
		State st = state(p.server);
		Group g = st.of.get(host.getUUID());
		if (g == null) {
			g = new Group();
			g.leader = host.getUUID();
			g.names.put(host.getUUID(), name(host));
			st.of.put(host.getUUID(), g);
		}
		if (g.names.size() >= MAX) return false;
		g.names.put(p.getUUID(), name(p));
		st.of.put(p.getUUID(), g);
		st.setDirty();
		announce(p.server, g, Component.literal(name(p) + " joined the party").withStyle(ChatFormatting.GREEN));
		sync(p.server, g);
		boards(p.server, g);
		return true;
	}

	private static int decline(CommandSourceStack src) {
		ServerPlayer p = me(src);
		if (p == null) return 0;
		if (ASKED.remove(p.getUUID())) {
			board(p);
			return 1;
		}
		Invite inv = INVITES.remove(p.getUUID());
		if (inv == null) return fail(p, "Nobody has invited you");
		ServerPlayer from = p.server.getPlayerList().getPlayer(inv.from);
		if (from != null) from.sendSystemMessage(Component.literal(name(p) + " declined your invite").withStyle(ChatFormatting.GRAY));
		board(p);
		return 1;
	}

	private static int leave(CommandSourceStack src) {
		ServerPlayer p = me(src);
		if (p == null) return 0;
		if (group(p) == null) return fail(p, "You're not in a party");
		remove(p.server, p.getUUID(), " left the party");
		return 1;
	}

	private static int kick(CommandSourceStack src, String who) {
		ServerPlayer p = me(src);
		if (p == null) return 0;
		Group g = group(p);
		if (g == null || g.role(p.getUUID()) == Net.PartyCard.MEMBER) return fail(p, "Only the leader or a commander can kick");
		UUID u = member(g, who);
		if (u == null || u.equals(p.getUUID())) return fail(p, who + " isn't in your party");
		if (g.role(u) >= g.role(p.getUUID())) return fail(p, "Only the leader can kick a commander");
		remove(p.server, u, " was kicked from the party");
		return 1;
	}

	private static int list(CommandSourceStack src) {
		ServerPlayer p = me(src);
		if (p == null) return 0;
		Group g = group(p);
		if (g == null) {
			p.sendSystemMessage(Component.literal("You're not in a party. /party invite NAME to start one").withStyle(ChatFormatting.GRAY));
			return 1;
		}
		MutableComponent m = Component.literal("Party (" + g.names.size() + "/" + MAX + "): ").withStyle(ChatFormatting.GOLD);
		boolean first = true;
		for (Map.Entry<UUID, String> e : g.names.entrySet()) {
			if (!first) m.append(Component.literal(", ").withStyle(ChatFormatting.GRAY));
			first = false;
			m.append(Component.literal(e.getValue() + (e.getKey().equals(g.leader) ? " (leader)" : g.commanders.contains(e.getKey()) ? " (commander)" : "")).withStyle(ChatFormatting.WHITE));
		}
		p.sendSystemMessage(m);
		return 1;
	}

	/** u out of their party; the lead passed on, the party gone if one's left. */
	static void remove(MinecraftServer server, UUID u, String why) {
		State st = state(server);
		Group g = st.of.remove(u);
		if (g == null) return;
		String gone = g.names.remove(u);
		g.owed.remove(u);
		g.commanders.remove(u);
		st.setDirty();
		ServerPlayer was = server.getPlayerList().getPlayer(u);
		if (was != null) {
			was.sendSystemMessage(Component.literal("You" + (why.contains("kicked") ? " were kicked from" : " left") + " the party").withStyle(ChatFormatting.GRAY));
			PacketDistributor.sendToPlayer(was, new Net.PartySync(List.of()));
			board(was);
		}
		announce(server, g, Component.literal(gone + why).withStyle(ChatFormatting.GRAY));
		if (g.names.size() <= 1) {
			for (UUID m : g.names.keySet()) {
				st.of.remove(m);
				ServerPlayer o = server.getPlayerList().getPlayer(m);
				if (o != null) {
					o.sendSystemMessage(Component.literal("The party broke up").withStyle(ChatFormatting.GRAY));
					PacketDistributor.sendToPlayer(o, new Net.PartySync(List.of()));
					if (g.bank > 0) {
						Coins.give(o, g.bank);
						o.sendSystemMessage(Component.literal("The party's bank came to you: " + g.bank + " coins").withStyle(ChatFormatting.GOLD));
					}
					board(o);
				} else if (g.bank > 0) st.unpaid.merge(m, g.bank, (a, b) -> (int) Math.min(Integer.MAX_VALUE, (long) a + b));
			}
			return;
		}
		if (g.leader.equals(u)) {
			// a commander first, if there is one
			g.leader = g.names.keySet().stream().filter(g.commanders::contains).findFirst().orElse(g.names.keySet().iterator().next());
			g.commanders.remove(g.leader);
			announce(server, g, Component.literal(g.names.get(g.leader) + " leads the party now").withStyle(ChatFormatting.GOLD));
		}
		sync(server, g);
		boards(server, g);
	}

	// ---------------------------------------------------------------- the Party screen

	private static UUID member(Group g, String who) {
		for (Map.Entry<UUID, String> m : g.names.entrySet()) if (m.getValue().equalsIgnoreCase(who)) return m.getKey();
		return null;
	}

	/** A full table to try the screens on, by yourself, with you at the head of it. */
	private static int testParty(ServerPlayer p) {
		State st = state(p.server);
		Group g = st.of.get(p.getUUID());
		if (g == null) {
			g = new Group();
			g.leader = p.getUUID();
			g.names.put(p.getUUID(), name(p));
			st.of.put(p.getUUID(), g);
		}
		for (int i = 0; i < CAST.length; i++) if (member(g, CAST[i][0]) == null) standIn(st, g, CAST[i][0], CAST_HP[i], CAST[i][1].equals("1"));
		g.bank = 500;
		g.ledger.clear();
		note(g, "Test_Odo took 120");
		note(g, "Test_Bram put in 300");
		Coins.give(p, 1000);
		sync(p.server, g);
		boards(p.server, g);
		return 1;
	}

	private static void standIn(State st, Group g, String name, float[] hp, boolean commander) {
		UUID u = UUID.nameUUIDFromBytes(name.getBytes(java.nio.charset.StandardCharsets.UTF_8));
		STAND_INS.put(u, hp);
		g.names.put(u, name);
		if (commander) g.commanders.add(u);
		st.of.put(u, g);
	}

	/** Who's asked p to join, if that still stands. */
	private static String invitedBy(ServerPlayer p) {
		if (ASKED.contains(p.getUUID())) return "Test_Mira";
		Invite inv = INVITES.get(p.getUUID());
		ServerPlayer from = inv == null || p.level().getGameTime() > inv.until ? null : p.server.getPlayerList().getPlayer(inv.from);
		return from == null ? "" : name(from);
	}

	private static void board(ServerPlayer p) {
		Group g = group(p);
		List<Net.PartyCard> cards = new ArrayList<>();
		if (g != null) g.names.forEach((u, name) -> cards.add(new Net.PartyCard(name, g.role(u), rankOf(p, u), p.server.getPlayerList().getPlayer(u) != null || STAND_INS.containsKey(u) && STAND_INS.get(u)[0] >= 0)));
		PacketDistributor.sendToPlayer(p, new Net.PartyBoard(cards, Ranks.party(p), g == null ? 0 : g.bank, g == null ? List.of() : List.copyOf(g.ledger), invitedBy(p)));
	}

	private static int rankOf(ServerPlayer p, UUID u) {
		ServerPlayer o = p.server.getPlayerList().getPlayer(u);
		return o == null ? 0 : Ranks.rank(o);
	}

	private static void boards(MinecraftServer server, Group g) {
		for (UUID u : g.names.keySet()) {
			ServerPlayer o = server.getPlayerList().getPlayer(u);
			if (o != null) board(o);
		}
	}

	/** What's in p's party's bank. */
	static int bank(ServerPlayer p) {
		Group g = group(p);
		return g == null ? 0 : g.bank;
	}

	private static void note(Group g, String line) {
		g.ledger.add(0, line);
		if (g.ledger.size() > LEDGER) g.ledger.remove(LEDGER);
	}

	/** Pays in what you have, up to what the bank can hold. */
	private static void putIn(ServerPlayer p, Group g, int coins) {
		int n = Math.min(Math.min(coins, Coins.of(p)), Integer.MAX_VALUE - g.bank);
		if (n <= 0) return;
		Coins.give(p, -n);
		g.bank += n;
		note(g, name(p) + " put in " + n);
	}

	/** Takes out what's there, up to what your purse can hold. */
	private static void takeOut(ServerPlayer p, Group g, int coins) {
		if (g.role(p.getUUID()) == Net.PartyCard.MEMBER) {
			fail(p, "Only the leader or a commander can take from the bank");
			return;
		}
		int n = Math.min(Math.min(coins, g.bank), Integer.MAX_VALUE - Coins.of(p));
		if (n <= 0) return;
		g.bank -= n;
		Coins.give(p, n);
		note(g, name(p) + " took " + n);
	}

	/** The leader's calls: a commander's rank, on or off, and handing over the lead. */
	private static void rank(ServerPlayer p, Group g, String who, boolean lead) {
		UUID u = member(g, who);
		if (!p.getUUID().equals(g.leader) || u == null || u.equals(p.getUUID())) return;
		if (lead) {
			g.leader = u;
			g.commanders.remove(u);
			g.commanders.add(p.getUUID());
			announce(p.server, g, Component.literal(g.names.get(u) + " leads the party now").withStyle(ChatFormatting.GOLD));
		} else if (!g.commanders.remove(u)) {
			g.commanders.add(u);
			announce(p.server, g, Component.literal(g.names.get(u) + " is a commander now").withStyle(ChatFormatting.GOLD));
		}
		sync(p.server, g);
	}

	static void act(ServerPlayer p, Net.PartyAct m) {
		CommandSourceStack src = p.createCommandSourceStack();
		Group g = group(p);
		switch (m.what()) {
			case Net.PartyAct.INVITE -> {
				ServerPlayer who = p.server.getPlayerList().getPlayerByName(m.who());
				if (who != null) invite(src, who);
				else if (!FMLLoader.isProduction() && m.who().equals(GUEST)) {
					if (g == null) testParty(p);
					g = group(p);
					if (member(g, GUEST) == null && g.names.size() < MAX) standIn(state(p.server), g, GUEST, new float[] {15, 20, 1}, false);
					sync(p.server, g);
				}
			}
			case Net.PartyAct.ACCEPT -> accept(src);
			case Net.PartyAct.DECLINE -> decline(src);
			case Net.PartyAct.LEAVE -> {
				if (g != null) leave(src);
			}
			case Net.PartyAct.KICK -> kick(src, m.who());
			case Net.PartyAct.COMMANDER, Net.PartyAct.LEAD -> {
				if (g != null) rank(p, g, m.who(), m.what() == Net.PartyAct.LEAD);
			}
			case Net.PartyAct.PUT_IN, Net.PartyAct.TAKE_OUT -> {
				if (g == null || m.coins() <= 0) break;
				if (m.what() == Net.PartyAct.PUT_IN) putIn(p, g, m.coins());
				else takeOut(p, g, m.coins());
				state(p.server).setDirty();
			}
			default -> {}
		}
		if (g != null) {
			state(p.server).setDirty();
			boards(p.server, g);
		}
		board(p);
	}

	// ---------------------------------------------------------------- the HUD

	private static void sync(MinecraftServer server, Group g) {
		List<Net.PartySpot> spots = new ArrayList<>();
		for (UUID u : g.names.keySet()) {
			ServerPlayer o = server.getPlayerList().getPlayer(u);
			if (o != null) spots.add(new Net.PartySpot(u, o.getX(), o.getY(), o.getZ(), o.level().dimension().location().toString()));
		}
		for (UUID to : g.names.keySet()) {
			ServerPlayer tp = server.getPlayerList().getPlayer(to);
			if (tp == null) continue;
			List<Net.PartyMember> out = new ArrayList<>();
			g.names.forEach((u, name) -> {
				if (u.equals(to)) return;
				ServerPlayer o = server.getPlayerList().getPlayer(u);
				float[] in = STAND_INS.get(u);
				if (in != null) {
					out.add(new Net.PartyMember(name, in[0], in[1], u.equals(g.leader), in[0] >= 0, in[2] > 0));
					return;
				}
				out.add(new Net.PartyMember(name, o != null ? o.getHealth() : 0, o != null ? o.getMaxHealth() : 20, u.equals(g.leader), o != null,
						o != null && o.level() == tp.level() && o.distanceTo(tp) < NEAR));
			});
			PacketDistributor.sendToPlayer(tp, new Net.PartySync(out));
			PacketDistributor.sendToPlayer(tp, new Net.PartySpots(spots));
		}
	}

	/** The scroll wheel's mark: to everyone in the party in this world, or only you if you're alone. */
	static void ping(ServerPlayer p, Net.Ping m) {
		long now = p.server.getTickCount();
		Long last = PINGED.get(p.getUUID());
		if (last != null && now - last < PING_GAP) return;
		PINGED.put(p.getUUID(), now);
		Net.PingAt out = new Net.PingAt(name(p), m.x(), m.y(), m.z());
		Group g = group(p);
		if (g == null) {
			PacketDistributor.sendToPlayer(p, out);
			return;
		}
		for (UUID u : g.names.keySet()) {
			ServerPlayer o = p.server.getPlayerList().getPlayer(u);
			if (o != null && o.level() == p.level()) PacketDistributor.sendToPlayer(o, out);
		}
	}

	// ---------------------------------------------------------------- talk

	private static String name(ServerPlayer p) {
		return p.getScoreboardName();
	}

	private static int fail(ServerPlayer p, String why) {
		p.sendSystemMessage(Component.literal(why).withStyle(ChatFormatting.RED));
		return 0;
	}

	private static void announce(MinecraftServer server, Group g, Component c) {
		for (UUID u : g.names.keySet()) {
			ServerPlayer o = server.getPlayerList().getPlayer(u);
			if (o != null) o.sendSystemMessage(c);
		}
	}
}
