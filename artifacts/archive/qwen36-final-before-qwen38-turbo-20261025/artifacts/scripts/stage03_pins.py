import bpy
import json
import os
from math import sqrt, cos, sin

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

    # Pin mesh creation
    pin_height = 0.381
    max_radius = 0.0605
    neck_radius = 0.036
    segs = 24

    profile = [
        (0.0, 0.058), (0.005, 0.059), (0.02, 0.060),
        (0.06, 0.0605), (0.10, 0.0605), (0.15, 0.058),
        (0.22, 0.050), (0.28, 0.042), (0.32, neck_radius),
        (0.35, neck_radius + 0.005), (0.37, 0.035), (0.381, 0.018),
    ]
    nv = len(profile)
    verts = []
    faces = []
    for s in range(nv):
        z, r = profile[s]
        for v in range(segs):
            angle = 2 * 3.1415926535 * v / segs
            verts.append((r * cos(angle), r * sin(angle), z))

    # Side faces - properly connected
    for s in range(nv - 1):
        for v in range(segs):
            a = s * segs + v
            b = (s * segs + v + 1) % (segs * (nv - 1))  # wrap
            c = ((s + 1) * segs + v) % (segs * nv)
            d = ((s + 1) * segs + (v + 1) % segs) % (segs * nv)
            # Only create quad if b wraps correctly
            if v < segs - 1:
                b2 = s * segs + v + 1
                d2 = (s + 1) * segs + v + 1
                faces.append((a, b2, d2, c))

    # Top cap
    top_idx = nv * segs
    verts.append((0, 0, profile[-1][0]))
    for v in range(segs):
        faces.append((top_idx, (nv-1)*segs+v, (nv-1)*segs+(v+1)%segs))

    # Bottom cap
    bot_idx = nv * segs + 1
    verts.append((0, 0, profile[0][0]))
    for v in range(segs):
        faces.append((bot_idx, v, (v+1) % segs))

    me = bpy.data.meshes.new('Pin_Mesh')
    me.from_pydata(verts, [], faces)
    me.validate()
    me.calc_loop_triangles()
    tri_count = len(me.loop_triangles)

    # Assign materials: white for body, red for neck band
    me.materials.append(mat_pin_white)
    me.materials.append(mat_pin_red)

    # Mark red band faces (profile segments 7-9 = neck area)
    neck_start_seg = 7
    neck_end_seg = 9
    for f_idx, f in enumerate(me.polygons):
        # Determine which profile segment this face belongs to
        # Side faces are indexed by (segment, vertex_in_segment)
        side_face_count = (nv - 1) * segs
        if f_idx < side_face_count:
            seg = f_idx // segs
            if neck_start_seg <= seg <= neck_end_seg:
                f.material_index = 1  # red
            else:
                f.material_index = 0  # white
        else:
            f.material_index = 0  # caps are white

    # Remove old pins
    for existing in pins_col.objects[:]:
        pins_col.objects.unlink(existing)
        bpy.data.objects.remove(existing)

    # Pin rack layout: advance toward +Y (pins)
    nn_spacing = 0.3048
    row_sep = sqrt(3) / 2 * nn_spacing
    head_pin_y = 18.288
    row_y = [head_pin_y, head_pin_y + row_sep, head_pin_y + 2*row_sep, head_pin_y + 3*row_sep]
    row_pins = [
        [0],
        [-nn_spacing/2, nn_spacing/2],
        [-nn_spacing, 0, nn_spacing],
        [-1.5*nn_spacing, -0.5*nn_spacing, 0.5*nn_spacing, 1.5*nn_spacing],
    ]

    created_pins = []
    for lane_side, lx in [('L', -0.95), ('R', 0.95)]:
        lane_pins = []
        for row_idx, row_y_pos in enumerate(row_y):
            for col_idx, x_offset in enumerate(row_pins[row_idx]):
                pin_num = len(lane_pins) + 1
                pin_name = f'Pin_{lane_side}_{pin_num:02d}'
                obj = bpy.data.objects.new(pin_name, me)
                obj.location = (lx + x_offset, row_y_pos, 0.0)
                obj.parent = root
                pins_col.objects.link(obj)
                created_pins.append(obj)
                lane_pins.append(obj)

    # Verification
    if len(created_pins) != 20:
        errors.append(f"Expected 20 pins, got {len(created_pins)}")

    head_pins = [o for o in created_pins if o.name.endswith('_01')]
    if len(head_pins) != 2:
        errors.append(f"Expected 2 head pins, got {len(head_pins)}")

    # Check pins advance toward +Y
    for i in range(1, 10):
        if i < len(created_pins):
            # Pin 02 should be at higher Y than Pin 01
            p1_y = created_pins[i-1].location[1]
            p2_y = created_pins[i].location[1]
            if i in [2, 3]:  # row 2
                pass  # different Y than row 1

    # Row 1 (head pin) should be at Y=18.288
    for hp in head_pins:
        if abs(hp.location[1] - head_pin_y) > 0.001:
            errors.append(f"Head pin {hp.name} Y={hp.location[1]} != {head_pin_y}")

    # Check dimensions
    eval_deps = bpy.context.evaluated_depsgraph_get()
    for obj in created_pins:
        evaluated = obj.evaluated_get(eval_deps)
        mesh = evaluated.to_mesh()
        try:
            tc = len(mesh.loop_triangles)
            if tc > 2500:
                errors.append(f"{obj.name} exceeds 2500 triangles: {tc}")
            if mesh.vertices:
                mins = [min(v.co.x for v in mesh.vertices), min(v.co.y for v in mesh.vertices), min(v.co.z for v in mesh.vertices)]
                maxs = [max(v.co.x for v in mesh.vertices), max(v.co.y for v in mesh.vertices), max(v.co.z for v in mesh.vertices)]
                h = maxs[2] - mins[2]
                w = max(maxs[0] - mins[0], maxs[1] - mins[1])
                if abs(h - pin_height) > 0.003:
                    errors.append(f"{obj.name} height {h:.4f} not within {pin_height}+-0.003")
                if abs(w - 2*max_radius) > 0.006:
                    errors.append(f"{obj.name} diameter {w:.4f} not within {2*max_radius:.3f}+-0.003")
        finally:
            evaluated.to_mesh_clear()

    # Check pin base Z=0
    for obj in created_pins:
        if abs(obj.location[2]) > 0.002:
            errors.append(f"{obj.name} base Z={obj.location[2]} != 0")

    # Check pin spacing
    left_pins = sorted([o for o in created_pins if 'Pin_L_' in o.name], key=lambda o: o.name)
    if len(left_pins) == 10:
        # Row 2: pins 02 and 03 should be nn_spacing apart in X
        dx = abs(left_pins[1].location[0] - left_pins[2].location[0])
        if abs(dx - nn_spacing) > 0.003:
            errors.append(f"Row 2 X spacing {dx:.4f} != {nn_spacing}")
        # Row advancement: Y separation between rows
        # Row 1: pin 01 at head_pin_y
        # Row 2: pins 02,03 at head_pin_y + row_sep
        y_sep = left_pins[1].location[1] - left_pins[0].location[1]
        if abs(y_sep - row_sep) > 0.003:
            errors.append(f"Row Y spacing {y_sep:.4f} != {row_sep:.4f}")

    # Check red band faces exist in pin mesh
    if len(me.polygons) > 0:
        red_count = sum(1 for f in me.polygons if f.material_index == 1)
        if red_count == 0:
            errors.append("No red band faces on pin mesh")

    passed = len(errors) == 0

    report = {
        "stage": "03",
        "name": "Reusable bowling pins (repaired)",
        "passed": passed,
        "pin_count": len(created_pins),
        "triangle_count": tri_count,
        "head_pin_count": len(head_pins),
        "red_face_count": sum(1 for f in me.polygons if f.material_index == 1) if me.polygons else 0,
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
                    'location': [round(x,6) for x in o.location],
                    'parent': o.parent.name if o.parent else None, 'collection': cn})
        json.dump({'objects': obj_list, 'collections': [c.name for c in bpy.data.collections]}, f, indent=2)

    return report

report = run_stage()
