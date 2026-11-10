package com.snoringwalrus.ashbound.client;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.snoringwalrus.ashbound.Kitchen;
import com.snoringwalrus.ashbound.Net;
import com.snoringwalrus.ashbound.Trades;

import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * A trade's bench (Cooking, Brewing, Alchemy), remade 11/7 (the user: "the UI is awful, show it cooking with a timer, faster the more you
 * make it", "everything should be centered", "the text is bad when highlighting", "we need something to let people know the recipes").
 * Three columns on one centre line:
 * <ul>
 * <li>the recipe book: "Can make" (you have its things), or every recipe of the trade, the ones not learnt yet with their needs hidden
 * (learnt from townsfolk, recipe pages, or guessing: Recipes), the ones above your level with the level that opens them. Each row: name and time, what it needs (green on hand, red not) and your mastery stars. Click: its things go in from your pack.</li>
 * <li>the pot: the recipe, the station's fire as a ring round the dish, the five slots, what's missing, how many, Cook; the rarities' chances
 * as one bar (hover it), your mastery of the recipe.</li>
 * <li>the fire: everything queued with its own bar, the Ready tray (click to take).</li>
 * </ul>
 * What's on the fire comes from the server (Net.KitchenState, each thing's start and done tick); the countdown runs on here.
 */
public class BenchScreen extends AbstractContainerScreen<Trades.Bench> {
	private static final int W = 430, H = 290;
	private static final int TOP = 24, BOTTOM = 198;                            // the three panels
	private static final int BOOK_X = 10, BOOK_W = 124, MID_X = 140, MID_W = 150, FIRE_X = 296, FIRE_W = 124;
	private static final int CX = W / 2, FIRE_CX = FIRE_X + FIRE_W / 2;
	private static final int ROW_Y = 58, ROW_H = 22, ROWS = 6;
	private static final int RING_Y = 74, RING_R = 26;
	private static final int QUEUE_Y = 40, QUEUE_ROWS = 3, TRAY_Y = 121, TRAY_N = 5, TILE = 20;
	private static final int BATCH_W = 14 + 4 + 24 + 4 + 14 + 8 + 56;
	private static final int GOLD = 0xFFF0C890, GREEN = 0xFF9CD070, PICK_FILL = 0xFF3C2414;
	private int scroll, amount = 1;
	private boolean all;
	private Trades.Good picked;

	public BenchScreen(Trades.Bench menu, Inventory inv, Component title) {
		super(menu, inv, title);
		imageWidth = W;
		imageHeight = H;
	}

	@Override
	protected void init() {
		super.init();
		int x = leftPos, y = topPos;
		addRenderableWidget(new AshUi.AshButton(x + BOOK_X + 4, y + 41, 56, 13, Component.literal("Can make"), b -> {
			all = false;
			scroll = 0;
		}, false));
		addRenderableWidget(new AshUi.AshButton(x + BOOK_X + BOOK_W - 60, y + 41, 56, 13, Component.literal("All recipes"), b -> {
			all = true;
			scroll = 0;
		}, false));
		boolean batch = menu.tier >= 1;
		int bw = batch ? BATCH_W : 56, bx = x + CX - bw / 2, by = y + 152;
		if (batch) {
			addRenderableWidget(new AshUi.AshButton(bx, by, 14, 16, Component.literal("-"), b -> amount = Math.max(1, amount - 1), false));
			addRenderableWidget(new AshUi.AshButton(bx + 46, by, 14, 16, Component.literal("+"), b -> amount = Math.min(16, amount + 1), false));
			bx += 68;
		}
		addRenderableWidget(new AshUi.AshButton(bx, by, 56, 16, Component.literal(menu.pos != null ? "Cook" : "Make"),
				b -> PacketDistributor.sendToServer(new Net.TradeAct(Trades.CRAFT, String.valueOf(amount))), true));
		if (menu.pos != null)
			addRenderableWidget(new AshUi.AshButton(x + FIRE_CX - 35, y + 166, 70, 14, Component.literal("Take all"),
					b -> PacketDistributor.sendToServer(new Net.TradeAct(Trades.TAKE_READY, "")), false));
	}

	// ---------------------------------------------------------------- what's known, what's on hand

	private Trades.Trade trade() {
		return Trades.trade(menu.kind.trade);
	}

	/** The kinds of thing on hand, in the pack and the slots (Meat 3, Herb 1...). */
	private Map<String, Integer> onHand() {
		Map<String, Integer> m = new HashMap<>();
		for (ItemStack s : minecraft.player.getInventory().items) {
			String k = s.isEmpty() ? null : Trades.kindOf(s);
			if (k != null) m.merge(k, s.getCount(), Integer::sum);
		}
		for (int i = 0; i < Trades.SLOTS_IN; i++) {
			ItemStack s = menu.slots.get(i).getItem();
			String k = s.isEmpty() ? null : Trades.kindOf(s);
			if (k != null) m.merge(k, s.getCount(), Integer::sum);
		}
		return m;
	}

	/** What a recipe still needs that isn't on hand (kind ids, one per missing thing). */
	private static List<String> missing(Trades.Good g, Map<String, Integer> have) {
		Map<String, Integer> left = new HashMap<>(have);
		List<String> out = new ArrayList<>();
		for (String n : g.needs()) {
			int got = left.getOrDefault(n, 0);
			if (got > 0) left.put(n, got - 1);
			else out.add(n);
		}
		return out;
	}

	private boolean known(Trades.Good g) {
		return Trades.knows(minecraft.player, g.id());
	}

	/** Known, and your trade is up to it. */
	private boolean makeable(Trades.Good g) {
		return Trades.canMake(minecraft.player, g);
	}

	private List<Trades.Good> book() {
		Map<String, Integer> have = onHand();
		List<Trades.Good> out = new ArrayList<>();
		for (Trades.Good g : Trades.GOODS.values())
			if (g.kind() == menu.kind && (all || makeable(g) && missing(g, have).isEmpty())) out.add(g);
		out.sort(Comparator.comparing((Trades.Good g) -> !known(g)).thenComparing((Trades.Good g) -> !makeable(g)).thenComparingInt(Trades.Good::level));
		return out;
	}

	private int knownCount() {
		int n = 0;
		for (Trades.Good g : Trades.GOODS.values()) if (g.kind() == menu.kind && known(g)) n++;
		return n;
	}

	private int total() {
		int n = 0;
		for (Trades.Good g : Trades.GOODS.values()) if (g.kind() == menu.kind) n++;
		return n;
	}

	/** The recipe the slots make (or the one last picked from the book). */
	private Trades.Good recipe() {
		List<String> k = new ArrayList<>();
		for (int i = 0; i < Trades.SLOTS_IN; i++) {
			ItemStack s = menu.slots.get(i).getItem();
			if (!s.isEmpty()) k.add(Trades.kindOf(s));
		}
		Trades.Good g = k.isEmpty() ? null : Trades.match(menu.kind, k);
		if (g != null && known(g)) return g;
		return k.isEmpty() ? picked : null;
	}

	private Trades.Good bookAt(double mx, double my) {
		int x = leftPos + BOOK_X, y = topPos + ROW_Y;
		if (mx < x || mx >= x + BOOK_W || my < y) return null;
		int i = (int) Math.floor((my - y) / ROW_H);
		if (i >= ROWS) return null;
		List<Trades.Good> b = book();
		return i + scroll < b.size() ? b.get(i + scroll) : null;
	}

	// ---------------------------------------------------------------- the fire, as the server last told it

	private long now() {
		return Net.clientKitchen.now() + (minecraft.level.getGameTime() - Net.clientKitchenAt);
	}

	private List<ItemStack> ready() {
		List<ItemStack> out = new ArrayList<>();
		var k = Net.clientKitchen;
		long t = now();
		for (int i = 0; i < k.items().size(); i++) if (k.done().get(i) <= t) out.add(k.items().get(i));
		return out;
	}

	/** Indices of the things still cooking or waiting, in order. */
	private List<Integer> queue() {
		List<Integer> out = new ArrayList<>();
		var k = Net.clientKitchen;
		long t = now();
		for (int i = 0; i < k.items().size(); i++) if (k.done().get(i) > t) out.add(i);
		return out;
	}

	/** How far along thing i is, 0..1 (0 while it waits its turn). */
	private float progress(int i) {
		var k = Net.clientKitchen;
		long s = k.start().get(i), d = k.done().get(i), t = now();
		return d <= s ? 1 : Mth.clamp((t - s) / (float) (d - s), 0, 1);
	}

	private int readyAt(double mx, double my) {
		int x0 = leftPos + FIRE_CX - (TRAY_N * TILE) / 2, y0 = topPos + TRAY_Y;
		if (mx < x0 || my < y0) return -1;
		int c = (int) ((mx - x0) / TILE), r = (int) ((my - y0) / TILE);
		if (c >= TRAY_N || r >= 2) return -1;
		int i = r * TRAY_N + c;
		return i < ready().size() ? i : -1;
	}

	/** The thing on the fire under the mouse: the big dish in the ring, or a queue row. */
	private ItemStack fireAt(double mx, double my) {
		var k = Net.clientKitchen;
		List<Integer> q = queue();
		int cx = leftPos + CX, cy = topPos + RING_Y;
		if (!q.isEmpty() && Math.abs(mx - cx) < 17 && Math.abs(my - cy) < 17) return k.items().get(q.get(0));
		if (menu.pos == null) return ItemStack.EMPTY;
		int rx = leftPos + FIRE_X + 5;
		for (int r = 0; r < QUEUE_ROWS && r < q.size(); r++) {
			int ry = topPos + QUEUE_Y + r * 20;
			if (mx >= rx && mx < leftPos + FIRE_X + FIRE_W - 5 && my >= ry - 1 && my < ry + 17) return k.items().get(q.get(r));
		}
		return ItemStack.EMPTY;
	}

	// ---------------------------------------------------------------- input

	@Override
	public boolean mouseClicked(double mx, double my, int button) {
		Trades.Good g = bookAt(mx, my);
		if (g != null) {
			picked = g;
			if (makeable(g)) PacketDistributor.sendToServer(new Net.TradeAct(Trades.FILL, g.id()));
			return true;
		}
		if (menu.pos != null && readyAt(mx, my) >= 0) {
			PacketDistributor.sendToServer(new Net.TradeAct(Trades.TAKE_READY, ""));
			return true;
		}
		return super.mouseClicked(mx, my, button);
	}

	@Override
	public boolean mouseScrolled(double mx, double my, double dx, double dy) {
		if (mx >= leftPos + BOOK_X && mx < leftPos + BOOK_X + BOOK_W && my < topPos + BOTTOM) {
			scroll = Math.max(0, Math.min(Math.max(0, book().size() - ROWS), scroll - (int) Math.signum(dy)));
			return true;
		}
		return super.mouseScrolled(mx, my, dx, dy);
	}

	// ---------------------------------------------------------------- drawing

	private void centred(GuiGraphics g, String s, int cx, int y, int colour, int maxW) {
		String t = font.plainSubstrByWidth(s, maxW);
		g.drawString(font, t, cx - font.width(t) / 2, y, colour, false);
	}

	private static String stars(int n) {
		return "★".repeat(n) + "☆".repeat(4 - n);
	}

	private String kindWord(String n) {
		String w = Trades.KIND_NAMES.getOrDefault(n, n);
		return w.length() > 6 ? w.substring(0, 5) + "." : w;
	}

	@Override
	protected void renderBg(GuiGraphics g, float pt, int mx, int my) {
		int x = leftPos, y = topPos;
		var p = minecraft.player;
		Trades.Trade t = trade();
		int lv = Trades.level(p, t.id());
		AshUi.panel(g, x, y, W, H);
		AshUi.header(g, x, y, W, 20, title.getString().toUpperCase());
		for (int[] c : new int[][] {{BOOK_X, BOOK_W}, {MID_X, MID_W}, {FIRE_X, FIRE_W}}) AshUi.inset(g, x + c[0], y + TOP, c[1], BOTTOM - TOP);
		Map<String, Integer> have = onHand();
		Trades.Good over = bookAt(mx, my), sel = recipe();
		book(g, x, y, mx, my, lv, have, over, sel);
		pot(g, x, y, have, sel);
		fire(g, x, y);
		AshUi.divider(g, x + 10, y + Trades.PACK_Y - 7, W - 20);
		for (int i = Trades.SLOTS_IN; i < menu.slots.size(); i++) {
			var s = menu.slots.get(i);
			AshUi.inset(g, x + s.x - 1, y + s.y - 1, 18, 18);
		}
	}

	private void book(GuiGraphics g, int x, int y, int mx, int my, int lv, Map<String, Integer> have, Trades.Good over, Trades.Good sel) {
		var p = minecraft.player;
		List<Trades.Good> b = book();
		g.drawString(font, "Recipe book", x + BOOK_X + 5, y + TOP + 5, AshUi.TEXT, false);
		String count = knownCount() + " of " + total();
		g.drawString(font, count, x + BOOK_X + BOOK_W - 5 - font.width(count), y + TOP + 5, AshUi.MUTED, false);
		for (int i = 0; i < ROWS && i + scroll < b.size(); i++) {
			Trades.Good gd = b.get(i + scroll);
			boolean learnt = known(gd), open = learnt && makeable(gd);
			int rx = x + BOOK_X + 3, ry = y + ROW_Y + i * ROW_H, rw = BOOK_W - 6 - (b.size() > ROWS ? 3 : 0), rh = ROW_H - 2;
			// the picked row: a dark ember fill and a bright rim, so its words stay readable
			if (gd == sel) {
				g.fill(rx, ry, rx + rw, ry + rh, PICK_FILL);
				g.renderOutline(rx, ry, rw, rh, AshUi.BLACK);
				g.renderOutline(rx + 1, ry + 1, rw - 2, rh - 2, AshUi.EMBER_LT);
			} else AshUi.row(g, rx, ry, rw, rh, false, gd == over);
			ItemStack icon = new ItemStack(Trades.ITEMS.get(gd.id()).get());
			g.renderItem(icon, rx + 2, ry + 2);
			if (!open) g.fill(rx + 2, ry + 2, rx + 18, ry + 18, 0xA0101010);
			int st = Kitchen.stars(Trades.madeCount(p, gd.id()));
			String right1 = open ? Kitchen.clock(Kitchen.seconds(gd, st)) : learnt ? t(lv, gd) : "";
			int r1 = rx + rw - 4 - font.width(right1);
			g.drawString(font, right1, r1, ry + 2, open ? AshUi.MUTED : AshUi.BAD, false);
			g.drawString(font, font.plainSubstrByWidth(gd.name(), r1 - (rx + 21) - 3), rx + 21, ry + 2, open ? AshUi.TEXT : learnt ? AshUi.BODY : AshUi.MUTED, false);
			String sts = stars(st);
			int r2 = rx + rw - 4 - font.width(sts);
			if (open) g.drawString(font, sts, r2, ry + 11, GOLD, false);
			if (!learnt) {                                         // what it needs and does is the secret
				g.drawString(font, "Not learnt", rx + 21, ry + 11, AshUi.BAD, false);
				continue;
			}
			Map<String, Integer> left = new HashMap<>(have);
			int nx = rx + 21;
			for (String n : gd.needs()) {
				int got = left.getOrDefault(n, 0);
				left.put(n, got - 1);
				String w = kindWord(n);
				if (nx + font.width(w) > (open ? r2 - 3 : rx + rw - 4)) break;
				g.drawString(font, w, nx, ry + 11, got > 0 ? GREEN : AshUi.BAD, false);
				nx += font.width(w) + 4;
			}
		}
		if (b.size() > ROWS) {                                    // a thin scrollbar on the right
			int sx = x + BOOK_X + BOOK_W - 5, sy = y + ROW_Y, sh = ROWS * ROW_H - 2;
			g.fill(sx, sy, sx + 2, sy + sh, 0xFF2A2622);
			int th = Math.max(10, sh * ROWS / b.size()), ty = sy + (sh - th) * scroll / Math.max(1, b.size() - ROWS);
			g.fill(sx, ty, sx + 2, ty + th, AshUi.EMBER_LT);
		}
		if (b.isEmpty()) {
			centred(g, "Nothing you can make", x + BOOK_X + BOOK_W / 2, y + ROW_Y + 16, AshUi.MUTED, BOOK_W - 8);
			centred(g, "with what you carry", x + BOOK_X + BOOK_W / 2, y + ROW_Y + 27, AshUi.MUTED, BOOK_W - 8);
			centred(g, "See All recipes", x + BOOK_X + BOOK_W / 2, y + ROW_Y + 42, AshUi.EMBER_LT, BOOK_W - 8);
		}
	}

	private String t(int lv, Trades.Good gd) {
		return "Lv " + gd.level();
	}

	private void pot(GuiGraphics g, int x, int y, Map<String, Integer> have, Trades.Good sel) {
		var p = minecraft.player;
		Trades.Trade t = trade();
		int lv = Trades.level(p, t.id()), cx = x + CX;
		centred(g, t.name() + " " + lv + ", " + Trades.rank(lv), cx, y + TOP + 5, AshUi.MUTED, MID_W - 8);
		var k = Net.clientKitchen;
		List<Integer> q = queue();
		int ci = q.isEmpty() ? -1 : q.get(0);
		float prog;
		String under;
		ItemStack dish;
		if (ci >= 0) {
			prog = progress(ci);
			under = "cooking  " + Kitchen.clock((k.done().get(ci) - now() + 19) / 20);
			dish = k.items().get(ci);
		} else {
			dish = sel != null ? new ItemStack(Trades.ITEMS.get(sel.id()).get()) : ItemStack.EMPTY;
			under = sel != null && known(sel) ? "takes " + Kitchen.clock(Kitchen.seconds(sel, Kitchen.stars(Trades.madeCount(p, sel.id())))) : "";
			prog = ready().isEmpty() ? 0 : 1;
		}
		ring(g, cx, y + RING_Y, RING_R, prog, ci >= 0);
		if (!dish.isEmpty()) {
			g.pose().pushPose();
			g.pose().translate(cx - 16, y + RING_Y - 16, 0);
			g.pose().scale(2, 2, 1);
			g.renderItem(dish, 0, 0);
			g.pose().popPose();
		} else AshUi.flame(g, cx - 3, y + RING_Y - 4);
		String head = ci >= 0 ? dish.getHoverName().getString() : sel != null ? sel.name() : "Pick a recipe";
		centred(g, head, cx, y + TOP + 16, ci >= 0 || sel != null ? AshUi.EMBER_LT : AshUi.MUTED, MID_W - 8);
		centred(g, under, cx, y + RING_Y + RING_R + 5, ci >= 0 ? GOLD : AshUi.MUTED, MID_W - 8);
		for (int i = 0; i < Trades.SLOTS_IN; i++) AshUi.inset(g, x + Trades.IN_X + i * 22 - 1, y + Trades.IN_Y - 1, 18, 18);
		// under the slots: what's in them, or what the picked recipe still lacks
		List<String> told = new ArrayList<>();
		for (int i = 0; i < Trades.SLOTS_IN; i++) {
			ItemStack s = menu.slots.get(i).getItem();
			if (!s.isEmpty()) told.add(Trades.KIND_NAMES.getOrDefault(Trades.kindOf(s), "?"));
		}
		String line;
		int col;
		if (!told.isEmpty()) {
			line = String.join(", ", told);
			col = AshUi.BODY;
		} else if (sel != null && !known(sel)) {
			line = "Not learnt yet";
			col = AshUi.BAD;
		} else if (sel != null && !makeable(sel)) {
			line = "Opens at " + t.name() + " " + sel.level();
			col = AshUi.BAD;
		} else if (sel != null && !missing(sel, have).isEmpty()) {
			List<String> m = new ArrayList<>();
			for (String n : missing(sel, have)) m.add(Trades.KIND_NAMES.getOrDefault(n, n));
			line = "Missing: " + String.join(", ", m);
			col = AshUi.BAD;
		} else {
			line = "Pick a recipe";
			col = AshUi.MUTED;
		}
		centred(g, line, cx, y + 141, col, MID_W - 8);
		if (menu.tier >= 1) centred(g, "x" + amount, cx - BATCH_W / 2 + 30, y + 156, AshUi.TEXT, 24);
		// the rarities as one bar (hover for the numbers)
		double[] odds = Trades.oddsAt(Trades.rarityLevel(p, menu), Trades.gateFloor(menu), Trades.cap(menu.tier), Trades.rolls(menu.tier));
		int ox = cx - 65, oy = y + 173, ow = 130, at = ox;
		g.fill(ox - 1, oy - 1, ox + ow + 1, oy + 5, AshUi.BLACK);
		Trades.Rarity[] rs = Trades.Rarity.values();
		for (int i = 0; i < 5; i++) {
			int w = i == 4 ? ox + ow - at : (int) Math.round(ow * odds[i] / 100);
			if (w > 0) g.fill(at, oy, at + w, oy + 4, 0xFF000000 | rs[i].colour.getColor());
			at += Math.max(0, w);
		}
		// your mastery of the recipe
		if (sel != null && known(sel)) {
			int made = Trades.madeCount(p, sel.id()), st = Kitchen.stars(made);
			int lo = st == 0 ? 0 : Kitchen.STARS_AT[st - 1], hi = st >= 4 ? lo : Kitchen.STARS_AT[st];
			centred(g, stars(st) + "  " + (st >= 4 ? "mastered" : "made " + made + " of " + hi), cx, y + 182, GOLD, MID_W - 8);
			AshUi.bar(g, cx - 50, y + 192, 100, 2, st >= 4 ? 1 : (made - lo) / (float) Math.max(1, hi - lo));
		}
	}

	private void fire(GuiGraphics g, int x, int y) {
		int fx = x + FIRE_CX;
		centred(g, menu.pos != null ? "On the fire" : "Made at once here", fx, y + TOP + 5, AshUi.TEXT, FIRE_W - 8);
		if (menu.pos == null) {
			centred(g, "Your own station", fx, y + TOP + 22, AshUi.MUTED, FIRE_W - 8);
			centred(g, "cooks over time", fx, y + TOP + 33, AshUi.MUTED, FIRE_W - 8);
			return;
		}
		var k = Net.clientKitchen;
		List<Integer> q = queue();
		if (q.isEmpty()) centred(g, "Nothing cooking", fx, y + QUEUE_Y + 12, AshUi.MUTED, FIRE_W - 8);
		for (int r = 0; r < QUEUE_ROWS && r < q.size(); r++) {
			int i = q.get(r), ry = y + QUEUE_Y + r * 20;
			int rx = x + FIRE_X + 5;
			g.renderItem(k.items().get(i), rx, ry);
			String clock = r == 0 ? Kitchen.clock((k.done().get(i) - now() + 19) / 20) : Kitchen.clock((k.done().get(i) - k.start().get(i)) / 20);
			int cw = font.width(clock);
			g.drawString(font, font.plainSubstrByWidth(k.items().get(i).getHoverName().getString(), FIRE_W - 30 - cw), rx + 19, ry, r == 0 ? AshUi.TEXT : AshUi.MUTED,
					false);
			g.drawString(font, clock, x + FIRE_X + FIRE_W - 5 - cw, ry, r == 0 ? GOLD : AshUi.MUTED, false);
			AshUi.bar(g, rx + 19, ry + 11, FIRE_W - 30, 2, progress(i));
		}
		centred(g, q.size() > QUEUE_ROWS ? "+" + (q.size() - QUEUE_ROWS) + " more waiting" : "", fx, y + QUEUE_Y + QUEUE_ROWS * 20 + 1, AshUi.MUTED, FIRE_W - 8);
		List<ItemStack> rd = ready();
		centred(g, "Ready" + (rd.isEmpty() ? "" : " (" + rd.size() + ")"), fx, y + TRAY_Y - 11, rd.isEmpty() ? AshUi.MUTED : GREEN, FIRE_W - 8);
		int tx = fx - (TRAY_N * TILE) / 2;
		for (int i = 0; i < 2 * TRAY_N; i++) {
			int sx = tx + (i % TRAY_N) * TILE + 1, sy = y + TRAY_Y + (i / TRAY_N) * TILE;
			AshUi.inset(g, sx, sy, 18, 18);
			if (i < rd.size()) g.renderItem(rd.get(i), sx + 1, sy + 1);
		}
	}

	/** The fire as a ring of embers round the dish: lit as far as it's come, clockwise from the top (green once done). */
	private static void ring(GuiGraphics g, int cx, int cy, int r, float k, boolean live) {
		int n = 72;
		for (int pass = 0; pass < 2; pass++)
			for (int i = 0; i < n; i++) {
				double a = -Math.PI / 2 + 2 * Math.PI * i / n;
				int px = cx + (int) Math.round(Math.cos(a) * r), py = cy + (int) Math.round(Math.sin(a) * r);
				if (pass == 0) g.fill(px - 2, py - 2, px + 2, py + 2, AshUi.BLACK);
				else g.fill(px - 1, py - 1, px + 1, py + 1, i < k * n ? (live ? AshUi.EMBER_LT : GREEN) : 0xFF3D3833);
			}
	}

	@Override
	protected void renderLabels(GuiGraphics g, int mx, int my) {
		// the header says what this is
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		super.render(g, mx, my, pt);
		renderTooltip(g, mx, my);
		Trades.Good gd = bookAt(mx, my);
		if (gd != null) {
			List<Component> lines = new ArrayList<>();
			lines.add(Component.literal(gd.name()).withStyle(ChatFormatting.GOLD));
			List<String> needs = new ArrayList<>();
			for (String n : gd.needs()) needs.add(Trades.KIND_NAMES.getOrDefault(n, n));
			lines.add(Component.literal("Needs: " + String.join(", ", needs)).withStyle(ChatFormatting.WHITE));
			if (!known(gd)) {
				lines.set(1, Component.literal("Not learnt yet").withStyle(ChatFormatting.RED));
			} else {
				for (String l : Trades.lines(gd, 1)) lines.add(Component.literal(l).withStyle(l.startsWith("-") ? ChatFormatting.RED : ChatFormatting.BLUE));
				if (!gd.stats().isEmpty() || !gd.fx().isEmpty()) lines.add(Component.literal(gd.kind().minutes + " min buff").withStyle(ChatFormatting.GRAY));
			}
			if (!known(gd)) {
				lines.add(Component.literal("Learn it: ask townsfolk, read recipe pages").withStyle(ChatFormatting.YELLOW));
				lines.add(Component.literal("from chests and monsters, or guess it here").withStyle(ChatFormatting.YELLOW));
				if (Trades.level(minecraft.player, trade().id()) < gd.level())
					lines.add(Component.literal("Made at " + trade().name() + " " + gd.level()).withStyle(ChatFormatting.RED));
			} else if (!makeable(gd)) lines.add(Component.literal("Opens at " + trade().name() + " " + gd.level()).withStyle(ChatFormatting.RED));
			else lines.add(Component.literal("Click: its things go in from your pack").withStyle(ChatFormatting.GRAY));
			g.renderComponentTooltip(font, lines, mx, my);
			return;
		}
		ItemStack hov = fireAt(mx, my);                          // the dish on the fire, or one waiting: what it'll do
		if (!hov.isEmpty()) {
			g.renderComponentTooltip(font, getTooltipFromItem(minecraft, hov), mx, my);
			return;
		}
		int ri = menu.pos != null ? readyAt(mx, my) : -1;
		if (ri >= 0) {
			List<Component> lines = new ArrayList<>(getTooltipFromItem(minecraft, ready().get(ri)));
			lines.add(Component.literal("Click to take everything ready").withStyle(ChatFormatting.GRAY));
			g.renderComponentTooltip(font, lines, mx, my);
			return;
		}
		int ox = leftPos + CX - 65, oy = topPos + 173;
		if (mx >= ox && mx < ox + 130 && my >= oy - 2 && my < oy + 6) {
			var p = minecraft.player;
			double[] odds = Trades.oddsAt(Trades.rarityLevel(p, menu), Trades.gateFloor(menu), Trades.cap(menu.tier), Trades.rolls(menu.tier));
			List<Component> lines = new ArrayList<>();
			lines.add(Component.literal("What comes out").withStyle(ChatFormatting.GOLD));
			Trades.Rarity[] rs = Trades.Rarity.values();
			for (int i = 0; i < 5; i++)
				lines.add(Component.literal(rs[i].title + "  " + (i > Trades.cap(menu.tier) ? "-" : Math.round(odds[i]) + "%")).withStyle(rs[i].colour));
			lines.add(Component.literal(menu.tier >= 2 ? "Your house: best of two rolls" : menu.tier == 1 ? "Your station: up to Epic" : "A borrowed stove: up to Rare")
					.withStyle(ChatFormatting.GRAY));
			g.renderComponentTooltip(font, lines, mx, my);
		}
	}
}
