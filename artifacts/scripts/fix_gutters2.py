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
wall_thick = 0.015

def create_gutter(name, x_center):
    half = gutter_width / 2
    # Create a U-channel with wall thickness
    # Profile: outer bottom-left, inner bottom-left, inner bottom-right, outer bottom-right,
    # outer right wall top, inner right wall top, inner left wall top, outer left wall top
    profile = [
        (-half, -gutter_depth),
        (-half + wall_thick, -gutter_depth),
        (half - wall_thick, -gutter_depth),
        (half, -gutter_depth),
        (half, 0),
        (half - wall_thick, 0),
        (-half + wall_thick, 0),
        (-half, 0),
    ]
    
    verts = []
    for px, pz in profile:
        verts.append((x_center + px, 0, pz))
    for px, pz in profile:
        verts.append((x_center + px, gutter_length, pz))
    
    n = len(profile)
    faces = []
    # Bottom outer
    faces.append((0, 3, n + 3, n))
    # Bottom inner (floor of trough)
    faces.append((1, 2, n + 2, n + 1))
    # Left wall inner
    faces.append((1, 6, n + 6, n + 1))
    # Right wall inner
    faces.append((2, 5, n + 5, n + 2))
    # Left wall outer
    faces.append((7, 0, n, n + 7))
    # Right wall outer
    faces.append((3, 4, n + 4, n + 3))
    # Left wall top
    faces.append((6, 7, n + 7, n + 6))
    # Right wall top
    faces.append((4, 5, n + 5, n + 4))
    # Front and back caps
    faces.append((0, 1, 6, 7))
    faces.append((3, 2, 5, 4))
    faces.append((n, n + 1, n + 6, n + 7))
    faces.append((n + 3, n + 2, n + 5, n + 4))
    
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

report = {"gutters_created": 4, "thick_walls": True}