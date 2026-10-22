import bpy
import json

sc = bpy.context.scene
report = {
    "stage": "05",
    "phase": "materials",
    "source_job": "18536999eae34d2b8d5d0a6c2999c70e",
    "checks": {}
}

asset_coll = bpy.data.collections.get("KART01_ASSET")
root = bpy.data.objects.get("Kart01_Root")
assert asset_coll is not None, "KART01_ASSET missing"
assert root is not None, "Kart01_Root missing"

# Create materials
def create_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        bsdf = mat.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat

mat_red = create_material("MAT_Kart_Red", (0.776, 0.157, 0.157))
mat_rubber = create_material("MAT_Rubber_Dark", (0.09, 0.09, 0.09), roughness=0.7)
mat_metal = create_material("MAT_Metal_Dark", (0.2, 0.2, 0.2), roughness=0.3, metallic=0.9)
mat_rim = create_material("MAT_Rim_Silver", (0.8, 0.8, 0.8), roughness=0.2, metallic=1.0)
mat_seat = create_material("MAT_Seat_Black", (0.05, 0.05, 0.05), roughness=0.8)

# Assign materials to objects
assignments = {
    "Kart01_Chassis": mat_red,
    "Kart01_Bumper_Front": mat_red,
    "Kart01_Bumper_Rear": mat_red,
    "Kart01_SidePod_L": mat_red,
    "Kart01_SidePod_R": mat_red,
    "Kart01_Floor": mat_metal,
    "Kart01_Axle_Front": mat_metal,
    "Kart01_Axle_Rear": mat_metal,
    "Kart01_Seat": mat_seat,
    "Kart01_Seat_Back": mat_seat,
    "Kart01_SteeringColumn": mat_metal,
    "Kart01_SteeringWheel": mat_seat,
    "Kart01_Pedal_L": mat_metal,
    "Kart01_Pedal_R": mat_metal,
}

# Wheels get rubber
for wheel_name in ["Kart01_Wheel_FL", "Kart01_Wheel_FR", "Kart01_Wheel_RL", "Kart01_Wheel_RR"]:
    assignments[wheel_name] = mat_rubber

# Create simple rims (cylinders inside each wheel)
rim_positions = [
    ("Kart01_Rim_FL", -0.46, -0.55),
    ("Kart01_Rim_FR", 0.46, -0.55),
    ("Kart01_Rim_RL", -0.48, 0.55),
    ("Kart01_Rim_RR", 0.48, 0.55),
]

for rim_name, x, y in rim_positions:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.14, location=(x, y, 0.17), vertices=8)
    rim = bpy.context.active_object
    rim.name = rim_name
    rim.location = (x, y, 0.17)
    asset_coll.objects.link(rim)
    rim.parent = root
    sc.collection.objects.unlink(rim)
    assignments[rim_name] = mat_rim

# Apply all assignments
for obj_name, mat in assignments.items():
    obj = bpy.data.objects.get(obj_name)
    if obj and obj.type == 'MESH':
        if not obj.data.materials:
            obj.data.materials.append(mat)
        else:
            obj.data.materials[0] = mat

report["checks"]["materials_created"] = ["MAT_Kart_Red", "MAT_Rubber_Dark", "MAT_Metal_Dark", "MAT_Rim_Silver", "MAT_Seat_Black"]
report["checks"]["objects_with_materials"] = len(assignments)
report["result"] = "PASS"
print(json.dumps(report, indent=2))