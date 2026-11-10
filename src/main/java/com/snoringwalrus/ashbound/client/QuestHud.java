package com.snoringwalrus.ashbound.client;

import java.util.List;

import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.Net;

import net.minecraft.ChatFormatting;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.Mth;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.client.event.ClientPlayerNetworkEvent;
import net.neoforged.neoforge.client.event.RegisterGuiLayersEvent;
import net.neoforged.neoforge.client.event.RenderGuiLayerEvent;
import net.neoforged.neoforge.client.gui.VanillaGuiLayers;
import net.neoforged.neoforge.common.NeoForge;

/**
 * The compass along the top of the screen: the four quarters sliding by as you turn, each quest you're following as a
 * mark of its own colour, their names and how far they are under the bar. Nothing to follow, and it isn't there; boss
 * bars move down to make room. A quest finished comes up under it for a few seconds.
 */
public final class QuestHud {
	private QuestHud() {}

	static final int W = 170;
	private static final int H = 11, TOP = 5, ROOM = 20, LINE = 10, BANNER_MS = 4000;
	/** one per quest followed, in the order they were picked */
	private static final int[] COLOURS = {0xFFFFD24A, 0xFF6CD8FF, 0xFFFF8AC8, 0xFF9BE07A, 0xFFFF9A50};
	private static final String[] QUARTERS = {"S", "", "W", "", "N", "", "E", ""};
	private static List<Net.QuestTrack> now = List.of();
	private static String finished;
	private static long finishedAt;

	public static void hooks(IEventBus bus) {
		bus.addListener((RegisterGuiLayersEvent e) -> e.registerAbove(VanillaGuiLayers.HOTBAR,
				ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "compass"), QuestHud::draw));
		Net.onQuestTrack = m -> now = m.all().stream().filter(t -> !t.title().isEmpty()).toList();
		NeoForge.EVENT_BUS.addListener((ClientPlayerNetworkEvent.LoggingOut e) -> {
			now = List.of();
			QuestScreen.leave();
		});
		NeoForge.EVENT_BUS.addListener((RenderGuiLayerEvent.Pre e) -> {
			if (e.getName().equals(VanillaGuiLayers.BOSS_OVERLAY) && showing()) {
				e.getGuiGraphics().pose().pushPose();
				e.getGuiGraphics().pose().translate(0, ROOM + (now.size() - 1) * LINE, 0);
			}
		});
		NeoForge.EVENT_BUS.addListener((RenderGuiLayerEvent.Post e) -> {
			if (e.getName().equals(VanillaGuiLayers.BOSS_OVERLAY) && showing()) e.getGuiGraphics().pose().popPose();
		});
	}

	/** A quest just done. */
	static void finished(String title) {
		finished = title;
		finishedAt = System.currentTimeMillis();
		Minecraft mc = Minecraft.getInstance();
		mc.getSoundManager().play(SimpleSoundInstance.forUI(SoundEvents.PLAYER_LEVELUP, 1.4f, 0.5f));
	}

	private static boolean showing() {
		return !now.isEmpty() && !Minecraft.getInstance().options.hideGui;
	}

	/** Where something at this yaw falls along the bar, the bar spanning a quarter turn each side. */
	private static float along(float yaw, float heading) {
		return Mth.wrapDegrees(yaw - heading) / 90f * (W / 2f);
	}

	private static void draw(GuiGraphics g, DeltaTracker dt) {
		Minecraft mc = Minecraft.getInstance();
		LocalPlayer p = mc.player;
		if (p == null || mc.options.hideGui) return;
		if (showing()) compass(g, mc, p, dt);
		banner(g, mc);
	}

	private static void compass(GuiGraphics g, Minecraft mc, LocalPlayer p, DeltaTracker dt) {
		int cx = g.guiWidth() / 2, x0 = cx - W / 2, y = TOP;
		float heading = p.getViewYRot(dt.getGameTimeDeltaPartialTick(false));
		VitalsHud.frame(g, x0, y, W, H);
		g.fill(x0, y, x0 + W, y + H, 0xE0181412);
		g.fill(x0, y + H - 1, x0 + W, y + H, AshUi.EMBER_C);
		g.enableScissor(x0, y, x0 + W, y + H);
		for (int k = 0; k < 8; k++) {
			float a = along(k * 45f, heading);
			if (Math.abs(a) > W / 2f + 8) continue;
			int ax = cx + Math.round(a);
			String q = QUARTERS[k];
			if (q.isEmpty()) g.fill(ax, y + 7, ax + 1, y + H - 1, 0xFF6A625A);
			else g.drawString(mc.font, q, ax - mc.font.width(q) / 2, y + 2, q.equals("N") ? AshUi.EMBER_LT : AshUi.TEXT, false);
		}
		g.disableScissor();
		g.fill(cx, y - 2, cx + 1, y + 3, 0xFFECE4D6);
		for (int i = now.size() - 1; i >= 0; i--) {   // the first picked drawn last, on top
			Net.QuestTrack q = now.get(i);
			if (!q.has()) continue;
			int colour = COLOURS[i % COLOURS.length];
			double dx = q.x() + 0.5 - p.getX(), dz = q.z() + 0.5 - p.getZ();
			float a = along((float) (Mth.atan2(-dx, dz) * Mth.RAD_TO_DEG), heading);
			int mx = cx + Mth.clamp(Math.round(a), -W / 2 + 3, W / 2 - 3);
			g.fill(mx - 1, y + 1, mx + 2, y + H - 2, colour);
			g.fill(mx - 2, y + 3, mx + 3, y + H - 4, colour);
			g.fill(mx, y + 3, mx + 1, y + H - 4, 0xFF1A1208);
		}
		int ty = y + H + 4;
		for (int i = 0; i < now.size(); i++) {
			Net.QuestTrack q = now.get(i);
			String text = q.title() + (q.has() ? "  " + Math.round(Math.hypot(q.x() - p.getX(), q.z() - p.getZ())) + "m" : "");
			g.drawString(mc.font, text, cx - mc.font.width(text) / 2, ty, COLOURS[i % COLOURS.length], true);
			ty += LINE;
		}
	}

	private static void banner(GuiGraphics g, Minecraft mc) {
		long since = System.currentTimeMillis() - finishedAt;
		if (finished == null || since > BANNER_MS) return;
		float a = since < 250 ? since / 250f : since > BANNER_MS - 800 ? (BANNER_MS - since) / 800f : 1f;
		int alpha = Math.max(4, Math.round(a * 255)) << 24;
		int cx = g.guiWidth() / 2, y = g.guiHeight() / 5;
		Component head = Component.literal("QUEST COMPLETE").withStyle(ChatFormatting.BOLD);
		g.drawString(mc.font, head, cx - mc.font.width(head) / 2, y, alpha | 0xF0A050, true);
		AshUi.rule(g, cx - 90, cx - 4, y + 11, false);
		AshUi.rule(g, cx + 4, cx + 90, y + 11, true);
		g.drawString(mc.font, finished, cx - mc.font.width(finished) / 2, y + 16, alpha | 0xECE4D6, true);
	}
}
