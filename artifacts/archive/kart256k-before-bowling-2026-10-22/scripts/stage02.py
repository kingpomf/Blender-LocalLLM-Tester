import bpy
import json

def run_stage():
    scene = bpy.context.scene

    # Load previous verified scene (worker loads source_job as /job/input.blend)
    bpy.ops.wm.open_mainfile(filepath="/job/input.blend")

    # Get collections
    kart_asset = bpy.data.collections["KART01_ASSET"]
    kart_presentation = bpy.data.collections["KART01_PRESENTATION"]

    # Create Kart01_Root empty at world origin
    bpy.ops.object.empty_add(location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "Kart01_Root"
    root.location = (0, 0, 0)
    kart_asset.objects.link(root)

    # Create main chassis (centered on X=0, Z>=0.17m)
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0.35))
    chassis = bpy.context.active_object
    chassis.name = "Kart01_Chassis"
    chassis.scale = (0.5, 0.8, 0.15)
    chassis.location = (0, 0, 0.35)
    kart_asset.objects.link(chassis)

    # Create floor (spans driver foot and seat area)
    bpy.ops.mesh.primitive_cube_add(location=(0, -0.2, 0.175))
    floor = bpy.context.active_object
    floor.name = "Kart01_Floor"
    floor.scale = (0.45, 0.7, 0.025)
    floor.location = (0, -0.2, 0.175)
    kart_asset.objects.link(floor)

    # Create front bumper (rounded rectangular)
    bpy.ops.mesh.primitive_cube_add(location=(0, -0.9, 0.2))
    bumper_front = bpy.context.active_object
    bumper_front.name = "Kart01_Bumper_Front"
    bumper_front.scale = (0.4, 0.05, 0.15)
    bumper_front.location = (0, -0.9, 0.2)
    kart_asset.objects.link(bumper_front)

    # Create rear bumper (rounded rectangular)
    bpy.ops.mesh.primitive_cube_add(location=(0, 0.8, 0.2))
    bumper_rear = bpy.context.active_object
    bumper_rear.name = "Kart01_Bumper_Rear"
    bumper_rear.scale = (0.4, 0.05, 0.15)
    bumper_rear.location = (0, 0.8, 0.2)
    kart_asset.objects.link(bumper_rear)

    # Create left side pod (mirrored position)
    bpy.ops.mesh.primitive_cube_add(location=(-0.45, 0, 0.25))
    side_pod_l = bpy.context.active_object
    side_pod_l.name = "Kart01_SidePod_L"
    side_pod_l.scale = (0.05, 0.75, 0.15)
    side_pod_l.location = (-0.45, 0, 0.25)
    kart_asset.objects.link(side_pod_l)

    # Create right side pod (mirrored position)
    bpy.ops.mesh.primitive_cube_add(location=(0.45, 0, 0.25))
    side_pod_r = bpy.context.active_object
    side_pod_r.name = "Kart01_SidePod_R"
    side_pod_r.scale = (0.05, 0.75, 0.15)
    side_pod_r.location = (0.45, 0, 0.25)
    kart_asset.objects.link(side_pod_r)

    # Save scene
    bpy.ops.wm.save_mainfile(filepath="/job/scene.blend")

    # Verify required objects exist
    assert "Kart01_Root" in bpy.data.objects, "Kart01_Root missing"
    assert "Kart01_Chassis" in bpy.data.objects, "Kart01_Chassis missing"
    assert "Kart01_Floor" in bpy.data.objects, "Kart01_Floor missing"
    assert "Kart01_Bumper_Front" in bpy.data.objects, "Kart01_Bumper_Front missing"
    assert "Kart01_Bumper_Rear" in bpy.data.objects, "Kart01_Bumper_Rear missing"
    assert "Kart01_SidePod_L" in bpy.data.objects, "Kart01_SidePod_L missing"
    assert "Kart01_SidePod_R" in bpy.data.objects, "Kart01_SidePod_R missing"

    return {
        "stage": "02",
        "passed": True,
        "objects": ["Kart01_Root", "Kart01_Chassis", "Kart01_Floor", "Kart01_Bumper_Front", "Kart01_Bumper_Rear", "Kart01_SidePod_L", "Kart01_SidePod_R"],
        "chassis_z": 0.35,
        "floor_z": 0.175
    }

report = run_stage()
