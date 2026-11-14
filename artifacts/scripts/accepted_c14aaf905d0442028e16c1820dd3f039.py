import bpy

ROOT_NAME = "BowlingPair01_ROOT"
STATIC = "BP01_STATIC"


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


def make_obj(name, verts, faces, mat, coll):
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
        raise ValueError("non-manifold boundary in %s: %d bad edge uses" % (name, bad))
    if signed_volume(verts, faces) <= 0.0:
        raise ValueError("inward normals on %s" % name)
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    ob.parent = bpy.data.objects[ROOT_NAME]
    coll.objects.link(ob)
    return ob


def box(name, x0, x1, y0, y1, z0, z1, mat, coll):
    verts = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
             (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
             (3, 7, 6, 2), (0, 4, 7, 3), (1, 2, 6, 5)]
    return make_obj(name, verts, faces, mat, coll)


def world_bounds(ob):
    mw = ob.matrix_world
    xs, ys, zs = [], [], []
    for v in ob.data.vertices:
        w = mw @ v.co
        xs.append(w.x)
        ys.append(w.y)
        zs.append(w.z)
    return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))


TRAY_TOP = 0.50


def run():
    root = bpy.data.objects[ROOT_NAME]
    static = bpy.data.collections[STATIC]

    frame = pbr_mat("MAT_ReturnFrame", (0.11, 0.11, 0.13), 0.45, 0.5)
    tray = pbr_mat("MAT_ReturnTray", (0.16, 0.16, 0.19), 0.35, 0.4)
    hood = pbr_mat("MAT_HoodShell", (0.13, 0.14, 0.20), 0.40, 0.3)
    accent = pbr_mat("MAT_HoodAccent", (0.62, 0.30, 0.10), 0.35)

    parts = []
    parts.append(box("ReturnFrame_Post", -0.09, 0.09, -3.10, -2.30, 0.0, 0.42, frame, static))
    parts.append(box("ReturnRack_Tray", -0.34, 0.34, -3.30, -2.10, 0.42, TRAY_TOP, tray, static))
    parts.append(box("ReturnRack_Rail_L", -0.36, -0.34, -3.30, -2.10, 0.50, 0.56, tray, static))
    parts.append(box("ReturnRack_Rail_R", 0.34, 0.36, -3.30, -2.10, 0.50, 0.56, tray, static))
    parts.append(box("ReturnHood_Body", -0.36, 0.36, -4.28, -3.40, 0.0, 0.95, hood, static))
    parts.append(box("ReturnHood_LipLower", -0.26, 0.26, -3.50, -3.34, 0.40, 0.50, accent, static))
    parts.append(box("ReturnHood_LipUpper", -0.26, 0.26, -3.50, -3.34, 0.62, 0.72, accent, static))
    parts.append(box("ReturnHood_Cap", -0.36, 0.36, -4.28, -3.34, 0.95, 1.02, hood, static))

    bounds = {}
    for ob in parts:
        b = world_bounds(ob)
        if b[0] < -0.400001 or b[1] > 0.400001:
            raise ValueError("return part x out of footprint: %s %s" % (ob.name, b))
        if b[2] < -4.300001 or b[3] > -0.299999:
            raise ValueError("return part y out of footprint: %s %s" % (ob.name, b))
        bounds[ob.name] = [round(c, 4) for c in b]

    report = {
        "stage": "05",
        "revision": "rev7-return-rack",
        "created": sorted(b.name for b in parts),
        "return_bounds": bounds,
        "tray_top_z": TRAY_TOP,
        "opening_slot_z": [0.50, 0.62],
        "opening_facing": "+Y at y=-3.34",
        "materials": [frame.name, tray.name, hood.name, accent.name],
        "root_children": len(root.children),
    }
    return report


if __name__ == '__blender_author__':
    report = run()
