package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;

import net.minecraft.ChatFormatting;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.alchemy.PotionContents;
import net.minecraft.world.item.alchemy.Potions;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * The class every player picks when they first join, one per party role. It's a start, not a cage: a kit of rank F
 * gear and one small lasting bonus, and any class can use any weapon after that. The server holds all of it: it asks
 * until it has an answer, a pick only counts once, and the kit is given once per player (flags survive death), so
 * nobody farms kits by relogging or by a client sending the packet again. An op can give someone a new choice with
 * /ashbound class reset PLAYER, or a new choice and a new kit with /ashbound class reset PLAYER kit.
 */
public final class Classes {
	private Classes() {}

	/** Gear ids are ashbound's unless they say otherwise; "id*n" in a pack is that many. The bonus is a stat of {@link Passives}. */
	public record Cls(String id, String name, String role, String blurb, String main, String off, String chest, String legs, String boots,
			List<String> pack, String perk, String perkKey, double perkValue) {}

	private static final String APPLES = "minecraft:golden_apple*3", FEW_APPLES = "minecraft:golden_apple*2";
	/** What everyone sets out with: tools, a bed, and food and light for the road. */
	private static final List<String> ROAD_PACK = List.of("minecraft:iron_pickaxe", "minecraft:iron_axe", "minecraft:iron_shovel",
			"minecraft:cooked_beef*32", "minecraft:torch*32", "minecraft:red_bed");
	private static final int HEALING_POTIONS = 3;

	public static final List<Cls> ALL = List.of(
			new Cls("vanguard", "Vanguard", "Tank", "Sword and shield at the front, so the monsters look at you and not your party.",
					"bilge_falchion", "cask_lid_shield", "bilgewader_coat", "bilgewader_waders", "bilgewader_boots", List.of(APPLES), "+2 armour", "armour", 2),
			new Cls("breaker", "Breaker", "Hammer", "Slow, heavy blows that knock monsters off their feet.",
					"coopers_mallet", "", "cooper_hauberk", "cooper_tassets", "cooper_boots", List.of(APPLES), "+0.5 impact, staggers harder", "impact", 0.5),
			new Cls("reaver", "Reaver", "Two-hander", "Wide swings of a huge blade. Clears a crowd, drinks stamina.",
					"stave_cleaver", "", "cooper_hauberk", "cooper_tassets", "cooper_boots", List.of(APPLES), "+4% damage", "dmg%", 4),
			new Cls("lancer", "Lancer", "Spear", "Long reach, and a thrust that goes through the first monster into the next.",
					"bilge_boathook", "", "cooper_hauberk", "cooper_tassets", "cooper_boots", List.of(APPLES), "+1 enemy hit per swing", "strikes", 1),
			new Cls("shade", "Shade", "Daggers", "A blade in each hand, fast and light. Stay moving or die.",
					"spigot_knife", "spigot_knife", "corkrunner_jerkin", "corkrunner_breeches", "corkrunner_boots", List.of(APPLES), "+4% move speed", "move%", 4),
			new Cls("hunter", "Hunter", "Bow", "Hits from far off, with a knife for whatever gets close.",
					"hoop_bow", "", "corkrunner_jerkin", "corkrunner_breeches", "corkrunner_boots", List.of("minecraft:arrow*320", "spigot_knife", FEW_APPLES), "+8% arrow damage", "arrow%", 8),
			new Cls("ashcaster", "Ashcaster", "Black mage", "Hurls bolts from a staff. Hits hardest, falls fastest.",
					"apprentice_black_staff", "", "vintner_robe", "vintner_wraps", "vintner_slippers", List.of(FEW_APPLES), "+6% spell power", "spell%", 6),
			new Cls("mender", "Mender", "White mage", "Heals you and everyone near you. The party that has one lives longer.",
					"apprentice_white_staff", "", "vintner_robe", "vintner_wraps", "vintner_slippers", List.of(FEW_APPLES), "+8% spell power", "heal%", 8),
			new Cls("caller", "Caller", "Summoner", "Calls thralls to fight for you while you stay out of reach.",
					"apprentice_summon_staff", "", "vintner_robe", "vintner_wraps", "vintner_slippers", List.of(FEW_APPLES), "+15% thrall health", "thrall_hp%", 15));

	public static final int START_COINS = 150;
	private static final String FLAG = "class_", KIT_GIVEN = "class_kit";
	/** Asked again this often (ticks), in case Esc or a loading screen closed the question. */
	private static final int ASK_EVERY = 60;
	/** Nothing hurts you while you're reading the classes, for this long after you join (ticks). */
	private static final int GRACE = 6000;
	private static final Set<UUID> ASKING = new HashSet<>();

	/** Your own class on your own screen; empty until you've picked one. */
	public static String client = "";

	public static Cls byId(String id) {
		for (Cls c : ALL)
			if (c.id().equals(id)) return c;
		return null;
	}

	public static Cls of(Player p) {
		for (Cls c : ALL)
			if (Coins.flag(p, FLAG + c.id())) return c;
		return null;
	}

	/** This class's bonus, if it's yours. {@link Passives#stat} adds it to the tree's. */
	static double stat(Player p, String key) {
		for (Cls c : ALL)
			if (c.perkKey().equals(key) && Coins.flag(p, FLAG + c.id())) return c.perkValue();
		return 0;
	}

	/** Nothing hurts you while a first-join question is open; the mount's comes right after this one. */
	static void asking(ServerPlayer p, boolean on) {
		if (on) ASKING.add(p.getUUID());
		else ASKING.remove(p.getUUID());
	}

	private static ItemStack stack(String id, int n) {
		if (id.isEmpty()) return ItemStack.EMPTY;
		ResourceLocation at = id.contains(":") ? ResourceLocation.parse(id) : ResourceLocation.fromNamespaceAndPath(Ashbound.ID, id);
		return new ItemStack(BuiltInRegistries.ITEM.get(at), n);
	}

	private static void add(List<ItemStack> l, String entry) {
		int star = entry.indexOf('*');
		ItemStack one = stack(star < 0 ? entry : entry.substring(0, star), 1);
		for (int left = star < 0 ? 1 : Integer.parseInt(entry.substring(star + 1)); left > 0; left -= one.getMaxStackSize())
			l.add(one.copyWithCount(Math.min(left, one.getMaxStackSize())));
	}

	/** Everything that goes in the pack, not what's worn, in stacks that fit. */
	private static List<ItemStack> bag(Cls c) {
		List<ItemStack> l = new ArrayList<>();
		c.pack().forEach(e -> add(l, e));
		ROAD_PACK.forEach(e -> add(l, e));
		for (int i = 0; i < HEALING_POTIONS; i++) l.add(PotionContents.createItemStack(Items.POTION, Potions.HEALING));
		return l;
	}

	/** The whole kit, for the chooser to show: one tile for each thing, however many stacks of it. */
	public static List<ItemStack> kit(Cls c) {
		List<ItemStack> all = new ArrayList<>(), out = new ArrayList<>();
		for (ItemStack s : List.of(stack(c.main(), 1), stack(c.off(), 1), stack(c.chest(), 1), stack(c.legs(), 1), stack(c.boots(), 1)))
			if (!s.isEmpty()) all.add(s);
		all.addAll(bag(c));
		for (ItemStack s : all) {
			ItemStack same = out.stream().filter(o -> ItemStack.isSameItemSameComponents(o, s)).findFirst().orElse(null);
			if (same != null) same.grow(s.getCount());
			else out.add(s.copy());
		}
		return out;
	}

	public static ItemStack icon(Cls c) {
		return stack(c.main(), 1);
	}

	private static void stow(ServerPlayer p, ItemStack s) {
		if (!p.getInventory().add(s)) p.drop(s, false);
	}

	/** On you, with whatever was there going to your pack. */
	private static void wear(ServerPlayer p, EquipmentSlot slot, ItemStack s) {
		if (s.isEmpty()) return;
		ItemStack old = p.getItemBySlot(slot);
		p.setItemSlot(slot, s);
		if (!old.isEmpty()) stow(p, old);
	}

	/** A player's answer. Anything but a first, known pick is ignored. */
	public static void pick(ServerPlayer p, String id) {
		Cls c = byId(id);
		if (c == null || of(p) != null || !p.isAlive()) return;
		Coins.setFlag(p, FLAG + c.id());
		ASKING.remove(p.getUUID());
		Skills.keepOwn(p);
		if (!Coins.flag(p, KIT_GIVEN)) {
			Coins.setFlag(p, KIT_GIVEN);
			wear(p, EquipmentSlot.MAINHAND, stack(c.main(), 1));
			wear(p, EquipmentSlot.OFFHAND, stack(c.off(), 1));
			wear(p, EquipmentSlot.CHEST, stack(c.chest(), 1));
			wear(p, EquipmentSlot.LEGS, stack(c.legs(), 1));
			wear(p, EquipmentSlot.FEET, stack(c.boots(), 1));
			bag(c).forEach(s -> stow(p, s));
			Coins.give(p, START_COINS);
		}
		PacketDistributor.sendToPlayer(p, new Net.ClassState(c.id()));
		p.sendSystemMessage(Component.literal("Class chosen: " + c.name() + ". " + c.perk() + ".").withStyle(ChatFormatting.GOLD));
		if (Mounts.of(p) == null) Mounts.ask(p);
	}

	private static int reset(CommandSourceStack src, ServerPlayer p, boolean kit) {
		List<String> l = new ArrayList<>(p.getData(Coins.FLAGS));
		l.removeIf(f -> f.startsWith(FLAG) && (kit || !f.equals(KIT_GIVEN)));
		p.setData(Coins.FLAGS, l);
		src.sendSuccess(() -> Component.literal(p.getName().getString() + " can choose a class again" + (kit ? " and gets a new kit" : " (no second kit)")), true);
		return 1;
	}

	static void init() {
		NeoForge.EVENT_BUS.addListener((PlayerEvent.PlayerLoggedInEvent e) -> {
			if (e.getEntity() instanceof ServerPlayer p) {
				Cls c = of(p);
				if (c != null) PacketDistributor.sendToPlayer(p, new Net.ClassState(c.id()));
			}
		});
		NeoForge.EVENT_BUS.addListener((PlayerEvent.PlayerLoggedOutEvent e) -> ASKING.remove(e.getEntity().getUUID()));
		// not at login: the "loading terrain" screen closes whatever opened under it
		NeoForge.EVENT_BUS.addListener((PlayerTickEvent.Post e) -> {
			if (e.getEntity() instanceof ServerPlayer p && p.tickCount % ASK_EVERY == 0 && p.isAlive() && of(p) == null) {
				ASKING.add(p.getUUID());
				PacketDistributor.sendToPlayer(p, new Net.ClassState(""));
			}
		});
		NeoForge.EVENT_BUS.addListener((LivingIncomingDamageEvent e) -> {
			if (e.getEntity() instanceof ServerPlayer p && p.tickCount < GRACE && ASKING.contains(p.getUUID())) e.setCanceled(true);
		});
		NeoForge.EVENT_BUS.addListener((RegisterCommandsEvent e) -> e.getDispatcher().register(Commands.literal("ashbound")
				.requires(s -> s.hasPermission(2))
				.then(Commands.literal("class").then(Commands.literal("reset").then(Commands.argument("player", EntityArgument.player())
						.executes(c -> reset(c.getSource(), EntityArgument.getPlayer(c, "player"), false))
						.then(Commands.literal("kit").executes(c -> reset(c.getSource(), EntityArgument.getPlayer(c, "player"), true))))))));
	}
}
