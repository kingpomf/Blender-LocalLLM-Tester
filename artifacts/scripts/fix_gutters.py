import bpy

# Remove all gutter-related objects
for name in list(bpy.data.objects.keys()):
    if "Gutter" in name or "Rail" in name or "Divider" in name:
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

def create_open_gutter(name, x_center):
    # U-channel: bottom + 2 sides, open at top
    # Cross-section: 3 points (bottom-left, bottom-right, top-right) -> extrude
    half = gutter_width / 2
    # Profile: bottom and two walls
    profile = [
        (-half, -gutter_depth),  # bottom-left
        (half, -gutter_depth),   # bottom-right
        (half, 0),               # right wall top
        (-half, 0),              # left wall top
    ]
    
    verts = []
    for px, pz in profile:
        verts.append((x_center + px, 0, pz))
    for px, pz in profile:
        verts.append((x_center + px, gutter_length, pz))
    
    n = len(profile)
    faces = []
    # Bottom face
    faces.append((0, 1, n + 1, n))
    # Right wall
    faces.append((1, 2, n + 2, n + 1))
    # Left wall
    faces.append((3, 0, n, n + 3))
    
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    obj = bpy.data.objects.new(name, mesh)
    static_col.objects.link(obj)
    obj.parent = root
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return obj

# Create 4 gutters
positions = {
    "Gutter_L_Outer": -1.6044,
    "Gutter_L_Inner": -0.2956,
    "Gutter_R_Inner": 0.2956,
    "Gutter_R_Outer": 1.6044
}
for name, x in positions.items():
    create_open_gutter(name, x)

# Pin decks (already exist, just ensure correct Z)
for name in ["PinDeck_L", "PinDeck_R"]:
    obj = bpy.data.objects.get(name)
    if obj:
        obj.location.z = 0.0

report = {
    "gutters_created": 4,
    "open_channel": True
}