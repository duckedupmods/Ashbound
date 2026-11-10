package com.snoringwalrus.ashbound;

import java.util.List;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;

import javax.annotation.Nullable;
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
	private static final Map<String, double[]> ROLE_AT = new HashMap<>(); // "role:rank" -> that role's target health, hit (pass 13)
	private static final Map<String, Integer> BAND_TOP = new HashMap<>();
	private static final Map<String, Double> CROWD = new HashMap<>();
	private static double partyHp = 0.15, partyRoadHp = 0.15, partyBossDmg = 0.08, partyGateDmg = 0.04, partySoloBoss = 0, partyRadius = 32, partyShare = 0.25;
	private static double armourK = 40, toughPer = 20;
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
			if (o.has("rank_role"))
				for (Map.Entry<String, JsonElement> e : o.getAsJsonObject("rank_role").entrySet())
					for (Map.Entry<String, JsonElement> r : e.getValue().getAsJsonObject().entrySet()) {
						JsonArray a = r.getValue().getAsJsonArray();
						ROLE_AT.put(r.getKey() + ":" + e.getKey(), new double[] {a.get(0).getAsDouble(), a.get(1).getAsDouble(), a.size() > 2 ? a.get(2).getAsDouble() : 0});
					}
			for (Map.Entry<String, JsonElement> e : o.getAsJsonObject("band_top").entrySet()) BAND_TOP.put(e.getKey(), e.getValue().getAsInt());
			for (Map.Entry<String, JsonElement> e : o.getAsJsonObject("crowd").entrySet()) CROWD.put(e.getKey(), e.getValue().getAsDouble());
			JsonObject lv = o.getAsJsonObject("levels");
			levelA = lv.get("a").getAsDouble();
			levelP = lv.get("p").getAsDouble();
			maxLevel = lv.get("max").getAsInt();
			hpPerLevel = o.getAsJsonObject("player").get("hp_per_level").getAsDouble();
			armourK = o.getAsJsonObject("player").get("armour_k").getAsDouble();
			toughPer = o.getAsJsonObject("player").get("tough_per").getAsDouble();
			JsonObject p = o.getAsJsonObject("party");
			partyHp = p.get("hp_per_player").getAsDouble();
			partyRoadHp = p.get("road_hp_per_player").getAsDouble();
			partyBossDmg = p.get("boss_dmg_per_player").getAsDouble();
			partyGateDmg = p.get("gate_dmg_per_player").getAsDouble();
			partySoloBoss = p.has("solo_boss_dmg") ? p.get("solo_boss_dmg").getAsDouble() : 0;
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

	/** Minecraft caps max health at 1024 and armour at 30; the solved bosses need more health (balance.py: F bosses ~2000, more in a party), a set of
	 * rank S plate more armour. The caps are raised for good, on both sides (the client clamps the same attributes). Found by SelfTest.balance */
	static void raiseCaps() {
		try {
			java.lang.reflect.Field f = net.neoforged.fml.util.ObfuscationReflectionHelper.findField(
					net.minecraft.world.entity.ai.attributes.RangedAttribute.class, "maxValue");
			f.setDouble(Attributes.MAX_HEALTH.value(), 1_000_000);
			f.setDouble(Attributes.ARMOR.value(), 1_000_000);
		} catch (Exception e) {
			Ashbound.LOG.error("couldn't raise the health and armour caps; bosses stop at 1024, armour at 30", e);
		}
	}

	static void register() {
		raiseCaps();
		NeoForge.EVENT_BUS.addListener((LivingIncomingDamageEvent e) -> {
			if (e.getSource().getEntity() instanceof Player && e.getEntity() instanceof Mob m) party(m);
			if (e.getEntity() instanceof Player p) {
				if (e.getSource().getEntity() instanceof Mob m) e.setAmount(e.getAmount() * crowded(p, m));
				armour(e, p);
			}
		});
	}

	/** What a player's armour lets through: every armourK of it is one more health bar, with nothing that runs out at the top the way vanilla's does at 20. */
	public static float kept(Player p) {
		return kept(p.getAttributeValue(Attributes.ARMOR), p.getAttributeValue(Attributes.ARMOR_TOUGHNESS));
	}

	static float kept(double armour, double toughness) {
		return (float) (armourK / (armourK + armour * (1 + toughness / toughPer)));
	}

	/** Takes vanilla's armour off a player's hit and puts ours on. A monster's spell counts as a blow, though vanilla's armour would let it through. */
	private static void armour(LivingIncomingDamageEvent e, Player p) {
		boolean counts = !e.getSource().is(net.minecraft.tags.DamageTypeTags.BYPASSES_ARMOR) || e.getSource().getEntity() instanceof Mob;
		e.getContainer().addModifier(net.neoforged.neoforge.common.damagesource.DamageContainer.Reduction.ARMOR,
				(c, vanilla) -> counts ? c.getNewDamage() * (1 - kept(p)) : vanilla);
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
		double[] step = step(own, to);
		if (step == null) return;
		double hp = step[0], hit = step[1];
		shrink(m.getAttribute(Attributes.MAX_HEALTH), hp);
		shrink(m.getAttribute(Attributes.ATTACK_DAMAGE), hit);
		shrink(m.getAttribute(Attributes.ARMOR), step[2]);
		m.setHealth(m.getMaxHealth());
		m.getPersistentData().putString(SOFT, to);
		m.getPersistentData().putDouble(SOFT_HP, hp);
	}

	/** One of our monsters made a monster of another rank (up or down): health, hit and armour as that rank's plain monster
	 * stands to its own, and paid for like it (Encounters' deserters keep to the party's rank). */
	static void atRank(Mob m, String kind, String to) {
		Mult own = solved(kind);
		if (own == null || own.rank().equals(to)) return;
		double[] step = step(own, to);
		if (step == null) return;
		double hp = step[0], hit = step[1];
		shrink(m.getAttribute(Attributes.MAX_HEALTH), hp);
		shrink(m.getAttribute(Attributes.ATTACK_DAMAGE), hit);
		shrink(m.getAttribute(Attributes.ARMOR), step[2]);
		m.setHealth(m.getMaxHealth());
		m.getPersistentData().putString(SOFT, to);
		m.getPersistentData().putDouble(SOFT_HP, hp);
	}

	/** health and hit from a monster's own rank to another: as its role's target there stands to its role's target at home (a boss climbs
	 * the ranks faster than a plain monster does), else as the plain monsters do */
	@Nullable
	private static double[] step(Mult own, String to) {
		double[] from = ROLE_AT.get(own.role() + ":" + own.rank()), now = ROLE_AT.get(own.role() + ":" + to);
		if (from == null || now == null) {
			from = NORMAL.get(own.rank());
			now = NORMAL.get(to);
		}
		if (from == null || now == null) return null;
		// armour follows the role's own armour there (pass 13: it followed the hit, so a boss moved up three ranks wore 3.5x its armour)
		double arm = from.length > 2 && from[2] > 0 && now[2] > 0 ? now[2] / from[2] : now[1] / from[1];
		return new double[] {now[0] / from[0], now[1] / from[1], arm};
	}

	private static void shrink(AttributeInstance a, double to) {
		if (a != null) a.addPermanentModifier(new AttributeModifier(SOFTENED, to - 1, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL));
	}

	/** the rank a kill pays at */
	static String paysAs(LivingEntity e, String own) {
		String r = e.getPersistentData().getString(SOFT);
		return r.isEmpty() ? own : r;
	}

	/** Past a rank above your party's, a monster pays as one of that rank would: this share of what it's worth. */
	static double paysUpTo(String rank, int party) {
		int top = Math.min(party + 1, LADDER.length() - 1), own = LADDER.indexOf(rank);
		if (own <= top) return 1;
		String to = LADDER.substring(top, top + 1);
		double[] from = NORMAL.get(rank), now = NORMAL.get(to);
		return from == null || now == null ? 1 : now[0] * ash(to) / (from[0] * ash(rank));
	}

	/** What the Party screen says about a party of n. */
	public static List<String> scaling(int n) {
		int hp = (int) Math.round(partyHp * 100 * (n - 1)), hit = (int) Math.round(partyGateDmg * 100 * (n - 1)), boss = (int) Math.round(partyBossDmg * 100 * (n - 1));
		return List.of("In a gate, " + n + (n == 1 ? " player: " : " players: ") + "monsters +" + hp + "% health, +" + hit + "% damage, bosses +" + boss + "%",
				"Ash and coins each: " + Math.round(share(n) * 100) + "% of a kill",
				"Materials, gear and boss weapons: everyone rolls their own",
				"Your rank sets which gates open and what you find");
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
		// a gate, a boss arena or a summoned overworld boss is a fight the party came for: a gate's scaling (pass 13); the road's is lighter
		boolean road = m.level().dimension() != Lairs.GATES && !BossArenas.isArena(m.level().dimension()) && !m.getTags().contains(WorldBosses.TAG);
		m.getPersistentData().putInt(SEEN, n);
		float share = m.getHealth() / m.getMaxHealth();
		grow(m.getAttribute(Attributes.MAX_HEALTH), (road ? partyRoadHp : partyHp) * (n - 1));
		// alone, a gate, arena or summoned boss hits softer (pass 15: one player takes every blow; balance_mc.py)
		double hit = road ? 0 : n == 1 && boss(m) ? partySoloBoss : (boss(m) ? partyBossDmg : partyGateDmg) * (n - 1);
		grow(m.getAttribute(Attributes.ATTACK_DAMAGE), hit);
		m.setHealth(m.getMaxHealth() * share);
	}

	private static void grow(AttributeInstance a, double by) {
		if (a == null) return;
		a.removeModifier(PARTY);
		if (by != 0) a.addPermanentModifier(new AttributeModifier(PARTY, by, AttributeModifier.Operation.ADD_MULTIPLIED_BASE));
	}
}
