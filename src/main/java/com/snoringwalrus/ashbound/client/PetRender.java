package com.snoringwalrus.ashbound.client;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import com.snoringwalrus.ashbound.Bag;
import com.snoringwalrus.ashbound.Curios;
import com.snoringwalrus.ashbound.Pets;
import com.snoringwalrus.ashbound.Rations;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.BlockEntityWithoutLevelRenderer;
import net.minecraft.client.renderer.LevelRenderer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.core.BlockPos;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.client.event.ClientPlayerNetworkEvent;
import net.neoforged.neoforge.client.event.RenderLevelStageEvent;
import net.neoforged.neoforge.client.extensions.common.IClientItemExtensions;
import net.neoforged.neoforge.common.NeoForge;

/**
 * Pets, drawn on each client with no entity behind them (Pets). Each keeps its own place here: it's carried along with its owner
 * and chases a spot beside them a frame at a time, so it swings out on a turn but stays with you at a sprint; it just reappears if
 * you've got too far ahead. Heel pets wait out a ride.
 */
public final class PetRender {
	private PetRender() {}

	/** where a heel pet walks and a hover pet floats, from the owner: to the left, up, behind */
	private static final double HEEL_SIDE = 0.75, HEEL_BACK = 0.65, HOVER_SIDE = 0.8, HOVER_UP = 1.8, HOVER_BACK = 0.15;
	/** how quickly it closes on that spot (a share of the gap a second), how much of the owner's own move it shares, how far before it gives up and reappears */
	private static final double CHASE = 6, CARRY = 0.85, TOO_FAR = 20;
	private static final int GROUND_UP = 2, GROUND_DOWN = 5;
	private static final float STRIDE = 0.8f;
	private static final Map<UUID, Follow> AT = new HashMap<>();
	/** the Bag's pouch, built with the pets (tools/voxpets.py --bag) */
	private static final String BAG = "bottomless_bag";
	private static final float[] BAG_BOX = {0.0f, 0.359f, 0.003f, 0.719f};
	/** the Ration Pouch's, the same way (--rations) */
	private static final String RATIONS = "ration_pouch";
	private static final float[] RATIONS_BOX = {0.003f, 0.35f, 0.02f, 0.712f};

	private static final class Follow {
		double x, y, z, ownerX, ownerZ;
		float yaw, stride, pace;
		long last = System.nanoTime();
	}

	public static void hooks() {
		NeoForge.EVENT_BUS.addListener(PetRender::draw);
		NeoForge.EVENT_BUS.addListener((ClientPlayerNetworkEvent.LoggingOut e) -> AT.clear());
	}

	private static double ground(Level level, double x, double y, double z) {
		int top = Mth.floor(y) + GROUND_UP;
		BlockPos.MutableBlockPos at = new BlockPos.MutableBlockPos();
		for (int by = top; by > top - GROUND_UP - GROUND_DOWN; by--) {
			at.set(Mth.floor(x), by, Mth.floor(z));
			var shape = level.getBlockState(at).getCollisionShape(level, at);
			if (!shape.isEmpty()) return by + shape.max(net.minecraft.core.Direction.Axis.Y);
		}
		return y;
	}

	private static void draw(RenderLevelStageEvent e) {
		if (e.getStage() != RenderLevelStageEvent.Stage.AFTER_ENTITIES) return;
		Minecraft mc = Minecraft.getInstance();
		if (mc.level == null) return;
		float pt = e.getPartialTick().getGameTimeDeltaPartialTick(false), t = mc.level.getGameTime() + pt;
		MultiBufferSource.BufferSource buf = mc.renderBuffers().bufferSource();
		PoseStack ps = e.getPoseStack();
		Vec3 cam = e.getCamera().getPosition();
		boolean any = false;
		for (Player p : mc.level.players()) {
			Pets.Pet pet = p.isInvisible() || p.isSpectator() ? null : Pets.worn(p);
			boolean heel = pet != null && pet.where() == Pets.Where.HEEL;
			if (pet == null || heel && p.isPassenger()) {
				AT.remove(p.getUUID());
				continue;
			}
			Follow f = step(mc.level, p, heel, pt, t);
			ps.pushPose();
			ps.translate(f.x - cam.x, f.y - cam.y, f.z - cam.z);
			ps.mulPose(Axis.YP.rotationDegrees(-f.yaw));
			ps.scale(pet.size(), pet.size(), pet.size());
			int light = LevelRenderer.getLightColor(mc.level, BlockPos.containing(f.x, f.y + 0.3, f.z));
			MountRender.pet(pet.id(), t, f.stride, f.pace, !heel, 0, ps, buf, light);
			ps.popPose();
			any = true;
		}
		if (any) buf.endBatch();
		AT.keySet().removeIf(u -> mc.level.getPlayerByUUID(u) == null);
	}

	private static Follow step(Level level, Player p, boolean heel, float pt, float t) {
		Vec3 at = p.getPosition(pt);
		float body = Mth.rotLerp(pt, p.yBodyRotO, p.yBodyRot);
		Vec3 spot = (heel ? new Vec3(HEEL_SIDE, 0, -HEEL_BACK) : new Vec3(HOVER_SIDE, HOVER_UP + Mth.sin(t * 0.07f) * 0.1f, -HOVER_BACK)).yRot(-body * Mth.DEG_TO_RAD).add(at);
		if (heel) spot = new Vec3(spot.x, ground(level, spot.x, at.y, spot.z), spot.z);
		Follow f = AT.get(p.getUUID());
		long now = System.nanoTime();
		if (f == null || Math.abs(f.x - spot.x) + Math.abs(f.y - spot.y) + Math.abs(f.z - spot.z) > TOO_FAR) {
			f = new Follow();
			f.x = spot.x;
			f.y = spot.y;
			f.z = spot.z;
			f.yaw = body;
			f.last = now;
			f.ownerX = at.x;
			f.ownerZ = at.z;
			AT.put(p.getUUID(), f);
			return f;
		}
		float dt = Math.min(0.1f, (now - f.last) / 1.0E9f);
		f.last = now;
		float k = 1 - (float) Math.exp(-CHASE * dt);
		double carryX = (at.x - f.ownerX) * CARRY, carryZ = (at.z - f.ownerZ) * CARRY;
		f.ownerX = at.x;
		f.ownerZ = at.z;
		double dx = carryX + (spot.x - f.x - carryX) * k, dz = carryZ + (spot.z - f.z - carryZ) * k, moved = Math.hypot(dx, dz);
		f.x += dx;
		f.z += dz;
		f.y += (spot.y - f.y) * Math.min(1, k * 2);
		f.stride += (float) moved / STRIDE;
		float speed = dt > 0 ? (float) moved / dt : 0;
		f.pace += (Math.min(1, speed / 2) - f.pace) * Math.min(1, dt * 8);
		float want = speed > 0.3f ? (float) (Mth.atan2(-dx, dz) * Mth.RAD_TO_DEG) : body;
		f.yaw = Mth.rotLerp(Math.min(1, dt * 7), f.yaw, want);
		return f;
	}

	/** The real pet in an inventory slot, in the hand, on the ground. */
	public static IClientItemExtensions items() {
		return new IClientItemExtensions() {
			private BlockEntityWithoutLevelRenderer icon;

			@Override
			public BlockEntityWithoutLevelRenderer getCustomRenderer() {
				if (icon == null) icon = new BlockEntityWithoutLevelRenderer(Minecraft.getInstance().getBlockEntityRenderDispatcher(), Minecraft.getInstance().getEntityModels()) {
					@Override
					public void renderByItem(ItemStack stack, ItemDisplayContext ctx, PoseStack ps, MultiBufferSource buf, int light, int overlay) {
						Pets.Pet pet = stack.getItem() instanceof Curios.Curio c ? Pets.ALL.get(c.spec().id()) : null;
						boolean rations = stack.is(Rations.POUCH.get());
						if (pet == null && !rations && !stack.is(Bag.POUCH.get())) return;
						float[] b = rations ? RATIONS_BOX : pet == null ? BAG_BOX : pet.box();
						float k = 0.92f / b[3];
						ps.pushPose();
						ps.translate(0.5, 0.5, 0.5);
						ps.scale(k, k, k);
						ps.translate(-b[0], -b[1], -b[2]);
						float t = Minecraft.getInstance().level == null ? 0 : Minecraft.getInstance().level.getGameTime();
						MountRender.pet(rations ? RATIONS : pet == null ? BAG : pet.id(), t, 0, 0, false, 0, ps, buf, light);
						ps.popPose();
					}
				};
				return icon;
			}
		};
	}
}
