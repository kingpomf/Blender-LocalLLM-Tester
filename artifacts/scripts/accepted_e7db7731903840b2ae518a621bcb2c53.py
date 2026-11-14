import bpy
from math import cos, pi, sin

ROOT_NAME = "BowlingPair01_ROOT"
STATIC = "BP01_STATIC"
LANE_W = 1.0668
LANE_Y0, LANE_Y1 = 0.0, 19.20
APPR_Y0 = -4.572
CX = 0.95
TH = 0.15  # slab thickness below Z=0


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


def make_obj(name, verts, faces, mats, coll, slots=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate(verbose=False, clean_customdata=True)
    me.update()
    if len(me.vertices) != len(verts):
        raise ValueError("vertex loss in %s: %d/%d" % (name, len(me.vertices), len(verts)))
    if len(me.polygons) != len(faces):
        raise ValueError("face loss in %s: %d/%d" % (name, len(me.polygons), len(faces)))
    if not all(p.area > 1e-9 for p in me.polygons):
        raise ValueError("degenerate face in %s" % name)
    for m in mats:
        me.materials.append(m)
    if slots is not None:
        if len(slots) != len(me.polygons):
            raise ValueError(
                "slot/polygon mismatch in %s: %d slots vs %d polys"
                % (name, len(slots), len(me.polygons)))
        for idx, s in enumerate(slots):
            if not 0 <= s < len(me.materials):
                raise ValueError("bad slot %d for %s" % (s, name))
            me.polygons[idx].material_index = s
    ob = bpy.data.objects.new(name, me)
    ob.parent = bpy.data.objects[ROOT_NAME]
    coll.objects.link(ob)
    return ob


def slab(name, xb, yb, ztop, zbot, mats, board_slot_fn, coll):
    nv = len(xb) * len(yb)
    top = [(xb[i], yb[j], ztop) for j in range(len(yb)) for i in range(len(xb))]
    bot = [(xb[i], yb[j], zbot) for j in range(len(yb)) for i in range(len(xb))]
    verts = top + bot
    faces = []
    slots = []
    ny, nx = len(yb), len(xb)
    for j in range(ny - 1):
        for i in range(nx - 1):
            a = j * nx + i
            faces.append((a, a + 1, a + nx + 1, a + nx))
            slots.append(board_slot_fn(i))
            b = nv + j * nx + i
            faces.append((b + nx + 1, b + 1, b, b + nx))
            slots.append(board_slot_fn(i))
    for i in range(nx - 1):  # -Y side, row j == 0
        faces.append((i, nv + i, nv + i + 1, i + 1))
        slots.append(2)
    last = (ny - 1) * nx  # +Y side, row j == ny-1
    for i in range(nx - 1):
        faces.append((last + i, last + i + 1, nv + last + i + 1, nv + last + i))
        slots.append(2)
    for j in range(ny - 1):  # -X side
        a = j * nx
        faces.append((a, a + nx, nv + a + nx, nv + a))
        slots.append(2)
    for j in range(ny - 1):  # +X side
        a = j * nx + nx - 1
        faces.append((a + nx, a, nv + a, nv + a + nx))
        slots.append(2)
    return make_obj(name, verts, faces, mats, coll, slots)


def box(name, x0, x1, y0, y1, z0, z1, mat, coll):
    verts = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
             (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 4, 7, 3),
             (1, 2, 6, 5), (0, 1, 5, 4), (3, 7, 6, 2)]
    return make_obj(name, verts, faces, [mat], coll)


def tri_prism(name, pts, z0, z1, mat, coll):
    n = len(pts)
    verts = [(p[0], p[1], z0) for p in pts] + [(p[0], p[1], z1) for p in pts]
    faces = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
    for k in range(n):
        i, j = k, (k + 1) % n
        faces.append((i, j, j + n, i + n))
    return make_obj(name, verts, faces, [mat], coll)


def cyl(name, cx, cy, r, z0, z1, mat, coll, n=8):
    verts = []
    for k in range(n):
        a = 2 * pi * k / n
        verts.append((cx + r * cos(a), cy + r * sin(a), z0))
    for k in range(n):
        a = 2 * pi * k / n
        verts.append((cx + r * cos(a), cy + r * sin(a), z1))
    faces = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
    for k in range(n):
        i, j = k, (k + 1) % n
        faces.append((i, j, j + n, i + n))
    return make_obj(name, verts, faces, [mat], coll)


def bbox(ob):
    mw = ob.matrix_world
    xs, ys, zs = [], [], []
    for v in ob.data.vertices:
        w = mw @ v.co
        xs.append(w.x)
        ys.append(w.y)
        zs.append(w.z)
    return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))


def mesh_evidence(ob):
    me = ob.data
    used = sorted({p.material_index for p in me.polygons})
    return {
        "verts": len(me.vertices),
        "polys": len(me.polygons),
        "edges": len(me.edges),
        "slots": len(me.materials),
        "used_slots": used,
        "loose_edges": sum(1 for e in me.edges if e.is_loose),
        "nonmanifold_verts": sum(1 for v in me.vertices if not v.is_manifold),
        "min_face_area": round(min(p.area for p in me.polygons), 8),
        "min_normal_len": round(min(p.normal.length for p in me.polygons), 8),
    }


def run():
    scene = bpy.context.scene
    root = bpy.data.objects[ROOT_NAME]
    static = bpy.data.collections[STATIC]

    wood_a = pbr_mat("MAT_LaneWood_A", (0.52, 0.36, 0.20), 0.35)
    wood_b = pbr_mat("MAT_LaneWood_B", (0.45, 0.30, 0.16), 0.38)
    edge = pbr_mat("MAT_LaneEdge", (0.20, 0.14, 0.09), 0.5)
    appr = pbr_mat("MAT_Approach", (0.23, 0.24, 0.28), 0.6)
    foul = pbr_mat("MAT_FoulLine", (0.05, 0.05, 0.06), 0.6)
    mark = pbr_mat("MAT_Marking", (0.80, 0.55, 0.20), 0.45)

    yb = [LANE_Y0 + (LANE_Y1 - LANE_Y0) * j / 6 for j in range(7)]
    names = []
    evidence = {}
    for side, cx in (("L", -CX), ("R", CX)):
        xb = [cx - LANE_W / 2 + LANE_W * i / 12 for i in range(13)]
        nm = slab("Lane_%s_Surface" % side, xb, yb, 0.0, -TH,
                  [wood_a, wood_b, edge], lambda i: i % 2, static)
        names.append(nm.name)
        evidence[nm.name] = mesh_evidence(nm)
        nm = box("Approach_%s" % side, cx - LANE_W / 2, cx + LANE_W / 2,
                 APPR_Y0, 0.0, -TH, 0.0, appr, static)
        names.append(nm.name)
        evidence[nm.name] = mesh_evidence(nm)
        nm = box("FoulLine_%s" % side, cx - LANE_W / 2, cx + LANE_W / 2,
                 -0.02, 0.02, -0.001, 0.0015, foul, static)
        names.append(nm.name)
        offs = [-0.414, -0.276, -0.138, 0.0, 0.138, 0.276, 0.414]
        for k, dx in enumerate(offs):
            y0 = 4.52 if dx == 0.0 else 4.47
            pts = [(cx + dx - 0.02, y0), (cx + dx + 0.02, y0), (cx + dx, y0 + 0.09)]
            nm = tri_prism("Arrow_%s_%02d" % (side, k + 1), pts,
                           -0.001, 0.0015, mark, static)
            names.append(nm.name)
        offs_d = [-0.45, -0.30, -0.15, 0.0, 0.15, 0.30, 0.45]
        for k, dx in enumerate(offs_d):
            nm = cyl("Dot_%s_%02d" % (side, k + 1), cx + dx, -1.0, 0.02,
                     -0.001, 0.0015, mark, static)
            names.append(nm.name)

    report = {
        "stage": "01",
        "revision": "rev2-boundary-index-fix",
        "created": names,
        "lane_bounds": {n: [round(c, 4) for c in bbox(bpy.data.objects[n])]
                        for n in ("Lane_L_Surface", "Lane_R_Surface",
                                  "Approach_L", "Approach_R")},
        "mesh_evidence": evidence,
        "marking_counts": {
            "foul_lines": sum(1 for n in names if n.startswith("FoulLine_")),
            "arrows": sum(1 for n in names if n.startswith("Arrow_")),
            "dots": sum(1 for n in names if n.startswith("Dot_")),
        },
        "root_children": len(root.children),
    }
    return report


if __name__ == '__blender_author__':
    report = run()
