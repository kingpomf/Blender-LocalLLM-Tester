import bpy

# Move pin decks so front edge is at head pin position
for name in ["PinDeck_L", "PinDeck_R"]:
    obj = bpy.data.objects.get(name)
    if obj:
        obj.location.y = 18.288

report = {"pin_decks_front_at_head_pin": True}