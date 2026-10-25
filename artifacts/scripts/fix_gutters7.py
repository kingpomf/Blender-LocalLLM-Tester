import bpy

# Remove existing gutters
for name in list(bpy.data.objects.keys()):
    if name.startswith("Gutter_"):
        obj = bpy.data.objects[name]
        mesh = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)

root = bpy.data.objects["BowlingPair01_ROOT"]
static_col = bpy.data.collections.get("BP01_STATIC")

gutter_width = 0.24
gutter_depth = 0.12
gutter_length = 19.2

def create_gutter(name, x_center):
    half = gutter_width / 2
    # Create gutter with explicit bottom and walls
    # Bottom face
    bottom_verts = [
        (x_center - half, 0, -gutter_depth),
        (x_center + half, 0, -gutter_depth),
        (x_center + half, gutter_length, -gutter_depth),
        (x_center - half, gutter_length, -gutter_depth),
    ]
    bottom_mesh = bpy.data.meshes.new(f"{name}_bottom")
    bottom_obj = bpy.data.objects.new(f"{name}_bottom", bottom_mesh)
    static_col.objects.link(bottom_obj)
    bottom_obj.parent = root
    bottom_mesh.from_pydata(bottom_verts, [], [(0, 1, 2, 3)])
    bottom_mesh.update()
    
    # Left wall
    left_verts = [
        (x_center - half, 0, -gutter_depth),
        (x_center - half, 0, 0),
        (x_center - half, gutter_length, 0),
        (x_center - half, gutter_length, -gutter_depth),
    ]
    left_mesh = bpy.data.meshes.new(f"{name}_left")
    left_obj = bpy.data.objects.new(f"{name}_left", left_mesh)
    static_col.objects.link(left_obj)
    left_obj.parent = root
    left_mesh.from_pydata(left_verts, [], [(0, 1, 2, 3)])
    left_mesh.update()
    
    # Right wall
    right_verts = [
        (x_center + half, 0, -gutter_depth),
        (x_center + half, 0, 0),
        (x_center + half, gutter_length, 0),
        (x_center + half, gutter_length, -gutter_depth),
    ]
    right_mesh = bpy.data.meshes.new(f"{name}_right")
    right_obj = bpy.data.objects.new(f"{name}_right", right_mesh)
    static_col.objects.link(right_obj)
    right_obj.parent = root
    right_mesh.from_pydata(right_verts, [], [(0, 1, 2, 3)])
    right_mesh.update()
    
    return bottom_obj

positions = {
    "Gutter_L_Outer": -1.6044,
    "Gutter_L_Inner": -0.2956,
    "Gutter_R_Inner": 0.2956,
    "Gutter_R_Outer": 1.6044
}
for name, x in positions.items():
    create_gutter(name, x)

report = {"gutters_created": 4, "separate_parts": True}