import bpy

# Remove old solid gutters
old_gutters = ["Gutter_L_Outer", "Gutter_L_Inner", "Gutter_R_Inner", "Gutter_R_Outer"]
for name in old_gutters:
    obj = bpy.data.objects.get(name)
    if obj:
        mesh = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)

root = bpy.data.objects["BowlingPair01_ROOT"]
static_col = bpy.data.collections.get("BP01_STATIC")

# Gutter parameters
gutter_width = 0.24
gutter_depth = 0.12
gutter_length = 19.2
wall_thickness = 0.015
lip_size = 0.015

# Cross-section profile (open U-channel with lips)
# Points: (x, z) in local coords, centered at x=0
def make_gutter_profile():
    half = gutter_width / 2
    profile = [
        (-half, -gutter_depth),      # bottom-left
        (half, -gutter_depth),       # bottom-right
        (half, 0),                   # right wall top
        (half - lip_size, 0),        # right lip outer
        (half - lip_size, wall_thickness),  # right lip top
        (-half + lip_size, wall_thickness), # left lip top
        (-half + lip_size, 0),       # left lip outer
        (-half, 0),                  # left wall top
    ]
    return profile

profile = make_gutter_profile()

# Create gutter at given X center
def create_gutter(name, x_center):
    # Build vertices for both ends
    verts = []
    # Start end (Y=0)
    for i, (px, pz) in enumerate(profile):
        verts.append((x_center + px, 0, pz))
    # End end (Y=19.2)
    for i, (px, pz) in enumerate(profile):
        verts.append((x_center + px, gutter_length, pz))
    
    n = len(profile)
    faces = []
    # Bottom face
    faces.append((0, 1, n + 1, n))
    # Right wall
    faces.append((1, 2, n + 2, n + 1))
    # Right lip side
    faces.append((2, 3, n + 3, n + 2))
    # Right lip top
    faces.append((3, 4, n + 4, n + 3))
    # Left lip top
    faces.append((4, 5, n + 5, n + 4))
    # Left lip side
    faces.append((5, 6, n + 6, n + 5))
    # Left wall
    faces.append((6, 7, n + 7, n + 6))
    
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    obj = bpy.data.objects.new(name, mesh)
    static_col.objects.link(obj)
    obj.parent = root
    
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return obj

# Gutter positions (X centers)
gutter_positions = {
    "Gutter_L_Outer": -1.6044,
    "Gutter_L_Inner": -0.2956,
    "Gutter_R_Inner": 0.2956,
    "Gutter_R_Outer": 1.6044
}

for name, x in gutter_positions.items():
    create_gutter(name, x)

# Central divider between inner gutters
divider = bpy.data.meshes.new("Divider_mesh")
div_obj = bpy.data.objects.new("Gutter_Divider", divider)
static_col.objects.link(div_obj)
div_obj.parent = root
div_verts = [
    (-0.015, 0, -0.12),
    (0.015, 0, -0.12),
    (0.015, 0, 0),
    (-0.015, 0, 0),
    (-0.015, gutter_length, -0.12),
    (0.015, gutter_length, -0.12),
    (0.015, gutter_length, 0),
    (-0.015, gutter_length, 0),
]
div_faces = [
    (0, 1, 5, 4),  # bottom
    (1, 2, 6, 5),  # right
    (2, 3, 7, 6),  # top
    (3, 0, 4, 7),  # left
    (0, 3, 2, 1),  # front
    (4, 5, 6, 7),  # back
]
divider.from_pydata(div_verts, [], div_faces)
divider.update()

# Outer rails (thin strips above outer gutters)
def create_rail(name, x_center):
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    obj = bpy.data.objects.new(name, mesh)
    static_col.objects.link(obj)
    obj.parent = root
    verts = [
        (x_center - 0.02, 0, 0),
        (x_center + 0.02, 0, 0),
        (x_center + 0.02, gutter_length, 0),
        (x_center - 0.02, gutter_length, 0),
        (x_center - 0.02, 0, 0.03),
        (x_center + 0.02, 0, 0.03),
        (x_center + 0.02, gutter_length, 0.03),
        (x_center - 0.02, gutter_length, 0.03),
    ]
    faces = [
        (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6),
        (3, 0, 4, 7), (0, 3, 2, 1), (4, 5, 6, 7),
    ]
    mesh.from_pydata(verts, [], faces)
    mesh.update()

create_rail("Rail_L_Outer", -1.6044)
create_rail("Rail_R_Outer", 1.6044)

# Rear pit
pit = bpy.data.meshes.new("RearPit_mesh")
pit_obj = bpy.data.objects.new("RearPit", pit)
static_col.objects.link(pit_obj)
pit_obj.parent = root
# Pit: Y=19.2 to 19.8, X=-1.8 to 1.8, depth -0.3
pit_verts = [
    (-1.8, 19.2, -0.3), (1.8, 19.2, -0.3),
    (1.8, 19.8, -0.3), (-1.8, 19.8, -0.3),
    (-1.8, 19.2, 0), (1.8, 19.2, 0),
    (1.8, 19.8, 0), (-1.8, 19.8, 0),
]
pit_faces = [
    (0, 1, 2, 3),  # bottom
    (0, 3, 7, 4),  # front
    (1, 5, 6, 2),  # back
    (0, 4, 5, 1),  # left
    (3, 2, 6, 7),  # right
]
pit.from_pydata(pit_verts, [], pit_faces)
pit.update()

report = {
    "gutters_created": 4,
    "divider_created": True,
    "rails_created": 2,
    "pit_created": True
}