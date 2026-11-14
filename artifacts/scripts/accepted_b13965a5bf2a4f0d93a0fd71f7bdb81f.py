import bpy
from math import acos, cos, pi, sin
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT_NAME = "BowlingPair01_ROOT"
BALLS = "BP01_BALLS"
R = 0.108
NSEG = 48
NRING = 20
RECESS_DEPTH = 0.025
SHOULDER_DEPTH = 0.007
HOLE_I = 8
HOLE_KS = (7, 12, 17)
RECESS_ANG = 10.5
SHOULDER_ANG = 14.5
TRAY_TOP = 0.50
BALL_Y = -2.7
BALL_XS = (-0.23, 0.0, 0.23)


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


def ang_dist(phi_a, th_a, phi_b, th_b):
    xa = sin(phi_a) * cos(th_a)
    ya = sin(phi_a) * sin(th_a)
    za = cos(phi_a)
    xb = sin(phi_b) * cos(th_b)
    yb = sin(phi_b) * sin(th_b)
    zb = cos(phi_b)
    d = max(-1.0, min(1.0, xa * xb + ya * yb + za * zb))
    return acos(d)


def ball_mesh(mat):
    n, nr = NSEG, NRING
    verts = []
    index = {}
    for i in range(nr + 1):
        phi = pi * i / nr
        for k in range(n):
            if i == 0 or i == nr:
                if k == 0:
                    index[(i, k)] = len(verts)
                    verts.append((0.0, 0.0, R * cos(phi)))
                continue
            theta = 2 * pi * k / n
            radius = R
            for hk in HOLE_KS:
                d = ang_dist(phi, theta, pi * HOLE_I / nr, 2 * pi * hk / n)
                if d <= pi * RECESS_ANG / 180.0:
                    radius = R - RECESS_DEPTH
                elif d <= pi * SHOULDER_ANG / 180.0:
                    radius = min(radius, R - SHOULDER_DEPTH)
            index[(i, k)] = len(verts)
            verts.append((radius * sin(phi) * cos(theta),
                          radius * sin(phi) * sin(theta),
                          radius * cos(phi)))
    faces = []
    for i in range(nr):
        for k in range(n):
            k2 = (k + 1) % n
            if i == 0:
                faces.append((index[(0, 0)], index[(1, k)], index[(1, k2)]))
            elif i == nr - 1:
                faces.append((index[(nr, 0)], index[(nr - 1, k2)], index[(nr - 1, k)]))
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
    if signed_volume(verts, [tuple(f) for f in faces]) <= 0.0:
        raise ValueError("inward normals on ball %s" % mat.name)
    me.materials.append(mat)
    return me


def ball_evidence(ob):
    me = ob.data
    local = [v.co for v in me.vertices]
    radii = [(c.x ** 2 + c.y ** 2 + c.z ** 2) ** 0.5 for c in local]
    radius = max(radii)
    recessed = {i for i, r in enumerate(radii) if r <= radius - 0.015}
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
    xs = [c.x for c in local]
    ys = [c.y for c in local]
    zs = [c.z for c in local]
    center = [(min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (min(zs) + max(zs)) / 2]
    tris = 0
    for p in me.polygons:
        tris += len(p.loop_indices) - 2
    return {
        "radius": round(radius, 5),
        "diameter": round(2 * radius, 5),
        "min_radius": round(min(radii), 5),
        "hole_depth": round(radius - min(radii), 5),
        "recessed_verts": len(recessed),
        "deep_regions": sum(1 for s in sizes if s >= 3),
        "region_sizes": sorted(sizes),
        "pivot_error": round((center[0] ** 2 + center[1] ** 2 + center[2] ** 2) ** 0.5, 6),
        "triangles": tris,
    }


def world_polygon_lists(names):
    polys = []
    for n in names:
        ob = bpy.data.objects[n]
        mw = ob.matrix_world
        loop_verts = [lp.vertex_index for lp in ob.data.loops]
        for p in ob.data.polygons:
            vs = [loop_verts[li] for li in range(p.loop_start, p.loop_start + p.loop_total)]
            if len(vs) >= 3:
                polys.append([(mw @ ob.data.vertices[vs[0]].co),
                              (mw @ ob.data.vertices[vs[1]].co),
                              (mw @ ob.data.vertices[vs[2]].co)])
                for a in range(3, len(vs)):
                    polys.append([(mw @ ob.data.vertices[vs[0]].co),
                                  (mw @ ob.data.vertices[vs[a - 1]].co),
                                  (mw @ ob.data.vertices[vs[a]].co)])
    return polys


def run():
    root = bpy.data.objects[ROOT_NAME]
    balls_coll = bpy.data.collections[BALLS]

    specs = [
        ("Ball_01", "MAT_Ball_01_Azure", (0.045, 0.16, 0.55)),
        ("Ball_02", "MAT_Ball_02_Burgundy", (0.48, 0.045, 0.085)),
        ("Ball_03", "MAT_Ball_03_Teal", (0.03, 0.42, 0.38)),
    ]
    created = []
    evidence = {}
    centers = []
    for (name, matname, color) in specs:
        mat = pbr_mat(matname, color, 0.13, 0.0)
        me = ball_mesh(mat)
        x = BALL_XS[len(created)]
        ob = bpy.data.objects.new(name, me)
        ob.parent = root
        ob.location = (x, BALL_Y, TRAY_TOP + 0.108)
        ob.rotation_euler = (0.0, 0.0, 0.0)
        ob.scale = (1.0, 1.0, 1.0)
        balls_coll.objects.link(ob)
        created.append(name)
        centers.append((x, BALL_Y, TRAY_TOP + 0.108))
        ev = ball_evidence(ob)
        if abs(ev["diameter"] - 0.216) > 0.003:
            raise ValueError("ball diameter: %s %s" % (name, ev["diameter"]))
        if ev["pivot_error"] > 0.001:
            raise ValueError("ball pivot error: %s %s" % (name, ev["pivot_error"]))
        if ev["triangles"] > 8000:
            raise ValueError("ball triangle budget: %s %s" % (name, ev["triangles"]))
        if ev["deep_regions"] != 3:
            raise ValueError("ball recess regions: %s %s" % (name, ev["region_sizes"]))
        if ev["hole_depth"] < 0.015:
            raise ValueError("ball hole depth: %s %s" % (name, ev["hole_depth"]))
        evidence[name] = ev

    rack_names = [o.name for o in bpy.data.objects
                  if o.type == 'MESH' and o.name.startswith(('Hood', 'ReturnRack', 'ReturnFrame'))]
    bvhs = {}
    for rn in rack_names:
        polys = world_polygon_lists([rn])
        verts = []
        for tri in polys:
            verts.extend(tri)
        tris = [[b, b + 1, b + 2] for b in range(0, len(verts), 3)]
        bvhs[rn] = BVHTree.FromPolygons(verts, tris)
    contacts = {}
    for name, c in zip(created, centers):
        best = None
        for rn, tree in bvhs.items():
            hit = tree.find_nearest(Vector(c), 2.0)
            if hit and hit[3] is not None:
                if best is None or hit[3] < best[1]:
                    best = (rn, hit[3])
        contacts[name] = {"nearest_rack": best[0] if best else None,
                          "distance": round(best[1], 5) if best else None,
                          "ball_radius": 0.108,
                          "contact_error": round(abs(best[1] - 0.108), 5) if best else None}
        if best is None or abs(best[1] - 0.108) > 0.005001:
            raise ValueError("ball rack contact: %s %s" % (name, contacts[name]))

    gaps = {}
    for i in range(len(centers)):
        for j in range(i + 1, len(centers)):
            d = ((centers[i][0] - centers[j][0]) ** 2 + (centers[i][1] - centers[j][1]) ** 2
                 + (centers[i][2] - centers[j][2]) ** 2) ** 0.5
            gaps["%s_%s" % (created[i], created[j])] = round(d - 0.216, 5)
            if d - 0.216 < 0.005 - 1e-6:
                raise ValueError("ball separation: %s %s" % (gaps, created))

    report = {
        "stage": "04",
        "revision": "rev8-balls",
        "created": created,
        "centers": [[round(c, 4) for c in cc] for cc in centers],
        "evidence": evidence,
        "rack_contact": contacts,
        "inter_ball_gaps_m": gaps,
        "rack_objects": sorted(rack_names),
        "materials": [s[1] for s in specs],
        "grip_facing": "+Y (hole centers near theta 52.5/90/127.5 deg)",
        "root_children": len(root.children),
    }
    return report


if __name__ == '__blender_author__':
    report = run()
