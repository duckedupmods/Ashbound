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
	private static final String TRACK_JOB = "track:req:";
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

	/** The quest you picked, or once that's done, the first open one, in the book's order. */
	private static Journal.Quest followed(ServerPlayer p, Set<String> done) {
		for (String f : p.getData(Coins.FLAGS)) {
			if (!f.startsWith("track:")) continue;
			Journal.Quest q = Journal.of(f.substring(6));
			if (q != null && Journal.open(q, done)) return q;
		}
		for (Journal.Chapter c : Journal.CHAPTERS) for (Journal.Quest q : c.quests()) if (Journal.open(q, done)) return q;
		return null;
	}

	/** The guild request you've set the compass on, if it's still there to follow. */
	private static Net.GuildJob job(ServerPlayer p) {
		for (String f : p.getData(Coins.FLAGS)) {
			if (!f.startsWith(TRACK_JOB)) continue;
			String id = f.substring(TRACK_JOB.length());
			for (Net.GuildJob j : Guild.jobs(p)) if (j.id().equals(id)) return j;
		}
		return null;
	}

	static void state(ServerPlayer p) {
		Set<String> done = done(p);
		Journal.Quest q = followed(p, done);
		Net.GuildJob j = job(p);
		Set<String> told = new java.util.HashSet<>(done);
		if (Coins.flag(p, TAUGHT)) told.add(Journal.TAUGHT);
		PacketDistributor.sendToPlayer(p, new Net.JournalState(String.join(",", told), j != null ? "req:" + j.id() : q == null ? "" : q.key()));
		PacketDistributor.sendToPlayer(p, new Net.GuildJobs(Guild.jobs(p)));
		point(p);
	}

	private static final String TAUGHT = "journal_taught";

	/** From the Journal: follow this one; empty, just send the state. */
	static void pick(ServerPlayer p, String key) {
		if (key.equals(Journal.TAUGHT)) {
			Coins.setFlag(p, TAUGHT);
			return;
		}
		if (!key.isEmpty() && (Journal.of(key) != null || key.startsWith("req:"))) {
			List<String> flags = new ArrayList<>(p.getData(Coins.FLAGS));
			flags.removeIf(f -> f.startsWith("track:"));
			flags.add("track:" + key);
			p.setData(Coins.FLAGS, flags);
		}
		state(p);
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
		for (GateEntity g : p.serverLevel().getEntitiesOfClass(GateEntity.class, p.getBoundingBox().inflate(GATE_SEARCH), g -> g.rank() == rank))
			if (best == null || g.distanceToSqr(p) < best.distanceToSqr(p)) best = g;
		return best == null ? null : new int[] {best.getBlockX(), best.getBlockZ()};
	}

	private static void point(ServerPlayer p) {
		Net.GuildJob j = job(p);
		if (j != null) {
			PacketDistributor.sendToPlayer(p, new Net.QuestTrack(j.title(), j.x(), j.z(), j.has()));
			return;
		}
		Journal.Quest q = followed(p, done(p));
		boolean here = p.level().dimension() == net.minecraft.world.level.Level.OVERWORLD;   // inside a gate, nothing to point at
		int[] at = q == null || !here ? null : where(p, q.where());
		String title = q == null ? "" : here && at == null && q.where().startsWith("gate:") ? q.title() + " (no gate near)" : q.title();
		PacketDistributor.sendToPlayer(p, new Net.QuestTrack(title, at == null ? 0 : at[0], at == null ? 0 : at[1], at != null));
	}
}
