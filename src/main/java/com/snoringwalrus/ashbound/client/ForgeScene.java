package com.snoringwalrus.ashbound.client;

import java.util.HashMap;
import java.util.Map;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.Gear;
import com.snoringwalrus.ashbound.Npc;
import com.snoringwalrus.ashbound.Net;
import com.snoringwalrus.ashbound.Smithing;
import com.snoringwalrus.ashbound.Vfx;

import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.client.renderer.texture.TextureAtlas;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.client.event.RenderHandEvent;
import net.neoforged.neoforge.client.event.RenderLevelStageEvent;
import net.neoforged.neoforge.client.event.ViewportEvent;
import yesman.epicfight.client.world.capabilites.entitypatch.player.LocalPlayerPatch;
import yesman.epicfight.gameasset.Animations;
import yesman.epicfight.world.capabilities.EpicFightCapabilities;
import yesman.epicfight.world.capabilities.entitypatch.LivingEntityPatch;

/**
 * The stage of the forging (ForgeStrikeScreen is the play): the camera stands to the side so you see both smiths, you
 * hold your tool, the work lies on the anvil as the real piece, metal a glowing lump beaten out into its shape, its
 * colour its heat, cloth taking on the gate's colour. Nothing here touches the server's world: the tool in your hand is
 * only your client's. Anyone else near an anvil sees the same blows from what's passed round (Net.ForgeEcho).
 */
@EventBusSubscriber(modid = Ashbound.ID, value = Dist.CLIENT)
public final class ForgeScene {
	private ForgeScene() {}

	private static boolean on, wasHidden, ghost, cloth, flat, master;
	private static CameraType wasCamera;
	private static BlockPos anvil;
	private static Vec3 centre, forward, right, eye;
	private static float yaw, pitch, faceYaw;
	private static Npc smith;
	private static ItemStack work = ItemStack.EMPTY, saved = ItemStack.EMPTY;
	private static int colour = 0xFFFFFF;
	/** Tools shown in others' hands, and what they really hold. */
	private static final Map<Integer, ItemStack> HELD = new HashMap<>();

	/** the work's look, which the screen sets: its heat (0 cold, 1 white), how far it's beaten out, how high it's lifted, its spin */
	static float heat, shape, lift, spin, dolly;
	/** at the Joining: the second piece, and how far the two have closed on each other */
	static float join;
	private static ItemStack other = ItemStack.EMPTY;
	private static float punch, shake;

	public static boolean on() {
		return on;
	}

	public static Vec3 eye() {
		return eye;
	}

	public static float yaw() {
		return yaw;
	}

	public static float pitch() {
		return pitch;
	}

	static void tint(int rgb) {
		colour = rgb;
	}

	static void show(ItemStack s) {
		work = s;
		flat = s.getItem() instanceof ArmorItem;
	}

	static void second(ItemStack s) {
		other = s;
		join = 0;
	}

	private static ItemStack tool(boolean needle) {
		Item t = needle ? com.snoringwalrus.ashbound.Weapons.TAILOR_NEEDLE.get() : com.snoringwalrus.ashbound.Weapons.SMITH_HAMMER.get();
		return new ItemStack(t);
	}

	/** @param shaped the piece already has its shape (an upgrade)  @param asMaster on the master's side of the anvil */
	static void start(Net.ForgeStart m, ItemStack piece, Smithing.Craft craft, boolean shaped, boolean asMaster) {
		Minecraft mc = Minecraft.getInstance();
		on = true;
		anvil = m.anvil();
		ghost = m.ghost();
		show(piece);
		cloth = craft.cloth;
		master = asMaster;
		faceYaw = m.face();
		float a = faceYaw * Mth.DEG_TO_RAD;
		forward = new Vec3(-Mth.sin(a), 0, Mth.cos(a));
		right = new Vec3(-forward.z, 0, forward.x);
		centre = anvil.getBottomCenter().add(0, ghost ? 1f : m.job().type() == Smithing.FUSE ? 1.12f : 0.95f, 0);   // the Cold Forge's altar stands higher
		smith = mc.level.getEntity(m.smith()) instanceof Npc n ? n : null;
		heat = lift = spin = dolly = punch = shake = 0;
		shape = shaped || flat ? 1 : 0;
		wasCamera = mc.options.getCameraType();
		wasHidden = mc.options.hideGui;
		mc.options.setCameraType(CameraType.THIRD_PERSON_BACK);
		mc.options.hideGui = true;
		Inventory inv = mc.player.getInventory();
		saved = inv.getSelected();
		ItemStack hand = tool(cloth);
		inv.items.set(inv.selected, hand);
		if (smith != null) smith.setItemInHand(InteractionHand.MAIN_HAND, hand.copy());
		frame();
	}

	/** Back to the world: restored before the finished piece arrives, so it's never overwritten by the tool's slot. */
	static void stop() {
		if (!on) return;
		on = false;
		Minecraft mc = Minecraft.getInstance();
		mc.options.setCameraType(wasCamera);
		mc.options.hideGui = wasHidden;
		if (mc.player != null) {
			mc.player.getInventory().items.set(mc.player.getInventory().selected, saved);
			LocalPlayerPatch p = EpicFightCapabilities.getEntityPatch(mc.player, LocalPlayerPatch.class);
			if (p != null) p.getClientAnimator().playAnimation(Animations.BIPED_IDLE, 0f);
		}
		if (smith != null) smith.setItemInHand(InteractionHand.MAIN_HAND, ItemStack.EMPTY);
		smith = null;
		other = ItemStack.EMPTY;
	}

	/** From the side, whichever side has room, close to the work as it nears its end. */
	private static void frame() {
		Minecraft mc = Minecraft.getInstance();
		Vec3 look = centre.add(0, 0.2, 0);
		double best = -1;
		Vec3 at = look;
		for (int s : new int[] {1, -1}) {
			Vec3 to = look.add(right.scale(s * (2.9 - dolly * 1.0))).add(forward.scale(-0.3)).add(0, 0.45 - dolly * 0.15, 0);
			var hit = mc.level.clip(new ClipContext(look, to, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, mc.player));
			double far = hit.getType() == HitResult.Type.MISS ? 99 : hit.getLocation().distanceTo(look);
			if (far > best) {
				best = far;
				at = hit.getType() == HitResult.Type.MISS ? to : look.add(to.subtract(look).normalize().scale(Math.max(0.8, far - 0.3)));
			}
		}
		eye = at;
		Vec3 d = look.subtract(eye).normalize();
		yaw = (float) (Mth.atan2(-d.x, d.z) * Mth.RAD_TO_DEG);
		pitch = (float) (-Math.asin(d.y) * Mth.RAD_TO_DEG);
	}

	// ---------------------------------------------------------------- what happens

	private static void play(Holder<SoundEvent> s, float pitch, float volume) {
		play(s.value(), pitch, volume);
	}

	private static void play(SoundEvent s, float pitch, float volume) {
		Minecraft.getInstance().getSoundManager().play(SimpleSoundInstance.forUI(s, pitch, volume));
	}

	private static void clip(Player who, boolean blow) {
		LivingEntityPatch<?> p = EpicFightCapabilities.getEntityPatch(who, LivingEntityPatch.class);
		if (p != null) p.getClientAnimator().playAnimationInstantly(blow ? Smithing.STRIKE : Smithing.TAP);
	}

	/** The master's tap: small, high, and an arm goes with it (a friend's, if they've taken the master's side). */
	static void tap() {
		tink();
		sparks(3, 0.05f);
		if (master) clip(Minecraft.getInstance().player, false);
		else if (smith != null) {
			LivingEntityPatch<?> p = EpicFightCapabilities.getEntityPatch(smith, LivingEntityPatch.class);
			if (p != null) p.getClientAnimator().playAnimationInstantly(Smithing.TAP);
		}
	}

	private static void tink() {
		if (cloth) play(SoundEvents.WOOL_HIT, 1.6f, 0.5f);
		else play(SoundEvents.ANVIL_USE, 1.9f, 0.32f);
	}

	/** A soft count before the first bar. */
	static void count() {
		play(SoundEvents.ANVIL_USE, 1.4f, 0.14f);
	}

	/** Your blow; how good it was is 0 (off the beat) to 1. */
	static void strike(float how) {
		Minecraft mc = Minecraft.getInstance();
		clip(mc.player, !cloth);
		if (cloth) {
			play(SoundEvents.ARMOR_EQUIP_LEATHER, 1f + how * 0.4f, how > 0 ? 0.8f : 0.3f);
			if (how > 0) sparks((int) (2 + how * 4), 0.05f);
			punch = how;
			return;
		}
		if (how <= 0) {
			play(SoundEvents.ANVIL_LAND, 0.7f, 0.3f);
			sparks(2, 0.08f);
		} else {
			play(SoundEvents.ANVIL_PLACE, 0.9f + how * 0.3f, 0.5f + how * 0.3f);
			play(SoundEvents.ANVIL_USE, 1.1f, 0.4f);
			sparks((int) (8 + how * 22), 0.14f + how * 0.1f);
			punch = 1;
			shake = 0.5f + how * 0.8f;
		}
	}

	static void bellows(float heatNow) {
		Minecraft mc = Minecraft.getInstance();
		if (cloth) {
			play(SoundEvents.BUCKET_FILL, 1.4f, 0.12f);
			return;
		}
		play(SoundEvents.FIRECHARGE_USE, 0.5f + heatNow * 0.7f, 0.22f);
		for (int i = 0; i < 2; i++) mc.level.addParticle(ParticleTypes.LAVA, centre.x, centre.y + 0.1, centre.z, 0, 0, 0);
	}

	/** The finish: a wall of steam, or for cloth the rune flaring. */
	static void quench(float how) {
		Minecraft mc = Minecraft.getInstance();
		if (cloth) {
			play(SoundEvents.ENCHANTMENT_TABLE_USE, 1f, 0.9f);
			for (int i = 0; i < 40; i++) {
				double a = i * 0.7, s = 0.06;
				mc.level.addParticle(ParticleTypes.ENCHANT, centre.x, centre.y + 0.3, centre.z, Math.cos(a) * s * 8, i * 0.04, Math.sin(a) * s * 8);
			}
			return;
		}
		play(SoundEvents.LAVA_EXTINGUISH, 0.8f, 1f);
		play(SoundEvents.FIRE_EXTINGUISH, 0.7f, 0.7f);
		shake = 1.2f;
		for (int i = 0; i < 60; i++) {
			double a = i * 0.7, s = 0.02 + i * 0.002;
			mc.level.addParticle(ParticleTypes.CLOUD, centre.x + Math.cos(a) * 0.3, centre.y, centre.z + Math.sin(a) * 0.3, Math.cos(a) * s, 0.04 + i * 0.002, Math.sin(a) * s);
		}
	}

	/** The finished piece comes up. */
	static void reveal(Smithing.Quality q) {
		play(SoundEvents.PLAYER_LEVELUP, q == Smithing.Quality.PERFECT ? 1.3f : 0.8f, q.ordinal() * 0.2f + 0.2f);
		if (q == Smithing.Quality.PERFECT) play(SoundEvents.BELL_BLOCK, 1f, 0.8f);
		sparks(16 + q.ordinal() * 16, 0.2f);
	}

	/** The Joining's end: a column of fire stands up off the altar. */
	static void pillar() {
		Minecraft mc = Minecraft.getInstance();
		other = ItemStack.EMPTY;
		play(SoundEvents.GENERIC_EXPLODE.value(), 0.6f, 0.8f);
		play(SoundEvents.BEACON_POWER_SELECT, 0.6f, 1f);
		shake = 2f;
		var rnd = mc.level.random;
		for (int i = 0; i < 160; i++) {
			double a = rnd.nextDouble() * Mth.TWO_PI, r = rnd.nextDouble() * 0.28, up = 0.25 + rnd.nextDouble() * 0.6;
			int rgb = i % 2 == 0 ? 0xFFC65A : 0xFFF8E0;
			mc.level.addParticle(new Vfx.Opt(rgb, 0.08f, 20 + rnd.nextInt(20), 0f, Vfx.GLOW | Vfx.STREAK), centre.x + Math.cos(a) * r, centre.y, centre.z + Math.sin(a) * r, 0, up, 0);
		}
	}

	private static void sparks(int n, float speed) {
		spray(centre.add(right.scale(0.2)), n, speed);
	}

	private static void spray(Vec3 at, int n, float speed) {
		Minecraft mc = Minecraft.getInstance();
		var rnd = mc.level.random;
		int rgb = cloth ? colour : 0xFF9A30;
		for (int i = 0; i < n; i++) {
			double a = rnd.nextDouble() * Mth.TWO_PI, up = 0.05 + rnd.nextDouble() * 0.2;
			double s = speed * (0.4 + rnd.nextDouble());
			mc.level.addParticle(new Vfx.Opt(rgb, 0.05f, 10 + rnd.nextInt(10), 0.8f, Vfx.GLOW | Vfx.STREAK), at.x, at.y + 0.04, at.z,
					Math.cos(a) * s, up + s * 0.5, Math.sin(a) * s);
		}
	}

	/** What someone else did at an anvil: the one across from you, or a stranger you're watching. */
	public static void echo(Net.ForgeEcho m) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.level == null || !(mc.level.getEntity(m.player()) instanceof Player who)) return;
		Vec3 front = who.position().add(who.getLookAngle().multiply(1, 0, 1).normalize()).add(0, 0.95, 0);
		switch (m.action()) {
			case Smithing.BEGIN -> {
				HELD.putIfAbsent(m.player(), who.getMainHandItem());
				who.setItemSlot(EquipmentSlot.MAINHAND, tool(m.value() > 0));
			}
			case Smithing.END, Smithing.LEAVE -> {
				ItemStack was = HELD.remove(m.player());
				if (was != null) who.setItemSlot(EquipmentSlot.MAINHAND, was);
			}
			case Smithing.SWING -> {
				clip(who, true);
				mc.level.playLocalSound(front.x, front.y, front.z, m.value() > 0 ? SoundEvents.ANVIL_PLACE : SoundEvents.ANVIL_LAND, SoundSource.PLAYERS, 0.6f, 1.1f, false);
				spray(front, m.value() > 0 ? 12 : 2, 0.16f);
			}
			case Smithing.MASTER -> {
				clip(who, false);
				if (on) tink();
				else mc.level.playLocalSound(front.x, front.y, front.z, SoundEvents.ANVIL_USE, SoundSource.PLAYERS, 0.32f, 1.9f, false);
			}
			default -> {}
		}
		if (on && mc.screen instanceof ForgeStrikeScreen s && who.distanceToSqr(centre) < 25) s.heard(m.action(), m.value());
	}

	// ---------------------------------------------------------------- each tick and frame

	@SubscribeEvent
	static void tick(ClientTickEvent.Post e) {
		Minecraft mc = Minecraft.getInstance();
		if (!on || mc.player == null) return;
		mc.player.setYRot(faceYaw);
		mc.player.setYHeadRot(faceYaw);
		mc.player.yBodyRot = faceYaw;
		frame();
		LocalPlayerPatch p = EpicFightCapabilities.getEntityPatch(mc.player, LocalPlayerPatch.class);
		if (p != null) {
			var anim = p.getClientAnimator();
			var stance = cloth || master ? Smithing.LOW : Smithing.READY;
			if (!anim.isPlaying(stance) && !anim.isPlaying(Smithing.STRIKE) && !anim.isPlaying(Smithing.TAP)) anim.playAnimation(stance, 0f);
		}
		punch *= 0.7f;
		shake *= 0.75f;
	}

	@SubscribeEvent
	static void angles(ViewportEvent.ComputeCameraAngles e) {
		if (!on || shake < 0.02f) return;
		double t = System.nanoTime() * 1e-8;
		e.setPitch(e.getPitch() + (float) Math.sin(t * 3.7) * shake * 0.5f);
		e.setRoll(e.getRoll() + (float) Math.sin(t * 2.3 + 2) * shake * 0.9f);
	}

	@SubscribeEvent
	static void noHand(RenderHandEvent e) {
		if (on) e.setCanceled(true);
	}

	/** What the work looks like at a heat: metal dull red, orange, yellow, near white; cloth its gate's colour, deepening. */
	private static float[] glow(float h) {
		h = Mth.clamp(h, 0, 1);
		if (cloth) return new float[] {(colour >> 16 & 255) / 255f * h, (colour >> 8 & 255) / 255f * h, (colour & 255) / 255f * h};
		float r = Mth.clamp(h * 3f, 0, 1), g = Mth.clamp(h * 1.6f - 0.35f, 0, 1), b = Mth.clamp(h * 2f - 1.25f, 0, 1);
		return new float[] {r, g, b};
	}

	/** The gauge's colour at k along it (rgb, a little dimmed). */
	static int gaugeColour(float k) {
		float[] c = glow(k);
		return (int) (c[0] * 115) << 16 | (int) (c[1] * 115) << 8 | (int) (c[2] * 115);
	}

	@SubscribeEvent
	static void draw(RenderLevelStageEvent e) {
		if (!on || e.getStage() != RenderLevelStageEvent.Stage.AFTER_ENTITIES) return;
		Minecraft mc = Minecraft.getInstance();
		MultiBufferSource.BufferSource buf = mc.renderBuffers().bufferSource();
		PoseStack ps = e.getPoseStack();
		Vec3 cam = e.getCamera().getPosition();
		ps.pushPose();
		if (ghost) {
			ps.pushPose();
			ps.translate(anvil.getX() - cam.x, anvil.getY() - cam.y, anvil.getZ() - cam.z);
			mc.getBlockRenderer().renderSingleBlock(Blocks.ANVIL.defaultBlockState(), ps, buf, 0xF000F0, OverlayTexture.NO_OVERLAY);
			ps.popPose();
		}
		ps.translate(centre.x - cam.x, centre.y - cam.y + 0.04 + lift, centre.z - cam.z);
		ps.mulPose(Axis.YP.rotationDegrees(-faceYaw));
		ps.translate(0.12, 0, 0);
		ps.mulPose(Axis.YP.rotationDegrees(spin));
		ItemDisplayContext how = flat ? ItemDisplayContext.FIXED : ItemDisplayContext.THIRD_PERSON_RIGHT_HAND;
		if (spin == 0 && !other.isEmpty() && join < 1) {   // the two crossed on the altar, closing as the blows land
			ps.pushPose();
			ps.mulPose(Axis.YP.rotationDegrees(38 * (1 - join)));
			ps.translate(0, 0.07 * (1 - join), 0);
			ps.mulPose(Axis.ZP.rotationDegrees(90));
			ps.scale(1.1f, 1.1f, 1.1f);
			piece(mc, buf, ps, other, ItemDisplayContext.THIRD_PERSON_RIGHT_HAND);
			ps.popPose();
			ps.mulPose(Axis.YP.rotationDegrees(-38 * (1 - join)));
		}
		if (spin == 0) ps.mulPose(flat ? Axis.XP.rotationDegrees(90) : Axis.ZP.rotationDegrees(90)); // lying on the anvil; on the way up it stands
		float s = flat ? 0.8f * (1 - punch * 0.08f) : 1.1f, along = flat ? 1 : Mth.lerp(shape, 0.32f, 1f), wide = flat ? 1 : Mth.lerp(shape, 1.5f, 1f) * (1 - punch * 0.12f);
		ps.scale(s * wide, s * along, s * wide);
		piece(mc, buf, ps, work, how);
		ps.popPose();
	}

	/** One piece at its heat: darkened as it heats, then its glow over it. */
	private static void piece(Minecraft mc, MultiBufferSource.BufferSource buf, PoseStack ps, ItemStack s, ItemDisplayContext how) {
		float[] c = glow(heat);
		float cold = cloth ? 1 : Mth.clamp(1 - heat * 1.4f, 0.12f, 1);
		mc.getItemRenderer().renderStatic(s, how, 0xF000F0, OverlayTexture.NO_OVERLAY, ps, rt -> new Tint(buf.getBuffer(rt), cold, cold, cold), mc.level, 0);
		buf.endBatch();
		if (heat > 0.03f) {
			RenderType hot = RenderType.eyes(TextureAtlas.LOCATION_BLOCKS);
			mc.getItemRenderer().renderStatic(s, how, 0xF000F0, OverlayTexture.NO_OVERLAY, ps, rt -> new Tint(buf.getBuffer(hot), c[0], c[1], c[2]), mc.level, 0);
			buf.endBatch();
		}
	}

	/** Any model drawn in a colour of ours. */
	private record Tint(VertexConsumer v, float r, float g, float b) implements VertexConsumer {
		@Override
		public VertexConsumer addVertex(float x, float y, float z) {
			v.addVertex(x, y, z);
			return this;
		}

		@Override
		public VertexConsumer setColor(int red, int green, int blue, int alpha) {
			v.setColor((int) (red * r), (int) (green * g), (int) (blue * b), alpha);
			return this;
		}

		@Override
		public VertexConsumer setUv(float u, float w) {
			v.setUv(u, w);
			return this;
		}

		@Override
		public VertexConsumer setUv1(int u, int w) {
			v.setUv1(u, w);
			return this;
		}

		@Override
		public VertexConsumer setUv2(int u, int w) {
			v.setUv2(u, w);
			return this;
		}

		@Override
		public VertexConsumer setNormal(float x, float y, float z) {
			v.setNormal(x, y, z);
			return this;
		}
	}
}
