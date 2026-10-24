import bpy
import json
import os

def run_stage():
    scene = bpy.context.scene
    cam_name = 'CAM_BowlingPair01_Overview'
    output_path = '/job/artifacts/renders/BowlingPair01_overview.png'

    cam_obj = bpy.data.objects.get(cam_name)
    if cam_obj is None or cam_obj.type != 'CAMERA':
        raise ValueError(f"Camera {cam_name} not found")

    scene.camera = cam_obj
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 128
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.filepath = output_path
    scene.render.use_persistent_data = True

    bpy.context.scene.render.engine = 'CYCLES'
    bpy.ops.render.render(write_still=True)

    if os.path.exists(output_path):
        sz = os.path.getsize(output_path)
        report = {"stage": "07", "camera": cam_name, "passed": True, "output_size": sz, "errors": []}
    else:
        report = {"stage": "07", "camera": cam_name, "passed": False, "errors": [f"Render output not found at {output_path}"]}

    out_dir = '/job'
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, 'report.json'), 'w') as f:
        json.dump(report, f, indent=2)

report = run_stage()
