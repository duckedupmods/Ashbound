package com.snoringwalrus.ashbound.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.Thrall;

import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import org.joml.Matrix3f;
import org.joml.Matrix4f;
import org.joml.Quaternionf;

/**
 * A thrall from tools/voxthralls.py, posed here like the mounts are. It has no legs to walk on: it hangs in the air and
 * bobs, leans into its movement, its fire streams back, and its blade arm draws up and comes down on each blow. The
 * flame is grey in the texture and takes the colour of the staff that called it.
 */
public class ThrallRender extends EntityRenderer<Thrall> {
	private static final float REVENANT = 0.68f, CHAMPION = 0.92f, HOVER = 0.25f, BOB = 0.1f, LEAN = 0.5f;

	public ThrallRender(EntityRendererProvider.Context ctx) {
		super(ctx);
		shadowRadius = 0.7f;
	}

	private static String id(Thrall e) {
		return e.champion ? "champion" : "revenant";
	}

	@Override
	public ResourceLocation getTextureLocation(Thrall e) {
		return ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "textures/entity/mount_" + id(e) + ".png");
	}

	/** Up, back and down: how far through a blow its arm is. */
	private static float blow(float a) {
		return a < 0.35f ? -Mth.sin(a / 0.35f * Mth.HALF_PI) * 1.5f : -1.5f + 2.4f * Mth.sin((a - 0.35f) / 0.65f * Mth.HALF_PI);
	}

	private static void turn(String name, Quaternionf q, float t, float speed, float swing, float headYaw) {
		if (name.equals("torso")) q.rotateX(speed * LEAN + Mth.sin(t * 0.09f) * 0.04f + swing * 0.12f).rotateY(swing * -0.3f);
		else if (name.equals("head")) q.rotateY(headYaw).rotateX(-speed * LEAN * 0.8f);
		else if (name.equals("arm_r")) q.rotateX(swing);
		else if (name.equals("fore_r")) q.rotateX(swing * 0.5f + Mth.sin(t * 0.07f) * 0.06f);
		else if (name.equals("arm_l")) q.rotateX(swing * 0.7f - speed * 0.4f + Mth.sin(t * 0.08f + 1) * 0.08f);
	}

	@Override
	public void render(Thrall e, float yaw, float pt, PoseStack ps, MultiBufferSource buf, int light) {
		MountRender.Model m = MountRender.model(id(e));
		float t = e.tickCount + pt, body = Mth.rotLerp(pt, e.yBodyRotO, e.yBodyRot), speed = Math.min(1, e.walkAnimation.speed(pt) * 1.4f);
		float swing = blow(e.getAttackAnim(pt)), headYaw = Mth.wrapDegrees(Mth.rotLerp(pt, e.yHeadRotO, e.yHeadRot) - body) * Mth.DEG_TO_RAD;
		float k = (e.champion ? CHAMPION : REVENANT) * e.getScale();
		ps.pushPose();
		ps.translate(0, HOVER + Mth.sin(t * 0.1f) * BOB, 0);
		ps.mulPose(Axis.YP.rotationDegrees(-body));
		ps.scale(k, k, k);
		Matrix4f[] world = new Matrix4f[m.bones().size()];
		Quaternionf q = new Quaternionf();
		for (int i = 0; i < world.length; i++) {
			MountRender.Bone b = m.bones().get(i);
			q.identity();
			turn(b.name(), q, t, speed, e.getAttackAnim(pt) > 0 ? swing : 0, headYaw);
			Matrix4f at = b.parent() < 0 ? new Matrix4f() : new Matrix4f(world[b.parent()]);
			world[i] = at.translate(b.px(), b.py(), b.pz()).rotate(q).translate(-b.px(), -b.py(), -b.pz());
		}
		int frame = (int) (t / 20 * MountRender.FPS) % m.frames(), tint = e.tint();
		float shift = (float) frame / m.frames();
		VertexConsumer lit = buf.getBuffer(RenderType.entityCutoutNoCull(getTextureLocation(e)));
		for (int i = 0; i < world.length; i++) {
			MountRender.Bone b = m.bones().get(i);
			ps.pushPose();
			ps.last().pose().mul(world[i]);
			ps.last().normal().mul(new Matrix3f(world[i]));
			MountRender.quads(lit, ps.last(), b.lit(), 0, light, 0, 0, 0xFFFFFF);
			MountRender.quads(lit, ps.last(), b.glow(), 0, LightTexture.FULL_BRIGHT, 0, 0, tint);
			MountRender.quads(lit, ps.last(), b.flame(), shift, LightTexture.FULL_BRIGHT, t, 0.012f, tint);
			ps.popPose();
		}
		ps.popPose();
		super.render(e, yaw, pt, ps, buf, light);
	}
}
