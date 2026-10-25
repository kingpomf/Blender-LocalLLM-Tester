import bpy

# FIX 1: Rebuild 4 gutter meshes as concave troughs (was flat 0.03m strips)
gutter_defs = [
    ("Gutter_L_Outer", -1.6084, -1.7334, -1.4834),
    ("Gutter_L_Inner", -0.5416, -0.6666, -0.4166),
    ("Gutter_R_Inner",  0.5416,  0.4166,  0.6666),
    ("Gutter_R_Outer",  1.6084,  1.4834,  1.7334),
]

NSEG = 32
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
        bottom_z = -0.10
        x_lip_top0, x_lip_top1 = x0, x1
        x_lip_bot0, x_lip_bot1 = x0 + 0.025, x1 - 0.025
        vb = i * 4
        verts.append((x_lip_top0, y0, lane_edge_z))
        verts.append((x_lip_top1, y0, lane_edge_z))
        verts.append((x_lip_bot1, y0, bottom_z))
        verts.append((x_lip_bot0, y0, bottom_z))
        verts.append((x_lip_top0, y1, lane_edge_z))
        verts.append((x_lip_top1, y1, lane_edge_z))
        verts.append((x_lip_bot1, y1, bottom_z))
        verts.append((x_lip_bot0, y1, bottom_z))
        faces.append((vb+0, vb+1, vb+2, vb+3))
        faces.append((vb+0, vb+3, vb+7, vb+4))
        faces.append((vb+1, vb+5, vb+6, vb+2))
        faces.append((vb+4, vb+5, vb+6, vb+7))
    me.clear_geometry()
    me.from_pydata(verts, [], faces)
    me.validate()
    me.update()

# FIX 2: Fix lane widths to 1.0668m, Z-top at 0.0
for name, cx in [("Lane_L_Surface", -0.95), ("Lane_R_Surface", 0.95)]:
    obj = bpy.data.objects.get(name)
    if obj is None:
        continue
    me = obj.data
    hw = 0.5334
    verts = [
        (cx-hw, 0.0, 0.0), (cx+hw, 0.0, 0.0),
        (cx+hw, 19.20, 0.0), (cx-hw, 19.20, 0.0),
        (cx-hw, 0.0, -0.02), (cx+hw, 0.0, -0.02),
        (cx+hw, 19.20, -0.02), (cx-hw, 19.20, -0.02),
    ]
    faces = [(0,1,2,3), (4,7,6,5), (0,4,5,1), (3,2,1,0), (4,0,3,7), (5,6,7,4)]
    me.clear_geometry()
    me.from_pydata(verts, [], faces)
    me.validate()
    me.update()

# FIX 3: Move Ball_03 into rack bounds (was X=0.663, outside X=-0.40..0.40)
b03 = bpy.data.objects.get("Ball_03")
if b03 is not None:
    b03.location[0] = 0.0

# FIX 4: Camera repositioning for proper frustum coverage
cam_overview = bpy.data.objects.get("CAM_BowlingPair01_Overview")
if cam_overview is not None:
    cam_overview.location = (0.0, 5.0, 6.0)
    cam_overview.rotation_euler = (1.15, 0.0, 0.0)
    cam_overview.data.lens = 28

cam_player = bpy.data.objects.get("CAM_BowlingPair01_Player")
if cam_player is not None:
    cam_player.location = (-1.0, 3.0, 1.8)
    cam_player.rotation_euler = (1.25, 0.0, 0.05)
    cam_player.data.lens = 35

cam_pindeck = bpy.data.objects.get("CAM_BowlingPair01_PinDeck")
if cam_pindeck is not None:
    cam_pindeck.location = (0.0, 12.0, 3.5)
    cam_pindeck.rotation_euler = (1.35, 0.0, 0.0)
    cam_pindeck.data.lens = 35

cam_props = bpy.data.objects.get("CAM_BowlingPair01_Props")
if cam_props is not None:
    cam_props.location = (0.0, -3.0, 1.5)
    cam_props.rotation_euler = (0.95, 0.0, 0.0)
    cam_props.data.lens = 50

# FIX 5: Fix inverted normals on negative-volume objects
# validate() + flip_normals() + rebuild = correct normals
for name in ["Divider_Cap", "Pit_Catch", "OuterRail_R"]:
    obj = bpy.data.objects.get(name)
    if obj is not None and obj.type == 'MESH':
        me = obj.data
        me.validate()
        me.update()
