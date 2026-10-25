import bpy
import math
from mathutils import Vector, Quaternion

def set_camera_look_at(cam, target, up=(0, 0, 1), tilt_x=0.0):
    """Orient camera to look at target. Blender cameras look along -Z."""
    dir_vec = (target - cam.location).normalized()
    # to_track_quat('-Z', 'Y') aligns object's -Z at dir_vec
    # Since Blender cameras look along -Z, the camera now points AT target
    quat = dir_vec.to_track_quat('-Z', 'Y')
    euler = quat.to_euler()
    euler[0] += tilt_x  # slight upward tilt
    cam.rotation_euler = euler

# ============================================================
# Fix camera orientations using proper -Z looking convention
# ============================================================

# Overview: from [3,8,5] looking toward scene center [0, 9.6, 1]
cam_overview = bpy.data.objects.get("CAM_BowlingPair01_Overview")
if cam_overview is not None:
    set_camera_look_at(cam_overview, Vector([0.0, 9.6, 1.0]), tilt_x=0.1)

# Player: from left approach [-1.5, 2, 1.5] looking down left lane [-0.95, 10, 0]
cam_player = bpy.data.objects.get("CAM_BowlingPair01_Player")
if cam_player is not None:
    set_camera_look_at(cam_player, Vector([-0.95, 10.0, 0.0]), tilt_x=0.05)

# PinDeck: from [0, 10, 4] looking at pins [0, 17.5, 0.5]
cam_pindeck = bpy.data.objects.get("CAM_BowlingPair01_PinDeck")
if cam_pindeck is not None:
    set_camera_look_at(cam_pindeck, Vector([0.0, 17.5, 0.5]), tilt_x=0.05)

# Props: from [0.5, -1.5, 1] looking at balls [0, -2.3, 0.2]
cam_props = bpy.data.objects.get("CAM_BowlingPair01_Props")
if cam_props is not None:
    set_camera_look_at(cam_props, Vector([0.0, -2.3, 0.2]), tilt_x=0.1)