"""Textured materials for the monsters (Cycles): layered like a painted texture set, not flat colours.
Every material stacks a base with large mottling, cavity grime (ambient occlusion), worn edges (pointiness), fine
surface detail in the bump, and the stains of the Archive (ink, dust, silk). Built from nodes so they can be baked
to UV textures for the game.
    import monster_tex as T; m = T.skin("scholar_skin")"""
import bpy


class _M:
    """a material under construction: n(type, **inputs) makes a node, l(out, in) links"""

    def __init__(self, name):
        self.m = bpy.data.materials.new(name)
        self.m.use_nodes = True
        self.t = self.m.node_tree
        self.b = next(x for x in self.t.nodes if x.type == "BSDF_PRINCIPLED")
        self.co = self.n("ShaderNodeAttribute", _attribute_name="rest", _attribute_type="GEOMETRY").outputs["Vector"]

    def n(self, kind, **kw):
        x = self.t.nodes.new(kind)
        for k, v in kw.items():
            if k.startswith("_"):
                setattr(x, k[1:], v)
            else:
                x.inputs[k].default_value = v
        return x

    def l(self, a, b):
        self.t.links.new(a, b)

    def noise(self, scale, detail=4.0, rough=0.55, distort=0.0, vec=None):
        x = self.n("ShaderNodeTexNoise", Scale=scale, Detail=detail, Roughness=rough, Distortion=distort)
        self.l(vec or self.co, x.inputs["Vector"])
        return x.outputs["Fac"]

    def ramp(self, fac, a, b, lo=0.0, hi=1.0):
        """fac mapped through lo..hi to a value from a to b (clamped)"""
        x = self.n("ShaderNodeMapRange", **{"From Min": lo, "From Max": hi, "To Min": a, "To Max": b})
        self.l(fac, x.inputs["Value"])
        return x.outputs["Result"]

    def mix(self, fac, a, b, blend="MIX"):
        x = self.n("ShaderNodeMix", _data_type="RGBA", _blend_type=blend, _clamp_result=True)
        # the Mix node carries float, vector and colour sockets under the same names: the colour ones are 6, 7 -> 2
        self.l(fac, x.inputs[0])
        for sock, v in ((6, a), (7, b)):
            if isinstance(v, tuple):
                x.inputs[sock].default_value = (*v, 1) if len(v) == 3 else v
            else:
                self.l(v, x.inputs[sock])
        return x.outputs[2]

    def math(self, op, a, b=None, clamp=True):
        x = self.n("ShaderNodeMath", _operation=op, _use_clamp=clamp)
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                x.inputs[i].default_value = v
            else:
                self.l(v, x.inputs[i])
        return x.outputs["Value"]

    def cavity(self, dist=0.04):
        """1 out in the open, toward 0 deep in a crevice"""
        x = self.n("ShaderNodeAmbientOcclusion", Distance=dist)
        x.samples = 8
        return x.outputs["AO"]

    def edges(self, lo=0.5, hi=0.56):
        """0 on flat and hollow surface, 1 on sharp outer edges (worn first)"""
        g = self.n("ShaderNodeNewGeometry")
        return self.ramp(g.outputs["Pointiness"], 0.0, 1.0, lo, hi)

    def up(self):
        """how much a surface faces the sky (dust settles there)"""
        g = self.n("ShaderNodeNewGeometry")
        sep = self.n("ShaderNodeSeparateXYZ")
        self.l(g.outputs["Normal"], sep.inputs["Vector"])
        return self.ramp(sep.outputs["Z"], 0.0, 1.0, 0.3, 0.95)

    def bump(self, height, strength, dist=0.003, normal=None):
        x = self.n("ShaderNodeBump", Strength=strength, Distance=dist)
        self.l(height, x.inputs["Height"])
        if normal is not None:
            self.l(normal, x.inputs["Normal"])
        return x.outputs["Normal"]

    def stretch(self, sx, sy, sz):
        x = self.n("ShaderNodeMapping", Scale=(sx, sy, sz))
        self.l(self.co, x.inputs["Vector"])
        return x.outputs["Vector"]

    def out(self, color, rough=None, normal=None, **kw):
        self.l(color, self.b.inputs["Base Color"])
        if rough is not None:
            if isinstance(rough, (int, float)):
                self.b.inputs["Roughness"].default_value = rough
            else:
                self.l(rough, self.b.inputs["Roughness"])
        if normal is not None:
            self.l(normal, self.b.inputs["Normal"])
        for k, v in kw.items():
            if isinstance(v, (int, float, tuple)):
                self.b.inputs[k].default_value = (*v, 1) if isinstance(v, tuple) and len(v) == 3 else v
            else:
                self.l(v, self.b.inputs[k])
        return self.m


def skin(name, base=(0.12, 0.105, 0.115), bruise=(0.05, 0.055, 0.085), ink_attr="ink"):
    """dead grey-violet skin: bruised mottling, dark veins under it, grime in every fold, wet ink stains from the
    hands up with ragged edges, pores and fine wrinkles"""
    M = _M(name)
    mott = M.noise(2.6, 6, 0.6)
    col = M.mix(M.ramp(mott, 0, 1, 0.38, 0.68), base, bruise)
    blot = M.noise(11, 3, 0.5)
    col = M.mix(M.ramp(blot, 0, 0.35, 0.55, 0.75), col, (0.16, 0.09, 0.09))          # reddish blotches
    vor = M.n("ShaderNodeTexVoronoi", _feature="DISTANCE_TO_EDGE", Scale=3.5, Randomness=1.0)
    warp = M.n("ShaderNodeTexNoise", Scale=3.0, Detail=2.0)
    M.l(M.co, warp.inputs["Vector"])
    wv = M.n("ShaderNodeVectorMath", _operation="ADD")
    M.l(M.co, wv.inputs[0])
    sc_ = M.n("ShaderNodeVectorMath", _operation="SCALE", Scale=0.25)
    M.l(warp.outputs["Color"], sc_.inputs[0])
    M.l(sc_.outputs["Vector"], wv.inputs[1])
    M.l(wv.outputs["Vector"], vor.inputs["Vector"])
    vein = M.ramp(vor.outputs["Distance"], 0.55, 0.0, 0.0, 0.01)
    col = M.mix(vein, col, (0.02, 0.025, 0.05))
    cav = M.cavity(0.05)
    col = M.mix(M.ramp(cav, 0.85, 0.0, 0.2, 1.0), col, (0.01, 0.008, 0.01))         # grime in the folds
    edge = M.edges(0.55, 0.65)
    col = M.mix(M.math("MULTIPLY", edge, 0.15), col, (0.3, 0.28, 0.3))              # sheen on the ridges
    at = M.n("ShaderNodeAttribute", _attribute_name=ink_attr).outputs["Fac"]
    ragged = M.noise(7, 5, 0.65)
    ink = M.ramp(M.math("ADD", M.math("MULTIPLY", at, 1.4), M.math("SUBTRACT", ragged, 0.55)), 0, 1, 0.45, 0.55)
    col = M.mix(ink, col, (0.004, 0.004, 0.007))
    rough = M.ramp(ink, 0.5, 0.08)
    pores = M.noise(160, 2, 0.5)
    wr = M.noise(28, 4, 0.55, distort=0.6)
    h = M.math("ADD", M.math("MULTIPLY", pores, 0.4), M.math("MULTIPLY", wr, 0.6))
    h = M.math("ADD", h, M.math("MULTIPLY", vein, 0.6))
    return M.out(col, rough, M.bump(h, 0.35, 0.004), **{"Subsurface Weight": 0.12, "Subsurface Scale": 0.03,
                                                       "Coat Weight": ink, "Coat Roughness": 0.08})


def cloth(name, base=(0.016, 0.014, 0.017)):
    """old black wool: a fine weave, faded where it rubs, silk dust settled on top, ink soaked in patches"""
    M = _M(name)
    weave = M.noise(240, 3, 0.6)                                    # felted wool: fine and even every way
    mott = M.noise(4, 5, 0.6)
    col = M.mix(M.ramp(mott, 0, 1, 0.35, 0.7), base, (0.035, 0.03, 0.033))
    col = M.mix(M.math("MULTIPLY", M.edges(0.55, 0.65), 0.5), col, (0.06, 0.055, 0.058))   # worn, greyed
    dust = M.math("MULTIPLY", M.up(), M.ramp(M.noise(9, 4), 0, 1, 0.58, 0.72))
    col = M.mix(M.math("MULTIPLY", dust, 0.25), col, (0.16, 0.15, 0.13))
    col = M.mix(M.ramp(M.cavity(0.06), 0.8, 0, 0.3, 1), col, (0.004, 0.004, 0.005))
    inkp = M.ramp(M.noise(3.2, 6, 0.7), 0, 1, 0.62, 0.66)
    col = M.mix(inkp, col, (0.002, 0.002, 0.004))
    h = M.math("ADD", M.math("MULTIPLY", weave, 0.5), M.math("MULTIPLY", M.noise(30, 6), 0.5))
    return M.out(col, M.ramp(inkp, 0.92, 0.25), M.bump(h, 0.5, 0.0015),
                 **{"Sheen Weight": 0.15, "Sheen Roughness": 0.35, "Sheen Tint": (0.3, 0.3, 0.32)})


def iron(name, base=(0.09, 0.09, 0.1)):
    """black iron: rust bleeding out of the crevices and pits, the edges rubbed back to bright metal"""
    M = _M(name)
    cav = M.cavity(0.03)
    rustn = M.noise(6, 6, 0.65)
    rust = M.ramp(M.math("ADD", M.ramp(cav, 1, 0, 0.3, 1), M.math("SUBTRACT", rustn, 0.35)), 0, 1, 0.35, 0.6)
    rc = M.mix(M.noise(18, 4), (0.16, 0.06, 0.025), (0.28, 0.12, 0.04))
    col = M.mix(rust, base, rc)
    edge = M.edges(0.5, 0.53)
    col = M.mix(edge, col, (0.42, 0.42, 0.44))
    metal = M.ramp(rust, 1.0, 0.0)
    pit = M.n("ShaderNodeTexVoronoi", Scale=90)
    M.l(M.co, pit.inputs["Vector"])
    h = M.math("ADD", M.math("MULTIPLY", pit.outputs["Distance"], 0.4), M.math("MULTIPLY", rustn, 0.4))
    return M.out(col, M.ramp(rust, 0.38, 0.85), M.bump(h, 0.4, 0.002), Metallic=metal)


def leather(name, base=(0.05, 0.018, 0.013)):
    """an old binding: oxblood leather crazed with cracks, scuffed pale at the edges, grime in the creases"""
    M = _M(name)
    cr = M.n("ShaderNodeTexVoronoi", _feature="DISTANCE_TO_EDGE", Scale=38)
    M.l(M.co, cr.inputs["Vector"])
    crack = M.ramp(cr.outputs["Distance"], 1.0, 0.0, 0.0, 0.025)
    col = M.mix(M.ramp(M.noise(5, 5), 0, 1, 0.35, 0.7), base, (0.028, 0.012, 0.01))
    col = M.mix(M.math("MULTIPLY", crack, 0.9), col, (0.006, 0.004, 0.004))
    col = M.mix(M.edges(0.5, 0.55), col, (0.15, 0.08, 0.05))
    col = M.mix(M.ramp(M.cavity(0.04), 0.8, 0, 0.3, 1), col, (0.004, 0.003, 0.003))
    h = M.math("SUBTRACT", M.noise(60, 5), M.math("MULTIPLY", crack, 0.6))
    return M.out(col, M.ramp(crack, 0.42, 0.75), M.bump(h, 0.6, 0.002),
                 **{"Coat Weight": 0.25, "Coat Roughness": 0.35})


def silk(name, base=(0.4, 0.37, 0.3), translucent=0.25):
    """old silk wound tight: fibres streaked along the wrap, yellowed and greyed with age, filth soaked up from the
    floor, ink splashed on it; light comes through it a little"""
    M = _M(name)
    fv = M.n("ShaderNodeTexVoronoi", _feature="DISTANCE_TO_EDGE", Scale=55, Randomness=1.0)
    M.l(M.co, fv.inputs["Vector"])
    fib = M.math("ADD", M.ramp(fv.outputs["Distance"], 0.0, 1.0, 0.0, 0.06), M.math("MULTIPLY", M.noise(90, 5), 0.4))
    col = M.mix(M.ramp(M.noise(3, 5), 0, 1, 0.3, 0.7), base, (0.4, 0.36, 0.27))
    col = M.mix(M.ramp(fib, 0, 1, 0.45, 0.65), (0.2, 0.18, 0.14), col)               # fibres: dark between strands
    col = M.mix(M.math("MULTIPLY", M.ramp(fib, 0, 1, 0.6, 0.8), 0.6), col, (0.62, 0.6, 0.53))
    # filth wicked up from the floor
    sep = M.n("ShaderNodeSeparateXYZ")
    M.l(M.co, sep.inputs["Vector"])
    low = M.ramp(M.math("ADD", sep.outputs["Z"], M.math("MULTIPLY", M.noise(4, 4), 0.25)), 1, 0, 0.1, 0.9)
    col = M.mix(M.math("MULTIPLY", low, 0.85), col, (0.11, 0.09, 0.07))
    col = M.mix(M.ramp(M.cavity(0.05), 0.9, 0, 0.3, 1), col, (0.07, 0.06, 0.05))
    splash = M.ramp(M.noise(5.5, 6, 0.75), 0, 1, 0.68, 0.71)
    col = M.mix(splash, col, (0.004, 0.004, 0.006))
    h = M.math("ADD", fib, M.math("MULTIPLY", M.noise(20, 3), 0.3))
    return M.out(col, M.ramp(splash, 0.55, 0.15), M.bump(h, 0.45, 0.003),
                 **{"Sheen Weight": 0.3, "Sheen Roughness": 0.3, "Subsurface Weight": translucent,
                    "Subsurface Scale": 0.02})


def chitin(name, base=(0.012, 0.011, 0.012)):
    """spider armour: lacquer-black plates with a bruised-purple sheen at the edges, banded, scuffed, dusty on top"""
    M = _M(name)
    band = M.n("ShaderNodeTexVoronoi", Scale=9, Randomness=1.0)     # plates, not stripes
    M.l(M.co, band.inputs["Vector"])
    col = M.mix(M.ramp(band.outputs["Distance"], 0, 1, 0.3, 0.9), base, (0.022, 0.018, 0.024))
    col = M.mix(M.math("MULTIPLY", M.edges(0.56, 0.66), 0.3), col, (0.07, 0.055, 0.075))
    dust = M.math("MULTIPLY", M.up(), M.ramp(M.noise(12, 4), 0, 1, 0.5, 0.7))
    col = M.mix(M.math("MULTIPLY", dust, 0.25), col, (0.16, 0.15, 0.13))
    scr = M.noise(110, 3, 0.5)
    return M.out(col, M.ramp(dust, 0.22, 0.8), M.bump(M.math("ADD", scr, band.outputs["Distance"]), 0.25, 0.002),
                 **{"Coat Weight": M.ramp(dust, 0.9, 0.1), "Coat Roughness": 0.12})


def teeth(name):
    M = _M(name)
    col = M.mix(M.ramp(M.noise(30, 3), 0, 1, 0.3, 0.7), (0.3, 0.24, 0.13), (0.18, 0.12, 0.06))
    col = M.mix(M.ramp(M.cavity(0.01), 1, 0, 0.2, 1), col, (0.03, 0.015, 0.01))
    return M.out(col, 0.35, **{"Coat Weight": 0.3})


def glow_glass(name, color=(0.45, 0.72, 1.0), strength=2.0):
    """lens glass lit from behind: bright in the middle, falling off to the rim, a little grime"""
    M = _M(name)
    lw = M.n("ShaderNodeLayerWeight", Blend=0.3)
    core = M.ramp(lw.outputs["Facing"], 1.0, 0.15, 0.0, 0.8)
    em = M.mix(M.ramp(M.noise(40, 3), 0, 1, 0.3, 0.7), color, (color[0] * 0.6, color[1] * 0.7, color[2] * 0.8))
    M.l(em, M.b.inputs["Emission Color"])
    M.l(M.math("MULTIPLY", core, strength, clamp=False), M.b.inputs["Emission Strength"])
    return M.out(M.mix(core, (0.0, 0.0, 0.0), (0.02, 0.03, 0.04)), 0.08, **{"Coat Weight": 1.0})
