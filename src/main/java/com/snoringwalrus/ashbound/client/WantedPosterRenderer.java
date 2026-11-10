package com.snoringwalrus.ashbound.client;

import org.joml.Matrix4f;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.WantedPoster;

import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;

/**
 * A wanted poster (WantedPoster, tools/posters.py's art): the Legend's poster for its rank flat against its wall, and the
 * SLAIN stamp over it once it's dead.
 */
public class WantedPosterRenderer extends EntityRenderer<WantedPoster> {
	private static final String RANKS = "fedcbas";
	private static final ResourceLocation SLAIN = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/entity/wanted/slain.png");
	static final ResourceLocation TORN = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/entity/wanted/torn.png");

	/** You've taken this one: you tore it down, so you see only the scrap left on its nail. */
	static boolean torn(int bounty) {
		String key = "fav:@legend:" + bounty;
		for (com.snoringwalrus.ashbound.Errands.View v : com.snoringwalrus.ashbound.Errands.client)
			if (v.key().equals(key)) return true;
		return WantedScreen.tornNow == bounty;
	}

	public WantedPosterRenderer(EntityRendererProvider.Context ctx) {
		super(ctx);
		shadowRadius = 0;
	}

	@Override
	public ResourceLocation getTextureLocation(WantedPoster p) {
		int r = Math.max(0, Math.min(RANKS.length() - 1, p.rank()));
		return ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/entity/wanted/" + p.legend() + "_" + RANKS.charAt(r) + ".png");
	}

	@Override
	public void render(WantedPoster p, float yaw, float dt, PoseStack ps, MultiBufferSource buf, int light) {
		ps.pushPose();
		ps.mulPose(Axis.YP.rotationDegrees(-p.getYRot()));
		float s = p.scale(), w = WantedPoster.WIDE * s / 2, h = WantedPoster.TALL * s / 2;
		boolean torn = !p.slain() && torn(p.bountyId());
		quad(ps, buf.getBuffer(RenderType.entityCutoutNoCull(torn ? TORN : getTextureLocation(p))), w, h, 0.002f, light);
		if (p.slain()) quad(ps, buf.getBuffer(RenderType.entityCutoutNoCull(SLAIN)), w, h, 0.006f, light);
		ps.popPose();
		super.render(p, yaw, dt, ps, buf, light);
	}

	/** The paper, facing +z (out of the wall once turned), a hair proud of it. */
	private static void quad(PoseStack ps, VertexConsumer vc, float w, float h, float z, int light) {
		Matrix4f m = ps.last().pose();
		var pose = ps.last();
		vc.addVertex(m, -w, -h, z).setColor(255, 255, 255, 255).setUv(0, 1).setOverlay(OverlayTexture.NO_OVERLAY).setLight(light).setNormal(pose, 0, 0, 1);
		vc.addVertex(m, w, -h, z).setColor(255, 255, 255, 255).setUv(1, 1).setOverlay(OverlayTexture.NO_OVERLAY).setLight(light).setNormal(pose, 0, 0, 1);
		vc.addVertex(m, w, h, z).setColor(255, 255, 255, 255).setUv(1, 0).setOverlay(OverlayTexture.NO_OVERLAY).setLight(light).setNormal(pose, 0, 0, 1);
		vc.addVertex(m, -w, h, z).setColor(255, 255, 255, 255).setUv(0, 0).setOverlay(OverlayTexture.NO_OVERLAY).setLight(light).setNormal(pose, 0, 0, 1);
	}

	@Override
	protected boolean shouldShowName(WantedPoster p) {
		return false;
	}
}
