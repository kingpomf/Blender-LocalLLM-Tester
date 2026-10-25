import bpy
import json
import os
from mathutils import Vector

def reshape_mesh(obj, hw, hy, hz):
    me = obj.data
    for v in me.vertices:
        sx = 1.0 if v.co.x > 0 else -1.0 if v.co.x < 0 else 0.0
        sy = 1.0 if v.co.y > 0 else -1.0 if v.co.y < 0 else 0.0
        sz = 1.0 if v.co.z > 0 else -1.0 if v.co.z < 0 else 0.0
        v.co.x = hw * sx
        v.co.y = hy * sy
        v.co.z = hz * sz
    me.validate()
    obj.dimensions = (hw * 2, hy * 2, hz * 2)

def run_stage():
    scene = bpy.context.scene
    required_names = ['BP01_STATIC', 'BP01_PINS', 'BP01_BALLS', 'BP01_COLLISION', 'BP01_PRESENTATION']
    for name in required_names:
        assert name in bpy.data.collections, f"Missing collection {name}"
    errors = []
    root = bpy.data.objects['BowlingPair01_ROOT']
    static_col = bpy.data.collections['BP01_STATIC']
    balls_col = bpy.data.collections['BP01_BALLS']
    pres_col = bpy.data.collections['BP01_PRESENTATION']

    # FIX 1: Ball positions
    ball_positions = [
        ('Ball_01', -0.221, -2.30, 0.188),
        ('Ball_02', 0.221, -2.30, 0.188),
        ('Ball_03', 0.0, -2.30, 0.188),
    ]
    for bname, bx, by, bz in ball_positions:
        obj = balls_col.objects.get(bname)
        if obj:
            obj.location[0] = bx
            obj.location[1] = by
            obj.location[2] = bz
        else:
            errors.append(f"Ball {bname} not found in BP01_BALLS")

    # FIX 2: Hood_Canopy - shrink width
    hood = static_col.objects.get('Hood_Canopy')
    if hood:
        reshape_mesh(hood, 0.38, 1.80, 0.06)
        hood.location[0] = 0.0
        hood.location[1] = -2.29
        hood.location[2] = 2.0
    else:
        errors.append("Hood_Canopy not found")

    # FIX 3: AlleyFloor - move below z=0
    af = static_col.objects.get('AlleyFloor')
    if af:
        af.location[2] = -0.325
    else:
        errors.append("AlleyFloor not found")

    # FIX 4: MaskingWall
    mw = static_col.objects.get('MaskingWall')
    if mw:
        mw.location[1] = 20.0
        mw.location[2] = 3.125
    else:
        errors.append("MaskingWall not found")

    # FIX 5: ReturnRack_Supports
    for idx in range(3):
        sname = 'ReturnRack_Support' if idx == 0 else 'ReturnRack_Support.%03d' % idx
        sup = static_col.objects.get(sname)
        if sup:
            reshape_mesh(sup, 0.04, 0.15, 0.50)
        else:
            errors.append(f"{sname} not found")

    # FIX 6: Cameras
    old_cams = []
    for existing in pres_col.objects:
        if existing.name.startswith('CAM_BowlingPair01_'):
            old_cams.append(existing.name)
    for cam_name in old_cams:
        obj = pres_col.objects.get(cam_name)
        if obj:
            for c in obj.users_collection[:]:
                c.objects.unlink(obj)
            if obj.type == 'CAMERA' and obj.data:
                if obj.data.users == 0:
                    bpy.data.cameras.remove(obj.data)
            if obj.users == 0:
                bpy.data.objects.remove(obj)

    camera_configs = [
        ('CAM_BowlingPair01_Overview',
         (-4.0, -9.0, 5.0),
         (0, 10, 1.0)),
        ('CAM_BowlingPair01_Player',
         (-1.5, -3.0, 1.8),
         (-0.95, 18.0, 0.5)),
        ('CAM_BowlingPair01_PinDeck',
         (0, 16.5, 3.0),
         (0, 18.8, 0.3)),
        ('CAM_BowlingPair01_Props',
         (1.5, -1.5, 1.2),
         (0, -2.3, 0.15)),
    ]

    for cam_name, loc, target in camera_configs:
        cam_data = bpy.data.cameras.new(cam_name + '_data')
        cam_data.angle = 0.85
        cam_data.lens_unit = 'FOV'
        cam_obj = bpy.data.objects.new(cam_name, cam_data)
        cam_obj.location[0] = loc[0]
        cam_obj.location[1] = loc[1]
        cam_obj.location[2] = loc[2]
        cam_obj.parent = root
        dir_vec = Vector((target[0]-loc[0], target[1]-loc[1], target[2]-loc[2])).normalized()
        rot_quat = dir_vec.to_track_quat('-Z', 'Y')
        cam_obj.rotation_euler = rot_quat.to_euler()
        pres_col.objects.link(cam_obj)

    # Verification
    for bname, bx, by, bz in ball_positions:
        obj = balls_col.objects.get(bname)
        if obj:
            if abs(obj.location[0] - bx) > 0.01:
                errors.append(f"{bname} x = {obj.location[0]:.3f}, expected {bx}")
            if abs(obj.location[2] - bz) > 0.01:
                errors.append(f"{bname} z = {obj.location[2]:.3f}, expected {bz}")

    if hood:
        bbox_max_x = hood.location[0] + hood.dimensions[0] / 2
        if bbox_max_x > 0.41 or -bbox_max_x > 0.41:
            errors.append(f"Hood x={bbox_max_x:.3f} outside bounds")

    if af:
        z_max = af.location[2] + af.dimensions[2] / 2
        if z_max > 0.0:
            errors.append(f"AlleyFloor max z = {z_max:.3f} >= 0")

    expected_cams = ['CAM_BowlingPair01_Overview', 'CAM_BowlingPair01_Player',
                     'CAM_BowlingPair01_PinDeck', 'CAM_BowlingPair01_Props']
    present_cams = [o.name for o in pres_col.objects if o.name.startswith('CAM_')]
    for cname in expected_cams:
        if cname not in present_cams:
            errors.append(f"Camera {cname} not created")

    passed = len(errors) == 0

    report = {
        "stage": "04-07 fix",
        "name": "Geometry corrections: balls, dressing, cameras",
        "passed": passed,
        "errors": errors,
    }

    out_dir = '/job'
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, 'report.json'), 'w') as f:
        json.dump(report, f, indent=2)

    return report

report = run_stage()
