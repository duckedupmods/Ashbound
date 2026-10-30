package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.google.gson.Gson;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.mojang.serialization.JsonOps;

import net.minecraft.ChatFormatting;
import net.minecraft.core.RegistryAccess;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.RegistryOps;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.server.packs.resources.SimpleJsonResourceReloadListener;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.profiling.ProfilerFiller;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.AddReloadListenerEvent;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * The shops: each one's wares are a file in data/ashbound/shop/ (tools/npc_shops.py), named for the shopkeeper's
 * kind or their trade ("trade_baker"); the city's cast says who keeps which. Everything is priced in coins.
 *
 *   "buy":  [{"item": {"id": "minecraft:bread", "count": 3}, "price": 20}, ...]   an ItemStack, with components if need be
 *   "sell": [{"item": "minecraft:bone", "price": 3}, ...]                          what they'll take off you, each
 */
public final class Shop {
	private Shop() {}

	public record Wares(List<Net.ShopLine> buy, List<Net.ShopLine> sell) {}

	private static Map<String, Wares> SHOPS = Map.of();

	public static Wares of(String id) {
		return id == null || id.isEmpty() ? null : SHOPS.get(id);
	}

	private static void load(Map<ResourceLocation, JsonElement> files, RegistryAccess access) {
		Map<String, Wares> out = new HashMap<>();
		RegistryOps<JsonElement> ops = RegistryOps.create(JsonOps.INSTANCE, access);
		for (var e : files.entrySet()) {
			if (!e.getKey().getNamespace().equals(Ashbound.ID)) continue;
			try {
				JsonObject j = e.getValue().getAsJsonObject();
				List<Net.ShopLine> buy = new ArrayList<>(), sell = new ArrayList<>();
				if (j.has("buy")) for (JsonElement le : j.getAsJsonArray("buy")) {
					JsonObject l = le.getAsJsonObject();
					var s = ItemStack.CODEC.parse(ops, l.get("item"));
					if (s.result().isPresent()) buy.add(new Net.ShopLine(s.result().get(), l.get("price").getAsInt()));
					else Ashbound.LOG.warn("Shop {}: no such ware {}", e.getKey(), l.get("item"));
				}
				if (j.has("sell")) for (JsonElement le : j.getAsJsonArray("sell")) {
					JsonObject l = le.getAsJsonObject();
					ItemStack s = new ItemStack(BuiltInRegistries.ITEM.get(ResourceLocation.parse(l.get("item").getAsString())));
					if (!s.isEmpty()) sell.add(new Net.ShopLine(s, l.get("price").getAsInt()));
				}
				out.put(e.getKey().getPath(), new Wares(buy, sell));
			} catch (Exception ex) {
				Ashbound.LOG.error("Couldn't read the shop {}", e.getKey(), ex);
			}
		}
		SHOPS = out;
		Ashbound.LOG.info("{} shops", out.size());
	}

	/** Shows you their wares. */
	public static void open(ServerPlayer p, Npc npc) {
		Wares w = of(npc.shopId());
		Talk.Kind k = npc.kind();
		if (w == null || k == null) return;
		Coins.sync(p);
		PacketDistributor.sendToPlayer(p, new Net.ShopOpen(npc.getId(), k.name(), k.title(), w.buy(), w.sell()));
	}

	/** How many of this they're carrying (plain ones: no damage, no enchantments, no custom name). */
	public static int carried(Player p, ItemStack like) {
		int n = 0;
		var inv = p.getInventory();
		for (int i = 0; i < inv.getContainerSize(); i++) {
			ItemStack s = inv.getItem(i);
			if (plain(s, like)) n += s.getCount();
		}
		return n;
	}

	private static boolean plain(ItemStack s, ItemStack like) {
		return !s.isEmpty() && s.is(like.getItem()) && !s.isDamaged() && !s.isEnchanted() && !s.has(DataComponents.CUSTOM_NAME);
	}

	public static void onTrade(Net.ShopTrade msg, ServerPlayer p) {
		if (!(p.level().getEntity(msg.entity()) instanceof Npc npc) || npc.distanceTo(p) > 8) return;
		Wares w = of(npc.shopId());
		if (w == null) return;
		List<Net.ShopLine> lines = msg.sell() ? w.sell() : w.buy();
		if (msg.line() < 0 || msg.line() >= lines.size()) return;
		Net.ShopLine l = lines.get(msg.line());
		int times = Math.max(1, Math.min(64, msg.times()));
		if (msg.sell()) {
			times = Math.min(times, carried(p, l.stack()));
			if (times <= 0) return;
			int left = times;
			var inv = p.getInventory();
			for (int i = 0; i < inv.getContainerSize() && left > 0; i++) {
				ItemStack s = inv.getItem(i);
				if (!plain(s, l.stack())) continue;
				int take = Math.min(left, s.getCount());
				s.shrink(take);
				left -= take;
			}
			int pay = times * l.price();
			Coins.give(p, pay);
			p.displayClientMessage(Component.literal("+" + pay + " coins").withStyle(ChatFormatting.GOLD), true);
			p.level().playSound(null, npc.blockPosition(), SoundEvents.CHAIN_PLACE, SoundSource.NEUTRAL, 0.8f, 1.3f);
		} else {
			if (!p.isCreative()) times = Math.min(times, Coins.of(p) / Math.max(1, l.price()));
			if (times <= 0) {
				p.displayClientMessage(Component.literal("Not enough coins").withStyle(ChatFormatting.DARK_RED), true);
				return;
			}
			for (int k = 0; k < times; k++) {
				ItemStack s = l.stack().copy();
				if (!p.getInventory().add(s) && !s.isEmpty()) p.spawnAtLocation(s);
			}
			int cost = times * l.price();
			Coins.pay(p, cost);
			p.displayClientMessage(Component.literal("-" + cost + " coins").withStyle(ChatFormatting.GOLD), true);
			p.level().playSound(null, npc.blockPosition(), SoundEvents.ARMOR_EQUIP_LEATHER.value(), SoundSource.NEUTRAL, 0.8f, 1.0f);
		}
		p.containerMenu.broadcastChanges();
	}

	static void init() {
		NeoForge.EVENT_BUS.addListener((AddReloadListenerEvent e) -> {
			RegistryAccess access = e.getRegistryAccess();
			e.addListener(new SimpleJsonResourceReloadListener(new Gson(), "shop") {
				@Override
				protected void apply(Map<ResourceLocation, JsonElement> files, ResourceManager rm, ProfilerFiller pf) {
					load(files, access);
				}
			});
		});
	}
}
