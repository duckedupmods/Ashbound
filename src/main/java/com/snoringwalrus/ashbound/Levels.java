package com.snoringwalrus.ashbound;

import java.util.List;
import java.util.function.Supplier;

import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.serialization.Codec;

import net.minecraft.ChatFormatting;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.attachment.AttachmentType;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.network.PacketDistributor;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.registries.NeoForgeRegistries;

/**
 * Your level (1-100) and Ash (docs/BALANCE.md pass 3). Every solved monster pays Ash and coins by its health and
 * rank (tools/balance.py), to everyone fighting near it and their party a little further off, each in full, so a party isn't punished. Ash buys levels
 * in the tree (K, Passives); each level is a point for it and a little more health.
 */
public final class Levels {
	private Levels() {}

	static final DeferredRegister<AttachmentType<?>> ATTACHMENTS = DeferredRegister.create(NeoForgeRegistries.ATTACHMENT_TYPES, Ashbound.ID);

	public static final Supplier<AttachmentType<Integer>> LEVEL = ATTACHMENTS.register("level",
			() -> AttachmentType.builder(() -> 1).serialize(Codec.INT).copyOnDeath().build());
	public static final Supplier<AttachmentType<Integer>> ASH = ATTACHMENTS.register("ash",
			() -> AttachmentType.builder(() -> 0).serialize(Codec.INT).copyOnDeath().build());

	private static final ResourceLocation HEALTH = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "level");

	/** what the server last told this client */
	public static int clientLevel = 1, clientAsh, clientNext = 1;
	/** client: when Ash last came in, and the last level up (ms; the HUD shows them for a moment) */
	public static long clientGained, clientLevelled;

	/** Ash from this level to the next */
	public static int cost(int level) {
		return (int) Math.round(Balance.levelA * Math.pow(level, Balance.levelP));
	}

	public static int level(ServerPlayer p) {
		return p.getData(LEVEL);
	}

	static void register(IEventBus bus) {
		ATTACHMENTS.register(bus);
		NeoForge.EVENT_BUS.addListener(Levels::died);
		NeoForge.EVENT_BUS.addListener((PlayerEvent.PlayerLoggedInEvent e) -> {
			if (e.getEntity() instanceof ServerPlayer p) refresh(p, false);
		});
		NeoForge.EVENT_BUS.addListener((PlayerEvent.PlayerRespawnEvent e) -> {
			if (e.getEntity() instanceof ServerPlayer p) {
				refresh(p, false);
				p.setHealth(p.getMaxHealth());
			}
		});
		NeoForge.EVENT_BUS.addListener((PlayerEvent.PlayerChangedDimensionEvent e) -> {
			if (e.getEntity() instanceof ServerPlayer p) refresh(p, false);
		});
		NeoForge.EVENT_BUS.addListener((RegisterCommandsEvent e) -> e.getDispatcher().register(Commands.literal("ashbound")
				.requires(s -> s.hasPermission(2))
				.then(Commands.literal("ash").then(Commands.argument("n", IntegerArgumentType.integer(0))
						.executes(c -> cheatAsh(c.getSource(), IntegerArgumentType.getInteger(c, "n")))))
				.then(Commands.literal("level").then(Commands.argument("n", IntegerArgumentType.integer(1, 100))
						.executes(c -> cheatLevel(c.getSource(), IntegerArgumentType.getInteger(c, "n")))))));
	}

	private static void died(LivingDeathEvent e) {
		LivingEntity dead = e.getEntity();
		if (!(dead.level() instanceof ServerLevel level) || Spells.isThrall(dead)) return;
		ResourceLocation id = BuiltInRegistries.ENTITY_TYPE.getKey(dead.getType());
		if (!id.getNamespace().equals(Ashbound.ID)) return;
		Balance.Mult m = Balance.solved(id.getPath());
		if (m == null) return;
		// its own health (a foreman's raised one too), not what it grew for a party
		AttributeInstance hp = dead.getAttribute(Attributes.MAX_HEALTH);
		double worth = (hp != null ? hp.getBaseValue() : dead.getMaxHealth()) * Balance.paysFor(dead);
		String rank = Balance.paysAs(dead, m.rank());
		double ash = worth * Balance.ash(rank);
		int coins = (int) Math.round(worth * Balance.coins(rank));
		List<ServerPlayer> near = level.getEntitiesOfClass(ServerPlayer.class, dead.getBoundingBox().inflate(Balance.radius()), p -> !p.isSpectator());
		if (near.isEmpty() && e.getSource().getEntity() instanceof ServerPlayer killer) near = List.of(killer);
		near = new java.util.ArrayList<>(near);
		near.addAll(Party.alongside(near, Party.SHARE));
		double share = Balance.share(near.size());
		for (ServerPlayer p : near) {
			give(p, Math.max(1, (int) Math.round(ash * share * (1 + Passives.stat(p, "ash%") / 100))));
			if (coins > 0) Coins.give(p, (int) Math.round(coins * share * (1 + Passives.stat(p, "coins%") / 100)));
		}
	}

	public static void give(ServerPlayer p, int ash) {
		p.setData(ASH, (int) Math.min(Integer.MAX_VALUE, (long) p.getData(ASH) + ash));
		refresh(p, true);
	}

	/** buys one level with Ash (the tree's button): a point to spend and a little more health */
	static void levelUp(ServerPlayer p) {
		int lv = p.getData(LEVEL), ash = p.getData(ASH);
		if (lv >= Balance.maxLevel || ash < cost(lv)) return;
		lv++;
		p.setData(LEVEL, lv);
		p.setData(ASH, ash - cost(lv - 1));
		p.sendSystemMessage(Component.literal("Level " + lv).withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD)
				.append(Component.literal("  a point for the tree, +" + String.format(java.util.Locale.ROOT, "%.1f", Balance.hpPerLevel) + " health")
						.withStyle(ChatFormatting.GRAY)));
		p.level().playSound(null, p.blockPosition(), SoundEvents.PLAYER_LEVELUP, SoundSource.PLAYERS, 0.8f, 0.8f);
		health(p, lv, true);
		send(p, false, true);
		Skills.remind(p);
	}

	/** sets the health that goes with your level and tells the client */
	private static void refresh(ServerPlayer p, boolean gained) {
		health(p, p.getData(LEVEL), false);
		send(p, gained, false);
	}

	static void sync(ServerPlayer p) {
		send(p, false, false);
	}

	private static void send(ServerPlayer p, boolean gained, boolean up) {
		int lv = p.getData(LEVEL);
		PacketDistributor.sendToPlayer(p, new Net.Level(lv, p.getData(ASH), lv < Balance.maxLevel ? cost(lv) : 0, gained, up));
	}

	private static void health(ServerPlayer p, int lv, boolean heal) {
		AttributeInstance a = p.getAttribute(Attributes.MAX_HEALTH);
		if (a == null) return;
		double by = Balance.hpPerLevel * (lv - 1);
		AttributeModifier old = a.getModifier(HEALTH);
		if (old != null && old.amount() == by) return;
		a.removeModifier(HEALTH);
		if (by > 0) a.addPermanentModifier(new AttributeModifier(HEALTH, by, AttributeModifier.Operation.ADD_VALUE));
		if (heal) p.setHealth(p.getMaxHealth());
		else if (p.getHealth() > p.getMaxHealth()) p.setHealth(p.getMaxHealth());
	}

	private static int cheatAsh(CommandSourceStack src, int n) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
		give(src.getPlayerOrException(), n);
		return 1;
	}

	private static int cheatLevel(CommandSourceStack src, int n) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
		ServerPlayer p = src.getPlayerOrException();
		p.setData(LEVEL, n);
		p.setData(ASH, 0);
		refresh(p, false);
		health(p, n, true);
		Passives.sync(p);
		src.sendSuccess(() -> Component.literal("Level " + n + ", " + p.getMaxHealth() + " health"), false);
		return 1;
	}
}
