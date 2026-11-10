package com.snoringwalrus.ashbound.client;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.joml.Matrix3f;
import org.joml.Matrix4f;
import org.joml.Vector3f;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mojang.blaze3d.platform.NativeImage;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.BufferBuilder;
import com.mojang.blaze3d.vertex.ByteBufferBuilder;
import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.mojang.blaze3d.vertex.MeshData;
import com.mojang.blaze3d.vertex.VertexBuffer;
import com.mojang.blaze3d.vertex.VertexFormat;
import com.snoringwalrus.ashbound.Arena;
import com.snoringwalrus.ashbound.ArenaShape;
import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.Net;

import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.RenderStateShard;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.ShaderInstance;
import net.minecraft.client.renderer.texture.DynamicTexture;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.client.event.RenderLevelStageEvent;

/**
 * The Ring's crowd (Arena; the look is tools/blender/arena_ring.py): the city's own townsfolk - their meshes
 * (animmodels/entity/npc, the forge's cube cast) and their own textures - packed on the stands: townsfolk, elves, dwarves,
 * the outcast demons, adventurers of every rank, grown-ups and children. Most sit (legs turned forward over the step),
 * some stand, some with an arm in the air, all facing the sand. Not entities: posed and baked once into one mesh (in
 * SECTIONS slices round the bowl, every texture on one sheet), drawn into every Ring near you. They jump when the server
 * says (Net.ArenaCheer): a few slices at each kill, all of them when a wave starts, a wave running round the bowl when
 * one's won, on their feet roaring when a ruler comes through, hushed when one of you falls.
 */
@EventBusSubscriber(modid = Ashbound.ID, value = Dist.CLIENT)
public final class ArenaCrowd {
	private ArenaCrowd() {}

	static final int SECTIONS = 48, TW = 128, TH = 64, COLS = 16;
	static final ResourceLocation SHEET = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "dynamic/arena_crowd");
	private static VertexBuffer[] mesh;
	private static boolean failed;
	/** per slice: ticks of hopping left; the time a wave was won (the running wave), a ruler came, one fell */
	private static final float[] HOP = new float[SECTIONS];
	private static long wonAt = -1000, rulerAt = -1000, hushAt = -1000, ticks;

	static {
		Net.onCheer = ArenaCrowd::cheer;
	}

	/** Entity cut-out drawing (lit like any entity) in triangles, off the crowd's sheet. */
	static final class Types extends RenderType {
		private Types() {
			super(null, null, null, 0, false, false, null, null);
		}

		static final RenderType CROWD = create(Ashbound.ID + "_arena_crowd", DefaultVertexFormat.NEW_ENTITY, VertexFormat.Mode.TRIANGLES, 1 << 16, false, false,
				CompositeState.builder().setShaderState(RENDERTYPE_ENTITY_CUTOUT_NO_CULL_SHADER).setTextureState(new RenderStateShard.TextureStateShard(SHEET, false, false))
						.setTransparencyState(NO_TRANSPARENCY).setCullState(NO_CULL).setLightmapState(LIGHTMAP).setOverlayState(OVERLAY).createCompositeState(true));
	}

	static void cheer(Net.ArenaCheer m) {
		var mc = Minecraft.getInstance();
		if (mc.level == null) return;
		var r = mc.level.getRandom();
		switch (m.kind()) {
			case 0 -> {
				for (int i = 0; i < 6; i++) HOP[r.nextInt(SECTIONS)] = 12;
			}
			case 1 -> {
				for (int i = 0; i < SECTIONS; i++) HOP[i] = 8 + r.nextInt(6);
			}
			case 2 -> {
				wonAt = ticks;
				for (int i = 0; i < SECTIONS; i++) HOP[i] = 20;
			}
			case 3 -> rulerAt = ticks;
			case 4 -> hushAt = ticks;
			default -> {}
		}
	}

	@SubscribeEvent
	static void tick(ClientTickEvent.Post e) {
		ticks++;
		for (int i = 0; i < SECTIONS; i++) if (HOP[i] > 0) HOP[i]--;
	}

	/** How high slice i is off its seats right now. */
	private static float lift(int i, float pt) {
		float t = ticks + pt;
		if (t - hushAt < 60) return 0;
		float y = 0;
		if (HOP[i] > 0) y = Math.max(y, 0.35f * Math.abs(Mth.sin((HOP[i] - pt) * 0.55f)));
		float w = t - wonAt - i * 1.4f;
		if (w > 0 && w < 12) y = Math.max(y, 0.7f * Mth.sin(w / 12f * Mth.PI));
		float rl = t - rulerAt;
		if (rl > 0 && rl < 60) y = Math.max(y, 0.3f * Math.abs(Mth.sin(rl * 0.45f + i)));
		return y;
	}

	@SubscribeEvent
	static void draw(RenderLevelStageEvent e) {
		if (e.getStage() != RenderLevelStageEvent.Stage.AFTER_ENTITIES || failed) return;
		var mc = Minecraft.getInstance();
		if (mc.level == null || mc.level.dimension() != Arena.RING) return;
		if (mesh == null) build();
		if (mesh == null) return;
		Vec3 cam = e.getCamera().getPosition();
		float pt = e.getPartialTick().getGameTimeDeltaPartialTick(false);
		RenderType type = Types.CROWD;
		type.setupRenderState();
		ShaderInstance sh = RenderSystem.getShader();
		if (sh != null) {
			for (int slot = 0; slot < ArenaShape.SLOTS; slot++) {
				BlockPos o = ArenaShape.origin(slot);
				if (Math.abs(o.getX() - cam.x) > 300) continue;
				for (int i = 0; i < SECTIONS; i++) {
					if (mesh[i] == null) continue;
					Matrix4f mv = new Matrix4f(e.getModelViewMatrix()).translate((float) (o.getX() - cam.x), (float) (o.getY() - cam.y + lift(i, pt)), (float) (o.getZ() - cam.z));
					mesh[i].bind();
					mesh[i].drawWithShader(mv, e.getProjectionMatrix(), sh);
				}
			}
			VertexBuffer.unbind();
		}
		type.clearRenderState();
	}

	// ---------------------------------------------------------------- the townsfolk's meshes

	/** One of the cast: their triangles (x y z u v nx ny nz, the game's frame, standing), which limb each is on, how big. */
	private record Look(float[] tris, byte[] limb, float scale, float armX, float rLegX, float lLegX) {}

	private static final byte HEAD = 0, BODY = 1, R_ARM = 2, L_ARM = 3, R_LEG = 4, L_LEG = 5;
	private static final Map<String, Byte> LIMBS = Map.ofEntries(Map.entry("head", HEAD), Map.entry("hat", HEAD), Map.entry("torso", BODY),
			Map.entry("jacket", BODY), Map.entry("rightArm", R_ARM), Map.entry("rightSleeve", R_ARM), Map.entry("leftArm", L_ARM), Map.entry("leftSleeve", L_ARM),
			Map.entry("rightLeg", R_LEG), Map.entry("rightPants", R_LEG), Map.entry("leftLeg", L_LEG), Map.entry("leftPants", L_LEG));

	/** Who sits in the stands: the townsfolk, the races, the adventurers (not the leads, nor Veyra). */
	private static boolean crowd(String kind) {
		return kind.startsWith("townsfolk_") || kind.startsWith("demon_") || kind.startsWith("dwarf_") || kind.startsWith("elf_") || kind.startsWith("adv");
	}

	private static Look look(String kind, int cell, double scale) throws Exception {
		var rm = Minecraft.getInstance().getResourceManager();
		JsonObject v;
		try (var in = new InputStreamReader(rm.getResourceOrThrow(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "animmodels/entity/npc/" + kind + ".json")).open(),
				StandardCharsets.UTF_8)) {
			v = JsonParser.parseReader(in).getAsJsonObject().getAsJsonObject("vertices");
		}
		float[] pos = floats(v.getAsJsonObject("positions").getAsJsonArray("array")), uv = floats(v.getAsJsonObject("uvs").getAsJsonArray("array")),
				nrm = floats(v.getAsJsonObject("normals").getAsJsonArray("array"));
		float u0 = (cell % COLS) * TW, v0 = (cell / COLS) * TH;
		List<Float> out = new ArrayList<>();
		List<Byte> limbs = new ArrayList<>();
		float armX = 0, rLeg = 0, lLeg = 0;
		int armN = 0, rN = 0, lN = 0;
		for (var part : v.getAsJsonObject("parts").entrySet()) {
			Byte limb = LIMBS.get(part.getKey());
			if (limb == null) continue;
			JsonArray a = part.getValue().getAsJsonObject().getAsJsonArray("array");
			for (int i = 0; i + 8 < a.size(); i += 9) {
				for (int c = 0; c < 3; c++) {
					int pi = a.get(i + c * 3).getAsInt() * 3, ui = a.get(i + c * 3 + 1).getAsInt() * 2, ni = a.get(i + c * 3 + 2).getAsInt() * 3;
					// the mesh is z-up: x, z, -y in the game's frame
					float x = pos[pi], y = pos[pi + 2], z = -pos[pi + 1];
					out.add(x);
					out.add(y);
					out.add(z);
					out.add((u0 + uv[ui] * TW) / (COLS * TW));
					out.add(uv[ui + 1]);           // fixed below, once the sheet's height is known
					out.add(nrm[ni]);
					out.add(nrm[ni + 2]);
					out.add(-nrm[ni + 1]);
					if (limb == R_ARM && y < 1.5f) {
						armX += x;
						armN++;
					}
					if (limb == R_LEG) {
						rLeg += x;
						rN++;
					}
					if (limb == L_LEG) {
						lLeg += x;
						lN++;
					}
				}
				limbs.add(limb);
			}
		}
		float[] t = new float[out.size()];
		for (int i = 0; i < t.length; i++) t[i] = out.get(i);
		// v onto the sheet: this cell's row
		for (int i = 4; i < t.length; i += 8) t[i] = v0 + t[i] * TH;
		byte[] lb = new byte[limbs.size()];
		for (int i = 0; i < lb.length; i++) lb[i] = limbs.get(i);
		return new Look(t, lb, (float) scale, armN == 0 ? -0.35f : armX / armN, rN == 0 ? -0.12f : rLeg / rN, lN == 0 ? 0.12f : lLeg / lN);
	}

	private static float[] floats(JsonArray a) {
		float[] f = new float[a.size()];
		for (int i = 0; i < f.length; i++) f[i] = a.get(i).getAsFloat();
		return f;
	}

	// ---------------------------------------------------------------- baking the stands

	private static void build() {
		try {
			Map<String, Double> scales = NpcLooks.scales();
			List<String> kinds = new ArrayList<>();
			for (String k : scales.keySet()) if (crowd(k)) kinds.add(k);
			kinds.sort(String::compareTo);
			if (kinds.isEmpty()) {
				failed = true;
				return;
			}
			int rows = (kinds.size() + COLS - 1) / COLS;
			NativeImage sheet = new NativeImage(COLS * TW, rows * TH, true);
			List<Look> looks = new ArrayList<>();
			var rm = Minecraft.getInstance().getResourceManager();
			for (String k : kinds) {
				int cell = looks.size();
				try (InputStream in = rm.getResourceOrThrow(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/entity/npc/" + k + ".png")).open();
						NativeImage img = NativeImage.read(in)) {
					int cx = (cell % COLS) * TW, cy = (cell / COLS) * TH;
					for (int y = 0; y < TH; y++)
						for (int x = 0; x < TW; x++) sheet.setPixelRGBA(cx + x, cy + y, img.getPixelRGBA(x * img.getWidth() / TW, y * img.getHeight() / TH));
					looks.add(look(k, cell, scales.getOrDefault(k, 1.0)));
				} catch (Exception ex) {
					Ashbound.LOG.warn("crowd: {} left out ({})", k, ex.toString());
				}
			}
			float sheetH = rows * TH;
			for (Look l : looks) for (int i = 4; i < l.tris().length; i += 8) l.tris()[i] /= sheetH;
			Minecraft.getInstance().getTextureManager().register(SHEET, new DynamicTexture(sheet));

			BufferBuilder[] b = new BufferBuilder[SECTIONS];
			for (int i = 0; i < SECTIONS; i++) b[i] = new BufferBuilder(new ByteBufferBuilder(1 << 20), VertexFormat.Mode.TRIANGLES, DefaultVertexFormat.NEW_ENTITY);
			for (int[] s : ArenaShape.seats()) {
				int h = hash(s[0], s[1], s[2]);
				if ((h & 15) < 3) continue;                       // a few empty seats
				double a = Math.atan2(s[2] + 0.5, s[0] + 0.5);
				int sec = Mth.floor((a + Math.PI) / (Math.PI * 2) * SECTIONS) % SECTIONS;
				Look l = looks.get(Math.floorMod(h >> 4, looks.size()));
				person(b[sec], l, s[0] + 0.5f, s[1], s[2] + 0.5f, h);
			}
			mesh = new VertexBuffer[SECTIONS];
			for (int i = 0; i < SECTIONS; i++) {
				MeshData d = b[i].build();
				if (d == null) continue;
				VertexBuffer vb = new VertexBuffer(VertexBuffer.Usage.STATIC);
				vb.bind();
				vb.upload(d);
				VertexBuffer.unbind();
				mesh[i] = vb;
			}
			Ashbound.LOG.info("The Ring's crowd: {} of the cast on the stands", looks.size());
		} catch (Exception ex) {
			Ashbound.LOG.error("The Ring's crowd failed to build", ex);
			failed = true;
		}
	}

	private static int hash(int x, int y, int z) {
		int h = x * 73856093 ^ y * 19349663 ^ z * 83492791;
		h ^= h >>> 13;
		h *= 0x5bd1e995;
		return h ^ (h >>> 15);
	}

	/** One of them on their seat (x, y, z the seat's top middle), facing the middle of the sand: sat (legs forward over
	 *  the step), on their feet, now and then with an arm thrown up. */
	private static void person(BufferBuilder b, Look l, float x, float y, float z, int h) {
		boolean standing = ((h >> 12) & 7) < 2, cheering = ((h >> 15) & 7) < 2;
		float yaw = (float) Math.atan2(-x, -z);          // +z turned toward the middle
		Matrix3f turn = new Matrix3f().rotationY(yaw);
		Matrix3f legs = new Matrix3f().rotationX(-Mth.HALF_PI), arm = new Matrix3f().rotationX(-160 * Mth.DEG_TO_RAD);
		float k = l.scale(), drop = standing ? 0 : -0.68f, back = standing ? 0 : -0.15f;
		Vector3f p = new Vector3f(), n = new Vector3f();
		float[] t = l.tris();
		for (int tri = 0; tri < l.limb().length; tri++) {
			byte limb = l.limb()[tri];
			for (int c = 0; c < 3; c++) {
				int i = (tri * 3 + c) * 8;
				p.set(t[i], t[i + 1], t[i + 2]);
				n.set(t[i + 5], t[i + 6], t[i + 7]);
				if (!standing && (limb == R_LEG || limb == L_LEG)) {
					float px = limb == R_LEG ? l.rLegX() : l.lLegX();
					p.sub(px, 0.75f, 0).mul(legs).add(px, 0.75f, 0);
					n.mul(legs);
				}
				if (cheering && limb == R_ARM) {
					p.sub(l.armX(), 1.375f, 0).mul(arm).add(l.armX(), 1.375f, 0);
					n.mul(arm);
				}
				p.add(0, drop, back).mul(k).mul(turn);
				n.mul(turn);
				b.addVertex(x + p.x, y + p.y, z + p.z).setColor(0xFFC8C8D2).setUv(t[i + 3], t[i + 4]).setOverlay(OverlayTexture.NO_OVERLAY).setLight(0xF000F0)
						.setNormal(n.x, n.y, n.z);
			}
		}
	}
}
