package com.snoringwalrus.ashbound.client;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import org.joml.Matrix4f;
import org.joml.Vector4f;

import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.Net;

import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.client.event.InputEvent;
import net.neoforged.neoforge.client.event.RegisterGuiLayersEvent;
import net.neoforged.neoforge.client.event.RenderLevelStageEvent;
import net.neoforged.neoforge.client.gui.VanillaGuiLayers;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * The scroll wheel marks what you're looking at for your party: a beam and a ring on the spot, a sound, and a marker on
 * the screen with who, and how far off. A marker off the edge of the screen sticks to the edge, on the side it lies.
 */
public final class Pings {
	private Pings() {}

	private record Mark(String who, Vec3 at, long ends) {}

	private static final double REACH = 160;
	private static final long LASTS = 8000, FADES = 1000;
	private static final int EMBER = 0xFF9A30, EDGE = 18;
	private static final List<Mark> MARKS = new ArrayList<>();
	private static final Matrix4f VIEW = new Matrix4f(), LENS = new Matrix4f();
	private static Vec3 from = Vec3.ZERO;

	/** Where a spot in the world falls on the HUD, or null if it's behind you. */
	static net.minecraft.world.phys.Vec2 screen(Vec3 at, int w, int h) {
		Vector4f v = new Vector4f((float) (at.x - from.x), (float) (at.y - from.y), (float) (at.z - from.z), 1);
		VIEW.transform(v);
		LENS.transform(v);
		return v.w <= 0 ? null : new net.minecraft.world.phys.Vec2((v.x / v.w * 0.5f + 0.5f) * w, (-v.y / v.w * 0.5f + 0.5f) * h);
	}

	public static void hooks(IEventBus bus) {
		bus.addListener((RegisterGuiLayersEvent e) -> e.registerAbove(VanillaGuiLayers.HOTBAR,
				ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "pings"), Pings::draw));
		NeoForge.EVENT_BUS.addListener((RenderLevelStageEvent e) -> {
			if (e.getStage() != RenderLevelStageEvent.Stage.AFTER_PARTICLES) return;
			VIEW.set(e.getModelViewMatrix());
			LENS.set(e.getProjectionMatrix());
			from = e.getCamera().getPosition();
		});
		// the wheel's yours in survival: pick block only stays for creative
		NeoForge.EVENT_BUS.addListener((InputEvent.InteractionKeyMappingTriggered e) -> {
			Minecraft mc = Minecraft.getInstance();
			if (e.isPickBlock() && mc.gameMode != null && !mc.gameMode.hasInfiniteItems() && e.getKeyMapping().same(CurioKeys.PING)) {
				e.setCanceled(true);
				e.setSwingHand(false);
			}
		});
	}

	/** Whatever's under the crosshair, a monster before the ground behind it. */
	static void send() {
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null || mc.level == null) return;
		Vec3 eye = mc.player.getEyePosition(), far = eye.add(mc.player.getLookAngle().scale(REACH));
		HitResult block = mc.level.clip(new ClipContext(eye, far, ClipContext.Block.OUTLINE, ClipContext.Fluid.NONE, mc.player));
		Vec3 end = block.getType() == HitResult.Type.MISS ? far : block.getLocation();
		AABB swept = new AABB(eye, end).inflate(1);
		var hit = ProjectileUtil.getEntityHitResult(mc.player, eye, end, swept, e -> e.isPickable() && !e.isSpectator(), eye.distanceToSqr(end));
		if (hit != null) {
			Entity e = hit.getEntity();
			PacketDistributor.sendToServer(new Net.Ping(e.getX(), e.getY() + e.getBbHeight() * 0.5, e.getZ()));
		} else if (block.getType() != HitResult.Type.MISS) PacketDistributor.sendToServer(new Net.Ping(end.x, end.y, end.z));
	}

	public static void got(Net.PingAt m) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.level == null) return;
		Vec3 at = new Vec3(m.x(), m.y(), m.z());
		MARKS.add(new Mark(m.who(), at, System.currentTimeMillis() + LASTS));
		FxKit.column(mc.level, at, EMBER, 9, 0.18f, 26, null);
		FxKit.rune(mc.level, at, EMBER, 1.2f, 26);
		mc.getSoundManager().play(SimpleSoundInstance.forUI(SoundEvents.NOTE_BLOCK_PLING.value(), 1.5f, 0.7f));
	}

	private static void draw(GuiGraphics g, DeltaTracker dt) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.player == null || mc.options.hideGui || MARKS.isEmpty()) return;
		long now = System.currentTimeMillis();
		int w = g.guiWidth(), h = g.guiHeight();
		for (Iterator<Mark> it = MARKS.iterator(); it.hasNext();) {
			Mark m = it.next();
			if (now >= m.ends()) {
				it.remove();
				continue;
			}
			Vector4f v = new Vector4f((float) (m.at().x - from.x), (float) (m.at().y - from.y), (float) (m.at().z - from.z), 1);
			VIEW.transform(v);
			LENS.transform(v);
			boolean behind = v.w <= 0;
			float d = Math.max(Math.abs(v.w), 0.001f), sx = v.x / d, sy = -v.y / d;
			if (behind) {   // behind you: it comes out mirrored, and goes to the bottom edge
				sx = -sx;
				sy = 1;
			}
			int x = Mth.clamp(Math.round((sx * 0.5f + 0.5f) * w), EDGE, w - EDGE), y = Mth.clamp(Math.round((sy * 0.5f + 0.5f) * h), EDGE, h - EDGE);
			int a = Math.max(4, Math.round(255 * Mth.clamp((m.ends() - now) / (float) FADES, 0, 1))) << 24;
			g.fill(x - 3, y - 1, x + 4, y + 2, a | EMBER);
			g.fill(x - 1, y - 3, x + 2, y + 4, a | EMBER);
			g.fill(x - 1, y - 1, x + 2, y + 2, a | 0xFFF0D8);
			String line = m.who() + "  " + Math.round(mc.player.position().distanceTo(m.at())) + "m";
			g.drawCenteredString(mc.font, line, Mth.clamp(x, mc.font.width(line) / 2 + 2, w - mc.font.width(line) / 2 - 2), y + 7, a | 0xF0E8D8);
		}
	}
}
