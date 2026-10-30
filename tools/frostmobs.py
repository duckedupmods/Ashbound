"""The rest of the Frozen Procession for the Epic Fight Frost gate: three more of the army that froze on the pass,
built on the Frostbound's own body (E:/Ashbound/tools/voxfrost.py) so they march as one host.

    standard_bearer   the elite who carries the key: the host's frozen banner on a tall pole, a tower shield
    frost_chaplain    the army's priest: a hood and long vestments, a censer of ice smoke, a staff crowned in ice
    rime_knight       the heavy line: horned helm, doubled pauldrons, a two-handed greatsword grown out of ice

    python tools/frostmobs.py [names] [--preview]   writes tools/mob_src (the meshes efmob reads), then
    python tools/port_gate.py frost mobs
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, 'E:/Ashbound/tools')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import voxsword as V  # noqa: E402
from voxsword import h3  # noqa: E402
from voxboss import Part, PB, C  # noqa: E402
import voxmob as M  # noqa: E402
import voxfrost as F  # noqa: E402

OUT = Path(os.path.dirname(os.path.abspath(__file__))) / 'mob_src'
HALBERD = {"halberd"}


def base(name, drop_head=False):
    s, parts = F.frostbound(False)
    s.name = name
    keep = []
    for b in s.boxes:
        if b.part.name in HALBERD:
            continue
        if drop_head and b.part.name == "head" and b.tag in ("helm", "visor", "brow", "plume", "icicle", "eye"):
            continue
        keep.append(b)
    s.boxes[:] = keep

    def add(part, box, mat, **kw):
        lo, size = box
        b = PB(part, lo, size, mat, tag=kw.pop("tag", part.name), **kw)
        s.boxes.append(b)
        return b

    def icicles(parent, x0, x1, y, z, n, longest=2.6, seed=0):
        for k in range(n):
            x = x0 + (x1 - x0) * (k + 0.5) / n
            ln = longest * (0.4 + 0.6 * h3(k, seed, 3))
            add(parent, C(x, y - ln, z, 0.5, ln, 0.5), "ice", tag="icicle")
    return s, parts, add, icicles


def standard_bearer():
    """the banner of the host held high in the right fist, a tower shield on the left arm, a crowned helm"""
    s, parts, add, icicles = base("standard_bearer")
    gx, gy, gz = -6.6, 12.6, 1.4
    pole = Part("banner", (gx, gy, gz), (("x", 88), ("z", 4)), parts["hand_r"])
    add(pole, C(gx, gy - 14.0, gz, 1.3, 58.0, 1.3), "wood", tag="pole")
    top = gy + 44.0
    add(pole, C(gx, top - 0.6, gz, 2.0, 1.6, 2.0), "gold", tag="collar")
    add(pole, C(gx, top + 1.0, gz, 0.9, 5.0, 0.9), "blade", tag="finial")
    add(pole, C(gx, top + 2.4, gz, 3.0, 0.8, 0.9), "gold", tag="finial")
    add(pole, C(gx, top - 3.0, gz + 6.0, 1.0, 1.0, 13.0), "wood", tag="crossbar")
    # the banner itself, frozen stiff in the wind it last felt: the host's sigil on it, icicles off its hem
    add(pole, ((gx - 0.3, top - 21.0, gz + 0.8), (0.6, 18.0, 11.2)), "cloth", tag="flag")
    add(pole, ((gx - 0.45, top - 13.0, gz + 4.0), (0.9, 6.0, 4.8)), "sigil", tag="flag_sigil")
    add(pole, ((gx - 0.45, top - 15.4, gz + 5.8), (0.9, 2.4, 1.2)), "sigil", tag="flag_sigil")
    add(pole, ((gx - 0.4, top - 4.2, gz + 0.8), (0.8, 1.2, 11.2)), "gold", tag="flag_rod")
    for k in range(5):
        z = gz + 1.6 + k * 2.3
        ln = 2.0 + 2.2 * h3(k, 4, 3)
        add(pole, ((gx - 0.25, top - 21.0 - ln, z), (0.5, ln, 0.5)), "ice", tag="icicle")
    add(pole, C(gx, gy - 15.0, gz, 1.0, 1.8, 1.0), "steel", tag="butt")
    # the tower shield along the left forearm
    sh = Part("shield", (6.6, 18.0, 0), (), parts["fore_l"])
    add(sh, C(9.2, 8.0, 0.4, 1.0, 16.0, 10.0), "steel", tag="shield")
    add(sh, C(9.8, 8.6, 0.4, 0.5, 14.8, 8.8), "cloth", tag="shield_face")
    add(sh, C(10.2, 13.0, 0.4, 0.5, 5.0, 2.0), "sigil", tag="shield_sigil")
    add(sh, C(10.2, 14.6, 0.4, 0.5, 1.6, 5.0), "sigil", tag="shield_sigil")
    add(sh, C(9.8, 23.6, 0.4, 1.6, 0.8, 10.4), "gold", tag="shield_rim")
    add(sh, C(9.8, 7.6, 0.4, 1.6, 0.8, 10.4), "gold", tag="shield_rim")
    icicles(sh, 9.6, 10.0, 7.6, 3.6, 3, 2.2, seed=12)
    # a crown of ice points ringing the helm, a heavier gorget: the host's champion
    for k, (x, z) in enumerate(((-2.4, 2.6), (0, 2.9), (2.4, 2.6), (-2.8, 0), (2.8, 0), (-2.4, -2.6), (2.4, -2.6))):
        add(parts["head"], C(x, 41.4, z + 0.2, 0.9, 2.4 + 1.4 * h3(k, 2, 3), 0.9), "ice", tag="crown")
    add(parts["head"], C(0, 40.4, 0.2, 6.4, 1.2, 6.8), "gold", tag="circlet")
    add(parts["torso"], C(0, 33.6, -0.2, 12.8, 1.4, 6.4), "gold", tag="gorget_trim")
    return s, parts


def frost_chaplain():
    """a deep hood with only the cold light under it, vestments to the boots, a staff of ice, a censer"""
    s, parts, add, icicles = base("frost_chaplain", drop_head=True)
    head, hips, torso = parts["head"], parts["hips"], parts["torso"]
    add(head, C(0, 33.0, -0.2, 7.0, 8.8, 7.6), "cloth", tag="hood")
    add(head, C(0, 41.6, -1.2, 4.6, 1.6, 4.6), "cloth", tag="hood")
    add(head, C(0, 39.0, -4.2, 4.0, 4.0, 1.2), "cloth", tag="hood")
    add(head, C(0, 33.4, 3.55, 4.6, 6.2, 0.3), "dark", tag="cowl")
    add(head, C(-1.1, 37.0, 3.7, 1.0, 0.7, 0.3), "eye", group="glow", tag="eye")
    add(head, C(1.1, 37.0, 3.7, 1.0, 0.7, 0.3), "eye", group="glow", tag="eye")
    icicles(head, -3.0, 3.0, 33.0, 3.9, 6, 2.2, seed=21)
    add(head, C(0, 41.0, 3.6, 1.0, 1.0, 0.5), "sigil", tag="hood_sigil")
    # vestments: long panels fore and aft, a stole of the host's sigil down the front
    vest = {}
    for z, lean in ((2.9, -3), (-2.9, 4)):
        v = vest[z > 0] = Part("vest%d" % (z > 0), (0, 20.4, z), (("x", lean),), hips)
        add(v, C(0, 2.2, z, 8.0, 18.4, 0.7), "cloth", tag="vestment")
    for side in (1, -1):
        v = Part("vest_side%d" % (side > 0), (side * 4.4, 20.4, 0), (("z", side * 5),), hips)
        add(v, C(side * 4.6, 4.0, 0, 0.7, 16.6, 5.2), "cloth", tag="vestment")
    for side in (-1.6, 1.6):
        add(torso, C(side, 22.0, 3.2, 1.2, 10.4, 0.4), "sigil", tag="stole")
    add(vest[True], C(0, 2.6, 3.4, 2.4, 15.0, 0.4), "sigil", tag="stole")
    add(torso, C(0, 32.4, -0.2, 12.4, 1.6, 6.4), "cloth", tag="mantle")
    # the staff in the right fist, a crystal of ice for a head
    gx, gy, gz = -6.6, 12.6, 1.4
    st = Part("staff", (gx, gy, gz), (("x", 86), ("z", 4)), parts["hand_r"])
    add(st, C(gx, gy - 16.0, gz, 1.2, 46.0, 1.2), "wood", tag="haft")
    top = gy + 30.0
    add(st, C(gx, top - 1.0, gz, 2.0, 1.4, 2.0), "gold", tag="collar")
    for k, (dx, dz) in enumerate(((-1.1, 0), (1.1, 0), (0, -1.1), (0, 1.1))):
        add(st, C(gx + dx, top, gz + dz, 0.6, 3.0, 0.6), "gold", tag="claw")
    add(st, C(gx, top + 0.4, gz, 2.2, 6.0, 2.2), "ice", group="glow", tag="crystal")
    add(st, C(gx, top + 6.4, gz, 1.2, 2.4, 1.2), "ice", group="glow", tag="crystal")
    # the censer, swung from the left fist on a chain, ice smoke light inside its cage
    cn = Part("censer", (6.6, 12.0, 0.4), (("x", 86),), parts["hand_l"])
    add(cn, C(6.6, 4.6, 0.4, 0.3, 7.4, 0.3), "sigil", tag="chain")
    add(cn, C(6.6, 1.0, 0.4, 3.2, 3.6, 3.2), "gold", tag="censer")
    add(cn, C(6.6, 1.5, 0.4, 3.4, 2.4, 2.4), "ice", group="glow", tag="ember")
    add(cn, C(6.6, 1.5, 0.4, 2.4, 2.4, 3.4), "ice", group="glow", tag="ember")
    add(cn, C(6.6, 4.4, 0.4, 2.0, 0.8, 2.0), "gold", tag="censer")
    add(cn, C(6.6, 0.2, 0.4, 2.0, 0.8, 2.0), "gold", tag="censer")
    return s, parts


def rime_knight():
    """the heavy line of the host: a greatsword of glacier ice in both hands, horns of ice on the helm"""
    s, parts, add, icicles = base("rime_knight")
    head, torso = parts["head"], parts["torso"]
    for side in (1, -1):                       # horns sweeping back off the helm
        hn = Part("horn%d" % (side > 0), (side * 2.9, 39.0, 0.4), (("z", side * -40), ("x", -20)), head)
        add(hn, C(side * 2.9, 39.0, 0.4, 1.6, 3.0, 1.6), "ice", tag="horn")
        add(hn, C(side * 2.9, 41.8, 0.0, 1.2, 3.0, 1.2), "ice", tag="horn")
        add(hn, C(side * 2.9, 44.6, -0.4, 0.8, 2.6, 0.8), "ice", tag="horn")
    add(head, C(0, 33.0, 2.6, 6.2, 2.6, 1.4), "steel", tag="bevor")
    for side in (1, -1):                       # a second, larger pauldron over the first, edged in frost
        pl = Part("pauldron_big%d" % (side > 0), (side * 6.2, 35.0, -0.2), (("z", side * -24),), torso)
        add(pl, C(side * 7.4, 32.6, -0.2, 6.4, 3.2, 7.4), "steel", tag="pauldron")
        add(pl, C(side * 7.4, 35.6, -0.2, 5.0, 1.4, 6.4), "steel", tag="pauldron")
        for k in range(3):
            add(pl, C(side * (5.6 + k * 1.6), 36.8, -0.2, 0.9, 1.6 + k * 0.8, 0.9), "ice", tag="spike")
        icicles(pl, side * 4.8, side * 10.0, 32.6, 3.4, 4, 2.6, seed=side + 30)
    add(torso, C(0, 22.4, -2.8, 9.0, 8.0, 0.8), "steel", tag="backplate")
    # the greatsword, held like the halberd: the grip through both fists, the blade up over the head
    gx, gy, gz = -6.6, 12.6, 1.4
    sw = Part("greatsword", (gx, gy, gz), (("x", 70), ("z", 8)), parts["hand_r"])
    add(sw, C(gx, gy - 6.0, gz, 1.3, 10.0, 1.3), "wood", tag="grip")
    add(sw, C(gx, gy - 7.4, gz, 2.0, 1.6, 2.0), "steel", tag="pommel")
    add(sw, C(gx, gy - 8.2, gz, 1.2, 1.0, 1.2), "ice", tag="pommel")
    g = gy + 4.0
    add(sw, C(gx, g, gz, 1.8, 1.6, 9.0), "steel", tag="guard")
    add(sw, C(gx, g + 0.4, gz + 4.8, 1.4, 2.4, 1.2), "ice", tag="guard")
    add(sw, C(gx, g + 0.4, gz - 4.8, 1.4, 2.4, 1.2), "ice", tag="guard")
    add(sw, C(gx, g + 1.6, gz, 1.6, 3.0, 4.2), "blade", tag="ricasso")
    add(sw, C(gx, g + 4.6, gz, 0.9, 20.0, 4.6), "ice", tag="blade")
    add(sw, C(gx, g + 4.6, gz, 1.3, 20.0, 1.2), "blade", tag="fuller")
    add(sw, C(gx, g + 24.6, gz, 0.9, 2.6, 3.0), "ice", tag="blade")
    add(sw, C(gx, g + 27.2, gz, 0.8, 1.8, 1.4), "ice", tag="tip")
    for k in range(4):                         # ice teeth grown out along the edge
        add(sw, C(gx, g + 8.0 + k * 4.6, gz + 2.7, 0.7, 1.8, 1.0), "ice", tag="tooth")
        add(sw, C(gx, g + 10.0 + k * 4.6, gz - 2.7, 0.7, 1.8, 1.0), "ice", tag="tooth")
    return s, parts


MOBS = {"standard_bearer": standard_bearer, "frost_chaplain": frost_chaplain, "rime_knight": rime_knight}
POINTS = {"eyes": ("head", (0, 37.2, 3.6)), "hand_l": ("hand_l", (6.6, 11.0, 1.0))}


def main():
    V.T = 2
    M.ASSETS = OUT
    names = [a for a in sys.argv[1:] if not a.startswith("--")] or list(MOBS)
    for n in names:
        s, parts = MOBS[n]()
        if "--preview" in sys.argv:
            M.preview(s, n)
        else:
            M.export(s, parts, n, F.BONES, POINTS)
            print("wrote", n, len(s.boxes), "boxes")


if __name__ == "__main__":
    main()
