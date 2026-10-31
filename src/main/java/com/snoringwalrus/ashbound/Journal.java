package com.snoringwalrus.ashbound;

import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

/** The quests as the Journal screen and the compass read them, from the same list as the quest book (tools/questbook.py). */
public final class Journal {
	private Journal() {}

	/**
	 * @param flag what Story.mark sets when it's done  @param where what the compass points at: "capital", "at:x,z" in the
	 * city, or "gate:R"  @param who the townsperson who ends it by talking, saying `say`, and you answering `reply`
	 * @param reach or ends it by coming this close to `where`
	 */
	public record Quest(String key, String title, String text, String flag, List<String> deps, String where, String who, List<String> say, String reply, int reach) {}

	public record Chapter(String title, String sub, List<Quest> quests) {}

	public static final List<Chapter> CHAPTERS = load();
	/** Said both ways, in place of a quest: this player's been through the Journal's lesson. */
	public static final String TAUGHT = "#taught";
	private static final Map<String, Quest> BY_KEY = new HashMap<>();

	static {
		for (Chapter c : CHAPTERS) for (Quest q : c.quests) BY_KEY.put(q.key, q);
	}

	private static List<String> strings(JsonObject o, String k) {
		List<String> out = new ArrayList<>();
		o.getAsJsonArray(k).forEach(s -> out.add(s.getAsString()));
		return out;
	}

	private static List<Chapter> load() {
		List<Chapter> out = new ArrayList<>();
		try (var in = new InputStreamReader(Journal.class.getResourceAsStream("/ashbound/journal.json"), StandardCharsets.UTF_8)) {
			for (JsonElement e : JsonParser.parseReader(in).getAsJsonArray()) {
				JsonObject c = e.getAsJsonObject();
				List<Quest> quests = new ArrayList<>();
				for (JsonElement qe : c.getAsJsonArray("quests")) {
					JsonObject q = qe.getAsJsonObject();
					quests.add(new Quest(q.get("key").getAsString(), q.get("title").getAsString(), q.get("text").getAsString(), q.get("flag").getAsString(),
							strings(q, "deps"), q.get("where").getAsString(), q.get("who").getAsString(), strings(q, "say"), q.get("reply").getAsString(), q.get("reach").getAsInt()));
				}
				out.add(new Chapter(c.get("title").getAsString(), c.get("sub").getAsString(), quests));
			}
		} catch (java.io.IOException e) {
			throw new IllegalStateException("journal.json", e);
		}
		return out;
	}

	public static Quest of(String key) {
		return BY_KEY.get(key);
	}

	/** Open to you: not done, and everything before it is. */
	public static boolean open(Quest q, Set<String> done) {
		return !done.contains(q.key) && done.containsAll(q.deps);
	}
}
