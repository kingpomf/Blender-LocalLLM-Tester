import bpy

ROOT_NAME = "BowlingPair01_ROOT"
COLL = "BP01_COLLISION"
CX = 0.95
LANE_W = 1.0668
GW = 0.22
GAP = 0.001
Z_LIP = 0.003
Z_TROUGH = -0.105
Z_BOTTOM = -0.118
Y0, Y1 = 0.0, 19.20


def pbr_mat(name, base, rough=0.5, metallic=0.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    assert nt is not None
    bsdf = nt.nodes.get("Principled BSDF")
    if bsdf is None:
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
        nt.links.new(bsdf.outputs[0], out.inputs[0])
    bsdf.inputs["Base Color"].default_value = (base[0], base[1], base[2], 1.0)  # type: ignore[attr-defined]
    bsdf.inputs["Roughness"].default_value = rough  # type: ignore[attr-defined]
    bsdf.inputs["Metallic"].default_value = metallic  # type: ignore[attr-defined]
    return mat


def edge_uses(me):
    loop_verts = [lp.vertex_index for lp in me.loops]
    uses = {}
    for p in me.polygons:
        s = p.loop_start
        t = p.loop_total
        for k in range(t):
            a = loop_verts[s + k]
            b = loop_verts[s + (k + 1) % t]
            key = (a, b) if a < b else (b, a)
            uses[key] = uses.get(key, 0) + 1
    return uses


def signed_volume(verts, faces):
    total = 0.0
    for f in faces:
        a = verts[f[0]]
        for i in range(1, len(f) - 1):
            b = verts[f[i]]
            c = verts[f[i + 1]]
            total += (a[0] * (b[1] * c[2] - b[2] * c[1])
                      - a[1] * (b[0] * c[2] - b[2] * c[0])
                      + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0
    return total


def make_proxy(name, verts, faces, mat, coll):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate(verbose=False, clean_customdata=True)
    me.update()
    if len(me.vertices) != len(verts) or len(me.polygons) != len(faces):
        raise ValueError("element loss in %s" % name)
    if not all(p.area > 1e-9 for p in me.polygons):
        raise ValueError("degenerate face in %s" % name)
    uses = edge_uses(me)
    bad = sum(1 for c in uses.values() if c != 2)
    if bad or sum(1 for e in me.edges if e.is_loose):
        raise ValueError("proxy non-manifold in %s: %d bad edge uses" % (name, bad))
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    ob.hide_render = True
    coll.objects.link(ob)
    return ob


def prism(name, profile, y0, y1, mat, coll):
    n = len(profile)
    verts = [(p[0], y0, p[1]) for p in profile] + [(p[0], y1, p[1]) for p in profile]
    faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    for k in range(n):
        j = (k + 1) % n
        faces.append((k, j, n + j, n + k))
    if signed_volume(verts, faces) < 0.0:
        faces = [tuple(reversed(f)) for f in faces]
    return make_proxy(name, verts, faces, mat, coll)


def box(name, x0, x1, y0, y1, z0, z1, mat, coll):
    verts = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
             (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
             (3, 7, 6, 2), (0, 4, 7, 3), (1, 2, 6, 5)]
    return make_proxy(name, verts, faces, mat, coll)


def tri_count_obj(ob):
    return sum(len(p.loop_indices) - 2 for p in ob.data.polygons)


def bounds(ob):
    xs = [v.co.x for v in ob.data.vertices]
    ys = [v.co.y for v in ob.data.vertices]
    zs = [v.co.z for v in ob.data.vertices]
    return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))


def visual_bounds(name):
    ob = bpy.data.objects[name]
    mw = ob.matrix_world
    xs, ys, zs = [], [], []
    for v in ob.data.vertices:
        w = mw @ v.co
        xs.append(w.x)
        ys.append(w.y)
        zs.append(w.z)
    return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))


def run():
    coll = bpy.data.collections[COLL]
    proxy_mat = pbr_mat("MAT_CollisionProxy", (0.30, 0.30, 0.32), 0.6)

    lane_min = {"L": -CX - LANE_W / 2, "R": CX - LANE_W / 2}
    lane_max = {"L": -CX + LANE_W / 2, "R": CX + LANE_W / 2}
    spans = {
        "Gutter_L_Outer": (lane_min["L"] - GAP - GW, lane_min["L"] - GAP),
        "Gutter_L_Inner": (lane_max["L"] + GAP, lane_max["L"] + GAP + GW),
        "Gutter_R_Inner": (lane_min["R"] - GAP - GW, lane_min["R"] - GAP),
        "Gutter_R_Outer": (lane_max["R"] + GAP, lane_max["R"] + GAP + GW),
    }

    created = {}
    compare = {}
    for gname, (xa, xb) in spans.items():
        mid = (xa + xb) / 2.0
        profile = [(xa, Z_BOTTOM), (xb, Z_BOTTOM), (xb, Z_LIP),
                   (mid, Z_TROUGH), (xa, Z_LIP)]
        ob = prism("COL_" + gname, profile, Y0, Y1, proxy_mat, coll)
        created[ob.name] = bounds(ob)
        vb = visual_bounds(gname)
        pb = created[ob.name]
        worst = max(abs(pb[i] - vb[i]) for i in range(6))
        compare[ob.name] = {"proxy": [round(c, 4) for c in pb],
                            "visual": [round(c, 4) for c in vb],
                            "max_delta": round(worst, 5)}
        if worst > 0.01:
            raise ValueError("proxy bounds mismatch: %s %s" % (ob.name, compare[ob.name]))

    for side in ("L", "R"):
        ob = box("COL_LaneBed_%s" % side, lane_min[side], lane_max[side], Y0, Y1,
                 -0.15, 0.0, proxy_mat, coll)
        created[ob.name] = bounds(ob)
        vb = visual_bounds("Lane_%s_Surface" % side)
        pb = created[ob.name]
        worst = max(abs(pb[i] - vb[i]) for i in range(6))
        compare[ob.name] = {"proxy": [round(c, 4) for c in pb],
                            "visual": [round(c, 4) for c in vb],
                            "max_delta": round(worst, 5)}
        if worst > 0.01:
            raise ValueError("lane bed mismatch: %s %s" % (ob.name, compare[ob.name]))

    total_tris = 0
    for ob in coll.objects:
        if not ob.name.startswith("COL_"):
            raise ValueError("collision collection object must start COL_: %s" % ob.name)
        if not ob.hide_render:
            raise ValueError("collision proxy not render-hidden: %s" % ob.name)
        total_tris += tri_count_obj(ob)

    report = {
        "stage": "06",
        "revision": "rev11-collision-proxies",
        "created": sorted(created),
        "proxy_vs_visual": compare,
        "collision_triangles": total_tris,
        "collision_object_count": len(coll.objects),
        "all_hidden_from_render": True,
        "parented_to_visual_root": [o.parent.name for o in coll.objects if o.parent],
    }
    return report


if __name__ == '__blender_author__':
    report = run()
