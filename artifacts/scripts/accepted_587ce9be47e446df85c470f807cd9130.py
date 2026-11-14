import bpy

ROOT_NAME = "BowlingPair01_ROOT"
STATIC = "BP01_STATIC"
Y0, Y1 = 0.0, 19.20
CX = 0.95
LANE_W = 1.0668
GW = 0.22
GAP = 0.001
Z_LIP = 0.003
Z_TROUGH = -0.105
Z_BOTTOM = -0.118


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


def prism(name, profile, y0, y1, mat, coll):
    n = len(profile)
    verts = [(p[0], y0, p[1]) for p in profile] + [(p[0], y1, p[1]) for p in profile]
    faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    for k in range(n):
        j = (k + 1) % n
        faces.append((k, j, n + j, n + k))
    if signed_volume(verts, faces) < 0.0:
        faces = [tuple(reversed(f)) for f in faces]
    return make_obj(name, verts, faces, [mat], coll)


def box(name, x0, x1, y0, y1, z0, z1, mat, coll):
    verts = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
             (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
             (3, 7, 6, 2), (0, 4, 7, 3), (1, 2, 6, 5)]
    ob = make_obj(name, verts, faces, [mat], coll)
    if signed_volume(verts, faces) <= 0.0:
        raise ValueError("inward normals on %s" % name)
    return ob


def gutter_profile(xa, xb):
    inner = 0.018
    shoulder = 0.092
    return [
        (xa, Z_BOTTOM),
        (xb, Z_BOTTOM),
        (xb, Z_LIP),
        (xb - inner, Z_LIP),
        (xb - inner, -0.075),
        (xb - shoulder, Z_TROUGH),
        (xa + shoulder, Z_TROUGH),
        (xa + inner, -0.075),
        (xa + inner, Z_LIP),
        (xa, Z_LIP),
    ]


def world_bounds(ob):
    mw = ob.matrix_world
    xs, ys, zs = [], [], []
    for v in ob.data.vertices:
        w = mw @ v.co
        xs.append(w.x)
        ys.append(w.y)
        zs.append(w.z)
    return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))


def gutter_evidence(ob, lane_edge, lip_is_min):
    b = world_bounds(ob)
    mid = (b[0] + b[1]) / 2.0
    coords = [(ob.matrix_world @ v.co) for v in ob.data.vertices]
    central = [w.z for w in coords if abs(w.x - mid) < 0.02]
    lip = b[0] if lip_is_min else b[1]
    return {
        "bounds": [round(c, 4) for c in b],
        "width_x": round(b[1] - b[0], 4),
        "y_span": [round(b[2], 4), round(b[3], 4)],
        "trough_center_min_z": round(min(central), 4),
        "min_z": round(b[4], 4),
        "max_z": round(b[5], 4),
        "lane_edge": round(lane_edge, 4),
        "gutter_lip": round(lip, 4),
        "adjacency_gap": round(abs(lane_edge - lip), 4),
        "profile_verts": len(ob.data.vertices),
        "polys": len(ob.data.polygons),
    }


def run():
    root = bpy.data.objects[ROOT_NAME]
    static = bpy.data.collections[STATIC]

    gut_mat = pbr_mat("MAT_GutterMetal", (0.18, 0.19, 0.21), 0.45, 0.6)
    div_mat = pbr_mat("MAT_Divider", (0.13, 0.13, 0.15), 0.6)
    rail_mat = pbr_mat("MAT_Rail", (0.10, 0.10, 0.12), 0.5, 0.3)

    lane_min = {"L": -CX - LANE_W / 2, "R": CX - LANE_W / 2}
    lane_max = {"L": -CX + LANE_W / 2, "R": CX + LANE_W / 2}

    spans = {
        "Gutter_L_Outer": (lane_min["L"] - GAP - GW, lane_min["L"] - GAP,
                           lane_min["L"], False),
        "Gutter_L_Inner": (lane_max["L"] + GAP, lane_max["L"] + GAP + GW,
                           lane_max["L"], True),
        "Gutter_R_Inner": (lane_min["R"] - GAP - GW, lane_min["R"] - GAP,
                           lane_min["R"], False),
        "Gutter_R_Outer": (lane_max["R"] + GAP, lane_max["R"] + GAP + GW,
                           lane_max["R"], True),
    }
    evidence = {}
    created = []
    for name, (xa, xb, lane_edge, lip_is_min) in spans.items():
        ob = prism(name, gutter_profile(xa, xb), Y0, Y1, gut_mat, static)
        created.append(name)
        ev = gutter_evidence(ob, lane_edge, lip_is_min)
        if not (0.22 - 1e-6 <= ev["width_x"] <= 0.25 + 1e-6):
            raise ValueError("gutter width out of range: %s %s" % (name, ev["width_x"]))
        if not (0.0 <= ev["adjacency_gap"] <= 0.01 + 1e-6):
            raise ValueError("gutter adjacency out of range: %s %s" % (name, ev["adjacency_gap"]))
        if ev["max_z"] > 0.005 + 1e-6:
            raise ValueError("gutter lip too high: %s %s" % (name, ev["max_z"]))
        if not (-0.12 - 1e-6 <= ev["min_z"] <= -0.08 + 1e-6):
            raise ValueError("gutter depth out of range: %s %s" % (name, ev["min_z"]))
        if ev["trough_center_min_z"] > -0.08 + 1e-6:
            raise ValueError("gutter trough not deep at center: %s %s"
                             % (name, ev["trough_center_min_z"]))
        evidence[name] = ev

    div_a = spans["Gutter_L_Inner"][1]
    div_b = spans["Gutter_R_Inner"][0]
    divider = box("Divider_Cap", div_a, div_b, Y0, Y1, -0.12, -0.01, div_mat, static)
    created.append(divider.name)

    rails = []
    rails.append(box("Rail_L_Outer", spans["Gutter_L_Outer"][0] - 0.075,
                     spans["Gutter_L_Outer"][0], Y0, Y1, -0.15, 0.04, rail_mat, static))
    rails.append(box("Rail_R_Outer", spans["Gutter_R_Outer"][1],
                     spans["Gutter_R_Outer"][1] + 0.075, Y0, Y1, -0.15, 0.04, rail_mat, static))
    for r in rails:
        created.append(r.name)

    allx = []
    for n in list(spans) + ["Lane_L_Surface", "Lane_R_Surface"]:
        b = world_bounds(bpy.data.objects[n])
        allx.append(b[0])
        allx.append(b[1])

    report = {
        "stage": "02",
        "revision": "rev4b-gutters-divider-rails",
        "created": created,
        "gutters": evidence,
        "divider_bounds": [round(c, 4) for c in world_bounds(divider)],
        "rail_bounds": {r.name: [round(c, 4) for c in world_bounds(r)] for r in rails},
        "pair_envelope_x": [round(min(allx), 4), round(max(allx), 4)],
        "gutter_material": gut_mat.name,
        "root_children": len(root.children),
    }
    return report


if __name__ == '__blender_author__':
    report = run()
