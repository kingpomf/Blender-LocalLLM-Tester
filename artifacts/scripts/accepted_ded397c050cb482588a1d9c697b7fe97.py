import bpy

# Move pin decks slightly forward so head pin is on deck, not at edge
for name in ["PinDeck_L", "PinDeck_R"]:
    obj = bpy.data.objects.get(name)
    if obj:
        obj.location.y = 18.2

report = {"pin_decks_shifted_forward": True}