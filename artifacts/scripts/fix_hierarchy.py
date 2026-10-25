import bpy

root_name = "BowlingPair01_ROOT"
root = bpy.data.objects.get(root_name)
if root is None:
    root = bpy.data.objects.new(root_name, None)
    bpy.context.scene.collection.objects.link(root)

objects_to_parent = []
for obj in bpy.context.scene.objects:
    if obj == root:
        continue
    if obj.type == 'MESH' or obj.type == 'EMPTY':
        objects_to_parent.append(obj)

for obj in objects_to_parent:
    obj.parent = root

report = {
    "objects_parented": len(objects_to_parent),
    "root": root_name,
    "names": [o.name for o in objects_to_parent]
}