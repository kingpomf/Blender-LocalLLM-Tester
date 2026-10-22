import bpy
import math

def run_stage():
    scene = bpy.context.scene

    # Create Kart01_Ground (neutral matte plane at Z=0)
    bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "Kart01_Ground"
    ground.location = (0, 0, -0.01)
    scene.collection.children["KART01_PRESENTATION"].objects.link(ground)

    # Create LIGHT_Kart01_Key
    bpy.ops.object.light_add(type='SUN', location=(3, 0, 6))
    key_light = bpy.context.active_object
    key_light.name = "LIGHT_Kart01_Key"
    key_light.location = (3, 0, 6)
    scene.collection.children["KART01_PRESENTATION"].objects.link(key_light)

    # Create LIGHT_Kart01_Fill
    bpy.ops.object.light_add(type='SUN', location=(-3, 0, 6))
    fill_light = bpy.context.active_object
    fill_light.name = "LIGHT_Kart01_Fill"
    fill_light.location = (-3, 0, 6)
    scene.collection.children["KART01_PRESENTATION"].objects.link(fill_light)

    # Create LIGHT_Kart01_Rim
    bpy.ops.object.light_add(type='SUN', location=(0, -3, 6))
    rim_light = bpy.context.active_object
    rim_light.name = "LIGHT_Kart01_Rim"
    rim_light.location = (0, -3, 6)
    scene.collection.children["KART01_PRESENTATION"].objects.link(rim_light)

    # Create CAM_Kart01_Perspective
    bpy.ops.object.camera_add(location=(2, -2, 1))
    persp_cam = bpy.context.active_object
    persp_cam.name = "CAM_Kart01_Perspective"
    persp_cam.location = (2, -2, 1)
    persp_cam.rotation_euler = (0.5, 0, 0)
    scene.collection.children["KART01_PRESENTATION"].objects.link(persp_cam)
    scene.camera = persp_cam

    # Create CAM_Kart01_Front
    bpy.ops.object.camera_add(location=(0, 1.5, 0.5))
    front_cam = bpy.context.active_object
    front_cam.name = "CAM_Kart01_Front"
    front_cam.location = (0, 1.5, 0.5)
    front_cam.rotation_euler = (0, math.pi, 0)
    scene.collection.children["KART01_PRESENTATION"].objects.link(front_cam)

    # Create CAM_Kart01_Side
    bpy.ops.object.camera_add(location=(1.5, 0, 0.5))
    side_cam = bpy.context.active_object
    side_cam.name = "CAM_Kart01_Side"
    side_cam.location = (1.5, 0, 0.5)
    side_cam.rotation_euler = (0, math.pi / 2, 0)
    scene.collection.children["KART01_PRESENTATION"].objects.link(side_cam)

    # Create CAM_Kart01_Rear
    bpy.ops.object.camera_add(location=(0, -1.5, 0.5))
    rear_cam = bpy.context.active_object
    rear_cam.name = "CAM_Kart01_Rear"
    rear_cam.location = (0, -1.5, 0.5)
    rear_cam.rotation_euler = (0, math.pi, 0)
    scene.collection.children["KART01_PRESENTATION"].objects.link(rear_cam)

    # Save scene
    bpy.ops.wm.save_as_mainfile(filepath='/job/scene.blend')

    return {
        "cameras": ["CAM_Kart01_Perspective", "CAM_Kart01_Front", "CAM_Kart01_Side", "CAM_Kart01_Rear"],
        "lights": ["LIGHT_Kart01_Key", "LIGHT_Kart01_Fill", "LIGHT_Kart01_Rim"],
        "ground": "Kart01_Ground"
    }

report = run_stage()
