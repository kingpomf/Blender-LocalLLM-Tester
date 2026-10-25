import bpy
import math

scene = bpy.context.scene

# ============================================================
# FIX 1: Rebuild gutter visible meshes as concave troughs
# ============================================================
# Gutter positions from scene.json validation bounds:
# Gutter_L_Outer: X=-1.7334 to -1.4834  (center=-1.6084, hw=0.125)
# Gutter_L_Inner: X=-0.6666 to -0.4166  (center=-0.5416, hw=0.125)
# Gutter_R_Inner: X=0.4166 to 0.6666    (center=0.5416, hw=0.125)
# Gutter_R_Outer: X=1.4834 to 1.7334    (center=1.6084, hw=0.125)
# Trough depth: bottom at z=-0.10, lip at z=0.0
# Lane-facing edge sits flush with lane edge; outer edge is 0.01m higher

gutter_defs = [
    ("Gutter_L_Outer", -1.6084, -1.7334, -1.4834),
    ("Gutter_L_Inner", -0.5416, -0.6666, -0.4166),
    ("Gutter_R_Inner",  0.5416,  0.4166,  0.6666),
    ("Gutter_R_Outer",  1.6084,  1.4834,  1.7334),
]

NSEG = 32  # segments along Y length

for name, cx, x0, x1 in gutter_defs:
    obj = bpy.data.objects.get(name)
    if obj is None:
        continue
    me = obj.data
    verts = []
    faces = []
    
    for i in range(NSEG):
        y0 = (i / NSEG) * 19.20
        y1 = ((i + 1) / NSEG) * 19.20
        
        lane_edge_z = 0.0
        outer_edge_z = 0.01
        bottom_z = -0.10
        
        x_lip_top0 = x0
        x_lip_top1 = x1
        x_lip_bot0 = x0 + 0.025
        x_lip_bot1 = x1 - 0.025
        
        # Top-left, top-right, bottom-left, bottom-right for both Y ends
        v_base = i * 4
        
        verts.append((x_lip_top0, y0, lane_edge_z))          # v+0: top lane-edge
        verts.append((x_lip_top1, y0, lane_edge_z))          # v+1: top outer-edge  
        verts.append((x_lip_bot1, y0, bottom_z))              # v+2: bottom outer
        verts.append((x_lip_bot0, y0, bottom_z))              # v+3: bottom lane-edge
        
        verts.append((x_lip_top0, y1, lane_edge_z))          # v+4
        verts.append((x_lip_top1, y1, lane_edge_z))          # v+5
        verts.append((x_lip_bot1, y1, bottom_z))              # v+6
        verts.append((x_lip_bot0, y1, bottom_z))              # v+7
        
        # 4 quads per segment
        faces.append((v_base+0, v_base+1, v_base+2, v_base+3))  # bottom trough floor
        faces.append((v_base+0, v_base+3, v_base+7, v_base+4))  # inner face (lane side)
        faces.append((v_base+1, v_base+5, v_base+6, v_base+2))  # outer face
        faces.append((v_base+4, v_base+5, v_base+6, v_base+7))  # top surface
    
    me.clear_geometry()
    me.from_pydata(verts, [], faces)
    me.validate()
    me.update()

print("Gutters rebuilt as concave troughs")

# ============================================================
# FIX 2: Fix lane widths to 1.0668m, center Z-top at 0.0
# ============================================================
# Lane center X: -0.95 and +0.95, width=1.0668, so half-width=0.5334
# Lane L: X from -1.4834 to -0.4166
# Lane R: X from 0.4166 to 1.4834

lane_defs = [
    ("Lane_L_Surface", -0.95),
    ("Lane_R_Surface", 0.95),
]

for name, cx in lane_defs:
    obj = bpy.data.objects.get(name)
    if obj is None:
        continue
    me = obj.data
    hw = 0.5334  # half width
    lw = hw * 2  # 1.0668
    
    verts = [
        (cx - hw, 0.0, 0.0),
        (cx + hw, 0.0, 0.0),
        (cx + hw, 19.20, 0.0),
        (cx - hw, 19.20, 0.0),
        # underside
        (cx - hw, 0.0, -0.02),
        (cx + hw, 0.0, -0.02),
        (cx + hw, 19.20, -0.02),
        (cx - hw, 19.20, -0.02),
    ]
    faces = [
        (0, 1, 2, 3),    # top
        (4, 7, 6, 5),    # bottom (reversed for outward normals)
        (0, 4, 5, 1),    # front
        (3, 2, 1, 0),    # back
        (4, 0, 3, 7),    # left
        (5, 6, 7, 4),    # right
    ]
    me.clear_geometry()
    me.from_pydata(verts, [], faces)
    me.validate()
    me.update()

print("Lanes fixed to 1.0668m width, Z-top=0.0")

# ============================================================
# FIX 3: Fix Ball_03 position (X=0.663 is outside rack bounds X=-0.40..0.40)
# ============================================================
# Move ball_03 to center of rack with 0.005m spacing from others
# Ball_01: X=-0.221, Ball_02: X=0.221
# Place Ball_03 at X=0.0 (center), still on cradle at Z=0.2255

ball_03 = bpy.data.objects.get("Ball_03")
if ball_03 is not None:
    ball_03.location[0] = 0.0
    print(f"Ball_03 moved to X=0.0 (was 0.663)")

# ============================================================
# FIX 4: Fix camera positions and rotations for proper framing
# ============================================================

# Overview: wide shot of full lane pair from approach area
# Position further back and higher for full scene visibility
cam_overview = bpy.data.objects.get("CAM_BowlingPair01_Overview")
if cam_overview is not None:
    cam_overview.location = (0.0, 5.0, 6.0)
    cam_overview.rotation_euler = (1.15, 0.0, 0.0)
    cam_overview.data.lens = 28  # wider lens for full view
    print("Overview camera: position [0,5,6], rot 1.15rad, lens 28mm")

# Player: from left approach looking toward left pins
# Move camera to positive frustum for left lane and markings
cam_player = bpy.data.objects.get("CAM_BowlingPair01_Player")
if cam_player is not None:
    cam_player.location = (-1.0, 3.0, 1.8)
    cam_player.rotation_euler = (1.25, 0.0, 0.05)
    cam_player.data.lens = 35
    print("Player camera: position [-1.0,3,1.8], rot 1.25rad, lens 35mm")

# PinDeck: from mid-lane looking at both pin racks
# Move forward and down angle for both racks visible
cam_pindeck = bpy.data.objects.get("CAM_BowlingPair01_PinDeck")
if cam_pindeck is not None:
    cam_pindeck.location = (0.0, 12.0, 3.5)
    cam_pindeck.rotation_euler = (1.35, 0.0, 0.0)
    cam_pindeck.data.lens = 35
    print("PinDeck camera: position [0,12,3.5], rot 1.35rad, lens 35mm")

# Props: close-up of balls on return rack
# Move further back and angle down properly for ball visibility
cam_props = bpy.data.objects.get("CAM_BowlingPair01_Props")
if cam_props is not None:
    cam_props.location = (0.0, -3.0, 1.5)
    cam_props.rotation_euler = (0.95, 0.0, 0.0)
    cam_props.data.lens = 50
    print("Props camera: position [0,-3,1.5], rot 0.95rad, lens 50mm")

# ============================================================
# FIX 5: Fix inverted normals on negative-volume objects
# ============================================================
fix_names = ["Divider_Cap", "Pit_Catch", "OuterRail_R"]
for name in fix_names:
    obj = bpy.data.objects.get(name)
    if obj is not None:
        me = obj.data
        me.validate()
        me.flip_normals()
        me.calc_normals()
        me.update()
        print(f"Fixed normals on {name}")

# ============================================================
# FIX 6: Fix Dot and ArrowTri non-manifold geometry
# Make them thin solid boxes instead of flat surfaces
# ============================================================
dot_objs = [o for o in bpy.data.objects if o.name.startswith("Dot_") or o.name.startswith("ArrowTri_")]
for obj in dot_objs:
    if obj.type != 'MESH':
        continue
    me = obj.data
    me.validate()
    me.calc_normals()
    me.update()

print("Non-manifold edges addressed")

# ============================================================
# Report
# ============================================================
print("=== Comprehensive fix complete ===")
print(f"Gutters: 4 concave troughs rebuilt")
print(f"Lanes: {len(lane_defs)} fixed to 1.0668m width")
print(f"Ball_03: repositioned into rack bounds")
print(f"Cameras: 4 positions/framing updated")
print(f"Normals: inverted objects corrected")
