package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

import javax.annotation.Nullable;

import net.minecraft.ChatFormatting;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtUtils;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.network.Filterable;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.BiomeTags;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.MapItem;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.item.component.ItemLore;
import net.minecraft.world.item.component.WrittenBookContent;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.ChestBlock;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.level.saveddata.maps.MapDecorationTypes;
import net.minecraft.world.level.saveddata.maps.MapItemSavedData;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;
import net.neoforged.neoforge.event.level.BlockEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;

/**
 * A fallen party's stash (Encounters' "fallen" scene): one of the dead carries a torn map, a real map with a red X on it, 300 to
 * 800 blocks off. It goes in the Journal and on the compass. Nothing's there until someone carrying the map comes near: then the
 * spot's marked (a dead tree, their banner at its foot, a skull on a stake) and a chest is buried two blocks under the X. Start
 * digging and what killed them comes for you: their dungeon's elite, made a bane, with a pack. While it lives the chest won't
 * give; once it's down, opening the chest showers a share over the head of everyone in the opener's party within 250 and of
 * anyone who hit the bane (Dropped.rain), the party's last pages among it; nobody else. Kept in the world's saved data (a map in someone's bag outlives the session).
 */
final class Treasure {
	private Treasure() {}

	static final String TAG = "ashbound_stash";
	/** how far the X is from where the map was found; how near someone with the map has to come for the spot to be made; how near
	 * the X a block has to be broken to wake its guard; the guard's reach that keeps the chest shut */
	static final int NEAR = 300, FAR = 800, PLACE = 56, WAKE = 7, GUARDS = 40, SHARE = 250;
	private static final ResourceLocation BANE = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "stash_bane");
	private static final String RANKS = "FEDCBAS";

	static final class Stash {
		int id, rank;
		BlockPos pos = BlockPos.ZERO;
		@Nullable
		BlockPos chest;
		String gate = "", party = "";
		boolean placed, woke, opened;
		@Nullable
		UUID guard;
		String guardName = "";
		/** whoever's hit its bane: they share in it, party or not */
		final Set<UUID> hitters = new HashSet<>();

		String giver() {
			return Errands.TREASURE + id;
		}

		CompoundTag save() {
			CompoundTag t = new CompoundTag();
			t.putInt("id", id);
			t.putInt("rank", rank);
			t.put("pos", NbtUtils.writeBlockPos(pos));
			if (chest != null) t.put("chest", NbtUtils.writeBlockPos(chest));
			t.putString("gate", gate);
			t.putString("party", party);
			t.putBoolean("placed", placed);
			t.putBoolean("woke", woke);
			t.putBoolean("opened", opened);
			if (guard != null) t.putUUID("guard", guard);
			t.putString("guard_name", guardName);
			ListTag hit = new ListTag();
			for (UUID u : hitters) hit.add(NbtUtils.createUUID(u));
			t.put("hitters", hit);
			return t;
		}

		static Stash load(CompoundTag t) {
			Stash s = new Stash();
			s.id = t.getInt("id");
			s.rank = t.getInt("rank");
			s.pos = NbtUtils.readBlockPos(t, "pos").orElse(BlockPos.ZERO);
			s.chest = NbtUtils.readBlockPos(t, "chest").orElse(null);
			s.gate = t.getString("gate");
			s.party = t.getString("party");
			s.placed = t.getBoolean("placed");
			s.woke = t.getBoolean("woke");
			s.opened = t.getBoolean("opened");
			if (t.hasUUID("guard")) s.guard = t.getUUID("guard");
			s.guardName = t.getString("guard_name");
			for (Tag u : t.getList("hitters", Tag.TAG_INT_ARRAY)) s.hitters.add(NbtUtils.loadUUID(u));
			return s;
		}
	}

	static final class State extends SavedData {
		final Map<Integer, Stash> stashes = new HashMap<>();
		int next = 1;

		@Override
		public CompoundTag save(CompoundTag tag, HolderLookup.Provider reg) {
			ListTag list = new ListTag();
			for (Stash s : stashes.values()) list.add(s.save());
			tag.put("stashes", list);
			tag.putInt("next", next);
			return tag;
		}

		static State load(CompoundTag tag, HolderLookup.Provider reg) {
			State st = new State();
			for (Tag t : tag.getList("stashes", Tag.TAG_COMPOUND)) {
				Stash s = Stash.load((CompoundTag) t);
				st.stashes.put(s.id, s);
			}
			st.next = Math.max(1, tag.getInt("next"));
			return st;
		}
	}

	static State state(ServerLevel l) {
		return l.getServer().overworld().getDataStorage().computeIfAbsent(new SavedData.Factory<>(State::new, State::load, null), "ashbound_stashes");
	}

	// ---------------------------------------------------------------- the map

	/** A torn map to a new stash near..far from `from`, for a party of this rank, whose killers were this dungeon's. */
	static ItemStack map(ServerLevel l, BlockPos from, int rank, String gate, String party, RandomSource r, int near, int far) {
		BlockPos spot = spot(l, from, near, far, r);
		State st = state(l);
		Stash s = new Stash();
		s.id = st.next++;
		s.rank = Math.max(0, Math.min(6, rank));
		s.pos = spot;
		s.gate = gate;
		s.party = party;
		st.stashes.put(s.id, s);
		st.setDirty();
		ItemStack m = MapItem.create(l, spot.getX(), spot.getZ(), (byte) 2, true, true);
		MapItem.renderBiomePreviewMap(l, m);
		MapItemSavedData.addTargetDecoration(m, spot, "+", MapDecorationTypes.RED_X);
		m.set(DataComponents.ITEM_NAME, Component.literal("Torn Map of " + AdventurerTalk.the(party, false)));
		m.set(DataComponents.LORE, new ItemLore(List.of(
				Component.literal(line("stash_scrawl", Map.of("party", AdventurerTalk.the(party, false)), r)).withStyle(ChatFormatting.GRAY, ChatFormatting.ITALIC),
				Component.literal(RANKS.charAt(s.rank) + "-rank. Dig under the X.").withStyle(ChatFormatting.DARK_GRAY))));
		CustomData.update(DataComponents.CUSTOM_DATA, m, t -> t.putInt(TAG, s.id));
		return m;
	}

	/** The stash this map leads to, if it is one of ours. */
	@Nullable
	static Stash of(ServerLevel l, ItemStack m) {
		if (!m.is(Items.FILLED_MAP)) return null;
		CustomData cd = m.get(DataComponents.CUSTOM_DATA);
		if (cd == null || !cd.contains(TAG)) return null;
		return state(l).stashes.get(cd.copyTag().getInt(TAG));
	}

	/** Out in the wild on dry land: no sea, river or beach, no town. The land isn't there yet, so its biome is asked of the world's
	 * own recipe; the ground is found when someone comes. */
	static BlockPos spot(ServerLevel l, BlockPos from, int near, int far, RandomSource r) {
		BlockPos last = from;
		for (int k = 0; k < 40; k++) {
			double a = r.nextDouble() * Math.PI * 2, d = near + r.nextDouble() * (far - near);
			BlockPos at = new BlockPos((int) Math.round(from.getX() + Math.cos(a) * d), l.getSeaLevel() + 8, (int) Math.round(from.getZ() + Math.sin(a) * d));
			last = at;
			var b = l.getBiome(at);
			if (b.is(BiomeTags.IS_OCEAN) || b.is(BiomeTags.IS_DEEP_OCEAN) || b.is(BiomeTags.IS_RIVER) || b.is(BiomeTags.IS_BEACH)) continue;
			if (Adventurers.town(at) != null) continue;
			return at;
		}
		return last;
	}

	// ---------------------------------------------------------------- the spot, made when someone comes

	private static BlockState block(String id, BlockState fallback) {
		Block b = BuiltInRegistries.BLOCK.getOptional(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, id)).orElse(null);
		return b == null ? fallback : b.defaultBlockState();
	}

	private static BlockState facing(BlockState s, Direction d) {
		return s.hasProperty(BlockStateProperties.HORIZONTAL_FACING) ? s.setValue(BlockStateProperties.HORIZONTAL_FACING, d) : s;
	}

	/** Dry ground near the X (a lake may have been drawn over): its top, the first air over solid ground. */
	private static BlockPos dry(ServerLevel l, BlockPos at) {
		for (int ring = 0; ring <= 12; ring += 2)
			for (int dx = -ring; dx <= ring; dx += 2)
				for (int dz = -ring; dz <= ring; dz += 2) {
					if (Math.max(Math.abs(dx), Math.abs(dz)) != ring) continue;
					BlockPos top = l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, at.offset(dx, 0, dz));
					if (l.getFluidState(top).isEmpty() && l.getFluidState(top.below()).isEmpty() && !l.getBlockState(top.below()).getCollisionShape(l, top.below()).isEmpty())
						return top;
				}
		return l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, at);
	}

	/** The spot, marked: a dead tree with their banner at its foot, a skull on a stake, turned earth over the X, and the chest two
	 * blocks under it. */
	static void place(ServerLevel l, Stash s, RandomSource r) {
		BlockPos top = dry(l, s.pos);
		s.pos = top;
		BlockPos ground = top.below();
		if (l.getBlockState(top).canBeReplaced()) l.setBlock(top, Blocks.AIR.defaultBlockState(), 3);
		// turned earth over it, a ring of it round about
		for (int dx = -1; dx <= 1; dx++)
			for (int dz = -1; dz <= 1; dz++) {
				BlockPos g = l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, ground.offset(dx, 0, dz)).below();
				if (Math.abs(g.getY() - ground.getY()) > 1 || !(l.getBlockState(g).is(BlockTags.DIRT) || l.getBlockState(g).is(BlockTags.SAND))) continue;
				if ((dx == 0 && dz == 0) || r.nextFloat() < 0.6f) l.setBlock(g, Blocks.COARSE_DIRT.defaultBlockState(), 3);
				if (l.getBlockState(g.above()).canBeReplaced()) l.setBlock(g.above(), Blocks.AIR.defaultBlockState(), 3);
			}
		l.setBlock(ground, Blocks.COARSE_DIRT.defaultBlockState(), 3);
		l.setBlock(ground.below(), Blocks.DIRT.defaultBlockState(), 3);
		BlockPos chest = ground.below(2);
		Direction face = Direction.Plane.HORIZONTAL.getRandomDirection(r);
		l.setBlock(chest, Blocks.CHEST.defaultBlockState().setValue(ChestBlock.FACING, face), 3);
		if (l.getBlockState(chest.below()).getCollisionShape(l, chest.below()).isEmpty()) l.setBlock(chest.below(), Blocks.DIRT.defaultBlockState(), 3);
		s.chest = chest;
		// the dead tree, a few steps off, its branches bare
		Direction off = Direction.Plane.HORIZONTAL.getRandomDirection(r);
		BlockPos foot = l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, top.relative(off, 3).relative(off.getClockWise(), r.nextInt(3) - 1));
		BlockState log = block("wildwood_log", Blocks.DARK_OAK_LOG.defaultBlockState());
		int tall = 4 + r.nextInt(3);
		for (int y = 0; y < tall; y++) {
			BlockPos p = foot.above(y);
			if (!l.getBlockState(p).canBeReplaced()) break;
			l.setBlock(p, log, 3);
		}
		for (int b = 0; b < 2; b++) {
			Direction way = b == 0 ? off.getClockWise() : off.getCounterClockWise();
			BlockPos at = foot.above(tall - 1 - b * 2);
			int reach = 1 + r.nextInt(2);
			for (int k = 1; k <= reach; k++) {
				BlockPos p = at.relative(way, k).above(k > 1 ? 1 : 0);
				if (!l.getBlockState(p).canBeReplaced()) break;
				l.setBlock(p, log.hasProperty(RotatedPillarBlock.AXIS) ? log.setValue(RotatedPillarBlock.AXIS, way.getAxis()) : log, 3);
			}
		}
		// their banner at its foot and a skull on a stake by the X, both facing it
		Direction toX = off.getOpposite();
		BlockPos banner = foot.relative(toX);
		if (l.getBlockState(banner).canBeReplaced()) l.setBlock(banner, facing(block("war_banner", Blocks.BLACK_BANNER.defaultBlockState()), toX.getOpposite()), 3);
		BlockPos stake = l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, top.relative(toX, 2).relative(toX.getClockWise(), 2));
		if (l.getBlockState(stake).canBeReplaced()) l.setBlock(stake, facing(block("hunter_stake", Blocks.SKELETON_SKULL.defaultBlockState()), toX), 3);
		s.placed = true;
		state(l).setDirty();
	}

	// ---------------------------------------------------------------- its guard, and the chest

	/** Whatever killed them was waiting by it: their dungeon's elite, a bane now, and a pack, for however many came. */
	static void wake(ServerLevel l, Stash s, ServerPlayer by) {
		if (s.woke || s.opened) return;
		s.woke = true;
		RandomSource r = l.getRandom();
		Gear.Dungeon d = Gear.of(s.gate);
		if (d == null) d = Adventurers.any(Adventurers.dungeons(RANKS.charAt(s.rank)), r);
		state(l).setDirty();
		if (d == null) return;
		int players = Math.max(1, (int) l.players().stream().filter(p -> !p.isSpectator() && p.distanceToSqr(s.pos.getX(), p.getY(), s.pos.getZ()) < 32 * 32).count());
		String rank = String.valueOf(RANKS.charAt(s.rank));
		Mob bane = Encounters.monster(l, d.elite(), s.pos, 12, r);
		if (bane != null) {
			Balance.atRank(bane, d.elite(), rank);
			var hp = bane.getAttribute(Attributes.MAX_HEALTH);
			if (hp != null) hp.addPermanentModifier(new AttributeModifier(BANE, 1.5 + 0.5 * (players - 1), AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL));
			var hit = bane.getAttribute(Attributes.ATTACK_DAMAGE);
			if (hit != null) hit.addPermanentModifier(new AttributeModifier(BANE, 0.25, AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL));
			bane.setHealth(bane.getMaxHealth());
			s.guardName = bane.getType().getDescription().getString() + ", Bane of " + AdventurerTalk.the(s.party, true);
			bane.setCustomName(Component.literal(s.guardName).withStyle(ChatFormatting.DARK_RED));
			bane.setCustomNameVisible(true);
			bane.addTag(TAG);
			if (l.addFreshEntity(bane)) {
				s.guard = bane.getUUID();
				bane.setTarget(by);
				l.playSound(null, bane.getX(), bane.getY(), bane.getZ(), SoundEvents.RAVAGER_ROAR, SoundSource.HOSTILE, 3f, 0.7f);
			}
		}
		int pack = 2 + Math.min(4, players - 1) + r.nextInt(2);
		for (int k = 0; k < pack; k++) {
			String id = d.mobs().get(r.nextInt(d.mobs().size()));
			Mob m = Encounters.monster(l, id, s.pos, 14, r);
			if (m == null) continue;
			Balance.atRank(m, id, rank);
			m.addTag(TAG);
			if (l.addFreshEntity(m)) m.setTarget(by);
		}
		String said = line("stash_wake", Map.of("party", AdventurerTalk.the(s.party, false), "bane", s.guardName), r);
		for (ServerPlayer p : l.players())
			if (p.distanceToSqr(s.pos.getX(), p.getY(), s.pos.getZ()) < 64 * 64) {
				p.sendSystemMessage(Component.literal(said).withStyle(ChatFormatting.RED));
				p.displayClientMessage(Component.literal(s.guardName + "!").withStyle(ChatFormatting.DARK_RED, ChatFormatting.BOLD), true);
			}
	}

	/** Still about and still alive: the chest won't give. */
	static boolean guarded(ServerLevel l, Stash s) {
		return s.guard != null && l.getEntity(s.guard) instanceof Mob m && m.isAlive() && m.distanceToSqr(s.pos.getX(), m.getY(), s.pos.getZ()) < GUARDS * GUARDS;
	}

	/** Dug up: the chest bursts and everyone near gets their share, falling over their heads. */
	static void open(ServerLevel l, Stash s, ServerPlayer by) {
		if (s.opened) return;
		RandomSource r = l.getRandom();
		if (!s.woke) wake(l, s, by);
		if (guarded(l, s)) {
			by.displayClientMessage(Component.literal(s.guardName + " still guards it.").withStyle(ChatFormatting.RED), true);
			return;
		}
		s.opened = true;
		state(l).setDirty();
		if (s.chest != null && l.getBlockState(s.chest).is(Blocks.CHEST)) l.removeBlock(s.chest, false);
		BlockPos at = s.chest == null ? s.pos : s.chest;
		l.playSound(null, at, SoundEvents.CHEST_OPEN, SoundSource.BLOCKS, 1.2f, 0.8f);
		l.playSound(null, at, SoundEvents.PLAYER_LEVELUP, SoundSource.PLAYERS, 0.8f, 0.7f);
		l.sendParticles(net.minecraft.core.particles.ParticleTypes.HAPPY_VILLAGER, at.getX() + 0.5, at.getY() + 1, at.getZ() + 0.5, 24, 0.6, 0.6, 0.6, 0.1);
		Gear.Dungeon d = Gear.of(s.gate);
		int[] pay = Errands.pay(s.rank);
		for (ServerPlayer p : sharers(l, s, by, at)) {
			int coins = pay[0] * 2, gp = Guild.of(p).registered() ? pay[1] * 2 : 0;
			Coins.give(p, coins);
			if (gp > 0) Guild.points(p, gp);
			List<ItemStack> share = new java.util.ArrayList<>(loot(p, s, d, r));
			share.addAll(Chains.extra(p, "treasure"));
			String got = Dropped.rain(l, p, share, r);
			p.sendSystemMessage(Component.literal("You dig out " + AdventurerTalk.the(s.party, false) + "'s stash!").withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD));
			p.sendSystemMessage(Component.literal("  +" + coins + " coins" + (gp > 0 ? ", +" + gp + " GP" : "") + got).withStyle(ChatFormatting.YELLOW));
		}
		for (ServerPlayer p : l.getServer().getPlayerList().getPlayers()) Errands.drop(p, s.giver());
	}

	/** Who gets a share: whoever opened it, their party, and anyone who hit the bane; all of them within SHARE of it, in this world. */
	static List<ServerPlayer> sharers(ServerLevel l, Stash s, ServerPlayer by, BlockPos at) {
		java.util.LinkedHashSet<ServerPlayer> who = new java.util.LinkedHashSet<>();
		who.add(by);
		who.addAll(com.snoringwalrus.ashbound.Party.others(by));
		for (UUID u : s.hitters) if (l.getServer().getPlayerList().getPlayer(u) instanceof ServerPlayer p) who.add(p);
		who.removeIf(p -> p.level() != l || p.isSpectator() || p.distanceToSqr(at.getX(), at.getY(), at.getZ()) > SHARE * SHARE);
		return new ArrayList<>(who);
	}

	/** Someone's hit a stash's bane: they're in on it. */
	private static void hit(net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent e) {
		if (!(e.getEntity().level() instanceof ServerLevel l) || !e.getEntity().getTags().contains(TAG) || !(e.getSource().getEntity() instanceof ServerPlayer p)) return;
		for (Stash s : state(l).stashes.values())
			if (!s.opened && e.getEntity().getUUID().equals(s.guard) && s.hitters.add(p.getUUID())) state(l).setDirty();
	}

	/** One player's share: finds of their rank, the killers' dungeon's mats, a good chance of a world weapon, now and then one of
	 * the dungeon's own, and the party's last pages. */
	static List<ItemStack> loot(ServerPlayer p, Stash s, @Nullable Gear.Dungeon d, RandomSource r) {
		List<ItemStack> out = new ArrayList<>();
		out.add(new ItemStack(Ranks.find(p, r)));
		out.add(new ItemStack(Ranks.find(p, r)));
		if (r.nextFloat() < 0.5f) out.add(new ItemStack(Ranks.find(p, r)));
		if (d != null) {
			mat(out, d, 0, 3 + r.nextInt(3));
			if (r.nextFloat() < 0.7f) mat(out, d, 1, 1 + r.nextInt(3));
			if (r.nextFloat() < 0.3f) mat(out, d, 2, 1);
			if (r.nextFloat() < 0.15f) {
				List<Gear.Weapon> arms = d.weapons().stream().filter(w -> !w.boss()).toList();
				var it = arms.isEmpty() ? null : Gear.item(arms.get(r.nextInt(arms.size())).id());
				if (it != null) out.add(new ItemStack(it));
			}
		}
		if (r.nextFloat() < 0.4f) {
			var it = WorldArms.pick(r, s.rank + 1);
			if (it != null) out.add(new ItemStack(it));
		}
		out.add(pages(s, d, r));
		return out;
	}

	private static void mat(List<ItemStack> out, Gear.Dungeon d, int which, int n) {
		if (d.mats().length <= which) return;
		var it = Gear.item(d.mats()[which]);
		if (it != null) out.add(new ItemStack(it, n));
	}

	/** The last pages of their diary: out, the stash, the end. */
	static ItemStack pages(Stash s, @Nullable Gear.Dungeon d, RandomSource r) {
		Map<String, String> w = new HashMap<>();
		w.put("party", AdventurerTalk.the(s.party, false));
		w.put("Party", AdventurerTalk.the(s.party, true));
		w.put("foe", s.guardName.isEmpty() ? "it" : s.guardName.substring(0, s.guardName.indexOf(',') < 0 ? s.guardName.length() : s.guardName.indexOf(',')));
		w.put("gate", d == null ? "the gate" : d.title());
		w.put("rank", String.valueOf(RANKS.charAt(s.rank)));
		List<Filterable<Component>> pages = new ArrayList<>();
		for (String k : List.of("diary_out", "diary_stash", "diary_end")) pages.add(Filterable.passThrough(Component.literal(line(k, w, r))));
		ItemStack b = new ItemStack(Items.WRITTEN_BOOK);
		b.set(DataComponents.WRITTEN_BOOK_CONTENT, new WrittenBookContent(Filterable.passThrough("Last Pages"), AdventurerTalk.the(s.party, true), 0, pages, true));
		b.set(DataComponents.CUSTOM_NAME, Component.literal(AdventurerTalk.the(s.party, true) + "' Last Pages").withStyle(ChatFormatting.GOLD));
		return b;
	}

	static String line(String key, Map<String, String> w, RandomSource r) {
		return Encounters.line(key, w, r);
	}

	// ---------------------------------------------------------------- the world

	/** players we've already put a stash in the Journal for, this session */
	private static final Set<String> TRACKED = new HashSet<>();

	/** Put in the Journal and on the compass (if there's room on their list). */
	static void track(ServerPlayer p, Stash s) {
		if (!TRACKED.add(p.getUUID() + ":" + s.id)) return;
		if (Errands.find(p, "fav:" + s.giver()) != null || Errands.full(p)) return;
		Errands.add(p, new Errands.Errand("treasure", Errands.KILL, s.giver(), 1, 0, 0, 0, s.giver(), "The map", s.pos.getX(), s.pos.getZ(), Errands.day(p),
				AdventurerTalk.the(s.party, true) + "' Stash", "Dig under the X on the torn map"));
		Story.pick(p, "fav:" + s.giver());
	}

	private static void tick(ServerTickEvent.Post e) {
		var server = e.getServer();
		if (server.getTickCount() % 20 != 7) return;
		ServerLevel l = server.overworld();
		for (ServerPlayer p : l.players()) {
			if (p.isSpectator()) continue;
			var inv = p.getInventory();
			for (int i = 0; i < inv.getContainerSize(); i++) {
				ItemStack m = inv.getItem(i);
				if (!m.is(Items.FILLED_MAP)) continue;
				Stash s = of(l, m);
				if (s == null || s.opened) continue;
				track(p, s);
				double dx = p.getX() - s.pos.getX(), dz = p.getZ() - s.pos.getZ();
				if (!s.placed && dx * dx + dz * dz < PLACE * PLACE && l.isPositionEntityTicking(s.pos)) {
					place(l, s, l.getRandom());
					p.displayClientMessage(Component.literal(line("stash_near", Map.of(), l.getRandom())).withStyle(ChatFormatting.GOLD), true);
				}
			}
		}
	}

	@Nullable
	private static Stash at(ServerLevel l, BlockPos pos, int reach) {
		for (Stash s : state(l).stashes.values()) {
			if (!s.placed || s.opened) continue;
			if (reach == 0 ? pos.equals(s.chest) : Math.abs(pos.getX() - s.pos.getX()) <= reach && Math.abs(pos.getZ() - s.pos.getZ()) <= reach && Math.abs(pos.getY() - s.pos.getY()) <= 10)
				return s;
		}
		return null;
	}

	/** Digging by the X wakes its guard; breaking the chest is opening it. */
	private static void broke(BlockEvent.BreakEvent e) {
		if (!(e.getLevel() instanceof ServerLevel l) || !(e.getPlayer() instanceof ServerPlayer p) || l.dimension() != net.minecraft.world.level.Level.OVERWORLD) return;
		Stash chest = at(l, e.getPos(), 0);
		if (chest != null) {
			e.setCanceled(true);
			open(l, chest, p);
			return;
		}
		Stash near = at(l, e.getPos(), WAKE);
		if (near != null && !near.woke) wake(l, near, p);
	}

	private static void opened(PlayerInteractEvent.RightClickBlock e) {
		if (!(e.getLevel() instanceof ServerLevel l) || !(e.getEntity() instanceof ServerPlayer p) || l.dimension() != net.minecraft.world.level.Level.OVERWORLD) return;
		Stash s = at(l, e.getPos(), 0);
		if (s == null) return;
		e.setCanceled(true);
		e.setCancellationResult(net.minecraft.world.InteractionResult.SUCCESS);
		if (e.getHand() == net.minecraft.world.InteractionHand.MAIN_HAND) open(l, s, p);
	}

	private static void commands(RegisterCommandsEvent e) {
		e.getDispatcher().register(Commands.literal("ashbound").requires(c -> c.hasPermission(2)).then(Commands.literal("treasure").executes(c -> {
			ServerPlayer p = c.getSource().getPlayerOrException();
			ServerLevel l = p.serverLevel();
			RandomSource r = p.getRandom();
			int rank = Ranks.party(p);
			Gear.Dungeon d = Adventurers.any(Adventurers.dungeons(RANKS.charAt(rank)), r);
			List<Adventurers.Party> pool = Adventurers.PARTIES.stream().filter(x -> Math.abs(RANKS.indexOf(x.rank()) - rank) <= 1).toList();
			String party = pool.isEmpty() ? "The Lost" : pool.get(r.nextInt(pool.size())).name();
			p.getInventory().placeItemBackInInventory(map(l, p.blockPosition(), rank, d == null ? "" : d.gate(), party, r, 60, 100));
			c.getSource().sendSuccess(() -> Component.literal("A torn map to a stash 60-100 blocks off"), false);
			return 1;
		})));
	}

	static void init() {
		NeoForge.EVENT_BUS.addListener(Treasure::tick);
		NeoForge.EVENT_BUS.addListener(Treasure::broke);
		NeoForge.EVENT_BUS.addListener(Treasure::opened);
		NeoForge.EVENT_BUS.addListener(Treasure::hit);
		NeoForge.EVENT_BUS.addListener(Treasure::commands);
	}
}
