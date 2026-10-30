package com.snoringwalrus.ashbound;

import java.util.List;

import com.mojang.brigadier.arguments.StringArgumentType;

import net.minecraft.ChatFormatting;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.SharedSuggestionProvider;
import net.minecraft.core.Holder;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.item.component.Unbreakable;
import net.minecraft.world.item.enchantment.Enchantment;
import net.minecraft.world.item.enchantment.Enchantments;
import net.neoforged.bus.api.EventPriority;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.RegisterCommandsEvent;

/**
 * Testing helpers (operators only).
 *
 *   /ashbound tank        netherite armour (Protection IV, Unbreaking III) and, until turned off, Resistance III,
 *                         Fire Resistance, Regeneration II and Saturation: a boss's blows still land and hurt a little,
 *                         but you can stand in a fight long enough to see all of it. Armour you wore goes to your bag.
 *   /ashbound tank off    the effects taken away again (the armour stays)
 *   /ashbound set <id>    put on one of the dungeon armour sets (what you wore goes to your bag), to look at it
 *   /ashbound gear <gate> a dungeon's ten forged weapons, six boss weapons and a stack of each of its drops
 */
public final class Cheats {
	private Cheats() {}

	private static final List<Holder<MobEffect>> EFFECTS = List.of(
			MobEffects.DAMAGE_RESISTANCE, MobEffects.FIRE_RESISTANCE, MobEffects.REGENERATION, MobEffects.SATURATION);

	static void register() {
		NeoForge.EVENT_BUS.addListener(EventPriority.LOWEST, (LivingIncomingDamageEvent e) -> {
			if (e.getSource().getEntity() instanceof Player p && e.getSource().getDirectEntity() == p && oneshot(p.getMainHandItem())) {
				e.setCanceled(false);
				e.setAmount(e.getEntity().getMaxHealth() * 1000f + 100000f);
			}
		});
		NeoForge.EVENT_BUS.addListener((RegisterCommandsEvent e) -> e.getDispatcher().register(Commands.literal("ashbound")
				.requires(s -> s.hasPermission(2))
				.then(Commands.literal("oneshot").executes(c -> oneshot(c.getSource())))
				.then(Commands.literal("tank")
						.executes(c -> tank(c.getSource()))
						.then(Commands.literal("off").executes(c -> untank(c.getSource()))))
				.then(Commands.literal("set").then(Commands.argument("id", StringArgumentType.word())
						.suggests((c, b) -> SharedSuggestionProvider.suggest(Gear.DUNGEONS.stream()
								.flatMap(d -> d.sets().stream()).map(Gear.Set::id), b))
						.executes(c -> wear(c.getSource(), StringArgumentType.getString(c, "id")))))
				.then(Commands.literal("gear").then(Commands.argument("gate", StringArgumentType.word())
						.suggests((c, b) -> SharedSuggestionProvider.suggest(Gear.DUNGEONS.stream().map(Gear.Dungeon::gate), b))
						.executes(c -> gear(c.getSource(), StringArgumentType.getString(c, "gate")))))));
	}

	private static void stow(ServerPlayer p, EquipmentSlot slot) {
		ItemStack old = p.getItemBySlot(slot);
		if (!old.isEmpty() && !p.getInventory().add(old.copy())) p.drop(old.copy(), false);
		p.setItemSlot(slot, ItemStack.EMPTY);
	}

	private static void give(ServerPlayer p, ItemStack s) {
		if (!p.getInventory().add(s)) p.drop(s, false);
	}

	private static int tank(CommandSourceStack src) {
		ServerPlayer p = src.getPlayer();
		if (p == null) return 0;
		var enchants = p.level().registryAccess().lookupOrThrow(Registries.ENCHANTMENT);
		Holder<Enchantment> prot = enchants.getOrThrow(Enchantments.PROTECTION), unb = enchants.getOrThrow(Enchantments.UNBREAKING);
		Object[][] suit = {{EquipmentSlot.HEAD, Items.NETHERITE_HELMET}, {EquipmentSlot.CHEST, Items.NETHERITE_CHESTPLATE},
				{EquipmentSlot.LEGS, Items.NETHERITE_LEGGINGS}, {EquipmentSlot.FEET, Items.NETHERITE_BOOTS}};
		for (Object[] s : suit) {
			EquipmentSlot slot = (EquipmentSlot) s[0];
			stow(p, slot);
			ItemStack piece = new ItemStack((Item) s[1]);
			piece.enchant(prot, 4);
			piece.enchant(unb, 3);
			p.setItemSlot(slot, piece);
		}
		p.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, MobEffectInstance.INFINITE_DURATION, 2, false, false, true));
		p.addEffect(new MobEffectInstance(MobEffects.FIRE_RESISTANCE, MobEffectInstance.INFINITE_DURATION, 0, false, false, true));
		p.addEffect(new MobEffectInstance(MobEffects.REGENERATION, MobEffectInstance.INFINITE_DURATION, 1, false, false, true));
		p.addEffect(new MobEffectInstance(MobEffects.SATURATION, MobEffectInstance.INFINITE_DURATION, 0, false, false, true));
		p.setHealth(p.getMaxHealth());
		src.sendSuccess(() -> Component.literal("Tank mode: netherite armour, Resistance III, Fire Resistance, Regeneration II (/ashbound tank off to stop)"), false);
		return 1;
	}

	static final String ONESHOT = "ashbound_oneshot";

	/** a test blade that kills whatever it hits in one blow, bosses too */
	private static int oneshot(CommandSourceStack src) {
		ServerPlayer p = src.getPlayer();
		if (p == null) return 0;
		ItemStack blade = new ItemStack(Items.NETHERITE_SWORD);
		blade.set(DataComponents.CUSTOM_NAME, Component.literal("Bossbane (test)").withStyle(ChatFormatting.GOLD));
		blade.set(DataComponents.ENCHANTMENT_GLINT_OVERRIDE, true);
		blade.set(DataComponents.UNBREAKABLE, new Unbreakable(true));
		CompoundTag tag = new CompoundTag();
		tag.putBoolean(ONESHOT, true);
		blade.set(DataComponents.CUSTOM_DATA, CustomData.of(tag));
		give(p, blade);
		src.sendSuccess(() -> Component.literal("Bossbane: one hit kills anything"), false);
		return 1;
	}

	static boolean oneshot(ItemStack s) {
		CustomData d = s.get(DataComponents.CUSTOM_DATA);
		return d != null && d.copyTag().getBoolean(ONESHOT);
	}

	private static int untank(CommandSourceStack src) {
		ServerPlayer p = src.getPlayer();
		if (p == null) return 0;
		for (Holder<MobEffect> e : EFFECTS) p.removeEffect(e);
		src.sendSuccess(() -> Component.literal("Tank mode off (the armour's yours to keep)"), false);
		return 1;
	}

	private static EquipmentSlot slot(String s) {
		return switch (s) {
			case "helm" -> EquipmentSlot.HEAD;
			case "chest" -> EquipmentSlot.CHEST;
			case "legs" -> EquipmentSlot.LEGS;
			default -> EquipmentSlot.FEET;
		};
	}

	private static int wear(CommandSourceStack src, String id) {
		ServerPlayer p = src.getPlayer();
		if (p == null) return 0;
		for (Gear.Dungeon d : Gear.DUNGEONS)
			for (Gear.Set s : d.sets()) {
				if (!s.id().equals(id)) continue;
				for (Gear.Piece pc : s.pieces()) {
					Item it = Gear.item(pc.id());
					if (it == null) continue;
					EquipmentSlot slot = slot(pc.slot());
					stow(p, slot);
					p.setItemSlot(slot, new ItemStack(it));
				}
				src.sendSuccess(() -> Component.literal("Wearing " + s.id() + " (" + s.cls() + ") from " + d.title()), false);
				return 1;
			}
		src.sendFailure(Component.literal("No armour set called " + id));
		return 0;
	}

	private static int gear(CommandSourceStack src, String gate) {
		ServerPlayer p = src.getPlayer();
		if (p == null) return 0;
		Gear.Dungeon d = Gear.of(gate);
		if (d == null) {
			src.sendFailure(Component.literal("No dungeon called " + gate));
			return 0;
		}
		for (Gear.Weapon w : d.weapons()) {
			Item it = Gear.item(w.id());
			if (it != null) give(p, new ItemStack(it));
		}
		for (String m : d.mats()) {
			Item it = Gear.item(m);
			if (it != null) give(p, new ItemStack(it, it.getDefaultMaxStackSize()));
		}
		src.sendSuccess(() -> Component.literal(d.title() + ": " + d.weapons().size() + " weapons and its three drops"), false);
		return 1;
	}
}
