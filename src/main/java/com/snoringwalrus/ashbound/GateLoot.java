package com.snoringwalrus.ashbound;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import net.minecraft.ChatFormatting;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;

/**
 * What a gate's dwellers leave (docs/GEAR.md, rates in docs/BALANCE.md), each player rolling their own so a party of five gets five shares:
 * half of them a common drop, casters now and then the elite drop, the elite (the key-holder) both, and the boss its trophy, a handful of
 * the rest and a one-in-five chance of one of its six boss weapons, picked at random, that climbs with every miss.
 */
public final class GateLoot {
	private GateLoot() {}

	enum Role { COMMON, CASTER, ELITE, BOSS }

	private record Who(Gear.Dungeon dungeon, Role role) {}

	private static final Map<String, Who> WHO = new HashMap<>();

	static void register() {
		for (Gear.Dungeon d : Gear.DUNGEONS) {
			for (String m : d.mobs()) WHO.put(m, new Who(d, d.casters().contains(m) ? Role.CASTER : Role.COMMON));
			WHO.put(d.elite(), new Who(d, Role.ELITE));
			WHO.put(d.boss(), new Who(d, Role.BOSS));
		}
		NeoForge.EVENT_BUS.addListener((LivingDeathEvent e) -> {
			if (!e.getEntity().level().isClientSide) drop(e.getEntity());
		});
	}

	/** a gate's elite (its key-holder) */
	static boolean elite(LivingEntity e) {
		var key = BuiltInRegistries.ENTITY_TYPE.getKey(e.getType());
		Who w = key.getNamespace().equals(Ashbound.ID) ? WHO.get(key.getPath()) : null;
		return w != null && w.role() == Role.ELITE;
	}

	/** Temper Embers: a boss always leaves one or two each, these are the rest. */
	private static final float EMBER_COMMON = 0.03f, EMBER_ELITE = 0.35f;

	private static ItemStack mat(Gear.Dungeon d, int which, int n) {
		Item it = Gear.item(d.mats()[which]);
		return it == null ? ItemStack.EMPTY : new ItemStack(it, n);
	}

	/** owner: only they can pick it up */
	private static void spill(LivingEntity e, ItemStack s, @org.jetbrains.annotations.Nullable ServerPlayer owner) {
		if (s.isEmpty()) return;
		ItemEntity ie = new ItemEntity(e.level(), e.getX(), e.getY() + 0.5, e.getZ(), s);
		ie.setDefaultPickUpDelay();
		if (owner != null) ie.setTarget(owner.getUUID());
		e.level().addFreshEntity(ie);
	}

	/** Everyone near the kill, and their party a little further off. */
	private static List<ServerPlayer> fighters(LivingEntity e) {
		List<ServerPlayer> near = new java.util.ArrayList<>(e.level().getEntitiesOfClass(ServerPlayer.class, e.getBoundingBox().inflate(Balance.radius()), p -> !p.isSpectator()));
		near.addAll(Party.alongside(near, Party.SHARE));
		return near;
	}

	private static void give(ServerPlayer p, ItemStack s) {
		if (s.isEmpty()) return;
		if (!p.getInventory().add(s)) p.drop(s, false);
	}

	private static void drop(LivingEntity e) {
		if (Spells.isThrall(e)) return;
		var key = BuiltInRegistries.ENTITY_TYPE.getKey(e.getType());
		if (!key.getNamespace().equals(Ashbound.ID)) return;
		Who w = WHO.get(key.getPath());
		if (w == null) return;
		RandomSource r = e.getRandom();
		Gear.Dungeon d = w.dungeon();
		if (w.role() == Role.BOSS) {
			boss(e, d, r);
			return;
		}
		List<ServerPlayer> near = fighters(e);
		for (ServerPlayer p : near) {
			ServerPlayer own = near.size() > 1 ? p : null;
			switch (w.role()) {
				// rates from tools/balance.py MATS: a full set takes about two clears, a weapon about half of one
				case COMMON -> {
					if (r.nextFloat() < 0.5f) spill(e, mat(d, 0, 1), own);
					if (r.nextFloat() < EMBER_COMMON) spill(e, new ItemStack(Smithing.TEMPER.get()), own);
				}
				case CASTER -> {
					if (r.nextFloat() < 0.5f) spill(e, mat(d, 0, 1), own);
					if (r.nextFloat() < 0.05f) spill(e, mat(d, 1, 1), own);
					if (r.nextFloat() < EMBER_COMMON) spill(e, new ItemStack(Smithing.TEMPER.get()), own);
				}
				default -> {
					spill(e, mat(d, 0, 3), own);
					spill(e, mat(d, 1, 1), own);
					if (r.nextFloat() < EMBER_ELITE) spill(e, new ItemStack(Smithing.TEMPER.get()), own);
				}
			}
		}
	}

	/** A boss weapon's chance, and what each boss without one adds: soft bad-luck protection, so ten at the very worst. */
	static final float WEAPON_ODDS = 0.20f, WEAPON_MISS = 0.09f;

	static float weaponOdds(int misses) {
		return Math.min(1, WEAPON_ODDS + WEAPON_MISS * misses);
	}

	private static void boss(LivingEntity e, Gear.Dungeon d, RandomSource r) {
		ServerLevel level = (ServerLevel) e.level();
		List<ServerPlayer> fought = level.getEntitiesOfClass(ServerPlayer.class, e.getBoundingBox().inflate(64), p -> !p.isSpectator());
		List<Gear.Weapon> pool = d.bossWeapons();
		for (ServerPlayer p : fought) {
			if (level.dimension() == Lairs.GATES) ColdForge.bossDown(p, d);   // not a tower's, or one that got out
			Story.mark(p, "kill/" + d.boss());
			give(p, mat(d, 2, 1));
			give(p, new ItemStack(Smithing.TEMPER.get(), 1 + r.nextInt(2)));
			give(p, mat(d, 1, 1 + r.nextInt(2)));
			give(p, mat(d, 0, 4 + r.nextInt(4)));
			Books.drops(p, d.rank(), r).forEach(b -> give(p, b));
			if (pool.isEmpty()) continue;
			if (r.nextFloat() >= weaponOdds(p.getData(Levels.BOSS_MISSES))) p.setData(Levels.BOSS_MISSES, p.getData(Levels.BOSS_MISSES) + 1);
			else {
				p.setData(Levels.BOSS_MISSES, 0);
				Gear.Weapon w = pool.get(r.nextInt(pool.size()));
				Item it = Gear.item(w.id());
				if (it == null) continue;
				give(p, new ItemStack(it));
				Story.mark(p, "story/boss_weapon");
				p.sendSystemMessage(Component.translatable("entity.ashbound." + d.boss()).append(" left you ")
						.append(Component.literal(w.name()).withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD)).append("!"));
				level.playSound(null, p.blockPosition(), SoundEvents.UI_TOAST_CHALLENGE_COMPLETE, SoundSource.PLAYERS, 0.8f, 1f);
			}
		}
		if (level.dimension() == Lairs.GATES) Guild.gateClosed(fought, d.rank());
	}
}
