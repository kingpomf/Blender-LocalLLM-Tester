import bpy

# Clear default objects
for obj in bpy.data.objects:
    bpy.data.objects.remove(obj, do_unlink=True)

# Set metric units
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0

# Create collections
collections = {}
for name in ['BP01_STATIC', 'BP01_PINS', 'BP01_BALLS', 'BP01_COLLISION', 'BP01_PRESENTATION']:
    coll = bpy.data.collections.new(name)
    scene.collection.children.link(coll)
    collections[name] = coll

# Create root empty at origin with identity transform
root = bpy.data.objects.new('BowlingPair01_ROOT', None)
root.location = (0.0, 0.0, 0.0)
root.rotation_euler = (0.0, 0.0, 0.0)
root.scale = (1.0, 1.0, 1.0)
scene.collection.objects.link(root)

# Parent static collection to root
collections['BP01_STATIC'].parent = root
collections['BP01_PINS'].parent = root
collections['BP01_BALLS'].parent = root
# BP01_COLLISION and BP01_PRESENTATION stay at scene root (not exported with visual root)

report = {
    "stage": "stage00_setup",
    "root_name": "BowlingPair01_ROOT",
    "root_location": [0.0, 0.0, 0.0],
    "root_scale": [1.0, 1.0, 1.0],
    "collections_created": list(collections.keys()),
    "unit_system": "METRIC",
    "unit_scale": 1.0
}