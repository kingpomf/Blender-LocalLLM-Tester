import bpy
import json


def run_stage():
    """Stage 00: Contract and scene safety — create collections and root for BowlingPair01."""

    # 1. Scene setup: metric units, unit scale 1, meters
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0

    # Verify units
    assert scene.unit_settings.system == 'METRIC', "Scene units must be METRIC"
    assert scene.unit_settings.scale_length == 1.0, "Unit scale must be 1.0"

    # 2. Create collections
    collections = {
        'BP01_STATIC': bpy.data.collections.new('BP01_STATIC'),
        'BP01_PINS': bpy.data.collections.new('BP01_PINS'),
        'BP01_BALLS': bpy.data.collections.new('BP01_BALLS'),
        'BP01_COLLISION': bpy.data.collections.new('BP01_COLLISION'),
        'BP01_PRESENTATION': bpy.data.collections.new('BP01_PRESENTATION'),
    }

    # Link collections to scene
    for name, collection in collections.items():
        scene.collection.children.link(collection)

    # 3. Create empty root object at origin
    root = bpy.data.objects.new('BowlingPair01_ROOT', None)
    root.location = (0.0, 0.0, 0.0)
    root.rotation_euler = (0.0, 0.0, 0.0)
    root.scale = (1.0, 1.0, 1.0)
    scene.collection.objects.link(root)

    # 5. Report
    report = {
        'stage': '00',
        'name': 'Contract and scene safety',
        'passed': True,
        'collections': list(collections.keys()),
        'units': scene.unit_settings.system,
        'unit_scale': scene.unit_settings.scale_length,
        'root_name': root.name,
        'root_location': [root.location.x, root.location.y, root.location.z],
        'root_scale': [root.scale.x, root.scale.y, root.scale.z],
        'root_rotation': [root.rotation_euler.x, root.rotation_euler.y, root.rotation_euler.z],
        'scene_objects': len(scene.objects),
        'collection_count': len(collections),
    }

    return report


report = run_stage()
