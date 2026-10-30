package com.snoringwalrus.ashbound;

import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import net.minecraft.core.component.DataComponents;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.CustomData;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.living.LivingDamageEvent;
import net.neoforged.neoforge.event.entity.living.LivingShieldBlockEvent;
import net.neoforged.neoforge.registries.DeferredItem;

/**
 * The Joined weapons, the Cold Forge's own (tools/joinedgear.py): one of each kind, made by laying two boss weapons of
 * a rank in its hands. What comes out stands a rank above them and a good step above any boss weapon of that rank, and
 * feeding it another boss weapon of at least its rank raises it, up to S+. Every fifth blow lets the seam go in a burst.
 */
public final class Joined {
	private Joined() {}

	/** What a Joined weapon's rank is called, from its stage; the boss ranks they stand on start one earlier. */
	private static final String[] RANK = {"", "C", "B", "A", "S", "S+"};
	private static final String LADDER = "DCBAS";
	public static final int TOP = 5;
	private static final double OVER_BOSS = 1.12, A_RANK = 1.08;
	private static final float BURST = 0.6f;
	private static final int EVERY = 5;

	public static final List<Gear.Weapon> ALL = new ArrayList<>();
	private static final Map<String, Gear.Weapon> BY_ID = new HashMap<>(), BY_KIND = new HashMap<>();

	static void init() {
		try (var in = new InputStreamReader(Joined.class.getResourceAsStream("/ashbound/joined.json"), StandardCharsets.UTF_8)) {
			for (JsonElement e : JsonParser.parseReader(in).getAsJsonArray()) {
				JsonObject o = e.getAsJsonObject();
				Gear.Weapon w = new Gear.Weapon(o.get("id").getAsString(), o.get("name").getAsString(), o.get("kind").getAsString(), 'D', true,
						new Gear.Cost(0, 0, 0), o.get("damage").getAsDouble(), o.get("speed").getAsDouble());
				ALL.add(w);
				BY_ID.put(w.id(), w);
				BY_KIND.put(w.kind(), w);
				Gear.WEAPON.put(w.id(), w);
				DeferredItem<net.minecraft.world.item.Item> it = Weapons.ITEMS.registerItem(w.id(), p -> Gear.weapon(w, p));
				Gear.ITEMS.put(w.id(), it);
				Gear.WEAPONS.add(it);
			}
		} catch (java.io.IOException e) {
			throw new IllegalStateException("joined.json", e);
		}
		NeoForge.EVENT_BUS.addListener(Joined::onHit);
		NeoForge.EVENT_BUS.addListener(Joined::onBlock);
	}

	private static String id(ItemStack s) {
		return net.minecraft.core.registries.BuiltInRegistries.ITEM.getKey(s.getItem()).getPath();
	}

	public static boolean is(ItemStack s) {
		return BY_ID.containsKey(id(s));
	}

	public static Gear.Weapon of(String kind) {
		return BY_KIND.get(kind);
	}

	public static int stage(ItemStack s) {
		CustomData c = s.get(DataComponents.CUSTOM_DATA);
		return c == null ? 0 : c.copyTag().getInt("ash_joined");
	}

	static void setStage(ItemStack s, int stage) {
		CompoundTag t = s.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag();
		t.putInt("ash_joined", stage);
		s.set(DataComponents.CUSTOM_DATA, CustomData.of(t));
	}

	public static String rank(int stage) {
		return RANK[Math.max(0, Math.min(TOP, stage))];
	}

	/** How much above its item's own stats a Joined weapon of this stage stands (Smithing.mult). */
	static double mult(ItemStack s) {
		int st = stage(s);
		return st <= 0 ? 1 : OVER_BOSS * Math.pow(A_RANK, st);
	}

	/** What two pieces would make, as a stage: 0 if they can't be joined. Two boss weapons of a kind and rank, or a Joined weapon first and a boss weapon of at least its rank. */
	public static int after(ItemStack a, ItemStack b) {
		if (a.isEmpty() || b.isEmpty() || is(b)) return 0;
		Gear.Weapon wb = Smithing.boss(b);
		if (wb == null) return 0;
		int rb = LADDER.indexOf(wb.rank());
		if (is(a)) {
			int st = stage(a);
			if (st >= TOP || !Gear.WEAPON.get(id(a)).kind().equals(wb.kind()) || rb < st) return 0;
			return Math.min(TOP, Math.max(st, rb) + 1);
		}
		Gear.Weapon wa = Smithing.boss(a);
		return wa != null && wa.kind().equals(wb.kind()) && wa.rank() == wb.rank() ? Math.min(TOP, rb + 1) : 0;
	}

	/** The slots of what could go in with the piece in `slot`. */
	public static List<Integer> seconds(Player p, int slot) {
		var items = p.getInventory().items;
		List<Integer> out = new ArrayList<>();
		for (int i = 0; i < items.size(); i++) if (i != slot && after(items.get(slot), items.get(i)) > 0) out.add(i);
		return out;
	}

	/** Whether this piece can go first at the Cold Forge at all. */
	public static boolean canLead(ItemStack s) {
		return is(s) ? stage(s) < TOP : Smithing.boss(s) != null;
	}

	/** The piece the pair would make, as it will be shown. */
	public static ItemStack result(ItemStack a, ItemStack b) {
		Gear.Weapon w = of(Smithing.boss(a).kind());
		ItemStack s = new ItemStack(Gear.item(w.id()));
		setStage(s, after(a, b));
		return s;
	}

	// ---------------------------------------------------------------- the seam letting go

	private static final Map<UUID, Integer> COUNT = new HashMap<>();
	private static boolean bursting;

	private static boolean counted(ServerPlayer p) {
		int n = COUNT.merge(p.getUUID(), 1, Integer::sum);
		if (n < EVERY) return false;
		COUNT.put(p.getUUID(), 0);
		return true;
	}

	private static void burst(ServerPlayer p, LivingEntity at, float amount) {
		ServerLevel level = p.serverLevel();
		level.sendParticles(ParticleTypes.FLAME, at.getX(), at.getY(0.5), at.getZ(), 40, 0.5, 0.4, 0.5, 0.18);
		level.sendParticles(ParticleTypes.LAVA, at.getX(), at.getY(0.5), at.getZ(), 8, 0.4, 0.3, 0.4, 0);
		level.playSound(null, at.blockPosition(), SoundEvents.FIRECHARGE_USE, SoundSource.PLAYERS, 0.8f, 0.7f);
		level.playSound(null, at.blockPosition(), SoundEvents.ANVIL_LAND, SoundSource.PLAYERS, 0.35f, 1.8f);
		bursting = true;
		for (LivingEntity o : level.getEntitiesOfClass(LivingEntity.class, at.getBoundingBox().inflate(3.5), e -> e instanceof Enemy && e.isAlive())) {
			o.invulnerableTime = 0;
			o.hurt(p.damageSources().playerAttack(p), amount);
		}
		bursting = false;
	}

	private static void onHit(LivingDamageEvent.Post e) {
		if (bursting || !(e.getSource().getEntity() instanceof ServerPlayer p) || stage(p.getMainHandItem()) <= 0 || e.getNewDamage() <= 0) return;
		if (counted(p)) burst(p, e.getEntity(), e.getNewDamage() * BURST);
	}

	private static void onBlock(LivingShieldBlockEvent e) {
		if (!e.getBlocked() || !(e.getEntity() instanceof ServerPlayer p) || !(stage(p.getOffhandItem()) > 0 || stage(p.getMainHandItem()) > 0)) return;
		if (counted(p)) burst(p, p, Math.max(4f, e.getOriginalBlockedDamage() * 2f));
	}
}
