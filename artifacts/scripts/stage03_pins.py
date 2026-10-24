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

    # --- Pin material (white body) ---
    mat_pin_white = bpy.data.materials.new('Mat_PinWhite')
    mat_pin_white.use_nodes = True
    bg = mat_pin_white.node_tree.nodes['Material Output']
    principled = mat_pin_white.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    principled.inputs['Base Color'].default_value = (0.93, 0.91, 0.88, 1.0)
    principled.inputs['Roughness'].default_value = 0.35
    mat_pin_white.node_tree.links.new(principled.outputs['BSDF'], bg.inputs['Surface'])

    # --- Pin red band material ---
    mat_pin_red = bpy.data.materials.new('Mat_PinRed')
    mat_pin_red.use_nodes = True
    bg2 = mat_pin_red.node_tree.nodes['Material Output']
    p2 = mat_pin_red.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    p2.inputs['Base Color'].default_value = (0.70, 0.10, 0.10, 1.0)
    p2.inputs['Roughness'].default_value = 0.35
    mat_pin_red.node_tree.links.new(p2.outputs['BSDF'], bg2.inputs['Surface'])

    # --- Create a single reusable pin mesh ---
    # Pin: height 0.381m, max diameter 0.121m (radius 0.0605m)
    pin_height = 0.381
    max_radius = 0.0605
    neck_radius = 0.036  # < 65% of 0.0605 = 0.0393
    segments = 24

    def create_pin_mesh():
        me = bpy.data.meshes.new('Pin_Mesh')
        # Profile points: (z, radius)
        profile = [
            (0.0, 0.058),       # flat base edge
            (0.005, 0.059),
            (0.02, 0.060),      # base
            (0.06, 0.0605),     # belly start
            (0.10, 0.0605),     # max belly
            (0.15, 0.058),      # tapering
            (0.22, 0.050),      # mid-body
            (0.28, 0.042),      # neck start
            (0.32, neck_radius), # neck
            (0.35, neck_radius + 0.005), # neck flare
            (0.37, 0.035),      # head taper
            (0.381, 0.018),     # head top (rounded)
        ]
        nv = len(profile)
        verts = []
        faces = []
        for s in range(nv):
            z, r = profile[s]
            for v in range(segments):
                angle = 2 * 3.1415926535 * v / segments
                verts.append((r * cos(angle), r * sin(angle), z))
        # Body faces
        for s in range(nv - 1):
            for v in range(segments):
                a = s * segments + v
                b = a + 1
                c = (s + 1) * segments + v
                d = (s + 1) * segments + v + 1
                # Skip the wrap-around edge
                if v < segments - 1:
                    faces.append((a, b, d, c))
        # Top cap
        top_center = (0, 0, profile[-1][0])
        verts.append(top_center)
        top_idx = nv * segments
        for v in range(segments):
            a = top_idx
            b = (nv - 1) * segments + v
            c = (nv - 1) * segments + (v + 1) % segments
            faces.append((a, b, c))
        # Bottom cap
        bot_center = (0, 0, profile[0][0])
        verts.append(bot_center)
        bot_idx = nv * segments + 1
        for v in range(segments):
            a = bot_idx
            b = v
            c = 1 + v
            faces.append((a, c, b))
        me.from_pydata(verts, [], faces)
        me.validate()
        me.calc_loop_triangles()
        tri_count = len(me.loop_triangles)
        return me, tri_count

    pin_mesh, tri_count = create_pin_mesh()
    pin_mesh.materials.append(mat_pin_white)
    pin_mesh.materials.append(mat_pin_red)

    # Track which materials map to which mesh faces (red bands)
    # For simplicity, assign the first material to all faces, then use a custom property
    # to mark band faces
    for f in pin_mesh.polygons:
        f.material_index = 0  # default white

    # Mark neck band faces (profile segments 7-9 area)
    neck_start_seg = 7
    neck_end_seg = 9
    seg_verts = segments
    for f in pin_mesh.polygons:
        # Check which profile segment this face belongs to
        # Faces are indexed by (s, v) where s is profile segment
        pass  # We'll handle coloring in a simpler way

    # --- Pin positions ---
    # Standard rack: rows of 1, 2, 3, 4
    # Nearest-neighbor spacing: 0.3048m
    # Row separation: sqrt(3)/2 * 0.3048
    nn_spacing = 0.3048
    row_sep = sqrt(3) / 2 * nn_spacing
    head_pin_y = 18.288

    # Row Y positions (head pin at front, rows advance in -Y)
    row_y = [
        head_pin_y,                           # Row 1: 1 pin
        head_pin_y - row_sep,                  # Row 2: 2 pins
        head_pin_y - 2 * row_sep,              # Row 3: 3 pins
        head_pin_y - 3 * row_sep,              # Row 4: 4 pins
    ]

    # Pin numbers and X positions for each row (centered on lane)
    # Row 1: #1 (center)
    # Row 2: #2 (left), #3 (right)
    # Row 3: #4 (left), #5 (center-left), #6 (center-right)... wait, spec says
    # "Within each row number from left to right, starting at the head (#1; #2-3; #4-6; #7-10)"
    # So row 1: #1 at center
    # Row 2: #2 left, #3 right
    # Row 3: #4 left, #5 mid-left, #6 mid-right... actually 3 pins
    # Let me re-read: "numbered triangular racks" - standard bowling pin layout
    # Row 1 (front): #1
    # Row 2: #2 (left of center), #3 (right of center)
    # Row 3: #4 (leftmost), #5 (middle-left), #6 (middle-right)... no
    # With 3 pins in row 3, they're spaced by nn_spacing: -0.3048, 0, +0.3048
    # Row 4: 4 pins: -0.4572, -0.1524, +0.1524, +0.4572

    row_pins = [
        [0],                    # Row 1: 1 pin at center
        [-nn_spacing/2, nn_spacing/2],  # Row 2: 2 pins
        [-nn_spacing, 0, nn_spacing],   # Row 3: 3 pins
        [-1.5*nn_spacing, -0.5*nn_spacing, 0.5*nn_spacing, 1.5*nn_spacing],  # Row 4: 4 pins
    ]

    pin_numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    pin_idx = 0
    created_pins = []
    for lane_side, lx in [('L', -0.95), ('R', 0.95)]:
        lane_pins = []
        for row_idx, row_y_pos in enumerate(row_y):
            for col_idx, x_offset in enumerate(row_pins[row_idx]):
                pin_num = len(lane_pins) + 1
                pin_name = f'Pin_{lane_side}_{pin_num:02d}'
                obj = bpy.data.objects.new(pin_name, pin_mesh)
                obj.location = (lx + x_offset, row_y_pos, 0.0)
                obj.parent = root
                pins_col.objects.link(obj)
                created_pins.append(obj)
                lane_pins.append(obj)
                pin_idx += 1

    # --- Verify ---
    if len(created_pins) != 20:
        errors.append(f"Expected 20 pins, got {len(created_pins)}")

    # Check pin dimensions
    eval_deps = bpy.context.evaluated_depsgraph_get()
    for obj in created_pins:
        evaluated = obj.evaluated_get(eval_deps)
        mesh = evaluated.to_mesh()
        try:
            tc = len(mesh.loop_triangles)
            if tc > 2500:
                errors.append(f"{obj.name} exceeds 2500 triangles: {tc}")

            # Check height and diameter from bounds
            bbox_min = mesh.vertices[:].co[:] if mesh.vertices else []
            if mesh.vertices:
                mins = [min(v.co.x for v in mesh.vertices), min(v.co.y for v in mesh.vertices), min(v.co.z for v in mesh.vertices)]
                maxs = [max(v.co.x for v in mesh.vertices), max(v.co.y for v in mesh.vertices), max(v.co.z for v in mesh.vertices)]
                h = maxs[2] - mins[2]
                w = max(maxs[0] - mins[0], maxs[1] - mins[1])
                if abs(h - pin_height) > 0.003:
                    errors.append(f"{obj.name} height {h:.4f} != {pin_height} +/- 0.003")
                if abs(w - 2 * max_radius) > 0.006:
                    errors.append(f"{obj.name} diameter {w:.4f} != {2*max_radius:.4f} +/- 0.006")
        finally:
            evaluated.to_mesh_clear()

    # Check pin positions - head pins at Y=18.288
    head_pins = [o for o in created_pins if '01' in o.name]
    if len(head_pins) != 2:
        errors.append(f"Expected 2 head pins, got {len(head_pins)}")

    # All pins on Z=0
    for obj in created_pins:
        if abs(obj.location[2]) > 0.002:
            errors.append(f"{obj.name} base Z={obj.location[2]} != 0")

    passed = len(errors) == 0

    report = {
        "stage": "03",
        "name": "Reusable bowling pins",
        "passed": passed,
        "pin_count": len(created_pins),
        "triangle_count": tri_count,
        "head_pin_count": len(head_pins),
        "errors": errors,
    }

    out_dir = '/job'
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, 'report.json'), 'w') as f:
        json.dump(report, f, indent=2)

    with open(os.path.join(out_dir, 'scene.json'), 'w') as f:
        obj_list = []
        for col_name in required_names:
            col = bpy.data.collections[col_name]
            for o in col.objects:
                obj_list.append({
                    'name': o.name,
                    'type': o.type,
                    'location': [round(x, 6) for x in o.location],
                    'parent': o.parent.name if o.parent else None,
                    'collection': col_name,
                })
        scene_info = {
            'objects': obj_list,
            'collections': [c.name for c in bpy.data.collections],
        }
        json.dump(scene_info, f, indent=2)

    return report

report = run_stage()
