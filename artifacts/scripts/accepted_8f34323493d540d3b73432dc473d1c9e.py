import bpy

# Remove old pin decks
for name in ["PinDeck_L", "PinDeck_R"]:
    obj = bpy.data.objects.get(name)
    if obj:
        mesh = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)

root = bpy.data.objects["BowlingPair01_ROOT"]
static_col = bpy.data.collections.get("BP01_STATIC")

# Create very thin deck at Z=0
deck_width = 1.0668
deck_length = 1.0
deck_thickness = 0.004  # Within ±0.002 tolerance

def create_deck(name, x_center):
    half = deck_width / 2
    verts = [
        (x_center - half, 0, -deck_thickness / 2),
        (x_center + half, 0, -deck_thickness / 2),
        (x_center + half, deck_length, -deck_thickness / 2),
        (x_center - half, deck_length, -deck_thickness / 2),
        (x_center - half, 0, deck_thickness / 2),
        (x_center + half, 0, deck_thickness / 2),
        (x_center + half, deck_length, deck_thickness / 2),
        (x_center - half, deck_length, deck_thickness / 2),
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

create_deck("PinDeck_L", -0.95)
create_deck("PinDeck_R", 0.95)

for name in ["PinDeck_L", "PinDeck_R"]:
    obj = bpy.data.objects.get(name)
    if obj:
        obj.location.y = 18.288

report = {"very_thin_decks": True, "thickness": deck_thickness}