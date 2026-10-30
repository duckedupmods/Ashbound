"""The Ashbound logo's picture: a black greatsword driven down through a burning crack in the world, chained from the
four corners. tools/logo.py frames and letters it.

    blender -b -P tools/blender/logo.py -- tools/renders/logo
"""
import math
import os
import random
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(__file__))
import vfx_concepts as V
import vfx_mage as M

SIZE, SAMPLES = 1024, 220
GUARD, TIP = 2.08, -2.5       # the blade, top and point
FIRE = (V.lin(0x8A1206), V.lin(0xF05A18), V.lin(0xFFC050))


def iron(rough=0.3, base=0.035):
    m = bpy.data.materials.new("iron")
    m.use_nodes = True
    nt = m.node_tree
    p = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (base, base * 0.92, base * 0.9, 1)
    p.inputs["Metallic"].default_value = 1
    tx = nt.nodes.new("ShaderNodeTexNoise")
    tx.inputs["Scale"].default_value = 70
    tx.inputs["Detail"].default_value = 9
    ramp = nt.nodes.new("ShaderNodeMapRange")
    ramp.inputs["To Min"].default_value = rough - 0.16
    ramp.inputs["To Max"].default_value = rough + 0.3
    ramp.inputs["From Min"].default_value = 0.35
    ramp.inputs["From Max"].default_value = 0.65
    nt.links.new(tx.outputs[0], ramp.inputs["Value"])
    nt.links.new(ramp.outputs[0], p.inputs["Roughness"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.12
    bump.inputs["Distance"].default_value = 0.01
    nt.links.new(tx.outputs[0], bump.inputs["Height"])
    nt.links.new(bump.outputs[0], p.inputs["Normal"])
    return m


def stone():
    """the wall of the world the crack tears: dark, broken slabs that only the fire shows"""
    m = bpy.data.materials.new("stone")
    m.use_nodes = True
    nt = m.node_tree
    p = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (0.012, 0.01, 0.01, 1)
    p.inputs["Roughness"].default_value = 0.8
    vo = nt.nodes.new("ShaderNodeTexVoronoi")
    vo.feature = "DISTANCE_TO_EDGE"
    vo.inputs["Scale"].default_value = 1.5
    tx = nt.nodes.new("ShaderNodeTexNoise")
    tx.inputs["Scale"].default_value = 5
    tx.inputs["Detail"].default_value = 11
    ramp = nt.nodes.new("ShaderNodeMapRange")
    ramp.inputs["From Max"].default_value = 0.06
    nt.links.new(vo.outputs["Distance"], ramp.inputs["Value"])
    mix = nt.nodes.new("ShaderNodeMath")
    mix.operation = "MULTIPLY"
    nt.links.new(ramp.outputs[0], mix.inputs[0])
    nt.links.new(tx.outputs[0], mix.inputs[1])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 1
    bump.inputs["Distance"].default_value = 0.5
    nt.links.new(mix.outputs[0], bump.inputs["Height"])
    nt.links.new(bump.outputs[0], p.inputs["Normal"])
    return m


def mesh(name, verts, faces, mat, smooth=False):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    if smooth:
        for f in me.polygons:
            f.use_smooth = True
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat)
    return o


def blade(mat):
    """a heavy two-hander, point down: a section with a fuller, a broken edge, wider at the shoulder"""
    R = random.Random(11)
    notch = sorted((R.uniform(0.08, 0.84), R.uniform(0.012, 0.024), R.uniform(0.05, 0.11), R.choice((-1, 1))) for _ in range(11))
    rows, faces, N = [], [], 120
    for i in range(N + 1):
        t = i / N
        w = 0.42 - 0.12 * t
        if t > 0.78:
            w *= (1 - t) / 0.22
        z = GUARD + (TIP - GUARD) * t
        left, right = w, w
        for at, wide, deep, side in notch:
            cut = max(0, 1 - abs(t - at) / wide) * deep
            if side < 0:
                left -= cut
            else:
                right -= cut
        th = 0.08 * max(0.1, min(1, w / 0.3))
        fuller = 0.42 if t < 0.72 else 0.42 + (t - 0.72) * 3
        rows.append([(-left, 0, z), (-w * 0.56, -th, z), (-w * 0.16, -th * fuller, z), (w * 0.16, -th * fuller, z), (w * 0.56, -th, z), (right, 0, z),
                     (w * 0.56, th, z), (w * 0.16, th * fuller, z), (-w * 0.16, th * fuller, z), (-w * 0.56, th, z)])
    verts = [v for r in rows for v in r]
    for i in range(N):
        for k in range(10):
            a, b = i * 10 + k, i * 10 + (k + 1) % 10
            faces.append((a, b, b + 10, a + 10))
    faces += [tuple(range(10))]
    return mesh("blade", verts, faces, mat)


def sweep(path, wide, deep, mat, name="sweep"):
    """a diamond section along a path in the picture's plane: wide across it, deep front to back"""
    verts, faces, n = [], [], len(path)
    for i, (x, z) in enumerate(path):
        ax, az = path[min(i + 1, n - 1)], path[max(i - 1, 0)]
        dx, dz = ax[0] - az[0], ax[1] - az[1]
        l = math.hypot(dx, dz) or 1
        nx, nz = -dz / l, dx / l
        verts += [(x + nx * wide[i], 0, z + nz * wide[i]), (x, -deep[i], z), (x - nx * wide[i], 0, z - nz * wide[i]), (x, deep[i], z)]
    for i in range(n - 1):
        for k in range(4):
            a, b = i * 4 + k, i * 4 + (k + 1) % 4
            faces.append((a, b, b + 4, a + 4))
    return mesh(name, verts, faces, mat)


def plate(pts, thick, y, mat, name="plate"):
    """a flat convex shape, its edges chamfered"""
    o = mesh(name, [(x, y - thick, z) for x, z in pts] + [(x, y + thick, z) for x, z in pts],
             [tuple(range(len(pts)))[::-1], tuple(range(len(pts), len(pts) * 2))] + [(k, (k + 1) % len(pts), (k + 1) % len(pts) + len(pts), k + len(pts)) for k in range(len(pts))], mat)
    b = o.modifiers.new("b", "BEVEL")
    b.width = thick * 0.7
    b.segments = 2
    b.angle_limit = math.radians(25)
    return o


def hilt(mat):
    z = GUARD
    # a swept guard: down at the blade, up and out to two points
    for sx in (-1, 1):
        path, wide, deep = [], [], []
        for i in range(25):
            t = i / 24
            path.append((sx * 1.72 * t, z + 0.06 - 0.1 * math.sin(t * 2.6) + 0.72 * t ** 3.2))
            wide.append(0.17 * (1 - t) ** 0.75 + 0.006)
            deep.append(0.12 * (1 - t) ** 0.6 + 0.006)
        sweep(path, wide, deep, mat, "guard")
    plate([(0, z + 0.32), (0.3, z + 0.14), (0.42, z - 0.04), (0.2, z - 0.32), (0, z - 0.42), (-0.2, z - 0.32), (-0.42, z - 0.04), (-0.3, z + 0.14)], 0.13, 0, mat, "heart")
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.1, depth=0.72, location=(0, 0, z + 0.56))
    bpy.context.active_object.data.materials.append(iron(0.6, 0.02))
    for i in range(6):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.104, minor_radius=0.024, location=(0, 0, z + 0.27 + i * 0.115), rotation=(0.09, 0.14, 0))
        bpy.context.active_object.data.materials.append(mat)
    top = z + 0.92
    path = [(0, top + (i / 16) * 0.72) for i in range(17)]
    w = [0.05 + 0.2 * math.sin(math.pi * min(1, i / 8)) ** 0.7 if i < 8 else 0.25 * (1 - (i - 8) / 8) ** 1.5 + 0.004 for i in range(17)]
    sweep(path, w, [v * 0.7 for v in w], mat, "pommel")
    # the ember set in the guard, and the heat in the fuller
    M.ball((0, -0.16, z - 0.04), 0.09, V.lin(0xFF5A18), 3)
    pts, R = [], random.Random(5)
    for i in range(30):
        t = 0.05 + 0.6 * i / 29
        pts.append((R.uniform(-0.022, 0.022), -0.05, GUARD + (TIP - GUARD) * t))
    M.tube(pts, 0.009, V.lin(0xFF5A18), 5)


def chain(a, b, sag, mat, seed):
    """iron links from a to b, each through the last and turned a quarter from it"""
    a, b = Vector(a), Vector(b)
    span = (b - a).length
    major, minor, long = 0.15, 0.05, 1.45
    pitch = 2 * (major * long - minor) * 0.98
    n = int(span / pitch)
    R = random.Random(seed)

    def at(t):
        return a.lerp(b, t) + Vector((0, 0, -sag * 4 * t * (1 - t)))
    for i in range(n):
        t = (i + 0.5) / n
        p, d = at(t), (at(t + 0.01) - at(t - 0.01)).normalized()
        turn = math.radians(45 + 90 * (i % 2) + R.uniform(-7, 7))
        side = d.cross(Vector((0, 1, 0))).normalized()
        up = d.cross(side).normalized()
        u = side * math.cos(turn) + up * math.sin(turn)
        w = d.cross(u).normalized()
        bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=24, minor_segments=8, location=p)
        o = bpy.context.active_object
        for v in o.data.vertices:
            v.co.x *= long
        o.matrix_world = Matrix((d, u, w)).transposed().to_4x4()
        o.location = p
        o.data.materials.append(mat)
        for f in o.data.polygons:
            f.use_smooth = True


def crack():
    """the tear: it starts at the sword's point and opens upward like a flame, red at the lip, white-gold at the heart"""
    N = 90

    def edge(sign, inset, seed):
        R, out = random.Random(seed), []
        for i in range(N + 1):
            t = i / N
            z = -2.6 + 7.4 * t
            wide = (2.15 * math.sin(math.pi * t ** 0.62) ** 1.25 + 0.02) * (1 - inset)
            jag = (R.uniform(-0.3, 0.3) if i % 6 == 0 else R.uniform(-0.09, 0.09)) * (1 - inset) * min(1, wide * 2)
            out.append((sign * max(0.01, wide + jag) + 0.14 * math.sin(z * 1.3) * min(1, t * 3), z))
        return out
    y = 2.0
    for inset, rgb, strength, name in ((0.0, V.lin(0x6A0C04), 1.1, "lip"), (0.2, V.lin(0xD83A0C), 1.9, "fire"), (0.46, V.lin(0xFF8A20), 2.6, "heart"), (0.72, V.lin(0xFFD070), 3.6, "core")):
        y -= 0.03
        l, r = edge(-1, inset, 3 + int(inset * 50)), edge(1, inset, 9 + int(inset * 50))
        pts = l + r[::-1]
        mesh(name, [(x, y, z) for x, z in pts], [tuple(range(len(pts)))], V.glow_mat(rgb, strength, soft=False, noise=7.0, seed=int(inset * 10)))


def main(out):
    sc = V.reset()
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs[1].default_value = 0
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.render.resolution_x = sc.render.resolution_y = SIZE
    sc.cycles.samples = SAMPLES
    sc.cycles.max_bounces = 8

    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.data.lens = 85
    cam.location = (0, -21, 0.1)
    cam.rotation_euler = (math.radians(90), 0, 0)
    sc.collection.objects.link(cam)
    sc.camera = cam

    bpy.ops.mesh.primitive_plane_add(size=16, location=(0, 2.1, 0), rotation=(math.radians(90), 0, 0))
    bpy.context.active_object.data.materials.append(stone())
    crack()
    steel, links = iron(), iron(0.34, 0.16)
    blade(steel)
    hilt(steel)
    # the band on the blade, and the chains that hold it from the corners of the world
    plate([(-0.42, -0.1), (0.42, -0.1), (0.48, 0.0), (0.42, 0.1), (-0.42, 0.1), (-0.48, 0.0)], 0.17, 0, steel, "band")
    for sx in (-1, 1):
        chain((sx * 5.4, 0.3, 4.2), (sx * 0.5, -0.12, 0.08), 0.3, links, sx + 3)
        chain((sx * 5.4, 0.3, -2.9), (sx * 0.5, -0.12, -0.08), 0.12, links, sx + 7)

    # fire over the crack; the iron shows only as an edge against it, a little ember from the sides for the chains
    for at, r, seed, tall in (((-0.72, 1.6, 2.6), 0.62, 3, 2.2), ((0.72, 1.6, 2.0), 0.66, 7, 2.4), ((-0.95, 1.6, 0.1), 0.56, 9, 1.9), ((0.9, 1.6, -0.7), 0.5, 11, 1.8), ((0, 1.6, 3.5), 0.4, 13, 1.8)):
        M.burn(at, r, FIRE, strength=4.5, density=5, scale=4.2, seed=seed, stretch=(1, 0.5, tall))
    V.light((-3.2, -2.6, 2.2), V.lin(0xFF5A20), 90, 1.0)
    V.light((3.2, -2.6, 2.2), V.lin(0xFF5A20), 90, 1.0)
    V.light((-3.2, -2.6, -1.8), V.lin(0xFF4818), 60, 1.0)
    V.light((3.2, -2.6, -1.8), V.lin(0xFF4818), 60, 1.0)
    M.embers((0, 0.4, 0.8), 170, 4.6, V.lin(0xFF7A28), seed=4, up=0.5, length=(0.03, 0.1), strength=3)

    sc.render.filepath = os.path.join(out, "picture.png")
    bpy.ops.render.render(write_still=True)
    print("rendered logo", flush=True)


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1])
