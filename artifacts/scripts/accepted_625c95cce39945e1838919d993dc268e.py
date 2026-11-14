import bpy
from math import pi, sin, cos
from mathutils import Vector

ROOT_NAME = "BowlingPair01_ROOT"
BALLS = "BP01_BALLS"
PROPS_CAMERA = "CAM_BowlingPair01_Props"

R = 0.108
NSEG = 48
NRING = 24
HOLE_R = 0.018
HOLE_DEPTH = 0.032
HOLE_PROTRUSION = 0.020
BALL_Y = -2.7
TRAY_TOP = 0.50
BALL_Z = TRAY_TOP + R
BALL_XS = (-0.23, 0.0, 0.23)
BALL_NAMES = ("Ball_01", "Ball_02", "Ball_03")

HOLE_DIRS = (
    Vector((0.0, -0.32, 0.94)),
    Vector((0.28, 0.19, 0.94)),
    Vector((-0.28, 0.19, 0.94)),
)


def pbr_mat(name, base, rough=0.12, metallic=0.0):
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


def sphere_mesh(name):
    verts = []
    faces = []
    index = {}
    for i in range(NRING + 1):
        phi = pi * i / NRING
        z = R * cos(phi)
        rr = R * sin(phi)
        if i == 0 or i == NRING:
            index[(i, 0)] = len(verts)
            verts.append((0.0, 0.0, z))
            continue
        for k in range(NSEG):
            theta = 2 * pi * k / NSEG
            index[(i, k)] = len(verts)
            verts.append((rr * cos(theta), rr * sin(theta), z))
    for i in range(NRING):
        for k in range(NSEG):
            k2 = (k + 1) % NSEG
            if i == 0:
                faces.append((index[(0, 0)], index[(1, k)], index[(1, k2)]))
            elif i == NRING - 1:
                faces.append((index[(NRING, 0)], index[(NRING - 1, k2)], index[(NRING - 1, k)]))
            else:
                faces.append((index[(i, k)], index[(i, k2)],
                              index[(i + 1, k2)], index[(i + 1, k)]))
    if signed_volume(verts, faces) < 0.0:
        faces = [tuple(reversed(f)) for f in faces]

    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate(verbose=False, clean_customdata=True)
    me.update()
    if len(me.vertices) != len(verts) or len(me.polygons) != len(faces):
        raise ValueError("sphere element loss in %s" % name)
    return me


def cylinder_mesh(name, radius, depth):
    half = depth / 2.0
    n = 24
    verts = [(0.0, 0.0, -half)]
    bottom_start = len(verts)
    for k in range(n):
        theta = 2 * pi * k / n
        verts.append((radius * cos(theta), radius * sin(theta), -half))
    top_center = len(verts)
    verts.append((0.0, 0.0, half))
    top_start = len(verts)
    for k in range(n):
        theta = 2 * pi * k / n
        verts.append((radius * cos(theta), radius * sin(theta), half))

    faces = []
    for k in range(n):
        k2 = (k + 1) % n
        faces.append((0, bottom_start + k, bottom_start + k2))
        faces.append((bottom_start + k, top_start + k, top_start + k2, bottom_start + k2))
        faces.append((top_center, top_start + k2, top_start + k))
    if signed_volume(verts, faces) < 0.0:
        faces = [tuple(reversed(f)) for f in faces]

    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate(verbose=False, clean_customdata=True)
    me.update()
    if len(me.vertices) != len(verts) or len(me.polygons) != len(faces):
        raise ValueError("cutter element loss in %s" % name)
    return me


def apply_boolean_diff(ball, cutter, mat, name):
    bpy.context.view_layer.update()
    mod = ball.modifiers.new(name, 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.solver = 'EXACT'
    mod.object = cutter

    depsgraph = bpy.context.evaluated_depsgraph_get()
    ball_eval = ball.evaluated_get(depsgraph)
    new_me = bpy.data.meshes.new_from_object(
        ball_eval,
        preserve_all_data_layers=True,
        depsgraph=depsgraph,
    )
    ball.modifiers.remove(mod)
    if len(new_me.polygons) == 0 or len(new_me.vertices) == 0:
        bpy.data.meshes.remove(new_me, do_unlink=True)
        raise ValueError("boolean produced empty mesh for %s" % ball.name)

    new_me.materials.clear()
    new_me.materials.append(mat)
    old_me = ball.data
    ball.data = new_me
    ball.data.validate(verbose=False, clean_customdata=True)
    ball.data.update()
    if old_me is not None and old_me.users == 0:
        bpy.data.meshes.remove(old_me, do_unlink=True)

    cutter_me = cutter.data
    bpy.data.objects.remove(cutter, do_unlink=True)
    if cutter_me is not None and cutter_me.users == 0:
        bpy.data.meshes.remove(cutter_me, do_unlink=True)


def make_cutter(direction, name, coll):
    length = HOLE_DEPTH + HOLE_PROTRUSION
    center = direction * (R + (HOLE_PROTRUSION - HOLE_DEPTH) / 2.0)
    euler = direction.to_track_quat('Z', 'Y').to_euler()
    me = cylinder_mesh(name, HOLE_R, length)
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    ob.location = (center.x, center.y, center.z)
    ob.rotation_euler = euler
    ob.scale = (1.0, 1.0, 1.0)
    return ob


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


def check_ball(ob):
    me = ob.data
    me.validate(verbose=False, clean_customdata=True)
    me.update()
    if not me.polygons:
        raise ValueError("no ball polygons in %s" % ob.name)
    bad_faces = [i for i, p in enumerate(me.polygons) if p.area <= 1e-10]
    if bad_faces:
        raise ValueError("degenerate ball face in %s: %s" % (ob.name, bad_faces[:5]))
    loose = sum(1 for e in me.edges if e.is_loose)
    uses = edge_uses(me)
    bad_edges = sum(1 for c in uses.values() if c != 2)
    if loose or bad_edges:
        raise ValueError("ball non-manifold in %s loose=%d bad=%d" % (ob.name, loose, bad_edges))
    radii = [v.co.length for v in me.vertices]
    max_r = max(radii)
    min_r = min(radii)
    if max_r < R - 0.001 or max_r > R + 0.001:
        raise ValueError("ball exterior radius changed in %s: %.6f" % (ob.name, max_r))
    depth = max_r - min_r
    if depth < 0.015:
        raise ValueError("ball hole depth too small in %s: %.6f" % (ob.name, depth))
    tri = 0
    for p in me.polygons:
        tri += len(p.loop_indices) - 2
    if tri > 8000:
        raise ValueError("ball triangle budget exceeded in %s: %d" % (ob.name, tri))
    xs = [v.co.x for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    zs = [v.co.z for v in me.vertices]
    center = [
        (min(xs) + max(xs)) / 2.0,
        (min(ys) + max(ys)) / 2.0,
        (min(zs) + max(zs)) / 2.0,
    ]
    pivot = (center[0] ** 2 + center[1] ** 2 + center[2] ** 2) ** 0.5
    if pivot > 0.001:
        raise ValueError("ball pivot error in %s: %.6f" % (ob.name, pivot))
    return {
        "name": ob.name,
        "diameter": round(2.0 * max_r, 5),
        "hole_depth": round(depth, 5),
        "triangles": tri,
        "vertices": len(me.vertices),
        "faces": len(me.polygons),
        "pivot_error": round(pivot, 6),
    }


def run():
    root = bpy.data.objects[ROOT_NAME]
    balls_coll = bpy.data.collections[BALLS]
    cam = bpy.data.objects[PROPS_CAMERA]

    for name in BALL_NAMES:
        ob = bpy.data.objects.get(name)
        if ob is not None:
            me = ob.data
            bpy.data.objects.remove(ob, do_unlink=True)
            if me is not None and me.users == 0:
                bpy.data.meshes.remove(me, do_unlink=True)

    specs = [
        ("Ball_01", "MAT_Ball_01_Azure", (0.045, 0.16, 0.55)),
        ("Ball_02", "MAT_Ball_02_Burgundy", (0.48, 0.045, 0.085)),
        ("Ball_03", "MAT_Ball_03_Teal", (0.03, 0.42, 0.38)),
    ]
    evidence = []

    for (name, matname, color) in specs:
        mat = pbr_mat(matname, color, 0.10, 0.0)
        me = sphere_mesh(name)
        me.materials.append(mat)
        ob = bpy.data.objects.new(name, me)
        balls_coll.objects.link(ob)

        for idx, raw_dir in enumerate(HOLE_DIRS):
            direction = raw_dir.normalized()
            cutter_name = "%s_hole_%02d" % (name, idx + 1)
            cutter = make_cutter(direction, cutter_name, balls_coll)
            apply_boolean_diff(ob, cutter, mat, cutter_name)
            bpy.context.view_layer.update()

        x = BALL_XS[len(evidence)]
        ob.parent = root
        ob.matrix_parent_inverse = root.matrix_world.inverted()
        ob.location = (x, BALL_Y, BALL_Z)
        ob.rotation_euler = (0.0, 0.0, 0.0)
        ob.scale = (1.0, 1.0, 1.0)
        grip = Vector((cam.location.x, cam.location.y, cam.location.z))
        grip = grip - Vector((ob.location.x, ob.location.y, ob.location.z))
        if grip.length < 1e-6:
            grip = Vector((0.0, 1.0, 0.7))
        ob.rotation_euler = grip.normalized().to_track_quat('Z', 'Y').to_euler()

        ev = check_ball(ob)
        ev["location"] = [round(v, 4) for v in ob.location]
        ev["rotation_euler"] = [round(v, 4) for v in ob.rotation_euler]
        evidence.append(ev)

    for a in BALL_XS:
        for b in BALL_XS:
            if a < b and abs(b - a) < 2 * R + 0.005:
                raise ValueError("insufficient ball separation: %.4f" % (abs(b - a)))

    return {
        "stage": "04",
        "revision": "rev13-ball-visible-holes",
        "balls": evidence,
        "camera_target_role": PROPS_CAMERA,
    }


if __name__ == '__blender_author__':
    report = run()
