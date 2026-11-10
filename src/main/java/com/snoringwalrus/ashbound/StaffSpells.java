package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.EnumSet;
import java.util.Iterator;
import java.util.List;
import java.util.UUID;

import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.living.LivingDropsEvent;
import net.neoforged.neoforge.event.entity.living.LivingExperienceDropEvent;
import net.neoforged.neoforge.event.server.ServerStoppingEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;

/**
 * What a staff actually does. Every staff of a school used to cast the same thing, so a staff was only a number. Now each one has a
 * {@link Style}, settled by its name so it's always the same: a black staff may lob a bursting ball, lay a rune or bring its element
 * down from above; a white one may rain healing or set a spring on the ground; a summoner's calls the Bound (Mounts.BOUND), blades or
 * mages or one great brute, burning in its own colour. Its element and how hard it hits are still {@link Spells}'.
 */
public final class StaffSpells {
	private StaffSpells() {}

	/** Cost and wait are the share of that school's plain cast, so a bigger spell is slower to come round. */
	public enum Style {
		BOLT("black", "Bolt", "hurls bolts of %s", 1, 1),
		ORB("black", "Orb", "lobs a ball of %s that bursts where it lands", 1.5f, 2),
		RUNE("black", "Rune", "lays a rune of %s: the first monster over it sets it off", 1.2f, 1.5f),
		LANCE("black", "Lance", "drives a lance of %s through everything in line", 1.5f, 2),
		FAN("black", "Fan", "fans out three bolts of %s", 1.25f, 1.5f),
		FALL("black", "Fall", "brings %s down where you aim, three times over", 2.5f, 4),

		CIRCLE("white", "Circle", "heals you and those near, or one ally from afar: aim at them, or pick a party member with G", 1, 1),
		RAIN("white", "Rain", "rains healing where you aim, on all who stand in it", 1.3f, 2.5f),
		MEND("white", "Mend", "mends one ally hard, or you if there's no one to aim at", 0.8f, 0.67f),
		SPRING("white", "Spring", "sets a healing spring on the ground that lasts", 1.2f, 4),
		FLASK("white", "Flask", "throws a flask of healing that bursts where it lands", 1, 1),

		BLADES("summon", "Blades", "calls fighters of %s, blades first", 1, 1),
		MAGES("summon", "Mages", "calls casters of %s, who hang back and throw bolts", 1, 1),
		BRUTE("summon", "Brute", "calls one great brute of %s", 1, 1),
		SWARM("summon", "Swarm", "calls a swarm of %s, weak but many", 1, 1),
		BAND("summon", "Warband", "calls a warband of %s, blades and mages together", 1, 1);

		private static final java.util.Map<String, Style> DEALT = new java.util.HashMap<>();
		public final String school, title, says;
		public final float cost, wait;

		Style(String school, String title, String says, float cost, float wait) {
			this.school = school;
			this.title = title;
			this.says = says;
			this.cost = cost;
			this.wait = wait;
		}

		/** The plain staffs have the plain spell; the rest of a school are dealt out in order of name, so each spell gets its share. */
		public static Style of(Gear.Weapon w) {
			if (DEALT.isEmpty()) deal();
			return DEALT.getOrDefault(w.id(), w.kind().equals("white") ? CIRCLE : w.kind().equals("summon") ? BLADES : BOLT);
		}

		private static void deal() {
			java.util.Map<String, List<Gear.Weapon>> schools = new java.util.HashMap<>();
			for (var it : BuiltInRegistries.ITEM)
				if (it instanceof Spells.Staff s && !s.weapon.id().startsWith("apprentice_")) schools.computeIfAbsent(s.weapon.kind(), k -> new ArrayList<>()).add(s.weapon);
			schools.forEach((school, staffs) -> {
				staffs.sort(java.util.Comparator.comparing(Gear.Weapon::id));
				List<Style> mine = java.util.Arrays.stream(values()).filter(s -> s.school.equals(school)).toList();
				for (int i = 0; i < staffs.size(); i++) DEALT.put(staffs.get(i).id(), mine.get(i % mine.size()));
			});
		}

		/** What a staff's spell was set to at the forge (11/7: the user picks Mend, Spring, Rain... when it's made), else its own. */
		public static final String KEY = "ash_spell";

		public static Style of(ItemStack s) {
			if (!(s.getItem() instanceof Spells.Staff st)) return BOLT;
			Style own = of(st.weapon);
			if (st.weapon.id().startsWith("apprentice_")) return own;
			var c = s.get(net.minecraft.core.component.DataComponents.CUSTOM_DATA);
			if (c == null || !c.contains(KEY)) return own;
			try {
				Style pick = valueOf(c.copyTag().getString(KEY));
				return pick.school.equals(st.weapon.kind()) ? pick : own;
			} catch (IllegalArgumentException e) {
				return own;
			}
		}

		/** The spell of the staff of w in p's hands (main first), else w's own. */
		public static Style of(Gear.Weapon w, @javax.annotation.Nullable LivingEntity p) {
			if (p != null)
				for (ItemStack s : new ItemStack[] {p.getMainHandItem(), p.getOffhandItem()})
					if (s.getItem() instanceof Spells.Staff st && st.weapon == w) return of(s);
			return of(w);
		}

		/** The spells a staff of this school can be made with (the plain staffs keep theirs). */
		public static List<Style> choices(Gear.Weapon w) {
			if (w.id().startsWith("apprentice_")) return List.of(of(w));
			return java.util.Arrays.stream(values()).filter(s -> s.school.equals(w.kind())).toList();
		}

		public static void set(ItemStack s, Style st) {
			net.minecraft.world.item.component.CustomData.update(net.minecraft.core.component.DataComponents.CUSTOM_DATA, s, t -> t.putString(KEY, st.name()));
		}

		public String line(String element) {
			return title + ": " + (says.contains("%s") ? String.format(says, element) : says);
		}
	}

	/** Blocks: how far you can aim one, and the size of each burst. */
	private static final double AIM = 32, ORB_WIDE = 3, RUNE_WIDE = 3.5, RUNE_TRIP = 1.5, FALL_WIDE = 3, LANCE_LONG = 24, LANCE_WIDE = 1.2;
	private static final double RAIN_WIDE = 5, SPRING_WIDE = 4, FLASK_WIDE = 4, FAN_APART = 12;
	/** Each of these against one plain bolt's hit (20 before power). */
	private static final float ORB_HIT = 1.3f, RUNE_HIT = 2, LANCE_HIT = 1.5f, FAN_HIT = 0.6f, FALL_HIT = 1.1f;
	/** Each of these against one plain circle's heal, all told. */
	private static final float RAIN_HEAL = 2.5f, SPRING_HEAL = 3, MEND_HEAL = 1.8f, FLASK_HEAL = 1;
	private static final int FALLS = 3, FALL_EVERY = 8, FALL_DROPS = 12, MOST_RUNES = 3, RUNE_LASTS = 1200, RUNE_SHOWS = 70, RUNE_LOOKS = 5;
	private static final int RAIN_PULSES = 8, RAIN_EVERY = 15, SPRING_PULSES = 8, SPRING_EVERY = 30;
	private static final double LOB_SPEED = 1.1;

	/** Summons, against a revenant's health and hit. */
	private static final double BRUTE_HP = 2.6, BRUTE_HIT = 1.8, SWARM_HP = 0.45, SWARM_HIT = 0.55, MAGE_HP = 0.7, MAGE_BOLT = 1.3, REVENANT_HP = 30;
	private static final int THRALL_LASTS = 600, LONG_LASTS = 900, SWARM_LASTS = 400, CAST_EVERY = 40;
	private static final double CAST_REACH = 18, BOLT_SPEED = 1.4;

	/** Something left on the ground: a rune, or a patch of healing. */
	private static final class Spot {
		final ServerLevel level;
		final UUID owner;
		final Style style;
		final Vec3 at;
		final String look;
		final float amount;
		final long until;
		double wide;
		long next;

		Spot(ServerLevel level, UUID owner, Style style, Vec3 at, String look, float amount, int lasts) {
			wide = style == Style.RAIN ? RAIN_WIDE : style == Style.SPRING ? SPRING_WIDE : RUNE_WIDE;
			this.level = level;
			this.owner = owner;
			this.style = style;
			this.at = at;
			this.look = look;
			this.amount = amount;
			until = level.getGameTime() + lasts;
		}
	}

	private static final List<Spot> SPOTS = new ArrayList<>();

	static void register() {
		NeoForge.EVENT_BUS.addListener((ServerTickEvent.Post e) -> tick());
		NeoForge.EVENT_BUS.addListener((ServerStoppingEvent e) -> SPOTS.clear());
		NeoForge.EVENT_BUS.addListener((LivingDropsEvent e) -> {
			if (Spells.isThrall(e.getEntity())) e.setCanceled(true);
		});
		NeoForge.EVENT_BUS.addListener((LivingExperienceDropEvent e) -> {
			if (Spells.isThrall(e.getEntity())) e.setCanceled(true);
		});
		// /ashbound staffstyle STYLE: a staff that casts it, to try
		NeoForge.EVENT_BUS.addListener((net.neoforged.neoforge.event.RegisterCommandsEvent e) -> e.getDispatcher().register(
				net.minecraft.commands.Commands.literal("ashbound").requires(c -> c.hasPermission(2))
						.then(net.minecraft.commands.Commands.literal("staffstyle").then(net.minecraft.commands.Commands
								.argument("style", com.mojang.brigadier.arguments.StringArgumentType.word())
								.suggests((c, b) -> net.minecraft.commands.SharedSuggestionProvider.suggest(java.util.Arrays.stream(Style.values()).map(s -> s.name().toLowerCase()), b))
								.executes(c -> give(c.getSource().getPlayerOrException(), com.mojang.brigadier.arguments.StringArgumentType.getString(c, "style")))))));
	}

	private static int give(ServerPlayer p, String name) {
		for (var it : BuiltInRegistries.ITEM)
			if (it instanceof Spells.Staff s && !s.weapon.id().startsWith("apprentice_") && Style.of(s.weapon).name().equalsIgnoreCase(name)) {
				p.getInventory().placeItemBackInInventory(new ItemStack(it));
				p.sendSystemMessage(Component.literal(s.weapon.name() + ": " + Style.of(s.weapon).title));
				return 1;
			}
		return 0;
	}

	// ---------------------------------------------------------------- what's about

	static List<LivingEntity> enemies(ServerLevel level, Vec3 at, double wide) {
		return level.getEntitiesOfClass(LivingEntity.class, new AABB(at, at).inflate(wide), m -> m instanceof Enemy && Spells.ownerOf(m) == null && !Spells.isThrall(m) && m.isAlive() && m.distanceToSqr(at) < wide * wide * 1.6);
	}

	private static List<LivingEntity> allies(ServerLevel level, Vec3 at, double wide) {
		return level.getEntitiesOfClass(LivingEntity.class, new AABB(at, at).inflate(wide), e -> (e instanceof Player || Spells.ownerOf(e) != null) && e.isAlive() && e.distanceToSqr(at) < wide * wide * 1.6);
	}

	/** Where the crosshair lands: the first thing solid, else straight down from as far as you can aim. */
	static Vec3 aimed(ServerPlayer p) {
		ServerLevel level = p.serverLevel();
		Vec3 eye = p.getEyePosition(), far = eye.add(p.getLookAngle().scale(AIM));
		var hit = level.clip(new ClipContext(eye, far, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, p));
		Vec3 at = hit.getType() == HitResult.Type.MISS ? far : hit.getLocation();
		var down = level.clip(new ClipContext(at.add(0, 0.2, 0), at.add(0, -AIM, 0), ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, p));
		return down.getType() == HitResult.Type.MISS ? at : down.getLocation();
	}

	/** One of the look-only pieces in client/StyleFx. */
	private static void style(ServerLevel level, String what, String look, Vec3 at, Vec3 dir, float r) {
		Spells.skillFx(level, "style_" + what + ":" + look, at, dir, r, null);
	}

	private static void blast(ServerPlayer p, Vec3 at, double wide, float damage, String look, String burst) {
		ServerLevel level = p.serverLevel();
		int seconds = Passives.has(p, "long_effects") ? 6 : 3;
		for (LivingEntity m : enemies(level, at, wide)) {
			m.hurt(p.damageSources().indirectMagic(p, p), damage);
			Spells.element(look, m, seconds);
		}
		style(level, burst, look, at.add(0, 0.5, 0), Vec3.ZERO, (float) wide);
		level.playSound(null, at.x, at.y, at.z, SoundEvents.GENERIC_EXPLODE.value(), SoundSource.PLAYERS, 0.5f, 1.5f);
	}

	private static void mend(ServerPlayer p, List<LivingEntity> who, float amount, String look) {
		ServerLevel level = p.serverLevel();
		for (LivingEntity e : who) {
			Meters.heal(p, e, amount);
			e.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 40, 0));
			Spells.touched(p, e);
			Spells.fx(level, Spells.FX_BLESS, look, e.position(), 0, e);
		}
		CurioFx.healed(p, who);
	}

	// ---------------------------------------------------------------- casting

	/** The black staffs that aren't a plain bolt. */
	static void black(ServerPlayer p, Gear.Weapon w, Style s, double pw) {
		ServerLevel level = p.serverLevel();
		String look = Spells.look(w);
		float hit = (float) (20.0 * pw);
		Spells.fx(level, Spells.FX_CAST, look, p.getEyePosition(), s == Style.FALL ? 2 : 1, p);
		switch (s) {
			case ORB -> {
				Spells.Bolt b = Spells.fire(p, look, p.getLookAngle(), LOB_SPEED, 0, false, -1);
				b.lobbed();
				b.lands = at -> blast(p, at, ORB_WIDE, hit * ORB_HIT, look, "orb_burst");
				style(level, "orb", look, p.position(), Vec3.ZERO, b.getId());
			}
			case RUNE -> {
				List<Spot> mine = new ArrayList<>(SPOTS.stream().filter(o -> o.style == Style.RUNE && o.owner.equals(p.getUUID())).toList());
				if (mine.size() >= MOST_RUNES) SPOTS.remove(mine.get(0));
				SPOTS.add(new Spot(level, p.getUUID(), Style.RUNE, aimed(p), look, hit * RUNE_HIT, RUNE_LASTS));
			}
			case LANCE -> {
				Vec3 from = p.getEyePosition(), dir = p.getLookAngle(), to = from.add(dir.scale(LANCE_LONG));
				var wall = level.clip(new ClipContext(from, to, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, p));
				double far = wall.getType() == HitResult.Type.MISS ? LANCE_LONG : wall.getLocation().distanceTo(from);
				java.util.Set<LivingEntity> struck = new java.util.HashSet<>();
				for (double d = LANCE_WIDE; d < far; d += LANCE_WIDE) struck.addAll(enemies(level, from.add(dir.scale(d)), LANCE_WIDE));
				for (LivingEntity m : struck) {
					m.hurt(p.damageSources().indirectMagic(p, p), hit * LANCE_HIT);
					Spells.element(look, m, 3);
				}
				style(level, "lance", look, from.add(dir), dir, (float) far);
			}
			case FAN -> {
				Vec3 dir = p.getLookAngle();
				for (int i = -1; i <= 1; i++) Spells.fire(p, look, dir.yRot((float) Math.toRadians(i * FAN_APART)), 1.6, hit * FAN_HIT, false, -1);
				style(level, "fan", look, p.getEyePosition().add(dir.scale(1.4)), dir, 3.2f);
			}
			case FALL -> {
				Vec3 at = aimed(p);
				style(level, "mark", look, at, Vec3.ZERO, (float) FALL_WIDE);
				for (int i = 0; i < FALLS; i++) {
					style(level, "fall", look, at, Vec3.ZERO, FALL_DROPS + i * FALL_EVERY);
					JoinedSkills.later(p, FALL_DROPS + i * FALL_EVERY, () -> blast(p, at, FALL_WIDE, hit * FALL_HIT, look, "fall_burst"));
				}
			}
			default -> {}
		}
		level.playSound(null, p.blockPosition(), SoundEvents.BLAZE_SHOOT, SoundSource.PLAYERS, 0.6f, 1.2f);
	}

	/** The white staffs that aren't the circle. amount is what one plain circle heals. */
	static void white(ServerPlayer p, Gear.Weapon w, Style s, float amount) {
		ServerLevel level = p.serverLevel();
		String look = Spells.look(w);
		switch (s) {
			case RAIN -> {
				Spot rain = new Spot(level, p.getUUID(), Style.RAIN, aimed(p), look, amount * RAIN_HEAL / RAIN_PULSES, RAIN_PULSES * RAIN_EVERY);
				SPOTS.add(rain);
				Spells.fx(level, Spells.FX_WARD, look, rain.at, (float) RAIN_WIDE, null);
			}
			case MEND -> {
				ServerPlayer one = Spells.healTarget(p);
				if (one != null) Spells.beam(p, one, look, amount * MEND_HEAL);
				else mend(p, List.of(p), amount * MEND_HEAL, look);
				style(level, "mend", look, (one != null ? one : p).position(), Vec3.ZERO, 0);
			}
			case SPRING -> {
				SPOTS.removeIf(o -> o.style == Style.SPRING && o.owner.equals(p.getUUID()));
				SPOTS.add(new Spot(level, p.getUUID(), Style.SPRING, aimed(p), look, amount * SPRING_HEAL / SPRING_PULSES, SPRING_PULSES * SPRING_EVERY));
			}
			case FLASK -> {
				Spells.Bolt b = Spells.fire(p, look, p.getLookAngle(), LOB_SPEED, 0, false, -1);
				b.lobbed();
				b.lands = at -> {
					style(level, "flask_burst", look, at, Vec3.ZERO, (float) FLASK_WIDE);
					mend(p, allies(level, at, FLASK_WIDE), amount * FLASK_HEAL, look);
				};
				style(level, "flask", look, p.position(), Vec3.ZERO, b.getId());
			}
			default -> {}
		}
		level.playSound(null, p.blockPosition(), SoundEvents.AMETHYST_BLOCK_RESONATE, SoundSource.PLAYERS, 1f, 1.2f);
	}

	// ---------------------------------------------------------------- the first key: a staff's own spell, great

	/** How much bigger the great forms are than the plain cast. */
	private static final float GREAT = 1.6f;
	private static final int GREAT_ORBS = 3, GREAT_RUNES = 5, GREAT_LANCES = 3, GREAT_FAN = 7, GREAT_FALLS = 5, GREAT_FLASKS = 3;
	private static final double GREAT_APART = 15, RING = 3.5;

	/** What R does with a black or white staff that isn't the plain bolt or circle: its own spell, bigger. */
	static void great(ServerPlayer p, Gear.Weapon w, Style s, double pw, float amount) {
		ServerLevel level = p.serverLevel();
		String look = Spells.look(w);
		float hit = (float) (20.0 * pw);
		Vec3 dir = p.getLookAngle();
		Spells.fx(level, Spells.FX_CAST, look, p.getEyePosition(), 2, p);
		switch (s) {
			case ORB -> {
				for (int i = 0; i < GREAT_ORBS; i++) {
					Spells.Bolt b = Spells.fire(p, look, dir.yRot((float) Math.toRadians((i - 1) * GREAT_APART)), LOB_SPEED, 0, false, -1);
					b.lobbed();
					b.lands = at -> blast(p, at, ORB_WIDE * 1.3, hit * ORB_HIT * 1.2f, look, "orb_burst");
					style(level, "orb", look, p.position(), Vec3.ZERO, b.getId());
				}
			}
			case RUNE -> {
				Vec3 at = aimed(p);
				for (int i = 0; i < GREAT_RUNES; i++) {
					double a = Math.PI * 2 * i / GREAT_RUNES;
					Vec3 o = at.add(Math.cos(a) * RING, 0, Math.sin(a) * RING);
					var down = level.clip(new ClipContext(o.add(0, 2, 0), o.add(0, -4, 0), ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, p));
					Spot r = new Spot(level, p.getUUID(), Style.RUNE, down.getType() == HitResult.Type.MISS ? o : down.getLocation(), look, hit * RUNE_HIT, RUNE_LASTS / 2);
					SPOTS.add(r);
					style(level, "rune", look, r.at, Vec3.ZERO, (float) RUNE_TRIP);
				}
			}
			case LANCE -> {
				for (int i = 0; i < GREAT_LANCES; i++) {
					Vec3 d = dir.yRot((float) Math.toRadians((i - 1) * GREAT_APART * 0.7)), from = p.getEyePosition();
					var wall = level.clip(new ClipContext(from, from.add(d.scale(LANCE_LONG)), ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, p));
					double far = wall.getType() == HitResult.Type.MISS ? LANCE_LONG : wall.getLocation().distanceTo(from);
					java.util.Set<LivingEntity> struck = new java.util.HashSet<>();
					for (double k = LANCE_WIDE; k < far; k += LANCE_WIDE) struck.addAll(enemies(level, from.add(d.scale(k)), LANCE_WIDE));
					for (LivingEntity m : struck) {
						m.hurt(p.damageSources().indirectMagic(p, p), hit * LANCE_HIT * 1.2f);
						Spells.element(look, m, 3);
					}
					style(level, "lance", look, from.add(d), d, (float) far);
				}
			}
			case FAN -> {
				for (int i = 0; i < GREAT_FAN; i++)
					Spells.fire(p, look, dir.yRot((float) Math.toRadians((i - GREAT_FAN / 2) * FAN_APART)), 1.6, hit * FAN_HIT * 1.3f, false, -1);
				style(level, "fan", look, p.getEyePosition().add(dir.scale(1.4)), dir, 3.2f * GREAT);
			}
			case FALL -> {
				Vec3 at = aimed(p);
				double wide = FALL_WIDE * GREAT;
				style(level, "mark", look, at, Vec3.ZERO, (float) wide);
				for (int i = 0; i < GREAT_FALLS; i++) {
					style(level, "fall", look, at, Vec3.ZERO, FALL_DROPS + i * FALL_EVERY);
					JoinedSkills.later(p, FALL_DROPS + i * FALL_EVERY, () -> blast(p, at, wide, hit * FALL_HIT, look, "fall_burst"));
				}
			}
			case RAIN -> {
				Spot rain = new Spot(level, p.getUUID(), Style.RAIN, aimed(p), look, amount * RAIN_HEAL * GREAT / RAIN_PULSES, RAIN_PULSES * RAIN_EVERY);
				rain.wide = RAIN_WIDE * GREAT;
				SPOTS.add(rain);
				Spells.fx(level, Spells.FX_WARD, look, rain.at, (float) rain.wide, null);
			}
			case MEND -> {
				ServerPlayer one = Spells.healTarget(p);
				if (one != null) Spells.beam(p, one, look, amount * MEND_HEAL * 2);
				mend(p, allies(level, p.position(), SPRING_WIDE), amount * MEND_HEAL * (one != null ? 0.5f : 1.5f), look);
				style(level, "mend", look, (one != null ? one : p).position(), Vec3.ZERO, 0);
			}
			case SPRING -> {
				SPOTS.removeIf(o -> o.style == Style.SPRING && o.owner.equals(p.getUUID()));
				Spot spring = new Spot(level, p.getUUID(), Style.SPRING, aimed(p), look, amount * SPRING_HEAL * GREAT / SPRING_PULSES, SPRING_PULSES * SPRING_EVERY);
				spring.wide = SPRING_WIDE * GREAT;
				SPOTS.add(spring);
			}
			case FLASK -> {
				for (int i = 0; i < GREAT_FLASKS; i++) {
					Spells.Bolt b = Spells.fire(p, look, dir.yRot((float) Math.toRadians((i - 1) * GREAT_APART)), LOB_SPEED, 0, false, -1);
					b.lobbed();
					b.lands = at -> {
						style(level, "flask_burst", look, at, Vec3.ZERO, (float) FLASK_WIDE);
						mend(p, allies(level, at, FLASK_WIDE), amount * FLASK_HEAL, look);
					};
					style(level, "flask", look, p.position(), Vec3.ZERO, b.getId());
				}
			}
			default -> {}
		}
		level.playSound(null, p.blockPosition(), s.school.equals("white") ? SoundEvents.BEACON_POWER_SELECT : SoundEvents.BLAZE_SHOOT, SoundSource.PLAYERS, 1f, 0.7f);
	}

	private static void tick() {
		for (Iterator<Spot> it = SPOTS.iterator(); it.hasNext(); ) {
			Spot s = it.next();
			long now = s.level.getGameTime();
			Player who = s.level.getPlayerByUUID(s.owner);
			if (now > s.until || !(who instanceof ServerPlayer p)) {
				it.remove();
				continue;
			}
			Spells.BY = p;   // the rune's or the spring's effects are its caster's (put back after the loop)
			if (s.style == Style.RUNE) {
				if (now % RUNE_LOOKS == 0 && !enemies(s.level, s.at, RUNE_TRIP).isEmpty()) {
					blast(p, s.at, s.wide, s.amount, s.look, "rune_burst");
					it.remove();
					continue;
				}
				if (now >= s.next) {
					style(s.level, "rune", s.look, s.at, Vec3.ZERO, (float) RUNE_TRIP);
					s.next = now + RUNE_SHOWS;
				}
				continue;
			}
			if (now < s.next) continue;
			boolean rain = s.style == Style.RAIN;
			double wide = s.wide;
			s.next = now + (rain ? RAIN_EVERY : SPRING_EVERY);
			style(s.level, rain ? "rain" : "spring", s.look, s.at, Vec3.ZERO, (float) wide);
			mend(p, allies(s.level, s.at, wide), s.amount, s.look);
		}
		Spells.BY = null;
	}

	// ---------------------------------------------------------------- summons

	/** How many a cast of n really brings. */
	static int band(Gear.Weapon w, int n) {
		return band(w, n, null);
	}

	static int band(Gear.Weapon w, int n, @javax.annotation.Nullable LivingEntity p) {
		return switch (Style.of(w, p)) {
			case SWARM -> n * 2;
			case BRUTE -> Math.max(1, n / 2);
			default -> n;
		};
	}

	/**
	 * The k-th of a call: false for the plain staff, whose calls are revenants.
	 */
	static boolean call(ServerPlayer p, Gear.Weapon w, int k, double x, double z, double pw) {
		if (w.id().startsWith("apprentice_")) return false;
		Style s = Style.of(w, p);
		boolean mage = s == Style.MAGES || s == Style.BAND && k % 2 == 1;
		var type = (s == Style.BRUTE ? Mounts.GATEBREAKER : s == Style.SWARM ? Mounts.RIFTLING : mage ? Mounts.CANTOR : s == Style.BAND ? Mounts.OATHWARDEN : Mounts.RIFTBLADE).get();
		double hp = REVENANT_HP * pw * (s == Style.BRUTE ? BRUTE_HP : s == Style.SWARM ? SWARM_HP : mage ? MAGE_HP : 1);
		double hit = Spells.THRALL_DMG * pw * (s == Style.BRUTE ? BRUTE_HIT : s == Style.SWARM ? SWARM_HIT : 1);
		int lasts = s == Style.SWARM ? SWARM_LASTS : Passives.has(p, "long_thralls") ? LONG_LASTS : THRALL_LASTS;
		Mob m = Spells.thrall(p, type, x, p.getY(), z, lasts, hp, hit);
		if (m == null) return false;
		if (m instanceof Thrall bound) bound.tint(SpellLook.colour(Spells.look(w)));
		if (mage) m.goalSelector.addGoal(-1, new Cast(m, p, Spells.look(w), (float) (hit * MAGE_BOLT)));
		style(p.serverLevel(), s.name().toLowerCase(java.util.Locale.ROOT), Spells.look(w), m.position(), Vec3.ZERO, 0);
		return true;
	}

	/** A caster on your side: it stands off and throws bolts while it can see what it's fighting. */
	static final class Cast extends Goal {
		private final Mob mob;
		private final Player owner;
		private final String look;
		private final float damage;
		private int wait;

		Cast(Mob mob, Player owner, String look, float damage) {
			this.mob = mob;
			this.owner = owner;
			this.look = look;
			this.damage = damage;
			setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
		}

		private boolean inSight() {
			LivingEntity t = mob.getTarget();
			return t != null && t.isAlive() && mob.distanceTo(t) < CAST_REACH && mob.hasLineOfSight(t);
		}

		@Override
		public boolean canUse() {
			return inSight();
		}

		@Override
		public boolean canContinueToUse() {
			return inSight();
		}

		@Override
		public boolean requiresUpdateEveryTick() {
			return true;
		}

		@Override
		public void tick() {
			LivingEntity t = mob.getTarget();
			mob.getNavigation().stop();
			mob.getLookControl().setLookAt(t, 30, 30);
			if (--wait > 0 || !(mob.level() instanceof ServerLevel level)) return;
			wait = CAST_EVERY;
			Vec3 from = mob.getEyePosition(), dir = t.getBoundingBox().getCenter().subtract(from).normalize();
			Spells.Bolt b = new Spells.Bolt(Spells.BOLT.get(), level);
			b.setOwner(owner);
			b.setPos(from.add(dir));
			b.setDeltaMovement(dir.scale(BOLT_SPEED));
			b.damage = damage;
			b.setGate(look);
			b.setBraid(-1);
			level.addFreshEntity(b);
			mob.swing(net.minecraft.world.InteractionHand.MAIN_HAND);
			Spells.fx(level, Spells.FX_CAST, look, from, 1, null);
		}
	}
}
