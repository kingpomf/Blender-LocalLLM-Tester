import bpy

# Rename back to PinDeck
obj_l = bpy.data.objects.get("Deck_L")
obj_r = bpy.data.objects.get("Deck_R")
if obj_l:
    obj_l.name = "PinDeck_L"
if obj_r:
    obj_r.name = "PinDeck_R"

report = {"decks_renamed_back": True}