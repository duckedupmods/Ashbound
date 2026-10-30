package com.snoringwalrus.ashbound.client;

import java.util.Set;

import com.snoringwalrus.ashbound.Ashbound;
import com.snoringwalrus.ashbound.Levels;
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
 * Health, stamina and mana, top left in place of the hearts, the hunger row and Epic Fight's stamina bar: an iron socket
 * with your level, three bars that grow as their maximum does, and armour and food under them. A hit leaves a pale
 * chunk that drains after a moment; hold the player list key (TAB) for the numbers. Your party goes under them, a name
 * and a thin bar each. Also wires up the compass and the screens the server asks for.
 */
public final class VitalsHud {
	private VitalsHud() {}

	private static final int X = 6, Y = 6, SOCKET = 25, GAP = 2, HP_H = 11, BAR_H = 6, MEMBER_W = 80, MEMBER_H = 3;
	private static final float HOLD_MS = 500, DRAIN = 0.4f, FOLLOW = 14;
	private static final ResourceLocation ARMOUR = ResourceLocation.withDefaultNamespace("hud/armor_full"),
			FOOD = ResourceLocation.withDefaultNamespace("hud/food_full");
	/** What this draws instead. */
	private static final Set<ResourceLocation> HIDDEN = Set.of(VanillaGuiLayers.PLAYER_HEALTH, VanillaGuiLayers.ARMOR_LEVEL, VanillaGuiLayers.FOOD_LEVEL,
			VanillaGuiLayers.AIR_LEVEL, ResourceLocation.fromNamespaceAndPath("epicfight", "stamina_bar"));

	private static final Bar HP = new Bar(), STAMINA = new Bar(), MANA = new Bar();
	private static long last;

	/** A bar's eased fill and the pale chunk behind it. */
	private static final class Bar {
		float shown = 1, trail = 1, was = 1;
		long hold;

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
			if (HIDDEN.contains(e.getName())) e.setCanceled(true);
		});
		Net.onForge = m -> Minecraft.getInstance().setScreen(new ForgeScreen(m.pos(), m.known()));
		Net.onForgeStart = ForgeStrikeScreen::open;
		Net.onForgeEcho = ForgeScene::echo;
		Net.onColdWake = ColdScene::play;
		Net.onJournal = QuestScreen::state;
		Net.onGuildJobs = QuestScreen::jobs;
		QuestHud.hooks(bus);
		SpellFx.hooks();
		NeoForge.EVENT_BUS.addListener((ClientPlayerNetworkEvent.LoggingOut e) -> Net.clientParty = java.util.List.of());
	}

	/** Long enough to tell you've grown, never the width of the screen: a little more each time the maximum doubles. */
	private static int length(float max, float start) {
		return Mth.clamp(Math.round(110 + 16 * (float) (Math.log(max / start) / Math.log(2))), 90, 190);
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

	private static void bar(GuiGraphics g, int x, int y, int w, int h, Bar b, int top, int bottom, int edge, int trough) {
		frame(g, x, y, w, h);
		g.fill(x, y, x + w, y + h, trough);
		int fw = Math.round(w * Mth.clamp(b.shown, 0, 1)), tw = Math.round(w * Mth.clamp(b.trail, 0, 1));
		if (tw > fw) g.fill(x + fw, y, x + tw, y + h, 0xFFE8C8A0);
		if (fw <= 0) return;
		g.fillGradient(x, y, x + fw, y + h, top, bottom);
		g.fill(x, y, x + fw, y + 1, edge);
		if (fw < w) g.fill(x + fw - 1, y, x + fw, y + h, edge);
	}

	private static void draw(GuiGraphics g, DeltaTracker dt) {
		Minecraft mc = Minecraft.getInstance();
		LocalPlayer p = mc.player;
		if (p == null || mc.options.hideGui || mc.gameMode == null || !mc.gameMode.canHurtPlayer()) return;
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

		// your level, in the socket; lit while one is ready to buy
		boolean ready = Levels.clientNext > 0 && Levels.clientAsh >= Levels.clientNext;
		frame(g, X, Y, SOCKET, SOCKET);
		g.fill(X, Y, X + SOCKET, Y + SOCKET, 0xFF16120F);
		if (ready) g.fill(X, Y, X + SOCKET, Y + SOCKET, (int) (0x50 + 0x30 * Math.sin(now / 300.0)) << 24 | 0xE8742C);
		g.fill(X + 3, Y + SOCKET - 2, X + SOCKET - 3, Y + SOCKET - 1, AshUi.EMBER_C);
		String lv = String.valueOf(Levels.clientLevel);
		g.drawString(mc.font, lv, X + (SOCKET - mc.font.width(lv)) / 2 + 1, Y + (SOCKET - 8) / 2, AshUi.EMBER_LT, true);

		// the bars
		int bx = X + SOCKET + 5, y = Y, hw = length(maxHp, 20), sw = length(maxSt, 15), mw = length(maxMana, 100);
		boolean poison = p.hasEffect(MobEffects.POISON), wither = p.hasEffect(MobEffects.WITHER);
		bar(g, bx, y, hw, HP_H, HP, poison ? 0xFF8EA83A : wither ? 0xFF4A4440 : 0xFFD8402C, poison ? 0xFF46601A : wither ? 0xFF201C1A : 0xFF7A1410,
				poison ? 0xFFD4E88A : wither ? 0xFF8A8076 : 0xFFFF9A7A, 0xFF1E0E0C);
		if (hp < 0.25f) {   // close to death, the bar's frame beats
			int beat = (int) (0x70 + 0x60 * Math.sin(now / 160.0)) << 24 | 0xE0301C;
			g.renderOutline(bx - 1, y - 1, hw + 2, HP_H + 2, beat);
		}
		float absorb = p.getAbsorptionAmount();
		if (absorb > 0) {
			int aw = Math.min(hw, Math.round(hw * absorb / maxHp));
			g.fill(bx, y, bx + aw, y + 2, 0xFFFFD24A);
		}
		String life = Math.round(p.getHealth()) + (absorb > 0 ? "+" + Math.round(absorb) : "") + " / " + Math.round(maxHp);
		g.drawString(mc.font, life, bx + (hw - mc.font.width(life)) / 2, y + 2, AshUi.TEXT, true);

		y += HP_H + GAP + 1;
		bar(g, bx, y, sw, BAR_H, STAMINA, 0xFFA4C840, 0xFF4A6A18, 0xFFE0F090, 0xFF141A0C);
		if (numbers) g.drawString(mc.font, Math.round(patch == null ? maxSt : patch.getStamina()) + " / " + Math.round(maxSt), bx + sw + 5, y - 1, 0xFFC8DC8A, true);
		y += BAR_H + GAP + 1;
		bar(g, bx, y, mw, BAR_H, MANA, 0xFF5AA0FF, 0xFF1E3E9A, 0xFFB8DCFF, 0xFF141A2A);
		if (numbers) g.drawString(mc.font, Math.round(Spells.clientMana) + " / " + Math.round(maxMana), bx + mw + 5, y - 1, 0xFF9CC8FF, true);

		// armour, food, and breath while it's running out
		y = Y + SOCKET + 5;
		int tx = X - 1;
		int armour = p.getArmorValue();
		if (armour > 0) {
			g.blitSprite(ARMOUR, tx, y, 9, 9);
			String s = String.valueOf(armour);
			g.drawString(mc.font, s, tx + 11, y + 1, AshUi.BODY, true);
			tx += 11 + mc.font.width(s) + 7;
		}
		int food = p.getFoodData().getFoodLevel();
		g.blitSprite(FOOD, tx, y, 9, 9);
		String s = String.valueOf(food);
		g.drawString(mc.font, s, tx + 11, y + 1, food <= 6 ? AshUi.BAD : AshUi.BODY, true);
		tx += 11 + mc.font.width(s) + 7;
		int air = p.getAirSupply(), maxAir = p.getMaxAirSupply();
		if (air < maxAir) {
			int w = 50, ay = y + 2;
			frame(g, tx, ay, w, 4);
			g.fill(tx, ay, tx + w, ay + 4, 0xFF102028);
			g.fill(tx, ay, tx + Math.round(w * Math.max(0, air) / (float) maxAir), ay + 4, 0xFF7ADCF0);
		}
		party(g, mc, X, y + 15);
	}

	/** The others in your party: dim when they're far off, grey when they're offline, an ember by the leader. */
	private static void party(GuiGraphics g, Minecraft mc, int x, int y) {
		for (Net.PartyMember m : Net.clientParty) {
			int tx = x;
			if (m.leader()) {
				g.fill(tx, y + 2, tx + 3, y + 5, AshUi.EMBER_C);
				tx += 6;
			}
			g.drawString(mc.font, m.name(), tx, y, !m.online() ? 0xFF6F685D : m.near() ? AshUi.TEXT : AshUi.BODY, true);
			y += 10;
			frame(g, x, y, MEMBER_W, MEMBER_H);
			g.fill(x, y, x + MEMBER_W, y + MEMBER_H, 0xFF1E0E0C);
			if (m.online()) g.fill(x, y, x + Math.round(MEMBER_W * Mth.clamp(m.health() / Math.max(1, m.max()), 0, 1)), y + MEMBER_H, 0xFFD8402C);
			y += MEMBER_H + 7;
		}
	}
}
