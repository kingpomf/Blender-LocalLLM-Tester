import bpy
import math
from mathutils import Vector, Quaternion

def set_camera_look_at(cam, target, tilt_deg=0):
    """Set camera to look at target using rotation difference from -Z default."""
    direction = (target - cam.location).normalized()
    
    # Default camera looks along -Z (0, 0, -1) when rotation is (0,0,0)
    default_dir = Vector((0, 0, -1))
    
    # Compute quaternion that rotates -Z to direction
    quat = default_dir.rotation_difference(direction)
    
    # Apply tilt around camera's local X axis
    if tilt_deg != 0:
        tilt_rad = math.radians(tilt_deg)
        tilt_quat = Quaternion((1, 0, 0), tilt_rad)
        quat = tilt_quat * quat
    
    cam.rotation_euler = quat.to_euler('ZXY')

# ============================================================
# Fix camera orientations
# ============================================================

# Overview: from [3,8,5] looking toward center [0, 9.6, 1], tilt 10 deg
cam_overview = bpy.data.objects.get("CAM_BowlingPair01_Overview")
if cam_overview is not None:
    set_camera_look_at(cam_overview, Vector([0.0, 9.6, 1.0]), tilt_deg=10)

# Player: from left approach [-1.5, 2, 1.5] looking down lane [-0.95, 10, 0], tilt 5 deg
cam_player = bpy.data.objects.get("CAM_BowlingPair01_Player")
if cam_player is not None:
    set_camera_look_at(cam_player, Vector([-0.95, 10.0, 0.0]), tilt_deg=5)

# PinDeck: from [0, 10, 4] looking at pins [0, 17.5, 0.5], tilt 5 deg
cam_pindeck = bpy.data.objects.get("CAM_BowlingPair01_PinDeck")
if cam_pindeck is not None:
    set_camera_look_at(cam_pindeck, Vector([0.0, 17.5, 0.5]), tilt_deg=5)

# Props: from [0.5, -1.5, 1] looking at balls [0, -2.3, 0.2], tilt 10 deg
cam_props = bpy.data.objects.get("CAM_BowlingPair01_Props")
if cam_props is not None:
    set_camera_look_at(cam_props, Vector([0.0, -2.3, 0.2]), tilt_deg=10)
