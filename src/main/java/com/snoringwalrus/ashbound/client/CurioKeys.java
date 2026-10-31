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

	/** Tab-targeting for a healer: the player you're looking at, or else the next of the party near you, then no one. */
	public static final KeyMapping HEAL_TARGET = new KeyMapping("key.ashbound.heal_target", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_G,
			"key.categories.ashbound");
	/** Who it's on; the party HUD marks them. */
	public static String healTarget = "";

	public static final KeyMapping JOURNAL = new KeyMapping("key.ashbound.journal", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_J,
			"key.categories.ashbound");

	public static final KeyMapping MOUNT = new KeyMapping("key.ashbound.mount", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_H,
			"key.categories.ashbound");

	public static final KeyMapping BAG = new KeyMapping("key.ashbound.bag", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_I,
			"key.categories.ashbound");

	/** The skill keys past the first, which is R above. */
	private static final KeyMapping[] SLOTS = {SKILL, slot(1, GLFW.GLFW_KEY_Z), slot(2, GLFW.GLFW_KEY_X), slot(3, GLFW.GLFW_KEY_C)};
	public static final KeyMapping SKILLS = new KeyMapping("key.ashbound.skills", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_N, "key.categories.ashbound");
	public static final KeyMapping PING = new KeyMapping("key.ashbound.ping", InputConstants.Type.MOUSE, GLFW.GLFW_MOUSE_BUTTON_MIDDLE, "key.categories.ashbound");
	public static final KeyMapping FORM = new KeyMapping("key.ashbound.form", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_B, "key.categories.ashbound");

	private static KeyMapping slot(int i, int key) {
		return new KeyMapping("key.ashbound.skill_" + i, InputConstants.Type.KEYSYM, key, "key.categories.ashbound");
	}

	static KeyMapping slotKey(int i) {
		return SLOTS[i];
	}

	public static void skillHud(net.neoforged.bus.api.IEventBus bus) {
		SkillHud.hooks(bus);
		SkillFx.hooks(bus);
	}

	private static boolean jumpWas, jumped;

	public static void register(RegisterKeyMappingsEvent e) {
		e.register(SKILL);
		e.register(JOURNAL);
		e.register(HEAL_TARGET);
		e.register(POWER);
		e.register(MOUNT);
		e.register(BAG);
		e.register(SKILLS);
		e.register(FORM);
		e.register(PING);
		for (int i = 1; i < SLOTS.length; i++) e.register(SLOTS[i]);
	}

	public static void hooks() {
		NeoForge.EVENT_BUS.addListener((ClientTickEvent.Post e) -> tick());
		// every world starts in third person; F5 still changes it
		NeoForge.EVENT_BUS.addListener((ClientPlayerNetworkEvent.LoggingIn e) -> Minecraft.getInstance().options.setCameraType(CameraType.THIRD_PERSON_BACK));
	}

	private static final String KEYS_DONE = "ashbound-keys-2.done";
	/** How far you can pick someone by looking at them, and how true: {@link com.snoringwalrus.ashbound.Spells} reaches as far. */
	private static final double PICK_REACH = 32, PICK_AIM = 0.985;
	private static boolean keysChecked;

	/** Once: anything else out of the box on a skill key loses it, or both would fire. Rebinding one after that stays yours. */
	private static void clearKeys(Minecraft mc) {
		if (keysChecked) return;
		keysChecked = true;
		var mark = net.neoforged.fml.loading.FMLPaths.CONFIGDIR.get().resolve(KEYS_DONE);
		if (java.nio.file.Files.exists(mark)) return;
		// Epic Fight's lock-on and the Curios screen both sit on G out of the box
		var lock = yesman.epicfight.client.input.EpicFightKeyMappings.LOCK_ON;
		if (lock.same(HEAL_TARGET)) mc.options.setKey(lock, InputConstants.Type.KEYSYM.getOrCreate(GLFW.GLFW_KEY_O));
		for (KeyMapping mine : java.util.List.of(SLOTS[1], SLOTS[2], SLOTS[3], FORM, SKILLS, HEAL_TARGET))
			for (KeyMapping k : mc.options.keyMappings)
				if (k != mine && !k.isUnbound() && k.same(mine) && !k.getCategory().equals(mine.getCategory())) mc.options.setKey(k, InputConstants.UNKNOWN);
		KeyMapping.resetMapping();
		mc.options.save();
		try {
			java.nio.file.Files.writeString(mark, "");
		} catch (java.io.IOException e) {
			// it's looked at again next time
		}
	}

	private static boolean wears(LocalPlayer p, String id) {
		ResourceLocation key = ResourceLocation.fromNamespaceAndPath("ashbound", id);
		return CuriosApi.getCuriosInventory(p).map(inv -> inv.isEquipped(st ->
				net.minecraft.core.registries.BuiltInRegistries.ITEM.getKey(st.getItem()).equals(key))).orElse(false);
	}

	private static void setHealTarget(String name) {
		healTarget = name;
		PacketDistributor.sendToServer(new Net.HealPick(name));
	}

	/** Whoever's under the crosshair, or null. */
	private static String aimedAt(LocalPlayer p) {
		String best = null;
		double aim = PICK_AIM;
		for (var o : p.clientLevel.players()) {
			if (o == p || o.isSpectator() || o.distanceTo(p) > PICK_REACH) continue;
			double dot = p.getLookAngle().dot(o.getBoundingBox().getCenter().subtract(p.getEyePosition()).normalize());
			if (dot > aim) {
				aim = dot;
				best = o.getName().getString();
			}
		}
		return best;
	}

	private static void stepHealTarget(LocalPlayer p) {
		String aimed = aimedAt(p);
		var near = Net.clientParty.stream().filter(m -> m.online() && m.near()).map(Net.PartyMember::name).toList();
		if (aimed != null) setHealTarget(aimed.equals(healTarget) ? "" : aimed);
		else if (!near.isEmpty()) {
			int at = near.indexOf(healTarget) + 1;
			setHealTarget(at < near.size() ? near.get(at) : "");
		} else if (!healTarget.isEmpty()) setHealTarget("");
		else {
			p.displayClientMessage(net.minecraft.network.chat.Component.literal("Look at a player, then press the key"), true);
			return;
		}
		p.displayClientMessage(net.minecraft.network.chat.Component.literal(healTarget.isEmpty() ? "Heal target: none" : "Heal target: " + healTarget), true);
	}

	private static boolean stillHere(LocalPlayer p) {
		return Net.clientParty.stream().anyMatch(m -> m.name().equals(healTarget)) || p.clientLevel.players().stream().anyMatch(o -> o.getName().getString().equals(healTarget));
	}

	private static void tick() {
		Minecraft mc = Minecraft.getInstance();
		LocalPlayer p = mc.player;
		if (p == null) return;
		PartyMap.tick();
		while (PING.consumeClick()) Pings.send();
		while (BAG.consumeClick()) PacketDistributor.sendToServer(new Net.BagAct(com.snoringwalrus.ashbound.Bag.OPEN, net.minecraft.world.item.ItemStack.EMPTY));
		while (HEAL_TARGET.consumeClick()) stepHealTarget(p);
		// they've gone
		if (!healTarget.isEmpty() && !stillHere(p)) setHealTarget("");
		while (POWER.consumeClick()) PacketDistributor.sendToServer(new Net.CurioKey(p.isShiftKeyDown() ? 2 : 0));
		var swap = yesman.epicfight.client.input.EpicFightKeyMappings.SWITCH_MODE;
		if (!swap.isUnbound()) {
			mc.options.setKey(swap, InputConstants.UNKNOWN);
			KeyMapping.resetMapping();
		}
		while (SKILL.consumeClick()) PacketDistributor.sendToServer(new Net.CurioKey(Net.JOINED_SKILL));
		for (int i = 1; i < SLOTS.length; i++) while (SLOTS[i].consumeClick()) PacketDistributor.sendToServer(new Net.SkillUse(i));
		while (SKILLS.consumeClick()) if (mc.screen == null) mc.setScreen(new SkillScreen());
		while (FORM.consumeClick()) PacketDistributor.sendToServer(new Net.CurioKey(Net.FORM));
		clearKeys(mc);
		while (MOUNT.consumeClick()) {
			if (p.isShiftKeyDown() && !p.isPassenger() && !com.snoringwalrus.ashbound.Mounts.client.isEmpty()) mc.setScreen(new MountUpScreen());
			else PacketDistributor.sendToServer(new Net.CurioKey(Net.MOUNT));
		}
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
