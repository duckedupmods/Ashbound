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
	}

	private static final String[] NAMES = {"Character", "Bag", "Pets", "Mount", "Skills", "Journal"};
	private static final int H = 15, GAP = 2, PAD = 10, MIN_Y = 2, CHARACTER = 0, BAG = 1, PETS = 2, MOUNT = 3, SKILLS = 4, JOURNAL = 5;

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
			int all = -GAP, y = Math.max(MIN_Y, ((Panel) e.getScreen()).panelTop() - H - 1);
			for (String name : NAMES) all += font.width(name) + PAD + GAP;
			int x = (e.getScreen().width - all) / 2;
			for (int i = 0; i < NAMES.length; i++) {
				int w = font.width(NAMES[i]) + PAD;
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

	private static void openCharacter() {
		PacketDistributor.sendToServer(new CPacketOpenCurios(ItemStack.EMPTY));
	}

	private static int active(Screen s) {
		return s instanceof CharacterScreen ? CHARACTER : s instanceof BagScreen ? BAG : s instanceof PetScreen ? PETS : s instanceof MountUpScreen ? MOUNT
				: s instanceof SkillScreen ? SKILLS : s instanceof QuestScreen ? JOURNAL : -1;
	}

	private static final class Tab extends AbstractButton {
		private final int which;
		private final boolean on;

		Tab(int x, int y, int w, int which, boolean on) {
			super(x, y, w, H, Component.literal(NAMES[which]));
			this.which = which;
			this.on = on;
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
				default -> QuestScreen.open();
			}
		}

		@Override
		protected void renderWidget(GuiGraphics g, int mx, int my, float pt) {
			var font = Minecraft.getInstance().font;
			AshUi.row(g, getX(), getY(), width, H, on, isHovered());
			g.drawString(font, getMessage(), getX() + (width - font.width(getMessage())) / 2, getY() + 4, on || isHovered() ? AshUi.TEXT : AshUi.BODY, true);
		}

		@Override
		protected void updateWidgetNarration(NarrationElementOutput out) {
			defaultButtonNarrationText(out);
		}
	}
}
