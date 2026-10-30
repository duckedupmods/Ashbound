package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;

import com.mojang.serialization.Codec;

import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.neoforged.neoforge.attachment.AttachmentType;
import net.neoforged.neoforge.network.PacketDistributor;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.registries.NeoForgeRegistries;

/**
 * Coins: what you buy, sell and pay with (shops, later the Guild's rewards). A purse attached to you, saved, kept
 * when you die, sent to you whenever it changes. Also what the townsfolk remember of you (FLAGS: "met_smith"...).
 */
public final class Coins {
	private Coins() {}

	static final DeferredRegister<AttachmentType<?>> ATTACHMENTS = DeferredRegister.create(NeoForgeRegistries.ATTACHMENT_TYPES, Ashbound.ID);

	public static final Supplier<AttachmentType<Integer>> PURSE = ATTACHMENTS.register("coins",
			() -> AttachmentType.builder(() -> 0).serialize(Codec.INT).copyOnDeath().build());

	public static final Supplier<AttachmentType<List<String>>> FLAGS = ATTACHMENTS.register("flags",
			() -> AttachmentType.<List<String>>builder(() -> new ArrayList<>()).serialize(Codec.STRING.listOf()).copyOnDeath().build());

	/** Your purse as the server last told it (client side). */
	public static int client;

	public static int of(Player p) {
		return p.level().isClientSide() ? client : p.getData(PURSE);
	}

	public static void set(ServerPlayer p, int coins) {
		p.setData(PURSE, Math.max(0, coins));
		sync(p);
	}

	public static void sync(ServerPlayer p) {
		PacketDistributor.sendToPlayer(p, new Net.Purse(p.getData(PURSE)));
	}

	/** Adds (or with a negative n takes) coins; never below nothing. */
	public static void give(ServerPlayer p, int n) {
		set(p, (int) Math.max(0, Math.min(Integer.MAX_VALUE, (long) of(p) + n)));
	}

	/** Takes n coins if you have them (creative pays nothing). */
	public static boolean pay(ServerPlayer p, int n) {
		if (p.isCreative()) return true;
		if (of(p) < n) return false;
		give(p, -n);
		return true;
	}

	public static boolean flag(Player p, String f) {
		return p.getData(FLAGS).contains(f);
	}

	public static void setFlag(Player p, String f) {
		if (flag(p, f)) return;
		List<String> l = new ArrayList<>(p.getData(FLAGS));
		l.add(f);
		p.setData(FLAGS, l);
	}
}
