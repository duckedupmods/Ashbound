package com.snoringwalrus.ashbound;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import net.minecraft.ChatFormatting;
import net.minecraft.core.Holder;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EquipmentSlotGroup;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.item.component.ItemAttributeModifiers;
import net.minecraft.world.level.storage.loot.LootPool;
import net.minecraft.world.level.storage.loot.entries.LootItem;
import net.minecraft.world.level.storage.loot.predicates.LootItemRandomChanceCondition;
import net.minecraft.world.level.storage.loot.providers.number.ConstantValue;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.LootTableLoadEvent;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;
import net.neoforged.neoforge.event.entity.player.ItemTooltipEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;
import net.neoforged.neoforge.registries.DeferredItem;

/**
 * The world's weapons (/ashbound/world_arms.json, tools/worldarms.py): never forged, only found, Uncommon to
 * Legendary. Each is its own design; what a copy rolls is its own too: the first time it lands in someone's
 * inventory it is identified and gets one to four affixes (more and stronger the rarer it is) on top of its base.
 * They turn up in the chests of every structure in the modpack, now and then off any monster, more often off dungeon elites, tower
 * foremen and bosses, and in the tower bosses' hoards.
 */
public final class WorldArms {
	private WorldArms() {}

	public enum Tier {
		UNCOMMON("Uncommon", ChatFormatting.GREEN, 1, 1.0, 12), RARE("Rare", ChatFormatting.BLUE, 2, 1.2, 6),
		EPIC("Epic", ChatFormatting.LIGHT_PURPLE, 3, 1.4, 2), LEGENDARY("Legendary", ChatFormatting.GOLD, 4, 1.6, 1);

		public final String title;
		final ChatFormatting colour;
		final int affixes, weight;
		final double power;

		Tier(String title, ChatFormatting colour, int affixes, double power, int weight) {
			this.title = title;
			this.colour = colour;
			this.affixes = affixes;
			this.power = power;
			this.weight = weight;
		}
	}

	public record Arm(String id, String name, String kind, Tier tier, String about, String home, Gear.Weapon weapon) {}

	public static final List<Arm> ARMS = load();

	/** a found armour set (/ashbound/world_armour.json, tools/worldarmour.py); Armors registers its pieces */
	public record Garb(String id, String cls, char rank, Tier tier, String about, List<String> parts) {}

	public record Found(DeferredItem<Item> item, Garb garb) {}

	public static final List<Garb> GARB = loadGarb();
	/** each found piece by its id, filled in as Armors registers them */
	static final Map<String, Found> GARB_ITEMS = new java.util.LinkedHashMap<>();

	private static List<Garb> loadGarb() {
		List<Garb> out = new ArrayList<>();
		try (InputStream in = WorldArms.class.getResourceAsStream("/ashbound/world_armour.json")) {
			if (in == null) return out;
			for (JsonElement el : JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonArray()) {
				JsonObject o = el.getAsJsonObject();
				String id = o.get("id").getAsString();
				List<String> parts = new ArrayList<>();
				for (JsonElement pc : o.getAsJsonArray("pieces")) parts.add(pc.getAsJsonObject().get("id").getAsString().substring(id.length() + 1));
				out.add(new Garb(id, o.get("cls").getAsString(), o.get("rank").getAsString().charAt(0),
						Tier.valueOf(o.get("rarity").getAsString().toUpperCase()), o.get("about").getAsString(), parts));
			}
		} catch (Exception e) {
			Ashbound.LOG.error("world armour not loaded", e);
		}
		return out;
	}
	static final Map<String, Arm> BY_ID = new HashMap<>();
	static final Map<Item, Arm> BY_ITEM = new HashMap<>();
	static final List<DeferredItem<Item>> ITEMS = new ArrayList<>();
	static final String ROLL = "ashbound_roll";

	private static List<Arm> load() {
		List<Arm> out = new ArrayList<>();
		try (InputStream in = WorldArms.class.getResourceAsStream("/ashbound/world_arms.json")) {
			if (in == null) return out;
			for (JsonElement el : JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonArray()) {
				JsonObject o = el.getAsJsonObject();
				Tier t = Tier.valueOf(o.get("rarity").getAsString().toUpperCase());
				Gear.Weapon w = new Gear.Weapon(o.get("id").getAsString(), o.get("name").getAsString(), o.get("kind").getAsString(),
						o.get("rank").getAsString().charAt(0), t.ordinal() >= Tier.EPIC.ordinal(), new Gear.Cost(0, 0, 0),
						o.has("damage") ? o.get("damage").getAsDouble() : 0, o.has("speed") ? o.get("speed").getAsDouble() : 0);
				out.add(new Arm(w.id(), w.name(), w.kind(), t, o.get("about").getAsString(), o.get("home").getAsString(), w));
			}
		} catch (Exception e) {
			Ashbound.LOG.error("world arms not loaded", e);
		}
		return out;
	}

	/** registers them (after {@link Gear#init}: they're weapons like the dungeons', just not forged) */
	static void init() {
		for (Arm a : ARMS) {
			BY_ID.put(a.id(), a);
			Gear.WEAPON.put(a.id(), a.weapon());
			DeferredItem<Item> it = Weapons.ITEMS.registerItem(a.id(), p -> Gear.weapon(a.weapon(),
					p.component(DataComponents.ITEM_NAME, Component.translatable("item.ashbound." + a.id()).withStyle(a.tier().colour))));
			Gear.ITEMS.put(a.id(), it);
			Gear.WEAPONS.add(it);
			ITEMS.add(it);
		}
		NeoForge.EVENT_BUS.addListener(WorldArms::identify);
		NeoForge.EVENT_BUS.addListener(WorldArms::tooltip);
		NeoForge.EVENT_BUS.addListener(WorldArms::chests);
		NeoForge.EVENT_BUS.addListener(WorldArms::died);
		NeoForge.EVENT_BUS.addListener(WorldArms::unequipped);
	}

	static Arm of(ItemStack s) {
		if (s.isEmpty()) return null;
		if (BY_ITEM.isEmpty()) for (DeferredItem<Item> d : ITEMS) BY_ITEM.put(d.get(), BY_ID.get(d.getId().getPath()));
		return BY_ITEM.get(s.getItem());
	}

	/** the dungeon whose element a world staff casts */
	static Gear.Dungeon home(Gear.Weapon w) {
		Arm a = BY_ID.get(w.id());
		return a == null ? null : Gear.of(a.home());
	}

	// ---------------------------------------------------------------- rolls

	private record Affix(String name, Holder<Attribute> attr, AttributeModifier.Operation op, double lo, double hi, String kinds) {
		boolean fits(String kind) {
			return switch (kinds) {
				case "melee" -> !List.of("shield", "bow", "black", "white", "summon").contains(kind);
				case "staff" -> List.of("black", "white", "summon").contains(kind);
				case "guard" -> kind.equals("shield") || kind.equals("hammer") || kind.equals("twohander");
				default -> true;
			};
		}
	}

	/** rolls sized by tools/balance.py pass 5: one uncommon affix is worth 2-4% (docs/BALANCE.md power scale) */
	private static final List<Affix> AFFIXES = List.of(
			new Affix("Keen", Attributes.ATTACK_DAMAGE, AttributeModifier.Operation.ADD_MULTIPLIED_BASE, 0.04, 0.08, "melee"),
			new Affix("Swift", Attributes.ATTACK_SPEED, AttributeModifier.Operation.ADD_MULTIPLIED_BASE, 0.03, 0.06, "melee"),
			new Affix("Brutal", Attributes.ATTACK_DAMAGE, AttributeModifier.Operation.ADD_VALUE, 0.15, 0.35, "melee"),
			new Affix("Hale", Attributes.MAX_HEALTH, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL, 0.025, 0.045, "any"),
			new Affix("Fleet", Attributes.MOVEMENT_SPEED, AttributeModifier.Operation.ADD_MULTIPLIED_BASE, 0.015, 0.03, "any"),
			new Affix("Warded", Attributes.ARMOR, AttributeModifier.Operation.ADD_VALUE, 0.3, 0.6, "any"),
			new Affix("Steadfast", Attributes.KNOCKBACK_RESISTANCE, AttributeModifier.Operation.ADD_VALUE, 0.03, 0.06, "guard"),
			new Affix("Tempered", Attributes.ARMOR_TOUGHNESS, AttributeModifier.Operation.ADD_VALUE, 0.4, 0.9, "guard"),
			new Affix("Lucky", Attributes.LUCK, AttributeModifier.Operation.ADD_VALUE, 0.4, 0.8, "any"),
			new Affix("Arcane", Spells.SPELL_POWER, AttributeModifier.Operation.ADD_MULTIPLIED_BASE, 0.04, 0.08, "staff"),
			new Affix("Deep", Spells.MAX_MANA, AttributeModifier.Operation.ADD_VALUE, 2, 4, "staff"),
			new Affix("Flowing", Spells.MANA_REGEN, AttributeModifier.Operation.ADD_MULTIPLIED_BASE, 0.03, 0.05, "staff"));

	static boolean identified(ItemStack s) {
		return s.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).contains(ROLL);
	}

	/** gives a found copy its affixes, on top of the weapon's own stats */
	static void roll(ItemStack s, Arm a, RandomSource r) {
		List<Affix> pool = new ArrayList<>(AFFIXES.stream().filter(f -> f.fits(a.kind())).toList());
		Collections.shuffle(pool, new java.util.Random(r.nextLong()));
		EquipmentSlotGroup slot = a.kind().equals("shield") ? EquipmentSlotGroup.HAND : EquipmentSlotGroup.MAINHAND;
		ItemAttributeModifiers.Builder b = ItemAttributeModifiers.builder();
		for (ItemAttributeModifiers.Entry e : s.getAttributeModifiers().modifiers()) b.add(e.attribute(), e.modifier(), e.slot());
		CompoundTag tag = new CompoundTag();
		StringBuilder names = new StringBuilder();
		for (int i = 0; i < Math.min(a.tier().affixes, pool.size()); i++) {
			Affix f = pool.get(i);
			double v = (f.lo() + r.nextDouble() * (f.hi() - f.lo())) * a.tier().power;
			if (f.name().equals("Brutal") && a.weapon() != null) v *= Gear.scale(a.weapon().rank()) / Gear.scale('C');
			v = Math.round(v * 1000) / 1000.0;
			b.add(f.attr(), new AttributeModifier(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "roll_" + i), v, f.op()), slot);
			if (names.length() > 0) names.append(", ");
			names.append(f.name());
		}
		tag.putString("affixes", names.toString());
		s.set(DataComponents.ATTRIBUTE_MODIFIERS, b.build());
		CustomData.update(DataComponents.CUSTOM_DATA, s, t -> t.put(ROLL, tag));
	}

	/** found copies are identified as soon as they're in someone's pack */
	/** a piece with max health on it changed out: health drops to the new max, which the client would play as a hit */
	private static void unequipped(net.neoforged.neoforge.event.entity.living.LivingEquipmentChangeEvent e) {
		if (!(e.getEntity() instanceof net.minecraft.server.level.ServerPlayer p)) return;
		var mods = e.getFrom().getOrDefault(net.minecraft.core.component.DataComponents.ATTRIBUTE_MODIFIERS,
				net.minecraft.world.item.component.ItemAttributeModifiers.EMPTY);
		for (var m : mods.modifiers())
			if (m.attribute().equals(Attributes.MAX_HEALTH) && m.modifier().amount() > 0) {
				net.neoforged.neoforge.network.PacketDistributor.sendToPlayer(p, new Net.QuietHealth());
				return;
			}
	}

	private static void identify(PlayerTickEvent.Post e) {
		if (!(e.getEntity() instanceof ServerPlayer p) || p.tickCount % 20 != 0) return;
		var inv = p.getInventory();
		for (int i = 0; i < inv.getContainerSize(); i++) {
			ItemStack s = inv.getItem(i);
			Arm a = of(s);
			if (a == null || identified(s)) continue;
			roll(s, a, p.getRandom());
			if (a.tier().ordinal() >= Tier.EPIC.ordinal()) {
				p.displayClientMessage(Component.literal(a.tier().title + "! ").withStyle(a.tier().colour, ChatFormatting.BOLD)
						.append(Component.literal(a.name()).withStyle(a.tier().colour)), true);
				p.level().playSound(null, p.blockPosition(), a.tier() == Tier.LEGENDARY ? SoundEvents.UI_TOAST_CHALLENGE_COMPLETE
						: SoundEvents.PLAYER_LEVELUP, SoundSource.PLAYERS, 0.7f, 1.1f);
			}
		}
	}

	private static void tooltip(ItemTooltipEvent e) {
		Arm a = of(e.getItemStack());
		if (a == null) {
			Found f = e.getItemStack().isEmpty() ? null : GARB_ITEMS.get(BuiltInRegistries.ITEM.getKey(e.getItemStack().getItem()).getPath());
			if (f != null) {
				List<Component> lines = e.getToolTip();
				int at = Math.min(1, lines.size());
				String cls = f.garb().cls().substring(0, 1).toUpperCase() + f.garb().cls().substring(1);
				lines.add(at++, Component.literal(f.garb().tier().title + " " + cls + " Armour").withStyle(f.garb().tier().colour));
				lines.add(at, Component.literal(f.garb().about()).withStyle(ChatFormatting.DARK_GRAY, ChatFormatting.ITALIC));
			}
			return;
		}
		List<Component> lines = e.getToolTip();
		int at = Math.min(1, lines.size());
		String type = switch (a.kind()) {
			case "twohander" -> "Greatsword";
			case "black" -> "Black Staff";
			case "white" -> "White Staff";
			case "summon" -> "Summoning Staff";
			default -> a.kind().substring(0, 1).toUpperCase() + a.kind().substring(1);
		};
		lines.add(at++, Component.literal(a.tier().title + " " + type).withStyle(a.tier().colour));
		lines.add(at++, Component.literal(a.about()).withStyle(ChatFormatting.DARK_GRAY, ChatFormatting.ITALIC));
		CompoundTag roll = e.getItemStack().getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag().getCompound(ROLL);
		lines.add(at, roll.contains("affixes") ? Component.literal(roll.getString("affixes")).withStyle(ChatFormatting.AQUA)
				: Component.literal("Unidentified: pick it up to see what it rolled").withStyle(ChatFormatting.GRAY));
	}

	// ---------------------------------------------------------------- where they turn up

	/** a random one, rarer ones less often; luck (a dungeon's rank, a boss) tilts it up */
	public static Item pick(RandomSource r, int luck) {
		int total = 0;
		for (Arm a : ARMS) total += weight(a, luck);
		int k = r.nextInt(Math.max(1, total));
		for (Arm a : ARMS) {
			k -= weight(a, luck);
			if (k < 0) return Gear.item(a.id());
		}
		return null;
	}

	private static int weight(Arm a, int luck) {
		return weight(a.tier(), luck);
	}

	private static int weight(Tier t, int luck) {
		int w = t.weight;
		return t == Tier.UNCOMMON ? Math.max(1, w - 4 * luck) : w * (1 + luck);
	}

	/** a random found armour piece, weighted the same way */
	public static Item pickGarb(RandomSource r, int luck) {
		int total = 0;
		for (Found f : GARB_ITEMS.values()) total += weight(f.garb().tier(), luck);
		int k = r.nextInt(Math.max(1, total));
		for (Found f : GARB_ITEMS.values()) {
			k -= weight(f.garb().tier(), luck);
			if (k < 0) return f.item().get();
		}
		return null;
	}

	private static void spill(LivingEntity e, int luck, @org.jetbrains.annotations.Nullable Player owner) {
		spill(e, pick(e.getRandom(), luck), owner);
	}

	/** owner: only they can pick it up (each player in a fight rolls their own) */
	static void spill(LivingEntity e, Item it, @org.jetbrains.annotations.Nullable Player owner) {
		if (it == null) return;
		ItemEntity ie = new ItemEntity(e.level(), e.getX(), e.getY() + 0.5, e.getZ(), new ItemStack(it));
		ie.setDefaultPickUpDelay();
		ie.setGlowingTag(true);
		if (owner != null) ie.setTarget(owner.getUUID());
		e.level().addFreshEntity(ie);
	}

	/** any monster now and then; ours (elites, foremen, bosses) more often */
	private static void died(LivingDeathEvent e) {
		LivingEntity d = e.getEntity();
		if (!(d.level() instanceof ServerLevel) || !(e.getSource().getEntity() instanceof Player) || Spells.isThrall(d)) return;
		RandomSource r = d.getRandom();
		boolean boss = d instanceof MobSkills.User u && u.kind().boss();
		boolean foreman = d.getTags().stream().anyMatch(t -> t.startsWith("ashbound_tower_key:"));
		boolean elite = GateLoot.elite(d);
		// rare on purpose (10/29: a tower gave 3 weapons and an armour piece): a tower's sure thing is its boss hoard.
		// Each player fighting near it rolls their own (docs/BALANCE.md: a party isn't punished)
		List<Player> near = new ArrayList<>(d.level().getEntitiesOfClass(Player.class, d.getBoundingBox().inflate(Balance.radius()), p -> !p.isSpectator()));
		if (near.isEmpty()) near.add((Player) e.getSource().getEntity());
		near.addAll(Party.alongside(near, Party.SHARE));
		for (Player p : near) {
			Player own = near.size() > 1 ? p : null;
			if (boss) {
				if (r.nextFloat() < 0.15f) spill(d, 2, own);
				if (r.nextFloat() < 0.07f) spill(d, pickGarb(r, 2), own);
			} else if (foreman) {
				if (r.nextFloat() < 0.06f) spill(d, 1, own);
				if (r.nextFloat() < 0.03f) spill(d, pickGarb(r, 1), own);
			} else if (elite) {
				if (r.nextFloat() < 0.05f) spill(d, 1, own);
				if (r.nextFloat() < 0.02f) spill(d, pickGarb(r, 1), own);
			} else if (d instanceof Enemy && r.nextFloat() < 0.003f) spill(d, 0, own);
		}
	}

	/** every vanilla chest has a chance of one */
	/** the modpack's big dungeon mods: their chests are a dungeon's reward, so a weapon is likelier there */
	static final java.util.Set<String> BIG_DUNGEONS = java.util.Set.of("dungeons_arise", "cataclysm", "tlc",
			"betterdungeons", "betterstrongholds", "betterfortresses", "betteroceanmonuments", "mowziesmobs");

	private static void chests(LootTableLoadEvent e) {
		ResourceLocation id = e.getName();
		String ns = id.getNamespace(), path = id.getPath();
		// every structure's chests, the modpack's above all (Dungeons Arise, Cataclysm, YUNG's, Towns and Towers, Lost
		// Castle, Dungeons and Taverns...); vanilla's too, since several of those mods fill their chests from vanilla tables.
		// Not our own: the towers' hoards roll these weapons themselves (tools/towers/towerloot.py)
		boolean stash = path.contains("chest") || ns.equals("kaisyn") && (path.startsWith("village/") || path.startsWith("outpost/"));
		if ((ns.equals(Ashbound.ID) && !path.equals("chests/wayside")) || !stash || path.contains("entities/") || path.contains("archeology") || path.contains("archaeology")) return;
		float chance = BIG_DUNGEONS.contains(ns) || path.contains("end_city") || path.contains("ancient_city") || path.contains("bastion")
				|| path.contains("boss") || path.contains("treasure") ? 0.15f
				: path.contains("village") || path.contains("house") || path.contains("tavern") ? 0.04f : 0.07f;
		LootPool.Builder pool = LootPool.lootPool().setRolls(ConstantValue.exactly(1)).when(LootItemRandomChanceCondition.randomChance(chance));
		for (Arm a : ARMS) {
			Item it = BuiltInRegistries.ITEM.get(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, a.id()));
			pool.add(LootItem.lootTableItem(it).setWeight(a.tier().weight));
		}
		e.getTable().addPool(pool.name("ashbound_world_arms").build());
		// the first gates' drops, so a chest on the road is worth a look to a new player too
		if (!ns.equals(Ashbound.ID)) {
			LootPool.Builder road = LootPool.lootPool().setRolls(ConstantValue.exactly(1)).when(LootItemRandomChanceCondition.randomChance(0.35f));
			for (Gear.Dungeon d : Gear.DUNGEONS)
				if (d.rank() == 'F') road.add(LootItem.lootTableItem(Gear.item(d.mats()[0])).setWeight(4)
						.apply(net.minecraft.world.level.storage.loot.functions.SetItemCountFunction.setCount(
								net.minecraft.world.level.storage.loot.providers.number.UniformGenerator.between(1, 4))));
			e.getTable().addPool(road.name("ashbound_road").build());
		}
		if (GARB_ITEMS.isEmpty()) return;
		// and a found armour piece, half as often
		LootPool.Builder garb = LootPool.lootPool().setRolls(ConstantValue.exactly(1)).when(LootItemRandomChanceCondition.randomChance(chance * 0.5f));
		for (Found f : GARB_ITEMS.values()) garb.add(LootItem.lootTableItem(f.item().get()).setWeight(f.garb().tier().weight));
		e.getTable().addPool(garb.name("ashbound_world_armour").build());
	}
}
