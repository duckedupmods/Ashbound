package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.UUID;

import com.google.gson.Gson;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;

import net.minecraft.ChatFormatting;
import net.minecraft.commands.Commands;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.server.packs.resources.SimpleJsonResourceReloadListener;
import net.minecraft.util.RandomSource;
import net.minecraft.util.profiling.ProfilerFiller;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.AddReloadListenerEvent;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * What the townsfolk say and do: each kind of NPC is a file in data/ashbound/npc/ (tools/efmob.py --npc) - their
 * name, title, and a conversation as named nodes. A node has lines (said together), options, and may jump straight
 * on to another node when a condition holds ("go_if": [["registered", "welcome"]]). An option has its text, a
 * condition to show it ("if"), where it goes ("go") and what it does ("do": close, shop, register, heal, quests,
 * flag:x). Lines can say {player}, {name}, {rank}, {points}, {next}.
 *
 * Forge NPCs carry "tags" (recipe, role, age, sex, rank); "@townsfolk/child" anywhere a kind is asked for (the
 * city's cast, /ashbound npc) picks one of those at random. Anyone with a shop is asked for their wares too.
 */
public final class Talk {
	private Talk() {}

	public record Option(String text, String cond, String go, String act) {}

	public record Node(List<String> lines, List<String[]> goIf, List<Option> options) {}

	public record Kind(String id, String name, String title, String start, Map<String, Node> nodes, List<String> tags) {}

	private static Map<String, Kind> KINDS = Map.of();

	public static Kind kind(String id) {
		return KINDS.get(id);
	}

	/** A kind for "@tag/tag..." (one of those carrying every tag, at random), or the id itself; null if none. */
	public static String resolve(String sel, RandomSource rnd) {
		if (!sel.startsWith("@")) return KINDS.containsKey(sel) ? sel : null;
		List<String> want = List.of(sel.substring(1).toLowerCase(Locale.ROOT).split("[/ ]+"));
		List<String> hits = KINDS.values().stream().filter(k -> k.tags().containsAll(want)).map(Kind::id).sorted().toList();
		return hits.isEmpty() ? null : hits.get(rnd.nextInt(hits.size()));
	}

	private record Session(int entity, String kind, List<Option> shown) {}

	private static final Map<UUID, Session> SESSIONS = new HashMap<>();

	// ---------------------------------------------------------------- loading

	private static void load(Map<ResourceLocation, JsonElement> files) {
		Map<String, Kind> out = new HashMap<>();
		for (var e : files.entrySet()) {
			if (!e.getKey().getNamespace().equals(Ashbound.ID)) continue;
			String id = e.getKey().getPath();
			try {
				JsonObject j = e.getValue().getAsJsonObject();
				Map<String, Node> nodes = new HashMap<>();
				for (Map.Entry<String, JsonElement> ne : j.getAsJsonObject("nodes").entrySet()) {
					JsonObject n = ne.getValue().getAsJsonObject();
					List<String> lines = new ArrayList<>();
					if (n.has("text")) {
						if (n.get("text").isJsonArray()) n.getAsJsonArray("text").forEach(t -> lines.add(t.getAsString()));
						else lines.add(n.get("text").getAsString());
					}
					List<String[]> goIf = new ArrayList<>();
					if (n.has("go_if")) n.getAsJsonArray("go_if").forEach(g -> goIf.add(new String[] {g.getAsJsonArray().get(0).getAsString(), g.getAsJsonArray().get(1).getAsString()}));
					List<Option> opts = new ArrayList<>();
					if (n.has("options")) {
						for (JsonElement oe : n.getAsJsonArray("options")) {
							JsonObject o = oe.getAsJsonObject();
							opts.add(new Option(o.get("text").getAsString(), str(o, "if"), str(o, "go"), str(o, "do")));
						}
					}
					nodes.put(ne.getKey(), new Node(lines, goIf, opts));
				}
				List<String> tags = new ArrayList<>();
				if (j.has("tags")) j.getAsJsonArray("tags").forEach(t -> tags.add(t.getAsString()));
				out.put(id, new Kind(id, j.get("name").getAsString(), str(j, "title"), j.has("start") ? j.get("start").getAsString() : "start", nodes, tags));
			} catch (Exception ex) {
				Ashbound.LOG.error("Couldn't read the NPC {}", e.getKey(), ex);
			}
		}
		KINDS = out;
		Ashbound.LOG.info("{} kinds of townsfolk", out.size());
	}

	private static String str(JsonObject o, String key) {
		return o.has(key) ? o.get(key).getAsString() : "";
	}

	// ---------------------------------------------------------------- the conversation

	public static void open(ServerPlayer p, Npc npc) {
		Kind k = npc.kind();
		if (k != null) show(p, npc, k, k.start());
	}

	public static boolean talking(Player p, Npc npc) {
		Session s = SESSIONS.get(p.getUUID());
		return s != null && s.entity() == npc.getId();
	}

	public static void close(ServerPlayer p) {
		if (SESSIONS.remove(p.getUUID()) != null) PacketDistributor.sendToPlayer(p, new Net.NpcTalk(-1, "", "", "", List.of()));
	}

	private static void show(ServerPlayer p, Npc npc, Kind k, String nodeId) {
		if (nodeId.equals(k.start())) {
			Journal.Quest q = Story.meeting(p, k.id());
			if (q != null) {
				say(p, npc, k, String.join("\n", q.say().stream().map(l -> fill(p, k, l)).toList()), List.of(new Option(q.reply(), "", k.start(), "mark:" + q.flag())));
				return;
			}
		}
		Node n = k.nodes().get(nodeId);
		for (int hops = 0; n != null && hops < 8; hops++) {
			String next = null;
			for (String[] g : n.goIf()) {
				if (holds(p, g[0])) {
					next = g[1];
					break;
				}
			}
			if (next == null) break;
			nodeId = next;
			n = k.nodes().get(next);
		}
		if (n == null) {
			close(p);
			npc.stopTalking();
			return;
		}
		List<Option> shown = new ArrayList<>();
		for (Option o : n.options()) if (o.cond().isEmpty() || holds(p, o.cond())) shown.add(o);
		// a shopkeeper whose own words don't mention their wares is asked for them first thing
		if (nodeId.equals(k.start()) && Shop.of(npc.shopId()) != null && shown.stream().noneMatch(o -> o.act().endsWith("shop")))
			shown.add(0, new Option("Show me your wares.", "", "", "shop"));
		String text = String.join("\n", n.lines().stream().map(l -> fill(p, k, l)).toList());
		// now and then they've a favour to ask, and say so before anything else (Errands)
		if (nodeId.equals(k.start()) && !k.id().equals(Intro.KIND)) {
			String hook = Errands.hook(p, npc);
			if (!hook.isEmpty()) text = hook;
			shown.addAll(0, Errands.options(p, npc));
		}
		say(p, npc, k, text, shown);
	}

	private static void say(ServerPlayer p, Npc npc, Kind k, String text, List<Option> shown) {
		SESSIONS.put(p.getUUID(), new Session(npc.getId(), k.id(), shown));
		PacketDistributor.sendToPlayer(p, new Net.NpcTalk(npc.getId(), k.name(), k.title(), text, shown.stream().map(o -> fill(p, k, o.text())).toList()));
	}

	/** For the self-test. */
	static boolean test(ServerPlayer p, String cond) {
		return holds(p, cond);
	}

	/** Conditions: what the townsfolk remember of you (flags), and the Guild's register. "!" for not, "&" for and. */
	private static boolean holds(ServerPlayer p, String cond) {
		if (cond.contains("&")) {
			for (String c : cond.split("&")) if (!holds(p, c.trim())) return false;
			return true;
		}
		boolean not = cond.startsWith("!");
		String c = not ? cond.substring(1) : cond;
		if (c.startsWith("flag:")) return Coins.flag(p, c.substring(5)) != not;
		if (c.startsWith("coins:")) return Coins.of(p) >= Integer.parseInt(c.substring(6)) != not;
		if (c.startsWith("has:")) {
			int colon = c.lastIndexOf(':');
			return count(p, c.substring(4, colon)) >= Integer.parseInt(c.substring(colon + 1)) != not;
		}
		boolean v = switch (c) {
			case "registered" -> Guild.of(p).registered();
			case "rank_up" -> Guild.of(p).canRankUp();
			case "max_rank" -> Guild.of(p).next() < 0;
			case "ready" -> Guild.anyReady(p);
			case "shards_ready" -> ColdForge.shardsReady(p);
			case "hurt" -> p.getHealth() < p.getMaxHealth();
			default -> Coins.flag(p, c);
		};
		return v != not;
	}

	/** "a|b": how many of either you carry. */
	private static int count(ServerPlayer p, String items) {
		int n = 0;
		for (ItemStack s : p.getInventory().items) if (matches(s, items)) n += s.getCount();
		return n;
	}

	private static boolean matches(ItemStack s, String items) {
		return !s.isEmpty() && List.of(items.split("\\|")).contains(BuiltInRegistries.ITEM.getKey(s.getItem()).toString());
	}

	private static void take(ServerPlayer p, String items, int n) {
		for (ItemStack s : p.getInventory().items) {
			if (n <= 0 || !matches(s, items)) continue;
			int t = Math.min(n, s.getCount());
			s.shrink(t);
			n -= t;
		}
	}

	private static void give(ServerPlayer p, String id, int n) {
		ItemStack s = new ItemStack(BuiltInRegistries.ITEM.get(ResourceLocation.parse(id)), n);
		if (!p.getInventory().add(s)) p.drop(s, false);
	}

	private static String fill(ServerPlayer p, Kind k, String s) {
		Guild.Card c = Guild.of(p);
		return s.replace("{player}", p.getName().getString()).replace("{name}", k.name()).replace("{rank}", c.rankName())
				.replace("{points}", String.valueOf(c.points())).replace("{next}", c.next() < 0 ? "-" : String.valueOf(c.next()));
	}

	public static void onPick(Net.NpcPick msg, ServerPlayer p) {
		Session s = SESSIONS.get(p.getUUID());
		if (s == null || s.entity() != msg.entity()) return;
		if (!(p.level().getEntity(msg.entity()) instanceof Npc npc) || npc.distanceTo(p) > 7) {
			close(p);
			return;
		}
		if (msg.option() < 0 || msg.option() >= s.shown().size()) {
			SESSIONS.remove(p.getUUID());
			npc.stopTalking();
			return;
		}
		Option o = s.shown().get(msg.option());
		Kind k = kind(s.kind());
		// "flag:x;shop": what they'll remember first, then the conversation's own ending
		String act = o.act();
		int semi = act.lastIndexOf(';');
		if (semi >= 0) {
			act(p, act.substring(0, semi));
			act = act.substring(semi + 1).trim();
		}
		if (act.startsWith("errand:")) {
			Errands.Reply r = k == null ? null : Errands.pick(p, npc, act);
			if (r != null) say(p, npc, k, r.text(), r.options());
			else {
				close(p);
				npc.stopTalking();
			}
			return;
		}
		switch (act) {
			case "close" -> {
				close(p);
				npc.stopTalking();
				return;
			}
			case "shop" -> {
				SESSIONS.remove(p.getUUID());
				Shop.open(p, npc);
				return;
			}
			case "forge" -> {
				close(p);
				npc.stopTalking();
				GateForge.open(p, npc);
				return;
			}
			case "intro" -> {
				close(p);
				npc.stopTalking();
				Intro.start(p, npc);
				return;
			}
			case "quests" -> {
				close(p);
				npc.stopTalking();
				Guild.board(p, npc);
				return;
			}
			case "" -> {}
			default -> act(p, act);
		}
		if (!o.go().isEmpty() && k != null) show(p, npc, k, o.go());
		else {
			close(p);
			npc.stopTalking();
		}
	}

	private static void act(ServerPlayer p, String act) {
		for (String a : act.split(";")) {
			a = a.trim();
			if (a.startsWith("flag:")) Coins.setFlag(p, a.substring(5));
			else if (a.startsWith("mark:")) Story.mark(p, a.substring(5));
			else if (a.equals("bind_ember")) ColdForge.bind(p);
			else if (a.equals("give_brand")) ColdForge.giveBrand(p);
			else if (a.equals("register")) {
				Guild.register(p);
				Story.mark(p, "story/registered");
			}
			else if (a.equals("rank_up")) Guild.rankUp(p);
			else if (a.equals("heal")) p.setHealth(p.getMaxHealth());
			else if (a.startsWith("pay:")) Coins.pay(p, Integer.parseInt(a.substring(4)));
			else if (a.startsWith("coins:")) Coins.give(p, Integer.parseInt(a.substring(6)));
			else if (a.startsWith("give:") || a.startsWith("take:")) {
				int colon = a.lastIndexOf(':');
				String items = a.substring(5, colon);
				int n = Integer.parseInt(a.substring(colon + 1));
				if (a.startsWith("give:")) give(p, items, n);
				else take(p, items, n);
			}
			else if (a.startsWith("effect:")) {   // effect:name:seconds:amplifier
				String[] e = a.split(":");
				BuiltInRegistries.MOB_EFFECT.getHolder(ResourceLocation.withDefaultNamespace(e[1]))
						.ifPresent(h -> p.addEffect(new MobEffectInstance(h, Integer.parseInt(e[2]) * 20, Integer.parseInt(e[3]))));
			}
		}
	}

	// ---------------------------------------------------------------- putting them in the world

	/** A townsperson of this kind (or "@tags") at x, y, z facing yaw, spending their day there as `mode` says (Npc). */
	public static Npc spawn(ServerLevelAccessor level, String kind, String shop, String mode, double x, double y, double z, float yaw) {
		String k = resolve(kind, level.getRandom());
		if (k == null && !kind.startsWith("@")) return null;
		Npc n = Townsfolk.NPC.get().create(level.getLevel());
		if (n == null) return null;
		n.moveTo(x, y, z, yaw, 0);
		n.setYHeadRot(yaw);
		n.setYBodyRot(yaw);
		n.setup(k != null ? k : kind, shop, mode);
		level.addFreshEntity(n);
		return n;
	}

	static void init() {
		NeoForge.EVENT_BUS.addListener((AddReloadListenerEvent e) -> e.addListener(new SimpleJsonResourceReloadListener(new Gson(), "npc") {
			@Override
			protected void apply(Map<ResourceLocation, JsonElement> files, ResourceManager rm, ProfilerFiller pf) {
				load(files);
			}
		}));
		NeoForge.EVENT_BUS.addListener((PlayerEvent.PlayerLoggedOutEvent e) -> SESSIONS.remove(e.getEntity().getUUID()));
		NeoForge.EVENT_BUS.addListener((PlayerEvent.PlayerLoggedInEvent e) -> {
			if (e.getEntity() instanceof ServerPlayer sp) Coins.sync(sp);
		});
		NeoForge.EVENT_BUS.addListener((RegisterCommandsEvent e) -> e.getDispatcher().register(Commands.literal("ashbound").requires(c -> c.hasPermission(2))
				.then(Commands.literal("coins").then(Commands.argument("n", IntegerArgumentType.integer(0)).executes(c -> {
					Coins.set(c.getSource().getPlayerOrException(), IntegerArgumentType.getInteger(c, "n"));
					return 1;
				})))
				.then(Commands.literal("npc")
						// a crowd of forge NPCs round you: /ashbound npc crowd 8 @townsfolk
						.then(Commands.literal("crowd").then(Commands.argument("n", IntegerArgumentType.integer(1, 40))
								.then(Commands.argument("tags", StringArgumentType.greedyString()).executes(c -> {
									ServerPlayer p = c.getSource().getPlayerOrException();
									String sel = StringArgumentType.getString(c, "tags");
									if (!sel.startsWith("@")) sel = "@" + sel;
									int n = IntegerArgumentType.getInteger(c, "n"), made = 0;
									ServerLevel l = p.serverLevel();
									for (int i = 0; i < n; i++) {
										double a = i * 2.39996, r = 2.5 + 1.1 * Math.sqrt(i);
										Vec3 at = p.position().add(Math.cos(a) * r, 0, Math.sin(a) * r);
										at = new Vec3(at.x, l.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, (int) Math.floor(at.x), (int) Math.floor(at.z)), at.z);
										float yaw = (float) Math.toDegrees(Math.atan2(p.getX() - at.x, at.z - p.getZ()));
										if (resolve(sel, l.getRandom()) != null && spawn(l, sel, "", "stroll", at.x, at.y, at.z, yaw) != null) made++;
									}
									if (made == 0) c.getSource().sendFailure(Component.literal("No forge NPCs tagged " + sel));
									return made;
								}))))
						.then(Commands.argument("kind", StringArgumentType.word()).executes(c -> {
							ServerPlayer p = c.getSource().getPlayerOrException();
							String kind = StringArgumentType.getString(c, "kind");
							if (resolve(kind, p.getRandom()) == null || spawn(p.serverLevel(), kind, kind, "stand", p.getX(), p.getY(), p.getZ(), p.getYRot() + 180f) == null) {
								c.getSource().sendFailure(Component.literal("No townsperson called " + kind));
								return 0;
							}
							return 1;
						})))));
	}
}
