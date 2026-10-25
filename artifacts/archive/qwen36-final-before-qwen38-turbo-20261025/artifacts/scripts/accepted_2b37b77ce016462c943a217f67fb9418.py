import bpy

# Restore original camera positions and rotations from the base scene

cam_overview = bpy.data.objects.get("CAM_BowlingPair01_Overview")
if cam_overview is not None:
    cam_overview.location = (3.0, 8.0, 5.0)
    cam_overview.rotation_euler = (1.2001, 0.0, -0.3000)

cam_player = bpy.data.objects.get("CAM_BowlingPair01_Player")
if cam_player is not None:
    cam_player.location = (-1.5, 2.0, 1.5)
    cam_player.rotation_euler = (1.3000, 0.0, 0.1000)

cam_pindeck = bpy.data.objects.get("CAM_BowlingPair01_PinDeck")
if cam_pindeck is not None:
    cam_pindeck.location = (0.0, 10.0, 4.0)
    cam_pindeck.rotation_euler = (1.3990, 0.0, 0.0)

cam_props = bpy.data.objects.get("CAM_BowlingPair01_Props")
if cam_props is not None:
    cam_props.location = (0.5, -1.5, 1.0)
    cam_props.rotation_euler = (1.0000, 0.0, -0.1000)