package com.snoringwalrus.ashbound;

import com.google.common.collect.HashMultimap;
import com.google.common.collect.Multimap;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import net.minecraft.ChatFormatting;
import net.minecraft.core.Holder;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.level.storage.loot.LootPool;
import net.minecraft.world.level.storage.loot.entries.LootItem;
import net.minecraft.world.level.storage.loot.predicates.LootItemRandomChanceCondition;
import net.minecraft.world.level.storage.loot.providers.number.ConstantValue;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.LootTableLoadEvent;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.level.Level;
import net.neoforged.neoforge.registries.DeferredItem;
import top.theillusivec4.curios.api.CuriosApi;
import top.theillusivec4.curios.api.SlotContext;
import top.theillusivec4.curios.api.type.capability.ICurioItem;
import yesman.epicfight.registry.entries.EpicFightAttributes;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Curios and relics (docs/RELICS.md, tools/curios.py): 20 rings, 20 amulets, 20 charms and 16 relics in the Curios slots
 * (ring x2, necklace, charm and our relic slot). Their stats are attribute modifiers while worn; the stats no attribute
 * holds (bow damage, Ash, coins...) are summed by {@link #stat} and read where the tree's are ({@link Passives#stat}).
 */
public final class Curios {
	private Curios() {}

	public record Spec(String id, String name, String slot, WorldArms.Tier tier, String faction, Map<String, Double> stats, String effect,
			Worn worn) {}

	/** how it's drawn on the body (client/WornCurios.java): its mesh, size, the top-middle it hangs from and its depth, in pixels */
	public record Worn(String model, float scale, float topX, float topY, float topZ, float depth) {}

	public static final List<Spec> SPECS = load();
	static final List<DeferredItem<Item>> ITEMS = new ArrayList<>();
	public static final List<DeferredItem<Item>> PET_ITEMS = new ArrayList<>();

	private record Attr(Holder<Attribute> attr, AttributeModifier.Operation op, double scale, String label) {}

	private static final Map<String, Attr> ATTR = new LinkedHashMap<>();
	/** stats no attribute holds: how they read in the tooltip */
	private static final Map<String, String> OWN = new LinkedHashMap<>();

	private static Map<String, Attr> attrs() {
		if (ATTR.isEmpty()) {
			var base = AttributeModifier.Operation.ADD_MULTIPLIED_BASE;
			var total = AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL;
			var add = AttributeModifier.Operation.ADD_VALUE;
			ATTR.put("dmg%", new Attr(Attributes.ATTACK_DAMAGE, total, 0.01, "Melee damage"));
			ATTR.put("speed%", new Attr(Attributes.ATTACK_SPEED, total, 0.01, "Attack speed"));
			ATTR.put("health%", new Attr(Attributes.MAX_HEALTH, total, 0.01, "Max health"));
			ATTR.put("armour%", new Attr(Attributes.ARMOR, total, 0.01, "Armour"));
			ATTR.put("tough%", new Attr(Attributes.ARMOR_TOUGHNESS, total, 0.01, "Toughness"));
			ATTR.put("kb%", new Attr(Attributes.KNOCKBACK_RESISTANCE, add, 0.01, "Knockback resistance"));
			ATTR.put("move%", new Attr(Attributes.MOVEMENT_SPEED, base, 0.01, "Move speed"));
			ATTR.put("luck", new Attr(Attributes.LUCK, add, 1, "Luck"));
			ATTR.put("mana", new Attr(Spells.MAX_MANA, add, 1, "Mana"));
			ATTR.put("mana_regen%", new Attr(Spells.MANA_REGEN, base, 0.01, "Mana regen"));
			ATTR.put("spell%", new Attr(Spells.SPELL_POWER, base, 0.01, "Spell power"));
			ATTR.put("heal%", new Attr(Spells.SPELL_POWER, base, 0.01, "Healing"));
			ATTR.put("stamina_regen%", new Attr(EpicFightAttributes.STAMINA_REGEN, base, 0.01, "Stamina regen"));
			ATTR.put("safe_fall", new Attr(Attributes.SAFE_FALL_DISTANCE, add, 1, "Safe fall (blocks)"));
			ATTR.put("mining%", new Attr(Attributes.BLOCK_BREAK_SPEED, base, 0.01, "Mining speed"));
			ATTR.put("oxygen", new Attr(Attributes.OXYGEN_BONUS, add, 1, "Oxygen"));
			ATTR.put("swim%", new Attr(Attributes.WATER_MOVEMENT_EFFICIENCY, add, 0.01, "Swim speed"));
			OWN.put("arrow%", "Bow damage");
			OWN.put("thrall_dmg%", "Thrall damage");
			OWN.put("thrall_hp%", "Thrall health");
			OWN.put("ash%", "Ash from kills");
			OWN.put("coins%", "Coins from kills");
			OWN.put("elite_dmg%", "Damage to elites and bosses");
			OWN.put("poison_short%", "Shorter poison and wither");
			OWN.put("dodge_cost%", "Cheaper dodges");
		}
		return ATTR;
	}

	private static List<Spec> load() {
		List<Spec> out = new ArrayList<>();
		try (InputStream in = Curios.class.getResourceAsStream("/ashbound/curios.json")) {
			if (in == null) return out;
			for (JsonElement el : JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonArray()) {
				JsonObject o = el.getAsJsonObject();
				Map<String, Double> stats = new LinkedHashMap<>();
				for (var e : o.getAsJsonObject("stats").entrySet()) stats.put(e.getKey(), e.getValue().getAsDouble());
				JsonObject w = o.getAsJsonObject("worn");
				var top = w.getAsJsonArray("top");
				out.add(new Spec(o.get("id").getAsString(), o.get("name").getAsString(), o.get("slot").getAsString(),
						WorldArms.Tier.valueOf(o.get("rarity").getAsString().toUpperCase()), o.get("faction").getAsString(), stats,
						o.get("effect").getAsString(), new Worn(w.get("model").getAsString(), w.get("scale").getAsFloat(),
						top.get(0).getAsFloat(), top.get(1).getAsFloat(), top.get(2).getAsFloat(), w.get("depth").getAsFloat())));
			}
		} catch (Exception e) {
			Ashbound.LOG.error("curios not loaded", e);
		}
		return out;
	}

	/** registers them (on the weapons' item register) */
	static void init() {
		for (Spec s : SPECS) ITEMS.add(register(s));
		for (Spec s : Pets.specs()) {
			DeferredItem<Item> item = register(s);
			ITEMS.add(item);
			PET_ITEMS.add(item);
		}
		NeoForge.EVENT_BUS.addListener(Curios::chests);
		NeoForge.EVENT_BUS.addListener(Curios::died);
	}

	private static DeferredItem<Item> register(Spec s) {
		return Weapons.ITEMS.registerItem(s.id(), p -> new Curio(p.stacksTo(1)
				.component(DataComponents.ITEM_NAME, Component.translatable("item.ashbound." + s.id()).withStyle(s.tier().colour)), s));
	}

	// ---------------------------------------------------------------- where they turn up (like the world weapons, rarer)

	public static Item item(Spec s) {
		return BuiltInRegistries.ITEM.get(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, s.id()));
	}

	private static String buff(String key, double value) {
		Attr a = ATTR.get(key);
		return num(value) + (key.endsWith("%") ? "%" : "") + " " + (a != null ? a.label() : OWN.getOrDefault(key, key));
	}

	/** What a curio gives, a line a stat. */
	public static List<String> buffs(Spec s) {
		attrs();
		return s.stats().entrySet().stream().map(e -> buff(e.getKey(), e.getValue())).toList();
	}

	/** a random curio (relics: false) or relic (true), rarer tiers less often, luck tilting it up */
	static Item pick(RandomSource r, boolean relic, int luck) {
		List<Spec> pool = SPECS.stream().filter(s -> s.slot().equals("relic") == relic).toList();
		int total = 0;
		for (Spec s : pool) total += weight(s.tier(), luck);
		int k = r.nextInt(Math.max(1, total));
		for (Spec s : pool) {
			k -= weight(s.tier(), luck);
			if (k < 0) return item(s);
		}
		return null;
	}

	/** a random pet, the same way */
	static Item pet(RandomSource r, int luck) {
		List<Spec> pool = Pets.specs();
		int total = 0;
		for (Spec s : pool) total += weight(s.tier(), luck);
		int k = r.nextInt(Math.max(1, total));
		for (Spec s : pool) {
			k -= weight(s.tier(), luck);
			if (k < 0) return item(s);
		}
		return null;
	}

	private static int weight(WorldArms.Tier t, int luck) {
		return t == WorldArms.Tier.UNCOMMON ? Math.max(1, t.weight - 4 * luck) : t.weight * (1 + luck);
	}

	/** monsters: bosses and tower foremen can drop a relic; each player near rolls their own */
	private static void died(LivingDeathEvent e) {
		LivingEntity d = e.getEntity();
		if (!(d.level() instanceof ServerLevel) || !(e.getSource().getEntity() instanceof Player) || Spells.isThrall(d)) return;
		RandomSource r = d.getRandom();
		boolean boss = d instanceof MobSkills.User u && u.kind().boss();
		boolean foreman = d.getTags().stream().anyMatch(t -> t.startsWith("ashbound_tower_key:"));
		boolean elite = GateLoot.elite(d);
		List<Player> near = new ArrayList<>(d.level().getEntitiesOfClass(Player.class, d.getBoundingBox().inflate(Balance.radius()), p -> !p.isSpectator()));
		if (near.isEmpty()) near.add((Player) e.getSource().getEntity());
		for (Player p : near) {
			Player own = near.size() > 1 ? p : null;
			if (boss) {
				if (r.nextFloat() < 0.12f) WorldArms.spill(d, pick(r, false, 2), own);
				if (r.nextFloat() < 0.06f) WorldArms.spill(d, pick(r, true, 0), own);
				if (r.nextFloat() < 0.08f) WorldArms.spill(d, pet(r, 2), own);
			} else if (foreman) {
				if (r.nextFloat() < 0.05f) WorldArms.spill(d, pick(r, false, 1), own);
				if (r.nextFloat() < 0.02f) WorldArms.spill(d, pick(r, true, 0), own);
				if (r.nextFloat() < 0.04f) WorldArms.spill(d, pet(r, 1), own);
			} else if (elite) {
				if (r.nextFloat() < 0.04f) WorldArms.spill(d, pick(r, false, 1), own);
				if (r.nextFloat() < 0.02f) WorldArms.spill(d, pet(r, 1), own);
			} else if (d instanceof Enemy && r.nextFloat() < 0.002f) WorldArms.spill(d, pick(r, false, 0), own);
			else if (d instanceof Enemy && r.nextFloat() < 0.001f) WorldArms.spill(d, pet(r, 0), own);
		}
	}

	/** structure chests: a curio now and then; a relic only in the big dungeons' and treasure chests */
	private static void chests(LootTableLoadEvent e) {
		ResourceLocation id = e.getName();
		String ns = id.getNamespace(), path = id.getPath();
		boolean stash = path.contains("chest") || ns.equals("kaisyn") && (path.startsWith("village/") || path.startsWith("outpost/"));
		if (ns.equals(Ashbound.ID) || !stash || path.contains("entities/") || path.contains("archeology") || path.contains("archaeology")) return;
		boolean big = WorldArms.BIG_DUNGEONS.contains(ns) || path.contains("end_city") || path.contains("ancient_city") || path.contains("bastion")
				|| path.contains("boss") || path.contains("treasure");
		float chance = big ? 0.10f : path.contains("village") || path.contains("house") || path.contains("tavern") ? 0.025f : 0.05f;
		LootPool.Builder pool = LootPool.lootPool().setRolls(ConstantValue.exactly(1)).when(LootItemRandomChanceCondition.randomChance(chance));
		for (Spec s : SPECS) if (!s.slot().equals("relic")) pool.add(LootItem.lootTableItem(item(s)).setWeight(s.tier().weight));
		e.getTable().addPool(pool.name("ashbound_curios").build());
		LootPool.Builder pets = LootPool.lootPool().setRolls(ConstantValue.exactly(1)).when(LootItemRandomChanceCondition.randomChance(big ? 0.05f : 0.015f));
		for (Spec s : Pets.specs()) pets.add(LootItem.lootTableItem(item(s)).setWeight(s.tier().weight));
		e.getTable().addPool(pets.name("ashbound_pets").build());
		if (!big) return;
		LootPool.Builder relics = LootPool.lootPool().setRolls(ConstantValue.exactly(1)).when(LootItemRandomChanceCondition.randomChance(0.03f));
		for (Spec s : SPECS) if (s.slot().equals("relic")) relics.add(LootItem.lootTableItem(item(s)));
		e.getTable().addPool(relics.name("ashbound_relics").build());
	}

	/** a stat no attribute holds, summed over what the player wears (0 for the attribute stats: those are modifiers) */
	static double stat(Player p, String key) {
		if (attrs().containsKey(key)) return 0;
		double[] v = {0};
		CuriosApi.getCuriosInventory(p).ifPresent(inv -> inv.findCurios(st -> st.getItem() instanceof Curio).forEach(r ->
				v[0] += ((Curio) r.stack().getItem()).spec.stats().getOrDefault(key, 0.0)));
		return v[0];
	}

	/** whether the player wears this curio or relic */
	static boolean wears(Player p, String id) {
		return CuriosApi.getCuriosInventory(p).map(inv -> inv.isEquipped(st -> st.getItem() instanceof Curio c && c.spec.id().equals(id)))
				.orElse(false);
	}

	private static String num(double v) {
		return (v > 0 ? "+" : "") + (v == Math.rint(v) ? String.valueOf((int) v) : String.valueOf(v));
	}

	public static final class Curio extends Item implements ICurioItem {
		final Spec spec;

		public Spec spec() {
			return spec;
		}

		Curio(Properties p, Spec spec) {
			super(p);
			this.spec = spec;
		}

		@Override
		public Multimap<Holder<Attribute>, AttributeModifier> getAttributeModifiers(SlotContext ctx, ResourceLocation id, ItemStack stack) {
			Map<Holder<Attribute>, Map<AttributeModifier.Operation, Double>> sum = new LinkedHashMap<>();
			for (var e : spec.stats().entrySet()) {
				Attr a = attrs().get(e.getKey());
				if (a != null) sum.computeIfAbsent(a.attr(), k -> new LinkedHashMap<>()).merge(a.op(), e.getValue() * a.scale(), Double::sum);
			}
			Multimap<Holder<Attribute>, AttributeModifier> out = HashMultimap.create();
			sum.forEach((attr, ops) -> ops.forEach((op, v) -> out.put(attr,
					new AttributeModifier(id.withSuffix("_" + op.name().toLowerCase()), v, op))));
			return out;
		}

		/** taking off max health: the lower max isn't a hit (no red flash, no flinch), as with the tree and weapons */
		@Override
		public void onUnequip(SlotContext ctx, ItemStack next, ItemStack stack) {
			if (ctx.entity() instanceof net.minecraft.server.level.ServerPlayer p && spec.stats().getOrDefault("health%", 0.0) > 0)
				net.neoforged.neoforge.network.PacketDistributor.sendToPlayer(p, new Net.QuietHealth());
		}

		/** the Curios slot it goes in (an amulet in their necklace slot) */
		public String slotId() {
			return spec.slot().equals("amulet") ? "necklace" : spec.slot();
		}

		/** right-click in hand: into a free slot of its kind, or swapped for what's worn there (the first ring, sneak: the second) */
		@Override
		public InteractionResultHolder<ItemStack> use(Level level, Player p, InteractionHand hand) {
			ItemStack held = p.getItemInHand(hand);
			var handler = CuriosApi.getCuriosInventory(p).flatMap(inv -> inv.getStacksHandler(slotId())).orElse(null);
			if (handler == null || handler.getSlots() == 0) return InteractionResultHolder.pass(held);
			var stacks = handler.getStacks();
			int at = p.isShiftKeyDown() ? stacks.getSlots() - 1 : 0;   // both rings on: sneak swaps the second
			for (int i = 0; i < stacks.getSlots(); i++)
				if (stacks.getStackInSlot(i).isEmpty()) {
					at = i;
					break;
				}
			ItemStack old = stacks.getStackInSlot(at);
			if (!old.isEmpty() && ItemStack.isSameItemSameComponents(old, held)) return InteractionResultHolder.fail(held);
			if (!level.isClientSide) {
				stacks.setStackInSlot(at, held.copy());
				level.playSound(null, p.blockPosition(), spec.slot().equals("relic") ? SoundEvents.ARMOR_EQUIP_NETHERITE.value()
						: SoundEvents.ARMOR_EQUIP_CHAIN.value(), SoundSource.PLAYERS, 0.8f, 1.1f);
			}
			return InteractionResultHolder.sidedSuccess(old.copy(), level.isClientSide);
		}

		@Override
		public List<Component> getAttributesTooltip(List<Component> tooltips, TooltipContext ctx, ItemStack stack) {
			return new ArrayList<>();   // our own lines below, the same wording for every stat
		}

		@Override
		public void appendHoverText(ItemStack stack, TooltipContext ctx, List<Component> lines, net.minecraft.world.item.TooltipFlag flag) {
			String slot = switch (spec.slot()) {
				case "amulet" -> "Amulet";
				case "charm" -> "Charm";
				case "relic" -> "Relic";
				case "pet" -> "Pet";
				default -> "Ring";
			};
			lines.add(Component.literal(spec.tier().title + " " + slot).withStyle(spec.tier().colour));
			lines.add(Component.literal(spec.faction()).withStyle(ChatFormatting.DARK_GRAY, ChatFormatting.ITALIC));
			attrs();
			for (var e : spec.stats().entrySet())
				lines.add(Component.literal(buff(e.getKey(), e.getValue())).withStyle(e.getValue() < 0 ? ChatFormatting.RED : ChatFormatting.BLUE));
			if (spec.slot().equals("relic")) {
				int t = CurioFx.tier(stack);
				lines.add(Component.literal("Power " + CurioFx.roman(t) + (t < 3 ? "  (raise it at a Gate Forge with boss trophies and Ash)" : ""))
						.withStyle(ChatFormatting.YELLOW));
			}
			if (!spec.effect().isEmpty())
				lines.add(Component.literal(spec.effect()).withStyle(spec.tier() == WorldArms.Tier.LEGENDARY ? ChatFormatting.GOLD : ChatFormatting.LIGHT_PURPLE));
		}
	}
}
