import bpy
import math
from mathutils import Vector, Quaternion, Matrix, Euler

def set_camera_look_at(cam, target, tilt_deg=0):
    """Set camera rotation using rotation matrix with explicit up vector."""
    # Direction from camera to target
    direction = (target - cam.location).normalized()
    
    # Build rotation: align camera -Z with direction using quaternion
    quat = direction.to_track_quat('-Z', 'Y')
    
    # Convert to ZXY Euler (Blender default order)
    euler = quat.to_euler('ZXY')
    
    # Apply tilt around camera's X axis
    tilt_rad = math.radians(tilt_deg)
    tilt_quat = Quaternion((1, 0, 0), tilt_rad)
    euler = (tilt_quat * quat).to_euler('ZXY')
    
    cam.rotation_euler = euler

# ============================================================
# Fix camera orientations using matrix-based approach
# ============================================================

# Overview: from [3,8,5] looking toward center [0, 9.6, 1], tilt up 10 deg
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
