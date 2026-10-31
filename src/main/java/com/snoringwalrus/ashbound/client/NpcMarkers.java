package com.snoringwalrus.ashbound.client;

import java.util.HashMap;
import java.util.Map;

import com.mojang.blaze3d.vertex.PoseStack;
import com.snoringwalrus.ashbound.Marks;
import com.snoringwalrus.ashbound.Net;
import com.snoringwalrus.ashbound.Npc;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.network.chat.Component;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.client.event.ClientPlayerNetworkEvent;
import net.neoforged.neoforge.client.event.RenderLevelStageEvent;
import net.neoforged.neoforge.common.NeoForge;

/** Draws what the server says hangs over each head ({@link Marks}): big, always facing you, bobbing a little. */
public final class NpcMarkers {
	private NpcMarkers() {}

	private static final int LIT = 0xF000F0, OUTLINE = 0xFF1A1208;
	private static final float OVER = 0.65f, SIZE = 0.05f, BOB = 0.07f;
	private static final String[] GLYPHS = {"\u2605", "!", "?"};
	private static final int[] COLOURS = {0xFFFFE9A0, 0xFFFFC21F, 0xFF8FE060};
	private static final Map<Integer, Integer> SHOWN = new HashMap<>();

	public static void hooks() {
		Net.onNpcMarks = m -> {
			SHOWN.clear();
			for (int i = 0; i < m.ids().size(); i++) SHOWN.put(m.ids().get(i), m.marks().get(i));
		};
		NeoForge.EVENT_BUS.addListener((ClientPlayerNetworkEvent.LoggingOut e) -> SHOWN.clear());
		NeoForge.EVENT_BUS.addListener(NpcMarkers::draw);
	}

	private static void draw(RenderLevelStageEvent e) {
		if (e.getStage() != RenderLevelStageEvent.Stage.AFTER_ENTITIES || SHOWN.isEmpty()) return;
		Minecraft mc = Minecraft.getInstance();
		if (mc.level == null || mc.options.hideGui) return;
		float pt = e.getPartialTick().getGameTimeDeltaPartialTick(false);
		MultiBufferSource.BufferSource buf = mc.renderBuffers().bufferSource();
		PoseStack ps = e.getPoseStack();
		Vec3 cam = e.getCamera().getPosition();
		float bob = Mth.sin((mc.level.getGameTime() + pt) * 0.12f) * BOB;
		SHOWN.forEach((id, mark) -> {
			if (!(mc.level.getEntity(id) instanceof Npc n)) return;
			Vec3 at = n.getPosition(pt);
			double head = n.getBbHeight() * NpcLooks.scale(n.kindId()) + OVER + bob;
			FormattedCharSequence glyph = Component.literal(GLYPHS[mark]).getVisualOrderText();
			ps.pushPose();
			ps.translate(at.x - cam.x, at.y + head - cam.y, at.z - cam.z);
			ps.mulPose(e.getCamera().rotation());
			ps.scale(SIZE, -SIZE, SIZE);
			Font font = mc.font;
			font.drawInBatch8xOutline(glyph, -font.width(glyph) / 2f, -4, COLOURS[mark], OUTLINE, ps.last().pose(), buf, LIT);
			ps.popPose();
		});
		buf.endBatch();
	}
}
