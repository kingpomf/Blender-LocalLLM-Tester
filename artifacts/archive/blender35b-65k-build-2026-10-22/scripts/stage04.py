import bpy
import math

def run_stage():
    scene = bpy.context.scene

    # Create seat base (rectangular box)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    seat_base = bpy.context.active_object
    seat_base.name = "Kart01_SeatBase"
    seat_base.scale = (0.5, 0.4, 0.08)
    seat_base.location = (0, -0.15, 0.22)
    scene.collection.children["KART01_ASSET"].objects.link(seat_base)

    # Create seat back (angled box)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    seat_back = bpy.context.active_object
    seat_back.name = "Kart01_SeatBack"
    seat_back.scale = (0.5, 0.35, 0.4)
    seat_back.location = (0, -0.25, 0.42)
    seat_back.rotation_euler = (0.1, 0, 0)
    scene.collection.children["KART01_ASSET"].objects.link(seat_back)

    # Create steering column (cylinder)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.02, depth=0.3, location=(0, 0, 0))
    steering_col = bpy.context.active_object
    steering_col.name = "Kart01_SteeringColumn"
    steering_col.scale = (1.0, 1.0, 1.0)
    steering_col.location = (0, -0.7, 0.35)
    steering_col.rotation_euler = (0.5, 0, 0)
    scene.collection.children["KART01_ASSET"].objects.link(steering_col)

    # Create steering wheel (torus approximation)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.1, minor_radius=0.02, location=(0, 0, 0))
    steering_wheel = bpy.context.active_object
    steering_wheel.name = "Kart01_SteeringWheel"
    steering_wheel.scale = (1.0, 1.0, 1.0)
    steering_wheel.location = (0, -0.7, 0.5)
    steering_wheel.rotation_euler = (0, 0.5, 0)
    scene.collection.children["KART01_ASSET"].objects.link(steering_wheel)

    # Create left pedal (small box)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    pedal_l = bpy.context.active_object
    pedal_l.name = "Kart01_Pedal_L"
    pedal_l.scale = (0.08, 0.04, 0.015)
    pedal_l.location = (0.05, -0.55, 0.18)
    scene.collection.children["KART01_ASSET"].objects.link(pedal_l)

    # Create right pedal (small box)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    pedal_r = bpy.context.active_object
    pedal_r.name = "Kart01_Pedal_R"
    pedal_r.scale = (0.08, 0.04, 0.015)
    pedal_r.location = (-0.05, -0.55, 0.18)
    scene.collection.children["KART01_ASSET"].objects.link(pedal_r)

    # Save scene
    bpy.ops.wm.save_as_mainfile(filepath='/job/scene.blend')

    return {
        "objects": ["Kart01_SeatBase", "Kart01_SeatBack", "Kart01_SteeringColumn",
                   "Kart01_SteeringWheel", "Kart01_Pedal_L", "Kart01_Pedal_R"],
        "seat_center": (0, -0.15, 0.22),
        "steering_center": (0, -0.7, 0.5)
    }

report = run_stage()
