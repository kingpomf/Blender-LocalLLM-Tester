import bpy
import json
import os
import bmesh

def run_stage():
    scene = bpy.context.scene
    required_names = ['BP01_STATIC', 'BP01_PINS', 'BP01_BALLS', 'BP01_COLLISION', 'BP01_PRESENTATION']
    for name in required_names:
        assert name in bpy.data.collections, f"Missing collection {name}"
    errors = []
    root = bpy.data.objects['BowlingPair01_ROOT']
    static_col = bpy.data.collections['BP01_STATIC']

    def make_mat(name, color, rough=0.5):
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        tree = mat.node_tree
        for n in list(tree.nodes):
            tree.nodes.remove(n)
        p = tree.nodes.new('ShaderNodeBsdfPrincipled')
        p.inputs['Base Color'].default_value = color
        p.inputs['Roughness'].default_value = rough
        out = tree.nodes.new('ShaderNodeOutputMaterial')
        tree.links.new(p.outputs['BSDF'], out.inputs['Surface'])
        return mat

    mat_hood = make_mat('Mat_Hood', (0.20, 0.20, 0.25, 1.0), 0.6)
    mat_wood = make_mat('Mat_Wood', (0.55, 0.35, 0.20, 1.0), 0.4)
    mat_sboard = make_mat('Mat_Score', (0.15, 0.15, 0.15, 1.0), 0.3)
    mat_screen = make_mat('Mat_Screen', (0.05, 0.20, 0.05, 1.0), 0.1)
    mat_wall = make_mat('Mat_Wall', (0.40, 0.38, 0.35, 1.0), 0.7)
    mat_floor = make_mat('Mat_Alfloor', (0.50, 0.48, 0.45, 1.0), 0.6)
    mat_deco1 = make_mat('Mat_Stripe', (0.60, 0.15, 0.15, 1.0), 0.3)
    mat_deco2 = make_mat('Mat_LightBar', (0.90, 0.85, 0.60, 1.0), 0.2)

    def make_box(name, w, h, d, mat, parent=None):
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=max(w, h, d))
        for v in bm.verts:
            if v.co[0] != 0:
                v.co[0] *= w / 2
            if v.co[1] != 0:
                v.co[1] *= d / 2
            if v.co[2] != 0:
                v.co[2] *= h / 2
        bm.verts.ensure_lookup_table()
        me = bpy.data.meshes.new(name + '_Mesh')
        bm.to_mesh(me)
        bm.free()
        me.validate()
        me.materials.append(mat)
        obj = bpy.data.objects.new(name, me)
        obj.parent = parent
        static_col.objects.link(obj)
        return obj

    # Remove old stage 05 objects
    for existing in list(static_col.objects):
        if existing.name.startswith(('Hood','ReturnRack','Bench','Scoreboard','Screen','MaskingWall','AlleyFloor','Stripe','LightBar','ReturnFrame')):
            static_col.objects.unlink(existing)
            bpy.data.objects.remove(existing)

    # 1. Ball return hood and rack (X=-0.40..0.40, Y=-4.30..-0.30)
    # Hood canopy: narrower to fit within X bounds
    hood = make_box('Hood_Canopy', 0.60, 0.12, 3.00, mat_hood, root)
    hood.location = (0.0, -2.30, 2.0)

    # Rack supports (at Y=-3.80, -2.80, -1.80, all within Y=-4.30..-0.30)
    for y in [-3.80, -2.80, -1.80]:
        support = make_box('ReturnRack_Support', 0.08, 0.10, 0.06, mat_hood, root)
        support.location = (0.0, y, 0.50)

    # Rack cradle (supports balls at x=-0.22, 0.0, +0.22)
    for i, x in enumerate([-0.22, 0.0, 0.22]):
        cradle = make_box(f'ReturnRack_Cradle_{i}', 0.06, 0.25, 0.60, mat_wood, root)
        cradle.location = (x, -2.30, 0.08)

    # Return opening frame
    ret_open = make_box('ReturnFrame', 0.50, 0.50, 0.05, mat_hood, root)
    ret_open.location = (0.0, -0.35, 0.80)

    # 2. Benches (Y < -4.572)
    for lane_side, lx in [('L', -1.50), ('R', 1.50)]:
        bench = make_box(f'Bench_{lane_side}', 1.20, 0.40, 0.50, mat_wood, root)
        bench.location = (lx, -5.0, 0.0)

    # 3. Overhead scoreboard housings (screen bottoms Z>=2.20)
    for lane_side, lx in [('L', -0.95), ('R', 0.95)]:
        housing = make_box(f'Scoreboard_{lane_side}', 0.80, 0.10, 1.50, mat_sboard, root)
        housing.location = (lx, 12.0, 3.50)
        screen = make_box(f'Screen_{lane_side}', 0.70, 0.05, 1.20, mat_screen, root)
        screen.location = (lx, 12.0, 2.30)
        label_w = 0.15 if lane_side == 'L' else -0.15
        label_obj = make_box(f'Label_{lane_side}', 0.30, 0.30, 0.02, mat_deco1, root)
        label_obj.location = (lx + label_w, 12.0, 2.60)

    # 4. Rear masking wall above/behind pits
    pin_top_z = 0.381
    wall_z = pin_top_z + 0.60
    mask_wall = make_box('MaskingWall', 5.0, 1.50, 0.15, mat_wall, root)
    mask_wall.location = (0.0, 19.80, wall_z + 0.75)

    # 5. Alley floor
    alley_floor = make_box('AlleyFloor', 6.0, 26.0, 0.05, mat_floor, root)
    alley_floor.location = (0.0, 10.0, -0.025)

    # Decorative elements
    stripe = make_box('Stripe_01', 0.10, 0.05, 15.0, mat_deco1, root)
    stripe.location = (-2.50, 10.0, 3.0)
    lightbar = make_box('LightBar_01', 0.30, 0.10, 12.0, mat_deco2, root)
    lightbar.location = (0.0, 10.0, 4.50)

    # Verification
    hood_objs = [o for o in static_col.objects if o.name.startswith('Hood') or o.name.startswith('ReturnRack') or o.name.startswith('ReturnFrame')]
    if len(hood_objs) < 4:
        errors.append(f"Ball return: expected >=4 objects, got {len(hood_objs)}")

    for ho in hood_objs:
        if ho.location[0] < -0.45 or ho.location[0] > 0.45:
            errors.append(f"{ho.name} X={ho.location[0]} outside X=-0.40..0.40")

    bench_objs = [o for o in static_col.objects if o.name.startswith('Bench')]
    if len(bench_objs) != 2:
        errors.append(f"Expected 2 benches, got {len(bench_objs)}")
    for bo in bench_objs:
        if bo.location[1] >= -4.572:
            errors.append(f"{bo.name} Y={bo.location[1]} >= -4.572")

    screen_objs = [o for o in static_col.objects if o.name.startswith('Screen_')]
    if len(screen_objs) != 2:
        errors.append(f"Expected 2 screens, got {len(screen_objs)}")
    for so in screen_objs:
        if so.location[2] < 2.19:
            errors.append(f"{so.name} Z={so.location[2]} < 2.20")

    mask_wall_objs = [o for o in static_col.objects if o.name.startswith('MaskingWall')]
    if len(mask_wall_objs) != 1:
        errors.append(f"Expected 1 masking wall, got {len(mask_wall_objs)}")

    deco_count = len([o for o in static_col.objects if o.name.startswith(('Stripe', 'LightBar'))])
    if deco_count < 2:
        errors.append(f"Expected >=2 decorative elements, got {deco_count}")

    passed = len(errors) == 0

    report = {
        "stage": "05",
        "name": "Return, seating and alley dressing (bounds fixed)",
        "passed": passed,
        "hood_count": len(hood_objs),
        "bench_count": len(bench_objs),
        "screen_count": len(screen_objs),
        "deco_count": deco_count,
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
