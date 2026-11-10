package com.snoringwalrus.ashbound.client;

import com.snoringwalrus.ashbound.Bag;
import com.snoringwalrus.ashbound.Mounts;
import com.snoringwalrus.ashbound.Net;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.AbstractButton;
import net.minecraft.client.gui.narration.NarrationElementOutput;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.inventory.InventoryScreen;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ServerboundContainerClosePacket;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.client.event.ScreenEvent;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.network.PacketDistributor;
import top.theillusivec4.curios.client.gui.CuriosScreen;
import top.theillusivec4.curios.common.network.client.CPacketOpenCurios;

/** The row of tabs along the top of your own screens, and what puts CharacterScreen where the inventory was. Creative keeps its own. */
final class MenuTabs {
	private MenuTabs() {}

	/** A screen with the tabs on it: where its panel starts. */
	interface Panel {
		int panelTop();

		/** Where the panel's middle is across, when it isn't the screen's. */
		default int panelMiddle() {
			return -1;
		}
	}

	private static final String[] NAMES = {"Character", "Bag", "Pets", "Mount", "Skills", "Trades", "Journal", "Party"};
	/** A tab is its icon, the open one its icon and name; hovering one names it. */
	private static final int H = 20, ICON_W = 22, GAP = 2, PAD = 10, MIN_Y = 2, CHARACTER = 0, BAG = 1, PETS = 2, MOUNT = 3, SKILLS = 4, TRADES = 5, JOURNAL = 6, PARTY = 7;

	static void hooks() {
		NeoForge.EVENT_BUS.addListener((ScreenEvent.Opening e) -> {
			Minecraft mc = Minecraft.getInstance();
			if (e.getNewScreen() instanceof InventoryScreen && !mc.gameMode.hasInfiniteItems()) {
				e.setCanceled(true);
				openCharacter();
			} else if (e.getNewScreen() instanceof CuriosScreen s) e.setNewScreen(new CharacterScreen(s.getMenu(), mc.player.getInventory(), s.getTitle()));
		});
		NeoForge.EVENT_BUS.addListener((ScreenEvent.Init.Post e) -> {
			int on = active(e.getScreen());
			if (on < 0) return;
			var font = Minecraft.getInstance().font;
			Screen sc = e.getScreen();
			int mid = ((Panel) sc).panelMiddle() >= 0 ? ((Panel) sc).panelMiddle() : sc.width / 2;
			int all = -GAP, y = Math.max(MIN_Y, ((Panel) sc).panelTop() - H - 1);
			for (int i = 0; i < NAMES.length; i++) all += width(font, i, on == i) + GAP;
			int x = Math.max(2, Math.min(sc.width - all - 2, mid - all / 2));
			for (int i = 0; i < NAMES.length; i++) {
				int w = width(font, i, on == i);
				e.addListener(new Tab(x, y, w, i, on == i));
				x += w + GAP;
			}
		});
	}

	/**
	 * Quietly lets go of the menu that's open: the screen stays up until the next one comes. Closing it the usual way goes through no
	 * screen at all, and that grabs the mouse and sends it back to the middle.
	 */
	private static void leaveMenu() {
		LocalPlayer p = Minecraft.getInstance().player;
		if (p.containerMenu == p.inventoryMenu) return;
		p.connection.send(new ServerboundContainerClosePacket(p.containerMenu.containerId));
		p.containerMenu = p.inventoryMenu;
	}

	private static int width(net.minecraft.client.gui.Font font, int i, boolean on) {
		return on ? ICON_W + font.width(NAMES[i]) + PAD - 2 : ICON_W;
	}

	private static ItemStack icon(int i) {
		return switch (i) {
			case CHARACTER -> new ItemStack(net.minecraft.world.item.Items.IRON_CHESTPLATE);
			case BAG -> new ItemStack(Bag.POUCH.get());
			case PETS -> new ItemStack(net.minecraft.world.item.Items.BONE);
			case MOUNT -> new ItemStack(net.minecraft.world.item.Items.SADDLE);
			case SKILLS -> new ItemStack(net.minecraft.world.item.Items.ENCHANTED_BOOK);
			case TRADES -> new ItemStack(net.minecraft.world.item.Items.CRAFTING_TABLE);
			case JOURNAL -> new ItemStack(net.minecraft.world.item.Items.WRITABLE_BOOK);
			default -> new ItemStack(net.minecraft.world.item.Items.SHIELD);
		};
	}

	private static void openCharacter() {
		PacketDistributor.sendToServer(new CPacketOpenCurios(ItemStack.EMPTY));
	}

	private static int active(Screen s) {
		return s instanceof CharacterScreen ? CHARACTER : s instanceof BagScreen ? BAG : s instanceof PetScreen ? PETS : s instanceof MountUpScreen ? MOUNT
				: s instanceof SkillScreen ? SKILLS : s instanceof TradesScreen ? TRADES : s instanceof QuestScreen ? JOURNAL : s instanceof PartyScreen ? PARTY : -1;
	}

	private static final class Tab extends AbstractButton {
		private final int which;
		private final boolean on;

		Tab(int x, int y, int w, int which, boolean on) {
			super(x, y, w, H, Component.literal(NAMES[which]));
			this.which = which;
			this.on = on;
			if (!on) setTooltip(net.minecraft.client.gui.components.Tooltip.create(getMessage()));
		}

		@Override
		public void onPress() {
			if (on) return;
			Minecraft mc = Minecraft.getInstance();
			leaveMenu();
			switch (which) {
				case CHARACTER -> openCharacter();
				case BAG -> PacketDistributor.sendToServer(new Net.BagAct(Bag.OPEN, ItemStack.EMPTY));
				case PETS -> mc.setScreen(new PetScreen());
				case MOUNT -> {
					if (!Mounts.client.isEmpty()) mc.setScreen(new MountUpScreen());
				}
				case SKILLS -> mc.setScreen(new SkillScreen());
				case TRADES -> mc.setScreen(new TradesScreen());
				case PARTY -> PartyScreen.open();
				default -> QuestScreen.open();
			}
		}

		@Override
		protected void renderWidget(GuiGraphics g, int mx, int my, float pt) {
			var font = Minecraft.getInstance().font;
			AshUi.row(g, getX(), getY(), width, H, on, isHovered());
			g.renderItem(icon(which), getX() + 3, getY() + 2);
			if (on) g.drawString(font, getMessage(), getX() + ICON_W, getY() + 6, AshUi.TEXT, true);
		}

		@Override
		protected void updateWidgetNarration(NarrationElementOutput out) {
			defaultButtonNarrationText(out);
		}
	}
}
