package com.snoringwalrus.ashbound.client;

import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.Books;
import com.snoringwalrus.ashbound.Classes;
import com.snoringwalrus.ashbound.Forms;
import com.snoringwalrus.ashbound.Levels;
import com.snoringwalrus.ashbound.Skills;

import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.client.event.RegisterGuiLayersEvent;
import net.neoforged.neoforge.client.gui.VanillaGuiLayers;

/** The four skill keys, left of the hotbar, in iron sockets like the relic's: the first is what's in your hand. */
final class SkillHud {
	private SkillHud() {}

	private static final int SIZE = 22, GAP = 2, OFF_HOTBAR = 8;

	static void hooks(IEventBus bus) {
		bus.addListener((RegisterGuiLayersEvent e) -> e.registerAbove(VanillaGuiLayers.HOTBAR,
				ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "skills"), SkillHud::draw));
	}

	private static final ResourceLocation ICONS = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/gui/skill_icons.png");
	private static final int ICON = 16, COLUMNS = 6, ROWS = 9;

	/** A skill's picture at this spot (tools/skill_items.py). */
	static void icon(GuiGraphics g, Skills.Skill s, int x, int y) {
		int i = Skills.ALL.indexOf(s);
		g.blit(ICONS, x, y, (i % COLUMNS) * ICON, (i / COLUMNS) * ICON, ICON, ICON, COLUMNS * ICON, ROWS * ICON);
	}

	/** What the first key does, and the cooldown it runs on, or null. */
	static String held(Minecraft mc) {
		return SkillScreen.heldName(mc.player.getMainHandItem());
	}

	/** The Tome itself, with the Form key under it: dim until its moment comes, burning red when it has, its seconds while
	 * you're in it, then its rest. */
	private static void form(GuiGraphics g, Font font, int x, int y, long now) {
		int at = Forms.ALL.indexOf(Forms.byId(Forms.clientForm));
		if (at < 0) return;
		boolean in = Forms.clientUntil > now;
		if (Forms.clientReady || in) {
			int rim = (int) (0x90 + 0x60 * (0.5 + 0.5 * Math.sin(now / 90.0))) << 24 | 0xF03018;
			g.fill(x - 1, y - 1, x + SIZE + 1, y + 1, rim);
			g.fill(x - 1, y + SIZE - 1, x + SIZE + 1, y + SIZE + 1, rim);
			g.fill(x - 1, y + 1, x + 1, y + SIZE - 1, rim);
			g.fill(x + SIZE - 1, y + 1, x + SIZE + 1, y + SIZE - 1, rim);
		}
		g.renderItem(new ItemStack(Books.TOMES.get(at).get()), x + 3, y + 3);
		g.pose().pushPose();
		g.pose().translate(0, 0, 200);
		if (!Forms.clientReady && !in) {
			g.fill(x + 1, y + 1, x + SIZE - 1, y + SIZE - 1, 0x99050404);
			if (Forms.clientHave >= 0 && Forms.clientRest <= now) {   // how close the moment is: the Crown's thralls out
				String n = Forms.clientHave + "/" + Forms.needs(Forms.clientForm);
				g.drawString(font, n, x + SIZE / 2 - font.width(n) / 2, y + 4, 0xFFC8A0FF, true);
			}
		}
		long until = in ? Forms.clientUntil : Forms.clientRest > now ? Forms.clientRest : 0;
		if (until > 0) {
			String secs = String.valueOf((int) Math.ceil((until - now) / 1000.0));
			g.drawString(font, secs, x + SIZE / 2 - font.width(secs) / 2, y + 7, in ? 0xFFFF8050 : AshUi.TEXT, true);
		}
		String key = CurioKeys.FORM.getTranslatedKeyMessage().getString();
		g.pose().scale(0.75f, 0.75f, 1);
		g.drawString(font, key, Math.round((x + SIZE - 1) / 0.75f) - font.width(key), Math.round((y + SIZE - 7) / 0.75f), Forms.clientReady ? 0xFFFFA050 : AshUi.MUTED, true);
		g.pose().popPose();
	}

	private static void draw(GuiGraphics g, DeltaTracker dt) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null || mc.options.hideGui || mc.player.isSpectator()) return;
		var font = mc.font;
		long now = System.currentTimeMillis();
		int y = g.guiHeight() - SIZE - 1, x0 = g.guiWidth() / 2 - 91 - OFF_HOTBAR - Skills.SLOTS * (SIZE + GAP) + GAP;
		for (int i = 0; i < Skills.SLOTS; i++) {
			int x = x0 + i * (SIZE + GAP);
			g.fill(x - 1, y - 1, x + SIZE + 1, y + SIZE + 1, 0xFF050404);
			g.fill(x, y, x + SIZE, y + SIZE, 0xFF3D3833);
			g.fill(x + 1, y + 1, x + SIZE - 1, y + SIZE - 1, 0xFF16120F);
			if (i == Skills.SLOTS - 1 && !Forms.clientForm.isEmpty()) {   // the key the Tome took holds its Form
				form(g, font, x, y, now);
				continue;
			}
			String cool = null;
			if (i == 0) {
				String name = held(mc);
				if (name != null) {
					g.renderItem(mc.player.getMainHandItem(), x + 3, y + 3);
					cool = "held";
				}
			} else {
				var s = Skills.byId(Skills.clientBar[i] == null ? "" : Skills.clientBar[i]);
				if (s != null) {
					icon(g, s, x + 3, y + 3);
					cool = s.id();
				}
			}
			g.pose().pushPose();
			g.pose().translate(0, 0, 200);
			long[] c = cool == null ? null : Skills.clientCooling.get(cool);
			if (c != null && c[0] > now) {
				int h = Math.round((SIZE - 2) * (c[0] - now) / (float) c[1]);
				g.fill(x + 1, y + SIZE - 1 - h, x + SIZE - 1, y + SIZE - 1, 0xB0050404);
				String secs = String.valueOf((int) Math.ceil((c[0] - now) / 1000.0));
				g.drawString(font, secs, x + SIZE / 2 - font.width(secs) / 2, y + 7, AshUi.TEXT, true);
			}
			String key = CurioKeys.slotKey(i).getTranslatedKeyMessage().getString();
			g.pose().scale(0.75f, 0.75f, 1);
			g.drawString(font, key, Math.round((x + SIZE - 1) / 0.75f) - font.width(key), Math.round((y + SIZE - 7) / 0.75f), AshUi.MUTED, true);
			g.pose().popPose();
		}
		if (!Classes.client.isEmpty() && Skills.pending(Levels.clientLevel, Skills.clientPicks) >= 0) {
			String t = "New skill: " + CurioKeys.SKILLS.getTranslatedKeyMessage().getString();
			g.drawString(font, t, x0 + (Skills.SLOTS * (SIZE + GAP) - font.width(t)) / 2, y - 11, AshUi.EMBER_LT, true);
		}
	}
}
