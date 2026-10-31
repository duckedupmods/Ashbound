package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import net.minecraft.ChatFormatting;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.entity.EntityAttributeCreationEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;
import net.neoforged.neoforge.network.PacketDistributor;
import net.neoforged.neoforge.registries.DeferredHolder;

/**
 * The mount a player picks right after their class. The server holds the pick the way it holds the class (a flag, once).
 * A mount isn't kept in the world: the key calls it and sends it away, it can't be hurt, and it's gone when you get off, so
 * there's nothing to lose or to fetch. It won't come into a gate. Models: tools/voxmounts.py. Saved picks are flags, an op can
 * clear one with /ashbound mount reset PLAYER, or give one with /ashbound mount set PLAYER KIND.
 */
public final class Mounts {
	private Mounts() {}

	/**
	 * speed in the attribute's units (43 blocks a second per 1), jump as a launch speed, step in blocks; scale, seat and box in blocks;
	 * strides are a full cycle of the legs, in blocks, at a walk and at full speed
	 */
	public record Kind(String id, String name, String title, String blurb, String special, double speed, double jump, double step,
			boolean glides, boolean charges, float scale, float seatY, float seatZ, float w, float h, float strideWalk, float strideRun, boolean burns) {}

	public static final List<Kind> ALL = List.of(
			new Kind("ashmane", "Ashmane", "The burning warhorse", "A destrier that never stopped burning. Nothing on four legs catches it.",
					"Fastest of the five", 0.30, 0.72, 1.1, false, false, 0.74f, 2.411f, -0.135f, 1.3f, 1.7f, 2.2f, 5.5f, true),
			new Kind("rimehorn", "Rimehorn", "The crowned stag", "Antlers of living ice, and a leap that clears walls and rivers.",
					"Jumps six blocks high", 0.245, 1.08, 1.1, false, false, 0.67f, 2.677f, -0.114f, 1.2f, 1.7f, 2.0f, 4.6f, false),
			new Kind("gravefang", "Gravefang", "The soulfire wolf", "Wears its own bones. Goes up rock faces as if they were stairs.",
					"Climbs ledges three blocks high", 0.255, 0.72, 3.1, false, false, 0.8f, 2.211f, -0.311f, 1.3f, 1.5f, 1.6f, 3.7f, false),
			new Kind("thornback", "Thornback", "The old boar of the wood", "A hillside that decided to walk. It does not go around things.",
					"Charges through monsters at full speed", 0.225, 0.6, 1.1, false, true, 0.72f, 2.454f, -0.122f, 1.5f, 1.6f, 1.2f, 2.6f, true),
			new Kind("stormdrake", "Stormdrake", "The lightning wyvern", "Too heavy to fly for long, but off a high place it owns the sky.",
					"Hold jump in the air to glide", 0.24, 0.72, 1.1, true, false, 0.78f, 2.267f, 0.118f, 1.4f, 1.6f, 1.5f, 3.2f, false));

	private static final String FLAG = "mount_";
	private static final int ASK_EVERY = 60;
	/** You don't get on with something hitting you (ticks since the last hit). */
	private static final int CALM = 60;
	private static final Map<String, DeferredHolder<EntityType<?>, EntityType<Mount>>> TYPES = new LinkedHashMap<>();

	/** Your own mount on your own screen; empty until you've picked one. */
	public static String client = "";

	public static Kind byId(String id) {
		for (Kind k : ALL)
			if (k.id().equals(id)) return k;
		return null;
	}

	public static Kind of(Player p) {
		for (Kind k : ALL)
			if (Coins.flag(p, FLAG + k.id())) return k;
		return null;
	}

	public static EntityType<Mount> type(Kind k) {
		return TYPES.get(k.id()).get();
	}

	static Kind ofType(EntityType<?> t) {
		for (Kind k : ALL)
			if (TYPES.get(k.id()).get() == t) return k;
		throw new IllegalArgumentException(String.valueOf(t));
	}

	public static final java.util.function.Supplier<EntityType<Thrall>> REVENANT = Monsters.ENTITIES.register("thrall_revenant",
			() -> EntityType.Builder.<Thrall>of((t, l) -> new Thrall(t, l, false), MobCategory.MISC).sized(0.7f, 2.1f).noSave().build("thrall_revenant"));
	public static final java.util.function.Supplier<EntityType<Thrall>> CHAMPION = Monsters.ENTITIES.register("thrall_champion",
			() -> EntityType.Builder.<Thrall>of((t, l) -> new Thrall(t, l, true), MobCategory.MISC).sized(1.3f, 3.6f).noSave().build("thrall_champion"));

	static void ask(ServerPlayer p) {
		Classes.asking(p, true);
		PacketDistributor.sendToPlayer(p, new Net.MountState(""));
	}

	/** A player's answer. Anything but a first, known pick is ignored. */
	public static void pick(ServerPlayer p, String id) {
		Kind k = byId(id);
		if (k == null || of(p) != null || Classes.of(p) == null || !p.isAlive()) return;
		Coins.setFlag(p, FLAG + k.id());
		Classes.asking(p, false);
		PacketDistributor.sendToPlayer(p, new Net.MountState(k.id()));
		p.sendSystemMessage(Component.literal(k.name() + " answers to you now. Press the mount key (H) to call it.").withStyle(ChatFormatting.GOLD));
	}

	/** The key: on if you're not riding, off if you are. */
	public static void toggle(ServerPlayer p) {
		if (p.getVehicle() instanceof Mount m) {
			m.leave();
			return;
		}
		Kind k = of(p);
		if (k == null || p.isPassenger() || !p.isAlive()) return;
		String no = p.level().dimension() == Lairs.GATES ? "Your mount won't follow you into a gate."
				: p.getLastHurtByMobTimestamp() > 0 && p.tickCount - p.getLastHurtByMobTimestamp() < CALM ? "Not with them on you."
				: null;
		Mount m = no == null ? type(k).create(p.level()) : null;
		// it comes up beside you, on your right if it fits, and you vault across; with no room or no ground, it comes up under you
		if (m != null) {
			Vec3 right = Vec3.directionFromRotation(0, p.getYRot() + 90);
			boolean found = false;
			for (int side : p.onGround() ? new int[] {1, -1, 0} : new int[] {0}) {
				Vec3 at = p.position().add(right.scale(side * Mount.BESIDE));
				m.moveTo(at.x, at.y, at.z, p.getYRot(), 0);
				if (found = p.level().noCollision(m)) {
					m.side(side);
					break;
				}
			}
			if (!found) {
				no = "There's no room for it here.";
				m = null;
			}
		}
		if (no != null) {
			p.displayClientMessage(Component.literal(no).withStyle(ChatFormatting.RED), true);
			return;
		}
		p.level().addFreshEntity(m);
		p.startRiding(m, true);
		m.arrive();
	}

	private static int reset(CommandSourceStack src, ServerPlayer p) {
		List<String> l = new ArrayList<>(p.getData(Coins.FLAGS));
		l.removeIf(f -> f.startsWith(FLAG));
		p.setData(Coins.FLAGS, l);
		if (p.getVehicle() instanceof Mount) p.stopRiding();
		PacketDistributor.sendToPlayer(p, new Net.MountState(""));
		src.sendSuccess(() -> Component.literal(p.getName().getString() + " can choose a mount again"), true);
		return 1;
	}

	private static int set(CommandSourceStack src, ServerPlayer p, String id) {
		Kind k = byId(id);
		if (k == null) {
			src.sendFailure(Component.literal("No such mount: " + id));
			return 0;
		}
		reset(src, p);
		Coins.setFlag(p, FLAG + k.id());
		PacketDistributor.sendToPlayer(p, new Net.MountState(k.id()));
		return 1;
	}

	public static void register(IEventBus bus) {
		for (Kind k : ALL)
			TYPES.put(k.id(), Monsters.ENTITIES.register("mount_" + k.id(), () -> EntityType.Builder.<Mount>of(Mount::new, MobCategory.MISC)
					.sized(k.w(), k.h()).fireImmune().clientTrackingRange(10).updateInterval(1).noSave().build(Ashbound.ID + ":mount_" + k.id())));
		bus.addListener((EntityAttributeCreationEvent e) -> {
			e.put(REVENANT.get(), Thrall.attributes(false).build());
			e.put(CHAMPION.get(), Thrall.attributes(true).build());
			for (Kind k : ALL) e.put(type(k), Mount.attributes(k).build());
		});
		NeoForge.EVENT_BUS.addListener((PlayerEvent.PlayerLoggedInEvent e) -> {
			if (e.getEntity() instanceof ServerPlayer p) {
				Kind k = of(p);
				if (k != null) PacketDistributor.sendToPlayer(p, new Net.MountState(k.id()));
			}
		});
		// a mount doesn't outlive its rider's visit
		NeoForge.EVENT_BUS.addListener((PlayerEvent.PlayerLoggedOutEvent e) -> {
			if (e.getEntity().getVehicle() instanceof Mount) e.getEntity().stopRiding();
		});
		// after the class is settled, and again if Esc closed the question
		NeoForge.EVENT_BUS.addListener((PlayerTickEvent.Post e) -> {
			if (e.getEntity() instanceof ServerPlayer p && p.tickCount % ASK_EVERY == 0 && p.isAlive() && Classes.of(p) != null && of(p) == null) ask(p);
		});
		NeoForge.EVENT_BUS.addListener((RegisterCommandsEvent e) -> e.getDispatcher().register(Commands.literal("ashbound")
				.requires(s -> s.hasPermission(2))
				.then(Commands.literal("mount")
						.then(Commands.literal("reset").then(Commands.argument("player", EntityArgument.player())
								.executes(c -> reset(c.getSource(), EntityArgument.getPlayer(c, "player")))))
						.then(Commands.literal("set").then(Commands.argument("player", EntityArgument.player())
								.then(Commands.argument("kind", com.mojang.brigadier.arguments.StringArgumentType.word())
										.executes(c -> set(c.getSource(), EntityArgument.getPlayer(c, "player"), com.mojang.brigadier.arguments.StringArgumentType.getString(c, "kind")))))))));
	}
}
