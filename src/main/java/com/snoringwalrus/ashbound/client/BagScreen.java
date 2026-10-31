package com.snoringwalrus.ashbound.client;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;

import org.lwjgl.glfw.GLFW;

import com.snoringwalrus.ashbound.Bag;
import com.snoringwalrus.ashbound.Net;
import com.snoringwalrus.ashbound.Tidy;

import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * The Bottomless Bag (Bag): a search box and how it's sorted, tabs by what things are, a grid of everything in it with
 * real counts, and your own inventory under that. The server does all the moving.
 *
 * The screen's corner (leftPos, topPos) is where the inventory starts, so its slots can stay put in the Menu whatever
 * height the grid gets; the panel is measured from px, py.
 */
public class BagScreen extends AbstractContainerScreen<Bag.Menu> implements MenuTabs.Panel {
	private static final int COLS = 12, CELL = 20, W = 268, TOP = 62, BELOW = 90, MOST_ROWS = 8, FEWEST_ROWS = 3;
	private static final int GRID_X = 10, BAR_X = 254, BAR_W = 6;
	private static final String[] TABS = {"All", "Arms", "Armour", "Food", "Goods", "Blocks"};
	private static final String[] SORTS = {"Most", "A-Z", "Rarest"};
	/** Stay as you left them: you go looking in the same places. */
	private static int tab, sort;

	private EditBox search;
	private AshUi.AshButton sorted;
	private int px, py, rows, scroll;
	private boolean dragging;
	private Net.BagLines seen;
	private boolean stale = true;
	private List<Net.BagLine> shown = List.of();
	private Net.BagLine hover;

	public BagScreen(Bag.Menu menu, Inventory inv, Component title) {
		super(menu, inv, title);
	}

	// ---------------------------------------------------------------- layout

	private int gridY() {
		return py + TOP;
	}

	private int panelH() {
		return TOP + rows * CELL + BELOW;
	}

	@Override
	public int panelTop() {
		return py;
	}

	@Override
	protected void init() {
		rows = Math.max(FEWEST_ROWS, Math.min(MOST_ROWS, (height - 16 - TOP - BELOW) / CELL));
		imageWidth = W;
		imageHeight = panelH();
		String had = search == null ? "" : search.getValue();
		super.init();
		px = leftPos;
		py = topPos;
		topPos = gridY() + rows * CELL + 6;
		search = new EditBox(font, px + 16, py + 29, W - 90, 10, Component.literal("Search"));
		search.setBordered(false);
		search.setMaxLength(50);
		search.setTextColor(0xFFFFFFFF);
		search.setHint(Component.literal("Search the bag").withStyle(s -> s.withColor(AshUi.DIM & 0xFFFFFF)));
		search.setValue(had);
		search.setResponder(s -> stale = true);
		addRenderableWidget(search);
		sorted = addRenderableWidget(new AshUi.AshButton(px + W - 66, py + 25, 56, 16, sortName(), b -> {
			sort = (sort + 1) % SORTS.length;
			b.setMessage(sortName());
			stale = true;
		}, false));
		int rx = px + Bag.SLOTS_X + 168, rw = W - 10 - (Bag.SLOTS_X + 168), by = topPos + Bag.HOTBAR_Y;
		addRenderableWidget(new AshUi.AshButton(rx, by - 20, rw, 16, Component.literal("Put in all"), b -> send(Bag.PUT_PACK, ItemStack.EMPTY), true));
		addRenderableWidget(new AshUi.AshButton(rx, by, rw, 16, Component.literal("Put in like"), b -> send(Bag.PUT_LIKE, ItemStack.EMPTY), false));
	}

	private static Component sortName() {
		return Component.literal(SORTS[sort]);
	}

	private static void send(int what, ItemStack item) {
		PacketDistributor.sendToServer(new Net.BagAct(what, item));
	}

	// ---------------------------------------------------------------- what's shown

	private boolean found(ItemStack s, String[] words) {
		if (words.length == 0) return true;
		StringBuilder all = new StringBuilder(BuiltInRegistries.ITEM.getKey(s.getItem()).toString());
		for (Component line : s.getTooltipLines(Item.TooltipContext.of(minecraft.level), minecraft.player, TooltipFlag.NORMAL)) all.append(' ').append(line.getString());
		String hay = all.toString().toLowerCase(Locale.ROOT);
		for (String w : words) if (!hay.contains(w)) return false;
		return true;
	}

	private void refresh() {
		seen = Net.clientBag;
		stale = false;
		String q = search.getValue().toLowerCase(Locale.ROOT).trim();
		String[] words = q.isEmpty() ? new String[0] : q.split("\\s+");
		List<Net.BagLine> out = new ArrayList<>();
		for (Net.BagLine l : seen.lines()) if ((tab == 0 || Tidy.shelf(l.stack()) == tab - 1) && found(l.stack(), words)) out.add(l);
		Comparator<Net.BagLine> byName = Comparator.comparing(l -> l.stack().getHoverName().getString());
		out.sort(switch (sort) {
			case 0 -> Comparator.comparingLong(Net.BagLine::count).reversed().thenComparing(byName);
			case 2 -> Comparator.comparingInt((Net.BagLine l) -> AshUi.rarity(l.stack(), 0)).reversed().thenComparing(byName);
			default -> byName;
		});
		shown = out;
		scroll = Math.min(scroll, maxScroll());
	}

	private int maxScroll() {
		return Math.max(0, (shown.size() + COLS - 1) / COLS - rows);
	}

	private boolean overGrid(double mx, double my) {
		return mx >= px + GRID_X && mx < px + GRID_X + COLS * CELL && my >= gridY() && my < gridY() + rows * CELL;
	}

	private Net.BagLine lineAt(double mx, double my) {
		if (!overGrid(mx, my)) return null;
		int i = (scroll + (int) (my - gridY()) / CELL) * COLS + (int) (mx - px - GRID_X) / CELL;
		return i < shown.size() ? shown.get(i) : null;
	}

	private void barTo(double my) {
		scroll = (int) Math.round((my - gridY()) / (rows * CELL) * maxScroll());
		scroll = Math.max(0, Math.min(maxScroll(), scroll));
	}

	/** A tab's left edge, the one past the last for where they end. */
	private int tabX(int i) {
		int x = px + 14;
		for (int t = 0; t < i; t++) x += font.width(Component.literal(TABS[t]).withStyle(ChatFormatting.BOLD)) + 10;
		return x;
	}

	// ---------------------------------------------------------------- input

	@Override
	protected boolean hasClickedOutside(double mx, double my, int left, int top, int button) {
		return mx < px || my < py || mx >= px + W || my >= py + panelH();
	}

	@Override
	public boolean mouseClicked(double mx, double my, int button) {
		boolean inBox = search.isMouseOver(mx, my);
		if (!inBox && search.isFocused()) {
			search.setFocused(false);
			setFocused(null);
		}
		if (inBox && button == 1) {
			search.setValue("");
			return true;
		}
		if (overGrid(mx, my)) {
			if (button > 1) return true;
			Net.BagLine l = lineAt(mx, my);
			if (!menu.getCarried().isEmpty()) send(button == 0 ? Bag.LEFT : Bag.RIGHT, ItemStack.EMPTY);
			else if (l != null) send(hasShiftDown() ? Bag.QUICK : button == 0 ? Bag.LEFT : Bag.RIGHT, l.stack());
			return true;
		}
		if (mx >= px + BAR_X && mx < px + BAR_X + BAR_W && my >= gridY() && my < gridY() + rows * CELL) {
			dragging = true;
			barTo(my);
			return true;
		}
		int ty = py + 45;
		if (my >= ty - 2 && my < ty + 12)
			for (int i = 0; i < TABS.length; i++)
				if (mx >= tabX(i) - 3 && mx < tabX(i + 1) - 7) {
					tab = i;
					scroll = 0;
					stale = true;
					return true;
				}
		return super.mouseClicked(mx, my, button);
	}

	@Override
	public boolean mouseDragged(double mx, double my, int button, double dx, double dy) {
		if (dragging) {
			barTo(my);
			return true;
		}
		return super.mouseDragged(mx, my, button, dx, dy);
	}

	@Override
	public boolean mouseReleased(double mx, double my, int button) {
		if (dragging) {
			dragging = false;
			return true;
		}
		return super.mouseReleased(mx, my, button);
	}

	@Override
	public boolean mouseScrolled(double mx, double my, double sx, double sy) {
		scroll = Math.max(0, Math.min(maxScroll(), scroll - (int) Math.signum(sy)));
		return true;
	}

	@Override
	public boolean keyPressed(int key, int scan, int mods) {
		if (key != GLFW.GLFW_KEY_ESCAPE && search.isFocused()) {
			if (key == GLFW.GLFW_KEY_ENTER || key == GLFW.GLFW_KEY_KP_ENTER) {
				search.setFocused(false);
				setFocused(null);
			} else search.keyPressed(key, scan, mods);
			return true;
		}
		if (key == GLFW.GLFW_KEY_F && Screen.hasControlDown()) {
			setFocused(search);
			return true;
		}
		if (CurioKeys.BAG.matches(key, scan)) {
			onClose();
			return true;
		}
		return super.keyPressed(key, scan, mods);
	}

	// ---------------------------------------------------------------- drawing

	/** Ten thousand doesn't fit on a tile. */
	private static String shortCount(long n) {
		if (n < 10_000) return Long.toString(n);
		String[] names = {"k", "M", "B", "T"};
		double v = n;
		int i = -1;
		while (v >= 1000 && i < names.length - 1) {
			v /= 1000;
			i++;
		}
		return (v < 100 ? String.format(Locale.ROOT, "%.1f", v) : String.format(Locale.ROOT, "%.0f", v)) + names[i];
	}

	@Override
	protected void renderBg(GuiGraphics g, float pt, int mx, int my) {
		if (stale || seen != Net.clientBag) refresh();
		AshUi.panel(g, px, py, W, panelH());
		AshUi.header(g, px, py, W, 20, "BOTTOMLESS BAG");
		AshUi.inset(g, px + 12, py + 25, W - 82, 16);
		tabs(g);
		grid(g, mx, my);
		AshUi.divider(g, px + 10, topPos - 4, W - 20);
		for (var s : menu.slots) AshUi.inset(g, leftPos + s.x - 1, topPos + s.y - 1, 18, 18);
		side(g);
	}

	private void tabs(GuiGraphics g) {
		int y = py + 45;
		for (int i = 0; i < TABS.length; i++) {
			Component t = Component.literal(TABS[i]).withStyle(ChatFormatting.BOLD);
			g.drawString(font, t, tabX(i), y, i == tab ? 0xFFF2EADC : 0xFF8A8076, true);
			if (i == tab) g.fill(tabX(i), y + 10, tabX(i) + font.width(t), y + 11, AshUi.EMBER_C);
		}
		String n = shown.size() == Net.clientBag.lines().size() ? "" : shown.size() + " found";
		g.drawString(font, n, px + W - 10 - font.width(n), y, AshUi.MUTED, false);
	}

	private void grid(GuiGraphics g, int mx, int my) {
		int x0 = px + GRID_X, y0 = gridY();
		hover = lineAt(mx, my);
		for (int r = 0; r < rows; r++)
			for (int c = 0; c < COLS; c++) {
				int x = x0 + c * CELL, y = y0 + r * CELL, i = (r + scroll) * COLS + c;
				if (i >= shown.size()) {
					g.fill(x + 1, y + 1, x + CELL - 1, y + CELL - 1, 0x46050404);
					g.renderOutline(x + 1, y + 1, CELL - 2, CELL - 2, 0x40857B70);
					continue;
				}
				Net.BagLine l = shown.get(i);
				AshUi.tile(g, x, y, CELL, AshUi.rarity(l.stack(), 0));
				if (l == hover) g.renderOutline(x, y, CELL, CELL, AshUi.EMBER_LT);
				g.renderItem(l.stack(), x + 2, y + 2);
				if (l.count() > 1) {
					String n = shortCount(l.count());
					g.pose().pushPose();
					g.pose().translate(x + CELL - 1, y + CELL - 7, 200);
					g.pose().scale(0.75f, 0.75f, 1f);
					g.drawString(font, n, -font.width(n), 0, 0xFFFFFFFF, true);
					g.pose().popPose();
				}
			}
		if (shown.isEmpty()) {
			String s = Net.clientBag.lines().isEmpty() ? "It's empty. Shift-click things in your pack to put them in." : "Nothing here by that name.";
			var lines = font.split(net.minecraft.network.chat.Component.literal(s), COLS * CELL - 16);
			int ly = y0 + (rows * CELL - lines.size() * 10) / 2;
			for (var line : lines) {
				g.drawString(font, line, x0 + (COLS * CELL - font.width(line)) / 2, ly, AshUi.MUTED, true);
				ly += 10;
			}
		}
		int bar = rows * CELL, max = maxScroll();
		AshUi.inset(g, px + BAR_X, y0, BAR_W, bar);
		int thumb = Math.max(12, bar * rows / (rows + max));
		int ty = y0 + (max == 0 ? 0 : (bar - thumb) * scroll / max);
		if (max > 0) g.fillGradient(px + BAR_X + 1, ty + 1, px + BAR_X + BAR_W - 1, ty + thumb - 1, AshUi.EMBER_LT, AshUi.EMBER_C);
	}

	/** Right of the inventory: how much is in it, and who with. */
	private void side(GuiGraphics g) {
		int x = px + Bag.SLOTS_X + 168, right = px + W - 10, y = topPos;
		long total = 0;
		for (Net.BagLine l : Net.clientBag.lines()) total += l.count();
		g.drawString(font, "ITEMS", x, y, AshUi.LABEL, false);
		String n = shortCount(total);
		g.drawString(font, n, right - font.width(n), y, AshUi.TEXT, true);
		g.drawString(font, "KINDS", x, y + 11, AshUi.LABEL, false);
		String k = String.valueOf(Net.clientBag.lines().size());
		g.drawString(font, k, right - font.width(k), y + 11, AshUi.TEXT, true);
		int with = Net.clientBag.sharing();
		String who = with > 1 ? "Shared by " + with : "Yours alone";
		g.drawString(font, who, x, y + 24, with > 1 ? AshUi.EMBER_LT : AshUi.MUTED, false);
	}

	@Override
	protected void renderLabels(GuiGraphics g, int mx, int my) {
		// the header says what this is
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		super.render(g, mx, my, pt);
		renderTooltip(g, mx, my);
	}

	@Override
	protected void renderTooltip(GuiGraphics g, int mx, int my) {
		if (hover == null || !menu.getCarried().isEmpty()) {
			super.renderTooltip(g, mx, my);
			return;
		}
		ItemStack s = hover.stack();
		List<Component> lines = new ArrayList<>(getTooltipFromItem(minecraft, s));
		lines.add(Component.literal(String.format("%,d in the bag", hover.count())).withStyle(s2 -> s2.withColor(AshUi.EMBER_LT & 0xFFFFFF)));
		if (!hover.who().isEmpty()) lines.add(Component.literal("From " + hover.who()).withStyle(ChatFormatting.GRAY));
		g.renderTooltip(font, lines, s.getTooltipImage(), s, mx, my);
	}
}
