import bpy

ROOT_NAME = "BowlingPair01_ROOT"
STATIC = "BP01_STATIC"

SEGMENTS = {
    "a": lambda s, W, H: (s, W - s, H - s, H),
    "b": lambda s, W, H: (W - s, W, H / 2 + s / 2, H - s),
    "c": lambda s, W, H: (W - s, W, s, H / 2 - s / 2),
    "d": lambda s, W, H: (s, W - s, 0.0, s),
    "e": lambda s, W, H: (0.0, s, s, H / 2 - s / 2),
    "f": lambda s, W, H: (0.0, s, H / 2 + s / 2, H - s),
    "g": lambda s, W, H: (s, W - s, H / 2 - s / 2, H / 2 + s / 2),
}
DIGITS = {"0": "abcdef", "1": "bc", "2": "abged"}


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


def box_only(name, verts, faces, mat, coll):
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


def box(name, x0, x1, y0, y1, z0, z1, mat, coll):
    verts = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
             (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
             (3, 7, 6, 2), (0, 4, 7, 3), (1, 2, 6, 5)]
    return box_only(name, verts, faces, mat, coll)


def union_boxes(name, boxes, mat, coll):
    verts = []
    faces = []
    for (x0, x1, y0, y1, z0, z1) in boxes:
        b = len(verts)
        verts.extend([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                      (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)])
        faces.extend([(b + 0, b + 3, b + 2, b + 1), (b + 4, b + 5, b + 6, b + 7),
                      (b + 0, b + 1, b + 5, b + 4), (b + 3, b + 7, b + 6, b + 2),
                      (b + 0, b + 4, b + 7, b + 3), (b + 1, b + 2, b + 6, b + 5)])
    return box_only(name, verts, faces, mat, coll)


def label(name, text, x_center, z_center, H, y_front, depth, mat, coll):
    s = 0.16 * H
    W = 0.55 * H
    pitch = W + 0.20 * H
    total = pitch * (len(text) - 1) + W
    x_start = x_center - total / 2.0
    boxes = []
    for idx, ch in enumerate(text):
        xl = x_start + idx * pitch
        z0 = z_center - H / 2.0
        for seg in DIGITS[ch]:
            u0, u1, v0, v1 = SEGMENTS[seg](s, W, H)
            boxes.append((xl + u0, xl + u1, y_front - depth, y_front - 0.001,
                          z0 + v0, z0 + v1))
    return union_boxes(name, boxes, mat, coll)


def score_grid(name, x0, x1, z0, z1, y_front, rows, cols, mat, coll):
    t = 0.012
    d = 0.006
    boxes = []
    for r in range(rows + 1):
        z = z0 + (z1 - z0) * r / rows
        boxes.append((x0, x1, y_front - d, y_front - 0.001, z - t / 2, z + t / 2))
    for c in range(cols + 1):
        x = x0 + (x1 - x0) * c / cols
        boxes.append((x - t / 2, x + t / 2, y_front - d, y_front - 0.001, z0, z1))
    return union_boxes(name, boxes, mat, coll)


def world_bounds(ob):
    mw = ob.matrix_world
    xs, ys, zs = [], [], []
    for v in ob.data.vertices:
        w = mw @ v.co
        xs.append(w.x)
        ys.append(w.y)
        zs.append(w.z)
    return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))


def run():
    root = bpy.data.objects[ROOT_NAME]
    static = bpy.data.collections[STATIC]

    screen_mat = pbr_mat("MAT_ScreenFace", (0.03, 0.04, 0.06), 0.25)
    grid_mat = pbr_mat("MAT_ScoreGrid", (0.65, 0.68, 0.72), 0.35)
    label_mat = pbr_mat("MAT_LabelCream", (0.92, 0.88, 0.70), 0.35)
    mount_mat = pbr_mat("MAT_MountMetal", (0.12, 0.12, 0.14), 0.45, 0.5)

    created = {}
    screens = []
    for side, cx, text in (("L", -0.95, "01"), ("R", 0.95, "02")):
        sc = box("Screen_%s" % side, cx - 0.50, cx + 0.50, 0.30, 0.52, 2.20, 2.95,
                 screen_mat, static)
        screens.append(sc)
        created[sc.name] = world_bounds(sc)
        mount = box("ScoreMount_%s" % side, cx - 0.08, cx + 0.08, 0.32, 0.50, 2.95, 3.42,
                    mount_mat, static)
        created[mount.name] = world_bounds(mount)
        grid = score_grid("ScoreGrid_%s" % side, cx - 0.44, cx + 0.44, 2.26, 2.50,
                          0.30, 3, 10, grid_mat, static)
        created[grid.name] = world_bounds(grid)
        dig = label("LaneDigits_%s" % side, text, cx, 2.70, 0.34, 0.30, 0.02,
                    label_mat, static)
        created[dig.name] = world_bounds(dig)

    if len(screens) != 2:
        raise ValueError("screen count must be 2")
    for sc in screens:
        b = created[sc.name]
        if b[4] < 2.20 - 1e-6:
            raise ValueError("screen bottom below 2.20: %s %s" % (sc.name, b))

    for side, cx, text in (("L", -0.95, "01"), ("R", 0.95, "02")):
        mask = label("MaskingDigits_%s" % side, text, cx, 1.72, 0.62, 20.30, 0.10,
                     label_mat, static)
        created[mask.name] = world_bounds(mask)

    report = {
        "stage": "05",
        "revision": "rev10-screens-labels",
        "screens": {s.name: [round(c, 4) for c in created[s.name]] for s in screens},
        "screen_bottom_z": {s.name: round(created[s.name][4], 4) for s in screens},
        "labels": {"LaneDigits_L": "01", "LaneDigits_R": "02",
                   "MaskingDigits_L": "01", "MaskingDigits_R": "02"},
        "label_bounds": {n: [round(c, 4) for c in created[n]]
                         for n in ("LaneDigits_L", "LaneDigits_R", "MaskingDigits_L",
                                   "MaskingDigits_R")},
        "grid_bounds": {n: [round(c, 4) for c in created[n]]
                        for n in ("ScoreGrid_L", "ScoreGrid_R")},
        "materials": [screen_mat.name, grid_mat.name, label_mat.name, mount_mat.name],
        "root_children": len(root.children),
    }
    return report


if __name__ == '__blender_author__':
    report = run()
