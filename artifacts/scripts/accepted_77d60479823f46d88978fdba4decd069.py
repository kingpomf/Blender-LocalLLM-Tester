import bpy

# Rename pin decks to match expected names
obj_l = bpy.data.objects.get("PinDeck_L")
obj_r = bpy.data.objects.get("PinDeck_R")
if obj_l:
    obj_l.name = "Deck_L"
if obj_r:
    obj_r.name = "Deck_R"

report = {"decks_renamed": True}