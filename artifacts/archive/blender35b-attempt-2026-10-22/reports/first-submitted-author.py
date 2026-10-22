import bpy
import json

def run_stage():
    # Clean default objects
    bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)
    bpy.data.objects.remove(bpy.data.objects["Camera"], do_unlink=True)
    bpy.data.objects.remove(bpy.data.objects["Light"], do_unlink=True)

    # Create required collections
    kart_asset = bpy.data.collections.new("KART01_ASSET")
    bpy.scene.collection.children.link(kart_asset)

    kart_presentation = bpy.data.collections.new("KART01_PRESENTATION")
    bpy.scene.collection.children.link(kart_presentation)

    # Set units
    bpy.scene.unit_settings.system = 'METRIC'
    bpy.scene.unit_settings.scale_length = 1.0

    # Save blend
    bpy.ops.wm.save_as_mainfile(filepath="/job/Kart01.blend")

    report = {
        "stage": 0,
        "passed": True,
        "collections": ["KART01_ASSET", "KART01_PRESENTATION"],
        "units": "METRIC",
        "scale": 1.0
    }
    return report

report = run_stage()