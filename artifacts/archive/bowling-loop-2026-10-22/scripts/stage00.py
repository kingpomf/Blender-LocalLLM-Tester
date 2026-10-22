import bpy
import json
from typing import cast

def run_stage():
    # Stage 00: Create scene foundation for BowlingPair01
    # Start with fresh isolated zero-object scene (no source_job)
    # Create collections and root object as specified in 00-CONTRACT.md

    scene = cast(bpy.types.Scene, bpy.context.scene)

    # Set metric units, scale 1, meters; Blender X/Y ground plane, Z up
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0

    # Create the root object at origin (midway between lanes at foul line,
    # lane surface height)
    root_data = bpy.data.objects.new("BowlingPair01_ROOT", None)
    root_data.location = [0.0, 0.0, 0.0]
    root_data.rotation_euler = [0.0, 0.0, 0.0]
    root_data.scale = [1.0, 1.0, 1.0]

    # Create required collections
    collections = [
        "BP01_STATIC",
        "BP01_PINS",
        "BP01_BALLS",
        "BP01_COLLISION",
        "BP01_PRESENTATION"
    ]

    for name in collections:
        if name not in bpy.data.collections:
            bpy.data.collections.new(name)

    # Link root to scene
    bpy.context.scene.collection.objects.link(root_data)

    # Verify the scene state
    result = {
        "collections": collections,
        "units": scene.unit_settings.system,
        "unit_scale": scene.unit_settings.scale_length,
        "root_name": root_data.name,
        "root_location": list(root_data.location),
        "root_rotation": list(root_data.rotation_euler),
        "root_scale": list(root_data.scale),
        "object_count": len(bpy.data.objects),
        "collection_count": len(bpy.data.collections)
    }

    return result

report = run_stage()