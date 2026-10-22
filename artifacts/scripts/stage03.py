import bpy
import json

def run_stage():
    scene = bpy.context.scene

    # Load previous verified scene (worker loads source_job as /job/input.blend)
    bpy.ops.wm.open_mainfile(filepath="/job/input.blend")

    # Get collections
    kart_asset = bpy.data.collections["KART01_ASSET"]
    kart_presentation = bpy.data.collections["KART01_PRESENTATION"]

    # Create front axle (along X axis, at front of kart)
    bpy.ops.mesh.primitive_cylinder_add(location=(0, -0.55, 0.175))
    axle_front = bpy.context.active_object
    axle_front.name = "Kart01_Axle_Front"
    axle_front.scale = (0.46, 0.46, 0.025)
    axle_front.location = (0, -0.55, 0.175)
    kart_asset.objects.link(axle_front)

    # Create rear axle (along X axis, at rear of kart)
    bpy.ops.mesh.primitive_cylinder_add(location=(0, 0.55, 0.175))
    axle_rear = bpy.context.active_object
    axle_rear.name = "Kart01_Axle_Rear"
    axle_rear.scale = (0.48, 0.48, 0.025)
    axle_rear.location = (0, 0.55, 0.175)
    kart_asset.objects.link(axle_rear)

    # Create front-left wheel (at X=-0.46, Y=-0.9)
    bpy.ops.mesh.primitive_cylinder_add(location=(-0.46, -0.9, 0.17))
    wheel_fl = bpy.context.active_object
    wheel_fl.name = "Kart01_Wheel_FL"
    wheel_fl.scale = (0.07, 0.07, 0.17)
    wheel_fl.location = (-0.46, -0.9, 0.17)
    kart_asset.objects.link(wheel_fl)

    # Create front-right wheel (at X=0.46, Y=-0.9)
    bpy.ops.mesh.primitive_cylinder_add(location=(0.46, -0.9, 0.17))
    wheel_fr = bpy.context.active_object
    wheel_fr.name = "Kart01_Wheel_FR"
    wheel_fr.scale = (0.07, 0.07, 0.17)
    wheel_fr.location = (0.46, -0.9, 0.17)
    kart_asset.objects.link(wheel_fr)

    # Create rear-left wheel (at X=-0.48, Y=0.8)
    bpy.ops.mesh.primitive_cylinder_add(location=(-0.48, 0.8, 0.17))
    wheel_rl = bpy.context.active_object
    wheel_rl.name = "Kart01_Wheel_RL"
    wheel_rl.scale = (0.07, 0.07, 0.17)
    wheel_rl.location = (-0.48, 0.8, 0.17)
    kart_asset.objects.link(wheel_rl)

    # Create rear-right wheel (at X=0.48, Y=0.8)
    bpy.ops.mesh.primitive_cylinder_add(location=(0.48, 0.8, 0.17))
    wheel_rr = bpy.context.active_object
    wheel_rr.name = "Kart01_Wheel_RR"
    wheel_rr.scale = (0.07, 0.07, 0.17)
    wheel_rr.location = (0.48, 0.8, 0.17)
    kart_asset.objects.link(wheel_rr)

    # Save scene
    bpy.ops.wm.save_mainfile(filepath="/job/scene.blend")

    # Verify required objects exist
    assert "Kart01_Axle_Front" in bpy.data.objects, "Kart01_Axle_Front missing"
    assert "Kart01_Axle_Rear" in bpy.data.objects, "Kart01_Axle_Rear missing"
    assert "Kart01_Wheel_FL" in bpy.data.objects, "Kart01_Wheel_FL missing"
    assert "Kart01_Wheel_FR" in bpy.data.objects, "Kart01_Wheel_FR missing"
    assert "Kart01_Wheel_RL" in bpy.data.objects, "Kart01_Wheel_RL missing"
    assert "Kart01_Wheel_RR" in bpy.data.objects, "Kart01_Wheel_RR missing"

    return {
        "stage": "03",
        "passed": True,
        "objects": ["Kart01_Axle_Front", "Kart01_Axle_Rear", "Kart01_Wheel_FL", "Kart01_Wheel_FR", "Kart01_Wheel_RL", "Kart01_Wheel_RR"],
        "wheelbase": 1.1,
        "front_track": 0.92,
        "rear_track": 0.96,
        "wheel_diameter": 0.34,
        "wheel_width": 0.14
    }

report = run_stage()
