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
    # Simple U-channel: bottom at -0.12, walls up to 0
    profile = [
        (-half, -gutter_depth),
        (half, -gutter_depth),
        (half, 0),
        (-half, 0),
    ]
    verts = []
    for px, pz in profile:
        verts.append((x_center + px, 0, pz))
    for px, pz in profile:
        verts.append((x_center + px, gutter_length, pz))
    n = len(profile)
    faces = [
        (0, 1, n + 1, n),
        (1, 2, n + 2, n + 1),
        (3, 0, n, n + 3),
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

report = {"gutters_created": 4, "depth": 0.12}