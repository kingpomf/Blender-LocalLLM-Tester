import bpy
import math
from mathutils import Vector, Quaternion

def set_camera_look_at(cam, target, tilt_deg=0):
    """Set camera to look at target using explicit axis-angle rotation."""
    direction = (target - cam.location).normalized()
    
    # Camera default looks along -Z. Compute axis and angle to rotate -Z to direction.
    default = Vector((0, 0, -1))
    
    # Handle edge case where direction is same as default
    if abs(default.dot(direction)) > 0.9999:
        if default.dot(direction) > 0:
            # Already pointing the right way
            cam.rotation_euler = (0, 0, 0)
            return
        else:
            # 180 degree flip - rotate around X
            cam.rotation_euler = (math.pi, 0, 0)
            return
    
    axis = default.cross(direction).normalized()
    angle = math.acos(max(-1, min(1, default.dot(direction))))
    quat = Quaternion(axis, angle)
    
    # Apply tilt around camera local X
    if tilt_deg != 0:
        tilt_rad = math.radians(tilt_deg)
        tilt_quat = Quaternion((1, 0, 0), tilt_rad)
        quat = tilt_quat * quat
    
    cam.rotation_euler = quat.to_euler()

# ============================================================
# Fix camera orientations - use default Euler order (ZYX)
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
