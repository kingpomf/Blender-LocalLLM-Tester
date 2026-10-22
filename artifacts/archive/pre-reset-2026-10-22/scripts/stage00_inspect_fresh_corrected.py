"""Assisted correction of the failed model-authored pre-change inspection.

Preserve stage00_inspect_fresh.py as evaluation evidence. This script observes
the initial scene; Metric units/collections are Stage 00 setup postconditions.
"""
import bpy

scene = bpy.context.scene
units = scene.unit_settings
authorized_defaults = {"Cube", "Camera", "Light"}
object_names = sorted(bpy.data.objects.keys())
user_objects = sorted(set(object_names) - authorized_defaults)

report = {
    "stage": "00",
    "phase": "inspect_fresh_scene",
    "assisted_correction_of": "cb743bfa380d43a98cfe895514e5356a",
    "blender_version": bpy.app.version_string,
    "scene_name": scene.name,
    "checks": {
        "objects": [
            {
                "name": obj.name,
                "type": obj.type,
                "location": list(obj.location),
                "dimensions": list(obj.dimensions),
                "collections": sorted(c.name for c in obj.users_collection),
            }
            for obj in sorted(bpy.data.objects, key=lambda obj: obj.name)
        ],
        "collections": [
            {"name": col.name, "all_objects": sorted(o.name for o in col.all_objects)}
            for col in sorted(bpy.data.collections, key=lambda col: col.name)
        ],
        "units": {
            "system": units.system,
            "length_unit": units.length_unit,
            "scale_length": units.scale_length,
        },
        "axis_convention": "Z-up; ground plane X/Y (Blender convention)",
        "default_objects_present": sorted(set(object_names) & authorized_defaults),
        "user_objects_present": user_objects,
    },
    "cleanup_needed": bool(set(object_names) & authorized_defaults),
    "stage_setup_required": True,
    "result": "PASS" if not user_objects else "BLOCKED",
}
assert not user_objects, f"Unexpected user-created objects: {user_objects}"
# Do not assert Metric here: record the pre-change state, then configure and
# validate METRIC / scale 1.0 in the subsequent Stage 00 setup revision.
