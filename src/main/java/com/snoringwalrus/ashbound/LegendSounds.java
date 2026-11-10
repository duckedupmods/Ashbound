package com.snoringwalrus.ashbound;

import java.util.HashMap;
import java.util.Map;

import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * The Legends' own voices (tools/make_sounds.py + legend_sounds.json, ElevenLabs): each one's idle rumble, roar, hurt,
 * death, footfall, and the one sound only it makes ("sig": the Penitent's bell, Blackbriar's crows, the Plough's scrape,
 * Sunbreaker's beam, Mire's cackle, the Smile's giggle, Harpoon's chain, the Mountain's quake).
 */
public final class LegendSounds {
	private LegendSounds() {}

	static final DeferredRegister<SoundEvent> SOUNDS = DeferredRegister.create(Registries.SOUND_EVENT, Ashbound.ID);
	static final String[] LEGENDS = {"rime_penitent", "old_blackbriar", "red_plough", "sunbreaker", "grandmother_mire", "hollow_smile",
			"old_harpoon", "walking_mountain",
			// not Legends, but voiced the same way: the ashfall night's own (Ashfall, tools/mobs/ashwalkers.py)
			"ashwalker", "cinder_hulk", "ash_herald"};
	/** voiced like the Legends but recorded at their own pitch, not pitched up for a Legend's 0.8 */
	static final java.util.Set<String> AS_RECORDED = java.util.Set.of("ashwalker", "cinder_hulk", "ash_herald");
	static final String[] KINDS = {"idle", "roar", "hurt", "death", "step", "sig"};
	private static final Map<String, DeferredHolder<SoundEvent, SoundEvent>> BY = new HashMap<>();
	private static final Map<String, GateMobs.Voice> VOICES = new HashMap<>();

	static {
		for (String l : LEGENDS)
			for (String k : KINDS) {
				String id = "legend." + l + "." + k;
				BY.put(l + "." + k, SOUNDS.register(id, () -> SoundEvent.createVariableRangeEvent(ResourceLocation.fromNamespaceAndPath(Ashbound.ID, id))));
			}
	}

	static void register(IEventBus bus) {
		SOUNDS.register(bus);
	}

	/** One of a Legend's sounds (null if it isn't a Legend). */
	static SoundEvent get(String legend, String kind) {
		DeferredHolder<SoundEvent, SoundEvent> h = BY.get(legend + "." + kind);
		return h == null ? null : h.get();
	}

	static boolean has(String legend) {
		return BY.containsKey(legend + ".roar");
	}

	/** Its voice for GateMobs (built when first asked for, once the sounds are registered). Already deep: pitched so the
	 * Legend's 0.8 brings it back to as recorded. */
	static GateMobs.Voice voice(String legend) {
		return VOICES.computeIfAbsent(legend, l -> new GateMobs.Voice(get(l, "idle"), get(l, "hurt"), get(l, "death"), get(l, "step"), AS_RECORDED.contains(l) ? 1f : 1.25f));
	}
}
