import bpy
import json
import os

sc = bpy.context.scene
report = {
    "stage": "08",
    "phase": "final_validation",
    "checks": {}
}

asset_coll = bpy.data.collections.get("KART01_ASSET")
pres_coll = bpy.data.collections.get("KART01_PRESENTATION")
root = bpy.data.objects.get("Kart01_Root")

# Check 1: All named asset objects exist exactly once
required_asset_objects = [
    "Kart01_Root", "Kart01_Chassis", "Kart01_Floor",
    "Kart01_Bumper_Front", "Kart01_Bumper_Rear",
    "Kart01_SidePod_L", "Kart01_SidePod_R",
    "Kart01_Axle_Front", "Kart01_Axle_Rear",
    "Kart01_Wheel_FL", "Kart01_Wheel_FR",
    "Kart01_Wheel_RL", "Kart01_Wheel_RR",
    "Kart01_Seat", "Kart01_Seat_Back",
    "Kart01_SteeringColumn", "Kart01_SteeringWheel",
    "Kart01_Pedal_L", "Kart01_Pedal_R",
    "Kart01_Rim_FL", "Kart01_Rim_FR",
    "Kart01_Rim_RL", "Kart01_Rim_RR"
]

missing = []
for name in required_asset_objects:
    if bpy.data.objects.get(name) is None:
        missing.append(name)
report["checks"]["asset_objects_exist"] = len(missing) == 0
if missing:
    report["checks"]["missing_asset_objects"] = missing

# Check 2: Exactly four wheel objects
wheel_objects = [o for o in asset_coll.objects if "Wheel" in o.name and "Steering" not in o.name]
report["checks"]["exactly_four_wheels"] = len(wheel_objects) == 4
report["checks"]["wheel_count"] = len(wheel_objects)

# Check 3: Asset envelope and ground contact
# Find bounding box of all asset objects
all_verts = []
for obj in asset_coll.objects:
    if obj.type == 'MESH':
        deps = bpy.context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(deps)
        world_matrix = eval_obj.matrix_world
        for vert in eval_obj.data.vertices:
            world_pos = world_matrix @ vert.co
            all_verts.append(world_pos)

if all_verts:
    min_x = min(v[0] for v in all_verts)
    max_x = max(v[0] for v in all_verts)
    min_y = min(v[1] for v in all_verts)
    max_y = max(v[1] for v in all_verts)
    min_z = min(v[2] for v in all_verts)
    max_z = max(v[2] for v in all_verts)

    width = max_x - min_x
    length = max_y - min_y
    height = max_z - min_z

    report["checks"]["envelope_width"] = round(width, 3)
    report["checks"]["envelope_length"] = round(length, 3)
    report["checks"]["envelope_height"] = round(height, 3)
    report["checks"]["envelope_width_ok"] = width <= 1.20 + 0.02
    report["checks"]["envelope_length_ok"] = length <= 1.80 + 0.02
    report["checks"]["envelope_height_ok"] = height <= 1.05 + 0.02
    report["checks"]["ground_contact_ok"] = min_z >= -0.01 and min_z <= 0.01
else:
    report["checks"]["envelope"] = "no vertices found"

# Check 4: Wheelbase and tracks
wheel_positions = []
for name in ["Kart01_Wheel_FL", "Kart01_Wheel_FR", "Kart01_Wheel_RL", "Kart01_Wheel_RR"]:
    obj = bpy.data.objects.get(name)
    if obj:
        wheel_positions.append((name, obj.location))

# Wheelbase (distance between front and rear axles)
if len(wheel_positions) >= 4:
    # Sort by Y position
    wheel_positions.sort(key=lambda x: x[1][1])
    front_axle_y = (wheel_positions[0][1][1] + wheel_positions[1][1][1]) / 2
    rear_axle_y = (wheel_positions[2][1][1] + wheel_positions[3][1][1]) / 2
    wheelbase = abs(rear_axle_y - front_axle_y)
    report["checks"]["wheelbase"] = round(wheelbase, 3)
    report["checks"]["wheelbase_ok"] = abs(wheelbase - 1.10) <= 0.02

    # Front track
    front_track = abs(wheel_positions[0][1][0] - wheel_positions[1][1][0])
    report["checks"]["front_track"] = round(front_track, 3)
    report["checks"]["front_track_ok"] = abs(front_track - 0.92) <= 0.02

    # Rear track
    rear_track = abs(wheel_positions[2][1][0] - wheel_positions[3][1][0])
    report["checks"]["rear_track"] = round(rear_track, 3)
    report["checks"]["rear_track_ok"] = abs(rear_track - 0.96) <= 0.02

# Check 5: All asset objects parented to Kart01_Root
hierarchy_ok = True
for obj in asset_coll.objects:
    if obj != root:
        parent = obj.parent
        while parent is not None:
            if parent == root:
                break
            parent = parent.parent
        else:
            if obj != root:
                hierarchy_ok = False
                report["checks"]["hierarchy_issue"] = obj.name
report["checks"]["all_parented_to_root"] = hierarchy_ok

# Check 6: Mesh scales are applied
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
report["checks"]["scales_applied"] = scale_ok

# Check 7: Every visible mesh has a material
material_ok = True
for obj in asset_coll.objects:
    if obj.type == 'MESH' and not obj.hide_render:
        if not obj.data.materials:
            material_ok = False
            report["checks"]["material_issue"] = obj.name
            break
report["checks"]["all_meshes_have_materials"] = material_ok

# Check 8: No duplicate suffixes
dup_names = [o.name for o in asset_coll.objects if ".00" in o.name]
report["checks"]["no_duplicate_suffixes"] = len(dup_names) == 0
if dup_names:
    report["checks"]["duplicate_names"] = dup_names

# Check 9: Collection membership
asset_only = [o.name for o in asset_coll.objects if any(o.name.startswith(p) for p in ["CAM_", "LIGHT_", "Kart01_Ground"])]
pres_only = [o.name for o in pres_coll.objects if not any(o.name.startswith(p) for p in ["CAM_", "LIGHT_", "Kart01_Ground"])]
report["checks"]["collection_membership_ok"] = len(asset_only) == 0 and len(pres_only) == 0
if asset_only:
    report["checks"]["asset_only_issues"] = asset_only
if pres_only:
    report["checks"]["pres_only_issues"] = pres_only

# Check 10: Total triangle count
total_tris = 0
for obj in asset_coll.objects:
    if obj.type == 'MESH':
        deps = bpy.context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(deps)
        mesh = eval_obj.to_mesh()
        total_tris += len(mesh.polygons)
        eval_obj.to_mesh_clear()

report["checks"]["total_triangles"] = total_tris
report["checks"]["triangle_budget_ok"] = total_tris <= 4500

# Check 11: Blend saves successfully
test_path = "/job/test_save.blend"
try:
    bpy.data.scenes["Scene"].render.filepath = test_path
    bpy.ops.wm.save_as_mainfile(filepath=test_path)
    report["checks"]["blend_saves"] = True
except Exception as e:
    report["checks"]["blend_saves"] = False
    report["checks"]["save_error"] = str(e)

# Check 12: Render files exist
render_files = [
    "artifacts/renders/Kart01_perspective.png",
    "artifacts/renders/Kart01_front.png",
    "artifacts/renders/Kart01_side.png",
    "artifacts/renders/Kart01_rear.png",
]
renders_exist = True
for f in render_files:
    if not os.path.exists(f) or os.path.getsize(f) == 0:
        renders_exist = False
        report["checks"]["render_issue"] = f
report["checks"]["all_renders_exist"] = renders_exist

# Overall result
all_checks = [
    report["checks"].get("asset_objects_exist", False),
    report["checks"].get("exactly_four_wheels", False),
    report["checks"].get("envelope_width_ok", False),
    report["checks"].get("envelope_length_ok", False),
    report["checks"].get("envelope_height_ok", False),
    report["checks"].get("ground_contact_ok", False),
    report["checks"].get("wheelbase_ok", False),
    report["checks"].get("front_track_ok", False),
    report["checks"].get("rear_track_ok", False),
    report["checks"].get("all_parented_to_root", False),
    report["checks"].get("scales_applied", False),
    report["checks"].get("all_meshes_have_materials", False),
    report["checks"].get("no_duplicate_suffixes", False),
    report["checks"].get("collection_membership_ok", False),
    report["checks"].get("triangle_budget_ok", False),
    report["checks"].get("blend_saves", False),
    report["checks"].get("all_renders_exist", False),
]
report["result"] = "PASS" if all(all_checks) else "FAIL"
print(json.dumps(report, indent=2))