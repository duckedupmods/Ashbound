package com.snoringwalrus.ashbound.client;

import java.util.List;

import com.snoringwalrus.ashbound.Net;
import com.snoringwalrus.ashbound.Skills;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraft.util.FormattedCharSequence;
import net.neoforged.neoforge.network.PacketDistributor;

/** A book of a skill you don't have: what it teaches, your own skills to choose from, and that the one you pick is gone for good. */
public class ReplaceScreen extends Screen {
	private static final int W = 340, PAD = 14, ROW_H = 26, ROW_GAP = 3, BTN_W = 140, BTN_H = 20, RED = 0xFFE05A40, HEAD = 96;
	private final Skills.Skill skill;
	private final int rank;
	private int picked = -1;

	public ReplaceScreen(String skill, int rank) {
		super(Component.literal("Replace a skill"));
		this.skill = Skills.byId(skill);
		this.rank = rank;
	}

	private List<Skills.Skill> mine() {
		return Skills.ALL.stream().filter(s -> Skills.clientRanks.getOrDefault(s.id(), 0) > 0).toList();
	}

	private int high() {
		return HEAD + mine().size() * (ROW_H + ROW_GAP) + PAD * 2 + BTN_H + 12;
	}

	private int left() {
		return (width - W) / 2;
	}

	private int top() {
		return (height - high()) / 2;
	}

	private int rowY(int i) {
		return top() + HEAD + i * (ROW_H + ROW_GAP);
	}

	private int buttonY() {
		return top() + high() - PAD - BTN_H;
	}

	private static boolean in(double mx, double my, int x, int y, int w, int h) {
		return mx >= x && mx < x + w && my >= y && my < y + h;
	}

	@Override
	public boolean isPauseScreen() {
		return false;
	}

	@Override
	public boolean mouseClicked(double mx, double my, int button) {
		List<Skills.Skill> m = mine();
		for (int i = 0; i < m.size(); i++)
			if (in(mx, my, left() + PAD, rowY(i), W - PAD * 2, ROW_H)) {
				picked = i;
				return true;
			}
		if (picked >= 0 && picked < m.size() && in(mx, my, left() + PAD, buttonY(), BTN_W, BTN_H)) {
			PacketDistributor.sendToServer(new Net.BookSwap(m.get(picked).id()));
			onClose();
			return true;
		}
		if (in(mx, my, left() + W - PAD - BTN_W, buttonY(), BTN_W, BTN_H)) {
			onClose();
			return true;
		}
		return super.mouseClicked(mx, my, button);
	}

	@Override
	public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
		g.fill(0, 0, width, height, 0xB0000000);
		int x = left() + PAD, w = W - PAD * 2, y = top() + 32;
		AshUi.panel(g, left(), top(), W, high());
		AshUi.header(g, left(), top(), W, 24, "REPLACE A SKILL");
		SkillHud.icon(g, skill, x, y);
		g.drawString(font, skill.name() + "  Rank " + rank, x + 22, y, AshUi.TEXT, true);
		g.drawString(font, Skills.spec(skill.spec()).name() + " path", x + 22, y + 10, AshUi.MUTED, false);
		y += 22;
		for (FormattedCharSequence l : font.split(Component.literal(skill.blurb()), w)) {
			g.drawString(font, l, x, y, AshUi.BODY, false);
			y += 10;
		}
		g.drawString(font, "Choose the skill to give up. It's gone for good.", x, top() + HEAD - 12, RED, false);
		List<Skills.Skill> m = mine();
		for (int i = 0; i < m.size(); i++) {
			Skills.Skill s = m.get(i);
			int ry = rowY(i);
			AshUi.row(g, x, ry, w, ROW_H, i == picked, in(mx, my, x, ry, w, ROW_H));
			SkillHud.icon(g, s, x + 6, ry + 5);
			g.drawString(font, s.name(), x + 28, ry + 9, i == picked ? AshUi.TEXT : AshUi.BODY, true);
			String r = "Rank " + Skills.clientRanks.get(s.id());
			g.drawString(font, r, x + w - 8 - font.width(r), ry + 9, AshUi.MUTED, false);
		}
		int by = buttonY(), yes = x, no = left() + W - PAD - BTN_W;
		AshUi.row(g, yes, by, BTN_W, BTN_H, false, picked >= 0 && in(mx, my, yes, by, BTN_W, BTN_H));
		AshUi.row(g, no, by, BTN_W, BTN_H, false, in(mx, my, no, by, BTN_W, BTN_H));
		String a = picked >= 0 && picked < m.size() ? "Give up " + m.get(picked).name() : "Pick a skill first", b = "Close the book";
		g.drawString(font, font.plainSubstrByWidth(a, BTN_W - 8), yes + (BTN_W - Math.min(BTN_W - 8, font.width(a))) / 2, by + 6, picked >= 0 ? RED : AshUi.MUTED, true);
		g.drawString(font, b, no + (BTN_W - font.width(b)) / 2, by + 6, AshUi.TEXT, true);
	}
}
