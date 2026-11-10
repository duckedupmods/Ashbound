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
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.sounds.SoundEvents;
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
 * Health, stamina, mana and, once you're getting hungry, food, above the hotbar in place of the hearts, the hunger row and Epic Fight's stamina bar: your
 * level in an iron crest, a blade each side of it for health and mana, stamina running out from under it, armour and
 * food above. They grow as their maximum does; a hit leaves a pale chunk that drains after a moment. Hold the player
 * list key (TAB) for the stamina number. Your party goes top left, a card each. Also wires up the compass
 * and the screens the server asks for.
 */
public final class VitalsHud {
	private VitalsHud() {}

	private static final int X = 6, Y = 6, SOCKET = 28, WING_H = 10, BAR_H = 3, MEMBER_FACE = 24, MEMBER_STEP = 30, MEMBER_ROW = 36, MEMBER_H = 5, NOTCHES = 10, TIP = 5;
	/** up from the bottom of the screen */
	private static final int XP_UP = 25, STAMINA_UP = 32, WING_UP = 46, ROW_UP = 13, WIND_UP = 66;
	/** how far the held item's name and the action bar rise to clear them */
	private static final int LIFT = 14, TOP_OF_ROW = 30;
	/** Up from the bottom of the screen, and the food level the bar comes up at and it starts to warn at. */
	private static final int HUNGER_UP = 28, HUNGER_SHOWS = 14, HUNGER_WARNS = 6;
	private static int fedLast = 20;
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
		Net.onForge = m -> Minecraft.getInstance().setScreen(new ForgeScreen(m.pos()));
		Net.onForgeStart = ForgeStrikeScreen::open;
		Net.onForgeEcho = ForgeScene::echo;
		Net.onColdWake = ColdScene::play;
		Net.onIntro = IntroScene::play;
		Net.onPing = Pings::got;
		Pings.hooks(bus);
		NpcMarkers.hooks();
		PetRender.hooks();
		Net.onJournal = QuestScreen::state;
		Net.onGuildJobs = QuestScreen::jobs;
		QuestHud.hooks(bus);
		InvButtons.hooks();
		MenuTabs.hooks();
		BossHud.hooks();
		SpellFx.hooks();
		TradeFx.hooks();
		NeoForge.EVENT_BUS.addListener((ClientPlayerNetworkEvent.LoggingOut e) -> Net.clientParty = java.util.List.of());
	}

	/** How long your mount can stay up, over the armour and food, only while it's not full. */
	private static void wind(GuiGraphics g, LocalPlayer p) {
		if (!(p.getVehicle() instanceof Mount m) || m.getFirstPassenger() != p || com.snoringwalrus.ashbound.Mounts.tireless(p) || Mount.wind >= 1) return;
		int w = 100, h = 3, x = (g.guiWidth() - w) / 2, y = g.guiHeight() - WIND_UP;
		frame(g, x, y, w, h);
		g.fill(x, y, x + w, y + h, 0xFF102028);
		g.fill(x, y, x + Math.round(w * Mount.wind), y + h, Mount.wind < 0.2f ? 0xFFE05030 : 0xFF8FD8FF);
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
		if (!Net.clientParty.isEmpty()) party(g, mc, X, Y, mc.options.keyPlayerList.isDown());
		wind(g, p);
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
		hunger(g, cx, bottom - HUNGER_UP, sw, p.getFoodData().getFoodLevel(), now);

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
		hungry(g, mc, cx, wingY + WING_H / 2, p.getFoodData().getFoodLevel(), now);

		// armour on the left, food on the right, breath past the food while it's running out
		int y = wingY - ROW_UP;
		int armour = p.getArmorValue();
		if (armour > 0) {
			String a = String.valueOf(armour);
			int ax = cx - inner - 3 - mc.font.width(a);
			g.drawString(mc.font, a, ax, y + 1, AshUi.BODY, true);
			g.blitSprite(ARMOUR, ax - 11, y, 9, 9);
		}
		toxicity(g, p, cx - inner - 3 - (armour > 0 ? mc.font.width(String.valueOf(armour)) + 18 : 0), y + 2, now);
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

	/** Elixir toxicity left of the armour, ending at right: only while there's some in you, beating once it's over your limit. */
	private static void toxicity(GuiGraphics g, LocalPlayer p, int right, int y, long now) {
		double tox = com.snoringwalrus.ashbound.Trades.toxicity(p), limit = com.snoringwalrus.ashbound.Trades.toxLimit(p);
		if (tox <= 0.5) return;
		int w = 40, x = right - w;
		frame(g, x, y, w, 4);
		g.fill(x, y, x + w, y + 4, 0xFF0E1A0A);
		g.fill(x, y, x + Math.round(w * (float) Math.min(1, tox / limit)), y + 4, 0xFF7AC03A);
		if (tox > limit) g.renderOutline(x - 1, y - 1, w + 2, 6, (int) (0x70 + 0x60 * Math.sin(now / 160.0)) << 24 | 0x9AE040);
	}

	/** Under the stamina it comes up with, running out from the middle the same way: nothing to see while you're fed. */
	private static void hunger(GuiGraphics g, int cx, int y, int half, int food, long now) {
		if (food > HUNGER_SHOWS) return;
		g.fill(cx - half, y, cx + half, y + 2, 0xE0140C04);
		int w = Math.round(half * food / 20f), pulse = (int) (0x90 + 0x6F * Math.sin(now / 180.0));
		if (w > 0) g.fill(cx - w, y, cx + w, y + 2, food > HUNGER_WARNS ? 0xFFE8A82C : pulse << 24 | 0xF06A20);
	}

	/** Over the crest while it's getting serious, with one low rumble when it first does. */
	private static void hungry(GuiGraphics g, Minecraft mc, int cx, int cy, int food, long now) {
		if (food <= HUNGER_WARNS && fedLast > HUNGER_WARNS) mc.getSoundManager().play(SimpleSoundInstance.forUI(SoundEvents.PLAYER_BURP, 0.45f, 0.7f));
		fedLast = food;
		if (food > HUNGER_WARNS) return;
		String s = food == 0 ? "Starving" : "Hungry";
		int w = mc.font.width(s) + 11, x = cx - w / 2, y = cy - TOP_OF_ROW - (Forms.clientReady ? 11 : 0);
		g.blitSprite(FOOD, x, y - 1, 9, 9);
		g.drawString(mc.font, s, x + 11, y, (int) (0xC0 + 0x3F * Math.sin(now / 180.0)) << 24 | 0xF08A40, true);
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

	/**
	 * The others in your party, a card each along the top: a big face on a dark plate so it reads over anything, health under it going
	 * from green through amber to red, and the plate's rim beating red when they're nearly dead. Dimmed when they're far off, dark when
	 * they're offline, an ember on the leader's corner, a lit rim round your heal target. Holding the player list key names them.
	 */
	private static void party(GuiGraphics g, Minecraft mc, int x, int y, boolean named) {
		// as many across as fit before the compass, the rest on a row under them
		int across = Math.max(1, (g.guiWidth() / 2 - QuestHud.W / 2 - x) / MEMBER_STEP), rows = (Net.clientParty.size() + across - 1) / across;
		int top = y, ty = y + rows * MEMBER_ROW + 2, i = 0;
		long now = System.currentTimeMillis();
		for (Net.PartyMember m : Net.clientParty) {
			int fx = x + i % across * MEMBER_STEP;
			y = top + i / across * MEMBER_ROW;
			i++;
			boolean aimed = m.name().equals(CurioKeys.healTarget);
			float hp = m.online() ? Mth.clamp(m.health() / Math.max(1, m.max()), 0, 1) : 0;
			boolean dying = m.online() && hp < 0.3f;
			g.fill(fx - 2, y - 2, fx + MEMBER_FACE + 2, y + MEMBER_FACE + MEMBER_H + 3, 0xE0050404);
			int beat = (int) (0xA0 + 0x5F * Math.sin(now / 160.0)) << 24 | 0xE0301C;
			g.renderOutline(fx - 2, y - 2, MEMBER_FACE + 4, MEMBER_FACE + MEMBER_H + 5, aimed ? AshUi.EMBER_LT : dying ? beat : 0xFF3D3833);
			PartyScreen.face(g, mc, m.name(), fx, y, MEMBER_FACE);
			if (!m.online() || !m.near()) g.fill(fx, y, fx + MEMBER_FACE, y + MEMBER_FACE, m.online() ? 0x40000000 : 0xB0000000);
			if (m.leader()) {
				g.fill(fx + MEMBER_FACE - 6, y, fx + MEMBER_FACE, y + 6, 0xFF050404);
				g.fill(fx + MEMBER_FACE - 5, y, fx + MEMBER_FACE, y + 5, AshUi.EMBER_C);
			}
			int by = y + MEMBER_FACE + 1;
			g.fill(fx, by, fx + MEMBER_FACE, by + MEMBER_H, 0xFF2A1210);
			if (hp > 0) g.fill(fx, by, fx + Math.max(1, Math.round(MEMBER_FACE * hp)), by + MEMBER_H, hp > 0.6f ? 0xFF58C848 : hp > 0.3f ? 0xFFE8A82C : 0xFFE8402C);
			if (named) {
				String life = m.online() ? "  " + Math.round(m.health()) + " / " + Math.round(m.max()) : "  offline";
				g.drawString(mc.font, m.name() + life, x, ty, aimed ? AshUi.EMBER_LT : !m.online() ? 0xFF6F685D : AshUi.TEXT, true);
				ty += 10;
			}
		}
	}
}
