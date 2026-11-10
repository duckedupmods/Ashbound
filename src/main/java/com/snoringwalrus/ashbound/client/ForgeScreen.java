package com.snoringwalrus.ashbound.client;

import java.util.List;

import com.snoringwalrus.ashbound.Gear;
import com.snoringwalrus.ashbound.GateForge;
import com.snoringwalrus.ashbound.Net;
import com.snoringwalrus.ashbound.Smithing;

import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * The Gate Forge, in the shop's ash look: the gates down the left in rank order (those whose drops you carry lit,
 * scroll for the rest), the picked one's gear under its tabs (weapons, then each armour class), then what you carry
 * that can be upgraded or fused, and on the right the piece you picked, big, with its stats, what it takes of the
 * gate's three drops against what you carry, how many Temper Embers to burn on it and what that does for the odds, and the
 * ember FORGE button. The piece comes straight out; the Joining alone goes to the anvil (ForgeStrikeScreen).
 */
public class ForgeScreen extends Screen {
	private static final int ROW = 24, GAP = 3, DETAIL = 160, SIDE = 112;

	private final BlockPos pos;
	private int result;
	private static final String[] TABS = {"weapon", "robe", "light", "medium", "heavy", "upgrade", "fusion"};
	private static final String[] TAB_NAMES = {"Weapons", "Robe", "Light", "Medium", "Heavy", "Upgrade", "Fusion"};
	private static final int UPGRADE = 5, FUSION = 6;

	/** A line in the list: the piece, whose drops it takes, how many, and where it is (a recipe, or your pack's slot). */
	private record Entry(ItemStack stack, Gear.Dungeon gate, Gear.Cost cost, Gear.Recipe recipe, int slot) {}
	private static final int TAB_H = 16;
	private final List<Gear.Dungeon> gates = Gear.DUNGEONS.stream()
			.sorted(java.util.Comparator.comparingInt((Gear.Dungeon d) -> "FEDCBAS".indexOf(d.rank()))).toList();
	private int gate, tab, selected, scroll, gateScroll;
	private AshUi.AshButton forge, less, more;
	private int embers;
	private ItemStack hoverStack;
	private int resultY = -100;
	/** At the Cold Forge: the Joining and nothing else. At a Gate Forge everything else, and no Joining. */
	private final boolean cold;
	/**
	 * Finding gear (11/7, the user: "a tab with all the staffs, and more filters"): a search box (names, kinds, and for a staff every
	 * spell it can be made with), the weapon's kind, the rank, and every gate at once instead of the one picked.
	 */
	private EditBox search;
	private AshUi.AshButton kindBtn, rankBtn, allBtn;
	private int kindPick, rankPick;
	private boolean allGates;
	private static final List<String> KINDS = new java.util.ArrayList<>();
	/** The list for the recipe tabs, built again only when what it's built from changes. */
	private List<Entry> cached;
	private String cachedFor = "";
	/** The spell a staff will be made with (StaffSpells.Style's ordinal; -1 until a staff is picked), and where its row is. */
	private int spell = -1;
	private int spellY = -100;

	public ForgeScreen(BlockPos pos) {
		super(Component.literal("Gate Forge"));
		this.pos = pos;
		cold = com.snoringwalrus.ashbound.ColdForge.isLit(net.minecraft.client.Minecraft.getInstance().level.getBlockState(pos));
		if (cold) tab = FUSION;
	}

	private Gear.Dungeon dungeon() {
		return gates.get(gate);
	}

	private static List<String> kinds() {
		if (KINDS.isEmpty()) {
			KINDS.add("");
			Gear.WEAPON.values().stream().map(Gear.Weapon::kind).distinct().sorted().forEach(KINDS::add);
		}
		return KINDS;
	}

	static String kindName(String k) {
		return switch (k) {
			case "" -> "Any type";
			case "white" -> "Healing staff";
			case "black" -> "Black staff";
			case "summon" -> "Summon staff";
			default -> Character.toUpperCase(k.charAt(0)) + k.substring(1).replace('_', ' ');
		};
	}

	private boolean matches(Gear.Recipe r, ItemStack s, String q) {
		StringBuilder b = new StringBuilder(s.getHoverName().getString()).append(' ');
		Gear.Weapon w = Gear.WEAPON.get(r.id());
		if (w != null) {
			b.append(w.kind()).append(' ').append(kindName(w.kind())).append(' ');
			if (s.getItem() instanceof com.snoringwalrus.ashbound.Spells.Staff)
				for (var st : com.snoringwalrus.ashbound.StaffSpells.Style.choices(w)) b.append(st.title).append(' ');
		}
		for (var line : s.getTooltipLines(Item.TooltipContext.of(minecraft.level), minecraft.player, net.minecraft.world.item.TooltipFlag.NORMAL))
			b.append(line.getString()).append(' ');
		String all = b.toString().toLowerCase(java.util.Locale.ROOT);
		for (String word : q.split("\\s+")) if (!all.contains(word)) return false;
		return true;
	}

	private List<Entry> list() {
		List<Entry> out = new java.util.ArrayList<>();
		var items = minecraft.player.getInventory().items;
		if (tab == UPGRADE || tab == FUSION) {
			for (int i = 0; i < items.size(); i++) {
				ItemStack s = items.get(i);
				if (s.isEmpty()) continue;
				Gear.Dungeon d = Smithing.home(s.getItem());
				if (d == null && !(tab == FUSION && com.snoringwalrus.ashbound.Joined.is(s))) continue;
				if (tab == UPGRADE && Smithing.plus(s) < Smithing.TOP) out.add(new Entry(s, d, Smithing.upgradeCost(Smithing.plus(s)), null, i));
				if (tab == FUSION) {
					// what it takes comes from the gate of what's going in with it
					if (!com.snoringwalrus.ashbound.Joined.canLead(s)) continue;
					List<Integer> with = com.snoringwalrus.ashbound.Joined.seconds(minecraft.player, i);
					Gear.Dungeon pay = with.isEmpty() ? d : Smithing.home(items.get(with.get(Math.floorMod(result, with.size()))).getItem());
					out.add(new Entry(s, pay == null ? gates.get(0) : pay, Smithing.fuseCost(), null, i));
				}
			}
			return out;
		}
		String q = search == null ? "" : search.getValue().toLowerCase(java.util.Locale.ROOT).trim();
		String key = tab + "|" + gate + "|" + allGates + "|" + kindPick + "|" + rankPick + "|" + q;
		if (cached != null && key.equals(cachedFor)) return cached;
		for (Gear.Dungeon d : allGates ? gates : List.of(dungeon())) {
			if (rankPick > 0 && d.rank() != "FEDCBAS".charAt(rankPick - 1)) continue;
			for (Gear.Recipe r : d.recipes()) {
				if (!r.tab().equals(TABS[tab])) continue;
				if (tab == 0 && kindPick > 0) {
					Gear.Weapon w = Gear.WEAPON.get(r.id());
					if (w == null || !w.kind().equals(kinds().get(kindPick))) continue;
				}
				ItemStack s = stack(r);
				if (s.isEmpty() || !q.isEmpty() && !matches(r, s, q)) continue;
				out.add(new Entry(s, d, r.cost(), r, -1));
			}
		}
		cached = out;
		cachedFor = key;
		return out;
	}

	private void refilter() {
		selected = 0;
		scroll = 0;
		spell = -1;
	}

	/** The piece going in with this one (the one picked of those that can), or -1. */
	private int second(Entry e) {
		List<Integer> l = com.snoringwalrus.ashbound.Joined.seconds(minecraft.player, e.slot());
		return l.isEmpty() ? -1 : l.get(Math.floorMod(result, l.size()));
	}

	private boolean canDo(Entry e) {
		if (!GateForge.affords(minecraft.player, e.gate(), e.cost())) return false;
		return tab != FUSION || second(e) >= 0;
	}

	private int embersHeld() {
		return GateForge.count(minecraft.player, Smithing.TEMPER.get());
	}

	private boolean carries(Gear.Dungeon d) {
		for (String m : d.mats()) if (GateForge.count(minecraft.player, Gear.item(m)) > 0) return true;
		return false;
	}

	private int gatesShown() {
		return Math.max(1, (ph() - 32) / 22);
	}

	private ItemStack stack(Gear.Recipe r) {
		Item it = Gear.item(r.id());
		return it == null ? ItemStack.EMPTY : new ItemStack(it);
	}

	// ---------------------------------------------------------------- layout

	private int pw() {
		return Math.min(width - 16, 660);
	}

	private int ph() {
		return Math.min(height - 16, 290);
	}

	private int px() {
		return (width - pw()) / 2;
	}

	private int py() {
		return (height - ph()) / 2;
	}

	private int mainX() {
		return px() + SIDE + 6;
	}

	private int mainW() {
		return pw() - SIDE - DETAIL - 12;
	}

	private int gridX() {
		return mainX() + 10;
	}

	private int gridY() {
		return py() + 46 + TAB_H + 2;
	}

	private int gridW() {
		return mainW() - 20;
	}

	private int colW() {
		return (gridW() - 4) / 2;
	}

	private int rowsShown() {
		return Math.max(1, (ph() - 46 - TAB_H - 2 - 12) / (ROW + GAP));
	}

	private int dx() {
		return mainX() + mainW() + 6;
	}

	@Override
	protected void init() {
		forge = addRenderableWidget(new AshUi.AshButton(dx() + 10, py() + ph() - 34, DETAIL - 20, 22, Component.literal("FORGE"), b -> craft(), true));
		less = addRenderableWidget(new AshUi.AshButton(dx() + DETAIL - 56, py() + ph() - 64, 20, 14, Component.literal("-"), b -> embers = Math.max(0, embers - 1), false));
		more = addRenderableWidget(new AshUi.AshButton(dx() + DETAIL - 32, py() + ph() - 64, 20, 14, Component.literal("+"), b -> embers = Math.min(Math.min(Smithing.MOST_EMBERS, embersHeld()), embers + 1), false));
		// the finding row, over the tabs: search | kind | rank | all gates (shift-click a button to go back one)
		int fy = py() + 25, fw = gridW(), sw = Math.round(fw * 0.38f), kw = Math.round(fw * 0.26f), rw = Math.round(fw * 0.14f), aw = fw - sw - kw - rw - 9;
		String had = search == null ? "" : search.getValue();
		search = new EditBox(font, gridX() + 4, fy + 3, sw - 6, 10, Component.literal("Search"));
		search.setBordered(false);
		search.setMaxLength(40);
		search.setTextColor(0xFFFFFFFF);
		search.setHint(Component.literal("Search: mend, bow, frost...").withStyle(s -> s.withColor(AshUi.DIM & 0xFFFFFF)));
		search.setValue(had);
		search.setResponder(s -> refilter());
		search.visible = !cold;
		addRenderableWidget(search);
		int x = gridX() + sw + 3;
		kindBtn = addRenderableWidget(new AshUi.AshButton(x, fy, kw, 14, Component.literal(kindName(kinds().get(kindPick))), b -> {
			kindPick = (kindPick + (hasShiftDown() ? kinds().size() - 1 : 1)) % kinds().size();
			b.setMessage(Component.literal(kindName(kinds().get(kindPick))));
			refilter();
		}, false));
		x += kw + 3;
		rankBtn = addRenderableWidget(new AshUi.AshButton(x, fy, rw, 14, Component.literal(rankName()), b -> {
			rankPick = (rankPick + (hasShiftDown() ? 7 : 1)) % 8;
			b.setMessage(Component.literal(rankName()));
			refilter();
		}, false));
		x += rw + 3;
		allBtn = addRenderableWidget(new AshUi.AshButton(x, fy, aw, 14, Component.literal(allGates ? "All gates" : "This gate"), b -> {
			allGates = !allGates;
			b.setMessage(Component.literal(allGates ? "All gates" : "This gate"));
			refilter();
		}, false));
	}

	private String rankName() {
		return rankPick == 0 ? "Any rank" : "Rank " + "FEDCBAS".charAt(rankPick - 1);
	}

	private void craft() {
		if (selected < 0 || selected >= list().size()) return;
		Entry e = list().get(selected);
		Net.Job job;
		if (tab == UPGRADE) job = new Net.Job(Smithing.UPGRADE, -1, -1, e.slot());
		else if (tab == FUSION) {
			job = new Net.Job(Smithing.FUSE, second(e), 0, e.slot());
		} else job = new Net.Job(Smithing.MAKE, Gear.DUNGEONS.indexOf(e.gate()), e.gate().recipes().indexOf(e.recipe()),
				e.stack().getItem() instanceof com.snoringwalrus.ashbound.Spells.Staff ? spell : -1);
		PacketDistributor.sendToServer(new Net.ForgeCraft(pos, job, embers));
		if (tab == FUSION) onClose();   // that one's done by hand, at the anvil
		embers = 0;
	}

	@Override
	public boolean isPauseScreen() {
		return false;
	}

	@Override
	public void tick() {
		if (minecraft.player == null || minecraft.player.distanceToSqr(pos.getCenter()) > 64) onClose();
	}

	private int itemAt(double mx, double my) {
		if (mx < gridX() || mx >= gridX() + gridW() || my < gridY()) return -1;
		int r = (int) ((my - gridY()) / (ROW + GAP));
		if (r >= rowsShown() || (my - gridY()) - r * (ROW + GAP) >= ROW) return -1;
		int c = mx < gridX() + colW() ? 0 : mx >= gridX() + colW() + 4 ? 1 : -1;
		if (c < 0) return -1;
		int i = (r + scroll) * 2 + c;
		return i < list().size() ? i : -1;
	}

	private int gateAt(double mx, double my) {
		int x = px() + 6, y = py() + 26;
		if (mx < x || mx >= x + SIDE - 12 || my < y) return -1;
		int i = (int) ((my - y) / 22);
		return i < gatesShown() && i + gateScroll < gates.size() && (my - y) - i * 22 < 20 ? i + gateScroll : -1;
	}

	private int tabAt(double mx, double my) {
		int y = py() + 42;
		if (cold || mx < gridX() || mx >= gridX() + gridW() || my < y || my >= y + TAB_H) return -1;
		return (int) ((mx - gridX()) * FUSION / gridW());
	}

	@Override
	public boolean mouseClicked(double mx, double my, int button) {
		if (super.mouseClicked(mx, my, button)) return true;
		int g = gateAt(mx, my);
		if (g >= 0) {
			gate = g;
			if (allGates) {
				allGates = false;
				allBtn.setMessage(Component.literal("This gate"));
			}
			refilter();
			return true;
		}
		int t = tabAt(mx, my);
		if (t >= 0) {
			tab = t;
			refilter();
			return true;
		}
		int i = itemAt(mx, my);
		if (i >= 0) {
			if (i != selected) spell = -1;
			selected = i;
			result = 0;
			return true;
		}
		if (spellY > 0 && mx >= dx() + 10 && mx < dx() + DETAIL - 10 && my >= spellY && my < spellY + 14 && selected >= 0 && selected < list().size()
				&& list().get(selected).stack().getItem() instanceof com.snoringwalrus.ashbound.Spells.Staff st) {
			var ch = com.snoringwalrus.ashbound.StaffSpells.Style.choices(st.weapon());
			int at = Math.max(0, ch.indexOf(com.snoringwalrus.ashbound.StaffSpells.Style.values()[Math.max(0, spell)]));
			spell = ch.get(Math.floorMod(at + (button == 1 ? -1 : 1), ch.size())).ordinal();
			return true;
		}
		if (tab == FUSION && mx >= dx() + 10 && mx < dx() + DETAIL - 10 && my >= resultY && my < resultY + 18) {
			result++;
			return true;
		}
		return false;
	}

	@Override
	public boolean mouseScrolled(double mx, double my, double sx, double sy) {
		if (mx < px() + SIDE) {
			gateScroll = Math.max(0, Math.min(gates.size() - gatesShown(), gateScroll - (int) Math.signum(sy)));
			return true;
		}
		int max = Math.max(0, (list().size() + 1) / 2 - rowsShown());
		scroll = Math.max(0, Math.min(max, scroll - (int) Math.signum(sy)));
		return true;
	}

	// ---------------------------------------------------------------- drawing

	@Override
	public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
		g.fill(0, 0, width, height, 0x70000000);
		hoverStack = null;
		gates(g, mx, my);
		int x = mainX(), y = py(), w = mainW(), h = ph();
		Gear.Dungeon d = dungeon();
		AshUi.panel(g, x, y, w, h);
		boolean finding = tab < UPGRADE;
		AshUi.header(g, x, y, w, 20, tab == UPGRADE ? "UPGRADE" : tab == FUSION ? "THE COLD FORGE" : allGates ? "ALL GATES" : d.title().toUpperCase() + "  -  RANK " + d.rank());
		int ty = y + 27;
		search.visible = finding;
		kindBtn.visible = finding && tab == 0;
		rankBtn.visible = allBtn.visible = finding;
		if (finding) {
			int sw = Math.round(gridW() * 0.38f);
			g.fill(gridX(), y + 25, gridX() + sw, y + 39, 0xFF0E0B09);
			g.renderOutline(gridX(), y + 25, sw, 14, search.isFocused() ? AshUi.EMBER_LT : 0xFF3D3833);
		} else g.drawString(font, Component.literal(tab == UPGRADE ? "RAISE WHAT YOU CARRY" : "TWO BECOME ONE").withStyle(ChatFormatting.BOLD), gridX(), ty, 0xFFF2EADC, true);
		int hovTab = tabAt(mx, my), tw0 = gridW() / FUSION;
		for (int t = 0; t < (cold ? 0 : FUSION); t++) {
			int tx = gridX() + t * tw0;
			AshUi.row(g, tx, py() + 42, tw0 - 2, TAB_H, t == tab, t == hovTab);
			g.drawString(font, TAB_NAMES[t], tx + (tw0 - 2 - font.width(TAB_NAMES[t])) / 2, py() + 46, t == tab ? AshUi.TEXT : AshUi.MUTED, false);
		}
		List<Entry> l = list();
		int hovered = itemAt(mx, my);
		for (int r = 0; r < rowsShown(); r++) {
			for (int c = 0; c < 2; c++) {
				int i = (r + scroll) * 2 + c;
				if (i >= l.size()) break;
				Entry rc = l.get(i);
				ItemStack s = rc.stack();
				int rx = gridX() + c * (colW() + 4), ry = gridY() + r * (ROW + GAP);
				AshUi.row(g, rx, ry, colW(), ROW, i == selected, i == hovered);
				boolean can = canDo(rc);
				int rar = can ? 2 : 0;
				AshUi.tile(g, rx + 2, ry + 2, 20, rar);
				g.renderItem(s, rx + 4, ry + 4);
				if (i == hovered && mx < rx + 22) hoverStack = s;
				int tw = colW() - 30;
				g.drawString(font, font.plainSubstrByWidth(s.getHoverName().getString(), tw), rx + 26, ry + 4, can ? AshUi.RARITY_TEXT[2] : AshUi.BODY, true);
				g.drawString(font, font.plainSubstrByWidth(costLine(rc.cost()), tw), rx + 26, ry + 14, can ? 0xFFFFD2A8 : AshUi.DIM, false);
			}
		}
		if (l.isEmpty() && finding) {
			// the towers make armour only: their weapons are the world's, in its chests and the tower hoards
			String none = tab == 0 && !allGates && dungeon().weapons().isEmpty() ? "A tower forges armour only: its weapons are found" : "Nothing here by those filters";
			g.drawString(font, none, gridX() + (gridW() - font.width(none)) / 2, gridY() + 40, AshUi.MUTED, false);
		}
		if (l.isEmpty() && tab >= UPGRADE) {
			String none = tab == UPGRADE ? "Carry gate gear to raise it" : "Bring it two boss weapons of a kind and rank";
			g.drawString(font, none, gridX() + (gridW() - font.width(none)) / 2, gridY() + 40, AshUi.MUTED, false);
		}
		if ((l.size() + 1) / 2 > rowsShown()) {
			String more = "scroll for more";
			g.drawString(font, more, x + w - 10 - font.width(more), y + h - 10, AshUi.DIM, false);
		}
		detail(g, mx, my);
	}

	private static String costLine(Gear.Cost c) {
		StringBuilder b = new StringBuilder().append(c.common());
		if (c.elite() > 0) b.append(" + ").append(c.elite());
		if (c.trophy() > 0) b.append(" + ").append(c.trophy());
		return b.toString();
	}

	private void gates(GuiGraphics g, int mx, int my) {
		int x = px(), y = py(), h = ph();
		AshUi.panel(g, x, y, SIDE, h);
		AshUi.header(g, x, y, SIDE, 20, "GATES");
		int hov = gateAt(mx, my);
		for (int i = gateScroll; i < Math.min(gates.size(), gateScroll + gatesShown()); i++) {
			Gear.Dungeon d = gates.get(i);
			int ry = y + 26 + (i - gateScroll) * 22;
			AshUi.row(g, x + 6, ry, SIDE - 12, 20, i == gate && !allGates, i == hov);
			String rank = String.valueOf(d.rank());
			g.drawString(font, Component.literal(rank).withStyle(ChatFormatting.BOLD), x + 11, ry + 6, 0xFF000000 | d.colour(), true);
			String name = d.title().replaceFirst("^The ", "");
			g.drawString(font, font.plainSubstrByWidth(name, SIDE - 36), x + 24, ry + 6, i == gate ? AshUi.TEXT : carries(d) ? AshUi.BODY : AshUi.DIM, false);
		}
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		super.render(g, mx, my, pt);
		if (hoverStack != null && !hoverStack.isEmpty()) g.renderTooltip(font, hoverStack, mx, my);
	}

	private void detail(GuiGraphics g, int mx, int my) {
		int x = dx(), y = py(), w = DETAIL, h = ph();
		AshUi.panel(g, x, y, w, h);
		List<Entry> l = list();
		forge.visible = selected >= 0 && selected < l.size();
		less.visible = more.visible = forge.visible && tab != FUSION;
		if (!forge.visible) return;
		Entry rc = l.get(selected);
		Gear.Dungeon d = rc.gate();
		ItemStack s = rc.stack();
		List<com.snoringwalrus.ashbound.StaffSpells.Style> spells = rc.recipe() != null && s.getItem() instanceof com.snoringwalrus.ashbound.Spells.Staff st
				? com.snoringwalrus.ashbound.StaffSpells.Style.choices(st.weapon()) : List.of();
		spellY = -100;
		if (spells.size() > 1) {
			if (spell < 0 || !spells.contains(com.snoringwalrus.ashbound.StaffSpells.Style.values()[spell]))
				spell = com.snoringwalrus.ashbound.StaffSpells.Style.of(s).ordinal();
			s = s.copy();
			com.snoringwalrus.ashbound.StaffSpells.Style.set(s, com.snoringwalrus.ashbound.StaffSpells.Style.values()[spell]);
		}
		g.fillGradient(x + 4, y + 4, x + w - 4, y + 54, 0x50000000 | (d.colour() & 0xFFFFFF), d.colour() & 0xFFFFFF);
		AshUi.divider(g, x + 4, y + 54, w - 8);
		AshUi.tile(g, x + w - 46, y + 12, 36, 2);
		g.pose().pushPose();
		g.pose().translate(x + w - 44, y + 14, 0);
		g.pose().scale(2f, 2f, 1f);
		g.renderItem(s, 0, 0);
		g.pose().popPose();
		if (mx >= x + w - 46 && mx < x + w - 10 && my >= y + 12 && my < y + 48) hoverStack = s;
		int ty = y + 12;
		for (FormattedCharSequence line : font.split(s.getHoverName().copy().withStyle(ChatFormatting.BOLD), w - 64)) {
			g.drawString(font, line, x + 10, ty, AshUi.RARITY_TEXT[2], true);
			ty += 10;
		}
		g.drawString(font, "Rank " + d.rank() + (Smithing.plus(s) > 0 ? "  +" + Smithing.plus(s) : ""), x + 10, ty + 2, 0xFFC8B98F, false);
		int sy = y + 60;
		if (tab == UPGRADE) {
			int n = Smithing.plus(s);
			g.drawString(font, "+" + n + " to +" + (n + 1) + ": 4% stronger", x + 10, sy, AshUi.TEXT, false);
			sy += 10;
			g.drawString(font, font.plainSubstrByWidth("If it doesn't take, the drops go,", w - 20), x + 10, sy, AshUi.MUTED, false);
			sy += 10;
			g.drawString(font, "never the piece.", x + 10, sy, AshUi.MUTED, false);
			sy += 10;
		} else if (tab == FUSION) {
			int b = second(rc);
			var com_items = minecraft.player.getInventory().items;
			int count = com.snoringwalrus.ashbound.Joined.seconds(minecraft.player, rc.slot()).size();
			g.drawString(font, count > 1 ? "WITH (click to change)" : "WITH", x + 10, sy, AshUi.LABEL, false);
			sy += 11;
			resultY = sy;
			if (b >= 0) {
				ItemStack sec = com_items.get(b);
				g.renderItem(sec, x + 10, sy);
				if (mx >= x + 10 && mx < x + 26 && my >= sy && my < sy + 16) hoverStack = sec;
				g.drawString(font, font.plainSubstrByWidth(sec.getHoverName().getString(), w - 40), x + 30, sy + 4, AshUi.BODY, true);
			} else {
				g.drawString(font, font.plainSubstrByWidth("Another boss " + Smithing.boss(s).kind() + " of its rank", w - 20), x + 10, sy + 4, AshUi.BAD, false);
			}
			sy += 19;
			if (b >= 0) {
				ItemStack ts = com.snoringwalrus.ashbound.Joined.result(s, com_items.get(b));
				int st = com.snoringwalrus.ashbound.Joined.stage(ts);
				g.drawString(font, "BECOMES", x + 10, sy, AshUi.LABEL, false);
				sy += 11;
				g.renderItem(ts, x + 10, sy);
				if (mx >= x + 10 && mx < x + 26 && my >= sy && my < sy + 16) hoverStack = ts;
				g.drawString(font, font.plainSubstrByWidth(ts.getHoverName().getString() + ", Rank " + com.snoringwalrus.ashbound.Joined.rank(st), w - 40), x + 30, sy + 4, AshUi.RARITY_TEXT[2], true);
				sy += 19;
			}
		} else {
			if (spells.size() > 1) {
				// the spell it'll be made with: click for the next, right-click for the one before
				g.drawString(font, "SPELL  (click to change)", x + 10, sy, AshUi.LABEL, false);
				sy += 11;
				spellY = sy;
				boolean hot = mx >= x + 10 && mx < x + w - 10 && my >= sy && my < sy + 14;
				AshUi.row(g, x + 10, sy, w - 20, 14, true, hot);
				String name = "<  " + com.snoringwalrus.ashbound.StaffSpells.Style.values()[spell].title + "  >";
				g.drawString(font, name, x + (w - font.width(name)) / 2, sy + 3, AshUi.TEXT, true);
				sy += 18;
			}
			// what it does, as its own tooltip says it, past its name
			var tip = s.getTooltipLines(net.minecraft.world.item.Item.TooltipContext.of(minecraft.level), minecraft.player, net.minecraft.world.item.TooltipFlag.NORMAL);
			for (int k = 1, n = 0; k < tip.size() && n < 6; k++) {
				String line = tip.get(k).getString();
				if (line.isBlank()) continue;
				g.drawString(font, font.plainSubstrByWidth(line, w - 20), x + 10, sy, tip.get(k).getStyle().getColor() != null ? tip.get(k).getStyle().getColor().getValue() | 0xFF000000 : AshUi.BODY, false);
				sy += 10;
				n++;
			}
		}
		sy += 4;
		g.drawString(font, "IT TAKES", x + 10, sy, AshUi.LABEL, false);
		int ly = sy + 12;
		int[] need = {rc.cost().common(), rc.cost().elite(), rc.cost().trophy()};
		for (int k = 0; k < 3; k++) {
			if (need[k] == 0) continue;
			Item it = Gear.item(d.mats()[k]);
			if (it == null) continue;
			ItemStack ms = new ItemStack(it);
			int have = GateForge.countKin(minecraft.player, d, k);   // any dungeon of this rank's will do
			g.renderItem(ms, x + 10, ly);
			if (mx >= x + 10 && mx < x + 26 && my >= ly && my < ly + 16) hoverStack = ms;
			g.drawString(font, font.plainSubstrByWidth(ms.getHoverName().getString(), w - 74), x + 30, ly + 4, AshUi.BODY, false);
			String n = have + "/" + need[k];
			g.drawString(font, n, x + w - 10 - font.width(n), ly + 4, have >= need[k] ? 0xFF9BE07A : AshUi.BAD, true);
			ly += 20;
		}
		boolean can = canDo(rc);
		forge.active = can;
		forge.setMessage(Component.literal(tab == UPGRADE ? "UPGRADE" : tab == FUSION ? "FUSE" : "FORGE"));
		if (tab == FUSION) {
			String note = minecraft.player.isCreative() ? "Creative: free" : can ? "You have what it takes" : "Clear the gate for more";
			g.drawString(font, note, x + (w - font.width(note)) / 2, y + h - 48, can ? AshUi.MUTED : AshUi.BAD, false);
			return;
		}
		embers = Math.min(embers, embersHeld());
		less.active = embers > 0;
		more.active = embers < Math.min(Smithing.MOST_EMBERS, embersHeld());
		g.renderItem(new ItemStack(Smithing.TEMPER.get()), x + 10, y + h - 66);
		g.drawString(font, embers + " of " + embersHeld(), x + 30, y + h - 61, AshUi.BODY, false);
		String chance;
		if (tab == UPGRADE) chance = "Chance it takes: " + Math.round(Smithing.upgradeChance(Smithing.plus(s), embers) * 100) + "%";
		else {
			float[] odds = Smithing.odds(embers);
			chance = "Masterwork " + Math.round(odds[2] * 100) + "%  Perfect " + Math.round(odds[3] * 100) + "%";
		}
		g.drawString(font, chance, x + (w - font.width(chance)) / 2, y + h - 46, can ? AshUi.EMBER_LT : AshUi.BAD, false);
	}
}
