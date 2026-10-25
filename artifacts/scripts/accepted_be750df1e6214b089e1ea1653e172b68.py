import bpy

# Fix pin deck position - top surface at Z=0
for name in ["PinDeck_L", "PinDeck_R"]:
    obj = bpy.data.objects.get(name)
    if obj:
        obj.location.z = -0.01

report = {"pin_decks_top_at_zero": True}