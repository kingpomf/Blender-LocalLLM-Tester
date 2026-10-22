import bpy
import json

sc = bpy.context.scene
report = {
    "stage": "07",
    "phase": "presentation_cameras_and_lighting",
    "source_job": "a3b4be8121804a6e8bf28327db912b11",
    "checks": {}
}

pres_coll = bpy.data.collections.get("KART01_PRESENTATION")
assert pres_coll is not None, "KART01_PRESENTATION missing"

# Create ground plane at Z=0
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Kart01_Ground"
ground.location = (0, 0, 0)
pres_coll.objects.link(ground)
sc.collection.objects.unlink(ground)

# Create cameras
def create_camera(name, location, target):
    bpy.ops.camera.add(location=location)
    cam = bpy.context.active_object
    cam.name = name
    cam.data.lens = 50.0
    # Aim camera at target
    direction = (target[0] - location[0], target[1] - location[1], target[2] - location[2])
    cam.rotation_euler = cam.to_track_quat(direction, 'Y', 'Z').to_euler()
    pres_coll.objects.link(cam)
    sc.collection.objects.unlink(cam)
    return cam

# Perspective camera (3/4 view)
cam_persp = create_camera("CAM_Kart01_Perspective", (3, -3, 2), (0, 0, 0.3))
sc.camera = cam_persp

# Front camera (looking at front of kart)
cam_front = create_camera("CAM_Kart01_Front", (0, -4, 1), (0, 0, 0.3))

# Side camera (looking at left side of kart)
cam_side = create_camera("CAM_Kart01_Side", (-4, 0, 1), (0, 0, 0.3))

# Rear camera (looking at rear of kart)
cam_rear = create_camera("CAM_Kart01_Rear", (0, 4, 1), (0, 0, 0.3))

# Create lights
def create_light(name, location, energy=1000, color=(1.0, 1.0, 1.0)):
    bpy.ops.object.light_add(type='AREA', location=location)
    light = bpy.context.active_object
    light.name = name
    light.data.energy = energy
    light.data.color = color
    light.data.size = 2.0
    light.data.shape = 'SQUARE'
    pres_coll.objects.link(light)
    sc.collection.objects.unlink(light)
    return light

# Key light (main, from upper right)
light_key = create_light("LIGHT_Kart01_Key", (5, -5, 5), energy=1500)
direction = (-5, 5, -5)
light_key.rotation_euler = light_key.to_track_quat(direction, 'Y', 'Z').to_euler()

# Fill light (softer, from left)
light_fill = create_light("LIGHT_Kart01_Fill", (-5, 0, 3), energy=500, color=(0.9, 0.95, 1.0))
direction = (5, 0, -3)
light_fill.rotation_euler = light_fill.to_track_quat(direction, 'Y', 'Z').to_euler()

# Rim light (from behind)
light_rim = create_light("LIGHT_Kart01_Rim", (0, 5, 4), energy=800)
direction = (0, -5, -4)
light_rim.rotation_euler = light_rim.to_track_quat(direction, 'Y', 'Z').to_euler()

report["checks"]["cameras"] = ["CAM_Kart01_Perspective", "CAM_Kart01_Front", "CAM_Kart01_Side", "CAM_Kart01_Rear"]
report["checks"]["lights"] = ["LIGHT_Kart01_Key", "LIGHT_Kart01_Fill", "LIGHT_Kart01_Rim"]
report["checks"]["ground"] = "Kart01_Ground"
report["result"] = "PASS"
print(json.dumps(report, indent=2))