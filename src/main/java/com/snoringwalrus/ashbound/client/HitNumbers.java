package com.snoringwalrus.ashbound.client;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.Net;

import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec2;
import net.minecraft.world.phys.Vec3;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.client.event.ClientPlayerNetworkEvent;
import net.neoforged.neoforge.client.event.RegisterGuiLayersEvent;
import net.neoforged.neoforge.client.gui.VanillaGuiLayers;
import net.neoforged.neoforge.common.NeoForge;

/**
 * The numbers that jump off what you hit: drawn on the HUD at the spot's place on screen rather than in the world, so a shader pack can't
 * lose them. They pop, arc up and off to one side and fade, and the size goes by how the hit compares with your usual one, so a big hit
 * looks big at any level. Soft colours, none of them white. Off with the Party screen's button (HudPrefs).
 */
public final class HitNumbers {
	private HitNumbers() {}

	private static final int LASTS = 900, MOST = 48, HIT = 0xF0DCBC, BIG = 0xFFB84A, THRALL = 0xC8A0E8, HEAL = 0x7FE08A;
	private static final float POP = 0.14f, POP_SIZE = 0.6f, RISE = 30, DROP = 16, DRIFT = 22, SMALLEST = 0.85f, LARGEST = 1.8f, BIG_FROM = 1.6f, USUAL_KEEP = 0.92f, FADE_FROM = 0.6f;
	private static final float[] usual = new float[3];

	private record Pop(Vec3 at, String text, int colour, float size, float side, long born) {}

	private static final List<Pop> POPS = new ArrayList<>();

	public static void hooks(IEventBus bus) {
		HudPrefs.load();
		Net.onHitNumber = HitNumbers::add;
		bus.addListener((RegisterGuiLayersEvent e) -> e.registerAbove(VanillaGuiLayers.HOTBAR,
				ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "hit_numbers"), HitNumbers::draw));
		NeoForge.EVENT_BUS.addListener((ClientPlayerNetworkEvent.LoggingOut e) -> POPS.clear());
	}

	static String shortly(float n) {
		return n >= 1_000_000 ? String.format("%.1fM", n / 1_000_000) : n >= 10_000 ? String.format("%.1fk", n / 1000) : String.format("%,d", Math.max(1, Math.round(n)));
	}

	private static void add(Net.HitNumber m) {
		if (!HudPrefs.numbers) return;
		int k = m.kind();
		usual[k] = usual[k] == 0 ? m.amount() : usual[k] * USUAL_KEEP + m.amount() * (1 - USUAL_KEEP);
		float against = m.amount() / usual[k];
		int colour = k == Net.HitNumber.HEAL ? HEAL : k == Net.HitNumber.THRALL ? THRALL : against >= BIG_FROM ? BIG : HIT;
		var r = Minecraft.getInstance().level == null ? null : Minecraft.getInstance().level.random;
		float side = r == null ? 0 : r.nextFloat() * 2 - 1;
		POPS.add(new Pop(new Vec3(m.x(), m.y(), m.z()), (k == Net.HitNumber.HEAL ? "+" : "") + shortly(m.amount()), colour, Mth.clamp(against, SMALLEST, LARGEST), side, System.currentTimeMillis()));
		if (POPS.size() > MOST) POPS.remove(0);
	}

	private static void draw(GuiGraphics g, DeltaTracker dt) {
		Minecraft mc = Minecraft.getInstance();
		if (POPS.isEmpty() || mc.player == null || mc.options.hideGui) return;
		long now = System.currentTimeMillis();
		for (Iterator<Pop> it = POPS.iterator(); it.hasNext();) {
			Pop p = it.next();
			float t = (now - p.born()) / (float) LASTS;
			if (t >= 1) {
				it.remove();
				continue;
			}
			Vec2 at = Pings.screen(p.at(), g.guiWidth(), g.guiHeight());
			if (at == null) continue;
			float size = p.size() * (1 + POP_SIZE * Math.max(0, 1 - t / POP));
			int a = Math.max(8, Math.round(255 * (t < FADE_FROM ? 1 : (1 - t) / (1 - FADE_FROM)))) << 24;
			g.pose().pushPose();
			g.pose().translate(at.x + p.side() * DRIFT * t, at.y - RISE * t + DROP * t * t, 0);
			g.pose().scale(size, size, 1);
			g.drawCenteredString(mc.font, p.text(), 0, -4, a | p.colour());
			g.pose().popPose();
		}
	}
}
