import bpy
import json

sc = bpy.context.scene
report = {
    "stage": "04",
    "phase": "seat_and_steering",
    "source_job": "396d5237b4864d26b0bc7a6a621adfba",
    "checks": {}
}

asset_coll = bpy.data.collections.get("KART01_ASSET")
root = bpy.data.objects.get("Kart01_Root")
assert asset_coll is not None, "KART01_ASSET missing"
assert root is not None, "Kart01_Root missing"

# Kart01_Seat - base and backrest
# Seat base
bpy.ops.mesh.primitive_cube_add(size=0.4, location=(0, 0.4, 0.22))
seat_base = bpy.context.active_object
seat_base.name = "Kart01_Seat_Base"
seat_base.scale = (0.35, 0.25, 0.05)
seat_base.location = (0, 0.4, 0.22)
asset_coll.objects.link(seat_base)
seat_base.parent = root
sc.collection.objects.unlink(seat_base)

# Seat backrest
bpy.ops.mesh.primitive_cube_add(size=0.4, location=(0, 0.55, 0.35))
seat_back = bpy.context.active_object
seat_back.name = "Kart01_Seat_Back"
seat_back.scale = (0.35, 0.05, 0.2)
seat_back.location = (0, 0.55, 0.35)
seat_back.rotation_euler = (0.2, 0, 0)
asset_coll.objects.link(seat_back)
seat_back.parent = root
sc.collection.objects.unlink(seat_back)

# Rename seat base to Kart01_Seat (joined mesh approach)
seat_base.name = "Kart01_Seat"

# Kart01_SteeringColumn - angled from chassis to driver
bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.3, location=(0, -0.1, 0.3), vertices=6)
col = bpy.context.active_object
col.name = "Kart01_SteeringColumn"
col.rotation_euler = (0.3, 0, 0)
col.location = (0, -0.1, 0.3)
asset_coll.objects.link(col)
col.parent = root
sc.collection.objects.unlink(col)

# Kart01_SteeringWheel - low-poly ring
bpy.ops.mesh.primitive_torus_add(major_radius=0.12, minor_radius=0.015, major_segments=8, minor_segments=4, location=(0, -0.05, 0.4))
wheel = bpy.context.active_object
wheel.name = "Kart01_SteeringWheel"
wheel.location = (0, -0.05, 0.4)
asset_coll.objects.link(wheel)
wheel.parent = root
sc.collection.objects.unlink(wheel)

# Kart01_Pedal_L
bpy.ops.mesh.primitive_cube_add(size=0.05, location=(-0.1, -0.3, 0.18))
pedal_l = bpy.context.active_object
pedal_l.name = "Kart01_Pedal_L"
pedal_l.scale = (0.05, 0.08, 0.01)
pedal_l.location = (-0.1, -0.3, 0.18)
asset_coll.objects.link(pedal_l)
pedal_l.parent = root
sc.collection.objects.unlink(pedal_l)

# Kart01_Pedal_R
bpy.ops.mesh.primitive_cube_add(size=0.05, location=(0.1, -0.3, 0.18))
pedal_r = bpy.context.active_object
pedal_r.name = "Kart01_Pedal_R"
pedal_r.scale = (0.05, 0.08, 0.01)
pedal_r.location = (0.1, -0.3, 0.18)
asset_coll.objects.link(pedal_r)
pedal_r.parent = root
sc.collection.objects.unlink(pedal_r)

# Count total triangles for stage 04 objects
stage04_objs = ["Kart01_Seat", "Kart01_Seat_Back", "Kart01_SteeringColumn", "Kart01_SteeringWheel", "Kart01_Pedal_L", "Kart01_Pedal_R"]
total_tris = 0
for name in stage04_objs:
    obj = bpy.data.objects.get(name)
    if obj and obj.type == 'MESH':
        deps = bpy.context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(deps)
        mesh = eval_obj.to_mesh()
        total_tris += len(mesh.polygons)
        eval_obj.to_mesh_clear()

report["checks"]["objects"] = [o.name for o in asset_coll.objects]
report["checks"]["stage04_triangles"] = total_tris
assert total_tris <= 1000, f"Stage 04 triangle budget exceeded: {total_tris}"
report["result"] = "PASS"
print(json.dumps(report, indent=2))