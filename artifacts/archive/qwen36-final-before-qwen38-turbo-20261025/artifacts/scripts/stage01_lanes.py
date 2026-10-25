import bpy
import json
import os

def run_stage():
    scene = bpy.context.scene

    required_names = ['BP01_STATIC', 'BP01_PINS', 'BP01_BALLS', 'BP01_COLLISION', 'BP01_PRESENTATION']
    for name in required_names:
        assert name in bpy.data.collections, f"Missing collection {name}"

    errors = []

    root = bpy.data.objects['BowlingPair01_ROOT']
    static_col = bpy.data.collections['BP01_STATIC']

    # Verify Stage02 objects still exist (they were built from this scene)
    for required in ('Lane_L_Surface', 'Lane_R_Surface', 'Approach_L', 'Approach_R',
                     'Gutter_L_Outer', 'Gutter_L_Inner', 'Gutter_R_Inner', 'Gutter_R_Outer',
                     'Divider_Cap', 'PinDeck_L', 'PinDeck_R', 'Pit_Catch',
                     'OuterRail_L', 'OuterRail_R'):
        assert required in bpy.data.objects, f"Missing required object: {required}"

    # --- Materials (same as before) ---
    mat_wood = bpy.data.materials.new('Mat_Wood')
    mat_wood.use_nodes = True
    bg = mat_wood.node_tree.nodes['Material Output']
    principled = mat_wood.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    principled.inputs['Base Color'].default_value = (0.72, 0.52, 0.28, 1.0)
    principled.inputs['Roughness'].default_value = 0.55
    mat_wood.node_tree.links.new(principled.outputs['BSDF'], bg.inputs['Surface'])

    mat_foul = bpy.data.materials.new('Mat_FoulLine')
    mat_foul.use_nodes = True
    bg2 = mat_foul.node_tree.nodes['Material Output']
    p2 = mat_foul.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    p2.inputs['Base Color'].default_value = (0.15, 0.12, 0.10, 1.0)
    p2.inputs['Roughness'].default_value = 0.6
    mat_foul.node_tree.links.new(p2.outputs['BSDF'], bg2.inputs['Surface'])

    mat_arrow = bpy.data.materials.new('Mat_Arrow')
    mat_arrow.use_nodes = True
    bg3 = mat_arrow.node_tree.nodes['Material Output']
    p3 = mat_arrow.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    p3.inputs['Base Color'].default_value = (0.18, 0.15, 0.12, 1.0)
    p3.inputs['Roughness'].default_value = 0.7
    mat_arrow.node_tree.links.new(p3.outputs['BSDF'], bg3.inputs['Surface'])

    mat_dot = bpy.data.materials.new('Mat_Dot')
    mat_dot.use_nodes = True
    bg4 = mat_dot.node_tree.nodes['Material Output']
    p4 = mat_dot.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    p4.inputs['Base Color'].default_value = (0.35, 0.28, 0.15, 1.0)
    p4.inputs['Roughness'].default_value = 0.7
    mat_dot.node_tree.links.new(p4.outputs['BSDF'], bg4.inputs['Surface'])

    # --- Correct box mesh: 6 faces with proper vertex order ---
    # Vertex 0-3 at z=-h/2 (bottom), 4-7 at z=+h/2 (top)
    # All faces use CCW winding for outward normals
    def make_box(name, w, d, h, loc):
        me = bpy.data.meshes.new(name + '_Mesh')
        hw, hd, hh = w/2.0, d/2.0, h/2.0
        verts = [
            (-hw, -hd, -hh), (hw, -hd, -hh), (hw, hd, -hh), (-hw, hd, -hh),  # 0-3 bottom
            (-hw, -hd,  hh), (hw, -hd,  hh), (hw, hd,  hh), (-hw, hd,  hh),  # 4-7 top
        ]
        faces = [
            (0, 3, 2, 1),  # front (+Y)
            (5, 4, 7, 6),  # back (-Y)
            (4, 0, 1, 5),  # right (+X)
            (2, 3, 7, 6),  # left (-X)
            (3, 0, 4, 7),  # top (+Z)
            (1, 2, 6, 5),  # bottom (-Z)
        ]
        me.from_pydata(verts, [], faces)
        me.validate()
        obj = bpy.data.objects.new(name, me)
        obj.location = loc
        me.materials.append(mat_wood)
        return obj

    # --- Lane/approach dimensions ---
    lane_width = 1.0668
    lane_length = 19.20
    lane_thickness = 0.15
    approach_length = 4.572
    approach_thickness = 0.15

    # Lane tops are at Z=0 (center at -0.075)
    lane_center_z = -lane_thickness / 2.0

    # --- Rebuild lane surfaces ---
    for existing in ['Lane_L_Surface', 'Lane_R_Surface', 'Approach_L', 'Approach_R']:
        if existing in bpy.data.objects:
            old = bpy.data.objects[existing]
            if old.name in static_col.objects:
                static_col.objects.unlink(old)
            bpy.data.objects.remove(old)

    ll = make_box('Lane_L_Surface', lane_width, lane_length, lane_thickness,
                  (-0.95, lane_length / 2.0, lane_center_z))
    static_col.objects.link(ll)
    ll.parent = root

    rl = make_box('Lane_R_Surface', lane_width, lane_length, lane_thickness,
                  (0.95, lane_length / 2.0, lane_center_z))
    static_col.objects.link(rl)
    rl.parent = root

    lap = make_box('Approach_L', lane_width, approach_length, approach_thickness,
                   (-0.95, -approach_length / 2.0, -approach_thickness / 2.0))
    static_col.objects.link(lap)
    lap.parent = root

    rap = make_box('Approach_R', lane_width, approach_length, approach_thickness,
                   (0.95, -approach_length / 2.0, -approach_thickness / 2.0))
    static_col.objects.link(rap)
    rap.parent = root

    # --- Markings at Z=0 (flush with lane surface) ---
    foul_depth = 0.04
    foul_thickness = 0.003
    arrow_height = 0.003
    dot_radius = 0.02
    dot_thickness = 0.003
    arrow_center_y = 4.57
    dot_center_y = -1.0
    arrow_x_spread = 0.35
    arrow_positions = [-arrow_x_spread, -arrow_x_spread*0.66, -arrow_x_spread*0.33,
                       0.0, arrow_x_spread*0.33, arrow_x_spread*0.66, arrow_x_spread]

    # Remove old marking objects
    for existing in static_col.objects[:]:
        if existing.name.startswith('Foul_') or existing.name.startswith('ArrowTri_') or \
           existing.name.startswith('ArrowStrip_') or existing.name.startswith('Dot_'):
            static_col.objects.unlink(existing)
            bpy.data.objects.remove(existing)

    # Foul lines: thin strip centered at Z=0 (bottom at -foul_thickness/2, top at +foul_thickness/2)
    for lx in [-0.95, 0.95]:
        fname = 'Foul_L' if lx < 0 else 'Foul_R'
        foul = make_box(fname, lane_width + 0.02, foul_depth, foul_thickness,
                        (lx, 0.0, 0.0))
        foul.data.materials[0] = mat_foul
        static_col.objects.link(foul)
        foul.parent = root

    # Arrow strips: flat strip at Z=0
    for lx in [-0.95, 0.95]:
        sname = 'ArrowStrip_L' if lx < 0 else 'ArrowStrip_R'
        a_strip = make_box(sname, 0.08, 0.65, arrow_height, (lx, arrow_center_y, 0.0))
        a_strip.data.materials[0] = mat_arrow
        static_col.objects.link(a_strip)
        a_strip.parent = root

    # Arrow triangles: flat on surface at Z=0
    for lx in [-0.95, 0.95]:
        tname = 'ArrowTri_L' if lx < 0 else 'ArrowTri_R'
        for i, ax in enumerate(arrow_positions):
            me = bpy.data.meshes.new(f'{tname}_{i+1:02d}_Mesh')
            tri_w = 0.045
            tri_h = 0.06
            cx = lx + ax
            verts = [
                (cx - tri_w/2, arrow_center_y - tri_h/2, 0.0),
                (cx + tri_w/2, arrow_center_y - tri_h/2, 0.0),
                (cx, arrow_center_y + tri_h/2, 0.0),
            ]
            me.from_pydata(verts, [], [(0, 1, 2)])
            me.validate()
            obj = bpy.data.objects.new(f'{tname}_{i+1:02d}', me)
            obj.location = (0, 0, 0)
            obj.data.materials.append(mat_arrow)
            static_col.objects.link(obj)
            obj.parent = root

    # Dots: flat circles at Z=0
    from math import cos, sin, pi
    for lx in [-0.95, 0.95]:
        dname = 'Dot_L' if lx < 0 else 'Dot_R'
        for i, ax in enumerate(arrow_positions):
            me = bpy.data.meshes.new(f'{dname}_{i+1:02d}_Mesh')
            cx = lx + ax
            verts = []
            for v in range(16):
                angle = 2 * pi * v / 16
                verts.append((cx + dot_radius*cos(angle), dot_center_y + dot_radius*sin(angle), 0.0))
            me.from_pydata(verts, [], [tuple(range(16))])
            me.validate()
            obj = bpy.data.objects.new(f'{dname}_{i+1:02d}', me)
            obj.location = (0, 0, 0)
            obj.data.materials.append(mat_dot)
            static_col.objects.link(obj)
            obj.parent = root

    # --- Verification ---
    lane_objs = [o for o in static_col.objects if o.name in ('Lane_L_Surface', 'Lane_R_Surface', 'Approach_L', 'Approach_R')]
    if len(lane_objs) != 4:
        errors.append(f"Expected 4 lane/approach objects, got {len(lane_objs)}")

    # Check lane surface Z position (top should be at Z=0)
    for lo in lane_objs:
        if lo.name.endswith('_Surface'):
            # Verify box topology: should have 6 faces, 8 vertices
            if len(lo.data.polygons) != 6:
                errors.append(f"{lo.name} has {len(lo.data.polygons)} faces, expected 6")
            if len(lo.data.vertices) != 8:
                errors.append(f"{lo.name} has {len(lo.data.vertices)} verts, expected 8")

    foul_objs = [o for o in static_col.objects if o.name.startswith('Foul_')]
    if len(foul_objs) != 2:
        errors.append(f"Expected 2 foul lines, got {len(foul_objs)}")

    # Check markings are within 0.002m of Z=0 surface
    for mo in foul_objs + [o for o in static_col.objects if o.name.startswith('ArrowTri_')]:
        z_max = max(v.co.z for v in mo.data.vertices)
        z_min = min(v.co.z for v in mo.data.vertices)
        if z_max > 0.002 or z_min < -0.002:
            errors.append(f"{mo.name} Z range {z_min:.4f}-{z_max:.4f} not within +-0.002 of surface")

    arrow_tris = [o for o in static_col.objects if o.name.startswith('ArrowTri_')]
    if len(arrow_tris) != 14:
        errors.append(f"Expected 14 arrow triangles, got {len(arrow_tris)}")

    dots = [o for o in static_col.objects if o.name.startswith('Dot_')]
    if len(dots) != 14:
        errors.append(f"Expected 14 dots, got {len(dots)}")

    # All objects parented to root
    for o in static_col.objects:
        if o.parent != root:
            errors.append(f"{o.name} not parented to root")

    passed = len(errors) == 0

    report = {
        "stage": "01",
        "name": "Lane pair and markings (repaired)",
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
