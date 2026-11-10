package com.snoringwalrus.ashbound.client;

import java.util.ArrayList;
import java.util.List;

import com.mojang.blaze3d.platform.InputConstants;
import com.snoringwalrus.ashbound.Net;

import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.FormattedText;
import net.minecraft.network.chat.Style;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.Mth;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * Talking to a townsperson, in the ash look: the world stays in view, an ash panel along the bottom with their name
 * on a plate over its edge, what they say typed out a few letters a tick (click or Space shows it all), your answers
 * as rows down its right side (click, or keys 1-9). Closing it (Esc) ends it. The panel grows to fit what's said and the words sit
 * in the middle of it; something too long for the window scrolls, following the typing.
 */
public class TalkScreen extends Screen {
	private static final int OPT = 18, OPT_GAP = 3, LINE = 11, PARAGRAPH = 4, MAX_W = 600, TEXT_TOP = 12, TEXT_FOOT = 24, ROOM_ABOVE = 70;

	/** A wrapped line, and any extra gap under it. */
	private record Line(String text, int after) {}

	private int entity;
	private String name, title, text;
	private List<String> options;
	private List<Line> lines = List.of();
	private float shown;
	private int ticks, textH, scroll;
	private boolean sentClose;

	public TalkScreen(Net.NpcTalk msg) {
		super(Component.literal(msg.name()));
		set(msg);
	}

	/** A new node of the same conversation. */
	public void set(Net.NpcTalk msg) {
		entity = msg.entity();
		name = msg.name();
		title = msg.title();
		text = msg.text();
		options = msg.options();
		shown = 0;
		ticks = 0;
		scroll = 0;
		wrap();
	}

	@Override
	protected void init() {
		wrap();
	}

	/** All of it, up front, so nothing moves about as it types. */
	private void wrap() {
		if (font == null) return;
		List<Line> out = new ArrayList<>();
		int tall = 0;
		for (String para : text.split("\n", -1)) {
			List<FormattedText> parts = font.getSplitter().splitLines(para, textW(), Style.EMPTY);
			for (int i = 0; i < parts.size(); i++) out.add(new Line(parts.get(i).getString().stripTrailing(), i == parts.size() - 1 ? PARAGRAPH : 0));
			if (parts.isEmpty()) out.add(new Line("", PARAGRAPH));
		}
		for (Line l : out) tall += LINE + l.after;
		lines = out;
		textH = tall - PARAGRAPH;
		scroll = Mth.clamp(scroll, 0, Math.max(0, textH - textRoom()));
	}

	public int entity() {
		return entity;
	}

	// ---------------------------------------------------------------- layout

	private int boxW() {
		return Math.min(width - 24, MAX_W);
	}

	/** As wide as the longest answer, so short ones leave the words more room. */
	private int answersW() {
		int most = 0;
		for (String o : options) most = Math.max(most, font.width(o));
		return Mth.clamp(most + 28, 110, Math.min(220, boxW() * 2 / 5));
	}

	private int textW() {
		return boxW() - answersW() - 40;
	}

	private int boxH() {
		return Math.min(height - ROOM_ABOVE, Math.max(84, Math.max(22 + options.size() * (OPT + OPT_GAP), textH + TEXT_TOP + TEXT_FOOT)));
	}

	private int textRoom() {
		return boxH() - TEXT_TOP - TEXT_FOOT;
	}

	private int boxX() {
		return (width - boxW()) / 2;
	}

	private int boxY() {
		return height - boxH() - 10;
	}

	private int optX() {
		return boxX() + boxW() - answersW() - 12;
	}

	private int optY(int i) {
		int total = options.size() * (OPT + OPT_GAP) - OPT_GAP;
		return boxY() + (boxH() - total) / 2 + i * (OPT + OPT_GAP);
	}

	private int optionAt(double mx, double my) {
		if (typing() || mx < optX() || mx >= optX() + answersW()) return -1;
		for (int i = 0; i < options.size(); i++) if (my >= optY(i) && my < optY(i) + OPT) return i;
		return -1;
	}

	private void pick(int i) {
		if (typing()) {
			shown = text.length();
			return;
		}
		PacketDistributor.sendToServer(new Net.NpcPick(entity, i));
	}

	private boolean typing() {
		return shown < text.length();
	}

	@Override
	public void tick() {
		ticks++;
		if (typing()) {
			shown = Math.min(text.length(), shown + 1.8f);
			scroll = Math.max(0, typedH() - textRoom());
			// a soft tick of the pen now and then while it types
			if (ticks % 3 == 0) Minecraft.getInstance().getSoundManager().play(SimpleSoundInstance.forUI(SoundEvents.BOOK_PAGE_TURN, 1.8f, 0.06f));
		}
	}

	/** How far down the typing has got. */
	private int typedH() {
		int left = Mth.floor(shown), down = 0;
		for (Line l : lines) {
			if (left <= 0) break;
			down += LINE + l.after;
			left -= l.text.length() + 1;
		}
		return down;
	}

	@Override
	public boolean mouseScrolled(double mx, double my, double dx, double dy) {
		if (typing()) return false;
		scroll = Mth.clamp(scroll - (int) (dy * LINE * 2), 0, Math.max(0, textH - textRoom()));
		return true;
	}

	@Override
	public boolean isPauseScreen() {
		return false;
	}

	@Override
	public boolean keyPressed(int k, int scan, int mods) {
		if (k == InputConstants.KEY_SPACE || k == InputConstants.KEY_RETURN) {
			if (typing()) shown = text.length();
			return true;
		}
		if (k >= InputConstants.KEY_1 && k <= InputConstants.KEY_9) {
			int i = k - InputConstants.KEY_1;
			if (i < options.size()) pick(i);
			return true;
		}
		return super.keyPressed(k, scan, mods);
	}

	@Override
	public boolean mouseClicked(double mx, double my, int button) {
		if (typing()) {
			shown = text.length();
			return true;
		}
		int i = optionAt(mx, my);
		if (i >= 0) {
			Minecraft.getInstance().getSoundManager().play(SimpleSoundInstance.forUI(SoundEvents.UI_BUTTON_CLICK, 1f));
			pick(i);
			return true;
		}
		return super.mouseClicked(mx, my, button);
	}

	@Override
	public void onClose() {
		if (!sentClose) {
			sentClose = true;
			PacketDistributor.sendToServer(new Net.NpcPick(entity, -1));
		}
		super.onClose();
	}

	/** The server ended it: close without telling it back. */
	public void closeQuietly() {
		sentClose = true;
		super.onClose();
	}

	// ---------------------------------------------------------------- drawing

	@Override
	public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
		// only a shadow rising from the bottom: the world (and who you're talking to) stays in view
		g.fillGradient(0, height - boxH() - 70, width, height, 0x00000000, 0x90000000);
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		super.render(g, mx, my, pt);
		int x = boxX(), y = boxY(), w = boxW(), h = boxH();
		// the name plate, a small panel of its own standing on the box's edge
		Component nm = Component.literal(name.toUpperCase()).withStyle(ChatFormatting.BOLD);
		int nw = Math.max(font.width(nm), font.width(title.toUpperCase())) + 30;   // the title is drawn in capitals, which are wider
		int nh = title.isEmpty() ? 22 : 30;
		AshUi.panel(g, x + 12, y - nh + 4, nw, nh);
		g.drawString(font, nm, x + 25, y - nh + 11, AshUi.TEXT, true);
		if (!title.isEmpty()) g.drawString(font, title.toUpperCase(), x + 25, y - nh + 21, AshUi.EMBER_LT, false);
		AshUi.panel(g, x, y, w, h);
		// what they say, typed out, in the middle of the room there is
		int mid = x + 14 + textW() / 2, top = y + TEXT_TOP, room = textRoom();
		int ty = textH <= room ? top + (room - textH) / 2 : top - scroll, left = Mth.floor(shown);
		g.enableScissor(x, top, x + w, top + room);
		for (Line l : lines) {
			int n = typing() ? Math.min(l.text.length(), left) : l.text.length();
			if (n > 0) g.drawString(font, l.text.substring(0, n), mid - font.width(l.text) / 2, ty, AshUi.TEXT, true);
			left -= l.text.length() + 1;
			ty += LINE + l.after;
		}
		g.disableScissor();
		String hint = typing() ? "Space  show all     Esc  leave" : (textH > room ? "Wheel  read on     " : "") + "1-" + Math.max(1, options.size()) + "  answer     Esc  leave";
		g.drawString(font, hint, mid - font.width(hint) / 2, y + h - 16, AshUi.DIM, false);
		// the line between the words and the answers
		int lx = optX() - 8;
		for (int i = y + 10; i < y + h - 10; i += 2) {
			float k = 1 - Math.abs((i - y - h / 2f) / (h / 2f - 10));
			g.fill(lx, i, lx + 1, i + 2, ((int) (0xB0 * k) << 24) | 0x5C544C);
		}
		// the answers
		int hov = optionAt(mx, my);
		for (int i = 0; i < options.size(); i++) {
			int oy = optY(i), ox = optX(), ow = answersW();
			boolean on = i == hov;
			if (typing()) {
				g.fill(ox, oy, ox + ow, oy + OPT, 0x08FFF0DC);
				g.renderOutline(ox, oy, ow, OPT, 0x60050404);
				continue;
			}
			AshUi.row(g, ox, oy, ow, OPT, on, false);
			g.fill(ox + 3, oy + 3, ox + 15, oy + 15, 0xFF0C0B0A);
			g.renderOutline(ox + 3, oy + 3, 12, 12, on ? AshUi.EMBER_LT : 0xFF5C544C);
			String k = String.valueOf(i + 1);
			g.drawString(font, k, ox + 9 - font.width(k) / 2, oy + 5, on ? 0xFFFFF3E2 : 0xFFCFC6B8, true);
			g.drawString(font, font.plainSubstrByWidth(options.get(i), ow - 24), ox + 20, oy + 5, on ? 0xFFFFF3E2 : AshUi.BODY, true);
		}
	}
}
