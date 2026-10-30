"""Brings Ashbound's weapons over to the Epic Fight add-on.

For each weapon in WEAPONS it copies our own mesh and textures out of E:/Ashbound, gives the mesh a
material for NeoForge's OBJ loader, writes the item model (3D in hand, the flat icon in menus), the Epic
Fight weapon data (which of Epic Fight's movesets it swings with) and its name, and regenerates
Weapons.java with the items' stats. Run: python tools/port_weapons.py
"""
import json
import os
import shutil

SRC = 'E:/Ashbound/src/main/resources/assets/ashbound/'
GAME = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace('\\', '/') + '/'
ASSETS = GAME + 'src/main/resources/assets/ashbound/'
DATA = GAME + 'src/main/resources/data/ashbound/'
JAVA = GAME + 'src/main/java/com/snoringwalrus/ashbound/Weapons.java'

# name, Epic Fight weapon type, damage, attack speed, durability, impact, armour negation, most targets per swing
WEAPONS = [
    ('kiln_blade', 'sword', 7.5, 1.6, 1500, 0.8, 10, 1),
    ('kiln_fang', 'dagger', 5.5, 2.4, 1200, 0.4, 15, 1),
    ('kiln_pike', 'spear', 8.5, 1.2, 1400, 1.2, 20, 2),
    # no hammer type in Epic Fight: the maul swings with the greatsword's heavy two-handed moves
    ('kiln_maul', 'greatsword', 11.0, 0.85, 1500, 3.2, 30, 3),
    ('kiln_greatsword', 'greatsword', 14.5, 0.85, 2000, 2.8, 20, 3),
]


def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=1)


def material(name, path):
    """Gives a mesh its materials for NeoForge's OBJ loader: the weapon's texture, and for the "fire" group
    the same texture full-bright (an ambient colour of white is read as emitted light)."""
    lines = ['mtllib %s.mtl' % name]
    for l in open(path, encoding='utf-8').read().splitlines():
        if l.startswith(('mtllib', 'usemtl')):
            continue
        lines.append(l)
        if l.startswith('g '):
            lines.append('usemtl ' + ('glow' if l.split()[1] == 'fire' else 'blade'))
    open(path, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    tex = 'ashbound:item/%s_3d' % name
    open(path[:-4] + '.mtl', 'w', encoding='utf-8').write(
        'newmtl blade\nKa 0 0 0\nmap_Kd %s\n\nnewmtl glow\nKa 1 1 1\nmap_Kd %s\n' % (tex, tex))


def port(name, kind, impact, negation, strikes):
    os.makedirs(ASSETS + 'textures/item', exist_ok=True)
    for t in (name, name + '_3d'):
        shutil.copy(SRC + 'textures/item/' + t + '.png', ASSETS + 'textures/item/' + t + '.png')
    os.makedirs(ASSETS + 'models/mesh', exist_ok=True)
    shutil.copy(SRC + 'models/mesh/%s.obj' % name, ASSETS + 'models/mesh/%s.obj' % name)
    material(name, ASSETS + 'models/mesh/%s.obj' % name)
    held = json.load(open(SRC + 'models/item/%s_held.json' % name, encoding='utf-8'))
    icon = {'parent': 'minecraft:item/generated', 'textures': {'layer0': 'ashbound:item/' + name}}
    dump(ASSETS + 'models/item/%s.json' % name, {
        'loader': 'neoforge:separate_transforms', 'gui_light': 'front',
        'base': {'loader': 'neoforge:obj', 'model': 'ashbound:models/mesh/%s.obj' % name, 'flip_v': True,
                 'display': held.get('display', {})},
        'perspectives': {k: icon for k in ('gui', 'ground', 'fixed')}})
    dump(DATA + 'capabilities/weapons/%s.json' % name, {
        'type': ('ashbound:' if kind == 'greatsword' else 'epicfight:') + kind,   # Movesets.java
        'attributes': {'common': {'impact': impact, 'armor_negation': negation, 'max_strikes': strikes}}})


def main():
    names = json.load(open(SRC + 'lang/en_us.json', encoding='utf-8'))
    try:
        lang = json.load(open(ASSETS + 'lang/en_us.json', encoding='utf-8'))
    except FileNotFoundError:
        lang = {}
    rows = []
    for name, kind, dmg, speed, dur, impact, neg, strikes in WEAPONS:
        port(name, kind, impact, neg, strikes)
        lang['item.ashbound.' + name] = names['item.ashbound.' + name]
        rows.append('\t\tweapon("%s", %sf, %sf, %d);' % (name, dmg, speed, dur))
    dump(ASSETS + 'lang/en_us.json', lang)
    java = open(JAVA, encoding='utf-8').read()
    a, b = java.index('\t// generated: weapons\n'), java.index('\t// end generated\n')
    java = java[:a] + '\t// generated: weapons\n\tstatic void all() {\n' + '\n'.join(rows) + '\n\t}\n' + java[b:]
    open(JAVA, 'w', encoding='utf-8').write(java)
    print('ported', len(WEAPONS), 'weapons')


if __name__ == '__main__':
    main()
