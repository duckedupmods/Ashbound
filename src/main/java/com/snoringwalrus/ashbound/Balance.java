package com.snoringwalrus.ashbound;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;

/**
 * The numbers tools/balance.py solves (docs/BALANCE.md): each monster's health and damage on top of its own,
 * tower foremen's health, every armour class's armour per rank, and how a monster grows for a party.
 * Change them in the tool and run --solve, not here.
 */
public final class Balance {
	private Balance() {}

	record Mult(double hp, double dmg, String role, String rank) {}

	private static final Map<String, Mult> MOBS = new HashMap<>();
	private static final Map<String, Double> FOREMAN = new HashMap<>();
	private static final Map<String, double[]> ARMOUR = new HashMap<>(); // "heavy:C" -> armour, toughness
	private static final Map<String, Double> ASH = new HashMap<>(), COINS = new HashMap<>(); // per point of health, by rank
	private static double partyHp = 0.4, partyBossDmg = 0.05, partyRadius = 32;
	static double levelA = 80, levelP = 1.55, hpPerLevel = 0.4;
	static int maxLevel = 100;

	static {
		try (InputStream in = Balance.class.getResourceAsStream("/ashbound/balance.json")) {
			JsonObject o = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
			for (Map.Entry<String, JsonElement> e : o.getAsJsonObject("mobs").entrySet()) {
				JsonArray a = e.getValue().getAsJsonArray();
				MOBS.put(e.getKey(), new Mult(a.get(0).getAsDouble(), a.get(1).getAsDouble(), a.get(2).getAsString(), a.get(3).getAsString()));
			}
			for (Map.Entry<String, JsonElement> e : o.getAsJsonObject("foreman_hp").entrySet())
				FOREMAN.put(e.getKey(), e.getValue().getAsDouble());
			for (Map.Entry<String, JsonElement> c : o.getAsJsonObject("armour").entrySet())
				for (Map.Entry<String, JsonElement> r : c.getValue().getAsJsonObject().entrySet()) {
					JsonArray a = r.getValue().getAsJsonArray();
					ARMOUR.put(c.getKey() + ":" + r.getKey(), new double[] {a.get(0).getAsDouble(), a.get(1).getAsDouble()});
				}
			for (Map.Entry<String, JsonElement> e : o.getAsJsonObject("ash_per_hp").entrySet()) ASH.put(e.getKey(), e.getValue().getAsDouble());
			for (Map.Entry<String, JsonElement> e : o.getAsJsonObject("coins_per_hp").entrySet()) COINS.put(e.getKey(), e.getValue().getAsDouble());
			JsonObject lv = o.getAsJsonObject("levels");
			levelA = lv.get("a").getAsDouble();
			levelP = lv.get("p").getAsDouble();
			maxLevel = lv.get("max").getAsInt();
			hpPerLevel = o.getAsJsonObject("player").get("hp_per_level").getAsDouble();
			JsonObject p = o.getAsJsonObject("party");
			partyHp = p.get("hp_per_player").getAsDouble();
			partyBossDmg = p.get("boss_dmg_per_player").getAsDouble();
			partyRadius = p.get("radius").getAsDouble();
		} catch (Exception e) {
			Ashbound.LOG.error("balance.json not loaded, monsters keep their own numbers", e);
		}
	}

	static Mult mob(String id) {
		return MOBS.getOrDefault(id, new Mult(1, 1, "normal", "C"));
	}

	/** one of the solved monsters (null for anything else: townsfolk, vanilla mobs) */
	static Mult solved(String id) {
		return MOBS.get(id);
	}

	static double ash(String rank) {
		return ASH.getOrDefault(rank, 0.0);
	}

	static double coins(String rank) {
		return COINS.getOrDefault(rank, 0.0);
	}

	static double radius() {
		return partyRadius;
	}

	/** a tower foreman's health, or twice its own if the tower isn't solved */
	static double foreman(String tower, double own) {
		return FOREMAN.getOrDefault(tower, own * 2);
	}

	/** a full set's armour and toughness for a class at a rank (null: use the old ladder) */
	static double[] armour(String cls, char rank) {
		return ARMOUR.get(cls + ":" + rank);
	}

	// --- party scaling: a monster grows with the players around it the first time each new one joins the fight ---

	private static final ResourceLocation PARTY = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "party");
	private static final String SEEN = "ashbound_party";

	/** Minecraft caps max health at 1024; the solved bosses need more (balance.py: F bosses ~2000, more in a party).
	 * The cap is raised for good, on both sides (the client clamps the same attribute). Found by SelfTest.balance */
	static void raiseHealthCap() {
		try {
			java.lang.reflect.Field f = net.neoforged.fml.util.ObfuscationReflectionHelper.findField(
					net.minecraft.world.entity.ai.attributes.RangedAttribute.class, "maxValue");
			f.setDouble(net.minecraft.world.entity.ai.attributes.Attributes.MAX_HEALTH.value(), 1_000_000);
		} catch (Exception e) {
			Ashbound.LOG.error("couldn't raise the max health cap; bosses stop at 1024", e);
		}
	}

	static void register() {
		raiseHealthCap();
		NeoForge.EVENT_BUS.addListener((LivingIncomingDamageEvent e) -> {
			if (e.getSource().getEntity() instanceof Player && e.getEntity() instanceof Mob m) party(m);
		});
	}

	private static void party(Mob m) {
		ResourceLocation id = BuiltInRegistries.ENTITY_TYPE.getKey(m.getType());
		if (!id.getNamespace().equals(Ashbound.ID) || !MOBS.containsKey(id.getPath()) || m.getTags().contains(Spells.THRALL)) return;
		int n = m.level().getEntitiesOfClass(Player.class, m.getBoundingBox().inflate(partyRadius), p -> !p.isSpectator()).size();
		if (n <= m.getPersistentData().getInt(SEEN)) return;
		m.getPersistentData().putInt(SEEN, n);
		float share = m.getHealth() / m.getMaxHealth();
		grow(m.getAttribute(Attributes.MAX_HEALTH), partyHp * (n - 1));
		if ("boss".equals(MOBS.get(id.getPath()).role())) grow(m.getAttribute(Attributes.ATTACK_DAMAGE), partyBossDmg * (n - 1));
		m.setHealth(m.getMaxHealth() * share);
	}

	private static void grow(AttributeInstance a, double by) {
		if (a == null) return;
		a.removeModifier(PARTY);
		if (by > 0) a.addPermanentModifier(new AttributeModifier(PARTY, by, AttributeModifier.Operation.ADD_MULTIPLIED_BASE));
	}
}
