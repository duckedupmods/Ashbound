package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.List;

import net.minecraft.ChatFormatting;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.SlotAccess;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.inventory.ClickAction;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.BundleItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.BundleContents;
import net.minecraft.world.level.Level;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.neoforged.neoforge.registries.DeferredItem;

/**
 * The Ration Pouch: a bundle that only takes plain food, carried anywhere in your pack or your belt pouch, and you eat from it by yourself once you've
 * got hungry, so hunger is keeping it stocked and never stops a fight. Food that does something else (a golden apple, a raw one, a
 * stew and its bowl) stays out: that's a choice to make with your own hand.
 */
public final class Rations {
	private Rations() {}

	/** Hunger at or under which you eat, of 20, and how many ticks apart it looks. */
	private static final int EAT_AT = 10, EVERY = 40;

	public static final class Pouch extends BundleItem {
		Pouch(Properties p) {
			super(p);
		}

		@Override
		public boolean overrideStackedOnOther(ItemStack pouch, Slot slot, ClickAction action, Player player) {
			if (action == ClickAction.SECONDARY && slot.hasItem() && !plain(slot.getItem())) return false;
			return super.overrideStackedOnOther(pouch, slot, action, player);
		}

		@Override
		public boolean overrideOtherStackedOnMe(ItemStack pouch, ItemStack other, Slot slot, ClickAction action, Player player, SlotAccess access) {
			if (action == ClickAction.SECONDARY && !other.isEmpty() && !plain(other)) return false;
			return super.overrideOtherStackedOnMe(pouch, other, slot, action, player, access);
		}

		/** A bundle tips out when used; this stays shut. */
		@Override
		public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
			return InteractionResultHolder.pass(player.getItemInHand(hand));
		}

		@Override
		public void appendHoverText(ItemStack stack, TooltipContext ctx, List<Component> lines, TooltipFlag flag) {
			super.appendHoverText(stack, ctx, lines, flag);
			lines.add(Component.literal("You eat from it by yourself when you get hungry").withStyle(ChatFormatting.GRAY));
			lines.add(Component.literal("Right-click food onto it to fill it").withStyle(ChatFormatting.DARK_GRAY));
		}
	}

	public static final DeferredItem<Item> POUCH = Weapons.ITEMS.registerItem("ration_pouch", Pouch::new,
			new Item.Properties().stacksTo(1).component(DataComponents.BUNDLE_CONTENTS, BundleContents.EMPTY));

	static void register() {
		NeoForge.EVENT_BUS.addListener((ServerTickEvent.Post e) -> {
			if (e.getServer().getTickCount() % EVERY != 0) return;
			for (ServerPlayer p : e.getServer().getPlayerList().getPlayers()) feed(p);
		});
	}

	/** A pouch with this in it already. */
	static ItemStack stocked(ItemStack food) {
		ItemStack pouch = new ItemStack(POUCH.get());
		pouch.set(DataComponents.BUNDLE_CONTENTS, new BundleContents(List.of(food)));
		return pouch;
	}

	/** Food and nothing but: no effects, nothing left in your hand after. */
	static boolean plain(ItemStack s) {
		FoodProperties f = s.get(DataComponents.FOOD);
		return f != null && f.effects().isEmpty() && f.usingConvertsTo().isEmpty();
	}

	static void feed(ServerPlayer p) {
		if (p.getFoodData().getFoodLevel() > EAT_AT || !p.isAlive() || p.isSpectator() || p.isCreative()) return;
		for (ItemStack pouch : BeltPouch.held(p)) if (pouch.is(POUCH.get()) && eatFrom(p, pouch)) return;
		for (int i = 0; i < p.getInventory().getContainerSize(); i++) {
			ItemStack pouch = p.getInventory().getItem(i);
			if (pouch.is(POUCH.get()) && eatFrom(p, pouch)) return;
		}
	}

	private static boolean eatFrom(ServerPlayer p, ItemStack pouch) {
		BundleContents in = pouch.get(DataComponents.BUNDLE_CONTENTS);
		if (in == null || in.isEmpty()) return false;
		List<ItemStack> left = new ArrayList<>();
		in.itemCopyStream().forEach(left::add);
		ItemStack next = left.get(0);
		p.getFoodData().eat(next.get(DataComponents.FOOD));
		p.level().playSound(null, p.blockPosition(), SoundEvents.GENERIC_EAT, SoundSource.PLAYERS, 0.5f, 1.1f);
		p.displayClientMessage(Component.literal("You eat from your pouch: ").withStyle(ChatFormatting.GRAY).append(next.getHoverName()), true);
		next.shrink(1);
		if (next.isEmpty()) left.remove(0);
		pouch.set(DataComponents.BUNDLE_CONTENTS, new BundleContents(left));
		return true;
	}
}
