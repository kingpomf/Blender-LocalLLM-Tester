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

    # Check root
    if abs(root.location[0]) > 0.001 or abs(root.location[1]) > 0.001 or abs(root.location[2]) > 0.001:
        errors.append(f"Root location {root.location} != origin")
    if abs(root.rotation_euler[0]) > 0.001 or abs(root.rotation_euler[1]) > 0.001 or abs(root.rotation_euler[2]) > 0.001:
        errors.append(f"Root rotation != identity")
    if abs(root.scale[0]-1.0) > 0.001 or abs(root.scale[1]-1.0) > 0.001 or abs(root.scale[2]-1.0) > 0.001:
        errors.append(f"Root scale != (1,1,1)")

    # Ensure required materials exist
    mat_names = set(m.name for m in bpy.data.materials)
    for mname, color in [('Mat_PinWhite', (0.93, 0.91, 0.88, 1.0)), ('Mat_PinRed', (0.70, 0.10, 0.10, 1.0)), ('Mat_Gutter', (0.15, 0.15, 0.15, 1.0)), ('Mat_Ball_01', (0.10, 0.15, 0.60, 1.0)), ('Mat_Ball_02', (0.55, 0.15, 0.20, 1.0)), ('Mat_Ball_03', (0.10, 0.40, 0.38, 1.0))]:
        if mname not in mat_names:
            mat = bpy.data.materials.new(mname)
            mat.use_nodes = True
            tree = mat.node_tree
            for n in list(tree.nodes):
                tree.nodes.remove(n)
            p = tree.nodes.new('ShaderNodeBsdfPrincipled')
            p.inputs['Base Color'].default_value = color
            p.inputs['Roughness'].default_value = 0.35
            out = tree.nodes.new('ShaderNodeOutputMaterial')
            tree.links.new(p.outputs['BSDF'], out.inputs['Surface'])

    # Count visual triangles
    eval_deps = bpy.context.evaluated_depsgraph_get()
    total_tri = 0
    visual = []
    for cn in ['BP01_STATIC', 'BP01_PINS', 'BP01_BALLS']:
        col = bpy.data.collections[cn]
        for obj in col.objects:
            visual.append(obj)
            evaluated = obj.evaluated_get(eval_deps)
            mesh = evaluated.to_mesh()
            try:
                total_tri += len(mesh.loop_triangles)
            finally:
                evaluated.to_mesh_clear()

    if total_tri > 150000:
        errors.append(f"Visual triangles {total_tri} > 150000")

    # Fix collision objects: ensure hide_render=true and proper alignment
    collision_col = bpy.data.collections['BP01_COLLISION']
    mat_collision = bpy.data.materials.new('Mat_Collision') if 'Mat_Collision' not in bpy.data.materials else bpy.data.materials['Mat_Collision']
    if not mat_collision.use_nodes:
        mat_collision.use_nodes = True
        tree = mat_collision.node_tree
        for n in list(tree.nodes):
            tree.nodes.remove(n)
        p = tree.nodes.new('ShaderNodeBsdfPrincipled')
        p.inputs['Base Color'].default_value = (0.8, 0.1, 0.1, 1.0)
        p.inputs['Roughness'].default_value = 0.8
        out = tree.nodes.new('ShaderNodeOutputMaterial')
        tree.links.new(p.outputs['BSDF'], out.inputs['Surface'])

    # Set hide_render on all existing collision objects
    for obj in collision_col.objects:
        obj.hide_render = True

    # Create collision proxies with correct positions matching visual gutters
    # First, clear and recreate
    for existing in list(collision_col.objects):
        collision_col.objects.unlink(existing)
        bpy.data.objects.remove(existing)

    def make_proxy(name, verts, faces, parent=None):
        me = bpy.data.meshes.new(name + '_Mesh')
        me.from_pydata(verts, [], faces)
        me.validate()
        me.materials.append(mat_collision)
        obj = bpy.data.objects.new(name, me)
        obj.parent = parent
        obj.hide_render = True  # EXCLUDE from beauty renders
        collision_col.objects.link(obj)
        return obj

    # Lane beds (matching lane surfaces)
    for lx in [-0.95, 0.95]:
        lane_verts = [
            (lx-0.60, 0.0, 0.001), (lx+0.60, 0.0, 0.001),
            (lx+0.60, 19.20, 0.001), (lx-0.60, 19.20, 0.001),
            (lx-0.60, 0.0, -0.01), (lx+0.60, 0.0, -0.01),
            (lx+0.60, 19.20, -0.01), (lx-0.60, 19.20, -0.01),
        ]
        lane_faces = [(0,1,2,3), (4,5,6,7), (0,4,5,1), (3,2,1,0), (4,0,3,7), (5,4,7,6)]
        make_proxy('COL_LaneBed_L' if lx < 0 else 'COL_LaneBed_R', lane_verts, lane_faces, root)

    # Gutter troughs - align precisely with visual gutter bounds
    # Visual gutters: L_Outer [-1.7334, -1.4834], L_Inner [-0.6666, -0.4166], R_Inner [0.4166, 0.6666], R_Outer [1.4834, 1.7334]
    gutter_bounds = [
        ('COL_Gutter_L_Outer', (-1.7334, 0.0, -0.08), (-1.4834, 19.20, 0.0)),
        ('COL_Gutter_L_Inner', (-0.6666, 0.0, -0.08), (-0.4166, 19.20, 0.0)),
        ('COL_Gutter_R_Inner', (0.4166, 0.0, -0.08), (0.6666, 19.20, 0.0)),
        ('COL_Gutter_R_Outer', (1.4834, 0.0, -0.08), (1.7334, 19.20, 0.0)),
    ]
    for pname, (x1, y1, z1), (x2, y2, z2) in gutter_bounds:
        cx = (x1 + x2) / 2
        hw = abs(x2 - x1) / 2
        dv = [
            (cx-hw, y1, z1), (cx+hw, y1, z1),
            (cx+hw, y2, z1), (cx-hw, y2, z1),
            (cx-hw, y1, z1-0.03), (cx+hw, y1, z1-0.03),
            (cx+hw, y2, z1-0.03), (cx-hw, y2, z1-0.03),
        ]
        df = [(0,1,2,3), (4,5,6,7), (0,4,5,1), (3,2,1,0), (4,0,3,7), (5,4,7,6)]
        make_proxy(pname, dv, df, root)

    # Outer rails
    for rx in [-1.7434, 1.7434]:
        rail_verts = [
            (rx-0.025, -0.5, 0.0), (rx+0.025, -0.5, 0.0),
            (rx+0.025, -0.5, -0.08), (rx-0.025, -0.5, -0.08),
            (rx-0.025, 19.20, 0.0), (rx+0.025, 19.20, 0.0),
            (rx+0.025, 19.20, -0.08), (rx-0.025, 19.20, -0.08),
        ]
        rail_faces = [(0,1,2,3), (4,5,6,7), (0,4,5,1), (3,2,1,0), (4,0,3,7), (5,4,7,6)]
        make_proxy('COL_Rail_L' if rx < 0 else 'COL_Rail_R', rail_verts, rail_faces, root)

    # Rear stop
    stop_verts = [
        (-1.80, 19.20, 0.0), (1.80, 19.20, 0.0),
        (1.80, 19.20, -0.30), (-1.80, 19.20, -0.30),
        (-1.80, 19.60, 0.0), (1.80, 19.60, 0.0),
        (1.80, 19.60, -0.30), (-1.80, 19.60, -0.30),
    ]
    stop_faces = [(0,1,2,3), (4,5,6,7), (0,4,5,1), (3,2,1,0), (4,0,3,7), (5,4,7,6)]
    make_proxy('COL_RearStop', stop_verts, stop_faces, root)

    # Count collision triangles
    collision_tri = 0
    for obj in collision_col.objects:
        evaluated = obj.evaluated_get(eval_deps)
        mesh = evaluated.to_mesh()
        try:
            collision_tri += len(mesh.loop_triangles)
        finally:
            evaluated.to_mesh_clear()

    if collision_tri > 10000:
        errors.append(f"Collision triangles {collision_tri} > 10000")

    # Verify pin and ball counts
    pin_objs = [o for o in bpy.data.collections['BP01_PINS'].objects]
    ball_objs = [o for o in bpy.data.collections['BP01_BALLS'].objects]
    if len(pin_objs) != 20:
        errors.append(f"Pin count {len(pin_objs)} != 20")
    if len(ball_objs) != 3:
        errors.append(f"Ball count {len(ball_objs)} != 3")

    # Verify collision exclusion
    for obj in collision_col.objects:
        if not obj.hide_render:
            errors.append(f"{obj.name} not hidden from render")

    passed = len(errors) == 0

    report = {
        "stage": "06",
        "name": "Materials, hierarchy and collision (exclusion fixed)",
        "passed": passed,
        "visual_triangles": total_tri,
        "collision_triangles": collision_tri,
        "pin_count": len(pin_objs),
        "ball_count": len(ball_objs),
        "proxy_count": len(collision_col.objects),
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
