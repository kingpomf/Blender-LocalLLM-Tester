import bpy

root = bpy.data.objects["BowlingPair01_ROOT"]
static_col = bpy.data.collections.get("BP01_STATIC")

for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue
    name = obj.name
    if name.startswith("FoulLine") or name.startswith("ArrowTri") or name.startswith("Dot_"):
        bpy.context.scene.collection.objects.unlink(obj)
        if static_col:
            static_col.objects.link(obj)
        obj.parent = root

report = {"moved_to_static": True}