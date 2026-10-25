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

def create_gutter(name, x_center):
    half = gutter_width / 2
    # Create profile: left wall top -> down -> across bottom -> up -> right wall top
    segments = 8
    profile = []
    # Left wall
    profile.append((-half, 0))
    # Left side of curve (going down)
    for i in range(1, segments):
        t = i / segments
        angle = -math.pi / 2 * t
        x = -half + (half - 0) * (1 + math.cos(angle)) / 2
        z = gutter_depth * math.sin(angle)
        profile.append((x, z))
    # Bottom
    profile.append((0, -gutter_depth))
    # Right side of curve (going up)
    for i in range(1, segments):
        t = i / segments
        angle = -math.pi / 2 + math.pi / 2 * t
        x = half * (1 + math.cos(angle)) / 2
        z = gutter_depth * math.sin(angle)
        profile.append((x, z))
    # Right wall
    profile.append((half, 0))
    
    # Create 3D by extruding along Y
    verts = []
    for px, pz in profile:
        verts.append((x_center + px, 0, pz))
    for px, pz in profile:
        verts.append((x_center + px, gutter_length, pz))
    
    n = len(profile)
    faces = []
    for i in range(n - 1):
        faces.append((i, i + 1, n + i + 1, n + i))
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

report = {"gutters_created": 4, "explicit_profile": True}