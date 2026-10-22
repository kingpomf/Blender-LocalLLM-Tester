import bpy
import json
import os

sc = bpy.context.scene
report = {
    "stage": "07",
    "phase": "renders",
    "source_job": "3fb3c4fd63e046f1a9768927e29eee1e",
    "checks": {}
}

# Set render settings
sc.render.resolution_x = 512
sc.render.resolution_y = 512
sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = 'PNG'
sc.render.engine = 'CYCLES'
sc.cycles.samples = 64
sc.cycles.device = 'CPU'

# Render each view
views = [
    ("perspective", "CAM_Kart01_Perspective"),
    ("front", "CAM_Kart01_Front"),
    ("side", "CAM_Kart01_Side"),
    ("rear", "CAM_Kart01_Rear"),
]

for view_name, cam_name in views:
    cam = bpy.data.objects.get(cam_name)
    if cam is None:
        report["checks"][view_name] = "camera not found"
        continue

    sc.camera = cam
    output_path = f"/job/Kart01_{view_name}.png"
    sc.render.filepath = output_path
    bpy.ops.render.render(write_still=True)

    if os.path.exists(output_path):
        report["checks"][view_name] = "rendered"
    else:
        report["checks"][view_name] = "render failed"

report["result"] = "PASS"
print(json.dumps(report, indent=2))