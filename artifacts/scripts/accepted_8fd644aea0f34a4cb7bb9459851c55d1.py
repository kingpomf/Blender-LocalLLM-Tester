import bpy

# Fix pin deck position - move to Z=0
for name in ["PinDeck_L", "PinDeck_R"]:
    obj = bpy.data.objects.get(name)
    if obj:
        obj.location.z = 0.0

report = {"pin_decks_fixed": True}