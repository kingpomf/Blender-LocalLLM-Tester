import bpy
import json
import os
from math import cos, sin, pi

def run_stage():
    scene = bpy.context.scene
    required_names = ['BP01_STATIC', 'BP01_PINS', 'BP01_BALLS', 'BP01_COLLISION', 'BP01_PRESENTATION']
    for name in required_names:
        assert name in bpy.data.collections, f"Missing collection {name}"
    errors = []
    root = bpy.data.objects['BowlingPair01_ROOT']
    pins_col = bpy.data.collections['BP01_PINS']
    static_col = bpy.data.collections['BP01_STATIC']

    for r in ('Lane_L_Surface', 'Lane_R_Surface'):
        assert r in bpy.data.objects, f"Missing: {r}"

    # Materials
    mat_pin_white = bpy.data.materials.new('Mat_PinWhite')
    mat_pin_white.use_nodes = True
    bg = mat_pin_white.node_tree.nodes['Material Output']
    p = mat_pin_white.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value = (0.93, 0.91, 0.88, 1.0)
    p.inputs['Roughness'].default_value = 0.35
    mat_pin_white.node_tree.links.new(p.outputs['BSDF'], bg.inputs['Surface'])

    mat_pin_red = bpy.data.materials.new('Mat_PinRed')
    mat_pin_red.use_nodes = True
    bg2 = mat_pin_red.node_tree.nodes['Material Output']
    p2 = mat_pin_red.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    p2.inputs['Base Color'].default_value = (0.70, 0.10, 0.10, 1.0)
    p2.inputs['Roughness'].default_value = 0.35
    mat_pin_red.node_tree.links.new(p2.outputs['BSDF'], bg2.inputs['Surface'])

    # Pin mesh: clean lathe
    pin_height = 0.381
    profile = [
        (0.058, 0.0), (0.060, 0.003), (0.0605, 0.010),
        (0.0605, 0.040), (0.0600, 0.080), (0.0570, 0.130),
        (0.0480, 0.190), (0.0380, 0.250), (0.0300, 0.290),
        (0.0320, 0.320), (0.0250, 0.355), (0.0150, 0.381),
    ]
    segs = 24
    nv = len(profile)

    verts = []
    for z, r in profile:
        for v in range(segs):
            angle = 2 * pi * v / segs
            verts.append((r * cos(angle), r * sin(angle), z))

    faces = []
    side_count = (nv - 1) * segs
    for s in range(nv - 1):
        for v in range(segs):
            a = s * segs + v
            b = s * segs + (v + 1) % segs
            d = (s + 1) * segs + (v + 1) % segs
            c = (s + 1) * segs + v
            faces.append((a, b, d, c))

    # Top cap (head)
    top_idx = nv * segs
    verts.append((0, 0, profile[-1][0]))
    for v in range(segs):
        faces.append((top_idx, (nv - 1) * segs + v, (nv - 1) * segs + (v + 1) % segs))

    # Bottom cap
    bot_idx = nv * segs + 1
    verts.append((0, 0, profile[0][0]))
    for v in range(segs):
        faces.append((bot_idx, v, (v + 1) % segs))

    me = bpy.data.meshes.new('Pin_Mesh')
    me.from_pydata(verts, [], faces)
    me.validate()
    me.update()
    tri_count = len(me.loop_triangles)

    me.materials.append(mat_pin_white)
    me.materials.append(mat_pin_red)

    band_start_seg = 6
    band_end_seg = 8
    for f_idx, f in enumerate(me.polygons):
        if f_idx < side_count:
            seg = f_idx // segs
            if band_start_seg <= seg <= band_end_seg:
                f.material_index = 1
            else:
                f.material_index = 0
        else:
            f.material_index = 0

    # Copy mesh BEFORE removing old objects (old objects share the mesh data block)
    pin_copy = me.copy()
    pin_copy.name = 'Pin_Mesh_Copied'
    pin_copy.materials.clear()
    pin_copy.materials.append(mat_pin_white)
    pin_copy.materials.append(mat_pin_red)
    for f_idx, f in enumerate(pin_copy.polygons):
        if f_idx < side_count:
            seg = f_idx // segs
            if band_start_seg <= seg <= band_end_seg:
                f.material_index = 1
            else:
                f.material_index = 0
        else:
            f.material_index = 0

    old_names = [o.name for o in pins_col.objects[:]]
    for nm in old_names:
        old_obj = bpy.data.objects[nm]
        pins_col.objects.unlink(old_obj)
        bpy.data.objects.remove(old_obj)

    # Pin rack layout
    nn_spacing = 0.3048
    row_sep = (3 ** 0.5) / 2 * nn_spacing
    head_pin_y = 18.288
    row_y = [head_pin_y, head_pin_y + row_sep, head_pin_y + 2 * row_sep, head_pin_y + 3 * row_sep]
    row_pins = [
        [0],
        [-nn_spacing / 2, nn_spacing / 2],
        [-nn_spacing, 0, nn_spacing],
        [-1.5 * nn_spacing, -0.5 * nn_spacing, 0.5 * nn_spacing, 1.5 * nn_spacing],
    ]

    created_pins = []
    for lane_side, lx in [('L', -0.95), ('R', 0.95)]:
        lane_pin_count = 0
        for row_idx, ry_pos in enumerate(row_y):
            for col_idx, x_off in enumerate(row_pins[row_idx]):
                lane_pin_count += 1
                pin_name = f'Pin_{lane_side}_{lane_pin_count:02d}'
                obj = bpy.data.objects.new(pin_name, pin_copy)
                obj.location = (lx + x_off, ry_pos, 0.0)
                obj.parent = root
                pins_col.objects.link(obj)
                created_pins.append(obj)

    # Verification
    if len(created_pins) != 20:
        errors.append(f"Expected 20 pins, got {len(created_pins)}")

    head_pins = [o for o in created_pins if '_01' in o.name]
    left_pins = sorted([o for o in created_pins if 'Pin_L_' in o.name], key=lambda o: int(o.name.split('_')[-1]))
    right_pins = sorted([o for o in created_pins if 'Pin_R_' in o.name], key=lambda o: int(o.name.split('_')[-1]))

    for lane, pins in [('Left', left_pins), ('Right', right_pins)]:
        if len(pins) != 10:
            errors.append(f"{lane} has {len(pins)} pins, expected 10")
    if len(head_pins) != 2:
        errors.append(f"Expected 2 head pins, got {len(head_pins)}")

    # Check Y advancement
    if len(left_pins) >= 2:
        y1 = left_pins[0].location[1]
        y2 = left_pins[1].location[1]
        if y2 <= y1:
            errors.append(f"Row advancement failed: pin 01 Y={y1} >= pin 02 Y={y2}")

    # Check head pin Y
    for hp in head_pins:
        if abs(hp.location[1] - head_pin_y) > 0.005:
            errors.append(f"Head pin {hp.name} Y={hp.location[1]:.4f} != {head_pin_y}")

    # Check dimensions and topology
    eval_deps = bpy.context.eval_depsgraph_get() if hasattr(bpy.context, 'evaluated_depsgraph_get') else bpy.context.evaluated_depsgraph_get()
    for obj in created_pins[:1]:
        evaluated = obj.evaluated_get(eval_deps)
        emesh = evaluated.to_mesh()
        try:
            tc = len(emesh.loop_triangles)
            if tc > 2500:
                errors.append(f"{obj.name} exceeds 2500 triangles: {tc}")
            verts_z = [v.co.z for v in emesh.vertices]
            verts_r = [(v.co.x**2 + v.co.y**2)**0.5 for v in emesh.vertices]
            h = max(verts_z) - min(verts_z)
            w = 2 * max(verts_r)
            if abs(h - pin_height) > 0.005:
                errors.append(f"{obj.name} height {h:.4f} != {pin_height}")
            if abs(w - 2 * 0.0605) > 0.005:
                errors.append(f"{obj.name} diameter {w:.4f} != 0.121")
        finally:
            evaluated.to_mesh_clear()

    # Check red band faces
    red_count = sum(1 for f in pin_copy.polygons if f.material_index == 1)
    if red_count == 0:
        errors.append("No red band faces on pin mesh")
    else:
        print(f"Red band faces: {red_count}")

    expected_faces = side_count + segs + segs
    actual_faces = len(pin_copy.polygons)
    if actual_faces != expected_faces:
        errors.append(f"Pin face count {actual_faces} != expected {expected_faces}")

    passed = len(errors) == 0

    report = {
        "stage": "03",
        "name": "Reusable bowling pins (repaired clean lathe)",
        "passed": passed,
        "pin_count": len(created_pins),
        "triangle_count": tri_count,
        "head_pin_count": len(head_pins),
        "red_face_count": red_count,
        "face_count": actual_faces,
        "expected_face_count": expected_faces,
        "errors": errors,
    }

    out_dir = '/job'
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, 'report.json'), 'w') as f:
        json.dump(report, f, indent=2)
    with open(os.path.join(out_dir, 'scene.json'), 'w') as f:
        obj_list = []
        for cn in required_names:
            col = bpy.data.collections[cn]
            for o in col.objects:
                obj_list.append({'name': o.name, 'type': o.type,
                    'location': [round(x, 6) for x in o.location],
                    'parent': o.parent.name if o.parent else None, 'collection': cn})
        json.dump({'objects': obj_list, 'collections': [c.name for c in bpy.data.collections]}, f, indent=2)

    return report

report = run_stage()
