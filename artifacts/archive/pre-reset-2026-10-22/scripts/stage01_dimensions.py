import bpy
import json

sc = bpy.context.scene
report = {
    "stage": "01",
    "phase": "coordinate_system_and_dimensions",
    "source_job": "220a53c4f1574cefa9881705053bef02",
    "checks": {}
}

# Target envelope constants
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

# Verify collections exist from Stage 00
asset_coll = bpy.data.collections.get("KART01_ASSET")
pres_coll = bpy.data.collections.get("KART01_PRESENTATION")
assert asset_coll is not None, "KART01_ASSET missing"
assert pres_coll is not None, "KART01_PRESENTATION missing"
report["checks"]["collections"] = ["KART01_ASSET", "KART01_PRESENTATION"]

# Create reference envelope marker (non-rendering)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, ENVELOPE_Z / 2))
env_obj = bpy.context.active_object
env_obj.name = "REF_envelope"
env_obj.scale = (ENVELOPE_X, ENVELOPE_Y, ENVELOPE_Z)
env_obj.show_render = False
pres_coll.objects.link(env_obj)
sc.collection.objects.unlink(env_obj)

# Reference points for wheelbase (front and rear axle positions)
# Front axle at Y = -wheelbase/2, rear at Y = +wheelbase/2
bpy.ops.mesh.primitive_plane_add(size=0.05, location=(0, -WHEELBASE/2, 0.001))
fa = bpy.context.active_object
fa.name = "REF_front_axle"
fa.show_render = False
pres_coll.objects.link(fa)
sc.collection.objects.unlink(fa)

bpy.ops.mesh.primitive_plane_add(size=0.05, location=(0, WHEELBASE/2, 0.001))
ra = bpy.context.active_object
ra.name = "REF_rear_axle"
ra.show_render = False
pres_coll.objects.link(ra)
sc.collection.objects.unlink(ra)

report["checks"]["ref_objects"] = ["REF_envelope", "REF_front_axle", "REF_rear_axle"]
report["result"] = "PASS"
print(json.dumps(report, indent=2))