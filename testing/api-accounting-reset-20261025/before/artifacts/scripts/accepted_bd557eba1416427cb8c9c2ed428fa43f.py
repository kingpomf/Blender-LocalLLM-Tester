import bpy
import math
from mathutils import Vector

# ============================================================
# Final collision/geometry/camera fix for Stage 06 + 07
# Source: 2b37b77ce016462c943a217f67fb9418
# ============================================================

scene = bpy.context.scene
root = bpy.data.objects.get("BowlingPair01_ROOT")
collision_col = bpy.data.collections.get("BP01_COLLISION")

# ============================================================
# FIX 1: Rebuild gutter collision meshes as concave U-profiles
# ============================================================

COL_GUTTERS = [
    ("COL_Gutter_L_Outer", -1.6084, -1.7334, -1.4834),
    ("COL_Gutter_L_Inner", -0.5416, -0.6666, -0.4166),
    ("COL_Gutter_R_Inner",  0.5416,  0.4166,  0.6666),
    ("COL_Gutter_R_Outer",  1.6084,  1.4834,  1.7334),
]

def remove_collision_obj(name):
    if name in bpy.data.objects:
        obj = bpy.data.objects[name]
        if root and obj.parent == root:
            root.children.unlink(obj)
        bpy.data.objects.remove(obj, do_unlink=True)
    if name in bpy.data.meshes:
        bpy.data.meshes.remove(bpy.data.meshes[name])

def rebuild_gutter_collision(name, cx, x0, x1, length=19.20, trough_depth=0.10):
    nseg = 16
    verts = []
    faces = []
    for i in range(nseg):
        y0 = (i / nseg) * length
        y1 = ((i + 1) / nseg) * length
        x_lane_top = x0
        x_outer_top = x1
        x_lane_bot = x0 + 0.015
        x_outer_bot = x1 - 0.015
        v_base = i * 4
        verts.append((x_lane_top,  y0, 0.000))
        verts.append((x_outer_top, y0, 0.000))
        verts.append((x_outer_bot, y0, -trough_depth))
        verts.append((x_lane_bot,  y0, -trough_depth))
        verts.append((x_lane_top,  y1, 0.000))
        verts.append((x_outer_top, y1, 0.000))
        verts.append((x_outer_bot, y1, -trough_depth))
        verts.append((x_lane_bot,  y1, -trough_depth))
        faces.append((v_base+0, v_base+1, v_base+2, v_base+3))
        faces.append((v_base+1, v_base+5, v_base+6, v_base+2))
        faces.append((v_base+0, v_base+3, v_base+7, v_base+4))
        faces.append((v_base+4, v_base+5, v_base+6, v_base+7))
    if name in bpy.data.objects:
        remove_collision_obj(name)
    me = bpy.data.meshes.new(name + "_Mesh")
    me.from_pydata(verts, [], faces)
    me.validate()
    me.update()
    obj = bpy.data.objects.new(name, me)
    obj.location = Vector((cx, length / 2.0, 0.0))
    if root:
        obj.parent = root
    if collision_col:
        collision_col.objects.link(obj)
    return obj

for name, cx, x0, x1 in COL_GUTTERS:
    obj = rebuild_gutter_collision(name, cx, x0, x1)
    bbox = obj.bound_box
    z_min = min(v[2] for v in bbox)
    print(f"Gutter {name}: z_min={z_min:.3f}, width={x1-x0:.3f}")

# ============================================================
# FIX 2: Fix lane collision bounds - align Z-top to 0.0
# ============================================================

COL_LANES = [
    ("COL_Lane_L", -0.95, -1.4834, -0.4166),
    ("COL_Lane_R",  0.95,  0.4166,  1.4834),
]
lane_thickness = 0.02

for name, cx, x0, x1 in COL_LANES:
    if name in bpy.data.objects:
        remove_collision_obj(name)
    verts = [
        (x0, 0.0, 0.0),
        (x1, 0.0, 0.0),
        (x1, 19.20, 0.0),
        (x0, 19.20, 0.0),
        (x0, 0.0, -lane_thickness),
        (x1, 0.0, -lane_thickness),
        (x1, 19.20, -lane_thickness),
        (x0, 19.20, -lane_thickness),
    ]
    faces = [
        (0, 1, 2, 3),
        (4, 7, 6, 5),
        (0, 4, 5, 1),
        (3, 2, 1, 0),
        (4, 0, 3, 7),
        (5, 6, 7, 4),
    ]
    me = bpy.data.meshes.new(name + "_Mesh")
    me.from_pydata(verts, [], faces)
    me.validate()
    me.update()
    obj = bpy.data.objects.new(name, me)
    obj.location = Vector((cx, 9.6, 0.0))
    if root:
        obj.parent = root
    if collision_col:
        collision_col.objects.link(obj)
    bbox = obj.bound_box
    z_max = max(v[2] for v in bbox)
    print(f"Lane {name}: z_top={z_max:.4f}")

# ============================================================
# FIX 3: Fix inverted normals on closed surfaces
# ============================================================

FLAT_BOX_NAMES = [
    "Divider_Cap", "Pit_Catch", "OuterRail_R",
    "OuterRail_L",
]

for name in FLAT_BOX_NAMES:
    obj = bpy.data.objects.get(name)
    if obj and obj.type == 'MESH':
        me = obj.data
        me.flip_normals()
        me.update()
        print(f"Fixed normals: {name}")

# ============================================================
# FIX 4: Fix ArrowTri and Dot - make thin boxes
# ============================================================

def make_thin_box(name, center_x, center_y, z, width, depth, thickness):
    hw, hd, ht = width / 2.0, depth / 2.0, thickness / 2.0
    if name in bpy.data.objects:
        remove_collision_obj(name)
    verts = [
        (center_x - hw, center_y - hd, z + ht),
        (center_x + hw, center_y - hd, z + ht),
        (center_x + hw, center_y + hd, z + ht),
        (center_x - hw, center_y + hd, z + ht),
        (center_x - hw, center_y - hd, z - ht),
        (center_x + hw, center_y - hd, z - ht),
        (center_x + hw, center_y + hd, z - ht),
        (center_x - hw, center_y + hd, z - ht),
    ]
    faces = [
        (0, 1, 2, 3),
        (4, 7, 6, 5),
        (0, 4, 5, 1),
        (3, 2, 1, 0),
        (4, 0, 3, 7),
        (5, 6, 7, 4),
    ]
    me = bpy.data.meshes.new(name + "_Mesh")
    me.from_pydata(verts, [], faces)
    me.validate()
    me.update()
    obj = bpy.data.objects.new(name, me)
    obj.location = (center_x, center_y, z)
    if root:
        obj.parent = root
    if collision_col:
        collision_col.objects.link(obj)

arrow_z = 0.002
for lane_center, lane_x in [(-0.95, "L"), (0.95, "R")]:
    for i in range(7):
        dx = (i - 3) * 0.12
        ax = lane_center + dx
        ay = 4.57
        make_thin_box(f"ArrowTri_{lane_x}_{i+1:02d}", ax, ay, arrow_z, 0.08, 0.10, 0.002)

dot_z = 0.002
for lane_center, lane_x in [(-0.95, "L"), (0.95, "R")]:
    for i in range(7):
        dx = (i - 3) * 0.12
        dxy = lane_center + dx
        make_thin_box(f"Dot_{lane_x}_{i+1:02d}", dxy, -1.0, dot_z, 0.04, 0.04, 0.002)

print("ArrowTri and Dot rebuilt as thin boxes")

# ============================================================
# FIX 5: Ball_03 rack contact positioning
# ============================================================

ball_03 = bpy.data.objects.get("Ball_03")
if ball_03:
    ball_03.location = Vector((0.0, -2.3, 0.2255))
    print(f"Ball_03: position = {ball_03.location}")

# ============================================================
# FIX 6: Camera framing - ensure all targets in positive frustum
# ============================================================

cam_configs = [
    ("CAM_BowlingPair01_Overview", Vector((0.0, 5.0, 6.0)), Vector((0.0, 9.6, 1.0)), 0.1, 28),
    ("CAM_BowlingPair01_Player", Vector((-1.0, 3.0, 1.8)), Vector((-0.95, 10.0, 0.5)), 0.05, 35),
    ("CAM_BowlingPair01_PinDeck", Vector((0.0, 12.0, 3.5)), Vector((0.0, 17.5, 0.8)), 0.05, 35),
    ("CAM_BowlingPair01_Props", Vector((0.0, -3.5, 1.5)), Vector((0.0, -2.3, 0.2255)), 0.15, 50),
]

for cam_name, loc, target, tilt, lens in cam_configs:
    cam = bpy.data.objects.get(cam_name)
    if cam:
        cam.location = loc
        dir_to_scene = target - loc
        quat = dir_to_scene.normalized().to_track_quat('-Z', 'Y')
        euler = quat.to_euler()
        euler[0] += tilt
        cam.rotation_euler = euler
        if hasattr(cam.data, 'lens'):
            cam.data.lens = lens
        print(f"{cam_name}: loc={cam.location}, lens={lens}")

print("=== FINAL FIX COMPLETE ===")