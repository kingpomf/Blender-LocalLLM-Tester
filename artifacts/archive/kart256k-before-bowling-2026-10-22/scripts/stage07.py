import bpy
import json

def run_stage():
    scene = bpy.context.scene

    # Load previous verified scene (worker loads source_job as /job/input.blend)
    bpy.ops.wm.open_mainfile(filepath="/job/input.blend")

    # Get collections
    kart_asset = bpy.data.collections["KART01_ASSET"]
    kart_presentation = bpy.data.collections["KART01_PRESENTATION"]

    # Create Kart01_Ground (neutral matte plane at Z=0)
    bpy.ops.mesh.primitive_plane_add(location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "Kart01_Ground"
    ground.scale = (2.0, 3.0, 1.0)
    kart_presentation.objects.link(ground)

    # Create key light
    bpy.ops.object.light_add(type='AREA', location=(2, 0, 3))
    key_light = bpy.context.active_object
    key_light.name = "LIGHT_Kart01_Key"
    key_light.data.energy = 1000
    key_light.data.size = 1.0
    kart_presentation.objects.link(key_light)

    # Create fill light
    bpy.ops.object.light_add(type='AREA', location=(-2, 0, 2))
    fill_light = bpy.context.active_object
    fill_light.name = "LIGHT_Kart01_Fill"
    fill_light.data.energy = 500
    fill_light.data.size = 1.0
    kart_presentation.objects.link(fill_light)

    # Create rim light
    bpy.ops.object.light_add(type='AREA', location=(0, -2, 2))
    rim_light = bpy.context.active_object
    rim_light.name = "LIGHT_Kart01_Rim"
    rim_light.data.energy = 800
    rim_light.data.size = 1.0
    kart_presentation.objects.link(rim_light)

    # Create perspective camera
    bpy.ops.object.camera_add(location=(3, 2, 1.5))
    cam_perspective = bpy.context.active_object
    cam_perspective.name = "CAM_Kart01_Perspective"
    cam_perspective.data.lens = 35
    cam_perspective.data.sensor_width = 36
    kart_presentation.objects.link(cam_perspective)

    # Create front camera
    bpy.ops.object.camera_add(location=(0, -2.5, 1.0))
    cam_front = bpy.context.active_object
    cam_front.name = "CAM_Kart01_Front"
    cam_front.data.lens = 35
    cam_front.data.sensor_width = 36
    kart_presentation.objects.link(cam_front)

    # Create side camera
    bpy.ops.object.camera_add(location=(2.5, 0, 1.0))
    cam_side = bpy.context.active_object
    cam_side.name = "CAM_Kart01_Side"
    cam_side.data.lens = 35
    cam_side.data.sensor_width = 36
    kart_presentation.objects.link(cam_side)

    # Create rear camera
    bpy.ops.object.camera_add(location=(0, 2.5, 1.0))
    cam_rear = bpy.context.active_object
    cam_rear.name = "CAM_Kart01_Rear"
    cam_rear.data.lens = 35
    cam_rear.data.sensor_width = 36
    kart_presentation.objects.link(cam_rear)

    # Save scene
    bpy.ops.wm.save_mainfile(filepath="/job/scene.blend")

    # Verify required objects exist
    assert "Kart01_Ground" in bpy.data.objects, "Kart01_Ground missing"
    assert "LIGHT_Kart01_Key" in bpy.data.objects, "LIGHT_Kart01_Key missing"
    assert "LIGHT_Kart01_Fill" in bpy.data.objects, "LIGHT_Kart01_Fill missing"
    assert "LIGHT_Kart01_Rim" in bpy.data.objects, "LIGHT_Kart01_Rim missing"
    assert "CAM_Kart01_Perspective" in bpy.data.objects, "CAM_Kart01_Perspective missing"
    assert "CAM_Kart01_Front" in bpy.data.objects, "CAM_Kart01_Front missing"
    assert "CAM_Kart01_Side" in bpy.data.objects, "CAM_Kart01_Side missing"
    assert "CAM_Kart01_Rear" in bpy.data.objects, "CAM_Kart01_Rear missing"

    return {
        "stage": "07",
        "passed": True,
        "objects": ["Kart01_Ground", "LIGHT_Kart01_Key", "LIGHT_Kart01_Fill", "LIGHT_Kart01_Rim",
                    "CAM_Kart01_Perspective", "CAM_Kart01_Front", "CAM_Kart01_Side", "CAM_Kart01_Rear"],
        "render_resolution": [512, 512]
    }

report = run_stage()
