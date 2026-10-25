import bpy

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
    # Solid block, not hollow
    verts = [
        (x_center - half, 0, -gutter_depth),
        (x_center + half, 0, -gutter_depth),
        (x_center + half, gutter_length, -gutter_depth),
        (x_center - half, gutter_length, -gutter_depth),
        (x_center - half, 0, 0),
        (x_center + half, 0, 0),
        (x_center + half, gutter_length, 0),
        (x_center - half, gutter_length, 0),
    ]
    faces = [
        (0, 1, 2, 3), (4, 5, 6, 7),
        (0, 4, 7, 3), (1, 5, 6, 2),
        (0, 1, 5, 4), (3, 7, 6, 2),
    ]
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    obj = bpy.data.objects.new(name, mesh)
    static_col.objects.link(obj)
    obj.parent = root
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return obj

positions = {
    "Gutter_L_Outer": -1.6044,
    "Gutter_L_Inner": -0.2956,
    "Gutter_R_Inner": 0.2956,
    "Gutter_R_Outer": 1.6044
}
for name, x in positions.items():
    create_gutter(name, x)

report = {"gutters_created": 4, "solid_block": True}