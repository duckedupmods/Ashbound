package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * What the quest book reads. The game keeps its own truth in flags; each step that matters also grants a silent
 * advancement (data/ashbound/advancement/story, cold), and the book's tasks (FTB Quests, run/config/ftbquests, made by
 * tools/questbook.py) watch those. So nothing here knows the book exists but the book item given on first login.
 * The same list drives the Journal (key J) and the compass: this keeps which quest you're following and tells your
 * client where it lies.
 */
public final class Story {
	private Story() {}

	private static final int CITY_RADIUS = 260, GATE_SEARCH = 300;
	/** a flag per quest followed; NONE once you've unfollowed everything yourself, so the book doesn't pick one for you */
	private static final String TRACK = "track:", NONE = "track:none", REQ = "req:", FAV = "fav:", UNFOLLOW = "unfollow:", ABANDON = "abandon:";
	/** how many the compass carries at once; following one more lets go of the oldest */
	private static final int MOST_FOLLOWED = 5;
	/** From the city's centre (cast.json's receptionist). */
	private static final int[] DESK = {-12, -117};
	private static final ResourceLocation BOOK = ResourceLocation.fromNamespaceAndPath("ftbquests", "book");

	static void init() {
		NeoForge.EVENT_BUS.addListener((PlayerEvent.PlayerLoggedInEvent e) -> {
			if (!(e.getEntity() instanceof ServerPlayer p) || Coins.flag(p, "book_given")) return;
			Coins.setFlag(p, "book_given");
			Item book = BuiltInRegistries.ITEM.get(BOOK);
			if (book != Items.AIR) p.getInventory().add(new ItemStack(book));
		});
		NeoForge.EVENT_BUS.addListener((PlayerEvent.PlayerLoggedInEvent e) -> {
			if (e.getEntity() instanceof ServerPlayer p) state(p);
		});
		NeoForge.EVENT_BUS.addListener((PlayerTickEvent.Post e) -> {
			if (e.getEntity() instanceof ServerPlayer p && p.tickCount % 40 == 0) {
				lookForTheCity(p);
				arrive(p);
				point(p);
			}
		});
	}

	private static void lookForTheCity(ServerPlayer p) {
		if (Coins.flag(p, "found_capital")) return;
		int[] c = Capital.centre();
		if (c == null || p.level().dimension() != net.minecraft.world.level.Level.OVERWORLD) return;
		if (p.distanceToSqr(c[0], p.getY(), c[1]) > CITY_RADIUS * CITY_RADIUS) return;
		Coins.setFlag(p, "found_capital");
		mark(p, "story/capital");
	}

	/** Any open step that's done by getting there. */
	private static void arrive(ServerPlayer p) {
		if (p.level().dimension() != net.minecraft.world.level.Level.OVERWORLD) return;
		Set<String> done = done(p);
		for (Journal.Chapter c : Journal.CHAPTERS) for (Journal.Quest q : c.quests()) {
			if (q.reach() <= 0 || !Journal.open(q, done)) continue;
			int[] at = where(p, q.where());
			if (at != null && p.distanceToSqr(at[0], p.getY(), at[1]) < q.reach() * q.reach()) mark(p, q.flag());
		}
	}

	/** The step this townsperson has words for, when it's open to you. */
	static Journal.Quest meeting(ServerPlayer p, String kind) {
		Set<String> done = done(p);
		for (Journal.Chapter c : Journal.CHAPTERS) for (Journal.Quest q : c.quests()) if (kind.equals(q.who()) && Journal.open(q, done)) return q;
		return null;
	}

	/** A step done, for your party too: the Journal's flag, and ashbound:<path>, which the book may be watching. */
	public static void mark(ServerPlayer p, String path) {
		own(p, path);
		Party.share(p, path);
	}

	/** The same for you alone. */
	static void own(ServerPlayer p, String path) {
		if (!Coins.flag(p, "q:" + path)) {
			Coins.setFlag(p, "q:" + path);
			state(p);
		}
		var a = p.server.getAdvancements().get(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, path));
		if (a == null) return;
		for (String c : p.getAdvancements().getOrStartProgress(a).getRemainingCriteria()) p.getAdvancements().award(a, c);
	}

	// ---------------------------------------------------------------- the Journal and the compass

	private static Set<String> done(ServerPlayer p) {
		Set<String> out = new HashSet<>();
		for (Journal.Chapter c : Journal.CHAPTERS) for (Journal.Quest q : c.quests()) if (Coins.flag(p, "q:" + q.flag())) out.add(q.key());
		return out;
	}

	/**
	 * Everything you follow, in the order you picked it: story quests still open, requests still on your card or the board,
	 * favours you still owe. Followed nothing that's left, and never cleared the list yourself: the first open quest in the
	 * book's order, as it always was.
	 */
	static List<String> followed(ServerPlayer p, Set<String> done) {
		List<String> out = new ArrayList<>();
		List<Net.GuildJob> jobs = Guild.jobs(p);
		for (String f : p.getData(Coins.FLAGS)) {
			if (!f.startsWith(TRACK) || f.equals(NONE)) continue;
			String key = f.substring(TRACK.length());
			if (live(p, key, done, jobs) && !out.contains(key)) out.add(key);
		}
		if (out.isEmpty() && !p.getData(Coins.FLAGS).contains(NONE))
			for (Journal.Chapter c : Journal.CHAPTERS) for (Journal.Quest q : c.quests()) if (Journal.open(q, done)) return List.of(q.key());
		return out;
	}

	/** Still something to follow: open, still on the card or the board, still owed. */
	private static boolean live(ServerPlayer p, String key, Set<String> done, List<Net.GuildJob> jobs) {
		if (Chains.isKey(key)) return Chains.find(p, key) != null;
		if (key.startsWith(REQ)) return job(jobs, key) != null;
		if (key.startsWith(FAV)) return Errands.find(p, key) != null;
		Journal.Quest q = Journal.of(key);
		return q != null && Journal.open(q, done);
	}

	private static Net.GuildJob job(List<Net.GuildJob> jobs, String key) {
		for (Net.GuildJob j : jobs) if ((REQ + j.id()).equals(key)) return j;
		return null;
	}

	static void state(ServerPlayer p) {
		Set<String> done = done(p);
		Set<String> told = new java.util.HashSet<>(done);
		if (Coins.flag(p, TAUGHT)) told.add(Journal.TAUGHT);
		PacketDistributor.sendToPlayer(p, new Net.JournalState(String.join(",", told), String.join(",", followed(p, done))));
		PacketDistributor.sendToPlayer(p, new Net.GuildJobs(Guild.jobs(p), Guild.taken(p)));
		point(p);
	}

	private static final String TAUGHT = "journal_taught";

	/** From the Journal: follow this one too, "unfollow:" one, "abandon:" a request or a favour; empty, just send the state. */
	static void pick(ServerPlayer p, String key) {
		if (key.equals(Journal.TAUGHT)) {
			Coins.setFlag(p, TAUGHT);
			return;
		}
		if (key.startsWith(ABANDON)) {
			String what = key.substring(ABANDON.length());
			if (Chains.isKey(what)) Chains.abandon(p, what);
			else if (what.startsWith(REQ)) Guild.abandon(p, what.substring(REQ.length()));
			else if (what.startsWith(FAV)) Errands.abandon(p, what);
			unfollow(p, what);
		} else if (key.startsWith(UNFOLLOW)) {
			Set<String> done = done(p);
			List<String> now = followed(p, done);
			List<String> flags = new ArrayList<>(p.getData(Coins.FLAGS));
			flags.removeIf(f -> f.startsWith(TRACK));
			for (String k : now) if (!k.equals(key.substring(UNFOLLOW.length()))) flags.add(TRACK + k);   // the book's own pick becomes yours to drop
			if (flags.stream().noneMatch(f -> f.startsWith(TRACK))) flags.add(NONE);
			p.setData(Coins.FLAGS, flags);
		} else if (!key.isEmpty() && (Journal.of(key) != null || key.startsWith(REQ) || key.startsWith(FAV) || Chains.isKey(key))) {
			List<String> flags = new ArrayList<>(p.getData(Coins.FLAGS));
			flags.remove(NONE);
			if (!flags.contains(TRACK + key)) {
				if (flags.stream().noneMatch(f -> f.startsWith(TRACK))) for (String k : followed(p, done(p))) flags.add(TRACK + k);   // keep the book's pick beside it
				flags.add(TRACK + key);
			}
			List<String> mine = flags.stream().filter(f -> f.startsWith(TRACK)).toList();
			for (int i = 0; i < mine.size() - MOST_FOLLOWED; i++) flags.remove(mine.get(i));
			p.setData(Coins.FLAGS, flags);
		}
		state(p);
	}

	private static void unfollow(ServerPlayer p, String key) {
		List<String> flags = new ArrayList<>(p.getData(Coins.FLAGS));
		if (flags.remove(TRACK + key)) p.setData(Coins.FLAGS, flags);
	}

	/** Elowen's desk. */
	static int[] desk() {
		int[] c = Capital.centre();
		return c == null ? null : new int[] {c[0] + DESK[0], c[1] + DESK[1]};
	}

	static int[] where(ServerPlayer p, String code) {
		int[] c = Capital.centre();
		if (code.equals("capital")) return c;
		if (code.startsWith("at:")) {
			if (c == null) return null;
			String[] xz = code.substring(3).split(",");
			return new int[] {c[0] + Integer.parseInt(xz[0]), c[1] + Integer.parseInt(xz[1])};
		}
		if (!code.startsWith("gate:")) return null;
		int rank = "FEDCBAS".indexOf(code.charAt(5));
		GateEntity best = null;
		for (GateEntity g : p.serverLevel().getEntitiesOfClass(GateEntity.class, p.getBoundingBox().inflate(GATE_SEARCH), g -> g.rank() == rank && !g.sky()))
			if (best == null || g.distanceToSqr(p) < best.distanceToSqr(p)) best = g;
		return best == null ? null : new int[] {best.getBlockX(), best.getBlockZ()};
	}

	/** Every quest you follow, as marks on the compass. */
	private static void point(ServerPlayer p) {
		Set<String> done = done(p);
		List<Net.GuildJob> jobs = Guild.jobs(p);
		boolean here = p.level().dimension() == net.minecraft.world.level.Level.OVERWORLD;   // inside a gate, nothing to point at
		List<Net.QuestTrack> marks = new ArrayList<>();
		for (String key : followed(p, done)) {
			if (Chains.isKey(key)) {
				Net.QuestTrack t = Chains.track(p, key);
				if (t != null) marks.add(t);
			} else if (key.startsWith(FAV)) {
				Errands.Errand fav = Errands.find(p, key);
				// a letter goes to someone, not somewhere: only who asked has a place on the compass
				if (fav != null) marks.add(new Net.QuestTrack(fav.title(), fav.x(), fav.z(), (fav.type() != Errands.DELIVER || fav.giver().startsWith(Errands.ADV)) && here));
			} else if (key.startsWith(REQ)) {
				Net.GuildJob j = job(jobs, key);
				if (j != null) marks.add(new Net.QuestTrack(j.title(), j.x(), j.z(), j.has()));
			} else {
				Journal.Quest q = Journal.of(key);
				if (q == null) continue;
				int[] at = !here ? null : where(p, q.where());
				String title = here && at == null && q.where().startsWith("gate:") ? q.title() + " (no gate near)" : q.title();
				marks.add(new Net.QuestTrack(title, at == null ? 0 : at[0], at == null ? 0 : at[1], at != null));
			}
		}
		PacketDistributor.sendToPlayer(p, new Net.QuestTracks(marks));
	}
}
