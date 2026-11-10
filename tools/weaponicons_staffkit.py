"""The staff's long shaft for the icons, and st(): a head drawn seven rows tall in the top right, with the shaft
carrying on from wherever the head leaves it."""
from weaponicons import I

SHAFT = [".......owo", "......owo", ".....owo", "....owo", "...owo", "..owo", ".owo", "owo", "go"]


def st(name, pal, head, marks=(), shaft=SHAFT):
    rows = [r.ljust(16, ".") for r in head.strip("\n").split("\n")]
    rows = (rows + ["." * 16] * 7)[:7]
    # the shaft carries on from wherever the head left it
    top = next(((y, r.index("w")) for y in (6, 5) for r in [rows[y]] if "w" in r), (6, 9))
    shift = top[1] - (6 - top[0]) - 9
    body = []
    for r in shaft:
        r = "." * shift + r if shift >= 0 else r[-shift:]     # running off the left edge
        body.append(r[:16].ljust(16, "."))
    rows += body
    g = [list(r) for r in rows[:16]]
    for y, x, c in marks:
        g[y][x] = c
    if " g=" not in " " + pal:
        pal += " g=7a6a4a"
    I(name, pal, "\n".join("".join(r) for r in g))
