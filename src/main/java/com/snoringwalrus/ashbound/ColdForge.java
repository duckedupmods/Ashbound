package com.snoringwalrus.ashbound;

import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.living.LivingDeathEvent;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.neoforged.neoforge.network.PacketDistributor;
import net.neoforged.neoforge.registries.DeferredItem;

/**
 * The Cold Forge in the vault under the Ashforge, older than the city round it. It sits dead until someone brings it a
 * First Ember: Wendel tells you of it, you touch the cold stone, he sends you after three shards the rank E, D and C
 * bosses carry, and he binds them into the Ember. Fed the Ember it wakes (client/ColdScene), for everyone, for good,
 * and the Joining of boss weapons is done on its altar.
 */
public final class ColdForge {
	private ColdForge() {}

	public static final DeferredItem<Item> SHARD = Weapons.ITEMS.registerItem("ember_shard", p -> new Item(p.rarity(Rarity.RARE).stacksTo(3).fireResistant()));
	public static final DeferredItem<Item> EMBER = Weapons.ITEMS.registerItem("first_ember", p -> new Item(p.rarity(Rarity.EPIC).stacksTo(1).fireResistant()));
	/** Ossric's sigil, Wendel's once the forge is awake: Veyra sends you with it to the Kiln-Father's Hearth (BossArenas). */
	public static final DeferredItem<Item> BRAND = Weapons.ITEMS.registerItem("founders_brand", p -> new Item(p.rarity(Rarity.EPIC).stacksTo(1).fireResistant()));

	private static final String SHARD_RANKS = "EDC";
	private static final int SWAP_AT = 80, WAKE_ENDS = 220;

	static void init() {
		NeoForge.EVENT_BUS.addListener(ColdForge::onClick);
		NeoForge.EVENT_BUS.addListener(ColdForge::tick);
	}

	// ---------------------------------------------------------------- where its pieces lie

	private record Layout(int w, int d, Map<Integer, int[]> cells, List<int[]> pieces) {}

	private static Layout dead, lit;

	private static Layout read(JsonObject all, String name) {
		JsonObject o = all.getAsJsonObject(name);
		JsonArray size = o.getAsJsonArray("size");
		Map<Integer, int[]> cells = new HashMap<>();
		List<int[]> pieces = new ArrayList<>();
		for (var e : o.getAsJsonArray("pieces")) {
			JsonArray a = e.getAsJsonArray();
			int[] c = {a.get(0).getAsInt(), a.get(1).getAsInt(), a.get(2).getAsInt(), a.get(3).getAsInt()};
			pieces.add(c);
			cells.put(c[3], c);
		}
		return new Layout(size.get(0).getAsInt(), size.get(2).getAsInt(), cells, pieces);
	}

	private static void load() {
		if (dead != null) return;
		try (var in = new InputStreamReader(ColdForge.class.getResourceAsStream("/ashbound/cold_forge_pieces.json"), StandardCharsets.UTF_8)) {
			JsonObject all = JsonParser.parseReader(in).getAsJsonObject();
			dead = read(all, "cold_forge");
			lit = read(all, "cold_forge_lit");
		} catch (java.io.IOException e) {
			throw new IllegalStateException("cold_forge_pieces.json", e);
		}
	}

	private static int[] turn(int x, int z, int q) {
		for (int i = 0; i < q; i++) {
			int t = x;
			x = -z - 1;
			z = t;
		}
		return new int[] {x, z};
	}

	private static int quarter(Direction f) {
		return f == Direction.EAST ? 1 : f == Direction.SOUTH ? 2 : f == Direction.WEST ? 3 : 0;
	}

	/** Where a cell of a footprint falls in the world, from the world's corner the sculpt was placed from (capital_city.sculpt). */
	private static BlockPos at(BlockPos corner, Layout l, int q, int x, int y, int z) {
		int[] a = turn(0, 0, q), b = turn(l.w - 1, l.d - 1, q), t = turn(x, z, q);
		return corner.offset(t[0] - Math.min(a[0], b[0]), y, t[1] - Math.min(a[1], b[1]));
	}

	private static BlockPos corner(BlockState s, BlockPos pos) {
		load();
		boolean on = isLit(s);
		Layout l = on ? lit : dead;
		PropBlock.Sculpt b = (PropBlock.Sculpt) s.getBlock();
		int[] c = l.cells.get(s.getValue(b.piece));
		int q = quarter(s.getValue(PropBlock.FACING));
		BlockPos zero = at(BlockPos.ZERO, l, q, c[0], c[1], c[2]);
		return pos.subtract(zero);
	}

	public static boolean isLit(BlockState s) {
		return s.is(SculptBlocks.COLD_FORGE_LIT.get());
	}

	private static boolean isDead(BlockState s) {
		return s.is(SculptBlocks.COLD_FORGE.get());
	}

	/** The altar the work lies on, if `pos` is a piece of the woken forge. */
	static BlockPos altar(Level level, BlockPos pos) {
		BlockState s = level.getBlockState(pos);
		if (!isLit(s)) return null;
		return at(corner(s, pos), lit, quarter(s.getValue(PropBlock.FACING)), 4, 0, 0);
	}

	// ---------------------------------------------------------------- touching it

	private static void say(ServerPlayer p, String line) {
		p.displayClientMessage(Component.literal(line).withStyle(ChatFormatting.GRAY, ChatFormatting.ITALIC), true);
	}

	private static void onClick(PlayerInteractEvent.RightClickBlock e) {
		BlockState s = e.getLevel().getBlockState(e.getPos());
		if (!isDead(s) && !isLit(s)) return;
		e.setCanceled(true);
		e.setCancellationResult(InteractionResult.sidedSuccess(e.getLevel().isClientSide));
		if (!(e.getEntity() instanceof ServerPlayer p) || e.getHand() != net.minecraft.world.InteractionHand.MAIN_HAND) return;
		if (isLit(s)) {
			if (!Coins.flag(p, "cold_lit")) {                  // woken by someone else while you were away
				Coins.setFlag(p, "cold_lit");
				Story.mark(p, "cold/lit");
			}
			BlockPos work = altar(p.level(), e.getPos());
			if (Coins.flag(p, "cold_proved")) {
				if (!Smithing.join(p, work)) {
					Bag.show(p);
					PacketDistributor.sendToPlayer(p, new Net.ForgeOpen(e.getPos()));
				}
			} else say(p, Coins.flag(p, "cold_brand") ? "The hands wait. The Kiln-Father won't fit down here: take the Brand to Veyra in the guild hall."
					: "The fire burns, the hands don't move. It wants something of you first. Ask Wendel.");
			return;
		}
		if (p.getMainHandItem().is(EMBER.get())) {
			wake(p, s, e.getPos());
			return;
		}
		if (!Coins.flag(p, "cold_told")) {
			say(p, "Cold stone. Older than the walls around it.");
			return;
		}
		if (!Coins.flag(p, "cold_seen")) {
			Coins.setFlag(p, "cold_seen");
			Story.mark(p, "cold/seen");
			p.level().playSound(null, e.getPos(), SoundEvents.BASALT_BREAK, SoundSource.BLOCKS, 1f, 0.5f);
			say(p, "Ash runs out of the runes at your touch. Nothing else stirs. Wendel should hear of this.");
			return;
		}
		say(p, Coins.flag(p, "cold_hunt") ? "It waits for its Ember." : "Nothing stirs. Wendel should hear of this.");
	}

	// ---------------------------------------------------------------- the quest's steps

	/** A boss of the gates falls with you there: the shard it carries, if you're after them. */
	static void bossDown(ServerPlayer p, Gear.Dungeon d) {
		Story.mark(p, "story/first_gate");
		Story.mark(p, "story/gate_" + Character.toLowerCase(d.rank()));
		if (!Coins.flag(p, "cold_hunt") || SHARD_RANKS.indexOf(d.rank()) < 0) return;
		String flag = "ember_" + Character.toLowerCase(d.rank());
		if (Coins.flag(p, flag)) return;
		Coins.setFlag(p, flag);
		Story.mark(p, "cold/shard_" + Character.toLowerCase(d.rank()));
		ItemStack s = new ItemStack(SHARD.get());
		if (!p.getInventory().add(s)) p.drop(s, false);
		p.sendSystemMessage(Component.literal("A shard of old fire falls out of what's left of it. ").withStyle(ChatFormatting.GOLD)
				.append(Component.literal("Ember Shard").withStyle(ChatFormatting.BOLD)));
		p.level().playSound(null, p.blockPosition(), SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.PLAYERS, 1f, 0.6f);
	}

	static boolean shardsReady(ServerPlayer p) {
		return GateForge.carried(p, SHARD.get()) >= SHARD_RANKS.length();
	}

	/** Wendel binds the three shards. */
	static void bind(ServerPlayer p) {
		if (!shardsReady(p)) return;
		int n = SHARD_RANKS.length();
		for (ItemStack s : p.getInventory().items) {
			if (n > 0 && s.is(SHARD.get())) {
				int k = Math.min(n, s.getCount());
				s.shrink(k);
				n -= k;
			}
		}
		ItemStack e = new ItemStack(EMBER.get());
		if (!p.getInventory().add(e)) p.drop(e, false);
		Coins.setFlag(p, "cold_ember");
		Story.mark(p, "cold/ember");
		p.level().playSound(null, p.blockPosition(), SoundEvents.BLAZE_SHOOT, SoundSource.PLAYERS, 0.8f, 0.6f);
	}

	static void giveBrand(ServerPlayer p) {
		ItemStack b = new ItemStack(BRAND.get());
		if (!p.getInventory().add(b)) p.drop(b, false);
		Coins.setFlag(p, "cold_brand");
		Story.mark(p, "cold/brand");
	}

	// ---------------------------------------------------------------- waking

	private static final class Waking {
		final ServerLevel level;
		final BlockPos corner;
		final Direction facing;
		final List<ServerPlayer> there;
		int t;

		Waking(ServerLevel level, BlockPos corner, Direction facing, List<ServerPlayer> there) {
			this.level = level;
			this.corner = corner;
			this.facing = facing;
			this.there = there;
		}
	}

	private static final List<Waking> WAKING = new ArrayList<>();

	private static void wake(ServerPlayer p, BlockState s, BlockPos pos) {
		ServerLevel level = p.serverLevel();
		BlockPos c = corner(s, pos);
		Direction f = s.getValue(PropBlock.FACING);
		for (Waking w : WAKING) if (w.corner.equals(c)) return;
		p.getMainHandItem().shrink(1);
		BlockPos centre = at(c, dead, quarter(f), 4, 2, 3);
		List<ServerPlayer> there = level.getEntitiesOfClass(ServerPlayer.class, new net.minecraft.world.phys.AABB(centre).inflate(32), o -> !o.isSpectator());
		Net.ColdWake m = new Net.ColdWake(centre, f.toYRot(), WAKE_ENDS, SWAP_AT);
		for (ServerPlayer o : there) PacketDistributor.sendToPlayer(o, m);
		WAKING.add(new Waking(level, c, f, there));
	}

	private static void swap(Waking w) {
		int q = quarter(w.facing);
		for (int[] c : dead.pieces) {
			BlockPos b = at(w.corner, dead, q, c[0], c[1], c[2]);
			if (isDead(w.level.getBlockState(b))) w.level.setBlock(b, Blocks.AIR.defaultBlockState(), Block.UPDATE_CLIENTS);
		}
		PropBlock.Sculpt block = (PropBlock.Sculpt) SculptBlocks.COLD_FORGE_LIT.get();
		for (int[] c : lit.pieces) {
			BlockState st = block.defaultBlockState().setValue(PropBlock.FACING, w.facing).setValue(block.piece, c[3]);
			w.level.setBlock(at(w.corner, lit, q, c[0], c[1], c[2]), st, Block.UPDATE_CLIENTS);
		}
	}

	private static void tick(ServerTickEvent.Post e) {
		if (WAKING.isEmpty()) return;
		for (var it = WAKING.iterator(); it.hasNext();) {
			Waking w = it.next();
			if (++w.t == SWAP_AT) {
				swap(w);
				for (ServerPlayer o : w.there) {
					Coins.setFlag(o, "cold_lit");
					Story.mark(o, "cold/lit");
				}
			}
			if (w.t >= WAKE_ENDS) it.remove();
		}
	}
}
