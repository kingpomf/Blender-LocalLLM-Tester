import bpy
import json

sc = bpy.context.scene
report = {
    "stage": "01",
    "phase": "coordinate_system_and_dimensions",
    "source_job": "220a53c4f1574cefa9881705053bef02",
    "checks": {}
}

ENVELOPE_X = 1.20
ENVELOPE_Y = 1.80
ENVELOPE_Z = 1.05
WHEELBASE = 1.10
FRONT_TRACK = 0.92
REAR_TRACK = 0.96
WHEEL_DIA = 0.34
WHEEL_W = 0.14
GROUND_TOL = 0.01

report["targets"] = {
    "envelope": {"x": ENVELOPE_X, "y": ENVELOPE_Y, "z": ENVELOPE_Z},
    "wheelbase": WHEELBASE,
    "front_track": FRONT_TRACK,
    "rear_track": REAR_TRACK,
    "wheel_diameter": WHEEL_DIA,
    "wheel_width": WHEEL_W,
    "ground_tolerance": GROUND_TOL
}

asset_coll = bpy.data.collections.get("KART01_ASSET")
pres_coll = bpy.data.collections.get("KART01_PRESENTATION")
assert asset_coll is not None, "KART01_ASSET missing"
assert pres_coll is not None, "KART01_PRESENTATION missing"
report["checks"]["collections"] = ["KART01_ASSET", "KART01_PRESENTATION"]

# Create reference envelope using direct mesh creation (no bpy.ops)
env_mesh = bpy.data.meshes.new("REF_envelope_mesh")
env_obj = bpy.data.objects.new("REF_envelope", env_mesh)
env_obj.location = (0, 0, ENVELOPE_Z / 2)
env_obj.scale = (ENVELOPE_X, ENVELOPE_Y, ENVELOPE_Z)
env_obj.show_render = False
pres_coll.objects.link(env_obj)

# Front axle reference
fa_mesh = bpy.data.meshes.new("REF_front_axle_mesh")
fa_obj = bpy.data.objects.new("REF_front_axle", fa_mesh)
fa_obj.location = (0, -WHEELBASE/2, 0.001)
fa_obj.show_render = False
pres_coll.objects.link(fa_obj)

# Rear axle reference
ra_mesh = bpy.data.meshes.new("REF_rear_axle_mesh")
ra_obj = bpy.data.objects.new("REF_rear_axle", ra_mesh)
ra_obj.location = (0, WHEELBASE/2, 0.001)
ra_obj.show_render = False
pres_coll.objects.link(ra_obj)

report["checks"]["ref_objects"] = ["REF_envelope", "REF_front_axle", "REF_rear_axle"]
report["result"] = "PASS"
print(json.dumps(report, indent=2))