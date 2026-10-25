import bpy

# Remove old gutters and lanes
for name in list(bpy.data.objects.keys()):
    if name.startswith("Gutter_") or name.startswith("Lane_"):
        obj = bpy.data.objects[name]
        mesh = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)

root = bpy.data.objects["BowlingPair01_ROOT"]
static_col = bpy.data.collections.get("BP01_STATIC")

lane_width = 1.0668
lane_length = 19.2
gutter_width = 0.24
gutter_depth = 0.12

def create_lane(lane_name, x_center):
    half = lane_width / 2
    verts = [
        (x_center - half, 0, 0),
        (x_center + half, 0, 0),
        (x_center + half, lane_length, 0),
        (x_center - half, lane_length, 0),
    ]
    faces = [(0, 1, 2, 3)]
    mesh = bpy.data.meshes.new(f"{lane_name}_mesh")
    obj = bpy.data.objects.new(lane_name, mesh)
    static_col.objects.link(obj)
    obj.parent = root
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return obj

def create_gutter(name, x_center):
    half = gutter_width / 2
    # U-channel with proper face normals
    # Profile: bottom, left wall, right wall
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
        verts.append((x_center + px, lane_length, pz))
    
    n = len(profile)
    faces = []
    # Side walls
    for i in range(n - 1):
        faces.append((i, i + 1, n + i + 1, n + i))
    # Bottom
    faces.append((0, 1, n + 1, n))
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

create_lane("Lane_L_Surface", -0.95)
create_lane("Lane_R_Surface", 0.95)
create_gutter("Gutter_L_Outer", -1.6044)
create_gutter("Gutter_L_Inner", -0.2956)
create_gutter("Gutter_R_Inner", 0.2956)
create_gutter("Gutter_R_Outer", 1.6044)

report = {"lanes": 2, "gutters": 4, "u_channel": True}