import bpy

# Fix: AlleyFloor top is at z=+0.325 (above z=0), obscuring the scene.
# Move floor center from z=-0.025 to z=-0.325 so top surface sits at z=0.
# Floor extends from z=-0.65 to z=0, below the playing surface.
floor = bpy.data.objects.get("AlleyFloor")
if floor is not None:
    floor.location[2] = -0.325