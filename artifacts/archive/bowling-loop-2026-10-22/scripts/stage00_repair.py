import bpy
import bmesh
import json

def run_stage():
    # Use scene = bpy.context.scene, not bpy.scene
    scene = bpy.context.scene
    view_layer = bpy.context.view_layer

    # Set metric units with scale 1 (meters)
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0

    # Create required collections
    collections = [
        'BP01_STATIC',
        'BP01_PINS',
        'BP01_BALLS',
        'BP01_COLLISION',
        'BP01_PRESENTATION'
    ]

    # Create collection objects
    for name in collections:
        col = bpy.data.collections.new(name)
        # Link collection into scene.collection.children
        scene.collection.children.link(col)

    # Create empty root at origin
    root = bpy.data.objects.new('BowlingPair01_ROOT', None)
    root.location = (0.0, 0.0, 0.0)
    root.rotation_euler = (0.0, 0.0, 0.0)
    root.scale = (1.0, 1.0, 1.0)
    # Link root into scene.collection
    scene.collection.objects.link(root)

    # Verify collections are linked
    linked_names = [c.name for c in scene.collection.children]
    for name in collections:
        assert name in linked_names, f"Collection {name} not linked into scene"

    # Verify root is in scene.collection
    assert 'BowlingPair01_ROOT' in [o.name for o in scene.collection.objects]

    # Verify units
    assert scene.unit_settings.system == 'METRIC', "Units not METRIC"
    assert scene.unit_settings.scale_length == 1.0, "Unit scale not 1.0"

    report = {
        "passed": True,
        "collections": collections,
        "root_name": "BowlingPair01_ROOT",
        "units": scene.unit_settings.system,
        "unit_scale": scene.unit_settings.scale_length,
        "message": "Collections linked, root created, metric units set"
    }
    return report

report = run_stage()
