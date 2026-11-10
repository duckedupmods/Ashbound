package com.snoringwalrus.ashbound.client;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import org.joml.Matrix4f;
import org.joml.Quaternionf;
import org.lwjgl.opengl.GL11;

import com.mojang.blaze3d.pipeline.TextureTarget;
import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.GateDungeons;
import com.snoringwalrus.ashbound.GateEntity;
import com.snoringwalrus.ashbound.Lairs;
import com.snoringwalrus.ashbound.SkyCrack;

import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.texture.AbstractTexture;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.LightLayer;
import net.minecraft.world.phys.Vec3;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.client.event.RenderLevelStageEvent;

/**
 * What you see through a gate (tools/gate_window.py is the look): its dungeon's first hall, really there behind it, and
 * through a way out, the world you came in from. Each frame, for the nearest few open gates, the far side (a BlockMesh)
 * is drawn from your own camera into a texture of its own (half size), as if it stood just behind the tear; the tear's
 * inside (gate_rift.fsh) then shows that texture where it is on screen, so it shifts as you move like a real window.
 * The far side is turned to whichever face you're looking at. Under a shader pack there's no window (the dark inside).
 */
@EventBusSubscriber(modid = Ashbound.ID, value = Dist.CLIENT)
public final class GateWindow {
	private GateWindow() {}

	public static final int SLOTS = 3;
	static final ResourceLocation[] TEX = new ResourceLocation[SLOTS];
	private static final TextureTarget[] TARGETS = new TextureTarget[SLOTS];
	private static final Map<UUID, Integer> SLOT = new HashMap<>();
	private static boolean registered;

	/** A far side: its blocks, where the tear stands in it (its foot), which way is "in", and what's behind it all. */
	private record Side(BlockMesh mesh, Vec3 anchor, Vec3 in, float[] sky) {}

	/** First halls by dungeon, a few kept. */
	private static final Map<String, Side> HALLS = new LinkedHashMap<>(8, 0.75f, true);
	/** The world behind the last gate you came near (shown through any way out); which gate it was. */
	private static Side outside;
	private static UUID outsideOf;

	static {
		for (int i = 0; i < SLOTS; i++) TEX[i] = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "gate_pocket_" + i);
	}

	/** Its textures, so the tear's render types can name them (GateRenderer, once, on the render thread). */
	static void register() {
		if (registered) return;
		registered = true;
		for (int i = 0; i < SLOTS; i++) {
			int k = i;
			Minecraft.getInstance().getTextureManager().register(TEX[i], new AbstractTexture() {
				@Override
				public void load(ResourceManager rm) {}

				@Override
				public int getId() {
					return TARGETS[k] == null ? 0 : TARGETS[k].getColorTextureId();
				}

				@Override
				public void releaseId() {}
			});
		}
	}

	/** Which texture this gate's far side was drawn into this frame, or -1 (none: draw the dark inside). */
	public static int slot(GateEntity g) {
		return SLOT.getOrDefault(g.getUUID(), -1);
	}

	// ---------------------------------------------------------------- the far sides

	/** A dungeon's first hall: what lies beyond its arrival point (it arrives facing north, so "in" is -z), lit by its own lamps. */
	private static Side hall(String lair) {
		Side have = HALLS.get(lair);
		if (have != null) return have;
		Vec3 tp = Lairs.points(lair).get("tp");
		if (tp == null) return null;
		int tx = Mth.floor(tp.x), ty = Mth.floor(tp.y), plane = Mth.floor(tp.z) + 1;
		BlockMesh.Blocks b = new BlockMesh.Blocks();
		Lairs.blocks(lair, (x, y, z, st) -> {
			if (z <= plane - 1 && z >= plane - 48 && Math.abs(x - tx) <= 20 && y >= ty - 4 && y <= ty + 18) b.put(x, y, z, st);
		});
		b.flood();
		Side s = new Side(BlockMesh.of(b, 0), new Vec3(tp.x, ty, plane), new Vec3(0, 0, -1), new float[] {0.015f, 0.015f, 0.025f});
		HALLS.put(lair, s);
		if (HALLS.size() > 6) {
			var first = HALLS.entrySet().iterator().next();
			first.getValue().mesh().close();
			HALLS.remove(first.getKey());
		}
		return s;
	}

	/** First halls with their roofs cut away, for cracks in the sky: you look down into them through the tear. */
	private static final Map<String, Side> OPEN_HALLS = new LinkedHashMap<>(4, 0.75f, true);
	/** how much bigger than life a hall hangs behind a sky crack, and how far behind the tear its floor is (in its blocks) */
	private static final float SKY_HALL = 1.6f, SKY_DEPTH = 14f;

	/** A dungeon's first hall as a sky crack shows it: roof and bedrock gone, its floor's middle the anchor. */
	private static Side openHall(String lair) {
		Side have = OPEN_HALLS.get(lair);
		if (have != null) return have;
		Vec3 tp = Lairs.points(lair).get("tp");
		if (tp == null) return null;
		int tx = Mth.floor(tp.x), ty = Mth.floor(tp.y), tz = Mth.floor(tp.z);
		Map<Long, net.minecraft.world.level.block.state.BlockState> all = new HashMap<>();
		Lairs.blocks(lair, (x, y, z, st) -> {
			if (z <= tz + 4 && z >= tz - 46 && Math.abs(x - tx) <= 26 && y >= ty - 4 && y <= ty + 40) all.put(BlockPos.asLong(x, y, z), st);
		});
		// the roof: the first solid block over the arrival point's neighbourhood (a third of the way up the ones found)
		List<Integer> roofs = new ArrayList<>();
		for (int dx = -6; dx <= 6; dx += 3)
			for (int dz = -12; dz <= 0; dz += 3)
				for (int y = ty + 2; y < ty + 40; y++) {
					var st = all.get(BlockPos.asLong(tx + dx, y, tz + dz));
					if (st != null && !st.isAir() && st.getLightEmission() == 0 && st.isSolid()) {
						roofs.add(y);
						break;
					}
				}
		roofs.sort(null);
		int roof = roofs.isEmpty() ? ty + 12 : roofs.get(roofs.size() / 3);
		BlockMesh.Blocks b = new BlockMesh.Blocks();
		for (var e : all.entrySet()) {
			BlockPos p = BlockPos.of(e.getKey());
			if (p.getY() < roof && !e.getValue().is(net.minecraft.world.level.block.Blocks.BEDROCK)) b.put(p.getX(), p.getY(), p.getZ(), e.getValue());
		}
		b.flood();
		Side s = new Side(BlockMesh.of(b, 0), new Vec3(tx + 0.5, ty, tz - 21), new Vec3(0, 0, -1), new float[] {0.03f, 0.012f, 0.012f});
		OPEN_HALLS.put(lair, s);
		if (OPEN_HALLS.size() > 3) {
			var first = OPEN_HALLS.entrySet().iterator().next();
			first.getValue().mesh().close();
			OPEN_HALLS.remove(first.getKey());
		}
		return s;
	}

	/** The world in front of a gate, from the side you stand on, as you walk up to it: kept for its way out. Blocks are
	 *  kept as they lie (axis-aligned, relative to its foot); "in" is the way away from the gate on your side. */
	private static void snapshot(GateEntity g) {
		Minecraft mc = Minecraft.getInstance();
		Vec3 f = g.facing();
		if (mc.player.position().subtract(g.position()).dot(f) < 0) f = f.reverse();
		BlockPos foot = g.blockPosition();
		BlockMesh.Blocks b = new BlockMesh.Blocks();
		BlockPos.MutableBlockPos p = new BlockPos.MutableBlockPos();
		for (int dx = -30; dx <= 30; dx++)
			for (int dz = -30; dz <= 30; dz++) {
				double along = (dx + 0.5) * f.x + (dz + 0.5) * f.z;
				if (along < 1 || along > 30) continue;
				for (int dy = -6; dy <= 20; dy++) {
					p.set(foot.getX() + dx, foot.getY() + dy, foot.getZ() + dz);
					b.put(dx, dy, dz, mc.level.getBlockState(p));
					b.light(dx, dy, dz, mc.level.getBrightness(LightLayer.BLOCK, p), mc.level.getBrightness(LightLayer.SKY, p));
				}
			}
		Vec3 sky = mc.level.getSkyColor(mc.player.position(), 1);
		if (outside != null) outside.mesh().close();
		outside = new Side(BlockMesh.of(b, 1), Vec3.ZERO, f, new float[] {(float) sky.x, (float) sky.y, (float) sky.z});
		outsideOf = g.getUUID();
	}

	@SubscribeEvent
	static void tick(ClientTickEvent.Post e) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.level == null || mc.player == null || mc.level.dimension() == Lairs.GATES) return;
		for (Entity en : mc.level.entitiesForRendering()) {
			if (en instanceof GateEntity g && !g.wayOut() && !g.getUUID().equals(outsideOf) && en.getId() >= 0
					&& g.distanceToSqr(mc.player) < 14 * 14 && !g.closing())
				snapshot(g);
		}
	}

	private static Side side(GateEntity g) {
		if (g.wayOut()) return outside;
		String lair = GateDungeons.of(g).lair();
		return lair == null ? null : g.sky() ? openHall(lair) : hall(lair);
	}

	// ---------------------------------------------------------------- drawing them

	private static TextureTarget target(int i, int w, int h) {
		TextureTarget t = TARGETS[i];
		if (t == null) {
			t = TARGETS[i] = new TextureTarget(w, h, true, Minecraft.ON_OSX);
			t.setFilterMode(GL11.GL_LINEAR);
		} else if (t.width != w || t.height != h) {
			t.resize(w, h, Minecraft.ON_OSX);
		}
		return t;
	}

	@SubscribeEvent
	static void draw(RenderLevelStageEvent e) {
		if (e.getStage() != RenderLevelStageEvent.Stage.AFTER_SKY) return;
		SLOT.clear();
		Minecraft mc = Minecraft.getInstance();
		if (mc.level == null || ShaderPacks.on()) return;
		Vec3 cam = e.getCamera().getPosition();
		List<GateEntity> near = new ArrayList<>();
		for (Entity en : mc.level.entitiesForRendering())
			if (en instanceof GateEntity g && g.position().distanceToSqr(cam) < (g.sky() ? 480 * 480 : 112 * 112)) near.add(g);
		if (near.isEmpty()) return;
		near.sort((a, b) -> Double.compare(a.position().distanceToSqr(cam), b.position().distanceToSqr(cam)));
		var main = mc.getMainRenderTarget();
		int w = Math.max(1, main.width / 2), h = Math.max(1, main.height / 2);
		float pt = e.getPartialTick().getGameTimeDeltaPartialTick(false);
		int used = 0;
		for (GateEntity g : near) {
			if (used >= SLOTS) break;
			Side s = side(g);
			if (s == null || !s.mesh().ready()) continue;
			if (g instanceof SkyCrack sk) {
				// hung behind the tear, its floor away from you: looking up through the crack you look down into it
				Vec3 mid = sk.getPosition(pt).add(0, GateEntity.MID, 0);
				Quaternionf face = new Quaternionf().rotateY((float) Math.toRadians(-sk.getYRot())).rotateX((float) Math.toRadians(sk.tilt()))
						.rotateZ((float) Math.toRadians(sk.roll()));
				org.joml.Vector3f toCam = new org.joml.Vector3f((float) (cam.x - mid.x), (float) (cam.y - mid.y), (float) (cam.z - mid.z))
						.rotate(new Quaternionf(face).invert());
				float sgn = toCam.z >= 0 ? 1 : -1;
				// its up toward you (the face's z, your side), its "in" along the tear's length, its width across it
				Matrix4f hall = new Matrix4f(sgn, 0, 0, 0, 0, 0, sgn, 0, 0, -1, 0, 0, 0, 0, 0, 1);
				TextureTarget t = target(used, w, h);
				t.setClearColor(s.sky()[0], s.sky()[1], s.sky()[2], 1);
				t.clear(Minecraft.ON_OSX);
				t.bindWrite(true);
				Matrix4f mv = new Matrix4f(e.getModelViewMatrix())
						.translate((float) (mid.x - cam.x), (float) (mid.y - cam.y), (float) (mid.z - cam.z))
						.rotate(face)
						.mul(hall)
						.scale(SKY_HALL)
						.translate(0, -SKY_DEPTH, 0)
						.translate((float) -s.anchor().x, (float) -s.anchor().y, (float) -s.anchor().z);
				s.mesh().draw(mv, e.getProjectionMatrix(), true, true);
				SLOT.put(g.getUUID(), used++);
				continue;
			}
			// "in" on the far side goes away from you: turned to the face you're looking at
			Vec3 at = g.getPosition(pt), f = g.facing();
			if (cam.subtract(at).dot(f) < 0) f = f.reverse();
			float turn = (float) (Math.atan2(-f.x, -f.z) - Math.atan2(s.in().x, s.in().z));
			TextureTarget t = target(used, w, h);
			t.setClearColor(s.sky()[0], s.sky()[1], s.sky()[2], 1);
			t.clear(Minecraft.ON_OSX);
			t.bindWrite(true);
			Matrix4f mv = new Matrix4f(e.getModelViewMatrix())
					.translate((float) (at.x - cam.x), (float) (at.y - cam.y), (float) (at.z - cam.z))
					.rotateY(turn)
					.translate((float) -s.anchor().x, (float) -s.anchor().y, (float) -s.anchor().z);
			s.mesh().draw(mv, e.getProjectionMatrix(), true, true);
			SLOT.put(g.getUUID(), used++);
		}
		main.bindWrite(true);
	}
}
