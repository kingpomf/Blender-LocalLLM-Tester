import bpy
import math

def run_stage():
    scene = bpy.context.scene

    # Create reference guides for coordinate system and dimensions
    # These help visualize the envelope and key dimensions

    # Ground plane reference (X/Y plane at Z=0) - use a proper plane primitive
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "REF_Ground"
    ground.scale = (1.2, 1.8, 1.0)
    scene.collection.children["KART01_PRESENTATION"].objects.link(ground)

    # X axis reference (red line along X)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.6, 0, 0.01))
    x_axis = bpy.context.active_object
    x_axis.name = "REF_X_Axis"
    x_axis.scale = (1.2, 0.02, 0.02)
    scene.collection.children["KART01_PRESENTATION"].objects.link(x_axis)

    # Y axis reference (green line along Y)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.9, 0.01))
    y_axis = bpy.context.active_object
    y_axis.name = "REF_Y_Axis"
    y_axis.scale = (0.02, 1.8, 0.02)
    scene.collection.children["KART01_PRESENTATION"].objects.link(y_axis)

    # Z axis reference (blue line along Z)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.525))
    z_axis = bpy.context.active_object
    z_axis.name = "REF_Z_Axis"
    z_axis.scale = (0.02, 0.02, 1.05)
    scene.collection.children["KART01_PRESENTATION"].objects.link(z_axis)

    # Save scene
    bpy.ops.wm.save_as_mainfile(filepath='/job/scene.blend')

    return {
        "reference_guides": ["REF_Ground", "REF_X_Axis", "REF_Y_Axis", "REF_Z_Axis"],
        "envelope": {"x_max": 1.2, "y_max": 1.8, "z_max": 1.05},
        "wheelbase": 1.1,
        "front_track": 0.92,
        "rear_track": 0.96,
        "wheel_diameter": 0.34,
        "wheel_width": 0.14
    }

report = run_stage()
