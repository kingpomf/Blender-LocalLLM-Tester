import bpy
import math

def run_stage():
    scene = bpy.context.scene

    # Create Kart01_Root at world origin
    root = bpy.data.objects.new("Kart01_Root", None)
    root.location = (0, 0, 0)
    root.rotation_euler = (0, 0, 0)
    root.scale = (1, 1, 1)
    scene.collection.objects.link(root)
    scene.collection.children["KART01_ASSET"].objects.link(root)

    # Create main chassis body - tapered shape
    # Front nose narrower than rear body
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.25))
    chassis = bpy.context.active_object
    chassis.name = "Kart01_Chassis"
    chassis.scale = (0.6, 1.0, 0.1)
    # Set position: front at -Y, rear at +Y
    chassis.location = (0, -0.05, 0.25)
    scene.collection.children["KART01_ASSET"].objects.link(chassis)

    # Create floor - flat driver floor
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Kart01_Floor"
    floor.scale = (0.7, 1.1, 0.05)
    floor.location = (0, -0.05, 0.17)
    scene.collection.children["KART01_ASSET"].objects.link(floor)

    # Create front bumper
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    bumper_f = bpy.context.active_object
    bumper_f.name = "Kart01_Bumper_Front"
    bumper_f.scale = (0.65, 0.08, 0.1)
    bumper_f.location = (0, -0.95, 0.15)
    scene.collection.children["KART01_ASSET"].objects.link(bumper_f)

    # Create rear bumper
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    bumper_r = bpy.context.active_object
    bumper_r.name = "Kart01_Bumper_Rear"
    bumper_r.scale = (0.65, 0.08, 0.1)
    bumper_r.location = (0, 0.85, 0.15)
    scene.collection.children["KART01_ASSET"].objects.link(bumper_r)

    # Create left side pod
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    pod_l = bpy.context.active_object
    pod_l.name = "Kart01_SidePod_L"
    pod_l.scale = (0.08, 0.9, 0.15)
    pod_l.location = (-0.55, -0.05, 0.25)
    scene.collection.children["KART01_ASSET"].objects.link(pod_l)

    # Create right side pod (mirrored)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    pod_r = bpy.context.active_object
    pod_r.name = "Kart01_SidePod_R"
    pod_r.scale = (0.08, 0.9, 0.15)
    pod_r.location = (0.55, -0.05, 0.25)
    scene.collection.children["KART01_ASSET"].objects.link(pod_r)

    # Save scene
    bpy.ops.wm.save_as_mainfile(filepath='/job/scene.blend')

    return {
        "objects": ["Kart01_Root", "Kart01_Chassis", "Kart01_Floor",
                    "Kart01_Bumper_Front", "Kart01_Bumper_Rear",
                    "Kart01_SidePod_L", "Kart01_SidePod_R"],
        "triangle_budget": 1500
    }

report = run_stage()
