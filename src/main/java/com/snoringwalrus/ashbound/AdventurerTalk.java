package com.snoringwalrus.ashbound;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import javax.annotation.Nullable;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.player.Player;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * What adventurers say: a line over their head now and then (taunts, calls, small talk by rank, a nod when they see you,
 * thanks when you helped), and a few words when you talk to them, through the townsfolk's talk screen: who they are, and
 * what they've heard (a gate open near, a breakout on the board, the nearest town, a weapon in some ruin). The lines are
 * /ashbound/adventurer_lines.json.
 */
final class AdventurerTalk {
	private AdventurerTalk() {}

	static final Map<String, List<String>> LINES = load();
	private static final String RANKS = "FEDCBAS";

	private static Map<String, List<String>> load() {
		Map<String, List<String>> out = new HashMap<>();
		try (InputStream in = AdventurerTalk.class.getResourceAsStream("/ashbound/adventurer_lines.json")) {
			if (in == null) return out;
			JsonObject o = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
			for (var e : o.entrySet()) {
				if (!e.getValue().isJsonArray()) continue;
				List<String> l = new ArrayList<>();
				for (JsonElement s : e.getValue().getAsJsonArray()) l.add(s.getAsString());
				out.put(e.getKey(), l);
			}
		} catch (Exception ex) {
			Ashbound.LOG.error("adventurer lines not loaded", ex);
		}
		return out;
	}

	/** Low, middle or high: F-E, D-C, B and up. */
	static String tier(Adventurer a) {
		int r = RANKS.indexOf(a.rank());
		return r <= 1 ? "low" : r <= 3 ? "mid" : "high";
	}

	/** One of the lines under this key, filled in; "" if there are none. */
	static String line(String key, Adventurer a, @Nullable Player p, Map<String, String> more, RandomSource r) {
		List<String> l = LINES.get(key);
		if (l == null || l.isEmpty()) return "";
		String s = l.get(r.nextInt(l.size()));
		s = s.replace("{name}", a.getName().getString()).replace("The {party}", the(a.partyName, true)).replace("the {party}", the(a.partyName, false)).replace("{party}", a.partyName).replace("{rank}", a.rank());
		if (p != null) {
			s = s.replace("{player}", p.getName().getString());
			if (p instanceof ServerPlayer sp) s = s.replace("{player_rank}", String.valueOf(RANKS.charAt(Math.max(0, Math.min(6, Ranks.rank(sp))))));
		}
		for (var e : more.entrySet()) s = s.replace("{" + e.getKey() + "}", e.getValue());
		return s;
	}

	/** Which nod: by how far the player's rank is from theirs. */
	static String seeing(Adventurer a, ServerPlayer p) {
		int gap = Ranks.rank(p) - RANKS.indexOf(a.rank());
		return gap >= 2 ? "see_higher" : gap <= -2 ? "see_lower" : "see_same";
	}

	// ---------------------------------------------------------------- talking to them

	/** what's on the screen; what they've just asked of you, if anything (taken as it was said) */
	private record Session(int entity, List<String> acts, @Nullable Ask ask) {}

	/** A request as they put it: the favour itself, the words, and for a camp where it is and what's in it. */
	record Ask(String kind, Errands.Errand errand, String text, @Nullable net.minecraft.core.BlockPos camp, int count) {}

	private static final Map<UUID, Session> SESSIONS = new HashMap<>();

	private static final Map<String, String> ROLE = Map.of("tank", "shieldbearer", "breaker", "breaker", "striker", "blade", "lancer", "lancer",
			"ranger", "ranger", "rogue", "rogue", "black_mage", "black mage", "white_mage", "white mage");

	static void open(ServerPlayer p, Adventurer a) {
		// the hunter, the duelist: their scene has its own words
		if (Encounters.talk(p, a)) return;
		if (a.getTarget() != null) {
			a.bark("busy", p, Map.of(), true);
			return;
		}
		// the whole party stops to hear it out
		a.hold(p);
		for (Adventurer m : a.mates()) m.hold(p);
		String greet = a.owes(p) ? "greet_owed" : "greet_" + tier(a);
		show(p, a, line(greet, a, p, Map.of(), p.getRandom()));
	}

	private static void show(ServerPlayer p, Adventurer a, String text) {
		List<String> labels = new ArrayList<>(List.of("Who are you?", "Heard anything?"));
		List<String> acts = new ArrayList<>(List.of("who", "rumour"));
		if (asks(a, p)) {
			labels.add("Need a hand with anything?");
			acts.add("ask");
		}
		labels.add("Good hunting.");
		acts.add("bye");
		send(p, a, text, labels, acts, null);
	}

	private static void send(ServerPlayer p, Adventurer a, String text, List<String> labels, List<String> acts, @Nullable Ask ask) {
		SESSIONS.put(p.getUUID(), new Session(a.getId(), acts, ask));
		String title = a.partyName + "  -  " + a.rank() + "-rank " + ROLE.getOrDefault(a.role(), a.role());
		PacketDistributor.sendToPlayer(p, new Net.NpcTalk(a.getId(), a.getName().getString(), title, text, labels));
	}

	private static void close(ServerPlayer p) {
		if (SESSIONS.remove(p.getUUID()) != null) PacketDistributor.sendToPlayer(p, new Net.NpcTalk(-1, "", "", "", List.of()));
	}

	/** An option picked on the talk screen: true if it was one of ours (Talk.onPick asks us first). */
	static boolean pick(Net.NpcPick msg, ServerPlayer p) {
		Session s = SESSIONS.get(p.getUUID());
		if (s == null || s.entity() != msg.entity()) return false;
		if (!(p.level().getEntity(msg.entity()) instanceof Adventurer a) || a.distanceTo(p) > 8 || msg.option() < 0 || msg.option() >= s.acts().size()) {
			if (msg.option() < 0) SESSIONS.remove(p.getUUID());
			else close(p);
			return true;
		}
		RandomSource r = p.getRandom();
		switch (s.acts().get(msg.option())) {
			case "who" -> show(p, a, who(a, p));
			case "rumour" -> show(p, a, rumour(a, p, r));
			case "ask" -> {
				Ask ask = asks(a, p) ? offer(a, p, r) : null;
				if (ask == null) show(p, a, line("req_none", a, p, Map.of(), r));
				else send(p, a, ask.text(), List.of("I'll do it.", "Not today."), List.of("take", "no"), ask);
			}
			case "take" -> {
				if (s.ask() == null || !asks(a, p)) show(p, a, line("req_none", a, p, Map.of(), r));
				else if (Errands.full(p)) show(p, a, line("req_full", a, p, Map.of(), r));
				else if (take(a, p, s.ask(), r)) show(p, a, line("req_take_" + s.ask().kind(), a, p, Map.of(), r));
				else show(p, a, line("req_none", a, p, Map.of(), r));
			}
			case "no" -> {
				a.refused.add(p.getUUID());
				for (Adventurer m : a.mates()) m.refused.add(p.getUUID());
				show(p, a, line("req_no", a, p, Map.of(), r));
			}
			default -> {
				close(p);
				a.bark("bye", p, Map.of(), true);
			}
		}
		a.hold(p);
		return true;
	}

	// ---------------------------------------------------------------- what they'd ask of you

	/** They've something to ask, and not of you already: you've not said no, nor taken it. */
	static boolean asks(Adventurer a, ServerPlayer p) {
		return !a.ask.isEmpty() && !a.refused.contains(p.getUUID()) && Errands.find(p, "fav:" + Errands.ADV + a.party) == null;
	}

	/** What they ask, worked out as they say it: a camp needs somewhere for it (else they'd sooner you fetched them something), and a
	 * report or a fetch needs the Guild to leave it with. Null if there's nothing they can ask after all. */
	@Nullable
	static Ask offer(Adventurer a, ServerPlayer p, RandomSource r) {
		ServerLevel l = p.serverLevel();
		int rank = Math.max(0, RANKS.indexOf(a.rank()));
		int[] pay = Errands.pay(rank), desk = Story.desk();
		boolean guild = Guild.of(p).registered();
		String kind = a.ask;
		net.minecraft.core.BlockPos camp = null;
		if (kind.equals("camp")) {
			camp = Adventurers.town(a.blockPosition()) == null ? Adventurers.campSite(l, a.position(), r) : null;
			if (camp == null) kind = "fetch";
		}
		if (!kind.equals("camp") && desk == null) return null;
		Gear.Dungeon d = Adventurers.any(Adventurers.dungeons(a.rank().charAt(0)), r);
		String giver = Errands.ADV + a.party;
		long day = l.getDayTime() / 24000L;
		double mul;
		String title = line("req_title_" + kind, a, p, Map.of(), r), objective, text;
		int type, count = 1, x, z;
		String target;
		switch (kind) {
			case "camp" -> {
				count = 3 + r.nextInt(3);
				mul = 1.3;
				type = Errands.KILL;
				target = Errands.CAMP + a.party;
				x = camp.getX();
				z = camp.getZ();
				Map<String, String> w = new HashMap<>(where(p, x, z, d == null ? "gate" : d.title()));
				w.put("n", String.valueOf(count));
				text = line("req_ask_camp", a, p, w, r);
				objective = "Clear the camp, " + w.get("far") + " blocks " + w.get("dir") + ": " + count + " of them";
			}
			case "fetch" -> {
				if (d == null) return null;
				boolean rare = r.nextFloat() < 0.35f;
				String mat = Ashbound.ID + ":" + d.mats()[rare ? 1 : 0];
				var item = net.minecraft.core.registries.BuiltInRegistries.ITEM.get(net.minecraft.resources.ResourceLocation.parse(mat));
				count = rare ? 1 + r.nextInt(2) : 3 + r.nextInt(3);
				mul = rare ? 1.2 : 0.9;
				type = Errands.COLLECT;
				target = mat;
				x = desk[0];
				z = desk[1];
				String name = new net.minecraft.world.item.ItemStack(item).getHoverName().getString();
				text = line("req_ask_fetch", a, p, Map.of("n", String.valueOf(count), "item", name, "gate", d.title()), r);
				objective = "Leave " + count + " " + name + " at the Guild desk";
			}
			default -> {
				mul = 0.6;
				type = Errands.DELIVER;
				target = Errands.GUILD;
				x = desk[0];
				z = desk[1];
				text = line("req_ask_report", a, p, Map.of(), r);
				objective = "Carry their sealed report to the Guild desk";
			}
		}
		int coins = (int) Math.round(pay[0] * mul), points = guild ? (int) Math.round(pay[1] * mul) : 0;
		Errands.Errand e = new Errands.Errand(Errands.ADV_T + kind, type, target, count, 0, coins, points, giver, a.partyName, x, z, day, title, objective);
		String reward = coins + " coins" + (points > 0 ? ", +" + points + " GP" : "") + ", and maybe something from their pack";
		return new Ask(kind, e, text + "\n\n" + objective + "\nReward: " + reward, camp, count);
	}

	/** Taken on: on your list; a camp's monsters put there now (out of your sight), and the party sets off for it. */
	static boolean take(Adventurer a, ServerPlayer p, Ask ask, RandomSource r) {
		Errands.Errand e = ask.errand();
		List<Adventurer> all = new ArrayList<>(a.mates());
		all.add(a);
		if (ask.camp() != null) {
			int n = Adventurers.makeCamp(p.serverLevel(), ask.camp(), a.party.toString(), a.rank().charAt(0), ask.count(), r);
			if (n == 0) return false;
			e = new Errands.Errand(e.template(), e.type(), e.target(), n, 0, e.coins(), e.points(), e.giver(), e.giverName(), e.x(), e.z(), e.day(), e.title(),
					e.objective().replace(": " + ask.count() + " of them", ": " + n + " of them"));
		}
		if (!Errands.add(p, e)) return false;
		for (Adventurer m : all) {
			m.ask = "";
			if (ask.camp() == null) continue;
			if (m.mode.equals("camp")) m.breakCamp();
			m.mode = "roam";
			m.stay = -1;
			m.home = null;
			m.task = ask.camp();
		}
		return true;
	}

	/** A party's name after "the": "The Mudlarks" already has it, "Lantern Hounds" doesn't. */
	static String the(String party, boolean cap) {
		String bare = party.startsWith("The ") ? party.substring(4) : party;
		return (cap ? "The " : "the ") + bare;
	}

	/** What the Guild's receptionist says when you hand over a party's report, or what they asked for. */
	static String deskThanks(String party, ServerPlayer p) {
		List<String> l = LINES.getOrDefault("req_desk", List.of("From the {party}? Thank you, I'll see they hear of it."));
		return l.get(p.getRandom().nextInt(l.size())).replace("The {party}", the(party, true)).replace("the {party}", the(party, false)).replace("{party}", party).replace("{player}", p.getName().getString());
	}

	private static String who(Adventurer a, ServerPlayer p) {
		List<Adventurer> all = new ArrayList<>(a.mates());
		all.add(a);
		Adventurer lead = all.stream().min(java.util.Comparator.comparingInt(m -> m.slot)).orElse(a);
		// how long they've been at it: the same for a party every time you ask
		List<String> since = LINES.getOrDefault("since", List.of("a while"));
		String when = since.get(Math.floorMod(a.partyName.hashCode(), since.size()));
		return line("who", a, p, Map.of("count", String.valueOf(all.size()), "since", when, "lead", lead == a ? "I" : lead.getName().getString()), p.getRandom());
	}

	/** Something true about the world near you, if they know any: an open gate, a breakout or raid on the board, a town; else talk of a weapon. */
	static String rumour(Adventurer a, ServerPlayer p, RandomSource r) {
		ServerLevel l = p.serverLevel();
		List<String> heard = new ArrayList<>();
		GateEntity gate = l.getEntitiesOfClass(GateEntity.class, p.getBoundingBox().inflate(600)).stream()
				.min(java.util.Comparator.comparingDouble(g -> g.distanceToSqr(p))).orElse(null);
		if (gate != null) heard.add(line("rumour_gate", a, p, where(p, gate.getX(), gate.getZ(), GateEntity.RANKS[Math.max(0, Math.min(GateEntity.RANKS.length - 1, gate.rank()))]), r));
		Incidents.Incident inc = Incidents.live().stream().filter(i -> !i.over).min(java.util.Comparator.comparingDouble(i -> Math.hypot(i.x - p.getX(), i.z - p.getZ()))).orElse(null);
		if (inc != null && Math.hypot(inc.x - p.getX(), inc.z - p.getZ()) < 2000) heard.add(line("rumour_incident", a, p, where(p, inc.x, inc.z, inc.title()), r));
		Capital.Site town = null;
		double best = 3000;
		for (Capital.Site s : Capital.sites) {
			double d = Math.hypot(s.x - p.getX(), s.z - p.getZ());
			if (d < best && d > 120) {
				best = d;
				town = s;
			}
		}
		if (town != null) heard.add(line("rumour_town", a, p, where(p, town.x, town.z, town.title), r));
		List<WorldArms.Arm> big = WorldArms.ARMS.stream().filter(x -> x.tier() == WorldArms.Tier.LEGENDARY || x.tier() == WorldArms.Tier.EPIC).toList();
		if (!big.isEmpty()) {
			double ang = r.nextDouble() * Math.PI * 2;
			heard.add(line("rumour_weapon", a, p, where(p, p.getX() + Math.cos(ang) * 500, p.getZ() + Math.sin(ang) * 500, big.get(r.nextInt(big.size())).name()), r));
		}
		// a real lead before talk of weapons, mostly
		if (heard.isEmpty()) return line("rumour_none", a, p, Map.of(), r);
		int real = heard.size() - (big.isEmpty() ? 0 : 1);
		return real > 0 && r.nextFloat() < 0.8f ? heard.get(r.nextInt(real)) : heard.get(heard.size() - 1);
	}

	private static Map<String, String> where(ServerPlayer p, double x, double z, String what) {
		double dx = x - p.getX(), dz = z - p.getZ();
		// Minecraft's north is -z
		String[] dirs = {"east", "south-east", "south", "south-west", "west", "north-west", "north", "north-east"};
		int k = Math.floorMod((int) Math.round(Math.atan2(dz, dx) / (Math.PI / 4)), 8);
		long far = Math.max(50, Math.round(Math.hypot(dx, dz) / 50) * 50);
		return Map.of("dir", dirs[k], "far", String.valueOf(far), "what", what);
	}
}
