import bpy

ROOT_NAME = "BowlingPair01_ROOT"
STATIC = "BP01_STATIC"
CX = 0.95
LANE_W = 1.0668
DECK_Y0, DECK_Y1 = 17.90, 19.20
DECK_TOP = 0.0015
PIT_Y0, PIT_Y1 = 19.20, 20.10


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


def make_obj(name, verts, faces, mats, coll, slots=None):
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
    for m in mats:
        me.materials.append(m)
    if slots is not None:
        if len(slots) != len(me.polygons):
            raise ValueError("slot/polygon mismatch in %s" % name)
        for idx, s in enumerate(slots):
            me.polygons[idx].material_index = s
    ob = bpy.data.objects.new(name, me)
    ob.parent = bpy.data.objects[ROOT_NAME]
    coll.objects.link(ob)
    return ob


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


def box(name, x0, x1, y0, y1, z0, z1, mat, coll):
    verts = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
             (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
             (3, 7, 6, 2), (0, 4, 7, 3), (1, 2, 6, 5)]
    if signed_volume(verts, faces) <= 0.0:
        raise ValueError("inward normals on %s" % name)
    return make_obj(name, verts, faces, [mat], coll)


def prism_x(name, profile, x0, x1, mat, coll):
    n = len(profile)
    verts = [(x0, p[0], p[1]) for p in profile] + [(x1, p[0], p[1]) for p in profile]
    faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    for k in range(n):
        j = (k + 1) % n
        faces.append((k, j, n + j, n + k))
    if signed_volume(verts, faces) < 0.0:
        faces = [tuple(reversed(f)) for f in faces]
    if signed_volume(verts, faces) <= 0.0:
        raise ValueError("inward normals on %s" % name)
    return make_obj(name, verts, faces, [mat], coll)


def world_verts(ob):
    return [(ob.matrix_world @ v.co) for v in ob.data.vertices]


def poly_count(ob):
    return len(ob.data.polygons)


def world_bounds(ob):
    mw = ob.matrix_world
    xs, ys, zs = [], [], []
    for v in ob.data.vertices:
        w = mw @ v.co
        xs.append(w.x)
        ys.append(w.y)
        zs.append(w.z)
    return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))


def pit_profile():
    return [
        (PIT_Y0, -0.32),
        (PIT_Y1, -0.32),
        (PIT_Y1, -0.02),
        (PIT_Y1 - 0.06, -0.02),
        (PIT_Y1 - 0.06, -0.28),
        (PIT_Y0 + 0.06, -0.28),
        (PIT_Y0 + 0.06, -0.02),
        (PIT_Y0, -0.02),
    ]


def run():
    root = bpy.data.objects[ROOT_NAME]
    static = bpy.data.collections[STATIC]

    deck_mat = pbr_mat("MAT_LaneWood_B", (0.45, 0.30, 0.16), 0.38)
    seam_mat = pbr_mat("MAT_DeckSeam", (0.30, 0.20, 0.11), 0.45)
    pit_mat = pbr_mat("MAT_PitCatch", (0.07, 0.07, 0.08), 0.7)

    created = []
    decks = {}
    for side, cx in (("L", -CX), ("R", CX)):
        name = "PinDeck_%s" % side
        x0, x1 = cx - LANE_W / 2, cx + LANE_W / 2
        ob = box(name, x0, x1, DECK_Y0, DECK_Y1, -0.005, DECK_TOP, deck_mat, static)
        b = world_bounds(ob)
        if abs(b[5]) > 0.002 + 1e-9:
            raise ValueError("deck top out of tolerance: %s %s" % (name, b[5]))
        rack_x = [cx - 0.4572 - 0.0605, cx + 0.4572 + 0.0605]
        rack_y = [18.288 - 0.0605, 18.288 + 3 * 0.3048 * 0.8660254 + 0.0605]
        cover = (b[0] <= rack_x[0] + 0.002 and b[1] >= rack_x[1] - 0.002
                 and b[2] <= rack_y[0] + 0.002 and b[3] >= rack_y[1] - 0.002)
        if not cover:
            raise ValueError("deck does not cover rack footprint: %s" % name)
        decks[name] = {
            "bounds": [round(c, 4) for c in b],
            "top_z": round(b[5], 5),
            "rack_footprint_x": [round(c, 4) for c in rack_x],
            "rack_footprint_y": [round(c, 4) for c in rack_y],
            "coverage_margin_x": [round(rack_x[0] - b[0], 4), round(b[1] - rack_x[1], 4)],
            "coverage_margin_y": [round(rack_y[0] - b[2], 4), round(b[3] - rack_y[1], 4)],
            "polys": poly_count(ob),
        }
        created.append(name)
        seam = box("DeckSeam_%s" % side, x0, x1, DECK_Y0, DECK_Y0 + 0.03,
                   -0.004, DECK_TOP + 0.0005, seam_mat, static)
        created.append(seam.name)

    pit = prism_x("Pit_Catch", pit_profile(), -1.7044, 1.7044, pit_mat, static)
    created.append(pit.name)
    pb = world_bounds(pit)
    if not abs(pb[2] - 19.20) <= 0.01:
        raise ValueError("pit min y out of range: %s" % pb[2])
    if pb[3] < 19.799999:
        raise ValueError("pit does not extend 0.60m back: %s" % pb[3])
    if pb[5] >= 0.0:
        raise ValueError("pit top not recessed: %s" % pb[5])
    coords = world_verts(pit)
    interior = [w.z for w in coords if 19.26 <= w.y <= 20.04]

    report = {
        "stage": "02",
        "revision": "rev5-decks-pit",
        "created": created,
        "decks": decks,
        "pit": {
            "bounds": [round(c, 4) for c in pb],
            "depth_min_z": round(pb[4], 4),
            "top_z": round(pb[5], 4),
            "interior_min_z": round(min(interior), 4),
            "interior_verts": len(interior),
            "polys": poly_count(pit),
        },
        "deck_material": deck_mat.name,
        "pit_material": pit_mat.name,
        "root_children": len(root.children),
    }
    return report


if __name__ == '__blender_author__':
    report = run()
