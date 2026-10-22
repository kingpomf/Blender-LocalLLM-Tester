import bpy
import json

sc = bpy.context.scene
report = {
    "stage": "03",
    "phase": "axles_and_wheels",
    "source_job": "495b62f5931e4048b504cdc641ba3e96",
    "checks": {}
}

asset_coll = bpy.data.collections.get("KART01_ASSET")
root = bpy.data.objects.get("Kart01_Root")
assert asset_coll is not None, "KART01_ASSET missing"
assert root is not None, "Kart01_Root missing"

WHEEL_RADIUS = 0.17
WHEEL_WIDTH = 0.14
WHEELBASE = 1.10
FRONT_TRACK = 0.92
REAR_TRACK = 0.96

# Axles - simple cylinders along X axis
# Front axle at Y = -WHEELBASE/2 = -0.55
bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=FRONT_TRACK + 0.04, location=(0, -WHEELBASE/2, 0.17), rotation=(0, 0, 0))
axle_f = bpy.context.active_object
axle_f.name = "Kart01_Axle_Front"
axle_f.rotation_euler = (0, 0, 0)
asset_coll.objects.link(axle_f)
axle_f.parent = root
sc.collection.objects.unlink(axle_f)

# Rear axle at Y = +WHEELBASE/2 = +0.55
bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=REAR_TRACK + 0.04, location=(0, WHEELBASE/2, 0.17), rotation=(0, 0, 0))
axle_r = bpy.context.active_object
axle_r.name = "Kart01_Axle_Rear"
axle_r.rotation_euler = (0, 0, 0)
asset_coll.objects.link(axle_r)
axle_r.parent = root
sc.collection.objects.unlink(axle_r)

# Wheels - use low-poly cylinders (12 segments) for tires
# Wheel centers at Z = WHEEL_RADIUS = 0.17 so bottoms touch Z=0.00
def create_wheel(name, x, y, z):
    bpy.ops.mesh.primitive_cylinder_add(radius=WHEEL_RADIUS, depth=WHEEL_WIDTH, location=(x, y, z), vertices=12)
    wheel = bpy.context.active_object
    wheel.name = name
    wheel.rotation_euler = (0, 0, 0)
    wheel.location = (x, y, z)
    asset_coll.objects.link(wheel)
    wheel.parent = root
    sc.collection.objects.unlink(wheel)
    return wheel

# Front wheels
fl = create_wheel("Kart01_Wheel_FL", -FRONT_TRACK/2, -WHEELBASE/2, WHEEL_RADIUS)
fr = create_wheel("Kart01_Wheel_FR", FRONT_TRACK/2, -WHEELBASE/2, WHEEL_RADIUS)

# Rear wheels
rl = create_wheel("Kart01_Wheel_RL", -REAR_TRACK/2, WHEELBASE/2, WHEEL_RADIUS)
rr = create_wheel("Kart01_Wheel_RR", REAR_TRACK/2, WHEELBASE/2, WHEEL_RADIUS)

# Count total triangles
total_tris = 0
for obj in asset_coll.objects:
    if obj.type == 'MESH':
        deps = bpy.context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(deps)
        mesh = eval_obj.to_mesh()
        total_tris += len(mesh.polygons)
        eval_obj.to_mesh_clear()

report["checks"]["objects"] = [o.name for o in asset_coll.objects]
report["checks"]["total_triangles"] = total_tris
report["checks"]["wheel_radius"] = WHEEL_RADIUS
report["checks"]["wheelbase"] = WHEELBASE
report["checks"]["front_track"] = FRONT_TRACK
report["checks"]["rear_track"] = REAR_TRACK
assert total_tris <= 1500, f"Triangle budget exceeded: {total_tris}"
report["result"] = "PASS"
print(json.dumps(report, indent=2))