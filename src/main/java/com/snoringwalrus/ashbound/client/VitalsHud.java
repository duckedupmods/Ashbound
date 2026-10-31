package com.snoringwalrus.ashbound.client;

import java.util.Set;

import com.snoringwalrus.ashbound.Ashbound;
import com.mojang.math.Axis;
import com.snoringwalrus.ashbound.Forms;
import com.snoringwalrus.ashbound.Levels;
import com.snoringwalrus.ashbound.Mount;
import com.snoringwalrus.ashbound.Net;
import com.snoringwalrus.ashbound.Spells;

import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.effect.MobEffects;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.client.event.ClientPlayerNetworkEvent;
import net.neoforged.neoforge.client.event.RegisterGuiLayersEvent;
import net.neoforged.neoforge.client.event.RenderGuiLayerEvent;
import net.neoforged.neoforge.client.gui.VanillaGuiLayers;
import net.neoforged.neoforge.common.NeoForge;
import yesman.epicfight.client.world.capabilites.entitypatch.player.LocalPlayerPatch;
import yesman.epicfight.world.capabilities.EpicFightCapabilities;

/**
 * Health, stamina and mana, above the hotbar in place of the hearts, the hunger row and Epic Fight's stamina bar: your
 * level in an iron crest, a blade each side of it for health and mana, stamina running out from under it, armour and
 * food above. They grow as their maximum does; a hit leaves a pale chunk that drains after a moment. Hold the player
 * list key (TAB) for the stamina number. Your party goes top left, a name and a thin bar each. Also wires up the compass
 * and the screens the server asks for.
 */
public final class VitalsHud {
	private VitalsHud() {}

	private static final int X = 6, Y = 6, SOCKET = 28, WING_H = 10, BAR_H = 3, MEMBER_W = 80, MEMBER_H = 3, NOTCHES = 10, TIP = 5;
	/** up from the bottom of the screen */
	private static final int XP_UP = 25, STAMINA_UP = 32, WING_UP = 46, ROW_UP = 13;
	/** how far the held item's name and the action bar rise to clear them */
	private static final int LIFT = 14, TOP_OF_ROW = 30;
	private static final float HOLD_MS = 500, DRAIN = 0.4f, FOLLOW = 14;
	private static final ResourceLocation ARMOUR = ResourceLocation.withDefaultNamespace("hud/armor_full"),
			FOOD = ResourceLocation.withDefaultNamespace("hud/food_full");
	/** What this draws instead. */
	private static final Set<ResourceLocation> HIDDEN = Set.of(VanillaGuiLayers.PLAYER_HEALTH, VanillaGuiLayers.ARMOR_LEVEL, VanillaGuiLayers.FOOD_LEVEL,
			VanillaGuiLayers.AIR_LEVEL, VanillaGuiLayers.EXPERIENCE_BAR, VanillaGuiLayers.EXPERIENCE_LEVEL, ResourceLocation.fromNamespaceAndPath("epicfight", "stamina_bar"));
	private static final Set<ResourceLocation> LIFTED = Set.of(VanillaGuiLayers.SELECTED_ITEM_NAME, VanillaGuiLayers.OVERLAY_MESSAGE);

	private static final Bar HP = new Bar(), STAMINA = new Bar(), MANA = new Bar();
	private static long last;

	/** A bar's eased fill and the pale chunk behind it. */
	static final class Bar {
		float shown = 1, trail = 1, was = 1;
		long hold;

		Bar() {}

		Bar(float f) {
			shown = trail = was = f;
		}

		long hitAt() {
			return hold - (long) HOLD_MS;
		}

		void step(float f, float dt, long now) {
			shown += (f - shown) * Math.min(1, dt * FOLLOW);
			if (f < was - 0.001f) hold = now + (long) HOLD_MS;
			was = f;
			if (f >= trail) trail = f;
			else if (now > hold) trail = Math.max(f, trail - DRAIN * dt);
		}
	}

	public static void hooks(IEventBus bus) {
		bus.addListener((RegisterGuiLayersEvent e) -> e.registerAbove(VanillaGuiLayers.HOTBAR,
				ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "vitals"), VitalsHud::draw));
		NeoForge.EVENT_BUS.addListener((RenderGuiLayerEvent.Pre e) -> {
			if (HIDDEN.contains(e.getName()) || e.getName().equals(VanillaGuiLayers.VEHICLE_HEALTH) && Minecraft.getInstance().player.getVehicle() instanceof Mount) e.setCanceled(true);
			else if (LIFTED.contains(e.getName())) {
				e.getGuiGraphics().pose().pushPose();
				e.getGuiGraphics().pose().translate(0, -LIFT, 0);
			}
		});
		NeoForge.EVENT_BUS.addListener((RenderGuiLayerEvent.Post e) -> {
			if (LIFTED.contains(e.getName())) e.getGuiGraphics().pose().popPose();
		});
		Net.onForge = m -> Minecraft.getInstance().setScreen(new ForgeScreen(m.pos(), m.known()));
		Net.onForgeStart = ForgeStrikeScreen::open;
		Net.onForgeEcho = ForgeScene::echo;
		Net.onColdWake = ColdScene::play;
		Net.onIntro = IntroScene::play;
		Net.onJournal = QuestScreen::state;
		Net.onGuildJobs = QuestScreen::jobs;
		QuestHud.hooks(bus);
		InvButtons.hooks();
		BossHud.hooks();
		SpellFx.hooks();
		NeoForge.EVENT_BUS.addListener((ClientPlayerNetworkEvent.LoggingOut e) -> Net.clientParty = java.util.List.of());
	}

	/** Long enough to tell you've grown, never the width of the screen: a little more each time the maximum doubles. */
	private static int length(float max, float start) {
		return Mth.clamp(Math.round(74 + 10 * (float) (Math.log(max / start) / Math.log(2))), 60, 130);
	}

	/** A frame with its corners cut: black, then the iron line inside it. */
	static void frame(GuiGraphics g, int x, int y, int w, int h) {
		g.fill(x + 1, y - 2, x + w - 1, y + h + 2, AshUi.BLACK);
		g.fill(x - 2, y + 1, x + w + 2, y + h - 1, AshUi.BLACK);
		g.fill(x - 1, y, x + w + 1, y + h, AshUi.BLACK);
		g.fill(x, y - 1, x + w, y, AshUi.LINE);
		g.fill(x, y + h, x + w, y + h + 1, AshUi.LINE);
		g.fill(x - 1, y, x, y + h, AshUi.LINE);
		g.fill(x + w, y, x + w + 1, y + h, AshUi.LINE);
	}

	private static void draw(GuiGraphics g, DeltaTracker dt) {
		Minecraft mc = Minecraft.getInstance();
		LocalPlayer p = mc.player;
		if (p == null || mc.options.hideGui || mc.gameMode == null) return;
		if (!Net.clientParty.isEmpty()) party(g, mc, X, Y);
		if (!mc.gameMode.canHurtPlayer()) return;
		long now = System.currentTimeMillis();
		float step = Math.min(0.1f, (now - last) / 1000f);
		last = now;
		boolean numbers = mc.options.keyPlayerList.isDown();

		float maxHp = Math.max(1, p.getMaxHealth()), hp = Mth.clamp(p.getHealth() / maxHp, 0, 1);
		LocalPlayerPatch patch = EpicFightCapabilities.getEntityPatch(p, LocalPlayerPatch.class);
		float maxSt = patch == null ? 15 : Math.max(1, patch.getMaxStamina()), stamina = patch == null ? 1 : Mth.clamp(patch.getStamina() / maxSt, 0, 1);
		float maxMana = Math.max(1, Spells.clientMax), mana = Math.min(1, Spells.clientMana / maxMana);
		HP.step(hp, step, now);
		STAMINA.step(stamina, step, now);
		MANA.step(mana, step, now);

		int cx = g.guiWidth() / 2, bottom = g.guiHeight();
		int wingY = bottom - WING_UP, staminaY = bottom - STAMINA_UP, inner = SOCKET / 2 + 1;
		int hw = length(maxHp, 20), mw = length(maxMana, 100), sw = length(maxSt, 15);

		// experience: a thread along the top of the hotbar, the number off its left end
		int xy = bottom - XP_UP;
		g.fill(cx - 91, xy, cx + 91, xy + 2, 0xC0050404);
		g.fill(cx - 91, xy, cx - 91 + Math.round(182 * p.experienceProgress), xy + 2, 0xFF8ADC52);
		if (p.experienceLevel > 0) {
			String xp = String.valueOf(p.experienceLevel);
			g.drawString(mc.font, xp, cx - 95 - mc.font.width(xp), xy - 3, 0xFF8ADC52, true);
		}

		// stamina runs out from the middle both ways, under the wings
		frame(g, cx - sw, staminaY, sw * 2, BAR_H);
		g.fill(cx - sw, staminaY, cx + sw, staminaY + BAR_H, 0xFF141A0C);
		int fs = Math.round(sw * Mth.clamp(STAMINA.shown, 0, 1)), ts = Math.round(sw * Mth.clamp(STAMINA.trail, 0, 1));
		if (ts > fs) g.fill(cx - ts, staminaY, cx + ts, staminaY + BAR_H, 0xFFE8C8A0);
		if (fs > 0) {
			g.fillGradient(cx - fs, staminaY, cx + fs, staminaY + BAR_H, 0xFFC4E04A, 0xFF4A6A18);
			g.fill(cx - fs, staminaY, cx + fs, staminaY + 1, 0xFFE8F4A0);
		}
		if (numbers) g.drawString(mc.font, Math.round(patch == null ? maxSt : patch.getStamina()) + " / " + Math.round(maxSt), cx + sw + 8, staminaY - 2, 0xFFC8DC8A, true);

		// health and mana, a blade each side of the crest
		boolean poison = p.hasEffect(MobEffects.POISON), wither = p.hasEffect(MobEffects.WITHER);
		wing(g, cx - inner - hw, wingY, hw, HP, true, poison ? 0xFF8EA83A : wither ? 0xFF4A4440 : 0xFFD8402C, poison ? 0xFF46601A : wither ? 0xFF201C1A : 0xFF7A1410,
				poison ? 0xFFD4E88A : wither ? 0xFF8A8076 : 0xFFFF9A7A, 0xFF1E0E0C);
		wing(g, cx + inner, wingY, mw, MANA, false, 0xFF5AA0FF, 0xFF1E3E9A, 0xFFB8DCFF, 0xFF141A2A);
		if (hp < 0.25f) {   // close to death, the blade's frame beats
			int beat = (int) (0x70 + 0x60 * Math.sin(now / 160.0)) << 24 | 0xE0301C;
			g.renderOutline(cx - inner - hw - 1, wingY - 1, hw + 2, WING_H + 2, beat);
		}
		float absorb = p.getAbsorptionAmount();
		if (absorb > 0) {
			int aw = Math.min(hw, Math.round(hw * absorb / maxHp));
			g.fill(cx - inner - aw, wingY, cx - inner, wingY + 2, 0xFFFFD24A);
		}
		String life = Math.round(p.getHealth()) + (absorb > 0 ? "+" + Math.round(absorb) : "") + " / " + Math.round(maxHp);
		g.drawString(mc.font, life, cx - inner - hw + (hw - mc.font.width(life)) / 2, wingY + 1, AshUi.TEXT, true);
		String magic = Math.round(Spells.clientMana) + " / " + Math.round(maxMana);
		g.drawString(mc.font, magic, cx + inner + (mw - mc.font.width(magic)) / 2, wingY + 1, AshUi.TEXT, true);

		crest(g, mc, cx, wingY + WING_H / 2, now);

		// armour on the left, food on the right, breath past the food while it's running out
		int y = wingY - ROW_UP;
		int armour = p.getArmorValue();
		if (armour > 0) {
			String a = String.valueOf(armour);
			int ax = cx - inner - 3 - mc.font.width(a);
			g.drawString(mc.font, a, ax, y + 1, AshUi.BODY, true);
			g.blitSprite(ARMOUR, ax - 11, y, 9, 9);
		}
		int tx = cx + inner + 3, food = p.getFoodData().getFoodLevel();
		g.blitSprite(FOOD, tx, y, 9, 9);
		String f = String.valueOf(food);
		g.drawString(mc.font, f, tx + 11, y + 1, food <= 6 ? AshUi.BAD : AshUi.BODY, true);
		tx += 11 + mc.font.width(f) + 7;
		int air = p.getAirSupply(), maxAir = p.getMaxAirSupply();
		if (air < maxAir) {
			int w = 50, ay = y + 2;
			frame(g, tx, ay, w, 4);
			g.fill(tx, ay, tx + w, ay + 4, 0xFF102028);
			g.fill(tx, ay, tx + Math.round(w * Math.max(0, air) / (float) maxAir), ay + 4, 0xFF7ADCF0);
		}
	}

	/** One blade: fills from the crest outward, a pale chunk where a hit landed, notches every tenth, a point at the far end. */
	private static void wing(GuiGraphics g, int x, int y, int w, Bar b, boolean left, int top, int bottom, int edge, int trough) {
		frame(g, x, y, w, WING_H);
		g.fill(x, y, x + w, y + WING_H, trough);
		int fw = Math.round(w * Mth.clamp(b.shown, 0, 1)), tw = Math.round(w * Mth.clamp(b.trail, 0, 1));
		int from = left ? x + w : x, sign = left ? -1 : 1;
		if (tw > fw) g.fill(Math.min(from + sign * fw, from + sign * tw), y, Math.max(from + sign * fw, from + sign * tw), y + WING_H, 0xFFE8C8A0);
		if (fw > 0) {
			g.fillGradient(Math.min(from, from + sign * fw), y, Math.max(from, from + sign * fw), y + WING_H, top, bottom);
			g.fill(Math.min(from, from + sign * fw), y, Math.max(from, from + sign * fw), y + 1, edge);
			if (fw < w) g.fill(left ? from - fw : from + fw - 1, y, left ? from - fw + 1 : from + fw, y + WING_H, edge);
		}
		for (int i = 1; i < NOTCHES; i++) g.fill(x + w * i / NOTCHES, y + WING_H - 2, x + w * i / NOTCHES + 1, y + WING_H, 0x90050404);
		tip(g, left ? x - 2 : x + w + 2, y, WING_H, left, TIP);
	}

	/** A stepped iron point on the end of a bar. */
	static void tip(GuiGraphics g, int x, int y, int h, boolean left, int size) {
		for (int i = 0; i < size; i++) {
			int tx = x + (left ? -i - 1 : i);
			g.fill(tx, y - 1 + i, tx + 1, y + h + 1 - i, AshUi.BLACK);
			if (i < size - 1) g.fill(tx, y + i, tx + 1, y + h - i, AshUi.LINE);
		}
	}

	/** Your level in an iron diamond between the blades; it burns while a level is ready to buy. */
	private static void crest(GuiGraphics g, Minecraft mc, int cx, int cy, long now) {
		boolean ready = Levels.clientNext > 0 && Levels.clientAsh >= Levels.clientNext;
		var pose = g.pose();
		pose.pushPose();
		pose.translate(cx, cy, 0);
		pose.mulPose(Axis.ZP.rotationDegrees(45));
		g.fill(-10, -10, 10, 10, AshUi.BLACK);
		g.fill(-9, -9, 9, 9, AshUi.LINE);
		g.fill(-8, -8, 8, 8, 0xFF16120F);
		if (ready) g.fill(-8, -8, 8, 8, (int) (0x70 + 0x40 * Math.sin(now / 300.0)) << 24 | 0xE8742C);
		if (Forms.clientReady) {   // a Form's moment has come: it burns, fast and red
			float beat = (float) (0.5 + 0.5 * Math.sin(now / 90.0));
			g.fill(-10, -10, 10, 10, (int) (0x90 + 0x60 * beat) << 24 | 0xF03018);
			g.fill(-6, -6, 6, 6, (int) (0x80 + 0x70 * beat) << 24 | 0xFFD060);
		}
		g.fill(-6, 5, 6, 6, AshUi.EMBER_C);
		g.fill(5, -6, 6, 6, AshUi.EMBER_C);
		pose.popPose();
		long left = Forms.clientUntil - now;
		String lv = left > 0 ? String.valueOf((int) Math.ceil(left / 1000.0)) : String.valueOf(Levels.clientLevel);
		g.drawString(mc.font, lv, cx - mc.font.width(lv) / 2 + 1, cy - 4, left > 0 ? 0xFFFF8050 : AshUi.EMBER_LT, true);
		if (Forms.clientReady) {
			String key = "[" + CurioKeys.FORM.getTranslatedKeyMessage().getString() + "] " + Forms.byId(Forms.clientForm).tome();
			g.drawString(mc.font, key, cx - mc.font.width(key) / 2, cy - TOP_OF_ROW, 0xFFFFA050, true);
		}
	}

	/** The others in your party: dim when they're far off, grey when they're offline, an ember by the leader. */
	private static void party(GuiGraphics g, Minecraft mc, int x, int y) {
		for (Net.PartyMember m : Net.clientParty) {
			int tx = x;
			if (m.leader()) {
				g.fill(tx, y + 2, tx + 3, y + 5, AshUi.EMBER_C);
				tx += 6;
			}
			boolean aimed = m.name().equals(CurioKeys.healTarget);
			g.drawString(mc.font, aimed ? "> " + m.name() : m.name(), tx, y, aimed ? AshUi.EMBER_LT : !m.online() ? 0xFF6F685D : m.near() ? AshUi.TEXT : AshUi.BODY, true);
			y += 10;
			frame(g, x, y, MEMBER_W, MEMBER_H);
			g.fill(x, y, x + MEMBER_W, y + MEMBER_H, 0xFF1E0E0C);
			if (m.online()) g.fill(x, y, x + Math.round(MEMBER_W * Mth.clamp(m.health() / Math.max(1, m.max()), 0, 1)), y + MEMBER_H, 0xFFD8402C);
			y += MEMBER_H + 7;
		}
	}
}
