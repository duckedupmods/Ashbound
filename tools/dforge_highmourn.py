"""Highmourn's house stone: five hewn stones for the capital's houses (bricks with stairs, slab and wall, big
quoins for the corners, a cracked brick to weather with), each chosen to suit a house's plaster and roof.
dforge.py imports this; python tools/blockforge.py highmourn --sheet."""
from blockforge import R
from dforge import dungeon, B

STONES = (   # name, title, ramp dark -> light, mortar
    ("hearthstone", "Hearthstone", R("#5a4c3c", "#7a6a54", "#98866a", "#b4a282", "#ccbc9a", "#e2d6b8"), R("#3e352c", "#574c40")),
    ("honeystone", "Honeystone", R("#5a4026", "#7c5a34", "#9e7844", "#ba9458", "#d2ae70", "#e6ca90"), R("#3e2e20", "#5a4632")),
    ("rosestone", "Rosestone", R("#5a3a38", "#7a504c", "#986862", "#b48278", "#cc9e90", "#e0bcac"), R("#40302e", "#5a4844")),
    ("duskstone", "Duskstone", R("#2c323e", "#404856", "#565f70", "#6e7a8a", "#8a96a4", "#a8b2be"), R("#22262e", "#383e48")),
    ("ashstone", "Ashstone", R("#3a3836", "#524f4b", "#6b6761", "#858078", "#a09a90", "#bab4a8"), R("#2a2826", "#43403c")),
)

blocks = []
for n, t, ramp, mortar in STONES:
    blocks += [
        B(n + "_bricks", t + " Bricks", "hewn", family=("stairs", "slab", "wall"), stem=n + "_brick",
          stem_title=t + " Brick", args=dict(ramp=ramp, mortar=mortar)),
        B(n + "_quoin", t + " Quoin", "hewn", args=dict(ramp=ramp, mortar=mortar, big=True)),
        B("cracked_" + n + "_bricks", "Cracked " + t + " Bricks", "hewn", args=dict(ramp=ramp, mortar=mortar, crack=True)),
    ]
dungeon("highmourn", blocks=blocks)
