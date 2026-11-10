package com.snoringwalrus.ashbound.client;

import java.io.InputStreamReader;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.Wagon;

import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;

/**
 * Hob's wagon and Bramble from tools/mcstyle_props.py --install (assets cubes/hob_wagon.json and cubes/bramble.json: parts
 * of quads, each part turning about its own pivot). The wagon stands still; Bramble idles: breathes, shifts his head,
 * now and then drops it to graze, swishes his tail and stamps a fore hoof.
 */
public class WagonRender extends EntityRenderer<Wagon> {
	private record Part(String name, float px, float py, float pz, float[] quads) {}

	private static final Map<String, List<Part>> MODELS = new ConcurrentHashMap<>();
	private static final ResourceLocation WAGON = tex("hob_wagon"), HORSE = tex("bramble");

	public WagonRender(EntityRendererProvider.Context ctx) {
		super(ctx);
		shadowRadius = 1.6f;
	}

	private static ResourceLocation tex(String id) {
		return ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/entity/" + id + ".png");
	}

	private static List<Part> model(String id) {
		return MODELS.computeIfAbsent(id, k -> {
			ResourceLocation at = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "cubes/" + id + ".json");
			List<Part> out = new ArrayList<>();
			try (Reader r = new InputStreamReader(Minecraft.getInstance().getResourceManager().getResourceOrThrow(at).open(), StandardCharsets.UTF_8)) {
				for (var e : JsonParser.parseReader(r).getAsJsonObject().getAsJsonArray("parts")) {
					JsonObject p = e.getAsJsonObject();
					JsonArray pv = p.getAsJsonArray("pivot"), q = p.getAsJsonArray("quads");
					float[] v = new float[q.size()];
					for (int i = 0; i < v.length; i++) v[i] = q.get(i).getAsFloat();
					out.add(new Part(p.get("name").getAsString(), pv.get(0).getAsFloat(), pv.get(1).getAsFloat(), pv.get(2).getAsFloat(), v));
				}
			} catch (java.io.IOException ex) {
				Ashbound.LOG.error("Couldn't read the wagon's model " + at, ex);
			}
			return out;
		});
	}

	@Override
	public ResourceLocation getTextureLocation(Wagon e) {
		return WAGON;
	}

	@Override
	public void render(Wagon e, float yaw, float pt, PoseStack ps, MultiBufferSource buf, int light) {
		ps.pushPose();
		ps.mulPose(Axis.YP.rotationDegrees(-e.getYRot()));
		VertexConsumer w = buf.getBuffer(RenderType.entityCutoutNoCull(WAGON));
		for (Part p : model("hob_wagon")) MountRender.quads(w, ps.last(), p.quads(), 0, light, 0, 0, 0xFFFFFF);
		float t = e.tickCount + pt + (e.getId() * 37 % 400);
		VertexConsumer h = buf.getBuffer(RenderType.entityCutoutNoCull(HORSE));
		ps.translate(0, 0.006f * Mth.sin(t * 0.09f), 0);                       // breathing
		for (Part p : model("bramble")) {
			ps.pushPose();
			ps.translate(p.px(), p.py(), p.pz());
			turn(p.name(), t, ps);
			ps.translate(-p.px(), -p.py(), -p.pz());
			MountRender.quads(h, ps.last(), p.quads(), 0, light, 0, 0, 0xFFFFFF);
			ps.popPose();
		}
		ps.popPose();
		super.render(e, yaw, pt, ps, buf, light);
	}

	/** 0 to 1 and back over [from, to) of a repeating cycle, eased at both ends */
	private static float bump(float t, float cycle, float from, float to) {
		float c = t % cycle;
		if (c < from || c >= to) return 0;
		float k = (c - from) / (to - from);
		return Mth.sin(k * Mth.PI) * Mth.sin(k * Mth.PI);
	}

	private static void turn(String part, float t, PoseStack ps) {
		switch (part) {
			case "neck" -> {
				float graze = bump(t, 420, 240, 380);
				ps.mulPose(Axis.YP.rotationDegrees(6 * Mth.sin(t * 0.031f) * (1 - graze)));
				ps.mulPose(Axis.XP.rotationDegrees(3 * Mth.sin(t * 0.05f) + 30 * graze + 2 * graze * Mth.sin(t * 0.6f)));
			}
			case "tail" -> {
				float flick = bump(t, 150, 100, 124);
				ps.mulPose(Axis.YP.rotationDegrees(10 * Mth.sin(t * 0.11f) + 28 * flick * Mth.sin(t * 0.8f)));
				ps.mulPose(Axis.XP.rotationDegrees(-4 - 10 * flick));
			}
			case "leg_fr" -> ps.mulPose(Axis.XP.rotationDegrees(-32 * bump(t, 290, 60, 78)));
			case "leg_fl" -> ps.mulPose(Axis.XP.rotationDegrees(-26 * bump(t, 530, 410, 426)));
			default -> {}
		}
	}
}
