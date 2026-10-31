package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

import net.minecraft.ChatFormatting;
import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.network.PacketDistributor;
import net.neoforged.neoforge.registries.DeferredItem;

/**
 * What bosses leave you to read. A skill book teaches its skill at its rank, the rarer the higher, so a lucky one early
 * makes you strong for a long way; one of the rank you already have raises it by one. A book of a skill your path hasn't
 * reached yet teaches it early. Any other of your class's skills means giving one of yours up for it, for good: the
 * reader chooses on their screen (client/ReplaceScreen) and {@link #swap} is the bargain. An Awakening Tome is {@link Forms}.
 */
public final class Books {
	private Books() {}

	private static final String[] TITLES = {"Worn", "Bound", "Gilded", "Ancient", "Mythic"};
	private static final Rarity[] RARITY = {Rarity.COMMON, Rarity.UNCOMMON, Rarity.RARE, Rarity.EPIC, Rarity.EPIC};
	private static final float BOOK_CHANCE = 0.35f, TOME_CHANCE = 0.04f, TOME_PER_RANK = 0.01f, LUCKY = 0.03f;
	private static final String RANKS = "FEDCBAS";

	public static final List<DeferredItem<Item>> BOOKS = new ArrayList<>(), TOMES = new ArrayList<>();
	/** Opens the warning on the reader's screen. */
	public static Consumer<Forms.Form> onTome = f -> {};
	public static Consumer<Net.BookOffer> onOffer = m -> {};

	static void register() {
		for (int i = 0; i < TITLES.length; i++) {
			int rank = i + 1;
			BOOKS.add(Weapons.ITEMS.registerItem("skill_book_" + rank, p -> new Book(rank, p.stacksTo(1).rarity(RARITY[rank - 1]))));
		}
		for (Forms.Form f : Forms.ALL) TOMES.add(Weapons.ITEMS.registerItem("tome_" + f.id(), p -> new Tome(f, p.stacksTo(1).rarity(Rarity.EPIC).fireResistant())));
	}

	public static ItemStack book(int rank, String skill) {
		ItemStack s = new ItemStack(BOOKS.get(rank - 1).get());
		CompoundTag t = new CompoundTag();
		t.putString("skill", skill);
		s.set(DataComponents.CUSTOM_DATA, CustomData.of(t));
		return s;
	}

	private static String skillOf(ItemStack s) {
		return s.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag().getString("skill");
	}

	/** A book's rank from the dungeon it came from: mostly near its own, and now and then a great deal better. */
	static int rollRank(char dungeon, RandomSource r) {
		int top = 1 + Math.max(0, RANKS.indexOf(dungeon)) * 4 / 6;
		int rank = 1 + r.nextInt(top);
		return r.nextFloat() < LUCKY ? Math.min(Skills.MAX_RANK, rank + 2) : rank;
	}

	/** What a boss leaves this player beyond its gear. */
	static List<ItemStack> drops(ServerPlayer p, char dungeon, RandomSource r) {
		List<ItemStack> out = new ArrayList<>();
		Classes.Cls c = Classes.of(p);
		if (r.nextFloat() < BOOK_CHANCE) {
			List<Skills.Skill> from = c != null ? Skills.ofClass(c.id()) : Skills.ALL;
			out.add(book(rollRank(dungeon, r), from.get(r.nextInt(from.size())).id()));
		}
		if (c != null && r.nextFloat() < TOME_CHANCE + TOME_PER_RANK * Math.max(0, RANKS.indexOf(dungeon)))
			for (int i = 0; i < Forms.ALL.size(); i++) if (Forms.ALL.get(i).cls().equals(c.id())) out.add(new ItemStack(TOMES.get(i).get()));
		return out;
	}

	public static class Book extends Item {
		final int rank;

		Book(int rank, Properties p) {
			super(p);
			this.rank = rank;
		}

		@Override
		public Component getName(ItemStack s) {
			Skills.Skill k = Skills.byId(skillOf(s));
			return Component.literal(TITLES[rank - 1] + " Book" + (k == null ? "" : " of " + k.name()));
		}

		@Override
		public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
			ItemStack s = player.getItemInHand(hand);
			if (level.isClientSide) return InteractionResultHolder.sidedSuccess(s, true);
			ServerPlayer p = (ServerPlayer) player;
			Skills.Skill k = Skills.byId(skillOf(s));
			Classes.Cls mine = Classes.of(p);
			if (k == null || mine == null || !Skills.spec(k.spec()).cls().equals(mine.id())) {
				p.displayClientMessage(Component.literal(k == null ? "The pages are blank" : mine == null ? "Choose your class first" : "Only a " + Classes.byId(Skills.spec(k.spec()).cls()).name() + " can read this").withStyle(ChatFormatting.RED), true);
				return InteractionResultHolder.fail(s);
			}
			int have = Skills.rank(p, k.id()), to = rank > have ? rank : Math.min(have + 1, Skills.MAX_RANK);
			if (have == 0 && (Skills.lost(p, k.id()) || (Skills.picks(p) >> Skills.tier(k) & 1) != 0)) {   // you've chosen on its level already
				PacketDistributor.sendToPlayer(p, new Net.BookOffer(k.id(), rank));
				return InteractionResultHolder.success(s);
			}
			if (rank < have || to == have) {
				p.displayClientMessage(Component.literal("You've gone past what this can teach").withStyle(ChatFormatting.GRAY), true);
				return InteractionResultHolder.fail(s);
			}
			Skills.teach(p, k.id(), to);
			Spells.skillFx(p.serverLevel(), "book_" + rank, p.position(), Vec3.ZERO, to, p);
			p.displayClientMessage(Component.literal(k.name() + "  Rank " + to).withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD), true);
			s.shrink(1);
			return InteractionResultHolder.consume(s);
		}

		@Override
		public void appendHoverText(ItemStack s, TooltipContext ctx, List<Component> lines, TooltipFlag flag) {
			Skills.Skill k = Skills.byId(skillOf(s));
			if (k == null) return;
			lines.add(Component.literal("Teaches " + k.name() + " at rank " + rank).withStyle(ChatFormatting.GOLD));
			lines.add(Component.literal(k.blurb()).withStyle(ChatFormatting.GRAY));
			lines.add(Component.literal(Classes.byId(Skills.spec(k.spec()).cls()).name() + ", " + Skills.spec(k.spec()).name() + " path").withStyle(ChatFormatting.DARK_GRAY));
			lines.add(Component.literal("If you've chosen another at level " + Skills.unlock(k) + ", one of your skills goes for good").withStyle(ChatFormatting.RED));
		}
	}

	public static class Tome extends Item {
		final Forms.Form form;

		Tome(Forms.Form form, Properties p) {
			super(p);
			this.form = form;
		}

		@Override
		public Component getName(ItemStack s) {
			return Component.literal(form.tome());
		}

		/** The warning comes first, on the reader's screen; {@link #confirm} is the bargain. */
		@Override
		public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
			if (level.isClientSide) onTome.accept(form);
			return InteractionResultHolder.sidedSuccess(player.getItemInHand(hand), level.isClientSide);
		}

		@Override
		public void appendHoverText(ItemStack s, TooltipContext ctx, List<Component> lines, TooltipFlag flag) {
			lines.add(Component.literal("Awakening Tome: " + Classes.byId(form.cls()).name()).withStyle(ChatFormatting.DARK_RED));
			lines.add(Component.literal("When: " + form.trigger()).withStyle(ChatFormatting.GRAY));
			lines.add(Component.literal(form.gift()).withStyle(ChatFormatting.GOLD));
			lines.add(Component.literal(form.price()).withStyle(ChatFormatting.RED));
			lines.add(Component.literal("Reading it costs your last skill key for good").withStyle(ChatFormatting.RED));
		}
	}

	/** The reader chose what to give up. The book has to still be in their hand. */
	public static void swap(ServerPlayer p, String give) {
		for (InteractionHand hand : InteractionHand.values()) {
			ItemStack s = p.getItemInHand(hand);
			if (!(s.getItem() instanceof Book b)) continue;
			Skills.Skill k = Skills.byId(skillOf(s));
			Classes.Cls mine = Classes.of(p);
			if (k == null || mine == null || !Skills.spec(k.spec()).cls().equals(mine.id()) || Skills.rank(p, give) == 0 || Skills.rank(p, k.id()) > 0) return;
			Skills.replace(p, give, k.id(), b.rank);
			Spells.skillFx(p.serverLevel(), "book_" + b.rank, p.position(), Vec3.ZERO, b.rank, p);
			p.displayClientMessage(Component.literal(Skills.byId(give).name() + " is gone.  " + k.name() + "  Rank " + b.rank).withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD), true);
			s.shrink(1);
			return;
		}
	}

	/** The reader said yes. It has to still be in their hand. */
	public static void confirm(ServerPlayer p, String id) {
		Forms.Form f = Forms.byId(id);
		if (f == null) return;
		for (InteractionHand hand : InteractionHand.values()) {
			ItemStack s = p.getItemInHand(hand);
			if (s.getItem() instanceof Tome t && t.form == f) {
				if (Forms.read(p, f)) s.shrink(1);
				return;
			}
		}
	}
}
