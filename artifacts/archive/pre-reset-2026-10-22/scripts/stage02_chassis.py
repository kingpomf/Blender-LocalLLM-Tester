import bpy
import json

sc = bpy.context.scene
report = {
    "stage": "02",
    "phase": "chassis_and_bumpers",
    "source_job": "12e9d0520c024192aa0204e7c0d70710",
    "checks": {}
}

asset_coll = bpy.data.collections.get("KART01_ASSET")
assert asset_coll is not None, "KART01_ASSET missing"

# Kart01_Root - empty at world origin
root = bpy.data.objects.new("Kart01_Root", None)
root.location = (0, 0, 0)
asset_coll.objects.link(root)

# Kart01_Chassis - main body (tapered front)
# Using a box with custom vertex positions to create tapered front
chassis_data = bpy.data.meshes.new("Kart01_Chassis_mesh")
verts = [
    # Bottom face (Y=-0.6 to 0.8, X=-0.4 to 0.4, Z=0.17)
    (-0.4, -0.6, 0.17), (0.4, -0.6, 0.17), (0.4, 0.8, 0.17), (-0.4, 0.8, 0.17),
    # Top face (Y=-0.6 to 0.8, X=-0.25 to 0.25, Z=0.4) - narrower at front
    (-0.25, -0.6, 0.4), (0.25, -0.6, 0.4), (0.25, 0.8, 0.4), (-0.25, 0.8, 0.4)
]
faces = [
    # Bottom
    (0, 1, 2, 3),
    # Top
    (4, 5, 6, 7),
    # Front face (tapered)
    (0, 1, 5, 4),
    # Back face
    (2, 3, 7, 6),
    # Left face
    (0, 3, 7, 4),
    # Right face
    (1, 2, 6, 5),
    # Bottom-front slope
    (0, 1, 5, 4),
]
chassis_data.from_pydata(verts, [], faces)
chassis = bpy.data.objects.new("Kart01_Chassis", chassis_data)
chassis.location = (0, 0, 0)
asset_coll.objects.link(chassis)
chassis.parent = root

# Kart01_Floor - flat driver floor
floor_data = bpy.data.meshes.new("Kart01_Floor_mesh")
floor_verts = [
    (-0.35, -0.5, 0.17), (0.35, -0.5, 0.17),
    (0.35, 0.7, 0.17), (-0.35, 0.7, 0.17)
]
floor_faces = [(0, 1, 2, 3)]
floor_data.from_pydata(floor_verts, [], floor_faces)
floor = bpy.data.objects.new("Kart01_Floor", floor_data)
floor.location = (0, 0, 0)
asset_coll.objects.link(floor)
floor.parent = root

# Kart01_Bumper_Front - simple box
bf_data = bpy.data.meshes.new("Kart01_Bumper_Front_mesh")
bpy.ops.mesh.primitive_cube_add(size=0.05, location=(-0.3, -0.6, 0.18))
bf = bpy.context.active_object
bf.name = "Kart01_Bumper_Front"
bf.scale = (0.05, 1.0, 0.05)
bf.location = (-0.3, -0.6, 0.18)
asset_coll.objects.link(bf)
bf.parent = root
sc.collection.objects.unlink(bf)

# Kart01_Bumper_Rear - simple box
br_data = bpy.data.meshes.new("Kart01_Bumper_Rear_mesh")
bpy.ops.mesh.primitive_cube_add(size=0.05, location=(-0.35, 0.9, 0.18))
br = bpy.context.active_object
br.name = "Kart01_Bumper_Rear"
br.scale = (0.05, 1.0, 0.05)
br.location = (-0.35, 0.9, 0.18)
asset_coll.objects.link(br)
br.parent = root
sc.collection.objects.unlink(br)

# Kart01_SidePod_L
bpy.ops.mesh.primitive_cube_add(size=0.1, location=(-0.42, 0.1, 0.24))
spl = bpy.context.active_object
spl.name = "Kart01_SidePod_L"
spl.scale = (0.08, 0.15, 0.12)
spl.location = (-0.42, 0.1, 0.24)
asset_coll.objects.link(spl)
spl.parent = root
sc.collection.objects.unlink(spl)

# Kart01_SidePod_R
bpy.ops.mesh.primitive_cube_add(size=0.1, location=(0.42, 0.1, 0.24))
spr = bpy.context.active_object
spr.name = "Kart01_SidePod_R"
spr.scale = (0.08, 0.15, 0.12)
spr.location = (0.42, 0.1, 0.24)
asset_coll.objects.link(spr)
spr.parent = root
sc.collection.objects.unlink(spr)

# Count total triangles
total_tris = 0
for obj in asset_coll.objects:
    if obj.type == 'MESH':
        deps = bpy.context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(deps)
        mesh = eval_obj.to_mesh()
        total_tris += len(mesh.polygons)
        mesh = eval_obj.to_mesh_clear()

report["checks"]["objects"] = [o.name for o in asset_coll.objects]
report["checks"]["total_triangles"] = total_tris
report["checks"]["root_at_origin"] = root.location == (0, 0, 0)
assert total_tris <= 1500, f"Triangle budget exceeded: {total_tris}"
report["result"] = "PASS"
print(json.dumps(report, indent=2))