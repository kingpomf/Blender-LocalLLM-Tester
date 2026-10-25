import bpy
import math

# ============================================================
# Final collision/geometry/camera fix for Stage 06 + 07
# Source: 2b37b77ce016462c943a217f67fb9418
# ============================================================

scene = bpy.context.scene
root = bpy.data.objects.get("BowlingPair01_ROOT")
collision_col = bpy.data.collections.get("BP01_COLLISION")
presentation_col = bpy.data.collections.get("BP01_PRESENTATION")

# ============================================================
# FIX 1: Rebuild gutter collision meshes as concave U-profiles
# Spec: 0.22-0.25m wide, trough bottom 0.08-0.12m below lane
# Current: flat boxes [0.25, 19.2, 0.03] - rejected
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
    """Build concave U-profile collision mesh using from_pydata."""
    hw = (x1 - x0) / 2.0  # half width ~0.125
    nseg = 16

    verts = []
    faces = []

    for i in range(nseg):
        y0 = (i / nseg) * length
        y1 = ((i + 1) / nseg) * length

        # U-profile cross-section vertices (4 points per Y)
        # x0 = lane edge, x1 = outer edge
        # Top lane-edge lip, top outer-edge lip, bottom outer, bottom inner
        x_lane_top = x0
        x_outer_top = x1
        x_lane_bot = x0 + 0.015
        x_outer_bot = x1 - 0.015

        v_base = i * 4

        # Front Y face vertices
        verts.append((x_lane_top,  y0, 0.000))   # v+0: top lane-edge
        verts.append((x_outer_top, y0, 0.000))   # v+1: top outer-edge
        verts.append((x_outer_bot, y0, -trough_depth))  # v+2: bottom outer
        verts.append((x_lane_bot,  y0, -trough_depth))  # v+3: bottom lane-edge

        # Back Y face vertices
        verts.append((x_lane_top,  y1, 0.000))   # v+4
        verts.append((x_outer_top, y1, 0.000))   # v+5
        verts.append((x_outer_bot, y1, -trough_depth))  # v+6
        verts.append((x_lane_bot,  y1, -trough_depth))  # v+7

        # 4 faces per segment: bottom, outer, inner (lane-side), top lip
        faces.append((v_base+0, v_base+1, v_base+2, v_base+3))  # trough bottom
        faces.append((v_base+1, v_base+5, v_base+6, v_base+2))  # outer face
        faces.append((v_base+0, v_base+3, v_base+7, v_base+4))  # inner lane-side face
        faces.append((v_base+4, v_base+5, v_base+6, v_base+7))  # top lip surface

    if name in bpy.data.objects:
        remove_collision_obj(name)

    me = bpy.data.meshes.new(name + "_Mesh")
    me.from_pydata(verts, [], faces)
    me.validate()
    me.update()

    obj = bpy.data.objects.new(name, me)
    obj.location = (cx, length / 2.0, 0.0)
    if root:
        obj.parent = root
    if collision_col:
        collision_col.objects.link(obj)
    return obj

gutter_results = []
for name, cx, x0, x1 in COL_GUTTERS:
    obj = rebuild_gutter_collision(name, cx, x0, x1)
    bbox = obj.bound_box
    z_min = min(v[2] for v in bbox)
    gutter_results.append(f"{name}: z_min={z_min:.3f}, width={x1-x0:.3f}")

for r in gutter_results:
    print(r)

# ============================================================
# FIX 2: Fix lane collision bounds - align Z-top to 0.0
# Current: Z range [-0.01, 0.001] instead of [thickness, 0.0]
# Spec: surface Z=0.0 ±0.002
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
        (x0, 0.0, 0.0),          # 0: front-left-top
        (x1, 0.0, 0.0),          # 1: front-right-top
        (x1, 19.20, 0.0),        # 2: back-right-top
        (x0, 19.20, 0.0),        # 3: back-left-top
        (x0, 0.0, -lane_thickness),  # 4: front-left-bottom
        (x1, 0.0, -lane_thickness),  # 5: front-right-bottom
        (x1, 19.20, -lane_thickness),# 6: back-right-bottom
        (x0, 19.20, -lane_thickness),# 7: back-left-bottom
    ]
    # Faces with outward normals:
    # top: 0,1,2,3 (CCW looking from above = outward)
    # bottom: 4,7,6,5 (CW looking from below = outward)
    # front: 0,4,5,1 (outward = toward negative Y)
    # back: 3,2,1,0 (outward = toward positive Y)
    # left: 4,0,3,7 (outward = toward negative X)
    # right: 5,6,7,4 (outward = toward positive X)
    faces = [
        (0, 1, 2, 3),   # top (lane surface)
        (4, 7, 6, 5),   # bottom
        (0, 4, 5, 1),   # front (approach side)
        (3, 2, 1, 0),   # back (pin deck side)
        (4, 0, 3, 7),   # left
        (5, 6, 7, 4),   # right
    ]

    me = bpy.data.meshes.new(name + "_Mesh")
    me.from_pydata(verts, [], faces)
    me.validate()
    me.update()

    obj = bpy.data.objects.new(name, me)
    obj.location = (cx, 9.6, 0.0)
    if root:
        obj.parent = root
    if collision_col:
        collision_col.objects.link(obj)

# Verify lane collision bounds
for name, cx, x0, x1 in COL_LANES:
    obj = bpy.data.objects.get(name)
    if obj:
        bbox = obj.bound_box
        z_max = max(v[2] for v in bbox)
        print(f"{name}: z_top={z_max:.4f}, x_range=[{x0:.4f}, {x1:.4f}]")

# ============================================================
# FIX 3: Fix inverted normals on closed surfaces
# Affected: Divider_Cap, Pit_Catch, OuterRail_R, all Gutter*
# Also: Gutter_L_Outer, Gutter_L_Inner, Gutter_R_Inner, Gutter_R_Outer
# ============================================================

FLAT_BOX_NAMES = [
    "Divider_Cap", "Pit_Catch", "OuterRail_R",
    "Gutter_L_Outer", "Gutter_L_Inner", "Gutter_R_Inner", "Gutter_R_Outer",
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
# FIX 4: Fix ArrowTri and Dot - make thin boxes, not flat surfaces
# Spec: zero volume and non-manifold edges
# ============================================================

def make_thin_box(name, center_x, center_y, z, width, depth, thickness):
    """Create a thin solid box to replace flat ArrowTri/Dot."""
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
        (0, 1, 2, 3),   # top
        (4, 7, 6, 5),   # bottom
        (0, 4, 5, 1),   # front
        (3, 2, 1, 0),   # back
        (4, 0, 3, 7),   # left
        (5, 6, 7, 4),   # right
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

# Arrow triangles per lane: 7 per lane, centered near Y=4.57
# Lane centers: X=-0.95 and X=0.95
# Arrow spacing: 7 arrows, spread ~0.12m apart laterally
arrow_z = 0.002  # just above lane surface
for lane_center, lane_x in [(-0.95, "L"), (0.95, "R")]:
    for i in range(7):
        dx = (i - 3) * 0.12  # spread from center
        ax = lane_center + dx
        ay = 4.57
        make_thin_box(f"ArrowTri_{lane_x}_{i+1:02d}", ax, ay, arrow_z, 0.08, 0.10, 0.002)

# Approach dots per lane: 7 per lane, centered near Y=-1.0
dot_z = 0.002
for lane_center, lane_x in [(-0.95, "L"), (0.95, "R")]:
    for i in range(7):
        dx = (i - 3) * 0.12
        dxy = lane_center + dx
        make_thin_box(f"Dot_{lane_x}_{i+1:02d}", dxy, -1.0, dot_z, 0.04, 0.04, 0.002)

print("ArrowTri and Dot rebuilt as thin boxes")

# ============================================================
# FIX 5: Ball_03 rack contact - position properly on return cradle
# Spec: surface contact within 0.005m, no penetration
# Previous: nearest_rack_distance = 0.447m (too far)
# ============================================================

ball_03 = bpy.data.objects.get("Ball_03")
if ball_03:
    # Center of rack area is X=0.0, Y=-2.3
    # Cradle top at Z~0.1175, ball radius 0.108
    # Ball center should be at Z = cradle_top + radius = ~0.2255
    ball_03.location = (0.0, -2.3, 0.2255)
    print(f"Ball_03: position = {ball_03.location}")

# ============================================================
# FIX 6: Camera framing - ensure all targets in positive frustum
# Blender cameras look along -Z axis; frustum = positive Z relative to cam
# ============================================================

# Overview: from elevated position behind approach, looking down full lane pair
cam_overview = bpy.data.objects.get("CAM_BowlingPair01_Overview")
if cam_overview:
    cam_overview.location = (0.0, 5.0, 6.0)
    dir_to_scene = (0.0, 9.6, 1.0) - cam_overview.location
    quat = dir_to_scene.normalized().to_track_quat('-Z', 'Y')
    euler = quat.to_euler()
    euler[0] += 0.1  # slight upward tilt to see approach
    cam_overview.rotation_euler = euler
    if hasattr(cam_overview.data, 'lens'):
        cam_overview.data.lens = 28
    print(f"Overview cam: loc={cam_overview.location}, rot={tuple(round(x,4) for x in cam_overview.rotation_euler)}, lens=28")

# Player: from left approach looking down left lane
cam_player = bpy.data.objects.get("CAM_BowlingPair01_Player")
if cam_player:
    cam_player.location = (-1.0, 3.0, 1.8)
    dir_to_scene = (-0.95, 10.0, 0.5) - cam_player.location
    quat = dir_to_scene.normalized().to_track_quat('-Z', 'Y')
    euler = quat.to_euler()
    euler[0] += 0.05
    cam_player.rotation_euler = euler
    if hasattr(cam_player.data, 'lens'):
        cam_player.data.lens = 35
    print(f"Player cam: loc={cam_player.location}, rot={tuple(round(x,4) for x in cam_player.rotation_euler)}, lens=35")

# PinDeck: from mid-lane looking at pin racks
cam_pindeck = bpy.data.objects.get("CAM_BowlingPair01_PinDeck")
if cam_pindeck:
    cam_pindeck.location = (0.0, 12.0, 3.5)
    dir_to_scene = (0.0, 17.5, 0.8) - cam_pindeck.location
    quat = dir_to_scene.normalized().to_track_quat('-Z', 'Y')
    euler = quat.to_euler()
    euler[0] += 0.05
    cam_pindeck.rotation_euler = euler
    if hasattr(cam_pindeck.data, 'lens'):
        cam_pindeck.data.lens = 35
    print(f"PinDeck cam: loc={cam_pindeck.location}, rot={tuple(round(x,4) for x in cam_pindeck.rotation_euler)}, lens=35")

# Props: close-up of balls on return rack, angled for grip visibility
cam_props = bpy.data.objects.get("CAM_BowlingPair01_Props")
if cam_props:
    cam_props.location = (0.0, -3.5, 1.5)
    dir_to_scene = (0.0, -2.3, 0.2255) - cam_props.location
    quat = dir_to_scene.normalized().to_track_quat('-Z', 'Y')
    euler = quat.to_euler()
    euler[0] += 0.15  # tilt down toward balls
    cam_props.rotation_euler = euler
    if hasattr(cam_props.data, 'lens'):
        cam_props.data.lens = 50
    print(f"Props cam: loc={cam_props.location}, rot={tuple(round(x,4) for x in cam_props.rotation_euler)}, lens=50")

# ============================================================
# Summary
# ============================================================
print("\n=== FINAL FIX SUMMARY ===")
print(f"Gutter collision: 4 concave U-profiles rebuilt")
print(f"Lane collision: 2 meshes with Z-top aligned to 0.0")
print(f"Normals: fixed on {len(FLAT_BOX_NAMES)} flat-box objects")
print(f"ArrowTri/Dot: rebuilt as thin boxes (7 per lane)")
print(f"Ball_03: repositioned on return cradle")
print(f"Cameras: 4 views repositioned with proper tracking")
print("=== END SUMMARY ===")
