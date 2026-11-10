package com.snoringwalrus.ashbound.client;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.joml.Matrix4f;

import com.google.gson.JsonElement;
import com.google.gson.JsonParser;
import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.Lairs;

import net.minecraft.client.Minecraft;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.phys.Vec3;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.RenderLevelStageEvent;

/**
 * The intro's quick run through a whole dungeon while Hob talks (IntroScene): the dungeon's blocks, meshed in the
 * background when the telling starts (BlockMesh), hung at the top of the sky over the wagon where nothing else is, and drawn
 * with the world; its monsters stand at their spots, only on this screen; the camera flies the walkable route from its
 * arrival hall to its boss that tools/dungeon_run.py found (data/ashbound/lair/NAME_run.json).
 */
@EventBusSubscriber(modid = Ashbound.ID, value = Dist.CLIENT)
public final class DungeonRun {
	private DungeonRun() {}

	public static final String LAIR = "gate_cellar";
	/** How far ahead along the route the camera looks, in blocks; the run's two cuts: so many blocks of its first halls, then
	 *  the last stretch up to the boss, stopping this short of him (a 290-block route in eleven seconds was a blur). */
	private static final int AHEAD = 7, FIRST = 50, LAST = 30, SHORT = 9;
	/** the boss, spawned before the rest so the cap on monsters never leaves him out; the camera ends on him */
	private static LivingEntity boss;

	private static BlockMesh mesh;
	private static final List<Vec3> PATH = new ArrayList<>();
	private static final List<Entity> MOBS = new ArrayList<>();
	private static Vec3 origin = Vec3.ZERO;
	private static boolean showing;

	/** At the start of the telling: the dungeon meshed in the background, placed high over `near`. */
	public static void prepare(Vec3 near) {
		close();
		Minecraft mc = Minecraft.getInstance();
		if (mc.level == null || Lairs.points(LAIR).get("tp") == null) return;
		PATH.clear();
		try (InputStream in = DungeonRun.class.getResourceAsStream("/data/ashbound/lair/" + LAIR + "_run.json")) {
			if (in == null) return;
			for (JsonElement p : JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject().getAsJsonArray("path")) {
				var a = p.getAsJsonArray();
				PATH.add(new Vec3(a.get(0).getAsDouble(), a.get(1).getAsDouble(), a.get(2).getAsDouble()));
			}
		} catch (Exception e) {
			Ashbound.LOG.error("No route for the intro's dungeon run", e);
			return;
		}
		BlockMesh.Blocks b = new BlockMesh.Blocks();
		int[] ys = {Integer.MAX_VALUE, Integer.MIN_VALUE};
		Lairs.blocks(LAIR, (x, y, z, st) -> {
			b.put(x, y, z, st);
			ys[0] = Math.min(ys[0], y);
			ys[1] = Math.max(ys[1], y);
		});
		b.flood();
		mesh = BlockMesh.of(b, 0);
		// as high as the world goes: forty blocks over the wagon, the big trees of the wood grew into its halls
		int top = mc.level.getMaxBuildHeight() - 4 - ys[1];
		origin = new Vec3(Mth.floor(near.x), top, Mth.floor(near.z));
	}

	public static boolean ready() {
		return mesh != null && mesh.ready() && PATH.size() > 1;
	}

	/** The run starts: its monsters step in. */
	public static void begin() {
		Minecraft mc = Minecraft.getInstance();
		if (!ready() || mc.level == null) return;
		showing = true;
		int id = -900000;
		List<Map.Entry<String, Vec3>> spots = new ArrayList<>(Lairs.points(LAIR).entrySet());
		spots.sort((a, b) -> Boolean.compare(!a.getKey().equals("boss"), !b.getKey().equals("boss")));
		for (Map.Entry<String, Vec3> e : spots) {
			String k = e.getKey();
			ResourceLocation type = null;
			if (k.startsWith("mob:")) {
				String[] p = k.split(":");
				if (p.length >= 3) type = ResourceLocation.tryBuild(p[1], p[2]);
			} else if (k.equals("boss")) {
				type = Lairs.boss(LAIR);
			}
			if (type == null || MOBS.size() >= 70) continue;
			var t = BuiltInRegistries.ENTITY_TYPE.getOptional(type);
			if (t.isEmpty() || !(t.get().create(mc.level) instanceof LivingEntity m)) continue;
			Vec3 at = origin.add(e.getValue());
			m.setId(id--);
			m.moveTo(at.x, at.y, at.z, 0, 0);                     // facing south: up the route, toward the camera
			m.setYHeadRot(0);
			m.setYBodyRot(0);
			if (m instanceof Mob mob) mob.setNoAi(true);
			mc.level.addEntity(m);
			MOBS.add(m);
			if (k.equals("boss")) boss = m;
		}
	}

	/** The run's over: its monsters go (the blocks stay meshed till close). */
	public static void end() {
		showing = false;
		Minecraft mc = Minecraft.getInstance();
		if (mc.level != null) for (Entity m : MOBS) mc.level.removeEntity(m.getId(), Entity.RemovalReason.DISCARDED);
		MOBS.clear();
		boss = null;
	}

	public static void close() {
		end();
		if (mesh != null) mesh.close();
		mesh = null;
	}

	/** The run's cuts: its first halls (k 0..1), or the last stretch to its boss. */
	public static Vec3 cut(boolean last, float k) {
		return origin.add(along(index(last, k)));
	}

	/** Where the camera looks in a cut: ahead along the route, and at the end of the last, up at the boss. */
	public static Vec3 cutLook(boolean last, float k) {
		int n = PATH.size() - 1;
		Vec3 ahead = origin.add(along(Math.min(index(last, k) + AHEAD, n))).add(0, -0.5, 0);
		if (!last) return ahead;
		Vec3 at = boss != null ? boss.position().add(0, boss.getBbHeight() * 0.6, 0) : Lairs.points(LAIR).get("boss") == null ? null : origin.add(Lairs.points(LAIR).get("boss")).add(0, 2.2, 0);
		return at == null ? ahead : ahead.lerp(at, Mth.clamp(k * 1.6f - 0.15f, 0, 1));
	}

	private static float index(boolean last, float k) {
		int n = PATH.size() - 1;
		if (!last) return k * Math.min(FIRST, n * 0.4f);
		float from = Math.max(0, n - LAST), to = Math.max(from, n - SHORT);
		return Mth.lerp(k, from, to);
	}

	private static Vec3 along(float i) {
		int a = Mth.clamp(Mth.floor(i), 0, PATH.size() - 1), b = Math.min(a + 1, PATH.size() - 1);
		return PATH.get(a).lerp(PATH.get(b), Mth.clamp(i - a, 0, 1));
	}

	@SubscribeEvent
	static void draw(RenderLevelStageEvent e) {
		if (!showing || mesh == null) return;
		boolean solid = e.getStage() == RenderLevelStageEvent.Stage.AFTER_CUTOUT_BLOCKS;
		boolean clear = e.getStage() == RenderLevelStageEvent.Stage.AFTER_TRANSLUCENT_BLOCKS;
		if (!solid && !clear) return;
		Vec3 cam = e.getCamera().getPosition();
		Matrix4f mv = new Matrix4f(e.getModelViewMatrix()).translate((float) (origin.x - cam.x), (float) (origin.y - cam.y), (float) (origin.z - cam.z));
		mesh.draw(mv, e.getProjectionMatrix(), solid, clear);
	}
}
