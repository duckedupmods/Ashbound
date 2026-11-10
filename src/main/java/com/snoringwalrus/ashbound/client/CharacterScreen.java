package com.snoringwalrus.ashbound.client;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

import com.snoringwalrus.ashbound.BeltPouch;
import com.snoringwalrus.ashbound.Classes;
import com.snoringwalrus.ashbound.Coins;
import com.snoringwalrus.ashbound.Guild;
import com.snoringwalrus.ashbound.Levels;
import com.snoringwalrus.ashbound.Net;
import com.snoringwalrus.ashbound.Spells;
import com.snoringwalrus.ashbound.Tidy;
import com.snoringwalrus.ashbound.mixin.SlotAccessor;

import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.EffectRenderingInventoryScreen;
import net.minecraft.client.gui.screens.inventory.InventoryScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.inventory.Slot;
import net.neoforged.neoforge.network.PacketDistributor;
import top.theillusivec4.curios.common.inventory.CurioSlot;
import top.theillusivec4.curios.common.inventory.container.CuriosContainer;
import yesman.epicfight.client.world.capabilites.entitypatch.player.LocalPlayerPatch;
import yesman.epicfight.world.capabilities.EpicFightCapabilities;

/**
 * The inventory, in place of both the vanilla one and Curios' panel (MenuTabs swaps them): what you wear beside your character, your
 * relics and pet, what you're worth, then your pack, and the belt pouch hanging off its left side, where a right-click uses what's in
 * it. It stands on Curios' menu, which holds all of those; the slots are only moved.
 */
public class CharacterScreen extends EffectRenderingInventoryScreen<CuriosContainer> implements MenuTabs.Panel {
	/** Read by mixin/DollFadeMixin. */
	public static boolean drawingDoll;

	private static final int W = 284, H = 212, CELL = 18, LEFT = 12, TOP = 30, DOLL_X = 32, DOLL_W = 70, DOLL_H = 90, DOLL_SCALE = 34;
	private static final int CURIO_X = 105, CURIO_ROWS = 5, STATS_X = 164, STATS_W = 108, PACK_Y = 126, HOTBAR_Y = 184, CRAFT_X = 202, CRAFT_Y = 138, RESULT_X = 254;
	/** Room for every slot a player has, Cataclysm's too (SelfTest counts them): a curio in a slot past these is worn with nothing to show for it. */
	public static final int CURIO_CELLS = 15;
	/** Our own slots lead; other mods' come after. */
	private static final List<String> OURS = List.of("relic", "pet", "necklace", "ring", "charm");
	/** the menu's slots, in order, the same as the vanilla inventory's; Curios' own come after the off hand */
	private static final int RESULT = 0, CRAFT = 1, ARMOUR = 5, PACK = 9, HOTBAR = 36, OFF_HAND = 45;
	private static final List<String> ARMOUR_NAMES = List.of("Helmet", "Chest", "Legs", "Boots");
	/** the pouch's panel left of the main one, and where a hidden slot goes */
	private static final int POUCH_W = 38, POUCH_H = 92, POUCH_X = -POUCH_W - 2, POUCH_Y = 30, POUCH_SLOT_Y = 16, HIDDEN = -1000;

	public CharacterScreen(CuriosContainer menu, Inventory inv, Component title) {
		super(menu, inv, title);
		imageWidth = W;
		imageHeight = H;
	}

	@Override
	protected void init() {
		super.init();
		addRenderableWidget(new AshUi.AshButton(leftPos + CRAFT_X, topPos + HOTBAR_Y - 1, W - LEFT - CRAFT_X, 18, Component.literal("Sort pack"),
				b -> PacketDistributor.sendToServer(new Net.InvTidy(Tidy.SORT)), false));
	}

	@Override
	public int panelTop() {
		return topPos;
	}

	@Override
	public int panelMiddle() {
		return leftPos + imageWidth / 2;
	}

	private void put(int i, int x, int y) {
		SlotAccessor s = (SlotAccessor) menu.slots.get(i);
		s.setAshX(x);
		s.setAshY(y);
	}

	/** Each frame: Curios rebuilds its slots whenever yours change. */
	private void place() {
		put(RESULT, RESULT_X, CRAFT_Y + CELL / 2);
		for (int i = 0; i < 4; i++) {
			put(CRAFT + i, CRAFT_X + i % 2 * CELL, CRAFT_Y + i / 2 * CELL);
			put(ARMOUR + i, LEFT, TOP + i * CELL);
		}
		put(OFF_HAND, LEFT, TOP + 4 * CELL);
		for (int i = 0; i < 27; i++) put(PACK + i, LEFT + i % 9 * CELL, PACK_Y + i / 9 * CELL);
		for (int i = 0; i < 9; i++) put(HOTBAR + i, LEFT + i * CELL, HOTBAR_Y);
		int pouch = 0;
		List<CurioSlot> worn = new ArrayList<>();
		for (int i = OFF_HAND + 1; i < menu.slots.size(); i++) {
			if (menu.slots.get(i) instanceof CurioSlot c && !c.isCosmetic() && inPouch(c)) {
				put(i, POUCH_X + (POUCH_W - CELL) / 2 + 1, POUCH_Y + POUCH_SLOT_Y + pouch * CELL);
				pouch++;
				continue;
			}
			put(i, HIDDEN, HIDDEN);
			if (menu.slots.get(i) instanceof CurioSlot c && !c.isCosmetic()) worn.add(c);
		}
		worn.sort(Comparator.comparingInt(CharacterScreen::rank));
		for (int n = 0; n < Math.min(worn.size(), CURIO_CELLS); n++) put(menu.slots.indexOf(worn.get(n)), CURIO_X + n / CURIO_ROWS * CELL, TOP + n % CURIO_ROWS * CELL);
	}

	private static int rank(CurioSlot c) {
		int r = OURS.indexOf(c.getIdentifier());
		return r < 0 ? OURS.size() : r;
	}

	private static boolean inPouch(CurioSlot c) {
		return c.getIdentifier().equals(BeltPouch.SLOT);
	}

	private boolean overPouch(double mx, double my) {
		return mx >= leftPos + POUCH_X && mx < leftPos + POUCH_X + POUCH_W && my >= topPos + POUCH_Y && my < topPos + POUCH_Y + POUCH_H;
	}

	@Override
	protected boolean hasClickedOutside(double mx, double my, int left, int top, int button) {
		return !overPouch(mx, my) && super.hasClickedOutside(mx, my, left, top, button);
	}

	@Override
	public boolean mouseClicked(double mx, double my, int button) {
		if (button == 1 && menu.getCarried().isEmpty() && hoveredSlot instanceof CurioSlot c && inPouch(c)) {
			if (c.getItem().is(Guild.CARD_ITEM.get())) {
				Net.onCard.run();
				return true;
			}
			if (BeltPouch.opens(c.getItem())) {
				PacketDistributor.sendToServer(new Net.PouchUse(c.getSlotIndex()));
				return true;
			}
		}
		return super.mouseClicked(mx, my, button);
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		place();
		super.render(g, mx, my, pt);
		String empty = emptyName();
		if (empty != null) g.renderTooltip(font, Component.literal(empty), mx, my);
		else if (mx >= armourBox[0] && mx < armourBox[0] + armourBox[2] && my >= armourBox[1] && my < armourBox[1] + armourBox[3])
			g.renderTooltip(font, Component.literal("Hits on you do " + armourCut + "% less damage"), mx, my);
		else renderTooltip(g, mx, my);
	}

	/** What the empty slot under the mouse is for. */
	private String emptyName() {
		if (hoveredSlot == null || hoveredSlot.hasItem() || !menu.getCarried().isEmpty()) return null;
		if (hoveredSlot instanceof CurioSlot c) return c.getSlotName();
		int i = hoveredSlot.index;
		return i == OFF_HAND ? "Off hand" : i >= ARMOUR && i < PACK ? ARMOUR_NAMES.get(i - ARMOUR) : null;
	}

	@Override
	protected void renderBg(GuiGraphics g, float pt, int mx, int my) {
		int x = leftPos, y = topPos;
		AshUi.panel(g, x, y, W, H);
		AshUi.header(g, x, y, W, 24, "CHARACTER");
		AshUi.panel(g, x + POUCH_X, y + POUCH_Y, POUCH_W, POUCH_H);
		g.drawCenteredString(font, "Pouch", x + POUCH_X + POUCH_W / 2, y + POUCH_Y + 5, AshUi.MUTED);
		for (Slot s : menu.slots) if (s.x != HIDDEN) AshUi.tile(g, x + s.x - 1, y + s.y - 1, CELL, AshUi.rarity(s.getItem(), 0));
		AshUi.inset(g, x + DOLL_X, y + TOP - 1, DOLL_W, DOLL_H);
		drawingDoll = true;
		InventoryScreen.renderEntityInInventoryFollowsMouse(g, x + DOLL_X + 2, y + TOP + 1, x + DOLL_X + DOLL_W - 2, y + TOP + DOLL_H - 3, DOLL_SCALE, 0.0625f, mx, my, minecraft.player);
		drawingDoll = false;
		stats(g, x + STATS_X, y + TOP);
		g.drawString(font, "Crafting", x + CRAFT_X, y + PACK_Y, AshUi.MUTED, false);
		int ay = y + CRAFT_Y + CELL - 1, ax = x + RESULT_X - 13;
		g.fill(ax, ay, ax + 6, ay + 2, AshUi.DIM);
		for (int i = 0; i < 3; i++) g.fill(ax + 6 + i, ay - 2 + i, ax + 7 + i, ay + 4 - i, AshUi.DIM);
	}

	/** where Armour is drawn, for its tooltip, and what it takes off a hit */
	private int[] armourBox = new int[4];
	private int armourCut;

	private void stats(GuiGraphics g, int x, int y) {
		var p = minecraft.player;
		Classes.Cls c = Classes.byId(Classes.client);
		g.drawString(font, Component.literal(p.getGameProfile().getName()).withStyle(ChatFormatting.BOLD), x, y, AshUi.TEXT, true);
		g.drawString(font, "Level " + Levels.clientLevel + (c == null ? "" : "  " + c.name()), x, y + 11, AshUi.EMBER_LT, false);
		int by = y + 24;
		LocalPlayerPatch patch = EpicFightCapabilities.getEntityPatch(p, LocalPlayerPatch.class);
		by = bar(g, x, by, "Health", p.getHealth(), p.getMaxHealth(), 0xFFB84A3C);
		by = bar(g, x, by, "Mana", Spells.clientMana, Spells.clientMax, 0xFF5A8CCC);
		if (patch != null) by = bar(g, x, by, "Stamina", patch.getStamina(), patch.getMaxStamina(), 0xFF8AA648);
		by = y + 70;
		String armour = String.valueOf(p.getArmorValue()), attack = String.format("%.1f", p.getAttributeValue(Attributes.ATTACK_DAMAGE));
		g.drawString(font, "Armour", x, by, AshUi.MUTED, false);
		g.drawString(font, armour, x + font.width("Armour") + 4, by, AshUi.TEXT, false);
		// what it takes off a hit is on hover: written beside it, it ran into Attack
		armourBox = new int[] {x, by - 1, font.width("Armour") + 4 + font.width(armour), 10};
		armourCut = Math.round(100 * (1 - com.snoringwalrus.ashbound.Balance.kept(p)));
		g.drawString(font, attack, x + STATS_W - font.width(attack), by, AshUi.TEXT, false);
		g.drawString(font, "Attack", x + STATS_W - font.width(attack) - font.width("Attack") - 4, by, AshUi.MUTED, false);
		by += 12;
		String coins = String.format("%,d", Coins.client);
		AshUi.flame(g, x, by - 1);
		g.drawString(font, String.format("%,d", Levels.clientAsh), x + 13, by, AshUi.TEXT, false);
		AshUi.coin(g, x + STATS_W - font.width(coins) - 13, by - 1);
		g.drawString(font, coins, x + STATS_W - font.width(coins), by, AshUi.TEXT, false);
	}

	private int bar(GuiGraphics g, int x, int y, String name, float now, float max, int colour) {
		String of = Math.round(now) + " / " + Math.round(max);
		g.drawString(font, name, x, y, AshUi.MUTED, false);
		g.drawString(font, of, x + STATS_W - font.width(of), y, AshUi.BODY, false);
		g.fill(x, y + 9, x + STATS_W, y + 12, 0xFF1A1613);
		g.fill(x, y + 9, x + Math.round(STATS_W * Mth.clamp(now / Math.max(1, max), 0, 1)), y + 12, colour);
		return y + 15;
	}

	@Override
	protected void renderLabels(GuiGraphics g, int mx, int my) {}
}
