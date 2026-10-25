import bpy
import math

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
    # Create a curved trough (half-cylinder)
    # Profile: arc from left wall top, down to bottom, up to right wall top
    segments = 16
    profile = []
    for i in range(segments + 1):
        t = i / segments
        angle = math.pi * t
        # Half-circle arc
        x = half - wall_thick - (half - wall_thick) * math.cos(angle)
        z = -gutter_depth + (half - wall_thick) * math.sin(angle)
        # Add wall thickness on sides
        if i == 0 or i == segments:
            x = half - wall_thick if i == segments else -half + wall_thick
            z = 0
        profile.append((x, z))
    
    # Add wall tops
    profile.insert(0, (-half, 0))
    profile.append((half, 0))
    
    # Create 3D geometry by extruding profile along Y
    verts = []
    for i, (px, pz) in enumerate(profile):
        verts.append((x_center + px, 0, pz))
    for i, (px, pz) in enumerate(profile):
        verts.append((x_center + px, gutter_length, pz))
    
    n = len(profile)
    faces = []
    # Create faces between consecutive profile points
    for i in range(n - 1):
        faces.append((i, i + 1, n + i + 1, n + i))
    # Front and back caps
    faces.append(tuple(range(n)))
    faces.append(tuple(range(n, 2 * n)))
    
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

report = {"gutters_created": 4, "curved_trough": True}