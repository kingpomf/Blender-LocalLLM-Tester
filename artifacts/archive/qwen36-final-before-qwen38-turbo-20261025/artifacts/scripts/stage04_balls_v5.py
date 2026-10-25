import bpy
import json
import os
import bmesh
from math import sqrt, radians

def run_stage():
    scene = bpy.context.scene
    required_names = ['BP01_STATIC', 'BP01_PINS', 'BP01_BALLS', 'BP01_COLLISION', 'BP01_PRESENTATION']
    for name in required_names:
        assert name in bpy.data.collections, f"Missing collection {name}"
    errors = []
    root = bpy.data.objects['BowlingPair01_ROOT']
    balls_col = bpy.data.collections['BP01_BALLS']

    # Clean up existing ball/static objects
    for existing in list(balls_col.objects):
        if 'Ball_' in existing.name:
            balls_col.objects.unlink(existing)
            bpy.data.objects.remove(existing)

    ball_colors = [
        ('Ball_01', (0.10, 0.15, 0.60, 1.0)),
        ('Ball_02', (0.55, 0.15, 0.20, 1.0)),
        ('Ball_03', (0.10, 0.40, 0.38, 1.0)),
    ]

    mats = {}
    for bname, color in ball_colors:
        mat = bpy.data.materials.new(f'Mat_{bname}')
        mat.use_nodes = True
        tree = mat.node_tree
        for n in list(tree.nodes):
            tree.nodes.remove(n)
        p = tree.nodes.new('ShaderNodeBsdfPrincipled')
        p.inputs['Base Color'].default_value = color
        p.inputs['Roughness'].default_value = 0.15
        out = tree.nodes.new('ShaderNodeOutputMaterial')
        tree.links.new(p.outputs['BSDF'], out.inputs['Surface'])
        mats[bname] = mat

    ball_radius = 0.108
    hole_depth = 0.025
    hole_positions = [
        (0.02, 0.035, ball_radius * 0.93),
        (-0.03, 0.02, ball_radius * 0.93),
        (0.06, 0.015, ball_radius * 0.93),
    ]
    hole_radius = 0.018  # distance from hole center to pull vertices

    def create_ball_with_holes(radius, hole_positions, hole_depth_val):
        me = bpy.data.meshes.new('Ball_Mesh')
        bm = bmesh.new()
        # Create UV sphere with good resolution
        bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=radius)

        for hx, hy, hz in hole_positions:
            # Find vertices near the hole position
            for v in bm.verts:
                dist = sqrt((v.co[0]-hx)**2 + (v.co[1]-hy)**2 + (v.co[2]-hz)**2)
                if dist < hole_radius:
                    # Pull vertex inward along sphere normal
                    mag = sqrt(v.co[0]**2 + v.co[1]**2 + v.co[2]**2)
                    if mag > 0.001:
                        sf = 1.0 - (hole_depth_val / mag)
                        v.co[0] *= sf
                        v.co[1] *= sf
                        v.co[2] *= sf

        bm.to_mesh(me)
        bm.free()
        me.validate()
        me.calc_loop_triangles()
        return me

    for bname, color in ball_colors:
        ball_mesh = create_ball_with_holes(ball_radius, hole_positions, hole_depth)
        ball_mesh.materials.append(mats[bname])
        obj = bpy.data.objects.new(bname, ball_mesh)
        obj.location = (0, 0, 0)
        obj.parent = root
        balls_col.objects.link(obj)

    # Position balls on return rack: Z = radius (touching surface)
    spacing = 0.221
    ball_y = -2.30
    ball_z = ball_radius

    for i, (bname, _) in enumerate(ball_colors):
        ball_obj = [o for o in balls_col.objects if o.name == bname][0]
        ball_obj.location = (spacing * (-1 + 2*i), ball_y, ball_z)

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
                if abs(diam - 2*ball_radius) > 0.003:
                    errors.append(f"{obj.name} diameter {diam:.4f} not within {2*ball_radius:.3f}+-0.003")
                center_x = (mins[0] + maxs[0]) / 2
                center_y = (mins[1] + maxs[1]) / 2
                if abs(center_x) > 0.001 or abs(center_y) > 0.001:
                    errors.append(f"{obj.name} pivot offset: ({center_x:.4f}, {center_y:.4f})")
        finally:
            evaluated.to_mesh_clear()

    for i in range(1, len(ball_objs)):
        prev = ball_objs[i-1]
        curr = ball_objs[i]
        center_dist = sqrt((prev.location[0]-curr.location[0])**2 +
                          (prev.location[1]-curr.location[1])**2 +
                          (prev.location[2]-curr.location[2])**2)
        surface_gap = center_dist - 2*ball_radius
        if surface_gap < -0.001:
            errors.append(f"{ball_objs[i].name} overlaps: gap={surface_gap:.4f}")

    passed = len(errors) == 0

    report = {
        "stage": "04",
        "name": "Reusable bowling balls (v5 - vertex pull holes)",
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
        for cn in required_names:
            col = bpy.data.collections[cn]
            for o in col.objects:
                obj_list.append({'name': o.name, 'type': o.type,
                    'location': [round(x,6) for x in o.location],
                    'parent': o.parent.name if o.parent else None, 'collection': cn})
        json.dump({'objects': obj_list, 'collections': [c.name for c in bpy.data.collections]}, f, indent=2)

    return report

report = run_stage()
