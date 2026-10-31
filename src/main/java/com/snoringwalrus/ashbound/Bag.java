package com.snoringwalrus.ashbound;

import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.function.Supplier;

import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.Container;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.MenuType;
import net.minecraft.world.inventory.Slot;
import net.minecraft.ChatFormatting;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.SlotAccess;
import net.minecraft.world.inventory.ClickAction;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.saveddata.SavedData;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.common.extensions.IMenuTypeExtension;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.neoforged.neoforge.network.PacketDistributor;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * The Bottomless Bag: no end to what it holds, kept with the world, opened from the inventory or with its key.
 *
 * Everyone has their own, and a party sees all of theirs as one: what you put in stays yours underneath, so anyone can
 * take it while you're together and it goes with you if you leave, and nothing has to be split when a party breaks up.
 * Taking draws on your own first. Things are held by kind with a count, so it costs the same at ten or ten billion.
 */
public final class Bag {
	private Bag() {}

	public static final int OPEN = 0, LEFT = 1, RIGHT = 2, QUICK = 3, PUT_PACK = 4, PUT_LIKE = 5;
	/** the backpack part of the inventory; the hotbar stays in your hands */
	private static final int PACK_FROM = 9, PACK_TO = 35;
	/** Where the inventory sits in the screen, which has its corner at the top left of the pack: see client/BagScreen. */
	public static final int SLOTS_X = 11, HOTBAR_Y = 58;

	private static final DeferredRegister<MenuType<?>> MENUS = DeferredRegister.create(Registries.MENU, Ashbound.ID);
	public static final Supplier<MenuType<Menu>> MENU = MENUS.register("bag", () -> IMenuTypeExtension.create((id, inv, buf) -> new Menu(id, inv)));

	/** Stacks count as the same kind if they'd stack. */
	private record Kind(ItemStack stack) {
		@Override
		public boolean equals(Object o) {
			return o instanceof Kind k && ItemStack.isSameItemSameComponents(stack, k.stack);
		}

		@Override
		public int hashCode() {
			return ItemStack.hashItemAndComponents(stack);
		}
	}

	private static Kind kind(ItemStack s) {
		return new Kind(s.copyWithCount(1));
	}

	private static final class State extends SavedData {
		final Map<UUID, Map<Kind, Long>> bags = new HashMap<>();
		/** Whose bags changed since anyone looking was told. */
		final Set<UUID> changed = new HashSet<>();

		void touch(UUID owner) {
			changed.add(owner);
			setDirty();
		}

		@Override
		public CompoundTag save(CompoundTag tag, HolderLookup.Provider reg) {
			ListTag all = new ListTag();
			bags.forEach((owner, bag) -> {
				ListTag items = new ListTag();
				bag.forEach((k, n) -> {
					CompoundTag t = new CompoundTag();
					t.put("item", k.stack().save(reg));
					t.putLong("n", n);
					items.add(t);
				});
				CompoundTag t = new CompoundTag();
				t.putUUID("owner", owner);
				t.put("items", items);
				all.add(t);
			});
			tag.put("bags", all);
			return tag;
		}

		static State load(CompoundTag tag, HolderLookup.Provider reg) {
			State s = new State();
			for (Tag e : tag.getList("bags", Tag.TAG_COMPOUND)) {
				CompoundTag t = (CompoundTag) e;
				Map<Kind, Long> bag = new LinkedHashMap<>();
				for (Tag i : t.getList("items", Tag.TAG_COMPOUND)) {
					CompoundTag it = (CompoundTag) i;
					ItemStack.parse(reg, it.get("item")).ifPresent(st -> bag.put(new Kind(st), it.getLong("n")));
				}
				s.bags.put(t.getUUID("owner"), bag);
			}
			return s;
		}
	}

	private static State state(MinecraftServer server) {
		return server.overworld().getDataStorage().computeIfAbsent(new SavedData.Factory<>(State::new, State::load, null), "ashbound_bag");
	}

	// ---------------------------------------------------------------- what's in it

	/** The whole stack, into p's own. */
	static void store(ServerPlayer p, ItemStack s) {
		if (s.isEmpty()) return;
		State st = state(p.server);
		st.bags.computeIfAbsent(p.getUUID(), k -> new LinkedHashMap<>()).merge(kind(s), (long) s.getCount(), Long::sum);
		st.touch(p.getUUID());
	}

	/** Up to n of this kind, no more than a stack, from p's own first and then the party's. */
	static ItemStack take(ServerPlayer p, ItemStack like, int n) {
		State st = state(p.server);
		Kind k = kind(like);
		n = Math.min(n, like.getMaxStackSize());
		int got = 0;
		for (UUID u : Party.circle(p).keySet()) {
			Map<Kind, Long> bag = st.bags.get(u);
			Long has = bag == null ? null : bag.get(k);
			if (has == null) continue;
			int out = (int) Math.min(has, n - got);
			if (out == has) bag.remove(k);
			else bag.put(k, has - out);
			st.touch(u);
			got += out;
			if (got == n) break;
		}
		return k.stack().copyWithCount(got);
	}

	/** How many of this kind p can reach. */
	static long count(ServerPlayer p, ItemStack like) {
		State st = state(p.server);
		Kind k = kind(like);
		long n = 0;
		for (UUID u : Party.circle(p).keySet()) n += st.bags.getOrDefault(u, Map.of()).getOrDefault(k, 0L);
		return n;
	}

	/** What p sees: each kind once with its total, and whose it is when that's more than p. */
	private static Net.BagLines lines(ServerPlayer p) {
		State st = state(p.server);
		Map<UUID, String> circle = Party.circle(p);
		Map<Kind, Long> total = new LinkedHashMap<>();
		Map<Kind, Set<String>> whose = new HashMap<>();
		circle.forEach((u, name) -> st.bags.getOrDefault(u, Map.of()).forEach((k, n) -> {
			total.merge(k, n, Long::sum);
			whose.computeIfAbsent(k, x -> new LinkedHashSet<>()).add(name);
		}));
		List<Net.BagLine> out = total.entrySet().stream()
				.map(e -> new Net.BagLine(e.getKey().stack(), e.getValue(), circle.size() > 1 ? String.join(", ", whose.get(e.getKey())) : "")).toList();
		return new Net.BagLines(out, circle.size());
	}

	// ---------------------------------------------------------------- the screen

	/** Your inventory and nothing else: the bag's own grid isn't slots, since what's in it can't be counted in stacks. */
	public static final class Menu extends AbstractContainerMenu {
		public Menu(int id, Inventory inv) {
			super(MENU.get(), id);
			for (int r = 0; r < 3; r++)
				for (int c = 0; c < 9; c++) addSlot(new Slot(inv, PACK_FROM + r * 9 + c, SLOTS_X + c * 18, r * 18));
			for (int c = 0; c < 9; c++) addSlot(new Slot(inv, c, SLOTS_X + c * 18, HOTBAR_Y));
		}

		@Override
		public boolean stillValid(Player p) {
			return p.isAlive();
		}

		/** Shift-click in your pack: into the bag. */
		@Override
		public ItemStack quickMoveStack(Player p, int i) {
			Slot s = slots.get(i);
			if (s.hasItem()) {
				if (p instanceof ServerPlayer sp) {
					store(sp, s.getItem());
					sound(sp, true);
				}
				s.set(ItemStack.EMPTY);
			}
			return ItemStack.EMPTY;
		}
	}

	public static void act(ServerPlayer p, Net.BagAct m) {
		if (m.what() == OPEN) {
			if (!p.isSpectator()) {
				p.openMenu(new SimpleMenuProvider((id, inv, pl) -> new Menu(id, inv), Component.literal("Bottomless Bag")));
				PacketDistributor.sendToPlayer(p, lines(p));
			}
			return;
		}
		if (!(p.containerMenu instanceof Menu menu)) return;
		ItemStack held = menu.getCarried();
		ItemStack like = m.item();
		switch (m.what()) {
			case LEFT, RIGHT -> {
				if (!held.isEmpty()) {
					store(p, m.what() == LEFT ? held : held.copyWithCount(1));
					if (m.what() == LEFT) menu.setCarried(ItemStack.EMPTY);
					else held.shrink(1);
					sound(p, true);
				} else if (!like.isEmpty()) {
					menu.setCarried(take(p, like, m.what() == LEFT ? like.getMaxStackSize() : (like.getMaxStackSize() + 1) / 2));
					sound(p, false);
				}
			}
			case QUICK -> {
				if (like.isEmpty() || !held.isEmpty()) return;
				ItemStack got = take(p, like, like.getMaxStackSize());
				p.getInventory().add(got);
				store(p, got);
				sound(p, false);
			}
			case PUT_PACK, PUT_LIKE -> {
				if (stash(p, m.what() == PUT_LIKE)) sound(p, true);
			}
			default -> {}
		}
		menu.broadcastChanges();
	}

	/** Your pack goes in, the hotbar and the Bag's own pouch stay, or only what's already in it. */
	private static boolean stash(ServerPlayer p, boolean likeOnly) {
		Inventory inv = p.getInventory();
		boolean any = false;
		for (int i = PACK_FROM; i <= PACK_TO; i++) {
			ItemStack s = inv.getItem(i);
			if (s.isEmpty() || s.getItem() instanceof Pouch || likeOnly && count(p, s) == 0) continue;
			store(p, s);
			inv.setItem(i, ItemStack.EMPTY);
			any = true;
		}
		return any;
	}

	/**
	 * The Bag in your hand, for when you've your hands full of loot: right-click opens it, sneak and right-click sends your whole pack
	 * in, and in any inventory, right-click it with an item or right-click an item with it. The key and the tab open the same Bag.
	 */
	public static final class Pouch extends Item {
		Pouch(Properties p) {
			super(p);
		}

		@Override
		public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
			if (player instanceof ServerPlayer p) {
				if (!p.isShiftKeyDown()) act(p, new Net.BagAct(OPEN, ItemStack.EMPTY));
				else {
					boolean any = stash(p, false);
					if (any) sound(p, true);
					p.displayClientMessage(Component.literal(any ? "Your pack is in the Bag" : "Nothing in your pack to put away"), true);
				}
			}
			return InteractionResultHolder.sidedSuccess(player.getItemInHand(hand), level.isClientSide);
		}

		private static void keep(Player player, ItemStack s) {
			if (player instanceof ServerPlayer p) {
				store(p, s.copy());
				sound(p, true);
			}
		}

		@Override
		public boolean overrideStackedOnOther(ItemStack bag, Slot slot, ClickAction click, Player player) {
			if (click != ClickAction.SECONDARY || !slot.hasItem() || slot.getItem().getItem() instanceof Pouch || !slot.mayPickup(player)) return false;
			keep(player, slot.getItem());
			slot.set(ItemStack.EMPTY);
			return true;
		}

		@Override
		public boolean overrideOtherStackedOnMe(ItemStack bag, ItemStack held, Slot slot, ClickAction click, Player player, SlotAccess carried) {
			if (click != ClickAction.SECONDARY || held.isEmpty() || !slot.allowModification(player)) return false;
			keep(player, held);
			carried.set(ItemStack.EMPTY);
			return true;
		}

		@Override
		public void appendHoverText(ItemStack s, TooltipContext ctx, List<Component> lines, TooltipFlag flag) {
			lines.add(Component.literal("Holds anything, your party shares it").withStyle(ChatFormatting.GRAY));
			lines.add(Component.literal("Right-click: open").withStyle(ChatFormatting.DARK_GRAY));
			lines.add(Component.literal("Sneak + right-click: put your pack in").withStyle(ChatFormatting.DARK_GRAY));
			lines.add(Component.literal("Right-click it with an item: put it in").withStyle(ChatFormatting.DARK_GRAY));
		}
	}

	public static final DeferredItem<Item> POUCH = Weapons.ITEMS.registerItem("bottomless_bag", Pouch::new, new Item.Properties().stacksTo(1));

	private static void sound(ServerPlayer p, boolean in) {
		p.playNotifySound(in ? SoundEvents.BUNDLE_INSERT : SoundEvents.BUNDLE_REMOVE_ONE, SoundSource.PLAYERS, 0.7f, 0.9f + p.getRandom().nextFloat() * 0.2f);
	}

	/** Whoever has it open sees what changed, at most once a tick however much moved. */
	private static void tell(MinecraftServer server) {
		State st = state(server);
		if (st.changed.isEmpty()) return;
		for (ServerPlayer p : server.getPlayerList().getPlayers())
			if (p.containerMenu instanceof Menu && Party.circle(p).keySet().stream().anyMatch(st.changed::contains)) PacketDistributor.sendToPlayer(p, lines(p));
		st.changed.clear();
	}

	static void register(IEventBus bus) {
		MENUS.register(bus);
		NeoForge.EVENT_BUS.addListener((ServerTickEvent.Post e) -> tell(e.getServer()));
	}
}
