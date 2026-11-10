"""The sixteen older staffs the weapon pass missed (their 10/29 renders), on the staff kit's shaft (see
tools/weaponicons_staffkit.py, tools/itemicons.py)."""
import itemicons  # noqa: F401  (the staff kit draws into the same list)
from weaponicons_staffkit import st

CROOK = """
.........oooo...
........oggGGo..
.......ogoooGGo.
.......ogo..oGo.
........o...oGo.
...........oGo..
..........owo...
"""


st("aurora_staff", "o=0e0e16 k=1e1e2a s=6a7aa0 h=ffffff y=c8e8ff w=2a2a34", """
..........ooo...
.........oksko..
........okshsko.
........oshyhso.
........okshsko.
.........oksko..
........owooo...
""")

st("bonefire_staff", "o=100a06 b=2e2a28 e=ff8a30 x=ffffff y=ffd060 w=3a3a3a", """
..........ooo...
.........obbbo..
........obeyebo.
........obyxybo.
........obeyebo.
.........obbbo..
........owooo...
""")

st("coilcaller", "o=0a140e g=5aa070 G=2e6a44 w=3a5a3a", CROOK)
st("djinn_lamp", "o=1a1004 g=ecc464 G=a07828 w=4a3a2a", CROOK)
st("draugrcaller", "o=0a0a0e g=6e6e78 G=3a3a44 w=2a2a30", CROOK)
st("goblincaller", "o=1a140a g=dcd0ae G=9a8e6a w=4a3a2a", CROOK)
st("scorpion_rod", "o=1a1004 g=ecc464 G=a07828 w=2a6a6a", CROOK)
st("war_drum", "o=0e0a08 g=8e9298 G=4a4e56 w=3a2a20", CROOK)

st("coiled_sun", "o=1a1004 y=f2c14e Y=a8701f h=fff4c0 x=ffffff w=2a3a2a", """
..........ooo...
.........oyYyo..
........oyohoYo.
........oYhxhYo.
........oyohoYo.
.........oYyYo..
.........owo....
""")

st("dawn_lamp", "o=081414 t=64e4d4 T=2a9a8a k=1a2a2a x=ffffff w=4a2a2a", """
..........ooo...
.........otTto..
........otkkkto.
........oTkxkTo.
........otkkkto.
.........otTto..
.........owo....
""")

st("jade_censer", "o=081410 g=4e9e6e G=2a5a3e k=0e1a12 x=a8ffc4 w=1e3a28", """
..........ooo...
.........ogGgo..
........ogkkkgo.
........oGkxkGo.
........ogkkkgo.
.........ogGgo..
.........owo....
""")

st("frozen_crown", "o=0e1220 h=ffffff c=cce8ff C=8ab8e0 w=2a2a34", """
.........oooo...
........ohhhho..
........ohhhcCo.
........ohhcCCo.
.........occCo..
..........ooo...
.........owo....
""")

st("rune_staff", "o=0a0e16 h=ffffff S=8e9eac w=1e2a3a", """
..........o.o...
.........ohohSo.
..........ohSo..
.........ohhSSo.
..........ohSo..
..........oSo...
.........owo....
""")

st("sandwraith_censer", "o=0e1410 t=74e4d4 T=2a9a8a y=ecc464 Y=a07828 w=8e6e3e", """
...........oo...
..........otto..
.........otTTto.
..........oyyo..
..........otTo..
..........oyYo..
.........owo....
""")

st("shaman_rattle", "o=140e08 h=fff4e0 y=cca464 w=2a2a2a", """
..........o.oo..
...........ohho.
..........ohhho.
.........oyhhyo.
.........oyyyo..
..........oyo...
.........owo....
""")

st("venom_staff", "o=0a140a h=e4ffd4 g=64c444 G=2e7020 w=1e3a1e", """
............oo..
...........ohgo.
..........ohgGo.
..........ogGo..
.........ogGo...
.........oGo....
........owo.....
""")
