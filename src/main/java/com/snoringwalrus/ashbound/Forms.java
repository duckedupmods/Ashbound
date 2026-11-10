package com.snoringwalrus.ashbound;

import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;
import net.neoforged.neoforge.event.entity.living.LivingHealEvent;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * The Awakening Tomes: a rare book for your class that rewrites you. Reading one costs your last skill key for good and
 * gives you a Form you can only take when its moment comes (the drake under 30% health, and so on). The key then
 * transforms you for a while, with a gift and a price, and in the Form the same key is the Form's own strike. The trade
 * is the point: a Form must be able to get you killed. One Tome at a time; reading another costs Ash.
 */
public final class Forms {
	private Forms() {}

	/** A Form's strike waits this long, in ticks. */
	private static final int STRIKE_REST = 60, SECOND = 20;
	private static final int SWAP_ASH_PER_LEVEL = 50;
	private static final double DRAKE_HEALTH = 0.3, RED_HEALTH = 0.5, ALLY_HEALTH = 0.2, EMPTY_MANA = 0.1, ALLY_REACH = 16;
	private static final int STAG_STILL = 3 * SECOND, KILL_WINDOW = 5 * SECOND, HAMMER_HITS = 8, HAMMER_WINDOW = 10 * SECOND, CROWN_THRALLS = 3;
	private static final double RED_DRAIN = 0.02, RED_DRINK = 0.15, SKY_GROUND = 2.5;

	public record Form(String id, String cls, String tome, String trigger, String gift, String price, int seconds, int rest, double dealt, double taken) {}

	public static final List<Form> ALL = List.of(
			new Form("drake", "vanguard", "Heart of the Cinder Drake", "Under 30% health", "Dragon wings of fire, fire breath, more than double damage",
					"No armour at all, and you take double damage", 20, 120, 2.2, 2),
			new Form("hammerfall", "breaker", "The Last Hammerfall", "8 hits in 10 seconds", "Every blow is a shockwave", "You can't sprint, and you take more damage", 15, 90, 1.4, 1.2),
			new Form("communion", "reaver", "Red Communion", "Under 50% health", "Your hits heal you, and the closer to death the harder you hit",
					"Your health drains away, and nothing else can heal you", 18, 100, 1.3, 1.3),
			new Form("tyrant", "lancer", "Sky Tyrant's Oath", "While in the air", "Free leaps, and hits far harder", "Far more damage on the ground", 18, 90, 1.6, 1),
			new Form("noone", "shade", "Name of No One", "Right after a kill", "Unseen, and every hit is a killing blow", "One hit breaks it and leaves you at 1 health", 12, 80, 3, 1),
			new Form("stag", "hunter", "The Pale Stag's Eye", "Standing still for 3 seconds", "Your shots hit twice as hard", "You can barely move, and you take more damage", 15, 80, 2, 1.5),
			new Form("offering", "ashcaster", "Burnt Offering", "Mana almost gone", "Spells cost health instead, and hit twice as hard",
					"Healing is halved, and you take more damage", 15, 90, 2, 1.3),
			new Form("martyr", "mender", "Martyr's Vow", "An ally near death", "Your ally is pulled back from the edge", "You fall to 1 health and can't heal for 15 seconds", 15, 120, 1, 1),
			new Form("crown", "caller", "Crown of the Hollow King", "All your thralls out", "They fuse into the Ossuary Colossus, which fights for you (more thralls, a bigger beast)",
					"Costs all your mana and 30% of your health; no other thralls until it ends", 20, 120, 1, 0.7));

	private static final class Active {
		final Form form;
		long until, nextStrike;

		Active(Form form, long until) {
			this.form = form;
			this.until = until;
		}
	}

	private static final Map<UUID, Active> ACTIVE = new HashMap<>();
	private static final Map<UUID, Long> REST = new HashMap<>(), KILLED = new HashMap<>();
	private static final Map<UUID, Integer> STILL = new HashMap<>();
	private static final Map<UUID, int[]> HITS = new HashMap<>();
	private static final Map<UUID, Boolean> SENT = new HashMap<>();
	private static final Map<UUID, Integer> SENT_HAVE = new HashMap<>();
	private static final Set<UUID> DRINKING = new HashSet<>(), SHAKING = new HashSet<>();
	/** the Crown: at most this many thralls go into the Colossus, and it takes this much of your health */
	private static final int CROWN_MOST = 5;
	private static final float CROWN_BLOOD = 0.3f;
	private static final ResourceLocation STAT = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "form");

	// your own, on your own screen
	public static String clientForm = "";
	public static boolean clientReady;
	public static long clientUntil, clientRest;
	/** how many of what the moment needs you have (the Crown's thralls out), -1 where it isn't a count */
	public static int clientHave = -1;

	public static void register() {
		NeoForge.EVENT_BUS.addListener((PlayerTickEvent.Post e) -> {
			if (e.getEntity() instanceof ServerPlayer p) tick(p);
		});
		NeoForge.EVENT_BUS.addListener(Forms::hurt);
		NeoForge.EVENT_BUS.addListener(Forms::heal);
		NeoForge.EVENT_BUS.addListener((LivingDeathEvent e) -> {
			if (e.getSource().getEntity() instanceof ServerPlayer p) KILLED.put(p.getUUID(), p.level().getGameTime());
			if (e.getEntity() instanceof ServerPlayer p) leave(p);
		});
		NeoForge.EVENT_BUS.addListener((PlayerEvent.PlayerLoggedOutEvent e) -> {
			if (e.getEntity() instanceof ServerPlayer p) leave(p);
			UUID id = e.getEntity().getUUID();
			REST.remove(id);
			KILLED.remove(id);
			STILL.remove(id);
			HITS.remove(id);
			SENT.remove(id);
			SENT_HAVE.remove(id);
		});
	}

	public static Form byId(String id) {
		for (Form f : ALL) if (f.id().equals(id)) return f;
		return null;
	}

	public static Form of(Player p) {
		return byId(p.getData(Skills.STATE).getOrDefault("form", ""));
	}

	public static boolean active(Player p, String id) {
		Active a = ACTIVE.get(p.getUUID());
		return a != null && a.form.id().equals(id);
	}

	/** What another Tome costs you. */
	public static int swapCost(ServerPlayer p) {
		return SWAP_ASH_PER_LEVEL * Levels.level(p);
	}

	/** Takes the book's bargain. Whoever calls this has checked the book is in their hand. */
	static boolean read(ServerPlayer p, Form f) {
		Classes.Cls c = Classes.of(p);
		if (c == null || !c.id().equals(f.cls())) {
			p.displayClientMessage(Component.literal("Only a " + Classes.byId(f.cls()).name() + " can read this").withStyle(ChatFormatting.RED), true);
			return false;
		}
		Form had = of(p);
		if (had == f) {
			p.displayClientMessage(Component.literal("You've already read this").withStyle(ChatFormatting.GRAY), true);
			return false;
		}
		if (had != null) {
			int ash = p.getData(Levels.ASH);
			if (ash < swapCost(p)) {
				p.displayClientMessage(Component.literal("Needs " + swapCost(p) + " Ash to take another Tome").withStyle(ChatFormatting.RED), true);
				return false;
			}
			p.setData(Levels.ASH, ash - swapCost(p));
		}
		leave(p);
		Skills.setForm(p, f.id());
		Spells.skillFx(p.serverLevel(), "tome", p.position(), Vec3.ZERO, 0, p);
		sync(p);
		p.sendSystemMessage(Component.literal("You've awakened: " + f.tome() + ". It isn't a skill: it's a Form that waits for its moment ("
				+ f.trigger().toLowerCase() + "). When the moment comes the crest above your hotbar burns red; press the Form key (B unless you changed it) to take it.")
				.withStyle(ChatFormatting.GOLD));
		return true;
	}

	static void sync(ServerPlayer p) {
		Active a = ACTIVE.get(p.getUUID());
		Form f = of(p);
		long now = p.level().getGameTime();
		PacketDistributor.sendToPlayer(p, new Net.FormState(f == null ? "" : f.id(), ready(p), a == null ? 0 : (int) (a.until - now),
				(int) Math.max(0, REST.getOrDefault(p.getUUID(), 0L) - now), have(p)));
	}

	/** How many of what the moment needs you've got, where it's a count: the Crown's thralls. */
	private static int have(ServerPlayer p) {
		Form f = of(p);
		return f != null && f.id().equals("crown") ? Spells.thralls(p) : -1;
	}

	/** How many the moment needs, for the count on your screen. */
	public static int needs(String form) {
		return form.equals("crown") ? CROWN_THRALLS : 0;
	}

	private static boolean ready(ServerPlayer p) {
		Form f = of(p);
		return f != null && !ACTIVE.containsKey(p.getUUID()) && REST.getOrDefault(p.getUUID(), 0L) <= p.level().getGameTime() && moment(p, f);
	}

	/** Whether this is the moment the Form can be taken. */
	private static boolean moment(ServerPlayer p, Form f) {
		long now = p.level().getGameTime();
		return switch (f.id()) {
			case "drake" -> p.getHealth() <= p.getMaxHealth() * DRAKE_HEALTH;
			case "communion" -> p.getHealth() <= p.getMaxHealth() * RED_HEALTH;
			case "hammerfall" -> {
				int[] h = HITS.get(p.getUUID());
				yield h != null && h[0] >= HAMMER_HITS && now - h[1] < HAMMER_WINDOW;
			}
			case "tyrant" -> !p.onGround() && !p.isInWater();
			case "noone" -> now - KILLED.getOrDefault(p.getUUID(), Long.MIN_VALUE / 2) < KILL_WINDOW;
			case "stag" -> STILL.getOrDefault(p.getUUID(), 0) >= STAG_STILL;
			case "offering" -> Spells.mana(p) <= Spells.max(p) * EMPTY_MANA;
			case "martyr" -> dying(p) != null;
			case "crown" -> Spells.thralls(p) >= CROWN_THRALLS;
			default -> false;
		};
	}

	private static ServerPlayer dying(ServerPlayer p) {
		for (ServerPlayer o : p.serverLevel().getEntitiesOfClass(ServerPlayer.class, p.getBoundingBox().inflate(ALLY_REACH), o -> o != p && o.isAlive() && !o.isSpectator()))
			if (o.getHealth() <= o.getMaxHealth() * ALLY_HEALTH) return o;
		return null;
	}

	private static void tick(ServerPlayer p) {
		UUID id = p.getUUID();
		if (of(p) == null) return;
		STILL.put(id, p.getDeltaMovement().horizontalDistanceSqr() < 1e-4 && p.onGround() ? STILL.getOrDefault(id, 0) + 1 : 0);
		Active a = ACTIVE.get(id);
		if (a != null) {
			if (p.level().getGameTime() >= a.until) leave(p);
			else during(p, a);
		}
		boolean ready = ready(p);
		int have = have(p);
		if (!Boolean.valueOf(ready).equals(SENT.get(id)) || have != SENT_HAVE.getOrDefault(id, -2)) {
			SENT.put(id, ready);
			SENT_HAVE.put(id, have);
			sync(p);
		}
	}

	private static void during(ServerPlayer p, Active a) {
		switch (a.form.id()) {
			case "communion" -> {
				if (p.tickCount % SECOND == 0 && p.getHealth() > 1) p.setHealth(Math.max(1, p.getHealth() - (float) (p.getMaxHealth() * RED_DRAIN)));
			}
			case "noone" -> p.addEffect(new MobEffectInstance(MobEffects.INVISIBILITY, SECOND, 0, false, false));
			case "stag" -> p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, SECOND, 3, false, false));
			case "hammerfall" -> p.setSprinting(false);
			default -> {}
		}
	}

	/** The key: take the Form if its moment has come, its strike if you're in it. */
	public static void key(ServerPlayer p) {
		Active a = ACTIVE.get(p.getUUID());
		if (a != null) {
			if (p.level().getGameTime() >= a.nextStrike) {
				a.nextStrike = p.level().getGameTime() + STRIKE_REST;
				strike(p, a.form);
			}
			return;
		}
		if (ready(p)) enter(p, of(p));
	}

	private static void stat(ServerPlayer p, net.minecraft.core.Holder<Attribute> a, double value, AttributeModifier.Operation op) {
		var i = p.getAttribute(a);
		if (i != null) i.addOrReplacePermanentModifier(new AttributeModifier(STAT, value, op));
	}

	private static void enter(ServerPlayer p, Form f) {
		ServerLevel l = p.serverLevel();
		ACTIVE.put(p.getUUID(), new Active(f, l.getGameTime() + f.seconds() * (long) SECOND));
		HITS.remove(p.getUUID());
		switch (f.id()) {
			case "drake" -> stat(p, Attributes.ARMOR, -1, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL);
			case "crown" -> {
				int eaten = Math.min(CROWN_MOST, Spells.thralls(p));
				Spells.dismiss(p);
				p.setData(Spells.MANA, 0f);
				p.setHealth(Math.max(1, p.getHealth() - p.getMaxHealth() * CROWN_BLOOD));
				Spells.colossus(p, eaten, f.seconds() * SECOND);
			}
			case "martyr" -> {
				ServerPlayer o = dying(p);
				if (o != null) {
					o.setHealth(o.getMaxHealth() * 0.6f);
					o.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, 5 * SECOND, 3));
					Spells.skillFx(l, "martyr_saved", o.position(), Vec3.ZERO, 0, o);
				}
				p.setHealth(1);
			}
			default -> {}
		}
		Spells.skillFx(l, "form_" + f.id(), p.position(), p.getLookAngle(), 0, p);
		PacketDistributor.sendToPlayersTrackingEntityAndSelf(p, new Net.FormAura(p.getId(), f.id()));
		p.displayClientMessage(Component.literal(f.tome()).withStyle(ChatFormatting.RED, ChatFormatting.BOLD), true);
		l.playSound(null, p.blockPosition(), SoundEvents.ENDER_DRAGON_GROWL, SoundSource.PLAYERS, 1f, 1.1f);
		sync(p);
	}

	static void leave(ServerPlayer p) {
		Active a = ACTIVE.remove(p.getUUID());
		if (a == null) return;
		for (var attr : List.of(Attributes.ARMOR, Attributes.SCALE)) {
			var i = p.getAttribute(attr);
			if (i != null) i.removeModifier(STAT);
		}
		REST.put(p.getUUID(), p.level().getGameTime() + a.form.rest() * (long) SECOND);
		if (a.form.id().equals("crown")) Spells.dismiss(p);   // the Colossus falls apart with it
		PacketDistributor.sendToPlayersTrackingEntityAndSelf(p, new Net.FormAura(p.getId(), ""));
		sync(p);
	}

	private static void strike(ServerPlayer p, Form f) {
		ServerLevel l = p.serverLevel();
		Spells.skillFx(l, "strike_" + f.id(), p.position(), p.getLookAngle(), 0, p);
		switch (f.id()) {
			case "drake" -> {
				Vec3 eye = p.getEyePosition(), dir = p.getLookAngle();
				float hit = JoinedSkills.strength(p) * 2;
				for (LivingEntity e : l.getEntitiesOfClass(LivingEntity.class, new AABB(eye, eye).inflate(9), x -> x instanceof Enemy && x.isAlive())) {
					Vec3 to = e.getBoundingBox().getCenter().subtract(eye);
					if (to.length() <= 9 && to.normalize().dot(dir) > 0.7) {
						JoinedSkills.strike(p, e, hit);
						e.igniteForSeconds(4);
					}
				}
			}
			case "hammerfall" -> JoinedSkills.ringHit(p, p.position(), 6, 3, 0.6);
			case "communion" -> {
				p.setHealth(Math.max(1, p.getHealth() - p.getMaxHealth() * 0.05f));
				JoinedSkills.ringHit(p, p.position(), 4.5, 2.5, 0.1);
			}
			case "tyrant" -> {
				Vec3 go = p.getLookAngle().multiply(1, 0, 1).normalize();
				p.setDeltaMovement(go.scale(0.8).add(0, 1.1, 0));
				p.hurtMarked = true;
			}
			case "noone" -> JoinedSkills.twoShadows(p, 2);
			case "stag" -> JoinedSkills.volley(p, p.getMainHandItem());
			case "offering" -> {
				Gear.Weapon w = Spells.held(p);
				if (w != null) Spells.heldSkill(p, w);
			}
			default -> {}
		}
	}

	private static double dealt(ServerPlayer p, Active a) {
		if (a.form.id().equals("communion")) return a.form.dealt() + (1 - p.getHealth() / p.getMaxHealth()) * 1.2;
		return a.form.dealt();
	}

	private static void hurt(LivingIncomingDamageEvent e) {
		if (e.getEntity() instanceof ServerPlayer p) {
			Active a = ACTIVE.get(p.getUUID());
			if (a != null) {
				e.setAmount((float) (e.getAmount() * a.form.taken() * (a.form.id().equals("tyrant") && p.onGround() ? SKY_GROUND : 1)));
				if (a.form.id().equals("noone")) {
					e.setAmount(0);
					p.setHealth(1);
					leave(p);
				}
			}
		}
		if (!(e.getSource().getEntity() instanceof ServerPlayer p)) return;
		UUID id = p.getUUID();
		Active a = ACTIVE.get(id);
		if (a == null) {
			Form f = of(p);
			if (f != null && f.id().equals("hammerfall")) {
				int[] h = HITS.computeIfAbsent(id, k -> new int[2]);
				long now = p.level().getGameTime();
				if (now - h[1] > HAMMER_WINDOW) h[0] = 0;
				h[0]++;
				h[1] = (int) now;
			}
			return;
		}
		e.setAmount((float) (e.getAmount() * dealt(p, a)));
		if (a.form.id().equals("communion")) {
			DRINKING.add(id);
			Meters.heal(p, p, e.getAmount() * (float) RED_DRINK * Gear.drink(p));
			DRINKING.remove(id);
		}
		if (a.form.id().equals("hammerfall") && SHAKING.add(id)) {
			JoinedSkills.ringHit(p, e.getEntity().position(), 3, 0.5, 0.2);
			Spells.skillFx(p.serverLevel(), "hammer_wave", e.getEntity().position(), Vec3.ZERO, 3, null, p);
			SHAKING.remove(id);
		}
	}

	private static void heal(LivingHealEvent e) {
		if (!(e.getEntity() instanceof ServerPlayer p)) return;
		Active a = ACTIVE.get(p.getUUID());
		if (a == null) return;
		switch (a.form.id()) {
			case "communion" -> {
				if (!DRINKING.contains(p.getUUID())) e.setCanceled(true);
			}
			case "martyr" -> e.setCanceled(true);
			case "offering" -> e.setAmount(e.getAmount() / 2);
			default -> {}
		}
	}

	/** Burnt Offering: pays for a spell in blood, a fifth of its mana in health. */
	static boolean paysInBlood(ServerPlayer p, float cost) {
		if (!active(p, "offering")) return false;
		p.setHealth(Math.max(1, p.getHealth() - cost / 5));
		return true;
	}
}
