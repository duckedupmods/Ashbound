package com.snoringwalrus.ashbound;

import java.util.List;
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
import net.minecraft.world.entity.LivingEntity;
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
	private static final Map<String, double[]> NORMAL = new HashMap<>(); // a rank's plain monster: health, hit
	private static final Map<String, Integer> BAND_TOP = new HashMap<>();
	private static final Map<String, Double> CROWD = new HashMap<>();
	private static double partyHp = 0.15, partyRoadHp = 0.15, partyBossDmg = 0.08, partyGateDmg = 0.04, partyRadius = 32, partyShare = 0.25;
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
			for (Map.Entry<String, JsonElement> e : o.getAsJsonObject("rank_normal").entrySet()) {
				JsonArray a = e.getValue().getAsJsonArray();
				NORMAL.put(e.getKey(), new double[] {a.get(0).getAsDouble(), a.get(1).getAsDouble()});
			}
			for (Map.Entry<String, JsonElement> e : o.getAsJsonObject("band_top").entrySet()) BAND_TOP.put(e.getKey(), e.getValue().getAsInt());
			for (Map.Entry<String, JsonElement> e : o.getAsJsonObject("crowd").entrySet()) CROWD.put(e.getKey(), e.getValue().getAsDouble());
			JsonObject lv = o.getAsJsonObject("levels");
			levelA = lv.get("a").getAsDouble();
			levelP = lv.get("p").getAsDouble();
			maxLevel = lv.get("max").getAsInt();
			hpPerLevel = o.getAsJsonObject("player").get("hp_per_level").getAsDouble();
			JsonObject p = o.getAsJsonObject("party");
			partyHp = p.get("hp_per_player").getAsDouble();
			partyRoadHp = p.get("road_hp_per_player").getAsDouble();
			partyBossDmg = p.get("boss_dmg_per_player").getAsDouble();
			partyGateDmg = p.get("gate_dmg_per_player").getAsDouble();
			partyRadius = p.get("radius").getAsDouble();
			partyShare = p.get("reward_share").getAsDouble();
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

	/** What each of n players near a kill gets of its Ash and coins: a party kills far faster for what a monster grows, so it still comes out ahead (about 1.5x solo) without running away from the game. */
	static double share(int n) {
		return 1 / (1 + partyShare * Math.max(0, n - 1));
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
			if (e.getEntity() instanceof Player p && e.getSource().getEntity() instanceof Mob m) e.setAmount(e.getAmount() * crowded(p, m));
		});
	}

	// --- camps: what keeps a crowd of monsters from taking you apart ---

	private static final String LADDER = "FEDCBAS", SOFT = "ashbound_soft", SOFT_HP = "ashbound_soft_hp";
	private static final ResourceLocation SOFTENED = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "softened");
	private static final long CROWD_TICKS = 20;
	private static final Map<Player, long[]> LAST_BLOW = new java.util.WeakHashMap<>();

	/** the rank a level plays at */
	static String rankAt(int level) {
		for (char r : LADDER.toCharArray())
			if (level < BAND_TOP.getOrDefault(String.valueOf(r), 0)) return String.valueOf(r);
		return "S";
	}

	/** A place outside a gate is never more than a rank above the best player near it: anything else there comes down to that rank, and pays like it. Walk into the void castle at level 5 and it's only a hard fight. */
	static void soften(Mob m, String kind, int level) {
		Mult own = solved(kind);
		if (own == null) return;
		int top = Math.min(LADDER.indexOf(rankAt(level)) + 1, LADDER.length() - 1);
		if (LADDER.indexOf(own.rank()) <= top) return;
		String to = LADDER.substring(top, top + 1);
		double[] from = NORMAL.get(own.rank()), now = NORMAL.get(to);
		if (from == null || now == null) return;
		double hp = now[0] / from[0], hit = now[1] / from[1];
		shrink(m.getAttribute(Attributes.MAX_HEALTH), hp);
		shrink(m.getAttribute(Attributes.ATTACK_DAMAGE), hit);
		shrink(m.getAttribute(Attributes.ARMOR), hit);
		m.setHealth(m.getMaxHealth());
		m.getPersistentData().putString(SOFT, to);
		m.getPersistentData().putDouble(SOFT_HP, hp);
	}

	private static void shrink(AttributeInstance a, double to) {
		if (a != null) a.addPermanentModifier(new AttributeModifier(SOFTENED, to - 1, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL));
	}

	/** the rank a kill pays at */
	static String paysAs(LivingEntity e, String own) {
		String r = e.getPersistentData().getString(SOFT);
		return r.isEmpty() ? own : r;
	}

	/** how much of its own health a kill is paid for */
	static double paysFor(LivingEntity e) {
		return e.getPersistentData().contains(SOFT_HP) ? e.getPersistentData().getDouble(SOFT_HP) : 1;
	}

	/** One monster hits you in full; the others that land inside the same second do a share of it. Bosses always hit in full. */
	private static float crowded(Player p, Mob by) {
		ResourceLocation id = BuiltInRegistries.ENTITY_TYPE.getKey(by.getType());
		Mult m = id.getNamespace().equals(Ashbound.ID) ? solved(id.getPath()) : null;
		if (id.getNamespace().equals(Ashbound.ID) && m == null || boss(by)) return 1;
		return crowded(p, by.getId(), p.level().getGameTime(), CROWD.getOrDefault(m == null ? "C" : paysAs(by, m.rank()), 1.0));
	}

	static float crowded(Player p, int by, long now, double share) {
		long[] last = LAST_BLOW.get(p);
		if (last != null && last[0] != by && now - last[1] < CROWD_TICKS) return (float) share;
		LAST_BLOW.put(p, new long[] {by, now});
		return 1;
	}

	/** Our monsters, and every other mod's: Cataclysm's and the rest grow for a party too. Vanilla's don't. */
	static boolean scales(Mob m) {
		ResourceLocation id = BuiltInRegistries.ENTITY_TYPE.getKey(m.getType());
		if (m.getTags().contains(Spells.THRALL)) return false;
		if (id.getNamespace().equals(Ashbound.ID)) return MOBS.containsKey(id.getPath());
		return !id.getNamespace().equals("minecraft") && m instanceof net.minecraft.world.entity.monster.Enemy;
	}

	/** Another mod's boss: tagged as one, or simply as big as one. */
	private static final double BOSS_HEALTH = 150;

	static boolean boss(Mob m) {
		ResourceLocation id = BuiltInRegistries.ENTITY_TYPE.getKey(m.getType());
		if (id.getNamespace().equals(Ashbound.ID)) return "boss".equals(MOBS.get(id.getPath()).role());
		return m.getType().is(net.neoforged.neoforge.common.Tags.EntityTypes.BOSSES) || m.getAttributeBaseValue(Attributes.MAX_HEALTH) >= BOSS_HEALTH;
	}

	private static void party(Mob m) {
		if (!scales(m)) return;
		List<Player> there = m.level().getEntitiesOfClass(Player.class, m.getBoundingBox().inflate(partyRadius), p -> !p.isSpectator());
		int n = there.size();
		if (n <= m.getPersistentData().getInt(SEEN)) return;
		boolean road = m.level().dimension() != Lairs.GATES;
		m.getPersistentData().putInt(SEEN, n);
		float share = m.getHealth() / m.getMaxHealth();
		grow(m.getAttribute(Attributes.MAX_HEALTH), (road ? partyRoadHp : partyHp) * (n - 1));
		grow(m.getAttribute(Attributes.ATTACK_DAMAGE), road ? 0 : (boss(m) ? partyBossDmg : partyGateDmg) * (n - 1));
		m.setHealth(m.getMaxHealth() * share);
	}

	private static void grow(AttributeInstance a, double by) {
		if (a == null) return;
		a.removeModifier(PARTY);
		if (by > 0) a.addPermanentModifier(new AttributeModifier(PARTY, by, AttributeModifier.Operation.ADD_MULTIPLIED_BASE));
	}
}
