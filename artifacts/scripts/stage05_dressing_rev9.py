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


def union_boxes(name, boxes, mat, coll):
    verts = []
    faces = []
    for (x0, x1, y0, y1, z0, z1) in boxes:
        base = len(verts)
        verts.extend([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                      (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)])
        faces.extend([(base + 0, base + 3, base + 2, base + 1), (base + 4, base + 5, base + 6, base + 7),
                      (base + 0, base + 1, base + 5, base + 4), (base + 3, base + 7, base + 6, base + 2),
                      (base + 0, base + 4, base + 7, base + 3), (base + 1, base + 2, base + 6, base + 5)])
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate(verbose=False, clean_customdata=True)
    me.update()
    if not all(p.area > 1e-9 for p in me.polygons):
        raise ValueError("degenerate face in %s" % name)
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    ob.parent = bpy.data.objects[ROOT_NAME]
    coll.objects.link(ob)
    return ob


def world_bounds(ob):
    mw = ob.matrix_world
    xs, ys, zs = [], [], []
    for v in ob.data.vertices:
        w = mw @ v.co
        xs.append(w.x)
        ys.append(w.y)
        zs.append(w.z)
    return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))


def bench(name, cx, mat, coll):
    boxes = [
        (cx - 0.50, cx + 0.50, -6.20, -4.90, 0.24, 0.46),
        (cx - 0.50, cx + 0.50, -6.20, -6.05, 0.46, 0.95),
        (cx - 0.44, cx - 0.30, -6.10, -5.96, 0.0, 0.24),
        (cx + 0.30, cx + 0.44, -6.10, -5.96, 0.0, 0.24),
        (cx - 0.44, cx - 0.30, -5.14, -5.00, 0.0, 0.24),
        (cx + 0.30, cx + 0.44, -5.14, -5.00, 0.0, 0.24),
    ]
    return union_boxes(name, boxes, mat, coll)


def run():
    root = bpy.data.objects[ROOT_NAME]
    static = bpy.data.collections[STATIC]

    floor_mat = pbr_mat("MAT_AlleyFloor", (0.20, 0.21, 0.24), 0.55)
    wall_mat = pbr_mat("MAT_WallPanel", (0.16, 0.17, 0.22), 0.6)
    seat_mat = pbr_mat("MAT_SeatCushion", (0.34, 0.10, 0.12), 0.55)
    stripe_mat = pbr_mat("MAT_StripGlow", (0.75, 0.25, 0.06), 0.35)
    light_mat = pbr_mat("MAT_LightBar", (0.90, 0.90, 0.86), 0.25)

    created = {}
    floor = box("AlleyFloor", -2.20, 2.20, -7.00, 21.00, -0.12, -0.004, floor_mat, static)
    created[floor.name] = world_bounds(floor)
    if created[floor.name][5] > 0.000001:
        raise ValueError("floor top above z0")
    if created[floor.name][2] > -5.15 or created[floor.name][3] < 20.0:
        raise ValueError("floor span insufficient")

    wall = box("MaskingWall", -2.20, 2.20, 20.30, 20.55, 1.00, 3.20, wall_mat, static)
    created[wall.name] = world_bounds(wall)
    pin_top = 0.381
    if created[wall.name][4] - pin_top < 0.60 - 1e-6:
        raise ValueError("masking clearance too small: %s" % created[wall.name][4])

    benches = []
    for side, cx in (("L", -1.10), ("R", 1.10)):
        benches.append(bench("Bench_%s" % side, cx, seat_mat, static))
    for b in benches:
        created[b.name] = world_bounds(b)
        if created[b.name][3] >= -4.572:
            raise ValueError("bench intrudes on approach: %s %s" % (b.name, created[b.name]))

    deco = []
    deco.append(box("Stripe_Upper", -2.20, 2.20, 20.26, 20.30, 2.30, 2.45, stripe_mat, static))
    deco.append(box("Stripe_Lower", -2.20, 2.20, 20.26, 20.30, 1.12, 1.27, stripe_mat, static))
    deco.append(box("LightBar_L", -1.55, -1.40, -2.00, 4.00, 3.30, 3.42, light_mat, static))
    deco.append(box("LightBar_R", 1.40, 1.55, -2.00, 4.00, 3.30, 3.42, light_mat, static))
    for d in deco:
        created[d.name] = world_bounds(d)

    report = {
        "stage": "05",
        "revision": "rev9-dressing-core",
        "floor_bounds": [round(c, 4) for c in created["AlleyFloor"]],
        "masking_wall_bounds": [round(c, 4) for c in created["MaskingWall"]],
        "masking_clearance_above_pin_tops": round(created["MaskingWall"][4] - pin_top, 4),
        "bench_names": sorted(b.name for b in benches),
        "bench_max_y": {b.name: round(created[b.name][3], 4) for b in benches},
        "decorations": sorted(d.name for d in deco),
        "materials": [floor_mat.name, wall_mat.name, seat_mat.name, stripe_mat.name, light_mat.name],
        "root_children": len(root.children),
    }
    return report


if __name__ == '__blender_author__':
    report = run()
