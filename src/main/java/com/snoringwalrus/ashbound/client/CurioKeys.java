package com.snoringwalrus.ashbound.client;

import com.mojang.blaze3d.platform.InputConstants;
import com.snoringwalrus.ashbound.Net;
import net.minecraft.client.CameraType;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.client.event.ClientPlayerNetworkEvent;
import net.neoforged.neoforge.client.event.ClientTickEvent;
import net.neoforged.neoforge.client.event.RegisterKeyMappingsEvent;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.network.PacketDistributor;
import org.lwjgl.glfw.GLFW;
import top.theillusivec4.curios.api.CuriosApi;

/**
 * The curio key (V): the worn relic's power, or with sneak the Rift Key. And the Gryphon Plume: jump again in the
 * air, hold jump to drift down (movement is the client's; the server is told so the fall doesn't count).
 */
public final class CurioKeys {
	private CurioKeys() {}

	public static final KeyMapping POWER = new KeyMapping("key.ashbound.relic_power", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_V,
			"key.categories.ashbound");

	/** The Joined weapons' skill. Epic Fight's own mode switch sits on R out of the box and is taken off every key. */
	public static final KeyMapping SKILL = new KeyMapping("key.ashbound.joined_skill", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_R,
			"key.categories.ashbound");

	public static final KeyMapping JOURNAL = new KeyMapping("key.ashbound.journal", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_J,
			"key.categories.ashbound");

	private static boolean jumpWas, jumped;

	public static void register(RegisterKeyMappingsEvent e) {
		e.register(SKILL);
		e.register(JOURNAL);
		e.register(POWER);
	}

	public static void hooks() {
		NeoForge.EVENT_BUS.addListener((ClientTickEvent.Post e) -> tick());
		// every world starts in third person; F5 still changes it
		NeoForge.EVENT_BUS.addListener((ClientPlayerNetworkEvent.LoggingIn e) -> Minecraft.getInstance().options.setCameraType(CameraType.THIRD_PERSON_BACK));
	}

	private static boolean wears(LocalPlayer p, String id) {
		ResourceLocation key = ResourceLocation.fromNamespaceAndPath("ashbound", id);
		return CuriosApi.getCuriosInventory(p).map(inv -> inv.isEquipped(st ->
				net.minecraft.core.registries.BuiltInRegistries.ITEM.getKey(st.getItem()).equals(key))).orElse(false);
	}

	private static void tick() {
		Minecraft mc = Minecraft.getInstance();
		LocalPlayer p = mc.player;
		if (p == null) return;
		while (POWER.consumeClick()) PacketDistributor.sendToServer(new Net.CurioKey(p.isShiftKeyDown() ? 2 : 0));
		var swap = yesman.epicfight.client.input.EpicFightKeyMappings.SWITCH_MODE;
		if (!swap.isUnbound()) {
			mc.options.setKey(swap, InputConstants.UNKNOWN);
			KeyMapping.resetMapping();
		}
		while (SKILL.consumeClick()) PacketDistributor.sendToServer(new Net.CurioKey(Net.JOINED_SKILL));
		while (JOURNAL.consumeClick()) if (mc.screen == null) QuestScreen.open();
		boolean jump = mc.options.keyJump.isDown();
		if (p.onGround() || p.isInWater() || p.getAbilities().flying) jumped = false;
		else if (wears(p, "gryphon_plume")) {
			if (jump && !jumpWas && !jumped && p.tickCount > 5) {
				Vec3 v = p.getDeltaMovement();
				p.setDeltaMovement(v.x, 0.6, v.z);
				p.resetFallDistance();
				jumped = true;
				PacketDistributor.sendToServer(new Net.CurioKey(1));
			} else if (jump && p.getDeltaMovement().y < -0.12) {
				Vec3 v = p.getDeltaMovement();
				p.setDeltaMovement(v.x, -0.12, v.z);
				p.resetFallDistance();
			}
		}
		jumpWas = jump;
	}
}
