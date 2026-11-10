package com.snoringwalrus.ashbound;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import yesman.epicfight.api.collider.MultiOBBCollider;
import yesman.epicfight.api.collider.Collider;
import yesman.epicfight.api.animation.AnimationManager.AnimationAccessor;
import yesman.epicfight.api.animation.types.StaticAnimation;
import yesman.epicfight.gameasset.Animations;
import yesman.epicfight.world.capabilities.entitypatch.MobPatch;
import yesman.epicfight.world.entity.ai.goal.CombatBehaviors;
import yesman.epicfight.world.entity.ai.goal.CombatBehaviors.Behavior;
import yesman.epicfight.world.entity.ai.goal.CombatBehaviors.BehaviorSeries;

/**
 * How each gate monster fights (/ashbound/mob_moves.json, written by tools/mob_moves.py): its stance - the weapon it
 * swings, so which of Epic Fight's combos it strings together and the grip it holds (an unseen item of that weapon
 * type, so the blows land where the blade goes) - and its own skills (MobSkills). Every reach is grown with the
 * monster's size and measured from its middle, the way Epic Fight measures: a big one swings from where it stands
 * instead of pressing up against you and staring.
 */
public final class MobMoves {
	private MobMoves() {}

	public record Skill(String name, String arg, int phase) {}

	public record Spec(String gate, String stance, List<Skill> skills, boolean shield) {}

	@SuppressWarnings("unchecked")
	private record Stance(String grip, boolean twoGrips, double reach, AnimationAccessor<? extends StaticAnimation>[][] combos,
			AnimationAccessor<? extends StaticAnimation> dash) {}

	private static final Spec PLAIN = new Spec("", "claw", List.of(), false);
	private static final Map<String, Spec> SPECS = load();
	private static final Map<String, Stance> STANCES = new HashMap<>();

	@SafeVarargs
	private static AnimationAccessor<? extends StaticAnimation>[] c(AnimationAccessor<? extends StaticAnimation>... a) {
		return a;
	}

	private static void stance(String name, String grip, boolean two, double reach, AnimationAccessor<? extends StaticAnimation> dash,
			AnimationAccessor<? extends StaticAnimation>[]... combos) {
		STANCES.put(name, new Stance(grip, two, reach, combos, dash));
	}

	/** Epic Fight fills its animation fields late, so the stances are put together the first time one is asked for. */
	private static synchronized void stances() {
		if (!STANCES.isEmpty()) return;
		stance("sword", "grip_sword", false, 2.2, Animations.SWORD_DASH,
				c(Animations.BIPED_MOB_ONEHAND1, Animations.BIPED_MOB_ONEHAND2), c(Animations.SWORD_AUTO1, Animations.SWORD_AUTO2, Animations.SWORD_AUTO3));
		stance("dual", "grip_sword", true, 2.3, Animations.SWORD_DUAL_DASH,
				c(Animations.BIPED_MOB_SWORD_DUAL1, Animations.BIPED_MOB_SWORD_DUAL2, Animations.BIPED_MOB_SWORD_DUAL3),
				c(Animations.SWORD_DUAL_AUTO1, Animations.SWORD_DUAL_AUTO2, Animations.SWORD_DUAL_AUTO3));
		stance("greatsword", "grip_greatsword", false, 2.9, Animations.GREATSWORD_DASH,
				c(Animations.GREATSWORD_AUTO1, Animations.GREATSWORD_AUTO2), c(Animations.BIPED_MOB_GREATSWORD));
		stance("longsword", "grip_longsword", false, 2.6, Animations.LONGSWORD_DASH,
				c(Animations.BIPED_MOB_LONGSWORD1, Animations.BIPED_MOB_LONGSWORD2), c(Animations.LONGSWORD_AUTO1, Animations.LONGSWORD_AUTO2, Animations.LONGSWORD_AUTO3));
		stance("rapier", "grip_uchigatana", false, 2.4, Animations.UCHIGATANA_DASH,
				c(Animations.BIPED_MOB_UCHIGATANA1, Animations.BIPED_MOB_UCHIGATANA2, Animations.BIPED_MOB_UCHIGATANA3),
				c(Animations.UCHIGATANA_AUTO1, Animations.UCHIGATANA_AUTO2, Animations.UCHIGATANA_AUTO3));
		stance("sabre", "grip_tachi", false, 2.5, Animations.TACHI_DASH,
				c(Animations.BIPED_MOB_TACHI), c(Animations.TACHI_AUTO1, Animations.TACHI_AUTO2, Animations.TACHI_AUTO3));
		stance("spear", "grip_spear", false, 3.2, Animations.SPEAR_DASH,
				c(Animations.BIPED_MOB_SPEAR_TWOHAND1, Animations.BIPED_MOB_SPEAR_TWOHAND2, Animations.BIPED_MOB_SPEAR_TWOHAND3),
				c(Animations.SPEAR_TWOHAND_AUTO1, Animations.SPEAR_TWOHAND_AUTO2));
		stance("dagger", "grip_dagger", false, 1.9, Animations.DAGGER_DASH,
				c(Animations.BIPED_MOB_DAGGER_ONEHAND1, Animations.BIPED_MOB_DAGGER_ONEHAND2, Animations.BIPED_MOB_DAGGER_ONEHAND3),
				c(Animations.DAGGER_AUTO1, Animations.DAGGER_AUTO2, Animations.DAGGER_AUTO3));
		stance("twin_daggers", "grip_dagger", true, 2.0, Animations.DAGGER_DUAL_DASH,
				c(Animations.BIPED_MOB_DAGGER_TWOHAND1, Animations.BIPED_MOB_DAGGER_TWOHAND2),
				c(Animations.DAGGER_DUAL_AUTO1, Animations.DAGGER_DUAL_AUTO2, Animations.DAGGER_DUAL_AUTO3, Animations.DAGGER_DUAL_AUTO4));
		stance("axe", "grip_axe", false, 2.2, Animations.AXE_DASH,
				c(Animations.VINDICATOR_SWING_AXE1, Animations.VINDICATOR_SWING_AXE2, Animations.VINDICATOR_SWING_AXE3), c(Animations.AXE_AUTO1, Animations.AXE_AUTO2));
		stance("twin_axes", "grip_axe", true, 2.2, Animations.AXE_DASH,
				c(Animations.VINDICATOR_SWING_AXE1, Animations.VINDICATOR_SWING_AXE2, Animations.VINDICATOR_SWING_AXE3),
				c(Animations.SWORD_DUAL_AUTO1, Animations.SWORD_DUAL_AUTO2, Animations.SWORD_DUAL_AUTO3));
		stance("maul", "grip_greatsword", false, 2.8, Animations.GREATSWORD_DASH,
				c(Animations.GREATSWORD_AUTO1, Animations.GREATSWORD_AUTO2), c(Animations.BIPED_MOB_GREATSWORD), c(Animations.VINDICATOR_SWING_AXE3));
		stance("fist", null, false, 1.9, Animations.FIST_DASH,
				c(Animations.FIST_AUTO1, Animations.FIST_AUTO2, Animations.FIST_AUTO3));
		stance("claw", null, false, 1.9, Animations.FIST_DASH,
				c(Animations.ZOMBIE_ATTACK1, Animations.ZOMBIE_ATTACK2, Animations.ZOMBIE_ATTACK3), c(Animations.FIST_AUTO1, Animations.FIST_AUTO2));
		stance("caster", "grip_spear", false, 2.4, null,
				c(Animations.BIPED_MOB_SPEAR_ONEHAND), c(Animations.BIPED_MOB_ONEHAND1));
		stance("tool", "grip_axe", false, 2.0, Animations.TOOL_DASH,
				c(Animations.TOOL_AUTO1, Animations.TOOL_AUTO2), c(Animations.BIPED_MOB_ONEHAND1, Animations.BIPED_MOB_ONEHAND2));
		stance("crawler", null, false, 1.9, null,
				c(Animations.SPIDER_ATTACK), c(Animations.SPIDER_JUMP_ATTACK));
		stance("crab", null, false, 2.2, null, c(CrabClips.CLAW));          // claws, low: never rears like a spider
	}

	private static Map<String, Spec> load() {
		Map<String, Spec> out = new HashMap<>();
		try (InputStream in = MobMoves.class.getResourceAsStream("/ashbound/mob_moves.json")) {
			if (in == null) return out;
			for (Map.Entry<String, JsonElement> e : JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject().entrySet()) {
				JsonObject o = e.getValue().getAsJsonObject();
				List<Skill> skills = new ArrayList<>();
				for (JsonElement s : o.getAsJsonArray("skills")) {
					JsonObject so = s.getAsJsonObject();
					skills.add(new Skill(so.get("name").getAsString(), so.get("arg").getAsString(), so.get("phase").getAsInt()));
				}
				out.put(e.getKey(), new Spec(o.get("gate").getAsString(), o.get("stance").getAsString(), skills, o.get("shield").getAsBoolean()));
			}
		} catch (Exception e) {
			Ashbound.LOG.error("monster moves not loaded", e);
		}
		return out;
	}

	static Spec of(GateMobs.Kind k) {
		return SPECS.getOrDefault(k.id(), PLAIN);
	}

	/** A crab: it swings its claws where a spider would bite or leap. */
	static boolean crab(GateMobs.Kind k) {
		return "crab".equals(of(k).stance());
	}

	static String gate(GateMobs.Kind k) {
		return of(k).gate();
	}

	private static Stance stance(GateMobs.Kind k) {
		stances();
		return STANCES.getOrDefault(of(k).stance(), STANCES.get(k.spider() ? "crawler" : "claw"));
	}

	/** How far its swings reach from its middle: the stance's, grown with its size, plus half its own width. */
	static double reach(GateMobs.Kind k) {
		if (k.reach() > 0) return k.reach() * k.scale() * 0.85 + k.w() * 0.5;
		return stance(k).reach() * Math.max(1.0, k.scale() * 0.85) + k.w() * 0.5;
	}

	/** A boss's chase, about a walking player's pace. A mob's ground speed goes with the square of its speed stat, so 0.29 is 3.7 blocks a second. */
	private static final double BOSS_PACE = 0.29;

	static double chase(GateMobs.Kind k) {
		return k.boss() ? Math.max(1.0, BOSS_PACE / k.speed()) : 1.0;
	}

	/** The biggest bosses often don't fit the pathfinder's way through trees: with no path, a boss just walks at you. */
	static void press(Mob m, GateMobs.Kind k) {
		LivingEntity t = m.getTarget();
		if (!k.boss() || t == null || !m.getNavigation().isDone() || MobSkills.busy(m) || m.distanceTo(t) <= stopAt(k)) return;
		m.getMoveControl().setWantedPosition(t.getX(), t.getY(), t.getZ(), chase(k));
	}

	private static final Map<GateMobs.Kind, Collider> COLLIDERS = new java.util.concurrent.ConcurrentHashMap<>();

	/** Its swing's hit box: as long as the weapon you see (tools/efskin.py), down the grip. Epic Fight scales it with the model. */
	static Collider collider(GateMobs.Kind k) {
		if (k.reach() <= 0) return null;
		return COLLIDERS.computeIfAbsent(k, x -> new MultiOBBCollider(3, 0.35, 0.5, x.reach() / 2, 0, 0, -x.reach() / 2));
	}

	static AnimationAccessor<? extends StaticAnimation> dash(GateMobs.Kind k) {
		Stance s = stance(k);
		return s.dash() != null ? s.dash() : s.combos()[0][0];
	}

	static AnimationAccessor<? extends StaticAnimation> opener(GateMobs.Kind k) {
		return stance(k).combos()[0][0];
	}

	/** Where the chase stops: a little inside its reach. */
	static double stopAt(GateMobs.Kind k) {
		return reach(k) * 0.7;
	}

	static int cooldown(String skill) {
		return switch (skill) {
			case "bolt" -> 50;
			case "dash", "pounce" -> 80;
			case "slam", "volley", "blink", "spin", "pull" -> 120;
			case "leap", "charge", "breath", "lightning" -> 150;
			case "quake", "rain", "cloud", "burrow" -> 200;
			case "beam", "roar" -> 240;
			case "heal" -> 300;
			case "summon" -> 420;
			default -> 120;
		};
	}

	/** where a skill can be used from, as [nearest, farthest] from the monster's middle */
	private static double[] range(String skill, GateMobs.Kind k) {
		double r = reach(k), s = MobSkills.size(k);
		return switch (skill) {
			case "slam", "spin" -> new double[] {0, r * 1.1};
			case "leap" -> new double[] {r * 1.3, 14 + 2 * s};
			case "charge" -> new double[] {r * 1.4, 16 + 2 * s};
			case "pull" -> new double[] {r * 1.4, 13};
			case "blink" -> new double[] {r * 1.1, 18};
			case "dash" -> new double[] {r * 0.9, r * 2.2};
			case "pounce" -> new double[] {1.5, 9 + s};
			case "burrow" -> new double[] {3, 18};
			case "breath" -> new double[] {0, 6 + 2 * s};
			case "quake" -> new double[] {0, 12};
			case "roar", "heal", "summon" -> new double[] {0, 24};
			default -> new double[] {3, 22};
		};
	}

	/** How likely it is to reach for a skill over its plain swings: casters live on them, bosses lean on them. */
	private static float weight(String skill, GateMobs.Kind k, Spec spec) {
		float w = spec.stance().equals("caster") ? 60 : 22;
		if (k.boss()) w *= 1.6f;
		if (skill.equals("bolt") && spec.stance().equals("caster")) w = 90;
		return w;
	}

	/** Every attack it can make, as Epic Fight combat behaviours. */
	static <T extends MobPatch<?>> CombatBehaviors.Builder<T> behaviours(Mob mob, GateMobs.Kind k) {
		Spec spec = of(k);
		Stance st = stance(k);
		double r = reach(k);
		CombatBehaviors.Builder<T> b = CombatBehaviors.builder();
		float melee = spec.stance().equals("caster") ? 25 : 100;
		for (AnimationAccessor<? extends StaticAnimation>[] combo : st.combos()) {
			BehaviorSeries.Builder<T> series = BehaviorSeries.<T>builder().weight(melee / st.combos().length).canBeInterrupted(false).looping(false);
			for (AnimationAccessor<? extends StaticAnimation> a : combo)
				series.nextBehavior(Behavior.<T>builder().animationBehavior(a).custom(p -> free(mob) && within(mob, 0, r)));
			b.newBehaviorSeries(series);
		}
		if (st.dash() != null)
			b.newBehaviorSeries(BehaviorSeries.<T>builder().weight(18).cooldown(90).canBeInterrupted(false).looping(false)
					.nextBehavior(Behavior.<T>builder().animationBehavior(st.dash()).custom(p -> free(mob) && within(mob, r * 0.9, r * 2.0))));
		if (spec.stance().equals("caster") || spec.stance().equals("dagger") || spec.stance().equals("twin_daggers"))
			b.newBehaviorSeries(BehaviorSeries.<T>builder().weight(30).cooldown(80).canBeInterrupted(false).looping(false)
					.nextBehavior(Behavior.<T>builder().animationBehavior(Animations.BIPED_STEP_BACKWARD).custom(p -> free(mob) && within(mob, 0, r * 0.8))));
		for (Skill sk : spec.skills()) {
			double[] rg = range(sk.name(), k);
			b.newBehaviorSeries(BehaviorSeries.<T>builder().weight(weight(sk.name(), k, spec)).canBeInterrupted(false).looping(false)
					.nextBehavior(Behavior.<T>builder().behavior(p -> MobSkills.cast(mob, sk))
							.custom(p -> MobSkills.ready(mob, sk) && within(mob, rg[0], rg[1]))));
		}
		return b;
	}

	/** How far a stance's swings reach, for someone of a player's size (an adventurer). */
	static double reach(String stance) {
		stances();
		return STANCES.get(stance).reach() + 0.3;
	}

	/** An adventurer's attacks (Adventurers): the combos and dash of the stance their weapon is swung in, and a step back for the light ones. */
	static <T extends MobPatch<?>> CombatBehaviors.Builder<T> behaviours(Mob mob, String stance) {
		stances();
		Stance st = STANCES.get(stance);
		double r = reach(stance);
		CombatBehaviors.Builder<T> b = CombatBehaviors.builder();
		for (AnimationAccessor<? extends StaticAnimation>[] combo : st.combos()) {
			BehaviorSeries.Builder<T> series = BehaviorSeries.<T>builder().weight(100f / st.combos().length).canBeInterrupted(false).looping(false);
			for (AnimationAccessor<? extends StaticAnimation> a : combo)
				series.nextBehavior(Behavior.<T>builder().animationBehavior(a).custom(p -> within(mob, 0, r)));
			b.newBehaviorSeries(series);
		}
		if (st.dash() != null)
			b.newBehaviorSeries(BehaviorSeries.<T>builder().weight(18).cooldown(90).canBeInterrupted(false).looping(false)
					.nextBehavior(Behavior.<T>builder().animationBehavior(st.dash()).custom(p -> within(mob, r * 0.9, r * 2.0))));
		if (stance.equals("dagger"))
			b.newBehaviorSeries(BehaviorSeries.<T>builder().weight(30).cooldown(80).canBeInterrupted(false).looping(false)
					.nextBehavior(Behavior.<T>builder().animationBehavior(Animations.BIPED_STEP_BACKWARD).custom(p -> within(mob, 0, r * 0.8))));
		return b;
	}

	private static boolean free(Mob mob) {
		return !MobSkills.busy(mob);
	}

	/** its target between `min` and `max` from its middle, and not far above or below it */
	private static boolean within(Mob mob, double min, double max) {
		LivingEntity t = mob.getTarget();
		if (t == null) return false;
		double dy = t.getY() - mob.getY();
		if (dy > Math.max(2.5, mob.getBbHeight()) || dy < -Math.max(3.0, mob.getBbHeight())) return false;
		double dx = t.getX() - mob.getX(), dz = t.getZ() - mob.getZ(), d = Math.sqrt(dx * dx + dz * dz);
		return d >= min && d <= max;
	}

	/** puts its unseen grip in its hand(s), so Epic Fight swings and hits with that weapon */
	static void grip(Mob m, GateMobs.Kind k) {
		Stance st = stance(k);
		if (m instanceof MobSkills.User u) u.state().gripped = true;
		if (st.grip() == null) return;
		Item it = BuiltInRegistries.ITEM.get(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, st.grip()));
		if (it == Items.AIR) return;
		if (m.getMainHandItem().getItem() != it) {
			m.setItemSlot(EquipmentSlot.MAINHAND, new ItemStack(it));
			m.setDropChance(EquipmentSlot.MAINHAND, 0);
		}
		if (st.twoGrips() && m.getOffhandItem().getItem() != it) {
			m.setItemSlot(EquipmentSlot.OFFHAND, new ItemStack(it));
			m.setDropChance(EquipmentSlot.OFFHAND, 0);
		}
	}

	/** grips: an unseen item of each weapon type the monsters swing (its capability file names the type) */
	static final String[] GRIPS = {"grip_sword", "grip_greatsword", "grip_longsword", "grip_uchigatana", "grip_tachi", "grip_spear", "grip_dagger", "grip_axe"};

	static void register() {
		for (String g : GRIPS) Weapons.ITEMS.registerSimpleItem(g, new Item.Properties().stacksTo(1));
	}
}
