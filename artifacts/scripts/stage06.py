import bpy
import json

def run_stage():
    scene = bpy.context.scene

    # Load previous verified scene (worker loads source_job as /job/input.blend)
    bpy.ops.wm.open_mainfile(filepath="/job/input.blend")

    # Get collections
    kart_asset = bpy.data.collections["KART01_ASSET"]
    kart_presentation = bpy.data.collections["KART01_PRESENTATION"]

    # Get Kart01_Root
    root = bpy.data.objects["Kart01_Root"]

    # Parent all asset objects to Kart01_Root
    asset_objects = [
        "Kart01_Chassis", "Kart01_Floor", "Kart01_Bumper_Front", "Kart01_Bumper_Rear",
        "Kart01_SidePod_L", "Kart01_SidePod_R", "Kart01_Axle_Front", "Kart01_Axle_Rear",
        "Kart01_Wheel_FL", "Kart01_Wheel_FR", "Kart01_Wheel_RL", "Kart01_Wheel_RR",
        "Kart01_Seat_Base", "Kart01_Seat_Back", "Kart01_SteeringColumn",
        "Kart01_SteeringWheel", "Kart01_Pedal_L", "Kart01_Pedal_R"
    ]

    for obj_name in asset_objects:
        obj = bpy.data.objects[obj_name]
        obj.parent = root

    # Apply scale on every mesh object
    for obj_name in asset_objects:
        obj = bpy.data.objects[obj_name]
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        obj.select_set(False)

    # Apply rotation on every mesh object (except wheels which may retain local rotation)
    non_wheel_objects = [
        "Kart01_Chassis", "Kart01_Floor", "Kart01_Bumper_Front", "Kart01_Bumper_Rear",
        "Kart01_SidePod_L", "Kart01_SidePod_R", "Kart01_Axle_Front", "Kart01_Axle_Rear",
        "Kart01_Seat_Base", "Kart01_Seat_Back", "Kart01_SteeringColumn",
        "Kart01_SteeringWheel", "Kart01_Pedal_L", "Kart01_Pedal_R"
    ]
    for obj_name in non_wheel_objects:
        obj = bpy.data.objects[obj_name]
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        obj.select_set(False)

    # Reset Kart01_Root transform to ensure it's at origin
    root.location = (0, 0, 0)
    root.rotation_euler = (0, 0, 0)
    root.scale = (1, 1, 1)

    # Save scene
    bpy.ops.wm.save_mainfile(filepath="/job/scene.blend")

    # Verify hierarchy
    for obj_name in asset_objects:
        obj = bpy.data.objects[obj_name]
        assert obj.parent == root, f"{obj_name} not parented to Kart01_Root"

    # Count total triangles
    total_triangles = 0
    for obj_name in asset_objects:
        obj = bpy.data.objects[obj_name]
        evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh = evaluated.to_mesh()
        try:
            mesh.calc_loop_triangles()
            total_triangles += len(mesh.loop_triangles)
        finally:
            evaluated.to_mesh_clear()

    # Verify total budget
    assert total_triangles <= 4500, f"Total triangles {total_triangles} exceeds 4500"

    return {
        "stage": "06",
        "passed": True,
        "hierarchy": "All asset objects parented to Kart01_Root",
        "total_triangles": total_triangles,
        "asset_objects": asset_objects
    }

report = run_stage()
