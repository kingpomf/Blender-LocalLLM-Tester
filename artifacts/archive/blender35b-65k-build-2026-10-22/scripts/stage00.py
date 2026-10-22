import bpy

def run_stage():
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0

    # Create required collections
    asset_coll = bpy.data.collections.new('KART01_ASSET')
    scene.collection.children.link(asset_coll)

    presentation_coll = bpy.data.collections.new('KART01_PRESENTATION')
    scene.collection.children.link(presentation_coll)

    # Save scene
    bpy.ops.wm.save_as_mainfile(filepath='/job/scene.blend')

    return {
        "collections": ["KART01_ASSET", "KART01_PRESENTATION"],
        "units": "METRIC",
        "unit_scale": 1.0
    }

report = run_stage()
