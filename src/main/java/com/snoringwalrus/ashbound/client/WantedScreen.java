package com.snoringwalrus.ashbound.client;

import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.math.Axis;
import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.Net;

import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.Mth;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * A wanted poster, read (Bounties.read): the poster large on the left, what it's offering on the right, and Back / Take it
 * (Claim the bounty, when yours is dead). Taking it tears it off its nail: the sheet rips away under the strip that stays.
 */
public class WantedScreen extends Screen {
	private static final int W = 340, H = 236, PAD = 12, PW = 152, PH = 209, BTN_W = 74, BTN_H = 20, TEAR = 16;
	private static final String RANKS = "FEDCBAS";
	/** the poster's rows left on the nail when it's torn (tools/posters.py TORN) */
	private static final int TORN_ROWS = 30;
	/** a poster just torn here, shown torn on the wall before the server's word comes back */
	static int tornNow = -1;

	private final Net.PosterView v;
	private final ResourceLocation tex;
	/** ticks since it was torn (-1: not yet) */
	private int tear = -1;

	public WantedScreen(Net.PosterView v) {
		super(Component.literal("Wanted"));
		this.v = v;
		int r = Math.max(0, Math.min(6, v.nums().get(0)));
		tex = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/entity/wanted/" + v.texts().get(0) + "_" + Character.toLowerCase(RANKS.charAt(r)) + ".png");
	}

	private int left() {
		return (width - W) / 2;
	}

	private int top() {
		return (height - H) / 2;
	}

	private int col() {
		return left() + PAD + PW + 14;
	}

	private int btnY() {
		return top() + H - PAD - BTN_H;
	}

	/** the main button: take it, or claim; none when there's nothing to do */
	private String main() {
		return switch (v.state()) {
			case 0 -> "Take it";
			case 2 -> "Claim bounty";
			default -> null;
		};
	}

	private static boolean in(double mx, double my, int x, int y, int w, int h) {
		return mx >= x && mx < x + w && my >= y && my < y + h;
	}

	@Override
	public boolean isPauseScreen() {
		return false;
	}

	@Override
	public void tick() {
		if (tear >= 0 && ++tear > TEAR) onClose();
	}

	@Override
	public boolean mouseClicked(double mx, double my, int button) {
		if (tear >= 0) return true;
		int x2 = left() + W - PAD - BTN_W, x1 = x2 - 6 - BTN_W, y = btnY();
		if (in(mx, my, x2, y, BTN_W, BTN_H)) {
			onClose();
			return true;
		}
		if (main() != null && in(mx, my, x1, y, BTN_W, BTN_H)) {
			PacketDistributor.sendToServer(new Net.PosterAct(v.entity()));
			var sounds = Minecraft.getInstance().getSoundManager();
			if (v.state() == 0) {
				tear = 0;
				tornNow = v.nums().get(3);
				sounds.play(SimpleSoundInstance.forUI(SoundEvents.PAINTING_BREAK, 1.3f, 1f));
				sounds.play(SimpleSoundInstance.forUI(SoundEvents.BOOK_PAGE_TURN, 0.7f, 1f));
			} else {
				sounds.play(SimpleSoundInstance.forUI(SoundEvents.PLAYER_LEVELUP, 1.4f, 0.5f));
				onClose();
			}
			return true;
		}
		return super.mouseClicked(mx, my, button);
	}

	private int lines(GuiGraphics g, String text, int x, int y, int w, int colour) {
		for (FormattedCharSequence l : font.split(Component.literal(text), w)) {
			g.drawString(font, l, x, y, colour, false);
			y += 10;
		}
		return y;
	}

	@Override
	public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
		g.fill(0, 0, width, height, 0xB0000000);
		AshUi.panel(g, left(), top(), W, H);
		poster(g, pt);
		int x = col(), w = left() + W - PAD - x, y = top() + PAD + 4;
		// who's wanted
		g.drawString(font, "WANTED BY THE GUILD", x, y, AshUi.EMBER_C, false);
		y += 13;
		for (FormattedCharSequence l : font.split(Component.literal(v.texts().get(1)).withStyle(ChatFormatting.BOLD), w)) {
			g.drawString(font, l, x, y, AshUi.TEXT, true);
			y += 11;
		}
		y += 3;
		int rank = v.nums().get(0);
		AshUi.seal(g, x, y, 20, rank);
		g.drawString(font, RANKS.charAt(Math.max(0, Math.min(6, rank))) + "-rank Legend", x + 26, y + 6, AshUi.BODY, false);
		y += 28;
		AshUi.divider(g, x, y, w);
		y += 8;
		// where
		g.drawString(font, "LAST SEEN", x, y, AshUi.LABEL, false);
		y += 11;
		y = lines(g, "In " + v.texts().get(2) + ",", x, y, w, AshUi.BODY);
		y = lines(g, v.texts().get(3) + " from here.", x, y, w, AshUi.MUTED);
		y += 6;
		// what it pays
		g.drawString(font, "REWARD", x, y, AshUi.LABEL, false);
		y += 11;
		AshUi.coin(g, x, y - 1);
		g.drawString(font, String.format("%,d coins", v.nums().get(1)), x + 12, y, AshUi.EMBER_LT, false);
		y += 11;
		if (v.nums().get(2) > 0) {
			g.drawString(font, "+" + v.nums().get(2) + " Guild Points", x + 12, y, AshUi.BODY, false);
			y += 11;
		}
		y += 4;
		String note = switch (v.state()) {
			case 1 -> "You're already hunting it. Follow the compass, then its tracks.";
			case 2 -> "You slew " + v.texts().get(1) + ". The Guild pays.";
			case 3 -> "Slain" + (v.texts().get(4).isEmpty() ? "." : " by " + v.texts().get(4) + ".");
			case 4 -> "Your hands are full. Finish or give up a favour first.";
			default -> "Tear it down to take the hunt. It goes in your Journal and on your compass.";
		};
		lines(g, note, x, y, w, v.state() == 4 ? AshUi.BAD : v.state() == 2 ? AshUi.EMBER_LT : AshUi.DIM);
		// the buttons
		int x2 = left() + W - PAD - BTN_W, x1 = x2 - 6 - BTN_W, by = btnY();
		String main = main();
		if (main != null) {
			AshUi.row(g, x1, by, BTN_W, BTN_H, false, tear < 0 && in(mx, my, x1, by, BTN_W, BTN_H));
			g.drawString(font, main, x1 + (BTN_W - font.width(main)) / 2, by + 6, AshUi.EMBER_C, true);
		}
		AshUi.row(g, x2, by, BTN_W, BTN_H, false, tear < 0 && in(mx, my, x2, by, BTN_W, BTN_H));
		g.drawString(font, "Back", x2 + (BTN_W - font.width("Back")) / 2, by + 6, AshUi.TEXT, true);
	}

	/** The poster, nailed up in its frame; when torn, the sheet rips off below the strip that stays and falls away. */
	private void poster(GuiGraphics g, float pt) {
		int px = left() + PAD, py = top() + PAD + 2;
		g.fill(px - 2, py - 2, px + PW + 2, py + PH + 2, 0xFF1A1410);
		if (tear < 0) {
			g.blit(tex, px, py, PW, PH, 0, 0, 128, 176, 128, 176);
			return;
		}
		float t = Mth.clamp((tear + pt) / TEAR, 0, 1);
		int cut = PH * TORN_ROWS / 176;
		// the sheet: rips from the left corner, swings down and away, fading
		var ps = g.pose();
		ps.pushPose();
		ps.translate(px + PW * 0.15f, py + cut, 0);
		ps.translate(t * 30, t * t * 140, 0);
		ps.mulPose(Axis.ZP.rotationDegrees(t * 24));
		RenderSystem.enableBlend();
		g.setColor(1, 1, 1, 1 - t * t);
		g.blit(tex, -(int) (PW * 0.15f), 0, PW, PH - cut, 0, TORN_ROWS, 128, 176 - TORN_ROWS, 128, 176);
		g.setColor(1, 1, 1, 1);
		ps.popPose();
		// what's left on the nail
		g.blit(WantedPosterRenderer.TORN, px, py, PW, PH, 0, 0, 128, 176, 128, 176);
	}

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		super.render(g, mx, my, pt);
	}
}
