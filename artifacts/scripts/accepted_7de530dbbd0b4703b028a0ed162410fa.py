import bpy

# Move pin decks so center is at head pin position
for name in ["PinDeck_L", "PinDeck_R"]:
    obj = bpy.data.objects.get(name)
    if obj:
        obj.location.y = 18.288 - 0.5  # Center at head pin

report = {"pin_decks_centered_at_head_pin": True}