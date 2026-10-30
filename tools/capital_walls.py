"""Highmourn's walls: a roofed gallery wall between tall spired towers round the south of the valley, the gatehouse
with its barbican and drawbridge over the moat, the water gate where the river leaves, and at each end a spur wall
climbing the slope to a hill tower.

The look aimed for (fantasy-gothic city walls, the way the good Minecraft builds do them):
    vertical: slender square and octagonal towers 3-4 times as tall as they're wide, each under a dark spire 3 times
    as tall as it's wide, with gabled dormers on its faces and little spired turrets at its corners;
    depth everywhere: a stepped plinth, buttresses on a steady rhythm, recessed blind-arch panels with a slit in each,
    the gallery jutting out on corbels, framed lancet windows set back in their reveals;
    texture: dark deepslate footing, a grey body blended in patches of greystone, stone bricks, tuff and andesite,
    pale stone only where it's dressed (string courses, window frames, the arch's rings), dark slate roofs;
    weathered: moss and damp streaks low down, vines off the corbels.
"""
import math

import capital_land as L

S = put = pick = None        # set by capital.py (its Build)

G, MG = "deepslate_bricks", "cracked_deepslate_bricks"
GW, GSL = "polished_blackstone_wall", "deepslate_brick_slab"
LIME, CRL, MOL = "deepslate_tiles", "cracked_deepslate_tiles", "deepslate_tiles"      # dressed trim: tiles in the brick
CARVED, FLAG, PILLAR = "chiseled_deepslate", "ashbound:limestone_flagstones", "ashbound:limestone_pillar"
GILT = "ashbound:gilded_tiles"
ROOF, ROOFB = "polished_blackstone_brick", "polished_blackstone_bricks"
DARK = "light_gray_stained_glass"           # a window's glass, set back in its reveal
PANE = "light_gray_stained_glass_pane"
WATER = "water[level=0]"
LANTERN = "lantern[hanging=false,waterlogged=false]"
HANG = "lantern[hanging=true,waterlogged=false]"
BARS = "iron_bars[east=false,north=false,south=false,west=false,waterlogged=%s]"

WALK = 25                    # the gallery's floor
EAVE = 31                    # the gallery roof's eaves (ridge 6 higher)
BAY = 9                      # buttress spacing along the curtain
A_END = math.acos(-58 / L.RZ)     # the wall's ends, on the ellipse (angle from due south)
N_EACH = 7                   # towers each side of the gate
GATE_HALF = 0.075            # the gatehouse's span either side of due south (radians)

noise = L.noise


# ================================================================ small helpers

def stairs(mat, facing, half="bottom"):
    return "%s_stairs[facing=%s,half=%s,shape=straight,waterlogged=false]" % (mat, facing, half)


def slab(mat, typ="bottom"):
    return "%s_slab[type=%s,waterlogged=false]" % (mat, typ)


def toward(dx, dz):
    if abs(dx) > abs(dz):
        return "east" if dx > 0 else "west"
    return "south" if dz > 0 else "north"


OPP = {"north": "south", "south": "north", "east": "west", "west": "east"}


def seat(x, z, y):
    """The first free cell over what the column holds at or under y: a finial goes there, never on air."""
    while y > 0 and S.get(x, y - 1, z) is None:
        y -= 1
    return y


def vine(x, y, z, wall_dir):
    """A vine at x, y, z clinging to the block on its wall_dir side."""
    sides = {k: "false" for k in ("east", "north", "south", "west")}
    sides[wall_dir] = "true"
    put(x, y, z, "vine[east=%s,north=%s,south=%s,up=false,west=%s]" % (sides["east"], sides["north"], sides["south"], sides["west"]))


def stone(x, y, z, top=EAVE):
    """The wall's stone: dark deepslate bricks in one tone, some tiles and cracked bricks through it."""
    if y < 10:
        return pick(("deepslate_bricks", 10), ("cracked_deepslate_bricks", 2), ("deepslate_tiles", 2))
    return pick(("deepslate_bricks", 16), ("deepslate_tiles", 3), ("cracked_deepslate_bricks", 1), ("polished_deepslate", 1))


def roof_stair(facing):
    """A roof step whose high side faces `facing` (toward the ridge)."""
    return stairs(ROOF, facing)


def slate():
    return pick((ROOFB, 10), ("cracked_polished_blackstone_bricks", 1))


# ================================================================ the wall's line

def ell_pt(a):
    return L.RX * math.sin(a), L.RZ * math.cos(a)


# k -> (plan, half width, eaves height): square where the wall runs near an axis, octagonal on the diagonals
TOWER_KINDS = {1: ("square", 6, 50), 2: ("oct", 5, 42), 3: ("oct", 6, 56), 4: ("oct", 5, 44), 5: ("square", 6, 50),
               6: ("oct", 5, 42), 7: ("oct", 7, 58)}


def tower_angles():
    """(angle, plan, eaves height, side, index, half width) for each tower, out from the gate both ways."""
    out = []
    for k in range(1, N_EACH + 1):
        f = (k / N_EACH) ** 0.95
        a = GATE_HALF + (A_END - GATE_HALF) * f
        plan, hw, h0 = TOWER_KINDS[k]
        for sgn in (-1, 1):
            j = 0.02 * L.snoise(k * 7.0, sgn * 3.0, 1.3, 91)
            h = h0 + round(3 * L.snoise(k * 5.0, sgn, 1.1, 92))
            out.append((sgn * (a + j), plan, h, sgn, k, hw))
    return out


TOWERS = tower_angles()


def wall_points():
    """The curtain's corners, west end to east end: the towers, and the gatehouse's two sides in the middle."""
    pts = sorted([(t[0], ell_pt(t[0])) for t in TOWERS] + [(-GATE_HALF, ell_pt(-GATE_HALF)), (GATE_HALF, ell_pt(GATE_HALF))])
    return [p for _, p in pts]


def segments():
    """(A, B, normal out, index) for each straight run of wall (none across the gatehouse)."""
    pts = wall_points()
    out = []
    for i in range(len(pts) - 1):
        (ax, az), (bx, bz) = pts[i], pts[i + 1]
        mx, mz = (ax + bx) / 2, (az + bz) / 2
        if abs(mx) < 20 and mz > 0:          # the gatehouse's span
            continue
        tx, tz = bx - ax, bz - az
        ln = math.hypot(tx, tz)
        nx, nz = tz / ln, -tx / ln
        if nx * mx + nz * mz < 0:
            nx, nz = -nx, -nz
        out.append(((ax, az), (bx, bz), (nx, nz), i))
    return out


def water_gate_at(x, z):
    return L.poly_d(x, z, L.RIVER_OUT) <= L.river_hw(x, z, True) + 1


# ================================================================ a curtain wall

def curtain_block(u, d, yy, ln, x, z, in_dir):
    """What the curtain has u along it, d out from its line (outer face at d 4), yy over its foot: a state, "air" to
    clear, or None for nothing."""
    bay = u % BAY
    inner_run = 2.0 < u < ln - 2.0
    pier = bay < 3.0 and inner_run
    # -------- the foundation, the stepped plinth, the body
    if yy < 0:
        return stone(x, yy, z) if -5.0 <= d <= 7.0 else None
    if yy < WALK - 1:
        outer = 6.0 if yy <= 3 else 5.0 if yy <= 7 else 4.0
        if pier:
            outer = 7.0 if yy <= 12 else 6.0
        if d < -4.0 or d > outer + 1.0:
            return None
        if d > outer:
            # a cap of stairs on each step's top
            if not pier and ((yy == 4 and 5.0 < d <= 6.0) or (yy == 8 and 4.0 < d <= 5.0)):
                return stairs("polished_blackstone_brick" if yy == 8 else "deepslate_brick", in_dir)
            if pier and yy == 13 and 6.0 < d <= 7.0:
                return stairs("polished_blackstone_brick", in_dir)
            return None
        # the recessed panel between buttresses: a blind pointed arch with a slit in it
        if 3.0 < d <= 4.0 and inner_run and 3.0 <= bay < 8.0:
            if 10 <= yy <= 20 or (yy == 21 and 4.0 <= bay < 7.0) or (yy == 22 and 5.0 <= bay < 6.0):
                return None
        if 2.0 < d <= 3.0 and inner_run and 5.0 <= bay < 6.0 and 13 <= yy <= 18:
            return "air"
        if 1.0 < d <= 2.0 and inner_run and 5.0 <= bay < 6.0 and 13 <= yy <= 18:
            return DARK
        if 2.0 < d <= 3.0 and inner_run and 4.0 <= bay < 7.0 and yy in (12, 19):
            return LIME
        # the inner face: blind arches a bay long
        if -4.0 <= d < -3.0 and 1 <= yy <= 12 and inner_run and 2.5 <= bay < 8.5:
            cx = abs(bay - 5.5)
            if yy <= 9 or (yy - 9) ** 2 + cx * cx * 1.6 <= 10:
                return None
        return stone(x, yy, z)
    if yy == WALK - 1:
        # the corbels the gallery stands out on (a buttress's are a block further out)
        if -4.0 <= d <= 4.0:
            return stone(x, yy, z)
        if pier and 4.0 < d <= 6.0:
            return stone(x, yy, z)
        if 4.0 < d <= 5.0 and int(u) % 2 == 0:
            return stairs("polished_blackstone_brick", in_dir, "top")
        return None
    # -------- the gallery: a covered walk along the top, windows both ways, under a slate roof
    off = abs(d - 0.5)
    roof_y = EAVE + 6 - int(off)
    if pier and 5.0 < d <= 6.0 and yy <= EAVE + 4:
        return stone(x, yy, z) if yy <= EAVE else GW          # the buttress runs up the gallery to a spike
    if off <= 6.0 and yy == roof_y:
        if off < 1.0:
            return slate()
        return roof_stair(OPP[in_dir] if d < 0.5 else in_dir)
    if off <= 6.0 and roof_y - 2 <= yy < roof_y and yy > EAVE - 1:
        return slate()                                          # the roof's under-layer: no holes on the diagonals
    if off < 1.0 and yy == roof_y + 1 and int(u) % 4 == 0:
        return GW                                               # spikes along the ridge
    if yy > roof_y or d < -4.0 or d > 5.0:
        return None
    if yy == WALK:
        return FLAG if -3.0 <= d <= 4.0 else stone(x, yy, z)
    if -4.0 <= d < -3.0 or 4.0 < d <= 5.0:
        if int(u) % 4 == 2 and yy in (WALK + 2, WALK + 3):
            return PANE
        return stone(x, yy, z)
    return "air"


def curtain(A, B, n, idx, y0=0):
    (ax, az), (bx, bz) = A, B
    tx, tz = bx - ax, bz - az
    ln = math.hypot(tx, tz)
    tx, tz = tx / ln, tz / ln
    nx, nz = n
    out_dir = toward(nx, nz)
    in_dir = OPP[out_dir]
    xs = [ax, bx, ax + nx * 10, bx + nx * 10, ax - nx * 8, bx - nx * 8]
    zs = [az, bz, az + nz * 10, bz + nz * 10, az - nz * 8, bz - nz * 8]
    vines = {}
    for x in range(int(min(xs)) - 1, int(max(xs)) + 2):
        for z in range(int(min(zs)) - 1, int(max(zs)) + 2):
            px, pz = x + 0.5 - ax, z + 0.5 - az
            u = px * tx + pz * tz
            d = px * nx + pz * nz
            if not (0 <= u <= ln) or not (-6.0 <= d <= 7.5):
                continue
            wg = water_gate_at(x + 0.5, z + 0.5)
            for y in range(y0 - 8, y0 + EAVE + 8):
                yy = y - y0
                ring = False
                if wg and yy < 12:
                    # the water gate: a pointed arch over the river, a dressed ring round it, an iron grate down
                    # to the water in the wall's middle
                    rd = L.poly_d(x + 0.5, z + 0.5, L.RIVER_OUT)
                    hw = L.river_hw(x, z, True) + 1
                    top = 4 + math.sqrt(max(0.0, (hw + 2) ** 2 - rd * rd)) * 0.9
                    if -6 <= yy <= top:
                        if 1.5 <= d < 2.5 and yy >= -3:
                            put(x, y, z, BARS % ("true" if yy <= -1 else "false"))
                        continue
                    ring = yy <= top + 1.5
                b = curtain_block(u, d, yy, ln, x, z, in_dir)
                if ring and b is not None and abs(d) >= 4.5:
                    b = CARVED if yy > top + 0.8 and rd < 1.0 else LIME
                if b is not None:
                    put(x, y, z, b)
            if 3.4 < d <= 4.6 and u % BAY >= 2.0 and noise(u * 0.7 + idx * 13, 0, 3.5, 83) > 0.74:
                vines[(x, z)] = int(3 + 9 * noise(u, idx, 2.0, 84))
    for (x, z), ln_ in vines.items():
        vx = x + (1 if out_dir == "east" else -1 if out_dir == "west" else 0)
        vz = z + (1 if out_dir == "south" else -1 if out_dir == "north" else 0)
        for y in range(y0 + WALK - 3, y0 + WALK - 3 - ln_, -1):
            if (vx, vz) in vines or S.get(vx, y, vz) is not None:
                break
            vine(vx, y, vz, in_dir)
    # lanterns hung in the gallery
    for u in range(int(BAY / 2), int(ln) - 2, BAY):
        x, z = int(math.floor(ax + tx * u + nx * 0.5)), int(math.floor(az + tz * u + nz * 0.5))
        put(x, y0 + EAVE + 5, z, HANG)


def dormer(ax, az, tx, tz, nx, nz, u0, y0):
    """A gabled dormer on the gallery roof: its face flush with the gallery's, a window in it, a little roof back."""
    along_pos, along_neg = toward(tx, tz), toward(-tx, -tz)
    mx, mz = ax + tx * u0 + nx * 3, az + tz * u0 + nz * 3
    cells = []
    for x in range(int(mx) - 7, int(mx) + 8):
        for z in range(int(mz) - 7, int(mz) + 8):
            px, pz = x + 0.5 - ax, z + 0.5 - az
            t = px * tx + pz * tz - u0
            d = px * nx + pz * nz
            if abs(t) < 2.5 and 1.0 < d <= 6.5:
                cells.append((x, z, t, d))
    for x, z, t, d in cells:                 # the main roof's eave out in front of it goes
        if abs(t) < 1.5 and d > 5.0:
            for yy in range(EAVE, EAVE + 4):
                put(x, y0 + yy, z, None)
    for x, z, t, d in cells:
        at = abs(t)
        if 4.0 < d <= 5.0 and at < 1.5:
            for yy in range(EAVE, EAVE + 4):
                if at < 0.5 and yy in (EAVE + 1, EAVE + 2):
                    put(x, y0 + yy, z, "air")
                elif yy == EAVE + 3 and at >= 0.5:
                    pass
                else:
                    put(x, y0 + yy, z, LIME if at < 0.5 or yy == EAVE else stone(x, yy, z))
            if at < 0.5:
                put(x, y0 + EAVE + 5, z, GW)
                put(x, y0 + EAVE + 6, z, GW)
        mr = y0 + EAVE + 6 - int(abs(d - 0.5))
        ry = y0 + EAVE + 4 - int(at + 0.5)
        if ry >= mr and d <= 6.0:
            put(x, ry, z, slate() if at < 0.5 else roof_stair(along_pos if t < 0 else along_neg))


# ================================================================ towers

def plan_m(px, pz, plan):
    """The tower plan's 'radius' of a point: octagon (faces on the axes and diagonals) or square."""
    ax_, az_ = abs(px), abs(pz)
    if plan == "oct":
        return max(ax_, az_, (ax_ + az_) * 0.7071)
    return max(ax_, az_)


def tower(cx, cz, plan, h, y0=0, facing_out=(0.0, 1.0), hw=6, banner=True):
    """A tower on the wall's line at cx, cz, hw its half width, h its eaves: a stepped plinth, buttresses clasping its
    corners (square) or pilasters on its angles (octagon), framed lancet windows, a room at the gallery with doors
    both ways along the wall, a corbel table at the eaves, and its spire."""
    ox, oz = facing_out
    ol = math.hypot(ox, oz)
    ox, oz = ox / ol, oz / ol
    icx, icz = int(math.floor(cx)), int(math.floor(cz))
    cx, cz = icx + 0.5, icz + 0.5          # on the block grid, so the plan's symmetric
    walk = y0 + WALK
    R = hw + 4
    for x in range(icx - R, icx + R + 1):
        for z in range(icz - R, icz + R + 1):
            px, pz = x + 0.5 - cx, z + 0.5 - cz
            m = plan_m(px, pz, plan)
            across = abs(px * ox + pz * oz)
            ax_, az_ = abs(px), abs(pz)
            # which face it's on, and how far along that face from its middle
            if plan == "oct":
                terms = sorted([ax_, az_, (ax_ + az_) * 0.7071], reverse=True)
                corner = terms[0] - terms[1] < 0.9
                axis_face = (ax_ + az_) * 0.7071 < max(ax_, az_)
                along = min(ax_, az_) if axis_face else abs(ax_ - az_) * 0.7071
            else:
                corner = ax_ > hw - 2.0 and az_ > hw - 2.0
                along = min(ax_, az_)
                axis_face = True
            for y in range(y0 - 8, y0 + h + 1):
                yy = y - y0
                # the plinth steps in twice; the buttresses run up to the eaves, stepping in halfway
                grow = 3.0 if yy < 0 else 2.0 if yy <= 4 else 1.0 if yy <= 8 else 0.0
                if corner and yy < h - 3:
                    grow = max(grow, (1.5 if yy <= h * 0.55 else 0.8) if plan == "square" else 1.0)
                if m > hw + grow:
                    if not corner and ((yy == 5 and m <= hw + 2.0) or (yy == 9 and m <= hw + 1.0)):
                        put(x, y, z, stairs("polished_blackstone_brick" if yy == 9 else "deepslate_brick", toward(-px, -pz)))
                    continue
                e = hw - m                 # how deep inside the plain face
                room = e > 1.6 and walk < y < y0 + h
                door = walk < y <= walk + 3 and across <= 1.5 and e < 2.0
                if room or door:
                    put(x, y, z, "air")
                    continue
                if (y == walk or y == y0 + h) and e > 1.6:
                    put(x, y, z, FLAG if y == walk else "spruce_planks")
                    continue
                if 0.0 <= e < 2.0 and not corner:
                    w = window_at(yy, h, along, axis_face, plan)
                    if w == "open":
                        put(x, y, z, "air" if e < 1.0 else (PANE if walk < y < y0 + h else DARK))
                        continue
                    if w == "frame" and e < 1.0:
                        put(x, y, z, LIME)
                        continue
                put(x, y, z, stone(x, yy, z, h))
            # the corbel table at the eaves, a dark band over it the spire stands on
            if hw < m <= hw + 1.0:
                if (x + z) % 2 == 0 or corner:
                    put(x, y0 + h - 2, z, stairs("polished_blackstone_brick", toward(-px, -pz), "top"))
                put(x, y0 + h - 1, z, stone(x, h, z))
                put(x, y0 + h, z, stone(x, h, z))
    spire(cx, cz, y0 + h + 1, hw, plan, banner)
    put(icx, walk + 4, icz, HANG)


def window_at(yy, h, along, axis_face, plan):
    """'open', 'frame' or None for a face block yy up, `along` from the face's middle: a slit low down, tall pointed
    lancets in the room at the gallery, another row up a tall tower; each framed in dressed stone."""
    rows = [(13, 19, 0.6), (WALK + 3, WALK + 10, 1.5 if axis_face else 0.6)]
    if h - 10 > WALK + 16 and axis_face:
        rows.append((h - 13, h - 7, 1.5))
    for a, b, half in rows:
        if a <= yy <= b and along < half:
            return "open"
        if yy == b + 1 and along < 0.5 and half > 1.0:
            return "open"                               # the pointed head
        if a - 1 <= yy <= b + 2 and along < half + 1.0:
            return "frame"
    return None


def spire(cx, cz, y0, hw, plan, banner=True):
    """A dark slate spire three times as tall as it's wide, flared at the eaves, with a gabled dormer on each of the
    four faces and a little spired turret at each corner, a gilded finial on top."""
    R0 = hw + 1.9
    H = int(round(R0 * 4.6))
    icx, icz = int(math.floor(cx)), int(math.floor(cz))

    def rad(k):
        return R0 * max(0.0, 1 - k / H) ** 1.2
    for x in range(icx - hw - 4, icx + hw + 5):
        for z in range(icz - hw - 4, icz + hw + 5):
            px, pz = x + 0.5 - cx, z + 0.5 - cz
            m = plan_m(px, pz, plan)
            f = toward(-px, -pz)
            for k in range(H):
                r = rad(k) + (0.8 if k == 0 else 0.0)
                if r - 1.5 < m <= r:
                    put(x, y0 + k, z, roof_stair(f) if m > rad(k + 1) or k == 0 else slate())
    top = seat(icx, icz, y0 + H)
    put(icx, top, icz, GW)
    put(icx, top + 1, icz, GILT)
    put(icx, top + 2, icz, BARS % "false")
    put(icx, top + 3, icz, BARS % "false")
    if banner:
        put(icx, top + 4, icz, "red_banner[rotation=0]")
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        lucarne(icx, icz, y0, hw, dx, dz)
    for sx in (-1, 1):
        for sz in (-1, 1):
            k = hw * 0.7071 + 0.4 if plan == "oct" else hw - 0.2
            turret(cx + sx * k, cz + sz * k, y0 - 1)


def lucarne(icx, icz, y0, hw, dx, dz):
    """A stone dormer on the spire's face (dx, dz): its front flush with the eaves band, a tall slit window, a steep
    gable with a pinnacle, its little roof running back into the spire."""
    tx, tz = -dz, dx
    cells = []
    for x in range(icx - hw - 4, icx + hw + 5):
        for z in range(icz - hw - 4, icz + hw + 5):
            px, pz = x - icx, z - icz          # whole numbers: the tower's on the grid
            n = px * dx + pz * dz
            t = px * tx + pz * tz
            if abs(t) <= 3 and hw - 2 <= n <= hw + 2:
                cells.append((x, z, n, t))
    for x, z, n, t in cells:                 # clear the spire's flare in front of it
        if n >= hw + 1 and abs(t) <= 3:
            for y in range(y0, y0 + 10):
                put(x, y, z, None)
    for x, z, n, t in cells:
        at = abs(t)
        if n == hw + 1 and at <= 2:
            for k in range(0, 8):
                y = y0 + k
                if at == 0 and 1 <= k <= 4:
                    put(x, y, z, "air")
                elif (at == 1 and k <= 5) or (at == 0 and k in (0, 5)):
                    put(x, y, z, LIME)
                elif (at == 2 and k <= 5) or (at == 1 and k == 6) or (at == 0 and k in (6, 7)):
                    put(x, y, z, stone(x, 20, z))
            if at == 0:
                put(x, y0 + 9, z, GW)
                put(x, y0 + 10, z, GW)
        if n == hw and at == 0:
            for k in range(1, 5):
                put(x, y0 + k, z, DARK)
        if hw - 2 <= n <= hw and at == 2:
            for k in range(0, 6):
                put(x, y0 + k, z, stone(x, 20, z))          # its cheeks
        if at <= 3:
            ry = y0 + 8 - at
            put(x, ry, z, slate() if at == 0 else roof_stair(toward(-t * tx, -t * tz)))


def turret(cx, cz, y0):
    """A little round turret corbelled out at a spire's corner, its own needle spire on top."""
    icx, icz = int(math.floor(cx)), int(math.floor(cz))
    for x in range(icx - 4, icx + 5):
        for z in range(icz - 4, icz + 5):
            dd = math.hypot(x + 0.5 - cx, z + 0.5 - cz)
            for k in range(-5, 6):
                r = 1.75 if k >= 0 else 1.75 * (1 + k / 6.0)
                if dd > r:
                    continue
                if k in (2, 3) and dd > 1.0 and (x + z) % 2 == 0:
                    put(x, y0 + k, z, DARK)
                elif k == 5 and dd > 1.0:
                    put(x, y0 + k, z, stairs("polished_blackstone_brick", toward(cx - x - 0.5, cz - z - 0.5), "top"))
                else:
                    put(x, y0 + k, z, stone(x, 20, z))
            for k in range(13):
                r = 2.4 * (1 - k / 13.0) ** 1.2
                if r - 1.3 < dd <= r:
                    step = dd > 2.4 * (1 - (k + 1) / 13.0) ** 1.2
                    put(x, y0 + 6 + k, z, roof_stair(toward(cx - x - 0.5, cz - z - 0.5)) if step else slate())
    yt = seat(icx, icz, y0 + 19)
    put(icx, yt, icz, GW)
    put(icx, yt + 1, icz, BARS % "false")


# ================================================================ the gatehouse, the drawbridge, the barbican

GZ = L.GATE_Z
GX = 15                       # the gate towers' centres either side


def gatehouse():
    """Two tall square towers either side of a pointed arch three orders deep, a gabled hall over it with three
    lancets and the city's crest, the portcullis half up and the doors open; out over the moat the drawbridge, down;
    beyond it the barbican."""
    for sx in (-1, 1):
        tower(sx * GX, GZ + 1, "square", 62, 0, (sx * 0.35, 1.0), hw=7)
    z0, z1 = GZ - 7, GZ + 5
    for x in range(-8, 9):
        ax = abs(x)
        for z in range(z0, z1 + 1):
            order = 2 if z == z1 else 1 if z == z1 - 1 else 0
            half = 6 + order
            for y in range(-8, 38):
                if ax <= 5 and 0 < y <= 13 + pointed(ax, 6, 8):
                    put(x, y, z, "air")
                    continue
                if order > 0 and ax <= half and 0 < y <= 14 + order + pointed(ax, half + 1, 9 + order):
                    put(x, y, z, CARVED if order == 2 else LIME)
                    continue
                if z == z1:
                    # three lancets over the arch, a tall middle one, framed
                    w = None
                    for wx, a, b, wh in ((0, 26, 34, 1), (-5, 27, 32, 0), (5, 27, 32, 0)):
                        if abs(x - wx) <= wh and a <= y <= b or (wh and x == wx and y == b + 1):
                            w = "open"
                        elif abs(x - wx) <= wh + 1 and a - 1 <= y <= b + 2 and w is None:
                            w = "frame"
                    if w == "open":
                        put(x, y, z, "air")
                        put(x, y, z - 1, DARK)
                        continue
                    if w == "frame":
                        put(x, y, z, LIME)
                        continue
                    if y == 36:
                        put(x, y, z, stairs("polished_blackstone_brick", "north", "top"))
                        continue
                if z == z1 - 1 and y > 24 and S.get(x, y, z) == DARK:
                    continue
                put(x, y, z, stone(x, y, z))
            if ax <= 5:
                put(x, 0, z, FLAG)
    # the hall's roof: a steep slate gable, its ridge running between the towers
    zc = (z0 + z1) / 2.0
    for x in range(-8, 9):
        for z in range(z0 - 1, z1 + 2):
            dz = abs(z - zc)
            top = 38 + int((7.0 - dz) * 1.5)
            low = 38 + int((6.0 - dz) * 1.5) + 1 if dz < 6.5 else 38
            for y in range(max(38, low), top):
                put(x, y, z, slate())
            put(x, top, z, slate() if dz < 0.6 else roof_stair("north" if z > zc else "south"))
    for x in range(-8, 9, 4):
        put(x, 38 + int(7.0 * 1.5) + 1, int(zc), GW)
    # the crest over the arch
    for x in range(-3, 4):
        for y in range(22, 27):
            if abs(x) + abs(y - 24) <= 2:
                put(x, y, z1 + 1, GILT if abs(x) + abs(y - 24) <= 1 else CARVED)
    # the portcullis, half up, and the great doors swung back against the passage's sides
    zp = GZ + 3
    for x in range(-5, 6):
        for y in range(9, 22):
            if y <= 13 + pointed(abs(x), 6, 8):
                put(x, y, zp, BARS % "false")
    for sx in (-1, 1):
        for z in range(GZ - 6, GZ + 1):
            for y in range(1, 13):
                put(sx * 5, y, z, "dark_oak_planks")
        for z in (z0 + 2, z1 - 3):                   # on the passage's sides, not on air
            put(sx * 5, 6, z, "ashbound:wall_lantern[facing=%s]" % ("east" if sx < 0 else "west"))
    # great banners down the towers' fronts: red, gold-edged, the city's sign on them
    for sx in (-1, 1):
        cx, cz = sx * GX, GZ + 9
        for x in range(cx - 3, cx + 4):
            for y in range(22, 50):
                edge = abs(x - cx) == 3
                if y < 26 and abs(x - cx) < 4 - (26 - y):         # a swallowtail's notch
                    continue
                sign = abs(x - cx) + abs(y - 38) <= 2 or (x == cx and 33 <= y <= 43)
                put(x, y, cz, "yellow_wool" if edge else GILT if sign else "red_wool")
            put(x, 50, cz, "dark_oak_slab[type=bottom,waterlogged=false]")
    drawbridge()
    barbican()


def pointed(ax, half, rise):
    """How high a pointed (two-centred) arch rises over its springing, ax out from its middle, half its span."""
    if ax > half:
        return -999
    rc = half * 1.6
    return math.sqrt(max(0.0, rc * rc - (ax + rc - half) ** 2)) * rise / math.sqrt(rc * rc - (rc - half) ** 2)


def drawbridge():
    """Out of the gate: a short timber drawbridge, down, over the first stretch of the moat onto a stone bridge's
    pier; the bridge itself on a pointed arch over the water, parapets with blackstone rails, lanterns on the piers."""
    zd0, zd1 = GZ + 6, GZ + 13          # the drawbridge (lowered), hinged at the gate's front
    zp0, zp1 = GZ + 14, GZ + 16         # the pier it rests on, a cutwater either side
    za0, za1 = GZ + 17, GZ + 22         # the arch over the moat's outer half
    zb1 = GZ + 26                       # the bridge runs on over the far bank to the barbican
    bed = L.MOAT_BED
    # the drawbridge: dark oak beams down its edges and across every fourth row, spruce planks between, iron straps
    for x in range(-5, 6):
        for z in range(zd0, zd1 + 1):
            edge = abs(x) == 5
            beam = (z - zd0) % 4 == 0
            put(x, 0, z, "dark_oak_log[axis=z]" if edge else "dark_oak_log[axis=x]" if beam else "spruce_planks")
            put(x, -1, z, "dark_oak_planks" if edge or beam else "spruce_slab[type=top,waterlogged=false]")
            for y in range(1, 4):
                put(x, y, z, "air")
        for z in (zd0 + 1, zd1 - 1):
            put(x, 1, z, "air")
    for sx in (-1, 1):
        for z in range(zd0, zd1 + 1, 3):
            put(sx * 5, 1, z, "iron_bars[east=false,north=true,south=true,west=false,waterlogged=false]")
        # the hinge: a heavy blackstone sill at the gate's lip, iron rings each side
        put(sx * 6, 0, zd0, CARVED)
        put(sx * 6, 1, zd0, GW)
    # the stone bridge: pier, arch, the far span over the bank; its deck humps a block over the arch
    def rise(z):
        return 1 if za0 - 1 <= z <= za1 + 1 else 0
    for x in range(-7, 8):
        ax = abs(x)
        for z in range(zp0 - 1, zb1 + 1):
            pier = zp0 <= z <= zp1
            wide = 6 if not pier else 7          # the parapet bulges out over the pier (a refuge)
            if ax > wide:
                continue
            dh = rise(z)
            ramp = dh and (z == za0 - 1 or z == za1 + 1)
            for y in range(bed, 5):
                r = y - dh
                if r >= 1:
                    # the parapet: a stone course, blackstone rail over it, a lantern over the pier
                    if ax == wide and r == 1:
                        put(x, y, z, stone(x, 6, z))
                    elif ax == wide and r == 2:
                        put(x, y, z, LIME if pier else GW)
                    elif ax == wide and r == 3 and pier and z == zp0 + 1:
                        put(x, y, z, LANTERN)
                    elif ax < wide:
                        put(x, y, z, "air")
                    continue
                if z == zp0 - 1:
                    # the pier's cutwater: a pointed nose into the moat, stepped back as it rises
                    if ax <= 4 - max(0, y + 3) // 2 and y < -1:
                        put(x, y, z, LIME if y == -2 else stone(x, y - bed, z))
                    continue
                if za0 <= z <= za1:
                    half = (za1 - za0 + 1) / 2.0
                    m = abs(z - (za0 + za1) / 2.0)
                    top = -4 + pointed(m, half + 0.5, 4.4)
                    if y <= top:
                        put(x, y, z, "air" if y > L.WATER_OUT else None)
                        continue
                    if y <= top + 1.2 and ax >= wide - 1:
                        put(x, y, z, LIME)          # the arch's dressed ring on both faces
                        continue
                if r == 0:
                    if ramp and ax < wide:
                        put(x, y, z, stairs("deepslate_tile", "south" if z == za0 - 1 else "north"))
                        put(x, y - 1, z, FLAG if ax <= 3 else LIME)
                    else:
                        put(x, y, z, FLAG if ax <= 3 else LIME if ax < wide else stone(x, 8, z))
                elif ax == wide and r == -1:
                    put(x, y, z, stairs("polished_blackstone_brick", "east" if x > 0 else "west", "top"))   # a drip course
                elif not (ramp and r == -1):
                    put(x, y, z, stone(x, y - bed, z))
    # lanterns on posts at the bridge's far end
    for sx in (-1, 1):
        put(sx * 6, 3, zb1 - 1, GW)
        put(sx * 6, 4, zb1 - 1, LANTERN)


def barbican():
    """Beyond the moat: a walled court with two octagonal spired towers and an outer arch, the road coming in."""
    zf = GZ + 46
    za = GZ + 27
    for sx in (-1, 1):
        for x in (sx * 12, sx * 11, sx * 10):
            for z in range(za, zf - 6):
                for y in range(-8, 19):
                    put(x, y, z, stone(x, y, z, 19))
                if abs(x) == 12:
                    put(x, 19, z, stone(x, 19, z) if z % 3 != 0 else None)
                    put(x, 20, z, slab("deepslate_brick") if z % 3 != 0 else None)
                elif abs(x) == 11:
                    put(x, 18, z, FLAG)
        tower(sx * 14, zf - 3, "oct", 32, 0, (sx * 0.4, 1.0), hw=4, banner=False)
    for x in range(-11, 12):
        for z in (zf - 2, zf - 1, zf):
            ax = abs(x)
            for y in range(-8, 22):
                if ax <= 4 and 0 < y <= 9 + pointed(ax, 5, 5):
                    put(x, y, z, "air")
                    continue
                if z == zf and ax <= 5 and 0 < y <= 10 + pointed(ax, 6, 6):
                    put(x, y, z, LIME)
                    continue
                if y >= 19:
                    if z == zf and (y == 19 or (x % 3 != 0 and y <= 20)):
                        put(x, y, z, stone(x, y, z))
                    elif z < zf and y == 19:
                        put(x, y, z, FLAG)
                    continue
                put(x, y, z, stone(x, y, z, 21))
            if ax <= 4:
                put(x, 0, z, FLAG)
    for x in range(-3, 4):
        for y in (14, 15, 16):
            if abs(x) + abs(y - 15) <= 2:
                put(x, y, zf, GILT if abs(x) + abs(y - 15) == 0 else CARVED)
    for x in range(-9, 10):
        for z in range(za, zf - 2):
            put(x, 0, z, FLAG if abs(x) <= 4 else pick((FLAG, 4), ("gravel", 1)))


# ================================================================ the moat

def moat():
    """Water round the wall's open south side, down between stone revetments, a kerb along each bank."""
    bed = L.MOAT_BED
    for x in range(-L.RX - 30, L.RX + 31):
        for z in range(40, L.RZ + 40):
            d = L.moat_d(x, z)
            if d is None or L.floor_d(x, z) >= 0:
                continue
            river = L.poly_d(x, z, L.RIVER_OUT) <= L.river_hw(x, z, True) + 1
            kerb = (d < 10.0 or d > 22.0) and not river
            for y in range(bed, 1):
                if S.get(x, y, z) is not None and not S.get(x, y, z).startswith("water"):
                    continue
                if kerb:
                    put(x, y, z, pick((G, 5), (MG, 1), ("mossy_stone_bricks", 1 if y < -5 else 0)))
                    if y == 0:
                        put(x, 1, z, "polished_deepslate_slab[type=bottom,waterlogged=false]")    # the kerb, over the turf
                elif y == bed:
                    put(x, y, z, pick(("gravel", 3), ("mud", 1)))
                elif y <= L.WATER_OUT:
                    put(x, y, z, WATER)
                    if y == L.WATER_OUT and noise(x, z, 5, 85) > 0.86:
                        put(x, y + 1, z, "lily_pad")
                else:
                    put(x, y, z, "air")


# ================================================================ the ends: spur walls up the slope to hill towers

def spur(sgn):
    """From the end tower straight out up the hillside, the wall stepping up with the ground, to a hill tower."""
    a = sgn * A_END
    ex, ez = ell_pt(a)
    ux, uz = math.sin(a), math.cos(a) * (L.RZ / L.RX)
    ul = math.hypot(ux, uz)
    ux, uz = ux / ul, uz / ul
    length = 64
    tx, tz = ex + ux * length, ez + uz * length
    return (ex, ez), (tx, tz), (ux, uz)


def spur_wall(ground, sgn):
    (ex, ez), (tx, tz), (ux, uz) = spur(sgn)
    nx, nz = -uz, ux
    for x in range(int(min(ex, tx)) - 6, int(max(ex, tx)) + 7):
        for z in range(int(min(ez, tz)) - 6, int(max(ez, tz)) + 7):
            px, pz = x + 0.5 - ex, z + 0.5 - ez
            u = px * ux + pz * uz
            d = px * nx + pz * nz
            if not (8 <= u <= 60) or abs(d) > 4.5:
                continue
            g = ground(x, z)
            top = g + 16
            pier = u % BAY < 2.0
            if abs(d) > 3.5 and not pier:
                continue
            for y in range(g - 6, top + 2):
                if abs(d) > 3.5:
                    if y < top - 3:
                        put(x, y, z, stone(x, y - g, z, 18))
                    elif y == top - 3:
                        put(x, y, z, stairs("polished_blackstone_brick", toward(-d * nx, -d * nz)))
                elif y < top:
                    put(x, y, z, stone(x, y - g, z, 18))
                elif y == top:
                    put(x, y, z, FLAG if abs(d) < 2.5 else stone(x, 18, z))
                elif abs(d) >= 2.5 and int(u) % 3 != 2:
                    put(x, y, z, stone(x, 18, z))
    g = ground(int(tx), int(tz))
    tower(tx, tz, "oct", 30, g, (ux, uz), hw=4)


# ================================================================ all of it

def build(ground):
    """ground(x, z): the land's height there (capital.H)."""
    segs = segments()
    for A, B, n, i in segs:
        curtain(A, B, n, i, 0)
    for a, plan, h, sgn, k, hw in TOWERS:
        x, z = ell_pt(a)
        tower(x, z, plan, h, 0, (x / L.RX ** 2, z / L.RZ ** 2), hw=hw)
    gatehouse()
    moat()
    for sgn in (-1, 1):
        spur_wall(ground, sgn)
    print("walls: %d curtains, %d towers" % (len(segs), len(TOWERS)))
