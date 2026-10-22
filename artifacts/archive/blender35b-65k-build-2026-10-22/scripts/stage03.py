import bpy
import math

def run_stage():
    scene = bpy.context.scene

    # Create front-left wheel
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.17, depth=0.14, location=(0, 0, 0))
    fl_wheel = bpy.context.active_object
    fl_wheel.name = "Kart01_Wheel_FL"
    fl_wheel.scale = (1.0, 1.0, 1.0)
    fl_wheel.location = (-0.46, -0.95, 0.17)
    # Rotate to lie flat on ground
    fl_wheel.rotation_euler = (math.pi / 2, 0, 0)
    scene.collection.children["KART01_ASSET"].objects.link(fl_wheel)

    # Create front-right wheel
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.17, depth=0.14, location=(0, 0, 0))
    fr_wheel = bpy.context.active_object
    fr_wheel.name = "Kart01_Wheel_FR"
    fr_wheel.scale = (1.0, 1.0, 1.0)
    fr_wheel.location = (0.46, -0.95, 0.17)
    fr_wheel.rotation_euler = (math.pi / 2, 0, 0)
    scene.collection.children["KART01_ASSET"].objects.link(fr_wheel)

    # Create rear-left wheel
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.17, depth=0.14, location=(0, 0, 0))
    rl_wheel = bpy.context.active_object
    rl_wheel.name = "Kart01_Wheel_RL"
    rl_wheel.scale = (1.0, 1.0, 1.0)
    rl_wheel.location = (-0.48, 0.85, 0.17)
    rl_wheel.rotation_euler = (math.pi / 2, 0, 0)
    scene.collection.children["KART01_ASSET"].objects.link(rl_wheel)

    # Create rear-right wheel
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.17, depth=0.14, location=(0, 0, 0))
    rr_wheel = bpy.context.active_object
    rr_wheel.name = "Kart01_Wheel_RR"
    rr_wheel.scale = (1.0, 1.0, 1.0)
    rr_wheel.location = (0.48, 0.85, 0.17)
    rr_wheel.rotation_euler = (math.pi / 2, 0, 0)
    scene.collection.children["KART01_ASSET"].objects.link(rr_wheel)

    # Save scene
    bpy.ops.wm.save_as_mainfile(filepath='/job/scene.blend')

    return {
        "wheels": ["Kart01_Wheel_FL", "Kart01_Wheel_FR", "Kart01_Wheel_RL", "Kart01_Wheel_RR"],
        "wheel_radius": 0.17,
        "wheel_depth": 0.14,
        "positions": {
            "FL": (-0.46, -0.95, 0.17),
            "FR": (0.46, -0.95, 0.17),
            "RL": (-0.48, 0.85, 0.17),
            "RR": (0.48, 0.85, 0.17)
        }
    }

report = run_stage()
