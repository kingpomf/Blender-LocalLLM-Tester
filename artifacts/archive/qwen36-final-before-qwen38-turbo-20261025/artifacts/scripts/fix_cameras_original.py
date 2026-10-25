import bpy

# ============================================================
# Restore original camera rotations from the base scene
# and slightly adjust positions for better framing
# ============================================================

# Overview: original rotation [1.2001, 0, -0.3000]
# Move camera further back and left for wider view
cam_overview = bpy.data.objects.get("CAM_BowlingPair01_Overview")
if cam_overview is not None:
    cam_overview.rotation_euler = (1.2001, 0.0, -0.3000)
    cam_overview.location = (4.0, 6.0, 6.0)

# Player: original rotation [1.300, 0, 0.1000]
cam_player = bpy.data.objects.get("CAM_BowlingPair01_Player")
if cam_player is not None:
    cam_player.rotation_euler = (1.3000, 0.0, 0.1000)

# PinDeck: original rotation [1.399, 0, 0]
cam_pindeck = bpy.data.objects.get("CAM_BowlingPair01_PinDeck")
if cam_pindeck is not None:
    cam_pindeck.rotation_euler = (1.3990, 0.0, 0.0)

# Props: original rotation [1.000, 0, -0.1000]
cam_props = bpy.data.objects.get("CAM_BowlingPair01_Props")
if cam_props is not None:
    cam_props.rotation_euler = (1.0000, 0.0, -0.1000)
