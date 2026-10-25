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

def make_concave_gutter(name, x1, x2, parent, col):
    profile = [
        (x1, 0.001),
        (x1 + (x2-x1)*0.05, -0.02),
        (x1 + (x2-x1)*0.20, -0.06),
        ((x1+x2)/2, -0.10),
        (x1 + (x2-x1)*0.80, -0.06),
        (x1 + (x2-x1)*0.95, -0.02),
        (x2, 0.001),
    ]
    y_start, y_end = 0.0, 19.20
    y_segs = 30
    dy = (y_end - y_start) / y_segs
    verts = []
    faces = []
    for s in range(y_segs + 1):
        y = y_start + s * dy
        for px, pz in profile:
            verts.append((px, y, pz))
    nv = len(profile)
    for s in range(y_segs):
        for vi in range(nv - 1):
            a = s * nv + vi
            b = a + 1
            c = (s + 1) * nv + vi + 1
            d = (s + 1) * nv + vi
            faces.append((a, b, c, d))
    me = bpy.data.meshes.new(name + '_Mesh')
    me.from_pydata(verts, [], faces)
    me.validate()
    obj = bpy.data.objects.new(name, me)
    obj.parent = parent
    col.objects.link(obj)
    return obj

def run_stage():
    scene = bpy.context.scene
    required_names = ['BP01_STATIC', 'BP01_PINS', 'BP01_BALLS', 'BP01_COLLISION', 'BP01_PRESENTATION']
    for name in required_names:
        assert name in bpy.data.collections, f"Missing collection {name}"
    errors = []
    root = bpy.data.objects['BowlingPair01_ROOT']
    static_col = bpy.data.collections['BP01_STATIC']
    balls_col = bpy.data.collections['BP01_BALLS']
    col_col = bpy.data.collections['BP01_COLLISION']
    pres_col = bpy.data.collections['BP01_PRESENTATION']

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

    hood = static_col.objects.get('Hood_Canopy')
    if hood:
        reshape_mesh(hood, 0.38, 1.80, 0.06)
        hood.location[0] = 0.0
        hood.location[1] = -2.29
        hood.location[2] = 2.0
    else:
        errors.append("Hood_Canopy not found in BP01_STATIC")

    af = static_col.objects.get('AlleyFloor')
    if af:
        af.location[2] = -0.325
    else:
        errors.append("AlleyFloor not found")

    mw = static_col.objects.get('MaskingWall')
    if mw:
        mw.location[1] = 20.0
        mw.location[2] = 3.125
    else:
        errors.append("MaskingWall not found")

    for idx in range(3):
        sname = 'ReturnRack_Support' if idx == 0 else 'ReturnRack_Support.%03d' % idx
        sup = static_col.objects.get(sname)
        if sup:
            reshape_mesh(sup, 0.04, 0.15, 0.50)
        else:
            errors.append(f"{sname} not found")

    # Collect names to delete, then delete in separate pass
    gutter_names = []
    for o in col_col.objects:
        if o.name.startswith('COL_Gutter_'):
            gutter_names.append(o.name)
    for gname in gutter_names:
        existing = col_col.objects.get(gname)
        if existing:
            col_col.objects.unlink(existing)
            if existing.data:
                bpy.data.meshes.remove(existing.data)
            bpy.data.objects.remove(existing)

    gutter_defs = [
        ('COL_Gutter_L_Outer', -1.7334, -1.4834),
        ('COL_Gutter_L_Inner', -0.4166, -0.1666),
        ('COL_Gutter_R_Inner', 0.1666, 0.4166),
        ('COL_Gutter_R_Outer', 1.4834, 1.7334),
    ]
    for gname, x1, x2 in gutter_defs:
        make_concave_gutter(gname, x1, x2, root, col_col)

    lanebed_names = []
    for o in col_col.objects:
        if o.name.startswith('COL_LaneBed_'):
            lanebed_names.append(o.name)
    for lname in lanebed_names:
        existing = col_col.objects.get(lname)
        if existing:
            col_col.objects.unlink(existing)
            if existing.data:
                bpy.data.meshes.remove(existing.data)
            bpy.data.objects.remove(existing)

    for lx in [-0.95, 0.95]:
        lname = 'COL_LaneBed_L' if lx < 0 else 'COL_LaneBed_R'
        hw = 0.5999
        me = bpy.data.meshes.new(lname + '_Mesh')
        verts = [
            (lx - hw, 0.0, -0.005),
            (lx + hw, 0.0, -0.005),
            (lx + hw, 19.20, -0.005),
            (lx - hw, 19.20, -0.005),
            (lx - hw, 0.0, 0.005),
            (lx + hw, 0.0, 0.005),
            (lx + hw, 19.20, 0.005),
            (lx - hw, 19.20, 0.005),
        ]
        faces = [(0,1,2,3),(4,7,6,5),(4,0,1,5),(3,2,6,7),(3,7,4,0),(1,4,5,2)]
        me.from_pydata(verts, [], faces)
        me.validate()
        obj = bpy.data.objects.new(lname, me)
        obj.parent = root
        col_col.objects.link(obj)

    rail_names = []
    for o in col_col.objects:
        if o.name in ('COL_Rail_L', 'COL_Rail_R', 'COL_RearStop'):
            rail_names.append(o.name)
    for rname in rail_names:
        existing = col_col.objects.get(rname)
        if existing:
            col_col.objects.unlink(existing)
            if existing.data:
                bpy.data.meshes.remove(existing.data)
            bpy.data.objects.remove(existing)

    for rx, rname in [(-1.755, 'COL_Rail_L'), (1.755, 'COL_Rail_R')]:
        me = bpy.data.meshes.new(rname + '_Mesh')
        rw, rh = 0.04, 0.10
        verts = [
            (rx - rw/2, -0.5, 0.0), (rx + rw/2, -0.5, 0.0),
            (rx + rw/2, -0.5, -rh), (rx - rw/2, -0.5, -rh),
            (rx - rw/2, 20.0, 0.0), (rx + rw/2, 20.0, 0.0),
            (rx + rw/2, 20.0, -rh), (rx - rw/2, 20.0, -rh),
        ]
        faces = [(0,1,2,3),(4,5,6,7),(3,2,6,7),(0,4,7,3),(0,3,2,1),(4,0,1,5)]
        me.from_pydata(verts, [], faces)
        me.validate()
        obj = bpy.data.objects.new(rname, me)
        obj.parent = root
        col_col.objects.link(obj)

    me_r = bpy.data.meshes.new('COL_RearStop_Mesh')
    verts_r = [
        (-1.8, 19.80, 0.0), (1.8, 19.80, 0.0),
        (1.8, 19.80, -0.15), (-1.8, 19.80, -0.15),
        (-1.8, 20.60, 0.0), (1.8, 20.60, 0.0),
        (1.8, 20.60, -0.15), (-1.8, 20.60, -0.15),
    ]
    faces_r = [(0,1,2,3),(4,5,6,7),(3,2,6,7),(0,4,7,3),(0,3,2,1),(4,0,1,5)]
    me_r.from_pydata(verts_r, [], faces_r)
    me_r.validate()
    obj_r = bpy.data.objects.new('COL_RearStop', me_r)
    obj_r.parent = root
    col_col.objects.link(obj_r)

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

    col_gutters = [o for o in col_col.objects if o.name.startswith('COL_Gutter_')]
    if len(col_gutters) != 4:
        errors.append(f"Expected 4 collision gutters, got {len(col_gutters)}")

    passed = len(errors) == 0

    report = {
        "stage": "04-07 fix",
        "name": "Geometry corrections: balls, dressing, collision, cameras",
        "passed": passed,
        "errors": errors,
    }

    out_dir = '/job'
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, 'report.json'), 'w') as f:
        json.dump(report, f, indent=2)

    return report

report = run_stage()
