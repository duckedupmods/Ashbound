"""Epic Fight's own skeletons in Blender, for concepts that pose exactly as the game will.

Reads an armature (biped, spider, ...) and an animation straight out of the Epic Fight jar we run against (read
only, nothing of theirs is copied into the mod). Joint matrices are 4x4 row-major, local to the parent, in Blender's
frame (x right, y forward, z up); a joint's +y runs along its bone. A pose is the animation's local matrices at a
time, chained down the hierarchy; a mesh built round the bind pose is skinned onto it with weights per joint.
    import efrig; arm = efrig.Armature("biped"); pose = arm.pose("biped/combat/greatsword_auto1", 0.35)
    efrig.skin(obj, arm, pose, weights)  # or efrig.rigid(obj, arm, pose, "Hand_R")"""
import json, zipfile, glob, os
from mathutils import Matrix, Vector

JAR = (glob.glob(os.path.expanduser("~/.gradle/caches/modules-2/files-2.1/maven.modrinth/epic-fight/*/*/epic-fight-*.jar"))
       or [None])[0]
_zip = zipfile.ZipFile(JAR) if JAR else None


def _read(path):
    return json.loads(_zip.read("assets/epicfight/animmodels/" + path + ".json"))


def _mat(a):
    return Matrix([a[0:4], a[4:8], a[8:12], a[12:16]])


class Armature:
    def __init__(self, name):
        d = _read("entity/" + name)["armature"]
        self.joints = d["joints"]
        self.parent, self.local = {}, {}

        def walk(h, par):
            self.parent[h["name"]] = par
            self.local[h["name"]] = _mat(h["transform"])
            for c in h.get("children", []):
                walk(c, h["name"])
        for h in d["hierarchy"]:
            walk(h, None)
        self.bind = self.chain(self.local)
        self.children = {j: [c for c, p in self.parent.items() if p == j] for j in self.joints}

    def chain(self, local):
        out = {}

        def w(j):
            if j not in out:
                p = self.parent[j]
                out[j] = (w(p) if p else Matrix.Identity(4)) @ local[j]
            return out[j]
        for j in self.joints:
            w(j)
        return out

    def at(self, j):
        """where joint j stands in the bind pose"""
        return self.bind[j].to_translation()

    def pose(self, anim=None, t=0.0, over=None):
        """world matrices of every joint at time t of the animation (bind pose without one); over = {joint: extra
        local rotation Matrix} to bend a joint further by hand"""
        local = dict(self.local)
        coord = None
        if anim:
            for e in _read("animations/" + anim)["animation"]:
                if e["name"] == "Coord":
                    # a skill's root-motion joint: Root is local to it; keep its turn, drop the travel
                    coord = _mat(e["transform"][0]).to_3x3().to_4x4()
                    continue
                if e["name"] not in local:
                    continue
                ts, tr = e["time"], e["transform"]
                i = max([k for k, x in enumerate(ts) if x <= t] or [0])
                a = _mat(tr[i])
                if i + 1 < len(ts) and ts[i + 1] > ts[i] and t > ts[i]:
                    b = _mat(tr[i + 1])
                    f = (t - ts[i]) / (ts[i + 1] - ts[i])
                    la, ra, _ = a.decompose()
                    lb, rb, _ = b.decompose()
                    a = Matrix.Translation(la.lerp(lb, f)) @ ra.slerp(rb, f).to_matrix().to_4x4()
                local[e["name"]] = a
        if coord is not None:
            local["Root"] = coord @ local["Root"]
        for j, m in (over or {}).items():
            local[j] = local[j] @ m
        return self.chain(local)

    def segment(self, j):
        """the bone of joint j as (head, tail) in the bind pose: to its child, or a stub along its +y"""
        h = self.at(j)
        kids = [c for c in self.children[j] if (self.at(c) - h).length > 1e-3]
        if kids:
            return h, sum((self.at(c) for c in kids), Vector()) / len(kids)
        return h, h + self.bind[j].to_3x3() @ Vector((0, 0.15, 0))


def rigid(o, arm, pose, j):
    """a mesh built in the bind pose, carried by joint j"""
    o.data.transform(pose[j] @ arm.bind[j].inverted())


def auto_weights(verts, arm, joints, power=6.0, top=2, segs=None):
    """weights per vertex from its distance to each listed joint's bone, the nearest few blended (enough for
    elbows and knees to bend smoothly); returns [(joint, w), ...] per vertex"""
    segs = {j: (segs or {}).get(j) or arm.segment(j) for j in joints}
    out = []
    for v in verts:
        ds = []
        for j, (a, b) in segs.items():
            ab = b - a
            t = max(0.0, min(1.0, (v - a).dot(ab) / max(ab.length_squared, 1e-9)))
            ds.append((max((v - (a + ab * t)).length, 1e-4), j))
        ds.sort()
        ds = ds[:top]
        ws = [(j, d ** -power) for d, j in ds]
        s = sum(w for _, w in ws)
        out.append([(j, w / s) for j, w in ws])
    return out


def skin(o, arm, pose, weights):
    """linear blend skinning of mesh o (built in the bind pose) onto the pose"""
    sk = {j: pose[j] @ arm.bind[j].inverted() for j in arm.joints}
    for v, ws in zip(o.data.vertices, weights):
        p = Vector()
        for j, w in ws:
            p += (sk[j] @ v.co) * w
        v.co = p
    o.data.update()


if __name__ == "__main__":
    for n in ("biped", "spider"):
        a = Armature(n)
        for j in a.joints:
            h, t = a.segment(j)
            print(n, j, tuple(round(x, 3) for x in h), "->", tuple(round(x, 3) for x in t))


def skin_points(pts, arm, pose, weights):
    """points (a strand's) carried the same way as skin()"""
    sk = {j: pose[j] @ arm.bind[j].inverted() for j in arm.joints}
    return [sum(((sk[j] @ Vector(p)) * w for j, w in ws), Vector()) for p, ws in zip(pts, weights)]
