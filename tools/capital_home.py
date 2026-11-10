"""The player's homestead (pass 16): on the hillside outside Highmourn's north-west wall, where the Terrace Walk's road
climbs out to its lookout (the user's pick, 11/7). Given after the main quest; its stations are the house's (tier 2: no
rarity cap, the better of two rolls).

  the pad       a shelf levelled into the slope at PAD, a dressed retaining wall round its downhill sides, the cut
                behind it faced in stone
  the house     the city's own kit (E:/Ashbound/tools/houses.py): greystone below, timber and plaster above, facing
                the city and the lake. Ground floor: the kitchen (the Cook's Hearth under the chimney, a table, the
                pantry) and the brew corner (the Brewer's Cask, kegs). Upstairs: the alchemy loft (the Alchemist's
                Bench, a potion shelf, books) and the bedroom
  the yard      a path from the door to a stone stair down the retaining wall, a well, a bench
  the fields    two terraces stepped down the hill either side of the stair: farmland in rows with a water channel,
                wheat, carrots, potatoes and beetroot, fenced, an orchard row along the bottom
  the lane      from the stair's foot down to the Terrace Walk's road

    python tools/capital_preview.py home   -> E:/Ashbound/tools/renders/struct/hm_home.obj and its shots
"""
import json
import os
import sys

sys.path.insert(0, "E:/Ashbound/tools")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import houses as HS  # noqa: E402
import structkit as K  # noqa: E402


def honey_solid():
    """structkit's solid() skips anything named "honey" (honey blocks), so the city's honeystone walls never counted as
    walls: the panes in them were joined to nothing. Patched here (E:/Ashbound stays as it is); call before the panes
    are joined."""
    if getattr(K.solid, "honey", False):
        return
    base = K.solid

    def solid(state):
        if state:
            n = state.split("[", 1)[0]
            if "honeystone" in n and not any(k in n for k in ("slab", "stairs", "wall", "pane", "fence")):
                return True
        return base(state)
    solid.honey = True
    K.solid = solid


honey_solid()

PAD = 10                            # the shelf's floor, over the valley floor
HX, HZ, W, D = -238, -120, 15, 17   # the main hall's frame: north-west corner, width, depth (with two jetties)
PAD_BOX = (-243, -124, -209, -98)   # x0, z0, x1, z1 of the levelled shelf
STAIR_X = -231                      # the stone stair down the front wall (in line with the door), the lane below it
FIELDS = [(-246, -95, -235, -82, 4), (-227, -87, -206, -78, 4)]   # x0, z0, x1, z1, floor: either side of the lane
ROAD = (-92, -90)                   # the front road's rows: from the stair's foot east to the city's road
WEST_BOX, WEST_Y = (-300, -128, -244, -99), 18   # the west terrace, up a stair from the shelf: the field and the plot
WEST_STAIR_Z = -106                 # the stair up to it (3 wide), the path west along it
FARM = (-272, -126, -253, -109)     # tilled and watered, left for the party to sow
PLOT = (-298, -126, -276, -101)     # free ground for whatever they build
ORCHARD_Z = -79
ROAD_END = (-192, -95)              # where the Terrace Walk's road ends below the shelf's east side (y 0)
GATE_Z = -111                       # the drive's way into the yard, through the shelf's east wall
GROUND = {}                         # (x, z) -> the ground's new height (capital.py shapes the land to it, CLEAR)
STONE = "stone_bricks"
WALLTOP = "stone_brick_wall[east=low,north=none,south=none,up=true,waterlogged=false,west=low]"
CROPS = ("wheat[age=7]", "carrots[age=7]", "potatoes[age=7]", "beetroots[age=3]")


class Lift:
    """The kit builds at the city's floor; this lifts it onto the shelf."""

    def __init__(self, S, dy):
        self.S, self.dy, self.rnd = S, dy, S.rnd

    def put(self, x, y, z, st):
        # the shelf is cut into the hill: a cell the kit empties must be air in the file, or the hill's own earth
        # comes back there in the game (the cellar stair, the doorways)
        self.S.put(x, y + self.dy, z, "air" if st is None else st)

    def get(self, x, y, z):
        return self.S.get(x, y + self.dy, z)

    def pick(self, *a):
        return self.S.pick(*a)

    def box(self, x0, y0, z0, x1, y1, z1, st):
        self.S.box(x0, y0 + self.dy, z0, x1, y1 + self.dy, z1, st)

    def __getattr__(self, k):
        return getattr(self.S, k)


def level(S, ground, x0, z0, x1, z1, y, face="stone", edges=(), bank=False, keep=()):
    """Cut or fill the land in the box to a floor at y: air above it, earth below, grass on top. The edges named
    ('n', 's', 'e', 'w') get a dressed retaining wall where the land falls away, one course proud as a kerb."""
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            g = ground(x, z)
            edge = (("w" in edges and x == x0) or ("e" in edges and x == x1) or ("n" in edges and z == z0) or ("s" in edges and z == z1))
            GROUND[(x, z)] = y
            for yy in range(y + 1, max(g, y) + 12):        # clear: the shelf's bank may have been laid over a field
                S.put(x, yy, z, "air")
            for yy in range(min(g, y) - 2, y):
                S.put(x, yy, z, STONE if edge and (not bank or yy >= y - 1) else "dirt")
            S.put(x, y, z, STONE if edge else "grass_block[snowy=false]")
            if edge and g < y:
                S.put(x, y + 1, z, WALLTOP)
    # the cut behind: where the land stands over the shelf, a bank laid back at 45 degrees (a dressed footing, then
    # grass), never a cliff
    for x in range(x0 - 14, x1 + 15):
        for z in range(z0 - 14, z1 + 15):
            if x0 <= x <= x1 and z0 <= z <= z1 or any(a <= x <= c and b <= z <= d for a, b, c, d in keep):
                continue
            r = max(x0 - x, x - x1, z0 - z, z - z1)
            g = ground(x, z)
            top = y + 1 + r
            if g <= top:
                continue
            GROUND[(x, z)] = top
            for yy in range(top + 1, g + 1):
                S.put(x, yy, z, "air")
            S.put(x, top, z, STONE if r == 1 else "grass_block[snowy=false]")
            if r == 1:
                S.put(x, top - 1, z, STONE)
    if not bank:
        return
    # the fill in front: where the land falls away below the shelf, a bank of earth laid down at 45 degrees to meet it
    # (the shelf's own rim a low kerb), not a bastion
    for x in range(x0 - 14, x1 + 15):
        for z in range(z0 - 14, z1 + 15):
            if x0 <= x <= x1 and z0 <= z <= z1 or any(a <= x <= c and b <= z <= d for a, b, c, d in keep):
                continue
            r = max(x0 - x, x - x1, z0 - z, z - z1)
            g = ground(x, z)
            top = y - r
            if g >= top:
                continue
            GROUND[(x, z)] = top
            for yy in range(g + 1, top):
                S.put(x, yy, z, "dirt")
            S.put(x, top, z, "grass_block[snowy=false]")


SCULPT = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "renders", "sculpt_pieces.json")))
QTURN = {"north": 0, "east": 1, "south": 2, "west": 3}
DIR = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}
FENCE = "spruce_fence[east=false,north=false,south=false,waterlogged=false,west=false]"
POST = "stripped_spruce_log[axis=y]"


def sculpt(F, name, lx, y, lz, facing="north"):
    """A sculpted prop (tools/sculpt.py) with its footprint's north-west corner at lx, lz in the frame (a frame facing
    south: its own coordinates are the world's turned by nothing), its foot on y, its front looking `facing`."""
    info = SCULPT[name]
    q = QTURN[facing]
    w, h, d = info["size"]

    def turn(x, z):
        for _ in range(q):
            x, z = -z - 1, x
        return x, z
    ends = [turn(0, 0), turn(w - 1, d - 1)]
    mx, mz = min(e[0] for e in ends), min(e[1] for e in ends)
    for cx, cy, cz, idx in info["pieces"]:
        x, z = turn(cx, cz)
        F.put(lx + x - mx, y + cy, lz + z - mz, "ashbound:%s[facing=%s,piece=%d]" % (name, facing, idx))


def bed(F, lx, y, lz, facing, colour):
    """A bed with its head at lx, lz, the head toward `facing`."""
    dx, dz = DIR[facing]
    F.put(lx, y, lz, "%s_bed[facing=%s,occupied=false,part=head]" % (colour, facing))
    F.put(lx - dx, y, lz - dz, "%s_bed[facing=%s,occupied=false,part=foot]" % (colour, facing))


def chest(F, lx, y, lz, facing):
    F.put(lx, y, lz, "chest[facing=%s,type=single,waterlogged=false]" % facing)


def door(F, lx, y, lz, facing, hinge="left", wood="spruce"):
    for k, half in ((0, "lower"), (1, "upper")):
        F.put(lx, y + k, lz, "%s_door[facing=%s,half=%s,hinge=%s,open=false,powered=false]" % (wood, facing, half, hinge))


def partition(F, x0, z0, x1, z1, y0, y1, doors=(), mat="spruce_planks"):
    """An inner wall of planks between stripped-log posts at its ends; doorways (lx, lz) left open two high."""
    for x in range(min(x0, x1), max(x0, x1) + 1):
        for z in range(min(z0, z1), max(z0, z1) + 1):
            end = (x, z) in ((x0, z0), (x1, z1))
            for y in range(y0, y1 + 1):
                if (x, z) in doors and y < y0 + 2:
                    F.put(x, y, z, "air")
                else:
                    F.put(x, y, z, POST if end else mat)


def wall_lamp(F, lx, y, lz, facing):
    F.put(lx, y, lz, "ashbound:wall_lantern[facing=%s]" % facing)


def hang_lamp(F, lx, y, lz):
    F.put(lx, y, lz, "lantern[hanging=true,waterlogged=false]")


def rug(F, x0, z0, x1, z1, y, colour):
    """A carpet on the floor's empty cells only: laid after the furniture it must not eat the chairs' feet (11/7: the
    loft's rug took the armchairs' and the table's bottoms, leaving their tops floating)."""
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            if F.get(x, y, z) in (None, "air", "minecraft:air"):
                F.put(x, y, z, "%s_carpet" % colour)


def ground_floor(F, st):
    """The kitchen across the back (lz 1..5) behind a timbered wall with a wide doorway; the great hall in front."""
    F.box(1, 0, 1, 13, 0, 5, "ashbound:limestone_flagstones")
    for lx in range(1, 14):
        for y in range(1, 5):
            if lx in (6, 7):
                F.put(lx, y, 6, "air" if y < 4 else "stripped_spruce_log[axis=x]")
            else:
                F.put(lx, y, 6, POST if lx in (1, 5, 8, 13) else "spruce_planks")
    # the kitchen: the Cook's Hearth (3 wide) square on the back wall, facing the doorway from the hall, its breast
    # bricked up to the ceiling; the dresser, the sink and the pantry either side, the table to the west
    sculpt(F, "manor_cookhearth", 5, 1, 1, "south")
    for lx in (5, 6, 7):
        for lz in (1, 2):
            F.put(lx, 4, lz, "bricks")
    F.put(1, 1, 1, "barrel[facing=up,open=false]")
    sculpt(F, "welsh_dresser", 2, 1, 1, "south")
    F.put(4, 1, 1, "water_cauldron[level=3]")
    F.put(8, 1, 1, "ashbound:grain_sacks[facing=south]")
    chest(F, 9, 1, 1, "south")
    F.put(10, 1, 1, "ashbound:produce_crate[facing=south]")
    F.put(1, 1, 3, "barrel[facing=east,open=false]")
    F.put(1, 1, 4, "crafting_table")
    F.put(1, 1, 5, "ashbound:produce_crate[facing=east]")
    sculpt(F, "kitchen_worktable", 2, 1, 4, "south")
    sculpt(F, "pot_rack", 2, 4, 4, "south")
    for lx in (2, 3):
        sculpt(F, "bar_stool", lx, 1, 5, "north")
    hang_lamp(F, 9, 4, 3)
    hang_lamp(F, 3, 4, 3)
    # the cellar stair, two wide down the east side: its top step level with the floor at lz 2 (a landing over it at
    # lz 1, clear), five steps south to the cellar's floor; a rail on its open side
    for lx in (12, 13):
        HS.flight(F, st, lx, 6, -4, 5, "north", under=None)
        F.put(lx, 1, 1, "air")
    F.put(11, 1, 1, "air")
    for lz in range(3, 6):
        F.put(11, 1, lz, FENCE)
    # the great hall: the feast table for sixteen under two chandeliers
    rug(F, 3, 8, 10, 11, 1, "red")
    for lx in (1, 2):                               # the stair up, two wide along the west wall, clear at its foot
        HS.flight(F, st, lx, 12, 1, 5, "north")
    for lx in (4, 7):
        sculpt(F, "trestle_table", lx, 1, 9, "north")
        sculpt(F, "guild_chandelier", lx, 3, 8, "north")
    for lx in range(4, 10):
        sculpt(F, "guild_chair", lx, 1, 8, "south")
        sculpt(F, "guild_chair", lx, 1, 11, "north")
    for lz in (9, 10):
        sculpt(F, "guild_chair", 3, 1, lz, "east")
        sculpt(F, "guild_chair", 10, 1, lz, "west")
    # the hearth in the east wall, an armchair either side of it facing across the fire
    for lz in (9, 10, 11):
        for y in range(1, 5):
            F.put(14, y, lz, "bricks")
    for lz in (9, 11):
        for y in range(1, 5):
            F.put(13, y, lz, "bricks")
    F.put(13, 1, 10, "campfire[facing=west,lit=true,signal_fire=false,waterlogged=false]")
    F.put(13, 2, 10, "air")
    F.put(13, 3, 10, "brick_stairs[facing=east,half=top,shape=straight,waterlogged=false]")
    F.put(13, 4, 10, "bricks")
    rug(F, 11, 9, 12, 11, 1, "green")
    sculpt(F, "hearth_armchair", 12, 1, 8, "south")
    sculpt(F, "hearth_armchair", 12, 1, 12, "north")
    # arms by the kitchen wall, a guard of armour either side of the door, the party's chests under the windows
    sculpt(F, "weapon_rack", 3, 1, 7, "south")
    sculpt(F, "armour_stand", 5, 1, 13, "north")
    sculpt(F, "armour_stand", 8, 1, 13, "north")
    for lx in (4, 10, 11, 12):                     # (the stair's foot, lx 1..3, kept clear)
        chest(F, lx, 1, 13, "north")
    for lx in (4, 10):
        wall_lamp(F, lx, 3, 7, "south")
    wall_lamp(F, 5, 3, 13, "north")
    wall_lamp(F, 13, 3, 13, "west")


def first_floor(F, st):
    """A corridor across the middle (lz 7..8) between four bedrooms of two beds; the stair up to the loft runs along
    it."""
    partition(F, 1, 6, 13, 6, 6, 8, doors={(2, 6), (6, 6), (7, 6), (10, 6)})
    partition(F, 5, 1, 5, 5, 6, 8)
    partition(F, 8, 1, 8, 5, 6, 8)
    partition(F, 3, 9, 13, 9, 6, 8, doors={(5, 9), (11, 9)})
    partition(F, 3, 10, 3, 11, 6, 8)
    partition(F, 8, 10, 8, 14, 6, 8)
    for lx in (1, 2):
        F.put(lx, 6, 12, FENCE)                       # over the stairwell's end
    door(F, 2, 6, 6, "north")
    door(F, 10, 6, 6, "north")
    door(F, 5, 6, 9, "south")
    door(F, 11, 6, 9, "south")
    for lx in (6, 7):                                 # the stair to the loft, two wide in its own well, up north
        HS.flight(F, st, lx, 5, 6, 4, "north")
        F.put(lx, 8, 6, "air")                       # no lintel over the well's mouth: it caught heads on the first step
    rug(F, 3, 8, 12, 8, 6, "red")
    wall_lamp(F, 4, 8, 7, "south")
    wall_lamp(F, 10, 8, 8, "north")
    rooms = [  # (bed x's, head lz, head toward, nightstand x, chest lz, chest facing, wardrobe (lx, lz, facing), washstand, rug, colour, lamp)
        ((1, 3), 1, "north", 2, 3, "south", (4, 1, "west"), (4, 4, "west"), (1, 4, 3, 5), "red", (2, 3)),
        ((10, 12), 1, "north", 11, 3, "south", (13, 1, "west"), (9, 4, "east"), (10, 4, 12, 5), "blue", (11, 3)),
        ((4, 6), 14, "south", 5, 12, "north", (1, 13, "east"), (7, 10, "west"), (4, 11, 6, 11), "green", (5, 12)),
        ((10, 12), 14, "south", 11, 12, "north", (13, 10, "west"), (9, 10, "east"), (10, 11, 12, 11), "yellow", (11, 12)),
    ]
    for xs, hz, toward, nx, cz, cf, wr, ws, rg, colour, lamp in rooms:
        rug(F, rg[0], rg[1], rg[2], rg[3], 6, colour)
        for x in xs:
            bed(F, x, 6, hz, toward, colour)
            chest(F, x, 6, cz, cf)
        sculpt(F, "nightstand", nx, 6, hz, "south" if toward == "north" else "north")
        sculpt(F, "wardrobe", wr[0], 6, wr[1], wr[2])
        sculpt(F, "washstand", ws[0], 6, ws[1], ws[2])
        hang_lamp(F, lamp[0], 8, lamp[1])


def loft(F, st):
    """Under the roof: the alchemy room along the north gable, the library along the south one, the party's chests
    down the sides; a rail round the stair."""
    for lz in (3, 4, 5):                              # the rail round the stair's well
        F.put(5, 10, lz, FENCE)
        F.put(8, 10, lz, FENCE)
    for lx in (6, 7):
        F.put(lx, 10, 6, FENCE)
    shelf = {1: "potion_shelf", 2: "potion_shelf", 3: "candle_rack", 13: "potion_shelf"}
    for lx, n in shelf.items():
        F.put(lx, 10, 1, "ashbound:%s[facing=south]" % n)
    sculpt(F, "manor_alembic", 10, 10, 1, "south")      # in sight from the stair's head
    F.put(9, 10, 1, "ashbound:book_pile[facing=south]")
    sculpt(F, "master_desk", 2, 10, 3, "south")
    sculpt(F, "school_chair", 2, 10, 4, "north")
    rug(F, 1, 4, 4, 5, 10, "purple")
    for lx in (2, 13):                              # on the timbers between the gable's windows (clear of the still)
        wall_lamp(F, lx, 11, 1, "south")
    # the library and its reading corner
    for lx in (4, 8, 12):
        sculpt(F, "scroll_shelf", lx, 10, 15, "north")
    sculpt(F, "round_table", 6, 10, 12, "north")
    sculpt(F, "hearth_armchair", 5, 10, 12, "east")
    sculpt(F, "hearth_armchair", 8, 10, 13, "west")
    F.put(2, 10, 15, "ashbound:book_pile[facing=north]")
    rug(F, 4, 11, 9, 14, 10, "brown")
    wall_lamp(F, 1, 11, 15, "north")
    # the party's chests down both sides
    for lz in range(9, 13):
        chest(F, 1, 10, lz, "east")
        chest(F, 13, 10, lz, "west")
    for lz in (8, 12):                              # lamps on chains from the ridge
        top = HS.roof_top(F, 7, lz)
        hang_lamp(F, 7, 12, lz)
        for y in range(13, top):
            F.put(7, y, lz, "chain[axis=y,waterlogged=false]")


def cellar(F, st):
    """Under the whole hall, down from the kitchen: keg racks and a wall of casks, wine in racks, the larder, a tasting
    table under the lamps, the party's chests along the east wall."""
    F.box(0, -5, 0, F.w - 1, -1, D - 3, STONE)
    F.box(1, -4, 1, F.w - 2, -1, D - 4, "air")
    F.box(1, -5, 1, F.w - 2, -5, D - 4, "ashbound:limestone_flagstones")
    sculpt(F, "keg_rack", 1, -4, 1, "south")
    sculpt(F, "keg_rack", 6, -4, 1, "south")
    F.put(10, -4, 1, "barrel[facing=up,open=false]")
    F.put(11, -4, 1, "barrel[facing=up,open=false]")
    for lz in list(range(3, 7)) + list(range(8, 12)):
        for y in ((-4, -3) if lz < 7 else (-4,)):
            sculpt(F, "cellar_barrel", 1, y, lz, "east")
    for lx in range(2, 7):
        for y in (-4, -3):
            sculpt(F, "wine_rack", lx, y, 13, "north")
    larder = {8: "ashbound:produce_crate[facing=north]", 9: "ashbound:grain_sacks[facing=north]", 10: "ashbound:grain_sacks[facing=north]",
              11: "ashbound:produce_crate[facing=north]", 12: "barrel[facing=up,open=false]"}
    for lx, b in larder.items():
        F.put(lx, -4, 13, b)
    for lz in range(9, 13):
        chest(F, 13, -4, lz, "west")
        chest(F, 12, -4, lz, "west") if lz in (11, 12) else None
    sculpt(F, "trestle_table", 5, -4, 6, "north")
    for lz in (6, 7):
        sculpt(F, "bar_stool", 4, -4, lz, "east")
        sculpt(F, "bar_stool", 8, -4, lz, "west")
    for lx, lz in ((6, 7), (3, 3), (10, 3), (3, 10), (10, 10)):
        F.put(lx, -1, lz, "lantern[hanging=true,waterlogged=false]")


def house(S):
    """The manor: the main hall (15 wide, three storeys and a cellar, beds for eight) and the brewhouse wing on its east
    side, one front door."""
    L = Lift(S, PAD)
    F = HS.Frame(L, HX, HZ, W, D, "south")
    st = HS.Style(L, grand=True, col="ochre_plaster", roof="ashbound:clay_roof_tile", shutter="ashbound:green_shutter",
                  door="dark_oak_door", rug="red_carpet", bed="red_bed", wood="spruce", flowers=True)
    w, g = W, D - 3                               # the ground floor's front wall (lz 14); two jetties beyond it
    plank = "%s_planks" % st.wood
    F.box(0, 0, 0, w - 1, 0, g, plank)
    HS.stone_storey(F, st, 1, g, front_windows=(1, 2, 3, 4, 10, 11, 12, 13))
    F.box(1, 5, 1, w - 2, 5, g + 1, plank)
    for lx in range(0, w, 2):
        F.put(lx, 4, g + 1, HS.stairs("stone_brick", "north", "top"))
    HS.framed_storey(F, st, 5, g + 1)
    F.box(1, 9, 1, w - 2, 9, g + 2, plank)
    for lx in range(0, w, 2):
        F.put(lx, 8, g + 2, HS.stairs(st.wood, "north", "top"))
    HS.framed_storey(F, st, 9, g + 2)
    HS.gable_roof(F, st, 12, g + 2, steep=1)
    HS.front_door(F, st, 7, g)
    door(F, 6, 1, g, "north", hinge="right", wood="dark_oak")
    HS.chimney(F, 6, 0, 4, HS.roof_top(F, 6, 0) + 2)     # the Cook's Hearth's flue, in the back wall
    HS.chimney(F, w - 1, 10, 5, HS.roof_top(F, w - 1, 10) + 2)
    cellar(F, st)
    ground_floor(F, st)
    first_floor(F, st)
    loft(F, st)
    brewhouse(L)
    for y in (1, 2):                               # the doorway to the brewhouse
        F.put(w - 1, y, 7, "air")
    F.put(w - 1, 3, 7, "ashbound:greystone")
    return F


def brewhouse(L):
    """The wing on the hall's east side, its door from the hall: the Brewer's Cask and the cooper's bench, a keg rack,
    the grain and a table to taste at; a hay loft over it."""
    F = HS.Frame(L, HX + W, HZ + 5, 9, 11, "south")
    st = HS.Style(L, col="ochre_plaster", roof="ashbound:clay_roof_tile", shutter="ashbound:green_shutter",
                  door="spruce_door", wood="spruce", flowers=True)
    g = 9                                          # its front flush with the hall's; no door of its own
    plank = "%s_planks" % st.wood
    F.box(0, 0, 0, 8, 0, g, "ashbound:limestone_flagstones")
    HS.stone_storey(F, st, 1, g, front_windows=(2, 4, 6))
    F.box(1, 5, 1, 7, 5, g + 1, plank)
    HS.framed_storey(F, st, 5, g + 1)
    HS.gable_roof(F, st, 8, g + 1, steep=1, ridge_x=True)
    sculpt(F, "manor_brewery", 3, 1, 1, "south")       # straight ahead through the doorway from the hall
    for lx in (3, 4, 5):
        for lz in (1, 2):
            F.put(lx, 4, lz, "bricks")
    for lz in (2, 3):
        sculpt(F, "cellar_barrel", 7, 1, lz, "west")
    for lz, b in ((4, "ashbound:grain_sacks[facing=east]"), (5, "ashbound:produce_crate[facing=east]"), (6, "ashbound:grain_sacks[facing=east]")):
        F.put(1, 1, lz, b)
    sculpt(F, "round_table", 3, 1, 5, "north")
    for lx, lz in ((2, 6), (5, 5), (4, 7)):
        sculpt(F, "bar_stool", lx, 1, lz, "north")
    for lx in (2, 3):
        chest(F, lx, 1, 8, "north")
    for lx in (5, 6):
        F.put(lx, 1, 8, "barrel[facing=up,open=false]")
    hang_lamp(F, 4, 4, 3)
    hang_lamp(F, 4, 4, 6)
    for lx in (1, 2, 6, 7):                         # the hay loft (round the kettle's flue)
        for lz in (1, 2):
            F.put(lx, 6, lz, "hay_block[axis=x]")
    for lx in (1, 2, 6, 7):
        F.put(lx, 7, 1, "hay_block[axis=x]")
    for y in (1, 2):                               # its side of the doorway from the hall
        F.put(0, y, 2, "air")
    return F


def stone_face(S, x0, z0, x1, z1, y0, y1):
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            for y in range(y0, y1 + 1):
                S.put(x, y, z, STONE)


def fence_ring(S, x0, z0, x1, z1, y, gates=()):
    """A spruce fence round the box at y; gates (x, z, facing) set into it. The export joins the posts."""
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            if x in (x0, x1) or z in (z0, z1):
                S.put(x, y, z, "spruce_fence[east=false,north=false,south=false,waterlogged=false,west=false]")
    for x, z, facing in gates:
        S.put(x, y, z, "spruce_fence_gate[facing=%s,in_wall=false,open=false,powered=false]" % facing)


def lamp_post(S, x, y, z):
    for k in (1, 2):
        S.put(x, y + k, z, "spruce_fence[east=false,north=false,south=false,waterlogged=false,west=false]")
    S.put(x, y + 3, z, "lantern[hanging=false,waterlogged=false]")


def farm(S, y):
    """The kitchen garden: a fence with a double gate to the path and one toward the house, two paths crossing in
    the middle, four beds edged in logs with a channel down each; wheat, carrots and potatoes, beetroot, and one bed
    tilled and left for the party. A scarecrow, hives on posts along the back, flowers by the fence."""
    fx0, fz0, fx1, fz1 = FARM
    cx, cz = (fx0 + fx1) // 2, (fz0 + fz1) // 2
    for x in range(fx0 + 1, fx1):
        for z in range(fz0 + 1, fz1):
            S.put(x, y, z, "dirt_path" if x in (cx, cx + 1) or z in (cz, cz + 1) else "grass_block[snowy=false]")
    beds = [((fx0 + 1, fz0 + 1, cx - 1, cz - 1), ("wheat[age=7]",)),
            ((cx + 2, fz0 + 1, fx1 - 1, cz - 1), ("carrots[age=7]", "potatoes[age=7]")),
            ((fx0 + 1, cz + 2, cx - 1, fz1 - 1), ("beetroots[age=3]",)),
            ((cx + 2, cz + 2, fx1 - 1, fz1 - 1), ())]
    for (x0, z0, x1, z1), crops in beds:
        mid = (z0 + z1) // 2
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                if x in (x0, x1) or z in (z0, z1):              # the log edging, laid along its side
                    S.put(x, y, z, "stripped_spruce_log[axis=%s]" % ("x" if z in (z0, z1) else "z"))
                elif z == mid:
                    S.put(x, y, z, "water")
                else:
                    S.put(x, y, z, "farmland[moisture=7]")
                    if crops:
                        S.put(x, y + 1, z, crops[(z - z0) % len(crops)])
    sx, sz = fx1 - 3, fz0 + 2                                     # the scarecrow in the carrot bed
    sculpt(S, "field_scarecrow", sx, y + 1, sz, "south")
    fence_ring(S, fx0, fz0, fx1, fz1, y + 1, gates=[(cx, fz1, "south"), (cx + 1, fz1, "south"),
                                                   (fx1, cz, "east"), (fx1, cz + 1, "east")])
    for x in (cx, cx + 1):                                        # the gate's path out to the main one
        S.put(x, y, fz1 + 1, "dirt_path")
    lamp_post(S, cx - 1, y, fz1 + 1)
    lamp_post(S, cx + 2, y, fz1 + 1)
    # the path from the east gate round to the stair's head, past the shed
    for x in range(fx1 + 1, fx1 + 5):
        for z in (cz, cz + 1):
            S.put(x, y, z, "dirt_path")
    for z in range(min(cz, FARM[1] + 6), WEST_STAIR_Z - 1):
        for x in (fx1 + 3, fx1 + 4):
            S.put(x, y, z, "dirt_path")
    # hives on posts along the back, flowers between them
    flowers = ("poppy", "cornflower", "oxeye_daisy", "allium", "azure_bluet", "dandelion")
    for i, x in enumerate(range(fx0, fx1 + 1)):
        z = fz0 - 1
        if (x - fx0) % 6 == 3:
            S.put(x, y + 1, z, "stripped_spruce_log[axis=y]")
            S.put(x, y + 2, z, "beehive[facing=south,honey_level=0]")
        else:
            S.put(x, y + 1, z, flowers[i % len(flowers)])
    for i, x in enumerate(range(fx0, fx1 + 1)):                  # and along the front, either side of the gate
        if x not in (cx - 1, cx, cx + 1, cx + 2) and i % 2 == 0:
            S.put(x, y + 1, fz1 + 1, flowers[(i + 3) % len(flowers)])


def shed(S, y):
    """The tool shed by the garden's east gate: posts and planks under a little gable of spruce, a door on the path;
    the tools, a chest and barrels inside, hay stacked by it, the handcart parked by it."""
    x0, z0, x1, z1 = FARM[2] + 1, FARM[1], FARM[2] + 6, FARM[1] + 5
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            S.put(x, y, z, "spruce_planks")
            edge = x in (x0, x1) or z in (z0, z1)
            corner = x in (x0, x1) and z in (z0, z1)
            for k in (1, 2, 3):
                S.put(x, y + k, z, "stripped_spruce_log[axis=y]" if corner else "spruce_planks" if edge else "air")
    zm = (z0 + z1) / 2.0
    for z in range(z0 - 1, z1 + 2):                               # the gable, its ridge along x
        rise = int(min(z - (z0 - 1), (z1 + 1) - z))
        facing = "south" if z < zm else "north"
        for x in range(x0 - 1, x1 + 2):
            S.put(x, y + 3 + rise, z, "spruce_stairs[facing=%s,half=bottom,shape=straight,waterlogged=false]" % facing)
        for x in (x0, x1):                                        # the gable ends filled in
            for k in range(4, 3 + rise):
                S.put(x, y + k, z, "spruce_planks")
    for z in (z0 + 2, z0 + 3):                                    # windows in the ends
        S.put(x0, y + 2, z, "glass_pane[east=false,north=true,south=true,waterlogged=false,west=false]")
        S.put(x1, y + 2, z, "glass_pane[east=false,north=true,south=true,waterlogged=false,west=false]")
    dx = x0 + 2
    for k, half in ((1, "lower"), (2, "upper")):
        S.put(dx, y + k, z1, "spruce_door[facing=north,half=%s,hinge=left,open=false,powered=false]" % half)
    sculpt(S, "tool_wall", x0 + 1, y + 1, z0 + 1, "south")
    S.put(x0 + 3, y + 1, z0 + 1, "chest[facing=south,type=single,waterlogged=false]")
    S.put(x0 + 4, y + 1, z0 + 1, "barrel[facing=up,open=false]")
    S.put(x0 + 4, y + 1, z0 + 3, "composter[level=0]")
    S.put(x0 + 1, y + 1, z0 + 3, "ashbound:grain_sacks[facing=east]")
    S.put(x0 + 2, y + 3, z0 + 2, "lantern[hanging=true,waterlogged=false]")
    for z in (z0, z0 + 1):                                         # hay against the east end
        S.put(x1 + 1, y + 1, z, "hay_block[axis=y]")
    S.put(x1 + 1, y + 2, z0, "hay_block[axis=y]")
    sculpt(S, "farm_handcart", x1 + 1, y + 1, z0 + 3, "east")


def west(S, ground):
    """The west terrace, up a stone stair from the house's shelf: the field (tilled and watered, the party sows it)
    and the free plot beyond it, fenced at the corners, for whatever they build."""
    x0, z0, x1, z1 = WEST_BOX
    y = WEST_Y
    # the retaining wall where the terrace stands over the house's shelf, a stair up through it
    stone_face(S, x1, PAD_BOX[1], x1, z1, PAD + 1, y)
    for z in range(PAD_BOX[1], z1 + 1):
        if not WEST_STAIR_Z - 1 <= z <= WEST_STAIR_Z + 1:
            S.put(x1, y + 1, z, WALLTOP)
    n = y - PAD - 1
    for i in range(n):                              # climbing west from the shelf
        x = x1 - i
        for dz in (-1, 0, 1):
            z = WEST_STAIR_Z + dz
            for yy in range(PAD - 2, PAD + 1 + i):
                S.put(x, yy, z, STONE)
            S.put(x, PAD + 1 + i, z, "stone_brick_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]")
            for yy in range(PAD + 2 + i, y + 5):
                S.put(x, yy, z, "air")
        for dz in (-2, 2):
            stone_face(S, x, WEST_STAIR_Z + dz, x, WEST_STAIR_Z + dz, PAD + 1, y)
            S.put(x, y + 1, WEST_STAIR_Z + dz, WALLTOP)
    # the path from the stair's head to the plot
    for x in range(PLOT[2] + 1, x1 - n + 1):
        for dz in (-1, 0, 1):
            S.put(x, y, WEST_STAIR_Z + dz, "dirt_path")
    farm(S, y)
    shed(S, y)
    # the plot: open lawn, a post with a lantern at each corner
    px0, pz0, px1, pz1 = PLOT
    for x, z in ((px0, pz0), (px1, pz0), (px0, pz1), (px1, pz1)):
        S.put(x, y + 1, z, "spruce_fence[east=false,north=false,south=false,waterlogged=false,west=false]")
        S.put(x, y + 2, z, "spruce_fence[east=false,north=false,south=false,waterlogged=false,west=false]")
        S.put(x, y + 3, z, "lantern[hanging=false,waterlogged=false]")


def yard(S, ground):
    door_x = HX + 7
    for z in range(HZ + D, PAD_BOX[3]):             # the path from the door to the stair's head
        for dx in (-1, 0, 1):
            S.put(door_x + dx, PAD, z, "dirt_path")
    # the stair down the front wall to the fields' level, and the lane on down to the road
    y, z = PAD, PAD_BOX[3]
    while y > FIELDS[0][4]:
        for dx in (-1, 0, 1):
            S.put(STAIR_X + dx, y, z, "stone_brick_stairs[facing=north,half=bottom,shape=straight,waterlogged=false]")
            for yy in range(y + 1, y + 4):
                S.put(STAIR_X + dx, yy, z, "air")
            for yy in range(y - 3, y):
                S.put(STAIR_X + dx, yy, z, STONE)
        for dx in (-2, 2):
            S.put(STAIR_X + dx, y, z, STONE)
            S.put(STAIR_X + dx, y + 1, z, WALLTOP)
        y -= 1
        z += 1
    for zz in range(z, (FIELDS[0][1] + FIELDS[0][3]) // 2 + 3):   # the farm lane to the west field's gate (the road turns off east)
        gy = FIELDS[0][4]
        for dx in (-1, 0, 1):
            S.put(STAIR_X + dx, gy, zz, "dirt_path")
            GROUND[(STAIR_X + dx, zz)] = gy
            for yy in range(gy + 1, gy + 4):
                S.put(STAIR_X + dx, yy, zz, "air")
    # a well and a bench in the yard
    wx, wz = HX + W + 12, HZ + 8
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            S.put(wx + dx, PAD + 1, wz + dz, "water" if dx == dz == 0 else "cobblestone_wall[east=low,north=low,south=low,up=true,waterlogged=false,west=low]"
                  if (dx, dz) != (0, 0) else STONE)
    S.put(wx, PAD, wz, "water")
    for dx, dz in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        S.put(wx + dx, PAD + 2, wz + dz, "spruce_fence[east=false,north=false,south=false,waterlogged=false,west=false]")
        S.put(wx + dx, PAD + 3, wz + dz, "spruce_slab[type=bottom,waterlogged=false]")
    for dx in (-1, 0, 1):
        S.put(wx + dx, PAD + 3, wz, "spruce_slab[type=bottom,waterlogged=false]")
    for k in range(3):
        S.put(HX - 3, PAD + 1, HZ + 8 + k, "spruce_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]")


def road(S, ground):
    """The front road: from the stair's foot (y 4) east along the foot of the shelf's bank, level until past the
    shelf, then down four broad steps to where the Terrace Walk's road ends. Its banks laid back at 45 degrees (cut
    into the shelf's bank above it, filled down to the field below), lanterns on posts along the field side."""
    z0, z1 = ROAD
    x0 = STAIR_X + 2
    ex, ez = ROAD_END
    steps = {PAD_BOX[2] + 2: 3, PAD_BOX[2] + 4: 2, PAD_BOX[2] + 6: 1, PAD_BOX[2] + 8: 0}   # x where it drops a step
    h = FIELDS[0][4]
    infield = lambda x, z: any(a <= x <= c and b <= z <= d for a, b, c, d, _ in FIELDS)
    for x in range(x0, ex + 4):
        up = x in steps
        h = steps.get(x, h)
        for z in range(z0, z1 + 1):
            for yy in range(h - 3, h):
                S.put(x, yy, z, "dirt")
            S.put(x, h, z, "dirt_path")
            GROUND[(x, z)] = h
            for yy in range(h + 1, h + 8):
                S.put(x, yy, z, "air")
            if up:                                     # the step up toward the house (west)
                S.put(x, h + 1, z, "stone_brick_stairs[facing=west,half=bottom,shape=straight,waterlogged=false]")
        for k in range(8):                             # the bank above it (north), cut back at 45 degrees
            z = z0 - 1 - k
            g = GROUND.get((x, z), ground(x, z))
            if g > h + 1 + k:
                GROUND[(x, z)] = h + 1 + k
                for yy in range(h + 2 + k, g + 1):
                    S.put(x, yy, z, "air")
                S.put(x, h + 1 + k, z, "grass_block[snowy=false]")
            elif k == 0 and g < h:                      # a verge level with it
                for yy in range(g, h):
                    S.put(x, yy, z, "dirt")
                S.put(x, h, z, "grass_block[snowy=false]")
                GROUND[(x, z)] = h
        for k in range(8):                             # and below it (south), filled down at 45 degrees
            z = z1 + 1 + k
            if infield(x, z):
                break
            g = GROUND.get((x, z), ground(x, z))
            top = h - k
            if g >= top:
                break
            for yy in range(g, top):
                S.put(x, yy, z, "dirt")
            S.put(x, top, z, "grass_block[snowy=false]")
            GROUND[(x, z)] = top
        if (x - x0) % 9 == 3 and not up:
            lamp_post(S, x, h, z1 + 1)
    # joined to the city's road: an apron of path over its end
    for x in range(ex - 6, ex + 4):
        for z in range(ez - 1, z0):
            if GROUND.get((x, z), ground(x, z)) <= 1:
                S.put(x, 0, z, "dirt_path")
                GROUND[(x, z)] = 0
                for yy in range(1, 6):
                    S.put(x, yy, z, "air")


def fields(S, ground):
    """Two terraces down the hill either side of the lane: farmland in rows with water channels, crops, a fence
    round each with a gate on the lane and a path through the middle to it."""
    fence = "spruce_fence[east=%s,north=%s,south=%s,waterlogged=false,west=%s]"
    for i, (x0, z0, x1, z1, fy) in enumerate(FIELDS):
        level(S, ground, x0, z0, x1, z1, fy, edges=("s", "e") if i == 0 else ("s", "e", "w"), keep=(PAD_BOX, WEST_BOX))
        pz = (z0 + z1) // 2 + 1                       # the path's row
        gx = (x0 + x1) // 2                           # (the east field: a path in from its north gate, off the road)
        for x in range(x0 + 1, x1):
            for z in range(z0 + 1, z1):
                if z == pz or (i == 1 and x in (gx, gx + 1) and z < pz):
                    S.put(x, fy, z, "dirt_path")
                elif abs(z - pz) % 4 == 2:            # a channel two rows either side of the path, then every four:
                    S.put(x, fy, z, "water")          # every crop within reach of water
                else:
                    S.put(x, fy, z, "farmland[moisture=7]")
                    S.put(x, fy + 1, z, CROPS[((z - z0) // 5 + i) % len(CROPS)])
        for x in range(x0, x1 + 1):
            for z in (z0, z1):
                if x == STAIR_X:
                    continue
                S.put(x, fy + 1 + (1 if S.get(x, fy + 1, z) == WALLTOP else 0), z, fence % ("true" if x < x1 else "false", "false", "false", "true" if x > x0 else "false"))
        for z in range(z0 + 1, z1):
            for x in (x0, x1):
                S.put(x, fy + 1, z, fence % ("false", "true", "true", "false"))
        if i == 1:                                     # the east field: a double gate on the road, the path up to it
            for x in (gx, gx + 1):
                S.put(x, fy + 1, z0, "spruce_fence_gate[facing=north,in_wall=false,open=false,powered=false]")
                for z in range(z0 - 1, ROAD[1]):
                    for k in range(fy - 3, fy):
                        S.put(x, k, z, "dirt")
                    S.put(x, fy, z, "dirt_path")
                    GROUND[(x, z)] = fy
                    for k in range(fy + 1, fy + 5):
                        S.put(x, k, z, "air")
            continue
        gx = x1 if x1 < STAIR_X else x0                # the side on the lane
        S.put(gx, fy + 1, pz, "spruce_fence_gate[facing=%s,in_wall=false,open=false,powered=false]" % ("east" if gx == x1 else "west"))
        lane_y = FIELDS[0][4]
        step = 1 if gx == x1 else -1
        x, yy = gx + step, fy
        while abs(x - STAIR_X) > 1:                    # from the gate to the lane: level ground, or steps up to it
            for z in range(z0 + 1, z1):
                for k in range(yy + 1, yy + 12):
                    S.put(x, k, z, "air")
                S.put(x, yy, z, "dirt_path" if z == pz else "grass_block[snowy=false]")
                for k in range(yy - 3, yy):
                    S.put(x, k, z, "dirt")
            if yy < lane_y:
                S.put(x, yy + 1, pz, "stone_brick_stairs[facing=%s,half=bottom,shape=straight,waterlogged=false]" % ("west" if step > 0 else "east"))
                yy += 1
            x += step


def orchard(S, ground):
    """A row of small fruit trees along the fields' foot."""
    for i, x in enumerate(range(-242, -205, 8)):
        g = ground(x, ORCHARD_Z)
        for y in range(g + 1, g + 5):
            S.put(x, y, ORCHARD_Z, "oak_log[axis=y]")
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                for dy in (3, 4, 5):
                    r = abs(dx) + abs(dz)
                    if r <= (3 if dy == 4 else 2) and not (dx == dz == 0 and dy < 5):
                        S.put(x + dx, g + dy, ORCHARD_Z + dz, "oak_leaves[distance=1,persistent=true,waterlogged=false]"
                              if (x + dx + dz + dy + i) % 7 else "ashbound:wildwood_leaves_sunlit[distance=1,persistent=true,waterlogged=false]")


def near(x, z, m=16):
    """In the homestead's ground or its cut banks (the city's trees keep off it)."""
    boxes = [PAD_BOX, WEST_BOX, (STAIR_X, ROAD[0], ROAD_END[0], ROAD[1])] + [f[:4] for f in FIELDS]
    return any(a - m <= x <= c + m and b - m <= z <= d + m for a, b, c, d in boxes)


def build(S, ground):
    """ground(x, z): the land's height there (capital_land's), for cutting and filling round the homestead."""
    level(S, ground, *WEST_BOX, WEST_Y, edges=("s", "w"), keep=(PAD_BOX,) + tuple(f[:4] for f in FIELDS))
    level(S, ground, *PAD_BOX, PAD, edges=("s", "e"), bank=True, keep=(WEST_BOX,))
    house(S)
    west(S, ground)
    yard(S, ground)
    fields(S, ground)
    road(S, ground)
    print("  manor: %d stub panes framed" % HS.frame_panes(S))
