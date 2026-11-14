import bpy
from math import acos, cos, pi, sin
from mathutils import Vector

ROOT_NAME = "BowlingPair01_ROOT"
BALLS = "BP01_BALLS"
PROPS_CAMERA = "CAM_BowlingPair01_Props"

R = 0.108
NSEG = 64
NRING = 24
RECESS_DEPTH = 0.032
SHOULDER_DEPTH = 0.012
RECESS_ANG = 16.0 * pi / 180.0
SHOULDER_ANG = 21.0 * pi / 180.0
BALL_Y = -2.7
TRAY_TOP = 0.50
BALL_Z = TRAY_TOP + R
BALL_XS = (-0.23, 0.0, 0.23)
BALL_NAMES = ("Ball_01", "Ball_02", "Ball_03")

HOLE_DIRS = (
    Vector((0.0, -0.32, 0.94)).normalized(),
    Vector((0.28, 0.19, 0.94)).normalized(),
    Vector((-0.28, 0.19, 0.94)).normalized(),
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


def angle_to(dir_vec):
    nearest = pi
    for hd in HOLE_DIRS:
        dot = dir_vec.dot(hd)
        dot = max(-1.0, min(1.0, dot))
        nearest = min(nearest, acos(dot))
    return nearest


def ball_mesh(mat):
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
            dir_vec = Vector((sin(phi) * cos(theta), sin(phi) * sin(theta), cos(phi)))
            radius = R
            d = angle_to(dir_vec)
            if d <= RECESS_ANG:
                radius = R - RECESS_DEPTH
            elif d <= SHOULDER_ANG:
                radius = R - SHOULDER_DEPTH
            index[(i, k)] = len(verts)
            verts.append((dir_vec.x * radius, dir_vec.y * radius, dir_vec.z * radius))
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

    me = bpy.data.meshes.new(mat.name)
    me.from_pydata(verts, [], faces)
    me.validate(verbose=False, clean_customdata=True)
    me.update()
    if len(me.vertices) != len(verts) or len(me.polygons) != len(faces):
        raise ValueError("ball element loss in %s" % mat.name)
    if not all(p.area > 1e-9 for p in me.polygons):
        raise ValueError("degenerate ball face in %s" % mat.name)
    uses = edge_uses(me)
    bad = sum(1 for c in uses.values() if c != 2)
    if bad or sum(1 for e in me.edges if e.is_loose):
        raise ValueError("ball non-manifold in %s: %d bad edge uses" % (mat.name, bad))
    if signed_volume(verts, faces) <= 0.0:
        raise ValueError("inward normals on ball %s" % mat.name)
    me.materials.append(mat)
    return me


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
    local = [v.co for v in me.vertices]
    radii = [(vec.x ** 2 + vec.y ** 2 + vec.z ** 2) ** 0.5 for vec in local]
    max_r = max(radii)
    min_r = min(radii)
    recessed = {i for i, r in enumerate(radii) if r <= max_r - 0.015}
    loop_verts = [lp.vertex_index for lp in me.loops]
    graph = {i: set() for i in recessed}
    for p in me.polygons:
        vs = [loop_verts[li] for li in range(p.loop_start, p.loop_start + p.loop_total)]
        for a, b in zip(vs, vs[1:] + vs[:1]):
            if a in graph and b in graph:
                graph[a].add(b)
                graph[b].add(a)
    remaining = set(recessed)
    sizes = []
    while remaining:
        stack = [remaining.pop()]
        group = []
        while stack:
            i = stack.pop()
            group.append(i)
            for j in graph[i] & remaining:
                remaining.discard(j)
                stack.append(j)
        sizes.append(len(group))
    deep_regions = sum(1 for s in sizes if s >= 3)
    if deep_regions != 3:
        raise ValueError("expected three ball recess regions in %s, got %d" % (ob.name, deep_regions))
    bad_faces = [i for i, p in enumerate(me.polygons) if p.area <= 1e-9]
    if bad_faces:
        raise ValueError("degenerate ball face in %s: %s" % (ob.name, bad_faces[:5]))
    loose = sum(1 for e in me.edges if e.is_loose)
    uses = edge_uses(me)
    bad_edges = sum(1 for c in uses.values() if c != 2)
    if loose or bad_edges:
        raise ValueError("ball non-manifold in %s loose=%d bad=%d" % (ob.name, loose, bad_edges))
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
    xs = [vec.x for vec in local]
    ys = [vec.y for vec in local]
    zs = [vec.z for vec in local]
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
        "deep_regions": deep_regions,
        "region_sizes": sorted(sizes),
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

    for idx, (name, matname, color) in enumerate(specs):
        mat = pbr_mat(matname, color, 0.10, 0.0)
        me = ball_mesh(mat)
        ob = bpy.data.objects.new(name, me)
        balls_coll.objects.link(ob)
        ob.parent = root
        ob.matrix_parent_inverse = root.matrix_world.inverted()
        ob.location = (BALL_XS[idx], BALL_Y, BALL_Z)
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
        "revision": "rev13b-ball-visible-holes",
        "balls": evidence,
        "camera_target_role": PROPS_CAMERA,
    }


if __name__ == '__blender_author__':
    report = run()
