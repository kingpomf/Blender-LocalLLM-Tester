import bpy
import json

def run_stage():
    scene = bpy.context.scene

    # Load previous verified scene (worker loads source_job as /job/input.blend)
    bpy.ops.wm.open_mainfile(filepath="/job/input.blend")

    # Get collections
    kart_asset = bpy.data.collections["KART01_ASSET"]
    kart_presentation = bpy.data.collections["KART01_PRESENTATION"]

    # Create reference guides for Stage 01 dimensions using cube primitives
    # X width reference (1.20m) - a cube scaled to 1.2 x 0.1 x 0.1
    bpy.ops.mesh.primitive_cube_add(location=(0.6, 0, 0))
    x_obj = bpy.context.active_object
    x_obj.name = "REF_X_Width"
    x_obj.scale = (1.2, 0.1, 0.1)
    x_obj.location = (0.6, 0, 0)
    kart_presentation.objects.link(x_obj)

    # Y length reference (1.80m) - a cube scaled to 0.1 x 1.8 x 0.1
    bpy.ops.mesh.primitive_cube_add(location=(0, 0.9, 0))
    y_obj = bpy.context.active_object
    y_obj.name = "REF_Y_Length"
    y_obj.scale = (0.1, 1.8, 0.1)
    y_obj.location = (0, 0.9, 0)
    kart_presentation.objects.link(y_obj)

    # Z height reference (1.05m) - a cube scaled to 0.1 x 0.1 x 1.05
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0.525))
    z_obj = bpy.context.active_object
    z_obj.name = "REF_Z_Height"
    z_obj.scale = (0.1, 0.1, 1.05)
    z_obj.location = (0, 0, 0.525)
    kart_presentation.objects.link(z_obj)

    # Save scene
    bpy.ops.wm.save_mainfile(filepath="/job/scene.blend")

    # Verify reference guides exist
    assert "REF_X_Width" in bpy.data.objects, "REF_X_Width missing"
    assert "REF_Y_Length" in bpy.data.objects, "REF_Y_Length missing"
    assert "REF_Z_Height" in bpy.data.objects, "REF_Z_Height missing"

    return {
        "stage": "01",
        "passed": True,
        "reference_guides": ["REF_X_Width", "REF_Y_Length", "REF_Z_Height"],
        "envelope": {"x": 1.2, "y": 1.8, "z": 1.05},
        "wheelbase": 1.1,
        "front_track": 0.92,
        "rear_track": 0.96,
        "wheel_diameter": 0.34,
        "wheel_width": 0.14
    }

report = run_stage()
