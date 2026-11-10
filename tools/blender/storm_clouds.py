"""The gate storm's clouds for the game (client/StormSky): the deck of gate_storm.py baked to one picture, looking straight
up at it from below, with alpha (how thick the cloud is), its spiral turning round the eye, the gate's red glowing round
the eye. The game lays it on three discs at different heights and turns them at different speeds.
  blender -b -P tools/blender/storm_clouds.py -- [fast]  ->  src/main/resources/assets/ashbound/textures/entity/storm_clouds.png"""
import os, sys, math
import bpy, bmesh

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "..", "src", "main", "resources", "assets", "ashbound", "textures", "entity", "storm_clouds.png"))
R = 180.0                     # the deck's radius (the picture spans 2R)
BASE_Z, TOP_Z = 0.0, 34.0
EYE_R = 7.0                   # small: the tear itself is the eye
HOT = (1.0, 0.13, 0.06)       # tinted again in game per rank; red reads for all

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
try:
    cp = bpy.context.preferences.addons["cycles"].preferences
    cp.compute_device_type = "OPTIX"
    cp.get_devices()
    for d in cp.devices:
        d.use = d.type == "OPTIX"
    sc.cycles.device = "GPU"
except Exception as e:
    print("gpu", e)
sc.cycles.samples = 32 if "fast" in ARGS else 128
sc.cycles.use_denoising = True
sc.cycles.volume_bounces = 2
sc.cycles.volume_step_rate = 2.0
sc.render.film_transparent = True
sc.render.resolution_x = sc.render.resolution_y = 512 if "fast" in ARGS else 1024
sc.view_settings.view_transform = "Standard"
sc.render.image_settings.color_mode = "RGBA"

w = bpy.data.worlds.new("w")
sc.world = w
w.use_nodes = True
bg = w.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.5, 0.52, 0.58, 1)
bg.inputs["Strength"].default_value = 0.6
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(20), 0, math.radians(30))
sc.collection.objects.link(sun)


def N(nt, kind, **inputs):
    n = nt.nodes.new(kind)
    for k, v in inputs.items():
        if k.startswith("_"):
            setattr(n, k[1:], v)
        else:
            n.inputs[k].default_value = v
    return n


def L(nt, a, b):
    nt.links.new(a, b)


def M(nt, op, a=None, b=None, va=0.0, vb=0.0):
    n = nt.nodes.new("ShaderNodeMath")
    n.operation = op
    n.inputs[0].default_value = va
    n.inputs[1].default_value = vb
    if a is not None:
        L(nt, a, n.inputs[0])
    if b is not None:
        L(nt, b, n.inputs[1])
    return n.outputs[0]


def S(nt, x, a, b):
    m = N(nt, "ShaderNodeMapRange", _interpolation_type="SMOOTHSTEP", **{"From Min": a, "From Max": b})
    L(nt, x, m.inputs["Value"])
    return m.outputs[0]


m = bpy.data.materials.new("cloud")
m.use_nodes = True
nt = m.node_tree
for n in list(nt.nodes):
    nt.nodes.remove(n)
out = N(nt, "ShaderNodeOutputMaterial")
pos = N(nt, "ShaderNodeNewGeometry").outputs["Position"]
sp = N(nt, "ShaderNodeSeparateXYZ")
L(nt, pos, sp.inputs[0])
r = M(nt, "SQRT", M(nt, "ADD", M(nt, "MULTIPLY", sp.outputs["X"], sp.outputs["X"]), M(nt, "MULTIPLY", sp.outputs["Y"], sp.outputs["Y"])))
twist = M(nt, "MULTIPLY", M(nt, "EXPONENT", M(nt, "MULTIPLY", r, vb=-1 / 60)), vb=6.0)
rot = N(nt, "ShaderNodeVectorRotate", _rotation_type="Z_AXIS")
L(nt, pos, rot.inputs["Vector"])
L(nt, twist, rot.inputs["Angle"])
sq = N(nt, "ShaderNodeVectorMath", _operation="MULTIPLY")
sq.inputs[1].default_value = (1.0, 1.0, 2.2)
L(nt, rot.outputs[0], sq.inputs[0])
nb = N(nt, "ShaderNodeTexNoise", Scale=0.02, Detail=7.0, Roughness=0.58, Distortion=0.4)
L(nt, sq.outputs[0], nb.inputs["Vector"])
nf = N(nt, "ShaderNodeTexNoise", Scale=0.1, Detail=4.0, Roughness=0.6)
L(nt, sq.outputs[0], nf.inputs["Vector"])
lump = M(nt, "ADD", nb.outputs["Fac"], M(nt, "MULTIPLY", M(nt, "SUBTRACT", nf.outputs["Fac"], vb=0.5), vb=0.35))
foot = M(nt, "ADD", M(nt, "MULTIPLY", nb.outputs["Fac"], vb=-10.0), vb=BASE_Z + 6)
above = S(nt, M(nt, "SUBTRACT", sp.outputs["Z"], foot), 0.0, 4.0)
below = S(nt, sp.outputs["Z"], TOP_Z, TOP_Z - 8)
wall = M(nt, "ADD", M(nt, "ADD", M(nt, "MULTIPLY", sp.outputs["Z"], vb=0.25), vb=EYE_R),
         M(nt, "MULTIPLY", M(nt, "SUBTRACT", nf.outputs["Fac"], vb=0.5), vb=8.0))
out_eye = S(nt, M(nt, "SUBTRACT", r, wall), 0.0, 9.0)
edge = S(nt, r, R * 0.98, R * 0.7)
pile = M(nt, "MULTIPLY", M(nt, "EXPONENT", M(nt, "MULTIPLY", r, vb=-1 / 70)), vb=0.2)
dens = M(nt, "MULTIPLY", S(nt, M(nt, "ADD", lump, pile), 0.44, 0.62), above)
dens = M(nt, "MULTIPLY", M(nt, "MULTIPLY", dens, below), M(nt, "MULTIPLY", out_eye, edge))
vol = N(nt, "ShaderNodeVolumePrincipled")
vol.inputs["Color"].default_value = (0.24, 0.24, 0.27, 1)
vol.inputs["Anisotropy"].default_value = 0.2
L(nt, M(nt, "MULTIPLY", dens, vb=0.3), vol.inputs["Density"])
glow = M(nt, "MULTIPLY", M(nt, "EXPONENT", M(nt, "MULTIPLY", M(nt, "SUBTRACT", r, wall), vb=-1 / 16)),
         M(nt, "MULTIPLY", dens, S(nt, nf.outputs["Fac"], 0.38, 0.68)))
vol.inputs["Emission Color"].default_value = (*HOT, 1)
L(nt, M(nt, "MULTIPLY", glow, vb=1.4), vol.inputs["Emission Strength"])
L(nt, vol.outputs[0], out.inputs["Volume"])

bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, segments=64, radius1=R, radius2=R, depth=TOP_Z - BASE_Z + 16)
me = bpy.data.meshes.new("deck")
bm.to_mesh(me)
ob = bpy.data.objects.new("deck", me)
ob.location = (0, 0, (BASE_Z - 10 + TOP_Z + 6) / 2)
me.materials.append(m)
sc.collection.objects.link(ob)

cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
cam.data.type = "ORTHO"
cam.data.ortho_scale = 2 * R
cam.data.clip_end = 500
cam.location = (0, 0, BASE_Z - 40)
cam.rotation_euler = (math.pi, 0, 0)   # looking straight up
sc.collection.objects.link(cam)
sc.camera = cam
sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("WROTE", OUT)
