import bpy
import json

sc = bpy.context.scene
report = {
    "stage": "06",
    "phase": "hierarchy_and_transforms",
    "source_job": "52988f0f148c43ad8fa5924ee7d0a7a3",
    "checks": {}
}

asset_coll = bpy.data.collections.get("KART01_ASSET")
root = bpy.data.objects.get("Kart01_Root")
assert asset_coll is not None, "KART01_ASSET missing"
assert root is not None, "Kart01_Root missing"

# Verify root transforms
report["checks"]["root_location"] = [round(c, 3) for c in root.location]
report["checks"]["root_rotation"] = [round(c, 3) for c in root.rotation_euler]
report["checks"]["root_scale"] = [round(c, 3) for c in root.scale]
assert all(abs(c) < 0.001 for c in root.location), "Root not at origin"
assert all(abs(c) < 0.001 for c in root.rotation_euler), "Root has rotation"
assert all(abs(c - 1.0) < 0.001 for c in root.scale), "Root has scale"

# Apply transforms to all mesh objects
for obj in asset_coll.objects:
    if obj.type == 'MESH':
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        obj.select_set(False)

# Verify evaluated scales are (1,1,1)
scale_ok = True
for obj in asset_coll.objects:
    if obj.type == 'MESH':
        deps = bpy.context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(deps)
        for c in eval_obj.scale:
            if abs(c - 1.0) > 0.001:
                scale_ok = False
                report["checks"]["scale_issue"] = obj.name
                break

report["checks"]["all_scales_applied"] = scale_ok

# Check for duplicate suffixes
dup_names = [o.name for o in asset_coll.objects if ".00" in o.name]
report["checks"]["duplicate_suffixes"] = dup_names
assert not dup_names, f"Duplicate suffixes found: {dup_names}"

# Count total triangles
total_tris = 0
for obj in asset_coll.objects:
    if obj.type == 'MESH':
        deps = bpy.context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(deps)
        mesh = eval_obj.to_mesh()
        total_tris += len(mesh.polygons)
        eval_obj.to_mesh_clear()

report["checks"]["total_triangles"] = total_tris
assert total_tris <= 4500, f"Total triangle budget exceeded: {total_tris}"

# Verify hierarchy - all asset objects should be children of root (directly or indirectly)
hierarchy_ok = True
for obj in asset_coll.objects:
    parent = obj.parent
    while parent is not None:
        if parent == root:
            break
        parent = parent.parent
    else:
        if obj != root:
            hierarchy_ok = False
            report["checks"]["hierarchy_issue"] = obj.name

report["checks"]["hierarchy_valid"] = hierarchy_ok
report["result"] = "PASS"
print(json.dumps(report, indent=2))