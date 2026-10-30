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
 *   /party invite NAME, /party accept, /party decline, /party leave, /party kick NAME, /party
 */
final class Party {
	private Party() {}

	static final int MAX = 8;
	/** How far off a member still shares a kill's Ash, coins and drop rolls. */
	static final double SHARE = 64;
	/** What came down the party's line as a request to settle, not a quest step. */
	static final String REQUEST = "req:";
	private static final int INVITE_TICKS = 20 * 60, EVERY = 10, NEAR = 128;

	private static final class Group {
		UUID leader;
		final Map<UUID, String> names = new LinkedHashMap<>();
		final Map<UUID, Set<String>> owed = new HashMap<>();
	}

	private record Invite(UUID from, long until) {}

	private static final Map<UUID, Invite> INVITES = new HashMap<>();

	private static final class State extends SavedData {
		final Map<UUID, Group> of = new HashMap<>();

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
					members.add(m);
				});
				t.put("members", members);
				groups.add(t);
			}
			tag.put("groups", groups);
			return tag;
		}

		static State load(CompoundTag tag, HolderLookup.Provider reg) {
			State s = new State();
			for (Tag e : tag.getList("groups", Tag.TAG_COMPOUND)) {
				CompoundTag t = (CompoundTag) e;
				Group g = new Group();
				g.leader = t.getUUID("leader");
				for (Tag me : t.getList("members", Tag.TAG_COMPOUND)) {
					CompoundTag m = (CompoundTag) me;
					UUID u = m.getUUID("id");
					g.names.put(u, m.getString("name"));
					Set<String> owed = new LinkedHashSet<>();
					for (Tag o : m.getList("owed", Tag.TAG_STRING)) owed.add(o.getAsString());
					if (!owed.isEmpty()) g.owed.put(u, owed);
					s.of.put(u, g);
				}
			}
			return s;
		}
	}

	private static State state(MinecraftServer server) {
		return server.overworld().getDataStorage().computeIfAbsent(new SavedData.Factory<>(State::new, State::load, null), "ashbound_party");
	}

	private static Group group(ServerPlayer p) {
		return state(p.server).of.get(p.getUUID());
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
		if (g != null && !g.leader.equals(p.getUUID())) return fail(p, "Only the party leader can invite");
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
		return 1;
	}

	private static int accept(CommandSourceStack src) {
		ServerPlayer p = me(src);
		if (p == null) return 0;
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
		return true;
	}

	private static int decline(CommandSourceStack src) {
		ServerPlayer p = me(src);
		if (p == null) return 0;
		Invite inv = INVITES.remove(p.getUUID());
		if (inv == null) return fail(p, "Nobody has invited you");
		ServerPlayer from = p.server.getPlayerList().getPlayer(inv.from);
		if (from != null) from.sendSystemMessage(Component.literal(name(p) + " declined your invite").withStyle(ChatFormatting.GRAY));
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
		if (g == null || !g.leader.equals(p.getUUID())) return fail(p, "Only the party leader can kick");
		for (Map.Entry<UUID, String> m : g.names.entrySet())
			if (m.getValue().equalsIgnoreCase(who) && !m.getKey().equals(p.getUUID())) {
				remove(p.server, m.getKey(), " was kicked from the party");
				return 1;
			}
		return fail(p, who + " isn't in your party");
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
			m.append(Component.literal(e.getValue() + (e.getKey().equals(g.leader) ? " (leader)" : "")).withStyle(ChatFormatting.WHITE));
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
		st.setDirty();
		ServerPlayer was = server.getPlayerList().getPlayer(u);
		if (was != null) {
			was.sendSystemMessage(Component.literal("You" + (why.contains("kicked") ? " were kicked from" : " left") + " the party").withStyle(ChatFormatting.GRAY));
			PacketDistributor.sendToPlayer(was, new Net.PartySync(List.of()));
		}
		announce(server, g, Component.literal(gone + why).withStyle(ChatFormatting.GRAY));
		if (g.names.size() <= 1) {
			for (UUID m : g.names.keySet()) {
				st.of.remove(m);
				ServerPlayer o = server.getPlayerList().getPlayer(m);
				if (o != null) {
					o.sendSystemMessage(Component.literal("The party broke up").withStyle(ChatFormatting.GRAY));
					PacketDistributor.sendToPlayer(o, new Net.PartySync(List.of()));
				}
			}
			return;
		}
		if (g.leader.equals(u)) {
			g.leader = g.names.keySet().iterator().next();
			announce(server, g, Component.literal(g.names.get(g.leader) + " leads the party now").withStyle(ChatFormatting.GOLD));
		}
		sync(server, g);
	}

	// ---------------------------------------------------------------- the HUD

	private static void sync(MinecraftServer server, Group g) {
		for (UUID to : g.names.keySet()) {
			ServerPlayer tp = server.getPlayerList().getPlayer(to);
			if (tp == null) continue;
			List<Net.PartyMember> out = new ArrayList<>();
			g.names.forEach((u, name) -> {
				if (u.equals(to)) return;
				ServerPlayer o = server.getPlayerList().getPlayer(u);
				out.add(new Net.PartyMember(name, o != null ? o.getHealth() : 0, o != null ? o.getMaxHealth() : 20, u.equals(g.leader), o != null,
						o != null && o.level() == tp.level() && o.distanceTo(tp) < NEAR));
			});
			PacketDistributor.sendToPlayer(tp, new Net.PartySync(out));
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
