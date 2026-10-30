"""The Roster v2 monsters as monsterforge specs: one theme (ramps) per dungeon, then each monster's choices.
Roles per dungeon (docs/DUNGEONS.md): swarm, brute, caster, skirmisher, elite (the key), boss.

    python tools/monsterforge.py <gate|name> [--preview]
"""
import os
import sys
from voxsword import ramp
from voxboss import Part, C
import monsterforge as MF

# ================================================================ themes

THEMES = {
    "weeping_mine": dict(
        metal=ramp("#1a1410", "#2e2218", "#4a3222", "#6a4428", "#8c5a30", "#b07440", "#d09a5a"),     # old copper, rust
        cloth=ramp("#14181c", "#20262c", "#2c343c", "#3a444e", "#4c5862"),
        leather=ramp("#140e0a", "#22180f", "#342416", "#4a3420", "#60442a"),
        skin=ramp("#2a3034", "#3c464a", "#566266", "#75838a", "#97a6ac"),                           # grey, dust-sick
        accent=ramp("#3a2410", "#6a4018", "#9a6024", "#c8843a", "#eab060"),
        glow=ramp("#0c4a48", "#1a7e78", "#34b8aa", "#7ce8d8", "#d0fff6"),
        crystal=ramp("#0a3a40", "#126068", "#1e8c90", "#3cc0b8", "#86e8dc", "#e0fff8"),
        rock=ramp("#121418", "#1c2026", "#2a2f36", "#3a4048", "#4e555e", "#666e78"),
        crust=(ramp("#126068", "#1e8c90", "#3cc0b8", "#86e8dc"), 0.22),
        fur=ramp("#2a2420", "#3e352c", "#55493c", "#6e604e", "#8a7a64"),
        eye=ramp("#1a7e78", "#34b8aa", "#7ce8d8", "#e0fff8"),
        veins=True,
        bone=ramp("#4a4438", "#6e6654", "#948a72", "#b8ae94", "#d8d0b8"),
        flesh=ramp("#5a2a2a", "#8a4040", "#b46060", "#d88a84"), vein=ramp("#8a4040", "#b46060"),
    ),
}

GATES = {}
SPECS = {}


def spec(gate, name, **kw):
    kw["theme"] = THEMES[gate]
    kw["gate"] = gate
    SPECS[name] = kw
    GATES.setdefault(gate, []).append(name)


def by_gate(g):
    return GATES[g]


# ================================================================ extras (what only one monster has)

def crystal_growth(where, n=4, length=3.4, seed=1):
    def f(B):
        part, at = where(B)
        B.spikes(part, at, n, length, mat="crystal", seed=seed)
    return f


def weeping_eyes(B):
    """crystal tears run from the eyes down the face"""
    hd = B.parts["head"]
    for sx in (-1.2, 1.2):
        B.add(hd, C(sx, 33.0, 3.55, 0.6, 3.4, 0.4), "crystal", group="glow", tag="tear")


def keyring(B):
    hips = B.parts["hips"]
    B.add(hips, C(4.4, 16.4, 2.2, 0.4, 3.0, 0.4), "accent", tag="keyring")
    for k in range(3):
        B.add(hips, C(4.0 + k * 0.6, 14.4 - k * 0.4, 2.4, 0.4, 2.2, 1.0), "accent", tag="key")


def vein_heart(B):
    to = B.parts["torso"]
    B.add(to, C(0, 25.0, 3.6, 4.4, 4.8, 1.6), "crystal", group="glow", tag="heart")
    B.add(to, C(0, 25.8, 4.3, 2.4, 2.8, 0.6), "glow", group="glow", tag="heart_core")
    B.spikes(to, (0, 29.0, 3.0), 3, 3.0, mat="crystal", seed=40)


def vein_arm(B):
    """the Vein's right arm: no hand left, a club of raw crystal grown over the fist"""
    hd = B.parts["hand_r"]
    x = -B.sw
    B.add(hd, C(x, 5.0, 0.2, 6.4, 9.0, 6.4), "rock", tag="club")
    B.spikes(hd, (x, 8.0, 0.2), 7, 5.0, mat="crystal", seed=44, spread=2.4)


def burrow_claws(B):
    for nm, sx in (("hand_l", 1), ("hand_r", -1)):
        hd = B.parts[nm]
        x = sx * B.sw
        B.add(hd, C(x, 10.0, 1.0, 4.4, 3.0, 2.6), "skin", tag="digger")
        for c in (-1.4, -0.4, 0.6, 1.6):
            B.add(hd, C(x + c, 5.6, 1.6, 0.8, 4.6, 1.0), "bone", tag="claw")


def cart_body(B):
    to = B.parts["torso"]
    B.add(to, C(0, 19.0, 0, 13.0, 10.0, 9.6), "metal", tag="cart")
    B.add(to, C(0, 19.0, 0, 13.6, 1.2, 10.2), "accent", tag="cart_band")
    B.add(to, C(0, 27.6, 0, 13.6, 1.2, 10.2), "accent", tag="cart_band")
    for sx in (-1, 1):
        for sz in (-1, 1):
            B.add(to, C(sx * 7.0, 17.6, sz * 3.0, 1.2, 3.6, 3.6), "dark", tag="wheel")
    B.add(to, C(0, 28.8, 0, 11.0, 2.6, 8.0), "rock", tag="ore")
    B.spikes(to, (0, 31.0, 0), 6, 4.0, mat="crystal", seed=31, spread=3.2)


# ================================================================ the Weeping Mine (E)

spec("weeping_mine", "shard_crawler", rig="crawler", size=0.6, leg_len=0.9, body_mat="rock", leg_mat="rock",
     joint_mat="crystal", fang_mat="crystal",
     extra=[crystal_growth(lambda B: (B.parts["abdomen"], (0, 12.6, -7.6)), 6, 4.0, 3),
            crystal_growth(lambda B: (B.parts["body"], (0, 10.0, 0)), 3, 2.6, 4)],
     ent=(1.0, 0.6), stats=dict(hp=18, speed=0.3, dmg=4, armor=4, kb=0))

spec("weeping_mine", "cart_golem", build=dict(size=1.35, bulk=1.5, hunch=14, arms=1.3, legs=1.2), legs="rock", hips="rock",
     torso="rock", shoulders="crystal", shoulder_size=1.2, head="golem", head_size=1.0, arms="rock", eye="glow",
     back="cart", head_spikes=4, extra=[crystal_growth(lambda B: (B.parts["fore_l"], (B.sw, 20.0, -1.0)), 3, 3.0, 5)],
     ent=(1.6, 3.6), stats=dict(hp=70, speed=0.18, dmg=11, armor=8, kb=0.9))

spec("weeping_mine", "lamp_miner", build=dict(size=0.98, hunch=12), legs="cloth", hips="leather", torso="leather",
     shoulders="leather", head="miner", arms="leather", back=["pack", "crystals"],
     back_opt={"pack": {"lamp": True}, "crystals": {"n": 4, "len": 4.0}},
     right="staff", right_opt={"top": "lantern", "shaft": "wood"},
     left="lantern", extra=[weeping_eyes], ent=(0.9, 2.7), stats=dict(hp=28, speed=0.22, dmg=5, armor=2, kb=0))

spec("weeping_mine", "blind_burrower", build=dict(size=0.92, hunch=26, arms=1.15, bulk=0.85), legs="bare", hips="leather",
     torso="bare", head="mole", arms="bare", back="crystals", back_opt={"crystals": {"n": 3, "len": 3.0}},
     extra=[burrow_claws], ent=(0.9, 2.4), stats=dict(hp=24, speed=0.32, dmg=6, armor=0, kb=0))

spec("weeping_mine", "foreman", build=dict(size=1.15, bulk=1.25, hunch=6, arms=1.15), legs="cloth", hips="leather",
     torso="leather", shoulders="crystal", shoulder_size=1.1, head="miner", arms="plate", back="pack",
     right="pick2", right_opt={"size": 1.25, "head": "metal", "head_size": 1.3}, fur_collar=True, bandolier=True,
     extra=[keyring, weeping_eyes], ent=(1.2, 3.2), stats=dict(hp=140, speed=0.21, dmg=11, armor=8, kb=0.7), key=True)

spec("weeping_mine", "the_vein", build=dict(size=2.2, bulk=1.6, hunch=14, arms=1.3, legs=1.2), legs="rock", hips="rock",
     torso="rock", shoulders="crystal", shoulder_size=1.4, head="golem", head_size=1.0, arms="rock", eye="glow",
     head_spikes=7, spike_mat="crystal", big_arm=1.3, back=["crystals", "cart"], back_opt={"crystals": {"n": 9, "len": 7.0}},
     extra=[vein_heart, vein_arm], ent=(2.8, 6.2), stats=dict(hp=420, speed=0.2, dmg=16, armor=10, kb=1.0), boss=True)


# ================================================================ the Tide Chapel (E)

THEMES["tide_chapel"] = dict(
    metal=ramp("#0e1c1a", "#1a2e2a", "#28443e", "#3a5c54", "#527a6e", "#729a8c", "#9cbcae"),       # sea-eaten bronze-green
    cloth=ramp("#0a1a1a", "#122828", "#1c3a38", "#284e4a", "#36645e"),
    leather=ramp("#1a140e", "#2a2016", "#3c2e20", "#4e3e2c", "#645038"),
    skin=ramp("#4a5a58", "#62746e", "#7e908a", "#9cada6", "#bcc8c2"),                              # drowned, blue-grey
    accent=ramp("#2a1a08", "#4a3010", "#6e4a1c", "#94682c", "#b88a44", "#d8ac66"),                  # bell bronze
    glow=ramp("#2a6a70", "#4a9aa0", "#7cc8cc", "#b4e8ea", "#eafcfc"),                              # pearl light
    crystal=ramp("#3a6870", "#5a9098", "#86b8c0", "#b8dce0", "#e8f8fa"),
    rock=ramp("#1a2220", "#26302e", "#34403c", "#44524e", "#566662"),
    crust=(ramp("#8a8676", "#aaa694", "#c8c4b0", "#e2dece"), 0.2),                                 # barnacles
    crust_cloth=(ramp("#1e3a20", "#2e5430", "#40703e"), 0.15),                                     # weed
    scale=ramp("#2a0e08", "#4a1a0e", "#6e2a16", "#944022", "#b85a32", "#d47c4a"),                  # crab shell
    bone=ramp("#6a6656", "#8a8672", "#aaa692", "#c8c4b0", "#e2dece"),
    eye=ramp("#4a9aa0", "#7cc8cc", "#b4e8ea", "#eafcfc"),
    fur=ramp("#1e3a20", "#2e5430", "#40703e", "#548a50"),                                          # kelp
)
THEMES["tide_chapel"]["extra_shaders"] = {
    "bronze": MF.mk(ramp("#10140c", "#1e2414", "#2e3420", "#42462a", "#5a5a36", "#7a7444"), 0.45, 1.4, 0.22, 0.14,
                    crust=(ramp("#2a5a4a", "#3e7a64", "#5a9a80", "#7cb89c"), 0.3))}


def barnacles(where, n=6, seed=1):
    def f(B):
        part, at = where(B)
        B.spikes(part, at, n, 1.4, mat="bone", seed=seed, spread=3.0)
    return f


def kelp(B):
    """weed hanging off the shoulders and belt"""
    to, hips = B.parts["torso"], B.parts["hips"]
    for k, x in enumerate((-4.4, -2.0, 1.4, 3.8)):
        B.add(to, C(x, 22.0 - k % 2 * 3, 2.9, 0.8, 9.0 + k % 2 * 3, 0.4), "fur", tag="kelp")
    for k, x in enumerate((-3.0, 0.4, 2.8)):
        B.add(hips, C(x, 10.0 - k, 3.0, 0.8, 9.0, 0.4), "fur", tag="kelp")


def crab_claw(B):
    """the right arm ends in a crab's great claw"""
    hd = B.parts["hand_r"]
    x = -B.sw
    B.add(hd, C(x, 5.6, 0.6, 5.4, 8.0, 5.2), "scale", tag="claw")
    up = Part("pincer_top", (x, 13.0, 3.0), (("x", -26),), hd)
    B.add(up, C(x, 13.0, 4.6, 3.6, 2.4, 9.0), "scale", tag="pincer")
    B.add(up, C(x, 12.6, 8.8, 2.6, 1.4, 1.2), "bone", tag="pincer_tip")
    lo = Part("pincer_low", (x, 7.0, 3.0), (("x", 14),), hd)
    B.add(lo, C(x, 6.6, 4.2, 3.0, 2.2, 7.6), "scale", tag="pincer")
    B.spikes(hd, (x, 8.0, -1.6), 4, 1.2, mat="bone", seed=17)


def eyestalks(B):
    hd = B.parts["head"]
    for sx in (-1.6, 1.6):
        B.add(hd, C(sx, 40.6, 2.0, 0.8, 3.4, 0.8), "scale", tag="stalk")
        B.add(hd, C(sx, 44.0, 2.0, 1.4, 1.4, 1.4), "eye", group="glow", tag="eye")


def choir_heads(B):
    """two more of the choir grown into its shoulders, mouths open"""
    to = B.parts["torso"]
    for sx in (-6.2, 6.2):
        B.add(to, C(sx, 31.4, 1.6, 3.6, 4.2, 3.6), "skin", tag="choir_head")
        B.add(to, C(sx, 32.2, 3.45, 1.6, 1.4, 0.3), "dark", tag="choir_mouth")
        for ex in (-0.8, 0.8):
            B.add(to, C(sx + ex, 34.0, 3.45, 0.6, 0.4, 0.3), "eye", group="glow", tag="eye")
        B.spikes(to, (sx, 35.6, 1.6), 3, 1.0, mat="bone", seed=int(sx))


def bell_body(B):
    """the Drowned Bell: a church bell grown over head and chest, its clapper swinging inside, weed and shells"""
    to = B.parts["torso"]
    B.add(to, C(0, 24.0, 0, 14.0, 13.0, 12.0), "bronze", tag="bell")
    B.add(to, C(0, 37.0, 0, 10.0, 3.0, 9.0), "bronze", tag="bell")
    B.add(to, C(0, 23.0, 0, 15.4, 1.6, 13.4), "bronze", tag="lip")
    B.add(to, C(0, 40.0, 0, 4.0, 3.0, 2.0), "metal", tag="crown")
    B.add(to, C(0, 26.0, 6.05, 7.0, 6.0, 0.3), "dark", tag="mouth")
    for sx in (-2.2, 2.2):
        B.add(to, C(sx, 32.0, 6.1, 1.8, 1.2, 0.3), "eye", group="glow", tag="eye")
    B.add(to, C(0, 22.0, 0, 3.0, 4.0, 3.0), "metal", tag="clapper")
    B.spikes(to, (0, 37.0, 0), 8, 2.0, mat="bone", seed=55, spread=5.0)
    for k, x in enumerate((-6.0, -3.0, 0.5, 3.6, 6.2)):
        B.add(to, C(x, 16.0 - k % 2 * 3, 6.2 - abs(x) * 0.25, 0.9, 8.0, 0.4), "fur", tag="kelp")


spec("tide_chapel", "tide_crab", rig="crawler", size=0.75, leg_len=0.8, legs=8, body_mat="scale", leg_mat="scale", pincers=True,
     joint_mat="bone", fang_mat="scale", extra=[barnacles(lambda B: (B.parts["abdomen"], (0, 12.0, -7.6)), 5, 3)],
     ent=(1.1, 0.7), stats=dict(hp=16, speed=0.32, dmg=4, armor=4, kb=0))

spec("tide_chapel", "crab_knight", build=dict(size=1.3, bulk=1.4, hunch=8, arms=1.1), legs="chitin", hips="chitin",
     torso="chitin", shoulders="spiked", spike_mat="scale", shoulder_size=1.2, head="helm", arms="chitin", big_arm=1.4,
     back="shell", back_opt={"shell": {"mat": "scale", "barnacles": "bone"}}, left="shield",
     left_opt={"head": "scale", "face": "metal", "w": 11, "h": 15},
     extra=[crab_claw, eyestalks], ent=(1.4, 3.4), stats=dict(hp=70, speed=0.19, dmg=10, armor=10, kb=0.8))

spec("tide_chapel", "tide_priest", build=dict(size=1.0, hunch=10), legs="robe", hips="robe", torso="robe", head="hood",
     arms="robe", hand_mat="skin", back="cloak", right="staff", right_opt={"top": "lantern"}, left="censer",
     extra=[kelp, barnacles(lambda B: (B.parts["torso"], (0, 32.0, -2.0)), 4, 7)],
     ent=(0.9, 2.8), stats=dict(hp=30, speed=0.21, dmg=5, armor=2, kb=0))

spec("tide_chapel", "net_thrower", build=dict(size=0.98, hunch=12, bulk=0.9), legs="cloth", hips="leather",
     torso="leather", shoulders="leather", head="hood", arms="leather", back="quiver", right="harpoon", left="net",
     extra=[kelp], ent=(0.9, 2.7), stats=dict(hp=26, speed=0.3, dmg=6, armor=2, kb=0))

spec("tide_chapel", "barnacle_choir", build=dict(size=1.3, bulk=1.4, hunch=6), legs="robe", hips="robe", torso="robe",
     head="mask", mask_mat="bone", hair="fur", arms="robe", hand_mat="skin", back="cloak",
     right="staff", right_opt={"top": "orb", "size": 1.2}, left="book",
     extra=[choir_heads, kelp, barnacles(lambda B: (B.parts["torso"], (0, 28.0, 2.6)), 7, 9)],
     ent=(1.3, 3.4), stats=dict(hp=150, speed=0.2, dmg=10, armor=8, kb=0.6), key=True)

spec("tide_chapel", "drowned_bell", build=dict(size=2.2, bulk=1.6, hunch=4, arms=1.3, legs=1.25), legs="plate",
     hips="plate", torso="plate", shoulders="spiked", spike_mat="bone", shoulder_size=1.3, head="skull", head_size=0.01,
     arms="plate", right="anchor", right_opt={"size": 1.1, "head": "metal"}, left="chain_ball", left_opt={"head": "accent"},
     back="cloak", extra=[bell_body], texel=1, ent=(3.0, 6.4), stats=dict(hp=440, speed=0.2, dmg=16, armor=10, kb=1.0), boss=True)


# ================================================================ the Brigand's Gorge (E)

THEMES["brigands_gorge"] = dict(
    metal=ramp("#16161a", "#24242a", "#36363e", "#4a4a54", "#62626c", "#7e7e88", "#a0a0aa"),
    cloth=ramp("#2a0806", "#44100a", "#621a10", "#82261a", "#a03424"),                            # bandit red
    leather=ramp("#1a100a", "#2a1a10", "#3e2818", "#543822", "#6c4a2e"),
    skin=ramp("#3a2418", "#563626", "#764a34", "#966446", "#b48060"),                             # sun-dark
    accent=ramp("#4a2e08", "#7a4c10", "#a87018", "#d0961f", "#ecbc34", "#ffdc6a"),                 # stolen gold
    glow=ramp("#6a1a04", "#a83a0a", "#e06a1a", "#ffa04a", "#ffd8a0"),
    rock=ramp("#3a1a12", "#52261a", "#6c3422", "#88442c", "#a45a3a"),
    fur=ramp("#1e1610", "#2e2218", "#403022", "#54402e", "#6a523c"),
    bone=ramp("#6a5e48", "#8a7c62", "#aa9a7e", "#c8b89a", "#e2d4b8"),
    eye=ramp("#a83a0a", "#e06a1a", "#ffa04a", "#ffe0b0"),
    skin_ogre=None,
)
THEMES["brigands_gorge"]["extra_shaders"] = {
    "ogre": MF.mk(ramp("#2a3018", "#3a4220", "#4c562a", "#606c36", "#788644"), 0.5, 1.0, 0.24, 0.04)}


def scarf_mask(B):
    """a scarf pulled up over the nose, the eyes shadowed under the hood"""
    hd = B.parts["head"]
    B.add(hd, C(0, 33.0, 3.2, 5.6, 3.2, 1.0), "cloth", tag="scarf")
    B.add(hd, C(1.4, 31.0, 3.4, 1.4, 2.6, 0.4), "cloth", tag="scarf_tail")


def wide_hat(B):
    hd = B.parts["head"]
    B.add(hd, C(0, 40.0, 0.2, 10.0, 0.8, 10.0), "leather", tag="brim")
    B.add(hd, C(0, 40.8, 0.0, 5.6, 3.0, 5.6), "leather", tag="crown_hat")
    B.add(hd, C(0, 40.8, 0.0, 5.8, 0.8, 5.8), "accent", tag="hatband")
    B.add(hd, C(2.6, 41.4, -1.6, 0.6, 4.0, 1.6), "cloth", tag="feather")


def tusks(B):
    hd = B.parts["head"]
    for sx in (-1.4, 1.4):
        B.add(hd, C(sx, 33.6, 3.6, 0.9, 2.6, 0.9), "bone", tag="tusk")
    B.add(hd, C(0, 37.4, 3.2, 5.6, 1.4, 0.8), "ogre", tag="brow")


def sash(B):
    hips = B.parts["hips"]
    B.add(hips, C(0, 19.6, 0, 9.2, 2.0, 5.8), "cloth", tag="sash")
    B.add(hips, C(-3.6, 13.0, 2.6, 1.4, 6.6, 0.4), "cloth", tag="sash_tail")


def loot_sack(B):
    to = B.parts["torso"]
    B.add(to, C(0, 22.0, -5.6, 8.0, 9.0, 5.0), "leather", tag="sack")
    B.add(to, C(0, 31.0, -5.6, 3.0, 1.6, 2.0), "accent", tag="sack_tie")
    B.spikes(to, (0, 31.0, -5.6), 3, 1.6, mat="accent", seed=19)


def kings_beard(B):
    hd = B.parts["head"]
    B.add(hd, C(0, 30.6, 2.8, 4.6, 4.4, 2.0), "cloth", tag="beard")
    B.add(hd, C(0, 29.0, 3.0, 2.6, 2.0, 1.6), "cloth", tag="beard")


def charms(B):
    """bone charms and a hex bag hung off the belt"""
    hips = B.parts["hips"]
    for k, x in enumerate((-3.6, -1.2, 1.4, 3.6)):
        B.add(hips, C(x, 15.4 - k % 2, 2.8, 0.3, 4.0, 0.3), "leather", tag="cord")
        B.add(hips, C(x, 14.0 - k % 2, 2.8, 1.4, 1.6, 1.0), "bone" if k % 2 else "fur", tag="charm")


spec("brigands_gorge", "footpad", build=dict(size=0.92, hunch=10, bulk=0.85), legs="cloth", hips="leather", torso="leather",
     head="hood", arms="leather", right="dagger", right_opt={"head": "metal"}, extra=[scarf_mask, sash],
     ent=(0.8, 2.6), stats=dict(hp=18, speed=0.3, dmg=4, armor=1, kb=0))

spec("brigands_gorge", "gorge_ogre", build=dict(size=1.5, bulk=1.7, hunch=18, arms=1.35, legs=1.2), legs="bare", hips="beast",
     torso="gut", gut_mat="fur", shoulders="fur", head="face", hair="fur", arms="bare", bracers="leather",
     right="club", right_opt={"size": 1.4, "head": "metal", "shaft": "wood"}, extra=[tusks, loot_sack],
     ent=(1.6, 3.8), stats=dict(hp=75, speed=0.18, dmg=12, armor=3, kb=0.8))

spec("brigands_gorge", "hedge_hexer", build=dict(size=0.95, hunch=20), legs="robe", hips="robe", torso="robe", head="hood",
     arms="robe", hand_mat="skin", back="cloak", right="staff", right_opt={"top": "skull"}, left="lantern",
     extra=[charms], ent=(0.9, 2.6), stats=dict(hp=26, speed=0.21, dmg=5, armor=1, kb=0))

spec("brigands_gorge", "knife_dancer", build=dict(size=0.98, hunch=6, bulk=0.85), legs="cloth", hips="leather",
     torso="leather", head="mask", mask_mat="cloth", hair="dark", arms="leather", right="dagger", left="dagger",
     extra=[sash], ent=(0.8, 2.7), stats=dict(hp=24, speed=0.33, dmg=6, armor=1, kb=0))

spec("brigands_gorge", "bandit_lieutenant", build=dict(size=1.15, bulk=1.2, hunch=4), legs="plate", hips="leather",
     torso="leather", shoulders="plate", head="face", hair="dark", arms="plate", back="cape", bandolier=True,
     right="sword", right_opt={"size": 1.2}, left="shield", left_opt={"w": 9, "h": 12, "head": "wood", "face": "cloth"},
     extra=[wide_hat, sash], ent=(1.1, 3.1), stats=dict(hp=140, speed=0.23, dmg=10, armor=8, kb=0.6), key=True)

spec("brigands_gorge", "red_jack", build=dict(size=2.0, bulk=1.4, hunch=4, arms=1.15), legs="plate", hips="cloth",
     torso="plate", shoulders="spiked", spike_mat="accent", shoulder_size=1.2, head="face", hair="cloth", crown="accent",
     arms="plate", back=["cape", "pack"], right="greatsword", right_opt={"size": 1.2, "glow_edge": True},
     extra=[kings_beard, sash], texel=1, ent=(2.0, 5.8), stats=dict(hp=420, speed=0.24, dmg=15, armor=10, kb=0.9), boss=True)


# ================================================================ the Rookery (D)

THEMES["rookery"] = dict(
    metal=ramp("#0c0c10", "#16161c", "#22222a", "#30303a", "#42424e", "#5a5a68", "#7a7a88"),
    cloth=ramp("#08080c", "#101016", "#1a1a22", "#24242e", "#30303c"),
    leather=ramp("#120c0c", "#1e1414", "#2c1e1e", "#3c2a2a", "#4e3838"),
    skin=ramp("#3a3430", "#524a44", "#6c625a", "#887c72", "#a4988c"),
    accent=ramp("#5a5446", "#7a7260", "#9a927c", "#bab29a", "#d8d0b8"),                               # bone
    glow=ramp("#34205e", "#4e3488", "#7056b0", "#9a84d4", "#d0c4f2"),                              # omen violet
    feather=ramp("#06060a", "#0e0e14", "#18182a", "#24243e", "#343456", "#4a4a74"),                  # blue-black sheen
    rock=ramp("#0e0e12", "#16161c", "#1e1e26", "#282832", "#34343e"),
    bone=ramp("#5a5446", "#7a7260", "#9a927c", "#bab29a", "#d8d0b8"),
    eye=ramp("#7056b0", "#9a84d4", "#d0c4f2", "#f4f0ff"),
    fur=ramp("#06060a", "#0e0e14", "#18182a", "#24243e"),
    scale=ramp("#141210", "#221e1a", "#322c26", "#443c34", "#584e44"),
)


def talons(B):
    for nm in ("foot_l", "foot_r"):
        ft = B.parts[nm]
        x = (1 if nm.endswith("l") else -1) * B.lw
        for c in (-1.2, 0, 1.2):
            B.add(ft, C(x + c, 0, 4.4, 0.7, 1.0, 2.6), "bone", tag="boot")


def feather_cape(B):
    to = B.parts["torso"]
    cp = Part("feather_cape", (0, 33.0, -3.4), (("x", 12),), to)
    for k, x in enumerate((-4.8, -2.4, 0, 2.4, 4.8)):
        B.add(cp, C(x, 12.0 - abs(x) * 0.6, -3.4 - k % 2 * 0.3, 2.6, 21.0 - abs(x) * 0.6, 0.6), "feather", tag="cape")


def omen_eye(B):
    to = B.parts["torso"]
    B.add(to, C(0, 27.6, 3.0, 3.0, 2.0, 0.4), "glow", group="glow", tag="omen")
    B.add(to, C(0, 28.1, 3.25, 1.0, 1.0, 0.3), "dark", tag="pupil")


spec("rookery", "carrion_crow", build=dict(size=0.6, hunch=26, bulk=0.9), legs="chitin", hips="feather", torso="feather",
     shoulders="feather", head="bird", arms="feather", beak="accent", back="tail", back_opt={"tail": {"mat": "feather"}},
     extra=[talons], ent=(0.7, 1.6), stats=dict(hp=12, speed=0.32, dmg=3, armor=0, kb=0))

spec("rookery", "crowbrute", build=dict(size=1.35, bulk=1.5, hunch=16, arms=1.3, legs=1.2), legs="chitin", hips="leather",
     torso="feather", shoulders="spiked", spike_mat="bone", head="bird", beak="accent", arms="feather",
     right="maul", right_opt={"size": 1.2, "head": "metal", "shaft": "wood"}, back="cape", back_opt={"cape": {"mat": "feather"}},
     extra=[talons], ent=(1.4, 3.6), stats=dict(hp=70, speed=0.2, dmg=11, armor=6, kb=0.7))

spec("rookery", "augur", build=dict(size=1.0, hunch=14), legs="robe", hips="robe", torso="robe", head="bird", beak="accent",
     arms="robe", hand_mat="skin", back="cloak", right="staff", right_opt={"top": "orb"}, left="book",
     extra=[omen_eye, talons], ent=(0.9, 2.8), stats=dict(hp=28, speed=0.22, dmg=5, armor=2, kb=0))

spec("rookery", "feather_blade", build=dict(size=1.0, hunch=10, bulk=0.85), legs="chitin", hips="leather", torso="feather",
     head="bird", beak="accent", arms="feather", right="sword", right_opt={"head": "metal"}, left="dagger",
     extra=[feather_cape, talons], ent=(0.9, 2.8), stats=dict(hp=26, speed=0.33, dmg=6, armor=2, kb=0))

spec("rookery", "rook_captain", build=dict(size=1.2, bulk=1.25, hunch=6), legs="plate", hips="plate", torso="plate",
     shoulders="feather", shoulder_size=1.3, head="bird", beak="metal", arms="plate", right="spear", right_opt={"size": 1.1},
     left="shield", left_opt={"head": "metal", "face": "feather", "w": 10, "h": 16}, extra=[feather_cape, talons],
     ent=(1.2, 3.2), stats=dict(hp=150, speed=0.22, dmg=11, armor=9, kb=0.6), key=True)

spec("rookery", "raven_mother", build=dict(size=2.2, bulk=1.3, hunch=12, arms=1.2), legs="robe", hips="robe", torso="feather",
     shoulders="feather", shoulder_size=1.5, head="bird", beak="bone", crown="bone", arms="feather", back=["wings", "cloak"],
     back_opt={"cloak": {"mat": "feather"}}, right="scythe", right_opt={"size": 1.2, "head": "metal"},
     extra=[omen_eye, talons], texel=1, ent=(2.4, 6.0), stats=dict(hp=460, speed=0.22, dmg=16, armor=8, kb=0.9), boss=True)


# ================================================================ the Hollow Circus (D)

THEMES["hollow_circus"] = dict(
    metal=ramp("#1a1418", "#2a2028", "#3c2e3a", "#50404e", "#665466", "#80708a"),
    cloth=ramp("#3a0810", "#561018", "#741a24", "#922432", "#b03242"),                              # circus red
    leather=ramp("#1e0e0a", "#2e1810", "#422418", "#583222", "#70422e"),
    skin=ramp("#6a5c50", "#867664", "#a4927c", "#c2b098", "#dccab2"),                               # greasepaint pale
    accent=ramp("#4a2e08", "#7a4c10", "#a87018", "#d0961f", "#ecbc34", "#ffdc6a"),                  # gilt
    glow=ramp("#a8601a", "#e09a3a", "#ffc870", "#ffe6b0", "#fff6e0"),
    wood=ramp("#3a2a1a", "#544028", "#6e5638", "#8a6e4a", "#a6885e"),
    bone=ramp("#8a8478", "#a8a294", "#c4bfb2", "#dcd8cc", "#f0eee6"),                               # white paint
    eye=ramp("#e09a3a", "#ffc870", "#ffe6b0", "#ffffff"),
    fur=ramp("#1a1210", "#2a1e1a", "#3c2c26", "#504034"),
    rock=ramp("#140e14", "#1e161e", "#2a202a", "#382c38", "#463848"),
)
THEMES["hollow_circus"]["extra_shaders"] = {
    "motley": MF.mk(ramp("#1a0a14", "#3a1228", "#6a1a3a", "#a02a4a", "#d04a5e"), 0.5, 1.0, 0.1, 0.0,
                    pattern=lambda p, n, i, j, w, h: 0.3 if ((i + j) // 3 + (i - j) // 3) % 2 == 0 else -0.25),
    "paintwood": MF.mk(ramp("#6a5c50", "#867664", "#a4927c", "#c2b098", "#dccab2"), 0.55, 1.0, 0.12, 0.1, stripe=4)}


def top_hat(B):
    hd = B.parts["head"]
    B.add(hd, C(0, 40.4, 0.2, 8.4, 0.8, 8.4), "dark", tag="brim")
    B.add(hd, C(0, 41.2, 0.2, 5.8, 6.4, 5.8), "dark", tag="tophat")
    B.add(hd, C(0, 41.4, 0.2, 6.0, 1.2, 6.0), "cloth", tag="hatband")


def jester_hat(B):
    hd = B.parts["head"]
    for side in (1, -1):
        h = Part("jest%d" % (side > 0), (side * 2.0, 40.0, 0.2), (("z", side * -55),), hd)
        B.add(h, C(side * 2.0, 40.0, 0.2, 2.8, 6.0, 2.8), "motley", tag="jester")
        B.add(h, C(side * 2.0, 46.0, 0.2, 1.6, 1.6, 1.6), "accent", tag="bell")


def mustache(B):
    hd = B.parts["head"]
    B.add(hd, C(0, 35.2, 3.5, 5.0, 1.2, 0.6), "fur", tag="mustache")
    for sx in (-2.8, 2.8):
        B.add(hd, C(sx, 35.8, 3.5, 1.0, 1.6, 0.6), "fur", tag="mustache")


def puppet_strings(B):
    """strings up from its wrists and head to nothing: the hand that worked it is long gone"""
    for nm in ("hand_l", "hand_r", "head"):
        p = B.parts[nm]
        if nm == "head":
            B.add(p, C(0, 41.0, 0.2, 0.3, 14.0, 0.3), "bone", tag="string")
        else:
            x = (1 if nm.endswith("l") else -1) * B.sw
            B.add(p, C(x, 14.0, 0.2, 0.3, 12.0, 0.3), "bone", tag="string")


def tear(B):
    hd = B.parts["head"]
    B.add(hd, C(1.2, 35.0, 3.65, 0.6, 1.6, 0.3), "glow", group="glow", tag="tear")


def ring_coat(B):
    """the Ringmaster's red tailcoat, its tails to the knees, gilt buttons"""
    to = B.parts["torso"]
    for sx in (-2.4, 2.4):
        tl = Part("tail%d" % (sx > 0), (sx, 21.6, -2.6), (("x", 10),), to)
        B.add(tl, C(sx, 9.0, -2.6, 4.0, 12.6, 0.7), "cloth", tag="coattail")
    for k in range(4):
        B.add(to, C(1.6, 22.4 + k * 2.4, 2.75, 0.9, 0.9, 0.3), "accent", tag="button")
    B.add(to, C(0, 26.0, 2.7, 3.0, 7.0, 0.3), "bone", tag="shirtfront")


spec("hollow_circus", "circus_puppet", build=dict(size=0.85, hunch=18, bulk=0.8), legs="bare", hips="leather", torso="leather",
     head="mask", mask_mat="paintwood", hair="cloth", arms="bare", extra=[puppet_strings, tear],
     extra_mats={"skin": "paintwood"}, ent=(0.8, 2.4), stats=dict(hp=16, speed=0.28, dmg=4, armor=0, kb=0))

spec("hollow_circus", "strongman", build=dict(size=1.45, bulk=1.7, hunch=6, arms=1.35, legs=1.15), legs="cloth", hips="leather",
     torso="bare", head="face", hair="dark", arms="bare", bracers="accent", right="hammer",
     right_opt={"size": 1.3, "head": "dark", "head_size": 1.2, "shaft": "metal"}, extra=[mustache],
     ent=(1.5, 3.8), stats=dict(hp=72, speed=0.2, dmg=12, armor=3, kb=0.9))

spec("hollow_circus", "fire_eater", build=dict(size=1.0, hunch=10), legs="cloth", hips="robe", torso="robe", head="mask",
     mask_mat="bone", hair="fur", arms="robe", hand_mat="skin", right="torch", left="torch", extra=[tear],
     ent=(0.9, 2.8), stats=dict(hp=26, speed=0.23, dmg=6, armor=1, kb=0), fire=True)

spec("hollow_circus", "knife_juggler", build=dict(size=0.98, hunch=6, bulk=0.85), legs="cloth", hips="leather", torso="leather",
     head="mask", mask_mat="bone", hair="motley", arms="leather", right="dagger", left="dagger", extra=[jester_hat],
     ent=(0.8, 2.7), stats=dict(hp=24, speed=0.34, dmg=6, armor=1, kb=0))

spec("hollow_circus", "harlequin", build=dict(size=1.15, hunch=4, bulk=1.0), legs="cloth", hips="leather", torso="leather",
     shoulders="leather", head="mask", mask_mat="bone", hair="dark", arms="leather", back="cape", back_opt={"cape": {"mat": "motley"}},
     right="rapier", right_opt={"size": 1.2}, left="dagger", extra=[jester_hat, tear],
     ent=(1.0, 3.1), stats=dict(hp=145, speed=0.27, dmg=10, armor=6, kb=0.5), key=True)

spec("hollow_circus", "ringmaster", build=dict(size=2.2, bulk=1.35, hunch=4), legs="cloth", hips="cloth", torso="leather",
     shoulders="plate", head="face", hair="dark", arms="cloth", right="flail", right_opt={"size": 1.4, "head": "accent"},
     left="staff", left_opt={"top": "orb"}, extra=[top_hat, mustache, ring_coat], texel=1,
     ent=(2.2, 6.4), stats=dict(hp=450, speed=0.23, dmg=15, armor=8, kb=0.9), boss=True)


# ================================================================ the Mirefen Coven (D)

THEMES["mirefen_coven"] = dict(
    metal=ramp("#101010", "#1a1a18", "#262622", "#34342e", "#44443c", "#58584e"),                   # black iron
    cloth=ramp("#141a0c", "#1e2812", "#2a381a", "#384a22", "#4a602e"),
    leather=ramp("#16100a", "#22180e", "#2e2214", "#3c2e1a", "#4a3a22"),
    skin=ramp("#1e2218", "#2c3224", "#3c4432", "#4e5842", "#626e54"),                             # bog-grey
    accent=ramp("#3a3424", "#544c34", "#6e6446", "#8a7e5a", "#a69a70"),                             # bone-twig
    glow=ramp("#2a7a1a", "#44b02a", "#7ce04a", "#b4f88a", "#e4ffd0"),
    fur=ramp("#18240e", "#223214", "#2e421a", "#3c5422", "#4c682c"),                                 # moss
    rock=ramp("#1a1e16", "#24281e", "#30362a", "#3e4636", "#4e5844"),
    bone=ramp("#4a4434", "#6a624a", "#8a8062", "#aa9e7e", "#c8bc9a"),
    eye=ramp("#44b02a", "#7ce04a", "#b4f88a", "#f0ffe0"),
    scale=ramp("#1e1a10", "#2c2616", "#3c3420", "#4e442a", "#625636"),
    crust_cloth=(ramp("#1e3410", "#2c4a16", "#3e621e"), 0.18),
)


def hag_nose(B):
    hd = B.parts["head"]
    B.add(hd, C(0, 34.4, 4.2, 1.2, 1.6, 3.0), "skin", tag="nose")
    B.add(hd, C(0, 33.6, 5.4, 0.8, 1.2, 0.8), "skin", tag="nose")
    B.add(hd, C(0, 30.6, 2.6, 3.6, 3.0, 1.2), "fur", tag="hair_lank")


def antlers(B):
    hd = B.parts["head"]
    for side in (1, -1):
        a = Part("antler%d" % (side > 0), (side * 2.4, 40.0, 0.0), (("z", side * -30),), hd)
        B.add(a, C(side * 2.4, 40.0, 0.0, 1.0, 6.0, 1.0), "accent", tag="antler")
        b = Part("tine%d" % (side > 0), (side * 2.4, 43.0, 0.0), (("z", side * -40),), a)
        B.add(b, C(side * 2.4, 43.0, 0.0, 0.8, 3.6, 0.8), "accent", tag="antler")
        c = Part("tine2%d" % (side > 0), (side * 2.4, 45.0, 0.0), (("z", side * 45),), a)
        B.add(c, C(side * 2.4, 45.0, 0.0, 0.7, 3.0, 0.7), "accent", tag="antler")


def hexbag(B):
    hips = B.parts["hips"]
    B.add(hips, C(-3.4, 14.0, 2.4, 2.4, 3.2, 2.0), "leather", tag="hexbag")
    B.add(hips, C(-3.4, 17.2, 2.4, 0.4, 2.4, 0.4), "leather", tag="cord")
    B.add(hips, C(-3.4, 15.0, 3.45, 1.0, 1.0, 0.3), "glow", group="glow", tag="hexmark")


def bog_weed(B):
    to, hips = B.parts["torso"], B.parts["hips"]
    for k, x in enumerate((-3.6, -0.8, 2.0, 4.0)):
        B.add(to, C(x, 21.0 - k % 2 * 2, 2.8, 0.8, 8.0, 0.4), "fur", tag="weed")
    for k, x in enumerate((-2.0, 1.6)):
        B.add(hips, C(x, 9.0, 3.0, 0.8, 9.0, 0.4), "fur", tag="weed")


def troll_moss(B):
    to = B.parts["torso"]
    B.spikes(to, (0, 32.0, -2.0), 6, 2.2, mat="fur", seed=23, spread=4.0)
    hd = B.parts["head"]
    B.add(hd, C(0, 34.6, 3.6, 2.0, 2.4, 1.6), "skin", tag="nose")
    for sx in (-1.4, 1.4):
        B.add(hd, C(sx, 33.2, 3.6, 0.8, 1.8, 0.8), "bone", tag="tusk")


def cauldron_back(B):
    """Mother Mire carries her cauldron on her back, chained, still boiling"""
    to = B.parts["torso"]
    B.add(to, C(0, 20.0, -7.6, 11.0, 9.0, 9.0), "metal", tag="cauldron")
    B.add(to, C(0, 28.6, -7.6, 12.0, 1.2, 10.0), "metal", tag="cauldron_rim")
    B.add(to, C(0, 28.0, -7.6, 9.0, 0.8, 7.0), "glow", group="glow", tag="brew")
    B.spikes(to, (0, 29.0, -7.6), 4, 2.4, mat="glow", seed=60, spread=2.0)
    for sx in (-4.0, 4.0):
        B.add(to, C(sx, 26.0, -3.2, 0.8, 8.0, 0.8), "metal", tag="chain")


spec("mirefen_coven", "mire_thrall", build=dict(size=0.95, hunch=22, bulk=0.9), legs="bare", hips="cloth", torso="bare",
     head="skull", arms="bare", claws=True, claw_mat="bone", extra=[bog_weed], eye="glow",
     ent=(0.8, 2.6), stats=dict(hp=20, speed=0.24, dmg=5, armor=1, kb=0))

spec("mirefen_coven", "bog_troll", build=dict(size=1.55, bulk=1.7, hunch=24, arms=1.45, legs=1.2), legs="beast", hips="beast",
     torso="gut", gut_mat="fur", shoulders="fur", shoulder_size=1.3, head="face", hair="fur", arms="bare",
     right="club", right_opt={"size": 1.5, "head": "accent", "shaft": "wood"}, extra=[troll_moss], claws=True, claw_hands="l",
     ent=(1.6, 3.8), stats=dict(hp=80, speed=0.19, dmg=12, armor=4, kb=0.8))

spec("mirefen_coven", "hag_sister", build=dict(size=0.95, hunch=26), legs="robe", hips="robe", torso="robe", head="face",
     hair="fur", arms="robe", hand_mat="skin", back="cloak", right="staff", right_opt={"top": "skull"}, left="censer",
     extra=[hag_nose, hexbag], ent=(0.9, 2.5), stats=dict(hp=28, speed=0.21, dmg=5, armor=1, kb=0))

spec("mirefen_coven", "fen_crawler", rig="crawler", size=0.9, leg_len=1.15, body_mat="scale", leg_mat="scale", joint_mat="fur",
     fang_mat="bone", extra=[], ent=(1.4, 0.9), stats=dict(hp=24, speed=0.34, dmg=6, armor=2, kb=0))

spec("mirefen_coven", "coven_matron", build=dict(size=1.25, hunch=14, bulk=1.1), legs="robe", hips="robe", torso="robe",
     shoulders="fur", head="face", hair="fur", arms="robe", hand_mat="skin", back="cloak",
     right="staff", right_opt={"top": "lantern", "size": 1.2}, left="lantern", extra=[hag_nose, antlers, hexbag],
     ent=(1.1, 3.4), stats=dict(hp=150, speed=0.21, dmg=10, armor=6, kb=0.5), key=True)

spec("mirefen_coven", "mother_mire", build=dict(size=2.3, bulk=1.4, hunch=20, arms=1.25), legs="robe", hips="robe",
     torso="robe", shoulders="fur", shoulder_size=1.4, head="face", hair="fur", arms="robe", hand_mat="skin",
     right="scythe", right_opt={"size": 1.1, "head": "metal"}, left="chain_ball", left_opt={"head": "metal"},
     extra=[hag_nose, antlers, cauldron_back, bog_weed], claws=True, texel=1,
     ent=(2.4, 6.2), stats=dict(hp=470, speed=0.21, dmg=16, armor=8, kb=0.9), boss=True)


# ================================================================ hand-built monsters (tools/mobs/<gate>.py) replace the specs above

def _hand_built():
    import importlib
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mobs")
    sys.path.insert(0, here)
    for f in sorted(os.listdir(here)) if os.path.isdir(here) else []:
        if f.endswith(".py") and not f.startswith("_"):
            gate = f[:-3]
            mod = importlib.import_module(gate)
            for n in GATES.pop(gate, []):
                SPECS.pop(n, None)
            for n, s in mod.MOBS.items():
                SPECS[n] = dict(s, gate=gate)
                GATES.setdefault(gate, []).append(n)


_hand_built()
