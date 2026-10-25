import bpy

# Fix deck position - move to Z=0
for name in ["Deck_L", "Deck_R"]:
    obj = bpy.data.objects.get(name)
    if obj:
        obj.location.z = 0.0

# Create pit
pit_name = "Pit"
if bpy.data.objects.get(pit_name):
    obj = bpy.data.objects[pit_name]
    mesh = obj.data
    bpy.data.objects.remove(obj, do_unlink=True)
    if mesh.users == 0:
        bpy.data.meshes.remove(mesh)

static_col = bpy.data.collections.get("BP01_STATIC")
root = bpy.data.objects["BowlingPair01_ROOT"]

# Pit: extends from 19.2m to 20.0m (0.8m long), recessed 0.05m
pit_x_min = -1.6044
pit_x_max = 1.6044
pit_y_start = 19.2
pit_y_end = 20.0
pit_depth = 0.05

verts = [
    (pit_x_min, pit_y_start, -pit_depth),
    (pit_x_max, pit_y_start, -pit_depth),
    (pit_x_max, pit_y_end, -pit_depth),
    (pit_x_min, pit_y_end, -pit_depth),
]
faces = [(0, 1, 2, 3)]
mesh = bpy.data.meshes.new(f"{pit_name}_mesh")
obj = bpy.data.objects.new(pit_name, mesh)
static_col.objects.link(obj)
obj.parent = root
mesh.from_pydata(verts, [], faces)
mesh.update()

report = {"decks_fixed": True, "pit_created": True}