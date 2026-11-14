import bpy

ROOT_NAME = "BowlingPair01_ROOT"
PREFIX_MAP = (("Arrow_", "ArrowTri_"), ("FoulLine_", "Foul_"))


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
    renamed = []
    for ob in list(bpy.data.objects):
        if ob.type != 'MESH':
            continue
        old = ob.name
        new = None
        for src, dst in PREFIX_MAP:
            if old.startswith(src):
                new = dst + old[len(src):]
                break
        if new is None or new == old:
            continue
        if new in bpy.data.objects:
            raise ValueError("name conflict: %s" % new)
        me = ob.data
        ob.name = new
        if me is not None and me.name == old:
            me.name = new
        renamed.append({"old": old, "new": new})

    names = sorted(o.name for o in bpy.data.objects if o.type == 'MESH')
    counts = {}
    for prefix in ("ArrowTri_L", "ArrowTri_R", "Dot_L", "Dot_R", "Foul_L", "Foul_R"):
        counts[prefix] = sum(1 for n in names if n.startswith(prefix))

    markings = {}
    for n in names:
        if n.startswith(("ArrowTri_", "Dot_", "Foul_")):
            ob = bpy.data.objects[n]
            b = world_bounds(ob)
            markings[n] = {
                "x": [round(b[0], 4), round(b[1], 4)],
                "y_center": round((b[2] + b[3]) / 2.0, 4),
                "z": [round(b[4], 5), round(b[5], 5)],
                "z_within_0.002": abs(b[4]) <= 0.002001 and abs(b[5]) <= 0.002001,
                "slots": len(getattr(ob.data, "materials", []) or []),
            }

    foul_dims_y = {}
    for side in ("L", "R"):
        obj = bpy.data.objects.get("Foul_%s" % side)
        if obj is not None:
            b = world_bounds(obj)
            foul_dims_y[side] = round(b[3] - b[2], 5)

    report = {
        "stage": "01",
        "revision": "rev3-marking-contract-names",
        "renamed_count": len(renamed),
        "renamed": [r["new"] for r in renamed],
        "marking_counts": counts,
        "markings": markings,
        "foul_line_y_extent_m": foul_dims_y,
        "mesh_object_names": names,
        "root_children": len(bpy.data.objects[ROOT_NAME].children),
    }
    return report


if __name__ == '__blender_author__':
    report = run()
