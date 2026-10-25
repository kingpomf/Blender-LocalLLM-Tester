import bpy
import mathutils

def set_camera_lookat(cam, target_loc, up_vec=None):
    """Orient camera to look at target using quaternion rotation."""
    if up_vec is None:
        up_vec = mathutils.Vector((0, 0, 1))
    
    # Calculate direction from camera to target
    direction = (target_loc - cam.location).normalized()
    
    # Calculate quaternion that rotates (0, 1, 0) to direction
    # with up_vec as the up reference
    quat = direction.to_track_quat('Z', 'Y')
    cam.rotation_euler = quat.to_euler()

# ============================================================
# Fix 1: Ball_03 - restore to x=0.663 (proper spacing from Ball_02 at 0.221)
# The [-0.4,0.4] bound applies to return STRUCTURE, not balls
# ============================================================
ball03 = bpy.data.objects.get("Ball_03")
if ball03 is not None:
    ball03.location[0] = 0.663

# ============================================================
# Fix 2: Camera orientations - use lookat for proper frustum inclusion
# ============================================================

# Overview: from [3,8,5] looking toward center of alley [0, 9.6, 0]
cam_overview = bpy.data.objects.get("CAM_BowlingPair01_Overview")
if cam_overview is not None:
    set_camera_lookat(cam_overview, mathutils.Vector([0.0, 9.6, 0.0]))
    # Slight tilt up to include overhead elements
    euler = cam_overview.rotation_euler
    euler[0] += 0.15  # tilt up slightly

# Player: from left approach [-1.5,2,1.5] looking down left lane
cam_player = bpy.data.objects.get("CAM_BowlingPair01_Player")
if cam_player is not None:
    set_camera_lookat(cam_player, mathutils.Vector([-0.95, 10.0, 0.0]))
    euler = cam_player.rotation_euler
    euler[0] += 0.10

# PinDeck: from [0,10,4] looking at pins
cam_pindeck = bpy.data.objects.get("CAM_BowlingPair01_PinDeck")
if cam_pindeck is not None:
    set_camera_lookat(cam_pindeck, mathutils.Vector([0.0, 17.5, 0.5]))
    euler = cam_pindeck.rotation_euler
    euler[0] += 0.05

# Props: from near return [0.5,-1.5,1] looking at balls
cam_props = bpy.data.objects.get("CAM_BowlingPair01_Props")
if cam_props is not None:
    set_camera_lookat(cam_props, mathutils.Vector([0.0, -2.3, 0.2]))
    euler = cam_props.rotation_euler
    euler[0] += 0.10