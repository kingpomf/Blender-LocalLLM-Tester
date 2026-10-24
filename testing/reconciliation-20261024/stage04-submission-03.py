import bpy
import json
import os
from math import pi, sin, cos
import bmesh

def run_stage():
    scene = bpy.context.scene

    required_names = ['BP01_STATIC', 'BP01_PINS', 'BP01_BALLS', 'BP01_COLLISION', 'BP01_PRESENTATION']
    for name in required_names:
        assert name in bpy.data.collections, f"Missing collection {name}"

    errors = []

    root = bpy.data.objects['BowlingPair01_ROOT']
    balls_col = bpy.data.collections['BP01_BALLS']

    ball_colors = [
        ('Ball_01', (0.10, 0.15, 0.60, 1.0)),
        ('Ball_02', (0.55, 0.15, 0.20, 1.0)),
        ('Ball_03', (0.10, 0.40, 0.38, 1.0)),
    ]

    mats = {}
    for bname, color in ball_colors:
        mat = bpy.data.materials.new(f'Mat_{bname}')
        mat.use_nodes = True
        bg = mat.node_tree.nodes['Material Output']
        p = mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
        p.inputs['Base Color'].default_value = color
        p.inputs['Roughness'].default_value = 0.15
        mat.node_tree.links.new(p.outputs['BSDF'], bg.inputs['Surface'])
        mats[bname] = mat

    ball_radius = 0.108
    hole_depth = 0.025

    def create_ball_bm(radius, hole_depth):
        me = bpy.data.meshes.new('Ball_Mesh')
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=32, radius=radius)

        hole_positions = [
            (0.02, 0.035, radius*0.93),
            (-0.03, 0.02, radius*0.93),
            (0.06, 0.015, radius*0.93),
        ]

        for hx, hy, hz in hole_positions:
            best_f = None
            best_d = 999
            for f in bm.faces:
                fc = f.calc_center_median()
                d = ((fc[0]-hx)**2 + (fc[1]-hy)**2 + (fc[2]-hz)**2)**0.5
                if d < best_d:
                    best_d = d
                    best_f = f
            if best_f and best_d < 0.08:
                bmesh.ops.extrude_face_only(bm, faces=[best_f])
                for nf in bm.faces:
                    for v in nf.verts:
                        mag = (v.co[0]**2 + v.co[1]**2 + v.co[2]**2)**0.5
                        if mag > 0:
                            v.co[0] -= v.co[0]/mag * hole_depth
                            v.co[1] -= v.co[1]/mag * hole_depth
                            v.co[2] -= v.co[2]/mag * hole_depth

        bm.to_mesh(me)
        bm.free()
        me.validate()
        me.calc_loop_triangles()
        tc = len(me.loop_triangles)
        return me, tc

    for bname, color in ball_colors:
        ball_mesh, tri_count = create_ball_bm(ball_radius, hole_depth)
        ball_mesh.materials.append(mats[bname])
        obj = bpy.data.objects.new(bname, ball_mesh)
        obj.location = (0, 0, 0)
        obj.parent = root
        balls_col.objects.link(obj)

    return_x_positions = [-0.15, 0.0, 0.15]
    for i, (bname, _) in enumerate(ball_colors):
        ball_obj = [o for o in balls_col.objects if o.name == bname][0]
        ball_obj.location = (return_x_positions[i], -2.30, ball_radius + 0.005)
        if i > 0:
            prev = [o for o in balls_col.objects if o.name == ball_colors[i-1][0]][0]
            sep = abs(ball_obj.location[0] - prev.location[0])
            if sep < 0.005:
                errors.append(f"{bname} separation too small: {sep}")

    ball_objs = [o for o in balls_col.objects if 'Ball_' in o.name]
    if len(ball_objs) != 3:
        errors.append(f"Expected 3 balls, got {len(ball_objs)}")

    eval_deps = bpy.context.evaluated_depsgraph_get()
    for obj in ball_objs:
        evaluated = obj.evaluated_get(eval_deps)
        mesh = evaluated.to_mesh()
        try:
            tc = len(mesh.loop_triangles)
            if tc > 8000:
                errors.append(f"{obj.name} exceeds 8000 triangles: {tc}")
            if mesh.vertices:
                mins = [min(v.co.x for v in mesh.vertices), min(v.co.y for v in mesh.vertices), min(v.co.z for v in mesh.vertices)]
                maxs = [max(v.co.x for v in mesh.vertices), max(v.co.y for v in mesh.vertices), max(v.co.z for v in mesh.vertices)]
                dims = [maxs[i] - mins[i] for i in range(3)]
                diam = max(dims)
                if abs(diam - 2*ball_radius) > 0.006:
                    errors.append(f"{obj.name} diameter {diam:.4f} not within {2*ball_radius:.3f}+-0.003")
        finally:
            evaluated.to_mesh_clear()

    passed = len(errors) == 0

    report = {
        "stage": "04",
        "name": "Reusable bowling balls",
        "passed": passed,
        "ball_count": len(ball_objs),
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
