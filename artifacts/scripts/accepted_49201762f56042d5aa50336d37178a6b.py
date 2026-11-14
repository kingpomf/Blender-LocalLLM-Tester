import bpy
from math import cos, pi, sin

ROOT_NAME = "BowlingPair01_ROOT"
PINS = "BP01_PINS"
CX = 0.95
SPACING = 0.3048
HEAD_Y = 18.288
SEG = 24

PROFILE = [
    (0.000, 0.0300),
    (0.008, 0.0340),
    (0.025, 0.0420),
    (0.055, 0.0500),
    (0.090, 0.0560),
    (0.130, 0.0600),
    (0.150, 0.0605),
    (0.180, 0.0590),
    (0.210, 0.0545),
    (0.240, 0.0470),
    (0.270, 0.0360),
    (0.290, 0.0290),
    (0.300, 0.0255),
    (0.320, 0.0205),
    (0.345, 0.0250),
    (0.365, 0.0340),
    (0.372, 0.0395),
]
APEX_Z = 0.381
RED_BANDS = {10, 12}


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


def pin_mesh(white, red):
    n = SEG
    rows = len(PROFILE)
    verts = [(0.0, 0.0, 0.0)]
    rings = []
    for (z, r) in PROFILE:
        ring = []
        for k in range(n):
            a = 2 * pi * k / n
            ring.append(len(verts))
            verts.append((r * cos(a), r * sin(a), z))
        rings.append(ring)
    apex = len(verts)
    verts.append((0.0, 0.0, APEX_Z))

    faces = []
    slots = []
    base = rings[0]
    for k in range(n):
        faces.append((0, base[k], base[(k + 1) % n]))
        slots.append(0)
    for i in range(rows - 1):
        slot = 1 if (i in RED_BANDS) else 0
        lo, hi = rings[i], rings[i + 1]
        for k in range(n):
            j = (k + 1) % n
            faces.append((lo[k], lo[j], hi[j], hi[k]))
            slots.append(slot)
    top = rings[-1]
    for k in range(n):
        faces.append((apex, top[(k + 1) % n], top[k]))
        slots.append(0)

    if signed_volume(verts, faces) < 0.0:
        faces = [tuple(reversed(f)) for f in faces]

    me = bpy.data.meshes.new("Pin_Body")
    me.from_pydata(verts, [], faces)
    me.validate(verbose=False, clean_customdata=True)
    me.update()
    if len(me.vertices) != len(verts) or len(me.polygons) != len(faces):
        raise ValueError("pin element loss: %d/%d verts %d/%d faces"
                         % (len(me.vertices), len(verts), len(me.polygons), len(faces)))
    if not all(p.area > 1e-9 for p in me.polygons):
        raise ValueError("degenerate pin face")
    uses = edge_uses(me)
    bad = sum(1 for c in uses.values() if c != 2)
    if bad or sum(1 for e in me.edges if e.is_loose):
        raise ValueError("pin non-manifold: %d bad edge uses" % bad)
    me.materials.append(white)
    me.materials.append(red)
    for idx, s in enumerate(slots):
        me.polygons[idx].material_index = s
    return me


def pin_evidence(ob):
    me = ob.data
    local = [v.co for v in me.vertices]
    loop_verts = [lp.vertex_index for lp in me.loops]
    zs = [c.z for c in local]
    radii = [(c.x ** 2 + c.y ** 2) ** 0.5 for c in local]
    neck = [r for c, r in zip(local, radii) if 0.27 <= c.z <= 0.34]
    tris = 0
    for p in me.polygons:
        tris += len(p.loop_indices) - 2
    bands = []
    for p in me.polygons:
        if p.material_index != 1:
            continue
        zs_f = [local[loop_verts[li]].z
                for li in range(p.loop_start, p.loop_start + p.loop_total)]
        bands.append((min(zs_f), max(zs_f)))
    merged = []
    for low, high in sorted(bands):
        if not merged or low > merged[-1][1] + 1e-5:
            merged.append([round(low, 4), round(high, 4)])
        else:
            merged[-1][1] = round(max(merged[-1][1], high), 4)
    mw = ob.matrix_world
    world = [(mw @ c) for c in local]
    wxs = [w.x for w in world]
    wys = [w.y for w in world]
    wzs = [w.z for w in world]
    return {
        "dims": [round(max(wxs) - min(wxs), 4), round(max(wys) - min(wys), 4),
                 round(max(wzs) - min(wzs), 4)],
        "world_min_z": round(min(wzs), 5),
        "local_min_z": round(min(zs), 5),
        "translation": [round(v, 4) for v in ob.matrix_world.translation],
        "scale": [round(v, 4) for v in ob.scale],
        "max_radius": round(max(radii), 4),
        "neck_min_radius": round(min(neck), 4) if neck else None,
        "neck_ratio": round(min(neck) / max(radii), 4) if neck else None,
        "triangles": tris,
        "red_band_intervals": merged,
    }


def run():
    root = bpy.data.objects[ROOT_NAME]
    pins_coll = bpy.data.collections[PINS]

    white = pbr_mat("MAT_PinWhite", (0.85, 0.84, 0.80), 0.30)
    red = pbr_mat("MAT_PinRed", (0.55, 0.045, 0.045), 0.32)

    me = pin_mesh(white, red)

    created = []
    evidence = {}
    for side, cx in (("L", -CX), ("R", CX)):
        number = 1
        for row in range(4):
            for column in range(row + 1):
                name = "Pin_%s_%02d" % (side, number)
                x = cx + (column - row / 2) * SPACING
                y = HEAD_Y + row * (3 ** 0.5) / 2 * SPACING
                ob = bpy.data.objects.new(name, me)
                ob.parent = root
                ob.location = (x, y, 0.0)
                ob.rotation_euler = (0.0, 0.0, 0.0)
                ob.scale = (1.0, 1.0, 1.0)
                pins_coll.objects.link(ob)
                created.append(name)
                ev = pin_evidence(ob)
                if abs(ev["dims"][2] - 0.381) > 0.003:
                    raise ValueError("pin height out of tolerance: %s %s" % (name, ev["dims"]))
                if abs(max(ev["dims"][:2]) - 0.121) > 0.003:
                    raise ValueError("pin diameter out of tolerance: %s %s" % (name, ev["dims"]))
                if not ev["neck_ratio"] or ev["neck_ratio"] >= 0.65:
                    raise ValueError("pin neck ratio fails: %s %s" % (name, ev["neck_ratio"]))
                if ev["triangles"] > 2500:
                    raise ValueError("pin triangle budget: %s %s" % (name, ev["triangles"]))
                if len(ev["red_band_intervals"]) != 2:
                    raise ValueError("pin red bands: %s %s" % (name, ev["red_band_intervals"]))
                if not all(0.24 <= lo < hi <= 0.36 for lo, hi in ev["red_band_intervals"]):
                    raise ValueError("pin band z range: %s %s" % (name, ev["red_band_intervals"]))
                evidence[name] = ev
                number += 1

    report = {
        "stage": "03",
        "revision": "rev6c-pins",
        "pin_count": len(created),
        "shared_mesh": me.name,
        "mesh_users": me.users,
        "sample": {n: evidence[n] for n in ("Pin_L_01", "Pin_L_07", "Pin_R_01", "Pin_R_10")},
        "neck_ratio": evidence["Pin_L_01"]["neck_ratio"],
        "triangles_per_pin": evidence["Pin_L_01"]["triangles"],
        "red_bands": evidence["Pin_L_01"]["red_band_intervals"],
        "materials": [white.name, red.name],
        "positions": {n: evidence[n]["translation"] for n in created},
        "pin_collection_contents": sorted(o.name for o in pins_coll.objects),
    }
    return report


if __name__ == '__blender_author__':
    report = run()
