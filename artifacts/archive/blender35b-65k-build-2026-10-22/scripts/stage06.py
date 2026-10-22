import bpy
import math

def run_stage():
    scene = bpy.context.scene

    # Set Kart01_Root transform
    root = bpy.data.objects["Kart01_Root"]
    root.location = (0, 0, 0)
    root.rotation_euler = (0, 0, 0)
    root.scale = (1, 1, 1)

    # Parent all asset objects to Kart01_Root
    asset_objects = [
        "Kart01_Chassis", "Kart01_Floor", "Kart01_Bumper_Front", "Kart01_Bumper_Rear",
        "Kart01_SidePod_L", "Kart01_SidePod_R", "Kart01_Wheel_FL", "Kart01_Wheel_FR",
        "Kart01_Wheel_RL", "Kart01_Wheel_RR", "Kart01_SeatBase", "Kart01_SeatBack",
        "Kart01_SteeringColumn", "Kart01_SteeringWheel", "Kart01_Pedal_L", "Kart01_Pedal_R"
    ]

    for obj_name in asset_objects:
        obj = bpy.data.objects[obj_name]
        obj.parent = root
        # Apply transform to object
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Save scene
    bpy.ops.wm.save_as_mainfile(filepath='/job/scene.blend')

    return {
        "root": "Kart01_Root",
        "parented_objects": asset_objects,
        "total_objects": len(asset_objects)
    }

report = run_stage()
