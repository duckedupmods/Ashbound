"""A sheet of stick figures: one Epic Fight animation at several times, to pick a pose for a concept.
  blender -b -P tools/blender/efpose_sheet.py -- <armature> <anim> t1 t2 ...  ->  tools/renders/dungeon/pose_<anim>_<t>.png"""
import os, sys, math
import bpy, bmesh
from mathutils import Vector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import efrig

A = sys.argv[sys.argv.index("--") + 1:]
arm = efrig.Armature(A[0])
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "renders", "dungeon", "poses")
os.makedirs(OUT, exist_ok=True)
for t in map(float, A[2:]):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.render.resolution_x = sc.render.resolution_y = 360
    pose = arm.pose(A[1], t)
    bm = bmesh.new()
    for j in arm.joints:
        h, tl = arm.segment(j)
        m = pose[j] @ arm.bind[j].inverted()
        a, b = m @ h, m @ tl
        d = b - a
        if d.length < 1e-3:
            continue
        q = d.to_track_quat("Z", "Y").to_matrix().to_4x4()
        r = 0.06 if j in ("Torso", "Chest") else 0.035
        bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=r, radius2=r * 0.7, depth=d.length,
                              matrix=__import__("mathutils").Matrix.Translation((a + b) / 2) @ q)
        bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=6, radius=r * 1.2,
                                  matrix=__import__("mathutils").Matrix.Translation(a))
    hd = pose["Head"].to_translation() if "Head" in pose else Vector()
    me = bpy.data.meshes.new("s")
    bm.to_mesh(me)
    sc.collection.objects.link(bpy.data.objects.new("s", me))
    cd = bpy.data.cameras.new("c")
    cam = bpy.data.objects.new("c", cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.location = (3.6, 1.2, 1.3)
    cam.rotation_euler = (Vector((0, 0, 0.8)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    cd.lens = 28
    sc.render.filepath = os.path.join(OUT, "pose_%s_%.2f.png" % (A[1].split("/")[-1], t))
    bpy.ops.render.render(write_still=True)
