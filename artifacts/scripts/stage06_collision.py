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

    if abs(root.location[0]) > 0.001 or abs(root.location[1]) > 0.001 or abs(root.location[2]) > 0.001:
        errors.append(f"Root location {root.location} != origin")
    if abs(root.rotation_euler[0]) > 0.001 or abs(root.rotation_euler[1]) > 0.001 or abs(root.rotation_euler[2]) > 0.001:
        errors.append(f"Root rotation {root.rotation_euler} != identity")
    if abs(root.scale[0]-1.0) > 0.001 or abs(root.scale[1]-1.0) > 0.001 or abs(root.scale[2]-1.0) > 0.001:
        errors.append(f"Root scale {root.scale} != (1,1,1)")

    mat_names = set(m.name for m in bpy.data.materials)
    for mname, color in [('Mat_PinWhite', (0.93, 0.91, 0.88, 1.0)), ('Mat_PinRed', (0.70, 0.10, 0.10, 1.0)), ('Mat_Gutter', (0.15, 0.15, 0.15, 1.0)), ('Mat_Ball_01', (0.10, 0.15, 0.60, 1.0)), ('Mat_Ball_02', (0.55, 0.15, 0.20, 1.0)), ('Mat_Ball_03', (0.10, 0.40, 0.38, 1.0))]:
        if mname not in mat_names:
            mat = bpy.data.materials.new(mname)
            mat.use_nodes = True
            bg = mat.node_tree.nodes['Material Output']
            p = mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
            p.inputs['Base Color'].default_value = color
            p.inputs['Roughness'].default_value = 0.35
            mat.node_tree.links.new(p.outputs['BSDF'], bg.inputs['Surface'])

    eval_deps = bpy.context.evaluated_depsgraph_get()
    total_tri = 0
    per_cat = {}
    for cn in ['BP01_STATIC', 'BP01_PINS', 'BP01_BALLS']:
        col = bpy.data.collections[cn]
        cat_tri = 0
        for obj in col.objects:
            evaluated = obj.evaluated_get(eval_deps)
            mesh = evaluated.to_mesh()
            try:
                cat_tri += len(mesh.loop_triangles)
            finally:
                evaluated.to_mesh_clear()
        per_cat[cn] = cat_tri
        total_tri += cat_tri

    if total_tri > 150000:
        errors.append(f"Visual triangles {total_tri} > 150000")

    collision_col = bpy.data.collections['BP01_COLLISION']
    for existing in collision_col.objects[:]:
        collision_col.objects.unlink(existing)
        bpy.data.objects.remove(existing)

    mat_collision = bpy.data.materials.new('Mat_Collision')
    mat_collision.use_nodes = True
    bg = mat_collision.node_tree.nodes['Material Output']
    p = mat_collision.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value = (0.8, 0.1, 0.1, 1.0)
    p.inputs['Roughness'].default_value = 0.8
    mat_collision.node_tree.links.new(p.outputs['BSDF'], bg.inputs['Surface'])

    def make_proxy(name, verts, faces, parent=None):
        me = bpy.data.meshes.new(name + '_Mesh')
        me.from_pydata(verts, [], faces)
        me.validate()
        me.materials.append(mat_collision)
        obj = bpy.data.objects.new(name, me)
        obj.parent = parent
        collision_col.objects.link(obj)
        return obj

    for lx in [-0.95, 0.95]:
        lane_verts = [
            (lx-0.60, 0.0, 0.001), (lx+0.60, 0.0, 0.001),
            (lx+0.60, 19.20, 0.001), (lx-0.60, 19.20, 0.001),
            (lx-0.60, 0.0, -0.01), (lx+0.60, 0.0, -0.01),
            (lx+0.60, 19.20, -0.01), (lx-0.60, 19.20, -0.01),
        ]
        lane_faces = [(0,1,2,3), (4,5,6,7), (0,4,5,1), (3,2,1,0), (4,0,3,7), (5,4,7,6)]
        make_proxy(f'COL_LaneBed_L' if lx < 0 else 'COL_LaneBed_R', lane_verts, lane_faces, root)

    gutter_proxies = [
        ('COL_Gutter_L_Outer', (-1.4834, 0.0, 0.0), (-1.7334, 19.20, -0.08)),
        ('COL_Gutter_L_Inner', (-0.4166, 0.0, 0.0), (-0.6666, 19.20, -0.08)),
        ('COL_Gutter_R_Inner', (0.4166, 0.0, 0.0), (0.6666, 19.20, -0.08)),
        ('COL_Gutter_R_Outer', (1.4834, 0.0, 0.0), (1.7334, 19.20, -0.08)),
    ]
    for pname, (x1, y1, z1), (x2, y2, z2) in gutter_proxies:
        hw = abs(x2-x1)/2
        cx = (x1+x2)/2
        dv = [(cx-hw, y1, z1), (cx+hw, y1, z1), (cx+hw, y2, z1), (cx-hw, y2, z1),
              (cx-hw, y1, z1-0.03), (cx+hw, y1, z1-0.03), (cx+hw, y2, z1-0.03), (cx-hw, y2, z1-0.03)]
        df = [(0,1,2,3), (4,5,6,7), (0,4,5,1), (3,2,1,0), (4,0,3,7), (5,4,7,6)]
        make_proxy(pname, dv, df, root)

    for rx in [-1.7434, 1.7434]:
        rail_verts = [
            (rx-0.025, -0.5, 0.0), (rx+0.025, -0.5, 0.0),
            (rx+0.025, -0.5, -0.08), (rx-0.025, -0.5, -0.08),
            (rx-0.025, 19.20, 0.0), (rx+0.025, 19.20, 0.0),
            (rx+0.025, 19.20, -0.08), (rx-0.025, 19.20, -0.08),
        ]
        rail_faces = [(0,1,2,3), (4,5,6,7), (0,4,5,1), (3,2,1,0), (4,0,3,7), (5,4,7,6)]
        make_proxy(f'COL_Rail_L' if rx < 0 else 'COL_Rail_R', rail_verts, rail_faces, root)

    stop_verts = [
        (-1.80, 19.20, 0.0), (1.80, 19.20, 0.0),
        (1.80, 19.20, -0.30), (-1.80, 19.20, -0.30),
        (-1.80, 19.60, 0.0), (1.80, 19.60, 0.0),
        (1.80, 19.60, -0.30), (-1.80, 19.60, -0.30),
    ]
    stop_faces = [(0,1,2,3), (4,5,6,7), (0,4,5,1), (3,2,1,0), (4,0,3,7), (5,4,7,6)]
    make_proxy('COL_RearStop', stop_verts, stop_faces, root)

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

    pin_objs = [o for o in bpy.data.collections['BP01_PINS'].objects]
    ball_objs = [o for o in bpy.data.collections['BP01_BALLS'].objects]
    if len(pin_objs) != 20:
        errors.append(f"Pin count {len(pin_objs)} != 20")
    if len(ball_objs) != 3:
        errors.append(f"Ball count {len(ball_objs)} != 3")

    passed = len(errors) == 0

    report = {
        "stage": "06",
        "name": "Materials, hierarchy and collision",
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
