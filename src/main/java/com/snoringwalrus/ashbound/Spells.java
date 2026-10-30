package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.EnumSet;
import java.util.Iterator;
import java.util.List;
import java.util.UUID;
import java.util.function.Consumer;
import java.util.function.Supplier;

import org.joml.Vector3f;

import com.mojang.serialization.Codec;

import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.RangedAttribute;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.target.TargetGoal;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.attachment.AttachmentType;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.EntityAttributeModificationEvent;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.neoforged.neoforge.network.PacketDistributor;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.registries.NeoForgeRegistries;

/**
 * Mana and the three staff schools. Every dungeon makes one staff of each: BLACK throws a bolt of the dungeon's
 * element, WHITE heals you and everyone near, SUMMON calls up the dungeon's own dwellers to fight for you a while.
 * How hard comes from the staff's rank and your SPELL_POWER (robes raise it); mana fills back once you stop casting.
 */
public final class Spells {
	private Spells() {}

	static final DeferredRegister<Attribute> ATTRIBUTES = DeferredRegister.create(Registries.ATTRIBUTE, Ashbound.ID);
	static final DeferredRegister<AttachmentType<?>> ATTACHMENTS = DeferredRegister.create(NeoForgeRegistries.ATTACHMENT_TYPES, Ashbound.ID);
	static final DeferredRegister<EntityType<?>> ENTITIES = DeferredRegister.create(Registries.ENTITY_TYPE, Ashbound.ID);

	public static final DeferredHolder<Attribute, Attribute> SPELL_POWER = ATTRIBUTES.register("spell_power",
			() -> new RangedAttribute("attribute.ashbound.spell_power", 1.0, 0, 10).setSyncable(true));
	public static final DeferredHolder<Attribute, Attribute> MAX_MANA = ATTRIBUTES.register("max_mana",
			() -> new RangedAttribute("attribute.ashbound.max_mana", 100, 0, 2000).setSyncable(true));
	public static final DeferredHolder<Attribute, Attribute> MANA_REGEN = ATTRIBUTES.register("mana_regen",
			() -> new RangedAttribute("attribute.ashbound.mana_regen", 1.0, 0, 10).setSyncable(true));

	public static final Supplier<AttachmentType<Float>> MANA = ATTACHMENTS.register("mana",
			() -> AttachmentType.builder(() -> 100f).serialize(Codec.FLOAT).build());

	public static final DeferredHolder<EntityType<?>, EntityType<Bolt>> BOLT = ENTITIES.register("spell_bolt",
			() -> EntityType.Builder.<Bolt>of(Bolt::new, MobCategory.MISC).sized(0.4f, 0.4f).clientTrackingRange(8).updateInterval(1)
					.build(Ashbound.ID + ":spell_bolt"));

	// what the client's told to draw (client/SpellFx): FX with where, how big, and who it's on
	public static final int FX_CAST = 0, FX_HIT = 1, FX_OVERLOAD = 2, FX_HEAL = 3, FX_BLESS = 4, FX_LANCE = 5, FX_WARD = 6, FX_GUARD = 7, FX_SUMMON = 8, FX_RISE = 9, FX_GONE = 10, FX_GREAT_HEAL = 11;
	private static final int FX_RANGE = 96;
	/** each tick of a bolt on the client */
	public static Consumer<Bolt> onBolt = b -> {};

	static void fx(ServerLevel l, int kind, String gate, Vec3 at, float r, Entity on) {
		PacketDistributor.sendToPlayersNear(l, null, at.x, at.y, at.z, FX_RANGE, new Net.SpellFx(kind, gate, at.toVector3f(), r, on == null ? -1 : on.getId()));
	}

	/** what the client last heard: mana now and at most */
	public static float clientMana = 100, clientMax = 100;

	static void register(IEventBus bus) {
		ATTRIBUTES.register(bus);
		ATTACHMENTS.register(bus);
		ENTITIES.register(bus);
		bus.addListener((EntityAttributeModificationEvent e) -> {
			e.add(EntityType.PLAYER, SPELL_POWER);
			e.add(EntityType.PLAYER, MAX_MANA);
			e.add(EntityType.PLAYER, MANA_REGEN);
		});
		NeoForge.EVENT_BUS.addListener((PlayerTickEvent.Post e) -> {
			if (e.getEntity() instanceof ServerPlayer p) regen(p);
		});
		NeoForge.EVENT_BUS.addListener((ServerTickEvent.Post e) -> tickThralls());
		// /ashbound spell <gate, or heal, radiance, summon, overload, great_heal, host, braid>: see any of the magic without its staff
		NeoForge.EVENT_BUS.addListener((net.neoforged.neoforge.event.RegisterCommandsEvent e) -> e.getDispatcher().register(
				net.minecraft.commands.Commands.literal("ashbound").requires(c -> c.hasPermission(2))
						.then(net.minecraft.commands.Commands.literal("spell").then(net.minecraft.commands.Commands
								.argument("name", com.mojang.brigadier.arguments.StringArgumentType.word())
								.suggests((c, b) -> net.minecraft.commands.SharedSuggestionProvider.suggest(previews(), b))
								.executes(c -> preview(c.getSource().getPlayerOrException(),
										com.mojang.brigadier.arguments.StringArgumentType.getString(c, "name")))))));
		NeoForge.EVENT_BUS.addListener((LivingIncomingDamageEvent e) -> {
			if (friendly(e.getSource().getEntity(), e.getEntity())) e.setCanceled(true);
		});
	}

	// ---------------------------------------------------------------- mana

	public static float mana(Player p) {
		return p.level().isClientSide ? clientMana : p.getData(MANA);
	}

	public static float max(Player p) {
		return (float) p.getAttributeValue(MAX_MANA);
	}

	private static final String LAST_CAST = "ashbound_last_cast";

	private static void regen(ServerPlayer p) {
		float m = p.getData(MANA), cap = max(p);
		long since = p.level().getGameTime() - p.getPersistentData().getLong(LAST_CAST);
		// mana comes back while you cast too, faster once you stop: a full bar is about 10 s of nonstop bolts (docs/BALANCE.md pass 7)
		if (m < cap) m = Math.min(cap, m + (float) (cap * (since > 30 ? 0.14 : 0.06) * p.getAttributeValue(MANA_REGEN)) / 20f);
		if (m > cap) m = cap;
		if (m != p.getData(MANA)) p.setData(MANA, m);
		if (p.tickCount % 5 == 0) PacketDistributor.sendToPlayer(p, new Net.Mana(m, cap));
	}

	private static boolean spend(ServerPlayer p, float cost) {
		if (p.isCreative()) return true;
		float m = p.getData(MANA);
		if (m < cost) return false;
		p.setData(MANA, m - cost);
		p.getPersistentData().putLong(LAST_CAST, p.level().getGameTime());
		PacketDistributor.sendToPlayer(p, new Net.Mana(m - cost, max(p)));
		return true;
	}

	/** Martyr (the tree): with no mana a heal costs your own health instead, a fifth of its mana cost */
	private static boolean martyr(ServerPlayer p, Gear.Weapon w) {
		if (!w.kind().equals("white") || !Passives.has(p, "martyr") || p.getHealth() <= cost("white") / 5f + 1) return false;
		p.hurt(p.damageSources().magic(), cost("white") / 5f);
		return true;
	}

	// ---------------------------------------------------------------- the staffs

	static int cost(String school) {
		return switch (school) { case "white" -> 38; case "summon" -> 60; default -> 16; };
	}

	/** After any cast, how long until a staff of another school answers. */
	private static final int SWAP_COOLDOWN = 10;

	/** Every staff you carry waits, not just the one that cast, or swapping staffs is a way round it. */
	private static void rest(ServerPlayer p, String school) {
		for (ItemStack s : p.getInventory().items) lock(p, s, school);
		for (ItemStack s : p.getInventory().offhand) lock(p, s, school);
	}

	private static void lock(ServerPlayer p, ItemStack stack, String school) {
		if (!(stack.getItem() instanceof Staff staff)) return;
		if (staff.weapon.kind().equals(school)) p.getCooldowns().addCooldown(staff, cooldown(school));
		else if (!p.getCooldowns().isOnCooldown(staff)) p.getCooldowns().addCooldown(staff, SWAP_COOLDOWN);
	}

	static int cooldown(String school) {
		return switch (school) { case "white" -> 60; case "summon" -> 300; default -> 20; };
	}

	/** a staff's strength: its rank on the ladder, a boss's a touch more */
	static double power(Gear.Weapon w, Player p) {
		return Gear.scale(w.rank()) * (w.boss() ? 1.15 : 1) * p.getAttributeValue(SPELL_POWER) * Passives.spellMult(p) * Smithing.mult(p.getMainHandItem());
	}

	static Gear.Dungeon home(Gear.Weapon w) {
		if (Joined.ALL.contains(w)) return Gear.of("foundry");   // its fire is the Cold Forge's
		Gear.Dungeon world = WorldArms.home(w);
		if (world != null) return world;
		for (Gear.Dungeon d : Gear.DUNGEONS) if (d.weapons().contains(w)) return d;
		return Gear.DUNGEONS.get(0);
	}

	public static class Staff extends Item {
		/** swings a second: slower than a spear's 1.2. Without it a staff swings as fast as a bare fist */
		private static final double SWING = 1.0;
		final Gear.Weapon weapon;

		public Staff(Gear.Weapon weapon, Properties p) {
			super(p.attributes(net.minecraft.world.item.component.ItemAttributeModifiers.builder()
					.add(net.minecraft.world.entity.ai.attributes.Attributes.ATTACK_SPEED, new net.minecraft.world.entity.ai.attributes.AttributeModifier(Item.BASE_ATTACK_SPEED_ID, SWING - 4,
							net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation.ADD_VALUE), net.minecraft.world.entity.EquipmentSlotGroup.MAINHAND).build()));
			this.weapon = weapon;
		}

		@Override
		public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
			ItemStack stack = player.getItemInHand(hand);
			if (player.getCooldowns().isOnCooldown(this)) return InteractionResultHolder.fail(stack);
			if (level.isClientSide) return InteractionResultHolder.sidedSuccess(stack, true);
			ServerPlayer p = (ServerPlayer) player;
			if (!spend(p, cost(weapon.kind())) && !martyr(p, weapon)) {
				p.displayClientMessage(Component.literal("Not enough mana").withStyle(ChatFormatting.BLUE), true);
				return InteractionResultHolder.fail(stack);
			}
			CurioFx.onCast(p, cost(weapon.kind()));
			cast(p, weapon);
			rest(p, weapon.kind());
			stack.hurtAndBreak(1, p, hand == InteractionHand.MAIN_HAND ? net.minecraft.world.entity.EquipmentSlot.MAINHAND
					: net.minecraft.world.entity.EquipmentSlot.OFFHAND);
			return InteractionResultHolder.consume(stack);
		}

		@Override
		public void appendHoverText(ItemStack stack, TooltipContext ctx, List<Component> lines, TooltipFlag flag) {
			String what = switch (weapon.kind()) {
				case "white" -> "White staff: heals you and those near";
				case "summon" -> "Summoner staff: calls " + Component.translatable("entity.ashbound." + home(weapon).summon()).getString() + "s to fight for you";
				default -> "Black staff: hurls " + home(weapon).element().toLowerCase() + " bolts";
			};
			lines.add(Component.literal(what).withStyle(ChatFormatting.AQUA));
			lines.add(Component.literal(cost(weapon.kind()) + " mana").withStyle(ChatFormatting.BLUE));
			lines.add(Passives.staminaLine(null, stack));
			Gear.tooltip(weapon, lines);
		}
	}

	private static List<String> previews() {
		List<String> out = new ArrayList<>(List.of("heal", "radiance", "summon", "overload", "great_heal", "host", "braid"));
		for (Gear.Dungeon d : Gear.DUNGEONS) out.add(d.gate());
		return out;
	}

	private static int preview(ServerPlayer p, String name) {
		ServerLevel level = p.serverLevel();
		Vec3 ahead = p.position().add(p.getLookAngle().multiply(1, 0, 1).normalize().scale(6));
		Gear.Dungeon any = Gear.DUNGEONS.get(0);
		switch (name) {
			case "heal", "radiance" -> {
				fx(level, FX_HEAL, "", p.position(), 8, null);
				fx(level, FX_BLESS, "", p.position(), 0, p);
				for (LivingEntity m : level.getEntitiesOfClass(LivingEntity.class, p.getBoundingBox().inflate(8), m -> m instanceof Enemy && name.equals("radiance")))
					fx(level, FX_LANCE, "", m.position(), 0, m);
			}
			case "summon", "host" -> {
				boolean host = name.equals("host");
				fx(level, FX_SUMMON, any.gate(), ahead, host ? 7 : 3.6f, null);
				for (int k = 0; k < (host ? 6 : 2); k++) {
					double a = k * Math.PI * 2 / (host ? 6 : 2);
					fx(level, FX_RISE, any.gate(), ahead.add(Math.cos(a) * 2.4, 0, Math.sin(a) * 2.4), 0, null);
				}
			}
			case "overload" -> fx(level, FX_OVERLOAD, "foundry", ahead.add(0, 1, 0), 0, null);
			case "great_heal" -> {
				fx(level, FX_GREAT_HEAL, "", p.position(), 10, null);
				fx(level, FX_BLESS, "", p.position(), 0, p);
			}
			case "braid" -> {
				fx(level, FX_CAST, "foundry", p.getEyePosition(), 2, p);
				for (int i = 0; i < 3; i++) fire(p, "foundry", 1.5, 0, false, i);
			}
			default -> {
				if (Gear.of(name) == null) return 0;
				fx(level, FX_CAST, name, p.getEyePosition(), 1, p);
				fire(p, name, 1.6, 0, false, -1);
			}
		}
		return 1;
	}

	/** One bolt, off along where you're looking; braid 0-2 wind round each other. */
	private static void fire(ServerPlayer p, String gate, double speed, float damage, boolean overload, int braid) {
		ServerLevel level = p.serverLevel();
		Bolt b = new Bolt(BOLT.get(), level);
		b.setOwner(p);
		Vec3 look = p.getLookAngle();
		b.setPos(p.getX() + look.x * 0.8, p.getEyeY() - 0.2 + look.y * 0.8, p.getZ() + look.z * 0.8);
		b.setDeltaMovement(look.scale(speed));
		b.damage = damage;
		b.overload = overload;
		b.setGate(gate);
		b.setBraid(braid);
		level.addFreshEntity(b);
	}

	static void cast(ServerPlayer p, Gear.Weapon w) {
		if (Passives.titanLocked(p)) {
			p.displayClientMessage(net.minecraft.network.chat.Component.literal("Titan's Grip: only two-handers answer you")
					.withStyle(net.minecraft.ChatFormatting.RED), true);
			return;
		}
		Gear.Dungeon d = home(w);
		double pw = power(w, p);
		ServerLevel level = p.serverLevel();
		switch (w.kind()) {
			case "white" -> heal(p, d, pw);
			case "summon" -> summon(p, d, w.boss() ? 3 : 2, pw);
			default -> {
				fx(level, FX_CAST, d.gate(), p.getEyePosition(), 1, p);
				fire(p, d.gate(), 1.6, (float) (20.0 * pw), Passives.overload(p), -1);
				level.playSound(null, p.blockPosition(), SoundEvents.BLAZE_SHOOT, SoundSource.PLAYERS, 0.6f, 1.4f);
			}
		}
		p.swing(InteractionHand.MAIN_HAND, true);
	}

	static DustParticleOptions dust(int rgb, float size) {
		return new DustParticleOptions(new Vector3f((rgb >> 16 & 255) / 255f, (rgb >> 8 & 255) / 255f, (rgb & 255) / 255f), size);
	}

	/** each element's own spark next to its coloured dust */
	static ParticleOptions spark(String gate) {
		return switch (gate) {
			case "foundry", "crypt" -> ParticleTypes.FLAME;
			case "clockwork_spire" -> ParticleTypes.ELECTRIC_SPARK;
			case "ossuary" -> ParticleTypes.SOUL_FIRE_FLAME;
			case "frost" -> ParticleTypes.SNOWFLAKE;
			case "temple" -> ParticleTypes.END_ROD;
			case "rotwood", "plague" -> ParticleTypes.SPORE_BLOSSOM_AIR;
			case "gallows" -> ParticleTypes.SMOKE;
			case "silk" -> ParticleTypes.WHITE_ASH;
			case "weeping_mine", "storm_bastion" -> ParticleTypes.ELECTRIC_SPARK;
			case "tide_chapel", "abyssal_lighthouse" -> ParticleTypes.BUBBLE_POP;
			case "brigands_gorge", "rookery" -> ParticleTypes.SMOKE;
			case "hollow_circus" -> ParticleTypes.NOTE;
			case "mirefen_coven" -> ParticleTypes.WITCH;
			case "sandsunk_tomb", "eclipse_cathedral" -> ParticleTypes.WAX_ON;
			case "fallen_titan", "bloodmoon_court" -> ParticleTypes.DAMAGE_INDICATOR;
			case "jade_monastery" -> ParticleTypes.HAPPY_VILLAGER;
			case "obsidian_labyrinth", "wyrms_hoard" -> ParticleTypes.LAVA;
			default -> ParticleTypes.FALLING_DRIPSTONE_WATER;
		};
	}

	/** what a black bolt of each element does besides the hurt */
	static void element(String gate, LivingEntity t, int seconds) {
		switch (gate) {
			case "cellar" -> t.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, seconds * 20, 1));
			case "gallows", "ossuary" -> t.addEffect(new MobEffectInstance(MobEffects.WITHER, seconds * 20, 0));
			case "rotwood", "plague" -> t.addEffect(new MobEffectInstance(MobEffects.POISON, seconds * 25, 0));
			case "crypt", "foundry", "clockwork_spire" -> t.igniteForSeconds(seconds + 1);
			case "temple" -> t.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, seconds * 12, 3));
			case "frost" -> {
				t.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, seconds * 20, 2));
				t.setTicksFrozen(Math.max(t.getTicksFrozen(), 200));
			}
			case "silk" -> t.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, seconds * 10, 5));
			case "weeping_mine", "storm_bastion" -> t.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, seconds * 20, 1));
			case "tide_chapel", "abyssal_lighthouse" -> {
				t.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, seconds * 15, 1));
				t.addEffect(new MobEffectInstance(MobEffects.DARKNESS, seconds * 15, 0));
			}
			case "brigands_gorge", "rookery", "hollow_circus" -> t.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, seconds * 20, 0));
			case "mirefen_coven", "fallen_titan", "bloodmoon_court" -> t.addEffect(new MobEffectInstance(MobEffects.WITHER, seconds * 20, 1));
			case "sandsunk_tomb", "obsidian_labyrinth", "wyrms_hoard", "eclipse_cathedral" -> t.igniteForSeconds(seconds + 2);
			case "jade_monastery" -> t.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, seconds * 15, 2));
			default -> {}
		}
	}

	// ---------------------------------------------------------------- the Joined staffs' R skills (JoinedSkills)

	/** Three bolts at once, each twice a staff's, wound round each other. */
	static void accordBolts(ServerPlayer p, Gear.Weapon w) {
		ServerLevel level = p.serverLevel();
		double pw = power(w, p);
		fx(level, FX_CAST, home(w).gate(), p.getEyePosition(), 2, p);
		for (int i = 0; i < 3; i++) fire(p, home(w).gate(), 1.5, (float) (40.0 * pw), Passives.overload(p), i);
		level.playSound(null, p.blockPosition(), SoundEvents.BLAZE_SHOOT, SoundSource.PLAYERS, 1f, 0.7f);
	}

	/** Everyone near back up by a third, and a guard of golden hearts. */
	static void accordHeal(ServerPlayer p) {
		ServerLevel level = p.serverLevel();
		fx(level, FX_GREAT_HEAL, "", p.position(), 10, null);
		for (Player o : level.getEntitiesOfClass(Player.class, p.getBoundingBox().inflate(10))) {
			o.heal(o.getMaxHealth() * 0.35f);
			o.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.ABSORPTION, 300, 2));
			fx(level, FX_BLESS, "", o.position(), 0, o);
		}
		level.playSound(null, p.blockPosition(), SoundEvents.BEACON_POWER_SELECT, SoundSource.PLAYERS, 1f, 1.2f);
	}

	/** Twice the usual host. */
	static void accordSummon(ServerPlayer p, Gear.Weapon w) {
		summon(p, home(w), 6, power(w, p));
	}

	private static void heal(ServerPlayer p, Gear.Dungeon d, double pw) {
		ServerLevel level = p.serverLevel();
		// the tree: Mending Aura reaches further and heals more, Martyr heals more, Purify, Blessing, Sanctuary
		boolean aura = Passives.has(p, "heal_chain");
		int reach = aura ? 12 : 8;
		float amount = (float) (9.0 * pw * (aura ? 1.15 : 1) * (Passives.has(p, "martyr") ? 1.5 : 1));
		boolean purify = Passives.has(p, "purify"), bless = Passives.has(p, "blessing");
		List<LivingEntity> near = level.getEntitiesOfClass(LivingEntity.class, p.getBoundingBox().inflate(reach),
				e -> e == p || e instanceof Player || ownerOf(e) != null);
		for (LivingEntity e : near) {
			e.heal(amount);
			if (purify) for (var bad : List.of(MobEffects.POISON, MobEffects.WITHER, MobEffects.MOVEMENT_SLOWDOWN)) e.removeEffect(bad);
			if (bless) Passives.blessed(e, level.getGameTime() + 100);
			e.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 80, 0));
			fx(level, FX_BLESS, d.gate(), e.position(), 0, e);
		}
		fx(level, FX_HEAL, d.gate(), p.position(), reach, null);
		// the tree: Aegis shields whoever was healed, Radiance burns the monsters in reach
		if (Passives.has(p, "aegis")) for (LivingEntity e : near) {
			e.addEffect(new MobEffectInstance(MobEffects.ABSORPTION, 200, 0));
			fx(level, FX_GUARD, d.gate(), e.position(), 0, e);
		}
		if (Passives.has(p, "radiance"))
			for (LivingEntity m : level.getEntitiesOfClass(LivingEntity.class, p.getBoundingBox().inflate(reach),
					m -> m instanceof net.minecraft.world.entity.monster.Enemy && ownerOf(m) == null && m.isAlive())) {
				m.hurt(p.damageSources().indirectMagic(p, p), amount * 0.5f);
				fx(level, FX_LANCE, d.gate(), m.position(), 0, m);
			}
		if (Passives.has(p, "sanctuary")) {
			var cloud = new net.minecraft.world.entity.AreaEffectCloud(level, p.getX(), p.getY(), p.getZ());
			cloud.setOwner(p);
			cloud.setRadius(3.5f);
			cloud.setRadiusPerTick(0);
			cloud.setDuration(80);
			cloud.setParticle(Vfx.wisp(d.colour(), 0.3f, 16, -0.01f, true));
			fx(level, FX_WARD, d.gate(), p.position(), 3.5f, null);
			cloud.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 40, 1));
			level.addFreshEntity(cloud);
		}
		CurioFx.healed(p, near);
		level.playSound(null, p.blockPosition(), SoundEvents.AMETHYST_BLOCK_RESONATE, SoundSource.PLAYERS, 1f, 1.2f);
	}

	/** one thrall of any kind for a while (the curios' broodlings and ghost warriors): hp and hit before the tree's bonuses */
	static Mob thrall(ServerPlayer p, EntityType<?> type, double x, double y, double z, int ticks, double hp, double dmg) {
		ServerLevel level = p.serverLevel();
		if (!(type.create(level) instanceof Mob m)) return null;
		m.moveTo(x, y, z, p.getYRot(), 0);
		m.finalizeSpawn(level, level.getCurrentDifficultyAt(m.blockPosition()), MobSpawnType.MOB_SUMMONED, null);
		m.addTag(THRALL);
		m.targetSelector.removeAllGoals(g -> true);
		m.targetSelector.addGoal(1, new Guard(m, p));
		m.goalSelector.addGoal(3, new Heel(m, p));
		var h = m.getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.MAX_HEALTH);
		if (h != null) {
			h.setBaseValue(hp * (1 + Passives.stat(p, "thrall_hp%") / 100));
			m.setHealth(m.getMaxHealth());
		}
		var d = m.getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.ATTACK_DAMAGE);
		if (d != null) d.setBaseValue(dmg * (1 + Passives.stat(p, "thrall_dmg%") / 100));
		level.addFreshEntity(m);
		fx(level, FX_RISE, "", new Vec3(x, y, z), 0, null);
		THRALLS.add(new Thrall(m, p.getUUID(), level.getGameTime() + ticks));
		return m;
	}

	// ---------------------------------------------------------------- summons: thralls of the one who called them

	private record Thrall(Mob mob, UUID owner, long until) {}

	private static final List<Thrall> THRALLS = new ArrayList<>();
	private static final int THRALL_GLOW = 0x9A5AD8;
	static final String THRALL = "ashbound_thrall";
	/** a thrall's hit before spell power (tools/balance.py THRALL_DMG): four of them about match a sword */
	static final double THRALL_DMG = 4.3;

	public static boolean isThrall(Entity e) {
		return e.getTags().contains(THRALL);
	}

	/** how many thralls someone has out */
	static int thralls(Player p) {
		return (int) THRALLS.stream().filter(t -> t.owner().equals(p.getUUID())).count();
	}

	static UUID ownerOf(Entity e) {
		for (Thrall t : THRALLS) if (t.mob() == e) return t.owner();
		return null;
	}

	private static void summon(ServerPlayer p, Gear.Dungeon d, int count, double pw) {
		ServerLevel level = p.serverLevel();
		EntityType<?> type = BuiltInRegistries.ENTITY_TYPE.get(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, d.summon()));
		// at most four at once (six with Legion): the oldest goes
		int most = Passives.has(p, "legion") ? 6 : 4;
		List<Thrall> mine = THRALLS.stream().filter(t -> t.owner().equals(p.getUUID())).toList();
		for (int k = 0; k < mine.size() + count - most; k++) {
			mine.get(k).mob().discard();
			THRALLS.remove(mine.get(k));
		}
		fx(level, FX_SUMMON, d.gate(), p.position().add(p.getLookAngle().multiply(1, 0, 1).normalize().scale(1.5)), count > 3 ? 7 : 3.6f, null);
		for (int k = 0; k < count; k++) {
			double a = p.getYRot() * Math.PI / 180 + (k - (count - 1) / 2.0) * 0.9;
			double x = p.getX() - Math.sin(a) * 2.2, z = p.getZ() + Math.cos(a) * 2.2;
			Entity e = type.create(level);
			if (!(e instanceof Mob m)) return;
			m.moveTo(x, p.getY(), z, p.getYRot(), 0);
			m.finalizeSpawn(level, level.getCurrentDifficultyAt(m.blockPosition()), MobSpawnType.MOB_SUMMONED, null);
			m.addTag(THRALL);
			m.targetSelector.removeAllGoals(g -> true);
			m.targetSelector.addGoal(1, new Guard(m, p));
			m.goalSelector.addGoal(3, new Heel(m, p));
			var hp = m.getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.MAX_HEALTH);
			if (hp != null) {
				hp.setBaseValue(hp.getBaseValue() * pw * (1 + Passives.stat(p, "thrall_hp%") / 100));
				m.setHealth(m.getMaxHealth());
			}
			var dmg = m.getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.ATTACK_DAMAGE);
			if (dmg != null) dmg.setBaseValue(THRALL_DMG * pw * (1 + Passives.stat(p, "thrall_dmg%") / 100)); // the same for every school's thrall
			level.addFreshEntity(m);
			fx(level, FX_RISE, d.gate(), new Vec3(x, p.getY(), z), 0, null);
			THRALLS.add(new Thrall(m, p.getUUID(), level.getGameTime() + (Passives.has(p, "long_thralls") ? 900 : 600)));
		}
		level.playSound(null, p.blockPosition(), SoundEvents.EVOKER_PREPARE_SUMMON, SoundSource.PLAYERS, 1f, 1f);
	}

	private static void tickThralls() {
		for (Iterator<Thrall> it = THRALLS.iterator(); it.hasNext(); ) {
			Thrall t = it.next();
			Mob m = t.mob();
			if (m.isRemoved() || !m.isAlive()) {
				it.remove();
				continue;
			}
			ServerLevel level = (ServerLevel) m.level();
			Player owner = level.getPlayerByUUID(t.owner());
			if (owner == null || level.getGameTime() > t.until()) {
				fx(level, FX_GONE, "", m.position(), 0, null);
				m.discard();
				it.remove();
				continue;
			}
			if (m.distanceToSqr(owner) > 32 * 32) m.teleportTo(owner.getX() + 1, owner.getY(), owner.getZ() + 1);
			if (m.tickCount % 6 == 0) level.sendParticles(Vfx.wisp(THRALL_GLOW, 0.35f, 14, -0.02f, true), m.getX(), m.getY() + 0.15, m.getZ(), 1, 0.3, 0, 0.3, 0.005);
		}
	}

	/** no friendly fire: thralls and players of a side don't hurt each other */
	private static boolean friendly(Entity attacker, Entity victim) {
		if (attacker == null) return false;
		boolean a = isThrall(attacker) || attacker instanceof Player, v = isThrall(victim) || victim instanceof Player;
		if (attacker instanceof Player && victim instanceof Player) return false;   // PvP stays as the server sets it
		return a && v && (isThrall(attacker) || isThrall(victim));
	}

	/** a thrall fights whatever fights its caller, or whatever its caller fights, else the nearest monster */
	static final class Guard extends TargetGoal {
		private final Player owner;

		Guard(Mob m, Player owner) {
			super(m, false);
			this.owner = owner;
			setFlags(EnumSet.of(Flag.TARGET));
		}

		private LivingEntity pick() {
			LivingEntity t = owner.getLastHurtByMob();
			if (t == null || !t.isAlive() || isThrall(t)) t = owner.getLastHurtMob();
			if (t != null && t.isAlive() && !isThrall(t) && !(t instanceof Player)) return t;
			LivingEntity best = null;
			double bd = 16 * 16;
			for (Mob e : mob.level().getEntitiesOfClass(Mob.class, mob.getBoundingBox().inflate(16), e -> e instanceof Enemy && !isThrall(e) && e.isAlive())) {
				double dd = e.distanceToSqr(mob);
				if (dd < bd) {
					bd = dd;
					best = e;
				}
			}
			return best;
		}

		@Override
		public boolean canUse() {
			LivingEntity t = pick();
			if (t == null) return false;
			targetMob = t;
			return true;
		}

		@Override
		public void start() {
			mob.setTarget(targetMob);
			super.start();
		}

		@Override
		public boolean canContinueToUse() {
			LivingEntity t = mob.getTarget();
			return t != null && t.isAlive() && !isThrall(t) && !(t instanceof Player) && mob.distanceToSqr(t) < 24 * 24;
		}
	}

	/** keeps a thrall near its caller when there's nothing to fight */
	static final class Heel extends Goal {
		private final Mob mob;
		private final Player owner;

		Heel(Mob mob, Player owner) {
			this.mob = mob;
			this.owner = owner;
			setFlags(EnumSet.of(Flag.MOVE));
		}

		@Override
		public boolean canUse() {
			return mob.getTarget() == null && mob.distanceToSqr(owner) > 36;
		}

		@Override
		public void tick() {
			mob.getNavigation().moveTo(owner, 1.1);
		}

		@Override
		public boolean canContinueToUse() {
			return mob.getTarget() == null && mob.distanceToSqr(owner) > 9;
		}
	}

	// ---------------------------------------------------------------- the black staffs' bolt

	public static class Bolt extends Projectile {
		private static final EntityDataAccessor<String> GATE = SynchedEntityData.defineId(Bolt.class, EntityDataSerializers.STRING);
		private static final EntityDataAccessor<Integer> BRAID = SynchedEntityData.defineId(Bolt.class, EntityDataSerializers.INT);
		private static final double BRAID_WIDE = 0.55, BRAID_TURN = 0.55;
		float damage = 6;
		boolean overload;
		/** on the client: its look has been put on it */
		public boolean dressed;
		private Entity hit;

		public Bolt(EntityType<? extends Bolt> type, Level level) {
			super(type, level);
			setNoGravity(true);
		}

		@Override
		protected void defineSynchedData(SynchedEntityData.Builder b) {
			b.define(GATE, "cellar");
			b.define(BRAID, -1);
		}

		void setBraid(int i) {
			entityData.set(BRAID, i);
		}

		/** Where braiding puts it off its straight line at this age. */
		private Vec3 braid(int t, Vec3 v, int i) {
			Vec3 side = v.cross(new Vec3(0, 1, 0));
			side = side.lengthSqr() < 1e-4 ? new Vec3(1, 0, 0) : side.normalize();
			Vec3 up = side.cross(v).normalize();
			double a = i * Math.PI * 2 / 3 + t * BRAID_TURN, wide = BRAID_WIDE * Math.min(1, t / 6.0);
			return side.scale(Math.cos(a) * wide).add(up.scale(Math.sin(a) * wide));
		}

		void setGate(String g) {
			entityData.set(GATE, g);
		}

		public String gate() {
			return entityData.get(GATE);
		}

		@Override
		public void tick() {
			super.tick();
			HitResult hit = ProjectileUtil.getHitResultOnMoveVector(this, this::canHitEntity);
			if (hit.getType() != HitResult.Type.MISS) hitTargetOrDeflectSelf(hit);
			if (isRemoved()) return;
			Vec3 v = getDeltaMovement();
			int i = entityData.get(BRAID);
			Vec3 turn = i < 0 ? Vec3.ZERO : braid(tickCount + 1, v, i).subtract(braid(tickCount, v, i));
			setPos(getX() + v.x + turn.x, getY() + v.y + turn.y, getZ() + v.z + turn.z);
			if (level().isClientSide) onBolt.accept(this);
			else if (tickCount > 50) discard();
		}

		@Override
		protected boolean canHitEntity(Entity e) {
			return super.canHitEntity(e) && !(e instanceof Player) && !isThrall(e);
		}

		@Override
		protected void onHitEntity(EntityHitResult r) {
			if (level().isClientSide) return;
			Entity owner = getOwner();
			if (r.getEntity() instanceof LivingEntity t) {
				t.hurt(damageSources().indirectMagic(this, owner), damage);
				element(gate(), t, owner instanceof Player p && Passives.has(p, "long_effects") ? 6 : 3);
				if (overload) {
					// Overload (the tree): the sixth bolt bursts over everything near what it hit
					for (LivingEntity m : level().getEntitiesOfClass(LivingEntity.class, t.getBoundingBox().inflate(3),
							m -> m != t && m != owner && !(m instanceof Player) && !isThrall(m)))
						m.hurt(damageSources().indirectMagic(this, owner), damage * 0.5f);
					fx((ServerLevel) level(), FX_OVERLOAD, gate(), position(), 0, null);
				}
			}
			hit = r.getEntity();
			burst();
		}

		@Override
		protected void onHitBlock(BlockHitResult r) {
			super.onHitBlock(r);
			if (!level().isClientSide) burst();
		}

		private void burst() {
			ServerLevel s = (ServerLevel) level();
			fx(s, FX_HIT, gate(), position().add(0, 0.2, 0), 1, hit);
			s.playSound(null, blockPosition(), SoundEvents.GENERIC_EXPLODE.value(), SoundSource.PLAYERS, 0.3f, 1.8f);
			discard();
		}
	}
}
