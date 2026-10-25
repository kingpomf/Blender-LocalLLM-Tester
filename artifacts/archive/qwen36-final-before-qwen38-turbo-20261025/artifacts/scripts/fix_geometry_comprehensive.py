import bpy

# ============================================================
# Comprehensive geometry corrections
# ============================================================

# 1. AlleyFloor: top at z=0 is not clearly "below z0".
#    Move center from -0.325 to -0.475 so top surface is at z=-0.15.
floor = bpy.data.objects.get("AlleyFloor")
if floor is not None:
    floor.location[2] = -0.475

# 2. MaskingWall: location [0, 19.8, 1.731], dimensions [12.5, 0.375, 3.75]
#    Local Z range: -1.875 to +1.875. Global Z: -0.144 to +3.606.
#    Pin tops at z~1.076. Need wall bottom >= 1.076 + 0.60 = 1.676.
#    Target: center at z=2.625 -> bottom at z=0.75, top at z=4.5
#    Actually need bottom >= 1.676 -> center >= 1.676 + 1.875 = 3.551
masking = bpy.data.objects.get("MaskingWall")
if masking is not None:
    masking.location[2] = 3.551

# 3. Ball positions: balls at z=0.108, cradles at z=0.08 center (top at 0.1175)
#    Gap = 0.008m. Fix: move balls so bottom sits ON cradle top.
#    Ball radius = 0.108. Cradle top = 0.1175. Ball center should be at 0.1175 + 0.108 = 0.2255
for name in ("Ball_01", "Ball_02", "Ball_03"):
    ball = bpy.data.objects.get(name)
    if ball is not None:
        ball.location[2] = 0.2255

# 4. Camera rotations: set in radians using ZYX order
#    Overview: look from [3,8,5] toward center of scene [0,10,1]
cam_overview = bpy.data.objects.get("CAM_BowlingPair01_Overview")
if cam_overview is not None:
    cam_overview.rotation_euler = (1.22173, 0.0, -0.30000)

#    Player: look from [-1.5,2,1.5] toward left lane pins
cam_player = bpy.data.objects.get("CAM_BowlingPair01_Player")
if cam_player is not None:
    cam_player.rotation_euler = (1.30000, 0.0, 0.10000)

#    PinDeck: look from [0,10,4] toward pins at z~1.076
cam_pindeck = bpy.data.objects.get("CAM_BowlingPair01_PinDeck")
if cam_pindeck is not None:
    cam_pindeck.rotation_euler = (1.40000, 0.0, 0.0)

#    Props: look from [0.5,-1.5,1] toward balls at return
cam_props = bpy.data.objects.get("CAM_BowlingPair01_Props")
if cam_props is not None:
    cam_props.rotation_euler = (1.00000, 0.0, -0.10000)
