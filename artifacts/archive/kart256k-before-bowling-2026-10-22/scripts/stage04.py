import bpy
import json

def run_stage():
    scene = bpy.context.scene

    # Load previous verified scene (worker loads source_job as /job/input.blend)
    bpy.ops.wm.open_mainfile(filepath="/job/input.blend")

    # Get collections
    kart_asset = bpy.data.collections["KART01_ASSET"]
    kart_presentation = bpy.data.collections["KART01_PRESENTATION"]

    # Create seat (centered on X=0, rear half of kart)
    # Seat base
    bpy.ops.mesh.primitive_cube_add(location=(0, 0.2, 0.3))
    seat_base = bpy.context.active_object
    seat_base.name = "Kart01_Seat_Base"
    seat_base.scale = (0.35, 0.3, 0.05)
    seat_base.location = (0, 0.2, 0.3)
    kart_asset.objects.link(seat_base)

    # Seat back
    bpy.ops.mesh.primitive_cube_add(location=(0, 0.35, 0.5))
    seat_back = bpy.context.active_object
    seat_back.name = "Kart01_Seat_Back"
    seat_back.scale = (0.35, 0.05, 0.35)
    seat_back.location = (0, 0.35, 0.5)
    kart_asset.objects.link(seat_back)

    # Create steering column (points from front-center chassis toward driver)
    bpy.ops.mesh.primitive_cylinder_add(location=(0, -0.5, 0.4))
    steering_col = bpy.context.active_object
    steering_col.name = "Kart01_SteeringColumn"
    steering_col.scale = (0.02, 0.02, 0.15)
    steering_col.location = (0, -0.5, 0.4)
    kart_asset.objects.link(steering_col)

    # Create steering wheel (simple ring approximation)
    bpy.ops.mesh.primitive_torus_add(location=(0, -0.7, 0.55), major_radius=0.08, minor_radius=0.02)
    steering_wheel = bpy.context.active_object
    steering_wheel.name = "Kart01_SteeringWheel"
    steering_wheel.location = (0, -0.7, 0.55)
    kart_asset.objects.link(steering_wheel)

    # Create left pedal (ahead of seat, above floor)
    bpy.ops.mesh.primitive_cube_add(location=(-0.1, -0.8, 0.2))
    pedal_l = bpy.context.active_object
    pedal_l.name = "Kart01_Pedal_L"
    pedal_l.scale = (0.08, 0.15, 0.02)
    pedal_l.location = (-0.1, -0.8, 0.2)
    kart_asset.objects.link(pedal_l)

    # Create right pedal (ahead of seat, above floor)
    bpy.ops.mesh.primitive_cube_add(location=(0.1, -0.8, 0.2))
    pedal_r = bpy.context.active_object
    pedal_r.name = "Kart01_Pedal_R"
    pedal_r.scale = (0.08, 0.15, 0.02)
    pedal_r.location = (0.1, -0.8, 0.2)
    kart_asset.objects.link(pedal_r)

    # Save scene
    bpy.ops.wm.save_mainfile(filepath="/job/scene.blend")

    # Verify required objects exist
    assert "Kart01_Seat_Base" in bpy.data.objects, "Kart01_Seat_Base missing"
    assert "Kart01_Seat_Back" in bpy.data.objects, "Kart01_Seat_Back missing"
    assert "Kart01_SteeringColumn" in bpy.data.objects, "Kart01_SteeringColumn missing"
    assert "Kart01_SteeringWheel" in bpy.data.objects, "Kart01_SteeringWheel missing"
    assert "Kart01_Pedal_L" in bpy.data.objects, "Kart01_Pedal_L missing"
    assert "Kart01_Pedal_R" in bpy.data.objects, "Kart01_Pedal_R missing"

    return {
        "stage": "04",
        "passed": True,
        "objects": ["Kart01_Seat_Base", "Kart01_Seat_Back", "Kart01_SteeringColumn", "Kart01_SteeringWheel", "Kart01_Pedal_L", "Kart01_Pedal_R"],
        "seat_position": (0, 0.2, 0.3),
        "steering_position": (0, -0.7, 0.55)
    }

report = run_stage()
