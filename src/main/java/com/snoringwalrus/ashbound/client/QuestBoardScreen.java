package com.snoringwalrus.ashbound.client;

import java.util.ArrayList;
import java.util.List;

import com.snoringwalrus.ashbound.Guild;
import com.snoringwalrus.ashbound.Net;
import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * The guild's request board, at the receptionist, like the boards in the guild halls of the stories:
 * small papers crammed on dark wood, each tacked up crooked with its own pin, its rank's wax seal, what
 * it wants and what it pays in coins. Pick one and the right side tells you all of it, with Take It /
 * Report / Abandon. Along the top your rank and how far to the next evaluation. Requests more than one
 * rank above yours hang there too, greyed and locked (only the next rank's; higher ones aren't posted
 * for you).
 */
public class QuestBoardScreen extends Screen {
	/** Each rank's colour, F to SSS (the guild card and the HUD use these too). */
	static final int[] RANK_COLOUR = {0xFF8E8E8E, 0xFF5FAE4E, 0xFF3FA3B5, 0xFF4A74D8, 0xFF9A58D8, 0xFFD8A23A, 0xFFD84838, 0xFFB01838, 0xFFFFD860};
	private static final int DETAIL = 178;
	private static final int[] PAPER = {0xFFFFFFFF, 0xFFF4EBDA, 0xFFE6D6B8, 0xFFD8C6A2, 0xFFFFF8EC};
	private static final int[] PINS = {0xFFC0342A, 0xFFC89A3A, 0xFF8A8480};

	private int entity;
	private List<Net.QuestView> quests;
	private boolean takenTab;
	private String selected;
	private int page;
	private AshUi.AshButton take, report, abandon, leave;

	public QuestBoardScreen(Net.QuestBoard msg) {
		super(Component.literal("Request Board"));
		set(msg);
	}

	public void set(Net.QuestBoard msg) {
		entity = msg.entity();
		quests = msg.quests();
		if (selected == null || list().stream().noneMatch(q -> q.id().equals(selected))) {
			List<Net.QuestView> l = list();
			selected = l.isEmpty() ? null : l.get(0).id();
		}
	}

	public int entity() {
		return entity;
	}

	private int myRank() {
		return Guild.of(minecraft.player).rank();
	}

	private List<Net.QuestView> list() {
		List<Net.QuestView> out = new ArrayList<>();
		int me = minecraft == null || minecraft.player == null ? 0 : myRank();
		for (Net.QuestView q : quests) {
			boolean taken = q.state() == Guild.ACTIVE || q.state() == Guild.READY;
			if (taken != takenTab) continue;
			if (q.state() == Guild.LOCKED && q.rank() > me + 2) continue;
			out.add(q);
		}
		return out;
	}

	private int taken() {
		int n = 0;
		for (Net.QuestView q : quests) if (q.state() == Guild.ACTIVE || q.state() == Guild.READY) n++;
		return n;
	}

	private Net.QuestView sel() {
		for (Net.QuestView q : quests) if (q.id().equals(selected)) return q;
		return null;
	}

	// ---------------------------------------------------------------- layout

	private int pw() {
		return Math.min(width - 16, 620);
	}

	private int ph() {
		return Math.min(height - 16, 330);
	}

	private int px() {
		return (width - pw()) / 2;
	}

	private int py() {
		return (height - ph()) / 2;
	}

	private int bx() {
		return px() + 10;
	}

	private int by() {
		return py() + 44;
	}

	private int bw() {
		return pw() - DETAIL - 30;
	}

	private int bh() {
		return ph() - 54;
	}

	private int dx() {
		return px() + pw() - DETAIL - 10;
	}

	private int cols() {
		return Math.max(2, bw() / 96);
	}

	private int rowsFit() {
		return Math.max(1, bh() / 82);
	}

	private int perPage() {
		return cols() * rowsFit();
	}

	/** A note's place on the board: its cell, nudged and tilted by its id so it hangs the same way each time. */
	private record Note(Net.QuestView q, float cx, float cy, int w, int h, float rot, int pinX, int paper, int pin) {}

	private List<Note> notes() {
		List<Net.QuestView> l = list();
		int per = perPage(), from = Math.min(page * per, Math.max(0, l.size() - 1) / per * per);
		int cols = cols(), rows = rowsFit();
		float cw = bw() / (float) cols, ch = bh() / (float) rows;
		int w = (int) Math.min(cw - 8, 96), h = (int) Math.min(ch - 8, 86);
		List<Note> out = new ArrayList<>();
		for (int i = from; i < Math.min(l.size(), from + per); i++) {
			Net.QuestView q = l.get(i);
			java.util.Random r = new java.util.Random(q.id().hashCode() * 31L + 7);
			int k = i - from;
			float cx = bx() + cw * (k % cols + 0.5f) + (r.nextFloat() - 0.5f) * Math.max(0, cw - w - 4);
			float cy = by() + ch * (k / cols + 0.5f) + (r.nextFloat() - 0.5f) * Math.max(0, ch - h - 4);
			float rot = (r.nextFloat() - 0.5f) * 12f;
			int pinX = (int) (w * (0.32f + r.nextFloat() * 0.36f));
			out.add(new Note(q, cx, cy, w, h, rot, pinX, PAPER[r.nextInt(PAPER.length)], PINS[r.nextInt(PINS.length)]));
		}
		return out;
	}

	@Override
	protected void init() {
		int x = dx(), w = DETAIL, by = py() + ph() - 30;
		take = addRenderableWidget(new AshUi.AshButton(x, by, w - 58, 20, Component.literal("TAKE IT"), b -> act(Guild.ACCEPT), true));
		report = addRenderableWidget(new AshUi.AshButton(x, by, w - 58, 20, Component.literal("REPORT"), b -> act(Guild.REPORT), true));
		abandon = addRenderableWidget(new AshUi.AshButton(x, by, w - 58, 20, Component.literal("ABANDON"), b -> act(Guild.ABANDON), false));
		leave = addRenderableWidget(new AshUi.AshButton(x + w - 54, by, 54, 20, Component.literal("LEAVE"), b -> onClose(), false));
	}

	private void tab(boolean t) {
		takenTab = t;
		page = 0;
		List<Net.QuestView> l = list();
		selected = l.isEmpty() ? null : l.get(0).id();
	}

	private void act(int action) {
		Net.QuestView q = sel();
		if (q != null) PacketDistributor.sendToServer(new Net.QuestAct(entity, action, q.id()));
	}

	@Override
	public boolean isPauseScreen() {
		return false;
	}

	@Override
	public boolean mouseClicked(double mx, double my, int button) {
		if (super.mouseClicked(mx, my, button)) return true;
		int ty = py() + 27;
		if (my >= ty - 2 && my < ty + 12) {
			if (mx >= bx() && mx < bx() + 64) {
				tab(false);
				return true;
			}
			if (mx >= bx() + 72 && mx < bx() + 150) {
				tab(true);
				return true;
			}
		}
		List<Note> ns = notes();
		for (int i = ns.size() - 1; i >= 0; i--) {
			Note n = ns.get(i);
			if (Math.abs(mx - n.cx()) <= n.w() / 2f && Math.abs(my - n.cy()) <= n.h() / 2f) {
				selected = n.q().id();
				minecraft.getSoundManager().play(net.minecraft.client.resources.sounds.SimpleSoundInstance.forUI(net.minecraft.sounds.SoundEvents.BOOK_PAGE_TURN, 1.4f, 0.5f));
				return true;
			}
		}
		return false;
	}

	@Override
	public boolean mouseScrolled(double mx, double my, double sx, double sy) {
		int pages = Math.max(1, (list().size() + perPage() - 1) / perPage());
		page = Math.max(0, Math.min(pages - 1, page - (int) Math.signum(sy)));
		return true;
	}

	// ---------------------------------------------------------------- drawing

	private ItemStack hover;

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		super.render(g, mx, my, pt);
		if (hover != null) g.renderTooltip(font, hover, mx, my);
	}

	@Override
	public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
		g.fill(0, 0, width, height, 0x70000000);
		int x = px(), y = py(), w = pw(), h = ph();
		AshUi.panel(g, x, y, w, h);
		AshUi.header(g, x, y, w, 20, null);
		AshUi.diamond(g, x + 12, y + 9);
		g.drawString(font, Component.literal("REQUEST BOARD").withStyle(ChatFormatting.BOLD), x + 22, y + 8, AshUi.TEXT, true);
		g.drawString(font, "ADVENTURERS' GUILD", x + 30 + font.width(Component.literal("REQUEST BOARD").withStyle(ChatFormatting.BOLD)), y + 8, 0xFF7D756A, false);
		card(g, x + w - 12, y + 5);
		// tabs
		int ty = y + 27;
		tabLabel(g, "THE BOARD", bx(), ty, !takenTab);
		tabLabel(g, "TAKEN " + taken() + "/" + Guild.MAX_ACTIVE, bx() + 72, ty, takenTab);
		List<Net.QuestView> l = list();
		int pages = Math.max(1, (l.size() + perPage() - 1) / perPage());
		if (pages > 1) {
			String pg = "page " + (Math.min(page, pages - 1) + 1) + "/" + pages + "  (scroll)";
			g.drawString(font, pg, bx() + bw() - font.width(pg), ty, AshUi.DIM, false);
		}
		// the board
		int bx = bx(), by = by(), bw = bw(), bh = bh();
		g.blitSprite(AshUi.WOOD, bx, by, bw, bh);
		g.fillGradient(bx, by, bx + bw, by + 16, 0x90000000, 0x00000000);
		g.fillGradient(bx, by + bh - 16, bx + bw, by + bh, 0x00000000, 0x90000000);
		g.renderOutline(bx - 1, by - 1, bw + 2, bh + 2, AshUi.BLACK);
		g.renderOutline(bx, by, bw, bh, 0xFF4A3A2A);
		g.enableScissor(bx + 1, by + 1, bx + bw - 1, by + bh - 1);
		Note picked = null;
		for (Note n : notes()) {
			if (n.q().id().equals(selected)) picked = n;
			else note(g, n, false);
		}
		if (picked != null) note(g, picked, true);
		g.disableScissor();
		if (l.isEmpty()) {
			String s = takenTab ? "You haven't taken any requests." : "The board is bare. Come back at dawn.";
			g.drawString(font, s, bx + (bw - font.width(s)) / 2, by + bh / 2 - 4, 0xFFCFC6B8, true);
		}
		// the line between the board and the one picked
		g.fill(dx() - 9, by, dx() - 8, by + bh, AshUi.BLACK);
		g.fill(dx() - 8, by, dx() - 7, by + bh, AshUi.LINE);
		detail(g, mx, my);
	}

	private void tabLabel(GuiGraphics g, String s, int x, int y, boolean on) {
		Component c = Component.literal(s).withStyle(ChatFormatting.BOLD);
		g.drawString(font, c, x, y, on ? 0xFFF2EADC : 0xFF8A8076, true);
		if (on) g.fill(x, y + 10, x + font.width(c), y + 11, AshUi.EMBER_C);
	}

	/** One paper on the board, tacked up crooked. */
	private void note(GuiGraphics g, Note n, boolean picked) {
		Net.QuestView q = n.q();
		int w = n.w(), h = n.h(), l = -w / 2, t = -h / 2;
		boolean locked = q.state() == Guild.LOCKED;
		g.pose().pushPose();
		g.pose().translate(n.cx(), n.cy(), 0);
		g.pose().mulPose(com.mojang.math.Axis.ZP.rotation(n.rot() * (float) Math.PI / 180f));
		if (picked) g.pose().scale(1.06f, 1.06f, 1f);
		// its shadow on the wood, then the paper
		g.fill(l + 2, t + 3, l + w + 2, t + h + 3, picked ? 0x90000000 : 0x60000000);
		if (picked) {
			g.fill(l - 3, t - 3, l + w + 3, t + h + 3, AshUi.EMBER_C);
			g.fill(l - 2, t - 2, l + w + 2, t + h + 2, 0xFF1A0A04);
		}
		int paper = locked ? 0xFF6A6058 : n.paper();
		AshUi.tinted(g, AshUi.PARCHMENT, l, t, w, h, paper);
		g.renderOutline(l, t, w, h, 0x903A2A16);
		g.fillGradient(l + 1, t + h - 10, l + w - 1, t + h - 1, 0x00000000, 0x30503010);
		// the pin
		AshUi.tinted(g, AshUi.PIN, l + n.pinX() - 3, t + 1, 6, 6, n.pin());
		// rank seal
		AshUi.seal(g, l + w - 17, t + 3, 14, q.rank());
		int ink = locked ? 0xFF2A2420 : AshUi.INK;
		// the title, two lines at most
		int ly = t + 9;
		int lines = 0;
		for (FormattedCharSequence line : font.split(Component.literal(q.title()).withStyle(ChatFormatting.BOLD), w - 24)) {
			if (lines++ == 2) break;
			g.drawString(font, line, l + 5, ly, ink, false);
			ly += 9;
		}
		// what it wants: its item and how many
		ItemStack icon = icon(q.icon());
		int iy = t + h - 31;
		if (!icon.isEmpty()) g.renderItem(icon, l + 4, iy);
		String want;
		if (q.state() == Guild.ACTIVE || q.state() == Guild.READY) want = q.progress() + "/" + q.count();
		else if (locked) want = "LOCKED";
		else want = (q.objective().startsWith("Slay") ? "slay " : "bring ") + q.count();
		g.drawString(font, want, l + 22, iy + 5, locked ? 0xFF4A2A20 : AshUi.INK_RED, false);
		if (q.state() == Guild.ACTIVE || q.state() == Guild.READY) {
			int bw = w - 10, bx = l + 5, byy = iy + 17;
			g.fill(bx, byy, bx + bw, byy + 3, 0x50503010);
			g.fill(bx, byy, bx + (int) (bw * Math.min(1f, q.progress() / (float) Math.max(1, q.count()))), byy + 3, q.state() == Guild.READY ? 0xFF4E8A44 : 0xFFA0300C);
		}
		// what it pays
		AshUi.coin(g, l + 5, t + h - 11);
		g.drawString(font, String.format("%,d", q.coins()), l + 16, t + h - 10, ink, false);
		// a stamp when it's done
		if (q.state() == Guild.READY) {
			g.pose().pushPose();
			g.pose().translate(l + w - 26, t + h - 26, 0);
			g.pose().mulPose(com.mojang.math.Axis.ZP.rotation(-0.22f));
			String st = "REPORT";
			int sw = font.width(Component.literal(st).withStyle(ChatFormatting.BOLD));
			g.renderOutline(-sw / 2 - 3, -6, sw + 6, 13, 0xE0B8401A);
			g.drawString(font, Component.literal(st).withStyle(ChatFormatting.BOLD), -sw / 2, -3, 0xE0B8401A, false);
			g.pose().popPose();
		}
		g.pose().popPose();
	}

	private static ItemStack icon(String id) {
		try {
			var it = BuiltInRegistries.ITEM.get(ResourceLocation.parse(id));
			return new ItemStack(it);
		} catch (Exception e) {
			return ItemStack.EMPTY;
		}
	}

	/** Your rank, along the right of the header: its seal, how far to the next evaluation. */
	private void card(GuiGraphics g, int right, int y) {
		Guild.Card c = Guild.of(minecraft.player);
		int next = c.next(), prev = Guild.NEED[c.rank()];
		float k = next < 0 ? 1 : Math.min(1f, (c.points() - prev) / (float) Math.max(1, next - prev));
		String gp = next < 0 ? c.points() + " GP" : c.points() + "/" + next + " GP";
		int bw = 90;
		int bx = right - bw;
		g.drawString(font, gp, right - font.width(gp), y + 1, AshUi.EMBER_LT, false);
		String to = c.canRankUp() ? "EVALUATION READY" : next < 0 ? "SSS" : "TO " + Guild.RANKS[Math.min(Guild.RANKS.length - 1, c.rank() + 1)] + "-RANK";
		g.drawString(font, to, right - font.width(gp) - 6 - font.width(to), y + 1, c.canRankUp() ? 0xFF8AD070 : AshUi.LABEL, false);
		AshUi.bar(g, bx, y + 11, bw, 3, k);
		AshUi.seal(g, bx - 18, y - 1, 16, c.rank());
	}

	/** The request picked: all of it, and what you can do about it. */
	private void detail(GuiGraphics g, int mx, int my) {
		int x = dx(), y = by(), w = DETAIL;
		Net.QuestView q = sel();
		take.visible = report.visible = abandon.visible = false;
		hover = null;
		if (q == null) return;
		AshUi.seal(g, x, y, 22, q.rank());
		int ty = y + 2;
		for (FormattedCharSequence line : font.split(Component.literal(q.title()).withStyle(ChatFormatting.BOLD), w - 28)) {
			g.drawString(font, line, x + 27, ty, AshUi.TEXT, true);
			ty += 10;
		}
		g.drawString(font, Guild.RANKS[q.rank()] + "-RANK REQUEST", x + 27, ty, AshUi.EMBER_LT, false);
		ty = Math.max(ty + 14, y + 28);
		for (FormattedCharSequence line : font.split(Component.literal(q.text()).withStyle(ChatFormatting.ITALIC), w)) {
			g.drawString(font, line, x, ty, 0xFFB9AB90, false);
			ty += 10;
		}
		ty += 4;
		AshUi.divider(g, x, ty, w);
		ty += 7;
		g.drawString(font, "TASK", x, ty, AshUi.LABEL, false);
		ty += 11;
		AshUi.diamond(g, x, ty + 1);
		g.drawString(font, font.plainSubstrByWidth(q.objective(), w - 10), x + 9, ty, AshUi.BODY, true);
		ty += 12;
		if (q.state() == Guild.ACTIVE || q.state() == Guild.READY) {
			AshUi.bar(g, x + 1, ty + 1, w - 40, 4, q.progress() / (float) Math.max(1, q.count()));
			String pr = q.progress() + " / " + q.count();
			g.drawString(font, pr, x + w - font.width(pr), ty, q.state() == Guild.READY ? 0xFF8AD070 : AshUi.MUTED, false);
			ty += 12;
		}
		AshUi.divider(g, x, ty, w);
		ty += 7;
		g.drawString(font, "REWARD", x, ty, AshUi.LABEL, false);
		ty += 11;
		// tiles: coins, guild points, then any items
		int tx = x;
		AshUi.tile(g, tx, ty, 22, 3);
		g.blitSprite(AshUi.COIN, tx + 4, ty + 4, 14, 14);
		reward(g, tx, ty, String.format("%,d", q.coins()));
		tx += 30;
		AshUi.tile(g, tx, ty, 22, 2);
		g.renderItem(new ItemStack(Guild.CARD_ITEM.get()), tx + 3, ty + 3);
		reward(g, tx, ty, "+" + q.points() + " GP");
		tx += 30;
		hover = null;
		for (String gift : q.gifts()) {
			if (tx + 22 > x + w) break;
			String[] p = gift.split("\\*");
			ItemStack s = icon(p[0]);
			if (s.isEmpty()) continue;
			s.setCount(p.length > 1 ? Integer.parseInt(p[1]) : 1);
			AshUi.tile(g, tx, ty, 22, 1);
			g.renderItem(s, tx + 3, ty + 3);
			reward(g, tx, ty, "x" + s.getCount());
			if (mx >= tx && mx < tx + 22 && my >= ty && my < ty + 22) hover = s;
			tx += 30;
		}
		// what you can do
		int bottom = py() + ph() - 30;
		switch (q.state()) {
			case Guild.AVAILABLE -> {
				take.visible = true;
				take.active = taken() < Guild.MAX_ACTIVE;
				if (!take.active) g.drawString(font, "You can carry " + Guild.MAX_ACTIVE + " at a time", x, bottom - 12, AshUi.DIM, false);
			}
			case Guild.ACTIVE -> abandon.visible = true;
			case Guild.READY -> report.visible = true;
			case Guild.LOCKED -> g.drawString(font, "Needs " + Guild.RANKS[Math.max(0, q.rank() - 1)] + "-rank or higher", x, bottom + 6, AshUi.BAD, false);
			default -> {}
		}
	}

	private void reward(GuiGraphics g, int tx, int ty, String s) {
		g.pose().pushPose();
		g.pose().translate(tx + 11, ty + 25, 0);
		g.pose().scale(0.75f, 0.75f, 1f);
		g.drawString(font, s, -font.width(s) / 2, 0, AshUi.TEXT, true);
		g.pose().popPose();
	}
}
