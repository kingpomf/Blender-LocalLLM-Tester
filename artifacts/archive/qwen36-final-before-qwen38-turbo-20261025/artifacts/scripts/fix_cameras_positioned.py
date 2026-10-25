import bpy

# ============================================================
# Reposition cameras to be in front of the scene
# and pointing correctly at the bowling alley
# ============================================================

# Overview: from high up looking down at the full alley
cam_overview = bpy.data.objects.get("CAM_BowlingPair01_Overview")
if cam_overview is not None:
    cam_overview.location = (5.0, 15.0, 10.0)
    cam_overview.rotation_euler = (1.2217, 0.0, -0.3000)

# Player: from left side looking toward pins
cam_player = bpy.data.objects.get("CAM_BowlingPair01_Player")
if cam_player is not None:
    cam_player.location = (-3.0, 5.0, 2.0)
    cam_player.rotation_euler = (1.2000, 0.0, 0.0)

# PinDeck: from behind pins looking forward
cam_pindeck = bpy.data.objects.get("CAM_BowlingPair01_PinDeck")
if cam_pindeck is not None:
    cam_pindeck.location = (0.0, 12.0, 3.0)
    cam_pindeck.rotation_euler = (1.2000, 0.0, 0.0)

# Props: close-up of balls on return
cam_props = bpy.data.objects.get("CAM_BowlingPair01_Props")
if cam_props is not None:
    cam_props.location = (0.5, -0.5, 1.5)
    cam_props.rotation_euler = (0.8000, 0.0, 0.0)
