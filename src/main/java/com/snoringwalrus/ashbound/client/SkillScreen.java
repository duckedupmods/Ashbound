package com.snoringwalrus.ashbound.client;

import java.util.ArrayList;
import java.util.List;

import com.snoringwalrus.ashbound.Books;
import com.snoringwalrus.ashbound.Classes;
import com.snoringwalrus.ashbound.Forms;
import com.snoringwalrus.ashbound.Joined;
import com.snoringwalrus.ashbound.Levels;
import com.snoringwalrus.ashbound.Net;
import com.snoringwalrus.ashbound.Skills;
import com.snoringwalrus.ashbound.Spells;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * Your skills and the keys they're on. When your level has earned a choice it's all six of your class's skills, three
 * rows of two with the row you're choosing on lit up; otherwise click a skill on the left and a key on the right to put
 * it there, right click a key to empty it. The first key is locked: it's whatever you're holding. What's still to choose
 * is under your skills, with its level.
 */
public class SkillScreen extends Screen implements MenuTabs.Panel {
	private static final int W = 420, H = 240, PAD = 12, TOP = 30, CARD_W = 150, CARD_H = 36, GAP = 3, SLOT = 26, SLOT_GAP = 8, ROW = (H - TOP - PAD) / 3, ROWS = 5, EFFECTS_W = 52;
	private int picked;

	public SkillScreen() {
		super(Component.literal("Skills"));
	}

	/** What the first key does with this in hand, or null. */
	static String heldName(ItemStack held) {
		if (Joined.stage(held) > 0) return "Joined skill";
		return held.getItem() instanceof Spells.Staff ? Skills.heldName(held) : null;
	}

	private int left() {
		return (width - W) / 2;
	}

	private int top() {
		return (height - H) / 2;
	}

	@Override
	public int panelTop() {
		return top();
	}

	private static boolean in(double mx, double my, int x, int y, int w, int h) {
		return mx >= x && mx < x + w && my >= y && my < y + h;
	}

	private static int pending() {
		return Skills.pending(Levels.clientLevel, Skills.clientPicks);
	}

	private boolean choosing() {
		return pending() >= 0 || known().isEmpty();
	}

	private List<Skills.Skill> known() {
		List<Skills.Skill> l = new ArrayList<>();
		for (Skills.Skill s : Skills.ALL) if (Skills.clientRanks.getOrDefault(s.id(), 0) > 0) l.add(s);
		return l;
	}

	private int cardY(int i) {
		return top() + TOP + i * (CARD_H + GAP);
	}

	private int infoX() {
		return left() + PAD + CARD_W + 10;
	}

	private int slotX(int i) {
		return infoX() + i * (SLOT + SLOT_GAP);
	}

	private int slotY() {
		return top() + H - PAD - SLOT - 12;
	}

	private int choiceW() {
		return (W - PAD * 2 - 10) / 2;
	}

	private int choiceX(int i) {
		return left() + PAD + i * (choiceW() + 10);
	}

	private int choiceY(int tier) {
		return top() + TOP + tier * ROW;
	}

	@Override
	protected void init() {
		addRenderableWidget(new AshUi.AshButton(left() + W - PAD - EFFECTS_W, top() + 5, EFFECTS_W, 14, Component.literal("Effects"), b -> minecraft.setScreen(new FxSetup(this)), false));
	}

	@Override
	public boolean isPauseScreen() {
		return false;
	}

	@Override
	public boolean mouseClicked(double mx, double my, int button) {
		if (choosing()) {
			int tier = pending();
			if (tier >= 0 && !Classes.client.isEmpty()) {
				List<Skills.Skill> c = Skills.choices(Classes.client, tier);
				for (int i = 0; i < c.size(); i++)
					if (in(mx, my, choiceX(i), choiceY(tier), choiceW(), ROW - GAP)) {
						PacketDistributor.sendToServer(new Net.SkillPick(c.get(i).id()));
						return true;
					}
			}
			return super.mouseClicked(mx, my, button);
		}
		List<Skills.Skill> k = known();
		for (int i = 0; i < k.size(); i++)
			if (in(mx, my, left() + PAD, cardY(i), CARD_W, CARD_H)) {
				picked = i;
				return true;
			}
		for (int i = Skills.FIRST_OWN_SLOT; i < (Forms.clientForm.isEmpty() ? Skills.SLOTS : Skills.SLOTS - 1); i++)
			if (in(mx, my, slotX(i), slotY(), SLOT, SLOT)) {
				if (button == 1) PacketDistributor.sendToServer(new Net.SkillSet(i, ""));
				else if (picked < k.size()) PacketDistributor.sendToServer(new Net.SkillSet(i, k.get(picked).id()));
				return true;
			}
		return super.mouseClicked(mx, my, button);
	}

	@Override
	public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
		g.fill(0, 0, width, height, 0xA0000000);
		AshUi.panel(g, left(), top(), W, H);
		boolean choosing = choosing();
		AshUi.header(g, left(), top(), W, 24, !choosing ? "SKILLS" : pending() >= 0 ? "CHOOSE A SKILL: LEVEL " + Skills.UNLOCK[pending()] : "YOUR FIRST SKILL COMES AT LEVEL " + Skills.SPEC_LEVEL);
		if (choosing) choose(g, mx, my);
		else skills(g, mx, my);
	}

	private void wrap(GuiGraphics g, String text, int x, int y, int w, int colour) {
		for (FormattedCharSequence l : font.split(Component.literal(text), w)) {
			g.drawString(font, l, x, y, colour, false);
			y += 10;
		}
	}

	private void choose(GuiGraphics g, int mx, int my) {
		if (Classes.client.isEmpty()) return;
		int now = pending();
		for (int tier = 0; tier < Skills.UNLOCK.length; tier++) {
			List<Skills.Skill> c = Skills.choices(Classes.client, tier);
			for (int i = 0; i < c.size(); i++) {
				Skills.Skill s = c.get(i);
				boolean mine = Skills.clientRanks.containsKey(s.id()), open = tier == now;
				int x = choiceX(i), y = choiceY(tier), w = choiceW(), h = ROW - GAP;
				AshUi.row(g, x, y, w, h, mine, open && in(mx, my, x, y, w, h));
				SkillHud.icon(g, s, x + 7, y + 7);
				g.drawString(font, s.name(), x + 29, y + 6, mine ? AshUi.EMBER_LT : open ? AshUi.TEXT : AshUi.MUTED, true);
				g.drawString(font, Skills.spec(s.spec()).name() + ", level " + Skills.unlock(s), x + 29, y + 17, AshUi.LABEL, false);
				wrap(g, s.blurb(), x + 29, y + 29, w - 37, open || mine ? AshUi.BODY : AshUi.MUTED);
			}
		}
	}

	private void skills(GuiGraphics g, int mx, int my) {
		List<Skills.Skill> k = known();
		for (int i = 0; i < k.size(); i++) {
			Skills.Skill s = k.get(i);
			int cy = cardY(i);
			AshUi.row(g, left() + PAD, cy, CARD_W, CARD_H, i == picked, in(mx, my, left() + PAD, cy, CARD_W, CARD_H));
			SkillHud.icon(g, s, left() + PAD + 7, cy + 10);
			g.drawString(font, s.name(), left() + PAD + 29, cy + 7, i == picked ? AshUi.TEXT : AshUi.BODY, true);
			g.drawString(font, "Rank " + Skills.clientRanks.get(s.id()), left() + PAD + 29, cy + 20, AshUi.MUTED, false);
		}
		int row = k.size();
		for (int tier = 0; tier < Skills.UNLOCK.length && row < ROWS && !Classes.client.isEmpty(); tier++) {
			if ((Skills.clientPicks >> tier & 1) != 0) continue;
			List<Skills.Skill> c = Skills.choices(Classes.client, tier);
			int cy = cardY(row++);
			AshUi.row(g, left() + PAD, cy, CARD_W, CARD_H, false, false);
			g.drawString(font, "Level " + Skills.UNLOCK[tier], left() + PAD + 8, cy + 7, AshUi.LABEL, false);
			g.drawString(font, font.plainSubstrByWidth(c.get(0).name() + " or " + c.get(1).name(), CARD_W - 14), left() + PAD + 8, cy + 20, AshUi.MUTED, false);
		}
		for (Skills.Skill s : Skills.ALL) {
			if (row >= ROWS || !Skills.clientRanks.containsKey(s.id()) || Skills.clientRanks.get(s.id()) > 0) continue;
			int cy = cardY(row++);
			AshUi.row(g, left() + PAD, cy, CARD_W, CARD_H, false, false);
			g.drawString(font, s.name(), left() + PAD + 8, cy + 7, AshUi.MUTED, false);
			g.drawString(font, "Given up", left() + PAD + 8, cy + 20, 0xFFE05A40, false);
		}
		int x = infoX(), w = left() + W - PAD - x, y = top() + TOP;
		if (picked < k.size()) {
			Skills.Skill s = k.get(picked);
			g.drawString(font, s.name(), x, y, AshUi.TEXT, true);
			wrap(g, s.blurb(), x, y + 14, w, AshUi.BODY);
			g.drawString(font, s.cooldown() + "s cooldown", x, y + 48, AshUi.MUTED, false);
		}
		if (!Forms.clientForm.isEmpty()) {
			Forms.Form f = Forms.byId(Forms.clientForm);
			g.drawString(font, f.tome(), x, y + 62, 0xFFE05A40, true);
			wrap(g, "When: " + f.trigger() + ". Key " + CurioKeys.FORM.getTranslatedKeyMessage().getString(), x, y + 74, w, AshUi.BODY);
		}
		g.drawString(font, "Click a skill, then a key", x, slotY() - 12, AshUi.LABEL, false);
		String held = SkillHud.held(Minecraft.getInstance());
		for (int i = 0; i < Skills.SLOTS; i++) {
			int sx = slotX(i), sy = slotY();
			AshUi.row(g, sx, sy, SLOT, SLOT, false, i >= Skills.FIRST_OWN_SLOT && in(mx, my, sx, sy, SLOT, SLOT));
			String id = Skills.clientBar[i];
			Skills.Skill s = id == null ? null : Skills.byId(id);
			boolean taken = i == Skills.SLOTS - 1 && !Forms.clientForm.isEmpty();
			if (s != null && !taken && i > 0) SkillHud.icon(g, s, sx + 5, sy + 5);
			else if (taken) g.renderItem(new ItemStack(Books.TOMES.get(Forms.ALL.indexOf(Forms.byId(Forms.clientForm))).get()), sx + 5, sy + 5);
			else {
				String t = i == 0 ? held == null ? "-" : "held" : "";
				g.drawString(font, t, sx + (SLOT - font.width(t)) / 2, sy + 9, AshUi.MUTED, true);
			}
			String key = (taken ? CurioKeys.FORM : CurioKeys.slotKey(i)).getTranslatedKeyMessage().getString();
			g.drawString(font, key, sx + (SLOT - font.width(key)) / 2, sy + SLOT + 3, AshUi.MUTED, false);
		}
	}
}
