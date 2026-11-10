package com.snoringwalrus.ashbound;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import net.minecraft.ChatFormatting;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.FloatTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.LongTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.saveddata.SavedData;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.entity.EntityJoinLevelEvent;
import net.neoforged.neoforge.event.entity.living.FinalizeSpawnEvent;
import net.neoforged.neoforge.event.entity.living.LivingDropsEvent;
import net.neoforged.neoforge.event.entity.player.CanPlayerSleepEvent;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.neoforged.neoforge.network.PacketDistributor;
import net.neoforged.neoforge.registries.DeferredItem;

/**
 * Ashfall Night (tools/blender/ashfall_night.py is the look): about one night in ODDS, never two running, the far
 * fire-mountain wakes and ash falls till dawn. The sky goes red and the air thick (client/AshfallSky); nobody sleeps it
 * away; the night's monsters come thicker and harder and leave more, and Cinders, which only these nights give; Legends
 * wake more readily (WorldBeasts); the towns light braziers in their streets (gone again at dawn: a light block in the
 * air and a display, no block of theirs is touched).
 */
public final class Ashfall {
	private Ashfall() {}

	static final String TAG = "ashbound_ashfall", FX = "ashbound_ashfall_fx";
	static final int ODDS = 12;
	/** the night: from just after dusk till just before dawn (day time) */
	static final int DUSK = 12600, DAWN = 23200;
	static final float MORE = 1 / 3f, HARDER = 0.3f, LOOT = 0.5f, CINDER_CHANCE = 0.35f;
	static final double LIGHT_WITHIN = 160;
	private static final ResourceLocation HP = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "ashfall_hp"),
			DMG = ResourceLocation.fromNamespaceAndPath(Ashbound.ID, "ashfall_dmg");

	public static final net.neoforged.neoforge.registries.DeferredHolder<net.minecraft.core.particles.ParticleType<?>, net.minecraft.core.particles.SimpleParticleType> FLAKE =
			Gates.PARTICLES.register("ash_flake", () -> new net.minecraft.core.particles.SimpleParticleType(false)),
			EMBER = Gates.PARTICLES.register("ash_ember", () -> new net.minecraft.core.particles.SimpleParticleType(false));
	public static final DeferredItem<Item> CINDER = Weapons.ITEMS.registerItem("cinder", p -> new Item(p.rarity(Rarity.UNCOMMON).fireResistant()) {
		@Override
		public void appendHoverText(ItemStack st, Item.TooltipContext ctx, List<Component> lines, net.minecraft.world.item.TooltipFlag f) {
			lines.add(Component.translatable("item.ashbound.cinder.desc").withStyle(ChatFormatting.GRAY, ChatFormatting.ITALIC));
		}
	});

	/** client: is ash falling here, and since when (game time) */
	public static boolean client;
	public static long clientSince;

	static final class State extends SavedData {
		boolean on;
		long since, rolled = -1, last = -10;
		/** the light blocks hung in the air by the braziers, to take down at dawn */
		final Set<Long> lights = new HashSet<>();
		/** towns lit tonight, "x,z" */
		final Set<String> lit = new HashSet<>();

		@Override
		public CompoundTag save(CompoundTag tag, HolderLookup.Provider reg) {
			tag.putBoolean("on", on);
			tag.putLong("since", since);
			tag.putLong("rolled", rolled);
			tag.putLong("last", last);
			ListTag l = new ListTag();
			for (long p : lights) l.add(LongTag.valueOf(p));
			tag.put("lights", l);
			ListTag t = new ListTag();
			for (String s : lit) t.add(StringTag.valueOf(s));
			tag.put("lit", t);
			return tag;
		}

		static State load(CompoundTag tag, HolderLookup.Provider reg) {
			State s = new State();
			s.on = tag.getBoolean("on");
			s.since = tag.getLong("since");
			s.rolled = tag.getLong("rolled");
			s.last = tag.getLong("last");
			for (Tag t : tag.getList("lights", Tag.TAG_LONG)) s.lights.add(((LongTag) t).getAsLong());
			for (Tag t : tag.getList("lit", Tag.TAG_STRING)) s.lit.add(t.getAsString());
			return s;
		}
	}

	static State state(MinecraftServer server) {
		return server.overworld().getDataStorage().computeIfAbsent(new SavedData.Factory<>(State::new, State::load, null), "ashbound_ashfall");
	}

	/** server: is it an ashfall night now */
	public static boolean on(Level l) {
		if (l.isClientSide()) return client;
		return l.getServer() != null && l.dimension() == Level.OVERWORLD && state(l.getServer()).on;
	}

	static boolean night(long dayTime) {
		long t = dayTime % 24000;
		return t >= DUSK && t < DAWN;
	}

	// ---------------------------------------------------------------- start and end

	static void start(ServerLevel l) {
		State s = state(l.getServer());
		if (s.on) return;
		s.on = true;
		s.since = l.getGameTime();
		s.last = l.getDayTime() / 24000;
		s.lit.clear();
		s.setDirty();
		sync(l.getServer(), null);
		for (ServerPlayer p : l.players()) {
			p.sendSystemMessage(Component.literal("Far off, the fire-mountain wakes. Ash begins to fall.").withStyle(ChatFormatting.RED, ChatFormatting.ITALIC));
			p.sendSystemMessage(Component.literal("No one will sleep tonight. Stay near the fires.").withStyle(ChatFormatting.GRAY, ChatFormatting.ITALIC));
			l.playSound(null, p.blockPosition(), SoundEvents.AMBIENT_BASALT_DELTAS_MOOD.value(), SoundSource.AMBIENT, 1.4f, 0.55f);
			l.playSound(null, p.blockPosition(), SoundEvents.LIGHTNING_BOLT_THUNDER, SoundSource.WEATHER, 0.5f, 0.35f);
			if (p.isSleeping()) p.stopSleepInBed(true, true);
		}
	}

	static void stop(ServerLevel l) {
		State s = state(l.getServer());
		if (!s.on) return;
		s.on = false;
		s.setDirty();
		sync(l.getServer(), null);
		for (ServerPlayer p : l.players())
			p.sendSystemMessage(Component.literal("Dawn. The ash stops falling, and the fires are let die.").withStyle(ChatFormatting.GOLD, ChatFormatting.ITALIC));
		douse(l);
		sendHome(l);
	}

	static void sync(MinecraftServer server, ServerPlayer only) {
		State s = state(server);
		Net.AshfallSync m = new Net.AshfallSync(s.on, s.since);
		if (only != null) PacketDistributor.sendToPlayer(only, m);
		else PacketDistributor.sendToAllPlayers(m);
	}

	private static void tick(ServerTickEvent.Post e) {
		MinecraftServer server = e.getServer();
		if (server.getTickCount() % 20 != 7) return;
		ServerLevel l = server.overworld();
		State s = state(server);
		long dt = l.getDayTime(), day = dt / 24000;
		if (s.on) {
			if (!night(dt)) {
				stop(l);
				return;
			}
			for (ServerPlayer p : l.players())
				if (p.isSleeping()) {
					p.stopSleepInBed(true, true);
					p.displayClientMessage(Component.literal("The ash is falling. You can't rest tonight.").withStyle(ChatFormatting.RED), true);
				}
			if (server.getTickCount() % 100 == 7) lightTowns(l, s);
			if (server.getTickCount() % 40 == 7) crackle(l);
			if (server.getTickCount() % 300 == 7) roam(l);
		} else {
			if (!s.lights.isEmpty() && server.getTickCount() % 200 == 7) douse(l);
			if (night(dt) && s.rolled != day) {
				s.rolled = day;
				s.setDirty();
				if (day - s.last > 1 && l.getRandom().nextInt(ODDS) == 0 && !l.players().isEmpty()) start(l);
			}
		}
	}

	// ---------------------------------------------------------------- nobody sleeps

	private static void sleep(CanPlayerSleepEvent e) {
		if (e.getProblem() != null || !on(e.getEntity().level())) return;
		e.setProblem(Player.BedSleepingProblem.OTHER_PROBLEM);
		e.getEntity().displayClientMessage(Component.literal("The ash is falling. You can't rest tonight.").withStyle(ChatFormatting.RED), true);
	}

	// ---------------------------------------------------------------- the night's monsters: thicker, harder, richer

	private static void spawned(FinalizeSpawnEvent e) {
		if (e.isSpawnCancelled() || e.getSpawnType() != MobSpawnType.NATURAL) return;
		ServerLevel l = e.getLevel().getLevel();
		if (l.dimension() != Level.OVERWORLD || !on(l)) return;
		Mob m = e.getEntity();
		if (!(m instanceof Enemy) && m.getType().getCategory() != MobCategory.MONSTER) return;
		harden(m);
		// one in three brings another of its kind along
		if (l.getRandom().nextFloat() < MORE) {
			Entity other = m.getType().create(l);
			if (other instanceof Mob o) {
				double a = l.getRandom().nextDouble() * Math.PI * 2;
				double x = e.getX() + Math.cos(a) * 2.5, z = e.getZ() + Math.sin(a) * 2.5;
				BlockPos at = l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, BlockPos.containing(x, 0, z));
				if (Math.abs(at.getY() - e.getY()) <= 3 && l.getBlockState(at).getCollisionShape(l, at).isEmpty()) {
					o.moveTo(x, at.getY(), z, l.getRandom().nextFloat() * 360, 0);
					o.finalizeSpawn(l, l.getCurrentDifficultyAt(at), MobSpawnType.EVENT, null);
					harden(o);
					l.addFreshEntityWithPassengers(o);
				}
			}
		}
	}

	static void harden(Mob m) {
		if (m.getTags().contains(TAG)) return;
		m.addTag(TAG);
		AttributeInstance hp = m.getAttribute(Attributes.MAX_HEALTH);
		if (hp != null && !hp.hasModifier(HP)) hp.addPermanentModifier(new AttributeModifier(HP, HARDER, AttributeModifier.Operation.ADD_MULTIPLIED_BASE));
		AttributeInstance dmg = m.getAttribute(Attributes.ATTACK_DAMAGE);
		if (dmg != null && !dmg.hasModifier(DMG)) dmg.addPermanentModifier(new AttributeModifier(DMG, HARDER, AttributeModifier.Operation.ADD_MULTIPLIED_BASE));
		m.setHealth(m.getMaxHealth());
	}

	private static void drops(LivingDropsEvent e) {
		if (!e.getEntity().getTags().contains(TAG) || !(e.getSource().getEntity() instanceof Player) || !(e.getEntity().level() instanceof ServerLevel l)) return;
		RandomSource r = l.getRandom();
		List<ItemEntity> more = new ArrayList<>();
		for (ItemEntity it : e.getDrops())
			if (r.nextFloat() < LOOT) {
				ItemStack copy = it.getItem().copy();
				if (copy.getMaxStackSize() == 1 && r.nextFloat() < 0.7f) continue;   // gear doubles less often
				more.add(new ItemEntity(l, it.getX(), it.getY(), it.getZ(), copy));
			}
		e.getDrops().addAll(more);
		var m = e.getEntity();
		if (m.getTags().contains(WALKER)) {
			// the night's own are made of it
			boolean hulk = m.getType().builtInRegistryHolder().key().location().getPath().equals("cinder_hulk");
			int n = hulk ? 3 + r.nextInt(3) : 1 + r.nextInt(2);
			e.getDrops().add(new ItemEntity(l, m.getX(), m.getY() + 0.5, m.getZ(), new ItemStack(CINDER.get(), n)));
		} else if (r.nextFloat() < CINDER_CHANCE)
			e.getDrops().add(new ItemEntity(l, m.getX(), m.getY() + 0.5, m.getZ(), new ItemStack(CINDER.get(), 1 + (r.nextFloat() < 0.3f ? 1 : 0))));
	}

	// ---------------------------------------------------------------- our own come out: the factions' monsters leave their holds

	static final String ROAMER = "ashbound_ashfall_roamer";
	/** how far a hold's monsters wander (from the player, in chunks), how many round one player at once */
	static final int HOLD_REACH = 10, ROAMERS = 6;

	/** Round each player, now and then: the nearest hold of a faction (a mod structure, Haunts) sends one of its own out
	 * into the open toward them. None in a town. */
	private static void roam(ServerLevel l) {
		RandomSource r = l.getRandom();
		for (ServerPlayer p : l.players()) {
			if (p.isSpectator() || r.nextFloat() > 0.65f) continue;
			if (l.getEntitiesOfClass(Mob.class, p.getBoundingBox().inflate(64), m -> m.getTags().contains(ROAMER)).size() >= ROAMERS) continue;
			boolean town = false;
			for (Capital.Site s : Capital.sites)
				if (Math.hypot(p.getX() - s.x, p.getZ() - s.z) < 140) town = true;
			if (town) continue;
			String faction = nearestHold(l, p);
			// near a hold, its own come out half the time; everywhere, the Ashwalkers
			if (faction != null && r.nextBoolean()) {
				String kind = Haunts.roamer(faction, r);
				Mob m = kind == null ? null : bring(l, p, kind, r);
				if (m != null) {
					int best = 1;
					for (ServerPlayer q : l.players()) if (q.distanceToSqr(p) < 64 * 64) best = Math.max(best, Levels.level(q));
					Balance.soften(m, kind, best);
					harden(m);
				}
			} else {
				// a pack: walkers, a herald ringing two on, or a hulk on its own
				float roll = r.nextFloat();
				String[] pack = roll < 0.6f ? new String[] {"ashwalker", "ashwalker", r.nextBoolean() ? "ashwalker" : null}
						: roll < 0.85f ? new String[] {"ash_herald", "ashwalker", "ashwalker"} : new String[] {"cinder_hulk"};
				String rank = "FEDCBAS".substring(Math.min(6, Ranks.party(p)), Math.min(6, Ranks.party(p)) + 1);
				BlockPos near = null;
				for (String kind : pack) {
					if (kind == null) continue;
					Mob m = bring(l, p, kind, r, near);
					if (m == null) continue;
					if (near == null) near = m.blockPosition();
					Balance.atRank(m, kind, rank);
					m.addTag(TAG);
					m.addTag(WALKER);
				}
			}
		}
	}

	static final String WALKER = "ashbound_ashwalker";

	private static Mob bring(ServerLevel l, ServerPlayer p, String kind, RandomSource r) {
		return bring(l, p, kind, r, null);
	}

	/** one of ours out of the ash toward this player (next to `near` if given, for a pack), in a puff of smoke */
	private static Mob bring(ServerLevel l, ServerPlayer p, String kind, RandomSource r, BlockPos near) {
		EntityType<?> type = net.minecraft.core.registries.BuiltInRegistries.ENTITY_TYPE
				.getOptional(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, kind)).orElse(null);
		if (type == null) return null;
		BlockPos at = near == null ? open(l, p, r) : l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
				near.offset(r.nextInt(5) - 2, 0, r.nextInt(5) - 2));
		if (at == null || near != null && Math.abs(at.getY() - near.getY()) > 3 || !(type.create(l) instanceof Mob m)) return null;
		m.moveTo(at.getX() + 0.5, at.getY(), at.getZ() + 0.5, r.nextFloat() * 360, 0);
		m.addTag(ROAMER);
		m.setPersistenceRequired();   // out of the vanilla despawn (a player flying high is "far"); gone at dawn instead
		net.neoforged.neoforge.event.EventHooks.finalizeMobSpawn(m, l, l.getCurrentDifficultyAt(at), MobSpawnType.EVENT, null);
		m.setTarget(p);
		l.addFreshEntity(m);
		l.sendParticles(ParticleTypes.LARGE_SMOKE, m.getX(), m.getY() + 0.5, m.getZ(), 12, 0.4, 0.6, 0.4, 0.02);
		l.sendParticles(ParticleTypes.LAVA, m.getX(), m.getY() + 0.5, m.getZ(), 4, 0.3, 0.3, 0.3, 0);
		// its own sound coming up out of the ash (the rise, the vent bursting, the bell)
		if (LegendSounds.has(kind)) l.playSound(null, m.blockPosition(), LegendSounds.get(kind, "sig"), SoundSource.HOSTILE, 1.6f, 0.95f + r.nextFloat() * 0.1f);
		return m;
	}

	/** the faction of the nearest hold whose start lies in the loaded land round this player */
	private static String nearestHold(ServerLevel l, ServerPlayer p) {
		var reg = l.registryAccess().registryOrThrow(net.minecraft.core.registries.Registries.STRUCTURE);
		int cx = p.getBlockX() >> 4, cz = p.getBlockZ() >> 4;
		String best = null;
		double bestD = Double.MAX_VALUE;
		for (int dx = -HOLD_REACH; dx <= HOLD_REACH; dx++)
			for (int dz = -HOLD_REACH; dz <= HOLD_REACH; dz++) {
				var ch = l.getChunkSource().getChunkNow(cx + dx, cz + dz);
				if (ch == null) continue;
				for (var e : ch.getAllStarts().entrySet()) {
					ResourceLocation id = reg.getKey(e.getKey());
					if (id == null || id.getNamespace().equals(Ashbound.ID) || !e.getValue().isValid()) continue;
					String f = Haunts.factionOf(id);
					if (f == null) continue;
					double d = dx * dx + dz * dz;
					if (d < bestD) {
						bestD = d;
						best = f;
					}
				}
			}
		return best;
	}

	/** open ground under the sky 22-40 blocks off: near the ground under the player (flying or not) */
	private static BlockPos open(ServerLevel l, ServerPlayer p, RandomSource r) {
		int ground = l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, p.blockPosition()).getY();
		for (int t = 0; t < 12; t++) {
			double a = r.nextDouble() * Math.PI * 2, d = 22 + r.nextDouble() * 18;
			BlockPos at = l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,
					BlockPos.containing(p.getX() + Math.cos(a) * d, 0, p.getZ() + Math.sin(a) * d));
			if (!l.isPositionEntityTicking(at) || Math.abs(at.getY() - Math.min(ground, p.getY())) > 16) continue;
			if (!l.getFluidState(at.below()).isEmpty() || !l.getBlockState(at.below()).isFaceSturdy(l, at.below(), net.minecraft.core.Direction.UP)) continue;
			if (!l.getBlockState(at).getCollisionShape(l, at).isEmpty() || !l.getBlockState(at.above()).getCollisionShape(l, at.above()).isEmpty()
					|| !l.getBlockState(at.above(2)).getCollisionShape(l, at.above(2)).isEmpty()) continue;
			return at;
		}
		return null;
	}

	/** dawn: they go back into the ash */
	private static void sendHome(ServerLevel l) {
		for (Entity e : l.getAllEntities())
			if (e instanceof Mob m && m.getTags().contains(ROAMER) && m.isAlive()) {
				l.sendParticles(ParticleTypes.LARGE_SMOKE, m.getX(), m.getY() + 0.5, m.getZ(), 10, 0.4, 0.6, 0.4, 0.02);
				m.discard();
			}
	}

	// ---------------------------------------------------------------- the towns' fires

	/** Towns near a player, not yet lit tonight: braziers down their open ground, round their middle. */
	private static void lightTowns(ServerLevel l, State s) {
		for (Capital.Site site : Capital.sites) {
			String key = site.x + "," + site.z;
			if (s.lit.contains(key)) continue;
			boolean near = false;
			for (ServerPlayer p : l.players())
				if (Math.hypot(p.getX() - site.x, p.getZ() - site.z) < LIGHT_WITHIN) near = true;
			if (!near || !l.isPositionEntityTicking(new BlockPos(site.x, site.floor, site.z))) continue;
			s.lit.add(key);
			s.setDirty();
			int n = braziers(l, s, site);
			Ashbound.LOG.info("ashfall: lit {} braziers in {}", n, site.title);
		}
	}

	private static int braziers(ServerLevel l, State s, Capital.Site site) {
		List<BlockPos> put = new ArrayList<>();
		int max = "highmourn".equals(site.name) ? 24 : 10, reach = "highmourn".equals(site.name) ? 90 : 40;
		// round the middle in widening rings, every few degrees, on open ground under the sky
		for (int r = 6; r <= reach && put.size() < max; r += 4)
			for (int k = 0, steps = Math.max(6, r / 2); k < steps && put.size() < max; k++) {
				double a = (k + (r % 8 == 0 ? 0.5 : 0)) * Math.PI * 2 / steps;
				int x = site.x + (int) Math.round(Math.cos(a) * r), z = site.z + (int) Math.round(Math.sin(a) * r);
				BlockPos stand = l.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, new BlockPos(x, 0, z));
				if (!l.isPositionEntityTicking(stand) || Math.abs(stand.getY() - site.floor) > 12) continue;
				if (!l.getBlockState(stand).isAir() || !l.getBlockState(stand.above()).isAir() || !l.getFluidState(stand.below()).isEmpty()) continue;
				if (!l.getBlockState(stand.below()).isFaceSturdy(l, stand.below(), net.minecraft.core.Direction.UP)) continue;
				// not in a doorway or against a wall: open on all four sides
				boolean open = true;
				for (var d : net.minecraft.core.Direction.Plane.HORIZONTAL)
					if (!l.getBlockState(stand.relative(d)).getCollisionShape(l, stand.relative(d)).isEmpty()) open = false;
				if (!open || put.stream().anyMatch(q -> q.distSqr(stand) < 81)) continue;
				put.add(stand);
			}
		for (BlockPos p : put) brazier(l, s, p);
		return put.size();
	}

	private static void brazier(ServerLevel l, State s, BlockPos stand) {
		// the post (a wall block's look), a campfire's fire on it; a light in the air where the fire is
		display(l, stand, "minecraft:polished_blackstone_wall", 0.8f, 1.0f, 0);
		display(l, stand, "minecraft:campfire", 0.75f, 0.6f, 1.0f);
		BlockPos light = stand.above();
		if (l.getBlockState(light).isAir()) {
			l.setBlock(light, Blocks.LIGHT.defaultBlockState().setValue(net.minecraft.world.level.block.LightBlock.LEVEL, 14), 3);
			s.lights.add(light.asLong());
			s.setDirty();
		}
		l.playSound(null, stand, SoundEvents.FIRECHARGE_USE, SoundSource.BLOCKS, 0.6f, 0.8f);
	}

	private static void display(ServerLevel l, BlockPos at, String block, float wide, float tall, float up) {
		CompoundTag tag = new CompoundTag();
		tag.putString("id", "minecraft:block_display");
		CompoundTag bs = new CompoundTag();
		bs.putString("Name", block);
		if (block.endsWith("campfire")) {
			CompoundTag props = new CompoundTag();
			props.putString("lit", "true");
			bs.put("Properties", props);
		}
		tag.put("block_state", bs);
		CompoundTag tf = new CompoundTag();
		tf.put("left_rotation", floats(0, 0, 0, 1));
		tf.put("right_rotation", floats(0, 0, 0, 1));
		tf.put("translation", floats(-wide / 2, up, -wide / 2));
		tf.put("scale", floats(wide, tall, wide));
		tag.put("transformation", tf);
		if (block.endsWith("campfire")) {
			CompoundTag br = new CompoundTag();
			br.putInt("block", 15);
			br.putInt("sky", 0);
			tag.put("brightness", br);
		}
		ListTag tags = new ListTag();
		tags.add(StringTag.valueOf(FX));
		tag.put("Tags", tags);
		Entity e = EntityType.loadEntityRecursive(tag, l, en -> {
			en.moveTo(at.getX() + 0.5, at.getY(), at.getZ() + 0.5, 0, 0);
			return en;
		});
		if (e != null) l.addFreshEntity(e);
	}

	private static ListTag floats(float... v) {
		ListTag t = new ListTag();
		for (float f : v) t.add(FloatTag.valueOf(f));
		return t;
	}

	/** smoke and sparks off the braziers players can see */
	private static void crackle(ServerLevel l) {
		for (ServerPlayer p : l.players())
			for (Entity e : l.getEntities((Entity) null, p.getBoundingBox().inflate(48), en -> en.getTags().contains(FX)
					&& en instanceof net.minecraft.world.entity.Display.BlockDisplay)) {
				if (l.getRandom().nextFloat() < 0.5f) continue;
				l.sendParticles(p, ParticleTypes.CAMPFIRE_COSY_SMOKE, false, e.getX(), e.getY() + 1.6, e.getZ(), 1, 0.1, 0.1, 0.1, 0.01);
				l.sendParticles(p, ParticleTypes.LAVA, false, e.getX(), e.getY() + 1.4, e.getZ(), 1, 0.1, 0.05, 0.1, 0);
			}
	}

	/** Dawn: the fires out, the lights down (those in loaded land now, the rest when it loads). */
	private static void douse(ServerLevel l) {
		State s = state(l.getServer());
		for (Entity e : l.getAllEntities())
			if (e != null && e.getTags().contains(FX)) e.discard();
		s.lights.removeIf(p -> {
			BlockPos b = BlockPos.of(p);
			if (!l.isLoaded(b)) return false;
			if (l.getBlockState(b).is(Blocks.LIGHT)) l.setBlock(b, Blocks.AIR.defaultBlockState(), 3);
			return true;
		});
		s.setDirty();
	}

	/** a brazier's display coming back from disk after the night it was lit for: gone */
	private static void joined(EntityJoinLevelEvent e) {
		if (e.getLevel().isClientSide() || !e.getEntity().getTags().contains(FX) && !e.getEntity().getTags().contains(ROAMER)) return;
		if (!(e.getLevel() instanceof ServerLevel l) || !state(l.getServer()).on) e.setCanceled(true);
	}

	private static void login(PlayerEvent.PlayerLoggedInEvent e) {
		if (e.getEntity() instanceof ServerPlayer p) sync(p.getServer(), p);
	}

	private static void commands(RegisterCommandsEvent e) {
		e.getDispatcher().register(Commands.literal("ashbound").requires(c -> c.hasPermission(2)).then(Commands.literal("ashfall")
				.then(Commands.literal("start").executes(c -> {
					ServerLevel l = c.getSource().getServer().overworld();
					if (!night(l.getDayTime())) l.setDayTime(l.getDayTime() / 24000 * 24000 + DUSK + 20);
					start(l);
					return 1;
				}))
				.then(Commands.literal("stop").executes(c -> {
					stop(c.getSource().getServer().overworld());
					return 1;
				}))));
	}

	static void init() {
		NeoForge.EVENT_BUS.addListener(Ashfall::tick);
		NeoForge.EVENT_BUS.addListener(Ashfall::sleep);
		NeoForge.EVENT_BUS.addListener(Ashfall::spawned);
		NeoForge.EVENT_BUS.addListener(Ashfall::drops);
		NeoForge.EVENT_BUS.addListener(Ashfall::joined);
		NeoForge.EVENT_BUS.addListener(Ashfall::login);
		NeoForge.EVENT_BUS.addListener(Ashfall::commands);
	}
}
