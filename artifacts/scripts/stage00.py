import bpy
import json

def run_stage():
    scene = bpy.context.scene

    # Remove default cube, camera, and light (empty scene means zero objects)
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for cam in list(bpy.data.cameras):
        bpy.data.cameras.remove(cam)
    for light in list(bpy.data.lights):
        bpy.data.lights.remove(light)

    # Create required collections
    kart_asset = bpy.data.collections.new("KART01_ASSET")
    bpy.context.scene.collection.children.link(kart_asset)
    kart_presentation = bpy.data.collections.new("KART01_PRESENTATION")
    bpy.context.scene.collection.children.link(kart_presentation)

    # Set units to Metric with scale 1.0
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0

    # Save scene
    bpy.ops.wm.save_mainfile(filepath="/job/scene.blend")

    # Verify collections exist
    assert "KART01_ASSET" in bpy.data.collections, "KART01_ASSET collection missing"
    assert "KART01_PRESENTATION" in bpy.data.collections, "KART01_PRESENTATION collection missing"
    assert len(bpy.data.objects) == 0, f"Expected 0 objects after cleanup, found {len(bpy.data.objects)}"
    assert scene.unit_settings.system == 'METRIC', "Units not METRIC"
    assert scene.unit_settings.scale_length == 1.0, "Unit scale not 1.0"

    return {
        "stage": "00",
        "passed": True,
        "collections": ["KART01_ASSET", "KART01_PRESENTATION"],
        "units": "METRIC",
        "unit_scale": 1.0,
        "object_count": 0
    }

report = run_stage()
