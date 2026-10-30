package com.snoringwalrus.ashbound.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.Curios;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.client.resources.model.BakedModel;
import net.minecraft.client.resources.model.ModelResourceLocation;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.client.event.ModelEvent;
import net.neoforged.bus.api.IEventBus;
import top.theillusivec4.curios.api.CuriosApi;
import yesman.epicfight.api.animation.Joint;
import yesman.epicfight.api.client.event.EpicFightClientEventHooks;
import yesman.epicfight.api.utils.math.MathUtils;
import yesman.epicfight.api.utils.math.OpenMatrix4f;
import yesman.epicfight.client.renderer.patched.entity.PatchedLivingEntityRenderer;
import yesman.epicfight.client.renderer.patched.layer.PatchedLayer;
import yesman.epicfight.world.capabilities.entitypatch.LivingEntityPatch;

/**
 * Worn curios drawn on the body, riding Epic Fight's joints (players always have its body, AshboundClient), placed as in
 * the concept (tools/blender/curio_worn.py, tools/curios.py --worn): the amulet's chain laid on the chest and running
 * under the head, a ring round each fist, the charm strapped to the outside of the right thigh and the relic the left (on
 * the legs, so the legs never swing through them). Curios' own layer is never drawn under Epic Fight, so this replaces it; its per-slot eye toggle still hides one.
 * <p>
 * Placement is in Minecraft pixels on the bind pose (x the body's left, y up from the feet, z out of the chest). Joint
 * frames (Epic Fight's biped): Chest has +Y up, the front at -Z and +X the body's right, so it is the concept's frame
 * turned 180 about Y; the hands and thighs have +Y down the limb and the front at +Z, the concept turned 180 about Z.
 * Our meshes are in pixels too (voxsword.to_item: x and z centred on 0.5, model y 0.8 at item y 6.25/16).
 */
public final class WornCurios extends PatchedLayer<LivingEntity, LivingEntityPatch<LivingEntity>, EntityModel<LivingEntity>,
		RenderLayer<LivingEntity, EntityModel<LivingEntity>>> {

	/** joint heights on the bind pose, in pixels (biped.json: Root and the thighs 0.764, Chest 1.114, the hands 1.094) */
	private static final float HIP_Y = 12.22f, CHEST_Y = 17.82f, HAND_Y = 17.5f;
	/** where the bail of a worn amulet sits (and its chain's 4 px climb to the collar, curios.py COLLAR_DROP) */
	private static final float BAIL_Y = 20f, CHEST_FRONT = 2.35f;
	/** model pixels after the item renderer's -0.5 shift: x and z already centred, y 2.55 px low */
	private static final float ITEM_Y = (0.5f - 6.25f / 16) * 16 + 0.8f;

	public static void hooks(IEventBus bus) {
		bus.addListener((ModelEvent.RegisterAdditional e) -> {
			for (Curios.Spec s : Curios.SPECS) if (!s.worn().model().equals(s.id())) e.register(model(s));
		});
		register();
	}

	@SuppressWarnings({"rawtypes", "unchecked"})
	private static void register() {
		EpicFightClientEventHooks.Registry.MODIFY_PATCHED_ENTITY.registerEvent(e -> {
			if (e.get(EntityType.PLAYER) instanceof PatchedLivingEntityRenderer r) r.addCustomLayer((PatchedLayer) new WornCurios());
		});
	}

	private static ModelResourceLocation model(Curios.Spec s) {
		return ModelResourceLocation.standalone(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "item/" + s.worn().model()));
	}

	@Override
	protected void renderLayer(LivingEntityPatch<LivingEntity> patch, LivingEntity entity, RenderLayer<LivingEntity, EntityModel<LivingEntity>> layer,
			PoseStack pose, MultiBufferSource buffers, int light, OpenMatrix4f[] poses, float bob, float yRot, float xRot, float partial) {
		if (entity.isInvisible()) return;
		CuriosApi.getCuriosInventory(entity).ifPresent(inv -> inv.getCurios().forEach((slot, h) -> {
			var stacks = h.getStacks();
			for (int i = 0; i < stacks.getSlots(); i++) {
				ItemStack s = stacks.getStackInSlot(i);
				if (s.isEmpty() || !(s.getItem() instanceof Curios.Curio c) || i < h.getRenders().size() && !h.getRenders().get(i)) continue;
				String joint = switch (slot) {
					case "necklace" -> "Chest";
					case "charm" -> "Thigh_R";
					case "relic" -> "Thigh_L";
					case "ring" -> i == 0 ? "Hand_R" : i == 1 ? "Hand_L" : null;
					default -> null;
				};
				if (joint == null) continue;
				Joint j = patch.getArmature().searchJointByName(joint);
				if (j == null || j.getId() >= poses.length) continue;
				pose.pushPose();
				MathUtils.mulStack(pose, poses[j.getId()]);
				pose.scale(1 / 16f, 1 / 16f, 1 / 16f);
				place(slot, c.spec().worn(), pose);
				pose.translate(0, ITEM_Y, 0);
				pose.scale(16, 16, 16);
				var items = Minecraft.getInstance().getItemRenderer();
				if (slot.equals("necklace")) {
					BakedModel m = Minecraft.getInstance().getModelManager().getModel(model(c.spec()));
					items.render(s, ItemDisplayContext.NONE, false, pose, buffers, light, OverlayTexture.NO_OVERLAY, m);
				} else items.renderStatic(entity, s, ItemDisplayContext.NONE, false, pose, buffers, entity.level(), light, OverlayTexture.NO_OVERLAY, entity.getId());
				pose.popPose();
			}
		}));
	}

	/** from the joint into the piece's own pixels: the concept's placement (curio_worn.py), slot by slot */
	private static void place(String slot, Curios.Worn w, PoseStack pose) {
		float k = w.scale();
		switch (slot) {
			case "necklace" -> {          // the bail on the upper chest, the chain up to the collar
				pose.mulPose(Axis.YP.rotationDegrees(180));
				pose.translate(0, BAIL_Y - CHEST_Y, CHEST_FRONT);
				pose.scale(k, k, k);
				return;
			}
			case "ring" -> {              // round the fist, the setting to the front
				pose.mulPose(Axis.ZP.rotationDegrees(180));
				pose.translate(0, 12.9f - HAND_Y, 0);
				pose.mulPose(Axis.XP.rotationDegrees(90));
				pose.scale(k, k, k);
				return;
			}
			case "charm" -> {             // strapped to the outside of the right thigh, facing out: it swings with the leg
				pose.mulPose(Axis.ZP.rotationDegrees(180));
				pose.translate(-2f - w.depth() * k / 2 - 0.1f, 11.8f - HIP_Y, 0);
				pose.mulPose(Axis.YP.rotationDegrees(-90));
			}
			default -> {                  // the relic on the outside of the left thigh, facing out
				pose.mulPose(Axis.ZP.rotationDegrees(180));
				pose.translate(2f + w.depth() * k / 2 + 0.1f, 11.6f - HIP_Y, 0);
				pose.mulPose(Axis.YP.rotationDegrees(90));
			}
		}
		pose.scale(k, k, k);
		pose.translate(-w.topX(), -w.topY(), -w.topZ());
	}
}
