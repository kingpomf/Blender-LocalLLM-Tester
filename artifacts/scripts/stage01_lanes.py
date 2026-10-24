import bpy
import json
import os
from math import cos, sin, pi
from mathutils import Vector

def run_stage():
    scene = bpy.context.scene

    # --- Load source scene ---
    # source_job provides the Stage 00 scene with root + collections

    required_names = ['BP01_STATIC', 'BP01_PINS', 'BP01_BALLS', 'BP01_COLLISION', 'BP01_PRESENTATION']
    for name in required_names:
        assert name in bpy.data.collections, f"Missing collection {name}"

    errors = []

    # --- Materials ---
    # Wood material for lanes/approach
    mat_wood = bpy.data.materials.new('Mat_Wood')
    mat_wood.use_nodes = True
    bg = mat_wood.node_tree.nodes['Material Output']
    principled = mat_wood.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    principled.inputs['Base Color'].default_value = (0.72, 0.52, 0.28, 1.0)
    principled.inputs['Roughness'].default_value = 0.55
    mat_wood.node_tree.links.new(principled.outputs['BSDF'], bg.inputs['Surface'])

    # Dark foul line material
    mat_foul = bpy.data.materials.new('Mat_FoulLine')
    mat_foul.use_nodes = True
    bg2 = mat_foul.node_tree.nodes['Material Output']
    p2 = mat_foul.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    p2.inputs['Base Color'].default_value = (0.15, 0.12, 0.10, 1.0)
    p2.inputs['Roughness'].default_value = 0.6
    mat_foul.node_tree.links.new(p2.outputs['BSDF'], bg2.inputs['Surface'])

    # Arrow material (dark marking on wood)
    mat_arrow = bpy.data.materials.new('Mat_Arrow')
    mat_arrow.use_nodes = True
    bg3 = mat_arrow.node_tree.nodes['Material Output']
    p3 = mat_arrow.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    p3.inputs['Base Color'].default_value = (0.18, 0.15, 0.12, 1.0)
    p3.inputs['Roughness'].default_value = 0.7
    mat_arrow.node_tree.links.new(p3.outputs['BSDF'], bg3.inputs['Surface'])

    # Dot material (light circle on wood)
    mat_dot = bpy.data.materials.new('Mat_Dot')
    mat_dot.use_nodes = True
    bg4 = mat_dot.node_tree.nodes['Material Output']
    p4 = mat_dot.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    p4.inputs['Base Color'].default_value = (0.35, 0.28, 0.15, 1.0)
    p4.inputs['Roughness'].default_value = 0.7
    mat_dot.node_tree.links.new(p4.outputs['BSDF'], bg4.inputs['Surface'])

    # --- Helper: create a thin box mesh ---
    def make_box(name, w, h, d, loc):
        me = bpy.data.meshes.new(name + '_Mesh')
        obj = bpy.data.objects.new(name, me)
        # Box from -w/2 to w/2, etc
        hw, hh, hd = w / 2.0, h / 2.0, d / 2.0
        verts = [
            (-hw, -hd, -hh), (hw, -hd, -hh), (hw, hd, -hh), (-hw, hd, -hh),
            (-hw, -hd, hh), (hw, -hd, hh), (hw, hd, hh), (-hw, hd, hh),
        ]
        faces = [(0,1,2,3), (4,5,6,7), (0,4,5,1), (3,2,1,0), (4,0,3,7), (5,4,7,6)]
        me.from_pydata(verts, [], faces)
        me.validate()
        obj.location = loc
        # Apply material
        me.materials.append(mat_wood)
        return obj

    # --- Lane dimensions ---
    lane_width = 1.0668       # ±0.005
    lane_length = 19.20       # Y=0 to Y=19.20
    lane_thickness = 0.15     # extends below Z=0
    lane_half_w = lane_width / 2.0

    # Approach dimensions
    approach_length = 4.572   # Y=-4.572 to Y=0
    approach_thickness = 0.15

    # Foul line dimensions
    foul_width = lane_width + 0.02
    foul_thickness = 0.003
    foul_depth = 0.04  # 0.04m strip at Y=0

    # Arrow dimensions
    arrow_width = 0.06
    arrow_height = 0.003
    arrow_depth = 0.12
    arrow_y_positions = [-0.15, -0.05, 0.05, 0.15, 0.25, 0.35, 0.45]  # centered near Y=4.57 offset
    # Arrows are centered at Y=4.57, so offset from center of arrow strip
    arrow_center_y = 4.57
    # Arrow spacing ~0.10m across lane
    arrow_x_spread = 0.35

    # Dot dimensions
    dot_radius = 0.02
    dot_thickness = 0.003
    dot_center_y = -1.0

    # --- Root ---
    root = bpy.data.objects['BowlingPair01_ROOT']
    static_col = bpy.data.collections['BP01_STATIC']

    # --- Left lane ---
    ll = make_box('Lane_L_Surface', lane_width, lane_length, lane_thickness,
                  ( -0.95, lane_length / 2.0, -lane_thickness / 2.0))
    static_col.objects.link(ll)
    ll.parent = root

    # Right lane
    rl = make_box('Lane_R_Surface', lane_width, lane_length, lane_thickness,
                  ( 0.95, lane_length / 2.0, -lane_thickness / 2.0))
    static_col.objects.link(rl)
    rl.parent = root

    # --- Left approach ---
    lap = make_box('Approach_L', lane_width, approach_length, approach_thickness,
                   (-0.95, -approach_length / 2.0, -approach_thickness / 2.0))
    static_col.objects.link(lap)
    lap.parent = root

    # Right approach
    rap = make_box('Approach_R', lane_width, approach_length, approach_thickness,
                   (0.95, -approach_length / 2.0, -approach_thickness / 2.0))
    static_col.objects.link(rap)
    rap.parent = root

    # --- Foul lines ---
    for lx, lname in [(-0.95, 'Foul_L'), (0.95, 'Foul_R')]:
        foul = make_box(lname, foul_width, foul_depth, foul_thickness,
                        (lx, 0.0, lane_thickness - foul_thickness / 2.0))
        foul.data.materials[0] = mat_foul
        static_col.objects.link(foul)
        foul.parent = root

    # --- Arrow strips (7 per lane) ---
    for lx, lname in [(-0.95, 'ArrowStrip_L'), (0.95, 'ArrowStrip_R')]:
        # Single thin strip at Y=arrow_center_y
        arrow_strip = make_box('ArrowStrip_' + lname[5:], 0.08, 0.65, arrow_height,
                               (lx, arrow_center_y, lane_thickness - arrow_height / 2.0))
        arrow_strip.data.materials[0] = mat_arrow
        static_col.objects.link(arrow_strip)
        arrow_strip.parent = root

    # --- Arrow triangles (7 per lane) on the strip ---
    arrow_positions = [-arrow_x_spread, -arrow_x_spread * 0.66, -arrow_x_spread * 0.33,
                       0.0, arrow_x_spread * 0.33, arrow_x_spread * 0.66, arrow_x_spread]

    for lx, lname in [(-0.95, 'ArrowTri_L'), (0.95, 'ArrowTri_R')]:
        for i, ax in enumerate(arrow_positions):
            me = bpy.data.meshes.new(f'{lname}_{i+1:02d}_Mesh')
            # Triangle pointing toward pins (+Y)
            tri_w = 0.045
            tri_h = 0.06
            cx = lx + ax
            cy = arrow_center_y
            verts = [
                (cx - tri_w/2, cy - tri_h/2, lane_thickness - arrow_height/2),
                (cx + tri_w/2, cy - tri_h/2, lane_thickness - arrow_height/2),
                (cx, cy + tri_h/2, lane_thickness - arrow_height/2),
            ]
            me.from_pydata(verts, [], [(0, 1, 2)])
            me.validate()
            obj = bpy.data.objects.new(f'{lname}_{i+1:02d}', me)
            obj.location = (0, 0, 0)
            obj.data.materials.append(mat_arrow)
            static_col.objects.link(obj)
            obj.parent = root

    # --- Dots (7 per lane) ---
    for lx, lname in [(-0.95, 'Dot_L'), (0.95, 'Dot_R')]:
        for i, ax in enumerate(arrow_positions):
            # Circle mesh for dots using from_pydata
            me = bpy.data.meshes.new(f'{lname}_{i+1:02d}_Mesh')
            cx = lx + ax
            cy = dot_center_y
            cz = lane_thickness - dot_thickness / 2.0
            nv = 16
            verts = []
            faces = []
            for v in range(nv):
                angle = 2 * 3.14159265 * v / nv
                vx = cx + dot_radius * cos(angle)
                vy = cy + dot_radius * sin(angle)
                verts.append((vx, vy, cz))
            faces.append(tuple(range(nv)))
            me.from_pydata(verts, [], faces)
            me.validate()
            obj = bpy.data.objects.new(f'{lname}_{i+1:02d}', me)
            obj.location = (0, 0, 0)
            obj.data.materials.append(mat_dot)
            static_col.objects.link(obj)
            obj.parent = root

    # --- Verification ---
    # Count lane surfaces
    lane_objs = [o for o in static_col.objects if o.name in ('Lane_L_Surface', 'Lane_R_Surface', 'Approach_L', 'Approach_R')]
    if len(lane_objs) != 4:
        errors.append(f"Expected 4 lane/approach objects, got {len(lane_objs)}")

    # Check lane surface dimensions
    for lo in lane_objs:
        if lo.name.endswith('_Surface'):
            w = lo.dimensions.x
            l = lo.dimensions.y
            if abs(w - lane_width) > 0.005:
                errors.append(f"{lo.name} width {w} not within {lane_width}±0.005")
            if abs(l - lane_length) > 0.01:
                errors.append(f"{lo.name} length {l} not within {lane_length}±0.01")

    # Check approach bounds
    for aname in ('Approach_L', 'Approach_R'):
        ao = [o for o in static_col.objects if o.name == aname][0]
        if abs(ao.dimensions.y - approach_length) > 0.01:
            errors.append(f"{aname} approach length wrong: {ao.dimensions.y}")

    # Check foul line count (2)
    foul_objs = [o for o in static_col.objects if o.name.startswith('Foul_')]
    if len(foul_objs) != 2:
        errors.append(f"Expected 2 foul lines, got {len(foul_objs)}")

    # Check arrow count (14 total = 7 per lane)
    arrow_tris = [o for o in static_col.objects if o.name.startswith('ArrowTri_')]
    if len(arrow_tris) != 14:
        errors.append(f"Expected 14 arrow triangles, got {len(arrow_tris)}")

    # Check dot count (14 total = 7 per lane)
    dots = [o for o in static_col.objects if o.name.startswith('Dot_')]
    if len(dots) != 14:
        errors.append(f"Expected 14 dots, got {len(dots)}")

    # Check all objects are children of root or linked to static_col
    for o in static_col.objects:
        if o.parent != root:
            errors.append(f"{o.name} not parented to root")

    passed = len(errors) == 0

    report = {
        "stage": "01",
        "name": "Lane pair and markings",
        "passed": passed,
        "lane_count": len([o for o in static_col.objects if 'Lane' in o.name]),
        "approach_count": len([o for o in static_col.objects if 'Approach' in o.name]),
        "foul_line_count": len(foul_objs),
        "arrow_count": len(arrow_tris),
        "dot_count": len(dots),
        "total_objects": len(static_col.objects),
        "errors": errors,
    }

    out_dir = '/job'
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, 'report.json'), 'w') as f:
        json.dump(report, f, indent=2)

    with open(os.path.join(out_dir, 'scene.json'), 'w') as f:
        obj_list = []
        for o in scene.collection.objects:
            obj_list.append({
                'name': o.name,
                'type': o.type,
                'location': [round(x, 6) for x in o.location],
                'parent': o.parent.name if o.parent else None,
            })
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
