package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import javax.annotation.Nullable;

import com.mojang.brigadier.arguments.IntegerArgumentType;

import net.minecraft.ChatFormatting;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.entity.EntityJoinLevelEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredItem;

/**
 * Meteor falls (tools/blender/meteor_fall.py is the look): when a gate breaks somewhere, pieces of its crystal ring fall
 * as meteors. Now and then, for a party out in the wilds, a gate-shard (MeteorShard) comes down out of the sky ahead of
 * them: a fireball with a burning trail going to smoke. It hits 70 to 130 blocks off and blows out a crater (scorched
 * earth, the middle glassed and cracked with heat, trees round it burnt bare), and stands leaning in it, smoke climbing
 * off it for all to see. Come close and it wakes: its gate's monsters crawl out of the cracks every 20 seconds while
 * you break its three veins, each one going with a heat pulse round it (step back). The last one and it bursts: coins
 * and GP to everyone there and their own loot falling round them (finds, the gate's mats, now and then a weapon, and
 * Shardglass). Nobody comes for 20 minutes and it goes dark and crumbles. The crater stays: its glassed ground mines
 * for Shardglass. It never lands in a town, on water, or where anything has been built.
 */
final class Meteors {
	private Meteors() {}

	static final String TAG = "ashbound_meteor";
	/** the first 30 to 45 minutes out, then every 40 to 80 */
	private static final int FIRST = 36000, FIRST_MORE = 18000, EVERY = 48000, MORE = 48000, RETRY = 3600;
	/** it lands this far ahead of you */
	static final int NEAR = 70, FAR = 130;
	/** it wakes when someone comes this close; goes dark this long after landing if nobody does; crumbles after EMPTY with nobody within FAR_GONE */
	static final int WAKE = 22, COOL = 24000, EMPTY = 3000, FAR_GONE = 200;
	/** monsters out of the cracks every WAVE; a heat pulse PULSE after a vein breaks, hitting whoever is within HEAT */
	static final int WAVE = 400, PULSE = 30, HEAT = 7;
	private static final String RANKS = "FEDCBAS";
	private static final Map<Object, Long> NEXT = new HashMap<>();
	static final Map<UUID, Fall> LIVE = new HashMap<>();

	// ---------------------------------------------------------------- the crater's blocks and the Shardglass

	static final DeferredBlock<Block> GLASSED = block("glassed_ground", Block::new, BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_BLACK)
			.strength(2.5f, 6f).requiresCorrectToolForDrops().sound(SoundType.AMETHYST).lightLevel(s -> 7).emissiveRendering((s, g, p) -> true));
	static final DeferredBlock<Block> SCORCHED = block("scorched_earth", Block::new, BlockBehaviour.Properties.ofFullCopy(Blocks.COARSE_DIRT).mapColor(MapColor.COLOR_BLACK));
	static final DeferredBlock<Block> CHARRED = block("charred_log", RotatedPillarBlock::new, BlockBehaviour.Properties.ofFullCopy(Blocks.OAK_LOG).mapColor(MapColor.COLOR_BLACK));
	public static final DeferredItem<Item> SHARDGLASS = Weapons.ITEMS.registerItem("shardglass", p -> new Item(p.rarity(Rarity.RARE).fireResistant()) {
		@Override
		public void appendHoverText(ItemStack st, Item.TooltipContext ctx, List<Component> lines, net.minecraft.world.item.TooltipFlag f) {
			lines.add(Component.translatable("item.ashbound.shardglass.desc").withStyle(ChatFormatting.GRAY, ChatFormatting.ITALIC));
		}
	});

	private static DeferredBlock<Block> block(String name, java.util.function.Function<BlockBehaviour.Properties, ? extends Block> make, BlockBehaviour.Properties props) {
		DeferredBlock<Block> b = WorldBlocks.BLOCKS.registerBlock(name, make::apply, props);
		WorldBlocks.ITEMS.add(Weapons.ITEMS.registerSimpleBlockItem(b));
		return b;
	}

	/** One coming down or standing in its crater: who it's for, what comes out of it, how it's going. */
	static final class Fall {
		final int rank, players;
		@Nullable
		final Object group;
		@Nullable
		final Gear.Dungeon dungeon;
		final List<String> monsters;
		final List<UUID> mobs = new ArrayList<>();
		long landed, lastNear, nextWave, pulseAt = -1;
		int radius;
		boolean won;

		Fall(int rank, int players, @Nullable Object group, @Nullable Gear.Dungeon dungeon) {
			this.rank = rank;
			this.players = Math.max(1, players);
			this.group = group;
			this.dungeon = dungeon;
			this.monsters = dungeon == null ? List.of() : dungeon.mobs();
		}
	}

	// ---------------------------------------------------------------- it comes down

	@Nullable
	static MeteorShard open(ServerLevel l, BlockPos ground, int rank, int players, @Nullable Object group, RandomSource r) {
		MeteorShard s = Gates.METEOR.get().create(l);
		if (s == null) return null;
		rank = Mth.clamp(rank, 0, 6);
		double a = r.nextDouble() * Math.PI * 2;
		Vec3 from = new Vec3(Math.cos(a) * (150 + r.nextInt(50)), 170 + r.nextInt(40), Math.sin(a) * (150 + r.nextInt(50)));
		s.moveTo(ground.getX() + 0.5, ground.getY(), ground.getZ() + 0.5, r.nextFloat() * 360f, 0);
		s.setUp(r.nextInt(), rank, from, l.getGameTime());
		s.addTag(TAG);
		Fall f = new Fall(rank, players, group, Adventurers.any(Adventurers.dungeons(RANKS.charAt(rank)), r));
		f.radius = 8 + rank / 2;
		f.lastNear = l.getGameTime();
		if (!l.addFreshEntity(s)) return null;
		s.fall = s.getUUID();
		LIVE.put(s.getUUID(), f);
		for (ServerPlayer p : near(l, s.position(), 600))
			p.displayClientMessage(Component.literal("A gate-shard falls from the sky, " + dir(p, s.position()) + "!").withStyle(ChatFormatting.LIGHT_PURPLE, ChatFormatting.BOLD), true);
		return s;
	}

	static void tick(ServerLevel l, MeteorShard s) {
		Fall f = LIVE.get(s.fall);
		long now = l.getGameTime();
		RandomSource r = l.getRandom();
		switch (s.phase()) {
			case MeteorShard.FALLING -> {
				long age = now - s.start();
				if (age % 25 == 0) {
					// the roar of it coming, heard from where the head is
					Vec3 h = s.position().add(s.head(0));
					l.playSound(null, h.x, h.y, h.z, SoundEvents.BLAZE_SHOOT, SoundSource.HOSTILE, 14f, 0.3f + age / (float) MeteorShard.FALL * 0.3f);
					l.playSound(null, h.x, h.y, h.z, SoundEvents.FIRECHARGE_USE, SoundSource.HOSTILE, 12f, 0.4f);
				}
				if (age == MeteorShard.FALL - 20) sound(l, s.position(), SoundEvents.WARDEN_SONIC_BOOM, 10f, 0.4f);
				if (age >= MeteorShard.FALL) land(l, s, f, r);
			}
			case MeteorShard.LANDED -> {
				if (!near(l, s.position(), FAR_GONE).isEmpty()) f.lastNear = now;
				for (ServerPlayer p : near(l, s.position(), WAKE))
					if (!p.isCreative()) {
						wake(l, s);
						return;
					}
				if (now - f.landed > COOL) goDark(l, s, "The gate-shard's light goes out.");
				else if (now % 80 == 0) sound(l, s.position(), SoundEvents.AMETHYST_BLOCK_RESONATE, 3f, 0.5f);
			}
			case MeteorShard.AWAKE -> {
				if (!near(l, s.position(), FAR_GONE).isEmpty()) f.lastNear = now;
				if (now - f.lastNear > EMPTY) {
					goDark(l, s, "Left alone, the gate-shard goes dark. What came out of it stays.");
					return;
				}
				if (f.pulseAt > 0 && now >= f.pulseAt) {
					f.pulseAt = -1;
					pulse(l, s, f);
				}
				if (now >= f.nextWave) {
					wave(l, s, f, r);
					f.nextWave = now + WAVE;
				}
				if (now % 60 == 0) sound(l, s.position(), SoundEvents.BEACON_AMBIENT, 3f, 0.5f);
			}
			case MeteorShard.SHATTER -> {
				if (now - s.phaseAt >= MeteorShard.BURST) finish(l, s, f, r);
			}
			default -> {
				if (now - s.phaseAt > 60) {
					LIVE.remove(s.fall);
					s.discard();
				}
			}
		}
	}

	/** It hits: the crater, the blast, the shard left standing in the middle with smoke climbing off it. */
	static void land(ServerLevel l, MeteorShard s, Fall f, RandomSource r) {
		BlockPos at = s.blockPosition();
		int floor = crater(l, at, f.radius, r);
		s.moveTo(s.getX(), floor, s.getZ(), s.getYRot(), 0);
		s.phase(MeteorShard.LANDED);
		s.veins(3, veinHp(f));
		f.landed = l.getGameTime();
		f.lastNear = f.landed;
		Vec3 m = s.position();
		for (ServerPlayer p : near(l, m, 400)) {
			l.sendParticles(p, ParticleTypes.EXPLOSION_EMITTER, true, m.x, m.y + 2, m.z, 3, 2, 1, 2, 0);
			l.sendParticles(p, ParticleTypes.LAVA, true, m.x, m.y + 1, m.z, 80, f.radius * 0.5, 1, f.radius * 0.5, 0.5);
			l.sendParticles(p, ParticleTypes.CAMPFIRE_SIGNAL_SMOKE, true, m.x, m.y + 2, m.z, 40, f.radius * 0.4, 1, f.radius * 0.4, 0.06);
			if (p.distanceToSqr(m) < 600 * 600)
				p.displayClientMessage(Component.literal("The gate-shard hits the ground, " + dir(p, m) + "! Smoke climbs off it.").withStyle(ChatFormatting.LIGHT_PURPLE), true);
		}
		sound(l, m, SoundEvents.GENERIC_EXPLODE.value(), 18f, 0.45f);
		sound(l, m, SoundEvents.LIGHTNING_BOLT_THUNDER, 16f, 0.5f);
		sound(l, m, SoundEvents.AMETHYST_CLUSTER_BREAK, 8f, 0.4f);
		// the blast: whoever is close is thrown back and singed
		for (Player p : l.getEntitiesOfClass(Player.class, s.getBoundingBox().inflate(f.radius * 2.2))) {
			if (p.isSpectator() || p.isCreative()) continue;
			Vec3 away = p.position().subtract(m);
			double d = away.length();
			away = away.normalize().scale(1.6 * (1 - d / (f.radius * 2.2)) + 0.3);
			p.push(away.x, 0.6, away.z);
			p.hurtMarked = true;
			if (d < f.radius + 2) p.hurt(l.damageSources().explosion(s, s), 3 + 2 * f.rank);
		}
	}

	static float veinHp(Fall f) {
		return (float) (55 * (1 + f.rank) * Math.sqrt(f.players));
	}

	/** Someone's come close (or struck it): it wakes, and its gate's monsters start crawling out. */
	static void wake(ServerLevel l, MeteorShard s) {
		Fall f = LIVE.get(s.fall);
		if (f == null || s.phase() != MeteorShard.LANDED) return;
		s.phase(MeteorShard.AWAKE);
		f.nextWave = l.getGameTime() + 20;
		sound(l, s.position(), SoundEvents.BEACON_ACTIVATE, 6f, 0.4f);
		sound(l, s.position(), SoundEvents.WARDEN_EMERGE, 4f, 0.6f);
		for (ServerPlayer p : near(l, s.position(), 96))
			p.sendSystemMessage(Component.literal("The gate-shard wakes! Its gate's monsters crawl out of the cracks. Break its three veins.")
					.withStyle(ChatFormatting.LIGHT_PURPLE));
	}

	/** Out of the cracks round it: its gate's monsters. */
	static void wave(ServerLevel l, MeteorShard s, Fall f, RandomSource r) {
		if (f.monsters.isEmpty()) return;
		f.mobs.removeIf(u -> !(l.getEntity(u) instanceof Mob m) || !m.isAlive());
		int most = 6 + 2 * f.players;
		int count = Math.min(most - f.mobs.size(), 2 + (f.players > 2 ? 1 : 0) + f.rank / 3);
		for (int i = 0; i < count; i++) {
			Mob m = Encounters.monster(l, Adventurers.any(f.monsters, r), s.blockPosition(), 4 + f.radius * 0.4, r);
			if (m == null) continue;
			m.addTag(TAG);
			if (!l.addFreshEntity(m)) continue;
			f.mobs.add(m.getUUID());
			l.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, SCORCHED.get().defaultBlockState()), m.getX(), m.getY() + 0.3, m.getZ(), 16, 0.5, 0.2, 0.5, 0.1);
			Player p = l.getNearestPlayer(m.getX(), m.getY(), m.getZ(), 64, false);
			if (p != null && !p.isCreative()) m.setTarget(p);
		}
		if (count > 0) sound(l, s.position(), SoundEvents.ROOTED_DIRT_BREAK, 3f, 0.5f);
	}

	/** One of its veins broken (MeteorShard.hurt): the next one, a heat pulse coming; the last, and it bursts. */
	static void veinBroken(ServerLevel l, MeteorShard s) {
		Fall f = LIVE.get(s.fall);
		if (f == null || f.won) return;
		int left = s.veins() - 1;
		Vec3 m = s.position();
		l.sendParticles(ParticleTypes.END_ROD, m.x, m.y + 3, m.z, 40, 1, 1.5, 1, 0.25);
		sound(l, m, SoundEvents.AMETHYST_CLUSTER_BREAK, 4f, 0.5f);
		if (left <= 0) {
			s.veins(0, 0);
			s.phase(MeteorShard.SHATTER);
			f.won = true;
			sound(l, m, SoundEvents.BEACON_DEACTIVATE, 6f, 0.4f);
			return;
		}
		s.veins(left, veinHp(f));
		f.pulseAt = l.getGameTime() + PULSE;
		sound(l, m, SoundEvents.RESPAWN_ANCHOR_CHARGE, 4f, 0.5f);
		for (ServerPlayer p : near(l, m, 64))
			p.displayClientMessage(Component.literal("A vein breaks! The shard heats up, step back! " + left + " left.").withStyle(ChatFormatting.GOLD), true);
	}

	/** The heat it lets go when a vein breaks: a ring of fire out to HEAT, hurting and throwing whoever is in it. */
	static void pulse(ServerLevel l, MeteorShard s, Fall f) {
		Vec3 m = s.position();
		for (int i = 0; i < 48; i++) {
			double a = i / 48.0 * Math.PI * 2;
			l.sendParticles(ParticleTypes.FLAME, m.x + Math.cos(a) * HEAT * 0.6, m.y + 0.6, m.z + Math.sin(a) * HEAT * 0.6, 3, 0.4, 0.2, 0.4, 0.08);
		}
		l.sendParticles(ParticleTypes.LAVA, m.x, m.y + 1, m.z, 30, HEAT * 0.4, 0.5, HEAT * 0.4, 0.3);
		sound(l, m, SoundEvents.GENERIC_EXPLODE.value(), 3f, 0.8f);
		sound(l, m, SoundEvents.BLAZE_SHOOT, 4f, 0.5f);
		for (Player p : l.getEntitiesOfClass(Player.class, s.getBoundingBox().inflate(HEAT))) {
			if (p.isSpectator() || p.isCreative() || p.distanceToSqr(m) > HEAT * HEAT) continue;
			Vec3 away = p.position().subtract(m).normalize().scale(1.1);
			p.push(away.x, 0.45, away.z);
			p.hurtMarked = true;
			p.hurt(l.damageSources().magic(), 4 + 3 * f.rank);
			p.igniteForSeconds(2);
		}
	}

	/** It bursts: everyone there paid like a gate run of its rank, twice over, and their own loot falling round them. */
	static void finish(ServerLevel l, MeteorShard s, Fall f, RandomSource r) {
		Vec3 m = s.position();
		l.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, Blocks.AMETHYST_BLOCK.defaultBlockState()), m.x, m.y + 3, m.z, 120, 1.5, 2.5, 1.5, 0.3);
		l.sendParticles(ParticleTypes.END_ROD, m.x, m.y + 3, m.z, 80, 1, 2, 1, 0.4);
		l.sendParticles(ParticleTypes.EXPLOSION, m.x, m.y + 2, m.z, 6, 1.5, 1.5, 1.5, 0);
		sound(l, m, SoundEvents.GLASS_BREAK, 6f, 0.5f);
		sound(l, m, SoundEvents.GENERIC_EXPLODE.value(), 6f, 0.6f);
		int[] pay = Errands.pay(f.rank);
		for (ServerPlayer p : near(l, m, 64)) {
			int coins = pay[0] * 2, gp = Guild.of(p).registered() ? pay[1] * 2 : 0;
			Coins.give(p, coins);
			if (gp > 0) Guild.points(p, gp);
			List<ItemStack> share = loot(p, f, r);
			share.addAll(Chains.extra(p, "meteor"));
			String got = Dropped.rain(l, p, share, r);
			p.sendSystemMessage(Component.literal("The gate-shard bursts! Its pieces rain down around you.").withStyle(ChatFormatting.LIGHT_PURPLE, ChatFormatting.BOLD));
			p.sendSystemMessage(Component.literal("  +" + coins + " coins" + (gp > 0 ? ", +" + gp + " GP" : "") + got).withStyle(ChatFormatting.YELLOW));
		}
		for (UUID u : f.mobs) if (l.getEntity(u) instanceof Mob mob) mob.setPersistenceRequired();
		LIVE.remove(s.fall);
		s.discard();
	}

	/** One player's share: a find of their rank (half the time two), its gate's mats, once in a while a weapon, and Shardglass. */
	static List<ItemStack> loot(ServerPlayer p, Fall f, RandomSource r) {
		List<ItemStack> out = new ArrayList<>();
		out.add(new ItemStack(Ranks.find(p, r)));
		if (r.nextFloat() < 0.5f) out.add(new ItemStack(Ranks.find(p, r)));
		out.add(new ItemStack(SHARDGLASS.get(), 2 + r.nextInt(3)));
		Gear.Dungeon d = f.dungeon;
		if (d == null) return out;
		mat(out, d, 0, 2 + r.nextInt(3));
		if (r.nextFloat() < 0.5f) mat(out, d, 1, 1 + r.nextInt(2));
		if (r.nextFloat() < 0.12f) mat(out, d, 2, 1);
		if (r.nextFloat() < 0.06f) {
			List<Gear.Weapon> arms = d.weapons().stream().filter(w -> !w.boss()).toList();
			var it = arms.isEmpty() ? null : Gear.item(arms.get(r.nextInt(arms.size())).id());
			if (it != null) out.add(new ItemStack(it));
		}
		return out;
	}

	private static void mat(List<ItemStack> out, Gear.Dungeon d, int which, int n) {
		if (d.mats().length <= which) return;
		var it = Gear.item(d.mats()[which]);
		if (it != null) out.add(new ItemStack(it, n));
	}

	private static void goDark(ServerLevel l, MeteorShard s, String why) {
		Fall f = LIVE.get(s.fall);
		s.phase(MeteorShard.DARK);
		sound(l, s.position(), SoundEvents.BEACON_DEACTIVATE, 4f, 0.4f);
		for (ServerPlayer p : near(l, s.position(), FAR_GONE)) p.displayClientMessage(Component.literal(why).withStyle(ChatFormatting.GRAY), true);
		if (f != null) for (UUID u : f.mobs) if (l.getEntity(u) instanceof Mob mob) mob.setPersistenceRequired();
	}

	// ---------------------------------------------------------------- the crater

	/** What someone made: wood worked into planks, stairs, slabs, walls, fences, doors, glass, bricks, cloth, lights, paths and
	 *  fields, workstations, and anything of this mod's own builds (its crater blocks aside). */
	static boolean built(BlockState s) {
		if (s.is(SCORCHED.get()) || s.is(GLASSED.get()) || s.is(CHARRED.get())) return false;
		var id = net.minecraft.core.registries.BuiltInRegistries.BLOCK.getKey(s.getBlock());
		if (Ashbound.ID.equals(id.getNamespace())) return true;
		return s.is(BlockTags.PLANKS) || s.is(BlockTags.WOOL) || s.is(BlockTags.WOOL_CARPETS) || s.is(BlockTags.STAIRS) || s.is(BlockTags.SLABS)
				|| s.is(BlockTags.WALLS) || s.is(BlockTags.FENCES) || s.is(BlockTags.FENCE_GATES) || s.is(BlockTags.DOORS) || s.is(BlockTags.TRAPDOORS)
				|| s.is(BlockTags.BEDS) || s.is(BlockTags.BANNERS) || s.is(BlockTags.CANDLES) || s.is(BlockTags.RAILS) || s.is(BlockTags.STONE_BRICKS)
				|| s.is(BlockTags.ANVIL) || s.is(net.neoforged.neoforge.common.Tags.Blocks.GLASS_BLOCKS) || s.is(net.neoforged.neoforge.common.Tags.Blocks.GLASS_PANES)
				|| s.is(Blocks.BRICKS) || s.is(Blocks.TORCH) || s.is(Blocks.WALL_TORCH) || s.is(Blocks.LANTERN) || s.is(Blocks.SOUL_LANTERN)
				|| s.is(Blocks.COBBLESTONE) || s.is(Blocks.SMOOTH_STONE) || s.is(Blocks.HAY_BLOCK) || s.is(Blocks.DIRT_PATH) || s.is(Blocks.FARMLAND)
				|| s.is(Blocks.CRAFTING_TABLE) || s.is(Blocks.LADDER) || s.is(Blocks.SCAFFOLDING) || s.is(BlockTags.SIGNS) || s.is(BlockTags.ALL_HANGING_SIGNS);
	}

	/** What a fall may blast: the land and what grows on it, never anything built, never a fluid or bedrock. */
	static boolean natural(BlockState s) {
		return s.isAir() || (!built(s) && !s.hasBlockEntity() && s.getFluidState().isEmpty() && s.getBlock().defaultDestroyTime() >= 0 && !s.is(Blocks.BEDROCK));
	}

	/** Is this ground fit for one: dry, nothing built and no chests or the like within reach. */
	static boolean fits(ServerLevel l, BlockPos at, int radius) {
		return unfit(l, at, radius) == null;
	}

	/** Why it isn't (null if it is). */
	@Nullable
	static String unfit(ServerLevel l, BlockPos at, int radius) {
		int reach = (int) Math.ceil(radius * 2.4);
		for (int dx = -reach; dx <= reach; dx += 2)
			for (int dz = -reach; dz <= reach; dz += 2) {
				if (dx * dx + dz * dz > reach * reach) continue;
				BlockPos col = at.offset(dx, 0, dz);
				if (!l.hasChunkAt(col)) return "not loaded";
				BlockPos top = l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING, col);
				BlockPos ground = l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, col);
				if (!l.getFluidState(ground.below()).isEmpty() || !l.getFluidState(ground).isEmpty()) return "water";
				for (BlockPos b : new BlockPos[] {ground.below(), ground, top.below()}) {
					BlockState bs = l.getBlockState(b);
					if (!bs.isAir() && (built(bs) || bs.hasBlockEntity()))
						return "built: " + net.minecraft.core.registries.BuiltInRegistries.BLOCK.getKey(bs.getBlock());
				}
				if (Math.abs(ground.getY() - at.getY()) > 14) return "too steep";
			}
		for (int cx = (at.getX() - reach) >> 4; cx <= (at.getX() + reach) >> 4; cx++)
			for (int cz = (at.getZ() - reach) >> 4; cz <= (at.getZ() + reach) >> 4; cz++)
				for (BlockPos b : l.getChunk(cx, cz).getBlockEntitiesPos()) {
					if (b.getY() < at.getY() - 10 || b.distSqr(at) > (reach + 2) * (reach + 2)) continue;
					BlockState bs = l.getBlockState(b);
					if (bs.is(Blocks.BEEHIVE) || bs.is(Blocks.BEE_NEST)) continue;
					return "built: " + net.minecraft.core.registries.BuiltInRegistries.BLOCK.getKey(bs.getBlock());
				}
		return null;
	}

	private static void set(ServerLevel l, BlockPos p, BlockState s) {
		if (natural(l.getBlockState(p))) l.setBlock(p, s, Block.UPDATE_CLIENTS);
	}

	/** The crater round `at` (its centre on the ground): a bowl, glassed and cracked in the middle and scorched out to a
	 *  raised rim; past the rim the ground burnt, plants gone, trees stripped to charred trunks, rock thrown out over it.
	 *  Only the land and what grows on it is touched. Returns the floor's height at the middle. */
	static int crater(ServerLevel l, BlockPos at, int radius, RandomSource r) {
		BlockState air = Blocks.AIR.defaultBlockState(), glass = GLASSED.get().defaultBlockState(), scorch = SCORCHED.get().defaultBlockState();
		int cy = at.getY() - 1, deep = Math.max(3, Math.round(5f * radius / 11f));
		int reach = (int) Math.ceil(radius * 2.4);
		for (int dx = -reach; dx <= reach; dx++)
			for (int dz = -reach; dz <= reach; dz++) {
				double d = Math.sqrt(dx * dx + dz * dz);
				if (d > reach) continue;
				BlockPos col = at.offset(dx, 0, dz);
				if (!l.hasChunkAt(col)) continue;
				int g = l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, col).getY() - 1;
				if (d < radius) {
					int fl = cy - (int) Math.round(deep * (1 - (d / radius) * (d / radius)));
					for (int y = fl + 1; y <= Math.max(g, fl) + 14; y++) set(l, col.atY(y), air);
					boolean glassed = d < radius * 0.42 || (d < radius * 0.7 && r.nextFloat() < 0.3f);
					for (int y = Math.max(fl - 6, Math.min(g, fl - 1)); y <= fl; y++) set(l, col.atY(y), y == fl && glassed ? glass : scorch);
				} else if (d < radius + 3) {
					int up = (int) Math.round(Math.max(0, 2.2 - Math.abs(d - (radius + 1.2)) * 1.1));
					for (int y = g + 1; y <= g + 16; y++) set(l, col.atY(y), air);
					for (int y = g - 1; y <= g + up; y++) set(l, col.atY(y), scorch);
				} else {
					double burn = 0.9 - (d - radius - 3) / (reach - radius - 3) * 0.8;
					if (r.nextFloat() < burn) {
						BlockState top = l.getBlockState(col.atY(g));
						if (top.is(BlockTags.DIRT) || top.is(BlockTags.SAND) || top.is(Blocks.SNOW_BLOCK)) set(l, col.atY(g), scorch);
					}
					for (int y = g + 1; y <= g + 20; y++) {
						BlockPos p = col.atY(y);
						BlockState s = l.getBlockState(p);
						if (s.is(BlockTags.LEAVES)) {
							if (r.nextFloat() < burn + 0.25) l.setBlock(p, air, Block.UPDATE_CLIENTS);
						} else if (s.is(BlockTags.LOGS)) {
							if (r.nextFloat() < burn + 0.3) l.setBlock(p, CHARRED.get().defaultBlockState()
									.setValue(RotatedPillarBlock.AXIS, s.hasProperty(RotatedPillarBlock.AXIS) ? s.getValue(RotatedPillarBlock.AXIS) : net.minecraft.core.Direction.Axis.Y), Block.UPDATE_CLIENTS);
						} else if (!s.isAir() && s.canBeReplaced() && s.getFluidState().isEmpty() && r.nextFloat() < burn + 0.2) l.setBlock(p, air, Block.UPDATE_CLIENTS);
					}
				}
			}
		// rock thrown out over the land round it
		for (int i = 0; i < radius * 6; i++) {
			double a = r.nextDouble() * Math.PI * 2, d = radius + 2 + Math.abs(r.nextGaussian()) * radius * 0.6;
			BlockPos col = at.offset((int) Math.round(Math.cos(a) * d), 0, (int) Math.round(Math.sin(a) * d));
			if (!l.hasChunkAt(col)) continue;
			BlockPos top = l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, col);
			if (l.getBlockState(top).isAir() && natural(l.getBlockState(top.below())) && l.getFluidState(top.below()).isEmpty())
				l.setBlock(top, r.nextFloat() < 0.1f ? glass : scorch, Block.UPDATE_CLIENTS);
		}
		return cy - deep + 1;
	}

	// ---------------------------------------------------------------- helpers, when and where

	private static String dir(ServerPlayer p, Vec3 at) {
		double dx = at.x - p.getX(), dz = at.z - p.getZ();
		String[] dirs = {"east", "south-east", "south", "south-west", "west", "north-west", "north", "north-east"};
		return "to the " + dirs[Math.floorMod((int) Math.round(Math.atan2(dz, dx) / (Math.PI / 4)), 8)];
	}

	private static void sound(ServerLevel l, Vec3 m, SoundEvent s, float volume, float pitch) {
		l.playSound(null, m.x, m.y, m.z, s, SoundSource.HOSTILE, volume, pitch);
	}

	static List<ServerPlayer> near(ServerLevel l, Vec3 m, double reach) {
		List<ServerPlayer> out = new ArrayList<>();
		for (ServerPlayer p : l.players()) if (!p.isSpectator() && p.position().distanceToSqr(m) < reach * reach) out.add(p);
		return out;
	}

	/** Ahead of whoever it's for, where they'll see it come down: 70 to 130 blocks off, on dry natural ground, outside any town. */
	/** why the last spot() found nothing, for the command */
	static String lastWhy = "";

	@Nullable
	static BlockPos spot(ServerLevel l, ServerPlayer p, int radius, RandomSource r) {
		Map<String, Integer> why = new HashMap<>();
		for (int k = 0; k < 16; k++) {
			double a = Math.toRadians(p.getYRot() + 90 + (r.nextDouble() - 0.5) * 120), d = NEAR + r.nextDouble() * (FAR - NEAR);
			BlockPos col = BlockPos.containing(p.getX() + Math.cos(a) * d, 0, p.getZ() + Math.sin(a) * d);
			if (!l.hasChunkAt(col)) continue;
			BlockPos top = l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, col);
			String no = Adventurers.town(top) != null ? "in a town" : unfit(l, top, radius);
			if (no != null) {
				why.merge(no, 1, Integer::sum);
				continue;
			}
			return top;
		}
		lastWhy = why.entrySet().stream().sorted((a, b) -> b.getValue() - a.getValue()).map(e -> e.getKey() + " x" + e.getValue()).limit(3)
				.reduce((a, b) -> a + ", " + b).orElse("nothing loaded ahead");
		return null;
	}

	private static void spawner(ServerTickEvent.Post e) {
		var server = e.getServer();
		if (server.getTickCount() % 200 != 100) return;
		ServerLevel l = server.overworld();
		RandomSource r = l.getRandom();
		long now = l.getGameTime();
		Map<Object, List<ServerPlayer>> groups = new java.util.LinkedHashMap<>();
		for (ServerPlayer p : l.players()) if (!p.isSpectator()) groups.computeIfAbsent(com.snoringwalrus.ashbound.Party.fightKey(p), x -> new ArrayList<>()).add(p);
		for (var g : groups.entrySet()) {
			Object key = g.getKey();
			Long next = NEXT.get(key);
			if (next == null) {
				NEXT.put(key, now + FIRST + r.nextInt(FIRST_MORE));
				continue;
			}
			if (now < next || LIVE.values().stream().anyMatch(k -> key.equals(k.group)) || SkyCracks.LIVE.values().stream().anyMatch(k -> key.equals(k.group))) continue;
			ServerPlayer p = g.getValue().get(r.nextInt(g.getValue().size()));
			if (Adventurers.town(p.blockPosition()) != null || p.getY() < l.getSeaLevel() - 10 || !l.canSeeSky(p.blockPosition())) {
				NEXT.put(key, now + RETRY);
				continue;
			}
			int rank = Ranks.party(p);
			int with = (int) g.getValue().stream().filter(o -> o.distanceTo(p) < 64).count();
			BlockPos at = spot(l, p, 8 + Math.min(6, rank) / 2, r);
			MeteorShard s = at == null ? null : open(l, at, rank, with, key, r);
			NEXT.put(key, now + (s == null ? RETRY : EVERY + r.nextInt(MORE)));
		}
	}

	/** Nothing of one outlives the session it was in (its crater does). */
	private static void join(EntityJoinLevelEvent e) {
		if (e.loadedFromDisk() && e.getEntity() instanceof MeteorShard) e.setCanceled(true);
	}

	private static void commands(RegisterCommandsEvent e) {
		e.getDispatcher().register(Commands.literal("ashbound").requires(s -> s.hasPermission(2)).then(Commands.literal("meteor")
				.executes(c -> make(c.getSource().getPlayerOrException(), -1))
				.then(Commands.literal("win").executes(c -> winNearest(c.getSource().getPlayerOrException())))
				.then(Commands.argument("rank", IntegerArgumentType.integer(0, 6)).executes(c -> make(c.getSource().getPlayerOrException(), IntegerArgumentType.getInteger(c, "rank"))))));
	}

	/** `/ashbound meteor win`: the nearest shard burst on the spot, as if its veins were all broken. */
	private static int winNearest(ServerPlayer p) {
		ServerLevel l = p.serverLevel();
		MeteorShard best = null;
		for (var e : LIVE.entrySet())
			if (!e.getValue().won && l.getEntity(e.getKey()) instanceof MeteorShard s && s.phase() != MeteorShard.FALLING && s.phase() != MeteorShard.DARK
					&& (best == null || s.distanceToSqr(p) < best.distanceToSqr(p))) best = s;
		if (best == null) {
			p.sendSystemMessage(Component.literal("No gate-shard standing here"));
			return 0;
		}
		Fall f = LIVE.get(best.fall);
		for (UUID u : f.mobs) if (l.getEntity(u) instanceof Mob m) m.kill();
		f.mobs.clear();
		f.won = true;
		finish(l, best, f, l.getRandom());
		return 1;
	}

	private static int make(ServerPlayer p, int rank) {
		int rk = rank < 0 ? Ranks.party(p) : rank;
		BlockPos at = spot(p.serverLevel(), p, 8 + Math.min(6, rk) / 2, p.getRandom());
		if (at == null) {
			p.sendSystemMessage(Component.literal("No open ground ahead for a gate-shard (" + lastWhy + ")"));
			return 0;
		}
		return open(p.serverLevel(), at, rk, 1, com.snoringwalrus.ashbound.Party.fightKey(p), p.getRandom()) == null ? 0 : 1;
	}

	static void init() {
		NeoForge.EVENT_BUS.addListener(Meteors::spawner);
		NeoForge.EVENT_BUS.addListener(Meteors::commands);
		NeoForge.EVENT_BUS.addListener(Meteors::join);
	}
}
