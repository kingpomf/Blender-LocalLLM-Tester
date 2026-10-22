import bpy
import json

# Stage 00: Contract and Scene Safety - Setup
# Creates required collections and validates scene state.

sc = bpy.context.scene
report = {
    "stage": "00",
    "phase": "setup",
    "source_job": "63e47cd8a09f4ff591c5629d191198e8",
    "checks": {}
}

# Verify empty scene (authorized cleanup already confirmed)
objects = [o for o in sc.objects if not o.name.startswith("KART01")]
if objects:
    raise ValueError(f"Unexpected objects in fresh scene: {[o.name for o in objects]}")
report["checks"]["objects"] = []

# Create required collections
asset_coll = bpy.data.collections.get("KART01_ASSET")
if asset_coll is None:
    asset_coll = bpy.data.collections.new("KART01_ASSET")
    sc.collection.children.link(asset_coll)

pres_coll = bpy.data.collections.get("KART01_PRESENTATION")
if pres_coll is None:
    pres_coll = bpy.data.collections.new("KART01_PRESENTATION")
    sc.collection.children.link(pres_coll)

coll_names = [c.name for c in bpy.data.collections if not c.name.startswith("KART01")]
report["checks"]["collections"] = coll_names
assert "KART01_ASSET" in [c.name for c in bpy.data.collections]
assert "KART01_PRESENTATION" in [c.name for c in bpy.data.collections]

# Validate units
us = sc.unit_settings
report["checks"]["units"] = {
    "system": us.system,
    "length_unit": us.length_unit,
    "scale_length": us.scale_length
}
assert us.system == "METRIC", f"Expected METRIC, got {us.system}"
assert us.scale_length == 1.0, f"Expected scale 1.0, got {us.scale_length}"

report["result"] = "PASS"
print(json.dumps(report, indent=2))