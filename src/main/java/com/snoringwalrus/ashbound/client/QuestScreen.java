package com.snoringwalrus.ashbound.client;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import com.snoringwalrus.ashbound.Journal;
import com.snoringwalrus.ashbound.Net;

import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.util.FormattedCharSequence;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * The Journal: the chapters down the side, the quests of the picked one, and the picked quest with what it asks and a
 * button to set the compass on it. Done, open and locked come from the server (Net.JournalState).
 */
public class QuestScreen extends Screen {
	private static final int SIDE = 130, DETAIL = 190, ROW = 18, GAP = 2;

	private static Set<String> done = new HashSet<>();
	private static String tracked = "";
	private static List<Journal.Quest> jobs = List.of();
	private static boolean joined;

	private int chapter, picked, scroll;
	private AshUi.AshButton follow;

	public QuestScreen() {
		super(Component.literal("Journal"));
	}

	/** What the server says. */
	public static void state(Net.JournalState m) {
		Set<String> was = done;
		done = new HashSet<>(List.of(m.done().isEmpty() ? new String[0] : m.done().split(",")));
		tracked = m.tracked();
		if (joined) for (String key : done) if (!was.contains(key) && Journal.of(key) != null) QuestHud.finished(Journal.of(key).title());
		joined = true;
	}

	/** What the Guild has for you and what's out there, as quests of a last chapter. */
	public static void jobs(Net.GuildJobs m) {
		List<Journal.Quest> out = new ArrayList<>();
		for (Net.GuildJob j : m.jobs())
			out.add(new Journal.Quest("req:" + j.id(), j.title(), j.text(), "", List.of(), "", "", List.of(), "", 0));
		jobs = out;
	}

	private static List<Journal.Chapter> chapters() {
		List<Journal.Chapter> out = new ArrayList<>(Journal.CHAPTERS);
		out.add(new Journal.Chapter("Guild Requests", "What you've taken, and what's out there.", jobs));
		return out;
	}

	/** A new world: what it tells you first is what you already had. */
	public static void leave() {
		joined = false;
	}

	/** The key: asks for the latest and opens. */
	static void open() {
		PacketDistributor.sendToServer(new Net.JournalPick(""));
		Minecraft.getInstance().setScreen(new QuestScreen());
	}

	private List<Journal.Quest> quests() {
		return chapters().get(chapter).quests();
	}

	private int pw() {
		return Math.min(width - 16, 640);
	}

	private int ph() {
		return Math.min(height - 16, 280);
	}

	private int px() {
		return (width - pw()) / 2;
	}

	private int py() {
		return (height - ph()) / 2;
	}

	private int listX() {
		return px() + SIDE + 6;
	}

	private int listW() {
		return pw() - SIDE - DETAIL - 12;
	}

	private int rows() {
		return Math.max(1, (ph() - 40) / (ROW + GAP));
	}

	private int dx() {
		return listX() + listW() + 6;
	}

	@Override
	protected void init() {
		follow = addRenderableWidget(new AshUi.AshButton(dx() + 10, py() + ph() - 34, DETAIL - 20, 22, Component.literal("FOLLOW"), b -> {
			Journal.Quest q = picked < quests().size() ? quests().get(picked) : null;
			if (q != null) PacketDistributor.sendToServer(new Net.JournalPick(q.key()));
		}, true));
	}

	@Override
	public boolean isPauseScreen() {
		return false;
	}

	@Override
	public boolean mouseClicked(double mx, double my, int button) {
		if (super.mouseClicked(mx, my, button)) return true;
		if (mx >= px() + 8 && mx < px() + SIDE - 2 && my >= py() + 32) {
			int c = (int) ((my - py() - 32) / (ROW + 6));
			if (c >= 0 && c < chapters().size()) {
				chapter = c;
				picked = 0;
				scroll = 0;
				return true;
			}
		}
		if (mx >= listX() + 8 && mx < listX() + listW() - 8 && my >= py() + 32) {
			int r = (int) ((my - py() - 32) / (ROW + GAP)) + scroll;
			if (r >= 0 && r < quests().size()) {
				picked = r;
				return true;
			}
		}
		return false;
	}

	@Override
	public boolean mouseScrolled(double mx, double my, double h, double v) {
		scroll = Math.max(0, Math.min(Math.max(0, quests().size() - rows()), scroll - (int) Math.signum(v)));
		return true;
	}

	private int colour(Journal.Quest q) {
		return done.contains(q.key()) ? 0xFF9BE07A : Journal.open(q, done) ? 0xFFFFD24A : 0xFF6A625A;
	}

	@Override
	public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
		g.fill(0, 0, width, height, 0x70000000);
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		super.render(g, mx, my, pt);
		int x = px(), y = py(), w = pw(), h = ph();
		// the chapters
		AshUi.panel(g, x, y, SIDE, h);
		AshUi.header(g, x, y, SIDE, 20, "JOURNAL");
		List<Journal.Chapter> all = chapters();
		for (int c = 0; c < all.size(); c++) {
			Journal.Chapter ch = all.get(c);
			int ry = y + 32 + c * (ROW + 6);
			boolean hov = mx >= x + 8 && mx < x + SIDE - 2 && my >= ry && my < ry + ROW + 4;
			AshUi.row(g, x + 8, ry, SIDE - 16, ROW + 4, c == chapter, hov);
			long n = ch.quests().stream().filter(q -> done.contains(q.key())).count();
			g.drawString(font, font.plainSubstrByWidth(ch.title(), SIDE - 28), x + 13, ry + 3, c == chapter ? AshUi.TEXT : AshUi.BODY, false);
			g.drawString(font, c == all.size() - 1 ? String.valueOf(ch.quests().size()) : n + " / " + ch.quests().size(), x + 13, ry + 12, AshUi.MUTED, false);
		}
		// its quests
		Journal.Chapter ch = all.get(chapter);
		AshUi.panel(g, listX(), y, listW(), h);
		AshUi.header(g, listX(), y, listW(), 20, ch.title().toUpperCase());
		for (int r = 0; r < rows() && r + scroll < ch.quests().size(); r++) {
			Journal.Quest q = ch.quests().get(r + scroll);
			int ry = y + 32 + r * (ROW + GAP);
			boolean hov = mx >= listX() + 8 && mx < listX() + listW() - 8 && my >= ry && my < ry + ROW;
			AshUi.row(g, listX() + 8, ry, listW() - 16, ROW, r + scroll == picked, hov);
			g.fill(listX() + 13, ry + 6, listX() + 19, ry + 12, colour(q));
			if (q.key().equals(tracked)) g.fill(listX() + 15, ry + 8, listX() + 17, ry + 10, 0xFF1A1208);
			boolean locked = !done.contains(q.key()) && !Journal.open(q, done);
			g.drawString(font, font.plainSubstrByWidth(locked ? "? ? ?" : q.title(), listW() - 40), listX() + 24, ry + 5, locked ? AshUi.MUTED : AshUi.BODY, false);
		}
		// the picked one
		AshUi.panel(g, dx(), y, DETAIL, h);
		Journal.Quest q = picked < ch.quests().size() ? ch.quests().get(picked) : null;
		boolean locked = q == null || (!done.contains(q.key()) && !Journal.open(q, done));
		AshUi.header(g, dx(), y, DETAIL, 20, q == null || locked ? "UNKNOWN" : done.contains(q.key()) ? "DONE" : "OPEN");
		int ty = y + 30;
		if (q != null) {
			Component title = Component.literal(locked ? "Not yet" : q.title()).withStyle(ChatFormatting.BOLD);
			for (FormattedCharSequence line : font.split(title, DETAIL - 20)) {
				g.drawString(font, line, dx() + 10, ty, AshUi.TEXT, true);
				ty += 11;
			}
			ty += 4;
			String text = locked ? "Finish what comes before it." : q.text();
			for (FormattedCharSequence line : font.split(Component.literal(text), DETAIL - 20)) {
				g.drawString(font, line, dx() + 10, ty, AshUi.BODY, false);
				ty += 10;
			}
		}
		boolean can = q != null && Journal.open(q, done);
		follow.active = can && !q.key().equals(tracked);
		follow.visible = can;
		follow.setMessage(Component.literal(q != null && q.key().equals(tracked) ? "FOLLOWING" : "FOLLOW"));
		follow.render(g, mx, my, pt);
	}
}
