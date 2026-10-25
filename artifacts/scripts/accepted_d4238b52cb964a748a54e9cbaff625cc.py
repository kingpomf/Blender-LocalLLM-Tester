import bpy

for obj in bpy.context.scene.objects:
    if obj.name == "FoulLine_L":
        obj.name = "Foul_L"
    elif obj.name == "FoulLine_R":
        obj.name = "Foul_R"

report = {"renamed": ["Foul_L", "Foul_R"]}