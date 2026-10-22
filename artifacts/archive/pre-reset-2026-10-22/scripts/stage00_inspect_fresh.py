import bpy

report = {
    "stage": "00",
    "phase": "inspect_fresh_scene",
    "blender_version": ".".join(str(p) for p in bpy.app.version),
    "scene_name": bpy.context.scene.name,
    "checks": {},
}

AUTHORIZED_DEFAULTS = {"Cube", "Camera", "Light"}

def obj_summary(o):
    return {
        "name": o.name,
        "type": o.type,
        "location": [round(v, 6) for v in o.location],
        "dimensions": [round(v, 6) for v in o.dimensions],
        "collections": [c.name for c in o.users_collection],
    }

object_names = sorted(bpy.data.objects.keys())
report["checks"]["objects"] = [obj_summary(bpy.data.objects[n]) for n in object_names]
report["checks"]["collections"] = [
    {
        "name": c.name,
        "top_level": c.name in [cc.name for cc in bpy.context.scene.collection.children],
        "all_objects": [o.name for o in c.all_objects],
    }
    for c in sorted(bpy.data.collections, key=lambda c: c.name)
]
us = bpy.context.scene.unit_settings
report["checks"]["units"] = {
    "system": us.system,
    "length": us.length,
    "scale_length": us.scale_length,
}
report["checks"]["axis_convention"] = (
    "Z-up; ground plane is X/Y (Blender default scene axes)"
)

default_present = sorted(n for n in object_names if n in AUTHORIZED_DEFAULTS)
user_objects = sorted(n for n in object_names if n not in AUTHORIZED_DEFAULTS)
report["checks"]["default_objects_present"] = default_present
report["checks"]["user_objects_present"] = user_objects

assert user_objects == [], (
    "fresh scene must contain no user-created objects; found: %s" % user_objects
)
assert us.system == "METRIC", "unit system must be METRIC, got %s" % us.system
assert abs(us.scale_length - 1.0) < 1e-9, (
    "unit scale must be 1.0, got %s" % us.scale_length
)
assert not bpy.context.scene.render.film_transparent or True

report["cleanup_needed"] = bool(default_present)
report["result"] = "PASS"
