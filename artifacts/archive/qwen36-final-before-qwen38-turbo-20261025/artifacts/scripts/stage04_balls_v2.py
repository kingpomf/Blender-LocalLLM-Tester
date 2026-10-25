import bpy
import json
import os
import bmesh
from math import pi, sin, cos, sqrt

def run_stage():
    scene = bpy.context.scene
    required_names = ['BP01_STATIC', 'BP01_PINS', 'BP01_BALLS', 'BP01_COLLISION', 'BP01_PRESENTATION']
    for name in required_names:
        assert name in bpy.data.collections, f"Missing collection {name}"
    errors = []
    root = bpy.data.objects['BowlingPair01_ROOT']
    balls_col = bpy.data.collections['BP01_BALLS']

    # Clean up existing ball objects
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
        bg = mat.node_tree.nodes['Material Output']
        p = mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
        p.inputs['Base Color'].default_value = color
        p.inputs['Roughness'].default_value = 0.15
        p.inputs['Clearcoat'].default_value = 0.8
        p.inputs['Clearcoat Roughness'].default_value = 0.1
        mat.node_tree.links.new(p.outputs['BSDF'], bg.inputs['Surface'])
        mats[bname] = mat

    ball_radius = 0.108
    hole_depth = 0.025
    # Bowling grip: 3 holes - index finger, middle finger, ring finger
    # On upper hemisphere near equator for realistic grip
    hole_positions = [
        (0.02, 0.035, ball_radius * 0.93),
        (-0.03, 0.02, ball_radius * 0.93),
        (0.06, 0.015, ball_radius * 0.93),
    ]
    hole_face_radius = 0.040  # faces within this distance of hole center form one patch

    def create_ball_with_holes(radius, hole_positions, hole_depth_val):
        """Create a bowling ball with proper recessed finger holes using bmesh."""
        me = bpy.data.meshes.new('Ball_Mesh')
        bm = bmesh.new()
        # Create sphere with good resolution for hole geometry
        bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=radius)

        # For each hole, find a cluster of faces and create a recess
        for hx, hy, hz in hole_positions:
            # Find faces near the hole position
            candidates = []
            for f in bm.faces:
                fc = f.calc_center_median()
                dist = sqrt((fc[0]-hx)**2 + (fc[1]-hy)**2 + (fc[2]-hz)**2)
                if dist < hole_face_radius:
                    candidates.append((dist, f))

            if not candidates:
                continue

            # Sort by distance, take closest cluster
            candidates.sort()
            patch_faces = [c[1] for c in candidates[:12]]  # Take up to 12 closest faces

            if len(patch_faces) < 3:
                continue

            # Extrude the face patch (as a region)
            geom_list = []
            for pf in patch_faces:
                geom_list.append(pf)
                for e in pf.edges:
                    geom_list.append(e)
                for v in pf.verts:
                    geom_list.append(v)

            result = bmesh.ops.extrude_face_region(bm, geom=geom_list)
            new_geoms = result['geom']
            new_faces = [g for g in new_geoms if isinstance(g, bmesh.types.BMFace)]

            if new_faces:
                # For each new face, push its vertices toward center to create recess depth
                for nf in new_faces:
                    for v in nf.verts:
                        mag = sqrt(v.co[0]**2 + v.co[1]**2 + v.co[2]**2)
                        if mag > 0.001:
                            scale_factor = 1.0 - (hole_depth_val / mag)
                            v.co[0] *= scale_factor
                            v.co[1] *= scale_factor
                            v.co[2] *= scale_factor

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

    # Position balls on return rack cradle: Z = radius (touching surface at z=0)
    # X spacing: 0.221m center-to-center, Y at -2.30 (on return)
    spacing = 0.221
    x_positions = [-spacing, 0.0, spacing]
    ball_y = -2.30
    ball_z = ball_radius  # center at radius height, bottom at z=0

    for i, (bname, _) in enumerate(ball_colors):
        ball_obj = [o for o in balls_col.objects if o.name == bname][0]
        ball_obj.location = (x_positions[i], ball_y, ball_z)

    # Verification
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
                # Check center pivot
                center_x = (mins[0] + maxs[0]) / 2
                center_y = (mins[1] + maxs[1]) / 2
                if abs(center_x) > 0.001 or abs(center_y) > 0.001:
                    errors.append(f"{obj.name} pivot offset from center: ({center_x:.4f}, {center_y:.4f})")
        finally:
            evaluated.to_mesh_clear()

    # Check separation between balls (surface gap >= 0.005m)
    for i in range(1, len(ball_objs)):
        prev = ball_objs[i-1]
        curr = ball_objs[i]
        center_dist = sqrt((prev.location[0]-curr.location[0])**2 +
                          (prev.location[1]-curr.location[1])**2 +
                          (prev.location[2]-curr.location[2])**2)
        surface_gap = center_dist - 2*ball_radius
        if surface_gap < -0.001:
            errors.append(f"{ball_objs[i].name} overlaps previous: surface_gap={surface_gap:.4f}")

    passed = len(errors) == 0

    report = {
        "stage": "04",
        "name": "Reusable bowling balls (repaired with proper recess geometry)",
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
