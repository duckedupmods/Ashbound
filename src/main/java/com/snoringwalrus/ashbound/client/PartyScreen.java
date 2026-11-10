package com.snoringwalrus.ashbound.client;

import java.util.ArrayList;
import java.util.List;

import com.snoringwalrus.ashbound.Coins;
import com.snoringwalrus.ashbound.Net;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.components.PlayerFaceRenderer;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.multiplayer.PlayerInfo;
import net.minecraft.network.chat.Component;
import net.minecraft.util.Mth;
import net.neoforged.fml.loading.FMLLoader;
import net.neoforged.neoforge.network.PacketDistributor;

/**
 * The party: who's in it on the left with what you can do to whoever's picked, the bank at the top right, and who's around to invite
 * under that. What's on it is Net.clientBoard; what can be pressed is only a courtesy, the server checks each one (Party.act).
 */
public class PartyScreen extends Screen implements MenuTabs.Panel {
	private static final int W = 384, H = 232, PAD = 10, TOP = 28, LEFT_W = 206, ROW = 22, BTN_H = 16, BTN_GAP = 4, LINE = 10, INVITE_ROW = 16, MEMBER_HP = 3;
	private static final String[] ROLES = {"Member", "Commander", "Leader"};

	private String picked = "";
	private int scroll;
	private EditBox amount;
	private AshUi.AshButton commander, lead, kick, leave, putIn, takeOut, accept, decline;
	private static final int NUMBERS_W = 92, METERS_W = 52, SWITCH_Y = 4, SEAL = 14, MEMBER_SEAL = 10;

	public PartyScreen() {
		super(Component.literal("Party"));
	}

	static void open() {
		send(Net.PartyAct.SHOW, "", 0);
		Minecraft.getInstance().setScreen(new PartyScreen());
	}

	private static void send(int what, String who, int coins) {
		PacketDistributor.sendToServer(new Net.PartyAct(what, who, coins));
	}

	/** A player's face, or a blank where their skin isn't known: they're not on the server just now. */
	static void face(GuiGraphics g, Minecraft mc, String name, int x, int y, int size) {
		PlayerInfo info = mc.getConnection() == null ? null : mc.getConnection().getPlayerInfo(name);
		// a dev run's stand-ins (/partytest) borrow your face
		if (info == null && name.startsWith("Test_") && !FMLLoader.isProduction()) info = mc.getConnection().getPlayerInfo(mc.player.getUUID());
		if (info != null) PlayerFaceRenderer.draw(g, info.getSkin(), x, y, size);
		else {
			g.fill(x, y, x + size, y + size, 0xFF2C2925);
			g.drawCenteredString(mc.font, "?", x + size / 2, y + (size - 8) / 2, AshUi.MUTED);
		}
	}

	// ---------------------------------------------------------------- layout

	private int left() {
		return (width - W) / 2;
	}

	private int top() {
		return (height - H) / 2;
	}

	private int rightX() {
		return left() + LEFT_W + PAD * 2;
	}

	private int rightW() {
		return W - LEFT_W - PAD * 3;
	}

	private int amountY() {
		return top() + TOP + 24;
	}

	private int ledgerY() {
		return amountY() + BTN_H * 2 + BTN_GAP + 6;
	}

	private int inviteY() {
		return ledgerY() + 4 * LINE + 16;
	}

	private int inviteRows() {
		return (top() + H - PAD - inviteY()) / INVITE_ROW;
	}

	@Override
	public int panelTop() {
		return top();
	}

	@Override
	protected void init() {
		int ax = left() + PAD, by = top() + H - PAD - BTN_H, w3 = (LEFT_W - 2 * BTN_GAP) / 3, rx = rightX(), half = (rightW() - BTN_GAP) / 2;
		commander = addRenderableWidget(button(ax, by, w3, "Commander", false, b -> send(Net.PartyAct.COMMANDER, picked, 0)));
		lead = addRenderableWidget(button(ax + w3 + BTN_GAP, by, w3, "Make leader", false, b -> send(Net.PartyAct.LEAD, picked, 0)));
		kick = addRenderableWidget(button(ax + 2 * (w3 + BTN_GAP), by, w3, "Kick", false, b -> send(Net.PartyAct.KICK, picked, 0)));
		leave = addRenderableWidget(button(ax, by, LEFT_W, "Leave the party", false, b -> send(Net.PartyAct.LEAVE, "", 0)));
		accept = addRenderableWidget(button(ax, top() + TOP + 44, (LEFT_W - BTN_GAP) / 2, "Accept", true, b -> send(Net.PartyAct.ACCEPT, "", 0)));
		decline = addRenderableWidget(button(ax + (LEFT_W + BTN_GAP) / 2, top() + TOP + 44, (LEFT_W - BTN_GAP) / 2, "Decline", false, b -> send(Net.PartyAct.DECLINE, "", 0)));
		String had = amount == null ? "" : amount.getValue();
		amount = new EditBox(font, rx + 4, amountY() + 4, rightW() - 8, 10, Component.literal("Coins"));
		amount.setBordered(false);
		amount.setMaxLength(9);
		amount.setFilter(s -> s.matches("\\d*"));
		amount.setTextColor(0xFFFFFFFF);
		amount.setHint(Component.literal("How many coins").withStyle(s -> s.withColor(AshUi.DIM & 0xFFFFFF)));
		amount.setValue(had);
		addRenderableWidget(amount);
		putIn = addRenderableWidget(button(rx, amountY() + BTN_H + BTN_GAP, half, "Put in", true, b -> bank(Net.PartyAct.PUT_IN)));
		takeOut = addRenderableWidget(button(rx + half + BTN_GAP, amountY() + BTN_H + BTN_GAP, half, "Take out", false, b -> bank(Net.PartyAct.TAKE_OUT)));
		int sx = left() + W - PAD - METERS_W;
		addRenderableWidget(button(sx, top() + SWITCH_Y, METERS_W, "Meter", false, b -> minecraft.setScreen(new MeterSetup(this))));
		addRenderableWidget(button(sx - BTN_GAP - NUMBERS_W, top() + SWITCH_Y, NUMBERS_W, numbersLabel(), false, b -> {
			HudPrefs.numbers = !HudPrefs.numbers;
			HudPrefs.save();
			b.setMessage(Component.literal(numbersLabel()));
		}));
	}

	private static String numbersLabel() {
		return "Hit numbers: " + (HudPrefs.numbers ? "On" : "Off");
	}

	private static AshUi.AshButton button(int x, int y, int w, String name, boolean ember, net.minecraft.client.gui.components.Button.OnPress press) {
		return new AshUi.AshButton(x, y, w, BTN_H, Component.literal(name), press, ember);
	}

	private void bank(int what) {
		if (amount.getValue().isEmpty()) return;
		send(what, "", Mth.clamp(Integer.parseInt(amount.getValue()), 0, Integer.MAX_VALUE));
		amount.setValue("");
	}

	@Override
	public boolean isPauseScreen() {
		return false;
	}

	// ---------------------------------------------------------------- what's what

	private static List<Net.PartyCard> cards() {
		return Net.clientBoard.cards();
	}

	private String me() {
		return minecraft.player.getGameProfile().getName();
	}

	private int myRole() {
		for (Net.PartyCard c : cards()) if (c.name().equalsIgnoreCase(me())) return c.role();
		return -1;
	}

	private Net.PartyCard pick() {
		for (Net.PartyCard c : cards()) if (c.name().equals(picked)) return c;
		return null;
	}

	/** Whoever's on the server and in no list of ours, by name. Someone in another party is told so when you try. */
	private List<String> strangers() {
		List<String> out = new ArrayList<>();
		for (PlayerInfo i : minecraft.getConnection().getOnlinePlayers()) {
			String n = i.getProfile().getName();
			if (!n.equalsIgnoreCase(me()) && cards().stream().noneMatch(c -> c.name().equalsIgnoreCase(n))) out.add(n);
		}
		if (!FMLLoader.isProduction() && cards().stream().noneMatch(c -> c.name().equals("Test_Guest"))) out.add("Test_Guest");
		out.sort(String.CASE_INSENSITIVE_ORDER);
		return out;
	}

	private boolean canInvite() {
		return cards().size() < 8 && myRole() != Net.PartyCard.MEMBER;
	}

	private int rowY(int i) {
		return top() + TOP + i * ROW;
	}

	private boolean invited() {
		return cards().isEmpty() && !Net.clientBoard.invitedBy().isEmpty();
	}

	/** Who you can press what on, each frame: the board can change under you. */
	private void buttons() {
		Net.PartyCard p = pick();
		int mine = myRole();
		boolean inParty = mine >= 0, other = p != null && !p.name().equalsIgnoreCase(me()), leader = mine == Net.PartyCard.LEADER;
		commander.visible = other;
		lead.visible = other;
		kick.visible = other;
		leave.visible = inParty && !other;
		if (other) {
			commander.setMessage(Component.literal(p.role() == Net.PartyCard.COMMANDER ? "Demote" : "Commander"));
			commander.active = leader;
			lead.active = leader;
			kick.active = mine > p.role();
		}
		accept.visible = decline.visible = invited();
		amount.visible = putIn.visible = takeOut.visible = inParty;
		takeOut.active = mine >= Net.PartyCard.COMMANDER;
	}

	// ---------------------------------------------------------------- input

	@Override
	public boolean mouseClicked(double mx, double my, int button) {
		if (super.mouseClicked(mx, my, button)) return true;
		int x = left() + PAD;
		for (int i = 0; i < cards().size(); i++)
			if (mx >= x && mx < x + LEFT_W && my >= rowY(i) && my < rowY(i) + ROW - 2) {
				picked = cards().get(i).name();
				return true;
			}
		if (canInvite() && mx >= rightX() && mx < rightX() + rightW() && my >= inviteY()) {
			int r = (int) (my - inviteY()) / INVITE_ROW + scroll;
			List<String> all = strangers();
			if (r >= scroll && r < Math.min(all.size(), scroll + inviteRows())) {
				send(Net.PartyAct.INVITE, all.get(r), 0);
				return true;
			}
		}
		return false;
	}

	@Override
	public boolean mouseScrolled(double mx, double my, double sx, double sy) {
		scroll = Math.max(0, Math.min(Math.max(0, strangers().size() - inviteRows()), scroll - (int) Math.signum(sy)));
		return true;
	}

	@Override
	public boolean keyPressed(int key, int scan, int mods) {
		if (!amount.isFocused() && CurioKeys.PARTY.matches(key, scan)) {
			onClose();
			return true;
		}
		return super.keyPressed(key, scan, mods);
	}

	// ---------------------------------------------------------------- drawing

	@Override
	public void render(GuiGraphics g, int mx, int my, float pt) {
		buttons();
		super.render(g, mx, my, pt);
	}

	@Override
	public void renderBackground(GuiGraphics g, int mx, int my, float pt) {
		g.fill(0, 0, width, height, 0x70000000);
		AshUi.panel(g, left(), top(), W, H);
		AshUi.header(g, left(), top(), W, 20, cards().isEmpty() ? "PARTY" : "PARTY  " + cards().size() + " / 8");
		rank(g, mx, my);
		members(g, mx, my);
		right(g, mx, my);
	}

	/** The party's rank up in the corner, and over it what a party of this size does to a fight. */
	private void rank(GuiGraphics g, int mx, int my) {
		int x = left() + PAD - 2, y = top() + 3;
		AshUi.seal(g, x, y, SEAL, Net.clientBoard.rank());
		String title = cards().isEmpty() ? "Your rank" : "Party rank";
		g.drawString(font, title, x + SEAL + 3, y + 4, AshUi.MUTED, false);
		if (mx >= x && mx < x + SEAL + 3 + font.width(title) && my >= y && my < y + SEAL)
			g.renderComponentTooltip(font, com.snoringwalrus.ashbound.Balance.scaling(Math.max(1, cards().size())).stream().map(s -> (Component) Component.literal(s)).toList(), mx, my);
	}

	private void members(GuiGraphics g, int mx, int my) {
		int x = left() + PAD;
		if (cards().isEmpty()) {
			String s = invited() ? Net.clientBoard.invitedBy() + " invites you to their party." : "You're not in a party. Pick someone on the right to invite them.";
			int y = top() + TOP + 6;
			for (var line : font.split(Component.literal(s), LEFT_W - 8)) {
				g.drawString(font, line, x + 4, y, AshUi.BODY, false);
				y += LINE;
			}
			return;
		}
		for (int i = 0; i < cards().size(); i++) {
			Net.PartyCard c = cards().get(i);
			int y = rowY(i);
			boolean hover = mx >= x && mx < x + LEFT_W && my >= y && my < y + ROW - 2;
			AshUi.row(g, x, y, LEFT_W, ROW - 2, c.name().equals(picked), hover);
			face(g, minecraft, c.name(), x + 4, y + 2, 16);
			boolean on = online(c);
			if (!on) g.fill(x + 4, y + 2, x + 20, y + 18, 0xB0000000);
			g.drawString(font, c.name(), x + 25, y + 2, on ? AshUi.TEXT : AshUi.DIM, true);
			String role = ROLES[c.role()];
			g.drawString(font, role, x + LEFT_W - 6 - font.width(role), y + 2, c.role() > Net.PartyCard.MEMBER ? AshUi.EMBER_LT : AshUi.MUTED, false);
			AshUi.seal(g, x + LEFT_W - 6 - font.width(role) - MEMBER_SEAL - 3, y + 1, MEMBER_SEAL, c.rank());
			float hp = health(c);
			g.fill(x + 25, y + 13, x + LEFT_W - 6, y + 13 + MEMBER_HP, 0xFF1E0E0C);
			if (hp > 0) g.fill(x + 25, y + 13, x + 25 + Math.round((LEFT_W - 31) * hp), y + 13 + MEMBER_HP, 0xFFD8402C);
		}
	}

	/** The HUD's line is fresher than the board, which only comes when something changes. */
	private boolean online(Net.PartyCard c) {
		return c.name().equalsIgnoreCase(me()) || Net.clientParty.stream().anyMatch(m -> m.name().equals(c.name()) && m.online());
	}

	private float health(Net.PartyCard c) {
		if (c.name().equalsIgnoreCase(me())) return Mth.clamp(minecraft.player.getHealth() / minecraft.player.getMaxHealth(), 0, 1);
		for (Net.PartyMember m : Net.clientParty) if (m.name().equals(c.name()) && m.online()) return Mth.clamp(m.health() / Math.max(1, m.max()), 0, 1);
		return 0;
	}

	private void right(GuiGraphics g, int mx, int my) {
		int x = rightX(), w = rightW(), y = top() + TOP;
		if (myRole() >= 0) {
			g.drawString(font, "PARTY BANK", x, y, AshUi.LABEL, false);
			AshUi.price(g, x + w, y, Net.clientBoard.bank(), AshUi.EMBER_LT);
			g.drawString(font, "You carry", x, y + 11, AshUi.MUTED, false);
			AshUi.price(g, x + w, y + 11, Coins.client, AshUi.BODY);
			AshUi.inset(g, x, amountY(), w, BTN_H);
			int ly = ledgerY();
			for (String line : Net.clientBoard.ledger().subList(0, Math.min(4, Net.clientBoard.ledger().size()))) {
				g.drawString(font, font.plainSubstrByWidth(line, w), x, ly, AshUi.MUTED, false);
				ly += LINE;
			}
			AshUi.divider(g, x, inviteY() - 12, w);
		}
		if (myRole() >= 0 && !canInvite()) {
			g.drawString(font, cards().size() >= 8 ? "The party is full" : "Only a commander can invite", x, inviteY(), AshUi.DIM, false);
			return;
		}
		g.drawString(font, "INVITE", x, inviteY() - 8, AshUi.LABEL, false);
		List<String> all = strangers();
		if (all.isEmpty()) g.drawString(font, "Nobody else is on", x, inviteY() + 3, AshUi.DIM, false);
		for (int r = 0; r < inviteRows() && r + scroll < all.size(); r++) {
			String n = all.get(r + scroll);
			int ry = inviteY() + r * INVITE_ROW;
			boolean hover = mx >= x && mx < x + w && my >= ry && my < ry + INVITE_ROW - 1;
			AshUi.row(g, x, ry, w, INVITE_ROW - 1, false, hover);
			face(g, minecraft, n, x + 3, ry + 2, 11);
			g.drawString(font, font.plainSubstrByWidth(n, w - 42), x + 18, ry + 4, AshUi.BODY, false);
			if (hover) g.drawString(font, "Invite", x + w - 4 - font.width("Invite"), ry + 4, AshUi.EMBER_LT, false);
		}
	}
}
