package com.snoringwalrus.ashbound;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.network.PacketDistributor;
import top.theillusivec4.curios.api.CuriosApi;

/**
 * Pets: worn in their own Curios slot like any curio (Curios.Curio does the buffs, the tooltip and right-click to wear), but alive
 * to look at. There's no entity: client/PetRender and client/WornCurios draw them on whoever wears one, so they can't die, get
 * lost or cost the server anything. resources/ashbound/pets.json comes from tools/voxpets.py --export, models from the same place.
 */
public final class Pets {
	private Pets() {}

	public enum Where {
		HEEL("Trots at your heel"), HOVER("Flies beside you");

		final String says;

		Where(String says) {
			this.says = says;
		}
	}

	/** box: the model's middle x, y, z and its longest side, in blocks at full size; size: how big it's drawn */
	public record Pet(String id, Where where, float size, float[] box, Curios.Spec spec) {}

	public static final Map<String, Pet> ALL = load();

	private static Map<String, Pet> load() {
		Map<String, Pet> out = new LinkedHashMap<>();
		try (InputStream in = Pets.class.getResourceAsStream("/ashbound/pets.json")) {
			if (in == null) return out;
			for (JsonElement el : JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonArray()) {
				JsonObject o = el.getAsJsonObject();
				Map<String, Double> stats = new LinkedHashMap<>();
				for (var e : o.getAsJsonObject("stats").entrySet()) stats.put(e.getKey(), e.getValue().getAsDouble());
				var b = o.getAsJsonArray("box");
				float[] box = {b.get(0).getAsFloat(), b.get(1).getAsFloat(), b.get(2).getAsFloat(), b.get(3).getAsFloat()};
				String id = o.get("id").getAsString();
				Where where = Where.valueOf(o.get("where").getAsString().toUpperCase());
				out.put(id, new Pet(id, where, o.get("size").getAsFloat(), box, new Curios.Spec(id, o.get("name").getAsString(), "pet",
						WorldArms.Tier.valueOf(o.get("rarity").getAsString().toUpperCase()), where.says, stats, "", new Curios.Worn(id, 1, 0, 0, 0, 0))));
			}
		} catch (Exception e) {
			Ashbound.LOG.error("pets not loaded", e);
		}
		return out;
	}

	public static List<Curios.Spec> specs() {
		List<Curios.Spec> out = new ArrayList<>();
		for (Pet p : ALL.values()) out.add(p.spec());
		return out;
	}

	private static String id(ItemStack s) {
		return s.getItem() instanceof Curios.Curio c && ALL.containsKey(c.spec().id()) ? c.spec().id() : "";
	}

	private static void hand(ServerPlayer p, ItemStack s) {
		p.getInventory().add(s);
		if (!s.isEmpty()) Bag.store(p, s);
	}

	/** From PetScreen: call a pet out of your pack or the Bag, or send back the one that's out. An empty id only asks what you've got. */
	public static void act(ServerPlayer p, String id) {
		var inv = CuriosApi.getCuriosInventory(p).orElse(null);
		var slot = inv == null ? null : inv.getStacksHandler("pet").orElse(null);
		if (slot == null || slot.getSlots() == 0) return;
		ItemStack out = slot.getStacks().getStackInSlot(0).copy();
		Pet pet = ALL.get(id);
		if (pet != null) {
			if (id.equals(id(out))) {
				inv.setEquippedCurio("pet", 0, ItemStack.EMPTY);
				hand(p, out);
			} else {
				ItemStack call = ItemStack.EMPTY;
				for (ItemStack s : p.getInventory().items) if (id.equals(id(s))) {
					call = s.split(1);
					break;
				}
				if (call.isEmpty()) call = Bag.take(p, new ItemStack(Curios.item(pet.spec())), 1);
				if (!call.isEmpty()) {
					inv.setEquippedCurio("pet", 0, call);
					if (!out.isEmpty()) hand(p, out);
				}
			}
		}
		String worn = id(slot.getStacks().getStackInSlot(0));
		List<String> owned = new ArrayList<>();
		for (Pet q : ALL.values()) {
			ItemStack like = new ItemStack(Curios.item(q.spec()));
			if (q.id().equals(worn) || p.getInventory().items.stream().anyMatch(s -> q.id().equals(id(s))) || Bag.count(p, like) > 0) owned.add(q.id());
		}
		PacketDistributor.sendToPlayer(p, new Net.PetList(owned, worn));
	}

	/** What p has out, if it's showing. */
	public static Pet worn(Player p) {
		var h = CuriosApi.getCuriosInventory(p).flatMap(inv -> inv.getStacksHandler("pet")).orElse(null);
		if (h == null || h.getSlots() == 0 || !h.getRenders().isEmpty() && !h.getRenders().get(0)) return null;
		return h.getStacks().getStackInSlot(0).getItem() instanceof Curios.Curio c ? ALL.get(c.spec().id()) : null;
	}
}
